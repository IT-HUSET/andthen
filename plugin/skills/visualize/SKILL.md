---
description: Use when reviewing a PRD, requirements-clarification, architecture trade-off report, or architecture strategic-design report visually. Renders a self-contained HTML view in the user's browser, captures section-anchored notes, and exports them as a markdown payload via clipboard. Trigger on 'review visually', 'visualize this prd', 'visualize this clarification', 'visualize trade-off', 'visualize strategic-design', 'andthen visualize'.
argument-hint: "<path-to-artifact-markdown>"
user-invocable: true
---

# Visualize Workflow Artifact

A self-contained HTML view of an AndThen artifact (PRD, `requirements-clarification.md`, architecture trade-off report, or architecture strategic-design report) opened in the user's browser, with section-anchored notes that export as a markdown payload downstream skills consume as conversational input.

Open-loop by design: emit HTML, open browser, exit. The skill does not block waiting for user interaction.


## When to Use

- Reviewing a PRD before handing to the `andthen:plan` skill
- Reviewing `requirements-clarification.md` before the `andthen:prd` skill
- Reviewing trade-off analysis before ADR formalization
- Reviewing a strategic-design report before refining or chaining into `--mode fitness` / `--mode decompose`
- Verifying an existing artifact retrospectively


## How to Use

1. Read the artifact at `$1`.
2. Detect the artifact type by content (filename advisory only).
3. Load the matching template from `templates/`:
   - `templates/prd.md` for PRDs
   - `templates/clarification.md` for `requirements-clarification.md`
   - `templates/tradeoff.md` for architecture trade-off reports
   - `templates/diagrams.md` for inline-SVG diagram patterns referenced by the templates above
   - **No specialized template** for `strategic-design` — fall back to **generic-prose rendering** (the same fallback `templates/prd.md` describes for unmatched H2 sections): emit one `<section data-anchor=...>` per H2, with the section body rendered as styled markdown. The Note affordance and View-source toggle apply per section, identical to template-driven types. Specialized renderers (e.g. context-map visual, subdomain-tree card grid) are deferred until visual polish is requested.
4. Generate a single self-contained HTML file at `.agent_temp/visualize/<slug>-<timestamp>.html`. Resolve the path against the repo root (`git rev-parse --show-toplevel`) when inside a git working tree, falling back to CWD when there is no repo. This matches the `.agent_temp/` convention other AndThen skills use, so artifacts land predictably regardless of which subdirectory the user invoked from. `<slug>` is the basename without extension; `<timestamp>` is `YYYYMMDD-HHMMSS`.
5. Open the file in the user's browser via the OS-detected command (see Browser-Open Detection below).
6. Print the output path and exit. Do not block on user interaction.


## Artifact Type Detection

Run heuristics in order; first match wins. **Filename hints are advisory only — content decides.**

| Type | Markers |
|---|---|
| `prd` | H1 contains "PRD" or "Product Requirements"; H2 contains both "Executive Summary" and "Functional Requirements" |
| `clarification` | H1 starts with "Requirements Clarification"; H2 contains "Decisions Log" |
| `strategic-design` | H1 contains "Strategic Design" / "Strategic-Design"; OR H2 set contains both "Subdomains" and "Context Map" (case-insensitive). Routes to generic-prose rendering — no specialized template. *Ordered before `tradeoff` because both report shapes share `Executive Summary` + `How to Read This Report`; the more-specific marker pair wins under first-match-wins.* |
| `tradeoff` | H1 or H2 contains "Trade-off" / "Trade off" / "Decision Analysis"; presence of a scoring matrix table (rows = options, columns = criteria) |

If no match, exit with the message *"andthen:visualize: cannot detect artifact type. Supported: PRD (`prd.md`), `requirements-clarification.md`, architecture strategic-design reports, architecture trade-off reports."* and write no HTML.


## Core Requirements (every render)

- **Single self-contained HTML file.** All CSS, JS, and SVG inlined. No external scripts, fonts, stylesheets, icons. Must work from `file://` with no network access.
- **Dark theme.** System font for UI, monospace for code/values. Use the theme tokens below.
- **Two-pane layout.** Left = scrollable artifact content; right = sticky sidebar holding the **Copy notes** button (top), section navigator with note-count badges, and a unified note list. The sidebar is always visible at viewports ≥1100px and collapses to a top drawer below that. *Why:* the floating-TOC-only pattern hid navigation on common laptop widths and put the affordances at the bottom of each section card where users miss them.
- **Static affordances, JS-attached handlers.** The `+ Note` button, `View source` toggle, and per-section note-count span MUST be present in the static HTML body of each `<section>`. JavaScript only attaches click handlers and renders the dynamic note list. *Why:* if JS fails, errors out, or is delayed, the user must still see *that* notes are possible. Empty `<div class="sec-actions"></div>` placeholders waiting for JS injection are a known regression — never ship them.
- **Read-only render + section-anchored notes.** No structured editing. One Note affordance + one View-source toggle per H2 section. Diagrams do not get their own Note affordance — the parent section's Note covers any diagram inside it.
- **Notes payload via clipboard.** "Copy notes" writes a markdown payload via `navigator.clipboard.writeText`; on failure, reveals a textarea with payload pre-selected for manual copy.
- **LocalStorage persistence.** Notes survive refresh; "Restore previous notes?" prompt on reload when a matching prior session exists.
- **`beforeunload` warning.** Fires when notes exist and have not been copied since last edit.


## Theme Tokens

```css
:root {
  /* Surfaces — three-tier depth (page → main panel → inset card) */
  --bg: #0b0f15;
  --panel: #141a22;
  --panel-2: #1b232d;
  --panel-3: #232c38;
  --border: #2a323d;
  --border-soft: #1e252f;

  /* Text */
  --text: #e1e6ec;
  --text-muted: #8a94a3;
  --text-faint: #5d6675;

  /* Accents */
  --accent: #6ea8ff;          /* primary action, links, current-section */
  --accent-soft: rgba(110, 168, 255, 0.12);
  --accent-strong: #8ab9ff;   /* hover */
  --ok: #4cc38a;
  --warn: #e4b06a;
  --danger: #f87171;

  /* Type */
  --mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  --ui: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;

  /* Geometry */
  --radius: 10px;
  --radius-sm: 6px;
  --shadow-1: 0 1px 0 rgba(255,255,255,0.02) inset, 0 1px 2px rgba(0,0,0,0.3);
  --shadow-2: 0 6px 24px rgba(0,0,0,0.35);
}
* { box-sizing: border-box; }
html, body { background: var(--bg); color: var(--text); }
body { font-family: var(--ui); margin: 0; line-height: 1.55; font-size: 15px; }
code, pre { font-family: var(--mono); }
```

The palette is GitHub-dark-derived but slightly warmer (text shifts toward `#e1e6ec`, accent toward `#6ea8ff`) so the page reads as a *review surface* rather than an IDE pane. Keep the three-tier surface system (`--bg → --panel → --panel-2`) for clear visual depth between page, section card, and inset elements.


## Layout Skeleton (every render)

```html
<body>
  <div class="app">
    <header class="topbar">
      <div class="crumb">andthen:visualize · <strong>{{TYPE}}</strong> · {{basename}}</div>
      <div class="meta-pills">{{status, date, ...}}</div>
    </header>

    <main class="content">
      <h1 class="doc-title">{{H1}}</h1>
      <div class="doc-meta">{{meta}}</div>
      <!-- one <section class="card"> per H2, see Section Block below -->
    </main>

    <aside class="sidebar">
      <div class="sidebar-head">
        <button class="copy-btn" id="copy-btn">
          Copy notes <span class="count-pill" id="note-total">0</span>
        </button>
        <div class="copy-feedback" id="copy-feedback"></div>
      </div>
      <nav class="toc" aria-label="Sections">
        <ol id="toc-list"></ol>
      </nav>
      <div class="sidebar-notes" id="sidebar-notes" hidden>
        <h4>All notes</h4>
        <ol id="all-notes-list"></ol>
      </div>
    </aside>
  </div>
</body>
```

CSS grid for the shell:

```css
.app {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  grid-template-rows: auto 1fr;
  grid-template-areas: "topbar topbar" "content sidebar";
  min-height: 100vh;
}
.topbar { grid-area: topbar; position: sticky; top: 0; z-index: 50; }
.content { grid-area: content; max-width: 880px; padding: 1.25rem 2rem 4rem; margin: 0 auto; }
.sidebar { grid-area: sidebar; position: sticky; top: 56px; align-self: start;
  height: calc(100vh - 56px); overflow: auto;
  border-left: 1px solid var(--border); padding: 1rem 1.1rem; }

@media (max-width: 1100px) {
  .app { grid-template-columns: 1fr; grid-template-areas: "topbar" "sidebar" "content"; }
  .sidebar { position: static; height: auto; border-left: 0; border-bottom: 1px solid var(--border); }
}
```


## Section Block (static HTML, per H2)

Each H2 renders to this exact shape — the affordances are part of the static markup, not JS-injected.

```html
<section class="card" id="{{anchor}}" data-anchor="{{anchor}}" data-heading="{{verbatim H2}}">
  <header class="card-head">
    <h2>{{verbatim H2}}</h2>
    <div class="card-actions">
      <button type="button" class="btn-note"   data-act="note">+ Note <span class="note-count" data-role="count">0</span></button>
      <button type="button" class="btn-source" data-act="src">View source</button>
    </div>
  </header>

  <div class="card-body">
    {{rendered section content per template}}
  </div>

  <div class="note-area" hidden>
    <textarea placeholder="Note for &quot;{{verbatim H2}}&quot;…" rows="3"></textarea>
    <div class="note-controls">
      <button type="button" class="btn-primary" data-add>Add note</button>
      <button type="button" data-cancel>Cancel</button>
      <span class="hint">⌘/Ctrl + Enter</span>
    </div>
    <ol class="note-list"></ol>
  </div>

  <pre class="src-area" hidden></pre>
</section>
```

**Two non-negotiables in this block:**

1. **Both `id` and `data-anchor`** carry the same kebab value. `id` makes URL-fragment navigation work for the sidebar TOC and any linked-deep usage. `data-anchor` stays as the JS hook (cleaner querySelector, survives any future id-mangling). Without `id`, TOC links navigate the URL but don't scroll — a known regression.
2. **`+ Note` and `View source` buttons are present in the static HTML**, with the inline `note-count` span starting at `0`. JS only flips the `hidden` attribute on `.note-area` / `.src-area`, populates the source on first open, and updates the count. *Why both:* an empty `<div class="sec-actions">` placeholder is invisible at parse time and gone if JS fails. Inline buttons render in either case.

The `.note-area` and `.src-area` use the native `hidden` attribute (not `display: none` via class) so the toggle is a single attribute flip and the initial state is unambiguous in the markup.

**Affordance CSS (canonical — copy verbatim):**

```css
.card-actions { display: flex; gap: 0.45rem; align-items: center; }
.card-actions button {
  border-radius: var(--radius-sm);
  padding: 0.32rem 0.7rem; font-size: 0.78rem; line-height: 1.2;
  display: inline-flex; align-items: center; gap: 0.4rem;
  font-family: var(--ui); cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}
/* Primary affordance — accent-bordered, accent text. */
.btn-note {
  background: transparent; color: var(--accent);
  border: 1px solid rgba(110, 168, 255, 0.32);
  font-weight: 600;
}
.btn-note:hover { background: var(--accent-soft); color: var(--accent-strong); border-color: var(--accent); }
.btn-note .note-count {
  background: var(--accent); color: #061121;
  font-family: var(--mono); font-size: 0.68rem; font-weight: 700;
  min-width: 1.1rem; height: 1.1rem; padding: 0 0.32rem;
  border-radius: 999px;
  display: inline-flex; align-items: center; justify-content: center; line-height: 1;
}
.btn-note .note-count[data-empty="1"] {
  background: transparent; color: var(--text-faint);
  border: 1px solid var(--border);
}
/* Secondary affordance — muted, no fill. */
.btn-source {
  background: transparent; color: var(--text-muted);
  border: 1px solid var(--border);
}
.btn-source:hover { color: var(--text); border-color: var(--accent); background: var(--accent-soft); }
```

This locks the primary/secondary distinction so neither button drifts into "subtle muted gray" territory in future renders. Per-renderer per-section CSS may extend other classes; **don't override** `.btn-note` / `.btn-source` style.


## Sidebar Behavior

- **Copy button** at the top is the primary action. Disabled when `state.notes.length === 0`. Pill shows current note total. Inline feedback (`Copied · N notes`) appears below for 2.2s after a successful copy.
- **Section navigator** (`<ol id="toc-list">`) is JS-built from `section.card[id]` elements. Each `<a href="#{{anchor}}">` shows the heading text and a `note-count` badge that hides itself when count is 0 (`badge.empty { display: none }`). The currently-visible section gets `aria-current="true"` via `IntersectionObserver`.
- **All notes list** (`<ol id="all-notes-list">`) appears below the navigator only when `state.notes.length > 0` (`hidden` attribute toggled by JS). Each entry is a clickable card: heading verbatim, note text, timestamp, and a delete `×`. Click the heading to scroll to that section.
- **Sidebar visibility:** always visible ≥1100px; collapses to a stacked drawer at the top of the page below that. Never `display: none` the sidebar entirely — that re-introduces the original "TOC missing on laptops" bug.


## Renderer Discipline

Each H2 section dispatches to **one** specialized renderer (defined per artifact type in `templates/`) chosen by case-insensitive substring match on the heading. **Schema mismatch is the failure mode to avoid:** if a section's content does not fit a renderer's shape, fall back to **Generic Prose** (rendered markdown with `<h3>`/`<h4>`/`<p>`/`<ul>`/`<ol>`/`<table>`). Never repurpose a renderer for a different schema just because the heading sits in a similar position. Past renders have shipped Non-Functional Requirements as five empty `story-card` placeholders because the user-stories renderer was reused for a Category/Requirement/Threshold table.

**Per-section schema contract (PRD-shaped artifacts):**

| Section heading (substring) | Renderer | Source schema |
|---|---|---|
| Executive Summary | Capability cards + metric tiles | bulleted summary + Success Metrics table |
| Scope | Three-column kanban (In/Out/MVP) | H3 subsections with bullet lists |
| Functional Requirements | Story-grid + FR-card list | user-stories table + numbered FR sections |
| Non-Functional Requirements | **NFR rows** (canonical HTML/CSS below) | Category/Requirement/Threshold table |
| Edge Cases | Styled generic table | Scenario/Expected table |
| Constraints & Assumptions | Two-column constraints/assumptions + dependency cards | H3 subsections + Dependency table |
| Decisions Log | Decision cards (Decision title · Rationale · Alternatives footer) | Decision/Rationale/Alternatives table |
| Success Metrics (top-level) | Metric tiles | Metric/Target table |
| (anything else) | Generic Prose | as-is markdown |

*Source-schema notes:* renderer **names** match `templates/prd.md` headings; **column shapes** above match the canonical PRD template (`plugin/references/prd-template.md`). When the source markdown's columns don't match the documented shape, fall back to Generic Prose rather than ad-hoc-mapping unfamiliar columns into renderer slots — that's the regression this section exists to prevent. Trade-off, strategic-design, and clarification artifacts have their own per-section renderers in `templates/tradeoff.md` and `templates/clarification.md`; this table covers PRDs only.

**Section-block wrapper is universal.** Every H2 produces a `<section class="card" id="{anchor}">` block with the standard affordances (Note button, View source toggle, count span) per the *Section Block* contract above — that's true regardless of which renderer matched. The renderer choice only changes what fills `.card-body`. Generic Prose is **not** a permission to skip the wrapper or the affordances; it is a body-level fallback only.

**NFR Renderer (canonical):**

```html
<div class="nfr-grid">
  <div class="nfr-row">
    <span class="nfr-cat">{{category}}</span>
    <div class="nfr-body">
      <p class="nfr-req">{{requirement}}</p>
      <p class="nfr-target">{{threshold/target}}</p>
    </div>
  </div>
  <!-- one row per source row -->
</div>
```

```css
.nfr-grid { display: flex; flex-direction: column; gap: 0.55rem; }
.nfr-row { display: grid; grid-template-columns: 160px minmax(0, 1fr); gap: 0.85rem;
  background: var(--panel-2); border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm); padding: 0.7rem 0.9rem; align-items: start; }
.nfr-cat { font-family: var(--mono); font-size: 0.78rem; color: var(--accent); font-weight: 700; }
.nfr-body { display: flex; flex-direction: column; gap: 0.3rem; }
.nfr-req { margin: 0; color: var(--text); font-size: 0.92rem; line-height: 1.45; }
.nfr-target { margin: 0; color: var(--text-muted); font-size: 0.85rem;
  border-top: 1px dashed var(--border); padding-top: 0.4rem; }
@media (max-width: 700px) { .nfr-row { grid-template-columns: 1fr; gap: 0.4rem; } }
```

**Section-deduplication rule:** when a renderer consumes a structured part of a section (e.g. Executive Summary's `Success Metrics` table → metric tiles), *that part must not be emitted a second time as fallback prose*. The Executive Summary template rendering metric tiles AND a duplicate `<table>` AND an orphan `<ul><li><strong>Success Metrics</strong>:</li></ul>` is the named regression. **Mechanism:** the specialized renderer records the **source line range** it consumed (or the exact verbatim source text); the Generic Prose pass that fills the rest of `.card-body` skips any line range / text span already claimed. A renderer that consumes "the bullet whose text starts with `**Success Metrics**:` and the immediately-following pipe-table" must report both spans as consumed before prose fallback runs.


## JavaScript Authoring Discipline

The `<script>` block is the most fragile part of the render — a single SyntaxError disables every interactive affordance on the page (buttons stop responding, TOC stays empty, copy never wires). Three rules are non-negotiable:

1. **Never put literal newlines inside regex literals or single/double-quoted string literals.** `/.../` regex literals are syntactically single-line; `'...'` and `"..."` strings cannot contain raw newlines. Use `\n` (escape sequence) always. Template literals `` `...` `` *can* span lines, but inside them, newlines that need to appear in the output value must still be written as `\n` if you intend them as data — raw newlines become part of the literal value in ways that look fine but break adjacent regex/string code.

   **Anti-pattern (the regression):**
   ```javascript
   lines.push(`- ${note.text.replace(/
   /g, '
     ')}`);                              // SyntaxError: Invalid regular expression
   return lines.join('
   ');
   ```

   **Correct:**
   ```javascript
   lines.push(`- ${note.text.replace(/\n/g, '\n  ')}`);
   return lines.join('\n');
   ```

2. **Wrap the whole script in an IIFE** (`(function(){'use strict'; ... })();`) so a typo in one helper doesn't pollute window globals or silently shadow built-ins. The `'use strict'` directive surfaces accidental implicit-global assignments at parse time rather than as quiet bugs at runtime.

3. **Compose, don't re-derive.** The helpers under *Notes State Shape*, *Clipboard Write with Fallback*, *LocalStorage*, and *`beforeunload` Warning* below are the building blocks — the script body is one IIFE that wires them together with a small DOM layer (event handlers per `data-act` button, IntersectionObserver for `aria-current`, TOC builder over `section.card[id]`, all-notes list mirroring `state.notes`). Use the helpers as written; don't rename `state` / `notesDirty` / payload shape to fit a slicker style. The DOM-wiring layer is small but easy to get wrong — favor `hidden`-attribute toggles (Section Block contract), single-event-listener delegation per list, and `IntersectionObserver` with `rootMargin: '-20% 0px -70% 0px'` so the active-section indicator updates before the user reads the section heading.


## Section Anchor Scheme

Anchor key = lowercase-kebab of the verbatim H2 text:
- `Functional Requirements` → `functional-requirements`
- `Success Metrics` → `success-metrics`

Collisions resolved by suffix (`-2`, `-3`). Anchors are stable across re-runs as long as headings don't change.

The **payload uses the verbatim heading text**, not the kebab anchor — downstream skills match against their own headings without slug normalization.

**Nested H3 cards** (e.g. per-option cards inside a trade-off `## Options` section) carry `data-anchor-parent="<parent-anchor>"` purely as a CSS / DOM hook for layout; only H2 sections carry `data-anchor` and a Note affordance. One Note per H2 covers the whole section regardless of how many H3 cards it contains.


## Notes State Shape

Single state object. Every interaction reads/writes through it. Persist on every change.

```javascript
const state = {
  artifactPath: '<the path the user passed to the skill>',  // use as-given (typically project-relative); do NOT canonicalize to absolute — downstream skills receive this in the payload header and match against their own working-tree paths
  artifactSha1: '<sha-1 hex of artifactPath>',
  tabUuid: sessionStorage.getItem('andthen-visualize-tab-uuid') || (() => {
    const u = crypto.randomUUID();
    sessionStorage.setItem('andthen-visualize-tab-uuid', u);
    return u;
  })(),  // per-tab, stable across refresh; sessionStorage scope = tab lifetime
  notes: [
    {
      sectionAnchor: 'functional-requirements',
      headingVerbatim: 'Functional Requirements',
      text: 'Split FR-3 into FR-3a/FR-3b',
      createdAt: '2026-05-04T14:30:00Z'
    }
  ],
  notesDirty: false  // set to true on every add/edit/delete; reset to false ONLY after a successful clipboard copy
};
```

**`notesDirty` write sites** — set to `true` in every code path that mutates `state.notes` (add note, edit note text, delete note). The reset to `false` lives in the success branch of `copyNotes()` only. A second edit after a copy MUST flip the flag back to `true` so `beforeunload` re-arms.


## Notes Payload Format (exact)

When the user clicks "Copy notes" with N>0 notes attached, write this to clipboard:

```markdown
# andthen:visualize notes for <artifact-path>

## Section: <heading text verbatim>
- <note 1 text>
- <note 2 text>

## Section: <next heading verbatim>
- <note text>
```

Group consecutive notes by `sectionAnchor`, but use `headingVerbatim` in the rendered `## Section: ...` line. Preserve note order within each section.

If `notes.length === 0`, do not write to clipboard. Show inline "No notes to copy" near the button.


## Clipboard Write with Fallback

```javascript
async function copyNotes() {
  if (state.notes.length === 0) {
    flashInline('No notes to copy');
    return;
  }
  const payload = buildPayload(state.notes, state.artifactPath);
  try {
    await navigator.clipboard.writeText(payload);
    state.notesDirty = false;
    flashCopiedFeedback();
  } catch {
    revealTextareaFallback(payload);
  }
}
```

Textarea fallback: insert a visible `<textarea>` pre-populated with `payload`, focus it, call `.select()`, with the message *"Clipboard write blocked. Copy the payload below manually."*


## LocalStorage

Key scheme: `andthen:visualize:<artifactSha1>:<tabUuid>`

```javascript
function saveToLocalStorage() {
  try {
    const key = `andthen:visualize:${state.artifactSha1}:${state.tabUuid}`;
    localStorage.setItem(key, JSON.stringify({
      artifactPath: state.artifactPath,
      tabUuid: state.tabUuid,
      notes: state.notes,
      updatedAt: new Date().toISOString()
    }));
  } catch {}
}
```

On load, scan for any keys matching `andthen:visualize:<artifactSha1>:` from a *different* tabUuid. If found, prompt *"Restore previous notes?"* — accept copies them into `state.notes` and **sets `state.notesDirty = true`** so the `beforeunload` warning re-arms (the restored notes were never copied to clipboard *in this tab*; treating them as already-saved would let the user lose them on accidental tab close).

If LocalStorage is unavailable (private browsing): show a one-time warning at top of page — *"Note persistence disabled (private browsing?). Notes won't survive refresh."* Render proceeds.


## `beforeunload` Warning

```javascript
window.addEventListener('beforeunload', (e) => {
  if (state.notes.length > 0 && state.notesDirty) {
    e.preventDefault();
    e.returnValue = '';
  }
});
```

The standard browser warning shows. We don't customize the message — most browsers ignore custom strings.


## Browser-Open Detection (Bash)

After writing the HTML, run the OS-appropriate open command. On any failure, print the path with `Open this in your browser:` prefix and exit 0.

```bash
case "$(uname -s)" in
  Darwin*)            opener="open" ;;
  Linux*)             opener="xdg-open" ;;
  MINGW*|MSYS*|CYGWIN*|Windows_NT) opener='start ""' ;;
  *)                  opener="" ;;
esac
if [ -n "$opener" ] && command -v "${opener%% *}" >/dev/null 2>&1; then
  $opener "$html_path" >/dev/null 2>&1 || echo "Open this in your browser: $html_path"
else
  echo "Open this in your browser: $html_path"
fi
```


## Common Mistakes

- **Literal newlines in regex / quoted-string literals** → see *JavaScript Authoring Discipline* rule 1. The bullet exists here only so the failure mode (every button on the page goes inert; one regex SyntaxError disables the whole `<script>`) is searchable from the Common Mistakes index.
- **Reusing a renderer for a different schema** → emitting Non-Functional Requirements as five empty `story-card` placeholders happens when the user-stories `story-grid` renderer is dispatched against a Category/Requirement/Threshold table. Each section heading dispatches to **one** specialized renderer per the Renderer Discipline table, or falls back to Generic Prose. Structurally similar but semantically wrong renderers are *worse* than prose fallback because they ship empty card scaffolds.
- **Duplicate Success Metrics in Executive Summary** → emitting metric tiles AND a fallback `<table>` AND an orphan `<ul><li><strong>Success Metrics</strong>:</li></ul>` simultaneously is the named regression. When a specialized renderer consumes a structured part of the source, that span must be removed from the prose-fallback queue. See Section-deduplication rule.
- **Markdown italicizes `_blank` in `target="_blank"`** → unescaped underscores in raw markdown that pass through a Markdown→HTML pipeline get parsed as emphasis, leaving `target="<em>blank"` and `target="</em>blank"` in the output. Either emit the anchors directly as HTML (skip Markdown for the doc-meta block), or wrap underscore-bearing identifiers in code spans / HTML-escape the underscores. Same trap applies to any `snake_case` identifier in prose.
- **JS-injecting the `+ Note` / `View source` buttons** → they MUST be in the static HTML per the Section Block contract. An empty `<div class="sec-actions"></div>` placeholder renders nothing at parse time and stays invisible if JS fails. Past renders shipped this regression and users reported "no visible way to add notes."
- **Sections with `data-anchor` but no `id`** → URL-fragment navigation (TOC clicks, deep links) silently no-ops because `#anchor` resolves against `id`, not `data-*`. Always emit both attributes with the same kebab value.
- **TOC behind a `min-width: 1400px` media query** → hides the only navigation on every common laptop. The sidebar must remain reachable on narrow viewports — collapse it into a drawer above the content rather than display-none-ing it.
- **Subtle muted gray for primary affordances** → `+ Note` is the page's primary interaction; `View source` is secondary. The Section Block's *Affordance CSS* canonical block locks this — copy it verbatim and don't override `.btn-note` / `.btn-source` per-section.
- **External resources** (CDN scripts, web fonts, hosted icons) → must work from `file://`, inline everything.
- **`agent-browser`** → wrong tool. It's used by the `andthen:excalidraw-diagram` skill for *automation*. Visualize wants the user's *primary* browser.
- **Non-deterministic class names or DOM ordering** → keep section blocks ordered as in the source; class names follow the section anchor scheme.
- **Slug-normalizing the payload heading** → keep verbatim H2 text in the payload. Slugs are for in-page anchors only.
- **Dropping notes on copy success** → reset `notesDirty = false` but preserve `notes[]`. The user may keep editing.
- **Skipping LocalStorage** → refresh-loses-work is a real UX bug; persistence is mandatory.
- **Customizing the `beforeunload` message** → don't bother, browsers ignore it.
- **Hand-building HTML for diagrams from scratch each time** → use `templates/diagrams.md` for the coordinate math; it's the part most likely to be wrong.


## FOLLOW-UP ACTIONS

Skip this section when `AUTO_MODE=true` — print only the output path.

After the user reviews the rendered artifact and copies notes:

1. **Apply notes via downstream skill** — paste the clipboard payload into the chat when invoking the relevant downstream skill:
   - PRD review notes → `andthen:prd` (amendment context) or as conversational input to a fresh `andthen:plan` invocation
   - Clarification review notes → `andthen:clarify` amendment mode
   - Trade-off review notes → next `andthen:architecture` invocation (e.g. ADR formalization)
   - Strategic-design review notes → next `andthen:architecture` invocation (e.g. `--mode strategic-design` for refinement, `--mode fitness` to formalize, or `--mode decompose` for a contested boundary)
2. **Re-visualize after edits** — re-run `/andthen:visualize <path>` on the updated artifact to verify changes landed.
