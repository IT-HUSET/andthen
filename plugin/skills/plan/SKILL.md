---
description: Use when the user wants an implementation plan with FIS specs for every story. Trigger on 'create a plan', 'break this into stories', 'plan this feature', 'spec all stories', 'batch spec this plan'. Produces the full plan bundle (`plan.md` + all FIS + `.technical-research.md`) from an existing `prd.md`, or `plan.md` alone with `--skip-specs`. Requires an existing `prd.md` in the input directory — redirect to `andthen:prd` if missing.
argument-hint: "<path-to-directory-with-prd.md> [--skip-specs] [--stories S01,S03] [--phase N] [--max-parallel N] [--skip-review]"
---

# Create Implementation Plan Bundle


Transform a Product Requirements Document (`prd.md`) into a complete implementation plan bundle: `plan.md` with story breakdown **plus** batch-generated Feature Implementation Specifications (FIS) — one per story — **plus** shared `.technical-research.md`. Runs story breakdown with a consolidation pass, parallel FIS sub-agents, and a cross-cutting review in one flow.

**Invariant**: one story → one FIS. The Story Catalog `FIS` column is a unique-key column; no two stories share a FIS path.

**`prd.md` is a required input** — if the input directory has no `prd.md`, the skill fails fast and redirects to the `andthen:prd` skill. PRD synthesis is not this skill's job.

**Philosophy**: Story breakdown and detailed specs are co-produced. Specs decay quickly when divorced from the story context that motivated them; batching keeps them aligned and lets a cross-cutting review catch inter-story inconsistencies before execution starts.


## VARIABLES

_Specs directory containing `prd.md` (**required**):_
INPUT: $ARGUMENTS

_Output directory (defaults to input directory):_
OUTPUT_DIR: `INPUT` (when `INPUT` is a directory containing `prd.md`), or resolved per the input contract below

### Optional Flags
- `--skip-specs` → SKIP_SPECS: Produce `plan.md` only (cheap planning pass; skip technical research, FIS generation, and cross-cutting review)
- `--stories S01,S03,...` → STORY_FILTER: Only generate FIS for listed story IDs
- `--phase N` → PHASE_FILTER: Only generate FIS for stories in phase N
- `--max-parallel N` → MAX_PARALLEL: Concurrency cap per sub-wave (default 5, max 10)
- `--skip-review` → SKIP_REVIEW: Skip the cross-cutting review step


## INSTRUCTIONS

- Require `INPUT`. Stop if missing.
- Delegate research and exploration to sub-agents _(if supported)_.
- Stories define scope, not implementation details. Minimum stories to cover requirements.
- Organize stories into logical phases.
- **Headless-first** — continue to completion without pausing for routine clarification. Make reasonable assumptions, document them, and surface unresolved questions in `plan.md`.
- Stop only on true contract failures: missing `prd.md` (redirect to the `andthen:prd` skill), incompatible artifacts, or ambiguity so severe no defensible plan can be produced.
- Focus on "what" not "how" at the plan level; detailed implementation decisions live in per-story FIS files.
- **Resume contract**: when re-running on a partially-specced directory, skip stories whose `**FIS**` field already points at an existing file. Re-running only fills gaps.
- Read the `Learnings` document (see **Project Document Index**) before FIS generation, if it exists.


### Orchestrator Role

**You are the orchestrator.** Parse the PRD, break stories down (with a consolidation pass for the 1:1 story↔FIS invariant), write `plan.md`, run technical research, spawn one parallel sub-agent per story to generate FIS files, update `plan.md` after each sub-wave, and run the cross-cutting review. Do not write specs directly, write implementation code, or let your context fill with spec content.


## GOTCHAS
- Agent creates too many small stories – push for fewer, larger vertical slices
- Wave assignments get ignored during execution – explicitly mark dependencies between stories
- Not reading the `State` document (see **Project Document Index**) before planning – misses context about current phase, active blockers, and recent decisions that should inform story priorities
- **Carried-forward stories without PRD coverage** – use the **Provenance** field; a story with no PRD feature and no provenance is a traceability gap
- **Skipping the Consolidation Pass** – two stories with shared implementation surface produce two specs that drift. Merge them at the story level in Step 3 instead
- Spawning specs for stories with unresolved spec-time dependencies before the producing story's spec completes — check the technical research for pre-resolved decisions; if covered, parallelization is safe
- Not updating `plan.md` FIS fields after spec generation — downstream skills check this field to skip already-specced stories
- Over-parallelizing – more than 10 concurrent sub-agents causes I/O contention and degraded spec quality
- Skipping cross-cutting review — individual specs can't detect overlapping scope, inconsistent ADRs, or missing integration seams
- **Technical research becomes stale if plan changes** — re-run technical research before generating new specs after plan edits
- **Status updates get dropped when context is exhausted** — `plan.md` FIS field updates are gates. Update immediately after each sub-wave


## WORKFLOW

### 1. Input Validation & PRD Detection

1. **Parse INPUT** — determine type:
   - **Directory with `prd.md`**: set `OUTPUT_DIR = INPUT`; proceed to Step 2.
   - **Directory without `prd.md`**: stop and redirect to the `andthen:prd` skill. Print the expected chain: `andthen:prd <input> → andthen:plan <same-directory>`.
   - **Any other input** (file, URL, inline): stop and redirect to the `andthen:prd` skill.

2. **Document optional assets** present in the PRD directory (ADRs/Architecture, Design system, Wireframes). Keep references for the plan's document-references header.

**Gate**: `prd.md` exists at `OUTPUT_DIR/prd.md`; optional assets catalogued


### 2. Requirements Analysis

Scan codebase structure (use a sub-agent if supported) to identify natural implementation boundaries, feature groupings, and dependency relationships — enough to inform story breakdown. Read the `State` document (see **Project Document Index**; default: `docs/STATE.md`) if it exists — use current phase, active stories, and blockers to inform story priorities. Reference the `Ubiquitous Language` document (see **Project Document Index**) if it exists; use canonical terms in story names and acceptance criteria.

Synthesize into a unified understanding of: all PRD requirements and user stories, MVP scope, success criteria, prioritization (P0/P1/P2), natural implementation boundaries, feature dependencies, and complexity/risk areas.

> Do not save `.technical-research.md` here — deep technical research is generated in Step 5 (after story breakdown), where it directly informs FIS generation.

**Gate**: Feature mapping complete


### 3. Story Breakdown

#### Design Space Analysis _(if applicable)_

For features with multiple design dimensions, use design space decomposition to inform story structure: independent dimensions → separate stories, coupled dimensions → same story, high-uncertainty dimensions → spike story. If a decomposition was produced upstream (by `clarify` or `trade-off`), reference and build on it. Skip for straightforward designs.

#### Story Guidelines

**Each story should be:**
- **Vertical** — Cuts through all layers (data → logic → API → UI) to produce a demoable/testable end-to-end slice, even if narrow in scope
- **Bounded** — Clear scope, single responsibility
- **Verifiable** — Has acceptance criteria
- **Independent** — Minimal coupling to other stories (after dependencies met)

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
- **Status**: Tracking field — initially `Pending` (updated to `Spec Ready` / `In Progress` / `Done` during execution)
- **FIS**: Reference to generated spec — initially `–` (updated to file path after FIS generation in Step 6). Exactly one FIS per story; FIS paths are unique across the Story Catalog
- **Scope**: 2-4 sentences — what's included and excluded (no implementation approach — that's for the per-story FIS)
- **Acceptance criteria**: 3-6 testable outcomes — the first 2-3 should be must-be-TRUE observable truths from goal-backward analysis; remaining items are supplementary verification points
- **Dependencies**: Other story IDs that must complete first
- **Phase**: Which implementation phase
- **Wave**: Execution wave within phase (W1, W2, W3...) — pre-computed during planning
- **Parallel**: [P] if can run parallel with others in same phase
- **Risk**: Low/Medium/High with brief note if Medium+
- Include `Provenance` for carried-forward stories, `Key Scenarios` for behavioral seeds, and `Asset refs` for design references — only when applicable.

**Do not include in stories** (deferred to the per-story FIS):
- Technical approach, patterns, or library choices
- File paths, line numbers, or code specifics
- Implementation gotchas or constraints with workarounds
- Full technical design or pseudocode

#### Consolidation Pass

Before finalizing the Story Catalog, sweep the draft stories and **merge any set (pair or larger)** where any of these hold:

- **Shared implementation surface** — the stories would touch substantially the same files or modules. Separate FIS would duplicate shared architectural context and drift.
- **Tight dependency chain** — `A → B` (or `A → B → C`) where downstream stories have no independent demo value without the upstream (e.g., "define API endpoint" + "wire endpoint to handler" + "surface endpoint in UI" for the same feature).
- **Trivially small set** — each story in the set would produce a barely-populated FIS (small surface, few acceptance criteria — well below the 3-6 guideline in Story Definition) and they share a primary concern.

Run pairwise, then iterate to a fixed point so a 3-way or larger merge composes naturally from successive pair-merges. Merge by union: combine acceptance criteria, reconcile scope into a single coherent vertical slice, renumber if needed. The merged story is still one demoable outcome, just broader. If a merged story becomes too large for a single FIS, the `andthen:spec` skill's oversize pivot handles that during generation — do not pre-split here.

> **Why this matters**: the plan↔FIS join is a single-column contract (the `FIS` field). Keeping it 1:1 means downstream skills (`exec-plan`, `exec-spec`, `ops`) never need to reason about shared or composite specs, and plan.md is unambiguous at a glance. Two stories wanting to share a spec is a signal they were one story.

**Gate**: All stories defined; no two stories intended to share a FIS path


### 4. Create Plan Document

Generate `plan.md` using the template at [`templates/plan-template.md`](templates/plan-template.md).

This template defines the document's operational contract. Preserve the heading names, Story Catalog columns, and standard story metadata labels because downstream skills parse them directly. Adapt the phase names, story count, and example content to the project.

**Document references header**: Include a blockquote header at the top linking to all key reference documents discovered during Input Validation (PRD, ADRs, design system, wireframes, etc.). Use relative paths. Omit entries where no document exists — only include actual references.

Keep these invariants from the template:
- Story Catalog columns remain `ID | Name | Phase | Wave | Dependencies | Parallel | Risk | Status | FIS`
- Each story defines `**Status**`, `**FIS**`, `**Phase**`, `**Wave**`, `**Dependencies**`, `**Parallel**`, `**Risk**`, `**Scope**`, `**Acceptance Criteria**`, and `**Asset refs**`
- `**Key Scenarios**` stays optional and seeds later FIS scenario generation
- `**Provenance**` is required for stories with no direct PRD feature coverage
- Every row's `**FIS**` path is unique across the catalog (1:1 story↔FIS invariant)

#### Self-Check (plan.md)
- [ ] All PRD features have corresponding stories
- [ ] Stories without PRD feature coverage have a **Provenance** annotation
- [ ] Stories have clear boundaries (no overlap)
- [ ] Dependencies accurately mapped
- [ ] Parallel markers correctly applied
- [ ] Wave assignments are pre-computed and consistent with dependencies
- [ ] Risk areas identified (Risk column and Risk Summary populated)
- [ ] No missing functionality (cross-cutting concerns like auth, logging, error pages covered)
- [ ] Not over-granular (combined where sensible)

Optional: Invoke the `andthen:review --mode doc` skill on `plan.md` before continuing.

#### Initialize Project State (if the `State` document exists; see **Project Document Index**)
If the `State` document exists, update it to reflect the new plan via the `andthen:ops` skill:
- `update-state phase "Phase 1: {first_phase_name}"`
- `update-state status "On Track"`
- `update-state note "Plan created: {plan_name} ({N} stories, {M} phases)"`

If the `State` document does not exist, do not create it — suggest it in follow-up actions instead.

**Gate**: `plan.md` saved and validated

> **If `--skip-specs` is set**: stop here and print the path to `plan.md`. Do not run Steps 5–7.


### 5. Technical Research (One-Time Upfront Discovery)

Before spawning any spec sub-agents, do **all discovery and research work once** via up to 3 parallel sub-agents. This eliminates redundant codebase scanning, guideline reading, and architecture analysis each spec sub-agent would otherwise do independently.

**Sub-agent 1: Project Context** — Read CLAUDE.md guidelines; scan codebase structure (`tree -d`, `git ls-files | head -250`); identify conventions (naming, file organization, test patterns, abstractions); read the `Learnings` document (see **Project Document Index**) if it exists; identify tech stack and key framework versions. Output: dense summary of tech stack, conventions, key patterns, relevant guidelines, learnings.

**Sub-agent 2: Story-Scoped File Map** — For each story: search for related files/modules, identify existing patterns to follow (file:line references), flag files multiple stories will touch. Output: per-story file list with relevance notes plus a shared-files section.

**Sub-agent 3: Shared Architectural Decisions** — For each pair of dependent stories: identify the interface/contract between them (API shape, data types, naming, error handling); document the shared decision so both specs can reference it. Also identify: naming conventions that must be consistent, shared abstractions multiple stories will create/consume, API patterns that must be uniform. Extract **binding PRD constraints** from `OUTPUT_DIR/prd.md`: requirements that specify explicit capabilities (e.g., "must support remote hosts"), protocol details, security requirements, or user-facing behaviors. These constraints must flow unchanged into FIS success criteria — they are not subject to architectural trade-offs or scope narrowing by individual stories. Output: numbered list of shared decisions with rationale, specific enough to reference in FIS success criteria; plus a separate "Binding PRD Constraints" section listing constraints with source feature IDs.

External research (API docs, library lookups) is deferred to individual spec sub-agents that need it — most stories don't reference external APIs, and the ones that do can delegate to the `andthen:documentation-lookup` agent from within their sub-agent prompt.

**Consolidation**: After all sub-agents complete, save to `{OUTPUT_DIR}/.technical-research.md`:

```markdown
# Technical Research: {Plan Name}
Generated: {date}

> **Verification note**: This research is a point-in-time snapshot. File:line references, API behaviors, and library details must be verified against the current codebase during spec execution. Treat findings as leads to investigate, not facts to trust.

## Project Context
{Sub-agent 1 output}

## Story-Scoped File Map
{Sub-agent 2 output}

## Shared Architectural Decisions
{Sub-agent 3 output}
```

If a `.technical-research.md` already exists (e.g. from a prior run), merge new sections into it rather than overwriting.

**Gate**: Technical research saved to `{OUTPUT_DIR}/.technical-research.md`, covers all stories in scope


### 6. Parallel FIS Creation

Apply filters (`STORY_FILTER`, `PHASE_FILTER`); skip stories whose `**FIS**` field already points at a file that exists on disk. Remaining in-scope stories each get one sub-agent producing one FIS.

#### Wave Ordering

The technical research pre-resolves most inter-story architectural decisions. Default: all in-scope stories launch in parallel (up to `MAX_PARALLEL`, default 5, max 10). Exception: hold back a story if its spec depends on a decision the technical research could not pre-resolve — wait for the producing story's spec to complete first. Fallback: if the technical research is incomplete or unavailable, use strict wave ordering (W1 complete → W2). Batch into sub-waves if story count exceeds `MAX_PARALLEL`.

#### Sub-Agent Prompts

Use a strong reasoning model (`model: "opus"`, `gpt-5.4`, or similar). These sub-agents do **not** invoke `/andthen:spec`; they are ad-hoc sub-agents with FIS-authoring instructions inlined below, because the batch flow has already pre-computed the shared technical research the per-spec skill would otherwise redo.

**Shared references** (provided to every sub-agent):
- FIS template: `templates/fis-template.md`
- Authoring guidelines: `references/fis-authoring-guidelines.md`
- Technical research: `{OUTPUT_DIR}/.technical-research.md`

**Shared authoring rules** — read the technical research for shared decisions and file maps; **reference** it from the FIS rather than inlining its content (enforce the Technical Research Separation rule from the guidelines); honour every entry in the "Binding PRD Constraints" section — each applicable constraint flows into FIS success criteria unchanged; delegate external API/library lookups the technical research does not cover to the `andthen:documentation-lookup` agent; always run Plan-Spec Alignment Check, Reverse Coverage Check (**plan-level sources only** — sub-agents do not have `prd.md` in context; PRD-level reverse coverage is handled in Step 7), and Self-Check from the guidelines; report back success/failure, FIS path, confidence score, and any `PHANTOM_SCOPE` findings from Reverse Coverage.

**Per-story inputs** (one sub-agent per story):
- Story ID, name, scope, acceptance criteria, Key Scenarios (if present), dependencies
- Output path: `{OUTPUT_DIR}/s{NN}-{story-name}.md` (e.g. `s01-user-auth.md`)

> **Size signal**: if a draft FIS would exceed the oversize thresholds in `references/fis-authoring-guidelines.md`, the story was too broad — the sub-agent reports back and the orchestrator revisits Step 3 for that story rather than pre-splitting here.

#### Wait, Collect, and Update Plan

Wait for all sub-agents in the current sub-wave to complete. Log any failures (continue with remaining stories — don't block the wave). Immediately after each sub-wave:

**Gate** — update `plan.md` for each successfully generated FIS:
- Set `**FIS**` field to the generated spec path (unique per row — enforces the 1:1 invariant)
- Set `**Status**` field to `Spec Ready` (if not already `In Progress` or `Done`)

#### Spec Flow Example

```
8-story plan (after Step 3 Consolidation Pass) → 8 FIS files

Step 6 (MAX_PARALLEL=4):
  Sub-wave 1: spec-S01, spec-S02, spec-S03, spec-S04 (parallel)
  Sub-wave 2: spec-S05, spec-S06, spec-S07, spec-S08 (parallel)
  → Update plan.md FIS fields after each sub-wave
```

**Gate**: All specs complete, all `plan.md` FIS fields updated (each path unique)


### 7. Cross-Cutting Review & Fixes

> **Skip this step if `--skip-review` flag is set.**

Delegate to a single opus sub-agent with all generated FIS paths. Provide: plan path, list of all FIS paths. The sub-agent should read ALL FIS files, `plan.md`, and `prd.md`, then check for:

1. **Overlapping scope** – multiple stories modifying the same files or creating the same abstractions
2. **Inconsistent architectural decisions** – contradictory ADR choices across stories
3. **Missing integration seams** – Story B needs output Story A's spec doesn't produce
4. **Dependency gaps** – cross-story dependencies not reflected in FIS task ordering
5. **Inconsistent naming/patterns** – different conventions for similar operations or shared concerns
6. **Duplicate work** – same utility, component, or abstraction independently created in multiple stories
7. **Plan-vs-FIS alignment** – every plan acceptance criterion must be covered by FIS success criteria; flag any criterion silently narrowed without a scope note
8. **Intra-story scope contradictions** – items in "What We're NOT Doing" that block a success criterion
9. **Scenario gaps** – plan Key Scenario seeds not mapped to FIS scenarios; cross-story scenario dependencies (Story B's scenario assumes behavior from Story A that isn't covered)
10. **PRD-FIS requirements traceability** – verify that every PRD feature requirement's acceptance criteria has at least one corresponding FIS scenario. This catches requirements that were narrowed during plan decomposition or lost during spec generation. Example: a PRD requiring "remote host support" should not produce a FIS that says "always loopback"
11. **Scenario chain connectivity** – for each multi-step flow in the PRD (`User Flows` preferred; fall back to sequenced User Stories), verify FIS scenarios chain cleanly: each leg's **Then** outputs must satisfy the next leg's **Given**. Distinct from #10 (per-criterion coverage) — #11 catches orphan outputs and unsourced inputs between adjacent scenarios. List the scenarios in flow order and name the handoff artifact (state, record, event, UI element) between each pair; flag any gap. Example: flow "upload file → see result" — Story A's scenario ends at "job enqueued", Story B's begins at "job completes", but no scenario produces the user-visible result state.

Output per finding: severity (CRITICAL/HIGH/MEDIUM/LOW), stories affected, issue description, recommendation, FIS sections to update. Include a summary with total findings by severity, overall readiness (READY/NEEDS FIXES/BLOCKED), and list of FIS files needing updates.

#### Fix Issues

If the review found CRITICAL or HIGH severity issues, apply fixes to resolve inter-story inconsistencies: overlapping scope → clarify file ownership with cross-references; inconsistent ADRs → align on the most prevalent or architecturally sound choice; missing seams → add missing outputs to the producing story; naming inconsistencies → standardize on the most prevalent pattern; duplicate work → consolidate into the earliest story.

**Broken scenario chains (#11)** — pick one:
- Add the missing scenario to the FIS whose story naturally owns that leg. Don't stretch an unrelated FIS.
- If no story owns it, add a new story: re-enter Step 3 (Phase/Wave/Dependencies/Risk), update the Story Catalog, re-run technical research if files fall outside the existing map, then Step 6 for that story before execution.
- If the gap is a missing upstream decision, treat as a contract failure (per INSTRUCTIONS): pause for user input, surface the minimum missing decision, and don't invent the answer.

**Phantom-scope findings** (from sub-agent `PHANTOM_SCOPE` return summaries): sub-agents only saw plan-level sources, so first re-check each finding against `prd.md` — criteria that trace to a PRD outcome are **not** phantom scope (suppress). For confirmed phantom scope: remove the unsourced Success Criterion, or amend plan/PRD to justify it. Treat confirmed phantom scope as MEDIUM severity by default; upgrade to HIGH when it drives significant implementation work or introduces new dependencies.

After fixes, re-read changed FIS files and re-walk affected PRD flows.

**Gate**: Cross-cutting review complete; CRITICAL/HIGH issues and confirmed phantom scope resolved; FIS files updated


## OUTPUT

```
OUTPUT_DIR/
├── prd.md                 # Product Requirements Document (carried in, not modified)
├── plan.md                # Implementation plan with story catalog
├── .technical-research.md # Shared technical research (hidden companion)
└── s0N-*.md               # FIS files — one per story, one story per FIS
```

- With `--skip-specs`: only `plan.md` is produced (plus unchanged `prd.md`).

When complete, print the output's **relative path from the project root**.


## COMPLETION

Print a summary:
- **plan.md**: path
- **FIS files created**: count (one per in-scope story)
- **Stories specced**: count and list with FIS paths
- **Stories skipped**: (already had FIS)
- **Stories failed**: (if any, with error details)
- **Cross-cutting review**: findings count by severity, readiness assessment
- **Fixes applied**: list of FIS files modified
- **Readiness**: overall assessment for execution


## FOLLOW-UP ACTIONS

After completion, suggest the following next steps. **Recommend starting a clean session** for the context-intensive downstream skill.

1. **Execute the plan** _(clean session)_: Invoke the `andthen:exec-plan` skill — the bundle is fully specced.
2. **Execute story by story**: Invoke the `andthen:exec-spec` skill per story for more control.
3. **Review the bundle**: Invoke the `andthen:review --mode doc` skill on `plan.md` or `--mode gap` once implementation begins.
4. **Initialize project state** (if not already tracking): Create the `State` document via the `andthen:init` skill.


## FAILURE HANDLING

- **Individual spec failure** → log and continue. Report in summary.
- **>50% of specs fail** → pause this run and return a failure summary with the blocking details.
- **Cross-cutting review sub-agent fails** → warn user that cross-cutting review was skipped; specs are usable but unvalidated for inter-story consistency.
- **Fix step fails** → report unfixed issues to user. Specs are usable but may have inter-story inconsistencies that surface during execution.


---


## Appendix: Templates

**USE THE TEMPLATE**:
- Plan: [`templates/plan-template.md`](templates/plan-template.md)
- FIS: `templates/fis-template.md`
- PRD template (used by the `andthen:prd` skill upstream): `templates/prd-template.md`
