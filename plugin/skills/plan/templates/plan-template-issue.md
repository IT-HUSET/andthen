# Implementation Plan Template — GitHub Issue Body

> Markdown rendering shape used **only** for `andthen:plan --to-issue` (the single-issue body that humans review on GitHub). Local plans are JSON: see [`plan-schema.md`](../../../references/plan-schema.md). This template is never written to disk.
>
> The shape is an operational contract — `andthen:exec-plan --from-issue` parses the rendered issue body into a local `plan.json` ledger. Heading names, Story Catalog columns, and the `### Story S0N: <name>` story-section anchors are pinned because the parser depends on them. The canonical body shape is [`plan-issue-shape.md`](../../../references/plan-issue-shape.md); this template is the single-issue rendering of that contract — for granular `--create-story-issues` mode, render directly from `plan-issue-shape.md` instead.


# Implementation Plan: [Project Name]

> **PRD**: [`prd.md`](./prd.md) — or `github://issue/<prd-N>` for issue-input PRDs

[Plan summary — 1–3 short paragraphs of context describing scope and sequencing strategy.]


## Shared Decisions

> _Optional — include only when stories have inter-dependencies that imply a shared interface, naming convention, or abstraction. Omit the section when none apply._
>
> 3-6 bullets naming inter-story interface contracts, naming conventions, or shared abstractions multiple stories will create or consume. FIS sub-agents inherit these as-is so independently-generated specs don't drift on shared concerns.

- **[Decision name]**: [one-line description; name the producing and consuming stories]
- **[Decision name]**: [description]


## Binding Constraints

> _Optional — include only when the PRD contains "must support X"-style language at risk of being silently dropped during plan decomposition. Omit when none apply._
>
> Each entry: verbatim PRD span + heading anchor + source feature ID. These flow unchanged into FIS Required Context blocks — they are not subject to architectural trade-offs or scope narrowing by individual stories.

- **[FR-N — short label]**: "[verbatim PRD text span]" — source: [`prd.md#<heading-slug>`](./prd.md#heading-slug)
- **[FR-N — short label]**: "[verbatim text]" — source: [`prd.md#<heading-slug>`](./prd.md#heading-slug)


## Story Catalog

| ID | Name | Phase | Wave | Dependencies | Parallel | Risk | Status | FIS |
|----|------|-------|------|--------------|----------|------|--------|-----|
| S01 | [Name] | Foundation | W1 | - | No | Low | Pending | - |
| S02 | [Name] | Core | W2 | S01 | Yes | Medium | Pending | - |
| S03 | [Name] | Core | W2 | S01 | Yes | Medium | Pending | - |

> **Dependency cell contract**: `Dependencies` is scheduler input. Use `-` or comma-separated story IDs from this table only, e.g. `S01, S04`. Prose dependencies are invalid.
>
> **FIS cells stay unset (`-`)**: FIS files are generated just-in-time by `andthen:exec-plan --from-issue`. Do not pre-populate FIS paths in the issue body.


### Story S01: [Story Name]

**Scope**: [1-2 sentences covering the intended outcome, what is included, and what is excluded. Detailed success criteria and scenarios belong in the JIT-generated story FIS.]
**Source refs**: [PRD feature IDs and anchors, e.g. FR-2, FR-5 — `prd.md#export-rules`]
**Asset refs**: [Wireframe refs, ADR refs, design-system refs if any — omit when none]


### Story S02: [Parallel Story Name]

**Scope**: [1-2 sentence story brief]
**Source refs**: [PRD feature IDs and anchors]
**Asset refs**: [Relevant asset refs]


### Story S03: [Carried-Forward Story Example]

**Provenance**: Carried from previous plan: S13
**Scope**: [Describe the carried-forward scope clearly; only include `**Provenance**` when no PRD feature directly covers this story]
**Asset refs**: [Relevant asset refs]


Refs #<prd-issue-N>

> **Footer**: omit the `Refs #<prd-issue-N>` line when no PRD issue was the input (i.e. the PRD was a local `prd.md`).


## Execution

This plan is published as a GitHub issue. Stories' FIS files are generated just-in-time when an executor consumes the issue:

1. `andthen:exec-plan --from-issue <plan-issue-N>` — materializes a local `plan.json` ledger, generates each story's FIS just-in-time, runs the per-story `exec-spec → quick-review` pipeline by phase and wave, then a final gap review. Phase ordering and parallel markers are honored; dependencies block waves automatically.
2. **Status tracking**: The Story Catalog above is the issue's snapshot at publish time; it is not rewritten as execution progresses. `andthen:exec-plan --from-issue` tracks `status` / `fis` in the local ledger and posts per-story closure comments back to this issue.
