# Atlas Model Schemas (`architecture-model.json`, `domain-model.json`)

Canonical schema for the two typed atlas artifacts, distinguished by `kind`:

- **`architecture-model`** – written by the `andthen:describe` skill in `--mode codebase`: a description of the codebase as it stands – clusters (contexts), the modules inside them, and the dependencies between them, every entry anchored to a real path in the repository.
- **`domain-model`** – written by the `andthen:describe` skill in `--mode domain`: a projection of the canonical Ubiquitous Language document – bounded contexts from the doc's clusters, one node per glossary term, overloaded terms carrying per-context meanings, every entry anchored into the doc.

Both are consumed by downstream tooling. They share one invariant core – document shape, id and reference resolution, the `ref` rule, evidence semantics, formatting; `kind` selects the node enum and a few kind-specific rules called out below.

**Machine form.** `architecture-model.schema.json` beside this file (JSON Schema draft 2020-12) is the shape contract; this reference carries the semantics no schema can state.

> **A model, not a ledger or a dump.** Treating it as a ledger invites appended status and history; treating it as a dump invites every file the scanner found or every phrase the doc contains. It is a *description of what exists* – small, typed, and refutable against the source it points at.

## Contents

- Document shape – `meta`, `contexts[]`, `nodes[]`, `edges[]`, `tours[]`
- Identity and references – id uniqueness, reference resolution, the `ref` rule
- Evidence semantics – what each `evidence` value claims and how it renders
- Persistence and precedence – committed projections; who owns context identity
- Altitude – how many nodes a useful model has (kind-dependent)
- Formatting conventions
- Validation
- Example


## Document shape

```jsonc
{
  "schemaVersion": "1",
  "kind": "architecture-model",           // discriminator: "architecture-model" or "domain-model"
  "meta": {
    "project": "Acme Billing",
    "generatedBy": "andthen:describe",
    "date": "2026-08-12",                 // real date, YYYY-MM-DD
    "revision": "a1b2c3d",                // source's last commit, suffixed -dirty when the tree differs
    "summary": "One line on what the model covers."  // optional
  },
  "contexts": [
    { "id": "billing", "name": "Billing", "kind": "bounded-context",
      "summary": "Invoicing, dunning, and payment reconciliation.", "evidence": "declared" }
  ],
  "nodes": [
    { "id": "invoice-engine", "name": "Invoice Engine", "contextId": "billing",
      "kind": "module", "ref": "src/billing/invoice/",
      "summary": "Builds invoices from usage records.",       // optional
      "metrics": { "files": 12, "loc": 2400, "churn": 31, "fanIn": 4, "fanOut": 7 }  // optional
    }
  ],
  "edges": [
    { "from": "invoice-engine", "to": "payment-gateway", "kind": "calls",
      "label": "charge",                  // optional
      "weight": 3,                        // optional
      "evidence": "imports" }
  ],
  "tours": [                              // optional guided walkthroughs
    { "id": "money-in", "title": "How money moves in",
      "steps": [ { "nodeId": "invoice-engine", "note": "Usage becomes an invoice here." } ] }
  ]
}
```

### Top-level fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `schemaVersion` | string | yes | Currently `"1"` for both kinds. Consumers must reject unknown versions rather than best-effort rendering. |
| `kind` | string | yes | `"architecture-model"` or `"domain-model"`. The hard discriminator consumers key on before inspecting anything else. |
| `meta` | object | yes | See below. |
| `contexts` | array of objects | yes | Clusters. At least one; every node belongs to one. |
| `nodes` | array of objects | yes | The things drawn. At least one. |
| `edges` | array of objects | yes | Directed relationships between nodes. Present but `[]` when none. **`domain-model`: must be `[]`** – v1 defines no domain edge kinds. |
| `tours` | array of objects | no | Guided walkthroughs. Omit or `[]` when none. |

### `meta` object

| Field | Type | Required | Notes |
|---|---|---|---|
| `project` | string | yes | Display name. |
| `generatedBy` | string | yes | Producing skill – normally `"andthen:describe"` for both kinds. |
| `date` | string | yes | `YYYY-MM-DD`, a real date – never guessed. |
| `revision` | string | yes | The source's last commit (git short SHA), suffixed `-dirty` when the working tree differs from it. Makes the model refutable: a reader diffs the source against it. |
| `summary` | string | no | One line on what the model covers. |

A consumer counting commits behind HEAD to show staleness reads the SHA before the `-dirty` suffix, and treats a suffixed revision as already stale.

### `contexts[]` object

Same shape for both kinds (`bounded-context` fits the domain doc's clusters).

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | kebab-case, unique across `contexts`. |
| `name` | string | yes | Display name. |
| `kind` | string | yes | One of `bounded-context`, `layer`, `subsystem`, `external`. |
| `summary` | string | yes | One sentence: what this cluster is responsible for. |
| `evidence` | string | yes | `declared` or `inferred` – see **Evidence semantics**. |

### `nodes[]` object

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | kebab-case, unique across `nodes`. |
| `name` | string | yes | Display name. |
| `contextId` | string | yes | Must resolve to a `contexts[].id`. |
| `kind` | string | yes | `architecture-model`: `module`, `package`, `service`, `component`, `store`, `entrypoint`, `external`. `domain-model`: `entity`, `action`, `state`, `policy` (the DDD extraction categories). |
| `ref` | string | yes | Repo-relative path, optionally `path#anchor`. See **the `ref` rule**. |
| `summary` | string | no | One sentence on the node's job (or the term's definition). |
| `metrics` | object | no | Only these five keys: `files`, `loc`, `churn`, `fanIn`, `fanOut`, each a non-negative integer. Omit metrics you did not measure – absent beats guessed. |
| `avoid` | array of strings | no | `domain-model` only: the term's avoid-synonyms from the doc's Avoid column. When present, a non-empty array of non-empty strings – omit the key when there are none, never `[]`. |
| `meanings` | array of objects | no | `domain-model` only: per-context meanings of an overloaded term. Omit unless the term is overloaded. |

Four architecture kinds are what downstream tooling draws the system's runtime shape from, so they carry fixed meanings: a `service` runs or deploys as its own process; an `entrypoint` is where a process starts (a `main`, a CLI, a route table); a `store` is a datastore the code reads or writes at runtime; an `external` is a system outside the repository the code talks to at runtime, its `ref` the code or config that integrates it. A third-party library is not a node – importing one is not a runtime relationship.

`metrics` cover the module the node represents (typically the `ref` directory), not just the file `ref` may point at. Legal on both kinds; the domain emitter omits them.

`meanings`, when present: at least 2 entries; each carries `contextId` (resolving to a `contexts[].id`, all distinct across the array), `label` (the source doc's context text, verbatim), and `meaning` – both non-empty strings. A node with `meanings` renders floating between its meaning contexts rather than on any single sheet.

### `edges[]` object

`architecture-model` only in practice – a `domain-model` carries `edges: []`.

| Field | Type | Required | Notes |
|---|---|---|---|
| `from` | string | yes | Must resolve to a `nodes[].id`. |
| `to` | string | yes | Must resolve to a `nodes[].id`. |
| `kind` | string | yes | One of `depends`, `calls`, `publishes`, `consumes`, `reads`, `writes`. |
| `label` | string | no | Short qualifier shown on the highlighted edge (e.g. the call or topic name). |
| `weight` | integer | no | Positive; relative strength or call count. Consumers treat absent as `1`. |
| `evidence` | string | yes | `imports`, `declared`, `git-coupling`, or `inferred`. |

### `tours[]` object

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | kebab-case, unique across `tours`. |
| `title` | string | yes | Tour name in the selector. |
| `steps` | array of objects | yes | Ordered; at least one. |

Each step carries a `note` (string, why this stop matters) and **exactly one** target – `nodeId` resolving to a `nodes[].id`, or `contextId` resolving to a `contexts[].id`. Two targets is ambiguous, zero is undrawable; both are validation errors.


## Identity and references

Ids are unique **per collection**, not globally – a context and a node may share an id, and referring fields say which collection they resolve against. Every `contextId` (on a node or inside a `meanings` entry), `from`, `to`, and tour-step target must resolve to an existing id in its collection; a dangling reference is an error, never a silently dropped node, edge, or tether.

**The `ref` rule.** `nodes[].ref` is mandatory and repo-relative: no leading `/`, no scheme (`://`), no `~`, and nothing that escapes the repository (a normalized path must not start with `..`). This is the provenance contract – a node without a real location is an assertion nobody can check, and the whole model exists to be checkable. Point at the location that best represents the node, with an optional `#anchor` for a symbol or heading: for `architecture-model`, the directory or file the module lives in; for `domain-model`, the Ubiquitous Language document section the term comes from (`<ul-doc-path>#<section-slug>` – markdown table rows have no per-row anchors, so section granularity is the contract). A coarser architecture node produced by re-clustering is legitimate only when a real directory (or manifest entry) contains exactly that group – never invent an aggregate path. Consumers render `ref` as inert code text, never as a link.


## Evidence semantics

Every context and edge states where its claim came from, so a reader can weigh it:

| Value | Applies to | Claim |
|---|---|---|
| `imports` | edges | Tool-derived from an import/dependency scan or the ecosystem's dependency tooling. |
| `git-coupling` | edges | Tool-derived from co-change frequency in history. Real signal, weaker than a static reference. |
| `declared` | contexts, edges | Stated in project documentation – a Context Map, ADR, architecture doc, or the Ubiquitous Language document itself (a domain model's contexts are `declared`: the grouping is stated in the doc). |
| `inferred` | contexts, edges | Agent judgment from reading the code. Honest guess, not a measurement. |

`inferred` is legitimate – clustering and naming are judgment work by definition – but it must be *marked*, so a reader can tell the model's observations from its opinions. Mislabelling a guess as `imports` is the one failure this field exists to prevent.

Summary prose is authorial under any evidence value – the evidence claim covers the grouping or relationship, not the wording – so regeneration may freely reword summaries.


## Persistence and precedence

Models are **committed projections, not records**. The sources of truth are the codebase (for `architecture-model`) and the Ubiquitous Language document (for `domain-model`); a model that disagrees with its source is stale, not authoritative – regenerate it. Emitters write `<kind>.json` under the `Models` location in the Project Document Index (default `docs/models/`), never hand-edited. `meta.revision` is what makes the commit honest: it names the source revision the model describes, so a reader can tell a stale model from a wrong one.

**Context identity.** When a `Context Map` document exists (Project Document Index), it owns bounded-context identity: a context with `kind: "bounded-context"` takes its `id`/`name` from the map – a model never invents a second name for a mapped context. `layer`, `subsystem`, and `external` contexts are exempt (they describe code shape, not strategic design). Absent a map, models declare their own grouping, marked honestly by `evidence`.


## Altitude

- **`architecture-model`**: **10–60 nodes is the useful range**, at module/package level. Below that the model says nothing the README doesn't; above it the picture stops being readable and starts being a file listing. Past ~120 nodes the altitude is simply wrong: re-cluster into coarser nodes rather than shipping a hairball. Edges follow the same discipline: collapse parallel relationships into one weighted edge, and model a high-fan-in shared component's dependencies once at the right altitude rather than enumerating every consumer.

- **`domain-model`**: neither clause above applies. A glossary projection mirrors its doc 1:1 – the doc is already curated, and dropping terms would break refutability against it. Past ~120 terms the emitter surfaces an altitude note (the doc may want curation) and emits anyway; re-clustering is never the fix.


## Formatting conventions

- **Indent**: 2 spaces; trailing newline at EOF.
- **Key order**: schema-document order within each object shape – diffs then reflect content, not ordering drift.
- **Paths**: POSIX separators, repo-relative.


## Validation

No shipped verb validates a model: the producer checks its candidate against the schema and this reference before writing – shape, id uniqueness, reference resolution (including `meanings` entries), the `ref` rule, tour-step targets, and the domain kind's rules. A failing model is not written – print the itemized violations and direct the fix at the source or the projection.


## Example

A minimal valid `domain-model.json`:

```json
{
  "schemaVersion": "1",
  "kind": "domain-model",
  "meta": {
    "project": "Acme Billing",
    "generatedBy": "andthen:describe",
    "date": "2026-08-12",
    "revision": "a1b2c3d"
  },
  "contexts": [
    {
      "id": "billing",
      "name": "Billing",
      "kind": "bounded-context",
      "summary": "Invoicing and payment terminology.",
      "evidence": "declared"
    },
    {
      "id": "identity",
      "name": "Identity",
      "kind": "bounded-context",
      "summary": "Account and authentication terminology.",
      "evidence": "declared"
    }
  ],
  "nodes": [
    {
      "id": "invoice",
      "name": "Invoice",
      "contextId": "billing",
      "kind": "entity",
      "ref": "docs/UBIQUITOUS_LANGUAGE.md#billing",
      "summary": "A bill issued for metered usage.",
      "avoid": ["bill", "statement"]
    },
    {
      "id": "account",
      "name": "Account",
      "contextId": "billing",
      "kind": "entity",
      "ref": "docs/UBIQUITOUS_LANGUAGE.md#overloaded-terms",
      "summary": "Overloaded across billing and identity.",
      "meanings": [
        { "contextId": "billing", "label": "Billing", "meaning": "The payer account charged for usage." },
        { "contextId": "identity", "label": "User identity", "meaning": "A login principal." }
      ]
    }
  ],
  "edges": []
}
```
