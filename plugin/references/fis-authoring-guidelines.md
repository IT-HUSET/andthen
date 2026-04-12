# FIS Authoring Guidelines

Shared authoring guidelines for generating Feature Implementation Specifications (FIS). Referenced by `spec` (standalone) and `spec-plan` (batch sub-agents).


## FIS Authoring Principles

> The FIS is an executable specification optimized for AI agents — concise, actionable, reference-heavy.
>
> **Core Principles:**
> 1. **Intent over Implementation**: Describe outcomes, goals and context, not exact code changes — the implementing agent decides *how*
> 2. **References over Content**: Link to docs, code (file:line), and research — don't inline them
> 3. **Patterns by Reference**: Point to existing code patterns (file:line) rather than reproducing them
> 4. **Decisions, not Explanations**: State the decision, not lengthy rationale
> 5. **Information Dense**: Keywords and patterns from the codebase, minimal prose
>
> **DON'Ts:**
> - No code snippets longer than 5 lines — reference existing patterns instead
> - No inline documentation excerpts — link to the source
> - No verbose prose or explanations — be terse and actionable
> - No repeating information available elsewhere — reference it
> - No describing code changes or file creation steps — describe outcomes and goals
> - No file tree listings or "Outline of New/Changed Files" — the implementer discovers structure from the codebase


## Technical Research Separation

Technical research that supports the FIS but doesn't require intent review belongs in a **Technical Research** companion document (`technical-research.md`) stored alongside the FIS. This keeps the FIS reviewable for intent correctness while preserving implementation-enabling details for the executing agent.

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

When writing the FIS, reference the technical research rather than inlining findings. Example: `See [Technical Research](./technical-research.md#architecture-analysis) for detailed trade-off analysis`.

### Verification during execution

Technical research is a **point-in-time snapshot** — codebase patterns, API behaviors, and library versions change. The executing agent MUST treat research findings as leads to verify, not facts to trust:
- **File:line references** may be stale — verify they still exist and match the described pattern
- **API behaviors** described in research should be confirmed against the current codebase or docs
- **Library gotchas** may be version-specific — check the project's actual dependency versions
- **Architecture patterns** referenced should be confirmed they still exist in the codebase

A research finding that doesn't match reality is a signal to investigate, not to force-fit the research into the implementation.


## Scenarios and Proof-of-Work

Scenarios are the bridge between requirements and tests. Borrowed from BDD's core insight: a well-written scenario IS both the requirement and the test specification — no translation gap, no drift between "what we want" and "how we verify it."

**Writing effective scenarios:**
- Each scenario should illustrate one behavior concretely. The **Given** makes preconditions explicit (what must already be true), the **When** names the trigger (what happens), and the **Then** states observable outcomes (what must be true after).
- Use actual codebase identifiers (method names, event names, status values, domain terms) — not abstract descriptions. This is ubiquitous language in action.
- Cover the happy path first, then edge cases (boundaries, empty states, concurrent access), then at least one error/failure case. 3-7 scenarios is the sweet spot.
- If you can't write the **Then** clause, you don't understand the requirement yet — surface this as ambiguity rather than inventing an answer.

**Negative-path checklist** — after drafting scenarios, review for these three categories of missing coverage. Don't add a scenario per parameter — look for the *riskiest* gap in each category and add one scenario if the category is completely uncovered. The 3-7 scenario target still applies.

- **Omitted optional inputs**: Are there optional parameters where the null/absent case could produce a fragile default (empty string instead of null, zero instead of absent)? One scenario covering the most representative omitted-input case is sufficient.
- **No-match cases**: Are there selectors, filters, or lookups where "nothing matches" could fall through to an unintended default? A `firstWhere` with an `orElse` fallback that silently proceeds is a bug if the intent is ignore/reject.
- **Rejection paths**: Are there external integration points (webhooks, API calls) where unmatched/invalid input should be explicitly ignored or rejected? One scenario covering the reject/ignore path is sufficient.

**Proof-of-Work principle** (after Tegmark & Omohundro's asymmetry insight — verification is cheaper than generation): every claim of completion must come with verifiable evidence. An agent that *claims* "task done" is a trust problem; an agent that produces checkable artifacts is an engineering problem. Proof takes many forms — passing tests for behavioral scenarios, green Verify-line checks for task outcomes, clean stub detection for substantive implementation, visual validation for UI, build/type/lint pass for structural correctness.

**Proof is defined at spec time, executed at implementation time.** The FIS locks down what proof is required; exec-spec produces and verifies it. Every Success Criterion must have a proof path: at least one scenario (for behavioral criteria) or a task Verify line (for structural criteria). The Testing Strategy maps scenarios to execution groups so proof is produced incrementally, not deferred to the end. A criterion with no defined proof path is a spec gap, not an implementation decision.

**Traceability**: Scenarios form a chain across the workflow. Plan stories may include **Key Scenarios** — one-line behavioral seeds (happy path, edge case, error). During spec, these seeds are elaborated into full Given/When/Then scenarios. During execution, scenarios become test cases (proof-of-work). If a plan story has Key Scenarios, every seed should map to at least one FIS scenario — don't silently drop seeds.


## Key Generation Guidelines

1. **Outcomes, not code changes**: Each task describes what must be TRUE when done, not what code to write. The implementing agent determines the implementation.
2. **Task brevity**: Each task description is 1-3 lines. State the outcome, reference the pattern (file:line), include the Verify line. If a task description exceeds 3 lines, it is either too large (split it) or too detailed (describe the outcome, not the steps).
3. Each task: atomic, self-contained, with file:line references to patterns to follow. Group related tasks into Execution Groups (see Grouping Heuristics below)
4. Mark parallelizable **groups** with [P] and declare group dependencies. Tasks within a group are always sequential
5. Reference patterns, don't reproduce them
6. Each task must include a **`Verify:`** line — a concrete, observable check proving the outcome. **Verify lines must assert the described behavior, not just build success.** At least one assertion per task should fail if the outcome is not achieved:
   - Weak: `dart analyze clean` (proves compilation, not behavior)
   - Weak: `tests pass` (proves existing tests work, not that new behavior exists)
   - Strong: `Integration test: follow-up turn receives resume: true at harness boundary`
   - Strong: `Test: effectiveConcurrency(3) returns 3 when maxParallel is 5 — AND dispatch loop calls it`
   Where applicable, trace verification back to the feature's Success Criteria. Reference: `${CLAUDE_PLUGIN_ROOT}/references/verification-patterns.md` for stub-detection and wiring-check patterns.

   **Prescriptive details must be in Verify lines.** When the FIS prescribes specific outputs (column names, format strings, error messages, file locations), the Verify line MUST check the prescribed detail — not just that "output exists." The implementing sub-agent receives extracted task descriptions, not the full FIS, so prescriptive details that aren't in the Verify line are likely to be overlooked.
   - Weak: `Verify: traces list shows token breakdown` (doesn't name the columns)
   - Strong: `Verify: traces list output includes columns IN_TOKENS, OUT_TOKENS, CACHE_R, CACHE_W`
   - Weak: `Verify: pool summary displays after agent list` (doesn't specify format)
   - Strong: `Verify: pool summary matches format "Pool: N runners, N active, N available"`
   - Weak: `Verify: config class exists in config package`
   - Strong: `Verify: GitHubWebhookConfig exists at packages/dartclaw_config/lib/src/github_config.dart`

   Rule of thumb: if you prescribed a specific format, column name, file path, or string in the FIS — put it in the Verify line verbatim.
7. Stay within 100-250 line target (shorter is better)
8. Replace `<path-to-this-file>` in the self-executing callout with the actual FIS output path


## Task Grouping Heuristics

After defining individual tasks (TI01, TI02...), organize them into **Execution Groups**.
Each group is executed by a single sub-agent, reducing context boundaries between tasks.
Apply these affinity signals to determine grouping (in priority order):

1. **Tight coupling** – Task B directly extends what Task A creates (API shape,
   naming, internal structure). Always group together.
   _Example: "Create data model" + "Create repository for that model"_

2. **Same file** – Tasks that create then modify the same primary file.
   _Example: "Create ServerBuilder" + "Convert fields to final" + "Decompose handler"_

3. **Same concern across files** – Tasks applying the same conceptual change to
   different files. Always group together.
   _Example: "Remove old event firing" from 6 different call sites_

4. **Layer affinity** – Tasks at the same architectural layer that share context.
   _Example: "Create API routes" + "Add validation middleware" + "Add error handling"_

5. **Test cohesion** – All test tasks for the same implementation group together.
   _Example: All unit tests for a single class → one group_

6. **Trivial absorption** – Barrel exports, verify steps, cleanup tasks get absorbed
   into the nearest group rather than standing alone.

**Slicing Strategies:**
- **Vertical Slicing** (default): First group produces a thin end-to-end path through the stack; subsequent groups add breadth
- **Risk-First Slicing**: Tackle the highest-uncertainty piece first — fail fast before investing in dependent work. If a WebSocket connection is the architectural unknown, that's Group 1
- **Contract-First Slicing**: Define interfaces/types first (API contracts, TypeScript types, protocol buffers), then both sides implement against the contract in parallel

**Rollback-Friendly Groups** (applies to all strategies): Prefer additive changes within a group — add the new, wire it in, then remove the old in a subsequent group. When a group both deletes and replaces in one pass, a failed verification gate forces a revert that leaves the system broken (old system removed, replacement also reverted). Separating "add new" from "remove old" keeps each group independently revertable.

**Constraints:**
- Max 4 implementation tasks per group (test groups can go to 6)
- Never group across independent concerns

**Cross-Group Contracts:**
When a task in Group A creates an abstraction, parameter, or interface that a task in Group B MUST consume, state this explicitly in Group B's task description as a hard requirement. Don't rely on the implementing agent discovering it — sub-agents work in separate contexts with no shared memory. Example: if G1 creates `effectiveConcurrency()`, G3's task should say "Dispatch loop MUST use `effectiveConcurrency()` from G1 for concurrency cap."

**Dependency & Parallelism:**
- Mark groups `[P]` when they share the same dependency level and touch different files
- Declare explicit dependencies: `← [depends: G1, G2]`
- Test groups typically depend on all implementation groups


## Plan-Spec Alignment Check (when FIS originated from a plan story)

Before finalizing, cross-check each plan acceptance criterion against the FIS:
- For each acceptance criterion in the plan story, verify the FIS Success Criteria can deliver it
- If any criterion cannot be fully satisfied (due to scope exclusions, architectural constraints, or "What We're NOT Doing" items), you MUST either:
  (a) Expand the FIS scope to address the criterion, or
  (b) Add a scope note to the FIS explaining the narrowing (e.g., "replace-mode harnesses only; see Constraints") and flag it for the spec-plan cross-cutting review
- Do not finalize a FIS that silently narrows a plan requirement


## Self-Check

Quick sanity check before saving:
- [ ] FIS follows template structure
- [ ] All tasks are atomic and have file:line references where relevant
- [ ] Tasks are organized into execution groups with clear dependencies
- [ ] ADR clearly states the decision
- [ ] Scenarios cover happy path, edge cases, and at least one error case; all plan Key Scenario seeds mapped (if from a plan story)
- [ ] Negative-path checklist applied: omitted optional inputs, no-match selectors/filters, and rejection paths for external integrations all covered by scenarios
- [ ] Every Success Criterion has a proof path — at least one scenario (behavioral) or task Verify line (structural)
- [ ] **Scope-consistency**: every item listed in "In Scope" is exercised by at least one scenario (for behavioral items) or task with a Verify line (for structural items) — items with no coverage are either phantom features (remove from scope) or underspecified (add a scenario or task)
- [ ] **Output format completeness**: if `--json`, structured output, or machine-readable format is a Success Criterion, at least one scenario's **Then** clause specifies the output shape (key fields, structure) — not just "returns JSON"
- [ ] No over-specification — if a section feels padded, trim it
- [ ] No item in "What We're NOT Doing" blocks or contradicts a Success Criterion — for each exclusion, trace the data/flag path from requirement to runtime behavior; if the exclusion blocks a necessary intermediate step, either remove the exclusion or escalate
- [ ] No code snippets longer than 5 lines — describe outcomes and reference patterns instead

### Confidence Check
Rate your FIS 1-10 for single-pass implementation success:
- **9-10**: All context present, clear decisions, validation automated
- **7-8**: Good detail, minor clarifications might be needed
- **<7**: Missing context, unclear architecture, needs revision

**If score <7**: Revise or ask for user clarification.
