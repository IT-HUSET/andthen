# ADR-024: Name the skills `plan` and `exec-plan`, and give every story status a writer

## Status
Accepted. Recorded 2026-10-02.

- Amends [ADR-020](ADR-020-one-authoring-and-one-execution-skill.md): the merged skills keep their router layout and change name. `spec` becomes `plan`, and `exec-spec` becomes `exec-plan`.
- Amends [ADR-003](ADR-003-runtime-state.md): under `--worktree` the plan run writes the dispatched batch's `in-progress` rows before the batch branches.

## Context

ADR-020 merged four entry points into `spec` and `exec-spec`. A survey of eleven frameworks and skill libraries (2026-10-01) found "spec" naming the requirements step in seven and the breakdown step in none, and "plan" naming the breakdown step in seven. AndThen's `spec` cuts stories and writes `plan.json`, so a reader arriving from the field maps it one layer too high. The oracle's case for keeping the names stands as cost, not reason: the FIS is the contract, no harm is recorded, and DartClaw 0.27.0/0.27.1 invoke both skills. rc.4 is untagged, and after 1.0 any rename is breaking (ADR-020).

The story statuses have three gaps:
- `in-progress` has had no execution-time writer since `64bab154` (2026-09-29); only an on-demand `handoff` sets it.
- No skill writes `skipped`.
- `spec-ready` repeats what `fis` already records.

A plan board downstream needs to see which stories are executing.

The maintainer settled the names, statuses, the wave term, and the Specs & Plans entry on 2026-10-02. Three points stayed open:
1. Under `--worktree` a story writes its row in its own worktree. The main checkout therefore sees `in-progress` only at merge, when the story is already `done`.
2. Whether a failed story stays `in-progress` or gets a status of its own.
3. A hand-skipped dependency blocks its dependents in AndThen (`plan-schema.md` § Execution semantics). DartClaw counts it as satisfied (`dartclaw-discover-andthen-plan` rule 7).

**Success criteria:**
- A board reading the main checkout's `plan.json` sees which stories are executing.
- Every status has a named writer.
- AndThen and DartClaw agree on dependency semantics.

**Dealbreakers:**
- Two concurrent writers on one copy.
- A status no skill writes, apart from a hand-set `skipped`.
- A run that executes the wrong thing without an error.

**Weighted criteria:**

| Criterion | Weight |
|---|---|
| Board accuracy: the main `plan.json` shows the true state | 25 |
| Writer discipline: one writer per copy, no new kind of writer | 25 |
| Failure loudness: nothing executes wrongly in silence | 20 |
| Surface added: shipped words and DartClaw edits | 15 |
| Downstream contract stability | 15 |

## Decision

**Names.** `spec` becomes `plan` and `exec-spec` becomes `exec-plan`, with the router layout and branches unchanged. FIS and PRD keep their names. Renaming `prd.md` to `spec.md` is held.

**Statuses: `pending`, `in-progress`, `done`, `skipped`.**
- `pending`: not started. `fis` says whether the FIS exists, which replaces `pending` + `spec-ready`. The breakdown writes `pending` with `fis` set where it wrote `spec-ready`.
- `in-progress`: written when a story starts, by the session executing it. That is a direct `exec-plan` run, or the story subagent a plan run dispatched. `handoff` stops writing story status.
- `done`: written with `verified`, as now.
- `skipped`: set by hand. No skill writes it.

A story is dependency-ready when it is `pending` with a FIS, or `in-progress`, and every `dependsOn` story is `done`.

**Waves.** "Wave" names a dependency-ready batch, replacing the coined phrase. A wave is derived from `dependsOn` and never stored.

**Specs & Plans entry.** The `init` template's entry and this repo's `AGENTS.md` entry name `plan` and state the one-writer rule.

**Open point 1: under `--worktree` the plan run marks the batch.**
- Before a batch branches, the plan run commits the dispatched stories' rows as `in-progress` on `BASE_BRANCH`. They go in the pre-batch `chore` commit with the other pre-batch writes.
- No story copy exists yet, so each copy still has one writer at a time. Each story then edits only its own row, and the merge brings `done` back clean.
- Without `--worktree` the story's own write lands in the shared tree, so the plan run writes nothing.

**Open point 2: a failed story stays `in-progress`.** Its failure lives in the run report. Under `--worktree` it also lives in the preserved branch and worktree, and a rerun resumes on them. There is no `failed` status.

**Open point 3: `skipped` blocks its dependents.** `done` already requires `verified`, so `skipped` means "not built", and a dependent's FIS presumes its dependency's code. AndThen's ready rule stands, and DartClaw aligns in three places:
- Discover rule 7 prunes only `done` dependencies.
- Rule 6 also omits every story that depends on a `skipped` one, directly or transitively. Without that, the dangling edge throws `Unknown dependency IDs` (`dependency_graph.dart:105`) and blocks the whole plan, not just the dependents.
- The validator's remediation hint (`story_specs_contract_validator.dart:79`) names `done` only. Today it steers a retry toward treating `skipped` as satisfied.

To unblock a dependent, the user who skipped the story edits one `dependsOn` line.

**Why C2 over the floor.** The floor leads the weighted total 410 to 405, within one point of noise on any row. C2 is chosen on a gate: under `--worktree` the floor fails the first success criterion outright, and C2 is the cheapest of the options that pass.

## Consequences

**Easier**
- Skill names match the field's step names: `clarify` → `plan` → `exec-plan` → `review`.
- Every status has one named writer, and in both modes a board reading one file sees which stories are executing.
- `spec-ready` leaves, so `fis` alone records whether a FIS exists.
- After a hand skip, AndThen and DartClaw run the same plan the same way.

**Harder**
- Under `--worktree`, one more commit per batch on `BASE_BRANCH`. Today the pre-batch commit is conditional, so most batches make none.
- Four sites saying the plan run writes no row change together: ADR-003, `plan-schema.md` § State writers, the opening of `plan-run.md`, and `story-worktrees.md` § Before each batch branches.
- The main checkout can show a stale `in-progress`: for a story that failed, one that stopped on its base check before starting, or a batch whose run crashed. Accepted, because resume treats `in-progress` as ready. A board can read `in-progress` with no live `story/{id}` branch as stalled. That is a read-side hint, not a contract.
- rc bundles holding `spec-ready` or `owner` fail `plan.schema.json`, which checks only what `plan` writes. Readers take them as they stand: `spec-ready` and `blocked` read as `pending`, as rc.3 already read `blocked`, and a field the schema lacks is ignored. A story with any other status stays unstarted and is named in the run report, so a hand-typed `Done` never re-runs finished work (`plan-schema.md` § Execution semantics, amended 2026-10-05). ADR-020's "no migration" holds. DartClaw's discover skill reads any unknown status as `pending`, so the two differ only on a status no release wrote.
- DartClaw changes in the same release:
  - the skill names in both built-in workflows;
  - the discover skill's enum note, which still lists the removed `blocked`;
  - discover rules 6 and 7;
  - the validator hint;
  - the `spec-ready` fixtures.
- About 980 name matches in 91 files here (measured 2026-09-29).

**Unchanged**
- ADR-020's router layout, one author per story, the single plan writer at authoring, and the fresh-session hand-off lines.
- The FIS format. `plan.json` stays schema v2, because schema versions count breaking changes against a release (ADR-003), and 1.0 is unreleased.

## Alternatives Considered

1. **C3: downstream reads each worktree's copy**, through `git worktree list` and the `story/{id}` branches. Rejected: the board reads worktrees, not the main checkout, so it fails the first success criterion as worded, and the branch naming becomes an artifact contract. Score 385.
2. **C4: a `failed` status, written by the story.** Rejected: under `--worktree` a failed story is never merged, so `failed` never reaches the main checkout, and a crashed turn writes nothing. Score 350. A variant has the plan run write `failed` in its next pre-batch commit. That does reach the main checkout, but it still misses a crashed run, adds a status, and widens the run's write role.
3. **C5: `skipped` satisfies its dependents**, DartClaw's current rule. Rejected: a dependent runs on a base missing the skipped story's code, with no error. Score 360.
4. **Keep `spec` and `exec-spec`** (oracle second opinion, 2026-10-01). Rejected by the maintainer on 2026-10-02 on the name survey. Its points stand as the costs above.
5. **Floor option, C1: accept that worktree runs show `in-progress` only at merge.** Rejected: it fails the first success criterion under `--worktree`. Score 410, see the Decision.

## Implementation Notes

1. Run `git mv plugin/skills/spec plugin/skills/plan`, and the same for `exec-spec` → `exec-plan`. Sweep every bare name, frontmatter description, and `Trigger on` clause, not only sigils (Learnings: a rename sweep is caught only where a name is a sigil).
2. Schema and authoring:
   - Drop `spec-ready` from the `plan.schema.json` enum.
   - Update `plan-schema.md`'s transitions, ready rule, and § State writers.
   - `breakdown.md` writes `pending` with `fis` set, and its gates read "every story has a FIS".
   - `plan-run.md` Step 1.3 requires a FIS for every `pending` and `in-progress` story.
3. In `story.md`, write `status: in-progress` once the tree is baselined, before the first task edit.
4. In `story-worktrees.md` § Before each batch branches, the batch's `in-progress` rows join the pre-batch `chore` commit. Update the opening of `plan-run.md` to match.
5. In the glossary, a "Wave" row replaces "Dependency-ready batch" and drops "wave" from the terms to avoid. `plugin/README.md:200` uses "dependency-ready batches" for authoring order, which is a different rule (`breakdown.md:34`), so reword it.
6. Update the Specs & Plans entry in `plugin/skills/init/templates/CLAUDE.template.md` and `AGENTS.md`.
7. Evals: the `now-what-active-plan` rubric, and every fixture holding `spec-ready`. Case directories keep their names (ADR-020).
8. Docs: `MIGRATING-FROM-0.x.md` flips its spec/plan rows. Update `README.md`, `plugin/README.md`, `COOKBOOK.md`, the rc.4 CHANGELOG, and the Still Current notes naming `spec` or `exec-spec`.
9. DartClaw, same release: the workflows, the discover skill (enum, rules 6 and 7), the validator hint, and the fixtures.

Risk: a name missed in prose routes a subagent to a skill that no longer exists. Step 1's sweep mitigates it, plus `install-skills.sh --validate-only` and `audit-cookbook.py`.

## Project Compliance

- **Product Decision Rule and Proportionality.** No new status and no script. It extends the existing pre-batch commit, and state stays with its owning local artifact, per the standing non-goal "no central workflow database".
- **Settled decisions.**
  - ADR-003's one writer per copy holds, since the plan run's write and the story's write are sequential.
  - Still Current "A decision never stops a run" keeps `blocked` out.
  - "AndThen renders nothing; it owns the artifact contracts" holds: the board reads one file AndThen owns, and no shipped skill names it.
- **Architecture.** No structural change; skills stay self-contained.

## Reopens

- If the board reads worktree copies anyway: C3 then costs less.
- If a recorded run shows a stale `in-progress` misleading a reader where a liveness hint would not.

## References

- Research: `docs/temp/research/terminology-alignment-sdd-agentic.md` (local, not committed), § "Decision set, settled with the maintainer 2026-10-02".
- Trade-off artifacts: `docs/temp/research/plan-rename-and-story-statuses/` (local).
- Related: ADR-003, ADR-014, ADR-020.
