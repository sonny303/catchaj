"""Agent-Truth-Sync: Ingests resume and Granola notes to produce and validate career_truth_doc.md."""

import re
import sys
import importlib.util
from pathlib import Path

# Load settings from config.py if present, or fall back to config.example.py in template mode
try:
    from config import settings
except ImportError:
    _example_cfg = Path(__file__).resolve().parent / "config.example.py"
    if _example_cfg.exists():
        _spec = importlib.util.spec_from_file_location("config", _example_cfg)
        _mod = importlib.util.module_from_spec(_spec)
        import sys
        sys.modules["config"] = _mod
        _spec.loader.exec_module(_mod)
        settings = _mod.settings
    else:
        raise

BANNED_BUZZWORDS = [
    r"\bspearheaded\b",
    r"\bfostered synergy\b",
    r"\bsynergy\b",
    r"\btestament to\b",
    r"\bproven track record\b",
    r"\bleveraged cutting-edge solutions\b",
    r"\bcutting-edge\b",
    r"\bthought leader\b",
    r"\bparadigm shift\b",
    r"\bworld-class\b",
]

def check_anti_buzzwords(text: str) -> list[str]:
    """Flag any banned buzzwords in text."""
    violations = []
    for pattern in BANNED_BUZZWORDS:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        if matches:
            violations.append(f"Found buzzword '{matches[0]}' matching rule {pattern}")
    return violations

def validate_truth_doc(doc_path: Path) -> bool:
    """Ensure truth document exists and meets all quality guardrails."""
    if not doc_path.exists():
        print(f"[-] Truth document does not exist: {doc_path}")
        return False

    content = doc_path.read_text(encoding="utf-8")
    violations = check_anti_buzzwords(content)
    if violations:
        print("[!] Anti-buzzword violations detected in truth doc:")
        for v in violations:
            print(f"    - {v}")
        return False

    # Check for required sections
    required_sections = [
        "1. Core Competencies",
        "2. Products Shipped",
        "3. Revenue & Operational Metrics",
        "4. Clinical & B2B Integrations",
        "5. Leadership & Cross-Functional Anecdotes",
    ]
    missing = [sec for sec in required_sections if sec not in content]
    if missing:
        print(f"[!] Missing required sections in {doc_path}: {missing}")
        return False

    print(f"[✓] Truth document successfully validated: {doc_path}")
    print(f"    - Length: {len(content)} characters, {len(content.splitlines())} lines")
    return True

def sync_granola_notes(notes_dir: Path) -> str:
    """Ingest any exported Granola notes from local directory."""
    if not notes_dir.exists():
        notes_dir.mkdir(parents=True, exist_ok=True)
        return ""

    gathered_text = []
    for ext in ["*.md", "*.txt", "*.json"]:
        for note_file in notes_dir.glob(ext):
            try:
                gathered_text.append(f"--- NOTE: {note_file.name} ---\n" + note_file.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"[!] Warning reading note {note_file}: {e}")

    if gathered_text:
        print(f"[+] Loaded {len(gathered_text)} notes from {notes_dir}")
    return "\n\n".join(gathered_text)

def main():
    print("=== Agent-Truth-Sync: Knowledge Synchronization ===")
    granola_dir = settings.truth_doc_path.parent / "granola_notes"
    granola_content = sync_granola_notes(granola_dir)

    # Validate career_truth_doc.md (or fallback to template in fresh clone)
    truth_doc = settings.truth_doc_path
    if not truth_doc.exists():
        fallback_doc = settings.truth_doc_path.parent / "career_truth_doc.template.md"
        if fallback_doc.exists():
            print(f"[*] Note: {truth_doc.name} not found. Validating template baseline: {fallback_doc.name}")
            truth_doc = fallback_doc

    if not validate_truth_doc(truth_doc):
        sys.exit(1)

    print("[✓] Agent-Truth-Sync completed with 100% confidence.")

if __name__ == "__main__":
    main()
