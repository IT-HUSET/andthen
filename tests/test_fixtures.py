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
PR_SECTION = REPO / "plugin/skills/ship/references/pr-section.md"
PR_DESCRIPTION = RENDERS / "pr-description.md"

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


CELL = re.compile(r"(?<!\\)\|")
SEPARATOR = re.compile(r"^\|(?:\s*-+\s*\|)+$")


def tables(lines):
    """Each run of table lines as rows of stripped cells, separator dropped."""
    found, current = [], None
    for line in lines:
        if not line.startswith("|"):
            current = None
            continue
        if current is None:
            current = []
            found.append(current)
        if not SEPARATOR.match(line.strip()):
            current.append([cell.strip() for cell in CELL.split(line.strip())[1:-1]])
    return found


def choices(cell):
    """`{{A / B}}` -> [A, B]."""
    return [choice.strip() for choice in cell.strip("{}").split(" / ")]


def section_spec():
    """What `ship`'s reference fixes: heading, line labels, table headers,
    lens rows with their verdicts and remediated tokens, and the read-closely tokens."""
    text = PR_SECTION.read_text(encoding="utf-8")
    heading = re.search(r"^## .+$", text, re.M).group(0)
    body = [line for line in text.split(heading, 1)[1].splitlines() if not line.startswith(">")]
    outcome, lens, reading = tables(body)
    return {"heading": heading, "labels": re.findall(r"^([A-Z][A-Za-z]+): ", "\n".join(body), re.M),
            "headers": [outcome[0], lens[0], reading[0]],
            "lenses": {row[0]: choices(row[1]) for row in lens[1:]},
            "remediated": {row[0]: choices(row[3]) for row in lens[1:]},
            "reasons": choices(reading[1][0])}


def section_problems(body):
    """Every way a pull request body's section departs from the reference."""
    spec = section_spec()
    lines = body.splitlines()
    starts = [i for i, line in enumerate(lines) if line == spec["heading"]]
    if len(starts) != 1:
        return [f"{len(starts)} section headings"]
    rest = lines[starts[0] + 1:]
    section = rest[:next((i for i, line in enumerate(rest) if line.startswith("## ")), len(rest))]
    problems = [f"no {label}: line" for label in spec["labels"]
                if not any(line.startswith(f"{label}: ") for line in section)]
    found = tables(section)
    if [table[0][0] for table in found] != [header[0] for header in spec["headers"]]:
        return problems + [f"tables {[table[0][0] for table in found]}"]
    headers = [list(header) for header in spec["headers"]]
    if sum(line.startswith("PRD: ") for line in section) > 1:
        headers[0].insert(headers[0].index("Requirements") + 1, "PRD")
    for table, header in zip(found, headers):
        if table[0] != header:
            problems.append(f"header {table[0]}")
        problems += [f"row width {row}" for row in table[1:] if len(row) != len(header)]
        problems += [f"empty cell {row}" for row in table[1:] if {"", "–", "—"} & set(row)]
    outcome, lens, reading = found
    if [row[0] for row in lens[1:]] != list(spec["lenses"]):
        problems.append(f"lens rows {[row[0] for row in lens[1:]]}")
    for name, verdict, commit, remediated in (row[:4] for row in lens[1:] if len(row) >= 4):
        if verdict not in spec["lenses"].get(name, []):
            problems.append(f"{name} verdict {verdict!r}")
        if (verdict == "not reviewed") != (commit == "-"):
            problems.append(f"{name} commit {commit!r}")
        if remediated not in spec["remediated"].get(name, []) or (
                verdict == "not reviewed" and remediated != "-"):
            problems.append(f"{name} remediated {remediated!r}")
    problems += [f"reason {row[0]!r}" for row in reading[1:] if row[0] not in spec["reasons"]]
    if any(row[1:2] == ["not reviewed"] for row in lens[1:]) and not any(
            row[0] == "unchecked" for row in reading[1:]):
        problems.append("a lens is not reviewed and no unchecked row says so")
    problems += [f"outcome {row[2]!r}" for row in outcome[1:]
                 if len(row) > 2 and row[0] != "-" and not re.match(r"^(\[OC\d{2}\] |-$)", row[2])]
    return problems


class ShipSectionTest(unittest.TestCase):
    """A viewer joins a shipped pull request to its PRD, proof, and reviews by
    the section `ship`'s reference fixes, so the corpus body must carry exactly
    that shape, and the checker must fire on each departure a writer is likely
    to make."""

    def setUp(self):
        self.body = PR_DESCRIPTION.read_text(encoding="utf-8")

    def test_the_fixture_carries_the_section_the_reference_fixes(self):
        self.assertEqual(section_problems(self.body), [])

    def test_the_section_restates_prose_rather_than_replacing_it(self):
        prose = self.body.split(section_spec()["heading"])[0]
        self.assertIn("## Where to read closely", prose)

    def test_the_section_still_conforms_without_its_details_block(self):
        bare = re.sub(r"^(</?details>|<summary>.*</summary>)\n", "", self.body, flags=re.M)
        self.assertNotEqual(bare, self.body)
        self.assertEqual(section_problems(bare), [])

    def test_a_row_without_a_plan_carries_an_untagged_outcome(self):
        row = "| S01 | scripts/fixtures/renders/plan.json | [OC01] A page script cannot read the session cookie. |"
        planless = self.body.replace(row, "| - | - | A page script cannot read the session cookie. |")
        self.assertNotEqual(planless, self.body)
        self.assertEqual(section_problems(planless), [])

    def test_each_departure_fires_with_its_problem(self):
        body = self.body
        departures = [
            (body + "\n## Ship summary\n", "2 section headings"),
            (body.replace("\nUndo: ", "\nRollback: "), "no Undo: line"),
            (body.replace("\nPRD: ", "\nRequirements file: "), "no PRD: line"),
            (body.replace("| gap |", "| spec |"), "lens rows"),
            (body.replace("| unchecked |", "| unreviewed |", 1), "reason 'unreviewed'"),
            (body.replace("| security | not reviewed | - |", "| security | not reviewed | – |"),
             "empty cell"),
            (body.replace("| Reviewed commit |", "| Commit |"), "header"),
            (body.replace("| code | FAIL |", "| code | Needs Fixes |"), "code verdict 'Needs Fixes'"),
            (body.replace("| code | FAIL | 9c4e2a7 | yes |", "| code | FAIL (remediated) | 9c4e2a7 | - |"),
             "code verdict"),
            (body.replace("| 9c4e2a7 | yes |", "| 9c4e2a7 | Yes |"), "code remediated 'Yes'"),
            (body.replace("| security | not reviewed | - | - |", "| security | not reviewed | - | yes |"),
             "security remediated 'yes'"),
            (body.replace(" | Remediated |", " |").replace("| 9c4e2a7 | yes |", "| 9c4e2a7 |"), "header"),
            (body.replace("| [OC01] A page script", "| A page script"), "outcome"),
            (body.replace("PRD: ", "PRD: docs/other/prd.md\nPRD: ", 1), "header"),
        ]
        for departed, problem in departures:
            with self.subTest(problem):
                self.assertNotEqual(departed, body, "departure did not apply")
                self.assertTrue(any(p.startswith(problem) for p in section_problems(departed)),
                                section_problems(departed))


class NotesSampleTest(unittest.TestCase):
    """The payload shape a viewer sends back: owner and path
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
