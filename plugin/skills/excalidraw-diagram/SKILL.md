---
description: Create high visual quality Excalidraw diagrams that communicate with clarity and intuition. Produces educational, visually rich diagrams where structure and design do the explaining.
argument-hint: "<topic-or-source> [output-dir]"
---

# Create Excalidraw Diagram

Generate `.excalidraw` JSON diagrams where the visual structure explains the concept. The output is a source file plus a rendered PNG that has been visually reviewed.


## VARIABLES

TOPIC: $1 (required – what to visualize: inline description, file path, URL, or concept reference)
OUTPUT_DIR: $2 (defaults to `<project_root>/docs/diagrams/` if not provided)

### Variable Validation
- If `TOPIC` is empty, **STOP** and ask the user what to visualize
- Create `OUTPUT_DIR` if it does not exist
- Resolve a stable output name before writing files


## USAGE

```bash
/excalidraw-diagram "How webhook ingestion works"
/excalidraw-diagram @docs/architecture.md docs/diagrams/
/excalidraw-diagram "OpenAI realtime event flow" docs/diagrams/
```


## INSTRUCTIONS

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails**
  - **Foundational Development Guidelines and Standards**
- **Diagram generation only** – create the `.excalidraw` source and rendered PNG, not implementation code
- **Resolve style guide first** – check the project's **Project Document Index** for a `Diagram Style Guide` entry; if absent, use `references/style-guide.md`
- **Read the element format** – `references/element-format.md` defines supported element shapes, labels, bindings, and sizing rules
- **Use `label` shorthand** – prefer the `label` property on shapes for auto-centered text instead of separate text elements. The render template handles conversion to full format
- **Technical diagrams must be grounded in reality** – use real API names, data shapes, events, and method signatures, not placeholders
- **Build section-by-section** – do not attempt a non-trivial diagram in one giant JSON pass
- **Mandatory render loop** – after generating JSON, you MUST render via agent-browser, view the screenshot, and fix issues in a loop until it's right
- **agent-browser required** – the render-and-validate loop uses `agent-browser`. If not installed, tell the user to run `npm install -g agent-browser && agent-browser install`
- **Design refinement (optional)** – Phase 4 uses the `andthen:ui-ux-designer` agent _(if supported by your coding agent)_ to review design quality of the rendered diagram. The agent uses the `frontend-design` skill _(if available)_ for enhanced design evaluation. If neither is available, self-evaluate using the Phase 4 criteria
- **Visual validation (final QC)** – Phase 5 uses the `andthen:visual-validation-specialist` agent _(if supported by your coding agent)_ for independent visual validation with structured issue reporting. Falls back to self-validation if sub-agents are not supported


## GOTCHAS

- **Text overflow** – Labels too long for containers. Widen the shape or shorten the text
- **Arrow routing** – Arrows crossing through elements. Add intermediate waypoints in the `points` array
- **Uniform boxes** – Using the same shape/size for everything destroys visual hierarchy
- **Missing connections** – Position alone doesn't show relationships. Every relationship needs an arrow
- **Too small text** – Minimum `fontSize: 16` for body, `20` for titles. Below 14 is unreadable
- **JSON truncation** – Generating the entire diagram in one pass hits output token limits. Always build section-by-section for non-trivial diagrams
- **Skipping the render loop** – JSON looks right but the visual result has overlaps, clipping, or spacing issues. Always render and inspect
- **Forgetting `fillStyle: "solid"`** – Without it, `backgroundColor` won't show
- **Emoji in text** – Emoji don't render in Excalidraw's font. Use shapes instead


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
For technical diagrams, gather the real specifics that must appear visually:
- Data formats and schemas (actual JSON/protobuf/GraphQL shapes)
- Method signatures and API endpoints (real names, not placeholders)
- Event names, lifecycle hooks, status codes
- How components actually communicate (HTTP, gRPC, WebSocket, pub/sub)

**The placeholder trap**: Generic labels like `"Service A" → "Service B"` communicate nothing that a bullet list couldn't. Replace with specifics: `"OrderService.create() → Stripe /v1/charges POST → webhook delivery to /api/webhooks/stripe"`.

Prefer `andthen:documentation-lookup` or authoritative project docs when external documentation is required.

#### 1.4 Map Concepts to Visual Patterns
Use the Pattern Catalog (see Design Reference below). Each major concept gets a different pattern. Do not make every section look like the same card layout.

#### 1.5 Plan the Layout
Before writing JSON, decide:
- The hero element (largest, most whitespace)
- The reading direction: left→right, top→bottom, radial, or comparison
- Section/zone boundaries
- Which areas need overview vs detail artifacts
- Target canvas size (see Canvas Sizing in Design Reference)

**Gate**: The diagram has a clear narrative, chosen depth, chosen patterns, and a planned layout


### Phase 2: Generate JSON

#### 2.1 Resolve References
Read, in this order:
1. Project-specific diagram style guide from the Document Index, if present
2. Otherwise `references/style-guide.md`
3. `references/element-format.md`

These files are the source of truth for visual styling and JSON shape rules.

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
For each logical section:
1. Add zone backgrounds first when needed
2. Add primary shapes with `label` fields
3. Add arrows and bindings
4. Add free-floating headings and annotations
5. Add evidence artifacts for technical diagrams

Rules:
- Use descriptive IDs such as `ingest_service`, `webhook_arrow`, `phase_title`
- Namespace seeds per section (section 1: `100xxx`, section 2: `200xxx`)
- Keep sections spatially separated
- Reuse style-guide color families instead of inventing ad-hoc colors
- Use explicit arrow bindings when a connection targets a shape
- Update cross-section bindings when an arrow connects to a previous section's element

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

# 2. Wait for the Excalidraw library to load from CDN
agent-browser wait --text "Ready" --load networkidle

# 3. Inject the diagram JSON and render
#    Read the .excalidraw file content, then inject via eval
agent-browser eval --stdin <<'JSEOF'
const data = <PASTE_OR_READ_DIAGRAM_JSON_HERE>;
await window.renderDiagram(data);
JSEOF
```

The `renderDiagram` function validates the JSON before rendering. If validation fails, it returns `{ success: false, validationErrors: [...] }` with specific messages (e.g. missing `"type": "excalidraw"`, empty elements array). Fix the issues and re-inject.

```bash
# 4. Size the viewport to fit the diagram (tight crop, no excess whitespace)
#    renderDiagram returns { width, height } – use those values
agent-browser set viewport <width> <height>

# 5. Screenshot the result
agent-browser screenshot <OUTPUT_DIR>/<name>.png
```

#### 3.3 View & Audit
Use the **Read** tool on the PNG to visually inspect:

**1. Against your design vision:**
- Does the visual structure match the conceptual structure?
- Does each section use the intended pattern?
- Is the visual hierarchy correct – hero elements dominant, supporting elements smaller?
- For technical diagrams: are evidence artifacts readable and properly placed?

**2. For visual defects:**
- Text clipped by or overflowing its container
- Text or shapes overlapping
- Arrows crossing through elements
- Arrows landing on wrong elements or pointing into empty space
- Labels floating ambiguously
- Uneven spacing between elements that should be evenly spaced
- Text too small to read
- Unbalanced composition

#### 3.4 Fix & Re-render
Edit the JSON to fix issues. Common fixes:
- Widen containers when text is clipped
- Adjust `x`/`y` coordinates for spacing
- Add intermediate waypoints to arrow `points` arrays
- Reposition labels closer to what they describe
- Resize elements to rebalance visual weight

**Re-render** after each fix pass. Since agent-browser keeps the page open, re-rendering is fast – just re-inject the updated JSON and re-screenshot:

```bash
agent-browser eval --stdin <<'JSEOF'
const data = <UPDATED_DIAGRAM_JSON>;
await window.renderDiagram(data);
JSEOF
agent-browser set viewport <new-width> <new-height>
agent-browser screenshot <OUTPUT_DIR>/<name>.png
```

Typically 2–4 iterations.

#### 3.5 Export Portable Version (Optional)
If the user needs a standard `.excalidraw` file without `label` shortcuts (e.g., to open directly in excalidraw.com):

```bash
agent-browser eval "window.getConvertedJSON()"
```

Save the result as a standard `.excalidraw` file. Note: `agent-browser eval` already JSON-encodes its return value, so do NOT wrap in `JSON.stringify()` (that would double-encode).

**Gate**: The PNG is readable, balanced, and free of obvious layout defects


### Phase 4: Design Refinement

Review the rendered PNG for design quality – composition, hierarchy, color harmony, whitespace balance, and visual flow. This phase uses an independent design eye to catch issues the creator may miss.

#### 4.1 Launch Design Review

Launch the `andthen:ui-ux-designer` agent _(if supported by your coding agent; otherwise evaluate manually using the criteria below)_ with:
- The rendered PNG screenshot from Phase 3
- The resolved style guide (project or default)
- The original TOPIC description
- **Review mode** – evaluate, don't redesign

The agent uses the `frontend-design` skill _(if available)_ and evaluates:

| Aspect | What to Check |
|--------|---------------|
| **Composition** | Visual weight distribution, balance, focal point clarity |
| **Hierarchy** | Size/color/position correctly guide attention to hero → primary → secondary |
| **Color harmony** | Palette consistency, contrast between adjacent elements, style guide compliance |
| **Whitespace** | Hero element has 200px+ breathing room, no overcrowded regions, no large voids |
| **Visual flow** | Eye path follows intended narrative (left→right, top→bottom, or radial) |
| **Pattern variety** | Each major concept uses a distinct visual pattern (no uniform cards/grids) |

#### 4.2 Apply Improvements

If the design review identifies issues:
1. **Triage** – categorize as CRITICAL (breaks visual argument), MAJOR (weakens clarity), or MINOR (polish)
2. **Fix** – edit the `.excalidraw` JSON to address CRITICAL and MAJOR issues:
   - Rebalance element sizes/positions for better composition
   - Adjust spacing for improved whitespace distribution
   - Reposition elements to strengthen visual flow
   - Swap patterns where the current choice doesn't mirror the concept
3. **Re-render** – inject updated JSON and re-screenshot:

```bash
agent-browser eval --stdin <<'JSEOF'
const data = <UPDATED_DIAGRAM_JSON>;
await window.renderDiagram(data);
JSEOF
agent-browser set viewport <new-width> <new-height>
agent-browser screenshot <OUTPUT_DIR>/<name>.png
```

4. **Verify** – view the updated PNG and confirm improvements land correctly

_(If the `frontend-design` skill is not available and sub-agents are not supported, perform a self-evaluation against the criteria table above and apply any obvious improvements.)_

**Gate**: Design quality reviewed – composition balanced, hierarchy clear, visual flow guides the narrative


### Phase 5: Visual Validation (Final QC)

Independent visual validation by a specialist agent. This separates creation from judgment – a different "pair of eyes" performs the final quality gate.

#### 5.1 Launch Validation

Launch the `andthen:visual-validation-specialist` sub-agent _(if supported by your coding agent)_ with:
- The rendered PNG screenshot (latest from Phase 4, or Phase 3 if Phase 4 was skipped)
- The resolved style guide as the design reference
- The TOPIC description as the requirements reference

The specialist validates:

| Check | What It Covers |
|-------|----------------|
| **Layout defects** | Text overflow, element overlap, arrow misrouting, clipped content |
| **Style guide compliance** | Colors, fill styles, stroke widths, font sizes match the resolved style guide |
| **Readability** | All text legible at export size (>= 16px body, >= 20px titles), sufficient contrast |
| **Structural integrity** | Arrows connect to intended elements, no dangling connections, all IDs resolve |
| **Composition** | No large voids, no overcrowded regions, balanced visual weight |

The agent produces a structured report with:
- **Overall Status**: PASS / FAIL / PARTIAL
- **Issues** categorized as P1 Critical, P2 Major, P3 Minor
- **Specific fixes** for each issue (element IDs, coordinate adjustments, property changes)

#### 5.2 Remediation Loop

Structured fix-and-revalidate cycle with bounded iterations:

1. **Triage** – P1 Critical and P2 Major issues MUST be fixed; P3 Minor issues SHOULD be fixed if straightforward
2. **Fix** – edit the `.excalidraw` JSON to address issues using the specific fixes from the validation report
3. **Re-render** – inject updated JSON and re-screenshot:

```bash
agent-browser eval --stdin <<'JSEOF'
const data = <UPDATED_DIAGRAM_JSON>;
await window.renderDiagram(data);
JSEOF
agent-browser set viewport <new-width> <new-height>
agent-browser screenshot <OUTPUT_DIR>/<name>.png
```

4. **Re-validate** – send the updated PNG back to the `andthen:visual-validation-specialist` for re-assessment
5. **Loop** – repeat steps 1–4 until all P1/P2 issues are resolved and validation status is PASS

**Loop bound**: Maximum **3 remediation cycles**. If issues persist after 3 cycles, escalate to the user with a summary of remaining issues and what was attempted.

_(If sub-agents are not supported by your coding agent, perform a self-validation against the checks table above. Apply fixes for any issues found, re-render, and re-inspect. Limit to 2 additional fix passes.)_

**Gate**: Visual validation PASS – no P1/P2 issues remaining, diagram is production-ready


### Phase 6: Output

Save final artifacts to `OUTPUT_DIR`:
- `<name>.excalidraw` – the diagram source (JSON)
- `<name>.png` – rendered screenshot

If the user needs a portable Excalidraw export without `label` shortcuts, obtain the converted JSON from the render template and save that version as well.


## OUTPUT

```
OUTPUT_DIR/
├── <name>.excalidraw    # Excalidraw JSON source
└── <name>.png           # Rendered PNG screenshot
```


## QUALITY CHECKLIST

### Research & Evidence (Technical Diagrams)
- [ ] **Grounded in reality**: Actual specs, data formats, API names researched and used
- [ ] **Evidence artifacts embedded**: Code snippets, JSON shapes, real inputs, or method signatures visible in the diagram
- [ ] **Multi-zoom**: Overview + section zones + detail artifacts all coexist on the canvas
- [ ] **Specificity test passes**: Real content shown – no generic placeholders like "Service A"

### Structural Design
- [ ] **Structure test passes**: Shape arrangement communicates meaning even with text removed
- [ ] **Pattern variety**: Each major concept uses a different visual pattern from the pattern catalog
- [ ] **Shape vocabulary consistent**: Shape types used consistently (rectangles = actions, ellipses = states, diamonds = decisions)
- [ ] **Scale encodes hierarchy**: Hero, primary, secondary sizes are visually distinct

### Text Placement
- [ ] **Box-budget rule**: Fewer than 30% of text elements inside containers
- [ ] **Lines as structure**: Tree/timeline patterns use lines + free-floating text, not boxes
- [ ] **Typography hierarchy**: Font size and color alone create heading → body → detail levels

### Technical Correctness
- [ ] **Label shorthand**: Shapes with text use `label` property
- [ ] **Style guide followed**: All colors, fills, strokes, typography from resolved style guide (project or default)
- [ ] **Font sizes**: >= 16 for body, >= 20 for titles
- [ ] **Opacity**: `opacity: 100` for all elements
- [ ] **Descriptive IDs**: Element IDs describe what they are

### Render Validation (Phase 3)
- [ ] **Rendered to PNG**: Rendered and inspected via agent-browser
- [ ] **No text overflow**: All text fits within containers
- [ ] **No overlapping elements**: Shapes and text don't overlap
- [ ] **Even spacing**: Consistent spacing between similar elements
- [ ] **Arrows land correctly**: Arrows connect to intended elements
- [ ] **Readable at export size**: Text legible in rendered PNG
- [ ] **Balanced composition**: No large voids or overcrowded regions

### Design Refinement (Phase 4)
- [ ] **Design review performed**: Composition, hierarchy, color harmony, whitespace, and flow evaluated
- [ ] **Style guide compliance**: Colors, fills, and strokes match the resolved style guide
- [ ] **Pattern variety confirmed**: Each major concept uses a distinct visual pattern
- [ ] **Improvements applied**: CRITICAL and MAJOR design issues addressed and re-rendered
- [ ] **Graceful degradation**: Phase completed (via sub-agent or self-evaluation) regardless of `frontend-design` availability

### Final Visual Validation (Phase 5)
- [ ] **Independent validation**: `visual-validation-specialist` agent reviewed the rendered PNG (or self-validated if sub-agents unavailable)
- [ ] **No P1/P2 issues**: All Critical and Major issues resolved
- [ ] **Style guide compliance verified**: Font sizes, colors, fill styles, stroke widths match spec
- [ ] **Readability confirmed**: All text legible at export size
- [ ] **Remediation bounded**: Fix loop completed within 3 cycles (or escalated to user)
- [ ] **Final status PASS**: Validation report shows PASS status


## DESIGN REFERENCE

### Design Principles

**Structure is the argument.** A diagram succeeds when its visual topology – the arrangement of shapes, the direction of arrows, the scale of elements – communicates meaning independently of labels. Text annotates; structure persuades.

Two litmus tests for every diagram:

1. **Structure test**: Cover all text. Does the shape arrangement alone convey the core relationship? A fan-out shape radiating arrows communicates "one source, many targets" even without labels. If the structure is just a grid of equal boxes, the diagram is decoration, not communication.

2. **Specificity test**: Does the diagram contain concrete, verifiable details – real API names, actual data formats, genuine code snippets – or just abstract placeholders? A diagram that says `handleWebhook(event: StripeEvent)` teaches; one that says `"Process" → "Handler"` merely labels.

#### What This Means in Practice

| Weak | Strong | Why |
|------|--------|-----|
| Equal-sized boxes in a row | Sizes reflect importance (hero → primary → small) | Scale encodes hierarchy |
| Every label in a rectangle | Most text free-floating; boxes reserved for connectable entities | Typography alone creates hierarchy |
| One shape type throughout | Different shapes per concept type (ellipse for state, diamond for decision, rectangle for action) | Shape vocabulary mirrors concept vocabulary |
| Arrows implied by proximity | Explicit arrows with typed endpoints (arrow, dot, bar) | Relationships must be visible, not assumed |


### Evidence Artifacts

Evidence artifacts embed real, verifiable details directly into the diagram. They transform a diagram from "here's how it works in theory" to "here's what you'll actually see."

**Rendering**: All artifacts use the dark "editor pane" container from the style guide – dark background, monospace font, syntax-colored text. See the style guide's Evidence Artifacts section for exact colors.

| Artifact | Example | Rendering |
|----------|---------|-----------|
| **Code snippet** | `async function handleEvent(e: ServerEvent)` | Dark rectangle + syntax-colored text |
| **Data shape** | `{ "type": "state_delta", "delta": [...] }` | Dark rectangle + JSON-colored text |
| **Sequence** | `INIT → CONNECTED → STREAMING → DONE` | Timeline pattern (line + dots + labels) |
| **Real input** | An actual HTTP request, user message, or CLI command | Dark rectangle + terminal-colored text |
| **UI fragment** | What the user actually sees on screen | Nested rectangles mimicking the real layout |
| **Method signature** | `OrderService.create(items: LineItem[]) → Order` | Inline within shape labels, monospace |


### Multi-Zoom Rule

A comprehensive technical diagram should be readable at three distances – like a map that works at country, city, and street level:

| Zoom Level | What's Visible | Excalidraw Implementation |
|-----------|----------------|--------------------------|
| **Overview** | The full pipeline – major stages and their flow direction | Large shapes, bold arrows, hero elements |
| **Sections** | Logical groupings within stages – what belongs together | Zone backgrounds (style guide Section 6), section headings |
| **Detail** | Evidence artifacts – the actual code, data, and specifics | Dark "editor pane" containers with monospace text inside zones |

All three levels coexist on the same canvas. The viewer's eye naturally scans overview → section → detail.


### Text Placement Strategy

The default is **free-floating text** – no surrounding shape. Containers (rectangles, ellipses, diamonds) are reserved for elements that need to be *connectable* or where shape meaning matters.

**When to add a container**:
- The element is an arrow endpoint (arrows need something to bind to)
- The shape carries semantic meaning (diamond = decision, ellipse = state)
- The element is the visual anchor of a section

**When to keep text free-floating**:
- Section titles and headings (font size creates hierarchy)
- Annotations and descriptions (proximity to the relevant shape is enough)
- Labels that describe nearby elements (the position IS the association)

**The box-budget rule**: Aim for fewer than 30% of text elements inside containers. If most of your text is boxed, you're over-containing – the diagram will look like a form, not a visual argument. Use font size (28px title → 16px body) and color (zone stroke color for headings → gray for annotations) to create hierarchy without borders.


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
Element size signals significance. Use a consistent size scale:

| Role | Approximate Size | Purpose |
|------|-----------------|---------|
| Hero element | 300×150 | The diagram's focal point – largest, most whitespace around it (200px+) |
| Primary | 180×90 | Main components |
| Secondary | 120×60 | Supporting elements |
| Marker | 60×40 or smaller | Dots, labels, minor details |

#### Eye Flow
Every diagram has an intended reading order. Guide it with:
- **Direction**: Left→right or top→bottom for sequences; radial for hub-and-spoke
- **Arrows**: Every relationship must have an explicit arrow. Proximity alone doesn't communicate connection – if A relates to B, draw the arrow
- **Whitespace**: The hero element gets the most breathing room; dense clusters signal "these are closely related"

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

The style guide (`references/style-guide.md`) controls all visual settings and ships with three **aesthetic presets** (Section 11):

| Preset | When to Use |
|--------|-------------|
| **Hand-drawn Blueprint** (default) | Exploratory, educational, whiteboard-style |
| **Warm Industrial** | Technical with warmth and character |
| **Clean Technical** | Presentations, documentation, formal audiences |

Key defaults (Hand-drawn Blueprint preset):

- `roughness: 1` – Slightly hand-drawn, the signature look (use `0` for evidence artifacts and zones)
- `fillStyle: "solid"` – Clean, readable; use `"hachure"` sparingly for accumulated state (caches, databases)
- `strokeWidth: 1` thin, `2` standard, `4` bold emphasis
- `opacity: 100` for all foreground elements – use color/size/stroke for hierarchy, not transparency

The style guide also includes a **semantic color overlay** (Section 1) that maps concept types (AI/LLM, Data, Security, etc.) to color families, so the same concept looks consistent across diagrams.
