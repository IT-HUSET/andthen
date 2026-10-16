#!/usr/bin/env python3
"""End-state reconciliation for the init case, run with cwd = the workspace.

Case data, not harness: an existing repository is set up with no question, so its
end state is an instruction file whose Project Document Index keeps the preamble's
first-write rule and lists only what exists - Key Dev Commands and Agent Temp - a Key
Dev Commands document naming the repository's own test command, and none of the other
five Core documents nor their entries - each of those is created, and its entry added,
by the first skill that writes to it. Whether the run asked nothing and closed on its
offers stays the rubric's call.

The test command is read by meaning: `make test` and the unittest invocation behind it
are one command, and a literal needle for either fails a correct document that chose
the other.

Python 3 standard library only, 3.9-compatible."""

import re
import sys
from pathlib import Path

INSTRUCTION_FILES = ("AGENTS.md", "CLAUDE.md")
INIT_ENTRIES = ("Key Dev Commands", "Agent Temp")
# Created, and listed, on first write, never by init.
LATER_DOCUMENTS = (("Product", "PRODUCT.md"), ("Architecture", "ARCHITECTURE.md"),
                   ("Testing Strategy", "TESTING-STRATEGY.md"), ("Decisions", "DECISIONS.md"),
                   ("Learnings", "LEARNINGS.md"))
COMMANDS_DOCUMENT = "KEY_DEVELOPMENT_COMMANDS.md"
TEST_COMMAND = re.compile(r"make\s+test|-m\s+unittest", re.I)
# Every later writer's creation rule lives in this one preamble sentence.
FIRST_WRITE = re.compile(r"seed <name>", re.I)


def entry(name):
    """An Index entry in the heading shape, the bullet shape, or a table row naming it."""
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
                 for name in INIT_ENTRIES if present and not entry(name).search(index)]
    problems += ["the Index lists %s, which does not exist yet" % name
                 for name, _ in LATER_DOCUMENTS if present and entry(name).search(index)]
    if present and not FIRST_WRITE.search(index):
        problems.append("the Index preamble lost the first-write rule")
    commands = files_named(COMMANDS_DOCUMENT)
    if not commands:
        problems.append("no %s in the workspace" % COMMANDS_DOCUMENT)
    elif not any(TEST_COMMAND.search(p.read_text(encoding="utf-8", errors="replace"))
                 for p in commands):
        problems.append("%s does not name the repository's test command" % commands[0])
    problems += ["%s exists before any skill wrote to it" % p
                 for _, document in LATER_DOCUMENTS for p in files_named(document)]
    for problem in problems:
        sys.stderr.write(problem + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
