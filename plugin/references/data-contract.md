# Plan/FIS Data Contract

This document is the **single canonical source** for the plan/FIS data contract. Skills reference this document; they do not restate the contract inline.

> Skills that reference this document: `ops`, `exec-spec`, `exec-plan`.


## FIS Mutability Contract

FIS spec content — Required Context, Success Criteria, Scenarios, Scope, Architecture Decision, Implementation Plan, Testing Strategy, and Validation — is read-only input to the `andthen:exec-spec` skill during execution.

The FIS itself is mutable only through the `andthen:ops` skill's `update-fis <path> <task_id|all>`, `update-fis <path> observations <markdown-body>`, and `update-fis <path> discovered-requirements <markdown-body>` forms. No other write path is sanctioned.

Discovered Requirements is the single sanctioned append-only channel for FIS-augmenting requirement discoveries during execution. Append the requirement before writing the test or code that depends on it.


## Story Catalog Columns

Every `plan.md` Story Catalog table uses exactly these columns, in this order:

| Column | Type | Description |
|---|---|---|
| `ID` | String | Story identifier, e.g. `S01`. Uppercase `S` + two-digit zero-padded number. |
| `Name` | String | Short story name. |
| `Phase` | String | Phase name/number. |
| `Wave` | String | Wave assignment, e.g. `W1`. |
| `Dependencies` | String | Comma-separated story IDs, or `-` if none. |
| `Parallel` | String | `Yes` / `No` / `[P]` — whether this story can run in parallel with wave siblings. |
| `Risk` | String | `Low` / `Medium` / `High`. |
| `Status` | String | Current state per the Status State Machine below. |
| `FIS` | String | Relative POSIX path to the story's FIS file, or an unset sentinel (see FIS-Unset Sentinel below). |


## Required Story Metadata Labels

Each story section in `plan.md` carries these fields (bold-label format):

- `**Status**`
- `**FIS**`
- `**Phase**`
- `**Wave**`
- `**Dependencies**`
- `**Parallel**`
- `**Risk**`
- `**Scope**`
- `**Acceptance Criteria**`


## Status State Machine

`Pending → Spec Ready → In Progress → Done`

Forward transitions are skill-implicit per the write-authority table below. Backward transitions (`Done → In Progress`, `In Progress → Spec Ready`) are allowed only through explicit `andthen:ops update-plan` calls — never inferred.

### Write Authority

| Transition | Write authority |
|---|---|
| `Pending → Spec Ready` | `andthen:plan` Step 6 (after FIS lands); `andthen:spec` post-save action (plan-story input mode) |
| `Spec Ready → In Progress` | `andthen:exec-spec` Step 2 — marks story active in the State document (Active Stories table). The plan row `**Status**` field is **not** written to `In Progress`; it advances directly to `Done` in Step 5b. |
| `In Progress → Done` | `andthen:exec-spec` Step 5b (plan row `**Status**` field + Story Catalog row) |
| Any backward transition | `andthen:ops update-plan` explicit call only |

`andthen:exec-plan` orchestrates but does not write `Status` directly — it delegates through `andthen:ops` for cross-story state and repair writes only.


## FIS-Unset Sentinel

A `**FIS**:` field value matching the following regex is classified as **unset**:

```
^\s*(-|–|—|TBD|N/A)?\s*$
```

(case-insensitive on the literal tokens `TBD` and `N/A`; applied to the span after `**FIS**:` on the row)

This covers: ASCII hyphen `-` (U+002D), en-dash `–` (U+2013), em-dash `—` (U+2014, defensive for rich-text-editor paste), `TBD`, `N/A`, empty, and whitespace-only values.

A `**FIS**:` field with a path value that points at a **non-existent file** is also classified as unset (file-existence check required).


## FIS Structural Integrity Contract

Before executing destructive work, `exec-spec` Step 2 verifies the FIS is structurally well-formed. The three required conditions:

1. **`## Success Criteria` heading exists** — matched by `^## Success Criteria` — and its span (heading line through the next `^## ` heading or EOF) contains at least one `- [ ] ` checkbox line.
2. **`## Implementation Plan` heading exists** — matched by `^## Implementation Plan` — and its span contains at least one task with a Verify line (matched by `Verify:` or `**Verify**:` anywhere in the span).
3. **`## Final Validation Checklist` heading exists** — presence-only check; matched by `^## Final Validation Checklist`.

Failure on any condition: emit `BLOCKED: <fis-path> missing: <comma-separated section list>` and exit before Step 3. Do not enter Step 3 on a failed structural check.

> **Pre-0.14.x FIS** (no Required/Deeper Context sections, no provenance fields): these FIS will fail the structural integrity check because they lack the required section headings. The failure is intentional — pre-0.14.x FIS require re-spec. The `BLOCKED:` message directs the user to re-spec.


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
- No `**Status**:` field in the FIS header — Status is plan-row-only to avoid a second source of truth
