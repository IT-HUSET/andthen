# Domain Map

## Subdomains

| Subdomain | Type | Rationale | Owns |
|-----------|------|-----------|------|
| Reconciliation | core | Matching processor events to invoices is what customers pay for, and the rules are hard. | The match decision and its evidence. |
| Billing | supporting | Needed, but nothing here sets the product apart. | Invoice lifecycle. |
| Identity | generic | Sign-in and session are solved elsewhere. | Credentials and sessions. |

## Relationships

- An invoice is settled by one or more processor events.
- A session belongs to one customer, and a customer owns many invoices.

## Worked Example

Acme Ltd is invoiced 1,200 EUR (invoice INV-7). The processor reports two payments, 700 and 500 EUR. Reconciliation matches both to INV-7 and marks it settled, and Billing stops dunning. A 700 EUR payment with no invoice stays unsettled and shows up as an exception.

Rules shown: an invoice settles only when matched payments cover its total, and Billing never writes settlement state.

## Open Questions

- Identity is generic today, but a planned single sign-on feature may make it supporting.

## Bounded Contexts

| Context | Purpose | Subdomains owned | Team | Code location |
|---------|---------|------------------|------|---------------|
| Reconciliation | Match processor events to invoices. | Reconciliation | finance-core | `src/reconciliation/` |
| Billing | Generate and track invoices. | Billing | finance-core | `src/billing/` |
| Identity | Sign-in and session. | Identity | platform | `src/identity/` |

## Integration Patterns

| Upstream / peer | Downstream / peer | Channel | Pattern | Notes |
|----------|------------|---------|---------|-------|
| Billing | Reconciliation | invoice events | Customer/Supplier | Reconciliation asks Billing for the invoice fields it needs. |
| Reconciliation | Billing | settlement state | Published Language | Billing reads the settled/unsettled state Reconciliation publishes and never writes it. |
| Identity | Reconciliation | session token | Conformist | Session handling is generic; Reconciliation takes Identity's token as defined. |
| Billing | Identity |  | Separate Ways | Symmetric: Billing keeps its own customer contact data rather than integrating with Identity. |
