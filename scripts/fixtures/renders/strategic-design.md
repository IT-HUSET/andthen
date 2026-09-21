# Strategic Design: Ledger Contexts

## Executive Summary

Three subdomains, one of them core. The reconciliation context is where the product's value sits and where the model must be sharpest.

## Subdomains

- **Reconciliation** (core) – matching processor events to invoices.
- **Billing** (supporting) – invoice generation.
- **Identity** (generic) – sign-in and session.

## Context Map

```mapviz
[Reconciliation] "core"
[Billing] "supporting"
[Identity] "generic"
Billing -> Reconciliation : "customer-supplier"
Identity -> Reconciliation : "conformist"
```

## Bounded Contexts

### Reconciliation
Owns the match decision and its evidence; publishes settled/unsettled state.

### Billing
Owns invoice lifecycle; consumes settlement state and never writes it.

## Open Issues

- The processor's event vocabulary leaks into Billing through a shared type.
