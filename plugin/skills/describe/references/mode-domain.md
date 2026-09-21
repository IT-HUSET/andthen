# Mode: domain


Read codebase, docs, and conversation as source material without modifying them; write or update only the `Ubiquitous Language` document (and, with `--model`, `domain-model.json` under `Models`).

Under `MODEL`, skip the extraction workflow and run **Model Projection** below, projecting the existing `Ubiquitous Language` document into `domain-model.json`: the document is canonical, the model a projection of it, never an independent extraction. `MODEL_ONLY` means the same thing here – the projection writes no documentation either way, so the two differ only in the codebase mode.


## WORKFLOW

### 1. Gather Context

**1.1** Read the existing `Ubiquitous Language` document (see **Project Document Index**) when one exists. Merging into it is the default – a full regenerate discards curated terms, so it happens only when the user asks for one.

**1.2** Explore the codebase to identify domain-relevant sources:
- Domain model files (entities, value objects, aggregates, services)
- API endpoints and route definitions
- Database schemas and migrations
- Documentation: the `Product`, `Architecture`, and `Context Map` documents (see **Project Document Index**), PRDs, specs, README
- Test descriptions (often reveal intended behavior in domain terms)

On a large codebase, spawn generic subagents whose prompts carry the source areas to scan and a read-only scope – the installed role agent for the tier when available, else inherit.

**1.3** If SCOPE is provided, focus exploration on that area.

### 2. Extract Domain Terms

For each source, extract domain terms across the usual DDD categories – entities, actions/processes, states, rules/policies, and relationships – never technical jargon (framework terms, library names) that is not domain language. Note any inconsistencies (same concept, different names across files).

### 3. Resolve Ambiguity and Synonymy

**3.1** Identify synonym clusters – terms that refer to the same concept – and pick a **canonical term** for each.

**3.2** Identify overloaded terms – same word meaning different things in different contexts, e.g. "account" (user account vs billing account vs bank account) – and assign bounded context qualifiers.

**3.3** Merge new terms into the existing glossary, marking additions `(new)` and changes `(updated)`; on an explicit regenerate request, replace it instead.

### 4. Generate Glossary

When a `Context Map` document exists (see **Project Document Index**), group the `## [Domain Cluster]` headings by its bounded contexts and draw the `Bounded Context` values from it, so the glossary and the map stay aligned; otherwise cluster by domain theme as usual.

Output the `Ubiquitous Language` document in the shape of its template in `project-document-templates.md` – cluster tables, then `## Overloaded Terms`. The template header is the row contract – one sentence under 200 characters saying what the term is and where it lives (`Tenant | An organization-level account | company, org, workspace`), synonyms only in Avoid – and it binds merged rows as much as new ones: an existing row past it is rewritten, not preserved.


## MODEL PROJECTION (`--model`)

Project the `Ubiquitous Language` document into the typed `domain-model` artifact defined in `architecture-model.md` – `kind: "domain-model"`, `meta.generatedBy: "andthen:describe"`. The projection mirrors the doc 1:1: every context and node is refutable against the doc at section granularity.

The projection reads the `Ubiquitous Language` document (see **Project Document Index**). If it does not exist, stop with a pointer to run this skill's extraction first – never fabricate a glossary just to emit a model.

**Projection contract** (doc → model):

- **Cluster discriminator**: an H2 is a cluster iff its first table's header row begins `| Term | Definition |`; the reserved sections `Overloaded Terms`, `Usage Notes`, and `Changelog` are never clusters or nodes (`Usage Notes` has a `| Term | Preferred usage |` table – the Definition column is what excludes it).
- **Contexts**: one per cluster – `id` = kebab-slug of the heading, `name` = heading text, `kind: "bounded-context"`, `evidence: declared` (the grouping is stated in the doc), `summary` = your one-line gloss of the cluster's scope (summary prose is authorial; the evidence claim covers the grouping, not the wording).
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
  - **`meanings` entries** – one per context/meaning cell pair: `label` = the doc's context text verbatim (honest to the source), `contextId` = the best-fit cluster by your judgment, never dangling and distinct across the term's meanings (the tie-break toward the term's home cluster applies only where it keeps them distinct).
  - **Degraded overload** – when distinct `contextId`s cannot be assigned without falsifying the source (fewer clusters than meanings, or honest judgment collapsing onto one cluster), emit the term as a plain node without `meanings` and surface the degraded overload in the emission summary.
- **Empty projection**: a doc yielding zero clusters or zero term nodes is this skill's error – stop with a message naming the empty projection and write no model file; the user must never see a raw gate failure from a run they did not invoke as validation.

**Validate before writing**: check the candidate against `architecture-model.schema.json` and `architecture-model.md`, then write it as `domain-model.json` under the `Models` location from the **Project Document Index** (default: `docs/models/`), a committed projection per the schema's Persistence and precedence: `meta.revision` is the document revision it projects, and the document stays the record.

On success, print the output path plus the emission summary (context/node counts, merged duplicates, any altitude note).


## OUTPUT (extraction runs – `--model` output is defined in Model Projection above)

Save to the `Ubiquitous Language` document location from the **Project Document Index** (default: `docs/UBIQUITOUS_LANGUAGE.md`)

When complete, print the output path and suggest:
1. Review the glossary for accuracy with domain experts
2. Re-run this mode with `--model` to project the glossary into a Domain Model
