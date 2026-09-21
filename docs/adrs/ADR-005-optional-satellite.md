# ADR-005: Keep the core workflow independent of the satellite

**Status:** Superseded by [ADR-018](ADR-018-one-plugin.md) on 2026-09-20 – the satellite merges into core before 1.0 ships; five skills move, `council` and `e2e-test` retire, `security-review` folds into the `security` lens.

**Recorded:** 2026-09-07 (retrospective)

## Context

A lightweight workflow install should not require every analysis, visualization, or integration tool. Splitting those tools into another plugin is useful only if core workflows remain complete when it is absent.

## Decision

The `andthen` plugin owns the complete core workflow. The `andthen-some` plugin supplies optional tools and deeper capabilities. Core offers a satellite skill only when installed and states the available core behavior otherwise.

Deep architecture analysis is the `andthen:architecture` skill's modes and codebase and domain description is the core `andthen:describe` skill, so no offer-when-installed prose sits on either path. `council`, `security-review`, `tracker`, `visualize`, `explain-changes`, and the solo tools stay in the satellite: scripts, checklists, and tools core never requires.

Required decision settlement remains in core: the `andthen:architecture` skill's trade-off mode. The `andthen:quick-implement` skill also belongs in core, preserving a verified path for small changes without a specification.

## Rationale

Making an optional capability a hard dependency breaks core-only installs. Keeping a slim core capability where necessary preserves completion without requiring the deeper tool. The later move of `quick-implement` into core applies the same rule: proportionality requires a small-change path in the base install.

`spike` remains optional because it produces evidence rather than shipped changes. Individual skill placements lack separate recorded trade-off analyses.

## Consequences

Core must describe fallbacks wherever it offers satellite capabilities. Optional depth can be unavailable without blocking the base workflow. Future placement decisions must follow dependency needs rather than freeze today's skill inventory.

## Evidence

- History: `31c4211` establishes the satellite; `c2924b4` moves optional skills and adds fallbacks; `07b6815` returns `quick-implement` to core.
- Boundary as it stood: `docs/ARCHITECTURE.md` § Two Plugins, One Marketplace and `plugin-some/README.md`, both at `6090fc6^` – `6090fc6` merges the satellite into `andthen` under ADR-018.

## Amendments

- 2026-09-09 – audit decision D7, with [ADR-011](ADR-011-per-story-code-review.md). `architecture-analysis` returns to `architecture` as modes and `describe` returns to core: the split's recurring cost was four offer-when-installed passages, an inert 88-line calibration copy, and a stale `openai.yaml` in core, while mode files load on demand and cost core nothing until invoked; the size win (2,611 → 1,655 lines) came from compressing the textbook references, not from the split. The story-gate clause was stale since `e5359ac` (2026-09-08) and is gone under ADR-011. `19a4326` lands the move.
