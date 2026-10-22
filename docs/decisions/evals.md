# Decisions: Evals

Rationale, evidence, history, and reopen conditions for the **Evals** bullets in [DECISIONS.md](../DECISIONS.md) § Still Current. Each decision is stated there; a section here holds only what would not fit its one line.

## Eval cells run the plugin, not the operator

Excluded from `~/.claude`: the user `CLAUDE.md`, output style, and MCP servers. A run is staged outside the repo so the repo's `CLAUDE.md` does not load either. The operator's rules made a cell measure them instead of the plugin (2026-09-24 `plan` cells). The roles are committed as project agents and stay because subjects without a `reviewer` ran critics as general-purpose at high effort. Codex keeps only what DartClaw's pinned state dir forces.

## `claude plugin eval` is not the eval harness

Long journeys cannot run in it. Wanted instead: baseline cells inside the DartClaw harness measuring core journeys against no plugin.

Reopens if plugin eval gains code graders or a second host.
