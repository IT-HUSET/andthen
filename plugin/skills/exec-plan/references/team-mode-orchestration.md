# Team-Mode Orchestration

Loaded when `--team` is active (Step 3T). Single source of truth for team-mode behavior; default-mode does not load it.

## Contents
- Team Setup
- Implementer Prompt
- Reviewer Prompt
- Task Management
- Merge Wave
- Status Updates Gate
- Multi-Repo Rules
- Monitoring
- Final Worktree Teardown


## Team Setup

Create team `"plan-pipeline"` with pre-assigned tasks. Size: 1 implementer (≤4 stories), 2 (5–10), 3 (11+). Add 1–2 reviewers for `quick-review`. Use a capable coding model for all teammates.

Define `AUTO_SUFFIX = " --auto"` when `AUTO_MODE=true`, else `""`. Define `WORKTREE_SUFFIX = " --defer-shared-writes"` when `USE_WORKTREE=true`, else `""` (propagated form of `--worktree`; exec-spec's flag describes its own behavior).

**Pre-create worktrees in bash** _(when `USE_WORKTREE=true`)_. Harness isolation is unreliable under `team_name`; every worktree is created by the orchestrator before TeamCreate. Per `impl-*`:

```
bash ${CLAUDE_SKILL_DIR}/scripts/create-worktree.sh {STORY_ID} {BASE_BRANCH} {CODE_DIR_ABS}
```

Capture `WORKTREE_PATH=` from stdout into `{WORKTREE_PATH_ABS}`. Non-zero exit → Stop-the-Line. Pre-existing branch/directory → run `teardown-worktrees.sh` first.

**Substitution scope** – at team creation, replace in every teammate system prompt: `{AUTO_SUFFIX}`, `{WORKTREE_SUFFIX}`, `{CODE_DIR_ABS}`, `{BASE_BRANCH}`. Per-task placeholders for implementers – `{STORY_ID}` (bare plan id, e.g. `S03`; derived by the orchestrator from the task's story binding), `{fis_path}`, and (under `USE_WORKTREE=true`) `{WORKTREE_PATH_ABS}` – filled at TeamCreate. Reviewer derives `STORY_ID` from its task name at runtime. Scripts always receive bare `{STORY_ID}`, never the team task name. Teammates have no access to orchestrator-side variables; anything not substituted is derived at runtime.


## Implementer Prompt

Apply the **Worker Contract** from `exec-plan/SKILL.md` Step 3b. The team Implementer runs only the `exec-spec` half of the canonical Worker Prompt – the `quick-review` half is the Reviewer's task.

Placeholders pre-substituted by the orchestrator at TeamCreate: `{AUTO_SUFFIX}`, `{WORKTREE_SUFFIX}`, `{CODE_DIR_ABS}`, `{BASE_BRANCH}`. Per-task: `{STORY_ID}`, `{fis_path}`, and (worktree mode) `{WORKTREE_PATH_ABS}`.

Per `impl-*` task assigned to you (orchestrator pre-assigns owners – work only your assigned tasks, no shared-queue claiming):
- `cd {CODE_DIR_ABS}` (worktree mode: `cd {WORKTREE_PATH_ABS}` instead).
- **Worktree mode** (`{WORKTREE_PATH_ABS}` non-empty), as first action after `cd`: `bash ${CLAUDE_SKILL_DIR}/scripts/verify-in-worktree.sh {STORY_ID} {WORKTREE_PATH_ABS}`. Anything other than `VERIFY_OK` → STOP, report `VERIFY_FAIL:<reason>`, fail the task. Subsequent operations use absolute paths only (relative paths silently leak to the main checkout). Pass the `## Deferred Shared Writes` audit block through to your report; do NOT stage `plan.json` or the State document inside the worktree branch – the `andthen:merge-resolve` skill's G2 guard fails the story.
- `/andthen:exec-spec {fis_path}{AUTO_SUFFIX}{WORKTREE_SUFFIX}`.
- On success: report `exec-spec` Step 4a numbers (build, tests, lint/type-check, format). Orchestrator handles squash-merge and cleanup.
- On `BLOCKED:` or Failed Story Report: do not mark done; preserve the worktree and report details.
- Do not call `andthen:ops update-*` yourself – `exec-spec` Step 5b owns those (Worker Contract).

Escalate unresolvable issues. Absolute FIS paths.


## Reviewer Prompt

Apply the **Worker Contract** from `exec-plan/SKILL.md` Step 3b. The team Reviewer runs only the `quick-review` half of the canonical Worker Prompt.

Per `review-*` task assigned to you (orchestrator pre-assigns owners; `impl-Sxx` and `review-Sxx` are never assigned to the same teammate, so self-review cannot occur):
- Derive story id by stripping `review-` from your task name (`review-S03` → `S03`).
- `cd {CODE_DIR_ABS}`.
- **Resolve the review commit SHA** – the change set is committed in both modes, so `git diff` is empty; `quick-review`'s `commit <sha>` FOCUS form provides the change set:
  - **Worktree mode**: create an unreferenced review snapshot for the full branch diff: `git commit-tree "story-<story-id>^{tree}" -p "$(git merge-base {BASE_BRANCH} story-<story-id>)" -m "review snapshot <story-id>"`. Empty result → escalate.
  - **No worktree mode**: `git rev-parse HEAD`. Task-dependency ordering (`impl-<story-id>` completes before `review-<story-id>`) guarantees the implementer's commit is at HEAD.
- **Substitute `<story-id>` and `<hex-sha>` as literals** (slash-command lines are not bash; `$VAR` and `<placeholder>` reach `quick-review` unexpanded). Invoke: `/andthen:quick-review story <story-id> commit <hex-sha>{AUTO_SUFFIX}`.
- Accepted findings → report to orchestrator, do not mark done. Else mark done.
- Do not call `andthen:ops update-*` yourself (Worker Contract).

Escalate unresolvable issues.


## Task Management

**Naming**: `impl-{story_id}` / `review-{story_id}` (one impl + one review per story; one FIS per story).

**Pre-assignment** (no self-claim): at TeamCreate, the orchestrator round-robin distributes `impl-*` across implementer teammates and `review-*` across reviewer teammates, setting the `owner` field on every task. Same-task races are prevented by ownership, and self-review is prevented at assignment time – the same teammate is never assigned both `impl-Sxx` and `review-Sxx`. Teammates work only their assigned tasks; no claim discipline needed.

**Dependencies** (sequential, `USE_WORKTREE=false`): each `impl-*` blocked by the previous `review-*`. `AUTO_MODE` may unblock the next independent story after recording a failure. Parallel markers ignored.

**Dependencies** (worktree, `USE_WORKTREE=true`): current-wave `impl-*` unblocked; each `review-*` blocked until matching `impl-*` succeeds; merge waits for review pass or recorded failure; W2+ `impl-*` blocked until prior wave's merged successes + recorded failures land.

**Failure containment**: a failed `impl-*` blocks only its own `review-*` and downstream stories. `AUTO_MODE`: record failure, preserve worktree/branch, skip dependents, continue independent work. No-worktree: prove shared checkout clean before unblocking another `impl-*`.


## Merge Wave _(worktree mode only)_

After current-wave `impl-*` and `review-*` succeed or are recorded failed, merge only reviewed-successful implementations. Before each merge, take `{WORKTREE_PATH_ABS}` from the `create-worktree.sh` capture (fall back to step 5's `git worktree list --porcelain` lookup only after orchestrator restart). Implementer `BLOCKED:` / Failed Story Report, quick-review accepted **Fix-routed** findings, or dirty worktree → record failed story; no merge, no deferred writes, no cleanup for that story. Accepted **Note-routed** findings are recorded as the story's surfaced notes (Step 6 rollup), not a merge blocker.

For each successful worktree branch in sequence:

1. **Invoke `/andthen:merge-resolve`** with the story's parameters.

   First, extract the implementer's `Completion summary` from the audit block (regex `^Completion summary:\s*(.+)$`, trimmed; fallback `"{STORY_ID}: completed (worktree merge)"`) and write it to `.agent_temp/merge-summary-{STORY_ID}.txt` so prose never reaches the shell argument vector. Reuse this `SUMMARY` in step 3's `update-state note`.

   ```
   /andthen:merge-resolve {STORY_ID} {BASE_BRANCH} {WORKTREE_PATH_ABS} .agent_temp/merge-summary-{STORY_ID}.txt \
     --guard-path {PLAN_FILE_PATH} \
     [--guard-path {STATE_FILE_PATH}]   # only when the State document exists per Project Document Index
   ```

   Multi-repo (`PLAN_DIR ≠ CODE_DIR`): pass `--guard-path` unchanged – the skill's underlying script drops guard paths that resolve outside `CODE_DIR` and emits a `GUARD_SKIPPED:G2:<path>` line on stderr (informational; multi-repo plan/state files cannot leak into `CODE_DIR`'s history).

   Branch on `merge_resolve.outcome`:

   - `resolved` → proceed to step 2.
   - `failed` with `error_message` starting `precondition:` → Stop-the-Line. CWD drifted off `BASE_BRANCH` or main checkout is dirty / wrong repo. Investigate before any further merges.
   - `failed` with `error_message` starting `guard:` → record `FAILED:{error_message}`, preserve worktree (the skill wrote `.andthen-fail-reason` so teardown classifies it as `UNMERGED:<branch>:<reason>`), continue with the next story.
   - `failed` with `error_message` starting `squash:` → record `FAILED:{error_message}`, preserve worktree, continue. The skill has already rolled back the partial squash on the main checkout.
   - `failed` with `error_message` starting `logic_conflict:` or `verification:` → record `FAILED:{error_message}` with `conflicted_files` and `resolution_summary` from the skill output. If the skill wrote `.agent_temp/merge-resolve-{STORY_ID}.patch`, include the path so the user can replay. Preserve worktree. Continue. The skill has rolled back the partial squash on the main checkout.
   - `failed` with `error_message` starting `commit:` → record `FAILED:{error_message}`, preserve worktree, continue. The skill has rolled back the staged squash.
   - `cancelled` → record `FAILED:cancelled` (harness STOP between steps), preserve worktree, continue. If cancellation happened after conflict detection, the skill has rolled back the partial squash on the main checkout.

2. **Verify build** on `{BASE_BRANCH}` post-commit.

3. **Apply deferred shared writes** (this is the **primary** write path for `plan.json` / State in worktree mode, not a repair). `STORY_ID`, `FIS_FILE_PATH`, and `PLAN_FILE_PATH` come from Step 1's plan parse; the audit block contributes only `Completion summary` (already captured into `SUMMARY` above). Run:

   - `andthen:ops update-plan {PLAN_FILE_PATH} {STORY_ID} done`
   - `andthen:ops update-plan-fis {PLAN_FILE_PATH} {STORY_ID} {FIS_FILE_PATH}` – only when the story's `fis` is `null` or differs from `{FIS_FILE_PATH}` after path normalization.
   - `andthen:ops update-state active-story {STORY_ID} Done` – only if the State document exists.
   - `andthen:ops update-state note "{SUMMARY}"`.

   Missing audit block is not Stop-the-Line; log the miss and proceed with the fallback `SUMMARY` already in hand.

4. **Commit the resulting writes in the repo where the files live**:
   - **Single-repo** (`PLAN_DIR == CODE_DIR`) – commit on `CODE_DIR`'s `{BASE_BRANCH}`. See Worktree Merge Ordering below.
   - **Multi-repo** (`PLAN_DIR ≠ CODE_DIR`) – `plan.json` and the State document live outside `CODE_DIR`'s history. If `PLAN_DIR` is itself a git repo, commit there; otherwise the file edits stand on their own. `CODE_DIR`'s `{BASE_BRANCH}` is unaffected.

5. **Clean up worktree and branch** in `CODE_DIR` (orchestrator's CWD). **Precondition**: `pwd` must be `CODE_DIR`, not inside a `story-*` worktree (`git worktree remove` refuses to remove the current worktree). Use `{WORKTREE_PATH_ABS}` captured at create time; fall back to lookup only on orchestrator restart.
   - Captured-path fallback: `WORKTREE_PATH=$(git worktree list --porcelain | awk -v b="refs/heads/story-{STORY_ID}" '/^worktree /{p=$2} $1=="branch" && $2==b {print p}')`.
   - Empty `$WORKTREE_PATH` (create aborted, or directory manually deleted) → skip `git worktree remove`, run `git worktree prune`, then `git branch -D story-{STORY_ID} 2>/dev/null || true`. Continue. Not Stop-the-Line.
   - `git worktree remove "$WORKTREE_PATH"` then `git branch -D story-{STORY_ID}`. `-D` (not `-d`) is required: squash commits have different SHA + tree-parents than the side branch's tip, so `-d`'s "fully-merged" check always refuses after squash. The squash commit on `{BASE_BRANCH}` already carries all the work.
   - Verify `git worktree list` no longer contains `story-{STORY_ID}`. Leftover → Stop-the-Line; `create-worktree.sh` would collide on the same story id.

Run all five steps for one worktree before starting the next – sequential ordering keeps each merge based on a tip that includes the prior story's deferred writes.


### Worktree Merge Ordering

**No stale-base merges.** A Wave N+1 worktree branched off an outdated `{BASE_BRANCH}` stomps deferred writes when it merges back. Wave N+1 worktrees branch only after every Wave N squash-merge, per-story review, and `CODE_DIR`-bound write (single-repo deferred writes, repair writes, phase transitions) is committed to `{BASE_BRANCH}`. Multi-repo plan/state writes land in `PLAN_DIR` and are not subject to this gate.

**Deferred-write commits land before the next wave's worktrees are created.** Single-repo: the Merge Wave step 4 commit must reach `{BASE_BRANCH}` before any Wave N+1 worktree exists. Do not parallelize.

Worktree creation is bash-only (`create-worktree.sh`). Never `EnterWorktree` / `ExitWorktree` / `Agent({isolation:"worktree"})`.


## Status Updates Gate

Same green-gate discipline as Step 3c, then run the **Writes-Landed Checklist** per story.

Checklist source-of-truth by mode:
- **Worktree** – primary writes come from the Merge Wave post-review "apply deferred shared writes" substep, not the worktree branch. Run the checklist after deferred writes commit (single-repo: from `{BASE_BRANCH}`; multi-repo: from `PLAN_DIR`). Miss → one-shot repair via `andthen:ops update-*`.
- **No worktree** – `exec-spec` Step 5b writes status in-place; same as Step 3c; one-shot repair on miss.

Also verify the **Plan Acceptance Gate** before `Done`: every FIS scenario/criteria checkbox is `[x]` (Final Validation Checklist when present), implementation observations present when the FIS narrowed scope, `review-*` task completed without accepted **Fix-routed** findings (accepted Note-routed findings are recorded as surfaced notes, not a gate).

Pass → record in the ledger's `completed` list.

Advance to the next phase only after every current-phase story is verified green or recorded failed/skipped.

**Green-gate timing**:
- **Worktree** – per-worktree build/tests pre-merge; orchestrator gate on `{BASE_BRANCH}` post-merge. Stop-the-Line on `{BASE_BRANCH}`, not inside a worktree.
- **No worktree** – gate after each `impl-*`, before the matching `review-*` unblocks.

**Take-over topology** (orchestrator repair):
- **Worktree, pre-merge** – `cd {WORKTREE_PATH_ABS}`, apply fix, re-run `Key Dev Commands` verification, `git -C {WORKTREE_PATH_ABS} commit -am "<repair summary>"`. Never `EnterWorktree` / `ExitWorktree`. Merge Wave continues. `AUTO_MODE` permits this only for bounded fix-forward; otherwise preserve and record failure.
- **Worktree post-merge** or **no worktree** – repair on `{BASE_BRANCH}` in orchestrator's CWD.


## Multi-Repo Rules _(CODE_DIR ≠ PLAN_DIR's git root)_
- All git operations target `CODE_DIR` – never the plan repo.
- `create-worktree.sh` receives `CODE_DIR_ABS` as its third argument so worktrees land under `CODE_DIR/.claude/worktrees/`.
- FIS paths passed to agents are **absolute**.
- Plan repo is **read-only for git operations** – only the orchestrator updates `plan.json`.


## Monitoring

Print progress updates – the user cannot see agent activity. Report: task creation/assignment, agent starts/completions, wave completions, merge results, phase summaries, failures.


## Final Worktree Teardown

Runs after all phases complete and before team shutdown. Also runs on failure exits (Stop-the-Line, >50% phase failure, final review unresolvable). See `exec-plan/SKILL.md` FAILURE HANDLING.

**Precondition**: `pwd` is `CODE_DIR` (main checkout), not inside a `story-*` worktree.

Invoke:
```
bash ${CLAUDE_SKILL_DIR}/scripts/teardown-worktrees.sh {BASE_BRANCH}
```

`git worktree prune` alone only purges admin records for already-gone directories. Live `story-*` worktrees persist until removed explicitly.

**Stdout consumption**: each line classifies one leftover worktree. `MERGED:<branch>` was cleaned automatically; `UNMERGED:<branch>[:<reason>]` is preserved for the user. Other prefixes (`MERGED_DIRTY:`, `MERGED_INDETERMINATE:`, `DETACHED:`) are also preserved – log them as informational diagnostics, no special handling.

**Non-zero exit** → Stop-the-Line. Empty stdout (exit 0) → no action.

**Post-teardown verify**: `git worktree list` shows only main checkout, pre-existing non-`story-*` worktrees, and explicitly preserved `story-*` ones. Anything else is Stop-the-Line.

After teardown: shutdown teammates, delete team.
