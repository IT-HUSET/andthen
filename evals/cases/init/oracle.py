#!/usr/bin/env python3
"""End-state reconciliation for the init case, run with cwd = the workspace.

Case data, not harness: an existing repository is set up with no question, so its
end state is an instruction file whose Project Document Index names every Core
document and keeps the preamble's first-write rule, a Key Dev Commands document naming the repository's own test command, and
none of the other five Core documents - each of those is created later, by the first
skill that writes to it. Whether the run asked nothing and closed on its offers stays
the rubric's call.

The test command is read by meaning: `make test` and the unittest invocation behind it
are one command, and a literal needle for either fails a correct document that chose
the other.

Python 3 standard library only, 3.9-compatible."""

import re
import sys
from pathlib import Path

INSTRUCTION_FILES = ("AGENTS.md", "CLAUDE.md")
CORE_ENTRIES = ("Product", "Architecture", "Key Dev Commands", "Testing Strategy",
                "Decisions", "Learnings")
# Created on first write, never by init.
LATER_DOCUMENTS = ("PRODUCT.md", "ARCHITECTURE.md", "TESTING-STRATEGY.md",
                   "DECISIONS.md", "LEARNINGS.md")
COMMANDS_DOCUMENT = "KEY_DEVELOPMENT_COMMANDS.md"
TEST_COMMAND = re.compile(r"make\s+test|-m\s+unittest", re.I)
# Every later writer's creation rule lives in this one preamble sentence.
FIRST_WRITE = re.compile(r"first skill that writes to it creates", re.I)


def entry(name):
    """An Index entry in the template's heading shape, the older bullet shape, or a
    table row naming it."""
    return re.compile(r"(?m)^\s*(?:#{2,6}\s*\**%s\b|[-*]\s*\*\*%s\*\*|\|\s*\**%s\**\s*\|)"
                      % ((re.escape(name),) * 3))


def files_named(name):
    return [p for p in Path(".").rglob(name) if ".git" not in p.parts]


def main():
    present = [Path(n) for n in INSTRUCTION_FILES if Path(n).is_file()]
    problems = []
    if not present:
        problems.append("no AGENTS.md or CLAUDE.md in the workspace")
    index = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in present)
    problems += ["the instruction file's Index has no %s entry" % name
                 for name in CORE_ENTRIES if present and not entry(name).search(index)]
    if present and not FIRST_WRITE.search(index):
        problems.append("the Index preamble lost the first-write rule")
    commands = files_named(COMMANDS_DOCUMENT)
    if not commands:
        problems.append("no %s in the workspace" % COMMANDS_DOCUMENT)
    elif not any(TEST_COMMAND.search(p.read_text(encoding="utf-8", errors="replace"))
                 for p in commands):
        problems.append("%s does not name the repository's test command" % commands[0])
    problems += ["%s exists before any skill wrote to it" % p
                 for name in LATER_DOCUMENTS for p in files_named(name)]
    for problem in problems:
        sys.stderr.write(problem + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
