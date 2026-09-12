# Catchaj three-page narrative redesign

## Goal
Reorganize Catchaj into one cohesive story with a clear purpose for every page:

```text
Why we built this  →  How to use it  →  How we designed it
Homepage              /how-to           /clexibility
```

The selected **Balanced Narrative Editorial** direction will guide all three pages: a focused single-column rhythm, Instrument Serif with Work Sans, and a light/dark system built from `#F7F8FA`, `#071F3D`, `#116BEE`, and `#E1EBF7`.

## 1. Homepage — why we built this
- Restore the v1 “Your next chapter. Less of the copy-paste.” opening and layered career-truth/application visual from the supplied reference.
- Center the page on the human problem: high-caliber professionals lose time to repetitive applications, while indiscriminate automation erodes trust.
- Tell the product thesis through three concise chapters: facts over fiction, fit over volume, and assistance over autopilot.
- Reintroduce the six-helper crew only as a compact narrative overview; detailed mechanics move to How to use.
- Make “the most important feature is a pause” the emotional culmination, explaining that Catchaj stages applications but never submits them.
- End with clear paths to “See how it works” and “Read the philosophy.”

## 2. How to use — product and quick start
- Move the current “Search wider. Resolve context. Build faster.” experience to a dedicated `/how-to` page.
- Retain the useful substance: capabilities, continuous-learning agent, build system, prerequisites, Node/Python/Docker installation, CLI example, contribution, and help.
- Reorder it into a practical sequence: understand the system → choose an interface → install → run a first query → extend.
- Tighten repeated marketing claims so this page answers “what does it do and how do I start?” rather than retelling the homepage motivation.
- Preserve readable code blocks, scannable requirements, and direct installation actions.

## 3. Clexibility — design philosophy
- Keep the pronunciation, Clear + Explainable + Extensible equation, and all nine accordion entries.
- Redesign the opening as a more immersive editorial statement with oversized typography, navy contrast sections, and electric-blue details.
- Add a concise bridge showing how Clexibility governs search, roles, learning, and auditability without repeating the full product overview.
- Give the accordion a stronger progressive rhythm and clearer selected state.
- Add restrained motion: staged text reveals, subtle path/line movement, accordion transitions, and a breathing status cue; respect reduced-motion settings.

## Shared experience
- Use the supplied Catchaj bird/path logo as the real site brand asset and derive the favicon from it.
- Introduce consistent navigation: “Why we built this,” “How to use,” and “Clexibility,” with a clear active state.
- Apply the selected navy/electric-blue palette through semantic design tokens, with mostly light storytelling and intentional dark sections.
- Keep borders thin, corners restrained, spacing generous, and interactions accessible from keyboard and touch.
- Ensure each page has one distinct promise and next step, while shared visual motifs make the journey feel continuous.

## Content boundaries
- **Homepage owns:** audience tension, values, human review, and the reason Catchaj exists.
- **How to use owns:** features, workflow, technical setup, examples, and support.
- **Clexibility owns:** principles, definitions, explainability, and system-design rationale.
- Shared statements appear only as short connective references, preventing repetitive sections.

## Technical details
- Create the `/how-to` route and update the existing `/` and `/clexibility` routes.
- Reuse the current structured product data, adding only narrative content needed for the restored homepage.
- Update semantic color and typography tokens; load Instrument Serif and Work Sans through route head links.
- Store the supplied logo through the project asset flow and use an optimized real favicon file.
- Give every page unique title, description, Open Graph text, canonical URL, and Twitter card metadata.
- Implement in small batches to respect the project’s three-file-per-change limit.

## Validation
- Verify all three pages and their navigation at desktop, tablet, and 320px mobile widths.
- Check logo rendering, layout continuity, accordion keyboard behavior, code-block overflow, reduced-motion behavior, and absence of horizontal scrolling.
- Confirm page-specific metadata and clean browser console output.
