# Feature Implementation Specification Template

> **Purpose:**
> Executable specification optimized for AI agents – concise, actionable, reference-heavy.
>
> **Core Principles:**
> 1. **Intent over Implementation**: Describe outcomes, goals and context, not exact code changes — the implementing agent decides *how*
> 2. **References over Content**: Link to docs, code (file:line), and research – don't inline them
> 3. **Patterns by Reference**: Point to existing code patterns (file:line) rather than reproducing them
> 4. **Decisions, not Explanations**: State the decision, not lengthy rationale
> 5. **Validation at Execution**: Code is written during exec-spec, not spec
> 6. **Information Dense**: Keywords and patterns from the codebase, minimal prose
>
> **DON'Ts**
> - ❌ Code snippets longer than 5-10 lines – reference existing patterns instead
> - ❌ Inline documentation excerpts – link to the source
> - ❌ Verbose prose or explanations – be terse and actionable
> - ❌ Repeating information available elsewhere – reference it
> - ❌ Describing code changes or file creation steps – describe outcomes and goals instead
> - ❌ Over-engineering or out-of-scope functionality


## Feature Overview and Goal
{{Clear description of what needs to be built and why}}


## Success Criteria (Must Be TRUE)
State what must be observably TRUE when this feature is complete:
- [ ] {{Observable truth from user's perspective}}
- [ ] {{Verifiable system behavior}}
- [ ] {{Measurable technical requirement}}

### Health Metrics (Must NOT Regress)
Existing behaviors and baselines that must be preserved — guards against Goodhart-style optimization:
- [ ] {{Existing tests continue to pass}}
- [ ] {{Performance baseline not degraded}}
- [ ] {{Existing API contracts / interfaces unchanged (unless explicitly scoped)}}


## Scope & Boundaries

### In Scope
- ✅ {{Core functionality to be built}}
- ✅ {{Integration points to be created}}
- ✅ {{User interactions to be enabled}}

### What We're NOT Doing
- ❌ {{Out of scope item - be specific}}
- ❌ {{Feature explicitly not included}}
- ❌ {{Existing functionality not to be modified}}

### Anti-Patterns to Avoid
- ❌ Don't {{common mistake}} - instead {{correct approach}}
- ❌ Don't {{framework misuse}} - use {{proper pattern}}
- ❌ Don't {{reinvent wheel}} - use existing {{utility/pattern}}

### Agent Decision Authority (optional — include when scope boundaries are ambiguous)
- **Autonomous**: {{Decisions the agent can make — e.g. internal naming, data structures, file organization}}
- **Escalate**: {{Decisions requiring human input — e.g. new external dependencies, API contract changes, scope expansion}}


## Solution Architecture and Design

### Architecture Decision Record (ADR)
{{Links to relevant ADRs / _OR_ include details inline below (Decision, Rationale, Alternatives Considered)}}

#### Decision
**We will**: {{Chosen approach}}

#### Rationale
{{Why this approach best solves the problem given constraints}}

#### Alternatives Considered
1. **{{Alternative 1}}**: {{Brief description}}
- ❌ Rejected because: {{Specific reason}}
2. **{{Alternative 2}}**: {{Brief description}}
- ❌ Rejected because: {{Specific reason}}

### Technical Overview

#### Outline of New/Changed Files
```bash
# Show where new files/modules will be added or updated
{{Illustrate the changes with annotations}}
```

#### UI/UX Design (if applicable)
{{Describe any UI/UX changes, including new screens, UI components, interactions, or user flows}}

#### UI Mockups/Wireframes (if applicable)
{{Include links to existing wireframes and/or simple mockups/sketches in Markdown / Ascii format}}


#### Data Models & Structures (if applicable)
{{Describe new or modified data models, including fields and types etc}}
```
# Data model pseudocode
```

#### Integration Points (if applicable)
{{Describe how this integrates with existing systems or APIs}}


## Critical Documentation & Context

### Documentation & References
```
# Reference format: type | path/url | section | why needed
file   | src/components/Modal.tsx:45-78    | Pattern for dialog handling
file   | src/api/users.ts:12-34            | API structure to follow
url    | https://docs.example.com/auth     | OAuth flow reference
doc    | docs/architecture/adr-001.md      | Auth architecture decision
wire   | docs/specs/wireframes/login.html  | UI layout for login screen
```
> Keep this list focused – only include references that are essential for implementation.


### Known Constraints & Gotchas
- **Constraint**: {{Known limitation}} - Workaround: {{Specific solution}}
- **Gotcha**: {{Common mistake}} - Avoid by: {{Best practice}}
- **Critical**: {{Framework/library limitation}} - Must handle by: {{Specific approach}}


## Implementation Plan
Below is an overview of the tasks that make up the implementation plan.
**IMPORTANT:**
- Tasks are organized into **Execution Groups** – clusters of related tasks executed by a single sub-agent
- Tasks within a group execute sequentially. Groups marked **[P]** can run in parallel with sibling groups at the same dependency level
- Individual tasks retain their IDs (TI01, TI02...) for tracking. Check off task checkboxes (- [ ] → - [x]) as tasks are completed

### Execution Groups

> **Vertical slice ordering**: Order groups so the first group produces a thin but working end-to-end path through all layers. Subsequent groups widen the slice with additional cases, edge handling, and polish. The goal is a demoable result as early as possible.

_Examples — note how tasks describe outcomes, not code changes:_

#### G1: Project Foundation ← [depends: none]
- [ ] **TI01** Working Fresh project scaffold with dev server
  - Deno + Fresh framework, standard directory layout (routes/, islands/, components/, lib/)
  - Dev server, build, lint, and type-check tasks all operational
  - **Verify**: `deno task check` passes; `deno task start` serves on localhost

- [ ] **TI02** Supabase integration with server and browser clients
  - Authenticated Supabase access from both server routes and browser islands
  - Environment variables documented in .env.example
  - Follow pattern: `lib/db/client.ts:1-20`
  - **Verify**: Type-check passes; both clients importable from `lib/supabase/`

#### G2: Development Tooling [P] ← [depends: G1]
- [ ] **TI03** Linting, formatting, and E2E test infrastructure
  - Deno fmt/lint/check configured as runnable tasks
  - Playwright configured for E2E tests in tests/e2e/
  - **Verify**: `deno task lint` runs cleanly; Playwright config resolves

#### G3: Design System [P] ← [depends: G1]
- [ ] **TI04** Design system foundation matching ADR-002
  - Pico CSS + Google Fonts (Nunito Sans, Outfit) integrated
  - Custom theme variables (color, spacing, typography) per ADR-002
  - Responsive breakpoints configured
  - **Verify**: Dev server renders themed page; CSS custom properties inspectable in browser

### Testing Strategy
> Defines what to test and how – gives the testing agent concrete direction during exec-spec.
> Only include scenarios and coverage goals here; actual test code is written during execution.

#### Test Scope
- **Unit tests**: {{Key modules/functions requiring unit tests, with expected behaviors}}
- **Integration tests**: {{API endpoints, service interactions, data flows to verify}} _(if applicable)_
- **E2E tests**: {{Critical user journeys to validate end-to-end}} _(if applicable)_

#### Key Test Scenarios
{{Derive from success criteria – each criterion should map to at least one test scenario}}
- {{Scenario 1: description + expected outcome}}
- {{Scenario 2: description + expected outcome}}

#### Edge Cases & Error Scenarios
- {{Edge case 1: boundary condition or unusual input}}
- {{Error scenario 1: expected failure mode and how it should be handled}}

#### Test Patterns & References
```
# Reference format: type | path | what to follow
test   | tests/unit/users.test.ts:15-40      | Test structure and assertion style
test   | tests/e2e/auth.spec.ts:8-25         | E2E test setup pattern
config | playwright.config.ts                | E2E configuration
```

#### Test-Implementation Pairing
> Map test scenarios to execution groups to create a natural red-green rhythm.
> Tests paired with a group should be written (and failing) before the group executes.

| Execution Group | Test Scenarios | Expected Behavior |
|----------------|----------------|--------------------|
| G1 | {{Scenario 1, Scenario 2}} | {{Tests fail before G1, pass after}} |
| G2 | {{Scenario 3}} | {{Tests fail before G2, pass after}} |

_Skip for purely structural tasks (scaffolding, config, migrations) where tests-first adds no value._

### Validation Tasks
> Validation methodology details defined in exec-spec.

- [ ] **TV01** [P] Level 1: Code review and analysis
- [ ] **TV02** [P] Level 2: Unit, integration, E2E testing
- [ ] **TV03** [P] Level 3: Visual validation _(if UI applicable)_
- [ ] **TV04** Address validation issues, verify *Final Validation Checklist*

### Feature-Specific Validation (if any)
{{Only add requirements not covered by standard validation levels}}


## Final Validation Checklist

### Feature Validation
- [ ] **All success criteria** from the top-level "Success Criteria" section met
- [ ] **All tasks** in the implementation plan are _fully completed_ (not partially) and the completion is _reviewed, verified checkboxes checked_
- [ ] **No regressions** or breaking changes introduced
- [ ] **UI verified** to match requirements (if applicable)

### Technical Validation
- [ ] **All validation levels** completed successfully
- [ ] Code **builds / compiles** and **all** tests pass without errors
- [ ] **No** analysis, linting/type errors or critical code style issues
- [ ] Code follows existing codebase patterns, naming conventions and structures
- [ ] **All** temporary, refactored, migrated or obsolete code/files removed and cleaned up
- [ ] No commented-out code left behind
