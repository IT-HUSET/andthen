# Plan/FIS Data Contract

This document is the **single canonical source** for the plan/FIS data contract. Skills reference this document; they do not restate the contract inline.

> Skills that reference this document: `ops`, `plan`, `spec`, `exec-spec`, `exec-plan`, `review`.


## FIS Mutability Contract

FIS spec content — Required Context, Success Criteria, Scenarios, Scope, Architecture Decision, Implementation Plan, Testing Strategy, and Validation — is read-only input to the `andthen:exec-spec` skill during execution.

The FIS itself is mutable only through the `andthen:ops` skill's `update-fis <path> <task_id|all>`, `update-fis <path> observations <markdown-body>`, and `update-fis <path> discovered-requirements <markdown-body>` forms. No other write path is sanctioned.

Discovered Requirements is the single sanctioned append-only channel for FIS-augmenting requirement discoveries during execution. Append the requirement before writing the test or code that depends on it.


## Story Catalog Columns

Every local `plan.md` and plan-issue Story Catalog table uses exactly these columns, in this order:

| Column | Type | Description |
|---|---|---|
| `ID` | String | Story identifier, e.g. `S01`. Uppercase `S` + two-digit zero-padded number. |
| `Name` | String | Short story name. |
| `Phase` | String | Phase name/number. |
| `Wave` | String | Wave assignment, e.g. `W1`. |
| `Dependencies` | String | Comma-separated story IDs from the same Story Catalog, or `-` if none. Prose is invalid. |
| `Parallel` | String | `Yes` / `No` / `[P]` — whether this story can run in parallel with wave siblings. |
| `Risk` | String | `Low` / `Medium` / `High`. |
| `Status` | String | Current state per the Status State Machine below. |
| `FIS` | String | Relative POSIX path to the story's FIS file, or an unset sentinel (see FIS-Unset Sentinel below). |


## Required Story Brief Labels

Each local `plan.md` story section and granular story issue body carries a compact story brief. The Story Catalog is the source of truth for status, FIS path, phase, wave, dependencies, parallelism, and risk.

- `**Scope**`
- `**Source refs**` — required for PRD-backed stories; omit only when `**Provenance**` explains why no PRD source exists.

Optional labels:

- `**Provenance**` — required only for stories with no direct PRD feature coverage.
- `**Asset refs**` — wireframes, ADRs, design-system references, or other upstream artifacts needed by the FIS author.
- `**Notes**` — only for load-bearing planning notes that do not belong in the Story Catalog or Dependency Graph.


## Dependency Cell Contract

`Dependencies` cells are machine-readable scheduler input. A valid Story Catalog value is exactly one of:

- `-` when the story has no dependencies
- One or more story IDs from the same Story Catalog, separated by commas, e.g. `S01` or `S01, S04`

Do not put prose, phase names, milestone gates, or "all previous work" summaries in dependency cells. A value such as `Blocks A-G complete` is parsed as a literal dependency ID by downstream schedulers and fails with an unknown-dependency error. Express broad sequencing through phase/wave assignment, the `## Dependency Graph` section, or concrete story IDs.


## Status State Machine

Story Catalog status values are:

`Pending → Spec Ready → Done`

`In Progress` belongs in the State document's Active Stories table, not in the Story Catalog. Forward transitions are skill-implicit per the write-authority table below. Backward transitions (`Done → Spec Ready`) are allowed only through explicit `andthen:ops update-plan` calls — never inferred.

### Write Authority

| Transition | Write authority |
|---|---|
| `Pending → Spec Ready` | `andthen:plan` Step 5 (after FIS lands); `andthen:spec` post-save action (plan-story input mode) |
| `Spec Ready → Done` | `andthen:exec-spec` Step 5b (Story Catalog `Status` column). The `In Progress` state, when needed, is represented only in the State document's Active Stories table. |
| Any backward transition | `andthen:ops update-plan` explicit call only |

`andthen:exec-plan` orchestrates but does not write `Status` directly — it delegates through `andthen:ops` for cross-story state and repair writes only.


## FIS-Unset Sentinel

A Story Catalog `FIS` cell value matching the following regex is classified as **unset**:

```
^\s*(-|–|—|TBD|N/A)?\s*$
```

(case-insensitive on the literal tokens `TBD` and `N/A`; applied to the normalized cell text)

This covers: ASCII hyphen `-` (U+002D), en-dash `–` (U+2013), em-dash `—` (U+2014, defensive for rich-text-editor paste), `TBD`, `N/A`, empty, and whitespace-only values.

A Story Catalog `FIS` cell with a path value that points at a **non-existent file** is also classified as unset (file-existence check required).


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
**Plan**: <relative-posix-path-from-project-root-to-plan.md>
**Story-ID**: <ID>
```

- Path: POSIX forward slashes; no leading `./`; no trailing slash
- `Story-ID`: uppercase `S` prefix + two-digit zero-padded number (e.g. `S03`)
- No `**Status**:` field in the FIS header — Status is Story Catalog-only to avoid a second source of truth
