#!/usr/bin/env bash
# create-worktree.sh – Create an isolated story-* worktree for team-mode exec-plan.
# Used by: exec-plan (team mode, Step 3T pre-spawn)
#
# Bash-driven worktree creation is the contract: harness isolation under
# `team_name` is unreliable, so pre-creating the worktree and forcing the
# teammate into it via prompt prelude + absolute paths is the only way to
# guarantee isolation.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: create-worktree.sh STORY_ID BASE_BRANCH CODE_DIR [--help]

Creates an isolated git worktree for one story in team-mode exec-plan.

Arguments:
  STORY_ID     bare plan story id, e.g. S03 (no story- prefix)
  BASE_BRANCH  branch to start the worktree from (resolved at run start)
  CODE_DIR     absolute path to the main code repo checkout

Behavior:
  1. Validate args; reject pre-existing branch story-<STORY_ID> (use teardown first).
  2. git worktree add CODE_DIR/.claude/worktrees/story-<STORY_ID> -b story-<STORY_ID> BASE_BRANCH
  3. If CODE_DIR/.gitmodules exists, run `git submodule update --init --recursive`
     inside the new worktree. `git worktree add` does not init submodules.
  4. Ensure `.claude/worktrees/` is excluded from main-checkout git status via
     CODE_DIR/.git/info/exclude (local-only; no commit, no .gitignore mutation).

Stdout (machine-readable):
  WORKTREE_PATH=<absolute path>   on success

Exit codes:
  0  worktree created
  2  usage error (missing/invalid arguments)
  3  git error, pre-existing branch, or filesystem failure
EOF
}

# Roll back a partially created worktree on failure. Uses globals CODE_DIR_ABS,
# WORKTREE_PATH, BRANCH which are set before any call site. Best-effort: a
# failed rollback should not mask the original error.
_rollback_worktree() {
  git -C "$CODE_DIR_ABS" worktree remove --force "$WORKTREE_PATH" >/dev/null 2>&1 || true
  git -C "$CODE_DIR_ABS" branch -D "$BRANCH" >/dev/null 2>&1 || true
}

STORY_ID=""
BASE_BRANCH=""
CODE_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    -*) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
    *)
      if [[ -z "$STORY_ID" ]]; then STORY_ID="$1"
      elif [[ -z "$BASE_BRANCH" ]]; then BASE_BRANCH="$1"
      elif [[ -z "$CODE_DIR" ]]; then CODE_DIR="$1"
      else
        echo "Error: unexpected argument: $1" >&2
        usage >&2
        exit 2
      fi
      shift
      ;;
  esac
done

if [[ -z "$STORY_ID" || -z "$BASE_BRANCH" || -z "$CODE_DIR" ]]; then
  echo "Error: STORY_ID, BASE_BRANCH, and CODE_DIR are all required" >&2
  usage >&2
  exit 2
fi

# Story ids are alphanumeric + hyphen by plan-schema contract; reject anything
# else so shell-escaping concerns downstream stay theoretical.
if ! [[ "$STORY_ID" =~ ^[A-Za-z0-9-]+$ ]]; then
  echo "Error: STORY_ID '$STORY_ID' contains characters outside [A-Za-z0-9-]" >&2
  exit 2
fi

# Defense-in-depth: the `impl-` / `review-` prefixes are team task-name shapes,
# not story ids. Accepting them here silently would create branches named
# `story-impl-S03` that disagree with the Squashed-story trailer and downstream
# tooling. Caller must pass the bare plan story id.
if [[ "$STORY_ID" == impl-* || "$STORY_ID" == review-* ]]; then
  echo "Error: STORY_ID '$STORY_ID' looks like a team task name; pass the bare plan story id (e.g. S03), not the full team task name (e.g. impl-S03)." >&2
  exit 2
fi

if [[ ! -d "$CODE_DIR/.git" && ! -f "$CODE_DIR/.git" ]]; then
  echo "Error: CODE_DIR '$CODE_DIR' is not a git checkout" >&2
  exit 2
fi

CODE_DIR_ABS=$(cd "$CODE_DIR" && pwd -P)

if ! git -C "$CODE_DIR_ABS" rev-parse --verify "$BASE_BRANCH" >/dev/null 2>&1; then
  echo "Error: BASE_BRANCH '$BASE_BRANCH' does not resolve to a git ref in $CODE_DIR_ABS" >&2
  exit 3
fi

BRANCH="story-$STORY_ID"
WORKTREE_PATH="$CODE_DIR_ABS/.claude/worktrees/$BRANCH"

# Pre-existing branch is an explicit failure: a leftover from a previous run
# means teardown didn't complete. Surfacing this loudly is the contract.
if git -C "$CODE_DIR_ABS" show-ref --verify --quiet "refs/heads/$BRANCH"; then
  echo "Error: branch '$BRANCH' already exists in $CODE_DIR_ABS — run teardown-worktrees.sh first, or remove it manually" >&2
  exit 3
fi

# Pre-existing worktree directory is also a failure for the same reason.
if [[ -e "$WORKTREE_PATH" ]]; then
  echo "Error: worktree path '$WORKTREE_PATH' already exists" >&2
  exit 3
fi

mkdir -p "$CODE_DIR_ABS/.claude/worktrees"

# Create the worktree. Capture stderr so a failure surfaces the underlying git
# message rather than just the exit code.
ADD_ERR=""
if ! ADD_ERR=$(git -C "$CODE_DIR_ABS" worktree add "$WORKTREE_PATH" -b "$BRANCH" "$BASE_BRANCH" 2>&1); then
  echo "Error: git worktree add failed: $ADD_ERR" >&2
  # Best-effort cleanup of an empty .claude/worktrees parent we may have just
  # created. rmdir refuses non-empty dirs — safe under concurrent runs sharing
  # the dir.
  rmdir "$CODE_DIR_ABS/.claude/worktrees" 2>/dev/null || true
  exit 3
fi

# Initialize submodules inside the new worktree if the repo has any. `git
# worktree add` does not do this automatically (per upstream design). Without
# this step a submodule-using repo would land in the worktree with empty
# submodule directories and any build/test in exec-spec would fail mysteriously
# — exactly the failure mode this step exists to prevent. Failure here must
# abort and roll back, not warn-and-proceed: a half-initialized worktree
# trips exec-spec on the implementer side, where the diagnostic chain is
# much longer.
if [[ -f "$CODE_DIR_ABS/.gitmodules" ]]; then
  SUBMODULE_ERR=""
  if ! SUBMODULE_ERR=$(git -C "$WORKTREE_PATH" submodule update --init --recursive 2>&1); then
    echo "Error: submodule init failed in $WORKTREE_PATH: $SUBMODULE_ERR" >&2
    # Roll back the worktree so re-run is idempotent.
    git -C "$CODE_DIR_ABS" worktree remove --force "$WORKTREE_PATH" >/dev/null 2>&1 || true
    git -C "$CODE_DIR_ABS" branch -D "$BRANCH" >/dev/null 2>&1 || true
    exit 3
  fi
fi

# Add .claude/worktrees/ to local exclude AFTER the worktree exists so a
# failed `git worktree add` doesn't leave a stale .gitignore-equivalent entry
# behind. .git/info/exclude is local-only and never committed — appropriate
# for ephemeral, per-checkout state like this.
#
# This step IS load-bearing: without the exclude, the newly created linked
# worktree at $CODE_DIR/.claude/worktrees/story-XX/ appears as an untracked
# directory in the main checkout's `git status --porcelain`. Both
# merge-worktree.sh's PRECONDITION and team-mode-orchestration.md's per-wave
# main-checkout audit fail-the-wave on non-empty porcelain — so a silent
# exclude failure would misfire as `FAILED:main-checkout-leak` against every
# completed impl-* in the wave. Fail-fast with rollback (mirrors the
# submodule-init handler above) instead of swallowing the error.
EXCLUDE_FILE="$CODE_DIR_ABS/.git/info/exclude"
EXCLUDE_LINE=".claude/worktrees/"
# CODE_DIR may be a worktree itself with .git as a file; resolve common-dir
# to land in the real exclude location either way.
GIT_COMMON_DIR=$(git -C "$CODE_DIR_ABS" rev-parse --git-common-dir 2>/dev/null || true)
if [[ -n "$GIT_COMMON_DIR" ]]; then
  case "$GIT_COMMON_DIR" in
    /*) EXCLUDE_FILE="$GIT_COMMON_DIR/info/exclude" ;;
    *)  EXCLUDE_FILE="$CODE_DIR_ABS/$GIT_COMMON_DIR/info/exclude" ;;
  esac
fi
EXCLUDE_ERR=""
if ! EXCLUDE_ERR=$(mkdir -p "$(dirname "$EXCLUDE_FILE")" 2>&1); then
  echo "Error: cannot create exclude-file directory $(dirname "$EXCLUDE_FILE"): $EXCLUDE_ERR" >&2
  _rollback_worktree
  exit 3
fi
if ! EXCLUDE_ERR=$(touch "$EXCLUDE_FILE" 2>&1); then
  echo "Error: cannot create $EXCLUDE_FILE: $EXCLUDE_ERR" >&2
  _rollback_worktree
  exit 3
fi
if ! grep -qxF "$EXCLUDE_LINE" "$EXCLUDE_FILE" 2>/dev/null; then
  if ! EXCLUDE_ERR=$(printf '%s\n' "$EXCLUDE_LINE" >> "$EXCLUDE_FILE" 2>&1); then
    echo "Error: cannot append '$EXCLUDE_LINE' to $EXCLUDE_FILE: $EXCLUDE_ERR" >&2
    _rollback_worktree
    exit 3
  fi
fi

printf 'WORKTREE_PATH=%s\n' "$WORKTREE_PATH"
exit 0
