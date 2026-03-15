---
description: Creates implementation plan with story breakdown. Can start from existing PRD or discover requirements first. Lightweight planning - detailed specs created JIT per story.
argument-hint: [Specs directory containing PRD, or requirements source (file/URL/description)]
---

# Create Implementation Plan

Transform requirements into lightweight implementation plan with story breakdown. If a PRD already exists, starts from that. If not, runs requirements discovery to create one first.

Stories are scoped and sequenced but NOT fully specified - use `/andthen:spec` just-in-time before implementing each story.

**Philosophy**: Detailed specs decay quickly. This command creates just enough structure to sequence work and track progress, while deferring detailed specification to implementation time.


## Variables

_Specs directory containing PRD, or requirements source (**required**):_
INPUT: $ARGUMENTS

_Output directory (defaults to input directory, or `<project_root>/docs/specs/` for new PRDs):_
OUTPUT_DIR: `INPUT` (if directory) or `<project_root>/docs/specs/` _(or as configured in **Project Document Index**)_


## Instructions

- **Make sure `INPUT` is provided** - otherwise **STOP** immediately and ask user for input
- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails**
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Orchestrate, don't do everything yourself** - Delegate research, analysis, and exploration to sub-agents _(if supported by your coding agent)_ (see Workflow below)
- **Lightweight planning** - Stories define scope, not implementation details
- **No over-engineering** - Minimum stories to cover requirements
- **Progressive implementation** - Organize into logical phases (examples provided are templates, adapt to project)
- **JIT specification** - Detailed specs come later via `/andthen:spec`
- **Interactive when discovering requirements** - Interview user iteratively; don't assume answers
- **Focus on "what" not "how"** - Requirements, not implementation details
- **Be specific** - Replace vague terms with measurable criteria
- **Document decisions** - Record rationale, trade-offs, alternatives considered


## Workflow

### 1. Input Validation & PRD Detection

1. **Parse INPUT** - Determine type:
   - **Directory with PRD**: `INPUT` is a directory containing `prd.md` → proceed to Step 2
   - **File path**: Read and extract requirements → proceed to Step 1b
   - **URL**: Fetch and extract requirements → proceed to Step 1b
   - **Inline description**: Use directly → proceed to Step 1b

2. **If PRD found** (directory with existing `prd.md`):
   - Document optional assets if present (Architecture/ADRs, Design system, Wireframes)
   - **Gate**: PRD validated → skip to Step 2

3. **If no PRD** (requirements source provided):
   - Validate prerequisites: requirements should be reasonably refined (not raw ideas)
   - If input is too vague, recommend `/andthen:clarify` first
   - Initial gap analysis — document what's explicitly stated, assumed/implied, and missing/unclear (functional requirements, user flows, edge cases, success criteria, business context, MVP scope)
   - Proceed to Step 1b (Requirements Discovery)

**Gate**: Input validated


### 1b. Requirements Discovery & PRD Creation _(skip if PRD already exists)_

#### Requirements Discovery Interview

Interview user to fill gaps. Ask 3-5 targeted questions at a time, iterate until no major gaps remain.

**Core Functionality**
- Must-have vs nice-to-have features?
- Specific workflow for each major user action?
- Data validation rules and constraints?
- Error handling and recovery?
- Does this involve UI/frontend work? (determines if wireframes needed)

**Users & Permissions**
- User roles and their permissions?
- Expected user onboarding process?
- Accessibility requirements?
- Devices and platforms to support?

**Business Logic**
- Business rules and constraints?
- Concurrent access handling?
- Data retention and deletion policies?
- Compliance or regulatory requirements?

**Edge Cases & Errors**
- Network connectivity loss handling?
- Incomplete or partial data handling?
- Timeout and retry policies?
- Graceful degradation under load?
- Fallback for external dependency failures?

**Success Metrics**
- Specific metrics defining success?
- Performance benchmarks?
- Quality thresholds?

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
Use the `andthen-review-doc` skill to validate PRD for:
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


### 2. Requirements Analysis

**Delegate** codebase exploration to sub-agents _(if supported by your coding agent)_ to keep your context lean:

- Spawn an **Explore agent** _(if supported by your coding agent)_ to analyze codebase structure, existing patterns, and relevant files

Collect sub-agent results and synthesize into a unified understanding of:

#### Understand the PRD
- All requirements and user stories
- MVP scope and boundaries
- Success criteria
- Prioritization (P0/P1/P2)

#### Map to Implementation Units
For each major feature/requirement:
- Identify natural implementation boundaries
- Note dependencies between features
- Flag complexity and risk areas
- Group related functionality

**Gate**: Feature mapping complete


### 3. Story Breakdown

#### Story Guidelines

**Each story should be:**
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
Phase 1: Foundation (Sequential)
├── Project setup / scaffolding
├── Core architecture / routing
└── Data layer setup

Phase 2: Core Features (Parallel where possible)
├── [P] Feature A
├── [P] Feature B
└── [P] Feature C (depends on A)

Phase 3: Integration (Sequential)
├── External service connections
├── API integrations
└── Cross-feature integration

Phase 4: Polish (Parallel)
├── [P] UI refinement
├── [P] Error handling
├── [P] Performance
└── [P] Accessibility
```

#### Story Definition

For each story, define:
- **ID**: Sequential identifier (S01, S02, etc.)
- **Name**: Brief descriptive name
- **Status**: Tracking field — initially `Pending` (updated to `In Progress` / `Done` during execution)
- **FIS**: Reference to generated spec — initially `—` (updated to file path when `/andthen:spec` creates the FIS)
- **Scope**: 2-4 sentences — what's included and excluded (no implementation approach — that's for `/andthen:spec`)
- **Acceptance criteria**: 3-6 testable outcomes — specific and unambiguous
- **Dependencies**: Other story IDs that must complete first
- **Phase**: Which implementation phase
- **Parallel**: [P] if can run parallel with others in same phase
- **Risk**: Low/Medium/High with brief note if Medium+
- **Asset refs**: Relevant wireframes, ADRs, design system sections

**Do NOT include** (these are deferred to `/andthen:spec`):
- Technical approach, patterns, or library choices
- File paths, line numbers, or code specifics
- Implementation gotchas or constraints with workarounds
- Full technical design or pseudocode

**Gate**: All stories defined


### 4. Create Plan Document

Generate `plan.md` with a structure like the following (adapt phases and structure to fit the project).

**Document references header**: Include a blockquote header at the top linking to all key reference documents discovered during Input Validation (PRD, ADRs, design system, wireframes, etc.). Use relative paths. Omit entries where no document exists — only include actual references.

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

| ID | Name | Phase | Dependencies | Parallel | Risk | Status |
|----|------|-------|--------------|----------|------|--------|
| S01 | [Name] | Foundation | - | No | Low | Pending |
| S02 | [Name] | Foundation | S01 | No | Low | Pending |
| S03 | [Name] | Core | S01, S02 | [P] | Medium | Pending |

## Phase Breakdown

### Phase 1: Foundation
_Sequential execution - establishes base for all features_

#### S01: [Story Name]
**Status**: Pending
**FIS**: —
**Scope**: [2-4 sentences covering what is built and what's excluded]
**Acceptance Criteria**:
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]
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
S01 ──→ S02 ──→ S05
  │       │
  │       └──→ S06
  │
  └──→ S03 ──→ S07
  │
  └──→ S04
```

## Risk Summary

| Story | Risk | Concern | Mitigation |
|-------|------|---------|------------|
| S03 | Medium | [Concern] | [Approach] |

## Execution Guide

1. Execute Phase 1 stories sequentially (S01 → S02 → ...)
2. For each story ready to implement:
   - Run `/andthen:spec` with story scope as input → update **FIS** field with generated spec path
   - Run `/andthen:exec-spec` on generated FIS
   - Check off completed acceptance criteria in this plan
   - Update **Status** field (Pending → In Progress → Done)
3. Phase 2+ stories marked [P] can run in parallel after dependencies met
4. Use `/andthen:review-gap` after completing all stories

> **Status tracking**: After each story's spec is created, update the **FIS** field with the spec file path. After implementation and review, check off acceptance criteria and set **Status** to Done. Update the Story Catalog table status accordingly. `/andthen:exec-plan` does this automatically; for manual per-story execution, the orchestrating agent or user is responsible.
</example-plan-format>

**Gate**: Plan document complete


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
Use the `andthen-review-doc` skill to validate plan for:
- Requirements coverage
- Story scope clarity
- Dependency correctness

**Gate**: Validation complete


## Output

```
OUTPUT_DIR/
└── plan.md    # Implementation plan
```

When complete, print the output's **relative path from the project root**. Do not use absolute paths.


## Follow-Up Actions

After completion, suggest:

1. **Start implementation**: `/andthen:spec` for first story (S01)
2. **Create wireframes** (if UI work): `/andthen:wireframes`
3. **Create GitHub issues** (if requested):
   ```bash
   # Create milestone
   gh milestone create "[Project Name] MVP" --description "..."

   # Create issues per story
   gh issue create --title "S01: [Story Name]" --body "..." --milestone "[Project Name] MVP"
   gh issue create --title "S02: [Story Name]" --body "..." --milestone "[Project Name] MVP"
   # ... etc
   ```
4. **Review plan**: Use the `andthen-review-doc` skill on `plan.md`
