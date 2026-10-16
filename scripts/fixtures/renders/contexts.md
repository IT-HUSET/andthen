# Contexts: Ledger

## Executive Summary

Three contexts, one per subdomain, and the reconciliation context is the core. It sits downstream of both other contexts, so its contracts with them decide how sharp its model can stay.

## Bounded Contexts

### Reconciliation
Owns the match decision and its evidence; publishes settled/unsettled state.

### Billing
Owns invoice lifecycle; consumes settlement state and never writes it.

### Identity
Owns sign-in and session; supplies the session token the others accept.

## Integration Patterns

```mapviz
[Reconciliation] "core"
[Billing] "supporting"
[Identity] "generic"
Billing -> Reconciliation : "customer-supplier"
Reconciliation -> Billing : "published-language"
Identity -> Reconciliation : "conformist"
```

| Upstream / peer | Downstream / peer | Channel | Pattern | Rationale |
|----------|------------|---------|---------|-----------|
| Billing | Reconciliation | invoice events | Customer/Supplier | Reconciliation asks Billing for the invoice fields it needs. |
| Reconciliation | Billing | settlement state | Published Language | Billing reads the settled/unsettled state Reconciliation publishes and never writes it. |
| Identity | Reconciliation | session token | Conformist | Session handling is generic; Reconciliation takes Identity's token as defined. |
| Billing | Identity |  | Separate Ways | Symmetric: Billing keeps its own customer contact data. |

## Ubiquitous-Language Touchpoints

- The processor's event vocabulary leaks into Billing through a shared type.

## Domain Map Registration

Registered in `docs/DOMAIN-MAP.md`: three Bounded Contexts rows and four Integration Patterns rows.
