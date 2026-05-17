# Fitness Functions Template

Use when the source is an architecture **fitness-functions** report from the `andthen:architecture` skill in `--mode fitness`. Detection: H1 or H2 contains "Fitness Functions" / "Fitness Function" (case-insensitive); OR H2 set contains BOTH "Proposed Fitness Functions" AND ("Governance" OR "ADR Gap Analysis").

Fitness reports propose automated architectural-governance checks across the **4-level governance stack** (commit / PR / nightly / production). The visualization optimizes for "which checks live where, and which ADR gaps drive them".


## Layout

```
+-------------------------------------------------------------+
| andthen:visualize · Fitness · <basename>           [ Copy ] |
+-------------------------------------------------------------+
| eyebrow + serif H1 + status pill row                        |
| [ KPI band: Proposed · ADR Gaps · Critical · Coverage % ]   |
| [ Where-to-focus band (ADR gaps + L1/L2 proposals first) ]  |
+-------------------------------------------------------------+
| ## Executive Summary  /  ## How to Read This Report         |
| [ Generic prose ]                              [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Current Governance Coverage                              |
| [ Coverage table grouped by level ]            [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## ADR Gap Analysis                                         |
| [ ADR cards with gap chips ]                   [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Proposed Fitness Functions                               |
| [ Per-level lanes (L1..L4) with proposal cards ]            |
|                                                [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Prioritized Implementation Roadmap                       |
| [ Numbered walkthrough – starter 3 + growth path ]          |
|                                                [ Note ] [ <> ]|
+-------------------------------------------------------------+
```


## KPI Cells

| Cell | Label | Source |
|---|---|---|
| 1 | Proposed | Count of proposal cards under `## Proposed Fitness Functions` (sum across all governance levels) |
| 2 | ADR Gaps | Count of ADRs in `## ADR Gap Analysis` whose status is `no enforcement` / `gap` (or equivalent) |
| 3 | Critical | Count of proposals with `Severity: CRITICAL` (case-insensitive, when severity is declared in the proposal body) |
| 4 | Coverage % | Source's `Current Governance Coverage` percentage when present (e.g. "L1: 60%"); rendered as a single label (e.g. "60% L1") or "—" when not present in source |

Auto-`.attention`: cell 2 when count > 0; cell 3 when count > 0.


## Section Renderers

### Current Governance Coverage → Coverage table grouped by level

The source typically describes existing CI checks, lint rules, and tests organized by governance level. Render as a 4-row table (one row per level) with a coverage chip + body cell per row.

```html
<table class="fitness-coverage">
  <thead><tr><th>Level</th><th>Coverage</th><th>Existing checks</th></tr></thead>
  <tbody>
    <tr data-level="1"><td><span class="fl-chip fl-1">L1 commit</span></td><td><code>60%</code></td><td>lint, prettier, type-check</td></tr>
    <tr data-level="2"><td><span class="fl-chip fl-2">L2 PR</span></td><td><code>30%</code></td><td>unit tests; no arch tests</td></tr>
    <tr data-level="3"><td><span class="fl-chip fl-3">L3 nightly</span></td><td><code>0%</code></td><td>none</td></tr>
    <tr data-level="4"><td><span class="fl-chip fl-4">L4 prod</span></td><td><code>—</code></td><td>none</td></tr>
  </tbody>
</table>
```

```css
.fitness-coverage { width: 100%; border-collapse: collapse; }
.fitness-coverage th { background: var(--panel-2); text-align: left; padding: 0.5rem 0.7rem;
                       font-family: var(--mono); font-size: 0.74rem; color: var(--text-muted);
                       border-bottom: 1px solid var(--border); }
.fitness-coverage td { padding: 0.5rem 0.7rem; border-bottom: 1px solid var(--border-soft); }
.fl-chip { font-family: var(--mono); font-size: 0.72rem; font-weight: 700; padding: 0.1rem 0.5rem;
           border-radius: var(--radius-sm); color: #FAF9F5; }
.fl-1 { background: var(--ok); }                  /* fast, every commit – olive */
.fl-2 { background: var(--accent); }              /* per PR – clay */
.fl-3 { background: var(--warn); }                /* nightly – amber */
.fl-4 { background: var(--text-muted); }          /* production – muted */
```

When the source structures coverage differently (e.g. prose only, no per-level breakdown), fall back to Generic Prose.

### ADR Gap Analysis → ADR cards with gap chips

One card per ADR referenced. Parse ADR reference (`ADR-NNN: Title`), current enforcement status, and the gap description.

```html
<article class="fitness-adr-card" data-gap="open">
  <header class="fa-head">
    <span class="fa-adr"><code>ADR-007</code></span>
    <h3>Adopt event-sourcing for order context</h3>
    <span class="fa-gap-chip gap-open">No enforcement</span>
  </header>
  <p class="fa-body">{{description of how the ADR is currently unenforced}}</p>
  <p class="fa-proposal">Proposes: <a href="#proposed-fitness-functions-fn-3">FF-3</a>, <a href="#proposed-fitness-functions-fn-7">FF-7</a></p>
</article>
```

```css
.fitness-adr-list { display: flex; flex-direction: column; gap: 0.55rem; }
.fitness-adr-card { background: var(--panel); border: 1px solid var(--border-soft);
                    border-left: 3px solid var(--accent); border-radius: var(--radius-sm);
                    padding: 0.7rem 0.9rem; }
.fitness-adr-card[data-gap="open"] { border-left-color: var(--danger); }
.fitness-adr-card[data-gap="partial"] { border-left-color: var(--warn); }
.fitness-adr-card[data-gap="enforced"] { border-left-color: var(--ok); }
.fa-head { display: flex; align-items: baseline; gap: 0.55rem; margin-bottom: 0.35rem; }
.fa-head h3 { flex: 1; margin: 0; font-family: var(--ui); font-size: 0.95rem; font-weight: 600; }
.fa-adr code { color: var(--accent); font-size: 0.78rem; }
.fa-gap-chip { font-family: var(--mono); font-size: 0.72rem; font-weight: 700;
               padding: 0.1rem 0.5rem; border-radius: 999px; color: #FAF9F5; }
.fa-gap-chip.gap-open { background: var(--danger); }
.fa-gap-chip.gap-partial { background: var(--warn); }
.fa-gap-chip.gap-enforced { background: var(--ok); }
.fa-proposal { margin: 0.3rem 0 0; font-size: 0.85rem; color: var(--text-muted); }
.fa-proposal a { color: var(--accent); }
```

### Proposed Fitness Functions → Per-level lanes

The headline section. Each proposal is a card with name, what-it-checks, threshold, level, implementation approach, ADR enforced (if any), severity. Group cards into 4 lanes by governance level.

```html
<div class="fitness-lanes">
  <section class="fitness-lane" data-level="1">
    <header class="fl-head"><span class="fl-chip fl-1">L1 commit</span> <span class="fl-subtitle">&lt;30s · every commit</span></header>
    <div class="fl-cards">
      <article class="ff-card" id="proposed-fitness-functions-fn-1" data-anchor-parent="proposed-fitness-functions" data-severity="high">
        <h4 class="ff-name">No imports across bounded contexts</h4>
        <dl class="ff-fields">
          <dt>Checks</dt><dd>Import paths do not cross <code>contexts/&lt;X&gt;/</code> → <code>contexts/&lt;Y&gt;/</code></dd>
          <dt>Threshold</dt><dd>0 violations</dd>
          <dt>Implementation</dt><dd>ts-arch-test rule; runs in pre-commit</dd>
          <dt>Enforces</dt><dd><a href="#adr-gap-analysis-adr-007">ADR-007</a></dd>
          <dt>Severity</dt><dd><span class="rf-severity sev-high">HIGH</span></dd>
        </dl>
      </article>
    </div>
  </section>
  <!-- L2, L3, L4 lanes … -->
</div>
```

```css
.fitness-lanes { display: flex; flex-direction: column; gap: 0.9rem; }
.fitness-lane { background: var(--panel-2); border-radius: var(--radius-sm); padding: 0.7rem 0.9rem; }
.fl-head { display: flex; align-items: baseline; gap: 0.55rem; margin-bottom: 0.5rem; }
.fl-subtitle { font-family: var(--mono); font-size: 0.74rem; color: var(--text-muted); }
.fl-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 0.55rem; }
.ff-card { background: var(--panel); border: 1px solid var(--border-soft);
           border-radius: var(--radius-sm); padding: 0.7rem 0.85rem; }
.ff-card[data-severity="critical"] { border-left: 3px solid var(--danger); }
.ff-card[data-severity="high"]     { border-left: 3px solid var(--accent); }
.ff-card[data-severity="medium"]   { border-left: 3px solid var(--warn); }
.ff-card[data-severity="low"]      { border-left: 3px solid var(--ok); }
.ff-name { margin: 0 0 0.4rem; font-family: var(--ui); font-size: 0.92rem; font-weight: 600; }
.ff-fields dt { font-family: var(--mono); font-size: 0.7rem; color: var(--text-muted);
                text-transform: uppercase; letter-spacing: 0.05em; }
.ff-fields dd { margin: 0.1rem 0 0.4rem; font-size: 0.88rem; color: var(--text); }
.ff-fields code { color: var(--accent); font-size: 0.82rem; }
```

When a proposal's source body doesn't declare a governance level, place it in an unlabeled lane at the bottom; do not synthesize a level.

The `.rf-severity` chip styles reuse the `review-report.md` definitions; load that template's CSS when this section emits a severity chip.

### Prioritized Implementation Roadmap → Numbered walkthrough

The mode reference says "start with 3 fitness functions and grow". Render the source's roadmap (typically a numbered list or H3 phases) as a numbered **walkthrough** (`diagrams.md#walkthrough`):

- Step number = roadmap position.
- Step title = phase name or first-3 proposal cluster.
- Step body = which proposals (link to their cards) and the conditions for growing the set.


## Where-to-Focus Inputs

1. **Every ADR with `gap-open`** (cap 3) → "ADR gap: <ADR-NNN title>" anchored at the ADR card.
2. **CRITICAL/HIGH proposals at L1 or L2** (the cheap-to-enforce tier) → "L1 quick win: <proposal>".
3. **L4 (production) proposals with no L1/L2 equivalent** → "Only-runtime check: <proposal> – consider an upstream gate".


## Edge Cases

- **No ADRs in the project** → `## ADR Gap Analysis` typically reads "No ADRs found; consider authoring after this report". Render Generic Prose; KPI cell 2 = 0.
- **Proposals without explicit levels** → group at the bottom in a single "Unleveled" lane with a muted header. Do not infer L1-L4 from prose alone.
- **Coverage table absent** → KPI cell 4 = "—"; section renders as Generic Prose when source authored it differently.
- **Single-level proposals only** (e.g. all L2 PR checks) → render the lane with the other three labeled lanes empty + muted "no proposals yet" placeholder; preserves the 4-level scaffold for orientation.


## Example Use Cases

- **Platform engineer** – jump to L1 quick wins via the Where-to-Focus band, copy notes per proposal for the implementation backlog.
- **Architecture lead** – inspect ADR gap chips to spot which decisions lack automated enforcement and route to the next `andthen:architecture --mode fitness` round.
