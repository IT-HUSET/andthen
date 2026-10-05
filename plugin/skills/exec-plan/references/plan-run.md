# Plan Run

You are the orchestrator: you schedule stories and own the run's verification gate, while one fresh subagent per ready story owns everything inside it, its `plan.json` row included. You write no row, except under `--worktree`, where you mark each batch `in-progress` before it branches. `PLAN_PATH` is `PLAN_DIR/plan.json`, absolute.

## Step 1: Parse the plan

1. **Branch.** Take `BASE_BRANCH` from the current git root's HEAD and print `BASE_BRANCH={value}`.
   - Under `--worktree`, stop when a tracked file carries uncommitted changes, rather than stash or commit what the run does not own: stories branch from HEAD and merge back into it, so that dirt neither reaches them nor survives the merge.
   - Under `--worktree`, stop too when the bundle is untracked (`git ls-files --error-unmatch {PLAN_DIR}/plan.json`): a worktree holds no copy of it to write, and a story's row reaches the main checkout only through the merge.
2. **Read `plan.json`.** Stop when it is missing – the `andthen:plan` skill owns producing it – or not parseable JSON.
3. **Resolve FIS files.** Every `pending` and `in-progress` story needs a canonical pointer resolving to a file. On failure, stop naming each such story and the `andthen:plan` skill as its route.

## Step 2: Waves

Re-read `plan.json` before each batch and take its wave, the stories now dependency-ready, in source order. When candidates remain but none is ready, stop with the dependency evidence: a cycle or an edge nothing satisfies surfaces here, and those stories stay unstarted in the report.

- **Without `--worktree`**, run the wave one story at a time, because a shared tree shares one test run.
- **With `--worktree`**, dispatch a batch of the wave at once, up to what you can triage in one re-read (about five), and merge every return before the next batch, so dependents branch from a base holding what they depend on.

**Dispatch** a fresh implementer subagent that invokes the `andthen:exec-plan` skill on `{FIS_PATH}`, telling it a plan run dispatched it, with:
- `--auto`, whether or not this run carries it, since nobody is watching a story subagent;
- `--no-full-tier`, since the full tier it defers is Step 3's;
- `--tdd` when this run received it.

The FIS names its own plan, so no further argument passes. The subagent owns the story whole, down to the commit of its code and its row, so add no second review.

**Return.** It returns a completion report or a `## Failed Story Report`. A completion counts only once the re-read `plan.json` shows its row `done`; otherwise the story failed. Under `--worktree` that is the copy in the story's worktree, read before the merge, which then brings the row to the main checkout.

**Containment.** Report a failed story's dependents `skipped`, with `blocked_by`, in the run report only: their rows stay unchanged, because `skipped` is terminal and they would never run again. An unattended run continues independent stories only where the failed changes are provably isolated – always so under `--worktree`, where they never left the story's worktree – and stops otherwise. Never start a second writer over a failed story's unfinished edits.

**Batch discovery triage.** After each batch, route a discovery that affects an unstarted story into its FIS before dispatch: a scope-preserving constraint under `## Discovered Requirements`, a contract change as a decision – asked, or in an unattended run its recommendation recorded per `unattended-runs.md` § Recording an assumption.

## Step 3: Final verification

Run it whenever at least one story is `done`: each got only the fast tier, so a partial run's retained code is otherwise unverified. On the final tree, run build, lint/types, cross-story integration, and the full tier the stories deferred, or the fast tier under `--no-full-tier`. Report the tier that ran and the evidence fields of `verification-evidence.md`, then the integration result on two lines:

- `Scope: complete` or `Scope: incomplete – {failed/skipped ids}`;
- `Verification: passed`, `failed – {evidence}`, or `not run – {reason}` when a failed story's leftovers make the checks impossible.

Each repair round of a red gate is a fresh implementer subagent that invokes the `andthen:triage` skill with `--auto` and a scope naming the failing checks – the commands and what they returned – and the affected FIS paths. The assigned checks bound the work, so no original task is replayed. Require its changed paths and check evidence, then re-run what the repair invalidated.

A round that turns nothing green, changes anything outside the repository, or returns malformed output fails the run with the open checks and the affected stories. A repair writes no `plan.json` row: a red run gate blocks the run's success claim, not evidence already executed.

Commit a repair per the commit rule, under the owning story's trailers. Once the gate is green, simplify when the skill's Workflow step 2 applies. Report any other change by path, as pending the user's commit.

## Step 4: Aggregate report

Always write the summary: completed stories with their `Reviewed:` lines verbatim, the batches executed, the `Scope:` and `Verification:` lines, tree state and commands run, repairs pending the user's commit, and `PLAN_PATH`. Success needs green verification from this invocation on the final tree; a gate skipped, unavailable, or run on an earlier tree cannot produce it.

Where any story failed or was skipped, add `Completed`, `Failed`, `Skipped`, and `Blocked by` sections: story ids, FIS paths, failure evidence, report paths, preserved worktrees. Each failed story gets its route out.

**Notes rollup**: each completed story's open findings and Drift Notes, or `none`, every stale upstream target they name with a recommend-only reconciliation.

Leave `plan.json` and the FIS files in place: the `andthen:ship` skill deletes them when the plan's branch ships.

**The plan-level review is not yours**: after every story's report this is the run's most loaded context. End with exactly one `Next (fresh session):` line carrying it on `{PLAN_PATH}`, plus `--auto` in an unattended run. Under `--no-full-tier` the line opens with running the full tier first. Scope it to the `done` stories, because a review over the whole plan raises gap findings against stories nobody implemented: where any story failed or was skipped, name the `done` ids after `{PLAN_PATH}`. Where none is `done`, print `Next: no completed stories – nothing to review.` instead.
