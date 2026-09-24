# FIS Authoring Guidelines

How to author a Feature Implementation Specification against `fis-contract.md`, which defines its surfaces, shapes, proof forms, and tags.

## FIS Authoring Principles

FIS is an executable spec: intent over implementation, references over content, decisions not explanations.

**Need-to-know** – the executor is a frontier model that loads the project's instruction files, reads `Learnings` and every **Project Document Index** document whose read trigger its task meets, and searches outward from every surface a task names. A line earns its place only if that executor would miss or misread the fact without it: a decision the source underdetermines, a trap the code does not show, wiring no outward search reaches (implicit registration, a generated or reflective call site, a consumer in another package). What those channels already carry – a Learnings trap, a triggered guideline's rule, a Key Dev Command, how a named function behaves, a discoverable caller – is never listed or restated.

**Single source of truth** – the executor holds the whole FIS in context and resolves every id, so no line has to stand alone, and a fact stated in two sections drifts into a contradiction the executor reconciles silently. Each fact has one home, and every other section names it by id instead of re-typing it – "scenario S01's readings", and another story always as "story S04", since stories and scenarios both number from `S01`:

- behavior – its Acceptance Scenario;
- a non-behavioral invariant – its Structural Criterion;
- a boundary no scenario refuses, and the story owning the other side – *What We're NOT Doing*;
- a cross-cutting or framework-level trap – *Constraints & Gotchas*;
- a choice the source underdetermines – *Architecture Decision*;
- a code pattern to follow – the `file#symbol` on each task that follows it;
- a referenced source's content – that source, cited, never paraphrased.

A task adds only what none of those carries. The layering the contract builds stays: an Expected Outcome states what a user judges, its scenarios the concrete readings.


## Feature Overview and Goal Authoring

The `## Feature Overview and Goal` section is the FIS's intent anchor.

- **Intent** – one sentence naming *why* the feature exists: the problem solved or user/business value unlocked. Not a scope summary, not a title restatement.
- **Expected Outcomes** – 2-4 user- or business-observable success conditions, one sentence each: the FIS's own contract, distinct from upstream PRD outcomes and from its Acceptance Scenarios, which carry the mechanics – which fallback, which ref, which message.

**Outcome ↔ Scenario coverage** – every Expected Outcome is exemplified by ≥1 scenario tagged with its `[OC<NN>]`; an unexemplified outcome is unproven.


## Cross-Document References

**Reference substitution** – prefer a durable, addressable artifact over a description or copied extract: an executable test over restated acceptance prose, a function over pseudocode, an HTML mockup over a visual description.

1. **Anchors over line numbers.** Local reference and Proof paths are repo-root-relative POSIX paths, anchored by heading (Markdown), symbol (code), or dotted key path (YAML/JSON); lines only where no stable identifier exists. Never comma-join fragments (`path#A,B`). A wireframe or external API document is context like any other.
2. **Resolve at authoring time.** Open every reference and run every Proof binding; Required sources must be durable and available to the executor. Pin cross-repo ports by commit and name the parity expectation.
3. **Inline only without a durable address** – then only the irreducible span (≤20 lines each, ≤40 total) as a blockquote under an H3 naming its source path and the date extracted. Exact issue-transported requirements may exceed that budget when no durable source exists – never narrow or omit them.


## Acceptance Scenario Authoring

One scenario per behavior: the happy path and the edges that matter. **Negative-path checklist** – after drafting, add one scenario for the riskiest gap in each category still uncovered, not one per parameter: **omitted optional inputs**, **no-match cases** (a selector or lookup matching nothing and falling through), **rejection paths**.

**Mechanism Fidelity** – for a required mechanism (LLM turn, algorithm, external call), title or GWT must distinguish it from a trivial substitute, and Proof verifies that articulated mechanism. Without it a stub satisfies the scenario.


## Architecture Decision Authoring

**Default: 3-4 lines max.** One `**Approach**:` line; a `**Why this over the floor**:` line whenever the approach is not the floor option (do nothing, or extend what exists), naming that floor and the requirement clause that rules it out – the clause the self-review prices each component against. Trade-off analysis past 4 lines is upstream work for the `andthen:architecture --mode trade-off` skill; reference the resulting ADR instead.

The optional `**Flow**:` block (~10 lines, outside that cap) is the one home of the component or step order – Approach names the design, never the sequence. It carries order and seams only; a rationale there is trade-off analysis leaking past the cap.


## Key Generation Guidelines

**Cross-consumer surface inventory** – for a cross-cutting rename or restructure, search the repo case-insensitively for every literal *before* writing tasks: the inventory IS the rename surface, and every match maps to a task or a documented exclusion.

1. **Outcomes, not code changes**: each task states what is TRUE when done, in state-of-the-world verbs, and the executor determines implementation: "Replace foo with bar" → "Module X uses bar (foo retired)".
2. **Task brevity**: the outcome in one clause, a pattern reference (`file#symbol`) where one applies, a dependency on an earlier task, `Verify`, `SATISFIES`; more means too large (split) or too detailed (state the outcome). The outcome's acceptance clauses live in what `SATISFIES` names, which is what the In-FIS tie-breaker reads, and in what `Verify` asserts.
3. **`Verify`** – one of the three *Runnable Proof Forms* plus the assertion proving the task's outcome, never build success alone. **`SATISFIES`** – the `S<NN>` scenarios and `SC<NN>` Structural Criteria the task advances, comma-separated: the one trace between work and acceptance, in that direction only, so nothing can disagree with it.

   **Coverage is clause-level, by reference.** A task's `Verify` covers every acceptance-significant clause of what its `SATISFIES` names, not the title's gist. A Verify may name a target whole instead of re-typing its Then only when its test will assert every clause – confirmed at authoring for an existing test (*Resolve at authoring time*) – and then states only what the target does not: how it is observed (the fake, the recorded argv, the captured prompt) and any clause it adds. Otherwise it spells out the clauses it covers. A task satisfying "the record is created *and* linked to its owner" whose Verify proves only creation leaves the join unbuilt and still completes green – that omission is the failure this binding exists to catch.

   **Assertions name outcomes.** Literal values belong only to contracts (column names, mandated errors); apply *Diff-scoped leanness*.

   - ``**Verify**: `cmd: traces list --limit 1` – output includes columns IN_TOKENS, OUT_TOKENS, CACHE_R, CACHE_W``

4. A FIS is as short as completeness allows. Past ~18 tasks this is no longer one execution-sized spec: save anyway, emit `OVERSIZE:`, and recommend decomposition. Past ~6,000 words with the task count in range, the problem is prose and splitting leaves each half as long: apply **Single source of truth** first, every cut naming the home that keeps its clause, re-save, and fire the signal only on what remains.
5. **What We're NOT Doing**: exclusions and deferrals an executor could plausibly build, with reasons; a surface nothing touches needs no "unchanged" line.


## Constraints & Gotchas Authoring

A bullet belongs in `## Constraints & Gotchas` only when **cross-cutting** (≥2 tasks – a shared test-harness, fixture, or execution-order constraint included) or naming a **non-obvious framework-level trap**; task-local concerns live in their task, since accumulated task-local notes bury the real cross-cutting traps.


## Plan-Spec Alignment Check (when FIS originated from a plan story)

A plan-derived FIS's scenarios and criteria cover the story's scope, Source refs, and every applicable Binding Constraint. Where they fall short, expand the FIS or add an explicit narrowing note for the plan's cross-cutting review; never narrow silently.


## Reverse Coverage Check (phantom-scope guard)

Reverse coverage catches FIS work no upstream asked for: each scenario and Structural Criterion must trace to a plan story scope, Source ref, Binding Constraint, PRD outcome, or (standalone) feature-request element; one that traces to none is **phantom scope**.

- **Batch subagent mode** (from the `andthen:plan` skill): trace against plan-level sources plus each `bindingConstraints[].anchor` resolved against the PRD. Remove each candidate or return it as a `PHANTOM_SCOPE` entry in the completion summary – **never edit `plan.json` or `prd.md` from a subagent**; the orchestrator resolves it.
- **Standalone**: remove, or raise with the user and on approval add a scope note for plan/PRD amendment.
- **Standalone with no plan or PRD**: accept only what traces to a user- or business-observable outcome in the feature request. "Uses X library", "refactors Y" are phantom absent a user-facing reason.


## Self-Check

Read with *Proof-surface runnability* in `fis-contract.md`:

- **Task ↔ Scenario coverage** – every task's `SATISFIES` names ≥1 existing `S<NN>` or `SC<NN>`. A task naming nothing is unproven scope, one naming a missing target is broken wiring; a task fitting neither kind is split, removed, or anchored.
- **Verify lines stay unrun** – they are exec-time checks, and authoring proves the *design* of the surface, never its result. A `cmd:` absence check inverts its search's exit: no match exits 1.
- **Prose-vs-Verify scope alignment** – "rename all X" / "strip all Y" gets a Verify enforcing that same scope, not a narrower sample.
- **Conditional-section discipline** – a section the template marks "Omit" is absent unless its condition holds; a retained empty heading reads as a gap and gets filled with filler on the next pass.
