# FIS: Harden the session cookie

**Plan**: scripts/fixtures/renders/plan.json
**Story-ID**: S01

## Feature Overview and Goal

**Intent**: a stolen page script must not be able to read a session, so the cookie stops being
readable from JavaScript.

**Expected Outcomes**:
- `[OC01]` A page script cannot read the session cookie.

## Acceptance Scenarios

- **S01 [OC01] A sign-in response sets the session cookie HttpOnly**
  - **Given** a valid credential pair
  - **When** the sign-in endpoint returns 200
  - **Then** the `Set-Cookie` header carries `HttpOnly` and `SameSite=Lax`
  - **Proof**: `tests/auth/test_session.py#test_sign_in_sets_httponly` – red at spec time

## Structural Criteria

- **SC01** The cookie flags are set in one place, not per handler

## Implementation Plan

### Work Areas

- `src/auth/session.py` – cookie construction

### Implementation Tasks

- **TI01** The sign-in response carries HttpOnly and SameSite=Lax
  - **Verify**: `tests/auth/test_session.py#test_sign_in_sets_httponly` – the header carries both flags
  - **SATISFIES**: S01
- **TI02** Every handler builds its cookie through one helper
  - **Verify**: `tests/auth/test_session.py#test_single_cookie_builder` – no handler constructs Set-Cookie itself
  - **SATISFIES**: SC01
