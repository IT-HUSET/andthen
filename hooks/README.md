# Hooks

Standalone Claude Code hooks; `context-hint.py` also runs on Codex. Pick the ones you need and add them to your settings individually.

## Available Hooks

| Script | Hook Event | Matcher | Purpose |
|--------|-----------|---------|---------|
| `block-dangerous-commands.py` | PreToolUse | `Bash` | Blocks destructive shell commands (rm -rf, fork bombs, pipe-to-shell, etc.) |
| `notify.sh` | UserPromptSubmit, Stop, Notification | -- | Desktop notifications when Claude finishes or needs attention |
| `notify-elevenlabs.sh` | UserPromptSubmit, Stop, Notification | -- | Voice notifications via ElevenLabs TTS API |
| `context-hint.py` | Stop | -- | Tells the agent the session's context size past a threshold, so it can suggest a fresh session (Claude Code and Codex) |

Claude Code re-reads the project-root `CLAUDE.md` after compaction on its own, so no hook is needed to keep project rules in context.

## Prerequisites

- **Python 3.8+** (for `block-dangerous-commands.py` and `context-hint.py`)
- **jq** (recommended; scripts have fallback to Python-based or grep/sed JSON parsing)
- **curl** (for ElevenLabs voice notifications)

## Installation

Two approaches – pick one per hook:

### Option A: Copy to `~/.claude/hooks/` (self-contained)

```bash
# Create directories
mkdir -p ~/.claude/hooks/scripts ~/.claude/hooks/configs

# Copy scripts you want (pick any combination)
cp hooks/scripts/block-dangerous-commands.py ~/.claude/hooks/scripts/
cp hooks/scripts/notify.sh                   ~/.claude/hooks/scripts/
cp hooks/scripts/notify-elevenlabs.sh        ~/.claude/hooks/scripts/
cp hooks/scripts/context-hint.py             ~/.claude/hooks/scripts/

# Copy config
cp hooks/configs/blocked-commands.json       ~/.claude/hooks/configs/

# Make scripts executable
chmod +x ~/.claude/hooks/scripts/*.py ~/.claude/hooks/scripts/*.sh
```

Then reference as `~/.claude/hooks/scripts/<script>` in settings.

### Option B: Reference from repo (auto-updates with pulls)

Point settings directly at the cloned repo path.

Config customization still works – scripts check `~/.claude/hooks/configs/` first (user override), then script-relative `../configs/` (repo defaults), then hardcoded defaults.

---

## Hook Details & Settings Configuration

Add entries to `~/.claude/settings.json` (user-level, global) or `.claude/settings.json` (project-level, shared with team) for each hook you want. Use `.claude/settings.local.json` for project-local overrides that shouldn't be committed.

---

### block-dangerous-commands.py

Intercepts Bash commands and blocks destructive patterns: `rm -rf`, fork bombs, `chmod 777`, `dd` to devices, `mkfs`, pipe-to-shell (`curl | sh`), interpreter escapes (`bash -c`, `eval`, `python3 -c`), network tools (`nc`, `socat`, `telnet`), system control (`shutdown`, `reboot`), privilege commands (`chown`, `passwd`, `useradd`), and obfuscated execution (`base64 | bash`, reverse shells). Text inside quotes is treated as data, so a commit message or search pattern that names these commands passes, unless it contains `$(...)` or backticks, which still execute – so a `-m "$(cat <<'EOF' … EOF)"` commit message is scanned too. Quoting the command name or a flag (`"rm" -rf`, `rm '-rf'`) does not hide it. Tool names match only where they run as a command (after a separator, pipe, `sudo`, `timeout`, `xargs`, and similar wrappers), so `grep nc` passes and `timeout 5 nc -z host 80` does not.

> **Note/Disclaimer/Warning:** This is not an exhaustive list of dangerous commands. It covers common destructive patterns but cannot catch every possible risky operation. Always review agent commands, keep Claude Code's built-in permission system enabled, and add project-specific patterns to your local `blocked-commands.json` as needed.

**Config**: `blocked-commands.json` – customize blocked patterns. Copy to `~/.claude/hooks/configs/` to override defaults.

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

Sends desktop notifications when Claude finishes a task (Stop event) or needs attention (permission prompt, idle). Uses macOS `osascript`, Linux `notify-send`, or terminal bell as fallback. Debounces to one notification per 5s, and skips the Stop notification when the turn took under 30s, since you are likely still watching. The `UserPromptSubmit` entry records when each turn starts; without it, every Stop notifies.

No config file. No dependencies beyond Bash (jq optional, has grep/sed fallback).

**Add all three entries to settings** – under `hooks.UserPromptSubmit`, `hooks.Stop`, and `hooks.Notification`:

```json
"UserPromptSubmit": [{
  "hooks": [{
    "type": "command",
    "command": "bash ~/.claude/hooks/scripts/notify.sh",
    "timeout": 10
  }]
}],
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

**Add all three entries to settings** – same structure as `notify.sh`:

```json
"UserPromptSubmit": [{
  "hooks": [{
    "type": "command",
    "command": "bash ~/.claude/hooks/scripts/notify-elevenlabs.sh",
    "timeout": 10
  }]
}],
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

### context-hint.py

The model cannot see how large its context has grown, and long interactive sessions get worse well before the window fills. When the agent is about to end its turn, this hook reads the size of the last request from the session transcript. Past the threshold it blocks the stop once, telling the model the size, and the model adds one closing line: continue here, or start a fresh session after writing a handoff, or nothing when it is mid-task and should go on. You decide.

- **Threshold**: `CONTEXT_HINT_THRESHOLD` tokens, default `200000`, one absolute number on both hosts, because the decline tracks tokens rather than the window size. The hint fires on crossing it and again at every further 50k. A compacted session reads small again, so the hint returns once it regrows past the threshold.
- **Silent** below the threshold, while the agent is already continuing because of a Stop hook, and in a run with a single prompt (headless, `--auto`, or otherwise unattended). Claude Code subagents end on `SubagentStop`, so they never reach it.
- **Cost**: each firing is one extra model turn. One small state file per session in `$TMPDIR`.
- **Fails open**: any error prints nothing and lets the stop through.

No config file. Python 3 standard library only. Set the threshold in your shell profile, or for Claude Code in the settings `env` block, as for [ElevenLabs](#elevenlabs-setup).

**Claude Code** – add to the `hooks.Stop` array in settings, beside any `notify.sh` entry:

```json
{
  "hooks": [{
    "type": "command",
    "command": "python3 ~/.claude/hooks/scripts/context-hint.py",
    "timeout": 10
  }]
}
```

**Codex** – hooks are on by default (`[features] hooks = true` in `config.toml` turns them back on). Add the same entry to `~/.codex/hooks.json` or a repo's `.codex/hooks.json`, pointing at wherever you copied the script; Codex asks you to trust a new hook in `/hooks` before it runs it, and hands the model the hint as a new prompt.

```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/hooks/scripts/context-hint.py",
        "timeout": 10
      }]
    }]
  }
}
```

In `config.toml` the same entry is a `[[hooks.Stop]]` table holding a `[[hooks.Stop.hooks]]` table with `type`, `command`, and `timeout`.

---

## Full Example

Complete `~/.claude/settings.json` with the command blocker and desktop notifications enabled:

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
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "bash ~/.claude/hooks/scripts/notify.sh",
        "timeout": 10
      }]
    }],
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

2. Set `ELEVENLABS_API_KEY` – pick one approach:

   **Shell profile** (`~/.zshrc`, `~/.bashrc`, etc.):
   ```bash
   export ELEVENLABS_API_KEY="your-api-key-here"
   ```

   **Claude Code settings** (`~/.claude/settings.json` – user-level, always available regardless of how Claude Code is launched):
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
