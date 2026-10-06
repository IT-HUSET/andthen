# ADR-026: Ship the branch with a `ship` skill

## Status
Accepted. Recorded 2026-10-03.

Supersedes the Still Current note "No `close-plan` verb", deleted from `Decisions` with this record, and `plan-schema.md` § Shipping's "The user ships it, and no skill does". It also replaces the "commit and open the PR yourself" guidance that took the place of `quick-implement`'s PR creation. `implement-fix` itself still never commits.

*Amended 2026-10-06: story commits no longer carry each FIS's Intent and Expected Outcomes, and `ship` no longer keeps them unsquashed. Squash merging is the common case, and it keeps no branch commit in the base branch's history, so in the common case the commits are no durable record. A squash message listing every story's message also does not scale. The requirements file and the PR body, which `ship` writes from each FIS before deleting the bundle, carry the intent. `ship` never repoints a link at a branch commit, and it leaves the squash message to the host and the merger.*

*Amended 2026-10-06: the PR body also states whether the change is a one-way or two-way door and its blast radius, linking the ADR that settled a one-way door, so the reviewer knows which changes to read slowly. It is always written, because a missing line reads as two-way, and it adds no ask.*

## Context

**The workflow ends on a checklist.** Once a plan's stories are done and its plan-level review is clean, `review`, `implement-fix` on that review's report, and `now-what` print `Next: ship –` with four steps for the user:

1. Commit the fixes left in the working tree.
2. Land what is worth keeping from each FIS's Implementation Observations in `Learnings` or `Decisions`.
3. Delete `plan.json` and the FIS files.
4. Open the PR, keeping the story commits' messages, the only record left of each story's Intent and Expected Outcomes.

**Step 2 is judgment and can be skipped without a trace, and step 3 destroys its input.** andthen-studio's only close-out (`8d16a71`, 2026-09-17, a 0.x run) deleted 10 FIS files, 3,275 lines, and added no `Learnings` or `Decisions` entry. Its three doc edits only repointed links to the deleted bundles. One of those FIS, S02, recorded an unused `trellis_shelf` dependency, still in `pubspec.yaml` and recorded nowhere since. It also recorded that the generated embed map goes stale after a template edit, which the project's `AGENTS.md` covers only for a fresh clone.

1.0 already routes the actionable half. The plan-level review reads a FIS's open observations as findings (`full-review.md`), and `implement-fix` defers what it cannot fix to Tech Debt. Traps and design changes have no route but step 2. The evidence is one case, from 0.x, so the decision rests on it together with the next two points.

**The steps are spelled out in eleven places**: `plan-schema.md`, `now-what`, `full-review.md`, `implement-fix`'s close, three places in `plugin/README.md`, and five in the Cookbook. The Lean principle asks for one source per fact.

**Every comparable library ships this step** (survey of 2026-10-03): Superpowers `finishing-a-development-branch`, Compound Engineering `ce-commit-push-pr` and `ce-compound`, Anthropic's `commit-commands`, Matt Pocock's `pr`, GSD `ship`, Spec Kit's `git` extension and its community `ship`. Adoption is demand, not evidence under the Decision Rule, so it is context only.

## Decision

**A `ship` skill ships the current branch.** It is the 19th skill and the one owner of the close-out.

- **Any branch, input read leniently.** With a plan bundle on the branch, `ship` runs the plan close-out: it lands what the FIS observations hold worth keeping, then deletes the bundle, keeping the requirements file. Without one, it commits and opens the PR.
- **Open work is asked about, not gated.** An unfinished story or an open CRITICAL or HIGH finding is named and asked about once, recommendation first, per the Still Current note "A decision never stops a run".
- **All four steps, one ask.** The commit and the bundle deletion run without asking, because the branch history keeps both. One question before push and PR shows the title and body built from the FIS files and the plan's source. Under `--auto` the run stops before the push and prints the push and PR command, because opening a PR needs consent.
- **Written to intent.** The skill states outcomes and the reason behind each of its few hard rules: land before delete, carry story intent into the PR body, ask once before publishing. Routine git and host work is left to the model, per the Product principles Flexible and Intent-driven and the Skill-authoring guidelines.
- **The printers hand off.** `review`, `implement-fix`, and `now-what` close a ready plan on one `Next (fresh session):` line invoking `ship`, in place of the spelled-out steps.
- **It lands in the 1.0 RC line.**

## Consequences

**Easier**
- The knowledge step runs whenever a plan ships, by an agent applying the `Learnings` admission test, before the deletion that would lose it.
- The close-out has one source; the eleven restatements shrink to a `Next` line or a pointer.
- A branch without a plan still gets a commit and a PR.

**Harder**
- 19 skills, and one more always-loaded description against Codex's shared description budget.
- The skill needs a budget raise, partly offset by the removed restatements.
- AndThen now pushes and opens PRs, an outward-facing action, behind the one ask.
- The docs naming the close-out change: README, `plugin/README.md`, Cookbook, CHANGELOG, two migration-guide rows, and the Architecture document's artifact-lifecycle paragraph.

**Unchanged**
- `implement-fix` never commits, and `exec-plan` commits per story as before.
- Working artifacts stay branch-scoped, and the non-goal against keeping specs past merge stands; `ship` is now what enforces it.
- The plan-level review stays the judge of readiness.

## Alternatives Considered

1. **Fold the knowledge step into the runs that print `Next: ship –`.** Rejected: one procedure spread over three skills, and `now-what` would turn from router into executor.
2. **Plan branches only.** Rejected: an input gate no contract needs (Product, Flexible). A branch without a plan needs only commit and PR, which the same skill does with no extra rule.
3. **Steps 1–3, never push.** Rejected: the step that carries story intent into the PR stays manual.
4. **All four steps, no ask.** Rejected: nothing previews the PR body before it is published.
5. **After 1.0.** Rejected: the RC cycle still admits skills (ADR-025), and the docs describing the workflow's end change once rather than twice.
6. **Floor option: keep the printed checklist.** Rejected: the knowledge step stays skippable with no trace (studio `8d16a71`), and the eleven restatements stay.

## Implementation Notes

Plan it with the `andthen:plan` skill from this ADR. The items left open for that plan's Preflight settled on 2026-10-04:

- **PR body layout.** The project's PR template or named PR process sets it. The body states the intent, the outcomes, and their proof for a reviewer deciding whether to merge, from the plan's source (its requirements file or tracker item), each FIS's Intent and Expected Outcomes, each story's `verified.summary`, and the latest review's verdict, because the bundle and the review report never merge.
- **Commit message shape.** Left to the model and the project's conventions.
- **A design-changing Drift Note.** A recommended `Decisions` line, or a `decide` run where alternatives are open. `ship` writes only `Learnings` traps and never a decision record, as `handoff` does.
- **A host without a CLI.** The run ends on the title, the body, and the commands still to run.

1. `plugin/skills/ship/SKILL.md` and `agents/openai.yaml`, authored per `docs/SKILL-AUTHORING-GUIDELINES.md` and reviewed with the `skill-review` skill.
2. `plan-schema.md` § Shipping keeps the readiness condition; the steps and "no skill does" move to the skill. `exec-plan`'s `plan-run.md` line on leaving the bundle in place names `ship`.
3. `review` (`full-review.md`), `implement-fix`, and `now-what` close a ready plan on `Next (fresh session):` invoking `ship`, and `now-what` routes a request to ship or open the PR to it.
4. Installer arrays for any shared reference `ship` loads, and the Architecture document's skill list and artifact-lifecycle paragraph.
5. Docs: README (count, and the figure via `scripts/skills-overview.py`), `plugin/README.md` (a `ship` section and the three closing lines), Cookbook (close-out, the Ship row, PR timing, the worked example), the migration guide's `quick-implement` rows, the rc.4 CHANGELOG, and the Ubiquitous Language if "ship" settles as a term.
6. `tests/surface-budget.json` raised in the same commit; `UNATTENDED` gains `ship` if it takes `--auto`.

## Project Compliance

- **Product Decision Rule.** It names the failure it prevents, observations deleted unread (studio `8d16a71`, one case), and the outcome it enables, one owner for the close-out.
- **Lean, Flexible, Intent-driven, Robust.** One source for the close-out; any branch, lenient input, no input checks; hard rules only where a contract needs one.
- **Non-goals.** It enforces "no specs kept past merge", and it opens a PR through the host without adding tracker state or a service.
- **Still Current notes.** "A decision never stops a run", "`--auto` is the only unattended trigger", "A question goes where the run stops for it", and "A fresh-session hand-off says so in the line it prints" all hold.
- **ADR-003.** `ship` deletes `plan.json` only once no story run is writing it.
- **ADR-018.** The description stays under the cap, and the surface raise is the reviewed act in `tests/surface-budget.json`.

## Reopens

- If several shipped plans show the knowledge step landing nothing worth keeping, which would make it ceremony.
- If every supported host ships its own commit-and-PR command that makes that half redundant.

## References

- This session's competitor survey and interview with the maintainer, 2026-10-03.
- andthen-studio commit `8d16a71`.
- Related: ADR-003, ADR-018, ADR-024, ADR-025.
