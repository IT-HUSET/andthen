# andthen:clarify visual review notes for scripts/fixtures/renders/prd.md

## Section: Scope
- Rotation on privilege change is in scope but the flow is not in User Flows.

## Section: Functional Requirements
- FR-3: name the rotation trigger – privilege change only, or every re-authentication?
- Missing: what happens to the old cookie after rotation.
  Revoke immediately, or let it expire? Decide before the FIS.

## Section: Success Metrics
- The p95 latency target has no baseline row.
