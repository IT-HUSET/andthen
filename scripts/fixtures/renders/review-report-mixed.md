# Mixed Review: Workspace Invitations

**Review mode**: mixed
**Resolved chain**: code, gap, security
**Target**: plan docs/specs/workspace-invitations/plan.json
**Revision**: 8b31d07
**Follows**: workspace-invitations-andthen-mixed-review-claude-2026-09-15.md
**Remediated**: fixes applied after this verdict – see `## Remediation Status`

## Executive Summary

**Overall readiness: FAIL** - code Needs Fixes, gap FAIL, security Ready.

Follow-up review over the two finding families the 2026-09-15 report left open, the artifacts their repairs touched, and the seat-count invariant neither pass covered. Both are still open: the seat-count write outside the acceptance transaction (Finding 1) and the S03 expiry scenario with no proof (Finding 2).

Intent Context: `docs/specs/workspace-invitations/plan.json`. Drift Notes: S02 records the rate limit deferred to a later story.

Guardrails Coverage: 7 checked, 1 finding
Filter summary: 2 validated, 0 downgraded, 1 withdrawn

## Coverage Matrix

| Surface | Evidence read | Positive proof | Falsifier attempted | Result |
|---|---|---|---|---|
| `src/invitations/accept.ts` | the accept handler and its seat write | an accepted invitation increments the seat count once | accepting the same invitation twice | finding |
| `src/invitations/token.ts` | token mint and verify | a tampered token is rejected | a token whose expiry field is absent | covered |
| S03 Acceptance Scenarios | the FIS scenarios against their proofs | every scenario names a proof that runs | a scenario whose proof asserts nothing | finding |
| `tests/invitations/test_accept.py` | the four cases added by the repair | red before the repair, green after | a revoked invitation replayed after acceptance | covered |

## Findings

### Code

#### Finding 1 - MEDIUM - Seat count is written outside the acceptance transaction

- **Reviewer**: correctness
- **Confidence**: 100
- **Location**: `src/invitations/accept.ts:74`
- **Scope relation**: primary
- **Finding**: The seat increment commits in its own transaction after the membership row, so a crash between them leaves the count low.
- **Threatened assumption or invariant**: seat count equals the number of memberships.
- **Evidence**: two `await tx.commit()` calls in one handler; no compensating read.
- **Impact**: Billing under-counts seats until someone reconciles by hand.
- **Suggested fix**: Write both rows in the one transaction the handler already opens.
- **Verification needed**: A test that fails the second write and asserts the membership rolled back.
- `Class:` code-defect
- `Routing:` Fix - one transaction boundary, uniquely determined.

### Gap

#### Finding 2 - HIGH - S03 ships without the expiry scenario it declares

- **Reviewer**: conformance
- **Confidence**: 100
- **Location**: `docs/specs/workspace-invitations/s03-expire-invitations.md`
- **Scope relation**: primary
- **Finding**: Verification depth – scenario S03-2 (an expired invitation cannot be accepted) names a proof that no test file defines.
- **Threatened assumption or invariant**: every Acceptance Scenario has a proof that runs.
- **Evidence**: the named proof id is absent from the suite; the story is recorded `done`.
- **Impact**: An expired invitation is accepted, and nothing in the suite says so.
- **Suggested fix**: Write the named proof, then re-run the story's verification.
- **Verification needed**: The proof is red against the current code.
- `Class:` code-defect
- `Routing:` Fix - the proof is named in the FIS, so its shape is not the reviewer's invention.

### Security

No findings. Token mint, verify, and revoke were attacked with tampered, absent, and replayed tokens; the trust boundary between invitation acceptance and workspace membership holds.

## Compliance

- Guidelines adherence: the repair follows the project's one-transaction-per-handler rule except at `accept.ts:74`, Finding 1.
- Architecture patterns: invitation acceptance stays inside the workspace module; no new cross-module call.
- Security awareness: no secrets, raw queries, or unvalidated input on the changed paths.

## Trust-Boundary Map

- invitation token (URL) → signature and expiry check in `token.ts` → membership insert
- accepting user's session → workspace-scoped authz check → seat count update

## Critic Coverage

Code: double acceptance, a crash between the two writes, a revoked invitation replayed. Gap: every S01–S03 scenario walked to its named proof. Security: tampered, absent, and replayed tokens against mint, verify, and revoke.

## Verification Evidence

- `npm test` – 212 passed, 0 failed
- `npm run lint` – clean
- `npm audit --omit=dev` – 0 vulnerabilities

## Verdict

**Overall readiness: FAIL** - code Needs Fixes, gap FAIL, security Ready.

### Gap

| Dimension     | Score | Threshold | Status |
|---------------|-------|-----------|--------|
| Functionality | 8/10  | >= 7      | PASS |
| Completeness  | 6/10  | >= 9      | FAIL |
| Wiring        | 9/10  | >= 8      | PASS |

**Overall: FAIL**

## Next Steps

1. Move the seat increment into the acceptance transaction (Finding 1); no dependency.
2. Write the S03-2 expiry proof (Finding 2), then re-run S03's verification; done when the proof is red against the current code and green after the fix.

## Remediation Status

- **Finding 1 - Seat count is written outside the acceptance transaction** - RESOLVED - both rows now commit in the handler's transaction; `tests/invitations/test_accept.py::test_rollback_on_seat_write_failure` is green.
- **Finding 2 - S03 ships without the expiry scenario it declares** - DEFERRED - `decision needed`: whether an expired invitation is rejected or silently renewed is open in the PRD. Entered in the Tech Debt Backlog under High.
