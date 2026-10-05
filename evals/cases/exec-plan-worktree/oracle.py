#!/usr/bin/env python3
"""State reconciliation for the exec-plan-worktree case, run with cwd = the workspace.

Case data, not harness. Two independent stories ran in parallel worktrees and
were merged back; the checks read the merged tree and the git shape (one
worktree left, no story branches, a merge commit, both trailers), and this
oracle reads what no check.json key sees: each story row, the task id it
recorded, and the `verified` record each story wrote and committed in its own
worktree from the proof lines it executed, which reached the main checkout with
the merge.

Python 3 standard library only, 3.9-compatible.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import story_state  # noqa: E402

PLAN = Path("docs/specs/run-summary/plan.json")


def main():
    problems = []
    for story_id in ("S01", "S02"):
        row, found = story_state.story(PLAN, story_id)
        if row is None:
            problems.extend(found)
            continue
        problems.extend(story_state.diverges(PLAN, row, verified=True, status="done",
                                             completedTaskIds=["TI01"]))
    for problem in problems:
        sys.stderr.write(problem + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
