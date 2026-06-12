# Changeset Walkthrough Template

Use when the source is a **Changeset Walkthrough** produced by the `andthen:explain-changes` skill. Detection: H1 starts with "Changeset Walkthrough"; OR H2 set contains BOTH "Change Map" AND "Change Narrative".

Walkthroughs are *comprehension, not judgment* – risk tags mean "where careful reading pays off", never defects, and nothing renders as a verdict. Unlike the document-shaped artifacts, a changeset is explored, not read: the render is an interactive app with four perspectives (Overview / Tour / Files / Architecture) over the same data.

**This artifact type renders via the bundled deterministic renderer, not by hand-authoring HTML.** The render is an interactive application – tabbed views, a guided cluster stepper with a docked module map, collision-free SVG layout, zoom/pan, a command palette, filterable tables, sunburst and mosaic visuals, animation and keyboard navigation. That surface is far beyond what any model can reliably hand-emit per render (hand-authored attempts produce overlapping SVG labels and dead scripts), so layout math, diagram geometry, and the interaction layer are computed by a script and verified by built-in assertions. Do not hand-write the app HTML; do not "improve" the script's output by editing it.

## Render procedure

1. Compute the output path per the SKILL.md convention (`.agent_temp/visual-review/<slug>-<timestamp>.html`).
2. Run the bundled renderer (Node ≥18, no dependencies):

```bash
node "${CLAUDE_SKILL_DIR}/scripts/render-changeset.mjs" "<artifact-path>" "<output-path>"
```

3. On success the script prints a JSON summary (counts, assertions passed). Open the output per the SKILL.md *Browser-Open Detection* step and print the path.
4. On script failure, the error names the offending artifact line – it almost always means the artifact deviates from the `andthen:explain-changes` template contract (Change Map columns, cluster H3 shape, `@@ path:line @@` fence heads, closed vocabularies). Report the error verbatim and point at the artifact line; do not patch the renderer output by hand.

The renderer owns the full experience contract for this type: App Shell with perspective tabs, linked cluster model with per-cluster hues, change mosaic (full-basename tiles, risk fill, churn mini-bars), cluster cards with sparklines, guided Tour stepper with docked module mini-map and mark-reviewed ledger, facet-filterable Files table with delta bars and directory sunburst, full-width Architecture map with text-fit nodes, collision-free edge labels, zoom/pan, blast-radius hover and flow playback, ⌘K command palette, keyboard navigation, reading-progress bar, reduced-motion discipline, JS-off stacked fallback – plus the standard notes machinery (Section Block affordances, LocalStorage, clipboard payload with owner `andthen:explain-changes`) byte-compatible with every other render.

## Fallback (no Node available)

Only when `node` is genuinely unavailable: render a plain document fallback using `templates/render-shell.md` (two-pane shell, one Section Block per H2, Generic Prose bodies, diff fences as plain `<pre>` blocks), and tell the user the interactive changeset experience requires Node ≥18. Do not attempt to recreate the app shell, diagrams, or interactions by hand – a degraded-but-honest document beats a broken imitation.
