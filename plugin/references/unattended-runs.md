# Unattended Runs

## Recording an assumption

An assumption records a choice the run made because no answer was coming:

- an unattended run;
- a subagent with no user to ask;
- a question the run stopped on and nobody answered – one it continued past was not asked, however the question was sent;
- a reading its brief leaves to it.

Record the recommendation in the artifact, where it bites:

`ASSUMPTION: <what was assumed> – <what would change it>`

Both halves are required.

## Unattended runs

A run is unattended when `--auto` is in the skill's arguments, and only then, never because of how it was launched.

An unattended run:

- asks nothing;
- takes every recommendation and records it per **Recording an assumption**;
- skips an action that needs consent and is incidental to the call, and names it;
- offers no follow-ups beyond the hand-off line and template sections its skill requires;
- passes `--auto` to every nested `andthen:*` skill invocation that accepts it, so the mode survives delegation;
- closes on its artifact paths and status, or on `BLOCKED: <what is needed>` for an unusable call.

A call is unusable when required input is missing or invalid, when credentials or tooling are missing, when the working tree carries changes the run does not own and its skill gives no rule for, or when its own purpose is an action that needs consent its arguments do not give.
