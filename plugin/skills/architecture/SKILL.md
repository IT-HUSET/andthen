---
description: Use for architecture design, review, decomposition, trade-off analysis, ADRs, CUPID/DDD guidance, fitness functions, strategic design, and event storming. Operates in seven modes – `review`, `decompose`, `advise`, `fitness`, `trade-off`, `strategic-design`, `event-storming` – runnable singly or as a chain (e.g. `--mode review,fitness` or `--mode event-storming,strategic-design,decompose`). Trigger on 'architecture review', 'design architecture', 'CUPID', 'DDD', 'bounded context', 'subdomain', 'context map', 'event storming', 'strategic design', 'should we split this module', 'should we merge these packages', 'propose fitness functions', 'compare options', 'trade-off', 'write an ADR', 'which approach'.
user-invocable: true
argument-hint: "[--mode <mode>[,<mode>...]] [--output-dir <path>] [--to-pr <number>] [--visual] [--auto|--headless] [scope/path]"
---

# Architecture

Architectural design, analysis, decomposition evaluation, trade-off research, and governance guidance. Evidence-based, framework-attributed, actionable.

## VARIABLES

ARGUMENTS: $ARGUMENTS (strip any flag tokens like `--mode`, `--to-pr`, `--count`, `--output-dir`, `--visual`, `--auto`, or `--headless` before interpreting the remainder as scope/topic)

### Mode (auto-detected from arguments or explicit `--mode`)

| Mode | Triggers | Mode reference |
|------|----------|----------------|
| **review** (default) | "review architecture", "assess health", "analyze structure", "modularity check" | `references/mode-review.md` |
| **decompose** | "should I split", "merge these", "extract package", "decomposition", "too big" | `references/mode-decompose.md` |
| **advise** | architectural questions, greenfield design, "which pattern", "how should I structure", CUPID/DDD, trade-off framing questions | `references/mode-advise.md` |
| **fitness** | "fitness functions", "governance", "architectural tests", "prevent drift" | `references/mode-fitness.md` |
| **trade-off** | "trade-off analysis", "compare options", "evaluate alternatives", "write an ADR", "which approach" | `references/mode-trade-off.md` |
| **strategic-design** | "strategic design", "subdomains", "bounded contexts", "context map", "domain map", "model the domain" | `references/mode-strategic-design.md` |
| **event-storming** | "event storming", "discover the domain", "process discovery", "pivotal events", Brandolini | `references/mode-event-storming.md` |

**Multi-mode**: `--mode` accepts a comma-separated list (e.g. `--mode review,fitness`, `--mode advise,trade-off`, or `--mode event-storming,strategic-design,decompose`). Modes execute in declared order, sharing context – metrics, dependency graphs, candidate options, subdomain/context candidates, and findings computed by an earlier mode feed later modes without recomputation. `decompose` requires a boundary, `advise` requires a question, `trade-off` requires a decision topic, and `strategic-design` / `event-storming` require a scope or topic (the domain or workflow under discovery) – include those inputs (via scope/argument or Phase 0) when chaining them.

### Optional Output Flags
- `--output-dir <path>` -> OUTPUT_DIR: explicit report-directory override; bypasses the directory-priority resolution and source-code subdirectory guard in [`review-report-location.md`](${CLAUDE_PLUGIN_ROOT}/references/review-report-location.md). Path must exist and be writable – `BLOCKED: --output-dir <path> not writable` in `AUTO_MODE`, warning + fallthrough to heuristic tiers in default mode. When combined with `--to-pr`, the report writes to `--output-dir` and is then posted as the PR comment. In **trade-off** mode the path also roots the research-artifacts subtree at `OUTPUT_DIR/[topic-slug]/` (the report file sits at `OUTPUT_DIR/`, alongside the subtree); when `--output-dir` is absent, OUTPUT_DIR defaults to the **Project Document Index** Research location, or `<project_root>/docs/research/`.
- `--to-pr <number>` -> PUBLISH_PR: post the report as a plain PR comment
- `--visual` -> VISUAL_MODE: after the report is written and filtered, invoke the `andthen:visualize` skill on the produced report. Supported outputs: `review`, `trade-off`, `strategic-design`, `fitness`, `decompose`, `event-storming`, and ADR reports (every mode's primary output).
- `--auto` / `--headless` -> AUTO_MODE: automation-safe execution with no conversational prompts

### Mode-Specific Flags

For **trade-off** mode:
- `--count <N>` -> COUNT: number of alternatives to compare (default `5`)

The remaining non-flag argument text is treated as the decision topic (`TOPIC`) for trade-off, the boundary for decompose, the question for advise, or the scope path for review/fitness.

## INSTRUCTIONS

- When `ARGUMENTS` is empty or ambiguous (no clear mode or scope), or when a declared chain is missing a required input for one of its modes (decompose boundary, advise question, trade-off topic), start with guided setup (see Phase 0). Do not assume a mode or run a full-project review by default.
- **Automation mode** (`--auto` / `--headless`) – never ask the user what to do next. Infer mode and scope from the arguments using the auto-detect table; if no defensible inference is possible, stop with `BLOCKED:` and list the minimum missing decisions (mode, scope, decompose boundary, advise question, trade-off topic, or strategic-design / event-storming domain or workflow scope). Propagate `--auto` to nested `andthen:*` skill invocations that accept it (the `andthen:ops` skill is exempt – it is deterministic).
- **Fully read and understand all project rules, guardrails, principles and guidelines (as defined in `CLAUDE.md` / `AGENTS.md` and other referenced files) before starting work.**
- Analysis and design only. Do not modify code.
- Calibrate severity with `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` and `references/architecture-calibration.md`.
- **Visual review is a post-filter handoff.** In `AUTO_MODE`, run it only when `--visual` is present. When present, complete the normal report/filter gate first, then invoke the `andthen:visualize` skill on the produced report; the visualizer owns HTML rendering, note export, browser-open behavior, and `.agent_temp/visual-review/` output. Every architecture mode's primary report is supported (`review`, `trade-off`, `strategic-design`, `fitness`, `decompose`, `event-storming`, and ADR outputs); the `advise` mode lacks a dedicated visualize template, so `--visual` on a pure `advise` run is a no-op – print a one-line note instead of falling through to a generic renderer. **Multi-mode chains** (`--mode review,fitness` etc.) produce one combined report; the visualizer detects a single artifact type per file and dispatches first-match-wins, so chain output renders with the renderer for the first-detected mode and other mode sections fall to Generic Prose. When `--visual` is set on a multi-mode chain, print a one-line warning naming which mode's renderer will activate; the user can opt to re-run individual modes with `--output-dir` if per-mode-fidelity rendering is needed.
- Read project learnings if they exist.
- Load only the mode reference and supporting references needed for the selected mode(s) – do not load all references upfront. For multi-mode chains, load the deduplicated union; `advise` supporting references load lazily inside the mode.
- Adapt all tooling suggestions, metric computation, and fitness function implementations to the detected language.
- **Evidence over opinion**: compute metrics and analyze structure before forming conclusions. Never report "this module seems too large" – report specific metric values, file paths, and import chains.
- **Framework attribution**: every recommendation cites a named principle (e.g. "Per SAP (Martin)..." or "Ford/Richards disintegration driver #3...").
- **Actionable findings**: every finding includes a concrete remediation path and a fitness function to prevent recurrence.
- **Progressive improvement**: support the "frozen rules" pattern – snapshot current violation count, fail CI only on regressions.
- **Multi-scale awareness**: tag findings by C4 level (Context / Container / Component / Code).
- **Connascence-aware coupling**: classify coupling by connascence type, not just edge count.

## GOTCHAS

- Running a full-project review when invoked with no arguments instead of asking the user what they want
- Reporting opinions without computed metrics
- Loading all references when the mode only needs a subset
- Treating infrastructure packages in Zone of Pain as problems (database drivers, runtime bindings may legitimately sit there)
- Missing dynamic connascence crossing package boundaries (always HIGH or CRITICAL)
- Recommending decomposition without scoring integration drivers alongside disintegration drivers
- Inflating severity for borderline metrics – report as INFO with context, not HIGH
- For `advise`/`trade-off`: recommending from popularity or novelty instead of fit for this project
- Applying the Ousterhout module-design lens (`references/ousterhout-modules.md`) at Container or Context level – it is a Component/Code lens for in-process module and API design only, not for service decomposition

## WORKFLOW

### Phase 0: Guided Setup _(when ARGUMENTS is empty or ambiguous)_

Skip this phase when `AUTO_MODE=true` – if mode and scope cannot be inferred from the arguments, stop with `BLOCKED:` listing the minimum missing inputs instead of prompting.

When invoked without clear mode and scope, guide the user interactively:

1. Present the available modes with one-line descriptions:
   - **review** – Full health assessment: dependency metrics, connascence analysis, anti-pattern scan, fitness function proposals
   - **decompose** – Evaluate a specific split/merge decision with Ford/Richards driver scoring
   - **advise** – Design or refactor guidance grounded in CUPID, DDD, and established architectural frameworks (covers greenfield design)
   - **fitness** – Propose fitness functions for architectural governance and ADR enforcement
   - **trade-off** – Trade-off analysis: research technical options, compare them systematically using weighted criteria, deliver an evidence-based recommendation or ADR
   - **strategic-design** – Discovery-oriented strategic DDD: classify subdomains (core/supporting/generic), propose bounded contexts and sizing, draw the context map with named integration patterns, surface UL touchpoints (greenfield + brownfield paths)
   - **event-storming** – Brandolini-style event-storming session as a discovery technique: orange events, blue commands, yellow actors, lilac policies, purple hotspots, green read models; Big Picture / Process Modeling / Design Level

2. Ask what they want to accomplish and which part of the codebase or decision to focus on. The user may select one mode or a chain (e.g. `advise,trade-off` or `event-storming,strategic-design,decompose`). Each mode has a required input: **decompose** → boundary; **advise** → question; **trade-off** → decision topic + constraints; **strategic-design** / **event-storming** → domain or workflow scope (event-storming also needs level; Big Picture is the default).

3. Confirm mode(s) and scope before proceeding to Phase 1. When modes were elicited interactively here, confirm the order; when modes arrived via explicit `--mode`, do not re-confirm – the order is already declared.

**Gate**: Mode(s) and scope confirmed by user

### Phase 1: Context & Setup

1. Parse mode(s) from `ARGUMENTS` (auto-detect a single mode, or parse a comma-separated list from explicit `--mode`), or use the mode(s) confirmed in Phase 0. Preserve declared order for multi-mode chains.
2. Read project rules, guidelines, and existing ADRs. Also read the existing `Architecture` document (see **Project Document Index**) if present – it's the authoritative system-shape baseline for `review` / `decompose` / `fitness` modes. For `advise` / `trade-off` / `strategic-design` / `event-storming` modes, also read the `Product` document (see **Project Document Index**) if present – vision and anti-goals anchor design decisions and subdomain classification.
3. Detect the primary language from project files (only required for modes that compute structural metrics – `review`, `decompose`, `fitness`). The discovery and design modes (`advise`, `trade-off`, `strategic-design`, `event-storming`) do not require language detection – they reason about contexts, decisions, and events at the C4 Context/Container level rather than computing metrics:

   | Indicator | Language | Tooling |
   |-----------|----------|---------|
   | `pubspec.yaml` | Dart | `lakos` (metrics + cycles), `dart pub deps --json`, `dart analyze` |
   | `package.json` | JavaScript/TypeScript | `dependency-cruiser` (rules + metrics), `madge` (cycles) |
   | `go.mod` | Go | `go mod graph`, custom cycle detection |
   | `pom.xml` / `build.gradle` | Java/Kotlin | ArchUnit (architecture tests), JDepend (metrics) |
   | `*.csproj` / `*.sln` | C#/.NET | NetArchTest, NDepend |
   | `pyproject.toml` / `setup.py` | Python | Deptry, pydeps, import-linter |
   | `Cargo.toml` | Rust | `cargo tree`, `cargo udeps` |

4. Load the mode reference file for each selected mode. For multi-mode chains, load the deduplicated union of mode refs and any supporting references they declare.

**Gate**: Mode(s), scope, language (when relevant), and references are clear

### Phase 2: Analysis / Design

Execute the selected mode by following its mode-reference file. For multi-mode invocations, run each mode in declared order, carrying forward dependency graph, computed metrics, classified connascence, candidate options, and findings – never recompute work an earlier mode already produced.

- `review` → `references/mode-review.md`
- `decompose` → `references/mode-decompose.md`
- `advise` → `references/mode-advise.md` (covers greenfield design, refactor guidance, CUPID/DDD assessment, and pattern advice)
- `fitness` → `references/mode-fitness.md`
- `trade-off` → `references/mode-trade-off.md`
- `strategic-design` → `references/mode-strategic-design.md` (subdomain classification, bounded-context discovery and sizing, context mapping, UL touchpoints; greenfield + brownfield paths)
- `event-storming` → `references/mode-event-storming.md` (Brandolini's three levels; produces event timelines, command/actor maps, hotspots, and subdomain or aggregate candidates)

**Gate**: Mode work complete with evidence-based findings or an evidence-based recommendation

### Phase 3: Findings Filter

Use `${CLAUDE_PLUGIN_ROOT}/references/adversarial-challenge.md` (`Generic Findings-Filter Template`) with:
- **Role**: `Findings Filter reviewing architecture findings`
- **Shared calibration**: `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md`
- **Skill calibration**: `references/architecture-calibration.md`
- **Context block**: `The codebase/decision under review is a {project description and scale}. Primary language: {language or N/A}. Mode: {mode}. Scope: {scope}. Project stage: {from discovery}.` For multi-mode chains, render `{mode}` as the comma-separated list in declared order and tag each finding with the mode that produced it so the challenger applies the right reasoning to each.
- **Questions**:
  1. `Is this finding or recommendation based on computed metrics, collected evidence, or a named framework – or on opinion?`
  2. `Is the severity/confidence proportional – could this package/decision legitimately sit where it does given its architectural role or the project's constraints?`
  3. `Does it account for the project's scale, maturity stage, and team capability?`
  4. `Would acting on this actually improve architectural health or decision quality, or is it theoretical improvement?`
- **Verdicts**: `VALIDATED`, `DOWNGRADED`, `WITHDRAWN`
- **Findings payload**: `{all findings and/or recommendation rationale}`

Apply verdicts before writing the final report.

**Gate**: Findings filtered

### Phase 4: Report

Format findings per `references/review-output.md`. For multi-mode invocations, produce **one combined report**: a single Executive Summary covering the chain, a merged `How to Read This Report` legend (deduplicated across modes), and the per-mode sections in declared order, each clearly labeled with its mode name. Do not produce separate report files per mode. When composing per-mode sections into the combined report, **drop each mode's individual `Executive Summary` and `How to Read This Report` items** from its template – those appear once at the top of the combined report. All other mode-specific sections stay intact.

Each mode reference file declares what its report must include. See the reference for details.

**Report output conventions** – filename and directory resolve per [`review-report-location.md`](${CLAUDE_PLUGIN_ROOT}/references/review-report-location.md). This skill contributes:
- **`<feature-name>` token**: `<scope-or-topic>` (the package/module/topic under analysis)
- **Report suffix**: `architecture`
- **Target nature** (per mode):
  - `review` / `decompose` / `fitness` → source-code (the primary target is a package/directory; tier-2 co-location is disabled)
  - `advise` / `trade-off` / `strategic-design` / `event-storming` → doc artifact, with a **substituted tier-2 destination** (per the asset's tier-2 hook): the project's research/ADR location from the Project Document Index `Research` / `ADRs` rows. When such a row resolves, it replaces tier 2's "next to target" destination; tier 1 still wins, tiers 3/4 still apply on miss.

### Publish to PR _(if --to-pr)_
If `PUBLISH_PR` is set, post the report file's contents as a plain PR comment via `gh pr comment <number> --body-file <report-path>`. If the command does not return a direct comment URL, resolve it via follow-up lookup. Print the direct comment URL.

### Visual Review _(if --visual)_
After the report is written and Phase 3 findings are filtered, invoke the `andthen:visualize` skill on supported architecture outputs. Print both the report path and the visualizer's output path.

## FOLLOW-UP ACTIONS

Skip this section when `AUTO_MODE=true` – print only the verdict/findings summary and the report path.

After each analysis – including a combined report from a declared multi-mode chain – present findings and offer the actions below. After a chain, scope the "Continue with another mode" offer to modes not yet run in this session.

Offer:
1. **Continue with another mode** – carry forward current session context
2. **Deep-dive into a specific finding** – zoom into a single package, boundary, or option
3. **Create fitness function implementations** from proposals
4. **Formalize an ADR** from a `trade-off` recommendation or an `advise` decision
5. **Code-level review** for correctness, style, security (invoke the `andthen:review` skill with `--mode code`)
6. **Review visually** – _every mode's primary report is supported (`review`, `trade-off`, `strategic-design`, `fitness`, `decompose`, `event-storming`, ADR); OMIT this entry only after a pure `advise` run (no structured report)_. Run `andthen:visualize <report-path>` to spot scope and edge-case issues a markdown view obscures.
7. **End session** – finalize the report and stop
- **Common chains**: `review → decompose → fitness`; `advise → trade-off → ADR`; `review → advise → fitness`; `fitness → review`; `event-storming → strategic-design → decompose` _(end-to-end discovery into decomposition)_; `strategic-design → fitness` _(formalize strategic decisions as fitness functions)_; `strategic-design,trade-off` _(weighted-criteria comparison when an integration-pattern choice is contested)_

When the user selects a follow-up that maps to another mode, loop back to Phase 1 with the new mode and narrowed scope. Do not re-read project rules or re-detect language – reuse context from the current session.
