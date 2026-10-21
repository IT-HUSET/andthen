# Code Review: CSV export

**Review mode**: code
**Target**: paths src/reporter/cli.py, src/reporter/pipeline.py, src/reporter/retry.py
**Revision**: 9d4e1b7
**Remediated**: fixes applied after this verdict – see `## Remediation Status`

## Executive Summary

**Readiness: Needs Fixes** - 0 CRITICAL, 1 HIGH, 1 MEDIUM, 0 LOW

The command line breaks its own documented exit-code contract on ordinary bad input, which blocks readiness on its own. The retry policy is a real finding whose repair waits on an open decision.

Scope: `src/reporter/cli.py`, `src/reporter/pipeline.py`, `src/reporter/retry.py`. Intent Context: `docs/PRODUCT.md`, `docs/ARCHITECTURE.md` § Key Constraints, `docs/DECISIONS.md`, `docs/specs/csv-export/s01-export-csv.md`. Drift Notes: none recorded.

Guardrails Coverage: 5 checked, 1 findings
Filter summary: 2 validated, 0 downgraded, 0 withdrawn

## Coverage Matrix

| Surface | Evidence read | Positive proof | Falsifier attempted | Result |
|---|---|---|---|---|
| Exit codes of `cli.main` | `src/reporter/cli.py`, `src/reporter/records.py`, `docs/ARCHITECTURE.md` § Key Constraints | the missing-ledger branch returns 2 with a message | a ledger row whose amount is not an integer | finding |
| Staging order in `pipeline.run` | `src/reporter/pipeline.py`, `tests/test_pipeline.py` | seed, label, then report, each read from disk | `build_label` run in a fresh process | covered |
| Retry around the report write | `src/reporter/retry.py`, `src/reporter/pipeline.py`, `docs/LEARNINGS.md`, `docs/DECISIONS.md` | `tests/test_retry.py` pins the pause sequence | a block that clears in milliseconds, one that outlasts the maximum | finding |

## Findings

### Finding 1 - HIGH - A malformed amount cell escapes `cli.main` as a traceback

- **Reviewer**: code lens
- **Confidence**: 100
- **Location**: `src/reporter/cli.py:21-25`, raised from `src/reporter/records.py:16`
- **Scope relation**: primary
- **Finding**: `main` maps `FileNotFoundError` to exit code 2 and nothing else. `records.parse_row` deliberately raises `ValueError` for a row with the wrong field count or a non-integer `amount`, and no handler on the path to `main` catches it.
- **Threatened assumption or invariant**: `docs/ARCHITECTURE.md` § Key Constraints: "A bad ledger is reported as a message on stderr with exit code 2. A traceback reaching the user is a bug."
- **Evidence**: a ledger holding the row `1,north,fourty` exits 1 with a `ValueError` traceback from `records.py:16`. `tests/` has no test for the command line's exit codes.
- **Impact**: ordinary bad input from a finance export reaches the analyst as a traceback and exit code 1, which a script wrapping the tool cannot tell from a crash.
- **Suggested fix**: catch `ValueError` beside `FileNotFoundError` in `main`, write a message naming the ledger to stderr, return 2.
- **Verification needed**: a test that drives `main` over a malformed ledger and asserts exit code 2, a message on stderr, and no traceback.
- `Class:` code-defect
- `Routing:` Fix - bounded to `cli.main`, uniquely determined by the documented constraint.

### Finding 2 - MEDIUM - A flat one-second pause makes a busy report cost five silent seconds

- **Reviewer**: code lens
- **Confidence**: 75
- **Location**: `src/reporter/retry.py:5-6`, reached from `src/reporter/pipeline.py:36`
- **Scope relation**: primary
- **Finding**: `PAUSE_SECONDS = 1.0` and `MAX_RETRIES = 5` make every blocked report write wait one second per attempt, up to five, before the command line says anything.
- **Threatened assumption or invariant**: `docs/LEARNINGS.md` § Platform Traps treats the blocked rewrite as transient, so the wait should track how long the block lasts.
- **Evidence**: `retry.retry` sleeps `PAUSE_SECONDS` between attempts and never varies it; `tests.test_retry` pins the flat sequence.
- **Impact**: an analyst with the previous report open in a spreadsheet waits five seconds with no output, then sees the write fail.
- **Suggested fix**: a growing pause under a ceiling. `docs/DECISIONS.md` § Pending ("Retry backoff") holds this open until the hold time on the shared drive is measured, so the repair is that decision, not an edit.
- **Verification needed**: the measurement the Pending row names, then `tests.test_retry` over the chosen sequence.
- `Class:` ambiguous-intent
- `Routing:` Note - the remedy is the open Retry backoff decision in `docs/DECISIONS.md` § Pending, so no mechanical fix is determined.

## Compliance

- Layering: `cli` → `pipeline` → leaves holds for the files in scope.
- Standard library only: holds.
- Exit-code contract: violated, Finding 1.

## Critic Coverage

The exit-code contract against every exception `records.parse_row` raises, whether `pipeline.run` reads its inputs from disk, and whether the retry pause assertion would still fail if the pause were removed.

## Verification Evidence

- `python3 -m unittest discover -s tests -t .` – 13 passed

## Verdict

**Readiness: Needs Fixes** - 0 CRITICAL, 1 HIGH, 1 MEDIUM, 0 LOW

## Next Steps

1. Fix Finding 1 in `src/reporter/cli.py` with its test.
2. Finding 2 waits on the Retry backoff decision.

## Remediation Status

- **Finding 1 - A malformed amount cell escapes `cli.main` as a traceback** - RESOLVED - `cli.main` catches the `ValueError`, writes `bad ledger <path>: <reason>` to stderr and returns 2; `tests.test_cli` covers exit codes 0 and 2, the malformed amount among them.
- **Finding 2 - A flat one-second pause makes a busy report cost five silent seconds** - SURFACED - routed Note; the remedy is the open Retry backoff decision in `docs/DECISIONS.md` § Pending, which waits on a measurement nobody has taken.
