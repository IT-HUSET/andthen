# FIS Authoring Guidelines

Shared authoring guidelines for generating Feature Implementation Specifications (FIS). Referenced by `spec` (standalone) and `plan` (batch FIS generation).

## Contents

- FIS Authoring Principles
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


## Cross-Document References

Every reference from a FIS to another document (PRD, plan, research, ADRs, guidelines, glossary) is a **trust boundary**: the intent behind that reference lives with the author, not the executor. Punting the resolution ("see the plan") forces every downstream reader – exec-spec, review, remediate-findings, council reviewers – to re-discover what the author already knew.

### Two-tier model

- **Required Context** (load-bearing, inlined verbatim) – spans the executor *must* know to act on the FIS. Pulled from the source at spec time, inlined as a block in the FIS, pinned with `<!-- source: path#anchor -->` and `<!-- extracted: <commit-sha when source is in this repo; YYYY-MM-DD otherwise> -->` comments for audit. The inlined text is authoritative at execution time even if the source later drifts.
- **Deeper Context** (optional, anchored pointers) – supplementary material available if the inlined Required Context leaves a gap. Each bullet is `path/to/source.md#heading-slug – one-line description`. Readers resolve on demand.

### Authoring rules

1. **Anchors over line numbers.** `prd.md#error-handling` and `src/auth.ts#validateToken` survive source edits; `prd.md:42-78` rots on the first line shift. Anchor by heading slug (markdown), symbol or `Container.member` (code), unquoted dotted key path (YAML/JSON), or quoted `#"key.with.dots"` when the key itself contains dots. Fall back to `path:LINE-LINE` only when no stable identifier exists. Never use comma-joined fragments (`path#A,B`) – they break URL encoding when published to GitHub.

   **Pair every reference with intent**: the why column states *what the executor should learn* from this pointer, not just a label ("Dialog pattern – copy focus-trap + escape-key handling", not "Pattern for dialog handling").

   **Scope**: this rule governs *new* FIS authoring. Reference rows pre-existing in a FIS are not retroactive findings.

2. **Resolve at authoring time, not execution time.** Before emitting the FIS, walk every cross-doc reference, extract the span, and decide required vs deeper. A bare "see the plan" without anchor or inlined content is not acceptable.

3. **Required Context unavailability test.** A span belongs in Required Context only if the executor cannot proceed without it should the source vanish at execution time. If the executor can read the source on demand without losing intent, the pointer belongs in Deeper Context. This filters defensive copying.

4. **Inline budget.** Per block: typically 30-100 lines, hard cap 200 lines. Total across all blocks: ≤ 250 lines. The per-block cap and total are not additive – two blocks at the per-block hard cap (400 lines) breach the total and must be cut down.

5. **Keep code pointers out of Required Context.** `src/foo.ts#parseFoo` pattern pointers belong inside task descriptions or in `Code Patterns & External References`. Required/Deeper Context is reserved for upstream *intent* documents (PRD, plan, ADRs, guidelines, glossary).

6. **Omit empty sections.** If a FIS has no load-bearing upstream spans to inline, omit the Required Context section entirely rather than leaving a stub. Same for Deeper Context. Standalone FIS with no PRD/plan upstream typically have neither section.

7. **One focus per block.** Each `### From ...` Required Context block carries one decision, constraint, or contract. Multiple decisions in one block obscure the intent the block is preserving – split into separate blocks when the same source span carries multiple distinct intents.

### Why the inlined text is authoritative

A FIS is a contract with the executor. If the author pulls text from `prd.md` or a story scope from `plan.json` at spec time, that's the intent the FIS is committing to – even if the upstream source later changes. Drift between the pinned span and the current source is a *review* signal, not an *execution* failure.


## Acceptance Scenarios and Proof-of-Work

Each scenario: one behavior, concrete Given/When/Then using actual codebase identifiers. Cover happy path first, then edge cases, then at least one error case. 3-7 scenarios is the sweet spot. If you can't write the **Then** clause, surface it as ambiguity.

**Canonical shape** – every scenario is a single top-level checkbox under `## Acceptance Scenarios` whose bold label carries a stable scenario ID and a comma-separated task-tag list, followed by nested Given/When/Then bullets. The bold label functions as a pseudo-heading while remaining a checkbox – satisfying the structural-integrity gate (any `- [ ] ` in span) and letting `ops update-fis all` flip checkboxes per scenario. See [`fis-template.md`](${CLAUDE_PLUGIN_ROOT}/references/fis-template.md) for the display form and worked example. Do NOT emit scenarios as `### S<NN> ...` markdown headers – that breaks the checkbox proof shape.

### Scenario Authoring Principles

Dan North's "Introducing BDD" (2006) anchors scenarios as Given/When/Then examples; Liz Keogh's "Acceptance Criteria vs. Scenarios" (2011) separates abstract rules from concrete examples. Apply these:

- **Concrete over Abstract** – use actual data: "Given Fluffy is 3 weeks old" instead of "Given an animal under selling age".
- **Observable Boundary** – assert visible behavior: "Then checkout rejects the sale" instead of "Then `AgePolicy.validate()` returns false".
- **Declarative over Imperative** – state precondition, event, outcome: "When checkout runs" instead of "When the test constructs mocks and calls methods".

**Negative-path checklist** – after drafting scenarios, review for these three categories. Add one scenario per uncovered category (the riskiest gap), not one per parameter:

- **Omitted optional inputs**: null/absent case producing a fragile default?
- **No-match cases**: selectors, filters, or lookups where "nothing matches" falls through to an unintended default?
- **Rejection paths**: external integration points where unmatched/invalid input should be explicitly ignored or rejected?

**Proof-of-Work**: each Acceptance Scenario's nested Given/When/Then IS the proof contract – the test/verification the executor produces must satisfy it. Each Structural Criterion is proved by a task Verify line. The scenario's `[TI<NN>]` tag set maps proofs to the tasks that produce them, so proof is produced incrementally.

**Traceability**: if a legacy plan includes **Key Scenarios** or acceptance criteria, treat them as seeds and map each retained seed to at least one FIS Acceptance Scenario – don't silently drop them.


## Architecture Decision Authoring

**Default: 3-4 lines max.** One `**Approach**:` line, optionally followed by a `**Why this over alternatives**:` line carrying the load-bearing causal narrative. If trade-off analysis genuinely exceeds 4 lines, it is upstream work for the `andthen:architecture` skill in `--mode trade-off`. Reference the resulting ADR from the FIS; do not perform the analysis inline.


## Key Generation Guidelines

1. **Outcomes, not code changes**: Each task describes what must be TRUE when done, not what code to write. The executing agent determines the implementation.
2. **Outcome-shape audit on task titles**: ban implementation verbs in titles – `Replace`, `Refactor`, `Update`, `Modify`, `Add to`. Required: state-of-the-world verbs. "Replace foo with bar" should be rewritten as "Module X uses bar (foo retired)".
3. **Task brevity**: Each task description is 1-3 lines. State the outcome, reference the pattern (`file#symbol` – see Cross-Document References rule #1), include the Verify line. If a task exceeds 3 lines, it is either too large (split) or too detailed (describe outcome, not steps).
4. Each task: atomic, self-contained, with `file#symbol` references to patterns to follow. Order tasks so later tasks can build on earlier ones without hidden dependencies (see Task Ordering).
5. Reference patterns, don't reproduce them.
6. Each task must include a **`Verify:`** line – a concrete, observable check proving the outcome. **Verify lines must assert the described behavior, not just build success.** Trace verification back to Acceptance Scenarios where applicable.

   **Verify prescribed-detail audit**: every prescribed value (column name, format string, error message, file path, flag value, exact string) named in the FIS appears verbatim in at least one Verify line. A proof check that doesn't name the prescribed detail lets the implementation satisfy the task in spirit while missing the contract.

   - Weak: `Verify: traces list shows token breakdown`
   - Strong: `Verify: traces list output includes columns IN_TOKENS, OUT_TOKENS, CACHE_R, CACHE_W`

7. Most good FIS files land in 200-500 lines. Once a draft pushes past ~700 lines or ~18 tasks, that is a strong signal this is no longer one execution-sized spec. Save the FIS regardless, but warn the user and recommend a path: for standalone feature requests, switch to the `/andthen:prd → /andthen:plan → /andthen:exec-plan` chain; for `story {story_id} of plan.json` inputs, revisit the source plan and decompose before regenerating.
8. **What We're NOT Doing** is explicit: 3-5 specific exclusions or deferrals with reasons.

## Constraints & Gotchas Authoring

A bullet belongs in `## Constraints & Gotchas` only if it is **cross-cutting** (applies to ≥2 tasks) OR names a **non-obvious framework-level trap**. Task-local concerns – patterns to follow, specific files to touch, single-task gotchas – live in the task description. Letting the section accumulate task-local notes diffuses attention away from the genuinely cross-cutting traps.


## Task Ordering

After defining individual tasks (TI01, TI02...), order them so implementation can proceed sequentially without hidden orchestration metadata. Put foundational tasks first, then widening tasks, then polish/integration. Keep related tasks adjacent when they share context.

When a later task must consume something from an earlier task (an API, a type, a component), state this explicitly in the later task's description. Don't rely on the executing agent discovering it from context. Example: if TI01 creates `effectiveConcurrency()`, TI03 should say "Dispatch loop MUST use `effectiveConcurrency()` from TI01 for concurrency cap."


## Plan-Spec Alignment Check (when FIS originated from a plan story)

Before finalizing, cross-check the plan story brief, its Source refs, and any applicable Binding Constraints against the FIS:
- Verify the FIS Acceptance Scenarios and Structural Criteria deliver the story scope and every applicable Binding Constraint.
- If the FIS cannot fully satisfy the story scope, either: (a) expand the FIS scope, or (b) add a scope note explaining the narrowing and flag it for the `andthen:plan` cross-cutting review.
- Do not finalize a FIS that silently narrows a plan story or Binding Constraint.


## Reverse Coverage Check (phantom-scope guard)

Forward coverage (Work Areas → tasks) catches plan criteria the FIS misses. Reverse coverage catches the opposite: FIS work no upstream asked for.

For each FIS Acceptance Scenario and Structural Criterion, name the plan story scope, Source ref, Binding Constraint, PRD outcome, or (standalone) feature-request element it serves. Any unnamed criterion is **phantom scope**.

**Resolution depends on mode:**

- **Batch sub-agent mode** (from the `andthen:plan` skill) – check against plan-level sources plus the `bindingConstraints[]` array in `plan.json` (each entry's `verbatim` text and `anchor` are the binding source). Only criteria with no plan-level *and* no Binding Constraints source are candidates for phantom-scope reporting. For each candidate: (a) remove, or (b) return a `PHANTOM_SCOPE` entry in your completion summary so the orchestrator can escalate. **Do not edit `plan.json` or `prd.md` from a sub-agent** – phantom-scope resolution flows through the orchestrator.
- **Standalone mode**: (a) remove, or (b) raise with the user and – on approval – add a scope note for plan/PRD amendment.
- **Standalone with no plan or PRD**: accept the criterion only if it traces to a user- or business-observable outcome in the feature request. "Uses X library", "refactors Y" are phantom scope absent a user-facing reason.


## Forward Coverage – Work Areas

`### Work Areas` is the FIS's forward-coverage anchor. Each Work Area names a component, file, or surface being changed (3-7 bullets, inventory not behavioral). Every Work Area must map to at least one implementing task or Acceptance Scenario. A Work Area with no implementing task or scenario is a **forward-coverage gap** – distinct from missing-test or missing-feature gaps.


## Self-Check

Named principles to verify before saving. Each names a failure mode; treat the named mode as the rule, not the checklist mechanics.

- **Template structure** – follows Key Generation Guidelines (Architecture Decision in 3-4 lines max, no over-specification, code snippets ≤5 lines).
- **Size signal** – if oversized per Key Generation Guidelines #7, emit the `OVERSIZE:` signal.
- **Scope-consistency** – every Work Area exercised by a scenario or Verify line. See Reverse Coverage Check + Forward Coverage – Work Areas.
- **Canonical scenario shape** – every scenario line matches the canonical shape in *Acceptance Scenarios and Proof-of-Work* above; no `### S<NN>` headers within `## Acceptance Scenarios`; negative-path checklist applied; every prescribed value appears verbatim in ≥1 Verify line.
- **Outcome-shape audit on task titles** – no titles starting with `Replace`, `Refactor`, `Update`, `Modify`, or `Add to`.
- **Anchor and Verify dry-run audit** – every cited `path#anchor` resolves against the actual source heading slug; every `rg`/`grep`/shell command in a Verify line was actually executed against the current source state and its prose claim matches the command's actual output. Catches `rg -c` exit-semantics traps (no match exits 1, does not print `0`), case-sensitivity mismatches, and stale line numbers.
- **Cross-consumer surface inventory** (for cross-cutting contract changes that rename or restructure something referenced by multiple consuming skills/references) – before writing tasks, sweep with `grep -rni` for every literal string being renamed; the resulting inventory IS the rename surface; every match maps to a task or a documented exclusion. Skip when the FIS is local to one file or surface.
- **Prose-vs-Verify scope alignment** – when an audit instruction says "rename all X" or "strip all Y", the corresponding Verify check enforces the same scope (not narrower).
- **Empty-section discipline** – each template section with a "**Leave empty** when…" prompt is *intended to stay empty* in the typical case. Resist auto-filling. Fill only when the named condition (e.g. "test approach is non-obvious", "synthesis non-obvious from Architecture Decision + Code Patterns") actually holds for this feature. Empty headings are a feature, not a gap.

### Confidence Check
Rate your FIS 1-10 for single-pass implementation success:
- **9-10**: All context present, clear decisions, validation automated
- **7-8**: Good detail, minor clarifications might be needed
- **<7**: Missing context, unclear architecture, needs revision

**If score <7**: revise or ask for user clarification. **If score <7 AND oversized**: see Key Generation Guidelines #7.
