#!/usr/bin/env python3
"""Reply-survival reconciliation for the clarify case, run with cwd = the workspace.

Case data, not harness: the scripted interview settles a rejected alternative and a
boundary and leaves one question open, and a PRD carrying none of the three has lost
the interview whatever shape it has. Whether each reply is preserved without
invention, and whether the document reads as a PRD, stays the rubric's call - a judge
reads that, a regex cannot.

The replies are read by meaning, never by wording. `a second file` and `a separate
totals file` are one rejected alternative, `per-period breakdown` and `totals broken
down by month` one boundary, and a literal needle for either fails a correct PRD that
chose the other word - which spends a live run to learn nothing.

Python 3 standard library only, 3.9-compatible."""

import re
import sys
from pathlib import Path

PRD = Path("docs") / "specs" / "report-totals" / "prd.md"

# One scripted reply each. The alternative is read as its noun next to the word that
# separates it, so that a stray `second` elsewhere in the PRD cannot answer for it.
REPLIES = (
    ("the rejected second-file alternative",
     re.compile(r"\b(?:second|separate|standalone|distinct|another|own|dedicated"
                r"|sidecar|extra|additional)\b[^.\n]{0,30}"
                r"\b(?:file|report|document|output|artifact)", re.I)),
    ("the per-period breakdown held out of scope",
     re.compile(r"breakdown|broken down|per[- ]?period|periodic"
                r"|by (?:period|month|week|day)", re.I)),
    ("the default-production question left open",
     re.compile(r"default|opt[- ]?in|opt[- ]?out|automatic"
                r"|always (?:produced|emitted|written|included)|behind a flag"
                r"|every run|each run|only when|on request"
                r"|when (?:asked|requested)|unless asked", re.I)),
)


def main():
    if not PRD.is_file():
        problems = ["no %s in the workspace" % PRD]
    else:
        text = PRD.read_text(encoding="utf-8", errors="replace")
        problems = ["%s: does not record %s" % (PRD, reply)
                    for reply, pattern in REPLIES if not pattern.search(text)]
    for problem in problems:
        sys.stderr.write(problem + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
