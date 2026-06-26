# `plan.json` Schema

Canonical schema for the local `plan.json` written by the `andthen:plan` skill and read by the `andthen:exec-plan`, `andthen:ops`, and `andthen:review --mode gap` skills. Inlined into `plan`, `exec-plan`, `ops`, `review`; `now-what` detects `plan.json` artifact presence but does not consume this schema reference. The plan is data, not prose: the PRD carries narrative, the plan is a typed manifest of stories, dependencies, and runtime state.

**Single source of truth.** Updates to top-level fields, sub-object shapes, status enum, writability, file location, formatting, migration, or the canonical example MUST land here – not in `data-contract.md` (which defers here) and not duplicated into skill prompts. Drift across consumers is a maintenance bug.

> **Why JSON, not markdown?** Frontier models edit markdown more freely than JSON – markdown invites "rephrasing", JSON does not. The Story Catalog contract (closed status enum, machine-readable dependencies, unique FIS paths) is data wearing a markdown costume; this schema makes the typing explicit and removes the regex parser.

GitHub-issue mode (`--to-issue` / `--from-issue`) uses the **markdown** body shape from [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md) – JSON is the local runtime state; markdown is the GitHub transport. `--from-issue` materializes a local `plan.json` from the issue body once, then drives execution from it; the `andthen:exec-plan` skill owns the detailed from-issue flow.

## Contents

- Document shape – top-level fields, `overview`, `sharedDecisions[]`, `bindingConstraints[]`, `stories[]`, `riskSummary[]`
- Status enum (closed) – the six valid `status` values
- Writability rules – which fields each skill may write; the Preservation predicate
- File location – where `plan.json` lives relative to `prd.md`
- Formatting conventions – indent, key order, POSIX paths
- Migration from legacy `plan.md`
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
| `references` | array of strings | no | Free-form upstream-artifact references (ADRs, design system, wireframes, glossary, research). `[]` when none. |
| `overview` | object | yes | See below. |
| `sharedDecisions` | array of objects | no | Inter-story interface contracts. `[]` when none. |
| `bindingConstraints` | array of objects | no | Verbatim PRD spans that flow unchanged into FIS Required Context. `[]` when none. |
| `stories` | array of objects | yes | The Story Catalog. Order is human reading order; consumers MUST look up by `id`, never by array index. |
| `riskSummary` | array of objects | no | Structured replacement for the legacy `## Risk Summary` table. `[]` when none. |
| `executionNotes` | string | no | Short narrative on how to run the plan. Replaces legacy `## Execution Guide`. `""` when none. |

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
| `dependsOn` | array of strings | yes | Story IDs from this catalog. `[]` when none. **Prose is invalid.** |
| `parallel` | boolean | yes | `true` when the story can run in parallel with wave siblings. |
| `risk` | string | yes | One of `"low"`, `"medium"`, `"high"`. |
| `status` | string | yes | See **Status enum** below. |
| `fis` | string or null | yes | Relative POSIX path, or `null` when not yet generated. Unique across stories **for non-null values** (1:1 story↔FIS invariant); multiple pending stories sharing `null` is valid pre-generation. |
| `owner` | string or null | no | Coordination field: who is executing the story (name or forge handle), or `null`/absent when unclaimed. Advisory, not a lock – makes "who's on what" visible so teammates don't collide. Must not contain `|`/newlines or equal a FIS-Unset Sentinel form (per `data-contract.md`) – such values break the issue round-trip. Solo plans leave it `null`. Legacy plans without the key are valid; regeneration writes `null` when unset. |
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
| `spec-ready` | `andthen:spec` after FIS write (withheld on a blocking self-review Note) | FIS file exists; ready to execute. |
| `in-progress` | Explicit `andthen:ops update-plan <id> in-progress` (or future exec-spec entry hook) | Exec started; dependents must wait. Available for orchestrators that want explicit in-flight signaling; the bundled exec-spec flow transitions `spec-ready → done` directly. |
| `done` | `andthen:exec-spec` after Acceptance Scenarios and Structural Criteria pass (via `andthen:ops`) | Story complete. |
| `skipped` | Dependency containment or explicit `andthen:ops update-plan` | Story not attempted because an upstream dependency failed, or explicitly marked skipped by an orchestrator/user. |
| `blocked` | Explicit `andthen:ops update-plan <id> blocked` | Manual block; consumers skip and warn. |

Forward transitions are skill-implicit per the write-authority table below. Backward transitions require explicit `andthen:ops update-plan` calls. Unknown values rejected at write time.

**Governing plan**: a plan *governs* current work while it has any undone story (`status` not `done`/`skipped`); all-done/skipped bundles are inert history. Consumers that resolve "the governing plan(s)" – state derivation, active-story routing, report placement – use this predicate.


## Writability rules

A plan in flight is **runtime state** – the agent re-reads it at session start to resume. Only state-tracking fields (`stories[].status`, `stories[].fis`, `stories[].owner`) are mutable in flight, only via `andthen:ops`. Other skills (`exec-spec`, `exec-plan`, `review`, `quick-review`, `remediate-findings`, `now-what`) **must not** write to `plan.json`.

| Field | Initial writer | Subsequent mutator |
|---|---|---|
| `schemaVersion`, `prd`, `references`, `overview`, `sharedDecisions`, `bindingConstraints`, story `id`/`name`/`phase`/`wave`/`dependsOn`/`parallel`/`risk`/`scope`/`sourceRefs`/`provenance`/`assetRefs`/`notes`, `riskSummary`, `executionNotes` | `andthen:plan` (initial creation) | `andthen:plan` rerun – full regeneration that **preserves** existing `status`/`fis`/`owner` per the predicate below |
| `stories[].status` | `andthen:plan` (`"pending"`) | `andthen:ops update-plan <plan> <id> <status>` |
| `stories[].fis` | `andthen:plan` after FIS write (or `null`) | `andthen:ops update-plan-fis <plan> <id> <fis-path>` |
| `stories[].owner` | `andthen:plan` (`null`) | `andthen:ops update-plan-owner <plan> <id> <owner>` (pass `-` to clear) |

**Preservation predicate** (full regeneration): a story's existing `status`, `fis`, and `owner` are preserved only when ALL hold – `id` survives regeneration; `scope` string-equal; `sourceRefs` set-equal; `assetRefs` set-equal; `provenance` string-equal; the preserved `fis` path still resolves. Content-equality (not name) is the load-bearing guard: a same-id story whose content-defining fields drifted would otherwise graft a stale FIS onto new content. Stories failing any clause reset to `status: "pending"`, `fis: null`, `owner: null`. `owner` is coordination state, not PRD-derived, so a content-stable story keeps its claim across a local `andthen:plan` regeneration; `--from-issue` reruns instead refresh `owner` from the issue's Owner cell.

Exception: `andthen:exec-plan --from-issue` reconciliation rewrites `.agent_temp/from-issue-<N>/plan.json` as a full regeneration.

User-initiated hand edits to `plan.json` are allowed and trusted – the contract guards agent behavior, not tampering. If a user edits the file, they own the consequences. Pre-existing legacy `metadata` blocks (e.g. `immutableDigest`) are ignored on read and dropped on the next regeneration.

> **Concurrency**: single-writer assumption. Concurrent `andthen:ops` calls last-writer-wins silently. Do not run concurrent orchestrators against the same file.


## File location

`plan.json` lives next to `prd.md` and the per-story FIS files, per the project's **Project Document Index** `Specs & Plans` row (typical: `docs/specs/<version-or-feature>/plan.json`).

When `--from-issue <N>` is set, `andthen:exec-plan` materializes a per-issue `plan.json` at `.agent_temp/from-issue-<N>/plan.json`. Path is stable across reruns to support resume.


## Formatting conventions

- **Indent**: 2 spaces.
- **Key order**: schema-document order for every schema-defined object shape: top-level (`schemaVersion`, `prd`, `references`, `overview`, `sharedDecisions`, `bindingConstraints`, `stories`, `riskSummary`, `executionNotes`); `overview` (`summary`, `phases`); `overview.phases[]` (`id`, `name`, `waves`); `sharedDecisions[]` (`title`, `description`, `stories`); `bindingConstraints[]` (`featureId`, `anchor`, `verbatim`); story object (`id`, `name`, `phase`, `wave`, `dependsOn`, `parallel`, `risk`, `status`, `fis`, `owner`, `scope`, `sourceRefs`, `provenance`, `assetRefs`, `notes`); `riskSummary[]` (`story`, `risk`, `mitigation`).
- **Trailing newline** at EOF.
- **Sorted-by-schema** writes – diffs reflect *content*, not *ordering* drift.


## Migration from legacy `plan.md`

When `andthen:plan` reruns in a directory with a legacy `plan.md` but no `plan.json`, it parses the markdown Story Catalog, maps each row into `stories[]`, and writes `plan.json`. Six legacy statuses round-trip:

| Legacy `plan.md` status | `plan.json` status |
|---|---|
| `Pending` | `pending` |
| `Spec Ready` | `spec-ready` |
| `In Progress` | `in-progress` |
| `Done` | `done` |
| `Skipped` | `skipped` |
| `Blocked` | `blocked` |

Unrecognized legacy values (e.g. `Retired`) map to `skipped` with a one-line annotation appended to `executionNotes` describing the rename – durable audit trail, not removed on subsequent reruns.

Stories whose legacy `FIS` cell pointed at an existing file preserve path and status and **skip FIS regeneration**. Stories with sentinel or missing FIS paths get `fis: null`, `status: "pending"`, and FIS generation runs as in a fresh plan. The legacy `plan.md` is left in place for the user to delete; downstream consumers ignore it.


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
      "owner": null,
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
      "owner": null,
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
