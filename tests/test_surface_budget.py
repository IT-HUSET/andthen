#!/usr/bin/env python3
"""One aggregate word budget over the shipped prompt surface: `str.split()` words
over `plugin/**/*.md` but `README.md`, against the number in
`tests/surface-budget.json`. Words, not files – a per-file ceiling does not see
growth that arrives as new files. ADR-018 carries the rationale; this enforces it.

Every shipped description is held to one cap too, since all of them compete in
one listing on every turn."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUDGET = Path(__file__).resolve().parent / "surface-budget.json"
# Codex shares one budget across every installed description (8,000 chars when
# the window is unknown); one skill stays well under its share.
DESCRIPTION_CAP = 400


def surface_words():
    """`str.split()` words over every shipped `plugin/**/*.md` but `README.md`."""
    return sum(
        len(path.read_text(encoding="utf-8").split())
        for path in sorted((ROOT / "plugin").rglob("*.md"))
        if path.name != "README.md"
    )


def description(skill_md):
    """The `description:` value between the leading `---` fences."""
    head = skill_md.split("---", 2)[1]
    for line in head.splitlines():
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip()
    return ""


def over_cap(skills):
    """{skill: length} for every description past `DESCRIPTION_CAP`."""
    lengths = {name: len(description(text)) for name, text in skills.items()}
    return {name: length for name, length in lengths.items() if length > DESCRIPTION_CAP}


class SurfaceBudgetTest(unittest.TestCase):
    def test_surface_stays_within_budget(self):
        budget = json.loads(BUDGET.read_text(encoding="utf-8"))["words"]
        words = surface_words()
        self.assertLessEqual(
            words,
            budget,
            f"shipped prompt surface is {words} words against a budget of {budget} "
            f"({words - budget} over): cut elsewhere, or raise tests/surface-budget.json "
            f"in this commit to a round number a few percent above the count – "
            f"the raise is the reviewed act.",
        )


class DescriptionCapTest(unittest.TestCase):
    def test_every_shipped_description_within_cap(self):
        skills = {
            path.parent.name: path.read_text(encoding="utf-8")
            for path in sorted((ROOT / "plugin" / "skills").glob("*/SKILL.md"))
        }
        self.assertTrue(skills)
        self.assertEqual(over_cap(skills), {})

    def test_an_over_long_description_fires(self):
        synthetic = "---\ndescription: " + "x" * (DESCRIPTION_CAP + 1) + "\n---\n"
        self.assertEqual(over_cap({"synthetic": synthetic}), {"synthetic": DESCRIPTION_CAP + 1})


if __name__ == "__main__":
    unittest.main()
