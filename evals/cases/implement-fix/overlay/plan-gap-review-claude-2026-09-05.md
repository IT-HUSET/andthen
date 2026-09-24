# Gap Review – docs/specs/run-staging/plan.json – 2026-09-05

**Review mode**: gap
**Target**: plan docs/specs/run-staging/plan.json
**Revision**: 4c1d9e2

Intent Context: docs/specs/run-staging/plan.json (s01-build-seed.md, s02-build-label.md).

## Findings

### Finding 1 - HIGH - build_label reads a module-level copy of the seed instead of seed.txt

- **Reviewer**: gap lens
- **Confidence**: 100
- **Location**: `src/reporter/pipeline.py`
- **Scope relation**: primary
- **Finding**: Wiring – `src/reporter/pipeline.py` keeps the seed in a module-level dictionary that `build_seed` fills, and `build_label` reads that dictionary instead of `seed.txt`.
- **Threatened assumption or invariant**: S02's structural criterion SC01 requires the label to be derived from the prerequisite artifact, and `docs/ARCHITECTURE.md` § Data Flow states the label is derived from `seed.txt`.
- **Evidence**: `build_label` never opens a file; its only input is the dictionary `build_seed` wrote in the same process.
- **Impact**: a caller that stages a run and asks for its label in a fresh process raises `KeyError`.
- **Suggested fix**: read `seed.txt` under the run root and normalize it.
- **Verification needed**: a test that stages a seed in one process and builds the label in another.
- `Class:` code-defect
- `Routing:` Fix - bounded, uniquely determined.

## Verdict

| Dimension     | Score | Threshold | Status |
|---------------|-------|-----------|--------|
| Functionality | 8/10  | >= 7      | PASS |
| Completeness  | 6/10  | >= 9      | FAIL |
| Wiring        | 8/10  | >= 8      | PASS |

**Overall: FAIL**
