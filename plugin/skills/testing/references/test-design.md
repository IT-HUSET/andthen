# Test Design – Behavior Over Implementation

Canon: GOOS (Freeman & Pryce), Dodds' Testing Trophy, Farley's diagnosability and friction-as-feedback, Beck's Test Desiderata, assumed known.

## The one rule

**Test behavior, not implementation.** A behavior-first test and an implementation-coupled test look identical while green – the difference shows up on refactor. Dodds: *"The more your tests resemble the way your software is used, the more confidence they can give you."*

Implementation-coupled signals, any one of which is a rewrite: assertions on internal call counts (unless the repetition *is* the behavior, e.g. retries); a red bar after a rename, reorder, or extract-method; assertions on output formatting nothing downstream consumes; assertions added because the test was red, not because the behavior is defined.

## Level signal in the Arrange block

When Arrange outgrows Act + Assert combined, one of these is true: wrong level – promote to integration; too many responsibilities in the unit – split it; setup belongs in a named fixture (`a_customer_with_overdue_invoices`, not `setup_db_with_data_3`).

## Mocks

Each mock declares "this collaborator's behavior is not part of what I'm proving". Mock at system edges only – filesystem, network, clock, randomness; your own repositories and services take a real implementation with a fixture or an in-memory fake. Elaborate stubbing encodes the call graph: replace with a fake or promote to integration. **Never mock the unit under test** – needing to means the unit was mis-identified.

## Diagnosability

The cost of a test is paid when it fails. Name = spec sentence (`rejects_withdrawal_when_balance_insufficient`); one assertion per behavior; a custom message on any non-obvious expected value; group by scenario (`describe("when account has overdue invoices")`), not by method.

## Audit vocabulary

Beck's Test Desiderata (2019) name the twelve properties a test trades between – Isolated, Composable, Fast, Inspiring, Writable, Readable, Behavioral, Structure-insensitive, Automated, Specific, Deterministic, Predictive. Use the names to say *why* an existing test feels wrong before rewriting it; the trades are real and the project's Testing Strategy says which it tolerates.

## Domain-specific patterns

- **Property-based testing** (hypothesis, fast-check, proptest) – pure-ish functions with too-large input spaces: parsers, serialization, ordering, idempotency.
- **Golden / snapshot tests** – rendered output. Dangerous as defaults: bugs sail through rubber-stamped snapshot updates, so require explicit per-file updates, never `--update-all`.
- **Contract tests** – at service boundaries, both sides asserting against a shared contract rather than each other's mocks.
- **Type-level tests** (`expectTypeOf`, `tsd`) – libraries where the type *is* the contract.
