# PRD Template

Use when the source is a Product Requirements Document. Detection: H1 contains "PRD" / "Product Requirements"; H2 contains both "Executive Summary" and "Functional Requirements".


## Layout

```
+-------------------------------------------------------------+
| andthen:visualize · PRD · <basename>     [ Copy notes (N) ] |
+-------------------------------------------------------------+
| ## Executive Summary                                        |
| [ Capability cards row ]                                    |
| [ Note ] [ <> ]                                             |
+-------------------------------------------------------------+
| ## Scope                                                    |
| [ Kanban: In Scope | Out of Scope | MVP ]                   |
| [ Note ] [ <> ]                                             |
+-------------------------------------------------------------+
| ## Functional Requirements                                  |
| [ User stories grid ]                                       |
| [ Note ] [ <> ]                                             |
+-------------------------------------------------------------+
| ## User Flows                                               |
| [ Inline SVG flowchart — see diagrams.md#flowchart ]        |
| [ Note ] [ <> ]                                             |
+-------------------------------------------------------------+
| ## Decisions Log                                            |
| [ Inline SVG timeline — see diagrams.md#timeline ]          |
| [ Note ] [ <> ]                                             |
+-------------------------------------------------------------+
| ## Dependencies                                             |
| [ Cards grid — see diagrams.md#list-graph ]                 |
| [ Note ] [ <> ]                                             |
+-------------------------------------------------------------+
| ## Success Metrics                                          |
| [ Metric tiles ]                                            |
| [ Note ] [ <> ]                                             |
+-------------------------------------------------------------+
```


## Section Renderers

Match each H2 in the source to a renderer below by case-insensitive substring on the heading text. Sections that don't match any specific renderer fall back to **Generic Prose** (rendered markdown).

### Executive Summary → capability cards

Parse the "Capabilities at Glance" subsection (H3 under Executive Summary) or the first list/table in the section. Each item becomes a card.

```html
<div class="capability-grid">
  <article class="capability-card">
    <h3>{{capability name}}</h3>
    <p>{{capability description}}</p>
  </article>
  <!-- ... -->
</div>
```

```css
.capability-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; }
.capability-card { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1rem 1.2rem; }
.capability-card h3 { margin: 0 0 0.5rem; color: var(--accent); font-size: 1rem; }
.capability-card p { margin: 0; color: var(--text-muted); font-size: 0.9rem; }
```

### Scope → kanban

Parse H3 subsections under `## Scope`. Typical headings: "In Scope", "Out of Scope", "MVP Boundary", "Not Doing". Render as 3 columns; merge "Not Doing" into "Out of Scope" with a divider.

```css
.scope-kanban { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.scope-column { background: var(--panel); border-radius: 8px; padding: 1rem; }
.scope-column h3 { margin-top: 0; }
.scope-column.in-scope h3 { color: #1a7f37; }   /* green */
.scope-column.out-scope h3 { color: var(--text-muted); }
.scope-column.mvp h3 { color: #bf8700; }        /* amber */
.scope-column ul { padding-left: 1.2rem; margin: 0.5rem 0; }
```

### Functional Requirements → user stories grid

If the section contains a user-stories table (typical columns: As a / I want / So that), parse rows and render as cards. Otherwise render as generic markdown.

```javascript
function parseUserStoriesTable(body) {
  // Find the first markdown table; assume row 1 = header, separator, then data rows
  const lines = body.split('\n').filter(l => /^\s*\|/.test(l));
  if (lines.length < 3) return null;
  const headers = parseRow(lines[0]);
  const rows = lines.slice(2).map(parseRow);
  return { headers, rows };
}
```

Story card:
```html
<article class="story-card">
  <div class="role">As a <strong>{{role}}</strong></div>
  <div class="want">I want <strong>{{want}}</strong></div>
  <div class="benefit">so that {{benefit}}</div>
</article>
```

### User Flows → flowchart

For each numbered flow (H3 under `## User Flows`), generate one inline SVG flowchart. See `diagrams.md#flowchart` for the layout algorithm. Each flow gets its own diagram + Note affordance attached to the flow's parent section.

### Decisions Log → table + timeline

Render the source's `| Decision | Rationale | Date |` table as-is (collapsed by default behind a "Show table" toggle). Above the table, render the **inline SVG timeline** per `diagrams.md#timeline`.

### Dependencies → cards grid

Parse the `| Dependency | Purpose | Risk |` table; render each row as a card. See `diagrams.md#list-graph` for card structure and risk-level coloring.

### Success Metrics → metric tiles

```html
<div class="metrics-grid">
  <div class="metric-tile">
    <div class="metric-label">{{name}}</div>
    <div class="metric-target">{{target}}</div>
    <div class="metric-rationale">{{rationale}}</div>
  </div>
</div>
```

```css
.metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
.metric-tile { background: var(--panel); border-left: 3px solid var(--accent); border-radius: 6px; padding: 1rem; }
.metric-target { font-size: 1.5rem; font-weight: 600; color: var(--accent); margin: 0.3rem 0; }
.metric-rationale { font-size: 0.85rem; color: var(--text-muted); }
```

### Generic Prose (fallback)

Render markdown inline. Convert H3/H4 to `<h3>/<h4>`, lists to `<ul>/<ol>`, code spans to `<code>`, bold to `<strong>`, italics to `<em>`. Code blocks render verbatim inside `<pre><code>`.


## Pre-population

For each PRD invocation:

1. Read the source markdown.
2. Parse into H2-anchored sections per the SKILL.md anchor scheme.
3. For each section, dispatch to a renderer above (case-insensitive substring match on H2 text).
4. Sections without a specific renderer fall back to Generic Prose.
5. Wrap each rendered section in the standard `<section data-anchor="{{anchor}}">` block from the SKILL.md HTML scaffold (with Note + View source affordances).


## Example Use Cases

- Reviewing a fresh PRD before handing to `andthen:plan`
- Verifying an existing PRD with stakeholders
- Exporting review notes for `andthen:prd` amendment
