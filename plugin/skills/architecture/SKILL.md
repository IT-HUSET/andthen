---
description: Architecture advice and structural analysis – design advice, health review, decomposition, fitness functions. Trigger on 'how should I structure this', 'should I split this', 'architecture review'. Modeling the domain is the andthen:domain skill; making and recording a decision is the andthen:decide skill; mapping the as-built codebase is the andthen:describe skill.
argument-hint: "[--mode <mode>[,<mode>...]: advise|review|decompose|fitness] [--output-dir <path>] [--auto] [scope/path]"
---

# Architecture

Architecture advice and structural analysis, in one mode or a chain of modes. No mode modifies code.

## Input

`INPUT` is `$ARGUMENTS` minus flags – the selected mode's **Required input**.

- `--mode` takes one mode or a comma-separated chain (`--mode review,fitness`).
- `--output-dir` sets `OUTPUT_DIR`. Absent, the analysis modes write under `reviews/` in the **Project Document Index** `Agent Temp` location, never a source tree.
- `--auto` makes the run unattended: read [`unattended-runs.md`](../../references/unattended-runs.md) and follow it.

| Mode | Triggers | Required input | Reference |
|------|----------|----------------|-----------|
| **advise** | architectural questions, greenfield design, "how should I structure", CUPID, tactical DDD | the question | [`mode-advise.md`](references/mode-advise.md) |
| **review** | "review architecture", "assess health", "analyze structure", "modularity check" | the scope path | [`mode-review.md`](references/mode-review.md) |
| **decompose** | "should I split", "merge these", "extract package", "decomposition", "too big" | the boundary | [`mode-decompose.md`](references/mode-decompose.md) |
| **fitness** | "fitness functions", "governance", "architectural tests", "prevent drift" | the scope path | [`mode-fitness.md`](references/mode-fitness.md) |

## Rules

- Print each recommended skill invocation as a complete, paste-ready line in the host's syntax, including its target path or request and required arguments.
- Every dispatch is a fresh subagent: the installed role agent it names (`reviewer`, `worker`) when available, else a generic inherited subagent. Never pin model or effort in a prompt.
- A project document a run has to create – `Product` on the first Proportionality answer – is seeded through a `worker` subagent that invokes the `andthen:init` skill with `seed <Index entry>` and the content to seed, keeping the templates out of this run's context.

## Workflow

1. **Select the mode.** Resolve it from the Mode table and name it in one line so the user can redirect, because selection is reversible. Ask only when intent is genuinely ambiguous (no match, or several with no dominant one) or a **Required input** is missing, and only for that. An empty invocation asks, and never assumes a mode or reviews the whole project.

   **Gate**: each selected mode and its **Required input** settled, confirmed by the user where it was asked.

2. **Read the context.** The project's documents, all per the **Project Document Index**:
   - `Learnings`.
   - `Decisions` – its ADR index and Still Current notes are settled choices, plus the ADRs it points at. A recommendation that reopens one names it and says what new evidence reopens it.
   - `Architecture` when present – the system-shape baseline for `review` / `decompose` / `fitness`.
   - `Domain Map` when present – read before any boundary or integration judgment. An Index entry still named `Context Map` is read as the `Domain Map`.
   - **Anchor on the `Product` document's Proportionality facts.** Drop or flag every component the design proposes that they do not carry or a standing technical non-goal forbids, citing the anchor (`flagged: exceeds stage prototype in docs/PRODUCT.md`). When the facts are absent, ask for all three in one question before you recommend, and write the answers into its Proportionality section, `unknown` for one left unanswered. An unattended run skips the question, writes nothing to `Product`, and says the anchor was unavailable.

   Then read each selected mode's reference from the Mode table and what it needs below – the deduplicated union for a chain, nothing beyond it:
   - Every mode: [`architecture-calibration.md`](references/architecture-calibration.md).
   - `review`, `decompose`, `fitness`: [`review-calibration.md`](../../references/review-calibration.md) and [`review-output.md`](references/review-output.md).

   **Gate**: each selected mode's reference and its loads read.

3. **Run the modes.** Follow each selected mode's reference end to end. A chain runs in declared order and reuses what an earlier mode computed. `advise` runs once, last when listed with analysis modes, on their findings.

   **Gate**: mode work complete with an evidence-based recommendation or findings.

4. **Filter the findings.** The filter runs over every finding and recommendation rationale. Spawn a fresh reviewer subagent. It reads `review-calibration.md` § Findings Filter and `architecture-calibration.md`, whose paths its prompt names, and runs the filter as `Findings Filter reviewing architecture findings and recommendations`. Its prompt carries:

   - the decision or codebase under review, with the project's description, scale, stage, and primary language;
   - the mode and scope – a chain lists its modes in declared order, each finding tagged with the mode that produced it, so the filter applies the right reasoning to each;
   - these questions:
     1. Is this finding or recommendation based on computed metrics, collected evidence, or a named framework – or on opinion?
     2. Is the severity/confidence proportional – could this decision, package, or boundary legitimately go the other way given its architectural role or the project's constraints?
     3. Does it account for the project's scale, maturity stage, and team capability?
     4. Would acting on this actually improve decision or architectural quality, or is it theoretical improvement?

   **Gate**: the reviewer's `Filter summary` line received and its verdicts applied before the presentation or report.

5. **Report.** Follow the mode reference's Output, and write per **Output** below.

   **Gate**: the report presented, and for an analysis mode written to its file with the path printed.

6. **Record learnings.** After `decompose`, append emerging traps or anti-patterns to the `Learnings` document, admitting each against its header note.

   **Gate**: each appended trap admitted against the header note, or none.

## Output

A multi-mode invocation produces **one combined report**, never a file per mode: one Executive Summary for the chain, one merged `How to Read This Report` legend, then the per-mode sections in declared order, each labeled with its mode and otherwise intact.

An analysis-mode report is one file in `OUTPUT_DIR`, named `<scope-or-topic>-architecture-<agent>-<YYYY-MM-DD>.md` for the package, module, or topic analysed. `<agent>` is the executing agent's short name (`claude`, `codex`, else `agent`), and a colliding name takes `-2`, `-3`, …. Print its path relative to the project root.

## Follow-up

Close on one `Next (fresh session):` line for the first case that applies, never a menu. A run another skill invoked prints none, because its caller owns the next step.

- **The report recommends a mode not yet run, or another skill** – that invocation, as the report prints it.
- **A fork the analysis surfaced, or an `advise` recommendation, to settle and record** – the `andthen:decide` skill on it.
