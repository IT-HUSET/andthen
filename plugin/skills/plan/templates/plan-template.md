# Implementation Plan Template

> Use this template as the baseline shape for `plan.md`.
> This document is an operational contract, not just a narrative artifact. Keep the heading names, Story Catalog columns, and standard story brief labels stable because downstream skills read them.


# Implementation Plan: [Project Name]

> **PRD**: [`prd.md`](./prd.md)

> **References**: any upstream artifacts the plan depends on — ADRs, design system, wireframes, glossary, ad-hoc research, etc. One bullet per reference. Omit the section entirely when none exist.
> - [Label](relative-path) — one-line purpose
> - [Label](relative-path) — one-line purpose


## Overview
- **Total stories**: [N]
- **Phases**: [N]
- **Approach**: [1-2 sentence summary of the sequencing strategy]


## Story Catalog

| ID | Name | Phase | Wave | Dependencies | Parallel | Risk | Status | FIS |
|----|------|-------|------|--------------|----------|------|--------|-----|
| S01 | [Name] | Foundation | W1 | - | No | Low | Pending | – |
| S02 | [Name] | Core | W2 | S01 | [P] | Medium | Pending | `docs/specs/my-feature/s02-feature.md` |
| S03 | [Name] | Core | W2 | S01 | [P] | Medium | Pending | `docs/specs/my-feature/s03-other-feature.md` |

> **Invariant**: each row's `FIS` path is unique — one story maps to exactly one FIS. Stories that would share a spec should have been merged in Step 3's Consolidation Pass.
>
> **Dependency cell contract**: `Dependencies` is scheduler input. Use `-` or comma-separated story IDs from this table only, e.g. `S01, S04`. Do not put prose here (`Blocks A-G complete`, `all previous phases`, etc.); put broad sequencing notes in `## Dependency Graph`, phase notes, or the execution guide.


## Shared Decisions

> _Optional — include only when stories have inter-dependencies that imply a shared interface, naming convention, or abstraction. Omit the section when none apply._
>
> 3-6 bullets naming inter-story interface contracts, naming conventions, or shared abstractions multiple stories will create or consume. FIS sub-agents inherit these as-is so independently-generated specs don't drift on shared concerns.

- **[Decision name]**: [one-line description; name the producing and consuming stories]
- **[Decision name]**: [description]


## Binding Constraints

> _Optional — include only when the PRD contains "must support X"-style language at risk of being silently dropped during plan decomposition. Omit when none apply._
>
> Each entry: verbatim PRD span + heading anchor + source feature ID. These flow unchanged into FIS Required Context blocks — they are not subject to architectural trade-offs or scope narrowing by individual stories.

- **[FR-N — short label]**: "[verbatim PRD text span]" — source: [`prd.md#<heading-slug>`](./prd.md#heading-slug)
- **[FR-N — short label]**: "[verbatim text]" — source: [`prd.md#<heading-slug>`](./prd.md#heading-slug)


## Phase Breakdown

### Phase 1: [Phase Name]
_[Sequential execution or short rationale for this phase]_

#### S01: [Story Name]
**Scope**: [1-2 sentences covering the intended outcome, what is included, and what is excluded. Detailed success criteria and scenarios belong in the story FIS.]
**Source refs**: [PRD feature IDs and anchors, e.g. FR-2, FR-5 — `prd.md#export-rules`]
**Asset refs**: [Wireframe refs, ADR refs, design-system refs if any]

#### [P] S02: [Parallel Story Name]
**Scope**: [1-2 sentence story brief]
**Source refs**: [PRD feature IDs and anchors]
**Asset refs**: [Relevant asset refs]

#### S03: [Carried-Forward Story Example]
**Provenance**: Carried from previous plan: S13
**Scope**: [Describe the carried-forward scope clearly; only include `**Provenance**` when no PRD feature directly covers this story]
**Asset refs**: [Relevant asset refs]


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

Use this section for human-readable sequencing notes. If a note represents a hard execution gate, encode it in the Story Catalog as concrete story IDs rather than prose.


## Risk Summary

| Story | Risk | Concern | Mitigation |
|-------|------|---------|------------|
| S02 | Medium | [Concern] | [Approach] |


## Execution Guide

This plan ships fully specced — every story already has a FIS (see the `FIS` column).

1. **Execute the whole bundle**: invoke the `andthen:exec-plan` skill on this directory. It runs the per-story `exec-spec → quick-review` pipeline by phase and wave, then a final gap review.
2. **Or execute one story at a time**: invoke the `andthen:exec-spec` skill on a single story's FIS for finer control.
3. Phase ordering and `[P]` parallel markers are honored by `exec-plan`; dependencies block waves automatically.
4. After execution, the `andthen:exec-plan` skill runs `andthen:review --mode gap` on `plan.md` for cross-story coverage validation.

> **Status tracking**: The Story Catalog is authoritative for `Status` and `FIS`. Phase Breakdown story briefs intentionally do not repeat those fields.
