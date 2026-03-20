#!/usr/bin/env bash
# verify-implementation.sh — Combined existence + substance + wiring check
# Used by: exec-spec, exec-plan

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'EOF'
Usage: verify-implementation.sh <file1> [file2...]

For each file: checks existence, scans for stubs (via check-stubs.sh),
and verifies wiring (referenced by other files).
Summary output suitable for FIS task verification lines.

Delegates to sibling scripts check-stubs.sh and check-wiring.sh when
available, falling back to inline checks otherwise.

Options:
  --help    Show this help message

Exit codes:
  0  All files pass all checks
  1  Issues found (missing, empty, stubs, or unwired)
  2  Usage error
EOF
}

FILES=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    -*) echo "Unknown option: $1" >&2; usage; exit 2 ;;
    *) FILES+=("$1"); shift ;;
  esac
done

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "Error: At least one file path is required" >&2
  usage
  exit 2
fi

PASS=0
FAIL=0
TOTAL=${#FILES[@]}

echo "Verifying ${TOTAL} file(s)..."
echo ""

for file in "${FILES[@]}"; do
  STATUS="✓"
  ISSUES=()

  # Check 1: Existence
  if [[ ! -f "$file" ]]; then
    STATUS="✗"
    ISSUES+=("does not exist")
    ((FAIL++))
    echo "$STATUS $file — ${ISSUES[*]}"
    continue
  fi

  # Check 2: Non-empty
  if [[ ! -s "$file" ]]; then
    STATUS="✗"
    ISSUES+=("empty file")
  fi

  # Check 3: Stub detection — delegate to check-stubs.sh if available
  STUB_COUNT=0
  if [[ -x "$SCRIPT_DIR/check-stubs.sh" ]]; then
    STUB_COUNT=$("$SCRIPT_DIR/check-stubs.sh" "$file" --json 2>/dev/null | grep -o '"count": [0-9]*' | grep -o '[0-9]*' || echo "0")
  else
    STUB_COUNT=$(rg -c 'TODO|FIXME|HACK|XXX|raise NotImplementedError|throw.*not.implemented|placeholder|not.yet.implemented' "$file" 2>/dev/null || echo "0")
  fi
  if [[ "$STUB_COUNT" -gt 0 ]]; then
    STATUS="✗"
    ISSUES+=("${STUB_COUNT} stub indicator(s)")
  fi

  # Check 4: Wiring (is this file referenced by others?)
  basename=$(basename "$file")
  stem="${basename%.*}"
  SKIP_WIRING=false

  # Skip wiring for non-code files and entry points
  if echo "$file" | grep -qE '\.md$|\.json$|\.yml$|\.yaml$|\.toml$|\.env|\.lock$'; then
    SKIP_WIRING=true
  fi
  if [[ "$stem" == "index" || "$stem" == "main" || "$stem" == "app" || "$stem" == "mod" || "$stem" == "lib" ]]; then
    SKIP_WIRING=true
  fi

  if [[ "$SKIP_WIRING" == false ]]; then
    REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
    FULL_PATH=$(realpath "$file" 2>/dev/null || echo "$file")
    REF_COUNT=$(rg -l "$stem" "$REPO_ROOT" --type-not lock 2>/dev/null | grep -v "$FULL_PATH" | head -1 | wc -l || echo "0")
    REF_COUNT=$(echo "$REF_COUNT" | tr -d ' ')
    if [[ "$REF_COUNT" -eq 0 ]]; then
      STATUS="✗"
      ISSUES+=("not referenced by other files")
    fi
  fi

  if [[ ${#ISSUES[@]} -eq 0 ]]; then
    ((PASS++))
    echo "$STATUS $file — pass"
  else
    ((FAIL++))
    echo "$STATUS $file — ${ISSUES[*]}"
  fi
done

echo ""
echo "Summary: ${PASS}/${TOTAL} pass, ${FAIL}/${TOTAL} fail"

if [[ $FAIL -gt 0 ]]; then
  exit 1
fi

exit 0
