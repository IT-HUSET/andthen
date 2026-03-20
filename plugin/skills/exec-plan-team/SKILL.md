---
description: Executes an implementation plan through an Agent Team pipeline with inter-agent coordination (requires Agent Teams)
argument-hint: <path-to-plan-directory>
---

# Execute Plan (Agent Teams)

Execute ALL stories in an implementation plan (from `andthen:plan`) through a parallelized pipeline: parallel **spec** generation (sub-agents), then Agent Team **exec-spec → review-gap** per story.

**Requires Agent Teams** — Falls back to sequential execution (manual per-story loop) if Teams unavailable.


## VARIABLES
PLAN_DIR: $ARGUMENTS


## USAGE

```
/exec-plan-team PLAN_DIR="path/to/plan"
```


## INSTRUCTIONS

Make sure `PLAN_DIR` is provided — otherwise **STOP** immediately and ask the user to provide the path to the plan directory.

### Core Rules
- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails** (absolute must-follow rules)
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Complete Implementation**: All stories in plan must be implemented
- **Plan is source of truth** — follow phase ordering, dependencies, and parallel markers exactly
- **Pre-generate specs** — run parallel sub-agents for spec generation before starting the Agent Team
- **Agent Team for impl + review** — use Agent Teams for parallel implementation and review
- **Per-story pipeline**: spec (sub-agent) → exec-spec → review-gap (with fix loop)

### Orchestrator Role
**You are the orchestrator.** Your job is to:
- Parse the plan and extract stories, phases, dependencies, parallel markers
- Generate specs for each phase using parallel sub-agents (before team pipeline)
- Size and create the Agent Team for implementation + review
- Create pipeline tasks with correct dependency chains
- Monitor progress via the task list and coordinate agents
- Handle failures and escalate when needed
- Run final verification after all stories complete

**You do NOT:**
- Write implementation code directly
- Let your context get bloated with implementation details
- Skip final verification due to context exhaustion


## GOTCHAS
- Executing stories out of wave order when there are dependencies
- Starting implementation before all specs for the current phase are generated
- Not running review-gap after completing a wave
- Agent Teams feature flag not enabled — check for CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS
- Not spawning troubleshooter on escalation


## WORKFLOW

### Step 1: Check Agent Teams Availability

Verify Agent Teams are available by checking that team creation tools exist in your available tools (e.g. `TeamCreate`).

If Agent Team tools are NOT available (experimental feature not enabled):
- Suggest using `andthen:exec-plan` instead (portable version that works without Agent Teams)
- If user specifically wants Agent Teams, inform them it requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Exit

**Gate**: Agent Teams confirmed available


### Step 2: Parse Plan

1. Read `PLAN_DIR/plan.md`
2. If plan file missing, **STOP** and recommend `andthen:plan` first
3. Extract:
   - **Stories**: ID, name, scope, acceptance criteria, dependencies
   - **Phases**: Phase groupings and execution order
   - **Parallel markers**: `[P]` flags for concurrent execution
   - **Dependencies**: Cross-story dependency graph
   - **Waves**: Wave assignments per story (W1, W2, W3...) if present in the plan
4. Build execution plan respecting phase ordering and dependency chains

**Gate**: Plan parsed and phases identified


### Step 3: Generate Specs (Parallel Sub-Agents)

Before setting up the Agent Team, pre-generate all FIS documents for the current phase using parallel sub-agents. Specs produce documentation (low conflict risk), so they can safely run in parallel without worktree isolation.

> **This step repeats for each phase** — generate specs for Phase N stories before starting the Agent Team pipeline for that phase (see Step 6).

For each story in the current phase that does **not** already have a FIS:

1. **Check for existing FIS** — Look for a FIS path in the story's `**FIS**` field in `plan.md`, or search the spec output directory (typically `docs/specs/`, or as configured in your project's Document Index). If a valid FIS exists, skip that story.

2. **Spawn parallel sub-agents** — One opus sub-agent per story needing a spec. Each sub-agent runs `andthen:spec` with the story scope as input.

**Sub-agent prompt template** for spec generation:
```
Create a Feature Implementation Specification for story {story_id}: {story_name}
Plan: {PLAN_DIR}/plan.md
Story scope: {story_scope}

Run andthen:spec with the story scope above.
Read the Workflow Rules, Guardrails and Guidelines in CLAUDE.md before starting.
Save the FIS to docs/specs/ (per spec convention).
Report back: success/failure, FIS path.
```

**Model assignment**: Use `model: "opus"` for all spec sub-agents (deep reasoning is the highest-leverage factor for spec quality).

3. **Wait for all spec sub-agents to complete** for the current phase.
4. **Update plan.md** — Set each story's `**FIS**` field to the generated spec path.

**Gate**: All stories in current phase have FIS documents


### Step 4: Size Team

Scale team based on total story count (specs are pre-generated before the team starts):

| Plan Size | Stories | Implementers | Reviewers | Total |
|---|---|---|---|---|
| Small | 1-4 | 1 | 1 | 2 |
| Medium | 5-10 | 2 | 2 | 4 |
| Large | 11+ | 3 | 2 | 5 |

**Gate**: Team sized based on story count


### Step 5: Create Team and Spawn Agents

**IMPORTANT — Use Agent Teams, NOT regular sub-agents.**
Teammates must be spawned into the team (with `team_name` and `name`) so they share a task list and can message each other. Regular sub-agents are isolated and cannot coordinate.

**Workflow:**
1. Create the team (e.g., name: `"plan-pipeline"`)
2. Spawn each teammate into the team (with `team_name`, `name`, and `model`)
3. Create pipeline tasks per phase (in Step 6)
4. Set task dependencies, assignments, and track completion
5. Use inter-agent messaging for coordination
6. Send shutdown requests when done
7. Delete the team to clean up resources

#### Agent Roles and Models

| Role | Model | Rationale |
|---|---|---|
| Implementer | `sonnet` | Fast, capable execution of well-defined specs |
| Reviewer | `sonnet` | Efficient validation and fix loops |
| Troubleshooter | `sonnet` | Fast diagnosis and targeted fixes |

> **Note**: Spec generation is handled by parallel sub-agents _before_ the Agent Team starts (see Step 3). The team only handles implementation and review.

**Implementers** (`model: "sonnet"`) — Claim `impl-{story_id}` tasks and run `andthen:exec-spec` on the pre-generated FIS. Output: implemented story.

**Reviewers** (`model: "sonnet"`) — Claim `review-{story_id}` tasks (blocked by corresponding impl task) and run `andthen:review-gap` per story. If issues found: fix them, then re-validate. **Max 2 fix attempts** — if issues persist after 2 rounds, escalate to the orchestrator via message instead of continuing the loop. Output: validated story.

Each agent loops: **claim task → execute → mark done → claim next**.

**Troubleshooter (on-demand)** (`model: "sonnet"`) — NOT spawned upfront. The orchestrator spawns a troubleshooter teammate only when an agent escalates an issue it cannot resolve (build failures, analysis errors, cross-story conflicts, persistent test failures, etc.). Uses `andthen:build-troubleshooter` agent type. Receives a `fix-{story_id}` task with the issue context from the escalating agent. Shut down after the issue is resolved.

#### Spawn Template

Use this as prompt context when spawning each teammate into the team (with `team_name: "plan-pipeline"`, `name: "<role-N>"`, and `model: "sonnet"`).

```
Role: {Implementer | Reviewer}
Team: plan-pipeline
Plan: {PLAN_DIR}/plan.md

Your workflow (loop until no tasks remain):
1. Check the task list for available tasks matching your role ({impl-*|review-*})
2. Claim an unblocked, unassigned task (set owner to your name)
3. Execute:
   - Implementer: Run andthen:exec-spec on the FIS for this story
   - Reviewer: Run andthen:review-gap for this story. Fix any issues found, then re-validate (max 2 fix attempts — escalate to orchestrator if issues persist)
4. Mark task completed
5. Check the task list for next available task
6. If no tasks available, notify orchestrator via message

Important:
- Wait for tasks to appear in the task list before claiming work
- Read the Workflow Rules, Guardrails and Guidelines in CLAUDE.md before starting
- Follow existing codebase patterns
- For issues you cannot resolve yourself (build failures, analysis errors, persistent test failures, cross-story conflicts), escalate to orchestrator via message with full issue context — the orchestrator will spawn a dedicated troubleshooter
```

**Gate**: Team created and all agents spawned


### Step 6: Phase Loop

For each phase in the plan:

#### 6a. Generate Specs for This Phase

Run Step 3 (Generate Specs) for the current phase's stories. All FIS documents must exist before creating implementation tasks.

#### 6b. Create Pipeline Tasks

For each story in the current phase, create tasks:
- `impl-{story_id}`: "Implement {story_name}" — immediately unblocked (FIS already exists from Step 3/6a)
- `review-{story_id}`: "Review and validate {story_name}"

**Wave-based task creation** (if waves present in plan):
- Group story tasks by wave within each phase
- W1 story tasks are immediately unblocked (no wave predecessors)
- W2 story tasks are blocked by completion of all W1 review tasks
- W3+ story tasks are blocked by completion of all previous wave review tasks
- This simplifies dependency setup: wave ordering replaces per-story dependency chains

#### 6c. Set Dependencies

Set task dependencies (blocked-by):
- `review-{story_id}` blocked by `impl-{story_id}`
- Cross-story dependencies from plan: if S05 depends on S03, then `impl-S05` blocked by `review-S03`

#### 6d. Monitor Progress

- Poll the task list periodically until all review tasks for the current phase are complete
- Handle agent messages (failures, questions, status updates)
- Track completion by wave within each phase — all stories in wave N must complete before wave N+1 tasks are unblocked

#### 6e. Update Plan

After each story's pipeline completes (exec-spec → review-gap), update `plan.md`:
- Set the story's **Status** field to `Done`
- Set the story's **FIS** field to the generated spec path (e.g. `**FIS**: docs/specs/story-name.md`)
- Check off completed acceptance criteria checkboxes (`- [ ]` → `- [x]`)
- Update the Story Catalog table: set the story's Status column to `Done`

Also update each completed FIS file:
- Mark all task checkboxes as checked (`- [x]`)
- Mark success criteria and Final Validation Checklist items as checked

Move to next phase only after ALL stories in current phase are complete and plan is updated.

**Create Phase N+1 tasks only after Phase N is fully complete.**

**Gate**: All stories in current phase completed and verified

#### Pipeline Flow Example

```
Phase 1 (Sequential): S01 → S02
  [spec-S01, spec-S02 in parallel] → impl-S01 → review-S01 → impl-S02 → review-S02

Phase 2 (Parallel [P]): S03[P], S04[P], S05 (depends on S03)
  [spec-S03, spec-S04, spec-S05 in parallel]
  impl-S03 → review-S03 → impl-S05 → review-S05
  impl-S04 → review-S04   (parallel with S03)
```

**Gate**: All phases complete, all stories implemented and reviewed


### Step 7: Final Verification

**Orchestrator performs directly** (not delegated):

1. Run build — verify it succeeds
2. Run tests — verify all pass
3. Review overall integration across stories
4. Include verification evidence in completion summary:
   - **Build**: exit code or success/failure status
   - **Tests**: pass/fail counts (e.g., "42/42 pass")
   - **Linting/types**: error and warning counts

**Gate**: Build, tests, and integration verification all pass


### Step 8: Documentation Update

Spawn a **general-purpose sub-agent** _(if supported by your coding agent)_ to update project documentation. Scope the update to:
- **README**: reflect any new features, changed APIs, or updated setup steps from the implementation
- **CHANGELOG**: add entries for all implemented stories (following existing changelog format)
- **Affected docs**: update any documentation files directly referenced or impacted by the plan's changes

**Gate**: Documentation updated


### Step 9: Clean Up

1. Send shutdown requests to each teammate
2. Wait for shutdown confirmations
3. Delete the team to remove team and task files


## FAILURE HANDLING

- **Agent reports failure** via message → orchestrator spawns an **on-demand Troubleshooter** teammate (`andthen:build-troubleshooter`) with issue context → creates a `fix-{story_id}` task → troubleshooter diagnoses and fixes → shuts down troubleshooter after resolution → escalates to user only if troubleshooter also fails
- **Dependent stories stay blocked** when a predecessor fails
- **If >50% of a phase fails** → pause execution, notify user with failure summary


## COMPLETION

When all phases are complete, print a summary including: stories completed, total phases, verification results (build/test status), and the path to the updated `PLAN_DIR/plan.md`.


## FALLBACK: NO AGENT TEAMS

If Agent Teams unavailable (Step 1 check fails), suggest the manual equivalent:

```bash
# For each story in plan order:
andthen:spec "S01: [Story Name]"
andthen:exec-spec
andthen:review-gap
# ... repeat for each story
```
