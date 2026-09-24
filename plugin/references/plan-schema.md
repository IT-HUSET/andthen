# The Plan Schema

`plan.json` is authoritative plan-bundle state: durable intent, dependency edges, and minimal resumable execution state. Phases, batches, parallel flags, and risk labels are derived views, not persisted facts.

**Machine form.** `plan.schema.json` (JSON Schema draft 2020-12) owns shape invariants; the skill that authors or regenerates a plan checks its candidate against it before writing. It opens no FIS – task ids, provenance, and proofs are the executing agent's read. `schemaVersion` bumps only on a breaking delta.

## Document Shape

```json
{
  "schemaVersion": "2",
  "prd": "docs/prd.md",
  "overview": { "summary": "Dependency-ordered delivery of the requested capability." },
  "sharedDecisions": [],
  "bindingConstraints": [],
  "stories": [
    {
      "id": "S01",
      "name": "Foundation",
      "dependsOn": [],
      "status": "spec-ready",
      "fis": "s01-foundation.md",
      "completedTaskIds": [],
      "owner": null,
      "scope": "Establish the shared contract.",
      "sourceRefs": ["docs/prd.md#foundation"],
      "provenance": "docs/plans/plan.json",
      "assetRefs": [],
      "sequencing": null
    }
  ]
}
```

A story `id` is unique within the plan – the lookup key every row write and dependency edge resolves through, which no JSON Schema expresses. The fields whose *meaning* prose has to state:

| Field | Contract |
|---|---|
| `prd` | Repo-root-relative path of the `prd.md` or requirements file the plan came from, or `null` when it came from anything else – a description, an intent doc, a tracker item. |
| `fis` | Canonical `sNN-<slug>.md` basename beside the plan, or `null`; `done` requires a non-null FIS, and a terminal row keeps the pointer it finished with. |
| `completedTaskIds` | Unique task IDs in the FIS's declared order, naming tasks of the FIS `fis` points at: empty while `fis` is `null`, and cleared when that pointer changes. |
| `verified` | `{at, summary}`, written with `done` and never without it: `at` a UTC ISO-8601 minute, `summary` one line on § Execution semantics' shape – the only trace of what ran once the bundle is deleted. |
| `owner` | The run session holding the story, or `null`; an `owner` on a row that is not `in-progress` is stale and free to take. |
| `scope` | Bounded implementation brief. |
| `provenance` | The plan path recorded in the FIS header. |
| `sequencing` | Residual dependency rationale, or `null`. |

## FIS identity

A plan story's FIS sits beside the plan as `s{NN}-{name}.md`: `NN` is the zero-padded story number (`01`, never `1`) and `{name}` is a kebab-case slug of the story name – lowercase, alphanumerics and ASCII hyphen, whitespace collapsed, no leading or trailing hyphen (`s01-user-auth.md`). A pointer is accepted only in that exact form, derived from the story ID and name, with no directory component and resolving to a regular file – a symlink would alias two stories onto one spec; the authoring skill requires matching provenance in the target before it writes.

That provenance sits between the FIS's H1 and `## Feature Overview and Goal`; a declaration elsewhere is malformed:

```
**Plan**: <relative-posix-path-from-project-root-to-plan.json>
**Story-ID**: <ID>
```

The path is repo-root-relative POSIX, no leading `./` or trailing slash, resolved from the project root holding the FIS and never from a working directory; `Story-ID` is uppercase `S` plus two digits (`S03`). There is no `**Status**:` field – `status` is `plan.json`-only, so no second source of truth exists.

## State ownership

`andthen:plan` owns durable planning fields and initializes new stories to `pending`, `fis: null`, `completedTaskIds: []`, and `owner: null`. Regeneration preserves that runtime state only when the story ID and normalized name still identify the same story and what it retains stays valid against the regenerated FIS.

Runtime state – `status`, `verified`, `fis`, `completedTaskIds`, `owner` – is edited in place per this schema by the skill that owns what it writes. **While a run is in flight there is exactly one writer**: the run session executing the bundle (the `andthen:exec-plan` or `andthen:exec-spec` skill). A story subagent never opens the file – it reports its state and the session writes the row. That is what makes parallel stories safe; two racing writers lose a row.

Status transitions: `pending` → `spec-ready` when the story has a FIS, `in-progress` at dispatch, then `done` or `skipped`, both terminal. A legacy `blocked` row reads as `spec-ready`.

## Execution semantics

A story is dependency-ready when its status is `spec-ready` or `in-progress` and every `dependsOn` story is `done`. A skipped or failed prerequisite contains its dependents rather than satisfying the edge.

`completedTaskIds` is the resume authority for what a re-run may skip. `verified.summary` is one line quoted from executed output – the proof command, its exit status, and the runner's own result line (`{cmd} -> exit=0, Ran 4 tests, OK`); an exit code alone records that something ran, not what it found, and "looks right" is never a verification.

## Canonical serialization

- UTF-8 JSON, two-space indentation, one trailing newline.
- Schema order: top level `schemaVersion`, `prd`, `overview`, `sharedDecisions`, `bindingConstraints`, `stories`; story `id`, `name`, `dependsOn`, `status`, `fis`, `completedTaskIds`, `verified`, `owner`, `scope`, `sourceRefs`, `provenance`, `assetRefs`, `sequencing`.
- Preserve story, dependency, and completed-task source order.
- Path-valued fields are repo-root-relative POSIX strings; no absolute paths, backslashes, dot/dot-dot components, or containment escapes. A `sourceRefs` entry is such a path with an optional `#anchor`, or – for a tracker-sourced plan – the item's URL.

## The one-story plan

Every FIS is a plan story, so a standalone feature gets a `plan.json` of its own beside it – written by `andthen:spec`, the one exception to `andthen:plan` owning plan authorship. One state shape means one reader and no second schema to keep aligned.

It carries `schemaVersion` `"2"`, `prd` the input PRD's path or `null`, an `overview` whose `summary` is the feature's one line, and a single story `S01`: `name` and `scope` from the feature, `dependsOn: []`, `completedTaskIds: []`, `fis` the canonical `s01-<slug>.md` basename, and `status` `spec-ready`.
