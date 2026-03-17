---
name: exec-plan
description: Executes an entire implementation plan through a pipeline (spec → exec-spec → review-gap per story)
argument-hint: <path-to-plan-directory>
---

# Execute Plan

Execute ALL stories in an implementation plan (from `/andthen:plan`) through a pipeline: **spec → exec-spec → review-gap** per story.

Uses **parallel sub-agents** _(if supported by your coding agent)_ for concurrent story execution, otherwise executes stories sequentially.


## Variables
PLAN_DIR: $ARGUMENTS


## Usage

```
/exec-plan PLAN_DIR="path/to/plan"
```


## Instructions

Make sure `PLAN_DIR` is provided — otherwise **STOP** immediately and ask the user to provide the path to the plan directory.

### Core Rules
- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails** (absolute must-follow rules)
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Complete Implementation**: All stories in plan must be implemented
- **Plan is source of truth** — follow phase ordering, dependencies, and parallel markers exactly
- **Per-story pipeline**: spec → exec-spec → review-gap (with fix loop)

### Orchestrator Role
**You are the orchestrator.** Your job is to:
- Parse the plan and extract stories, phases, dependencies, parallel markers
- Execute the per-story pipeline (delegating to sub-agents when possible)
- Track progress and update the plan as stories complete
- Handle failures and escalate when needed
- Run final verification after all stories complete

**You do NOT:**
- Write implementation code directly
- Let your context get bloated with implementation details
- Skip final verification due to context exhaustion


## Workflow

### Step 1: Parse Plan

1. Read `PLAN_DIR/plan.md`
2. If plan file missing, **STOP** and recommend `/andthen:plan` first
3. Extract:
   - **Stories**: ID, name, scope, acceptance criteria, dependencies
   - **Phases**: Phase groupings and execution order
   - **Parallel markers**: `[P]` flags for concurrent execution
   - **Dependencies**: Cross-story dependency graph
   - **Waves**: Wave assignments per story (W1, W2, W3...) if present in the plan
4. Build execution plan respecting phase ordering and dependency chains

**Gate**: Plan parsed and phases identified


### Step 2: Phase Loop

For each phase in the plan:

#### 2a. Identify Stories for This Phase

For each story in the current phase:

1. **Check for existing FIS** — Look for a FIS path in the story's `**FIS**` field in `plan.md`, or search the spec output directory (typically `docs/specs/`, or as configured in your project's Document Index) for a matching spec file. If a valid FIS already exists, skip the spec step for that story.

2. Determine execution approach:
   - Stories marked `[P]` with no cross-dependencies → can run in parallel
   - Stories with dependencies → must wait for predecessors to complete

#### 2b. Execute Story Pipelines

For each story (or group of parallel stories), run the three-stage pipeline:

**Stage 1 — Spec** _(skip if FIS already exists)_:
Run `/andthen:spec` with story scope as input. Output: FIS document in `docs/specs/`.

**Stage 2 — Implement**:
Run `/andthen:exec-spec` on the FIS for this story. Output: implemented story.

**Stage 3 — Review**:
Run `/andthen:review-gap` for this story. If issues found: fix them, then re-validate. **Max 2 fix attempts** — if issues persist after 2 rounds, escalate to the user.

> **Note — nested loops**: When `exec-spec` runs internally (Stage 2), its TV04 remediation loop handles *implementation-level* issues (code review, tests, visual validation) with a 3-cycle cap. The exec-plan review-gap loop here handles *integration and gap-level* issues across stories. These are complementary — exec-spec fixes code before exec-plan validates requirements.

#### Wave-Based Execution (within each phase)
If stories have wave assignments (W1, W2, etc.) from the plan:
1. Execute all W1 stories in parallel (these have no dependencies)
2. After W1 completes, execute all W2 stories in parallel
3. Continue through remaining waves
All stories in the same wave run in parallel (waves subsume [P] markers).

If no wave assignments present, fall back to the [P] marker
and dependency-based approach below.

**Parallelism strategy** — Use **parallel sub-agents** _(if supported by your coding agent)_ for independent `[P]` stories:
- Spawn one sub-agent per independent story pipeline (spec → exec-spec → review-gap)
- Each sub-agent runs the full three-stage pipeline for its story
- Use `isolation: "worktree"` for parallel sub-agents to avoid file conflicts. If worktree isolation is not available, execute parallel stories sequentially to avoid file conflicts
- If sub-agents not available, execute stories sequentially

**Sub-agent prompt template** for parallel story execution:
```
Execute the full pipeline for story {story_id}: {story_name}
Plan: {PLAN_DIR}/plan.md

Pipeline:
1. Spec: Check if FIS exists at {fis_path}. If not, run /andthen:spec with this scope: {story_scope}
2. Implement: Run /andthen:exec-spec on the FIS
3. Review: Run /andthen:review-gap. Fix issues (max 2 attempts), then report results.

Important:
- Read the Workflow Rules, Guardrails and Guidelines in CLAUDE.md before starting
- Follow existing codebase patterns
- Report back: success/failure, FIS path, any issues encountered
```

**Model assignment** — When spawning sub-agents, use `model: "opus"` for spec-only sub-agents (Stage 1 alone), and `model: "sonnet"` for implementation and review sub-agents. When a single sub-agent runs the full pipeline for a story, use `model: "opus"` (spec quality is the highest-leverage factor).

**When to split stages vs. full-pipeline sub-agents**: For plans with 4+ stories, prefer splitting stages across separate sub-agents to enable parallelism (e.g., spec agent finishes S01 and moves to S02 while impl agent starts S01). For small plans (1-3 stories), a single opus sub-agent per story running the full pipeline is simpler and avoids coordination overhead.

#### 2c. Update Plan

After each story's pipeline completes (spec → exec-spec → review-gap), update `plan.md` (consider using the `ops` skill for standardized status updates):
- Set the story's **Status** field to `Done`
- Set the story's **FIS** field to the generated spec path (e.g. `**FIS**: docs/specs/story-name.md`)
- Check off completed acceptance criteria checkboxes (`- [ ]` → `- [x]`)
- Update the Story Catalog table: set the story's Status column to `Done`

Also update each completed FIS file:
- Mark all task checkboxes as checked (`- [x]`)
- Mark success criteria and Final Validation Checklist items as checked

Move to next phase only after ALL stories in current phase are complete and plan is updated.

**Gate**: All stories in current phase completed and verified

#### Pipeline Flow Example

```
Phase 1 (Sequential): S01 → S02
  spec-S01 → impl-S01 → review-S01 → spec-S02 → impl-S02 → review-S02

Phase 2 (Parallel [P]): S03[P], S04[P], S05 (depends on S03)
  S03 pipeline ──────────────────────→ S05 pipeline
  S04 pipeline (parallel with S03)
```

**Gate**: All phases complete, all stories implemented and reviewed


### Step 3: Final Verification

**Orchestrator performs directly** (not delegated):

1. Run build — verify it succeeds
2. Run tests — verify all pass
3. Review overall integration across stories
4. Include verification evidence in completion summary:
   - **Build**: exit code or success/failure status
   - **Tests**: pass/fail counts (e.g., "42/42 pass")
   - **Linting/types**: error and warning counts

**Gate**: Build, tests, and integration verification all pass


### Step 4: Documentation Update

Spawn a **general-purpose sub-agent** _(if supported by your coding agent)_ to update project documentation. Scope the update to:
- **README**: reflect any new features, changed APIs, or updated setup steps from the implementation
- **CHANGELOG**: add entries for all implemented stories (following existing changelog format)
- **Affected docs**: update any documentation files directly referenced or impacted by the plan's changes

**Gate**: Documentation updated


## Failure Handling

- **Story pipeline fails** → attempt fix (max 2 rounds via review-gap loop). If unresolvable, use `andthen:build-troubleshooter` sub-agent _(if supported)_ for diagnosis. Escalate to user only if troubleshooter also fails.
- **Dependent stories stay blocked** when a predecessor fails
- **If >50% of a phase fails** → pause execution, notify user with failure summary


## Completion

When all phases are complete, print a summary including: stories completed, total phases, verification results (build/test status), and the path to the updated `PLAN_DIR/plan.md`.
