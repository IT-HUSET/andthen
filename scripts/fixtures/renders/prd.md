# PRD: Session Hardening

> **Shipped**: 2026-08-29T09:40Z

## Executive Summary

Sign-in issues session cookies without the flags a browser needs to keep them out of script and off plaintext transports. This PRD covers the cookie policy and the audit trail that proves a sign-in happened.

### Capabilities at Glance

- **FR1: Hardened Session Cookie** _(Must / P0)_ – one policy, applied wherever a session is issued.
- **FR2: Sign-In Audit Trail** _(Must / P0)_ – one immutable row per attempt, success or failure.

## Scope

### In Scope
- Cookie flags on the sign-in and refresh paths.
- Audit rows for sign-in attempts.

### Out of Scope
- Session revocation UI.

### Not Doing
- Device fingerprinting.

## Functional Requirements

### User Stories

| ID | Story | Acceptance Criteria | Priority |
|---|---|---|---|
| US01 | As a signed-in user, I want my session cookie unreadable by page scripts, so that a script injection cannot lift my session | No sign-in response sets a cookie a script can read | Must / P0 |
| US02 | As a security reviewer, I want every sign-in attempt recorded, so that I can reconstruct an incident | Every attempt leaves one audit row | Must / P0 |

### Feature Specifications

#### FR1: Hardened Session Cookie
**Description**: Every response that issues a session sets the `sid` cookie through one policy.

**Acceptance Criteria**:
- [ ] When the sign-in or refresh endpoint issues a session, the auth service shall set `sid` with `HttpOnly`, `Secure`, `SameSite=Lax`, and `Path=/`.
- [ ] If a request carries a `sid` cookie without those flags, then the auth service shall replace it on the next sign-in, never rewrite it in place.

**Inputs / Outputs**:
- **Inputs**: a validated credential pair or refresh token
- **Outputs**: the `Set-Cookie` header

**Priority**: Must / P0

#### FR2: Sign-In Audit Trail
**Description**: Every sign-in attempt leaves one immutable audit row.

**Acceptance Criteria**:
- [ ] When a sign-in attempt completes, the auth service shall write one audit row naming the user, the outcome, and the timestamp before the response is written.
- [ ] If the audit store is unavailable, then the auth service shall buffer the row in a bounded queue and complete the sign-in.

**Inputs / Outputs**:
- **Inputs**: the attempt's user, outcome, and time
- **Outputs**: an audit row

**Priority**: Must / P0

## Non-Functional Requirements

| Category | Requirement | Threshold |
|---|---|---|
| Latency | Audit write on the sign-in path | ≤ 15 ms p95 |
| Availability | Sign-in succeeds when the audit store is degraded | Degrade to buffered write, never 5xx |

## User Flows

### 1. Credentials arrive
The handler validates the submitted credentials against the user store and rejects on any mismatch, without disclosing which field failed.

### 2. Session is issued
The session store mints an id and the cookie helper renders the full `Set-Cookie` value with the fixed flag set.

### 3. Attempt is recorded
The audit log receives one row naming the user, the outcome, and the timestamp before the response is written.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Audit write adds latency to sign-in | medium | medium | Buffered write with a bounded queue |
| `SameSite=Lax` breaks a cross-site embed | low | high | Inventory embeds before rollout |

## Edge Cases

| Scenario | Expected |
|---|---|
| Audit store unavailable | Sign-in succeeds; the row is buffered and retried |
| Existing session cookie without flags | Replaced on next sign-in, not rewritten in place |

## Constraints & Assumptions

### Constraints
- The cookie name `sid` is fixed by the existing edge configuration.

### Assumptions
- All first-party surfaces are served over HTTPS.

| Dependency | Purpose | Risk |
|---|---|---|
| Audit log service | Records sign-in events | medium |

## Success Metrics

| Metric | Target | Rationale |
|---|---|---|
| Sessions issued with the full flag set | 100% | The policy is only real if it has no gaps |

## Open Questions

- Should the refresh path share the audit event kind, or get its own?
