# ADR-032: Let a plan stop at the cut, with each FIS written when its story is claimed

## Status
Accepted. Recorded 2026-11-20.

*Revised 2026-11-23, before implementation, with the amendments of that day to ADR-026 (story pull requests) and ADR-028 (issue sync), so the files they share were edited once. Two facts were corrected (where a plan run stops, and the evidence below). Item 6 reads every finished story's discoveries, item 7 joins the hand-off list ADR-026 extends, item 8 covers `clarify`, and item 9 settles the stop's hand-off. A second `oracle` opinion on the combined design had publication moved from the end of the `plan` run to `ship`'s plan pull request, and a same-lines check on a late FIS dropped.*

Narrows the Still Current note "Specs are co-produced with the story breakdown" to the default path. Extends ADR-028: a child issue gains a body for a story with no FIS, and its 2026-11-05 rule on diverging copies gains one case. Leaves ADR-031 as amended: a late one-story FIS takes no `oracle` second opinion.

## Context

**No story issue can exist before every FIS does.** `plan` on a several-story source cuts the stories, writes `plan.json`, authors every FIS through one subagent each, runs the bundle review and the `oracle` pass, then Preflight (`breakdown.md` Steps 1–3 and 5–7). `tracker publish` builds each child issue from the story's FIS (Intent, Expected Outcomes, Acceptance Scenarios). Two things follow:

- A team sees the slicing in the tracker, and can claim a story there, only after every authoring subagent, the bundle review, and the `oracle` pass are paid for. A re-cut after that review discards FIS files.
- A story claimed weeks later runs a FIS written before its predecessors' code existed. Between-story discovery triage appends to it, but only what a story run noticed.

**Most of the mechanism exists.** The plan schema initialises a story to `pending` with `fis: null`. `plan story <id> of <plan.json>` authors one FIS, with the self-review, Preflight, and the row write when it is not `--batch`. An `exec-plan` plan run stops before its first story while a pending story has no FIS, naming each one and `plan` as its route (`plan-run.md` Step 1).

**The evidence is one run and a survey.** A post-mortem of 2026-11-22 records a 17-story plan whose cut was first reviewed after its FIS files, 73k words, existed, so fixing the cut meant discarding specs. No run shows a stale FIS. A survey of seven frameworks (2026-11-20) found two that write the per-story spec late or never: BMAD on its unreleased main authors story specs just in time and publishes at inception or on start, and Matt Pocock's `to-tickets` publishes thin vertical-slice tickets with no per-ticket spec. Neither is a measurement. The run supports reviewing a cut before its specs are written; that a team working from a tracker needs the cut there first rests on the maintainer's judgment.

## Decision

**`plan --stories-only` stops a several-story run after the cut. The stories are published from `plan.json`, and each FIS is authored when its story is claimed. The default, every FIS in the same run, is unchanged.**

1. **The stop.** Under `--stories-only`, the breakdown runs its Steps 1–3, writing `plan.json` with every story `pending` and `fis: null`, then Step 4, the check of item 3, and ends. On a one-story source or a description the flag has no effect, and the run says so.
2. **The trigger is a flag**, as `clarify --brief` stops at an earlier artifact. The stop skips the bundle review and the `oracle` pass, and the `Product` document's Verified principle removes a gate only "by an explicit workflow change".
3. **The cut is checked before the run ends.** One fresh `reviewer` subagent applies `self-review.md` § Bundle's coherence and traceability checks to the story briefs: source coverage, overlapping scope, dependency gaps, and a cross-story contract `sharedDecisions` does not pin. Preflight then runs once over the cut, and each answer lands where the breakdown's Step 1 says: `prd.md` through the `clarify` amendment, else `sharedDecisions` or the story's brief. An unattended run records its assumptions in the same places. The check is its own breakdown step, which only this path takes, so the default path could take it by one line if a later decision says so.
4. **A child issue for a story with no FIS** carries its `scope`, the heading text of each `#### FRn:` requirement its `sourceRefs` cite, and its blocked-by links. The parent issue holds the PRD, so no criterion is copied. The next publish replaces that body with the FIS sections once the FIS exists.
5. **A copy that lacks the FIS never downgrades an issue.** `publish` from a copy of `plan.json` where a story is `fis: null` leaves that story's child as it is when the child already carries FIS sections. The spec's home is therefore not pinned to a branch.
6. **The late FIS is written by the existing one-story path**, with its self-review and Preflight and nothing more. In a plan where stories are `done`, that path also reads every `done` story's `## Discovered Requirements` and `## Implementation Observations`, a non-dependency's included, because item 7 takes this story out of discovery triage. A narrowing note and a cross-story contract are Preflight items on this path, and a cross-story answer lands in `sharedDecisions`.
7. **Hand-offs name the authoring step.** `exec-plan`'s Follow-up and `now-what` gain one case: a story whose dependencies are `done` and that has no FIS routes to `plan` on `story <id> of <plan.json>`. It sits after "a dependency-ready story is left" in the list ADR-026's amendment of 2026-11-23 extends. Between-story discovery triage skips a story with no FIS, since item 6 reads the discoveries instead.
8. **`plan` on a story's issue authors that story.** A tracker item whose body holds a child `andthen-projection <id> <source>` line resolves to that story of the plan the line names, never to a new plan. Only a parent's line marks a published PRD, in `clarify` as in `plan`.
9. **The stop hands off to `ship`.** Where the project has an `Issue Tracker` document or the plan cites a tracker item, the stop's `Next (fresh session):` line names `ship`, whose plan pull request puts the cut on a shared branch and offers to publish it (ADR-028, amended 2026-11-23). Otherwise it names `plan` on the first story with no dependencies. The `plan` run publishes nothing itself: it commits nothing, so its cut is on no branch a teammate can check out.

## Consequences

**Easier**
- A team reviews the slicing and claims stories in the tracker after one cut, one reviewer pass, and one round of questions.
- A dependent story's FIS is written beside its predecessors' real code and their recorded discoveries.
- A re-cut before any FIS exists discards nothing.

**Harder**
- No whole-plan or parallel run until every story has a FIS: `exec-plan` on the plan directory, `--worktree` included, stops before its first story while one lacks a FIS, so each story runs as a direct story run.
- A plan that stopped at the cut never gets the bundle review or the `oracle` pass. Two defect classes that review catches today reach a late FIS unchecked: a seam its `done` predecessor never produced, and the criteria of one requirement two stories cite. Item 3's contract check and item 6's Preflight items narrow them, and nothing closes them.
- Nothing checks that two late FIS files changing the same lines carry a `dependsOn` edge. The cut applies that rule from briefs, which name no files. A missing edge surfaces as a failed merge in a `--worktree` run, which is loud and possible only once every FIS exists.
- The check on the cut reaches PRD user stories only through the `#### FRn:` entries the briefs cite. A user story no set of plan stories completes stays unnoticed until the outcome lens after the build. No run shows one falling through.
- `OVERSIZE:` can now fire after publication. Decomposing the story gives new story ids, and its claimed child issue is left open for a person to close.
- About eight prompt files change (Implementation Notes), and two always-loaded skills, `plan` and `exec-plan`, gain text every run reads.

**Kept over the second opinion.** The `oracle` asked for every late FIS to be authored on the milestone branch, so its issue is refreshed before the story branches. Not pinned: item 5 removes the downgrade that motivated it, a FIS that travels with its story's pull request is reviewed beside the code, and the `Product` document's Flexible principle keeps strictness for a contract or a recorded failure. Accepted: under story-branch authoring the issue shows scope and requirement names until the story's pull request opens, when `ship` publishes its FIS sections (ADR-028, amended 2026-11-23).

**Reversal**: two-way door for the skill text – the flag, the stop, and the cases in items 4–8 are prose. One-way for a cut already published: its issues stay, and a team that claimed from them has to be told.

## Alternatives Considered

1. **Floor option – change nothing.** Rejected: the Decision buys the slicing review and claimable issues before N authoring subagents, the bundle review, and the `oracle` pass run. It was the recommendation had no team-tracker use been stated.
2. **Author a FIS only for dependency-ready stories, as the new default.** Rejected: it changes every run and reverses the co-produced note outright with no run behind it.
3. **Trigger by words in the request.** Rejected: a run that skips two gates would hinge on how a sentence is read.
4. **Trigger by a line in the `Issue Tracker` document.** Rejected: the choice is per plan.
5. **No flag: let `publish` tolerate a story without a FIS and document a recipe.** Rejected: the stop still skips gates without an explicit switch, and the hand-offs in item 7 dead-end either way. The `publish` half is part of the Decision.
6. **Copy the cited requirements' acceptance criteria into each child.** Rejected: the parent issue already holds them, and the copy sits in several issues until each is refreshed.
7. **Scope alone in the child.** Rejected: a teammate has to open the parent to learn what the story covers.
8. **An `oracle` pass on each late FIS.** Rejected: about $2.89 and five minutes per story, against ADR-031's amendment that withdrew it from one-story runs.
9. **One catch-up bundle review after the last FIS.** Rejected: its findings arrive after earlier stories are built, and the plan gains a state to track.
10. **No check on the cut.** Rejected: an uncovered requirement stays silent until the plan-level gap review.
11. **Tracker as the breakdown's source of truth, two-way sync, or an issue per task.** Out of scope: ADR-028 settles them, and the survey's drift reports (CCPM, Spec Kit, BMAD) support it.
12. **Publish from the `plan` run when it stops.** Rejected at the 2026-11-23 revision: `plan` commits nothing, so the issues would describe a cut on no shared branch, before the plan's pull request is reviewed, and a published cut is one-way.
13. **`plan <plan.json>` authoring every remaining FIS at once, with the bundle review.** Not built: it serves checking a cut before paying for specs, which is the open question of reviewing the cut on every several-story plan, and that is not decided here.
14. **A same-lines `dependsOn` check when a late FIS is written.** Rejected: it reads every sibling FIS per late author to prevent a loud failure (Harder list).
15. **Naming PRD user stories in the check on the cut.** Not built: no run, and the same clause would belong in `self-review.md` § Bundle, a shared reference (Harder list).

## Implementation Notes

Implemented 2026-11-23 as skill text, with ADR-026's and ADR-028's amendments of that day. Surfaces it touches:

1. `plan`: `SKILL.md` (the flag, its no-effect cases, item 8's issue resolution, item 6's reads and Preflight routing) and `references/breakdown.md` (the stop, the reviewer over the cut, Preflight over the cut, the closing line).
2. `plugin/references/self-review.md`: only if § Bundle's two checks cannot be named for briefs from the breakdown's prompt.
3. `tracker`: `SKILL.md` § 2a (items 4 and 5).
4. `exec-plan`: `SKILL.md` Follow-up and `references/between-stories.md` (item 7).
5. `now-what`: `SKILL.md` (item 7).
6. Records: `README.md`, `plugin/README.md`, the Cookbook's team section and tables, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, and `docs/UBIQUITOUS_LANGUAGE.md` if "the cut" becomes a term.
7. An eval case for the stop, and `rg` across `evals/cases/` for cases keyed on a child body that always has FIS sections.

Item 8 rests on a reading of `plan/SKILL.md` step 1, which takes any `andthen-projection` body as a published PRD. No run has shown a second plan being started from a story's issue.

## Project Compliance

- **Decision Rule** (`docs/PRODUCT.md`): the outcome is named, and the need rests on judgment, not a run. This record says so, and the Reopens name what would withdraw it.
- **Verified**: the gates are removed by a flag, and the cut still gets a reader its author is not.
- **Lean**: no new skill, artifact, status, or `plan.json` field. `fis: null` already means "not yet specified".
- **Standing technical non-goals**: `plan.json` stays the plan's state, and the tracker stays a projection (ADR-028).
- **ADR-003**: one writer per copy holds. The session authoring a late FIS writes that story's row.

## Reopens

- A project that used the stop and re-cut after publication more than once: the cut needs more than item 3 before it is published.
- A late FIS that shipped a seam or contract defect the bundle review would have caught.
- Nobody uses the flag across a release cycle: remove it, and keep items 4, 5, and 8 only where they stand on their own.
- A run that starts a second plan from a story's issue despite item 8, or one that shows item 8 was never needed.
- A decision to review the cut on every several-story plan: item 3's step becomes the default path's, and alternative 13 is weighed again.
- A user who stopped at the cut and then wrote every FIS one run at a time: alternative 13.

## References

- Survey of 2026-11-20, from each repository's files: mattpocock/skills (`to-spec`, `to-tickets`), addyosmani/agent-skills, automazeio/ccpm, Kiro, github/spec-kit, bmad-code-org/BMAD-METHOD, Fission-AI/OpenSpec. Not committed, so its relevant findings are inline above.
- One `oracle` second opinion on this decision, 2026-11-20: six objections accepted (items 3 and 5–8, and the Harder list), one kept over (above).
- The maintainer's answers in the deciding session, 2026-11-20.
- The plan-skill post-mortem of 2026-11-22 (a 17-story, 148-task plan), not committed, so its relevant finding is inline above.
- One `oracle` second opinion on the combined design, 2026-11-23: alternatives 12 and 14, and item 6's wider read.
- ADR-003, ADR-028 and its 2026-11-05 amendment, ADR-031.
- `plugin/skills/plan/references/breakdown.md`, `plugin/references/plan-schema.md`, `plugin/skills/tracker/SKILL.md` § 2a, `plugin/skills/exec-plan/references/plan-run.md`.
