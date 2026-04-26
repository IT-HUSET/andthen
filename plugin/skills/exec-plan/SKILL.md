---
description: Use when the user wants to execute a fully-specced implementation plan bundle. Runs a fixed pipeline per story (exec-spec + quick-review) and a final gap review on the whole plan. Requires a plan bundle where every story already has a FIS. Supports Agent Teams (--team) and sub-agents (portable fallback). Trigger on 'execute this plan', 'implement this plan', 'run the plan', 'execute with agents', 'run as team'.
argument-hint: "<path-to-plan-directory> [path-to-code-repo] [--team] [--worktree] [--auto|--headless]"
---

# Execute Plan


Execute ALL stories in a fully-specced plan bundle (from the `andthen:plan` skill) through a fixed pipeline: **exec-spec → quick-review** per story, then one final gap review (`review --mode gap`) on the whole plan.

**Requires a fully-specced plan bundle** — every story in `plan.md` must already have a FIS. If any story's `**FIS**` field is `–` or points at a non-existent file, stop and redirect to the `andthen:plan` skill to complete spec generation (`andthen:plan` is resumable — it only fills missing FIS). If no `prd.md` exists upstream, the full chain is `andthen:prd → andthen:plan → andthen:exec-plan`; `andthen:plan` will redirect to `andthen:prd` itself when its input lacks a PRD.

Supports two execution modes:
- **Sub-agents** (default) – parallel sub-agents per wave, sequential fallback when unavailable
- **Agent Teams** (`--team`) – team-based pipeline with optional worktree isolation for parallel execution


## VARIABLES

PLAN_DIR: $ARGUMENTS first positional argument (strip any `--team`, `--worktree`, `--auto`, `--headless` flag tokens before interpreting the remainder as positional args)
CODE_DIR: second positional argument _(optional – for multi-repo setups where plan and code live in different repos)_

### Optional Flags
- `--team` → USE_TEAM: force Agent Teams mode; error if unavailable
- `--worktree` → USE_WORKTREE: enable isolated git worktrees for parallel execution (team mode only; default: `false`)
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

Require `PLAN_DIR`. Stop if missing.

### Core Rules
- **Complete implementation**: all stories in plan must be implemented
- **Plan is source of truth** – follow phase ordering, dependencies, and parallel markers exactly
- **Plan must be fully specced** – every story's `**FIS**` field must point at an existing file. Fail fast otherwise; redirect to the `andthen:plan` skill
- **Fixed pipeline per story**: `exec-spec` → `quick-review`, then one final `review --mode gap` on the whole plan
- **Automation mode** (`--auto` / `--headless`) — never ask the user what to do next. Propagate `--auto` to nested `andthen:*` skill invocations that accept it (the `andthen:ops` skill is exempt — it is deterministic), suppress advisory prompts, and return deterministic status/artifact output for the external orchestrator. Stop with `BLOCKED:` (listing the minimum missing inputs, non-green gates that cannot be repaired within the policy, missing tools, or unsafe external actions) only for invalid inputs, unrepairable red gates, missing execution tools, unsafe external actions, or real external blockers.
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
- **(Team mode, worktree)** Wave N+1 worktrees must be created AFTER Wave N merges **and** any orchestrator-applied writes that land in `CODE_DIR` (deferred shared writes in single-repo, repair writes, phase transition writes) are committed to `CODE_DIR`'s `BASE_BRANCH`. A worktree branched off a stale base will stomp those writes when it merges back. (Multi-repo plan/state writes land in `PLAN_DIR`, not `CODE_DIR`'s `BASE_BRANCH`, so they are not at risk from this; only `CODE_DIR`-bound writes apply to this gate.)
- **(Team mode, worktree)** `plan.md` / `State` document writes must be deferred via `exec-spec`'s "Deferred Shared Writes" audit block — concurrent worktree merges cannot safely carry table-row updates to those files. The orchestrator constructs the actual writes post-merge from values it already knows (`STORY_ID`, `FIS_FILE_PATH`, `PLAN_FILE_PATH`, completion summary) and applies them on `BASE_BRANCH` in single-repo (`PLAN_DIR == CODE_DIR`), or in `PLAN_DIR` in multi-repo (`PLAN_DIR ≠ CODE_DIR`). Do not parse the audit block as a script.


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

**Pre-validate flag combinations**: `--worktree` requires `--team` (worktree isolation is a team-mode feature; sub-agent mode runs sequentially in the orchestrator's CWD and has no worktrees to merge). If `USE_WORKTREE=true` and `USE_TEAM=false`, stop. In default mode, inform the user that `--worktree` is only meaningful with `--team` and ask whether to proceed with `--team` added or drop `--worktree`. In `AUTO_MODE`, emit `BLOCKED: --worktree requires --team` and exit.

Check whether Agent Teams are available by verifying that team creation tools exist (e.g. `TeamCreate`).

- **`--team` AND available** → Team mode (Step 3T)
- **`--team` AND unavailable** → stop. In default mode, inform the user it requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`; in `AUTO_MODE`, emit `BLOCKED: Agent Teams unavailable (requires CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1)` and exit.
- **No `--team`** → Sub-agent mode (Step 3). Mention `--team` is available if the user wants team execution, unless `AUTO_MODE=true`.

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

**Wave-based execution**: W1 in parallel (via sub-agents), then W2, etc. Fall back to sequential in-orchestrator execution if sub-agents are unavailable or delegated execution stalls / returns partial / non-green.

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

When `AUTO_MODE=true`, append `--auto` to both skill invocations in the sub-agent prompt.

**Model assignment**: Use a capable coding model (`model: "sonnet"`, `gpt-5.3-codex`, or similar).

#### 3c. Verify Green, Confirm Writes Landed (**Gate**)

Run immediately after each story — not as a batch. Worker self-reports do not count.

**Green gate**:
- Build / compile clean for affected packages
- Targeted tests pass (full suite runs in Step 5)
- Lint / type-check clean for touched files
- No broken intermediate state (partial migration, half-refactored call sites, dead imports)

Fail → story stays `In Progress`. Apply Stop-the-Line per `execution-discipline.md`: repair locally, re-delegate (template below), or invoke the `andthen:triage` skill. Iterate until green.

Pass → run the **Writes-Landed Checklist** below. This is a structured re-read, not a glance. Outside this repair path and Post-Completion bookkeeping, the orchestrator does not write story-level status.

**Writes-Landed Checklist** (per story just completed):

- [ ] **FIS** — open the FIS at `{fis_path}`. Every task checkbox is `[x]`. Final Validation Checklist items are `[x]`. Success criteria are `[x]`.
- [ ] **Plan story row** — open `plan.md`. The Story Catalog row for `{story_id}` shows status `Done`.
- [ ] **Plan story section** — the story's section header field shows `**Status**: Done`. `**FIS**` field points at the correct path. Acceptance criteria checkboxes are all `[x]`.
- [ ] **State document** (if it exists per **Project Document Index**) — `{story_id}` is no longer in the Active Stories table.

Missing item → call the matching `andthen:ops update-*` once to repair, then re-read that item only. Persistent miss after one repair pass is Stop-the-Line — do not advance the wave on unverified status.

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

Define `AUTO_SUFFIX = " --auto"` when `AUTO_MODE=true`, else `AUTO_SUFFIX = ""`. Define `WORKTREE_SUFFIX = " --defer-shared-writes"` when `USE_WORKTREE=true`, else `WORKTREE_SUFFIX = ""` (this is the propagated form of `--worktree` — exec-spec's flag describes its own behavior: defer shared-file writes). Substitute `{AUTO_SUFFIX}` and `{WORKTREE_SUFFIX}` literally into each teammate system prompt before creating the team — do not rely on teammates to evaluate `AUTO_MODE` / `USE_WORKTREE` themselves; they have no access to those variables.

**Implementer prompt** – include in each implementer's system prompt:
- Only work on assigned `impl-*` tasks
- Per task: `cd {CODE_DIR}` → (worktree: `EnterWorktree "story-{task_id}"`) → `/andthen:exec-spec {fis_path}{AUTO_SUFFIX}{WORKTREE_SUFFIX}` → commit → (worktree: `ExitWorktree(keep)`) → mark done; report `exec-spec` Step 4a numbers (build, tests, lint/type-check)
- `exec-spec` Step 5b writes status. Do NOT call `andthen:ops update-plan`, `update-fis`, or `update-state` *beyond* what `exec-spec` does internally (and do not suppress its Step 5b writes)
- **Worktree mode (`{WORKTREE_SUFFIX}` non-empty)**: `exec-spec` skips `plan.md` and `State` document writes and emits a `## Deferred Shared Writes (worktree mode)` audit block (Story / Plan / FIS / Completion summary). Pass that block through to your report so the orchestrator can read the `Completion summary` line and audit what was deferred — the orchestrator already knows Story / Plan / FIS from its own plan parse and constructs / applies the writes post-merge itself. Constraints: (1) do not apply those writes yourself, (2) do not stage or commit `plan.md` or the `State` document inside the worktree branch — only code (and FIS) edits belong there. Shadow plan/state commits inside the worktree defeat the deferral and resurrect the merge-conflict failure mode this flag exists to prevent.
- Absolute FIS paths; escalate unresolvable issues

**Reviewer prompt** – include in each reviewer's system prompt:
- Role constraint: only work on assigned `review-*` tasks
- Per-task workflow: `cd {CODE_DIR}` → `/andthen:quick-review{AUTO_SUFFIX}` on the story's changes (code is on `{BASE_BRANCH}` after impl/merge) → mark task done
- Escalate unresolvable issues to orchestrator

#### Task Management

**Task naming**: `impl-{story_id}` / `review-{story_id}` (one impl task per story, one review task per story — each story has its own FIS). Round-robin assign; do not self-assign impl and review of the same story to the same agent.

**Dependencies** (sequential, `USE_WORKTREE=false`): each `impl-*` blocked by previous `review-*`. Parallel markers ignored.

**Dependencies** (worktree, `USE_WORKTREE=true`): current-wave `impl-*` unblocked; `review-*` blocked until wave merge; W2+ `impl-*` blocked by prior-wave merge completion.

#### Merge Wave _(worktree mode only)_

After all `impl-*` in the current wave complete, for each worktree branch in sequence:

1. **Merge** the worktree branch into `BASE_BRANCH` (`--no-ff`). Conflict handling: imports → take both; lock files → `--theirs` + reinstall; logic conflicts → spawn troubleshooter or escalate.
2. **Verify build** on `BASE_BRANCH` post-merge.
3. **Apply deferred shared writes for this story.** The implementer's report contains a `## Deferred Shared Writes (worktree mode)` audit block with `Story`, `Plan`, `FIS`, and `Completion summary` fields. **Do not parse it as a script** — use it as audit / summary source.

   **Value sources** — the orchestrator already holds the structural values from Step 1's plan parse, not from the audit block or the task name:
   - `STORY_ID` is the plan story identifier (e.g. `S03`), extracted from `plan.md` at parse time. The team task names (`impl-{STORY_ID}` / `review-{STORY_ID}`) embed the same value but are *not* the source of truth.
   - `FIS_FILE_PATH` and `PLAN_FILE_PATH` are likewise from Step 1.
   - `Completion summary` is the only field actually pulled from the audit block — extract by matching the line `^Completion summary:\s*(.+)$` and trimming the captured value.

   Construct and run the writes:
   - `andthen:ops update-plan {PLAN_FILE_PATH} {STORY_ID} Done` — sets Status, Story Catalog row, acceptance-criteria checkboxes.
   - `andthen:ops update-plan {PLAN_FILE_PATH} {STORY_ID} fis "{FIS_FILE_PATH}"` — only if the plan story row's FIS field is *unset* (empty / `–` / placeholder) or *stale* (path differs from `{FIS_FILE_PATH}` after path normalization).
   - `andthen:ops update-state active-story {STORY_ID} Done` — only if the `State` document exists.
   - `andthen:ops update-state note "{Completion summary}"` — use the summary line from the audit block; if the audit block is missing or its summary is empty, fall back to `"{STORY_ID}: completed (worktree merge)"` (the substituted `STORY_ID` is the bare plan ID like `S03`, not the team task name `impl-S03`). A missing audit block is **not** a Stop-the-Line — all required values are already in the orchestrator's hand; the writes still proceed. Log the missing block as a worker self-report drift signal for follow-up.

   This is the **primary** write path for `plan.md` and `State` document in worktree mode (not a repair).

4. **Commit the resulting writes in the repo where the files live**:
   - **Single-repo** (`PLAN_DIR == CODE_DIR`) — commit on `CODE_DIR`'s `BASE_BRANCH`. Subsequent worktree merges in this wave and Wave N+1 worktrees must include these commits (see GOTCHAS).
   - **Multi-repo** (`PLAN_DIR ≠ CODE_DIR`) — `plan.md` and the `State` document are **not** in `CODE_DIR`'s history. If `PLAN_DIR` is itself a git repo, commit there; otherwise the file edits stand on their own. `CODE_DIR`'s `BASE_BRANCH` is unaffected, so the Wave N+1 stale-base concern does not apply to plan/state files in multi-repo. (Code-side commits from the merge in step 1 still land on `CODE_DIR`'s `BASE_BRANCH` as usual.)

5. **Clean up worktree and branch** in `CODE_DIR` (orchestrator's CWD). The implementer exited with `ExitWorktree(keep)`, so the directory and branch are still on disk; `ExitWorktree(remove)` cannot be used cross-session, so drop to git. Substitute the actual story id for the `{task_id}` placeholder in every command below (story ids are alphanumeric/hyphen, no further shell escaping needed). **Precondition**: `pwd` must be `CODE_DIR` (the main checkout), not inside a `story-*` worktree — `git worktree remove` refuses to remove the worktree you are currently in.
   - Resolve the worktree path: `WORKTREE_PATH=$(git worktree list --porcelain | awk -v b="refs/heads/story-{task_id}" '/^worktree /{p=$2} $1=="branch" && $2==b {print p}')`.
   - **Empty resolution** — if `WORKTREE_PATH` is empty (the implementer crashed before `EnterWorktree` succeeded, or the directory was manually deleted): skip `git worktree remove`, run `git worktree prune` to clear any stale admin record, then `git branch -D story-{task_id} 2>/dev/null || true` (the branch may or may not exist). Continue to the next merge — this is recoverable, not Stop-the-Line.
   - **Dirty-tree check** — `git -C "$WORKTREE_PATH" status --porcelain` must be empty (the implementer committed inside `exec-spec`). If not, **Stop-the-Line** per FAILURE HANDLING: log path + branch in the failure summary, leave the worktree intact, and abort the wave — uncommitted work is not safe to discard.
   - `git worktree remove "$WORKTREE_PATH"` then `git branch -D story-{task_id}`. `-D` (not `-d`) because `-d` checks ancestry against the orchestrator's *current* HEAD, which may not be `BASE_BRANCH` if the orchestrator switched branches for a repair; the merge in step 1 already committed the work into `BASE_BRANCH`, so the branch ref is redundant either way.
   - Verify `git worktree list` no longer contains `story-{task_id}`. If it does, Stop-the-Line — a leftover will collide with `EnterWorktree` if the same story id reappears.

   Then **unblock** the matching review task.

Run all five steps for one worktree before starting the next — sequential ordering keeps each merge based on a tip that already includes the prior story's deferred writes (single-repo) or sees the latest plan/state file content (multi-repo).

#### Status Updates (**Gate**)

Same green-gate discipline as Step 3c, then run the **Writes-Landed Checklist** (defined in Step 3c) per story.

Source of truth for the checklist depends on mode:
- **Worktree** — primary writes come from the Merge Wave step's "apply deferred shared writes" substep, not from inside the worktree branch. Run the checklist after the deferred writes are applied and committed (single-repo: read from `BASE_BRANCH`; multi-repo: read directly from `PLAN_DIR`). Any miss after that is a real loss → repair via the matching `andthen:ops update-*` once.
- **No worktree** — `exec-spec` Step 5b writes status in-place. Run the checklist as in Step 3c; one-shot repair on miss.

Additionally verify the **Plan Acceptance Gate** before accepting `Done`: each acceptance criterion demonstrably satisfied, scope notes present when the FIS narrowed scope.

Move to the next phase only after the current phase fully passes the checklist for every story.

**Green-gate timing**:
- **Worktree** — per-worktree build/tests pre-merge; orchestrator gate on `BASE_BRANCH` post-merge. Stop-the-Line on `BASE_BRANCH`, not inside a worktree.
- **No worktree** — gate after each `impl-*`, before the matching `review-*` unblocks.

**Take-over topology** (orchestrator repair):
- **Worktree, pre-merge** — re-enter the live worktree using `EnterWorktree`'s **path form** (`EnterWorktree path: <resolved-worktree-path>`), not the name form: the orchestrator did not create the worktree itself, and the name form only resolves session-created worktrees. Per `EnterWorktree`'s contract, path-entered worktrees cannot be removed via `ExitWorktree(remove)` — fix → re-verify → commit → exit with `ExitWorktree(keep)` → merge in step 1; cleanup still runs through bash `git worktree remove` in Merge Wave step 5, never `ExitWorktree(remove)`.
- **Worktree post-merge** or **no worktree** — repair on `BASE_BRANCH` in orchestrator's CWD.

#### Monitoring

Print progress updates — the user cannot see agent activity. Report task creation/assignment, agent starts/completions, wave completions, merge results, phase summaries, and failures.

After all phases, run **Final Worktree Teardown** in `CODE_DIR` before shutting down the team. `git worktree prune` alone does **not** clean anything — it only purges admin records for worktrees whose directories are already gone. Live `story-*` worktrees from failed waves, abandoned stories, or earlier runs persist until removed explicitly. **Precondition**: `pwd` must be `CODE_DIR` (the main checkout), not inside a `story-*` worktree.

Substitute the literal `BASE_BRANCH` value resolved at run start (e.g. `main`) into the merge-base test below — the orchestrator runs bash one-shot, so a `$BASE_BRANCH` shell variable is not in scope.

1. **Inventory leftovers** from `git worktree list --porcelain`. Walk the output paragraph-by-paragraph (records are blank-line separated). For each record, capture `WORKTREE_PATH` (from `^worktree <path>`) and `WORKTREE_BRANCH` (from `^branch refs/heads/<name>`, strip the `refs/heads/` prefix). A record is a leftover if **either** holds:
   - `WORKTREE_BRANCH` matches `story-*`, **or**
   - the record has no `branch` line (detached) **and** `WORKTREE_PATH` matches `*/.claude/worktrees/story-*` — porcelain output emits `detached` instead of a branch line for detached worktrees, so a branch-only filter would silently miss these.
2. **For each leftover**, classify by merge state and act:
   - **Unmerged** — `git merge-base --is-ancestor <WORKTREE_BRANCH> <BASE_BRANCH>` returns non-zero, or the worktree is detached and has no branch to test: the work is the only artifact. **Do not auto-discard.** Log `WORKTREE_PATH` and `WORKTREE_BRANCH` in the failure summary, leave the worktree intact, and skip.
   - **Merged** — `git worktree remove --force "$WORKTREE_PATH"` then (if `WORKTREE_BRANCH` is non-empty) `git branch -D "$WORKTREE_BRANCH"`. `--force` is correct here: a merged branch's working-tree edits are by definition redundant with `BASE_BRANCH`, and a leftover may still have stray scratch files that block bare `remove`.
3. `git worktree prune` (hygiene — clears any admin records left from manual filesystem deletes; not the primary mechanism).
4. **Verify**: `git worktree list` shows only the main checkout, pre-existing non-`story-*` user worktrees, and any `story-*` worktrees explicitly preserved as unmerged in step 2 (those are intentional, not leftovers). Anything else is Stop-the-Line.
5. Shutdown teammates, delete team.

Final Worktree Teardown runs whether the run completed successfully or failed (see FAILURE HANDLING) — skipping it on failure is the main source of accumulated leftovers across runs.

**Gate**: All phases complete.


### Step 4: Final Review

Spawn a `general-purpose` sub-agent whose prompt runs the `andthen:review` skill in `--mode gap` on the whole plan. Fresh context is load-bearing here — by this step the orchestrator has watched every story get built and is biased by construction context. A sub-agent sees only the plan and the final code, which is what the gap verdict should reflect.

**Model**: Use a strong reasoning model (`model: "opus"`, `gpt-5.4`, or similar). Gap review runs inline in the sub-agent's own context (per `lens-gap.md` — the gap lens does not delegate), so the sub-agent's model IS the reviewing model. Whole-plan gap review is cross-cutting (story interactions, acceptance-criteria coverage, requirements drift) rather than routine pattern-matching, which justifies the stronger tier over the sonnet default.

Resolve `PLAN_DIR` and `CODE_DIR` to absolute paths (`PLAN_DIR_ABS`, `CODE_DIR_ABS`) before substituting into the prompt — relative paths break in multi-repo setups where the sub-agent's CWD may match neither repo.

Before composing the prompt, set `AUTO_SUFFIX = " --auto"` when `AUTO_MODE=true`, else `AUTO_SUFFIX = ""`. Substitute `{AUTO_SUFFIX}` literally into the prompt below.

**Sub-agent prompt**:
```
Run /andthen:review --mode gap {PLAN_DIR_ABS}/plan.md{AUTO_SUFFIX} on the whole plan.

Implementation lives in: {CODE_DIR_ABS}

Do NOT pass --inline-findings — the final gap gate must write a report file so remediate-findings can consume it.

Report back:
1. The verdict (PASS/FAIL) from the canonical gap verdict table
2. The absolute path to the written report file
```

Verify the sub-agent returned both a verdict and a path that resolves to a readable file. If either is missing, stop — do not silently retry; the downstream remediation step depends on a valid report artifact. In `AUTO_MODE`, emit `BLOCKED: final gap review returned malformed output (missing verdict or report path)` before exiting.

If the verdict is FAIL, invoke the `andthen:remediate-findings` skill: `/andthen:remediate-findings {absolute_report_path}` (append `--auto` when `AUTO_MODE=true`). Remediation runs in the orchestrator (not a sub-agent) because it modifies code and must coordinate with orchestrator-owned state (`plan.md`, FIS checkboxes, `State` document). Known limitation: the orchestrator carries construction bias from having watched every story get built. Scope remediation narrowly to the gap report findings — do not re-evaluate or re-litigate decisions. If bias still leaks in, a later `exec-plan` run's fresh-context gap review is the intended second net. Escalate if issues persist after one remediation pass.

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
- **Always run Final Worktree Teardown before exiting**, including failure exits (Stop-the-Line escalation, `>50%` phase failure, final review unresolvable). Use the same merged/unmerged classification as the success path — merged `story-*` worktrees and branches are removed; unmerged ones are preserved (their content is the only record of the in-flight work) and listed in the failure summary so the user can decide whether to resume or discard.

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
