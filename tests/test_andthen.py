#!/usr/bin/env python3
"""Tests for scripts/andthen.py: the plugin install, role-agent and rules
placement, Codex trust, the download bootstrap, and the exit code that proves a run.

The host CLIs are stubbed at the one seam the script has (`_run`, `_which`), so
no test touches a real install: every home (`HOME`, `CLAUDE_CONFIG_DIR`,
`CODEX_HOME`, `COPILOT_HOME`) is a temp dir, and the stub emulates what each host
writes. Files are real: the script's own reads and writes run against temp trees."""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import ssl
import subprocess
import sys
import tarfile
import tempfile
import unittest
import urllib.error
from unittest import mock

try:
    import tomllib
except ImportError:  # Python 3.9-3.10: the script runs there, the suite's TOML checks do not
    tomllib = None

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import andthen  # noqa: E402

SCRIPT = ROOT / "scripts" / "andthen.py"
TEMPLATES = ROOT / "plugin" / "skills" / "init" / "templates"
RULES = (TEMPLATES / "guidelines" / "CRITICAL-RULES-AND-GUARDRAILS.md").read_text(encoding="utf-8")
MARKETPLACE = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
VERSION = MARKETPLACE["plugins"][0]["version"]
HEADING = "# Critical Rules and Guardrails"
INSTRUCTION_FILE = {"claude": "CLAUDE.md", "codex": "AGENTS.md", "copilot": "copilot-instructions.md"}
ROLE_DIR = {"claude": "claude", "codex": "codex", "copilot": "copilot"}


def role_templates(host: str) -> dict:
    return {p.name: p.read_bytes() for p in sorted((TEMPLATES / "agents" / ROLE_DIR[host]).iterdir())}


def garbage_write(path, data) -> None:
    """A `_write` whose result never reads back as what was asked for."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(b"garbage\n")


class AndthenCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.home = {key: self.root / key for key in ("claude", "codex", "copilot")}
        env = {"HOME": str(self.root / "home"), "USERPROFILE": str(self.root / "home"),
               "CLAUDE_CONFIG_DIR": str(self.home["claude"]), "CODEX_HOME": str(self.home["codex"]),
               "COPILOT_HOME": str(self.home["copilot"])}
        patcher = mock.patch.dict(os.environ, env)
        patcher.start()
        self.addCleanup(patcher.stop)
        os.environ.pop("CLAUDE_CODE_PLUGIN_SEED_DIR", None)
        self.on_path = {"claude", "codex", "copilot"}
        self.commands: list[list[str]] = []
        self.claude_install_path = self.home["claude"] / "plugins" / "cache" / "andthen" / "andthen" / VERSION
        self.tamper = False
        self.recorded_version = VERSION  # what Claude Code writes into installed_plugins.json
        self.skill_list_failures = ""  # extra `copilot skill list` output, one failing path per line
        for target, replacement in (("_which", self.fake_which), ("_run", self.fake_run)):
            patcher = mock.patch.object(andthen, target, replacement)
            patcher.start()
            self.addCleanup(patcher.stop)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    # ---- the stubbed hosts ------------------------------------------------

    def fake_which(self, cli: str):
        return "/stub/" + cli if cli in self.on_path else None

    def copy_plugin(self, destination: Path) -> None:
        shutil.rmtree(destination, ignore_errors=True)  # a reinstall replaces the copy
        shutil.copytree(ROOT / "plugin", destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        if self.tamper:
            (destination / "stale.txt").write_text("not in the source", encoding="utf-8")

    def fake_run(self, cmd, cwd=None):
        self.commands.append(list(cmd))
        cli, rest, out = cmd[0], cmd[1:], ""
        if cli == "claude" and rest[:2] == ["plugin", "install"]:
            self.copy_plugin(self.claude_install_path)
            record = {"version": 2, "plugins": {"andthen@andthen": [
                {"scope": "user", "installPath": str(self.claude_install_path),
                 "version": self.recorded_version}]}}
            (self.home["claude"] / "plugins").mkdir(parents=True, exist_ok=True)
            (self.home["claude"] / "plugins" / "installed_plugins.json").write_text(
                json.dumps(record), encoding="utf-8")
        elif cli == "codex" and rest[:2] == ["plugin", "add"]:
            self.copy_plugin(self.home["codex"] / "plugins" / "cache" / "andthen" / "andthen" / VERSION)
        elif cli == "copilot" and rest[:3] == ["plugin", "list", "--json"]:
            out = json.dumps([{"name": "andthen", "marketplace": "andthen", "version": VERSION}])
        elif cli == "copilot" and rest[:2] == ["skill", "list"]:
            out = "Plugin skills:\n" + self.skill_list_failures
        return subprocess.CompletedProcess(cmd, 0, out, "")

    # ---- helpers ------------------------------------------------------------

    def run_install(self, *args: str):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = andthen.main(["install", *args])
            except SystemExit as exit_:
                code = exit_.code
        return code, out.getvalue(), err.getvalue()

    def instruction_file(self, host: str) -> Path:
        return self.home[host] / INSTRUCTION_FILE[host]

    def host_commands(self, cli: str) -> list:
        return [c for c in self.commands if c[0] == cli]

    @staticmethod
    def config_level(config: Path, path: Path):
        return tomllib.loads(config.read_text(encoding="utf-8"))["projects"][str(path)].get("trust_level")


class PluginChannelTest(AndthenCase):
    def test_local_install_runs_the_sequence_on_each_host_and_verifies_it(self) -> None:
        code, out, _ = self.run_install()

        self.assertEqual(0, code, out)
        self.assertEqual(["plugin", "uninstall", "andthen@andthen"], self.host_commands("claude")[0][1:])
        self.assertEqual(["plugin", "marketplace", "remove", "andthen"], self.host_commands("claude")[1][1:])
        self.assertEqual(["plugin", "marketplace", "add", str(ROOT)], self.host_commands("claude")[2][1:])
        self.assertEqual(["plugin", "install", "andthen@andthen", "-y"], self.host_commands("claude")[3][1:])
        self.assertEqual(["plugin", "add", "andthen@andthen"], self.host_commands("codex")[3][1:])
        self.assertEqual(["plugin", "marketplace", "add", str(ROOT)], self.host_commands("copilot")[2][1:])
        self.assertEqual(3, out.count(f"  v andthen {VERSION}"))

    def test_an_installed_copy_that_differs_from_the_source_fails_the_run(self) -> None:
        self.tamper = True

        code, out, _ = self.run_install("--codex-only")

        self.assertEqual(1, code)
        self.assertIn("x andthen: installed copy differs from source", out)

    def test_claude_code_is_located_by_installed_plugins_json_not_a_computed_path(self) -> None:
        self.claude_install_path = self.root / "somewhere" / "else"

        code, out, _ = self.run_install("--claude-only")

        self.assertEqual(0, code, out)
        self.assertIn(f"v andthen {VERSION}", out)

    def test_a_host_that_recorded_no_install_fails_the_run(self) -> None:
        with mock.patch.object(andthen, "claude_install_record", side_effect=KeyError("andthen@andthen")):
            code, out, _ = self.run_install("--claude-only")

        self.assertEqual(1, code)
        self.assertIn("cannot find where Claude Code installed it", out)

    def test_a_skill_copilot_fails_to_parse_fails_the_run(self) -> None:
        broken = ROOT / "plugin" / "skills" / "plan" / "SKILL.md"
        self.skill_list_failures = f"  {broken}: invalid frontmatter\n"

        code, out, _ = self.run_install("--copilot-only")

        self.assertEqual(1, code)
        self.assertIn("x andthen: the host reports problems with the install", out)
        self.assertIn(f"{broken}: invalid frontmatter", out)

    def test_copilot_is_checked_by_its_own_listing_not_by_comparing_the_tree_with_itself(self) -> None:
        # Copilot loads the marketplace live, so its "installed copy" is the source tree.
        with mock.patch.object(andthen, "differences", wraps=andthen.differences) as diff, \
                mock.patch.object(andthen, "installed_version", wraps=andthen.installed_version) as read:
            code, out, _ = self.run_install("--copilot-only")
            self.assertEqual(0, code, out)
            self.assertEqual([], diff.call_args_list)
            self.assertEqual([], read.call_args_list)
            self.assertIn(f"v andthen {VERSION}", out)

            code, out, _ = self.run_install("--codex-only")  # the copies are still compared
            self.assertEqual(0, code, out)
            self.assertGreater(diff.call_count, 0)  # it recurses into subdirectories
            self.assertEqual(1, read.call_count)

    def test_a_version_the_host_recorded_that_differs_fails_the_run(self) -> None:
        self.recorded_version = "0.0.1"

        code, out, _ = self.run_install("--claude-only")

        self.assertEqual(1, code)
        self.assertIn("(host recorded 0.0.1)", out)

    def test_a_seeded_marketplace_is_verified_not_reinstalled(self) -> None:
        seed = self.root / "seed"
        (seed / "marketplaces" / "andthen").mkdir(parents=True)
        (seed / "known_marketplaces.json").write_text(json.dumps({"andthen": {}}), encoding="utf-8")
        self.copy_plugin(seed / "cache" / "andthen" / "andthen" / VERSION)
        os.environ["CLAUDE_CODE_PLUGIN_SEED_DIR"] = str(seed)

        code, out, _ = self.run_install("--claude-only")

        self.assertEqual(0, code, out)
        self.assertEqual([], self.host_commands("claude"))
        self.assertIn(f"v andthen {VERSION}", out)

    def test_a_seed_without_this_version_fails_without_touching_it(self) -> None:
        seed = self.root / "seed"
        (seed / "marketplaces" / "andthen").mkdir(parents=True)
        os.environ["CLAUDE_CODE_PLUGIN_SEED_DIR"] = str(seed)

        code, out, _ = self.run_install("--claude-only")

        self.assertEqual(1, code)
        self.assertEqual([], self.host_commands("claude"))
        self.assertIn(f"expected {VERSION}", out)

    def test_a_seed_that_lacks_the_marketplace_is_ignored(self) -> None:
        seed = self.root / "seed"
        seed.mkdir()
        os.environ["CLAUDE_CODE_PLUGIN_SEED_DIR"] = str(seed)

        code, out, _ = self.run_install("--claude-only")

        self.assertEqual(0, code, out)
        self.assertEqual(4, len(self.host_commands("claude")))

    def test_dry_run_runs_nothing(self) -> None:
        code, out, _ = self.run_install("--dry-run", "--roles", "--rules")

        self.assertEqual(0, code, out)
        self.assertEqual([], self.commands)
        self.assertIn("would run: claude plugin marketplace add", out)
        self.assertFalse(self.home["claude"].exists())

    def test_no_host_on_path_fails(self) -> None:
        self.on_path.clear()

        code, out, _ = self.run_install()

        self.assertEqual(1, code)
        self.assertIn("no host CLI", out)

    def test_a_missing_host_that_was_asked_for_by_name_fails(self) -> None:
        self.on_path.discard("codex")

        code, out, _ = self.run_install("--codex-only")

        self.assertEqual(1, code)
        self.assertIn("`codex` not on PATH", out)

    def test_a_missing_host_among_the_defaults_is_skipped(self) -> None:
        self.on_path.discard("codex")

        code, out, _ = self.run_install()

        self.assertEqual(0, code, out)
        self.assertEqual([], self.host_commands("codex"))
        self.assertIn("`codex` not on PATH - skipped", out)


class RolePlacementTest(AndthenCase):
    def test_missing_role_files_are_written_for_every_host_on_path(self) -> None:
        code, out, _ = self.run_install("--roles")

        self.assertEqual(0, code, out)
        for host in ("claude", "codex", "copilot"):
            placed = {p.name: p.read_bytes() for p in (self.home[host] / "agents").iterdir()}
            self.assertEqual(role_templates(host), placed)

    def test_an_identical_role_file_is_accepted_untouched(self) -> None:
        self.run_install("--roles")
        target = self.home["claude"] / "agents" / "oracle.md"
        before = target.stat().st_mtime_ns

        code, out, _ = self.run_install("--roles")

        self.assertEqual(0, code, out)
        self.assertEqual(before, target.stat().st_mtime_ns)

    def test_a_line_ending_or_trailing_whitespace_difference_is_not_a_difference(self) -> None:
        self.run_install("--roles")
        target = self.home["claude"] / "agents" / "oracle.md"
        crlf = target.read_bytes().replace(b"\n", b"  \r\n")
        target.write_bytes(crlf)

        code, out, _ = self.run_install("--roles")

        self.assertEqual(0, code, out)
        self.assertEqual(crlf, target.read_bytes())

    def test_a_different_role_file_is_refused_with_its_path_and_the_init_offer(self) -> None:
        self.run_install("--roles")
        target = self.home["codex"] / "agents" / "worker.toml"
        target.write_text("# my own worker\n", encoding="utf-8")

        code, out, _ = self.run_install("--roles")

        self.assertEqual(1, code)
        self.assertEqual("# my own worker\n", target.read_text(encoding="utf-8"))
        self.assertIn(f"x {target}", out)
        self.assertIn("andthen:init", out)
        self.assertIn("--replace-roles", out)

    def test_replace_roles_overwrites_a_different_role_file(self) -> None:
        self.run_install("--roles")
        target = self.home["copilot"] / "agents" / "reviewer.agent.md"
        target.write_text("edited\n", encoding="utf-8")

        code, out, _ = self.run_install("--replace-roles")

        self.assertEqual(0, code, out)
        self.assertEqual(role_templates("copilot")["reviewer.agent.md"], target.read_bytes())

    def test_only_the_named_host_gets_roles(self) -> None:
        code, out, _ = self.run_install("--claude-only", "--roles")

        self.assertEqual(0, code, out)
        self.assertTrue((self.home["claude"] / "agents").is_dir())
        self.assertFalse((self.home["codex"] / "agents").exists())

    def test_a_host_off_path_gets_nothing(self) -> None:
        self.on_path.discard("copilot")

        code, out, _ = self.run_install("--roles")

        self.assertEqual(0, code, out)
        self.assertFalse((self.home["copilot"] / "agents").exists())

    def test_only_regular_files_with_the_hosts_role_suffix_are_placed(self) -> None:
        tree = self.root / "tree"
        templates = tree / andthen.TEMPLATES / "agents" / "claude"
        (templates / "archive.md").mkdir(parents=True)
        (templates / "archive.md" / "old.md").write_text("nested\n", encoding="utf-8")
        (templates / ".DS_Store").write_bytes(b"\x00junk")
        (templates / "notes.txt").write_text("not a role\n", encoding="utf-8")
        (templates / "oracle.md").write_bytes(role_templates("claude")["oracle.md"])
        report = andthen.Report()

        with mock.patch.object(andthen, "REPO_ROOT", tree), contextlib.redirect_stdout(io.StringIO()):
            andthen.place_roles(andthen.HOST["claude"], False, False, report)

        self.assertFalse(report.failed)
        self.assertEqual(["oracle.md"], sorted(p.name for p in (self.home["claude"] / "agents").iterdir()))

    def test_a_role_write_that_does_not_read_back_is_undone(self) -> None:
        agents = self.home["claude"] / "agents"
        agents.mkdir(parents=True)
        mine = b"# my own worker\n"
        (agents / "worker.md").write_bytes(mine)

        with mock.patch.object(andthen, "_write", garbage_write):
            code, out, _ = self.run_install("--claude-only", "--replace-roles")

        self.assertEqual(1, code)
        self.assertIn("differs from its template after the write", out)
        self.assertEqual(mine, (agents / "worker.md").read_bytes())  # replaced, so put back
        self.assertEqual(["worker.md"], sorted(p.name for p in agents.iterdir()))  # the new ones removed


class RulesPlacementTest(AndthenCase):
    def test_a_missing_instruction_file_is_written_as_the_block(self) -> None:
        code, out, _ = self.run_install("--rules")

        self.assertEqual(0, code, out)
        for host in ("claude", "codex", "copilot"):
            self.assertEqual(RULES, self.instruction_file(host).read_text(encoding="utf-8"))

    def test_a_file_without_the_block_gets_it_appended_after_one_blank_line(self) -> None:
        mine = "# My notes\n\nKeep me exactly.\n"
        self.instruction_file("codex").parent.mkdir(parents=True)
        self.instruction_file("codex").write_text(mine, encoding="utf-8")

        code, out, _ = self.run_install("--rules")

        self.assertEqual(0, code, out)
        self.assertEqual(mine + "\n" + RULES, self.instruction_file("codex").read_text(encoding="utf-8"))

    def test_an_identical_block_among_the_users_own_content_is_accepted_untouched(self) -> None:
        mine = "# My notes\n\nabove\n\n" + RULES + "\n# Elsewhere\n\nbelow\n"
        self.instruction_file("claude").parent.mkdir(parents=True)
        self.instruction_file("claude").write_text(mine, encoding="utf-8")

        code, out, _ = self.run_install("--claude-only", "--rules")

        self.assertEqual(0, code, out)
        self.assertEqual(mine, self.instruction_file("claude").read_text(encoding="utf-8"))

    def test_the_block_ends_at_the_next_heading_that_is_not_the_guidelines_own(self) -> None:
        # A foreign `##` heading right after the block is the user's, so it must
        # not count against the block; one of the guideline's own must.
        mine = RULES + "\n## My addendum\n\nlocal rule\n"
        self.instruction_file("claude").parent.mkdir(parents=True)
        self.instruction_file("claude").write_text(mine, encoding="utf-8")

        code, out, _ = self.run_install("--claude-only", "--rules")

        self.assertEqual(0, code, out)

    def test_a_different_block_is_refused_and_never_overwritten(self) -> None:
        mine = "# Mine\n\n" + RULES.replace("Respect Chesterton's Fence", "Ignore Chesterton's Fence") + "\nafter\n"
        self.instruction_file("copilot").parent.mkdir(parents=True)
        self.instruction_file("copilot").write_text(mine, encoding="utf-8")

        code, out, _ = self.run_install("--rules")

        self.assertEqual(1, code)
        self.assertEqual(mine, self.instruction_file("copilot").read_text(encoding="utf-8"))
        self.assertIn(f"x {self.instruction_file('copilot')}", out)
        self.assertIn("andthen:init", out)
        # The other hosts are independent: their files were still placed.
        self.assertEqual(RULES, self.instruction_file("claude").read_text(encoding="utf-8"))

    def test_a_byte_order_mark_before_the_heading_does_not_hide_the_block(self) -> None:
        bom_block = b"\xef\xbb\xbf" + RULES.encode("utf-8")
        self.instruction_file("claude").parent.mkdir(parents=True)
        self.instruction_file("claude").write_bytes(bom_block)

        code, out, _ = self.run_install("--claude-only", "--rules")

        self.assertEqual(0, code, out)
        self.assertEqual(bom_block, self.instruction_file("claude").read_bytes())

    def test_appending_to_a_file_with_a_byte_order_mark_keeps_it(self) -> None:
        self.instruction_file("claude").parent.mkdir(parents=True)
        self.instruction_file("claude").write_bytes(b"\xef\xbb\xbf# Mine\n")

        code, out, _ = self.run_install("--claude-only", "--rules")

        self.assertEqual(0, code, out)
        placed = self.instruction_file("claude").read_bytes()
        self.assertTrue(placed.startswith(b"\xef\xbb\xbf# Mine\n\n"))
        self.assertEqual(1, placed.count(HEADING.encode("utf-8") + b"\n"))

    def test_the_heading_text_at_another_level_is_refused_not_duplicated(self) -> None:
        for level in ("##", "###"):
            with self.subTest(level=level):
                mine = f"# Mine\n\n{level} Critical Rules and Guardrails\n\nmy own take\n"
                self.instruction_file("claude").parent.mkdir(parents=True, exist_ok=True)
                self.instruction_file("claude").write_text(mine, encoding="utf-8")

                code, out, _ = self.run_install("--claude-only", "--rules")

                self.assertEqual(1, code)
                self.assertEqual(mine, self.instruction_file("claude").read_text(encoding="utf-8"))
                self.assertIn(f"x {self.instruction_file('claude')}", out)
                self.assertIn("andthen:init", out)

    def test_a_rules_write_that_does_not_read_back_is_undone(self) -> None:
        mine = b"# Mine\n\nkeep\n"
        self.instruction_file("claude").parent.mkdir(parents=True)
        self.instruction_file("claude").write_bytes(mine)

        with mock.patch.object(andthen, "_write", garbage_write):
            code, out, _ = self.run_install("--claude-only", "--rules")
            self.assertEqual(1, code)
            self.assertIn("differs from its template after the write", out)
            self.assertEqual(mine, self.instruction_file("claude").read_bytes())

            self.instruction_file("claude").unlink()
            code, _, _ = self.run_install("--claude-only", "--rules")
            self.assertEqual(1, code)
            self.assertFalse(self.instruction_file("claude").exists())  # a new file is removed again

    def test_a_crlf_only_difference_is_accepted_untouched(self) -> None:
        crlf = RULES.replace("\n", "\r\n").encode("utf-8")
        self.instruction_file("claude").parent.mkdir(parents=True)
        self.instruction_file("claude").write_bytes(crlf)

        code, out, _ = self.run_install("--claude-only", "--rules")

        self.assertEqual(0, code, out)
        self.assertEqual(crlf, self.instruction_file("claude").read_bytes())

    def test_appending_to_a_crlf_file_keeps_its_line_endings(self) -> None:
        self.instruction_file("claude").parent.mkdir(parents=True)
        self.instruction_file("claude").write_bytes(b"# Mine\r\n\r\nkeep\r\n")

        code, out, _ = self.run_install("--claude-only", "--rules")

        self.assertEqual(0, code, out)
        text = self.instruction_file("claude").read_bytes()
        self.assertTrue(text.startswith(b"# Mine\r\n\r\nkeep\r\n\r\n"))
        self.assertNotIn(b"\n", text.replace(b"\r\n", b""))


class PlacementGuardTest(AndthenCase):
    def test_a_write_that_does_not_read_back_as_the_template_fails_the_run(self) -> None:
        def corrupt(path, data):
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_bytes(data + b"junk\n")

        with mock.patch.object(andthen, "_write", corrupt):
            code, out, _ = self.run_install("--claude-only", "--roles", "--rules")

        self.assertEqual(1, code)
        self.assertIn("differs from its template after the write", out)

    def test_dry_run_reports_a_refusal_and_writes_nothing(self) -> None:
        self.instruction_file("claude").parent.mkdir(parents=True)
        mine = "# Critical Rules and Guardrails\n\nmine\n"
        self.instruction_file("claude").write_text(mine, encoding="utf-8")

        code, out, _ = self.run_install("--dry-run", "--roles", "--rules")

        self.assertEqual(1, code)
        self.assertIn("would write", out)
        self.assertEqual(mine, self.instruction_file("claude").read_text(encoding="utf-8"))
        self.assertFalse((self.home["claude"] / "agents").exists())
        self.assertFalse(self.instruction_file("codex").exists())


class TrustCase(AndthenCase):
    def setUp(self) -> None:
        super().setUp()
        self.project = self.root / "project"
        self.project.mkdir()
        self.resolved = self.project.resolve()
        self.escaped = str(self.resolved).replace("\\", "\\\\")
        self.header = f'[projects."{self.escaped}"]'
        self.config = self.home["codex"] / "config.toml"


class TrustEdgeTest(TrustCase):
    """The file-shape cases, asserted on bytes so they run on Python 3.9 too."""

    def test_a_header_on_the_last_line_without_a_newline_gets_its_key_on_the_next_line(self) -> None:
        self.home["codex"].mkdir(parents=True)
        self.config.write_bytes(self.header.encode("utf-8"))

        code, out, _ = self.run_install("--codex-only", "--trust", str(self.project))

        self.assertEqual(0, code, out)
        self.assertEqual(f'{self.header}\ntrust_level = "trusted"\n', self.config.read_text(encoding="utf-8"))

    def test_a_crlf_file_ending_in_a_header_without_a_newline_keeps_its_line_endings(self) -> None:
        self.home["codex"].mkdir(parents=True)
        self.config.write_bytes(f'model = "x"\r\n{self.header}'.encode("utf-8"))

        code, out, _ = self.run_install("--codex-only", "--trust", str(self.project))

        self.assertEqual(0, code, out)
        self.assertEqual(f'model = "x"\r\n{self.header}\r\ntrust_level = "trusted"\r\n'.encode("utf-8"),
                         self.config.read_bytes())

    def test_a_write_that_does_not_read_back_as_trusted_is_undone(self) -> None:
        self.home["codex"].mkdir(parents=True)
        mine = b'model = "x"\n'
        self.config.write_bytes(mine)

        with mock.patch.object(andthen, "_write", garbage_write):
            code, out, _ = self.run_install("--codex-only", "--trust", str(self.project))
            self.assertEqual(1, code)
            self.assertIn("is not trusted after the write", out)
            self.assertEqual(mine, self.config.read_bytes())

            self.config.unlink()
            code, _, _ = self.run_install("--codex-only", "--trust", str(self.project))
            self.assertEqual(1, code)
            self.assertFalse(self.config.exists())  # a new file is removed again

    def test_a_path_spelled_in_a_form_the_script_does_not_edit_is_refused_not_duplicated(self) -> None:
        spellings = {
            "inline table": f'[projects]\n"{self.escaped}" = {{ trust_level = "untrusted" }}\n',
            "dotted key": f'projects."{self.escaped}".trust_level = "untrusted"\n',
            "padded header": f'[ projects."{self.escaped}" ]\ntrust_level = "untrusted"\n',
            "literal key": f"[projects]\n'{self.resolved}' = {{ trust_level = \"untrusted\" }}\n",
            "dotted key in the projects table": f'[projects]\n"{self.escaped}".trust_level = "untrusted"\n',
            "projects as an inline table": f'projects = {{ "{self.escaped}" = {{ trust_level = "untrusted" }} }}\n',
        }
        self.home["codex"].mkdir(parents=True)
        for label, mine in spellings.items():
            with self.subTest(label):
                if label == "literal key" and "'" in str(self.resolved):
                    continue
                self.config.write_text(mine, encoding="utf-8")

                code, out, _ = self.run_install("--codex-only", "--trust", str(self.project))

                self.assertEqual(1, code)
                self.assertEqual(mine, self.config.read_text(encoding="utf-8"))
                self.assertIn(str(self.config), out)
                self.assertIn("by hand", out)

    def test_a_path_that_is_only_a_value_is_not_a_spelling_the_script_refuses(self) -> None:
        # The same run writes `source = "<checkout>"` under [marketplaces.andthen], and an MCP
        # server may run in the project: neither names the project as a key.
        values = {
            "marketplace source": f'[marketplaces.andthen]\nsource = "{self.escaped}"\n',
            "mcp cwd": f'[mcp_servers.x]\ncwd = "{self.escaped}"\n',
            "array element": f'writable_roots = ["{self.escaped}", "/tmp"]\n',
            "literal-string value": f"[marketplaces.andthen]\nsource = '{self.resolved}'\n",
        }
        self.home["codex"].mkdir(parents=True)
        for label, mine in values.items():
            with self.subTest(label):
                if label == "literal-string value" and "'" in str(self.resolved):
                    continue
                self.config.write_text(mine, encoding="utf-8")

                code, out, _ = self.run_install("--codex-only", "--trust", str(self.project))

                self.assertEqual(0, code, out)
                self.assertEqual(f'{mine}\n{self.header}\ntrust_level = "trusted"\n',
                                 self.config.read_text(encoding="utf-8"))

    def test_an_already_trusted_path_stays_accepted_beside_a_value_that_names_it(self) -> None:
        self.home["codex"].mkdir(parents=True)
        mine = f'{self.header}\ntrust_level = "trusted"\n\n[marketplaces.andthen]\nsource = "{self.escaped}"\n'
        self.config.write_text(mine, encoding="utf-8")

        code, out, _ = self.run_install("--codex-only", "--trust", str(self.project))

        self.assertEqual(0, code, out)
        self.assertIn("already trusted", out)
        self.assertEqual(mine, self.config.read_text(encoding="utf-8"))


@unittest.skipIf(tomllib is None, "reading the written TOML back needs tomllib (Python 3.11+)")
class TrustTest(TrustCase):

    def test_an_absent_path_is_appended_as_a_two_line_table_and_the_file_created(self) -> None:
        code, out, _ = self.run_install("--codex-only", "--trust", str(self.project))

        self.assertEqual(0, code, out)
        self.assertEqual("trusted", self.config_level(self.config, self.resolved))

    def test_the_path_is_resolved_and_the_rest_of_the_file_kept(self) -> None:
        link = self.root / "link"
        try:
            link.symlink_to(self.project, target_is_directory=True)
        except OSError:
            self.skipTest("symlinks need privileges on this host")
        self.home["codex"].mkdir(parents=True, exist_ok=True)
        mine = 'model = "x"\n\n[projects."/elsewhere"]\ntrust_level = "untrusted"\n'
        self.config.write_text(mine, encoding="utf-8")

        code, out, _ = self.run_install("--codex-only", "--trust", str(link))

        self.assertEqual(0, code, out)
        text = self.config.read_text(encoding="utf-8")
        self.assertTrue(text.startswith(mine))
        self.assertEqual("trusted", self.config_level(self.config, self.resolved))
        self.assertEqual("untrusted", self.config_level(self.config, Path("/elsewhere")))

    def test_an_already_trusted_path_is_accepted_untouched(self) -> None:
        self.home["codex"].mkdir(parents=True, exist_ok=True)
        # A literal-string header is how some Codex versions write a Windows path.
        header = f"[projects.'{self.resolved}']" if os.sep == "\\" else f'[projects."{self.resolved}"]'
        mine = f'{header}\ntrust_level = "trusted"\n\n[tui]\nx = 1\n'
        self.config.write_text(mine, encoding="utf-8")

        code, out, _ = self.run_install("--codex-only", "--trust", str(self.project))

        self.assertEqual(0, code, out)
        self.assertEqual(mine, self.config.read_text(encoding="utf-8"))

    def test_a_path_with_another_level_is_refused_and_left_alone(self) -> None:
        self.home["codex"].mkdir(parents=True, exist_ok=True)
        mine = f'[projects."{self.resolved}"]\ntrust_level = "untrusted"\n'
        if os.sep == "\\":
            mine = mine.replace("\\", "\\\\")
        self.config.write_text(mine, encoding="utf-8")

        code, out, _ = self.run_install("--codex-only", "--trust", str(self.project))

        self.assertEqual(1, code)
        self.assertEqual(mine, self.config.read_text(encoding="utf-8"))
        self.assertIn("untrusted", out)

    def test_a_table_without_a_trust_level_gets_the_key_under_its_header(self) -> None:
        self.home["codex"].mkdir(parents=True, exist_ok=True)
        escaped = str(self.resolved).replace("\\", "\\\\")
        self.config.write_text(f'[projects."{escaped}"]\nenabled = true\n', encoding="utf-8")

        code, out, _ = self.run_install("--codex-only", "--trust", str(self.project))

        self.assertEqual(0, code, out)
        table = tomllib.loads(self.config.read_text(encoding="utf-8"))["projects"][str(self.resolved)]
        self.assertEqual({"trust_level": "trusted", "enabled": True}, table)

    def test_trust_without_codex_in_scope_fails(self) -> None:
        self.on_path.discard("codex")

        code, out, _ = self.run_install("--trust", str(self.project))

        self.assertEqual(1, code)
        self.assertIn("--trust", out)
        self.assertFalse(self.config.exists())


class LooseDuplicateTest(AndthenCase):
    def write_codex_plugin_table(self) -> None:
        self.home["codex"].mkdir(parents=True, exist_ok=True)
        (self.home["codex"] / "config.toml").write_text(
            '[plugins."andthen@andthen"]\nenabled = true\n', encoding="utf-8")

    def test_loose_without_a_named_directory_refuses_beside_the_codex_plugin(self) -> None:
        self.write_codex_plugin_table()

        code, out, err = self.run_install("--loose", "--skills", "tracker")

        self.assertEqual(1, code)
        self.assertIn("twice", out + err)
        self.assertFalse((self.root / "home" / ".agents").exists())

    def test_loose_into_a_named_directory_proceeds_beside_the_codex_plugin(self) -> None:
        self.write_codex_plugin_table()
        destination = self.root / "skills"

        code, out, err = self.run_install("--loose", "--skills-dir", str(destination), "--skills", "tracker")

        self.assertEqual(0, code, out + err)
        self.assertTrue((destination / "andthen-tracker" / "SKILL.md").is_file())

    def test_loose_defaults_to_the_agents_skills_directory_without_the_codex_plugin(self) -> None:
        code, out, err = self.run_install("--loose", "--skills", "tracker")

        self.assertEqual(0, code, out + err)
        self.assertTrue((self.root / "home" / ".agents" / "skills" / "andthen-tracker" / "SKILL.md").is_file())
        self.assertEqual([], self.commands)

    def test_a_codex_config_naming_only_another_plugin_does_not_refuse(self) -> None:
        self.home["codex"].mkdir(parents=True, exist_ok=True)
        (self.home["codex"] / "config.toml").write_text('[plugins."other@andthen"]\nenabled = true\n', encoding="utf-8")

        code, out, err = self.run_install("--loose", "--skills", "tracker")

        self.assertEqual(0, code, out + err)

    def test_loose_can_be_combined_with_placement(self) -> None:
        destination = self.root / "skills"

        code, out, err = self.run_install("--loose", "--skills-dir", str(destination),
                                          "--skills", "tracker", "--claude-only", "--rules")

        self.assertEqual(0, code, out + err)
        self.assertEqual(RULES, self.instruction_file("claude").read_text(encoding="utf-8"))
        self.assertEqual([], self.commands)


class OptionCheckTest(AndthenCase):
    def test_an_empty_option_value_is_rejected_not_defaulted(self) -> None:
        # `--skills-dir ""` once fell back to ~/.agents/skills and `--skills ""` installed everything.
        for args in (["--loose", "--skills-dir", ""], ["--loose", "--skills", ""],
                     ["--skills-dir", ""], ["--skills", ""], ["--trust", ""]):
            with self.subTest(args=args):
                code, _, err = self.run_install(*args)

                self.assertEqual(2, code)
                self.assertIn(args[-2], err)
                self.assertIn("empty", err)
        self.assertFalse((self.root / "home").exists())
        self.assertEqual([], self.commands)

    def test_a_host_flag_with_loose_and_nothing_that_uses_hosts_is_rejected(self) -> None:
        for flag in ("--claude-only", "--codex-only", "--copilot-only"):
            with self.subTest(flag):
                code, _, err = self.run_install("--loose", flag, "--skills-dir", str(self.root / "skills"))

                self.assertEqual(2, code)
                self.assertIn(flag, err)
                self.assertIn("--roles", err)
        self.assertFalse((self.root / "skills").exists())

    def test_a_host_flag_with_loose_is_accepted_when_placement_uses_it(self) -> None:
        for extra in ("--roles", "--rules", "--replace-roles"):
            with self.subTest(extra):
                code, out, err = self.run_install("--loose", "--claude-only", "--skills-dir",
                                                  str(self.root / "skills"), "--skills", "tracker", extra)

                self.assertEqual(0, code, out + err)


class BootstrapTest(unittest.TestCase):
    """`bootstrap` with a fake `fetch` (a tarball built from a temp tree), a temp
    data home, and the child process mocked: no network, no real home."""

    CODELOAD = "https://codeload.github.com/IT-HUSET/andthen/tar.gz/"

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.home = self.root / "share" / "andthen"
        self.urls: list = []
        self.child_code = 0
        patcher = mock.patch.object(andthen.subprocess, "call", side_effect=self.fake_call)
        self.child = patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def fake_call(self, cmd):
        return self.child_code

    def tarball(self, top: str, files: dict) -> bytes:
        """GitHub's shape: one top-level directory named after the ref."""
        tree = self.root / "src" / top
        shutil.rmtree(tree.parent, ignore_errors=True)
        for name, text in files.items():
            (tree / name).parent.mkdir(parents=True, exist_ok=True)
            (tree / name).write_text(text, encoding="utf-8")
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
            tar.add(tree, arcname=top)
        return buffer.getvalue()

    def tree_files(self, version: str = "9.9.9", **extra: str) -> dict:
        manifest = {"name": "andthen", "plugins": [{"name": "other", "version": "0.0.1"},
                                                  {"name": "andthen", "version": version}]}
        return {".claude-plugin/marketplace.json": json.dumps(manifest),
                "scripts/andthen.py": "# the downloaded script\n", **extra}

    def bootstrap(self, args: list, data: bytes):
        def fetch(url: str) -> bytes:
            self.urls.append(url)
            return data
        return self.bootstrap_with(args, fetch)

    def bootstrap_with(self, args: list, fetch):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = andthen.bootstrap(args, fetch=fetch, home=self.home)
        return code, out.getvalue() + err.getvalue()

    def test_it_runs_the_downloaded_trees_own_script_without_ref_and_with_the_other_args(self) -> None:
        for ref_args, top in ((["--ref", "v1.0.1"], "andthen-1.0.1"), (["--ref=v1.0.1"], "andthen-1.0.1")):
            with self.subTest(ref_args=ref_args):
                code, out = self.bootstrap(["install", *ref_args, "--roles", "--rules"],
                                           self.tarball(top, self.tree_files()))

                self.assertEqual(0, code, out)
                self.assertEqual(self.CODELOAD + "v1.0.1", self.urls[-1])
                self.child.assert_called_with([sys.executable, str(self.home / "9.9.9" / "scripts" / "andthen.py"),
                                               "install", "--roles", "--rules"])

    def test_the_default_ref_is_main_and_the_top_level_name_is_never_computed(self) -> None:
        code, out = self.bootstrap(["install"], self.tarball("andthen-main", self.tree_files()))

        self.assertEqual(0, code, out)
        self.assertEqual([self.CODELOAD + "main"], self.urls)
        self.child.assert_called_once_with([sys.executable, str(self.home / "9.9.9" / "scripts" / "andthen.py"),
                                            "install"])

    def test_a_rerun_replaces_the_versions_copy_rather_than_overlaying_it(self) -> None:
        self.bootstrap(["install"], self.tarball("andthen-main", self.tree_files(**{"only-in-old.txt": "x"})))
        self.assertTrue((self.home / "9.9.9" / "only-in-old.txt").is_file())

        code, out = self.bootstrap(["install"], self.tarball("andthen-main", self.tree_files()))

        self.assertEqual(0, code, out)
        self.assertFalse((self.home / "9.9.9" / "only-in-old.txt").exists())
        self.assertEqual("# the downloaded script\n",
                         (self.home / "9.9.9" / "scripts" / "andthen.py").read_text(encoding="utf-8"))
        self.assertEqual(["9.9.9"], [p.name for p in self.home.iterdir()])  # no temp dir left behind

    def test_an_old_copy_that_cannot_be_removed_fails_clearly_without_running_the_child(self) -> None:
        # Windows refuses to delete a file a running host holds open.
        self.bootstrap(["install"], self.tarball("andthen-main", self.tree_files()))
        self.child.reset_mock()

        with mock.patch.object(andthen.Path, "rename", side_effect=PermissionError("in use")):
            code, out = self.bootstrap(["install"], self.tarball("andthen-main", self.tree_files()))

        self.assertEqual(1, code, out)
        self.assertIn(f"Cannot replace {self.home / '9.9.9'}", out)
        self.assertIn("close Claude Code, Codex, and Copilot CLI, then run again", out)
        self.child.assert_not_called()

    def test_another_version_gets_its_own_directory(self) -> None:
        self.bootstrap(["install"], self.tarball("andthen-main", self.tree_files("1.0.0")))
        self.bootstrap(["install"], self.tarball("andthen-main", self.tree_files("1.1.0")))

        self.assertEqual(["1.0.0", "1.1.0"], sorted(p.name for p in self.home.iterdir()))

    def test_a_tree_without_the_manifest_fails_clearly_and_leaves_the_home_alone(self) -> None:
        old = self.home / "9.9.9" / "keep.txt"
        old.parent.mkdir(parents=True)
        old.write_text("old copy", encoding="utf-8")

        code, out = self.bootstrap(["install", "--ref", "v0.1.0"], self.tarball("andthen-0.1.0", {"README.md": "x"}))

        self.assertEqual(1, code)
        self.assertIn("v0.1.0 is not an AndThen tree", out)
        self.child.assert_not_called()
        self.assertEqual(["9.9.9"], [p.name for p in self.home.iterdir()])
        self.assertEqual("old copy", old.read_text(encoding="utf-8"))

    def test_a_tree_that_predates_the_script_fails_clearly_and_leaves_the_home_alone(self) -> None:
        old = self.home / "9.9.9" / "keep.txt"
        old.parent.mkdir(parents=True)
        old.write_text("old copy", encoding="utf-8")
        files = self.tree_files()
        del files["scripts/andthen.py"]

        code, out = self.bootstrap(["install", "--ref", "v0.40.4"], self.tarball("andthen-0.40.4", files))

        self.assertEqual(1, code)
        self.assertIn("v0.40.4 predates scripts/andthen.py; follow that tag's own README", out)
        self.child.assert_not_called()
        self.assertEqual(["9.9.9"], [p.name for p in self.home.iterdir()])
        self.assertEqual("old copy", old.read_text(encoding="utf-8"))

    def test_the_childs_exit_code_is_the_scripts_exit_code(self) -> None:
        self.child_code = 7

        code, out = self.bootstrap(["install"], self.tarball("andthen-main", self.tree_files()))

        self.assertEqual(7, code, out)

    def test_a_failed_download_names_the_url_and_leaves_no_home(self) -> None:
        def refuse(url: str) -> bytes:
            raise urllib.error.URLError("no route to host")

        code, out = self.bootstrap_with(["install", "--ref", "nope"], refuse)

        self.assertEqual(1, code)
        self.assertIn("Cannot download " + self.CODELOAD + "nope", out)
        self.assertNotIn("SSL_CERT_FILE", out)
        self.assertFalse(self.home.exists())

    def test_a_certificate_error_adds_the_ca_bundle_hint(self) -> None:
        def untrusted(url: str) -> bytes:
            raise urllib.error.URLError(ssl.SSLCertVerificationError("self-signed certificate in chain"))

        code, out = self.bootstrap_with(["install"], untrusted)

        self.assertEqual(1, code)
        self.assertIn("SSL_CERT_FILE", out)


class RoutingTest(unittest.TestCase):
    """`main` hands over to `bootstrap` when `--ref` is given or no tree is around."""

    def test_ref_inside_a_checkout_downloads_that_version(self) -> None:
        for argv in (["install", "--ref", "v1.0.1", "--dry-run"], ["install", "--ref=v1.0.1"]):
            with self.subTest(argv=argv), mock.patch.object(andthen, "bootstrap", return_value=3) as boot:
                self.assertEqual(3, andthen.main(argv))
                boot.assert_called_once_with(argv)

    def test_no_tree_around_downloads_one(self) -> None:
        with tempfile.TemporaryDirectory() as bare, mock.patch.object(andthen, "REPO_ROOT", Path(bare)), \
                mock.patch.object(andthen, "bootstrap", return_value=4) as boot:
            self.assertEqual(4, andthen.main(["install", "--roles"]))
            boot.assert_called_once_with(["install", "--roles"])


class CommandLineTest(unittest.TestCase):
    def test_the_entry_point_has_a_shebang_and_the_executable_bit(self) -> None:
        self.assertEqual("#!/usr/bin/env python3", SCRIPT.read_text(encoding="utf-8").splitlines()[0])
        if os.name == "posix":
            self.assertTrue(os.access(SCRIPT, os.X_OK))
            self.assertTrue(os.access(ROOT / "scripts" / "validate-plugin.py", os.X_OK))

    def test_help_names_the_flags(self) -> None:
        result = subprocess.run([sys.executable, str(SCRIPT), "install", "--help"],
                                text=True, capture_output=True, check=False)

        self.assertEqual(0, result.returncode)
        for flag in ("--loose", "--roles", "--rules", "--replace-roles", "--trust", "--ref", "--skills-dir"):
            self.assertIn(flag, result.stdout)
        for gone in ("--display-brand", "--prefix", "--claude-user", "--claude-skills-dir", "stable"):
            self.assertNotIn(gone, result.stdout)
        self.assertIn("usage: andthen.py install", result.stdout)

    def test_ref_is_a_documented_option_of_install(self) -> None:
        # `main` takes --ref before the parser runs, so the parser must still list it.
        result = subprocess.run([sys.executable, str(SCRIPT), "install", "--help"],
                                text=True, capture_output=True, check=False)

        usage = " ".join(result.stdout.split("\n\n")[0].split())
        self.assertIn("[--ref REF]", usage)
        self.assertRegex(result.stdout, r"(?m)^\s+--ref REF\s+\S")

    def test_the_data_home_is_documented_as_the_code_resolves_it(self) -> None:
        wanted = "${XDG_DATA_HOME:-~/.local/share}/andthen/<version>"
        result = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                                text=True, capture_output=True, check=False)

        self.assertIn(wanted, " ".join(result.stdout.split()))
        self.assertIn(wanted, andthen.__doc__)

    @staticmethod
    def run_piped(tmp: str, cwd: Path, *args: str):
        """The script piped through `python -`, so `__file__` is `<stdin>`. A dead proxy
        makes any download fail offline, deterministically."""
        env = {k: v for k, v in os.environ.items() if "proxy" not in k.lower()}
        env.update(HOME=str(Path(tmp) / "home"), USERPROFILE=str(Path(tmp) / "home"),
                   XDG_DATA_HOME=str(Path(tmp) / "share"), https_proxy="http://127.0.0.1:9")
        return subprocess.run([sys.executable, "-", *args], input=SCRIPT.read_text(encoding="utf-8"),
                              cwd=cwd, env=env, text=True, capture_output=True, check=False)

    def test_piped_through_stdin_with_no_tree_it_reaches_the_bootstrap(self) -> None:
        # A module-level import of a sibling file would raise before anything ran.
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / "work"
            work.mkdir()

            result = self.run_piped(tmp, work, "install", "--roles", "--rules")

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("Cannot download https://codeload.github.com/IT-HUSET/andthen/tar.gz/main", result.stdout)
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse((Path(tmp) / "share").exists())

    def test_piped_from_a_subdirectory_of_a_tree_it_still_downloads_instead_of_using_that_tree(self) -> None:
        # `<stdin>` resolves against the cwd, so its "parent's parent" is the cwd's parent:
        # run from `docs/` of any checkout, that checkout used to be taken for the script's own tree.
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp) / "tree"
            (tree / ".claude-plugin").mkdir(parents=True)
            shutil.copy(ROOT / ".claude-plugin" / "marketplace.json", tree / ".claude-plugin")
            (tree / "docs").mkdir()

            result = self.run_piped(tmp, tree / "docs", "install", "--dry-run", "--claude-only")

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("Cannot download", result.stdout)
            self.assertNotIn("Marketplace:", result.stdout)


if __name__ == "__main__":
    unittest.main()
