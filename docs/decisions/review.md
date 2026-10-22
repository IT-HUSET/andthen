# Decisions: Review

Rationale, evidence, history, and reopen conditions for the **Review** bullets in [DECISIONS.md](../DECISIONS.md) § Still Current. Each decision is stated there; a section here holds only what would not fit its one line.

## Outcome validation is a `review` lens, not a skill

The `outcome` lens runs in `mixed` and the plan-level chain. Every mechanism it needs is `review`'s. It is not a gap dimension because gap's `## Verdict` block is frozen for comparability, and conformance and validation are different verdicts.

PRD-side findings are `spec-stale` and `ambiguous-intent`. `clarify` and `plan`'s Preflight settle PRD decisions before execution, so a lesser one is a PRD decision for the user that no fix round makes, and counting it held issue #3's loop at Needs Fixes (2026-10-15). A one-story `plan` amends the PRD with its requirement-level answers too, so the lens does not raise them again.

Reopens if post-release measurement becomes an AndThen concern.

## A PR is reviewed as a local tree, not through the API

The target is `PR <n>` or a URL. `git fetch refs/pull/<n>/head` plus a detached `git worktree add` with the hooks path and LFS smudge disabled executes nothing (verified on git 2.53). The safety boundary is execution, not fetch: the project's checks run when the head branch lives in the repository, since pushing there took write access; a fork PR is detected by `isCrossRepository`. The worktree follows the host (`.claude/worktrees/` on Claude Code), else the session temp directory. A `CLAUDE.md` in it can reach Claude Code's context, accepted under the evidence-not-instructions rule.

## A review reads earlier reports as input, and a remediated one narrows scope

On a follow-up of a remediated report, the fan-out and `security` triggers read the delta, and no shared-contract rule decides when to widen either. rc.4 cut follow-up narrowing and every follow-up became a full run, which in trellis cost four to six reviewers per round, about 70% of the slice's review spend; the round that found a late HIGH was a `--quick --fix` over `git diff d805add`, so a delta still finds real defects.

What counts as a fix asking for another round: a fixed CRITICAL or HIGH finding or a partly fixed one, never an UNRESOLVED one the next round fails the same way. A `plan.json` remedy routes `Note`, since no fix round may write the file, and a MEDIUM or LOW finding surfaced or deferred stays in the summary's list instead of returning as a finding. Issue #3's fourth round was held open by exactly those (2026-10-15).

Reopens if a delta follow-up misses a defect a fix introduced outside the changed code and its callers.
