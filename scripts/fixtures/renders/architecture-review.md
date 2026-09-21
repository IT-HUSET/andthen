# Architecture Review: Session and Audit Coupling

## Executive Summary

The sign-in handler now depends on the audit log directly, which puts an observability subsystem on the critical path of an availability-critical flow.

## Findings

### ARCH-001: Availability inversion between auth and audit

- **Severity**: HIGH
- **Dimension**: Resilience
- **C4 Level**: Container
- **Evidence**: `src/auth/routes/sign-in.ts:45` awaits `audit.write` before responding.
- **Impact**: Audit degradation becomes sign-in degradation.
- **Recommendation**: Publish the event to a local buffer and drain asynchronously.
- **Fitness Function**: Sign-in p95 unaffected by an audit store fault injection.

## Metrics Dashboard

| Package | Files | Fan-in | Fan-out | Cycles |
|---|---|---|---|---|
| `src/auth` | 14 | 3 | 4 | 0 |
| `src/audit` | 6 | 2 | 1 | 0 |

## Proposed Fitness Functions

- **L2 (PR)** – A sign-in request completes within budget while the audit store returns 503.
