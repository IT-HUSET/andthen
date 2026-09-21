# ADR-009: Separate remedy routing from story readiness

**Status:** Superseded by [ADR-011](ADR-011-per-story-code-review.md) on 2026-09-09 – the story gate and its parsed verdict retire; readiness is proof-bound completion alone.

**Recorded:** 2026-09-07 (retrospective)

## Context

A serious defect can require a design decision before it can be fixed. Treating every Note-routed finding as non-blocking would let such a defect pass the story gate merely because its remedy cannot be applied automatically.

## Decision

`Fix` and `Note` classify whether a remedy may be applied without a decision; they do not by themselves determine completion.

A story gate passes only when no accepted finding is routed `Fix` and no `primary` `code-defect` at HIGH or CRITICAL, with confidence at least 75, remains routed `Note`. The `andthen:ops` skill enforces both conditions when parsing gate reports and completing stories.

For a blocking Note, the executor resolves the decision and re-gates. It neither guesses the remedy nor completes over the defect.

## Rationale

The rejected alternative was widening `Fix` to include severe findings regardless of remedy certainty. That would authorize automatic changes whose direction still needs judgment. Keeping routing and readiness separate preserves both decision ownership and the completion bar.

## Consequences

A Note can block completion without authorizing remediation. Consumers must inspect severity, confidence, scope, and class alongside routing; counting Fix findings alone is insufficient. Other Notes remain subject to the existing routing and scope rules.

## Evidence

- History: `07b6815` records the decision and adds enforcement.
- Current contracts: [story gate verdict](../../plugin/references/story-execution.md), [reviewer rules](../../plugin/references/story-gate.md), [finding routing](../../plugin/references/review-calibration.md), and [gate parser](../../plugin/skills/ops/scripts/ops.py).
