# Pull Request & Bug Documentation: Fix Website Logo 404

## 1. Issue / Bug Report

### Title
`[BUG] Logo asset fails to load (404) on live marketing website`

### Description
On the live production website (`https://catchaj.sowmya.win`), the brand logo in the top navigation header and footer rendered as a broken image icon with fallback alt text `Catchaj`.

### Steps to Reproduce
1. Navigate to `https://catchaj.sowmya.win` (or `/how-to`, `/clexibility`).
2. Inspect the site header on the top-left corner.
3. Observe broken image icon `[x] Catchaj`.
4. Inspect Network tab in developer tools:
   - Request: `GET https://catchaj.sowmya.win/__l5e/assets-v1/112562e5-89b5-4ed9-ab4d-99e38b9b096b/catchaj-logo.png`
   - Response: `404 Not Found`

### Root Cause Analysis
1. **Missing Image Binary:** The image binary `catchaj-logo.png` was missing from the `website/` repository directory.
2. **Ephemeral Lovable Dev-Proxy Route:** The route components were importing `catchaj-logo.png.asset.json`, which referenced an internal Lovable sandbox preview path (`/__l5e/assets-v1/...`). In production/live environments outside the Lovable interactive editor session, this proxy route does not exist and returns `404`.

---

## 2. Pull Request Details

### Title
`fix(website): bundle brand logo asset and provide multi-tiered static fallbacks`

### Description
This PR resolves the broken brand logo issue on the live website by properly bundling the high-resolution brand asset into the Vite build pipeline, adding public static fallbacks, and updating route navigation headers and footers with graceful client-side fallbacks.

### Type of Change
- [x] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [x] Documentation update
- [ ] Code refactoring or performance optimization
- [ ] Security or PII scanner enhancement

### Core Principles Checklist
- [x] **Facts Over Fiction:** Changes do not introduce hallucinated outputs or bypass Career Truth Document grounding.
- [x] **Assistance Over Autopilot:** The system halts before final submission; no automated submit button clicks are introduced.
- [x] **Anti-Buzzword Pledge:** No banned corporate clichés (*"spearheaded"*, *"synergy"*, etc.) in templates or output generation.
- [x] **Zero-Leak Security:** No candidate PII, private keys, or API tokens are added or committed.
- [x] **Pre-Commit Tests Passed:** Verified with `.githooks/pre-commit` (all staged files clean).
- [x] **Synthetic Dry Run Passed:** Core python pipelines unaffected; synthetic verification clean.

---

## 3. Implementation Summary

1. **Bundled Asset Added:**
   - Added `website/src/assets/catchaj-logo.png` to enable Vite's asset bundling, hashing, and cache-busting pipeline.
2. **Static & Legacy Fallbacks:**
   - Placed static files in `website/public/catchaj-logo.png` and `website/public/logo.png`.
   - Created static fallback directory `website/public/__l5e/assets-v1/112562e5-89b5-4ed9-ab4d-99e38b9b096b/catchaj-logo.png` for backward compatibility with existing cached bundles.
3. **TypeScript Ambient Types:**
   - Added `website/src/vite-env.d.ts` for clean type definitions of image and asset JSON imports.
4. **Resilient Route Components:**
   - Updated `website/src/routes/index.tsx`, `website/src/routes/how-to.tsx`, and `website/src/routes/clexibility.tsx` to import `catchajLogo` directly, evaluate `logoSrc = catchajLogo || logoAsset.url || "/catchaj-logo.png"`, and supply an `onError` client fallback.

---

## 4. Verification & Live Confirmation

- **Pre-commit Scan:** Ran `.githooks/pre-commit` security & PII scanner. Passed with 0 warnings.
- **Git Commit:** Recorded as `28737c1` on `main`.
- **Live Deployment:** Published and verified live on `https://catchaj.sowmya.win`.
  - Vite bundled the asset to `/assets/catchaj-logo-Bdp-sp6b.png`.
  - Preload `<link rel="preload" as="image" href="/assets/catchaj-logo-Bdp-sp6b.png"/>` renders in `<head>`.
  - Image loads cleanly in header and footer across all breakpoints.
