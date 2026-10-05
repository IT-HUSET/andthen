#!/usr/bin/env python3
"""End-state reconciliation for the init-empty case, run with cwd = the workspace.

Case data, not harness: an empty repository gets one question, what the project is,
and its end state is an instruction file whose Project Overview carries the reply, an
Index preamble keeping the first-write rule, and no Key Dev Commands document, since nothing in the repository declares a command.
Whether exactly one question came before any write stays the rubric's call.

The reply is read by meaning: `photographs` and `pictures` name what `photos` does,
and `by the date taken` what `by capture date` does, so neither is a literal needle.

Python 3 standard library only, 3.9-compatible."""

import re
import sys
from pathlib import Path

INSTRUCTION_FILES = ("AGENTS.md", "CLAUDE.md")
COMMANDS_DOCUMENT = "KEY_DEVELOPMENT_COMMANDS.md"
OVERVIEW = re.compile(r"(?ms)^##\s+Project Overview\s*$(.*?)(?=^##\s|\Z)")
# Every later writer's creation rule lives in this one preamble sentence.
FIRST_WRITE = re.compile(r"first skill that writes to it creates", re.I)
REPLY = (
    ("the photos it works on", re.compile(r"photo|picture|image", re.I)),
    ("the renaming by date", re.compile(r"renam\w*[^.\n]{0,80}\b(?:date|taken|captur|timestamp|exif)"
                                        r"|\b(?:date|taken|captur|timestamp|exif)\w*[^.\n]{0,80}renam",
                                        re.I)),
)


def main():
    present = [Path(n) for n in INSTRUCTION_FILES if Path(n).is_file()]
    problems = []
    if not present:
        problems.append("no AGENTS.md or CLAUDE.md in the workspace")
    text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in present)
    overview = OVERVIEW.search(text)
    if present and not overview:
        problems.append("the instruction file has no Project Overview section")
    elif overview:
        problems += ["the Project Overview does not state %s" % part
                     for part, pattern in REPLY if not pattern.search(overview.group(1))]
    if present and not FIRST_WRITE.search(text):
        problems.append("the Index preamble lost the first-write rule")
    problems += ["%s exists, though nothing declares a command" % p
                 for p in Path(".").rglob(COMMANDS_DOCUMENT) if ".git" not in p.parts]
    for problem in problems:
        sys.stderr.write(problem + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
