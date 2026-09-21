# ADR-004: Distribute shared plugin sources through host manifests

**Status:** Accepted

**Recorded:** 2026-09-07 (retrospective)

## Context

AndThen supports Claude Code, Codex, and loose-skill consumers. Separate host-specific distribution trees would duplicate content and introduce another synchronization boundary. The shared-source choice predates 1.0; the satellite extends it.

## Decision

Each plugin has one source directory and both host manifests. Claude Code and Codex plugin channels ship `plugin/` and `plugin-some/` directly, without a generated distribution tree or build step.

Only the loose-skill installer inlines shared references and rewrites paths and namespaces, because those bundles leave the plugin structure.

Shared canonicals originate in `plugin/references/`. A satellite consumer receives a committed, byte-identical copy under `plugin-some/references/`, checked by validation and refreshed through `--sync-satellite-assets`.

2026-09-16: a consumer names a canonical by skill-root-relative path (`../../references/<asset>.md`), retiring `${CLAUDE_PLUGIN_ROOT}` – Codex never substituted the token, while both hosts announce the skill root. The path climbs into the consuming skill's *own* plugin dir, so the satellite copy stays load-bearing rather than a convenience.

## Rationale

The recorded rejected alternative was a generated distribution pipeline. Thin manifests let both hosts consume the same maintained content. Satellite copies are a deliberate exception: plugin roots resolve within their own plugin, so cross-plugin reference paths cannot supply shared files. Symlinks were excluded for Windows checkout compatibility.

## Consequences

Plugin releases avoid build-output drift, but shared-asset changes must synchronize satellite copies and pass install validation. Loose-skill packaging remains a separate transformation surface to verify. Skill-local references are outside canonical synchronization and may deliberately diverge.

## Evidence

- History: `8bb630c` adds dual manifests; `31c4211` extends distribution and canonical synchronization to the satellite.
- Recorded alternative: [packaging learnings](../LEARNINGS.md#cross-agent-packaging).
- Current mechanism: [distribution architecture](../ARCHITECTURE.md#distribution-channels) and [installer](../../scripts/install-skills.sh).

## Amendments

- 2026-09-20 – [ADR-018](ADR-018-one-plugin.md). The satellite copies retire with the satellite: one `plugin/references/`, no `_satellite_assets`, no `--sync-satellite-assets`, no byte-diff check. One source directory under both host manifests, no build step, and loose-skill inlining are unchanged.
