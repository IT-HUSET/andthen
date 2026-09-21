#!/usr/bin/env python3
"""Corpus tests for scripts/fixtures/renders/.

    python3 tests/test_fixtures.py

The corpus README's table is the contract downstream tooling reads: type, fixture,
owning skill, where notes go. The suite reads that table rather than restating it,
so a new type ships with a fixture and a row, or fails here.
"""

import json
import pathlib
import re
import unittest

REPO = pathlib.Path(__file__).resolve().parents[1]
RENDERS = REPO / "scripts/fixtures/renders"
README = RENDERS / "README.md"
NOTES = RENDERS / "visual-review-notes.md"
PLAN_SCHEMA = REPO / "plugin/references/plan.schema.json"

H2 = re.compile(r"^##\s+(\S.*?)\s*$", re.M)
KEBAB_ANCHOR = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ROW = re.compile(r"^\| `([a-z][a-z-]*)` \| (.+?) \| `([a-z-]+:[a-z-]+)` \| (.+?) \|$", re.M)
NOTES_H1 = re.compile(r"^# ([a-z-]+:[a-z-]+) visual review notes for (\S+)$")


def table():
    """type -> (fixtures, owner, destination) from the README table."""
    rows = {}
    for m in ROW.finditer(README.read_text(encoding="utf-8")):
        fixtures = [RENDERS / f for f in re.findall(r"`([^`]+)`", m.group(2))]
        rows[m.group(1)] = (fixtures, m.group(3), m.group(4))
    return rows


def h2_headings(path):
    return H2.findall(path.read_text(encoding="utf-8"))


def kebab(heading):
    return re.sub(r"^-+|-+$", "", re.sub(r"[^a-z0-9]+", "-", heading.lower()))


class CorpusTest(unittest.TestCase):

    def test_every_type_in_the_table_has_its_fixture(self):
        rows = table()
        self.assertGreaterEqual(len(rows), 17, "README table did not parse")
        for artifact_type, (fixtures, owner, _) in rows.items():
            with self.subTest(artifact_type):
                self.assertTrue(fixtures, "row names no fixture")
                for fixture in fixtures:
                    self.assertTrue(fixture.is_file(), f"missing fixture {fixture}")
                self.assertTrue((REPO / "plugin/skills" / owner.split(":")[1]).is_dir(),
                                f"owner {owner} is not a shipped skill")

    def test_every_fixture_in_the_directory_is_in_the_table(self):
        listed = {f.name for fixtures, _, _ in table().values() for f in fixtures}
        listed |= {README.name, NOTES.name}
        self.assertEqual(sorted(p.name for p in RENDERS.iterdir()), sorted(listed))

    def test_h2_anchors_are_kebab_and_collision_free(self):
        """A section anchor is the lowercase-kebab of the verbatim H2, unique per
        document. A fixture that needed a `-2` suffix would hide the collision rule
        behind an accident, so the corpus stays collision-free by construction."""
        for artifact_type, (fixtures, _, _) in table().items():
            for fixture in fixtures:
                if fixture.suffix != ".md":
                    continue
                with self.subTest(fixture.name):
                    anchors = [kebab(h) for h in h2_headings(fixture)]
                    self.assertTrue(anchors, "fixture has no H2 sections")
                    for anchor in anchors:
                        self.assertRegex(anchor, KEBAB_ANCHOR)
                    self.assertEqual(len(anchors), len(set(anchors)))

    def test_plan_fixture_matches_the_schema_version_validate_plan_enforces(self):
        supported = json.loads(PLAN_SCHEMA.read_text(encoding="utf-8"))
        plan = json.loads((RENDERS / "plan.json").read_text(encoding="utf-8"))
        self.assertEqual(plan["schemaVersion"], supported["properties"]["schemaVersion"]["const"])


class NotesSampleTest(unittest.TestCase):
    """The payload shape a viewer sends back and now-what routes on: owner and path
    in the H1, one `## Section:` block per annotated heading of that artifact,
    bullets, and two-space continuation for a multi-line note."""

    def test_header_names_a_table_owner_and_a_corpus_fixture(self):
        lines = NOTES.read_text(encoding="utf-8").splitlines()
        m = NOTES_H1.match(lines[0])
        self.assertIsNotNone(m, lines[0])
        owner, path = m.groups()
        fixture = REPO / path
        self.assertTrue(fixture.is_file(), f"{path} is not a corpus fixture")
        owners = {o for fixtures, o, _ in table().values() if fixture in fixtures}
        self.assertEqual(owners, {owner})
        self.assertEqual(lines[1], "")

    def test_sections_are_verbatim_headings_with_bullets_and_continuations(self):
        text = NOTES.read_text(encoding="utf-8")
        path = NOTES_H1.match(text.splitlines()[0]).group(2)
        headings = set(h2_headings(REPO / path))
        sections = re.findall(r"^## Section: (.+)$", text, re.M)
        self.assertTrue(sections)
        self.assertTrue(set(sections) <= headings, set(sections) - headings)
        body = [l for l in text.splitlines()[1:] if l and not l.startswith("## Section: ")]
        self.assertTrue(all(l.startswith("- ") or l.startswith("  ") for l in body), body)
        self.assertTrue(any(l.startswith("  ") for l in body), "no multi-line note in the sample")


if __name__ == "__main__":
    unittest.main(verbosity=1)
