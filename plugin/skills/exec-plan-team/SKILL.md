---
description: Execute an implementation plan through an Agent Team pipeline with configurable review mode (requires Agent Teams)
argument-hint: <path-to-plan | --issue <number> | issue URL> [path-to-code-repo] [--review-mode per-story|none|full-plan] [--worktree]
---

# Execute Plan (Agent Teams)

Execute ALL stories in an implementation plan (from `andthen:plan`) through a parallelized pipeline: **spec-plan** (parallel spec generation + cross-cutting review per phase), then Agent Team **exec-spec → merge**, with configurable review behavior. By default, stories execute **sequentially on the current branch**. Use `--worktree` to enable isolated git worktrees for parallel execution (prevents file conflicts but adds merge complexity).

**Requires Agent Teams** – Falls back to sequential execution (manual per-story loop) if Teams unavailable.


## VARIABLES
PLAN_SOURCE: $0
CODE_DIR: $1
REVIEW_MODE: parse from `--review-mode` flag (`per-story`, `none`, or `full-plan`; default `per-story`)
USE_WORKTREE: parse from `--worktree` flag (default: `false`; `--worktree` sets to `true`)
BASE_BRANCH: resolved at startup — the current branch of `CODE_DIR` when execution begins (e.g. `main`, `feat/v2`, etc.)


## USAGE

```
/exec-plan-team path/to/plan [path/to/code/repo] [--review-mode per-story|none|full-plan] [--worktree]
/exec-plan-team --issue 123 [path/to/code/repo] [--review-mode per-story|none|full-plan] [--worktree]
```

Omit `CODE_DIR` for single-repo projects; provide it when plan/specs live in a different repo from the code. `--worktree` enables isolated git worktrees for parallel execution; without it, stories run sequentially on the current branch (`[P]` markers are ignored).


## INSTRUCTIONS

Make sure `PLAN_SOURCE` is provided – otherwise **STOP** immediately and ask the user to provide the path to the plan directory or the typed GitHub plan artifact.

### Resolve PLAN_SOURCE

Resolve `PLAN_SOURCE` per the **Resolve Plan-Bundle Input** procedure in `${CLAUDE_PLUGIN_ROOT}/references/github-artifact-roundtrip.md` (run before `Resolve CODE_DIR`). Incompatible typed artifacts → **STOP** and direct the user to the correct skill.

### Resolve CODE_DIR

**Resolve CODE_DIR** (run before any other work):

1. If `CODE_DIR` was provided: verify it is a git repository (`git -C {CODE_DIR} rev-parse --git-dir`). Resolve to absolute path.
2. If `CODE_DIR` was NOT provided, **auto-detect**:
   a. If `PLAN_SOURCE_MODE = github-artifact`: set `CODE_DIR` = CWD's git root. GitHub-extracted artifacts in `.agent_temp/` are not themselves git repos, so repo inference must come from the current workspace. If the code lives in another repo, the user must provide `CODE_DIR` explicitly.
   b. Otherwise get the git root of PLAN_DIR: `git -C {PLAN_DIR} rev-parse --show-toplevel`
   c. Get the git root of CWD: `git rev-parse --show-toplevel`
   d. If they are the **same repo** → `CODE_DIR` = that git root
   e. If they are **different repos** → `CODE_DIR` = CWD's git root (multi-repo: plan is in a separate repo)
3. Resolve `CODE_DIR` to an **absolute path** and use it throughout all remaining steps.
4. Resolve `BASE_BRANCH`: `git -C {CODE_DIR} rev-parse --abbrev-ref HEAD` — this is the branch all work happens on (sequential) or merges back to (worktree mode).
5. Log: `"CODE_DIR resolved to: {CODE_DIR} (source: explicit | same-repo | multi-repo-auto | github-artifact-auto), BASE_BRANCH: {BASE_BRANCH}"`

**Multi-repo rules** (when CODE_DIR ≠ PLAN_DIR's git root):
- All git operations target `CODE_DIR` – never the plan repo
- `EnterWorktree` must be called from `CODE_DIR` context
- FIS paths passed to agents must be **absolute**
- The plan repo is **read-only for git operations** – only the orchestrator updates `plan.md`
- Never create branches, worktrees, or commits in the plan repo

### Core Rules
- Read **Workflow Rules, Guardrails and Guidelines** from CLAUDE.md before starting
- Plan is source of truth – follow phase ordering, dependencies, and parallel markers exactly
- Pre-generate specs via the `andthen:spec-plan` skill per phase before starting the Agent Team
- **Review mode**: `per-story` → `review-gap` after each merged story; FAIL triggers `remediate-findings`. `none` → skip. `full-plan` → one final `review-gap` on `PLAN_DIR/plan.md` after all stories merged; FAIL triggers `remediate-findings`
- **Worktree isolation** (`USE_WORKTREE = false` by default) – stories run sequentially on `{BASE_BRANCH}`. `USE_WORKTREE = true` (via `--worktree`) → implementers call `EnterWorktree` per task in `CODE_DIR` for parallel execution
- **Pre-assign all tasks** – no self-claiming; orchestrator assigns every task at creation time

**You are the orchestrator.** Parse the plan; delegate spec generation; size and create the team with pre-assigned tasks; merge waves; handle failures; run final review and verification. Do NOT write implementation code or skip final verification.


## GOTCHAS
- **Do NOT use `isolation: "worktree"` with `team_name`** – Claude Code bug ([#33045](https://github.com/anthropics/claude-code/issues/33045)) silently ignores isolation for team agents; instruct implementers to call `EnterWorktree` themselves
- **Multi-repo worktree pollution** – if `CODE_DIR` is not set and plan/code live in different repos, agents create worktrees in the plan repo. Always set `CODE_DIR` for multi-repo workspaces; verify agents are in `CODE_DIR` before `EnterWorktree`
- **Merge/cleanup commands must target CODE_DIR** – all `git merge`, `git checkout`, `git branch`, `git worktree remove` must use `git -C {CODE_DIR}`, not the orchestrator's CWD
- **Creating separate worktrees for composite-FIS stories** – stories sharing one FIS must share one worktree and one impl task; separate worktrees cause duplicate implementation and merge conflicts
- **Status updates get dropped on context exhaustion** – plan and FIS checkbox updates (Step 6e) are GATES that block the next phase; update immediately after each story, never as a batch at the end
- **Wave N+1 worktrees must be created AFTER Wave N merges complete** – branching from pre-merge `{BASE_BRANCH}` causes guaranteed conflicts
- **Wave N+1 merge must wait for Wave N reviews** (`per-story`) – reviews may fix code on `{BASE_BRANCH}`, so the merge target must be stable before merging. W(N+1) *impl* can overlap with W(N) reviews (worktrees are isolated), but the *merge* cannot
- **Only the orchestrator writes to STATE.md** – implementers and reviewers must NOT update STATE.md (avoids race conditions with parallel agents)
- **GitHub artifact mirrors are scratch space** – when `PLAN_SOURCE_MODE = github-artifact`, apply the Plan-Bundle Continuation Sync before finishing

### Helper Scripts
Helper scripts are available in `${CLAUDE_PLUGIN_ROOT}/scripts/` – use when applicable:
- `check-stubs.sh <path>` – scan for incomplete implementation indicators
- `check-wiring.sh <path>` – verify new/changed files are imported/referenced
- `verify-implementation.sh <file1> [file2...]` – combined existence + substance + wiring check


## WORKFLOW

### Step 1: Check Agent Teams Availability

Verify Agent Teams are available by checking that team creation tools exist (e.g. `TeamCreate`).

If Agent Team tools are NOT available:
- Suggest the `andthen:exec-plan` skill instead (portable, no Agent Teams required): `/andthen:exec-plan path/to/plan`
- If user specifically wants Agent Teams, inform them it requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Exit

**Gate**: Agent Teams confirmed available


### Step 2: Parse Plan

1. **Load session state** – Read `STATE.md` (default: `docs/STATE.md`) if it exists. Extract active stories, blockers, and current phase.
2. Read `PLAN_DIR/plan.md`. If missing, **STOP** and recommend the `andthen:plan` skill first.
3. Extract: stories (ID, name, scope, acceptance criteria, dependencies), phases, parallel markers `[P]`, dependency graph, wave assignments (W1, W2, W3…)
4. Build execution plan respecting phase ordering and dependency chains.

**Gate**: Plan parsed and phases identified


### Step 3: Generate Specs (via spec-plan)

Before setting up the Agent Team, pre-generate all FIS documents for the current phase:

```
/andthen:spec-plan {PLAN_DIR} --phase {N}
```

`spec-plan` handles: checking for existing FIS, parallel sub-agents (wave-ordered, up to 5 concurrent), cross-cutting review, and `plan.md` updates. After it completes, re-read `plan.md` to pick up updated FIS paths.

> This step repeats for each phase — generate specs for Phase N before starting the Agent Team pipeline for that phase (see Step 6).

**Gate**: All stories in current phase have FIS documents


### Step 4: Size Team

| Plan Size | Stories | Implementers | Reviewers (`per-story`) | Reviewers (`none`/`full-plan`) |
|---|---|---|---|---|
| Small | 1-4 | 1 | 1 | 0 |
| Medium | 5-10 | 2 | 2 | 0 |
| Large | 11+ | 3 | 2 | 0 |

**Gate**: Team sized based on story count


### Step 5: Create Team and Spawn Agents

**IMPORTANT – Use Agent Teams, NOT regular sub-agents.** Teammates must be spawned into the team (with `team_name` and `name`) so they share a task list and can message each other. Create team `"plan-pipeline"`, spawn teammates with a capable coding model (`model: "sonnet"`, `gpt-5.3-codex`, or similar), create pipeline tasks per phase (Step 6), coordinate via inter-agent messaging, then send shutdown requests and delete the team when done.

**Roles**: Implementer (all stories), Reviewer (`per-story` mode only), Troubleshooter (on-demand via the `andthen:build-troubleshooter` agent — NOT spawned upfront; only when an agent escalates).

#### Spawn Templates

Use these role-specific prompts when spawning each teammate (with `team_name: "plan-pipeline"`, `name: "<role-N>"`, capable coding model). Spawn reviewer teammates only when `REVIEW_MODE=per-story`. Use `/` or `$` prefix depending on agent platform.

**Implementer template:**
```
Role: Implementer
Team: plan-pipeline
Plan: {PLAN_DIR}/plan.md
Code repo: {CODE_DIR}
Review mode: {REVIEW_MODE}
Worktree isolation: {ENABLED if USE_WORKTREE=true, DISABLED (work directly on {BASE_BRANCH}) if USE_WORKTREE=false}

CRITICAL ROLE CONSTRAINT: You are an Implementer. ONLY work on tasks prefixed
with impl-* that are assigned to you (owner = your name). NEVER claim or work
on review-* tasks or unassigned tasks.

Your workflow (loop until no assigned tasks remain):
1. Check the task list for tasks assigned to you (owner = your name)
2. For each assigned impl-* task:
   a. Ensure your CWD is {CODE_DIR} – `cd {CODE_DIR}` if needed
   [IF USE_WORKTREE=true]
   b. Call EnterWorktree with name "story-{task_id}" (task_id: e.g., "S01" or "S01-S02")
   [END IF]
   c. /andthen:exec-spec {fis_path}    (FIS path is ABSOLUTE – do not modify it)
   d. Commit all changes {in the worktree if USE_WORKTREE=true}
   [IF USE_WORKTREE=true]
   e. Call ExitWorktree with action "keep" – orchestrator needs the branch for merge
   [END IF]
   f. Update FIS status: /andthen:ops update-fis {fis_path} all
   g. Mark task completed
3. Check for your next assigned task
4. If no tasks assigned to you, notify orchestrator via message

Rules:
- ONLY work on tasks assigned to you (owner = your name)
- CWD MUST be {CODE_DIR} before any work
- [USE_WORKTREE=true] EnterWorktree BEFORE impl; commit and ExitWorktree(keep) AFTER
- [USE_WORKTREE=false] No EnterWorktree; stories run sequentially on {BASE_BRANCH}
- FIS status updates (step 2f) are REQUIRED; FIS paths are absolute
- Read Workflow Rules, Guardrails and Guidelines in CLAUDE.md before starting
- Escalate unresolvable issues to orchestrator via message
```

**Reviewer template (`REVIEW_MODE=per-story` only):**
```
Role: Reviewer
Team: plan-pipeline
Plan: {PLAN_DIR}/plan.md
Code repo: {CODE_DIR}
Review mode: {REVIEW_MODE}
Worktree isolation: {ENABLED (you review on {BASE_BRANCH} after wave merge) if USE_WORKTREE=true, DISABLED (review implementer's commits directly on {BASE_BRANCH}) if USE_WORKTREE=false}

CRITICAL ROLE CONSTRAINT: You are a Reviewer. ONLY work on tasks prefixed
with review-* that are assigned to you (owner = your name). NEVER claim or
work on impl-* tasks or unassigned tasks.

Your workflow (loop until no assigned tasks remain):
1. Check the task list for tasks assigned to you (owner = your name)
2. For each assigned review-* task:
   a. Ensure your CWD is {CODE_DIR} – `cd {CODE_DIR}` if needed
   b. /andthen:review-gap {fis_path}    (FIS path is ABSOLUTE – do not modify it)
      Work on {BASE_BRANCH} – code is already merged {from worktrees if USE_WORKTREE=true / committed by implementer if false}
   c. If review-gap fails: capture the report path, run /andthen:remediate-findings {report_path} on {BASE_BRANCH}, then re-run review-gap (max 2 review/remediation rounds)
   d. If issues persist after 2 attempts, escalate to orchestrator via message
   e. Mark task completed
3. Check for your next assigned task
4. If no tasks assigned to you, notify orchestrator via message

Rules:
- ONLY work on tasks assigned to you (owner = your name)
- CWD MUST be {CODE_DIR}; FIS paths are absolute
- [USE_WORKTREE=true] Tasks unblocked by orchestrator AFTER wave merge
- [USE_WORKTREE=false] Tasks unblocked after corresponding impl-*; you are on the critical path
- Read Workflow Rules, Guardrails and Guidelines in CLAUDE.md before starting
- Escalate unresolvable issues to orchestrator via message
```

**Gate**: Team created and all agents spawned


### Step 6: Phase Loop

For each phase in the plan:

#### 6a. Generate Specs for This Phase

**Update project state** (if STATE.md exists): `andthen:ops update-state phase "{Phase N}: {phase_name}"` and `andthen:ops update-state status "On Track"`.

Run Step 3 for the current phase's stories. All FIS documents must exist before creating implementation tasks.

#### 6b. Create Pipeline Tasks and Set Dependencies

For each story in the current phase, create tasks with **pre-assigned owners**.

**Shared-FIS Dedup**: Group stories by FIS path. When multiple stories share the same FIS (composite or collected thin-specs):
- Create **one** impl task (not separate per story); one review task when `REVIEW_MODE=per-story`
- Use **one** worktree per shared FIS (when `USE_WORKTREE = true`)
- When constituent stories span different waves, assign to the **earliest wave** (thin-specs stories are trivial and should not block dependents) unless a constituent has an unresolved dependency on a non-constituent story in a later wave
- Run the **Plan Acceptance Gate** (Step 6e) for ALL constituent stories after the shared task completes

**Task naming:** Standard: `impl-{story_id}` / `review-{story_id}`. Composite: `impl-{S01-S02}` / `review-{S01-S02}`. Thin-specs: `impl-thin` / `review-thin`

**Pre-assignment rules:**
- Round-robin distribute `impl-*` across implementers; `review-*` across reviewers
- **Never assign impl and review of the same story to the same agent** (prevents self-review)
- Set `owner` field via TaskUpdate immediately after task creation

**Dependencies:**

When `USE_WORKTREE = true`:
- Current-wave `impl-*` tasks are immediately unblocked
- `review-*` tasks are created **blocked**; orchestrator unblocks them after wave merge (Step 6c)
- W2+ `impl-*` blocked by prior-wave **merge completion** (all modes) — worktrees are isolated, so impl can overlap with prior-wave reviews
- W2+ **merge** blocked by prior-wave review completion (`per-story`) — reviews may fix code on `{BASE_BRANCH}`, so the merge target must be stable before merging the next wave
- Cross-story deps from plan: `impl-S05` blocked by `review-S03` (`per-story`) or its impl+merge completion (other modes); composites inherit constituent deps

When `USE_WORKTREE = false` (sequential — only one story mutates `{BASE_BRANCH}` at a time):
- `per-story`: each `impl-*` blocked by previous story's `review-*` (full pipeline must finish before next starts)
- `none`/`full-plan`: each `impl-*` blocked by previous `impl-*`
- `review-*` blocked by its corresponding `impl-*`; parallel markers `[P]` are ignored

#### 6c. Merge Wave (when `USE_WORKTREE = true`)

> **Skip when `USE_WORKTREE = false`** – proceed directly to unblocking review tasks if `REVIEW_MODE=per-story`.

After ALL `impl-*` tasks in the current wave are complete:

0. **Wait for prior-wave reviews** (`REVIEW_MODE=per-story` only) – if prior-wave `review-*` tasks are still running, wait for them to finish before merging. Reviews may fix code on `{BASE_BRANCH}`, so the merge target must be stable. (Wave 1 skips this — no prior reviews.)
1. **Pre-merge conflict detection** – dry-run: `git -C {CODE_DIR} merge-tree $(git -C {CODE_DIR} merge-base {BASE_BRANCH} worktree-story-{task_id}) {BASE_BRANCH} worktree-story-{task_id}`
2. **Sequentially merge** (`--no-ff`): `git -C {CODE_DIR} checkout {BASE_BRANCH} && git -C {CODE_DIR} merge worktree-story-{task_id} --no-ff -m "Merge {task_id}: {task_name}"`
3. **Handle conflicts**: imports → take both; lock files → `git checkout --theirs` then reinstall; adjacent code → spawn Troubleshooter; incompatible logic → escalate to user
4. **Verify build + tests** on merged `{BASE_BRANCH}`
5. **Clean up**: `git -C {CODE_DIR} worktree remove .claude/worktrees/story-{task_id} && git -C {CODE_DIR} branch -d worktree-story-{task_id}`
6. **Unblock review tasks** for this wave (`REVIEW_MODE=per-story` only)

**Gate**: All wave branches merged, build passes, review tasks unblocked when `REVIEW_MODE=per-story`

#### 6d. Monitor and Report Progress

**You must print progress updates to the user throughout execution.** The user cannot see agent activity — you are their only window into what's happening.

**Print updates when:**
- A task is created or assigned → `"📋 Created {task_id} → assigned to {agent_name}"`
- An agent starts working on a task (first status message) → `"🔨 {agent_name} started {task_id}: {story_name}"`
- An agent completes a task → `"✅ {agent_name} completed {task_id}"`
- A wave completes → `"🌊 Wave {N} complete ({M}/{total} stories done)"`
- A merge succeeds/fails → `"🔀 Merged {task_id} into {BASE_BRANCH}"` or `"❌ Merge conflict on {task_id} — spawning troubleshooter"`
- A review completes → `"🔍 Review {task_id}: {PASS/FAIL}"`
- A phase completes → print phase summary (stories done, any issues)
- An agent reports a failure or escalation → print it immediately

**Polling loop:** Check the task list for completion. Between polls, handle incoming agent messages (failures, escalations, status updates) and print them. When all `impl-*` in a wave complete → run wave merge (Step 6c) if `USE_WORKTREE = true`, else proceed. When all `review-*` complete → advance to next wave/phase. `none`/`full-plan` → advance after merge (or impl if no `--worktree`).

#### 6e. Update Plan and FIS Status (REQUIRED GATE)

**CRITICAL – do this immediately after each story completes its required stages, not as a batch at the end.**

**Plan Acceptance Gate** (verify before marking Done):
1. Is each acceptance criterion in the plan demonstrably satisfied?
2. If the FIS narrowed scope, is the scope note present in the plan story's acceptance criteria?
3. If any criterion is unmet and no scope note explains it → do NOT mark Done → escalate to the user
4. For composite FIS: verify ALL constituent stories

Then invoke the `andthen:ops` skill to update `plan.md`:
- Set story **Status** to `Done` (composites: all constituent stories)
- Set story **FIS** field to generated spec path
- Check off completed acceptance criteria (`- [ ]` → `- [x]`)
- Update Story Catalog table Status to `Done`

Also use `andthen:ops update-fis {fis_path} all` for each completed FIS (marks all checkboxes; verification layer for context-exhausted implementers).

**Update STATE.md** (if it exists): `andthen:ops update-state active-story {story_id} Done`

After ops completes, **re-read plan.md and the FIS file** to verify updates were applied.

If `PLAN_SOURCE_MODE = github-artifact`, apply the **Plan-Bundle Continuation Sync** from `${CLAUDE_PLUGIN_ROOT}/references/github-artifact-roundtrip.md` now.

Move to next phase only after ALL stories in current phase are complete and plan is updated. **Create Phase N+1 tasks only after Phase N is fully complete.**

**Gate**: All stories completed, verified, AND plan.md + FIS checkboxes updated

#### Pipeline Flow Example

```
# Sequential (default), per-story review:
Phase 1: spec-plan --phase 1
  impl-S01 ({BASE_BRANCH}) → review-S01 → impl-S02 ({BASE_BRANCH}) → review-S02

# Worktrees (--worktree), per-story review (overlapped):
Phase 1: spec-plan --phase 1
  W1: impl-S01 (worktree) → MERGE W1 → review-S01 ({BASE_BRANCH}) ──────────┐
                                      └→ W2: impl-S02 (worktree, concurrent) ┴→ MERGE W2 → review-S02
  # W2 impl starts after W1 merge; W2 merge waits for W1 review to finish

Phase 2: spec-plan --phase 2, full-plan review:
  W1: impl-S03 ─┐
      impl-S04 ─┤→ MERGE ALL W1 → impl-S05 → MERGE W2
  Final: review-gap plan.md ({BASE_BRANCH}) → remediate-findings if FAIL
```

**Gate**: All phases complete. Per-story reviews complete when `REVIEW_MODE=per-story`.


### Step 7: Final Review Stage

- `per-story` – No extra review; story-level `review-gap` already completed in Step 6.
- `none` – Skip automated review. Record in completion summary that manual review is pending.
- `full-plan` – Run one final plan-level review:
  `/andthen:review-gap {PLAN_DIR}/plan.md`
  If it fails, capture the report path and run `/andthen:remediate-findings {report_path}`. Re-run review for up to 2 rounds before escalating to user.

**Gate**: Required review behavior for the selected `REVIEW_MODE` is complete


### Step 8: Final Verification

**Orchestrator performs directly** (not delegated):
1. Run build – verify it succeeds
2. Run tests – verify all pass
3. Review overall integration across stories
4. Include verification evidence per `${CLAUDE_PLUGIN_ROOT}/references/verification-evidence.md`: Build, Tests, Linting/types

**Gate**: Build, tests, and integration verification all pass


### Step 9: Documentation Update

Spawn a **general-purpose sub-agent** _(if supported)_ to update project documentation: refresh **README**, **CHANGELOG**, and any directly affected docs.

**Gate**: Documentation updated


### Step 10: Clean Up

1. **Remove any remaining worktrees** (when `USE_WORKTREE = true`):
   ```bash
   git -C {CODE_DIR} worktree list
   git -C {CODE_DIR} worktree prune
   ```
2. Send shutdown requests to each teammate; wait for confirmations; delete the team


### Step 11: Canonical Continuation Sync _(if `PLAN_SOURCE_MODE = github-artifact`)_
Apply the **Plan-Bundle Continuation Sync** from `${CLAUDE_PLUGIN_ROOT}/references/github-artifact-roundtrip.md` as the final gate.


## FAILURE HANDLING

- **Agent reports failure** → spawn an on-demand Troubleshooter (`andthen:build-troubleshooter` agent) with a `fix-{story_id}` task → shut down after resolution → escalate to user if troubleshooter also fails
- **Final plan review fails** (`full-plan`) → remediate then re-validate (max 2 review/remediation rounds). Escalate to user if issues persist.
- **Dependent stories stay blocked** when a predecessor fails
- **If >50% of a phase fails** → pause execution, notify user with failure summary
- **Update STATE.md on failure** (if it exists): `andthen:ops update-state status "At Risk"` (or `"Blocked"` for critical failures); add blockers via `andthen:ops update-state blocker "{description}"`


## COMPLETION

When all phases are complete, print a summary: stories completed, total phases, `REVIEW_MODE`, review results, verification results (build/test status), and the path to `PLAN_DIR/plan.md`.


## Post-Completion: Update Project State

After all phases complete (or if execution is interrupted/paused), follow `${CLAUDE_PLUGIN_ROOT}/references/post-completion-guide.md` (`Plan Runs` → `STATE.md`) for STATE.md updates.

## Post-Completion: Update Project Learnings

After all phases complete, follow `${CLAUDE_PLUGIN_ROOT}/references/post-completion-guide.md` (`Plan Runs` → `Learnings`) for learnings-file updates.


## FALLBACK: NO AGENT TEAMS

If Agent Teams unavailable (Step 1 check fails), suggest the manual equivalent:

```bash
# 1. Generate all specs first:
/andthen:spec-plan path/to/plan

# 2. For each story in plan order:
/andthen:exec-spec path/to/fis/s01-story-name.md
/andthen:review-gap path/to/fis/s01-story-name.md  # per-story mode only
/andthen:remediate-findings <path-to-gap-review-report>  # when review-gap fails

# 3. Optional review modes:
/andthen:review-gap path/to/plan/plan.md  # full-plan review after all stories
/andthen:remediate-findings <path-to-gap-review-report>  # when full-plan review fails
# none: user performs manual review
```
