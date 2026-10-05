#!/usr/bin/env python3
"""Both directions for the cookbook audit: every failure mode fires on the
prose that would break a user's paste, and none fires on the shipped prose. A gate
that flags its own fix gets switched off, so the negative cases are the point.

The rest of the file guards what a rewording of shipped prose must not undo: the
machine contracts `plan.schema.json` carries, and surfaces retired from the skills.
A rule *stated* in prose is never pinned here, because a sentence pinned here
cannot be reworked and drifts instead."""
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("audit_cookbook", ROOT / "scripts/audit-cookbook.py")
audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit)


def misses(line):
    out = []
    for skill, seg in audit.segments(line):
        audit.check(skill, seg, "T", out)
    return out


class ExtractionTest(unittest.TestCase):
    def test_comment_and_second_invocation_end_a_segment(self):
        segs = [s for _, s in audit.segments(
            "`/andthen:plan docs/x/`  # or: /andthen:plan @docs/y.md")]
        self.assertEqual([s.strip() for s in segs], ["docs/x/", "@docs/y.md"])

    def test_a_quoted_request_is_prose_not_an_option(self):
        self.assertEqual(misses('/andthen:implement-fix "add a --json flag"'), [])


class FiringTest(unittest.TestCase):
    def test_missing_skill_fires(self):
        self.assertIn("does not exist", misses("/andthen:nosuchskill")[0])

    def test_retired_flag_fires(self):
        self.assertIn("--council", misses("/andthen:review --council src/")[0])

    def test_unknown_mode_value_fires(self):
        self.assertIn("--mode nonesuch", misses("/andthen:review --mode nonesuch src/")[0])


class ShippedProseTest(unittest.TestCase):
    def test_the_live_docs_pass(self):
        self.assertEqual(audit.main(), 0)


class PlanSchemaContracts(unittest.TestCase):
    """`plan.schema.json` is what a plan candidate is checked against, so its version
    and its absent properties are machine contracts. The prose describing them is not."""

    def schema_text(self):
        return (ROOT / "plugin/references/plan.schema.json").read_text(encoding="utf-8")

    def test_current_plan_version_is_pinned_in_schema_and_corpus(self):
        self.assertEqual(json.loads(self.schema_text())["properties"]["schemaVersion"]["const"], "2")
        self.assertEqual(json.loads((ROOT / "scripts/fixtures/renders/plan.json")
                                    .read_text(encoding="utf-8"))["schemaVersion"], "2")

    def test_v2_schema_has_no_metadata_property(self):
        # 0.x shipped `metadata`; 1.0 regenerates a bundle from the PRD rather than
        # migrating its state, so no reader may resolve state the schema cannot hold.
        self.assertNotIn('"metadata"', self.schema_text())

    def test_v2_has_no_parallel_capacity_properties(self):
        # A shared worktree shares one test run, so stories run one at a time and
        # the schema carries no slot count to schedule against.
        self.assertFalse({"capacity", "maxParallel", "workerSlots"}
                         & set(json.loads(self.schema_text())["properties"]))


class RetiredSurfaceGuards(unittest.TestCase):
    """A flag, command form, or claim removed from the workflow must not reappear in
    shipped content. These are absence checks by design: they cost a reworder nothing
    and catch the one edit that would silently restore a surface users would then type.
    Every guard names a retired mechanism, never a phrase a rewrite may legitimately
    use; matching is case-insensitive so a re-cased surface does not slip through."""

    def absent(self, rel, *retired):
        body = (ROOT / rel).read_text(encoding="utf-8").lower()
        for token in retired:
            with self.subTest(path=rel, retired=token):
                self.assertNotIn(token.lower(), body)

    def test_issue_consumers_do_not_resolve_a_bare_issue_number(self):
        # A bare number resolves against whatever repo the agent happens to be in.
        for rel in ("plugin/skills/clarify/SKILL.md",
                    "plugin/skills/triage/SKILL.md", "plugin/skills/plan/SKILL.md"):
            self.absent(rel, "gh issue view <N>")

    def test_tracker_has_no_global_cap_or_substring_query(self):
        self.absent("plugin/skills/tracker/SKILL.md",
                    "--limit 200", '"andthen:tracker" in:body')

    def test_plan_v1_surfaces_stay_retired(self):
        # 1.0 regenerates a bundle from the PRD instead of migrating v1 state, so
        # neither the migration reader nor v1's `metadata` field has a consumer left.
        self.absent("plugin/skills/plan/references/breakdown.md", "migration input")
        self.absent("plugin/references/plan-schema.md", "`metadata`")
        self.absent("plugin/skills/tracker/SKILL.md", "legacy metadata")

    def test_team_mode_stays_retired(self):
        # `--worktree` is back as plain git in the run session; what stays retired is
        # Agent Teams orchestration, the capacity flag, and the script-driven
        # worktree lifecycle with its merge-resolve protocol.
        for rel in ("plugin/skills/exec-plan/SKILL.md", "plugin/references/plan-schema.md",
                    "plugin/skills/exec-plan/references/plan-run.md",
                    "plugin/skills/exec-plan/references/story-worktrees.md"):
            self.absent(rel, "--team", "--max-parallel", "merge-resolve",
                        "worktree-mode.md", "team-mode-orchestration.md",
                        "capacity-bounded", "story-implementer slots",
                        "attribution rule")

    def test_a_non_default_execution_target_is_not_a_warning(self):
        self.absent("plugin/skills/exec-plan/references/plan-run.md",
                    "WARNING: BASE_BRANCH={value} is not the repo's default branch")

    def test_checkbox_task_state_stays_retired(self):
        # Task state lives in the story's `plan.json` record, never in ticked boxes
        # the FIS carries.
        for rel in ("plugin/skills/exec-plan/SKILL.md",
                    "plugin/skills/exec-plan/references/story.md"):
            self.absent(rel, "checks the boxes", "Mark the task checkbox",
                        "status is untouched", "the only thing that writes",
                        "--plan {PLAN_FILE_PATH} --story {STORY_ID}")
        self.absent("plugin/skills/exec-plan/references/plan-run.md",
                    "exec-plan handles FIS writes only",
                    "keeps its pre-run `plan.json` status")
        self.absent("README.md", "A refused completion changes nothing")
        self.absent("COOKBOOK.md", "observations and ticked boxes")

    def test_the_ops_verb_surface_stays_retired(self):
        # The session executing a story writes its `plan.json` row with its file
        # tools, so no skill may route a state write through a script verb again.
        for rel in ("plugin/skills/exec-plan/SKILL.md",
                    "plugin/skills/exec-plan/references/story.md",
                    "plugin/skills/exec-plan/references/plan-run.md",
                    "plugin/skills/exec-plan/references/story-worktrees.md",
                    "plugin/skills/plan/SKILL.md", "plugin/skills/plan/references/breakdown.md",
                    "plugin/skills/handoff/SKILL.md", "plugin/references/plan-schema.md"):
            self.absent(rel, "ops.py", "andthen:ops", "validate-plan", "merge-story",
                        "read-state", "update-plan", "complete-task", "complete-story")
        self.assertFalse((ROOT / "plugin/skills/ops").exists())
        self.assertFalse((ROOT / "plugin/skills/exec-plan/references/story-merge.md").exists())

    def test_plan_authoring_has_no_post_status_validation_pass(self):
        # The candidate is checked before it is written, so no second pass follows.
        self.absent("plugin/skills/plan/references/breakdown.md",
                    "After those final status writes, pass the Step 4")

    def test_remediation_rounds_stay_retired(self):
        self.absent("plugin/skills/implement-fix/SKILL.md",
                    "closure re-review", "Two-round cap", "Rounds used",
                    "delegation-shape.md")
        self.absent("plugin/skills/implement-fix/references/report-annotation.md",
                    "Rounds used")

    def test_the_retired_review_gate_stays_gone(self):
        """ADR-014 retired the per-story review gate: the review is a code review
        sized to the change, with no report, no verdict grammar, and no flag. The
        tokens are assembled rather than typed, for the same reason a policing
        script skips its own source - the repository sweeps itself for them, and
        this guard must not be the match that sweep finds."""
        gate = "story-" + "gate"
        for rel in ("plugin/skills/review/SKILL.md",
                    "plugin/skills/review/references/full-review.md",
                    "plugin/skills/implement-fix/SKILL.md",
                    "plugin/skills/exec-plan/SKILL.md",
                    "plugin/skills/exec-plan/references/story.md",
                    "plugin/skills/exec-plan/references/plan-run.md"):
            self.absent(rel, "--" + gate, gate + ".md", "Story-" + "Gate:")

    def test_the_story_procedure_lives_in_the_exec_plan_body(self):
        """ADR-014's recorded regression was a plan run executing the story in its
        own session. The story procedure lives in `exec-plan/references/story.md`,
        which only the exec-plan body links, so a plan run - which reads
        `plan-run.md` - never loads the procedure it must delegate, and no other
        skill can run it in place. The retired shared-reference shapes stay gone."""
        self.assertTrue((ROOT / "plugin/skills/exec-plan/references/story.md").is_file())
        body = ROOT / "plugin/skills/exec-plan/SKILL.md"
        self.assertIn("](references/story.md)", body.read_text(encoding="utf-8"))
        mention = re.compile(r"(?<![\w-])story\.md")
        for path in sorted((ROOT / "plugin").rglob("*")):
            if not path.is_file() or path == body or path.suffix not in (".md", ".yaml", ".py"):
                continue
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertIsNone(mention.search(path.read_text(encoding="utf-8")))
        for rel in ("plugin/skills/spec", "plugin/skills/exec-spec"):
            with self.subTest(path=rel):
                self.assertFalse((ROOT / rel).exists())
        for rel in ("plugin/skills/exec-plan/SKILL.md",
                    "plugin/skills/exec-plan/references/story.md",
                    "plugin/skills/exec-plan/references/plan-run.md",
                    "plugin/skills/review/SKILL.md",
                    "plugin/skills/review/references/full-review.md",
                    "plugin/skills/implement-fix/SKILL.md",
                    "plugin/skills/plan/references/breakdown.md"):
            self.absent(rel, "story-execution.md", "caller-lines.md",
                        "delegation-shape.md", "data-contract.md",
                        "GOVERNING " + "PLAN PATH", "Executor " + "rounds")
        for rel in ("plugin/references/story-execution.md", "plugin/references/caller-lines.md",
                    "plugin/references/delegation-shape.md", "plugin/references/data-contract.md",
                    "plugin/references/" + "story-" + "gate.md"):
            with self.subTest(path=rel):
                self.assertFalse((ROOT / rel).exists())


if __name__ == "__main__":
    unittest.main(verbosity=1)
