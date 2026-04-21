---
description: Use when the user wants to execute a fully-specced implementation plan bundle. Runs a fixed pipeline per story (exec-spec + quick-review) and a final gap review on the whole plan. Requires a plan bundle where every story already has a FIS. Supports Agent Teams (--team) and sub-agents (portable fallback). Trigger on 'execute this plan', 'implement this plan', 'run the plan', 'execute with agents', 'run as team'.
argument-hint: <path-to-plan-directory> [path-to-code-repo] [--team] [--worktree]
---

# Execute Plan


Execute ALL stories in a fully-specced plan bundle (from the `andthen:plan` skill) through a fixed pipeline: **exec-spec → quick-review** per story, then one final gap review (`review --mode gap`) on the whole plan.

**Requires a fully-specced plan bundle** — every story in `plan.md` must already have a FIS. If any story's `**FIS**` field is `–` or points at a non-existent file, stop and redirect to the `andthen:plan` skill to complete spec generation (`andthen:plan` is resumable — it only fills missing FIS). If no `prd.md` exists upstream, the full chain is `andthen:prd → andthen:plan → andthen:exec-plan`; `andthen:plan` will redirect to `andthen:prd` itself when its input lacks a PRD.

Supports two execution modes:
- **Sub-agents** (default) – parallel sub-agents per wave, sequential fallback when unavailable
- **Agent Teams** (`--team`) – team-based pipeline with optional worktree isolation for parallel execution


## VARIABLES

PLAN_DIR: $ARGUMENTS
CODE_DIR: second positional argument _(optional – for multi-repo setups where plan and code live in different repos)_

### Optional Flags
- `--team` → USE_TEAM: force Agent Teams mode; error if unavailable
- `--worktree` → USE_WORKTREE: enable isolated git worktrees for parallel execution (team mode only; default: `false`)


## INSTRUCTIONS

Require `PLAN_DIR`. Stop if missing.

### Core Rules
- **Complete implementation**: all stories in plan must be implemented
- **Plan is source of truth** – follow phase ordering, dependencies, and parallel markers exactly
- **Plan must be fully specced** – every story's `**FIS**` field must point at an existing file. Fail fast otherwise; redirect to the `andthen:plan` skill
- **Fixed pipeline per story**: `exec-spec` → `quick-review`, then one final `review --mode gap` on the whole plan
- **Execution discipline and authoritative status writes** — see `references/execution-discipline.md` (Stop-the-Line, objective-vs-subjective finding policy, authoritative-writes ownership). `exec-spec` Step 5b is the per-story status write; sub-agents and teammates do not additionally call `andthen:ops update-*`. The orchestrator writes cross-story state and repair writes only.

### Orchestrator Role
**You are the orchestrator.** Parse the plan, run the per-story pipeline, verify each story's `exec-spec` writes landed, handle phase transitions, manage failures, run final verification.

**Delegate story code to `exec-spec`** (sub-agent, teammate, or sequential fallback). If a delegated story returns partial or non-green, take over locally, repair, re-verify, continue — reporting broken state is not completion.

Do not: generate specs (that's `andthen:plan`), let context bloat, or skip final verification.


## GOTCHAS
- Executing stories out of wave order when dependencies exist
- Accepting a plan bundle with missing FIS and trying to synthesize specs ad-hoc — stop and redirect to the `andthen:plan` skill instead
- **Status updates dropped when context exhausted** – plan and FIS checkpoint updates are gates that block the next phase
- Not updating the `State` document (see **Project Document Index**) when phases transition or blockers are discovered
- **Marking Done without verifying plan acceptance criteria**
- **(Team mode)** Do not use `isolation: "worktree"` with `team_name` – Claude Code bug ([#33045](https://github.com/anthropics/claude-code/issues/33045)); instruct implementers to call `EnterWorktree` themselves
- **(Team mode, worktree)** Wave N+1 worktrees must be created AFTER Wave N merges complete


## WORKFLOW

### Step 1: Parse Plan

1. **Resolve CODE_DIR** _(skip if `--team` not set and no second positional arg)_:
   - If provided: verify git repository, resolve to absolute path
   - If not provided: auto-detect from PLAN_DIR's git root vs CWD's git root. Same repo → use that root. Different repos → use CWD's git root
   - Resolve `BASE_BRANCH`: `git -C {CODE_DIR} rev-parse --abbrev-ref HEAD`

2. **Load session state** – Read the `State` document (see **Project Document Index**; default: `docs/STATE.md`) if it exists. Extract session continuity notes, active stories, blockers, and current phase.

3. Read `PLAN_DIR/plan.md`. If missing, stop — a valid plan artifact is required upstream (typically from the `andthen:plan` skill).
4. Extract stories (ID, name, scope, acceptance criteria, dependencies), phases, parallel markers `[P]`, dependency graph, and wave assignments (W1, W2, W3...)
5. **Verify bundle is fully specced**: every story's `**FIS**` field must point at an existing file. If any story has `**FIS**: –` or references a non-existent file, stop and print: `Plan bundle is not fully specced — run /andthen:plan {PLAN_DIR} to fill missing FIS (plan is resumable and only regenerates missing specs).` Do not proceed.
6. Build execution plan respecting phase ordering and dependency chains

**Gate**: Plan parsed, bundle verified fully specced, phases identified


### Step 2: Determine Execution Mode

Check whether Agent Teams are available by verifying that team creation tools exist (e.g. `TeamCreate`).

- **`--team` AND available** → Team mode (Step 3T)
- **`--team` AND unavailable** → inform user it requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`; exit
- **No `--team`** → Sub-agent mode (Step 3). Mention `--team` is available if the user wants team execution.

**Gate**: Execution mode determined


### Step 3: Phase Loop

For each phase in the plan:

#### 3a. Phase Transition

**Update project state** (if the `State` document exists; see **Project Document Index**): invoke the `andthen:ops` skill with `update-state phase "{Phase N}: {phase_name}"` and `update-state status "On Track"`.

The bundle is already fully specced (verified in Step 1, item 5). Re-read `plan.md` if any status updates from a prior phase may have landed during execution.

**Gate**: Phase context loaded, `plan.md` current

#### 3b. Execute Story Pipelines

**Per-story pipeline** (one FIS per story, so each story gets its own exec-spec + quick-review run):
1. **Implement**: `/andthen:exec-spec {fis_path}`
2. **Review**: `/andthen:quick-review` on the story's changes

**Wave-based execution**: W1 in parallel (via sub-agents if supported), then W2, etc. Fall back to sequential in-orchestrator execution if sub-agents are unavailable or delegated execution stalls / returns partial / non-green.

**Sub-agent prompt**:
```
Story {story_id}: {story_name}
Plan: {PLAN_DIR}/plan.md | FIS: {fis_path}

1. /andthen:exec-spec {fis_path}
2. /andthen:quick-review on the changes

Run `/andthen:exec-spec` — its Step 5b writes this story's status.
Do NOT call /andthen:ops update-plan, update-fis, or update-state
*beyond* what exec-spec does internally. (Suppressing exec-spec's
own Step 5b writes is also wrong.)

Report:
- Step results (success/failure), files changed
- `exec-spec` Step 4a numbers (build, tests, lint/type-check)
- Any issues, incomplete work, or non-green state — be explicit
```

**Model assignment**: Use a capable coding model (`model: "sonnet"`, `gpt-5.3-codex`, or similar).

#### 3c. Verify Green, Confirm Writes Landed (**Gate**)

Run immediately after each story — not as a batch. Worker self-reports do not count.

**Green gate**:
- Build / compile clean for affected packages
- Targeted tests pass (full suite runs in Step 5)
- Lint / type-check clean for touched files
- No broken intermediate state (partial migration, half-refactored call sites, dead imports)

Fail → story stays `In Progress`. Apply Stop-the-Line per `execution-discipline.md`: repair locally, re-delegate (template below), or invoke the `andthen:triage` skill. Iterate until green.

Pass → **re-read `plan.md` and the FIS** to confirm `exec-spec` Step 5b's writes landed (story row `Done`, FIS field, acceptance checkboxes, `State` active-story `Done`). Missing → call the matching `andthen:ops update-*` once to repair. Outside this repair path and Post-Completion bookkeeping, the orchestrator does not write story-level status.

**Re-delegation template** (remediation via sub-agent):
```
Remediate story {story_id} — prior attempt non-green.
Plan: {PLAN_DIR}/plan.md | FIS: {fis_path}

Failure list:
- {failure 1}
- {failure 2}

Fix forward on the existing tree. Target the listed failures, then re-run
`exec-spec` Step 4a verification (build, tests, lint/type-check).

`exec-spec` wrote status in the prior attempt — do NOT call
/andthen:ops update-* beyond what exec-spec does internally.

Report: failures resolved, verification numbers, new issues (if any).
```

**Gate**: All stories in current phase verified green and their plan.md + FIS writes confirmed (or repaired)

**Gate**: All phases complete.


### Step 3T: Phase Loop (Team Mode)

> **This step replaces Step 3 when `--team` is active.** Steps 4–6 are shared.

For each phase: update project state (same as Step 3a), then create and manage the Agent Team pipeline. The bundle is already fully specced — no per-phase spec generation step.

#### Team Setup

Create team `"plan-pipeline"` with pre-assigned tasks. Size: 1 implementer (≤4 stories), 2 (5–10), 3 (11+). Add 1–2 reviewers for `quick-review` tasks. Use a capable coding model for all teammates.

**Implementer prompt** – include in each implementer's system prompt:
- Only work on assigned `impl-*` tasks
- Per task: `cd {CODE_DIR}` → (worktree: `EnterWorktree "story-{task_id}"`) → `/andthen:exec-spec {fis_path}` → commit → (worktree: `ExitWorktree(keep)`) → mark done; report `exec-spec` Step 4a numbers (build, tests, lint/type-check)
- `exec-spec` Step 5b writes status. Do NOT call `andthen:ops update-plan`, `update-fis`, or `update-state` *beyond* what `exec-spec` does internally (and do not suppress its Step 5b writes)
- Absolute FIS paths; escalate unresolvable issues

**Reviewer prompt** – include in each reviewer's system prompt:
- Role constraint: only work on assigned `review-*` tasks
- Per-task workflow: `cd {CODE_DIR}` → `/andthen:quick-review` on the story's changes (code is on `{BASE_BRANCH}` after impl/merge) → mark task done
- Escalate unresolvable issues to orchestrator

#### Task Management

**Task naming**: `impl-{story_id}` / `review-{story_id}` (one impl task per story, one review task per story — each story has its own FIS). Round-robin assign; do not self-assign impl and review of the same story to the same agent.

**Dependencies** (sequential, `USE_WORKTREE=false`): each `impl-*` blocked by previous `review-*`. Parallel markers ignored.

**Dependencies** (worktree, `USE_WORKTREE=true`): current-wave `impl-*` unblocked; `review-*` blocked until wave merge; W2+ `impl-*` blocked by prior-wave merge completion.

#### Merge Wave _(worktree mode only)_

After all `impl-*` in the current wave complete: sequentially merge each worktree branch (`--no-ff`), verify build, clean up worktree/branch, then unblock review tasks. Handle conflicts: imports → take both; lock files → `--theirs` + reinstall; logic conflicts → spawn troubleshooter or escalate.

#### Status Updates (**Gate**)

Same verification discipline as Step 3c (green gate → confirm `exec-spec` writes landed → repair missing writes if needed). Additionally verify Plan Acceptance Gate before accepting Done: each acceptance criterion demonstrably satisfied, scope notes present when FIS narrowed scope. Move to next phase only after current phase fully complete.

**Green-gate timing**:
- **Worktree** — per-worktree build/tests pre-merge; orchestrator gate on `BASE_BRANCH` post-merge. Stop-the-Line on `BASE_BRANCH`, not inside a worktree.
- **No worktree** — gate after each `impl-*`, before the matching `review-*` unblocks.

**Take-over topology** (orchestrator repair):
- **Worktree, pre-merge** — enter the live worktree (`EnterWorktree` if implementer exited), fix, re-verify, commit, then merge.
- **Worktree post-merge** or **no worktree** — repair on `BASE_BRANCH` in orchestrator's CWD.

#### Monitoring

Print progress updates — the user cannot see agent activity. Report task creation/assignment, agent starts/completions, wave completions, merge results, phase summaries, and failures.

After all phases: clean up remaining worktrees (`git worktree prune`), shutdown teammates, delete team.

**Gate**: All phases complete.


### Step 4: Final Review

Spawn a `general-purpose` sub-agent whose prompt runs the `andthen:review` skill in `--mode gap` on the whole plan. Fresh context is load-bearing here — by this step the orchestrator has watched every story get built and is biased by construction context. A sub-agent sees only the plan and the final code, which is what the gap verdict should reflect.

**Model**: Use a strong reasoning model (`model: "opus"`, `gpt-5.4`, or similar). Gap review runs inline in the sub-agent's own context (per `lens-gap.md` — the gap lens does not delegate), so the sub-agent's model IS the reviewing model. Whole-plan gap review is cross-cutting (story interactions, acceptance-criteria coverage, requirements drift) rather than routine pattern-matching, which justifies the stronger tier over the sonnet default.

Resolve `PLAN_DIR` and `CODE_DIR` to absolute paths (`PLAN_DIR_ABS`, `CODE_DIR_ABS`) before substituting into the prompt — relative paths break in multi-repo setups where the sub-agent's CWD may match neither repo.

**Sub-agent prompt**:
```
Run /andthen:review --mode gap {PLAN_DIR_ABS}/plan.md on the whole plan.

Implementation lives in: {CODE_DIR_ABS}

Do NOT pass --inline-findings — the final gap gate must write a report file so remediate-findings can consume it.

Report back:
1. The verdict (PASS/FAIL) from the canonical gap verdict table
2. The absolute path to the written report file
```

Verify the sub-agent returned both a verdict and a path that resolves to a readable file. If either is missing, report the failure and stop — do not silently retry; the downstream remediation step depends on a valid report artifact.

If the verdict is FAIL, invoke the `andthen:remediate-findings` skill: `/andthen:remediate-findings {absolute_report_path}`. Remediation runs in the orchestrator (not a sub-agent) because it modifies code and must coordinate with orchestrator-owned state (`plan.md`, FIS checkboxes, `State` document). Known limitation: the orchestrator carries construction bias from having watched every story get built. Scope remediation narrowly to the gap report findings — do not re-evaluate or re-litigate decisions. If bias still leaks in, a later `exec-plan` run's fresh-context gap review is the intended second net. Escalate if issues persist after one remediation pass.

**Gate**: Final gap review complete

### Step 5: Final Verification

Run build, run tests, review cross-story integration. Include verification evidence: **Build** (exit code/status), **Tests** (pass/fail counts), **Linting/types** (error/warning counts).

**Gate**: Build, tests, integration pass

## FAILURE HANDLING

- **Story pipeline fails / non-green** → Stop-the-Line per `execution-discipline.md`. Iterate until green. A broken refactor is work to finish, not a blocker.
- **Escalate only on real external blockers** (see `execution-discipline.md`).
- **Final review fails** → one remediation pass (subjective-finding policy); escalate if issues persist
- **Dependent stories blocked** when predecessor fails
- **>50% of a phase fails** → pause this run and return a failure summary
- **Update the `State` document on failure** (see **Project Document Index**) via the `andthen:ops` skill: `update-state status "At Risk"` or `"Blocked"`

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
