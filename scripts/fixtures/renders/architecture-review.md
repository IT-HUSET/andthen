# Architecture Review: Session and Audit Coupling

## Executive Summary

The package structure is healthy apart from one runtime coupling. Findings: 1 HIGH. The most critical issue is ARCH-001: the sign-in handler waits on the audit log, which puts an observability subsystem on the critical path of an availability-critical flow. The most impactful recommendation is to take the audit write off that path.

## How to Read This Report

- **LOC** – lines of code. **Ca** / **Ce** – packages depending on this one / packages this one depends on.
- **I** – instability, `Ce / (Ca + Ce)`: 0 is stable, 1 is volatile. **A** – abstractness, abstract types over all types.
- **D** – distance from the main sequence, `|A + I - 1|`: below 0.3 is healthy. **Zone** – Zone of Pain or Zone of Uselessness; `–` means neither.
- **SDP** – Stable Dependencies Principle: a dependency points toward the more stable package.
- **C4 level** – where a finding sits: Context, Container, Component, or Code.
- **CoE** – connascence of execution: one element must run before another. It is a dynamic form, so static analysis cannot see it.

## Metrics Dashboard

| Package | LOC | Ca | Ce | I | A | D | Zone | Notes |
|---|---|---|---|---|---|---|---|---|
| `src/auth` | 1420 | 3 | 4 | 0.57 | 0.25 | 0.18 | – | new edge to `src/audit` |
| `src/audit` | 610 | 2 | 1 | 0.33 | 0.50 | 0.17 | – | |

## Findings

### ARCH-001: Availability inversion between auth and audit

- **Reviewer**: architecture
- **Severity**: HIGH
- **Confidence**: 100
- **Location**: `src/auth` → `src/audit`, C4 Component
- **Scope relation**: primary
- **Finding**: The sign-in handler awaits the audit write before it responds.
- **Threatened assumption or invariant**: sign-in availability does not depend on an observability subsystem.
- **Evidence**: detected – `src/auth/routes/sign-in.ts:45` awaits `audit.write` across the package boundary. Interpreted – an audit store outage or slowdown reaches every sign-in.
- **Impact**: Audit degradation becomes sign-in degradation.
- **Suggested fix**: Per Weirich's Rule of Locality, weaken the dynamic connascence crossing the boundary: publish the event to a local buffer and drain it asynchronously.
- **Verification needed**: Sign-in stays within its p95 budget while the audit store is down.
- **Dimension**: coupling
- **Connascence**: CoE – Strength: 6, Degree: 1, Locality: 1 -> Severity: 6
- **Fitness function**: `sign-in-survives-audit-outage`, governance level 3 (nightly).

## Dependency Graph

`src/auth` (I = 0.57) → `src/audit` (I = 0.33). The edge points toward the more stable package, so SDP holds. There are no cycles. `src/audit` is the foundation of this pair and `src/auth` the consumer.

## Proposed Fitness Functions

- **`sign-in-survives-audit-outage`** – checks that sign-in completes while the audit store returns 503.
  - Threshold: sign-in p95 within its budget.
  - Governance level: 3, nightly.
  - Implementation: an integration test that stubs the audit store with a 503 fault and measures sign-in latency.
  - Addresses: ARCH-001.
