#!/usr/bin/env python3
"""Regression tests for install-time canonical dependency validation."""

from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parent.parent


class InstallSkillsValidationCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name) / "repo"
        shutil.copytree(
            REPO,
            self.repo,
            ignore=shutil.ignore_patterns(".git", ".agent_temp", "__pycache__", "*.pyc"),
        )
        # The .sh entry point is a shim; install-skills.py is what the
        # fault-injection tests below patch.
        self.installer = self.repo / "scripts" / "install-skills.sh"
        self.implementation = self.repo / "scripts" / "install-skills.py"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_installer(self, *args: str) -> subprocess.CompletedProcess[str]:
        # shutil.which walks PATH; a bare "bash" lets CreateProcess find the
        # WSL stub in System32 first on Windows.
        bash = shutil.which("bash")
        self.assertIsNotNone(bash)
        return subprocess.run(
            [bash, str(self.installer), *args],
            cwd=self.repo,
            text=True,
            capture_output=True,
            check=False,
        )

    def append(self, relative_path: str, text: str) -> None:
        path = self.repo / relative_path
        with path.open("a", encoding="utf-8") as handle:
            handle.write(text)

    @staticmethod
    def snapshot(path: Path) -> dict[str, bytes]:
        return {str(item.relative_to(path)): item.read_bytes()
                for item in path.rglob("*") if item.is_file()}

    def test_undeclared_direct_core_reference_fails_validation(self) -> None:
        self.append(
            "plugin/skills/now-what/SKILL.md",
            "\n[calibration](../../references/review-calibration.md)\n",
        )

        result = self.run_installer("--validate-only")

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

        result = self.run_installer("--validate-only")

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

        result = self.run_installer("--validate-only")

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

        result = self.run_installer("--validate-only")

        self.assertEqual(0, result.returncode, result.stderr)

    def test_bare_mention_of_a_non_canonical_filename_passes_validation(self) -> None:
        # The check owns canonical loads only; naming an artifact file is prose.
        self.append(
            "plugin/skills/now-what/SKILL.md",
            "\nWrite `prd.md`.\n",
        )

        result = self.run_installer("--validate-only")

        self.assertEqual(0, result.returncode, result.stderr)

    def test_undeclared_reference_in_a_standalone_skill_fails_validation(self) -> None:
        # The closure check owns every skill in the one plugin dir, pipeline and
        # standalone alike - the tools that arrived with the merge included.
        self.append(
            "plugin/skills/tracker/SKILL.md",
            "\n[mutability](../../references/fis-mutability.md)\n",
        )

        result = self.run_installer("--validate-only")

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

        result = self.run_installer("--validate-only")

        self.assertEqual(1, result.returncode)
        self.assertIn("role worker body differs", result.stderr)

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

    def test_stale_skill_declaration_fails_validation(self) -> None:
        source = self.implementation.read_text(encoding="utf-8")
        source = source.replace(
            '_skill_assets_clarify="design-tree.md',
            '_skill_assets_clarify="review-calibration.md design-tree.md',
            1,
        )
        self.implementation.write_text(source, encoding="utf-8")

        result = self.run_installer("--validate-only")

        self.assertEqual(1, result.returncode)
        self.assertIn("clarify declares stale canonical asset review-calibration.md", result.stderr)

    def test_a_reference_linking_another_reference_fails_validation(self) -> None:
        # One level deep: a chain SKILL.md -> A.md -> B.md hides B behind a
        # partial read of A, so the skill body owns each load site's read-set.
        self.append(
            "plugin/skills/review/references/lens-code.md",
            "\nCalibrate with [`review-calibration.md`]"
            "(../../references/review-calibration.md).\n",
        )

        result = self.run_installer("--validate-only")

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

        result = self.run_installer("--validate-only")

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

        result = self.run_installer("--validate-only")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertNotIn("plugin/skills/review/references/lens-code.md:", result.stderr)

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

        result = self.run_installer("--validate-only")

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

        result = self.run_installer("--validate-only")

        self.assertEqual(1, result.returncode)
        self.assertIn("climbs out of the skill root", result.stderr)
        self.assertIn("../review/references/lens-code.md", result.stderr)

    def test_the_canonical_relative_path_passes_validation(self) -> None:
        self.append(
            "plugin/skills/review/SKILL.md",
            "\n[calibration](../../references/review-calibration.md)\n",
        )

        result = self.run_installer("--validate-only")

        self.assertEqual(0, result.returncode, result.stderr)

    def test_a_json_canonical_is_inlined_verbatim_and_its_path_rewritten(self) -> None:
        # A model schema is read with its reference, so it travels like any other
        # canonical: copied byte-for-byte (a consumer validates against it) and
        # its SKILL.md path rewritten local, since nothing may leave the bundle.
        cases = {
            "plan": ["plan.schema.json"],
        }
        for skill_name, schemas in cases.items():
            with self.subTest(skill=skill_name):
                destination = Path(self.temp_dir.name) / ("installed-%s" % skill_name)
                result = self.run_installer(
                    "--skills-dir", str(destination), "--skills", skill_name)

                self.assertEqual(0, result.returncode, result.stderr)
                skill_dir = destination / ("andthen-%s" % skill_name)
                body = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
                for schema in schemas:
                    installed = skill_dir / "references" / schema
                    self.assertEqual(
                        installed.read_bytes(),
                        (self.repo / "plugin" / "references" / schema).read_bytes())
                    self.assertIn("references/%s" % schema, body)
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

    # ---- Storage identity ------------------------------------------------
    # The installer rewrites every `andthen:` in markdown, while identifiers
    # matched on read must not move with the install prefix.

    def test_storage_identity_survives_a_renamed_install(self) -> None:
        """A tracker issue found by its projection line, or a plan by its schema
        `$id`, must read the same from a plugin install and a renamed loose
        install, or one teammate's publish misses the issues another created."""
        destination = Path(self.temp_dir.name) / "installed"
        result = self.run_installer("--skills-dir", str(destination),
                                    "--skills", "plan,tracker", "--prefix", "custom-")

        self.assertEqual(0, result.returncode, result.stderr)
        source = (self.repo / "plugin/skills/tracker/SKILL.md").read_text(encoding="utf-8")
        installed = (destination / "custom-tracker" / "SKILL.md").read_text(encoding="utf-8")
        for line in ("<!-- andthen-projection <source> -->",
                     "<!-- andthen-projection <id> <source> -->"):
            self.assertIn(line, source)
            self.assertIn(line, installed)
        # clarify and plan read the line too: a colon spelling anywhere becomes
        # `custom-projection` in a renamed install, a line no publish writes.
        spelled = re.compile(r"andthen:projection")
        self.assertTrue(spelled.search("below the hidden `andthen:projection` line"))
        offenders = [str(path.relative_to(self.repo))
                     for path in (self.repo / "plugin").rglob("*.md")
                     if spelled.search(path.read_text(encoding="utf-8"))]
        self.assertEqual([], offenders)
        self.assertIn('"$id": "andthen:plan.schema.json"',
                      (destination / "custom-plan" / "references" / "plan.schema.json")
                      .read_text(encoding="utf-8"))

    # ---- Cross-skill read-sets --------------------------------------------
    # No skill file reaches into another skill's directory: a skill that needs
    # another skill's rubric dispatches a subagent that invokes that skill, so
    # an installed bundle carries only its own canonicals, rewritten local.

    def test_a_skill_bundle_names_no_other_skills_files(self) -> None:
        for prefix, extra in (("andthen-", ()), ("custom-", ("--prefix", "custom-"))):
            with self.subTest(prefix=prefix):
                destination = Path(self.temp_dir.name) / ("installed-" + prefix)
                result = self.run_installer(
                    "--skills-dir", str(destination), "--skills", "exec-plan,review,now-what", *extra)
                self.assertEqual(0, result.returncode, result.stderr)
                skill_dir = destination / (prefix + "exec-plan")
                procedure = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
                self.assertNotIn("../../references/", procedure)
                self.assertNotIn("%sreview/references/" % prefix, procedure)
                self.assertNotIn("review/SKILL.md", procedure)
                # Canonical peers were inlined into the bundle and rewritten local.
                references = skill_dir / "references"
                for peer in ("fis-contract.md", "verification-evidence.md"):
                    self.assertTrue((references / peer).is_file())
                    self.assertNotIn("../../references/",
                                     (references / peer).read_text(encoding="utf-8"))
                router = destination / (prefix + "now-what")
                self.assertIn("(references/plan-schema.md)",
                              (router / "SKILL.md").read_text(encoding="utf-8"))
                shipping = (router / "references" / "plan-schema.md").read_text(encoding="utf-8")
                self.assertIn("**Shipping.**", shipping)
                self.assertIn("no load-bearing check failing", shipping)


if __name__ == "__main__":
    unittest.main()
