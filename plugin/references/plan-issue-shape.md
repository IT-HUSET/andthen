# Plan Issue Body Shape

This document is the **single canonical source** for the body shape of a plan issue produced by the `andthen:plan` skill in `--to-issue` mode and consumed by the `andthen:exec-plan` skill in `--from-issue` mode.

> Skills that reference this document: `plan`, `exec-plan`.

The contract has two shapes — **single-issue** (default `--to-issue`) and **granular** (`--to-issue --create-story-issues`). Both use the same parser-friendly H2 anchors so a downstream consumer can detect shape and extract sections without bespoke regex. The Story Catalog table column order is identical to the local `plan.md` template ([`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md) — Story Catalog Columns).


## Link Conventions

Plan and story issues use these exact link forms — they are contracts, not suggestions. `andthen:exec-plan --from-issue` extracts provenance from them.

| Token | Meaning | Where it appears |
|---|---|---|
| `Refs #N` | Provenance: this artifact derives from issue `#N` | Footer of any plan, PRD, story, clarify, or triage issue when an input issue was supplied |
| `Part of #N` | Containment: this story issue belongs to plan issue `#N` | Footer of every story issue created by `--create-story-issues` |
| `Depends on #N` | Inter-story ordering: this story depends on story issue `#N` | Inline in a story issue's `Dependencies` field; the consumer maps `#N` back to a Story ID via the parent plan's Story Catalog |

`Refs #N` and `Part of #N` are independent: a story issue carries both — `Refs` to the originating PRD issue, `Part of` to the parent plan issue.


## Parser-Friendly Section Markers

Both shapes use these H2 anchors. The consumer matches them by `^## <name>$` against a markdown body — do not introduce identical H2s elsewhere in the body.

- **`## Technical Research`** — full tech-research content (materialized to `<run-tempdir>/.technical-research.md` by `exec-plan --from-issue`).
- **`## Story Catalog`** — standard markdown table; columns per [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md).
- **`## Story Issues`** — granular-shape only; presence of this section with at least one `#<digit>` reference under it is the **shape-detection signal** for `exec-plan --from-issue`.

Story sections in the single-issue shape use H3: `### Story S0N: <name>`. Granular-shape story issues do not nest a duplicate `### Story` heading — the issue title carries the story name.


## Single-Issue Shape

Used by `andthen:plan --to-issue` (default). Everything lives in one issue; no story issues are created.

Body skeleton:

```
<plan summary — 1–3 paragraphs of context>

## Technical Research

<full tech-research content; no separate file>

## Story Catalog

| ID | Name | Phase | Wave | Dependencies | Parallel | Risk | Status | FIS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S01 | <name> | <phase> | W1 | - | Yes | Low | Pending | - |
| S02 | <name> | <phase> | W1 | - | Yes | Medium | Pending | - |

### Story S01: <name>

**Status**: Pending
**FIS**: -
**Phase**: <phase>
**Wave**: W1
**Dependencies**: -
**Parallel**: Yes
**Risk**: Low
**Scope**: <one-paragraph scope>
**Acceptance Criteria**:
- [ ] <criterion>

### Story S02: <name>

<same fields as S01>

Refs #<prd-N>
```

Story metadata fields mirror those of a local plan story. Omit the `Refs #<prd-N>` footer when no PRD issue was the input.


## Granular Shape

Used by `andthen:plan --to-issue --create-story-issues`. Produces one parent plan issue plus N child story issues.

### Parent Plan Issue Body Skeleton

```
<plan summary — 1–3 paragraphs>

## Technical Research

<full content; not duplicated into story issues>

## Story Catalog

| ID | Name | Phase | Wave | Dependencies | Parallel | Risk | Status | FIS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S01 | <name> | <phase> | W1 | - | Yes | Low | Pending | - |

## Story Issues

- #<S1-issue-N> — <story name> — <one-line scope>
- #<S2-issue-N> — <story name> — <one-line scope>

Refs #<prd-N>
```

The plan body is created first with placeholders under `## Story Issues`, then `gh issue edit <plan-N> --body-file` rewrites this section after every story issue exists, so the rendered numbers are real.

### Story Issue Body Skeleton

The issue title is `S0N: <name>`; the body has no nested `### Story` heading. The metadata fields below are the canonical 9 from `data-contract.md` `## Required Story Metadata Labels` — single-issue and granular shapes carry the same set so the consumer parses them uniformly.

```
<story description — same body the local plan would carry under its
 ### Story S0N: section, minus the H3 heading>

**Status**: Pending
**FIS**: -
**Phase**: <phase>
**Wave**: W1
**Dependencies**: Depends on #<sibling-issue-N>, Depends on #<sibling-issue-N>
**Parallel**: Yes
**Risk**: <Low|Medium|High>
**Scope**: <one-paragraph scope>
**Acceptance Criteria**:
- [ ] <criterion>

Refs #<prd-N>
Part of #<plan-N>
```

`Dependencies` is `-` when none. `**FIS**` stays `-` (FIS files are generated just-in-time by `andthen:exec-plan --from-issue`). The consumer maps `#<sibling-issue-N>` back to a Story ID via the parent plan's Story Catalog.

> **Two-pass `Depends on` resolution**: `gh issue create` is one-shot, so a story whose dependencies point at later-catalog stories cannot reference real issue numbers at first creation. The producer (`andthen:plan` granular mode) writes placeholder text initially and rewrites the dependencies via a second `gh issue edit <story-N>` call once every sibling issue exists. Story-issue bodies are therefore created twice in the granular flow; the final-form `Depends on #<sibling-issue-N>` shown above is the post-rewrite shape that consumers parse.

> **Producer / consumer race window**: between the first `gh issue create` calls and the final `gh issue edit` rewrites, the parent plan issue body has placeholder `## Story Issues` bullets and individual story issues have placeholder `Depends on` text. Producers (`andthen:plan --to-issue --create-story-issues`) MUST add the label `andthen-finalizing` to the parent plan issue at creation time and remove it after both rewrite passes complete. Consumers (`andthen:exec-plan --from-issue <plan-N>`) MUST check for the label before parsing — when present, stop with `BLOCKED: plan issue #<N> is still being finalized — retry after the producer completes` (default mode prints a wait-and-retry message; `AUTO_MODE` exits with the BLOCKED line).


## Shape Detection (consumer side)

`andthen:exec-plan --from-issue <N>` decides shape from the parent plan issue body alone:

- The parent plan issue body contains `## Story Issues` as a column-0 H2 line (NOT inside a fenced code block ```` ``` ```` and NOT inside an HTML comment `<!-- ... -->`) AND at least one column-0 bare `#<digit>` reference under it (also not inside a code block / comment) → **granular**.
- Otherwise → **single-issue**.

Producers MUST avoid emitting H2s with the parser-anchor names (`## Technical Research`, `## Story Catalog`, `## Story Issues`) inside the inlined `## Technical Research` section or anywhere else in the body — the technical-research synthesis is the largest source of accidental H2 collisions and must be sanitized (downshift any internal H2 to H3 or below) before inlining. Consumers strip fenced code blocks and HTML comments before applying the shape-detection regex.

The Story Catalog table is parsed identically in both shapes — it is the authoritative wave/dependency list. Story-section H3 headings (single-issue) and story-issue bodies (granular) are the per-story content sources, selected by shape.
