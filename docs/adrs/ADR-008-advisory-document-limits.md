# ADR-008: Make document size limits advisory by default

**Status:** Superseded by [ADR-012](ADR-012-size-notice-only.md) on 2026-09-09 – the advisory notice stays; `hard`, `prune`, and the admission checks beside it retire.

**Recorded:** 2026-09-07 (retrospective)

## Context

Document ceilings encourage pruning, but a count cannot distinguish necessary explanation from dispensable text. Refusing every over-limit write made the size threshold decide whether information deserved to survive.

## Decision

Document ceilings and the 200-character entry/cell cap are advisory. Writes at or beyond an advisory threshold emit a notice and proceed. A ceiling marked `hard` in the Project Document Index or in an explicit override refuses only a result above the limit; equality is allowed. Measurement uses the proposed result.

Whether an entry outlives its initiative remains the caller's admission judgment. Naming `plan.json` or a story is not itself grounds for refusing it. Duplicate and other admission checks remain.

Skill context-budget regression ceilings and FIS `OVERSIZE` decomposition are separate contracts and remain hard.

## Rationale

The alternatives were raising every ceiling or granting per-write exemptions. Both retain default refusal and turn necessary explanation into exception handling. Advisory limits instead expose the maintenance cost while leaving the content decision with the caller; projects can still opt into refusal.

## Consequences

A successful write can exceed an advisory size target, so its notice matters. `hard` supplies a mechanical bound, not a judgment of content quality. This changes durable-document admission without weakening execution or skill-budget gates.

## Evidence

- History: `b40cb29` introduces ceilings; `3ae01f1` changes their default and records the alternatives.
- Current behavior: [ops reference](../../plugin/README.md#ops), [size gates](../../plugin/skills/ops/scripts/ops.py), and [boundary tests](../../tests/test_ops.py).
