# The Plan Schema

`plan.json` is authoritative plan-bundle state: durable intent, dependency edges, and minimal resumable execution state. It and its FIS files are scoped to the plan's branch.

**Shipping.** The plan's branch is ready once every story is `done` or `skipped` (cut from scope), and its plan-level review over the `done` stories leaves no CRITICAL or HIGH finding open and no load-bearing check failing. A `DEFERRED` finding is still open: a deferral names a blocker, it does not accept the risk.

**Machine form.** `plan.schema.json` (JSON Schema draft 2020-12) owns the shape invariants. The skill that authors a plan checks its candidate against it before writing.

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
      "status": "pending",
      "fis": "s01-foundation.md",
      "completedTaskIds": [],
      "scope": "Establish the shared contract.",
      "sourceRefs": ["docs/prd.md#foundation"],
      "provenance": null,
      "assetRefs": [],
      "sequencing": null
    }
  ]
}
```

A story `id` is unique within the plan; JSON Schema cannot state it.

The fields whose *meaning* prose has to state:

| Field | Contract |
|---|---|
| `prd` | Repo-root-relative path of the `prd.md` or requirements file the plan came from (a PRD copied from a tracker item too), else `null`: a description, an intent doc, a bare tracker item. |
| `fis` | Canonical `sNN-<slug>.md` basename beside the plan, or `null`; `done` requires a non-null FIS. |
| `completedTaskIds` | Unique task IDs naming tasks of the FIS `fis` points at: empty while `fis` is `null`, and cleared when that pointer changes. |
| `verified` | `{at, summary}`, written with `done` and never without it; `at` a UTC ISO-8601 minute. |
| `provenance` | Why no `sourceRefs` entry covers the story, or `null`. |
| `sequencing` | Residual dependency rationale, or `null`. |

## FIS identity

A plan story's FIS sits beside the plan as `s{NN}-{name}.md` (`s01-user-auth.md`):

- `NN` is the zero-padded story number (`01`, never `1`);
- `{name}` is a kebab-case slug of the story name – lowercase, alphanumerics and ASCII hyphen, whitespace collapsed, no leading or trailing hyphen.

A pointer is accepted only in that exact form, derived from the story ID and name, with no directory component, and resolving to a regular file.

The FIS records its plan and story between its H1 and `## Feature Overview and Goal`:

```
**Plan**: <relative-posix-path-from-project-root-to-plan.json>
**Story-ID**: <ID>
```

The path is repo-root-relative POSIX, with no leading `./` or trailing slash, resolved from the project root holding the FIS and never from a working directory. `Story-ID` is uppercase `S` plus two digits (`S03`).

## State writers

`andthen:plan` owns durable planning fields and initializes new stories to `pending`, `fis: null`, and `completedTaskIds: []`.

Runtime state is `status`, `verified`, `fis`, and `completedTaskIds`. **The session executing a story writes its row** – a direct `andthen:exec-plan` run, or the story subagent a plan run dispatched. A plan run writes only under `--worktree`: the batch's rows as `in-progress`, committed before the batch branches, while no story copy exists yet. Authoring keeps one writer: the `andthen:plan` breakdown session writes the plan, and its story subagents report and never write it. Never put two writers on one copy of the file at once: racing writers lose a row.

Statuses: `pending` until execution starts, with `fis` recording whether the FIS exists; `in-progress` once execution starts, and still after a failure, which lives in the run report; `done`, written with `verified`; `skipped`, set only by hand. `done` and `skipped` are terminal for execution.

## Execution semantics

A story is dependency-ready when it is `pending` with a FIS, or `in-progress`, and every `dependsOn` story is `done`. A `skipped` dependency blocks its dependents, since it was never built and their FIS presumes its code.

An older plan runs as it stands: `spec-ready` and `blocked` read as `pending`, and a field this schema lacks, such as `owner`, is ignored. A story with any other status stays unstarted, and the run report names it.

`verified.summary` is one line quoted from executed output: the proof command, its exit status, and the runner's own result line (`{cmd} -> exit=0, Ran 4 tests, OK`). An exit code alone records that something ran, not what it found, and "looks right" is never a verification.

## Canonical serialization

- UTF-8 JSON, two-space indentation, one trailing newline.
- Keys in the example's order, `verified` after `completedTaskIds`.
- Preserve story and dependency source order, and completed tasks in the FIS's declared order.
- Path-valued fields are repo-root-relative POSIX strings; no absolute paths, backslashes, dot/dot-dot components, or containment escapes. A `sourceRefs` entry is such a path with an optional `#anchor`, or – for a tracker-sourced plan – the item's URL.
