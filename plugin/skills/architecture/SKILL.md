---
description: Use for architecture design, review, decomposition, trade-off analysis, ADRs, CUPID/DDD guidance, and fitness functions. Operates in five modes — `review`, `decompose`, `advise`, `fitness`, `trade-off` — runnable singly or as a chain (e.g. `--mode review,fitness`). Trigger on 'architecture review', 'design architecture', 'CUPID', 'DDD', 'bounded context', 'should we split this module', 'should we merge these packages', 'propose fitness functions', 'compare options', 'trade-off', 'write an ADR', 'which approach'.
user-invocable: true
argument-hint: "[scope/path] [--mode <mode>[,<mode>...]] [--to-pr <number>]"
---

# Architecture

Architectural design, analysis, decomposition evaluation, trade-off research, and governance guidance. Evidence-based, framework-attributed, actionable.

## VARIABLES

ARGUMENTS: $ARGUMENTS

### Mode (auto-detected from arguments or explicit `--mode`)

| Mode | Triggers | Mode reference |
|------|----------|----------------|
| **review** (default) | "review architecture", "assess health", "analyze structure", "modularity check" | `references/mode-review.md` |
| **decompose** | "should I split", "merge these", "extract package", "decomposition", "too big" | `references/mode-decompose.md` |
| **advise** | architectural questions, greenfield design, "which pattern", "how should I structure", CUPID/DDD, trade-off framing questions | `references/mode-advise.md` |
| **fitness** | "fitness functions", "governance", "architectural tests", "prevent drift" | `references/mode-fitness.md` |
| **trade-off** | "trade-off analysis", "compare options", "evaluate alternatives", "write an ADR", "which approach" | `references/mode-trade-off.md` |

**Multi-mode**: `--mode` accepts a comma-separated list (e.g. `--mode review,fitness` or `--mode advise,trade-off`). Modes execute in declared order, sharing context — metrics, dependency graphs, candidate options, and findings computed by an earlier mode feed later modes without recomputation. `decompose` requires a boundary, `advise` requires a question, and `trade-off` requires a decision topic — include those inputs (via scope/argument or Phase 0) when chaining them.

### Optional Output Flags
- `--to-pr <number>` -> PUBLISH_PR: post the report as a plain PR comment

### Mode-Specific Flags

For **trade-off** mode:
- `--count <N>` -> COUNT: number of alternatives to compare (default `5`)
- `--output-dir <path>` -> OUTPUT_DIR: where to write research artifacts and recommendation (default `<project_root>/docs/research/` or the **Project Document Index** research location)

The remaining non-flag argument text is treated as the decision topic (`TOPIC`) for trade-off, the boundary for decompose, the question for advise, or the scope path for review/fitness.

## INSTRUCTIONS

- When `ARGUMENTS` is empty or ambiguous (no clear mode or scope), or when a declared chain is missing a required input for one of its modes (decompose boundary, advise question, trade-off topic), start with guided setup (see Phase 0). Do not assume a mode or run a full-project review by default.
- When `--mode` declares multiple modes, treat them as a single declared chain: gather any required additional inputs up front before Phase 1 completes, and produce one combined report at the end.
- Read the Workflow Rules, Guardrails, and relevant project guidelines before starting.
- Analysis and design only. Do not modify code.
- Calibrate severity with `references/review-calibration.md` and `references/architecture-calibration.md`.
- Read project learnings if they exist.
- Load only the mode reference and supporting references needed for the selected mode(s) — do not load all references upfront. For multi-mode chains, load the deduplicated union; `advise` supporting references load lazily inside the mode.
- Adapt all tooling suggestions, metric computation, and fitness function implementations to the detected language.
- **Evidence over opinion**: compute metrics and analyze structure before forming conclusions. Never report "this module seems too large" — report specific metric values, file paths, and import chains.
- **Framework attribution**: every recommendation cites a named principle (e.g. "Per SAP (Martin)..." or "Ford/Richards disintegration driver #3...").
- **Actionable findings**: every finding includes a concrete remediation path and a fitness function to prevent recurrence.
- **Progressive improvement**: support the "frozen rules" pattern — snapshot current violation count, fail CI only on regressions.
- **Multi-scale awareness**: tag findings by C4 level (Context / Container / Component / Code).
- **Connascence-aware coupling**: classify coupling by connascence type, not just edge count.
- **Reader-oriented reports**: assume the reader may not know architecture shorthand. Include a brief `How to Read This Report` legend near the top of every report, define only the terms actually used, and expand acronyms on first prose mention.

## GOTCHAS

- Running a full-project review when invoked with no arguments instead of asking the user what they want
- Reporting opinions without computed metrics
- Loading all references when the mode only needs a subset
- Treating infrastructure packages in Zone of Pain as problems (database drivers, runtime bindings may legitimately sit there)
- Missing dynamic connascence crossing package boundaries (always HIGH or CRITICAL)
- Recommending decomposition without scoring integration drivers alongside disintegration drivers
- Inflating severity for borderline metrics — report as INFO with context, not HIGH
- For `advise`/`trade-off`: recommending from popularity or novelty instead of fit for this project

## WORKFLOW

### Phase 0: Guided Setup _(when ARGUMENTS is empty or ambiguous)_

When invoked without clear mode and scope, guide the user interactively:

1. Present the available modes with one-line descriptions:
   - **review** — Full health assessment: dependency metrics, connascence analysis, anti-pattern scan, fitness function proposals
   - **decompose** — Evaluate a specific split/merge decision with Ford/Richards driver scoring
   - **advise** — Design or refactor guidance grounded in CUPID, DDD, and established architectural frameworks (covers greenfield design)
   - **fitness** — Propose fitness functions for architectural governance and ADR enforcement
   - **trade-off** — Trade-off analysis: research technical options, compare them systematically using weighted criteria, deliver an evidence-based recommendation or ADR

2. Ask what they want to accomplish and which part of the codebase or decision to focus on. The user may select one mode or a chain (e.g. "advise then trade-off"). For **decompose**, ask which boundary. For **advise**, ask for the specific question. For **trade-off**, ask for the decision topic and any hard constraints.

3. Confirm mode(s) and scope before proceeding to Phase 1. When modes were elicited interactively here, confirm the order; when modes arrived via explicit `--mode`, do not re-confirm — the order is already declared.

**Gate**: Mode(s) and scope confirmed by user

### Phase 1: Context & Setup

1. Parse mode(s) from `ARGUMENTS` (auto-detect a single mode, or parse a comma-separated list from explicit `--mode`), or use the mode(s) confirmed in Phase 0. Preserve declared order for multi-mode chains.
2. Read project rules, guidelines, and existing ADRs.
3. Detect the primary language from project files (only required for modes that compute structural metrics — `review`, `decompose`, `fitness`):

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

Execute the selected mode by following its mode-reference file. For multi-mode invocations, run each mode in declared order, carrying forward dependency graph, computed metrics, classified connascence, candidate options, and findings — never recompute work an earlier mode already produced.

- `review` → `references/mode-review.md`
- `decompose` → `references/mode-decompose.md`
- `advise` → `references/mode-advise.md` (covers greenfield design, refactor guidance, CUPID/DDD assessment, and pattern advice)
- `fitness` → `references/mode-fitness.md`
- `trade-off` → `references/mode-trade-off.md`

**Gate**: Mode work complete with evidence-based findings or an evidence-based recommendation

### Phase 3: Adversarial Challenge

Use `references/adversarial-challenge.md` (`Generic Findings-Challenger Template`) with:
- **Role**: `Adversarial Challenger reviewing architecture findings`
- **Shared calibration**: `references/review-calibration.md`
- **Skill calibration**: `references/architecture-calibration.md`
- **Context block**: `The codebase/decision under review is a {project description and scale}. Primary language: {language or N/A}. Mode: {mode}. Scope: {scope}. Project stage: {from discovery}.` For multi-mode chains, render `{mode}` as the comma-separated list in declared order and tag each finding with the mode that produced it so the challenger applies the right reasoning to each.
- **Questions**:
  1. `Is this finding or recommendation based on computed metrics, collected evidence, or a named framework — or on opinion?`
  2. `Is the severity/confidence proportional — could this package/decision legitimately sit where it does given its architectural role or the project's constraints?`
  3. `Does it account for the project's scale, maturity stage, and team capability?`
  4. `Would acting on this actually improve architectural health or decision quality, or is it theoretical improvement?`
- **Verdicts**: `VALIDATED`, `DOWNGRADED`, `WITHDRAWN`
- **Findings payload**: `{all findings and/or recommendation rationale}`

Apply verdicts before writing the final report.

**Gate**: Findings challenged and filtered

### Phase 4: Report

Format findings per `references/review-output.md`. For multi-mode invocations, produce **one combined report**: a single Executive Summary covering the chain, a merged `How to Read This Report` legend (deduplicated across modes), and the per-mode sections in declared order, each clearly labeled with its mode name. Do not produce separate report files per mode. When composing per-mode sections into the combined report, **drop each mode's individual `Executive Summary` and `How to Read This Report` items** from its template — those appear once at the top of the combined report. All other mode-specific sections stay intact.

Each mode reference file declares what its report must include. See the reference for details.

**Report output conventions**:
- **Filename**: `<scope-or-topic>-architecture-<agent>-<YYYY-MM-DD>.md` — on collision append `-2`, `-3`. `<agent>` is your agent short name (`claude`, `codex`, etc.; fall back to `agent`).
- **Directory priority**:
  1. **Spec directory** — when the scope corresponds to a feature with an associated spec directory from the Project Document Index
  2. **Target directory** — for `review`/`decompose`/`fitness`, next to the primary target package/directory; for `advise`/`trade-off`, in the project's research/ADR location (see **Project Document Index**)
  3. **Fallback** — `{AGENT_TEMP}/reviews/` (default `.agent_temp/reviews/`)
- On completion, print the report's relative path from the project root.

### Publish to PR _(if --to-pr)_
If `PUBLISH_PR` is set, post the report file's contents as a plain PR comment via `gh pr comment <number> --body-file <report-path>`. If the command does not return a direct comment URL, resolve it via follow-up lookup. Print the direct comment URL.

## MULTI-STEP SESSIONS

This skill supports chaining multiple analyses/designs in a single session in two equivalent ways:

- **Declared upfront** — the user passes a comma-separated `--mode` list (or selects multiple modes in Phase 0). The chain runs end-to-end and produces one combined report (see Phase 4).
- **Interactive chaining** — after any single-mode run, FOLLOW-UP ACTIONS offer the next mode and the skill loops back to Phase 1 with the user's choice. Each loop produces its own report.

Both flavors carry forward context from prior steps — metrics computed in **review** should inform a subsequent **decompose**; options surfaced in **advise** should inform a subsequent **trade-off**.

Typical chains:
- **review** -> **decompose** (a specific finding) -> **fitness** (governance for the resolution)
- **advise** -> **trade-off** (evaluate the candidate options surfaced during advice) -> ADR
- **review** -> **advise** (dig into a specific concern) -> **fitness**
- **fitness** -> **review** (assess current state before proposing governance)

## FOLLOW-UP ACTIONS

After each analysis — including a combined report from a declared multi-mode chain — present findings and offer the actions below. After a chain, scope the "Continue with another mode" offer to modes not yet run in this session.

Offer:
1. **Continue with another mode** — carry forward current session context
2. **Deep-dive into a specific finding** — zoom into a single package, boundary, or option
3. **Create fitness function implementations** from proposals
4. **Formalize an ADR** from a `trade-off` recommendation or an `advise` decision
5. **Code-level review** for correctness, style, security (invoke the `andthen:review` skill with `--mode code`)
6. **End session** — finalize the report and stop

When the user selects a follow-up that maps to another mode, loop back to Phase 1 with the new mode and narrowed scope. Do not re-read project rules or re-detect language — reuse context from the current session.
