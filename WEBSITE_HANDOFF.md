# Catchaj — showcase website

## Proposed change / PR brief

**Title:** Add a GitHub Pages product case study for Catchaj

**User story:** As a visitor evaluating product management and AI building work, I want to understand the problem, explore the six-helper workflow, and see the rules in action, so I can assess the thinking behind the prototype.

**Requirements:**
- One responsive static page with no application backend, credentials, tracking, or build step.
- A distinct editorial identity, using Catchaj as the proposed project name.
- All six helpers, three product decisions, and an explicit human submission handoff.
- Interactive accessible helper tabs and a sample score/location/friction rules demo.
- Correct 85/95 thresholds, with location rejection overriding score.
- Synthetic examples only; no live application actions or fabricated impact metrics.
- Accurate prototype status and visible limits of grounding, privacy safeguards, scheduling, and browser support.

## Scope

Only `docs/` is the publishable site. The existing Python application is separate. External Google Fonts are optional; system fonts remain available when offline. The page sends no form or demo data and uses no local storage.

## Local preview

From this repository: `python3 -m http.server 4173 --directory docs --bind 127.0.0.1`

Open `http://127.0.0.1:4173`. Stop the server with Ctrl+C when finished.

## GitHub Pages publication

Publishing requires the user's approval and a chosen GitHub repository. This checkout initially had no commits or remote. No commits, pushes, or remote PRs have been created by this website change.

Prefer a separate showcase repository containing only the contents of `docs/`, served from `main` → `/ (root)`. Alternatively, if using a suitably reviewed repository, serve `main` → `/docs`. Use GitHub repository Settings → Pages to select the source. Assets and links are relative and support a repository subpath.

The entire repository has undergone a comprehensive sanitization pass and adheres to public git repository best practices (all candidate-specific PII removed, generic synthetic fixtures integrated, and deterministic pre-commit leak prevention active). The static site in `docs/` is self-contained and ready for GitHub Pages.

## Evidence limits

The website demonstrates the proposed product experience and gating rules. It does not verify the underlying job discovery providers, email/Sheets integration, grounded generation, unattended operation, or browser submission workflow. No quantified time savings or hiring outcomes are claimed.

## Fresh verification

- JavaScript syntax, unique HTML IDs, anchor destinations, and local assets: passed.
- All six helper panels and arrow-key tab navigation: verified in the browser.
- Score boundaries 84/85 and account-gated 94/95: correct decisions.
- Out-of-area location at score 100: rejected.
- Desktop (1280px), mobile (390px), and narrow mobile (320px): no horizontal overflow after the mobile illustration fix.
- Mobile hero and scoring controls: visually inspected.
- Browser error log: no errors during interaction checks.
- Website files passed the existing repository content scanner. This is scoped to the site, not a full source-repository privacy audit.
- `catchaj-website.zip` contains only the five static files from `docs/`, ready for a separate showcase repository.
