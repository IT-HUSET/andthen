---
description: Batch-create FIS specs for all stories in a plan with parallel sub-agents and cross-cutting review. Trigger on 'spec all stories', 'batch spec', 'pre-create specs'.
argument-hint: <path-to-plan-directory> [--stories S01,S03] [--phase N] [--max-parallel N] [--skip-review]
---

# Batch-Generate Specs for Plan


Batch-create Feature Implementation Specifications (FIS) for all stories in an implementation plan (from `andthen:plan`). Runs **parallel sub-agents** (one per story) in wave-ordered batches, then performs a **cross-cutting review** to catch inter-story inconsistencies.

Can be used:
- **Standalone** – pre-create and review all specs before execution (enables human review gate)
- **Delegated** – called by `andthen:exec-plan` or `andthen:exec-plan-team` to handle their spec-generation phase


## VARIABLES

PLAN_DIR: $ARGUMENTS

### Optional Flags
- `--stories S01,S03,...` → STORY_FILTER: Only generate specs for listed story IDs
- `--phase N` → PHASE_FILTER: Only generate specs for stories in phase N
- `--max-parallel N` → MAX_PARALLEL: Concurrency cap per sub-wave (default 5, max 10)
- `--skip-review` → SKIP_REVIEW: Skip the cross-cutting review step


## USAGE

```
/spec-plan path/to/plan                          # All stories
/spec-plan path/to/plan --phase 1                # Phase 1 only
/spec-plan path/to/plan --stories S01,S03,S05    # Specific stories
/spec-plan path/to/plan --max-parallel 8         # Higher concurrency
/spec-plan path/to/plan --skip-review            # Skip cross-cutting review
```


## INSTRUCTIONS

Make sure `PLAN_DIR` is provided – otherwise **STOP** immediately and ask the user to provide the path to the plan directory.

### Core Rules
- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work
- **Spec generation only** – no code changes, commits, or modifications during execution of this command
- **Plan is source of truth** — story scope, acceptance criteria, and dependencies come from the plan
- **Skip existing specs** – if a story already has a valid FIS (path in `**FIS**` field), skip it
- **Read project learnings** – If `LEARNINGS.md` exists (check Project Document Index for location), read it before starting

### Orchestrator Role
**You are the orchestrator.** Parse the plan, classify stories, spawn parallel sub-agents for STANDARD/COMPOSITE specs, write THIN specs directly, update plan.md after each sub-wave, and run cross-cutting review. You do NOT write STANDARD or COMPOSITE specs directly, write code, or let your context fill with spec content.


## GOTCHAS
- Spawning specs for stories with unresolved spec-time dependencies before the producing story's spec completes — check the research brief for pre-resolved decisions; if covered, parallelization is safe
- Not updating `plan.md` FIS fields after spec generation — downstream skills check this field to skip already-specced stories
- Over-parallelizing – more than 10 concurrent sub-agents causes I/O contention and degraded spec quality
- Skipping cross-cutting review — individual specs can't detect overlapping scope, inconsistent ADRs, or missing integration seams
- **Research brief becomes stale if plan changes** — re-run Step 1.5 before generating new specs after plan edits
- **Status updates get dropped when context is exhausted** — plan.md FIS field updates are GATES, not optional cleanup. Update immediately after each sub-wave


## WORKFLOW

### Step 1: Parse Plan

1. Read `PLAN_DIR/plan.md`. If missing, **STOP** and recommend `andthen:plan` first.
2. Extract: stories (ID, name, scope, acceptance criteria, dependencies), phases, wave assignments, dependency graph
3. Apply filters (STORY_FILTER, PHASE_FILTER); skip stories with existing FIS (check `**FIS**` field in plan.md — if file exists on disk, skip)
4. Build wave-ordered execution plan; set MAX_PARALLEL (default 5, max 10)

**Summary output**: Print stories to be specced, grouped by wave, and concurrency setting.

**Gate**: Plan parsed, stories identified, wave order established


### Step 1.5: Research Brief (One-Time Upfront Discovery)

Before spawning any spec sub-agents, do **all discovery and research work once** via up to 4 parallel sub-agents. This eliminates redundant codebase scanning, guideline reading, and architecture analysis each spec sub-agent would otherwise do independently.

**Sub-agent 1: Project Context** — Read CLAUDE.md guidelines; scan codebase structure (`tree -d`, `git ls-files | head -250`); identify conventions (naming, file organization, test patterns, abstractions); read LEARNINGS.md if it exists; identify tech stack and key framework versions. Output: dense summary of tech stack, conventions, key patterns, relevant guidelines, learnings.

**Sub-agent 2: Story-Scoped File Map** — For each story: search for related files/modules, identify existing patterns to follow (file:line references), flag files multiple stories will touch. Output: per-story file list with relevance notes plus a shared-files section.

**Sub-agent 3: Shared Architectural Decisions** — For each pair of dependent stories: identify the interface/contract between them (API shape, data types, naming, error handling); document the shared decision so both specs can reference it. Also identify: naming conventions that must be consistent, shared abstractions multiple stories will create/consume, API patterns that must be uniform. Output: numbered list of shared decisions with rationale, specific enough to reference in FIS success criteria.

**Sub-agent 4: External Research** _(only if stories reference external APIs/libraries needing documentation lookup)_ — For each external resource: look up current docs (use `andthen:documentation-lookup`), identify relevant patterns and known gotchas. Output: consolidated reference with one section per resource.

**Consolidation**: After all sub-agents complete, save to `{PLAN_DIR}/.research-brief.md`:

```markdown
# Research Brief: {Plan Name}
Generated: {date}

## Project Context
{Sub-agent 1 output}

## Story-Scoped File Map
{Sub-agent 2 output}

## Shared Architectural Decisions
{Sub-agent 3 output}

## External Research
{Sub-agent 4 output, or "No external research needed"}
```

**Gate**: Research brief saved to `{PLAN_DIR}/.research-brief.md`, covers all stories in scope


### Step 1.6: Story Classification & Grouping

After the research brief, classify each story — **fully automatic**, no user confirmation needed.

#### Classification Criteria

**THIN** — ALL conditions must be true:
- 2 or fewer acceptance criteria in the plan
- Scope description is 3 sentences or shorter
- Touches 3 or fewer files (per research brief file map)
- Story has no entries in the research brief's "Shared Architectural Decisions" section

**COMPOSITE** — ANY condition triggers grouping:
- **Linear dependency chain with shared files**: Stories form a chain (S01→S02 or longer) AND the research brief shows they share implementation files (exclude config/boilerplate like `package.json`, `tsconfig.json`, barrel index files)
- **Producer-consumer pair**: Research brief "Shared Architectural Decisions" lists an interface where Story A is the sole producer and Story B is the sole consumer
- **Same module/directory**: Stories primarily affect the same directory or module (per research brief file map), even without explicit dependencies
- **Phase cohesion**: All stories in a phase of ≤4 stories that share an architectural layer or concern
- **Maximum 5 stories per composite group** — split larger groups into multiple composites (split by dependency sub-chains, then by file overlap)

> **Precedence**: COMPOSITE > THIN > STANDARD. If a THIN-qualifying story participates in any COMPOSITE group, it joins the composite — not thin-specs.md. Classification uses data from the research brief (file maps, shared decisions), not subjective judgment. If the research brief doesn't provide clear signals, classify as STANDARD. Prefer COMPOSITE over STANDARD when grouping signals exist — fewer, richer FIS files produce better implementation coherence than many thin ones.

**STANDARD** — everything else (the default).

#### Classification → Spec Strategy

| Classification | Spec Strategy |
|----------------|---------------|
| THIN | Orchestrator collects all THIN stories into one FIS — no sub-agent needed |
| COMPOSITE | One spec sub-agent writes one FIS covering the entire group |
| STANDARD | One spec sub-agent per story, with research brief pre-loaded |

#### THIN: Collected FIS

All THIN stories in the current scope are collected into a **single** FIS file: `{PLAN_DIR}/thin-specs.md` (or `thin-specs-p{N}.md` when running with `--phase N`). The orchestrator writes this directly — no sub-agents needed. Use the standard FIS template (`${CLAUDE_PLUGIN_ROOT}/skills/spec/templates/fis-template.md`) and FIS authoring guidelines (`${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md`). Tag Success Criteria with source story IDs (e.g., `### S08: Story Name`) so acceptance gates can map criteria per story. Organize execution groups by story (tag each group with its source story ID) — same structure as COMPOSITE. Populate from plan story scope/criteria, Key Scenarios (if present), and research brief. Target: compact but complete.

After writing, update **ALL** THIN stories' **FIS** fields in plan.md to point to the thin-specs file and set **Status** to `Spec Ready`. The shared FIS path triggers existing shared-FIS dedup in exec-plan/exec-plan-team — exec-spec runs once, remaining stories skip to acceptance gate.

#### COMPOSITE: Multi-Story FIS

For COMPOSITE groups, one sub-agent covers all stories. Use concatenated IDs for the FIS output path: `{PLAN_DIR}/s01-s02-{feature-name}.md`. All constituent stories' **FIS** fields point to the same file; all get **Status** `Spec Ready`. Tag Success Criteria with source story IDs and organize execution groups by story (tag each group with its source story ID) — this enables per-story acceptance gate verification.

**Summary output**: Print classification results — counts per tier, which stories grouped into composites, which are thin, which are standard.

**Gate**: All stories classified, composites identified, thin-specs.md written


### Step 2: Parallel Spec Creation

> **THIN stories are already handled** — Step 1.6 wrote their FIS directly. Step 2 only handles STANDARD and COMPOSITE stories.

#### Wave Ordering

The research brief pre-resolves most inter-story architectural decisions. Default: all remaining STANDARD and COMPOSITE stories launch in parallel (up to MAX_PARALLEL). Exception: hold back a story if its spec depends on a decision the research brief could not pre-resolve — wait for the producing story's spec to complete first. Fallback: if the research brief is incomplete or unavailable, use strict wave ordering (W1 complete → W2).

Batch into sub-waves if story count exceeds MAX_PARALLEL.

#### Sub-Agent Prompts

Use a strong reasoning model (`model: "opus"`, `gpt-5.4`, or similar) for all spec sub-agents. Use `/andthen:spec` (or `$andthen:spec` for Codex CLI) prefix when invoking spec for individual stories outside the batch flow.

**STANDARD sub-agent** — provide:
- Story ID, name, scope, acceptance criteria, Key Scenarios (if present), dependencies
- References: FIS template (`${CLAUDE_PLUGIN_ROOT}/skills/spec/templates/fis-template.md`), authoring guidelines (`${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md`), research brief (`{PLAN_DIR}/.research-brief.md`)
- Instructions: read research brief for context and shared decisions; read FIS template and guidelines; generate FIS; run Plan-Spec Alignment Check and Self-Check from guidelines; save to `{PLAN_DIR}/{story-name}.md`; report back success/failure, FIS path, confidence score

**COMPOSITE sub-agent** — provide:
- All constituent stories (ID, name, scope, acceptance criteria, Key Scenarios if present)
- Same references as STANDARD
- Instructions: read research brief; generate ONE FIS covering all stories with execution groups organized by story (tag each group with its source story ID); run Plan-Spec Alignment Check for EACH story; run Self-Check; save to `{PLAN_DIR}/{composite-filename}.md`; report back success/failure, FIS path, confidence score

#### Wait, Collect, and Update Plan

Wait for all sub-agents in the current sub-wave to complete. Log any failures (continue with remaining stories — don't block the wave). Immediately after each sub-wave:

**REQUIRED GATE** — update plan.md for each successfully generated FIS:
- Set `**FIS**` field to the generated spec path
- Set `**Status**` field to `Spec Ready` (if not already `In Progress` or `Done`)
- COMPOSITE: set ALL constituent stories' fields

#### Spec Flow Example

```
10-story plan → After Step 1.6 classification:
  THIN: S07, S08, S10 → 1 file (thin-specs.md, written in Step 1.6)
  COMPOSITE: [S01+S02], [S04+S05+S06] → 2 files (one sub-agent each)
  STANDARD: S03, S09 → 2 files (one sub-agent each)
  Total: 5 FIS files instead of 10

Step 2 (MAX_PARALLEL=4):
  Sub-wave 1: spec-[S01+S02], spec-[S04+S05+S06], spec-S03, spec-S09 (parallel)
  → Update plan.md FIS fields (S01+S02 share composite, S04+S05+S06 share composite)
```

**Gate**: All specs complete, all plan.md FIS fields updated


### Step 3: Cross-Cutting Review

> **Skip this step if `--skip-review` flag is set.**

Delegate to a single opus sub-agent with all generated FIS paths. Provide: plan path, list of all FIS paths. The sub-agent should read ALL FIS files and the plan, then check for:

1. **Overlapping scope** – multiple stories modifying the same files or creating the same abstractions
2. **Inconsistent architectural decisions** – contradictory ADR choices across stories
3. **Missing integration seams** – Story B needs output Story A's spec doesn't produce
4. **Dependency gaps** – cross-story dependencies not reflected in FIS task ordering
5. **Inconsistent naming/patterns** – different conventions for similar operations or shared concerns
6. **Duplicate work** – same utility, component, or abstraction independently created in multiple stories
7. **Plan-vs-FIS alignment** – every plan acceptance criterion must be covered by FIS success criteria; flag any criterion silently narrowed without a scope note
8. **Intra-story scope contradictions** – items in "What We're NOT Doing" that block a success criterion
9. **Scenario gaps** – plan Key Scenario seeds not mapped to FIS scenarios; cross-story scenario dependencies (Story B's scenario assumes behavior from Story A that isn't covered)

Output per finding: severity (CRITICAL/HIGH/MEDIUM/LOW), stories affected, issue description, recommendation, FIS sections to update. Include a summary with total findings by severity, overall readiness (READY/NEEDS FIXES/BLOCKED), and list of FIS files needing updates.

**Gate**: Cross-cutting review complete, report received


### Step 4: Fix Issues

If the review found CRITICAL or HIGH severity issues, apply fixes to resolve inter-story inconsistencies. Use this heuristic: overlapping scope → clarify file ownership with cross-references; inconsistent ADRs → align on the most prevalent or architecturally sound choice; missing seams → add missing outputs to the producing story; naming inconsistencies → standardize on the most prevalent pattern; duplicate work → consolidate into the earliest story. After fixes, re-read changed FIS files to confirm consistency.

**When running standalone**: present the review report and proposed fixes to the user; ask for confirmation before modifying FIS files.

**When delegated** (by exec-plan or exec-plan-team): apply fixes automatically; report fixes back to calling orchestrator.

**Gate**: All CRITICAL and HIGH issues resolved, FIS files updated


## COMPLETION

Print a summary:
- **FIS files created**: count, with classification breakdown
- **Stories specced**: count and list with FIS paths (show shared paths)
- **Stories skipped**: (already had FIS)
- **Stories failed**: (if any, with error details)
- **Cross-cutting review**: findings count by severity, readiness assessment
- **Fixes applied**: list of FIS files modified
- **Readiness**: overall assessment for execution

```
Example output:

Spec Plan Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FIS files created: 5 (covering 8 stories)
  THIN: 1 collected file (3 stories)
  COMPOSITE: 2 files (5 stories)
  STANDARD: 2 files

Stories specced:  8 of 10 (2 already had FIS)
  S01, S02       → docs/specs/s01-s02-auth-flow.md (composite)
  S04, S05, S06  → docs/specs/s04-s05-s06-api-layer.md (composite)
  S03            → docs/specs/s03-user-dashboard.md
  S09            → docs/specs/s09-notifications.md
  S07, S08, S10  → docs/specs/thin-specs.md (collected)

Skipped (existing FIS): S04, S06

Cross-cutting review: 1 HIGH, 2 MEDIUM
  Fixed: aligned ADR for S03/S05 API patterns

Ready for execution.
```


## FAILURE HANDLING

- **Individual spec failure** → log and continue. Report in summary.
- **>50% of specs fail** → pause and notify user with failure details.
- **Cross-cutting review sub-agent fails** → warn user that cross-cutting review was skipped; specs are usable but unvalidated for inter-story consistency.
- **Fix step fails** → report unfixed issues to user. Specs are usable but may have inter-story inconsistencies that surface during execution.
