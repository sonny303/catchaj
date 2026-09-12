"""Agent-Evaluator: Triage & Notification Engine.

Enforces hard constraints (Seattle onsite vs US/Canada Remote, ATS friction gate >= 95%),
scores fit against career_truth_doc.md (0-100), appends matches to Google Sheet,
and fires notifications.
"""

import os
import json
import re
import importlib.util
from pathlib import Path
from pydantic import BaseModel, Field

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

from sheets_client import SheetsClient, is_posted_within_24h
from notifier import send_job_alert
from learning_agent import learning_agent_instance

class JobEvaluationResult(BaseModel):
    score: int = Field(ge=0, le=100, description="Overall match score from 0 to 100")
    location_category: str = Field(description="'US-Remote', 'Canada-Remote', 'Seattle-Onsite', or 'Disqualified'")
    location_passed: bool = Field(description="True if within Greater Seattle or US/Canada Remote")
    account_gate_required: bool = Field(description="True if Workday, Taleo, iCIMS, SuccessFactors")
    qualified: bool = Field(description="Meets location and score thresholds")
    match_rationale: str = Field(description="Key alignment points grounded in truth doc")
    gaps: str = Field(description="Identified gaps or missing requirements")
    visa_sponsorship_flag: bool = Field(default=False, description="True if Canadian role needing sponsorship")

def normalize_location(location_str: str, title: str = "", is_remote: bool = False) -> tuple[str, bool]:
    """Check location constraint:
    Allowed:
      - Any Remote in US / USA / All US time zones
      - Canada Remote (flag visa)
      - Greater Seattle / Seattle, WA (onsite/hybrid)
    Disqualified:
      - Any onsite/hybrid outside Greater Seattle metro
    """
    loc_lower = location_str.lower()
    title_lower = title.lower()

    if is_remote or "remote" in loc_lower or "anywhere" in loc_lower or "virtual" in loc_lower or "remote" in title_lower:
        if "canada" in loc_lower:
            return ("Canada-Remote", True)
        return ("US-Remote", True)

    # Check against allowed locations configured in settings
    for allowed in getattr(settings.search, "allowed_locations", []):
        allowed_lower = allowed.lower()
        if "remote" in allowed_lower:
            continue
        city_key = allowed_lower.split(",")[0].strip()
        if (len(city_key) > 2 and city_key in loc_lower) or allowed_lower in loc_lower:
            return (f"{allowed}-Local", True)

    # Check against candidate's current location in settings
    current_loc = getattr(settings.candidate, "current_location", "").lower()
    if current_loc:
        loc_city = current_loc.split(",")[0].strip()
        if len(loc_city) > 2 and loc_city in loc_lower:
            return (f"{settings.candidate.current_location}-Local", True)

    return ("Disqualified (Onsite/Hybrid outside target)", False)

FEEDBACK_FILE = settings.truth_doc_path.parent / "user_feedback.json"

def is_candidate_declined(company: str, title: str) -> tuple[bool, str]:
    """Check if candidate previously declined this company or role pattern."""
    if FEEDBACK_FILE.exists():
        try:
            feedbacks = json.loads(FEEDBACK_FILE.read_text(encoding="utf-8"))
            for fb in feedbacks:
                if fb.get("block_company") and fb.get("company", "").lower().strip() == company.lower().strip():
                    return (True, f"Excluded by user feedback: Blocked company '{company}'")
        except Exception:
            pass
    return (False, "")

def is_account_gated(ats_platform: str, url: str) -> bool:
    """Check if ATS requires account creation."""
    ats_lower = ats_platform.lower()
    url_lower = url.lower()
    for gated in settings.search.account_gated_ats:
        if gated in ats_lower or gated in url_lower:
            return True
    return False

def evaluate_with_gemini(job_data: dict, truth_doc_text: str) -> JobEvaluationResult:
    """Evaluate job posting using Google GenAI SDK if API key available."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.gemini_api_key)

    ats = job_data.get("ats_platform", "Other")
    url = job_data.get("url", "")
    loc_raw = job_data.get("location", "")
    loc_cat, loc_passed = normalize_location(loc_raw, title=job_data.get("title", ""), is_remote=job_data.get("is_remote", False))
    account_gated = is_account_gated(ats, url)

    target_titles_str = ", ".join(getattr(settings.search, "target_titles", ["Product Manager"])[:3])
    target_domains_str = ", ".join(getattr(settings.search, "target_domains", ["Technology"])[:6])

    prompt = f"""You are the Lead Job Evaluator.
Evaluate candidate fit for this job posting based strictly on the verified Candidate Truth Document.

CANDIDATE TRUTH DOCUMENT:
{truth_doc_text}

JOB POSTING DETAILS:
Title: {job_data.get('title')}
Company: {job_data.get('company')}
Location: {job_data.get('location')}
ATS Platform: {ats}
Description:
{job_data.get('description', '')[:4000]}

EVALUATION RULES:
1. Target Role Alignment: Evaluate alignment with target role titles ({target_titles_str}) and domain competencies ({target_domains_str}).
2. Grounded Assessment: Base all evaluation strictly on facts documented in the CANDIDATE TRUTH DOCUMENT above. Never assume or invent experience.
3. Rigor: Deduct points for significant misalignments (e.g., mismatched seniority, missing essential domain skills, or unrelated tech stacks).
4. Assign a composite match score from 0 to 100.
5. Output concise bullet points for match rationale and identified gaps.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=JobEvaluationResult,
            temperature=0.1,
        ),
    )

    result_dict = json.loads(response.text)
    eval_result = JobEvaluationResult(**result_dict)

    # Apply learning agent adjustment
    learned_delta, learned_bullets, is_blocked = learning_agent_instance.calculate_learned_adjustment(job_data)
    if is_blocked:
        eval_result.score = 0
        loc_passed = False
        eval_result.gaps = (eval_result.gaps + "\n" + "\n".join(learned_bullets)).strip()
    else:
        eval_result.score = min(100, max(0, eval_result.score + learned_delta))
        if learned_bullets:
            eval_result.match_rationale = (eval_result.match_rationale + "\n" + "\n".join([f"• {b}" for b in learned_bullets])).strip()

    threshold = learning_agent_instance.get_current_threshold(is_account_gated=account_gated)
    eval_result.qualified = loc_passed and (eval_result.score >= threshold)
    return eval_result

def evaluate_heuristic(job_data: dict, truth_doc_text: str) -> JobEvaluationResult:
    """Deterministic fallback evaluator when GEMINI_API_KEY is not yet populated."""
    ats = job_data.get("ats_platform", "Other")
    url = job_data.get("url", "")
    loc_raw = job_data.get("location", "")
    title = job_data.get("title", "").lower()
    desc = job_data.get("description", "").lower()
    account_gated = is_account_gated(ats, url)

    loc_cat, loc_passed = normalize_location(loc_raw, title=job_data.get("title", ""), is_remote=job_data.get("is_remote", False))
    company = job_data.get("company", "")
    company_blocked, block_reason = is_candidate_declined(company, title)

    score = 50
    rationale_bullets = []
    gaps_bullets = []

    if company_blocked:
        score = 0
        loc_passed = False
        gaps_bullets.append(block_reason)

    # Title check - Flexible regex for senior / lead / staff / principal PM & PM III+
    SENIOR_TITLE_REGEX = r"(?i)\b(senior|sr\.?|staff|lead|principal|director|head|vp)\b.*?\b(product\s+manager|pm)\b"
    LEVEL_TITLE_REGEX = r"(?i)\b(product\s+manager|pm)\b.*?\b(iii|iv|v|senior|sr\.?|lead|staff|principal)\b"

    if re.search(SENIOR_TITLE_REGEX, title) or re.search(LEVEL_TITLE_REGEX, title):
        score += 20
        rationale_bullets.append(f"Direct senior title alignment: {job_data.get('title', '').strip()}")
    elif any(t.lower() in title for t in settings.search.target_titles):
        score += 20
        rationale_bullets.append("Direct target title alignment")
    elif "product manager" in title or "product lead" in title or "pm" in title.split():
        score += 10
        rationale_bullets.append("Product management role")

    # Domain keywords in description
    domain_hits = [d for d in settings.search.target_domains if d.lower() in desc or d.lower() in title]
    if domain_hits:
        score += min(20, len(domain_hits) * 5)
        rationale_bullets.append(f"Healthcare domain matches: {', '.join(domain_hits[:4])}")
    else:
        gaps_bullets.append("Limited explicit healthcare terminology in summary snippet")

    # Tech stack hits
    tech_keywords = ["fhir", "ehr", "epic", "hl7", "rpm", "ai", "payer", "billing", "telehealth", "lims", "saas", "api"]
    tech_hits = [t for t in tech_keywords if t in desc]
    if tech_hits:
        score += min(15, len(tech_hits) * 4)
        rationale_bullets.append(f"Relevant tech stack: {', '.join(tech_hits).upper()}")

    # Apply Learning Agent continuous feedback adjustments
    learned_delta, learned_bullets, is_blocked = learning_agent_instance.calculate_learned_adjustment(job_data)
    if is_blocked:
        score = 0
        loc_passed = False
        gaps_bullets.extend(learned_bullets)
    else:
        score += learned_delta
        rationale_bullets.extend(learned_bullets)

    score = min(100, max(0, score))

    threshold = learning_agent_instance.get_current_threshold(is_account_gated=account_gated)
    qualified = loc_passed and (score >= threshold)

    if not loc_passed:
        gaps_bullets.append(f"Disqualified location: {loc_raw} (not US/Canada Remote or Seattle Metro)")

    if account_gated and score < threshold:
        gaps_bullets.append(f"Account-gated ATS ({ats}) requires >= {threshold}% match; score was {score}")
    elif not account_gated and score < threshold:
        gaps_bullets.append(f"Match score {score}% is below active threshold ({threshold}%)")

    return JobEvaluationResult(
        score=score,
        location_category=loc_cat,
        location_passed=loc_passed,
        account_gate_required=account_gated,
        qualified=qualified,
        match_rationale="\n".join([f"• {b}" for b in rationale_bullets]) or "Standard role alignment",
        gaps="\n".join([f"• {b}" for b in gaps_bullets]) or "None identified",
        visa_sponsorship_flag=(loc_cat == "Canada-Remote"),
    )

def evaluate_job(job_data: dict) -> JobEvaluationResult:
    """Route evaluation through Gemini or deterministic fallback."""
    truth_doc = settings.truth_doc_path.read_text(encoding="utf-8") if settings.truth_doc_path.exists() else ""

    if settings.gemini_api_key:
        try:
            return evaluate_with_gemini(job_data, truth_doc)
        except Exception as e:
            print(f"[!] Gemini evaluation failed ({e}). Falling back to deterministic engine.")

    return evaluate_heuristic(job_data, truth_doc)

def process_and_triage_job(job_data: dict, sheets_client: SheetsClient) -> bool:
    """Evaluate candidate job and stage to Google Sheets + Alert if qualified and within 24h."""
    date_posted = job_data.get("date_posted", "")
    if date_posted and not is_posted_within_24h(date_posted, max_hours=24):
        print(f"[*] Skipping {job_data.get('company')} - {job_data.get('title')}: Posted outside 24h window ({date_posted}).")
        return False

    eval_res = evaluate_job(job_data)

    print(f"[*] Evaluated: {job_data.get('company')} - {job_data.get('title')}")
    print(f"    - Score: {eval_res.score}/100 | Qualified: {eval_res.qualified} | Location: {eval_res.location_category}")

    if eval_res.qualified:
        row_dict = {
            "Job Title": job_data.get("title"),
            "Company": job_data.get("company"),
            "Location / Type": eval_res.location_category + (" (Sponsorship Required)" if eval_res.visa_sponsorship_flag else ""),
            "Match Score": eval_res.score,
            "Match Rationale & Gaps": f"RATIONALE:\n{eval_res.match_rationale}\n\nGAPS:\n{eval_res.gaps}",
            "Posting URL": job_data.get("url"),
            "ATS Platform": job_data.get("ats_platform"),
            "Status": "New",
            "Drafted Application Q&A": "",
            "Targeted Bullets": "",
            "Date Posted": job_data.get("date_posted", ""),
            "Source": job_data.get("source", "JobSpy"),
        }
        sheets_client.append_application(row_dict)
        send_job_alert(row_dict)
        return True
    return False

if __name__ == "__main__":
    client = SheetsClient()
    mock_job = {
        "title": "Lead Product Manager, Payer Integrations & FHIR",
        "company": "HealthTech Systems Inc.",
        "location": "Remote - US",
        "url": "https://boards.greenhouse.io/healthtech/jobs/12345",
        "ats_platform": "Greenhouse",
        "description": "Seeking a Lead PM with deep payer, FHIR, EHR, and AI evaluation experience to scale our healthcare SaaS platform.",
    }
    process_and_triage_job(mock_job, client)
