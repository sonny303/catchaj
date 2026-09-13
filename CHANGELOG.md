# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.1] - 2026-09-12

### Fixed
- **Showcase Website Brand Assets:** Fixed broken logo rendering on live production site (`catchaj.sowmya.win`) by bundling `catchaj-logo.png` directly into the Vite build pipeline, placing static root assets in `website/public/`, adding legacy proxy fallback paths (`/__l5e/...`), and implementing graceful browser `onError` fallbacks across all marketing routes (`/`, `/how-to`, `/clexibility`).
- **TypeScript Environment Support:** Added `website/src/vite-env.d.ts` for ambient typing of image imports (`.png`, `.svg`) and Lovable `.asset.json` descriptors.

## [1.0.0] - 2026-09-12

### Added
- **Six-Helper Pipeline:**
  - `pipeline_discover.py`: Automated job scraping across Greenhouse, Lever, Ashby, SmartRecruiters, Workday, and HiringCafe with composite SHA-256 deduplication.
  - `pipeline_evaluate.py`: Multi-criteria triage engine evaluating location constraints, account-gated ATS friction thresholds (85/95 rule), and domain competencies.
  - `pipeline_tailor.py`: Grounded application question drafter enforcing anti-buzzword standards and 100% factual adherence to Career Truth Documents.
  - `run_staged_application.py`: Visible Chromium browser staging via Playwright with mandatory human submission pause.
  - `sync_truth.py`: Ground truth synchronizer and anti-buzzword validator.
  - `learning_agent.py`: Continuous adaptive threshold calibration and user preference learning loop.
- **Privacy & Security Safeguards:**
  - `scripts/pre_commit_scan.py`: Deterministic pre-commit scanner detecting API keys, tokens, PII, and blocked private files with automated self-tests.
  - `scripts/install_hooks.sh`: Helper script to install `.githooks/pre-commit` into local git environment.
  - Sanitized public templates: `.env.example`, `config.example.py`, `career_truth_doc.template.md`, and `.pii_patterns.example.json`.
- **Synthetic Offline Sandbox:**
  - `examples/mock_truth_doc.md`: Verified synthetic baseline for fictional persona "Alex Morgan".
  - `examples/mock_jobs.json`: Realistic mock postings covering Greenhouse, Lever, Ashby, and Workday.
  - `examples/run_synthetic_dry_run.py`: 100% offline, zero-credential end-to-end dry run runner.
- **Web Dashboard & Showcase Website:**
  - `app.py`: Flask-based local review dashboard with two clean views, 1-click decline feedback loop, and staging session control.
  - `docs/`: Accessible, responsive static product marketing and interactive case study showcase ready for GitHub Pages.
- **Open-Source Repository Standards:**
  - Added `LICENSE` (MIT).
  - Added `CONTRIBUTING.md`, `SECURITY.md`, and `CODE_OF_CONDUCT.md`.
  - Added `.editorconfig` and `.gitattributes`.
  - Added `.github/workflows/ci.yml` automated GitHub Actions workflow.
  - Added `.github/` issue and pull request templates.
