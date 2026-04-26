---
source: plugin/skills/exec-plan/references/execution-discipline.md
---

# Execution Discipline

Shared rules for orchestration and execution skills.


## Stop-the-Line

Borrowed from Toyota. A red **objective gate** — failing build, tests, lint, type-check, stub check, wiring check, task-level `Verify` — is work to finish, not a delivery caveat. Do not advance past a red gate, do not mark `Done` on a broken tree, do not report the broken state as completion.


## Gate Classes

Two failure classes with different persistence policies:

| Class | Examples | Policy |
|---|---|---|
| **Objective red gate** | Build, tests, lint, type-check, stub/wiring check, task `Verify` | **Iterate until green.** Fix → re-run → repeat. Invoke the `andthen:triage` skill when iteration stalls. One-pass limits do **not** apply. |
| **Subjective finding** | Code-review CRITICAL/HIGH, visual-validation findings | **One pass max.** Focused remediation → re-run the relevant review lens → escalate if findings persist. |

Objective failures have binary answers and converge. Subjective findings drift and thrash — different policies on purpose.


## Real External Blockers

The only legitimate reasons to stop a run with unresolved work:

- Missing credentials or unavailable infrastructure
- Merge conflicts requiring human policy
- Missing or contradictory requirements the skill cannot resolve
- Repeated iteration failure on the *same* issue after running the `andthen:triage` skill

Partial sub-agent work, intermediate refactor state, and perceived scope overrun are **not** blockers — they are work to finish.


## Authoritative Status Writes

In orchestrated flows (e.g. `andthen:exec-spec` running under `andthen:exec-plan`):

- The **executing skill** writes its own story's status authoritatively via `andthen:ops` (plan.md story row, FIS field, FIS checkboxes, `State` active-story).
- **Delegating sub-agents and teammates do NOT additionally call `andthen:ops update-*`** on top of the executing skill — that duplicates writes.
- The **orchestrator** writes cross-story state only (phase transitions, overall status, session notes) plus *repair writes* when an executing-skill write is missing.
- After each delegated story, the orchestrator runs the **Writes-Landed Checklist** (`andthen:exec-plan` Step 3c) to confirm writes landed, and calls `andthen:ops update-*` exactly once per missing item to repair.

### Worktree Deferral

When the executing skill runs under `--defer-shared-writes` (typically `andthen:exec-spec --defer-shared-writes`, set automatically by `andthen:exec-plan --team --worktree`), the contract shifts to avoid concurrent worktree merges colliding on shared files:

- The executing skill writes **only** the FIS (story-local — merges cleanly).
- It defers `plan.md` and `State` document writes by emitting a `## Deferred Shared Writes (worktree mode)` **audit block** in its completion report — fields are `Story`, `Plan`, `FIS`, and `Completion summary`. The block is an audit record and summary source, not a script.
- The **orchestrator** constructs the actual `andthen:ops update-*` invocations from values it already knows (`STORY_ID`, `FIS_FILE_PATH`, `PLAN_FILE_PATH`) plus the completion summary from the audit block, and applies them as the **primary** write path (not a repair) immediately after merging that worktree, before the next worktree merges or Wave N+1 worktrees are created.
- Repo placement: writes land on `BASE_BRANCH` in single-repo (`PLAN_DIR == CODE_DIR`); in multi-repo (`PLAN_DIR ≠ CODE_DIR`) they land in `PLAN_DIR` (committed there if it is a git repo) and `CODE_DIR`'s history is unaffected.
- A missing audit block is **not** a Stop-the-Line — the orchestrator already has all required values; it falls back to a generated completion-summary string and proceeds, logging the miss as a worker self-report drift signal.
- The Writes-Landed Checklist runs *after* deferred writes are applied. A miss at that point is a real loss and triggers the same one-shot repair path.
