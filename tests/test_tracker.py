#!/usr/bin/env python3
"""Pins the payloads `andthen:tracker` projects a plan.json into.

The live path sends these payloads through the Issue Tracker document's
operation table, so what is asserted here is what the tracker receives. Runs
against the fixture corpus plan.json - no network, no gh, no fixtures of its own.
"""

import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugin" / "skills" / "tracker" / "scripts"
PLAN = ROOT / "scripts" / "fixtures" / "renders" / "plan.json"
SCHEMA = ROOT / "plugin" / "references" / "plan.schema.json"

sys.path.insert(0, str(SCRIPTS))
import tracker  # noqa: E402


def _capture(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        tracker.main(argv)
    return buf.getvalue()


def run(argv):
    return json.loads(_capture(argv))


class PublishTest(unittest.TestCase):
    def test_supported_version_matches_the_core_plan_schema(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(tracker.PLAN_SCHEMA_VERSION,
                         schema["properties"]["schemaVersion"]["const"])

    def test_an_older_plan_publishes_from_the_fields_it_carries(self):
        """A version label is form, not substance: a v1 plan still carries every
        field the projection reads, so refusing it strands a team's tracker on a
        regeneration nobody needed. The version it read is still reported."""
        plan = json.loads(PLAN.read_text(encoding="utf-8"))
        plan["schemaVersion"] = "1"
        plan["references"] = ["adr.md"]
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "plan.json"
            path.write_text(json.dumps(plan), encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr), \
                    mock.patch.object(tracker, "canonical_plan_path",
                                      return_value="specs/plan.json"):
                out = run(["publish", str(path), "--sha", "abc1234"])
        self.assertEqual([c["id"] for c in out["children"]],
                         [s["id"] for s in plan["stories"]])
        self.assertIn(plan["overview"]["summary"], out["parent"]["body"])
        self.assertIn("schemaVersion '1'", stderr.getvalue())

    def test_a_plan_missing_a_read_field_exits_naming_it(self):
        """A field the projection reads that is missing or unreadable cannot be
        projected; the exit names the field and the story before any tracker
        call, so no half-published plan and no traceback is left behind."""
        def missing_name(plan):
            del plan["stories"][1]["name"]

        def missing_stories(plan):
            del plan["stories"]

        def missing_id(plan):
            del plan["stories"][1]["id"]

        def empty_id(plan):
            # An empty id would give the child the parent's marker, so the
            # child's update would overwrite the parent issue.
            plan["stories"][1]["id"] = ""

        def scalar_depends_on(plan):
            plan["stories"][1]["dependsOn"] = [1]

        def null_scope(plan):
            plan["stories"][1]["scope"] = None

        def list_fis(plan):
            plan["stories"][1]["fis"] = ["s02-record-sign-ins.md"]

        def scalar_source_refs(plan):
            # Iterated as a string, this would publish one `PRD:` line per character.
            plan["stories"][1]["sourceRefs"] = "REQ-01"

        cases = ((missing_name, "story S02 lacks a readable `name`"),
                 (missing_stories, "plan.json lacks a `stories` list"),
                 (missing_id, "story #2 lacks a readable `id`"),
                 (empty_id, "story #2 lacks a readable `id`"),
                 (scalar_depends_on, "story S02 lacks a readable `dependsOn`"),
                 (null_scope, "story S02 lacks a readable `scope`"),
                 (list_fis, "story S02 lacks a readable `fis`"),
                 (scalar_source_refs, "story S02 lacks a readable `sourceRefs`"))
        for breaks, message in cases:
            with self.subTest(breaks.__name__):
                plan = json.loads(PLAN.read_text(encoding="utf-8"))
                breaks(plan)
                with tempfile.TemporaryDirectory() as tmp:
                    path = pathlib.Path(tmp) / "plan.json"
                    path.write_text(json.dumps(plan), encoding="utf-8")
                    with self.assertRaises(SystemExit) as ctx:
                        tracker.load_plan(path)
                self.assertIn(message, str(ctx.exception))
                self.assertIn(f"andthen:plan skill on the requirements source of {path.parent.as_posix()}",
                              str(ctx.exception))

    def test_a_repeated_story_id_stops_before_any_body_is_written(self):
        """Each child's marker is plan path plus story id, so two stories with
        one id would share an issue and the second body would overwrite the
        first. The exit names the id before anything is materialized."""
        plan = json.loads(PLAN.read_text(encoding="utf-8"))
        plan["stories"][1]["id"] = plan["stories"][0]["id"]
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "plan.json"
            path.write_text(json.dumps(plan), encoding="utf-8")
            body_dir = pathlib.Path(tmp) / "bodies"
            with mock.patch.object(tracker, "canonical_plan_path",
                                   return_value="specs/plan.json"), \
                    self.assertRaises(SystemExit) as ctx:
                _capture(["publish", str(path), "--body-dir", str(body_dir)])
            self.assertFalse(body_dir.exists())
        self.assertIn("repeats story id S01 (#2)", str(ctx.exception))

    def setUp(self):
        self.plan = json.loads(PLAN.read_text(encoding="utf-8"))
        self.plan_id = PLAN.relative_to(ROOT).as_posix()
        self.out = run(["publish", str(PLAN), "--sha", "abc1234"])

    def test_parent_carries_summary_and_one_source_ordered_line_per_story(self):
        """The parent is the whole plan's projection - a story missing from the
        checklist is a story the team cannot see."""
        body = self.out["parent"]["body"]
        self.assertIn(self.plan["overview"]["summary"], body)
        self.assertIn(f"PRD: {self.plan['prd']}", body)
        for story in self.plan["stories"]:
            self.assertIn(f"{story['id']} - {story['name']}", body)
        checks = [ln for ln in body.splitlines() if ln.startswith("- [")]
        self.assertEqual(len(checks), len(self.plan["stories"]))
        self.assertTrue(checks[0].startswith("- [x]"))   # S01 is done
        self.assertTrue(checks[1].startswith("- [ ]"))   # S02 is pending
        self.assertNotIn("### P", body)
        self.assertNotIn("**W", body)

    def test_child_carries_backreference_scope_anchors_and_dependencies(self):
        """The back-reference is the only join key - without it a re-run
        duplicates the whole plan into the tracker."""
        s02 = self.out["children"][1]
        self.assertEqual(s02["title"], "S02 - Record sign-ins in the audit trail")
        self.assertIn(tracker.machine_marker(self.plan_id, "S02"), s02["body"])
        self.assertIn("One audit row per successful sign-in.", s02["body"])
        self.assertIn("PRD: prd.md#observability", s02["body"])
        self.assertIn("Blocked by: S01", s02["body"])
        self.assertEqual(s02["dependsOn"], ["S01"])
        self.assertNotIn("labels", s02)
        self.assertNotIn("assignee", s02)

    def test_child_projects_external_task_progress_without_risk(self):
        """Tracker progress comes from plan state, never FIS checkboxes.

        Nothing populates a label, so the payload carries no label field to
        send: an always-empty one reads as a contract the tracker does not have.
        """
        self.assertIn("Completed tasks: TI01",
                      self.out["children"][0]["body"])
        self.assertNotIn("labels", self.out["children"][0])

    def test_fis_link_is_pinned_to_the_commit(self):
        """An unpinned FIS link rots the moment the branch closes."""
        self.assertIn("s01-harden-the-session-cookie.md@abc1234",
                      self.out["children"][0]["body"])

    def test_first_run_creates(self):
        self.assertEqual(self.out["parent"]["action"], "create")
        self.assertEqual([c["action"] for c in self.out["children"]],
                         ["create", "create"])

    def test_rerun_against_existing_issues_updates(self):
        """Re-publish is an update, not a second copy of the plan."""
        existing = [
            {"number": 10, "body": f"...\n\n{tracker.machine_marker(self.plan_id)}"},
            {"number": 11, "body": f"scope\n\n{tracker.machine_marker(self.plan_id, 'S01')}"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "existing.json"
            path.write_text(json.dumps(existing), encoding="utf-8")
            out = run(["publish", str(PLAN), "--existing", str(path)])
        self.assertEqual((out["parent"]["action"], out["parent"]["number"]),
                         ("update", 10))
        self.assertEqual((out["children"][0]["action"], out["children"][0]["number"]),
                         ("update", 11))
        self.assertEqual(out["children"][1]["action"], "create")

    def test_plan_identity_is_canonical_across_path_spellings(self):
        """The caller's path spelling cannot create a second tracker identity."""
        alternate = PLAN.parent / ".." / "renders" / PLAN.name
        self.assertEqual(tracker.canonical_plan_path(PLAN, ROOT),
                         tracker.canonical_plan_path(alternate, ROOT))
        self.assertEqual(self.out["plan"], self.plan_id)
        relative = run(["publish", self.plan_id, "--sha", "abc1234"])
        self.assertEqual(relative["plan"], self.out["plan"])
        self.assertEqual(relative["parent"]["search"], self.out["parent"]["search"])

    def test_only_an_exact_marker_line_matches(self):
        """Prose containing a marker-like substring is not tracker identity."""
        marker = tracker.machine_marker(self.plan_id)
        existing = [{"number": 10, "body": f"prefix {marker} suffix"}]
        self.assertEqual(tracker.resolve(existing, marker)["action"], "create")

    def test_duplicate_marker_is_blocked(self):
        """Ambiguous identity must stop publication instead of editing the first issue."""
        marker = tracker.machine_marker(self.plan_id, "S01")
        existing = [{"number": 11, "body": marker},
                    {"number": 12, "body": f"scope\n{marker}"}]
        with self.assertRaises(SystemExit) as ctx:
            tracker.resolve(existing, marker)
        self.assertIn("multiple tracker issues match", str(ctx.exception))
        self.assertIn("#11, #12", str(ctx.exception))

    def test_live_transport_materializes_literal_bodies_deterministically(self):
        """Shell-shaped plan data stays inert because body transport uses files."""
        plan = json.loads(PLAN.read_text(encoding="utf-8"))
        plan["overview"]["summary"] = "quoted ' \" $(touch nope)\nsecond line"
        plan["stories"][0]["scope"] = "line one\n`touch nope-too`\nline three"
        plan["stories"][0]["name"] = "quote ' and $(touch title-nope)"
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            plan_path = root / "specs" / "plan.json"
            plan_path.parent.mkdir()
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            body_dir = root / ".agent_temp" / "tracker-bodies"
            argv = ["publish", str(plan_path), "--body-dir", str(body_dir)]
            with mock.patch.object(tracker, "canonical_plan_path",
                                   return_value="specs/plan.json"):
                first = run(argv)
                second = run(argv)
            self.assertEqual(first["parent"]["body_file"],
                             second["parent"]["body_file"])
            for row in [first["parent"], *first["children"]]:
                self.assertEqual(pathlib.Path(row["body_file"]).read_text(encoding="utf-8"),
                                 row["body"])
            self.assertIn("$(touch nope)", first["parent"]["body"])
            self.assertIn("`touch nope-too`", first["children"][0]["body"])
            self.assertEqual(first["children"][0]["title"],
                             "S01 - quote ' and $(touch title-nope)")

    def test_dry_run_without_a_lookup_classifies_nothing(self):
        """A dry run makes no tracker call, so it cannot know whether an issue
        exists: the payloads are shown and create-versus-update is `unknown`,
        never a guessed `create` that a live run would contradict."""
        out = run(["publish", str(PLAN), "--dry-run"])
        self.assertEqual(out["parent"]["action"], "unknown")
        self.assertEqual({c["action"] for c in out["children"]}, {"unknown"})
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "existing.json"
            path.write_text("[]", encoding="utf-8")
            out = run(["publish", str(PLAN), "--dry-run", "--existing", str(path)])
        self.assertEqual(out["parent"]["action"], "create")

    def test_dry_run_writes_no_body_files(self):
        """The advertised no-write boundary wins even if body-dir is supplied."""
        with tempfile.TemporaryDirectory() as tmp:
            body_dir = pathlib.Path(tmp) / "bodies"
            out = run(["publish", str(PLAN), "--body-dir", str(body_dir),
                       "--dry-run"])
            self.assertFalse(body_dir.exists())
            self.assertNotIn("body_file", out["parent"])


if __name__ == "__main__":
    unittest.main()
