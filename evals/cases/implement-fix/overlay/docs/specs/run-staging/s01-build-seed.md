# Build Seed

**Plan**: docs/specs/run-staging/plan.json
**Story-ID**: S01

## Feature Overview and Goal

**Intent**: A run records what it was run over, so the files it writes can be traced back to a ledger.

**Expected Outcomes**:
- [OC01] The seed artifact under the output root holds the ledger's base name.

## Acceptance Scenarios

- **S01 [OC01] The seed is built**
  - **Given** a ledger named `March Ledger.csv` and an output directory that does not exist yet
  - **When** `build_seed` runs
  - **Then** `seed.txt` under that directory holds `March Ledger`
  - **Proof**: `cmd: python3 -m unittest tests.test_pipeline.PipelineTests.test_seed_is_the_ledger_name` – red at spec time

## Structural Criteria

- **SC01** The implementation uses only the Python standard library.

## Implementation Plan

### Implementation Tasks

- **TI01 Implement seed production**
  - Add `build_seed` to `src/reporter/pipeline.py`.
  - **Verify**: `cmd: python3 -m unittest tests.test_pipeline.PipelineTests.test_seed_is_the_ledger_name` – the seed is proved
  - **SATISFIES**: S01, SC01
