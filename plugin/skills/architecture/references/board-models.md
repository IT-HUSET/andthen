# Board Model Schemas (`event-storm`, `context-map`)

Canonical schema for the two typed boards the `andthen:architecture` skill emits with its Markdown reports, distinguished by `kind`:

- **`event-storm`** – written by `--mode event-storming`: the session's board – stickies on a timeline, the flows between them, and the candidates the level harvests. The report's eight sections stay the human record; the JSON is what a board view draws.
- **`context-map`** – written by `--mode strategic-design`: bounded contexts and the integration pattern on every relationship, one file per map (`current`, `target`, or the `registered` one the Context Map document records).

Both follow the atlas models' conventions (`architecture-model.md`): 2-space indent, schema-document key order, POSIX repo-relative paths.

`event-storm.schema.json` and `context-map.schema.json` beside this file (JSON Schema draft 2020-12) are the shape contract; this reference carries the semantics no schema can state.

## `event-storm`

```jsonc
{
  "schemaVersion": "1",
  "kind": "event-storm",
  "meta": {
    "project": "Acme Billing",
    "generatedBy": "andthen:architecture",
    "date": "2026-08-12",                 // real date, YYYY-MM-DD
    "revision": "a1b2c3d",                // source's last commit, suffixed -dirty when the tree differs
    "level": "process-modeling",          // big-picture | process-modeling | design-level
    "scope": "Order fulfilment, checkout to delivery",   // one line
    "source": "docs/specs/fulfilment/prd.md"             // the PRD or intent path, or "brownfield"
  },
  "lanes": [                              // optional swimlanes, one per process or actor
    { "id": "checkout", "label": "Checkout", "order": 0 }
  ],
  "stickies": [
    { "id": "place-order", "kind": "command", "label": "Place order", "lane": "checkout", "order": 0 },
    { "id": "order-placed", "kind": "event", "label": "Order placed", "lane": "checkout", "order": 1,
      "pivotal": true, "cluster": "ordering" },
    { "id": "who-cancels", "kind": "hotspot", "label": "Who may cancel after payment?",
      "attachedTo": "order-placed", "lane": "checkout", "order": 2 }
  ],
  "flows": [
    { "from": "place-order", "to": "order-placed", "kind": "emits" }
  ],
  "candidates": [
    { "id": "ordering", "kind": "workflow-boundary", "label": "Ordering",
      "rationale": "Everything before payment is one conversation.", "members": ["order-placed"] }
  ]
}
```

| Collection | Field | Required | Notes |
|---|---|---|---|
| `meta` | `project`, `generatedBy`, `date`, `revision` | yes | As the atlas models. `generatedBy` is `andthen:architecture`. |
| `meta` | `level` | yes | Brandolini's level the session ran at. |
| `meta` | `scope` | yes | One line, the report's scope. |
| `meta` | `source` | yes | The PRD or intent path the session was driven from, or `brownfield`. |
| `lanes[]` | `id`, `label`, `order` | yes | Optional collection; a board may have one lane or none. |
| `stickies[]` | `id`, `kind`, `label`, `order` | yes | `kind` is one of `event`, `command`, `actor`, `policy`, `read-model`, `aggregate`, `external-system`, `hotspot`; `label` is the verbatim domain term; `order` is a column every lane shares. |
| `stickies[]` | `note`, `lane`, `pivotal`, `attachedTo`, `cluster` | no | `pivotal` cuts every lane at its column; `attachedTo` names the sticky the question hangs on; `cluster` names the candidate the sticky belongs to. |
| `flows[]` | `from`, `to`, `kind` | yes | `triggers`, `emits`, `handles`, `reads` – the command → aggregate → event → policy chains of Process Modeling and Design Level. |
| `candidates[]` | `id`, `kind`, `label`, `rationale`, `members` | yes | `subdomain`, `workflow-boundary`, or `aggregate`; `members` are sticky ids. |
| `candidates[]` | `invariants` | no | The rules that force their members into one transaction. |

**The level bounds the board.** Big Picture carries events, actors, external systems, and hotspots and harvests `subdomain` candidates; Process Modeling adds commands, policies, and read models and harvests `workflow-boundary`; Design Level adds aggregates and harvests `aggregate`. A sticky or candidate outside its level is a validation error, because the board would claim a depth the session never reached.

**Cross-field invariants.** Ids unique per collection; `lane`, `attachedTo`, `cluster`, `flows[].from`/`to`, and `members` resolve; `order` unique within a lane (stickies without a lane form their own); `pivotal` only on events; `attachedTo` only on hotspots; `invariants` only on aggregates.

## `context-map`

```jsonc
{
  "schemaVersion": "1",
  "kind": "context-map",
  "meta": {
    "project": "Acme Billing",
    "generatedBy": "andthen:architecture",
    "date": "2026-08-12",
    "revision": "a1b2c3d",
    "status": "target"                    // current | target | registered
  },
  "contexts": [
    { "id": "billing", "name": "Billing", "purpose": "Invoicing, dunning, reconciliation.",
      "subdomainType": "core", "codeLocation": "src/billing/", "team": "payments" }
  ],
  "relationships": [
    { "from": "billing", "to": "notifications", "pattern": "published-language",
      "direction": "upstream-downstream", "channel": "invoice events",
      "rationale": "Notifications consume the event contract Billing publishes." }
  ]
}
```

| Collection | Field | Required | Notes |
|---|---|---|---|
| `meta` | `project`, `generatedBy`, `date`, `revision` | yes | As the atlas models. |
| `meta` | `status` | yes | `current` and `target` are a run's report-side maps; `registered` is the accepted map the Context Map document records. |
| `contexts[]` | `id`, `name`, `purpose`, `subdomainType` | yes | `subdomainType` is `core`, `supporting`, or `generic`. |
| `contexts[]` | `codeLocation`, `team` | no | `codeLocation` is repo-relative. |
| `relationships[]` | `from`, `to`, `pattern`, `direction`, `rationale` | yes | `pattern` is one of the nine below; `direction` is `upstream-downstream` (`from` upstream of `to`) or `symmetric`. |
| `relationships[]` | `channel` | no | The integration channel, when the same pair has several. |

The nine patterns: `partnership`, `shared-kernel`, `customer-supplier`, `conformist`, `anticorruption-layer`, `open-host-service`, `published-language`, `separate-ways`, `big-ball-of-mud`.

**Cross-field invariants.** Ids unique; endpoints resolve; no self-relationship; the symmetric patterns (`partnership`, `shared-kernel`, `separate-ways`) carry `direction: "symmetric"`.

## Persistence

Boards are checked against their schema and this reference before writing and are never hand-edited. The event storm and the registered map are committed projections under the `Models` location.
