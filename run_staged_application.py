"""Agent-Browser: Human-in-the-Loop (HITL) Execution Runner.

Launches visible Chromium (headless=False), navigates to job application page,
pre-fills candidate contact details and tailored responses, attaches base PDF resume,
and cleanly yields execution to the human user for review and submission.
Strict Guardrail: NEVER clicks final Submit button.
"""

import argparse
import sys
import time
import importlib.util
from pathlib import Path
from playwright.sync_api import sync_playwright

# Load settings from config.py if present, or fall back to config.example.py in template mode
try:
    from config import settings
except ImportError:
    _example_cfg = Path(__file__).resolve().parent / "config.example.py"
    if _example_cfg.exists():
        _spec = importlib.util.spec_from_file_location("config", _example_cfg)
        _mod = importlib.util.module_from_spec(_spec)
        sys.modules["config"] = _mod
        _spec.loader.exec_module(_mod)
        settings = _mod.settings
    else:
        raise

from sheets_client import SheetsClient

active_staging_sessions = {}

def fill_common_fields(page, candidate, qa_text: str, resume_path: Path):
    """Pre-filling standard ATS form fields (Greenhouse, Lever, Ashby, etc.)."""
    time.sleep(1)

    # First Name
    for sel in [
        'input[name*="first_name" i]',
        'input[id*="first_name" i]',
        'input[autocomplete="given-name"]',
        'input[placeholder*="first name" i]',
    ]:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=1000):
                loc.fill(candidate.name.split()[0])
                break
        except Exception:
            pass

    # Last Name
    for sel in [
        'input[name*="last_name" i]',
        'input[id*="last_name" i]',
        'input[autocomplete="family-name"]',
        'input[placeholder*="last name" i]',
    ]:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=1000):
                loc.fill(candidate.name.split()[-1])
                break
        except Exception:
            pass

    # Full Name
    for sel in [
        'input[name="name" i]',
        'input[id="name" i]',
        'input[placeholder*="full name" i]',
    ]:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=1000):
                loc.fill(candidate.name)
                break
        except Exception:
            pass

    # Email
    for sel in [
        'input[type="email"]',
        'input[name*="email" i]',
        'input[id*="email" i]',
        'input[autocomplete="email"]',
    ]:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=1000):
                loc.fill(candidate.email)
                break
        except Exception:
            pass

    # Phone
    for sel in [
        'input[type="tel"]',
        'input[name*="phone" i]',
        'input[id*="phone" i]',
        'input[autocomplete="tel"]',
    ]:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=1000):
                loc.fill(candidate.phone)
                break
        except Exception:
            pass

    # Location / City
    for sel in [
        'input[name*="location" i]',
        'input[id*="location" i]',
        'input[placeholder*="city" i]',
    ]:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=1000):
                loc.fill(candidate.current_location)
                break
        except Exception:
            pass

    # LinkedIn
    if candidate.linkedin_url:
        for sel in [
            'input[name*="linkedin" i]',
            'input[id*="linkedin" i]',
            'input[placeholder*="linkedin" i]',
        ]:
            try:
                loc = page.locator(sel).first
                if loc.is_visible(timeout=1000):
                    loc.fill(candidate.linkedin_url)
                    break
            except Exception:
                pass

    # Resume upload
    if resume_path and resume_path.exists():
        for sel in [
            'input[type="file"][name*="resume" i]',
            'input[type="file"][id*="resume" i]',
            'input[type="file"][data-qa*="resume" i]',
            'input[type="file"]',
        ]:
            try:
                file_input = page.locator(sel).first
                if file_input.count() > 0:
                    file_input.set_input_files(str(resume_path.resolve()))
                    print(f"[✓] Attached resume PDF: {resume_path.name}")
                    break
            except Exception:
                pass

    # Tailored Q&A / Cover Letter textareas
    if qa_text:
        try:
            textareas = page.locator("textarea").all()
            if textareas:
                textareas[0].fill(qa_text)
                print(f"[✓] Injected tailored content into application text area.")
        except Exception:
            pass

def stage_application(row_data: dict, row_index: int, sheets_client: SheetsClient, is_interactive_cli: bool = True):
    company = row_data.get("Company", "Target Company")
    title = row_data.get("Job Title", "Target Role")
    url = row_data.get("Posting URL", "")
    qa_content = row_data.get("Drafted Application Q&A", "")
    resume_path = settings.truth_doc_path.parent / "resume.pdf"

    if not url:
        print(f"[-] No URL found for {company} - {title}. Cannot stage.")
        return False

    print(f"\n" + "=" * 60)
    print(f"[*] Staging application in visible browser:")
    print(f"    Company: {company}")
    print(f"    Title: {title}")
    print(f"    URL: {url}")
    print("=" * 60)

    try:
        p = sync_playwright().start()
        # Launch visible browser cleanly without locked profile conflict
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        )
        page = context.new_page()

        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        fill_common_fields(page, settings.candidate, qa_content, resume_path)

        if is_interactive_cli:
            print(f"\n[ACTION REQUIRED] Application staged in browser for {company} - {title}. Review, complete any CAPTCHA, click Submit, then press [ENTER] here.")
            input()
            sheets_client.update_row_status(row_index, status="Submitted")
            print(f"[✓] Status updated to 'Submitted' in pipeline for {company} - {title}.")
            browser.close()
            p.stop()
        else:
            # Store active staging context so Web UI can close/submit
            active_staging_sessions[row_index] = {
                "browser": browser,
                "playwright": p,
                "company": company,
                "title": title,
            }
            print(f"[✓] Application staged in visible browser for {company}. Waiting for user confirmation in Web UI.")

        return True
    except Exception as e:
        print(f"[!] Error launching/staging in browser: {e}")
        return False

def close_staging_session(row_index: int, mark_submitted: bool = False, sheets_client: SheetsClient = None):
    """Close an active staging browser session."""
    session = active_staging_sessions.pop(row_index, None)
    if session:
        try:
            session["browser"].close()
            session["playwright"].stop()
        except Exception:
            pass

    if mark_submitted and sheets_client:
        sheets_client.update_row_status(row_index, status="Submitted")
        print(f"[✓] Status updated to 'Submitted' for row #{row_index}.")

def main():
    parser = argparse.ArgumentParser(description="Run staged application in visible browser.")
    parser.add_argument("--row", type=int, help="Specific sheet row index to stage (1-indexed).")
    args = parser.parse_args()

    client = SheetsClient()
    rows = client.get_all_rows()

    if not rows:
        print("[-] No rows in pipeline to stage.")
        return

    if args.row:
        idx = args.row - 2
        if 0 <= idx < len(rows):
            stage_application(rows[idx], args.row, client, is_interactive_cli=True)
        else:
            print(f"[-] Row {args.row} is out of bounds (1 to {len(rows)+1}).")
        return

    for idx, r in enumerate(rows, start=2):
        if r.get("Status", "").strip().lower() == "approved":
            stage_application(r, idx, client, is_interactive_cli=True)

if __name__ == "__main__":
    main()
