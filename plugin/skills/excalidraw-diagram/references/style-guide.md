# Diagram Style Guide (Default)

**Default visual style for generated Excalidraw diagrams.** This file is the fallback when a project does not configure its own style guide.

**To customize for your project**: Copy this file to your project (e.g. `docs/design/diagram-style-guide.md`), modify it to match your brand, and add a `Diagram Style Guide` row to the **Project Document Index** in your CLAUDE.md pointing to the copy.

**Aesthetic: Hand-drawn Blueprint** – clean white canvas, pastel-tinted shapes with confident strokes, and spatial zones that group by color family. Shapes use light shade[1] fills with strong shade[4] strokes. The hand-drawn Virgil font and `roughness: 1` give warmth. Zones use the lightest shade[0] tints as subtle spatial grouping. The result feels like a skilled architect's whiteboard sketch – organized, colorful but cohesive, approachable. Dark mode is a well-supported alternative (Section 9).

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

When deciding which color family to assign to a zone, use this mapping. It provides a consistent visual vocabulary so the same concept looks the same across different diagrams.

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
4. **This is guidance, not law**: The zone-driven system (shapes inherit from their zone) still takes precedence. Semantic colors tell you which family to *pick* for each zone – they don't override the zone-color rule.

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
| `1` | Hand-drawn (Virgil) | **Default.** Warm, human, distinctive. Pairs naturally with `roughness: 1`. |
| `2` | Normal (Helvetica) | Clean technical diagrams when hand-drawn is too informal |
| `3` | Code (monospace) | Code snippets, technical values inside evidence artifacts |

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

- Zones use **shade[0]** fill and **shade[1]** stroke – subtle tinted regions
- `opacity: 50` keeps zones present without overwhelming shape fills (which are shade[1] at opacity 100)
- `strokeWidth: 1` – visible but secondary to shape strokes
- `roughness: 0` – zones should be clean even in hand-drawn diagrams
- **Rounded corners** always
- Place zones FIRST in the elements array (back of z-order)
- Each zone gets its own color family – this is the core of the visual system

### Zone Labels

Place the zone title as free-floating text inside the top-left of the zone. Use the zone family's **stroke color** (shade[4]) and `fontSize: 20`–`24`, `fontFamily: 1` (Virgil). Example: "File-Based Storage" in `#1971c2` (blue[4]) inside a blue zone.

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

All evidence text: `fontFamily: 3` (monospace), `fontSize: 14`.

---

## 8. Canvas Background

| Property | Value |
|----------|-------|
| `viewBackgroundColor` | `#ffffff` (white) |

Clean white canvas. The pastel shade[1] fills and shade[0] zone tints provide all the warmth and color needed – a white canvas gives maximum contrast for everything.

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

## 10. Design Principles

### The Zone-Color Rule

**Shapes inherit color from their zone.** This single rule prevents rainbow chaos while allowing rich visual variety across sections:

- A diagram with 2 zones (blue, violet) + 2 accents (orange, green) uses 4 colors – cohesive because each zone is internally consistent.
- Compare to a diagram where every shape picks from 13 colors – it looks chaotic because there's no spatial logic.

### What Makes This Style Work

1. **Zones create color neighborhoods.** All the blue shapes form a visual cluster. All the violet shapes form another. The eye groups them automatically – structure and color reinforce each other.

2. **Pastel fills, strong strokes.** Shade[1] fills are soft and readable. Shade[4] strokes carry the color identity. The shape is defined by its stroke; the fill provides a gentle tint. Text on light fills is always legible.

3. **Colored zone headings unify.** "File-Based Storage" in `#1971c2` inside a blue zone ties the heading to its content. Black headings feel disconnected.

4. **Accents break the pattern with purpose.** An orange "Config" shape inside a blue zone stands out immediately as "different category." The color contrast communicates without needing a label.

5. **Hand-drawn warmth (roughness 1 + Virgil font).** The handwriting and slight wobble make diagrams feel like a skilled architect's whiteboard sketch – approachable and human.

6. **Legends earn colored arrows.** Colored arrows are powerful but require discipline. If you use them, include a legend at the bottom. Max 3 arrow types.

### Anti-Patterns

- **Per-shape coloring.** Don't assign colors to individual shapes. Assign colors to zones and categories.
- **More than 5–6 colors.** Zone families (2–4) + accents (1–2) = 3–6 max.
- **Cross-hatch.** Renders as noise at diagram scale. Use shape type (ellipse vs rectangle) for differentiation.
- **Monochrome monotony.** "Everything one color" is as bad as rainbow chaos. Use 2–4 zone families.
- **Black zone headings.** Zone headings should match their zone's stroke color. This is the cohesion signal.
- **Saturated fills (shade[2]+).** Use shade[1] for fills, shade[0] for zones. Shade[2] is too heavy for fills – it fights text readability and makes diagrams feel garish.

---

## 11. Aesthetic Presets

This style guide defaults to the **Hand-drawn Blueprint** aesthetic. To use a different preset, override the settings listed below in your project's copy of this file. Everything not listed stays the same – presets only change the "mood," not the color system or layout rules.

### Preset 1: Hand-drawn Blueprint (Default)

The current default – no changes needed. Clean white canvas, pastel-tinted shapes with confident strokes, Virgil handwriting font. Feels like a skilled architect's whiteboard sketch.

| Setting | Value |
|---------|-------|
| `viewBackgroundColor` | `#ffffff` (white) |
| `roughness` | `1` (hand-drawn warmth) |
| `fontFamily` | `1` (Virgil – hand-drawn) |
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
| `fontFamily` | `1` (keep Virgil) |
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

Precise, formal, presentation-ready. No hand-drawn wobble, Helvetica font, solid fills only. The "polished PDF" look.

| Setting | Default → Override |
|---------|-------------------|
| `viewBackgroundColor` | `#ffffff` (keep white) |
| `roughness` | `1` → `0` (crisp, no wobble – all elements) |
| `fontFamily` | `1` → `2` (Helvetica – clean, technical) |
| `fillStyle` | No `"hachure"` anywhere – `"solid"` for everything |
| `strokeWidth` | Standard `2` → `1` for shapes, `2` for primary flow only |
| Zone `roughness` | Already `0` (no change) |
| Zone `opacity` | `50` → `30` (very subtle – zones are hints, not regions) |
| Evidence artifacts | Keep `roughness: 0`, use `fontFamily: 3` (monospace) |
| `roundness` | Keep `{ "type": 3 }` – rounded corners complement clean lines |

**Personality**: Precise, corporate, restrained. Good for technical documentation, presentations, and formal architecture diagrams.

### Choosing a Preset

| If the diagram is... | Use |
|---------------------|-----|
| Exploratory, educational, whiteboard-style | **Hand-drawn Blueprint** |
| Technical but needs warmth and character | **Warm Industrial** |
| For a presentation, documentation, or formal audience | **Clean Technical** |
| Brand-specific | Copy any preset and customize fills/strokes to brand colors |
