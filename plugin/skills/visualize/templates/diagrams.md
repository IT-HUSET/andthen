# Diagrams Template

Inline-SVG diagrams generated at HTML emission time. All diagrams use:

- Pure SVG (no `<foreignObject>`, no library dependencies)
- Coordinates computed in the agent at write time, baked into the SVG markup
- Class hooks that key off the page-level CSS variables (`--accent`, `--panel`, etc.)


## Shared Container

Each diagram emitter calls `wrapSvg(type, width, height, body)` to produce the container below – `type` selects the `diagram-{type}` class, `width`/`height` set the `viewBox`, and `body` is substituted for the `<!-- nodes, lines, text -->` slot.

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

**Source**: rows of `| Dependency | Purpose | Risk |` (PRD Dependencies). MVP renders as a card grid (no edges – the data doesn't capture inter-dependency relationships).

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
.risk-low { color: var(--ok); background: var(--ok-soft); }
.risk-medium { color: var(--warn); background: rgba(176, 126, 43, 0.10); }   /* matches --warn rgb on light bg */
.risk-high { color: var(--danger); background: rgba(181, 72, 43, 0.10); }    /* matches --danger rgb on light bg */
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

## #module-map

**Source**: fenced DSL block tagged `mapviz`. Unambiguous to parse, trivial to re-emit verbatim in `View source`, ignored cleanly by other renderers, familiar shape (Mermaid-derived).

````markdown
```mapviz
[CustomerAPI] "REST · /v1/orders"
[OrdersSvc] "core domain" hot
[BillingSvc] "supplier"
[StripeAdapter] "ACL" terminal
{Decision: payment_ok?}

CustomerAPI -> OrdersSvc : "POST order"
OrdersSvc -> BillingSvc : "Customer-Supplier"
OrdersSvc -.-> StripeAdapter : "async webhook"
BillingSvc =success=> Decision
Decision =fail=> StripeAdapter
```
````

**Lexicon**:

- `[Name] "sub-text"` – rectangular component node. Trailing keywords (space-separated):
  - `hot` – clay highlight (active/important node)
  - `terminal` – rounded-rect shape (boundary / external system)
  - `chosen` – accent-fill (decision result)
- `{Name: text?}` – diamond decision node.
- Edges (left node → right node, `: "label"` optional):
  - `->`           gray solid (default sync request/response)
  - `-.->`         dashed clay (async / fan-out)
  - `=success=>`   olive solid (success path)
  - `=fail=>`      rust dashed (failure path)

**Output HTML** wraps a standard Section Block (`id`, `data-anchor`, static affordances per SKILL.md *Section Block* contract). The SVG and its detail-panel aside live inside `.card-body`:

```html
<div class="card-body">
  <p class="diagram-caption">Solid = sync. Dashed clay = async. Olive = success. Rust = failure.</p>
  <svg class="diagram diagram-module-map" viewBox="0 0 {{W}} {{H}}" role="img" aria-label="Module map for {{section}}">
    <defs>
      <marker id="arrow-gray"  viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--text-muted)"/></marker>
      <marker id="arrow-clay"  viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--accent)"/></marker>
      <marker id="arrow-olive" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--ok)"/></marker>
      <marker id="arrow-rust"  viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--danger)"/></marker>
    </defs>
    <g class="node"          data-k="customer-api">…</g>
    <g class="node hot"      data-k="orders-svc">…</g>
    <g class="node term"     data-k="stripe-adapter">…</g>
    <g class="node gate"     data-k="decision-payment-ok"><path class="diamond" d="…"/>…</g>
    <g class="edges">
      <path class="edge"         d="…" marker-end="url(#arrow-gray)"/>
      <path class="edge async"   d="…" marker-end="url(#arrow-clay)"/>
      <path class="edge success" d="…" marker-end="url(#arrow-olive)"/>
      <path class="edge fail"    d="…" marker-end="url(#arrow-rust)"/>
    </g>
  </svg>
  <!-- Paired aside.map-detail (see `templates/js-helpers.md` for the `wireModuleMap` binding contract) -->
  <pre class="src-area" hidden><!-- verbatim mapviz block --></pre>
</div>
```

**SVG layout pseudocode** – follows the determinism rules of every other diagram emitter (no `Math.random()`, output identical from same source):

```
function emitModuleMap(graph):
  ranks = layeredBFS(graph)                 # node.rank = longest-path-from-source
  for node n at (col, row) = position(n):    # within-rank order = source-declared order
    emit shape (rect | rounded-rect | diamond) + label + sub-text
    if n.hot:       add .hot   class
    if n.terminal:  add .term  class
    if n.chosen:    add .chosen class
    annotate g.node data-k = kebab(n.name)
  for edge e:
    pathD = orthogonalRoute(layout, e.from, e.to)
    emit <path class="edge {kind}" marker-end="url(#arrow-{kind || gray})"/>
  return wrappedSvg
```

```css
.diagram-module-map { background: var(--panel); }
.diagram-module-map .node rect      { fill: var(--panel-2); stroke: var(--border); stroke-width: 1.2; }
.diagram-module-map .node text      { fill: var(--text); }
.diagram-module-map .node.hot rect  { stroke: var(--accent); stroke-width: 2; fill: var(--accent-soft); }
.diagram-module-map .node.term rect { rx: 14; stroke-dasharray: 4 3; }
.diagram-module-map .node.chosen rect { fill: var(--accent); }
.diagram-module-map .node.chosen text { fill: var(--bg); font-weight: 600; }
.diagram-module-map .node.gate .diamond { fill: var(--panel-2); stroke: var(--warn); stroke-width: 1.5; }
.diagram-module-map .node.active rect,
.diagram-module-map .node.active .diamond { stroke: var(--accent); stroke-width: 2.5; filter: drop-shadow(0 0 0 var(--accent)); }
.diagram-module-map .node[data-k] { cursor: pointer; }
.diagram-module-map .edge         { fill: none; stroke: var(--text-muted); stroke-width: 1.2; }
.diagram-module-map .edge.async   { stroke: var(--accent); stroke-dasharray: 5 4; }
.diagram-module-map .edge.success { stroke: var(--ok); }
.diagram-module-map .edge.fail    { stroke: var(--danger); stroke-dasharray: 5 4; }
.diagram-caption { font-size: 0.78rem; color: var(--text-muted); margin: 0 0 0.6rem; }

.map-detail { background: var(--panel-2); border: 1px solid var(--border-soft); border-radius: var(--radius-sm);
              padding: 0.8rem 1rem; margin-top: 0.8rem; }
.map-detail .hint { font-size: 0.75rem; color: var(--text-faint); font-family: var(--mono); margin-bottom: 0.5rem; }
.map-detail .md-title { margin: 0 0 0.35rem; font-size: 1rem; color: var(--accent); }
.map-detail .md-meta  { font-family: var(--mono); font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.4rem; }
.map-detail .md-body  { color: var(--text); font-size: 0.92rem; line-height: 1.5; white-space: pre-line; }
```

**Empty-graph mitigation:** if the parsed `mapviz` block yields zero nodes (parse failure or empty body), fall back to Generic Prose for the section AND emit the verbatim DSL block inside a `<pre>` so the reviewer can see what was authored. Same shape as the existing `## Common Pitfalls` rule "*Empty source section → if there are zero items, skip the diagram entirely*."

**Detail-panel aside** (Phase 3.4 contract). The paired aside is rendered statically with a default-selected node so JS-disabled environments still see *some* content. All artifact-derived values use context-appropriate escaping: `id`, `data-default-node`, and SVG `data-k` values are HTML-attribute escaped; static title/meta/body placeholders are HTML text escaped; detail JSON is written as inert `<script type="application/json">` text with `<` escaped as `\u003c` so `</script>` cannot terminate the block. Node detail bodies are escaped text with preserved line breaks, not trusted HTML. See `wireModuleMap` in `templates/js-helpers.md`.

```html
<aside class="map-detail" id="map-detail-{{section-anchor-attr}}" data-default-node="{{first-node-key-attr}}">
  <div class="hint">Click a node in the diagram →</div>
  <div class="map-detail-body">
    <h3 class="md-title" data-role="title">{{DEFAULT_NODE_TITLE_ESCAPED_TEXT}}</h3>
    <div class="md-meta" data-role="meta">{{DEFAULT_NODE_META_ESCAPED_TEXT}}</div>
    <div class="md-body" data-role="body">{{DEFAULT_NODE_BODY_ESCAPED_TEXT}}</div>
  </div>
  <script type="application/json" data-role="nodes">{{DETAIL_DICT_JSON_ESCAPED_TEXT}}</script>
</aside>
```


---


## #walkthrough

**Source trigger** (per the SKILL.md cross-artifact dispatch table):
- PRD User Flows: 2–9 H3 substeps where **every** substep's stripped body char-count ≥ 50 (see `prd.md#User Flows` for the stripping rule)
- Trade-off Options: **every** option's H3 body carries ≥ 2 of `What changes` / `Where it changes` / `Risk` / `Trade-off` H4 substring (all-or-nothing per section – see `tradeoff.md#Options`)
- Clarification Resolved Decisions: ≤ 5 rows AND every Rationale's stripped char-count ≥ 60

**Layout**: vertical list of numbered steps. Each step: 34 px clay/oat circular badge, optional file-path mono line (when the first paragraph under the H3 is a single inline-code reference like `` `src/middleware/auth.ts`:14-31 ``), 2–3 sentences of prose, optional `<details class="snippet">` collapsible source listing. The one-at-a-time toggle (`templates/js-helpers.md`) closes other open snippets in the same `.walk` container.

```html
<div class="walk">
  <div class="step" data-step="1">  <!-- add .hot class when source has `_priority: hot_` or `<!-- hot -->` marker -->
    <div class="badge">1</div>
    <div class="step-body">
      <div class="step-loc"><code>{{file path}}</code><span class="range">{{:N-M}}</span></div>
      <p>{{prose paragraph(s)}}</p>
      <details class="snippet">
        <summary>show source</summary>
        <pre class="code">{{verbatim code}}</pre>
      </details>
    </div>
  </div>
  <!-- more steps … -->
</div>
```

```css
.walk { display: flex; flex-direction: column; gap: 0.85rem; margin: 0.5rem 0; }
.walk .step { display: grid; grid-template-columns: 34px minmax(0, 1fr); gap: 0.85rem; align-items: start; }
.walk .badge { width: 34px; height: 34px; border-radius: 999px;
               background: var(--panel-3); color: var(--text-muted);
               font-family: var(--mono); font-size: 0.85rem; font-weight: 700;
               display: inline-flex; align-items: center; justify-content: center; }
.walk .step.hot .badge { background: var(--accent); color: var(--bg); }
.walk .step-body { min-width: 0; }
.walk .step-loc { font-family: var(--mono); font-size: 0.78rem; color: var(--text-muted); margin-bottom: 0.3rem; }
.walk .step-loc code { background: var(--panel-2); padding: 0.1rem 0.35rem; border-radius: 4px; }
.walk .step-loc .range { color: var(--text-faint); margin-left: 0.3rem; }
.walk .snippet { margin-top: 0.5rem; }
.walk .snippet > summary { cursor: pointer; font-family: var(--mono); font-size: 0.78rem;
                            color: var(--text-muted); list-style: none; padding: 0.2rem 0; }
.walk .snippet > summary::before { content: '▸ '; color: var(--accent); }
.walk .snippet[open] > summary::before { content: '▾ '; }
.walk .snippet pre.code { background: var(--panel-2); border: 1px solid var(--border-soft);
                          border-radius: var(--radius-sm); padding: 0.7rem 0.9rem; overflow-x: auto;
                          font-size: 0.82rem; line-height: 1.45; margin: 0.3rem 0 0; }
```

**Section-dedup:** the walkthrough renderer consumes the line range from the first H3 substep to the last H3 substep's last child block. Generic Prose fallback must skip those lines (existing Renderer Discipline section-dedup mechanism).


---


## Common Pitfalls

- **Negative or NaN coordinates** → clamp with `Math.max(0, ...)` on score ratios; treat unparseable cells as 0 and emit a warning.
- **Empty source section** → if there are zero items, skip the diagram entirely (don't emit empty SVG with a single "no data" message – let the section's text content carry that).
- **Long axis labels overlapping** → truncate to ~14 chars; full label in `<title>`.
- **Date parsing for timeline** → accept `YYYY-MM-DD`. For other formats, fall back to lexical sort. Don't throw.
- **Tree depth >2** → MVP supports root → dimensions → options. Deeper hierarchies aren't expected; if encountered, render the top two levels and emit a "deeper levels truncated" footer text inside the diagram container.
- **N criteria < 3 for radar** → radar is undefined; render a simple bar comparison instead, or skip the diagram and emit an inline note.
- **Empty `mapviz` block** → falls back to Generic Prose + verbatim `<pre>` in `.card-body` (see `#module-map` empty-graph mitigation). Never emit an empty SVG shell – it reads as a broken diagram.
- **Walkthrough `<details>` interfering with `View source`** → the one-at-a-time toggle in the `templates/js-helpers.md` is scoped to `.walk details.snippet`, **never** bare `details`. A bare-`details` listener would close the section's `.src-area` source panel whenever a snippet opens.
- **Module-map detail JSON in an HTML attribute** → don't put the node dictionary in `data-nodes`. Attribute JSON is fragile because quote-bearing artifact text can break the attribute before JS parses it. Use the paired `script[type="application/json"][data-role="nodes"]` block and escape `<` as `\u003c` in the JSON text.
- **Module-map detail XSS** → node keys, title, meta, and body values are artifact-derived content and must render through attribute escaping, text escaping, or `textContent` only. Do not use `innerHTML` unless a strict sanitizer is added first.
- **Determinism** → never use `Math.random()` for layout; always derive coordinates from input data + fixed constants. The same source must produce identical SVG output.
