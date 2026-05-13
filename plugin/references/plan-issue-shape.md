# Plan Issue Body Shape

This document is the **single canonical source** for the body shape of a plan issue produced by the `andthen:plan` skill in `--to-issue` mode and consumed by the `andthen:exec-plan` skill in `--from-issue` mode.

> Skills that reference this document: `plan`, `exec-plan`.

Local plans are JSON ([`plan-schema.md`](plan-schema.md)). The markdown body shape defined here is the **GitHub transport** only – `--to-issue` renders the in-memory plan object as markdown into an issue body; `--from-issue` parses the issue body into a local `plan.json` ledger once and then drives execution from the local ledger.

The contract has two shapes – **single-issue** (default `--to-issue`) and **granular** (`--to-issue --create-story-issues`). Both use the same parser-friendly H2 anchors so a downstream consumer can detect shape and extract sections without bespoke regex. The Story Catalog table column order is documented in [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md) (Plan Issue Catalog).

Story Catalog `Dependencies` cells follow the same machine-readable contract as local plans: `-` or comma-separated Story IDs from the same table. Do not put prose such as `Blocks A-G complete` in the catalog. Granular story issue bodies may add optional `Depends on #<sibling-issue-N>` navigation after issue numbers exist, but the parent catalog remains the scheduling source of truth.


## Link Conventions

Plan and story issues use these exact link forms – they are contracts, not suggestions. `andthen:exec-plan --from-issue` extracts provenance from them.

| Token | Meaning | Where it appears |
|---|---|---|
| `> **PRD**: ...` | Durable PRD source: local `prd.md` path or `github://issue/<N>` | Header of every plan issue |
| `Refs #N` | Provenance: this artifact derives from issue `#N` | Footer of any plan, PRD, story, clarify, or triage issue when an input issue was supplied |
| `Part of #N` | Containment: this story issue belongs to plan issue `#N` | Footer of every story issue created by `--create-story-issues` |
| `Depends on #N` | Optional child-issue navigation for inter-story ordering | Inline in a granular story issue's optional `Depends on` note; the parent Story Catalog remains the scheduling source of truth |

`Refs #N` and `Part of #N` are independent: a story issue carries both – `Refs` to the originating PRD issue, `Part of` to the parent plan issue.


## Parser-Friendly Section Markers

Both shapes use these H2 anchors. The consumer matches them by `^## <name>$` against a markdown body – do not introduce identical H2s elsewhere in the body.

- **`## Shared Decisions`** – optional; bullets naming inter-story interface contracts, naming conventions, or shared abstractions (renders the JSON `sharedDecisions[]`).
- **`## Binding Constraints`** – optional; verbatim PRD spans + heading anchors that flow unchanged into FIS Required Context (renders the JSON `bindingConstraints[]`).
- **`## Story Catalog`** – standard markdown table; columns per [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md).
- **`## Story Issues`** – granular-shape only; presence of this section with at least one `#<digit>` reference under it is the **shape-detection signal** for `exec-plan --from-issue`.

> **Legacy parser tolerance**: `## Technical Research` is no longer emitted by producers. Consumers retain tolerance for legacy issues – if encountered, the section is read but not materialized. New plan issues must not emit this section.

Story sections in the single-issue shape use H3: `### Story S0N: <name>`. Granular-shape story issues do not nest a duplicate `### Story` heading – the issue title carries the story name.


## Single-Issue Shape

Used by `andthen:plan --to-issue` (default). Everything lives in one issue; no story issues are created.

Body skeleton:

```
> **PRD**: <prd.md path or github://issue/<prd-N>>

<plan summary – 1–3 paragraphs of context>

## Shared Decisions

<optional – 3-6 bullets naming inter-story interface contracts; omit section when none apply>

## Binding Constraints

<optional – verbatim PRD spans + heading anchors; omit section when none apply>

## Story Catalog

| ID | Name | Phase | Wave | Dependencies | Parallel | Risk | Status | FIS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S01 | <name> | <phase> | W1 | - | Yes | Low | Pending | - |
| S02 | <name> | <phase> | W1 | - | Yes | Medium | Pending | - |

### Story S01: <name>

**Scope**: <one-paragraph scope>
**Source refs**: <PRD feature IDs and anchors>
**Asset refs**: <optional refs, or omit>

### Story S02: <name>

<same compact story brief as S01>

Refs #<prd-N>
```

Story briefs render the JSON story brief fields: `Scope` (`scope`) plus `Source refs` (`sourceRefs`) for PRD-backed stories, with optional provenance, asset refs, and notes. The Story Catalog is the only status/FIS/scheduling surface. The `> **PRD**:` header is required so `exec-plan --from-issue` can resolve `Source refs` when generating JIT FIS files. Omit the `Refs #<prd-N>` footer when no PRD issue was the input.


## Granular Shape

Used by `andthen:plan --to-issue --create-story-issues`. Produces one parent plan issue plus N child story issues.

### Parent Plan Issue Body Skeleton

```
> **PRD**: <prd.md path or github://issue/<prd-N>>

<plan summary – 1–3 paragraphs>

## Shared Decisions

<optional – same shape as single-issue; omit when none apply; not duplicated into story issues>

## Binding Constraints

<optional – same shape as single-issue; omit when none apply; not duplicated into story issues>

## Story Catalog

| ID | Name | Phase | Wave | Dependencies | Parallel | Risk | Status | FIS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S01 | <name> | <phase> | W1 | - | Yes | Low | Pending | - |

## Story Issues

- #<S1-issue-N> – <story name> – <one-line scope>
- #<S2-issue-N> – <story name> – <one-line scope>

Refs #<prd-N>
```

The plan body is created first with placeholders under `## Story Issues`, then `gh issue edit <plan-N> --body-file` rewrites this section after every story issue exists, so the rendered numbers are real.

### Story Issue Body Skeleton

The issue title is `S0N: <name>`; the body has no nested `### Story` heading. The body carries the same compact story brief as a local plan story. Status, FIS path, phase, wave, dependencies, parallelism, and risk stay in the parent Story Catalog.

```
<story description – same compact body the single-issue shape carries
 under its `### Story S0N: <name>` heading>

**Scope**: <one-paragraph scope>
**Source refs**: <PRD feature IDs and anchors>
**Depends on**: #<sibling-issue-N>, #<sibling-issue-N>  <!-- optional; omit when none -->

Refs #<prd-N>
Part of #<plan-N>
```

Story issue `**Depends on**` notes are optional navigation only; omit the field when there are no dependencies. When emitted, each dependency uses a sibling issue number after the two-pass rewrite. Prose dependencies are invalid. The parent Story Catalog remains authoritative for scheduling, and its `FIS` cells stay `-` because FIS files are generated just-in-time by `andthen:exec-plan --from-issue`.

> **Two-pass `Depends on` resolution**: `gh issue create` is one-shot, so a story whose dependencies point at later-catalog stories cannot reference real issue numbers at first creation. The producer (`andthen:plan` granular mode) writes placeholder navigation text initially and rewrites it via a second `gh issue edit <story-N>` call once every sibling issue exists. Story-issue bodies are therefore created twice in the granular flow; the final-form `Depends on #<sibling-issue-N>` shown above is the post-rewrite navigation shape.

> **Producer / consumer race window**: between the first `gh issue create` calls and the final `gh issue edit` rewrites, the parent plan issue body has placeholder `## Story Issues` bullets and individual story issues may have placeholder `Depends on` text. Producers (`andthen:plan --to-issue --create-story-issues`) MUST add the label `andthen-finalizing` to the parent plan issue at creation time and remove it after both rewrite passes complete. Consumers (`andthen:exec-plan --from-issue <plan-N>`) MUST check for the label before parsing – when present, stop with `BLOCKED: plan issue #<N> is still being finalized – retry after the producer completes` (default mode prints a wait-and-retry message; `AUTO_MODE` exits with the BLOCKED line).


## Shape Detection (consumer side)

`andthen:exec-plan --from-issue <N>` decides shape from the parent plan issue body alone:

- The parent plan issue body contains `## Story Issues` as a column-0 H2 line (NOT inside a fenced code block ```` ``` ```` and NOT inside an HTML comment `<!-- ... -->`) AND at least one column-0 bare `#<digit>` reference under it (also not inside a code block / comment) → **granular**.
- Otherwise → **single-issue**.

Producers MUST avoid emitting H2s with the parser-anchor names (`## Shared Decisions`, `## Binding Constraints`, `## Story Catalog`, `## Story Issues`) anywhere outside their canonical position in the body – accidental H2 collisions inside inlined PRD spans (under `## Binding Constraints`) must be sanitized by downshifting to H3 or below before inlining. Consumers strip fenced code blocks and HTML comments before applying the shape-detection regex.

The Story Catalog table is parsed identically in both shapes – it is the authoritative wave/dependency list. Story-section H3 headings (single-issue) and story-issue bodies (granular) are the per-story content sources, selected by shape.
