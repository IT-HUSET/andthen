# Decisions

<!-- Maintenance:
     - The `andthen:architecture` skill in `--mode trade-off` auto-registers
       ADRs (appends to Current ADRs; moves prior rows to Superseded on
       supersession). Idempotent on ADR ID.
     - "Still Current" captures load-bearing choices that don't warrant a full
       ADR. Promote via `--mode trade-off` if the choice becomes contested.
     - Status enum (Current ADRs): Proposed | Accepted | Deprecated.
       Superseded decisions move to the dedicated table; Rejected decisions
       stay only in the ADR file itself (not indexed). -->

## Current ADRs

| ID | Title | Status | Scope |
|----|-------|--------|-------|

## Superseded

<!-- Move prior rows here when a new ADR supersedes them. Never delete –
     the lineage is load-bearing context for agents reading the codebase. -->

| Prior Decision | Superseded By | Notes |
|----------------|---------------|-------|

## Still Current

<!-- Load-bearing decisions that don't warrant a full ADR. One bullet each.
     Format: **<Topic>**: <decision + brief rationale>. -->

- **Sibling-story batching in plan spec authoring**: rejected – breaks 1 story ↔ 1 sub-agent ↔ 1 FIS, muddies OVERSIZE/PHANTOM_SCOPE attribution, and the preamble-amortization win shrank once per-FIS self-review was removed. Revisit hook resolved 2026-08-10: benchmark measured authoring (incl. preamble) at 14% of bundle cost vs remediation 41% – preamble does not dominate; rejection stands (`docs/temp/research/2026-08-10-spec-cost-remeasure.md`).
- **`disable-model-invocation` on skills**: rejected – it blocks Skill-tool invocation, breaking now-what routing and cross-skill chaining; the one open candidate is the deprecated `refactor` alias (smoke-test first). Reopens if a skill-invocable third tier ships.

## Pending

<!-- Decisions under discussion, awaiting acceptance. Typically populated by
     the `andthen:architecture` skill in `--mode trade-off` when a
     recommendation hasn't yet been accepted as an ADR. -->
