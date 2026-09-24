# Code Review: Session Hardening

**Review mode**: code
**Target**: story S01 in scripts/fixtures/renders/plan.json
**Revision**: 4f2c9e1-dirty

## Executive Summary

**Readiness: Needs Fixes** - 1 HIGH, 1 LOW, no CRITICAL.

The cookie helper is correct; the audit write is on the latency path with no bound on the retry queue.

Intent Context: `scripts/fixtures/renders/s01-harden-the-session-cookie.md`. Drift Notes: none recorded.

Guardrails Coverage: 4 checked, 0 findings
Filter summary: 1 validated, 1 downgraded, 0 withdrawn

## Coverage Matrix

| Surface | Evidence read | Positive proof | Falsifier attempted | Result |
|---|---|---|---|---|
| `src/auth/session/cookie.ts` | the helper and both callers | every branch sets `HttpOnly`, `Secure`, `SameSite=Lax` | the sign-in error path, which sets no cookie at all | covered |
| `src/audit/log/write.ts` | the buffered writer and its retry loop | a transient store failure still lands the write | the store staying down for the whole retry window | finding |
| `tests/auth/test_session.py` | the two flag assertions | red before the fix, green after | a `Path=/admin` cookie, which still passes | finding |

## Findings

### Finding 1 - HIGH - Unbounded audit retry queue

- **Reviewer**: correctness
- **Confidence**: 100
- **Location**: `src/audit/log/write.ts:22`
- **Scope relation**: primary
- **Finding**: The buffered write retries without a queue bound, so a degraded audit store grows heap until the process dies.
- **Threatened assumption or invariant**: audit buffering is bounded work on the sign-in path.
- **Evidence**: the retry loop appends on every failure and drops nothing; no test holds the store down.
- **Impact**: Sign-in outage caused by the subsystem added to observe sign-in.
- **Suggested fix**: Bound the queue and drop oldest with a counter.
- **Verification needed**: Test that the queue stops growing past the bound.
- `Class:` code-defect
- `Routing:` Fix - the bound is mechanical and inside the story's scope.

### Finding 2 - LOW - Cookie helper lacks a unit test for `Path`

- **Reviewer**: testing
- **Confidence**: 75
- **Location**: `src/auth/session/cookie.ts:1`
- **Scope relation**: primary
- **Finding**: The flag assertions cover `Secure` and `HttpOnly` but not `Path=/`.
- **Threatened assumption or invariant**: the session cookie is scoped to the whole site.
- **Evidence**: the assertion list names two flags; `Path` appears in neither test.
- **Impact**: A future edit could scope the cookie to a subpath unnoticed.
- **Suggested fix**: Extend the existing assertion.
- **Verification needed**: The extended assertion fails against a `Path=/admin` cookie.
- `Class:` code-defect
- `Routing:` Note - which assertion to extend is a choice, not a uniquely determined fix.

## Compliance

- Guidelines adherence: the cookie helper follows the project's one-helper-per-header rule.
- Architecture patterns: the audit writer is called from the sign-in path, which the Architecture document keeps free of blocking I/O – Finding 1.
- Security awareness: no secrets, raw queries, or unvalidated input on the changed paths.

## Critic Coverage

The sign-in error path, a store that stays down for the whole retry window, and a subpath-scoped cookie against the flag assertions.

## Verification Evidence

- `npm test` – 148 passed, 0 failed
- `npm run lint` – clean

## Verdict

**Readiness: Needs Fixes** - 1 HIGH, 1 LOW, no CRITICAL.

## Next Steps

1. Bound the audit retry queue before merge (Finding 1).
2. The missing `Path` assertion (Finding 2) can ride the follow-up story.
