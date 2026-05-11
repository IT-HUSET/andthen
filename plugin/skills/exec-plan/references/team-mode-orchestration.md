# Team-Mode Orchestration

Loaded when `--team` is active (Step 3T). Covers team setup, per-story implementer and reviewer prompts, task management, merge wave, status updates gate, monitoring, and Final Worktree Teardown.

This reference is the single source of truth for all team-mode behavior. Default-mode invocation (no `--team`) does not load this reference.


## Team Setup

Create team `"plan-pipeline"` with pre-assigned tasks. Size: 1 implementer (≤4 stories), 2 (5–10), 3 (11+). Add 1–2 reviewers for `quick-review` tasks. Use a capable coding model for all teammates.

Define `AUTO_SUFFIX = " --auto"` when `AUTO_MODE=true`, else `AUTO_SUFFIX = ""`. Define `WORKTREE_SUFFIX = " --defer-shared-writes"` when `USE_WORKTREE=true`, else `WORKTREE_SUFFIX = ""` (this is the propagated form of exec-plan's `--worktree` — exec-spec's flag describes its own behavior: defer shared-file writes).

**Pre-create-and-verify isolation** _(when `USE_WORKTREE=true`)_. Harness isolation is unreliable under `team_name` — every worktree is created via bash before TeamCreate; isolation is enforced by the implementer's first-action verify gate plus Merge Wave guards G1/G2/G3, never by `isolation: "worktree"` or `EnterWorktree`. Per `impl-*` task in the wave:

```
bash ${CLAUDE_SKILL_DIR}/scripts/create-worktree.sh {STORY_ID} {BASE_BRANCH} {CODE_DIR_ABS}
```

Capture `WORKTREE_PATH=` from stdout into `{WORKTREE_PATH_ABS}` for per-task substitution. Non-zero exit → Stop-the-Line. Pre-existing branch or directory → run `teardown-worktrees.sh` first.

**Substitution scope** — at team creation, replace each of the following placeholders in every teammate system prompt with its literal resolved value: `{AUTO_SUFFIX}`, `{WORKTREE_SUFFIX}`, `{CODE_DIR_ABS}` (absolute path to code repo), `{BASE_BRANCH}` (resolved at run start per Step 1). Per-task placeholders for the implementer — `{STORY_ID}` (bare plan story id, e.g. `S03`; derived by the orchestrator from the task's story binding — not by stripping the `impl-` prefix from the team task name like `impl-S03`), `{fis_path}`, and (under `USE_WORKTREE=true`) `{WORKTREE_PATH_ABS}` — are filled by the orchestrator at TeamCreate time. The reviewer derives `STORY_ID` from its task name at runtime. Scripts that take a story id (`create-worktree.sh`, `verify-in-worktree.sh`, `merge-worktree.sh`) always receive `{STORY_ID}` (bare), never the team task name. Teammates have no access to `AUTO_MODE` / `USE_WORKTREE` / orchestrator-side variables, so anything not in either list must be derived by the teammate at runtime.


## Implementer Prompt

Compose the per-story sub-agent prompt by substituting the canonical Per-Story Worker Prompt block (see `exec-plan/SKILL.md` bottom section) with `{MODE}=team` and these overrides:
- `{WORKTREE_PATH_ABS}`: the absolute path captured from `create-worktree.sh` for this story (worktree mode only)
- `{AUTO_SUFFIX}` and `{WORKTREE_SUFFIX}`: pre-substituted per Team Setup above

Include in each implementer's system prompt:
- **Inbox-STOP first** (every turn, before anything else): scan messages from the lead. If any contains `STOP` / `ABORT` / `CANCEL`, halt the task, report the message back, do not start or resume work. Mid-turn interrupt is not available from skill-side; this is the only synchronization point.
- **Self-review prevention** (claim-time): only claim `impl-*` tasks. Never claim `review-Sxx` if you previously completed `impl-Sxx` — pick a different unblocked task instead.
- **Per task, worktree mode** (`{WORKTREE_PATH_ABS}` non-empty) — step 1 below is the durable system-prompt restatement of `{WORKTREE_PRELUDE}` (defined in `exec-plan/SKILL.md` → Per-Story Worker Prompt). Edit both together:
  1. **HARD GATE — first action after inbox check**: `cd {WORKTREE_PATH_ABS}` then `bash ${CLAUDE_SKILL_DIR}/scripts/verify-in-worktree.sh {STORY_ID} {WORKTREE_PATH_ABS}`. Anything other than `VERIFY_OK` on stdout → STOP. Do not Read, Edit, Write, Glob, Grep, or run further bash; report the `VERIFY_FAIL:<reason>` line and mark the task failed.
  2. **Absolute paths only** for every Read/Edit/Glob/Grep/cd/shell substitution. Relative paths resolve against the team agent's internal project root (the main checkout), not the worktree, and silently leak edits.
  3. Run `/andthen:exec-spec {fis_path}{AUTO_SUFFIX}{WORKTREE_SUFFIX}`.
  4. **Post-impl HARD GATE — before reporting done**: re-run `bash ${CLAUDE_SKILL_DIR}/scripts/verify-in-worktree.sh {STORY_ID} {WORKTREE_PATH_ABS}` AND `git -C {CODE_DIR_ABS} status --porcelain`. Anything other than `VERIFY_OK` + empty porcelain → report `LEAK_DETECTED:<reason>` or `VERIFY_FAIL:<reason>` and mark the task failed. This closes the verify→exec-spec→report window.
  5. On success: report `exec-spec` Step 4a numbers (build, tests, lint/type-check, format). Do NOT call `EnterWorktree` or `ExitWorktree`. The orchestrator handles squash-merge and cleanup.
- **Per task, no-worktree mode** (`{WORKTREE_PATH_ABS}` empty): `cd {CODE_DIR_ABS}` → `/andthen:exec-spec {fis_path}{AUTO_SUFFIX}{WORKTREE_SUFFIX}`. Inbox-STOP and self-review rules above still apply; the worktree-specific HARD GATEs do not (no worktree to verify).
- **`{WORKTREE_SUFFIX}` non-empty (deferred shared writes)**: `exec-spec` skips `plan.json` / State writes and emits a `## Deferred Shared Writes` audit block (`Story` / `Plan` / `FIS` / `Completion summary`). Pass it through to your report. Do NOT stage or commit `plan.json` or the State document inside the worktree branch — guard G2 fails the story if you do.
- `exec-spec` `BLOCKED:` or Failed Story Report → do not mark done; preserve the worktree and report details.
- Absolute FIS paths. Escalate unresolvable issues.
- Do not call `andthen:ops update-*` — `exec-spec` Step 5b owns those.


## Reviewer Prompt

Compose the per-story sub-agent prompt by substituting the canonical Per-Story Worker Prompt block (see `exec-plan/SKILL.md` bottom section) with `{MODE}=team` and reviewer-specific overrides.

Include in each reviewer's system prompt:
- **Inbox-STOP first** (every turn): scan messages from the lead. If any contains `STOP` / `ABORT` / `CANCEL`, halt the task and report the message back. Mid-turn interrupt is not available from skill-side; this is the only synchronization point.
- **Self-review prevention** (claim-time): only claim `review-*` tasks. Never claim `review-Sxx` if you previously completed `impl-Sxx` — pick a different unblocked task instead. Self-review collapses the impl/review separation and is a Stop-the-Line for the run if it lands.
- Role constraint: only work on assigned `review-*` tasks. `{CODE_DIR_ABS}`, `{BASE_BRANCH}`, and `{AUTO_SUFFIX}` are pre-substituted in this prompt by the orchestrator (per the substitution-scope rule above). Derive your story id at runtime by stripping the `review-` prefix from your task name (`review-S03` → `S03`); call this `<story-id>`.
- **Per-task workflow**:
  1. `cd {CODE_DIR_ABS}`.
  2. **Resolve the review commit SHA** — the change set is committed in both modes, so `git diff` is empty either way; `quick-review`'s `commit <sha>` FOCUS form is what gives it the change set:
     - **Worktree mode (`USE_WORKTREE=true`)**: create an unreferenced review snapshot for the full branch diff: `git commit-tree "story-<story-id>^{tree}" -p "$(git merge-base {BASE_BRANCH} story-<story-id>)" -m "review snapshot <story-id>"`. Empty result → escalate.
     - **No worktree mode (`USE_WORKTREE=false`)**: `git rev-parse HEAD`. Task-dependency ordering (`impl-<story-id>` completes before `review-<story-id>` starts, no tasks intervene) guarantees the implementer's just-completed commit is at HEAD.
  3. **Substitute both `<story-id>` and `<hex-sha>` as literal values** (slash-command lines are not bash; `$VAR` and `<placeholder>` reach `quick-review` unexpanded). Invoke: `/andthen:quick-review story <story-id> commit <hex-sha>{AUTO_SUFFIX}`. The `commit <sha>` form is recognized by `quick-review`'s Determine Scope step (priority 1) — it sets the change set to `git show <sha>` and skips the empty-`git diff` fallback path.
  4. If quick-review returns accepted findings, report them to the orchestrator and do not mark the review task done. If no findings survive, mark task done.
- Escalate unresolvable issues to orchestrator.


## Task Management

**Task naming**: `impl-{story_id}` / `review-{story_id}` (one impl task per story, one review task per story — each story has its own FIS). Teammates self-claim unblocked tasks (the runtime prevents same-task races). **Self-review prevention is teammate-side** (see Implementer / Reviewer prompts): an agent that completed `impl-Sxx` must not claim `review-Sxx`.

**Dependencies** (sequential, `USE_WORKTREE=false`): each `impl-*` is blocked by the previous `review-*`, except `AUTO_MODE` may unblock the next independent story after recording a failed/skipped story. Parallel markers ignored.

**Dependencies** (worktree, `USE_WORKTREE=true`): current-wave `impl-*` unblocked; each `review-*` blocked until its matching `impl-*` succeeds AND the per-wave **main-checkout audit** below passes; merge waits for review pass or recorded failure; W2+ `impl-*` blocked until the prior wave has merged successes and recorded failed/skipped stories.

**Review-blocking mechanism**: at TeamCreate, mark each `review-Sxx` as `blockedBy: ["impl-Sxx", "audit-W<n>"]` where `audit-W<n>` is a synthetic orchestrator-owned task representing the wave's main-checkout audit. The orchestrator self-claims and self-completes `audit-W<n>` only after running the audit successfully — so reviews cannot fire on individual `impl-*` completions alone. Without this synthetic blocker, a fast first impl finish would let a reviewer self-claim `review-S01` before the audit fires; a subsequent audit failure would leave a stale "review passed" verdict for a story that's actually failed.

**Per-wave main-checkout audit** _(worktree mode; runs once after all wave `impl-*` complete or fail, before unblocking any `review-*`)_: `git -C {CODE_DIR_ABS} status --porcelain` must be empty. Non-empty → at least one teammate bypassed the verify gate and leaked edits. Do NOT unblock reviews. Record every completed `impl-*` in this wave as `FAILED:main-checkout-leak` with the porcelain output as evidence, preserve all worktrees untouched, and proceed to FAILURE HANDLING. Never `git restore` / `git checkout .` here — the leaked files are the forensic evidence.

**Failure containment**: a failed `impl-*` task blocks only its own `review-*` task and downstream stories. In `AUTO_MODE`, record the failure, preserve its worktree/branch, skip dependents, and continue independent work. In no-worktree mode, prove the shared checkout clean before unblocking another independent `impl-*`.


## Merge Wave _(worktree mode only)_

After current-wave `impl-*` and `review-*` tasks have succeeded or been recorded failed, merge only reviewed-successful implementation tasks. Before merging, take `{WORKTREE_PATH_ABS}` from the `create-worktree.sh` capture for this story (fall back to step 5's `git worktree list --porcelain` awk lookup only after orchestrator restart) and run `git -C "{WORKTREE_PATH_ABS}" status --porcelain`. If the implementer reported `BLOCKED:` / Failed Story Report, quick-review returned unresolved accepted findings, or the worktree is dirty, record a failed story and do not run merge, deferred writes, or cleanup for that story.

For each successful worktree branch in sequence:

1. **Squash-merge via `merge-worktree.sh`**. Extract `SUMMARY` from the implementer's audit block (`^Completion summary:\s*(.+)$`, trimmed; fallback `"{STORY_ID}: completed (worktree merge)"`). Write to `.agent_temp/merge-summary-{STORY_ID}.txt` so prose never reaches the shell argument vector. Reuse the same `SUMMARY` value in step 3's `update-state note`. Invoke:

   ```
   bash ${CLAUDE_SKILL_DIR}/scripts/merge-worktree.sh {STORY_ID} {BASE_BRANCH} {WORKTREE_PATH_ABS} .agent_temp/merge-summary-{STORY_ID}.txt \
     --guard-path {PLAN_FILE_PATH} \
     [--guard-path {STATE_FILE_PATH}]   # only if the State document exists per Project Document Index
   ```

   Multi-repo (`PLAN_DIR ≠ CODE_DIR`): pass `--guard-path` unchanged — the script's filter drops guard paths that resolve outside `CODE_DIR` and emits `GUARD_SKIPPED:G2:<path>` on stderr. In multi-repo, plan/State files don't live in `CODE_DIR`'s history so they cannot be leaked there anyway; the skip is informational. Capture both stdout and stderr from this invocation so `GUARD_SKIPPED:` (stderr) is preserved alongside the parsed status lines (stdout).

   The script runs PRECONDITION → G1 → G2 → G3 → squash → commit with the load-bearing `Squashed-story: {STORY_ID}` trailer, and never runs `git reset --hard` / `git clean` / `git branch -D` on failure. Parse stdout (one line per stage); branch by status:

   - `SQUASH_OK` + `COMMIT_OK` → proceed to step 2.
   - `SQUASH_CONFLICT` → conflict markers in the main checkout's index.
     - Spawn a sub-agent following [`worktree-merge-resolve.md`](worktree-merge-resolve.md); pass `STORY_ID`, `BASE_BRANCH`, `WORKTREE_PATH_ABS`, `SUMMARY` (or the summary-file path `.agent_temp/merge-summary-{STORY_ID}.txt` written in this step), and the project's verification commands from `CLAUDE.md` → `Key Dev Commands`.
     - `outcome: resolved` → proceed to step 2.
     - `outcome: failed` or `cancelled` → take `{ERROR_TAG}` from the sub-agent's `merge_resolve.error_message` output. If `.agent_temp/merge-resolve-{STORY_ID}.patch` exists (sub-agent preserved its staged resolution per `worktree-merge-resolve.md` Step 4), include the path in the failure record so the user can replay the resolution. Then:
       - `printf 'merge-resolve:%s\n' "{ERROR_TAG}" > "{WORKTREE_PATH_ABS}/.andthen-fail-reason"` — marker for `teardown-worktrees.sh`, which surfaces the failure as `UNMERGED:<branch>:merge-resolve:<error-tag>` instead of a bare `UNMERGED`.
       - `git reset --hard HEAD` on the main checkout to roll back the staged/working-tree squash content. **`git merge --abort` does NOT work after `git merge --squash`** — `--squash` deliberately suppresses `MERGE_HEAD`, so abort fails with "no merge to abort". `reset --hard HEAD` is safe here: the story branch's commits are unaffected (the squash copied from it).
       - Record `FAILED:merge-resolve-{ERROR_TAG}`, preserve worktree, continue.
   - `GUARD_FAIL:G1:empty_branch` → record `FAILED:worktree-routing-failure`, preserve worktree, continue.
   - `GUARD_FAIL:G1:no_merge_base` → record `FAILED:worktree-no-merge-base` (disconnected histories or a detached worktree branch — unusual), preserve worktree, continue.
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
   - `andthen:ops update-plan-fis {PLAN_FILE_PATH} {STORY_ID} {FIS_FILE_PATH}` — only when the story's `fis` is `null` or differs from `{FIS_FILE_PATH}` after path normalization.
   - `andthen:ops update-state active-story {STORY_ID} Done` — only if the State document exists.
   - `andthen:ops update-state note "{SUMMARY}"`.

   Missing audit block is not Stop-the-Line; log the miss and proceed with the fallback `SUMMARY` already in hand.

4. **Commit the resulting writes in the repo where the files live**:
   - **Single-repo** (`PLAN_DIR == CODE_DIR`) — commit on `CODE_DIR`'s `{BASE_BRANCH}`. See Worktree Merge Ordering below — subsequent merges in this wave and Wave N+1 worktrees must include these commits.
   - **Multi-repo** (`PLAN_DIR ≠ CODE_DIR`) — `plan.json` and the `State` document are **not** in `CODE_DIR`'s history. If `PLAN_DIR` is itself a git repo, commit there; otherwise the file edits stand on their own. `CODE_DIR`'s `{BASE_BRANCH}` is unaffected, so the Wave N+1 stale-base concern does not apply to plan/state files in multi-repo. (Code-side commits from the merge in step 1 still land on `CODE_DIR`'s `{BASE_BRANCH}` as usual.)

5. **Clean up worktree and branch** in `CODE_DIR` (orchestrator's CWD). **Precondition**: `pwd` must be `CODE_DIR`, not inside a `story-*` worktree (`git worktree remove` refuses to remove the current worktree). Use the `{WORKTREE_PATH_ABS}` captured at create time (held in the shell as `$WORKTREE_PATH`); fall back to lookup only on orchestrator restart.
   - Captured-path fallback: `WORKTREE_PATH=$(git worktree list --porcelain | awk -v b="refs/heads/story-{STORY_ID}" '/^worktree /{p=$2} $1=="branch" && $2==b {print p}')`.
   - Empty `$WORKTREE_PATH` (create aborted, or directory manually deleted) → skip `git worktree remove`, run `git worktree prune`, then `git branch -D story-{STORY_ID} 2>/dev/null || true`. Continue. Not Stop-the-Line.
   - `git -C "$WORKTREE_PATH" status --porcelain` non-empty → repair branch left state behind (G3 should have caught it upstream). `AUTO_MODE` records failed and preserves; else Stop-the-Line.
   - `git worktree remove "$WORKTREE_PATH"` then `git branch -D story-{STORY_ID}`. `-D` (not `-d`) is **required**: squash commits have different SHA + tree-parents than the side branch's tip, so `-d`'s "fully-merged" check always refuses after squash. The squash commit on `{BASE_BRANCH}` already carries all the work.
   - Verify `git worktree list` no longer contains `story-{STORY_ID}`. Leftover → Stop-the-Line; `create-worktree.sh` would collide on the same story id.

Run all five steps for one worktree before starting the next — sequential ordering keeps each merge based on a tip that includes the prior story's deferred writes.


### Worktree Merge Ordering

**No stale-base merges.** A Wave N+1 worktree branched off an outdated `{BASE_BRANCH}` stomps deferred writes when it merges back. Wave N+1 worktrees must branch off `{BASE_BRANCH}` only after every Wave N squash-merge, per-story review, and `CODE_DIR`-bound write (deferred shared writes in single-repo, repair writes, phase transition writes) is committed to `{BASE_BRANCH}`. Multi-repo plan/state writes land in `PLAN_DIR` and are not subject to this gate.

**Deferred-write commits land before the next wave's worktrees are created.** In single-repo setups, the Merge Wave step 4 commit must reach `{BASE_BRANCH}` before any Wave N+1 worktree is created. Do not parallelize worktree creation and deferred-writes commits.

Worktree creation is bash-only (`create-worktree.sh`). Never `EnterWorktree` / `ExitWorktree` / `Agent({isolation:"worktree"})` — see `## Team Setup` for the contract.


## Status Updates Gate

Same green-gate discipline as Step 3c, then run the **Writes-Landed Checklist** (defined in Step 3c of `exec-plan/SKILL.md`) per story.

Source of truth for the checklist depends on mode:
- **Worktree** — primary writes come from the Merge Wave step's post-review "apply deferred shared writes" substep, not from inside the worktree branch. Run the checklist after the deferred writes are applied and committed (single-repo: read from `{BASE_BRANCH}`; multi-repo: read directly from `PLAN_DIR`). Any miss after that is a real loss → repair via the matching `andthen:ops update-*` once.
- **No worktree** — `exec-spec` Step 5b writes status in-place. Run the checklist as in Step 3c; one-shot repair on miss.

Additionally verify the **Plan Acceptance Gate** before accepting `Done`: each FIS success criterion is demonstrably satisfied, implementation observations are present when the FIS narrowed scope, and the story's `review-*` task completed without accepted quick-review findings.

Checklist pass → record the story in the orchestrator run ledger's `completed` list.

Move to the next phase only after every current-phase story is verified green or recorded failed/skipped with dependents handled.

**Green-gate timing**:
- **Worktree** — per-worktree build/tests pre-merge; orchestrator gate on `{BASE_BRANCH}` post-merge. Stop-the-Line on `{BASE_BRANCH}`, not inside a worktree.
- **No worktree** — gate after each `impl-*`, before the matching `review-*` unblocks.

**Take-over topology** (orchestrator repair):
- **Worktree, pre-merge** — repair via bash: `cd {WORKTREE_PATH_ABS}` (captured at create time), apply the fix, re-run `Key Dev Commands` verification, `git -C {WORKTREE_PATH_ABS} commit -am "<repair summary>"` from orchestrator CWD. Never `EnterWorktree` / `ExitWorktree`. Merge Wave then runs as normal. `AUTO_MODE` permits this only for bounded fix-forward; otherwise preserve and record failure.
- **Worktree post-merge** or **no worktree** — repair on `{BASE_BRANCH}` in orchestrator's CWD.


## Multi-Repo Rules _(when CODE_DIR ≠ PLAN_DIR's git root)_
- All git operations target `CODE_DIR` – never the plan repo
- `create-worktree.sh` must be invoked with `CODE_DIR_ABS` as its third argument so worktrees land under `CODE_DIR/.claude/worktrees/` rather than the plan repo
- FIS paths passed to agents must be **absolute**
- The plan repo is **read-only for git operations** – only the orchestrator updates `plan.json`


## Monitoring

Print progress updates — the user cannot see agent activity. Report task creation/assignment, agent starts/completions, wave completions, merge results, phase summaries, and failures.


## Final Worktree Teardown

Run after all phases complete and before shutting down the team. Also runs on failure exits (Stop-the-Line escalation, `>50%` phase failure, final review unresolvable). See FAILURE HANDLING in `exec-plan/SKILL.md`.

**Precondition**: `pwd` must be `CODE_DIR` (the main checkout), not inside a `story-*` worktree.

Invoke:
```
bash ${CLAUDE_SKILL_DIR}/scripts/teardown-worktrees.sh {BASE_BRANCH}
```

`git worktree prune` alone does **not** clean anything — it only purges admin records for worktrees whose directories are already gone. Live `story-*` worktrees from failed waves, abandoned stories, or earlier runs persist until removed explicitly.

**Stdout consumption** (parse one line at a time):
- `MERGED:<branch>` — informational; worktree and branch were removed by the script.
- `MERGED_DIRTY:<branch>` — worktree is squash-merged but has uncommitted edits or post-squash commits; preserved so the user can commit, rebase, or discard before re-running. Log branch in the failure summary; do not treat as Stop-the-Line.
- `MERGED_INDETERMINATE:<branch>:diff_rc=<n>` — squash matched but `git diff` exited ≥128 (git error, not 0/1). Preserved pending diff-state inspection rather than misclassified as `MERGED_DIRTY`. Log branch and `diff_rc` in the failure summary; do not treat as Stop-the-Line (the script designed this as a recoverable case).
- `UNMERGED:<branch>` — worktree is preserved; log branch in the failure summary so the user can decide whether to resume or discard.
- `DETACHED:<path>` — worktree is preserved; log path in the failure summary.

**Non-zero exit** → Stop-the-Line per `${CLAUDE_PLUGIN_ROOT}/references/execution-discipline.md`. Do not silently ignore a non-zero exit or unparseable output.

**Empty stdout** (no leftovers) → exit 0, no action needed.

**Post-teardown verify**: `git worktree list` should show only the main checkout, pre-existing non-`story-*` user worktrees, and any `story-*` worktrees explicitly preserved as unmerged or detached. Anything else is Stop-the-Line.

After teardown: shutdown teammates, delete team.


## Known Limitations

These are runtime-level concerns that the skill prompts cannot fully gate. They are mitigated where possible and documented here so callers set the right expectations.

- **STOP propagation has one-turn latency, not zero.** The orchestrator cannot mid-turn-interrupt a teammate from skill-side; messages are processed between turns. The **Inbox-STOP first** rule in the Implementer / Reviewer prompts closes the window to one turn-cycle. If a wave's main-checkout audit fires STOP at t=10s and two teammates are mid-turn until t=180s, they finish their turns before reading the STOP. Plan for this.
- **Self-claim races have no skill-side override.** Runtime task-file-locking prevents two agents from grabbing the same task, but if a misbehaving teammate violates the **Self-review prevention** rule (claiming `review-Sxx` after completing `impl-Sxx`), the orchestrator catches it only at quick-review report time — the review is meaningless at that point. Stop-the-Line and re-delegate to a different agent.
