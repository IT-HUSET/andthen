# PRD: Session Hardening

## Executive Summary

Sign-in issues session cookies without the flags a browser needs to keep them out of script and off plaintext transports. This PRD covers the cookie policy and the audit trail that proves a sign-in happened.

### Capabilities at Glance

- **Hardened session cookie** – one policy, applied wherever a session is issued.
- **Sign-in audit trail** – one immutable row per attempt, success or failure.

## Scope

### In Scope
- Cookie flags on the sign-in and refresh paths.
- Audit rows for sign-in attempts.

### Out of Scope
- Session revocation UI.

### Not Doing
- Device fingerprinting.

## Functional Requirements

| As a | I want | So that |
|---|---|---|
| Signed-in user | my session cookie to be unreadable by page scripts | a script injection cannot lift my session |
| Security reviewer | every sign-in attempt recorded | I can reconstruct an incident |

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
