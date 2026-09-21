# Record Row Count

**Plan**: docs/specs/row-count/plan.json
**Story-ID**: S01

## Feature Overview and Goal

**Intent**: Whoever picks up a written report can tell how many records went into it without re-reading the ledger.

**Expected Outcomes**:
- [OC01] A run writes the number of exported records beside the report it wrote.

## Required Context

- `src/reporter/pipeline.py#run` – the stage sequence the count joins: seed, label, then the report.
- `docs/ARCHITECTURE.md#key-constraints` – a run writes only inside the output directory it was given.

## Acceptance Scenarios

- **S01 [OC01] A run records how many records it exported**
  - **Given** a ledger of two records and an output directory
  - **When** `run` completes
  - **Then** `rows.txt` under that directory holds `2`, and the report is written as before
  - **Proof**: `cmd: python3 -m unittest tests.test_pipeline` – red at spec time

## Structural Criteria

- **SC01** The implementation uses only the Python standard library.
- **SC02** Nothing is written outside the output directory the run was given.

## Implementation Plan

### Implementation Tasks

- **TI01 Write the exported record count**
  - Extend `run` in `src/reporter/pipeline.py` so the count of loaded records is written to `rows.txt` under the output root.
  - **Verify**: `cmd: python3 -m unittest tests.test_pipeline` – the count is proved beside the existing stages
  - **SATISFIES**: S01, SC01, SC02
