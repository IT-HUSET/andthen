#!/usr/bin/env python3
"""State reconciliation for the exec-plan case, run with cwd = the workspace.

Case data, not harness. The failure this case exists to catch is a run that
implements the story, narrates its verification, and reports the plan complete:
the claim spans the story row, the task IDs it recorded, and the `verified`
record the story subagent wrote from the proof lines it executed,
which no single check.json key sees. One story, because DartClaw caps a workflow
step at thirty minutes; the two-story overlay serves the implement-fix case.

Python 3 standard library only, 3.9-compatible.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import story_state  # noqa: E402

PLAN = Path("docs/specs/row-count/plan.json")


def main():
    row, problems = story_state.story(PLAN, "S01")
    if row is not None:
        problems = story_state.diverges(PLAN, row, verified=True, status="done",
                                        completedTaskIds=["TI01"])
    for problem in problems:
        sys.stderr.write(problem + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
