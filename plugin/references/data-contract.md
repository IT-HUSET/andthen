# Plan/FIS Data Contract

This document is the **single canonical source** for the FIS data contract and for the markdown shape used in GitHub plan-issue bodies. The structured local plan format lives in [`plan-schema.md`](plan-schema.md); this document defers to it for `plan.json` field shapes and references the markdown table only as the GitHub-issue transport.

> Skills that reference this document: `ops`, `plan`, `spec`, `exec-spec`, `exec-plan`, `review`.


## FIS Mutability Contract

FIS spec content — Required Context, Success Criteria, Scenarios, Scope, Architecture Decision, Implementation Plan, Testing Strategy, and Validation — is read-only input to the `andthen:exec-spec` skill during execution.

The FIS itself is mutable only through the `andthen:ops` skill's `update-fis <path> <task_id|all>`, `update-fis <path> observations <markdown-body>`, and `update-fis <path> discovered-requirements <markdown-body>` forms. No other write path is sanctioned.

Discovered Requirements is the single sanctioned append-only channel for FIS-augmenting requirement discoveries during execution. Append the requirement before writing the test or code that depends on it.


## Plan Schema

Local plans are JSON. The schema is canonical at [`plan-schema.md`](plan-schema.md): top-level fields, `stories[]` shape, status enum, writability rules, and file-location conventions live there. This document does not restate them.


## Plan Issue Catalog (markdown)

The GitHub-issue body shape (`andthen:plan --to-issue` output, parsed by `andthen:exec-plan --from-issue` to materialize a local `plan.json` ledger) carries a markdown Story Catalog table. Columns, in this order:

| Column | Maps to JSON field | Description |
|---|---|---|
| `ID` | `id` | Story identifier, e.g. `S01`. Uppercase `S` + two-digit zero-padded number. |
| `Name` | `name` | Short story name. |
| `Phase` | `phase` | Phase id matching `overview.phases[].id`. |
| `Wave` | `wave` | Wave id (e.g. `W1`). |
| `Dependencies` | `dependsOn` | Comma-separated story IDs from the same catalog, or `-` if none. Prose is invalid. |
| `Parallel` | `parallel` | `Yes` / `No` / `[P]` — renders the boolean. |
| `Risk` | `risk` | `Low` / `Medium` / `High` (capitalized in markdown; lowercase in JSON). |
| `Status` | `status` | Capitalized form of the schema enum (see mapping below). |
| `FIS` | `fis` | Relative POSIX path, or `-` when `null`. |

Status mapping between markdown rendering and the JSON enum: `Pending` ↔ `pending`, `Spec Ready` ↔ `spec-ready`, `In Progress` ↔ `in-progress`, `Done` ↔ `done`, `Skipped` ↔ `skipped`, `Blocked` ↔ `blocked`. The JSON enum is canonical; the capitalized form is markdown-only.

Story brief fields in the issue body (`### Story S0N: <name>` per story) carry the same content as the JSON story brief fields:

- `**Scope**` ↔ `scope`
- `**Source refs**` ↔ `sourceRefs`
- `**Provenance**` ↔ `provenance`
- `**Asset refs**` ↔ `assetRefs`
- `**Notes**` ↔ `notes`

The 1:1 story↔FIS invariant and the `dependsOn` machine-readable contract apply to both the markdown table cells and the JSON fields. Prose dependencies (`Blocks A-G complete`) are rejected.


## FIS-Unset Sentinel (markdown rendering only)

In the markdown issue catalog, a `FIS` cell value matching the following regex renders the JSON `null`:

```
^\s*(-|–|—|TBD|N/A)?\s*$
```

(case-insensitive on the literal tokens `TBD` and `N/A`; applied to the normalized cell text)

This covers: ASCII hyphen `-` (U+002D), en-dash `–` (U+2013), em-dash `—` (U+2014, defensive for rich-text-editor paste), `TBD`, `N/A`, empty, and whitespace-only values. JSON sources use `null` directly — the sentinel is only relevant when parsing markdown issue bodies.


## FIS Structural Integrity Contract

Before executing destructive work, `exec-spec` Step 2 verifies the FIS is structurally well-formed. The three required conditions:

1. **`## Success Criteria` heading exists** — matched by `^## Success Criteria` — and its span (heading line through the next `^## ` heading or EOF) contains at least one `- [ ] ` checkbox line.
2. **`## Implementation Plan` heading exists** — matched by `^## Implementation Plan` — and its span contains at least one task with a Verify line (matched by `Verify:` or `**Verify**:` anywhere in the span).
3. **`## Final Validation Checklist` heading exists** — presence-only check; matched by `^## Final Validation Checklist`.

Failure on any condition: emit `BLOCKED: <fis-path> missing: <comma-separated section list>` and exit before Step 3. Do not enter Step 3 on a failed structural check.

> Older FIS files lacking the required structural sections (Success Criteria, Implementation Plan, Final Validation Checklist) fail this check intentionally. The `BLOCKED:` message instructs the user to re-spec.


## FIS Filename Convention

FIS files produced for plan stories use:

```
s{NN}-{name}.md
```

- `NN` — two-digit zero-padded story number (e.g. `01`, `03`, never `1` or `3`)
- `{name}` — kebab-case slug derived from the story name: lowercase, alphanumerics + ASCII hyphen, punctuation dropped, whitespace runs collapsed to a single hyphen, leading/trailing hyphens trimmed

Examples: `s01-user-auth.md`, `s03-exec-plan-tightening.md`


## FIS Provenance Fields

Every FIS produced for a plan story carries provenance fields between the H1 heading and `## Feature Overview and Goal`:

```
**Plan**: <relative-posix-path-from-project-root-to-plan.json>
**Story-ID**: <ID>
```

- Path: POSIX forward slashes; no leading `./`; no trailing slash. For GitHub-issue-sourced plans, the value is `github://issue/<plan-N>` (the durable contract) — execution still drives off the local materialized ledger.
- `Story-ID`: uppercase `S` prefix + two-digit zero-padded number (e.g. `S03`)
- No `**Status**:` field in the FIS header — `status` is `plan.json`-only to avoid a second source of truth.
