#!/usr/bin/env python3
"""PreToolUse(Bash) hook: blocks dangerous/destructive shell commands via regex matching.

NOTE: This is not an exhaustive list of dangerous commands. It covers common destructive
patterns but cannot catch every possible risky operation. Always keep Claude Code's built-in
permission system enabled, and add project-specific patterns to blocked-commands.json as needed.
"""

import json
import re
import sys
from pathlib import Path

# rm's own flags: stop at a pipe or a nested command, whose flags are not rm's.
RM_RECURSIVE_FORCE = (
    r"\brm(?=(?:(?!\$\(|`)[^|])*\s(?:-[a-zA-Z]*[rR][a-zA-Z]*|--recursive)\b)"
    r"(?=(?:(?!\$\(|`)[^|])*\s(?:-[a-zA-Z]*f[a-zA-Z]*|--force)\b)"
)
WRAPPER_OPTIONS = {
    "sudo": {"-u", "-g", "-h", "-p", "-C", "-T", "-r", "-t", "-D", "-R",
             "--user", "--group", "--host", "--prompt", "--close-from", "--command-timeout",
             "--role", "--type", "--chdir", "--chroot"},
    "xargs": {"-a", "-d", "-E", "-I", "-J", "-L", "-n", "-P", "-R", "-S", "-s",
              "--arg-file", "--delimiter", "--max-args", "--max-procs", "--max-chars"},
    "env": {"-u", "-C", "-S", "--unset", "--chdir", "--split-string"},
    "exec": {"-a"},
    "nohup": set(),
    "timeout": {"-s", "-k", "--signal", "--kill-after"},
    "command": set(),
    "time": {"-f", "-o", "--format", "--output"},
    "nice": {"-n", "--adjustment"},
    "if": set(), "then": set(), "do": set(), "while": set(), "until": set(),
}
# Command position, so a tool name passed as an argument (`grep nc`) is not a match: segment
# start, after a pipe, subshell, group or `!`, or after a wrapper and its options, plus any
# VAR=value prefixes and a path.
CMD = (
    r"(?:^|[|(`{!]\s*|\b(?:" + "|".join(WRAPPER_OPTIONS) + r")"
    r"\s+(?:-\S*\s+(?:[^-\s]\S*\s+)?|\d\S*\s+)*)(?:\w+=\S*\s+)*(?:\S*/)?"
)

HARDCODED_DEFAULTS = [
    (RM_RECURSIVE_FORCE, "Recursive force delete blocked."),
    (r":\(\)\{.*\}", "Fork bomb blocked."),
    (r"\b(curl|wget)\s+.*\|\s*(sh|bash)", "Pipe-to-shell blocked."),
    (r"\bchmod\s+777", "chmod 777 blocked."),
    (r"\bdd\s+if=.*of=/dev/", "dd to device blocked."),
    (r"\bmkfs\.", "Filesystem format blocked."),
    (CMD + r"(nc|netcat|ncat)\b", "Netcat blocked."),
    (CMD + r"socat\b", "Socat blocked."),
    (CMD + r"telnet\b", "Telnet blocked."),
    (CMD + r"(shutdown|reboot|halt|poweroff)\b", "System shutdown/reboot blocked."),
    (CMD + r"(fdisk|parted)\b", "Disk partitioning blocked."),
    (CMD + r"(mount|umount)\b", "Filesystem mount/unmount blocked."),
    (CMD + r"(passwd|useradd|userdel|usermod)\b", "User management blocked."),
    (CMD + r"chown\b", "Ownership change blocked."),
    (r"\bcrontab\s+-r\b", "Crontab wipe blocked."),
    (r"\bbase64\b.*\|\s*(sh|bash|zsh|dash|ksh)\b", "Encoded payload execution blocked."),
    (r"bash\s+-i\s+>&\s*/dev/tcp/", "Reverse shell blocked."),
]

# One pass over escapes and both quote styles, so an apostrophe inside "..." or an escaped \'
# never pairs with a later quote and hides the command between them.
QUOTED = re.compile(r"\\.|'[^']*'|\"(?:[^\"\\]|\\.)*\"")


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
        return [(p["regex"], p["message"]) for p in config["patterns"]]
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return HARDCODED_DEFAULTS


def command_prefix(prefix):
    """Recognize wrapper prefixes without consuming the executable as an option value."""
    if prefix and not prefix[-1].isspace() and prefix[-1] not in ";&|(`{!\n":
        return False
    words = re.split(r"[;&|(`{!\n]", prefix)[-1].split()
    i = 0
    while i < len(words):
        if re.match(r"\w+=", words[i]):
            i += 1
            continue
        wrapper = words[i].rsplit("/", 1)[-1]
        if wrapper not in WRAPPER_OPTIONS:
            return False
        i += 1
        while i < len(words) and words[i].startswith("-"):
            option = words[i]
            i += 1
            if option == "--":
                break
            if wrapper == "command" and not option.startswith("--") and any(
                    flag in option[1:] for flag in "vV"):
                return False
            takes_value = option in WRAPPER_OPTIONS[wrapper]
            if not option.startswith("--"):
                for j, flag in enumerate(option[1:], 1):
                    if "-" + flag in WRAPPER_OPTIONS[wrapper]:
                        takes_value = j == len(option) - 1
                        break
            if takes_value:
                if i == len(words):
                    return False
                i += 1
        if wrapper == "timeout":
            if i == len(words):
                # Its duration is part of the prefix CMD matches, including when quoted.
                return True
            i += 1
    return True


def empty_literals(cmd):
    """Empty inert quoted strings but keep the quotes: their text is data, and patterns
    such as `python3 -c '` still need to see that a quoted argument follows. Escapes and
    double-quoted strings holding $ or a backtick stay, since those still execute. A quoted
    command word, flag, or fragment glued to other text (`"rm"`, `'-rf'`, `-r'f'`) is part
    of the command once the shell drops the quotes, so it stays with the quotes dropped."""

    parts, previous = [], 0
    for m in QUOTED.finditer(cmd):
        parts.append(cmd[previous:m.start()])
        previous = m.end()
        text = m.group(0)
        if text[0] == "\\" or (text[0] == '"' and ("$" in text or "`" in text)):
            parts.append(text)
            continue
        # Earlier quoted wrappers must already be normalized for CMD to recognize their prefix.
        before, after, inner = "".join(parts), cmd[m.end():], text[1:-1]
        command_word = command_prefix(before)
        glued = re.match(r"[\w./-]", before[-1:]) or re.match(r"[\w./'\"-]", after[:1])
        parts.append(inner if command_word or glued or inner.startswith("-") else text[0] * 2)

    parts.append(cmd[previous:])
    return "".join(parts)


def split_commands(cmd):
    """Split on &&, ||, ;, newlines, and a background & (not the & of 2>&1 or &>)."""
    return re.split(r"\s*(?:&&|\|\||[;\n]|(?<![<>&])&(?![>&]))\s*", cmd)


def check_command(command, patterns):
    """Check a command against all blocked patterns. Returns (blocked, message) or (False, None)."""
    for segment in split_commands(empty_literals(command)):
        segment = segment.strip()
        if not segment:
            continue

        for regex, message in patterns:
            try:
                if re.search(regex, segment):
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

    blocked, message = check_command(command, load_config())

    if blocked:
        print(f"BLOCKED: {message}", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
