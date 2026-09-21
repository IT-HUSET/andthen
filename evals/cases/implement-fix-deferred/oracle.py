#!/usr/bin/env python3
"""Deferral reconciliation for the implement-fix blocked-finding case, run with
cwd = the workspace. A Fix-routed finding whose repair encodes an open project
decision leaves three marks and no fourth: `src/reporter/retry.py` as it was
found, one new entry in the backlog the Project Document Index names, and the
input report recording the finding DEFERRED. Exactly one entry rather than at
least one - a pass that files the same deferral twice, or files its passing
observations beside it, leaves a backlog nobody can read as the deferral list
it is.

Case data, not harness. Python 3 standard library only, 3.9-compatible."""

import re
import subprocess
import sys
from pathlib import Path

RETRY = "src/reporter/retry.py"
BACKLOG = Path("docs/TECH-DEBT-BACKLOG.md")
REPORT = Path("retry-code-review-claude-2026-09-12.md")
STATUS_HEADING = re.compile(r"^## Remediation Status[ \t]*$", re.M)
# The report carries one finding, so any other status in the section is about
# that finding and contradicts the deferral.
NOT_DEFERRED = re.compile(r"\b(RESOLVED|UNRESOLVED|SURFACED)\b")


def git(*args):
    done = subprocess.run(["git", *args], text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    return done.stdout if done.returncode == 0 else None


def read(path):
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def entries(text):
    """One string per bullet, wrapped continuation lines folded in, so a check on
    an entry's wording holds however the writer broke the line."""
    found, current = [], None
    for line in text.splitlines():
        if line.startswith("- "):
            if current is not None:
                found.append(" ".join(current))
            current = [line[2:].strip()]
        elif current is not None:
            if line.strip() and line[:1].isspace():
                current.append(line.strip())
            else:
                found.append(" ".join(current))
                current = None
    if current is not None:
        found.append(" ".join(current))
    return found


def check():
    roots = (git("rev-list", "--max-parents=0", "HEAD") or "").split()
    if len(roots) != 1:
        return ["the workspace has %d root commit(s), so there is no starting state"
                " to compare the module against" % len(roots)]
    problems = []
    if (git("diff", "--name-only", roots[0], "--", RETRY) or "").strip():
        problems.append("%s: changed, and a finding deferred on an open decision is"
                        " not repaired in the same pass" % RETRY)

    before = entries(git("show", "%s:%s" % (roots[0], BACKLOG.as_posix())) or "")
    new = [entry for entry in entries(read(BACKLOG)) if entry not in before]
    if len(new) != 1:
        problems.append("%s: %d new entries, expected exactly 1 for the deferred"
                        " finding" % (BACKLOG, len(new)))
    else:
        lowered = new[0].lower()
        if "retry" not in lowered:
            problems.append("%s: the entry does not name what was deferred: %r"
                            % (BACKLOG, new[0]))
        if "decision" not in lowered or not ("backoff" in lowered or "decisions.md" in lowered):
            problems.append("%s: the entry does not name the open decision that blocks"
                            " the repair: %r" % (BACKLOG, new[0]))

    sections = STATUS_HEADING.split(read(REPORT))
    if len(sections) != 2:
        problems.append("%s: %d '## Remediation Status' section(s), expected exactly 1"
                        % (REPORT, len(sections) - 1))
    elif "DEFERRED" not in sections[1] or NOT_DEFERRED.search(sections[1]):
        problems.append("%s: Remediation Status does not record the finding DEFERRED:"
                        " %r" % (REPORT, sections[1].strip()[:160]))
    return problems


def main():
    problems = check()
    for problem in problems:
        sys.stderr.write(problem + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
