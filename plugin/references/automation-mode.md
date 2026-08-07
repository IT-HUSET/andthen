# Automation Mode

Shared automation rules for AndThen skills. Referenced from each skill's `INSTRUCTIONS` section.


## Headless-First (Execution Skills)

This skill runs to completion without pausing for routine clarification, even without `--auto`. Make conservative assumptions, document them in the skill's primary output, and surface unresolved questions explicitly. Stop only on **true contract failures** (see the `BLOCKED:` Triggers below).

Scope: this reference applies to execution-oriented skills only (`prd`, `plan`, `spec`, `exec-*`, `quick-implement`, `triage`, `simplify-code` and its deprecated alias `refactor`, `remediate-findings`). `preflight` and `issue-triage` consume it too, but their own local rules invert strict mode to interactive-by-contract and take precedence. Discovery and design skills (`clarify`, `architecture` trade-off / advise / event-storming / strategic-design modes) declare their own user-input contracts and do not consume this reference.

`--auto` is the official strict form of this rule (below). During transition, implementations may tolerate `--headless` as an undocumented alias that sets `AUTO_MODE=true`, but public surfaces and nested propagation use `--auto` only.


## Strict Mode (`--auto`)

When `AUTO_MODE=true`, never ask the user what to do next (no arrow prompts, no "Which approach?" pauses); make the most conservative assumption that preserves coherent output and record it in the artifact (FIS / PRD / plan / completion report); return a **deterministic completion summary** the orchestrator can parse – artifact paths, status, blockers – and stop only with `BLOCKED:` for the failure conditions below; never silently degrade.

### `BLOCKED:` Triggers (generic)

Each skill defines its own specific list; these baselines apply everywhere:

- Missing or unreadable required input.
- Incompatible upstream artifacts.
- Unsafe external actions (writes outside the project, irreversible operations without explicit consent in `INPUT`).
- Ambiguity or artifact conflict still unresolved after the **Resolution Ladder** in [`execution-discipline.md`](${CLAUDE_PLUGIN_ROOT}/references/execution-discipline.md) – no defensible output is producible. The ladder does not reach a skill whose deliverable *is* the unresolved set (`preflight`, `issue-triage`): enumerating an open decision is their output, not a block to climb past.
- Real external blockers per the same reference (credentials/infra, merge conflicts, a decision the user owns, repeated triage iteration on one issue).

The `BLOCKED:` line lists the **minimum** missing inputs / decisions so the orchestrator can repair and resume. Name the ladder rungs already tried in the accompanying report, not on the sentinel line, which the parser reads one issue at a time.


## `--auto` Propagation

When `AUTO_MODE=true`, propagate `--auto` to **every nested AndThen skill invocation that accepts it**. This is universal – do not restate at each call site.

**Exemption**: the `andthen:ops` skill is deterministic; it does not accept `--auto` and does not need it.


## Suppressed Output in Strict Mode

When `AUTO_MODE=true`, suppress conversational follow-up sections so output stays parseable:

- Skip "FOLLOW-UP ACTIONS" / "Next Steps" suggestions.
- Print only the artifact paths and the completion summary.
- Keep `BLOCKED:` lines structured (one issue per line, leading sentinel).
