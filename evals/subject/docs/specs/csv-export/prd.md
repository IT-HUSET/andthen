# Product Requirements Document: CSV Export

> **Source**: inline – the ledger owner's month-close request, 2026-04-09
> **Context**: `docs/PRODUCT.md` § Value Propositions, "A report in one command"
> **Related Assets**: ADR-001 (module layering)


## Executive Summary

- **Problem**: Every month close ends with the ledger owner reshaping the export by hand in a spreadsheet, and the shared folder holds only the latest month.
- **Vision**: A closed ledger leaves the tool as a file the rest of the company opens as-is, filed in the shared folder beside the earlier months.
- **Target Users**: the ledger owner; the analyst on a locked-down laptop.
- **Success Metrics**: months reshaped by hand – none; reports kept in the shared folder – one per closed month.

### Capabilities at a Glance
- **FR1: Export CSV** _(Must / P0)_ – records leave as a CSV report, header first, rows in a fixed order.
- **FR2: Report named after the ledger** _(Must / P0)_ – the report file carries its ledger's name, so a folder of months keeps every month.
- **FR3: Report inside the output directory** _(Must / P0)_ – the report lands under the directory the run names, created if needed.

### Scope Highlights
- **In scope**: CSV rendering, deterministic row order, ledger-derived report names, the output directory.
- **Out of scope**: a second output format, quoting or escaping, column selection, sending the report anywhere.
- **MVP boundary**: one command over one ledger writes one correctly named report.

### Key Constraints, Assumptions & Dependencies
- *Constraint:* standard library only – the analyst's laptop installs nothing (`docs/DECISIONS.md`).
- *Assumption:* ledgers carry no delimiter inside a cell, so no quoting rule is needed yet.


## Problem Definition

### Problem Statement
At month close the ledger owner exports the ledger, opens the result in a spreadsheet, fixes the column and row order by hand, saves it under the month's name, and drops it in the shared folder. Twenty minutes a month, and one month in three the by-hand copy differs from the ledger. Left alone, the shared folder stays a folder of hand-edited files nobody trusts.

### Target Users
- **Ledger owner** – closes the month and needs the numbers out as a file the company opens without asking questions, filed beside the earlier months.
- **Analyst on a locked-down laptop** – reruns an export from the copied tree; can run Python, cannot install anything.

### Desired Outcome
A closed month is one command: the report opens as-is anywhere in the company, and the shared folder holds one report per month, each named for its ledger, none overwritten by the next.

### Evidence & Context
- The month-close notes for February and March each record a by-hand reshape of the export.
- The shared folder held one file, `report.csv`, overwritten each month; February's report was recovered from an email attachment.


## Success Metrics

| Metric | Baseline | Target | How observed |
|--------|----------|--------|--------------|
| Months whose export was reshaped by hand | every month | none, from the first close after release | the month-close note |
| Reports kept in the shared folder | the latest month only | one per closed month | the shared folder listing |


## Scope

### In Scope
- Render records as CSV: header, one line per record, rows in label order.
- Name the report after its ledger; `--name` overrides.
- Write the report inside the output directory, creating it if needed.

### Out of Scope
- A second output format (`docs/DECISIONS.md`: CSV is the only one).
- Quoting or escaping inside cells.
- Column selection or filtering.
- Sending the report anywhere (`docs/PRODUCT.md`: no network access).

### MVP Boundary
One command over one ledger writes one report, named for the ledger, that opens as-is.


## Functional Requirements

### User Stories

| ID | Story | Acceptance Criteria | Priority |
|----|-------|---------------------|----------|
| US01 | As the ledger owner, I want the closed ledger exported as a CSV report, so that the company opens it without my reshaping it. | The report opens in a spreadsheet with `id`, `label`, `amount` columns and every ledger row, in the same order on every run. | Must / P0 |
| US02 | As the ledger owner, I want the report named after its ledger, so that the shared folder keeps every month and April does not overwrite March. | Exporting `march.csv` then `april.csv` into the same folder leaves two reports. | Must / P0 |
| US03 | As an analyst on a locked-down laptop, I want to rerun an export from the copied tree, so that I do not depend on the owner's machine. | `python3 -m src.reporter <ledger>` runs with nothing installed. | Must / P0 |

### Feature Specifications

#### FR1: Export CSV
**Description**: Render the ledger's records as CSV lines.

**Acceptance Criteria**:
- [ ] The first line is the header `id,label,amount`.
- [ ] One line per record follows, ordered by `label` ascending, so two runs over the same ledger produce the same bytes.

**Inputs / Outputs**:
- **Inputs**: the records read from a ledger.
- **Outputs**: the report lines.

**Validation**:
- A malformed row is rejected by the reader before rendering.

**Error Handling**:
- A rejected row is reported on stderr with exit code 2, never a traceback.

**Priority**: Must / P0

#### FR2: Report named after the ledger
**Description**: The report file is named for the ledger it came from, so a folder of monthly runs keeps one report per month.

**Acceptance Criteria**:
- [ ] Without `--name`, the report is `<run label>-report.csv`, where the run label is the ledger's base name with whitespace collapsed and lowercased – the label the run already records beside the report.
- [ ] Exporting two ledgers into the same output directory leaves two reports.
- [ ] `--name` still sets the file name outright.

**Inputs / Outputs**:
- **Inputs**: the ledger path; an optional `--name`.
- **Outputs**: the report's file name.

**Validation**:
- The derived name is a single path component.

**Error Handling**:
- None beyond FR3's containment.

**Priority**: Must / P0

#### FR3: Report inside the output directory
**Description**: The report is written under the directory the run names.

**Acceptance Criteria**:
- [ ] A missing output directory is created.
- [ ] The report is written inside it and its path is printed.
- [ ] Nothing is written outside the output directory.

**Inputs / Outputs**:
- **Inputs**: `--out` (default `out`), the report name, the report lines.
- **Outputs**: the report file; its path on stdout.

**Validation**:
- The report name is confined to the output directory.

**Error Handling**:
- A missing ledger: message on stderr, exit code 2.

**Priority**: Must / P0

### User Flows
1. Month close: the owner runs `python3 -m src.reporter ledgers/april.csv --out /shared/reports`; `april-report.csv` appears beside `march-report.csv`.
2. A rerun over the same ledger replaces that month's report and nothing else.
3. A malformed ledger row: the command reports the row on stderr and exits 2; no report is written.


## Non-Functional Requirements

| Category | Requirement | Threshold / Target |
|----------|-------------|--------------------|
| Performance | A 50,000-row ledger exports in one run | under 5 s on a laptop |
| Reliability | Same bytes on every run over the same ledger | byte-identical |
| Usability | Runs from the copied tree with nothing installed | standard library only |


## Edge Cases

| Scenario | Expected Behavior | Recovery Path |
|----------|-------------------|---------------|
| Ledger name with spaces or capitals (`March Ledger.csv`) | run label `march ledger`, report `march ledger-report.csv` | – |
| Two ledgers with the same base name in one month | the second replaces the first | pass `--name` |
| Empty ledger | header only | – |


## Constraints & Assumptions

### Constraints
- Standard library only; identical behavior on macOS, Linux, and Windows.
- A run writes only inside its output directory.

### Assumptions
- Ledgers carry no delimiter inside a cell.
- Amounts are whole units.

### Dependencies

| Dependency | Why It Matters |
|------------|----------------|
| `docs/DECISIONS.md` Still Current | CSV-only and whole-unit amounts bound FR1 |


## Open Questions

- None.


## Decisions Log

| Decision | Rationale | Alternatives Considered |
|----------|-----------|-------------------------|
| Report name derives from the run label the tool already writes | one naming rule, already normalized | a date stamp (ledgers are named by month already) |
