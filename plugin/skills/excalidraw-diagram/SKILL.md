---
description: Create high-visual-quality Excalidraw diagrams where structure and design do the explaining. Trigger on 'draw this architecture', 'workflow diagram', 'create an Excalidraw diagram'.
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
- This skill is phase-gated: resolve references first (Phase 2.1), ground technical diagrams in reality (Phase 1.3), commit a Layout Contract before JSON (Phase 1.5, a **mandatory gate**), run the render-and-validate loop (Phase 3), then design-refine and QC (Phase 4). Label shorthand vs portable form is canonical in GOTCHAS + Phase 5.
- The render loop uses `agent-browser` (`npm install -g agent-browser && agent-browser install` if not installed).


## GOTCHAS

- **Uniform grid = AI-aesthetic failure** – 6+ shapes with identical `(type, width, height, backgroundColor)` is the defining generic look. Apply the Anti-Uniformity Rule (rhythm breakers) from the style guide.
- **Implied connections** – Phase headers sitting above their children, or two boxes near each other, communicate nothing. Every relationship needs an **explicit arrow** or a line+text tree structure.
- **Label shorthand vs portable form** – the `label` form is render-only; export via `window.getConvertedJSON()` before saving (Phase 5 owns the contract), or the file opens as empty boxes in `app.excalidraw.com`.
- **Arrow routing** – arrows crossing through elements. Add intermediate waypoints in the `points` array.
- **JSON truncation** – generating the entire diagram in one pass hits output token limits. Build section-by-section for non-trivial diagrams.
- **Skipping the render loop** – JSON cannot prove the visual result; see Phase 3 (MANDATORY).
- **Pre-flight pitfalls** – ellipse/diamond sizing (`redrawTextBoundingBox` floors), fontSize floors, `fillStyle: "solid"`, emoji, off-grid snap-to-20 are covered in `element-format.md` and `style-guide.md` – read them in Phase 2.1.
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
- **Technical / Architectural** – real systems, APIs, protocols, or implementation flows; evidence artifacts are required

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
7. **Zone plan** – 2–4 zones, each with a color family per `style-guide.md` § Semantic Color Overlay and a `x/y/width/height` on the 20px grid.
8. **Canvas size** – S/M/L/XL/XXL per `style-guide.md` § Canvas Sizing. Prefer 4:3.
9. **Evidence artifacts** – count (technical diagrams: at least 1; ratio ~1 per 4–6 abstract nodes).
10. **Rhythm breakers** – how you avoid a uniform grid for any category with ≥ 6 items (anchor upsize / alternating row heights / evidence insertion).

**Gate**: The contract is written in plain text – all 10 items committed.


### Phase 2: Generate JSON

#### 2.1 Resolve References
Read, in this order:
1. Project-specific diagram style guide from the Document Index, if present
2. Otherwise `references/style-guide.md` – colors, size cascade, Anti-Uniformity Rule, shape vocabulary, design principles
3. `references/element-format.md` – JSON shape, label auto-sizing math, font metrics
4. `references/composition-playbook.md` – archetype recipes and the Pattern Catalog

These files are the source of truth for visual styling, JSON shape rules, and design quality.

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
#    The template sets window.__moduleReady = true once ready. Poll it directly –
#    see the ES-module readiness race GOTCHA (`wait --fn` ignores timeout overrides):
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
Edit the JSON to fix issues, then re-inject and re-screenshot using the same inject+screenshot block as Phase 3.2 (agent-browser keeps the page open).

Typically 2–4 iterations. After each re-render, run `window.lintLayout()` again – the counts should monotonically decrease.

**Gate**: The PNG is readable, balanced, and free of obvious layout defects


### Phase 4: Review and Refine

Independent review of design quality and final QC.

#### 4.1 Design Quality Review
Invoke the `andthen:ui-ux-design` skill with `--mode review`, passing the rendered PNG, resolved style guide, and TOPIC. Evaluate, don't redesign. Check: composition and visual weight balance; eye path follows intended narrative; each major concept uses a distinct visual pattern.

#### 4.2 Visual Validation (Final QC)
Invoke the `andthen:visual-validation` skill in a sub-agent with the latest PNG, resolved style guide, and TOPIC description. Check: text overflow/overlap/clipping; arrow misrouting or dangling connections; no large voids or overcrowded regions.

#### 4.3 Remediation Loop
1. **Triage** – P1/CRITICAL and P2/MAJOR issues MUST be fixed; minor issues fix if straightforward
2. **Fix** – edit the `.excalidraw` JSON and re-render using the re-render block from Phase 3.5, then re-run `window.lintLayout()` to confirm no regressions
3. **Verify** – view the updated PNG and re-validate if needed
4. **Loop bound** – maximum 3 remediation cycles; if issues persist, escalate to the user

**Gate**: Design quality reviewed, no P1/P2 issues remaining, diagram is production-ready


### Phase 5: Output (MANDATORY – Portable Save)

Save the **portable / expanded** form to `<name>.excalidraw`, plus the PNG – the file written in Phase 2.2 uses the render-only `label` shorthand (see GOTCHAS).

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
├── <name>.excalidraw
└── <name>.png
```


## QUALITY CHECKLIST

- [ ] **Layout Contract written** (Phase 1.5) before JSON
- [ ] **Grounded in reality** (technical, Phase 1.3): real specs, API names, data formats – no placeholders
- [ ] **Structure communicates** (Phase 2.3): arrangement conveys meaning text-removed; each concept a distinct pattern
- [ ] **Hero dominates** (Phase 3.4): squint test passes
- [ ] **No uniform grid** (Phase 1.5 rhythm breakers): see GOTCHAS + `style-guide.md` Anti-Uniformity Rule
- [ ] **Render validated** (Phase 3.3): `window.lintLayout()` returns zero CRITICAL and zero MAJOR; PNG inspected
- [ ] **Design reviewed** (Phase 4.1): composition balanced, flow guides narrative
- [ ] **Final QC passed** (Phase 4.3): no P1/P2 issues; remediation bounded within 3 cycles
- [ ] **Portable form saved** (Phase 5): final `.excalidraw` via `getConvertedJSON()` – opens clean in `app.excalidraw.com`
