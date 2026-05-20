# Automation Mode

Shared automation rules for AndThen skills. Referenced from each skill's `INSTRUCTIONS` section.


## Headless-First (Execution Skills)

This skill runs to completion without pausing for routine clarification, even without `--auto`. Make conservative assumptions, document them in the skill's primary output, and surface unresolved questions explicitly. Stop only on **true contract failures** – missing required input, incompatible artifacts, unsafe external actions, or ambiguity so severe no defensible output is producible.

Scope: this reference applies to execution-oriented skills only (`prd`, `plan`, `spec`, `exec-*`, `simplify-code`, `refactor`, `remediate-findings`). Discovery and design skills (`clarify`, `architecture` trade-off / advise / event-storming / strategic-design modes) declare their own user-input contracts and do not consume this reference.

`--auto` / `--headless` is the *strict* form of this rule (below).


## Strict Mode (`--auto` / `--headless`)

When `AUTO_MODE=true`:

- **Never ask the user what to do next**, not even once. No arrow prompts, no "Which approach?" pauses.
- **Make the most conservative assumption** that preserves a coherent output. Record it in the artifact (FIS / PRD / plan / completion report) so the chain remains auditable.
- **Return a deterministic completion summary** the orchestrator can parse – artifact paths, status, blockers.
- **Stop only with `BLOCKED:`** for the failure conditions below; never silently degrade.

### `BLOCKED:` Triggers (generic)

Each skill defines its own specific list; these baselines apply everywhere:

- Missing or unreadable required input.
- Incompatible upstream artifacts.
- Unsafe external actions (writes outside the project, irreversible operations without explicit consent in `INPUT`).
- Ambiguity so severe no defensible output is producible.
- Real external blockers per [`execution-discipline.md`](execution-discipline.md) (missing credentials/infra, merge conflicts requiring human policy, repeated triage iteration on the same issue).

The `BLOCKED:` line lists the **minimum** missing inputs / decisions so the orchestrator can repair and resume.


## `--auto` Propagation

When `AUTO_MODE=true`, propagate `--auto` to **every nested AndThen skill invocation that accepts it**. This is universal – do not restate at each call site.

**Exemption**: the `andthen:ops` skill is deterministic; it does not accept `--auto` and does not need it.


## Suppressed Output in Strict Mode

When `AUTO_MODE=true`, suppress conversational follow-up sections so output stays parseable:

- Skip "FOLLOW-UP ACTIONS" / "Next Steps" suggestions.
- Print only the artifact paths and the completion summary.
- Keep `BLOCKED:` lines structured (one issue per line, leading sentinel).
