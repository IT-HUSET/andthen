---
description: Implement code from a Feature Implementation Specification. Trigger on 'execute spec', 'implement this FIS', 'build from spec'.
argument-hint: <path-to-fis | --issue <number> | issue URL>
---

# Execute Feature Implementation Specification

Execute a fully-defined FIS document as an **orchestrator**, delegating all execution groups to sub-agents _(if supported by your coding agent)_. Each execution group is a cluster of related tasks executed by a single sub-agent.

## VARIABLES
FIS_SOURCE: $ARGUMENTS


## INSTRUCTIONS

### Core Rules
- **Make sure `FIS_SOURCE` is provided** – otherwise **STOP** immediately and ask for it.
- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** in CLAUDE.md / AGENTS.md before starting.
- **Complete Implementation**: 100% completion required - no partial work
- **FIS is source of truth** – follow it exactly
- **Sub-agents for all execution groups** – act as orchestrator, delegate all work to sub-agents, one per group _(if supported)_

### Orchestrator Role
**You are the orchestrator.** Your job:
- Load and understand the FIS, including execution group structure
- Delegate ALL execution groups to sub-agents (one per group)
- Track group completion and relay context between dependent groups
- Run verification gates between groups
- Ensure final validation checklist is complete

**You do NOT:** write implementation code directly, let context bloat with details, or skip final steps.

**Context Injection:** Before spawning each group sub-agent, extract the relevant task descriptions, key references, and ADR decisions from the FIS and pass them directly in the prompt. For dependent groups, inject the "Context for Dependent Groups" output from prerequisite groups. For critical handoffs, read key output files to verify context accuracy.

**Prescriptive Detail Injection:** When extracting task descriptions for sub-agent prompts, identify and include **prescriptive details** verbatim: specified column names/orders, output format strings, exact error messages, file paths where artifacts must be placed, data field names, and UI element requirements (buttons, controls, labels). These are the details most likely to drift during implementation — include them as explicit requirements in the sub-agent prompt, not just as part of general task context.

### Sub-Agent Protocol

#### Group Input Template
```
## Execution Group: {GROUP_ID} – {Group Name}
Execute the following tasks sequentially. Verify each task's criteria before proceeding.

### Task: {TASK_ID} – {Task title}
{Task description and sub-items from FIS}
**Verify**: {verification criteria}

## FIS Reference
Path: {FIS_FILE_PATH}
{ADR decision, key constraints, and relevant references – inlined by orchestrator}

## Key References (consolidated for all tasks in this group)
{File:line references relevant to ANY task in this group}

## Context from Prerequisite Groups
{Context for Dependent Groups output from completed prerequisite groups. Omit for the first group.}

## Scenarios to Satisfy
{Scenarios paired with tasks in this group from FIS Scenarios + Testing Strategy}
Write/verify tests for these scenarios BEFORE implementing – they should fail initially (red), then pass after (green). These tests are proof-of-work for the behavioral claims; task Verify lines provide proof for other dimensions.

## Domain Language (if UBIQUITOUS_LANGUAGE.md exists)
{Key terms relevant to this group}
Use canonical terms in code (class names, variables, functions). Avoid listed synonyms.

## UI Design Contract (if applicable)
Path: {UI_SPEC_PATH if generated in Step 1.7, otherwise omit}

## Structured Output Protocols
Use CONFUSION, NOTICED BUT NOT TOUCHING, and MISSING REQUIREMENT formats per `${CLAUDE_PLUGIN_ROOT}/references/structured-output-protocols.md`.

## Requirements
1. Execute tasks sequentially within this group
2. Verify each task before proceeding
3. Follow patterns in referenced files
4. Report back with the Group Result format below
```

#### Group Result Template
```
## Group Result: {GROUP_ID} – {Group Name}

### Per-Task Status
- {TASK_ID}: complete | partial | blocked – {brief summary}

### Context for Dependent Groups
- APIs/interfaces introduced: {function signatures, class shapes}
- Naming conventions established: {patterns chosen}
- Key file paths created/modified: {path – brief role}
- Integration points exposed: {what subsequent groups hook into}

### Issues
{blockers, errors, concerns for orchestrator}
```

#### Handling Group Results
After each group sub-agent completes:
1. **Read the result** – extract per-task status and group-level context
2. **Verify** – run verification commands for all tasks in the group
3. **Update FIS checkboxes immediately** – `- [ ]` → `- [x]` for all completed tasks. **Do this now** – this is a gate, not cleanup
4. **Relay context** – extract "Context for Dependent Groups" for subsequent group prompts
5. **Handle issues** – if blocked/partial: spawn a targeted fix sub-agent; if truly blocked, flag for user


## GOTCHAS
- Writing code directly instead of delegating – you are the orchestrator, always spawn sub-agents per group
- Context lost between groups – always relay "Context for Dependent Groups" output; read key output files for critical handoffs
- Group too large (>4 tasks) – split before executing to avoid sub-agent context fatigue
- **Status updates dropped when context exhausted** – update FIS checkboxes immediately after each group (Step 2), not as a batch. Plan and FIS updates in Step 4 are GATES
- FIS references get stale if spec was updated – always re-read the FIS
- Not signaling active-story status to STATE.md when called in a plan context – set "In Progress" at start

### Helper Scripts
Available in `${CLAUDE_PLUGIN_ROOT}/scripts/`:
- `check-stubs.sh <path>` – scan for incomplete implementation indicators
- `check-wiring.sh <path>` – verify new/changed files are imported/referenced
- `verify-implementation.sh <file1> [file2...]` – combined existence + substance + wiring check


## WORKFLOW

### Step 1: Resolve FIS Source and Prepare
1. Resolve `FIS_SOURCE` to a local `FIS_FILE_PATH`:
   - Local file path: use it directly
   - `--issue <number>` or GitHub issue URL: fetch the issue body and inspect the typed envelope per `${CLAUDE_PLUGIN_ROOT}/references/github-artifact-roundtrip.md`. Require `artifact_type: fis-bundle`; extract all embedded files preserving their repo-relative paths; set `FIS_FILE_PATH` from `canonical_local_primary`
   - If `canonical_local_primary` is missing, ambiguous, or does not match an extracted file, **STOP**
   - Recover metadata from the envelope:
     - `FIS_CANONICAL_PATH` = `fis_path` when present, otherwise `canonical_local_primary`
     - `PLAN_FILE_PATH` = `plan_path` when present; if it refers to an embedded companion file, use the extracted copy
     - `STORY_IDS` = `story_ids`
   - If the envelope says the FIS originated from a plan (`plan_path` present) but omits `story_ids`, **STOP** — plan-backed FIS execution needs that context for plan/state updates
   - If matching canonical local file paths already exist in the workspace, switch `FIS_FILE_PATH` / `PLAN_FILE_PATH` to those real files and treat the extracted directory as a read-only mirror
   - If `plan_path` is present but no embedded or local `PLAN_FILE_PATH` can actually be resolved, **STOP** — plan-backed FIS execution cannot update source plan state without the plan file
   - Otherwise set `FIS_SOURCE_MODE = github-artifact`
   - If the GitHub artifact is typed but incompatible (`plan-bundle`, `triage-plan`, `triage-completion`, or any `*-review` report), **STOP** and direct the user to the matching workflow skill
   - If the GitHub issue is untyped, **STOP** — `exec-spec` requires a local FIS path or a typed GitHub FIS artifact
2. Read FIS at _`FIS_FILE_PATH`_
3. Understand vital sections: Success Criteria, Scope, Architecture, Implementation Plan
4. **Read Technical Research** – if the FIS references a `technical-research.md` (companion document with codebase analysis, API research, architecture trade-offs), read it for implementation context. **Treat findings as leads to verify, not facts to trust** — file:line references, API behaviors, and library details may be stale. Confirm key references against the current codebase before relying on them. Include relevant verified findings when injecting context into sub-agent prompts.
5. Understand execution group structure – identify dependencies, parallelism, critical path
6. Analyze codebase: `tree -d` and `git ls-files | head -250` for overview
7. Read project learnings document (e.g. _`LEARNINGS.md`_, _`implementation-notes.md`_) for traps and non-obvious patterns
8. Create task tracking for ALL execution groups (implementation + validation)
9. **Update project state** (if STATE.md exists and the FIS originated from a plan): restore story context from `STORY_IDS`. For a single-story FIS, use that story directly. For a composite/shared FIS, mark the active work as the composite/story set rather than inventing a single story ID.

### Step 1.5: Scaffold Scenario Tests
If the FIS has a **Scenarios** and/or **Testing Strategy** section, spawn the `andthen:qa-test-engineer` agent _(if supported)_ to write test skeletons derived from the scenarios, organized by paired execution group. Run the suite to confirm tests fail (red) — they become acceptance gates for Step 2. These are proof-of-work for the behavioral scenarios — they verify *intent* (what should be true) rather than incidentally confirming what the implementation happens to produce. Verify lines and verification gates cover other proof dimensions (existence, wiring, structural correctness).

> **Skip when**:
> - No test runner exists in the project, OR
> - The FIS has no Scenarios/Testing Strategy section AND all tasks are configuration-only (no branching logic)
>
> When in doubt, scaffold — a test that can be written is a test worth having (Beyonce Rule).

### Step 1.7: UI Design Contract (if frontend work detected)
If the FIS contains UI/UX work, generate a **UI-SPEC.md** covering spacing, typography, color palette, component patterns, and responsive breakpoints. Source from FIS → project design system → UX-UI-GUIDELINES.md → reasonable defaults. Store as `.agent_temp/ui-spec-{feature-name}.md`. All subsequent sub-agents receive this contract.

**Skip when**: no UI work, comprehensive design system already referenced, or FIS states "no UI design contract needed".

### Step 2: Execute Implementation Groups
For each execution group (following dependency order in FIS):

**Sequential groups:** spawn foreground sub-agent → wait for Group Result → run verification gate → extract context → update FIS checkboxes.

**Parallel groups [P]:** spawn multiple foreground sub-agents in a single message → collect all Group Results → merge "Context for Dependent Groups".

**Verification gate (between groups):** run `Verify` for each task in the completed group; if any fail, spawn a targeted fix sub-agent before proceeding. For behavioral failures (wrong output, broken interaction, regression), apply the Prove-It Pattern: the fix sub-agent writes a failing test that demonstrates the bug before fixing it — the test proves the bug existed and prevents reintroduction in later groups. Never proceed to a dependent group with unresolved failures — a bug in Group 1 that propagates through Groups 2-5 costs far more than catching it here.

**Proof-of-Work rhythm** (when FIS has Scenarios): include paired scenario tests in sub-agent prompt; sub-agent verifies tests fail (red), implements until they pass (green). Combined with Verify-line checks at the verification gate, these provide layered proof of correct implementation. TV05 handles refactoring.

**Sub-agent selection:** default `general-purpose`; build/tooling → `andthen:build-troubleshooter` agent; UI → `andthen:ui-ux-designer` agent; architecture → `andthen:solution-architect` agent. Use **foreground** agents by default; background only for Steps 1.5 and 1.7 when independent prep work runs simultaneously.

### Step 3: Execute Validation Tasks
Step 2 gates catch task-level failures within groups. Step 3 catches cross-cutting issues — integration, security, architectural coherence — that pass individual group checks.

**CRITICAL**: Run all validation tasks as parallel sub-agents _(if supported; otherwise sequentially)_ – never directly from main agent.

#### TV01 [P] – Code Review
Sub-agent invokes the `andthen:review-code` skill covering: static analysis, linting, formatting, type checking, code quality, architecture, security, domain language, stub detection, and wiring verification.

#### TV02 [P] – Testing
`andthen:qa-test-engineer` sub-agent runs unit, integration, and E2E tests (as applicable).

#### TV03 [P] – Visual Validation (if UI)
`andthen:visual-validation-specialist` sub-agent _(if supported)_ for full visual validation per any Visual Validation Workflow defined in CLAUDE.md.

#### TV04 – Quality Review (orchestrator, not delegated)
- Review all group results for functionality gaps or requirement mismatches
- Review implemented code for simplification opportunities – unnecessary complexity, duplication, or over-abstraction introduced during implementation. Use the `andthen:refactor` skill for this.

#### TV05 – Remediation Loop
1. **Collect** all validation feedback from TV01-TV04
2. **Triage** by severity – CRITICAL/HIGH must fix; MEDIUM should fix; LOW optional. (review-code mapping: CRITICAL→CRITICAL, HIGH→HIGH, SUGGESTIONS→MEDIUM)
3. **Fix** – spawn sub-agents grouped by affected area to avoid conflicts
4. **Re-validate** – re-run only affected validation levels
5. **Loop** – repeat until all CRITICAL/HIGH resolved

**Loop bound**: Maximum **3 remediation cycles**. If issues persist, escalate to user with summary.

### Step 4: Verify Completion and Update Status
**Orchestrator performs directly – all substeps REQUIRED:**

#### 4a. Verify Implementation
1. Verify ALL success criteria in FIS are met
2. Verify ALL task checkboxes marked complete; mark any missed now
3. Verify Final Validation Checklist items satisfied
4. **Substantive check**: `rg "TODO|FIXME|placeholder|not.implemented" <changed-files>` – must be clean
5. **Wiring check**: each new file/component is imported or referenced by at least one other file
6. Include verification evidence per `${CLAUDE_PLUGIN_ROOT}/references/verification-evidence.md`: **Build**, **Tests**, **Linting/types**; add **Visual validation** and **Runtime** for UI/runtime stories
7. **Spec compliance spot-check**: Extract prescriptive details from the FIS (output format strings, column name lists, file paths for new artifacts, exact error messages, UI elements like buttons/controls) and grep/verify each against the implementation. This catches the most common exec-spec failure mode: implementation that works correctly but doesn't match the spec's prescribed format, structure, or location. Check: column names/order appear in source; prescribed file paths exist at specified locations; key substrings of format strings present in output code; prescribed UI elements exist in templates. Fix any mismatches before proceeding to 4b.

#### 4b. Update FIS Status (REQUIRED GATE)
Mark completed task, success-criteria, and Final Validation Checklist checkboxes in the FIS document.

#### 4c. Update Source Plan (REQUIRED GATE – if FIS from a plan)
Use restored `PLAN_FILE_PATH` + `STORY_IDS`. Invoke the `andthen:ops` skill to update the source plan: set each covered story Status to `Done`, set the FIS field path, check off acceptance criteria, and update the Story Catalog table. For composite/shared FIS, update **all** constituent stories listed in `STORY_IDS`. Note any scope changes or deviations. After ops completes, **re-read plan and FIS files** to verify updates applied (`ops` runs in fork context and modifications may not be visible in your current state).

#### 4d. Update Project State (if STATE.md exists)
Follow `${CLAUDE_PLUGIN_ROOT}/references/post-completion-guide.md` (`Story Runs` → `STATE.md`).

**Gate**: FIS checkboxes, success criteria, and plan status ALL updated before proceeding

### Step 5: Iteration (if needed)
If success criteria unmet: analyze gaps, create targeted fix groups, execute Steps 2-4 again.

### Step 6: Canonical Continuation Sync _(if `FIS_SOURCE_MODE = github-artifact`)_
The extracted `.agent_temp/github-artifacts/...` directory is only a working mirror. Before finishing:
- If the canonical local FIS / plan paths exist in the workspace, verify all final updates landed there
- Otherwise update the source GitHub issue to the latest typed `fis-bundle`, including:
  - Updated FIS contents
  - Updated `technical-research.md` when present
  - Updated `plan.md` when this was a plan-backed FIS
  - `fis_path`, `plan_path`, and `story_ids` metadata reflecting the final state

Do not finish with the temp mirror as the only updated copy.

## Post-Completion
Follow `${CLAUDE_PLUGIN_ROOT}/references/post-completion-guide.md` (`Story Runs` → `Learnings`) for learnings-file updates. Do not create a new learnings file from exec-spec.

> FIS checkbox/status updates and plan updates are handled in Step 4 – they are REQUIRED GATES, not post-completion tasks.
