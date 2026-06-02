# Diagram Style Guide (Default)

**Default visual style for generated Excalidraw diagrams.** This file is the fallback when a project does not configure its own style guide.

**To customize for your project**: Copy this file to your project (e.g. `docs/design/diagram-style-guide.md`), modify it to match your brand, and add a `Diagram Style Guide` row to the **Project Document Index** in your root agent instruction file (`CLAUDE.md` / `AGENTS.md`) pointing to the copy.

**Aesthetic: Hand-drawn Blueprint** – white canvas, shade[1] fills, shade[4] strokes, Excalifont, `roughness: 1`. Zones (shade[0]) group by color family. Full preset spec in §13; dark mode §9.

**All colors come from the standard Excalidraw picker palette** (Open Color + Radix Bronze). Users can customize diagrams using the built-in color picker.

---

## 1. Shape Colors – Zone-Driven System

Color is driven by **spatial zones**, not by individual shape semantics. Shapes inherit color from the zone they belong to. This creates cohesion within sections and clear visual separation between sections.

### Zone Color Families

Pick 2–4 families for any diagram. Each family has a **zone background** (shade[0]), **shape fill** (shade[1]), and **shape stroke** (shade[4]).

| Family | Zone BG | Shape Fill | Shape Stroke | Best for |
|--------|---------|------------|--------------|----------|
| **Blue** | `#e7f5ff` (blue[0]) | `#a5d8ff` (blue[1]) | `#1971c2` (blue[4]) | Core systems, services, primary flow |
| **Violet** | `#f3f0ff` (violet[0]) | `#d0bfff` (violet[1]) | `#6741d9` (violet[4]) | Data layers, relational storage, databases |
| **Teal** | `#e6fcf5` (teal[0]) | `#96f2d7` (teal[1]) | `#099268` (teal[4]) | Execution, runtime, processing |
| **Bronze** | `#f8f1ee` (bronze[0]) | `#eaddd7` (bronze[1]) | `#846358` (bronze[4]) | External, infrastructure, warm contrast |
| **Cyan** | `#e3fafc` (cyan[0]) | `#99e9f2` (cyan[1]) | `#0c8599` (cyan[4]) | Search, indexing, derived data |

**Within a zone, ALL shapes use that zone's fill/stroke pair.** This is the core rule. A blue zone has blue shapes. A violet zone has violet shapes. The zone color makes the grouping obvious; labels and layout differentiate within a zone.

### Accent Colors (cross-cutting)

Use these for shapes that represent a **distinct category that appears across multiple zones** – config objects, triggers, outputs. Max 2–3 accent colors per diagram.

| Accent | Fill | Stroke | Use for |
|--------|------|--------|---------|
| **Orange** | `#ffd8a8` (orange[1]) | `#e8590c` (orange[4]) | Config, settings, external inputs |
| **Green** | `#b2f2bb` (green[1]) | `#2f9e44` (green[4]) | Success outputs, derived/built artifacts |
| **Cyan** | `#99e9f2` (cyan[1]) | `#0c8599` (cyan[4]) | Search, indexing, derived data |

### Signal Colors (rare – semantic labels only)

These are for **status badges or callout labels**, not for shape fills in the main diagram. Use them on small label rectangles placed beside shapes, or for legend entries.

| Signal | Fill | Stroke | Meaning |
|--------|------|--------|---------|
| **Red** | `#ffc9c9` (red[1]) | `#e03131` (red[4]) | Error, critical, authoritative |
| **Yellow** | `#ffec99` (yellow[1]) | `#f08c00` (yellow[4]) | Warning, entry point, trigger |

### Color Rules

1. **Zones first.** Decide your 2–3 zones, assign each a color family. All shapes in a zone use that family.
2. **Accents cross zones.** If a config shape appears in both the blue and violet zones, it's orange in both. The accent color marks a cross-cutting category.
3. **Signals are labels, not shapes.** A small "AUTHORITATIVE" badge beside a shape, not the shape itself.
4. **3–5 distinct colors total** in any diagram. Zone families (2–3) + accents (1–2). More than 5 is chaos.

### Semantic Color Overlay

Map a zone's concept → color family for a consistent visual vocabulary across diagrams.

| Concept | Color Family | Fill | Stroke | Rationale |
|---------|-------------|------|--------|-----------|
| **Core systems, services, primary flow** | Blue | `#a5d8ff` | `#1971c2` | Central, authoritative – the backbone |
| **AI / LLM, agents, intelligence** | Violet | `#d0bfff` | `#6741d9` | Distinct from traditional compute |
| **Execution, runtime, processing** | Teal | `#96f2d7` | `#099268` | Active, computational |
| **Data, storage, databases** | Cyan | `#99e9f2` | `#0c8599` | Cool, structured, informational |
| **External, infrastructure, third-party** | Bronze | `#eaddd7` | `#846358` | Warm, distinct from internal systems |
| **Security, auth, permissions** | Teal (dark) | `#96f2d7` | `#087f5b` | Guarded, protected – use dashed stroke to distinguish from runtime |
| **Config, settings, inputs** | Orange (accent) | `#ffd8a8` | `#e8590c` | Cross-cutting, attention-grabbing |
| **Success, outputs, built artifacts** | Green (accent) | `#b2f2bb` | `#2f9e44` | Positive outcome, completion |
| **Decision, condition, branching** | Yellow (signal) | `#ffec99` | `#f08c00` | Choice point, caution |
| **Error, critical, failure** | Red (signal) | `#ffc9c9` | `#e03131` | Danger, requires attention |

**Rules**:
1. **Zone assignment**: When a zone represents one of these concepts, use its mapped color family. A "Data Layer" zone → Cyan. An "AI Pipeline" zone → Violet.
2. **Multiple zones, same concept**: If two zones both represent "processing," use the same family (Teal) – differentiate with layout and labels, not color.
3. **Unknown concepts**: Default to Blue for primary, Bronze for secondary.
4. **Guidance, not law**: picks the family per zone; the zone-color rule still governs.

### Fill Style

| Fill Style | `fillStyle` | When to use |
|------------|-------------|-------------|
| **Solid** | `"solid"` | **Default.** Clean, readable, lets color and stroke do the work. |
| **Hachure** | `"hachure"` | Sparingly – 1–2 shapes per diagram that represent stored/accumulated state (caches, databases). Adds textural interest without clutter. |
| **Cross-hatch** | `"cross-hatch"` | Avoid in most diagrams. Renders as visual noise at typical zoom. |

---

## 2. Stroke & Border Styles

| Stroke Style | `strokeStyle` | Use for |
|--------------|---------------|---------|
| **Solid** | `"solid"` | Active shapes, primary connections |
| **Dashed** | `"dashed"` | Optional paths, planned elements, soft boundaries, convention-based relationships |
| **Dotted** | `"dotted"` | Implicit relationships, annotations |

### Stroke Width

| Width | `strokeWidth` | When to use |
|-------|---------------|-------------|
| **Thin** | `1` | Zone borders, structural lines, dependency arrows |
| **Standard** | `2` | **Default** – all shapes and most arrows |
| **Bold** | `4` | Primary flow path (one per diagram) |

---

## 3. Line & Arrow Styles

### Arrow Types

| Arrow style | Properties | When to use |
|-------------|------------|-------------|
| **Standard flow** | `strokeWidth: 2`, `endArrowhead: "arrow"` | Normal connections |
| **Primary flow** | `strokeWidth: 4`, `endArrowhead: "arrow"` | The main "happy path" |
| **Return / feedback** | `strokeWidth: 2`, `strokeStyle: "dashed"`, `endArrowhead: "arrow"` | Return paths, callbacks |
| **Bidirectional** | `startArrowhead: "arrow"`, `endArrowhead: "arrow"` | Two-way communication |
| **Dependency** | `strokeWidth: 1`, `strokeStyle: "dashed"`, `endArrowhead: "dot"` | References, "uses" |

### Arrow Colors

Default arrows use `#343a40` (gray[4]) – dark, neutral, receding.

**Semantic arrow colors** are allowed when you have **2–3 distinct relationship types** documented in a legend:

| Relationship | `strokeColor` | `strokeStyle` | Legend label example |
|-------------|---------------|---------------|---------------------|
| Enforced (FK, hard dep) | `#343a40` (gray[4]) | `"solid"` | "Enforced (FK)" |
| Convention (soft dep) | `#e03131` (red[4]) | `"dashed"` | "Convention (no FK)" |
| Derived (rebuildable) | `#0c8599` (cyan[4]) | `"dashed"` | "Derived (rebuildable)" |

**Rules**: If you use colored arrows, you MUST include a legend at the bottom of the diagram showing what each color/style combination means. Max 3 arrow types. Without a legend, all arrows should be gray.

### Arrow Routing (CRITICAL)

1. **Never route arrows through shapes.** Add waypoints to route around.
2. **20px minimum clearance** from nearby shapes.
3. **Right-angle routing** for complex paths (90-degree turns).
4. **Parallel arrows offset** by 15–20px.
5. **Arrow labels**: above/beside the line, never overlapping. 3 words max.

### Structural Lines

| Use | `strokeColor` | `strokeWidth` | `strokeStyle` |
|-----|---------------|---------------|---------------|
| Dividers | `#ced4da` (gray[2]) | `1` | `"solid"` |
| Timeline trunk | `#868e96` (gray[3]) | `2` | `"solid"` |
| Subtle guides | `#e9ecef` (gray[1]) | `1` | `"dotted"` |

---

## 4. Typography

### Font Family

| `fontFamily` | Font | When to use |
|--------------|------|-------------|
| `5` | Hand-drawn (Excalifont) | **Default.** Warm, human, distinctive. Pairs naturally with `roughness: 1`. |
| `6` | Normal (Nunito) | Clean technical diagrams when hand-drawn is too informal |
| `8` | Code (Comic Shanns – monospace) | Code snippets, technical values inside evidence artifacts |

**Do not use** `1` (Virgil), `2` (Helvetica), or `3` (Cascadia) – Excalidraw flags all three as `deprecated` in `font-metadata.ts`. They still load for backward compatibility but new exports must use the IDs above.

### Font Size Hierarchy

| Level | `fontSize` | Use for |
|-------|-----------|---------|
| **Diagram title** | `28`–`32` | Main heading – one per diagram |
| **Section heading** | `20`–`24` | Zone titles |
| **Shape label** | `16`–`18` | Text inside shapes |
| **Body text** | `16` | Descriptions, annotations |
| **Detail** | `14` | Secondary notes (sparingly) |

NEVER use fontSize below `14`.

### Text Colors

| Level | `strokeColor` | Use for |
|-------|---------------|---------|
| **Title** | `#1e1e1e` (black) | Diagram title |
| **Zone heading** | Zone's stroke color (e.g. `#1971c2` for blue zone) | Section labels – colored to match their zone |
| **Zone subtitle** | Zone's lighter shade or `#868e96` | Secondary zone info |
| **Body** | `#868e96` (gray[3]) | Annotations |
| **On light fills** | `#343a40` (gray[4]) | Text inside shapes |
| **On dark fills** | `#ffffff` (white) | Text in evidence artifacts or dark-mode shapes |

Zone headings use their zone's stroke color – this is what makes the diagram feel designed, not generic. Blue zone heading in `#1971c2`, violet zone heading in `#6741d9`, etc.

---

## 5. Shape Styling

### Roughness

| `roughness` | When to use |
|-------------|-------------|
| `0` | Formal presentations, ultra-clean |
| `1` | **Default** – slight hand-drawn warmth. The signature personality. |
| `2` | Brainstorming only |

### Roundness

`roundness: { "type": 3 }` on all rectangles – **always rounded corners**.

Omit only on evidence artifact containers (sharp = "code editor pane") and diamonds.

### Opacity

`opacity: 100` for all foreground shapes, text, and arrows.

Zone backgrounds: `opacity: 50` (see Section 6).

### Size Cascade (Non-Negotiable)

Element size encodes importance. A diagram where every shape is the same size is an **unreadable grid**. Pick sizes from this cascade so that hero : primary : secondary ≈ **3 : 1.8 : 1**.

| Role | W × H | Breathing room | Use for |
|------|-------|----------------|---------|
| **Hero** | `320 × 160` | ≥ 160px on all sides | The single most important element – one per diagram |
| **Primary** | `180 × 90` | 40–60px | Zone-level nodes, primary flow participants |
| **Secondary** | `120 × 60` | 20–40px | Supporting nodes, list items, leaves |
| **Marker / Badge** | `12 × 12` to `80 × 28` | ≤ 20px | Timeline dots, signal badges, anchor points |
| **Evidence artifact** | 1.2–1.8× widest neighbor; `min height 80` | 40–60px | Code snippets, data shapes – always darkest on canvas |

**Rules**:
1. **Exactly one hero.** Two heroes = no hero.
2. **Squint test**: blur your eyes at 20% opacity – the hero must still dominate. If it doesn't, enlarge it or shrink the secondaries.
3. **Never reuse the hero size** on another shape. Primary-sized shapes may repeat; secondary-sized shapes repeat freely.
4. **Ellipses and diamonds need more room than rectangles for the same label** (ellipse ≈ 1.4×, diamond ≈ 2×). Up-size them from the cascade numbers. See `element-format.md` § Label Auto-Sizing.

### Anti-Uniformity Rule

**Never place 6+ shapes with identical `(type, width, height, backgroundColor)`.** This is the defining AI-aesthetic failure mode. Break uniform runs with ONE of:

- A larger **anchor** shape (1.5× primary size) every 3–4 items
- **Alternating row heights** (row 1: 90px, row 2: 60px) or a deliberate 60–80px gap at a conceptual boundary
- An **evidence artifact** inserted mid-sequence
- **Hachure fill** on every 3rd shape (adds texture variation inside one color family)

Check yourself: if you just generated a 3×4 or 4×3 grid of same-size rectangles, you have failed. Go back and apply a rhythm breaker.

### Shape Vocabulary

Each Excalidraw shape type carries a visual connotation. Use shapes consistently so viewers learn the vocabulary as they read the diagram.

| Shape | Excalidraw Type | Conveys | Examples |
|-------|----------------|---------|----------|
| **No shape** | free-floating text | Annotation, label, heading | Section titles, descriptions, detail notes |
| **Rounded rectangle** | `rectangle` + `roundness: {"type": 3}` | Process, action, component | Services, functions, pipeline stages |
| **Ellipse** | `ellipse` | State, origin, or destination | Start/end points, inputs/outputs, triggers |
| **Diamond** | `diamond` | Decision or condition | Branching logic, feature flags, conditionals |
| **Small dot** | `ellipse` (10-20px) | Marker or anchor point | Timeline steps, bullet points, connection nodes |
| **Overlapping ellipses** | multiple `ellipse` | Abstract / fuzzy concept | Context, memory, ambient state |
| **Lines + text** | `line` + free text | Hierarchical structure | Tree branches, org charts, taxonomies |

---

## 6. Section / Zone Backgrounds

Zones are large rounded rectangles that group related components. They are the backbone of the color system – each zone claims a color family.

### Zone Styling

```
backgroundColor: <family>[0]  (lightest shade – subtle tint)
strokeColor:     <family>[1]  (light shade – visible but soft border)
fillStyle:       "solid"
opacity:         50
strokeStyle:     "solid"
strokeWidth:     1
roughness:       0
roundness:       { "type": 3 }
```

- Place zones FIRST in the elements array (back of z-order)
- Each zone gets its own color family – this is the core of the visual system

### Zone Labels

Place the zone title as free-floating text inside the top-left of the zone. Use the zone family's **stroke color** (shade[4]) and `fontSize: 20`–`24`, `fontFamily: 5` (Excalifont). Example: "File-Based Storage" in `#1971c2` (blue[4]) inside a blue zone.

---

## 7. Evidence Artifacts (Technical Diagrams)

Dark "editor pane" containers for code, data examples, and concrete evidence.

### Container

```json
{ "type": "rectangle",
  "backgroundColor": "#343a40", "fillStyle": "solid",
  "strokeColor": "#1e1e1e", "strokeWidth": 2,
  "roughness": 0 }
```

Sharp corners (no `roundness`), clean edges (`roughness: 0`), bold border.

### Text Inside Artifacts

| Content type | `strokeColor` |
|-------------|---------------|
| Code | `#f8f9fa` (gray[0]) |
| JSON / data | `#69db7c` (green[2]) |
| Terminal output | `#eaddd7` (bronze[1]) |
| Config | `#3bc9db` (cyan[2]) |
| Keywords | `#f783ac` (pink[2]) |
| Strings | `#69db7c` (green[2]) |
| Numbers | `#ffd43b` (yellow[2]) |
| Types | `#4dabf7` (blue[2]) |
| Comments | `#868e96` (gray[3]) |

All evidence text: `fontFamily: 8` (Comic Shanns – Excalidraw's current monospace), `fontSize: 14`.

---

## 8. Canvas Background

| Property | Value |
|----------|-------|
| `viewBackgroundColor` | `#ffffff` (white) |

---

## 9. Dark Mode (Alternative)

For dark-themed diagrams, invert the shade mapping: shape fills use shade[4] (dark), strokes use shade[2] (bright). Zones use shade[4] at `opacity: 30` with invisible borders.

### Dark Mode Setup

Set `viewBackgroundColor: "#1e1e1e"` in appState, or place a bg rectangle:

```json
{ "type": "rectangle", "id": "darkbg", "x": -4000, "y": -3000, "width": 10000, "height": 7500,
  "backgroundColor": "#343a40", "fillStyle": "solid",
  "strokeColor": "transparent", "strokeWidth": 0, "roughness": 0 }
```

### Dark Mode Zone Families

| Family | Zone fill (`opacity: 30`) | Shape fill | Shape stroke (bright) |
|--------|--------------------------|------------|-----------------------|
| **Blue** | `#1971c2` | `#1971c2` | `#4dabf7` |
| **Teal** | `#099268` | `#099268` | `#38d9a9` |
| **Violet** | `#6741d9` | `#6741d9` | `#9775fa` |
| **Bronze** | `#846358` | `#846358` | `#d2bab0` |
| **Cyan** | `#0c8599` | `#0c8599` | `#3bc9db` |

Zone borders: `strokeColor: "transparent"` – the color tint alone defines the zone.

### Dark Mode Text & Arrows

Title: `#e9ecef` · Zone headings: zone's bright stroke (shade[2]) · Body: `#ced4da` · Shape labels: `#e9ecef` · Arrows: `#ced4da` · Error arrows: `#ff8787`

### Dark Mode Accents

| Accent | Fill | Stroke |
|--------|------|--------|
| **Orange** | `#e8590c` | `#ffa94d` |
| **Green** | `#2f9e44` | `#69db7c` |
| **Yellow** | `#f08c00` | `#ffd43b` |
| **Red** | `#e03131` | `#ff8787` |

---

## 10. Signal Badges (Status Without Shape Pollution)

When a shape needs a status or category tag (ASYNC, DEPRECATED, NEW, CRITICAL, CONTEXT:FORK), attach a small badge rather than changing the shape's color – that preserves zone-color semantics.

| Property | Value |
|----------|-------|
| Size | `60–100 × 24–28` (pill or tight rounded rect) |
| Position | Top-right corner of parent, overlapping border by ~50% |
| `backgroundColor` | Signal palette only (Red / Yellow / Green) |
| `roundness` | `{ "type": 3 }` |
| Text | `fontSize 12–14`, uppercase, 1–2 words |
| `strokeWidth` | `1` |

**Rules**: Badges are not arrow endpoints. Max 2 badge types per diagram. Max 20% of shapes get a badge – if more need one, the status belongs in a separate diagram layer.

---

## 11. Density Gradient (for XL / XXL canvases)

On canvases ≥ 1200px wide, partition the canvas into three density bands so the eye knows where to start and where to drill into. Without this, a large diagram reads as a flat sea of boxes.

| Band | Canvas area | Element density | Content |
|------|-------------|-----------------|---------|
| **Sparse** (entry side) | ~40% | ~20% of shapes | Hero, 1–2 zones, primary title, bold arrows |
| **Medium** (center) | ~20% | ~40% of shapes | Primary flow, 8–12 nodes |
| **Dense** (exit side) | ~40% | ~40% of shapes | Detail, leaf nodes, evidence artifacts |

**Rules**:
- Evidence artifacts always live in the Dense band.
- Transition between bands is a 60–80px whitespace gap or a thin 1px divider – never a hard zone boundary.
- Entry-side asymmetry: give **more** whitespace on the side the eye enters from (left/top for L→R flow). Entry-side padding ≈ 1.5× exit-side padding.

---

## 12. Design Principles

### Structure and Specificity

**Structure is the argument.** Two litmus tests:
1. **Structure test** – Cover all text. Does shape arrangement alone convey the core relationship? A fan-out radiating arrows says "one source, many targets" without labels. A grid of equal boxes is decoration.
2. **Specificity test** – Real API names, actual data formats, genuine code snippets? `handleWebhook(event: StripeEvent)` teaches; `"Process" → "Handler"` merely labels.

| Weak | Strong | Why |
|------|--------|-----|
| Equal-sized boxes | Sizes reflect importance (hero → primary → small) | Scale encodes hierarchy |
| Every label in a rectangle | Most text free-floating; boxes for connectable entities | Typography creates hierarchy |
| One shape type throughout | Different shapes per concept (ellipse = state, diamond = decision, rectangle = action) | Shape vocabulary mirrors concept vocabulary |
| Arrows implied by proximity | Explicit arrows with typed endpoints | Relationships must be visible, not assumed |

### Evidence Artifacts

Embed real, verifiable details directly into the diagram – not "Service A → Service B" but actual function signatures, data shapes, event names, and API endpoints. All artifacts use the dark "editor pane" container (Section 7 Evidence Artifacts): dark background, monospace font, syntax-colored text. Types: code snippets, JSON data shapes, sequences (timeline pattern), real HTTP inputs, UI fragments (nested rectangles), method signatures (inline monospace in shape labels).

### Multi-Zoom Rule

A comprehensive technical diagram is readable at three distances: **Overview** (large shapes + bold arrows show the full pipeline), **Sections** (zone backgrounds + section headings group related elements), **Detail** (dark "editor pane" containers with monospace text show evidence artifacts). All three coexist on one canvas; the eye scans overview → section → detail.

### Text Placement Strategy

Default to **free-floating text**. Add a container only when the element needs to be an arrow endpoint, carries shape-semantic meaning (diamond = decision, ellipse = state), or is a section anchor. Keep section titles, annotations, and nearby descriptive labels free-floating – font size and position create hierarchy without borders.

**Box-budget rule**: Fewer than 30% of text elements inside containers. Over-containing makes a diagram look like a form. Use font size (28px title → 16px body) and color (zone stroke for headings → gray for annotations) to create hierarchy.

### Anti-Patterns

- **Per-shape coloring.** Don't assign colors to individual shapes. Assign colors to zones and categories.
- **More than 5–6 colors.** Zone families (2–4) + accents (1–2) = 3–6 max.
- **Cross-hatch.** Renders as noise at diagram scale. Use shape type (ellipse vs rectangle) for differentiation.
- **Monochrome monotony.** "Everything one color" is as bad as rainbow chaos. Use 2–4 zone families.
- **Black zone headings.** Zone headings should match their zone's stroke color. This is the cohesion signal.
- **Saturated fills (shade[2]+).** Use shade[1] for fills, shade[0] for zones. Shade[2] is too heavy for fills – it fights text readability and makes diagrams feel garish.

---

## 13. Aesthetic Presets

This style guide defaults to the **Hand-drawn Blueprint** aesthetic. To use a different preset, override the settings listed below in your project's copy of this file. Everything not listed stays the same – presets only change the "mood," not the color system or layout rules.

### Preset 1: Hand-drawn Blueprint (Default)

The current default – no changes needed.

| Setting | Value |
|---------|-------|
| `viewBackgroundColor` | `#ffffff` (white) |
| `roughness` | `1` (hand-drawn warmth) |
| `fontFamily` | `5` (Excalifont – hand-drawn) |
| `fillStyle` | `"solid"` (default), `"hachure"` for accumulated state |
| Zone fills | Shade[0] at `opacity: 50` |
| Shape fills | Shade[1] (pastel) |
| Shape strokes | Shade[4] (strong, saturated) |

### Preset 2: Warm Industrial

Inspired by engineering schematics on aged paper. Warm parchment background, desaturated fills, saturated strokes. Same zone-color system, warmer ground tone.

| Setting | Default → Override |
|---------|-------------------|
| `viewBackgroundColor` | `#ffffff` → `#faf8f5` (warm parchment) |
| `roughness` | `1` (keep hand-drawn) |
| `fontFamily` | `5` (keep Excalifont) |
| Shape fills | Shade[1] → desaturated warm variants (reduce saturation ~20%, shift hue toward warm) |
| Shape strokes | Keep shade[4] (strokes carry the color identity) |
| Zone fills | Shade[0] → warm-shifted tints (e.g. blue zone: `#eef3f8` instead of `#e7f5ff`) |
| Zone strokes | `"transparent"` – the warm tint alone defines zones |
| Zone `opacity` | `50` → `40` (subtler on parchment) |
| Evidence artifacts bg | `#343a40` → `#1a1612` (warm near-black) |
| Body text color | `#868e96` → `#8c8378` (warm gray) |
| Title text color | `#1e1e1e` → `#1a1612` (near-black with warmth) |
| Arrow color | `#343a40` → `#3d3832` (warm dark gray) |

**Personality**: Warm, tactile, grounded. Good for diagrams that need to feel substantial and crafted.

### Preset 3: Clean Technical

Precise, formal, presentation-ready. No hand-drawn wobble, Nunito font, solid fills only. The "polished PDF" look.

| Setting | Default → Override |
|---------|-------------------|
| `viewBackgroundColor` | `#ffffff` (keep white) |
| `roughness` | `1` → `0` (crisp, no wobble – all elements) |
| `fontFamily` | `5` → `6` (Nunito – clean, technical) |
| `fillStyle` | No `"hachure"` anywhere – `"solid"` for everything |
| `strokeWidth` | Standard `2` → `1` for shapes, `2` for primary flow only |
| Zone `roughness` | Already `0` (no change) |
| Zone `opacity` | `50` → `30` (very subtle – zones are hints, not regions) |
| Evidence artifacts | Keep `roughness: 0`, use `fontFamily: 8` (Comic Shanns – monospace) |
| `roundness` | Keep `{ "type": 3 }` – rounded corners complement clean lines |

**Personality**: Precise, corporate, restrained. Good for technical documentation, presentations, and formal architecture diagrams.

### Choosing a Preset

| If the diagram is... | Use |
|---------------------|-----|
| Exploratory, educational, whiteboard-style | **Hand-drawn Blueprint** |
| Technical but needs warmth and character | **Warm Industrial** |
| For a presentation, documentation, or formal audience | **Clean Technical** |
| Brand-specific | Copy any preset and customize fills/strokes to brand colors |
