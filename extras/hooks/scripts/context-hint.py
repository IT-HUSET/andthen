#!/usr/bin/env python3
"""Stop hook for Claude Code and Codex: shows the user the session's context size once it
passes a threshold, so they can choose a fresh session.

The model cannot see its own context size, and long interactive sessions decline. Above
CONTEXT_HINT_THRESHOLD tokens (default 200000) the hook prints a `systemMessage` once per 50k
step: the host shows it to the user and runs no model turn, where blocking the stop cost a full
turn at 200k+ tokens to relay it. It stays silent below the threshold, while the agent is already
continuing because of a Stop hook, while the Stop input lists in-flight `background_tasks` (the
turn only ends to wait for them), and on unattended runs (Agent SDK, `claude -p`, `codex exec`).
Fails open: any error prints nothing and exits 0.
"""

import json
import os
import re
import sys
import tempfile

STEP = 50_000
MESSAGE = (
    "Context size: this session is at ~{k}k tokens, and long sessions lose detail. "
    "Consider a fresh session, with a handoff or brief first if this session knows anything not "
    "yet written down, and hand remaining pinned work to a subagent."
)
# Entrypoints (Claude Code transcripts) and rollout sources (Codex) of runs with nobody to advise.
UNATTENDED_SOURCES = ("exec", "mcp", "claude-code-github-action")


def lines_from_end(path, chunk=1 << 16):
    """Yield the file's lines last first, so a multi-MB transcript costs only its tail."""
    with open(path, "rb") as f:
        pos = f.seek(0, os.SEEK_END)
        pieces = []  # the line being read, its later pieces first; joined once, as one line can be MBs
        while pos > 0:
            size = min(chunk, pos)
            pos -= size
            f.seek(pos)
            first, *lines = f.read(size).split(b"\n")
            if lines:
                yield lines.pop() + b"".join(reversed(pieces))
                yield from reversed(lines)
                pieces = []
            pieces.append(first)
        yield b"".join(reversed(pieces))


def records_from_end(path, *markers):
    """Parse only lines holding a marker: a pasted image or PDF makes a line MBs of base64."""
    for line in lines_from_end(path):
        if not any(m in line for m in markers):
            continue
        try:
            record = json.loads(line)
        except ValueError:
            continue  # the line the host is still writing
        if isinstance(record, dict):
            yield record


def context_tokens(path):
    """The last request's input size: Claude Code's assistant usage, or Codex's token_count."""
    for r in records_from_end(path, b'"usage"', b'"token_count"'):
        usage = (r.get("message") or {}).get("usage") if r.get("type") == "assistant" else None
        if isinstance(usage, dict):
            return sum(usage.get(k) or 0 for k in
                       ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
        payload = r.get("payload") or {}
        if r.get("type") == "event_msg" and payload.get("type") == "token_count":
            last = (payload.get("info") or {}).get("last_token_usage")
            if last:
                return last["input_tokens"]
    return None


def is_interactive(path):
    """Whether a person is at the session, read from its first records: Claude Code stamps each
    record with the `entrypoint` it was started from (`cli`, `claude-desktop`, `sdk-cli`, ...),
    Codex's `session_meta` carries a `source` (`vscode`, `exec`, or a subagent's dict). A
    transcript saying neither is unknown, and unknown stays silent."""
    with open(path, "rb") as f:
        for _, line in zip(range(200), f):
            if b'"entrypoint"' not in line and b'"session_meta"' not in line:
                continue
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if not isinstance(record, dict):
                continue
            if record.get("entrypoint"):
                entrypoint = record["entrypoint"]
                return not (entrypoint.startswith("sdk") or entrypoint in UNATTENDED_SOURCES)
            if record.get("type") == "session_meta":
                source = (record.get("payload") or {}).get("source")
                return source is not None and not isinstance(source, dict) and source not in UNATTENDED_SOURCES
    return False


def hint(event):
    path = event.get("transcript_path")
    if event.get("stop_hook_active") or not path:
        return None
    threshold = int(os.environ.get("CONTEXT_HINT_THRESHOLD", 200_000))
    tokens = context_tokens(path)
    if tokens is None or tokens < threshold:
        return None
    step = (tokens - threshold) // STEP
    session = re.sub(r"[^A-Za-z0-9_-]", "", str(event.get("session_id") or "")) or "default"
    state = os.path.join(tempfile.gettempdir(), f"context-hint-{session}")
    try:
        with open(state, encoding="utf-8") as f:
            if int(f.read()) == step:
                return None
    except FileNotFoundError:
        pass
    if not is_interactive(path) or event.get("background_tasks"):
        return None
    # Record the step first: a failed write leaves the hook silent rather than repeating each turn.
    fd = os.open(state, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(str(step))
    return MESSAGE.format(k=tokens // 1000)


def main():
    try:
        message = hint(json.load(sys.stdin))
    except Exception:
        return
    if message:
        print(json.dumps({"systemMessage": message}))


if __name__ == "__main__":
    main()
