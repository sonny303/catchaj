# Security Policy

## 1. Supported Versions

We actively support the current stable version of **Catchaj**:

| Version | Supported          |
| :------ | :----------------- |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## 2. Zero-Leak Architecture

Catchaj is designed around the principle that **personal data and API credentials must never leak into version control**. We enforce this through multiple concentric layers of defense:

1. **Strict Version Control Exclusion (`.gitignore`):**
   - Private candidate profiles (`config.py`, `.env`, `career_truth_doc.md`, `master_resume.md`, `resume.pdf`) are explicitly excluded from Git tracking.
   - Local scrape caches, feedback databases, and browser profiles (`discovered_jobs_cache.json`, `applications_pipeline_local.csv`, `chrome_profile/`) are excluded.

2. **Deterministic Pre-Commit Scanner (`scripts/pre_commit_scan.py`):**
   - Runs automatically on every `git commit` via `.githooks/pre-commit`.
   - Blocks commits with exit code 1 if:
     - Blocked private files are staged.
     - High-entropy API keys (Google Gemini, OpenAI, Anthropic, AWS, GitHub, Stripe, HuggingFace, Resend, JWT, Bearer tokens) are detected.
     - Candidate PII (emails, phone numbers, full names, handles, private Google Sheet IDs) is detected.
   - Comprehensive automated self-test suite verified via `python3 scripts/pre_commit_scan.py --test`.

3. **Synthetic Sandbox Fixtures:**
   - Demonstrations, automated dry-runs, and public documentation strictly use the synthetic persona **"Alex Morgan"** (`examples/mock_truth_doc.md` and `examples/mock_jobs.json`).
   - No live network requests or external credentials are used during testing.

4. **Local Execution & Human Control:**
   - The application runs locally on your machine.
   - No data is transmitted to external telemetry servers.
   - The browser staging engine (`run_staged_application.py`) explicitly halts before submission — it **never** automates the final submit button.

---

## 3. Reporting a Vulnerability

If you discover a security vulnerability or potential credential leak mechanism in Catchaj, please report it responsibly:

- **Do NOT open a public GitHub issue** for sensitive security vulnerabilities.
- **Email:** Send details to the project maintainers via `security@example.com` (or create a private GitHub Security Advisory).
- **Include in your report:**
  - Description of the vulnerability.
  - Minimal steps to reproduce or proof of concept.
  - Potential impact assessment.
- **Response Timeline:**
  - Acknowledgement within 48 hours.
  - Regular status updates during triage and patch development.
  - Coordinated public disclosure after a fix is verified and released.

---

## 4. Remediation for Accidental Leaks

If you accidentally staged or committed credentials or personal data in a local checkout:

```bash
# 1. Unstage the offending file:
git restore --staged <file_path>

# 2. If already committed locally (before pushing):
git reset --soft HEAD~1
# Sanitize the file, then re-commit

# 3. If credentials were ever pushed to a remote repository:
# IMMEDIATELY revoke and rotate the API key / credential at the provider portal.
```

Thank you for helping keep Catchaj secure for all users!
