# Automation Mode

Shared automation rules for AndThen skills.


## Headless-First

A skill that loads this reference runs to completion without pausing for routine clarification, even without `--auto`: record the most conservative assumption in the skill's primary artifact (FIS / PRD / plan / completion report), surface unresolved questions explicitly, and stop only on the **true contract failures** the `BLOCKED:` Triggers below name.

A skill whose own rules invert headless-first – a discovery skill that is interactive by contract – states that itself and takes precedence over this default.


## Strict Mode (`--auto`)

`AUTO_MODE=true` adds what an unattended run needs: never ask the user what to do next, not even a "Which approach?" pause, and close on a **deterministic completion summary** the orchestrator can parse – artifact paths, status, blockers. Never silently degrade.

### `BLOCKED:` Triggers (generic)

Each skill defines its own specific list; these baselines apply everywhere:

- Missing or unreadable required input.
- Incompatible upstream artifacts.
- Unsafe external actions (writes outside the project, irreversible operations without explicit consent in `INPUT`).
- Ambiguity or artifact conflict still unresolved after the Resolution Ladder – re-read, widen, delegate, work around – so no defensible output is producible. The ladder does not reach a skill whose deliverable *is* the unresolved set: enumerating an open decision is its output, not a block to climb past.
- Real external blockers: missing credentials/infra, merge conflicts requiring human policy, a decision the user owns, or repeated triage failure on one issue.

The `BLOCKED:` line lists the **minimum** missing inputs / decisions so the orchestrator can repair and resume. Name the ladder rungs already tried in the accompanying report, not on the sentinel line, which the parser reads one issue at a time.


## `--auto` Propagation

When `AUTO_MODE=true`, propagate `--auto` to **every nested AndThen skill invocation that accepts it**.


## Suppressed Output in Strict Mode

When `AUTO_MODE=true`, suppress conversational follow-up sections so output stays parseable:

- Skip "FOLLOW-UP ACTIONS" / "Next Steps" suggestions.
- Print only the artifact paths, the completion summary, and a hand-off line the skill's own contract requires (the `andthen:exec-plan` skill's `Next:` line) – the orchestrator acts on it, so it is output, not a suggestion.
