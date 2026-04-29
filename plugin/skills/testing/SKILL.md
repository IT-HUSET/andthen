---
description: "Use when you need test strategy, coverage assessment, test authoring, or test-first (red-green-refactor) discipline — including the Prove-It bugfix flow and FIS scenario → test mapping. Covers unit and integration levels; defer persistent end-to-end suites to the `andthen:e2e-test` skill. Trigger on 'write tests for this', 'cover this module', 'TDD this', 'test-first', 'red-green-refactor', 'prove it with a test', 'assess test coverage', 'improve coverage', 'test strategy for this'."
argument-hint: "[--mode strategy|write|tdd|prove-it] [target/scope]"
user-invocable: true
---

# Testing

Prove behavior with the smallest tests that prove it. Cover what matters, at the lowest effective level, in tests that describe behavior — not implementation.


## VARIABLES

ARGUMENTS: $ARGUMENTS (strip any flag tokens like `--mode` before interpreting the remainder as the target/scope)


## PHILOSOPHY

- **Testability is a proxy for modularity** (Farley). Hard-to-test code is coupled code — test friction is architectural feedback.
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

Always cross-load `test-design.md` when writing assertions and `levels-and-strategy.md` when picking a level.


## DECISION FRAMEWORK

1. **Inspect existing test infrastructure** — frameworks, fixtures, helpers, naming conventions. Extend before inventing.
2. **Rank by risk.** Highest-risk unproven behavior first. See `levels-and-strategy.md` §"Coverage strategy".
3. **Pick the lowest effective level.** Default to integration when a unit test needs heavy mocking. See `levels-and-strategy.md` §"The three levels".
4. **Test-first** for `tdd` and `prove-it`; retro-fit for `write`.
5. **Prove the test would fail without the implementation.** Otherwise you haven't proven anything.
6. Leave coverage clearer than you found it.


## SCENARIO → TEST MAPPING

Working from FIS scenarios:
- **Given** → setup / fixtures / initial state
- **When** → the action under test
- **Then** → observable assertions

Every important scenario needs at least one test or a documented proof artifact. For scenarios that can't be tested directly (e.g. purely visual), name the stand-in and flag visual checks for the `andthen:visual-validation-specialist` agent.


## FRAMEWORK SELECTION

- Use the project's existing framework and conventions.
- If no setup exists, pick stack-appropriate defaults that match the repo's tooling.
- Prefer tools that run in CI without extra ceremony.
- Check CLAUDE.md and local docs before introducing a new framework.


## CALLER INTEGRATION

Callers (`exec-spec`, `triage`, `e2e-test`) invoke this skill as `/andthen:testing <target/scope>`. Runs in the caller's context by default — continuity matters for `tdd` and `prove-it`. For fresh-context isolation, the caller wraps the invocation in a `general-purpose` sub-agent.

Output is advisory for `strategy`; the tests themselves are the artifact for `write` / `tdd` / `prove-it`.

Persistent E2E suites are out of scope — hand off to the `andthen:e2e-test` skill.


## OUTPUT FORMAT

### Summary
Behavior covered or planned, level chosen, rationale.

### Implementation (if tests were written)
Key tests added or updated; notable fixtures or patterns. For `tdd` / `prove-it`, quote the red-step failure message.

### Coverage & Quality
- what is now proven
- notable edge/error cases covered
- pass/fail counts when available

### Recommendations
- remaining critical gaps
- next-best additions
- coupling signals surfaced by test friction


## REFERENCES

- `tdd-discipline.md` — Red/Green/Refactor, Tidy First, triangulation, anti-rationalization (Beck, Farley).
- `prove-it-pattern.md` — failing-test-first bugfix flow, characterization tests, Beyonce Rule (Feathers; *Software Engineering at Google*, 2020).
- `test-design.md` — behavior over implementation, Beck's Test Desiderata, diagnosability, mock minimization (Freeman & Pryce, Dodds, Farley, Beck).
- `levels-and-strategy.md` — unit/integration/E2E by trust boundary, Testing Trophy, risk×change matrix (Dodds, Farley).
- `${CLAUDE_PLUGIN_ROOT}/references/farley-framework.md` — testability-as-modularity anchor.
