# Feature Implementation Specification Template

> Both provenance lines, always – a standalone feature has a one-story plan of its own. A partial pair is malformed.

**Plan**: <repo-root-relative-posix-path-to-plan.json>
**Story-ID**: <S##>

## Feature Overview and Goal

**Intent**: {{1 sentence – why this feature exists, the problem it solves or the user/business value it unlocks}}

**Expected Outcomes** (2-4, each `[OC<NN>]`-tagged, one sentence each; the mechanics are the scenarios'):

- [OC01] {{user- or business-observable success condition}}
- [OC02] {{user- or business-observable success condition}}


## Required Context

> **Omit this section** when empty.

- `{{repo/root/relative/path.md}}#{{heading-slug-or-id}}` – {{why it binds this FIS, one clause}}


## Acceptance Scenarios

- **S01 [OC01] {{Happy path – short outcome description}}**
  - **Given** {{precondition / system state}}
  - **When** {{triggering action or event}}
  - **Then** {{observable outcome}}

- **S02 [OC01,OC02] [runtime] {{Edge case or error scenario}}**
  - **Proof**: `tests/auth/test_login.py#test_rejects_expired_token` – red at spec time


## Structural Criteria

- **SC01** {{Non-behavioral invariant this story's own diff could break, proved by a task Verify line}}


## Scope & Boundaries

### Work Areas
- {{Component or file surface being changed}}

### What We're NOT Doing
- {{Exclusion an executor could plausibly build}} – {{reason}}


## Architecture Decision

**Approach**: {{one-line approach + rationale}} {{(optional: `See ADR: <path>/NNN-<slug>.md`)}}
**Why this over the floor**: {{the floor option – do nothing, or extend what exists – and the requirement clause that rules it out; required whenever the approach is not that floor}}
**Flow**: {{Omit unless the feature is multi-component and the seams are not self-evident from Approach + tasks. Order and seams, each once}}


## Constraints & Gotchas

> **Omit this section** when empty.

- **Constraint**: {{Known limitation}} – Workaround: {{specific solution}}


## Implementation Plan

### Implementation Tasks

- **TI01** {{The state that is TRUE when done, in one clause}}
  - {{Only what no section above carries: a pattern to follow (`file#symbol`), a dependency on an earlier task, a local decision}}
  - **Verify**: `{{path/to/test_file#test_name}}` – {{how the SATISFIES targets are observed, plus any assertion they do not state}}
  - **SATISFIES**: {{S<NN> and/or SC<NN> this task advances}}

- **TI02** {{Outcome}}
  - **Verify**: `cmd: {{command}}` – {{assertion}}   _(or `inspect: {{path:LINE}}` where nothing executable can observe it)_
  - **SATISFIES**: {{S<NN> and/or SC<NN>}}


## Final Validation Checklist
> **Omit this entire section** unless the feature needs a check no task Verify, test tier, review, or visual validation makes – a run against the real service, a gate over the whole diff ("no new writes to `~/.claude/`").

- {{Feature-specific final check}}
