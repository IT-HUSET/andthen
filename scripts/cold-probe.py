#!/usr/bin/env python3
"""Ask the cheapest Claude model a prompt with no CLAUDE.md, git status, plugin, skill, or tool loaded,
so a probe of rule wording sees only the prompt (the `skill-review` leading-word probe).

Usage: python3 scripts/cold-probe.py <prompt-file>
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FLAGS = ["-p", "--safe-mode", "--tools", "", "--model", "haiku", "--no-session-persistence"]


def main(argv):
    if len(argv) != 2:
        sys.exit("usage: cold-probe.py <prompt-file>")
    claude = shutil.which("claude")  # resolves claude.cmd on Windows too
    if claude is None:
        sys.exit("cold-probe: the claude CLI is not on PATH")
    prompt = Path(argv[1]).read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as cwd:
        return subprocess.run([claude, *FLAGS], input=prompt, text=True, cwd=cwd).returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv))
