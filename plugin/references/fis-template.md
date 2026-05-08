# Feature Implementation Specification Template

**Plan**: <relative-posix-path-to-plan.json>
**Story-ID**: <S##>

## Feature Overview and Goal
{{1-2 sentences: what needs to be built and why}}


## Required Context

> Cross-doc reference rules: see [`fis-authoring-guidelines.md`](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md#cross-document-references) (inline budget, source-pin format).

{{Repeat blocks as needed. Keep each block focused: one decision, constraint, or contract per block.}}

### From `{{path/to/source.md}}` — "{{Section or Anchor Name}}"
<!-- source: {{path/to/source.md}}#{{heading-slug-or-id}} -->
<!-- extracted: {{commit-sha when source is in this repo; YYYY-MM-DD otherwise}} -->
> {{Inlined verbatim span. Follow the inline budget in the Cross-Document References guideline.}}


## Deeper Context

> Anchored pointers for supplementary context; read on demand. Omit when none exist.

- `{{path/to/source.md}}#{{heading-slug-or-id}}` — {{one-line description of what's there and when to read it}}
- `{{path/to/source.md}}#{{heading-slug-or-id}}` — {{description}}


## Success Criteria (Must Be TRUE)
> Each criterion must have a proof path: a Scenario (behavioral) or task Verify line (structural).
- [ ] {{Observable truth from user's perspective}}
- [ ] {{Verifiable system behavior}}
- [ ] {{Measurable technical requirement}}

### Health Metrics (Must NOT Regress)
- [ ] {{Existing tests continue to pass}}
- [ ] {{Performance baseline not degraded}}
- [ ] {{Existing API contracts / interfaces unchanged (unless explicitly scoped)}}


## Scenarios

> Scenarios as Proof-of-Work: see [`fis-authoring-guidelines.md`](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md#scenarios-and-proof-of-work) (authoring principles, negative-path checklist).

### {{Scenario Name}}
- **Given** {{precondition / system state}}
- **When** {{triggering action or event}}
- **Then** {{observable outcome}}

### {{Edge Case / Error Scenario Name}}
- **Given** {{precondition or boundary state}}
- **When** {{boundary condition or error trigger}}
- **Then** {{expected handling behavior}}


## Scope & Boundaries

### In Scope
_Every scope item must be covered by at least one scenario (behavioral items) or task with a Verify line (structural items)._
- {{Core functionality to be built}}
- {{Integration points to be created}}

### What We're NOT Doing
_Keep this to 3-5 explicit non-goals or deferrals with reasons._
- {{Out of scope item - be specific}} -- {{reason it is deferred or excluded}}
- {{Existing functionality not to be modified}} -- {{reason}}

### Agent Decision Authority (optional -- include when scope boundaries are ambiguous)
- **Autonomous**: {{Decisions the agent can make}}
- **Escalate**: {{Decisions requiring human input}}


## Architecture Decision

> Default: one line. If a genuine trade-off needs analysis, that is an upstream `andthen:architecture --mode trade-off` task — reference the resulting ADR here rather than performing the analysis inline.

**Approach**: {{one-line approach + rationale}} {{(optional: `See ADR: <path>/NNN-<slug>.md`)}}

{{Rare — only when an inline trade-off was actually performed and no ADR exists, expand to:}}

**Rationale**: {{why this approach, given constraints}}
**Alternatives considered**:
1. **{{Alt 1}}** -- rejected: {{reason}}
2. **{{Alt 2}}** -- rejected: {{reason}}


## Technical Overview

> Anything load-bearing belongs in `Required Context` (verbatim upstream spans). Use this section only for spec-time elaborations that have no upstream source — drop it entirely if Required Context already covers the surface.

### UI/UX Design (if applicable)
{{Describe UI changes, screens, interactions, user flows}}

### UI Mockups/Wireframes (if applicable)
{{Links to wireframes or simple ASCII mockups}}

### Data Models (if applicable)
{{Describe models, fields, types, and relationships in natural language. No pseudocode.}}

### Integration Points (if applicable)
{{How this integrates with existing systems or APIs}}


## Code Patterns & External References

> Code-pattern pointers (`file#symbol` — see [Cross-Document References rule #1](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md#cross-document-references) for the symbol-anchor ladder), external URLs, and wireframes. `doc` rows (PRD/plan/research/ADR) belong in `Required Context` or `Deeper Context`. The "why needed" column states *intent* — what the executor should learn — not just a label.

```
# type | path#anchor or url               | why needed (intent)
file   | src/components/Modal.tsx#Modal   | Dialog pattern — copy focus-trap + escape-key handling
file   | src/api/users.ts#getUser         | API shape — match request/response envelope and error mapping
url    | https://docs.example.com/auth    | OAuth flow reference
wire   | docs/specs/wireframes/login.html | UI layout for login screen
```


## Constraints & Gotchas
- **Constraint**: {{Known limitation}} -- Workaround: {{specific solution}}
- **Avoid**: {{Common mistake or anti-pattern}} -- Instead: {{correct approach}}
- **Critical**: {{Framework/library limitation}} -- Must handle by: {{approach}}


## Implementation Plan

> **Vertical slice ordering**: First tasks should produce a thin but working end-to-end path. Later tasks widen the slice.

### Implementation Tasks

_Example — replace with your actual tasks. Format: outcome + context line (constraints, `file#symbol` pattern reference) + behavioral Verify._

- [ ] **TI00 (example — delete this block)** Event ingestion endpoint accepts and validates incoming payloads
  - Follow `src/api/users.ts#getUser` for request/response envelope shape and field-level error mapping; reuse existing validation middleware
  - **Verify**: `Test: POST /events with valid payload returns 201; invalid payload returns 422 with field-level errors`

- [ ] **TI01** {{Outcome that must be TRUE when done}}
  - {{1-2 lines of context: constraints, pattern reference (`file#symbol`), key decisions}}
  - **Verify**: {{Behavioral assertion that fails if outcome not achieved}}

- [ ] **TI02** {{Outcome}}
  - {{Context — if this task depends on TI01 or another earlier task, state it explicitly here}}
  - **Verify**: {{Assertion}}

### Testing Strategy
> Derive test cases from the **Scenarios** section. Tag with task ID(s) the test proves.
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


## Implementation Observations

> _Managed by exec-spec post-implementation — append-only. Tag semantics: see [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md) (FIS Mutability Contract, tag definitions). AUTO_MODE assumption-recording: see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). Spec authors: leave this section empty._

Discovered Requirements entries use this shape:

- **Title**: short imperative phrase
- **Description**: 1-2 sentences on the discovered requirement
- **Rationale**: why it was missed in original spec
- **Interpretation** (AUTO_MODE only): the conservative interpretation chosen and why
- **Traced from**: task ID where the discovery occurred
- **Date**: YYYY-MM-DD

_No observations recorded yet._
