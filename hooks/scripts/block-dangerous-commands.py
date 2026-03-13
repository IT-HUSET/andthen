#!/usr/bin/env python3
"""PreToolUse(Bash) hook: blocks dangerous/destructive shell commands via regex matching."""

import json
import os
import re
import sys
from pathlib import Path

HARDCODED_DEFAULTS = [
    (r"\brm\s+.*-[rf]", "Destructive rm blocked."),
    (r":\(\)\{.*\}", "Fork bomb blocked."),
    (r"\b(curl|wget)\s+.*\|\s*(sh|bash)", "Pipe-to-shell blocked."),
    (r"\bchmod\s+777", "chmod 777 blocked."),
    (r"\bdd\s+if=.*of=/dev/", "dd to device blocked."),
    (r"\bmkfs\.", "Filesystem format blocked."),
]

HARDCODED_SAFE_PIPE_TARGETS = ["jq", "grep", "sort", "wc", "head", "tail", "less", "cat", "tee", "tr", "uniq"]


def load_config():
    """Load patterns from blocked-commands.json, fall back to hardcoded defaults."""
    # 1. User override
    user_config = Path.home() / ".claude" / "hooks" / "configs" / "blocked-commands.json"
    # 2. Repo defaults (script-relative ../configs/)
    repo_config = Path(__file__).resolve().parent.parent / "configs" / "blocked-commands.json"

    config_path = user_config if user_config.is_file() else repo_config
    try:
        with open(config_path) as f:
            config = json.load(f)
        patterns = [(p["regex"], p["message"]) for p in config["patterns"]]
        safe_targets = config.get("safe_pipe_targets", HARDCODED_SAFE_PIPE_TARGETS)
        return patterns, safe_targets
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return HARDCODED_DEFAULTS, HARDCODED_SAFE_PIPE_TARGETS


def strip_single_quotes(cmd):
    """Remove contents of single-quoted strings (bash literals are safe)."""
    return re.sub(r"'[^']*'", "", cmd)


def split_commands(cmd):
    """Split on &&, ||, ; to get individual command segments."""
    return re.split(r"\s*(?:&&|\|\||;)\s*", cmd)


def is_safe_pipe(segment, safe_targets):
    """Check if a pipe's target is in the safe list."""
    if "|" not in segment:
        return False
    parts = segment.split("|")
    if len(parts) < 2:
        return False
    # Get the final pipe target command name
    target = parts[-1].strip().split()[0] if parts[-1].strip() else ""
    return target in safe_targets


def check_command(command, patterns, safe_targets):
    """Check a command against all blocked patterns. Returns (blocked, message) or (False, None)."""
    processed = strip_single_quotes(command)
    segments = split_commands(processed)

    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue

        for regex, message in patterns:
            try:
                if re.search(regex, segment):
                    # For pipe-to-shell patterns, check if target is safe
                    if "|" in segment and is_safe_pipe(segment, safe_targets):
                        continue
                    return True, message
            except re.error:
                continue

    return False, None


def main():
    # Read JSON from stdin
    try:
        data = json.load(sys.stdin)
        command = data.get("tool_input", {}).get("command", "")
    except (json.JSONDecodeError, AttributeError, TypeError):
        # Malformed input - fail closed
        print("Hook error: blocking unknown command for safety", file=sys.stderr)
        sys.exit(2)

    if not command:
        sys.exit(0)

    patterns, safe_targets = load_config()
    blocked, message = check_command(command, patterns, safe_targets)

    if blocked:
        print(f"BLOCKED: {message}", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
