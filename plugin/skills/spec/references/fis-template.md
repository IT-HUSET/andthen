# Feature Implementation Specification Template

> Both provenance lines, always – a standalone feature has a one-story plan of its own. A partial pair is malformed.

**Plan**: <repo-root-relative-posix-path-to-plan.json>
**Story-ID**: <S##>

## Feature Overview and Goal

**Intent**: {{1 sentence – why this feature exists, the problem it solves or the user/business value it unlocks}}

**Expected Outcomes** (2-4, each `[OC<NN>]`-tagged):

- [OC01] {{observable success condition}}
- [OC02] {{observable success condition}}


## Required Context

> **Omit this section** when empty.

- `{{repo/root/relative/path.md}}#{{heading-slug-or-id}}` – {{what to learn and why it constrains this FIS}}


## Deeper Context

> **Omit this section** when empty.

- `{{path/to/source.md}}#{{heading-slug-or-id}}` – {{what's there and when to read it}}


## Acceptance Scenarios

- **S01 [OC01] {{Happy path – short outcome description}}**
  - **Given** {{precondition / system state}}
  - **When** {{triggering action or event}}
  - **Then** {{observable outcome}}

- **S02 [OC01,OC02] [runtime] {{Edge case or error scenario}}**
  - **Proof**: `tests/auth/test_login.py#test_rejects_expired_token` – red at spec time


## Structural Criteria

- **SC01** {{Non-behavioral invariant this story's own diff could break, proved by a task Verify line}}
- **SC02** {{Another such invariant – wiring, naming, config shape, migration reversibility}}


## Scope & Boundaries

### Work Areas
- {{Component or file surface being changed}}
- {{Integration point being created or modified}}

### What We're NOT Doing
- {{Out of scope item – be specific}} – {{reason it is deferred or excluded}}
- {{Existing functionality not to be modified}} – {{reason}}


## Architecture Decision

**Approach**: {{one-line approach + rationale}} {{(optional: `See ADR: <path>/NNN-<slug>.md`)}}
**Why this over the floor**: {{the floor option – do nothing, or extend what exists – and the requirement clause that rules it out; required whenever the approach is not that floor}}


## Technical Overview

> **Omit this entire section** unless the feature is multi-component and the seams are not self-evident from Architecture Decision + Code Patterns + tasks. Cap ~10 lines.

{{Synthesis prose, if non-obvious}}


## Code Patterns & External References

```
# type | path#anchor or url               | why needed (intent)
file   | src/components/Modal.tsx#Modal   | Dialog pattern – copy focus-trap + escape-key handling
file   | src/api/users.ts#getUser         | API shape – match request/response envelope and error mapping
wire   | docs/specs/wireframes/login.html | UI layout for login screen
```


## Constraints & Gotchas

- **Constraint**: {{Known limitation}} – Workaround: {{specific solution}}


## Implementation Plan

### Implementation Tasks

- **TI01** {{The state that is TRUE when done, in one clause}}
  - {{1-2 lines of context: constraints, pattern reference (`file#symbol`), key decisions}}
  - **Verify**: `{{path/to/test_file#test_name}}` – {{assertion that fails if the outcome is not achieved}}
  - **SATISFIES**: {{S<NN> and/or SC<NN> this task advances}}

- **TI02** {{Outcome}}
  - {{Context – if this task depends on TI01 or another earlier task, state it explicitly here}}
  - **Verify**: `cmd: {{command}}` – {{assertion}}   _(or `inspect: {{path:LINE}}` where nothing executable can observe it)_
  - **SATISFIES**: {{S<NN> and/or SC<NN>}}

### Testing Strategy
> **Omit this entire section** unless test level, fixture/harness, or mocking decisions are non-obvious. Name the exceptions by task ID.

- {{Test-approach note, if non-obvious}}

### Validation
> **Omit this entire section** unless this feature needs validation the test tier, a code review, and visual validation miss.

- {{Feature-specific validation requirement, if any}}

### Execution Contract
> **Omit this entire section** unless the feature has execution constraints beyond list order and per-task Verify gating – parallelism rules, special invocation commands.

- {{Feature-specific execution constraint, if any}}


## Final Validation Checklist
> **Omit this entire section** unless the feature has a final gate the scenarios, criteria, and task Verify lines miss ("no new writes to `~/.claude/`").

- {{Feature-specific final gate, if any}}


## Discovered Requirements

> _Managed by exec-spec during implementation – append-only, one bullet per requirement in the shape fis-mutability.md states. Spec authors: leave this section empty._

_No requirements discovered yet._


## Implementation Observations

> _Append-only: Preflight records a deferred decision here while authoring, exec-spec its observations post-implementation. Nothing else is written here._

_No observations recorded yet._
