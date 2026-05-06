# Execution Discipline

Universal red-gate rules for skills that execute work (`andthen:exec-spec`, `andthen:exec-plan`, and any future executor).


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
