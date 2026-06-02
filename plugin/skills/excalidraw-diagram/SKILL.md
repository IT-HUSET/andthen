---
description: Create high visual quality Excalidraw diagrams that communicate with clarity and intuition. Produces educational, visually rich diagrams where structure and design do the explaining. Trigger on 'draw this architecture', 'make a workflow diagram', 'create an Excalidraw diagram'.
argument-hint: "<topic-or-source> [output-dir]"
---

# Create Excalidraw Diagram

The output is a `.excalidraw` source file plus a rendered PNG that has been visually reviewed.


## VARIABLES

TOPIC: $1 (required – what to visualize: inline description, file path, URL, or concept reference)
OUTPUT_DIR: $2 (defaults to `<project_root>/docs/diagrams/` if not provided)

### Variable Validation
- If `TOPIC` is empty, **STOP** with a missing-input error that states the visualization topic is required
- Create `OUTPUT_DIR` if it does not exist
- Resolve a stable output name before writing files


## INSTRUCTIONS

- **Diagram generation only** – produce the `.excalidraw` source and rendered PNG, not implementation code
- **Resolve references first** – read the style guide, element-format, and composition-playbook before writing any shape (ordered list in Phase 2.1)
- **Commit to a Layout Contract before JSON** – Phase 1.5 below. Skipping this is the #1 cause of flat, AI-generic results.
- **Label shorthand renders; portable form ships.** Use `label` on shapes for auto-centered text (with explicit `width`/`height`), then save via `window.getConvertedJSON()` (Phase 5) or the file opens as empty boxes in `app.excalidraw.com`.
- **Technical diagrams must be grounded in reality** – use real API names, data shapes, events, and method signatures, not placeholders
- **Render-and-validate loop is mandatory** (Phase 3) and uses `agent-browser` (`npm install -g agent-browser && agent-browser install` if not installed)
- **Design refinement and final QC** – Phase 4 combines design review (via the `andthen:ui-ux-design` skill in `review` mode) and visual validation (via the `andthen:visual-validation` skill in a sub-agent when fresh context is useful). Fall back to self-evaluation using the criteria in Phase 4 if sub-agents are not supported


## GOTCHAS

- **Uniform grid = AI-aesthetic failure** – 6+ shapes with identical `(type, width, height, backgroundColor)` is the defining generic look. Apply the Anti-Uniformity Rule from the style guide: anchor shape every 3–4 items, alternating row heights, or an evidence artifact insertion.
- **Implied connections** – Phase headers sitting above their children, or two boxes near each other, communicate nothing. Every relationship needs an **explicit arrow** or a line+text tree structure.
- **Ellipses/diamonds are hungry** – for the same label, an ellipse needs ~1.4× a rectangle and a diamond needs ~2×. Hard-coding identical widths produces clipping; under-sized `width` also lets `redrawTextBoundingBox` silently expand the container, so over-size – cascade numbers are floors. See `element-format.md` § Label Auto-Sizing.
- **Label shorthand vs portable form** – the `label` form is render-only; export via `window.getConvertedJSON()` before saving (Phase 5 owns the contract), or the file opens as empty boxes in `app.excalidraw.com`.
- **Arrow routing** – arrows crossing through elements. Add intermediate waypoints in the `points` array.
- **Too small text** – minimum `fontSize: 16` for body, `20` for titles. Below 14 is unreadable. Scale up at XL/XXL canvas sizes.
- **JSON truncation** – generating the entire diagram in one pass hits output token limits. Build section-by-section for non-trivial diagrams.
- **Skipping the render loop** – JSON cannot prove the visual result; see Phase 3 (MANDATORY).
- **Forgetting `fillStyle: "solid"`** – without it, `backgroundColor` won't show.
- **Emoji in text** – emoji don't render in Excalidraw's font. Use shapes instead.
- **Off-grid coordinates** – snap all `x`, `y`, `width`, `height` to multiples of 20. Arbitrary values (x: 143, 287) produce an "almost aligned" look that reads as sloppy.
- **ES-module readiness race** – on cold load, the `esm.sh` module graph for `@excalidraw/excalidraw` takes 30s+, exceeding the 25s default `agent-browser wait` timeout. `AGENT_BROWSER_DEFAULT_TIMEOUT` and `--timeout` are **not honored by `wait --fn`** (verified empirically). Use the bash polling loop in Phase 3.2; do not rely on `sleep 2` (it only works when the module is cached from a prior session).


## WORKFLOW

### Phase 1: Discovery and Design

#### 1.1 Validate Input
- Read `TOPIC`
- If `TOPIC` is a file path or URL, read it first
- Determine the core teaching goal: what must the viewer understand after five seconds?

#### 1.2 Choose Diagram Depth
Decide which mode applies:

- **Conceptual** – mental model, pattern, or relationship map; no code or real payloads required
  - **Signals**: user says "explain how X works conceptually", topic is a design pattern, or audience is non-technical
- **Technical / Architectural** – real systems, APIs, protocols, or implementation flows; evidence artifacts are required
  - **Signals**: user names specific technologies, topic involves protocols or APIs, or diagram will serve as reference documentation

When in doubt, choose technical. Concrete details usually improve the result.

#### 1.3 Research Reality (Technical Diagrams)
Gather real data formats/schemas, method signatures, API endpoints, event names, and communication protocols. Generic labels (`"Service A" → "Service B"`) communicate nothing; use specifics (`"OrderService.create() → Stripe /v1/charges POST → webhook /api/webhooks/stripe"`). For external APIs, spawn a sub-agent that consults the project's `## Documentation Lookup Tools` section, invoke the dedicated `documentation-lookup` agent when available, or use project docs.

#### 1.4 Map Concepts to Visual Patterns
Use the Pattern Catalog from `references/composition-playbook.md` § Visual Patterns (enumerated in Phase 2.1). Each major concept gets a different pattern. Do not make every section look like the same card layout.

#### 1.5 Layout Contract (MANDATORY)

**Write the contract down before opening JSON.** Skipping this step is the #1 cause of uniform-grid, AI-generic output. The contract is ~10 lines, not a document.

Pick an archetype from `references/composition-playbook.md` (Pipeline, Architecture, Taxonomy, Lifecycle, Comparison, or a combination). Then commit, in plain text:

1. **Narrative spine** – one sentence: "X enters, transforms through Y, exits as Z." Or "These are the kinds of X, here's what overlaps."
2. **Archetype** – which playbook recipe you are adapting.
3. **Directional axis** – left→right, top→bottom, radial, or none (taxonomy). Once chosen, 90% of primary arrows travel this axis.
4. **Hero** – name the single most important element. Declare its size (`320×160`, used **once**) and its 160px breathing-room commitment.
5. **Size cascade** – confirm `hero : primary : secondary ≈ 3 : 1.8 : 1` using concrete numbers (e.g., `320×160 / 180×90 / 120×60`). Ellipses and diamonds up-size from these per `element-format.md` § Label Auto-Sizing.
6. **Shape vocabulary** – which Excalidraw shape types are in use and what each means (rectangle = service, ellipse = state, etc.). Max 4 types.
7. **Zone plan** – 2–4 zones, each with a color family from the semantic overlay (Blue = core, Violet = AI/data, Teal = runtime, Bronze = external, etc.) and a `x/y/width/height` on the 20px grid.
8. **Canvas size** – S/M/L/XL/XXL per `style-guide.md` § Canvas Sizing. Prefer 4:3.
9. **Evidence artifacts** – count (technical diagrams: at least 1; ratio ~1 per 4–6 abstract nodes).
10. **Rhythm breakers** – how you avoid a uniform grid for any category with ≥ 6 items (anchor upsize / alternating row heights / evidence insertion).

**Gate**: The contract is written. The diagram has a clear narrative, chosen archetype, locked axis, named hero, committed size cascade, shape vocabulary, zone plan, canvas size, evidence artifact count, and anti-uniformity strategy.


### Phase 2: Generate JSON

#### 2.1 Resolve References
Read, in this order:
1. Project-specific diagram style guide from the Document Index, if present
2. Otherwise `references/style-guide.md` – colors, size cascade, signal badges, density gradient, Anti-Uniformity Rule, **Shape Vocabulary (§ 5 Shape Styling)**, and **Design Principles family (§ 12: Structure/Specificity litmus tests, Evidence Artifacts, Multi-Zoom Rule, Text Placement Strategy, Box-budget rule)**
3. `references/element-format.md` – JSON shape, label auto-sizing math, font metrics
4. `references/composition-playbook.md` – archetype recipes (pipeline / architecture / taxonomy / lifecycle / comparison) AND **Pattern Catalog (§ Visual Patterns: Fan-out, Convergence, Tree, Timeline, Spiral/Cycle, Cloud, Assembly Line, Side-by-Side, Gap/Break)**

These files are the source of truth for visual styling, JSON shape rules, and design quality. Your Layout Contract from Phase 1.5 keyed off them; now you are executing it.

#### 2.2 Create Base File
Write the initial `.excalidraw` document to _`OUTPUT_DIR`_:

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [],
  "appState": {
    "viewBackgroundColor": "#ffffff",
    "gridSize": 20
  },
  "files": {}
}
```

#### 2.3 Build One Section at a Time
For each logical section: (1) add zone backgrounds, (2) add primary shapes with `label` fields, (3) add arrows and bindings, (4) add free-floating headings and annotations, (5) add evidence artifacts (technical diagrams). Use descriptive IDs (`ingest_service`, `webhook_arrow`), namespace seeds per section (section 1: `100xxx`), reuse style-guide color families, and update cross-section bindings when arrows connect to previous sections.

#### 2.4 Review the Complete JSON
Before rendering, verify:
- Every referenced `elementId` exists
- Cross-section arrows point to the correct elements
- IDs are unique
- Font sizes and spacing follow the style guide

**Gate**: A complete JSON document exists and is internally consistent


### Phase 3: Render and Self-Review (MANDATORY)

Render and inspect the image.

#### 3.1 Locate Render Template
Resolve the absolute path to `references/render_template.html`.

#### 3.2 Render with agent-browser

```bash
# 1. Open the render template
agent-browser open "file://<absolute-path-to-skill>/references/render_template.html"

# 2. Wait up to 60s for the Excalidraw ES-module graph to resolve from esm.sh.
#    The template sets window.__moduleReady = true once ready. The default
#    agent-browser wait timeout is 25s, a cold ESM load can take 30s+, and
#    neither AGENT_BROWSER_DEFAULT_TIMEOUT nor any --timeout flag is honored
#    by `wait --fn`. Poll the readiness flag directly:
for i in $(seq 1 60); do
  [[ "$(agent-browser eval 'String(window.__moduleReady)' 2>/dev/null)" == '"true"' ]] && break
  sleep 1
done

# 3. Inject the diagram JSON and render
#    Read the .excalidraw file content, then inject via eval
agent-browser eval --stdin <<'JSEOF'
const data = <PASTE_OR_READ_DIAGRAM_JSON_HERE>;
await window.renderDiagram(data);
JSEOF

# 4. Screenshot the result. Use AGENT_BROWSER_FULL=true for a full-page capture
#    at the diagram's native dimensions – no viewport sizing required.
AGENT_BROWSER_FULL=true agent-browser screenshot <OUTPUT_DIR>/<name>.png
```

The `renderDiagram` function validates the JSON before rendering. If validation fails, it returns `{ success: false, validationErrors: [...] }` with specific messages (e.g. missing `"type": "excalidraw"`, empty elements array). Fix the issues and re-inject.

#### 3.3 Layout Lint (automated)

Before the visual audit, run the layout lint – it catches defects faster than the eye:

```bash
agent-browser eval "window.lintLayout()"
```

Returns `{ ok, criticalCount, majorCount, minorCount, findings: { critical, major, minor } }`. Severity policy:

- **CRITICAL** (overlaps, text-over-shape) – fix before moving on
- **MAJOR** (uniform-grid, font < 14, tight spacing < 20px, no clear hero) – fix; each is a quality regression
- **MINOR** (off-grid coords, label-may-clip, no primary-flow arrow) – fix if straightforward

If `ok === false`, edit the JSON and re-inject before looking at the PNG – the lint tells you exactly which element IDs to touch.

#### 3.4 View & Audit
Use the **Read** tool on the PNG. Check against design vision (visual structure matches conceptual structure; each section uses its planned pattern; hero dominates even at 20% zoom – the "squint test"; evidence artifacts readable) and for visual defects the lint cannot see (arrow misrouting, narrative-axis violations, unbalanced composition, ugly curves, color clashes).

#### 3.5 Fix & Re-render
Edit the JSON to fix issues, then re-inject and re-screenshot (agent-browser keeps the page open):

```bash
agent-browser eval --stdin <<'JSEOF'
const data = <UPDATED_DIAGRAM_JSON>;
await window.renderDiagram(data);
JSEOF
AGENT_BROWSER_FULL=true agent-browser screenshot <OUTPUT_DIR>/<name>.png
```

Typically 2–4 iterations. After each re-render, run `window.lintLayout()` again – the counts should monotonically decrease. Use the same re-render block in Phase 4 as needed.

**Gate**: The PNG is readable, balanced, and free of obvious layout defects


### Phase 4: Review and Refine

Independent review of design quality and final QC.

#### 4.1 Design Quality Review
Invoke the `andthen:ui-ux-design` skill with `--mode review`, passing the rendered PNG, resolved style guide, and TOPIC. Evaluate, don't redesign. Check: composition and visual weight balance; hierarchy (hero → primary → secondary); color harmony and style guide compliance; hero element has 160px+ breathing room; eye path follows intended narrative; each major concept uses a distinct visual pattern.

#### 4.2 Visual Validation (Final QC)
Invoke the `andthen:visual-validation` skill in a sub-agent with the latest PNG, resolved style guide, and TOPIC description. Check: text overflow/overlap/clipping; arrow misrouting or dangling connections; all text legible (>= 16px body, >= 20px titles); colors/fills/strokes match style guide; no large voids or overcrowded regions.

#### 4.3 Remediation Loop
1. **Triage** – P1/CRITICAL and P2/MAJOR issues MUST be fixed; minor issues fix if straightforward
2. **Fix** – edit the `.excalidraw` JSON and re-render using the re-render block from Phase 3.5, then re-run `window.lintLayout()` to confirm no regressions
3. **Verify** – view the updated PNG and re-validate if needed
4. **Loop bound** – maximum 3 remediation cycles; if issues persist, escalate to the user

**Gate**: Design quality reviewed, no P1/P2 issues remaining, diagram is production-ready


### Phase 5: Output (MANDATORY – Portable Save)

Save the **portable / expanded** form to `<name>.excalidraw`, plus the PNG. The file you wrote in Phase 2.2 used the `label` shorthand and (for standalone text) likely has missing/undersized `width`/`height`. Those defects are invisible in the render template but break the file for every other consumer – most notably `app.excalidraw.com`, which shows empty shapes and clipped text.

Export the expanded form:

```bash
# getConvertedJSON expands labels to bound text elements and measures
# standalone text dimensions via Canvas measureText with the actual
# Excalidraw font. Overwrite the source .excalidraw file with this form.
agent-browser eval "window.getConvertedJSON()" > <OUTPUT_DIR>/<name>.excalidraw
```

Do NOT wrap in `JSON.stringify()` – `agent-browser eval` already JSON-encodes its return value, and `getConvertedJSON` returns a plain object.

**Verify** by opening the saved file in `app.excalidraw.com` (or visually inspect the JSON for `label:` on shapes – if any remain, the export failed and you saved the wrong form).


## OUTPUT

```
OUTPUT_DIR/
├── <name>.excalidraw    # Portable Excalidraw JSON (label shorthands expanded,
│                        # standalone text dimensions measured)
└── <name>.png           # Rendered PNG screenshot
```


## QUALITY CHECKLIST

- [ ] **Layout Contract written** (Phase 1.5) before JSON: narrative, archetype, axis, hero, size cascade, shape vocabulary, zone plan, canvas, evidence count, rhythm breakers
- [ ] **Grounded in reality** (technical): Actual specs, API names, and data formats used – no generic placeholders
- [ ] **Structure communicates**: Shape arrangement conveys meaning even with text removed; each major concept uses a different visual pattern from the catalog
- [ ] **Hero dominates**: Squint test passes – hero still identifiable at 20% opacity; size ratio hero:avg ≥ 2.0×
- [ ] **No uniform grid**: No 6+ shapes share `(type, width, height, color)` – rhythm breakers applied
- [ ] **Render validated**: `window.lintLayout()` returns zero CRITICAL and zero MAJOR findings; PNG inspected
- [ ] **Design reviewed**: Composition balanced, hierarchy clear, style guide complied with, visual flow guides narrative
- [ ] **Final QC passed**: No P1/P2 issues remaining; remediation bounded within 3 cycles
- [ ] **Portable form saved**: Final `.excalidraw` written via `getConvertedJSON()` – opens in `app.excalidraw.com` with all labels and text visible and not clipped
