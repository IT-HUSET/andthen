# Clarification Template

Use when the source is a `requirements-clarification.md` or product vision artifact from `andthen:clarify`. Detection: H1 starts with "Requirements Clarification"; or product-vision detection from SKILL.md matches.


## Layout

```
+-------------------------------------------------------------+
| andthen:visualize · Clarification · <basename>     [ Copy ] |
+-------------------------------------------------------------+
| ## Summary                                                  |
| [ rendered prose ]                            [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Scope                                                    |
| [ Kanban: In | Out | MVP | Not Doing ]        [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Functional Requirements                                  |
| [ Stories list + flow steps ]                 [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Design Decisions                                         |
| [ Design tree – see diagrams.md#tree ]        [ Note ] [ <> ]|
| [ Cross-consistency notes ]                                 |
| [ Resolved decisions table ]                                |
+-------------------------------------------------------------+
| ## Edge Cases                                               |
| [ Two-column table ]                          [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Success Criteria                                         |
| [ Checklist with disabled checkboxes ]        [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Decisions Log                                            |
| [ Decisions table ]                           [ Note ] [ <> ]|
+-------------------------------------------------------------+
```


## KPI Cells

The four-cell `.kpi-band` (rendered per the SKILL.md *KPI Summary Band* contract) sits between `.doc-header` and the first section. Clarification cells in source order:

| Cell | Label | Source |
|---|---|---|
| 1 | Open Questions | Count of bullets under `## Open Questions` not marked `(resolved)` / `→` / `lean:` |
| 2 | Resolved | Count of rows in `## Decisions Log` table |
| 3 | Decisions | Count of dimension rows in `## Design Decisions` → "Resolved Decisions" table |
| 4 | Edge Cases | Count of rows in `## Edge Cases` table |

Auto-`.attention`: cell 1 when count > 0.


## Section Renderers

Dispatch to **Feature Clarification Renderer** when detected type is `clarification`; dispatch to **Product Vision Renderer** when detected type is `product-vision`. Do not treat product vision as a PRD: it is upstream framing, not a feature requirements document.

### Feature Clarification Renderer

### Scope → 4-column kanban

Same renderer as PRD's scope, but include "Not Doing" as a fourth column (don't merge).

```css
.scope-kanban-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
.scope-column.not-doing h3 { color: var(--warn); }
```

### Design Decisions → tree + notes + table

The headline view of clarification documents. Three subsections:

1. **Design Space Decomposition** – render as inline SVG tree per `diagrams.md#tree`. Below the diagram, include the original ASCII text inside a `<details><summary>View source</summary><pre>...</pre></details>` so the user can verify the diagram matches the source.
2. **Cross-Consistency Notes** – bulleted list with light styling:

   ```css
   .cross-consistency { padding-left: 1rem; border-left: 2px solid var(--text-muted); margin: 1rem 0; }
   .cross-consistency li { color: var(--text-muted); }
   .cross-consistency li.incompatible::before { content: '✗ '; color: var(--danger); }
   .cross-consistency li.conditional::before { content: '~ '; color: var(--warn); }
   ```

3. **Resolved Decisions** – `| Dimension | Choice | Rationale |` table rendered as-is. **Walkthrough variant:** when the table has ≤ 5 rows AND every Rationale cell's stripped Unicode-code-point count is ≥ 60 (same stripping rule as `prd.md#User Flows` walkthrough trigger – strip leading/trailing whitespace and markdown markers, count code points), render as a numbered **Walkthrough** (see `diagrams.md#walkthrough`) instead of a plain table – each row becomes one step (Dimension as the step title, Choice in mono as the step location, Rationale as the prose).

Open Questions H3 blocks (when present under this section or its own H2) may emit `.risk-map` chips above the list per SKILL.md *Risk-map chips* contract: unresolved → `.attention`, leaning-toward → `.medium`, resolved → `.safe`. Light TL;DR (SKILL.md contract) may appear as the first child of an Open Question H3 block when authored.

### Edge Cases → highlighted table

Two-column `| Scenario | Expected Behavior |` table. Highlight the scenario column.

```css
.edge-cases td:first-child { color: var(--accent); font-family: var(--mono); font-size: 0.9rem; }
.edge-cases tr { border-bottom: 1px solid var(--border); }
```

### Success Criteria → checklist

Render `- [ ]` and `- [x]` lines as disabled checkboxes preserving check state from source.

```javascript
function renderCriterion(line) {
  const m = line.match(/^- \[(x| )\] (.+)$/);
  if (!m) return null;
  const checked = m[1] === 'x';
  return `<li class="${checked ? 'checked' : ''}">
    <input type="checkbox" disabled${checked ? ' checked' : ''}>
    ${escapeHtml(m[2])}
  </li>`;
}
```

```css
.criteria-list { list-style: none; padding: 0; }
.criteria-list li { padding: 0.4rem 0.6rem; border-left: 3px solid var(--border); margin: 0.3rem 0; background: var(--panel); border-radius: 4px; }
.criteria-list li.checked { border-left-color: var(--ok); }
.criteria-list input[type=checkbox] { margin-right: 0.5rem; }
```

### Decisions Log → table

Render the `| Decision | Rationale | Date |` table; date column muted.

```css
.decisions-log td:last-child { color: var(--text-muted); font-family: var(--mono); white-space: nowrap; }
```


### Product Vision Renderer

Render the product-scope document (`PRODUCT.md` by default) as a strategic review surface. KPI cells: Personas, Value Propositions, Anti-Goals, Open Questions. Add attention styling when Anti-Goals or Open Questions is non-zero.

Section dispatch:
- `Vision` and `Problem Statement` → Generic Prose with optional light TL;DR callout when authored.
- `Target Users & Personas` → persona cards with role/context/jobs-to-be-done.
- `Value Propositions` → outcome cards; preserve testable phrasing and avoid inventing metrics.
- `Product Principles` → decision-rule list with mono labels when bullets use `**Name** – rationale`.
- `Anti-Goals` → caution cards using warn/danger styling; these are load-bearing boundaries.
- `Success Metrics` → North Star tile plus Leading Indicator tiles.
- `Strategic Constraints` → grouped constraint cards for Business, Regulatory, Technical.
- `Roadmap Themes` → theme cards; themes are not feature commitments.
- `Open Questions` and `Decisions Log` → risk-map chips plus table/list renderers.
- Anything else → Generic Prose.


## Pre-population

Same approach as PRD: parse → dispatch per H2 substring match → render. Generic Prose fallback for unmatched sections.

The Design Decisions section is the visual centerpiece – make sure it's prominently styled (slightly larger panel, accent border) so reviewers gravitate to the design tree first.


## Example Use Cases

- Reviewing clarification output before authoring PRD
- Spotting unresolved design dimensions visually (open question count surfaced clearly)
- Exporting review notes for `andthen:clarify` amendment mode
