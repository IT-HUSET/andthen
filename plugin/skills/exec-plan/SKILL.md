---
description: Execute an entire implementation plan through a pipeline (spec-plan per phase, then exec-spec with configurable review mode)
argument-hint: <path-to-plan-directory> [--review-mode per-story|none|full-plan]
---

# Execute Plan

Execute ALL stories in an implementation plan (from `andthen:plan`) through a pipeline: **spec-plan (per phase) → exec-spec**, with configurable review behavior.

Pre-generates specs per phase via `andthen:spec-plan`, then executes using **parallel sub-agents** _(if supported)_, otherwise sequentially.


## VARIABLES
PLAN_DIR: positional argument from `$ARGUMENTS`
REVIEW_MODE: from `--review-mode` flag (`per-story`, `none`, or `full-plan`; default `per-story`)


## USAGE
```
/exec-plan path/to/plan [--review-mode per-story|none|full-plan]
```

## INSTRUCTIONS

Make sure `PLAN_DIR` is provided – otherwise **STOP** and ask.

### Core Rules
- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** in CLAUDE.md / AGENTS.md before starting.
- **Complete Implementation**: All stories in plan must be implemented
- **Plan is source of truth** – follow phase ordering, dependencies, and parallel markers exactly
- **Pre-generate specs**: invoke the `andthen:spec-plan` skill per phase

### Review Mode Contract (defined once)
- `per-story` (default): `review-gap` after each story; FAIL triggers `remediate-findings` (max 2 review/remediation rounds per story)
- `none`: skips automated `review-gap`
- `full-plan`: skips per-story review; one final `review-gap` on `PLAN_DIR/plan.md` after all phases; FAIL triggers `remediate-findings` (max 2 review/remediation rounds)

**Review mode guidance**: `per-story` (default) is recommended for most plans — it catches issues at the story level where they are cheapest to fix and prevents issue accumulation across stories. Use `none` only for time-critical execution where you accept the risk of deferred review. Use `full-plan` for small plans (4 or fewer stories) where per-story overhead exceeds the benefit.

Specs are pre-generated before execution starts. `exec-spec`'s TV05 loop handles *implementation-level* issues (3-cycle cap); `exec-plan`'s review-gap + remediate-findings loop handles *integration and gap-level* issues.

### Orchestrator Role
**You are the orchestrator.** Your job:
- Parse the plan and extract stories, phases, dependencies, parallel markers
- Invoke the `andthen:spec-plan` skill for spec generation per phase
- Execute the per-story pipeline (and per-story review when `REVIEW_MODE=per-story`)
- Track progress and update the plan as stories complete
- Handle failures and escalate when needed
- Run any required final plan-level review, then final verification

**You do NOT:** write implementation code directly, let context bloat, or skip final verification.


## GOTCHAS
- Executing stories out of wave order when dependencies exist
- Skipping spec-plan before executing a phase – all stories must have FIS before implementation starts
- Running the wrong review behavior for the selected `REVIEW_MODE`
- **Status updates dropped when context exhausted** – plan and FIS checkbox updates (Step 2c) are GATES blocking the next phase, not optional cleanup
- Not updating STATE.md when phases transition or blockers are discovered
- **Re-executing a composite FIS already implemented** – check the executed-FIS set before each story's pipeline
- **Marking Done without verifying plan acceptance criteria** – always check plan criteria against implementation

### Helper Scripts
Available in `${CLAUDE_PLUGIN_ROOT}/scripts/`: `check-stubs.sh`, `check-wiring.sh`, `verify-implementation.sh`.


## WORKFLOW

### Step 1: Parse Plan

0. **Load session state** – Read `STATE.md` (from Project Document Index, default: `docs/STATE.md`) if it exists. Extract session continuity notes, active stories, blockers, and current phase.

1. Read `PLAN_DIR/plan.md`; if missing, **STOP** and recommend the `andthen:plan` skill first
2. Extract stories (ID, name, scope, acceptance criteria, dependencies), phases, parallel markers `[P]`, dependency graph, and wave assignments (W1, W2, W3...)
3. Build execution plan respecting phase ordering and dependency chains

**Gate**: Plan parsed and phases identified


### Step 2: Phase Loop

For each phase in the plan:

#### 2a. Generate Specs for This Phase

**Update project state** (if STATE.md exists): `andthen:ops update-state phase "{Phase N}: {phase_name}"` and `andthen:ops update-state status "On Track"`.

Invoke the `andthen:spec-plan` skill:
```
/andthen:spec-plan {PLAN_DIR} --phase {N}
```
This handles: existing FIS checks, parallel sub-agent creation, wave ordering, cross-cutting review, and plan.md FIS field updates.

After `spec-plan` completes, re-read `plan.md` to pick up updated FIS paths.

**Gate**: All stories in current phase have FIS documents (verified via plan.md FIS fields)

#### 2b. Execute Story Pipelines

For each story (or group of parallel stories), run the required stages for the selected `REVIEW_MODE`. Specs already generated by Step 2a.

**Shared-FIS Dedup**: If this story's FIS path has already been executed by a prior story (composite or collected thin-specs FIS), skip exec-spec and review. Still run the **Plan Acceptance Gate** (Step 2c) and mark `Done`. Track executed FIS paths in a set.

**Stage 1 – Implement**: `/andthen:exec-spec {fis_path}`

**Stage 2 – Review** (`per-story` only): `/andthen:review-gap {fis_path}`. If it fails, capture the report path and run `/andthen:remediate-findings {report_path}`. Re-run review and repeat up to 2 rounds. Skip for `none` and `full-plan`.

**Wave-based execution**: Execute W1 stories in parallel, then W2, etc. If no wave assignments, use `[P]` markers and dependency order. If sub-agents not available, execute stories sequentially.

**Sub-agent prompt template** for parallel story execution:
```
Execute the implementation pipeline for story {story_id}: {story_name}
Plan: {PLAN_DIR}/plan.md
FIS: {fis_path}
Review mode: {REVIEW_MODE}

Pipeline (spec already generated):
1. Implement: /andthen:exec-spec {fis_path}
2. If review mode is per-story: /andthen:review-gap {fis_path}. If FAIL, capture the report path and run /andthen:remediate-findings {report_path}; then re-run review (max 2 rounds).
3. Update status:
   - FIS checkboxes: /andthen:ops update-fis {fis_path} all
   - Plan status: /andthen:ops update-plan {PLAN_DIR}/plan.md {story_id} Done

Important:
- Read Workflow Rules, Guardrails and Guidelines in CLAUDE.md before starting
- Follow existing codebase patterns
- Status updates are REQUIRED – do not skip step 3
- Do not run review-gap if review mode is none or full-plan
- After completing, update active story status via andthen:ops if STATE.md exists
- Report back: success/failure, FIS path, any issues
```

**Model assignment**: Use a capable coding model (`model: "sonnet"`, `gpt-5.3-codex`, or similar) for implementation and review sub-agents.

#### 2c. Update Plan and FIS Status (REQUIRED GATE)

**Do this immediately after each story's pipeline – not as a batch.**

**Plan Acceptance Gate** before marking Done:
1. Verify each plan acceptance criterion is satisfied against the implementation
2. If the FIS narrowed scope, a scope note must exist in plan criteria; otherwise escalate to user
3. **Verify spec compliance**: confirm that exec-spec's spec compliance spot-check (Step 4a.7) completed — check that FIS task checkboxes are marked and verification evidence exists. If evidence is missing or checkboxes are incomplete, flag the story for re-verification before marking Done

Invoke the `andthen:ops` skill to update `plan.md`: Status → `Done`, FIS field, acceptance criteria, Story Catalog status. Use `andthen:ops update-fis {fis_path} all` to mark FIS checkboxes (catches context-exhaustion gaps). Update STATE.md: `andthen:ops update-state active-story {story_id} Done`.

After ops completes, **re-read plan.md and the FIS** to verify updates applied.

**Gate**: All stories in current phase completed, verified, and plan.md + FIS checkboxes updated

#### Pipeline Flow Example
```
Phase 1 (Sequential, per-story): spec-plan → impl-S01 → review-S01 → impl-S02 → review-S02
Phase 2 (Parallel, full-plan):   spec-plan → impl-S03 ─────────────→ impl-S05
                                             impl-S04 (parallel)
                                             final review-gap after all complete
```

**Gate**: All phases complete. Per-story reviews complete when `REVIEW_MODE=per-story`.


### Step 3: Final Review Stage

- `per-story` – No extra step.
- `none` – Skip; note manual review pending in completion summary and STATE.md session note.
- `full-plan` – `/andthen:review-gap {PLAN_DIR}/plan.md`; if FAIL, capture the report path and run `/andthen:remediate-findings {report_path}`; re-run review for up to 2 rounds, then escalate if issues persist.

**Gate**: Required review for selected `REVIEW_MODE` complete

### Step 4: Final Verification

Run build, run tests, review cross-story integration. Include evidence per `${CLAUDE_PLUGIN_ROOT}/references/verification-evidence.md`: **Build**, **Tests**, **Linting/types**.

**Gate**: Build, tests, integration pass

### Step 5: Documentation Update

Spawn a general-purpose sub-agent to refresh: README (new features, changed APIs, setup steps), CHANGELOG (entries for each story, match existing format), and affected docs.

**Gate**: Documentation updated


## FAILURE HANDLING

- **Story pipeline fails** → attempt remediation (max 2 review/remediation rounds when `per-story`; otherwise use the `andthen:build-troubleshooter` agent or escalate)
- **Final review fails** (`full-plan`) → remediate (max 2 review/remediation rounds); escalate if persist
- **Dependent stories blocked** when predecessor fails
- **>50% of a phase fails** → pause, notify user with failure summary
- **Update STATE.md on failure**: `andthen:ops update-state status "At Risk"` or `"Blocked"`. Add blockers via `andthen:ops update-state blocker "{description}"`.


## COMPLETION

Print summary: stories completed, phases, `REVIEW_MODE`, review/verification results, path to updated `PLAN_DIR/plan.md`.

## Post-Completion
Follow `${CLAUDE_PLUGIN_ROOT}/references/post-completion-guide.md` (`Plan Runs` → `STATE.md` and `Learnings`).
