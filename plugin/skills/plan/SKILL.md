---
description: Use when the user wants an implementation plan with FIS specs for every story. Trigger on 'create a plan', 'break this into stories', 'plan this feature', 'spec all stories', 'batch spec this plan'. Produces the full plan bundle (`plan.md` + all FIS + `.technical-research.md`) from an existing `prd.md`, or `plan.md` alone with `--skip-specs`. Requires an existing `prd.md` in the input directory — redirect to `andthen:prd` if missing.
argument-hint: "[--skip-specs] [--stories S01,S03,...] [--phase N] [--max-parallel N] [--skip-review] [--issue <number>] [--to-issue] [--create-story-issues] [--auto|--headless] <path-to-directory-with-prd.md>"
---

# Create Implementation Plan Bundle


Transform a Product Requirements Document (`prd.md`) into a complete implementation plan bundle: `plan.md` with story breakdown **plus** batch-generated Feature Implementation Specifications (FIS) — one per story — **plus** shared `.technical-research.md`. Runs story breakdown with a consolidation pass, parallel FIS sub-agents, and a cross-cutting review in one flow.

**Invariant**: one story → one FIS. The Story Catalog `FIS` column is a unique-key column; no two stories share a FIS path.

**`prd.md` is a required input** — if the input directory has no `prd.md`, the skill fails fast and redirects to the `andthen:prd` skill. PRD synthesis is not this skill's job.

**Philosophy**: Story breakdown and detailed specs are co-produced. Specs decay quickly when divorced from the story context that motivated them; batching keeps them aligned and lets a cross-cutting review catch inter-story inconsistencies before execution starts.


## VARIABLES

_Specs directory containing `prd.md` (**required**):_
INPUT: $ARGUMENTS (strip any flag tokens like `--skip-specs`, `--stories`, `--phase`, `--max-parallel`, `--skip-review`, `--issue`, `--to-issue`, `--create-story-issues`, `--auto`, or `--headless` before interpreting the remainder as the specs-directory path)

_Output directory (defaults to input directory):_
OUTPUT_DIR: `INPUT` (when `INPUT` is a directory containing `prd.md`), or resolved per the input contract below

### Optional Flags
- `--skip-specs` → SKIP_SPECS: Produce `plan.md` only (cheap planning pass; skip technical research, FIS generation, and cross-cutting review)
- `--stories S01,S03,...` → STORY_FILTER: Only generate FIS for listed story IDs
- `--phase N` → PHASE_FILTER: Only generate FIS for stories in phase N
- `--max-parallel N` → MAX_PARALLEL: Concurrency cap per sub-wave (default 5, max 10)
- `--skip-review` → SKIP_REVIEW: Skip the cross-cutting review step
- `--issue <number>` → ISSUE_INPUT: Use a GitHub PRD issue as input (`gh issue view <N>`); the issue body replaces a local `prd.md` read. `OUTPUT_DIR` resolves to `<base-output-dir>/issue-<N>-<feature-slug>/` (mirrors `clarify` and `prd` patterns). Composes with all output modes — default bundle, `--skip-specs`, and `--to-issue`.
- `--to-issue` → PUBLISH_PLAN_ISSUE: Output the plan as a single GitHub issue per the **single-issue shape** in [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md). **Writes nothing to disk** — skip Steps 4 (plan.md write), 5 (local technical-research write), 6 (FIS generation), and 7 (cross-cutting review). Mutually exclusive with `--skip-specs` (FIS-not-needed is implicit in `--to-issue`). Default GitHub-output mode produces ONE plan issue.
- `--create-story-issues` → CREATE_STORY_ISSUES: Switch `--to-issue` from single-issue to **granular shape** per [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md): one parent plan issue PLUS N story issues with `Refs #<prd-N>` and `Part of #<plan-N>` links. **Requires `--to-issue`** — reject up-front if absent (`BLOCKED: --create-story-issues requires --to-issue` in `AUTO_MODE`; print error and stop in default mode) before any `gh` call.
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Require `INPUT`. Stop if missing.
- Delegate research and exploration to sub-agents to protect the main context window.
- Stories define scope, not implementation details. Minimum stories to cover requirements.
- Organize stories into logical phases.
- **Automation rules** (headless-first, `--auto` / `--headless` strict mode, `--auto` propagation): see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). Plan-specific `BLOCKED:` triggers: missing `prd.md` (redirect to the `andthen:prd` skill), incompatible artifacts, ambiguity so severe no defensible plan can be produced.
- Focus on "what" not "how" at the plan level; detailed implementation decisions live in per-story FIS files.
- **Resume contract**: when re-running on a partially-specced directory, skip stories whose `**FIS**` field already points at an existing file. Re-running only fills gaps.
- Read the `Learnings` document (see **Project Document Index**) before FIS generation, if it exists.


### Orchestrator Role

Do not write FIS content yourself — delegate to per-story sub-agents in Step 6.


## GOTCHAS
- **Carried-forward stories without PRD coverage** – use the **Provenance** field; a story with no PRD feature and no provenance is a traceability gap
- **Skipping the Consolidation Pass** – two stories with shared implementation surface produce two specs that drift. Merge them at the story level in Step 3 instead
- **Technical research becomes stale if plan changes** — re-run technical research before generating new specs after plan edits
- **Status updates get dropped when context is exhausted** — `plan.md` FIS field updates are gates. Update immediately after each sub-wave


## WORKFLOW

### 1. Input Validation & PRD Detection

0. **Flag-combination guard** — enforce up-front, before any I/O:
   - `--create-story-issues` without `--to-issue`: reject. Print `Error: --create-story-issues requires --to-issue (granular GitHub mode is meaningless without GitHub output).` and stop. `AUTO_MODE`: emit `BLOCKED: --create-story-issues requires --to-issue` and exit. No `gh` call has occurred yet.
   - `--to-issue` with `--skip-specs`: reject. Print `Error: --to-issue and --skip-specs are mutually exclusive — --to-issue already skips FIS generation.` and stop. `AUTO_MODE`: `BLOCKED: --to-issue is mutually exclusive with --skip-specs`.

1. **Parse INPUT** — determine type:
   - **`--issue <N>` flag (or INPUT is a GitHub issue URL)**: fetch the body with `gh issue view <N>` and treat it as the PRD source — the issue body replaces a local `prd.md` read. Resolve `OUTPUT_DIR` per the dispatch table below; in local-output modes use `<base-output-dir>/issue-<N>-<feature-slug>/` as the subdirectory (mirrors `clarify` and `prd`). The slug derives from the issue title (lowercase, alphanumerics + hyphen). Store the issue number for the plan's document-references header. On `gh` failure: surface verbatim and stop (`BLOCKED: gh authentication required` / `BLOCKED: PR/issue <N> not found` in `AUTO_MODE`). Proceed to Step 2.
   - **Directory with `prd.md`**: set `OUTPUT_DIR = INPUT`; proceed to Step 2.
   - **Directory without `prd.md`**: stop and redirect to the `andthen:prd` skill. Print the expected chain: `andthen:prd <input> → andthen:plan <same-directory>`.
   - **Any other input** (file, URL, inline): stop and redirect to the `andthen:prd` skill.

2. **Document optional assets** present in the PRD directory (ADRs/Architecture, Design system, Wireframes). Keep references for the plan's document-references header. In `--issue` mode this is best-effort — the issue body is the only authoritative source.

**Gate**: PRD source resolved (local `prd.md` or fetched issue body); optional assets catalogued


### 2. Requirements Analysis

Scan codebase structure (use a sub-agent) to identify natural implementation boundaries, feature groupings, and dependency relationships — enough to inform story breakdown. Read the `State` document (see **Project Document Index**; default: `docs/STATE.md`) if it exists — use current phase, active stories, and blockers to inform story priorities. Reference the `Ubiquitous Language` document (see **Project Document Index**) if it exists; use canonical terms in story names and acceptance criteria.

Synthesize into a unified understanding of: all PRD requirements and user stories, MVP scope, success criteria, prioritization (P0/P1/P2), natural implementation boundaries, feature dependencies, and complexity/risk areas.

> Do not save `.technical-research.md` here — deep technical research is generated in Step 5 (after story breakdown), where it directly informs FIS generation.

**Gate**: Feature mapping complete


### 3. Story Breakdown

#### Design Space Analysis _(if applicable)_

For features with multiple design dimensions, use design space decomposition to inform story structure: independent dimensions → separate stories, coupled dimensions → same story, high-uncertainty dimensions → spike story. If a decomposition was produced upstream (by `clarify` or `trade-off`), reference and build on it. Skip for straightforward designs.

#### Story Guidelines

Each story should be **vertical** (cuts through all layers to a demoable slice), **bounded** (clear scope, single responsibility), **verifiable** (has acceptance criteria), and **independent** (minimal coupling after dependencies met). Use minimum stories to cover requirements; no overlap; no over-granularity.

#### Implementation Phases and Wave Assignment

Organize stories into logical phases. Common pattern: **Phase 1 – Tracer Bullet** (thin e2e slice), **Phase 2 – Feature Slices** (parallel vertical slices), **Phase 3 – Hardening** (edge cases, polish, integration). Adapt to the project. Within each phase, assign waves: **W1** = no dependencies, **W2** = depends only on W1, **W3+** = cascading; stories in the same wave with [P] run in parallel.

**Goal-Backward Analysis**: for each story, work backward from the user-observable outcome — what must be TRUE when done, what artifacts must exist, how they connect to the system. Derive acceptance criteria from these observable truths.

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

**Do not include in stories** (deferred to per-story FIS): technical approach, patterns, library choices, file paths, implementation gotchas, or full technical design.

#### Consolidation Pass

Before finalizing the Story Catalog, sweep the draft stories and **merge any set (pair or larger)** where any of these hold:

- **Shared implementation surface** — the stories would touch substantially the same files or modules. Separate FIS would duplicate shared architectural context and drift.
- **Tight dependency chain** — `A → B` (or `A → B → C`) where downstream stories have no independent demo value without the upstream (e.g., "define API endpoint" + "wire endpoint to handler" + "surface endpoint in UI" for the same feature).
- **Trivially small set** — each story in the set would produce a barely-populated FIS (small surface, few acceptance criteria — well below the 3-6 guideline in Story Definition) and they share a primary concern.

Run pairwise, then iterate to a fixed point so a 3-way or larger merge composes naturally from successive pair-merges. Merge by union: combine acceptance criteria, reconcile scope into a single coherent vertical slice, renumber if needed. The merged story is still one demoable outcome, just broader. If a merged story turns out too large for a single FIS, Step 6's per-story sub-agent reports that back via the size signal and the orchestrator revisits Step 3 for that story — do not pre-split here.

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

> **If `--to-issue` is set**: do not write `plan.md` to disk in this step. Build the same logical plan content (story breakdown, catalog, metadata) in memory, then load `references/to-issue-mode.md` for the GitHub-output workflow (in-memory research synthesis, plan-issue body assembly per `plan-issue-shape.md`, single-issue or granular `gh issue create` flow, and the no-local-writes gate). Steps 5 (FIS generation) and 7 (cross-cutting review) are skipped in this mode.


### 5. Technical Research (One-Time Upfront Discovery)

Before spawning any spec sub-agents, do **all discovery and research work once** via up to 3 parallel sub-agents. This eliminates redundant codebase scanning, guideline reading, and architecture analysis each spec sub-agent would otherwise do independently.

**Sub-agent 1: Project Context** — Read project `CLAUDE.md` (Document Index, workflow rules); scan codebase structure; identify conventions, tech stack, learnings. Output: dense summary.

**Sub-agent 2: Story-Scoped File Map** — Per-story related files/modules; shared-files section. Output: per-story file list with relevance notes.

**Sub-agent 3: Shared Architectural Decisions** — For each pair of dependent stories: identify the interface/contract between them (API shape, data types, naming, error handling); document the shared decision so both specs can reference it. Also identify: naming conventions that must be consistent, shared abstractions multiple stories will create/consume, API patterns that must be uniform. Extract **binding PRD constraints** from `OUTPUT_DIR/prd.md`: requirements that specify explicit capabilities (e.g., "must support remote hosts"), protocol details, security requirements, or user-facing behaviors. These constraints must flow unchanged into FIS success criteria — they are not subject to architectural trade-offs or scope narrowing by individual stories. Output: numbered list of shared decisions with rationale, specific enough to reference in FIS success criteria; plus a separate "Binding PRD Constraints" section. Each constraint entry includes the verbatim PRD text span, the source feature ID, and the source PRD heading anchor (`prd.md#<heading-slug>`). Per-story sub-agents inherit these as-is; broken anchors found later are a doc-review finding, not an execution blocker.

External research (API docs, library lookups) is deferred to individual spec sub-agents that need it — most stories don't reference external APIs, and the ones that do can spawn a sub-agent that consults the project's `## Documentation Lookup Tools` section. Claude Code plugin users may invoke the `andthen:documentation-lookup` agent directly.

**Consolidation**: After all sub-agents complete, save to `{OUTPUT_DIR}/.technical-research.md`. **Use the template**: [`templates/technical-research-template.md`](templates/technical-research-template.md).

If a `.technical-research.md` already exists (e.g. from a prior run), merge new sections into it rather than overwriting.

**Gate**: Technical research saved to `{OUTPUT_DIR}/.technical-research.md`, covers all stories in scope


### 6. Parallel FIS Creation

Apply filters (`STORY_FILTER`, `PHASE_FILTER`); skip stories whose `**FIS**` field already points at a file that exists on disk. Remaining in-scope stories each get one sub-agent producing one FIS.

#### Wave Ordering

The technical research pre-resolves most inter-story architectural decisions. Default: all in-scope stories launch in parallel (up to `MAX_PARALLEL`, default 5, max 10). Exception: hold back a story if its spec depends on a decision the technical research could not pre-resolve — wait for the producing story's spec to complete first. Fallback: if the technical research is incomplete or unavailable, use strict wave ordering (W1 complete → W2). Batch into sub-waves if story count exceeds `MAX_PARALLEL`.

#### Sub-Agent Prompts

For each in-scope story, spawn a sub-agent that runs `/andthen:spec --auto story {story_id} of {OUTPUT_DIR}/plan.md`. The `andthen:spec` skill handles the full authoring flow per its guidelines at `${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md`. Because `.technical-research.md` already exists on disk (from Step 5), the spec skill's Steps 1–2 short-circuit to verification-only, keeping per-story invocation cost low.

**Additional context for each sub-agent** (pass alongside the skill invocation):
- Technical research: `{OUTPUT_DIR}/.technical-research.md` — use for shared decisions, file maps, and the binding-PRD-constraints extraction; skip research phases already covered.
- Binding PRD constraints: every applicable entry from the "Binding PRD Constraints" section of the technical research flows into FIS Success Criteria unchanged. Do not narrow the binding constraint set.
- Run Plan-Spec Alignment Check, Self-Check, and Reverse Coverage Check from the guidelines. Reverse Coverage Check runs against plan-level sources plus the binding-PRD-constraints extraction; PRD-level reverse coverage beyond the extracted constraints is handled by the orchestrator in Step 7.
- Report back: success/failure, FIS path, confidence score, any `PHANTOM_SCOPE` findings from Reverse Coverage, and any `OVERSIZE:` line emitted by the spec skill (verbatim, including line/task counts and recommendation).

> **Size signal**: if a sub-agent's completion summary contains an `OVERSIZE:` line (see `${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md` Key Generation Guidelines #6 for the threshold), the story was too broad — the orchestrator revisits Step 3 to decompose that story before regenerating its FIS. The oversized FIS that the spec sub-agent saved is discarded by the regeneration pass, so it does not need to be deleted up front.

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

1. **Overlapping scope** – multiple stories modifying the same files or abstractions
2. **Inconsistent architectural decisions** – contradictory ADR choices across stories
3. **Missing integration seams** – Story B needs output Story A's spec doesn't produce
4. **Dependency gaps** – cross-story dependencies not reflected in FIS task ordering
5. **Inconsistent naming/patterns** – different conventions for similar operations or shared concerns
6. **Duplicate work** – same utility, component, or abstraction independently created in multiple stories
7. **Plan-vs-FIS alignment** – every plan acceptance criterion must be covered by FIS success criteria; flag any criterion silently narrowed without a scope note
8. **Intra-story scope contradictions** – items in "What We're NOT Doing" that block a success criterion
9. **Scenario gaps** – plan Key Scenario seeds not mapped to FIS scenarios; cross-story scenario dependencies not covered
10. **PRD-FIS requirements traceability** – verify that every PRD feature requirement's acceptance criteria has at least one corresponding FIS scenario. This catches requirements that were narrowed during plan decomposition or lost during spec generation. Example: a PRD requiring "remote host support" should not produce a FIS that says "always loopback"
11. **Scenario chain connectivity** – for each multi-step flow in the PRD (`User Flows` preferred; fall back to sequenced User Stories), verify FIS scenarios chain cleanly: each leg's **Then** outputs must satisfy the next leg's **Given**. Distinct from #10 (per-criterion coverage) — #11 catches orphan outputs and unsourced inputs between adjacent scenarios. List the scenarios in flow order and name the handoff artifact (state, record, event, UI element) between each pair; flag any gap. Example: flow "upload file → see result" — Story A's scenario ends at "job enqueued", Story B's begins at "job completes", but no scenario produces the user-visible result state.

Output per finding: severity (CRITICAL/HIGH/MEDIUM/LOW), stories affected, issue description, recommendation, FIS sections to update. Include a summary with total findings by severity, overall readiness (READY/NEEDS FIXES/BLOCKED), and list of FIS files needing updates.

#### Fix Issues

Apply fixes for CRITICAL or HIGH severity issues: overlapping scope → clarify file ownership with cross-references; inconsistent ADRs → align on the most prevalent or architecturally sound choice; missing seams → add missing outputs to the producing story; naming inconsistencies → standardize on the most prevalent pattern; duplicate work → consolidate into the earliest story.

**Broken scenario chains (#11)** — pick one:
- Add the missing scenario to the FIS whose story naturally owns that leg. Don't stretch an unrelated FIS.
- If no story owns it, add a new story: re-enter Step 3 (Phase/Wave/Dependencies/Risk), update the Story Catalog, re-run technical research if files fall outside the existing map, then Step 6 for that story before execution.
- If the gap is a missing upstream decision, treat as a contract failure (per INSTRUCTIONS): stop, surface the minimum missing decision, and don't invent the answer. In `AUTO_MODE`, return `BLOCKED:` with the missing decision for the external orchestrator.

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
