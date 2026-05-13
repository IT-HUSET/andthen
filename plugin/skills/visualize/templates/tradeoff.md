# Trade-off Template

Use when the source is an architecture trade-off report from `andthen:architecture --mode trade-off`. Detection: H1 or H2 contains "Trade-off" / "Trade off" / "Decision Analysis"; presence of a scoring matrix table with options as rows and criteria as columns.


## Layout

```
+-------------------------------------------------------------+
| andthen:visualize · Trade-off · <basename>         [ Copy ] |
+-------------------------------------------------------------+
| ## Decision Statement                                       |
| [ rendered prose ]                            [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Scoring Matrix                                           |
| [ Table – recommended row highlighted ]       [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Options                                                  |
| Option 1: <name>                                            |
|   <description>                                             |
|   [ Inline SVG radar – see diagrams.md#radar ]              |
| Option 2: <name>                                            |
|   <description>                                             |
|   [ Inline SVG radar ]                                      |
| ...                                            [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Recommendation                                           |
| [ rendered prose, accent-highlighted ]        [ Note ] [ <> ]|
+-------------------------------------------------------------+
```


## KPI Cells

The four-cell `.kpi-band` (rendered per the SKILL.md *KPI Summary Band* contract) sits between `.doc-header` and the first section. Trade-off cells in source order:

| Cell | Label | Source |
|---|---|---|
| 1 | Options | Count of options (data rows in the scoring matrix, or H3 subsections under `## Options`) |
| 2 | Recommended | Label of the recommended option (single string, truncated to 16 chars; "—" if none) |
| 3 | Effort | Source's effort estimate (label from a `Effort:` line in the recommendation, or "—") |
| 4 | Risk Level | Source's risk indicator (`Low` / `Medium` / `High` from recommendation prose, or "—") |

Auto-`.attention`: cell 4 when value matches `/^high/i`.


## Section Renderers

### Decision Statement
Render as generic prose. If the section is short (≤ 3 paragraphs), use a slightly larger font for emphasis.

### Scoring Matrix

Render the source matrix table preserving option × criterion structure. Column headers from the source's first row; option labels from row 1 of each data row. Score cells render as numbers; the recommended row (typically the source marks with `← chosen`, `**`, or a "Recommended" cell) gets accent highlighting.

```css
.scoring-matrix { width: 100%; border-collapse: collapse; }
.scoring-matrix th { background: var(--panel); padding: 0.5rem; text-align: left; border-bottom: 1px solid var(--border); }
.scoring-matrix td { padding: 0.5rem; border-bottom: 1px solid var(--border); }
.scoring-matrix td.score { font-family: var(--mono); text-align: right; }
.scoring-matrix tr.recommended { border: 2px solid var(--accent); background: rgba(193, 95, 60, 0.08); }
.scoring-matrix tr.recommended td:first-child::before { content: '★ '; color: var(--accent); }
```

To detect the recommended row, scan each row's text for: `← chosen`, `(recommended)`, `**chosen**`, or a `Recommended` column with a non-empty value.

### Options

Each option in the source's `## Options` section (typically as H3 subsections per option) renders as a card with three regions. **Per-option Note buttons are intentionally omitted** – the SKILL.md anchor scheme is H2-keyed (verbatim heading text), so notes attach to the parent `## Options` section, not per-option H3. Reviewers wanting to comment on a specific option write the option's name into the note body (e.g. *"Option B: weight criterion X higher"*); the payload's `## Section: Options` block then carries one bullet per option-scoped note. Whole-diagram annotation stays anchored by the diagram's parent section heading, matching how downstream skills consume the payload.

**Above the H3 list:** emit a `<nav class="risk-map">` summary row (per the SKILL.md *Risk-map chips* contract). One chip per option, color-coded: recommended option → `.attention`, deferred/rejected options → `.neutral`, options with `risk: high` or `caveat:` in the body → `.medium`. Each chip's `href` points at the option's H3 sub-anchor (`#options-{option-kebab}`); click pulses the target.

**Option-body rendering (all-or-nothing per `## Options` section):** when **every** H3 option's body carries ≥ 2 H4 subheadings matching `/^(What changes|Where it changes|Risk|Trade-off)/i`, render every option as a **Walkthrough** (see `diagrams.md#walkthrough`) alongside its radar – Step 1 = What changes, Step 2 = Where, Step 3 = Risk. If even one option doesn't have the H4 set, render *every* option as prose-only body. Mixing Walkthrough and prose within the same `## Options` section is disallowed – it reads as a renderer bug, and the SKILL.md *Renderer Discipline* "one renderer per H2" rule applies per-section, not per-H3. Secondary detail (anything after the primary verdict paragraph, or content under an H4 named `Detailed analysis` / `Notes` / `Background`) wraps in `<details class="analysis">` (SKILL.md *Supporting-detail collapse* contract). Light TL;DR (SKILL.md contract) emits as the first child of each option's `.card-body` when the source authored one.

```html
<section class="option" data-anchor-parent="options">
  <h3>{{Option name}}</h3>
  <div class="option-body">
    <div class="option-prose">{{description and analysis}}</div>
    <svg class="diagram diagram-radar"><!-- see diagrams.md#radar --></svg>
  </div>
</section>
```

```css
.option { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; margin: 1rem 0; }
.option h3 { margin: 0 0 1rem; color: var(--accent); }
.option-body { display: grid; grid-template-columns: 1fr 320px; gap: 1.5rem; align-items: start; }
.option .diagram-radar { width: 320px; height: 320px; }

@media (max-width: 720px) {
  .option-body { grid-template-columns: 1fr; }
  .option .diagram-radar { width: 100%; max-width: 320px; }
}
```

For each option, extract the option's per-criterion scores from the corresponding scoring matrix row, plus the criteria weights (typically declared in the source's "Weighted Criteria" or "Criteria" section, or inferred as equal weight if absent). Pass to the radar chart algorithm in `diagrams.md#radar`.

### Recommendation

Render with accent border-left and slightly elevated background:

```css
.recommendation { border-left: 4px solid var(--accent); padding: 1rem 1.5rem; background: rgba(193, 95, 60, 0.05); border-radius: 0 8px 8px 0; }
.recommendation h2 { margin-top: 0; color: var(--accent); }
```

If the recommendation section names a specific option, render that option name as a clickable anchor link to the option's section.


## Pre-population

1. Parse the scoring matrix to extract options, criteria, scores, and (if present) weights.
2. Build the per-option score arrays for radar chart generation.
3. For each option's H3 subsection, render its prose + radar.
4. Match the scoring matrix's recommended row to the corresponding option section for cross-linking.


## Edge Cases

- **No weights declared in source** → use equal weights (1.0 / N for N criteria). Note in a small footer text under the matrix: *"Weights not specified – using equal weights."*
- **Non-numeric score cells** → treat as 0; emit a small inline warning in the cell *"non-numeric"* in `var(--warn)`.
- **Recommended row ambiguous** → if no row matches the detection patterns, render no row highlight; emit a small inline note above the matrix *"Recommendation row not detected – see Recommendation section below."*
- **Single-option trade-off** (degenerate case) → render the option card and radar normally; skip the matrix highlighting since there's no comparison.


## Example Use Cases

- Reviewing a trade-off analysis before formalizing as ADR
- Comparing options' shape visually (radar charts make weight-vs-score asymmetries obvious)
- Exporting review notes ("revisit option B's evidence", "weight criterion X higher") for a re-run of `andthen:architecture --mode trade-off`
