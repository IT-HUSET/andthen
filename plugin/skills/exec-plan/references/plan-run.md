# Plan Run

You are the orchestrator: you schedule stories and own the run's verification gate, while one fresh subagent per ready story owns everything inside it, its `plan.json` row included. You write no row, except under `--worktree`, where you mark each batch `in-progress` before it branches. `PLAN_PATH` is `PLAN_DIR/plan.json`, absolute.

## Step 1: Parse the plan

1. **Branch.** Ask `verification-evidence.md` § The commit rule's feature-branch question here, before any dispatch, because every story commits to the branch it starts on. Then take `BASE_BRANCH` from the current git root's HEAD and print `BASE_BRANCH={value}`.
   - Under `--worktree`, stop when a tracked file carries uncommitted changes, rather than stash or commit what the run does not own: stories branch from HEAD and merge back into it, so that dirt neither reaches them nor survives the merge.
   - Under `--worktree`, stop too when the bundle is untracked (`git ls-files --error-unmatch {PLAN_DIR}/plan.json`): a worktree holds no copy of it to write, and a story's row reaches the main checkout only through the merge.
2. **Read `plan.json`.** Stop when it is missing – the `andthen:plan` skill owns producing it – or not parseable JSON.
3. **Resolve FIS files.** Every `pending` and `in-progress` story needs a canonical pointer resolving to a file. On failure, stop naming each such story and the `andthen:plan` skill as its route.

## Step 2: Waves

Re-read `plan.json` before each batch and take its wave, the stories now dependency-ready, in source order. When candidates remain but none is ready, stop with the dependency evidence: a cycle or an edge nothing satisfies surfaces here, and those stories stay unstarted in the report.

- **Without `--worktree`**, run the wave one story at a time, because a shared tree shares one test run.
- **With `--worktree`**, dispatch a batch of the wave at once, up to what you can triage in one re-read (about five), and merge every return before the next batch, so dependents branch from a base holding what they depend on.

**Dispatch** a fresh implementer subagent that invokes the `andthen:exec-plan` skill on `{FIS_PATH}`, telling it it is a story subagent of an `andthen:exec-plan` plan run, with:
- `--auto`, whether or not this run carries it, since nobody is watching a story subagent;
- `--no-full-tier`, since this run owns the integrated checks in Step 3.

The FIS names its own plan, so no further argument passes. The subagent owns the story whole, so add no second review.

**Return.** It returns a completion report or a `## Failed Story Report`. A completion counts only once the re-read `plan.json` shows its row `done`; otherwise the story failed. Under `--worktree` that is the copy in the story's worktree, read before the merge, which then brings the row to the main checkout.

**Containment.** Report a failed story's dependents `skipped`, with `blocked_by`, in the run report only: their rows stay unchanged, because `skipped` is terminal and they would never run again. An unattended run continues independent stories only where the failed changes are provably isolated – always so under `--worktree`, where they never left the story's worktree – and stops otherwise. Never start a second writer over a failed story's unfinished edits.

**Between stories.** After each story, or each batch under `--worktree`, take both steps of `between-stories.md` before the next dispatch or Step 3.

## Step 3: Final verification

Whenever at least one story is `done`, a partial or resumed run included, verify the combined revision after simplification, because each story ran only its focused checks:

1. Collect the obligations: build, lint/types, cross-story integration, the full tier, the plan-final checklist items, and the deferred commands in each `done` FIS's Implementation Observations. A `done` FIS you cannot read leaves its obligations outstanding.
2. Run each once on that tree. A tier run covers each item whose command, configurations, and assertions it exercises. Under `--no-full-tier`, run fast; what only full covers stays outstanding for the caller.
3. Report the checked revision and, per obligation, its source and the command and result that covered it, or why it is outstanding, with the evidence fields of `verification-evidence.md`, then the integration result on two lines:

- `Scope: complete` or `Scope: incomplete – {failed/skipped ids}`;
- `Verification: passed` only when every obligation passed on that revision, `failed – {evidence}` for a red gate, or `not run – {outstanding checks and reason}`.

Each repair round of a red gate is a fresh implementer subagent that invokes the `andthen:triage` skill with `--auto` and a scope naming the failing checks – the commands and what they returned – and the affected FIS paths. The assigned checks bound the work, so no original task is replayed. Require its changed paths, left uncommitted for this run, and check evidence, then re-run what the repair invalidated.

A round that turns nothing green, changes anything outside the repository, or returns malformed output fails the run with the open checks and the affected stories. A repair writes no `plan.json` row: a red run gate blocks the run's success claim, not evidence already executed.

Commit a repair per `verification-evidence.md` § The commit rule, under the owning story's trailers. Report any other change by path, as pending the user's commit.

## Step 4: Aggregate report

Always write the summary, leading with what the person reads in place of the stories' diffs:

- the `Scope:` and `Verification:` lines;
- each completed story's **How it works** and `Reviewed:` blocks, verbatim;
- **Where to read closely**: one list of the lines the stories' reports carry under that name, copied under their story IDs, without the checks Step 3 has since run;
- **Decided without asking**: one list, never omitted, holding:
  - every line a story's report carries under that label, copied under its story ID;
  - each `ASSUMPTION:` line or triage resolution this run or a subagent it dispatched recorded;
  - `none`, when there is neither.

Below them, as reference: the batches executed, tree state and commands run, changes pending the user's commit, and `PLAN_PATH`.
Success needs green verification from this invocation on the final tree; a gate skipped, unavailable, or run on an earlier tree cannot produce it.

Where any story failed or was skipped, add `Completed`, `Failed`, `Skipped`, and `Blocked by` sections: story ids, FIS paths, failure evidence, report paths, preserved worktrees. Each failed story gets its route out.

**Notes rollup**: each completed story's open findings and any Drift Note the list above does not carry, or `none`, and every stale upstream target a Drift Note names, with a recommend-only reconciliation.

Leave `plan.json` and the FIS files in place: the `andthen:ship` skill deletes or keeps them, on the user's answer, when the plan's branch ships.

**The plan-level review is not yours**: after every story's report this is the run's most loaded context. End with exactly one `Next (fresh session):` line carrying it on `{PLAN_PATH}`, plus `--auto` in an unattended run. Where the person stopped the run on a revision at triage, end on the skill's Follow-up revision line instead, because a review of the old spec would be spent. Open the review handoff with any integrated check still to fix or run, including the caller's full tier under `--no-full-tier`. Scope it to the `done` stories, because a review over the whole plan raises gap findings against stories nobody implemented: where any story failed or was skipped, name the `done` ids after `{PLAN_PATH}`. Where none is `done`, print `Next: no completed stories – nothing to review.` instead.
