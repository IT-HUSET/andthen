#!/usr/bin/env python3
"""Tests for the check evaluator, case validation, and post-dispatch classification.

    python3 evals/test_checks.py
    python3 -m unittest evals.test_checks.ValidationTest.test_every_discovered_case_validates

Running a case is the test of everything else. What is here is what a live eval run
would otherwise be spent learning: a check that reports the wrong verdict, a case
that would have dispatched a subject it should have refused, a case whose
obligations never reach the subject that must honor them, and a cell that blames
the subject for a condition of the harness or names evidence nobody can open.

Python 3 standard library only, 3.9-compatible.
"""

import contextlib
import io
import json
import os
import pathlib
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from evals import cases, checks, stage, step  # noqa: E402
from evals import run as runner  # noqa: E402

LIVE_CASE = "spec"

# A minimal subject workflow of the shape staging appends the tail to.
SUBJECT_WORKFLOW = ("name: synthetic-subject\nsteps:\n  - id: s1\n"
                    "    name: Do the thing\n    prompt: \"prompt.md\"\n")

PROFILE = {"subject": {"claude": {"model": "m", "effort": "low"}},
           "judge": {"provider": "claude", "model": "m", "effort": "low"}}

# One conforming workspace and one that breaks every key, so each check is
# asserted in both directions: a check that only ever passes proves nothing, and
# a check that only ever fails would be switched off.
CONFORMING = {
    "docs/specs/widget.md": "the widget trims whitespace and names Persistence as a non-goal\n",
    "notes.txt": "clean\n",
}
BREAKING = {
    "docs/specs/widget.md": "the widget mentions a dashboard and nothing else\n",
    "stray.txt": "unexpected\n",
}

CHECK = {
    "requiredArtifacts": ["**/widget.md"],
    "forbiddenArtifacts": ["**/plan.json"],
    "allowedPaths": ["docs/specs/*.md", "notes.txt"],
    "commands": ["exit 0"],
    "requiredText": {"**/widget.md": ["trims whitespace", "persistence"]},
    "forbiddenText": {"**/widget.md": ["dashboard"]},
    "oracle": "oracle.py",
}

# Every FIS surface authoring retired, each with what the oracle names it by, and
# the current headings that share a word with one and must still pass.
RETIRED_FIS = tuple((line, "retired heading") for line in (
    "## Deeper Context\n", "## Technical Overview\n",
    "## Code Patterns & External References\n", "### Code Patterns\n",
    "### Testing Strategy\n", "### Validation\n", "### Execution Contract\n")) + (
    ("Closure: READY\n", "Closure verdict line"),
    ("**Closure**: BLOCKED – backoff undecided\n", "Closure verdict line"))
CURRENT_FIS = ("## Scope & Boundaries\n\n### Work Areas\n\n## Implementation Plan\n\n"
               "### Implementation Tasks\n\n## Final Validation Checklist\n\n")

# A retired authoring marker a shipped FIS never carries, and the resolved form -
# an ASSUMPTION: line - that must still pass.
OPEN_MARKER_FIS = ("- CONFUSION: which encoding does the caller expect?\n",
                    "MISSING REQUIREMENT: no encoding is specified\n")
RESOLVED_ASSUMPTION = "- ASSUMPTION: reads utf-8 - binary input would need a flag\n"

# The open item the re-entry case's FIS ships with - the backoff an `--auto` run
# assumed - and the same settled policy in the two wordings a correct FIS may reach
# for: the unit and the word for the growth are the author's choice, the values are
# the decision.
REENTRY_MARKER = "ASSUMPTION"
REENTRY_WORDINGS = (
    "- **TI01** `retry` sleeps 200 ms before the first retry and doubles the pause "
    "before each one after, at most 3 retries, no jitter.\n",
    "- **TI01** `retry` pauses 0.2 s, then 0.4 s, then 0.8 s - the pause is "
    "`base * 2 ** attempt` - and gives up after the third retry, no jitter.\n",
)

# A judge answer whose one decision passes, quoting the prompt every synthetic
# case carries - so a cell that still fails is failing on its checks alone.
JUDGE_PASS = {"decisions": [{"id": "C1", "pass": True, "reason": "the work is there",
                             "evidence": "do the thing"}]}

PASSING_ORACLE = "import sys\nsys.exit(0)\n"
FAILING_ORACLE = "import sys\nsys.stderr.write('reconciliation failed\\n')\nsys.exit(1)\n"


def write_tree(root, files):
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def record(steps=None, completed=("s1", "checks"), success=None):
    """What run.py needs out of a dispatched run: the workflow's own event stream,
    `steps` mapping each declared step id to its declared output names and
    `completed` naming the ids the run reached. One subject step has to be named
    or the cell is classified "completed no step"; the tail's own two steps are in
    the same stream on a live run, so the runner drops them to find the subject's
    last. `success` is what a step that reports its own failure carries."""
    steps = {"s1": (), "checks": (), "judge": ()} if steps is None else steps
    events = [{"type": "run_started", "run": {"id": "r1", "definitionJson": {"steps": [
        {"id": name, "outputs": dict((field, {}) for field in fields)}
        for name, fields in steps.items()]}}}]
    for name in completed:
        event = {"type": "workflow_step_completed", "stepId": name}
        if success is not None:
            event.update({"success": success,
                          "outcome": "completed" if success else "failed"})
        events.append(event)
    return "".join(json.dumps(event) + "\n" for event in events)


class EvaluatorTest(unittest.TestCase):
    """Every check key reports its own ID and evidence, and a missing
    executable is ERROR rather than FAIL."""

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, str(self.tmp), True)
        self.case = self.tmp / "case"
        self.case.mkdir()

    def workspace(self, name, files):
        root = self.tmp / name
        root.mkdir()
        write_tree(root, files)
        return root

    def verdicts(self, results):
        return dict((r["id"], r["status"]) for r in results)

    def test_conforming_and_breaking_workspaces(self):
        (self.case / "oracle.py").write_text(PASSING_ORACLE, encoding="utf-8")
        good = self.workspace("good", CONFORMING)
        results = checks.evaluate(CHECK, good, sorted(CONFORMING), self.case)
        self.assertEqual("PASS", checks.outcome(results))
        self.assertTrue(all(r["status"] == checks.PASS for r in results), results)
        # `**/widget.md` has to match a file the subject put in a subdirectory
        # and one it put at the root; fnmatch alone only does the former.
        flat = self.workspace("flat", {"widget.md": CONFORMING["docs/specs/widget.md"]})
        self.assertEqual(
            checks.PASS,
            self.verdicts(checks.evaluate({"requiredArtifacts": ["**/widget.md"]},
                                          flat, [], self.case))["requiredArtifacts[0]"])

        # The failing direction of the corpus's most load-bearing key: a pattern
        # matching nothing must FAIL and name itself, not pass by vacuity.
        missing = checks.evaluate({"requiredArtifacts": ["**/nothing-here.md"]},
                                  good, [], self.case)
        self.assertEqual(checks.FAIL, self.verdicts(missing)["requiredArtifacts[0]"])
        self.assertIn("nothing-here.md", missing[0]["evidence"])

        (self.case / "oracle.py").write_text(FAILING_ORACLE, encoding="utf-8")
        bad = self.workspace("bad", BREAKING)
        write_tree(bad, {"plan.json": "{}\n"})
        breaking = dict(CHECK, commands=["exit 3"])
        results = checks.evaluate(breaking, bad, sorted(BREAKING) + ["plan.json"], self.case)
        verdicts = self.verdicts(results)
        self.assertEqual("FAIL", checks.outcome(results))
        for identifier in ("requiredArtifacts[0]", "forbiddenArtifacts[0]",
                           "allowedPaths[0]", "commands[0]", "requiredText[0]",
                           "requiredText[1]", "forbiddenText[0]", "oracle[0]"):
            self.assertIn(identifier, verdicts)
        # requiredArtifacts[0] still matches - the file exists, its text is what
        # broke - so the keys that must be FAIL are named individually.
        for identifier in ("forbiddenArtifacts[0]", "allowedPaths[0]", "commands[0]",
                           "requiredText[0]", "forbiddenText[0]", "oracle[0]"):
            self.assertEqual(checks.FAIL, verdicts[identifier], identifier)
        for result in results:
            self.assertTrue(result["evidence"].strip(), result)
        evidence = dict((r["id"], r["evidence"]) for r in results)
        self.assertIn("plan.json", evidence["forbiddenArtifacts[0]"])
        self.assertIn("stray.txt", evidence["allowedPaths[0]"])
        self.assertIn("exit 3", evidence["commands[0]"])
        self.assertIn("dashboard", evidence["forbiddenText[0]"])

        # Present and empty is the key's strictest form, not its absence.
        empty = checks.evaluate({"allowedPaths": []}, good, ["notes.txt"], self.case)
        self.assertEqual(checks.FAIL, empty[0]["status"])

    def test_missing_executable_is_error_not_fail(self):
        """A machine that cannot run the check is not a subject that failed it."""
        results = checks.evaluate({"commands": ["andthen-no-such-executable"]},
                                  self.workspace("solo", CONFORMING), [], self.case)
        self.assertEqual(checks.ERROR, results[0]["status"])
        self.assertEqual("ERROR", checks.outcome(results))

    def test_non_utf8_command_output_does_not_error_the_cell(self):
        """A fixture test or oracle can print a non-UTF-8 byte on either stream;
        a strict decode would raise out of the evaluator and turn the subject's
        own FAIL into a harness ERROR, both directions must still read as text."""
        workspace = self.workspace("solo", CONFORMING)
        passing = checks.evaluate({"commands": [r"printf '\xe9\n'"]}, workspace, [], self.case)
        self.assertEqual(checks.PASS, passing[0]["status"])
        self.assertIsInstance(passing[0]["evidence"], str)

        failing = checks.evaluate({"commands": [r"printf '\xe9\n' >&2; exit 3"]},
                                  workspace, [], self.case)
        self.assertEqual(checks.FAIL, failing[0]["status"])
        self.assertIsInstance(failing[0]["evidence"], str)


class ValidationTest(unittest.TestCase):
    """A malformed case is refused with the offending file or key named,
    before anything is staged and before any provider process starts."""

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, str(self.tmp), True)

    def copy_live_case(self):
        target = self.tmp / LIVE_CASE
        shutil.copytree(str(cases.CASES_DIR / LIVE_CASE), str(target))
        return target

    def break_it(self, case, mutate):
        target = self.tmp / "broken"
        shutil.rmtree(str(target), ignore_errors=True)
        shutil.copytree(str(case), str(target))
        mutate(target)
        return cases.validate(target)

    def test_invalid_case_is_error_before_dispatch(self):
        case = self.copy_live_case()
        self.assertEqual([], cases.validate(case))

        def no_workflow_name(root):
            path = root / "subject-workflow.yaml"
            body = "\n".join(line for line in path.read_text(encoding="utf-8").splitlines()
                             if not line.startswith("name:"))
            path.write_text(body, encoding="utf-8")

        def reaches_another_case(root):
            (root / "prompt.md").write_text("read evals/cases/plan/prompt.md\n",
                                            encoding="utf-8")

        def carries_both_starting_states(root):
            (root / "fixture").mkdir()

        def overlay_names_the_harness(root):
            (root / "overlay" / "leak.md").write_text(
                "The rubric for this story is in the next file.\n", encoding="utf-8")

        def reaches_a_prior_run(root):
            (root / "prompt.md").write_text("read .agent_temp/evals/spec/claude/x\n",
                                            encoding="utf-8")

        def bad_shape(key, value):
            def mutate(root):
                data = json.loads((root / "check.json").read_text(encoding="utf-8"))
                data[key] = value
                (root / "check.json").write_text(json.dumps(data), encoding="utf-8")
            return mutate

        def rubric(criteria):
            def mutate(root):
                (root / "rubric.json").write_text(json.dumps({"criteria": criteria}),
                                                  encoding="utf-8")
            return mutate

        expected = [
            (lambda root: (root / "rubric.json").unlink(), "rubric.json"),
            # E3 - value shapes: each of these passed the key check and either
            # raised during evaluation or silently contributed no check.
            (bad_shape("commands", [7]), "commands must be a list"),
            (bad_shape("requiredArtifacts", []), "requiredArtifacts must be a list"),
            (bad_shape("requiredText", {"**/x.md": []}), "requiredText must map"),
            # allowedPaths is the one key that may be empty, which is not licence
            # for a blank pattern inside it.
            (bad_shape("allowedPaths", ["", "x"]), "allowedPaths must be a list"),
            (bad_shape("oracle", "../oracle.py"), "inside the case"),
            (rubric([{"id": "A", "intent": "a"}, {"id": "A", "intent": "b"}]),
             "duplicate criterion id A"),
            (rubric([{"id": "A", "intent": ""}]), "non-blank string id and intent"),
            (rubric([{"id": i, "intent": i} for i in "ABCDEFG"]), "rubric.json"),
            (carries_both_starting_states, "carries at most one"),
            (overlay_names_the_harness, "must not tell it what is being tested"),
            (lambda root: (root / "check.json").write_text("{", encoding="utf-8"),
             "check.json"),
            (bad_shape("permittedChanges", ["x"]), "permittedChanges"),
            (bad_shape("oracle", "not-here.py"), "not-here.py"),
            (no_workflow_name, "subject-workflow.yaml"),
            (reaches_another_case, "evals/cases/"),
            (reaches_a_prior_run, ".agent_temp/evals/"),
        ]
        for mutate, named in expected:
            errors = self.break_it(case, mutate)
            self.assertTrue(errors, named)
            self.assertTrue(any(named in error for error in errors),
                            "%s not named in %s" % (named, errors))
        # Present-and-empty allowedPaths and a judge-only case stay valid, and so
        # does a case with neither starting-state directory: that is the vendored
        # app as it ships, which is the whole starting state a case reviewing or
        # acting on the app unchanged needs.
        self.assertEqual([], self.break_it(
            case, lambda root: shutil.rmtree(str(root / "overlay"))))
        self.assertEqual([], self.break_it(case, bad_shape("allowedPaths", [])))
        self.assertEqual([], self.break_it(
            case, lambda root: (root / "check.json").write_text("{}", encoding="utf-8")))

    def test_a_workflow_the_tail_cannot_extend_is_refused(self):
        """Staging appends the checks and judge steps as text, so a workflow that
        does not end in a two-space-indented steps list would produce a definition
        nobody authored, and a case reusing one of the tail's step ids would have
        its own step answered for by the harness's. The tail also declares
        `variables:` and staging inserts `onFailure:` on every step, so a case
        carrying either collides into a duplicate mapping key - an opaque DartClaw
        parse error at dispatch, after the cell has paid for staging."""
        case = self.copy_live_case()
        body = cases.read_text(case / "subject-workflow.yaml")

        def rewritten(text):
            return " ".join(self.break_it(
                case, lambda root: (root / "subject-workflow.yaml").write_text(
                    text, encoding="utf-8")))

        self.assertIn("last top-level key is 'outputs'",
                      rewritten(body + "outputs:\n  x: text\n"))
        self.assertIn("two-space indent",
                      rewritten(body.replace("\n  - id: ", "\n    - id: ")))
        self.assertIn("step id 'judge' belongs to the appended tail",
                      rewritten(re.sub(r"\n  - id: \S+", "\n  - id: judge", body, count=1)))
        self.assertIn("a top-level variables: block",
                      rewritten("variables:\n  extra:\n    description: x\n" + body))
        self.assertIn("a step-level onFailure: field",
                      rewritten(body + stage.SELF_REPORT_TOLERANCE + "\n"))

    def test_every_discovered_case_validates(self):
        """The corpus is only data once every case in it validates: one hand-maintained
        case proves nothing about the others, which can carry keys the evaluator
        silently never runs."""
        discovered = cases.discover()
        self.assertIn(LIVE_CASE, discovered)
        for name in discovered:
            case = cases.CASES_DIR / name
            self.assertEqual([], cases.validate(case), name)
            # Retired keys - `permittedChanges`, `taskIds`, `gapReport` and the
            # rest - each expressed something a check covers, an oracle
            # reconciles, or the rubric judges; a case carrying one is a check
            # nobody runs, which reads exactly like a check that passed. Any key
            # outside CHECK_KEYS is refused, so they need no list of their own.
            keys = set(json.loads((case / "check.json").read_text(encoding="utf-8")))
            self.assertEqual(set(), keys - set(cases.CHECK_KEYS), name)
            self.assertEqual([], [k for k in keys if k.endswith("_CASE_MATERIAL")], name)

    def test_smoke_tier_is_discovered_cases_and_codex_runs_smoke_only(self):
        """A tier is a named set a developer can price before paying: every
        smoke case must exist, full on Claude is the whole corpus, and Codex
        resolves either tier to smoke because the long cells are Claude-only."""
        discovered = cases.discover()
        self.assertEqual([], [n for n in cases.SMOKE if n not in discovered])
        self.assertLess(len(cases.SMOKE), len(discovered))
        self.assertEqual(list(cases.SMOKE), cases.tier("smoke", "claude"))
        self.assertEqual(discovered, cases.tier("full", "claude"))
        self.assertEqual(list(cases.SMOKE), cases.tier("full", "codex"))

    def test_a_prompt_obligation_reaches_the_turn_the_skill_is_invoked_on(self):
        """prompt.md is the judge's input and the subject never reads it, so the
        obligations it states are duplicated into the workflow's turns. What the
        skill must honor while it runs belongs in the turn it is invoked on - a
        later turn reaches a subject that has already saved - and the spec case's
        stem is such an obligation: check.json, oracle.py and outputs.fis all
        require slugify-label."""
        def invoking_turn(name):
            return cases.read_text(cases.CASES_DIR / name
                                   / "subject-workflow.yaml").split("\n      - ")[1]

        self.assertIn("slugify-label", invoking_turn(LIVE_CASE))
        plan = invoking_turn("plan")
        # The directory as its own argument: it is a substring of the `prd.md`
        # obligation beside it, so bare containment would pass on a turn that
        # names no PRD source for the skill to plan from.
        self.assertIn("docs/specs/amount-filter\n", plan)
        for needle in ("independently executable", "docs/specs/amount-filter/prd.md"):
            self.assertIn(needle, plan)
        # Returning the path may come after, but a turn has to ask for it or the
        # step's declared `plan` output is never written.
        self.assertIn("plan.json", cases.read_text(
            cases.CASES_DIR / "plan" / "subject-workflow.yaml"))

    # Six of the cases carrying an oracle are driven here, for what no check.json
    # key can assert: a state transition, a branch's isolation, an annotated fix,
    # a deferral filed exactly once.
    # Each is staged from the real case and driven through the states around its
    # end state - the tree as staged, the end state a correct subject would leave,
    # and a deliberate break on top - because an oracle that only ever fails is
    # one nothing can satisfy, and one that only ever passes is one nothing can
    # fail.

    def stage_case(self, name):
        """The real case in a fresh run directory: the starting tree as one commit
        with any dirty/ copied over it, which is the tree the evaluator hands an
        oracle."""
        run = self.tmp / ("run-" + name)
        run.mkdir()
        return stage.stage_workspace(run, cases.CASES_DIR / name)

    def run_oracle(self, case, workspace):
        """Through the interpreter and from the workspace, the boundary the
        evaluator crosses when it runs an oracle."""
        return subprocess.run([sys.executable, str(cases.CASES_DIR / case / "oracle.py")],
                              cwd=str(workspace), capture_output=True, text=True)

    def commit(self, tree, message, *paths):
        stage.git(tree, "add", *paths)
        stage.git(tree, *(stage.IDENTITY + ("commit", "-q", "-m", message)))

    def edit_story(self, plan_path, story_id="S01", **fields):
        """One story record of a plan.json rewritten in place. Every FIS is a
        plan story (ADR-013), so this is the single state shape each journey
        oracle reads, and driving it here is how both directions are proved."""
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        next(s for s in plan["stories"] if s["id"] == story_id).update(fields)
        plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    def reentry_fis(self, workspace, body):
        """The FIS a re-entry leaves: the staged one with the settled policy
        integrated into the prose in place of its backoff assumption. Rebuilt from
        the overlay every time, so each wording starts from the same staged FIS
        rather than from the last one written."""
        staged = (cases.CASES_DIR / "spec-reentry" / "overlay" / "docs"
                  / "specs" / "retry-policy" / "s01-retry-policy.md")
        lines = staged.read_text(encoding="utf-8").splitlines(True)
        path = workspace / "docs" / "specs" / "retry-policy" / "s01-retry-policy.md"
        stage.write(path, "".join(body if REENTRY_MARKER + ":" in line else line
                                  for line in lines))
        return path

    def test_spec_reentry_oracle_reads_the_policy_by_meaning_not_by_wording(self):
        """Re-entry is the settled policy carried in the FIS and the staged legacy
        `blocked` story rewritten `spec-ready` in the record beside it, and this
        oracle reads both - the record because it is the state the next skill reads.

        The policy is read by meaning: a FIS that wrote `0.2 s` and `2 ** attempt`
        settled exactly what one that wrote `200 ms` and `doubling` did, and a
        literal needle for either spends a live run failing the other. What it must
        still catch is a term dropped, the backoff still assumed beside the decision,
        a retired marker written back, and a story left `blocked`."""
        workspace = self.stage_case("spec-reentry")
        plan_path = workspace / "docs" / "specs" / "retry-policy" / "plan.json"

        done = self.run_oracle("spec-reentry", workspace)
        self.assertEqual(1, done.returncode)
        for missing in ("200 ms base", "doubling growth", "3-retry maximum",
                        REENTRY_MARKER, "status is 'blocked'"):
            self.assertIn(missing, done.stderr)

        self.edit_story(plan_path, "S01", status="spec-ready")
        for body in REENTRY_WORDINGS:
            self.reentry_fis(workspace, body)
            done = self.run_oracle("spec-reentry", workspace)
            self.assertEqual(0, done.returncode, done.stderr)

        fis = self.reentry_fis(workspace, REENTRY_WORDINGS[0].replace("3 retries", "retries"))
        done = self.run_oracle("spec-reentry", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("3-retry maximum", done.stderr)

        for regressed, named in (
                ("  - ASSUMPTION: keep the fixed pause – the decision would change it\n",
                 REENTRY_MARKER),
                ("MISSING REQUIREMENT: the backoff policy is undecided\n",
                 "MISSING REQUIREMENT"),
                ("Closure: READY\n", "Closure verdict line")):
            stage.write(fis, REENTRY_WORDINGS[0] + regressed)
            done = self.run_oracle("spec-reentry", workspace)
            self.assertEqual(1, done.returncode, regressed)
            self.assertIn(named, done.stderr)

        self.reentry_fis(workspace, REENTRY_WORDINGS[0])
        self.edit_story(plan_path, "S01", status="blocked")
        done = self.run_oracle("spec-reentry", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("status is 'blocked'", done.stderr)

    def spec_end_state(self, workspace, fresh=True, body=CURRENT_FIS, **story):
        """The state a clean `andthen:spec` run leaves: the FIS, the one-story
        plan beside it (ADR-013), and the self-review's evidence."""
        spec = workspace / "docs" / "specs" / "label-slug"
        stage.write(spec / "s01-slugify-label.md",
                    "# Slugify Label\n\n**Plan**: docs/specs/label-slug/plan.json\n"
                    "**Story-ID**: S01\n\n" + body)
        stage.write(spec / "plan.json", json.dumps({"schemaVersion": "2", "stories": [dict(
            {"id": "S01", "status": "spec-ready", "completedTaskIds": [],
             "fis": "s01-slugify-label.md"}, **story)]}, indent=2) + "\n")
        stage.write(workspace / "review-evidence.json", json.dumps(
            {"freshContext": fresh, "remediated": False}) + "\n")

    def test_spec_oracle_reads_the_end_state_and_the_fresh_review(self):
        """The run ends on its next command, not a grade, so the oracle binds what
        the next skill reads - the FIS and its spec-ready story - plus evidence
        that a fresh-context reviewer, not the author, read the FIS."""
        workspace = self.stage_case("spec")
        done = self.run_oracle("spec", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("s01-slugify-label.md", done.stderr)

        self.spec_end_state(workspace)
        done = self.run_oracle("spec", workspace)
        self.assertEqual(0, done.returncode, done.stderr)

        # The author reviewing its own output is no review.
        self.spec_end_state(workspace, fresh=False)
        done = self.run_oracle("spec", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("freshContext is False", done.stderr)

        # Nothing writes the retired `blocked` status; a spec that does fails.
        self.spec_end_state(workspace, status="blocked")
        done = self.run_oracle("spec", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("expected 'spec-ready'", done.stderr)

        (workspace / "docs" / "specs" / "label-slug" / "plan.json").unlink()
        done = self.run_oracle("spec", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("plan.json", done.stderr)

    def test_spec_oracle_fails_a_fis_carrying_a_retired_surface(self):
        """Nothing a check.json key or the size ceiling sees fails a spec that
        regressed to the retired template or closed on a verdict: the FIS still
        validates, stays small, and hands off. Each retired surface fails alone,
        and the current headings that share a word with one - `Final Validation
        Checklist` - pass, or the check fails every correct FIS."""
        workspace = self.stage_case("spec")
        self.spec_end_state(workspace)
        done = self.run_oracle("spec", workspace)
        self.assertEqual(0, done.returncode, done.stderr)

        for line, named in RETIRED_FIS:
            self.spec_end_state(workspace, body=CURRENT_FIS + line)
            done = self.run_oracle("spec", workspace)
            self.assertEqual(1, done.returncode, line)
            self.assertIn(named, done.stderr)

    def test_spec_oracle_fails_a_fis_carrying_an_open_marker(self):
        """The shipped FIS carries the answer or an ASSUMPTION: where it bites,
        never the open question itself: a
        resolved ASSUMPTION: line passes, but a CONFUSION: or MISSING
        REQUIREMENT: marker left in place fails."""
        workspace = self.stage_case("spec")
        self.spec_end_state(workspace, body=CURRENT_FIS + RESOLVED_ASSUMPTION)
        done = self.run_oracle("spec", workspace)
        self.assertEqual(0, done.returncode, done.stderr)

        for line in OPEN_MARKER_FIS:
            self.spec_end_state(workspace, body=CURRENT_FIS + line)
            done = self.run_oracle("spec", workspace)
            self.assertEqual(1, done.returncode, line)
            self.assertIn("open marker", done.stderr)

    def test_plan_oracle_reads_every_fis_the_bundle_wrote(self):
        """The plan case writes a FIS per story, and a regression can land in any
        one of them: the oracle reads each FIS the plan points at, so a retired
        surface in the last story fails the bundle as surely as one in the first."""
        workspace = self.stage_case("plan")
        spec = workspace / "docs" / "specs" / "amount-filter"
        stories = ("S01", "s01-parse-amount.md"), ("S02", "s02-filter-by-amount.md")

        def bundle(last_body):
            stage.write(spec / "plan.json", json.dumps({"schemaVersion": "2", "stories": [
                {"id": sid, "status": "spec-ready", "completedTaskIds": [], "fis": name}
                for sid, name in stories]}, indent=2) + "\n")
            for index, (sid, name) in enumerate(stories):
                stage.write(spec / name,
                            "# Story\n\n**Plan**: docs/specs/amount-filter/plan.json\n"
                            "**Story-ID**: %s\n\n%s" % (
                                sid, last_body if index == len(stories) - 1 else CURRENT_FIS))

        bundle(CURRENT_FIS)
        done = self.run_oracle("plan", workspace)
        self.assertEqual(0, done.returncode, done.stderr)

        for line, named in RETIRED_FIS:
            bundle(CURRENT_FIS + line)
            done = self.run_oracle("plan", workspace)
            self.assertEqual(1, done.returncode, line)
            self.assertIn(named, done.stderr)
            self.assertIn(stories[-1][1], done.stderr)

    def test_implement_fix_oracle_accepts_an_annotated_fix_and_rejects_the_rest(self):
        """A remediated report is judged by the code and the annotation together:
        the fix has to land in src/reporter/pipeline.py and the report has to say
        so, once.
        A fix without the status section, a header without the remediated marker,
        a second section, and a status that contradicts the code are each broken
        in turn."""
        workspace = self.stage_case("implement-fix")
        done = self.run_oracle("implement-fix", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("'## Remediation Status' section(s), expected exactly 1", done.stderr)
        self.assertIn("build_label wrote", done.stderr)

        report = workspace / "plan-gap-review-claude-2026-09-05.md"
        original = report.read_text(encoding="utf-8")
        # The app's own module is the fix: the overlay replaced it with the
        # variant F1 describes, so restoring it is exactly the bounded repair.
        shutil.copy2(str(stage.SUBJECT / "src" / "reporter" / "pipeline.py"),
                     str(workspace / "src" / "reporter" / "pipeline.py"))
        status = ("\n## Remediation Status\n\n- **Finding 1 - build_label reads a module-level "
                  "copy of the seed** - RESOLVED - build_label reads seed.txt and normalizes "
                  "it; tests.test_pipeline green.\n")
        report.write_text(original + status, encoding="utf-8")
        done = self.run_oracle("implement-fix", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("0 '**Remediated**:' line(s) in the header", done.stderr)

        # The marker counts only in the header, where a reader meets it before the verdict.
        marker = "**Remediated**: fixes applied after this verdict – see `## Remediation Status`\n"
        report.write_text(original + status + marker, encoding="utf-8")
        done = self.run_oracle("implement-fix", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("0 '**Remediated**:' line(s) in the header", done.stderr)

        original = original.replace("\n\nIntent Context:", "\n" + marker + "\nIntent Context:", 1)
        self.assertIn(marker, original)
        report.write_text(original + status, encoding="utf-8")
        done = self.run_oracle("implement-fix", workspace)
        self.assertEqual(0, done.returncode, done.stderr)

        report.write_text(original + status + status, encoding="utf-8")
        done = self.run_oracle("implement-fix", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("2 '## Remediation Status' section(s)", done.stderr)

        report.write_text(original + status.replace("- RESOLVED -", "- UNRESOLVED -"),
                          encoding="utf-8")
        done = self.run_oracle("implement-fix", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("does not state Finding 1 RESOLVED", done.stderr)

        # The pre-template `F1:` key is not the contract's, so a bullet keyed that way is unread.
        report.write_text(original + status.replace("**Finding 1 - ", "F1: **"), encoding="utf-8")
        done = self.run_oracle("implement-fix", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("does not state Finding 1 RESOLVED", done.stderr)

    def test_exec_plan_worktree_oracle_needs_both_stories_done_on_executed_proof(self):
        """Two stories ran in parallel worktrees; the checks read the merged tree and
        the git shape, and this oracle reads the two story rows - each done, its one
        task recorded, and a verified record the run session wrote. Staged, both are
        spec-ready; both completed passes; one story left behind fails by name."""
        workspace = self.stage_case("exec-plan-worktree")
        plan = workspace / "docs" / "specs" / "run-summary" / "plan.json"
        done = self.run_oracle("exec-plan-worktree", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("story S01 status is 'spec-ready', expected 'done'", done.stderr)
        self.assertIn("story S02 status is 'spec-ready', expected 'done'", done.stderr)

        verified = {"at": "2026-09-16T10:00Z", "summary": "fast tier exit 0"}
        for story_id in ("S01", "S02"):
            self.edit_story(plan, story_id, status="done", completedTaskIds=["TI01"],
                            verified=verified)
        done = self.run_oracle("exec-plan-worktree", workspace)
        self.assertEqual(0, done.returncode, done.stderr)

        self.edit_story(plan, "S02", status="in-progress", completedTaskIds=[])
        doc = json.loads(plan.read_text(encoding="utf-8"))
        next(s for s in doc["stories"] if s["id"] == "S02").pop("verified")
        plan.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        done = self.run_oracle("exec-plan-worktree", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("story S02 has no verified record", done.stderr)
        self.assertNotIn("S01", done.stderr)
        self.assertIn("story S02 status is 'in-progress', expected 'done'", done.stderr)

    def test_spike_isolation_oracle_accepts_a_contained_spike_and_rejects_a_leaked_one(self):
        """The spike's evidence is a branch of its own; the caller checkout keeps
        its branch, its dirty edit, and its untracked note. A spike branch is
        built through a real worktree because that is the only way a commit lands
        on it without touching the caller tree - and the break is a commit on
        that same branch touching a caller file, which no path check would see."""
        workspace = self.stage_case("spike-isolation")
        done = self.run_oracle("spike-isolation", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("no spike/* branch", done.stderr)

        tree = self.tmp / "spike-worktree"
        stage.git(workspace, "worktree", "add", "-q", str(tree), "-b", "spike/csv-writer")
        stage.write(tree / "spike.py", "import csv\n\n\ndef render(rows):\n    return rows\n")
        self.commit(tree, "spike: csv writer timing", "spike.py")
        stage.git(workspace, "worktree", "remove", str(tree))
        done = self.run_oracle("spike-isolation", workspace)
        self.assertEqual(0, done.returncode, done.stderr)

        leak = self.tmp / "spike-worktree-leak"
        stage.git(workspace, "worktree", "add", "-q", str(leak), "spike/csv-writer")
        stage.write(leak / "src" / "reporter" / "cli.py",
                    "def main(argv=None):\n"
                    "    return 0  # the spike edited a caller file\n")
        self.commit(leak, "spike: edit a caller file", "src/reporter/cli.py")
        stage.git(workspace, "worktree", "remove", str(leak))
        done = self.run_oracle("spike-isolation", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("spike/csv-writer carries src/reporter/cli.py", done.stderr)

    def test_implement_fix_deferred_oracle_accepts_a_filed_deferral_and_rejects_the_rest(self):
        """A finding whose repair encodes an open decision is filed, not fixed: the
        module untouched, one backlog entry naming what was deferred and what
        blocks it, the report recording DEFERRED. Each mark is broken in turn, and
        the backlog both ways - no entry and a second one - because a pass that
        files its own observations beside the deferral leaves a file that is
        present either way."""
        workspace = self.stage_case("implement-fix-deferred")
        backlog = workspace / "docs" / "TECH-DEBT-BACKLOG.md"
        report = workspace / "retry-code-review-claude-2026-09-12.md"
        retry = workspace / "src" / "reporter" / "retry.py"
        empty_backlog = backlog.read_text(encoding="utf-8")
        unannotated = report.read_text(encoding="utf-8")
        untouched_retry = retry.read_text(encoding="utf-8")

        done = self.run_oracle("implement-fix-deferred", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("0 new entries", done.stderr)
        self.assertIn("'## Remediation Status' section(s), expected exactly 1", done.stderr)

        entry = ("- **A blocked report write waits a flat second five times** - "
                 "`retry.retry` pauses `PAUSE_SECONDS` unchanged at "
                 "`src/reporter/retry.py:5-6`. Deferred because decision needed: the "
                 "retry backoff in `docs/DECISIONS.md` stays open pending a "
                 "measurement. Source: retry-code-review-claude-2026-09-12.md.\n")
        status = ("\n## Remediation Status\n\n- **The retry policy is a flat one-second "
                  "pause five times** - DEFERRED - blocker: decision needed; the backoff "
                  "decision is open, entry filed in docs/TECH-DEBT-BACKLOG.md.\n")
        backlog.write_text(empty_backlog + entry, encoding="utf-8")
        report.write_text(unannotated + status, encoding="utf-8")
        done = self.run_oracle("implement-fix-deferred", workspace)
        self.assertEqual(0, done.returncode, done.stderr)

        retry.write_text(untouched_retry.replace("PAUSE_SECONDS = 1.0",
                                                 "PAUSE_SECONDS = 0.25"), encoding="utf-8")
        done = self.run_oracle("implement-fix-deferred", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("src/reporter/retry.py: changed", done.stderr)
        retry.write_text(untouched_retry, encoding="utf-8")

        backlog.write_text(empty_backlog + entry
                           + entry.replace("A blocked report write", "A second thought"),
                           encoding="utf-8")
        done = self.run_oracle("implement-fix-deferred", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("2 new entries", done.stderr)

        backlog.write_text(empty_backlog + entry, encoding="utf-8")
        report.write_text(unannotated + status.replace("DEFERRED", "RESOLVED"),
                          encoding="utf-8")
        done = self.run_oracle("implement-fix-deferred", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("does not record the finding DEFERRED", done.stderr)


    def test_architecture_oracle_weighs_three_options_by_meaning_not_by_wording(self):
        """The request names three options and a report carrying two has not run
        the trade-off - but which words name them is the author's, and `constant
        sleep` weighs exactly what `fixed pause` does. Two faithful vocabularies
        pass; each option struck from the report fails, naming that option."""
        workspace = self.stage_case("architecture")
        report = workspace / "docs" / "architecture-report.md"

        done = self.run_oracle("architecture", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("no docs/architecture-report.md", done.stderr)

        wordings = (
            ["The shipped fixed pause recovers nothing a held file does not release.",
             "A capped growing backoff spends the same budget over more attempts.",
             "A lock-file handshake waits on the holder instead of pausing."],
            ["Option A keeps the constant sleep, unchanged since it went out.",
             "Option B doubles the wait each attempt up to a ceiling.",
             "Option C takes a lockfile from the program holding the report."],
        )
        for lines in wordings:
            stage.write(report, "# Retry recovery options\n\n" + "\n".join(lines) + "\n")
            done = self.run_oracle("architecture", workspace)
            self.assertEqual(0, done.returncode, done.stderr)

        for dropped, option in enumerate(("the shipped fixed pause",
                                          "the capped growing backoff",
                                          "the lock-file handshake")):
            kept = [line for i, line in enumerate(wordings[0]) if i != dropped]
            stage.write(report, "# Retry recovery options\n\n" + "\n".join(kept) + "\n")
            done = self.run_oracle("architecture", workspace)
            self.assertEqual(1, done.returncode)
            self.assertIn("does not weigh %s" % option, done.stderr)

    def test_clarify_oracle_reads_the_scripted_replies_by_meaning_not_by_wording(self):
        """Three scripted replies leave a mark in the PRD - the rejected
        alternative, the boundary, the question left open - and the words each is
        recorded in are the author's: `their own output` rejects the same
        alternative `a second file` does. Whether the replies survive without
        invention is the rubric's, so what this must catch is a reply with no mark
        at all."""
        workspace = self.stage_case("clarify")
        prd = workspace / "docs" / "specs" / "report-totals" / "prd.md"

        done = self.run_oracle("clarify", workspace)
        self.assertEqual(1, done.returncode)
        self.assertIn("no docs/specs/report-totals/prd.md", done.stderr)

        wordings = (
            ["Totals are appended to the report; a second file was rejected.",
             "A per-period breakdown is out of scope.",
             "Whether totals are produced by default is unresolved."],
            ["Writing them to their own output was weighed and dropped.",
             "Totals broken down by month stay outside this release.",
             "Open: are the totals emitted automatically, or behind a flag?"],
        )
        for lines in wordings:
            stage.write(prd, "# Report totals\n\n" + "\n".join(lines) + "\n")
            done = self.run_oracle("clarify", workspace)
            self.assertEqual(0, done.returncode, done.stderr)

        for dropped, reply in enumerate(("the rejected second-file alternative",
                                         "the per-period breakdown held out of scope",
                                         "the default-production question left open")):
            kept = [line for i, line in enumerate(wordings[0]) if i != dropped]
            stage.write(prd, "# Report totals\n\n" + "\n".join(kept) + "\n")
            done = self.run_oracle("clarify", workspace)
            self.assertEqual(1, done.returncode)
            self.assertIn("does not record %s" % reply, done.stderr)


class ValidatePlanScriptTest(unittest.TestCase):
    """`validate_plan.py` is a script that shells out from a case's `check.json`
    exactly as `_run` in `checks.py` invokes it (TESTING-STRATEGY.md's
    integration level: a script driven end to end via `subprocess`, real files,
    real exit codes) - a unit test importing its function would prove the
    import, not the contract a check actually depends on. `ops.py` carried its
    own suite; this is the one committed fixture and one broken copy that prove
    its replacement still recognizes a valid plan and still fails loudly on a
    malformed one."""

    FIXTURE = pathlib.Path("scripts/fixtures/renders/plan.json")

    def run_validator(self, plan_path):
        return subprocess.run(
            [sys.executable, str(cases.REPO_ROOT / "evals" / "validate_plan.py"), str(plan_path)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def test_the_committed_fixture_plan_validates(self):
        done = self.run_validator(cases.REPO_ROOT / self.FIXTURE)
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertIn("OK:", done.stdout)

    def test_a_plan_with_stories_replaced_by_a_string_is_rejected(self):
        doc = json.loads((cases.REPO_ROOT / self.FIXTURE).read_text(encoding="utf-8"))
        doc["stories"] = "not a list"
        with tempfile.TemporaryDirectory() as tmp:
            broken = pathlib.Path(tmp) / "plan.json"
            broken.write_text(json.dumps(doc), encoding="utf-8")
            done = self.run_validator(broken)
        self.assertEqual(1, done.returncode)
        self.assertIn("ERROR:", done.stderr)

    def test_a_plan_whose_story_ids_collide_is_rejected(self):
        """Per-field uniqueness is the one invariant `plan.schema.json` cannot
        express, so a second `S01` passes every shape check while each row
        write and dependency edge resolves to whichever row came first - the
        corruption a run leaves behind and this check exists to catch."""
        doc = json.loads((cases.REPO_ROOT / self.FIXTURE).read_text(encoding="utf-8"))
        collider = dict(doc["stories"][1], id=doc["stories"][0]["id"])
        doc["stories"] = [doc["stories"][0], collider]
        with tempfile.TemporaryDirectory() as tmp:
            colliding = pathlib.Path(tmp) / "plan.json"
            colliding.write_text(json.dumps(doc), encoding="utf-8")
            done = self.run_validator(colliding)
        self.assertEqual(1, done.returncode)
        self.assertIn("duplicate story id(s) ['S01']", done.stderr)

    def test_a_done_story_without_verified_or_fis_is_rejected(self):
        """A `done` story is the record that a run finished and what it finished
        against; the schema's `if/then` ties both to `status: done`, so dropping
        `verified` or nulling `fis` must fail loudly rather than validate as a
        plan a run can trust."""
        doc = json.loads((cases.REPO_ROOT / self.FIXTURE).read_text(encoding="utf-8"))
        no_verified = dict(doc, stories=[dict(doc["stories"][0]), *doc["stories"][1:]])
        del no_verified["stories"][0]["verified"]
        with tempfile.TemporaryDirectory() as tmp:
            missing = pathlib.Path(tmp) / "plan.json"
            missing.write_text(json.dumps(no_verified), encoding="utf-8")
            done = self.run_validator(missing)
        self.assertEqual(1, done.returncode)
        self.assertIn("missing required field 'verified'", done.stderr)

        null_fis = dict(doc, stories=[dict(doc["stories"][0]), *doc["stories"][1:]])
        null_fis["stories"][0]["fis"] = None
        with tempfile.TemporaryDirectory() as tmp:
            nulled = pathlib.Path(tmp) / "plan.json"
            nulled.write_text(json.dumps(null_fis), encoding="utf-8")
            done = self.run_validator(nulled)
        self.assertEqual(1, done.returncode)
        self.assertIn("plan.stories[0].fis", done.stderr)


class RunnerTest(unittest.TestCase):
    """Who a cell blames
    after dispatch, and what a maintainer can open afterwards. Every assertion
    drives run.py itself: stage.dispatch and stage.preflight stand in for the two
    halves that cost money, the run directory is redirected because a cell under
    the evidence root reads as a maintainer's own run, and nothing else is
    doubled - a fix proved against a re-implementation is not proved."""

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, str(self.tmp), True)

    def make_case(self, check, overlay=None, fixture=True):
        """`fixture/` is a whole workspace, `overlay/` a patch over the vendored
        app, and neither directory is that app unchanged; a case carries at most
        one, which is what validation and staging both key on."""
        case = pathlib.Path(tempfile.mkdtemp(dir=str(self.tmp))) / "synthetic"
        if overlay is not None:
            write_tree(case / "overlay", overlay)
        elif fixture:
            (case / "fixture").mkdir(parents=True)
            (case / "fixture" / "seed.md").write_text("seed\n", encoding="utf-8")
        else:
            case.mkdir(parents=True)
        for name, text in (("prompt.md", "do the thing\n"),
                           ("subject-workflow.yaml", SUBJECT_WORKFLOW),
                           ("check.json", json.dumps(check)),
                           ("rubric.json", json.dumps(
                               {"criteria": [{"id": "C1", "intent": "it works"}]}))):
            (case / name).write_text(text, encoding="utf-8")
        return case

    def run_dir(self):
        path = pathlib.Path(tempfile.mkdtemp(dir=str(self.tmp))) / "run"
        path.mkdir()
        (path / "data").mkdir()
        return path

    def context(self, run, data):
        stage.write(run / "data" / "workflows" / "runs" / "r1" / "context.json",
                    json.dumps({"data": data}))

    def drive(self, check, subject=lambda workspace: None, record=record(),
              outputs=None, dispatched=None, judge=None, kv=None):
        """One cell through run.run_cell. `subject` leaves behind what the
        dispatched subject would have, `outputs` is the context it wrote, `judge`
        is how the judge step settled (`answer`, and `status`/`session` when they
        are not the accepted defaults), and `kv` is DartClaw's cost ledger. The
        checks step runs for real inside the double - it is a step of the
        dispatched run, so doubling it as well would prove the runner against a
        re-implementation."""
        case = self.make_case(check)

        def dispatch(run, provider, config, name, workspace, variables):
            stage.write(run / "stdout.jsonl", record)
            stage.write(run / "stderr.log", "")
            if kv is not None:
                stage.write(run / "data" / "kv.json", json.dumps(kv))
            data = dict(outputs or {})
            self.context(run, data)
            subject(workspace)
            with contextlib.redirect_stderr(io.StringIO()):
                refused = step.main(["--case", str(variables["case_dir"]),
                                     "--run", str(variables["run_dir"])])
            if not refused and judge is not None:
                data.update({"judge.status": judge.get("status", "accepted"),
                             "judge.sessionId": judge.get("session", "s-judge"),
                             "judge_result": judge["answer"]})
                self.context(run, data)
            return dispatched or {"exitCode": 2 if refused else 0, "timedOut": False}

        with mock.patch.object(cases, "CASES_DIR", case.parent), \
                mock.patch.object(stage, "new_run_dir", lambda c, p: self.run_dir()), \
                mock.patch.object(stage, "preflight", lambda providers: ""), \
                mock.patch.object(stage, "dispatch", dispatch):
            return runner.run_cell("synthetic", "claude", "default", PROFILE)

    def test_candidate_satisfies_its_manifests(self):
        """The staged manifests are what registers the candidate for Codex, and a
        manifest naming a plugin source that is not under candidate/ registers
        nothing. Gate 0's Codex attempts failed exactly there."""
        run = self.run_dir()
        stage.stage_candidate(run)
        candidate = run / "candidate"
        claude = cases.load_json(candidate / ".claude-plugin" / "marketplace.json")[0]
        codex = cases.load_json(candidate / ".agents" / "plugins" / "marketplace.json")[0]
        sources = ([p["source"] for p in claude["plugins"]]
                   + [p["source"]["path"] for p in codex["plugins"]])
        self.assertTrue(sources)
        for source in sources:
            self.assertTrue((candidate / source).is_dir(), source)

        # Registration enables the one plugin and materializes it in the Codex
        # cache, where DartClaw looks; staging its files alone evaluates nothing.
        # A Claude cell gets whichever plugins the operator has enabled.
        stage.register_codex(run)
        config = (run / "data" / "credentials" / "codex" / "config.toml").read_text(encoding="utf-8")
        self.assertIn('[plugins."andthen@andthen"]', config)
        self.assertIn('[projects."', config)
        cache = run / "data" / "credentials" / "codex" / "plugins" / "cache" / "andthen"
        self.assertTrue(next((cache / "andthen").iterdir())
                        .joinpath("skills", "spec", "SKILL.md").is_file())

    def test_both_role_defaults_and_both_providers_are_configured(self):
        """Every subject workflow pins `@workflow` and the appended tail pins
        `@reviewer`; both default to claude inside DartClaw regardless of
        agent.provider, so a Codex cell crashed before its first step wiring a
        provider the config never declared. One run carries both steps, so a
        judge on the other provider has to be declared beside the subject's."""
        run = self.run_dir()
        stage.write_config(run / "dartclaw.yaml", run, run / "workspace",
                           {"provider": "codex", "model": "gpt-5.6-luna", "effort": "high"},
                           {"provider": "claude", "model": "claude-opus-5",
                            "effort": "medium"})
        config = (run / "dartclaw.yaml").read_text(encoding="utf-8")
        for wanted in ("    workflow:\n      provider: codex\n",
                       "    reviewer:\n      provider: claude\n",
                       "  codex:\n", "  claude:\n"):
            self.assertIn(wanted, config)
        self.assertIn("        - %s\n" % (run / stage.REQUEST).parent, config)
        # The turn ceiling is the subject's, not the cell's wall: one dispatch
        # carries the tail too, so a config that wrote the wall here would let a
        # single subject turn spend the budget the checks and the judge need.
        self.assertIn("turn_timeout: %d\n" % stage.TURN_TIMEOUT, config)
        self.assertLess(stage.TURN_TIMEOUT, stage.TIMEOUT)

        # One provider block when the two roles share a provider, or DartClaw
        # parses a duplicate key.
        same = {"provider": "claude", "model": "claude-opus-5", "effort": "high"}
        stage.write_config(run / "dartclaw.yaml", run, run / "workspace", same, same)
        config = (run / "dartclaw.yaml").read_text(encoding="utf-8")
        self.assertEqual(1, config.count("\n  claude:\n"))
        self.assertNotIn("codex", config)

    def test_a_codex_cells_judge_step_gets_a_claude_wrapper(self):
        """The judge step spawns `claude` under the empty HOME dispatch_env gives
        a Codex cell, so the bare CLI would report `Not logged in`. A Codex cell's
        config names a wrapper script instead, which execs the real binary with
        the operator's HOME restored; a Claude cell still names the real binary,
        since it dispatches in the operator's own environment already."""
        run = self.run_dir()
        stage.write_config(run / "dartclaw.yaml", run, run / "workspace",
                           {"provider": "codex", "model": "gpt-5.6-luna", "effort": "high"},
                           {"provider": "claude", "model": "claude-opus-5",
                            "effort": "medium"})
        config = (run / "dartclaw.yaml").read_text(encoding="utf-8")
        wrapper = run / "claude"
        self.assertIn("  claude:\n    executable: %s\n    credentials_required: false\n"
                      % wrapper, config)
        self.assertTrue(wrapper.is_file())
        self.assertEqual(0o755, stat.S_IMODE(wrapper.stat().st_mode))
        exec_line = next(l for l in wrapper.read_text(encoding="utf-8").splitlines()
                         if l.startswith("exec "))
        self.assertIn("HOME=%s" % os.environ.get("HOME", ""), exec_line)

        # A Claude cell dispatches in the operator's own environment already, so
        # DartClaw's auth gate sees a real HOME and needs no bypass.
        stage.write_config(run / "dartclaw.yaml", run, run / "workspace",
                           {"provider": "claude", "model": "claude-opus-5", "effort": "high"},
                           {"provider": "claude", "model": "claude-opus-5", "effort": "high"})
        config = (run / "dartclaw.yaml").read_text(encoding="utf-8")
        self.assertIn("  claude:\n    executable: %s\n"
                      % (shutil.which("claude") or "claude"), config)
        self.assertNotIn("credentials_required", config)

    def test_a_claude_cell_dispatches_in_the_operators_own_environment(self):
        """What the corpus measures is the plugin as a user runs it, so a Claude
        cell hands DartClaw the parent environment whole: the operator's settings,
        memory, agents, MCP servers and installed candidate all reach the subject,
        and a redirected HOME would take every one of them away. Codex cannot
        follow - DartClaw builds the CODEX_HOME it pins from the operator's
        ~/.codex, so a Codex cell keeps its own HOME and the candidate it
        registered stands alone."""
        run = self.run_dir()
        self.assertEqual(dict(os.environ), stage.dispatch_env(run, "claude"))
        codex = stage.dispatch_env(run, "codex")
        self.assertEqual(str(run / "home"), codex["HOME"])
        self.assertEqual(str(run / "provider"), codex["CODEX_HOME"])

    def test_a_claude_cell_records_the_plugin_it_actually_ran(self):
        """Running in the operator's environment means running his installed
        plugin, not this working tree: a cell recorded `installedHead 2cd88e7`,
        an object that does not exist in this repo, while the install directory
        was byte-identical to the tree's plugin/. That sha is Claude Code's own
        bookkeeping, not this repo's, so staleness is decided by content: the
        install directory against the tree's plugin/, ignoring OS/lock files.
        The note fires only on a content mismatch or an unreadable manifest -
        never for Codex, whose cell registers a snapshot of the tree."""
        repo = pathlib.Path(tempfile.mkdtemp(dir=str(self.tmp)))
        source = repo / "plugin"
        (source / "skills").mkdir(parents=True)
        (source / "skills" / "a.md").write_text("alpha", encoding="utf-8")

        plugins = pathlib.Path(tempfile.mkdtemp(dir=str(self.tmp)))
        entry = {"scope": "user", "installPath": str(plugins / "cache" / "andthen"),
                 "gitCommitSha": "2cd88e7000000000000000000000000000000000"}
        stage.write(plugins / "installed_plugins.json", json.dumps(
            {"version": 2, "plugins": {"andthen@andthen": [entry],
                                       "other@elsewhere": [dict(entry, gitCommitSha="dead")]}}))

        # Identical content, extra OS/lock artifacts ignored: no note.
        install = pathlib.Path(entry["installPath"])
        (install / "skills").mkdir(parents=True)
        (install / "skills" / "a.md").write_text("alpha", encoding="utf-8")
        (install / ".DS_Store").write_text("junk", encoding="utf-8")
        (install / ".in_use").write_text("lock", encoding="utf-8")
        with mock.patch.object(stage, "CLAUDE_PLUGINS", plugins), \
             mock.patch.object(runner.cases, "REPO_ROOT", repo):
            candidate = runner._candidate()
        self.assertEqual(entry["gitCommitSha"], candidate["installedHead"])
        self.assertEqual(entry["installPath"], candidate["installPath"])
        self.assertTrue(candidate["installMatches"])
        cell = {"case": "spec", "provider": "claude", "candidate": candidate}
        self.assertIsNone(runner._install_note(cell))
        self.assertIsNone(runner._install_note(dict(cell, provider="codex")))

        # One differing byte: the note fires.
        (install / "skills" / "a.md").write_text("beta", encoding="utf-8")
        with mock.patch.object(stage, "CLAUDE_PLUGINS", plugins), \
             mock.patch.object(runner.cases, "REPO_ROOT", repo):
            candidate = runner._candidate()
        self.assertFalse(candidate["installMatches"])
        self.assertEqual(
            "installed plugin differs from the working tree's plugin/ - "
            "a Claude cell measures the install",
            runner._install_note(dict(cell, candidate=candidate)))

        # No manifest is not "the tree is what ran": it is not knowing.
        with mock.patch.object(stage, "CLAUDE_PLUGINS", plugins / "gone"), \
             mock.patch.object(runner.cases, "REPO_ROOT", repo):
            candidate = runner._candidate()
        self.assertIsNone(candidate["installedHead"])
        self.assertIsNone(candidate["installMatches"])
        self.assertEqual("installed plugin unknown",
                         runner._install_note(dict(cell, candidate=candidate)))

    def test_check_level_error_sets_error(self):
        """A check that could not run leaves result.json saying only
        ERROR, and a maintainer then pays a cell to learn which check it was.
        Nothing is judged either: the harness failed to evaluate this cell, so
        the checks step stops the run and no judge turn is spent on it."""
        cell, _ = self.drive({"commands": ["andthen-no-such-executable"]},
                             judge={"answer": JUDGE_PASS})
        self.assertEqual("ERROR", cell["outcome"])
        self.assertIn("commands[0]", cell["error"] or "")
        self.assertEqual([], cell["criteria"])
        self.assertIsNone(cell["judge"]["sessionId"])

        # A check that ran and failed is the subject's, and the judge still
        # weighed the workspace: the cell fails on the check alone.
        cell, _ = self.drive({"commands": ["exit 3"]}, judge={"answer": JUDGE_PASS})
        self.assertEqual("FAIL", cell["outcome"])
        self.assertIsNone(cell["error"])
        self.assertTrue(cell["criteria"][0]["pass"])

    def test_the_tail_is_appended_verbatim_to_the_cases_own_workflow(self):
        """One dispatch per cell is one definition, and the checks and judge steps
        are written once here rather than copied into every case. The only edit to
        the case's own text is the tolerance a subject's self-reported failure
        needs to still reach the checks: `onFailure` is a per-step field no
        `stepDefaults` entry carries, and a corpus that has to remember a harness
        line drifts from it. The tail's own script lines are held to DartClaw's
        substitution rule: it passes each {{...}} as one argument itself and
        refuses one inside shell quotes at run time ("command substitution
        failed"), a failure `dartclaw-workflow validate` does not catch."""
        case = self.make_case({})
        run = self.run_dir()
        stage.stage_workflows(run, case)
        staged = cases.read_text(run / "data" / "workflows" / "custom"
                                 / "subject-workflow.yaml")

        self.assertTrue(staged.endswith(cases.read_text(cases.TAIL_WORKFLOW)), staged)
        self.assertIn("  - id: s1\n" + stage.SELF_REPORT_TOLERANCE + "\n", staged)
        self.assertEqual("synthetic-subject", cases.workflow_name(
            run / "data" / "workflows" / "custom" / "subject-workflow.yaml"))
        for wanted in ("  - id: checks\n", "  - id: judge\n", "\nvariables:\n"):
            self.assertIn(wanted, staged)
        # Created empty, so the judge's provider can be granted it before any
        # step runs and the subject finds nothing in it.
        self.assertEqual([], list((run / stage.REQUEST).parent.iterdir()))

        for line in cases.read_text(cases.TAIL_WORKFLOW).splitlines():
            if line.strip().startswith("script:"):
                self.assertNotIn('"{{', line)
                self.assertNotIn("'{{", line)

    def test_a_checks_step_that_writes_no_results_is_error_not_a_crash(self):
        """The runtime failure this guards: the checks step's command never ran
        (e.g. DartClaw refused its substitutions), so checks.json is never
        written. cell["checks"] must land as [] rather than None, or _summary's
        `[c for c in cell["checks"] if ...]` raises TypeError instead of the
        cell reaching ERROR with a written summary.md."""
        case = self.make_case({})
        run = self.run_dir()

        def dispatch(run, provider, config, name, workspace, variables):
            stage.write(run / "stdout.jsonl", record())
            stage.write(run / "stderr.log", "checks: command substitution failed\n")
            self.context(run, {})
            # No step.main call: the checks step never ran, so checks.json is
            # never written - the condition run.py's error branch must cover.
            return {"exitCode": 1, "timedOut": False}

        with mock.patch.object(cases, "CASES_DIR", case.parent), \
                mock.patch.object(stage, "new_run_dir", lambda c, p: run), \
                mock.patch.object(stage, "preflight", lambda providers: ""), \
                mock.patch.object(stage, "dispatch", dispatch):
            cell, run_out = runner.run_cell("synthetic", "claude", "default", PROFILE)

        self.assertEqual("ERROR", cell["outcome"])
        self.assertEqual([], cell["checks"])
        self.assertIn("the checks step recorded no results", cell["error"])
        summary = (run_out / "summary.md").read_text(encoding="utf-8")
        self.assertIn("the checks step recorded no results", summary)

    def test_the_checks_step_writes_the_request_for_a_fail_but_not_an_error(self):
        """DartClaw stops a run at a bash step that exits nonzero, so this step's
        exit is what decides whether the judge step runs at all - and a check that
        failed still leaves a workspace worth weighing. The checks vetoing the
        judge is what left three live runs failing one wording check with no
        verdict beside it to say the case, not the skill, had moved. A check that
        could not run is the other case: the harness failed to evaluate the cell,
        so a judge turn would be spent on nothing. What the checks decided goes
        to the step's stderr, which DartClaw keeps in the run record as
        `checks.stderr`. The request never lands in the workspace: the rubric is
        what the case is measuring, and a subject that could read it could
        satisfy it without doing the work."""
        def evaluate(case_dir, run_dir):
            with contextlib.redirect_stderr(io.StringIO()) as log:
                code = step.main(["--case", str(case_dir), "--run", str(run_dir)])
            return code, log.getvalue()

        case = self.make_case({"requiredArtifacts": ["work.md"]})
        run = self.run_dir()
        workspace = stage.stage_workspace(run, case)
        code, log = evaluate(case, run)
        self.assertEqual(0, code)
        self.assertIn("checks: FAIL", log)
        self.assertEqual(checks.FAIL, cases.load_json(run / "checks.json")[0][0]["status"])
        self.assertEqual("C1", cases.load_json(
            run / stage.REQUEST)[0]["rubric"]["criteria"][0]["id"])

        stage.write(workspace / "work.md", "x\n")
        code, log = evaluate(case, run)
        self.assertEqual(0, code)
        self.assertIn("checks: PASS", log)
        self.assertEqual(checks.PASS, cases.load_json(run / "checks.json")[0][0]["status"])
        self.assertEqual([], [p for p in checks.workspace_files(workspace)
                              if "rubric" in p or "judge" in p])

        broken = self.make_case({"commands": ["andthen-no-such-executable"]})
        run = self.run_dir()
        stage.stage_workspace(run, broken)
        code, log = evaluate(broken, run)
        self.assertEqual(1, code)
        self.assertIn("checks: ERROR", log)
        self.assertEqual(checks.ERROR, cases.load_json(run / "checks.json")[0][0]["status"])
        self.assertFalse((run / stage.REQUEST).is_file())

        # A case this step cannot read at all: no results, no request, and the
        # nonzero exit stops the run before the judge is spent on nothing.
        unreadable = self.make_case({})
        (unreadable / "check.json").write_text("{ not json\n", encoding="utf-8")
        run = self.run_dir()
        stage.stage_workspace(run, unreadable)
        code, log = evaluate(unreadable, run)
        self.assertEqual(1, code)
        self.assertIn("check.json: not parseable JSON", log)
        self.assertFalse((run / "checks.json").is_file())
        self.assertFalse((run / stage.REQUEST).is_file())

    def test_a_failing_check_still_gets_a_verdict_and_still_fails_the_cell(self):
        """The cheapest layer must not veto the most valuable one: three live
        `spec-reentry` runs failed one wording check with the skill
        correct, and with no criteria beside it "the case is miscalibrated" and
        "the skill regressed" read identically. Criteria are not an appeal
        either - the cell passes only when checks and criteria both do - and the
        summary carries both sections so the pair can be read at a glance."""
        cell, run = self.drive(
            {"requiredText": {"work.md": ["a phrase the subject never wrote"]}},
            lambda workspace: stage.write(workspace / "work.md", "the widget trims\n"),
            judge={"answer": JUDGE_PASS})

        self.assertEqual("FAIL", cell["outcome"])
        self.assertIsNone(cell["error"])
        self.assertEqual(checks.FAIL, cell["checks"][0]["status"])
        self.assertEqual([True], [d["pass"] for d in cell["criteria"]])
        summary = (run / "summary.md").read_text(encoding="utf-8")
        self.assertIn("## Criteria", summary)
        self.assertIn("- C1 pass: the work is there", summary)
        self.assertIn("requiredText[0] fail:", summary)
        # The row says why without opening the cell.
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            runner._report([(cell, None)], 1.0)
        self.assertIn("| FAIL |", stdout.getvalue())
        self.assertIn("requiredText[0] fail:", stdout.getvalue().splitlines()[1])

    def judge(self, answer, work="the widget trims whitespace\n", outputs=None,
              judge_session="s-judge", subject_session="s-subject", kv=None):
        """One cell whose subject left `work.md` saying `the widget trims
        whitespace` and whose judge step answered `answer`; that text and any
        declared `outputs` are the only retained material a PASS may quote."""
        data = {"s1.status": "completed", "s1.sessionId": subject_session}
        data.update(outputs or {})
        return self.drive(
            {}, lambda workspace: stage.write(workspace / "work.md", work),
            record=record({"s1": tuple(outputs or ()), "checks": (),
                           "judge": ("judge_result",)}, ("s1", "judge")),
            outputs=data, judge={"answer": answer, "session": judge_session}, kv=kv)

    def test_a_pass_needs_a_reason_and_evidence_from_the_retained_material(self):
        """E1 - `{"pass": true, "evidence": "", "reason": ""}` was accepted and
        the cell derived PASS from the booleans. Unsupported output is ERROR,
        never a verdict. The rule binds a pass only: a FAIL on an absence has no
        line to quote and still has to be expressible."""
        grounded = {"decisions": [{"id": "C1", "pass": True, "reason": "it trims",
                                   "evidence": "the widget trims whitespace"}]}
        for bad in ({"decisions": [{"id": "C1", "pass": True, "reason": "", "evidence": ""}]},
                    {"decisions": [{"id": "C1", "pass": True, "reason": "it trims",
                                    "evidence": "the widget also lowercases"}]},
                    {"decisions": [{"id": "C1", "pass": True, "reason": "it trims"}]}):
            with self.subTest(bad=bad):
                cell, _ = self.judge(bad)
                self.assertEqual("ERROR", cell["outcome"])
                self.assertIn("quoted from the retained subject material", cell["error"])
                self.assertEqual([], cell["criteria"])
        cell, run = self.judge(grounded)
        self.assertEqual("PASS", cell["outcome"], cell["error"])
        # The answer a maintainer opens is beside the request it answered.
        self.assertEqual(grounded, cases.load_json(run / "judge-result.json")[0])

        absent = {"decisions": [{"id": "C1", "pass": False,
                                 "reason": "no artifact names the lowercase rule",
                                 "evidence": "no line in work.md mentions lowercasing"}]}
        cell, _ = self.judge(absent)
        self.assertEqual("FAIL", cell["outcome"])
        self.assertFalse(cell["criteria"][0]["pass"])
        # An absence is still stated: a FAIL that says nothing is unusable too.
        silent = {"decisions": [{"id": "C1", "pass": False, "reason": "", "evidence": ""}]}
        self.assertEqual("ERROR", self.judge(silent)[0]["outcome"])

    def test_the_judge_session_may_not_be_the_subjects_and_missing_ids_are_not_reuse(self):
        """The judge is a step of the subject's own run, so isolation is
        its own session: an id that comes back as the subject's says the boundary
        failed and the verdict is not independent. Ids the provider never
        recorded prove nothing either way."""
        grounded = {"decisions": [{"id": "C1", "pass": True, "reason": "it trims",
                                   "evidence": "the widget trims whitespace"}]}
        cell, _ = self.judge(grounded, judge_session="s-subject")
        self.assertEqual("ERROR", cell["outcome"])
        self.assertIn("reused the subject session 's-subject'", cell["error"])
        self.assertEqual([], cell["criteria"])
        cell, _ = self.judge(grounded, subject_session=None, judge_session=None)
        self.assertEqual("PASS", cell["outcome"], cell["error"])

    def test_a_judge_step_that_never_answered_is_not_a_judge_that_answered_badly(self):
        """The judge step can error, pause on a turn cap, or die with the dispatch,
        and then there is no output to parse. Reporting that as an unparseable
        answer names a defect that did not occur and sends a maintainer to a
        judge-result.json holding null; the step's status and the exit code are
        what say where to look."""
        passing = {"requiredArtifacts": ["work.md"]}

        def wrote(workspace):
            stage.write(workspace / "work.md", "x\n")

        cell, run = self.drive(passing, wrote)
        self.assertEqual("ERROR", cell["outcome"])
        self.assertEqual("the judge step recorded no status, dispatch exit 0; "
                         "see stderr.log", cell["error"])
        self.assertEqual([], cell["criteria"])
        self.assertFalse((run / "judge-result.json").is_file())

        # A settled failure is named as itself, and named before the decisions are
        # weighed: these are not decisions the judge could have produced.
        cell, _ = self.drive(passing, wrote,
                             judge={"answer": {"decisions": []}, "status": "failed"})
        self.assertEqual("ERROR", cell["outcome"])
        self.assertIn("the judge step settled 'failed'", cell["error"])

    def test_the_context_read_is_the_run_the_cell_dispatched(self):
        """A data dir that comes to hold a second record - a resume, a nested run -
        must not have another run's outputs weighed as this cell's, and a UUID sort
        gives no signal about which is which. The runner holds the id the event
        stream named; only the checks step, which reads this mid-run before any
        event has named it, falls back to the newest record."""
        run = self.run_dir()
        for name, verdict in (("r1", "the dispatched run"), ("r2", "another run")):
            stage.write(run / "data" / "workflows" / "runs" / name / "context.json",
                        json.dumps({"data": {"verdict": verdict}}))
        self.assertEqual({"verdict": "the dispatched run"}, stage.run_context(run, "r1"))
        self.assertEqual({"verdict": "another run"}, stage.run_context(run))

    def test_only_a_declared_output_is_material_the_judge_may_quote(self):
        """`outputs` is evidence a PASS has to quote from, so it carries what a
        step declared and nothing else: an output name is bare, DartClaw's
        per-step bookkeeping is `<id>.<field>` and its private entries are
        `_`-prefixed, and either one in the material is quotable ground for a
        verdict the subject never earned."""
        settled, outputs = stage.step_outputs({
            "s1.status": "completed", "s1.sessionId": "s-subject",
            "judge.status": "completed", "_internal": "bookkeeping",
            "report": "the finding"})
        self.assertEqual(["judge", "s1"], sorted(settled))
        self.assertEqual({"report": "the finding"}, outputs)

    def test_a_dirty_directory_starts_the_workspace_uncommitted(self):
        """A resumed story's earlier edits are dirty at session start; the
        committed fixture alone cannot stage that state."""
        case = self.make_case({})
        (case / "dirty").mkdir()
        (case / "dirty" / "seed.md").write_text("seed plus earlier work\n", encoding="utf-8")
        (case / "dirty" / "scratch.txt").write_text("untracked\n", encoding="utf-8")
        run = self.run_dir()
        workspace = stage.stage_workspace(run, case)
        status = stage.git(workspace, "status", "--porcelain")
        self.assertIn(" M seed.md", status)
        self.assertIn("?? scratch.txt", status)
        self.assertEqual("seed\n", stage.git(workspace, "show", "HEAD:seed.md"))
        # A fixture case is the whole workspace: the app is not laid down under it.
        self.assertFalse((workspace / "src" / "reporter").exists())
        # Planted and left alone is the starting state, not subject output;
        # planted and then edited is the subject's.
        stage.write(workspace / "scratch.txt", "untracked, then edited\n")
        changed, touched = stage.stage_diff(run, workspace)
        self.assertEqual(["scratch.txt"], changed)
        self.assertEqual(["scratch.txt"], touched)
        # Taking the diff staged everything; the checks that follow must see
        # the working tree the subject left, or an isolation oracle reads a
        # planted edit as staged by the subject.
        status = stage.git(workspace, "status", "--porcelain")
        self.assertIn(" M seed.md", status)
        self.assertIn("?? scratch.txt", status)

    def test_a_case_starts_from_the_vendored_app_under_whatever_it_adds(self):
        """The corpus has one starting project rather than one per case: a case
        carries what distinguishes it and the app supplies the rest, so a review
        has real code to look at and the Intent, Learnings and tech-debt anchors
        a skill reads are present in every cell. A case with nothing to add
        carries neither directory and gets the app itself - padding an overlay to
        satisfy a shape check would put a file in front of the subject that the
        case never wanted there."""
        case = self.make_case({}, overlay={
            "docs/LEARNINGS.md": "# Project Learnings\n\n- one trap\n"})
        (case / "dirty").mkdir()
        (case / "dirty" / "scratch.txt").write_text("untracked\n", encoding="utf-8")
        run = self.run_dir()
        workspace = stage.stage_workspace(run, case)

        # An app file no overlay carried, and the app's own replaced by the one
        # that did - the overlay is only what distinguishes this case.
        self.assertIn("def normalize_label", cases.read_text(
            workspace / "src" / "reporter" / "text_tools.py"))
        self.assertEqual("# Project Learnings\n\n- one trap\n",
                         cases.read_text(workspace / "docs" / "LEARNINGS.md"))
        self.assertFalse((workspace / "src" / "reporter" / "__pycache__").exists())
        self.assertEqual("1", stage.git(workspace, "rev-list", "--count", "HEAD").strip())
        # dirty/ still lands over the commit rather than in it.
        self.assertIn("?? scratch.txt", stage.git(workspace, "status", "--porcelain"))

        bare = self.make_case({}, fixture=False)
        run = self.run_dir()
        workspace = stage.stage_workspace(run, bare)
        self.assertEqual(cases.read_text(stage.SUBJECT / "docs" / "LEARNINGS.md"),
                         cases.read_text(workspace / "docs" / "LEARNINGS.md"))
        # One commit and nothing over it: the tree the subject opens is the app
        # plus nothing, and its diff afterwards is all its own.
        self.assertEqual("1", stage.git(workspace, "rev-list", "--count", "HEAD").strip())
        self.assertEqual("", stage.git(workspace, "status", "--porcelain").strip())

        # The app ignores .agent_temp/, and `reviews/` under it is where every
        # skill that writes a review report puts it, so the project's ignore must
        # not hide that from the judge. Everything else a subject leaves there is
        # its own scratch: forcing all of .agent_temp in put a 27 MB probe CSV
        # into one cell's diff. The artifact checks walk the filesystem, so the
        # scratch is still visible to them.
        stage.write(workspace / ".agent_temp" / "reviews" / "x-code-review.md", "found\n")
        stage.write(workspace / ".agent_temp" / "probe" / "big.csv", "label,amount\n")
        changed, touched = stage.stage_diff(run, workspace)
        self.assertEqual([".agent_temp/reviews/x-code-review.md"], changed)
        self.assertEqual(changed, touched)
        self.assertNotIn("big.csv", (run / "diff.patch").read_text(encoding="utf-8"))
        self.assertIn(".agent_temp/probe/big.csv", checks.workspace_files(workspace))

    def test_non_utf8_bytes_in_the_diff_do_not_error_the_cell(self):
        """A subject's latin-1 probe took two cells' verdicts with it: git's
        output was decoded strictly, so staging raised over a file nobody was
        measuring. Valid UTF-8 still arrives as itself."""
        case = self.make_case({}, fixture=False)
        run = self.run_dir()
        workspace = stage.stage_workspace(run, case)
        (workspace / "probe.csv").write_bytes(b"label,amount\nnorra\xe9,7\n")
        stage.write(workspace / "note.md", "the en dash – survives\n")
        changed, _ = stage.stage_diff(run, workspace)

        self.assertEqual(["note.md", "probe.csv"], changed)
        patch = (run / "diff.patch").read_text(encoding="utf-8")
        self.assertIn("�", patch)
        self.assertIn("the en dash – survives", patch)

    def test_an_unreadable_or_oversized_artifact_is_reported_not_sent(self):
        """`artifacts` is the judge's context. A subject's probe output is
        reported under `omitted` so the judge sees it was written, without the
        bytes reaching the model - and out of `artifacts`, because a note the
        harness wrote is not material a judge may quote to ground a PASS."""
        run = self.run_dir()
        workspace = run / "workspace"
        workspace.mkdir()
        stage.write(workspace / "report.md", "the finding\n")
        stage.write(workspace / "empty.md", "")
        (workspace / "big.csv").write_bytes(b"x\n" * stage.MAX_ARTIFACT_BYTES)
        (workspace / "latin.csv").write_bytes(b"norra\xe9,7\n")
        artifacts, omitted = stage.changed_text(workspace, [
            "report.md", "empty.md", "big.csv", "latin.csv", "never-written.md"])

        # An empty file and one the diff named but the tree no longer holds carry
        # nothing to weigh, so neither is sent nor reported.
        self.assertEqual({"report.md": "the finding\n"}, artifacts)
        self.assertEqual(["big.csv", "latin.csv"], sorted(o["path"] for o in omitted))
        reasons = dict((o["path"], o["reason"]) for o in omitted)
        self.assertIn("over the %d-byte artifact cap" % stage.MAX_ARTIFACT_BYTES,
                      reasons["big.csv"])
        self.assertEqual("not UTF-8 text", reasons["latin.csv"])
        self.assertEqual(stage.MAX_ARTIFACT_BYTES * 2,
                         next(o["bytes"] for o in omitted if o["path"] == "big.csv"))

    def test_what_a_judge_may_quote_and_how_the_quote_is_resolved(self):
        """`_material` is what a PASS must quote from. The omission notes are the
        harness talking about the subject, so quoting one proves nothing and the
        attempt is unusable - while the artifact beside them still grounds. A
        quote resolves as the judge read it, not as the artifact spells it: the
        wrap, the markdown emphasis and a JSON-escaped dash or quote are the
        differences that once cost a correct PASS."""
        request = {"prompt": "do the thing", "diff": "", "outputs": {},
                   "messages": {}, "artifacts": {"report.md": "the finding\n"},
                   "omitted": [{"path": "probe.csv", "bytes": 27,
                                "reason": "not UTF-8 text"}]}
        material = runner._material(request) + "\n" + runner._squash(
            json.dumps(dict(request, omitted=[]), indent=2))

        self.assertTrue(runner._grounded("the finding", material))
        self.assertFalse(runner._grounded("probe.csv", material))
        self.assertFalse(runner._grounded("not UTF-8 text", material))

        emphasised = runner._material(dict(request, artifacts={
            "report.md": "**the widget** trims `whitespace`\nand names the rule\n"}))
        self.assertTrue(runner._grounded("the widget\n  trims   whitespace", emphasised))
        # Two verbatim lines joined by an ellipsis are both read; an ellipsis
        # hiding an invented fragment is not.
        self.assertTrue(runner._grounded("the widget ... names the rule", emphasised))
        self.assertFalse(runner._grounded("the widget … also lowercases", emphasised))
        # A step output is quoted as the judge saw it, not as JSON spells it.
        outputs = runner._material(dict(request, outputs={
            "report": "the re-review — \"READY\" restored it\n"}))
        self.assertTrue(runner._grounded("re-review — \"READY\" restored", outputs))
        # A step output that embeds a JSON blob of its own is escaped once for
        # that blob and again when the request is serialised; the judge still
        # quotes it unescaped.
        double_escaped = runner._material(dict(request, outputs={
            "report": "before \\\"Ran 4 tests in 0.003s / OK\\\" after\n"}))
        self.assertTrue(runner._grounded(
            "\"Ran 4 tests in 0.003s / OK\"", double_escaped))

    def test_a_committed_story_is_still_the_subjects_diff(self):
        """exec-spec commits its story with a plain `git commit`, staged by path; a diff from HEAD
        then showed the judge only the state written around the commit and no
        implementation, and the path checks never saw the committed files."""
        case = self.make_case({})
        run = self.run_dir()
        workspace = stage.stage_workspace(run, case)
        stage.write(workspace / "labels.py", "def normalize_label(v):\n    return v.strip()\n")
        stage.git(workspace, "add", "labels.py")
        stage.git(workspace, *(stage.IDENTITY + ("commit", "-q", "-m", "feat: labels [S01]")))
        stage.write(workspace / "plan.json", "{}\n")
        changed, touched = stage.stage_diff(run, workspace)
        self.assertEqual(["labels.py", "plan.json"], changed)
        self.assertEqual(["labels.py", "plan.json"], touched)
        self.assertIn("normalize_label", (run / "diff.patch").read_text(encoding="utf-8"))

    def test_evidence_lists_run_relative_paths_under_request(self):
        """`request` alone names none of the files a maintainer opens, and
        the two the runner writes last are part of the evidence it lists."""
        cell, _ = self.drive({"requiredArtifacts": ["work.md"]},
                             lambda workspace: stage.write(workspace / "work.md", "x\n"))
        for wanted in ("stderr.log", "checks.json", "request/judge-request.json",
                       "result.json", "summary.md"):
            self.assertIn(wanted, cell["evidence"])
        self.assertNotIn("request", cell["evidence"])
        self.assertEqual([], [p for p in cell["evidence"] if "\\" in p])

    def test_jobs_runs_cells_at_once_and_reports_them_in_order(self):
        """--jobs N is what makes a tier get run: cells are independent DartClaw
        runs, so N of them proceed together, and the report keeps the asked-for
        order so a row is found where it was requested. A barrier both cells
        must reach proves they overlapped; a pool of one would wait forever."""
        barrier = threading.Barrier(2, timeout=10)
        seen = []

        def run_cell(case, provider, profile_name, profile):
            barrier.wait()
            seen.append(case)
            return {"case": case, "provider": provider, "outcome": "PASS", "error": None}, None

        smoke = ("b-case", "a-case")
        stdout = io.StringIO()
        # The sweep is doubled because the real one prunes the maintainer's own
        # evidence root, and it runs once, before any cell has a directory there.
        with mock.patch.object(runner, "run_cell", run_cell), \
                mock.patch.object(stage, "sweep", lambda: seen.append("sweep")), \
                mock.patch.object(cases, "SMOKE", smoke), \
                mock.patch.object(cases, "discover", lambda: sorted(smoke)), \
                contextlib.redirect_stdout(stdout):
            # A case named twice, once by the tier and once by name, runs once.
            code = runner.main(["smoke", "a-case", "--provider", "claude", "--jobs", "2"])
        self.assertEqual(0, code)
        self.assertEqual("sweep", seen[0])
        self.assertEqual(sorted(smoke), sorted(seen[1:]))
        rows = [line.split(" | ")[0] for line in stdout.getvalue().splitlines()[1:3]]
        self.assertEqual(list(smoke), rows)
        self.assertIn("2 cell(s) in", stdout.getvalue())

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            self.assertEqual(2, runner.main(["smoke", "--provider", "claude", "--jobs", "0"]))
        self.assertIn("--jobs", stderr.getvalue())

    def test_a_cell_leaves_no_credentials_directory_whatever_its_outcome(self):
        """The seeded token is the operator's live login, and the CODEX_HOME beside
        it was seven of the ten gigabytes the evidence root once held. Neither is
        evidence, so both go with the cell - on the ERROR path too, which is the
        one a teardown written after the happy path would miss."""
        def leave_state(fail):
            def subject(workspace):
                home = workspace.parent / "data" / "credentials" / "codex"
                stage.write(home / "auth.json", "{}")
                stage.write(home / "state_5.sqlite", "codex's own state")
                if fail:
                    raise RuntimeError("dispatch died")
            return subject

        for fail in (False, True):
            cell, run = self.drive({"commands": ["exit 0"]}, subject=leave_state(fail),
                                   judge={"answer": JUDGE_PASS})
            self.assertEqual(fail, "dispatch died" in (cell["error"] or ""))
            self.assertFalse((run / "data" / "credentials").exists())
            self.assertTrue((run / "result.json").is_file())

    def test_the_sweep_keeps_the_newest_cells_and_clears_a_killed_cells_token(self):
        """A killed cell never ran its teardown, which left 23 live tokens under
        the evidence root; the sweep clears one only when two walls have passed,
        because a younger cell may belong to a tier running in another terminal.
        Past the newest KEEP a cell goes whole, and a directory somebody renamed
        by hand is theirs."""
        now = time.mktime(time.strptime("20260918T120000", stage.STAMP_TIME))
        cells = self.tmp / "evidence" / "a-case" / "codex"
        stamps = ["2026091%dT100000-0000000%d" % (day, day) for day in range(4, 9)]
        for name in stamps + ["aborted-20260901T100000"]:
            stage.write(cells / name / "data" / "credentials" / "codex" / "auth.json", "{}")
            stage.write(cells / name / "result.json", "{}")
        stage.write(cells.parent / ".DS_Store", "")

        stage.sweep(self.tmp / "evidence", now=now)

        kept = sorted(p.name for p in cells.iterdir())
        self.assertEqual(stamps[-stage.KEEP:] + ["aborted-20260901T100000"], kept)
        token = "data/credentials/codex/auth.json"
        # 18 Sep 10:00 is two hours before `now`: inside two walls, so possibly live.
        self.assertTrue((cells / stamps[-1] / token).is_file())
        self.assertFalse((cells / stamps[-2] / "data" / "credentials").exists())
        self.assertTrue((cells / stamps[-2] / "result.json").is_file())
        self.assertTrue((cells / "aborted-20260901T100000" / token).is_file())

    def test_the_report_names_a_smoke_cell_over_the_bar(self):
        """One long cell is the whole tier's wall, so a smoke cell over the bar
        is named under the table; a full-only cell over it is not the tier's
        problem, and neither is a smoke cell under it."""
        def cell(case, seconds):
            return {"case": case, "provider": "claude", "outcome": "PASS", "error": None,
                    "durationSeconds": seconds, "tokens": None}
        smoke, over = cases.SMOKE[0], cases.SMOKE_SECONDS + 1
        rows = [(cell(smoke, over), None), (cell("clarify", over), None),
                (cell(cases.SMOKE[1], over - 1), None)]
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            runner._report(rows, 1.0)
        self.assertEqual(["  %s/claude: %ds over the %ds smoke bar"
                          % (smoke, over, cases.SMOKE_SECONDS)],
                         [line for line in stdout.getvalue().splitlines()
                          if "smoke bar" in line])

    def test_session_cost_lands_in_result_json_and_is_none_when_unrecorded(self):
        """DartClaw's session_cost row is the token record a maintainer reads
        for leanness; the harness copies it by the session id it already holds
        rather than measuring anything itself, and a missing row is `none`, not
        a zero that reads like a free run."""
        raw = {"input_tokens": 40, "output_tokens": 38827, "cache_read_tokens": 1005908,
               "cache_write_tokens": 188536, "total_tokens": 38867,
               "effective_tokens": 375127, "estimated_cost_usd": 5.9410987,
               "turn_count": 2, "provider": "claude"}
        # One run and one kv.json carry both sessions, so the two roles are
        # told apart by the step id that recorded each - `judge.sessionId` is the
        # appended tail's, every other step's is the subject's.
        answer = {"decisions": [{"id": "C1", "pass": False, "reason": "no evidence",
                                 "evidence": ""}]}
        cell, run = self.judge(
            answer, subject_session="subj-1", judge_session="judge-1",
            kv={"session_cost:subj-1": {"value": json.dumps(raw)},
                "session_cost:judge-1": {"value": json.dumps({"effective_tokens": 140575})}})

        self.assertEqual({"input": 40, "output": 38827, "cacheRead": 1005908,
                          "cacheWrite": 188536, "effective": 375127,
                          "estimatedUsd": 5.9410987}, cell["tokens"]["subject"])
        self.assertEqual(140575, cell["tokens"]["judge"]["effective"])
        written = json.loads((run / "result.json").read_text(encoding="utf-8"))
        self.assertEqual(cell["tokens"], written["tokens"])

        cell, _ = self.drive({}, outputs={"s1.sessionId": "subj-2"})
        self.assertEqual({"subject": None, "judge": None}, cell["tokens"])

    def test_worktree_escape_is_error_not_fail(self):
        """Artifacts left in a DartClaw worktree mean --inline did not
        land them in the workspace the evaluator reads. Evaluating anyway would
        report every artifact check as a subject that produced nothing."""
        check = {"requiredArtifacts": ["docs/x.md"]}
        cell, _ = self.drive(check, lambda workspace: stage.write(
            workspace / ".dartclaw" / "worktrees" / "abc123" / "docs" / "x.md", "x\n"))
        self.assertEqual("ERROR", cell["outcome"])
        self.assertIn(".dartclaw/worktrees", cell["error"] or "")
        self.assertEqual([], cell["checks"])

        cell, _ = self.drive(check, lambda workspace: stage.write(
            workspace / "docs" / "x.md", "x\n"))
        self.assertTrue(cell["checks"])
        self.assertEqual(checks.PASS, cell["checks"][0]["status"])

    def test_a_self_reported_step_failure_is_evaluated_not_an_error(self):
        """A subject that refuses correctly reports its own step failed,
        which exits DartClaw 1 although the step ran to the end and wrote its
        declared output. A self-report is not evidence: the checks and the judge
        decide, so only an output the step never wrote is a harness ERROR."""
        reported = record({"s1": ("outcome",)}, ("s1",), success=False)
        failed = {"exitCode": 1, "timedOut": False}
        check = {"requiredArtifacts": ["docs/x.md"]}

        cell, _ = self.drive(check, record=reported, dispatched=failed,
                             outputs={"outcome": "BLOCKED: state already exists"},
                             judge={"answer": JUDGE_PASS})
        self.assertEqual("FAIL", cell["outcome"])
        self.assertIsNone(cell["error"])
        self.assertEqual(checks.FAIL, cell["checks"][0]["status"])

        # Nothing to weigh: the step named an output and left it unwritten.
        cell, _ = self.drive(check, record=reported, dispatched=failed, outputs={})
        self.assertEqual("ERROR", cell["outcome"])
        self.assertIn("outcome", cell["error"])
        self.assertEqual([], cell["checks"])


class SubjectAppTest(unittest.TestCase):
    """The vendored application every case starts from.

    Its flaws are deliberate, which only works while three things hold. Its own
    suite is green, so a case that runs the tiers reads a red suite as its own
    failure rather than as the app's baseline. The manifest beside it is the only
    record of which flaw is deliberate and where, so a path it names that has
    moved leaves a case pointing at nothing. And the tree says nothing about the
    harness: a subject that can read what it is being measured on can satisfy it
    without doing the work - the same reason `oracle.py` is never copied into a
    workspace.
    """

    SUBJECT = pathlib.Path(__file__).resolve().parent / "subject"
    MANIFEST = pathlib.Path(__file__).resolve().parent / "subject-defects.md"
    # Two groups: what the app is measured on, and what is measuring it. Matched
    # by `cases.named_words`, the same rule a case's staged files are held to, so
    # the two lists cannot drift apart in how they read. No exception is carved
    # out for the manifest's own words - it lives beside the app, never inside
    # it, so nothing it says is in scope.
    FORBIDDEN = ("planted", "defect", "fixture", "eval",
                 "andthen", "dartclaw", "oracle", "judge", "rubric")
    NAMED_PATH = re.compile(r"`([\w.-]+(?:/[\w.-]+)+\.(?:py|md|json))(?::\d+(?:-\d+)?)?`")

    def subject_files(self):
        return [path for path in sorted(self.SUBJECT.rglob("*"))
                if path.is_file() and "__pycache__" not in path.parts]

    def test_the_app_suite_is_green(self):
        """A deliberate flaw the app's own tests catch is one no reviewer has to
        find, and a suite red for an unrelated reason fails every case that runs
        a tier. This is the command the app's `fast` tier declares."""
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
            cwd=str(self.SUBJECT), capture_output=True, text=True, timeout=300)
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)

    def test_every_address_the_manifest_names_resolves(self):
        """The manifest is what a case pins its expectation to. A file renamed in
        the app and not here is a case asserting a finding at an address nobody
        can open - which reads exactly like a subject that missed it."""
        root = self.SUBJECT.parent.parent
        named = set(self.NAMED_PATH.findall(self.MANIFEST.read_text(encoding="utf-8")))
        self.assertTrue(named, "the manifest names no files")
        for relative in sorted(named):
            base = root if relative.startswith("evals/") else self.SUBJECT
            self.assertTrue((base / relative).is_file(),
                            "%s is named by the manifest but does not exist" % relative)

    def test_the_app_never_names_the_harness(self):
        """The subject reads this tree. A word from the harness inside it - or the
        answer key's own vocabulary - tells the subject what it is being measured
        on, and a flaw it was told about proves nothing about finding flaws."""
        for path in self.subject_files():
            # Decoded permissively rather than read as text: a file this suite
            # cannot decode is still a file the word rule covers.
            named = cases.named_words(path.read_bytes().decode("utf-8", "replace"),
                                      self.FORBIDDEN)
            self.assertEqual([], named, "%s carries %s"
                             % (path.relative_to(self.SUBJECT), named))


if __name__ == "__main__":
    unittest.main()
