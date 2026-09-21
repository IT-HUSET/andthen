# ADR-012: Reduce durable-document checks to a size notice

**Status:** Superseded by [ADR-013](ADR-013-scripts-read-json-agents-read-markdown.md) on 2026-09-11 – the durable-document verbs and the size notice retire; agents append to Learnings and Tech Debt directly, and the Index size is theirs to read.

**Recorded:** 2026-09-09

**Supersedes:** [ADR-008](ADR-008-advisory-document-limits.md).

## Context

For a Learnings file whose Index row states 150 lines, `ops.py` carries 318 lines of durable-document machinery: ceiling resolution and `prune` 227, the mechanical admission checks 91, pinned by 22 tests. Of those, 180 demote a judgment the `ops` prompt already states – the admission test at `SKILL.md:62`: does a frontier model already know this, does code or git history carry it, does it outlive the initiative – to a count: the three-word bare-command test, the initiative-name regex, the 129-line `prune` candidate list, and `close-plan`'s auto-written Learnings bullet. `prune` has no automated caller, and its output is a list a search produces.

ADR-008 made ceilings advisory on the argument that a count cannot distinguish necessary explanation from dispensable text, and stopped at ceilings. CHANGELOG rc.1 then states the contract both ways: line 28 says an append at the ceiling is refused, line 72 says ceilings are advisory unless a row says `hard`. The machinery solves this repository's document-growth problem, generalised into core, where scale and artifact volume are unknown (PRODUCT, Proportionality).

## Decision

A durable write that reaches or crosses the size in its Project Document Index row lands and reports it in one line. Nothing refuses on size: the `hard` cell, `--ceiling`, and `prune` retire.

`update-learnings add` and `update-tech-debt` are plain append verbs: they detect a duplicate or near-duplicate entry and print the notice. The entry-length cap, the bare-command test, the story-id and bundle-path bans, and the initiative-name regex retire from them and from `close-plan`'s Decisions append. Whether an entry is novel, absent from code and history, and durable stays the caller's admission test, stated once in the `ops` prompt.

## Rationale

ADR-008's argument holds for every check beside the ceiling: a three-word test or a name regex cannot tell a trap from a bare command any better than a line count tells necessary from dispensable. Duplicate detection stays because a near-duplicate title is the one mechanical check an agent reliably misses. The notice stays because a document past the size it is worth on a read should say so on the write that got it there.

Rejected: move the family to the satellite – the satellite holds tools core never requires, not machinery core no longer wants. Rejected: keep `prune` as a user verb – the candidate list it prints is what the agent reading the notice would find with a search.

## Consequences

About 220 script lines and most of the 22 tests that pin them go; the Index's Ceiling column stays as the notice's source, and its `hard` form no longer means anything. The Index preamble, the `init` template's Index text, the `ops` trigger phrases, the README ops section, the cookbook, and the glossary rows Ceiling, Prune pass, and Admission test changed with `322b23d`; CHANGELOG rc.1 states the contract once.

A document can now grow past its row's size with nothing but the notice between it and the next write. Reopens on a document-growth failure a notice did not prevent.

## Evidence

- History: `b40cb29` (2026-08-29) hard ceilings and prune-before-append; `3ae01f1` (2026-09-07) advisory ceilings, recorded as ADR-008.
- Analysis: `docs/temp/research/1.0-audit/04-ops.md` (§ Durable-document machinery; cross-cutting observations) and `00-SYNTHESIS.md` (D8) – local, not committed.
- Implementation: `322b23d` – `prune`, `--ceiling`, hard ceilings, the entry cap, and the bare-command test out of `ops.py`; the notice and duplicate detection stay.
