#!/usr/bin/env python3
"""Tests for hooks/scripts/notify.sh and hooks/scripts/notify-elevenlabs.sh.

    python3 -m unittest tests.test_notify

Drives the real scripts with Claude Code's documented hook input. Shims on PATH
record what would have been announced without putting anything on screen or on the
speakers: `uname` reports Linux and `notify-send` logs its arguments for the desktop
script; `claude` logs the prompt it is asked to phrase and `curl` logs the request for
the voice script, which does that work in a detached background process.
"""

import json
import os
import pathlib
import shutil
import stat
import subprocess
import tempfile
import time
import unittest

REPO = pathlib.Path(__file__).resolve().parents[1]
BASH = shutil.which("bash")


@unittest.skipIf(os.name == "nt" or not BASH, "POSIX shell hook")
class DesktopNotifyTest(unittest.TestCase):
    SCRIPT = REPO / "hooks/scripts/notify.sh"
    TURN_FILE = "claude-notify-turn-s1"
    SHIMS = {"uname": "echo Linux", "notify-send": 'echo "$@" >> "$SHIM_LOG"'}
    PERMISSION_TEXT = "Permission Required"
    STOP_TEXT = "Task Complete"
    EXTRA_ENV = {}

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        shims = self.tmp / "bin"
        shims.mkdir()
        self.log = self.tmp / "shown.log"
        for name, body in self.SHIMS.items():
            shim = shims / name
            shim.write_text(f"#!/bin/sh\n{body}\n")
            shim.chmod(shim.stat().st_mode | stat.S_IXUSR)
        self.env = {**os.environ, **self.EXTRA_ENV, "SHIM_LOG": str(self.log),
                    "PATH": f"{shims}{os.pathsep}{os.environ['PATH']}", "TMPDIR": str(self.tmp)}

    def fire(self, event, env=None, **fields):
        payload = json.dumps({"session_id": "s1", "hook_event_name": event, **fields})
        proc = subprocess.run([BASH, str(self.SCRIPT)], input=payload, env={**self.env, **(env or {})},
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, "a notification hook must never block Claude")

    def shown(self, expect=None):
        # The voice script announces from a background process; wait for it when a text is expected.
        deadline = time.monotonic() + (5 if expect else 0)
        while True:
            text = self.log.read_text() if self.log.exists() else ""
            if not expect or expect in text or time.monotonic() > deadline:
                return text
            time.sleep(0.05)

    def age_turn(self, seconds):
        turn = self.tmp / self.TURN_FILE
        turn.write_text(str(int(turn.read_text()) - seconds))

    def test_permission_prompt_says_approval_is_needed(self):
        # Claude Code sends the type as `notification_type`; reading anything else
        # collapses every notification into the generic message.
        self.fire("Notification", message="Claude needs permission", notification_type="permission_prompt")
        self.assertIn(self.PERMISSION_TEXT, self.shown(self.PERMISSION_TEXT))

    def test_quick_reply_is_not_announced(self):
        # The user is still watching a reply that took under 30 s.
        self.fire("UserPromptSubmit", prompt="hi")
        self.fire("Stop")
        self.assertEqual(self.shown(), "")

    def test_long_turn_is_announced_even_as_the_first_of_the_session(self):
        self.fire("UserPromptSubmit", prompt="refactor this")
        self.age_turn(60)
        self.fire("Stop")
        self.assertIn(self.STOP_TEXT, self.shown(self.STOP_TEXT))

    def test_stop_without_a_recorded_turn_is_announced(self):
        # Setups without the UserPromptSubmit entry still get notified.
        self.fire("Stop")
        self.assertIn(self.STOP_TEXT, self.shown(self.STOP_TEXT))


class VoiceNotifyTest(DesktopNotifyTest):
    SCRIPT = REPO / "hooks/scripts/notify-elevenlabs.sh"
    TURN_FILE = "claude-tts-notify-turn-s1"
    SHIMS = {"claude": 'echo "claude $@" >> "$SHIM_LOG"; echo "Done"',
             "curl": 'echo "curl $@" >> "$SHIM_LOG"; echo 500'}
    PERMISSION_TEXT = "approve something"
    STOP_TEXT = "finished its task"
    EXTRA_ENV = {"ELEVENLABS_API_KEY": "test-key"}

    def test_nested_claude_call_does_not_announce_itself(self):
        # The script's own `claude -p` runs the user's hooks too; left unguarded it
        # would record turns and speak for its own phrasing call.
        nested = {"CLAUDE_TTS_NOTIFY_NESTED": "1"}
        self.fire("UserPromptSubmit", env=nested, prompt="phrase this")
        self.fire("Stop", env=nested)
        self.assertFalse((self.tmp / self.TURN_FILE).exists())
        time.sleep(0.5)
        self.assertEqual(self.shown(), "")


if __name__ == "__main__":
    unittest.main()
