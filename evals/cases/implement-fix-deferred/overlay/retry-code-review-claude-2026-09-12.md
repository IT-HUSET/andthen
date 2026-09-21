# Code Review – the report write path – 2026-09-12

Review mode used: code
Intent Context: docs/PRODUCT.md; docs/ARCHITECTURE.md § Key Constraints
Scope: `src/reporter/retry.py`, `src/reporter/pipeline.py`

## Findings

### F1 – The retry policy is a flat one-second pause five times, which fits neither end of the block it exists for (MEDIUM)

- reviewer: code lens
- severity: MEDIUM
- confidence: 90
- location: `src/reporter/retry.py:5-6`, reached from `src/reporter/pipeline.py:36`
- scope_relation: primary
- finding: `PAUSE_SECONDS = 1.0` and `MAX_RETRIES = 5` are module constants, so every blocked report write waits the same second and then gives up after five of them, whatever the block actually is.
- threatened_assumption_or_invariant: `docs/LEARNINGS.md` § Platform Traps treats the blocked rewrite as transient – the retry exists so a run survives it.
- evidence: `retry.retry` sleeps `PAUSE_SECONDS` between attempts and never varies it; `pipeline.run` routes `write_report` through it. `tests.test_retry.RetryTests.test_retries_a_transient_failure_until_it_succeeds` pins the pause sequence to `[PAUSE_SECONDS, PAUSE_SECONDS]`, so the flat shape is asserted rather than incidental.
- impact: a block that clears in 20 ms still costs a full second; one that outlasts five seconds fails the run over a file that was merely busy, and the analyst closing the month sees neither outcome coming.
- suggested_fix: replace the flat pause with one that grows per attempt under a ceiling, and update the pause-sequence assertion with it.
- verification_needed: `tests.test_retry` driving `retry` with a recording `sleep` over the new sequence, plus the give-up case at the ceiling.
- Class: code-defect
- Routing: Fix – bounded and local to `src/reporter/retry.py`; no call site changes.

Guardrails Coverage: 6 checked, 0 findings
Critic Coverage: the retry ceiling, the exception class the loop catches, the write path's own error reporting, and whether the pause assertion would still fail if the pause were removed altogether

## Verification Evidence

- Commands run: `python3 -m unittest discover -s tests -t .` – 13 passed
- Commands skipped/unavailable: none

## Readiness

Changes Requested – 0 CRITICAL, 0 HIGH, 1 MEDIUM, 0 LOW
