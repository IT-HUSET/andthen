---
description: Create PRD and implementation plan with story breakdown. Discover requirements interactively when no PRD exists, or build on prior artifacts from `andthen:clarify`. Lightweight planning - detailed specs are created later via `spec` or `spec-plan`.
argument-hint: "[Specs directory or requirements source] | --issue <number> [--to-issue]"
---

# Create PRD & Implementation Plan


Transform requirements into lightweight implementation plan with story breakdown. If a PRD already exists, starts from that. If prior artifacts exist (e.g., `requirements-clarification.md` from `andthen:clarify` or a draft PRD), uses them as the basis for PRD creation without re-doing discovery. If nothing exists, runs full requirements discovery to create a PRD first.

Stories are scoped and sequenced but NOT fully specified - generate detailed specs later via `andthen:spec` (manual per-story flow) or `andthen:spec-plan` (batch generation for `exec-plan`).

**Philosophy**: Detailed specs decay quickly. This command creates just enough structure to sequence work and track progress, while deferring detailed specification to implementation time.


## VARIABLES

_Specs directory (with PRD, requirements-clarification, or draft PRD), or requirements source (**required**):_
INPUT: $ARGUMENTS

_Output directory (defaults to input directory, or `<project_root>/docs/specs/` for new PRDs):_
OUTPUT_DIR: `INPUT` (if directory) or `<project_root>/docs/specs/` _(or as configured in **Project Document Index**)_

### Optional Flags
- `--issue <number>` → Fetch and use a GitHub issue as requirements input
- `--to-issue` → PUBLISH_ISSUE: Publish plan as a GitHub issue after saving locally


## USAGE

```
/plan docs/specs/my-feature/            # From directory with PRD or prior artifacts
/plan @docs/requirements.md             # From requirements file
/plan --issue 42                        # From GitHub issue
/plan "Build a user dashboard"          # From inline description
/plan docs/specs/my-feature/ --to-issue # Create plan and publish to GitHub issue
```


## INSTRUCTIONS

- **Make sure `INPUT` is provided** - otherwise **STOP** immediately and ask user for input
- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails**
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Orchestrate, don't do everything yourself** - Delegate research, analysis, and exploration to sub-agents _(if supported by your coding agent)_ (see Workflow below)
- **Lightweight planning** - Stories define scope, not implementation details
- **No over-engineering** - Minimum stories to cover requirements
- **Progressive implementation** - Organize into logical phases (examples provided are templates, adapt to project)
- **Deferred specification** - Detailed specs come later via `andthen:spec` or `andthen:spec-plan`
- **Interactive when discovering requirements** - Interview user iteratively; don't assume answers. After asking questions, **STOP and WAIT** for user responses before proceeding
- **Focus on "what" not "how"** - Requirements, not implementation details
- **Be specific** - Replace vague terms with measurable criteria
- **Document decisions** - Record rationale, trade-offs, alternatives considered


## GOTCHAS
- Agent creates too many small stories – push for fewer, larger vertical slices
- Skipping requirements discovery when no PRD exists – if no prior artifacts, run discovery first
- Wave assignments get ignored during execution – explicitly mark dependencies between stories
- Not reading STATE.md before planning – misses context about current phase, active blockers, and recent decisions that should inform story priorities


## WORKFLOW

### 1. Input Validation & PRD Detection

1. **Parse INPUT** - Determine type:
   - **`--issue` flag present** (or INPUT refers to a GitHub issue): Extract issue number from INPUT, use `gh issue view <number>` to fetch issue details (title, body, labels, comments). Use issue content as requirements input. Store issue number for reference in generated plan. → proceed to Step 1b
   - **Directory with PRD**: `INPUT` is a directory containing `prd.md` → proceed to Step 2
   - **Directory with prior artifacts**: `INPUT` is a directory containing `requirements-clarification.md` (from `andthen:clarify`) and/or a draft PRD (`prd-draft.md`), but no finalized `prd.md` → proceed to Step 1c
   - **File path**: Read and extract requirements → proceed to Step 1b
   - **URL**: Fetch and extract requirements → proceed to Step 1b
   - **Inline description**: Use directly → proceed to Step 1b

2. **If PRD found** (directory with existing `prd.md`):
   - Document optional assets if present (Architecture/ADRs, Design system, Wireframes)
   - **Gate**: PRD validated → skip to Step 2

3. **If prior artifacts found** (directory with `requirements-clarification.md` and/or `prd-draft.md`, but no finalized `prd.md`):
   - Read all existing artifacts in the directory
   - Document optional assets if present (Architecture/ADRs, Design system, Wireframes)
   - Proceed to Step 1c (PRD from Existing Artifacts)

4. **If no PRD and no prior artifacts** (requirements source provided):
   - Validate prerequisites: requirements should be reasonably refined (not raw ideas)
   - If input is too vague, recommend running the `andthen:clarify` skill first
   - Initial gap analysis – document what's explicitly stated, assumed/implied, and missing/unclear (functional requirements, user flows, edge cases, success criteria, business context, MVP scope)
   - Proceed to Step 1b (Requirements Discovery)

**Gate**: Input validated


### 1b. Requirements Discovery & PRD Creation _(skip if PRD already exists)_

#### Requirements Discovery Interview

Follow the same interview approach as `andthen:clarify` Phase 2 (targeted questions, **STOP and WAIT** for user responses, do not infer answers). Focus on gaps identified in Step 1a — cover areas relevant to planning: users & personas, core workflows, data model, integrations, constraints, NFRs, success metrics. Iterate until no major gaps remain.

> **CRITICAL**: After presenting questions, you must stop your response and wait for user input. Use the `AskUserQuestion` tool if available in your environment. Do not proceed past this section until the user has answered your questions and you've confirmed no major gaps remain.

**Gate**: All critical questions answered, no blocking ambiguities


#### Generate PRD Document

Structure the PRD from interview responses and save as `OUTPUT_DIR/<feature-name>/prd.md`. Apply MoSCoW prioritization (Must/Should/Could/Won't) and P0/P1/P2 levels to features.

Required sections:
- **Executive Summary** – project title, problem with quantified impact, vision, target users, success metrics
- **Problem Definition** – clear problem statement with evidence and context
- **Scope** – In Scope / Out of Scope / MVP Boundary
- **Functional Requirements** – User Stories table (`ID | Story | Acceptance Criteria | Priority`), Feature Specifications (description, acceptance criteria, inputs/outputs, validation, error handling, priority per feature), User Flows, UI Wireframes _(if applicable)_, Data Requirements
- **Non-Functional Requirements** – Performance, Reliability, Security, Usability (thresholds for each)
- **Edge Cases** – `Scenario | Expected Behavior` table
- **Constraints & Assumptions** – technical/resource/regulatory constraints, user/technical/business assumptions, Dependencies table
- **Decisions Log** – `Decision | Rationale | Alternatives Considered` table

#### PRD Validation
- [ ] Problem statement with measurable impact
- [ ] All user stories have testable acceptance criteria
- [ ] Success metrics are specific and measurable
- [ ] Scope explicitly defined (in/out)
- [ ] Every feature has defined error handling
- [ ] Non-functional requirements have clear thresholds
- [ ] No ambiguous terms without definitions
- [ ] All assumptions documented
- [ ] No conflicting requirements

Optional: Invoke the `andthen:review-doc` skill to validate the PRD before finalizing.

**Gate**: PRD created → continue to Step 2


### 1c. PRD Creation from Existing Artifacts _(skip if PRD already exists or no prior artifacts found)_

Use existing artifacts (`requirements-clarification.md` from `andthen:clarify` and/or `prd-draft.md`) as the primary basis for creating the PRD. This path avoids duplicating discovery work already completed.

- Map existing content against the PRD template (see Step 1b)
- If significant gaps remain, conduct a focused interview covering only the missing areas – ask 3-5 questions at a time, **STOP and WAIT for responses**.
  > **CRITICAL**: Do NOT re-ask questions already answered in the existing artifacts. Only ask about genuinely missing information.
- Structure and generate the PRD following the same template as Step 1b. Preserve decisions, rationale, and specific details from existing artifacts – do not paraphrase or generalize away specifics.
- Apply same Prioritization → PRD Validation steps as Step 1b.

**Gate**: PRD created → continue to Step 2


### 2. Requirements Analysis

Delegate codebase exploration to a sub-agent _(if supported)_ to keep context lean. Read `STATE.md` (default: `docs/STATE.md`) if it exists – use current phase, active stories, and blockers to inform story priorities. Reference `UBIQUITOUS_LANGUAGE.md` if present; use canonical terms in story names and acceptance criteria.

Synthesize into a unified understanding of: all PRD requirements and user stories, MVP scope, success criteria, prioritization (P0/P1/P2), natural implementation boundaries, feature dependencies, and complexity/risk areas.

**Technical research**: If codebase exploration surfaces substantial technical findings (architecture patterns, framework constraints, integration details, existing conventions) that would be useful during spec creation or execution, save them to `{OUTPUT_DIR}/technical-research.md`. This keeps the PRD and plan free of implementation details while preserving research for downstream skills (`andthen:spec`, `andthen:spec-plan`). Skip this if findings are minimal — not every plan needs a technical research document.

**Gate**: Feature mapping complete


### 3. Story Breakdown

#### Design Space Analysis _(if applicable)_

For features with multiple design dimensions – whether architectural, UI/UX, or interaction-related – use design space decomposition _(see `plugin/references/design-tree.md`)_ to inform story structure:

1. **Identify design dimensions** from the PRD (e.g., display mode, filtering approach, auth method, data freshness)
2. **Map dimension independence** – dimensions that can be built and tested separately are candidates for separate, parallelizable stories
3. **Identify coupling** – dimensions with cross-consistency constraints (where options in one affect viability of options in another) should be in the same story to avoid rework
4. **Spot foundational dimensions** – choices that other dimensions depend on belong in earlier phases (e.g., data model must precede display mode)
5. **Flag uncertainty** – dimensions with high uncertainty or contested options may warrant a spike/research story before implementation

If a design space decomposition was produced upstream (by `clarify` or `trade-off`), reference and build on it rather than re-creating it.

_Skip for projects with straightforward design decisions._

#### Story Guidelines

**Each story should be:**
- **Vertical** - Cuts through all layers (data → logic → API → UI) to produce a demoable/testable end-to-end slice, even if narrow in scope
- **Bounded** - Clear scope, single responsibility
- **Verifiable** - Has acceptance criteria
- **Independent** - Minimal coupling to other stories (after dependencies met)

**Story set rules:**
- Minimum stories to cover all requirements
- No overlap between stories
- No over-granularity (combine small related items)

#### Implementation Phases

Organize stories into logical phases. The number and nature of phases depends on the project - adapt as needed. Common pattern:

```
Phase 1: Tracer Bullet (Sequential)
├── Thin end-to-end slice of the most critical feature
├── Proves architecture works across all layers
└── Produces a demoable result

Phase 2: Feature Slices (Parallel where possible)
├── [P] Feature A – full vertical slice (data → logic → API → UI)
├── [P] Feature B – full vertical slice
└── Feature C (depends on A) – full vertical slice

Phase 3: Hardening (Parallel)
├── [P] Edge cases and error handling
├── [P] Performance optimization
├── [P] Accessibility and polish
└── [P] Cross-feature integration
```

#### Wave Assignment
Assign stories to execution waves within each phase:
- **W1**: Stories with no dependencies (can start immediately)
- **W2**: Stories dependent only on W1 completions
- **W3+**: Continue cascading

Stories in the same wave with [P] markers run in parallel.
Wave assignments are pre-computed here so exec-plan doesn't need
runtime dependency analysis.

#### Goal-Backward Analysis (per story)
Before defining tasks, work backward from the desired outcome:
1. **Observable Truth**: What must be TRUE from the user's perspective when this story is done?
2. **Required Artifacts**: What files, routes, UI elements, data models must exist?
3. **Wiring Connections**: How must this connect to the rest of the system? (imports, routes, API calls, DB relations)
4. **Failure Points**: What are the most likely ways this could silently fail?
5. **Vertical Slice Order**: What is the thinnest path through all layers that proves this story works end-to-end? This becomes the first implementation task.

These feed directly into acceptance criteria – each criterion should be a verifiable observable truth.

#### Story Definition

For each story, define:
- **ID**: Sequential identifier (S01, S02, etc.)
- **Name**: Brief descriptive name
- **Status**: Tracking field – initially `Pending` (updated to `Spec Ready` / `In Progress` / `Done` during execution)
- **FIS**: Reference to generated spec – initially `–` (updated to file path when `andthen:spec` creates the FIS). Multiple stories may reference the same FIS path when grouped into a composite specification by `andthen:spec-plan`
- **Scope**: 2-4 sentences – what's included and excluded (no implementation approach – that's for `andthen:spec`)
- **Acceptance criteria**: 3-6 testable outcomes – the first 2-3 should be must-be-TRUE observable truths from goal-backward analysis; remaining items are supplementary verification points
- **Key Scenarios** _(optional)_: 2-3 one-line behavioral seeds — the most important happy path, edge case, and error/failure scenario. These are elaborated into full Given/When/Then scenarios in the FIS during `andthen:spec`. Skip for purely structural stories
- **Dependencies**: Other story IDs that must complete first
- **Phase**: Which implementation phase
- **Wave**: Execution wave within phase (W1, W2, W3...) – pre-computed during planning
- **Parallel**: [P] if can run parallel with others in same phase
- **Risk**: Low/Medium/High with brief note if Medium+
- **Asset refs**: Relevant wireframes, ADRs, design system sections

**Do NOT include in stories** (these are deferred to `andthen:spec`; save to `technical-research.md` if discovered during analysis):
- Technical approach, patterns, or library choices
- File paths, line numbers, or code specifics
- Implementation gotchas or constraints with workarounds
- Full technical design or pseudocode

**Gate**: All stories defined


### 4. Create Plan Document

Generate `plan.md` with a structure like the following (adapt phases and structure to fit the project).

**Document references header**: Include a blockquote header at the top linking to all key reference documents discovered during Input Validation (PRD, ADRs, design system, wireframes, etc.). Use relative paths. Omit entries where no document exists – only include actual references.

<example-plan-format>
# Implementation Plan: [Project Name]

> **PRD**: [`prd.md`](./prd.md)
> **ADRs**: [link any ADR files if present]
> **Design System**: [link if present]
> **Wireframes**: [link if present]

## Overview
- **Total stories**: [N]
- **Phases**: [N]
- **Approach**: [1-2 sentence summary]

## Story Catalog

| ID | Name | Phase | Wave | Dependencies | Parallel | Risk | Status | FIS |
|----|------|-------|------|--------------|----------|------|--------|-----|
| S01 | [Name] | Foundation | W1 | - | No | Low | Pending | – |
| S02 | [Name] | Foundation | W1 | S01 | No | Low | Pending | – |
| S03 | Auth Middleware | Core | W2 | S01, S02 | [P] | Medium | Pending | `docs/specs/my-feature/s03-s04-auth-system.md` |
| S04 | Auth API Endpoints | Core | W2 | S03 | [P] | Medium | Pending | `docs/specs/my-feature/s03-s04-auth-system.md` |

## Phase Breakdown

### Phase 1: Foundation
_Sequential execution - establishes base for all features_

#### S01: [Story Name]
**Status**: Pending
**FIS**: –
**Scope**: [2-4 sentences covering what is built and what's excluded]
**Acceptance Criteria**:
- [ ] Project scaffolding exists and builds successfully _(must-be-TRUE)_
- [ ] Core architecture patterns are established and documented _(must-be-TRUE)_
- [ ] [Supplementary criterion]
**Assets**: [Wireframe refs, ADR refs if any]

#### S02: [Story Name]
**Status**: Pending
**FIS**: –
**Scope**: [2-4 sentences]
**Acceptance Criteria**: ...
**Assets**: ...

<!-- Composite FIS example: tightly coupled stories share one spec -->
#### [P] S03: Auth Middleware
**Status**: Pending
**FIS**: docs/specs/my-feature/s03-s04-auth-system.md
**Scope**: ...
**Key Scenarios**: _(elaborated into full Given/When/Then in FIS)_
- Happy: valid credentials → session token returned, user redirected to dashboard
- Edge: concurrent login from two devices → both sessions valid
- Error: expired token on protected route → 401 with clear re-auth prompt

#### [P] S04: Auth API Endpoints
**Status**: Pending
**FIS**: docs/specs/my-feature/s03-s04-auth-system.md
**Scope**: ...
<!-- S03/S04 share a composite FIS; exec-spec runs once for both -->

### Phase 2: Core Features
_Parallel execution where marked [P]_
...

### Phase 3+: Continue pattern
...

## Dependency Graph

```
Dependency arrows:
S01 ──→ S02 ──→ S05
  │       │
  │       └──→ S06
  │
  └──→ S03 ──→ S07
  │
  └──→ S04

Wave assignments:
W1: S01
W2: S02, S03, S04
W3: S05, S06, S07
```

## Risk Summary

| Story | Risk | Concern | Mitigation |
|-------|------|---------|------------|
| S03 | Medium | [Concern] | [Approach] |

## Execution Guide

1. Execute Phase 1 stories sequentially (S01 → S02 → ...)
2. For each story ready to implement:
   - Run the `andthen:spec` skill with story scope as input → update **FIS** field with generated spec path
     Example: `/andthen:spec story S01 of docs/specs/my-feature/plan.md` (or `$andthen:spec ...`)
   - Run the `andthen:exec-spec` skill on the generated FIS
     Example: `/andthen:exec-spec docs/specs/my-feature/story-name.md` (or `$andthen:exec-spec ...`)
   - Check off completed acceptance criteria in this plan
   - Update **Status** field (Pending → Spec Ready → In Progress → Done)
3. Phase 2+ stories marked [P] can run in parallel after dependencies met
4. Run the `andthen:review-gap` skill after completing all stories
   Example: `/andthen:review-gap docs/specs/my-feature/plan.md` (or `$andthen:review-gap ...`)

> **Status tracking**: After each story's spec is created, update the **FIS** field with the spec file path and set **Status** to `Spec Ready`. When implementation starts, set **Status** to `In Progress`. After implementation and review, check off acceptance criteria and set **Status** to `Done`. Update the Story Catalog table status accordingly. `andthen:exec-plan` does this automatically; for manual per-story execution, the orchestrating agent or user is responsible.
>
> **Composite FIS**: When multiple stories share a composite FIS (created by `andthen:spec-plan` for tightly coupled stories), `andthen:exec-spec` runs once for the composite FIS. All constituent stories are marked `Done` when the composite spec execution completes.
</example-plan-format>

**Gate**: Plan document complete

#### Initialize Project State (if STATE.md exists)
If STATE.md exists (path from **Project Document Index**), update it to reflect the new plan:
- Use `andthen:ops update-state phase "Phase 1: {first_phase_name}"`
- Use `andthen:ops update-state status "On Track"`
- Use `andthen:ops update-state note "Plan created: {plan_name} ({N} stories, {M} phases)"`

If STATE.md does not exist, do not create it – suggest it in follow-up actions instead.


### 5. Validation

#### Self-Check
- [ ] All PRD features have corresponding stories
- [ ] Stories have clear boundaries (no overlap)
- [ ] Dependencies accurately mapped
- [ ] Parallel markers correctly applied
- [ ] Wave assignments are pre-computed and consistent with dependencies
- [ ] Risk areas identified (Risk column and Risk Summary populated)
- [ ] No missing functionality (cross-cutting concerns like auth, logging, error pages covered)
- [ ] Not over-granular (combined where sensible)

Optional: Invoke the `andthen:review-doc` skill to validate the plan for requirements coverage and story scope clarity.

**Gate**: Validation complete


## OUTPUT

```
OUTPUT_DIR/
├── prd.md                # Product Requirements Document (if created)
├── plan.md               # Implementation plan
└── technical-research.md # Technical findings from codebase analysis (if substantial)
```

- If from GitHub issue: use `issue-{number}-{feature-name}/` as the output subdirectory name (e.g. `docs/specs/issue-42-user-dashboard/plan.md`). Include issue reference in the PRD and plan document headers.

When complete, print the output's **relative path from the project root**. Do not use absolute paths.

### Publish to GitHub _(if --to-issue)_
If PUBLISH_ISSUE is `true`:
1. Create a GitHub issue with title `[Plan] {project-name}: Implementation Plan`, body from plan.md, and label `plan` (create if it doesn't exist)
2. Print the issue URL


## FOLLOW-UP ACTIONS

After completion, suggest the following next steps. **Recommend starting a clean session** for the context-intensive skills (`spec-plan`, `exec-plan`) — they perform best with a fresh context window.

1. **Start with first story**: Run the `andthen:spec` skill for first story (S01)
   Example: `/andthen:spec story S01 of docs/specs/my-feature/plan.md` (or `$andthen:spec ...`)
2. **Create wireframes** (if UI work): Run the `andthen:wireframes` skill
   Example: `/andthen:wireframes docs/specs/my-feature/prd.md` (or `$andthen:wireframes ...`)
3. **Review plan**: Run the `andthen:review-doc` skill on `plan.md`
   Example: `/andthen:review-doc docs/specs/my-feature/plan.md` (or `$andthen:review-doc ...`)
4. **Batch-generate specs** _(clean session)_: Run the `andthen:spec-plan` skill to pre-create all FIS before execution
   Example: `/andthen:spec-plan docs/specs/my-feature/` (or `$andthen:spec-plan ...`)
5. **Execute the full plan** _(clean session)_: Run the `andthen:exec-plan` skill to spec and implement all stories
   Example: `/andthen:exec-plan docs/specs/my-feature/` (or `$andthen:exec-plan ...`)
6. **Initialize project state** (if not already tracking): Create `docs/STATE.md` for cross-session state tracking via `/andthen:init` or manually from the template in `templates/project-state-templates.md`
