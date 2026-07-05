---
description: Use when the user wants an implementation plan with FIS specs for every story. Trigger on 'create a plan', 'break this into stories', 'plan this feature', 'spec all stories', 'batch spec this plan'. Produces the full plan bundle (`plan.json` + all FIS) from an existing local `prd.md`, `--issue <number>`, or a GitHub issue URL. Redirect to `andthen:prd` when no PRD source is resolvable.
argument-hint: "[--max-parallel N] [--skip-review] [--issue <number>] [--to-issue] [--create-story-issues] [--visual] [--auto] <path-to-directory-with-prd.md | GitHub issue URL>"
---

# Create Implementation Plan Bundle


Produce a complete plan bundle from a PRD: a `plan.json` plus one FIS per story.

The plan is a typed JSON manifest per [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md) (referenced below as *The Plan Schema*).

**Philosophy**: story breakdown and detailed specs are co-produced. Specs decay when divorced from the story context that motivated them; batching keeps them aligned and lets a cross-cutting review catch inter-story inconsistencies before execution.


## VARIABLES

_Specs directory containing `prd.md`, or GitHub issue URL (**required**):_
INPUT: $ARGUMENTS (strip recognized flag tokens (see Optional Flags) before interpreting the remainder as the specs-directory path or GitHub issue URL; retired tokens are rejected in Step 1.0)

_Output directory (defaults to input directory):_
OUTPUT_DIR: `INPUT` (when `INPUT` is a directory containing `prd.md`), or resolved per the input contract below

### Optional Flags
- `--max-parallel N` → MAX_PARALLEL: concurrency cap per sub-wave (default 5, max 10)
- `--skip-review` → SKIP_REVIEW: skip the cross-cutting review step
- `--issue <number>` → ISSUE_INPUT: use a GitHub PRD issue as input (full handling in Step 1). Composes with local bundle output and `--to-issue`.
- `--to-issue` → PUBLISH_PLAN_ISSUE: render the in-memory plan as a GitHub issue instead of local artifacts – see Step 4's `--to-issue` branch.
- `--create-story-issues` → CREATE_STORY_ISSUES: switch `--to-issue` to **granular shape** – one parent plan issue + N story issues with `Refs #<prd-N>` / `Part of #<plan-N>` links. **Requires `--to-issue`** – rejected up-front in Step 1.
- `--visual` → VISUAL_MODE: invoke `andthen:visualize` on the produced `plan.json` after gates (Step 7). Ignored under `--to-issue`.
- `--auto` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Read project rules and guidelines (`CLAUDE.md` / `AGENTS.md` and referenced files) before starting; use the minimum number of stories that cover requirements, organized into logical phases.
- Require `INPUT`. Stop if missing.
- Delegate research/exploration to sub-agents to protect the main context window. Do not author FIS content yourself – Step 5 delegates one sub-agent per story.
- **Automation rules**: see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). Plan-specific `BLOCKED:` trigger: missing PRD source (redirect to `andthen:prd`).
- **Visual review** runs only under `--visual`, after gates – see Step 7.
- Read the `Learnings` document (see **Project Document Index**) before FIS generation, if it exists.


## GOTCHAS
- **Carried-forward stories without PRD coverage** – use `provenance`; a story with no PRD feature and no provenance is a traceability gap.
- **Skipping the Consolidation Pass** – two stories with shared implementation surface produce two specs that drift. Merge at the story level in Step 3.


## WORKFLOW

### 1. Input Validation & PRD Detection

0. **Flag-combination guard** – before any I/O, reject retired/incompatible flags per [`removed-flag-guards.md`](references/removed-flag-guards.md): `--skip-specs`, `--stories`/`--phase`, and `--create-story-issues` without `--to-issue`.

1. **Parse INPUT** – determine type:
   - **`--issue <N>` (or INPUT is a GitHub issue URL)**: fetch with `gh issue view <N>` and treat as PRD source. Resolve `OUTPUT_DIR` per the dispatch below; in local-output modes use `<base-output-dir>/issue-<N>-<feature-slug>/` (mirrors `clarify` / `prd`) and write the fetched body verbatim to `OUTPUT_DIR/prd.md` before Step 2 so later FIS sub-agents can resolve `Source refs`. Slug = lowercase issue title (alphanumerics + hyphen). Store the issue number for the plan's document-references header. `gh` failure: surface verbatim and stop (`BLOCKED: gh authentication required` / `BLOCKED: PR/issue <N> not found` in `AUTO_MODE`). Proceed to Step 2.
   - **Directory with `prd.md`**: set `OUTPUT_DIR = INPUT`; proceed.
   - **Directory without `prd.md`**: stop and redirect to `andthen:prd`. Print: `andthen:prd <input> → andthen:plan <same-directory>`.
   - **Any other input** (file, non-GitHub URL, inline): stop and redirect to `andthen:prd`.

2. **Document optional assets** in the PRD directory (ADRs/Architecture, Design system, Wireframes). Keep for the plan's `references[]`. In `--issue` mode this is best-effort.

3. **Legacy `plan.md` migration** _(local-output mode)_: if `OUTPUT_DIR/plan.json` is absent and `OUTPUT_DIR/plan.md` present, build the in-memory plan per [`legacy-plan-md-migration.md`](references/legacy-plan-md-migration.md).

**Gate**: PRD source resolved; optional assets catalogued; legacy `plan.md` (if present) parsed into the in-memory plan object


### 2. Requirements Analysis

**Read the resolved PRD source here** (local `prd.md`, or fetched issue body materialized as `OUTPUT_DIR/prd.md`). Single PRD read for plan generation; Step 5 sub-agents get spans only (no re-read), Step 6 re-reads fresh in its own sub-agent context.

Run a quick `tree -d` + `git ls-files | head -250` inline (no sub-agent) for natural implementation boundaries. Read `State`, `Ubiquitous Language`, `Architecture`, `Stack`, and `Product` documents (see **Project Document Index**) when present – priorities, canonical terminology, story splits, tech-stack constraints story scope must respect, and product anti-goals that bound decomposition. Do not restate Architecture boundaries in story scope.

Synthesize: PRD requirements and user stories, MVP scope, success criteria, prioritization (P0/P1/P2), implementation boundaries, dependencies, complexity/risk areas. Note "must support X" / "must not Y" language for the optional `## Binding Constraints` section in Step 4.

**Existing-plan handling** (local-output mode, `OUTPUT_DIR/plan.json` exists): treat the rerun as a full regeneration preserving intact story state per [`resume-regeneration.md`](references/resume-regeneration.md); both this and the Step 1 legacy path converge on an in-memory plan ready for Step 5.

**Gate**: feature mapping complete; PRD read once and held in working notes, or existing plan loaded for FIS-fill resume


### 3. Story Breakdown

#### Design Space Analysis _(if applicable)_

For multi-dimensional features, use design space decomposition: independent dimensions → separate stories, coupled → same story, high-uncertainty → spike story. Reference upstream decompositions from `clarify` or `trade-off` if available. Skip for straightforward designs.

#### Story Guidelines

Each story is **vertical** (demoable slice through all layers), **bounded** (clear scope, single responsibility), **verifiable** (enough source refs/scope to generate FIS Acceptance Scenarios and Structural Criteria), and **independent** (minimal coupling after dependencies met). Minimum stories to cover requirements; no overlap; no over-granularity.

**Enabler exception**: a story with no user-facing behavior to slice through (infrastructure, migration, cross-cutting sweep) may be layer- or module-shaped, verified by tests or fitness criteria instead of a demo. Size is never the trigger – an oversized vertical story splits into thinner verticals, not layers.

#### Implementation Phases and Wave Assignment

Organize into logical phases. Common pattern: **P1 Tracer Bullet** (thin e2e slice), **P2 Feature Slices** (parallel vertical slices), **P3 Hardening** (edges, polish, integration). Adapt to the project. Within a phase: **W1** = no dependencies, **W2** = depends only on W1, etc.; same-wave `parallel: true` stories run concurrently.

**Goal-Backward Analysis**: for each story, work backward from the user-observable outcome – what must be TRUE when done, artifacts produced, system connections. Defines story boundary and FIS seed context; detailed Acceptance Scenarios / Structural Criteria belong in the FIS.

#### Story Definition

Populate each `stories[]` object per *The Plan Schema* (full field shapes there). Non-obvious constraints:

- `id`: sequential (`"S01"`, `"S02"`, …), unique across the catalog.
- `status` starts `"pending"` (→ `"spec-ready"` after Step 5); `fis` starts `null`, unique across the catalog (1:1 story↔FIS).
- `dependsOn`: story IDs only – prose is invalid; broad sequencing belongs in phase/wave assignment or `executionNotes`.
- PRD-backed stories carry `sourceRefs`; otherwise `provenance` must explain why no PRD source exists.

**Do not include in plan story briefs** (deferred to per-story FIS): Acceptance Scenarios, Structural Criteria, technical approach, patterns, library choices, file paths, implementation gotchas, or full technical design.

#### Consolidation Pass

Before finalizing the catalog, sweep draft stories and **merge any set (pair or larger)** where any of these hold:

- **Shared implementation surface** – stories touch substantially the same files/modules. Separate FIS would duplicate architectural context and drift.
- **Tight dependency chain** – `A → B → C` where downstream stories have no independent demo value (e.g. "define endpoint" + "wire handler" + "surface in UI" for the same feature).
- **Trivially small set** – each story produces a barely-populated FIS and they share a primary concern.

Run pairwise, iterate to a fixed point – 3-way merges compose from successive pair-merges. Merge by union: combine outcomes, reconcile scope into one coherent vertical slice, renumber. The merged story is still one demoable outcome. If a merged story turns out too large for a single FIS, Step 5's spec sub-agent emits the size signal and the orchestrator revisits Step 3 – do not pre-split.

> **Why**: the plan↔FIS join is a single-field contract (`stories[].fis`). Keeping it 1:1 means downstream skills never reason about shared/composite specs.

**Gate**: all stories defined; no two stories share a FIS path


### 4. Write `plan.json`

**If `--to-issue` is set**: skip Steps 4–6 and run the GitHub-output flow in [`to-issue-mode.md`](references/to-issue-mode.md) (single-issue or granular shape; no durable local artifacts). Stop when that flow completes.

Assemble the in-memory plan object per *The Plan Schema* and write it to `OUTPUT_DIR/plan.json`. Use 2-space indentation and the schema's documented key order so diffs reflect content changes, not ordering drift. Story `status`/`fis`/`owner` initialize to `"pending"`/`null`/`null` (`owner` is claimed later via `andthen:ops update-plan-owner`).

**Top-level field assembly**: populate `schemaVersion` / `prd` / `references` / `overview.*` shapes per *The Plan Schema*. `prd` is `"github://issue/<N>"` when `--issue` was used.

**Shared Decisions and Binding Constraints (inline extraction)**: walk Step 2's working notes and populate the optional arrays:

- `sharedDecisions`: emit when stories share an interface/naming/abstraction. 3–6 entries; each: `title`, `description`, `stories` (producers + consumers). Empty otherwise.
- `bindingConstraints`: emit when the PRD has "must support X" / "must not Y" at risk of silent decomposition drop. Each: `featureId`, `anchor` (e.g. `"prd.md#export-rules"`), `verbatim` (the PRD span). Flow unchanged into FIS Required Context in Step 5. Empty otherwise.

Both are inline extractions – no sub-agent fan-out.

`riskSummary[]` aggregates per-story risk/mitigation pairs (replaces the legacy `## Risk Summary` table). `executionNotes` is a short narrative on running the plan (replaces the legacy `## Execution Guide`); place Step 1's `Migrated from legacy plan.md: ...` annotation here when applicable.

Schema invariants per *The Plan Schema*; enforced by the Self-Check below.

#### Self-Check (plan.json)
- [ ] Every PRD feature maps to a story; cross-cutting concerns (auth, logging, error pages) covered
- [ ] PRD-backed stories carry `sourceRefs`; stories without PRD coverage carry `provenance`
- [ ] `parallel` flags and wave assignments consistent with `dependsOn`
- [ ] `riskSummary[]` populated where stories carry non-low `risk`
- [ ] Validates against *The Plan Schema* (the schema invariants above), with key order matching schema-document order

#### Initialize Project State (if the `State` document exists; see **Project Document Index**)
If the `State` document exists, update it to reflect the new plan via the `andthen:ops` skill:
- `update-state phase "Phase 1: {first_phase_name}"`
- `update-state status "On Track"`
- `update-state note "Plan created: {plan_name} ({N} stories, {M} phases)"`

If the `State` document does not exist, do not create it – suggest it in follow-up actions instead.

**Gate**: `plan.json` saved and schema-validated


### 5. Parallel FIS Creation

Skip stories whose `stories[].fis` already points at a file that exists on disk (preserves both legacy-migration carryover and resume-rerun work). Every remaining story (`fis` is `null` or points at a missing file) gets one sub-agent producing one FIS.

#### Wave Ordering

`sharedDecisions` (when present) pre-resolves inter-story architectural decisions. Default: all in-scope stories launch in parallel (up to `MAX_PARALLEL`). Exception: hold back a story if its spec depends on a decision not captured in `sharedDecisions` – wait for the producing story's spec to complete first. Fallback: if `sharedDecisions` is empty, use strict wave ordering (W1 complete → W2). Batch into sub-waves if story count exceeds `MAX_PARALLEL`.

#### Sub-Agent Prompts

For each in-scope story, spawn a sub-agent that runs `/andthen:spec --auto story {story_id} of {OUTPUT_DIR}/plan.json`. The `andthen:spec` skill handles the full authoring flow per [the FIS authoring guidelines](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md) (referenced below as *The Authoring Guidelines*).

**Additional context for each sub-agent**:
- Reads `plan.json` (`sharedDecisions`, `bindingConstraints` as structured fields) plus only the PRD anchors in the story's `sourceRefs`. No whole-PRD re-read.
- Every applicable `bindingConstraints[]` entry flows unchanged into FIS Required Context with its anchor as the source pin. Do not narrow or redistribute into Acceptance Scenarios or Structural Criteria; those proof surfaces may reference the constraint, but the verbatim constraint lives in Required Context.
- Scenario shape, `Intent` / `Expected Outcomes` authoring, and the Plan-Spec Alignment / Self-Check / Reverse Coverage passes are the spec skill's job per *The Authoring Guidelines*. Batch-mode boundary: Reverse Coverage runs against plan-level sources + `bindingConstraints[]` only – PRD-level reverse coverage is the orchestrator's Step 6 job.
- Report back (verbatim): success/failure, FIS path, confidence score, any `PHANTOM_SCOPE` findings, any `OVERSIZE:` line, and any blocking self-review signal (`MISSING REQUIREMENT:` / `BLOCKED:`).

> **Size signal**: an `OVERSIZE:` line means the story was too broad – the orchestrator revisits Step 3 to decompose, then regenerates. The oversized FIS is overwritten by the regeneration.

#### Wait, Collect, and Verify Plan Writes

Wait for all sub-agents in the current sub-wave to complete. Log any failures (continue with remaining stories – don't block the wave).

**Authoritative writes**: each spec sub-agent drives its own `andthen:ops update-plan-fis` and `update-plan <story> spec-ready` calls per the spec skill's `## OUTPUT` "Update source plan" contract. The plan orchestrator does **not** re-issue those calls (no double-write).

**Gate** – per generated FIS, re-read `OUTPUT_DIR/plan.json` and verify the story's `fis` points at the reported FIS on disk and `status` is `"spec-ready"` (or `"done"` if terminal). On a non-`spec-ready` status, distinguish:
- **Deliberate hold** – spec reported a blocking self-review signal (`MISSING REQUIREMENT:` / `BLOCKED:`): the status is intentional. Do **not** force it; keep the `fis` pointer, carry the unresolved decision into the Step 6 summary, and resolve it before exec.
- **Write miss** – no blocking signal: repair with a single `andthen:ops update-plan-fis` / `update-plan <story> spec-ready`, re-read once. Persistent miss is a contract failure – record in the Step 6 summary so the user sees which story did not converge.

Worked sub-wave batching example: see [`wave-batching-example.md`](references/wave-batching-example.md).

**Gate**: all sub-waves complete and pass the per-FIS gate above; every story's `fis` set (each path unique).


### 6. Cross-Cutting Review & Fixes

> **Skip this step if `--skip-review` flag is set.**

Delegate to one sub-agent, routed per the **Sub-Agent Model Policy** (default: inherit; *cross-cutting judgment*), at **high** effort, with the plan path and all FIS paths. This is the **second (and only other) full PRD read** in the flow – the sub-agent reads `prd.md` fresh plus all FIS and `plan.json`, then checks for:

1. **Overlapping scope** – multiple stories modifying the same files/abstractions.
2. **Inconsistent architectural decisions** – contradictory ADR choices across stories.
3. **Missing integration seams** – Story B needs output Story A's spec doesn't produce.
4. **Dependency gaps** – cross-story dependencies not reflected in FIS task ordering.
5. **Inconsistent naming/patterns** – different conventions for similar operations.
6. **Duplicate work** – same utility/component/abstraction created in multiple stories.
7. **Plan-vs-FIS alignment** – every plan story scope and Binding Constraint covered by FIS scenarios/criteria; flag silent narrowing without a scope note.
8. **Intra-story scope contradictions** – `What We're NOT Doing` items that block a scenario or criterion.
9. **Scenario gaps** – legacy plan Key Scenario seeds not mapped to FIS scenarios; cross-story scenario dependencies uncovered.
10. **PRD-FIS traceability** – every PRD acceptance criterion has ≥1 FIS scenario. Catches requirements narrowed during decomposition or lost in spec generation. Example: PRD requiring "remote host support" should not produce a FIS that says "always loopback".
11. **Scenario chain connectivity** – for each PRD multi-step flow (`User Flows` preferred; fall back to sequenced User Stories), FIS scenarios chain cleanly: each leg's **Then** outputs satisfy the next leg's **Given**. Distinct from #10 – #11 catches orphan outputs and unsourced inputs between adjacent scenarios. List scenarios in flow order; name the handoff artifact (state, record, event, UI element) between each pair; flag any gap. Example: flow "upload → result" – Story A ends at "job enqueued", Story B starts at "job completes", but no scenario produces the user-visible result state.

Per finding: severity (CRITICAL/HIGH/MEDIUM/LOW), stories affected, description, recommendation, FIS sections to update. Summary: findings by severity, readiness (READY/NEEDS FIXES/BLOCKED), FIS files needing updates.

#### Fix Issues

Apply fixes for CRITICAL/HIGH: overlapping scope → clarify file ownership via cross-references; inconsistent ADRs → align on the prevalent/architecturally sound choice; missing seams → add outputs to the producing story; naming inconsistencies → standardize on prevalent pattern; duplicate work → consolidate into the earliest story.

**Broken scenario chains (#11)** – pick one:
- Add the missing scenario to the FIS whose story naturally owns that leg. Do not stretch an unrelated FIS.
- If no story owns it, add a new story: re-enter Step 3 (Phase/Wave/Dependencies/Risk), update the catalog, then Step 5 for that story.
- If the gap is a missing upstream decision, treat as a contract failure: stop, surface the minimum missing decision. `AUTO_MODE`: return `BLOCKED:` with the missing decision.

**Phantom-scope findings** (from sub-agent `PHANTOM_SCOPE` summaries): sub-agents only saw plan-level sources, so re-check each against `prd.md` first – PRD-traceable criteria are **not** phantom (suppress). Confirmed phantom: remove the unsourced scenario/criterion, or amend plan/PRD to justify. Default MEDIUM severity; upgrade to HIGH when it drives significant implementation work or new dependencies.

After fixes, re-read changed FIS files and re-walk affected PRD flows.

**Gate**: review complete; CRITICAL/HIGH issues and confirmed phantom scope resolved; FIS files updated


### 7. Visual Review _(only when `--visual` and local output mode)_

After `plan.json` exists, every generated FIS path is verified, and the cross-cutting review gate has passed or been explicitly skipped, invoke the `andthen:visualize` skill on the produced `plan.json`. Print both the plan path and the visualizer's output path.

**Gate**: HTML rendered and browser-open attempted, or fallback path printed


## OUTPUT

```
OUTPUT_DIR/
├── prd.md     # Product Requirements Document (carried in, not modified)
├── plan.json  # Implementation plan: typed manifest per plan-schema.md
└── s0N-*.md   # FIS files – one per story, one story per FIS
```

When complete, print the output's **relative path from the project root**.

Before printing completion, re-check that every FIS path listed in the summary exists on disk. If any are missing, treat the bundle as incomplete and repair or report the affected stories as failed; never emit missing paths as successful `story_specs`.


## COMPLETION

Print a summary: **plan.json** path; **FIS files created** count; **Stories specced**, **skipped**, **failed**; **Cross-cutting review** findings by severity and readiness; **Fixes applied**; **Readiness**; **Migration notice** (only when Step 1 migrated a legacy `plan.md`).


## FOLLOW-UP ACTIONS

Skip this section when `AUTO_MODE=true`; print only the completion summary and artifact paths.

After completion, suggest next steps. **Recommend starting a clean session** for the context-intensive downstream skills.

1. **Execute the plan** _(clean session)_: the `andthen:exec-plan` skill – the bundle is fully specced.
2. **Execute story by story**: the `andthen:exec-spec` skill per story for more control.
3. **Review the bundle**: the `andthen:review --mode doc` skill on `plan.json`, or `--mode gap` once implementation begins.
4. **Review visually**: the `andthen:visualize` skill on `plan.json` (skip when `--visual` already ran).
5. **Initialize project state** (if not already tracking): the `State` document via the `andthen:init` skill.


## FAILURE HANDLING

- **Individual spec failure** → log and continue. Report in summary.
- **>50% of specs fail** → pause this run and return a failure summary with the blocking details.
- **Cross-cutting review sub-agent fails** → warn user; specs are usable but unvalidated for inter-story consistency.
