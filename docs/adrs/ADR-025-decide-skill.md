# ADR-025: Make and record technical decisions in a `decide` skill

## Status
Accepted. Recorded 2026-10-02.

Amends [ADR-020](ADR-020-one-authoring-and-one-execution-skill.md) and [ADR-021](ADR-021-fold-backlog-triage-and-move-skill-review-out.md) in direction only: they cut entry points, and this adds one.

## Context

Every route to a decision record goes through `architecture --mode trade-off`. Seven skills send their open decisions there:
- `clarify`'s closing command;
- `plan`'s Preflight and FIS authoring guidelines;
- `handoff`;
- `spike`;
- an `exec-plan` pivot;
- `review`'s gap lens;
- `now-what`.

**An ADR costs a research project.** By default, `trade-off` compares five options and sends one research subagent to each. It then runs a findings-filter reviewer and writes four report files before the ADR. Its path loads about 2,900 words. A decision whose options are clear pays the same as a contested one, so a choice that binds beyond one story often goes unrecorded.

**Several decisions have no home between the PRD and the FIS.**
- `clarify` asks what is load-bearing for users and leaves the technical how out (`clarify/SKILL.md:76`).
- `plan`'s Preflight settles forks local to one FIS.
- `advise` answers in text and writes nothing.
- `trade-off` takes one decision per run.

No skill interviews the user across the decisions a technical solution needs.

**The step is hidden.**
- The `architecture` description lost its "trade-off" and "write an ADR" triggers in the structural load cuts (`553bf7e0`, 2026-09-26). Agents pick skills by description.
- The README's pipeline names `[architecture]` for a step that is really a decision.

**`trade-off` shares little with the other modes.** It loads no `architecture-calibration.md`, never chains, and writes to Research rather than Agent Temp (`architecture/SKILL.md:11,30,60`). The other modes read code and report on it.

## Decision

**A new `decide` skill makes and records technical decisions.** It interviews the user in rounds, as `clarify` does, over the decision points of a technical solution, a PRD, or a report. Each question carries a recommendation.

**One test routes every decision point.**
- A choice that binds beyond one story or is costly to reverse is decided here.
- A choice local to one story is left to `plan`'s Preflight.
- A user-visible requirement goes back to the PRD through `clarify`.
- A choice the code or the `Decisions` document already settles is cited, not asked.

**A decision deepens into a weighted trade-off analysis only when it is contested:** no option stands out, the evidence is missing, or the user asks. The analysis is today's `trade-off` procedure, moved to `decide/references/trade-off.md`. An empirical unknown still goes to `spike`.

**Each decision is recorded at its weight.**
- A decision with real alternatives and consequences gets an ADR from the unchanged template, registered in the `Decisions` document as today.
- A load-bearing choice with no real alternative gets a Still Current line.
- The playback that confirms the settled set also asks whether its ADRs go in `Accepted` or `Proposed` for others to sign off, with `Accepted` recommended. An unattended run writes `Proposed`, and its choices with no real alternative go to Pending.
- Only an `Accepted` ADR or a Still Current line settles a decision. A later run asks a `Proposed` ADR or a Pending entry again.

**`architecture` keeps advice and analysis.** It loses the `trade-off` mode and `advise`'s Design sub-mode. A fork that `advise` or an analysis mode surfaces is handed to `decide`.

**`--auto` stays.** An unattended run settles the decisions `INPUT` names by conservative inference, records the assumptions, and writes `Proposed`. The `architecture` eval case calls `decide`, and its directory keeps its name, as under ADR-020.

**Result:** 17 skills become 18. In the README, `decide` takes `architecture`'s place among the eight core skills, and the pipeline reads `[clarify] → [decide] → plan → exec-plan → review --fix → PR`.

## Consequences

**Easier**
- An ADR costs an interview round, not a research project, unless the decision is contested.
- One run settles every decision a solution needs, not one.
- Requests to decide, compare, or write an ADR match a skill named for the job.
- `architecture` becomes read-only advice and analysis, with fewer modes.

**Harder**
- There is one more always-loaded description, about 380 characters, against Codex's shared 8,000-character fallback (about 4,500 used).
- A decision no longer chains after analysis modes in one run. The analysis hands it to `decide`.
- rc users of `--mode trade-off` get an unknown mode. There is no alias before 1.0.
- About 35 files name the old route.
- DartClaw's skill guide names the `trade-off` mode in a doc line. No DartClaw workflow invokes it.

**Unchanged**
- The ADR template and the `Decisions` registration contract.
- `design-tree.md`, and the floor option in every alternative set.
- The trade-off artifacts and their Research location.
- The routing test "binds beyond this work or is costly to reverse".

**Dropped in the move**
- The "no ADR, the report stands as advisory" answer. A run records what it settles, and you can ask it not to.
- The `Learnings` append after a trade-off run. Traps reach `Learnings` at plan close-out.
- `architecture-calibration.md` in the Findings Filter, because it is `architecture`'s own file.
- The separate decision-context gate. Context, options, and weighted criteria are one gate, asked in the interview round where the decision sits.
- The ADR copy at `adr.md` beside the trade-off artifacts. The ADR in the `ADRs` location is the one record, and its *References* name the artifacts.

## Alternatives Considered

1. **An interview mode beside `trade-off` in `architecture`.** Rejected. Two modes would share the decision gates and the ADR contract. Every routing site would also choose between two ADR modes by how settled the decision looks, the failure that merged `prd` into `clarify` (`Decisions`, "Where work starts").
2. **Rework `trade-off` into one interviewing decision mode, still under `architecture`.** Rejected. It fixes the cost but not the visibility: the step stays behind another skill's description, and architecture's mode machinery (Phase 0, chaining, report naming) serves analysis.
3. **Technical decisions in `clarify`.** Rejected. `clarify`'s contract is requirements, and the PRD would carry design that the ADRs then repeat.
4. **Floor option: keep `trade-off`, and lower its default count and research.** Rejected. It stays one decision per run with no interview, and stays hidden.

## Implementation Notes

1. Create `plugin/skills/decide/`. `git mv` `mode-trade-off.md` to `references/trade-off.md` and `adr-template.md` to `references/adr-template.md`. Add `agents/openai.yaml`.
2. In `architecture`, remove the `trade-off` row, its loads and gates, and `advise`'s Design sub-mode. Its follow-up and Post-completion name `decide`.
3. Point every routing site at the `andthen:decide` skill: `clarify`, `plan` (body, `preflight.md`, `fis-authoring-guidelines.md`), `handoff`, `spike`, `exec-plan`'s `story.md`, `review`'s `lens-gap.md`, `now-what`, the `Decisions` template, and `prd-template.md`.
4. Installer arrays: `decide` takes `design-tree.md`, `review-calibration.md`, and `unattended-runs.md`, and `architecture` drops `design-tree.md`. Update `docs/ARCHITECTURE.md` § Shared Plugin Assets and its skill list to match.
5. Tests and evals:
   - `UNATTENDED` gains `decide`.
   - The fixtures README routes `tradeoff` and `adr` to `decide`.
   - The `architecture` eval prompt calls `decide`.
6. Docs: `README.md` (questions, pipeline, core table, counts), `plugin/README.md` (a `decide` section, and the `architecture` section without the decision modes), `COOKBOOK.md`, `MIGRATING-FROM-0.x.md`, the rc.4 CHANGELOG, the overview figure, and the Still Current note "Where work starts".

## Project Compliance

- **Product Decision Rule.** The addition prevents a named failure: decisions that bind beyond one story go unrecorded because the only route costs a research project. One skill is added, and one mode and one sub-mode are removed. No new artifact or document type is added.
- **Non-goal "a mandatory methodology".** `decide` stays optional, reached by the existing routing test.
- **"A skill whose interview is the deliverable takes no `--auto`".** The deliverable of `decide` is the record. The interview is how an attended run reaches it, and pipelines and the eval case need the unattended record.
- **ADR-018's budgets.** The description stays under `DESCRIPTION_CAP`. The moved procedure is net neutral, and the new body fits the surface budget's headroom.

## Reopens

- If recorded use shows decision requests landing in `architecture` rather than `decide`.
- If the shared description budget overflows on Codex.

## References

- This session's discussion with the maintainer, 2026-10-02.
- Related: ADR-018, ADR-020, ADR-021, ADR-024.
