# Automation Mode


## Headless-First

A skill that names this file as its automation rules follows headless-first: it answers routine questions itself instead of stopping to ask, even without `--auto`. Where its contract says it asks, it asks.

A run still stops on an unusable call – one it cannot continue because required input is missing or invalid, credentials or tooling are missing, the working tree has changes the run does not own, or an external or irreversible action has no consent in `INPUT`. If the user can fix it in the conversation, ask and continue; otherwise say what is needed and stop.


## Recording an assumption

When a run takes a recommendation instead of an answer – under headless-first or `--auto`, in a subagent that cannot ask, or for a question nobody answered – it records the recommendation in the artifact where the decision applies, such as the FIS, PRD, plan, or completion report:

`ASSUMPTION: <what was assumed> – <what would change it>`

Both halves are required: the second names the fact that would make the assumption wrong, so whoever meets it – executor, reviewer, user – knows to revisit it.


## Strict Mode (`--auto`)

`AUTO_MODE=true` is an unattended run:

- Never ask, and never silently degrade.
- **`--auto` propagation** – pass `--auto` to every nested AndThen skill invocation that accepts it.
- Take every open decision on its recommendation, recorded per **Recording an assumption**.
- Close on a deterministic completion summary (artifact paths, status) plus any hand-off line the skill's contract requires – the `andthen:exec-plan` skill's `Next (fresh session):` line is output the orchestrator acts on. The summary carries no "FOLLOW-UP ACTIONS" or "Next Steps" section; a section a written artifact's template requires stays.
- A run that stops ends on a failure with its evidence, or on `BLOCKED: <what is needed>` for an unusable call – a human must supply something and a plain retry will not help – never both. An action lacking consent stops alone; the rest of the run proceeds where it is independent.
