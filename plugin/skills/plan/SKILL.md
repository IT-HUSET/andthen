---
description: Use when the user wants a PRD, an implementation plan, or a feature broken into stories. Creates a PRD and multi-story implementation plan for larger work, building on `andthen:clarify` artifacts when present. Trigger on 'create a plan', 'create a PRD', 'break this into stories', 'plan this feature'.
argument-hint: "[Specs directory or requirements source] | --issue <number> [--to-issue]"
---

# Create PRD & Implementation Plan


Transform requirements into lightweight implementation plan with story breakdown. If a PRD already exists, starts from that. If prior artifacts exist (e.g., `requirements-clarification.md` from `andthen:clarify` or a draft PRD), uses them as the basis for PRD creation without re-doing discovery. If nothing exists, performs headless requirements synthesis to create a PRD first. Use `andthen:clarify` only when the user explicitly wants interactive discovery or when the input is too ambiguous to support any defensible plan.

Stories are scoped and sequenced but NOT fully specified - generate detailed specs later via `andthen:spec` (manual per-story flow) or `andthen:spec-plan` (batch generation for `exec-plan`).

**Philosophy**: Detailed specs decay quickly. This command creates just enough structure to sequence work and track progress, while deferring detailed specification to implementation time.


## VARIABLES

_Specs directory (with PRD, requirements-clarification, or draft PRD), or requirements source (**required**):_
INPUT: $ARGUMENTS

_Output directory (defaults to input directory, or `<project_root>/docs/specs/` for new PRDs):_
OUTPUT_DIR: `INPUT` (if directory), or parent directory of `INPUT` (if file is a prior artifact like `prd-draft.md`), or `<project_root>/docs/specs/` (for other inputs) _(or as configured in **Project Document Index**)_

### Optional Flags
- `--issue <number>` → Fetch and use a GitHub issue as requirements input
- `--to-issue` → PUBLISH_ISSUE: Publish plan as a GitHub issue after saving locally


## USAGE

```
/plan docs/specs/my-feature/            # From directory with PRD or prior artifacts
/plan @docs/requirements.md             # From requirements file
/plan --issue 42                        # From GitHub issue
/plan "Build a user dashboard"          # From inline description
/plan docs/specs/my-feature/prd-draft.md # From draft PRD file
/plan docs/specs/my-feature/ --to-issue # Create plan and publish to GitHub issue
```


## INSTRUCTIONS

- **Make sure `INPUT` is provided** - otherwise **STOP** immediately with a missing-input error that states requirements input or a source artifact is required
- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails**
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Orchestrate, don't do everything yourself** - Delegate research, analysis, and exploration to sub-agents _(if supported by your coding agent)_ (see Workflow below)
- **Lightweight planning** - Stories define scope, not implementation details
- **No over-engineering** - Minimum stories to cover requirements
- **Progressive implementation** - Organize into logical phases (examples provided are templates, adapt to project)
- **Deferred specification** - Detailed specs come later via `andthen:spec` or `andthen:spec-plan`
- **Headless-first planning** - Unless the user explicitly asked for interactive discovery, continue to completion without pausing for routine clarification. Make reasonable assumptions, document them explicitly, and surface unresolved questions in the output artifacts instead of blocking.
- **Stop only on true contract failures** - Missing required input, incompatible typed artifacts, or ambiguity so severe that no defensible PRD/plan can be produced are valid stop conditions. Ordinary requirement gaps are not.
- **Focus on "what" not "how"** - Requirements, not implementation details
- **Be specific** - Replace vague terms with measurable criteria
- **Document decisions** - Record rationale, trade-offs, alternatives considered


## GOTCHAS
- Agent creates too many small stories – push for fewer, larger vertical slices
- Skipping requirements discovery when no PRD exists – if no prior artifacts, run discovery first
- Wave assignments get ignored during execution – explicitly mark dependencies between stories
- Not reading the `State` document (see **Project Document Index**) before planning – misses context about current phase, active blockers, and recent decisions that should inform story priorities
- **Carried-forward stories without PRD coverage** – use the **Provenance** field; a story with no PRD feature and no provenance is a traceability gap
- **Inconsistent FIS path naming** – when composite stories share a FIS, the FIS filename must use the lowest story ID as prefix and include all constituent IDs (e.g., `s01-s02-s03-feature-name.md`). Do not re-assign story-to-FIS mapping after initial assignment — downstream agents and reviewers rely on ID-based file discovery


## WORKFLOW

### 1. Input Validation & PRD Detection

1. **Parse INPUT** - Determine type:
   - **`--issue` flag present** (or INPUT refers to a GitHub issue): Extract issue number from INPUT, use `gh issue view <number>` to fetch issue details (title, body, labels, comments), then inspect the body for a typed envelope per `${CLAUDE_PLUGIN_ROOT}/references/github-artifact-roundtrip.md`.
     - If `artifact_type: plan-bundle`, extract embedded files preserving their repo-relative paths; treat the extracted directory as `INPUT` and proceed as if the user had provided the local plan directory directly.
     - If the issue contains another typed workflow artifact (`fis-bundle`, `triage-plan`, `triage-completion`, or any `*-review` report), **STOP** and exit with the matching downstream skill instead of re-planning from the artifact body.
     - Otherwise use the issue content as requirements input. Store issue number for reference in generated plan. → proceed to Step 1b
   - **Directory with PRD**: `INPUT` is a directory containing `prd.md` → proceed to Step 2
   - **Directory with prior artifacts**: `INPUT` is a directory containing `requirements-clarification.md` (from `andthen:clarify`) and/or a draft PRD (`prd-draft.md`), but no finalized `prd.md` → proceed to Step 1c
   - **File path**: Read file. If it is a prior artifact (`prd-draft.md` or `requirements-clarification.md`) → proceed to Step 1c. Otherwise → proceed to Step 1b
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
   - If input is broad but directionally usable, infer the smallest coherent MVP, document assumptions and unresolved questions explicitly, and continue
   - If input is too vague to identify a coherent feature boundary, **STOP** and report the minimum missing contract needed to produce a defensible PRD/plan. Mention `andthen:clarify` as the interactive fallback.
   - Initial gap analysis – document what's explicitly stated, assumed/implied, and missing/unclear (functional requirements, user flows, edge cases, success criteria, business context, MVP scope)
   - Proceed to Step 1b (Requirements Synthesis)

**Gate**: Input validated


### 1b. Requirements Synthesis & PRD Creation _(skip if PRD already exists)_

#### Headless Requirements Synthesis

Cover the same areas as `andthen:clarify` Phase 2, but default to synthesis rather than interview: users & personas, core workflows, data model, integrations, constraints, NFRs, and success metrics. Fill ordinary gaps using explicit assumptions grounded in the source material, codebase patterns, adjacent artifacts, and standard product conventions.

When a gap materially affects scope or prioritization and the evidence is weak, choose the most conservative MVP assumption that still allows a coherent plan. Record it in `prd.md` under `Constraints & Assumptions` and in the `Decisions Log` with alternatives considered. Do not pause the run for routine clarification.

If the input is so ambiguous that multiple incompatible plans are equally plausible and none can be justified from the available evidence, **STOP** and report the smallest missing decisions required. Use `andthen:clarify` only as an explicit fallback for that case.

**Gate**: PRD is specific enough for planning; major assumptions and unresolved questions are documented explicitly


#### Generate PRD Document

Structure the PRD from the synthesized requirements and save as `OUTPUT_DIR/<feature-name>/prd.md`. Apply MoSCoW prioritization (Must/Should/Could/Won't) and P0/P1/P2 levels to features.

Use the PRD template at [`templates/prd-template.md`](templates/prd-template.md) as the baseline shape. Keep the required sections, adapt optional subsections to the project, and preserve concrete decisions from discovery rather than generalizing them away.

When running headlessly, do not leave important ambiguity implicit. Capture it as an explicit assumption, dependency, or deferred decision in the PRD so downstream skills inherit a usable contract.

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

Optional: Invoke the `andthen:review --doc-only` skill to validate the PRD before finalizing.

**Gate**: PRD created → continue to Step 2


### 1c. PRD Creation from Existing Artifacts _(skip if PRD already exists or no prior artifacts found)_

Use existing artifacts (`requirements-clarification.md` from `andthen:clarify` and/or `prd-draft.md`) as the primary basis for creating the PRD. This path avoids duplicating discovery work already completed.

- Map existing content against the PRD template (see Step 1b); use [`templates/prd-template.md`](templates/prd-template.md) as the target structure and only ask focused follow-up questions for genuinely missing sections
- If significant gaps remain, fill only the missing areas using bounded assumptions derived from the existing artifacts, codebase context, and adjacent documents. Do NOT re-ask questions already answered in the existing artifacts, and do not pause the run for routine clarification.
- If the artifacts are too ambiguous to support any defensible PRD shape, **STOP** and report the minimum missing decisions required. Mention `andthen:clarify` only as the interactive fallback for that case.
- **Extract technical details**: If the draft contains implementation-level content (architecture patterns, technology choices, API details, framework constraints, integration specifics), extract these into `{OUTPUT_DIR}/.technical-research.md` rather than carrying them into the PRD. The PRD should focus on *what* to build; technical details are preserved for downstream skills.
- Structure and generate the PRD following the same template as Step 1b. Preserve decisions, rationale, and specific details from existing artifacts – do not paraphrase or generalize away specifics.
- Apply same Prioritization → PRD Validation steps as Step 1b.

**Gate**: PRD created → continue to Step 2


### 2. Requirements Analysis

> **Hard gate**: Verify `prd.md` exists in OUTPUT_DIR before proceeding. If only a draft or clarification artifact exists, you skipped PRD finalization — go back to Step 1c.

Delegate codebase exploration to a sub-agent _(if supported)_ to keep context lean. Read the `State` document (see **Project Document Index**; default: `docs/STATE.md`) if it exists – use current phase, active stories, and blockers to inform story priorities. Reference the `Ubiquitous Language` document (see **Project Document Index**) if it exists; use canonical terms in story names and acceptance criteria.

Synthesize into a unified understanding of: all PRD requirements and user stories, MVP scope, success criteria, prioritization (P0/P1/P2), natural implementation boundaries, feature dependencies, and complexity/risk areas.

**Technical research**: If codebase exploration surfaces substantial technical findings (architecture patterns, framework constraints, integration details, existing conventions) that would be useful during spec creation or execution, save them to `{OUTPUT_DIR}/.technical-research.md` (append to existing content if the file was already created in Step 1c). This keeps the PRD and plan free of implementation details while preserving research for downstream skills (`andthen:spec`, `andthen:spec-plan`). Skip this if findings are minimal — not every plan needs a technical research document.

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
- **Provenance** _(if carried forward)_: `Carried from {milestone}: {original-story-id}` — required when a story has no corresponding PRD feature
- **Asset refs**: Relevant wireframes, ADRs, design system sections

**Do NOT include in stories** (these are deferred to `andthen:spec`; save to `.technical-research.md` if discovered during analysis):
- Technical approach, patterns, or library choices
- File paths, line numbers, or code specifics
- Implementation gotchas or constraints with workarounds
- Full technical design or pseudocode

**Gate**: All stories defined


### 4. Create Plan Document

Generate `plan.md` using the template at [`templates/plan-template.md`](templates/plan-template.md).

This template defines the document's operational contract. Preserve the heading names, Story Catalog columns, and standard story metadata labels because downstream skills parse them directly. Adapt the phase names, story count, and example content to the project.

**Document references header**: Include a blockquote header at the top linking to all key reference documents discovered during Input Validation (PRD, ADRs, design system, wireframes, etc.). Use relative paths. Omit entries where no document exists – only include actual references.

Keep these invariants from the template:
- Story Catalog columns remain `ID | Name | Phase | Wave | Dependencies | Parallel | Risk | Status | FIS`
- Each story defines `**Status**`, `**FIS**`, `**Phase**`, `**Wave**`, `**Dependencies**`, `**Parallel**`, `**Risk**`, `**Scope**`, `**Acceptance Criteria**`, and `**Asset refs**`
- `**Key Scenarios**` stays optional and seeds later FIS scenario generation
- `**Provenance**` is required for stories with no direct PRD feature coverage
- Composite/shared FIS mappings remain stable once assigned

**Gate**: Plan document complete

#### Initialize Project State (if the `State` document exists; see **Project Document Index**)
If the `State` document exists (path from **Project Document Index**), update it to reflect the new plan:
- Use `andthen:ops update-state phase "Phase 1: {first_phase_name}"`
- Use `andthen:ops update-state status "On Track"`
- Use `andthen:ops update-state note "Plan created: {plan_name} ({N} stories, {M} phases)"`

If the `State` document does not exist (see **Project Document Index**), do not create it – suggest it in follow-up actions instead.


### 5. Validation

#### Self-Check
- [ ] All PRD features have corresponding stories
- [ ] Stories without PRD feature coverage have a **Provenance** annotation
- [ ] Stories have clear boundaries (no overlap)
- [ ] Dependencies accurately mapped
- [ ] Parallel markers correctly applied
- [ ] Wave assignments are pre-computed and consistent with dependencies
- [ ] Risk areas identified (Risk column and Risk Summary populated)
- [ ] No missing functionality (cross-cutting concerns like auth, logging, error pages covered)
- [ ] Not over-granular (combined where sensible)

Optional: Invoke the `andthen:review --doc-only` skill to validate the plan for requirements coverage and story scope clarity.

**Gate**: Validation complete


## OUTPUT

```
OUTPUT_DIR/
├── prd.md                # Product Requirements Document (if created)
├── plan.md               # Implementation plan
└── .technical-research.md # Technical findings from codebase analysis (if substantial)
```

- If from GitHub issue: use `issue-{number}-{feature-name}/` as the output subdirectory name (e.g. `docs/specs/issue-42-user-dashboard/plan.md`). Include issue reference in the PRD and plan document headers.

When complete, print the output's **relative path from the project root**. Do not use absolute paths.

### Publish to GitHub _(if --to-issue)_
If PUBLISH_ISSUE is `true`:
1. Follow `${CLAUDE_PLUGIN_ROOT}/references/github-artifact-roundtrip.md`
   - `artifact_type`: `plan-bundle`
   - Title: `[Plan] {project-name}: Implementation Plan`
   - Primary file: `plan.md`
   - Companion files: `prd.md`; include `.technical-research.md` when it exists
   - Labels: `plan`, `andthen-artifact`
2. Print the issue URL and the local primary path (`plan.md`)


## FOLLOW-UP ACTIONS

After completion, suggest the following next steps. **Recommend starting a clean session** for the context-intensive skills (`spec-plan`, `exec-plan`) — they perform best with a fresh context window.

1. **Start with first story**: Run the `andthen:spec` skill for first story (S01)
   Example: `/andthen:spec story S01 of docs/specs/my-feature/plan.md` (or `$andthen:spec ...`)
2. **Create wireframes** (if UI work): Run the `andthen:wireframes` skill
   Example: `/andthen:wireframes docs/specs/my-feature/prd.md` (or `$andthen:wireframes ...`)
3. **Review plan**: Run the `andthen:review --doc-only` skill on `plan.md`
   Example: `/andthen:review --doc-only docs/specs/my-feature/plan.md` (or `$andthen:review --doc-only ...`)
4. **Batch-generate specs** _(clean session)_: Run the `andthen:spec-plan` skill to pre-create all FIS before execution
   Example: `/andthen:spec-plan docs/specs/my-feature/` (or `$andthen:spec-plan ...`)
5. **Execute the full plan** _(clean session)_: Run the `andthen:exec-plan` skill to spec and implement all stories
   Example: `/andthen:exec-plan docs/specs/my-feature/` (or `$andthen:exec-plan ...`)
6. **Initialize project state** (if not already tracking): Create the `State` document as defined in the **Project Document Index** via `/andthen:init` or manually from the template in `templates/project-state-templates.md` (default path: `docs/STATE.md`)


---


## Appendix: Templates

**USE THE TEMPLATES**:
- PRD: [`templates/prd-template.md`](templates/prd-template.md)
- Plan: [`templates/plan-template.md`](templates/plan-template.md)
