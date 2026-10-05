#!/usr/bin/env python3
"""State reconciliation for the plan case, run with cwd = the workspace.

Case data, not harness: `check.json`'s `validate_plan.py` call proves the
manifest against its schema, but nothing a check.json key sees proves the
bundle is *executable* - that every story is pending with a FIS, that its FIS
pointer resolves on the filesystem, and that each FIS names the story it was
written for and carries no retired section or verdict line. Provenance is a
claim across two files, which is what `oracle` is for.

The PRD holds two capabilities that ship independently in different modules,
so a bundle of one story means `plan` skipped the several-story breakdown this
attended case exists to exercise.

Whether each FIS carries runnable proof is the rubric's call (`plan-execution`):
no script parses a FIS (Decisions: "The `ops` skill and its script are
retired"), and a grammar violation is a finding, not a parse error.

Python 3 standard library only, 3.9-compatible.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import story_state  # noqa: E402

PLAN = Path("docs/specs/amount-filter/plan.json")
MIN_STORIES = 2

PROVENANCE = re.compile(r"^\*\*(Plan|Story-ID)\*\*:[ \t]*(\S.*?)[ \t]*$", re.M)


def fis_problems(row):
    """The header pair is what an implementer dispatched with only the FIS path
    reads to find its plan and row; a FIS that names another story would complete
    the wrong one. Every FIS this run wrote also carries no retired section or
    verdict line."""
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
                        "capabilities in different modules" % (PLAN, len(rows), MIN_STORIES))
    for row in rows:
        problems.extend(story_state.diverges(PLAN, row, status="pending"))
        problems.extend(fis_problems(row))
    for problem in problems:
        sys.stderr.write(problem + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
