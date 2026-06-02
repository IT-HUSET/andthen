# Decompose Template

Use when the source is an architecture **decompose** report from the `andthen:architecture` skill in `--mode decompose`. Detection: H1 or H2 contains "Decompose" / "Decomposition Analysis" (case-insensitive); OR H2 set contains BOTH ("Driver Scores" OR "Boundary Map") AND "Recommendation" AND **no scoring-matrix table** (the scoring-matrix exclusion disambiguates from trade-off; decompose uses driver tables instead).

Decompose reports evaluate a split/merge decision with Ford/Richards driver scoring, connascence analysis, and a verdict from `Split | Merge | Keep | Defer`. The visualization optimizes for "what are the drivers saying, and does the recommendation pass the 4-criteria check".


## Contents

- Layout
- Document Header
- KPI Cells
- Section Renderers
- Where-to-Focus Inputs
- Edge Cases
- Example Use Cases


## Layout

```
+-------------------------------------------------------------+
| andthen:visualize · Decompose · <basename>         [ Copy ] |
+-------------------------------------------------------------+
| eyebrow + serif H1 + status pill row                        |
| [ KPI band: Coupling Points · Strong Drivers · Risk · Verdict ]|
| [ Where-to-focus band (dynamic connascence + dealbreakers)  ]|
+-------------------------------------------------------------+
| ## Executive Summary  /  ## How to Read This Report         |
| [ Generic prose + verdict TL;DR callout ]      [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Boundary Map                                             |
| [ Coupling-point cards or mapviz when present ][ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Driver Scores (disintegration + integration)             |
| [ Two-radar pair + driver-score table ]        [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Connascence Analysis                                     |
| [ Per-boundary connascence cards ]             [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Consumer Analysis  (when targeting a library/SDK)        |
| [ Consumer-profile cards with waste % ]        [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Evaluation Matrix                                        |
| [ 4-criteria checklist (a/b/c/d) ]             [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Recommendation                                           |
| [ Verdict accent box + confidence + triggers ]              |
|                                                [ Note ] [ <> ]|
+-------------------------------------------------------------+
```


## Document Header

The verdict is the report's centerpiece. Parse the **Recommendation** section's first line (typically `**Recommendation**: Split`) to drive the status pill:

| Verdict | Status class |
|---|---|
| `Split` | `status-review` (clay coral – action recommended) |
| `Merge` | `status-review` (clay coral) |
| `Keep` | `status-approved` (olive – status quo accepted) |
| `Defer` | `status-deferred` (gray) |
| unparseable | plain `.meta-pill` |

Also surface **Confidence** (High / Medium / Low) as an extra `.meta-pill` with `k="confidence"`.


## KPI Cells

| Cell | Label | Source |
|---|---|---|
| 1 | Coupling Points | Count of items under `## Boundary Map` (bullets, table rows, or mapviz edges – whichever shape the source uses) |
| 2 | Strong Drivers | Count of drivers under `## Driver Scores` rated `Strong` (case-insensitive). Sum across disintegration + integration tables |
| 3 | Risk | Recommendation's risk-level prose – `Low` / `Medium` / `High` (a line in the recommendation body starting with one of those words, case-insensitive; or "—") |
| 4 | Verdict | The `Split` / `Merge` / `Keep` / `Defer` string – truncated to 16 chars; "—" when no verdict |

Auto-`.attention`: cell 3 when value starts with `high` (case-insensitive).


## Section Renderers

### Boundary Map → Coupling-point cards or mapviz

If the section body contains a fenced `mapviz` block → render via `diagrams.md#module-map` with paired detail panel (reuse the strategic-design renderer; the panel binds via `wireModuleMap`).

Otherwise, render as coupling-point cards – one card per cross-boundary point (function call, shared type, event, configuration, etc.).

```html
<article class="dc-coupling" data-anchor-parent="boundary-map">
  <header class="dc-coupling-head">
    <span class="dc-kind">function call</span>
    <h3>OrderService.allocateInventory → InventoryService.reserveStock</h3>
  </header>
  <p class="dc-coupling-body">{{description: shared types, locking semantics, transactional scope}}</p>
</article>
```

```css
.dc-coupling-list { display: flex; flex-direction: column; gap: 0.55rem; }
.dc-coupling { background: var(--panel); border: 1px solid var(--border-soft);
               border-radius: var(--radius-sm); padding: 0.65rem 0.9rem; }
.dc-coupling-head { display: flex; align-items: baseline; gap: 0.55rem; margin-bottom: 0.3rem; }
.dc-coupling-head h3 { flex: 1; margin: 0; font-family: var(--ui); font-size: 0.92rem;
                       font-weight: 600; font-family: var(--mono); color: var(--text); }
.dc-kind { font-family: var(--mono); font-size: 0.72rem; color: var(--accent);
           background: var(--accent-soft); padding: 0.1rem 0.45rem; border-radius: 999px; }
.dc-coupling-body { margin: 0; color: var(--text-muted); font-size: 0.88rem; }
```

### Driver Scores → Two-radar pair + driver-score table

The headline section. Ford/Richards has **6 disintegration drivers** and **4 integration drivers**, each scored Strong / Moderate / Weak / N/A with evidence.

Render two radars side-by-side: one for disintegration drivers (6 axes), one for integration drivers (4 axes). Use the `diagrams.md#radar` emitter; map qualitative scores to numerics: `Strong=3, Moderate=2, Weak=1, N/A=0`.

```html
<div class="dc-radars">
  <div class="dc-radar-pair">
    <h3 class="dc-radar-title">Disintegration drivers</h3>
    <svg class="diagram diagram-radar"><!-- 6 axes per Ford/Richards --></svg>
  </div>
  <div class="dc-radar-pair">
    <h3 class="dc-radar-title">Integration drivers</h3>
    <svg class="diagram diagram-radar"><!-- 4 axes per Ford/Richards --></svg>
  </div>
</div>
<table class="dc-driver-table">
  <thead><tr><th>Driver</th><th>Type</th><th>Score</th><th>Evidence</th></tr></thead>
  <tbody>
    <tr data-score="strong"><td>Service scope &amp; function</td><td>disintegration</td><td><span class="dc-score s-strong">Strong</span></td><td>{{evidence}}</td></tr>
  </tbody>
</table>
```

```css
.dc-radars { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 0.9rem; }
.dc-radar-title { margin: 0 0 0.4rem; font-family: var(--mono); font-size: 0.74rem;
                  color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.dc-driver-table { width: 100%; border-collapse: collapse; }
.dc-driver-table th { background: var(--panel-2); text-align: left; padding: 0.45rem 0.6rem;
                      font-family: var(--mono); font-size: 0.72rem; color: var(--text-muted);
                      border-bottom: 1px solid var(--border); }
.dc-driver-table td { padding: 0.45rem 0.6rem; border-bottom: 1px solid var(--border-soft);
                      font-size: 0.88rem; }
.dc-score { font-family: var(--mono); font-size: 0.72rem; font-weight: 700;
            padding: 0.1rem 0.5rem; border-radius: var(--radius-sm); color: #FAF9F5; }
.dc-score.s-strong   { background: var(--accent); }
.dc-score.s-moderate { background: var(--warn); }
.dc-score.s-weak     { background: var(--ok); }
.dc-score.s-na       { background: var(--text-faint); color: var(--text); }
@media (max-width: 760px) { .dc-radars { grid-template-columns: 1fr; } }
```

When the source uses fewer than the canonical 6+4 drivers (rare), render the radars with whatever axes are present and add a muted callout: "N drivers scored (canonical: 6 disintegration + 4 integration)".

### Connascence Analysis → Per-boundary connascence cards

One card per top coupling point. Each card lists the connascence type (CoN/CoT/CoM/CoP/CoA/CoE/CoTm/CoV/CoI), strength, degree, locality, and computed severity.

```html
<article class="dc-connascence" data-anchor-parent="connascence-analysis" data-locality="cross-boundary" data-kind="dynamic">
  <header class="dc-con-head">
    <span class="dc-con-type">CoV</span>
    <span class="dc-con-kind dynamic">dynamic</span>
    <h3>Shared price-currency invariant</h3>
    <span class="dc-con-severity sev-critical">CRITICAL</span>
  </header>
  <dl class="dc-con-fields">
    <dt>Strength</dt><dd>3</dd>
    <dt>Degree</dt><dd>2</dd>
    <dt>Locality</dt><dd>cross-boundary</dd>
    <dt>Severity</dt><dd>18 (CRITICAL)</dd>
  </dl>
</article>
```

```css
.dc-con-list { display: flex; flex-direction: column; gap: 0.55rem; }
.dc-connascence { background: var(--panel); border: 1px solid var(--border-soft);
                  border-radius: var(--radius-sm); padding: 0.7rem 0.9rem; }
.dc-connascence[data-kind="dynamic"] { border-left: 3px solid var(--danger); }
.dc-connascence[data-kind="static"]  { border-left: 3px solid var(--accent); }
.dc-con-head { display: flex; align-items: baseline; gap: 0.55rem; margin-bottom: 0.35rem; }
.dc-con-type { font-family: var(--mono); font-size: 0.78rem; font-weight: 700;
               background: var(--panel-3); color: var(--text-muted);
               padding: 0.15rem 0.55rem; border-radius: var(--radius-sm); }
.dc-con-kind { font-family: var(--mono); font-size: 0.7rem; padding: 0.1rem 0.4rem;
               border-radius: 999px; }
.dc-con-kind.dynamic { background: var(--danger); color: #FAF9F5; }
.dc-con-kind.static { background: var(--accent-soft); color: var(--accent); }
.dc-con-head h3 { flex: 1; margin: 0; font-family: var(--ui); font-size: 0.95rem; font-weight: 600; }
.dc-con-severity { font-family: var(--mono); font-size: 0.72rem; font-weight: 700;
                   padding: 0.1rem 0.5rem; border-radius: 999px; color: #FAF9F5; }
.dc-con-severity.sev-critical { background: var(--danger); }
.dc-con-severity.sev-high     { background: var(--accent); }
.dc-con-severity.sev-medium   { background: var(--warn); }
.dc-con-severity.sev-low      { background: var(--ok); }
.dc-con-fields dt { font-family: var(--mono); font-size: 0.7rem; color: var(--text-muted);
                    text-transform: uppercase; letter-spacing: 0.05em; }
.dc-con-fields dd { margin: 0.1rem 0 0.3rem; font-size: 0.88rem; color: var(--text); }
```

**Dynamic connascence crossing a package boundary always reads as HIGH or CRITICAL** per the architecture skill; if a card has `data-kind="dynamic" data-locality="cross-boundary"` and a lower severity, emit `<!-- decompose: dynamic cross-boundary CoX but severity Y -->` in `View source` so the gap surfaces.

### Consumer Analysis → Consumer-profile cards (when present)

One card per consumer profile (3-5 typical). Show profile name, forced-dependency waste percentage, and the one-line use case.

```css
.dc-consumer { background: var(--panel); border: 1px solid var(--border-soft);
               border-radius: var(--radius-sm); padding: 0.65rem 0.9rem; margin-bottom: 0.5rem; }
.dc-consumer-name { font-weight: 600; }
.dc-consumer-waste { font-family: var(--mono); font-size: 0.78rem; color: var(--accent); }
```

Section is **optional** – omit when the source has no `## Consumer Analysis` heading (typical when the boundary isn't a library/SDK).

### Evaluation Matrix → 4-criteria checklist

The mode reference defines four criteria: (a) zero external deps, (b) independent consumer use case, (c) acyclic DAG post-split, (d) low breaking-change cost. Render as a 4-row checklist with each row showing PASS/FAIL.

```html
<ol class="dc-eval-list">
  <li class="dc-eval-row" data-result="pass">
    <span class="dc-eval-letter">a</span>
    <span class="dc-eval-question">Zero external dependencies?</span>
    <span class="dc-eval-status pass">PASS</span>
  </li>
  <!-- b, c, d … -->
</ol>
<p class="dc-eval-summary">Splits require <strong>a+b+c</strong> to pass.</p>
```

```css
.dc-eval-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.35rem; }
.dc-eval-row { display: grid; grid-template-columns: 24px minmax(0, 1fr) 60px; gap: 0.6rem;
               align-items: baseline; padding: 0.45rem 0.6rem;
               background: var(--panel); border: 1px solid var(--border-soft);
               border-radius: var(--radius-sm); }
.dc-eval-row[data-result="pass"] { border-left: 3px solid var(--ok); }
.dc-eval-row[data-result="fail"] { border-left: 3px solid var(--danger); }
.dc-eval-letter { font-family: var(--mono); font-size: 0.78rem; font-weight: 700;
                  color: var(--text-muted); }
.dc-eval-status { font-family: var(--mono); font-size: 0.72rem; font-weight: 700;
                  text-align: right; }
.dc-eval-status.pass { color: var(--ok); }
.dc-eval-status.fail { color: var(--danger); }
.dc-eval-summary { margin: 0.5rem 0 0; font-size: 0.85rem; color: var(--text-muted); }
```

### Recommendation → Verdict accent box + confidence + triggers

Reuse `tradeoff.md` `.recommendation` styling, with two additions:

- **Verdict header** – render the `Split / Merge / Keep / Defer` verdict as a large chip with the matching status color.
- **Decomposition triggers** – when the source's "specific conditions for revisiting deferred decisions" body lists triggers (typical for `Defer`), render them as a numbered list with `decomposition trigger` mono labels.

```css
.dc-rec-verdict { display: inline-flex; align-items: center; padding: 0.3rem 0.8rem;
                  border-radius: var(--radius-sm); font-family: var(--mono); font-weight: 700;
                  font-size: 0.92rem; }
.dc-rec-verdict.v-split, .dc-rec-verdict.v-merge { background: var(--accent); color: #FAF9F5; }
.dc-rec-verdict.v-keep { background: var(--ok); color: #FAF9F5; }
.dc-rec-verdict.v-defer { background: var(--text-faint); color: var(--text); }
.dc-triggers { margin-top: 0.6rem; }
.dc-triggers li { margin-bottom: 0.3rem; }
.dc-triggers li::marker { color: var(--accent); }
```


## Where-to-Focus Inputs

1. **Dynamic connascence cards with `cross-boundary` locality** (CoE/CoTm/CoV/CoI crossing the proposed split line) – always anchor first; "Dynamic cross-boundary connascence: <type> on <coupling>".
2. **Failed evaluation criteria** – any `data-result="fail"` row in the Evaluation Matrix → "Evaluation gate failed: criterion <letter>".
3. **`Defer` verdict with a single decomposition trigger** – "Deferred until: <trigger>" so the reviewer can validate the condition is observable.
4. **High Risk** in the recommendation → "High risk: <rationale span>".


## Edge Cases

- **No coupling points listed** (rare; trivial boundary) → render `## Boundary Map` as Generic Prose with a muted callout "no significant cross-boundary coupling detected".
- **Driver tables with mixed N/A and Strong** → radars still emit; N/A axes draw at 0 (origin) and the diagram emitter must handle the all-zero degenerate case (collapse to a single point with a muted "no drivers scored" overlay).
- **`Defer` verdict with no triggers** → emit `<!-- decompose: defer without triggers → revisit condition undefined -->` in `View source` and render the recommendation accent box with a muted "no revisit triggers specified" footer.
- **Library/SDK target but no Consumer Analysis** → emit `<!-- decompose: library target but consumer analysis missing -->` in `View source`; surface the gap as a Where-to-Focus entry.


## Example Use Cases

- **Architect** – review driver radars at a glance to spot disintegration/integration imbalance, then dig into Connascence Analysis for the highest-cost coupling points.
- **Tech lead** – inspect the Evaluation Matrix to verify all required gates pass before action; copy notes for the design-doc follow-up.
