# catchaj.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Security: Pre-Commit Scan](https://img.shields.io/badge/Security-Pre--Commit%20Shield-green.svg)](scripts/pre_commit_scan.py)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Status: Prototype](https://img.shields.io/badge/Status-Prototype%20with%20Intent-orange.svg)](docs/index.html)

> *Your next chapter. Less of the copy-paste.*

**Catchaj** is an intelligent, human-in-the-loop (HITL) job application copilot built for experienced professionals who want leverage without sacrificing integrity.

Instead of mass-spamming hundreds of job boards with generic AI-generated cover letters, Catchaj assembles a coordinated crew of six focused AI helpers to handle the soul-crushing administrative busywork — discovering roles, evaluating genuine alignment, drafting authentic application answers, and pre-filling ATS web forms in a real browser.

**The most important feature is a pause.** The system prepares everything, including filling out the application form in a visible browser window, but it *strictly never clicks submit*. The final handoff belongs to the human.

---

## Three Guiding Principles

| | Principle | What it means |
|:--|:--|:--|
| 01 | **Facts over fiction** | Every draft is grounded in a verified Career Truth Document. If an accomplishment isn't documented, the AI is blocked from saying it. Zero hallucinations, zero buzzwords. |
| 02 | **Fit over volume** | Roles are scored 0–100 against strict criteria. Location mismatches are rejected immediately — even with a perfect score. Account-gated applications raise the bar to 95+. |
| 03 | **Assistance over autopilot** | The system finds, filters, drafts, and stages. You review, edit, and decide whether to press submit. |

---

## The Six Helpers

```
┌──────────────┬──────────────┬──────────────┬─────────────┬─────────────┐
│ 01. The      │ 02. The      │ 03. The      │ 04. The     │ 05. The     │
│ Fact-Checker │ Job Scout    │ Strict Judge │ Essay       │ Browser     │
│              │              │              │ Drafter     │ Copilot     │
│ (Career      │ (Discovery   │ (Scoring &   │ (Grounded   │ (Staging    │
│ Truth Doc)   │ & Dedupe)    │ Gatekeeping) │ Tailoring)  │ in Chrome)  │
└──────┬───────┴──────┬───────┴──────┬───────┴──────┬──────┴──────┬──────┘
       │              │              │              │             │
       └──────────────┴──────────────┼──────────────┴─────────────┘
                                     │
                             06. The Privacy Guard
                             (PII / Secret Shields)
                                     │
                             ▼ [THE PAUSE] ▼
                       Human Reviews & Clicks Submit
```

| Helper | Role | Working Rule |
|:-------|:-----|:-------------|
| **The Fact-Checker** | Ingests verified resume & interview notes into an immutable Career Truth Document | *"If it isn't in the Truth Document, it doesn't belong in the answer."* |
| **The Job Scout** | Scrapes job boards, fingerprints postings via SHA-256 to eliminate duplicates, detects the ATS platform | *"Find the possibilities. Skip the repeats."* |
| **The Strict Judge** | Evaluates fit score (0–100) with hard location and platform friction rules | *"85+ for clean forms; 95+ when extra accounts get in the way."* |
| **The Essay Drafter** | Drafts concise (120–180 word) answers grounded 100% in real candidate facts | *"Specific beats impressive-sounding."* |
| **The Browser Copilot** | Launches a visible browser, autofills fields, attaches PDF resume, and stages the tab | *"The last click belongs to you."* |
| **The Privacy Guard** | Pre-commit hooks and local scanners prevent PII, secrets, or API keys from leaking | *"Keep personal things personal."* |

---

## Tech Stack

`Python` · `Google Gemini` · `Playwright` · `JobSpy` · `Google Sheets` · `Human Judgment`

---

## Quick Start

### 1. Clone and set up

```bash
git clone https://github.com/your-username/catchaj.git
cd catchaj
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure your profile

```bash
# Copy the templates
cp .env.example .env
cp config.example.py config.py
cp career_truth_doc.template.md career_truth_doc.md
cp .pii_patterns.example.json .pii_patterns.json

# Edit with your real details
# - .env: API keys and notification settings
# - config.py: Your candidate profile and search criteria
# - career_truth_doc.md: Your verified career facts
# - .pii_patterns.json: Your PII patterns for leak detection
```

### 3. Install security hooks

```bash
bash scripts/install_hooks.sh
```

This installs a pre-commit hook that scans every staged file for:
- High-entropy secrets (API keys, private keys, tokens)
- Candidate PII (email, phone, name)
- Blocked private files

### 4. Try the synthetic dry run

```bash
python3 examples/run_synthetic_dry_run.py
```

Runs the full pipeline end-to-end using synthetic "Alex Morgan" fixtures — no API keys, no network, no real candidate data needed.

### 5. Run for real

```bash
python3 orchestrator.py
```

---

## Project Structure

```
catchaj/
├── orchestrator.py          # Master CLI entry point
├── pipeline_discover.py     # Job board scraping & deduplication
├── pipeline_evaluate.py     # Location & ATS account-gate triage
├── pipeline_tailor.py       # Grounded application drafting
├── run_staged_application.py # Playwright HITL browser staging
├── sync_truth.py            # Career Truth Document sync & validation
├── sheets_client.py         # Google Sheets pipeline logging
├── notifier.py              # Email alert notifications
├── daemon.py                # Background scheduler
├── learning_agent.py        # Feedback learning loop
├── config.example.py        # Public config template (→ copy to config.py)
├── .env.example             # Public env template (→ copy to .env)
├── career_truth_doc.template.md  # Career truth schema template
├── .pii_patterns.example.json    # PII scanner config template
├── scripts/
│   ├── pre_commit_scan.py   # Deterministic leak-prevention scanner
│   └── install_hooks.sh     # Git hook installer
├── examples/
│   ├── mock_truth_doc.md    # Synthetic career doc (Alex Morgan)
│   ├── mock_jobs.json       # Synthetic job postings
│   └── run_synthetic_dry_run.py  # Offline end-to-end test
└── docs/                    # Static marketing site
    ├── index.html
    ├── styles.css
    ├── app.js
    ├── favicon.svg
    └── .nojekyll
```

---

## Security & Privacy

- **Zero-leak architecture:** Private files (`config.py`, `.env`, `career_truth_doc.md`, `resume.pdf`) are gitignored and blocked by pre-commit hooks even if force-staged.
- **Deterministic scanning:** The pre-commit scanner uses regex-based detection for secrets across major providers (Google, OpenAI, Anthropic, AWS, GitHub, Stripe, HuggingFace) and candidate PII patterns.
- **Synthetic sandbox:** All examples use the fictional "Alex Morgan" persona — safe for demos, screenshots, and public sharing.
- **Local execution:** No data leaves your machine except explicit API calls you configure.

Run the security self-tests:

```bash
python3 scripts/pre_commit_scan.py --test
```

---

## Status

> **`PROTOTYPE WITH INTENT`** — This is a working product experiment exploring the intersection of AI assistance and human agency in the job search process.

## Community & Contributing

- [Contributing Guide](CONTRIBUTING.md) — How to report bugs, suggest features, and submit pull requests.
- [Security Policy](SECURITY.md) — How we protect candidate privacy and how to report vulnerabilities.
- [Code of Conduct](CODE_OF_CONDUCT.md) — Our community standards and expectations.
- [Changelog](CHANGELOG.md) — Version history and release notes.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

*A product management × AI building experiment.*  
*Built with AI. Designed around a human.*

