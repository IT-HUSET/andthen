# Feature Implementation Specification Template

> **Purpose:**
> Executable specification optimized for AI agents – concise, actionable, reference-heavy.
>
> **Core Principles:**
> 1. **References over Content**: Link to docs, code (file:line), and research – don't inline them
> 2. **Decisions, not Explanations**: State what to do, not lengthy rationale
> 3. **Patterns by Reference**: Point to existing code patterns (file:line) rather than reproducing them
> 4. **Validation at Execution**: Code is written during exec-spec, not spec
> 5. **Information Dense**: Keywords and patterns from the codebase, minimal prose
>
> **Size Constraint:**
> - Target: **300-500 lines** max for most features
> - If exceeding 500 lines, split into multiple specs or extract shared content to referenced files
>
> **DON'Ts**
> - ❌ Code snippets longer than 5-10 lines – reference existing patterns instead
> - ❌ Inline documentation excerpts – link to the source
> - ❌ Verbose prose or explanations – be terse and actionable
> - ❌ Repeating information available elsewhere – reference it
> - ❌ Over-engineering or out-of-scope functionality


## Feature Overview and Goal
{{Clear description of what needs to be built and why}}


## Success Criteria (Must Be TRUE)
State what must be observably TRUE when this feature is complete:
- [ ] {{Observable truth from user's perspective}}
- [ ] {{Verifiable system behavior}}
- [ ] {{Measurable technical requirement}}
- [ ] {{Performance/scaling requirement}}


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

_Examples:_

#### G1: Project Foundation ← [depends: none]
- [ ] **TI01** Initialize Fresh project structure in repository root
  - Create deno.json with Fresh dependencies and tasks
  - Set up basic routes/, islands/, components/, lib/ directories
  - Configure import maps and TypeScript settings
  - **Verify**: [Exists] `routes/`, `islands/`, `components/`, `lib/` dirs present; [Substantive] deno.json contains `fresh` dependency and `start`/`build` tasks; [Wired] import map resolves; [Functional] `deno task check` passes

- [ ] **TI02** Configure Supabase integration and environment
  - Create .env.example and .env files with Supabase credentials
  - Set up lib/supabase/client.ts and lib/supabase/server.ts
  - Configure database connection and authentication helpers
  - **Verify**: [Exists] `lib/supabase/client.ts` and `lib/supabase/server.ts` present; [Substantive] `createClient()` and `createServerClient()` have real implementations (not stubs); [Wired] `.env.example` lists `SUPABASE_URL` and `SUPABASE_ANON_KEY`; [Functional] type-check passes

#### G2: Development Tooling [P] ← [depends: G1]
- [ ] **TI03** Set up development tooling and scripts
  - Configure deno fmt, deno lint, and deno check tasks
  - Set up Playwright for E2E testing in tests/e2e/
  - Create development and deployment scripts
  - **Verify**: [Exists] deno.json contains `fmt`, `lint`, `check` tasks; [Substantive] `tests/e2e/playwright.config.ts` has base URL configured; [Wired] tasks are runnable from deno.json; [Functional] `deno task lint` executes without config errors

#### G3: Design System [P] ← [depends: G1]
- [ ] **TI04** Integrate design system foundation
  - Add Pico CSS CDN link and Google Fonts (Nunito Sans, Outfit)
  - Create static/styles/architecture-theme.css with custom variables
  - Set up responsive design system per ADR-002
  - Update barrel exports
  - **Verify**: [Exists] `architecture-theme.css` present; [Substantive] defines color, spacing, and typography custom properties per ADR-002; [Wired] root layout includes Pico CSS and Google Fonts links; [Functional] styles render correctly in browser

#### Grouping Constraints
- **Max 4 implementation tasks per group** (test groups can have up to 6)
- **Never group across independent concerns** – if tasks touch unrelated subsystems, keep them in separate groups
- **Absorb trivial tasks** – barrel exports, verification steps, cleanup tasks go into the nearest related group rather than standing alone
- **Tests group together** – all test tasks for a feature form one group (split if >6 tasks)

#### Implementation Notes (per task, only when needed)
- Reference existing patterns: `see src/components/Modal.tsx:45-78 for similar pattern`
- Only include pseudocode (max 5-10 lines) when no existing pattern exists in codebase
- Configuration/data models: describe structure briefly, don't write full schemas

#### Verification Criteria (per task, required)
Each task's **`Verify:`** line must check all 4 dimensions:
- **Exists**: file/path/route is present
- **Substantive**: contains real implementation (not stubs, TODOs, or placeholders)
- **Wired**: integrated into the system (imported, routed, called)
- **Functional**: works when invoked (build passes, test passes, or observable behavior)

Where applicable, verification should trace back to the feature's must-be-TRUE success criteria.

Reference: `${CLAUDE_PLUGIN_ROOT}/references/verification-patterns.md` for stub-detection
and wiring-check patterns.

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
