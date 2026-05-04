# Diagrams Template

Inline-SVG diagrams generated at HTML emission time. All diagrams use:

- Pure SVG (no `<foreignObject>`, no library dependencies)
- Coordinates computed in the agent at write time, baked into the SVG markup
- Class hooks that key off the page-level CSS variables (`--accent`, `--panel`, etc.)


## Shared Container

Each diagram emitter calls `wrapSvg(type, width, height, body)` to produce the container below — `type` selects the `diagram-{type}` class, `width`/`height` set the `viewBox`, and `body` is substituted for the `<!-- nodes, lines, text -->` slot.

```html
<svg class="diagram diagram-{{type}}"
     viewBox="0 0 {{width}} {{height}}"
     xmlns="http://www.w3.org/2000/svg"
     role="img"
     aria-label="{{type}} diagram for {{section}}">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--text-muted)"/>
    </marker>
  </defs>
  <!-- nodes, lines, text -->
</svg>
```

Define the arrow marker once per diagram (or once per page if multiple diagrams). Use `currentColor` and CSS variables where possible so theme changes propagate.

```css
.diagram { background: var(--panel); border-radius: 8px; padding: 1rem; margin: 0.5rem 0; max-width: 100%; }
.diagram text { fill: var(--text); font-family: var(--ui); font-size: 12px; }
.diagram .axis { stroke: var(--border); stroke-width: 1; }
.diagram .node { fill: var(--panel); stroke: var(--accent); stroke-width: 1.5; }
.diagram .node-pruned { stroke: var(--text-muted); opacity: 0.5; }
.diagram .node-chosen { fill: var(--accent); }
.diagram .edge { stroke: var(--border); stroke-width: 1; fill: none; }
.diagram .label-muted { fill: var(--text-muted); font-size: 11px; }
```


---

## #flowchart

**Source**: numbered list under "User Flows" (PRD), one diagram per flow.

**Layout**: horizontal box-and-arrow chain, wrapping to a second row at >5 boxes per row. Box width 140 px, height 60 px, gap 30 px.

```javascript
function emitFlowchart(steps) {
  const boxW = 140, boxH = 60, gapX = 30, gapY = 30, perRow = 5;
  const rows = Math.ceil(steps.length / perRow);
  const width = Math.min(perRow, steps.length) * (boxW + gapX) - gapX + 40;
  const height = rows * (boxH + gapY) + 20;
  const out = [];
  steps.forEach((step, i) => {
    const row = Math.floor(i / perRow);
    const col = i % perRow;
    const x = 20 + col * (boxW + gapX);
    const y = 10 + row * (boxH + gapY);
    out.push(`<rect class="node" x="${x}" y="${y}" width="${boxW}" height="${boxH}" rx="6"/>`);
    out.push(`<text x="${x + boxW/2}" y="${y + boxH/2 + 4}" text-anchor="middle">${escapeXml(step.label)}</text>`);
    if (i < steps.length - 1 && col < perRow - 1) {
      // horizontal arrow within row
      const x1 = x + boxW, x2 = x + boxW + gapX, ym = y + boxH/2;
      out.push(`<line class="edge" x1="${x1}" y1="${ym}" x2="${x2}" y2="${ym}" marker-end="url(#arrow)"/>`);
    } else if (i < steps.length - 1) {
      // wrap-down arrow to next row, first column
      // simplified: vertical line then horizontal back
      // for MVP: omit explicit wrap arrow; rely on visual order
    }
  });
  return wrapSvg('flowchart', width, height, out.join(''));
}
```

Long step labels: truncate at ~16 chars; full label in `<title>` for hover tooltip.


---

## #timeline

**Source**: rows of `| Decision | Rationale | Date |` (PRD Decisions Log), sorted ascending by date. If dates are unparseable, sort lexically (still deterministic).

**Layout**: vertical line on the left, circle nodes per decision, date label to the left, decision text + rationale to the right.

```javascript
function emitTimeline(decisions) {
  const rowH = 70, lineX = 110, width = 800;
  const height = decisions.length * rowH + 40;
  const out = [];
  out.push(`<line class="axis" x1="${lineX}" y1="20" x2="${lineX}" y2="${height - 20}"/>`);
  decisions.forEach((d, i) => {
    const cy = 30 + i * rowH;
    out.push(`<text class="label-muted" x="${lineX - 18}" y="${cy + 4}" text-anchor="end">${escapeXml(d.date)}</text>`);
    out.push(`<circle class="node" cx="${lineX}" cy="${cy}" r="6"/>`);
    out.push(`<text x="${lineX + 18}" y="${cy + 4}" font-weight="500">${escapeXml(d.decision)}</text>`);
    if (d.rationale) {
      out.push(`<text class="label-muted" x="${lineX + 18}" y="${cy + 22}">${escapeXml(truncate(d.rationale, 90))}</text>`);
    }
  });
  return wrapSvg('timeline', width, height, out.join(''));
}
```


---

## #list-graph

**Source**: rows of `| Dependency | Purpose | Risk |` (PRD Dependencies). MVP renders as a card grid (no edges — the data doesn't capture inter-dependency relationships).

```html
<div class="dep-grid">
  <div class="dep-card" data-anchor="dep-{{slug}}">
    <h4>{{name}}</h4>
    <p>{{purpose}}</p>
    <span class="risk risk-{{level}}">{{risk text}}</span>
  </div>
</div>
```

```css
.dep-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.75rem; }
.dep-card { background: var(--panel); border: 1px solid var(--border); border-radius: 6px; padding: 0.75rem 1rem; }
.dep-card h4 { margin: 0 0 0.4rem; }
.dep-card p { color: var(--text-muted); font-size: 0.9rem; margin: 0 0 0.5rem; }
.risk { display: inline-block; font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 12px; font-family: var(--mono); }
.risk-low { color: #1a7f37; background: rgba(26, 127, 55, 0.15); }
.risk-medium { color: #bf8700; background: rgba(191, 135, 0, 0.15); }
.risk-high { color: var(--accent-warn); background: rgba(248, 81, 73, 0.15); }
```

Risk-level inference: scan the risk-column text case-insensitively for "low" / "medium" / "high"; default to "medium" if ambiguous.


---

## #tree

**Source**: "Design Space Decomposition" section's compact-list shape:

```
[Feature]
- [Dimension A]: [Option 1] | [Option 2]
- [Dimension B]: [Option X] | [Option Y]
```

**Markers** in option text:
- `← chosen` after an option → render as **chosen** (accent fill, bold text)
- `✗ (pruned)` or any `✗ (...)` annotation → render as **pruned** (muted, strikethrough)

**Layout**: top-down tree. Root = feature; first level = dimensions (one per row); second level = options under each dimension.

```javascript
function parseDesignTree(sectionBody) {
  const lines = sectionBody.split('\n').map(l => l.trim()).filter(Boolean);
  let feature = '';
  const dimensions = [];
  // First non-empty bracketed line is the feature root
  for (const line of lines) {
    const fm = line.match(/^\[([^\]]+)\]\s*$/);
    if (fm && !feature) { feature = fm[1]; continue; }
    const dm = line.match(/^[-*]\s*([^:]+):\s*(.+)$/);
    if (dm) {
      const dimName = dm[1].trim();
      const options = dm[2].split('|').map(opt => {
        const text = opt.trim();
        const chosen = /←\s*chosen/i.test(text);
        const pruned = /✗\s*\(/.test(text);
        const cleanName = text.replace(/←\s*chosen/i, '').replace(/✗\s*\([^)]*\)/, '').trim();
        return { name: cleanName, status: chosen ? 'chosen' : pruned ? 'pruned' : 'normal' };
      });
      dimensions.push({ name: dimName, options });
    }
  }
  return { feature, dimensions };
}

function emitTree({ feature, dimensions }) {
  const rootW = 200, dimW = 180, optW = 150;
  const dimGapX = 20, dimGapY = 50, optGapY = 36;
  const rootY = 20, dimY = 100;
  const totalDims = dimensions.length;
  const totalW = totalDims * (dimW + dimGapX) - dimGapX + 40;
  const maxOpts = Math.max(1, ...dimensions.map(d => d.options.length));
  const height = dimY + 60 + maxOpts * optGapY + 40;
  const cx = totalW / 2;

  const out = [];
  // Root
  out.push(`<rect class="node" x="${cx - rootW/2}" y="${rootY}" width="${rootW}" height="50" rx="8"/>`);
  out.push(`<text x="${cx}" y="${rootY + 30}" text-anchor="middle" font-weight="600">${escapeXml(feature)}</text>`);

  dimensions.forEach((dim, di) => {
    const dx = 20 + di * (dimW + dimGapX);
    const dimCx = dx + dimW / 2;
    // Edge from root
    out.push(`<line class="edge" x1="${cx}" y1="${rootY + 50}" x2="${dimCx}" y2="${dimY}"/>`);
    // Dimension node
    out.push(`<g class="dim-group" data-dim="${di}">`);
    out.push(`<rect class="node" x="${dx}" y="${dimY}" width="${dimW}" height="40" rx="6"/>`);
    out.push(`<text x="${dimCx}" y="${dimY + 25}" text-anchor="middle">${escapeXml(dim.name)}</text>`);
    out.push(`</g>`);
    // Options
    dim.options.forEach((opt, oi) => {
      const oy = dimY + 60 + oi * optGapY;
      const ox = dimCx - optW / 2;
      out.push(`<line class="edge" x1="${dimCx}" y1="${dimY + 40}" x2="${dimCx}" y2="${oy}"/>`);
      const cls = opt.status === 'chosen' ? 'node-chosen' : opt.status === 'pruned' ? 'node-pruned' : '';
      out.push(`<g class="opt-group" data-dim="${di}">`);
      out.push(`<rect class="node ${cls}" x="${ox}" y="${oy}" width="${optW}" height="28" rx="4"/>`);
      const textCls = opt.status === 'pruned' ? 'pruned-text' : '';
      out.push(`<text class="${textCls}" x="${dimCx}" y="${oy + 18}" text-anchor="middle">${escapeXml(opt.name)}</text>`);
      out.push(`</g>`);
    });
  });

  return wrapSvg('tree', totalW, height, out.join(''));
}
```

**Interactivity**: clicking a dimension node toggles `display: none` on its option children.

```javascript
document.querySelectorAll('.diagram-tree .dim-group').forEach(g => {
  g.addEventListener('click', () => {
    const di = g.dataset.dim;
    document.querySelectorAll(`.diagram-tree .opt-group[data-dim="${di}"]`).forEach(o => {
      o.style.display = o.style.display === 'none' ? '' : 'none';
    });
  });
});
```

```css
.diagram-tree .dim-group { cursor: pointer; }
.diagram-tree .pruned-text { text-decoration: line-through; fill: var(--text-muted); }
.diagram-tree .node-chosen + text, .diagram-tree text + .node-chosen { fill: var(--bg); font-weight: 600; }
```


---

## #radar

**Source**: per option, a row of scores from the trade-off scoring matrix; criteria weights (or equal weights as fallback).

**Geometry**: regular polygon with N axes (N = criteria count). Axis length proportional to criterion **weight** so heavier criteria visually dominate. Score on each axis = (score / maxScore) × axis-length.

```javascript
function emitRadar(criteria, scores, weights, maxScore = 5) {
  const W = 320, H = 320;
  const cx = W / 2, cy = H / 2, baseR = 110;
  const N = criteria.length;
  if (N < 3) return ''; // radar undefined for <3 axes

  // Normalize weights so the max weight = 1.0 (so largest axis = baseR)
  const wMax = Math.max(...weights);
  const wNorm = weights.map(w => w / (wMax || 1));

  const axisEnds = criteria.map((_, i) => {
    const angle = (i / N) * 2 * Math.PI - Math.PI / 2;
    const r = wNorm[i] * baseR;
    return {
      x: cx + Math.cos(angle) * r,
      y: cy + Math.sin(angle) * r,
      labelX: cx + Math.cos(angle) * (r + 18),
      labelY: cy + Math.sin(angle) * (r + 18),
      angle, r,
      anchor: Math.cos(angle) > 0.3 ? 'start' : Math.cos(angle) < -0.3 ? 'end' : 'middle'
    };
  });

  const scorePoints = axisEnds.map((end, i) => {
    const ratio = Math.max(0, Math.min(1, (parseFloat(scores[i]) || 0) / maxScore));
    return {
      x: cx + Math.cos(end.angle) * end.r * ratio,
      y: cy + Math.sin(end.angle) * end.r * ratio
    };
  });

  const polyD = scorePoints.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ') + ' Z';

  const out = [];
  // Axis lines
  axisEnds.forEach(end => {
    out.push(`<line class="axis" x1="${cx}" y1="${cy}" x2="${end.x.toFixed(1)}" y2="${end.y.toFixed(1)}"/>`);
  });
  // Polygon
  out.push(`<path class="polygon" d="${polyD}"/>`);
  // Score points
  scorePoints.forEach(p => {
    out.push(`<circle class="point" cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="3"/>`);
  });
  // Axis labels
  axisEnds.forEach((end, i) => {
    out.push(`<text class="axis-label" x="${end.labelX.toFixed(1)}" y="${end.labelY.toFixed(1)}" text-anchor="${end.anchor}">${escapeXml(criteria[i])}</text>`);
  });

  return wrapSvg('radar', W, H, out.join(''));
}
```

```css
.diagram-radar .polygon { fill: var(--accent); fill-opacity: 0.3; stroke: var(--accent); stroke-width: 2; }
.diagram-radar .point { fill: var(--accent); }
.diagram-radar .axis-label { font-size: 10px; fill: var(--text-muted); }
```


---

## Common Pitfalls

- **Negative or NaN coordinates** → clamp with `Math.max(0, ...)` on score ratios; treat unparseable cells as 0 and emit a warning.
- **Empty source section** → if there are zero items, skip the diagram entirely (don't emit empty SVG with a single "no data" message — let the section's text content carry that).
- **Long axis labels overlapping** → truncate to ~14 chars; full label in `<title>`.
- **Date parsing for timeline** → accept `YYYY-MM-DD`. For other formats, fall back to lexical sort. Don't throw.
- **Tree depth >2** → MVP supports root → dimensions → options. Deeper hierarchies aren't expected; if encountered, render the top two levels and emit a "deeper levels truncated" footer text inside the diagram container.
- **N criteria < 3 for radar** → radar is undefined; render a simple bar comparison instead, or skip the diagram and emit an inline note.
- **Determinism** → never use `Math.random()` for layout; always derive coordinates from input data + fixed constants. The same source must produce identical SVG output.
