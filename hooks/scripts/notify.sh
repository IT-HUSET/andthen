#!/bin/bash
set -uo pipefail

# Hook 3: Completion Notification (Stop + Notification events)
# Sends desktop notification when Claude finishes or needs attention.
# Always exits 0 — notifications must never block Claude.

umask 077

sanitize() { echo "$1" | tr -d "'\"\`\\\\"; }

INPUT=$(cat)

# Parse JSON fields
if command -v jq &>/dev/null; then
  EVENT=$(echo "$INPUT" | jq -r '.hook_event_name // empty' 2>/dev/null)
  RAW_SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty' 2>/dev/null)
  MATCHER=$(echo "$INPUT" | jq -r '.matched_hook.matcher // empty' 2>/dev/null)
else
  EVENT=$(echo "$INPUT" | grep -o '"hook_event_name"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"hook_event_name"[[:space:]]*:[[:space:]]*"//;s/".*//')
  RAW_SESSION_ID=$(echo "$INPUT" | grep -o '"session_id"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"session_id"[[:space:]]*:[[:space:]]*"//;s/".*//')
  MATCHER=$(echo "$INPUT" | grep -o '"matcher"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"matcher"[[:space:]]*:[[:space:]]*"//;s/".*//')
fi

SESSION_ID=$(echo "$RAW_SESSION_ID" | tr -cd 'a-zA-Z0-9_-')
[[ -z "$SESSION_ID" ]] && SESSION_ID="default"

TMPBASE="${TMPDIR:-/tmp}"
DEBOUNCE_FILE="$TMPBASE/claude-notify-last-$SESSION_ID"
START_FILE="$TMPBASE/claude-session-start-$SESSION_ID"
NOW=$(date +%s)

# Record session start on first invocation
if [[ ! -f "$START_FILE" ]] || [[ -L "$START_FILE" ]]; then
  [[ -L "$START_FILE" ]] && exit 0
  echo "$NOW" > "$START_FILE"
fi

# Session duration check (Stop only) — suppress if < 30s
if [[ "$EVENT" == "Stop" ]]; then
  START_TIME=$(cat "$START_FILE" 2>/dev/null || echo "$NOW")
  ELAPSED=$(( NOW - START_TIME ))
  [[ "$ELAPSED" -lt 30 ]] && exit 0
fi

# Debounce: skip if notified within last 5 seconds
if [[ -f "$DEBOUNCE_FILE" ]] && [[ ! -L "$DEBOUNCE_FILE" ]]; then
  LAST=$(cat "$DEBOUNCE_FILE" 2>/dev/null || echo "0")
  DIFF=$(( NOW - LAST ))
  [[ "$DIFF" -lt 5 ]] && exit 0
fi

# Symlink check before writing debounce file
[[ -L "$DEBOUNCE_FILE" ]] && exit 0
echo "$NOW" > "$DEBOUNCE_FILE"

# Event routing
TITLE=""
MESSAGE=""
case "$EVENT" in
  Stop)
    TITLE="Claude Code - Task Complete"
    MESSAGE="Claude has finished responding"
    ;;
  Notification)
    case "$MATCHER" in
      *permission_prompt*)
        TITLE="Claude Code - Permission Required"
        MESSAGE="Claude needs your approval"
        ;;
      *idle_prompt*)
        TITLE="Claude Code - Needs Attention"
        MESSAGE="Claude is waiting for input"
        ;;
      *)
        TITLE="Claude Code - Notification"
        MESSAGE="Claude needs your attention"
        ;;
    esac
    ;;
  *)
    exit 0
    ;;
esac

# Platform detection and dispatch
SAFE_TITLE=$(sanitize "$TITLE")
SAFE_MSG=$(sanitize "$MESSAGE")

if [[ "$(uname)" == "Darwin" ]]; then
  osascript -e "display notification \"$SAFE_MSG\" with title \"$SAFE_TITLE\" sound name \"Glass\"" 2>/dev/null || true
elif command -v notify-send &>/dev/null; then
  notify-send -u normal "$SAFE_TITLE" "$SAFE_MSG" 2>/dev/null || true
else
  printf '\a'
fi

exit 0
