# Atlas Template

Use when the source is a typed atlas model – an **Architecture Model** (`architecture-model.json`, owner: the `andthen:map-codebase` skill) or a **Domain Model** (`domain-model.json`, owner: the `andthen:ubiquitous-language` skill). Detection: JSON parses AND `kind === "architecture-model"` or `kind === "domain-model"` (each with its own schemaVersion guard per SKILL.md). One renderer serves both kinds; the domain lens keys off the model `kind`.

**This artifact type renders via the bundled deterministic renderer, not by hand-authoring HTML.** The render is an immersive 3D atlas – orbit/pan camera with zoom-at-cursor, perspective-projected drafting sheets, LOD labels, focus tweens, mini-map, tours, search, list-view fallback – built on a hand-rolled Canvas2D engine. That surface cannot be reliably hand-emitted per render; the app lives in `templates/atlas.html` and the script only validates, injects, and seals it. Do not hand-write atlas HTML; do not edit the script's output.

## Render procedure

1. Compute the output path per the SKILL.md convention (`.agent_temp/visual-review/<slug>-<timestamp>.html`).
2. Run the bundled renderer (Node ≥18, no dependencies):

```bash
node "${CLAUDE_SKILL_DIR}/scripts/render-atlas.mjs" "<artifact-path>" "<output-path>"
```

3. On success the script prints a JSON summary (counts, bytes). Open the output per the SKILL.md *Browser-Open Detection* step and print the path.
4. On failure the script exits 1 with itemized validation errors (dangling refs, duplicate ids, enum violations, missing `ref`). That means the artifact deviates from the `architecture-model.md` contract – report the errors verbatim and route the fix to the model's owner (the `andthen:map-codebase` skill for an architecture model, the `andthen:ubiquitous-language` skill for a domain model); do not patch the model or the output by hand.

The renderer owns the full experience contract: cyanotype drafting identity, deterministic sort-by-id layout (identical model → identical atlas, byte for byte), painter's-order 3D projection with fog and DOM-label LOD, hover/focus highlighting with edge verb labels, detail panel (kind chip, inert `ref` code, metrics, clickable edge list, evidence badges – `inferred` renders dashed), fuzzy search, context legend and kind lens chips (data-driven from the model's node kinds), tours (model-provided, else a generic context tour), mini-map with click-to-aim, a 2D List view that doubles as the no-canvas fallback, and the standard notes machinery (localStorage, restore prompt, beforeunload guard, "No notes to copy") with clipboard payload owner keyed by `kind` – `andthen:map-codebase` or `andthen:ubiquitous-language`.

**Domain lens** (`kind === "domain-model"` only; architecture rendering takes none of these paths): a node with `meanings` floats between its meaning contexts' sheets – positioned purely from the resolved sheets' deterministic positions, drawn on no single sheet – with one dashed tether per meaning labelled by the verbatim doc label; floating-term labels render italic; the detail panel adds strikethrough `avoid` chips and a per-context meanings list; the List view and no-canvas fallback include meanings and avoid terms.

**Theme exception:** the atlas is intentionally dark and immersive – a deliberate divergence from the visualize light theme, per the SKILL.md exception. It still honors `prefers-reduced-motion` (instant cuts, no inertia) and keeps text contrast ≥ 4.5:1.

**Safe Output Boundary:** model strings reach the DOM via `textContent` only; `ref` is never a link; the single inline script is SHA-256-hashed into the CSP; the page makes zero external requests and works offline from `file://`.

## Fallback (no Node available)

Only when `node` is genuinely unavailable: print the exact render invocation from step 2 (for the user to run once Node ≥18 exists) and a brief summary read from the model JSON – project name plus context/node/edge counts – then stop. No hand-authored substitute: do not recreate the 3D app and do not degrade to a document render; the model JSON itself remains readable as the honest fallback.
