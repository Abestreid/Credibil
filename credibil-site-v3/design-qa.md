# Credibil design QA

## Visual target

- Direction: Editorial Intelligence / Dossier 01
- Reference: `/workspace/design-previews/credibil/option-1-editorial-intelligence.png`
- Browser capture: `/workspace/scratch/credibil-implementation-desktop.jpg`
- Side-by-side comparison: `/workspace/scratch/credibil-qa-comparison.png`
- Reference viewport: 1440 × 900
- Browser viewport: 1348 × 926

## Comparison

The implementation preserves the selected direction's defining relationships: a full navy evidence surface, oversized ivory headline, search as the primary conversion action, a large real product capture, restrained green status/action color, compact metadata typography, and the vertical dossier rail.

Deliberate refinements:

- The primary action uses Credibil green instead of the concept's blue, matching the supplied brand assets.
- The product proof combines the supplied company and relationship captures so the first viewport shows both identity and corporate context.
- The header uses the confirmed RO/EN language model and the approved public-site information architecture.

## Browser checks

- One `h1`, eleven section `h2` headings, no horizontal page overflow at 1363 px.
- Search autocomplete returns four realistic results and closes after selection.
- Hero and final search both preserve the query and open the authentication dialog.
- Product tabs update `aria-selected`, copy, and the real screenshot.
- RO/EN switch updates visible content and the document language.
- Navigation anchors reach product, monitoring, and MOLDAC sections.
- FAQ uses native expandable details.
- Console contains no application errors. Recorded errors are isolated to the cloud-browser extension.
- Reduced-motion handling, visible focus styles, mobile menu, stacked mobile layouts, and 44 px or larger primary controls are present in the responsive CSS.

## Result

Pass. The first viewport closely matches the selected visual target while the remaining page extends the same editorial evidence system without introducing a generic SaaS card language.
