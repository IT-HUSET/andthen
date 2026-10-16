---
description: Model the domain – classify subdomains, map bounded contexts and their integrations into the Domain Map, maintain the Ubiquitous Language glossary, run event storming. Trigger on 'model the domain', 'context map', 'build a glossary', 'event storming'. Design advice is the andthen:architecture skill; mapping the code is the andthen:describe skill.
argument-hint: "[--mode <mode>[,<mode>...]: subdomains|contexts|glossary|event-storming] [--output-dir <path>] [--auto] [scope/path]"
---

# Domain

Models the domain with the user as domain expert, in one mode or a chain of modes. Each mode writes one record, and no mode modifies code.

## Input

`INPUT` is `$ARGUMENTS` minus flags – the selected mode's **Required input**.

- `--mode` takes one mode or a comma-separated chain (`--mode subdomains,contexts`).
- `--output-dir` sets `OUTPUT_DIR`. Absent, a mode's report is written under `reviews/` in the **Project Document Index** `Agent Temp` location, never a source tree.
- `--auto` makes the run unattended: read [`unattended-runs.md`](../../references/unattended-runs.md) and follow it.

| Mode | Triggers | Required input | Reference |
|------|----------|----------------|-----------|
| **subdomains** | "subdomains", "core domain", "what matters most" | the domain or workflow scope | [`mode-subdomains.md`](references/mode-subdomains.md) |
| **contexts** | "bounded contexts", "context map", "domain map", "who owns what" | the domain or workflow scope | [`mode-contexts.md`](references/mode-contexts.md) |
| **glossary** | "glossary", "ubiquitous language", "domain terms", "terminology cleanup" | the focus area, blank for the whole project | [`mode-glossary.md`](references/mode-glossary.md) |
| **event-storming** | "event storming", "discover the domain", "process discovery", "pivotal events", "aggregates", "tactical design", Brandolini | the domain or workflow scope + the level, Big Picture the default, Design Level on "aggregates" or "tactical design" | [`mode-event-storming.md`](references/mode-event-storming.md) |

Loads beyond the mode's reference:

- `contexts`, `event-storming`: [`domain-calibration.md`](references/domain-calibration.md).
- `event-storming`: [`board-models.md`](references/board-models.md) and [`event-storm.schema.json`](references/event-storm.schema.json).

## Rules

- Print each recommended skill invocation as a complete, paste-ready line in the host's syntax, including its target path or request and required arguments.
- `Domain Map` and `Ubiquitous Language` are Project Document Index entries. An Index entry still named `Context Map` is read as the `Domain Map`.
- **Gates.** At each gate the mode reference names, present the proposal back: recommendation first, a one-line rationale, the real alternatives, and room for free-form input.
  - End the asking turn on the question, never on a report of what was produced. Use the host's structured user-input tool wherever it holds the turn for the answer, otherwise the reply.
  - Never proceed on an unanswered gate. Suggested or preselected answers are not confirmation, and neither is detailed `INPUT` – the *implicit confirmation from detailed input* failure mode.
- Every dispatch is a fresh subagent: the installed role agent it names (`reviewer`, `worker`) when available, else a generic inherited subagent. Never pin model or effort in a prompt.
- A project document a run has to create – `Domain Map` or `Ubiquitous Language` on its first write, `Product` on the first Proportionality answer – is seeded through a `worker` subagent that invokes the `andthen:init` skill with `seed <Index entry>` and the content to seed, keeping the templates out of this run's context.
- Recommend from fit for this project, never from popularity or novelty.

## Workflow

1. **Select the mode.** Resolve it from the Mode table and name it in one line so the user can redirect, because selection is reversible. Ask only when intent is genuinely ambiguous (no match, or several with no dominant one) or a **Required input** is missing, and only for that. An unspecific request asks, preselecting `contexts` when the `Domain Map` holds classified subdomains, else `subdomains`. `contexts` with no `Domain Map`, or one with no classified subdomains, runs as `subdomains,contexts`.

   **Gate**: each selected mode and its **Required input** settled, confirmed by the user where it was asked.

2. **Read the context.** The project's documents, all per the **Project Document Index**:
   - `Learnings`, in every mode but `glossary`.
   - `Decisions`, in every mode but `glossary` – its ADR index and Still Current notes are settled choices, plus the ADRs it points at. A recommendation that reopens one names it and says what new evidence reopens it.
   - `Architecture` when present.
   - `Domain Map` and `Ubiquitous Language` when present.
   - `context-map.json` under `Models` when present, as migration input: each context's `subdomainType` seeds `subdomains`, its `team` and `codeLocation` the `contexts` Team and Code location columns, and each relationship's `direction` and `rationale` the peer orientation and Notes of its Integration Patterns row. Once `contexts` registers, the completion summary says the file may now be deleted. Never delete it.
   - **Anchor on the `Product` document's Proportionality facts**, in `subdomains` and `contexts`. Drop or flag every subdomain classification and context sizing they do not carry or a standing technical non-goal forbids, citing the anchor (`flagged: exceeds stage prototype in docs/PRODUCT.md`). When the facts are absent, ask for all three in one question before you recommend, and write the answers into its Proportionality section, `unknown` for one left unanswered. An unattended run skips the question, writes nothing to `Product`, and says the anchor was unavailable.

   For `subdomains` and `contexts`, default the input path from artifact presence. **Greenfield** drives from a PRD, a hand-written `intent.md`, or the user's narrative. **Brownfield** drives from observed structure: the `Architecture` document the `andthen:describe` skill writes, module boundaries, persisted entities, and cross-module API calls. On either path the `Product` document's value propositions ground the classification, and an event-storm board for the scope under `event-storms/` in the `Models` location seeds the run.

   Then read each selected mode's reference from the Mode table and its loads – the deduplicated union for a chain, nothing beyond it.

   **Gate**: each selected mode's reference and its loads read.

3. **Run the modes.** Follow each selected mode's reference end to end. A chain runs in declared order and reuses what an earlier mode computed.

   **Gate**: mode work complete, its record written or, under `--auto`, its proposal printed.

4. **Filter the findings.** The filter runs over the findings and recommendations of `contexts` and `event-storming`, never over what the user confirmed at a gate, so a confirmed classification or context list is never downgraded or withdrawn. Spawn a fresh reviewer subagent. It reads [`review-calibration.md`](../../references/review-calibration.md) § Findings Filter and `domain-calibration.md`, whose paths its prompt names, and runs the filter as `Findings Filter reviewing domain findings and recommendations`. Its prompt carries:

   - the domain under review, with the project's description and primary language, and its scale and stage from the `Product` document's Proportionality facts when present;
   - the mode and scope, a chain's findings each tagged with the mode that produced it;
   - only the findings and recommendations;
   - these questions:
     1. Is this finding or recommendation based on collected evidence or a named framework – or on opinion?
     2. Is the severity/confidence proportional – could this boundary or classification legitimately go the other way given the project's constraints?
     3. Does it account for the project's scale, maturity stage, and team capability?
     4. Would acting on this actually improve the model, or is it theoretical improvement?

   **Gate**: the reviewer's `Filter summary` line received and its verdicts applied before the report is written, or the step skipped when neither `contexts` nor `event-storming` ran.

5. **Report.** Follow the mode reference's Output, and write per **Output** below.

   **Gate**: the report presented, and for `contexts` and `event-storming` written to its file with the path printed.

6. **Record learnings.** After `contexts` or `event-storming`, append emerging traps or anti-patterns to the `Learnings` document, admitting each against its header note.

   **Gate**: each appended trap admitted against the header note, or none.

## Output

Each mode writes one record: `subdomains` the `Domain Map`'s Subdomains, Relationships, Worked Example, and Open Questions; `contexts` its Bounded Contexts and Integration Patterns; `glossary` the `Ubiquitous Language`; `event-storming` its board under `Models`.

A `contexts` or `event-storming` report is one file in `OUTPUT_DIR`, named `<scope-or-topic>-domain-<agent>-<YYYY-MM-DD>.md` for the domain, workflow, or topic analysed. `<agent>` is the executing agent's short name (`claude`, `codex`, else `agent`), and a colliding name takes `-2`, `-3`, …. A chain of both is one combined report: one Executive Summary, one merged `How to Read This Report` legend, then the per-mode sections in declared order, each labeled with its mode and otherwise intact. Print its path relative to the project root.

## Follow-up

Close on one `Next (fresh session):` line for the first case that applies, never a menu.

- **The report or record points to a mode not yet run, or another skill** – that invocation, as it prints it.
- **A fork the analysis surfaced, to settle and record** – the `andthen:decide` skill on it.
