# ADR-011: Size the per-story review to the change

**Status:** Superseded by [ADR-014](ADR-014-story-runs-where-invoked.md) on 2026-09-13.

**Recorded:** 2026-09-09

**Supersedes:** [ADR-009](ADR-009-routing-and-readiness.md). **Amends:** [ADR-002](ADR-002-execution-ownership.md), [ADR-005](ADR-005-optional-satellite.md).

## Context

Every story ended in a story gate: one fresh reviewer per lens reading `story-gate.md`, `lens-code.md`, and five calibration and lens files – 6,021 words in seven files – over a change set pinned by `snapshot --files`, returning findings the coordinator turned into a `Story-Gate: PASS|FAIL @ <snapshot>` line for `complete-story` to parse. Nothing sized that read-set to the diff: a four-line story drew four reviewer agents and most of an 18-minute run (`docs/LEARNINGS.md`, "Per-story review depth compounds"). The 2026-09-08 cut (`d617f9b`, `e5359ac`, `bc8c50a`) reduced the count to one reviewer and one repair round, not the weight.

The snapshot pin arrived in `d7834f1` (2026-08-31) as a review-finding remediation with no incident behind it. It witnessed that a reviewer's PASS named specific bytes; when `e5359ac` moved verdict authorship to the coordinator, the session that could skip a re-gate became the session writing the pin, and the pin's rationale was orphaned. ADR-009's readiness scan over Note findings parses severity, confidence, and scope out of prose for a case no record shows occurring.

Proof-bound completion has the opposite record. Its founding incident is observed: on 0.x a story reached done with 237 checked boxes and no probe executed. `complete-story` running every proof and the fast tier is what that incident justified.

## Decision

The per-story review inside the `andthen:exec-spec` skill's procedure is a code review sized to the change. The coordinator, which wrote no code (ADR-002), reads the diff against the FIS and runs the proofs itself. It dispatches one fresh reviewer – reading `lens-code.md`, given `CODE DIRECTORY:` and the FIS path – only when the change touches a security surface or a shared contract, spans many files, or leaves a doubt the diff pass cannot settle. Findings that need a fix go to the implementer as one round; whatever stays open is reported in the completion report, never gated. No gate report, no verdict grammar, no machine-parsed verdict.

The full review (`review --mode code,gap,security`) and `remediate-findings` are a separate step in a fresh session or DartClaw step – the `Next:` line the `andthen:exec-plan` skill already prints. `exec-plan` runs `exec-spec` in-session per story and adds no review of its own; its run gate stays the full tier on the final tree.

`complete-story` enforces task state complete and every proof and the fast tier executed green, and writes the receipt. It knows nothing about findings.

The `andthen:review` skill gains a quick path – the lens rubric over the diff, no coverage matrix – the same read-set as the dispatch above and the answer to 'sanity-check this'.

## Rationale

`quick-implement` 2.3 already applies this rule, and under ADR-002 the coordinator did not write the change, so the independence the retired `--inline` flag once demanded holds for its diff pass by construction. With no parsed verdict there is nothing to pin, so the snapshot question is closed rather than answered.

Rejected: keep the gate and drop only the pin (the prior session's recommendation, report 11) – it keeps 6,021 words and a verdict grammar for every story regardless of size. Rejected: let a commit carry the pin – a mechanism for a failure nobody has seen. Rejected: narrow the reviewer's read-set to `story-gate.md` plus `lens-code.md` (report 01, A15) – a fresh reviewer and a parsed verdict still run for a four-line change.

PRODUCT's Effective principle removes redundant checks through an explicit workflow change, never by skipping an active gate. This record is that change.

## Consequences

Retired with the gate: `story-gate.md` as a reviewer contract (its five proof falsifiers move into `lens-code.md`, where any code reviewer reads them), the `Files:` line, the `Story-Gate: PASS|FAIL @ <snapshot>` line and its parser, the `snapshot` verb, `complete-story --gate` and `--evidence`, `unresolved_note_defects`, the gate-report receipt fields, the `story-gate` artifact kind in `parse-artifact`, the `.agent_temp/story-gate-*` path and its `## Recovery` block, the rounds counter, `remediate-findings`' gate-report reading, the story-gate fixture in `scripts/fixtures/artifacts/`, and the three execution eval oracles' gate assertions.

Open findings are enforced in one place: the separate `review` → `remediate-findings` step. The "independent review on every story" promise narrows to independent review where the change warrants it; the coordinator's diff pass is the review otherwise. The execution eval oracles re-pin to the receipt and the completion report. The Ubiquitous Language rows Story Gate, Story-Gate verdict, and the Completion Receipt's gate line retired with `36a0a42`.

Reopens on a comparison at the same defect-detection bar showing the coordinator's diff pass misses what a fresh reviewer caught.

## Evidence

- History: `538094b` one coordinator; `d7834f1` the pin, no incident; `ae14dd2` the story-scoped pin after four false whole-tree refusals; `07b6815` ADR-009's enforcement; `d617f9b`, `e5359ac`, `bc8c50a` one reviewer, one round, coordinator-written verdict.
- Analysis: `docs/temp/research/1.0-audit/00-SYNTHESIS.md` (D3, D5, D9), `01-execution-path.md` (mechanism table; § Story gate versus main's quick-review), `11-prior-session-spec-proof-story-gates.md` – local, not committed.
- Implementation: `fc5c039` retires the gate from `ops` – `--gate`, `--evidence`, `snapshot`, the `story-gate` artifact kind, and the verdict parser; `36a0a42` rebuilds `exec-spec` as the story procedure with the review sized to the change and deletes the gate reference; `b98b04d` lands the review chain, its five reference deletions swept into `322b23d`.
