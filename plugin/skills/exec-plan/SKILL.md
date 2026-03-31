---
description: Execute an entire implementation plan through a pipeline (spec-plan per phase, then exec-spec with configurable review mode)
argument-hint: <path-to-plan-directory> [--review-mode per-story|none|full-plan]
---

# Execute Plan


Execute ALL stories in an implementation plan (from `andthen:plan`) through a pipeline: **spec-plan (per phase) → exec-spec**, with configurable review behavior.

Pre-generates all specs for each phase via `andthen:spec-plan` (parallel sub-agents + cross-cutting review), then executes story implementation using **parallel sub-agents** _(if supported by your coding agent)_, otherwise sequentially.


## VARIABLES
PLAN_DIR: positional argument from `$ARGUMENTS`
REVIEW_MODE: parse from `--review-mode` flag (`per-story`, `none`, or `full-plan`; default `per-story`)


## USAGE

```
/exec-plan PLAN_DIR="path/to/plan"
/exec-plan PLAN_DIR="path/to/plan" --review-mode per-story
/exec-plan PLAN_DIR="path/to/plan" --review-mode none
/exec-plan PLAN_DIR="path/to/plan" --review-mode full-plan
```


## INSTRUCTIONS

Make sure `PLAN_DIR` is provided – otherwise **STOP** immediately and ask the user to provide the path to the plan directory.

### Core Rules
- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails** (absolute must-follow rules)
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Complete Implementation**: All stories in plan must be implemented
- **Plan is source of truth** – follow phase ordering, dependencies, and parallel markers exactly
- **Pre-generate specs**: delegate to `andthen:spec-plan` per phase (handles parallelism, wave ordering, and cross-cutting review)
- **Review mode contract**: `per-story` (default) runs `review-gap` after each story, `none` skips automated `review-gap`, `full-plan` skips per-story review and runs one final `review-gap` against `PLAN_DIR/plan.md` after all stories are implemented. Specs are pre-generated before execution starts.

### Orchestrator Role
**You are the orchestrator.** Your job is to:
- Parse the plan and extract stories, phases, dependencies, parallel markers
- Delegate spec generation to `andthen:spec-plan` per phase
- Execute the per-story implementation pipeline (and per-story review when `REVIEW_MODE=per-story`)
- Track progress and update the plan as stories complete
- Handle failures and escalate when needed
- Run any required final plan-level review, then final verification

**You do NOT:**
- Write implementation code directly
- Let your context get bloated with implementation details
- Skip final verification due to context exhaustion


## GOTCHAS
- Executing stories out of wave order when there are dependencies
- Skipping spec-plan before executing a phase – all stories must have FIS before implementation starts
- Running the wrong review behavior for the selected `REVIEW_MODE`
- **Status updates get dropped when context is exhausted** – plan and FIS checkbox updates (Step 2c) are GATES that block the next phase, not optional cleanup. Update immediately after each story completes
- Not updating STATE.md when phases transition or blockers are discovered – state drift causes session continuity loss

### Helper Scripts
Helper scripts are available in `${CLAUDE_PLUGIN_ROOT}/scripts/` – use when applicable:
- `check-stubs.sh <path>` – scan for incomplete implementation indicators
- `check-wiring.sh <path>` – verify new/changed files are imported/referenced
- `verify-implementation.sh <file1> [file2...]` – combined existence + substance + wiring check


## WORKFLOW

### Step 1: Parse Plan

0. **Load session state** – Read `STATE.md` (path from **Project Document Index**, default: `docs/STATE.md`) if it exists. Extract session continuity notes (context from previous sessions), active stories and their status (detect resumed work), blockers (may affect execution order), and current phase (verify alignment with plan). If STATE.md does not exist, skip – it is optional.

1. Read `PLAN_DIR/plan.md`
2. If plan file missing, **STOP** and recommend `andthen:plan` first
3. Extract:
   - **Stories**: ID, name, scope, acceptance criteria, dependencies
   - **Phases**: Phase groupings and execution order
   - **Parallel markers**: `[P]` flags for concurrent execution
   - **Dependencies**: Cross-story dependency graph
   - **Waves**: Wave assignments per story (W1, W2, W3...) if present in the plan
4. Build execution plan respecting phase ordering and dependency chains

**Gate**: Plan parsed and phases identified


### Step 2: Phase Loop

For each phase in the plan:

#### 2a. Identify Stories and Generate Specs for This Phase

**Update project state** (if STATE.md exists): Use `andthen:ops update-state phase "{Phase N}: {phase_name}"` and `andthen:ops update-state status "On Track"` to record the active phase.

**Pre-generate all specs** for this phase by delegating to `andthen:spec-plan` (use `/` or `$` prefix depending on agent platform):
```
/andthen:spec-plan {PLAN_DIR} --phase {N}
```
This handles: checking for existing FIS, parallel sub-agent creation (opus model), wave ordering within the phase, cross-cutting review, and plan.md FIS field updates.

After `spec-plan` completes, re-read `plan.md` to pick up updated FIS paths, then determine execution approach:
- Stories marked `[P]` with no cross-dependencies → can run in parallel
- Stories with dependencies → must wait for predecessors to complete

**Gate**: All stories in current phase have FIS documents (verified via plan.md FIS fields)

#### 2b. Execute Story Pipelines

For each story (or group of parallel stories), run the required execution stages for the selected `REVIEW_MODE` (use `/` prefix for Claude Code, `$` for Codex CLI). Specs are already generated by Step 2a.

**Stage 1 – Implement**:
`/andthen:exec-spec {fis_path}` (or `$andthen:exec-spec {fis_path}`) → Output: implemented story.

**Stage 2 – Review** (`REVIEW_MODE=per-story` only):
`/andthen:review-gap {fis_path}` (or `$andthen:review-gap {fis_path}`) – `review-gap` produces a dimensional verdict (PASS/FAIL) in its report Executive Summary. Treat FAIL as "issues found": fix them, then re-validate. Treat PASS as story complete. **Max 2 fix attempts** – if issues persist after 2 rounds, escalate to the user.

When `REVIEW_MODE=none` or `REVIEW_MODE=full-plan`, skip Stage 2 during story execution. `full-plan` runs a single plan-level `review-gap` after all phases complete; `none` leaves post-execution review to the user.

> **Note – nested loops**: When `exec-spec` runs internally (Stage 1), its TV04 remediation loop handles *implementation-level* issues (code review, tests, visual validation) with a 3-cycle cap. The `exec-plan` `review-gap` loop handles *integration and gap-level* issues. In `per-story` mode this happens per story; in `full-plan` mode it happens once against the whole plan after implementation.

#### Wave-Based Execution (within each phase)
If stories have wave assignments (W1, W2, etc.) from the plan:
1. Execute all W1 stories in parallel (these have no dependencies)
2. After W1 completes, execute all W2 stories in parallel
3. Continue through remaining waves
All stories in the same wave run in parallel (waves subsume [P] markers).

If no wave assignments present, fall back to the [P] marker
and dependency-based approach below.

**Parallelism strategy** – Use **parallel sub-agents** _(if supported by your coding agent)_ for independent `[P]` stories:
- Spawn one sub-agent per independent story execution pipeline
- Each sub-agent runs the required stages for its story based on `REVIEW_MODE`
- If sub-agents not available, execute stories sequentially

**Sub-agent prompt template** for parallel story execution (use `/` or `$` prefix depending on agent platform):
```
Execute the implementation pipeline for story {story_id}: {story_name}
Plan: {PLAN_DIR}/plan.md
FIS: {fis_path}
Review mode: {REVIEW_MODE}

Pipeline (spec is already generated):
1. Implement: /andthen:exec-spec {fis_path}
2. If review mode is per-story: /andthen:review-gap {fis_path} – Fix issues (max 2 attempts), then report results.
3. Update status: Update FIS checkboxes (all tasks, success criteria, validation checklist marked [x]).
   Update plan.md: set story Status to Done, check off acceptance criteria, update Story Catalog table.
   Use the `andthen:ops` skill for standardized updates.

Important:
- Read the Workflow Rules, Guardrails and Guidelines in CLAUDE.md before starting
- Follow existing codebase patterns
- Status updates are REQUIRED, not optional cleanup – do not skip step 3
- If review mode is `none` or `full-plan`, do not run `review-gap` on the individual FIS
- After completing the story pipeline, if STATE.md exists, update active story status via `andthen:ops`
- Report back: success/failure, FIS path, any issues encountered
```

**Model assignment** – Use `model: "sonnet"` for all implementation and review sub-agents. Spec generation is handled by `spec-plan` (Step 2a) using opus sub-agents.

#### 2c. Update Plan and FIS Status (REQUIRED GATE)

**CRITICAL – do this immediately after each story's pipeline completes, not as a batch at the end.**

After each story completes its required stages for the selected `REVIEW_MODE`, use the `andthen:ops` skill to update `plan.md`:
- Set the story's **Status** field to `Done`
- Set the story's **FIS** field to the generated spec path (e.g. `**FIS**: docs/specs/story-name.md`)
- Check off completed acceptance criteria checkboxes (`- [ ]` → `- [x]`)
- Update the Story Catalog table: set the story's Status column to `Done`

Also update each completed FIS file:
- Mark all task checkboxes as checked (`- [x]`)
- Mark success criteria and Final Validation Checklist items as checked

**Update STATE.md** (if it exists): Use `andthen:ops update-state active-story {story_id} Done` to reflect completion. If the next story is starting, also run `andthen:ops update-state active-story {next_story_id} "{next_story_name}" "In Progress"`.

After ops completes, **re-read plan.md and the FIS file** to verify updates were applied (`ops` runs in fork context and modifications may not be visible in your current state).

Move to next phase only after ALL stories in current phase are complete and plan is updated.

**Gate**: All stories in current phase completed, verified, AND plan.md + FIS checkboxes updated – verify before proceeding to next phase

#### Pipeline Flow Example

```
Phase 1 (Sequential, review mode = per-story): S01 → S02
  spec-plan Phase 1 (parallel spec creation + cross-cutting review)
  impl-S01 → review-S01 → impl-S02 → review-S02

Phase 2 (Parallel [P], review mode = full-plan): S03[P], S04[P], S05 (depends on S03)
  spec-plan Phase 2 (parallel spec creation + cross-cutting review)
  impl-S03 ──────────────────────→ impl-S05
  impl-S04 (parallel with S03)
  final review-gap PLAN_DIR/plan.md after all stories complete
```

**Gate**: All phases complete and all stories implemented. Per-story reviews must also be complete when `REVIEW_MODE=per-story`.


### Step 3: Final Review Stage

Handle review after implementation based on `REVIEW_MODE`:

- `per-story` – No extra review step here; story-level `review-gap` already completed in Step 2b.
- `none` – Skip automated review entirely. Record in the completion summary and session note that manual user review is still pending.
- `full-plan` – Run one final plan-level review on the merged implementation:
  `/andthen:review-gap {PLAN_DIR}/plan.md` (or `$andthen:review-gap {PLAN_DIR}/plan.md`)
  If issues are found: fix them, then re-validate. **Max 2 fix attempts** – if issues persist after 2 rounds, escalate to the user.

**Gate**: Required review behavior for the selected `REVIEW_MODE` is complete


### Step 4: Final Verification

**Orchestrator performs directly** (not delegated):

1. Run build – verify it succeeds
2. Run tests – verify all pass
3. Review overall integration across stories
4. Include verification evidence in completion summary:
   - **Build**: exit code or success/failure status
   - **Tests**: pass/fail counts (e.g., "42/42 pass")
   - **Linting/types**: error and warning counts

**Gate**: Build, tests, and integration verification all pass


### Step 5: Documentation Update

Spawn a **general-purpose sub-agent** _(if supported by your coding agent)_ to update project documentation. Scope the update to:
- **README**: reflect any new features, changed APIs, or updated setup steps from the implementation
- **CHANGELOG**: add entries for all implemented stories (following existing changelog format)
- **Affected docs**: update any documentation files directly referenced or impacted by the plan's changes

**Gate**: Documentation updated


## FAILURE HANDLING

- **Story pipeline fails** → if `REVIEW_MODE=per-story`, attempt fix (max 2 rounds via review-gap loop). Otherwise resolve within `exec-spec` or use `andthen:build-troubleshooter` sub-agent _(if supported)_ for diagnosis. Escalate to user only if troubleshooter also fails.
- **Final plan review fails** (`REVIEW_MODE=full-plan`) → attempt fix (max 2 rounds via final `review-gap` loop). Escalate to user if issues persist.
- **Dependent stories stay blocked** when a predecessor fails
- **If >50% of a phase fails** → pause execution, notify user with failure summary
- **Update STATE.md on failure** (if it exists): Use `andthen:ops update-state status "At Risk"` (or `"Blocked"` for critical failures). Add blockers via `andthen:ops update-state blocker "{description}"`.


## COMPLETION

When all phases are complete, print a summary including: stories completed, total phases, `REVIEW_MODE`, review results (or manual review pending for `none`), verification results (build/test status), and the path to the updated `PLAN_DIR/plan.md`.


## Post-Completion: Update Project State

After all phases complete (or if execution is interrupted/paused), update STATE.md via `andthen:ops` (if it exists):
- Set phase to the completed (or current) phase
- Set status to reflect outcome (`On Track` if all passed, `At Risk` if issues remain)
- Clear completed stories from Active Stories (mark as `Done`)
- Add a session continuity note summarizing: what was completed, what remains, any context the next session needs

Example: `andthen:ops update-state note "exec-plan complete: {N}/{M} stories done, all phases passed"` (or describe what remains if interrupted).


## Post-Completion: Update Project Learnings

After all phases complete, if the project has a learnings file (`LEARNINGS.md` or `implementation-notes.md` – check Project Document Index for location), update it with knowledge discovered across stories. Organize by topic, not chronologically. Types of knowledge to capture:
- **Traps & gotchas**: Non-obvious patterns that would bite a competent developer even with access to code and git history
- **Domain knowledge**: API quirks, framework behavior, naming decisions, business rules discovered in code
- **Procedural knowledge**: Deploy steps, test prerequisites, tooling patterns
- **Error patterns**: Recurring errors – note if deterministic (bad schema, wrong type → conclude immediately) or infrastructure (timeout, rate limit → log, conclude only when pattern emerges)
- **Cross-story insights**: Patterns that only become visible when implementing multiple stories (e.g., shared abstractions, recurring conflicts, dependency ordering lessons)

Keep entries brief (1-2 sentences each). Do NOT record what was implemented (that's in git history), how parts integrate (that's in the code), or routine decisions (that's in the FIS/spec).

**Self-maintenance**: When updating, also review nearby entries – merge overlapping items, remove knowledge that's no longer accurate, split sections that grow too long.
