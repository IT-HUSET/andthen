# Execution Discipline

Red-gate rules for skills that execute work: what is iterated to green, and what to climb before stopping.


## Stop-the-Line

A red **objective gate** is work to finish, not a delivery caveat: `Done` is not written on a broken tree. Partial subagent work, intermediate refactor state, and perceived scope overrun are work to finish too – only an unusable call (`automation-mode.md`) stops a run.


## Gate Classes

| Class | Examples | Policy |
|---|---|---|
| **Objective red gate** | Build, tests, lint, type-check, stub/wiring check, task `Verify` | **Iterate until green**, invoking the `andthen:triage` skill when iteration stalls. One-pass limits do **not** apply. |
| **Subjective finding** | Code-review CRITICAL/HIGH, visual-validation findings | **One repair round**: the actor the skill assigns applies the Fix-routed fixes once; re-run what they invalidated and report what stays open – the next review is a separate request. |

Objective failures converge; subjective findings thrash.


## Resolution Ladder (Stop Last)

Treat artifact conflict or locally unresolved ambiguity as investigation. Climb in order, stop at the first answer, and name the rung:

1. **Re-read** – the intent anchor and its Required Context; this confirms a reading but adds no evidence.
2. **Widen** – inspect governing PRD/ADRs/decisions and code. Authority and trust decide first; specificity and recency break ties only among peers. Cross-authority conflict needs amendment or a user decision.
3. **Delegate** – reconnaissance, documentation lookup, the `andthen:architecture` skill, or an empirical `andthen:spike` skill. Skip a spike during parallel work on a shared checkout.
4. **Work around** – take any sanctioned amendment path; otherwise use the narrowest defensible reading – working around must never become the cheap way past a gate. Persist code/FIS divergence as a FIS Drift Note; record an outcome-neutral reading as an `ASSUMPTION:` line (`automation-mode.md` § Recording an assumption) or a Discovered Requirement.
5. **Stop** – no rung answered and no reading is defensible. Name the rungs tried.

Stopping on what an earlier rung answers is the dominant cause of premature aborts in unattended runs.
