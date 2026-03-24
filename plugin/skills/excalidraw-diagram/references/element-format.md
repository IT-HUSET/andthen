# Excalidraw Element Format

Reference for generating Excalidraw JSON elements. Read `style-guide.md` alongside this for all visual styling (colors, fill styles, stroke patterns, typography, roughness, etc.).

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

**Note**: The style guide overrides many of these defaults (e.g. `fillStyle: "hachure"` for primary shapes, specific stroke/fill color pairs). Always consult the style guide for the correct values per element type.

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
{ "type": "text", "id": "t1", "x": 150, "y": 138, "text": "Hello", "fontSize": 20 }
```

- `x` is the LEFT edge of the text
- To center text at position cx: set `x = cx - estimatedWidth/2`
- `estimatedWidth ≈ text.length × fontSize × 0.5`
- Do NOT rely on `textAlign` or `width` for positioning – they only affect multi-line wrapping

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

NEVER use fontSize below 14 – it becomes unreadable.

### Element Sizes

- Minimum shape size: **120x60** for labeled rectangles/ellipses
- Leave **20-30px gaps** between elements minimum
- Prefer fewer, larger elements over many tiny ones

### Canvas & Padding

- **Padding**: Leave **40–80px** margin between the outermost elements and the canvas edge
- **Aspect ratio**: Prefer **4:3** (e.g. 800×600, 1200×900) – renders cleanly and avoids distortion when scaled
- **Scale fonts with canvas**: At large canvas sizes (1200+ wide), increase font minimums – 16px body text becomes hard to read. See the Canvas Sizing table in the main skill file for per-size font guidance

### Roughness

- `roughness: 0` – Clean, crisp (modern/technical). **Default for professional diagrams.**
- `roughness: 1` – Hand-drawn feel (brainstorming/informal)

---

## Complete Example: Two Connected Labeled Boxes

Uses the default "Schematic Warmth" style – bronze hachure for the primary shape, green solid for success, warm parchment canvas.

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
