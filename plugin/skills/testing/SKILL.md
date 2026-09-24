---
description: Test strategy, coverage, test authoring, and test-first (red-green-refactor) discipline, including the Prove-It bugfix flow and FIS scenario → test mapping – suites at every level, E2E included. Trigger on 'write tests for this', 'TDD this', 'prove it with a test', 'test coverage'.
argument-hint: "[--mode strategy|tdd|prove-it] [target/scope]"
---

# Testing

Prove behavior with the smallest tests that prove it. **Prove-It before claiming a fix** – a failing test that goes green is the only proof.


`$ARGUMENTS` minus flags is the target or scope.


## MODES

Default to `write` when unsure.

| Mode | Purpose | Loads |
|------|---------|-------|
| `strategy` | Author the project's `Testing Strategy` document, asking the user the choices the code cannot answer. No tests written. | `references/levels-and-strategy.md`, `references/test-design.md`, `references/tdd-discipline.md`, `references/prove-it-pattern.md` |
| `write` (default, no flag) | Author tests for existing behavior. | `references/test-design.md` |
| `tdd` | Drive new behavior test-first: red → green → refactor. | `references/test-design.md`, `references/tdd-discipline.md` |
| `prove-it` | Bugfix flow. Failing test reproduces the defect before any production change. | `references/test-design.md`, `references/prove-it-pattern.md` |

Every mode reads the `Testing Strategy` document per [`testing-strategy.md`](../../references/testing-strategy.md). That document carries this project's conventions; `strategy` authors it, to the procedure in `references/levels-and-strategy.md`, and records an unanswered question per [`automation-mode.md`](../../references/automation-mode.md) § Recording an assumption.


## DECISION FRAMEWORK

- **Prove each test fails without the implementation** – break the impl, watch it red – before declaring coverage done. A test that stays green against a broken impl proves nothing; the retrofit `write` path is where this slips most.
- **Test-first** for `tdd` and `prove-it`; retro-fit for `write`.
- **Pick the lowest effective level** the `Testing Strategy` document allows.


## SCENARIO → TEST MAPPING

- Reuse a bound `**Proof**:` only when its target resolves and runs; its annotated state then overrides the mode's initial state.
- A report, screenshot, or other documented artifact may support an unbound scenario, but is never a Proof binding.
- Where nothing executable can observe the outcome, the FIS declares that with an `inspect: path:LINE` Proof rather than dressing an artifact as a test.
- A purely visual case names that supporting artifact and routes to the `andthen:visual-validation` skill.


## FRAMEWORK SELECTION

Reuse the project's framework; any new tool must run in CI without extra ceremony. Before introducing one, read the `Key Dev Commands` document per [`verification-evidence.md`](../../references/verification-evidence.md) – it names what the project already runs, and its run-one-test row is the invocation a scenario `Proof` binds to.


## CALLER INTEGRATION

Runs in the caller's context by default – continuity matters for `tdd` and `prove-it`; for fresh-context isolation the caller wraps the invocation in a subagent.

The `Testing Strategy` document is the artifact for `strategy`; the tests themselves are the artifact for `write` / `tdd` / `prove-it`.


## OUTPUT FORMAT

Behavior covered, the level chosen and why, key tests added or updated, the red failure or green-parity evidence quoted for `tdd` / `prove-it`, the document path and sections written for `strategy`, pass/fail counts where available, and remaining critical gaps.

