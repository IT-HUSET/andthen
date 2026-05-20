---
description: Internal squash-merge for one story worktree branch into the integration branch (precondition + G1/G2/G3 guards, mechanical squash, semantic conflict resolution, commit with the load-bearing `Squashed-story:` trailer). Invoked per story by the `andthen:exec-plan` skill in team-mode Merge Wave. Not user-invocable.
context: fork
user-invocable: false
argument-hint: "<story-id> <base-branch> <worktree-path> <summary-file> [--guard-path PATH]..."
---

# Merge Resolve

Squash-merges one story worktree branch into the integration branch in the current main checkout. Resolves semantic conflicts inline if the mechanical squash leaves markers, then commits with the load-bearing `Squashed-story:` trailer that `teardown-worktrees.sh` keys off. All-or-nothing: either every guard passes, every marker resolves, verification passes, and one squash commit lands – or nothing changes on `BASE_BRANCH` and the worktree is preserved for inspection.

Internal skill (`user-invocable: false`). Sole caller: the `andthen:exec-plan` skill (team-mode Merge Wave, worktree mode), one invocation per story branch.

## Output Contract

Emit all four fields on every terminal path:

- `merge_resolve.outcome` – `resolved` | `failed` | `cancelled`
- `merge_resolve.conflicted_files` – JSON array of paths that carried conflict markers, sorted lexicographically; `[]` on clean squash or pre-squash termination
- `merge_resolve.resolution_summary` – prose: what was resolved and why, or what failed and where; `""` only if zero reasoning was produced before termination
- `merge_resolve.error_message` – `""` when `outcome: resolved`; otherwise the failure tag from the step that terminated (see step tables below)

## Inputs

Positional args (all required):

1. `STORY_ID` – bare plan id, e.g. `S03` (no `story-` prefix)
2. `BASE_BRANCH` – branch to merge into; must be currently checked out in CWD
3. `WORKTREE_PATH` – absolute path to the story worktree directory
4. `SUMMARY_FILE` – path to a file with the implementer's one-line completion summary. Empty / unreadable / blank → fallback subject `<STORY_ID>: completed (worktree merge)`.

Optional, repeatable:

- `--guard-path PATH` – paths whose diffs in the worktree branch are forbidden (typically `plan.json` and the State document). Enforces the orchestrator's `--defer-shared-writes` contract. Paths outside the repo's worktree are skipped automatically (multi-repo plan/state files live in a different repo and cannot leak here).

## Step 1 - Mechanical Squash with Guards

Invoke the deterministic guard-and-squash script:

```
bash ${CLAUDE_SKILL_DIR}/scripts/merge-worktree.sh <STORY_ID> <BASE_BRANCH> <WORKTREE_PATH> <SUMMARY_FILE> [--guard-path PATH ...]
```

The script runs, in order:

- **PRECONDITION** – CWD HEAD is on `BASE_BRANCH`, CWD's git common-dir matches the worktree's, main checkout is clean.
- **G1** – worktree branch carries ≥1 commit beyond merge-base with `BASE_BRANCH`. Catches worktree-routing failures (the teammate operated on the main checkout instead of the worktree).
- **G2** – worktree branch does not modify any `--guard-path` file (three-dot diff, immune to `BASE_BRANCH` advancing during the wave). Catches `--defer-shared-writes` violations.
- **G3** – worktree itself is clean (no uncommitted edits).
- **Squash** – `git merge --squash story-<STORY_ID>`.

The script does **not** commit. Final stdout line classifies the outcome:

| Final stdout line | Action |
|---|---|
| `SQUASH_OK` | Proceed to Step 3 (commit). |
| `SQUASH_CONFLICT` | Proceed to Step 2 (resolve). |
| `PRECONDITION_FAIL:<tag>` | Emit `outcome: failed`, `error_message: precondition:<tag>`. Stop. |
| `GUARD_FAIL:<tag>` | Emit `outcome: failed`, `error_message: guard:<tag>`. Stop. |
| `SQUASH_FAIL:<reason>` | Emit `outcome: failed`, `error_message: squash:<reason>`. Stop. |

Script exit code is non-zero for every status other than `SQUASH_OK` / `SQUASH_CONFLICT`; treat the stdout line as authoritative. On `SQUASH_FAIL` the script has already rolled back the partial squash on the main checkout (`git reset --hard HEAD`; `git merge --abort` does not work after `git merge --squash` because `--squash` suppresses `MERGE_HEAD`). The story branch is untouched in every failure path.

## Step 2 - Resolve Conflict Markers (only on `SQUASH_CONFLICT`)

Enumerate conflicted paths – this is the canonical source for `conflicted_files` (sort lexicographically):

```
git diff --name-only --diff-filter=U
```

For each file:

1. Locate every `<<<<<<<` / `=======` / `>>>>>>>` triplet.
2. Resolve each region by intent:
   - **Imports / use statements** → union both sides.
   - **Lock files / generated artifacts** → take the worktree branch's version.
   - **Logic conflicts** → preserve both behaviors when they compose. If sides are contradictory and tie-breaking cannot be derived from surrounding code, the FIS, or commit context: preserve a replay patch when useful, roll back the main checkout with `git reset --hard HEAD`, then emit `outcome: failed`, `error_message: logic_conflict:<file>:<line-range>`. Do not guess.
3. Rewrite the file with all markers removed.
4. `git add <file>`.

Accumulate one rationale per file for `resolution_summary`. After every file resolves, `git diff --name-only --diff-filter=U` must be empty – otherwise loop.

After `SQUASH_CONFLICT`, every failure or cancellation path must restore the main checkout before terminal output:

```
mkdir -p .agent_temp
git diff --staged > .agent_temp/merge-resolve-<STORY_ID>.patch
git diff >> .agent_temp/merge-resolve-<STORY_ID>.patch
git reset --hard HEAD
```

Write the replay patch only when it contains useful conflict-resolution work, and reference it in `resolution_summary`. This rollback is what lets the orchestrator preserve the story worktree and continue merging later stories without inheriting a dirty integration checkout.

## Step 2a - Verify (only on resolve path)

Run the project's verification commands from `CLAUDE.md` / `AGENTS.md` → `Key Dev Commands` (format, lint / analyze, type-check, test). Pre-existing failures unrelated to this merge: note in `resolution_summary`, do not swallow.

New failures attributable to the merge: fix-forward, re-run the full chain, retry at most twice. Still failing → emit `outcome: failed`, `error_message: verification:<which>`. Preserve the staged resolution as a replayable artifact before stopping:

```
mkdir -p .agent_temp
git diff --staged > .agent_temp/merge-resolve-<STORY_ID>.patch
```

Reference the path in `resolution_summary`. The orchestrator's failure-handling reads it to surface a replay hint to the user.

Then roll back the main checkout before emitting the failure:

```
git reset --hard HEAD
```

> **The `SQUASH_OK` path skips verify by design.** The worktree was already verified end-to-end by `andthen:exec-spec` and the squash content is byte-identical to the branch tip. Final Verification at the plan boundary (`andthen:exec-plan` Step 5) catches cross-story integration regressions.

## Step 3 - Commit

The commit message uses a load-bearing trailer that `teardown-worktrees.sh` keys off to classify the worktree as merged. Compose the subject from `SUMMARY_FILE` (first non-blank line); fall back to a default if empty:

```
SUMMARY=$(awk 'NF { print; exit }' "<SUMMARY_FILE>" 2>/dev/null || true)
: "${SUMMARY:=<STORY_ID>: completed (worktree merge)}"
printf 'story-%s: %s\n\nSquashed-story: %s\n' "<STORY_ID>" "$SUMMARY" "<STORY_ID>" \
  | git commit --cleanup=verbatim -F -
```

`printf | git commit -F -` keeps `SUMMARY` off the shell argument vector. `--cleanup=verbatim` preserves any `#`-led lines in the summary.

Commit failure (hook reject, signing key locked, commit-msg gate): roll back the staged squash on the main checkout, then emit failed:

```
git reset --hard HEAD
```

`git merge --abort` is not usable here because `git merge --squash` suppresses `MERGE_HEAD`. The story branch's commits are unaffected. Emit `outcome: failed`, `error_message: commit:<reason>`.

## Step 4 - Emit Output

On success:

```
merge_resolve.outcome: resolved
merge_resolve.conflicted_files: [...]   # [] on clean squash; sorted paths on resolve path
merge_resolve.resolution_summary: <non-empty prose>
merge_resolve.error_message: ""
```

On failure: emit the tag from the step that terminated (Step 1, 2, 2a, or 3). On cancellation (e.g. harness STOP between steps): if cancellation is observed after `SQUASH_CONFLICT`, first roll back the main checkout with `git reset --hard HEAD`; then emit `outcome: cancelled`, `error_message: cancelled`, conflicted_files = best-available from Step 2 (or `[]` if cancelled pre-detection).

## Absolute Prohibitions

On any failure or cancellation path the skill must NOT run:

- `git merge --abort` – suppressed by `--squash`; emits a misleading "no merge to abort" in logs
- `git reset` / `git restore` / `git checkout .` / `git clean` on the **worktree** or the **story branch** – preserved for inspection by design
- `git branch -D story-<STORY_ID>` – orchestrator owns teardown via `teardown-worktrees.sh`

The sanctioned exception is `git reset --hard HEAD` on the **main checkout** for rollback-only cleanup (Step 1's `SQUASH_FAIL` handling, already done by the script; Step 2 / 2a post-conflict failure or cancellation; Step 3's commit-failure rollback). The story branch is untouched in all cases.
