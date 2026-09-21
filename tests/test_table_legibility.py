#!/usr/bin/env python3
"""A markdown table cell holds a short phrase, not a paragraph. Agents and humans
edit shipped prompts in a plain editor, where a 300-character cell cannot be
aligned, wrapped, or diffed – the pipes stop lining up and every reword rewrites
the whole row. Anything needing a full sentence, more than one clause, or an
instruction is a list instead (one bullet per former row, bold lead for the key
column). The rule is stated in `docs/SKILL-AUTHORING-GUIDELINES.md`; this proves it.

Both directions, per the prompt-contract idiom: the scanner fires on a
paragraph-cell table and stays silent on the list it becomes, and the shipped
tree is clean."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# A cell longer than this is prose wearing a table's clothes.
LIMIT = 200

SCAN_DIRS = (
    "plugin/skills",
    "plugin/references",
)
SCAN_FILES = ("AGENTS.md",)


def _split_cells(line):
    """Cells of one markdown table row, `\\|` kept as literal text."""
    body = line.strip().strip("|")
    cells, current, escaped = [], [], False
    for char in body:
        if escaped:
            current.append(char)
            escaped = False
        elif char == "\\":
            current.append(char)
            escaped = True
        elif char == "|":
            cells.append("".join(current))
            current = []
        else:
            current.append(char)
    cells.append("".join(current))
    return cells


def _is_bare_code(cell):
    """A cell that is nothing but one inline-code span – a command or identifier.
    It carries no prose to move into a list and no rewording shortens it."""
    return len(cell) > 2 and cell.startswith("`") and cell.endswith("`") and "`" not in cell[1:-1]


def oversized_cells(text, limit=LIMIT):
    """(line number, cell) for every table cell over `limit`, code fences skipped."""
    found, fenced = [], False
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fenced = not fenced
            continue
        if fenced or not stripped.startswith("|"):
            continue
        for cell in _split_cells(line):
            cell = cell.strip()
            if len(cell) > limit and set(cell) - set("-: ") and not _is_bare_code(cell):
                found.append((lineno, cell))
    return found


def scanned_files():
    for name in SCAN_FILES:
        yield ROOT / name
    for rel in SCAN_DIRS:
        yield from sorted((ROOT / rel).rglob("*.md"))
    # docs/ top level only: docs/temp is transient, docs/adrs is a decision record.
    yield from sorted((ROOT / "docs").glob("*.md"))
    yield from sorted((ROOT / "docs/guidelines").glob("*.md"))
    yield from sorted((ROOT / "docs/prompt-guidelines").glob("*.md"))


PARAGRAPH_TABLE = """
| Document Type | Location | Notes |
|---|---|---|
| Specs & Plans | `docs/specs/` | Local working specs, never committed: PRD, plan.json, and one FIS per story for one feature, co-located. Read the governing FIS before implementing a story; execution updates the plan and FIS, never the PRD. A FIS past this ceiling is a story too big: decompose it, never trim it. |
"""

LIST_REPLACEMENT = """
- **Specs & Plans** – `docs/specs/`, 700 lines/file – Local working specs, never committed: PRD, plan.json, and one FIS per story for one feature, co-located. Read the governing FIS before implementing a story; execution updates the plan and FIS, never the PRD.
"""

SHORT_CELL_TABLE = """
| Tier | Command |
|------|---------|
| fast | `python3 -m unittest discover -s tests` |
"""


class ScannerTest(unittest.TestCase):
    def test_fires_on_a_paragraph_cell(self):
        hits = oversized_cells(PARAGRAPH_TABLE)
        self.assertEqual(len(hits), 1)
        self.assertTrue(hits[0][1].startswith("Local working specs"))

    def test_silent_on_the_list_it_becomes(self):
        self.assertEqual(oversized_cells(LIST_REPLACEMENT), [])

    def test_short_cells_stay_a_table(self):
        self.assertEqual(oversized_cells(SHORT_CELL_TABLE), [])

    def test_alignment_row_is_not_a_cell(self):
        self.assertEqual(oversized_cells("|" + "-" * 400 + "|\n"), [])

    def test_fenced_example_tables_are_skipped(self):
        self.assertEqual(
            oversized_cells("```\n" + PARAGRAPH_TABLE.strip() + "\n```\n"), []
        )

    def test_a_long_command_cell_is_not_prose(self):
        self.assertEqual(oversized_cells("| full | `" + "a b " * 60 + "` |\n"), [])

    def test_a_command_followed_by_prose_still_fires(self):
        self.assertEqual(len(oversized_cells("| full | `cmd` " + "and more " * 30 + "|\n")), 1)

    def test_escaped_pipe_does_not_split_a_cell(self):
        self.assertEqual(_split_cells(r"| a \| b | c |"), [r" a \| b ", " c "])


class ShippedProseTest(unittest.TestCase):
    def test_no_shipped_table_cell_is_a_paragraph(self):
        offenders = []
        for path in scanned_files():
            for lineno, cell in oversized_cells(path.read_text(encoding="utf-8")):
                rel = path.relative_to(ROOT)
                offenders.append(f"{rel}:{lineno} ({len(cell)} chars) {cell[:70]}…")
        self.assertEqual(
            offenders,
            [],
            f"table cells over {LIMIT} characters – make each a list entry, or trim it:\n"
            + "\n".join(offenders),
        )


if __name__ == "__main__":
    unittest.main()
