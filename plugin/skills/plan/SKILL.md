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

- Require `INPUT`. Stop if missing.
- Delegate research and exploration to sub-agents _(if supported)_.
- Stories define scope, not implementation details. Minimum stories to cover requirements.
- Organize into logical phases; detailed specs come later via `andthen:spec` or `andthen:spec-plan`.
- **Headless-first** — continue to completion without pausing for routine clarification. Make reasonable assumptions, document them, and surface unresolved questions in the output.
- Stop only on true contract failures (missing input, incompatible artifacts, or ambiguity so severe no defensible plan can be produced).
- Focus on "what" not "how". Replace vague terms with measurable criteria. Record rationale and trade-offs.


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
   - **`--issue` flag present** (or INPUT refers to a GitHub issue): follow `${CLAUDE_PLUGIN_ROOT}/references/resolve-github-input.md`.
     Compatible types: `plan-bundle` — extract and treat as `INPUT` directory. Redirects: `fis-bundle` → `andthen:exec-spec` / `andthen:spec`; `triage-plan` / `triage-completion` / any `*-review` → stop with matching downstream skill. Untyped: use issue content as requirements input; store issue number for reference. → proceed to Step 1b
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
   - If input is too vague to identify a coherent feature boundary, stop and report the minimum missing contract needed. Mention `andthen:clarify` as the interactive fallback.
   - Initial gap analysis – document what's explicitly stated, assumed/implied, and missing/unclear (functional requirements, user flows, edge cases, success criteria, business context, MVP scope)
   - Proceed to Step 1b (Requirements Synthesis)

**Gate**: Input validated


### 1b. Requirements Synthesis & PRD Creation _(skip if PRD already exists)_

#### Headless Requirements Synthesis

Cover the same areas as `andthen:clarify` Phase 2, but default to synthesis rather than interview: users & personas, core workflows, data model, integrations, constraints, NFRs, and success metrics. Fill ordinary gaps using explicit assumptions grounded in the source material, codebase patterns, adjacent artifacts, and standard product conventions.

When a gap materially affects scope or prioritization and the evidence is weak, choose the most conservative MVP assumption that still allows a coherent plan. Record it in `prd.md` under `Constraints & Assumptions` and in the `Decisions Log` with alternatives considered. Do not pause the run for routine clarification.

If the input is so ambiguous that multiple incompatible plans are equally plausible and none can be justified, stop and report the smallest missing decisions required. Use `andthen:clarify` only as an explicit fallback.

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
- If significant gaps remain, fill only the missing areas using bounded assumptions derived from the existing artifacts, codebase context, and adjacent documents. Do not re-ask questions already answered in the existing artifacts, and do not pause for routine clarification.
- If the artifacts are too ambiguous to support any defensible PRD shape, stop and report the minimum missing decisions required. Mention `andthen:clarify` as the interactive fallback.
- **Extract technical details**: If the draft contains implementation-level content (architecture patterns, technology choices, API details, framework constraints, integration specifics), keep them out of the PRD. The PRD should focus on *what* to build. Note any significant technical constraints in the PRD's `Constraints & Assumptions` section; deep technical research is deferred to `andthen:spec-plan` or `andthen:spec`.
- Structure and generate the PRD following the same template as Step 1b. Preserve decisions, rationale, and specific details from existing artifacts – do not paraphrase or generalize away specifics.
- Apply same Prioritization → PRD Validation steps as Step 1b.

**Gate**: PRD created → continue to Step 2


### 2. Requirements Analysis

> Verify `prd.md` exists in OUTPUT_DIR before proceeding. If only a draft or clarification artifact exists, go back to Step 1c.

Scan codebase structure (use a sub-agent if supported) to identify natural implementation boundaries, feature groupings, and dependency relationships — enough to inform story breakdown. Read the `State` document (see **Project Document Index**; default: `docs/STATE.md`) if it exists – use current phase, active stories, and blockers to inform story priorities. Reference the `Ubiquitous Language` document (see **Project Document Index**) if it exists; use canonical terms in story names and acceptance criteria.

Synthesize into a unified understanding of: all PRD requirements and user stories, MVP scope, success criteria, prioritization (P0/P1/P2), natural implementation boundaries, feature dependencies, and complexity/risk areas.

Do not save `.technical-research.md` here — deep technical research (architecture patterns, framework constraints, file maps, shared decisions) is done by `andthen:spec-plan` or `andthen:spec` downstream, where it directly informs spec creation.

**Gate**: Feature mapping complete


### 3. Story Breakdown

#### Design Space Analysis _(if applicable)_

For features with multiple design dimensions, use design space decomposition (see `plugin/references/design-tree.md`) to inform story structure: independent dimensions -> separate stories, coupled dimensions -> same story, high-uncertainty dimensions -> spike story. If a decomposition was produced upstream (by `clarify` or `trade-off`), reference and build on it. Skip for straightforward designs.

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

Organize stories into logical phases. Common pattern: **Phase 1 – Tracer Bullet** (thin e2e slice proving architecture), **Phase 2 – Feature Slices** (parallel vertical slices), **Phase 3 – Hardening** (edge cases, performance, polish, integration). Adapt phase count and names to the project.

#### Wave Assignment
Assign stories to execution waves within each phase: **W1** = no dependencies, **W2** = depends only on W1, **W3+** = cascading. Stories in the same wave with [P] run in parallel.

#### Goal-Backward Analysis (per story)
For each story, work backward from the user-observable outcome: what must be TRUE when done, what artifacts must exist, how they connect to the system. Derive acceptance criteria from these observable truths.

#### Story Definition

For each story, define:
- **ID**: Sequential identifier (S01, S02, etc.)
- **Name**: Brief descriptive name
- **Status**: Tracking field – initially `Pending` (updated to `Spec Ready` / `In Progress` / `Done` during execution)
- **FIS**: Reference to generated spec – initially `–` (updated to file path when `andthen:spec` creates the FIS). Multiple stories may reference the same FIS path when grouped into a composite specification by `andthen:spec-plan`
- **Scope**: 2-4 sentences – what's included and excluded (no implementation approach – that's for `andthen:spec`)
- **Acceptance criteria**: 3-6 testable outcomes – the first 2-3 should be must-be-TRUE observable truths from goal-backward analysis; remaining items are supplementary verification points
- **Dependencies**: Other story IDs that must complete first
- **Phase**: Which implementation phase
- **Wave**: Execution wave within phase (W1, W2, W3...) – pre-computed during planning
- **Parallel**: [P] if can run parallel with others in same phase
- **Risk**: Low/Medium/High with brief note if Medium+
- Include `Provenance` for carried-forward stories, `Key Scenarios` for behavioral seeds, and `Asset refs` for design references – only when applicable.

**Do not include in stories** (deferred to `andthen:spec`):
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
└── plan.md               # Implementation plan
```

- If from GitHub issue: use `issue-{number}-{feature-name}/` as the output subdirectory name (e.g. `docs/specs/issue-42-user-dashboard/plan.md`). Include issue reference in the PRD and plan document headers.

When complete, print the output's **relative path from the project root**. Do not use absolute paths.

### Publish to GitHub _(if --to-issue)_
If PUBLISH_ISSUE is `true`:
1. Follow `${CLAUDE_PLUGIN_ROOT}/references/github-artifact-roundtrip.md`
   - `artifact_type`: `plan-bundle`
   - Title: `[Plan] {project-name}: Implementation Plan`
   - Primary file: `plan.md`
   - Companion files: `prd.md`
   - Labels: `plan`, `andthen-artifact`
2. Print the issue URL and the local primary path (`plan.md`)


## FOLLOW-UP ACTIONS

After completion, suggest the following next steps. **Recommend starting a clean session** for the context-intensive skills (`spec-plan`, `exec-plan`) — they perform best with a fresh context window.

1. **Start with first story**: Run `andthen:spec` for story S01.
2. **Create wireframes** (if UI work): Run `andthen:wireframes` on the PRD.
3. **Review plan**: Run `andthen:review --doc-only` on `plan.md`.
4. **Batch-generate specs** _(clean session)_: Run `andthen:spec-plan` to pre-create all FIS before execution.
5. **Execute the full plan** _(clean session)_: Run `andthen:exec-plan` to spec and implement all stories.
6. **Initialize project state** (if not already tracking): Create the `State` document via `andthen:init` or manually from `templates/project-state-templates.md`.


---


## Appendix: Templates

**USE THE TEMPLATES**:
- PRD: [`templates/prd-template.md`](templates/prd-template.md)
- Plan: [`templates/plan-template.md`](templates/plan-template.md)
