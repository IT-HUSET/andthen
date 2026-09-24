# Code Review Calibration

Domain calibration for code and implementation review, applied after `review-calibration.md`. Contrastive examples, illustrative: the Findings Filter's withdrawal floor may cite one a finding clearly matches.


## Severity Calibration

### Critical

**IS Critical:**
> Auth middleware (`requireAuth.ts`) exists and correctly validates JWT tokens, but is not applied to any of the `/api/payments/*` routes. All payment endpoints are publicly accessible without authentication. – `routes/payments.ts:12-45`

Why: a security bypass on a critical data path; the code exists but the wiring is missing, invisible to a surface-level check.

**is NOT Critical (common over-escalation):**
> Missing input length validation on the admin-only internal configuration endpoint `/admin/settings`. Only accessible to authenticated admin users behind VPN.

Why: low exposure (authenticated admins, VPN-only). Medium – worth noting, not a blocker.


### High

**IS High:**
> The `processPayment` handler catches all exceptions with a bare `catch (e) {}` block – errors from the payment gateway (declined cards, network timeouts, duplicate charges) are silently swallowed. The user sees a success response regardless of whether payment actually processed. – `handlers/payment.ts:67-82`

Why: silent failure in a critical business path – the feature appears to work and fails in foreseeable error scenarios.

**is NOT High (common over-escalation):**
> `console.log("debug: user data", userData)` left in the registration handler. The log contains the user's name and email.

Why: should be removed, but logging to server stdout is not a security vulnerability (unlike the client-side console). Medium – code quality, not a data breach.

**IS High:**
> The search results component fetches every matching record – no `LIMIT`, no cursor, no pagination UI. It works on the 50-row demo fixture, and the `Product` document's Scale fact states 2M+ records. – `components/SearchResults.tsx:23`, `api/search.ts:15`

Why: an anchored cardinality the code cannot survive – a functional gap that surfaces only in production.

**is NOT High (common over-escalation):**
> The `UserProfile` component re-renders on every keystroke in the search bar. No memoization.

Why: no profiling and no performance requirement, so the cost is unmeasured. Low – speculative optimization, not a functional gap.


### Completeness and wiring

A stub on a required path is a completeness gap; an aspirational TODO on working code is not, and missing tests are a coverage finding instead.

Exported-but-never-imported is a wiring gap; wired at a coarser level than someone wanted is a design question.


## False Positive Traps

Patterns that look like code issues but are not:

1. **Framework conventions mistaken for missing code** – flagging Next.js pages for "missing explicit route registration" when file-based routing handles it. Verify whether the framework provides the behavior before flagging its absence.
2. **Intentional trade-offs documented in ADRs or comments** – flagging a synchronous database call when an ADR chose it over async for simplicity in a low-traffic admin tool. Check the decision records before escalating a design choice.
3. **Test utilities flagged as stubs** – a helper returning `{ id: 1, name: "test" }` is a fixture, intentionally minimal, not production code.
4. **Optional features flagged as missing** – the absence of dark mode when the requirements never mention it. A gap maps to an actual requirement.
