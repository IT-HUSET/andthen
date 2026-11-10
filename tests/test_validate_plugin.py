#!/usr/bin/env python3
"""Fault-injection tests for scripts/validate-plugin.py: each content check fires
on the text that would break it, and the live tree passes. Every test runs the
validator over a copy of `scripts/` and `plugin/`, so an injected fault never
touches the working tree."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parent.parent


class ValidatePluginCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name) / "repo"
        for part in ("scripts", "plugin"):
            shutil.copytree(REPO / part, self.repo / part,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        self.implementation = self.repo / "scripts" / "andthen_loose.py"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_validator(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.repo / "scripts" / "validate-plugin.py")],
            cwd=self.repo, text=True, capture_output=True, check=False)

    def append(self, relative_path: str, text: str) -> None:
        path = self.repo / relative_path
        with path.open("a", encoding="utf-8") as handle:
            handle.write(text)

    def test_the_live_tree_passes(self) -> None:
        result = self.run_validator()

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Validation passed", result.stdout)

    def test_undeclared_direct_core_reference_fails_validation(self) -> None:
        self.append(
            "plugin/skills/now-what/SKILL.md",
            "\n[calibration](../../references/review-calibration.md)\n",
        )

        result = self.run_validator()

        self.assertEqual(1, result.returncode)
        self.assertIn("now-what references canonical asset review-calibration.md", result.stderr)
        self.assertIn("_skill_assets_now_what", result.stderr)

    def test_canonical_mentioning_canonical_is_not_a_transitive_load(self) -> None:
        # A canonical naming another canonical by bare backticked filename is
        # prose, not a load: the closure is direct-only, so a skill that
        # consumes the first is not required to also declare the mentioned one.
        self.append(
            "plugin/references/plan-schema.md",
            "\nDecision trade-offs: `design-tree.md`.\n",
        )

        result = self.run_validator()

        self.assertEqual(0, result.returncode)
        self.assertIn("Validation passed", result.stdout)

    def test_bare_mention_of_an_unloaded_canonical_fails_validation(self) -> None:
        # A backticked filename loads nothing, so a SKILL.md that names a
        # canonical that way and never loads it points the model at a file it
        # will not have read.
        self.append(
            "plugin/skills/now-what/SKILL.md",
            "\nSee `review-calibration.md`.\n",
        )

        result = self.run_validator()

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "now-what mentions canonical asset review-calibration.md", result.stderr)

    def test_bare_mention_beside_its_own_load_passes_validation(self) -> None:
        # Shorthand for a canonical the skill already loads by path is legal:
        # the load site is in the same file.
        self.append(
            "plugin/skills/review/SKILL.md",
            "\nCalibrate with `review-calibration.md`.\n",
        )

        result = self.run_validator()

        self.assertEqual(0, result.returncode, result.stderr)

    def test_bare_mention_of_a_non_canonical_filename_passes_validation(self) -> None:
        # The check owns canonical loads only; naming an artifact file is prose.
        self.append(
            "plugin/skills/now-what/SKILL.md",
            "\nWrite `prd.md`.\n",
        )

        result = self.run_validator()

        self.assertEqual(0, result.returncode, result.stderr)

    def test_undeclared_reference_in_a_standalone_skill_fails_validation(self) -> None:
        # The closure check owns every skill in the one plugin dir, pipeline and
        # standalone alike - the tools that arrived with the merge included.
        self.append(
            "plugin/skills/tracker/SKILL.md",
            "\n[mutability](../../references/fis-mutability.md)\n",
        )

        result = self.run_validator()

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "tracker references canonical asset fis-mutability.md",
            result.stderr,
        )
        self.assertIn("_skill_assets_tracker", result.stderr)

    def test_a_role_body_that_differs_between_hosts_fails_validation(self) -> None:
        # One role, two host formats: only the frontmatter differs by contract,
        # so a body edit applied to one host is a fork under one role name.
        codex = self.repo / "plugin/skills/init/templates/agents/codex/worker.toml"
        body = codex.read_text(encoding="utf-8")
        codex.write_text(body.replace("You are the Worker:", "You are a worker:", 1),
                         encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(1, result.returncode)
        self.assertIn("role worker body differs", result.stderr)

    def test_a_copilot_role_body_that_differs_fails_validation(self) -> None:
        copilot = self.repo / "plugin/skills/init/templates/agents/copilot/worker.agent.md"
        body = copilot.read_text(encoding="utf-8")
        copilot.write_text(body.replace("You are the Worker:", "You are a worker:", 1),
                           encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(1, result.returncode)
        self.assertIn("role worker body differs between its Claude and Copilot", result.stderr)

    def test_a_role_without_a_copilot_template_fails_validation(self) -> None:
        (self.repo / "plugin/skills/init/templates/agents/copilot/worker.agent.md").unlink()

        result = self.run_validator()

        self.assertEqual(1, result.returncode)
        self.assertIn("role worker has no Copilot template", result.stderr)

    def test_stale_skill_declaration_fails_validation(self) -> None:
        source = self.implementation.read_text(encoding="utf-8")
        source = source.replace(
            '_skill_assets_clarify="design-tree.md',
            '_skill_assets_clarify="review-calibration.md design-tree.md',
            1,
        )
        self.implementation.write_text(source, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(1, result.returncode)
        self.assertIn("clarify declares stale canonical asset review-calibration.md", result.stderr)

    def test_a_missing_canonical_asset_fails_validation(self) -> None:
        (self.repo / "plugin/references/design-tree.md").unlink()

        result = self.run_validator()

        self.assertEqual(1, result.returncode)
        self.assertIn("design-tree.md not found; cannot inline for consuming skills", result.stderr)

    def test_a_reference_linking_another_reference_fails_validation(self) -> None:
        # One level deep: a chain SKILL.md -> A.md -> B.md hides B behind a
        # partial read of A, so the skill body owns each load site's read-set.
        self.append(
            "plugin/skills/review/references/lens-code.md",
            "\nCalibrate with [`review-calibration.md`]"
            "(../../references/review-calibration.md).\n",
        )

        result = self.run_validator()

        self.assertEqual(1, result.returncode)
        # The validator prints the absolute path; Windows renders it with backslashes.
        self.assertIn("plugin/skills/review/references/lens-code.md:",
                      result.stderr.replace("\\", "/"))
        self.assertIn("paths to no other file", result.stderr)

    def test_a_template_linking_a_reference_fails_validation(self) -> None:
        # The depth check covers every non-SKILL.md file in a skill, not only
        # files under references/ - a template chaining to a reference hides it
        # the same way a reference chaining to another reference would.
        self.append(
            "plugin/skills/init/templates/CLAUDE.template.md",
            "\nCalibrate with [`review-calibration.md`]"
            "(../references/review-calibration.md).\n",
        )

        result = self.run_validator()

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "plugin/skills/init/templates/CLAUDE.template.md:",
            result.stderr.replace("\\", "/"),
        )
        self.assertIn("paths to no other file", result.stderr)

    def test_a_bare_filename_in_reference_prose_passes_validation(self) -> None:
        # A filename in prose is a mention, not a load; only links and paths
        # build the chain the rule forbids.
        self.append(
            "plugin/skills/review/references/lens-code.md",
            "\nCalibrate with `review-calibration.md`, which the review skill loads.\n",
        )

        result = self.run_validator()

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertNotIn("plugin/skills/review/references/lens-code.md:", result.stderr)

    def test_a_sigil_reference_fails_validation(self) -> None:
        self.append("plugin/skills/review/SKILL.md", "\nRun /andthen:plan next.\n")

        result = self.run_validator()

        self.assertEqual(1, result.returncode)
        self.assertIn("uses a sigil skill reference", result.stderr)

    # ---- Path shape -------------------------------------------------------
    # Every path in shipped skill content resolves from the skill root both
    # hosts announce, so a canonical is the one thing a skill reaches above it.

    def test_a_retired_path_token_fails_validation(self) -> None:
        # Claude Code substituted ${CLAUDE_PLUGIN_ROOT}/${CLAUDE_SKILL_DIR} and
        # Codex never did, so a token left in skill text ships a literal path.
        self.append(
            "plugin/skills/review/SKILL.md",
            "\n[calibration](${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md)\n",
        )

        result = self.run_validator()

        self.assertEqual(1, result.returncode)
        self.assertIn("names a retired CLAUDE_PLUGIN_ROOT/CLAUDE_SKILL_DIR token",
                      result.stderr)

    def test_a_dotdot_path_outside_the_allowed_shape_fails_validation(self) -> None:
        # An installed bundle carries its own files only: any climb but the
        # canonical one points where the install put nothing.
        self.append(
            "plugin/skills/now-what/SKILL.md",
            "\n[lens](../review/references/lens-code.md)\n",
        )

        result = self.run_validator()

        self.assertEqual(1, result.returncode)
        self.assertIn("climbs out of the skill root", result.stderr)
        self.assertIn("../review/references/lens-code.md", result.stderr)

    def test_the_canonical_relative_path_passes_validation(self) -> None:
        self.append(
            "plugin/skills/review/SKILL.md",
            "\n[calibration](../../references/review-calibration.md)\n",
        )

        result = self.run_validator()

        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
