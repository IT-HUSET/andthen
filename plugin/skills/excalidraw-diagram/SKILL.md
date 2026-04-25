---
description: Create high visual quality Excalidraw diagrams that communicate with clarity and intuition. Produces educational, visually rich diagrams where structure and design do the explaining. Trigger on 'draw this architecture', 'make a workflow diagram', 'create an Excalidraw diagram'.
argument-hint: "<topic-or-source> [output-dir]"
---

# Create Excalidraw Diagram

Generate `.excalidraw` JSON diagrams where the visual structure explains the concept. The output is a source file plus a rendered PNG that has been visually reviewed.


## VARIABLES

TOPIC: $1 (required – what to visualize: inline description, file path, URL, or concept reference)
OUTPUT_DIR: $2 (defaults to `<project_root>/docs/diagrams/` if not provided)

### Variable Validation
- If `TOPIC` is empty, **STOP** with a missing-input error that states the visualization topic is required
- Create `OUTPUT_DIR` if it does not exist
- Resolve a stable output name before writing files


## INSTRUCTIONS

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails**
  - **Foundational Development Guidelines and Standards**
- **Diagram generation only** – create the `.excalidraw` source and rendered PNG, not implementation code
- **Resolve references first** – read the style guide, element format, and composition playbook before writing a single shape:
  1. Project's `Diagram Style Guide` (from the **Project Document Index**) if present, else `references/style-guide.md`
  2. `references/element-format.md` – JSON shape, label auto-sizing math, font metrics
  3. `references/composition-playbook.md` – archetype recipes (pipeline / architecture / taxonomy / lifecycle / comparison)
- **Commit to a Layout Contract before JSON** – Phase 1.5 below. Skipping this is the #1 cause of flat, AI-generic results.
- **Use `label` shorthand** – prefer the `label` property on shapes for auto-centered text instead of separate text elements. The render template handles conversion. **But always specify explicit `width` and `height`** – under-sizing lets Excalidraw silently grow the container and collapses your size cascade back toward uniformity.
- **Always save the portable (expanded) form** – the `label` shorthand is a render-time convenience, not an on-disk format. The final `.excalidraw` file must be written via `window.getConvertedJSON()` (Phase 5). Saving the shorthand form directly produces a file that opens as empty shapes in `app.excalidraw.com`.
- **Technical diagrams must be grounded in reality** – use real API names, data shapes, events, and method signatures, not placeholders
- **Build section-by-section** – do not attempt a non-trivial diagram in one giant JSON pass
- **Mandatory render loop with lint** – after generating JSON, you MUST render via agent-browser, run `window.lintLayout()`, view the screenshot, and iterate until critical and major findings are resolved
- **agent-browser required** – the render-and-validate loop uses `agent-browser`. If not installed, tell the user to run `npm install -g agent-browser && agent-browser install`
- **Design refinement and final QC** – Phase 4 combines design review (via the `andthen:ui-ux-design` skill in `review` mode) and visual validation (via the `andthen:visual-validation-specialist` agent if available). Fall back to self-evaluation using the criteria in Phase 4 if sub-agents are not supported


## GOTCHAS

- **Uniform grid = AI-aesthetic failure** – 6+ shapes with identical `(type, width, height, backgroundColor)` is the defining generic look. Apply the Anti-Uniformity Rule from the style guide: anchor shape every 3–4 items, alternating row heights, or an evidence artifact insertion.
- **Implied connections** – Phase headers sitting above their children, or two boxes near each other, communicate nothing. Every relationship needs an **explicit arrow** or a line+text tree structure.
- **Ellipses/diamonds are hungry** – for the same label, an ellipse needs ~1.4× a rectangle and a diamond needs ~2×. Hard-coding identical widths produces clipping. See `element-format.md` § Label Auto-Sizing.
- **Label shorthand silently resizes** – if your specified `width` is smaller than the label needs, `redrawTextBoundingBox` expands it at render time. Always over-size (the cascade numbers are floors, not ceilings).
- **Shorthand vs portable form** – the `label` shorthand only survives the render template's in-memory conversion. Writing a file with `label:` fields on shapes produces empty boxes in `app.excalidraw.com`. Always export via `window.getConvertedJSON()` before saving (Phase 5).
- **Standalone text width/height** – text elements without `width`/`height` (or with undersized ones) open clipped in Excalidraw. The render template's `refreshTextDimensions` measures them via Canvas `measureText` with the actual Excalidraw font and patches dimensions during `getConvertedJSON`. You don't need to set them manually, but if you bypass the portable export, you'll see truncated titles/subtitles that only fix themselves when the user clicks the element.
- **Arrow routing** – arrows crossing through elements. Add intermediate waypoints in the `points` array.
- **Too small text** – minimum `fontSize: 16` for body, `20` for titles. Below 14 is unreadable. Scale up at XL/XXL canvas sizes.
- **JSON truncation** – generating the entire diagram in one pass hits output token limits. Build section-by-section for non-trivial diagrams.
- **Skipping the render loop** – JSON looks right but the visual result has overlaps, clipping, or spacing issues. Always render, run `lintLayout()`, and inspect the PNG.
- **Forgetting `fillStyle: "solid"`** – without it, `backgroundColor` won't show.
- **Emoji in text** – emoji don't render in Excalidraw's font. Use shapes instead.
- **Off-grid coordinates** – snap all `x`, `y`, `width`, `height` to multiples of 20. Arbitrary values (x: 143, 287) produce an "almost aligned" look that reads as sloppy.
- **ES-module readiness race** – on cold load, the `esm.sh` module graph for `@excalidraw/excalidraw` takes 30s+, which exceeds the 25s default `agent-browser wait` timeout. `AGENT_BROWSER_DEFAULT_TIMEOUT` and `--timeout` are **not honored by `wait --fn`** (verified empirically). Both `wait --text` and `wait --fn` do exit non-zero on timeout, so they fail loudly — but that's still a failure you have to work around. The working pattern is the bash polling loop in Phase 3.2. Also: `sleep 2` only appears to work because the module is cached from a prior session — do not assume it.


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
Gather real data formats/schemas, method signatures, API endpoints, event names, and communication protocols. Generic labels (`"Service A" → "Service B"`) communicate nothing; use specifics (`"OrderService.create() → Stripe /v1/charges POST → webhook /api/webhooks/stripe"`). Use the `andthen:documentation-lookup` agent or project docs for external APIs.

#### 1.4 Map Concepts to Visual Patterns
Use the Pattern Catalog (see Design Reference below). Each major concept gets a different pattern. Do not make every section look like the same card layout.

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
2. Otherwise `references/style-guide.md` (colors, size cascade, signal badges, density gradient, anti-uniformity rule)
3. `references/element-format.md` (JSON shape, label auto-sizing math, font metrics)
4. `references/composition-playbook.md` (archetype recipes with concrete XY positions)

These files are the source of truth for visual styling and JSON shape rules. Your Layout Contract from Phase 1.5 keyed off them; now you are executing it.

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

You cannot judge the diagram from JSON alone. Render it and inspect the image.

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
#    at the diagram's native dimensions — no viewport sizing required.
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

Independent review of design quality and final QC. This phase separates creation from judgment.

#### 4.1 Design Quality Review
Invoke the `andthen:ui-ux-design` skill with `--mode review`, passing the rendered PNG, resolved style guide, and TOPIC. Evaluate, don't redesign. Check: composition and visual weight balance; hierarchy (hero → primary → secondary); color harmony and style guide compliance; hero element has 160px+ breathing room; eye path follows intended narrative; each major concept uses a distinct visual pattern.

#### 4.2 Visual Validation (Final QC)
Launch the `andthen:visual-validation-specialist` agent with the latest PNG, resolved style guide, and TOPIC description. Check: text overflow/overlap/clipping; arrow misrouting or dangling connections; all text legible (>= 16px body, >= 20px titles); colors/fills/strokes match style guide; no large voids or overcrowded regions.

#### 4.3 Remediation Loop
1. **Triage** – P1/CRITICAL and P2/MAJOR issues MUST be fixed; minor issues fix if straightforward
2. **Fix** – edit the `.excalidraw` JSON and re-render using the re-render block from Phase 3.5, then re-run `window.lintLayout()` to confirm no regressions
3. **Verify** – view the updated PNG and re-validate if needed
4. **Loop bound** – maximum 3 remediation cycles; if issues persist, escalate to the user

**Gate**: Design quality reviewed, no P1/P2 issues remaining, diagram is production-ready


### Phase 5: Output (MANDATORY – Portable Save)

Save the **portable / expanded** form to `<name>.excalidraw`, plus the PNG. The file you wrote in Phase 2.2 used the `label` shorthand and (for standalone text) likely has missing/undersized `width`/`height`. Those defects are invisible in the render template but break the file for every other consumer — most notably `app.excalidraw.com`, which shows empty shapes and clipped text.

Export the expanded form:

```bash
# getConvertedJSON expands labels to bound text elements and measures
# standalone text dimensions via Canvas measureText with the actual
# Excalidraw font. Overwrite the source .excalidraw file with this form.
agent-browser eval "window.getConvertedJSON()" > <OUTPUT_DIR>/<name>.excalidraw
```

Do NOT wrap in `JSON.stringify()` – `agent-browser eval` already JSON-encodes its return value, and `getConvertedJSON` returns a plain object.

**Verify** by opening the saved file in `app.excalidraw.com` (or visually inspect the JSON for `label:` on shapes — if any remain, the export failed and you saved the wrong form).


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


## DESIGN REFERENCE

### Design Principles

**Structure is the argument.** Visual topology communicates meaning independently of labels. Two litmus tests:
1. **Structure test** – Cover all text. Does shape arrangement alone convey the core relationship? A fan-out radiating arrows says "one source, many targets" without labels. A grid of equal boxes is decoration.
2. **Specificity test** – Real API names, actual data formats, genuine code snippets? `handleWebhook(event: StripeEvent)` teaches; `"Process" → "Handler"` merely labels.

| Weak | Strong | Why |
|------|--------|-----|
| Equal-sized boxes | Sizes reflect importance (hero → primary → small) | Scale encodes hierarchy |
| Every label in a rectangle | Most text free-floating; boxes for connectable entities | Typography creates hierarchy |
| One shape type throughout | Different shapes per concept (ellipse = state, diamond = decision, rectangle = action) | Shape vocabulary mirrors concept vocabulary |
| Arrows implied by proximity | Explicit arrows with typed endpoints | Relationships must be visible, not assumed |


### Evidence Artifacts

Embed real, verifiable details directly into the diagram – not "Service A → Service B" but actual function signatures, data shapes, event names, and API endpoints. All artifacts use the dark "editor pane" container (style guide Evidence Artifacts section): dark background, monospace font, syntax-colored text. Types: code snippets, JSON data shapes, sequences (timeline pattern), real HTTP inputs, UI fragments (nested rectangles), method signatures (inline monospace in shape labels).


### Multi-Zoom Rule

A comprehensive technical diagram is readable at three distances: **Overview** (large shapes + bold arrows show the full pipeline), **Sections** (zone backgrounds + section headings group related elements), **Detail** (dark "editor pane" containers with monospace text show evidence artifacts). All three coexist on one canvas; the eye scans overview → section → detail.


### Text Placement Strategy

Default to **free-floating text**. Add a container only when the element needs to be an arrow endpoint, carries shape-semantic meaning (diamond = decision, ellipse = state), or is a section anchor. Keep section titles, annotations, and nearby descriptive labels free-floating – font size and position create hierarchy without borders.

**Box-budget rule**: Fewer than 30% of text elements inside containers. Over-containing makes a diagram look like a form. Use font size (28px title → 16px body) and color (zone stroke for headings → gray for annotations) to create hierarchy.


### Pattern Catalog

Map each concept to the pattern that mirrors its behavior. **Each major concept must use a different visual pattern.** No uniform cards or grids.

#### Fan-out
One source spawns multiple outputs. Use for: broadcasting, triggers, root causes, one-to-many.
```
            ○ target
           ↗
    □ ──→ ○ target
    source ↘
            ○ target
```

#### Convergence
Multiple inputs merge into a single output. Use for: aggregation, funnels, synthesis, many-to-one.
```
    ○ input ↘
    ○ input ──→ □ result
    ○ input ↗
```

#### Tree
Parent-child branching hierarchy. Use for: file systems, org charts, taxonomies, nested structures. **Use lines + free-floating text, not boxes.**
```
    Root Label
    ├── Branch A
    │   ├── Leaf A1
    │   └── Leaf A2
    └── Branch B
        └── Leaf B1
```

#### Timeline
Ordered sequence of steps or events. Use for: protocols, lifecycles, step-by-step processes. **Line + small dots + free-floating labels.**
```
    ●──────●──────●──────●──────●
    Step 1  Step 2  Step 3  Step 4  Step 5
    detail  detail  detail  detail  detail
```

#### Spiral / Cycle
Continuous loop that repeats. Use for: feedback loops, iterative processes, retry patterns, evolution.
```
    □ ────→ □
    ↑         ↓
    □ ←──── □
```

#### Cloud
Overlapping ellipses forming a fuzzy region. Use for: abstract state, context, memory, ambient processes.
```
       ╭───╮
    ╭──┤   ├──╮
    │  ╰─┬─╯  │
    ╰────┴────╯
      abstract
```

#### Assembly Line
Input transforms through a process into output. Use for: ETL, compilation, data pipelines, before/after.
```
    ○○○  ──→  [ PROCESS ]  ──→  □□□
    raw         transform        result
```

#### Side-by-Side
Parallel structures for comparison. Use for: before/after, trade-offs, options, old vs new.
```
    ┌─── Option A ───┐    ┌─── Option B ───┐
    │  □ → □ → □     │    │  □ → □         │
    │  fast, complex  │    │  slow, simple   │
    └────────────────┘    └────────────────┘
```

#### Gap / Break
Visual whitespace or barrier between phases. Use for: phase transitions, context switches, boundaries.
```
    [ Phase 1 ]          [ Phase 2 ]
    □ → □ → □    ║║║    □ → □ → □
                 gap
```


### Shape Vocabulary

Each Excalidraw shape type carries a visual connotation. Use shape consistently so viewers learn the vocabulary as they read the diagram.

| Shape | Excalidraw Type | Conveys | Examples |
|-------|----------------|---------|----------|
| **No shape** | free-floating text | Annotation, label, heading | Section titles, descriptions, detail notes |
| **Rounded rectangle** | `rectangle` + `roundness: {"type": 3}` | Process, action, component | Services, functions, pipeline stages |
| **Ellipse** | `ellipse` | State, origin, or destination | Start/end points, inputs/outputs, triggers |
| **Diamond** | `diamond` | Decision or condition | Branching logic, feature flags, conditionals |
| **Small dot** | `ellipse` (10-20px) | Marker or anchor point | Timeline steps, bullet points, connection nodes |
| **Overlapping ellipses** | multiple `ellipse` | Abstract / fuzzy concept | Context, memory, ambient state |
| **Lines + text** | `line` + free text | Hierarchical structure | Tree branches, org charts, taxonomies |


### Spatial Hierarchy

#### Scale Encodes Importance
Element size signals significance. See `style-guide.md` § Size Cascade for the authoritative numbers: Hero `320×160` (used once, 160px+ breathing room), Primary `180×90`, Secondary `120×60`, Marker `12×12` to `80×28`. Ratio hero : primary : secondary ≈ 3 : 1.8 : 1.

#### Eye Flow
Guide reading order with direction (left→right or top→bottom for sequences; radial for hub-and-spoke), explicit arrows (every relationship needs an arrow – proximity alone doesn't communicate connection), and whitespace (hero element gets the most breathing room; dense clusters signal "closely related").

#### Canvas Sizing
Choose a target bounding box based on diagram complexity. Font readability degrades at larger sizes – adjust `fontSize` minimums accordingly.

| Size | Bounding Box | Best For | Font Minimum |
|------|-------------|----------|-------------|
| **S** | ~400×300 | Close-up on 2–3 elements, detail insets | 16px (standard) |
| **M** | ~600×450 | A single section or small concept | 16px (standard) |
| **L** | ~800×600 | Standard full diagram (most common) | 16px (standard) |
| **XL** | ~1200×900 | Large overviews with many sections | 18px body, 24px titles |
| **XXL** | ~1600×1200 | Complex panoramas, multi-zoom technical diagrams | 20px body, 28px titles |

**Guidelines**:
- **Prefer 4:3 aspect ratio** – renders cleanly across viewports and avoids distortion when scaled
- **Leave padding** – 40–80px margin around the outermost elements so nothing feels cramped against the edge
- **Scale fonts with canvas** – at XL/XXL sizes, standard 16px body text becomes hard to read. Increase font sizes proportionally
- **Don't over-size** – use the smallest canvas that fits your content comfortably. Empty space is wasted space (whitespace around the *hero* is intentional; whitespace around the *canvas edge* is not)


### Aesthetic Direction

The style guide (`references/style-guide.md`) ships with three **aesthetic presets** (Section 13): **Hand-drawn Blueprint** (default – exploratory, whiteboard feel), **Warm Industrial** (technical with warmth), **Clean Technical** (formal presentations). Key defaults for Hand-drawn Blueprint: `roughness: 1` (use `0` for evidence artifacts and zones), `fillStyle: "solid"` (use `"hachure"` sparingly for caches/databases), `strokeWidth: 2` standard, `opacity: 100` for all foreground elements. Section 1 of the style guide maps concept types (AI/LLM, Data, Security, etc.) to color families for cross-diagram consistency.
