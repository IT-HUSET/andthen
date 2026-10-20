#!/usr/bin/env python3
"""State reconciliation for the exec-plan-triage case, run with cwd = the workspace.

Case data, not harness. A story run on S01's FIS finished a story whose recorded
discovery contradicts a scenario of S02, the unstarted story that depends on it.
The claim spans git and files no single check.json key sees: S01's row is `done`
on a `verified` record, the commit carrying `Story-ID: S01` also carries the
append to S02's FIS, that append is a `## Discovered Requirements` bullet traced
from S01, S02's spec text above its tail sections is as the plan left it, and
S02's row has not moved.

Python 3 standard library only, 3.9-compatible.
"""

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import story_state  # noqa: E402

PLAN = Path("docs/specs/count-summary/plan.json")
S02_FIS = Path("docs/specs/count-summary/s02-write-run-summary.md")
STARTING_S02 = Path(__file__).resolve().parent / "overlay" / S02_FIS

# The two FIS tail sections, in the order fis-mutability.md fixes; everything above
# the first one is spec text a story run may not edit.
TAIL = re.compile(r"^## (?:Discovered Requirements|Implementation Observations)[ \t]*$", re.M)
DISCOVERED = re.compile(r"^## Discovered Requirements[ \t]*$", re.M)
STORY_ID_S01 = re.compile(r"^Story-ID: S01[ \t]*$", re.M)
TRACED_FROM_S01 = re.compile(r"Traced from[^\n]*\bS01\b")


def git(*args):
    done = subprocess.run(("git",) + args, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, universal_newlines=True)
    return done.stdout if done.returncode == 0 else ""


def story_commits():
    """Hashes of the commits whose message carries `Story-ID: S01`."""
    return [sha for sha in git("rev-list", "HEAD").split()
            if STORY_ID_S01.search(git("show", "-s", "--format=%B", sha))]


def head(text):
    """The spec text above the first tail section."""
    found = TAIL.search(text)
    return (text[:found.start()] if found else text).rstrip()


def discovered_bullets(text):
    """The bullets of the `## Discovered Requirements` section, one string each."""
    found = DISCOVERED.search(text)
    if not found:
        return []
    section = re.split(r"^## ", text[found.end():], maxsplit=1, flags=re.M)[0]
    return [b for b in re.split(r"^(?=- )", section, flags=re.M) if b.startswith("- ")]


def main():
    problems = []
    row, found = story_state.story(PLAN, "S01")
    problems.extend(found if row is None else story_state.diverges(
        PLAN, row, verified=True, status="done", completedTaskIds=["TI01"]))
    row, found = story_state.story(PLAN, "S02")
    problems.extend(found if row is None else story_state.diverges(
        PLAN, row, status="pending", completedTaskIds=[]))

    commits = story_commits()
    if not commits:
        problems.append("no commit carries 'Story-ID: S01'")
    elif not any(str(S02_FIS) in git("diff-tree", "--no-commit-id", "--name-only",
                                     "-r", sha).splitlines() for sha in commits):
        problems.append("no commit carrying 'Story-ID: S01' modifies %s" % S02_FIS)

    if not S02_FIS.is_file():
        problems.append("%s is gone" % S02_FIS)
    else:
        text = S02_FIS.read_text(encoding="utf-8")
        if head(text) != head(STARTING_S02.read_text(encoding="utf-8")):
            problems.append("%s: text above its tail sections differs from the plan's" % S02_FIS)
        if not any(TRACED_FROM_S01.search(b) for b in discovered_bullets(text)):
            problems.append("%s: no '## Discovered Requirements' bullet is traced from S01"
                            % S02_FIS)

    for problem in problems:
        sys.stderr.write(problem + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
