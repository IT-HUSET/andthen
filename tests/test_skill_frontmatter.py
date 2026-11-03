#!/usr/bin/env python3
"""Every SKILL.md and Copilot `.agent.md` role-template frontmatter value parses
under strict YAML. Claude Code's
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
COPILOT_TEMPLATES = sorted((ROOT / "plugin" / "skills" / "init" / "templates" / "agents" / "copilot").glob("*.agent.md"))
COPILOT_AGENT_FIELDS = {"name", "description", "model", "reasoning-effort", "include-custom-instructions"}


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


def flow_sequence_problem(value):
    # The role templates' `model: [a, b]` is a flow sequence, so its items are
    # flow-context plain scalars: each one is checked, not the brackets.
    if not value.endswith("]"):
        return "flow sequence is not closed by ']'"
    inner = value[1:-1].strip()
    if not inner:
        return None
    for item in (part.strip() for part in inner.split(",")):
        if not item:
            return "has an empty flow-sequence item"
        if any(c in item for c in "[]{}"):
            return f"item {item!r} nests a flow collection"
        problem = plain_scalar_problem(item)
        if problem:
            return f"item {item!r} {problem}"
    return None


def value_problem(value):
    if value.startswith("["):
        return flow_sequence_problem(value)
    return plain_scalar_problem(value)


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

    def test_flow_sequences_are_checked_item_by_item(self):
        for good in ("[a, b]", "[claude-opus-5.5, gpt-6.1-sol]", "[]", "['a: b', c]"):
            self.assertIsNone(value_problem(good), good)
        for bad in ("[a, b", "[a, , b]", "[a: b, c]", "[*alias]", "[[a], b]"):
            self.assertTrue(value_problem(bad), bad)


class FrontmatterTest(unittest.TestCase):
    def assert_strict_yaml_frontmatter(self, paths):
        self.assertTrue(paths)
        for path in paths:
            label = path.relative_to(ROOT / "plugin")
            for number, line in frontmatter_lines(path):
                match = FIELD.match(line)
                self.assertTrue(match, f"{label}:{number} is not `key: value`")
                value = (match.group(2) or "").strip()
                problem = value and value_problem(value)
                self.assertFalse(problem, f"{label}:{number} {match.group(1)} {problem}; quote the value")

    def test_every_skill_frontmatter_value_is_valid_strict_yaml(self):
        self.assert_strict_yaml_frontmatter(sorted((ROOT / "plugin" / "skills").glob("*/SKILL.md")))

    def test_every_copilot_role_template_frontmatter_value_is_valid_strict_yaml(self):
        self.assert_strict_yaml_frontmatter(COPILOT_TEMPLATES)

    def test_copilot_role_templates_use_only_fields_copilot_reads(self):
        # Copilot drops an unknown `.agent.md` field with only a discovery warning,
        # so a misspelt key silently unpins the role: `reasoningEffort` (the
        # `.agent.yaml` spelling) was ignored where `reasoning-effort` applies.
        # The set is what Copilot CLI 1.0.105 discovery accepted without warnings.
        self.assertTrue(COPILOT_TEMPLATES)
        for path in COPILOT_TEMPLATES:
            keys = {FIELD.match(line).group(1) for _, line in frontmatter_lines(path)}
            self.assertLessEqual(keys, COPILOT_AGENT_FIELDS, path.name)


if __name__ == "__main__":
    unittest.main()
