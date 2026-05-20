#!/usr/bin/env bash
# merge-worktree.sh – Squash-merge one story worktree into BASE_BRANCH after
# precondition + guard checks. Stops after the mechanical squash; the caller
# (andthen:merge-resolve skill) owns commit and conflict-resolution.
#
# Output-encoded status lines on stdout: the caller (an LLM-driven skill) parses
# the final line. Exit codes are secondary; treat stdout as authoritative.
#
# Failure paths NEVER run `git reset --hard`, `git clean`, or `git branch -D`
# on the story branch or inside the worktree. The main checkout (CWD on
# BASE_BRANCH) MAY be `git reset --hard HEAD`-rolled back to undo a partially
# applied squash on SQUASH_FAIL: `git merge --squash` suppresses MERGE_HEAD,
# so `git merge --abort` would fail with "no merge to abort".

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: merge-worktree.sh STORY_ID BASE_BRANCH WORKTREE_PATH SUMMARY_FILE [--guard-path PATH ...] [--help]

Runs PRECONDITION → G1 → G2 → G3 → `git merge --squash story-<STORY_ID>` from
the current main checkout (CWD must be on BASE_BRANCH). Does NOT commit – the
caller commits after Step 3 (or after Step 2's conflict resolution + Step 2a
verification, in the andthen:merge-resolve skill).

Arguments:
  STORY_ID       bare plan story id (e.g. S03; no story- prefix)
  BASE_BRANCH    branch to merge into; must be currently checked out in CWD
  WORKTREE_PATH  absolute path to the story-<STORY_ID> worktree
  SUMMARY_FILE   path to a file with the implementer's completion summary.
                 Passed through for the caller's commit step; this script does
                 not consume it. Path argument is required; the file itself
                 may be missing/empty (caller falls back to a default subject).

Optional, repeatable:
  --guard-path PATH  paths whose diffs in the worktree branch are forbidden
                     (typically plan.json and the State document). G2 uses a
                     three-dot diff so it is immune to BASE_BRANCH advancing
                     during the wave. Absolute paths outside the repo's
                     worktree are skipped automatically with a stderr note.

Stdout (final line is authoritative):
  SQUASH_OK                  mechanical squash succeeded, index staged
  SQUASH_CONFLICT            squash produced conflict markers; caller resolves
  PRECONDITION_FAIL:<tag>    where <tag> ∈ {missing_worktree,
                             missing_base_branch, missing_story_branch,
                             not_in_git_repo, repo_mismatch:<path>,
                             wrong_branch:<actual>, main_checkout_dirty,
                             g2_git_error:<path>:rc=<n>}
  GUARD_FAIL:<tag>           where <tag> ∈ {G1:no_merge_base, G1:empty_branch,
                             G2:<colon-separated paths>, G3:worktree_dirty}
  SQUASH_FAIL:<reason>       squash failed (non-conflict); main checkout rolled
                             back via `git reset --hard HEAD`

Exit codes:
  0  SQUASH_OK or SQUASH_CONFLICT (mechanical step ran to its end)
  2  usage error
  3  any precondition/guard/squash failure (stdout carries the structured reason)
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
  echo "PRECONDITION_FAIL:missing_worktree"
  echo "  WORKTREE_PATH '$WORKTREE_PATH' does not exist." >&2
  exit 3
fi
if ! git rev-parse --verify "$BASE_BRANCH" >/dev/null 2>&1; then
  echo "PRECONDITION_FAIL:missing_base_branch"
  echo "  BASE_BRANCH '$BASE_BRANCH' does not resolve to a git ref." >&2
  exit 3
fi
if ! git rev-parse --verify "refs/heads/$BRANCH" >/dev/null 2>&1; then
  echo "PRECONDITION_FAIL:missing_story_branch"
  echo "  Branch '$BRANCH' does not exist." >&2
  exit 3
fi

# Persist guard-failure reasons next to the worktree so teardown-worktrees.sh
# can surface them in the final classification as UNMERGED:<branch>:<reason>.
_mark_failure() {
  printf '%s\n' "$1" > "$WORKTREE_PATH/.andthen-fail-reason" 2>/dev/null || true
}

# ── PRECONDITION: CWD HEAD is BASE_BRANCH, main checkout clean ───────────────
# Repo identity first: CWD must share a common git dir with WORKTREE_PATH.
# Without this, a multi-repo CWD drift would squash the worktree's branch into
# whatever BASE_BRANCH happens to resolve in CWD's other repo.
CWD_COMMON_DIR=$(git rev-parse --git-common-dir 2>/dev/null || true)
WT_COMMON_DIR=$(git -C "$WORKTREE_PATH" rev-parse --git-common-dir 2>/dev/null || true)
if [[ -z "$CWD_COMMON_DIR" || -z "$WT_COMMON_DIR" ]]; then
  echo "PRECONDITION_FAIL:not_in_git_repo"
  exit 3
fi
CWD_COMMON_ABS=$(cd "$CWD_COMMON_DIR" 2>/dev/null && pwd -P) || {
  echo "PRECONDITION_FAIL:not_in_git_repo"; exit 3; }
WT_COMMON_ABS=$(cd "$WT_COMMON_DIR" 2>/dev/null && pwd -P) || {
  echo "PRECONDITION_FAIL:not_in_git_repo"; exit 3; }
if [[ "$CWD_COMMON_ABS" != "$WT_COMMON_ABS" ]]; then
  echo "PRECONDITION_FAIL:repo_mismatch:$CWD_COMMON_ABS"
  echo "  CWD git common-dir is '$CWD_COMMON_ABS'; worktree's is '$WT_COMMON_ABS'." >&2
  exit 3
fi

ACTUAL_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)
if [[ "$ACTUAL_BRANCH" != "$BASE_BRANCH" ]]; then
  echo "PRECONDITION_FAIL:wrong_branch:$ACTUAL_BRANCH"
  exit 3
fi
if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
  echo "PRECONDITION_FAIL:main_checkout_dirty"
  exit 3
fi

# ── G1: worktree branch carries at least one commit beyond merge-base ────────
MERGE_BASE=$(git merge-base "$BASE_BRANCH" "$BRANCH" 2>/dev/null || true)
if [[ -z "$MERGE_BASE" ]]; then
  echo "GUARD_FAIL:G1:no_merge_base"
  _mark_failure "G1:no_merge_base"
  exit 3
fi
COMMIT_COUNT=$(git rev-list --count "$MERGE_BASE..$BRANCH" 2>/dev/null || echo 0)
if [[ "$COMMIT_COUNT" -lt 1 ]]; then
  echo "GUARD_FAIL:G1:empty_branch"
  echo "  Worktree branch $BRANCH has zero commits beyond merge-base – likely a worktree-routing failure." >&2
  _mark_failure "G1:empty_branch"
  exit 3
fi

# ── G2: no diffs against forbidden guard paths ──────────────────────────────
# Three-dot range (A...B) diffs the merge-base of A and B against B (changes
# made on this branch). Two-dot would falsely fail when a prior wave story's
# deferred plan.json/STATE commit advanced BASE_BRANCH.
#
# Multi-repo defense: guard paths absolute and outside the repo's worktree
# cannot be in this repo's history; skip them with an informational stderr
# note rather than misfiring G2 as a no-op leak check.
if [[ ${#GUARD_PATHS[@]} -gt 0 ]]; then
  REPO_TOPLEVEL=$(git rev-parse --show-toplevel 2>/dev/null || true)
  if [[ -n "$REPO_TOPLEVEL" ]]; then
    REPO_TOPLEVEL_ABS=$(cd "$REPO_TOPLEVEL" && pwd -P)
    FILTERED_GUARDS=()
    SKIPPED_GUARDS=()
    for gp in "${GUARD_PATHS[@]}"; do
      if [[ "$gp" = /* ]]; then
        case "$gp/" in
          "$REPO_TOPLEVEL_ABS"/*) FILTERED_GUARDS+=("$gp") ;;
          *) SKIPPED_GUARDS+=("$gp") ;;
        esac
      else
        FILTERED_GUARDS+=("$gp")
      fi
    done
    if [[ ${#SKIPPED_GUARDS[@]} -gt 0 ]]; then
      SKIPPED_JOINED=$(IFS=:; printf '%s' "${SKIPPED_GUARDS[*]}")
      echo "GUARD_SKIPPED:G2:$SKIPPED_JOINED" >&2
    fi
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
    if DIFF_ERR=$(git diff --quiet "$BASE_BRANCH...$BRANCH" -- "$gp" 2>&1); then
      diff_rc=0
    else
      diff_rc=$?
    fi
    case "$diff_rc" in
      0) ;;
      1) LEAKED+=("$gp") ;;
      *)
        echo "PRECONDITION_FAIL:g2_git_error:$gp:rc=$diff_rc"
        if [[ -n "$DIFF_ERR" ]]; then
          printf '  git diff failed for guard path %q: %s\n' "$gp" "$DIFF_ERR" >&2
        else
          printf '  git diff failed for guard path %q with rc=%s.\n' "$gp" "$diff_rc" >&2
        fi
        exit 3
        ;;
    esac
  done
  if [[ ${#LEAKED[@]} -gt 0 ]]; then
    LEAKED_JOINED=$(IFS=:; printf '%s' "${LEAKED[*]}")
    echo "GUARD_FAIL:G2:$LEAKED_JOINED"
    echo "  Worktree branch contains forbidden diffs against shared-write paths." >&2
    _mark_failure "G2:$LEAKED_JOINED"
    exit 3
  fi
fi

# ── G3: worktree status clean ────────────────────────────────────────────────
if [[ -n "$(git -C "$WORKTREE_PATH" status --porcelain 2>/dev/null)" ]]; then
  echo "GUARD_FAIL:G3:worktree_dirty"
  _mark_failure "G3:worktree_dirty"
  exit 3
fi

# ── Squash ──────────────────────────────────────────────────────────────────
SQUASH_ERR=""
if SQUASH_ERR=$(git merge --squash "$BRANCH" 2>&1); then
  echo "SQUASH_OK"
  exit 0
fi

# Detect conflict vs other failure. Avoid `… | head -1 | grep -q .` – under
# `set -euo pipefail`, an early-close pipe can propagate SIGPIPE-141 and flip
# the conflict branch (destroying the index the caller needs to inspect).
if [[ -n "$(git ls-files --unmerged 2>/dev/null)" ]]; then
  echo "SQUASH_CONFLICT"
  # Do NOT `git merge --abort` here: the caller reads the conflicted index to
  # resolve markers and decides cleanup on resolve-failure.
  exit 0
fi

echo "SQUASH_FAIL:$SQUASH_ERR"
# Non-conflict squash failure → roll back any staged state so the main
# checkout is left clean. `git merge --abort` does NOT work after `git merge
# --squash` (suppresses MERGE_HEAD); `git reset --hard HEAD` clears partial
# squash from the main checkout. The story branch is untouched.
git reset --hard HEAD >/dev/null 2>&1 || true
_mark_failure "squash-fail:$SQUASH_ERR"
exit 3
