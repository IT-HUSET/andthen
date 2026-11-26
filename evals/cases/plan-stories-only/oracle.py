#!/usr/bin/env python3
"""State reconciliation for the plan-stories-only case, run with cwd = the workspace.

Case data, not harness: `check.json` proves the manifest against its schema and
that no FIS file landed beside it, but the schema admits a `fis` pointer and any
status, so neither proves the run stopped at the cut. Every story must be
`pending` with `fis` null - a pointer is a FIS the run claims it wrote - and the
PRD's two independent requirements in two leaf modules must still be two
stories, since a one-story cut takes the branch `--stories-only` ignores.

Python 3 standard library only, 3.9-compatible.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import story_state  # noqa: E402

PLAN = Path("docs/specs/ledger-hygiene/plan.json")
MIN_STORIES = 2


def main():
    rows, problems = story_state.stories(PLAN)
    if rows and len(rows) < MIN_STORIES:
        problems.append("%s: %d story, expected at least %d - two independent "
                        "requirements in two leaf modules" % (PLAN, len(rows), MIN_STORIES))
    for row in rows:
        problems.extend(story_state.diverges(PLAN, row, status="pending", fis=None))
    for problem in problems:
        sys.stderr.write(problem + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
