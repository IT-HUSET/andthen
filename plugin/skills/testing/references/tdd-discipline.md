# TDD Discipline – Red, Green, Refactor

Canon, assumed known: Beck (*TDD by Example*, *Tidy First?*, *Canon TDD*, "Augmented Coding: Beyond the Vibes"), Farley (*Modern Software Engineering*).

**TDD is a design technique**; the suite is the side-effect. Extensive mocking or infrastructure in a test is a coupling signal about the code, not a test-design problem.

## Workflow

### 1. Red

Write the smallest test expressing one behavior. Run it and **confirm it fails for the right reason**: a `ReferenceError` for a missing function is fine, a passing wrong assertion is a lie. If a stranger could not diagnose the miss from the failure message, rewrite the test. "Given X, When Y, Then A and B and C" is three tests.

**Anti-pattern: Horizontal Slicing.** Turn exactly one list item into a runnable test, make it pass, continue; never write every test up front.

### 2. Green

Move the bar; do not finish the feature. Use the obvious implementation, else fake it, else triangulate. If the minimum code is a full algorithm, the test is too big.

### 3. Refactor, on green only

Tidy *the code this cycle wrote* and the tests that drove it, plus Boy Scout tidies. A Boy Scout tidy in a file the change touches is small and behavior-preserving, or fixes an obvious small bug under a test that fails first. In a TDD cycle, an obvious small bug joins the test list; anything larger is reported. Once and Only Once drives the step.

**Tidy First** – a mid-loop refactor that turns out load-bearing for the next red test lands as its own commit first, tests re-run, then the red step starts. Refactoring without a green bar is debugging: revert to green first.

## Named principles

- **Living Test List** – when execution discovers a *requirement* rather than a test case, it goes through the `andthen:exec-plan` skill's Discovered Requirements channel before the test or code depending on it.

## When not to TDD

Skip the cycle, saying why, for spikes with a delete-date (never merged), formatting and pure tidying, static config and router tables (test the behavior they enable), and generated code (test the generator). Behavior visible only end-to-end still takes red-first, at the E2E level.
