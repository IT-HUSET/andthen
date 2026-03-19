# Hooks

Standalone Claude Code hooks. Pick the ones you need and add them to your settings individually.

## Available Hooks

| Script | Hook Event | Matcher | Purpose |
|--------|-----------|---------|---------|
| `block-dangerous-commands.py` | PreToolUse | `Bash` | Blocks destructive shell commands (rm -rf, fork bombs, pipe-to-shell, etc.) |
| `notify.sh` | Stop, Notification | -- | Desktop notifications when Claude finishes or needs attention |
| `notify-elevenlabs.sh` | Stop, Notification | -- | Voice notifications via ElevenLabs TTS API |
| `reinject-context.sh` | SessionStart | `compact` | Re-injects critical rules after context compaction |

## Prerequisites

- **Python 3.8+** (for `block-dangerous-commands.py`)
- **jq** (recommended; scripts have fallback to Python-based or grep/sed JSON parsing)
- **curl** (for ElevenLabs voice notifications)

## Installation

Two approaches — pick one per hook:

### Option A: Copy to `~/.claude/hooks/` (self-contained)

```bash
# Create directories
mkdir -p ~/.claude/hooks/scripts ~/.claude/hooks/configs

# Copy scripts you want (pick any combination)
cp hooks/scripts/block-dangerous-commands.py ~/.claude/hooks/scripts/
cp hooks/scripts/notify.sh                   ~/.claude/hooks/scripts/
cp hooks/scripts/notify-elevenlabs.sh        ~/.claude/hooks/scripts/
cp hooks/scripts/reinject-context.sh         ~/.claude/hooks/scripts/

# Copy config
cp hooks/configs/blocked-commands.json       ~/.claude/hooks/configs/

# Make scripts executable
chmod +x ~/.claude/hooks/scripts/*.py ~/.claude/hooks/scripts/*.sh
```

Then reference as `~/.claude/hooks/scripts/<script>` in settings.

### Option B: Reference from repo (auto-updates with pulls)

Point settings directly at the cloned repo path.

Config customization still works — scripts check `~/.claude/hooks/configs/` first (user override), then script-relative `../configs/` (repo defaults), then hardcoded defaults.

---

## Hook Details & Settings Configuration

Add entries to `~/.claude/settings.json` (user-level, global) or `.claude/settings.json` (project-level, shared with team) for each hook you want. Use `.claude/settings.local.json` for project-local overrides that shouldn't be committed.

---

### block-dangerous-commands.py

Intercepts Bash commands and blocks destructive patterns: `rm -rf`, fork bombs, `chmod 777`, `dd` to devices, `mkfs`, pipe-to-shell (`curl | sh`), interpreter escapes (`bash -c`, `eval`, `python3 -c`), network tools (`nc`, `socat`, `telnet`), system control (`shutdown`, `reboot`), privilege commands (`chown`, `passwd`, `useradd`), and obfuscated execution (`base64 | bash`, reverse shells). Allows safe pipe targets like `jq`, `grep`, `sort`.

> **Note/Disclaimer/Warning:** This is not an exhaustive list of dangerous commands. It covers common destructive patterns but cannot catch every possible risky operation. Always review agent commands, keep Claude Code's built-in permission system enabled, and add project-specific patterns to your local `blocked-commands.json` as needed.

**Config**: `blocked-commands.json` — customize blocked patterns and safe pipe targets. Copy to `~/.claude/hooks/configs/` to override defaults.

**Add to `hooks.PreToolUse` array in settings:**

```json
{
  "matcher": "Bash",
  "hooks": [{
    "type": "command",
    "command": "python3 ~/.claude/hooks/scripts/block-dangerous-commands.py",
    "statusMessage": "Validating command safety..."
  }]
}
```

---

### notify.sh

Sends desktop notifications when Claude finishes a task (Stop event) or needs attention (permission prompt, idle). Uses macOS `osascript`, Linux `notify-send`, or terminal bell as fallback. Includes smart debouncing (5s) and suppresses Stop notifications for short sessions (<30s).

No config file. No dependencies beyond Bash (jq optional, has grep/sed fallback).

**Add both entries to settings** — one under `hooks.Stop`, one under `hooks.Notification`:

```json
"Stop": [{
  "hooks": [{
    "type": "command",
    "command": "bash ~/.claude/hooks/scripts/notify.sh",
    "timeout": 10
  }]
}],
"Notification": [{
  "matcher": "permission_prompt|idle_prompt",
  "hooks": [{
    "type": "command",
    "command": "bash ~/.claude/hooks/scripts/notify.sh",
    "timeout": 10
  }]
}]
```

---

### notify-elevenlabs.sh

Voice notification variant using the ElevenLabs TTS API. Same events and debounce logic as `notify.sh`, but speaks the notification aloud instead of showing a desktop popup. Falls back silently if API key is not set or the API is unreachable.

No config file. Requires `ELEVENLABS_API_KEY` env var and `curl`. See [ElevenLabs Setup](#elevenlabs-setup).

**Add both entries to settings** — same structure as `notify.sh`:

```json
"Stop": [{
  "hooks": [{
    "type": "command",
    "command": "bash ~/.claude/hooks/scripts/notify-elevenlabs.sh",
    "timeout": 10
  }]
}],
"Notification": [{
  "matcher": "permission_prompt|idle_prompt",
  "hooks": [{
    "type": "command",
    "command": "bash ~/.claude/hooks/scripts/notify-elevenlabs.sh",
    "timeout": 10
  }]
}]
```

---

### reinject-context.sh

Re-injects `CLAUDE.md` (project instructions) into Claude's context after automatic compaction. Without this, rules from CLAUDE.md can be lost when the conversation gets long and context is compressed. Triggers only on the `compact` matcher (i.e., when Claude Code compacts context).

No config file. Requires `CLAUDE.md` to exist in the project directory.

**Add to `hooks.SessionStart` in settings:**

```json
"SessionStart": [{
  "matcher": "compact",
  "hooks": [{
    "type": "command",
    "command": "bash ~/.claude/hooks/scripts/reinject-context.sh"
  }]
}]
```

---

## Full Example

Complete `~/.claude/settings.json` with all included hooks enabled:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "python3 ~/.claude/hooks/scripts/block-dangerous-commands.py",
          "statusMessage": "Validating command safety..."
        }]
      }
    ],
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "bash ~/.claude/hooks/scripts/notify.sh",
        "timeout": 10
      }]
    }],
    "Notification": [{
      "matcher": "permission_prompt|idle_prompt",
      "hooks": [{
        "type": "command",
        "command": "bash ~/.claude/hooks/scripts/notify.sh",
        "timeout": 10
      }]
    }],
    "SessionStart": [{
      "matcher": "compact",
      "hooks": [{
        "type": "command",
        "command": "bash ~/.claude/hooks/scripts/reinject-context.sh"
      }]
    }]
  }
}
```

## Config Customization

Default configs live in `hooks/configs/`. To customize, copy to `~/.claude/hooks/configs/` and edit. Scripts check:
1. `~/.claude/hooks/configs/<name>.json` (user override)
2. Script-relative `../configs/<name>.json` (repo defaults)
3. Hardcoded fail-closed defaults

## ElevenLabs Setup

1. Get an API key from [elevenlabs.io](https://elevenlabs.io/app/settings/api-keys).

2. Set `ELEVENLABS_API_KEY` — pick one approach:

   **Shell profile** (`~/.zshrc`, `~/.bashrc`, etc.):
   ```bash
   export ELEVENLABS_API_KEY="your-api-key-here"
   ```

   **Claude Code settings** (`~/.claude/settings.json` — user-level, always available regardless of how Claude Code is launched):
   ```json
   {
     "env": {
       "ELEVENLABS_API_KEY": "your-api-key-here"
     }
   }
   ```

3. Optionally override defaults the same way:
   ```bash
   export ELEVENLABS_VOICE_ID="id1,id2,id3"   # comma-separated list; one picked at random each time
   export ELEVENLABS_MODEL_ID="eleven_flash_v2_5"         # default: eleven_flash_v2_5
   ```

> **Free tier limitation**: ElevenLabs free accounts cannot use premade/library voices via the API. You'll need a paid plan or a custom cloned voice. The voice ID in the hook must match a voice accessible to your account.
