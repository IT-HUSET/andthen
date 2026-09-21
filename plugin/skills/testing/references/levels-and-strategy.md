# Levels and Strategy – Where to Test, What to Cover

Canon: Dodds' Testing Trophy, Farley's feedback economics, Fowler's pyramid critique. This file carries the `strategy` mode's procedure and the budgets and coverage ranking it judges against; level definitions, the wrong-level signals, and the coverage-theatre refusals are in `testing-strategy.md`.

## Writing the document

1. Read the project's test tree, its `Key Dev Commands` Testing rows, and the CI workflow. What the project already does is the content; the four canon references are how you judge it, never what you transcribe.
2. Write what is *true of this project*: levels in use and when each applies, framework and fixture conventions, what must have a test before merge, known gotchas. Link the commands, never restate them – a second copy of a command drifts from the row that owns it.
3. Create the document at its **Project Document Index** location when absent, with those four sections and a link line to `Key Dev Commands`. Update it in place when present: rewrite the sections this run learned something about, leave the rest byte-identical, so a hand-written convention survives a re-run.

## Level budgets

| Level | Crosses | Time budget | Quantity |
|---|---|---|---|
| **Unit** | No trust boundary, no real IO. | Milliseconds; thousands in seconds. | Many. |
| **Integration** | One trust boundary at a time. | 100ms to a few seconds; hundreds in a minute or two. | Moderate – the ones that matter. |
| **E2E** | Many boundaries, often a real browser. | Seconds each; dozens take minutes. | Few. |

Static checks (types, lint, dependency audits) sit under the trophy and catch a class of bugs dynamic tests do not. **Farley's caveat**: integration slower than a couple of minutes stops developers running it locally – parallelize, or demote some to unit.

## Coverage ranking

Rank by blast radius of a silent failure (money, data loss, security, legal, user-visible correctness) against change frequency: high/high first and integration-heavy, high/low next (unit may suffice when logic-dense), low/high lightly, low/low left to types and lint. Structural risk (deep inheritance, many callers, cycles) and irreversibility (durable-state mutation) move a target up.

## Persistent E2E suites

This skill designs an E2E suite; the project runs it through its own `Key Dev Commands` rows.
