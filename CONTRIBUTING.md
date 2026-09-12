# Contributing to Catchaj

Thank you for your interest in contributing to **Catchaj**! We are building an intelligent, human-in-the-loop (HITL) job application copilot for experienced professionals who value leverage without sacrificing integrity.

Please read this guide before opening issues or submitting pull requests.

---

## 1. Code of Conduct

All contributors and participants agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please treat fellow community members with kindness, empathy, and respect.

---

## 2. Core Principles to Uphold

Every contribution must honor our three founding principles:

1. **Facts Over Fiction:** Zero hallucination. Every drafted response must strictly ground in the candidate's verified Career Truth Document.
2. **Fit Over Volume:** High thresholds and deliberate constraints. We do not support indiscriminate spam bots or uncurated mass-apply features.
3. **Assistance Over Autopilot:** The system prepares and stages; the human reviews, edits, and makes the final submission decision. The last click belongs to the human.
4. **Anti-Buzzword Pledge:** Prohibit empty AI corporate clichés (*"spearheaded"*, *"leveraged cutting-edge synergies"*, *"proven track record"*). Use direct, metric-driven language.

---

## 3. How Can I Contribute?

### Reporting Bugs
- Check the [existing issues](https://github.com/your-username/catchaj/issues) to avoid duplicates.
- Use our [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md).
- Include minimal reproduction steps, expected vs. actual behavior, and environment details.
- **Never include real API keys, passwords, or personal identifying information (PII) in issue reports.**

### Suggesting Enhancements
- Check existing discussions or issues.
- Use our [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md).
- Articulate the user problem, proposed solution, and alignment with the human-in-the-loop philosophy.

---

## 4. Local Development Setup

### Prerequisites
- Python 3.10 or higher
- Git
- Modern browser (Chromium / Google Chrome for Playwright)

### Step-by-Step Installation

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/catchaj.git
   cd catchaj
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Install pre-commit security hooks:**
   ```bash
   bash scripts/install_hooks.sh
   ```
   *This is mandatory.* The pre-commit scanner prevents accidental leaks of private candidate data, API keys, or private files.

5. **Set up local templates:**
   ```bash
   cp .env.example .env
   cp config.example.py config.py
   cp career_truth_doc.template.md career_truth_doc.md
   cp .pii_patterns.example.json .pii_patterns.json
   ```

---

## 5. Verification & Testing

Before submitting a pull request, run the following test suite:

### 1. Pre-Commit Security & PII Scan Self-Tests
```bash
python3 scripts/pre_commit_scan.py --test
```

### 2. Full Repository Content Scan
```bash
python3 scripts/pre_commit_scan.py $(git ls-files)
```

### 3. Offline Synthetic Dry Run
Runs discovery, triage scoring, and grounded tailoring offline using synthetic fixtures:
```bash
python3 examples/run_synthetic_dry_run.py
```

### 4. Career Truth Synchronization
```bash
python3 sync_truth.py
```

### 5. Python Syntax Check
```bash
python3 -m py_compile *.py scripts/*.py examples/*.py
```

---

## 6. Coding Conventions

- **Python Style:** Follow PEP 8 guidelines. Write clear, type-annotated functions where practical.
- **Imports:** Group standard library imports, third-party libraries, and local modules cleanly. Always provide resilient fallbacks to `config.example.py` for template evaluation.
- **Commit Messages:** Follow [Conventional Commits](https://www.conventionalcommits.org/):
  - `feat: add Greenhouse custom question parser`
  - `fix: handle missing salary range gracefully`
  - `docs: update quick start instructions in README`
  - `test: add unit test for location normalization`
- **Zero Leak Mandate:** Never commit real API keys, email addresses, phone numbers, or private resumes. Always use the synthetic fixtures (`examples/mock_truth_doc.md`, "Alex Morgan").

---

## 7. Submitting Pull Requests

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Commit your changes with clear, descriptive commit messages.
3. Push to your fork:
   ```bash
   git push origin feat/your-feature-name
   ```
4. Open a pull request against the `main` branch. Fill out the [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md).
5. Ensure all automated GitHub Actions checks pass.

Thank you for helping keep Catchaj thoughtful, trustworthy, and high-impact!
