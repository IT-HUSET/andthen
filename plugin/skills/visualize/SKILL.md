---
description: Use when reviewing an existing AndThen artifact visually – PRD, plan.json, requirements-clarification, product vision, FIS (feature implementation spec), review report (any lens), changeset walkthrough, architecture review / trade-off / strategic-design / fitness / decompose / event-storming report, or ADR. Renders a self-contained HTML view in the user's browser, captures section-anchored notes, and exports them as a markdown payload via clipboard. Trigger on 'review visually', 'visualize this prd', 'visualize this plan', 'visualize this fis', 'visualize this review', 'visualize this walkthrough', 'visualize this clarification', 'visualize trade-off', 'andthen visualize'.
argument-hint: "<path-to-artifact>"
user-invocable: true
---

# Visualize Workflow Artifact

Supported artifacts: PRD, `plan.json`, Feature Implementation Specification (FIS), `requirements-clarification.md`, product vision, review report (any `andthen:review` lens or `andthen:architecture --mode review` output), changeset walkthrough (`andthen:explain-changes` output), architecture trade-off report, architecture strategic-design report, architecture fitness-functions report, architecture decompose report, architecture event-storming report, and ADR.

**Open-loop by design:** emit HTML, open browser, exit. The skill does not block waiting for user interaction.

**Read-only by contract:** reads one artifact, writes a separate HTML review surface, never edits the source.

## When to Use

Use to eyeball any supported artifact before handing it to its consuming skill, or to verify one retrospectively.


## How to Use

1. Read the artifact at `$1`.
2. Detect the artifact type by content (filename advisory only) – see *Artifact Type Detection*.
3. Read `templates/render-shell.md` – the shared chrome (theme tokens, layout skeleton, section-block contract, cross-cutting component renderers, and the JavaScript layer). Every render uses it.
4. Load the matching per-artifact template from `templates/` (one per detected type – filename mirrors the Detection-table type, e.g. `templates/prd.md`, `templates/event-storming.md`, except `product-vision` renders via `templates/clarification.md` and `architecture-review` via `templates/review-report.md`). `templates/diagrams.md` and `templates/js-helpers.md` are pulled in by those templates as needed.
5. Generate a single self-contained HTML file at `.agent_temp/visual-review/<slug>-<timestamp>.html`. Resolve the path against the repo root (`git rev-parse --show-toplevel`) when inside a git working tree, falling back to CWD when there is no repo. `<slug>` is the basename without extension; `<timestamp>` is `YYYYMMDD-HHMMSS`.
6. Open the file in the user's browser via the OS-detected command (see *Browser-Open Detection*).
7. Print the output path and exit. Do not block on user interaction.


## Artifact Type Detection

Run heuristics in order; first match wins. **Filename hints are advisory only – content decides.**

| Type | Markers |
|---|---|
| `plan` | Valid JSON object with `schemaVersion === "1"`, `overview`, and `stories` array. *Ordered before markdown heuristics because `plan.json` has no H1/H2 headings. If JSON parses but these keys are missing, do not fall through to markdown detection – report unsupported JSON artifact shape. If the keys are present but `schemaVersion` is not `"1"`, stop with `andthen:visualize: unsupported plan.json schemaVersion "<value>"` and write no HTML.* |
| `fis` | H2 contains "Feature Overview and Goal" AND (H2 contains "Implementation Plan" OR H2 contains "Acceptance Scenarios" OR H2 contains "Structural Criteria"). |
| `prd` | H1 contains "PRD" or "Product Requirements"; H2 contains both "Executive Summary" and "Functional Requirements" |
| `clarification` | H1 starts with "Requirements Clarification"; H2 contains "Decisions Log" |
| `product-vision` | H1 starts with "Product Vision" or H1 contains "Product"; H2 set contains at least two of "Vision", "Problem Statement", "Target Users & Personas", "Value Propositions", "Anti-Goals", "Roadmap Themes" |
| `changeset-walkthrough` | H1 starts with "Changeset Walkthrough"; OR H2 set contains BOTH "Change Map" AND "Change Narrative". *Ordered before the report family since walkthroughs may carry an "Architectural Delta" H2.* |
| `event-storming` | H1 or H2 contains "Event Storming" / "Event-Storming" (case-insensitive); OR H2 set contains BOTH "Event Timeline" AND ("Hotspots" OR "Commands and Actors"). *Ordered before `strategic-design`, which event-storming reports overlap via a "Subdomain Candidates" H2; the Event-Timeline marker wins first.* |
| `fitness` | H1 contains "Fitness Functions" / "Fitness Function" (case-insensitive); OR H2 set contains BOTH "Proposed Fitness Functions" AND ("ADR Gap Analysis" OR "Current Governance Coverage" OR "Prioritized Implementation Roadmap"). *The H2 branch requires the fitness-mode discriminator – not "Fitness Functions" alone – because an architecture **review** report also carries a `## Proposed Fitness Functions` section and must NOT mis-detect as a fitness report.* |
| `decompose` | H1 or H2 contains "Decompose" / "Decomposition Analysis" (case-insensitive); OR H2 set contains ("Driver Scores" OR "Boundary Map") AND "Recommendation" AND **no scoring-matrix table is present** (the scoring-matrix exclusion disambiguates from `tradeoff`). |
| `strategic-design` | H1 contains "Strategic Design" / "Strategic-Design"; OR H2 set contains both "Subdomains" and "Context Map" (case-insensitive). *Ordered before `tradeoff`, which it overlaps via `Executive Summary`; the more-specific marker pair wins.* |
| `adr` | H1 matches `/^ADR[-\s]?\d/` (e.g. "ADR-011:", "ADR 11:", "ADR011:"); OR (H2 set contains "Decision" AND ("Consequences" OR "Alternatives Considered") AND **no scoring-matrix table is present**) (case-insensitive). *Ordered before `tradeoff`, which it overlaps via "Decision"; the scoring-matrix exclusion disambiguates.* |
| `tradeoff` | H1 or H2 contains "Trade-off" / "Trade off" / "Decision Analysis"; presence of a scoring matrix table (rows = options, columns = criteria) |
| `architecture-review` | H1 contains "Architecture Review" as a phrase; AND H2 set contains "Executive Summary"; AND H2 set contains at least one of "Findings", "Metrics Dashboard", or "Proposed Fitness Functions". *Uses `templates/review-report.md`, but ownership routes back to the `andthen:architecture` skill, not the generic review/remediation loop.* |
| `review-report` | H1 contains "Review" as a standalone word (case-insensitive – e.g. "Doc Review", "Code Review", "Council Review"); AND H2 set contains "Executive Summary"; AND H2 set contains at least one of "Findings", "Verdict", "Readiness Assessment", "Metrics Dashboard". *Last among markdown reports; overlaps `tradeoff`/`fitness`/`decompose` via `Executive Summary`, so the "Review" H1 + Findings/Verdict pair is the discriminator.* |

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

Owner = who maintains the source artifact, not the consumption target for the copied payload; FOLLOW-UP ACTIONS routing is authoritative for where notes go. The header is human/prompt-readable, not structurally parsed; pasting the markdown body into the chat alongside the consuming skill invocation is the contract.


## Core Requirements (every render)

These are contracts. The HTML/CSS/JS that satisfies them lives in `templates/render-shell.md` – read it before emitting.

- **Single self-contained HTML file.** All CSS, JS, and SVG inlined. No external scripts, fonts, stylesheets, icons. Must work from `file://` with no network access.
- **Warm light Anthropic-style theme;** use the theme tokens in `templates/render-shell.md`.
- **Two-pane layout.** Left = scrollable artifact content; right = sticky sidebar holding the **Copy notes** button (top), section navigator with note-count badges, and a unified note list. The sidebar is always visible at viewports ≥1100px and collapses to a top drawer below that. *Why:* a floating-TOC-only layout hides nav on laptop widths and buries affordances where users miss them. *Exception:* `changeset-walkthrough` renders as a tabbed app via the bundled deterministic renderer (`scripts/render-changeset.mjs`, per `templates/changeset.md`), never hand-authored; its output already embeds the notes machinery and affordances.
- **Static affordances, JS-attached handlers.** The `+ Note` button, `View source` toggle, and per-section note-count span MUST be present in the static HTML body of each `<section>`. JavaScript only attaches click handlers and renders the dynamic note list. *Why:* if JS fails, errors out, or is delayed, the user must still see *that* notes are possible. Empty `<div class="sec-actions"></div>` placeholders waiting for JS injection are a known regression – never ship them.
- **Read-only render + section-anchored notes.** No structured editing. One Note affordance + one View-source toggle per H2 section. Diagrams do not get their own Note affordance – the parent section's Note covers any diagram inside it.
- **Notes payload via clipboard.** "Copy notes" writes a markdown payload via `navigator.clipboard.writeText`; on failure, reveals a textarea with payload pre-selected for manual copy.
- **LocalStorage persistence.** Notes survive refresh; "Restore previous notes?" prompt on reload when a matching prior session exists.
- **`beforeunload` warning.** Fires when notes exist and have not been copied since last edit.


## Renderer Discipline

Each markdown H2 section, or plan virtual H2 section, dispatches to **one** specialized renderer (defined per artifact type in `templates/`) chosen by case-insensitive substring match on the heading. **Schema mismatch is the failure mode to avoid:** if a section's content does not fit a renderer's shape, fall back to **Generic Prose** (rendered markdown with `<h3>`/`<h4>`/`<p>`/`<ul>`/`<ol>`/`<table>`). Never repurpose a renderer for a different schema just because the heading sits in a similar position. Past renders have shipped Non-Functional Requirements as five empty `story-card` placeholders because the user-stories renderer was reused for a Category/Requirement/Threshold table.

**Per-section schema contract (PRD-shaped artifacts).** Per-heading PRD renderer specs live in `templates/prd.md` → Section Renderers. Two rules are load-bearing here:

- **Non-Functional Requirements** use the NFR rows renderer (Category/Requirement/Threshold), never the user-stories renderer.
- When the source markdown's columns do not match the documented shape, fall back to **Generic Prose** rather than forcing unfamiliar columns into renderer slots.

**Cross-artifact dispatch (renderers shared across templates).** Three structural renderers live in `templates/diagrams.md` and may be dispatched from any artifact's template based on the heading + source-shape conditions below. Heading-substring match still wins over shape detection; mapviz wins over walkthrough wins over flowchart for the same heading.

| Artifact | Section heading (substring) | Renderer dispatch (priority order) |
|---|---|---|
| Plan | Overview | Summary prose + phase/wave timeline from `overview.phases[]` |
| Plan | Story Catalog | Story cards; `.risk-map` links to story sub-anchors – see `templates/plan.md` |
| Plan | Dependency Graph | Phase/wave lanes + dependency edge list; invalid `dependsOn` references surface inline – see `templates/plan.md` |
| Plan | Shared Decisions / Binding Constraints / Risk Summary / Execution Notes | Card renderers from `templates/plan.md`; omit optional virtual sections when source arrays/strings are empty |
| PRD | User Flows | (1) `mapviz` fenced block → Module Map · (2) 2–9 H3 substeps where **every** substep's stripped body char-count ≥ 50 → Walkthrough · (3) else → Flowchart. (Char count: strip whitespace and markdown markers, count Unicode code points – see `templates/prd.md`.) |
| PRD | Risks | Risk rows + `.risk-map` chips + `<details class="analysis">` collapse |
| PRD | Edge Cases | Styled generic table (Scenario/Expected) |
| PRD | Constraints & Assumptions | Two-column constraints/assumptions + dependency cards (H3 subsections + Dependency table) |
| Clarification | Design Decisions → Resolved Decisions H3 | If ≤5 rows AND every Rationale's stripped char-count ≥ 60 → Walkthrough; else current tree+notes+table |
| Trade-off | Options → all option H3s together | If **every** option H3 carries ≥ 2 of {`What changes`, `Where it changes`, `Risk` / `Trade-off`} H4 substring → Walkthrough alongside radar for every option; else prose+radar for every option. All-or-nothing per section – never mixed |
| Trade-off | Options summary | `.risk-map` chips above the H3 list |
| Strategic-design | Context Map | `mapviz` → Module Map + interactive node→panel binding; else Generic Prose |
| Strategic-design | Bounded Contexts | per-context `mapviz` → Module Map; else card grid – see `templates/strategic-design.md` |
| Strategic-design | Subdomains | Card grid; else Generic Prose – see `templates/strategic-design.md` |
| ADR | Context | Generic Prose; inline `**Status:** …` / `**Date:** …` / `**Deciders:** …` / `**Related:** …` metadata consumed into eyebrow + pill row |
| ADR | Decision | Recommendation accent box (reuse `templates/tradeoff.md`); code blocks render verbatim |
| ADR | Alternatives Considered | Option cards (reuse `templates/tradeoff.md` `.option`, **no radar** since ADRs lack scoring matrices); one H3 per alternative – see `templates/adr.md` |
| ADR | Consequences | Three-bucket layout (Positive / Negative / Neutral); else Generic Prose – see `templates/adr.md` |
| FIS | Acceptance Scenarios | Checkbox cards + Given/When/Then 3-step walkthrough (parser: `templates/fis.md` *Acceptance Scenarios → Checkbox cards*) |
| FIS | Structural Criteria | Non-behavioral checklist; unchecked items fold into KPI "Open Items" – see `templates/fis.md` |
| FIS | Implementation Plan | Task walkthrough (`diagrams.md#walkthrough`) over the canonical task shape (parser: `templates/fis.md`) |
| FIS | Required Context | Source-pinned block cards parsing the `<!-- source:` / `<!-- extracted:` comment pair – see `templates/fis.md` |
| FIS | Code Patterns & External References | Type/path/intent table from the fenced code block – see `templates/fis.md` |
| Review | Findings | Risk-map chips + Finding cards; parser handles both `### Finding N - SEVERITY - Title` (review-skill) and `### ARCH-NNN: Title` (architecture); council-mode nests under reviewer/lens H3 dividers |
| Review | Verdict / Readiness Assessment | Gap-mode PASS/FAIL table; other lenses render the readiness label as a single chip |
| Review | Metrics Dashboard | Per-package metrics table – see `templates/review-report.md` |
| Review | Proposed Fitness Functions | Reuses `fitness.md` `.fitness-card` / `.fitness-lanes` renderer when present in an architecture review report |
| Changeset | (whole artifact) | Bundled deterministic renderer – run `node "${CLAUDE_SKILL_DIR}/scripts/render-changeset.mjs" <artifact> <output>` per `templates/changeset.md`; never hand-author this type's HTML. Document-shell fallback only when Node is unavailable |
| Fitness | Proposed Fitness Functions | Four-level lanes (L1 commit / L2 PR / L3 nightly / L4 prod) with per-proposal cards – see `templates/fitness.md` |
| Fitness | ADR Gap Analysis | ADR cards with `data-gap` chips; cross-link to Proposed Fitness Functions cards – see `templates/fitness.md` |
| Decompose | Driver Scores | Two-radar pair (6 disintegration + 4 integration axes) + driver-score table – see `templates/decompose.md` |
| Decompose | Connascence Analysis | Per-boundary connascence cards – see `templates/decompose.md` |
| Decompose | Evaluation Matrix | 4-criteria PASS/FAIL checklist (a+b+c required for Split) |
| Decompose | Recommendation | Verdict chip (Split / Merge / Keep / Defer) inside the reused tradeoff `.recommendation` box; triggers list for Defer – see `templates/decompose.md` |
| Event-storming | Event Timeline | Horizontal sticky-note strip; per-event H3 sub-anchors enable backlinking from Subdomain Candidates – see `templates/event-storming.md` |
| Event-storming | Commands and Actors | Sticky-note pairs grid – see `templates/event-storming.md` |
| Event-storming | Policies and Read Models | Two-column grid; Process Modeling and Design Level only – see `templates/event-storming.md` |
| Event-storming | Hotspots | Sticky-note cards with route hint to follow-up modes – see `templates/event-storming.md` |
| Event-storming | Subdomain Candidates / Workflow Boundaries / Aggregate Candidates | Per-candidate cards anchored on their pivotal-event cluster – see `templates/event-storming.md` |
| Event-storming | Recommended Next Steps | Hand-off chips for the level-appropriate next mode (`--mode strategic-design`, `--mode decompose`, `andthen:ubiquitous-language`, `andthen:excalidraw-diagram`) |

**DDD relationship vocabulary** recognized in `mapviz` edge labels (annotated, not parsed for layout) is specified in `templates/strategic-design.md` and `templates/diagrams.md#module-map`.

**Section-block wrapper is universal.** Every markdown H2, plus every plan virtual H2, produces a `<section class="card" id="{anchor}">` block with the standard affordances (Note button, View source toggle, count span) per the *Section Block* contract in `templates/render-shell.md` – that's true regardless of which renderer matched. The renderer choice only changes what fills `.card-body`. Generic Prose is **not** a permission to skip the wrapper or the affordances; it is a body-level fallback only.

**Cross-cutting render components** – markup + CSS in `templates/render-shell.md` → *Cross-cutting Component Renderers*; the correctness rules that a model gets wrong without them:

- **Risk-map chips** – summary-of-many anchor rows above Options / Risks / Open-Questions lists. **Two-pass renderer required:** build an anchor index in pass 1, validate chip targets against it in pass 2, flag misses with an inline comment + `aria-disabled`. A single-pass renderer cannot satisfy this (chips precede the sections they link to).
- **Supporting-detail collapse** (`<details class="analysis">`) – only on an explicit `<!-- analysis -->` marker or a `Detailed analysis`/`Notes`/`Background` H4. Never auto-split on length.
- **Light TL;DR callout** – only on an explicit `> TL;DR:` blockquote or a full-italic leading paragraph. Consumes that source span (see section-dedup).
- **Section-deduplication rule** – when a specialized renderer consumes a structured span (e.g. a Success Metrics table → metric tiles), the Generic Prose fallback must skip that span. Emitting metric tiles AND a duplicate table AND an orphan list item is the named regression.


## Section Anchor Scheme

Anchor key = lowercase-kebab of the verbatim H2 text (`Functional Requirements` → `functional-requirements`). Collisions resolved by suffix (`-2`, `-3`). Anchors are stable across re-runs as long as headings don't change. (The notes payload uses verbatim heading text, not the kebab anchor – see *Notes Payload Format*.)

**Nested H3 sub-anchors.** Each H3 inside a `.card-body` gets `id="{parent-anchor}-{h3-kebab}"` (e.g. `risks-database-timeout`), same collision-suffix scheme as H2; the TOC builder emits these as indented `<li class="l2">` children. H3 IDs are **URL-navigation-only** – H3 cards (e.g. per-option cards in a trade-off `## Options` section) carry a `data-anchor-parent="<parent-anchor>"` DOM/CSS hook but no `+ Note`, do not appear in the all-notes payload, and stay out of the IntersectionObserver active-section logic. Only H2 carries `data-anchor` and a Note; one Note per H2 covers the section regardless of H3 count.


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
- **Markdown italicizes `_blank` in `target="_blank"`** → underscores passing through a Markdown→HTML pipeline get parsed as emphasis (`target="<em>blank"`). Emit doc-meta anchors as raw HTML, or wrap underscore-bearing identifiers (any `snake_case`) in code spans.
- **Sections with `data-anchor` but no `id`** → URL-fragment navigation (TOC clicks, deep links) silently no-ops because `#anchor` resolves against `id`, not `data-*`. Always emit both attributes with the same kebab value.
- **`agent-browser`** → wrong tool. It's used by the `andthen:excalidraw-diagram` skill for *automation*. Visualize wants the user's *primary* browser.
- **Dropping notes on copy success** → reset `notesDirty = false` but preserve `notes[]`. The user may keep editing.
- **Customizing the `beforeunload` message** → don't bother, browsers ignore it.
- **Hand-building HTML for diagrams from scratch each time** → use `templates/diagrams.md` for the coordinate math; it's the part most likely to be wrong.

Failures that invert a contract above (see the named contract for the rule + why):

- Reusing a renderer for a wrong schema → *Renderer Discipline*.
- TOC hidden on narrow viewports → *Two-pane layout* (drawer, never `display:none`).
- Slug-normalizing the payload heading → *Notes Payload Format* (verbatim H2 text).


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
   - Strategic-design review notes → next `andthen:architecture --mode strategic-design` invocation
   - Fitness-functions review notes → next `andthen:architecture --mode fitness` invocation or implementation backlog
   - Decompose review notes → next `andthen:architecture --mode decompose` invocation
   - Event-storming review notes → `andthen:architecture --mode strategic-design` (Big Picture hand-off) or `--mode decompose` (Design Level hand-off)
2. **Re-visualize after edits** – re-run `/andthen:visualize <path>` on the updated artifact to verify changes landed.
