# Retry Policy

**Plan**: docs/specs/retry-policy/plan.json
**Story-ID**: S01

## Feature Overview and Goal

**Intent**: A report file another program holds open is re-attempted on a pause the project has settled, rather than on the one nobody decided.

**Expected Outcomes**:
- [OC01] A write that fails transiently and then succeeds returns the written path.
- [OC02] A write that keeps failing gives up after the settled number of retries with the last error.

## Required Context

- `src/reporter/retry.py#retry` – the helper `pipeline.run` wraps the report write in; it ships a fixed 1 s pause and five retries.
- `docs/DECISIONS.md#pending` – the backoff shape is the open decision this story settles.

## Acceptance Scenarios

- **S01 [OC01] A transient failure is retried until it succeeds**
  - **Given** a write that raises `OSError` twice and then succeeds
  - **When** `retry` wraps it
  - **Then** the call returns the written path, having paused between attempts on the settled policy
  - **Proof**: `tests.test_retry#RetryTests.test_retries_a_transient_failure_until_it_succeeds` – green today; it asserts the pause sequence, so it moves with the policy

- **S02 [OC02] A persistent failure gives up**
  - **Given** a write that always raises `OSError`
  - **When** `retry` wraps it
  - **Then** the last `OSError` propagates after the settled maximum
  - **Proof**: `tests.test_retry#RetryTests.test_gives_up_after_the_maximum` – green today; it asserts the attempt count, so it moves with the maximum

## Structural Criteria

- **SC01** The helper uses only the Python standard library.
- **SC02** `src/reporter/retry.py` imports nothing else from the package (ADR-001 layering).

## Implementation Plan

### Implementation Tasks

- **TI01 Pause between attempts on the settled policy**
  - `retry(fn)` in `src/reporter/retry.py` sleeps between attempts per the backoff policy.
  - **Verify**: `tests.test_retry#RetryTests.test_retries_a_transient_failure_until_it_succeeds` – the pause sequence is proved
  - **SATISFIES**: S01, SC01
- **TI02 Give up after the settled maximum**
  - After the maximum number of retries the last error propagates.
  - **Verify**: `tests.test_retry#RetryTests.test_gives_up_after_the_maximum` – the attempt count is proved
  - **SATISFIES**: S02, SC02

## What We're NOT Doing

- No jitter, no per-call override of the policy, no circuit breaker.

## Implementation Observations

_No observations recorded yet._

MISSING REQUIREMENT: the backoff policy is undecided – the fixed 1 s pause that ships today, or a pause that grows from a base up to a cap. The sleep in TI01 and the retry count in TI02 both depend on it.
