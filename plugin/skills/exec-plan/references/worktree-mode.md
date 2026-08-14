# Worktree Mode (`--worktree`)

Per-story git-worktree isolation for the `andthen:exec-plan` skill. Loaded when `USE_WORKTREE=true` in either execution mode – sub-agent (Step 3) or team (Step 3T; [`team-mode-orchestration.md`](team-mode-orchestration.md) owns the team-side wiring). Single source of truth for the worktree lifecycle: create → verify → squash-merge → teardown.

**Script-driven isolation is the contract** – the lifecycle runs through the bundled scripts and the `andthen:merge-resolve` skill, never `EnterWorktree` / `ExitWorktree` / `Agent({isolation:"worktree"})`. Harness isolation is host-specific (and unreliable under `team_name`), and it bypasses the guarded merge protocol: merge-resolve's G1/G2/G3 guards, the load-bearing `Squashed-story:` trailer, and teardown's leftover classification all key off this flow.

## Clean Baseline

Before creating any worktree, `CODE_DIR` must be on `{BASE_BRANCH}` with an empty porcelain status. Two classes are not user dirt: orchestrator-owned pending writes (Step 3a State/plan edits, triage appends) – commit them to `{BASE_BRANCH}` first; and framework temp output under `.agent_temp/` – ensure it is git-ignored, adding it to `.git/info/exclude` when absent (local-only, never committed): every later porcelain check, including merge-resolve's clean-checkout precondition, depends on it. Never stash, commit, or move pre-existing user changes – dirt the run does not own is Stop-the-Line: it breaks story attribution and fails every merge.

## Create (per wave)

Pre-create one worktree per schedulable story in the current wave, before its worker spawns – multi-repo: only the active story, per the parent skill's Multi-repo FIS attribution rule:

```
bash ${CLAUDE_SKILL_DIR}/scripts/create-worktree.sh {STORY_ID} {BASE_BRANCH} {CODE_DIR_ABS}
```

`{CODE_DIR_ABS}` is the absolute `CODE_DIR` from Step 1. Capture `WORKTREE_PATH=` from stdout into `{WORKTREE_PATH_ABS}`. Non-zero exit → Stop-the-Line. Pre-existing branch/directory → run `teardown-worktrees.sh` first. Wave N+1 worktrees are created only after the **Merge Ordering** gate below.

## Worker Isolation Block

Splice this block into each worktree worker's prompt with placeholders substituted – including `${CLAUDE_SKILL_DIR}`, which the orchestrator resolves to the exec-plan skill directory's absolute path (workers cannot resolve it themselves), and `{AUTO_SUFFIX}` (` --auto` when `AUTO_MODE=true`, else empty). Sub-agent mode appends it to the Step 3b Worker Prompt; team mode uses its own Implementer Prompt instead – do not splice this block there.

```
Worktree isolation (you run inside a dedicated git worktree):
- cd {WORKTREE_PATH_ABS}; first action after cd: bash ${CLAUDE_SKILL_DIR}/scripts/verify-in-worktree.sh {STORY_ID} {WORKTREE_PATH_ABS}. Anything other than VERIFY_OK → STOP, report VERIFY_FAIL:<reason>, and fail the story.
- Absolute paths only afterwards – relative paths silently leak to the main checkout.
- Do NOT stage plan.json or the State document in the story branch (merge guard G2 fails the story). Pass exec-spec's `## Deferred Shared Writes` audit block through to your report.
- On exec-spec success: require a non-empty story delta and confirm deferred plan.json / State writes are absent, then stage the attributable story delta and commit it with the brief subject `story {STORY_ID}`.
- Review the commit, never the working tree – after the commit `git diff` is empty, so the Worker Prompt's "on the changes" would silently review nothing. Snapshot the whole branch, so no earlier commit on a reused worktree escapes review: `git commit-tree "story-{STORY_ID}^{tree}" -p "$(git merge-base {BASE_BRANCH} story-{STORY_ID})" -m "review snapshot {STORY_ID}"`, then invoke the `andthen:quick-review` skill with `story {STORY_ID} commit <snapshot-sha>{AUTO_SUFFIX}` (literal hex SHA) and the exact `INTENT CONTEXT: {FIS_PATH}` line. Any accepted-Fix remediation gets its own commit and one re-review scoped to that commit alone.
- Leave the worktree clean and report `IMPLEMENTATION_COMMIT: <story branch tip – never a review snapshot>`, exec-spec's build / test / lint numbers, and the review outcome – every accepted quick-review finding with its `Class` and `Routing` fields, or `review clear`; a Fix finding still accepted after your one remediation round is reported as persistent.
- On BLOCKED: or a Failed Story Report: preserve the worktree and report details.
```

In a single repo, translate `{FIS_PATH}` into the worktree; a multi-repo run keeps the canonical absolute plan-repo path.

## Merge Flow (per story)

Merge only reviewed-successful stories: exec-spec green, per-story review cleared of accepted Fix findings. Reconciliation-class findings persist post-merge (step 3 below), never before. Worker `BLOCKED:` past triage, a Failed Story Report, `ambiguous-intent`, persistent code-defect Fix (the worker's single remediation round is the story's whole Fix budget – not a re-delegation trigger), or a worker-left dirty worktree → failed story: no merge, no deferred writes, no cleanup – preserve the worktree. Ordinary and ledger-linked drift Notes surface in Step 6 without blocking the merge.

Before each merge, take `{WORKTREE_PATH_ABS}` from the `create-worktree.sh` capture (fall back to step 5's `git worktree list --porcelain` lookup only after orchestrator restart), and require `git rev-parse story-{STORY_ID}` to equal the story's final reviewed commit (sub-agent mode: the reported `IMPLEMENTATION_COMMIT`, or a Repair Topology commit when one landed; team mode: the last `REVIEW_COMMIT`) – a mismatched tip carries unreviewed content: failed story, preserve the worktree. Run all five steps for one story before starting the next – sequential ordering keeps each merge based on a tip that includes the prior story's deferred writes. Single-repo: commit any pending CODE_DIR-bound orchestrator write (repair commits, phase writes) to `{BASE_BRANCH}` first – merge-resolve rejects a dirty checkout.

1. **Invoke the `andthen:merge-resolve` skill** with the story's arguments (one logical line):

   First, extract the worker's `Completion summary` from the audit block (regex `^Completion summary:\s*(.+)$`, trimmed; fallback `"{STORY_ID}: completed (worktree merge)"`) and write it to `.agent_temp/merge-summary-{STORY_ID}.txt` so prose never reaches the shell argument vector. Reuse this `SUMMARY` in step 3's `update-state note`.

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

   - Step 3c's **Review-Class Persistence Gate** first, now that the merged FIS and its sibling ledger are on `{BASE_BRANCH}`. Deferring it here keeps one writer on the ledger: the worker's in-worktree entries arrive with the squash, the orchestrator's review-derived entries land after. Persistence failure stops before any status write.
   - `andthen:ops update-plan-fis {PLAN_PATH} {STORY_ID} {FIS_POINTER}` – only when the story's `fis` is `null` or differs from the canonical basename pointer `{FIS_POINTER}` derived from trusted plan/story data; `{FIS_PATH}` remains the resolved artifact path.
   - Re-read and require that `fis === {FIS_POINTER}`, resolves beside the plan to `{FIS_PATH}`, and carries matching Plan/Story provenance. Failure leaves the prior status unchanged and contains the story.
   - Only after that gate: `andthen:ops update-plan {PLAN_PATH} {STORY_ID} done`.
   - `andthen:ops update-state active-story {STORY_ID} Done` – only if the State document exists.
   - `andthen:ops update-state note "{SUMMARY}"`.

   Missing audit block is not Stop-the-Line; log the miss and proceed with the fallback `SUMMARY` already in hand.

4. **Commit the resulting writes in the repo where the files live**:
   - **Single-repo** (`PLAN_DIR == CODE_DIR`) – commit on `CODE_DIR`'s `{BASE_BRANCH}`. See Merge Ordering below.
   - **Multi-repo** (`PLAN_DIR ≠ CODE_DIR`) – `plan.json` and the State document live outside `CODE_DIR`'s history. If `PLAN_DIR` is itself a git repo, commit there; otherwise the file edits stand on their own. `CODE_DIR`'s `{BASE_BRANCH}` is unaffected.

5. **Clean up worktree and branch** in `CODE_DIR` (orchestrator's CWD). **Precondition**: `pwd` must be `CODE_DIR`, not inside a `story-*` worktree (`git worktree remove` refuses to remove the current worktree).
   - Captured-path fallback: `WORKTREE_PATH=$(git worktree list --porcelain | awk -v b="refs/heads/story-{STORY_ID}" '/^worktree /{p=$2} $1=="branch" && $2==b {print p}')`.
   - Empty `$WORKTREE_PATH` (create aborted, or directory manually deleted) → skip `git worktree remove`, run `git worktree prune`, then `git branch -D story-{STORY_ID} 2>/dev/null || true`. Continue. Not Stop-the-Line.
   - `git worktree remove "$WORKTREE_PATH"` then `git branch -D story-{STORY_ID}`. `-D` (not `-d`) is required: squash commits have different SHA + tree-parents than the side branch's tip, so `-d`'s "fully-merged" check always refuses after squash. The squash commit on `{BASE_BRANCH}` already carries all the work.
   - Verify `git worktree list` no longer contains `story-{STORY_ID}`. Leftover → Stop-the-Line; `create-worktree.sh` would collide on the same story id.

## Merge Ordering

**No stale-base merges.** A Wave N+1 worktree branched off an outdated `{BASE_BRANCH}` stomps deferred writes when it merges back. Wave N+1 worktrees branch only after every Wave N squash-merge, per-story review, and `CODE_DIR`-bound write (single-repo deferred writes, repair writes, phase transitions, Step 3d triage FIS appends) is committed to `{BASE_BRANCH}` – else stale worktree FIS copies stomp the triage appends at merge. Do not parallelize. Multi-repo plan/state writes land in `PLAN_DIR` and are not subject to this gate.

## Verification Timing

- **Green gate**: build/tests run in the worktree pre-merge – gate ownership follows the execution mode's own rules (sub-agent mode: Step 3c, executed from `{WORKTREE_PATH_ABS}` – the story's changes exist nowhere else yet; team mode: implementer numbers + reviewer). A gate run that regenerates artifacts leaves the worktree dirty: restore it to the reviewed tip before the Merge Flow, or G3 fails a green story.
- **Orchestrator entry**: whenever the orchestrator itself works inside a worktree (this gate, Repair Topology), run `verify-in-worktree.sh` as the first action after `cd`, exactly as workers do – a `cd` that silently did not take turns the gate into a vacuous green against the main checkout, or lands repair commits on `{BASE_BRANCH}`. Anything other than `VERIFY_OK` → Stop-the-Line. Return to `CODE_DIR` before the Merge Flow – merge-resolve asserts the main checkout, so a lingering worktree CWD turns its `precondition:` branch into a spurious Stop-the-Line. A red gate inside a worktree is Step 3c iteration or containment; Stop-the-Line fires on the post-merge re-run on `{BASE_BRANCH}`.
- **Writes-Landed Checklist**: runs after the deferred shared writes commit (single-repo: from `{BASE_BRANCH}`; multi-repo: from `PLAN_DIR`), not merely after the green gate. Miss → one-shot repair via `andthen:ops update-*`.

## Repair Topology (orchestrator take-over)

- **Pre-merge**: `cd {WORKTREE_PATH_ABS}`, apply the one bounded repair using absolute paths under that root (only bash follows `cd` – file tools resolve relative paths against the session CWD and would silently edit the main checkout, which `verify-in-worktree.sh` cannot catch), re-run `Key Dev Commands` verification, and commit it in the worktree. Re-review the repair commit before merging (sub-agent mode: re-run the `andthen:quick-review` skill with `story {STORY_ID} commit <repair-sha>{AUTO_SUFFIX}` and the `INTENT CONTEXT: {FIS_PATH}` line; team mode: re-open the review task per `team-mode-orchestration.md`). Clear/Note-only proceeds to merge; persistent Fix fails and preserves the worktree.
- **Post-merge**: repair on `{BASE_BRANCH}` in the orchestrator's CWD, commit, re-review once with the same commit-scoped invocation; same containment on persistent Fix.

A retried or re-delegated story reuses its existing worktree – no second `create-worktree.sh` – with `verify-in-worktree.sh` still the retried worker's first action.

## Multi-Repo Rules _(CODE_DIR ≠ PLAN_DIR's git root)_

- Worktree and merge git operations target `CODE_DIR`; `create-worktree.sh` receives `CODE_DIR_ABS` as its third argument so worktrees land under `CODE_DIR/.claude/worktrees/`.
- FIS paths passed to workers are **absolute**; only the orchestrator updates plan/State files, per the parent skill's Multi-repo FIS attribution rule.

## Final Worktree Teardown

Runs after all phases complete, and on failure exits (Stop-the-Line, >50% phase failure, final review unresolvable). See `exec-plan/SKILL.md` FAILURE HANDLING.

**Precondition**: `pwd` is `CODE_DIR` (main checkout), not inside a `story-*` worktree.

Invoke:
```
bash ${CLAUDE_SKILL_DIR}/scripts/teardown-worktrees.sh {BASE_BRANCH}
```

`git worktree prune` alone only purges admin records for already-gone directories. Live `story-*` worktrees persist until removed explicitly.

**Stdout consumption**: each line classifies one leftover worktree. `MERGED:<branch>` was cleaned automatically; `UNMERGED:<branch>[:<reason>]` is preserved for the user. Other prefixes (`MERGED_DIRTY:`, `MERGED_INDETERMINATE:`, `DETACHED:`) are also preserved – log them as informational diagnostics, no special handling.

**Non-zero exit** → Stop-the-Line. Empty stdout (exit 0) → no action.

**Post-teardown verify**: `git worktree list` shows only main checkout, pre-existing non-`story-*` worktrees, and explicitly preserved `story-*` ones. Anything else is Stop-the-Line.
