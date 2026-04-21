# FIS Authoring Guidelines

Shared authoring guidelines for generating Feature Implementation Specifications (FIS). Referenced by `spec` (standalone) and `plan` (batch FIS generation).


## FIS Authoring Principles

> FIS is an executable spec: intent over implementation, references over content, decisions not explanations.
> No code snippets >5 lines, no inline docs, no verbose prose, no file trees — reference existing patterns and describe outcomes.


## Technical Research Separation

Technical research that supports the FIS but doesn't require intent review belongs in a **Technical Research** companion document (`.technical-research.md`) stored alongside the FIS. This keeps the FIS reviewable for intent correctness while preserving implementation-enabling details for the executing agent.

### What stays in the FIS (needs human intent review)
- Success criteria, scenarios, scope decisions
- Architecture decision (compact: chosen approach + rationale)
- UI/UX flows and user-facing interactions
- High-level data shapes and integration points (what connects, not protocol details)
- Constraints that affect scope or feasibility

### What goes in Technical Research (enables execution, doesn't need intent review)
- Codebase analysis: patterns found, conventions, file:line inventories, similar implementations
- API documentation excerpts, library research, version-specific gotchas
- Detailed architecture trade-off analysis (full alternatives comparison, PoC results)
- Field-level data model details, schema specifics, migration considerations
- Integration implementation details (auth flows, webhook formats, SDK usage patterns)
- Detailed workarounds for known limitations

**Guiding principle**: If a reviewer needs to validate *"are we building the right thing?"* → FIS. If the detail helps the executing agent *"build the thing right"* → Technical Research.

When writing the FIS, reference the technical research rather than inlining findings. Example: `See [Technical Research](./.technical-research.md#architecture-analysis) for detailed trade-off analysis`.


## Scenarios and Proof-of-Work

Each scenario: one behavior, concrete Given/When/Then using actual codebase identifiers. Cover happy path first, then edge cases, then at least one error case. 3-7 scenarios is the sweet spot. If you can't write the **Then** clause, surface it as ambiguity.

**Negative-path checklist** — after drafting scenarios, review for these three categories. Add one scenario per uncovered category (the riskiest gap), not one per parameter. The 3-7 target still applies.

- **Omitted optional inputs**: null/absent case producing a fragile default (empty string instead of null, zero instead of absent)?
- **No-match cases**: selectors, filters, or lookups where "nothing matches" falls through to an unintended default?
- **Rejection paths**: external integration points where unmatched/invalid input should be explicitly ignored or rejected?

**Proof-of-Work**: Every Success Criterion must have a proof path — at least one scenario (behavioral) or task Verify line (structural). The FIS locks down what proof is required; exec-spec produces and verifies it. Testing Strategy maps scenarios to task IDs so proof is produced incrementally, not deferred.

**Traceability**: Plan stories may include **Key Scenarios** (one-line behavioral seeds). During spec, seeds are elaborated into full scenarios. Every plan Key Scenario seed must map to at least one FIS scenario — don't silently drop seeds.

## Execution Contract

Include the template's **Execution Contract** section near the bottom of the Implementation Plan. Extend it only if the feature truly needs feature-specific execution constraints; for lightweight specs, phrase the validation bullet around the checks that actually exist.


## Key Generation Guidelines

1. **Outcomes, not code changes**: Each task describes what must be TRUE when done, not what code to write. The executing agent determines the implementation.
2. **Task brevity**: Each task description is 1-3 lines. State the outcome, reference the pattern (file:line), include the Verify line. If a task description exceeds 3 lines, it is either too large (split it) or too detailed (describe the outcome, not the steps).
3. Each task: atomic, self-contained, with file:line references to patterns to follow. Order tasks so later tasks can build on earlier ones without hidden dependencies (see Task Ordering below)
4. Reference patterns, don't reproduce them
5. Each task must include a **`Verify:`** line — a concrete, observable check proving the outcome. **Verify lines must assert the described behavior, not just build success.** At least one assertion per task should fail if the outcome is not achieved. Trace verification back to the feature's Success Criteria where applicable.

   **Prescriptive details must be in Verify lines.** When the FIS prescribes specific outputs (column names, format strings, error messages, file locations), the Verify line MUST check the prescribed detail verbatim — not just that "output exists." A proof check that doesn't name the prescribed detail lets the implementation satisfy the task in spirit while missing the exact contract.

   - Weak: `Verify: traces list shows token breakdown` (doesn't name the columns)
   - Strong: `Verify: traces list output includes columns IN_TOKENS, OUT_TOKENS, CACHE_R, CACHE_W`

   Rule of thumb: if you prescribed a specific format, column name, file path, or string in the FIS — put it in the Verify line verbatim.
6. Most good FIS files land in the 150-450 line range. Once a draft starts pushing past roughly ~600 lines or more than ~18 tasks, that is a strong signal that this is no longer one execution-sized spec. For standalone feature requests, prefer a spec-time decomposition pivot into a small plan bundle plus child FIS files. For `story {story_id} of plan.md` inputs, do **not** fan one plan story out into multiple child specs — decompose the plan upstream instead.
7. Replace `<path-to-this-file>` in the self-executing callout with the actual FIS output path
8. Make **What We're NOT Doing** explicit: 3-5 specific exclusions or deferrals with reasons. Use it to preserve scope boundaries across sessions, not as filler.
9. Include the **Execution Contract** section from the template. Keep it consistent unless the feature truly needs extra execution-specific constraints.


## Task Ordering

After defining individual tasks (TI01, TI02...), order them so the implementation can proceed sequentially without hidden orchestration metadata. The task list itself should make the dependency path obvious.

Put foundational tasks first, then widening tasks, then polish/integration tasks. Keep related tasks adjacent when they share context, but don't introduce separate grouping syntax unless the document genuinely needs it for reader clarity.

When a later task must consume something from an earlier task (an API, a type, a component), state this explicitly in the later task's description. Don't rely on the executing agent discovering it from context. Example: if TI01 creates `effectiveConcurrency()`, TI03 should say "Dispatch loop MUST use `effectiveConcurrency()` from TI01 for concurrency cap."


## Plan-Spec Alignment Check (when FIS originated from a plan story)

Before finalizing, cross-check each plan acceptance criterion against the FIS:
- For each acceptance criterion in the plan story, verify the FIS Success Criteria can deliver it
- If any criterion cannot be fully satisfied (due to scope exclusions, architectural constraints, or "What We're NOT Doing" items), you MUST either:
  (a) Expand the FIS scope to address the criterion, or
  (b) Add a scope note to the FIS explaining the narrowing (e.g., "replace-mode harnesses only; see Constraints") and flag it for the `andthen:plan` cross-cutting review
- Do not finalize a FIS that silently narrows a plan requirement


## Reverse Coverage Check (phantom-scope guard) — applies to all FIS

Forward coverage (above) catches plan criteria the FIS misses. Reverse coverage catches the opposite: FIS work no upstream asked for.

> Distinct from Self-Check's **Scope-consistency** (internal: In Scope → coverage within the FIS). Reverse Coverage is external: Success Criterion → upstream source.

For each FIS Success Criterion, name the plan acceptance criterion, PRD outcome, or (standalone) feature-request element it serves. Any unnamed criterion is **phantom scope**.

**Resolution depends on mode:**

- **Batch sub-agent mode** (from the `andthen:plan` skill) — binary: either (a) remove the criterion, or (b) return a `PHANTOM_SCOPE` entry in your completion summary so the orchestrator can escalate at the cross-cutting review. Do not rationalize by adding scope notes. Do not edit `plan.md` or `prd.md`. Note: sub-agents only see plan-level sources, so a criterion legitimately sourced from the PRD may appear phantom — report it anyway and let the orchestrator filter against `prd.md`.
- **Standalone mode**: (a) remove, or (b) raise with the user and — on approval — add a scope note documenting the proposed addition for plan/PRD amendment.
- **Standalone with no plan or PRD at all**: accept the criterion only if it traces to a user- or business-observable outcome in the feature request. "Uses X library", "refactors Y" are phantom scope absent a user-facing reason.

Do not finalize a FIS with Success Criteria the upstream contract doesn't justify.


## Self-Check

Quick sanity check before saving:
- [ ] **Template structure**: FIS follows the template; ADR states the decision; no over-specification or code snippets >5 lines
- [ ] **Size check**: 150-450 lines is the sweet spot; >600 lines or >18 tasks means split upstream (spec-time pivot for standalone requests only)
- [ ] **Scope-consistency**: every "In Scope" item is exercised by a scenario or Verify line; `What We're NOT Doing` is specific and never contradicts a Success Criterion
- [ ] **Coverage**: every Success Criterion has a proof path (scenario or Verify line); scenarios cover happy path, edge cases, one error case; negative-path checklist applied; plan Key Scenario seeds all mapped (if plan-derived); output shapes specified when structured output is a Success Criterion

### Confidence Check
Rate your FIS 1-10 for single-pass implementation success:
- **9-10**: All context present, clear decisions, validation automated
- **7-8**: Good detail, minor clarifications might be needed
- **<7**: Missing context, unclear architecture, needs revision

**If score <7**: Revise or ask for user clarification.

**If score <7 AND FIS exceeds size thresholds**: the feature is likely too large for a single spec. Recommend the `andthen:plan` skill for story decomposition before proceeding.
