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
- **Plan is source of truth** – follow wave ordering and dependencies exactly
- **Respect wave ordering** – complete all specs in wave N before starting wave N+1 (later stories may depend on earlier stories' architectural decisions)
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
- Write specs directly (delegate to sub-agents running `andthen:spec`)
- Write implementation code
- Let your context get bloated with spec content


## GOTCHAS
- Spawning specs for wave N+1 before wave N completes – later specs may need earlier architectural decisions
- Not updating `plan.md` FIS fields after spec generation – downstream skills (`exec-plan`, `exec-plan-team`) check this field to skip already-specced stories
- Over-parallelizing – more than 10 concurrent opus sub-agents causes filesystem I/O contention and degraded spec quality
- Skipping the cross-cutting review – individual specs can't detect overlapping scope, inconsistent ADRs, or missing integration seams between stories
- **Status updates get dropped when context is exhausted** – plan.md FIS field updates are GATES, not optional cleanup. Update immediately after each sub-wave completes


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


### Step 2: Wave Loop (Parallel Spec Creation)

For each wave in order (W1, then W2, then W3...):

#### 2a. Batch into Sub-Waves

If the current wave has more stories than MAX_PARALLEL, split into sub-waves of MAX_PARALLEL size.

#### 2b. Spawn Parallel Sub-Agents

For each sub-wave, spawn one opus sub-agent per story. Each sub-agent runs `/andthen:spec` (or `$andthen:spec` for Codex CLI).

**Sub-agent prompt template** (use `/` or `$` prefix depending on agent platform):
```
Create a Feature Implementation Specification for story {story_id}: {story_name}
Plan: {PLAN_DIR}/plan.md
Story scope: {story_scope}

Run: /andthen:spec story {story_id} of {PLAN_DIR}/plan.md
Read the Workflow Rules, Guardrails and Guidelines in CLAUDE.md before starting.
Report back: success/failure, FIS path.
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

**CRITICAL – do this immediately after each sub-wave completes, not as a batch at the end.**

For each successfully generated FIS:
- Set the story's `**FIS**` field in plan.md to the generated spec path
- Set the story's `**Status**` field to `Spec Ready` (if not already `In Progress` or `Done`)

**Gate**: All stories in current wave specced (or failed), plan.md updated, before proceeding to next wave

#### Wave Flow Example

```
Wave 1 (3 stories, MAX_PARALLEL=5):
  Sub-wave 1: spec-S01, spec-S02, spec-S03 (all parallel)
  → Update plan.md FIS fields

Wave 2 (7 stories, MAX_PARALLEL=5):
  Sub-wave 1: spec-S04, spec-S05, spec-S06, spec-S07, spec-S08 (parallel)
  → Update plan.md FIS fields
  Sub-wave 2: spec-S09, spec-S10 (parallel)
  → Update plan.md FIS fields

Wave 3 (1 story):
  Sub-wave 1: spec-S11
  → Update plan.md FIS fields
```

**Gate**: All waves complete, all plan.md FIS fields updated


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
