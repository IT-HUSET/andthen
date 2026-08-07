# Execution Discipline

Universal red-gate rules for skills that execute work (the `andthen:exec-spec` and `andthen:exec-plan` skills, and any future executor).


## Stop-the-Line

Borrowed from Toyota. A red **objective gate** – failing build, tests, lint, type-check, stub check, wiring check, task-level `Verify` – is work to finish, not a delivery caveat. Do not advance past a red gate, do not mark `Done` on a broken tree, do not report the broken state as completion.


## Gate Classes

Two failure classes with different persistence policies:

| Class | Examples | Policy |
|---|---|---|
| **Objective red gate** | Build, tests, lint, type-check, stub/wiring check, task `Verify` | **Iterate until green.** Fix → re-run → repeat. Invoke the `andthen:triage` skill when iteration stalls. One-pass limits do **not** apply. |
| **Subjective finding** | Code-review CRITICAL/HIGH, visual-validation findings | **One pass max.** Focused remediation → re-run the relevant review lens → escalate if findings persist. |

Objective failures have binary answers and converge. Subjective findings drift and thrash – different policies on purpose.


## Resolution Ladder (Block Last)

Treat artifact conflict or locally unresolved ambiguity as investigation. Climb in order, stop at the first answer, and name the rung:

1. **Re-read** – the intent anchor and deeper-context pointers; this confirms a reading but adds no evidence.
2. **Widen** – inspect governing PRD/ADRs/decisions and code. Authority and trust decide first; specificity and recency break ties only among peers. Cross-authority conflict needs amendment or a user decision.
3. **Delegate** – reconnaissance, documentation lookup, the `andthen:architecture` skill, or an empirical `andthen:spike` skill. Skip a spike during parallel work on a shared checkout.
4. **Work around** – take any sanctioned amendment path; otherwise use the narrowest defensible reading – working around must never become the cheap way past a gate. Persist code/FIS divergence as an OPEN ledger entry (it blocks shipping); record an outcome-neutral reading as `ASSUMPTION:` or a Discovered Requirement.
5. **Block** – no rung answered, or the user owns the decision. Name the rungs tried.

A `BLOCKED:` answerable by an earlier rung is a **false blocker** – the dominant cause of premature aborts in unattended runs.


## Real External Blockers

The only legitimate reasons to stop a run with unresolved work:

- Missing credentials or unavailable infrastructure
- Merge conflicts requiring human policy
- A decision the user owns – product intent, an external commitment, a trade-off with organizational consequences
- Missing or contradictory requirements still unresolved after the Resolution Ladder
- Repeated iteration failure on the *same* issue after running the `andthen:triage` skill

Partial sub-agent work, intermediate refactor state, and perceived scope overrun are **not** blockers – they are work to finish.
