#!/usr/bin/env python3
"""The `andthen:skill-review` bundle ships as text, so its contract is proved
the way a gate over shipped text is: the shape the bundle must keep (files,
frontmatter, the target and flags the hint and body agree on, canonicals
declared to the installer, no sigils or URLs) and the rubric's named lenses –
the four prose failure modes by name, in order, after the conflict audit.

Both directions, per the prompt-contract idiom: each checker fires on a
synthetic bundle that breaks the rule and stays silent on the shipped one."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "plugin" / "skills" / "skill-review"
INSTALLER = ROOT / "scripts" / "install-skills.py"

LENSES = ("Duplication", "Sediment", "Sprawl", "No-op")
CANONICAL_REF = re.compile(r"\.\./\.\./references/([A-Za-z0-9._-]+\.md)")
FLAG = re.compile(r"--[a-z][a-z-]*")
# The widened target: a skill bundle or a single prompt-like file. The hint is
# the only target contract a user reads before invoking, so the body cannot
# accept a narrower or wider one.
TARGET = "prompt-like file"
# Codex shares one budget across every installed description (8,000 chars when
# the window is unknown); one skill stays well under its share.
DESCRIPTION_CAP = 400


def frontmatter(text):
    """`key: value` pairs between the leading `---` fences."""
    head = text.split("---", 2)[1]
    return dict(line.split(":", 1) for line in head.strip().splitlines() if ":" in line)


def flag_mismatch(hint, body):
    """Flags the hint names that the body never mentions, and the reverse."""
    return set(FLAG.findall(hint)) ^ set(FLAG.findall(body))


def target_mismatch(hint, body):
    """True when only one of the hint and the body names the target kind."""
    return (TARGET in hint) != (TARGET in body)


def lens_defects(rubric):
    """Lenses missing or out of order, or a conflict audit that does not come first."""
    positions = [rubric.find(f"**{lens}**") for lens in LENSES]
    defects = [lens for lens, at in zip(LENSES, positions) if at < 0]
    found = [at for at in positions if at >= 0]
    if found != sorted(found):
        defects.append("order")
    audit = rubric.find("## Conflict audit")
    if audit < 0 or (found and audit > min(found)):
        defects.append("conflict-audit-first")
    return defects


def installer_list(name):
    match = re.search(rf'^{name}="([^"]*)"', INSTALLER.read_text(encoding="utf-8"), re.M)
    return set(match.group(1).split()) if match else set()


class BundleShapeTest(unittest.TestCase):
    def setUp(self):
        self.skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.meta = frontmatter(self.skill)

    def test_files_present(self):
        for rel in ("SKILL.md", "references/skill-craft-rubric.md", "agents/openai.yaml"):
            self.assertTrue((SKILL / rel).is_file(), rel)

    def test_description_short(self):
        self.assertLessEqual(len(self.meta["description"].strip()), DESCRIPTION_CAP)

    def test_hint_and_body_agree_on_flags(self):
        self.assertEqual(flag_mismatch(self.meta["argument-hint"], self.skill), set())
        self.assertEqual(flag_mismatch("[--fix] [--quiet]", "with `--fix` only"), {"--quiet"})

    def test_hint_and_body_agree_on_target(self):
        self.assertIn(TARGET, self.meta["argument-hint"])
        self.assertFalse(target_mismatch(self.meta["argument-hint"], self.skill))
        self.assertTrue(target_mismatch("<a prompt-like file>", "is one skill bundle"))

    def test_no_sigils_or_urls(self):
        for path in SKILL.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"/andthen:|\$andthen|https?://", path.name)

    def test_canonicals_declared_and_present(self):
        used = set(CANONICAL_REF.findall(self.skill))
        self.assertEqual(used, installer_list("_skill_assets_skill_review"))
        for asset in used:
            self.assertTrue((ROOT / "plugin" / "references" / asset).is_file(), asset)


class RubricLensesTest(unittest.TestCase):
    def test_shipped_rubric_clean(self):
        rubric = (SKILL / "references" / "skill-craft-rubric.md").read_text(encoding="utf-8")
        self.assertEqual(lens_defects(rubric), [])

    def test_missing_lens_fires(self):
        rubric = "## Conflict audit\n- **Duplication**\n- **Sediment**\n- **No-op**\n"
        self.assertEqual(lens_defects(rubric), ["Sprawl"])

    def test_reordered_lens_fires(self):
        rubric = "## Conflict audit\n- **Sediment**\n- **Duplication**\n- **Sprawl**\n- **No-op**\n"
        self.assertEqual(lens_defects(rubric), ["order"])

    def test_late_conflict_audit_fires(self):
        rubric = "- **Duplication**\n- **Sediment**\n- **Sprawl**\n- **No-op**\n## Conflict audit\n"
        self.assertEqual(lens_defects(rubric), ["conflict-audit-first"])


if __name__ == "__main__":
    unittest.main()
