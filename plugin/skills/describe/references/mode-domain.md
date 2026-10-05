# Mode: domain

Read the codebase, docs, and conversation as source material without modifying them. Write only the `Ubiquitous Language` document and, with a model flag, `domain-model.json` under `Models`.

## Input

Which steps run:

- No model flag – the extraction, Steps 1–4.
- `MODEL` – the extraction, then Step 5's projection.
- `MODEL_ONLY` – Step 5 alone. With no `Ubiquitous Language` document, run Steps 1–4 first and project what they wrote; say in the summary that the glossary was written, because the model's refs anchor into it.

## Rules

`Ubiquitous Language`, `Product`, `Architecture`, `Context Map`, and `Models` are Project Document Index entries.

## Workflow

### 1. Gather context

Read the existing `Ubiquitous Language` document when one exists. Merge into it by default: a full regenerate discards curated terms, so it happens only when the user asks for one.

Explore for domain-relevant sources, focused on `SCOPE` when it is given, including the `Product`, `Architecture`, and `Context Map` documents. On a large codebase, spawn `worker` subagents whose prompts carry the source areas to scan and a read-only scope.

**Gate**: every source area in scope is scanned.

### 2. Extract domain terms

For each source, extract domain terms across the usual DDD categories – entities, actions and processes, states, rules and policies, relationships – never technical jargon (framework terms, library names) that is not domain language. Note every inconsistency: one concept named differently across files.

**Gate**: every source's terms are extracted and every inconsistency is noted.

### 3. Resolve ambiguity and synonymy

- **Synonym clusters** – terms for the same concept get one **canonical term**.
- **Overloaded terms** – one word meaning different things in different contexts, such as "account" (user, billing, or bank account), get bounded-context qualifiers.
- **Merge** new terms into the existing glossary, marking additions `(new)` and changes `(updated)`.

**Gate**: every extracted term sits in one cluster or is marked overloaded, and every Step 2 inconsistency is resolved or listed.

### 4. Write the glossary

When a `Context Map` document exists, group the `## [Domain Cluster]` headings by its bounded contexts and draw the `Bounded Context` values from it, so the glossary and the map stay aligned. Otherwise cluster by domain theme.

Write the `Ubiquitous Language` document (default `docs/UBIQUITOUS_LANGUAGE.md`) in the shape of its template in `project-document-templates.md`: cluster tables, then `## Overloaded Terms`.

**Gate**: the glossary is written with every cluster table and `## Overloaded Terms`.

### 5. Model projection

Project the `Ubiquitous Language` document into the typed `domain-model` artifact `architecture-model.md` defines – `kind: "domain-model"`, `meta.generatedBy: "andthen:describe"`. The projection mirrors the document 1:1: every context and node is refutable against it at section granularity.

**Projection contract** (document → model):

- **Cluster discriminator**: an H2 is a cluster iff its first table's header row begins `| Term | Definition |`. The reserved sections `Overloaded Terms`, `Usage Notes`, and `Changelog` are never clusters or nodes (`Usage Notes` has a `| Term | Preferred usage |` table – the Definition column is what excludes it).
- **Contexts**: one per cluster – `id`/`name` from the `Context Map` for a mapped context, else `id` = kebab-slug of the heading and `name` = heading text; `kind: "bounded-context"`, `evidence: declared`, `summary` = your one-line gloss of the cluster's scope.
- **Term nodes**: one per glossary row.
  - `id` – kebab-slug of the term: lowercase, non-alphanumeric runs → single hyphen.
  - `contextId` – the `Bounded Context` column value matched case-insensitively to a context name when that column exists, else the enclosing cluster section. A value matching no context falls back to the enclosing cluster section and is surfaced in the emission summary – never a dangling reference, never a silent stop.
  - `kind` – the term's DDD category by your judgment: `entity | action | state | policy`.
  - `ref` – `<ul-doc-path>#<cluster-heading-slug>`, section-level because markdown table rows have no per-row anchors.
  - `summary` – the definition, condensed.
  - `avoid` – the Avoid column's synonyms; omit the key when the column is empty, never `[]`.

  A term appearing in two cluster sections keeps its first occurrence; surface the duplicate in the emission summary, never emit it twice.
- **Overloaded rows**: each distinct term in `## Overloaded Terms` carries per-context meanings.
  - **Match or mint** – the term extends its case-insensitively matching glossary node, or mints one with judged `kind` and `ref` = `<ul-doc-path>#overloaded-terms` when none exists. A minted node's own `contextId` = its first meaning's `contextId`; a matched glossary node keeps its cluster.
  - **Merge** – multiple rows for one term become one node carrying all meanings.
  - **`meanings` entries** – one per context/meaning cell pair: `label` = the document's context text verbatim (honest to the source), `contextId` = the best-fit cluster by your judgment, never dangling and distinct across the term's meanings (the tie-break toward the term's home cluster applies only where it keeps them distinct).
  - **Degraded overload** – when distinct `contextId`s cannot be assigned without falsifying the source (fewer clusters than meanings, or honest judgment collapsing onto one cluster), emit the term as a plain node without `meanings` and surface the degraded overload in the emission summary.

Write it as `domain-model.json` under `Models` (default `docs/models/`); `meta.revision` is the document revision it projects.

**Gate**: `domain-model.json` is written, every context and node traceable to the document.

## Output

Print the output paths. After a projection, add the emission summary: context and node counts, merged duplicates, any altitude note.

## Follow-up

Without a model flag, suggest `--model-only` to project the glossary into a Domain Model.
