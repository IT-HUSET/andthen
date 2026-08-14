# Team-Mode Orchestration

Loaded when `--team` is active (Step 3T). Single source of truth for team-mode behavior; default-mode does not load it. The worktree lifecycle (create → verify → squash-merge → teardown) is owned by [`worktree-mode.md`](worktree-mode.md) – this file wires it into team tasks.

## Team Setup

Create team `"plan-pipeline"` with pre-assigned tasks. Size: 1 implementer (≤4 stories), 2 (5–10), 3 (11+). Add 1–2 reviewers for `quick-review`. Implementers are medium/larger implementation tasks; reviewers are high-judgment review tasks. Let the nearest Sub-Agent Model Policy choose model and effort, or inherit when none exists.

Define `AUTO_SUFFIX = " --auto"` when `AUTO_MODE=true`, else `""`. Define `DEFER_SUFFIX = " --defer-shared-writes"` in every mode; the orchestrator owns shared status only after review.

Before `TeamCreate`, re-verify `CODE_DIR` is on `{BASE_BRANCH}` with an empty porcelain status – mandatory in both modes, since a phase transition or merge may have dirtied it since the last check (worktree runs first check it via `worktree-mode.md` → **Clean Baseline**). Never stash, commit, or move pre-existing user changes – a dirty checkout is Stop-the-Line; recommend `--worktree` only after the user makes the base checkout clean.

Apply the parent skill's **Multi-repo FIS attribution** rule before assigning tasks. In that topology, only the next story gets an active implementer or worktree.

**Pre-create worktrees** _(when `USE_WORKTREE=true`)_: before `TeamCreate`, run `worktree-mode.md` → **Create** for each currently active `impl-*` task's story, capturing `{WORKTREE_PATH_ABS}` per story. Multi-repo mode activates one.

**Substitution scope** – at team creation, replace in every teammate system prompt: `{AUTO_SUFFIX}`, `{DEFER_SUFFIX}`, `{CODE_DIR_ABS}`, `{BASE_BRANCH}`, `${CLAUDE_SKILL_DIR}`, `{UNTRUSTED_REQUIREMENTS_LINE}` (the run's exact line when externally derived, otherwise empty), and `{GOVERNING_PLAN_LINE}` (exact `GOVERNING PLAN PATH: {PLAN_PATH}` in local-directory mode, empty under `--from-issue`). Per story tasks fill `{STORY_ID}`, `{FIS_PATH}`, `{WORKTREE_PATH_ABS}`, and `{IMPLEMENTATION_ROOT}` (worktree path when active, otherwise `CODE_DIR`). In a single repo, translate `{FIS_PATH}` into that worktree; in a multi-repo run, keep the canonical absolute plan-repo path. Reviewer derives `STORY_ID` from its task name; before each initial/re-review unblock, the orchestrator sets exact task input `REVIEW_COMMIT: <full-sha>` to the implementation/repair commit. Scripts receive the bare story ID. Anything not substituted is derived at runtime.


## Implementer Prompt

Apply the **Worker Contract** from `exec-plan/SKILL.md` Step 3b. The team Implementer runs only the `exec-spec` half of the canonical Worker Prompt – the `quick-review` half is the Reviewer's task.

{UNTRUSTED_REQUIREMENTS_LINE}
{GOVERNING_PLAN_LINE}
CODE DIRECTORY: {IMPLEMENTATION_ROOT}

Per `impl-*` task assigned to you (orchestrator pre-assigns owners – work only your assigned tasks, no shared-queue claiming):
- `cd {CODE_DIR_ABS}` (worktree mode: `cd {WORKTREE_PATH_ABS}` instead).
- **Worktree mode** (`{WORKTREE_PATH_ABS}` non-empty), as first action after `cd`: `bash ${CLAUDE_SKILL_DIR}/scripts/verify-in-worktree.sh {STORY_ID} {WORKTREE_PATH_ABS}`. Anything other than `VERIFY_OK` → STOP, report `VERIFY_FAIL:<reason>`, fail the task. Subsequent operations use absolute paths only (relative paths silently leak to the main checkout). Pass the `## Deferred Shared Writes` audit block through to your report; do NOT stage `plan.json` or the State document inside the worktree branch – the `andthen:merge-resolve` skill's G2 guard fails the story.
- Invoke the `andthen:exec-spec` skill with `{FIS_PATH}{AUTO_SUFFIX}{DEFER_SUFFIX}`. The Worker Contract delegates exec-spec's standalone completion-presentation gate: skip it – the orchestrator owns the consolidated one.
- On success, require a non-empty story delta and confirm deferred `plan.json` / State writes are absent. Stage the attributable story delta, commit it with the brief subject `story {STORY_ID}`, and require the checkout clean. Report `IMPLEMENTATION_COMMIT: <full-sha>` plus `exec-spec` Step 4a numbers (build, tests, lint/type-check, format). Orchestrator handles squash-merge and cleanup. A missing commit, shared-write leak, or residual dirty status fails the task.
- On `BLOCKED:` or Failed Story Report: do not mark done; preserve the worktree and report details.


## Reviewer Prompt

Apply the **Worker Contract** from `exec-plan/SKILL.md` Step 3b. The team Reviewer runs only the `quick-review` half of the canonical Worker Prompt.

{UNTRUSTED_REQUIREMENTS_LINE}
{GOVERNING_PLAN_LINE}
INTENT CONTEXT: {FIS_PATH}

Per `review-*` task assigned to you (orchestrator pre-assigns owners; `impl-Sxx` and `review-Sxx` are never assigned to the same teammate, so self-review cannot occur):
- Derive story id by stripping `review-` from your task name (`review-S03` → `S03`).
- `cd {CODE_DIR_ABS}`.
- **Resolve `REVIEW_COMMIT`** from the task's exact input, require a commit object, and bind it to current state:
  - **Worktree mode**: require it to equal `git rev-parse story-<story-id>`, then create an unreferenced full-branch snapshot: `git commit-tree "story-<story-id>^{tree}" -p "$(git merge-base {BASE_BRANCH} story-<story-id>)" -m "review snapshot <story-id>"`. Require the snapshot tree to differ from its parent.
  - **No worktree mode**: require it to equal `git rev-parse HEAD`; use that exact SHA. Sequential dependencies guarantee no later implementation has started.
- **Substitute `<story-id>` and `<hex-sha>` as literals** (skill-invocation lines are not bash; `$VAR` and `<placeholder>` reach `quick-review` unexpanded). Invoke the `andthen:quick-review` skill with `story <story-id> commit <hex-sha>{AUTO_SUFFIX}` and preserve the exact `INTENT CONTEXT:` line.
- Apply `exec-plan` Step 3b class handling before routing: reconciliation classes return to the orchestrator's Step 3c persistence gate. For `code-defect`, Notes complete; Fix findings leave the task open for one repair/re-review and complete only when clear. No findings → complete.
- Do not call `andthen:ops update-*` yourself (Worker Contract).

## Task Management

**Naming**: `impl-{story_id}` / `review-{story_id}` (one impl + one review per story; one FIS per story).

**Pre-assignment** (no self-claim): at TeamCreate, the orchestrator round-robin distributes `impl-*` across implementer teammates and `review-*` across reviewer teammates, setting the `owner` field on every task. Same-task races are prevented by ownership, and self-review is prevented at assignment time – the same teammate is never assigned both `impl-Sxx` and `review-Sxx`. Teammates work only their assigned tasks; no claim discipline needed.

**Dependencies** (sequential, `USE_WORKTREE=false`): each `impl-*` is blocked by the previous `review-*`. In one repo, `AUTO_MODE` may unblock the next independent story after failure; multi-repo stops. Parallel markers ignored.

**Dependencies** (worktree, `USE_WORKTREE=true`): in one repo, current-wave `impl-*` tasks unblock together; multi-repo activates only the next story after the prior review, persistence, shared writes, and plan-repo commit. Each `review-*` waits for its implementation; merge waits for review pass or recorded failure.

**Failure containment**: a reported `BLOCKED:` first goes through **Worker `BLOCKED:` triage** (Step 3c). A repairable blocker re-opens the `impl-*` task once for its existing owner, reusing the story's existing worktree per `worktree-mode.md` → **Repair Topology**. After bounded repair, multi-repo preserves the plan delta and stops; in one repo the failed story blocks only its reviewer/dependents while `AUTO_MODE` continues independent work. No-worktree continuation requires a clean shared checkout.


## Merge Wave _(worktree mode only)_

After current-wave `impl-*` and `review-*` succeed or are recorded failed, run `worktree-mode.md` → **Merge Flow** for each reviewed-successful story in sequence, honoring its **Merge Ordering** gate before Wave N+1 worktrees are created. Failed-story classification, deferred shared writes, worktree cleanup, and ordering are owned by that reference.


## Status Updates Gate

Same green-gate discipline as Step 3c, then run the **Writes-Landed Checklist** per story.

Checklist source-of-truth by mode:
- **Worktree** – primary writes come from the Merge Flow's "apply deferred shared writes" substep, not the worktree branch; checklist and green-gate timing per `worktree-mode.md` → **Verification Timing**.
- **No worktree** – after the reviewer clears accepted Fix findings, apply Step 3c's Primary Shared Writes, then run the checklist; one-shot repair on miss. In a single repo, commit these orchestrator-owned shared writes before unblocking the next story and require the checkout clean. Green gate runs after each `impl-*`, before the matching `review-*` unblocks.

Also verify the **Plan Acceptance Gate** before `Done`: every FIS scenario/criteria checkbox is `[x]` (Final Validation Checklist when present), implementation observations present when the FIS narrowed scope, `review-*` task completed without accepted **Fix-routed** findings.

Pass → record in the ledger's `completed` list.

Advance to the next phase only after every current-phase story is verified green or recorded failed/skipped.

**Take-over topology** (orchestrator repair): commit the one bounded repair, re-open the matching `review-*` task with `REVIEW_COMMIT` set to the repair SHA, one re-run (worktree pre-merge: the reviewer creates a fresh full-branch snapshot). Clear/Note-only completes; persistent Fix fails the task. Repair locus: worktree runs per `worktree-mode.md` → **Repair Topology**; no-worktree repairs land on `{BASE_BRANCH}` in the orchestrator's CWD, and the checkout must again be clean before the next story starts.


## Multi-Repo Rules _(CODE_DIR ≠ PLAN_DIR's git root)_
- Implementation and merge git operations target `CODE_DIR`; worktree specifics per `worktree-mode.md` → **Multi-Repo Rules**.
- FIS paths passed to agents are **absolute**.
- Only the orchestrator updates plan/State files; the parent skill's Multi-repo FIS attribution rule owns serialization and commits.


## Monitoring

Print progress updates – the user cannot see agent activity. Report: task creation/assignment, agent starts/completions, wave completions, merge results, phase summaries, failures.


## Final Worktree Teardown _(worktree mode only)_

Run per `worktree-mode.md` → **Final Worktree Teardown**, including failure exits (see `exec-plan/SKILL.md` FAILURE HANDLING). After teardown (or directly, when `USE_WORKTREE=false`): shutdown teammates, delete team.
