#!/usr/bin/env python3
"""Stop hook for Claude Code and Codex: tells the model the session's context size once it
passes a threshold, so its closing advice can suggest a fresh session.

The model cannot see its own context size, and long interactive sessions decline. Above
CONTEXT_HINT_THRESHOLD tokens (default 200000) the hook blocks the stop once per 50k step with
a reason, and the model adds a closing line on how to proceed. It stays silent below the
threshold, while the agent is already continuing because of a Stop hook, and on a run with a
single prompt, which is headless or unattended. Fails open: any error prints nothing and exits 0.
"""

import json
import os
import re
import sys
import tempfile

STEP = 50_000
REASON = (
    "Context-size hint: this session is at ~{k}k tokens, and long sessions lose detail. "
    "Add one closing line of advice on how to proceed: continue here, or start a fresh session, "
    "writing a handoff or brief first if this session knows anything not yet written down. "
    "If the work is mid-task and continuing here is right, add nothing. "
    "This hint is for this reply only; never carry it into a summary or a later turn."
)


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


def has_second_prompt(path):
    """Claude Code marks typed prompts `origin.kind: human`, unlike tool results and task
    notifications; Codex starts one task per prompt."""
    prompts = 0
    for r in records_from_end(path, b'"human"', b'"task_started"'):
        claude = r.get("type") == "user" and (r.get("origin") or {}).get("kind") == "human"
        codex = r.get("type") == "event_msg" and (r.get("payload") or {}).get("type") == "task_started"
        prompts += claude or codex
        if prompts > 1:
            return True
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
    if not has_second_prompt(path):
        return None
    # Record the step first: a failed write leaves the hook silent rather than blocking each turn.
    fd = os.open(state, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(str(step))
    return REASON.format(k=tokens // 1000)


def main():
    try:
        reason = hint(json.load(sys.stdin))
    except Exception:
        return
    if reason:
        print(json.dumps({"decision": "block", "reason": reason}))


if __name__ == "__main__":
    main()
