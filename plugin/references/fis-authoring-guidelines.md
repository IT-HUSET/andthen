# FIS Authoring Guidelines

Shared authoring guidelines for generating Feature Implementation Specifications (FIS). Referenced by `spec` (standalone), `plan` (batch FIS generation), `ops` (FIS checkbox mutation), and `review` (FIS conformance).

## Contents

- FIS Authoring Principles
- Feature Overview and Goal Authoring – Intent + Expected Outcomes; outcomes as scenario anchor
- Cross-Document References – required vs. deeper references; reference substitution
- Acceptance Scenarios and Proof-of-Work – compact bound shape, BDD principles, negative-path checklist
- Architecture Decision Authoring – 3-4 line cap, ADR escalation
- Key Generation Guidelines – outcome-shape audit, Verify outcome rule, size signal
- Constraints & Gotchas Authoring
- Task Ordering
- Plan-Spec Alignment Check (when FIS originated from a plan story)
- Reverse Coverage Check (phantom-scope guard)
- Forward Coverage – Work Areas
- Self-Check – named principles + Confidence Check


## FIS Authoring Principles

FIS is an executable spec: intent over implementation, references over content, decisions not explanations.

> **FIS Mutability**: see [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md) – *FIS Mutability Contract*.


## Feature Overview and Goal Authoring

The `## Feature Overview and Goal` section is the FIS's intent anchor. Two load-bearing sub-blocks – do not collapse into prose.

- **Intent** – one sentence naming *why* the feature exists: the problem solved or user/business value unlocked. Not a scope summary, not a title restatement. If it reads identically to the feature name, it is missing.
- **Expected Outcomes** – 2-4 bulleted user-/business-observable success conditions, each `[OC<NN>]`-tagged (same two-digit zero-padded convention as `S<NN>` / `TI<NN>`). The FIS's own internal contract – distinct from upstream PRD outcomes (linked from Required Context) and from Acceptance Scenarios (concrete examples exemplifying each outcome).

**Outcome ↔ Scenario coverage** – every Expected Outcome exemplified by ≥1 scenario tagged with its `[OC<NN>]`; every scenario tags ≥1 outcome. Untagged scenarios are decoupled from intent; unexemplified outcomes are unproven.

**Outcomes vs. Structural Criteria** – Outcomes are *behavioral* and user-/business-facing (proved by scenarios). Structural Criteria are *non-behavioral* invariants/regression guards (proved by task Verify lines). Worked boundary: "User can export filtered results as CSV" is an Outcome; "Existing `/users` API contract is unchanged" is a Structural Criterion. If the user would notice the behavior, it's an Outcome; if they only notice when it breaks, it's a Structural Criterion.

**In-FIS tie-breaker** – when a scenario or task is ambiguous at execution time, Expected Outcomes resolve in favor of the named success condition before raising `CONFUSION:`. *Behavioral* tasks: indirect lookup (`[TI<NN>]` on scenarios → those scenarios' `[OC<NN>]` → matching outcomes). *Structural* tasks (no scenario tag; Verify proves a Structural Criterion): the resolving anchor is the Structural Criterion's text. If the resolving outcome/criterion is itself ambiguous, raise `CONFUSION:` – do not guess. The tie-breaker resolves *referent* ambiguity, not *text* ambiguity.


## Cross-Document References

A cross-document reference is a **trust boundary**: resolve it while authoring with an anchor and intent, never a bare "see the plan".

### Two-tier model

- **Required Context** – load-bearing anchored references the executor reads before implementation. Each bullet is ``- `path#anchor` – what to learn and why it constrains this FIS``.
- **Deeper Context** – supplementary anchored references read on demand, using the same shape.

### Reference substitution

Prefer a durable, addressable artifact over a description or copied extract: an executable test over restated acceptance prose, a function over pseudocode, an HTML mockup over a visual description. The FIS states the intent and delta; the reference carries the detail.

1. **Anchors over line numbers.** Emit local reference and Proof paths as repo-root-relative POSIX paths. Anchor Markdown by heading, code by symbol, and YAML/JSON by dotted key path; use lines only without a stable identifier. Never comma-join fragments (`path#A,B`). Every reference names what to learn. Consumers probe repo root and FIS directory: one match wins, zero is broken, two distinct matches ambiguous.
2. **Resolve at authoring time.** Open every reference and run every Proof binding. Required sources must be durable and available to the executor. Pin cross-repo ports by commit and name the parity expectation; for UI work, prefer a real HTML mockup from the `andthen:ui-ux-design` skill.
3. **Do not duplicate the source.** If the durable reference carries the needed detail, omit the equivalent FIS prose. Without a durable address, inline only the irreducible span (≤20 lines each, ≤40 total) using the existing H3 + `source` / `extracted` comments + blockquote shape. Exact issue-transported requirements may exceed these budgets when no durable source exists; never narrow or omit them.
4. **Either tier may contain code, tests, docs, ADRs, or mockups.**
5. **Omit empty sections.** Standalone FIS files with no upstream context commonly need neither tier.

Existing inline blocks remain valid. Missing/conflicting Required targets are spec-stale `CONFUSION:`; a followed broken Deeper target warns.


## Acceptance Scenarios and Proof-of-Work

Use 3-7 single-behavior scenarios: happy path, edges, then ≥1 error. If neither prose nor executable proof states the observable outcome, surface the ambiguity.

**Canonical shape** – one top-level checkbox with a bold label carrying ID, `[OC<NN>(,OC<NN>)*]`, then `[TI<NN>(,TI<NN>)*]`. It is the mutable pseudo-heading; never use `### S<NN>`.

- **Unbound** – nest concrete Given/When/Then.
- **Fully bound** – precise title + Proof only when the title itself states every acceptance-significant precondition, action, observable outcome, and required mechanism. Add GWT whenever the title cannot carry that contract clearly; the inspected target is evidence, never the contract's only home.
- **Supplemented** – add only missing Given/When/Then detail before Proof; never transcribe the test.

### Scenario Authoring Principles

- **Concrete over Abstract** – unbound scenarios use actual data: "Fluffy is 3 weeks old", not "an animal under selling age". Proof may carry the data.
- **Observable Boundary** – assert visible behavior: "Then checkout rejects the sale" not "Then `AgePolicy.validate()` returns false".
- **Declarative over Imperative** – state precondition, event, outcome, not test mechanics.
- **Mechanism Fidelity** – for a required mechanism (LLM turn, algorithm, external call), title or GWT must distinguish it from a trivial substitute; Proof verifies that articulated mechanism.

**Negative-path checklist** – after drafting, add one scenario per uncovered category (the riskiest gap), not one per parameter:

- **Omitted optional inputs** – null/absent case with a fragile default?
- **No-match cases** – selectors/filters/lookups where "nothing matches" falls through to an unintended default?
- **Rejection paths** – external integration points where unmatched/invalid input should be explicitly ignored or rejected?

**Proof Binding** – bind an existing test/suite as ``- **Proof**: `path[#test-name]` – <state>``; bare suites are valid. Resolve and run it before finalizing. States:

- `red at spec time` – new behavior/bug repro; failure matches the scenario contract or expected symptom. A suite identifies the covering failure.
- `green – parity/regression` – behavior-preservation only (ports, refactors, conformance); it cannot prove new behavior.

Bindings are never aspirational; brevity never excuses an ambiguous title or weak test.

**Proof-of-Work**: title plus any GWT is the complete articulated contract; Proof is executable evidence and never owns acceptance semantics. Task Verify lines prove Structural Criteria. `[OC<NN>]` and `[TI<NN>]` close Intent → Outcomes → Scenarios → Tasks.

**Traceability**: legacy plan **Key Scenarios** or acceptance criteria are seeds – map each retained seed to ≥1 FIS Acceptance Scenario.


## Architecture Decision Authoring

**Default: 3-4 lines max.** One `**Approach**:` line; optional `**Why this over alternatives**:` carrying the causal narrative. If trade-off analysis exceeds 4 lines, it is upstream work for the `andthen:architecture --mode trade-off` skill. Reference the resulting ADR; do not perform the analysis inline.


## Key Generation Guidelines

1. **Outcomes, not code changes**: each task describes what must be TRUE when done. The executor determines implementation.
2. **Outcome-shape audit on task titles**: ban implementation verbs (`Replace`, `Refactor`, `Update`, `Modify`, `Add to`). Use state-of-the-world verbs. "Replace foo with bar" → "Module X uses bar (foo retired)".
3. **Task brevity**: 1-3 lines per task – outcome, pattern reference (`file#symbol`), Verify line. >3 lines means too large (split) or too detailed (describe outcome).
4. Each task atomic, self-contained, with `file#symbol` pattern references. Pin a task's **read-set** – critical callers, callees, registration/config sites – only for wiring the executor would not find by searching from the surfaces it already knows: implicit registration, generated or reflective call sites, a consumer in another package. Discoverable callers are the executor's job; an exhaustive read-set rots faster than it helps. Resolve-at-authoring-time (Cross-Document References rule 2) applies to code pointers too. Order so later tasks build on earlier ones without hidden dependencies (see Task Ordering).
5. Reference patterns; do not reproduce them.
6. Every task has a **`Verify:`** line – a concrete observable check proving the outcome. **Verify must assert the described behavior, not just build success.** Trace to Acceptance Scenarios where applicable.

   **Verify names the outcome, not the command transcript** – the executor picks the check at exec time. Prescribe a literal value only when the value *is* the contract (a column name a consumer parses, a mandated error string). Exact counts and line numbers bind the spec to today's code and rot on the first unrelated edit – assert presence, absence, or the covering invariant instead.

   - Weak: `Verify: traces list shows token breakdown`
   - Strong: `Verify: traces list output includes columns IN_TOKENS, OUT_TOKENS, CACHE_R, CACHE_W`
   - Rotting: `Verify: rg -c 'IN_TOKENS' src/ prints 3`

7. A FIS is as short as completeness allows; a reference-rich small feature may need only 30-150 lines. Judge size in **words** first – dense 150-character lines defeat a line count, and the word bar is set to match ~700 lines of ordinary prose, not to tighten the norm. Past ~6,000 words, ~700 lines, or ~18 tasks signals this is no longer one execution-sized spec. Save anyway, but emit `OVERSIZE:` and recommend: standalone → run the `andthen:prd` skill, `andthen:plan` skill, then `andthen:exec-plan` skill; `story <id> of plan.json` → revisit the plan and decompose.
8. **What We're NOT Doing**: 3-5 specific exclusions/deferrals with reasons.

## Constraints & Gotchas Authoring

Bullets belong in `## Constraints & Gotchas` only when **cross-cutting** (≥2 tasks) OR naming a **non-obvious framework-level trap**. Task-local concerns live in task descriptions. Accumulating task-local notes diffuses attention from real cross-cutting traps.


## Task Ordering

Order tasks so implementation proceeds sequentially without hidden orchestration metadata. Foundational first, then widening, then polish/integration. Keep related tasks adjacent.

When a later task consumes something from an earlier one (API, type, component), state it explicitly in the later task's description. Example: TI01 creates `effectiveConcurrency()`; TI03 says "Dispatch loop MUST use `effectiveConcurrency()` from TI01 for concurrency cap."


## Plan-Spec Alignment Check (when FIS originated from a plan story)

Before finalizing a plan-derived FIS, require its scenarios and criteria to cover story scope, Source refs, and every applicable Binding Constraint. Expand the FIS or add an explicit narrowing note and flag Step 6; never narrow silently.


## Reverse Coverage Check (phantom-scope guard)

Forward coverage (Work Areas → tasks) catches plan criteria the FIS misses. Reverse coverage catches the opposite: FIS work no upstream asked for.

For each FIS scenario and Structural Criterion, name the plan story scope, Source ref, Binding Constraint, PRD outcome, or (standalone) feature-request element it serves. Any unnamed criterion is **phantom scope**.

The Outcome ↔ Scenario coverage rule (see *Feature Overview and Goal Authoring*) is enforced by Self-Check; not part of phantom-scope tracing.

**Resolution by mode:**

- **Batch sub-agent mode** (from the `andthen:plan` skill): check against plan-level sources + `bindingConstraints[]` (each entry's `verbatim` + `anchor`). Only criteria with no plan-level *and* no Binding Constraints source are candidates. For each: (a) remove, or (b) return a `PHANTOM_SCOPE` entry in the completion summary so the orchestrator can escalate. **Do not edit `plan.json` or `prd.md` from a sub-agent** – phantom-scope resolution flows through the orchestrator.
- **Standalone mode**: (a) remove, or (b) raise with the user; on approval, add a scope note for plan/PRD amendment.
- **Standalone with no plan or PRD**: accept only if it traces to a user- or business-observable outcome in the feature request. "Uses X library", "refactors Y" are phantom absent a user-facing reason.


## Forward Coverage – Work Areas

`### Work Areas` is the FIS's forward-coverage anchor: 3-7 bullets naming components/files/surfaces changed (inventory, not behavior). Every Work Area maps to ≥1 implementing task or Acceptance Scenario. A Work Area with no implementing task/scenario is a **forward-coverage gap** – distinct from missing-test/missing-feature gaps.


## Self-Check

Named principles to verify before saving. Each names a failure mode.

- **Template structure** – follows Key Generation Guidelines (Architecture Decision 3-4 lines max, no over-specification, code snippets ≤5 lines).
- **Size signal** – emit `OVERSIZE:` if oversized per Key Generation Guidelines #7.
- **Intent vs. scope** – `**Intent**:` sentence names *why*; not a title/scope restatement.
- **Outcome ↔ Scenario coverage** – every `[OC<NN>]` exemplified by ≥1 scenario; every scenario carries ≥1 `[OC<NN>]` tag.
- **Task ↔ Scenario coverage**:
    - *Rule*: every `[TI<NN>]` is either (a) referenced by ≥1 scenario `[TI<NN>]` (behavioral) or (b) carries a Verify line that proves a Structural Criterion (structural/setup). Every scenario `[TI<NN>]` resolves to a real task.
    - *Failure modes*: unreferenced task that proves no criterion → unproven scope; scenario tag pointing at a missing task → broken wiring; task fitting neither path → decoupled, must be split/removed/anchored.
    - *Classification*: behavioral/structural split is exhaustive, set at authoring time, re-asserted by exec-spec Step 5a. No syntactic suffix on criteria – linkage lives in the Verify-line text matching the criterion.
- **Scope-consistency** – every Work Area exercised by a scenario or Verify line.
- **Canonical scenario shape** – outcomes before tasks; no `### S<NN>`; valid Proof omits only detail title + target encode; negative paths applied.
- **Reference substitution** – every durable source replaces copied detail; Required Context is anchored bullets by default; inline fallbacks stay within budget except exact issue transport.
- **Mechanism Fidelity** – matches *Scenario Authoring Principles* above (mechanism-distinguishing observable; no stub/copy-satisfiable scenario).
- **Outcome-shape audit on task titles** – no outcome-shaped violations per Key Generation Guidelines #2.
- **Anchor and Proof dry-run audit** – resolve every anchor and Proof target; run bound tests and confirm recorded state and red reason match. Do **not** run Verify lines – they are exec-time checks, and one writable only as a command transcript is over-prescribed (Key Generation Guidelines #6). Where a Verify does prescribe a shell check, mind `rg -c` exit semantics (no match exits 1, prints nothing).
- **Cross-consumer surface inventory** (cross-cutting renames/restructures across multiple consuming skills/references) – before writing tasks, sweep with `grep -rni` for every literal string being renamed; the inventory IS the rename surface; every match maps to a task or a documented exclusion. Skip when the FIS is local to one surface.
- **Prose-vs-Verify scope alignment** – when an audit says "rename all X" / "strip all Y", the Verify enforces the same scope (not narrower).
- **Conditional-section discipline** – sections with an "**Omit this entire section**" prompt are absent in the typical case; emit one only when its named condition holds. A retained empty heading reads as a gap and gets filled with filler on the next pass.

### Confidence Check
Rate the FIS 1-10 for single-pass success:
- **9-10**: all context present, clear decisions, automated validation
- **7-8**: good detail, minor clarifications possible
- **<7**: missing context or unclear architecture – revise

**If <7**: revise or ask for clarification. **If <7 AND oversized**: see Key Generation Guidelines #7.
