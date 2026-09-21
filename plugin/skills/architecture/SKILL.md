---
description: Architecture decisions and structural analysis – trade-offs and ADRs, design advice, health review, decomposition, fitness functions, strategic DDD, event storming. Trigger on 'trade-off', 'write an ADR', 'how should I structure this', 'architecture review', 'should I split this', 'bounded contexts'. Mapping the as-built codebase or curating the glossary is the andthen:describe skill.
argument-hint: "[--mode <mode>[,<mode>...]: advise|trade-off|review|decompose|fitness|strategic-design|event-storming] [--output-dir <path>] [--auto] [scope/path]"
---

# Architecture

`INPUT` is `$ARGUMENTS` minus flags – the decision topic for trade-off, the question for advise, the boundary for decompose, the domain or workflow scope for strategic-design/event-storming, or the scope path for review/fitness.

- `--output-dir` sets `OUTPUT_DIR`, which must be writable.
- `COUNT` is the number of alternatives trade-off derives – 5 unless the request names one ("compare three options").
- `--auto` (`AUTO_MODE`) runs unattended. Never ask what to do next. Infer mode and scope from the Mode table, and where no defensible inference exists stop with `BLOCKED:` naming the minimum missing inputs. Propagate it to nested `andthen:*` skills that accept it. Close on the findings summary and the report path, no follow-up offers.

## Mode (auto-detected from arguments or explicit `--mode`)

| Mode | Triggers | Required input | Read |
|------|----------|----------------|----------------|
| **advise** (default) | architectural questions, greenfield design, "which pattern", "how should I structure", CUPID/DDD | the question | `references/mode-advise.md`, `references/architecture-calibration.md`, `references/adr-template.md` |
| **trade-off** | "trade-off analysis", "compare options", "evaluate alternatives", "write an ADR", "which approach" | decision topic + constraints | `references/mode-trade-off.md`, `../../references/design-tree.md`, `references/adr-template.md` |
| **review** | "review architecture", "assess health", "analyze structure", "modularity check" | the scope path | `references/mode-review.md`, `references/architecture-calibration.md`, `../../references/review-calibration.md`, `references/review-output.md` |
| **decompose** | "should I split", "merge these", "extract package", "decomposition", "too big" | the boundary | `references/mode-decompose.md`, `references/architecture-calibration.md`, `../../references/review-calibration.md`, `references/review-output.md` |
| **fitness** | "fitness functions", "governance", "architectural tests", "prevent drift" | the scope path | `references/mode-fitness.md`, `references/architecture-calibration.md`, `../../references/review-calibration.md`, `references/review-output.md` |
| **strategic-design** | "strategic design", "subdomains", "bounded contexts", "context map", "domain map", "model the domain" | the domain or workflow scope | `references/mode-strategic-design.md`, `references/architecture-calibration.md`, `../../references/review-calibration.md` |
| **event-storming** | "event storming", "discover the domain", "process discovery", "pivotal events", Brandolini | the domain or workflow scope + the level, Big Picture the default | `references/mode-event-storming.md`, `references/architecture-calibration.md` |

`strategic-design` and `event-storming` also read `../../references/board-models.md` and their board's machine form – `../../references/context-map.schema.json`, `../../references/event-storm.schema.json` – for the typed boards they emit with their Markdown reports.

**Multi-mode**: `--mode` takes a comma-separated list (`--mode review,fitness`).

The analysis modes (`review`, `decompose`, `fitness`, `strategic-design`, `event-storming`) run in declared order and share context – metrics, dependency graphs, subdomain and context candidates, findings – so a later mode never recomputes what an earlier one produced. Each still needs its own **Required input**, collected in Phase 0 when it is missing.

`advise` and `trade-off` are the decision modes and run alone: `advise` reaches structured comparison by moving into `trade-off`, which is the same thing done once.

A list mixing a decision mode with analysis modes is `BLOCKED:` naming the two invocations to run in order – dropping the analysis modes would report a partial run as complete.

In **trade-off** mode the `OUTPUT_DIR` subtree layout follows `references/mode-trade-off.md`, and absent `--output-dir`, `OUTPUT_DIR` defaults to the **Project Document Index** Research location, or `<project_root>/docs/research/`; the analysis modes default it to `reviews/` under the Index's `Agent Temp` location, never a source tree.

Each analysis-mode report is one file in `OUTPUT_DIR`, named `<scope-or-topic>-architecture-<agent>-<YYYY-MM-DD>.md` for the package, module, domain, or topic analysed – `<agent>` the executing agent's short name (`claude`, `codex`, else `agent`), a colliding name taking `-2`, `-3`, … – with its path printed relative to the project root.

## INSTRUCTIONS

- Resolve the mode from the Mode table and name it in one line so the user can redirect – selection is cheap and reversible, so a named, correctable choice beats a blocking menu.
- Phase 0 is for a genuinely ambiguous intent (no match, or several with no dominant one) or a missing required input, scoped to eliciting just that; an empty invocation gets Phase 0, never an assumed mode or a whole-project review.
- **`trade-off` and `event-storming` are interactive by contract**, and `strategic-design` holds one gate of its own – Step 8's map registration. At each gate the mode reference names, present the proposal back – recommendation first, one-line rationale, real alternatives, room for free-form input – through the host's structured user-input tool when available, permitted, and suited to the question, else in chat, and wait for an actual answer before dependent decisions: suggested or preselected answers are not confirmation, and neither is detailed `INPUT` (`mode-trade-off.md`'s *implicit confirmation from detailed input* failure mode).
- Analysis and design only: no mode modifies code.
- Recommend from fit for this project, never from popularity or novelty; `architecture-calibration.md`'s traps and the `Product` document's Proportionality facts (Phase 1) are the check against machinery out of proportion to the project's stage and scale.

## WORKFLOW

### Phase 0: Guided Setup _(ambiguous mode or missing input only; `BLOCKED:` under `--auto`)_

Present the Mode table's rows one line each, ask what they want to accomplish and where – one mode or a chain of analysis modes – and collect the **Required input** of each mode chosen. Confirm the order too when a chain was elicited here; an explicit `--mode` already declares it.

**Gate**: Mode(s) and scope confirmed by user

### Phase 1: Context & Setup

1. Read the project's documents (all per **Project Document Index**):
   - `Learnings` – the project's known traps.
   - `Decisions` – its ADR index and Still Current notes are settled choices, plus the ADRs it points at; a recommendation that reopens one names it and says what new evidence reopens it.
   - `Architecture` when present – the system-shape baseline for `review` / `decompose` / `fitness`.
   - `Context Map` when present – read before any boundary or integration judgment.
   - `Product` – anchor every component the design proposes, and every subdomain classification, against its **Proportionality** facts. Drop or flag what they do not carry or a standing technical non-goal forbids, citing the anchor (`flagged: exceeds stage prototype in docs/PRODUCT.md`). Absent or `unknown` facts are not licence to size against imagined scale – say the anchor was unavailable and let the user set it.
   - `architecture-model.json` under `Models` when it exists, in `strategic-design` – keep its context ids/names consistent with the accepted Context Map; align them or surface the divergence.
2. Detect the primary language from project files (`review`, `decompose`, `fitness` only):

   | Indicator | Language | Tooling |
   |-----------|----------|---------|
   | `pubspec.yaml` | Dart | `lakos` (metrics + cycles), `dart pub deps --json`, `dart analyze` |
   | `package.json` | JavaScript/TypeScript | `dependency-cruiser` (rules + metrics), `madge` (cycles) |
   | `go.mod` | Go | `go mod graph`, custom cycle detection |
   | `pom.xml` / `build.gradle` | Java/Kotlin | ArchUnit (architecture tests), JDepend (metrics) |
   | `*.csproj` / `*.sln` | C#/.NET | NetArchTest, NDepend |
   | `pyproject.toml` / `setup.py` | Python | Deptry, pydeps, import-linter |
   | `Cargo.toml` | Rust | `cargo tree`, `cargo udeps` |

3. Load what the Mode table's **Read** column names for each selected mode – the deduplicated union for a chain, nothing beyond it.

**Gate**: Mode(s), scope, language (when relevant), and references are clear

### Phase 2: Analysis / Design

Follow each selected mode's reference end to end, in declared order for chains, sharing context per **Multi-mode**.

**Gate**: Mode work complete with an evidence-based recommendation or findings

### Phase 3: Findings Filter

The filter runs over every finding and recommendation rationale – in `trade-off`, before the Step 5 gate. Spawn a fresh reviewer subagent – the installed `reviewer` role agent when available, else a generic inherited subagent; never pin model or effort in a prompt – that reads `../../references/review-calibration.md` § Findings Filter and `references/architecture-calibration.md` and runs the filter as `Findings Filter reviewing architecture findings and recommendations`. Its prompt carries the decision, codebase, or domain under review with the project's description, scale, stage, and primary language, the mode and scope – a chain lists its modes in declared order, each finding tagged with the mode that produced it so the filter applies the right reasoning to each – and these questions:
1. Is this finding or recommendation based on computed metrics, collected evidence, or a named framework – or on opinion?
2. Is the severity/confidence proportional – could this decision, package, or boundary legitimately go the other way given its architectural role or the project's constraints?
3. Does it account for the project's scale, maturity stage, and team capability?
4. Would acting on this actually improve decision or architectural quality, or is it theoretical improvement?

Apply the returned verdicts before the presentation or report.

**Gate**: Findings filtered

### Phase 4: Report

Follow the mode reference's Report Contents, `review` / `decompose` / `fitness` findings per `references/review-output.md`. A multi-mode invocation produces **one combined report**, never a file per mode: one Executive Summary for the chain, one merged `How to Read This Report` legend, then the per-mode sections in declared order, each labeled with its mode and otherwise intact.

## Post-Completion

After `trade-off`, `strategic-design`, `decompose`, or `event-storming`, append emerging traps or anti-patterns to the `Learnings` document (**Project Document Index**), admitting each against its header note; choices with rationale go to ADRs instead.

A project document a run has to create – `Decisions` on the first accepted ADR, `Context Map` on registration – is seeded by a subagent, so the template set stays out of this run's context: spawn a generic inherited subagent, the installed `worker` role agent when available, whose prompt names that document's template section in `../../references/project-document-templates.md`, the target path resolved from the **Project Document Index**, and the content to seed. An existing document is appended to in place, with no template loaded at all.

## FOLLOW-UP ACTIONS

After each analysis – a combined chain report included – present the findings and offer the follow-ups that apply:

- **Another mode** – after a chain, only modes not yet run. It loops back to Phase 1 with the narrowed scope and the session's context; project documents and language are not re-read.
- **An ADR** per `references/mode-trade-off.md` Step 6 – for an `advise` decision or a fork an analysis mode surfaced; after `trade-off` only when the user opted out there.
- **A code-level review** through the `andthen:review` skill with `--mode code`.
