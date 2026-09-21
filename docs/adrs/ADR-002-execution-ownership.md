# ADR-002: Keep execution coordination in the invoking session

**Status:** Superseded by [ADR-014](ADR-014-story-runs-where-invoked.md) on 2026-09-13.

**Recorded:** 2026-09-07 (retrospective)

## Context

Plan execution previously delegated each story to a complete `exec-spec` coordinator, which then delegated review. A child returning before its reviewers leaves no reliable collector for the gate. Implementation also needs fresh context and independent review.

## Decision

The session invoking the `andthen:exec-spec` or `andthen:exec-plan` skill coordinates the `andthen:exec-spec` skill's story procedure, which the `andthen:exec-plan` skill runs in this session per story. It owns decisions, child dispatch and result collection, the per-story review, FIS amendments, story completion, and commits.

One implementer child owns the story's code, tests, task verification, and task progress. A reviewer, when the change warrants one (ADR-011), and lookup agents are its siblings. The coordinator collects their completed results. Plan execution repeats this procedure without nesting the whole `exec-spec` coordinator.

## Rationale

This replaces nested executor coordination while retaining fresh implementation context and reviewer independence. One session can reconcile implementation evidence, review findings, and completion checks.

## Consequences

The coordinator carries more orchestration context and must remain active through collection. It cannot substitute an implementer's self-report for completion. Repair stays with the same implementer while addressable; otherwise a replacement receives the failure evidence and durable progress.

## Evidence

- History: `538094b` replaces nested execution; `92017cd` retires the separate host-specific waiting workaround.
- Current contract: [the story procedure](../../plugin/skills/exec-spec/SKILL.md).

## Amendments

- 2026-09-09 – [ADR-011](ADR-011-per-story-code-review.md) and audit decision D1. The shared story procedure is the `andthen:exec-spec` skill's own body, which `andthen:exec-plan` runs in-session per story; "review assembly, evidence persistence" became "the per-story review"; reviewers are siblings only when dispatched, sized to the change; "the gate" in Consequences became completion. The evidence link now points at `plugin/skills/exec-spec/SKILL.md`, which carries the procedure.
