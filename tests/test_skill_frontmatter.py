#!/usr/bin/env python3
"""Every SKILL.md frontmatter value parses under strict YAML. Claude Code's
lenient parser accepts an unquoted `: ` inside a plain scalar; Copilot CLI's
rejects it and drops the skill ("failed to parse YAML frontmatter"), which is
how `clarify` went missing there. Stdlib has no YAML parser, so this checks the
plain-scalar rules the frontmatter can break, not the whole grammar."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIELD = re.compile(r"^([A-Za-z][\w-]*):(?: (.*))?$")
# A plain scalar may not start with an indicator character, nor contain ": " or " #".
INDICATOR_START = tuple("-?:,[]{}#&*!|>'\"%@`")


def plain_scalar_problem(value):
    if value[0] in "'\"":
        return None  # quoted; its own closing quote is the parser's concern
    if value.startswith(INDICATOR_START):
        return f"starts with indicator {value[0]!r}"
    if ": " in value or value.endswith(":"):
        return "contains ': '"
    if " #" in value:
        return "contains ' #' (starts a comment)"
    return None


def frontmatter_lines(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    end = lines.index("---", 1)
    return enumerate(lines[1:end], 2)


class PlainScalarRuleTest(unittest.TestCase):
    def test_values_a_strict_parser_rejects_are_flagged(self):
        for bad in ("Ideation: gaps", "ends with:", "text #comment", "*alias", "@at", "`tick`"):
            self.assertTrue(plain_scalar_problem(bad), bad)

    def test_quoted_and_plain_values_pass(self):
        for good in ('"Ideation: gaps"', "'a: b'", "plain text, with commas – and dashes", "a#b"):
            self.assertIsNone(plain_scalar_problem(good), good)


class SkillFrontmatterTest(unittest.TestCase):
    def test_every_skill_frontmatter_value_is_valid_strict_yaml(self):
        skills = sorted((ROOT / "plugin" / "skills").glob("*/SKILL.md"))
        self.assertTrue(skills)
        for path in skills:
            for number, line in frontmatter_lines(path):
                match = FIELD.match(line)
                self.assertTrue(match, f"{path.parent.name}:{number} is not `key: value`")
                value = (match.group(2) or "").strip()
                problem = value and plain_scalar_problem(value)
                self.assertFalse(
                    problem,
                    f"{path.parent.name}/SKILL.md:{number} {match.group(1)} {problem}; quote the value",
                )


if __name__ == "__main__":
    unittest.main()
