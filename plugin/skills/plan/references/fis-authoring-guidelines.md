# FIS Authoring Guidelines

The craft rubric the author writes a FIS to and the fresh reviewer checks it against. `fis-contract.md` defines the surfaces, shapes, proof forms and tags.

## Principles

**Need-to-know** – the executor is a frontier model that loads the project's instruction files, reads `Learnings` and every Project Document Index document its task triggers, and searches outward from every surface a task names. A line earns its place only if that executor would miss or misread the fact without it: a decision the source underdetermines, a trap the code does not show, wiring no outward search reaches (implicit registration, a generated or reflective call site, a consumer in another package). Never restate what those channels carry.

**Single source of truth** – a fact stated in two sections drifts into a contradiction the executor reconciles silently. Each fact has one home, and every other section names it by id: "scenario S01's readings", and another story always as "story S04", since stories and scenarios both number from `S01`.

- behavior – its Acceptance Scenario;
- a non-behavioral invariant – its Structural Criterion;
- a boundary no scenario refuses, and the story owning the other side – *What We're NOT Doing*;
- a cross-cutting or framework-level trap – *Constraints & Gotchas*;
- a choice the source underdetermines – *Architecture Decision*;
- a code pattern to follow – the `file#symbol` on each task that follows it;
- a referenced source's content – that source, cited, never paraphrased.

A task adds only what none of those carries. **Intent** says why the feature exists, never a scope summary.

## Cross-Document References

Prefer a durable, addressable artifact to a description or extract: a test over restated acceptance prose, a function over pseudocode, a mockup over a visual description. Cite a PRD's sections as Required Context.

- **Anchors over line numbers.** Paths are repo-root-relative POSIX, anchored by heading, symbol or dotted key path, lines only where no stable identifier exists. Never comma-join fragments (`path#A,B`).
- **Resolve at authoring time.** Open every reference and run every Proof binding; a Required source must be durable and available to the executor.
- Inline only a source with no durable address, as a short dated blockquote naming it.

## Acceptance Scenarios

One scenario per behavior the user would notice: the happy path and the edges that matter.

What the user notices only when it breaks is a Structural Criterion, an invariant this story's own diff could break. A run-wide check – a performance baseline, the full suite green, an E2E journey – is the run's final verification, never a criterion.

**Negative-path checklist** – after drafting, add one scenario for the riskiest gap in each category still uncovered, not one per parameter: omitted optional inputs, no-match cases (a lookup matching nothing and falling through), rejection paths.

Articulate each scenario at one of three levels:

- **Unbound** – concrete Given/When/Then nested under the bullet.
- **Fully bound** – precise title + Proof, only where the title alone states every acceptance-significant precondition, action, observable outcome, and required mechanism.
- **Supplemented** – the missing Given/When/Then detail before Proof, never a transcription of the test.

**Mechanism Fidelity** – for a required mechanism (an LLM turn, an algorithm, an external call), the title or GWT distinguishes it from a trivial substitute, and Proof verifies that mechanism. Without it a stub satisfies the scenario.

## Architecture Decision

Three or four lines: one `**Approach**:` line, and a `**Why this over the floor**:` line whenever the approach is not the floor (do nothing, or extend what exists), naming the floor and the requirement clause that rules it out – the clause the self-review prices each component against. Trade-off analysis past that is upstream work: reference an ADR from the `andthen:decide` skill. The optional `**Flow**:` block (~10 lines, outside the cap) is the one home of component or step order and seams; a rationale there is trade-off analysis leaking past the cap.

## Tasks

Before tasks for a cross-cutting rename or restructure, search the repo case-insensitively for every literal: each match maps to a task or a documented exclusion.

1. **Outcomes, not code changes** – each task states what is TRUE when done, and the executor chooses the implementation: "Replace foo with bar" becomes "Module X uses bar (foo retired)".
2. **Brevity** – the outcome in one clause, a pattern reference (`file#symbol`) where one applies, a dependency on an earlier task, `Verify`, `SATISFIES`. More means too large (split) or too detailed (state the outcome).
3. **`Verify`** is one of the *Runnable Proof Forms* plus the assertion proving the outcome, never build success alone. **`SATISFIES`** lists the `S<NN>` and `SC<NN>` the task advances: the one trace from work to acceptance.
4. **Coverage is clause-level.** A `Verify` covers every acceptance-significant clause of what its `SATISFIES` names. It may name a target whole only when that test asserts every clause, and then states only how it is observed and any clause it adds. A task satisfying "the record is created *and* linked to its owner" whose Verify proves only creation leaves the join unbuilt and still completes green.
5. **Assertions name outcomes.** Literal values belong only to contracts (column names, mandated errors), per *Diff-scoped leanness*: ``**Verify**: `cmd: traces list --limit 1` – output includes columns IN_TOKENS, OUT_TOKENS, CACHE_R, CACHE_W``.

A FIS is as short as completeness allows. Past ~6,000 words with the task count in range, the problem is prose: apply **Single source of truth** first, each cut naming the home that keeps its clause, and signal `OVERSIZE:` only on what remains.

*What We're NOT Doing* lists exclusions an executor could plausibly build, with reasons. *Constraints & Gotchas* holds only what is cross-cutting (≥2 tasks, a shared harness or ordering included) or a non-obvious framework trap; a task-local concern lives in its task.

## Plan-Spec Alignment Check

A plan story's FIS covers the story's scope, `sourceRefs` and every applicable Binding Constraint. Where it falls short, expand the FIS or add an explicit narrowing note for the plan's cross-cutting review; never narrow silently.

## Reverse Coverage Check

Every scenario and Structural Criterion traces to a plan story's scope, a source ref, a Binding Constraint (its `anchor` resolved against the PRD), a PRD outcome, or, standalone, an element of the request. One that traces to none is phantom scope: remove it, or raise it with the user and on approval add a scope note for amendment; a `--batch` run reports it as `PHANTOM_SCOPE`. With no plan or PRD, only a user- or business-observable outcome counts: "uses X library" is phantom absent a user-facing reason.

## Self-Check

- **Task ↔ Scenario coverage** – every task's `SATISFIES` names ≥1 existing `S<NN>` or `SC<NN>`: a task naming nothing is unproven scope, one naming a missing target is broken wiring.
- **Verify lines stay unrun** – they are exec-time checks; authoring proves the design of the surface, never its result. A `cmd:` absence check inverts its search's exit: no match exits 1.
- **Prose-vs-Verify scope** – "rename all X" gets a Verify enforcing that whole scope, not a sample.
