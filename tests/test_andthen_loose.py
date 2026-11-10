#!/usr/bin/env python3
"""Tests for the loose-skill channel (scripts/andthen_loose.py), driven through
`andthen.py install --loose` over a copy of `scripts/`, `plugin/`, and the
manifest that makes the copy a tree (without it the script downloads one), so the
fault-injection tests can patch the module without touching the working tree."""

from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parent.parent


class LooseInstallCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.repo = root / "repo"
        for part in ("scripts", "plugin", ".claude-plugin"):
            shutil.copytree(REPO / part, self.repo / part,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        self.implementation = self.repo / "scripts" / "andthen_loose.py"
        # No Codex plugin and no real home: the run never reads this machine's.
        self.env = dict(os.environ, HOME=str(root / "home"), USERPROFILE=str(root / "home"),
                        CODEX_HOME=str(root / "codex"))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_installer(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.repo / "scripts" / "andthen.py"), "install", "--loose", *args],
            cwd=self.repo, env=self.env, text=True, capture_output=True, check=False)

    @staticmethod
    def snapshot(path: Path) -> dict[str, bytes]:
        return {str(item.relative_to(path)): item.read_bytes()
                for item in path.rglob("*") if item.is_file()}

    def test_a_stale_pycache_in_the_source_tree_does_not_reach_an_install(self) -> None:
        # Compiled Python is build output of whoever ran the source tree; the
        # copy is recursive, so nothing but an explicit strip keeps it out.
        cache = self.repo / "plugin" / "skills" / "tracker" / "__pycache__"
        cache.mkdir(parents=True, exist_ok=True)
        (cache / "helper.cpython-314.pyc").write_bytes(b"stale bytecode")
        destination = Path(self.temp_dir.name) / "installed"

        result = self.run_installer(
            "--skills-dir", str(destination), "--skills", "tracker")

        self.assertEqual(0, result.returncode, result.stderr)
        installed = destination / "andthen-tracker"
        self.assertTrue((installed / "SKILL.md").is_file())
        self.assertEqual([], sorted(installed.rglob("__pycache__")))
        self.assertEqual([], sorted(installed.rglob("*.pyc")))

    def test_a_json_canonical_is_inlined_verbatim_and_its_path_rewritten(self) -> None:
        # A model schema is read with its reference, so it travels like any other
        # canonical: copied byte-for-byte (a consumer validates against it) and
        # its SKILL.md path rewritten local, since nothing may leave the bundle.
        destination = Path(self.temp_dir.name) / "installed-plan"
        result = self.run_installer("--skills-dir", str(destination), "--skills", "plan")

        self.assertEqual(0, result.returncode, result.stderr)
        skill_dir = destination / "andthen-plan"
        body = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        installed = skill_dir / "references" / "plan.schema.json"
        self.assertEqual(installed.read_bytes(),
                         (self.repo / "plugin" / "references" / "plan.schema.json").read_bytes())
        self.assertIn("references/plan.schema.json", body)
        self.assertNotIn("../../references/", body)

    def test_post_install_scan_detects_a_missing_inlined_file(self) -> None:
        destination = Path(self.temp_dir.name) / "installed"
        args = ("--skills-dir", str(destination), "--skills", "clarify")
        first = self.run_installer(*args)
        self.assertEqual(0, first.returncode, first.stderr)
        skill = destination / "andthen-clarify"
        before = self.snapshot(skill)
        source = self.implementation.read_text(encoding="utf-8")
        source = source.replace(
            "shutil.copy(str(source), str(dst_refs / asset))",
            'None if asset == "design-tree.md"'
            " else shutil.copy(str(source), str(dst_refs / asset))",
            1,
        )
        self.implementation.write_text(source, encoding="utf-8")

        result = self.run_installer(*args)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "installed clarify is missing canonical asset references/design-tree.md",
            result.stderr,
        )
        self.assertEqual(self.snapshot(skill), before)
        self.assertEqual(list(destination.glob(".andthen-clarify.andthen-stage.*")), [])

    def test_partial_stage_copy_preserves_the_installed_skill_and_leaves_no_stage(self) -> None:
        destination = Path(self.temp_dir.name) / "installed"
        args = ("--skills-dir", str(destination), "--skills", "clarify")
        first = self.run_installer(*args)
        self.assertEqual(0, first.returncode, first.stderr)
        skill = destination / "andthen-clarify"
        before = self.snapshot(skill)
        source = self.implementation.read_text(encoding="utf-8")
        source = source.replace(
            "shutil.copytree(str(source), str(stage), symlinks=True, dirs_exist_ok=True)",
            'raise OSError("injected stage copy failure")',
            1,
        )
        self.implementation.write_text(source, encoding="utf-8")

        result = self.run_installer(*args)

        self.assertEqual(1, result.returncode)
        self.assertIn("failed to stage skill clarify", result.stderr)
        self.assertEqual(self.snapshot(skill), before)
        self.assertEqual(list(destination.glob(".andthen-clarify.andthen-stage.*")), [])

    def test_reinstall_replaces_owned_skill_and_removes_residue(self) -> None:
        destination = Path(self.temp_dir.name) / "installed"
        args = ("--skills-dir", str(destination), "--skills", "clarify")
        first = self.run_installer(*args)
        self.assertEqual(0, first.returncode, first.stderr)
        skill = destination / "andthen-clarify"

        fresh = self.snapshot(skill)
        (skill / "references" / "retired-0.x.md").write_text(
            "stale", encoding="utf-8")
        (skill / "scripts").mkdir(exist_ok=True)
        (skill / "scripts" / "retired.py").write_text("pass\n", encoding="utf-8")

        upgraded = self.run_installer(*args)

        self.assertEqual(0, upgraded.returncode, upgraded.stderr)
        self.assertEqual(fresh, self.snapshot(skill))

    def test_an_unknown_skill_fails_before_anything_is_written(self) -> None:
        destination = Path(self.temp_dir.name) / "installed"

        result = self.run_installer("--skills-dir", str(destination), "--skills", "no-such-skill")

        self.assertEqual(1, result.returncode)
        self.assertIn("unknown skill in --skills: no-such-skill", result.stderr)
        self.assertFalse(destination.exists())

    def test_dry_run_prints_the_plan_and_writes_nothing(self) -> None:
        destination = Path(self.temp_dir.name) / "installed"

        result = self.run_installer("--skills-dir", str(destination), "--skills", "clarify", "--dry-run")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("would install 1 skills into", result.stdout)
        self.assertFalse(destination.exists())

    def test_dry_run_with_a_relative_directory_creates_nothing(self) -> None:
        result = self.run_installer("--skills-dir", "preview/skills", "--skills", "clarify", "--dry-run")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("would install 1 skills into", result.stdout)
        self.assertIn(os.path.join("preview", "skills"), result.stdout)
        self.assertFalse((self.repo / "preview").exists())

    def test_a_relative_directory_is_created_and_reported_absolute_on_a_real_run(self) -> None:
        result = self.run_installer("--skills-dir", "made/skills", "--skills", "clarify")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue((self.repo / "made" / "skills" / "andthen-clarify" / "SKILL.md").is_file())

    # ---- Storage identity ------------------------------------------------
    # The installer rewrites every `andthen:` in markdown, while identifiers
    # matched on read must not move with the install namespace.

    def test_storage_identity_survives_the_namespace_rewrite(self) -> None:
        """A tracker issue found by its projection line, or a plan by its schema
        `$id`, must read the same from a plugin install and a loose install, or
        one teammate's publish misses the issues another created."""
        destination = Path(self.temp_dir.name) / "installed"
        result = self.run_installer("--skills-dir", str(destination), "--skills", "plan,tracker")

        self.assertEqual(0, result.returncode, result.stderr)
        source = (self.repo / "plugin/skills/tracker/SKILL.md").read_text(encoding="utf-8")
        installed = (destination / "andthen-tracker" / "SKILL.md").read_text(encoding="utf-8")
        for line in ("<!-- andthen-projection <source> -->",
                     "<!-- andthen-projection <id> <source> -->"):
            self.assertIn(line, source)
            self.assertIn(line, installed)
        # clarify and plan read the line too: a colon spelling anywhere becomes
        # `andthen-projection` in an install, a line no publish writes.
        spelled = re.compile(r"andthen:projection")
        self.assertTrue(spelled.search("below the hidden `andthen:projection` line"))
        offenders = [str(path.relative_to(self.repo))
                     for path in (self.repo / "plugin").rglob("*.md")
                     if spelled.search(path.read_text(encoding="utf-8"))]
        self.assertEqual([], offenders)
        self.assertIn('"$id": "andthen:plan.schema.json"',
                      (destination / "andthen-plan" / "references" / "plan.schema.json")
                      .read_text(encoding="utf-8"))

    # ---- Cross-skill read-sets --------------------------------------------
    # No skill file reaches into another skill's directory: a skill that needs
    # another skill's rubric dispatches a subagent that invokes that skill, so
    # an installed bundle carries only its own canonicals, rewritten local.

    def test_a_skill_bundle_names_no_other_skills_files(self) -> None:
        destination = Path(self.temp_dir.name) / "installed"
        result = self.run_installer(
            "--skills-dir", str(destination), "--skills", "exec-plan,review,now-what")
        self.assertEqual(0, result.returncode, result.stderr)
        skill_dir = destination / "andthen-exec-plan"
        procedure = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("../../references/", procedure)
        self.assertNotIn("andthen-review/references/", procedure)
        self.assertNotIn("review/SKILL.md", procedure)
        # Canonical peers were inlined into the bundle and rewritten local.
        references = skill_dir / "references"
        for peer in ("fis-contract.md", "verification-evidence.md"):
            self.assertTrue((references / peer).is_file())
            self.assertNotIn("../../references/",
                             (references / peer).read_text(encoding="utf-8"))
        router = destination / "andthen-now-what"
        self.assertIn("(references/plan-schema.md)",
                      (router / "SKILL.md").read_text(encoding="utf-8"))
        shipping = (router / "references" / "plan-schema.md").read_text(encoding="utf-8")
        self.assertIn("**Shipping.**", shipping)
        self.assertIn("no load-bearing check failing", shipping)


if __name__ == "__main__":
    unittest.main()
