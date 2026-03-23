#!/usr/bin/env bash
# check-stubs.sh – Scan for indicators of incomplete implementation
# Used by: review-gap, exec-spec, exec-plan

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: check-stubs.sh <path> [--json] [--include-docs]

Scans for indicators of incomplete implementation in code files.
Categories: TODO/FIXME, empty functions, placeholder returns, test stubs, config stubs.

By default, excludes documentation and non-code files (*.md, *.txt, templates/).
Use --include-docs to scan everything.

Options:
  --json          Output results as JSON
  --include-docs  Include documentation/non-code files in scan
  --help          Show this help message

Exit codes:
  0  Clean – no stubs found
  1  Stubs found
  2  Usage error
EOF
}

JSON_OUTPUT=false
INCLUDE_DOCS=false
TARGET=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --json) JSON_OUTPUT=true; shift ;;
    --include-docs) INCLUDE_DOCS=true; shift ;;
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

# Concurrency-safe temp directory
TMPDIR_STUBS=$(mktemp -d)
trap 'rm -rf "$TMPDIR_STUBS"' EXIT

# Build glob exclusions for non-code files
RG_EXCLUDES=""
if [[ "$INCLUDE_DOCS" == false ]]; then
  RG_EXCLUDES="--glob !*.md --glob !*.txt --glob !*.rst --glob !templates/ --glob !checklists/ --glob !docs/ --glob !CHANGELOG* --glob !LICENSE* --glob !README*"
fi

FOUND=0
declare -a RESULTS=()

# Helper: run rg with optional excludes (avoids empty-array expansion issues)
run_rg() {
  if [[ -n "$RG_EXCLUDES" ]]; then
    # shellcheck disable=SC2086
    rg "$@" $RG_EXCLUDES
  else
    rg "$@"
  fi
}

# Category 1: TODO/FIXME/HACK/XXX markers
if run_rg -n --no-heading 'TODO|FIXME|HACK|XXX' "$TARGET" --type-not lock 2>/dev/null | head -50 > "$TMPDIR_STUBS/todo.txt" && [[ -s "$TMPDIR_STUBS/todo.txt" ]]; then
  FOUND=1
  while IFS= read -r line; do
    RESULTS+=("todo:$line")
  done < "$TMPDIR_STUBS/todo.txt"
fi

# Category 2: Placeholder returns and not-implemented patterns
if run_rg -n --no-heading 'raise NotImplementedError|throw.*not.implemented|pass\s*$|return\s*nil\s*$|return\s*None\s*$|return\s*undefined\s*$|\.\.\.(\s*#|$)|not.yet.implemented|placeholder|stub' "$TARGET" --type-not lock 2>/dev/null | head -50 > "$TMPDIR_STUBS/placeholder.txt" && [[ -s "$TMPDIR_STUBS/placeholder.txt" ]]; then
  FOUND=1
  while IFS= read -r line; do
    RESULTS+=("placeholder:$line")
  done < "$TMPDIR_STUBS/placeholder.txt"
fi

# Category 3: Empty function bodies (common patterns across languages)
if run_rg -n --no-heading -U '(def |function |fn |func |async )\w+.*\{?\s*\n\s*(pass|\}|end|return;?\s*$)' "$TARGET" --type-not lock 2>/dev/null | head -30 > "$TMPDIR_STUBS/empty.txt" && [[ -s "$TMPDIR_STUBS/empty.txt" ]]; then
  FOUND=1
  while IFS= read -r line; do
    RESULTS+=("empty-body:$line")
  done < "$TMPDIR_STUBS/empty.txt"
fi

# Category 4: Test stubs (pending/skip/xit patterns)
if run_rg -n --no-heading 'xit\(|xdescribe\(|test\.skip|it\.skip|@pytest\.mark\.skip|pending\b|@Ignore|@Disabled' "$TARGET" --type-not lock 2>/dev/null | head -30 > "$TMPDIR_STUBS/test.txt" && [[ -s "$TMPDIR_STUBS/test.txt" ]]; then
  FOUND=1
  while IFS= read -r line; do
    RESULTS+=("test-stub:$line")
  done < "$TMPDIR_STUBS/test.txt"
fi

# Category 5: Config/env stubs
if run_rg -n --no-heading 'your[-_]?api[-_]?key|changeme|replace[-_]?me|INSERT[-_]?HERE|PLACEHOLDER|example\.com' "$TARGET" --type-not lock -i 2>/dev/null | head -20 > "$TMPDIR_STUBS/config.txt" && [[ -s "$TMPDIR_STUBS/config.txt" ]]; then
  FOUND=1
  while IFS= read -r line; do
    RESULTS+=("config-stub:$line")
  done < "$TMPDIR_STUBS/config.txt"
fi

# Output results
if [[ "$JSON_OUTPUT" == true ]]; then
  echo "{"
  echo "  \"found\": $FOUND,"
  echo "  \"count\": ${#RESULTS[@]},"
  echo "  \"results\": ["
  for i in "${!RESULTS[@]}"; do
    category="${RESULTS[$i]%%:*}"
    detail="${RESULTS[$i]#*:}"
    detail="${detail//\\/\\\\}"
    detail="${detail//\"/\\\"}"
    comma=","
    [[ $i -eq $((${#RESULTS[@]} - 1)) ]] && comma=""
    echo "    {\"category\": \"$category\", \"detail\": \"$detail\"}$comma"
  done
  echo "  ]"
  echo "}"
else
  if [[ $FOUND -eq 0 ]]; then
    echo "✓ No stubs found in $TARGET"
  else
    echo "⚠ Found ${#RESULTS[@]} stub indicator(s) in $TARGET:"
    echo ""
    CURRENT_CAT=""
    for result in "${RESULTS[@]}"; do
      category="${result%%:*}"
      detail="${result#*:}"
      if [[ "$category" != "$CURRENT_CAT" ]]; then
        CURRENT_CAT="$category"
        echo "[$category]"
      fi
      echo "  $detail"
    done
  fi
fi

exit $FOUND
