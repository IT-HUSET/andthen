# Write Run Summary

**Plan**: docs/specs/count-summary/plan.json
**Story-ID**: S02

## Feature Overview and Goal

**Intent**: Whoever scans an output directory can tell what a run covered from one line, without opening the report or `rows.txt`.

**Expected Outcomes**:
- [OC01] A run writes `summary.txt` beside the report, one line stating the number of ledger lines the run read and the ledger's file name, with the same number `rows.txt` holds.

## Required Context

- `src/reporter/pipeline.py#run` – the stage sequence the summary joins, after the record count.
- `docs/specs/count-summary/s01-record-row-count.md` – the story that writes `rows.txt`, the figure the summary repeats.
- `docs/ARCHITECTURE.md#key-constraints` – a run writes only inside the output directory it was given.

## Acceptance Scenarios

- **S01 [OC01] A run summarizes the ledger it read**
  - **Given** a ledger named `March Ledger.csv` with the lines `1,north,40`, a blank line, and `2,south,2`, and an output directory
  - **When** `run` completes
  - **Then** `summary.txt` under that directory holds `3 lines from March Ledger.csv`, and `rows.txt` holds `3`
  - **Proof**: `cmd: python3 -m unittest tests.test_pipeline` – TI01 adds the scenario's test first

## Structural Criteria

- **SC01** The implementation uses only the Python standard library.
- **SC02** Nothing is written outside the output directory the run was given.

## Implementation Plan

### Implementation Tasks

- **TI01 Write the run summary**
  - Add `test_run_writes_the_summary_line` to `tests/test_pipeline.py` asserting the scenario, then extend `run` in `src/reporter/pipeline.py` so `summary.txt` is written under the output root after the record count.
  - **Verify**: `cmd: python3 -m unittest tests.test_pipeline` – the summary is proved beside the existing stages
  - **SATISFIES**: S01, SC01, SC02
