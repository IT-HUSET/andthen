# Clarification Template

Use when the source is a `requirements-clarification.md` from `andthen:clarify`. Detection: H1 starts with "Requirements Clarification"; H2 contains "Decisions Log".


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
| [ Design tree — see diagrams.md#tree ]        [ Note ] [ <> ]|
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


## Section Renderers

### Scope → 4-column kanban

Same renderer as PRD's scope, but include "Not Doing" as a fourth column (don't merge).

```css
.scope-kanban-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
.scope-column.not-doing h3 { color: var(--accent-warn); }
```

### Design Decisions → tree + notes + table

The headline view of clarification documents. Three subsections:

1. **Design Space Decomposition** — render as inline SVG tree per `diagrams.md#tree`. Below the diagram, include the original ASCII text inside a `<details><summary>View source</summary><pre>...</pre></details>` so the user can verify the diagram matches the source.
2. **Cross-Consistency Notes** — bulleted list with light styling:

   ```css
   .cross-consistency { padding-left: 1rem; border-left: 2px solid var(--text-muted); margin: 1rem 0; }
   .cross-consistency li { color: var(--text-muted); }
   .cross-consistency li.incompatible::before { content: '✗ '; color: var(--accent-warn); }
   .cross-consistency li.conditional::before { content: '~ '; color: #bf8700; }
   ```

3. **Resolved Decisions** — `| Dimension | Choice | Rationale |` table rendered as-is.

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
.criteria-list li.checked { border-left-color: #1a7f37; }
.criteria-list input[type=checkbox] { margin-right: 0.5rem; }
```

### Decisions Log → table

Render the `| Decision | Rationale | Date |` table; date column muted.

```css
.decisions-log td:last-child { color: var(--text-muted); font-family: var(--mono); white-space: nowrap; }
```


## Pre-population

Same approach as PRD: parse → dispatch per H2 substring match → render. Generic Prose fallback for unmatched sections.

The Design Decisions section is the visual centerpiece — make sure it's prominently styled (slightly larger panel, accent border) so reviewers gravitate to the design tree first.


## Example Use Cases

- Reviewing clarification output before authoring PRD
- Spotting unresolved design dimensions visually (open question count surfaced clearly)
- Exporting review notes for `andthen:clarify` amendment mode
