# Build Label

**Plan**: docs/specs/run-staging/plan.json
**Story-ID**: S02

## Feature Overview and Goal

**Intent**: The run label is the seed the run already wrote, normalized - one derivation, not two.

**Expected Outcomes**:
- [OC01] The label artifact holds the normalized form of the seed the run wrote.

## Acceptance Scenarios

- **S01 [OC01] The label is derived**
  - **Given** S01 completed and `seed.txt` holds `March Ledger`
  - **When** `build_label` runs
  - **Then** `label.txt` holds `march ledger`
  - **Proof**: `cmd: python3 -m unittest tests.test_pipeline.PipelineTests.test_label_normalizes_the_seed` – red at spec time

## Structural Criteria

- **SC01** The implementation reads the prerequisite artifact rather than carrying its value in memory, so the stages stay independently callable (`docs/ARCHITECTURE.md` § Data Flow).

## Implementation Plan

### Implementation Tasks

- **TI01 Implement dependent label production**
  - Add `build_label` to `src/reporter/pipeline.py`.
  - **Verify**: `cmd: python3 -m unittest tests.test_pipeline.PipelineTests.test_label_normalizes_the_seed` – dependency consumption is proved
  - **SATISFIES**: S01, SC01
