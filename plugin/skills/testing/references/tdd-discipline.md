# TDD Discipline – Red, Green, Refactor

Canon: Beck (*TDD by Example*, *Tidy First?*, *Canon TDD*, "Augmented Coding: Beyond the Vibes"), Farley (*Modern Software Engineering*), assumed known.

**TDD is a design technique** – the suite is the side-effect. Extensive mocking or infrastructure in a test is a coupling signal about the code, not a test-design problem.

## The loop

### 1. Red

The smallest test expressing one behavior. Run it and **confirm it fails for the right reason** – a `ReferenceError` for a missing function is fine, a passing wrong assertion is a lie. If a stranger could not diagnose the miss from the failure message, rewrite the test. "Given X, When Y, Then A and B and C" is three tests.

**Anti-pattern: Horizontal Slicing.** Writing every test up front and every implementation afterward removes the observed-failure step from all of them and commits the test structure before the code reveals its shape. Canon TDD keeps the slice vertical: turn exactly one list item into a runnable test, make it pass, continue.

### 2. Green

Move the bar, do not finish the feature – obvious implementation, else fake it, else triangulate. If the minimum code is a full algorithm, the test is too big.

### 3. Refactor, on green only

Tidy *the code this cycle wrote* and the tests that drove it. Anything outside this cycle's edits is out of scope per the Boy Scout rule in CRITICAL RULES; standalone cleanup of unrelated co-located code is the `andthen:simplify-code` skill's job. Beck's Once and Only Once drives the step: duplication this cycle introduced names an abstraction that has not emerged yet.

**Tidy First** – a commit is structural (rename, extract, inline, reorder) or behavioral, never both. A mid-loop refactor that turns out load-bearing for the next red test lands as its own commit first, tests re-run, then the red step starts. Refactoring without a green bar is debugging – revert to green first.

## Named principles

- **Living Test List** – Canon TDD adds items to the list as they are discovered. When execution discovers a *requirement* rather than a test case, it goes through the `andthen:exec-spec` skill's Discovered Requirements channel before the test or code depending on it.
- **Make it work, make it right, make it fast** – work = Green, right = Refactor-on-green; fast only when measurement shows it matters.
- **Anti-Cheat Invariant** – tests guard against agent-introduced regressions only while they keep telling the truth; Beck names the failure "the genie cheating" by disabling or deleting tests. Never delete a test, disable it (`.skip`, `xit`, `@Disabled`, equivalents), or pass by weakening assertions. A flaky test is reported, never skipped on the agent's own call; quarantine happens only on a person's decision, per the `Testing Strategy` document. A wrong test is rewritten; a test whose subject was intentionally removed is replaced with a test for the new behavior.

## When not to TDD

Skip the cycle, saying why, for spikes with a delete-date (never merged), formatting and pure tidying, static config and router tables (test the behavior they enable), and generated code (test the generator). Behavior only visible end-to-end still takes red-first, at the E2E level.
