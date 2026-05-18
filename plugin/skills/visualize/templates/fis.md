# FIS Template

Use when the source is a **Feature Implementation Specification** (FIS) – the central spec produced by the `andthen:spec` or `andthen:plan` skills and consumed by the `andthen:exec-spec` / `andthen:exec-plan` skills. Detection: H2 contains "Feature Overview and Goal" AND (H2 contains "Implementation Plan" OR H2 contains "Acceptance Scenarios" OR H2 contains "Structural Criteria"). `Implementation Plan` is the strong marker.

A FIS is *execution input* – the visualization optimizes for "is this implementable as-written" rather than narrative reading. Scenarios, tasks, and the validation checklist are the load-bearing surfaces.


## Layout

```
+-------------------------------------------------------------+
| andthen:visualize · FIS · <basename>               [ Copy ] |
+-------------------------------------------------------------+
| eyebrow + serif H1 + status pill row                        |
| [ KPI band: Scenarios · Tasks · Open Items · Discovered ]   |
| [ Where-to-focus band (open items, oversize tasks, risks) ] |
+-------------------------------------------------------------+
| ## Feature Overview and Goal                                |
| [ Generic prose (1-2 sentences) ]              [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Required Context                                         |
| [ Source-pinned block cards ]                  [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Deeper Context                                           |
| [ Anchored pointer list ]                      [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Acceptance Scenarios                                     |
| [ Checkbox cards with Given/When/Then walk ]   [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Structural Criteria                                      |
| [ Non-behavioral checklist ]                   [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Scope & Boundaries                                       |
| [ Two-column kanban (Work Areas / Not Doing) ] [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Architecture Decision                                    |
| [ Accent box (reuse tradeoff.md .recommendation) ][ Note ] [<>]|
+-------------------------------------------------------------+
| ## Technical Overview  (often empty)                        |
| [ Generic prose with H3 subsections ]          [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Code Patterns & External References                      |
| [ Type/path/intent table ]                     [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Constraints & Gotchas                                    |
| [ Constraint cards (color-coded by tag) ]      [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Implementation Plan                                      |
| [ Task walkthrough; Testing Strategy / Validation /         |
|   Execution Contract sub-H3s render below (often empty) ]    |
+-------------------------------------------------------------+
| ## Final Validation Checklist  (often empty)                |
| [ Checklist ]                                  [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Implementation Observations  (post-exec, append-only)    |
| [ Discovered Requirements cards ]              [ Note ] [ <> ]|
+-------------------------------------------------------------+
```


## Document Header

FIS prologue typically carries a `**Plan**:` and `**Story-ID**:` bold-key inline metadata pair between the H1 and the first H2. Parse these – same rule as the ADR prologue scope (between H1 and the first `## ` heading; later occurrences render as prose, not consumed):

| Source key | Header consumption |
|---|---|
| `**Plan**:` | Extra `.meta-pill` with `k="plan"`, value is the basename (full path in `title=` tooltip) |
| `**Story-ID**:` | Eyebrow line: `FIS · {{Story-ID}}` (e.g. `FIS · S03`); also extra `.meta-pill` with `k="story"` |

When neither is present (standalone FIS not generated from a plan), the eyebrow reads `FIS` and no `plan`/`story` pills emit.

**Status pill** (derived – FIS has no source status field):

- `complete` / `status-done` when every Implementation-Plan task checkbox is checked AND every Final-Validation checkbox is checked (when the checklist exists).
- `in-progress` / `status-review` when any Implementation-Plan checkbox is checked but not all.
- `draft` / `status-draft` when no task checkbox is checked.


## KPI Cells

The four-cell `.kpi-band` sits between `.doc-header` and the first section. FIS cells in source order:

| Cell | Label | Source |
|---|---|---|
| 1 | Scenarios | Count of `- [ ]`/`- [x]` checkboxes directly under `## Acceptance Scenarios` that match the canonical scenario shape (see *Acceptance Scenarios → Checkbox cards* below); non-canonical checkboxes counted separately and surfaced via the non-canonical-shape comment in `View source` |
| 2 | Tasks | Count of `- [ ]`/`- [x]` checkboxes under `## Implementation Plan` → `### Implementation Tasks` whose bold label starts with `TI` + two digits (canonical task shape – see *Implementation Plan* renderer below) |
| 3 | Open Items | Count of unchecked task checkboxes + unchecked `## Structural Criteria` checkboxes + unchecked `## Final Validation Checklist` checkboxes (when the section is present). Open scenarios are *not* added (scenarios prove tasks; the task box is the actionable item) |
| 4 | Discovered | Count of `Discovered Requirements` entries under `## Implementation Observations` (one entry = one `**Title**:` line). `0` for a freshly authored FIS |

Auto-`.attention`: cell 3 when count > 0; cell 4 when count > 0.


## Section Renderers

Each H2 dispatches to **one** renderer per the SKILL.md cross-artifact dispatch table; Generic Prose is the fallback. Section Block wrapper (id + data-anchor + static affordances) is universal.

### Feature Overview and Goal → Intent + OC-anchored bullets

A specialized renderer (not Generic Prose) because the Expected Outcomes bullets need to emit anchor IDs that scenario-card outcome chips backlink to. Two short blocks render in order:
- `**Intent**:` (one sentence) – emit as a paragraph (no special parsing).
- `**Expected Outcomes**:` (2-4 bullets, each starting with an `[OC<NN>]` token) – for each bullet, extract the leading `[OC<NN>]` token, emit the bullet as `<li id="feature-overview-and-goal-oc<nn>">` (lowercase OC ID) with the token rendered inline at the start of the bullet text. Scenario-card outcome chips backlink to these IDs (`href="#feature-overview-and-goal-oc01"`).

If the FIS is legacy (no `**Expected Outcomes**:` sub-block), fall back to Generic Prose for the section body and skip OC ID emission – there is nothing to anchor.

Use `.tldr-light` callout when the source authors one explicitly per the SKILL.md *Light TL;DR callout* contract.

### Required Context → Source-pinned block cards

Each H3 (`### From \`path\` – "Section"`) renders as a card. Parse the two HTML comments (`<!-- source: ... -->`, `<!-- extracted: ... -->`) into a metadata strip; the `> {{inlined span}}` blockquote becomes the body.

```html
<article class="fis-context-card">
  <header class="fis-context-head">
    <span class="fis-context-source"><code>{{path}}</code></span>
    <span class="fis-context-anchor">#{{anchor}}</span>
    <span class="fis-context-extracted">{{commit-sha or YYYY-MM-DD}}</span>
  </header>
  <h3>{{verbatim H3 text}}</h3>
  <blockquote class="fis-context-body">{{inlined span}}</blockquote>
</article>
```

```css
.fis-context-card { background: var(--panel); border: 1px solid var(--border-soft);
                    border-left: 3px solid var(--accent); border-radius: var(--radius-sm);
                    padding: 0.85rem 1rem; margin: 0 0 0.7rem; }
.fis-context-head { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: baseline;
                    font-family: var(--mono); font-size: 0.74rem; color: var(--text-faint); }
.fis-context-head code { color: var(--accent); background: transparent; padding: 0; }
.fis-context-anchor { color: var(--text-muted); }
.fis-context-extracted { margin-left: auto; }
.fis-context-card > h3 { margin: 0.35rem 0 0.5rem; font-size: 0.95rem;
                         font-family: var(--ui); font-weight: 600; color: var(--text); }
.fis-context-body { margin: 0; padding: 0.55rem 0.8rem; border-left: 2px solid var(--border);
                    background: var(--panel-2); color: var(--text); font-size: 0.92rem; }
.fis-context-body p:first-child { margin-top: 0; }
.fis-context-body p:last-child { margin-bottom: 0; }
```

When a card lacks one of the metadata comments, omit the missing field – do not fabricate.

### Deeper Context → Anchored pointer list

Bullet list of `path#anchor – description`. Render each entry with the path/anchor in mono and the description in body text; no card decoration (it is intentionally lightweight). Empty section bodies (or section omitted) → suppress the H2 entirely so the card isn't a blank shell.

### Acceptance Scenarios → Checkbox cards with Given/When/Then walk

**Canonical shape** – defined in `plugin/references/fis-authoring-guidelines.md` *Acceptance Scenarios and Proof-of-Work*; worked example below. Each canonical scenario is one top-level checkbox whose bold label is `S` + two digits, a space, an outcome-tag set `[OC` + two digits (optionally comma-joined repeats) `]`, a space, a task-tag set `[TI` + two digits (optionally comma-joined repeats) `]`, a space, then the description – followed by nested Given/When/Then bullets. Outcome tags precede task tags; the two groups have distinct semantics (outcome tags anchor the scenario to Expected Outcomes in *Feature Overview and Goal*; task tags backlink to Implementation Tasks that prove the scenario). The structural-integrity gate in `data-contract.md` is loose (one `- [ ]` anywhere in the section span); strict canonical-shape enforcement lives in authoring discipline.

Render each scenario as a card. Extract the scenario ID, the outcome-tag set, the task-tag set, the description, and the checked state from the bold label. Nested Given/When/Then bullets become a three-step **walkthrough** (reuse `diagrams.md#walkthrough`).

```html
<article class="fis-scenario" data-anchor-parent="acceptance-scenarios" data-checked="{{1|0}}">
  <header class="fis-scenario-head">
    <span class="fis-scen-id">S01</span>
    <span class="fis-scen-desc">Happy path – user can export filtered results</span>
    <span class="fis-scen-oc-tags">
      <a class="fis-scen-oc-tag" href="#feature-overview-and-goal-oc01">OC01</a>
    </span>
    <span class="fis-scen-tags">
      <a class="fis-scen-tag" href="#implementation-plan-ti01">TI01</a>
      <a class="fis-scen-tag" href="#implementation-plan-ti03">TI03</a>
    </span>
    <span class="fis-scen-check" aria-label="checked">{{✓ when checked, otherwise empty}}</span>
  </header>
  <ol class="fis-scen-walk">
    <li><span class="fis-scen-step">Given</span> <span class="fis-scen-body">filtered results exist</span></li>
    <li><span class="fis-scen-step">When</span> <span class="fis-scen-body">the user exports CSV</span></li>
    <li><span class="fis-scen-step">Then</span> <span class="fis-scen-body">the CSV contains only filtered rows with the required columns</span></li>
  </ol>
</article>
```

```css
.fis-scenario { background: var(--panel); border: 1px solid var(--border-soft);
                border-radius: var(--radius-sm); padding: 0.7rem 0.9rem; margin: 0 0 0.6rem; }
.fis-scenario[data-checked="1"] { border-left: 3px solid var(--ok); }
.fis-scenario[data-checked="0"] { border-left: 3px solid var(--text-faint); }
.fis-scenario-head { display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.55rem;
                     margin-bottom: 0.5rem; }
.fis-scen-id { font-family: var(--mono); font-size: 0.74rem; font-weight: 700;
               background: var(--panel-3); color: var(--text-muted);
               padding: 0.1rem 0.4rem; border-radius: var(--radius-sm); }
.fis-scen-desc { font-weight: 600; color: var(--text); flex: 1; min-width: 0; }
.fis-scen-oc-tags, .fis-scen-tags { display: inline-flex; gap: 0.3rem; }
.fis-scen-oc-tag { font-family: var(--mono); font-size: 0.72rem; color: var(--text-muted);
                   text-decoration: none; border: 1px dashed var(--text-muted);
                   padding: 0.05rem 0.4rem; border-radius: 999px; }
.fis-scen-oc-tag:hover { background: var(--panel-3); }
.fis-scen-tag { font-family: var(--mono); font-size: 0.72rem; color: var(--accent);
                text-decoration: none; border: 1px solid var(--accent);
                padding: 0.05rem 0.4rem; border-radius: 999px; }
.fis-scen-tag:hover { background: var(--accent-soft); }
.fis-scen-check { color: var(--ok); font-family: var(--mono); }
.fis-scen-walk { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.3rem; }
.fis-scen-walk li { display: grid; grid-template-columns: 64px minmax(0, 1fr); gap: 0.55rem; align-items: baseline; }
.fis-scen-step { font-family: var(--mono); font-size: 0.74rem; color: var(--text-muted);
                 text-transform: uppercase; letter-spacing: 0.06em; }
.fis-scen-body { color: var(--text); font-size: 0.92rem; }
```

Each scenario card gets `id="acceptance-scenarios-s01"` (lowercase ID). Task-tag chips backlink to Implementation Plan tasks (`href="#implementation-plan-ti01"`); outcome-tag chips backlink to Expected Outcome bullets in Feature Overview and Goal (`href="#feature-overview-and-goal-oc01"`). Only task tags participate in the *Where-to-Focus* task-state mismatch check; outcome tags are anchors, not state.

**Non-canonical fallback** – when a `## Acceptance Scenarios` section contains plain `- [ ]` checkboxes that do *not* match the canonical shape above, render each line as a single-line scenario card (description-only, no walk) and leave a `<!-- fis-scenario: non-canonical shape -->` HTML comment in `View source` so the gap surfaces. Do not silently coerce.

### Structural Criteria → Checklist

Non-behavioral proof requirements: invariants, regression guards, and structural checks that must hold true when done. Each criterion is proved by a task `Verify` line, not a scenario.

`- [ ]` / `- [x]` bullets under `## Structural Criteria` render as disabled checkboxes (reuse the clarification template's checklist renderer). Unchecked items fold into KPI cell 3 ("Open Items") alongside unchecked tasks and unchecked FVC items. Empty body (section heading present but no checkboxes) → render a muted "no structural criteria authored" note; do not synthesize placeholder boxes.

When a structural-criteria checkbox is unchecked while every Implementation-Plan task is checked, surface the tag/state mismatch via the *Where-to-Focus* priority list (entry 4) so the reviewer sees the open non-behavioral proof surface before assuming completion.

### Scope & Boundaries → Two-column kanban

Two columns: **Work Areas** and **What We're NOT Doing** / **Out of Scope**. Reuse the PRD scope-kanban CSS, but emit `.scope-kanban` with 2 columns instead of 3. When an off-template `### Agent Decision Authority` H3 is present (authors add by hand for rare scope-partitioning cases), render it below the two columns as a two-bullet card (`Autonomous` / `Escalate`) with muted styling.

```css
.fis-scope-kanban { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
.fis-decision-authority { background: var(--panel-2); border-radius: var(--radius-sm);
                          padding: 0.7rem 0.9rem; margin-top: 0.8rem; }
.fis-decision-authority .k { font-family: var(--mono); font-size: 0.74rem;
                             color: var(--accent); font-weight: 700; }
```

### Architecture Decision → Accent box

Reuse `tradeoff.md` `.recommendation` styling. When the body matches a single `**Approach**:` line (the default shape), render as the accent box only. When the rare expanded shape (`**Rationale**:` + `**Alternatives considered**:` numbered list) is present, render the alternatives list below the accent box using the `tradeoff.md` `.option` layout (no radar).

When the body links to an external ADR (`See ADR: <path>/NNN-<slug>.md`), surface the link prominently in the accent box header.

### Technical Overview → Generic Prose

Render as-is with H3 sub-anchors. No special dispatch. The section often ships empty (template-default for the typical feature where synthesis is self-evident); when the body is empty or carries only the template's `{{Synthesis prose, if non-obvious}}` placeholder, render a muted "no synthesis needed" note rather than the prompt text.

### Code Patterns & External References → Type/path/intent table

The canonical FIS shape is a fenced code block with `# type | path#anchor | why needed (intent)` header and 1-line rows. Parse the block, render as a typed table.

```html
<table class="fis-patterns">
  <thead><tr><th>Type</th><th>Path / URL</th><th>Why needed (intent)</th></tr></thead>
  <tbody>
    <tr class="t-file"><td><code>file</code></td><td><code>src/api/users.ts#getUser</code></td><td>API shape – match request/response envelope</td></tr>
    <tr class="t-url"><td><code>url</code></td><td><a href="…">docs.example.com/auth</a></td><td>OAuth flow reference</td></tr>
  </tbody>
</table>
```

```css
.fis-patterns { width: 100%; border-collapse: collapse; }
.fis-patterns th { background: var(--panel-2); text-align: left;
                   padding: 0.45rem 0.6rem; font-family: var(--mono); font-size: 0.74rem;
                   color: var(--text-muted); border-bottom: 1px solid var(--border); }
.fis-patterns td { padding: 0.45rem 0.6rem; border-bottom: 1px solid var(--border-soft);
                   vertical-align: top; }
.fis-patterns td:first-child code { color: var(--accent); }
.fis-patterns tr.t-url td:nth-child(2) a { color: var(--text); text-decoration: underline; }
```

Render type values as muted code chips; treat `url` rows' second column as a clickable link (rel="noopener"), but the link must work from `file://` (no fetch) – it just opens the URL.

### Constraints & Gotchas → Constraint cards

The canonical FIS shape uses bold-key tags: `- **Constraint**: ...` / `- **Avoid**: ...` / `- **Critical**: ...`. Render each bullet as a card with the tag as an inline chip; color-code chips by tag (`Critical` → danger, `Constraint` → warn, `Avoid` → accent).

```css
.fis-gotcha-list { display: flex; flex-direction: column; gap: 0.5rem; }
.fis-gotcha { background: var(--panel); border: 1px solid var(--border-soft);
              border-radius: var(--radius-sm); padding: 0.55rem 0.8rem; }
.fis-gotcha .tag { font-family: var(--mono); font-size: 0.72rem; font-weight: 700;
                   padding: 0.08rem 0.45rem; border-radius: 999px; margin-right: 0.5rem; }
.fis-gotcha.t-critical .tag { background: var(--danger); color: #FAF9F5; }
.fis-gotcha.t-constraint .tag { background: var(--warn); color: #FAF9F5; }
.fis-gotcha.t-avoid .tag { background: var(--accent); color: #FAF9F5; }
.fis-gotcha .body { color: var(--text); font-size: 0.92rem; }
```

When the bullet doesn't match a known tag, render as a neutral card with a `note` tag.

### Implementation Plan → Task walkthrough

The headline section. Each task uses the canonical FIS shape – `- [ ] **TI<NN>** {{outcome}}` followed by 1-2 indented context lines and a `**Verify**:` line. Render the task list as a numbered **walkthrough** (`diagrams.md#walkthrough`):

- Step number = `TI<NN>` (zero-padded).
- Step title = the outcome text after `**TIxx**`.
- Step location = the canonical `file#symbol` pattern reference from the context line, when present.
- Step body = the remaining context lines, with the `**Verify**:` line surfaced as a distinct olive-accent footer.
- Checked tasks (`- [x]`) get olive `data-checked="1"` styling; unchecked tasks stay neutral.

```html
<ol class="fis-task-list">
  <li class="fis-task" id="implementation-plan-ti01" data-anchor-parent="implementation-plan" data-checked="0">
    <header class="fis-task-head">
      <span class="fis-task-id">TI01</span>
      <span class="fis-task-outcome">Event ingestion endpoint accepts and validates incoming payloads</span>
    </header>
    <p class="fis-task-context">Follow <code>src/api/users.ts#getUser</code> for envelope; reuse existing validation middleware.</p>
    <p class="fis-task-verify"><span class="k">Verify</span> <code>Test: POST /events with valid payload returns 201; invalid payload returns 422</code></p>
  </li>
</ol>
```

```css
.fis-task-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.6rem; }
.fis-task { background: var(--panel); border: 1px solid var(--border-soft);
            border-left: 3px solid var(--accent); border-radius: var(--radius-sm);
            padding: 0.7rem 0.9rem; }
.fis-task[data-checked="1"] { border-left-color: var(--ok); }
.fis-task[data-checked="1"] .fis-task-id { background: var(--ok); color: #FAF9F5; }
.fis-task-head { display: flex; align-items: baseline; gap: 0.6rem; margin-bottom: 0.4rem; }
.fis-task-id { font-family: var(--mono); font-size: 0.74rem; font-weight: 700;
               background: var(--accent); color: #FAF9F5;
               padding: 0.1rem 0.5rem; border-radius: var(--radius-sm); }
.fis-task-outcome { color: var(--text); font-weight: 600; }
.fis-task-context { margin: 0 0 0.35rem; color: var(--text-muted); font-size: 0.9rem; }
.fis-task-context code { color: var(--accent); }
.fis-task-verify { margin: 0; padding: 0.35rem 0.55rem;
                   background: var(--ok-soft); border-radius: var(--radius-sm);
                   font-size: 0.88rem; }
.fis-task-verify .k { font-family: var(--mono); font-size: 0.7rem; font-weight: 700;
                       color: var(--ok); margin-right: 0.35rem; }
.fis-task-verify code { color: var(--text); background: transparent; padding: 0; }
```

**Sub-sections** of `## Implementation Plan`:

- `### Testing Strategy` H3 renders as a bullet list below the task walkthrough with `[TIxx]` tags styled as `<a>` chips backlinking to the task cards (same pattern as scenario tag chips). Empty body (only the template's `{{Test-approach note, if non-obvious}}` placeholder) → render a muted "standard test approach" note rather than the prompt text.
- `### Validation` H3 renders as a muted prose block. Empty body (only the template's `{{Feature-specific validation requirement, if any}}` placeholder) → render a muted "no feature-specific validation" note.
- `### Execution Contract` H3 renders as Generic Prose. Empty body (only the template's `{{Feature-specific execution constraint, if any}}` placeholder) → render a muted "no feature-specific execution constraints" note.

### Final Validation Checklist → Checklist

Render `- [ ]` / `- [x]` bullets as disabled checkboxes (reuse the clarification checklist renderer). Empty body (only the template's `{{Feature-specific final gate, if any}}` placeholder) → render a muted "no feature-specific final gates" note rather than synthesizing an empty checkbox.

### Implementation Observations → Discovered Requirements cards

Per-entry card – one card per `**Title**:` line in the section body. Each entry has six expected fields (Title / Description / Rationale / Interpretation (AUTO_MODE only) / Traced from / Date); render as a labelled key/value grid.

```html
<article class="fis-observation">
  <header class="fis-obs-head">
    <h3>{{Title}}</h3>
    <span class="fis-obs-traced"><a href="#implementation-plan-ti04">TI04</a></span>
    <span class="fis-obs-date">{{YYYY-MM-DD}}</span>
  </header>
  <dl class="fis-obs-fields">
    <dt>Description</dt><dd>{{...}}</dd>
    <dt>Rationale</dt><dd>{{...}}</dd>
    <dt>Interpretation</dt><dd>{{... – AUTO_MODE only}}</dd>
  </dl>
</article>
```

```css
.fis-observation { background: var(--panel); border: 1px solid var(--border-soft);
                   border-left: 3px solid var(--warn); border-radius: var(--radius-sm);
                   padding: 0.7rem 0.9rem; margin: 0 0 0.6rem; }
.fis-obs-head { display: flex; align-items: baseline; gap: 0.55rem; margin-bottom: 0.4rem; }
.fis-obs-head h3 { margin: 0; font-size: 0.95rem; font-family: var(--ui); font-weight: 600; }
.fis-obs-traced a { font-family: var(--mono); font-size: 0.72rem; color: var(--accent);
                    text-decoration: none; border: 1px solid var(--accent);
                    padding: 0.05rem 0.4rem; border-radius: 999px; }
.fis-obs-date { margin-left: auto; font-family: var(--mono); font-size: 0.72rem;
                color: var(--text-muted); }
.fis-obs-fields dt { font-family: var(--mono); font-size: 0.72rem; color: var(--text-muted);
                     text-transform: uppercase; letter-spacing: 0.05em; }
.fis-obs-fields dd { margin: 0.15rem 0 0.5rem; color: var(--text); font-size: 0.9rem; }
```

When the section body is the verbatim `_No observations recorded yet._` placeholder, render that line muted and omit the cards. The KPI cell `Discovered` is `0` in that case.


## Where-to-Focus Inputs

Per SKILL.md *Where-to-Focus Priority Section* heuristic, in source-relevance order:

1. **Unchecked task with a `**Verify**:` line referencing a TODO, FIXME, placeholder, or "not implemented" marker** → "Verify command unresolved: TI<NN>".
2. **Constraint or Gotcha tagged `Critical`** → "Critical constraint: <body>".
3. **Discovered Requirements entries from a recent date** (within source's most-recent date among entries) → "Discovered after spec: <Title>".
4. **Unchecked Acceptance Scenario whose task-tag set references no implemented task** (a `[TI<NN>]` chip whose target task is checked but the scenario is unchecked, or vice versa – task/state mismatch). Outcome `[OC<NN>]` chips are anchors only and do not participate in this check. → "Scenario/task state mismatch: S<NN>".
5. **Unchecked Structural Criteria while every Implementation-Plan task is checked** → "Structural Criteria open after tasks complete: <criterion text>". Surfaces the non-behavioral proof surface a reviewer is most likely to skim past after seeing all tasks green.
6. **Oversize fallback** – if Implementation Plan has > 12 tasks, flag once with "Long execution: N tasks – consider splitting".


## Pre-population and Source Consumption

1. Parse the prologue metadata pair *before* dispatching the first H2. Consume both lines into `.doc-header` so Generic Prose fallback skips them.
2. Parse the Implementation Plan checkboxes once; cache the per-task checked state so Scenarios cards can render tag-chip backlinks with consistent state.
3. The Renderer Discipline *section-deduplication* rule applies: when the task walkthrough consumes the Implementation Tasks H3, the Generic Prose pass must not re-emit the same task lines as prose fallback.


## Edge Cases

- **FIS with no Implementation Plan tasks yet** (early draft) → KPI cell 2 = 0; task list renders the boilerplate `TI00 (example – delete this block)` row as muted, with a `<!-- fis: tasks not yet authored -->` comment in `View source`.
- **FIS with no Acceptance Scenarios** → KPI cell 1 = 0; render the section as a single Generic Prose card with a muted "no scenarios authored" note; the structural-integrity gate is `exec-spec`'s job, not the visualizer's.
- **FIS with no `## Structural Criteria` section** (early draft or hand-authored skip) → omit the section entirely; a missing heading is a `## Structural Criteria → Checklist` renderer no-op rather than a synthesized empty card. The `exec-spec` completion gate is the enforcement boundary, not the visualizer.
- **Long Required Context blockquotes** (> 30 lines) → render the first 12 lines, then wrap the remainder in `<details class="analysis">` with summary `Show full inlined span`. Reuses the SKILL.md *Supporting-detail collapse* contract.
- **Cross-references to plan-story sub-anchors** (`See plan S03`) → leave as plain text; cross-document anchors aren't resolvable from a single-artifact view.
- **AUTO_MODE assumption blocks in `## Implementation Observations`** (per `automation-mode.md`) → render as observation cards with the `Interpretation` field surfaced; same template otherwise.


## Example Use Cases

- **Spec author** – review the FIS before handing to the `andthen:exec-spec` skill; verify each Acceptance Scenario carries a task-tag chip and the chip's target task exists.
- **Executor** – read tasks in order, click a scenario tag chip to jump to the task it proves, confirm the `**Verify**:` line is executable.
- **Reviewer** – inspect the prologue `Plan` / `Story-ID` pills, then spot-check that every Implementation Task has a `**Verify**:` line and every scenario maps to at least one task.
