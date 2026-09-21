# Mixed Review: Workspace Invitations

**Review mode**: mixed
**Resolved chain**: code, gap, security
**Target**: plan docs/specs/workspace-invitations/plan.json
**Revision**: 8b31d07
**Follows**: workspace-invitations-andthen-mixed-review-claude-2026-09-15.md
**Remediated**: fixes applied after this verdict – see `## Remediation Status`

## Executive Summary

**Overall readiness: FAIL** on the gap lens; code **Needs Fixes**, security **Ready**. Follow-up review over the two finding families the 2026-09-15 report left open, the artifacts their repairs touched, and the seat-count invariant neither pass covered. Both are still open: the seat-count write outside the acceptance transaction (Finding 1) and the S03 expiry scenario with no proof (Finding 2).

Intent Context: `docs/specs/workspace-invitations/plan.json`. Drift Notes: S02 records the rate limit deferred to a later story.

Guardrails Coverage: 7 checked, 1 finding

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
- **Severity**: MEDIUM
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
- **Severity**: HIGH
- **Confidence**: 100
- **Location**: `docs/specs/workspace-invitations/s03-expire-invitations.md`
- **Scope relation**: primary
- **Finding**: Scenario S03-2 (an expired invitation cannot be accepted) names a proof that no test file defines.
- **Threatened assumption or invariant**: every Acceptance Scenario has a proof that runs.
- **Evidence**: the named proof id is absent from the suite; the story is recorded `done`.
- **Impact**: An expired invitation is accepted, and nothing in the suite says so.
- **Suggested fix**: Write the named proof, then re-run the story's verification.
- **Verification needed**: The proof is red against the current code.
- `Class:` code-defect
- `Routing:` Fix - the proof is named in the FIS, so its shape is not the reviewer's invention.

### Security

No findings. Token mint, verify, and revoke were attacked with tampered, absent, and replayed tokens; the trust boundary between invitation acceptance and workspace membership holds.

## Verdict

Per lens: code **Needs Fixes**, security **Ready**, gap below. **Overall readiness: FAIL** - the worst across lenses.

### Gap

| Dimension     | Score | Threshold | Status |
|---------------|-------|-----------|--------|
| Functionality | 8/10  | >= 7      | PASS |
| Completeness  | 6/10  | >= 9      | FAIL |
| Wiring        | 9/10  | >= 8      | PASS |

**Overall: FAIL**

## Remediation Status

- **Seat count is written outside the acceptance transaction** - RESOLVED - both rows now commit in the handler's transaction; `tests/invitations/test_accept.py::test_rollback_on_seat_write_failure` is green.
- **S03 ships without the expiry scenario it declares** - DEFERRED - `decision needed`: whether an expired invitation is rejected or silently renewed is open in the PRD. Entered in the Tech Debt Backlog under High.
