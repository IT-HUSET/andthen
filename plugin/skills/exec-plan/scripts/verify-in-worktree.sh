#!/usr/bin/env bash
# verify-in-worktree.sh – Hard-guard: assert the current process is operating
# inside the expected story-* worktree, not the main checkout.
# Used by: exec-plan team-mode implementer prompt (first action of every turn)
#          and the orchestrator's pre-merge per-wave audit.
#
# Harness isolation under `team_name` is unreliable, so this script is the
# only thing that distinguishes "agent is correctly isolated" from "agent is
# silently editing the main checkout". Failures here are STOP-the-line in the
# calling context.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: verify-in-worktree.sh STORY_ID EXPECTED_WORKTREE_PATH [--help]

Triple-checks that the current process is operating inside the expected
story-* worktree:
  1. pwd -P                              == EXPECTED_WORKTREE_PATH
  2. git rev-parse --show-toplevel       == EXPECTED_WORKTREE_PATH
  3. git rev-parse --abbrev-ref HEAD     == story-<STORY_ID>

Stdout (machine-readable, exactly one line):
  VERIFY_OK
  VERIFY_FAIL:expected_path_missing:<path>
  VERIFY_FAIL:pwd_mismatch:<actual>
  VERIFY_FAIL:toplevel_mismatch:<actual>
  VERIFY_FAIL:branch_mismatch:<actual>
  VERIFY_FAIL:not_in_git_repo

Exit codes:
  0  all three checks passed
  2  usage error (missing/invalid arguments)
  3  any check failed (diagnostic on stdout, details on stderr)
EOF
}

STORY_ID=""
EXPECTED_PATH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    -*) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
    *)
      if [[ -z "$STORY_ID" ]]; then STORY_ID="$1"
      elif [[ -z "$EXPECTED_PATH" ]]; then EXPECTED_PATH="$1"
      else
        echo "Error: unexpected argument: $1" >&2
        usage >&2
        exit 2
      fi
      shift
      ;;
  esac
done

if [[ -z "$STORY_ID" || -z "$EXPECTED_PATH" ]]; then
  echo "Error: STORY_ID and EXPECTED_WORKTREE_PATH are both required" >&2
  usage >&2
  exit 2
fi

EXPECTED_BRANCH="story-$STORY_ID"

# Canonicalize EXPECTED_PATH the same way we canonicalize observed paths, so a
# trailing-slash difference or symlink doesn't trigger a false negative. The
# explicit cd-failure branch covers the narrow window between the -d check and
# the canonicalize call (mid-call removal, permission flip) — without it, the
# substitution would silently yield empty and downstream comparisons would
# misfire as pwd_mismatch against an empty expected path.
if [[ ! -d "$EXPECTED_PATH" ]]; then
  echo "VERIFY_FAIL:expected_path_missing:$EXPECTED_PATH"
  echo "  Expected worktree path does not exist on disk: $EXPECTED_PATH" >&2
  exit 3
fi
if ! EXPECTED_PATH_CANON=$(cd "$EXPECTED_PATH" 2>/dev/null && pwd -P); then
  echo "VERIFY_FAIL:expected_path_missing:$EXPECTED_PATH"
  echo "  Expected worktree path is no longer accessible: $EXPECTED_PATH" >&2
  exit 3
fi

ACTUAL_PWD=$(pwd -P)
if [[ "$ACTUAL_PWD" != "$EXPECTED_PATH_CANON" ]]; then
  echo "VERIFY_FAIL:pwd_mismatch:$ACTUAL_PWD"
  echo "  pwd is '$ACTUAL_PWD'; expected '$EXPECTED_PATH_CANON'" >&2
  echo "  cd to the expected worktree path before any further bash, Read, Edit, Glob, or Grep." >&2
  exit 3
fi

ACTUAL_TOPLEVEL=$(git rev-parse --show-toplevel 2>/dev/null || true)
if [[ -z "$ACTUAL_TOPLEVEL" ]]; then
  echo "VERIFY_FAIL:not_in_git_repo"
  echo "  Current directory is not inside a git checkout: $ACTUAL_PWD" >&2
  exit 3
fi
if ! ACTUAL_TOPLEVEL_CANON=$(cd "$ACTUAL_TOPLEVEL" 2>/dev/null && pwd -P); then
  echo "VERIFY_FAIL:not_in_git_repo"
  echo "  git toplevel '$ACTUAL_TOPLEVEL' is not accessible from $ACTUAL_PWD" >&2
  exit 3
fi
if [[ "$ACTUAL_TOPLEVEL_CANON" != "$EXPECTED_PATH_CANON" ]]; then
  echo "VERIFY_FAIL:toplevel_mismatch:$ACTUAL_TOPLEVEL_CANON"
  echo "  git toplevel is '$ACTUAL_TOPLEVEL_CANON'; expected '$EXPECTED_PATH_CANON'" >&2
  echo "  You are likely in the main checkout, not the worktree. STOP and report VERIFY_FAILED to the orchestrator." >&2
  exit 3
fi

ACTUAL_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)
if [[ "$ACTUAL_BRANCH" != "$EXPECTED_BRANCH" ]]; then
  echo "VERIFY_FAIL:branch_mismatch:$ACTUAL_BRANCH"
  echo "  current branch is '$ACTUAL_BRANCH'; expected '$EXPECTED_BRANCH'" >&2
  exit 3
fi

echo "VERIFY_OK"
exit 0
