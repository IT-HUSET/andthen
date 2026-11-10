---
description: Execute a FIS, or a plan directory with one fresh subagent per story (`--worktree` runs independent stories in parallel) – implement, verify against its own proofs, review, complete on executed proof. Trigger on 'implement this FIS', 'execute the plan', 'run the stories in parallel'.
argument-hint: "[--auto] [--worktree] [--no-full-tier] <path-to-fis | plan directory>"
---

# Execute Feature Implementation Specification

Execute a FIS, or a plan with one fresh subagent per story, verify against its proofs, and complete on executed proof.

## Input

`$ARGUMENTS`, minus flags, is a FIS (`FIS_FILE_PATH`), or a plan directory or its `plan.json` (`PLAN_DIR` is the directory).

- `--auto` makes the run unattended: read [`unattended-runs.md`](../../references/unattended-runs.md) and follow it.
- `--worktree` runs a plan run's ready stories in parallel worktrees.
- `--no-full-tier` runs the fast tier where the run would run the full one, for a caller that runs the full tier on the final tree.

## Rules

- Print each recommended skill invocation as a complete, paste-ready line in the host's syntax, including its target path or request and required arguments.
- **Stop-the-Line.** A red objective gate – build, tests, lint, type-check, a substance or wiring scan, a task's `Verify` – is work to finish, not a delivery caveat.
  - Iterate it to green, invoking the `andthen:triage` skill when iteration stalls, and never write `Done` on a broken tree.
  - Partial subagent work, an intermediate refactor state, and a story's size or difficulty are work to finish too: a spec that should have been split is an upstream problem.
  - None of these stops a run.
    An open question ends one only on the Ladder's last rung.
    A red gate ends one when a repair through the `andthen:triage` skill turns nothing green.
- **Resolution Ladder.** An artifact conflict or an ambiguity you cannot settle locally is an investigation. Climb in order, stop at the first rung that answers, and name it:
  1. **Re-read** the intent anchor and its Required Context, which confirms a reading but adds no evidence.
  2. **Widen** to the governing PRD, ADRs, decisions, and code. Authority and trust decide first; specificity and recency break ties only among peers. A cross-authority conflict needs an amendment or a user decision.
  3. **Delegate** reconnaissance or a documentation lookup to a worker subagent, a design question to the `andthen:architecture` skill, or a feasibility question to an empirical `andthen:spike` skill. Skip a spike during parallel work on a shared checkout.
  4. **Work around** through a sanctioned amendment path, else on the narrowest defensible reading, never as the cheap way past a gate. Record a code↔FIS divergence as a Drift Note, and an outcome-neutral reading as an `ASSUMPTION:` line (`unattended-runs.md` § Recording an assumption) or a Discovered Requirement.
  5. **Stop** when no rung answered and no reading is defensible, naming the rungs tried.

  Stopping on what an earlier rung answers is the dominant cause of premature aborts in unattended runs.
- **Every dispatch is a fresh subagent**: the installed role agent it names (`implementer`, `reviewer`, `worker`) when available, else a generic inherited subagent. Never pin model or effort in a prompt. Dispatch in the foreground (`run_in_background: false` on Claude Code) and await each required result within your turn, because a progress message is not completion and a subagent's ended turn hands its run back. Keep failed or partial evidence.

## Workflow

### 1. Feature branch

Outside `--auto`, when the current branch is the remote's default branch, ask once whether to start a feature branch first, because commits land on the current branch and the pull request opens from it. Recommend starting it the way the project's written convention for starting work says, else as `<type>/<slug>`.

### 2. Route

Your mode is the first that matches:

- **Dispatched story run**: a FIS, where your request says you are a story subagent of an `andthen:exec-plan` plan run.
- **Direct story run**: any other FIS, even with a `plan.json` beside it, as one sits beside every FIS the `andthen:plan` skill writes.
- **Plan run**: a plan directory or its `plan.json`.

Read every file marked for your mode, then follow its procedure to the end.

| File | Dispatched story run | Direct story run | Plan run |
|---|---|---|---|
| [`story.md`](references/story.md), the story procedure | yes | yes | |
| [`plan-run.md`](references/plan-run.md), the plan procedure | | | yes |
| [`between-stories.md`](references/between-stories.md), triage and simplify | no | yes | yes |
| [`story-worktrees.md`](references/story-worktrees.md) | | | under `--worktree` |
| [`fis-contract.md`](../../references/fis-contract.md) | yes | yes | |
| [`plan-schema.md`](../../references/plan-schema.md) | | | yes |
| [`fis-mutability.md`](../../references/fis-mutability.md), [`verification-evidence.md`](../../references/verification-evidence.md) | yes | yes | yes |

## Follow-up

A failed story's route out is the `andthen:review` skill with `--fix` over the story's changed paths, for correctness and against its FIS, `<absolute FIS path>`, then this skill again on the same input. Under `--worktree` the review runs in the story's preserved worktree.

Close on one `Next (fresh session):` line. A dispatched story run prints none, and a plan run closes per `plan-run.md` Step 4. A direct story run that stopped at admission, or has written `done` or a `## Failed Story Report`, takes the first case that applies:

- **The story failed** – its route out.
- **The person chose a revision at triage** (never in an unattended run) – the `andthen:clarify` skill's amendment on the PRD for a scope change, else the `andthen:plan` skill on `"story <id> of <plan.json> – <the discovery, and the FIS's other Discovered Requirements>; revise its FIS"` for the first story whose FIS needs it, since `plan` writes from its request and never reads the old FIS.
- **A dependency-ready story is left** – this skill on the first such story's FIS.
- **Every story is `done` or `skipped`** – the plan-level review.
- **Otherwise** – this skill on the plan directory.

The plan-level review is the `andthen:review` skill with `--fix {plan.json}`.
