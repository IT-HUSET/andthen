# ADR-031: Name the `oracle` at two gates

## Status
Accepted. Recorded 2026-11-12.

*Amended 2026-11-13: the `plan` second opinion runs only when `plan` breaks the work into several stories. As first recorded it ran on every non-batch run. A one-story run now goes from the self-review straight to Preflight. The text below is the amended record, and alternative 10 holds what was withdrawn.*

Narrows the rule that a second opinion is never requested unasked (the Subagent Model Policy, `docs/MODEL-EFFORT-SELECTION-GUIDE.md`, `plugin/README.md` § Delegation). Two skills now take one read-only `oracle` second opinion at a gate. The session still never self-selects it.

## Context

**Planning is checked below the tier that did it.** The guide recommends running planning on the `oracle` template's model. Two checks on that work did not follow:

- `plan`'s self-review is "the only independent reader before the next skill builds on the document" (`self-review.md`), and it runs on `reviewer`, the mid flagship at medium effort.
- `decide` records a one-way door with no independent reader when the session finds it uncontested. Only a contested decision reaches the trade-off analysis and its Findings Filter, and "contested" is the session's call about its own confidence.

The amended `plan` gate leaves the first gap open on the one-story path: a spec the session wrote on the `oracle`'s model is still read by `reviewer` alone. On the several-story path the authors are `implementer` subagents, so there the gate rests on the measurements below, not on the tier gap.

**The self-review was measured on Claude Code, 2026-11-12.** 36 self-reviews of two two-story bundles the `implementer` wrote (Sonnet 5.5, high), each bundle also copied with four planted gaps. Twelve reviews per arm, scored without knowing the arm.

| | `reviewer` as shipped (Opus 5.5, medium) | `reviewer` body on Fable 5.2, medium | `oracle` as shipped (Fable 5.2, high) |
|---|---|---|---|
| Planted gaps found | 31 of 32 | 32 of 32 | 32 of 32 |
| Unplanted findings that change what gets built | 5 | 13 | 12 |
| Other Notes per review | 4.5 | 6.0 | 4.8 |
| Decision line or scenario value rewritten on a planted contradiction | 2 of 12 | 7 of 12 | 5 of 12 |
| Cost per review | $0.69 | $1.53 | $3.33 |
| Wall time per review | 114 s | 140 s | 399 s |

- The `reviewer` pin found the gaps the rubric names. The top model's edge was findings that change what gets built, about 2.5 times as many, resting mostly on two of the kind "an input nobody specified".
- Effort bought cost, not findings: 12 against 13 at 2.2 times the cost.
- With edit rights the top model rewrote a contradicted decision itself in half the chances. Every rewrite agreed with the source.
- No reviewer in any arm found a structural design fault in the implementer-authored specs.

**The second opinion was measured the same day.** Eight read-only `oracle` runs over the four as-authored bundles the `reviewer` pin had already reviewed, each given the bundle, the reviewer's return, and the `ASSUMPTION:` lines as open items. Scored by two readers who knew the arm.

| | `oracle` at high (as pinned) | `oracle` at medium |
|---|---|---|
| Runs | 4 | 4 |
| Build-changing gaps the reviewer's return lacked, raised | 5 of 6 | 6 of 6 |
| Cost per run | $2.89 | $1.69 |
| Wall time per run | 296 s | 131 s |

- The reviewer's return did not anchor it: the two findings the pin missed in the first measurement came back in 8 of 8 chances.
- About half the material findings arrived as an answer that split an open assumption, not as a new gap.
- Each return also carried three to eight additions, at most one of them material.
- Effort again bought cost, not findings.

**Limits.** Two small bundles over a 140-line subject, one scorer for the first measurement and no blinding for the second, planted gaps too easy to separate the arms, and runs of one arm on one bundle are not independent. No arm ran the second opinion without the reviewer's return. Both measurements ran on the several-story path, so no one-story spec was measured. The bundles were written at the `implementer`'s Claude pin of that day, Sonnet 5.5 at high, and commit `53a65b15` moved that pin to Opus at high, so the edge over specs the shipped pin writes is unmeasured. The first measurement's own report recommended keeping the `reviewer` pin until a larger run. This record goes further on the maintainer's judgment: a gap caught in planning is cheaper than one that is built.

**The `decide` gate has one run behind it, not a measurement.** It rests on the reading above and on the maintainer's judgment that top-model capacity is best spent on planning. One manual `decide --auto` run on the eval subject (2026-11-12, Opus 5.5 session, a report-schema contract other teams will consume) decided two one-way doors and spawned one `oracle` on Fable 5.2 at high. Its second opinion corrected one rationale and showed that "freeze the report as it is today" would freeze platform-dependent line endings, an unquoted label that merges rows, and a row order the PRD contradicts, so that alternative was rejected. The run cost $1.97 and took five minutes. A two-way-door run (`evals/cases/architecture`) took no second opinion and said so.

**The evidence covers one host.** On Codex and Copilot the `oracle` and `reviewer` templates pin the same model at different effort, so there the `plan` gate adds a second read at higher effort, not a stronger model. Effort is the dimension that bought nothing here, and the one the guide records as having bred scope creep. On those hosts the change is a bet.

## Decision

1. **`decide` takes one second opinion.** Before the playback, a run that decided a one-way door spawns one fresh read-only `oracle` subagent with each one-way door, its rationale, the rejected alternatives, and the answers and Proportionality facts it rests on, asking where each is wrong. Once per run, with no second one when a decision changes after it. An accepted objection reopens the frontier. One the decision was kept over is played back with the reason and recorded under the ADR's *Consequences*. It is not a question, so it runs under `--auto` too.
2. **`plan` takes one second opinion before Preflight when it breaks the work into several stories.** The bundle review stays on `reviewer`, with its rubric and its mechanical edits. Then one fresh read-only `oracle` subagent gets `plan.json`, every FIS, the source, the `Product` document, the bundle review's return, and the open items, the story subagents' `ASSUMPTION:` lines among them. It returns the answer it would give each item. As Notes it returns each answer that differs from, splits, or widens its item, and what an executor would still have to guess that no item and no Note names. Once per run. A one-story run takes none: that path was not measured, and attended, its author is the session, which put its questions to the user. An unattended one-story run has neither backstop (alternative 11).
3. **Its return is evidence the session weighs.** A returned Note passes the same `blocks:` filter as a self-review Note, so a minor addition becomes an assumption, never a question. An answer backs the session's recommendation, and closes an item only on a line the session has read. Where the session keeps its own answer, the `oracle`'s is offered as an alternative.
4. **The self-review Fix bar names scenario values and holds "however plainly its source settles the fix".** The self-review runs before Preflight answers reach the source, so a rewrite to the source can revert an answer the user gave, and `Applied:` edits are not re-reviewed. A contradiction is a Note, which Preflight closes by citing the source line.
5. **The role and the policy say so.** The `oracle` templates keep three jobs: the second-opinion job now covers a spec and its open questions, and "a gate a skill names it for" is a third kind of work. The policy's `oracle` list opens "Outside a gate a skill names it for", and its self-selection ban is unchanged.

`clarify`'s PRD self-review stays on `reviewer`, with no second opinion: it was not measured.

## Consequences

- A several-story `plan` run costs about $2.89 more and five minutes longer on Claude Code at this bundle size. A one-story run costs what it did. `decide` adds one top-model read to a run that decided a one-way door.
- The `plan` gate is not the cheap variant. Running the whole bundle review on `oracle` cost $3.33 against $3.58 for the review plus the second opinion. What the split buys is an `oracle` that cannot edit the specs, and an answer for every open item.
- The cost lever is the `oracle` template's effort pin, which no skill can set. At medium the second opinion cost $1.69 with no finding lost in four runs. The recalibration of 2026-11-12 kept the pin at high.
- An unattended one-story run records every open item as an assumption with no top-model reader.
- A session below the `oracle`'s pin now spends above its own model at these two points.
- Preflight can hold more items than before, since an answer may split an assumption in two.
- Installed role files and rules copies do not update with the plugin. Until `init` is rerun, an installed rule says the `oracle` is spawned only when the user asks, while the skills name it.
- The Claude eval cells that run the breakdown, `plan` and `spec-two-stories`, get slower and dearer. The one-story `spec` cell does not.

**Reversal**: two-way door – one paragraph in `decide/SKILL.md`, the second-opinion block in `breakdown.md`, and the template and policy wording. The Fix bar guard stands either way.

## Alternatives Considered

1. **Offer the `decide` second opinion as an answer the user picks** – rejected: its value is in not depending on the user knowing to ask. A per-question offer also took an answer slot from a real alternative and re-offered itself.
2. **`oracle` authors every per-story FIS** – rejected: paid once per story, and the measurement found no structural fault in implementer-authored specs.
3. **`oracle` authors only design-open stories** – rejected on the same evidence, and it adds a judgment call to every breakdown.
4. **`plan`'s whole self-review on `oracle`** – built first and withdrawn the same day on the maintainer's word: the rubric work is within the `reviewer` pin's reach (31 of 32 planted gaps), and with edit rights the top model rewrote contradicted decisions. It also returns no answers to the open items.
5. **The `reviewer` body on the top model at medium effort** – rejected for now: the first measurement points at it, but no role expresses it. A fifth role costs three templates and every "four roles" line, and repinning `reviewer` pays on every story.
6. **A generic inherited subagent for either pass** – rejected: it reaches the top model only when the session is on it, runs at the session's effort, and was not measured.
7. **The second opinion only when the self-review leaves an item open** – rejected: it would skip the gaps nobody named, which is the measured edge, and adds a judgment call.
8. **State the dispatch in `preflight.md`** – rejected: `plan`'s step 4 and the breakdown's Step 1 borrow that file's sitting for an earlier round, so a spawn stated there could fire twice.
9. **Floor option – change nothing, and leave the second opinion to the Cookbook recipe** – rejected: the Decision buys a top-model reader on every several-story `plan` run and every decided one-way door without the user asking.
10. **The second opinion on every non-batch `plan` run** – recorded 2026-11-12 and withdrawn the next day on the maintainer's word. On a one-story run it was unmeasured and cost $2.89 and about 296 s, where the whole `spec` eval run took 512 s with it. The recalibration had also just kept the `oracle` at high, which closed the cost lever.
11. **Several stories, or `--auto`** – rejected on cost and for want of a measurement. An unattended one-story run asks nothing, so its spec carries the same unanswered assumptions as a batch story's, and this is the mechanical criterion that matches the reasoning. It is a Reopen below.
12. **A `--second-opinion` flag** – rejected: a new argument for what the Cookbook recipe already does by asking.

An earlier draft of this record rejected a second opinion in Preflight because "Preflight makes no detection pass". That rule guards against the session re-reviewing its own document with the context that wrote it. A fresh subagent is not that, so `preflight.md` now reads "no detection pass of your own".

## Implementation Notes

- ADR-025's 2026-10-06 amendment rejected running the trade-off analysis for every one-way door "because on an uncontested choice it mostly confirms the recommendation". That stands. This second opinion may mostly confirm too. It is one read over the settled set, against a five-option research run per decision.
- A contested one-way door gets both the Findings Filter and the second opinion. They differ: the filter calibrates one analysis's findings before the recommendation, and the second opinion challenges the confirmed set after the answers.

## Project Compliance

- **Verified** (`docs/PRODUCT.md`): both gates give planning evidence its author did not produce.
- **Efficient**: the cost is weighed against a spec gap or a hard-to-reverse decision that gets built on.
- **Decision Rule**: the `plan` gate has its runs. The `decide` gate rests on analysis and one run, and this record says so.
- Skills name a role, never a model or effort.

## Reopens

- A larger run, five or more stories with harder planted gaps, where the second opinion adds nothing the self-review lacks, or its additions crowd Preflight.
- A rerun over bundles the shipped `implementer` pin wrote, where the edge is gone.
- A measurement of an unattended one-story run that shows build-changing assumptions reaching the executor.
- A Codex or Copilot run where the second read at higher effort produces scope creep.
- A recalibration that moves the `oracle` effort pin: redo the cost lines above.
- `decide` runs whose second opinion never changes a decision. No eval observes that gate: `evals/cases/architecture` runs `decide --auto` with no criterion on it.
- Fix-bar breaks on contradictions that continue under the reworded bar.
- A measurement of `clarify`'s PRD self-review.

## References

- The measurements' report and runs, `.agent_temp/spec-review-tier-comparison.md` and `.agent_temp/spec-review-tier/second-opinion/`, are not committed, so their numbers are inline above.
- Four `oracle` second opinions on this design and the maintainer's discussion, 2026-11-12 and 2026-11-13.
- ADR-025, `docs/MODEL-EFFORT-SELECTION-GUIDE.md`.
