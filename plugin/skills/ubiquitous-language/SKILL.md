---
description: Extract and maintain the project's Ubiquitous Language document (per the Project Document Index) from the codebase, documentation, and conversation, optionally projecting it into a typed Domain Model (`--model`) for atlas rendering. Trigger on 'build a glossary', 'extract ubiquitous language', 'domain terminology cleanup', 'emit a domain model'.
argument-hint: "[--update] [--model] [scope or focus area]"
---

# Extract and Maintain Ubiquitous Language


Read codebase, docs, and conversation as source material without modifying them; write or update only the `Ubiquitous Language` document (and, with `--model`, the `Domain Model` artifact).


## VARIABLES

ARGUMENTS: $ARGUMENTS

### Parse Arguments
- `--update` flag → UPDATE_MODE (merge mode)
- `--model` flag → MODEL: project the existing `Ubiquitous Language` document into `domain-model.json` – skip the extraction workflow and run **Model Projection** below. The document is canonical; the model is a projection of it, never an independent extraction.
- Remaining text (flag tokens excluded) → SCOPE (focus area, e.g., "authentication", "billing", or blank for full project)


## GOTCHAS
- Including technical jargon (framework terms, library names) that aren't domain language
- Glossary entries without usage examples are hard to apply


## WORKFLOW

### 1. Gather Context

**1.1** If UPDATE_MODE: read the existing `Ubiquitous Language` document (see **Project Document Index**) to understand current glossary state.

**1.2** Explore the codebase to identify domain-relevant sources:
- Domain model files (entities, value objects, aggregates, services)
- API endpoints and route definitions
- Database schemas and migrations
- Documentation: the `Product`, `Architecture`, and `Context Map` documents (see **Project Document Index**), PRDs, specs, README
- Test descriptions (often reveal intended behavior in domain terms)

Use Explore (or general-purpose) sub-agent for large codebases.

**1.3** If SCOPE is provided, focus exploration on that area.

### 2. Extract Domain Terms

For each source, extract domain terms across the usual DDD categories – entities, actions/processes, states, rules/policies, and relationships.

For each term, note:
- Where it appears (file:line references)
- How it's used (entity name, function name, variable, comment)
- Any inconsistencies (same concept, different names across files)

### 3. Resolve Ambiguity and Synonymy

**3.1** Identify synonym clusters – terms that refer to the same concept:
- e.g., "client" vs "customer" vs "user" vs "account holder"
- e.g., "cancel" vs "terminate" vs "deactivate" vs "suspend"

**3.2** For each cluster, pick a **canonical term** based on:
- Which term is most used in the codebase
- Which term best matches domain expert language
- Which term is least ambiguous

**3.3** Identify overloaded terms – same word meaning different things in different contexts:
- e.g., "account" (user account vs billing account vs bank account)
- Assign bounded context qualifiers

**3.4** If UPDATE_MODE: merge new terms with existing glossary, marking changes with `(new)` or `(updated)`.

### 4. Generate Glossary

When a `Context Map` document exists (see **Project Document Index**), group the `## [Domain Cluster]` headings by its bounded contexts and draw the `Bounded Context` values from it, so the glossary and the map stay aligned; otherwise cluster by domain theme as usual.

Output the `Ubiquitous Language` document using this structure:

```markdown
# Ubiquitous Language
> Domain glossary for [Project Name]. Use these exact terms in code, documentation, and discussion.

## [Domain Cluster]
| Term | Definition | Avoid (synonyms) | Bounded Context |
|------|-----------|-------------------|-----------------|
| Tenant | An organization-level account | company, org, workspace | Multi-tenancy |

## Overloaded Terms
| Term | Context A | Meaning A | Context B | Meaning B |
|------|-----------|-----------|-----------|-----------|

## Changelog
- [date]: Initial extraction / Updated [terms]
```


### 5. Validation

- [ ] No synonym appears as a canonical term elsewhere
- [ ] Overloaded terms are identified with context qualifiers
- [ ] Terms are actionable – a developer can use them to name things


## MODEL PROJECTION (`--model`)

Project the `Ubiquitous Language` document into the typed `domain-model` artifact defined in [`architecture-model.md`](${CLAUDE_PLUGIN_ROOT}/references/architecture-model.md) – `kind: "domain-model"`, `meta.generatedBy: "andthen:ubiquitous-language"`. The projection mirrors the doc 1:1: every context and node is refutable against the doc at section granularity.

**Input**: the `Ubiquitous Language` document (see **Project Document Index**). If it does not exist, stop with a pointer to run this skill's extraction first – never fabricate a glossary just to emit a model.

**Projection contract** (doc → model):

- **Cluster discriminator**: an H2 is a cluster iff its first table's header row begins `| Term | Definition |`; the reserved sections `Overloaded Terms`, `Usage Notes`, and `Changelog` are never clusters or nodes (`Usage Notes` has a `| Term | Preferred usage |` table – the Definition column is what excludes it).
- **Contexts**: one per cluster – `id` = kebab-slug of the heading, `name` = heading text, `kind: "bounded-context"`, `evidence: declared` (the grouping is stated in the doc), `summary` = your one-line gloss of the cluster's scope (summary prose is authorial; the evidence claim covers the grouping, not the wording).
- **Term nodes**: one per glossary row – `id` = kebab-slug of the term (lowercase, non-alphanumeric runs → single hyphen); `contextId` = the `Bounded Context` column value matched case-insensitively to a context name when that column exists, falling back to the enclosing cluster section when the value matches no context (surface the unmatched value in the emission summary – never a dangling reference, never a silent stop), else the enclosing cluster section; `kind` = the term's DDD category by your judgment (`entity | action | state | policy`); `ref` = `<ul-doc-path>#<cluster-heading-slug>` (section-level – markdown table rows have no per-row anchors); `summary` = the definition, condensed; `avoid` = the Avoid column's synonyms – omit the key when the column is empty, never `[]`. A term appearing in two cluster sections keeps its first occurrence; surface the duplicate in the emission summary, never emit it twice.
- **Overloaded rows**: each distinct term in `## Overloaded Terms` extends its case-insensitively matching glossary node, or – when none exists – mints a node with judged `kind` and `ref` = `<ul-doc-path>#overloaded-terms`. Multiple rows for one term merge into one node carrying all meanings. Each context/meaning cell pair becomes a `meanings` entry: `label` = the doc's context text verbatim (honest to the source), `contextId` = the best-fit cluster by your judgment – never dangling, and distinct across the term's meanings (the tie-break toward the term's home cluster applies only where it keeps them distinct). When distinct `contextId`s cannot be assigned without falsifying the source – fewer clusters than meanings, or honest judgment collapsing onto one cluster – emit the term as a plain node without `meanings` and surface the degraded overload in the emission summary. A minted node's own `contextId` = its first meaning's `contextId`; a matched glossary node keeps its cluster.
- **Altitude**: mirror the doc 1:1 – no curation cap. Past ~120 terms, surface an altitude note (the doc may want curation) and emit anyway.
- **Empty projection**: a doc yielding zero clusters or zero term nodes is this skill's error – stop with a message naming the empty projection and write no model file; the user must never see a raw gate failure from a run they did not invoke as validation.

**Validate before writing**: check every schema invariant from `architecture-model.md` – discriminators, id uniqueness, reference resolution (node and `meanings` `contextId`s), `ref` form, the domain node enum, `meanings`/`avoid` shapes, `edges: []` – then write to the `Domain Model` location from the **Project Document Index** (default: `.agent_temp/models/domain-model.json` – a transient projection per the schema's Persistence and precedence, regenerated on demand; the document is the record). A model that fails validation is not written: print the itemized violations and direct the fix at the document or the projection, so the user never faces an unexplained gate failure.

On success, print the output path plus the emission summary (context/node counts, merged duplicates, any altitude note) and suggest rendering it with the `andthen:visualize` skill.


## OUTPUT (extraction runs – `--model` output is defined in Model Projection above)

Save to the `Ubiquitous Language` document location from the **Project Document Index** (default: `docs/UBIQUITOUS_LANGUAGE.md`)

When complete, print the output path and suggest:
1. Review the glossary for accuracy with domain experts
2. Run the `andthen:ubiquitous-language` skill with `--update` periodically to keep it current
3. Run the `andthen:review` skill with `--mode code` to check code against the glossary
4. Run the `andthen:ubiquitous-language` skill with `--model` to project the glossary into a Domain Model for atlas rendering
