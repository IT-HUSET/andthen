# ADR-010: Give each story its own FIS authoring context

**Status:** Accepted

**Recorded:** 2026-09-07 (retrospective)

## Context

Plan authoring needs attributable story boundaries and failure signals. Having one subagent author several sibling FIS files could amortize its shared prompt context, but would combine work that must be assessed and retried separately.

## Decision

Keep one story, one authoring subagent, and one FIS per authoring assignment. The plan coordinator delegates FIS prose and owns collection, plan mutations, and cross-story reconciliation.

Dependency-ready stories can be dispatched together, but each has a separate author. Reauthoring remains scoped to the owning story; it does not turn sibling stories into one authoring assignment.

## Rationale

The recorded rejection of sibling-story batching rests on losing the one-to-one mapping and obscuring which story caused `OVERSIZE` or `PHANTOM_SCOPE` findings. The claimed prompt-amortization benefit is unproven: the original benchmark was never committed, and its skill-invocation accounting is not comparable to the replacement's transcript-segment accounting.

## Consequences

Separate authors repeat some context and need coordination across story boundaries. Their outputs and failures remain attributable to individual stories. Reconsider shared authoring only if a comparable benchmark demonstrates that preamble cost dominates; the old measurements cannot establish that case.

## Evidence

- History: `6cd0230` records the rejection; `e4d39a5` explicitly qualifies the missing benchmark evidence.
- Current contract: [plan authoring](../../plugin/skills/plan/SKILL.md).
- Measurement limits: the benchmark that produced the old measurements was retired 2026-09-12 (its one deterministic check counted a completion receipt field ADR-013 removed).
