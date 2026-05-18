# Team-Mode Orchestration

Loaded when `--team` is active (Step 3T). Covers team setup, implementer/reviewer prompts, task management, merge wave, status updates gate, monitoring, Final Worktree Teardown.

Single source of truth for team-mode behavior. Default-mode (no `--team`) does not load this.


## Team Setup

Create team `"plan-pipeline"` with pre-assigned tasks. Size: 1 implementer (≤4 stories), 2 (5–10), 3 (11+). Add 1–2 reviewers for `quick-review`. Use a capable coding model for all teammates.

Define `AUTO_SUFFIX = " --auto"` when `AUTO_MODE=true`, else `""`. Define `WORKTREE_SUFFIX = " --defer-shared-writes"` when `USE_WORKTREE=true`, else `""` (propagated form of `--worktree`; exec-spec's flag describes its own behavior).

**Pre-create-and-verify isolation** _(when `USE_WORKTREE=true`)_. Harness isolation is unreliable under `team_name` – every worktree is created via bash before TeamCreate; isolation is enforced by the implementer's first-action verify gate + Merge Wave guards G1/G2/G3, never by `isolation: "worktree"` or `EnterWorktree`. Per `impl-*`:

```
bash ${CLAUDE_SKILL_DIR}/scripts/create-worktree.sh {STORY_ID} {BASE_BRANCH} {CODE_DIR_ABS}
```

Capture `WORKTREE_PATH=` from stdout into `{WORKTREE_PATH_ABS}`. Non-zero exit → Stop-the-Line. Pre-existing branch/directory → run `teardown-worktrees.sh` first.

**Substitution scope** – at team creation, replace in every teammate system prompt: `{AUTO_SUFFIX}`, `{WORKTREE_SUFFIX}`, `{CODE_DIR_ABS}`, `{BASE_BRANCH}`. Per-task placeholders for implementers – `{STORY_ID}` (bare plan id, e.g. `S03`; derived by the orchestrator from the task's story binding, not by stripping the `impl-` prefix), `{fis_path}`, and (under `USE_WORKTREE=true`) `{WORKTREE_PATH_ABS}` – filled at TeamCreate. Reviewer derives `STORY_ID` from its task name at runtime. Scripts (`create-worktree.sh`, `verify-in-worktree.sh`, `merge-worktree.sh`) always receive bare `{STORY_ID}`, never the team task name. Teammates have no access to orchestrator-side variables; anything not substituted is derived at runtime.


## Implementer Prompt

Substitute the canonical Per-Story Worker Prompt block (`exec-plan/SKILL.md` bottom) with `{MODE}=team`:
- `{WORKTREE_PATH_ABS}`: absolute path from `create-worktree.sh` (worktree mode only)
- `{AUTO_SUFFIX}` / `{WORKTREE_SUFFIX}`: pre-substituted per Team Setup

Include in each implementer's system prompt:
- **Inbox-STOP first** (every turn, before anything): scan messages from the lead. `STOP` / `ABORT` / `CANCEL` → halt, report back, do not start or resume. Mid-turn interrupt is unavailable; this is the only sync point.
- **Self-review prevention** (claim-time): only claim `impl-*`. Never claim `review-Sxx` after completing `impl-Sxx`.
- **Per task, worktree mode** (`{WORKTREE_PATH_ABS}` non-empty) – step 1 is the durable restatement of `{WORKTREE_PRELUDE}` (defined in `exec-plan/SKILL.md` → Per-Story Worker Prompt). Edit both together:
  1. **HARD GATE – first action after inbox check**: `cd {WORKTREE_PATH_ABS}` then `bash ${CLAUDE_SKILL_DIR}/scripts/verify-in-worktree.sh {STORY_ID} {WORKTREE_PATH_ABS}`. Anything other than `VERIFY_OK` → STOP. Do not Read/Edit/Write/Glob/Grep/bash; report `VERIFY_FAIL:<reason>` and fail the task.
  2. **Absolute paths only** for every Read/Edit/Glob/Grep/cd/shell. Relative paths resolve against the team agent's project root (main checkout), silently leaking edits.
  3. `/andthen:exec-spec {fis_path}{AUTO_SUFFIX}{WORKTREE_SUFFIX}`.
  4. **Post-impl HARD GATE – before reporting done**: re-run `verify-in-worktree.sh` AND `git -C {CODE_DIR_ABS} status --porcelain`. Anything other than `VERIFY_OK` + empty porcelain → report `LEAK_DETECTED:<reason>` or `VERIFY_FAIL:<reason>` and fail. Closes the verify→exec-spec→report window.
  5. On success: report `exec-spec` Step 4a numbers (build, tests, lint/type-check, format). Do NOT call `EnterWorktree` / `ExitWorktree` – orchestrator handles squash-merge and cleanup.
- **Per task, no-worktree mode** (`{WORKTREE_PATH_ABS}` empty): `cd {CODE_DIR_ABS}` → `/andthen:exec-spec {fis_path}{AUTO_SUFFIX}{WORKTREE_SUFFIX}`. Inbox-STOP and self-review still apply; worktree HARD GATEs do not.
- **`{WORKTREE_SUFFIX}` non-empty (deferred shared writes)**: `exec-spec` skips `plan.json` / State writes and emits a `## Deferred Shared Writes` audit block. Pass it through to your report. Do NOT stage/commit `plan.json` or State inside the worktree branch – guard G2 fails the story.
- `exec-spec` `BLOCKED:` or Failed Story Report → do not mark done; preserve the worktree and report details.
- Absolute FIS paths. Escalate unresolvable issues.
- Do not call `andthen:ops update-*` – `exec-spec` Step 5b owns those.


## Reviewer Prompt

Substitute the canonical Per-Story Worker Prompt block with `{MODE}=team` and reviewer-specific overrides.

Include in each reviewer's system prompt:
- **Inbox-STOP first** (every turn): same protocol as implementer.
- **Self-review prevention** (claim-time): only claim `review-*`. Never claim `review-Sxx` after completing `impl-Sxx` – self-review collapses impl/review separation and is Stop-the-Line if it lands.
- Role: only `review-*` tasks. `{CODE_DIR_ABS}`, `{BASE_BRANCH}`, `{AUTO_SUFFIX}` pre-substituted. Derive story id by stripping `review-` from your task name (`review-S03` → `S03`).
- **Per-task workflow**:
  1. `cd {CODE_DIR_ABS}`.
  2. **Resolve review commit SHA** – the change set is committed in both modes, so `git diff` is empty; `quick-review`'s `commit <sha>` FOCUS form provides the change set:
     - **Worktree mode**: create an unreferenced review snapshot for the full branch diff: `git commit-tree "story-<story-id>^{tree}" -p "$(git merge-base {BASE_BRANCH} story-<story-id>)" -m "review snapshot <story-id>"`. Empty result → escalate.
     - **No worktree mode**: `git rev-parse HEAD`. Task-dependency ordering (`impl-<story-id>` completes before `review-<story-id>`) guarantees the implementer's commit is at HEAD.
  3. **Substitute `<story-id>` and `<hex-sha>` as literals** (slash-command lines are not bash; `$VAR` and `<placeholder>` reach `quick-review` unexpanded). Invoke: `/andthen:quick-review story <story-id> commit <hex-sha>{AUTO_SUFFIX}`. The `commit <sha>` FOCUS form is recognized by quick-review's priority-1 scope rule.
  4. Accepted findings → report to orchestrator, do not mark done. Else mark done.
- Escalate unresolvable issues.


## Task Management

**Naming**: `impl-{story_id}` / `review-{story_id}` (one impl + one review per story; one FIS per story). Teammates self-claim unblocked tasks; runtime prevents same-task races. **Self-review prevention is teammate-side** (see prompts): `impl-Sxx` completer must not claim `review-Sxx`.

**Dependencies** (sequential, `USE_WORKTREE=false`): each `impl-*` blocked by the previous `review-*`. `AUTO_MODE` may unblock the next independent story after recording a failure. Parallel markers ignored.

**Dependencies** (worktree, `USE_WORKTREE=true`): current-wave `impl-*` unblocked; each `review-*` blocked until matching `impl-*` succeeds AND the per-wave **main-checkout audit** passes; merge waits for review pass or recorded failure; W2+ `impl-*` blocked until prior wave's merged successes + recorded failures land.

**Review-blocking mechanism**: at TeamCreate, mark `review-Sxx` as `blockedBy: ["impl-Sxx", "audit-W<n>"]`. `audit-W<n>` is a synthetic orchestrator-owned task representing the wave's main-checkout audit; the orchestrator self-claims/completes it only after a successful audit. Without this synthetic blocker, a fast first impl finish would let `review-S01` start before the audit fires; a subsequent audit failure would leave a stale "review passed" verdict.

**Per-wave main-checkout audit** _(worktree mode; once after all wave `impl-*` complete or fail, before unblocking any `review-*`)_: `git -C {CODE_DIR_ABS} status --porcelain` must be empty. Non-empty → at least one teammate bypassed the verify gate and leaked edits. Do NOT unblock reviews. Record every completed `impl-*` in this wave as `FAILED:main-checkout-leak` with porcelain output as evidence, preserve all worktrees, proceed to FAILURE HANDLING. Never `git restore` / `git checkout .` here – the leaked files are forensic evidence.

**Failure containment**: a failed `impl-*` blocks only its own `review-*` and downstream stories. `AUTO_MODE`: record failure, preserve worktree/branch, skip dependents, continue independent work. No-worktree: prove shared checkout clean before unblocking another `impl-*`.


## Merge Wave _(worktree mode only)_

After current-wave `impl-*` and `review-*` succeed or are recorded failed, merge only reviewed-successful implementations. Before merging, take `{WORKTREE_PATH_ABS}` from the `create-worktree.sh` capture (fall back to step 5's `git worktree list --porcelain` awk lookup only after orchestrator restart) and run `git -C "{WORKTREE_PATH_ABS}" status --porcelain`. Implementer `BLOCKED:` / Failed Story Report, quick-review accepted findings, or dirty worktree → record failed story; no merge, no deferred writes, no cleanup for that story.

For each successful worktree branch in sequence:

1. **Squash-merge via `merge-worktree.sh`**. Extract `SUMMARY` from the implementer's audit block (`^Completion summary:\s*(.+)$`, trimmed; fallback `"{STORY_ID}: completed (worktree merge)"`). Write to `.agent_temp/merge-summary-{STORY_ID}.txt` so prose never reaches the shell argument vector. Reuse `SUMMARY` in step 3's `update-state note`. Invoke:

   ```
   bash ${CLAUDE_SKILL_DIR}/scripts/merge-worktree.sh {STORY_ID} {BASE_BRANCH} {WORKTREE_PATH_ABS} .agent_temp/merge-summary-{STORY_ID}.txt \
     --guard-path {PLAN_FILE_PATH} \
     [--guard-path {STATE_FILE_PATH}]   # only if the State document exists per Project Document Index
   ```

   Multi-repo (`PLAN_DIR ≠ CODE_DIR`): pass `--guard-path` unchanged – the script's filter drops guard paths that resolve outside `CODE_DIR` and emits `GUARD_SKIPPED:G2:<path>` on stderr. In multi-repo, plan/State files don't live in `CODE_DIR`'s history so they cannot be leaked there anyway; the skip is informational. Capture both stdout and stderr from this invocation so `GUARD_SKIPPED:` (stderr) is preserved alongside the parsed status lines (stdout).

   The script runs PRECONDITION → G1 → G2 → G3 → squash → commit with the load-bearing `Squashed-story: {STORY_ID}` trailer, and never runs `git reset --hard` / `git clean` / `git branch -D` on failure. Parse stdout (one line per stage); branch by status:

   - `SQUASH_OK` + `COMMIT_OK` → proceed to step 2.
   - `SQUASH_CONFLICT` → conflict markers in the main checkout's index.
     - Spawn a sub-agent following [`worktree-merge-resolve.md`](worktree-merge-resolve.md); pass `STORY_ID`, `BASE_BRANCH`, `WORKTREE_PATH_ABS`, `SUMMARY` (or the summary-file path `.agent_temp/merge-summary-{STORY_ID}.txt` written in this step), and the project's verification commands from `CLAUDE.md` → `Key Dev Commands`.
     - `outcome: resolved` → proceed to step 2.
     - `outcome: failed` or `cancelled` → take `{ERROR_TAG}` from the sub-agent's `merge_resolve.error_message` output. If `.agent_temp/merge-resolve-{STORY_ID}.patch` exists (sub-agent preserved its staged resolution per `worktree-merge-resolve.md` Step 4), include the path in the failure record so the user can replay the resolution. Then:
       - `printf 'merge-resolve:%s\n' "{ERROR_TAG}" > "{WORKTREE_PATH_ABS}/.andthen-fail-reason"` – marker for `teardown-worktrees.sh`, which surfaces the failure as `UNMERGED:<branch>:merge-resolve:<error-tag>` instead of a bare `UNMERGED`.
       - `git reset --hard HEAD` on the main checkout to roll back the staged/working-tree squash content. **`git merge --abort` does NOT work after `git merge --squash`** – `--squash` deliberately suppresses `MERGE_HEAD`, so abort fails with "no merge to abort". `reset --hard HEAD` is safe here: the story branch's commits are unaffected (the squash copied from it).
       - Record `FAILED:merge-resolve-{ERROR_TAG}`, preserve worktree, continue.
   - `GUARD_FAIL:G1:empty_branch` → record `FAILED:worktree-routing-failure`, preserve worktree, continue.
   - `GUARD_FAIL:G1:no_merge_base` → record `FAILED:worktree-no-merge-base` (disconnected histories or a detached worktree branch – unusual), preserve worktree, continue.
   - `GUARD_FAIL:G2:<paths>` → record `FAILED:shared-file-leak-into-branch`, preserve worktree, continue.
   - `GUARD_FAIL:G3:worktree_dirty` → record `FAILED:worktree-dirty`, preserve worktree, continue.
   - `COMMIT_FAIL:g2_git_error:<path>:rc=<n>` → Stop-the-Line; G2's `git diff` returned exit ≥128 (not a clean 0/1 result). Refusing to classify as leak avoids freezing the story under a false `FAILED:shared-file-leak-into-branch`. Investigate the underlying git error (lock contention, corrupt object, invalid pathspec) before retrying.
   - `COMMIT_FAIL:<reason>` → record `FAILED:commit-failed`, preserve worktree, continue.
   - `PRECONDITION_FAIL:main_checkout_dirty` → Stop-the-Line; investigate the main checkout before proceeding to other worktrees in the wave.
   - `PRECONDITION_FAIL:wrong_branch:<actual>` → Stop-the-Line; orchestrator CWD drifted off `{BASE_BRANCH}` between merges. Restore CWD branch state before proceeding.
   - `PRECONDITION_FAIL:not_in_git_repo` → Stop-the-Line; orchestrator CWD or `WORKTREE_PATH_ABS` resolved to a non-repo path.
   - `PRECONDITION_FAIL:repo_mismatch:<path>` → Stop-the-Line; CWD and the worktree belong to different repos (multi-repo misconfiguration or stale `WORKTREE_PATH_ABS` capture).
2. **Verify build** on `{BASE_BRANCH}` post-commit.
3. **Apply deferred shared writes** (this is the **primary** write path for `plan.json` / State in worktree mode, not a repair). `STORY_ID`, `FIS_FILE_PATH`, and `PLAN_FILE_PATH` come from Step 1's plan parse; the audit block contributes only `Completion summary` (already captured into `SUMMARY` in step 1). Run:

   - `andthen:ops update-plan {PLAN_FILE_PATH} {STORY_ID} done`
   - `andthen:ops update-plan-fis {PLAN_FILE_PATH} {STORY_ID} {FIS_FILE_PATH}` – only when the story's `fis` is `null` or differs from `{FIS_FILE_PATH}` after path normalization.
   - `andthen:ops update-state active-story {STORY_ID} Done` – only if the State document exists.
   - `andthen:ops update-state note "{SUMMARY}"`.

   Missing audit block is not Stop-the-Line; log the miss and proceed with the fallback `SUMMARY` already in hand.

4. **Commit the resulting writes in the repo where the files live**:
   - **Single-repo** (`PLAN_DIR == CODE_DIR`) – commit on `CODE_DIR`'s `{BASE_BRANCH}`. See Worktree Merge Ordering below – subsequent merges in this wave and Wave N+1 worktrees must include these commits.
   - **Multi-repo** (`PLAN_DIR ≠ CODE_DIR`) – `plan.json` and the `State` document are **not** in `CODE_DIR`'s history. If `PLAN_DIR` is itself a git repo, commit there; otherwise the file edits stand on their own. `CODE_DIR`'s `{BASE_BRANCH}` is unaffected, so the Wave N+1 stale-base concern does not apply to plan/state files in multi-repo. (Code-side commits from the merge in step 1 still land on `CODE_DIR`'s `{BASE_BRANCH}` as usual.)

5. **Clean up worktree and branch** in `CODE_DIR` (orchestrator's CWD). **Precondition**: `pwd` must be `CODE_DIR`, not inside a `story-*` worktree (`git worktree remove` refuses to remove the current worktree). Use the `{WORKTREE_PATH_ABS}` captured at create time (held in the shell as `$WORKTREE_PATH`); fall back to lookup only on orchestrator restart.
   - Captured-path fallback: `WORKTREE_PATH=$(git worktree list --porcelain | awk -v b="refs/heads/story-{STORY_ID}" '/^worktree /{p=$2} $1=="branch" && $2==b {print p}')`.
   - Empty `$WORKTREE_PATH` (create aborted, or directory manually deleted) → skip `git worktree remove`, run `git worktree prune`, then `git branch -D story-{STORY_ID} 2>/dev/null || true`. Continue. Not Stop-the-Line.
   - `git -C "$WORKTREE_PATH" status --porcelain` non-empty → repair branch left state behind (G3 should have caught it upstream). `AUTO_MODE` records failed and preserves; else Stop-the-Line.
   - `git worktree remove "$WORKTREE_PATH"` then `git branch -D story-{STORY_ID}`. `-D` (not `-d`) is **required**: squash commits have different SHA + tree-parents than the side branch's tip, so `-d`'s "fully-merged" check always refuses after squash. The squash commit on `{BASE_BRANCH}` already carries all the work.
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

Also verify the **Plan Acceptance Gate** before `Done`: every FIS scenario/criteria checkbox is `[x]` (Final Validation Checklist when present), implementation observations present when the FIS narrowed scope, `review-*` task completed without accepted findings.

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

**Stdout consumption** (line-by-line):
- `MERGED:<branch>` – worktree and branch removed.
- `MERGED_DIRTY:<branch>` – squash-merged but has uncommitted edits or post-squash commits; preserved for user. Log; not Stop-the-Line.
- `MERGED_INDETERMINATE:<branch>:diff_rc=<n>` – squash matched but `git diff` exited ≥128 (git error). Preserved pending inspection; not Stop-the-Line.
- `UNMERGED:<branch>` – preserved; log for user.
- `DETACHED:<path>` – preserved; log.

**Non-zero exit** → Stop-the-Line. Do not silently ignore.

**Empty stdout** → exit 0, no action.

**Post-teardown verify**: `git worktree list` shows only main checkout, pre-existing non-`story-*` worktrees, and explicitly preserved `story-*` ones. Anything else is Stop-the-Line.

After teardown: shutdown teammates, delete team.


## Known Limitations

Runtime-level concerns the skill prompts cannot fully gate.

- **STOP propagation has one-turn latency.** Messages are processed between turns; no mid-turn interrupt is available skill-side. The **Inbox-STOP first** rule closes the window to one turn-cycle. If a wave's audit fires STOP at t=10s and two teammates are mid-turn until t=180s, they finish their turns first.
- **Self-claim races have no skill-side override.** Task-file-locking prevents same-task races, but if a teammate violates self-review prevention (claiming `review-Sxx` after `impl-Sxx`), the orchestrator only catches it at quick-review report time. Stop-the-Line and re-delegate.
