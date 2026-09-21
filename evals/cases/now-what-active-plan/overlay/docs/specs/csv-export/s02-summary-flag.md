# Summary Flag

**Plan**: docs/specs/csv-export/plan.json
**Story-ID**: S02

## Feature Overview and Goal

**Intent**: A month's totals per label leave the tool with the report, for anyone who would otherwise sum them by hand.

**Expected Outcomes**:
- [OC01] `--summary` appends one `label,total` block to the written report; without it the report is unchanged.

## Acceptance Scenarios

- **S01 [OC01] Totals follow the records**
  - **Given** a ledger whose labels repeat
  - **When** the command line runs with `--summary`
  - **Then** the report carries its records and then a `label,total` block
  - **Proof**: `cmd: python3 -m unittest tests.test_export` – red at spec time

## Structural Criteria

- **SC01** Standard library only.

## Implementation Plan

### Implementation Tasks

- **TI01 Append the totals behind the flag**
  - **Verify**: `cmd: python3 -m unittest tests.test_export` – the block follows the records
  - **SATISFIES**: S01, SC01
