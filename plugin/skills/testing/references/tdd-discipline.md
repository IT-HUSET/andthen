# TDD Discipline — Red, Green, Refactor

Sources: Kent Beck (*Test-Driven Development: By Example*, 2002; *Tidy First?*, 2023), Dave Farley (*Modern Software Engineering*), Addy Osmani (anti-rationalization framing).

Home mode: `tdd`. Also used whenever a test drives *new* behavior.


## TDD is a design technique

**Primary output: better design. Test suite is a side-effect** (Farley). A failing test forces you to specify behavior from the outside, which surfaces modularity questions:

- What are this unit's inputs and outputs?
- What collaborators does it actually need?
- What seams must exist for a test to observe behavior?

Hard-to-test code is coupled code. See `farley-framework.md` §"Testability as Architecture Proxy". If a unit needs heavy mocks, shared state, or reflection to exercise, the architecture is the problem — not the test.


## The loop

### 1. Red — failing test

Smallest test that expresses one piece of intended behavior.

- Run it. **Confirm it fails for the right reason.** `ReferenceError` for a missing function is fine; a wrong-assertion pass is a lie.
- The failure message is the test's first output. If a stranger couldn't diagnose the miss from it, rewrite the test.
- One behavior per test. "Given X, When Y, Then A and B and C" is three tests.

### 2. Green — minimum code to pass

Move the bar. Don't finish the feature.

Beck's three strategies, in order of preference:
1. **Obvious implementation** — clear and simple, write it directly.
2. **Fake it** — return a constant that passes. Next test forces generalization.
3. **Triangulation** — introduce abstraction only when two+ tests demand it.

If the "minimum code" is a full algorithm, the test is too big.

### 3. Refactor — with tests green

Tidy code and tests while green. Typical moves:

- **Remove duplication** (tests↔production, tests↔tests). Beck's **Once and Only Once** drives the refactor step: duplication names an abstraction that hasn't emerged yet.
- **Rename for intent.** Test names carry domain vocabulary first — migrate them into production code.
- **Extract the seam the next test needs.** Design emerges here.

**Tidy First — separate structural from behavioral change** (Beck, 2023). Every commit is either:

- **Structural** (rename, extract, inline, reorder) — no observable behavior change.
- **Behavioral** — changes what the code does.

Never mix them. If a mid-loop refactor turns out to be load-bearing for the next red test, land it as its own commit first, re-run tests, then start the red step.

Rules:
- **Refactor without a green bar = debugging, not refactoring.** Revert to green first.
- Run tests after every structural edit. A 10-minute batch that breaks three tests in ways you can't localize is undisciplined.


### Named principle: *Make it work, make it right, make it fast*

Beck's three-phase order:

1. **Make it work** — pass the test. Any code that moves the bar.
2. **Make it right** — refactor on green. Remove duplication, rename, clarify.
3. **Make it fast** — only if measurement shows it matters.

Skipping step 2 ("it works, ship it") or starting at step 3 ("this will be slow") is the source of most TDD mistakes. The loop enforces the order.


## Anti-rationalization table

Every skip-worthy step has a seductive excuse:

| Excuse | Rebuttal |
|---|---|
| "I'll write the test after — I know what to build." | Red skipped → the test asserts whatever the code does. Regression gate at best, not a spec. |
| "Trivial change, no test needed." | Most regressions come from "trivial" changes. Writing the test costs less than one revert. |
| "Hard to test — let me ship and come back." | Hard-to-test = coupled. You won't come back. The friction is the bug report. |
| "Mocking this would take longer than the implementation." | Architectural feedback. Introduce the seam; the test is the forcing function. |
| "TDD is slower for exploratory work." | Spikes are fine. Delete the spike, then TDD. Don't promote untested spikes. |
| "The test duplicates the implementation." | The implementation is leaking structure the test shouldn't know. Re-assert on observable behavior. |


## When NOT to TDD

Skip the cycle (and document why) for:

- **Spikes / prototypes** with a known delete-date. Don't merge to main.
- **Formatting, renames, pure tidying** — no behavior change.
- **Static config / router tables** — test the behavior they enable, not the declaration.
- **Generated code** — test the generator.
- **Behavior only visible end-to-end, already covered by an E2E test** — red-first still applies, just at the E2E level.


## Signals — TDD done well

- Test names read as spec sentences: `transfer_rejects_insufficient_balance`.
- Production code has the shape the tests implied — no speculative methods, no dead branches.
- Refactoring is frequent and small.
- Cycles take minutes. A stuck cycle means the behavior under test is too big.


## Signals — TDD gone wrong

- Tests mock everything the code touches — nothing real is exercised.
- Tests break on internal renames — testing structure, not behavior.
- A "refactor" step that silently changed behavior.
- Long stretches of red. The step was too big.
