# Decisions: Authoring

Rationale, evidence, history, and reopen conditions for the **Authoring** bullets in [DECISIONS.md](../DECISIONS.md) § Still Current. Each decision is stated there; a section here holds only what would not fit its one line.

## PRD acceptance criteria are EARS rules, FIS scenarios their examples

Adopted 2026-10-18. The FIS self-review checks that every source acceptance criterion has a scenario, and the Validation and Error Handling lists the EARS rules replaced were not criteria, so nothing carried an error case into one. The gain in caught error and state cases is inferred, not measured.

Reopens on recorded plan runs whose scenarios still miss the PRD's `If` rules.

## Preflight closes, never holds

Every story Preflight closes stays `pending` with its FIS, and what an assumption leaves unclear is the executor's to settle by best reading, so there is no `Closure:` verdict, hold, or reviewer re-entry per answer. `exec-plan`'s pre-run checks are *admission*; the preflight name stays with the interview 0.x users know.

Reopens on a run where an executed unattended assumption shipped behaviour the plan-level review did not catch.

## The model judges which forks need the user

Contract-owned forks asked by rule: `plan`'s uncovered screens and its slice-or-keep question, and whether `exec-plan` and `ship` start a feature branch before committing on the remote's default branch.

On 2026-09-24 three rounds of per-case asking rules moved the `plan` eval to 1 of 5. A fixture with one fork that has no defensible default passed on the first two runs with no skill change, and the third failed only on a rubric that contradicted the skill. That is why an asking eval's rubric never requires a question a capable model can default.

Reopens on a run where a fork with no defensible default shipped as an assumption.

## Scope trades are a self-review Note and a preflight question, not a skill

Never blocking, because the design meets the requirements as written. The reviewer is the only agent holding both the design and the whole PRD, so a separate skill would only add surface.

Reopens if trade Notes go unanswered in practice.

## Document review is an authoring gate, not a `review` lens

The rubric stays out of the author-loaded `fis-authoring-guidelines.md`, so the author never reads the rubric it is judged by. There is no `--mode doc`: invoking `review` loaded roughly 9,000–12,000 instruction words to apply a few mechanical edits, and its matrix, report, and routing had no reader on those paths. Routing is a `blocks:` attribute on each Note, and bundle coverage a per-FIS roster the breakdown's gate checks.

Reopens if a hand-written PRD or FIS needs a standalone review that `clarify` amendment or a `plan` rerun cannot give, or a several-story `plan` eval shows the roster missing a FIS-local defect.

## `plan` has no re-entry handling

No revise-in-place, live-work guard, or regeneration that keeps story state. The user finishes or resets a started story first, and a Cookbook recipe says what to write. Supersedes "Unstarted specs are re-authorable" (2026-09-29, maintainer ruling).

## A FIS carries only what the executor would miss

The reason is signal and drift, not execution cost: reading a 6,000-word FIS is 2–5% of an `exec-plan` run, whose cost is turns × context. **Need-to-know** and by-reference `Verify` coverage are the authoring rules that carry it.

Tried and dropped: a reviewer cut duty, a contradiction class in the self-review, lifting the Architecture Decision line cap (the section doubled).

Reopens if an executor starts handing FIS excerpts to workers.

## Over-engineered work is discarded, and the PRD is cut first

The first evals harness (16k lines, never ran) was redone small rather than pruned, because a PRD prescribing release-grade guarantees regenerates the same bloat.

## Rejected concepts are Product non-goals, not a registry

Reopens if a project needs per-request provenance a bullet cannot carry.
