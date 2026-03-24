---
description: Execute an implementation plan through an Agent Team pipeline with inter-agent coordination (requires Agent Teams)
argument-hint: <path-to-plan> [path-to-code-repo]
---

# Execute Plan (Agent Teams)


Execute ALL stories in an implementation plan (from `andthen:plan`) through a parallelized pipeline: **spec-plan** (parallel spec generation + cross-cutting review per phase), then Agent Team **exec-spec (worktree) → merge → review-gap (main)** per wave. Implementers work in **isolated git worktrees** to prevent file conflicts during parallel execution.

**Requires Agent Teams** – Falls back to sequential execution (manual per-story loop) if Teams unavailable.


## VARIABLES
PLAN_DIR: $0
CODE_DIR: $1


## USAGE

```
/exec-plan-team path/to/plan
/exec-plan-team path/to/plan path/to/code/repo
```

- First argument (`$0`): **PLAN_DIR** – path to the plan directory (required)
- Second argument (`$1`): **CODE_DIR** – path to the code repository (optional, auto-resolved if omitted)

Omit `CODE_DIR` for single-repo projects. **Provide it** when plan/specs live in a different repo than the code (e.g., a private specs repo alongside a public code repo).


## INSTRUCTIONS

Make sure `PLAN_DIR` is provided – otherwise **STOP** immediately and ask the user to provide the path to the plan directory.

### Resolve CODE_DIR

**Resolve CODE_DIR** (run before any other work):

1. If `CODE_DIR` was provided (second argument is non-empty): verify it is a git repository (`git -C {CODE_DIR} rev-parse --git-dir`). Resolve to absolute path.
2. If `CODE_DIR` was NOT provided (second argument is empty), **auto-detect**:
   a. Get the git root of PLAN_DIR: `git -C {PLAN_DIR} rev-parse --show-toplevel`
   b. Get the git root of CWD: `git rev-parse --show-toplevel`
   c. If they are the **same repo** → `CODE_DIR` = that git root (single-repo project)
   d. If they are **different repos** → `CODE_DIR` = CWD's git root (multi-repo: plan is in a separate repo from code)
3. Resolve `CODE_DIR` to an **absolute path** and use it throughout all remaining steps.
4. Log the resolved value: `"CODE_DIR resolved to: {CODE_DIR} (source: explicit | same-repo | multi-repo-auto)"`

**Multi-repo rules** (when CODE_DIR ≠ PLAN_DIR's git root):
- All `git worktree`, `git merge`, `git branch`, and `git checkout` operations target `CODE_DIR` – never the plan repo
- `EnterWorktree` must be called from `CODE_DIR` context – agents must verify their CWD is `CODE_DIR` before invoking it
- FIS paths passed to agents must be **absolute** (they reference files in the plan repo, but agents work in `CODE_DIR`)
- The plan repo is **read-only for agents** – only the orchestrator updates `plan.md` and FIS checkboxes
- Never create branches, worktrees, or commits in the plan repo

### Core Rules
- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails** (absolute must-follow rules)
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Complete Implementation**: All stories in plan must be implemented
- **Plan is source of truth** – follow phase ordering, dependencies, and parallel markers exactly
- **Pre-generate specs** – delegate to `andthen:spec-plan` per phase (handles parallelism, wave ordering, and cross-cutting review) before starting the Agent Team
- **Agent Team for impl + review** – use Agent Teams for parallel implementation and review
- **Worktree isolation** – implementers use `EnterWorktree` per task (in `CODE_DIR`) to prevent file conflicts during parallel execution
- **Pre-assign all tasks** – orchestrator assigns every task to a specific agent at creation time (no self-claiming)
- **Per-story pipeline**: spec-plan (per phase) → exec-spec (worktree) → merge → review-gap (main branch, with fix loop)

### Orchestrator Role
**You are the orchestrator.** Your job is to:
- Parse the plan and extract stories, phases, dependencies, parallel markers
- Delegate spec generation to `andthen:spec-plan` per phase (before team pipeline)
- Size and create the Agent Team for implementation + review
- Create pipeline tasks with correct dependency chains and **pre-assigned owners**
- Monitor progress via the task list and coordinate agents
- **Merge worktree branches** into main after each wave of implementations completes
- Handle failures and escalate when needed
- Run final verification after all stories complete

**You do NOT:**
- Write implementation code directly
- Let your context get bloated with implementation details
- Skip final verification due to context exhaustion


## GOTCHAS
- Executing stories out of wave order when there are dependencies
- Starting implementation before `spec-plan` completes for the current phase
- Not running review-gap after completing a wave
- Agent Teams feature flag not enabled – check for CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS
- Not spawning troubleshooter on escalation
- **Agents claiming tasks not assigned to them** – self-review risk; all tasks must be pre-assigned with `owner`
- **Implementers not using EnterWorktree** – parallel implementers in the same working directory cause file conflicts and race conditions
- **Forgetting to merge worktree branches** before starting reviews or next wave – reviewers work on main post-merge
- **Do NOT use `isolation: "worktree"` with `team_name`** – known Claude Code bug ([#33045](https://github.com/anthropics/claude-code/issues/33045)) where isolation is silently ignored for team agents; instruct implementers to call `EnterWorktree` themselves instead
- **Multi-repo worktree pollution** – if plan and code live in different repos and `CODE_DIR` is not set, agents create worktrees/branches/commits in the plan repo instead of the code repo. Always set `CODE_DIR` for multi-repo workspaces. Agents must verify they are in `CODE_DIR` before calling `EnterWorktree`
- **FIS paths must be absolute in multi-repo setups** – FIS files live in the plan repo but agents work in `CODE_DIR`. Relative FIS paths won't resolve from the code repo. The orchestrator must convert all FIS paths to absolute before passing them to agents
- **Merge/cleanup commands must target CODE_DIR** – all `git merge`, `git checkout`, `git branch`, `git worktree remove` in Step 6d and Step 9 must use `git -C {CODE_DIR}` to target the code repo, not the orchestrator's CWD
- **Status updates get dropped when context is exhausted** – plan and FIS checkbox updates (Step 6f) are GATES that block the next phase, not optional cleanup. Update immediately after each story completes
- Not updating STATE.md when phases transition or blockers are discovered – state drift causes session continuity loss
- **Agents writing to STATE.md** – only the orchestrator updates STATE.md; implementers and reviewers must NOT write to it (avoids race conditions with parallel agents)

### Helper Scripts
Helper scripts are available in `${CLAUDE_PLUGIN_ROOT}/scripts/` – use when applicable:
- `check-stubs.sh <path>` – scan for incomplete implementation indicators
- `check-wiring.sh <path>` – verify new/changed files are imported/referenced
- `verify-implementation.sh <file1> [file2...]` – combined existence + substance + wiring check


## WORKFLOW

### Step 1: Check Agent Teams Availability

Verify Agent Teams are available by checking that team creation tools exist in your available tools (e.g. `TeamCreate`).

If Agent Team tools are NOT available (experimental feature not enabled):
- Suggest using the `andthen:exec-plan` skill instead (portable version that works without Agent Teams):
  `/andthen:exec-plan path/to/plan` (or `$andthen:exec-plan path/to/plan`)
- If user specifically wants Agent Teams, inform them it requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Exit

**Gate**: Agent Teams confirmed available


### Step 2: Parse Plan

0. **Load session state** – Read `STATE.md` (path from **Project Document Index**, default: `docs/STATE.md`) if it exists. Extract session continuity notes (context from previous sessions), active stories and their status (detect resumed work), blockers (may affect execution order), and current phase (verify alignment with plan). If STATE.md does not exist, skip – it is optional.

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


### Step 3: Generate Specs (via spec-plan)

Before setting up the Agent Team, pre-generate all FIS documents for the current phase by delegating to `andthen:spec-plan`. This handles parallel sub-agent creation (opus model), wave ordering, cross-cutting review, and plan.md updates.

> **This step repeats for each phase** – generate specs for Phase N stories before starting the Agent Team pipeline for that phase (see Step 6).

Run (use `/` or `$` prefix depending on agent platform):
```
/andthen:spec-plan {PLAN_DIR} --phase {N}
```

`spec-plan` handles:
- Checking for existing FIS (skips stories that already have one)
- Spawning parallel opus sub-agents per story (wave-ordered, up to 5 concurrent)
- Cross-cutting review to catch inter-story inconsistencies
- Fixing CRITICAL/HIGH issues and updating plan.md FIS fields

After `spec-plan` completes, re-read `plan.md` to pick up updated FIS paths.

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

**IMPORTANT – Use Agent Teams, NOT regular sub-agents.**
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

> **Note**: Spec generation is delegated to `andthen:spec-plan` _before_ the Agent Team starts (see Step 3). The team only handles implementation and review.

**Implementers** (`model: "sonnet"`) – Work on pre-assigned `impl-{story_id}` tasks. For each task: ensure CWD is `CODE_DIR`, enter an isolated worktree via `EnterWorktree`, run `/andthen:exec-spec {fis_path}` (or `$andthen:exec-spec {fis_path}`) with absolute FIS path, commit all changes, exit worktree with `action: "keep"` (preserves the branch for merge), then mark task complete. Output: implemented story on a worktree branch in `CODE_DIR`.

**Reviewers** (`model: "sonnet"`) – Work on pre-assigned `review-{story_id}` tasks (unblocked by orchestrator after wave merge). Ensure CWD is `CODE_DIR`, then run `/andthen:review-gap {fis_path}` (or `$andthen:review-gap {fis_path}`) with absolute FIS path per story **on the main branch** (post-merge). If issues found: fix them on main, then re-validate. **Max 2 fix attempts** – if issues persist after 2 rounds, escalate to the orchestrator via message instead of continuing the loop. Output: validated story.

Each agent loops: **check for assigned tasks → execute → mark done → check for next assigned task**.

**Troubleshooter (on-demand)** (`model: "sonnet"`) – NOT spawned upfront. The orchestrator spawns a troubleshooter teammate only when an agent escalates an issue it cannot resolve (build failures, analysis errors, cross-story conflicts, persistent test failures, etc.). Uses `andthen:build-troubleshooter` agent type. Receives a `fix-{story_id}` task with the issue context from the escalating agent. Shut down after the issue is resolved.

#### Spawn Templates

Use these role-specific prompts when spawning each teammate into the team (with `team_name: "plan-pipeline"`, `name: "<role-N>"`, and `model: "sonnet"`). Use `/` or `$` prefix depending on agent platform.

**Implementer template:**
```
Role: Implementer
Team: plan-pipeline
Plan: {PLAN_DIR}/plan.md
Code repo: {CODE_DIR}

CRITICAL ROLE CONSTRAINT: You are an Implementer. ONLY work on tasks prefixed
with impl-* that are assigned to you (owner = your name). NEVER claim or work
on review-* tasks or unassigned tasks.

Your workflow (loop until no assigned tasks remain):
1. Check the task list for tasks assigned to you (owner = your name)
2. For each assigned impl-* task:
   a. Ensure your CWD is {CODE_DIR} (the code repo) – `cd {CODE_DIR}` if needed
   b. Call EnterWorktree with name "story-{story_id}" to create an isolated worktree
   c. /andthen:exec-spec {fis_path}    (FIS path is ABSOLUTE – do not modify it)
   d. Commit all changes in the worktree (ensure nothing is left uncommitted)
   e. Call ExitWorktree with action "keep" – the orchestrator needs the branch for merge
   f. Mark task completed
3. Check the task list for your next assigned task
4. If no tasks assigned to you, notify orchestrator via message

Important:
- ONLY work on tasks where owner = your name – never claim unassigned tasks
- Your CWD MUST be {CODE_DIR} before calling EnterWorktree – worktrees must be
  created in the CODE repo, never in the plan repo
- ALWAYS use EnterWorktree before starting implementation (prevents file conflicts)
- ALWAYS commit and ExitWorktree(keep) when done – do not leave worktrees open
- FIS paths in task descriptions are absolute – use them as-is
- Read the Workflow Rules, Guardrails and Guidelines in CLAUDE.md before starting
- Follow existing codebase patterns
- Escalate issues you cannot resolve to orchestrator via message with full context
```

**Reviewer template:**
```
Role: Reviewer
Team: plan-pipeline
Plan: {PLAN_DIR}/plan.md
Code repo: {CODE_DIR}

CRITICAL ROLE CONSTRAINT: You are a Reviewer. ONLY work on tasks prefixed
with review-* that are assigned to you (owner = your name). NEVER claim or
work on impl-* tasks or unassigned tasks.

Your workflow (loop until no assigned tasks remain):
1. Check the task list for tasks assigned to you (owner = your name)
2. For each assigned review-* task:
   a. Ensure your CWD is {CODE_DIR} (the code repo) – `cd {CODE_DIR}` if needed
   b. /andthen:review-gap {fis_path}    (FIS path is ABSOLUTE – do not modify it)
      Work on main branch – code is already merged from worktrees
   c. If issues found: fix them on main, then re-validate (max 2 fix attempts)
   d. If issues persist after 2 fix attempts, escalate to orchestrator via message
   e. Mark task completed
3. Check the task list for your next assigned task
4. If no tasks assigned to you, notify orchestrator via message

Important:
- ONLY work on tasks where owner = your name – never claim unassigned tasks
- Your CWD MUST be {CODE_DIR} – all code changes happen in the code repo
- Review tasks are unblocked by the orchestrator AFTER the wave merge completes
- Work on the main branch (implementation has already been merged from worktrees)
- FIS paths in task descriptions are absolute – use them as-is
- Read the Workflow Rules, Guardrails and Guidelines in CLAUDE.md before starting
- Follow existing codebase patterns
- Escalate issues you cannot resolve to orchestrator via message with full context
```

**Gate**: Team created and all agents spawned


### Step 6: Phase Loop

For each phase in the plan:

#### 6a. Generate Specs for This Phase

**Update project state** (if STATE.md exists): Use `andthen:ops update-state phase "{Phase N}: {phase_name}"` and `andthen:ops update-state status "On Track"` to record the active phase.

Run Step 3 (Generate Specs via `spec-plan`) for the current phase's stories. All FIS documents must exist before creating implementation tasks.

#### 6b. Create Pipeline Tasks (Pre-Assigned)

For each story in the current phase, create tasks with **pre-assigned owners**:
- `impl-{story_id}`: "Implement {story_name}" – assign to a specific implementer
- `review-{story_id}`: "Review and validate {story_name}" – assign to a specific reviewer

**Pre-assignment rules:**
- Round-robin distribute `impl-*` tasks across implementers to balance workload
- Round-robin distribute `review-*` tasks across reviewers
- **Never assign impl and review of the same story to the same agent** (prevents self-review)
- Set the `owner` field via TaskUpdate immediately after task creation

**Wave-based task creation** (if waves present in plan):
- Group story tasks by wave within each phase
- W1 `impl-*` tasks are immediately unblocked (no wave predecessors)
- W1 `review-*` tasks are created as **blocked** – the orchestrator unblocks them after the wave merge (see Step 6d)
- W2 `impl-*` tasks are blocked by completion of all W1 review tasks
- W3+ tasks follow the same pattern: impl unblocked after previous wave reviews complete, review unblocked after current wave merge

#### 6c. Set Dependencies

Set task dependencies:
- `impl-{story_id}` – unblocked for current wave (ready for implementers to start)
- `review-{story_id}` – **create as blocked**. The orchestrator unblocks review tasks for each wave AFTER merging all worktree branches from that wave (see Step 6d)
- Cross-story dependencies from plan: if S05 depends on S03, then `impl-S05` blocked by `review-S03`

#### 6d. Merge Wave

After ALL `impl-*` tasks in the current wave are complete (all implementers have committed and exited their worktrees):

1. **Verify worktree branches exist** – Each completed impl task should have produced a worktree branch named `worktree-story-{story_id}` (the branch EnterWorktree creates)

2. **Pre-merge conflict detection** – Dry-run each merge to identify conflicts before starting:
   ```bash
   # All git commands target CODE_DIR (the code repo, not the plan repo)
   git -C {CODE_DIR} merge-tree $(git -C {CODE_DIR} merge-base HEAD worktree-story-{story_id}) HEAD worktree-story-{story_id}
   # Non-empty output = conflicts expected
   ```

3. **Sequentially merge each story branch into main** (`--no-ff` preserves explicit merge commits for easy per-story rollback):
   ```bash
   git -C {CODE_DIR} checkout main
   # Merge each story branch one at a time
   git -C {CODE_DIR} merge worktree-story-{story_id} --no-ff -m "Merge story {story_id}: {story_name}"
   # Repeat for each story in the wave
   ```

4. **Handle merge conflicts** by type:
   - **Import/config accumulation** (very common) – take both additions, they are additive
   - **Lock file conflicts** (common) – `git checkout --theirs pnpm-lock.yaml` then re-run package manager install to regenerate
   - **Adjacent code modifications** – spawn a Troubleshooter teammate with both stories' FIS as context
   - **Same function, incompatible logic** – escalate to user (implies a missed plan dependency)

5. **Verify build + tests** on merged main before proceeding to reviews

6. **Clean up worktrees**:
   ```bash
   git -C {CODE_DIR} worktree remove .claude/worktrees/story-{story_id}
   git -C {CODE_DIR} branch -d worktree-story-{story_id}
   # Repeat for each story in the wave
   ```

7. **Unblock review tasks** for this wave – update each `review-{story_id}` task to unblocked status so reviewers can pick them up

> **Critical invariant**: Wave N+1 worktrees must be created AFTER Wave N merges complete. Creating them before means they branch from pre-merge main and lack Wave N's changes – causing guaranteed conflicts and incorrect behavior.

**Gate**: All wave branches merged, build passes, review tasks unblocked

#### 6e. Monitor Progress

- Poll the task list periodically and track completion by wave:
  1. **Monitor impl tasks** – when all `impl-*` tasks in wave N complete → run wave merge (Step 6d)
  2. **Monitor review tasks** – when all `review-*` tasks in wave N complete → proceed to wave N+1 or next phase
- Handle agent messages (failures, questions, status updates)

#### 6f. Update Plan and FIS Status (REQUIRED GATE)

**CRITICAL – do this immediately after each story's review completes, not as a batch at the end.**

After each story's pipeline completes (exec-spec → review-gap), use the `andthen:ops` skill to update `plan.md`:
- Set the story's **Status** field to `Done`
- Set the story's **FIS** field to the generated spec path (e.g. `**FIS**: docs/specs/story-name.md`)
- Check off completed acceptance criteria checkboxes (`- [ ]` → `- [x]`)
- Update the Story Catalog table: set the story's Status column to `Done`

Also update each completed FIS file:
- Mark all task checkboxes as checked (`- [x]`)
- Mark success criteria and Final Validation Checklist items as checked

**Update STATE.md** (if it exists): Use `andthen:ops update-state active-story {story_id} Done` to reflect completion. If the next story is starting, also run `andthen:ops update-state active-story {next_story_id} "{next_story_name}" "In Progress"`.

After ops completes, **re-read plan.md and the FIS file** to verify updates were applied (`ops` runs in fork context and modifications may not be visible in your current state).

Move to next phase only after ALL stories in current phase are complete and plan is updated.

**Create Phase N+1 tasks only after Phase N is fully complete.**

**Gate**: All stories in current phase completed, verified, AND plan.md + FIS checkboxes updated – verify before proceeding to next phase

#### Pipeline Flow Example

```
Phase 1 (Sequential – W1: S01, W2: S02):
  spec-plan --phase 1 (parallel spec creation + cross-cutting review)
  W1: impl-S01 (worktree) → MERGE W1 → review-S01 (main)
  W2: impl-S02 (worktree) → MERGE W2 → review-S02 (main)

Phase 2 (Parallel – W1: S03[P], S04[P] | W2: S05 depends on S03):
  spec-plan --phase 2 (parallel spec creation + cross-cutting review)
  W1: impl-S03 (worktree) ─┐
      impl-S04 (worktree) ─┤→ MERGE ALL W1 → review-S03 + review-S04 (main, parallel)
                            │
  W2: impl-S05 (worktree) ─→ MERGE W2 → review-S05 (main)
```

Each implementer works in an isolated git worktree (via `EnterWorktree`). After all implementations in a wave complete, the orchestrator merges all worktree branches into main, then unblocks review tasks. Reviewers work on the merged main branch.

**Gate**: All phases complete, all stories implemented and reviewed


### Step 7: Final Verification

**Orchestrator performs directly** (not delegated):

1. Run build – verify it succeeds
2. Run tests – verify all pass
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

1. **Clean up any remaining worktrees** – remove worktree directories and branches that weren't cleaned up during wave merges:
   ```bash
   git -C {CODE_DIR} worktree list   # check for leftover worktrees
   git -C {CODE_DIR} worktree prune  # remove stale worktree references
   ```
2. Send shutdown requests to each teammate
3. Wait for shutdown confirmations
4. Delete the team to remove team and task files


## FAILURE HANDLING

- **Agent reports failure** via message → orchestrator spawns an **on-demand Troubleshooter** teammate (`andthen:build-troubleshooter`) with issue context → creates a `fix-{story_id}` task → troubleshooter diagnoses and fixes → shuts down troubleshooter after resolution → escalates to user only if troubleshooter also fails
- **Dependent stories stay blocked** when a predecessor fails
- **If >50% of a phase fails** → pause execution, notify user with failure summary
- **Update STATE.md on failure** (if it exists): Use `andthen:ops update-state status "At Risk"` (or `"Blocked"` for critical failures). Add blockers via `andthen:ops update-state blocker "{description}"`.


## COMPLETION

When all phases are complete, print a summary including: stories completed, total phases, verification results (build/test status), and the path to the updated `PLAN_DIR/plan.md`.


## Post-Completion: Update Project State

After all phases complete (or if execution is interrupted/paused), update STATE.md via `andthen:ops` (if it exists):
- Set phase to the completed (or current) phase
- Set status to reflect outcome (`On Track` if all passed, `At Risk` if issues remain)
- Clear completed stories from Active Stories (mark as `Done`)
- Add a session continuity note summarizing: what was completed, what remains, any context the next session needs

Example: `andthen:ops update-state note "exec-plan-team complete: {N}/{M} stories done, all phases passed"` (or describe what remains if interrupted).


## Post-Completion: Update Project Learnings

After all phases complete, if the project has a learnings file (`LEARNINGS.md` or `implementation-notes.md` – check Project Document Index for location), update it with knowledge discovered across stories. Organize by topic, not chronologically. Types of knowledge to capture:
- **Traps & gotchas**: Non-obvious patterns that would bite a competent developer even with access to code and git history
- **Domain knowledge**: API quirks, framework behavior, naming decisions, business rules discovered in code
- **Procedural knowledge**: Deploy steps, test prerequisites, tooling patterns
- **Error patterns**: Recurring errors – note if deterministic (bad schema, wrong type → conclude immediately) or infrastructure (timeout, rate limit → log, conclude only when pattern emerges)
- **Cross-story insights**: Patterns that only become visible when implementing multiple stories (e.g., shared abstractions, recurring conflicts, dependency ordering lessons)

Keep entries brief (1-2 sentences each). Do NOT record what was implemented (that's in git history), how parts integrate (that's in the code), or routine decisions (that's in the FIS/spec).

**Self-maintenance**: When updating, also review nearby entries – merge overlapping items, remove knowledge that's no longer accurate, split sections that grow too long.


## FALLBACK: NO AGENT TEAMS

If Agent Teams unavailable (Step 1 check fails), suggest the manual equivalent:

```bash
# 1. Generate all specs first (/ for Claude Code, $ for Codex):
/andthen:spec-plan path/to/plan                    # or $andthen:spec-plan ...

# 2. Then for each story in plan order:
/andthen:exec-spec path/to/fis/s01-story-name.md   # or $andthen:exec-spec ...
/andthen:review-gap path/to/fis/s01-story-name.md  # or $andthen:review-gap ...
# ... repeat for each story
```
