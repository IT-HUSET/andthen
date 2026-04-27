# Product Requirements Document Template

> Use this template as the baseline shape for `prd.md`.
> Keep the required sections. Adapt optional subsections to the project, but do not collapse functional requirements into vague prose.
> Focus on what must be true for users and the business. Put implementation-level architecture details in companion research, not in the PRD.


# Product Requirements Document: [Project Name]

> **Context**: [link to clarification, issue, backlog item, roadmap entry, or source requirements]
> **Related Assets**: [ADRs, design system, wireframes, research docs if they materially shape the requirements]


## Executive Summary
- **Problem**: [Clear statement of the user/business problem, ideally with quantified impact]
- **Vision**: [What the finished outcome enables]
- **Target Users**: [Primary users / personas]
- **Success Metrics**: [Specific measurable outcomes]


## Problem Definition

### Problem Statement
[Explain the current pain, why it matters, and what failure looks like if nothing changes.]

### Evidence & Context
- [Observed user pain, business driver, support volume, workflow friction, etc.]
- [Relevant constraints or timing context]


## Scope

### In Scope
- [Capability included in this effort]
- [Capability included in this effort]

### Out of Scope
- [Explicit non-goal]
- [Deferred follow-up]

### MVP Boundary
[Describe the smallest release that still solves the problem.]


## Functional Requirements

### User Stories

| ID | Story | Acceptance Criteria | Priority |
|----|-------|---------------------|----------|
| US01 | [As a ..., I want ..., so that ...] | [Testable outcome] | Must / P0 |

### Feature Specifications

#### FR1: [Feature Name]
**Description**: [What capability is required]

**Acceptance Criteria**:
- [ ] [Observable outcome]
- [ ] [Observable outcome]

**Inputs / Outputs**:
- **Inputs**: [User input, events, upstream data, optional parameters]
- **Outputs**: [UI state, records, API responses, side effects]

**Validation**:
- [Validation rules, limits, rejection conditions]

**Error Handling**:
- [Expected handling for failures, invalid inputs, or unavailable dependencies]

**Priority**: Must / Should / Could and P0 / P1 / P2

#### FR2+: [Repeat as needed]

### User Flows
1. [Primary flow]
2. [Alternate or edge flow]
3. [Failure or recovery flow]

### UI Wireframes _(if applicable)_
- [Link to wireframe or design asset]

### Data Requirements _(if applicable)_
- [Entities, fields, relationships, retention, reporting needs]


## Non-Functional Requirements

| Category | Requirement | Threshold / Target |
|----------|-------------|--------------------|
| Performance | [Expectation] | [e.g. p95 < 300ms] |
| Reliability | [Expectation] | [target] |
| Security | [Expectation] | [target] |
| Usability | [Expectation] | [target] |


## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| [Boundary condition] | [Expected handling] |
| [Failure mode] | [Expected handling] |


## Constraints & Assumptions

### Constraints
- [Technical, regulatory, staffing, timeline, platform, or compatibility constraint]

### Assumptions
- [Business assumption]
- [User assumption]
- [Technical assumption]

### Dependencies

| Dependency | Why It Matters |
|------------|----------------|
| [System, team, vendor, document] | [Impact on delivery or behavior] |


## Decisions Log

| Decision | Rationale | Alternatives Considered |
|----------|-----------|-------------------------|
| [Decision] | [Why this was chosen] | [Alternatives rejected] |
