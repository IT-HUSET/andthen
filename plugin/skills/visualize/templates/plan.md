# Plan Template

Use when the source is a local AndThen `plan.json` bundle. Detection: valid JSON object with `schemaVersion`, `overview`, and `stories` array. `schemaVersion === "1"` is the supported shape; unknown versions should stop with `andthen:visualize: unsupported plan.json schemaVersion "<value>"` rather than rendering a misleading view.

`plan.json` is data, not prose. Render it through **virtual H2 sections** derived from top-level fields. The Section Block wrapper from `SKILL.md` still applies: every virtual section gets a stable `id`, static `+ Note`, `Copy section`, and `View source` affordances. The source panel for each virtual section shows the pretty-printed JSON slice that produced it, or an explanatory empty slice marker such as `[]` / `null` when the field is absent.


## Layout

```
+-------------------------------------------------------------+
| andthen:visualize · Plan · <basename>              [ Copy ] |
+-------------------------------------------------------------+
| eyebrow + serif H1 + status pill row                        |
| [ KPI band: Stories · Ready/Done · High Risk · Blocked ]    |
| [ Where-to-focus band (blocked, high-risk, missing FIS) ]   |
+-------------------------------------------------------------+
| ## Overview                                                 |
| [ Summary + phase/wave timeline ]             [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Story Catalog                                            |
| [ Status/risk chips + story cards/table ]     [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Dependency Graph                                         |
| [ Dependency lanes + edge list ]              [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Shared Decisions                                         |
| [ Decision cards linked to stories ]          [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Binding Constraints                                      |
| [ Constraint cards grouped by featureId ]     [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Risk Summary                                             |
| [ Risk cards + mitigations ]                  [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Execution Notes                                          |
| [ Rendered prose ]                            [ Note ] [ <> ]|
+-------------------------------------------------------------+
```


## Document Header

- Eyebrow type: `PLAN · plan.json`.
- H1: `Implementation Plan: {{basename parent directory or prd field}}`.
- Status pill:
  - `done` when every story status is `done` or `skipped`.
  - Label `blocked` with CSS class `status-deprecated` when any story is `blocked`.
  - `in-progress` / `status-review` when any story is `in-progress`.
  - `review` when every non-terminal story is `spec-ready`.
  - `draft` when any schedulable story has `fis: null` or status `pending`.
- Meta pills: `schema`, `stories`, `phases`, `prd`, `sha`. Keep the `prd` value compact: basename plus tooltip/title with the full path.


## KPI Cells

The four-cell `.kpi-band` sits between `.doc-header` and the first section. Plan cells in source order:

| Cell | Label | Source |
|---|---|---|
| 1 | Stories | `stories.length` |
| 2 | Ready/Done | Count of stories whose `status` is `spec-ready` or `done` |
| 3 | High Risk | Count of stories where `risk === "high"` plus `riskSummary[]` entries with `risk === "high"` whose story is not already counted |
| 4 | Blocked | Count of stories whose `status` is `blocked`, plus stories with `fis === null` and status in `pending` / `spec-ready` / `in-progress` |

Auto-`.attention`: cell 3 when count > 0; cell 4 when count > 0.


## Virtual Sections

Emit these virtual H2 sections in this exact order when their source field exists. `Overview`, `Story Catalog`, and `Dependency Graph` always render. Optional sections are omitted when their arrays are empty and their string fields are blank.

| Virtual H2 | Source field(s) | Source panel payload |
|---|---|---|
| Overview | `overview`, `prd`, `references` | JSON object with `prd`, `references`, `overview` |
| Story Catalog | `stories[]` | JSON array of stories |
| Dependency Graph | `overview.phases[]`, `stories[].phase`, `stories[].wave`, `stories[].dependsOn`, `stories[].parallel` | JSON object with `phases` and compact story scheduling fields |
| Shared Decisions | `sharedDecisions[]` | JSON array |
| Binding Constraints | `bindingConstraints[]` | JSON array |
| Risk Summary | `riskSummary[]` plus story risk/status | JSON object with `riskSummary` and compact story risk fields |
| Execution Notes | `executionNotes` | JSON string |

Section anchors are the virtual heading slugs: `overview`, `story-catalog`, `dependency-graph`, `shared-decisions`, `binding-constraints`, `risk-summary`, `execution-notes`. Story cards and dependency nodes get H3 sub-anchors under their parent section, e.g. `story-catalog-s01`, `dependency-graph-s01`; these are URL navigation only and never get per-story Note buttons.


## Section Renderers

### Overview → Summary + phase timeline

Render `overview.summary` as prose, preserving paragraph breaks. Render `overview.phases[]` as a horizontal or wrapped phase timeline. Each phase tile shows phase id, name, waves, and count of stories in that phase.

```html
<div class="plan-phase-grid">
  <article class="plan-phase">
    <div class="phase-id">{{P1}}</div>
    <h3>{{Foundation}}</h3>
    <p class="phase-waves">{{W1, W2}}</p>
    <p class="phase-count">{{N}} stories</p>
  </article>
</div>
```

```css
.plan-phase-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.7rem; margin-top: 1rem; }
.plan-phase { background: var(--panel-2); border: 1px solid var(--border-soft); border-radius: var(--radius-sm); padding: 0.85rem; }
.phase-id { font-family: var(--mono); font-size: 0.72rem; color: var(--accent); font-weight: 700; }
.plan-phase h3 { margin: 0.25rem 0 0.35rem; font-size: 0.95rem; }
.phase-waves, .phase-count { margin: 0.15rem 0; color: var(--text-muted); font-size: 0.84rem; }
```

### Story Catalog → Reviewable story cards

Render one story card per `stories[]` entry, in source order. The top row carries ID, name, status, risk, phase/wave, parallel marker, and FIS presence. The body carries `scope`, `dependsOn`, `sourceRefs`, `assetRefs`, `provenance`, and `notes` when present. Missing FIS on a schedulable story gets `.attention`; `blocked` gets `.danger`; `done` gets `.safe`.

Above the cards, emit a `.risk-map` row of chips grouped by status: blocked and missing-FIS chips use `.attention`, high-risk chips use `.medium`, done chips use `.safe`, everything else uses `.neutral`. Each chip links to the story card's H3 sub-anchor and uses the two-pass risk-map target check from `SKILL.md`.

```html
<article class="plan-story status-spec-ready risk-high" id="story-catalog-s02" data-anchor-parent="story-catalog">
  <header class="story-head">
    <span class="story-id">S02</span>
    <h3>Core Migration</h3>
    <span class="story-chip status">spec-ready</span>
    <span class="story-chip risk">high</span>
  </header>
  <p class="story-scope">{{scope}}</p>
  <dl class="story-meta">
    <div><dt>phase</dt><dd>P2 · W2</dd></div>
    <div><dt>depends</dt><dd>S01</dd></div>
    <div><dt>fis</dt><dd>fis/s02-core-migration.md</dd></div>
  </dl>
</article>
```

```css
.plan-story { background: var(--panel); border: 1px solid var(--border-soft); border-radius: var(--radius-sm); padding: 0.9rem 1rem; margin: 0.75rem 0; }
.plan-story.attention { border-left: 3px solid var(--accent); padding-left: calc(1rem - 3px); }
.plan-story.danger { border-left: 3px solid var(--danger); padding-left: calc(1rem - 3px); }
.plan-story.safe { border-left: 3px solid var(--ok); padding-left: calc(1rem - 3px); }
.story-head { display: flex; flex-wrap: wrap; gap: 0.45rem; align-items: baseline; }
.story-id { font-family: var(--mono); color: var(--accent); font-weight: 700; }
.story-head h3 { margin: 0; flex: 1 1 220px; font-size: 1rem; }
.story-chip { font-family: var(--mono); font-size: 0.72rem; padding: 0.16rem 0.45rem; border-radius: 999px; border: 1px solid var(--border); color: var(--text-muted); }
.story-chip.status-done { color: var(--ok); border-color: var(--ok); background: var(--ok-soft); }
.story-chip.status-blocked { color: var(--danger); border-color: var(--danger); background: rgba(181, 72, 43, 0.10); }
.story-chip.risk-high { color: var(--danger); border-color: var(--danger); background: rgba(181, 72, 43, 0.10); }
.story-chip.risk-medium { color: var(--warn); border-color: var(--warn); background: rgba(176, 126, 43, 0.10); }
.story-scope { margin: 0.6rem 0; color: var(--text); }
.story-meta { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 0.45rem; margin: 0.65rem 0 0; }
.story-meta div { background: var(--panel-2); border-radius: var(--radius-sm); padding: 0.45rem 0.55rem; }
.story-meta dt { font-family: var(--mono); font-size: 0.68rem; color: var(--text-faint); text-transform: uppercase; }
.story-meta dd { margin: 0.1rem 0 0; color: var(--text-muted); font-size: 0.84rem; overflow-wrap: anywhere; }
```

### Dependency Graph → Phase/wave lanes

Render a compact dependency view that privileges scheduling clarity over graph cleverness:

1. Group stories by `phase`, then `wave`.
2. Within each wave, render story pills with status/risk color.
3. Below the lanes, render an edge list for every `dependsOn` relationship (`S02 ← S01`). Use links to story anchors.
4. Flag invalid dependencies inline when a `dependsOn` ID does not exist: `<!-- plan: dependency "S99" from "S02" not found -->` and add `.attention` to the dependent story pill.

Do not hand-draw a dense SVG graph for large plans. Lanes stay readable for 5 stories and for 50 stories; dense node-link diagrams do not.

### Shared Decisions → Decision cards

Render `sharedDecisions[]` as cards. Title is the card heading; description is prose; `stories[]` becomes linked chips to story cards. Empty `stories[]` emits an inline warning comment and a muted `No linked stories` chip.

### Binding Constraints → Grouped constraint cards

Group `bindingConstraints[]` by `featureId`. Each group shows the feature id, anchor link text, and verbatim constraint. The anchor may be a relative path plus fragment; render as text/link exactly as authored, with `overflow-wrap: anywhere`.

### Risk Summary → Risk cards

Render `riskSummary[]` as mitigation cards. Merge story data by `story` when possible to show story name, status, and phase/wave. If `riskSummary[]` is empty but stories carry `risk: "high"` or `status: "blocked"`, render those stories as generated risk cards and mark the source panel as coming from compact story risk fields.

### Execution Notes → Prose

Render `executionNotes` as markdown-like prose: split paragraphs on blank lines; preserve inline code and bare paths as `<code>` when obvious. If empty, omit the section.


## Where-to-Focus Inputs

Plan focus items come from deterministic checks:

1. Blocked stories.
2. Stories with `fis === null` and status `pending`, `spec-ready`, or `in-progress`.
3. High-risk stories that are not `done`.
4. Invalid dependency references.
5. Shared decisions with zero linked stories.

Each focus item links to the owning virtual section or story sub-anchor. Omit the focus band when fewer than two items render.


## Edge Cases

- **Legacy `metadata.immutableDigest` present** → ignore for rendering. If present, show a muted `legacy metadata ignored` pill in the header; do not treat it as a schema error.
- **Unknown top-level keys** → render them only in a final collapsed `Raw Extras` block inside `Execution Notes` if that section exists, otherwise omit from the main view and keep them visible in the source panels. Do not invent a first-class section for unknown keys.
- **Malformed JSON** → fail loud with the JSON parser error and write no HTML.
- **Empty `stories[]`** → render Overview plus an empty Story Catalog callout; KPI Story count is 0; status is draft.
- **Unknown story status or risk** → render the literal value in a neutral chip and add an inline source comment. Never coerce unknown values to an existing enum color.


## Example Use Cases

- Reviewing a newly generated plan bundle before `andthen:exec-plan`
- Checking whether a partially executed plan has blocked, missing-FIS, or high-risk stories
- Exporting plan-level review notes for `andthen:plan` regeneration or `andthen:review --mode gap`
