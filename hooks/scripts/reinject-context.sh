#!/bin/bash
set -uo pipefail

# Hook 4: Context Re-injection After Compaction (SessionStart with "compact" matcher)
# Re-injects CLAUDE.md (project instructions) into context after compaction.
# Always exits 0.

INPUT=$(cat)

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-}"
if [[ -z "$PROJECT_DIR" ]]; then
  if command -v jq &>/dev/null; then
    PROJECT_DIR=$(echo "$INPUT" | jq -r '.cwd // empty' 2>/dev/null)
  else
    PROJECT_DIR=$(echo "$INPUT" | grep -o '"cwd"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"cwd"[[:space:]]*:[[:space:]]*"//;s/".*//')
  fi
fi

[[ -z "$PROJECT_DIR" ]] && exit 0

CLAUDE_MD="$PROJECT_DIR/CLAUDE.md"
[[ -f "$CLAUDE_MD" ]] || exit 0

python3 -c "
import json, sys
content = open(sys.argv[1]).read()
output = {
    'hookSpecificOutput': {
        'hookEventName': 'SessionStart',
        'additionalContext': 'Project instructions (re-injected after compaction):\n\n' + content
    }
}
json.dump(output, sys.stdout)
" "$CLAUDE_MD" 2>/dev/null

exit 0
