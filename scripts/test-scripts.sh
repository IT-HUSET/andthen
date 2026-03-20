#!/usr/bin/env bash
# test-scripts.sh — Integration tests for plugin helper scripts
# Run from repo root: scripts/test-scripts.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_DIR="$REPO_ROOT/plugin/scripts"
PASS=0
FAIL=0

# Colors (if terminal supports them)
if [[ -t 1 ]]; then
  GREEN='\033[0;32m'
  RED='\033[0;31m'
  YELLOW='\033[0;33m'
  NC='\033[0m'
else
  GREEN='' RED='' YELLOW='' NC=''
fi

assert_exit() {
  local name="$1" expected="$2" actual="$3"
  if [[ "$actual" -eq "$expected" ]]; then
    printf "${GREEN}  ✓ %s (exit %s)${NC}\n" "$name" "$actual"
    PASS=$((PASS + 1))
  else
    printf "${RED}  ✗ %s (expected exit %s, got %s)${NC}\n" "$name" "$expected" "$actual"
    FAIL=$((FAIL + 1))
  fi
}

assert_contains() {
  local name="$1" pattern="$2" output="$3"
  if echo "$output" | grep -qE "$pattern"; then
    printf "${GREEN}  ✓ %s${NC}\n" "$name"
    PASS=$((PASS + 1))
  else
    printf "${RED}  ✗ %s — expected output to contain: %s${NC}\n" "$name" "$pattern"
    FAIL=$((FAIL + 1))
  fi
}

assert_not_contains() {
  local name="$1" pattern="$2" output="$3"
  if ! echo "$output" | grep -qE "$pattern"; then
    printf "${GREEN}  ✓ %s${NC}\n" "$name"
    PASS=$((PASS + 1))
  else
    printf "${RED}  ✗ %s — expected output NOT to contain: %s${NC}\n" "$name" "$pattern"
    FAIL=$((FAIL + 1))
  fi
}

# ─────────────────────────────────────────────
# Setup: create a temporary git repo with fixtures
# ─────────────────────────────────────────────
FIXTURE=$(mktemp -d)
trap 'rm -rf "$FIXTURE"' EXIT

cd "$FIXTURE"
git init -q
git config user.email "test@test.com"
git config user.name "Test"

# Create baseline files (committed)
mkdir -p src lib docs
cat > src/app.ts <<'CODE'
import { helper } from './helper';
export function main() {
  return helper();
}
CODE

cat > src/helper.ts <<'CODE'
export function helper() {
  return 'working';
}
CODE

cat > src/orphan.ts <<'CODE'
export function orphanFunction() {
  return 'nobody imports me';
}
CODE

cat > src/stubby.ts <<'CODE'
export function doSomething() {
  // TODO: implement this
  throw new Error('not implemented');
}

export function placeholder() {
  return 'PLACEHOLDER';
}
CODE

cat > lib/utils.ts <<'CODE'
import { orphanFunction } from '../src/orphan';
export const utils = { orphanFunction };
CODE

cat > docs/README.md <<'CODE'
# Project
TODO: write docs
This is a PLACEHOLDER for documentation.
CODE

# Initial commit
git add -A
git commit -q -m "initial"

# Add dirty (uncommitted) files to test worktree detection
cat > src/newfile.ts <<'CODE'
export function newFeature() {
  return 'brand new';
}
CODE

cat > src/wired-new.ts <<'CODE'
export function wiredNew() {
  return 'wired';
}
CODE
# Wire the new file
cat >> src/app.ts <<'CODE'
import { wiredNew } from './wired-new';
CODE

# Stage some changes
git add src/wired-new.ts


printf "\n${YELLOW}═══════════════════════════════════════════${NC}\n"
printf "${YELLOW}  Helper Script Integration Tests${NC}\n"
printf "${YELLOW}═══════════════════════════════════════════${NC}\n\n"


# ─────────────────────────────────────────────
# 1. check-stubs.sh
# ─────────────────────────────────────────────
printf "${YELLOW}▸ check-stubs.sh${NC}\n"

# 1a. Detects stubs in code files
output=$("$SCRIPT_DIR/check-stubs.sh" src/stubby.ts 2>&1) || ec=$?
assert_exit "finds stubs in stubby.ts" 1 "${ec:-0}"
assert_contains "reports TODO" "TODO" "$output"
assert_contains "reports placeholder" "placeholder" "$output"

# 1b. Clean file returns 0
output=$("$SCRIPT_DIR/check-stubs.sh" src/helper.ts 2>&1) && ec=0 || ec=$?
assert_exit "clean file exits 0" 0 "$ec"
assert_contains "reports no stubs" "No stubs found" "$output"

# 1c. Excludes docs by default
output=$("$SCRIPT_DIR/check-stubs.sh" docs 2>&1) && ec=0 || ec=$?
assert_exit "docs excluded by default" 0 "$ec"

# 1d. --include-docs finds stubs in docs
output=$("$SCRIPT_DIR/check-stubs.sh" docs --include-docs 2>&1) || ec=$?
assert_exit "--include-docs finds doc stubs" 1 "${ec:-0}"
assert_contains "reports doc stubs" "TODO" "$output"

# 1e. JSON output works
output=$("$SCRIPT_DIR/check-stubs.sh" src/stubby.ts --json 2>&1) || true
assert_contains "JSON has count" '"count":' "$output"
assert_contains "JSON has results" '"results":' "$output"

# 1f. Missing path returns exit 2
output=$("$SCRIPT_DIR/check-stubs.sh" /nonexistent 2>&1) || ec=$?
assert_exit "missing path exits 2" 2 "${ec:-0}"

# 1g. --help exits 0
"$SCRIPT_DIR/check-stubs.sh" --help >/dev/null 2>&1 && ec=0 || ec=$?
assert_exit "--help exits 0" 0 "$ec"

printf "\n"


# ─────────────────────────────────────────────
# 2. check-wiring.sh
# ─────────────────────────────────────────────
printf "${YELLOW}▸ check-wiring.sh${NC}\n"

# 2a. File path input works (was broken before fix)
output=$("$SCRIPT_DIR/check-wiring.sh" src/app.ts 2>&1) && ec=0 || ec=$?
assert_exit "file path input works" 0 "$ec"
assert_not_contains "no error message" "Error:" "$output"

# 2b. Directory path works
output=$("$SCRIPT_DIR/check-wiring.sh" src 2>&1) && ec=0 || ec=$?
# Should find files and report something (wiring results or "no files")
assert_contains "dir path produces output" "Wiring check:|No added" "$output"

# 2c. Detects untracked files (dirty worktree)
output=$("$SCRIPT_DIR/check-wiring.sh" src/newfile.ts 2>&1) && ec=0 || ec=$?
# newfile.ts is untracked and not imported by anyone
assert_contains "finds untracked file" "newfile" "$output"

# 2d. Detects staged files
output=$("$SCRIPT_DIR/check-wiring.sh" src/wired-new.ts 2>&1) && ec=0 || ec=$?
assert_contains "finds staged file" "wired-new" "$output"

# 2e. Missing path returns exit 2
output=$("$SCRIPT_DIR/check-wiring.sh" /nonexistent 2>&1) || ec=$?
assert_exit "missing path exits 2" 2 "${ec:-0}"

# 2f. --help exits 0
"$SCRIPT_DIR/check-wiring.sh" --help >/dev/null 2>&1 && ec=0 || ec=$?
assert_exit "--help exits 0" 0 "$ec"

printf "\n"


# ─────────────────────────────────────────────
# 3. verify-implementation.sh
# ─────────────────────────────────────────────
printf "${YELLOW}▸ verify-implementation.sh${NC}\n"

# 3a. Missing file exits 1
output=$("$SCRIPT_DIR/verify-implementation.sh" /nonexistent/file.ts 2>&1) || ec=$?
assert_exit "missing file exits 1" 1 "${ec:-0}"
assert_contains "reports does not exist" "does not exist" "$output"

# 3b. File with stubs exits 1 (strict mode)
output=$("$SCRIPT_DIR/verify-implementation.sh" src/stubby.ts 2>&1) || ec=$?
assert_exit "stubby file exits 1" 1 "${ec:-0}"
assert_contains "reports stub indicators" "stub indicator|stub" "$output"

# 3c. Clean wired file passes
output=$("$SCRIPT_DIR/verify-implementation.sh" src/helper.ts 2>&1) && ec=0 || ec=$?
assert_exit "clean wired file exits 0" 0 "$ec"
assert_contains "reports pass" "pass" "$output"

# 3d. Multiple files: mix of pass and fail
output=$("$SCRIPT_DIR/verify-implementation.sh" src/helper.ts src/stubby.ts /nonexistent.ts 2>&1) || ec=$?
assert_exit "mixed files exits 1" 1 "${ec:-0}"
assert_contains "shows summary" "Summary:" "$output"

# 3e. Empty file exits 1
touch src/empty.ts
output=$("$SCRIPT_DIR/verify-implementation.sh" src/empty.ts 2>&1) || ec=$?
assert_exit "empty file exits 1" 1 "${ec:-0}"
assert_contains "reports empty" "empty file" "$output"

# 3f. No args exits 2
output=$("$SCRIPT_DIR/verify-implementation.sh" 2>&1) || ec=$?
assert_exit "no args exits 2" 2 "${ec:-0}"

# 3g. --help exits 0
"$SCRIPT_DIR/verify-implementation.sh" --help >/dev/null 2>&1 && ec=0 || ec=$?
assert_exit "--help exits 0" 0 "$ec"

printf "\n"


# ─────────────────────────────────────────────
# 4. run-security-scan.sh
# ─────────────────────────────────────────────
printf "${YELLOW}▸ run-security-scan.sh${NC}\n"

# Create files with known security patterns
mkdir -p sec
cat > sec/safe.ts <<'CODE'
export function safe() {
  return 'hello';
}
CODE

cat > sec/vulnerable.ts <<'CODE'
const password = "supersecretpassword123";
const el = document.getElementById('x');
el.innerHTML = userInput;
CODE

# 4a. Clean file returns 0
output=$("$SCRIPT_DIR/run-security-scan.sh" sec/safe.ts 2>&1) && ec=0 || ec=$?
# Note: may still exit 0 if semgrep finds nothing, or exit 1 if semgrep finds something
# For pattern fallback: should be clean
if ! command -v semgrep &>/dev/null; then
  assert_exit "clean file exits 0 (fallback)" 0 "$ec"
else
  printf "  ⊘ skipped (Semgrep installed — exit code depends on Semgrep rules)\n"
fi

# 4b. Vulnerable file detected
output=$("$SCRIPT_DIR/run-security-scan.sh" sec/vulnerable.ts 2>&1) || ec=$?
if ! command -v semgrep &>/dev/null; then
  assert_exit "vulnerable file detected (fallback)" 1 "${ec:-0}"
  assert_contains "reports hardcoded secret" "hardcoded-secret\|secret" "$output"
  assert_contains "reports XSS" "xss-vector\|innerHTML" "$output"
else
  # Semgrep may not flag simple patterns without config/rules resolving
  # Just verify it runs without crashing — exit 0 or 1 are both acceptable
  if [[ "${ec:-0}" -le 1 ]]; then
    printf "  ⊘ semgrep ran (exit %s) — rule coverage varies\n" "${ec:-0}"
  else
    assert_exit "semgrep ran without error" 1 "${ec:-0}"
  fi
fi

# 4c. Missing path returns exit 2
output=$("$SCRIPT_DIR/run-security-scan.sh" /nonexistent 2>&1) || ec=$?
assert_exit "missing path exits 2" 2 "${ec:-0}"

# 4d. --help exits 0
"$SCRIPT_DIR/run-security-scan.sh" --help >/dev/null 2>&1 && ec=0 || ec=$?
assert_exit "--help exits 0" 0 "$ec"

# 4e. JSON format works (pattern fallback only)
if ! command -v semgrep &>/dev/null; then
  output=$("$SCRIPT_DIR/run-security-scan.sh" sec/vulnerable.ts --format json 2>&1) || true
  assert_contains "JSON has scanner" '"scanner":' "$output"
  assert_contains "JSON has results" '"results":' "$output"
fi

printf "\n"


# ─────────────────────────────────────────────
# 5. Concurrency safety
# ─────────────────────────────────────────────
printf "${YELLOW}▸ Concurrency safety${NC}\n"

# Run two check-stubs in parallel and verify no interference
"$SCRIPT_DIR/check-stubs.sh" src/stubby.ts --json > /dev/null 2>&1 &
pid1=$!
"$SCRIPT_DIR/check-stubs.sh" src/helper.ts --json > /dev/null 2>&1 &
pid2=$!
wait "$pid1" || true
wait "$pid2" || true

# Verify no leftover temp files in /tmp with our old naming
leftover=$(find /tmp -maxdepth 1 \( -name 'stubs_*.txt' -o -name 'sec_*.txt' \) 2>/dev/null | wc -l | tr -d ' ')
assert_exit "no leftover /tmp files" 0 "$leftover"

printf "\n"


# ─────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────
printf "${YELLOW}═══════════════════════════════════════════${NC}\n"
TOTAL=$((PASS + FAIL))
if [[ $FAIL -eq 0 ]]; then
  printf "${GREEN}All %s tests passed${NC}\n" "$TOTAL"
else
  printf "${RED}%s/%s tests passed, %s failed${NC}\n" "$PASS" "$TOTAL" "$FAIL"
fi
printf "${YELLOW}═══════════════════════════════════════════${NC}\n"

exit $FAIL
