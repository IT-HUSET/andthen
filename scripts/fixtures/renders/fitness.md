# Fitness Functions: Ledger Governance

## Current Governance Coverage

| Level | Check | Status |
|---|---|---|
| L1 commit | Lint boundary imports | present |
| L2 PR | Contract tests between Billing and Reconciliation | absent |

## ADR Gap Analysis

### ADR-009: Fixed cookie name
No automated check enforces the name; the edge config and the code can drift.

### ADR-014: Fixed session cookie flags
Partially covered by a unit test on the helper, not by a check on call sites.

## Proposed Fitness Functions

### L1 – No direct processor types in Billing
An import-boundary check fails the commit when Billing imports the processor event type.

### L2 – Sign-in survives audit degradation
A PR-level test injects a 503 from the audit store and asserts sign-in still returns 200 within budget.

## Prioritized Implementation Roadmap

1. L1 import-boundary check – cheapest, and it closes the leak named in strategic design.
2. L2 audit fault injection – needs a fault-injection harness first.
