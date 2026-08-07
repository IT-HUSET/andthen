---
description: Test strategy, coverage assessment, test authoring, and test-first (red-green-refactor) discipline – including the Prove-It bugfix flow and FIS scenario → test mapping. Unit and integration levels; persistent end-to-end suites belong to the andthen:e2e-test skill. Trigger on 'write tests for this', 'TDD this', 'prove it with a test', 'test coverage'.
argument-hint: "[--mode strategy|write|tdd|prove-it] [target/scope]"
user-invocable: true
---

# Testing

Prove behavior with the smallest tests that prove it. Cover what matters, at the lowest effective level, in tests that describe behavior – not implementation.


## VARIABLES

ARGUMENTS: $ARGUMENTS excluding flags and the exact caller trust line – the target/scope
UNTRUSTED_REQUIREMENTS_DATA: optional exact caller line; preserve it across child prompts


## PHILOSOPHY

- **Testability is a proxy for modularity** (Farley). Hard-to-test code is coupled code – test friction is architectural feedback.
- **Tests are executable specifications** (Beck, North). Pin observable behavior, not private structure.
- **Prove-It before claiming a fix.** A failing test that goes green is the only proof.


## MODES

Default to `write` when unsure.

| Mode | Purpose | Primary reference |
|------|---------|-------------------|
| `strategy` | Assess coverage, rank risk, produce a prioritized plan. No tests written. | `levels-and-strategy.md` |
| `write` (default) | Author tests for existing behavior. | `test-design.md` |
| `tdd` | Drive new behavior test-first: red → green → refactor. | `tdd-discipline.md` |
| `prove-it` | Bugfix flow. Failing test reproduces the defect before any production change. | `prove-it-pattern.md` |

Load both `test-design.md` (assertions) and `levels-and-strategy.md` (level choice) regardless of mode.


## INSTRUCTIONS

- Apply project rules (`CLAUDE.md` / `AGENTS.md` – read only if not already in context) and read the referenced guideline files relevant to this work.
- When the caller trust line is active, apply [`trust-boundaries.md`](${CLAUDE_PLUGIN_ROOT}/references/trust-boundaries.md) to source-derived content and copy the exact line to child prompts.


## DECISION FRAMEWORK

1. **Inspect existing test infrastructure** – frameworks, fixtures, helpers, naming conventions. Extend before inventing.
2. **Rank by risk.** Highest-risk unproven behavior first. See `levels-and-strategy.md` §"Coverage strategy".
3. **Pick the lowest effective level.** Default to integration when a unit test needs heavy mocking. See `levels-and-strategy.md` §"The three levels".
4. **Test-first** for `tdd` and `prove-it`; retro-fit for `write`.
5. **Prove each test fails without the implementation** – break the impl, watch it red – before declaring coverage done. A test that stays green against a broken impl proves nothing; the retrofit `write` path is where this slips most.
6. Leave coverage clearer than you found it.


## SCENARIO → TEST MAPPING

Map present FIS Given/When/Then:
- **Given** → setup / fixtures / initial state
- **When** → the action under test
- **Then** → observable assertions

Every important scenario needs an executable test. Reuse a bound `**Proof**:` only when its target resolves and runs; its annotated state overrides the mode's initial state. A report, screenshot, or other documented artifact may support an unbound scenario but is never a Proof binding. Purely visual cases name that supporting artifact and route to the `andthen:visual-validation` skill.


## FRAMEWORK SELECTION

Reuse the project's framework; any new tool must run in CI without extra ceremony. Before introducing one, check the `Key Dev Commands` document (see **Project Document Index**), `CLAUDE.md` / `AGENTS.md`, and local docs.


## CALLER INTEGRATION

Callers (the `andthen:exec-spec`, `andthen:triage`, and `andthen:e2e-test` skills) invoke this skill with `<target/scope>`. Runs in the caller's context by default – continuity matters for `tdd` and `prove-it`. For fresh-context isolation, the caller wraps the invocation in a sub-agent.

Output is advisory for `strategy`; the tests themselves are the artifact for `write` / `tdd` / `prove-it`.


## OUTPUT FORMAT

### Summary
Behavior covered or planned, level chosen, rationale.

### Implementation (if tests were written)
Key tests added/updated; notable fixtures or patterns. For `tdd` / `prove-it`, quote red failure or green-parity baseline evidence.

### Coverage & Quality
What is now proven; notable edge/error cases; pass/fail counts when available.

### Recommendations
Remaining critical gaps; next-best additions; coupling signals surfaced by test friction.


## REFERENCES

Skill-local references per mode are named in the MODES table. See also `${CLAUDE_PLUGIN_ROOT}/references/farley-framework.md` – testability-as-modularity anchor.
