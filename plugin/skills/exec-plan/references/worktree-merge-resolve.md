# Worktree Merge Resolve

Sub-agent procedure for resolving conflict markers produced by a squash-merge into `BASE_BRANCH`. Invoked from team-mode Merge Wave when `merge-worktree.sh` emits `SQUASH_CONFLICT`. **All-or-nothing**: resolve every marker, run the project's verification chain, commit with the load-bearing `Squashed-story:` trailer – or emit `outcome: failed` and leave the resolved index for inspection.

## Inputs (orchestrator-supplied)

- `STORY_ID`, `BASE_BRANCH`, `WORKTREE_PATH_ABS` (the source worktree, read-only here)
- `SUMMARY` – one-line completion summary used as the commit subject body in Step 5. Either the literal string or the path to a summary file (`.agent_temp/merge-summary-<STORY_ID>.txt`) the orchestrator already wrote. Empty / unreadable → fall back to `"<STORY_ID>: completed (worktree merge)"`.
- Project verification commands (build / lint / type-check / test) from `CLAUDE.md` → `Key Dev Commands`

## Procedure

### 1. Verify entry state

```
git status --porcelain | grep -E '^(UU|AA|DD|U |UD|AU)' | head -1
git rev-parse --abbrev-ref HEAD
```

- Empty unmerged-paths output → `outcome: cancelled`, `error: no_conflict_markers_present`, stop.
- Current branch ≠ `BASE_BRANCH` → `outcome: failed`, `error: wrong_branch:<actual>`, stop.

### 2. Enumerate conflicted files

```
git diff --name-only --diff-filter=U
```

Canonical source for `conflicted_files`. Sort lexicographically.

### 3. Resolve markers

For each conflicted file:

1. Locate every `<<<<<<<` / `=======` / `>>>>>>>` triplet.
2. For each region:
   - **Imports / use statements** → union both sides.
   - **Lock files / generated artifacts** → take the worktree branch's version.
   - **Logic conflicts** → reason about intent; preserve both behaviors where possible. If sides are contradictory and tie-break cannot be derived from surrounding code, FIS, or commit context → `outcome: failed`, `error: logic_conflict_in:<file>:<line-range>`, stop. Do not guess.
3. Rewrite the file with all markers removed.
4. `git add <file>`.

Accumulate one rationale per file for `resolution_summary`.

After resolving every file, `git diff --name-only --diff-filter=U` must be empty. Otherwise loop back.

### 4. Verify

Run every command from `Key Dev Commands`. Pre-existing failures unrelated to this merge are explicitly noted in `resolution_summary`, not swallowed. New failures attributable to the merge → fix-forward, re-run the entire verification chain, retry at most twice. Still failing → `outcome: failed`, `error: verification_failed:<which>:<output-tail>`, leave the index resolved, stop.

**Inter-attempt state contract.** Retries stack on prior fixes – the index + working tree carry over (rollback paths are prohibited, see below). If each retry surfaces a new downstream regression, the right move is `outcome: failed`, not continued drift: the orchestrator's post-failure rollback discards the accumulated state. Before emitting `outcome: failed`, preserve the staged resolution as `git diff --staged > .agent_temp/merge-resolve-{STORY_ID}.patch` and reference the file in `resolution_summary` – gives the user a replayable artifact for forensic / manual recovery.

### 5. Commit (all-or-nothing – only after verification passes)

```
# SUMMARY: the orchestrator-supplied input. If it names a readable file, take
# its first non-blank line (matches the convention in merge-worktree.sh).
# Otherwise treat it as the literal subject string. Empty / unreadable file /
# all-blank → fall back to the canonical default.
if [[ -n "${SUMMARY:-}" && -r "$SUMMARY" ]]; then
  SUMMARY=$(awk 'NF { print; exit }' "$SUMMARY")
fi
: "${SUMMARY:=${STORY_ID}: completed (worktree merge)}"
printf 'story-%s: %s\n\nSquashed-story: %s\n' "$STORY_ID" "$SUMMARY" "$STORY_ID" \
  | git commit --cleanup=verbatim -F -
```

`git commit -F -` so `SUMMARY` never reaches the shell argument vector. `--cleanup=verbatim` keeps `#`-led lines intact (default `strip` cleanup would drop a `# headline` SUMMARY's first line). Then emit `outcome: resolved`.

## Absolute prohibitions

Never on any failure or cancellation path:
- `git merge --abort` (orchestrator decides this).
- `git reset` (any form), `git checkout .` / `git restore .`, `git clean` (any form).
- `git branch -D story-<id>` (worktree branch is preserved on failure).

## Required outputs

Every terminal path emits:

```
merge_resolve.outcome: resolved | failed | cancelled
merge_resolve.conflicted_files: ["<path>", ...]    sorted; [] if cancelled before detection
merge_resolve.resolution_summary: <one paragraph per file + verification narrative; "" only if zero reasoning produced>
merge_resolve.error_message: <"" when resolved; otherwise the specific tag from steps 1/3/4>
```
