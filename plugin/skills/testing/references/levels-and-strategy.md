# Levels and Strategy – Where to Test, What to Cover

Canon: Dodds' Testing Trophy, Farley's feedback economics, Fowler's pyramid critique, *Software Engineering at Google* on coverage and flaky tests. This file carries the `strategy` mode's procedure and the budgets and coverage ranking it judges against; level definitions, the wrong-level signals, and the coverage-theatre refusals are in `testing-strategy.md`.

## Writing the document

1. Read the project's test tree, its `Key Dev Commands` Testing rows, the CI workflow, and the `Product` document's Proportionality facts – stage and scale size the before-merge bar, so a prototype does not inherit a production one. What the project already does is the content; the canon is how you judge it, never what you transcribe.
2. Ask the user, in one round, what none of those answers – these are owner decisions, not facts in the code: the areas and user journeys whose silent failure costs most (they get named tests and the few E2E journeys); whether test-first is required; a coverage gate on changed lines, or none; the flaky-test quarantine policy – who approves, for how long (never an agent's own call, per the Anti-Cheat Invariant); which of two conflicting conventions wins; the framework, when there are no tests yet. Give each question your recommendation; a reply of "default" takes them all. When no one can answer (a caller running `--auto`, or a subagent), or a question goes unanswered, write the recommendation as an `ASSUMPTION:` line (`automation-mode.md` § Recording an assumption), because an unmarked default reads to the next agent as a choice this project made.
3. Write what is *true of this project*: levels in use, when each applies, and whether each boundary runs real (a container, a temp dir) or a fake; framework and fixture conventions; what must have a test before merge, with the step-2 answers; known gotchas. Link the commands, never restate them – a second copy of a command drifts from the row that owns it.
4. Create the document at its **Project Document Index** location when absent, with those four sections and a link line to `Key Dev Commands`. Update it in place when present: rewrite the sections this run learned something about, leave the rest byte-identical, so a hand-written convention survives a re-run.

## Level budgets

| Level | Crosses | Time budget | Quantity |
|---|---|---|---|
| **Unit** | No trust boundary, no real IO. | Milliseconds; thousands in seconds. | Many. |
| **Integration** | One trust boundary at a time. | 100ms to a few seconds; hundreds in a minute or two. | Moderate – the ones that matter. |
| **E2E** | Many boundaries, often a real browser. | Seconds each; dozens take minutes. | Few. |

Static checks (types, lint, dependency audits) sit under the trophy and catch a class of bugs dynamic tests do not. **Farley's caveat**: integration slower than a couple of minutes stops developers running it locally – parallelize, or demote some to unit. This skill designs E2E suites; the project runs them through its own `Key Dev Commands` rows.

## Coverage ranking

Rank by blast radius of a silent failure (money, data loss, security, legal, user-visible correctness) against change frequency: high/high first and integration-heavy, high/low next (unit may suffice when logic-dense), low/high lightly, low/low left to types and lint. Structural risk (deep inheritance, many callers, cycles) and irreversibility (durable-state mutation) move a target up.
