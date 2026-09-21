# Export CSV

**Plan**: docs/specs/csv-export/plan.json
**Story-ID**: S01

## Feature Overview and Goal

**Intent**: A closed ledger leaves the tool as a file the rest of the company can open, without anyone reshaping it by hand first.

**Expected Outcomes**:
- [OC01] A ledger becomes a CSV report carrying a header row and one line per record.
- [OC02] Two runs over the same ledger produce byte-identical reports, whatever order the ledger happens to list its rows in.

## Required Context

- `docs/ARCHITECTURE.md#key-constraints` – the layering rule and the output-directory boundary the writer stays inside.
- `docs/DECISIONS.md#still-current` – CSV is the only output format, and `amount` is a whole unit.

## Acceptance Scenarios

- **S01 [OC01] A ledger becomes CSV**
  - **Given** two records read from a ledger
  - **When** `export_csv` runs
  - **Then** the result is a header line naming `id`, `label`, `amount` followed by one line per record
  - **Proof**: `tests.test_export#ExportCsvTests.test_writes_a_header` – green

- **S02 [OC02] Rows leave in label order**
  - **Given** records whose labels are not in alphabetical order in the ledger
  - **When** `export_csv` runs
  - **Then** the lines after the header are ordered by `label`, ascending, so the report does not depend on ledger order
  - **Proof**: `tests.test_export#ExportCsvTests.test_exports_rows_in_order` – green

- **S03 [OC01] The report lands in the output directory**
  - **Given** an output directory that does not exist yet
  - **When** `write_report` runs
  - **Then** the directory is created and the report is written inside it, and the written path is returned
  - **Proof**: `tests.test_export#WriteReportTests.test_writes_the_lines_under_the_root` – green

## Structural Criteria

- **SC01** The exporter uses only the standard library.
- **SC02** `src/reporter/export.py` imports nothing else from the package (ADR-001 layering).

## Implementation Plan

### Implementation Tasks

- **TI01 Records render as CSV lines**
  - `export_csv(rows)` in `src/reporter/export.py` returns the header line plus the rows in label order.
  - **Verify**: `tests.test_export#ExportCsvTests.test_exports_rows_in_order` – header first, then the records ordered by label
  - **SATISFIES**: S01, S02, SC01
- **TI02 The report file exists under the output directory**
  - `write_report(root, name, lines)` creates `root` if needed and returns the path it wrote.
  - **Verify**: `tests.test_export#WriteReportTests.test_writes_the_lines_under_the_root` – the file exists with the given lines
  - **SATISFIES**: S03, SC02

## What We're NOT Doing

- No second output format – CSV is the decided one (`docs/DECISIONS.md`).
- No quoting or escaping rules; the ledgers carry no delimiters inside a cell, and inventing an escape now would fix a shape we have not seen.
- No column selection or filtering; the report carries every record the ledger holds.

## Implementation Observations

_No observations recorded yet._
