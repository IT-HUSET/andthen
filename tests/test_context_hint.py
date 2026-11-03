#!/usr/bin/env python3
"""Tests for hooks/scripts/context-hint.py.

    python3 -m unittest tests.test_context_hint

Drives the real script through stdin with each host's Stop input and a transcript
shaped like the host's own: a Claude Code session JSONL and a Codex rollout. Above
the threshold the hook prints a user-facing `systemMessage` once per step; anything
else must stay silent and exit 0, and it never blocks the stop, because a block costs
a model turn. TMPDIR isolates the per-session state.
"""

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "hooks/scripts/context-hint.py"


def claude_transcript(tokens, prompts=2, entrypoint="claude-desktop"):
    """Each typed prompt is answered through a tool call, whose result Claude Code records as a
    user entry, and a subagent's task notification; the session ends on a request of `tokens`,
    whose entry writes a file longer than the hook's read chunk, and a subagent's usage summary,
    which is not the session's own size."""
    entries = []
    for i in range(prompts):
        entries += [
            {"type": "user", "origin": {"kind": "human"}, "message": {"role": "user", "content": f"prompt {i}"}},
            {"type": "assistant", "message": {"role": "assistant", "usage": {"input_tokens": 1000}}},
            {"type": "user", "toolUseResult": {}, "message": {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": "t1", "content": "ok"}]}},
            {"type": "user", "origin": {"kind": "task-notification"},
             "message": {"role": "user", "content": "<task-notification>done</task-notification>"}},
        ]
    entries += [
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "Write", "input": {"content": "x" * 200_000}}], "usage": {
            "input_tokens": 2, "cache_creation_input_tokens": 1000, "cache_read_input_tokens": tokens - 1002}}},
        {"type": "attachment", "attachment": {"origin": {"kind": "task-notification"},
                                              "usage": {"totalTokens": 900_000}}},
        {"type": "system", "subtype": "stop_hook_summary"},
    ]
    # Claude Code stamps every record with the entrypoint the session started from.
    return [{**e, "entrypoint": entrypoint} if entrypoint else e for e in entries]


def codex_rollout(tokens, prompts=2, source="vscode"):
    """Codex injects AGENTS.md as a user message and starts one task per prompt."""
    records = [
        {"type": "session_meta", "payload": {"id": "s1", "source": source}},
        {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [
            {"type": "input_text", "text": "# AGENTS.md instructions for /repo"}]}},
    ]
    for i in range(prompts):
        records += [
            {"type": "event_msg", "payload": {"type": "task_started", "model_context_window": 258400}},
            {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [
                {"type": "input_text", "text": f"prompt {i}"}]}},
            {"type": "event_msg", "payload": {"type": "token_count", "info": {
                "last_token_usage": {"input_tokens": 1000}, "model_context_window": 258400}}},
        ]
    records.append({"type": "event_msg", "payload": {"type": "token_count", "info": {
        "last_token_usage": {"input_tokens": tokens, "cached_input_tokens": tokens - 500},
        "model_context_window": 258400}}})
    return records


class ContextHintTest(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.transcript = self.tmp / "session.jsonl"
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("CONTEXT_HINT_")}
        self.env.update(TMPDIR=str(self.tmp), TMP=str(self.tmp), TEMP=str(self.tmp))

    def write(self, records):
        self.transcript.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")

    def stop(self, env=None, **fields):
        payload = {"session_id": "s1", "hook_event_name": "Stop", "transcript_path": str(self.transcript),
                   "stop_hook_active": False, **fields}
        proc = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps(payload), capture_output=True,
                              text=True, env={**self.env, **(env or {})})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stderr, "", "stderr on exit 0 is noise in the user's transcript")
        return proc.stdout

    def assertHint(self, out, tokens_k):
        output = json.loads(out)
        # A systemMessage reaches the user without a model turn; decision: block would cost one.
        self.assertEqual(list(output), ["systemMessage"])
        self.assertIn(f"~{tokens_k}k tokens", output["systemMessage"])
        self.assertIn("fresh session", output["systemMessage"])
        self.assertIn("hand remaining pinned work to a subagent", output["systemMessage"])

    def test_claude_session_below_threshold_stops_silently(self):
        self.write(claude_transcript(199_000))
        self.assertEqual(self.stop(), "")

    def test_claude_session_above_threshold_asks_for_closing_advice(self):
        # The size is the last request's input plus both cache counts, never a subagent's total.
        self.write(claude_transcript(210_000))
        self.assertHint(self.stop(), 210)

    def test_codex_session_below_threshold_stops_silently(self):
        self.write(codex_rollout(199_000))
        self.assertEqual(self.stop(turn_id="t1"), "")

    def test_codex_session_above_threshold_asks_for_closing_advice(self):
        self.write(codex_rollout(210_000))
        self.assertHint(self.stop(turn_id="t1"), 210)

    def test_threshold_override_moves_the_trigger(self):
        self.write(claude_transcript(120_000))
        self.assertEqual(self.stop(), "")
        self.assertHint(self.stop(env={"CONTEXT_HINT_THRESHOLD": "100000"}), 120)

    def test_fires_once_per_step_past_the_threshold(self):
        # Every turn's closing advice would be noise; one hint per 50k step is the cadence.
        self.write(claude_transcript(210_000))
        self.assertHint(self.stop(), 210)
        self.write(claude_transcript(240_000))
        self.assertEqual(self.stop(), "")
        self.write(claude_transcript(255_000))
        self.assertHint(self.stop(), 255)

    def test_sessions_keep_separate_steps(self):
        self.write(claude_transcript(210_000))
        self.assertHint(self.stop(), 210)
        self.assertHint(self.stop(session_id="s2"), 210)

    def test_continuation_from_a_stop_hook_is_let_through(self):
        # stop_hook_active is the loop guard on both hosts: blocking again could never end the turn.
        self.write(claude_transcript(210_000))
        self.assertEqual(self.stop(stop_hook_active=True), "")

    def test_single_prompt_interactive_session_gets_a_hint(self):
        # One long desktop session of subagent work has one typed prompt and still needs the hint.
        self.write(claude_transcript(400_000, prompts=1))
        self.assertHint(self.stop(), 400)
        self.write(claude_transcript(400_000, prompts=1, entrypoint="cli"))
        self.assertHint(self.stop(session_id="s2"), 400)
        self.write(codex_rollout(250_000, prompts=1))
        self.assertHint(self.stop(session_id="s3"), 250)

    def test_unattended_runs_get_no_hint(self):
        # Nobody reads a headless run's output; `sdk-*` is the Agent SDK and `claude -p`.
        for entrypoint in ("sdk-cli", "sdk-ts", "mcp"):
            self.write(claude_transcript(400_000, entrypoint=entrypoint))
            self.assertEqual(self.stop(), "", entrypoint)
        for source in ("exec", "mcp", {"subagent": {"thread_spawn": {"depth": 1}}}):
            self.write(codex_rollout(250_000, source=source))
            self.assertEqual(self.stop(), "", source)

    def test_session_of_unknown_origin_stays_silent(self):
        self.write(claude_transcript(400_000, entrypoint=None))
        self.assertEqual(self.stop(), "")

    def test_in_flight_background_tasks_defer_the_hint(self):
        # The turn only ends to wait for them; the hint comes on the stop after they report.
        # The step is not consumed meanwhile.
        self.write(claude_transcript(300_000))
        task = {"id": "t1", "type": "subagent", "status": "running", "description": "review"}
        self.assertEqual(self.stop(background_tasks=[task]), "")
        self.assertHint(self.stop(background_tasks=[]), 300)

    def test_unreadable_transcript_stops_silently(self):
        self.assertEqual(self.stop(transcript_path=str(self.tmp / "missing.jsonl")), "")
        self.assertEqual(self.stop(transcript_path=None), "")
        self.transcript.write_text('not json\n{"type": "assistant", "message": {"usage": "x"}}\n{"trunc',
                                   encoding="utf-8")
        self.assertEqual(self.stop(), "")

    def test_malformed_input_stops_silently(self):
        proc = subprocess.run([sys.executable, str(SCRIPT)], input="{", capture_output=True, text=True,
                              env=self.env)
        self.assertEqual((proc.returncode, proc.stdout, proc.stderr), (0, "", ""))


if __name__ == "__main__":
    unittest.main()
