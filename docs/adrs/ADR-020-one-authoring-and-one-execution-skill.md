# ADR-020: One authoring skill and one execution skill

## Status
Accepted. Recorded 2026-09-25.

- Replaces the split in which `spec` took one story with no PRD and `plan` took a PRD for several.
- Amends [ADR-014](ADR-014-story-runs-where-invoked.md), whose text now states the merged shape.
- *Amended 2026-10-02 by [ADR-024](ADR-024-plan-names-and-story-status-writers.md): the merged skills are renamed `plan` and `exec-plan`, with this layout unchanged.*

## Context

The spec-driven path has four entry points. The user picks between them by story count:

- `spec` and `plan` author the work;
- `exec-spec` and `exec-plan` execute it.

The README spends one of its three orientation questions on "one story or several?". Yet `plan` already decides the final story count, and `spec` already routes an oversized story to `plan`. The four descriptions define themselves against each other. The comparison with Pocock's skills, Superpowers and OpenSpec found their entry-point counts well below AndThen's 21. Pocock merged a similar split (`to-plan` and `to-issues` became `to-tickets`).

The merge has to keep the constraints behind the current shape:

- One FIS authoring context per story (Still Current "One authoring subagent per story").
- ADR-014: one `exec-spec` subagent per story.
- `plan.json` keeps a single writer.
- Several stories need a written source. The reason, now in `spec/SKILL.md`: story briefs carry pointers, the cross-cutting reviewer and the plan-level gap lens read the source, and Preflight answers amend it.
- The "fresh session" hand-off lines stay.
- Still Current: leanness is measured per consuming path.

After 1.0 any merge is a breaking rename.

**Weighted criteria:**

| Criterion | Weight |
|---|---|
| Entry points and user decisions removed | 25 |
| Words loaded per path | 25 |
| Constraints kept | 20 |
| Migration cost | 15 |
| Fit with the authoring rules | 15 |

## Decision

**Merge `plan` into `spec` and `exec-plan` into `exec-spec`, in a router layout.** Each body holds only reading the input and choosing a branch. Each branch is a reference the body names at its load site.

**`spec`, one or more stories**

- The body is about 1,010 words:
  - the input forms and the Durable-State Check;
  - priming and the Proportionality anchor;
  - the written-source rule;
  - a sizing step, placed before any FIS-authoring reference loads;
  - the dispatch lines.
- One story loads `references/fis-authoring.md`, today's authoring steps.
- Several stories load `references/breakdown.md`, today's `plan` steps. Add `regeneration.md` when `plan.json` exists.
- Inputs that fix the count need no judgment:
  - `story <id> of <plan.json>`, `--batch` and an existing FIS path are one story;
  - inline text is one story;
  - a v2 `plan.json` with several stories is several.
- Otherwise `spec` judges the count: one story when a single vertical slice fits one fresh-context execution run.
- Several stories still need a written source. Inline text that sizes to several is sent to `clarify --brief` in an attended run, and proceeds as one story with `OVERSIZE:` in an unattended one.

  *Amended 2026-09-28, withdrawn: this contradicts the count-fixing list above, which makes inline text one story, and as implemented it dropped 0.x's "one spec → one FIS" guarantee – an attended description could end the run with nothing written. Inline text is one story in both modes; `OVERSIZE:` after authoring carries the split offer and the `clarify` route – plain `clarify`, since `--brief` is a user-invoked flag no skill routes to.*
- The several-story branch spawns one fresh subagent per story, invoking the `andthen:spec` skill on `story <id> of <plan.json>` with `--batch`, one author per story.

**`exec-spec`, a FIS or a plan directory**

- The body is about 370 words: flags, the shared rules and the dispatch.
- A FIS loads `references/story.md`, today's `exec-spec` steps.
- A plan directory, or a `plan.json` path, loads `references/plan-run.md`, today's `exec-plan` steps. Add `references/story-worktrees.md` under `--worktree`.
- A plan run spawns one fresh subagent per ready story, invoking the `andthen:exec-spec` skill on that story's FIS with `--no-full-tier`. ADR-014's "never another executor" now applies to FIS runs.

**Result:** 21 skills become 19. The pipeline reads `clarify` → `spec` → `exec-spec` → `review`.

The floor option leads on the weighted total, 400 to 380, because this decision amends two accepted ADRs and a Still Current clause. It is chosen on a reason outside the criteria: this is a one-way door. After 1.0 the merge becomes 2.0, so the choice is now or never. The claim that users feel entry points more than words is the maintainer's judgment from the comparison, not a measurement.

## Consequences

**Easier**

- The user answers only "do I know what to build?". `spec` answers "one story or several?".
- Two entry points go, and the always-loaded descriptions lose about 465 characters.
- The four skills' files go from 9,082 to about 8,450 words (−7%), and about 100 routing words go elsewhere.
- Neither orchestrator loads the procedure it delegates, so the in-session regression ADR-014 records cannot recur through a shared body.
- `spec` becomes the only author of `plan.json`.

**Harder**

- `spec` makes a sizing judgment that users made before. A wrong call is caught by `OVERSIZE:` after authoring, which continues into the breakdown in an attended run.
- Measured per path (research estimates, ±10%), every path lands within +2% to +7% of today. Meeting "no path grows" strictly needs a compensating trim of about 160 words in the `spec` one-story path and about 120 in `story.md`.

*Amended 2026-09-25 on measurement, at implementation: moved verbatim, `plan`'s steps make a `breakdown.md` of 2,446 words, not the estimated 1,970, so the several-story orchestrator path is 5,592 words against 4,950 (+13.0%). The maintainer accepted it until the language pass after the structural load cuts. The other paths meet their bounds: one-story −0.2%, per-story −0.0%, one FIS −0.3%, plan run +3.0%.*

*Amended 2026-09-26 on re-measurement, after the structural load cuts and the review fix rounds: one-story +0.8%, per-story +1.2%, one FIS +1.6%, plan run +5.4%, several-story +14.4%. The maintainer holds every path at that measured ceiling until the language pass.*

*Amended 2026-09-28 on re-measurement, after the `--auto` reversal (`5e4b580`), the ask-site clarity edits (`5f3582b`, `preflight.md` +55 words in all) and the regression-audit fixes: `unattended-runs.md` now loads only under `--auto`, so an attended path no longer carries it. Attended: one-story −2.0%, per-story −3.8%, one FIS −4.1%, several-story +10.1%. Under `--auto`: +2.3%, +1.7%, +2.0%, +16.5%. These are the held ceilings until the language pass.*

*Amended 2026-09-28, after the language pass (the readability pilot on `spec` and `exec-spec`), measured by each path's load list in `SKILL.md`. The attended per-story figure retires: `--batch` always runs with `--auto`, and it no longer loads `plan.schema.json`. These are the held ceilings:*

| Path | Attended | `--auto` |
|---|---|---|
| One-story (7,324) | −2.1% (7,171) | +2.2% (7,487) |
| Per-story `--batch` (5,810) | – | −6.4% (5,440) |
| Several-story (4,950) | +7.2% (5,307) | +13.6% (5,623) |
| Several-story, existing `plan.json` | +10.9% (5,488) | +17.3% (5,804) |
| One FIS (5,149) | −8.2% (4,727) | −2.1% (5,043) |
| Plan run (3,463) | −9.2% (3,146) | −0.0% (3,462) |
| Plan run, `--worktree` | +6.8% (3,697) | +15.9% (4,013) |
- 54 files and about 229 lines change in this repo, including the evals.
- DartClaw's `plan-and-implement.yaml:96` must switch to `andthen:spec` in the same release.

**Unchanged**

- `clarify` writes the PRD.
- The quick track is two commands with no PRD.
- `prd: null`.
- The `plan.json` v2 schema and the FIS format. Existing bundles need no migration.

## Alternatives Considered

1. **A – merge with the one-story procedure kept in the `spec` and `exec-spec` bodies, and the several-story procedure in a reference.** Rejected. The several-story orchestrator would load +30% (4,942 → 6,422 words) and the plan-run orchestrator +49% (3,463 → 5,172), and both would carry the procedure they must delegate. Score 310.
2. **C – merge only the execution side.** Rejected. It removes one entry point but leaves the user's "one story or several?" choice at authoring, which is the decision the merge exists to remove. Score 365.
3. **One merged body with no references.** Rejected. The one-story path would load about 2,000 words it never runs.
4. **Floor option: keep four skills and sharpen the README's question.** Rejected. It keeps every accepted decision intact and costs nothing to migrate. But after 1.0 it becomes the permanent shape, with two entry points and a user-facing sizing decision the skills already make. Score 400; see the Decision.

## Settled open points

- `--tdd` passes through on a plan run. Before the merge `exec-plan` dropped it, and no reason was recorded.
- `--worktree` on a FIS is ignored and reported, per Still Current "No edge-case knobs, no strictness blocks".
- An unattended `OVERSIZE:` from a written source proceeds as one story. DartClaw's `spec-and-implement` depends on that.
- Eval case directories keep their names.
- Self-invocation (`spec` spawning `spec`) stays unambiguous because each dispatch line names the argument form it passes: "a fresh subagent that invokes the `andthen:spec` skill with …".

## Reopens

If `spec` is shown misjudging the story count in a way `OVERSIZE:` after authoring does not catch – the `spec-two-stories` eval case is the check.

## Project Compliance

- **Product Decision Rule.** It extends what exists (the `OVERSIZE:` route and `plan` deciding the count) rather than adding machinery. It removes two entry points and one user decision, and the words loaded per path stay roughly flat.
- **Settled decisions.** One author per story, the single writer, the fresh-session contract words, and "Specs are co-produced with the story breakdown" (strengthened: one run cuts, authors and reviews) all hold.
- **Architecture.** Skills stay self-contained (`docs/ARCHITECTURE.md:60`), and references stay one level deep, so `story-worktrees.md` is linked from the `exec-spec` body's load site; `plan-run.md` names only when in the run to read it.

## References

- Research, 2026-09-25: before the merge, counting the body and every reference a path opens, the one-story `spec` path loaded 7,324 words, a per-story `--batch` author 5,810, and `exec-spec` on one FIS 5,149 – the baselines behind the per-path percentages above.
- Related: ADR-014, ADR-018.
