# Comment lines in the ledger

**Plan**: docs/specs/ledger-hygiene/plan.json
**Story-ID**: S01

## Feature Overview and Goal

**Intent**: The ledger owner keeps month-close notes in the ledger itself, and the run reads past them instead of stopping on them.

**Expected Outcomes**:
- [OC01] A ledger with comment lines yields exactly the records of the same ledger without them.
- [OC02] A hash that is not the first character of a line stays part of its record.

## Required Context

- `docs/ARCHITECTURE.md#key-constraints` – the reader stays free of command-line concerns.

## Acceptance Scenarios

- **S01 [OC01] Comment lines are skipped**
  - **Given** a ledger whose first line and one middle line start with `#`
  - **When** `load_records` reads it
  - **Then** the result holds only the records of the lines that do not start with `#`
  - **Proof**: `tests.test_records#LoadRecordsTests.test_skips_comment_lines` – green

- **S02 [OC02] A later hash is data**
  - **Given** a record whose label contains `#` after its first character
  - **When** `load_records` reads it
  - **Then** the record keeps its label unchanged
  - **Proof**: `tests.test_records#LoadRecordsTests.test_keeps_a_later_hash` – green

## Structural Criteria

- **SC01** The reader uses only the standard library.

## Implementation Plan

### Implementation Tasks

- **TI01 The reader skips comment lines**
  - `load_records(path)` in `src/reporter/records.py` ignores a line whose first character is `#`.
  - **Verify**: `tests.test_records#LoadRecordsTests.test_skips_comment_lines` – only the non-comment records come back
  - **SATISFIES**: S01, S02, SC01

## What We're NOT Doing

- No comment after a record on the same line; the PRD scopes it out.

## Implementation Observations

_No observations recorded yet._
