# `plan.json` Schema

Canonical schema for the local `plan.json` artifact written by `andthen:plan` and read by `andthen:exec-plan`, `andthen:ops`, `andthen:review --mode gap`, and `andthen:now-what`. The schema is inlined into the `plan`, `exec-plan`, `ops`, and `review` skill bundles (the writers, validators, and gap reviewer); `now-what` only checks file existence and deserializes without needing the schema reference. The plan is data, not prose: the PRD carries narrative, the plan is a typed manifest of stories, dependencies, and runtime state.

**Single source of truth.** This file is the authoritative definition. Updates to top-level fields, sub-object shapes, the status enum, writability rules, file location, formatting conventions, migration prose, or the canonical example MUST land here – not in `data-contract.md` (which defers to this file for plan-shape questions) and not duplicated into skill prompts (which reference this file). Drift across consumers is a maintenance bug, not a feature.

> **Why JSON, not markdown?** Frontier models edit markdown more freely than JSON – markdown invites "rephrasing", JSON does not. The Story Catalog contract (closed status enum, machine-readable dependencies, unique FIS paths) is data wearing a markdown costume; this schema makes the typing explicit and removes the regex parser.

GitHub-issue mode (`--to-issue` / `--from-issue`) uses the **markdown** body shape from [`plan-issue-shape.md`](plan-issue-shape.md) – JSON is the local runtime ledger; markdown is the GitHub transport. When `--from-issue` is set, `andthen:exec-plan` materializes a local `plan.json` from the issue body once, then drives execution from the local ledger. See [`from-issue-mode.md`](../skills/exec-plan/references/from-issue-mode.md).

## Contents

- Document shape – top-level fields, `overview`, `sharedDecisions[]`, `bindingConstraints[]`, `stories[]`, `riskSummary[]`
- Status enum (closed) – the six valid `status` values and their semantics
- Writability rules – which fields each skill may write; the Preservation predicate
- File location – where `plan.json` lives relative to `prd.md`
- Formatting conventions – indent, key order, POSIX paths
- Migration from legacy `plan.md` – one-shot migration semantics
- Example – canonical worked example


## Document shape

```jsonc
{
  "schemaVersion": "1",
  "prd": "prd.md",
  "references": [],
  "overview": {
    "summary": "1–3 short paragraphs",
    "phases": [
      { "id": "P1", "name": "Foundation", "waves": ["W1", "W2"] }
    ]
  },
  "sharedDecisions": [],
  "bindingConstraints": [],
  "stories": [],
  "riskSummary": [],
  "executionNotes": ""
}
```

### Top-level fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `schemaVersion` | string | yes | Currently `"1"`. Consumers MUST reject unknown versions with `BLOCKED: unsupported plan.json schemaVersion`. |
| `prd` | string | yes | Relative POSIX path (`docs/specs/feature/prd.md`) **or** `github://issue/<N>` for issue-sourced plans. |
| `references` | array of strings | no | Free-form upstream-artifact references (ADRs, design system, wireframes, glossary, ad-hoc research). Empty array when none. |
| `overview` | object | yes | See below. |
| `sharedDecisions` | array of objects | no | Inter-story interface contracts. Empty array when none apply. |
| `bindingConstraints` | array of objects | no | Verbatim PRD spans that must flow unchanged into FIS Required Context. Empty array when none apply. |
| `stories` | array of objects | yes | The Story Catalog. Order conveys human reading order; consumers MUST look up stories by `id`, never by array index. |
| `riskSummary` | array of objects | no | Structured replacement for the legacy `## Risk Summary` markdown table. Empty array when none. |
| `executionNotes` | string | no | Short narrative on how to run the plan. Replaces the legacy `## Execution Guide` prose section. Empty string when none. |

### `overview` object

| Field | Type | Required | Notes |
|---|---|---|---|
| `summary` | string | yes | 1–3 short paragraphs of plain prose. |
| `phases` | array of objects | yes | At least one. |

Each phase:

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | E.g. `"P1"`. Unique within `phases`. |
| `name` | string | yes | E.g. `"Foundation"`. |
| `waves` | array of strings | yes | Ordered wave identifiers used by stories in this phase, e.g. `["W1", "W2"]`. |

### `sharedDecisions[]` object

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | yes | Decision name. |
| `description` | string | yes | One-line description; reference producing and consuming stories by ID. |
| `stories` | array of strings | yes | Story IDs that produce or consume this decision. |

### `bindingConstraints[]` object

| Field | Type | Required | Notes |
|---|---|---|---|
| `featureId` | string | yes | PRD feature ID (e.g. `"FR-2"`). |
| `anchor` | string | yes | PRD heading anchor (e.g. `"prd.md#export-rules"`). |
| `verbatim` | string | yes | Verbatim PRD span – flows unchanged into FIS Required Context. |

### `stories[]` object – the Story Catalog

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | Pattern `S\d{2,}` (uppercase `S` + zero-padded number). Unique across `stories`. |
| `name` | string | yes | Short descriptive name. |
| `phase` | string | yes | Matches an `overview.phases[].id`. |
| `wave` | string | yes | Matches one of the waves listed for the story's phase. |
| `dependsOn` | array of strings | yes | Story IDs from this catalog. Empty array when no dependencies. **Prose is invalid.** |
| `parallel` | boolean | yes | `true` when the story can run in parallel with wave siblings. |
| `risk` | string | yes | One of `"low"`, `"medium"`, `"high"`. |
| `status` | string | yes | See **Status enum** below. |
| `fis` | string or null | yes | Relative POSIX path to the FIS file, or `null` when not yet generated. Unique across stories **only for non-null values** (1:1 story↔FIS invariant); multiple pending stories sharing `null` is valid before FIS generation. |
| `scope` | string | yes | One paragraph: outcome, inclusions, exclusions. No implementation approach. |
| `sourceRefs` | array of strings | no | PRD feature IDs and anchors. Required for PRD-backed stories. |
| `provenance` | string or null | no | Required only when no direct PRD coverage exists. |
| `assetRefs` | array of strings | no | Wireframes, ADRs, design-system references. |
| `notes` | string or null | no | Load-bearing planning notes that don't fit elsewhere. |

### `riskSummary[]` object

| Field | Type | Required | Notes |
|---|---|---|---|
| `story` | string | yes | Story ID. |
| `risk` | string | yes | `"low"` / `"medium"` / `"high"`. |
| `mitigation` | string | yes | Mitigation approach. |


## Status enum (closed)

| Value | Set by | Meaning |
|---|---|---|
| `pending` | `andthen:plan` (initial) | Story exists; FIS not yet generated. |
| `spec-ready` | `andthen:plan` after FIS write | FIS file exists; ready to be executed. |
| `in-progress` | Explicit `andthen:ops update-plan <id> in-progress` (or future exec-spec entry hook) | Exec started; dependents must wait. Available in the enum for orchestrators that want explicit in-flight signaling; the bundled exec-spec flow currently transitions `spec-ready → done` directly. |
| `done` | `andthen:exec-spec` after Acceptance Scenarios and Structural Criteria pass (via `andthen:ops`) | Story complete. |
| `skipped` | `andthen:exec-plan --auto` failure-containment path | Dependency-chain failed upstream; story not attempted. |
| `blocked` | Explicit `andthen:ops update-plan <id> blocked` | Manual block; consumers skip and warn. |

Forward transitions are skill-implicit per the write-authority table below. Backward transitions only via explicit `andthen:ops update-plan` calls. Unknown values are rejected at write time.


## Writability rules

A plan in flight is treated as a **runtime ledger** – the persistent state file the agent reads at session start to resume work. Only the **state-tracking fields** (`stories[].status`, `stories[].fis`) are mutable in flight, and the authorized path is `andthen:ops`. Other skills (`exec-spec`, `exec-plan`, `review`, `quick-review`, `remediate-findings`, `now-what`) **must not** write to `plan.json`.

| Field | Initial writer | Subsequent mutator |
|---|---|---|
| `schemaVersion`, `prd`, `references`, `overview`, `sharedDecisions`, `bindingConstraints`, story `id`/`name`/`phase`/`wave`/`dependsOn`/`parallel`/`risk`/`scope`/`sourceRefs`/`provenance`/`assetRefs`/`notes`, `riskSummary`, `executionNotes` | `andthen:plan` (initial creation) | `andthen:plan` rerun – full regeneration that **preserves** existing `status`/`fis` per the predicate below |
| `stories[].status` | `andthen:plan` (`"pending"`) | `andthen:ops update-plan <plan> <id> <status>` |
| `stories[].fis` | `andthen:plan` after FIS write (or `null`) | `andthen:ops update-plan-fis <plan> <id> <fis-path>` |

**Preservation predicate** (full regeneration): a story's existing `status` and `fis` are preserved only when ALL hold – `id` survives regeneration; `scope` is string-equal; `sourceRefs` is set-equal; `assetRefs` is set-equal; `provenance` is string-equal; the preserved `fis` path still resolves to an existing file. Content-equality (not name) is the load-bearing guard: a same-id story whose content-defining fields drifted would otherwise graft a stale FIS onto new content. Stories failing any clause reset to `status: "pending"`, `fis: null`.

Exception: `andthen:exec-plan --from-issue` reconciliation rewrites `.agent_temp/from-issue-<N>/plan.json` as a full regeneration – see [`from-issue-mode.md`](../skills/exec-plan/references/from-issue-mode.md).

User-initiated hand edits to `plan.json` are allowed and trusted – the contract is a guardrail for agent behavior, not a tamper-detection mechanism. If a user edits the file, they own the consequences. Pre-existing `metadata` blocks (legacy 0.19.x with `immutableDigest`) are ignored on read and dropped on the next regeneration.

> **Concurrency**: single-writer assumption. Concurrent `andthen:ops` calls on the same `plan.json` last-writer-wins silently. Do not run concurrent orchestrators against the same file.


## File location

`plan.json` lives next to `prd.md` and the per-story FIS files, per the project's **Project Document Index** `Specs & Plans` row (typical default: `docs/specs/<version-or-feature>/plan.json`).

When `--from-issue <N>` is set, `andthen:exec-plan` materializes a per-issue ledger at `.agent_temp/from-issue-<N>/plan.json`. Path is stable across reruns to support resume.


## Formatting conventions

- **Indent**: 2 spaces.
- **Key order**: schema-document order (top-level: `schemaVersion`, `prd`, `references`, `overview`, `sharedDecisions`, `bindingConstraints`, `stories`, `riskSummary`, `executionNotes`; story object: `id`, `name`, `phase`, `wave`, `dependsOn`, `parallel`, `risk`, `status`, `fis`, `scope`, `sourceRefs`, `provenance`, `assetRefs`, `notes`).
- **Trailing newline** at EOF.
- **Sorted-by-schema** writes mean diffs reflect *content* changes, not *ordering* drift – important for PR review.


## Migration from legacy `plan.md`

When `andthen:plan` is rerun in a directory that contains a legacy `plan.md` but no `plan.json`, it parses the markdown Story Catalog, maps each row into a `stories[]` entry, and writes `plan.json`. Map all six legacy statuses round-trip to their new enum equivalents:

| Legacy `plan.md` status | `plan.json` status |
|---|---|
| `Pending` | `pending` |
| `Spec Ready` | `spec-ready` |
| `In Progress` | `in-progress` |
| `Done` | `done` |
| `Skipped` | `skipped` |
| `Blocked` | `blocked` |

Any unrecognized legacy value (e.g. `Retired` from earlier enums) maps to `skipped` with a one-line annotation appended to `executionNotes` describing the rename. The annotation is intentionally durable – left in `executionNotes` as an audit trail of the migration, not removed on subsequent reruns.

For each migrated story whose `FIS` cell pointed at an existing file, the path and the migrated status are preserved and **FIS regeneration is skipped**. Stories with sentinel or missing FIS paths get `fis: null`, `status: "pending"`, and FIS generation runs as in a fresh plan. The legacy `plan.md` is left in place for the user to delete; downstream consumers ignore it.


## Example

A minimal valid `plan.json`:

```json
{
  "schemaVersion": "1",
  "prd": "prd.md",
  "references": [],
  "overview": {
    "summary": "Two-phase rollout: foundation slice followed by parallel feature work.",
    "phases": [
      { "id": "P1", "name": "Foundation", "waves": ["W1"] },
      { "id": "P2", "name": "Feature work", "waves": ["W2"] }
    ]
  },
  "sharedDecisions": [],
  "bindingConstraints": [],
  "stories": [
    {
      "id": "S01",
      "name": "Schema and migrations",
      "phase": "P1",
      "wave": "W1",
      "dependsOn": [],
      "parallel": false,
      "risk": "low",
      "status": "pending",
      "fis": null,
      "scope": "Establish the database schema and reversible migrations for the alerting subsystem.",
      "sourceRefs": ["FR-1", "prd.md#data-model"],
      "provenance": null,
      "assetRefs": [],
      "notes": null
    },
    {
      "id": "S02",
      "name": "Alert classifier",
      "phase": "P2",
      "wave": "W2",
      "dependsOn": ["S01"],
      "parallel": true,
      "risk": "medium",
      "status": "pending",
      "fis": null,
      "scope": "Classify incoming events into alert categories with thresholded confidence.",
      "sourceRefs": ["FR-2", "FR-3", "prd.md#classifier"],
      "provenance": null,
      "assetRefs": [],
      "notes": null
    }
  ],
  "riskSummary": [
    { "story": "S02", "risk": "medium", "mitigation": "Add property tests around classifier thresholds." }
  ],
  "executionNotes": "Run S01 to clean schema before parallelizing S02 against any sibling stories."
}
```
