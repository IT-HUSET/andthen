#!/usr/bin/env python3
"""Tracker reconciliation for the tracker-publish case, run with cwd = the workspace.

Case data, not harness. The failure this case exists to catch is a re-run that
duplicates: a publish that stopped after creating a story's issue leaves it
unlinked from the parent, and the next run must find it again by its hidden line
rather than create a second one. The claim spans the tracker's issue list, each
body's hidden line, and the store's activity log, which no single check.json key
sees. Two runs of the same publish then settle on the same three issues, the
second creating nothing.

The Operation Table maps `fetch links` and `add blocked-by` but not `set parent`,
so one case shows an optional operation used where mapped and skipped, without a
stop, where not: S02 depends on S01, so #3 ends blocked by #2 and nothing else is
blocked, and the second run, reading the link first, writes none. The stub logs
every `block` call, a duplicate included, which is how a re-written link shows;
its docstring leaves that out, because the subject reads it.

The tracker is the stub's JSON store, so the checks read it directly.

Python 3 standard library only, 3.9-compatible.
"""

import json
import re
import sys
from pathlib import Path

STORE = Path("tools/issues.json")
SOURCE = "docs/specs/ledger-hygiene/prd.md"
PARENT_TITLE = "Ledger hygiene for month close"
REQUEST = "At month close the ledger owner's notes stop the run"
STORIES = {"S01": 2, "S02": 3}  # story id -> issue number: #2 is seeded, #3 is new
SEEDED = STORIES["S01"]  # #2, the seeded child
SEEDED_TITLE = "S01 - Comment lines in the ledger"  # #2's title, which a found issue keeps
PLAN_ID = "ledger-hygiene"  # the plan directory's name, leading a created child's title
# What each story's body must carry, so a body that kept its hidden line and lost
# its projection does not pass.
STORY_WORDS = {"S01": "comment", "S02": "24 characters"}
BLOCKED_BY = {1: [], 2: [], 3: [2]}  # issue -> its blockers: S02 depends on S01

LINE = re.compile(r"<!--[ \t]*andthen-projection[ \t]+([^>]*?)[ \t]*-->")
# A path the Durability rule bars from a body: a project directory, or a file
# with a document, code, or data extension.
PATH = re.compile(r"\b(?:docs|src|tests|tools|plugin|evals)/[\w./-]+"
                  r"|[\w./-]+\.(?:md|py|json|ya?ml|txt|csv|toml|sh)\b")
PROOF = re.compile(r"^[ \t]*(?:[-*][ \t]+)?\**Proof\**[ \t]*:", re.M | re.I)


def below(body):
    """The text under the first hidden line, or None when there is none."""
    found = LINE.search(body)
    return body[found.end():] if found else None


def main():
    try:
        store = json.loads(STORE.read_text(encoding="utf-8"))
        issues = dict((i["number"], i) for i in store["issues"])
        log = store["log"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        sys.stderr.write("%s: unreadable (%s)\n" % (STORE, exc))
        return 1
    problems = []

    # Total issues equal stories + 1, the numbers the seed and the creates make.
    wanted = [1] + sorted(STORIES.values())
    if sorted(issues) != wanted:
        problems.append("issues are %s, expected %s: a re-run duplicated or lost one"
                        % (sorted(issues), wanted))

    # The parent is the source issue, kept: its title, and its request above the line.
    parent = issues.get(1, {})
    body = parent.get("body", "")
    if parent.get("title") != PARENT_TITLE:
        problems.append("#1 title is %r, expected the found parent's %r"
                        % (parent.get("title"), PARENT_TITLE))
    lines = LINE.findall(body)
    if lines != [SOURCE]:
        problems.append("#1 hidden lines are %s, expected exactly [%r]" % (lines, SOURCE))
    if REQUEST not in body.split("<!--")[0]:
        problems.append("#1 lost the original request above its hidden line")
    if "## Stories" not in body:
        problems.append("#1 has no ## Stories checklist")
    for story, number in sorted(STORIES.items()):
        if not re.search(r"^[ \t]*-[ \t]+\[[ xX]\][ \t]+%s[ \t]+#%d\b" % (story, number),
                         body, re.M):
            problems.append("#1 checklist does not link %s to #%d" % (story, number))

    # Each story has one issue, with its own hidden line once; #2 is the seeded one.
    for story, number in sorted(STORIES.items()):
        child = issues.get(number, {})
        found = LINE.findall(child.get("body", ""))
        expected = "%s %s" % (story, SOURCE)
        if found != [expected]:
            problems.append("#%d hidden lines are %s, expected exactly [%r]"
                            % (number, found, expected))
        text = (below(child.get("body", "")) or "").lower()
        if STORY_WORDS[story] not in text:
            problems.append("#%d body below its line does not carry %s's content (no %r)"
                            % (number, story, STORY_WORDS[story]))
        title = child.get("title", "")
        if number == SEEDED:
            if title != SEEDED_TITLE:
                problems.append("#%d title is %r, expected the found child to keep %r"
                                % (number, title, SEEDED_TITLE))
        else:
            led = "%s %s" % (PLAN_ID, story)
            if not title.startswith(led):
                problems.append("#%d title is %r, expected one led by %r, so the id names "
                                "a story on a tracker shared by several plans"
                                % (number, title, led))

    # The Durability rule, over every body below its hidden line.
    for number, issue in sorted(issues.items()):
        text = below(issue.get("body", ""))
        if text is None:
            problems.append("#%d has no hidden line" % number)
            continue
        leaked = PATH.search(text)
        if leaked:
            problems.append("#%d names a file path below its hidden line: %r"
                            % (number, leaked.group(0)))
        if PROOF.search(text):
            problems.append("#%d carries a Proof line" % number)

    # The mapped link operation, used for the plan's one dependency and nothing else.
    for number, blockers in sorted(BLOCKED_BY.items()):
        found = sorted(issues.get(number, {}).get("blocked_by", []))
        if found != blockers:
            problems.append("#%d is blocked by %s, expected %s" % (number, found, blockers))

    # The second step creates nothing: no create after the checkpoint it opened with.
    marks = [i for i, event in enumerate(log) if event.get("op") == "checkpoint"]
    if len(marks) != 1:
        problems.append("the log holds %d checkpoints, expected the one step 2 opens with "
                        "(the subject skipped the prompt's checkpoint, not a skill failure)"
                        % len(marks))
    else:
        created = [e for e in log[marks[0]:] if e.get("op") == "create"]
        if created:
            problems.append("step 2 created issue(s) %s" % [e.get("number") for e in created])
        for number, blockers in sorted(BLOCKED_BY.items()):
            for blocker in blockers:
                if not any(e.get("op") == "block" and e.get("number") == number
                           and e.get("blocker") == blocker for e in log[:marks[0]]):
                    problems.append("step 1 never ran the mapped add blocked-by for #%d by #%d"
                                    % (number, blocker))
        relinked = [e for e in log[marks[0]:] if e.get("op") == "block"]
        if relinked:
            problems.append("step 2 wrote link(s) %s it could have read first"
                            % ["#%s by #%s" % (e.get("number"), e.get("blocker")) for e in relinked])
        if not any(e.get("op") == "create" for e in log[:marks[0]]):
            problems.append("step 1 created nothing, so #3 was never made")

    for problem in problems:
        sys.stderr.write(problem + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
