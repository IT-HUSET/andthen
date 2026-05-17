# Strategic-Design Template

Use when the source is an architecture strategic-design report from `andthen:architecture --mode strategic-design`. Detection (per SKILL.md): H1 contains "Strategic Design" / "Strategic-Design", **or** H2 set contains both "Subdomains" and "Context Map" (case-insensitive). Type-detection orders this before `tradeoff` so the more-specific marker pair wins under first-match-wins.

The report frames an event-stormed / DDD-aware view of the system: bounded contexts, subdomains, context map (relationships between contexts), and supporting prose. The visualization centerpiece is the **module map** (`#module-map` in `diagrams.md`) – a static + interactive SVG showing named components and their relationships.


## Layout

```
+-------------------------------------------------------------+
| andthen:visualize · Strategic Design · <basename>  [ Copy ] |
+-------------------------------------------------------------+
| eyebrow + serif H1 + status pill row                        |
| [ KPI band: Bounded Contexts · Subdomains · Relationships   |
|                                          · Open Issues ]    |
| [ Where-to-focus band (omitted if <2 priority items) ]      |
+-------------------------------------------------------------+
| ## Executive Summary  / How to Read this Report             |
| [ Generic prose ]                              [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Context Map                                              |
| [ Module Map (mapviz) + paired aside.map-detail panel ]     |
|                                                [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Bounded Contexts                                         |
| [ Per-context Module Map(s) OR card grid ]    [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Subdomains                                               |
| [ Card grid (reuse list-graph styling) ]      [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Open Issues / Risks / Next Steps                         |
| [ Generic prose + Risk-map chips above ]      [ Note ] [ <> ]|
+-------------------------------------------------------------+
```


## KPI Cells

The four-cell `.kpi-band` (rendered per the SKILL.md *KPI Summary Band* contract) sits between `.doc-header` and the first section. Strategic-design cells in source order:

| Cell | Label | Source |
|---|---|---|
| 1 | Bounded Contexts | Precedence: if a `mapviz` block exists in `## Context Map`, count its `[Name]` nodes. Else fall back to the count of H3 subsections under `## Bounded Contexts`. Never sum the two |
| 2 | Subdomains | Count = H3 subsections under `## Subdomains` PLUS top-level list items that are **not** inside any H3 body. Both shapes contribute; a mixed source (some H3s + some flat bullets) gets the full count, not silently undercounted to one shape |
| 3 | Relationships | Count of edges in the Context Map mapviz block (0 if no block) |
| 4 | Open Issues | Sum of `<li>` elements rendered in the body of `## Open Issues`, `## Risks`, and `## Next Steps` — counting every list item regardless of whether it sits directly under the H2 or inside an H3 body. These three sections are non-overlapping; the sum is intentional and deterministic |

Auto-`.attention`: cell 4 when count > 0.


## Section Renderers

Each H2 dispatches to **one** renderer per the SKILL.md cross-artifact dispatch table; Generic Prose is the fallback. Section Block wrapper (id + data-anchor + static affordances) is universal.

### Context Map → Module Map + interactive node panel

If the section body contains a fenced `mapviz` block → render via `diagrams.md#module-map`, paired with the static `aside.map-detail` panel. The `wireModuleMap` helper (`templates/js-helpers.md`) binds node-clicks to the panel; the module-map JSON script discipline applies (paired `<script type="application/json" data-role="nodes">` block, never artifact-derived JSON inside an HTML attribute).

**Paired-H3 detail convention** – each `[NodeName]` declared in the `mapviz` block may have a matching H3 in the same section body whose heading text equals the node label (case-insensitive, after stripping `[]`). The paired H3's body becomes the node's detail-panel content:

````markdown
## Context Map

```mapviz
[CustomerAPI] "REST · /v1/orders"
[OrdersSvc] "core domain" hot
[BillingSvc] "supplier"
```

### CustomerAPI

The public ingress edge. Handles auth, request shaping, and rate limiting before
forwarding to OrdersSvc.

`packages/api-gateway/src/server.ts`

### OrdersSvc

The order-domain service. Owns the lifecycle of an order from creation through
fulfillment. Holds the only writes to the orders table.

`packages/orders/src/index.ts`
````

The renderer serializes the paired-H3 dictionary into a paired `<script type="application/json" data-role="nodes">` block adjacent to the `aside.map-detail`, with `<` escaped as `\u003c` in the JSON text so a value containing `</script>` cannot terminate the block; title, meta, and body values are rendered as text (never `innerHTML`) per the `templates/diagrams.md` and `templates/js-helpers.md` discipline. The default-selected node is the first one declared in the DSL – the panel is never empty. A node without a paired H3 emits `<!-- module-map: no detail for node "X" -->` adjacent to the diagram so the gap surfaces in `View source`; clicking that node activates it in the SVG but leaves the panel content unchanged (early-return in `wireModuleMap`).

If no `mapviz` block is present → fall back to Generic Prose. The Context Map H2 still renders with full Section Block affordances.

### Bounded Contexts → per-context module map · card grid

If each H3 under `## Bounded Contexts` contains its own `mapviz` block → render one Module Map per context (each its own SVG + paired aside). Otherwise → card grid (one card per context with name + one-line description; reuse `diagrams.md#list-graph` styling).

### Subdomains → card grid

Render as a card grid (one card per H3 / list item under `## Subdomains`). Reuse `diagrams.md#list-graph` card styling. Per-subdomain classification (core / supporting / generic) maps to color: core → `--accent` border, supporting → default, generic → muted.

### Open Issues / Risks / Next Steps → Risk-map chips + Generic Prose

Above the list emit `<nav class="risk-map">` chips (SKILL.md *Risk-map chips* contract): unresolved → `.attention`, mitigated → `.medium`, resolved → `.safe`. Below the chips render Generic Prose.

### (anything else) → Generic Prose

Render markdown as-is. Standard Section Block affordances apply.


## Pre-population

1. Read the source markdown.
2. Parse into H2-anchored sections per the SKILL.md anchor scheme.
3. For each section, dispatch to a renderer above (case-insensitive substring match on H2 text, then schema detection per the SKILL.md cross-artifact dispatch table).
4. Sections without a specialized renderer fall back to Generic Prose.
5. Wrap every rendered section in the standard `<section class="card" id="{{anchor}}">` block from the SKILL.md Section Block contract.


## Edge Cases

- **Empty / malformed `mapviz` block** → fall back to Generic Prose + emit verbatim DSL inside a `<pre>`. Per `diagrams.md#module-map` empty-graph mitigation.
- **No `## Context Map` H2 at all** → no module map renders; document still detected as strategic-design via the Subdomains+Context-Map marker pair (the H1 marker alone is enough if both H2s are absent).
- **Node without paired H3** → static diagram still renders; the unpaired node's click activates the SVG but the detail panel keeps its previous selection. View-source surfaces the gap via the emission-time HTML comment.
- **DDD relationship vocabulary in edge labels** – recognized terms (`Customer-Supplier`, `Anti-Corruption Layer`, `Open Host`, `Published Language`, `Partnership`, `Shared Kernel`, `Separate Ways`, `Conformist`) are annotated, not parsed for layout. Convention: `Separate Ways` → dashed edge style; `Anti-Corruption Layer` target node → `terminal` keyword.


## Example Use Cases

- Reviewing a strategic-design report before chaining into `andthen:architecture --mode fitness` (formalize) or `--mode decompose` (contested boundary)
- Verifying context-map relationships against an event-stormed snapshot
- Exporting review notes for `andthen:architecture --mode strategic-design` refinement
