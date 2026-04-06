#!/bin/bash
set -uo pipefail

# ElevenLabs TTS Completion Notification (Stop + Notification events)
# Voice notification when Claude finishes or needs attention.
# Requires: ELEVENLABS_API_KEY env var, curl, afplay (macOS) or aplay (Linux)
# Always exits 0 – notifications must never block Claude.

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

# Session duration check (Stop only) – suppress if < 30s
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

# ElevenLabs config – ELEVENLABS_VOICE_ID can be a comma-separated list; one is picked at random
IFS=',' read -ra VOICE_IDS <<< "${ELEVENLABS_VOICE_ID:-21m00Tcm4TlvDq8ikWAM}"
VOICE_ID="${VOICE_IDS[RANDOM % ${#VOICE_IDS[@]}]}"
MODEL_ID="${ELEVENLABS_MODEL_ID:-eleven_flash_v2_5}"
API_KEY="${ELEVENLABS_API_KEY:-}"
[[ -z "$API_KEY" ]] && exit 0

# Event routing
PROMPT=""
FALLBACK=""
case "$EVENT" in
  Stop)
    PROMPT="Generate a short, fun, slightly witty spoken notification (max 10 words) announcing that Claude has finished its task. Vary the phrasing each time. Reply with only the message, no quotes."
    FALLBACK="Claude has finished responding"
    ;;
  Notification)
    case "$MATCHER" in
      *permission_prompt*)
        PROMPT="Generate a short, fun spoken notification (max 10 words) asking the user to approve something. Vary the phrasing each time. Reply with only the message, no quotes."
        FALLBACK="Claude needs your approval"
        ;;
      *idle_prompt*)
        PROMPT="Generate a short, fun spoken notification (max 10 words) letting the user know Claude is waiting for their input. Vary the phrasing each time. Reply with only the message, no quotes."
        FALLBACK="Claude is waiting for input"
        ;;
      *)
        PROMPT="Generate a short, fun spoken notification (max 10 words) saying Claude needs the user's attention. Vary the phrasing each time. Reply with only the message, no quotes."
        FALLBACK="Claude needs your attention"
        ;;
    esac
    ;;
  *)
    exit 0
    ;;
esac

# Detach heavy work (API calls + playback) so the hook exits immediately.
# This prevents Claude Code's hook timeout from killing playback mid-stream.
_tts_notify() {
  # Generate message via Claude Haiku, fall back to static message
  # Unset CLAUDECODE to allow running claude CLI from within a Claude Code session
  local MESSAGE="$2"
  if command -v claude &>/dev/null; then
    local GENERATED
    GENERATED=$(CLAUDECODE="" claude --model claude-haiku-4-5-20251001 --no-session-persistence -p "$1" 2>/dev/null | head -1 | tr -d '\"`')
    [[ -n "$GENERATED" ]] && MESSAGE="$GENERATED"
  fi

  # Generate speech (PCM 44100 avoids MP3 frame-padding clipping with afplay)
  local AUDIO_FILE="$TMPBASE/claude-tts-$$.wav"
  local HTTP_CODE
  HTTP_CODE=$(curl -s -o "$AUDIO_FILE" -w "%{http_code}" \
    -X POST "https://api.elevenlabs.io/v1/text-to-speech/$VOICE_ID?output_format=pcm_44100" \
    -H "xi-api-key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"text\":\"$(sanitize "$MESSAGE")\",\"model_id\":\"$(sanitize "$MODEL_ID")\"}" \
    2>/dev/null) || { rm -f "$AUDIO_FILE" 2>/dev/null; return; }

  [[ "$HTTP_CODE" != "200" ]] && { rm -f "$AUDIO_FILE" 2>/dev/null; return; }

  # Wrap raw PCM in a WAV header so afplay/aplay can read it
  local WAV_FILE="$TMPBASE/claude-tts-$$.pcm.wav"
  _pcm_to_wav "$AUDIO_FILE" "$WAV_FILE" && rm -f "$AUDIO_FILE" 2>/dev/null || {
    rm -f "$AUDIO_FILE" "$WAV_FILE" 2>/dev/null; return
  }

  # Play audio
  if [[ "$(uname)" == "Darwin" ]]; then
    afplay "$WAV_FILE" 2>/dev/null || true
  elif command -v aplay &>/dev/null; then
    aplay -f S16_LE -r 44100 -c 1 "$WAV_FILE" 2>/dev/null || true
  fi

  rm -f "$WAV_FILE" 2>/dev/null
}

# Minimal WAV header writer for raw PCM (16-bit signed LE, mono, 44100 Hz)
_pcm_to_wav() {
  local pcm_file="$1" wav_file="$2"
  local data_size byte_rate sample_rate=44100 channels=1 bits=16
  data_size=$(wc -c < "$pcm_file" | tr -d ' ')
  byte_rate=$(( sample_rate * channels * bits / 8 ))
  local file_size=$(( data_size + 36 ))
  local block_align=$(( channels * bits / 8 ))

  # Use printf + dd to build the 44-byte WAV header
  {
    printf 'RIFF'
    _le32 "$file_size"
    printf 'WAVEfmt '
    _le32 16               # chunk size
    _le16 1                # PCM format
    _le16 "$channels"
    _le32 "$sample_rate"
    _le32 "$byte_rate"
    _le16 "$block_align"
    _le16 "$bits"
    printf 'data'
    _le32 "$data_size"
    cat "$pcm_file"
  } > "$wav_file"
}

# Little-endian integer writers (portable, no python/perl needed)
_le16() {
  local v=$1
  printf "\\$(printf '%03o' $(( v & 0xFF )))\\$(printf '%03o' $(( (v >> 8) & 0xFF )))"
}
_le32() {
  local v=$1
  printf "\\$(printf '%03o' $(( v & 0xFF )))\\$(printf '%03o' $(( (v >> 8) & 0xFF )))\\$(printf '%03o' $(( (v >> 16) & 0xFF )))\\$(printf '%03o' $(( (v >> 24) & 0xFF )))"
}

# Launch in a detached background process so the hook can exit immediately
_tts_notify "$PROMPT" "$FALLBACK" </dev/null &>/dev/null &
disown 2>/dev/null
exit 0
