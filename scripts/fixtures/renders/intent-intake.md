# Intent: Invite Teammates by Email

## Problem
Workspace owners can only add teammates who already have an account, so onboarding a new hire means asking them to sign up first and then hunting for their exact address. Two of the last four onboardings stalled there.

## Proposed Outcome
An owner can send an invitation to any email address, and the recipient joins the workspace by following the link – with no prior account and no manual lookup by the owner.

## Affected Systems
- Workspace membership service (invitation records, acceptance)
- Transactional email sender
- Sign-up flow (accepting an invitation during registration)

## Constraints
- Invitations must not block the request that creates them
- Must work for addresses on domains we do not control

## Open Questions
- Should an invitation expire, and after how long?
- Can a non-owner member invite, or owners only?
