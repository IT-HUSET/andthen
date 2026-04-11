# Feature Implementation Specification Template


## Feature Overview and Goal
{{1-2 sentences: what needs to be built and why}}

{{If technical research was produced during spec creation, include this reference line. Remove if no research doc exists.}}
> **Technical Research**: [technical-research.md](./technical-research.md) _(codebase patterns, architecture analysis, API research)_


## Success Criteria (Must Be TRUE)
> Each criterion must have a defined proof path — at least one Scenario (for behavioral criteria) or a task Verify line (for structural criteria). If you can't define how to prove it, the criterion is too vague.
- [ ] {{Observable truth from user's perspective}}
- [ ] {{Verifiable system behavior}}
- [ ] {{Measurable technical requirement}}

### Health Metrics (Must NOT Regress)
- [ ] {{Existing tests continue to pass}}
- [ ] {{Performance baseline not degraded}}
- [ ] {{Existing API contracts / interfaces unchanged (unless explicitly scoped)}}


## Scenarios

> Concrete examples of expected behavior that serve as both requirement and test specification (Proof-of-Work — see authoring guidelines).

### {{Scenario Name}}
- **Given** {{precondition / system state}}
- **When** {{triggering action or event}}
- **Then** {{observable outcome}}

### {{Edge Case / Error Scenario Name}}
- **Given** {{precondition or boundary state}}
- **When** {{boundary condition or error trigger}}
- **Then** {{expected handling behavior}}

_Write 3-7 scenarios. Cover the happy path, key edge cases, and at least one error/failure case. Skip only for configuration-only work with no branching logic (e.g. env config, static asset changes)._


## Scope & Boundaries

### In Scope
- {{Core functionality to be built}}
- {{Integration points to be created}}

### What We're NOT Doing
- {{Out of scope item - be specific}}
- {{Existing functionality not to be modified}}

### Agent Decision Authority (optional -- include when scope boundaries are ambiguous)
- **Autonomous**: {{Decisions the agent can make}}
- **Escalate**: {{Decisions requiring human input}}


## Architecture Decision

{{For simple decisions (obvious from project patterns), use compact format:}}

**We will**: {{approach}} -- {{one-line rationale}} (over {{rejected alternatives}})

{{For genuine trade-offs (2+ viable alternatives), use full format:}}

**We will**: {{chosen approach}}
**Rationale**: {{why this approach, given constraints}}
**Alternatives considered**:
1. **{{Alt 1}}** -- rejected: {{reason}}
2. **{{Alt 2}}** -- rejected: {{reason}}

{{If covered by an existing ADR, reference it: `See ADR: docs/adrs/001-foo.md`}}


## Technical Overview

> High-level decisions and key references only. Detailed codebase analysis, API specifics, and implementation research belong in the **Technical Research** document.

### UI/UX Design (if applicable)
{{Describe UI changes, screens, interactions, user flows}}

### UI Mockups/Wireframes (if applicable)
{{Links to wireframes or simple ASCII mockups}}

### Data Models (if applicable)
{{Describe models, fields, types, and relationships in natural language. No pseudocode.}}

### Integration Points (if applicable)
{{How this integrates with existing systems or APIs}}


## References & Constraints

### Documentation & References
```
# type | path/url | why needed
file   | src/components/Modal.tsx:45-78    | Pattern for dialog handling
file   | src/api/users.ts:12-34            | API structure to follow
url    | https://docs.example.com/auth     | OAuth flow reference
doc    | docs/architecture/adr-001.md      | Auth architecture decision
wire   | docs/specs/wireframes/login.html  | UI layout for login screen
```

### Constraints & Gotchas
- **Constraint**: {{Known limitation}} -- Workaround: {{specific solution}}
- **Avoid**: {{Common mistake or anti-pattern}} -- Instead: {{correct approach}}
- **Critical**: {{Framework/library limitation}} -- Must handle by: {{approach}}


## Implementation Plan

Tasks are organized into **Execution Groups** -- clusters of related tasks executed by a single sub-agent.
Groups marked **[P]** can run in parallel with sibling groups at the same dependency level.
Tasks within a group execute sequentially.

> **Vertical slice ordering**: First group produces a thin but working end-to-end path. Subsequent groups widen the slice.

### Execution Groups

_Examples -- note how tasks describe outcomes, not code changes:_

#### G1: Core Data Pipeline <- [depends: none]
- [ ] **TI01** Event ingestion endpoint accepts and validates incoming payloads
  - Follow API pattern at `src/api/users.ts:12-34`; reuse existing validation middleware
  - **Verify**: `Test: POST /events with valid payload returns 201; invalid payload returns 422 with field-level errors`

- [ ] **TI02** Events persisted to storage with idempotency guarantee
  - Use existing repository pattern at `src/repos/base.ts:8-25`; dedup on event ID
  - **Verify**: `Test: sending same event twice produces exactly one stored record`

#### G2: Query Interface [P] <- [depends: G1]
- [ ] **TI03** Events queryable by type, time range, and source with pagination
  - Follow query builder pattern at `src/repos/users.ts:40-65`
  - **Verify**: `Test: query with type filter returns only matching events; pagination cursor works across pages`

_Replace examples above with your actual tasks. Format: outcome + context line + behavioral Verify._

#### G1: {{Group Name}} <- [depends: none]
- [ ] **TI01** {{Outcome that must be TRUE when done}}
  - {{1-2 lines of context: constraints, pattern reference (file:line), key decisions}}
  - **Verify**: {{Behavioral assertion that fails if outcome not achieved}}

#### G2: {{Group Name}} [P] <- [depends: G1]
- [ ] **TI02** {{Outcome}}
  - {{Context}}
  - **Verify**: {{Assertion}}

### Testing Strategy
> Derive test cases from the **Scenarios** section. Each scenario maps to one or more test cases. Tag with execution group for pairing.
- [G1] Scenario: {{scenario name}} → {{test description}}
- [G2] Scenario: {{scenario name}} → {{test description}}
- [edge] Scenario: {{scenario name}} → {{edge case test description}}

### Validation
> Standard validation (TV01-TV05: code review, testing, visual validation, quality review, remediation) is handled by exec-spec.
> Only add feature-specific validation requirements below if the standard levels are insufficient.

- {{Feature-specific validation requirement, if any}}


## Final Validation Checklist

- [ ] **All success criteria** met
- [ ] **All tasks** fully completed, verified, and checkboxes checked
- [ ] **No regressions** or breaking changes introduced
- [ ] **UI verified** to match requirements (if applicable)
