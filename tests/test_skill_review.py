#!/usr/bin/env python3
"""The project-level `skill-review` bundle is text, so its contract is proved
the way a gate over text is: the shape the bundle must keep (its home under
`.claude/skills/`, frontmatter, the target and flags the hint and body agree on,
canonicals read in place from `plugin/references/`, the Codex entry linking to
the one directory, no shipped file naming it, no sigils or URLs) and its one
rubric, the skill-authoring guidelines, resolving from the bundle and naming
the four prose failure modes in order, after the conflict audit.

Both directions, per the prompt-contract idiom: each checker fires on a
synthetic input that breaks the rule and stays silent on the real one."""
import os
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / ".claude" / "skills" / "skill-review"
SHARED = ROOT / "plugin" / "references"
# The Codex entry is a relative symlink to the Claude Code directory, never a
# copy, so the two hosts cannot drift (ADR-021).
CODEX_ENTRY = ROOT / ".agents" / "skills" / "skill-review"
CODEX_TARGET = "../../.claude/skills/skill-review"
# The bundle carries no rubric of its own: it reviews against the guidelines,
# so the craft has one home.
GUIDELINE = "../../../docs/SKILL-AUTHORING-GUIDELINES.md"

LENSES = ("Duplication", "Sediment", "Sprawl", "No-op")
CANONICALS = {"intent-and-rules-context.md", "lens-adversarial.md", "review-calibration.md"}
CANONICAL_PATH = re.compile(r"((?:\.\./)+[A-Za-z0-9./_-]*?references/[A-Za-z0-9._-]+\.md)")
FLAG = re.compile(r"--[a-z][a-z-]*")
# The widened target: a skill bundle or a single prompt-like file. The hint is
# the only target contract a user reads before invoking, so the body cannot
# accept a narrower or wider one.
TARGET = "prompt-like file"


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


def unresolved_canonicals(text, skill_dir):
    """Relative canonical paths that do not land on a file in `plugin/references/` –
    the bundle reads the shipped canonicals in place, so a path left in the plugin's
    `../../references/` form points at nothing from `.claude/skills/`."""
    shared = SHARED.resolve()
    return [
        rel for rel in CANONICAL_PATH.findall(text)
        if (skill_dir / rel).resolve().parent != shared or not (skill_dir / rel).is_file()
    ]


def naming_files(root, name="skill-review"):
    """Text files under `root` that name the project-level skill – text only, since
    an untracked `.DS_Store` records directory names."""
    return sorted(
        path.name for path in root.rglob("*")
        if path.is_file() and path.suffix in {".md", ".yaml", ".json", ".py"}
        and name in path.read_text(encoding="utf-8")
    )


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


class BundleShapeTest(unittest.TestCase):
    def setUp(self):
        self.skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.meta = frontmatter(self.skill)

    def test_files_present(self):
        for rel in ("SKILL.md", "references/fix.md", "agents/openai.yaml"):
            self.assertTrue((SKILL / rel).is_file(), rel)

    def test_rubric_is_the_guideline(self):
        self.assertIn(GUIDELINE, self.skill)
        self.assertTrue((SKILL / GUIDELINE).is_file(), GUIDELINE)

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

    def test_canonicals_resolve_under_plugin_references(self):
        named = {Path(rel).name for rel in CANONICAL_PATH.findall(self.skill)}
        self.assertEqual(named, CANONICALS)
        self.assertEqual(unresolved_canonicals(self.skill, SKILL), [])

    def test_a_plugin_relative_canonical_path_fires(self):
        stale = "`../../references/review-calibration.md`"
        self.assertEqual(unresolved_canonicals(stale, SKILL), ["../../references/review-calibration.md"])

    def test_codex_entry_links_to_the_bundle(self):
        if CODEX_ENTRY.is_symlink():
            target = os.readlink(CODEX_ENTRY)
        else:
            # A checkout without symlinks writes the link target as the file's text.
            self.assertTrue(CODEX_ENTRY.is_file(), CODEX_ENTRY)
            target = CODEX_ENTRY.read_text(encoding="utf-8").strip()
        self.assertEqual(Path(target).as_posix(), CODEX_TARGET)


class NotShippedTest(unittest.TestCase):
    """Only `plugin/` ships, so a shipped file naming a project-level skill dangles
    for every user."""

    def test_no_shipped_file_names_it(self):
        self.assertEqual(naming_files(ROOT / "plugin"), [])

    def test_a_shipped_mention_fires(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "README.md").write_text("see `skill-review`\n", encoding="utf-8")
            self.assertEqual(naming_files(Path(tmp)), ["README.md"])


class RubricLensesTest(unittest.TestCase):
    def test_guideline_clean(self):
        rubric = (SKILL / GUIDELINE).read_text(encoding="utf-8")
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
