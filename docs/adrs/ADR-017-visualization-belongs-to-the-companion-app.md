# ADR-017: Visualization belongs to the companion app

**Status:** Accepted

**Recorded:** 2026-09-18

**Supersedes:** [ADR-007](ADR-007-example-led-rendering.md).

## Context

AndThen shipped two satellite skills that produced rendered HTML: `visualize` composed a review page per artifact from one of two worked examples and dispatched the two atlas model kinds to a bundled Node renderer, and `explain-changes` wrote a Changeset Walkthrough that `visualize` then rendered as a tour.

The companion app that reads AndThen artifacts now renders plan boards, FIS, PRD, reports, diffs, the atlas, and tours from the same artifacts, and it is installed wherever those artifacts are read. Two producers of the same views is one too many, and the model-composed half never had a gate: its remaining differentiator was judgment-composed figures, which needs a browser look no CI runs, and it produced four reworks.

## Decision

**Retire `visualize` and `explain-changes`. AndThen keeps the contracts; the companion app owns every rendered view.**

AndThen owns what more than one consumer reads: the artifact schemas, the fixture corpus under `scripts/fixtures/renders/` with its owner routing table, and the visual-review-notes payload shape. The changeset walkthrough moves whole – its producer prompt and its only consumer are both downstream – so its template and fixture leave with the skills.

**Skills never mention the companion app.** Where a skill offered `visualize`, the offer is deleted and nothing replaces it; shipped references say "downstream tooling" at most. The app is private, and a shipped prompt that names it breaks for everyone who does not have it.

## Rationale

The notes loop closes better outside AndThen: the app invokes the owning skill directly instead of routing a payload through the clipboard, so the round-trip no longer depends on the user pasting it back.

Rejected: **keeping `visualize` for the atlas only** – the renderer was its one deterministic part, and the app vendors an owned copy, so the skill would ship a bundle for a view its only reader already draws. **Keeping `explain-changes` for its markdown output** – comprehension without the tour is what `andthen:review` already reads a changeset for.

## Consequences

ADR-007 is superseded: the worked examples, the per-type contracts, `check_render.py`, and `render-atlas.mjs` retire with the skills that ran them. The satellite drops to 8 skills.

A core-only install loses nothing it had: every offer site degraded to one line already, and those lines are what remains. Users without the companion app read the Markdown, which is what the fallbacks always said.

The tour gap between this change and the app's walkthrough view is accepted.

Reopens if artifact rendering has to serve readers outside the companion app – a public consumer, or a host with no app – in which case the contracts to rebuild from are the corpus and the notes payload, not the retired prompts.

## Evidence

- Retired paths: `plugin-some/skills/visualize/`, `plugin-some/skills/explain-changes/`.
- Current contracts: [`scripts/fixtures/renders/README.md`](../../scripts/fixtures/renders/README.md) (type table and owner routing), [`plugin/references/architecture-model.md`](../../plugin/references/architecture-model.md), [`plugin/references/board-models.md`](../../plugin/references/board-models.md).
