# Plan Issue Body Shape

**Single canonical source** for the plan-issue body shape produced by `andthen:plan --to-issue` and consumed by `andthen:exec-plan --from-issue`.

> Skills that reference this document: `plan`, `exec-plan`.

Local plans are JSON ([`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md)). The markdown body shape here is the **GitHub transport** only – `--to-issue` renders the in-memory plan as markdown; `--from-issue` parses the body into a local `plan.json` once and drives execution from it.

Two shapes – **single-issue** (default `--to-issue`) and **granular** (`--to-issue --create-story-issues`). Both use the same parser-friendly H2 anchors so consumers detect shape and extract sections without bespoke regex. Story Catalog column order: see [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md) (Plan Issue Catalog).

`Dependencies` cells follow the local-plan contract: `-` or comma-separated Story IDs. No prose (`Blocks A-G complete`). Granular story bodies may add optional `Depends on #<sibling-issue-N>` navigation; the parent catalog stays authoritative for scheduling.

The optional `Owner` column makes claiming visible on the issue itself: a developer claims a story by setting its `Owner` cell (and opening the `feat/S0N-...` branch) so others don't pick it up. Advisory coordination, not a lock – the issue stays the durable contract. Omission/empty-cell semantics: `data-contract.md` (Plan Issue Catalog).

## Link Conventions

Exact link forms – contracts, not suggestions. `andthen:exec-plan --from-issue` extracts provenance from them.

| Token | Meaning | Where it appears |
|---|---|---|
| `> **PRD**: ...` | Durable PRD source: local `prd.md` path or `github://issue/<N>` | Header of every plan issue |
| `Refs #N` | Provenance: this artifact derives from issue `#N` | Footer of any plan, PRD, story, clarify, or triage issue when an input issue was supplied |
| `Part of #N` | Containment: this story issue belongs to plan issue `#N` | Footer of every story issue created by `--create-story-issues` |
| `Depends on #N` | Optional child-issue navigation | Inline in a granular story's optional `Depends on` note; parent Story Catalog remains authoritative |

`Refs #N` and `Part of #N` are independent: a story issue carries both – `Refs` to the originating PRD issue, `Part of` to the parent plan issue.


## Parser-Friendly Section Markers

Both shapes use these H2 anchors, matched by `^## <name>$`. Do not introduce identical H2s elsewhere.

- **`## Shared Decisions`** – optional; bullets naming inter-story interface contracts/naming conventions/shared abstractions (renders JSON `sharedDecisions[]`).
- **`## Binding Constraints`** – optional; verbatim PRD spans + heading anchors that flow unchanged into FIS Required Context (renders JSON `bindingConstraints[]`).
- **`## Story Catalog`** – markdown table; columns per [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md).
- **`## Story Issues`** – granular-shape only; the **shape-detection signal** for `exec-plan --from-issue` (full rule: see Shape Detection below).

> **Legacy parser tolerance**: `## Technical Research` is no longer emitted. Consumers tolerate it in legacy issues (read but not materialized). New issues must not emit it.

Single-issue story sections use H3: `### Story S0N: <name>`. Granular story issues do not nest a `### Story` heading – the issue title carries the name.


## Single-Issue Shape

`andthen:plan --to-issue` default. Everything lives in one issue; no story issues created.

Body skeleton:

```
> **PRD**: <prd.md path or github://issue/<prd-N>>

<plan summary – 1–3 paragraphs of context>

## Shared Decisions

<optional – 3-6 bullets naming inter-story interface contracts; omit section when none apply>

## Binding Constraints

<optional – verbatim PRD spans + heading anchors; omit section when none apply>

## Story Catalog

| ID | Name | Phase | Wave | Dependencies | Parallel | Risk | Status | FIS | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S01 | <name> | <phase> | W1 | - | Yes | Low | Pending | - | - |
| S02 | <name> | <phase> | W1 | - | Yes | Medium | Pending | - | - |

### Story S01: <name>

**Scope**: <one-paragraph scope>
**Source refs**: <PRD feature IDs and anchors>
**Asset refs**: <optional refs, or omit>

### Story S02: <name>

<same compact story brief as S01>

Refs #<prd-N>
```

Story briefs render the JSON brief fields: `Scope` (`scope`) and `Source refs` (`sourceRefs`) for PRD-backed stories, with optional provenance/asset refs/notes. The Story Catalog is the only status/FIS/scheduling surface. The `> **PRD**:` header is required so the `andthen:exec-plan` skill's `--from-issue` flow can resolve `Source refs` when generating JIT FIS files. Omit the `Refs #<prd-N>` footer when no PRD issue was the input.


## Granular Shape

`andthen:plan --to-issue --create-story-issues`. One parent plan issue + N child story issues.

### Parent Plan Issue Body Skeleton

```
> **PRD**: <prd.md path or github://issue/<prd-N>>

<plan summary – 1–3 paragraphs>

## Shared Decisions

<optional – same shape as single-issue; omit when none apply; not duplicated into story issues>

## Binding Constraints

<optional – same shape as single-issue; omit when none apply; not duplicated into story issues>

## Story Catalog

| ID | Name | Phase | Wave | Dependencies | Parallel | Risk | Status | FIS | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S01 | <name> | <phase> | W1 | - | Yes | Low | Pending | - | - |

## Story Issues

- #<story-issue-1> – <story name> – <one-line scope>
- #<story-issue-2> – <story name> – <one-line scope>

Refs #<prd-N>
```

The plan body is created first with placeholders under `## Story Issues`; `gh issue edit <plan-N> --body-file` rewrites the section after every story issue exists so rendered numbers are real.

### Story Issue Body Skeleton

Title is `S0N: <name>`; body has no nested `### Story` heading. Body carries the same compact brief as a local plan story. Status, FIS path, phase, wave, dependencies, parallelism, risk live in the parent Story Catalog.

```
<story description – same compact body the single-issue shape carries
 under its `### Story S0N: <name>` heading>

**Scope**: <one-paragraph scope>
**Source refs**: <PRD feature IDs and anchors>
**Depends on**: #<sibling-issue-N>, #<sibling-issue-N>  <!-- optional; omit when none -->

Refs #<prd-N>
Part of #<plan-N>
```

Prose deps are invalid. Parent Story Catalog stays authoritative; its `FIS` cells stay `-` because FIS files are JIT-generated by the `andthen:exec-plan` skill (`--from-issue`).

> **Two-pass `Depends on` resolution**: `gh issue create` is one-shot, so a story whose deps point at later-catalog stories cannot reference real issue numbers on first creation. `andthen:plan` granular mode writes placeholder text initially and rewrites via a second `gh issue edit <story-N>` once every sibling exists. Story bodies are created twice; the final `Depends on #<sibling-issue-N>` shown above is the post-rewrite shape.

> **Producer / consumer race window**: between first `gh issue create` and final `gh issue edit` rewrites, the parent plan body has placeholder `## Story Issues` bullets and stories may have placeholder `Depends on` text. Producers (the `andthen:plan` skill with `--to-issue --create-story-issues`) MUST add label `andthen-finalizing` to the parent plan issue at creation and remove it after both rewrites complete. Consumers (the `andthen:exec-plan` skill with `--from-issue <plan-N>`) MUST check for the label before parsing – when present, stop with `BLOCKED: plan issue #<N> is still being finalized – retry after the producer completes` (default: print wait-and-retry; `AUTO_MODE` exits with the BLOCKED line).


## Shape Detection (consumer side)

The `andthen:exec-plan` skill's `--from-issue <N>` mode decides shape from the parent body alone:

- Parent body contains `## Story Issues` as a column-0 H2 line (NOT in a fenced code block ```` ``` ```` or HTML comment `<!-- ... -->`) AND ≥1 story-issue reference line under it (also not in code/comment) → **granular**. A story-issue reference line begins with optional whitespace, an optional Markdown bullet marker (`- `), then `#<digit>`; the producer's canonical final shape is `- #<story-issue-N> – <story name> – <one-line scope>`, where `<story-issue-N>` is the resolved numeric GitHub issue number for that story.
- Otherwise → **single-issue**.

Producers MUST avoid emitting parser-anchor H2 names (`## Shared Decisions`, `## Binding Constraints`, `## Story Catalog`, `## Story Issues`) outside their canonical positions – accidental collisions inside inlined PRD spans (under `## Binding Constraints`) must be sanitized by downshifting to H3+ before inlining. Consumers strip fenced code blocks and HTML comments before applying the shape-detection regex.

The Story Catalog parses identically in both shapes – authoritative wave/dependency list. Story-section H3 headings (single-issue) and story-issue bodies (granular) are the per-story content sources, selected by shape.
