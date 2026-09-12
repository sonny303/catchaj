# catchaj homepage replacement: product overview & quick-start

## Goal
Replace the current single-page product story with a polished marketing landing page that introduces catchaj as a flexible, installable developer tool and guides visitors to install it locally.

## What I’ll build
- A refreshed hero that positions catchaj as a plug-and-play, human-in-the-loop search and role-resolution engine.
- A features grid covering broadening search, role titles, domain locations, the plugin system, CLI/library support, the continuous learning agent, and the AI-powered agentic build system.
- A quick-start section with prerequisites, clone/install steps for Node, Python, and Docker, plus a runnable CLI example.
- A contribute/help footer with license, community, and support links.
- Primary CTA: "Install locally" leading to the quick-start block.
- Use the product name “catchaj” consistently across page copy and metadata.

## Visual direction
- Reuse the existing warm-paper editorial palette (archival paper base, deep forest ink, sage/olive accents, lime for status).
- Keep the current typography pair and tactile stamps.
- No gradients, no decorative color, 1px borders, 4px spacing grid.
- Large touch targets and responsive layouts for 320px and up.

## Technical details
- Update `src/routes/index.tsx` with the new sections, accessible headings, and keyboard-friendly structure.
- Update `src/data/catchaj.ts` with the overview copy, install commands, feature list, and quick-start data.
- Preserve the route head() with fresh title, description, and OG/Twitter metadata matching the new positioning.
- Keep the shared header/footer pattern and navigation anchors within the page where appropriate.
- No backend, auth, or external API dependencies.

## Validation
- Check the build output and TypeScript errors.
- Open the preview at desktop and mobile widths to confirm readable code blocks, tap targets, and visual rhythm.
- Verify SEO metadata in the page source.
