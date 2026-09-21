# FIS Authoring Guidelines

How to author a Feature Implementation Specification. The FIS contract – proof surfaces, scenario shape, proof forms, tags, and how a reader resolves references – is `fis-contract.md`.

## FIS Authoring Principles

FIS is an executable spec: intent over implementation, references over content, decisions not explanations.

**Single source of truth** – the executor holds the whole FIS in context and resolves every id, so no line has to stand alone, and a fact stated in two sections drifts into a contradiction the executor reconciles silently. Each fact has one home, and every other section names it by id instead of re-typing it – "scenario S01's readings", and another story always as "story S04", since stories and scenarios both number from `S01`:

- behavior – its Acceptance Scenario;
- a non-behavioral invariant – its Structural Criterion;
- a boundary and the story owning the other side – *What We're NOT Doing*;
- a cross-cutting or framework-level trap – *Constraints & Gotchas*;
- a choice the source underdetermines – *Architecture Decision*.

A task adds only what none of those carries. The contract's own restatements stay: an Expected Outcome, a scenario's Given/When/Then, a `Verify` or `Proof` assertion.


## Feature Overview and Goal Authoring

The `## Feature Overview and Goal` section is the FIS's intent anchor. Two sub-blocks, never collapsed into prose.

- **Intent** – one sentence naming *why* the feature exists: the problem solved or user/business value unlocked. Not a scope summary, not a title restatement. If it reads identically to the feature name, it is missing.
- **Expected Outcomes** – 2-4 bulleted user-/business-observable success conditions, each `[OC<NN>]`-tagged (same two-digit zero-padded convention as `S<NN>` / `TI<NN>`). The FIS's own internal contract – distinct from upstream PRD outcomes (linked from Required Context) and from Acceptance Scenarios (concrete examples exemplifying each outcome).

**Outcome ↔ Scenario coverage** – every Expected Outcome exemplified by ≥1 scenario tagged with its `[OC<NN>]`; every scenario tags ≥1 outcome. Untagged scenarios are decoupled from intent; unexemplified outcomes are unproven.


## Cross-Document References

**Reference substitution** – prefer a durable, addressable artifact over a description or copied extract: an executable test over restated acceptance prose, a function over pseudocode, an HTML mockup over a visual description. The FIS states the intent and delta; the reference carries the detail.

1. **Anchors over line numbers.** Local reference and Proof paths are repo-root-relative POSIX paths, anchored by heading (Markdown), symbol (code), or dotted key path (YAML/JSON); lines only where no stable identifier exists. Never comma-join fragments (`path#A,B`). Every reference names what to learn.
2. **Resolve at authoring time.** Open every reference and run every Proof binding; Required sources must be durable and available to the executor. Pin cross-repo ports by commit and name the parity expectation; for UI work, prefer a real HTML mockup from the `andthen:ui-ux-design` skill.
3. **Do not duplicate the source.** Where the durable reference carries the detail, omit the equivalent FIS prose. Without a durable address, inline only the irreducible span (≤20 lines each, ≤40 total) as a blockquote under an H3 naming its source path and the date extracted. Exact issue-transported requirements may exceed that budget when no durable source exists – never narrow or omit them.
4. **Omit empty sections.** Either tier may carry code, tests, docs, ADRs, or mockups; a standalone FIS with no upstream context commonly needs neither.


## Acceptance Scenario Authoring

One scenario per behavior: the happy path, the edges that matter, at least one error path. If neither prose nor executable proof states the observable outcome, surface the ambiguity.

### Scenario Authoring Principles

BDD canon applies, plus one rule it does not carry:

- **Mechanism Fidelity** – for a required mechanism (LLM turn, algorithm, external call), title or GWT must distinguish it from a trivial substitute, and Proof verifies that articulated mechanism. Without it a stub satisfies the scenario.

**Negative-path checklist** – after drafting, add one scenario for the riskiest gap in each uncovered category, not one per parameter: **omitted optional inputs**, **no-match cases** (a selector or lookup matching nothing and falling through), **rejection paths**.


## Architecture Decision Authoring

**Default: 3-4 lines max.** One `**Approach**:` line; a `**Why this over the floor**:` line whenever the approach is not the floor option (do nothing, or extend what exists), naming that floor and the requirement clause that rules it out – the self-review prices each component against that clause. If trade-off analysis exceeds 4 lines, it is upstream work for the `andthen:architecture --mode trade-off` skill. Reference the resulting ADR; do not perform the analysis inline.


## Key Generation Guidelines

**Cross-consumer surface inventory** – for a cross-cutting rename or restructure, sweep `grep -rni` for every literal *before* writing tasks: the inventory IS the rename surface, and every match maps to a task or a documented exclusion.

1. **Outcomes, not code changes**: each task states what is TRUE when done, in state-of-the-world verbs, and the executor determines implementation. Ban implementation verbs (`Replace`, `Refactor`, `Update`, `Modify`, `Add to`): "Replace foo with bar" → "Module X uses bar (foo retired)".
2. **Task brevity**: outcome, pattern reference (`file#symbol`), Verify line; anything beyond those three means too large (split) or too detailed (describe outcome). The outcome line names the state in one clause – its acceptance clauses live in what `SATISFIES` names, which is what the In-FIS tie-breaker reads, and in what `Verify` asserts.
3. Pin a task's **read-set** only for wiring the executor would not find by searching outward from surfaces it already knows – implicit registration, generated or reflective call sites, a consumer in another package. Discoverable callers are the executor's job; an exhaustive read-set rots faster than it helps.
4. Every task carries a **`Verify`** and a **`SATISFIES`**.

   **`Verify`** – one of the three *Runnable Proof Forms* plus the assertion proving the task's outcome, never build success alone.

   **`SATISFIES`** – the `S<NN>` scenarios and `SC<NN>` Structural Criteria this task advances, comma-separated. It is the one trace between work and acceptance, in that direction only, so nothing can disagree with it. The target kind *is* the task's classification – `S<NN>` behavioral, `SC<NN>` structural – so no separate label exists either.

   **Coverage is clause-level.** A task's `Verify` assertions cover every acceptance-significant clause of what its `SATISFIES` names, not the title's gist. A task satisfying "the record is created *and* linked to its owner" whose Verify proves only creation leaves the join unbuilt and still completes green – that omission is the failure this binding exists to catch.

   **Assertions name outcomes.** Literal values belong only to contracts (column names, mandated errors); apply *Diff-scoped leanness*.

   - ``**Verify**: `cmd: traces list --limit 1` – output includes columns IN_TOKENS, OUT_TOKENS, CACHE_R, CACHE_W``

5. A FIS is as short as completeness allows. Past ~18 tasks this is no longer one execution-sized spec: save anyway, emit `OVERSIZE:`, and recommend decomposition. Past ~6,000 words with the task count in range, the problem is prose and splitting leaves each half as long: apply **Single source of truth** first, every cut naming the home that keeps its clause, re-save, and fire the signal only on what remains.
6. **What We're NOT Doing**: specific exclusions/deferrals with reasons.


## Constraints & Gotchas Authoring

Bullets belong in `## Constraints & Gotchas` only when **cross-cutting** (≥2 tasks) OR naming a **non-obvious framework-level trap**. Task-local concerns live in task descriptions. Accumulating task-local notes diffuses attention from real cross-cutting traps.


## Task Ordering

Tasks are sequential, without hidden orchestration metadata. When a later task consumes something from an earlier one (API, type, component), the later task's description states it.


## Plan-Spec Alignment Check (when FIS originated from a plan story)

Before finalizing a plan-derived FIS, require its scenarios and criteria to cover story scope, Source refs, and every applicable Binding Constraint. Expand the FIS or add an explicit narrowing note and flag Step 6; never narrow silently.


## Reverse Coverage Check (phantom-scope guard)

Forward coverage catches plan criteria the FIS misses; reverse coverage catches the opposite – FIS work no upstream asked for. For each FIS scenario and Structural Criterion, name the plan story scope, Source ref, Binding Constraint, PRD outcome, or (standalone) feature-request element it serves. Any unnamed criterion is **phantom scope**.

- **Batch subagent mode** (from the `andthen:plan` skill): check against plan-level sources plus each `bindingConstraints[].anchor` resolved against the PRD. Candidates are criteria with neither source. Either remove them or return a `PHANTOM_SCOPE` entry in the completion summary – **never edit `plan.json` or `prd.md` from a subagent**; resolution flows through the orchestrator.
- **Standalone**: remove, or raise with the user and on approval add a scope note for plan/PRD amendment.
- **Standalone with no plan or PRD**: accept only what traces to a user- or business-observable outcome in the feature request. "Uses X library", "refactors Y" are phantom absent a user-facing reason.


## Self-Check

Read with *Proof-surface runnability* in `fis-contract.md`:

- **Task ↔ Scenario coverage** – every task's `SATISFIES` names a real `S<NN>` or `SC<NN>`. Task naming nothing → unproven scope; a target that does not exist → broken wiring; task fitting neither kind → decoupled, so split, remove, or anchor it.
- **Verify lines stay unrun** – they are exec-time checks, and authoring proves the *design* of the surface, never its result. Where a Verify's command form wraps a shell check, mind `rg -c` exit semantics (no match exits 1, prints nothing).
- **Prose-vs-Verify scope alignment** – "rename all X" / "strip all Y" gets a Verify enforcing that same scope, not a narrower sample.
- **Conditional-section discipline** – a section carrying an "**Omit this entire section**" prompt is absent in the typical case; a retained empty heading reads as a gap and gets filled with filler on the next pass.
