#!/usr/bin/env sh

set -eu

usage() {
  cat <<'EOF'
Evaluate whether Claude Code triggers the expected AndThen skills.

Usage:
  ./scripts/eval-skill-triggers.sh [options]

Options:
  --queries PATH    Query corpus JSON file (default: evals/skill-trigger-queries.json)
  --skill NAME      Limit evaluation to one skill (e.g. spec, plan, exec-spec)
  --runs N          Number of runs per query (default: 1)
  -h, --help        Show this help text

Notes:
  - Requires `claude` and `jq`
  - Uses `claude -p ... --verbose --output-format stream-json`
  - Exit code is 0 when every query matches expectation, 1 otherwise
EOF
}

repo_root=$(
  CDPATH= cd -- "$(dirname -- "$0")/.." && pwd
)

queries_file="$repo_root/evals/skill-trigger-queries.json"
skill_filter=""
runs=1

while [ "$#" -gt 0 ]; do
  case "$1" in
    --queries)
      queries_file="$2"
      shift 2
      ;;
    --skill)
      skill_filter="$2"
      shift 2
      ;;
    --runs)
      runs="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown option: %s\n\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! command -v jq >/dev/null 2>&1; then
  printf 'Error: jq is required\n' >&2
  exit 2
fi

if ! command -v claude >/dev/null 2>&1; then
  printf 'Error: claude CLI is required\n' >&2
  exit 2
fi

case "$runs" in
  ''|*[!0-9]*)
    printf 'Error: --runs must be a positive integer\n' >&2
    exit 2
    ;;
esac

if [ "$runs" -lt 1 ]; then
  printf 'Error: --runs must be at least 1\n' >&2
  exit 2
fi

if [ ! -f "$queries_file" ]; then
  printf 'Error: query file not found: %s\n' "$queries_file" >&2
  exit 2
fi

if [ -n "$skill_filter" ]; then
  query_count=$(jq --arg skill "$skill_filter" '[.[] | select(.skill == $skill)] | length' "$queries_file")
else
  query_count=$(jq '[.[]] | length' "$queries_file")
fi

if [ "$query_count" -eq 0 ]; then
  printf 'Error: no queries matched\n' >&2
  exit 2
fi

check_triggered() {
  query="$1"
  skill="$2"
  check_dir=$(mktemp -d)
  stream_file="$check_dir/claude-stream.jsonl"
  claude_stderr="$check_dir/claude.stderr"
  parsed_file="$check_dir/parsed.txt"
  jq_stderr="$check_dir/jq.stderr"
  first_skill_call=""

  if ! claude -p "$query" --effort low --tools Skill --verbose --output-format stream-json >"$stream_file" 2>"$claude_stderr"; then
    printf 'Error: claude CLI failed while evaluating query for skill %s\n' "$skill" >&2
    sed -n '1,20p' "$claude_stderr" >&2
    rm -rf "$check_dir"
    return 2
  fi

  if ! jq -r --unbuffered --arg skill "$skill" '
    def invoked_name:
      (.input.skill // .input.name // .input.command // "");

    def matches_skill:
      invoked_name == $skill
      or invoked_name == ("andthen:" + $skill)
      or invoked_name == ("andthen-" + $skill)
      or (invoked_name | endswith(":" + $skill))
      or (invoked_name | endswith("-" + $skill));

    if .type == "assistant" then
      .message.content[]?
      | select(.type == "tool_use" and .name == "Skill")
      | if matches_skill then "MATCH" else "OTHER" end
    else
      empty
    end
  ' "$stream_file" >"$parsed_file" 2>"$jq_stderr"; then
    printf 'Error: jq failed while parsing eval output for skill %s\n' "$skill" >&2
    sed -n '1,20p' "$jq_stderr" >&2
    rm -rf "$check_dir"
    return 2
  fi

  first_skill_call=$(sed -n '1p' "$parsed_file")
  rm -rf "$check_dir"

  [ "$first_skill_call" = "MATCH" ]
}

pass_count=0
fail_count=0
total_count=0

printf 'Evaluating %s query(s)', "$query_count"
if [ -n "$skill_filter" ]; then
  printf ' for skill %s', "$skill_filter"
fi
printf ' with %s run(s) each\n\n' "$runs"

while IFS=$(printf '\t') read -r skill should_trigger query; do
  [ -n "$skill" ] || continue

  total_count=$((total_count + 1))
  triggers=0

  i=1
  while [ "$i" -le "$runs" ]; do
    if check_triggered "$query" "$skill"; then
      triggers=$((triggers + 1))
    else
      status=$?
      if [ "$status" -eq 2 ]; then
        exit 2
      fi
    fi
    i=$((i + 1))
  done

  if [ "$should_trigger" = "true" ]; then
    if [ $((triggers * 2)) -ge "$runs" ]; then
      result="PASS"
      pass_count=$((pass_count + 1))
    else
      result="FAIL"
      fail_count=$((fail_count + 1))
    fi
  else
    if [ $((triggers * 2)) -lt "$runs" ]; then
      result="PASS"
      pass_count=$((pass_count + 1))
    else
      result="FAIL"
      fail_count=$((fail_count + 1))
    fi
  fi

  printf '[%s] skill=%s expected=%s triggered=%s/%s\n' \
    "$result" "$skill" "$should_trigger" "$triggers" "$runs"
  printf '  %s\n' "$query"
done <<EOF
$(if [ -n "$skill_filter" ]; then
    jq -r --arg skill "$skill_filter" '.[] | select(.skill == $skill) | [.skill, (.should_trigger | tostring), .query] | @tsv' "$queries_file"
  else
    jq -r '.[] | [.skill, (.should_trigger | tostring), .query] | @tsv' "$queries_file"
  fi)
EOF

printf '\nSummary: %s pass, %s fail, %s total\n' \
  "$pass_count" "$fail_count" "$total_count"

if [ "$fail_count" -gt 0 ]; then
  exit 1
fi

exit 0
