#!/usr/bin/env python3
"""One aggregate word budget over the shipped prompt surface: `str.split()` words
over `plugin/**/*.md` but `README.md`, against the number in
`tests/surface-budget.json`. Words, not files – a per-file ceiling does not see
growth that arrives as new files. ADR-018 carries the rationale; this enforces it."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUDGET = Path(__file__).resolve().parent / "surface-budget.json"


def surface_words():
    """`str.split()` words over every shipped `plugin/**/*.md` but `README.md`."""
    return sum(
        len(path.read_text(encoding="utf-8").split())
        for path in sorted((ROOT / "plugin").rglob("*.md"))
        if path.name != "README.md"
    )


class SurfaceBudgetTest(unittest.TestCase):
    def test_surface_stays_within_budget(self):
        budget = json.loads(BUDGET.read_text(encoding="utf-8"))["words"]
        words = surface_words()
        self.assertLessEqual(
            words,
            budget,
            f"shipped prompt surface is {words} words against a budget of {budget} "
            f"({words - budget} over): cut elsewhere, or raise the number in "
            f"tests/surface-budget.json in this commit – the raise is the reviewed act.",
        )


if __name__ == "__main__":
    unittest.main()
