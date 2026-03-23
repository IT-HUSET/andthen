#!/usr/bin/env bash
# run-security-scan.sh – Security scanning with Semgrep or pattern fallback
# Used by: review-code, review-gap

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: run-security-scan.sh <path> [--format json|text]

Runs Semgrep if installed, otherwise falls back to pattern-based checks.
Checks: hardcoded secrets, SQL injection, XSS vectors, unsafe deserialization,
        path traversal.

Options:
  --format <json|text>  Output format (default: text)
  --help                Show this help message

Exit codes:
  0  Clean – no findings
  1  Findings detected
  2  Usage error
EOF
}

TARGET=""
FORMAT="text"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --format) FORMAT="$2"; shift 2 ;;
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

FOUND=0

# Try Semgrep first
if command -v semgrep &>/dev/null; then
  echo "Running Semgrep scan..."
  if [[ "$FORMAT" == "json" ]]; then
    if semgrep scan --config auto --severity WARNING --severity ERROR --json "$TARGET" 2>/dev/null; then
      :
    else
      FOUND=1
    fi
  else
    if semgrep scan --config auto --severity WARNING --severity ERROR "$TARGET" 2>/dev/null; then
      echo "✓ Semgrep: No issues found"
    else
      FOUND=1
    fi
  fi
else
  echo "Semgrep not installed – falling back to pattern-based checks"
  echo ""

  # Concurrency-safe temp directory
  TMPDIR_SEC=$(mktemp -d)
  trap 'rm -rf "$TMPDIR_SEC"' EXIT

  declare -a FINDINGS=()

  # Pattern 1: Hardcoded secrets
  if rg -n --no-heading -i '(api[_-]?key|secret[_-]?key|password|token|credential)\s*[:=]\s*["\x27][^"\x27]{8,}' "$TARGET" --type-not lock 2>/dev/null | head -20 > "$TMPDIR_SEC/secrets.txt" && [[ -s "$TMPDIR_SEC/secrets.txt" ]]; then
    FOUND=1
    while IFS= read -r line; do
      FINDINGS+=("hardcoded-secret:$line")
    done < "$TMPDIR_SEC/secrets.txt"
  fi

  # Pattern 2: SQL injection risks
  if rg -n --no-heading '(execute|query|raw)\s*\(.*\$|f".*SELECT.*\{|f".*INSERT.*\{|f".*UPDATE.*\{|f".*DELETE.*\{|\+.*SQL|string\.Format.*SELECT' "$TARGET" --type-not lock 2>/dev/null | head -20 > "$TMPDIR_SEC/sqli.txt" && [[ -s "$TMPDIR_SEC/sqli.txt" ]]; then
    FOUND=1
    while IFS= read -r line; do
      FINDINGS+=("sql-injection:$line")
    done < "$TMPDIR_SEC/sqli.txt"
  fi

  # Pattern 3: XSS vectors
  if rg -n --no-heading 'innerHTML\s*=|dangerouslySetInnerHTML|v-html|\.html\(|document\.write\(' "$TARGET" --type-not lock 2>/dev/null | head -20 > "$TMPDIR_SEC/xss.txt" && [[ -s "$TMPDIR_SEC/xss.txt" ]]; then
    FOUND=1
    while IFS= read -r line; do
      FINDINGS+=("xss-vector:$line")
    done < "$TMPDIR_SEC/xss.txt"
  fi

  # Pattern 4: Unsafe deserialization
  if rg -n --no-heading 'pickle\.loads?|yaml\.load\(|eval\(|unserialize\(|JSON\.parse\(.*user|ObjectInputStream' "$TARGET" --type-not lock 2>/dev/null | head -20 > "$TMPDIR_SEC/deser.txt" && [[ -s "$TMPDIR_SEC/deser.txt" ]]; then
    FOUND=1
    while IFS= read -r line; do
      FINDINGS+=("unsafe-deserialization:$line")
    done < "$TMPDIR_SEC/deser.txt"
  fi

  # Pattern 5: Path traversal
  if rg -n --no-heading '\.\.\/|path\.join\(.*req\.|os\.path\.join\(.*input|file_get_contents\(.*\$' "$TARGET" --type-not lock 2>/dev/null | head -20 > "$TMPDIR_SEC/path.txt" && [[ -s "$TMPDIR_SEC/path.txt" ]]; then
    FOUND=1
    while IFS= read -r line; do
      FINDINGS+=("path-traversal:$line")
    done < "$TMPDIR_SEC/path.txt"
  fi

  # Output results
  if [[ "$FORMAT" == "json" ]]; then
    echo "{"
    echo "  \"scanner\": \"pattern-fallback\","
    echo "  \"found\": $FOUND,"
    echo "  \"count\": ${#FINDINGS[@]},"
    echo "  \"results\": ["
    for i in "${!FINDINGS[@]}"; do
      category="${FINDINGS[$i]%%:*}"
      detail="${FINDINGS[$i]#*:}"
      detail="${detail//\\/\\\\}"
      detail="${detail//\"/\\\"}"
      comma=","
      [[ $i -eq $((${#FINDINGS[@]} - 1)) ]] && comma=""
      echo "    {\"category\": \"$category\", \"detail\": \"$detail\"}$comma"
    done
    echo "  ]"
    echo "}"
  else
    if [[ $FOUND -eq 0 ]]; then
      echo "✓ No security issues found (pattern-based scan)"
    else
      echo "⚠ Found ${#FINDINGS[@]} potential security issue(s):"
      echo ""
      CURRENT_CAT=""
      for finding in "${FINDINGS[@]}"; do
        category="${finding%%:*}"
        detail="${finding#*:}"
        if [[ "$category" != "$CURRENT_CAT" ]]; then
          CURRENT_CAT="$category"
          echo "[$category]"
        fi
        echo "  $detail"
      done
      echo ""
      echo "Note: Pattern-based scan – verify findings manually. Install Semgrep for deeper analysis."
    fi
  fi
fi

exit $FOUND
