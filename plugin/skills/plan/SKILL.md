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

Interview user to fill gaps. Ask 3-5 targeted questions at a time, then **STOP and WAIT for the user's response** before continuing. Do NOT assume or infer answers – you MUST receive actual answers from the user. Iterate until no major gaps remain.

> **CRITICAL**: After presenting questions, you must stop your response and wait for user input. Do not proceed past this section until the user has answered your questions and you've confirmed no major gaps remain. Use the `AskUserQuestion` tool if available in your environment.

Conduct requirements discovery covering: users and personas, core workflows, data model, integrations, constraints, and non-functional requirements. Ask questions iteratively – **STOP and WAIT** for user responses between rounds.

Focus areas:
- Core functionality (must-have vs nice-to-have, workflows, validation, error handling, UI involvement)
- Users & permissions (roles, accessibility, devices)
- Business logic (rules, concurrency, compliance)
- Edge cases & error handling (connectivity, partial data, timeouts, graceful degradation)
- Success metrics (measurable outcomes, performance benchmarks)

**Gate**: All critical questions answered, no blocking ambiguities


#### Structure PRD

Based on interview responses, structure comprehensive PRD:

##### Executive Summary
- Project title
- Problem statement with quantified impact
- Product vision and objectives
- Target audience and user personas
- Success definition with measurable metrics

##### Problem Definition & Context
- Clear problem statement with evidence
- User research insights and pain points
- Market opportunity (if applicable)
- Competitive landscape (if applicable)

##### MVP Scope & Boundaries

**In Scope**
- Core functionality (must-haves)
- Explicit inclusions

**Out of Scope**
- Explicit exclusions
- Deferred to future iterations

**MVP Boundary**
- Minimum viable version definition
- MVP validation approach

##### Functional Requirements

**User Stories**
- Format: "As a [user type], I want [goal], so that [benefit]"
- Include acceptance criteria for each

**Feature Specifications**
For each feature:
- Description and purpose
- Testable acceptance criteria
- Input/output specifications
- Validation rules
- Error handling
- Priority (P0/P1/P2)

**Core User Flows**
- Primary flows with step-by-step descriptions
- Alternative paths
- Error scenarios and recovery

**UI Wireframes** _(if applicable - skip for backend-only work)_
- Simple ASCII wireframes for core screens/views
- Focus on layout structure and key elements only
- Show primary user interaction points
- Keep minimal - just enough to communicate intent

**Data Requirements**
- Data models and relationships
- Required fields and constraints
- Data validation rules
- Privacy considerations

##### Non-Functional Requirements

**Performance**
- Response time expectations
- Throughput requirements
- Scalability considerations

**Reliability**
- Uptime requirements
- Error recovery expectations
- Data backup needs

**Security**
- Authentication requirements
- Authorization and access control
- Data protection needs
- Compliance requirements

**Usability**
- Accessibility standards
- Browser/device compatibility
- Internationalization needs

##### Edge Cases
| Scenario | Expected Behavior |
|----------|------------------|
| [Edge case] | [Handling] |

##### Constraints & Assumptions

**Constraints**
- Technical constraints
- Resource limitations
- Regulatory constraints

**Assumptions**
- User behavior assumptions
- Technical assumptions
- Business assumptions
- External dependencies

**Gate**: PRD structure complete with all sections filled


#### Prioritization

Apply systematic prioritization to features:

**MoSCoW Classification**
- **Must have**: Core MVP functionality
- **Should have**: Important but not vital
- **Could have**: Desirable but optional
- **Won't have**: Explicitly out of scope

**Priority Levels**
- P0: Critical - MVP blocker
- P1: High - Core functionality
- P2: Medium - Important enhancement

**Gate**: All features prioritized


#### PRD Validation

##### Completeness Check
- [ ] Problem definition clearly articulated with impact
- [ ] All user stories have testable acceptance criteria
- [ ] Every feature has defined error handling
- [ ] All edge cases have specified behavior
- [ ] Success metrics are specific and measurable
- [ ] Non-functional requirements have clear thresholds
- [ ] No ambiguous terms without definitions

##### Quality Check
- [ ] Requirements focus on "what" not "how"
- [ ] All assumptions documented
- [ ] Dependencies identified
- [ ] Security considerations included
- [ ] Accessibility standards specified
- [ ] No conflicting requirements
- [ ] No over-specification or gold-plating

##### Optional: Peer Review
Use the `andthen:review-doc` skill to validate PRD for:
- Missing requirements or user stories
- Over-engineered or unnecessarily complex features
- Conflicting requirements
- Ambiguities and unclear priorities
- Scope creep beyond MVP

**Action**: Revise PRD based on review findings before finalizing.

**Gate**: All validation checks pass


#### Generate PRD Document

Generate markdown document following this structure:

```markdown
# Product Requirements Document: [Name]

## Executive Summary
- **Project**: [Title]
- **Problem**: [Statement with quantified impact]
- **Vision**: [Product vision]
- **Target Users**: [User personas]
- **Success Metrics**: [Measurable outcomes]

## Problem Definition
[Clear problem statement with evidence and context]

## Scope

### In Scope
- [Explicit inclusions]

### Out of Scope
- [Explicit exclusions]

### MVP Boundary
- [Minimum viable version definition]

## Functional Requirements

### User Stories
| ID | Story | Acceptance Criteria | Priority |
|----|-------|---------------------|----------|
| US01 | As a [user], I want [goal], so that [benefit] | [Criteria] | P0/P1/P2 |

### Feature Specifications

#### [Feature Name]
- **Description**: [What and why]
- **Acceptance Criteria**: [Testable criteria]
- **Inputs**: [Expected inputs]
- **Outputs**: [Expected outputs]
- **Validation**: [Rules and constraints]
- **Error Handling**: [Error scenarios and recovery]
- **Priority**: P0/P1/P2

### User Flows
1. [Primary flow with steps]

### UI Wireframes
<!-- Include only if PRD involves UI work -->
```
+----------------------------------+
|  [Screen Name]                   |
+----------------------------------+
|  [Header/Nav]                    |
+----------------------------------+
|                                  |
|  [Main Content Area]             |
|  - Key element 1                 |
|  - Key element 2                 |
|                                  |
+----------------------------------+
|  [Actions/Footer]                |
+----------------------------------+
```

### Data Requirements
- [Data models, fields, constraints]

## Non-Functional Requirements

### Performance
- [Response times, throughput, scalability]

### Reliability
- [Uptime, recovery, backup]

### Security
- [Auth, access control, compliance]

### Usability
- [Accessibility, compatibility, i18n]

## Edge Cases
| Scenario | Expected Behavior |
|----------|------------------|
| [Edge case] | [Handling] |

## Constraints & Assumptions

### Constraints
- [Technical, resource, regulatory]

### Assumptions
- [User, technical, business assumptions]

### Dependencies
| Dependency | Purpose | Risk |
|------------|---------|------|
| [System/API] | [Why needed] | [Risk level] |

## Decisions Log
| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| [Choice] | [Why] | [Other options rejected] |
```

Store PRD in: `OUTPUT_DIR/<feature-name>/prd.md`

**Gate**: PRD created → continue to Step 2


### 1c. PRD Creation from Existing Artifacts _(skip if PRD already exists or no prior artifacts found)_

Use existing artifacts (`requirements-clarification.md` from `andthen:clarify` and/or `prd-draft.md`) as the primary basis for creating the PRD. This path avoids duplicating discovery work already completed.

#### Assess Existing Coverage

Review the available artifacts and assess PRD readiness:

- Map existing content against the PRD structure (see Step 1b: Structure PRD)
- Identify sections that are fully covered by existing artifacts
- Identify gaps or sections that need additional information

#### Targeted Gap-Filling _(only if needed)_

If significant gaps remain after reviewing existing artifacts, conduct a **focused** interview covering only the missing areas. Ask 3-5 questions at a time, then **STOP and WAIT for the user's response**.

> **CRITICAL**: Do NOT re-ask questions already answered in the existing artifacts. Only ask about genuinely missing information.

Skip this step entirely if existing artifacts provide sufficient coverage for all PRD sections.

**Gate**: All gaps resolved or deemed non-blocking

#### Structure & Generate PRD

Using existing artifacts as the primary source, structure the PRD following the same format as Step 1b: Structure PRD. Preserve decisions, rationale, and specific details from the existing artifacts – do not paraphrase or generalize away specifics.

Then proceed through **Prioritization → PRD Validation → Generate PRD Document** (same substeps as Step 1b).

**Gate**: PRD created → continue to Step 2


### 2. Requirements Analysis

**Delegate** codebase exploration to sub-agents _(if supported by your coding agent)_ to keep your context lean:

- Spawn an **Explore agent** _(if supported by your coding agent)_ to analyze codebase structure, existing patterns, and relevant files

Collect sub-agent results and synthesize into a unified understanding of:

- **Project state context**: Read `STATE.md` (path from **Project Document Index**, default: `docs/STATE.md`) if it exists. Use current phase, active stories, blockers, and recent decisions as context for planning – e.g., if blockers exist, plan stories to address them; if a phase is in progress, the new plan may be a continuation.

#### Understand the PRD
- All requirements and user stories
- MVP scope and boundaries
- Success criteria
- Prioritization (P0/P1/P2)
- Domain terminology – reference `UBIQUITOUS_LANGUAGE.md` if it exists; use canonical terms in story names and acceptance criteria

#### Map to Implementation Units
For each major feature/requirement:
- Identify natural implementation boundaries
- Note dependencies between features
- Flag complexity and risk areas
- Group related functionality

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
- **FIS**: Reference to generated spec – initially `–` (updated to file path when `andthen:spec` creates the FIS)
- **Scope**: 2-4 sentences – what's included and excluded (no implementation approach – that's for `andthen:spec`)
- **Acceptance criteria**: 3-6 testable outcomes – the first 2-3 should be must-be-TRUE observable truths from goal-backward analysis; remaining items are supplementary verification points
- **Dependencies**: Other story IDs that must complete first
- **Phase**: Which implementation phase
- **Wave**: Execution wave within phase (W1, W2, W3...) – pre-computed during planning
- **Parallel**: [P] if can run parallel with others in same phase
- **Risk**: Low/Medium/High with brief note if Medium+
- **Asset refs**: Relevant wireframes, ADRs, design system sections

**Do NOT include** (these are deferred to `andthen:spec`):
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

| ID | Name | Phase | Wave | Dependencies | Parallel | Risk | Status |
|----|------|-------|------|--------------|----------|------|--------|
| S01 | [Name] | Foundation | W1 | - | No | Low | Pending |
| S02 | [Name] | Foundation | W1 | S01 | No | Low | Pending |
| S03 | [Name] | Core | W2 | S01, S02 | [P] | Medium | Pending |

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
...

### Phase 2: Core Features
_Parallel execution where marked [P]_

#### [P] S03: [Story Name]
...

### Phase 3: Integration
...

### Phase 4: Polish
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
- [ ] No missing functionality
- [ ] Stories have clear boundaries (no overlap)
- [ ] Dependencies accurately mapped
- [ ] Parallel markers correctly applied
- [ ] Risk areas identified
- [ ] Not over-granular (combined where sensible)

#### Optional: Peer Review
Use the `andthen:review-doc` skill to validate plan for:
- Requirements coverage
- Story scope clarity
- Dependency correctness

**Gate**: Validation complete


## OUTPUT

```
OUTPUT_DIR/
├── prd.md     # Product Requirements Document (if created)
└── plan.md    # Implementation plan
```

- If from GitHub issue: use `issue-{number}-{feature-name}/` as the output subdirectory name (e.g. `docs/specs/issue-42-user-dashboard/plan.md`). Include issue reference in the PRD and plan document headers.

When complete, print the output's **relative path from the project root**. Do not use absolute paths.

### Publish to GitHub _(if --to-issue)_
If PUBLISH_ISSUE is `true`:
1. Create a GitHub issue using `gh issue create`:
   - Title: `[Plan] {project-name}: Implementation Plan`
   - Body: Contents of the generated plan.md
   - Labels: `plan` (create if it doesn't exist)
2. Print the issue URL


## FOLLOW-UP ACTIONS

After completion, suggest:

1. **Start implementation**: Run the `andthen:spec` skill for first story (S01)
   Example: `/andthen:spec story S01 of docs/specs/my-feature/plan.md` (or `$andthen:spec ...`)
2. **Create wireframes** (if UI work): Run the `andthen:wireframes` skill
   Example: `/andthen:wireframes docs/specs/my-feature/prd.md` (or `$andthen:wireframes ...`)
3. **Create GitHub issues** (if requested):
   ```bash
   # Create milestone
   gh milestone create "[Project Name] MVP" --description "..."

   # Create issues per story
   gh issue create --title "S01: [Story Name]" --body "..." --milestone "[Project Name] MVP"
   gh issue create --title "S02: [Story Name]" --body "..." --milestone "[Project Name] MVP"
   # ... etc
   ```
4. **Review plan**: Run the `andthen:review-doc` skill on `plan.md`
   Example: `/andthen:review-doc docs/specs/my-feature/plan.md` (or `$andthen:review-doc ...`)
5. **Initialize project state** (if not already tracking): Create `docs/STATE.md` for cross-session state tracking via `/andthen:init` or manually from the template in `templates/project-state-templates.md`
