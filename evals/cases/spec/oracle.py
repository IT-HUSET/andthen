#!/usr/bin/env python3
"""State reconciliation for the spec case, run with cwd = the workspace.

Case data, not harness: this file holds what only this case knows, which is what
keeps the runner generic - the FIS size ceiling, the one-story plan's status, and
the review-evidence shape. Whether the FIS kept the request's decisions is the
judge's call, not a phrase match: a correct FIS words a clause its own way.

A remediated verdict passes at any grade. The skill's Self-Review is one
rubric-loading reviewer pass at Step 7 that never re-reviews, and Step 9 writes
the one-story plan only afterwards - so the recorded verdict is a snapshot of a
FIS the run had not finished, and a reviewer that grades the missing plan.json
gating is reading the contract correctly at that moment. What the contract does
bind is the end state this file checks directly: the plan exists, validates, and
carries the story; the FIS is under the ceiling. Unremediated, the grade is the
end state and only a clean one passes.

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

    problems.extend(plan_problems(fis))

    evidence = find("review-evidence.json")
    remediated = None
    if evidence is not None:
        data = load(evidence)
        if isinstance(data, dict):
            remediated = data.get("remediated")
            if not isinstance(remediated, bool):
                problems.append("%s: remediated is not a boolean" % evidence)
            if not (isinstance(data.get("verdict"), str) and data["verdict"].strip()):
                problems.append("%s: verdict is not a recorded grade" % evidence)
    fields = {"freshContext": True}
    if remediated is not True:
        fields["verdict"] = ("READY", "PASS")
    problems.extend(expect_json(evidence, "review-evidence.json", fields))

    for problem in problems:
        sys.stderr.write(problem + "\n")
    return 1 if problems else 0


def plan_problems(fis):
    """A standalone FIS is a one-story plan written beside it (ADR-013): the
    story carries the closure verdict as its status and points at the FIS by
    canonical basename, so a spec that closes READY in prose while its story
    stays blocked would never execute."""
    rows, problems = story_state.stories(PLAN)
    if problems:
        return problems
    if len(rows) != 1:
        return ["%s: %d stories, expected exactly one" % (PLAN, len(rows))]
    wanted = {"id": "S01", "status": "spec-ready", "completedTaskIds": []}
    if fis is not None:
        wanted["fis"] = fis.name
    return story_state.diverges(PLAN, rows[0], **wanted)


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return exc


def expect_json(path, name, fields):
    if path is None:
        return ["no %s in the workspace" % name]
    data = load(path)
    if not isinstance(data, dict):
        return ["%s: not a JSON object (%s)" % (path, data)]
    # A tuple of wanted values accepts any of them, case-insensitively: the
    # recorded grade is the FIS closure word `READY`, or gap mode's `PASS` when
    # a run records a review verdict instead.
    def accepted(value, want):
        wanted = want if isinstance(want, tuple) else (want,)
        return value in wanted or (isinstance(value, str)
                                   and value.lower() in [w.lower() for w in wanted
                                                         if isinstance(w, str)])
    return ["%s: %s is %r, expected %r" % (path, key, data.get(key), want)
            for key, want in sorted(fields.items())
            if not accepted(data.get(key), want)]


if __name__ == "__main__":
    sys.exit(main())
