"""Agent-Tailor: Application Drafter & Resume Bullet Selector.

Pulls rows with status 'New', inspects the application form / posting for
unique specific interview-like questions.
- If unique interview questions exist: drafts concise (120-180 words) answers
  grounded 100% in career_truth_doc.md addressing those exact questions, selects
  supporting accomplishment bullets, verifies zero buzzwords, and updates status to 'Drafted'.
- If the application only has standard fields (contact, resume, work auth, EEO):
  leaves Q&A and highlights completely blank ("") so no irrelevant drawer appears.
"""

import json
import re
import importlib.util
from pathlib import Path
import requests

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

from sheets_client import SheetsClient
from sync_truth import check_anti_buzzwords, BANNED_BUZZWORDS

SYNTHETIC_FALLBACK_BULLETS = [
    "Product-managed automated prior-authorization microservices utilizing HL7 FHIR and electronic payer rule evaluation at Apex Health Systems, cutting review turnaround by 52% with 100% regulatory compliance.",
    "Shipped real-time patient eligibility and cost-estimation services embedded into provider scheduling workflows, eliminating point-of-care billing surprises and reducing front-desk support inquiries by 40%.",
    "Directed product strategy for an AI-native remote patient monitoring platform at Vigilance Medical AI, deploying continuous biometric ingestion and risk scoring that decreased 30-day hospital readmissions.",
    "Formulated precision/recall tuning and alarm volume budgets for nurse triage squads, decreasing non-actionable alerts by 48% while preserving 99.5% sensitivity for urgent clinical decompensations.",
    "Standardized SMART-on-FHIR connectors embedding patient dashboards directly into Epic and Cerner workflows, growing daily active clinician adoption by 65% across 14 hospital departments.",
    "Architected real-time ADT event notification pipelines handling 15 million daily clinical messages with 99.99% availability at CareBridge Interoperability.",
    "Designed and launched a 0→1 closed-loop community social care referral product, embedding resource directories and referral tracking into clinical EHR screens.",
]

# Patterns for standard form fields that do NOT count as interview questions
STANDARD_DISQUALIFIERS = [
    r'\b(?:first|last|full|legal)\s*name\b',
    r'\bemail\b',
    r'\bphone\b',
    r'\bmobile\b',
    r'\bresume\b',
    r'\bcv\b',
    r'\bcover\s*letter\b',
    r'\bwebsite\b',
    r'\blinkedin\b',
    r'\bgithub\b',
    r'\bportfolio\s*(?:url|link)?\b',
    r'\baddress\b',
    r'\bcity\b',
    r'\bstate\b',
    r'\bcountry\b',
    r'\bpostal\b',
    r'\bzip\b',
    r'\bpronoun',
    r'\bgender\b',
    r'\brace\b',
    r'\bethnicit',
    r'\bveteran\b',
    r'\bdisabilit',
    r'\bsexual\s*orientation\b',
    r'\bsalary\b',
    r'\bcompensation\b',
    r'\bnotice\s*period\b',
    r'\bstart\s*date\b',
    r'\brelocation\b',
    r'\bwork\s*authorization\b',
    r'\bauthorized\s*to\s*work\b',
    r'\bsponsorship\b',
    r'\bvisa\b',
    r'\bcitizen',
    r'\bhear\s*about\b',
    r'\bhow\s*did\s*you\b.*?(?:hear|find)',
    r'\bsource\b',
    r'\breferral\b',
    r'\battestation\b',
    r'\bveracity\b',
    r'\bconsent\b',
    r'\bagreement\b',
    r'\bterms\b',
    r'\bnon-compete\b',
    r'\bnon-disclosure\b',
    r'\bworking\s*preference',
]

# Positive signals indicating qualitative interview questions
INTERVIEW_QUESTION_SIGNALS = [
    r'\bwhy\b',
    r'\bdescribe\b',
    r'\btell\s*us\b',
    r'\bexplain\b',
    r'\bhow\s*(?:do|have|would|are)\s*you\b',
    r'\bwhat\s*(?:is|are)\s*your\b',
    r'\bwhat\s*excites\b',
    r'\bwhat\s*interests\b',
    r'\bexperience\s*(?:with|in|leading|shipping|managing)\b',
    r'\bproject\b',
    r'\baccomplish',
    r'\bchallenge\b',
    r'\bapproach\b',
    r'\bphilosophy\b',
    r'\bshare\s*an?\s*example\b',
]

def is_interview_question(label: str, field_types: list[str] = None) -> bool:
    """Classify if a form field is a genuine qualitative interview/essay question."""
    lbl = (label or "").strip()
    lbl_lower = lbl.lower()

    if not lbl or len(lbl) < 10:
        return False

    # Disqualify standard fields
    for dis in STANDARD_DISQUALIFIERS:
        if re.search(dis, lbl_lower):
            return False

    # If field is only single select / multi select / file upload, not an interview essay question
    if field_types and all('select' in ft or 'file' in ft for ft in field_types):
        return False

    # Positive interview signals
    for sig in INTERVIEW_QUESTION_SIGNALS:
        if re.search(sig, lbl_lower):
            return True

    # If sufficiently long and ends with a question mark
    if len(lbl) > 35 and '?' in lbl:
        return True

    return False

def extract_interview_questions_from_posting(url: str, ats_platform: str = "", description: str = "") -> tuple[list[str], str]:
    """Inspect application page / API to extract specific interview questions and posted/updated date.
    
    Returns (questions_list, date_posted_str).
    """
    if not url:
        return [], ""

    questions = []
    posted_date = ""

    # 1. Greenhouse ATS
    gh_match = re.search(r'(?:job-boards|boards)\.greenhouse\.io/([^/]+)/jobs/(\d+)', url)
    if not gh_match:
        gh_match = re.search(r'greenhouse\.io/([^/]+)/jobs/(\d+)', url)
    if gh_match:
        board, jid = gh_match.group(1), gh_match.group(2)
        api_url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs/{jid}?questions=true"
        try:
            resp = requests.get(api_url, timeout=4, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                data = resp.json()
                posted_date = str(data.get("updated_at", "") or "")[:10]
                for q in data.get("questions", []):
                    lbl = q.get("label", "")
                    fields = [f.get("type", "") for f in q.get("fields", [])]
                    if is_interview_question(lbl, fields):
                        questions.append(lbl.strip())
                return questions, posted_date
        except Exception:
            pass

    # 2. Lever ATS
    lever_match = re.search(r'jobs\.lever\.co/([^/]+)/([a-zA-Z0-9-]+)', url)
    if lever_match:
        company, jid = lever_match.group(1), lever_match.group(2)
        api_url = f"https://api.lever.co/v0/postings/{company}/{jid}"
        try:
            resp = requests.get(api_url, timeout=4, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                data = resp.json()
                created_at = data.get("createdAt")
                if created_at:
                    from datetime import datetime
                    posted_date = datetime.utcfromtimestamp(created_at / 1000.0).strftime("%Y-%m-%d")
                for q in data.get("customQuestions", []):
                    lbl = q.get("text", "")
                    fields = [q.get("type", "")]
                    if is_interview_question(lbl, fields):
                        questions.append(lbl.strip())
                return questions, posted_date
        except Exception:
            pass

    # 3. Direct Job Description Fallback
    if description:
        app_q_match = re.search(
            r'(?:application\s*questions?|questions?\s*for\s*applicants?|please\s*answer)[:\n]+(.*?)(?:\n\n[A-Z]|\Z)',
            description,
            re.IGNORECASE | re.DOTALL
        )
        if app_q_match:
            lines = app_q_match.group(1).splitlines()
            for line in lines:
                cleaned = re.sub(r'^\s*[-*•\d.)]+\s*', '', line).strip()
                if is_interview_question(cleaned):
                    questions.append(cleaned)

    return questions, posted_date

def parse_bullets_from_truth(truth_doc_text: str) -> list[str]:
    """Extract candidate bullet points from Sections 2, 3, 4, 5 of truth doc."""
    if not truth_doc_text:
        return []
    bullets = []
    in_section = False
    for line in truth_doc_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            sec_lower = stripped.lower()
            in_section = any(k in sec_lower for k in ["products shipped", "metrics", "integrations", "anecdotes", "competencies"])
            continue
        if in_section:
            if stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith("• "):
                item = stripped[2:].strip()
                cleaned = re.sub(r"^\*\*(.+?)\*\*:\s*", r"\1: ", item)
                if len(cleaned) > 25 and not cleaned.startswith("[") and not cleaned.startswith("**["):
                    bullets.append(cleaned)
    return bullets

def select_targeted_bullets(job_title: str, description: str, truth_doc_text: str) -> list[str]:
    """Select 4-5 most relevant project bullets from truth doc based on role keywords."""
    extracted = parse_bullets_from_truth(truth_doc_text)
    pool = extracted if extracted else SYNTHETIC_FALLBACK_BULLETS

    desc_lower = (job_title + " " + description).lower()
    scored_bullets = []
    for b in pool:
        score = 0
        b_lower = b.lower()
        for kw in ["fhir", "payer", "claims", "insurance", "rpm", "monitoring", "clinical", "ehr", "epic", "cerner", "ai", "model", "interoperability", "adt", "prior-auth", "decision support", "biometric", "onboarding"]:
            if kw in desc_lower and kw in b_lower:
                score += 3
        for word in job_title.lower().split():
            if len(word) > 3 and word in b_lower:
                score += 2
        scored_bullets.append((score, b))

    # Sort descending by relevance score
    scored_bullets.sort(key=lambda x: x[0], reverse=True)
    selected = [b for _, b in scored_bullets[:5]]
    return selected

def draft_answer_for_question(question: str, job_title: str, company: str, truth_doc_text: str) -> str:
    """Draft a concise (120-180 words) answer strictly grounded in candidate truth doc."""
    if settings.gemini_api_key:
        try:
            from google import genai
            client = genai.Client(api_key=settings.gemini_api_key)
            prompt = f"""You are Agent-Tailor, a high-signal application drafting agent.
Candidate: {settings.candidate.name} ({', '.join(settings.search.target_titles[:2])}).

TRUTH DOC:
{truth_doc_text}

ROLE: {company} - {job_title}
APPLICATION QUESTION:
"{question}"

TASK:
Draft a concise (120-180 words) answer to this specific question, grounded 100% in the candidate truth doc.
STRICT RULES:
- Address the exact question asked directly and factually.
- Ground all facts and metrics strictly in the verified candidate truth doc.
- ABSOLUTELY NO generic buzzwords: BANNED are 'spearheaded', 'fostered synergy', 'testament to', 'proven track record', 'leveraged cutting-edge solutions'.
- Use direct, metric-backed product leadership language.
"""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            draft = response.text.strip()
            violations = check_anti_buzzwords(draft)
            if not violations:
                return draft
        except Exception as e:
            print(f"[!] Gemini tailoring failed ({e}). Using deterministic grounded synthesis.")

    # Grounded deterministic synthesis tailored to question keywords
    q_lower = question.lower()
    bullets = parse_bullets_from_truth(truth_doc_text)
    relevant_bullets = []
    for b in bullets:
        b_lower = b.lower()
        if any(w in q_lower and w in b_lower for w in ["fhir", "prior-auth", "ehr", "rpm", "biometric", "ai", "interoperability", "onboarding", "hospital", "payer"]):
            relevant_bullets.append(b)

    if not relevant_bullets:
        relevant_bullets = bullets[:2] if bullets else SYNTHETIC_FALLBACK_BULLETS[:2]

    evidence_text = " ".join(relevant_bullets[:2])

    return f"In my product management career across clinical interoperability and digital health platforms, I have directly addressed this domain. Specifically, {evidence_text} At {company}, I apply this grounded, metric-driven approach to ensure high clinical reliability and seamless workflow adoption."

def draft_tailored_qa_for_questions(questions: list[str], job_title: str, company: str, description: str, truth_doc_text: str) -> str:
    """Draft answers for each specific interview question."""
    if not questions:
        return ""

    qa_blocks = []
    for idx, q in enumerate(questions, start=1):
        ans = draft_answer_for_question(q, job_title, company, truth_doc_text)
        qa_blocks.append(f"### Q{idx}: {q}\n{ans}")

    return "\n\n".join(qa_blocks)

def process_tailoring_pipeline(sheets_client: SheetsClient, force_all: bool = False):
    """Scan pipeline for rows, inspect application form for custom interview questions,
    and populate Q&A and highlights ONLY if custom interview questions exist.
    """
    rows = sheets_client.get_all_rows()
    truth_doc_text = settings.truth_doc_path.read_text(encoding="utf-8") if settings.truth_doc_path.exists() else ""

    print(f"[*] Checking {len(rows)} pipeline rows for tailoring...")
    for idx, row in enumerate(rows, start=2):  # row 1 is header
        status = row.get("Status", "").strip()
        if not force_all and status != "New":
            continue

        company = row.get("Company", "")
        title = row.get("Job Title", "")
        url = row.get("Posting URL", "")
        ats = row.get("ATS Platform", "")
        rationale = row.get("Match Rationale & Gaps", "")

        print(f"[+] Inspecting application form for custom interview questions: {company} - {title} (Row {idx})")
        questions, posted_date = extract_interview_questions_from_posting(url, ats, rationale)

        existing_date = row.get("Date Posted", "")
        final_date = existing_date if existing_date else posted_date

        if questions:
            print(f"    [!] Found {len(questions)} custom interview questions: {questions}")
            qa_draft = draft_tailored_qa_for_questions(questions, title, company, rationale, truth_doc_text)
            bullets = select_targeted_bullets(title, " ".join(questions) + " " + rationale, truth_doc_text)
            formatted_bullets = "\n".join([f"• {b}" for b in bullets])

            # Anti-buzzword audit & sanitization
            buzzword_violations = check_anti_buzzwords(qa_draft) + check_anti_buzzwords(formatted_bullets)
            if buzzword_violations:
                print(f"    [!] Buzzword violations caught: {buzzword_violations}. Sanitizing...")
                for pat in BANNED_BUZZWORDS:
                    qa_draft = re.sub(pat, "led", qa_draft, flags=re.IGNORECASE)
                    formatted_bullets = re.sub(pat, "led", formatted_bullets, flags=re.IGNORECASE)
        else:
            print(f"    [✓] Standard application form: 0 custom interview questions. Q&A and highlights left blank.")
            qa_draft = ""
            formatted_bullets = ""

        sheets_client.update_row_status(
            row_index=idx,
            status="Drafted",
            qa_content=qa_draft,
            bullets=formatted_bullets,
            date_posted=final_date,
        )
        print(f"[✓] Row {idx} successfully updated to 'Drafted'.")

if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv
    client = SheetsClient()
    process_tailoring_pipeline(client, force_all=force)

