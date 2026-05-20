# FIS Authoring Guidelines

Shared authoring guidelines for generating Feature Implementation Specifications (FIS). Referenced by `spec` (standalone) and `plan` (batch FIS generation).

## Contents

- FIS Authoring Principles
- Feature Overview and Goal Authoring – Intent + Expected Outcomes; outcomes as scenario anchor
- Cross-Document References – two-tier model + authoring rules + why inlined text is authoritative
- Acceptance Scenarios and Proof-of-Work – canonical shape, BDD principles, negative-path checklist
- Architecture Decision Authoring – 3-4 line cap, ADR escalation
- Key Generation Guidelines – outcome-shape audit, Verify prescribed-detail audit, size signal
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
- **Expected Outcomes** – 2-4 bulleted user-/business-observable success conditions, each `[OC<NN>]`-tagged (same two-digit zero-padded convention as `S<NN>` / `TI<NN>`). The FIS's own internal contract – distinct from upstream PRD outcomes (inlined into Required Context) and from Acceptance Scenarios (concrete BDD examples exemplifying each outcome).

**Outcome ↔ Scenario coverage** – every Expected Outcome exemplified by ≥1 scenario tagged with its `[OC<NN>]`; every scenario tags ≥1 outcome. Untagged scenarios are decoupled from intent; unexemplified outcomes are unproven.

**Outcomes vs. Structural Criteria** – Outcomes are *behavioral* and user-/business-facing (proved by scenarios). Structural Criteria are *non-behavioral* invariants/regression guards (proved by task Verify lines). Worked boundary: "User can export filtered results as CSV" is an Outcome; "Existing `/users` API contract is unchanged" is a Structural Criterion. If the user would notice the behavior, it's an Outcome; if they only notice when it breaks, it's a Structural Criterion.

**In-FIS tie-breaker** – when a scenario or task is ambiguous at execution time, Expected Outcomes resolve in favor of the named success condition before raising `CONFUSION:`. *Behavioral* tasks: indirect lookup (`[TI<NN>]` on scenarios → those scenarios' `[OC<NN>]` → matching outcomes). *Structural* tasks (no scenario tag; Verify proves a Structural Criterion): the resolving anchor is the Structural Criterion's text. If the resolving outcome/criterion is itself ambiguous, raise `CONFUSION:` – do not guess. The tie-breaker resolves *referent* ambiguity, not *text* ambiguity.


## Cross-Document References

Every cross-doc reference is a **trust boundary**: the intent behind it lives with the author, not the executor. Punting resolution ("see the plan") forces every downstream reader to re-discover what the author already knew.

### Two-tier model

- **Required Context** (load-bearing, inlined verbatim) – spans the executor *must* know. Pulled at spec time, inlined as a block, pinned with `<!-- source: path#anchor -->` and `<!-- extracted: <commit-sha when source is in this repo; YYYY-MM-DD otherwise> -->`. The inlined text is authoritative even if the source later drifts.
- **Deeper Context** (optional, anchored pointers) – supplementary, read-on-demand. Each bullet is `path/to/source.md#heading-slug – one-line description`.

### Authoring rules

1. **Anchors over line numbers.** `prd.md#error-handling`, `src/auth.ts#validateToken` survive source edits; `prd.md:42-78` rots on the first line shift. Anchor by heading slug (markdown), symbol or `Container.member` (code), unquoted dotted key path (YAML/JSON), or quoted `#"key.with.dots"` when the key contains dots. Fall back to `path:LINE-LINE` only when no stable identifier exists. Never use comma-joined fragments (`path#A,B`) – they break URL encoding on GitHub.

   **Pair every reference with intent**: name *what the executor should learn* ("Dialog pattern – copy focus-trap + escape-key handling", not "Pattern for dialog handling").

   **Scope**: governs *new* authoring; pre-existing rows are not retroactive findings.

2. **Resolve at authoring time, not execution time.** Walk every reference, extract spans, decide required vs deeper. A bare "see the plan" without anchor or inlined content is not acceptable.

3. **Required Context unavailability test.** A span belongs in Required Context only if the executor cannot proceed without it should the source vanish. Otherwise it belongs in Deeper Context. This filters defensive copying.

4. **Inline budget.** Per block: typically 30-100 lines, hard cap 200. Total ≤ 250 lines. Not additive – two blocks at the per-block hard cap (400 lines) breach the total.

5. **Keep code pointers out of Required Context.** `src/foo.ts#parseFoo` pattern pointers belong in task descriptions or `Code Patterns & External References`. Required/Deeper Context is reserved for upstream *intent* documents (PRD, plan, ADRs, guidelines, glossary).

6. **Omit empty sections.** No load-bearing spans → omit Required Context entirely. Same for Deeper Context. Standalone FIS with no PRD/plan upstream typically have neither.

7. **One focus per block.** Each `### From ...` block carries one decision/constraint/contract. Split when one source span carries multiple distinct intents.

### Why the inlined text is authoritative

A FIS is a contract with the executor. The text the author pulled at spec time is the intent the FIS commits to, even if the upstream later changes. Drift is a *review* signal, not an *execution* failure.


## Acceptance Scenarios and Proof-of-Work

Each scenario: one behavior, concrete Given/When/Then using actual codebase identifiers. Order: happy path, edge cases, ≥1 error case. 3-7 scenarios. If you can't write the **Then**, surface as ambiguity.

**Canonical shape** – every scenario is a single top-level checkbox under `## Acceptance Scenarios` whose bold label carries a scenario ID, `[OC<NN>(,OC<NN>)*]`, then `[TI<NN>(,TI<NN>)*]`, followed by nested Given/When/Then. Tag groups appear as separate bracketed tokens, outcomes before tasks. The bold label functions as a pseudo-heading while remaining a checkbox – letting `ops update-fis all` flip per-scenario checkboxes. See [`fis-template.md`](${CLAUDE_PLUGIN_ROOT}/references/fis-template.md) for the display form. Do NOT emit scenarios as `### S<NN> ...` headers – that breaks the checkbox proof shape.

### Scenario Authoring Principles

Dan North's "Introducing BDD" (2006) anchors scenarios in concrete examples; Liz Keogh's "Acceptance Criteria vs. Scenarios" (2011) separates abstract rules from concrete examples. Apply these:

- **Concrete over Abstract** – use actual data: "Given Fluffy is 3 weeks old" not "Given an animal under selling age".
- **Observable Boundary** – assert visible behavior: "Then checkout rejects the sale" not "Then `AgePolicy.validate()` returns false".
- **Declarative over Imperative** – state precondition, event, outcome: "When checkout runs" not "When the test constructs mocks and calls methods".

**Negative-path checklist** – after drafting, add one scenario per uncovered category (the riskiest gap), not one per parameter:

- **Omitted optional inputs** – null/absent case with a fragile default?
- **No-match cases** – selectors/filters/lookups where "nothing matches" falls through to an unintended default?
- **Rejection paths** – external integration points where unmatched/invalid input should be explicitly ignored or rejected?

**Proof-of-Work**: each scenario's nested Given/When/Then IS the proof contract. Each Structural Criterion is proved by a task Verify line. `[OC<NN>]` anchors the proof to the Expected Outcome(s) exemplified; `[TI<NN>]` maps it to producing tasks. Together they close Intent → Outcomes → Scenarios → Tasks.

**Traceability**: legacy plan **Key Scenarios** or acceptance criteria are seeds – map each retained seed to ≥1 FIS Acceptance Scenario.


## Architecture Decision Authoring

**Default: 3-4 lines max.** One `**Approach**:` line; optional `**Why this over alternatives**:` carrying the causal narrative. If trade-off analysis exceeds 4 lines, it is upstream work for `andthen:architecture --mode trade-off`. Reference the resulting ADR; do not perform the analysis inline.


## Key Generation Guidelines

1. **Outcomes, not code changes**: each task describes what must be TRUE when done. The executor determines implementation.
2. **Outcome-shape audit on task titles**: ban implementation verbs (`Replace`, `Refactor`, `Update`, `Modify`, `Add to`). Use state-of-the-world verbs. "Replace foo with bar" → "Module X uses bar (foo retired)".
3. **Task brevity**: 1-3 lines per task – outcome, pattern reference (`file#symbol`), Verify line. >3 lines means too large (split) or too detailed (describe outcome).
4. Each task atomic, self-contained, with `file#symbol` pattern references. Order so later tasks build on earlier ones without hidden dependencies (see Task Ordering).
5. Reference patterns; do not reproduce them.
6. Every task has a **`Verify:`** line – a concrete observable check proving the outcome. **Verify must assert the described behavior, not just build success.** Trace to Acceptance Scenarios where applicable.

   **Verify prescribed-detail audit**: every prescribed value (column name, format string, error message, file path, flag value) named in the FIS appears verbatim in ≥1 Verify line.

   - Weak: `Verify: traces list shows token breakdown`
   - Strong: `Verify: traces list output includes columns IN_TOKENS, OUT_TOKENS, CACHE_R, CACHE_W`

7. Good FIS files land in 200-500 lines. Past ~700 lines or ~18 tasks signals this is no longer one execution-sized spec. Save anyway, but emit `OVERSIZE:` and recommend: standalone → `/andthen:prd → /andthen:plan → /andthen:exec-plan`; `story <id> of plan.json` → revisit the plan and decompose.
8. **What We're NOT Doing**: 3-5 specific exclusions/deferrals with reasons.

## Constraints & Gotchas Authoring

Bullets belong in `## Constraints & Gotchas` only when **cross-cutting** (≥2 tasks) OR naming a **non-obvious framework-level trap**. Task-local concerns live in task descriptions. Accumulating task-local notes diffuses attention from real cross-cutting traps.


## Task Ordering

Order tasks so implementation proceeds sequentially without hidden orchestration metadata. Foundational first, then widening, then polish/integration. Keep related tasks adjacent.

When a later task consumes something from an earlier one (API, type, component), state it explicitly in the later task's description. Example: TI01 creates `effectiveConcurrency()`; TI03 says "Dispatch loop MUST use `effectiveConcurrency()` from TI01 for concurrency cap."


## Plan-Spec Alignment Check (when FIS originated from a plan story)

Before finalizing, cross-check the plan story brief, its Source refs, and applicable Binding Constraints against the FIS:
- FIS scenarios + criteria deliver the story scope and every applicable Binding Constraint.
- If the FIS can't fully satisfy the scope: (a) expand the FIS, or (b) add a scope note explaining the narrowing and flag for the `andthen:plan` cross-cutting review.
- Do not finalize a FIS that silently narrows a plan story or Binding Constraint.


## Reverse Coverage Check (phantom-scope guard)

Forward coverage (Work Areas → tasks) catches plan criteria the FIS misses. Reverse coverage catches the opposite: FIS work no upstream asked for.

For each FIS scenario and Structural Criterion, name the plan story scope, Source ref, Binding Constraint, PRD outcome, or (standalone) feature-request element it serves. Any unnamed criterion is **phantom scope**.

The Outcome ↔ Scenario coverage rule (see *Feature Overview and Goal Authoring*) is enforced by Self-Check; not part of phantom-scope tracing.

**Resolution by mode:**

- **Batch sub-agent mode** (from `andthen:plan`): check against plan-level sources + `bindingConstraints[]` (each entry's `verbatim` + `anchor`). Only criteria with no plan-level *and* no Binding Constraints source are candidates. For each: (a) remove, or (b) return a `PHANTOM_SCOPE` entry in the completion summary so the orchestrator can escalate. **Do not edit `plan.json` or `prd.md` from a sub-agent** – phantom-scope resolution flows through the orchestrator.
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
- **Canonical scenario shape** – matches *Acceptance Scenarios and Proof-of-Work* above (outcomes before tasks); no `### S<NN>` headers; negative-path checklist applied; every prescribed value appears verbatim in ≥1 Verify line.
- **Outcome-shape audit on task titles** – no titles starting with `Replace`, `Refactor`, `Update`, `Modify`, `Add to`.
- **Anchor and Verify dry-run audit** – every cited `path#anchor` resolves against the actual source heading slug; every `rg`/`grep`/shell command in a Verify was executed against the current source and the prose claim matches the output. Catches `rg -c` exit-semantics traps (no match exits 1, does not print `0`), case-sensitivity mismatches, stale line numbers.
- **Cross-consumer surface inventory** (cross-cutting renames/restructures across multiple consuming skills/references) – before writing tasks, sweep with `grep -rni` for every literal string being renamed; the inventory IS the rename surface; every match maps to a task or a documented exclusion. Skip when the FIS is local to one surface.
- **Prose-vs-Verify scope alignment** – when an audit says "rename all X" / "strip all Y", the Verify enforces the same scope (not narrower).
- **Empty-section discipline** – sections with "**Leave empty** when…" prompts stay empty in the typical case. Fill only when the named condition holds. Empty headings are a feature, not a gap.

### Confidence Check
Rate the FIS 1-10 for single-pass success:
- **9-10**: all context present, clear decisions, automated validation
- **7-8**: good detail, minor clarifications possible
- **<7**: missing context or unclear architecture – revise

**If <7**: revise or ask for clarification. **If <7 AND oversized**: see Key Generation Guidelines #7.
