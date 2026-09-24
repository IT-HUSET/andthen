#!/usr/bin/env python3
"""The review report's shape is a contract in shipped text, so it is proved the
way a gate over shipped text is: checkers run against `review/references/
report-template.md` (which specifies the shape), against both corpus fixtures
(which carry it), and against synthetic prose in both directions.

Downstream tooling reads lens, target, and revision off the header labels, the
verdict off the `## Verdict` lines, and each finding off its heading and field
labels, without parsing the title or the filename, so a renamed, dropped, or
reordered piece is a breaking change and has to fail here. The checkers read
the section order, the finding fields, and the verdict shapes from the template
itself, never from a copy, so the fixtures cannot drift from it unseen.
"""
import fnmatch
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "plugin" / "skills" / "review" / "SKILL.md"
TEMPLATE = ROOT / "plugin" / "skills" / "review" / "references" / "report-template.md"
CALIBRATION = ROOT / "plugin" / "references" / "review-calibration.md"
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
    """The template is the one place the header is specified, and Step 5 of
    the skill writes the report from it; the fixtures and every consumer
    follow it."""

    def setUp(self):
        self.step5 = SKILL.read_text(encoding="utf-8").split("### 5. Write One Report")[1]

    def test_each_field_is_specified_by_the_skill_that_writes_it(self):
        self.assertIn("report-template.md", self.step5)
        self.assertEqual(undeclared(TEMPLATE.read_text(encoding="utf-8"),
                                    REQUIRED + ("Resolved chain", "Follows")), [])
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


PLACEHOLDER = re.compile(r"\{\{(.*?)\}\}")
CHOICE = re.compile(r"[\w -]+(?:[|/][\w -]+)+")
LENS_NOTE = re.compile(r"^> ([A-Z][a-z]+) lens\.")
FIELD = re.compile(r"^- (?:\*\*([A-Z][A-Za-z ]*)\*\*:|`([A-Z][a-z]+):`)[ \t]*(.*)$")
HEADING = re.compile(r"^(#{3,4}) (.+?)\s*$")
REMEDIATION = "Remediation Status"
REMEDIATION_NOTE = re.compile(r"^> `(- \*\*Finding .+)`$", re.M)
REMEDIATION_BULLET = re.compile(r"`(- \*\*Finding \{N\} .+?)`")


def placeholders_blanked(line):
    """A shape with every `{x}` or `{{x}}` placeholder reduced to `{}`, so two
    files that spell their placeholders differently can be compared."""
    return re.sub(r"\{\{?[^{}]*\}\}?", "{}", line)


def shape(line):
    """A template line as a regex: literal text escaped, a `{{A|B}}` or
    `{{A/B}}` placeholder the alternation it offers, any other placeholder
    free text."""
    parts, last = [], 0
    for match in PLACEHOLDER.finditer(line):
        parts.append(re.escape(line[last:match.start()]))
        choice = match.group(1)
        parts.append("(" + "|".join(map(re.escape, re.split(r"[|/]", choice))) + ")"
                     if CHOICE.fullmatch(choice) else r"(\S.*?)")
        last = match.end()
    parts.append(re.escape(line[last:]))
    return re.compile("".join(parts))


def row(line):
    """A table row with its column padding collapsed, so alignment is free."""
    return " ".join(line.split())


def sections(text):
    """(H2 title, body lines) in file order; the H1 and header are skipped."""
    found = []
    for line in text.splitlines():
        if line.startswith("## "):
            found.append((line[3:].strip(), []))
        elif found:
            found[-1][1].append(line)
    return found


def template_spec():
    """What the template fixes: section order, the lens each conditional
    section belongs to, the finding heading, each field's label and value
    shape, the verdict line shape per review mode, and the gap table rows."""
    text = TEMPLATE.read_text(encoding="utf-8")
    spec = {"order": [], "lens_of": {}, "heading": None, "fields": [], "verdict": {}, "gap_rows": [],
            "remediation": REMEDIATION_NOTE.search(text).group(1)}
    for title, body in sections(text):
        spec["order"].append(title)
        first = next((line for line in body if line.strip()), "")
        if match := LENS_NOTE.match(first):
            spec["lens_of"][title] = match.group(1).lower()
        for line in body:
            if line.startswith("### Finding "):
                spec["heading"] = shape(line[4:])
            elif spec["heading"] and title == "Findings" and (match := FIELD.match(line)):
                spec["fields"].append((match.group(1) or match.group(2), shape(match.group(3))))
            if title == "Verdict" and line.startswith("> - "):
                modes, _, rest = line[4:].partition(" – ")
                if span := re.search(r"`(\*\*.+?)`", rest):
                    for mode in re.findall(r"`([a-z]+)`", modes):
                        spec["verdict"][mode] = shape(span.group(1))
            if title == "Verdict" and "/10" in line:
                spec["gap_rows"].append(shape(row(line)))
    return spec


def carries_rows(lines, rows):
    """Whether `lines` hold a match for every row shape, in order."""
    remaining = iter(row(line) for line in lines if line.startswith("|"))
    return all(any(pattern.fullmatch(line) for line in remaining) for pattern in rows)


def finding_problems(lines, mode, lenses, spec):
    """Finding headings, their level and numbering, each block's fields and
    values, and a chain's lens subheadings."""
    level = "####" if mode == "mixed" else "###"
    labels = [label for label, _ in spec["fields"]]
    problems, numbers, subheadings, blocks = [], [], [], []
    for line in lines:
        if match := HEADING.match(line):
            hashes, title = match.groups()
            if not title.startswith("Finding "):
                subheadings.append(title)
                blocks.append(None)
                continue
            if hashes != level:
                problems.append(f"finding heading at {hashes}, expected {level}: {title!r}")
            if not (found := spec["heading"].fullmatch(title)):
                problems.append(f"finding heading {title!r}")
                blocks.append(None)
                continue
            numbers.append(found.group(1))
            blocks.append((found, []))
        elif blocks and blocks[-1] and (match := FIELD.match(line)):
            blocks[-1][1].append((match.group(1) or match.group(2), match.group(3)))
    for found, fields in filter(None, blocks):
        number = found.group(1)
        if [label for label, _ in fields] != labels:
            problems.append(f"finding {number} fields {[label for label, _ in fields]}")
            continue
        for (label, value), (_, value_shape) in zip(fields, spec["fields"]):
            if not value_shape.fullmatch(value):
                problems.append(f"finding {number} {label} value {value!r}")
    if numbers != [str(n) for n in range(1, len(numbers) + 1)]:
        problems.append(f"finding numbers {numbers}")
    if mode == "mixed" and subheadings != [lens.capitalize() for lens in lenses]:
        problems.append(f"lens subheadings {subheadings}")
    return problems


def shape_problems(text):
    """Every way a report departs from the template, empty when it conforms."""
    spec = template_spec()
    header = dict(re.findall(r"^\*\*([A-Z][A-Za-z ]*)\*\*:[ \t]*(.*)$", text.split("\n## ", 1)[0], re.M))
    mode = header.get("Review mode", "")
    lenses = [lens.strip() for lens in header.get("Resolved chain", mode).split(",")]
    problems = []

    found = sections(text)
    titles = [title for title, _ in found]
    if titles and titles[-1] == REMEDIATION:
        titles = titles[:-1]
    expected = [t for t in spec["order"] if t not in spec["lens_of"] or spec["lens_of"][t] in lenses]
    if titles != expected:
        problems.append(f"sections {titles} != {expected}")

    body = dict(found)
    problems += finding_problems(body.get("Findings", []), mode, lenses, spec)

    verdict = body.get("Verdict", [])
    above_subheading = verdict[:next((i for i, l in enumerate(verdict) if l.startswith("### ")), len(verdict))]
    line_shape = spec["verdict"].get(mode)
    stated = [line for line in above_subheading if line_shape and line_shape.fullmatch(line)]
    if len(stated) != 1:
        problems.append(f"{mode} verdict line not stated once above any subheading")
    elif next((line for line in body.get("Executive Summary", []) if line.strip()), None) != stated[0]:
        problems.append("Executive Summary does not open on the verdict line")
    if mode == "gap" and not carries_rows(verdict, spec["gap_rows"]):
        problems.append("gap verdict lacks the dimension table")
    if mode == "mixed" and "gap" in lenses:
        gap = "\n".join(verdict).split("\n### Gap\n", 1)
        block = gap[1].splitlines() if len(gap) == 2 else []
        if not any(spec["verdict"]["gap"].fullmatch(line) for line in block):
            problems.append("mixed verdict has no `### Gap` block with its overall line")
        elif not carries_rows(block, spec["gap_rows"]):
            problems.append("gap verdict lacks the dimension table")

    bullet = shape(spec["remediation"])
    for line in body.get(REMEDIATION, []):
        if line.startswith("- ") and not bullet.fullmatch(line):
            problems.append(f"remediation bullet {line[:60]!r}")
    return problems


GAP_TABLE = """| Dimension | Score | Threshold | Status |
|---|---|---|---|
| Functionality | 8/10 | >= 7 | PASS |
| Completeness | 6/10 | >= 9 | FAIL |
| Wiring | 9/10 | >= 8 | PASS |"""


def as_gap_report(report):
    """The single-lens code fixture recast as a gap report: no corpus fixture
    is one, and the gap verdict shape needs a positive case."""
    readiness = "**Readiness: Needs Fixes** - 1 HIGH, 1 LOW, no CRITICAL."
    head, rest = report.split("## Compliance", 1)
    report = head + "## Critic Coverage" + rest.split("## Critic Coverage", 1)[1]
    report = report.replace(f"## Verdict\n\n{readiness}", f"## Verdict\n\n{GAP_TABLE}\n\n**Overall: FAIL**")
    return (report.replace(readiness, "**Overall: FAIL**")
            .replace("# Code Review", "# Gap Review").replace("**Review mode**: code", "**Review mode**: gap"))


class ReportShapeTest(unittest.TestCase):
    """Downstream tooling parses a report by the template's literal shapes, so
    the fixtures it pins must carry exactly those, and the checker must fire
    on each departure a writer is likely to make - with the problem it names,
    so a departure cannot pass on an unrelated one."""

    def test_every_fixture_conforms_to_the_template(self):
        for path in sorted(RENDERS.glob("review-report*.md")):
            self.assertEqual(shape_problems(path.read_text(encoding="utf-8")), [], path.name)

    def test_a_gap_report_conforms_and_its_table_is_checked(self):
        gap = as_gap_report(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(shape_problems(gap), [])
        renamed = gap.replace("| Wiring |", "| Integration |")
        self.assertIn("gap verdict lacks the dimension table", shape_problems(renamed))

    def test_the_template_renders_the_finding_contract_field_for_field(self):
        """The calibration owns the field set, the template how it renders; a
        field added to one and not the other is a finding nobody parses."""
        calibration = CALIBRATION.read_text(encoding="utf-8")
        contract = re.findall(r"^- `([a-z_]+)`",
                              calibration.split("Every finding carries:")[1].split("\n\n", 2)[1], re.M)
        spec = template_spec()
        rendered = [label.lower().replace(" ", "_") for label, _ in spec["fields"]]
        self.assertEqual(rendered, [field for field in contract if field != "severity"] + ["class", "routing"])
        self.assertIn("(CRITICAL|HIGH|MEDIUM|LOW)", spec["heading"].pattern,
                      "severity is rendered in the finding heading, its one place")

    def test_implement_fix_writes_the_remediation_bullet_the_template_shows(self):
        """`implement-fix` owns the Remediation Status mechanics and the template
        shows the result a parser joins by finding number; a drifted copy is
        bullets nobody can join."""
        annotation = REMEDIATION_BULLET.search(ANNOTATION.read_text(encoding="utf-8"))
        self.assertIsNotNone(annotation, "report-annotation.md states no numbered bullet shape")
        self.assertEqual(placeholders_blanked(annotation.group(1)),
                         placeholders_blanked(template_spec()["remediation"]))

    def test_each_departure_fires_with_its_problem(self):
        report = REPORT.read_text(encoding="utf-8")
        mixed = MIXED.read_text(encoding="utf-8")
        departures = [
            (report.replace("## Critic Coverage", "## Swap").replace(
                "## Verification Evidence", "## Critic Coverage").replace("## Swap", "## Verification Evidence"),
             "sections"),
            (report.replace("## Next Steps", "## Recommendations"), "sections"),
            (report.replace("## Critic Coverage", "## Trust-Boundary Map\n\n- a → b → c\n\n## Critic Coverage"),
             "sections"),
            (report.replace("- **Impact**: Sign-in outage", "Sign-in outage"), "finding 1 fields"),
            (report.replace("- **Confidence**: 100", "- **Confidence:** 100"), "finding 1 fields"),
            (report.replace("### Finding 1 - HIGH -", "### Finding 1 – HIGH –"), "finding heading"),
            (mixed.replace("- **Finding 1 - Seat count", "- **Seat count"), "remediation bullet"),
            (mixed.replace("transaction** - RESOLVED -", "transaction** – RESOLVED –"), "remediation bullet"),
            (report.replace("`Routing:` Fix - the bound", "`Routing:` Fixed - the bound"), "finding 1 Routing value"),
            (report.replace("- **Confidence**: 100", "- **Confidence**: high"), "finding 1 Confidence value"),
            (report.replace("### Finding 2 -", "### Finding 3 -"), "finding numbers"),
            (report.replace("### Finding 1 -", "#### Finding 1 -"), "finding heading at ####"),
            (report.replace("## Verdict\n\n**Readiness: Needs Fixes**", "## Verdict\n\n**Readiness: PASS**"),
             "verdict line not stated once"),
            (report.replace("## Executive Summary\n\n**Readiness: Needs Fixes**",
                            "## Executive Summary\n\n**Readiness: Ready**"),
             "Executive Summary does not open"),
            (mixed.replace("### Gap\n", ""), "no `### Gap` block"),
            (mixed.replace("### Security\n", "### Outcome\n"), "lens subheadings"),
        ]
        for text, problem in departures:
            with self.subTest(problem=problem):
                self.assertTrue(any(problem in found for found in shape_problems(text)),
                                shape_problems(text))


if __name__ == "__main__":
    unittest.main()
