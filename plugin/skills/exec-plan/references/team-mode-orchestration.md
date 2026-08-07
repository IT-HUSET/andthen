# Team-Mode Orchestration

Loaded when `--team` is active (Step 3T). Single source of truth for team-mode behavior; default-mode does not load it.

## Team Setup

Create team `"plan-pipeline"` with pre-assigned tasks. Size: 1 implementer (≤4 stories), 2 (5–10), 3 (11+). Add 1–2 reviewers for `quick-review`. Implementers are medium/larger implementation tasks; reviewers are high-judgment review tasks. Let the nearest Sub-Agent Model Policy choose model and effort, or inherit when none exists.

Define `AUTO_SUFFIX = " --auto"` when `AUTO_MODE=true`, else `""`. Define `DEFER_SUFFIX = " --defer-shared-writes"` in every mode; the orchestrator owns shared status only after review.

Before `TeamCreate`, require `CODE_DIR` to be on `{BASE_BRANCH}` with an empty porcelain status. This attribution baseline is mandatory in both modes; never stash, commit, or move pre-existing user changes. A dirty checkout is Stop-the-Line and recommends `--worktree` only after the user makes the base checkout clean.

Apply the parent skill's **Multi-repo FIS attribution** rule before assigning tasks. In that topology, only the next story gets an active implementer or worktree.

**Pre-create worktrees in bash** _(when `USE_WORKTREE=true`)_. Harness isolation is unreliable under `team_name`; the orchestrator creates worktrees for currently active `impl-*` tasks before TeamCreate. Multi-repo mode activates one.

```
bash ${CLAUDE_SKILL_DIR}/scripts/create-worktree.sh {STORY_ID} {BASE_BRANCH} {CODE_DIR_ABS}
```

Capture `WORKTREE_PATH=` from stdout into `{WORKTREE_PATH_ABS}`. Non-zero exit → Stop-the-Line. Pre-existing branch/directory → run `teardown-worktrees.sh` first.

**Substitution scope** – at team creation, replace in every teammate system prompt: `{AUTO_SUFFIX}`, `{DEFER_SUFFIX}`, `{CODE_DIR_ABS}`, `{BASE_BRANCH}`, `{UNTRUSTED_REQUIREMENTS_LINE}` (the run's exact line when externally derived, otherwise empty), and `{GOVERNING_PLAN_LINE}` (exact `GOVERNING PLAN PATH: {PLAN_PATH}` in local-directory mode, empty under `--from-issue`). Per story tasks fill `{STORY_ID}`, `{FIS_PATH}`, `{WORKTREE_PATH_ABS}`, and `{IMPLEMENTATION_ROOT}` (worktree path when active, otherwise `CODE_DIR`). In a single repo, translate `{FIS_PATH}` into that worktree; in a multi-repo run, keep the canonical absolute plan-repo path. Reviewer derives `STORY_ID` from its task name; before each initial/re-review unblock, the orchestrator sets exact task input `REVIEW_COMMIT: <full-sha>` to the implementation/repair commit. Scripts receive the bare story ID. Anything not substituted is derived at runtime.


## Implementer Prompt

Apply the **Worker Contract** from `exec-plan/SKILL.md` Step 3b. The team Implementer runs only the `exec-spec` half of the canonical Worker Prompt – the `quick-review` half is the Reviewer's task.

{UNTRUSTED_REQUIREMENTS_LINE}
{GOVERNING_PLAN_LINE}
CODE DIRECTORY: {IMPLEMENTATION_ROOT}

Per `impl-*` task assigned to you (orchestrator pre-assigns owners – work only your assigned tasks, no shared-queue claiming):
- `cd {CODE_DIR_ABS}` (worktree mode: `cd {WORKTREE_PATH_ABS}` instead).
- **Worktree mode** (`{WORKTREE_PATH_ABS}` non-empty), as first action after `cd`: `bash ${CLAUDE_SKILL_DIR}/scripts/verify-in-worktree.sh {STORY_ID} {WORKTREE_PATH_ABS}`. Anything other than `VERIFY_OK` → STOP, report `VERIFY_FAIL:<reason>`, fail the task. Subsequent operations use absolute paths only (relative paths silently leak to the main checkout). Pass the `## Deferred Shared Writes` audit block through to your report; do NOT stage `plan.json` or the State document inside the worktree branch – the `andthen:merge-resolve` skill's G2 guard fails the story.
- Invoke the `andthen:exec-spec` skill with `{FIS_PATH}{AUTO_SUFFIX}{DEFER_SUFFIX}`. The Worker Contract delegates exec-spec's standalone completion-presentation gate: skip it – the orchestrator owns the consolidated one.
- On success, require a non-empty story delta and confirm deferred `plan.json` / State writes are absent. Stage the attributable story delta, commit it with the brief subject `story {STORY_ID}`, and require the checkout clean. Report `IMPLEMENTATION_COMMIT: <full-sha>` plus `exec-spec` Step 4a numbers (build, tests, lint/type-check, format). Orchestrator handles squash-merge and cleanup. A missing commit, shared-write leak, or residual dirty status fails the task.
- On `BLOCKED:` or Failed Story Report: do not mark done; preserve the worktree and report details.


## Reviewer Prompt

Apply the **Worker Contract** from `exec-plan/SKILL.md` Step 3b. The team Reviewer runs only the `quick-review` half of the canonical Worker Prompt.

{UNTRUSTED_REQUIREMENTS_LINE}
{GOVERNING_PLAN_LINE}
INTENT CONTEXT: {FIS_PATH}

Per `review-*` task assigned to you (orchestrator pre-assigns owners; `impl-Sxx` and `review-Sxx` are never assigned to the same teammate, so self-review cannot occur):
- Derive story id by stripping `review-` from your task name (`review-S03` → `S03`).
- `cd {CODE_DIR_ABS}`.
- **Resolve `REVIEW_COMMIT`** from the task's exact input, require a commit object, and bind it to current state:
  - **Worktree mode**: require it to equal `git rev-parse story-<story-id>`, then create an unreferenced full-branch snapshot: `git commit-tree "story-<story-id>^{tree}" -p "$(git merge-base {BASE_BRANCH} story-<story-id>)" -m "review snapshot <story-id>"`. Require the snapshot tree to differ from its parent.
  - **No worktree mode**: require it to equal `git rev-parse HEAD`; use that exact SHA. Sequential dependencies guarantee no later implementation has started.
- **Substitute `<story-id>` and `<hex-sha>` as literals** (skill-invocation lines are not bash; `$VAR` and `<placeholder>` reach `quick-review` unexpanded). Invoke the `andthen:quick-review` skill with `story <story-id> commit <hex-sha>{AUTO_SUFFIX}` and preserve the exact `INTENT CONTEXT:` line.
- Apply `exec-plan` Step 3b class handling before routing: reconciliation classes return to the orchestrator's Step 3c persistence gate. For `code-defect`, Notes complete; Fix findings leave the task open for one repair/re-review and complete only when clear. No findings → complete.
- Do not call `andthen:ops update-*` yourself (Worker Contract).

## Task Management

**Naming**: `impl-{story_id}` / `review-{story_id}` (one impl + one review per story; one FIS per story).

**Pre-assignment** (no self-claim): at TeamCreate, the orchestrator round-robin distributes `impl-*` across implementer teammates and `review-*` across reviewer teammates, setting the `owner` field on every task. Same-task races are prevented by ownership, and self-review is prevented at assignment time – the same teammate is never assigned both `impl-Sxx` and `review-Sxx`. Teammates work only their assigned tasks; no claim discipline needed.

**Dependencies** (sequential, `USE_WORKTREE=false`): each `impl-*` is blocked by the previous `review-*`. In one repo, `AUTO_MODE` may unblock the next independent story after failure; multi-repo stops. Parallel markers ignored.

**Dependencies** (worktree, `USE_WORKTREE=true`): in one repo, current-wave `impl-*` tasks unblock together; multi-repo activates only the next story after the prior review, persistence, shared writes, and plan-repo commit. Each `review-*` waits for its implementation; merge waits for review pass or recorded failure.

**Failure containment**: a reported `BLOCKED:` first goes through **Worker `BLOCKED:` triage** (Step 3c). A repairable blocker re-opens the `impl-*` task once for its existing owner, reusing the story's existing worktree – no second `create-worktree.sh`, with `verify-in-worktree.sh` still the retried task's first action. After bounded repair, multi-repo preserves the plan delta and stops; in one repo the failed story blocks only its reviewer/dependents while `AUTO_MODE` continues independent work. No-worktree continuation requires a clean shared checkout.


## Merge Wave _(worktree mode only)_

After current-wave `impl-*` and `review-*` succeed or are recorded failed, merge only reviewed-successful implementations. Before each merge, take `{WORKTREE_PATH_ABS}` from the `create-worktree.sh` capture (fall back to step 5's `git worktree list --porcelain` lookup only after orchestrator restart). Implementer `BLOCKED:` past triage, Failed Story Report, `ambiguous-intent`, persistent code-defect Fix, or dirty worktree → failed story; no merge, deferred writes, or cleanup. Ordinary and ledger-linked drift Notes surface in Step 6 without blocking the merge.

For each successful worktree branch in sequence:

1. **Invoke the `andthen:merge-resolve` skill** with the story's arguments (one logical line):

   First, extract the implementer's `Completion summary` from the audit block (regex `^Completion summary:\s*(.+)$`, trimmed; fallback `"{STORY_ID}: completed (worktree merge)"`) and write it to `.agent_temp/merge-summary-{STORY_ID}.txt` so prose never reaches the shell argument vector. Reuse this `SUMMARY` in step 3's `update-state note`.

   ```
   {STORY_ID} {BASE_BRANCH} {WORKTREE_PATH_ABS} .agent_temp/merge-summary-{STORY_ID}.txt --guard-path {PLAN_PATH} [--guard-path {STATE_FILE_PATH}]
   ```

   `[--guard-path {STATE_FILE_PATH}]` only when the State document exists per the Project Document Index.

   Multi-repo (`PLAN_DIR ≠ CODE_DIR`): pass `--guard-path` unchanged – the skill's underlying script drops guard paths that resolve outside `CODE_DIR` and emits a `GUARD_SKIPPED:G2:<path>` line on stderr (informational; multi-repo plan/state files cannot leak into `CODE_DIR`'s history).

   Branch on `merge_resolve.outcome`:

   - `resolved` → proceed to step 2.
   - `failed` with `error_message` starting `precondition:` → Stop-the-Line. CWD drifted off `BASE_BRANCH` or main checkout is dirty / wrong repo. Investigate before any further merges.
   - Any other `failed`, and `cancelled` (harness STOP between steps; record as `FAILED:cancelled`) → record `FAILED:{error_message}` and preserve the worktree. Multi-repo stops; one repo continues with the next story. The skill is all-or-nothing: `{BASE_BRANCH}` is already rolled back / unchanged. Additionally: `logic_conflict:` / `verification:` → record `conflicted_files`, `resolution_summary`, and any replay patch; `guard:` / `squash:` → `.andthen-fail-reason` lets teardown classify the preserved worktree.

2. **Verify build** on `{BASE_BRANCH}` post-commit.

3. **Apply deferred shared writes** (this is the **primary** write path for `plan.json` / State in worktree mode, not a repair). `STORY_ID`, `FIS_PATH`, and `PLAN_PATH` come from Step 1's plan parse; the audit block contributes only `Completion summary` (already captured into `SUMMARY` above). Run:

   - `andthen:ops update-plan-fis {PLAN_PATH} {STORY_ID} {FIS_POINTER}` – only when the story's `fis` is `null` or differs from the canonical basename pointer `{FIS_POINTER}` derived from trusted plan/story data; `{FIS_PATH}` remains the resolved artifact path.
   - Re-read and require that `fis === {FIS_POINTER}`, resolves beside the plan to `{FIS_PATH}`, and carries matching Plan/Story provenance. Failure leaves the prior status unchanged and contains the story.
   - Only after that gate: `andthen:ops update-plan {PLAN_PATH} {STORY_ID} done`.
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


## Status Updates Gate

Same green-gate discipline as Step 3c, then run the **Writes-Landed Checklist** per story.

Checklist source-of-truth by mode:
- **Worktree** – primary writes come from the Merge Wave post-review "apply deferred shared writes" substep, not the worktree branch. Run the checklist after deferred writes commit (single-repo: from `{BASE_BRANCH}`; multi-repo: from `PLAN_DIR`). Miss → one-shot repair via `andthen:ops update-*`.
- **No worktree** – after the reviewer clears accepted Fix findings, apply Step 3c's Primary Shared Writes, then run the checklist; one-shot repair on miss. In a single repo, commit these orchestrator-owned shared writes before unblocking the next story and require the checkout clean.

Also verify the **Plan Acceptance Gate** before `Done`: every FIS scenario/criteria checkbox is `[x]` (Final Validation Checklist when present), implementation observations present when the FIS narrowed scope, `review-*` task completed without accepted **Fix-routed** findings.

Pass → record in the ledger's `completed` list.

Advance to the next phase only after every current-phase story is verified green or recorded failed/skipped.

**Green-gate timing**:
- **Worktree** – per-worktree build/tests pre-merge; orchestrator gate on `{BASE_BRANCH}` post-merge. Stop-the-Line on `{BASE_BRANCH}`, not inside a worktree.
- **No worktree** – gate after each `impl-*`, before the matching `review-*` unblocks.

**Take-over topology** (orchestrator repair):
- **Worktree, pre-merge** – `cd {WORKTREE_PATH_ABS}`, apply the one bounded repair, re-run `Key Dev Commands` verification, and commit it. Never `EnterWorktree` / `ExitWorktree`. Re-open the matching review task with `REVIEW_COMMIT` set to that SHA; it creates a fresh full-branch snapshot and re-runs once. Clear/Note-only completes; persistent Fix fails and preserves the worktree.
- **Worktree post-merge** or **no worktree** – repair on `{BASE_BRANCH}` in orchestrator's CWD. Commit the one bounded repair, re-open the matching review task with `REVIEW_COMMIT` set to that SHA, and apply the same transition; no-worktree must again be clean before the next story starts.


## Multi-Repo Rules _(CODE_DIR ≠ PLAN_DIR's git root)_
- Implementation, worktree, and merge git operations target `CODE_DIR`.
- `create-worktree.sh` receives `CODE_DIR_ABS` as its third argument so worktrees land under `CODE_DIR/.claude/worktrees/`.
- FIS paths passed to agents are **absolute**.
- Only the orchestrator updates plan/State files; the parent skill's Multi-repo FIS attribution rule owns serialization and commits.


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
