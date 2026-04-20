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
- After each delegated story, the orchestrator re-reads the target files to confirm writes landed, and calls `andthen:ops update-*` exactly once if any is missing.
