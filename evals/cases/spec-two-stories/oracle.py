#!/usr/bin/env python3
"""State reconciliation for the spec-two-stories case, run with cwd = the workspace.

Case data, not harness: `check.json`'s `validate_plan.py` call proves the
manifest against its schema, but not that `plan` took its several-story branch.
The PRD holds two independent requirements in two leaf modules, so a bundle of
one story is the sizing miss this case exists to catch (ADR-020 R3), and every
story must stay pending with a FIS that resolves beside the plan and names
the story it was written for.

Python 3 standard library only, 3.9-compatible.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import story_state  # noqa: E402

PLAN = Path("docs/specs/ledger-hygiene/plan.json")
MIN_STORIES = 2

PROVENANCE = re.compile(r"^\*\*(Plan|Story-ID)\*\*:[ \t]*(\S.*?)[ \t]*$", re.M)


def fis_problems(row):
    """A FIS naming another story would complete the wrong row when executed."""
    identifier, pointer = row.get("id"), row.get("fis")
    if not isinstance(pointer, str) or not pointer:
        return ["%s: story %s has no fis pointer" % (PLAN, identifier)]
    fis = PLAN.parent / pointer
    if not fis.is_file():
        return ["%s: story %s names %s, which does not resolve beside the plan"
                % (PLAN, identifier, pointer)]
    found = dict((m.group(1), m.group(2))
                 for m in PROVENANCE.finditer(fis.read_text(encoding="utf-8")))
    problems = []
    if found.get("Story-ID") != identifier:
        problems.append("%s: Story-ID is %r, expected %r"
                        % (fis, found.get("Story-ID"), identifier))
    if Path(found.get("Plan", "")).name != PLAN.name:
        problems.append("%s: Plan is %r, expected the plan beside it"
                        % (fis, found.get("Plan")))
    return problems + story_state.retired(fis)


def main():
    rows, problems = story_state.stories(PLAN)
    if rows and len(rows) < MIN_STORIES:
        problems.append("%s: %d story, expected at least %d - two independent "
                        "requirements in two leaf modules" % (PLAN, len(rows), MIN_STORIES))
    for row in rows:
        problems.extend(story_state.diverges(PLAN, row, status="pending"))
        problems.extend(fis_problems(row))
    for problem in problems:
        sys.stderr.write(problem + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
