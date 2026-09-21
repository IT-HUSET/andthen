#!/usr/bin/env python3
"""The review report's pinned header is a contract in shipped text, so it is
proved the way a gate over shipped text is: two checkers run against
`review/SKILL.md` Step 5 (which specifies the header), against both corpus
fixtures (which carry it), and against synthetic prose in both directions.

Downstream tooling reads lens, target, and revision off these labels without
parsing the title or the filename, so a renamed or dropped field is a breaking
change and has to fail here. The mixed fixture additionally pins the single
`## Verdict` section - a second one breaks the shape a reader and an agent both
match the verdict on.
"""
import fnmatch
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "plugin" / "skills" / "review" / "SKILL.md"
ANNOTATION = ROOT / "plugin" / "skills" / "implement-fix" / "references" / "report-annotation.md"
INIT = ROOT / "plugin" / "skills" / "init" / "SKILL.md"
NAME_FORM = "<feature>-andthen-<suffix>-<agent>-<YYYY-MM-DD>.md"
IGNORE_PATTERN = "*-andthen-*-review-*.md"
RENDERS = ROOT / "scripts" / "fixtures" / "renders"
REPORT = RENDERS / "review-report.md"
MIXED = RENDERS / "review-report-mixed.md"

# Present in every report file.
REQUIRED = ("Review mode", "Target", "Revision")

LABEL = re.compile(r"^\*\*([A-Z][A-Za-z ]*)\*\*:", re.M)
MARKER = re.compile(r"^\s*(\*\*Remediated\*\*:.*\S)\s*$", re.M)


def marker_line(text):
    """The one line that is itself a `**Remediated**:` marker, not prose about one."""
    found = MARKER.findall(text)
    return found[0] if len(found) == 1 else None


def undeclared(text, fields):
    """Header fields the text does not specify as a `**Label**:` bold label."""
    return [f for f in fields if f"**{f}**:" not in text]


def header_labels(report):
    """The bold labels between the H1 and the first section, in file order."""
    head = []
    for line in report.splitlines()[1:]:
        if line.startswith("## "):
            break
        head.append(line)
    return LABEL.findall("\n".join(head))


FOLLOWUP_STATE = re.compile(r"\b(resolved|still open|regressed)\b", re.I)


def states_earlier_finding_state(text):
    """Whether a report with a `**Follows**:` header states an earlier
    finding's state - resolved, still open, or regressed - in its body,
    above its own `## Remediation Status` heading. The header itself is
    excluded so a `**Resolved chain**:` label can't pass the check by
    accident. The follow-up contract (SKILL.md Step 1 § Earlier reports)
    requires the review to say this itself; the Remediation Status section
    is written afterward by `implement-fix` and does not count, or a report
    could satisfy the contract without the review pass ever having compared
    against the earlier findings."""
    body = text.split("\n## ", 1)[-1] if "\n## " in text else ""
    before = body.split("## Remediation Status")[0]
    return bool(FOLLOWUP_STATE.search(before))


class SkillSpecifiesTheHeaderTest(unittest.TestCase):
    """Step 5 of the skill is the one place the header is specified; the
    fixtures and every consumer follow it."""

    def setUp(self):
        self.step5 = SKILL.read_text(encoding="utf-8").split("### 5. Write One Report")[1]

    def test_each_field_is_specified_by_the_skill_that_writes_it(self):
        self.assertEqual(undeclared(self.step5, REQUIRED + ("Resolved chain", "Follows")), [])
        self.assertEqual(undeclared(ANNOTATION.read_text(encoding="utf-8"), ("Remediated",)), [])

    def test_a_dropped_field_fires(self):
        self.assertEqual(undeclared("**Review mode**: x\n**Target**: y", REQUIRED),
                         ["Revision"])

    def test_the_ignore_pattern_init_offers_matches_step_5_names_and_nothing_hand_written(self):
        """The `andthen` literal in the name exists for this pattern: without it
        an ignore rule leans on `-review-` and swallows a project's own files,
        and a wrongly ignored file fails silently - it just never gets committed."""
        self.assertIn(NAME_FORM, self.step5)
        self.assertIn(IGNORE_PATTERN, INIT.read_text(encoding="utf-8"))
        suffixes = re.findall(r"^\| [^|]+ \| `([a-z]+-review)` \|", self.step5, re.M)
        self.assertEqual(len(suffixes), 5)
        for suffix in suffixes:
            name = (NAME_FORM.replace("<feature>", "csv-export-s02").replace("<suffix>", suffix)
                    .replace("<agent>", "claude").replace("<YYYY-MM-DD>", "2026-09-18"))
            self.assertTrue(fnmatch.fnmatchcase(name, IGNORE_PATTERN), name)
            self.assertTrue(fnmatch.fnmatchcase(name[:-3] + "-2.md", IGNORE_PATTERN), name)
        for hand_written in ("design-review-notes-2026-01-01.md",
                             "csv-export-code-review-claude-2026-09-18.md"):
            self.assertFalse(fnmatch.fnmatchcase(hand_written, IGNORE_PATTERN), hand_written)


class FixtureHeaderTest(unittest.TestCase):
    """The corpus is what downstream tooling pins, so each fixture's header sits
    under the H1, ahead of any section, in the order Step 5 lists."""

    def test_single_lens_fixture_carries_the_required_fields(self):
        self.assertEqual(header_labels(REPORT.read_text(encoding="utf-8")), list(REQUIRED))

    def test_mixed_fixture_carries_every_field(self):
        self.assertEqual(header_labels(MIXED.read_text(encoding="utf-8")),
                         ["Review mode", "Resolved chain", "Target", "Revision",
                          "Follows", "Remediated"])

    def test_a_label_below_the_first_section_is_not_header(self):
        self.assertEqual(header_labels("# R\n\n**Target**: a\n\n## Verdict\n\n**Revision**: b\n"),
                         ["Target"])

    def test_the_marker_matches_the_line_implement_fix_is_told_to_write(self):
        """`implement-fix` owns the marker's exact text, so the fixture copies it
        from there rather than restating it - a drifted copy is what a consumer
        pins and then fails to match."""
        literal = marker_line(ANNOTATION.read_text(encoding="utf-8"))
        self.assertIsNotNone(literal, "report-annotation.md states no marker line")
        self.assertEqual(marker_line(MIXED.read_text(encoding="utf-8")), literal)
        self.assertIsNone(marker_line("**Remediated**: a\n**Remediated**: b\n"))

    def test_mixed_fixture_has_one_verdict_section_with_the_gap_block_under_it(self):
        text = MIXED.read_text(encoding="utf-8")
        self.assertEqual(re.findall(r"^## Verdict$", text, re.M), ["## Verdict"])
        self.assertTrue(re.search(r"^### Gap$", text, re.M))
        self.assertTrue(re.search(r"^\*\*Overall: (PASS|FAIL)\*\*$", text, re.M))

    def test_every_follow_up_fixture_states_earlier_findings_state(self):
        """Every fixture that carries `**Follows**:` proves the follow-up
        contract, not just the header shape - a report over an earlier one
        that never says what became of its findings leaves a reader with no
        way to tell resolved from still-open from regressed."""
        for path in sorted(RENDERS.glob("review-report*.md")):
            text = path.read_text(encoding="utf-8")
            if "**Follows**:" not in text:
                continue
            self.assertTrue(states_earlier_finding_state(text), path.name)

    def test_the_state_checker_fires_in_both_directions(self):
        passing = ("**Follows**: x\n\n## Executive Summary\n\n"
                   "The earlier finding is now resolved.\n\n## Remediation Status\n")
        below_only = ("**Follows**: x\n\n## Executive Summary\n\nSee below.\n\n"
                      "## Remediation Status\n\nResolved there.\n")
        unresolved_only = ("**Follows**: x\n\n## Executive Summary\n\n"
                           "Still UNRESOLVED per below.\n\n## Remediation Status\n")
        self.assertTrue(states_earlier_finding_state(passing))
        self.assertFalse(states_earlier_finding_state(below_only))
        self.assertFalse(states_earlier_finding_state(unresolved_only))


if __name__ == "__main__":
    unittest.main()
