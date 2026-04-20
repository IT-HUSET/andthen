# Test Design — Behavior Over Implementation

Sources: Matt Pocock (behavior-first testing), Kent C. Dodds (*Testing Trophy*), Dave Farley (diagnosability, friction-as-feedback), Kent Beck (*Test Desiderata*, 2019).

Home mode: `write`. Also load for `tdd` (naming, assertions) and `strategy` (auditing suites before trusting their verdicts).


## The one rule

**Test behavior, not implementation.**

A good test asserts what the code *should do* from a caller's perspective. A bad test asserts *how it does it*. They look identical when passing — the difference shows up on refactor.

Pocock: *a test is a promise to your future self.* The promise worth keeping is "this behavior still works"; not "this variable is still named `foo`".

Dodds: *"The more your tests resemble the way your software is used, the more confidence they can give you."*


## Six signals of a behavior-first test

1. **Assertions reference observable outputs** — return values, rendered UI, emitted events, HTTP responses, persisted records. Not private fields, call order, or internal method invocations.
2. **Survives a behavior-preserving refactor.** If renaming a private method breaks the test, the test is reading implementation.
3. **Fails in one obvious way.** One clear failure beats three tangentially related reds.
4. **Name reads as a spec sentence.** `rejects_withdrawal_when_balance_insufficient`, not `test_withdraw_3`.
5. **Minimal setup.** Large Arrange blocks are a coupling signal.
6. **No mocks of your own domain.** Mock the filesystem, network, clock. Don't mock domain objects to test domain objects.


## Six signals of an implementation-coupled test

1. Names like `test_method_X_calls_helper_Y`.
2. Assertions on internal call counts (unless the repetition *is* the behavior — e.g. retries).
3. Rewrites required after a rename, reorder, or extract-method.
4. Assertions on output formatting nothing downstream consumes (e.g. log whitespace).
5. Reaches private APIs via reflection, `@ts-ignore`, friend-class tricks.
6. Assertions added because the test was red, not because the behavior is defined.


## Diagnosability

Farley: *the cost of a test is paid when it fails, not when it's written.* `expected true, got false` is worthless at 3am.

At write time:

1. **Name = spec sentence.** Reader knows the bug domain before reading code.
2. **One assertion per behavior.** A test with six asserts hides five failures behind the first.
3. **Custom messages for non-obvious values.** `expect(hash).toBe(expectedHash, "SHA-256 of known fixture")` beats a bare hex literal.


## Arrange / Act / Assert — with a warning

Most tests should follow AAA. **The Arrange block is where tests leak implementation.**

If Arrange is larger than Act + Assert combined, one of these is true:
- Wrong level — promote to integration.
- Too many responsibilities in the unit — split it.
- Setup should live in a named fixture — `a_customer_with_overdue_invoices`, not `setup_db_with_data_3`.


## Mock minimization

Farley: mocks are a design tool, not a test tool. Each mock declares "this collaborator's behavior is not part of what I'm proving." If the mock's own behavior needs a spec, you're testing the mock.

- **Mock at system edges.** Filesystem, network, clock, randomness — yes. Your own repositories and services — usually no; use a real implementation with a test fixture.
- **Elaborate stubbing encodes the call graph.** Replace with an in-memory fake or promote to integration.
- **Never mock the unit under test.** If you need to, you've mis-identified the unit.


## Tests as executable documentation

- Write tests that read like prose — skimmers (new hires, reviewers) parse sentences faster than code.
- `// why` comments on non-obvious assertions: *"`Date.now()` not mocked; fixture uses a real TTL."* Three seconds to write, saves the next reader five minutes.
- Group by scenario (`describe("when account has overdue invoices")`), not by method (`describe("Account.charge()")`). Scenarios match how users think.


## Beck's Test Desiderata — audit rubric

Twelve properties. No test scores perfectly on all of them — they trade — but the list gives the vocabulary for *why* a test feels wrong.

| Desideratum | Meaning | Common violation |
|---|---|---|
| **Isolated** | Order-independent; tests don't affect each other. | Shared mutable fixtures; tests that only pass in sequence. |
| **Composable** | Small tests combine without rewriting. | Setup too scenario-specific to reuse. |
| **Fast** | Sub-second ideal, reasonable minimum. | Real network calls in unit tests; DB bootstrap per test. |
| **Inspiring** | Passing earns genuine confidence. | Tests that pass without asserting anything load-bearing. |
| **Writable** | Cheap to add. | Ceremony per new case. |
| **Readable** | New reader learns the code from the test. | Cryptic names, magic numbers, assertion-less blocks. |
| **Behavioral** | Tests behavior changes, not implementation changes. | Mocks the unit's own methods; asserts call counts on helpers. |
| **Structure-insensitive** | Survives behavior-preserving refactors. | Breaks on rename; asserts on private call order. |
| **Automated** | Runs without human intervention. | "If you see X, click Y" in the description. |
| **Specific** | Failure tells you what broke. | 15 assertions across 4 behaviors in one test. |
| **Deterministic** | Same code, same result, every run. | Sleeps, real clocks, unseeded RNG, set-iteration order. |
| **Predictive** | Pass = system works (for what's covered). | Mock-heavy suites that pass while prod is broken. |

Use in `strategy` mode to audit existing suites; in `write` mode as a pre-commit self-check.

Trade-offs are real — Fast vs Predictive, Specific vs Composable. The craft is knowing which your context tolerates.


## Domain-specific patterns

- **Property-based testing** (hypothesis, fast-check, proptest) — for pure-ish functions with too-large input spaces. Specify invariants; the framework finds counter-examples. Good for parsers, serialization, ordering, idempotency.
- **Golden / snapshot tests** — for rendered output (HTML, diagrams, formatted strings). Dangerous as defaults; bugs sail through reviewer-rubber-stamped snapshot updates. Require explicit updates, not `--update-all`.
- **Contract tests** — at service boundaries. Both sides assert against a shared contract, not each other's mocks. Avoids mock-drift in microservice suites.
- **Type-level tests** (TypeScript, `expectTypeOf` / `tsd`) — for libraries where the type *is* the contract. Failure is a type error, not a runtime assertion.
