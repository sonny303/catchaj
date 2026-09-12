## Description

Brief summary of the changes introduced by this pull request.

## Type of Change

- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Documentation update
- [ ] Code refactoring or performance optimization
- [ ] Security or PII scanner enhancement

## Core Principles Checklist

- [ ] **Facts Over Fiction:** Changes do not introduce hallucinated outputs or bypass Career Truth Document grounding.
- [ ] **Assistance Over Autopilot:** The system halts before final submission; no automated submit button clicks are introduced.
- [ ] **Anti-Buzzword Pledge:** No banned corporate clichés (*"spearheaded"*, *"synergy"*, etc.) in templates or output generation.
- [ ] **Zero-Leak Security:** No candidate PII, private keys, or API tokens are added or committed.
- [ ] **Pre-Commit Tests Passed:** Verified with `python3 scripts/pre_commit_scan.py --test`.
- [ ] **Synthetic Dry Run Passed:** Verified with `python3 examples/run_synthetic_dry_run.py`.

## Testing Conducted

Describe the tests executed locally to verify your changes.
