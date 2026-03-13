---
description: Executes an entire implementation plan through an Agent Team pipeline (spec → exec-spec → review-gap per story)
argument-hint: <path-to-plan-directory>
---

# Execute Plan with Agent Team Pipeline

Execute ALL stories in an implementation plan (from `/andthen:plan`) through a parallelized Agent Team pipeline: **spec → exec-spec → review-gap** per story.

**Uses Agent Teams** — Falls back to sequential execution (manual per-story loop) if Teams unavailable.


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
- **Agent Team for pipeline** — use Agent Teams for parallel story execution
- **Per-story pipeline**: spec → exec-spec → review-gap (with fix loop)

### Orchestrator Role
**You are the orchestrator.** Your job is to:
- Parse the plan and extract stories, phases, dependencies, parallel markers
- Size and create the Agent Team
- Create pipeline tasks with correct dependency chains
- Monitor progress via TaskList and coordinate agents
- Handle failures and escalate when needed
- Run final verification after all stories complete

**You do NOT:**
- Write implementation code directly
- Let your context get bloated with implementation details
- Skip final verification due to context exhaustion


## Workflow

### Step 1: Check Agent Teams Availability

Verify Agent Teams are available by checking that the `TeamCreate` tool exists in your available tools.

If the `TeamCreate` tool is NOT available (experimental feature not enabled):
- Inform user that exec-plan requires Agent Teams (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`)
- Suggest manual alternative: execute stories sequentially with `/andthen:spec` → `/andthen:exec-spec` → `/andthen:review-gap` per story
- Exit

**Gate**: Agent Teams confirmed available


### Step 2: Parse Plan

1. Read `PLAN_DIR/plan.md`
2. If plan file missing, **STOP** and recommend `/andthen:plan` first
3. Extract:
   - **Stories**: ID, name, scope, acceptance criteria, dependencies
   - **Phases**: Phase groupings and execution order
   - **Parallel markers**: `[P]` flags for concurrent execution
   - **Dependencies**: Cross-story dependency graph
4. Build execution plan respecting phase ordering and dependency chains

**Gate**: Plan parsed and phases identified


### Step 3: Size Team

Scale team based on total story count:

| Plan Size | Stories | Spec Creators | Implementers | Reviewers | Total |
|---|---|---|---|---|---|
| Small | 1-4 | 1 | 1 | 1 | 3 |
| Medium | 5-10 | 2 | 2 | 2 | 6 |
| Large | 11+ | 3 | 3 | 2 | 8 |

**Gate**: Team sized based on story count


### Step 4: Create Team and Spawn Agents

**IMPORTANT — Use Agent Team tools, NOT regular sub-agents.**
You MUST use the `TeamCreate` tool. Do NOT use `Task` alone (without `team_name`).

**Required tool sequence:**
1. `TeamCreate` — Create the team (e.g., `team_name: "plan-pipeline"`)
2. `Task` with `team_name` param — Spawn each teammate INTO the team
3. `TaskCreate` — Create pipeline tasks per phase (in Step 5)
4. `TaskUpdate` — Set dependencies, assignments, track completion
5. `SendMessage` — Inter-agent coordination
6. `SendMessage(type: "shutdown_request")` — Graceful shutdown when done
7. `TeamDelete` — Clean up team resources

#### Agent Roles

**Spec Creators** — Claim `spec-{story_id}` tasks and run `/andthen:spec` with story scope as input. Output: FIS document.

**Implementers** — Claim `impl-{story_id}` tasks (blocked by corresponding spec task) and run `/andthen:exec-spec` on the generated FIS. Output: implemented story.

**Reviewers** — Claim `review-{story_id}` tasks (blocked by corresponding impl task) and run `/andthen:review-gap` per story. If issues found: fix them, then re-validate. **Max 2 fix attempts** — if issues persist after 2 rounds, escalate to the orchestrator via `SendMessage` instead of continuing the loop. Output: validated story.

Each agent loops: **claim task → execute → mark done → claim next**.

**Troubleshooter (on-demand)** — NOT spawned upfront. The orchestrator spawns a troubleshooter teammate only when an agent escalates an issue it cannot resolve (build failures, analysis errors, cross-story conflicts, persistent test failures, etc.). Uses `andthen:build-troubleshooter` agent type. Receives a `fix-{story_id}` task with the issue context from the escalating agent. Shut down after the issue is resolved.

#### Spawn Template

Use this as prompt context when spawning each teammate via `Task(team_name: "plan-pipeline", name: "<role-N>", ...)`:

```
Role: {Spec Creator | Implementer | Reviewer}
Team: plan-pipeline
Plan: {PLAN_DIR}/plan.md

Your workflow (loop until no tasks remain):
1. Check TaskList for available tasks matching your role ({spec-*|impl-*|review-*})
2. Claim an unblocked, unassigned task via TaskUpdate (set owner to your name)
3. Execute:
   - Spec Creator: Run /andthen:spec with story scope from plan. Save FIS to docs/specs/ (per spec.md convention)
   - Implementer: Run /andthen:exec-spec on the FIS for this story
   - Reviewer: Run /andthen:review-gap for this story. Fix any issues found, then re-validate (max 2 fix attempts — escalate to orchestrator if issues persist)
4. Mark task completed via TaskUpdate
5. Check TaskList for next available task
6. If no tasks available, notify orchestrator via SendMessage

Important:
- Wait for tasks to appear in `TaskList` before claiming work
- Read the Workflow Rules, Guardrails and Guidelines in CLAUDE.md before starting
- Follow existing codebase patterns
- For issues you cannot resolve yourself (build failures, analysis errors, persistent test failures, cross-story conflicts), escalate to orchestrator via SendMessage with full issue context — the orchestrator will spawn a dedicated troubleshooter
```

**Gate**: Team created and all agents spawned


### Step 5: Phase Loop

For each phase in the plan:

#### 5a. Create Pipeline Tasks

For each story in the current phase, create 3 tasks:
- `spec-{story_id}`: "Create FIS for {story_name}"
- `impl-{story_id}`: "Implement {story_name}"
- `review-{story_id}`: "Review and validate {story_name}"

#### 5b. Set Dependencies

Use `TaskUpdate(addBlockedBy)`:
- `impl-{story_id}` blocked by `spec-{story_id}`
- `review-{story_id}` blocked by `impl-{story_id}`
- Cross-story dependencies from plan: if S05 depends on S03, then `spec-S05` blocked by `review-S03`

#### 5c. Monitor Progress

- Poll `TaskList` periodically until all review tasks for the current phase are complete
- Handle agent messages (failures, questions, status updates)

#### 5d. Update Plan

After each story's pipeline completes (spec → exec-spec → review), update `plan.md`:
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
  spec-S01 → impl-S01 → review-S01 → spec-S02 → impl-S02 → review-S02

Phase 2 (Parallel [P]): S03[P], S04[P], S05 (depends on S03)
  spec-S03 → impl-S03 → review-S03 → spec-S05 → impl-S05 → review-S05
  spec-S04 → impl-S04 → review-S04   (parallel with S03)
```

**Gate**: All phases complete, all stories implemented and reviewed


### Step 6: Final Verification

**Orchestrator performs directly** (not delegated):

1. Run build — verify it succeeds
2. Run tests — verify all pass
3. Review overall integration across stories
4. Include verification evidence in completion summary:
   - **Build**: exit code or success/failure status
   - **Tests**: pass/fail counts (e.g., "42/42 pass")
   - **Linting/types**: error and warning counts

**Gate**: Build, tests, and integration verification all pass


### Step 7: Documentation Update

Spawn a **general-purpose sub-agent** _(if supported by your coding agent)_ to update project documentation. Scope the update to:
- **README**: reflect any new features, changed APIs, or updated setup steps from the implementation
- **CHANGELOG**: add entries for all implemented stories (following existing changelog format)
- **Affected docs**: update any documentation files directly referenced or impacted by the plan's changes

**Gate**: Documentation updated


### Step 8: Clean Up

1. Use `SendMessage(type: "shutdown_request")` for each teammate
2. Wait for shutdown confirmations
3. Use `TeamDelete` to remove team and task files


## Failure Handling

- **Agent reports failure** via `SendMessage` → orchestrator spawns an **on-demand Troubleshooter** teammate (`andthen:build-troubleshooter`) with issue context → creates a `fix-{story_id}` task → troubleshooter diagnoses and fixes → shuts down troubleshooter after resolution → escalates to user only if troubleshooter also fails
- **Dependent stories stay blocked** when a predecessor fails
- **If >50% of a phase fails** → pause execution, notify user with failure summary


## Fallback: No Agent Teams

If Agent Teams unavailable (Step 1 check fails), suggest the manual equivalent:

```bash
# For each story in plan order:
/andthen:spec "S01: [Story Name]"
/andthen:exec-spec
/andthen:review-gap
# ... repeat for each story
```
