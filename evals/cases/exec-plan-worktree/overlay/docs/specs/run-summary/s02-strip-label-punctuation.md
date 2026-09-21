# Strip Label Punctuation

**Plan**: docs/specs/run-summary/plan.json
**Story-ID**: S02

## Feature Overview and Goal

**Intent**: A ledger whose name carries a trailing period or surrounding quotes labels its run the same as one without them, so two exports of the same ledger read as one label.

**Expected Outcomes**:
- [OC01] `normalize_label` drops leading and trailing punctuation before it collapses whitespace and lowercases.

## Required Context

- `src/reporter/text_tools.py#normalize_label` – the one label helper; a leaf module that imports nothing from the package.
- `tests/test_text_tools.py` – the helper's suite the scenario's test joins.
- `docs/adrs/adr-001-module-layering.md` – leaf modules stay import-free within the package.

## Acceptance Scenarios

- **S01 [OC01] Surrounding punctuation does not reach the label**
  - **Given** the text `  "North Region." `
  - **When** `normalize_label` runs
  - **Then** the result is `north region`
  - **Proof**: `cmd: python3 -m unittest tests.test_text_tools` – TI01 adds the scenario's test first

## Structural Criteria

- **SC01** The implementation uses only the Python standard library.
- **SC02** `text_tools.py` imports nothing from the package.

## Implementation Plan

### Implementation Tasks

- **TI01 Strip surrounding punctuation**
  - Add `test_strips_surrounding_punctuation` to `tests/test_text_tools.py` asserting the scenario, then extend `normalize_label` in `src/reporter/text_tools.py` to strip leading and trailing punctuation before the existing collapse and lowercase.
  - **Verify**: `cmd: python3 -m unittest tests.test_text_tools` – the helper's suite, the new test included
  - **SATISFIES**: S01, SC01, SC02
