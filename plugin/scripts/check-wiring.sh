#!/usr/bin/env bash
# check-wiring.sh – Verify that new/changed files are imported/referenced
# Used by: review-gap, exec-spec

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: check-wiring.sh <path> [--base-branch <branch>]

For each code file added or modified in the worktree (staged, unstaged,
and untracked), verifies it's imported or referenced by at least one
other file in the repository.

Accepts both file paths and directory paths.

Options:
  --base-branch <branch>  Also include files changed since this branch
                          (in addition to worktree changes). Default: none.
  --help                  Show this help message

Exit codes:
  0  All files wired (imported/referenced)
  1  Unwired files found
  2  Usage error
EOF
}

TARGET=""
BASE_BRANCH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --base-branch) BASE_BRANCH="$2"; shift 2 ;;
    -*) echo "Unknown option: $1" >&2; usage; exit 2 ;;
    *) TARGET="$1"; shift ;;
  esac
done

if [[ -z "$TARGET" ]]; then
  echo "Error: <path> is required" >&2
  usage
  exit 2
fi

if [[ ! -e "$TARGET" ]]; then
  echo "Error: Path does not exist: $TARGET" >&2
  exit 2
fi

# Resolve TARGET to a directory for git operations
if [[ -f "$TARGET" ]]; then
  TARGET_DIR="$(cd "$(dirname "$TARGET")" && pwd)"
else
  TARGET_DIR="$(cd "$TARGET" && pwd)"
fi

# Get repository root
REPO_ROOT=$(git -C "$TARGET_DIR" rev-parse --show-toplevel 2>/dev/null || echo "")
if [[ -z "$REPO_ROOT" ]]; then
  echo "Error: Not a git repository: $TARGET" >&2
  exit 2
fi

# Make TARGET relative to repo root for consistent path handling
REL_TARGET=$(python3 -c "import os.path; print(os.path.relpath('$(cd "$(dirname "$TARGET")" && pwd)/$(basename "$TARGET")', '$REPO_ROOT'))" 2>/dev/null || echo "$TARGET")

# Collect changed files from multiple sources
TMPDIR_WIRING=$(mktemp -d)
trap 'rm -rf "$TMPDIR_WIRING"' EXIT

# Source 1: Staged changes (git diff --cached)
git -C "$REPO_ROOT" diff --cached --name-only --diff-filter=AM -- "$REL_TARGET" 2>/dev/null >> "$TMPDIR_WIRING/files.txt" || true

# Source 2: Unstaged changes (git diff)
git -C "$REPO_ROOT" diff --name-only --diff-filter=AM -- "$REL_TARGET" 2>/dev/null >> "$TMPDIR_WIRING/files.txt" || true

# Source 3: Untracked files
git -C "$REPO_ROOT" ls-files --others --exclude-standard -- "$REL_TARGET" 2>/dev/null >> "$TMPDIR_WIRING/files.txt" || true

# Source 4: Branch comparison (optional)
if [[ -n "$BASE_BRANCH" ]]; then
  git -C "$REPO_ROOT" diff --name-only --diff-filter=AM "${BASE_BRANCH}...HEAD" -- "$REL_TARGET" 2>/dev/null >> "$TMPDIR_WIRING/files.txt" || true
fi

# If TARGET is a single file, add it directly
if [[ -f "$TARGET" ]]; then
  echo "$REL_TARGET" >> "$TMPDIR_WIRING/files.txt"
fi

# Deduplicate
CHANGED_FILES=$(sort -u "$TMPDIR_WIRING/files.txt" 2>/dev/null || echo "")

if [[ -z "$CHANGED_FILES" ]]; then
  echo "✓ No added/modified files found to check"
  exit 0
fi

UNWIRED=()
WIRED=()
SKIPPED=()

# File extensions that don't need wiring checks
SKIP_PATTERNS='\.md$|\.txt$|\.json$|\.yml$|\.yaml$|\.toml$|\.ini$|\.cfg$|\.env|\.lock$|\.log$|\.csv$|\.gitignore|LICENSE|Makefile|Dockerfile|\.dockerignore'

while IFS= read -r file; do
  [[ -z "$file" ]] && continue

  # Skip non-code files (but don't skip .sh – scripts can be wired)
  if echo "$file" | grep -qE "$SKIP_PATTERNS"; then
    SKIPPED+=("$file")
    continue
  fi

  # Get the basename and stem for searching
  basename=$(basename "$file")
  stem="${basename%.*}"

  # Skip index/entry point files (they wire others, not themselves)
  if [[ "$stem" == "index" || "$stem" == "main" || "$stem" == "app" || "$stem" == "mod" || "$stem" == "lib" ]]; then
    SKIPPED+=("$file (entry point)")
    continue
  fi

  # Search for references to this file by stem name
  # Exclude the file itself from results
  FULL_PATH="$REPO_ROOT/$file"
  REF_COUNT=$(rg -l --no-heading "$stem" "$REPO_ROOT" --type-not lock --glob '!*.lock' 2>/dev/null | grep -v "$FULL_PATH" | head -1 | wc -l || echo "0")
  REF_COUNT=$(echo "$REF_COUNT" | tr -d ' ')

  if [[ "$REF_COUNT" -gt 0 ]]; then
    WIRED+=("$file")
  else
    UNWIRED+=("$file")
  fi
done <<< "$CHANGED_FILES"

# Report
echo "Wiring check: ${#WIRED[@]} wired, ${#UNWIRED[@]} unwired, ${#SKIPPED[@]} skipped"
echo ""

if [[ ${#UNWIRED[@]} -gt 0 ]]; then
  echo "⚠ Unwired files (not imported/referenced by any other file):"
  for f in "${UNWIRED[@]}"; do
    echo "  ✗ $f"
  done
  echo ""
fi

if [[ ${#WIRED[@]} -gt 0 ]]; then
  echo "✓ Wired files:"
  for f in "${WIRED[@]}"; do
    echo "  ✓ $f"
  done
fi

if [[ ${#UNWIRED[@]} -gt 0 ]]; then
  exit 1
fi

exit 0
