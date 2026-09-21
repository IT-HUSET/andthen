#!/usr/bin/env python3
"""Every stated skill count equals the number of shipped skill directories. The
number lives in prose because readers want it, and prose does not follow the
tree: the single-plugin merge left "8 skills", "17 skills", and "6 skills" stale
in six places, caught only by review. Release notes are dated and stay out."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COUNT = re.compile(r"\b(\d+) skills\b")
DOCS = (
    "README.md",
    "plugin/README.md",
    "docs/ARCHITECTURE.md",
    "scripts/skills-overview.py",
)


def shipped_skills():
    return sum(
        1
        for path in (ROOT / "plugin" / "skills").iterdir()
        if path.is_dir() and not path.name.startswith(".")
    )


class SkillCountTest(unittest.TestCase):
    def test_every_stated_count_matches_the_shipped_tree(self):
        shipped = shipped_skills()
        for doc in DOCS:
            stated = []
            for number, line in enumerate(
                (ROOT / doc).read_text(encoding="utf-8").splitlines(), 1
            ):
                for match in COUNT.finditer(line):
                    stated.append((number, int(match.group(1))))
            self.assertTrue(stated, f"{doc} states no skill count; drop it from DOCS")
            for number, count in stated:
                self.assertEqual(
                    shipped,
                    count,
                    f"{doc}:{number} says {count} skills; plugin/skills/ holds {shipped}",
                )


if __name__ == "__main__":
    unittest.main()
