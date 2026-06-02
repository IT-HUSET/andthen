# Visualize Render Shell

Canonical chrome shared by every artifact render: theme tokens, page layout, the section-block contract, cross-cutting component renderers, and the JavaScript layer (state, clipboard, persistence, payload). The per-artifact `templates/*.md` files fill `.card-body`; this file defines everything around them. Read it when emitting HTML. Copy CSS/HTML/JS blocks verbatim – they are tuned for AA contrast, `file://` operation, and SyntaxError-free scripts.

## Contents
- Theme Tokens
- Layout Skeleton
- KPI Summary Band
- Where-to-Focus Priority Section
- Section Block (static HTML, per H2)
- Sidebar Behavior
- Cross-cutting Component Renderers (NFR, risk-map, analysis collapse, TL;DR, section-dedup)
- JavaScript Authoring Discipline
- IIFE Helper Library
- Notes State Shape
- Notes Payload Formatters
- Clipboard Write with Fallback
- LocalStorage
- `beforeunload` Warning


## Theme Tokens

```css
:root {
  /* Surfaces – warm-light, three-tier depth (ivory page → white card → oat inset) */
  --bg: #FAF9F5;        /* warm ivory page */
  --panel: #FFFFFF;     /* card surface */
  --panel-2: #F5F1E6;   /* warm oat – inset, code, textarea */
  --panel-3: #EBE5D2;   /* deeper oat – chip surface, hover */
  --border: #D9D2BE;    /* warm gray border */
  --border-soft: #E8E2D0;

  /* Text – warm dark */
  --text: #1F1B17;        /* near-black with warm tint */
  --text-muted: #6B6557;
  --text-faint: #9C9583;

  /* Accents – clay coral for active/interactive, olive for resolved/done.
     Hex values are deepened for AA contrast against the ivory background
     (deeper than the dark-theme variants we used previously). */
  --accent: #C15F3C;                          /* clay coral; ~5.0:1 on #FAF9F5 */
  --accent-soft: rgba(193, 95, 60, 0.10);     /* hover surface, soft fills */
  --accent-strong: #A04A2A;                   /* darker for hover text */
  --ok: #6B8049;                              /* deep olive; resolved / done */
  --ok-soft: rgba(107, 128, 73, 0.10);
  --warn: #B07E2B;                            /* deep amber */
  --danger: #B5482B;                          /* rust – failure path semantics */

  /* Type – serif for headlines (Anthropic-warm), sans for body, mono for code/metadata */
  --serif: "Tiempos Headline", "Charter", "Iowan Old Style", Georgia, "Times New Roman", serif;
  --ui: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
  --mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;

  /* Geometry */
  --radius: 10px;
  --radius-sm: 6px;
  --shadow-1: 0 1px 0 rgba(255,255,255,0.6) inset, 0 1px 2px rgba(0,0,0,0.04);
  --shadow-2: 0 6px 24px rgba(0,0,0,0.06);
}
* { box-sizing: border-box; }
html, body { background: var(--bg); color: var(--text); }
body { font-family: var(--ui); margin: 0; line-height: 1.55; font-size: 15px; }
code, pre { font-family: var(--mono); }
```

The palette is a warm-ivory light theme inspired by Anthropic's product surfaces: ivory background (`#FAF9F5`), warm-dark slate text (`#1F1B17`), clay coral accent (`#C15F3C`), and deep olive (`#6B8049`) for resolved/done. The page reads as a *review surface* – editorial rather than IDE-shaped. Keep the three-tier surface system (`--bg → --panel → --panel-2`) for clear depth: ivory page, white card, warm oat inset for nested content (textareas, code blocks, secondary panels). Color is **load-bearing**: clay = active/interactive, olive = resolved/done, amber (`--warn`) = caution, rust (`--danger`) = failure, muted gray = structural. The reviewer's eye learns this within seconds and can navigate by color signal. **Headlines use `--serif`** (`.doc-title`, `.card-head h2`); body prose uses `--ui` sans; code, metadata pills, and KPI labels use `--mono`. This three-family typography is part of the Anthropic-warm aesthetic – drop one family and the visual identity flattens.

**Tokenization rule:** CSS variables cannot be interpolated inside `rgba()`. Where a soft-fill alpha variant is needed (e.g. chip backgrounds, sticky-topbar translucency), use the corresponding `*-soft` token (`--accent-soft`, `--ok-soft`) or a literal `rgba(R,G,B,A)` matching the parent token's RGB. Do **not** hardcode arbitrary hex/rgba values in renderers – pre-flight audit with `rg '#[0-9a-fA-F]{3,6}|rgba?\('` before shipping a palette change.


## Layout Skeleton

```html
<body>
  <div class="app">
    <header class="topbar">
      <div class="crumb">andthen:visualize · <strong>{{TYPE}}</strong> · {{basename}}</div>
      <div class="meta-pills">{{status, date, ...}}</div>
    </header>

    <main class="content">
      <header class="doc-header">
        <div class="eyebrow">{{ARTIFACT_TYPE_UPPERCASE}} · {{SUBTYPE}}</div>
        <h1 class="doc-title">{{H1}}</h1>
        <div class="doc-meta">
          <span class="meta-pill filled status-{{STATUS_KEBAB}}">
            <span class="k">status</span> <span class="v">{{STATUS}}</span>
          </span>
          <span class="meta-pill"><span class="k">sections</span> <span class="v">{{SECTION_COUNT}}</span></span>
          <span class="meta-pill"><span class="k">open Qs</span> <span class="v">{{OPEN_Q_COUNT}}</span></span>
          <span class="meta-pill"><span class="k">updated</span> <span class="v">{{LAST_UPDATED}}</span></span>
          <span class="meta-pill"><span class="k">sha</span> <span class="v">{{SHA1_SHORT}}</span></span>
        </div>
      </header>
      <!-- optional .kpi-band (see KPI Summary Band below) -->
      <!-- optional .focus-band (see Where-to-Focus Priority Section below) -->
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

/* Scroll hygiene – smooth in-page navigation and 24px breathing room above
   anchored elements so a freshly-scrolled-to target doesn't kiss the topbar. */
html { scroll-behavior: smooth; }
section.card { scroll-margin-top: 24px; }
.doc-header, .kpi-band, .focus-band { scroll-margin-top: 24px; }

/* Document header: eyebrow (artifact type) + H1 + status pill row.
   Survives scrolling past the topbar because it's part of the page header. */
.doc-header { margin: 0 0 1.25rem; }
.eyebrow {
  font-family: var(--mono); font-size: 0.72rem;
  text-transform: uppercase; letter-spacing: 0.08em;
  color: var(--text-faint); margin-bottom: 0.4rem;
}
.doc-title { margin: 0 0 0.7rem; font-size: 1.75rem; line-height: 1.2; font-family: var(--serif); font-weight: 600; letter-spacing: -0.005em; }
.doc-meta { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.meta-pill {
  display: inline-flex; align-items: baseline; gap: 0.35rem;
  font-family: var(--mono); font-size: 0.74rem;
  padding: 0.18rem 0.55rem; border-radius: 999px;
  border: 1px solid var(--border); color: var(--text-muted);
}
.meta-pill .k { color: var(--text-faint); }
.meta-pill .v { color: var(--text); }
/* Filled status pills – semantic per status-kebab class. */
.meta-pill.filled { border-color: transparent; }
.meta-pill.filled .k, .meta-pill.filled .v { color: inherit; }
/* Filled status pills carry ivory text against deepened accent fills (AA pass on warm-light theme). */
.meta-pill.status-draft      { background: var(--warn);       color: #FAF9F5; }
.meta-pill.status-review     { background: var(--accent);     color: #FAF9F5; }  /* clay – under active review */
.meta-pill.status-approved   { background: var(--ok);         color: #FAF9F5; }  /* olive – approved / accepted = resolved */
.meta-pill.status-done       { background: var(--ok);         color: #FAF9F5; }
.meta-pill.status-deferred   { background: var(--text-faint); color: var(--text); }
.meta-pill.status-deprecated { background: var(--danger);     color: #FAF9F5; }  /* rust – do not follow */
```


## KPI Summary Band

Sits between `.doc-header` and the first `<section class="card">`. Four-cell grid showing the document's most navigation-relevant counts. Per-artifact KPI cells are defined in each template's `## KPI Cells` section (PRD, plan, clarification, trade-off, strategic-design, ADR). One-glance picture of *what am I about to read*.

```html
<aside class="kpi-band" aria-label="Document KPIs">
  <div class="kpi-card">
    <div class="kpi-label">{{cell 1 label}}</div>
    <div class="kpi-value">{{N}}</div>
  </div>
  <div class="kpi-card">…</div>
  <div class="kpi-card attention">  <!-- .attention applied auto by renderer; see rule below -->
    <div class="kpi-label">{{cell 4 label}}</div>
    <div class="kpi-value">{{N}}</div>
  </div>
</aside>
```

```css
.kpi-band { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.6rem; margin: 0 0 1.5rem; }
.kpi-card { background: var(--panel); border: 1px solid var(--border-soft); border-radius: var(--radius-sm);
            padding: 0.7rem 0.9rem; }
.kpi-card.attention { border-left: 3px solid var(--accent); padding-left: calc(0.9rem - 3px); }
.kpi-label { font-family: var(--mono); font-size: 0.7rem; color: var(--text-faint);
             text-transform: uppercase; letter-spacing: 0.06em; }
.kpi-value { font-size: 1.4rem; font-weight: 600; color: var(--text); margin-top: 0.15rem; }
@media (max-width: 700px) { .kpi-band { grid-template-columns: repeat(2, 1fr); } }
```

**Auto-attention rule:** the renderer adds `.attention` to a KPI card when the cell semantically signals "needs review" – any non-zero count for Risks / Open Questions, or a Risk Level value that starts with `high` (case-insensitive). The rule is deterministic and per-cell: same source → same `.attention` placement.

**Source consumption:** KPI cells read **counts** (or a single recommended label) from already-structured source content (tables, bullet lists). They do **not** consume source spans – the section-dedup rule is unaffected. The same Risks table that drives a KPI count still renders as risk cards below.


## Where-to-Focus Priority Section

Sits in the main column between the `.kpi-band` and the first `<section class="card">`. Turns a 12-section document into a 3-priority walk by naming the *most important things to review and why*. It is **not** a Section Block: no `+ Note` affordance, no `View source`, no TOC entry, no `id` carrying a section anchor. The band is metadata *about* other sections and references them by anchor.

```html
<aside class="focus-band" aria-label="Where to focus your review">
  <h2 class="focus-band-title">Where to focus your review</h2>
  <ol class="focus-list">
    <li class="focus-item" data-priority="open-question">
      <div class="n">1</div>
      <div>
        <div class="t">Open question: How does retry interact with idempotency keys?</div>
        <div class="d">Unresolved – section <a href="#design-decisions">Design Decisions</a>. <code>owner: @tobias</code></div>
      </div>
    </li>
    <li class="focus-item" data-priority="high-risk">…</li>
    <li class="focus-item" data-priority="out-of-scope">…</li>
  </ol>
</aside>
```

```css
.focus-band { background: var(--panel-2); border: 1px solid var(--border-soft);
              border-radius: var(--radius); padding: 0.9rem 1.1rem 1.1rem; margin: 0 0 1.5rem; }
.focus-band-title { margin: 0 0 0.7rem; font-size: 0.85rem; text-transform: uppercase;
                    letter-spacing: 0.08em; color: var(--text-faint); font-family: var(--mono); }
.focus-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.55rem; }
.focus-item { display: grid; grid-template-columns: 26px minmax(0, 1fr); gap: 0.7rem; align-items: start; }
.focus-item .n { width: 26px; height: 26px; border-radius: 999px;
                 background: var(--accent); color: var(--bg);
                 font-family: var(--mono); font-size: 0.78rem; font-weight: 700;
                 display: inline-flex; align-items: center; justify-content: center; }
.focus-item .t { color: var(--text); font-weight: 600; }
.focus-item .d { color: var(--text-muted); font-size: 0.85rem; margin-top: 0.15rem; }
.focus-item .d a { color: var(--accent); }
.focus-item .d code { font-size: 0.78rem; color: var(--text-muted); background: var(--panel-3);
                       padding: 0.05rem 0.35rem; border-radius: 4px; }
```

**Deterministic priority heuristic** (cap 5 items; order = kind-priority, then source order within a kind):

1. **Unresolved Open Questions** – any bullet under `## Open Questions` not marked `(resolved)` / `→` / `lean:`, or any `**Open question:**` substring in a section body. Label: *"Open question: <text>"*.
2. **High-severity items** – `severity: high` / `risk: high` on a source line (case-insensitive, optional whitespace after the colon), or a Risks-table row whose Risk column starts with "High" (case-insensitive). Label: *"High risk: <row text>"*.
3. **Recommended trade-off with caveat** – the recommended option's body contains a line beginning `caveat:` / `risk:` / `however`. Label: *"Caveat on chosen option: <caveat text>"*.
4. **Long sections** – word count > 500 in the rendered section body. Label: *"Deep read: <heading> (~N words)"*.
5. **Out-of-Scope / Deliberately-Not-Doing** – bullets under H3 "Out of Scope" / "Not Doing". Label: *"<bullet text>"*.

**Omission rule:** if fewer than 2 items would render, omit the band entirely. A one-item focus list reads as noise.

**Source consumption:** the band is **read-only** with respect to source – it references headings via anchor links, never consumes spans. Section-dedup is unaffected.


## Section Block (static HTML, per H2)

Each H2 renders to this exact shape – the affordances are part of the static markup, not JS-injected. `plan.json` has no markdown headings, so `plan.md` derives virtual H2 sections from top-level JSON fields and then emits this same shape.

```html
<section class="card" id="{{anchor}}" data-anchor="{{anchor}}" data-heading="{{verbatim H2}}">
  <header class="card-head">
    <span class="h2-number">{{TWO_DIGIT_INDEX}}</span>
    <h2>{{verbatim H2}}</h2>
    <div class="card-actions">
      <button type="button" class="btn-note"     data-act="note">+ Note <span class="note-count" data-role="count">0</span></button>
      <button type="button" class="btn-source"   data-act="src">View source</button>
      <button type="button" class="btn-copy-sect" data-act="copy-sect">Copy section</button>
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

**Three non-negotiables in this block:**

1. **Both `id` and `data-anchor`** carry the same kebab value. `id` makes URL-fragment navigation work for the sidebar TOC and any linked-deep usage. `data-anchor` stays as the JS hook (cleaner querySelector, survives any future id-mangling). Without `id`, TOC links navigate the URL but don't scroll – a known regression.
2. **`+ Note`, `View source`, and `Copy section` buttons are present in the static HTML**, with the inline `note-count` span starting at `0`. JS only flips the `hidden` attribute on `.note-area` / `.src-area`, populates the source on first open, updates the count, and (for `Copy section`) writes the section payload to clipboard. Static per the Core Requirement (never empty `sec-actions` placeholders). With JS disabled, `Copy section` is visible but inert – acceptable per the Section Block contract: affordance present, interactivity gracefully degraded.
3. **`{{TWO_DIGIT_INDEX}}` is zero-padded, 1-based, source-order**. Determinism rule: the badge index must reflect the source's H2 ordinal at emission time. The same artifact rendered twice must produce identical badges (`01 02 03 …`). Re-orders in source change badges; nothing else does.

The `.note-area` and `.src-area` use the native `hidden` attribute (not `display: none` via class) so the toggle is a single attribute flip and the initial state is unambiguous in the markup.

**Renderer-specific modifier classes** may extend the base markup – e.g. ADR Alternatives emit `<section class="option adr-alt" …>` so a single CSS rule (`.option.adr-alt .option-body { grid-template-columns: 1fr; }`) can collapse the option-body's empty radar column without overriding `.option`'s base grid. The base Section Block contract (id + data-anchor + static affordances + numbered badge) is unchanged; per-renderer modifiers come from the artifact's template. Consult the active artifact template for its modifier list.

**Affordance CSS (canonical – copy verbatim):**

```css
.card-head { display: flex; align-items: baseline; gap: 0.65rem; }
.card-head h2 { flex: 1; margin: 0; font-family: var(--serif); font-weight: 600; font-size: 1.15rem; line-height: 1.3; letter-spacing: -0.005em; }
.h2-number {
  font-family: var(--mono); font-size: 0.72rem; font-weight: 700;
  background: var(--panel-3); color: var(--text-muted);
  padding: 0.15rem 0.45rem; border-radius: var(--radius-sm);
  letter-spacing: 0.04em;
  align-self: center; flex-shrink: 0;
}
.card-actions { display: flex; gap: 0.45rem; align-items: center; }
.card-actions button {
  border-radius: var(--radius-sm);
  padding: 0.32rem 0.7rem; font-size: 0.78rem; line-height: 1.2;
  display: inline-flex; align-items: center; gap: 0.4rem;
  font-family: var(--ui); cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}
/* Primary affordance – accent-bordered, accent text. */
.btn-note {
  background: transparent; color: var(--accent);
  border: 1px solid rgba(193, 95, 60, 0.32);  /* clay – matches --accent rgb */
  font-weight: 600;
}
.btn-note:hover { background: var(--accent-soft); color: var(--accent-strong); border-color: var(--accent); }
.btn-note .note-count {
  background: var(--accent); color: #FAF9F5;
  font-family: var(--mono); font-size: 0.68rem; font-weight: 700;
  min-width: 1.1rem; height: 1.1rem; padding: 0 0.32rem;
  border-radius: 999px;
  display: inline-flex; align-items: center; justify-content: center; line-height: 1;
}
.btn-note .note-count[data-empty="1"] {
  background: transparent; color: var(--text-faint);
  border: 1px solid var(--border);
}
/* Secondary affordance – muted, no fill. */
.btn-source, .btn-copy-sect {
  background: transparent; color: var(--text-muted);
  border: 1px solid var(--border);
}
.btn-source:hover, .btn-copy-sect:hover { color: var(--text); border-color: var(--accent); background: var(--accent-soft); }
.btn-copy-sect[data-copied="1"] { color: var(--ok); border-color: var(--ok); }
```

This locks the primary/secondary distinction so neither button drifts into "subtle muted gray" territory in future renders. Per-renderer per-section CSS may extend other classes; **don't override** `.btn-note` / `.btn-source` style.


## Sidebar Behavior

- **Copy button** at the top is the primary action. Disabled when `state.notes.length === 0`. Pill shows current note total. Inline feedback (`Copied · N notes`) appears below for 2.2s after a successful copy.
- **Section navigator** (`<ol id="toc-list">`) is JS-built from `section.card[id]` elements. Each `<a href="#{{anchor}}">` shows the heading text and a `note-count` badge that hides itself when count is 0 (`badge.empty { display: none }`). The currently-visible section gets `aria-current="true"` via `IntersectionObserver`. **H3 sub-anchors** (per the Section Anchor Scheme in SKILL.md) appear as nested `<li class="l2">` children indented under the parent H2 entry; clicking one navigates by anchor only (no Note affordance, no count badge). Style: `.toc li.l2 { padding-left: 1.1rem; font-size: 0.85em; color: var(--text-muted); }`.
- **All notes list** (`<ol id="all-notes-list">`) appears below the navigator only when `state.notes.length > 0` (`hidden` attribute toggled by JS). Each entry is a clickable card: heading verbatim, note text, timestamp, and a delete `×`. Click the heading to scroll to that section.
- **Sidebar visibility:** always visible ≥1100px; collapses to a stacked drawer at the top of the page below that. Never `display: none` the sidebar entirely – that re-introduces the original "TOC missing on laptops" bug.


## Cross-cutting Component Renderers

Shared renderers dispatched from any artifact template per the SKILL.md *Renderer Discipline* dispatch tables. The *when* lives there; the *how* (markup + CSS) lives here.

### NFR Renderer (canonical)

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

### Risk-map chips (summary-of-many)

Above any section that summarizes a list of items (trade-off Options, PRD Risks, clarification Open Questions), emit a `<nav class="risk-map">` row of `<a class="risk-map-chip">` anchor links – one chip per item. Chips are color-semantic: `.safe` (olive) for resolved / low-risk, `.medium` (warn amber), `.attention` (clay) for items needing review, `.neutral` (gray) for everything else. Each chip's `href` points to its target's anchor (`#options-foo`, etc.) and clicking pulses the target via the delegated `pulseAnchor` handler in the IIFE.

**Emission-time gap check (two-pass renderer required):** the gap check is against a pre-built anchor index, **not** the partially-emitted HTML stream. Pass 1 walks the parsed source, collects every section/H3 anchor it will eventually emit, and produces an anchor set. Pass 2 emits HTML; when it reaches a `.risk-map-chip`, it looks up the target href in the set built by Pass 1. When the target is missing (typo, dropped section, broken cross-reference), emit an inline HTML comment `<!-- risk-map: chip target "#X" not found -->` adjacent to the chip so the View-source panel surfaces the gap, and add `aria-disabled="true"` (plus `pointer-events: none` via the `.risk-map-chip[aria-disabled="true"]` CSS rule below) to the chip itself. A single-pass renderer cannot satisfy this rule – chips are emitted *above* the H3 list they reference, so the target IDs don't exist in the emitted stream yet.

```html
<nav class="risk-map" aria-label="{{section name}} overview">
  <a class="risk-map-chip safe"      href="#options-foo">Option Foo</a>
  <a class="risk-map-chip medium"    href="#options-bar">Option Bar</a>
  <a class="risk-map-chip attention" href="#options-baz">Option Baz</a>
</nav>
```

```css
.risk-map { display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 0 0 0.9rem; }
.risk-map-chip {
  display: inline-flex; align-items: center; gap: 0.35rem;
  font-family: var(--mono); font-size: 0.78rem;
  padding: 0.25rem 0.65rem; border-radius: 999px;
  text-decoration: none; border: 1px solid transparent;
}
.risk-map-chip.safe      { background: var(--ok-soft);     color: var(--ok);     border-color: var(--ok); }
.risk-map-chip.medium    { background: rgba(176, 126, 43, 0.10); color: var(--warn);   border-color: var(--warn); }   /* matches --warn rgb */
.risk-map-chip.attention { background: var(--accent-soft); color: var(--accent); border-color: var(--accent); }
.risk-map-chip.neutral   { background: var(--panel-2);     color: var(--text-muted); border-color: var(--border); }
.risk-map-chip[aria-disabled="true"] { opacity: 0.4; pointer-events: none; }
```

### Supporting-detail collapse (`<details class="analysis">`)

Inside section bodies that have a clear primary "verdict" followed by extended analysis (trade-off Option bodies, PRD Risk rows), wrap the *secondary* prose in a `<details class="analysis">` block. Native HTML, zero JS. Two conservative triggers – primary content stays uncollapsed by default:

1. An explicit `<!-- analysis -->` HTML comment marker in the source separates primary from secondary, OR
2. An H4 named `Detailed analysis`, `Notes`, or `Background` introduces the secondary block.

Without either marker, **nothing collapses** – never auto-split on heuristic content length.

```html
<details class="analysis">
  <summary>Show detailed analysis</summary>
  <!-- secondary prose / tables / nested elements -->
</details>
```

```css
.analysis { margin-top: 0.7rem; border-top: 1px dashed var(--border); padding-top: 0.5rem; }
.analysis > summary {
  cursor: pointer; font-family: var(--mono); font-size: 0.78rem;
  color: var(--text-muted); padding: 0.2rem 0; list-style: none;
}
.analysis > summary::before { content: '▸ '; color: var(--accent); }
.analysis[open] > summary::before { content: '▾ '; }
.analysis[open] { background: var(--panel-2); border-radius: var(--radius-sm);
                  padding: 0.5rem 0.7rem 0.7rem; }
```

### Light TL;DR callout (per-section)

Emit a `.tldr-light` block as the first child of `.card-body` **only** when the section's first body content matches one of two conservative patterns:

1. An explicit `> TL;DR:` blockquote line, OR
2. A *full italic paragraph* – a single line of the form `*Whole sentence.*` (or `_Whole sentence._`), followed by a blank line. A mid-prose italicized phrase does **not** match.

If matched, the source span is **consumed** (removed from the prose-fallback queue per the section-dedup rule below). If no match, no callout is emitted – never auto-extract an arbitrary leading sentence. Applies wherever a "verdict in one glance" surface is wanted: trade-off Option H3 cards, PRD Risk rows, clarification Open Question H3 blocks. Other sections may include one too if explicitly authored.

```html
<div class="tldr-light">
  <span class="k">TL;DR</span>
  <span class="v">{{verbatim summary sentence}}</span>
</div>
```

```css
.tldr-light {
  display: flex; gap: 0.7rem; align-items: baseline;
  background: var(--panel-2); border-left: 3px solid var(--accent);
  padding: 0.6rem 0.9rem; border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  margin: 0 0 0.85rem;
}
.tldr-light .k { font-family: var(--mono); font-size: 0.7rem; letter-spacing: 0.06em;
                 text-transform: uppercase; color: var(--accent); flex-shrink: 0; }
.tldr-light .v { color: var(--text); font-size: 0.95rem; line-height: 1.5; }
```

### Section-deduplication rule

When a renderer consumes a structured part of a section (e.g. Executive Summary's `Success Metrics` table → metric tiles), *that part must not be emitted a second time as fallback prose*. The Executive Summary template rendering metric tiles AND a duplicate `<table>` AND an orphan `<ul><li><strong>Success Metrics</strong>:</li></ul>` is the named regression. **Mechanism:** the specialized renderer records the **source line range** it consumed (or the exact verbatim source text); the Generic Prose pass that fills the rest of `.card-body` skips any line range / text span already claimed. A renderer that consumes "the bullet whose text starts with `**Success Metrics**:` and the immediately-following pipe-table" must report both spans as consumed before prose fallback runs.


## JavaScript Authoring Discipline

The `<script>` block is the most fragile part of the render – a single SyntaxError disables every interactive affordance on the page (buttons stop responding, TOC stays empty, copy never wires). Three rules are non-negotiable:

1. **Never put literal newlines inside regex literals or single/double-quoted string literals.** `/.../` regex literals are syntactically single-line; `'...'` and `"..."` strings cannot contain raw newlines. Use `\n` (escape sequence) always. Template literals `` `...` `` *can* span lines, but inside them, newlines that need to appear in the output value must still be written as `\n` if you intend them as data – raw newlines become part of the literal value in ways that look fine but break adjacent regex/string code.

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

3. **Compose, don't re-derive.** The helpers under *Notes State Shape*, *Clipboard Write with Fallback*, *LocalStorage*, *`beforeunload` Warning*, and `js-helpers.md` (interactive-affordance helpers: `pulseAnchor`, `copySectionWithNote`, walkthrough snippet toggle, `wireModuleMap`) are the building blocks – the script body is one IIFE that wires them together with a small DOM layer (event handlers per `data-act` button, IntersectionObserver for `aria-current`, TOC builder over `section.card[id]`, all-notes list mirroring `state.notes`). Use the helpers as written; don't rename `state` / `notesDirty` / payload shape to fit a slicker style. The DOM-wiring layer is small but easy to get wrong – favor `hidden`-attribute toggles (Section Block contract), single-event-listener delegation per list, and `IntersectionObserver` with `rootMargin: '-20% 0px -70% 0px'` so the active-section indicator updates before the user reads the section heading.


## IIFE Helper Library

The four interactive-affordance helpers (`pulseAnchor`, `copySectionWithNote`, walkthrough one-at-a-time snippet toggle, `wireModuleMap`) live in `js-helpers.md` – copy them verbatim into the page-level IIFE alongside `state`, `copyNotes`, `flashInline`, `saveToLocalStorage`, and the `beforeunload` handler. Each helper is `try/catch`-wrapped so one handler failure cannot disable any other. See `js-helpers.md` for the code, the module-map JSON script discipline, and binding-site comments.


## Notes State Shape

Single state object. Every interaction reads/writes through it. Persist on every change.

```javascript
const state = {
  artifactPath: '<the path the user passed to the skill>',  // use as-given (typically project-relative); do NOT canonicalize to absolute – downstream skills receive this in the payload header and match against their own working-tree paths
  artifactOwner: '<andthen:prd|andthen:plan|andthen:spec|andthen:clarify|andthen:review|andthen:architecture>',
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

**`notesDirty` write sites** – set to `true` in every code path that mutates `state.notes` (add note, edit note text, delete note). The reset to `false` lives in the success branch of `copyNotes()` only. A second edit after a copy MUST flip the flag back to `true` so `beforeunload` re-arms.


## Notes Payload Formatters

The exact markdown payload format is the downstream contract – see *Notes Payload Format* in SKILL.md. These formatters produce it (compose, don't re-derive – `copySectionWithNote` in `js-helpers.md` reuses `buildSectionBlock`):

```javascript
function buildSectionBlock(headingVerbatim, notesForSection) {
  // One '## Section: …' block. Empty-notes case = heading line only, no bullets.
  var lines = ['## Section: ' + headingVerbatim.trim(), ''];
  notesForSection.forEach(function (n) {
    // Multi-line notes: continuation lines indent by 2 spaces (markdown list-item continuation).
    lines.push('- ' + n.text.replace(/\n/g, '\n  '));
  });
  return lines.join('\n');
}
function buildPayload(notes, artifactPath, artifactOwner) {
  var header = '# ' + artifactOwner + ' visual review notes for ' + artifactPath + '\n';
  // Group by sectionAnchor, preserve first-seen order, use headingVerbatim from the first note in each group.
  var groups = [];
  var byAnchor = Object.create(null);
  notes.forEach(function (n) {
    if (!byAnchor[n.sectionAnchor]) {
      byAnchor[n.sectionAnchor] = { heading: n.headingVerbatim, items: [] };
      groups.push(byAnchor[n.sectionAnchor]);
    }
    byAnchor[n.sectionAnchor].items.push(n);
  });
  return header + '\n' + groups.map(function (g) {
    return buildSectionBlock(g.heading, g.items);
  }).join('\n\n') + '\n';
}
```


## Clipboard Write with Fallback

```javascript
async function copyNotes() {
  if (state.notes.length === 0) {
    flashInline('No notes to copy');
    return;
  }
  const payload = buildPayload(state.notes, state.artifactPath, state.artifactOwner);
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
      artifactOwner: state.artifactOwner,
      tabUuid: state.tabUuid,
      notes: state.notes,
      updatedAt: new Date().toISOString()
    }));
  } catch {}
}
```

On load, scan for any keys matching `andthen:visualize:<artifactSha1>:` from a *different* tabUuid. If found, prompt *"Restore previous notes?"* – accept copies them into `state.notes` and **sets `state.notesDirty = true`** so the `beforeunload` warning re-arms (the restored notes were never copied to clipboard *in this tab*; treating them as already-saved would let the user lose them on accidental tab close).

If LocalStorage is unavailable (private browsing): show a one-time warning at top of page – *"Note persistence disabled (private browsing?). Notes won't survive refresh."* Render proceeds.


## `beforeunload` Warning

```javascript
window.addEventListener('beforeunload', (e) => {
  if (state.notes.length > 0 && state.notesDirty) {
    e.preventDefault();
    e.returnValue = '';
  }
});
```

The standard browser warning shows. We don't customize the message – most browsers ignore custom strings.
