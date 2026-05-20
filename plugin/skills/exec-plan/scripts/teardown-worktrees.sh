#!/usr/bin/env bash
# teardown-worktrees.sh – Classify and clean up leftover story-* worktrees
# Used by: exec-plan (team mode, Final Worktree Teardown)

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: teardown-worktrees.sh BASE_BRANCH [--help]

Inventories and classifies leftover story-* worktrees after a team-mode run.
Must be run from CODE_DIR (the main checkout), not inside a story-* worktree
(git refuses to remove the worktree you are currently in).

For each leftover worktree:
  MERGED:<branch>              – squash-merged into BASE_BRANCH; worktree + branch removed
  MERGED_DIRTY:<branch>        – squashed, but worktree has uncommitted edits or post-squash commits; preserved
  MERGED_INDETERMINATE:<branch>:diff_rc=<n>
                               – squash matched but `git diff` exited ≥128 (git error,
                                 not 0/1); preserved pending inspection rather than
                                 misclassified as MERGED_DIRTY
  UNMERGED:<branch>            – not merged; preserved for manual inspection
  UNMERGED:<branch>:<reason>   – not merged AND a guard-failure marker was found (e.g.
                                 G1:empty_branch, G2:<paths>, G3:worktree_dirty written by
                                 the merge-resolve skill); preserved
  DETACHED:<path>              – detached HEAD (no branch line); preserved
  DETACHED:<path>:<reason>     – detached with a guard-failure marker; preserved

Classification:
  Test A (primary):  git log BASE_BRANCH -E --grep="^Squashed-story: STORY_ID$"
  Test B (fallback): git merge-base --is-ancestor (for --no-ff merges from older runs)
  Dirty checks:      git status --porcelain (uncommitted) and
                     git diff <squash-sha> <branch> (post-squash commits)

Exit codes:
  0  Classification complete; merged leftovers cleaned up
  2  Usage error (missing BASE_BRANCH argument)
  3  Git or parse error (corrupt porcelain output, git failure)
EOF
}

# ── Argument parsing ─────────────────────────────────────────────────────────

BASE_BRANCH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    -*) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
    *)
      if [[ -z "$BASE_BRANCH" ]]; then
        BASE_BRANCH="$1"
        shift
      else
        echo "Error: unexpected argument: $1" >&2
        usage >&2
        exit 2
      fi
      ;;
  esac
done

if [[ -z "$BASE_BRANCH" ]]; then
  echo "Error: BASE_BRANCH argument is required" >&2
  usage >&2
  exit 2
fi

# Validate BASE_BRANCH resolves
if ! git rev-parse --verify "$BASE_BRANCH" &>/dev/null; then
  echo "Error: BASE_BRANCH '$BASE_BRANCH' does not resolve to a git ref" >&2
  exit 3
fi

# Pre-flight: ensure pwd is the main checkout, not a linked worktree.
# `git worktree remove` refuses to remove the worktree you are currently in,
# so any classification that ends in cleanup would fail mid-run from inside
# a story-* worktree. Fail fast with a clear error instead.
MAIN_CHECKOUT=$(git worktree list --porcelain 2>/dev/null | awk '/^worktree / {print $2; exit}')
if [[ -z "$MAIN_CHECKOUT" ]]; then
  echo "Error: not inside a git repository" >&2
  exit 3
fi
PWD_ABS=$(cd "$PWD" && pwd -P)
MAIN_ABS=$(cd "$MAIN_CHECKOUT" && pwd -P)
if [[ "$PWD_ABS" != "$MAIN_ABS" ]]; then
  echo "Error: must be run from the main checkout (CODE_DIR), not a worktree or subdirectory" >&2
  echo "  pwd:            $PWD_ABS" >&2
  echo "  main checkout:  $MAIN_ABS" >&2
  exit 3
fi

# ── Porcelain parser ──────────────────────────────────────────────────────────

# Walk git worktree list --porcelain paragraph-by-paragraph.
# Each paragraph is blank-line separated; the first paragraph is always the main checkout.

WORKTREE_LIST_OUTPUT=""
if ! WORKTREE_LIST_OUTPUT=$(git worktree list --porcelain 2>&1); then
  echo "Error: git worktree list --porcelain failed: $WORKTREE_LIST_OUTPUT" >&2
  exit 3
fi

# Split into paragraphs (records) on blank lines
declare -a RECORDS=()
CURRENT_RECORD=""

while IFS= read -r line || [[ -n "$line" ]]; do
  if [[ -z "$line" ]]; then
    if [[ -n "$CURRENT_RECORD" ]]; then
      RECORDS+=("$CURRENT_RECORD")
      CURRENT_RECORD=""
    fi
  else
    CURRENT_RECORD="${CURRENT_RECORD:+$CURRENT_RECORD$'\n'}$line"
  fi
done <<< "$WORKTREE_LIST_OUTPUT"
# Flush final record
if [[ -n "$CURRENT_RECORD" ]]; then
  RECORDS+=("$CURRENT_RECORD")
fi

MAIN_CHECKOUT_SKIPPED=false

for RECORD in "${RECORDS[@]}"; do
  # Extract fields from the record
  WORKTREE_PATH=""
  WORKTREE_BRANCH=""
  IS_DETACHED=false

  while IFS= read -r field; do
    case "$field" in
      worktree\ *)   WORKTREE_PATH="${field#worktree }" ;;
      branch\ *)     WORKTREE_BRANCH="${field#branch refs/heads/}" ;;
      detached)      IS_DETACHED=true ;;
    esac
  done <<< "$RECORD"

  # Skip the main checkout (first record)
  if [[ "$MAIN_CHECKOUT_SKIPPED" == false ]]; then
    MAIN_CHECKOUT_SKIPPED=true
    continue
  fi

  # Determine if this is a leftover story-* worktree
  IS_STORY_BRANCH=false
  IS_STORY_DETACHED=false

  if [[ -n "$WORKTREE_BRANCH" && "$WORKTREE_BRANCH" == story-* ]]; then
    IS_STORY_BRANCH=true
  fi

  if [[ "$IS_DETACHED" == true && "$WORKTREE_PATH" == */.claude/worktrees/story-* ]]; then
    IS_STORY_DETACHED=true
  fi

  # Skip non-story worktrees
  if [[ "$IS_STORY_BRANCH" == false && "$IS_STORY_DETACHED" == false ]]; then
    continue
  fi

  # Marker-file short-circuit: when the merge-resolve skill's script wrote a guard-failure
  # marker, it explicitly preserved the worktree for inspection. Skip the
  # squash-trailer / ancestry classification entirely and emit UNMERGED with
  # the recorded reason. This is load-bearing: an empty story branch (G1
  # failure) is structurally indistinguishable from a fully-merged branch
  # because its tip IS the merge-base, so Test B below would misclassify it
  # as MERGED. The marker is the orchestrator's explicit "do not auto-clean".
  REASON=""
  if [[ -r "$WORKTREE_PATH/.andthen-fail-reason" ]]; then
    REASON=$(head -1 "$WORKTREE_PATH/.andthen-fail-reason" 2>/dev/null || true)
  fi
  if [[ -n "$REASON" ]]; then
    if [[ "$IS_DETACHED" == true || -z "$WORKTREE_BRANCH" ]]; then
      echo "DETACHED:${WORKTREE_PATH}:${REASON}"
      echo "  Preserved detached worktree: $WORKTREE_PATH (reason: $REASON)" >&2
    else
      echo "UNMERGED:${WORKTREE_BRANCH}:${REASON}"
      echo "  Preserved unmerged worktree: $WORKTREE_PATH (branch: $WORKTREE_BRANCH, reason: $REASON)" >&2
    fi
    continue
  fi

  # Detached short-circuit: no branch → DETACHED classification.
  if [[ "$IS_DETACHED" == true || -z "$WORKTREE_BRANCH" ]]; then
    echo "DETACHED:${WORKTREE_PATH}"
    echo "  Preserved detached worktree: $WORKTREE_PATH" >&2
    continue
  fi

  # Derive STORY_ID by stripping story- prefix
  STORY_ID="${WORKTREE_BRANCH#story-}"
  # Escape regex metachars before injecting into --grep. We pass -E (ERE) below
  # so the escape set covers ERE specials. Story IDs are S\d\d by contract;
  # this is defense-in-depth.
  STORY_ID_ESC=$(printf '%s' "$STORY_ID" | sed 's/[][\\^$.*?+(){}|]/\\&/g')

  # Test A: trailer match (primary, squash-aware). -E is explicit so the
  # ERE escape above is correct; without -E, git log defaults to BRE where
  # (){}|+? are literals and escaping them flips them to metachars.
  MERGED=false
  SQUASH_SHA=$(git log "$BASE_BRANCH" -E --grep="^Squashed-story: ${STORY_ID_ESC}$" --pretty=format:%H -n 1 2>/dev/null)
  if [[ -n "$SQUASH_SHA" ]]; then
    MERGED=true
  fi

  # Test B: SHA ancestry fallback (for --no-ff merges from older runs).
  # Empty branches (tip == merge-base, no commits beyond) are *vacuously*
  # ancestors of BASE_BRANCH and would be misclassified MERGED by a bare
  # is-ancestor check – but they carry no work to claim merged. The marker
  # short-circuit above catches G1-detected empties, but a hand-cleared
  # marker (or an empty branch from outside the merge-resolve skill) would slip
  # past it; gating on "carries ≥1 commit beyond merge-base" closes that hole.
  if [[ "$MERGED" == false ]]; then
    MERGE_BASE_TB=$(git merge-base "$BASE_BRANCH" "$WORKTREE_BRANCH" 2>/dev/null || true)
    if [[ -n "$MERGE_BASE_TB" ]]; then
      BRANCH_COMMITS=$(git rev-list --count "$MERGE_BASE_TB..$WORKTREE_BRANCH" 2>/dev/null || echo 0)
      if [[ "$BRANCH_COMMITS" -gt 0 ]] \
         && git merge-base --is-ancestor "$WORKTREE_BRANCH" "$BASE_BRANCH" 2>/dev/null; then
        MERGED=true
      fi
    fi
  fi

  if [[ "$MERGED" == true ]]; then
    # Dirty-tree check before --force: the squash-merge preserved the
    # committed work on BASE_BRANCH, but uncommitted post-merge edits in
    # the worktree are user state we should not destroy. Reclassify as
    # MERGED_DIRTY so the user can commit or discard explicitly.
    if [[ -n "$(git -C "$WORKTREE_PATH" status --porcelain 2>/dev/null)" ]]; then
      echo "MERGED_DIRTY:${WORKTREE_BRANCH}"
      echo "  Preserved merged-but-dirty worktree: $WORKTREE_PATH (branch: $WORKTREE_BRANCH); commit or discard local changes first" >&2
      continue
    fi

    # Post-squash divergence check: when Test A matched, we have the squash SHA.
    # If the branch tip's tree differs from the squash, the branch carries
    # commits made after the squash that are NOT on BASE_BRANCH. Same hazard:
    # `branch -D` would discard committed work.
    #
    # Capture the exit code explicitly: `git diff --quiet` returns 0 (no diff),
    # 1 (diff present), or ≥128 on a git error (lock contention, missing tree
    # in a partially deleted worktree, etc). Treating every non-zero exit as
    # "diff present" would misclassify clean merged worktrees as MERGED_DIRTY
    # on transient git noise – preserving orphans the orchestrator already
    # moved on from.
    if [[ -n "$SQUASH_SHA" ]]; then
      diff_rc=0
      git diff --quiet "$SQUASH_SHA" "$WORKTREE_BRANCH" 2>/dev/null || diff_rc=$?
      if [[ "$diff_rc" -eq 1 ]]; then
        echo "MERGED_DIRTY:${WORKTREE_BRANCH}"
        echo "  Preserved merged worktree with post-squash work: $WORKTREE_PATH (branch: $WORKTREE_BRANCH); rebase onto $BASE_BRANCH or discard before re-running" >&2
        continue
      elif [[ "$diff_rc" -ne 0 ]]; then
        echo "MERGED_INDETERMINATE:${WORKTREE_BRANCH}:diff_rc=$diff_rc"
        echo "  Preserved merged worktree pending diff-state inspection: git diff $SQUASH_SHA $WORKTREE_BRANCH returned exit $diff_rc (not 0/1)." >&2
        continue
      fi
    fi

    echo "MERGED:${WORKTREE_BRANCH}"
    echo "  Removing merged worktree: $WORKTREE_PATH (branch: $WORKTREE_BRANCH)" >&2

    # Remove worktree and branch
    if ! git worktree remove --force "$WORKTREE_PATH" >/dev/null 2>&1; then
      echo "Error: failed to remove worktree $WORKTREE_PATH" >&2
      exit 3
    fi
    if ! git branch -D "$WORKTREE_BRANCH" >/dev/null 2>&1; then
      echo "Error: failed to delete branch $WORKTREE_BRANCH" >&2
      exit 3
    fi
  else
    # Marker-file case is handled by the short-circuit higher up. Reaching
    # here means no marker and the branch isn't merged: a true UNMERGED.
    echo "UNMERGED:${WORKTREE_BRANCH}"
    echo "  Preserved unmerged worktree: $WORKTREE_PATH (branch: $WORKTREE_BRANCH)" >&2
  fi
done

# Hygiene: prune stale admin records
git worktree prune 2>/dev/null || true

exit 0
