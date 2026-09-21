#!/usr/bin/env python3
"""Option-coverage reconciliation for the architecture case, run with cwd = the workspace.

Case data, not harness: the request names three options to weigh, and a report that
carries only two has not run the trade-off whatever else it says. Whether the frozen
weights are applied with evidence, and whether the rejected options keep their
material strengths, stays the rubric's call - a judge reads that, a regex cannot.

The options are read by meaning, never by wording. `fixed pause` and `constant sleep`
are one option, `capped growing backoff` and `exponential doubling` another, and a
literal needle for either fails a correct report that chose the other word - which
spends a live run to learn nothing.

Python 3 standard library only, 3.9-compatible."""

import re
import sys
from pathlib import Path

REPORT = Path("docs") / "architecture-report.md"

# One option each, matched in every faithful wording: what tells the three apart is
# the pause that never grows, the pause that does, and the handshake that waits on
# the holder instead of pausing. The words for each are the author's to choose.
OPTIONS = (
    ("the shipped fixed pause",
     re.compile(r"fixed|constant|flat|static|unchanged|shipped|current|existing"
                r"|status[- ]quo|do[- ]nothing", re.I)),
    ("the capped growing backoff",
     re.compile(r"back[- ]?off|exponential|doubl|growing|escalating|increasing", re.I)),
    ("the lock-file handshake",
     re.compile(r"lock|handshake", re.I)),
)


def main():
    if not REPORT.is_file():
        problems = ["no %s in the workspace" % REPORT]
    else:
        text = REPORT.read_text(encoding="utf-8", errors="replace")
        problems = ["%s: does not weigh %s" % (REPORT, option)
                    for option, pattern in OPTIONS if not pattern.search(text)]
    for problem in problems:
        sys.stderr.write(problem + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
