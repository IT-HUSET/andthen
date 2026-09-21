# ADR-016: One no-spec change skill

**Status:** Accepted

**Recorded:** 2026-09-14

## Context

Two skills changed code without a spec: `quick-implement` took a sentence, `remediate-findings` took a review report. They produced the same output – a verified change in the working tree – and the user picked between them by input shape, not by what they wanted done.

The open sub-question from 2026-09-13 was directional: whether remediation's distinct behavior (the Fix bar, `NO-OP`, the report annotation, the tech-debt write) fits in ten lines inside `quick-implement` as an input form, and keep both if not. It does not – those four are most of the remediation body. The test is met in the other direction: the inline form fits in about ten lines inside the remediation phases, once `--tdd` and PR creation go.

The two inputs also had opposite scope postures. Free text said "implement until requirements are met"; a report said "a `Routing: Note` is a boundary". Merging them needs that resolved, not averaged.

## Decision

**`implement-fix` is `remediate-findings` renamed, with one added input form.** Its six phases, its Fix bar, its `NO-OP`, its `## Remediation Status` annotation, and the tech-debt write are unchanged. `quick-implement` retires with no alias.

**The one rule: an inline request is its own findings list, every item routed `Fix` by the user.** Each stated requirement becomes one finding with the request as its evidence; Phases 2–6 then run exactly as for a report. That resolves the scope posture – the user's request *is* the Fix set, so scope is still never invented by the agent, and anything the request did not state is a `NOTICED BUT NOT TOUCHING:` / `MISSING REQUIREMENT:` block, never an edit. No mode file, no second body.

Four things carry over from `quick-implement`, each about a line, placed where a phase already does the equivalent: the scope guard that routes a plan- or PRD-sized request to `spec → exec-spec` or `clarify → plan`; the fuzzy-ask-to-verifiable-goal move before coding; tests-first where a branch is added; and the `Tech Debt` read when the change lands in a listed area.

## Rationale

One name, one body, one output. The remediation phases are the discipline worth keeping – the Intent anchor, the routing gate, the findings re-check – and a sentence-sized change loses nothing by running them.

Rejected: **grafting remediation onto `quick-implement` as a mode file** – heavier than the rename, and it inherits the wrong scope posture as the default. **Keeping both** – the 2026-09-13 test resolves against it now that the direction is settled.

## Consequences

The 1.0 core plugin drops to 17 skills. `--tdd` is gone (`andthen:testing --mode tdd` remains for strict TDD), as are PR creation and commit-on-request – the verified change stays in the working tree for the user, as remediation already left it. The visual-validation dispatch and the three-stop-and-amend counter go with them; the scope guard covers what the counter caught.

A one-sentence fix now runs the remediation phases and names their references. Accepted: heavier than the 101-line `quick-implement`, lighter than any two-mode design.

`andthen:review --fix`, the `exec-plan` `Next:` line, `now-what`, the `backlog-triage` Agent Brief, the docs, the overview figure, the glossary, and the migration table follow the rename. ADR-014's "`review` → `remediate-findings` enforces open findings" reads as `review` → `implement-fix` from here.

Reopens if the inline form accretes a second body, or if running six phases for a one-line fix proves to cost more than it catches.

## Evidence

- Current contract: [`plugin/skills/implement-fix/SKILL.md`](../../plugin/skills/implement-fix/SKILL.md).
