# Implementation Plan Template

> Use this template as the baseline shape for `plan.md`.
> This document is an operational contract, not just a narrative artifact. Keep the heading names, Story Catalog columns, and standard story metadata labels stable because downstream skills read them.


# Implementation Plan: [Project Name]

> **PRD**: [`prd.md`](./prd.md)
> **ADRs**: [link any ADR files if present]
> **Design System**: [link if present]
> **Wireframes**: [link if present]
> **Technical Research**: [link if present]


## Overview
- **Total stories**: [N]
- **Phases**: [N]
- **Approach**: [1-2 sentence summary of the sequencing strategy]


## Story Catalog

| ID | Name | Phase | Wave | Dependencies | Parallel | Risk | Status | FIS |
|----|------|-------|------|--------------|----------|------|--------|-----|
| S01 | [Name] | Foundation | W1 | - | No | Low | Pending | – |
| S02 | [Name] | Core | W2 | S01 | [P] | Medium | Pending | `docs/specs/my-feature/s02-feature.md` |
| S03 | [Name] | Core | W2 | S01 | [P] | Medium | Pending | `docs/specs/my-feature/s02-s03-shared-capability.md` |


## Phase Breakdown

### Phase 1: [Phase Name]
_[Sequential execution or short rationale for this phase]_

#### S01: [Story Name]
**Status**: Pending
**FIS**: –
**Phase**: Phase 1: [Phase Name]
**Wave**: W1
**Dependencies**: -
**Parallel**: No
**Risk**: Low
**Scope**: [2-4 sentences covering what is built and what is excluded]
**Acceptance Criteria**:
- [ ] [Must-be-TRUE observable truth]
- [ ] [Must-be-TRUE observable truth]
- [ ] [Supplementary verification point]
**Key Scenarios**: _(optional; seeds elaborated into full Given/When/Then scenarios in the FIS)_
- Happy: [primary success path]
- Edge: [boundary or alternate condition]
- Error: [failure or rejection path]
**Asset refs**: [Wireframe refs, ADR refs, design-system refs if any]

#### [P] S02: [Parallel Story Name]
**Status**: Pending
**FIS**: `docs/specs/my-feature/s02-s03-shared-capability.md`
**Phase**: Phase 1: [Phase Name]
**Wave**: W2
**Dependencies**: S01
**Parallel**: [P]
**Risk**: Medium - [brief concern]
**Scope**: [2-4 sentences]
**Acceptance Criteria**:
- [ ] [Observable outcome]
- [ ] [Observable outcome]
**Asset refs**: [Relevant asset refs]

#### S03: [Carried-Forward Story Example]
**Status**: Pending
**FIS**: `docs/specs/my-feature/s02-s03-shared-capability.md`
**Phase**: Phase 1: [Phase Name]
**Wave**: W2
**Dependencies**: S01
**Parallel**: [P]
**Risk**: Medium - [brief concern]
**Provenance**: Carried from 0.16.3: S13
**Scope**: [Describe the carried-forward scope clearly; only include `**Provenance**` when no PRD feature directly covers this story]
**Acceptance Criteria**:
- [ ] [Observable outcome]
**Asset refs**: [Relevant asset refs]

> **Composite FIS note**: When multiple tightly coupled stories share one FIS, point each story's `**FIS**` field to the same spec path. Composite FIS filenames must use the lowest story ID as prefix and include all constituent IDs (for example `s01-s02-s03-feature-name.md`).


## Dependency Graph

```text
Dependency arrows:
S01 ──→ S02 ──→ S05
  │
  └──→ S03

Wave assignments:
W1: S01
W2: S02, S03
W3: S05
```


## Risk Summary

| Story | Risk | Concern | Mitigation |
|-------|------|---------|------------|
| S02 | Medium | [Concern] | [Approach] |


## Execution Guide

1. Execute Phase 1 stories sequentially, then move wave by wave.
2. For each story ready to implement:
   - Run the `andthen:spec` skill using the story scope from this plan.
   - Update the story `**FIS**` field with the generated spec path and set `**Status**` to `Spec Ready`.
   - Run `andthen:exec-spec` on the generated FIS.
   - When implementation starts, set `**Status**` to `In Progress`.
   - After implementation and review, check off completed acceptance criteria and set `**Status**` to `Done`.
3. Stories marked `[P]` may run in parallel after dependencies are satisfied.
4. After the plan is complete, run `andthen:review --gap-only` against `plan.md`.

> **Status tracking**: Keep the Story Catalog table and the Phase Breakdown story sections in sync. `andthen:exec-plan` and `andthen:ops` rely on these fields for progress tracking.
