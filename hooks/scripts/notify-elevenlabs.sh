#!/bin/bash
set -uo pipefail

# ElevenLabs TTS Completion Notification (Stop + Notification events)
# Voice notification when Claude finishes or needs attention.
# Requires: ELEVENLABS_API_KEY env var, curl, afplay (macOS) or aplay (Linux)
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
DEBOUNCE_FILE="$TMPBASE/claude-tts-notify-last-$SESSION_ID"
START_FILE="$TMPBASE/claude-tts-session-start-$SESSION_ID"
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

# ElevenLabs config
VOICE_ID="${ELEVENLABS_VOICE_ID:-21m00Tcm4TlvDq8ikWAM}"
API_KEY="${ELEVENLABS_API_KEY:-}"
[[ -z "$API_KEY" ]] && exit 0

# Event routing
MESSAGE=""
case "$EVENT" in
  Stop)
    MESSAGE="Claude has finished responding"
    ;;
  Notification)
    case "$MATCHER" in
      *permission_prompt*)
        MESSAGE="Claude needs your approval"
        ;;
      *idle_prompt*)
        MESSAGE="Claude is waiting for input"
        ;;
      *)
        MESSAGE="Claude needs your attention"
        ;;
    esac
    ;;
  *)
    exit 0
    ;;
esac

# Generate speech
AUDIO_FILE="$TMPBASE/claude-tts-$$.mp3"
HTTP_CODE=$(curl -s -o "$AUDIO_FILE" -w "%{http_code}" \
  -X POST "https://api.elevenlabs.io/v1/text-to-speech/$VOICE_ID" \
  -H "xi-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"$(sanitize "$MESSAGE")\",\"model_id\":\"eleven_monolingual_v1\"}" \
  2>/dev/null) || { rm -f "$AUDIO_FILE" 2>/dev/null; exit 0; }

[[ "$HTTP_CODE" != "200" ]] && { rm -f "$AUDIO_FILE" 2>/dev/null; exit 0; }

# Play audio
if [[ "$(uname)" == "Darwin" ]]; then
  afplay "$AUDIO_FILE" 2>/dev/null || true
elif command -v aplay &>/dev/null; then
  aplay "$AUDIO_FILE" 2>/dev/null || true
fi

rm -f "$AUDIO_FILE" 2>/dev/null
exit 0
