# QA Testing Methodology

Core testing approach for strategy, test implementation, and verification. Optimize for meaningful coverage with the least complexity that still proves the behavior.

## Decision Framework

1. Inspect existing test infrastructure before adding anything new.
2. Identify the highest-risk behavior that is currently unproven.
3. Choose the lowest effective test level.
4. Add tests incrementally and keep them runnable in the real project environment.
5. Leave the codebase with clearer, more maintainable coverage than you found.

## Testing Levels

| Level | When to Use | Focus |
|-------|-------------|-------|
| **Unit** | Pure logic, calculations, transformations, policy rules | Fast proof of behavior in isolation |
| **Integration** | Boundaries between modules, services, DB, API, filesystem | Real collaboration between parts |
| **E2E** | Critical user journeys or release-risk flows | User-visible behavior across the stack |

Default to the lowest level that can genuinely prove the requirement.

## Test Writing Principles

- Cover happy path first, then the riskiest edge case, then a meaningful failure or rejection path.
- Prefer tests that describe behavior, not implementation details.
- Make failures easy to diagnose from the test name and assertions.
- Extend existing tests and fixtures before inventing parallel patterns.
- For new behavior, prove the test would fail without the implementation when practical.

## Scenario -> Test Mapping

When working from FIS scenarios:
- **Given** -> setup, fixtures, or initial state
- **When** -> the action under test
- **Then** -> the observable assertions

Each important scenario should have at least one test or equivalent proof artifact. If a scenario cannot be tested directly, document what evidence will stand in for it and why.

## Framework Selection Heuristics

- Use the project's existing framework and conventions whenever possible.
- If the project has no testing setup, choose common stack-appropriate defaults that match the repo's language and tooling.
- Prefer tools the current team can run in CI without extra ceremony.
- Check CLAUDE.md and local docs before introducing a new framework.

## Output Format

### Testing Summary
What behavior was covered, at what level, and why that level was chosen.

### Implementation
Key tests added or updated, including notable fixtures or patterns.

### Coverage & Quality
- what is now proven
- notable edge/error cases covered
- pass/fail status and counts when available

### Recommendations
- remaining critical gaps
- next-best additions if more coverage is needed
