#!/usr/bin/env python3
"""PreToolUse(Bash|PowerShell) hook: blocks dangerous/destructive shell commands via regex matching.

NOTE: The patterns are a suggested starting list, not a complete one. A command written another
way, such as a script file or an alias, gets past any pattern list, so keep the host's permission
rules and OS sandbox on, and add project-specific patterns to blocked-commands.json as needed.
"""

import json
import os
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
    r"\s+(?:-\S*\s+(?:[^-\s]\S*\s+)?|\d\S*\s+)*)(?:\w+=\S*\s+)*(?:\S*[/\\])?"
)

# A force push rewrites the remote's history. `push` must be git's subcommand, after only git's
# own options (`git stash push` is not a push), and the flag must be push's own, as for rm.
FORCE_PUSH = (
    CMD + r"git(?:\.exe)?(?:\s+-\S+(?:\s+[^-\s]\S*)?)*\s+push\b"
    r"(?=(?:(?!\$\(|`)[^|])*\s(?:--force(?:-with-lease|-if-includes)?\b|-[a-zA-Z]*f[a-zA-Z]*\b|\+\S))"
)

# Windows commands ignore case. PowerShell takes any unambiguous prefix of a parameter, and
# -Recurse is the only Remove-Item parameter starting with r (rm is covered above); `$(...)` there is
# an argument, not a nested command, so the flags are read past it. cmd.exe takes switches written
# together (/s/q), and Git Bash users double the slash (//s) so MSYS leaves it alone.
REMOVE_ITEM_RECURSE_FORCE = (
    r"(?i)\b(?:remove-item|ri|del|erase|rd|rmdir)\b(?=[^|]*\s-r[a-z]*\b)(?=[^|]*\s-fo[a-z]*\b)"
)
CMD_DELETE_TREE = r"(?i)\b(?:rd|rmdir|del|erase)\b(?=[^|]*(?:\s//?|/)s\b)(?=[^|]*(?:\s//?|/)q\b)"
FORMAT_DISK = (
    r"(?i)" + CMD + r"(?:(?:diskpart|format-volume|clear-disk|initialize-disk|remove-partition)\b"
    r"|format(?:\.com)?\s+[a-z]:)"
)
INVOKE_EXPRESSION = r"(?i)\|\s*iex\b|\biex\s*[($\"']|\binvoke-expression\b"

HARDCODED_DEFAULTS = [
    (RM_RECURSIVE_FORCE, "Recursive force delete blocked. Delete a tree with `rm -r <dir>` (no -f)."),
    (REMOVE_ITEM_RECURSE_FORCE, "Recursive force delete blocked."),
    (CMD_DELETE_TREE, "Recursive force delete blocked."),
    (FORCE_PUSH, "Force push blocked."),
    (r":\(\)\{.*\}", "Fork bomb blocked."),
    (r"\b(curl|wget)\s+.*\|\s*(sh|bash)", "Pipe-to-shell blocked."),
    (INVOKE_EXPRESSION, "Invoke-Expression blocked."),
    (r"\bchmod\s+777", "chmod 777 blocked."),
    (r"\bdd\s+if=.*of=/dev/", "dd to device blocked."),
    (r"\bmkfs\.", "Filesystem format blocked."),
    (FORMAT_DISK, "Disk format blocked."),
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
# PowerShell escapes with a backtick and doubles a quote inside its own kind ('it''s'); a
# backslash is a path separator, so "C:\dir\" ends at its second quote.
POWERSHELL_QUOTED = re.compile(r"`.|'(?:[^']|'')*'|\"(?:[^\"`]|`.|\"\")*\"")
# How a shell is read: its quoting, regex flags for its case rules, and its line continuation.
POSIX = (QUOTED, 0, re.compile(r"\\\r?\n"))
POWERSHELL = (POWERSHELL_QUOTED, re.IGNORECASE, re.compile(r"`\r?\n"))
# A shell's command-string argument (`sh -c '...'`, `cmd /c "..."`, `pwsh -Command "..."`) runs.
SHELL_COMMAND_ARGUMENT = re.compile(
    r"(?i)\b(?:bash|sh|zsh|dash|ksh|cmd|powershell|pwsh)(?:\.exe)?\s(?:[^|;&\n]*\s)?"
    r"(?:-[a-z]*c|-command|//?[ck])\s*$"
)


def shells(tool_name, windows=os.name == "nt" or sys.platform in ("cygwin", "msys")):
    """The readings a command gets. Codex runs PowerShell on Windows but names the tool Bash,
    and Claude Code's Bash there is Git Bash, so a Windows Bash command is read both ways."""
    if tool_name == "PowerShell":
        return (POWERSHELL,)
    return (POSIX, POWERSHELL) if windows else (POSIX,)


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


def empty_literals(cmd, quoted=QUOTED):
    """Empty inert quoted strings but keep the quotes: their text is data, and patterns
    such as `python3 -c '` still need to see that a quoted argument follows. Escapes and
    double-quoted strings holding $ or a backtick stay, since those still execute. A quoted
    command word, flag, or fragment glued to other text (`"rm"`, `'-rf'`, `-r'f'`) is part
    of the command once the shell drops the quotes, so it stays with the quotes dropped."""

    parts, previous = [], 0
    for m in quoted.finditer(cmd):
        parts.append(cmd[previous:m.start()])
        previous = m.end()
        text = m.group(0)
        if text[0] in "\\`" or (text[0] == '"' and ("$" in text or "`" in text)):
            parts.append(text)
            continue
        # Earlier quoted wrappers must already be normalized for CMD to recognize their prefix.
        before, after, inner = "".join(parts), cmd[m.end():], text[1:-1]
        command_word = command_prefix(before)
        glued = re.match(r"[\w./-]", before[-1:]) or re.match(r"[\w./'\"-]", after[:1])
        code = command_word or glued or inner.startswith("-") or SHELL_COMMAND_ARGUMENT.search(before)
        parts.append(inner if code else text[0] * 2)

    parts.append(cmd[previous:])
    return "".join(parts)


def split_commands(cmd):
    """Split on &&, ||, ;, newlines, and a background & (not the & of 2>&1 or &>)."""
    return re.split(r"\s*(?:&&|\|\||[;\n]|(?<![<>&])&(?![>&]))\s*", cmd)


# A quoted string, `$((...))` or comment (skipped whole, so `echo '<<EOF'` opens no heredoc) or a
# heredoc operator; `<<<` is a here-string, not a heredoc. Group 1 is `-` (tabs stripped); the
# delimiter is group 2 (`\TAG`), 3 (`'TAG'`), 4 (`"TAG"`) with no expansion in the body, or 5
# (`TAG`) with it.
HEREDOC_OPERATOR = re.compile(
    r"\\.|'[^']*'|\"(?:[^\"\\]|\\.)*\"|\$\(\([^)]*\)\)|(?<![^\s;&|(])#.*|(?<!<)<<(?!<)(-?)\s*(?:\\(\w+)|'(\w+)'|\"(\w+)\"|(\w+))")
# A shell reading its commands from stdin runs the body: a shell name, `$SHELL`, or `.` as a command.
SHELL_READER = re.compile(
    r"(?<![\w.-])(?:bash|sh|zsh|dash|ksh|fish|source)\b|\$\{?(?:SHELL|BASH)\b|(?:^|[;&|(]\s*)\.\s")
# What still executes in an unquoted body, which expands $(...) and backticks.
EXPANSION = re.compile(r"\$\([^)]*\)?|`[^`]*`?")


def without_heredoc_bodies(command):
    """Drop heredoc bodies, which are data (script text, commit messages) and made the patterns
    fire on what they merely mention. Kept: a body a shell reads, and in an unquoted body the
    $(...) and backtick expansions, which run. Fails closed: a body is dropped only once its
    terminator line is found, so an operator with no terminator line hides nothing."""
    lines = command.split("\n")
    kept, i = [], 0
    while i < len(lines):
        line = lines[i]
        kept.append(line)
        i += 1
        pending = []
        bodies = []
        for m in HEREDOC_OPERATOR.finditer(line):
            if m.lastindex:
                pending.append((m.group(1), m.lastindex != 5, m.group(m.lastindex)))
        for strip_tabs, no_expansion, tag in pending:
            body, end = [], i
            while end < len(lines):
                text = lines[end].rstrip("\r")
                end += 1
                if (text.lstrip("\t") if strip_tabs else text) == tag:
                    break
                body.append(text)
            else:
                kept.extend(lines[i:])
                return "\n".join(kept)
            i = end
            bodies.append((no_expansion, body))
        # A reader on the operator's line (`cat <<EOF | sh`), on the next one after a trailing `|`
        # or `\` or after the closing `)`/`}` of a group (`{ cat <<EOF ... } | sh`) runs the body.
        after = lines[i] if i < len(lines) else ""
        runs = bool(SHELL_READER.search(line) or line.rstrip().endswith(("|", "\\"))
                    or (re.match(r"\s*[)}]", after) and SHELL_READER.search(after)))
        for no_expansion, body in bodies:
            if runs:
                kept.extend(body)
            elif not no_expansion:
                kept.extend(e for text in body for e in EXPANSION.findall(text))
    return "\n".join(kept)


def check_command(command, patterns, readings=(POSIX,)):
    """Check a command against all blocked patterns. Returns (blocked, message) or (False, None)."""
    for quoted, flags, continuation in readings:
        # PowerShell has no heredocs; its here-strings are quoted text the patterns skip. A Bash
        # command's PowerShell reading drops heredoc bodies too: there `<<` is a parse error, so
        # the whole script, body included, never runs.
        text = without_heredoc_bodies(command) if POSIX in readings else command
        for segment in split_commands(empty_literals(continuation.sub(" ", text), quoted)):
            segment = segment.strip()
            if not segment:
                continue

            for regex, message in patterns:
                try:
                    if re.search(regex, segment, flags):
                        return True, message
                except re.error:
                    continue

    return False, None


def main():
    # Read JSON from stdin
    try:
        data = json.load(sys.stdin)
        command = data.get("tool_input", {}).get("command", "")
        readings = shells(data.get("tool_name"))
    except (json.JSONDecodeError, AttributeError, TypeError):
        # Malformed input - fail closed
        print("Hook error: blocking unknown command for safety", file=sys.stderr)
        sys.exit(2)

    if not command:
        sys.exit(0)

    blocked, message = check_command(command, load_config(), readings)

    if blocked:
        print(f"BLOCKED: {message}", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
