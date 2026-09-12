"""Notification Dispatcher for High-Match Job Postings.

Supports Gmail SMTP and Resend API, with terminal logging fallback.
"""

import smtplib
import importlib.util
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

def send_job_alert(job_info: dict) -> bool:
    """Send an alert email for a qualified job posting."""
    title = job_info.get("Job Title", "Healthcare Product Manager")
    company = job_info.get("Company", "Unknown Company")
    score = job_info.get("Match Score", 0)
    location = job_info.get("Location / Type", "Remote")
    url = job_info.get("Posting URL", "")
    rationale = job_info.get("Match Rationale & Gaps", "")
    sheet_link = f"https://docs.google.com/spreadsheets/d/{settings.google_sheet_id}/edit"

    subject = f"[HIGH MATCH: {score}/100] {company} - {title}"
    body_text = f"""HIGH-MATCH JOB DETECTED

Company: {company}
Title: {title}
Location: {location}
Match Score: {score}/100

Match Rationale & Gaps:
{rationale}

Job Posting URL:
{url}

Review in Google Sheet:
{sheet_link}

Status: Staged as 'New' in pipeline. Run tailoring to draft application questions.
"""

    # 1. Try Gmail SMTP if configured
    if settings.notification_provider == "gmail" and settings.gmail_app_password:
        try:
            msg = MIMEMultipart()
            msg["From"] = settings.gmail_user
            msg["To"] = settings.notification_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body_text, "plain"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(settings.gmail_user, settings.gmail_app_password)
                server.send_message(msg)
            print(f"[✓] Alert email sent via Gmail SMTP to {settings.notification_email} for {company}")
            return True
        except Exception as e:
            print(f"[!] Gmail SMTP dispatch failed: {e}")

    # 2. Try Resend if configured
    if settings.resend_api_key:
        try:
            import resend
            resend.api_key = settings.resend_api_key
            resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": settings.notification_email,
                "subject": subject,
                "text": body_text
            })
            print(f"[✓] Alert email sent via Resend API to {settings.notification_email} for {company}")
            return True
        except Exception as e:
            print(f"[!] Resend API dispatch failed: {e}")

    # Fallback: Terminal notification
    print("\n" + "=" * 60)
    print(f"[NOTIFICATION - PENDING SMTP/RESEND CONFIG]")
    print(f"TO: {settings.notification_email}")
    print(f"SUBJECT: {subject}")
    print(body_text)
    print("=" * 60 + "\n")
    return True
