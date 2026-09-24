#!/usr/bin/env python3
"""End-state reconciliation for the spec re-entry case, run with cwd = the workspace.

Case data, not harness. The starting state is one an `--auto` run leaves: the
FIS was authored with the backoff as an `ASSUMPTION:` where it bites, and an
older release left its story the legacy `blocked`, which reads as `spec-ready`.
Re-entry is two halves of one end state and neither alone is it: the FIS carries
the settled policy with the backoff assumption gone, and the story record beside
it is `spec-ready` with no completed task - the state the next skill reads.

The prose is read by meaning, never by wording. `200 ms` and `0.2 s` are one base,
`doubling` and `exponential` one growth, and a literal needle for either fails a
correct FIS that chose the other word - which spends a live run to learn nothing.
Whether the policy is integrated *once*, into the prose that owns it, stays the
rubric's call: a judge reads that, a regex cannot.

Python 3 standard library only, 3.9-compatible."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import story_state  # noqa: E402

SPEC_DIR = Path("docs") / "specs" / "retry-policy"
FIS_NAME = "s01-retry-policy.md"
FIS = SPEC_DIR / FIS_NAME
PLAN = SPEC_DIR / "plan.json"

# The open decision the re-entry closes: the backoff assumption the FIS was
# authored with. The decision settles the pause, so any assumption still made
# about it is the open item surviving, whatever it assumes. A shipped FIS never
# carries the open-decision marker either.
BACKOFF_ASSUMPTION = re.compile(r"ASSUMPTION:.*\b(?i:pause|backoff)")

# One term of the settled policy each, matched in every faithful wording: the unit,
# the word for the growth and the spelling of the count are the author's to choose,
# the values are not. The count is read next to the word it counts so that a stray
# 3 elsewhere in the FIS cannot answer for it.
SETTLED = (
    ("the 200 ms base",
     re.compile(r"\b(?:200\s*(?:ms|millisecond)|0\.2(?:\s*(?:s\b|sec|second))?)", re.I)),
    # The operator forms carry their exponent, because a bare `2**` is what every
    # markdown bold ending in 2 looks like - `**SC02**` matched the first draft.
    ("the doubling growth",
     re.compile(r"doubl|exponential|[x×]\s*2\b"
                r"|2\s*(?:\*\*|\^)\s*(?:attempt|\d|[nik]\b)", re.I)),
    ("the 3-retry maximum",
     re.compile(r"\b(?:3|three|third)\b[^.\n]{0,30}\b(?:retr|attempt)"
                r"|\b(?:retr|attempt)\w*[^.\n]{0,30}\b(?:3|three|third)\b", re.I)),
)


def fis_problems():
    if not FIS.is_file():
        return ["no %s in the workspace" % FIS]
    text = FIS.read_text(encoding="utf-8")
    problems = ["%s: does not state %s" % (FIS, term)
                for term, pattern in SETTLED if not pattern.search(text)]
    if BACKOFF_ASSUMPTION.search(text):
        problems.append("%s: still carries an ASSUMPTION about the backoff, so "
                        "the decision is not integrated" % FIS)
    return problems + story_state.retired(FIS)


def main():
    problems = fis_problems()
    row, unread = story_state.story(PLAN, "S01")
    problems.extend(unread if row is None else
                    story_state.diverges(PLAN, row, status="spec-ready",
                                         completedTaskIds=[], fis=FIS_NAME))
    for problem in problems:
        sys.stderr.write(problem + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
