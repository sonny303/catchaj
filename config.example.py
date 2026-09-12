"""Public configuration template for Healthcare PM Job Application Engine.

Public configuration template importing from .env.example with neutral placeholder values.
Copy this file to config.py and customize your candidate profile and environment variables.
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import dotenv_values

BASE_DIR = Path(__file__).resolve().parent

# Load configuration values directly from .env.example
_example_env = dotenv_values(BASE_DIR / ".env.example")


class CandidateProfile(BaseModel):
    """Sanitized candidate profile defaults."""
    name: str = "Alex Morgan"
    pronouns: str = "They/Them"
    email: str = "candidate@example.com"
    phone: str = "555-010-0199"
    current_location: str = "Seattle, WA"
    linkedin_url: str = "https://www.linkedin.com/in/example-pm"
    github_url: str = ""
    portfolio_url: str = ""
    work_authorization_us: bool = True
    requires_us_sponsorship: bool = False
    requires_canada_sponsorship: bool = False
    base_resume_path: Path = BASE_DIR / "career_truth_doc.template.md"
    base_resume_pdf_path: Path = BASE_DIR / "resume.pdf"


class SearchFilterConfig(BaseModel):
    """Target job criteria and filtering thresholds."""
    # Target Job Titles
    target_titles: list[str] = [
        "Senior Product Manager",
        "Staff Product Manager",
        "Lead Product Manager",
        "Principal Product Manager",
        "Director of Product Management",
        "Associate Director of Product Management",
    ]

    # Target Domains & Keywords
    target_domains: list[str] = [
        "Healthcare",
        "HealthTech",
        "Digital Health",
        "Medical Care",
        "Hospital Systems",
        "Health IT",
        "Provider Tech",
        "Payor Tech",
        "Health Plans",
        "MedTech",
        "SaMD",
        "Life Sciences",
        "Clinical Trials",
        "Telehealth",
        "RPM",
        "Digital Therapeutics",
        "DTx",
    ]

    # Location rules
    allowed_locations: list[str] = ["US-Remote", "Canada-Remote", "Seattle, WA", "Greater Seattle"]
    rejected_onsite_locations: list[str] = ["Onsite outside Seattle", "Hybrid outside Seattle"]

    # Thresholds
    score_threshold_frictionless: int = 75  # Greenhouse, Lever, Ashby, SmartRecruiters (broadened for higher recall)
    score_threshold_account_gated: int = 95  # Workday, Taleo, iCIMS, SuccessFactors

    # Account-gated ATS platforms
    account_gated_ats: list[str] = [
        "workday",
        "taleo",
        "icims",
        "successfactors",
        "brassring",
    ]


class Settings(BaseModel):
    """Public template application settings populated from .env.example."""
    # Candidate profile
    candidate: CandidateProfile = CandidateProfile()

    # Search config
    search: SearchFilterConfig = SearchFilterConfig()

    # Google Sheets
    google_sheet_id: str = _example_env.get(
        "GOOGLE_SHEET_ID", "your_google_sheet_id_here"
    ) or "your_google_sheet_id_here"
    google_service_account_path: Path = Path(
        _example_env.get("GOOGLE_SERVICE_ACCOUNT_JSON_PATH", "service_account.json") or "service_account.json"
    )
    sheet_tab_name: str = "Applications_Pipeline"

    # Gemini
    gemini_api_key: str = _example_env.get("GEMINI_API_KEY", "") or ""

    # Notification
    notification_provider: str = _example_env.get("NOTIFICATION_PROVIDER", "gmail") or "gmail"
    notification_email: str = _example_env.get("NOTIFICATION_EMAIL", "alerts@example.com") or "alerts@example.com"
    gmail_user: str = _example_env.get("GMAIL_USER", "alerts@example.com") or "alerts@example.com"
    gmail_app_password: str = _example_env.get("GMAIL_APP_PASSWORD", "") or ""
    resend_api_key: str = _example_env.get("RESEND_API_KEY", "") or ""

    # Truth Doc Path
    truth_doc_path: Path = BASE_DIR / "career_truth_doc.template.md"


settings = Settings()
