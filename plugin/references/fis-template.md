# Feature Implementation Specification Template

**Plan**: <relative-posix-path-to-plan.json>
**Story-ID**: <S##>

## Feature Overview and Goal

**Intent**: {{1 sentence – why this feature exists, the problem it solves or the user/business value it unlocks}}

**Expected Outcomes** (2-4 user- or business-observable success conditions, each `[OC<NN>]`-tagged; scenarios anchor to these via `[OC<NN>]`):

- [OC01] {{observable success condition}}
- [OC02] {{observable success condition}}


## Required Context

> Load-bearing upstream spans inlined verbatim from PRD, plan, ADRs, or guidelines. **Omit this entire section** when there are no upstream sources to inline.

### From `{{path/to/source.md}}` – "{{Section or Anchor Name}}"
<!-- source: {{path/to/source.md}}#{{heading-slug-or-id}} -->
<!-- extracted: {{commit-sha when source is in this repo; YYYY-MM-DD otherwise}} -->
> {{Inlined verbatim span. Follow the inline budget in the Cross-Document References guideline.}}


## Deeper Context

> Anchored pointers for supplementary context; read on demand. **Omit this entire section** when no supplementary pointers exist.

- `{{path/to/source.md}}#{{heading-slug-or-id}}` – {{one-line description of what's there and when to read it}}


## Acceptance Scenarios

- [ ] **S01 [OC01] [TI01] {{Happy path – short outcome description}}**
  - **Given** {{precondition / system state}}
  - **When** {{triggering action or event}}
  - **Then** {{observable outcome}}

- [ ] **S02 [OC01,OC02] [TI01,TI02] {{Edge case or error scenario}}**
  - **Given** {{precondition or boundary state}}
  - **When** {{boundary condition or error trigger}}
  - **Then** {{expected handling behavior}}


## Structural Criteria

> Non-behavioral proof requirements: invariants, regression guards, and structural checks that hold true when done. Each criterion is proved by a task Verify line, not a scenario.

- [ ] {{Existing tests continue to pass}}
- [ ] {{Performance baseline not degraded}}
- [ ] {{Existing API contracts / interfaces unchanged (unless explicitly scoped)}}


## Scope & Boundaries

### Work Areas
_Inventory of components, files, or surfaces being changed (3-7 bullets). Each Work Area must map to at least one task or scenario – a Work Area with no implementing task is a forward-coverage gap._
- {{Component or file surface being changed}}
- {{Integration point being created or modified}}

### What We're NOT Doing
_Keep this to 3-5 explicit non-goals or deferrals with reasons._
- {{Out of scope item - be specific}} -- {{reason it is deferred or excluded}}
- {{Existing functionality not to be modified}} -- {{reason}}


## Architecture Decision

**Approach**: {{one-line approach + rationale}} {{(optional: `See ADR: <path>/NNN-<slug>.md`)}}
**Why this over alternatives**: {{one-line causal narrative – optional}}


## Technical Overview

> Synthesis: how components, integration seams, data flow, or tier rationale weave together. **Leave empty** when this is self-evident from Architecture Decision + Code Patterns + per-task descriptions; fill only for multi-component features where the picture isn't obvious from those. Cap at ~10 lines when filled.

{{Synthesis prose, if non-obvious}}


## Code Patterns & External References

```
# type | path#anchor or url               | why needed (intent)
file   | src/components/Modal.tsx#Modal   | Dialog pattern – copy focus-trap + escape-key handling
file   | src/api/users.ts#getUser         | API shape – match request/response envelope and error mapping
url    | https://docs.example.com/auth    | OAuth flow reference
wire   | docs/specs/wireframes/login.html | UI layout for login screen
```


## Constraints & Gotchas

_A bullet belongs here only if it is cross-cutting (applies to ≥2 tasks) or names a non-obvious framework-level trap. Task-local concerns live in task descriptions._

- **Constraint**: {{Known limitation}} -- Workaround: {{specific solution}}
- **Avoid**: {{Common mistake or anti-pattern}} -- Instead: {{correct approach}}
- **Critical**: {{Framework/library limitation}} -- Must handle by: {{approach}}


## Implementation Plan

### Implementation Tasks

_Format: outcome + context line (constraints, `file#symbol` pattern reference) + behavioral Verify. Task titles describe state-of-the-world outcomes – avoid implementation verbs like `Replace`, `Refactor`, `Update`, `Modify`, `Add to`._

- [ ] **TI00 (example – delete this block)** Event ingestion endpoint accepts and validates incoming payloads
  - Follow `src/api/users.ts#getUser` for request/response envelope shape and field-level error mapping; reuse existing validation middleware
  - **Verify**: `Test: POST /events with valid payload returns 201; invalid payload returns 422 with field-level errors`

- [ ] **TI01** {{Outcome that must be TRUE when done}}
  - {{1-2 lines of context: constraints, pattern reference (`file#symbol`), key decisions}}
  - **Verify**: {{Behavioral assertion that fails if outcome not achieved}}

- [ ] **TI02** {{Outcome}}
  - {{Context – if this task depends on TI01 or another earlier task, state it explicitly here}}
  - **Verify**: {{Assertion}}

### Testing Strategy
> Default test approach: per-task Verify lines + scenario tests scaffolded from Acceptance Scenarios. **Leave empty** when this is sufficient; fill only when the test approach is non-obvious – level allocation (unit/integration/e2e), fixture or harness decisions, or mocking philosophy that scenario tags + Verify lines don't already encode. Use `[TI<NN>]` task tags to map test concerns to producing tasks.

- {{Test-approach note, if non-obvious}}

### Validation
> Standard validation (build/test checks, code review, visual validation, and 1-pass remediation) is handled by exec-spec. **Leave empty** when this is sufficient; only add feature-specific validation requirements if the standard levels are insufficient.

- {{Feature-specific validation requirement, if any}}

### Execution Contract
> Generic exec-spec discipline – task ordering, Verify gating, sub-agent usage, project validation gates, checkbox immediacy – is enforced by exec-spec. **Leave empty** when this is sufficient; fill only for feature-specific execution constraints (cross-task dependencies like "TI03 must complete before TI04", parallelism rules, or special invocation commands).

- {{Feature-specific execution constraint, if any}}


## Final Validation Checklist
> Acceptance Scenarios, Structural Criteria, and task Verify lines are the standard completion gates. **Leave empty** when these are sufficient; fill only for feature-specific final gates not already covered (e.g. "no new writes to `~/.claude/`", "no orphan migration files in `db/migrate/`").

- [ ] {{Feature-specific final gate, if any}}


## Implementation Observations

> _Managed by exec-spec post-implementation – append-only. Tag semantics: see [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md) (FIS Mutability Contract, tag definitions). AUTO_MODE assumption-recording: see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). Spec authors: leave this section empty._

Discovered Requirements entries use this shape:

- **Title**: short imperative phrase
- **Description**: 1-2 sentences on the discovered requirement
- **Rationale**: why it was missed in original spec
- **Interpretation** (AUTO_MODE only): the conservative interpretation chosen and why
- **Traced from**: task ID where the discovery occurred
- **Date**: YYYY-MM-DD

_No observations recorded yet._
