# ADR-007: Compose artifact views from worked examples

**Status:** Superseded by [ADR-017](ADR-017-visualization-belongs-to-the-companion-app.md) on 2026-09-18 – rendering leaves AndThen entirely; the worked examples, the per-type contracts, and the atlas renderer retire with the skills that ran them.

**Recorded:** 2026-09-07 (retrospective)

## Context

The visualizer maintained per-type templates and a deterministic changeset renderer. The design question was which presentation decisions needed fixed machinery and which could be made while rendering an artifact.

## Decision

Non-model artifacts render by adapting one of two worked HTML examples: document review or exploration. A bounded structural checker and browser inspection verify the result. Section identity, notes payload, plan virtual sections, FIS state, and safe output remain contracts.

Architecture and domain models retain the deterministic atlas renderer, which adds no prompt-loading cost. Shared notes behavior in both examples must remain aligned.

## Rationale

The decision note reports a three-input comparison in which the candidate won all three: the previous path overflowed at 390 px, omitted a walkthrough focus point, and lost notes on reload. This supported replacing the template family and changeset renderer while retaining their behavioral contracts.

## Consequences

Presentation quality depends on adapting and visually checking each result. Structural checks cannot establish source fidelity or interaction quality alone. Reconsider fixed per-type renderers if adaptations lose those properties in ways the checker cannot catch.

## Evidence

- History: `8c037be` implements the change; `c197d65` records the comparison conclusion; `c13ae9f` repairs shared notes behavior.
- The comparison conclusion is recorded; its raw artifacts are not preserved in committed history.
- Current contract: `plugin-some/skills/visualize/SKILL.md` and `plugin-some/README.md` § `visualize`.
