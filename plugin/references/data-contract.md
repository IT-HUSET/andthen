# Plan/FIS Data Contract

**Single canonical source** for the FIS data contract and the markdown shape used in GitHub plan-issue bodies. The local plan format lives in [`plan-schema.md`](plan-schema.md); this document defers there for `plan.json` shapes and covers the markdown table only as GitHub transport.

> Skills that reference this document: `ops`, `plan`, `spec`, `exec-spec`, `exec-plan`, `review`.

## Contents

- FIS Mutability Contract – read-only execution input + sanctioned write paths via `andthen:ops`
- Plan Schema – pointer to `plan-schema.md`
- Plan Issue Catalog (markdown) – column-to-JSON-field mapping for `--to-issue` / `--from-issue`
- FIS-Unset Sentinel (markdown only) – regex for `FIS` cell `null` rendering
- FIS Structural Integrity Contract – the two gate conditions before `exec-spec` destructive work
- FIS Filename Convention – `s{NN}-{name}.md` rules
- FIS Provenance Fields – the `**Plan**:` / `**Story-ID**:` header pair


## FIS Mutability Contract

All FIS spec content – every H2 from `## Feature Overview and Goal` through `## Final Validation Checklist` – is read-only input to `andthen:exec-spec` during execution. Sections that ship empty in the typical case (Technical Overview, Testing Strategy, Validation, Execution Contract, Final Validation Checklist) are still read; empty body means "standard handling applies" per the section's own prompt. Required/Deeper Context are content-conditional: inlined when upstream sources exist, omitted otherwise.

The FIS itself is mutable only through `andthen:ops`'s `update-fis <path> <task_id|all>`, `update-fis <path> observations <markdown-body>`, and `update-fis <path> discovered-requirements <markdown-body>` forms. No other write path is sanctioned.

Discovered Requirements is the single sanctioned append-only channel for FIS-augmenting requirement discoveries during execution. Append the requirement before writing the test or code that depends on it.


## Plan Schema

Local plans are JSON. Canonical schema at [`plan-schema.md`](plan-schema.md): top-level fields, `stories[]` shape, status enum, writability, file-location. Not restated here.


## Plan Issue Catalog (markdown)

The GitHub-issue body (`andthen:plan --to-issue`, parsed by `andthen:exec-plan --from-issue` to materialize a local `plan.json`) carries a markdown Story Catalog table. Columns, in order:

| Column | Maps to JSON field | Description |
|---|---|---|
| `ID` | `id` | Story identifier, e.g. `S01`. Uppercase `S` + two-digit zero-padded number. |
| `Name` | `name` | Short story name. |
| `Phase` | `phase` | Phase id matching `overview.phases[].id`. |
| `Wave` | `wave` | Wave id (e.g. `W1`). |
| `Dependencies` | `dependsOn` | Comma-separated story IDs from the same catalog, or `-`. Prose is invalid. |
| `Parallel` | `parallel` | `Yes` / `No` / `[P]` – renders the boolean. |
| `Risk` | `risk` | `Low` / `Medium` / `High` (capitalized in markdown; lowercase in JSON). |
| `Status` | `status` | Capitalized form of the schema enum (see below). |
| `FIS` | `fis` | Relative POSIX path, or `-` when `null`. |

Status mapping: `Pending` ↔ `pending`, `Spec Ready` ↔ `spec-ready`, `In Progress` ↔ `in-progress`, `Done` ↔ `done`, `Skipped` ↔ `skipped`, `Blocked` ↔ `blocked`. JSON enum is canonical; capitalized form is markdown-only.

Story brief fields (`### Story S0N: <name>` per story) carry the same content as JSON brief fields:

- `**Scope**` ↔ `scope`
- `**Source refs**` ↔ `sourceRefs`
- `**Provenance**` ↔ `provenance`
- `**Asset refs**` ↔ `assetRefs`
- `**Notes**` ↔ `notes`

The 1:1 story↔FIS invariant and the `dependsOn` machine-readable contract apply to both markdown cells and JSON fields. Prose dependencies (`Blocks A-G complete`) are rejected.


## FIS-Unset Sentinel (markdown rendering only)

In the markdown issue catalog, a `FIS` cell matching this regex renders JSON `null`:

```
^\s*(-|–|–|TBD|N/A)?\s*$
```

(case-insensitive on `TBD` / `N/A`; applied to normalized cell text)

Covers: ASCII hyphen `-` (U+002D), en-dash `–` (U+2013), em-dash `–` (U+2014, defensive for rich-text paste), `TBD`, `N/A`, empty, whitespace. JSON uses `null` directly – the sentinel is markdown-parse only.


## FIS Structural Integrity Contract

Before destructive work, `exec-spec` Step 2 verifies the FIS is structurally well-formed. Two required conditions:

1. **`## Acceptance Scenarios` heading exists** – matched by `^## Acceptance Scenarios` – and its span (heading line through the next `^## ` heading or EOF) contains at least one `- [ ] ` checkbox line.
2. **`## Implementation Plan` heading exists** – matched by `^## Implementation Plan` – and its span contains at least one task with a Verify line (matched by `Verify:` or `**Verify**:` anywhere in the span).

Failure on any condition: emit `BLOCKED: <fis-path> missing: <comma-separated section list>` (list names only `## Acceptance Scenarios` and/or `## Implementation Plan`) and exit before Step 3. Do not enter Step 3 on a failed structural check.

> FIS lacking `## Acceptance Scenarios` (typically older files carrying `## Success Criteria`) fail this check intentionally; the `BLOCKED:` message instructs the user to re-spec. `## Final Validation Checklist` ships visible-empty in the template and is not gated by this contract – authors may also omit the heading when no feature-specific final gates apply.


## FIS Filename Convention

FIS files for plan stories:

```
s{NN}-{name}.md
```

- `NN` – two-digit zero-padded story number (`01`, `03`, never `1` / `3`)
- `{name}` – kebab-case slug: lowercase, alphanumerics + ASCII hyphen, punctuation dropped, whitespace runs collapsed to single hyphen, leading/trailing hyphens trimmed

Examples: `s01-user-auth.md`, `s03-exec-plan-tightening.md`


## FIS Provenance Fields

Every plan-story FIS carries provenance fields between the H1 and `## Feature Overview and Goal`:

```
**Plan**: <relative-posix-path-from-project-root-to-plan.json>
**Story-ID**: <ID>
```

- Path: POSIX forward slashes; no leading `./`; no trailing slash. GitHub-issue-sourced plans use `github://issue/<plan-N>` (durable contract); execution drives off the local materialized ledger.
- `Story-ID`: uppercase `S` + two-digit zero-padded number (`S03`).
- No `**Status**:` field – `status` is `plan.json`-only to avoid a second source of truth.
