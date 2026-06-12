---
description: Use when reviewing an existing AndThen artifact visually – PRD, plan.json, requirements-clarification, product vision, FIS (feature implementation spec), review report (any lens), changeset walkthrough, architecture review / trade-off / strategic-design / fitness / decompose / event-storming report, or ADR. Renders a self-contained HTML view in the user's browser, captures section-anchored notes, and exports them as a markdown payload via clipboard. Trigger on 'review visually', 'visualize this prd', 'visualize this plan', 'visualize this fis', 'visualize this review', 'visualize this walkthrough', 'visualize this clarification', 'visualize trade-off', 'andthen visualize'.
argument-hint: "<path-to-artifact>"
user-invocable: true
---

# Visualize Workflow Artifact

Supported artifacts: PRD, `plan.json`, Feature Implementation Specification (FIS), `requirements-clarification.md`, product vision, review report (any `andthen:review` lens or `andthen:architecture --mode review` output), changeset walkthrough (`andthen:explain-changes` output), architecture trade-off report, architecture strategic-design report, architecture fitness-functions report, architecture decompose report, architecture event-storming report, and ADR.

**Open-loop by design:** emit HTML, open browser, exit. The skill does not block waiting for user interaction.

**Read-only by contract:** reads one artifact, writes a separate HTML review surface, never edits the source.

## Contents
- When to Use
- How to Use
- Artifact Type Detection
- Artifact Owner Identity
- Core Requirements (every render)
- Renderer Discipline
- Section Anchor Scheme
- Notes Payload Format (exact)
- Browser-Open Detection (Bash)
- Common Mistakes
- FOLLOW-UP ACTIONS


## When to Use

Use to eyeball any supported artifact (see Supported artifacts above) before handing it to its consuming skill, or to verify one retrospectively.


## How to Use

1. Read the artifact at `$1`.
2. Detect the artifact type by content (filename advisory only) – see *Artifact Type Detection*.
3. Read `templates/render-shell.md` – the shared chrome (theme tokens, layout skeleton, section-block contract, cross-cutting component renderers, and the JavaScript layer). Every render uses it.
4. Load the matching per-artifact template from `templates/`:
   - `templates/prd.md` for PRDs
   - `templates/plan.md` for local `plan.json` bundles
   - `templates/fis.md` for Feature Implementation Specifications (FIS)
   - `templates/clarification.md` for `requirements-clarification.md` and product vision artifacts
   - `templates/review-report.md` for review reports from the `andthen:review` skill (any lens) or architecture-review reports from `andthen:architecture --mode review`
   - `templates/changeset.md` for changeset walkthroughs from the `andthen:explain-changes` skill
   - `templates/tradeoff.md` for architecture trade-off reports
   - `templates/strategic-design.md` for architecture strategic-design reports
   - `templates/fitness.md` for architecture fitness-functions reports
   - `templates/decompose.md` for architecture decompose reports
   - `templates/event-storming.md` for architecture event-storming reports
   - `templates/adr.md` for ADRs (Architecture Decision Records)
   - `templates/diagrams.md` for inline-SVG diagram patterns (`flowchart`, `timeline`, `tree`, `radar`, `list-graph`, `module-map`, `walkthrough`) referenced by the templates above
   - `templates/js-helpers.md` for the four IIFE interactive-affordance helpers (`pulseAnchor`, `copySectionWithNote`, walkthrough snippet toggle, `wireModuleMap`)
5. Generate a single self-contained HTML file at `.agent_temp/visual-review/<slug>-<timestamp>.html`. Resolve the path against the repo root (`git rev-parse --show-toplevel`) when inside a git working tree, falling back to CWD when there is no repo. `<slug>` is the basename without extension; `<timestamp>` is `YYYYMMDD-HHMMSS`.
6. Open the file in the user's browser via the OS-detected command (see *Browser-Open Detection*).
7. Print the output path and exit. Do not block on user interaction.


## Artifact Type Detection

Run heuristics in order; first match wins. **Filename hints are advisory only – content decides.**

| Type | Markers |
|---|---|
| `plan` | Valid JSON object with `schemaVersion === "1"`, `overview`, and `stories` array. *Ordered before markdown heuristics because `plan.json` has no H1/H2 headings. If JSON parses but these keys are missing, do not fall through to markdown detection – report unsupported JSON artifact shape. If the keys are present but `schemaVersion` is not `"1"`, stop with `andthen:visualize: unsupported plan.json schemaVersion "<value>"` and write no HTML.* |
| `fis` | H2 contains "Feature Overview and Goal" AND (H2 contains "Implementation Plan" OR H2 contains "Acceptance Scenarios" OR H2 contains "Structural Criteria"). *The `Feature Overview and Goal` H2 is unique to FIS in the AndThen canon (canonical PRDs use `## Executive Summary` + `## Functional Requirements`; canonical clarifications use `## Decisions Log`). Ordering ahead of `prd` is defensive in case an off-canonical PRD ever borrows FIS section names.* |
| `prd` | H1 contains "PRD" or "Product Requirements"; H2 contains both "Executive Summary" and "Functional Requirements" |
| `clarification` | H1 starts with "Requirements Clarification"; H2 contains "Decisions Log" |
| `product-vision` | H1 starts with "Product Vision" or H1 contains "Product"; H2 set contains at least two of "Vision", "Problem Statement", "Target Users & Personas", "Value Propositions", "Anti-Goals", "Roadmap Themes" |
| `changeset-walkthrough` | H1 starts with "Changeset Walkthrough"; OR H2 set contains BOTH "Change Map" AND "Change Narrative". *Both marker pairs are unique in the AndThen canon; ordered before the report family defensively since walkthroughs may carry an "Architectural Delta" H2.* |
| `event-storming` | H1 or H2 contains "Event Storming" / "Event-Storming" (case-insensitive); OR H2 set contains BOTH "Event Timeline" AND ("Hotspots" OR "Commands and Actors"). *Ordered before `strategic-design` because event-storming reports may carry "Subdomain Candidates" as a Big-Picture output; the Event-Timeline marker wins first.* |
| `fitness` | H1 contains "Fitness Functions" / "Fitness Function" (case-insensitive); OR H2 set contains BOTH "Proposed Fitness Functions" AND ("ADR Gap Analysis" OR "Current Governance Coverage" OR "Prioritized Implementation Roadmap"). *The H2 branch requires the fitness-mode-specific discriminator (ADR Gap Analysis / Governance Coverage / Implementation Roadmap) – not just "Fitness Functions" alone – because an architecture **review** report also carries a `## Proposed Fitness Functions` section (per `mode-review.md`'s report-contents list) and must NOT mis-detect as a fitness report. Ordered before `strategic-design` and `tradeoff` because all share `Executive Summary` + `How to Read This Report`.* |
| `decompose` | H1 or H2 contains "Decompose" / "Decomposition Analysis" (case-insensitive); OR H2 set contains ("Driver Scores" OR "Boundary Map") AND "Recommendation" AND **no scoring-matrix table is present** (the scoring-matrix exclusion disambiguates from `tradeoff`). |
| `strategic-design` | H1 contains "Strategic Design" / "Strategic-Design"; OR H2 set contains both "Subdomains" and "Context Map" (case-insensitive). *Ordered before `tradeoff` because both report shapes share `Executive Summary` + `How to Read This Report`; the more-specific marker pair wins under first-match-wins.* |
| `adr` | H1 matches `/^ADR[-\s]?\d/` (e.g. "ADR-011:", "ADR 11:", "ADR011:"); OR (H2 set contains "Decision" AND ("Consequences" OR "Alternatives Considered") AND **no scoring-matrix table is present**) (case-insensitive). *Ordered before `tradeoff` because both share the "Decision" concept. The scoring-matrix exclusion in the H2-set branch is what disambiguates: trade-off reports always carry a scoring matrix, ADRs never do.* |
| `tradeoff` | H1 or H2 contains "Trade-off" / "Trade off" / "Decision Analysis"; presence of a scoring matrix table (rows = options, columns = criteria) |
| `architecture-review` | H1 contains "Architecture Review" as a phrase; AND H2 set contains "Executive Summary"; AND H2 set contains at least one of "Findings", "Metrics Dashboard", or "Proposed Fitness Functions". *Uses `templates/review-report.md`, but note ownership routes back to the `andthen:architecture` skill instead of the generic review/remediation loop.* |
| `review-report` | H1 contains "Review" as a standalone word (case-insensitive – e.g. "Doc Review", "Code Review", "Council Review"); AND H2 set contains "Executive Summary"; AND H2 set contains at least one of "Findings", "Verdict", "Readiness Assessment", "Metrics Dashboard". *Last among markdown reports because review reports overlap structurally with `tradeoff`, `fitness`, and `decompose` (all share `Executive Summary` + recommendation language). The "Review" H1 + Findings/Verdict marker pair is the discriminator.* |

If no match, exit with the message *"andthen:visualize: cannot detect artifact type. Supported: PRD (`prd.md`), `plan.json`, FIS, `requirements-clarification.md`, product vision, review reports (any lens), changeset walkthroughs, architecture review / trade-off / strategic-design / fitness / decompose / event-storming reports, ADRs (`NNN-title.md` with `# ADR-NNN:` H1)."* and write no HTML.


## Artifact Owner Identity

The renderer owns HTML production, but copied notes identify the skill that owns the source artifact so downstream routing is clear:

| Detected type | Notes header owner |
|---|---|
| `prd` | `andthen:prd` |
| `plan` | `andthen:plan` |
| `fis` | `andthen:spec` |
| `clarification`, `product-vision` | `andthen:clarify` |
| `architecture-review`, `tradeoff`, `strategic-design`, `fitness`, `decompose`, `event-storming`, `adr` | `andthen:architecture` |
| `review-report` | `andthen:review` |
| `changeset-walkthrough` | `andthen:explain-changes` |

Use the owner in the copied payload header: `# <owner> visual review notes for <artifact-path>`.

Owner = who maintains the source artifact, not the consumption target for the copied payload (FOLLOW-UP ACTIONS routing is authoritative for where notes go – notably review-report notes feed `andthen:remediate-findings`, not `andthen:review`). The header is human/prompt-readable, not structurally parsed; pasting the markdown body into the chat alongside the consuming skill invocation is the contract.


## Core Requirements (every render)

These are contracts. The HTML/CSS/JS that satisfies them lives in `templates/render-shell.md` – read it before emitting.

- **Single self-contained HTML file.** All CSS, JS, and SVG inlined. No external scripts, fonts, stylesheets, icons. Must work from `file://` with no network access.
- **Warm light theme (Anthropic-style).** Ivory background, warm-dark slate text, clay coral accent, olive for resolved/done. Serif for headlines, sans for body, mono for code and metadata. Use the theme tokens in `templates/render-shell.md`.
- **Two-pane layout.** Left = scrollable artifact content; right = sticky sidebar holding the **Copy notes** button (top), section navigator with note-count badges, and a unified note list. The sidebar is always visible at viewports ≥1100px and collapses to a top drawer below that. *Why:* a floating-TOC-only layout hides nav on laptop widths and buries affordances where users miss them. *Exception:* `changeset-walkthrough` renders as a tabbed interactive app, not a document – produced by the bundled deterministic renderer (`scripts/render-changeset.mjs`, invoked per `templates/changeset.md`), never hand-authored; the notes machinery and affordance contracts in this list are built into its output.
- **Static affordances, JS-attached handlers.** The `+ Note` button, `View source` toggle, and per-section note-count span MUST be present in the static HTML body of each `<section>`. JavaScript only attaches click handlers and renders the dynamic note list. *Why:* if JS fails, errors out, or is delayed, the user must still see *that* notes are possible. Empty `<div class="sec-actions"></div>` placeholders waiting for JS injection are a known regression – never ship them.
- **Read-only render + section-anchored notes.** No structured editing. One Note affordance + one View-source toggle per H2 section. Diagrams do not get their own Note affordance – the parent section's Note covers any diagram inside it.
- **Notes payload via clipboard.** "Copy notes" writes a markdown payload via `navigator.clipboard.writeText`; on failure, reveals a textarea with payload pre-selected for manual copy.
- **LocalStorage persistence.** Notes survive refresh; "Restore previous notes?" prompt on reload when a matching prior session exists.
- **`beforeunload` warning.** Fires when notes exist and have not been copied since last edit.


## Renderer Discipline

Each markdown H2 section, or plan virtual H2 section, dispatches to **one** specialized renderer (defined per artifact type in `templates/`) chosen by case-insensitive substring match on the heading. **Schema mismatch is the failure mode to avoid:** if a section's content does not fit a renderer's shape, fall back to **Generic Prose** (rendered markdown with `<h3>`/`<h4>`/`<p>`/`<ul>`/`<ol>`/`<table>`). Never repurpose a renderer for a different schema just because the heading sits in a similar position. Past renders have shipped Non-Functional Requirements as five empty `story-card` placeholders because the user-stories renderer was reused for a Category/Requirement/Threshold table.

**Per-section schema contract (PRD-shaped artifacts):**

| Section heading (substring) | Renderer | Source schema |
|---|---|---|
| Executive Summary | Capability cards + metric tiles | bulleted summary + Success Metrics table |
| Scope | Three-column kanban (In/Out/MVP) | H3 subsections with bullet lists |
| Functional Requirements | Story-grid + FR-card list | user-stories table + numbered FR sections |
| Non-Functional Requirements | **NFR rows** (canonical HTML/CSS in `templates/render-shell.md`) | Category/Requirement/Threshold table |
| Edge Cases | Styled generic table | Scenario/Expected table |
| Constraints & Assumptions | Two-column constraints/assumptions + dependency cards | H3 subsections + Dependency table |
| Decisions Log | Decision cards (Decision title · Rationale · Alternatives footer) | Decision/Rationale/Alternatives table |
| Success Metrics (top-level) | Metric tiles | Metric/Target table |
| (anything else) | Generic Prose | as-is markdown |

*Source-schema notes:* renderer **names** match `templates/prd.md` headings; **column shapes** above match the canonical PRD template (`plugin/references/prd-template.md`). When the source markdown's columns don't match the documented shape, fall back to Generic Prose rather than mapping unfamiliar columns into renderer slots. Trade-off, strategic-design, and clarification artifacts have their own per-section renderers in `templates/tradeoff.md`, `templates/strategic-design.md`, and `templates/clarification.md`; this table covers PRDs only.

**Cross-artifact dispatch (renderers shared across templates).** Three structural renderers live in `templates/diagrams.md` and may be dispatched from any artifact's template based on the heading + source-shape conditions below. Heading-substring match still wins over shape detection; mapviz wins over walkthrough wins over flowchart for the same heading.

| Artifact | Section heading (substring) | Renderer dispatch (priority order) |
|---|---|---|
| Plan | Overview | Summary prose + phase/wave timeline from `overview.phases[]` |
| Plan | Story Catalog | Story cards with status/risk/FIS/dependency chips; `.risk-map` links to story sub-anchors |
| Plan | Dependency Graph | Phase/wave lanes plus dependency edge list; invalid `dependsOn` references surface as inline comments and attention styling |
| Plan | Shared Decisions / Binding Constraints / Risk Summary / Execution Notes | Purpose-built card renderers from `templates/plan.md`; omit optional virtual sections when source arrays/strings are empty |
| PRD | User Flows | (1) `mapviz` fenced block → Module Map · (2) 2–9 H3 substeps where **every** substep's stripped body char-count ≥ 50 → Walkthrough · (3) else → Flowchart. (Character count: strip whitespace and markdown markers, count Unicode code points – see `templates/prd.md` for the rule.) |
| PRD | Risks | Risk rows + `.risk-map` chips + `<details class="analysis">` collapse |
| Clarification | Design Decisions → Resolved Decisions H3 | If ≤5 rows AND every Rationale's stripped char-count ≥ 60 → Walkthrough; else current tree+notes+table |
| Trade-off | Options → all option H3s together | If **every** option H3 carries ≥ 2 of {`What changes`, `Where it changes`, `Risk` / `Trade-off`} H4 substring → Walkthrough alongside radar for every option; else prose+radar for every option. All-or-nothing per section – never mixed |
| Trade-off | Options summary | `.risk-map` chips above the H3 list |
| Strategic-design | Context Map | `mapviz` → Module Map + interactive node→panel binding; else Generic Prose |
| Strategic-design | Bounded Contexts | per-context `mapviz` → Module Map; else card grid |
| Strategic-design | Subdomains | Card grid (reuse `list-graph` styling); else Generic Prose |
| ADR | Context | Generic Prose; inline `**Status:** …` / `**Date:** …` / `**Deciders:** …` / `**Related:** …` metadata consumed into eyebrow + pill row |
| ADR | Decision | Recommendation-styled accent box (reuse `templates/tradeoff.md` `.recommendation` styling); code blocks render verbatim |
| ADR | Alternatives Considered | Option cards (reuse `templates/tradeoff.md` `.option` layout, **no radar** since ADRs lack scoring matrices); emit each alternative as `<section class="option adr-alt" data-anchor-parent="alternatives-considered">` so `.option.adr-alt .option-body { grid-template-columns: 1fr; }` collapses the absent-radar column. One H3 per alternative |
| ADR | Consequences | Semantic three-bucket layout (Positive / Negative / Neutral) when H3 subsections match `/^(positive|negative|neutral|trade.?offs?)/i`; else Generic Prose with H3 carrying olive / danger / muted accents |
| FIS | Acceptance Scenarios | Checkbox cards parsed against the canonical scenario shape (see `templates/fis.md` *Acceptance Scenarios → Checkbox cards* for the parser definition); Given/When/Then bullets render as a 3-step walkthrough; per-card task-tag chips backlink to Implementation Plan task cards |
| FIS | Structural Criteria | Non-behavioral checklist – `- [ ]` / `- [x]` bullets render as disabled checkboxes (reuse clarification checklist renderer); unchecked items fold into KPI cell 3 ("Open Items") alongside unchecked tasks and unchecked FVC items |
| FIS | Implementation Plan | Task walkthrough (`diagrams.md#walkthrough`) over the canonical task shape; per-task Verify line surfaces as an olive-accented footer; Testing Strategy, Validation, and Execution Contract sub-H3s render below with chip-backlinks to task cards (often empty – render muted note when only the placeholder is present) |
| FIS | Required Context | Source-pinned block cards parsing the `<!-- source:` / `<!-- extracted:` HTML comment pair; the inlined blockquote becomes the body |
| FIS | Code Patterns & External References | Type/path/intent table parsed from the fenced code block; type column color-coded (file = accent, url = link, wire = muted) |
| Review | Findings | Risk-map chips (color-coded by severity) above + Finding cards below; field parser handles both `### Finding N - SEVERITY - Title` (review-skill shape) and `### ARCH-NNN: Title` (architecture shape); council-mode subsections nest cards under reviewer/lens H3 dividers |
| Review | Verdict / Readiness Assessment | Gap-mode PASS/FAIL table (canonical dimensions/score/threshold/status block); other lenses render the readiness label as a single chip |
| Review | Metrics Dashboard | Per-package metrics table; Zone of Pain / Uselessness rows highlighted by `D` threshold |
| Review | Proposed Fitness Functions | Reuses `fitness.md` `.fitness-card` / `.fitness-lanes` renderer when the section is present in an architecture review report |
| Changeset | (whole artifact) | Bundled deterministic renderer – run `node "${CLAUDE_SKILL_DIR}/scripts/render-changeset.mjs" <artifact> <output>` per `templates/changeset.md`; never hand-author this type's HTML (hand-authored attempts produce broken SVG layout and dead scripts). Document-shell fallback only when Node is unavailable |
| Fitness | Proposed Fitness Functions | Four-level lanes (L1 commit / L2 PR / L3 nightly / L4 prod) with per-proposal cards; severity chips reuse review-report styling |
| Fitness | ADR Gap Analysis | ADR cards with `data-gap` chips (open / partial / enforced); cross-links to the Proposed Fitness Functions cards |
| Decompose | Driver Scores | Two-radar pair (6 disintegration + 4 integration axes per Ford/Richards) alongside a driver-score table with strong/moderate/weak/N-A chips |
| Decompose | Connascence Analysis | Per-boundary connascence cards with type chip (CoN/CoT/.../CoI), dynamic vs static, severity score |
| Decompose | Evaluation Matrix | 4-criteria PASS/FAIL checklist (a+b+c required for Split) |
| Decompose | Recommendation | Verdict chip (Split / Merge / Keep / Defer) inside the reused tradeoff `.recommendation` accent box; decomposition triggers list for Defer verdicts |
| Event-storming | Event Timeline | Horizontal sticky-note strip (orange `.kind-event`); pivotal events accented; per-event H3 sub-anchors enable backlinking from Subdomain Candidates |
| Event-storming | Commands and Actors | Sticky-note pairs grid (blue command + yellow actor); unattributed commands flagged with a purple "no actor" placeholder |
| Event-storming | Policies and Read Models | Two-column grid (lilac policies / green read models); Process Modeling and Design Level only |
| Event-storming | Hotspots | Purple sticky-note cards with route hint to follow-up modes (vocabulary conflicts → `andthen:ubiquitous-language`) |
| Event-storming | Subdomain Candidates / Workflow Boundaries / Aggregate Candidates | Per-candidate cards anchored on the pivotal-event cluster they emerged from; subdomain type chip (core / supporting / generic) |
| Event-storming | Recommended Next Steps | Visual hand-off chips for the level-appropriate next mode (`--mode strategic-design`, `--mode decompose`, `andthen:ubiquitous-language`, `andthen:excalidraw-diagram`) |

**DDD relationship vocabulary** recognized in `mapviz` edge labels (annotated, not parsed for layout): `Customer-Supplier`, `Conformist`, `Anti-Corruption Layer`, `Open Host`, `Published Language`, `Partnership`, `Shared Kernel`, `Separate Ways`. Convention: `Separate Ways` → dashed edge style; `Anti-Corruption Layer` target node should be `terminal`.

**Section-block wrapper is universal.** Every markdown H2, plus every plan virtual H2, produces a `<section class="card" id="{anchor}">` block with the standard affordances (Note button, View source toggle, count span) per the *Section Block* contract in `templates/render-shell.md` – that's true regardless of which renderer matched. The renderer choice only changes what fills `.card-body`. Generic Prose is **not** a permission to skip the wrapper or the affordances; it is a body-level fallback only.

**Cross-cutting render components** (markup + CSS in `templates/render-shell.md` → *Cross-cutting Component Renderers*). The dispatch tables above say *when*; the shell defines *how* and the correctness rules:

- **NFR rows** – Category/Requirement/Threshold tables (never the user-stories renderer).
- **Risk-map chips** – summary-of-many anchor rows above Options / Risks / Open-Questions lists. **Two-pass renderer required:** build an anchor index in pass 1, validate chip targets against it in pass 2, flag misses with an inline comment + `aria-disabled`. A single-pass renderer cannot satisfy this (chips precede the sections they link to).
- **Supporting-detail collapse** (`<details class="analysis">`) – only on an explicit `<!-- analysis -->` marker or a `Detailed analysis`/`Notes`/`Background` H4. Never auto-split on length.
- **Light TL;DR callout** – only on an explicit `> TL;DR:` blockquote or a full-italic leading paragraph. Consumes that source span (see section-dedup).
- **Section-deduplication rule** – when a specialized renderer consumes a structured span (e.g. a Success Metrics table → metric tiles), the Generic Prose fallback must skip that span. Emitting metric tiles AND a duplicate table AND an orphan list item is the named regression.


## Section Anchor Scheme

Anchor key = lowercase-kebab of the verbatim H2 text:
- `Functional Requirements` → `functional-requirements`
- `Success Metrics` → `success-metrics`

Collisions resolved by suffix (`-2`, `-3`). Anchors are stable across re-runs as long as headings don't change. (The notes payload uses verbatim heading text, not the kebab anchor – see *Notes Payload Format*.)

**Nested H3 sub-anchors.** Each H3 inside a `.card-body` gets `id="{parent-anchor}-{h3-kebab}"` (e.g. `risks-database-timeout`). Same collision-suffix scheme as for H2 (`-2`, `-3`) keeps duplicate H3s across cards distinct. The TOC builder uses these to emit indented `<li class="l2">` children under each parent H2 entry in the sidebar nav. H3 IDs are **URL-navigation-only**: H3s do **not** get a `+ Note` affordance, do not appear in the all-notes payload, and do not enter the IntersectionObserver active-section logic. The contract remains "one Note per H2."

**Nested H3 cards** (e.g. per-option cards inside a trade-off `## Options` section) carry `data-anchor-parent="<parent-anchor>"` purely as a CSS / DOM hook for layout; only H2 sections carry `data-anchor` and a Note affordance. One Note per H2 covers the whole section regardless of how many H3 cards it contains.


## Notes Payload Format (exact)

When the user clicks "Copy notes" with N>0 notes attached, write this to clipboard:

```markdown
# <artifact-owner> visual review notes for <artifact-path>

## Section: <heading text verbatim>
- <note 1 text>
- <note 2 text>

## Section: <next heading verbatim>
- <note text>
```

Group consecutive notes by `sectionAnchor`, but use `headingVerbatim` in the rendered `## Section: ...` line. Preserve note order within each section.

If `notes.length === 0`, do not write to clipboard. Show inline "No notes to copy" near the button.

The JS formatters that produce this exact shape (`buildSectionBlock`, `buildPayload`) live in `templates/render-shell.md` → *Notes Payload Formatters*. Compose them; don't re-derive.


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

Traps NOT covered by a contract above (full rule here):

- **Literal newlines in regex / quoted-string literals** → one regex SyntaxError disables the whole `<script>` (every button goes inert, TOC stays empty, copy never wires). See `templates/render-shell.md` → *JavaScript Authoring Discipline* rule 1.
- **Markdown italicizes `_blank` in `target="_blank"`** → unescaped underscores in raw markdown that pass through a Markdown→HTML pipeline get parsed as emphasis, leaving `target="<em>blank"` and `target="</em>blank"` in the output. Either emit the anchors directly as HTML (skip Markdown for the doc-meta block), or wrap underscore-bearing identifiers in code spans / HTML-escape the underscores. Same trap applies to any `snake_case` identifier in prose.
- **Sections with `data-anchor` but no `id`** → URL-fragment navigation (TOC clicks, deep links) silently no-ops because `#anchor` resolves against `id`, not `data-*`. Always emit both attributes with the same kebab value.
- **`agent-browser`** → wrong tool. It's used by the `andthen:excalidraw-diagram` skill for *automation*. Visualize wants the user's *primary* browser.
- **Non-deterministic class names or DOM ordering** → keep section blocks ordered as in the source; class names follow the section anchor scheme.
- **Dropping notes on copy success** → reset `notesDirty = false` but preserve `notes[]`. The user may keep editing.
- **Skipping LocalStorage** → refresh-loses-work is a real UX bug; persistence is mandatory.
- **Customizing the `beforeunload` message** → don't bother, browsers ignore it.
- **Hand-building HTML for diagrams from scratch each time** → use `templates/diagrams.md` for the coordinate math; it's the part most likely to be wrong.

Failures that invert a contract above (see the named contract for the rule + why):

- Reusing a renderer for a wrong schema → *Renderer Discipline*.
- Duplicate Success Metrics (tiles + table + orphan list) → *Section-deduplication rule*.
- JS-injecting `+ Note` / `View source` → *Section Block* contract (static affordances).
- TOC hidden on narrow viewports (e.g. `min-width: 1400px`) → *Two-pane layout* (sidebar collapses to drawer, never `display:none`).
- Per-section override of `.btn-note` / `.btn-source` → *Affordance CSS* (copy verbatim).
- External CDN / font / icon resources → *Single self-contained HTML file*.
- Slug-normalizing the payload heading → *Notes Payload Format* (verbatim H2 text, not slug).


## FOLLOW-UP ACTIONS

Skip this section when `AUTO_MODE=true` – print only the output path.

After the user reviews the rendered artifact and copies notes:

1. **Apply notes via downstream skill** – paste the clipboard payload into the chat when invoking the relevant downstream skill:
   - PRD review notes → `andthen:prd` (amendment context) or as conversational input to a fresh `andthen:plan` invocation
   - Plan review notes → `andthen:plan` for regeneration, `andthen:exec-plan` for execution caveats, or `andthen:review --mode gap` for plan-level review context
   - FIS review notes → `andthen:spec` for regeneration (standalone FIS), `andthen:plan` for plan-story regeneration, or `andthen:exec-spec` as execution context (the executor inlines the notes alongside the spec)
   - Clarification review notes → `andthen:clarify` amendment mode
   - Architecture-review notes → next `andthen:architecture` invocation in the matching mode (usually `--mode review`, or `--mode trade-off` when the note asks for an ADR)
   - Review-report notes → `andthen:remediate-findings` for actionable findings, or back to `andthen:review` for re-scoping
   - Changeset-walkthrough notes → the PR conversation (paste as review comments), or `andthen:review` as scope/focus context for a follow-up findings review
   - Trade-off review notes → next `andthen:architecture` invocation (e.g. ADR formalization)
   - Strategic-design review notes → next `andthen:architecture` invocation (e.g. `--mode strategic-design` for refinement, `--mode fitness` to formalize, or `--mode decompose` for a contested boundary)
   - Fitness-functions review notes → next `andthen:architecture --mode fitness` invocation or implementation backlog
   - Decompose review notes → next `andthen:architecture --mode decompose` invocation (refinement) or formalization as an ADR via `--mode trade-off`
   - Event-storming review notes → `andthen:architecture --mode strategic-design` (Big Picture hand-off), `--mode decompose` (Design Level hand-off), `andthen:ubiquitous-language` (vocabulary hotspots), or `andthen:excalidraw-diagram` (board diagram)
2. **Re-visualize after edits** – re-run `/andthen:visualize <path>` on the updated artifact to verify changes landed.
