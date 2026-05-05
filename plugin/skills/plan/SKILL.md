---
description: Use when the user wants an implementation plan with FIS specs for every story. Trigger on 'create a plan', 'break this into stories', 'plan this feature', 'spec all stories', 'batch spec this plan'. Produces the full plan bundle (`plan.md` + all FIS) from an existing `prd.md`. Requires an existing `prd.md` in the input directory — redirect to `andthen:prd` if missing.
argument-hint: "[--max-parallel N] [--skip-review] [--issue <number>] [--to-issue] [--create-story-issues] [--auto|--headless] <path-to-directory-with-prd.md>"
---

# Create Implementation Plan Bundle


Transform a Product Requirements Document (`prd.md`) into a complete implementation plan bundle: `plan.md` with story breakdown **plus** batch-generated Feature Implementation Specifications (FIS) — one per story. Runs story breakdown with a consolidation pass, parallel FIS sub-agents, and a cross-cutting review in one flow.

**Invariant**: one story → one FIS. The Story Catalog `FIS` column is a unique-key column; no two stories share a FIS path.

**`prd.md` is a required input** — if the input directory has no `prd.md`, the skill fails fast and redirects to the `andthen:prd` skill. PRD synthesis is not this skill's job.

**Philosophy**: Story breakdown and detailed specs are co-produced. Specs decay quickly when divorced from the story context that motivated them; batching keeps them aligned and lets a cross-cutting review catch inter-story inconsistencies before execution starts.


## VARIABLES

_Specs directory containing `prd.md` (**required**):_
INPUT: $ARGUMENTS (first reject retired flag tokens like `--skip-specs`, `--stories`, or `--phase`; then strip active flag tokens like `--max-parallel`, `--skip-review`, `--issue`, `--to-issue`, `--create-story-issues`, `--auto`, or `--headless` before interpreting the remainder as the specs-directory path)

_Output directory (defaults to input directory):_
OUTPUT_DIR: `INPUT` (when `INPUT` is a directory containing `prd.md`), or resolved per the input contract below

### Optional Flags
- `--max-parallel N` → MAX_PARALLEL: Concurrency cap per sub-wave (default 5, max 10)
- `--skip-review` → SKIP_REVIEW: Skip the cross-cutting review step
- `--issue <number>` → ISSUE_INPUT: Use a GitHub PRD issue as input (`gh issue view <N>`); the issue body is the PRD source. In local-output mode, materialize that source verbatim as `OUTPUT_DIR/prd.md` so story `Source refs` remain resolvable during FIS generation. `OUTPUT_DIR` resolves to `<base-output-dir>/issue-<N>-<feature-slug>/` (mirrors `clarify` and `prd` patterns). Composes with local bundle output and `--to-issue`.
- `--to-issue` → PUBLISH_PLAN_ISSUE: Output the plan as a single GitHub issue per the **single-issue shape** in [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md). **Writes nothing to disk** — skip Steps 4 (plan.md write), 5 (FIS generation), and 6 (cross-cutting review). Default GitHub-output mode produces ONE plan issue.
- `--create-story-issues` → CREATE_STORY_ISSUES: Switch `--to-issue` from single-issue to **granular shape** per [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md): one parent plan issue PLUS N story issues with `Refs #<prd-N>` and `Part of #<plan-N>` links. **Requires `--to-issue`** — reject up-front if absent (`BLOCKED: --create-story-issues requires --to-issue` in `AUTO_MODE`; print error and stop in default mode) before any `gh` call.
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Require `INPUT`. Stop if missing.
- Delegate research and exploration to sub-agents to protect the main context window.
- Stories define scope, not implementation details. Minimum stories to cover requirements.
- Organize stories into logical phases.
- **Automation rules** (headless-first, `--auto` / `--headless` strict mode, `--auto` propagation): see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). Plan-specific `BLOCKED:` triggers: missing `prd.md` (redirect to the `andthen:prd` skill), incompatible artifacts, ambiguity so severe no defensible plan can be produced.
- Focus on "what" not "how" at the plan level; detailed implementation decisions live in per-story FIS files.
- **Resume contract**: when re-running on a partially-specced directory, skip stories whose Story Catalog `FIS` cell already points at an existing file. Re-running only fills gaps.
- Read the `Learnings` document (see **Project Document Index**) before FIS generation, if it exists.


### Orchestrator Role

Do not write FIS content yourself — delegate to per-story sub-agents in Step 5.


## GOTCHAS
- **Carried-forward stories without PRD coverage** – use the **Provenance** field; a story with no PRD feature and no provenance is a traceability gap
- **Skipping the Consolidation Pass** – two stories with shared implementation surface produce two specs that drift. Merge them at the story level in Step 3 instead
- **Status updates get dropped when context is exhausted** — Story Catalog `FIS` and `Status` updates are gates. Update immediately after each sub-wave
- **Prose in `Dependencies` cells breaks schedulers** — the Story Catalog `Dependencies` column is machine-readable. Use only comma-separated story IDs like `S01, S04`, or `-` when none. Do not write milestone prose such as `Blocks A-G complete`; express broad sequencing through phase/wave placement, Dependency Graph notes, or concrete story IDs.


## WORKFLOW

### 1. Input Validation & PRD Detection

0. **Flag-combination guard** — enforce up-front, before any I/O:
   - `--skip-specs`: reject. Print `Error: --skip-specs was removed. Run andthen:plan on the directory to create or resume the full local bundle, or use --to-issue for GitHub issue output without local FIS files.` and stop. `AUTO_MODE`: emit `BLOCKED: --skip-specs was removed; rerun andthen:plan to create/resume the full bundle or use --to-issue` and exit.
   - `--stories` or `--phase`: reject. Print `Error: --stories and --phase were removed. Run andthen:plan on the directory to fill all missing FIS files, or use andthen:spec story <id> of <plan.md> for a one-off story spec.` and stop. `AUTO_MODE`: emit `BLOCKED: --stories/--phase were removed; rerun andthen:plan to fill all missing FIS files` and exit.
   - `--create-story-issues` without `--to-issue`: reject. Print `Error: --create-story-issues requires --to-issue (granular GitHub mode is meaningless without GitHub output).` and stop. `AUTO_MODE`: emit `BLOCKED: --create-story-issues requires --to-issue` and exit. No `gh` call has occurred yet.

1. **Parse INPUT** — determine type:
   - **`--issue <N>` flag (or INPUT is a GitHub issue URL)**: fetch the body with `gh issue view <N>` and treat it as the PRD source. Resolve `OUTPUT_DIR` per the dispatch table below; in local-output modes use `<base-output-dir>/issue-<N>-<feature-slug>/` as the subdirectory (mirrors `clarify` and `prd`) and write the fetched issue body verbatim to `OUTPUT_DIR/prd.md` before Step 2 so later FIS sub-agents can resolve `Source refs`. The slug derives from the issue title (lowercase, alphanumerics + hyphen). Store the issue number for the plan's document-references header. On `gh` failure: surface verbatim and stop (`BLOCKED: gh authentication required` / `BLOCKED: PR/issue <N> not found` in `AUTO_MODE`). Proceed to Step 2.
   - **Directory with `prd.md`**: set `OUTPUT_DIR = INPUT`; proceed to Step 2.
   - **Directory without `prd.md`**: stop and redirect to the `andthen:prd` skill. Print the expected chain: `andthen:prd <input> → andthen:plan <same-directory>`.
   - **Any other input** (file, URL, inline): stop and redirect to the `andthen:prd` skill.

2. **Document optional assets** present in the PRD directory (ADRs/Architecture, Design system, Wireframes). Keep references for the plan's document-references header. In `--issue` mode this is best-effort — the issue body is the only authoritative source.

**Gate**: PRD source resolved (local `prd.md` or fetched issue body); optional assets catalogued


### 2. Requirements Analysis

**Read the resolved PRD source directly here** (local `prd.md`, or fetched issue body materialized as `OUTPUT_DIR/prd.md` in local-output issue mode). This is the single PRD read for plan generation — Step 5 sub-agents receive relevant spans as context (do not re-read), and Step 6's cross-cutting review reads the PRD fresh in its own sub-agent context.

Run a quick `tree -d` + `git ls-files | head -250` codebase scan inline (no sub-agent) to identify natural implementation boundaries — enough to inform story breakdown, not deep research. Read the `State` document (see **Project Document Index**; default: `docs/STATE.md`) if it exists — use current phase, active stories, and blockers to inform story priorities. Reference the `Ubiquitous Language` document (see **Project Document Index**) if it exists; use canonical terms in story names, scope, and source refs.

Synthesize into a unified understanding of: all PRD requirements and user stories, MVP scope, success criteria, prioritization (P0/P1/P2), natural implementation boundaries, feature dependencies, and complexity/risk areas. As you read the PRD, note any "must support X" / "must not Y" language that should land in the optional `## Binding Constraints` section in Step 4.

**Resume shortcut**: in local-output mode, if `OUTPUT_DIR/plan.md` already exists, do not regenerate the story breakdown or overwrite `plan.md`. Read the existing Story Catalog, validate the dependency cells per the Story Definition rule below, then jump to Step 5 to fill missing FIS files. This is the only supported partial-plan state: interrupted or legacy runs are completed by re-running `andthen:plan`, not by producing a plan-only artifact on purpose.

**Gate**: Feature mapping complete; PRD read once and held in working notes, or existing plan loaded for FIS-fill resume


### 3. Story Breakdown

#### Design Space Analysis _(if applicable)_

For features with multiple design dimensions, use design space decomposition to inform story structure: independent dimensions → separate stories, coupled dimensions → same story, high-uncertainty dimensions → spike story. If a decomposition was produced upstream (by `clarify` or `trade-off`), reference and build on it. Skip for straightforward designs.

#### Story Guidelines

Each story should be **vertical** (cuts through all layers to a demoable slice), **bounded** (clear scope, single responsibility), **verifiable** (has enough source refs and scope to generate FIS success criteria), and **independent** (minimal coupling after dependencies met). Use minimum stories to cover requirements; no overlap; no over-granularity.

#### Implementation Phases and Wave Assignment

Organize stories into logical phases. Common pattern: **Phase 1 – Tracer Bullet** (thin e2e slice), **Phase 2 – Feature Slices** (parallel vertical slices), **Phase 3 – Hardening** (edge cases, polish, integration). Adapt to the project. Within each phase, assign waves: **W1** = no dependencies, **W2** = depends only on W1, **W3+** = cascading; stories in the same wave with [P] run in parallel.

**Goal-Backward Analysis**: for each story, work backward from the user-observable outcome — what must be TRUE when done, what artifacts must exist, how they connect to the system. Use this to define the story boundary and FIS seed context; detailed success criteria and scenarios belong in the generated FIS, not in `plan.md`.

#### Story Definition

For each story, define the Story Catalog row:
- **ID**: Sequential identifier (S01, S02, etc.)
- **Name**: Brief descriptive name
- **Status**: Story Catalog tracking value — initially `Pending` (updated to `Spec Ready` / `Done` during execution). Do not repeat status in the story section.
- **FIS**: Story Catalog reference to generated spec — initially `–` (updated to file path after FIS generation in Step 5). Exactly one FIS per story; FIS paths are unique across the Story Catalog. Do not repeat the FIS path in the story section.
- **Dependencies**: Other story IDs that must complete first. The field is parseable scheduler input: use only `-` or comma-separated existing story IDs (`S01`, `S01, S04`). Do not put prose, phase names, "all previous blocks", or milestone gates here; broad sequencing belongs in phase/wave assignment or the `## Dependency Graph` narrative.
- **Phase**: Which implementation phase
- **Wave**: Execution wave within phase (W1, W2, W3...) — pre-computed during planning
- **Parallel**: [P] if can run parallel with others in same phase
- **Risk**: Low/Medium/High with brief note if Medium+

Then write a compact Phase Breakdown story brief:
- **Scope**: 1-2 sentences covering the intended outcome, what's included, and what's excluded. No implementation approach.
- **Source refs**: PRD feature IDs and anchors that the FIS author must read for detailed behavior, e.g. `FR-2, FR-5 — prd.md#export-rules`. Required for PRD-backed stories; omit only when `Provenance` explains why no PRD source exists.
- **Provenance**: required only for carried-forward stories or stories with no direct PRD feature coverage.
- **Asset refs**: optional wireframes, ADRs, design-system references, or other upstream artifacts the FIS author needs.
- **Notes**: optional load-bearing planning notes that do not belong in the Story Catalog or Dependency Graph.

**Do not include in plan story briefs** (deferred to per-story FIS): success criteria, full scenarios, technical approach, patterns, library choices, file paths, implementation gotchas, or full technical design.

#### Consolidation Pass

Before finalizing the Story Catalog, sweep the draft stories and **merge any set (pair or larger)** where any of these hold:

- **Shared implementation surface** — the stories would touch substantially the same files or modules. Separate FIS would duplicate shared architectural context and drift.
- **Tight dependency chain** — `A → B` (or `A → B → C`) where downstream stories have no independent demo value without the upstream (e.g., "define API endpoint" + "wire endpoint to handler" + "surface endpoint in UI" for the same feature).
- **Trivially small set** — each story in the set would produce a barely-populated FIS (small surface, little independent verification value) and they share a primary concern.

Run pairwise, then iterate to a fixed point so a 3-way or larger merge composes naturally from successive pair-merges. Merge by union: combine intended outcomes, reconcile scope into a single coherent vertical slice, renumber if needed. The merged story is still one demoable outcome, just broader. If a merged story turns out too large for a single FIS, Step 5's per-story sub-agent reports that back via the size signal and the orchestrator revisits Step 3 for that story — do not pre-split here.

> **Why this matters**: the plan↔FIS join is a single-column contract (the Story Catalog `FIS` column). Keeping it 1:1 means downstream skills (`exec-plan`, `exec-spec`, `ops`) never need to reason about shared or composite specs, and plan.md is unambiguous at a glance. Two stories wanting to share a spec is a signal they were one story.

**Gate**: All stories defined; no two stories intended to share a FIS path


### 4. Create Plan Document

Generate `plan.md` using the template at [`templates/plan-template.md`](templates/plan-template.md).

This template defines the document's operational contract. Preserve the heading names, Story Catalog columns, and standard story brief labels because downstream skills parse them directly. Adapt the phase names, story count, and example content to the project.

**Document references header**: Emit `**PRD**` always (it's the load-bearing input). Emit a generic `**References**` blockquote with one bullet per upstream artifact discovered during Input Validation (ADRs, design system, wireframes, glossary, ad-hoc research, etc.) — relative paths, one-line purpose each. Omit the `References` section entirely when no upstream artifacts exist.

**Shared Decisions and Binding Constraints (inline extraction, no sub-agent)**: After story breakdown, walk the working-notes PRD synthesis from Step 2:
- **`## Shared Decisions`** — emit when stories have inter-dependencies that imply a shared interface, naming convention, or abstraction multiple stories will create or consume. 3-6 bullets, each naming the producing and consuming stories. Omit the section when none apply.
- **`## Binding Constraints`** — emit when the PRD contains "must support X" / "must not Y" language at risk of being silently dropped during decomposition. Each entry: verbatim PRD span + heading anchor (`prd.md#<heading-slug>`) + source feature ID. These flow unchanged into FIS Required Context blocks during Step 5. Omit the section when none apply.

Both sections are **optional** — extracted inline from PRD content already loaded in Step 2, no sub-agent fan-out.

Keep these invariants from the template:
- Story Catalog columns remain `ID | Name | Phase | Wave | Dependencies | Parallel | Risk | Status | FIS`
- Story Catalog is the only place for `Status`, `FIS`, `Phase`, `Wave`, `Dependencies`, `Parallel`, and `Risk`
- Each story section defines `**Scope**`, PRD-backed stories define `**Source refs**`, and optional labels are `**Provenance**`, `**Asset refs**`, and `**Notes**`
- `**Source refs**` names the PRD feature IDs and anchors that carry detailed behavior; this is the lightweight bridge from slim plan to complete FIS
- `**Provenance**` is required for stories with no direct PRD feature coverage
- Every row's `FIS` path is unique across the catalog (1:1 story↔FIS invariant)
- Every `Dependencies` cell is `-` or comma-separated story IDs that exist in the same Story Catalog. Prose dependencies are invalid even when they are understandable to a human.

#### Self-Check (plan.md)
- [ ] All PRD features have corresponding stories
- [ ] PRD-backed stories have **Source refs**; stories without PRD feature coverage have a **Provenance** annotation
- [ ] Stories have clear boundaries (no overlap)
- [ ] Dependencies accurately mapped; every dependency token matches an existing `SNN` story ID
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

> **If `--to-issue` is set**: do not write `plan.md` to disk in this step. Build the same logical plan content (story breakdown, catalog, metadata, optional Shared Decisions / Binding Constraints) in memory, then load `references/to-issue-mode.md` for the GitHub-output workflow (plan-issue body assembly per `plan-issue-shape.md`, single-issue or granular `gh issue create` flow, and the no-local-writes gate). Steps 5 (FIS generation) and 6 (cross-cutting review) are skipped in this mode.


### 5. Parallel FIS Creation

Skip stories whose Story Catalog `FIS` cell already points at a file that exists on disk. Every remaining story gets one sub-agent producing one FIS.

#### Wave Ordering

Plan-level `## Shared Decisions` (when present) pre-resolves inter-story architectural decisions. Default: all in-scope stories launch in parallel (up to `MAX_PARALLEL`, default 5, max 10). Exception: hold back a story if its spec depends on a decision not captured in `## Shared Decisions` — wait for the producing story's spec to complete first. Fallback: if no `## Shared Decisions` section exists, use strict wave ordering (W1 complete → W2). Batch into sub-waves if story count exceeds `MAX_PARALLEL`.

#### Sub-Agent Prompts

For each in-scope story, spawn a sub-agent that runs `/andthen:spec --auto story {story_id} of {OUTPUT_DIR}/plan.md`. The `andthen:spec` skill handles the full authoring flow per its guidelines at `${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md`.

**Additional context for each sub-agent** (pass alongside the skill invocation):
- Each sub-agent reads `plan.md` (which carries the optional `## Shared Decisions` and `## Binding Constraints` sections inline) plus only the PRD anchors named in that story's `**Source refs**`. Do not re-read the whole PRD. Source refs exist so the slim plan can stay compact while the FIS still receives detailed behavior.
- Binding constraints: every applicable entry from `plan.md`'s `## Binding Constraints` section (when present) flows into FIS Success Criteria unchanged. Do not narrow the binding constraint set.
- Run Plan-Spec Alignment Check, Self-Check, and Reverse Coverage Check from the guidelines. Reverse Coverage Check runs against plan-level sources plus `plan.md`'s `## Binding Constraints`; PRD-level reverse coverage beyond those constraints is handled by the orchestrator in Step 6.
- Report back: success/failure, FIS path, confidence score, any `PHANTOM_SCOPE` findings from Reverse Coverage, and any `OVERSIZE:` line emitted by the spec skill (verbatim, including line/task counts and recommendation).

> **Size signal**: if a sub-agent's completion summary contains an `OVERSIZE:` line (see `${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md` Key Generation Guidelines #6 for the threshold), the story was too broad — the orchestrator revisits Step 3 to decompose that story before regenerating its FIS. The oversized FIS that the spec sub-agent saved is discarded by the regeneration pass, so it does not need to be deleted up front.

#### Wait, Collect, and Update Plan

Wait for all sub-agents in the current sub-wave to complete. Log any failures (continue with remaining stories — don't block the wave). Immediately after each sub-wave:

**Gate** — update `plan.md` for each successfully generated FIS:
- Set the Story Catalog `FIS` cell to the generated spec path (unique per row — enforces the 1:1 invariant)
- Set the Story Catalog `Status` cell to `Spec Ready` (if not already `Done`)

#### Spec Flow Example

```
8-story plan (after Step 3 Consolidation Pass) → 8 FIS files

Step 5 (MAX_PARALLEL=4):
  Sub-wave 1: spec-S01, spec-S02, spec-S03, spec-S04 (parallel)
  Sub-wave 2: spec-S05, spec-S06, spec-S07, spec-S08 (parallel)
  → Update Story Catalog FIS cells after each sub-wave
```

**Gate**: All specs complete, all Story Catalog `FIS` cells updated (each path unique)


### 6. Cross-Cutting Review & Fixes

> **Skip this step if `--skip-review` flag is set.**

Delegate to a single opus sub-agent with all generated FIS paths. Provide: plan path, list of all FIS paths. This is the **second (and only other) full PRD read** in the plan flow — the sub-agent reads `prd.md` fresh in its own context, plus all FIS files and `plan.md`, then checks for:

1. **Overlapping scope** – multiple stories modifying the same files or abstractions
2. **Inconsistent architectural decisions** – contradictory ADR choices across stories
3. **Missing integration seams** – Story B needs output Story A's spec doesn't produce
4. **Dependency gaps** – cross-story dependencies not reflected in FIS task ordering
5. **Inconsistent naming/patterns** – different conventions for similar operations or shared concerns
6. **Duplicate work** – same utility, component, or abstraction independently created in multiple stories
7. **Plan-vs-FIS alignment** – every plan story scope and Binding Constraint must be covered by FIS success criteria and scenarios; flag any scope silently narrowed without a scope note
8. **Intra-story scope contradictions** – items in "What We're NOT Doing" that block a success criterion
9. **Scenario gaps** – legacy plan Key Scenario seeds not mapped to FIS scenarios; cross-story scenario dependencies not covered
10. **PRD-FIS requirements traceability** – verify that every PRD feature requirement's acceptance criteria has at least one corresponding FIS scenario. This catches requirements that were narrowed during plan decomposition or lost during spec generation. Example: a PRD requiring "remote host support" should not produce a FIS that says "always loopback"
11. **Scenario chain connectivity** – for each multi-step flow in the PRD (`User Flows` preferred; fall back to sequenced User Stories), verify FIS scenarios chain cleanly: each leg's **Then** outputs must satisfy the next leg's **Given**. Distinct from #10 (per-criterion coverage) — #11 catches orphan outputs and unsourced inputs between adjacent scenarios. List the scenarios in flow order and name the handoff artifact (state, record, event, UI element) between each pair; flag any gap. Example: flow "upload file → see result" — Story A's scenario ends at "job enqueued", Story B's begins at "job completes", but no scenario produces the user-visible result state.

Output per finding: severity (CRITICAL/HIGH/MEDIUM/LOW), stories affected, issue description, recommendation, FIS sections to update. Include a summary with total findings by severity, overall readiness (READY/NEEDS FIXES/BLOCKED), and list of FIS files needing updates.

#### Fix Issues

Apply fixes for CRITICAL or HIGH severity issues: overlapping scope → clarify file ownership with cross-references; inconsistent ADRs → align on the most prevalent or architecturally sound choice; missing seams → add missing outputs to the producing story; naming inconsistencies → standardize on the most prevalent pattern; duplicate work → consolidate into the earliest story.

**Broken scenario chains (#11)** — pick one:
- Add the missing scenario to the FIS whose story naturally owns that leg. Don't stretch an unrelated FIS.
- If no story owns it, add a new story: re-enter Step 3 (Phase/Wave/Dependencies/Risk), update the Story Catalog, then Step 5 for that story before execution.
- If the gap is a missing upstream decision, treat as a contract failure (per INSTRUCTIONS): stop, surface the minimum missing decision, and don't invent the answer. In `AUTO_MODE`, return `BLOCKED:` with the missing decision for the external orchestrator.

**Phantom-scope findings** (from sub-agent `PHANTOM_SCOPE` return summaries): sub-agents only saw plan-level sources, so first re-check each finding against `prd.md` — criteria that trace to a PRD outcome are **not** phantom scope (suppress). For confirmed phantom scope: remove the unsourced Success Criterion, or amend plan/PRD to justify it. Treat confirmed phantom scope as MEDIUM severity by default; upgrade to HIGH when it drives significant implementation work or introduces new dependencies.

After fixes, re-read changed FIS files and re-walk affected PRD flows.

**Gate**: Cross-cutting review complete; CRITICAL/HIGH issues and confirmed phantom scope resolved; FIS files updated


## OUTPUT

```
OUTPUT_DIR/
├── prd.md     # Product Requirements Document (carried in, not modified)
├── plan.md    # Implementation plan with story catalog (+ optional Shared Decisions / Binding Constraints)
└── s0N-*.md   # FIS files — one per story, one story per FIS
```

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

Skip this section when `AUTO_MODE=true`; print only the completion summary and artifact paths.

After completion, suggest the following next steps. **Recommend starting a clean session** for the context-intensive downstream skill.

1. **Execute the plan** _(clean session)_: Invoke the `andthen:exec-plan` skill — the bundle is fully specced.
2. **Execute story by story**: Invoke the `andthen:exec-spec` skill per story for more control.
3. **Review the bundle**: Invoke the `andthen:review --mode doc` skill on `plan.md` or `--mode gap` once implementation begins.
4. **Initialize project state** (if not already tracking): Create the `State` document via the `andthen:init` skill.


## FAILURE HANDLING

- **Individual spec failure** → log and continue. Report in summary.
- **>50% of specs fail** → pause this run and return a failure summary with the blocking details.
- **Cross-cutting review sub-agent fails** → warn user; specs are usable but unvalidated for inter-story consistency.
