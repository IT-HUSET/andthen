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
- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails** (absolute must-follow rules)
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Spec generation only** – no code changes, commits, or modifications during execution of this command
- **Plan is source of truth** — story scope, acceptance criteria, and dependencies come from the plan
- **Relaxed wave ordering** — the research brief (Step 1.5) pre-resolves most inter-story architectural decisions, so stories can be specced in parallel regardless of wave assignment unless they have genuinely unresolvable spec-time dependencies (see Step 2). Falls back to strict wave ordering when the research brief is incomplete or unavailable
- **Skip existing specs** – if a story already has a valid FIS (path in `**FIS**` field), skip it
- **Read project learnings** – If `LEARNINGS.md` exists (check Project Document Index for location), read it before starting to avoid known traps and error patterns

### Orchestrator Role
**You are the orchestrator.** Your job is to:
- Parse the plan and determine which stories need specs
- Group stories into waves and manage concurrency
- Spawn parallel sub-agents for spec creation
- Track progress and update plan.md as specs are generated
- Run the cross-cutting review after all specs complete
- Fix inter-story inconsistencies found during review

**You do NOT:**
- Write STANDARD or COMPOSITE specs directly (delegate to sub-agents that generate FIS using the shared template and guidelines). Exception: THIN stories — the orchestrator writes minimal FIS directly (see Step 1.6)
- Write implementation code
- Let your context get bloated with spec content


## GOTCHAS
- Spawning specs for stories with unresolved spec-time dependencies before the producing story's spec completes — check the research brief for pre-resolved decisions; if the dependency is covered, parallelization is safe
- Not updating `plan.md` FIS fields after spec generation – downstream skills (`exec-plan`, `exec-plan-team`) check this field to skip already-specced stories
- Over-parallelizing – more than 10 concurrent opus sub-agents causes filesystem I/O contention and degraded spec quality
- Skipping the cross-cutting review — individual specs can't detect overlapping scope, inconsistent ADRs, or missing integration seams between stories
- **Research brief becomes stale if plan changes** — if the plan is modified after the research brief is generated, re-run Step 1.5 before generating new specs
- **Status updates get dropped when context is exhausted** — plan.md FIS field updates are GATES, not optional cleanup. Update immediately after each sub-wave completes


## WORKFLOW

### Step 1: Parse Plan

1. Read `PLAN_DIR/plan.md`
2. If plan file missing, **STOP** and recommend `andthen:plan` first
3. Extract:
   - **Stories**: ID, name, scope, acceptance criteria, dependencies
   - **Phases**: Phase groupings and execution order
   - **Waves**: Wave assignments per story (W1, W2, W3...) if present
   - **Dependencies**: Cross-story dependency graph
4. Apply filters:
   - If STORY_FILTER set: include only listed story IDs
   - If PHASE_FILTER set: include only stories in that phase
   - **Skip stories with existing FIS** – check the story's `**FIS**` field in plan.md for an existing file path. If the file exists on disk, skip that story.
5. Build wave-ordered execution plan from remaining stories
6. Determine MAX_PARALLEL (default 5, cap at 10)

**Summary output**: Print the stories that will be specced, grouped by wave, and the concurrency setting.

**Gate**: Plan parsed, stories identified, wave order established


### Step 1.5: Research Brief (One-Time Upfront Discovery)

Before spawning any spec sub-agents, do **all discovery and research work once** via parallel sub-agents. This eliminates the redundant codebase scanning, guideline reading, and architecture analysis that each spec sub-agent would otherwise do independently.

Spawn up to 4 parallel sub-agents (use the most capable model available):

**Sub-agent 1: Project Context**
```
Analyze the project for spec generation context.

1. Read CLAUDE.md / AGENTS.md guidelines (Foundational Rules, Development Guidelines, etc.)
2. Scan codebase structure: tree -d, git ls-files | head -250
3. Identify project conventions: naming patterns, file organization, test patterns, common abstractions
4. Read LEARNINGS.md (if exists, check Project Document Index) for traps and error patterns
5. Identify tech stack and key framework versions

Output a structured summary covering: tech stack, project conventions, key patterns, relevant guidelines, learnings.
Keep it dense — keywords and patterns, not prose.
```

**Sub-agent 2: Story-Scoped File Map**
```
For each story in the plan, identify relevant files in the codebase.

Plan: {PLAN_DIR}/plan.md
Stories: {list of story IDs and their scope descriptions}

For each story:
1. Search for files/modules related to the story's scope (grep for key terms, explore directories)
2. Identify existing patterns to follow (file:line references)
3. Flag files that multiple stories will touch (shared modification targets)

Output: per-story file list with relevance notes, plus a shared-files section listing files touched by 2+ stories.
```

**Sub-agent 3: Shared Architectural Decisions**
```
Analyze cross-story dependencies and pre-resolve shared architectural decisions.

Plan: {PLAN_DIR}/plan.md
Stories: {list of stories with scope, dependencies, acceptance criteria}

For each pair of dependent stories:
1. Identify the interface/contract between them (what the producing story must expose, what the consuming story needs)
2. Decide: API shape, data types, naming conventions, error handling patterns
3. Document the shared decision so both specs can reference it independently

Also identify:
- Naming conventions that must be consistent across stories
- Shared abstractions or utilities that multiple stories will create/consume
- API patterns (REST/GraphQL, error format, auth flow) that must be uniform

Output: numbered list of shared decisions with rationale. Each decision should be specific enough to be referenced by a FIS Success Criterion or task.
```

**Sub-agent 4: External Research** _(only spawn if stories reference external APIs, libraries, or frameworks that need documentation lookup)_
```
Batch external research for all stories in the plan.

Stories referencing external resources: {filtered list}

For each external resource:
1. Look up current documentation (use andthen:documentation-lookup)
2. Identify relevant API patterns, version-specific behavior, known gotchas
3. Consolidate findings — one entry per resource, not per story

Output: consolidated reference document with one section per external resource.
```

**Consolidation**: After all sub-agents complete, consolidate their outputs into `{PLAN_DIR}/.research-brief.md`. Structure:

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

After the research brief, classify each story into one of three tiers. This is **fully automatic** — no user confirmation needed.

#### Classification Criteria

**THIN** — ALL conditions must be true:
- 2 or fewer acceptance criteria in the plan
- Scope description is 3 sentences or shorter
- Touches 3 or fewer files (per research brief file map)
- Story has no entries in the research brief's "Shared Architectural Decisions" section (i.e., no cross-story interface decisions involve this story)

**COMPOSITE** — ANY condition triggers grouping:
- **Linear dependency chain with shared files**: Stories form a dependency chain (S01→S02 or S01→S02→S03) AND the research brief file map shows they share at least 50% of their relevant files
- **Producer-consumer pair**: The research brief's "Shared Architectural Decisions" lists an interface where Story A is the sole producer and Story B is the sole consumer (no other stories produce or consume that interface)
- **Maximum 3 stories per composite group** — if a chain is longer, split into multiple composites

> **Note**: Classification uses data from the research brief (file maps, shared decisions), not subjective judgment. If the research brief doesn't provide clear signals for a story, classify as STANDARD.

**STANDARD** — everything else (the default).

#### Classification → Spec Strategy

| Classification | Spec Strategy |
|----------------|---------------|
| THIN | Orchestrator writes minimal FIS directly — no sub-agent needed |
| COMPOSITE | One spec sub-agent writes one FIS covering the entire group |
| STANDARD | One spec sub-agent per story, with research brief pre-loaded |

#### THIN: Minimal FIS

For THIN stories, the orchestrator writes the FIS directly (no sub-agent) using the minimal template at [`${CLAUDE_PLUGIN_ROOT}/skills/spec/templates/fis-template-minimal.md`](../spec/templates/fis-template-minimal.md). Target: 30-60 lines. Populate from the plan story's scope/criteria and the research brief's file map, constraints, and architectural decisions.

After writing, update the story's **FIS** field in plan.md and set **Status** to `Spec Ready`.

#### COMPOSITE: Multi-Story FIS

For COMPOSITE groups, the sub-agent prompt combines all stories' scope and criteria:
- FIS output path uses concatenated IDs: `{PLAN_DIR}/s01-s02-{feature-name}.md`
- All constituent stories' **FIS** fields in plan.md point to the same file
- All stories get **Status** set to `Spec Ready`
- The FIS execution groups are organized by story (tag each group with its source story ID for traceability)

**Summary output**: Print the classification results — how many stories in each tier, which stories are grouped into composites, which are thin, which are standard.

**Gate**: All stories classified, composites identified, thin FIS documents written


### Step 2: Parallel Spec Creation

> **THIN stories are already handled** — Step 1.6 wrote their minimal FIS directly. Step 2 only handles STANDARD and COMPOSITE stories.

#### 2a. Determine Parallelism

The research brief (Step 1.5) pre-resolves most inter-story architectural decisions. This means spec-time wave ordering is largely unnecessary:

- **Default**: All remaining STANDARD and COMPOSITE stories launch in parallel (up to MAX_PARALLEL concurrent sub-agents)
- **Exception**: If a story's spec depends on a decision that could NOT be pre-resolved in the research brief (flagged during Step 1.5 Sub-agent 3), hold it back until the producing story's spec completes
- **Fallback**: If the research brief is incomplete or unavailable, fall back to strict wave ordering (W1 complete → W2)

Batch into sub-waves if the total story count exceeds MAX_PARALLEL.

#### 2b. Spawn Parallel Sub-Agents

For each sub-wave, spawn sub-agents by classification tier. Use `/` or `$` prefix depending on agent platform.

**THIN** (orchestrator writes directly, no sub-agent):
THIN stories were already written in Step 1.6 using the minimal template. Skip them here.

**STANDARD sub-agent prompt template**:
```
Generate a Feature Implementation Specification for story {story_id}: {story_name}

## Inputs
Plan: {PLAN_DIR}/plan.md
Story scope: {story_scope}
Acceptance criteria: {story_acceptance_criteria}
Dependencies: {story_dependencies}

## References
FIS template: ${CLAUDE_PLUGIN_ROOT}/skills/spec/templates/fis-template.md
Authoring guidelines: ${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md
Research brief: {PLAN_DIR}/.research-brief.md

## Instructions
1. Read the research brief for project context, relevant files, shared
   architectural decisions, and external references
2. Read the FIS template and authoring guidelines
3. Generate the FIS following the template structure and guidelines
4. Run the Plan-Spec Alignment Check and Self-Check from the guidelines
5. Save to: {PLAN_DIR}/{story-name}.md

Report back: success/failure, FIS path, confidence score.
```

**COMPOSITE sub-agent prompt template**:
```
Generate a single Feature Implementation Specification covering these stories:

## Stories
{for each story: ID, name, scope, acceptance criteria}

## Inputs
Plan: {PLAN_DIR}/plan.md
Combined acceptance criteria: all criteria from all constituent stories

## References
FIS template: ${CLAUDE_PLUGIN_ROOT}/skills/spec/templates/fis-template.md
Authoring guidelines: ${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md
Research brief: {PLAN_DIR}/.research-brief.md

## Instructions
1. Read the research brief for project context and shared decisions
2. Read the FIS template and authoring guidelines
3. Generate ONE FIS covering all stories. Organize execution groups by
   story (tag each group with its source story ID for traceability)
4. Run the Plan-Spec Alignment Check for EACH story's criteria
5. Run the Self-Check from the guidelines
6. Save to: {PLAN_DIR}/{composite-filename}.md

Report back: success/failure, FIS path, confidence score.
```

**Model assignment**: Use `model: "opus"` for all spec sub-agents (deep reasoning is the highest-leverage factor for spec quality).

#### 2c. Wait and Collect Results

Wait for all sub-agents in the current sub-wave to complete. Collect:
- FIS file paths (for successful specs)
- Failure details (for failed specs)

If a sub-agent fails:
- Log the failure with story ID and error details
- Continue with remaining stories (don't block the entire wave)
- Report failures in the completion summary

#### 2d. Update Plan (REQUIRED GATE)

**CRITICAL — do this immediately after each sub-wave completes, not as a batch at the end.**

For each successfully generated FIS:
- Set the story's `**FIS**` field in plan.md to the generated spec path
- Set the story's `**Status**` field to `Spec Ready` (if not already `In Progress` or `Done`)
- For COMPOSITE groups: set ALL constituent stories' `**FIS**` fields to the shared path AND set ALL their `**Status**` fields to `Spec Ready`

**Gate**: All stories specced (or failed), plan.md updated

#### Spec Flow Example

```
After Step 1.6 classification:
  THIN: S08, S10 (already written in Step 1.6)
  COMPOSITE: [S01+S02] (one sub-agent)
  STANDARD: S03, S04, S05, S06, S07, S09 (one sub-agent each)

Step 2 (MAX_PARALLEL=5):
  Sub-wave 1: spec-[S01+S02], spec-S03, spec-S04, spec-S05, spec-S06 (parallel)
  → Update plan.md FIS fields (S01, S02 both point to composite FIS)
  Sub-wave 2: spec-S07, spec-S09 (parallel)
  → Update plan.md FIS fields

Total: 7 sub-agents instead of 10 (thin stories handled directly, composite grouped)
```

**Gate**: All specs complete, all plan.md FIS fields updated


### Step 3: Cross-Cutting Review

> **Skip this step if `--skip-review` flag is set.**

After all specs are generated, run a cross-cutting review to catch inter-story issues that individual spec creation cannot detect.

**Delegate to a single opus sub-agent** with all generated FIS paths. This keeps the orchestrator's context clean.

**Review sub-agent prompt**:
```
Cross-cutting review of Feature Implementation Specifications.
Plan: {PLAN_DIR}/plan.md
FIS files to review:
{list of all FIS paths, one per line}

Read ALL FIS files and the plan. Then check for the following inter-story issues:

1. **Overlapping scope** – Multiple stories modifying the same files or creating the same abstractions. Flag conflicts and recommend which story should own each file.

2. **Inconsistent architectural decisions** – ADRs across stories that make contradictory choices (e.g., one story picks REST while another picks GraphQL for related endpoints). Recommend alignment.

3. **Missing integration seams** – Story B depends on output from Story A, but A's spec doesn't produce what B needs (missing exports, wrong interface shape, missing API endpoints).

4. **Dependency gaps** – Cross-story dependencies in the plan that aren't reflected in the FIS task ordering or scope.

5. **Inconsistent naming/patterns** – Stories using different naming conventions, different patterns for similar operations, or different approaches to shared concerns (error handling, logging, auth).

6. **Duplicate work** – Same utility, component, or abstraction independently created in multiple stories.

7. **Plan-vs-FIS alignment** – For each FIS, verify that every plan acceptance criterion is covered by the FIS Success Criteria. Flag any plan criterion that is not addressed, narrowed, or scoped down without a corresponding scope note in the FIS. This catches spec-layering gaps where the spec silently narrows what the plan promised.

8. **Intra-story scope contradictions** – Within each FIS, verify that items in "What We're NOT Doing" and "Constraints & Gotchas" do not prevent any Success Criterion from being met. For each exclusion, trace the data/flag path from requirement to runtime behavior. Flag contradictions where an exclusion blocks a necessary intermediate step.

Output format:
## Cross-Cutting Review Report

### Findings
For each issue found:
- **Severity**: CRITICAL / HIGH / MEDIUM / LOW
- **Stories affected**: S01, S03
- **Issue**: Description of the problem
- **Recommendation**: How to resolve it
- **FIS sections to update**: Specific sections in specific FIS files that need changes

### Summary
- Total findings by severity
- Overall readiness assessment: READY / NEEDS FIXES / BLOCKED
- List of FIS files that need updates

Report back: the full review report.
```

**Model assignment**: Use `model: "opus"` for the review sub-agent.

**Gate**: Cross-cutting review complete, report received


### Step 4: Fix Issues

If the cross-cutting review found CRITICAL or HIGH severity issues:

1. **Present findings to the user** (when running standalone) or **proceed to fix** (when delegated by exec-plan/exec-plan-team)
2. **Update affected FIS files** to resolve inconsistencies:
   - For overlapping scope: clarify file ownership, add cross-references between stories
   - For inconsistent ADRs: align on a single approach, update all affected FIS
   - For missing integration seams: add missing outputs to the producing story's FIS
   - For dependency gaps: add missing task dependencies
   - For naming inconsistencies: standardize on the most prevalent or most correct pattern
   - For duplicate work: consolidate into the earliest story, add references in later stories
   - For plan-vs-FIS misalignment: either expand FIS scope to cover the plan criterion, or update the plan criterion with a scope note explaining the narrowing
   - For intra-story scope contradictions: either remove the exclusion that blocks the success criterion, or revise the success criterion to be achievable within the stated scope
3. **Re-validate** – After fixes, do a quick re-read of changed FIS files to confirm consistency

**When running standalone** (user invoked `/spec-plan` directly):
- Present the review report and proposed fixes to the user
- Ask for confirmation before modifying FIS files
- User may want to review/edit specs manually before proceeding to execution

**When delegated** (called by `exec-plan` or `exec-plan-team`):
- Apply fixes automatically (the execution pipeline will validate further via review-gap)
- Report fixes made back to the calling orchestrator

**Gate**: All CRITICAL and HIGH issues resolved, FIS files updated


## COMPLETION

Print a summary including:
- **Stories specced**: count and list with FIS paths
- **Stories skipped**: (already had FIS)
- **Stories failed**: (if any, with error details)
- **Cross-cutting review**: findings count by severity, readiness assessment
- **Fixes applied**: list of FIS files modified during fix step
- **Readiness**: overall assessment for execution

```
Example output:

Spec Plan Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stories specced:  5 of 7 (2 already had FIS)
  S01 → docs/specs/s01-auth-middleware.md
  S03 → docs/specs/s03-user-dashboard.md
  S04 → docs/specs/s04-api-endpoints.md
  S05 → docs/specs/s05-data-migration.md
  S07 → docs/specs/s07-notification-service.md

Skipped (existing FIS): S02, S06

Cross-cutting review: 1 HIGH, 2 MEDIUM
  Fixed: aligned ADR for S03/S04 API patterns

Ready for execution.
```


## FAILURE HANDLING

- **Individual spec failure** → log and continue (don't block other stories). Report in summary.
- **>50% of specs fail** → pause and notify user with failure details.
- **Cross-cutting review sub-agent fails** → warn user that cross-cutting review was skipped, specs are still usable but unvalidated for inter-story consistency.
- **Fix step fails** → report unfixed issues to user. Specs are still usable but may have inter-story inconsistencies that surface during execution.
