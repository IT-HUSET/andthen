# Decisions: Workflow and skills

Rationale, evidence, history, and reopen conditions for the **Workflow and skills** bullets in [DECISIONS.md](../DECISIONS.md) § Still Current. Each decision is stated there; a section here holds only what would not fit its one line.

## Where work starts: two questions, and `plan` answers one

The two questions are independent, which is why `plan` decides the story count, before it loads either procedure, rather than the user picking a skill by it (ADR-020). `prd` merged into `clarify` because users picked between the two by how complete their input looked. The plan records the PRD's path in `prd`, `null` only when there is none. `decide` is `clarify`'s closing command when its PRD leaves such a design choice open, and Preflight's recommendation when authoring surfaces one (ADR-025).

A PRD is never mandatory: an issue that already specifies the work is its source, and a PRD for every feature would be ceremony. `sourceRefs` already carry an issue URL, so `prd` needs no URL form; ADR-028 relies on both.

## `clarify` writes the brief too, and has no unattended form

`--brief` works on any subject. `intent.md` was dropped at the `prd` merge because 0.x users picked between two skills by how complete the input looked; a flag on one skill is a stated choice.

Reopens if an unattended pipeline needs a PRD `plan` cannot give it.

## One authoring subagent per story

Batching siblings to amortize the shared preamble was rejected: the benchmark behind that claim was never committed, and its accounting is not comparable.

Reopens if a comparable benchmark shows preamble cost dominating.

## One no-spec change skill

`implement-fix` is `remediate-findings` renamed with the request as its one added input form. `quick-implement` retired into it rather than the reverse, because the Intent anchor, routing gate, and findings re-check were most of the remediation body and the inline form fit in about ten lines, while grafting remediation onto `quick-implement` as a mode would have inherited free text's "implement until requirements are met" as the default scope posture.

Reopens if the inline form accretes a second body, or running the phases for a one-line fix costs more than it catches.

## No model-only or user-only skills

The load-site exception covers ADR-020's branches: `plan`'s one-story and breakdown references, `exec-plan`'s story and plan-run references. `disable-model-invocation` is ruled out because it blocks Skill-tool invocation, and `now-what` routes to `exec-plan`.

Reopens if a skill-invocable third tier ships.
