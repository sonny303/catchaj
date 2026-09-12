# Add a dedicated Clexibility page

## Goal
Create a separate `/clexibility` route that explains Catch‑a‑J's core design philosophy, using an accordion for the nine letter aspects and a clear definition up front.

## What I'll build
- New route `src/routes/clexibility.tsx` mapped to `/clexibility`.
- Hero/intro section with the pronunciation, the "Clexibility = Clear + Explainable + Extensible" summary, and the table's nutshell paragraph.
- Accessible accordion for the nine aspects (C, L, E, X, I, B, I, L, I, T, Y), each with a one-line heading and short explanation from the brief.
- Navigation link added to the existing header, pointing to `/clexibility`.
- New data export in `src/data/catchaj.ts` with the Clexibility content so the route stays data-driven.
- Route-specific `head()` metadata (title, description, OG/Twitter, canonical `/clexibility`).

## Visual direction
- Reuse the warm paper-and-ink palette, DM Sans/Newsreader/Space Mono typography, and existing utility classes.
- Keep 1px borders, rounded-md cards, no shadows, 4px spacing grid.
- Use the `icon-tile`, `eyebrow`, and `nav-link` utilities where appropriate.
- Accordion uses shadcn/ui `Accordion` if available; otherwise builds a small accessible collapsible list with disclosure buttons and `aria-expanded`.

## Technical details
- File changes: `src/routes/clexibility.tsx`, `src/routes/index.tsx` (header nav only), `src/data/catchaj.ts`.
- `src/routes/clexibility.tsx` imports `clexibilityAspects` and `clexibilitySummary` from `src/data/catchaj.ts`.
- Header in `src/routes/index.tsx` gets a new `<Link to="/clexibility">Clexibility</Link>` alongside Capabilities/Agents/Install/Get help.
- No backend, auth, or external API dependencies.

## Validation
- Check build output and TypeScript errors after adding the route.
- Open `/clexibility` at desktop and mobile widths to confirm the accordion opens/closes, tap targets are ≥44px, and text is readable.
- Verify SEO metadata appears in the page source for `/clexibility`.
