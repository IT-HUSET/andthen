#!/usr/bin/env python3
"""State reconciliation for the spec case, run with cwd = the workspace.

Case data, not harness: this file holds what only this case knows, which is what
keeps the runner generic - the FIS size ceiling, the one-story plan's status, and
the review-evidence shape. Whether the FIS kept the request's decisions is the
judge's call, not a phrase match: a correct FIS words a clause its own way.

The evidence records that a fresh-context review ran and whether it remediated;
it carries no grade, because the run has none - Preflight ends on the next
command, not a verdict. What the contract binds is the end state this file
checks directly: the plan exists, validates, and carries the story pending with its FIS;
the FIS is under the ceiling and carries no retired section or verdict line.

Python 3 standard library only.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import story_state  # noqa: E402

MAX_FIS_WORDS = 1400

# Pinned, not searched: the project already carries a plan of its own, and the
# first plan.json a walk finds would be that one.
SPEC_DIR = Path("docs") / "specs" / "label-slug"
FIS_PATH = SPEC_DIR / "s01-slugify-label.md"
PLAN = SPEC_DIR / "plan.json"


def find(pattern):
    hits = [p for p in sorted(Path(".").rglob(pattern))
            if ".dartclaw" not in p.parts and ".git" not in p.parts]
    return hits[0] if hits else None


def main():
    problems = []

    fis = FIS_PATH if FIS_PATH.is_file() else None
    if fis is None:
        problems.append("no %s in the workspace" % FIS_PATH)
    else:
        text = fis.read_text(encoding="utf-8")
        words = len(text.split())
        if words > MAX_FIS_WORDS:
            problems.append("%s is %d words, over the %d ceiling"
                            % (fis, words, MAX_FIS_WORDS))
        problems.extend(story_state.retired(fis))

    problems.extend(plan_problems(fis))

    problems.extend(evidence_problems(find("review-evidence.json")))

    for problem in problems:
        sys.stderr.write(problem + "\n")
    return 1 if problems else 0


def plan_problems(fis):
    """A standalone FIS is a one-story plan written beside it (ADR-003): the
    story is pending and points at the FIS by canonical basename - the state
    the executor reads."""
    rows, problems = story_state.stories(PLAN)
    if problems:
        return problems
    if len(rows) != 1:
        return ["%s: %d stories, expected exactly one" % (PLAN, len(rows))]
    wanted = {"id": "S01", "status": "pending", "completedTaskIds": []}
    if fis is not None:
        wanted["fis"] = fis.name
    return story_state.diverges(PLAN, rows[0], **wanted)


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return exc


def evidence_problems(path):
    if path is None:
        return ["no review-evidence.json in the workspace"]
    data = load(path)
    if not isinstance(data, dict):
        return ["%s: not a JSON object (%s)" % (path, data)]
    problems = []
    if data.get("freshContext") is not True:
        problems.append("%s: freshContext is %r, expected True"
                        % (path, data.get("freshContext")))
    if not isinstance(data.get("remediated"), bool):
        problems.append("%s: remediated is not a boolean" % path)
    return problems


if __name__ == "__main__":
    sys.exit(main())
