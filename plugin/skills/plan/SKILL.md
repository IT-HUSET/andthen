---
description: Use when the user wants an implementation plan with FIS specs for every story. Trigger on 'create a plan', 'break this into stories', 'plan this feature', 'spec all stories', 'batch spec this plan'. Produces the full plan bundle (`plan.json` + all FIS) from an existing local `prd.md`, `--issue <number>`, or a GitHub issue URL. Redirect to `andthen:prd` when no PRD source is resolvable.
argument-hint: "[--max-parallel N] [--skip-review] [--issue <number>] [--to-issue] [--create-story-issues] [--visual] [--auto] <path-to-directory-with-prd.md | GitHub issue URL>"
---

# Create Implementation Plan Bundle


Produce a complete plan bundle from a PRD: a `plan.json` ledger plus one FIS per story.

The plan is a typed JSON manifest per [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md) (referenced below as *The Plan Schema*). Status, FIS path, and dependencies are typed fields; `andthen:exec-plan` / `andthen:ops` / `andthen:review --mode gap` deserialize declaratively.

**Philosophy**: story breakdown and detailed specs are co-produced. Specs decay when divorced from the story context that motivated them; batching keeps them aligned and lets a cross-cutting review catch inter-story inconsistencies before execution.


## VARIABLES

_Specs directory containing `prd.md`, or GitHub issue URL (**required**):_
INPUT: $ARGUMENTS (strip active flag tokens like `--max-parallel`, `--skip-review`, `--issue`, `--to-issue`, `--create-story-issues`, `--visual`, `--auto`, or `--headless` before interpreting the remainder as the specs-directory path or GitHub issue URL; retired tokens are rejected in Step 1.0)

_Output directory (defaults to input directory):_
OUTPUT_DIR: `INPUT` (when `INPUT` is a directory containing `prd.md`), or resolved per the input contract below

### Optional Flags
- `--max-parallel N` → MAX_PARALLEL: concurrency cap per sub-wave (default 5, max 10)
- `--skip-review` → SKIP_REVIEW: skip the cross-cutting review step
- `--issue <number>` → ISSUE_INPUT: use a GitHub PRD issue as input (`gh issue view <N>`). In local-output mode, materialize the issue body verbatim as `OUTPUT_DIR/prd.md` so story `Source refs` resolve during FIS generation. `OUTPUT_DIR` = `<base-output-dir>/issue-<N>-<feature-slug>/` (mirrors `clarify` / `prd`). Composes with local bundle output and `--to-issue`.
- `--to-issue` → PUBLISH_PLAN_ISSUE: render the in-memory plan as a single GitHub issue per the **single-issue shape** in [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md). **Writes no durable local artifacts** – skip Steps 4–6.
- `--create-story-issues` → CREATE_STORY_ISSUES: switch `--to-issue` to **granular shape** – one parent plan issue + N story issues with `Refs #<prd-N>` / `Part of #<plan-N>` links. **Requires `--to-issue`** (granular GitHub mode is meaningless without GitHub output) – rejected up-front in Step 1.
- `--visual` → VISUAL_MODE: after the local bundle is complete and validated, invoke `andthen:visualize` on the produced `plan.json`. Ignored under `--to-issue`.
- `--auto` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Read project rules and guidelines (`CLAUDE.md` / `AGENTS.md` and referenced files) before starting.
- Require `INPUT`. Stop if missing.
- Delegate research/exploration to sub-agents to protect the main context window. Do not author FIS content yourself – Step 5 delegates one sub-agent per story.
- Stories define scope, not implementation details. Use the minimum number of stories that cover requirements; organize into logical phases.
- **Automation rules**: see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). Plan-specific `BLOCKED:` triggers: missing PRD source (redirect to `andthen:prd`), incompatible artifacts, ambiguity so severe no defensible plan can be produced.
- **Visual review** runs only under `--visual`, after gates – see Step 7.
- Focus on "what" not "how" at the plan level; detailed decisions live in per-story FIS.
- **Resume contract**: re-running skips stories whose `stories[].fis` points at an existing file (status `spec-ready` or `done` preserved). Re-runs only fill gaps.
- **Schema contract**: `plan.json` follows *The Plan Schema*. Initial story `status` is `pending`; transitions to `spec-ready` after FIS generation.
- Read the `Learnings` document (see **Project Document Index**) before FIS generation, if it exists.


## GOTCHAS
- **Carried-forward stories without PRD coverage** – use `provenance`; a story with no PRD feature and no provenance is a traceability gap.
- **Skipping the Consolidation Pass** – two stories with shared implementation surface produce two specs that drift. Merge at the story level in Step 3.
- **Status updates dropped at end of context** – `stories[].fis` / `stories[].status` are gates after each sub-wave. Drive them through `andthen:ops update-plan-fis` / `update-plan`; ad-hoc hand-edits bypass the contract.
- **Prose in `dependsOn` is invalid** – the array is machine-readable scheduler input (see Story Definition).


## WORKFLOW

### 1. Input Validation & PRD Detection

0. **Flag-combination guard** – enforce up-front, before any I/O:
   - `--skip-specs`: reject. Print `Error: --skip-specs was removed. Run andthen:plan on the directory to create or resume the full local bundle, or use --to-issue for GitHub issue output without local FIS files.` and stop. `AUTO_MODE`: emit `BLOCKED: --skip-specs was removed; rerun andthen:plan to create/resume the full bundle or use --to-issue` and exit.
   - `--stories` or `--phase`: reject. Print `Error: --stories and --phase were removed. Run andthen:plan on the directory to fill all missing FIS files, or use andthen:spec story <id> of <plan.json> for a one-off story spec.` and stop. `AUTO_MODE`: emit `BLOCKED: --stories/--phase were removed; rerun andthen:plan to fill all missing FIS files` and exit.
   - `--create-story-issues` without `--to-issue`: reject. Print `Error: --create-story-issues requires --to-issue (granular GitHub mode is meaningless without GitHub output).` and stop. `AUTO_MODE`: emit `BLOCKED: --create-story-issues requires --to-issue` and exit. No `gh` call has occurred yet.

1. **Parse INPUT** – determine type:
   - **`--issue <N>` (or INPUT is a GitHub issue URL)**: fetch with `gh issue view <N>` and treat as PRD source. Resolve `OUTPUT_DIR` per the dispatch below; in local-output modes use `<base-output-dir>/issue-<N>-<feature-slug>/` (mirrors `clarify` / `prd`) and write the fetched body verbatim to `OUTPUT_DIR/prd.md` before Step 2 so later FIS sub-agents can resolve `Source refs`. Slug = lowercase issue title (alphanumerics + hyphen). Store the issue number for the plan's document-references header. `gh` failure: surface verbatim and stop (`BLOCKED: gh authentication required` / `BLOCKED: PR/issue <N> not found` in `AUTO_MODE`). Proceed to Step 2.
   - **Directory with `prd.md`**: set `OUTPUT_DIR = INPUT`; proceed.
   - **Directory without `prd.md`**: stop and redirect to `andthen:prd`. Print: `andthen:prd <input> → andthen:plan <same-directory>`.
   - **Any other input** (file, non-GitHub URL, inline): stop and redirect to `andthen:prd`.

2. **Document optional assets** in the PRD directory (ADRs/Architecture, Design system, Wireframes). Keep for the plan's `references[]`. In `--issue` mode this is best-effort.

3. **Legacy `plan.md` migration check** _(local-output mode only)_: if `OUTPUT_DIR/plan.json` is absent and `OUTPUT_DIR/plan.md` is present, parse the legacy Story Catalog (markdown contract per [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md)), build the in-memory plan per *The Plan Schema*, and hold it for Step 4. The check fires for `--issue` mode too if `OUTPUT_DIR` already carries a legacy `plan.md` from a prior run.
   - Map legacy statuses round-trip: `Pending`/`Spec Ready`/`In Progress`/`Done`/`Skipped`/`Blocked` → lowercase-kebab. Unrecognized values (e.g. `Retired`) → `"skipped"` with a durable `executionNotes` annotation: `Migrated from legacy plan.md: status "<old>" mapped to "skipped" for stories <id-list>.`
   - Preserve `fis` paths and statuses for rows whose `FIS` cell points at an existing file. FIS-unset rows get `fis: null`, `status: "pending"`.
   - Step 5 generates FIS only for `fis: null` stories.
   - After Step 4's `plan.json` write, emit: `Migrated plan.md → plan.json. plan.md is no longer consumed; delete when ready.` Do not auto-delete `plan.md`.

**Gate**: PRD source resolved; optional assets catalogued; legacy `plan.md` (if present) parsed into the in-memory plan object


### 2. Requirements Analysis

**Read the resolved PRD source here** (local `prd.md`, or fetched issue body materialized as `OUTPUT_DIR/prd.md`). Single PRD read for plan generation; Step 5 sub-agents get spans only (no re-read), Step 6 re-reads fresh in its own sub-agent context.

Run a quick `tree -d` + `git ls-files | head -250` inline (no sub-agent) for natural implementation boundaries. Read `State`, `Ubiquitous Language`, `Architecture`, `Stack`, and `Product` documents (see **Project Document Index**) when present – priorities, canonical terminology, story splits, tech-stack constraints story scope must respect, and product anti-goals that bound decomposition. Do not restate Architecture boundaries in story scope.

Synthesize: PRD requirements and user stories, MVP scope, success criteria, prioritization (P0/P1/P2), implementation boundaries, dependencies, complexity/risk areas. Note "must support X" / "must not Y" language for the optional `## Binding Constraints` section in Step 4.

**Existing-plan handling** (local-output mode, `OUTPUT_DIR/plan.json` exists): treat the rerun as a full regeneration preserving intact story state. Capture each story's `id`, `status`, `fis`, the content-defining fields per the **Preservation predicate** (see *Writability rules* in *The Plan Schema*), and `executionNotes` into a preservation map. Discard legacy `metadata` fields (e.g. `immutableDigest`) – not in the current schema. Continue Step 2 and proceed through 3–4 as a fresh generation. After Step 4's reassembly:

- **Preserve `executionNotes`** by prepending the captured value to the freshly assembled value (de-duplicate identical lines; the migration annotation is durable per the schema's **Migration from legacy `plan.md`** section).
- **Restore `status` and `fis`** from the preservation map per the **Preservation predicate**. Stories failing any clause reset to `pending` / `null`.
- Emit: `Regenerated plan.json; preserved status/fis for stories satisfying the Preservation predicate: <id-list>.` and (when applicable) `Reset to pending/null due to predicate failure (content drift or missing FIS file): <other-id-list>.`

If every story satisfies the predicate, omit the reset line – the regeneration is observationally a resume.

Step 1's legacy migration covers the `plan.md`-only case; both paths converge with an in-memory plan object ready for Step 5.

**Gate**: feature mapping complete; PRD read once and held in working notes, or existing plan loaded for FIS-fill resume


### 3. Story Breakdown

#### Design Space Analysis _(if applicable)_

For multi-dimensional features, use design space decomposition: independent dimensions → separate stories, coupled → same story, high-uncertainty → spike story. Reference upstream decompositions from `clarify` or `trade-off` if available. Skip for straightforward designs.

#### Story Guidelines

Each story is **vertical** (demoable slice through all layers), **bounded** (clear scope, single responsibility), **verifiable** (enough source refs/scope to generate FIS Acceptance Scenarios and Structural Criteria), and **independent** (minimal coupling after dependencies met). Minimum stories to cover requirements; no overlap; no over-granularity.

#### Implementation Phases and Wave Assignment

Organize into logical phases. Common pattern: **P1 Tracer Bullet** (thin e2e slice), **P2 Feature Slices** (parallel vertical slices), **P3 Hardening** (edges, polish, integration). Adapt to the project. Within a phase: **W1** = no dependencies, **W2** = depends only on W1, etc.; same-wave `parallel: true` stories run concurrently.

**Goal-Backward Analysis**: for each story, work backward from the user-observable outcome – what must be TRUE when done, artifacts produced, system connections. Defines story boundary and FIS seed context; detailed Acceptance Scenarios / Structural Criteria belong in the FIS.

#### Story Definition

For each story, populate the `stories[]` object per *The Plan Schema*:

- `id`: sequential identifier (`"S01"`, `"S02"`, …) – unique across the catalog.
- `name`: brief descriptive name.
- `status`: initial value `"pending"`. Transitions to `"spec-ready"` after Step 5; downstream skills drive `"in-progress"` / `"done"` / `"skipped"` / `"blocked"` via `andthen:ops`.
- `fis`: initial value `null`. Set to the relative POSIX path after FIS generation in Step 5. Unique across the catalog (1:1 invariant).
- `dependsOn`: array of story IDs from this catalog that must complete first. Empty array when none. Prose is invalid – broad sequencing belongs in phase/wave assignment or `executionNotes`.
- `phase`: phase ID matching one in `overview.phases[]`.
- `wave`: wave ID listed in that phase's `waves`.
- `parallel`: boolean – `true` if the story can run in parallel with wave siblings.
- `risk`: `"low"` / `"medium"` / `"high"`.

Then populate the compact story brief fields on the same `stories[]` object:

- `scope`: one paragraph covering intended outcome, inclusions, exclusions. No implementation approach.
- `sourceRefs`: PRD feature IDs and anchors the FIS author must read for detailed behavior, e.g. `["FR-2", "FR-5", "prd.md#export-rules"]`. Required for PRD-backed stories; omit only when `provenance` explains why no PRD source exists.
- `provenance`: string, required only for carried-forward stories or stories with no direct PRD feature coverage.
- `assetRefs`: optional array of wireframes, ADRs, design-system references, or other upstream artifacts the FIS author needs.
- `notes`: optional, for load-bearing planning notes that don't fit the other fields.

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

**If `--to-issue` is set**: this step is the GitHub-output branch, not the local-file branch. Do **not** write `plan.json`, update the State document, generate FIS files, or run the cross-cutting review. Render the in-memory plan object built from Steps 2–3 to the markdown issue-body shape per [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md). Use the issue-body template at [`plan-template-issue.md`](templates/plan-template-issue.md) as the single-issue rendering shape, then load [`to-issue-mode.md`](references/to-issue-mode.md) for the single-issue or granular `gh issue create` flow and its no-local-writes gate. After the issue workflow completes, stop.

Assemble the in-memory plan object per *The Plan Schema* and write it to `OUTPUT_DIR/plan.json`. Use 2-space indentation and the schema's documented key order so diffs reflect content changes, not ordering drift. Initial story `status` is `"pending"`; `fis` is `null` until Step 5 lands each FIS.

**Top-level field assembly**:

- `schemaVersion`: `"1"`.
- `prd`: relative POSIX path to `prd.md` (or `"github://issue/<N>"` when `--issue` was used).
- `references`: array of one short string per upstream artifact discovered during Step 1 (ADRs, design system, wireframes, glossary, ad-hoc research). Empty array when none.
- `overview.summary`: 1–3 short paragraphs of plain prose covering the sequencing strategy.
- `overview.phases`: ordered phase records – `id` (e.g. `"P1"`), `name`, and `waves` (ordered wave IDs used by stories in that phase).

**Shared Decisions and Binding Constraints (inline extraction)**: walk Step 2's working notes and populate the optional arrays:

- `sharedDecisions`: emit when stories share an interface/naming/abstraction. 3–6 entries; each: `title`, `description`, `stories` (producers + consumers). Empty otherwise.
- `bindingConstraints`: emit when the PRD has "must support X" / "must not Y" at risk of silent decomposition drop. Each: `featureId`, `anchor` (e.g. `"prd.md#export-rules"`), `verbatim` (the PRD span). Flow unchanged into FIS Required Context in Step 5. Empty otherwise.

Both are inline extractions – no sub-agent fan-out.

`riskSummary[]` aggregates per-story risk/mitigation pairs (replaces the legacy `## Risk Summary` table). `executionNotes` is a short narrative on running the plan (replaces the legacy `## Execution Guide`); place Step 1's `Migrated from legacy plan.md: ...` annotation here when applicable.

Schema invariants:

- Each non-null `fis` value is unique across the catalog (1:1 story↔FIS); multiple `null` is valid before FIS generation.
- Each `dependsOn` element is an existing `stories[].id`. Prose is invalid; broad sequencing lives in `executionNotes`.
- Stories without `sourceRefs` must carry `provenance`.
- Status values are restricted to the closed enum in *The Plan Schema*.

#### Self-Check (plan.json)
- [ ] Every PRD feature maps to a story; cross-cutting concerns (auth, logging, error pages) covered
- [ ] PRD-backed stories carry `sourceRefs`; stories without PRD coverage carry `provenance`
- [ ] `parallel` flags and wave assignments consistent with `dependsOn`
- [ ] `riskSummary[]` populated where stories carry non-low `risk`
- [ ] Validates against *The Plan Schema* (the schema invariants above), with key order matching schema-document order

If Step 1 detected a legacy `plan.md`, emit the one-line migration note now: `Migrated plan.md → plan.json. plan.md is no longer consumed; delete when ready.`

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

`sharedDecisions` (when present) pre-resolves inter-story architectural decisions. Default: all in-scope stories launch in parallel (up to `MAX_PARALLEL`, default 5, max 10). Exception: hold back a story if its spec depends on a decision not captured in `sharedDecisions` – wait for the producing story's spec to complete first. Fallback: if `sharedDecisions` is empty, use strict wave ordering (W1 complete → W2). Batch into sub-waves if story count exceeds `MAX_PARALLEL`.

#### Sub-Agent Prompts

For each in-scope story, spawn a sub-agent that runs `/andthen:spec --auto story {story_id} of {OUTPUT_DIR}/plan.json`. The `andthen:spec` skill handles the full authoring flow per [the FIS authoring guidelines](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md) (referenced below as *The Authoring Guidelines*).

**Additional context for each sub-agent**:
- Reads `plan.json` (`sharedDecisions`, `bindingConstraints` as structured fields) plus only the PRD anchors in the story's `sourceRefs`. No whole-PRD re-read.
- Every applicable `bindingConstraints[]` entry flows unchanged into FIS Required Context with its anchor as the source pin. Do not narrow or redistribute into Acceptance Scenarios or Structural Criteria; those proof surfaces may reference the constraint, but the verbatim constraint lives in Required Context.
- Acceptance Scenarios use the canonical `- [ ] **S<NN> [OC<NN>(,OC<NN>)*] [TI<NN>(,TI<NN>)*] <description>**` shape per *Acceptance Scenarios and Proof-of-Work* in *The Authoring Guidelines* (parser depends on the exact token shape; outcomes before tasks).
- `## Feature Overview and Goal` carries `**Intent**:` and `**Expected Outcomes**:` sub-blocks per *Feature Overview and Goal Authoring*. Distil intent/outcomes from the story's scope and Source refs. Every `[OC<NN>]` exemplified by ≥1 scenario tagging it; every scenario carries ≥1 `[OC<NN>]` tag.
- Run Plan-Spec Alignment Check, Self-Check, and Reverse Coverage Check from *The Authoring Guidelines*. Reverse Coverage runs against plan-level sources + `bindingConstraints[]`; PRD-level reverse coverage is the orchestrator's Step 6 job.
- Report back: success/failure, FIS path, confidence score, any `PHANTOM_SCOPE` findings, any `OVERSIZE:` line (verbatim).

> **Size signal**: an `OVERSIZE:` line means the story was too broad – the orchestrator revisits Step 3 to decompose, then regenerates. The oversized FIS is overwritten by the regeneration.

#### Wait, Collect, and Verify Plan Writes

Wait for all sub-agents in the current sub-wave to complete. Log any failures (continue with remaining stories – don't block the wave).

**Authoritative writes**: each spec sub-agent drives its own `andthen:ops update-plan-fis` and `update-plan <story> spec-ready` calls per the spec skill's `## OUTPUT` "Update source plan" contract. The plan orchestrator does **not** re-issue those calls (no double-write).

**Gate** – per generated FIS, re-read `OUTPUT_DIR/plan.json` and verify:
- The story's `fis` points at the reported FIS path on disk.
- The story's `status` is `"spec-ready"` (or `"done"` if already terminal).

Miss → repair with a single `andthen:ops update-plan-fis` / `update-plan <story> spec-ready`, re-read once. Persistent miss is a contract failure – record in the Step 6 review summary so the user sees which story did not converge.

#### Spec Flow Example

```
8-story plan (after Step 3 Consolidation Pass) → 8 FIS files

Step 5 (MAX_PARALLEL=4):
  Sub-wave 1: spec-S01, spec-S02, spec-S03, spec-S04 (parallel)
  Sub-wave 2: spec-S05, spec-S06, spec-S07, spec-S08 (parallel)
  → After each sub-wave: re-read plan.json and verify each story's fis + status landed
    (spec sub-agents drive the ops writes; orchestrator only repairs on miss)
```

**Gate**: All specs complete; every story's `fis` set (each path unique) and `status` advanced to `spec-ready` – verified by re-reading `plan.json`, repaired by the orchestrator only on miss


### 6. Cross-Cutting Review & Fixes

> **Skip this step if `--skip-review` flag is set.**

Delegate to one sub-agent (inheriting the session model) at **high** effort with the plan path and all FIS paths. This is the **second (and only other) full PRD read** in the flow – the sub-agent reads `prd.md` fresh plus all FIS and `plan.json`, then checks for:

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


## COMPLETION

Print a summary:
- **plan.json**: path
- **FIS files created**: count (one per in-scope story)
- **Stories specced**: count and list with FIS paths
- **Stories skipped**: (already had FIS)
- **Stories failed**: (if any, with error details)
- **Cross-cutting review**: findings count by severity, readiness assessment
- **Fixes applied**: list of FIS files modified
- **Readiness**: overall assessment for execution
- **Migration notice** (only when Step 1 migrated a legacy `plan.md`): one line confirming `plan.md` is no longer consumed and may be deleted.


## FOLLOW-UP ACTIONS

Skip this section when `AUTO_MODE=true`; print only the completion summary and artifact paths.

After completion, suggest the following next steps. **Recommend starting a clean session** for the context-intensive downstream skill.

1. **Execute the plan** _(clean session)_: Invoke the `andthen:exec-plan` skill – the bundle is fully specced.
2. **Execute story by story**: Invoke the `andthen:exec-spec` skill per story for more control.
3. **Review the bundle**: Invoke the `andthen:review --mode doc` skill on `plan.json` or `--mode gap` once implementation begins.
4. **Review visually**: Run `andthen:visualize <plan.json>` when a browser review of story sequencing, dependencies, and risk would help (skip when `--visual` already ran).
5. **Initialize project state** (if not already tracking): Create the `State` document via the `andthen:init` skill.


## FAILURE HANDLING

- **Individual spec failure** → log and continue. Report in summary.
- **>50% of specs fail** → pause this run and return a failure summary with the blocking details.
- **Cross-cutting review sub-agent fails** → warn user; specs are usable but unvalidated for inter-story consistency.
