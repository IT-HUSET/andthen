---
description: Execute a FIS, or a plan directory with one fresh subagent per story (`--worktree` runs independent stories in parallel) – implement, verify against its own proofs, review, complete on executed proof. Trigger on 'implement this FIS', 'execute the plan', 'run the stories in parallel'.
argument-hint: "[--auto] [--tdd] [--worktree] [--no-full-tier] <path-to-fis | plan directory>"
---

# Execute Feature Implementation Specification

Execute a FIS, or a plan with one fresh subagent per story, verify against its proofs, and complete on executed proof.

## Input

`$ARGUMENTS`, minus flags, is a FIS (`FIS_FILE_PATH`) or a plan directory or its `plan.json` (`PLAN_DIR` is the directory).

- `--auto` makes the run unattended: read [`unattended-runs.md`](../../references/unattended-runs.md) and follow it.
- `--tdd` writes tests first.
- `--worktree` runs a plan's ready stories in parallel worktrees.
- `--no-full-tier` runs the fast tier where the run would run the full one, for a caller that runs the full tier on the final tree.

## Rules

- Print each recommended skill invocation as a complete, paste-ready line in the host's syntax, including its target path or request and required arguments.

- **Stop-the-Line.** A red objective gate – build, tests, lint, type-check, a substance or wiring scan, a task's `Verify` – is work to finish, not a delivery caveat. Iterate it to green, invoking the `andthen:triage` skill when iteration stalls, and never write `Done` on a broken tree. Partial subagent work, an intermediate refactor state, and a story's size or difficulty are work to finish too: a spec that should have been split is an upstream problem. None of these stops a run; only the Ladder's last rung ends one on an open question.
- **Resolution Ladder.** An artifact conflict or an ambiguity you cannot settle locally is an investigation. Climb in order, stop at the first rung that answers, and name it:
  1. **Re-read** the intent anchor and its Required Context, which confirms a reading but adds no evidence.
  2. **Widen** to the governing PRD, ADRs, decisions, and code. Authority and trust decide first; specificity and recency break ties only among peers. A cross-authority conflict needs an amendment or a user decision.
  3. **Delegate** reconnaissance or a documentation lookup to a worker subagent, a design question to the `andthen:architecture` skill, or a feasibility question to an empirical `andthen:spike` skill. Skip a spike during parallel work on a shared checkout.
  4. **Work around** through a sanctioned amendment path, else on the narrowest defensible reading, never as the cheap way past a gate. Record a code↔FIS divergence as a Drift Note, and an outcome-neutral reading as an `ASSUMPTION:` line (`unattended-runs.md` § Recording an assumption) or a Discovered Requirement.
  5. **Stop** when no rung answered and no reading is defensible, naming the rungs tried.

  Stopping on what an earlier rung answers is the dominant cause of premature aborts in unattended runs.
- **The commit rule: commit only your own changes.** Stage by path, never `-A` or `-u`, and commit by path (`git commit -- <paths>`), because a plain commit takes whatever another session has staged. A file that also holds someone else's change stays uncommitted and goes in the report.
- **Every dispatch is a fresh subagent**: the installed role agent it names (`implementer`, `reviewer`, `worker`) when available, else a generic inherited subagent. Never pin model or effort in a prompt. Await each required result, because a progress message is not completion, and keep failed or partial evidence.

## Workflow

### 1. Route

Route on the path you were given, never on what sits beside it: every FIS the `andthen:plan` skill writes has a `plan.json` beside it. Read and follow:

- A FIS (story run): [`story.md`](references/story.md), [`fis-contract.md`](../../references/fis-contract.md), [`fis-mutability.md`](../../references/fis-mutability.md).
- A plan directory or its `plan.json` (plan run): [`plan-run.md`](references/plan-run.md), [`plan-schema.md`](../../references/plan-schema.md).
- A plan run under `--worktree`: [`story-worktrees.md`](references/story-worktrees.md).
- Every run: [`verification-evidence.md`](../../references/verification-evidence.md).

### 2. Simplify

Make it work, then make it good: the plan's change set is simplified once, on the finished whole. Only a run that completes the plan, every story `done` or `skipped`, simplifies: a plan run that took a story to `done`, once its gate is green; a story run no plan run dispatched, once it has committed.

Dispatch a fresh implementer subagent that invokes the `andthen:simplify-code` skill with `--auto` on the code paths the plan's commits changed – they carry its `Plan:` trailer – naming the plan's `plan.json` and handing over the latest green check results as its baseline. As for a repair, re-run what its change invalidated, then commit it per the commit rule as one `refactor` commit carrying the `Plan:` trailer; the plan-level review covers it. Report what it applied and deferred.

## Follow-up

A failed story's route out is the `andthen:review` skill with `--fix` over the story's changed paths, for correctness and against its FIS, `<absolute FIS path>`, then this skill again on the same input. Under `--worktree` the review runs in the story's preserved worktree.

Close on one `Next (fresh session):` line. A story a plan run dispatched prints none, and a plan run closes per `plan-run.md` Step 4. A story run takes the first case that applies:

- **The story failed** – its route out.
- **A dependency-ready story is left** – this skill on that story's FIS.
- **Every story is `done` or `skipped`** – the plan-level review.
- **Otherwise** – this skill on the plan directory.

The plan-level review is the `andthen:review` skill with `--fix {plan.json}`.
