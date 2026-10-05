# Levels and Strategy – Writing the Testing Strategy Document

Canon: Dodds' Testing Trophy, Farley's feedback economics, Fowler's pyramid critique, *Software Engineering at Google* on coverage and flaky tests. The canon is how you judge what the project does, never what you transcribe.

## Workflow

1. **Read what the project already does** – its test tree, its `Key Dev Commands` Testing rows, the CI workflow, and the `Product` document's Proportionality facts. Stage and scale size the before-merge bar, so a prototype does not inherit a production one. With the facts absent or `unknown`, say the anchor was unavailable and size the bar from what the project already runs.
2. **Ask the user, in one round, what none of those answer.** These are owner decisions, not facts in the code:
   - the areas and user journeys whose silent failure costs most – they get named tests and the few E2E journeys;
   - whether test-first is required;
   - a coverage gate on changed lines, or none; and a mutation gate on changed files – none unless the project already runs a mutation tool, because a full run is slow;
   - the flaky-test quarantine policy – who approves, and for how long (never an agent's own call, per the Anti-Cheat Invariant);
   - which of two conflicting conventions wins;
   - the framework, when there are no tests yet.

   Give each question your recommendation; a reply of "default" takes them all. When no one can answer, write the recommendation as an `ASSUMPTION:` line (`unattended-runs.md` § Recording an assumption). Gate: every question is answered or carries an `ASSUMPTION:` line.
3. **Write what is true of this project** – levels in use, when each applies, and whether each boundary runs real (a container, a temp dir) or a fake; framework and fixture conventions; what must have a test before merge, with the step-2 answers; known gotchas. Link the commands, never restate them: a second copy of a command drifts from the row that owns it.
4. **Create or update.** When the document is absent, create it at its **Project Document Index** location with those four sections and a link line to `Key Dev Commands`. When present, rewrite only the sections this run learned something about, so a hand-written convention survives a re-run. Gate: every other section is byte-identical.

## Level budgets

| Level | Crosses | Time budget | Quantity |
|---|---|---|---|
| **Unit** | No trust boundary, no real IO. | Milliseconds; thousands in seconds. | Many. |
| **Integration** | One trust boundary at a time. | 100ms to a few seconds; hundreds in a minute or two. | Moderate – the ones that matter. |
| **E2E** | Many boundaries, often a real browser. | Seconds each; dozens take minutes. | Few. |

Static checks (types, lint, dependency audits) sit under the trophy and catch a class of bugs dynamic tests do not.

**Farley's caveat**: integration slower than a couple of minutes stops developers running it locally – parallelize, or demote some to unit.

## Coverage ranking

Rank by the blast radius of a silent failure (money, data loss, security, legal, user-visible correctness) against change frequency:

- high blast radius, high change – first, integration-heavy;
- high blast radius, low change – next; unit may suffice when the logic is dense;
- low blast radius, high change – lightly;
- low blast radius, low change – left to types and lint.

Structural risk (deep inheritance, many callers, cycles) and irreversibility (durable-state mutation) move a target up.
