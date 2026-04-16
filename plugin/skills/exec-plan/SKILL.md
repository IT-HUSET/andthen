---
description: Use when the user wants to execute an implementation plan. Runs the AndThen plan pipeline (spec-plan per phase, then exec-spec + quick-review per story, final review-gap). Supports Agent Teams (--team) and sub-agents (portable fallback). Trigger on 'execute this plan', 'implement this plan', 'run the plan', 'execute with agents', 'run as team'.
argument-hint: <path-to-plan-directory | --issue <number> | issue URL> [path-to-code-repo] [--team] [--worktree]
---

# Execute Plan


Execute ALL stories in an implementation plan (from `andthen:plan`) through a fixed pipeline: **spec-plan (per phase) → exec-spec → quick-review** per story, then one **review-gap** on the whole plan.

Supports two execution modes:
- **Sub-agents** (default) – parallel sub-agents per wave, sequential fallback when unavailable
- **Agent Teams** (`--team`) – team-based pipeline with optional worktree isolation for parallel execution


## VARIABLES

PLAN_SOURCE: $ARGUMENTS
CODE_DIR: second positional argument _(optional – for multi-repo setups where plan and code live in different repos)_

### Optional Flags
- `--team` → USE_TEAM: force Agent Teams mode; error if unavailable
- `--worktree` → USE_WORKTREE: enable isolated git worktrees for parallel execution (team mode only; default: `false`)


## USAGE

```
/exec-plan path/to/plan                       # Sub-agent mode (default)
/exec-plan --issue 123                        # From GitHub issue
/exec-plan path/to/plan --team                # Force Agent Teams
/exec-plan path/to/plan --team --worktree     # Team + parallel worktrees
/exec-plan path/to/plan path/to/code --team   # Multi-repo setup
```


## INSTRUCTIONS

Require `PLAN_SOURCE`. Stop if missing.

### Core Rules
- **Complete implementation**: all stories in plan must be implemented
- **Plan is source of truth** – follow phase ordering, dependencies, and parallel markers exactly
- **Pre-generate specs**: invoke `andthen:spec-plan` per phase before executing stories
- **Fixed pipeline per story**: `exec-spec` → `quick-review`. One final `review-gap` on the whole plan after all stories.
- **Status updates are gates** – plan.md and FIS checkpoint updates must happen immediately after each story, not batched

### Orchestrator Role
**You are the orchestrator.** Parse the plan, invoke spec-plan per phase, execute the per-story pipeline, track progress, update the plan as stories complete, handle failures, and run final verification.

Do not: write implementation code directly, let context bloat, or skip final verification.


## GOTCHAS
- Executing stories out of wave order when dependencies exist
- Skipping spec-plan before executing a phase
- **Status updates dropped when context exhausted** – plan and FIS checkpoint updates are gates that block the next phase
- Not updating the `State` document (see **Project Document Index**) when phases transition or blockers are discovered
- **Re-executing a composite FIS already implemented** – check the executed-FIS set before each story's pipeline
- **Marking Done without verifying plan acceptance criteria**
- **(Team mode)** Do not use `isolation: "worktree"` with `team_name` – Claude Code bug ([#33045](https://github.com/anthropics/claude-code/issues/33045)); instruct implementers to call `EnterWorktree` themselves
- **(Team mode, worktree)** Wave N+1 worktrees must be created AFTER Wave N merges complete
- **(Team mode)** Only the orchestrator writes to the `State` document (avoids race conditions)

### Helper Scripts
Available in `${CLAUDE_PLUGIN_ROOT}/scripts/`: `check-stubs.sh`, `check-wiring.sh`, `verify-implementation.sh`.


## WORKFLOW

### Step 1: Parse Plan

0. Resolve `PLAN_SOURCE`: if `--issue` or GitHub URL, follow `${CLAUDE_PLUGIN_ROOT}/references/resolve-github-input.md`. Compatible types: `plan-bundle` — extract per the **Resolve Plan-Bundle Input** procedure in `${CLAUDE_PLUGIN_ROOT}/references/github-artifact-roundtrip.md`. All other typed artifacts → stop and exit with the correct skill. Untyped → stop — this skill requires a typed plan artifact.

1. **Resolve CODE_DIR** _(skip if `--team` not set and no second positional arg)_:
   - If provided: verify git repository, resolve to absolute path
   - If not provided: auto-detect from PLAN_DIR's git root vs CWD's git root. Same repo → use that root. Different repos → use CWD's git root
   - Resolve `BASE_BRANCH`: `git -C {CODE_DIR} rev-parse --abbrev-ref HEAD`

2. **Load session state** – Read the `State` document (see **Project Document Index**; default: `docs/STATE.md`) if it exists. Extract session continuity notes, active stories, blockers, and current phase.

3. Read `PLAN_DIR/plan.md`. If missing, stop — a valid plan artifact is required upstream (typically from `andthen:plan`).
4. Extract stories (ID, name, scope, acceptance criteria, dependencies), phases, parallel markers `[P]`, dependency graph, and wave assignments (W1, W2, W3...)
5. Build execution plan respecting phase ordering and dependency chains

**Gate**: Plan parsed and phases identified


### Step 2: Determine Execution Mode

Check whether Agent Teams are available by verifying that team creation tools exist (e.g. `TeamCreate`).

- **`--team` AND available** → Team mode (Step 3T)
- **`--team` AND unavailable** → inform user it requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`; exit
- **No `--team`** → Sub-agent mode (Step 3). Mention `--team` is available if the user wants team execution.

**Gate**: Execution mode determined


### Step 3: Phase Loop

For each phase in the plan:

#### 3a. Generate Specs for This Phase

**Update project state** (if the `State` document exists; see **Project Document Index**): `andthen:ops update-state phase "{Phase N}: {phase_name}"` and `andthen:ops update-state status "On Track"`.

Invoke `andthen:spec-plan`:
```
/andthen:spec-plan {PLAN_DIR} --phase {N}
```
After `spec-plan` completes, re-read `plan.md` to pick up updated FIS paths.

**Gate**: All stories in current phase have FIS documents

#### 3b. Execute Story Pipelines

**Shared-FIS Dedup**: If this story's FIS path has already been executed by a prior story (composite or collected thin-specs FIS), skip exec-spec and quick-review. Still run status update and mark `Done`. Track executed FIS paths in a set.

**Per-story pipeline**:
1. **Implement**: `/andthen:exec-spec {fis_path}`
2. **Review**: `/andthen:quick-review` on the story's changes

**Wave-based execution**: Execute W1 stories in parallel (via sub-agents if supported), then W2, etc. If sub-agents not available, execute stories sequentially.

**Sub-agent prompt** for parallel story execution:
```
Implement story {story_id}: {story_name}
Plan: {PLAN_DIR}/plan.md | FIS: {fis_path}

1. /andthen:exec-spec {fis_path}
2. /andthen:quick-review (on changes from step 1)
3. Update status: /andthen:ops update-fis {fis_path} all
   /andthen:ops update-plan {PLAN_DIR}/plan.md {story_id} Done

Status updates are required. Report back: success/failure, FIS path, any issues.
```

**Model assignment**: Use a capable coding model (`model: "sonnet"`, `gpt-5.3-codex`, or similar).

#### 3c. Update Plan and FIS Status (**Gate**)

Do this immediately after each story's pipeline — not as a batch.

Invoke `andthen:ops` to update `plan.md`: Status → `Done`, FIS field, acceptance criteria, Story Catalog status. Use `andthen:ops update-fis {fis_path} all` to mark FIS checkboxes. Update the `State` document (see **Project Document Index**): `andthen:ops update-state active-story {story_id} Done`.

After ops completes, **re-read plan.md and the FIS** to verify updates applied.

If `PLAN_SOURCE_MODE = github-artifact`, apply the **Plan-Bundle Continuation Sync** from `${CLAUDE_PLUGIN_ROOT}/references/github-artifact-roundtrip.md` now.

**Gate**: All stories in current phase completed, verified, and plan.md + FIS checkboxes updated

**Gate**: All phases complete.


### Step 3T: Phase Loop (Team Mode)

> **This step replaces Step 3 when `--team` is active.** Steps 4–6 are shared.

For each phase: run spec-plan (same as Step 3a), then create and manage the Agent Team pipeline.

#### Team Setup

Create team `"plan-pipeline"` with pre-assigned tasks. Size: 1 implementer (≤4 stories), 2 (5–10), 3 (11+). Add 1–2 reviewers for `quick-review` tasks. Use a capable coding model for all teammates.

**Implementer prompt** – include in each implementer's system prompt:
- Role constraint: only work on assigned `impl-*` tasks
- Per-task workflow: `cd {CODE_DIR}` → (if worktree: `EnterWorktree "story-{task_id}"`) → `/andthen:exec-spec {fis_path}` → commit → (if worktree: `ExitWorktree(keep)`) → `/andthen:ops update-fis {fis_path} all` → mark task done
- FIS paths are absolute; status updates are required; escalate unresolvable issues to orchestrator

**Reviewer prompt** – include in each reviewer's system prompt:
- Role constraint: only work on assigned `review-*` tasks
- Per-task workflow: `cd {CODE_DIR}` → `/andthen:quick-review` on the story's changes (code is on `{BASE_BRANCH}` after impl/merge) → mark task done
- Escalate unresolvable issues to orchestrator

#### Task Management

**Shared-FIS Dedup**: One impl task per unique FIS path; constituent stories share it.

**Task naming**: `impl-{story_id}` / `review-{story_id}`. Composite: `impl-{S01-S02}`. Round-robin assign; do not self-assign impl and review of the same story to the same agent.

**Dependencies** (sequential, `USE_WORKTREE=false`): each `impl-*` blocked by previous `review-*`. Parallel markers ignored.

**Dependencies** (worktree, `USE_WORKTREE=true`): current-wave `impl-*` unblocked; `review-*` blocked until wave merge; W2+ `impl-*` blocked by prior-wave merge completion.

#### Merge Wave _(worktree mode only)_

After all `impl-*` in the current wave complete: sequentially merge each worktree branch (`--no-ff`), verify build, clean up worktree/branch, then unblock review tasks. Handle conflicts: imports → take both; lock files → `--theirs` + reinstall; logic conflicts → spawn troubleshooter or escalate.

#### Status Updates (**Gate**)

Same as Step 3c. Additionally verify Plan Acceptance Gate before marking Done: each acceptance criterion demonstrably satisfied, scope notes present when FIS narrowed scope. For composite FIS: verify ALL constituent stories. Move to next phase only after current phase fully complete.

#### Monitoring

Print progress updates — the user cannot see agent activity. Report task creation/assignment, agent starts/completions, wave completions, merge results, phase summaries, and failures.

After all phases: clean up remaining worktrees (`git worktree prune`), shutdown teammates, delete team.

**Gate**: All phases complete.


### Step 4: Final Review

Run `/andthen:review-gap {PLAN_DIR}/plan.md` on the whole plan. If FAIL, run `/andthen:remediate-findings {report_path}`. Escalate if issues persist after one remediation pass.

**Gate**: Final review-gap complete

### Step 5: Final Verification

Run build, run tests, review cross-story integration. Include verification evidence: **Build** (exit code/status), **Tests** (pass/fail counts), **Linting/types** (error/warning counts).

**Gate**: Build, tests, integration pass

### Step 6: Canonical Continuation Sync _(if `PLAN_SOURCE_MODE = github-artifact`)_
Apply the **Plan-Bundle Continuation Sync** from `${CLAUDE_PLUGIN_ROOT}/references/github-artifact-roundtrip.md` as the final gate.


## FAILURE HANDLING

- **Story pipeline fails** → use `andthen:build-troubleshooter` agent or escalate
- **Final review fails** → remediate once; escalate if issues persist
- **Dependent stories blocked** when predecessor fails
- **>50% of a phase fails** → pause this run and return a failure summary
- **Update the `State` document on failure** (see **Project Document Index**): `andthen:ops update-state status "At Risk"` or `"Blocked"`

### Multi-Repo Rules _(team mode, when CODE_DIR ≠ PLAN_DIR's git root)_
- All git operations target `CODE_DIR` – never the plan repo
- `EnterWorktree` must be called from `CODE_DIR` context
- FIS paths passed to agents must be **absolute**
- The plan repo is **read-only for git operations** – only the orchestrator updates `plan.md`


## COMPLETION

Print summary: stories completed, total phases, execution mode, review/verification results, path to `PLAN_DIR/plan.md`.

## Post-Completion

### State Document (see **Project Document Index**)
Set phase to the completed or current phase. Set status to `On Track` when all checks passed, otherwise `At Risk`. Clear completed stories from Active Stories by marking them `Done`. Add a session continuity note summarizing what completed, what remains, and what the next session needs.

### Learnings (see **Project Document Index**)
If the `Learnings` document exists, capture cross-story insights, traps, domain knowledge, and error patterns. Organize by topic. Keep entries brief (1-2 sentences). Do not create a new `Learnings` document if none exists.
