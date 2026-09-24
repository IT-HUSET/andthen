---
description: Execute a fully-specced plan bundle (every story has a FIS) – one fresh subagent per story, `--worktree` runs independent stories in parallel, full verification, then a `Next:` line handing the plan-level review to a fresh session. Trigger on 'execute the plan', 'implement all stories', 'run the stories in parallel'.
argument-hint: "[--auto] [--worktree] [--no-full-tier] <path-to-plan-directory>"
---

# Execute Plan

`PLAN_DIR` is `$ARGUMENTS` minus flags; `PLAN_PATH` is `PLAN_DIR/plan.json` absolute, resolved in Step 1 and used unchanged in Steps 2–4. `--auto` is `AUTO_MODE`, automation-safe execution with no conversational prompts. `--worktree` runs a batch's ready stories in parallel worktrees. `--no-full-tier` makes the fast tier the run gate in Step 3; the report names the tier that ran.

## INSTRUCTIONS

**You are the orchestrator**: you schedule stories and own the run's verification gate, while the `andthen:exec-spec` skill – one fresh subagent per ready story – owns everything inside one. Every dispatch below is a fresh subagent: the installed role agent (`implementer`) when available, else a generic inherited subagent; never pin model or effort in a prompt. The plan-level review is not yours: after N stories' reports this is the run's most loaded context, so the run ends by printing its invocation as `Next:`.

### Rules
- **Plan is source of truth, and you are its only writer** – `plan.json` per [`plan-schema.md`](../../references/plan-schema.md), which defines the ready set and the status transitions; you edit the rows with your own file tools and the stories you dispatch only read them. Run rounds serially and never persist a derived scheduling label.
- **Execution discipline** – Stop-the-Line on red gates, Resolution Ladder before stopping, per [`execution-discipline.md`](../../references/execution-discipline.md).
- **Automation rules** – see [`automation-mode.md`](../../references/automation-mode.md).

## WORKFLOW

### Step 1: Parse Plan

1. **Resolve the branch**: in the current git root, take `BASE_BRANCH` from its HEAD and `DEFAULT_BRANCH` from the repo's default (origin/HEAD, else local `main`/`master`), and print `BASE_BRANCH={value}`.
   - A mismatch confirms in default mode; `AUTO_MODE` proceeds after printing that the execution target `BASE_BRANCH={value}` differs from the repo default (`{DEFAULT_BRANCH}`) and that every story will land on `{value}`. An unintended target is worth a line; a milestone branch is not faulty, and neither branch resolving skips it.
   - Under `--worktree`:
     - No tracked file carries uncommitted changes – stories branch from HEAD and merge back into it, so dirt neither reaches them nor survives the merge.
     - The bundle is itself tracked (`git ls-files --error-unmatch {PLAN_DIR}/plan.json`) – an untracked bundle has no copy in a worktree to write at all.

     Either stops the run – never stash or commit what the run does not own.
2. Read `PLAN_DIR/plan.json`, stopping when absent – the `andthen:plan` skill owns producing it – or on anything in it contradicting `plan-schema.md`, with the evidence; never schedule a catalog you could not read. Set `PLAN_PATH` absolute.
3. **Resolve FIS files**: `spec-ready` and `in-progress` stories need a canonical pointer resolving to a file, and `pending` is rejected. Failure: `Plan bundle has non-ready or missing FIS – run the andthen:plan skill on {PLAN_DIR} to repair it (plan is resumable).`
4. Initialize the run ledger (`completed`, `failed`, `skipped`, `blocked_by`): it feeds the aggregate report, while `plan.json` records the `done` transitions. Story state decides what the ledger takes:
   - `done` – no longer a candidate, but still in Step 3's scope, so an all-done rerun still verifies the tree.
   - a skipped or failed dependency – records each dependent as skipped with `blocked_by`.

**Gate**: `plan.json` parsed and valid; every schedulable story's FIS pointer resolves to a file; the dependency graph is ready

### Step 2: Dependency-Ready Batch Loop

Re-read `plan.json` before each batch and take that ready set in source order. If candidates remain but none is ready, stop with the dependency evidence: a cycle or an edge nothing satisfies surfaces exactly here, and those stories stay unstarted in the closing report.

- **Without `--worktree`** – run the ready set one story at a time, because a shared tree shares one test run.
- **With `--worktree`** – dispatch the batch at once, up to what you can triage in one re-read (about five), and merge every return before the next batch, so dependents branch from a base that holds what they depend on. Read [`story-worktrees.md`](references/story-worktrees.md) before the first dispatch.

#### Execute and triage each story

For each ready story, claim the row – `in-progress` and your `owner` – then spawn a fresh implementer subagent that invokes the `andthen:exec-spec` skill with `--auto --no-full-tier {FIS_PATH}`, saying that the plan row is yours and it reports its state rather than writing it. `--auto` on every story and never `--tdd`; the FIS names its own plan, so no further argument passes. That subagent owns the story whole, down to the code commit – so add no second review, and the full tier it deferred is Step 3's. Await the completed result – a progress message is not completion – and keep a failed or partial one: it returns a completion report or a `## Failed Story Report`.

Then write that story's row from the fields its result carries, copied unchanged, releasing `owner` with the terminal status, and commit the bundle write.

**Story-scoped containment** – a failed story is not `done` and does not unblock dependents. Its progress stays resumable, dependents never attempted are `skipped`, and `AUTO_MODE` continues independent stories only where the failed changes are provably isolated – always so under `--worktree`, where they never left the story's worktree – stopping otherwise. Never start a second writer over its unfinished edits.

Append a success – id, FIS path, verification summary, open findings, Drift Notes – to `completed`; record a failure's id, FIS, evidence, and Failed Story Report.

**Gate**: each story is verified and completed, or contained as failed/skipped, its terminal writes confirmed before the next round.

#### Batch discovery triage

After each batch, route discoveries affecting an unstarted story into its FIS before dispatch: a scope-preserving constraint under `## Discovered Requirements`, a contract change as a decision – asked, or under `AUTO_MODE` its recommendation recorded per `automation-mode.md` § Recording an assumption.

### Step 3: Final Verification

Run whenever at least one story is `done` – each got only the fast tier, so a partial run's retained code is otherwise unverified: build, lint/types, cross-story integration, and the full tier each story deferred, or the fast tier under `--no-full-tier`, on the final tree. Report the evidence fields from [`verification-evidence.md`](../../references/verification-evidence.md) plus the integration result on two lines: `Scope: complete` or `Scope: incomplete – {failed/skipped ids}`, and `Verification: passed`, `failed – {evidence}`, or `not run – {reason}` when a failed story's leftovers make the checks impossible – named, never an implied pass.

A red gate is iterated to green, each repair round a fresh implementer subagent that invokes the `andthen:triage` skill with `--auto` and a scope naming the failing checks – the commands and what they returned – and the affected FIS paths. The assigned checks bound the work, so no original task is replayed and no `completedTaskIds` entry is added. Require changed paths and check evidence, then re-run what the repair invalidated. A round that turns nothing green, changes outside the repository, or malformed output fails the run with the open checks and affected stories. Completed stories stay `done`: a red run gate blocks the run's success claim, not evidence already executed. Commit a repair with `git add -- {paths}` then `git commit -- {paths}`, whose pathspec ignores another session's staged work, under the owning story's trailers; report any other change as pending the user's commit, by path.

**Gate**: build, the run tier's tests, linting/types, and integration pass on the final tree

### Step 4: Aggregate Completion Report

Always write a deterministic summary: completed stories with `Reviewed:` lines verbatim, batches executed, the `Scope:` and `Verification:` lines, tree state and commands run, repairs pending the user's commit, `PLAN_PATH`. Success needs green verification from this invocation on the final tree; a gate skipped, unavailable, or run on an earlier tree cannot produce it.

**Notes rollup**: each completed story's open findings and Drift Notes, with recommend-only reconciliation for every stale upstream target they name; read the FIS observations, `none` when absent.

End with exactly one `Next (fresh session):` line carrying the one invocation this run does not perform, written in the host's own slash-command syntax so it pastes as-is into a new conversation: the `andthen:review` skill with `--mode code,gap,security,outcome --fix {PLAN_PATH}` (`--fix` runs `implement-fix` on the report), `--auto` appended in `AUTO_MODE`; under `--no-full-tier` the line opens with running the full tier first.

Scope it to the `done` stories: where any story failed or was skipped, the line names those `done` ids after `{PLAN_PATH}`; where none is `done`, it is replaced by `Next: no completed stories – nothing to review.` A review over the whole plan raises gap findings against stories nobody implemented.

Nothing closes the bundle: `plan.json` and the FIS files go with the merge.

If any story failed or was skipped, add `Completed`, `Failed`, `Skipped`, and `Blocked by` sections – story ids, FIS paths, failure evidence, report paths, preserved worktrees.

**Gate**: the aggregate report exists with its `Next (fresh session):` line scoped to what is `done`, or the no-completed-stories line in its place; unresolved failures visible to the next run.
