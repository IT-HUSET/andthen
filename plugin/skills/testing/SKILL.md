---
description: Test strategy, coverage, test authoring, and test-first (red-green-refactor) discipline, including the Prove-It bugfix flow and FIS scenario → test mapping – suites at every level, E2E included. Trigger on 'write tests for this', 'TDD this', 'prove it with a test'.
argument-hint: "[--mode strategy|tdd|prove-it] [target/scope]"
---

# Testing

Prove behavior with the smallest tests that prove it.

## Input

`$ARGUMENTS` minus flags is the target or scope. `--mode strategy|tdd|prove-it` picks the mode, else the request's wording does; with neither, or when unclear, the mode is `write`.

- `write` (default) – author tests for existing behavior, retrofitted.
- `tdd` – drive new behavior test-first: red → green → refactor.
- `prove-it` – the bugfix flow: a failing test reproduces the defect before any production change.
- `strategy` – author the project's `Testing Strategy` document. It writes no tests.

Read and follow:

- `strategy`: [`levels-and-strategy.md`](references/levels-and-strategy.md), and for a question it asked that no one answered, [`unattended-runs.md`](../../references/unattended-runs.md) § Recording an assumption.
- `tdd` or `strategy`: [`tdd-discipline.md`](references/tdd-discipline.md).
- `prove-it` or `strategy`: [`prove-it-pattern.md`](references/prove-it-pattern.md).
- Every mode, before choosing or binding a test command: [`verification-evidence.md`](../../references/verification-evidence.md).

## Rules

- Print each recommended skill invocation as a complete, paste-ready line in the host's syntax, including its target path or request and required arguments.

`Testing Strategy` and `Key Dev Commands` are Project Document Index entries.

- **Prove-It before claiming a fix**: a failing test that goes green is the only proof.
- **The `Testing Strategy` document** (default `docs/TESTING-STRATEGY.md`) names this project's levels, fixtures, before-merge bar, and gotchas, never commands: those stay in `Key Dev Commands`. A convention it states is never re-derived from general testing theory.
- **A missing document**, or one silent on the level or convention in question, is named the way `verification-evidence.md` names a missing command. Apply the defaults below, and wherever the test work is reported, say what was missing and that the defaults stood in, because silent defaults read to the next agent as this project's own decisions.
- **Falsifiability** – removing the protected behavior makes its owning test fail. Before declaring coverage done, break the implementation and watch each test go red (a mutation tool the project already runs, scoped to the changed files, does this: each surviving mutant is a missing assertion); the retrofit `write` path is where this slips most. Three shapes cause it:
  - **Tautological assertion** – the expected value comes from the code under test: its output, its logic re-derived, or a stub's canned value asserted back. Take it from the requirement or a hand-worked example; a characterization test (`prove-it-pattern.md`) pins current output on purpose and goes once the fix lands.
  - **Vacuous assertion** – it never runs (an un-awaited async test, a callback never called, a loop over an empty collection, a swallowed assertion error) or checks nothing a bug would change (a not-null where any value passes, an absence check on a fixture without the value).
  - **Success-only double** – a mock or fake that only succeeds, so the caller's error paths never run. Give it the real dependency's failure modes – errors, timeouts, empty or partial results, constraint violations – or use the real dependency.
- **Anti-Cheat Invariant.** Tests guard against agent-introduced regressions only while they keep telling the truth. Never delete a test except with the whole surface it covers, disable it (`.skip`, `xit`, `@Disabled`, equivalents), or pass by weakening assertions. A flaky test is reported, never skipped on your own call: quarantine happens only on a person's decision, per the `Testing Strategy` document. A wrong test is rewritten; a test whose subject was intentionally removed is replaced with a test for the new behavior.

## Workflow

`strategy` runs step 1, then follows its reference's Workflow in place of steps 2 to 4, applying their rubric.

1. **Read the `Testing Strategy` document and the `Key Dev Commands` rows**, per `verification-evidence.md`. Gate: each level, convention, and command the work binds to is stated there or named missing.

2. **Choose the level.** Level follows trust boundaries, not file count. A **trust boundary** is a line you do not own the other side of at runtime – filesystem, DB engine, third-party API, browser event loop, OS. Crossing none is a unit test, one at a time is integration, many (usually with a browser or the full stack) is E2E. Pick the lowest effective level the `Testing Strategy` document allows.

   The default is the sociable test: real collaborators, doubles only at trust boundaries. Behavior that lives at a boundary (a query, a file format) is proved against the real dependency, and an HTTP API through a contract test, since a fake of it proves the fake. E2E is reserved for journeys the business cannot ship without, because they cost minutes and rot fastest.

   A test whose label and boundaries disagree is slow, fragile, or proves nothing:
   - **"Integration" that is E2E** – crosses services, a browser, or a queue. Split it into contract tests at each boundary plus per-service integration.
   - **"E2E" that is unit** – asserts a value that never leaves the backend. Demote it.

   Rank what to cover by the blast radius of a silent failure and by change frequency. A global coverage percentage as a target is a vanity metric; uncovered changed lines are a real signal. Refuse coverage theatre: tests that fail Falsifiability, above. Gate: each planned test names its level, and no label disagrees with its boundaries.

3. **Author**, following the mode's reference where it has one. Every mode follows the design below. Canon, assumed known: GOOS (Freeman & Pryce), Dodds' Testing Trophy, Farley's diagnosability and friction-as-feedback, Beck's Test Desiderata.

   **Structure-insensitive: test behavior, not implementation.** A test drives the public interface and asserts what a caller observes, so only a behavior change turns it red; a structure-sensitive one looks identical while green. Any one of these signals means a rewrite:
   - reaching past the public interface – private members, internal state, collaborators the caller never sees;
   - assertions on internal call counts, unless the repetition *is* the behavior (retries);
   - a red bar after a rename, reorder, or extract-method;
   - assertions on output formatting nothing downstream consumes.

   **An Arrange block outgrowing Act and Assert combined** means one of three things. Stubs stand where real collaborators belong: use them, promoting to integration when they cross a boundary. The unit carries too many responsibilities: split it. Or the setup belongs in a named fixture (`a_customer_with_overdue_invoices`, not `setup_db_with_data_3`).

   **Mocks.** Mock at system edges only – filesystem, network, clock, randomness. Your own services run real. A repository may be an in-memory fake for its callers, and is itself proved against the real engine. Never mock the unit under test: needing to means the unit was mis-identified.

   **Snapshots** need explicit per-file updates, never `--update-all`, because bugs sail through rubber-stamped updates.

4. **Prove.** Break the implementation per Falsifiability and watch each test go red. Reuse the project's framework; any new tool must run in CI without extra ceremony. The run-one-test row of `Key Dev Commands` is the invocation a scenario `Proof` binds to. Gate: every test went red with its behavior removed, then green with it restored.

   **FIS scenario → test mapping:**
   - Reuse a bound `**Proof**:` only when its target resolves and runs; its annotated state then overrides the mode's initial state.
   - A report, screenshot, or other documented artifact may support an unbound scenario, but is never a Proof binding.
   - Where nothing executable can observe the outcome, the FIS declares that with an `inspect: path:LINE` Proof rather than dressing an artifact as a test.
   - A purely visual case names that supporting artifact and routes to the `andthen:visual-validation` skill.

## Output

Behavior covered, the level chosen and why, key tests added or updated, the red failure or green-parity evidence quoted for `tdd` and `prove-it`, each tidy with its file, the document path and sections written for `strategy`, pass/fail counts where available, and remaining critical gaps.
