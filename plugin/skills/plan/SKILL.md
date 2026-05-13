---
description: Use when the user wants an implementation plan with FIS specs for every story. Trigger on 'create a plan', 'break this into stories', 'plan this feature', 'spec all stories', 'batch spec this plan'. Produces the full plan bundle (`plan.json` + all FIS) from an existing `prd.md`. Requires an existing `prd.md` in the input directory – redirect to `andthen:prd` if missing.
argument-hint: "[--max-parallel N] [--skip-review] [--issue <number>] [--to-issue] [--create-story-issues] [--auto|--headless] <path-to-directory-with-prd.md>"
---

# Create Implementation Plan Bundle


Transform a Product Requirements Document (`prd.md`) into a complete implementation plan bundle: `plan.json` with structured story breakdown **plus** batch-generated Feature Implementation Specifications (FIS) – one per story. Runs story breakdown with a consolidation pass, parallel FIS sub-agents, and a cross-cutting review in one flow.

The plan output is a typed JSON manifest per [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md). Status, FIS path, and dependencies are typed fields, not parsed table cells; downstream consumers (`andthen:exec-plan`, `andthen:ops`, `andthen:review --mode gap`) deserialize and operate declaratively. GitHub-issue mode (`--to-issue`) still emits markdown for the issue body – JSON is the local runtime ledger; markdown is the GitHub transport.

**Invariant**: one story → one FIS. Each `stories[].fis` value is unique across the catalog (the 1:1 story↔FIS contract).

**`prd.md` is a required input** – if the input directory has no `prd.md`, the skill fails fast and redirects to the `andthen:prd` skill. PRD synthesis is not this skill's job.

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
- `--to-issue` → PUBLISH_PLAN_ISSUE: Output the plan as a single GitHub issue per the **single-issue shape** in [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md). **Writes nothing to disk** – skip Steps 4 (plan.json write), 5 (FIS generation), and 6 (cross-cutting review). The issue body is rendered from the in-memory plan object as markdown (the GitHub transport shape); no `plan.json` is written locally. Default GitHub-output mode produces ONE plan issue.
- `--create-story-issues` → CREATE_STORY_ISSUES: Switch `--to-issue` from single-issue to **granular shape** per [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md): one parent plan issue PLUS N story issues with `Refs #<prd-N>` and `Part of #<plan-N>` links. **Requires `--to-issue`** – reject up-front if absent (`BLOCKED: --create-story-issues requires --to-issue` in `AUTO_MODE`; print error and stop in default mode) before any `gh` call.
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Require `INPUT`. Stop if missing.
- Delegate research and exploration to sub-agents to protect the main context window.
- Stories define scope, not implementation details. Minimum stories to cover requirements.
- Organize stories into logical phases.
- **Automation rules** (headless-first, `--auto` / `--headless` strict mode, `--auto` propagation): see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). Plan-specific `BLOCKED:` triggers: missing `prd.md` (redirect to the `andthen:prd` skill), incompatible artifacts, ambiguity so severe no defensible plan can be produced.
- Focus on "what" not "how" at the plan level; detailed implementation decisions live in per-story FIS files.
- **Resume contract**: when re-running on a partially-specced directory, skip stories whose `stories[].fis` already points at an existing file (status `spec-ready` or `done` is preserved). Re-running only fills gaps.
- **Schema contract**: the local `plan.json` follows [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md). Initial story `status` is `pending`; transitions to `spec-ready` after FIS generation lands. Field order, indent, and writability rules are defined there.
- Read the `Learnings` document (see **Project Document Index**) before FIS generation, if it exists.


### Orchestrator Role

Do not write FIS content yourself – delegate to per-story sub-agents in Step 5.


## GOTCHAS
- **Carried-forward stories without PRD coverage** – use the `provenance` field; a story with no PRD feature and no provenance is a traceability gap
- **Skipping the Consolidation Pass** – two stories with shared implementation surface produce two specs that drift. Merge them at the story level in Step 3 instead
- **Status updates get dropped when context is exhausted** – `stories[].fis` and `stories[].status` updates are gates after each sub-wave. Drive them through `andthen:ops update-plan-fis` / `update-plan` so the deterministic mutation path runs; ad-hoc hand-edits from inside other skills bypass the contract and create drift that later skills can't reason about.
- **Prose in `dependsOn` is invalid** – the array is machine-readable scheduler input. Each element must be an existing story ID (`"S01"`, `"S04"`). Express broad sequencing through phase/wave placement or `executionNotes`.


## WORKFLOW

### 1. Input Validation & PRD Detection

0. **Flag-combination guard** – enforce up-front, before any I/O:
   - `--skip-specs`: reject. Print `Error: --skip-specs was removed. Run andthen:plan on the directory to create or resume the full local bundle, or use --to-issue for GitHub issue output without local FIS files.` and stop. `AUTO_MODE`: emit `BLOCKED: --skip-specs was removed; rerun andthen:plan to create/resume the full bundle or use --to-issue` and exit.
   - `--stories` or `--phase`: reject. Print `Error: --stories and --phase were removed. Run andthen:plan on the directory to fill all missing FIS files, or use andthen:spec story <id> of <plan.json> for a one-off story spec.` and stop. `AUTO_MODE`: emit `BLOCKED: --stories/--phase were removed; rerun andthen:plan to fill all missing FIS files` and exit.
   - `--create-story-issues` without `--to-issue`: reject. Print `Error: --create-story-issues requires --to-issue (granular GitHub mode is meaningless without GitHub output).` and stop. `AUTO_MODE`: emit `BLOCKED: --create-story-issues requires --to-issue` and exit. No `gh` call has occurred yet.

1. **Parse INPUT** – determine type:
   - **`--issue <N>` flag (or INPUT is a GitHub issue URL)**: fetch the body with `gh issue view <N>` and treat it as the PRD source. Resolve `OUTPUT_DIR` per the dispatch table below; in local-output modes use `<base-output-dir>/issue-<N>-<feature-slug>/` as the subdirectory (mirrors `clarify` and `prd`) and write the fetched issue body verbatim to `OUTPUT_DIR/prd.md` before Step 2 so later FIS sub-agents can resolve `Source refs`. The slug derives from the issue title (lowercase, alphanumerics + hyphen). Store the issue number for the plan's document-references header. On `gh` failure: surface verbatim and stop (`BLOCKED: gh authentication required` / `BLOCKED: PR/issue <N> not found` in `AUTO_MODE`). Proceed to Step 2.
   - **Directory with `prd.md`**: set `OUTPUT_DIR = INPUT`; proceed to Step 2.
   - **Directory without `prd.md`**: stop and redirect to the `andthen:prd` skill. Print the expected chain: `andthen:prd <input> → andthen:plan <same-directory>`.
   - **Any other input** (file, URL, inline): stop and redirect to the `andthen:prd` skill.

2. **Document optional assets** present in the PRD directory (ADRs/Architecture, Design system, Wireframes). Keep references for the plan's `references[]` array. In `--issue` mode this is best-effort – the issue body is the only authoritative source.

3. **Legacy `plan.md` migration check** _(local-output mode only)_: if `OUTPUT_DIR/plan.json` does not exist but `OUTPUT_DIR/plan.md` does, this is a one-shot migration of an older bundle. The check fires regardless of input source – including `--issue <N>` mode, where `OUTPUT_DIR` resolves to `<base-output-dir>/issue-<N>-<feature-slug>/`: if that subdirectory already contains a legacy `plan.md` from a prior run, it is migrated alongside the freshly fetched issue body. Parse the existing `plan.md` Story Catalog using the markdown contract per [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md), build the in-memory plan object per [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md), and remember it for Step 4.
   - Map all six legacy status values round-trip: `Pending` → `"pending"`, `Spec Ready` → `"spec-ready"`, `In Progress` → `"in-progress"`, `Done` → `"done"`, `Skipped` → `"skipped"`, `Blocked` → `"blocked"`. Any unrecognized legacy value (e.g. `Retired` from earlier enums) → `"skipped"` with a one-line annotation appended to `executionNotes`: `Migrated from legacy plan.md: status "<old>" mapped to "skipped" for stories <id-list>.` The annotation is intentionally durable – left in `executionNotes` as a migration audit trail.
   - Preserve `fis` paths and statuses for stories whose `FIS` cell points at an existing file. Stories with the FIS-unset sentinel get `fis: null`, `status: "pending"`.
   - Step 5 will then generate FIS only for stories with `fis: null`.
   - After successful write of `plan.json` in Step 4, emit a one-line user-visible note: `Migrated plan.md → plan.json. plan.md is no longer consumed; delete when ready.` Do not auto-delete `plan.md` (destructive – user's call).

**Gate**: PRD source resolved (local `prd.md` or fetched issue body); optional assets catalogued; legacy `plan.md` (if present) parsed into the in-memory plan object


### 2. Requirements Analysis

**Read the resolved PRD source directly here** (local `prd.md`, or fetched issue body materialized as `OUTPUT_DIR/prd.md` in local-output issue mode). This is the single PRD read for plan generation – Step 5 sub-agents receive relevant spans as context (do not re-read), and Step 6's cross-cutting review reads the PRD fresh in its own sub-agent context.

Run a quick `tree -d` + `git ls-files | head -250` codebase scan inline (no sub-agent) to identify natural implementation boundaries – enough to inform story breakdown, not deep research. Read the `State` document (see **Project Document Index**; default: `docs/STATE.md`) if it exists – use current phase, active stories, and blockers to inform story priorities. Reference the `Ubiquitous Language` document (see **Project Document Index**) if it exists; use canonical terms in story names, scope, and source refs. Reference the `Architecture` document (see **Project Document Index**) if it exists; let documented component boundaries inform natural story splits rather than restating them in story scope.

Synthesize into a unified understanding of: all PRD requirements and user stories, MVP scope, success criteria, prioritization (P0/P1/P2), natural implementation boundaries, feature dependencies, and complexity/risk areas. As you read the PRD, note any "must support X" / "must not Y" language that should land in the optional `## Binding Constraints` section in Step 4.

**Existing-plan handling** (in local-output mode, if `OUTPUT_DIR/plan.json` already exists): treat the rerun as a full regeneration that preserves intact story state. Capture each existing story's `id`, `status`, `fis`, the content-defining fields named in the **Preservation predicate** (see [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md)'s **Writability rules** section), and the document-level `executionNotes` into a preservation map. Any pre-existing `metadata` field (legacy 0.19.x `immutableDigest`) is discarded – it is not part of the current schema. Continue Step 2's analysis and proceed through Steps 3–4 as a fresh plan generation. After re-assembling the in-memory plan in Step 4:

- **Preserve `executionNotes`** by prepending the captured value to the freshly assembled `executionNotes` (de-duplicate identical lines; the migration annotation is intentionally durable per the schema's **Migration from legacy `plan.md`** section and must survive regeneration).
- **Restore `status` and `fis`** from the preservation map per the **Preservation predicate**. Stories failing any clause of the predicate reset to `pending` / `null`.
- Emit two stdout lines: `Regenerated plan.json; preserved status/fis for stories satisfying the Preservation predicate: <id-list>.` and (when applicable) `Reset to pending/null due to predicate failure (content drift or missing FIS file): <other-id-list>.`

If every regenerated story satisfies the preservation predicate, no stdout reset line is needed and the regeneration is observationally a resume.

The Step 1 legacy-migration sub-step covers the older `plan.md`-only case (no `plan.json` at all); both paths converge with an in-memory plan object ready for Step 5.

**Gate**: Feature mapping complete; PRD read once and held in working notes, or existing plan loaded for FIS-fill resume


### 3. Story Breakdown

#### Design Space Analysis _(if applicable)_

For features with multiple design dimensions, use design space decomposition to inform story structure: independent dimensions → separate stories, coupled dimensions → same story, high-uncertainty dimensions → spike story. If a decomposition was produced upstream (by `clarify` or `trade-off`), reference and build on it. Skip for straightforward designs.

#### Story Guidelines

Each story should be **vertical** (cuts through all layers to a demoable slice), **bounded** (clear scope, single responsibility), **verifiable** (has enough source refs and scope to generate FIS success criteria), and **independent** (minimal coupling after dependencies met). Use minimum stories to cover requirements; no overlap; no over-granularity.

#### Implementation Phases and Wave Assignment

Organize stories into logical phases. Common pattern: **Phase 1 – Tracer Bullet** (thin e2e slice), **Phase 2 – Feature Slices** (parallel vertical slices), **Phase 3 – Hardening** (edge cases, polish, integration). Adapt to the project. Within each phase, assign waves: **W1** = no dependencies, **W2** = depends only on W1, **W3+** = cascading; stories in the same wave with [P] run in parallel.

**Goal-Backward Analysis**: for each story, work backward from the user-observable outcome – what must be TRUE when done, what artifacts must exist, how they connect to the system. Use this to define the story boundary and FIS seed context; detailed success criteria and scenarios belong in the generated FIS, not in the plan.

#### Story Definition

For each story, populate the `stories[]` object per [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md):

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

**Do not include in plan story briefs** (deferred to per-story FIS): success criteria, full scenarios, technical approach, patterns, library choices, file paths, implementation gotchas, or full technical design.

#### Consolidation Pass

Before finalizing the Story Catalog, sweep the draft stories and **merge any set (pair or larger)** where any of these hold:

- **Shared implementation surface** – the stories would touch substantially the same files or modules. Separate FIS would duplicate shared architectural context and drift.
- **Tight dependency chain** – `A → B` (or `A → B → C`) where downstream stories have no independent demo value without the upstream (e.g., "define API endpoint" + "wire endpoint to handler" + "surface endpoint in UI" for the same feature).
- **Trivially small set** – each story in the set would produce a barely-populated FIS (small surface, little independent verification value) and they share a primary concern.

Run pairwise, then iterate to a fixed point so a 3-way or larger merge composes naturally from successive pair-merges. Merge by union: combine intended outcomes, reconcile scope into a single coherent vertical slice, renumber if needed. The merged story is still one demoable outcome, just broader. If a merged story turns out too large for a single FIS, Step 5's per-story sub-agent reports that back via the size signal and the orchestrator revisits Step 3 for that story – do not pre-split here.

> **Why this matters**: the plan↔FIS join is a single-field contract (`stories[].fis`). Keeping it 1:1 means downstream skills (`exec-plan`, `exec-spec`, `ops`) never need to reason about shared or composite specs, and the plan is unambiguous on read. Two stories wanting to share a spec is a signal they were one story.

**Gate**: All stories defined; no two stories intended to share a FIS path


### 4. Write `plan.json`

**If `--to-issue` is set**: this step is the GitHub-output branch, not the local-file branch. Do **not** write `plan.json`, update the State document, generate FIS files, or run the cross-cutting review. Render the in-memory plan object built from Steps 2–3 to the markdown issue-body shape per [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md). Use the issue-body template at [`templates/plan-template-issue.md`](templates/plan-template-issue.md) as the single-issue rendering shape, then load `references/to-issue-mode.md` for the single-issue or granular `gh issue create` flow and its no-local-writes gate. After the issue workflow completes, stop.

Assemble the in-memory plan object per [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md) and write it to `OUTPUT_DIR/plan.json`. Use 2-space indentation and the schema's documented key order so diffs reflect content changes, not ordering drift. Initial story `status` is `"pending"`; `fis` is `null` until Step 5 lands each FIS.

**Top-level field assembly**:

- `schemaVersion`: `"1"`.
- `prd`: relative POSIX path to `prd.md` (or `"github://issue/<N>"` when `--issue` was used).
- `references`: array of one short string per upstream artifact discovered during Step 1 (ADRs, design system, wireframes, glossary, ad-hoc research). Empty array when none.
- `overview.summary`: 1–3 short paragraphs of plain prose covering the sequencing strategy.
- `overview.phases`: ordered phase records – `id` (e.g. `"P1"`), `name`, and `waves` (ordered wave IDs used by stories in that phase).

**Shared Decisions and Binding Constraints (inline extraction, no sub-agent)**: walk the working-notes PRD synthesis from Step 2 and populate the optional arrays:

- `sharedDecisions`: emit when stories have inter-dependencies that imply a shared interface, naming convention, or abstraction multiple stories will create or consume. 3–6 entries; each carries `title`, `description`, and `stories` (producing and consuming story IDs). Empty array when none apply.
- `bindingConstraints`: emit when the PRD contains "must support X" / "must not Y" language at risk of being silently dropped during decomposition. Each entry carries `featureId`, `anchor` (e.g. `"prd.md#export-rules"`), and `verbatim` (the PRD span). These flow unchanged into FIS Required Context blocks during Step 5. Empty array when none apply.

Both arrays are inline extractions from PRD content already loaded in Step 2 – no sub-agent fan-out.

`riskSummary[]` aggregates per-story risk and mitigation pairs (replaces the legacy `## Risk Summary` markdown table). `executionNotes` is a short narrative on how to run the plan (replaces the legacy `## Execution Guide` section); populate the `Migrated from legacy plan.md: ...` annotation here when Step 1's legacy migration mapped any non-canonical status values.

Keep these schema invariants:

- Each story's `fis` value is unique across the catalog **for non-null values** (1:1 story↔FIS); multiple pending stories sharing `null` is valid before FIS generation.
- Each `dependsOn` element is an ID that exists in `stories[]`. Prose is invalid; broad sequencing lives in `executionNotes`.
- Stories without `sourceRefs` must carry a `provenance` string explaining the absence.
- Status values are restricted to the closed enum in [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md).

#### Self-Check (plan.json)
- [ ] All PRD features have corresponding stories
- [ ] PRD-backed stories carry `sourceRefs`; stories without PRD coverage carry `provenance`
- [ ] Stories have clear boundaries (no overlap)
- [ ] `dependsOn` arrays use only existing story IDs; no prose
- [ ] `parallel` flags correctly applied
- [ ] Wave assignments are pre-computed and consistent with dependencies
- [ ] Risk areas identified (`risk` field on stories; `riskSummary[]` populated where needed)
- [ ] No missing functionality (cross-cutting concerns like auth, logging, error pages covered)
- [ ] Not over-granular (combined where sensible)
- [ ] Document validates against [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md): `schemaVersion: "1"`, status enum values, unique `fis` paths (non-null only – multiple `null` values are valid pre-Step-5), key order matches schema-document order

If Step 1 detected a legacy `plan.md`, emit the one-line migration note now: `Migrated plan.md → plan.json. plan.md is no longer consumed; delete when ready.`

Optional: Invoke the `andthen:review --mode doc` skill on `plan.json` before continuing.

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

For each in-scope story, spawn a sub-agent that runs `/andthen:spec --auto story {story_id} of {OUTPUT_DIR}/plan.json`. The `andthen:spec` skill handles the full authoring flow per its guidelines at `${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md`.

**Additional context for each sub-agent** (pass alongside the skill invocation):
- Each sub-agent reads `plan.json` (which carries `sharedDecisions` and `bindingConstraints` as structured fields) plus only the PRD anchors named in that story's `sourceRefs`. Do not re-read the whole PRD. Source refs exist so the slim plan stays compact while the FIS still receives detailed behavior.
- Binding constraints: every applicable entry from `bindingConstraints[]` (when non-empty) flows into FIS Success Criteria unchanged. Do not narrow the binding constraint set.
- Run Plan-Spec Alignment Check, Self-Check, and Reverse Coverage Check from the guidelines. Reverse Coverage Check runs against plan-level sources plus `bindingConstraints[]`; PRD-level reverse coverage beyond those constraints is handled by the orchestrator in Step 6.
- Report back: success/failure, FIS path, confidence score, any `PHANTOM_SCOPE` findings from Reverse Coverage, and any `OVERSIZE:` line emitted by the spec skill (verbatim, including line/task counts and recommendation).

> **Size signal**: if a sub-agent's completion summary contains an `OVERSIZE:` line (see `${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md` Key Generation Guidelines #6 for the threshold), the story was too broad – the orchestrator revisits Step 3 to decompose that story before regenerating its FIS. The oversized FIS that the spec sub-agent saved is discarded by the regeneration pass, so it does not need to be deleted up front.

#### Wait, Collect, and Verify Plan Writes

Wait for all sub-agents in the current sub-wave to complete. Log any failures (continue with remaining stories – don't block the wave).

**Authoritative writes**: each spec sub-agent – invoked as `/andthen:spec --auto story <id> of <plan>` – drives its own `andthen:ops update-plan-fis` and `update-plan <story> spec-ready` calls per the spec skill's `## OUTPUT` "Update source plan" contract. The plan orchestrator does **not** redundantly re-issue those calls (no double-write).

**Gate** – for each successfully generated FIS, re-read `OUTPUT_DIR/plan.json` and verify the spec sub-agent's writes landed:
- The story's `fis` field points at the reported FIS path on disk.
- The story's `status` is `"spec-ready"` (or `"done"` – left untouched if already terminal).

On any miss, the spec sub-agent's ops calls dropped. Repair with a single `andthen:ops update-plan-fis` and/or `update-plan <story> spec-ready` against the missing field, then re-read once. Persistent miss is a contract failure – record in the cross-cutting review summary (Step 6) so the user sees which story did not converge.

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

Delegate to a single opus sub-agent with all generated FIS paths. Provide: plan path (`plan.json`), list of all FIS paths. This is the **second (and only other) full PRD read** in the plan flow – the sub-agent reads `prd.md` fresh in its own context, plus all FIS files and `plan.json`, then checks for:

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
11. **Scenario chain connectivity** – for each multi-step flow in the PRD (`User Flows` preferred; fall back to sequenced User Stories), verify FIS scenarios chain cleanly: each leg's **Then** outputs must satisfy the next leg's **Given**. Distinct from #10 (per-criterion coverage) – #11 catches orphan outputs and unsourced inputs between adjacent scenarios. List the scenarios in flow order and name the handoff artifact (state, record, event, UI element) between each pair; flag any gap. Example: flow "upload file → see result" – Story A's scenario ends at "job enqueued", Story B's begins at "job completes", but no scenario produces the user-visible result state.

Output per finding: severity (CRITICAL/HIGH/MEDIUM/LOW), stories affected, issue description, recommendation, FIS sections to update. Include a summary with total findings by severity, overall readiness (READY/NEEDS FIXES/BLOCKED), and list of FIS files needing updates.

#### Fix Issues

Apply fixes for CRITICAL or HIGH severity issues: overlapping scope → clarify file ownership with cross-references; inconsistent ADRs → align on the most prevalent or architecturally sound choice; missing seams → add missing outputs to the producing story; naming inconsistencies → standardize on the most prevalent pattern; duplicate work → consolidate into the earliest story.

**Broken scenario chains (#11)** – pick one:
- Add the missing scenario to the FIS whose story naturally owns that leg. Don't stretch an unrelated FIS.
- If no story owns it, add a new story: re-enter Step 3 (Phase/Wave/Dependencies/Risk), update the Story Catalog, then Step 5 for that story before execution.
- If the gap is a missing upstream decision, treat as a contract failure (per INSTRUCTIONS): stop, surface the minimum missing decision, and don't invent the answer. In `AUTO_MODE`, return `BLOCKED:` with the missing decision for the external orchestrator.

**Phantom-scope findings** (from sub-agent `PHANTOM_SCOPE` return summaries): sub-agents only saw plan-level sources, so first re-check each finding against `prd.md` – criteria that trace to a PRD outcome are **not** phantom scope (suppress). For confirmed phantom scope: remove the unsourced Success Criterion, or amend plan/PRD to justify it. Treat confirmed phantom scope as MEDIUM severity by default; upgrade to HIGH when it drives significant implementation work or introduces new dependencies.

After fixes, re-read changed FIS files and re-walk affected PRD flows.

**Gate**: Cross-cutting review complete; CRITICAL/HIGH issues and confirmed phantom scope resolved; FIS files updated


## OUTPUT

```
OUTPUT_DIR/
├── prd.md     # Product Requirements Document (carried in, not modified)
├── plan.json  # Implementation plan: typed manifest per plan-schema.md
└── s0N-*.md   # FIS files – one per story, one story per FIS
```

A legacy `plan.md` (if one was migrated in Step 1) is left untouched for the user to delete; downstream consumers ignore it.

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
4. **Initialize project state** (if not already tracking): Create the `State` document via the `andthen:init` skill.


## FAILURE HANDLING

- **Individual spec failure** → log and continue. Report in summary.
- **>50% of specs fail** → pause this run and return a failure summary with the blocking details.
- **Cross-cutting review sub-agent fails** → warn user; specs are usable but unvalidated for inter-story consistency.
