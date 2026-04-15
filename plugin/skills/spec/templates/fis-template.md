# Feature Implementation Specification Template


## Feature Overview and Goal
{{1-2 sentences: what needs to be built and why}}

{{If technical research was produced during spec creation, include this reference line. Remove if no research doc exists.}}
> **Technical Research**: [.technical-research.md](./.technical-research.md) _(codebase patterns, architecture analysis, API research)_


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

_Write 3-7 scenarios. Cover the happy path, key edge cases, and at least one error/failure case. After drafting, apply the **negative-path checklist** from the authoring guidelines: verify coverage for omitted optional inputs, no-match filter/selector cases, and rejection paths for external integrations — add scenarios for any gaps found. Skip scenarios only for configuration-only work with no branching logic (e.g. env config, static asset changes)._


## Scope & Boundaries

### In Scope
_Every scope item must be covered by at least one scenario (behavioral items) or task with a Verify line (structural items). If you list it here but can't write coverage for it, either remove it or flag it as underspecified._
- {{Core functionality to be built}}
- {{Integration points to be created}}

### What We're NOT Doing
_Keep this to 3-5 explicit non-goals or deferrals. Each item should name the exclusion and why it is excluded now._
- {{Out of scope item - be specific}} -- {{reason it is deferred or excluded}}
- {{Existing functionality not to be modified}} -- {{reason}}

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

{{If covered by an existing ADR, reference it using the `ADRs` location from the **Project Document Index**. Example: `See ADR: <path-from-ADRs-entry>/001-foo.md`}}


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

List implementation tasks in execution order. A later task may depend on a type, interface, or component established by an earlier task; state that dependency explicitly in the later task's context line.

> **Vertical slice ordering**: First tasks should produce a thin but working end-to-end path. Later tasks widen the slice.
> **Size discipline**: Most strong FIS files stay in the 100-300 line range. If a draft is pushing past roughly ~400 lines or >12 implementation tasks, split it at spec time rather than expecting `exec-spec` to recover later.

### Implementation Tasks

_Examples -- note how tasks describe outcomes, not code changes:_

- [ ] **TI01** Event ingestion endpoint accepts and validates incoming payloads
  - Follow API pattern at `src/api/users.ts:12-34`; reuse existing validation middleware
  - **Verify**: `Test: POST /events with valid payload returns 201; invalid payload returns 422 with field-level errors`

- [ ] **TI02** Events persisted to storage with idempotency guarantee
  - Use existing repository pattern at `src/repos/base.ts:8-25`; dedup on event ID
  - **Verify**: `Test: sending same event twice produces exactly one stored record`

- [ ] **TI03** Events queryable by type, time range, and source with pagination
  - Follow query builder pattern at `src/repos/users.ts:40-65`; depends on TI01/TI02 data model
  - **Verify**: `Test: query with type filter returns only matching events; pagination cursor works across pages`

_Replace examples above with your actual tasks. Format: outcome + context line + behavioral Verify._

- [ ] **TI01** {{Outcome that must be TRUE when done}}
  - {{1-2 lines of context: constraints, pattern reference (file:line), key decisions}}
  - **Verify**: {{Behavioral assertion that fails if outcome not achieved}}

- [ ] **TI02** {{Outcome}}
  - {{Context — if this task depends on TI01 or another earlier task, state it explicitly here}}
  - **Verify**: {{Assertion}}

### Testing Strategy
> Derive test cases from the **Scenarios** section. Each scenario maps to one or more test cases. Tag with the task ID(s) the test proves — the executing agent uses these tags to know which tests must go red→green for each task.
- [TI01] Scenario: {{scenario name}} → {{test description}}
- [TI02] Scenario: {{scenario name}} → {{test description}}
- [TI01,TI02] Scenario: {{scenario name}} → {{edge case test description}}

### Validation
> Standard validation (build/test checks, code review, visual validation, and 1-pass remediation) is handled by exec-spec.
> Only add feature-specific validation requirements below if the standard levels are insufficient.

- {{Feature-specific validation requirement, if any}}

### Execution Contract
- Implement tasks in listed order. Each **Verify** line must pass before proceeding to the next task.
- Prescriptive details (column names, format strings, file paths, error messages) are exact — implement them verbatim.
- Proactively use sub-agents for non-coding needs: documentation lookup, architectural advice, UX/UI guidance, build troubleshooting, research — spawn in background when possible and do not block progress unnecessarily.
- After all tasks: run the applicable project validation gates for the feature — build/tests/lint-analysis where those checks exist and are relevant — and keep `rg "TODO|FIXME|placeholder|not.implemented" <changed-files>` clean.
- Mark task checkboxes immediately upon completion — do not batch.


## Final Validation Checklist

- [ ] **All success criteria** met
- [ ] **All tasks** fully completed, verified, and checkboxes checked
- [ ] **No regressions** or breaking changes introduced
- [ ] **UI verified** to match requirements (if applicable)
