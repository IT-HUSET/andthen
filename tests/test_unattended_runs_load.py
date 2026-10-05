#!/usr/bin/env python3
"""`--auto` is the one unattended trigger, and `unattended-runs.md` is read in
that mode only. Nothing makes a run stop asking except that flag.

Three invariants, each a run that went wrong without it:

**The flag is advertised where it is honoured, and read only there.** A skill
that means something by `--auto` names it in `argument-hint`, which is
frontmatter and so always in context - the flag can never arrive as an unknown
token the skill drops, stops on, or silently runs attended past. The rules
behind it load with it: read unconditionally, they changed attended behaviour in
both directions. `implement-fix` began stopping to ask whether `shout("stop!")`
returns `STOP!` or `STOP!!`, a question it had answered itself in six prior runs
of the same eval, and `spec` stopped asking the `plan` case's PRD conflict at
all. A skill reading the file for one named section - `testing` for § Recording
an assumption - carries no load line and is not a loader.

**No skill settles questions its own text asks.** `unattended-runs.md` used to
carry a § Headless-First that had four skills - `spec`, `exec-spec`, `triage`,
`simplify-code` - answer routine questions themselves even in an attended run.
That set was the set of skills which had linked the old `automation-mode.md`,
which is a packaging fact about where the `--auto` rules lived, not a statement
about who should ask; and `plan` and `triage` each carry an ask contract it
contradicted, while the other two carry none for it to override. Measured, it
cost the `plan` eval its ask: Codex settled the PRD conflict itself in 3 of 3
runs, Claude in 2 of 3, every one of them attended. The phrase is retired and
must not return under any spelling.

**One trigger, so nothing drifts.** A reverted 2026-09-25 change replaced the
flag with a caller sentence and had to define it, rule it out as target text, and rule out
inferring it from how the run was launched - and hosts inferred it anyway. The
sentence must not come back as a second way to say the same thing.

An `ASSUMPTION:` line is the record of an answer nobody could give, so it is
reachable only from a question that was asked. Codex reached it without asking -
"Unanswered choices ... are recorded as assumptions in the specs" - because the
old wording keyed the fallback on a question "nobody answered", which the run
certifies about itself. Asked-then-unanswered is a fact about the transcript.

The gate binds a question a skill's text says to ask, not every choice an
`ASSUMPTION:` can record: an executor choosing the narrowest defensible reading
of its brief is `exec-plan` never stopping on FIS detail, a decision of its own,
and a rule that made it ask would contradict `exec-plan`'s `story.md`."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugin"
REFERENCE = PLUGIN / "references" / "unattended-runs.md"
PREFLIGHT = PLUGIN / "skills" / "plan" / "references" / "preflight.md"
GUIDELINE = ROOT / "docs" / "SKILL-AUTHORING-GUIDELINES.md"
# The path, not the link: install-skills.py counts a code-span path as a load too.
PATH = "../../references/unattended-runs.md"
LOAD = f"`--auto` makes the run unattended: read [`unattended-runs.md`]({PATH}) and follow it."
RETIRED_TRIGGER = "This run is unattended: no one can answer until it ends."
RETIRED_OPT_IN = re.compile(r"headless[\s-]*first", re.I)
UNATTENDED = {"architecture", "decide", "exec-plan", "implement-fix", "review", "simplify-code",
              "plan", "ship", "tracker", "triage", "ui-ux-design"}


def shipped_skills():
    """Each skill's markdown files, keyed by skill directory, then path within it:
    a skill reads its references, so a phrase there is the skill's own."""
    return {
        skill.name: {
            path.relative_to(skill).as_posix(): path.read_text(encoding="utf-8")
            for path in sorted(skill.rglob("*.md"))
        }
        for skill in sorted((PLUGIN / "skills").iterdir())
        if (skill / "SKILL.md").is_file()
    }


def advertises_auto(files):
    hint = re.search(r'^argument-hint:\s*"(.*)"\s*$', files["SKILL.md"], re.M)
    return bool(hint) and "--auto" in hint.group(1)


def ask_routes():
    """Every shipped file that routes an ask to the host's question tool, by path."""
    sites = {path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8")
             for path in sorted(PLUGIN.rglob("*.md"))}
    return {name: text for name, text in sites.items()
            if re.search(r"structured (question|user-input) tool", text)}


def missing_load(skills):
    """Skills advertising `--auto` without the canonical load line: the flag
    would name a mode whose rules the skill never reads."""
    return sorted(name for name, files in skills.items()
                  if advertises_auto(files) and LOAD not in files["SKILL.md"])


class FlagSurfaceTest(unittest.TestCase):
    def test_exactly_the_pinned_skills_advertise_the_flag(self):
        advertised = {name for name, files in shipped_skills().items() if advertises_auto(files)}
        self.assertEqual(
            advertised,
            UNATTENDED,
            "gaining or losing an unattended mode changes a skill's contract: "
            "decide it, then update UNATTENDED in this commit",
        )

    def test_every_advertising_skill_loads_the_reference(self):
        self.assertEqual(missing_load(shipped_skills()), [])

    def test_an_unloaded_flag_fires_and_a_paraphrase_does_not_satisfy(self):
        hint = 'argument-hint: "[--auto] [scope]"\n'
        self.assertEqual(missing_load({"synthetic": {"SKILL.md": hint}}), ["synthetic"])
        paraphrased = hint + f"- **Automation rules** - [`unattended-runs.md`]({PATH})."
        self.assertEqual(missing_load({"synthetic": {"SKILL.md": paraphrased}}), ["synthetic"])
        self.assertEqual(missing_load({"synthetic": {"SKILL.md": hint + LOAD}}), [])

    def test_a_skill_without_the_flag_is_not_required_to_load(self):
        # `testing` reads one named section, so it is not a loader.
        self.assertEqual(missing_load({"synthetic": {"SKILL.md": 'argument-hint: "[scope]"\n'}}), [])

    def test_no_skill_reads_the_reference_outside_the_flag(self):
        for name, files in shipped_skills().items():
            for path, text in files.items():
                if PATH not in text:
                    continue
                self.assertTrue(
                    LOAD in text or "§ Recording an assumption" in text,
                    f"{name}/{path} pulls the unattended rules into every run: gate the load "
                    "behind `--auto`, or cite the one section it needs by name",
                )


class OneTriggerTest(unittest.TestCase):
    def test_the_reference_names_the_flag_as_the_only_trigger(self):
        text = REFERENCE.read_text(encoding="utf-8")
        self.assertIn("A run is unattended when `--auto` is in the skill's arguments, and only then", text)

    def test_the_retired_sentence_and_opt_in_are_gone(self):
        surface = sorted(PLUGIN.rglob("*.md")) + [GUIDELINE]
        self.assertTrue(surface)
        for retired, why in ((re.compile(re.escape(RETIRED_TRIGGER)),
                              "`--auto` is the one trigger; a second wording drifts from it"),
                             (RETIRED_OPT_IN, "no skill settles questions its own text asks")):
            carriers = [path.relative_to(ROOT).as_posix() for path in surface
                        if retired.search(path.read_text(encoding="utf-8"))]
            self.assertEqual(carriers, [], f"{retired.pattern!r}: {why}")

    def test_the_sweep_reads_content(self):
        # Proves the sweep above finds a carrier rather than finding nothing to read,
        # and that the opt-in is caught under the old heading's spelling and a spaced one.
        self.assertIn(RETIRED_TRIGGER, f"a brief stating {RETIRED_TRIGGER}")
        for spelling in ("§ Headless-First", "headless first", "headless-first"):
            self.assertRegex(f"a brief stating {spelling}", RETIRED_OPT_IN)


class AssumptionGateTest(unittest.TestCase):
    def test_the_reference_reaches_an_assumption_only_through_a_question(self):
        text = REFERENCE.read_text(encoding="utf-8")
        self.assertIn("a question the run stopped on and nobody answered", text)
        self.assertIn("one it continued past was not asked", text)

    def test_preflight_gates_its_fallback_the_same_way(self):
        """The canonical rule lives in `unattended-runs.md`, which an attended run
        never loads, so Preflight restates it - and a restatement is where the two
        drifted. Preflight's said "once it was asked and the reply left it
        unanswered", which a question sent down a channel the run continued past
        satisfies: six Codex `plan` cells on 2026-09-28 asked the contested fork
        through `request_user_input_async`, got no answers, and wrote their own
        choice into the specs. The reference already gated it on the run having stopped, so
        the fix was alignment, and the shared clause is pinned in both files rather
        than two wordings that can drift again."""
        text = PREFLIGHT.read_text(encoding="utf-8")
        shared = "one it continued past was not asked, however the question was sent"
        self.assertIn(shared, REFERENCE.read_text(encoding="utf-8"))
        self.assertIn(shared, text)
        self.assertIn("An item never put to the user has no assumption", text)

    def test_every_ask_site_ends_its_turn_on_the_question(self):
        """Codex asked the `plan` case's four questions through
        `request_user_input_async`, a channel that does not end the turn, slept 50s,
        got `{"accepted":true}` and no answers, and finished on a report - so its
        first reply, which is what a caller reads, showed a settled plan. A tool is
        the right place for a question only while it holds the turn for the answer.

        Turn-holding alone is not enough, because it is a property of the host's
        tool and the model judges it wrong: every site used to hang the
        end-on-the-question duty off the *otherwise* branch, so picking the tool
        branch carried no duty at all and Codex's report was compliant. The duty is
        therefore stated about the run's own output, which the model can check as it
        composes, and it binds whichever channel carried the ask.

        The sites are discovered, not listed: the old test was suitability, which a
        multi-choice tool with a preselected recommendation passes perfectly, so a
        site added later would inherit the wrong test from whichever neighbour it
        was copied from."""
        routes = ask_routes()
        self.assertTrue(routes, "the phrase that routes an ask to a tool changed: retarget this sweep")
        missing = sorted(name for name, text in routes.items() if "holds the turn" not in text)
        self.assertEqual(
            missing,
            [],
            "each of these routes an ask to the host's question tool without requiring the tool to "
            "hold the turn for the answer, so on a host whose tool does not, the run continues past "
            "its own question and the reply reads as settled",
        )
        unbound = sorted(name for name, text in routes.items()
                         if "on the question, never on a report" not in text)
        self.assertEqual(
            unbound,
            [],
            "each of these leaves the end-on-the-question duty conditional on the channel, so a run "
            "that believes its tool holds the turn owes nothing and may finish on a report; state the "
            "duty about the run's own output, which does not depend on judging the host's tool",
        )

    def test_a_tool_that_holds_the_turn_carries_the_whole_round(self):
        """A Claude Code `plan` run on 2026-10-04 asked its twelve Preflight items in
        the reply, though `AskUserQuestion` holds the turn. Preflight allowed the tool
        "only where" it holds the turn, a restriction that never prefers it, and asked
        in "one sitting", which a tool taking four questions a call cannot carry in one
        call. So a site prefers the tool wherever it holds the turn, and a site that
        batches its questions says a batch past the per-call limit spans calls."""
        routes = ask_routes()
        unpreferred = sorted(name for name, text in routes.items()
                             if "wherever it holds the turn" not in text)
        self.assertEqual(
            unpreferred,
            [],
            "each of these permits the question tool without preferring it, so a run asks a "
            "round the tool could hold in the reply instead",
        )
        batching = {name: text for name, text in routes.items()
                    if re.search(r"one sitting|in rounds", text)}
        self.assertTrue(batching, "the phrase that batches an ask changed: retarget this sweep")
        unsplit = sorted(name for name, text in batching.items()
                         if "go in consecutive calls" not in text)
        self.assertEqual(
            unsplit,
            [],
            "each of these batches questions without saying a batch past the tool's per-call limit "
            "spans consecutive calls, so a batch too big for one call goes to the reply",
        )

    def test_the_asking_reply_records_no_answer(self):
        # Both observed failure shapes: a default listed in the reply, and the
        # assumption written into the artifact before the question was put.
        self.assertIn("ends on its last question and answers none of it",
                      PREFLIGHT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
