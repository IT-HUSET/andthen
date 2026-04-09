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

**Constraints:**
- Max 4 implementation tasks per group (test groups can go to 6)
- Never group across independent concerns
- First group should produce a thin working end-to-end path (vertical slice principle)

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
- [ ] No over-specification — if a section feels padded, trim it
- [ ] No item in "What We're NOT Doing" blocks or contradicts a Success Criterion — for each exclusion, trace the data/flag path from requirement to runtime behavior; if the exclusion blocks a necessary intermediate step, either remove the exclusion or escalate
- [ ] No code snippets longer than 5 lines — describe outcomes and reference patterns instead

### Confidence Check
Rate your FIS 1-10 for single-pass implementation success:
- **9-10**: All context present, clear decisions, validation automated
- **7-8**: Good detail, minor clarifications might be needed
- **<7**: Missing context, unclear architecture, needs revision

**If score <7**: Revise or ask for user clarification.
