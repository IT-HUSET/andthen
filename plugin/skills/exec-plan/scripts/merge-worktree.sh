#!/usr/bin/env bash
# merge-worktree.sh – Squash-merge one story worktree into BASE_BRANCH with
# guard pre-checks and output-encoded status. Encapsulates Merge Wave step 1.
# Used by: exec-plan (team mode, Merge Wave) — one invocation per worktree.
#
# Pattern borrowed from dartclaw-merge-resolve: output-encoded status lines so
# the orchestrator (an LLM) can branch on them without relying on exit codes
# alone. All-or-nothing: a story either passes every guard and lands as a clean
# squash commit, or the worktree is preserved untouched for the user.
#
# Failure paths NEVER run `git reset --hard`, `git clean`, or `git branch -D`
# on the story branch or inside the worktree. The main checkout (CWD on
# BASE_BRANCH) MAY be `git reset --hard HEAD`-rolled-back to undo a partially
# applied squash: `git merge --squash` deliberately suppresses MERGE_HEAD, so
# `git merge --abort` fails with "no merge to abort" — `reset --hard HEAD` is
# the only mechanism that clears a staged-squash + dirty working tree on the
# main checkout. The story branch's commits are unaffected (the squash copied
# from it; resetting the main checkout doesn't touch the source).

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: merge-worktree.sh STORY_ID BASE_BRANCH WORKTREE_PATH SUMMARY_FILE [--guard-path PATH ...] [--help]

Performs the squash-merge of story-<STORY_ID> into BASE_BRANCH in the current
working directory's main checkout, gated by three pre-checks.

Arguments:
  STORY_ID       bare plan story id (e.g. S03; no story- prefix)
  BASE_BRANCH    branch to merge into; must be currently checked out in CWD
  WORKTREE_PATH  absolute path to the story-<STORY_ID> worktree
  SUMMARY_FILE   path to a file containing the implementer's completion summary
                 (one-line title used as the commit subject body). The path
                 argument is required; if the file is missing, empty, or
                 whitespace-only, a fallback subject is used.

Optional:
  --guard-path PATH  paths whose diffs in the worktree branch are forbidden
                     (typically the plan.json and State document). Repeatable.
                     Guard G2 fires if the worktree branch *itself* modified
                     any --guard-path file relative to the merge-base with
                     BASE_BRANCH (three-dot diff; immune to BASE_BRANCH
                     advancing during the wave). Absolute paths outside CODE_DIR
                     (e.g. multi-repo plan.json under PLAN_DIR) cannot be in the
                     branch's history; G2 skips them and emits a GUARD_SKIPPED:G2
                     line on stderr — informational, not a failure.

Pre-merge guards (run in order, fail-fast):
  PRECONDITION  CWD's HEAD must be on BASE_BRANCH AND main checkout must be
                clean (git status --porcelain empty)
  G1            worktree branch must carry at least one commit beyond
                merge-base (catches EnterWorktree routing failures: empty
                worktree branch means the teammate operated on the main
                checkout, not the worktree)
  G2            worktree branch must not modify any --guard-path file
                (catches violations of the --defer-shared-writes contract)
  G3            worktree status --porcelain must be empty (uncommitted edits
                in the worktree)

Stdout (one line per stage; the orchestrator parses these):
  PRECONDITION_FAIL:not_in_git_repo
  PRECONDITION_FAIL:repo_mismatch:<cwd-common-dir>
  PRECONDITION_FAIL:wrong_branch:<actual>
  PRECONDITION_FAIL:main_checkout_dirty
  GUARD_FAIL:G1:no_merge_base
  GUARD_FAIL:G1:empty_branch
  GUARD_FAIL:G2:<colon-separated leaked paths>
  GUARD_FAIL:G3:worktree_dirty
  COMMIT_FAIL:g2_git_error:<path>:rc=<n>  G2 diff returned exit ≥128 (git error,
                                          not a clean 0/1) — refusing to
                                          classify as leak; investigate.
  SQUASH_OK                       mechanical squash succeeded
  SQUASH_CONFLICT                 squash produced conflict markers; orchestrator must invoke worktree-merge-resolve.md
  COMMIT_OK                       commit landed on BASE_BRANCH
  COMMIT_FAIL:<reason>            commit step failed (squash-failed or commit-failed)

Exit codes:
  0  full success (SQUASH_OK + COMMIT_OK)
  2  usage error
  3  any guard or stage failure (stdout carries the structured reason)
EOF
}

STORY_ID=""
BASE_BRANCH=""
WORKTREE_PATH=""
SUMMARY_FILE=""
GUARD_PATHS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --guard-path)
      shift
      if [[ $# -eq 0 ]]; then
        echo "Error: --guard-path requires a value" >&2
        exit 2
      fi
      GUARD_PATHS+=("$1")
      shift
      ;;
    -*) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
    *)
      if   [[ -z "$STORY_ID" ]];      then STORY_ID="$1"
      elif [[ -z "$BASE_BRANCH" ]];   then BASE_BRANCH="$1"
      elif [[ -z "$WORKTREE_PATH" ]]; then WORKTREE_PATH="$1"
      elif [[ -z "$SUMMARY_FILE" ]];  then SUMMARY_FILE="$1"
      else
        echo "Error: unexpected positional argument: $1" >&2
        usage >&2
        exit 2
      fi
      shift
      ;;
  esac
done

if [[ -z "$STORY_ID" || -z "$BASE_BRANCH" || -z "$WORKTREE_PATH" || -z "$SUMMARY_FILE" ]]; then
  echo "Error: STORY_ID, BASE_BRANCH, WORKTREE_PATH, and SUMMARY_FILE are all required" >&2
  usage >&2
  exit 2
fi

BRANCH="story-$STORY_ID"

if [[ ! -d "$WORKTREE_PATH" ]]; then
  echo "Error: WORKTREE_PATH '$WORKTREE_PATH' does not exist" >&2
  exit 3
fi

if ! git rev-parse --verify "$BASE_BRANCH" >/dev/null 2>&1; then
  echo "Error: BASE_BRANCH '$BASE_BRANCH' does not resolve to a git ref" >&2
  exit 3
fi
if ! git rev-parse --verify "refs/heads/$BRANCH" >/dev/null 2>&1; then
  echo "Error: branch '$BRANCH' does not exist" >&2
  exit 3
fi

# Persist guard failure reasons next to the worktree so teardown-worktrees.sh
# can surface them in the final classification.
_mark_failure() {
  _mf_reason="$1"
  printf '%s\n' "$_mf_reason" > "$WORKTREE_PATH/.andthen-fail-reason" 2>/dev/null || true
}

# ── PRECONDITION: CWD HEAD is BASE_BRANCH, main checkout clean ───────────────
# Repo identity first: CWD must share a common git dir with WORKTREE_PATH.
# Without this, a multi-repo CWD-drift would happily squash the worktree's
# branch into whatever BASE_BRANCH happens to resolve in CWD's *other* repo
# (e.g. a coincidentally-named `story-S03` across runs/repos).
CWD_COMMON_DIR=$(git rev-parse --git-common-dir 2>/dev/null || true)
WT_COMMON_DIR=$(git -C "$WORKTREE_PATH" rev-parse --git-common-dir 2>/dev/null || true)
if [[ -z "$CWD_COMMON_DIR" || -z "$WT_COMMON_DIR" ]]; then
  echo "PRECONDITION_FAIL:not_in_git_repo"
  echo "  CWD or WORKTREE_PATH is not inside a git checkout." >&2
  exit 3
fi
# Canonicalize before comparing — relative paths and symlinks would otherwise
# trigger a false mismatch. If `cd` fails (dir missing, permissions), classify
# as not_in_git_repo rather than falling back to the raw value: a relative
# common-dir compared against an absolute one would silently misfire as
# `repo_mismatch`, sending the user down the wrong investigation path.
if ! CWD_COMMON_ABS=$(cd "$CWD_COMMON_DIR" 2>/dev/null && pwd -P); then
  echo "PRECONDITION_FAIL:not_in_git_repo"
  echo "  CWD's git common-dir '$CWD_COMMON_DIR' is not accessible." >&2
  exit 3
fi
if ! WT_COMMON_ABS=$(cd "$WT_COMMON_DIR" 2>/dev/null && pwd -P); then
  echo "PRECONDITION_FAIL:not_in_git_repo"
  echo "  Worktree's git common-dir '$WT_COMMON_DIR' is not accessible." >&2
  exit 3
fi
if [[ "$CWD_COMMON_ABS" != "$WT_COMMON_ABS" ]]; then
  echo "PRECONDITION_FAIL:repo_mismatch:$CWD_COMMON_ABS"
  echo "  CWD's git common-dir is '$CWD_COMMON_ABS'; worktree's is '$WT_COMMON_ABS'." >&2
  echo "  Refusing to squash-merge: CWD is the wrong repo for $WORKTREE_PATH." >&2
  exit 3
fi

# Branch identity next: if HEAD is on a different branch, every later step
# (squash, commit, trailer write) would land on the wrong branch silently.
ACTUAL_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)
if [[ "$ACTUAL_BRANCH" != "$BASE_BRANCH" ]]; then
  echo "PRECONDITION_FAIL:wrong_branch:$ACTUAL_BRANCH"
  echo "  CWD HEAD is on '$ACTUAL_BRANCH'; expected '$BASE_BRANCH'." >&2
  echo "  Refusing to squash-merge: the commit would land on the wrong branch." >&2
  exit 3
fi
if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
  echo "PRECONDITION_FAIL:main_checkout_dirty"
  echo "  Main checkout has uncommitted changes; refusing to squash-merge." >&2
  echo "  Run \`git status\` in CWD and investigate before retrying." >&2
  exit 3
fi

# ── G1: worktree branch carries at least one commit beyond merge-base ────────
MERGE_BASE=$(git merge-base "$BASE_BRANCH" "$BRANCH" 2>/dev/null || true)
if [[ -z "$MERGE_BASE" ]]; then
  echo "GUARD_FAIL:G1:no_merge_base"
  echo "  Could not resolve merge-base for $BASE_BRANCH..$BRANCH" >&2
  _mark_failure "G1:no_merge_base"
  exit 3
fi
COMMIT_COUNT=$(git rev-list --count "$MERGE_BASE..$BRANCH" 2>/dev/null || echo 0)
if [[ "$COMMIT_COUNT" -lt 1 ]]; then
  echo "GUARD_FAIL:G1:empty_branch"
  echo "  Worktree branch $BRANCH has zero commits beyond merge-base $MERGE_BASE." >&2
  echo "  The implementer likely operated on the main checkout instead of the worktree" >&2
  echo "  (worktree-routing failure: harness isolation bypassed)." >&2
  _mark_failure "G1:empty_branch"
  exit 3
fi

# ── G2: no diffs against forbidden guard paths ──────────────────────────────
# Three-dot range (A...B) diffs the merge-base of A and B against B — i.e.
# "what did this branch change?" Two-dot (A..B) would also report changes
# made on A *after* the branch split, which here is exactly the case when
# the previous story in this wave squash-merged and committed deferred
# plan.json/STATE writes onto BASE_BRANCH: every still-pending wave story
# would falsely fail G2 with plan.json/STATE listed as "leaked".
if [[ ${#GUARD_PATHS[@]} -gt 0 ]]; then
  # Multi-repo defense: in `PLAN_DIR ≠ CODE_DIR` setups the orchestrator may
  # still pass `--guard-path {PLAN_FILE_PATH}` where {PLAN_FILE_PATH} is outside
  # CODE_DIR's worktree. `git diff` would silently return empty for such paths
  # (nothing tracked there), making G2 a no-op for the multi-repo plan file.
  # Surface non-repo-relative guard paths explicitly so the orchestrator can
  # decide whether to drop them or stop-the-line.
  REPO_TOPLEVEL=$(git rev-parse --show-toplevel 2>/dev/null || true)
  if [[ -n "$REPO_TOPLEVEL" ]]; then
    REPO_TOPLEVEL_ABS=$(cd "$REPO_TOPLEVEL" && pwd -P)
    SKIPPED_GUARDS=()
    FILTERED_GUARDS=()
    for gp in "${GUARD_PATHS[@]}"; do
      if [[ "$gp" = /* ]]; then
        # Absolute path: check membership.
        case "$gp/" in
          "$REPO_TOPLEVEL_ABS"/*) FILTERED_GUARDS+=("$gp") ;;
          *) SKIPPED_GUARDS+=("$gp") ;;
        esac
      else
        # Relative path: assume repo-relative (git diff resolves it that way).
        FILTERED_GUARDS+=("$gp")
      fi
    done
    if [[ ${#SKIPPED_GUARDS[@]} -gt 0 ]]; then
      SKIPPED_JOINED=$(IFS=:; printf '%s' "${SKIPPED_GUARDS[*]}")
      echo "GUARD_SKIPPED:G2:$SKIPPED_JOINED" >&2
      echo "  Guard paths outside CODE_DIR ($REPO_TOPLEVEL_ABS) — G2 cannot check them:" >&2
      for p in "${SKIPPED_GUARDS[@]}"; do echo "    $p" >&2; done
      echo "  Multi-repo plan/state files are outside CODE_DIR's history and cannot be leaked into a story branch, so this is informational, not a failure." >&2
    fi
    # Safe assignment under set -u: empty source array would error on bare
    # "${arr[@]}" expansion in pre-4.4 bash. The length check below also
    # tolerates the empty case naturally.
    if [[ ${#FILTERED_GUARDS[@]} -gt 0 ]]; then
      GUARD_PATHS=("${FILTERED_GUARDS[@]}")
    else
      GUARD_PATHS=()
    fi
  fi
fi

if [[ ${#GUARD_PATHS[@]} -gt 0 ]]; then
  LEAKED=()
  for gp in "${GUARD_PATHS[@]}"; do
    # `git diff --quiet` exits 0 (no diff), 1 (diff present), or ≥128 (git error:
    # lock contention, corrupt object, invalid pathspec, etc). Treating every
    # non-zero exit as "leaked" would misclassify a transient git error as a
    # shared-file-leak — the worst kind of false positive (freezes the worktree
    # under FAILED:shared-file-leak-into-branch with a marker the user must
    # clear). Capture the exit code explicitly and branch only on 1.
    rc=0
    git diff --quiet "$BASE_BRANCH...$BRANCH" -- "$gp" 2>/dev/null || rc=$?
    if [[ "$rc" -eq 1 ]]; then
      LEAKED+=("$gp")
    elif [[ "$rc" -ne 0 ]]; then
      echo "COMMIT_FAIL:g2_git_error:$gp:rc=$rc"
      echo "  G2 git diff returned exit $rc for guard path '$gp' — not a clean 0/1 result." >&2
      echo "  Refusing to classify as leak; investigate (lock contention? invalid path? corrupt object?)." >&2
      _mark_failure "g2-git-error:$gp:rc=$rc"
      exit 3
    fi
  done
  if [[ ${#LEAKED[@]} -gt 0 ]]; then
    # Subshell so `IFS=:` does not leak globally — the unsuffixed form
    # `IFS=: VAR=…` with no command is two persistent assignments, not a
    # single-command env override.
    LEAKED_JOINED=$(IFS=:; printf '%s' "${LEAKED[*]}")
    echo "GUARD_FAIL:G2:$LEAKED_JOINED"
    echo "  Worktree branch contains forbidden diffs against shared-write paths:" >&2
    for p in "${LEAKED[@]}"; do echo "    $p" >&2; done
    echo "  The implementer ignored the --defer-shared-writes contract." >&2
    _mark_failure "G2:$LEAKED_JOINED"
    exit 3
  fi
fi

# ── G3: worktree status clean ────────────────────────────────────────────────
if [[ -n "$(git -C "$WORKTREE_PATH" status --porcelain 2>/dev/null)" ]]; then
  echo "GUARD_FAIL:G3:worktree_dirty"
  echo "  Worktree $WORKTREE_PATH has uncommitted edits." >&2
  _mark_failure "G3:worktree_dirty"
  exit 3
fi

# ── Squash ──────────────────────────────────────────────────────────────────
SQUASH_ERR=""
if SQUASH_ERR=$(git merge --squash "$BRANCH" 2>&1); then
  echo "SQUASH_OK"
else
  # Detect conflict vs other failures. With --squash, `git merge` exits non-zero
  # on conflict and leaves the index in a partially-merged state with markers.
  # Avoid `… | head -1 | grep -q .` — under `set -euo pipefail`, `head -1`
  # closing the pipe early can propagate SIGPIPE-141, flipping the conflict
  # branch to its else (and triggering `git merge --abort`, destroying the
  # index the orchestrator needs to inspect). Capture once and test.
  if [[ -n "$(git ls-files --unmerged 2>/dev/null)" ]]; then
    echo "SQUASH_CONFLICT"
    echo "  Squash produced conflict markers; orchestrator must invoke worktree-merge-resolve.md before retry." >&2
    # Do NOT `git merge --abort` here: the orchestrator's semantic-merge
    # sub-agent reads the conflicted index to resolve. The orchestrator
    # decides cleanup on resolve-failure (preserve or abort), not us.
    exit 3
  else
    echo "COMMIT_FAIL:squash_failed:$SQUASH_ERR"
    # No conflict markers but squash failed → revert any staged state so the
    # main checkout is left clean. `git merge --abort` does NOT work after
    # `git merge --squash` (--squash suppresses MERGE_HEAD by design); use
    # `git reset --hard HEAD` to clear any partial squash from the main
    # checkout. The story branch is untouched (squash copied from it).
    git reset --hard HEAD >/dev/null 2>&1 || true
    _mark_failure "commit-fail:squash_failed:$SQUASH_ERR"
    exit 3
  fi
fi

# ── Compose commit subject from SUMMARY_FILE ────────────────────────────────
SUMMARY=""
if [[ -s "$SUMMARY_FILE" ]]; then
  # Take only the first non-blank line as the commit subject body. The full
  # summary is implementer prose and may run long; the orchestrator owns the
  # multi-line completion record elsewhere.
  SUMMARY=$(awk 'NF { print; exit }' "$SUMMARY_FILE" || true)
fi
if [[ -z "$SUMMARY" ]]; then
  SUMMARY="$STORY_ID: completed (worktree merge)"
fi

# ── Commit ───────────────────────────────────────────────────────────────────
# printf %s does no metacharacter expansion on the substituted value, and
# `git commit -F -` reads the message as a byte stream — SUMMARY never reaches
# the shell argument vector. The `Squashed-story: <id>` trailer is load-bearing:
# teardown-worktrees.sh uses it to classify a worktree as merged.
# `--cleanup=verbatim` keeps `#`-led lines intact: a SUMMARY first-line such
# as `# headline` would otherwise be dropped by git's default `strip` cleanup
# and leave the commit subject `story-<id>:` with no description.
COMMIT_ERR=""
if ! COMMIT_ERR=$(printf 'story-%s: %s\n\nSquashed-story: %s\n' \
      "$STORY_ID" "$SUMMARY" "$STORY_ID" \
      | git commit --cleanup=verbatim -F - 2>&1); then
  echo "COMMIT_FAIL:commit_failed:$COMMIT_ERR"
  # Squash succeeded but commit failed (hook rejected, signing key locked,
  # commit-msg gate failed, etc). Without rolling back, the index + working
  # tree carry the staged squash, dirtying the main checkout — the very state
  # PRECONDITION refuses on the next invocation, and the per-wave main-checkout
  # audit would misattribute the dirty tree to a teammate leak. `git merge
  # --abort` does NOT work after `git merge --squash` (--squash suppresses
  # MERGE_HEAD), so use `git reset --hard HEAD` to clear the staged squash
  # from the main checkout. The story branch is untouched.
  git reset --hard HEAD >/dev/null 2>&1 || true
  _mark_failure "commit-fail:commit_failed:$COMMIT_ERR"
  exit 3
fi

echo "COMMIT_OK"
exit 0
