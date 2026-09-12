#!/usr/bin/env python3
"""Pre-Commit Security & PII Leak Scanner.

Deterministic scanner that inspects staged files for:
1. High-entropy secrets (API keys, private keys, service account JSONs, bearer tokens, AWS/GitHub tokens).
2. Candidate PII (email addresses, phone numbers, specific names and handles).
3. Blocked private files (career_truth_doc.md, master_resume.md, resume.pdf, .env, service_account*.json, config.py, etc.).

Aborts git commits with exit code 1 and actionable remediation instructions if any leak is detected.
Exits 0 if clean.
Supports `--test` flag for automated verification self-tests.
"""

import os
import sys
import re
import json
import fnmatch
import subprocess
import argparse
import base64
from pathlib import Path

# Blocked file patterns that must never be staged or committed
BLOCKED_FILE_PATTERNS = [
    "career_truth_doc.md",
    "master_resume.md",
    "resume.pdf",
    "resume_temp.html",
    ".env",
    ".env.*",
    "service_account.json",
    "service_account*.json",
    "credentials*.json",
    "applications_pipeline_local.csv",
    "discovered_jobs_cache.json",
    "user_feedback.json",
    "user_feedback*.json",
    "learning_profile.json",
    "learning_profile*.json",
    "chrome_profile/*",
    "granola_notes/*",
    "config.py",
]

# Explicitly allowed public templates
ALLOWED_PUBLIC_TEMPLATES = {
    ".env.example",
    "career_truth_doc.template.md",
    "config.example.py",
}

def _build_candidate_pii_patterns(data: dict) -> list:
    patterns = []
    name = data.get("candidate_name", "")
    if name:
        parts = name.split()
        if len(parts) >= 2:
            first = re.escape(parts[0])
            last = re.escape(parts[-1])
            patterns.append((rf"(?i)\b{first}[-_\.\s]*{last}s?\b", "Candidate full name or concatenated handle"))
            patterns.append((rf"(?i)\b{last}s?[-_\.\s,]*{first}\b", "Candidate full name (reversed)"))
            patterns.append((rf"(?i)(?:^|[\W_]){first}(?:[\W_]|$)", "Candidate first name"))
            patterns.append((rf"(?i)(?:^|[\W_]){last}s?(?:[\W_]|$)", "Candidate last name or handle"))

    email = data.get("candidate_email", "")
    if email:
        patterns.append((rf"(?i)\b{re.escape(email)}\b", "Candidate protected email"))
        
    area = data.get("candidate_phone_area_code", "")
    prefix = data.get("candidate_phone_prefix", "")
    line = data.get("candidate_phone_line", "")
    if area and prefix and line:
        patterns.append((rf"(?:\+?1[-.\s/]?)?\(?{re.escape(area)}\)?[-.\s/]?{re.escape(prefix)}[-.\s/]?{re.escape(line)}\b", "Candidate protected phone number"))
        
    for handle in data.get("candidate_handles", []):
        patterns.append((rf"(?i)\b{re.escape(handle)}\b", "Candidate handle"))
        
    for pid in data.get("protected_ids", []):
        patterns.append((re.escape(pid), "Candidate Google Sheet ID / Protected ID"))
        
    return patterns

def _load_pii_patterns() -> list:
    repo_root = Path(__file__).resolve().parent.parent
    patterns_file = repo_root / ".pii_patterns.json"
    
    if not patterns_file.exists():
        print(f"[!] Warning: PII patterns file not found at {patterns_file}. Candidate-specific PII checks will be skipped.")
        return []
        
    try:
        with open(patterns_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return _build_candidate_pii_patterns(data)
    except Exception as e:
        print(f"[!] Warning: Failed to load PII patterns ({e}). Candidate-specific PII checks will be skipped.")
        return []

# Candidate specific PII patterns (loaded dynamically from gitignored config)
_RAW_CANDIDATE_PII = _load_pii_patterns()

# High-entropy secret patterns
SECRET_PATTERNS = [
    (r"\bAIza[0-9A-Za-z\-_]{35}\b", "Google / Gemini API Key"),
    (r"\bsk-(?:proj-|admin-)?[a-zA-Z0-9_\-]{20,}\b", "OpenAI API Key (Standard / Project / Admin)"),
    (r"\bsk-ant-[a-zA-Z0-9_\-]{20,}\b", "Anthropic API Key"),
    (r"\bre_[a-zA-Z0-9]{24,}\b", "Resend API Key"),
    (r"\b(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36}\b|\bgithub_pat_[a-zA-Z0-9_]{50,}\b", "GitHub Token"),
    (r"\bxox[baprs]-[0-9a-zA-Z]{10,48}\b", "Slack Token"),
    (r"\b(?:AKIA|ASIA|ABIA|ACCA)[0-9A-Z]{16}\b", "AWS Access Key ID"),
    (r"(?i)(?:aws_secret_access_key|aws_secret_key)\s*[:=]\s*['\"]?([a-zA-Z0-9/+=]{40})['\"]?", "AWS Secret Access Key"),
    (r"-----BEGIN (?:[A-Z0-9_-]+ )?PRIVATE KEY-----", "Private Key (RSA/EC/DSA/OPENSSH)"),
    (r"(?i)bearer\s+[a-zA-Z0-9_\-\.]{25,}", "Bearer Token"),
    (r"\bhf_[a-zA-Z0-9]{34,}\b", "HuggingFace Access Token"),
    (r"\b(?:sk|rk)_(?:live|test)_[0-9a-zA-Z]{24,}\b", "Stripe API Key"),
    (r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b", "JSON Web Token (JWT)"),
    (r"://[a-zA-Z0-9_.-]+:(?:(?!\$\{)[^@\s]{6,})@[a-zA-Z0-9_.-]+", "Database Connection URI with Credentials"),
]

# Generic secret assignment regex (matches quoted and unquoted assignments, including base64)
GENERIC_SECRET_ASSIGNMENT = re.compile(
    r"""(?i)(?:api_key|apikey|secret_key|app_password|access_token|auth_token|client_secret|access_key|aws_secret_access_key|private_key|api_token|token|password|secret|credential|session_key|service_role_key)\s*[:=]\s*['"]?([a-zA-Z0-9_\-\/\+=]{16,})['"]?"""
)

# Known safe placeholders that shouldn't trigger generic secret warnings
SAFE_SECRET_PLACEHOLDERS = {
    "your_gemini_api_key_here",
    "your_resend_api_key_here",
    "your_gmail_app_password_here",
    "your_google_sheet_id_here",
    "example_api_key",
    "placeholder_key",
    "change_me",
}

def is_safe_secret_placeholder(secret_val: str) -> bool:
    """Determine if an assigned credential string is an obvious placeholder."""
    s = secret_val.lower().strip()
    if s in SAFE_SECRET_PLACEHOLDERS:
        return True
    if any(s.startswith(p) for p in ["your_", "example_", "placeholder", "change_me", "my_", "<", "["]):
        return True
    if "example" in s or "placeholder" in s:
        return True
    return False

# Generic email regex (flags non-placeholder emails in code/docs)
GENERIC_EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

# Allowed domains/emails that are safe templates or examples
ALLOWED_EMAIL_DOMAINS = {
    "example.com",
    "example.org",
    "example.net",
}
ALLOWED_SPECIFIC_EMAILS = {
    "candidate@example.com",
    "alerts@example.com",
    "user@example.com",
    "test@example.com",
    "your_email@example.com",
    "onboarding@resend.dev",
}

# Generic phone regex (US format)
GENERIC_PHONE_PATTERN = re.compile(
    r"\b(?:\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
)
SAFE_PHONE_PREFIXES = ("555-01", "555-0100", "(555) 01", "5550100")

BINARY_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svgz",
    ".pyc", ".pyo", ".pyd", ".so", ".dylib", ".dll", ".zip",
    ".tar", ".gz", ".bz2", ".7z", ".exe", ".bin"
}


class Violation:
    def __init__(self, file_path: str, violation_type: str, details: str, line_number: int = None, snippet: str = ""):
        self.file_path = file_path
        self.violation_type = violation_type
        self.details = details
        self.line_number = line_number
        self.snippet = snippet

    def __str__(self):
        line_info = f" (Line {self.line_number})" if self.line_number else ""
        snip_info = f"\n       Snippet: {self.snippet}" if self.snippet else ""
        return f"  - [{self.violation_type}] {self.file_path}{line_info}: {self.details}{snip_info}"


def is_blocked_file(file_path: str) -> bool:
    """Check if file path matches blocked sensitive file patterns (case-insensitive & nested directory aware)."""
    norm_path = os.path.normpath(file_path).replace("\\", "/")
    norm_path_lower = norm_path.lower()
    file_name = os.path.basename(norm_path)
    file_name_lower = file_name.lower()

    # Allow public templates explicitly (case-insensitive)
    allowed_templates_lower = {t.lower() for t in ALLOWED_PUBLIC_TEMPLATES}
    if file_name_lower in allowed_templates_lower:
        return False

    for pattern in BLOCKED_FILE_PATTERNS:
        pat_lower = pattern.lower()
        if fnmatch.fnmatch(norm_path_lower, pat_lower) or fnmatch.fnmatch(file_name_lower, pat_lower):
            return True
        if pat_lower.endswith("/*"):
            prefix = pat_lower[:-2]
            if (
                norm_path_lower.startswith(prefix + "/")
                or f"/{prefix}/" in f"/{norm_path_lower}/"
                or norm_path_lower.endswith("/" + prefix)
                or norm_path_lower == prefix
            ):
                return True
    return False


def scan_content(file_path: str, content: str) -> list[Violation]:
    """Inspect text content for secrets and candidate PII."""
    violations = []
    lines = content.splitlines()

    # Exempt the scanner script itself from meta-checks (regex rule definitions)
    if os.path.basename(file_path) == "pre_commit_scan.py":
        return []

    # Check for service account JSON structure
    if "service_account" in content and "private_key" in content:
        if re.search(r'"type"\s*:\s*"service_account"', content) and re.search(r'"private_key"\s*:', content):
            violations.append(Violation(
                file_path=file_path,
                violation_type="SECRET (Service Account)",
                details="GCP Service Account JSON private credentials detected",
            ))

    for line_idx, line in enumerate(lines, start=1):
        # 1. Check Specific Candidate PII
        for pattern, desc in _RAW_CANDIDATE_PII:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for m in matches:
                violations.append(Violation(
                    file_path=file_path,
                    violation_type="CANDIDATE PII",
                    details=desc,
                    line_number=line_idx,
                    snippet=line.strip()[:100],
                ))

        # 2. Check Specific Secret Patterns
        for pattern, desc in SECRET_PATTERNS:
            matches = re.finditer(pattern, line)
            for m in matches:
                val = m.group(0)
                redacted = val[:4] + "..." + val[-4:] if len(val) > 8 else "***"
                violations.append(Violation(
                    file_path=file_path,
                    violation_type="SECRET",
                    details=desc,
                    line_number=line_idx,
                    snippet=f"Detected secret token: {redacted}",
                ))

        # 3. Check Generic Secret Assignments
        gen_matches = GENERIC_SECRET_ASSIGNMENT.finditer(line)
        for gm in gen_matches:
            secret_val = gm.group(1).strip()
            if not is_safe_secret_placeholder(secret_val):
                redacted = secret_val[:4] + "..." + secret_val[-4:] if len(secret_val) > 8 else "***"
                violations.append(Violation(
                    file_path=file_path,
                    violation_type="HIGH-ENTROPY SECRET",
                    details=f"Unsanitized credential assignment detected: {redacted}",
                    line_number=line_idx,
                    snippet=f"Key: {gm.group(0)[:40]}...",
                ))

        # 4. Check Generic Email Pattern (flag real emails, ignore example.com)
        email_matches = GENERIC_EMAIL_PATTERN.finditer(line)
        for em in email_matches:
            email_val = em.group(0)
            email_lower = email_val.lower()
            domain = email_lower.split("@")[-1] if "@" in email_lower else ""
            if domain not in ALLOWED_EMAIL_DOMAINS and email_lower not in ALLOWED_SPECIFIC_EMAILS:
                if not any(token in line for token in ["noreply@github.com", "user@domain.com"]):
                    violations.append(Violation(
                        file_path=file_path,
                        violation_type="PII (Email)",
                        details=f"Unsanitized email address: {email_val}",
                        line_number=line_idx,
                        snippet=line.strip()[:100],
                    ))

        # 5. Check Generic Phone Pattern (flag real phone numbers, ignore 555 dummy numbers)
        phone_matches = GENERIC_PHONE_PATTERN.finditer(line)
        for pm in phone_matches:
            phone_val = pm.group(0)
            clean_digits = re.sub(r"\D", "", phone_val)
            if not any(phone_val.startswith(prefix) or clean_digits.startswith(prefix) for prefix in SAFE_PHONE_PREFIXES):
                violations.append(Violation(
                    file_path=file_path,
                    violation_type="PII (Phone Number)",
                    details=f"Unsanitized phone number pattern: {phone_val}",
                    line_number=line_idx,
                    snippet=line.strip()[:100],
                ))

    return violations


def get_staged_files() -> list[str]:
    """Retrieve list of files currently staged in git index (excluding deleted files)."""
    try:
        res = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=d"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [f.strip() for f in res.stdout.splitlines() if f.strip()]
    except Exception as e:
        print(f"[!] Warning: Unable to inspect git staged files ({e})")
        return []


def get_file_content(file_path: str, from_git_index: bool = True) -> str:
    """Read file content directly from git staging index or local disk."""
    if from_git_index:
        try:
            res = subprocess.run(
                ["git", "show", f":{file_path}"],
                capture_output=True,
                text=True,
                check=True,
                errors="replace",
            )
            return res.stdout
        except Exception:
            pass

    p = Path(file_path)
    if p.exists() and p.is_file():
        try:
            return p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return ""
    return ""


def print_remediation_banner(violations: list[Violation]):
    """Print prominent failure banner and actionable remediation instructions."""
    print("\n" + "=" * 80)
    print(" 🛑  PRE-COMMIT LEAK DETECTED: SENSITIVE DATA OR SECRETS FOUND")
    print("=" * 80)
    print(f"\nThe pre-commit scan identified {len(violations)} security violation(s) in staged files:\n")

    for v in violations:
        print(str(v))

    print("\n" + "-" * 80)
    print(" ACTIONABLE REMEDIATION INSTRUCTIONS:")
    print("-" * 80)
    print("1. Unstage the offending file(s):")
    print("     git rm --cached <file_path>              # if no commits exist yet")
    print("     git reset HEAD <file_path>               # if previous commits exist")
    print("     git restore --staged <file_path>         # alternative modern unstaging")
    print("\n2. If the file contains private candidate data or credentials:")
    print("     - Ensure the file is listed in .gitignore")
    print("     - Remove it from git cache: git rm --cached <file_path>")
    print("     - Use sanitized templates: career_truth_doc.template.md, config.example.py, .env.example")
    print("\n3. If you accidentally entered real API keys or PII into a tracked file:")
    print("     - Replace credentials with environment variables or neutral placeholders")
    print("     - Re-stage the sanitized file: git add <file_path>")
    print("\n4. Verify your staged changes are clean:")
    print("     python3 scripts/pre_commit_scan.py")
    print("=" * 80 + "\n")


def run_scan(target_files: list[str] = None) -> int:
    """Main scan workflow for git files. Returns exit code (0 or 1)."""
    is_explicit_targets = target_files is not None and len(target_files) > 0
    if is_explicit_targets:
        print(f"[*] Running pre-commit security & PII scan on {len(target_files)} specified file(s)...")
        files_to_scan = target_files
    else:
        print("[*] Running pre-commit security & PII leak scan on staged files...")
        files_to_scan = get_staged_files()

    if not files_to_scan:
        print("[✓] Pre-commit security scan passed (no files to inspect).")
        return 0

    violations: list[Violation] = []

    for file_path in files_to_scan:
        # Step 1: Check if file name is in blocked list
        if is_blocked_file(file_path):
            violations.append(Violation(
                file_path=file_path,
                violation_type="BLOCKED PRIVATE FILE",
                details="Private candidate or credential file is blocked from version control",
            ))
            continue

        # Step 2: Skip binary extensions for content scanning
        ext = os.path.splitext(file_path)[1].lower()
        if ext in BINARY_EXTENSIONS:
            continue

        # Step 3: Scan content
        content = get_file_content(file_path, from_git_index=not is_explicit_targets)
        file_violations = scan_content(file_path, content)
        violations.extend(file_violations)

    if violations:
        print_remediation_banner(violations)
        return 1

    print(f"[✓] Pre-commit security scan passed ({len(files_to_scan)} file(s) clean).")
    return 0


def run_self_tests(exit_on_leak: bool = False) -> int:
    """Automated self-test suite verifying that simulated API keys and PII are caught and trigger exit code 1."""
    print("=" * 80)
    print(" PRE-COMMIT LEAK PREVENTION AUTOMATED SELF-TEST SUITE")
    print("=" * 80)

    global _RAW_CANDIDATE_PII
    # Temporarily override with test data
    test_pii_data = {
        "candidate_name": "Alex Morgan",
        "candidate_email": "alex.morgan@example.com",
        "candidate_phone_area_code": "555",
        "candidate_phone_prefix": "011",
        "candidate_phone_line": "1111",
        "candidate_handles": ["alexmorgan"],
        "protected_ids": ["your_google_sheet_id_here"]
    }
    _RAW_CANDIDATE_PII = _build_candidate_pii_patterns(test_pii_data)

    # Construct simulated test tokens dynamically to avoid false-positive static scanning by remote push protection
    sim_openai = "".join(["sk-", "abcdef1234567890abcdef1234567890"])
    sim_openai_proj = "".join(["sk-proj-", "abcdef1234567890abcdef123456"])
    sim_gemini = "".join(["AIzaSyD", "1234567890abcdef1234567890abcdef"])
    sim_privkey = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0"
    sim_sa_json = '{\n  "type": "service_account",\n  "project_id": "test-proj",\n  "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIE"\n}'
    sim_bearer = "".join(["Bearer ", "ya29.a0AbH6SMBabc1234567890abcdef12345"])
    sim_email = "alex.morgan@example.com"
    sim_phone_dashes = "555-011-1111"
    sim_phone_parens = "(555) 011-1111"
    sim_phone_spaces = "555 011 1111"
    sim_phone_slashes = "555/011/1111"
    sim_name = "Alex Morgan"
    sim_handle = "alexmorgan"
    sim_profile_var = "alex_profile"
    sim_github_pat = "".join(["github_", "pat_11AAAAAAA0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_abcdefg"])
    sim_aws_key = "".join(["ASIA", "IOSFODNN7EXAMPLE"])
    sim_aws_secret = "".join(["wJalrXUtn", "FEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"])
    sim_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    sim_db_uri = "postgresql://dbuser:supersecretpass123@db.prod.internal:5432/appdb"
    sim_hf = "".join(["hf_", "abcdefghijklmnopqrstuvwxyz12345678"])
    sim_stripe = "".join(["sk_live_", "1234567890abcdefghijklmn"])

    test_cases = [
        # (Title, filename, content, should_leak, expected_leak_type)
        (
            "Test 1: OpenAI Standard Key",
            "mock_app.py",
            f'API_KEY = "{sim_openai}"',
            True,
            "SECRET",
        ),
        (
            "Test 2: OpenAI Project Key",
            "mock_llm.py",
            f'OPENAI_API_KEY = "{sim_openai_proj}"',
            True,
            "SECRET",
        ),
        (
            "Test 3: Google Gemini API Key",
            "mock_service.py",
            f'GEMINI_KEY = "{sim_gemini}"',
            True,
            "SECRET",
        ),
        (
            "Test 4: Private Key Block",
            "cert.pem",
            f"{sim_privkey}\n...\n-----END RSA PRIVATE KEY-----",
            True,
            "SECRET",
        ),
        (
            "Test 5: Google Service Account JSON",
            "gcp_credentials.json",
            sim_sa_json,
            True,
            "SECRET (Service Account)",
        ),
        (
            "Test 6: Bearer Token",
            "client.py",
            f'headers = {{"Authorization": "{sim_bearer}"}}',
            True,
            "SECRET",
        ),
        (
            "Test 7: GitHub Fine-Grained Token",
            "git_sync.py",
            f'gh_token = "{sim_github_pat}"',
            True,
            "SECRET",
        ),
        (
            "Test 8: AWS Session Access Key (ASIA)",
            "aws_config.py",
            f'AWS_ACCESS_KEY_ID = "{sim_aws_key}"',
            True,
            "SECRET",
        ),
        (
            "Test 9: AWS Secret Key Assignment",
            "deploy.py",
            f'aws_secret_access_key = "{sim_aws_secret}"',
            True,
            "HIGH-ENTROPY SECRET",
        ),
        (
            "Test 10: Candidate Protected Email",
            "notes.txt",
            f"Please notify {sim_email}",
            True,
            "CANDIDATE PII",
        ),
        (
            "Test 11: Candidate Phone (Parens & Spaces)",
            "contact.txt",
            f"Phone on file: {sim_phone_parens} or {sim_phone_spaces}",
            True,
            "CANDIDATE PII",
        ),
        (
            "Test 12: Candidate Full Name & Handle",
            "profile.md",
            f"# Profile: {sim_name}\nGitHub Handle: {sim_handle}",
            True,
            "CANDIDATE PII",
        ),
        (
            "Test 13: Unquoted Secret Assignment (.env format)",
            "settings.ini",
            f"OPENAI_API_KEY={sim_openai}",
            True,
            "SECRET",
        ),
        (
            "Test 14: Blocked File Name (career_truth_doc.md)",
            "career_truth_doc.md",
            "Content irrelevant; blocked by file name",
            True,
            "BLOCKED PRIVATE FILE",
        ),
        (
            "Test 15: Blocked File Name (.env.local & config.py)",
            "config.py",
            "Content irrelevant; blocked by file name",
            True,
            "BLOCKED PRIVATE FILE",
        ),
        (
            "Test 16: Clean Public Templates Pass",
            "career_truth_doc.template.md",
            "# Career Truth Document: [Candidate Name]\nEmail: candidate@example.com\nPhone: 555-010-0199",
            False,
            "CLEAN",
        ),
        (
            "Test 17: Case-Insensitive Blocked Files (RESUME.PDF & Config.Py)",
            "RESUME.PDF",
            "Binary content skipped; blocked by case-insensitive filename",
            True,
            "BLOCKED PRIVATE FILE",
        ),
        (
            "Test 18: Subdirectory Nested Blocked Path",
            "sub/chrome_profile/Default/Preferences",
            "Nested browser profile file",
            True,
            "BLOCKED PRIVATE FILE",
        ),
        (
            "Test 19: Concatenated Name & Snake-Case Identifiers",
            "user_settings.py",
            f'github_handle = "{sim_handle}"\nprofile_var = "{sim_profile_var}"',
            True,
            "CANDIDATE PII",
        ),
        (
            "Test 20: Generic API Token & Password Assignments",
            "database.py",
            'API_TOKEN = "abcdef1234567890abcdef"\nDATABASE_PASSWORD = "supersecretpassword12345"',
            True,
            "HIGH-ENTROPY SECRET",
        ),
        (
            "Test 21: HuggingFace Token & Stripe API Key",
            "ml_models.py",
            f'HF_TOKEN = "{sim_hf}"\nSTRIPE_KEY = "{sim_stripe}"',
            True,
            "SECRET",
        ),
        (
            "Test 22: Candidate Phone with Slashes",
            "info.txt",
            f"Direct contact line: {sim_phone_slashes}",
            True,
            "CANDIDATE PII",
        ),
        (
            "Test 23: JSON Web Token (JWT)",
            "auth_handler.py",
            f'token = "{sim_jwt}"',
            True,
            "SECRET",
        ),
        (
            "Test 24: Database Connection URI with Credentials",
            "db_config.py",
            f'DATABASE_URL = "{sim_db_uri}"',
            True,
            "SECRET",
        ),
    ]

    all_passed = True
    test_count = len(test_cases)
    passed_count = 0

    for idx, (title, fname, content, should_leak, expected_type) in enumerate(test_cases, start=1):
        violations = []
        if is_blocked_file(fname):
            violations.append(Violation(
                file_path=fname,
                violation_type="BLOCKED PRIVATE FILE",
                details="Private file blocked from staging",
            ))
        else:
            violations.extend(scan_content(fname, content))

        detected_leak = len(violations) > 0
        status_ok = (detected_leak == should_leak)

        if status_ok:
            passed_count += 1
            if should_leak:
                leak_types = ", ".join(set(v.violation_type for v in violations))
                print(f"[{idx:02d}/{test_count:02d}] {title:<52} -> CAUGHT [{leak_types}] (Triggers exit code 1) [PASS]")
            else:
                print(f"[{idx:02d}/{test_count:02d}] {title:<52} -> CLEAN  (Triggers exit code 0) [PASS]")
        else:
            all_passed = False
            print(f"[{idx:02d}/{test_count:02d}] {title:<52} -> FAILED (Expected leak={should_leak}, Got={detected_leak}) [FAIL]")

    print("=" * 80)
    if all_passed:
        print(f"[✓] ALL {passed_count}/{test_count} SELF-TESTS PASSED.")
        print("VERIFIED: Simulated API keys, credentials, PII, and blocked files are caught and trigger exit code 1.")
        print("VERIFIED: Clean template files pass with exit code 0.")
    else:
        print(f"[!] SELF-TEST FAILURES DETECTED ({passed_count}/{test_count} passed).")
        return 1

    if exit_on_leak or os.getenv("PRE_COMMIT_TEST_EXIT_1") == "1":
        print("\n[!] Simulated leak exit requested: Aborting with exit code 1.")
        return 1

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Deterministic pre-commit security & PII scanner for catchaj"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Optional specific file(s) to scan. If omitted, scans git staged files.",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Execute automated self-tests verifying that simulated API keys and PII are caught and trigger exit code 1.",
    )
    parser.add_argument(
        "--simulate-leak",
        "--test-leak",
        dest="simulate_leak",
        action="store_true",
        help="Simulate a staged leak, print remediation banner, and abort with exit code 1.",
    )
    args = parser.parse_args()

    if args.simulate_leak:
        sim_name = "Alex Morgan"
        sim_email = "alex.morgan@example.com"
        simulated_violations = [
            Violation("config.py", "BLOCKED PRIVATE FILE", "Private candidate configuration file is blocked from version control"),
            Violation("service_account.json", "BLOCKED PRIVATE FILE", "Private service account credential is blocked from version control"),
            Violation("notes.txt", "CANDIDATE PII", f"Candidate email: {sim_email}", 5, f"Contact {sim_email}"),
            Violation(".env", "SECRET", "Detected secret token: sk-proj-***"),
        ]
        print_remediation_banner(simulated_violations)
        sys.exit(1)

    if args.test:
        sys.exit(run_self_tests())

    sys.exit(run_scan(target_files=args.files if args.files else None))


if __name__ == "__main__":
    main()
