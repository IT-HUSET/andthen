# Execution Discipline

Universal red-gate rules for skills that execute work: what stops a run, what must be iterated to green, and what to climb before blocking.


## Stop-the-Line

A red **objective gate** – failing build, tests, lint, type-check, stub check, wiring check, task-level `Verify` – is work to finish, not a delivery caveat: `Done` is not written on a broken tree.


## Gate Classes

Two failure classes with different persistence policies:

| Class | Examples | Policy |
|---|---|---|
| **Objective red gate** | Build, tests, lint, type-check, stub/wiring check, task `Verify` | **Iterate until green.** Fix → re-run → repeat. Invoke the `andthen:triage` skill when iteration stalls. One-pass limits do **not** apply. |
| **Subjective finding** | Code-review CRITICAL/HIGH, visual-validation findings | **One repair round.** The Fix-routed fixes are applied once, by the actor the skill assigns; re-run what they invalidated, report what stays open; the next review is a separate request. |

Objective failures converge; subjective findings thrash.


## Resolution Ladder (Block Last)

Treat artifact conflict or locally unresolved ambiguity as investigation. Climb in order, stop at the first answer, and name the rung:

1. **Re-read** – the intent anchor and deeper-context pointers; this confirms a reading but adds no evidence.
2. **Widen** – inspect governing PRD/ADRs/decisions and code. Authority and trust decide first; specificity and recency break ties only among peers. Cross-authority conflict needs amendment or a user decision.
3. **Delegate** – reconnaissance, documentation lookup, the `andthen:architecture` skill, or an empirical `andthen:spike` skill. Skip a spike during parallel work on a shared checkout.
4. **Work around** – take any sanctioned amendment path; otherwise use the narrowest defensible reading – working around must never become the cheap way past a gate. Persist code/FIS divergence as a FIS Drift Note; record an outcome-neutral reading as `ASSUMPTION:` or a Discovered Requirement.
5. **Block** – no rung answered, or the user owns the decision. Name the rungs tried.

A `BLOCKED:` answerable by an earlier rung is a **false blocker** – the dominant cause of premature aborts in unattended runs.


## Real External Blockers

What legitimately stops a run is `automation-mode.md`'s `BLOCKED:` list; partial subagent work, intermediate refactor state, and perceived scope overrun are not on it – they are work to finish.
