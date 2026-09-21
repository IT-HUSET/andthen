# Product Requirements Document Template

> Baseline shape for `prd.md`. Keep every `##` section below; adapt optional subsections to the project, but never collapse functional requirements into vague prose.


# Product Requirements Document: [Project Name]

> **Source**: [stable source identity: resolved path, full URL, or inline digest]
> **Context**: [durable references only – GitHub issue, backlog item, roadmap entry. Transient discovery artifacts are inlined in substance, never cited by path.]
> **Related Assets**: [ADRs, design system, wireframes – where they materially shape the requirements]


## Executive Summary

> **Human review entry point**: this section alone must convey *what is being built, for whom, why, and what is explicitly not in scope*, in ≤1 rendered page.

- **Problem**: [One sentence from `Problem Definition > Problem Statement`, with its quantified impact]
- **Vision**: [`Problem Definition > Desired Outcome` in one line – what is different once this is solved]
- **Target Users**: [From `Problem Definition > Target Users`]
- **Success Metrics**: [The 3–5 headline rows of `## Success Metrics`, metric and target only]

### Capabilities at a Glance
One line per **Feature Specification** (FR), in priority order. ID and feature name match the canonical `#### FRn: [Feature Name]` heading exactly, so anchor links and string traces resolve. User stories without a backing FR do not appear here.

> **Summary-not-source contract**: every line here derives from a canonical row below – a fact appearing nowhere below moves into its detail section – and the inline `(Must / P0)` tag agrees with the FR block's `**Priority**:` line; on conflict the canonical line wins and the summary is the bug.

- **FR1: [Feature Name]** _(Must / P0)_ – [single-line description of the capability]
- **FR2: [Feature Name]** _(Should / P1)_ – [single-line description]
- *(one line per FR. Past ~10 FRs, group by theme heading or list only Must/Should and point to `Functional Requirements`.)*

### Scope Highlights
Mirror `## Scope` when it lists ≤4 items per bucket; past that, pick the most contested or most easily misread.
- **In scope**: [2–4 bullets or a short comma-separated list of capabilities]
- **Out of scope**: [2–4 bullets naming the most likely-misread non-goals]
- **MVP boundary**: [single line – the smallest release that still solves the problem]

### Key Constraints, Assumptions & Dependencies
The 2–4 items that materially shape scope or priority, drawn from `Constraints`, `Assumptions`, or `Dependencies` in `## Constraints & Assumptions`, where the full lists live.
- [Constraint, assumption, or dependency – prefix with the bucket if not obvious, e.g. *Dependency:* vendor X must expose API Y]
- [Constraint, assumption, or dependency]


## Problem Definition

### Problem Statement
[The current pain, why it matters, and what failure looks like if nothing changes.]

### Target Users
- [Who has the problem – role or persona, and the job they are trying to get done when it bites]

### Desired Outcome
[What is different for those users and for the business once this is solved – the result, not the feature. Every requirement below serves it.]

### Evidence & Context
- [Observed user pain, business driver, support volume, workflow friction, etc.]
- [Relevant constraints or timing context]


## Success Metrics

How the Desired Outcome will be known to have happened. Outcomes, not outputs: "support tickets about X down 40%" is a metric, "export shipped" is a deliverable.

| Metric | Baseline | Target | How observed |
|--------|----------|--------|--------------|
| [User or business result that should move] | [Today's value, or `unknown`] | [Value and by when] | [Where the number comes from] |


## Scope

### In Scope
- [Capability included in this effort]
- [Capability included in this effort]

### Out of Scope
- [Explicit non-goal]
- [Deferred follow-up]

### MVP Boundary
[The smallest release that still solves the problem.]


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
- **Inputs**: [user input, events, upstream data, parameters]
- **Outputs**: [UI state, records, API responses, side effects]

**Validation**:
- [Validation rules, limits, rejection conditions]

**Error Handling**:
- [Failures, invalid inputs, unavailable dependencies]

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

| Scenario | Expected Behavior | Recovery Path |
|----------|-------------------|---------------|
| [Boundary condition] | [Expected handling] | [How the user/system recovers] |
| [Failure mode] | [Expected handling] | [How the user/system recovers] |


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


## Open Questions

- [Question precise enough to be closed as written by a later amendment, the plan, or an architecture trade-off]
- Area to revisit: [area not yet stateable as a question] – [what would sharpen it]


## Decisions Log

| Decision | Rationale | Alternatives Considered |
|----------|-----------|-------------------------|
| [Decision] | [Why this was chosen] | [Alternatives rejected] |
