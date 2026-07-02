# Excalidraw Element Format

Reference for generating Excalidraw JSON elements. Read `style-guide.md` alongside this for all visual styling (colors, fill styles, stroke patterns, typography, roughness, etc.).

## Contents

- JSON Structure
- Required Fields & Defaults
- Element Types (rectangle, ellipse, diamond, labeled shape/arrow, text, arrow, line, marker dot)
- Arrow Bindings (fixedPoint table)
- Sizing Rules (font sizes, font families, element sizes, label auto-sizing, text metrics, canvas/padding, roughness)
- Complete Example
- Common Mistakes

---

## JSON Structure

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [...],
  "appState": {
    "viewBackgroundColor": "#ffffff",
    "gridSize": 20
  },
  "files": {}
}
```

---

## Required Fields (all elements)

`type`, `id` (unique string), `x`, `y`, `width`, `height`

## Defaults (skip these – they apply automatically)

`strokeColor="#1e1e1e"`, `backgroundColor="transparent"`, `fillStyle="solid"`, `strokeWidth=2`, `roughness=1`, `opacity=100`

**Note**: The style guide overrides many of these defaults (specific stroke/fill color pairs; `fillStyle: "solid"` for shapes, `"hachure"` only for 1–2 accumulated-state shapes). Always consult the style guide for the correct values per element type.

---

## Element Types

### Rectangle

```json
{ "type": "rectangle", "id": "r1", "x": 100, "y": 100, "width": 200, "height": 100 }
```

- `roundness: { "type": 3 }` for rounded corners
- `backgroundColor: "#a5d8ff"`, `fillStyle: "solid"` for filled

### Ellipse

```json
{ "type": "ellipse", "id": "e1", "x": 100, "y": 100, "width": 150, "height": 150 }
```

### Diamond

```json
{ "type": "diamond", "id": "d1", "x": 100, "y": 100, "width": 150, "height": 150 }
```

### Labeled Shape (PREFERRED)

Add `label` to any shape for auto-centered text. No separate text element needed:

```json
{ "type": "rectangle", "id": "r1", "x": 100, "y": 100, "width": 200, "height": 80,
  "roundness": { "type": 3 }, "backgroundColor": "#a5d8ff", "fillStyle": "solid",
  "label": { "text": "Hello", "fontSize": 20 } }
```

- Works on rectangle, ellipse, diamond
- Text auto-centers and container auto-resizes to fit
- Saves tokens vs separate text elements
- The render template converts these to full format via `convertToExcalidrawElements`

### Labeled Arrow

```json
{ "type": "arrow", "id": "a1", "x": 300, "y": 150, "width": 200, "height": 0,
  "points": [[0,0],[200,0]], "endArrowhead": "arrow",
  "label": { "text": "connects" } }
```

### Standalone Text (titles, annotations only)

```json
{ "type": "text", "id": "t1", "x": 150, "y": 138, "text": "Hello", "fontSize": 20, "fontFamily": 5 }
```

- `x` is the LEFT edge of the text
- To center text at position cx: set `x = cx - estimatedWidth/2`
- `estimatedWidth ≈ text.length × fontSize × 0.5` (rough; see § Text Metrics for per-font rates)
- Do NOT rely on `textAlign` or `width` for positioning – they only affect multi-line wrapping
- **`width`/`height` may be omitted** – the render template's `getConvertedJSON` measures text via Canvas `measureText` with the actual Excalidraw font and patches dimensions into the portable file. If you skip the portable export and save the raw authored form, `app.excalidraw.com` will show clipped text that only fixes itself when the user clicks the element.

### Arrow

```json
{ "type": "arrow", "id": "a1", "x": 300, "y": 150, "width": 200, "height": 0,
  "points": [[0,0],[200,0]], "endArrowhead": "arrow" }
```

- `points`: `[dx, dy]` offsets from element `x`, `y`
- `endArrowhead`: `null` | `"arrow"` | `"bar"` | `"dot"` | `"triangle"`
- For curves: use 3+ points in `points` array

### Line (structural, not arrow)

```json
{ "type": "line", "id": "l1", "x": 100, "y": 100, "width": 0, "height": 200,
  "points": [[0,0],[0,200]], "strokeColor": "#757575" }
```

Use for timelines, tree structures, dividers – not for connections (use arrows for those).

### Small Marker Dot

```json
{ "type": "ellipse", "id": "dot1", "x": 94, "y": 94, "width": 12, "height": 12,
  "backgroundColor": "#4a9eed", "fillStyle": "solid", "strokeColor": "#4a9eed" }
```

Use for timeline markers, bullet points, connection nodes.

---

## Arrow Bindings

Connect arrows to shapes using `startBinding` and `endBinding`:

```json
{
  "type": "arrow", "id": "a1", "x": 300, "y": 150, "width": 150, "height": 0,
  "points": [[0,0],[150,0]], "endArrowhead": "arrow",
  "startBinding": { "elementId": "r1", "fixedPoint": [1, 0.5] },
  "endBinding": { "elementId": "r2", "fixedPoint": [0, 0.5] }
}
```

**fixedPoint** values (normalized 0-1 from top-left):

| Position | fixedPoint |
|----------|-----------|
| Top center | `[0.5, 0]` |
| Bottom center | `[0.5, 1]` |
| Left center | `[0, 0.5]` |
| Right center | `[1, 0.5]` |

---

## Sizing Rules

### Font Sizes

| Use | Min fontSize |
|-----|-------------|
| Titles, headings | **20** |
| Body text, labels | **16** |
| Secondary annotations (sparingly) | **14** |

Below 14px reads as unreadable – do not go lower.

### Font Family IDs

Text and label elements carry a numeric `fontFamily`. Use the current, non-deprecated IDs:

| `fontFamily` | Font | Use |
|--------------|------|-----|
| `5` | Excalifont | Hand-drawn default (replaces legacy `1` Virgil) |
| `6` | Nunito | Clean sans-serif (replaces legacy `2` Helvetica) |
| `8` | Comic Shanns | Monospace / code (replaces legacy `3` Cascadia) |

Never emit legacy IDs `1`/`2`/`3` – flagged `deprecated` in Excalidraw's `font-metadata.ts`. See `style-guide.md` §4.

### Element Sizes

- Minimum shape size: **120×60** for labeled rectangles (smaller for markers/badges only)
- Leave **20–40px gaps** between related elements, **60–80px** between unrelated elements
- Prefer fewer, larger elements over many tiny ones
- **Snap all `x`, `y`, `width`, `height` values to multiples of 20** (Excalidraw's default grid). Off-grid values produce an "almost aligned" look that reads as sloppy.
- For size cascade (hero / primary / secondary / marker), see `style-guide.md` § Size Cascade

### Label Auto-Sizing (CRITICAL)

When you attach `label: { text: "..." }` to a shape, Excalidraw computes a minimum container size from the text bounds, and `redrawTextBoundingBox` **silently expands the container at render time** if the supplied width is too small. This is the top cause of "boxes that end up all the same size" and of text overflowing or going missing.

**Internal padding**: `BOUND_TEXT_PADDING = 8px` per side (16px total).

**Minimum dimensions to fit a label** (where `W` and `H` are the measured text bounds):

| Shape | Min width | Min height | Scaling note |
|-------|-----------|------------|--------------|
| **Rectangle** | `W + 16` | `H + 16` | Baseline – tightest fit |
| **Ellipse** | `≈ (W + 16) × √2` | `≈ (H + 16) × √2` | Inscribed rectangle geometry – needs **~1.4×** a rectangle |
| **Diamond** | `2 × (W + 16)` | `2 × (H + 16)` | Rhombus geometry – needs **~2×** a rectangle |
| **Arrow (labeled)** | `W + 128` | – | Very generous padding |

**Implication**: do **not** use identical widths for a rectangle and an ellipse that hold the same label. The ellipse will look crammed or force text to overflow.

### Text Metrics (for pre-sizing)

Approximate character widths per font at common sizes. Use to estimate `W` before picking a container size. Add 20% padding on top of the estimate for safety.

| `fontFamily` | Font | `fontSize 16` | `fontSize 18` | `fontSize 24` |
|--------------|------|---------------|---------------|---------------|
| `5` | Excalifont | ~9px/char | ~10px/char | ~13px/char |
| `6` | Nunito | ~8px/char | ~9px/char | ~12px/char |
| `8` | Comic Shanns (mono) | ~10px/char | ~11px/char | ~14px/char |

**Quick sizing examples** (fontFamily 5, fontSize 18, 14-character label):
- Rectangle: `W ≈ 140`, min width `156`, **practical 220×60**
- Ellipse: needs `≈ 1.4× rect`, **practical 260×80**
- Diamond: needs `≈ 2× rect`, **practical 340×120**

### When to Specify Width/Height vs. Auto-Size

- **Specify** explicitly for every non-marker shape. This is how hierarchy is preserved – the size cascade (hero / primary / secondary) only works if you pick the numbers.
- **Auto-size** (omit `width`/`height`) only for marker dots, signal badges, and throwaway shapes where the label's natural size is fine.
- **Over-size rather than under-size.** If you're unsure the label fits, add 20–40px of slack. Excalidraw will silently grow under-sized containers, collapsing your hierarchy back toward uniformity.

### Canvas & Padding

- **Padding**: Leave **40–80px** margin between the outermost elements and the canvas edge
- **Aspect ratio**: Prefer **4:3** (e.g. 800×600, 1200×900) – renders cleanly and avoids distortion when scaled
- **Scale fonts with canvas**: At large canvas sizes (1200+ wide), increase font minimums – 16px body text becomes hard to read. See the Canvas Sizing table in the main skill file for per-size font guidance

### Roughness

Style-guide concern – see `style-guide.md` §5 (default `1`; presets override).

---

## Complete Example: Two Connected Labeled Boxes

Illustrates a bronze zone family + green accent on the **Warm Industrial** preset (warm parchment canvas). For the default **Hand-drawn Blueprint** preset, swap the canvas to `#ffffff` and use one of the zone families from the style guide – see `style-guide.md` for the full palette.

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    { "type": "rectangle", "id": "b1", "x": 100, "y": 100, "width": 200, "height": 100,
      "roundness": { "type": 3 }, "roughness": 1,
      "backgroundColor": "#eaddd7", "strokeColor": "#846358",
      "fillStyle": "hachure", "strokeWidth": 2,
      "label": { "text": "Process", "fontSize": 18 } },
    { "type": "rectangle", "id": "b2", "x": 450, "y": 100, "width": 200, "height": 100,
      "roundness": { "type": 3 }, "roughness": 1,
      "backgroundColor": "#b2f2bb", "strokeColor": "#2f9e44",
      "fillStyle": "solid", "strokeWidth": 2,
      "label": { "text": "Done", "fontSize": 18 } },
    { "type": "arrow", "id": "a1", "x": 300, "y": 150, "width": 150, "height": 0,
      "points": [[0,0],[150,0]], "endArrowhead": "arrow",
      "strokeColor": "#846358", "strokeWidth": 2, "roughness": 1,
      "startBinding": { "elementId": "b1", "fixedPoint": [1, 0.5] },
      "endBinding": { "elementId": "b2", "fixedPoint": [0, 0.5] } }
  ],
  "appState": { "viewBackgroundColor": "#fdf8f6", "gridSize": 20 },
  "files": {}
}
```

---

## Common Mistakes

- **Arrow labels need space**: Long labels overflow short arrows. Keep labels short or make arrows wider.
- **Elements overlap when y-coordinates are close**: Always check that text, boxes, and labels don't stack on top of each other.
- **Emoji don't render**: Do NOT use emoji in text – they don't render in Excalidraw's font.
- **Forgetting `fillStyle: "solid"`**: Without this, `backgroundColor` won't show.
- **Reusing IDs**: Every element must have a unique `id`. Use descriptive names like `"auth_box"`, `"arrow_to_db"`.
