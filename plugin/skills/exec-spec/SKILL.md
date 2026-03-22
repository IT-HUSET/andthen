---
description: Implement code from a Feature Implementation Specification. Trigger on 'execute spec', 'implement this FIS', 'build from spec'.
argument-hint: <path-to-fis>
---

# Execute Feature Implementation Specification


Execute a fully-defined FIS document as an **orchestrator**, delegating all execution groups to sub-agents _(if supported by your coding agent)_. Each execution group is a cluster of related tasks executed by a single sub-agent, reducing context boundaries and improving coherence.

## VARIABLES
FIS_FILE_PATH: $ARGUMENTS


## INSTRUCTIONS

### Core Rules
- **Make sure `FIS_FILE_PATH` is provided** — otherwise **STOP** immediately and ask the user to provide the path to the Feature Implementation Specification.
- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails** (absolute must-follow rules)
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Complete Implementation**: 100% completion required - no partial work
- **FIS is source of truth** — follow it exactly
- **Sub-agents for all execution groups** — act as orchestrator and delegate all work to sub-agents, one per execution group _(if supported by your coding agent)_

### Orchestrator Role
**You are the orchestrator.** Your job is to:
- Load and understand the FIS, including the execution group structure
- Delegate ALL execution groups to sub-agents (one sub-agent per group)
- Track group completion and relay context between dependent groups
- Run verification gates between groups
- Ensure final validation checklist is complete

**You do NOT:**
- Write implementation code directly (delegate to sub-agents)
- Let your context get bloated with implementation details
- Skip final steps due to context exhaustion

**Context Injection:**
Before spawning each group sub-agent, extract the relevant task descriptions, key references,
and ADR decision from the FIS and pass them directly in the prompt. For dependent groups,
inject the "Context for Dependent Groups" output from prerequisite groups — this is the
primary mechanism for maintaining coherence across group boundaries. For critical handoffs
(e.g., data model group → service group), also read key output files to verify context accuracy.

### Sub-Agent Protocol

#### Group Input Template (provide to each group sub-agent)
```
## Execution Group: {GROUP_ID} — {Group Name}
Execute the following tasks sequentially. Verify each task's criteria before
proceeding to the next. If a task's verification fails, fix it before moving on.

### Task: {TASK_ID} — {Task title}
{Task description and sub-items from FIS}
**Verify**: {verification criteria}

### Task: {TASK_ID} — {Task title}
{Task description and sub-items from FIS}
**Verify**: {verification criteria}

## FIS Reference
Path: {FIS_FILE_PATH}
{ADR decision, key constraints, and relevant references — inlined by orchestrator}

## Key References (consolidated for all tasks in this group)
{File:line references relevant to ANY task in this group}

## Context from Prerequisite Groups
{Context for Dependent Groups output from completed prerequisite groups.
Omit for the first group.}

## Tests to Satisfy (if Test-Implementation Pairing exists)
{Test scenarios paired with tasks in this group from FIS Testing Strategy}
Write/verify these tests BEFORE implementing. They should fail initially (red),
then pass after your implementation (green).

## Domain Language (if UBIQUITOUS_LANGUAGE.md exists)
{Key terms relevant to this group from the project's Ubiquitous Language glossary}
Use canonical terms in code (class names, variables, functions). Avoid listed synonyms.

## UI Design Contract (if applicable)
Path: {UI_SPEC_PATH if generated in Step 1.7, otherwise omit this section}

## Requirements
1. Execute tasks sequentially within this group
2. Verify each task before proceeding to the next
3. Follow patterns in referenced files
4. Report back with the Group Result format below
```

#### Group Result Template (sub-agent must provide)
```
## Group Result: {GROUP_ID} — {Group Name}

### Per-Task Status
- {TASK_ID}: complete | partial | blocked — {brief summary of what was done}
- {TASK_ID}: complete | partial | blocked — {brief summary}

### Context for Dependent Groups
- APIs/interfaces introduced: {function signatures, class shapes — not full code}
- Naming conventions established: {patterns chosen that dependents must follow}
- Key file paths created/modified: {path — brief role description}
- Integration points exposed: {what subsequent groups can hook into}

### Issues
{blockers, errors, concerns for orchestrator}
```

#### Handling Group Results
After each group sub-agent completes:
1. **Read the result** — extract per-task status and group-level context
2. **Verify** — run verification commands for all tasks in the group
3. **Update FIS checkboxes immediately** — check off completed task checkboxes (`- [ ]` → `- [x]`) for all tasks in the group. **Do this now, not later** — this is the primary mechanism to prevent status updates from being lost to context exhaustion
4. **Relay context** — extract "Context for Dependent Groups" for use in subsequent group prompts
5. **Handle issues** — if any task is blocked/partial:
   - If fixable: spawn a targeted sub-agent for just the failing task(s)
   - If blocked: flag for user before proceeding to dependent groups


## GOTCHAS
- Agent writes code directly instead of delegating groups to sub-agents — you are the orchestrator, never implement directly. Spawn one sub-agent per execution group
- Context lost between groups — always relay the "Context for Dependent Groups" output from completed groups. For critical handoffs, read key output files to verify context accuracy
- Group too large (>4 implementation tasks) — sub-agent risks context fatigue. If the FIS has oversized groups, split them before executing
- Context exhaustion causes skipped final validation — front-load TV04 verification checks
- FIS references get stale if the spec was updated — always re-read the FIS, don't rely on cached understanding
- **Status updates get dropped when context is exhausted** — update FIS checkboxes immediately after each group completes (Step 2), not as a batch at the end. Plan and FIS status updates in Step 5 are GATES, not optional cleanup

### Helper Scripts
Helper scripts are available in `${CLAUDE_PLUGIN_ROOT}/scripts/` — use when applicable:
- `check-stubs.sh <path>` — scan for incomplete implementation indicators (TODO/FIXME, empty functions, placeholders)
- `check-wiring.sh <path>` — verify new/changed files are imported/referenced
- `verify-implementation.sh <file1> [file2...]` — combined existence + substance + wiring check


## WORKFLOW

### Step 1: Load FIS and Prepare
1. Read FIS at _`FIS_FILE_PATH`_
2. Fully Understand vital sections like Success Criteria, Scope & Boundaries, Solution Architecture and Design, Critical Documentation & Context, Implementation Plan, etc.
3. Understand the execution group structure — identify group dependencies, parallelism opportunities, and the critical path through groups
4. Analyse the codebase to properly understand the project structure, relevant files and similar patterns
  - Use command like `tree -d` and `git ls-files | head -250` to get an overview of the codebase structure
5. Read the project learnings document (e.g. _`LEARNINGS.md`_, _`implementation-notes.md`_) for traps, gotchas, error patterns, and non-obvious knowledge from previous work
6. Create task tracking for ALL execution groups (implementation + validation)

### Step 1.5: Scaffold Test Suite (if Testing Strategy present)
If the FIS contains a **Testing Strategy** section:

1. Spawn a `andthen:qa-test-engineer` sub-agent _(if supported by your coding agent)_ to:
   - Write test skeletons based on the FIS Testing Strategy (test scenarios, edge cases, error cases)
   - If a **Test-Implementation Pairing** table exists, organize tests by their paired execution group
   - Follow test patterns referenced in the Testing Strategy section
   - Tests should assert expected behavior — they will naturally fail since implementation doesn't exist yet
2. Run the test suite to confirm tests are discovered and fail as expected (validates test infrastructure)
3. These tests become **acceptance gates** — implementation tasks in Step 2 must make them pass

> **Skip this step** when: the FIS has no Testing Strategy section, the feature is purely structural (scaffolding, config, migrations) where tests-first adds no value, or test infrastructure (runner, framework) is not yet set up and will be configured by an implementation task — in that case, defer test scaffolding until after that task completes.

### Step 1.7: UI Design Contract (if frontend work detected)

If the FIS contains UI/UX work (check for UI wireframes, frontend components,
CSS/styling tasks, or a "UI/UX Design" section):

1. Generate a **UI-SPEC.md** design contract covering:
   - Spacing system (margins, padding, gaps)
   - Typography (font families, sizes, weights, line heights)
   - Color palette (primary, secondary, accent, semantic colors)
   - Component patterns (buttons, forms, cards, modals)
   - Responsive breakpoints
   - Copywriting tone and conventions

2. Source decisions from (in priority order):
   - FIS UI/UX Design section
   - Project design system (per Document Index)
   - UX-UI-GUIDELINES.md
   - Reasonable defaults consistent with the existing codebase

3. Store as `.agent_temp/ui-spec-{feature-name}.md`

4. All subsequent implementation sub-agents receive this contract
   as additional context for UI consistency.

**Skip this step** when: FIS has no UI work, project has a comprehensive
design system already referenced, or the FIS explicitly states
"no UI design contract needed".

### Step 2: Execute Implementation Groups
For each execution group, following the dependency order declared in the FIS:

**Sequential groups:**
- Spawn a **foreground sub-agent** _(if supported by your coding agent)_ with Group Input Template
- Wait for Group Result
- Run verification gate (verify all tasks in the group)
- Extract "Context for Dependent Groups" for the next group's prompt
- Update FIS checkboxes, track cumulative context

**Parallel groups [P]:**
- Spawn **multiple foreground sub-agents in a single message** _(if supported by your coding agent; otherwise execute sequentially)_ — one per parallel group
- All parallel groups execute concurrently
- Groups don't have file conflicts (the spec skill ensures this via grouping heuristics)
- Collect all Group Results
- Merge "Context for Dependent Groups" from all parallel groups for downstream use

**Verification gate (between groups):**
After each group completes, before spawning dependent groups:
1. Run the `Verify` line for each task in the completed group
2. If any verification fails, spawn a targeted fix sub-agent before proceeding
3. This catches cascading failures early — before they propagate to dependent groups

**Test-first rhythm** (when FIS has Test-Implementation Pairing):
- Before delegating each group, include the paired test scenarios in the sub-agent prompt
- Sub-agent should first verify the paired tests exist and fail (red)
- Then implement until paired tests pass (green)
- The remediation loop (TV04) handles refactoring

**Sub-agent selection (per group):**
- Default: `general-purpose` agent
- Groups with build/tooling tasks: `andthen:build-troubleshooter`
- Groups with UI tasks: `andthen:ui-ux-designer`
- Groups with architecture tasks: `andthen:solution-architect`

**Agent mode:**
- Use **foreground** sub-agents by default (orchestrator needs results before proceeding to dependent groups)
- For parallel groups: spawn as multiple foreground Agent calls in a single message
- Background agents only for Step 1.5 (test scaffolding) and Step 1.7 (UI spec) when the orchestrator has independent prep work to do simultaneously

### Step 3: Execute Validation Tasks
**CRITICAL**: Execute all validation tasks (TV01-TV03) as a validation group in **parallel sub-agents** _(if supported by your coding agent; otherwise execute sequentially)_, never directly from the main agent.
Important: Correct implementation of requirements and acceptance criteria must be verified through tests and visual validation (when applicable).

#### TV01 [P] — Level 1: Code Review
The sub-agent for code review (general-purpose) should use the `andthen:review-code` skill for comprehensive review and analysis covering:

- Static analysis, linting, formatting and type checking issues
- Code quality (correctness, readability, best practices, performance, maintainability)
- Architecture (pattern adherence, ADR compliance, anti-pattern detection)
- Security (input validation, injection prevention, auth, data protection, OWASP Top 10)
- UI/UX (if applicable - visual quality, usability, accessibility)
- **Domain language**: Apply `DOMAIN-LANGUAGE-REVIEW-CHECKLIST.md` — verify code uses canonical terms from `UBIQUITOUS_LANGUAGE.md`
- **Stub detection**: Scan implemented files for TODO/placeholder/stub patterns per `${CLAUDE_PLUGIN_ROOT}/references/verification-patterns.md`
- **Wiring verification**: Confirm new components/routes/endpoints are actually connected to the system (imported, routed, called)

#### TV02 [P] — Level 2: Testing
Use the `andthen:qa-test-engineer` sub-agent _(if supported by your coding agent)_ to execute tests for new and existing functionality:
- Unit tests
- Integration tests (if applicable)
- E2E tests (if applicable)

#### TV03 [P] — Level 3: Visual Validation (if UI)
- Verify updated UI works correctly according to specified requirements
- Use the `andthen:visual-validation-specialist` sub-agent _(if supported by your coding agent)_ for full visual validation
- This agent automatically follows any **Visual Validation Workflow** defined in CLAUDE.md
- Checks for visual regressions and ensures UI matches design specs

#### TV04 — Remediation Loop
Structured fix-and-revalidate cycle with bounded iterations:

1. **Collect** all validation feedback from TV01-TV03 sub-agents
2. **Triage** issues by severity — CRITICAL and HIGH issues must be fixed; MEDIUM issues should be fixed; LOW issues are optional. When mapping from review-code findings: CRITICAL→CRITICAL, HIGH→HIGH, SUGGESTIONS→MEDIUM
3. **Fix** — spawn sub-agents _(if supported by your coding agent)_ to address issues, grouped by affected area to avoid conflicts
4. **Re-validate** — re-run only the affected validation levels (e.g., if only code issues were found, re-run TV01; if tests failed, re-run TV02)
5. **Loop** — repeat steps 2-4 until: all CRITICAL/HIGH issues are resolved and validation passes clean

**Loop bound**: Maximum **3 remediation cycles**. If issues persist after 3 cycles, escalate to the user with a summary of remaining issues and what was attempted.

### Step 4: Final Quality Assurance
As orchestrator (not delegated to sub-agent):
- Review all group results
- Check for functionality gaps or requirement mismatches
- Use `code-simplifier:code-simplifier` agent _(if supported by your coding agent)_ to look for simplification, maintainability, and general quality of life improvement opportunities

### Step 5: Verify Completion and Update Status
**Orchestrator performs directly — all substeps are REQUIRED, not optional cleanup:**

#### 5a. Verify Implementation
1. Verify ALL success criteria in FIS are met
2. Verify ALL task checkboxes marked complete (`- [x]`) — if any were missed during Step 2, mark them now
3. Verify Final Validation Checklist items are satisfied
4. **Substantive check**: Run `rg "TODO|FIXME|placeholder|not.implemented" <changed-files>` — must return clean (no matches in new implementation files)
5. **Wiring check**: For each new file/component created, verify it is imported or referenced by at least one other file in the system
6. Include verification evidence in completion summary (as applicable):
   - **Build**: exit code or success/failure status
   - **Tests**: pass/fail counts (e.g., "42/42 pass")
   - **Linting/types**: error and warning counts
   - **Visual validation**: screenshot confirming UI matches expectations (if UI)
   - **Runtime**: confirmation app starts and key flows work

#### 5b. Update FIS Status (REQUIRED GATE)
Update the FIS document itself:
- Mark all completed task checkboxes (`- [ ]` → `- [x]`)
- Mark all completed success criteria checkboxes
- Mark all Final Validation Checklist items as checked

#### 5c. Update Source Plan (REQUIRED GATE — if FIS originated from a plan)
If this FIS originated from a plan (`plan.md`), use the `andthen:ops` skill to update the plan:
- Set the story's **Status** field to `Done`
- Set the story's **FIS** field to the FIS file path (if not already set by `andthen:spec`)
- Check off completed acceptance criteria checkboxes (`- [ ]` → `- [x]`)
- Update the Story Catalog table status column to `Done`
- Note any scope changes or deviations

After ops completes, **re-read the plan and FIS files** to verify updates were applied (`ops` runs in fork context and modifications may not be visible in your current state).

**Gate**: FIS checkboxes, success criteria, and plan status are ALL updated before proceeding

### Step 6: Iteration (if needed)
If success criteria not met or if previous step failed to successfully verify completion:
1. Analyze gaps from validation feedback
2. Create targeted fix groups for remaining issues
3. Execute Steps 2-5 again


## Post-Completion: Update Project Learnings
After completion, if the project has a learnings file (`LEARNINGS.md` or `implementation-notes.md`), update it with knowledge discovered during this story. Organize by topic, not chronologically. Types of knowledge to capture:
- **Traps & gotchas**: Non-obvious patterns that would bite a competent developer even with access to code and git history
- **Domain knowledge**: API quirks, framework behavior, naming decisions, business rules discovered in code
- **Procedural knowledge**: Deploy steps, test prerequisites, tooling patterns
- **Error patterns**: Recurring errors — note if deterministic (bad schema, wrong type → conclude immediately) or infrastructure (timeout, rate limit → log, conclude only when pattern emerges)

Keep entries brief (1-2 sentences each). Do NOT record:
- What was implemented (that's in git history)
- How parts integrate (that's in the code)
- Routine decisions (that's in the FIS/spec)
- Language basics or framework docs

**Self-maintenance**: When updating, also review nearby entries — merge overlapping items, remove knowledge that's no longer accurate, split sections that grow too long.

> **Note**: FIS checkbox/status updates and source plan updates are handled in Step 5 (Verify Completion and Update Status) — they are required gates, not post-completion tasks.
