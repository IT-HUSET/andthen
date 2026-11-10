Sign-in now issues the session cookie out of reach of page scripts and records every attempt, so a script injection cannot lift a session and an incident can be reconstructed ([PRD](scripts/fixtures/renders/prd.md)).

## Outcomes and proof

- **S01** A page script cannot read the session cookie. Proof: `python3 -m unittest tests.auth.test_session`, 2 tests, OK.
- **S02** Every sign-in attempt leaves one audit row, and a degraded audit store never fails a sign-in. Proof: `python3 -m unittest tests.audit.test_signin_log`, 3 tests, OK.

Review: code FAIL and gap PASS at `9c4e2a7`. Both verdicts predate the fix for the review's one HIGH finding, the unbounded audit queue, and no review re-ran them. Security and outcome were not reviewed.

## Door and blast radius

Two-way door. A wrong cookie flag signs every user out on their next request, and a wrong audit write slows sign-in. Reverting the merge restores the old cookie code, but sessions issued meanwhile keep their flags until they expire, and the audit rows written stay in the store.

## Where to read closely

- `src/auth/session/cookie.ts` sets the flags for every session, so an error there reaches every user.
- The audit queue drops its oldest row when full. No check can judge whether losing a row beats slowing sign-in.
- No security or outcome review ran, `src/auth/session/refresh.ts` was not reviewed, and `npm run test:e2e` was skipped.
- `src/audit/log/write.ts` changed after the review at `9c4e2a7`, in the commit that bounded the queue.

## What stays open

The refresh path shares the sign-in audit event kind until the PRD's open question is settled.

<details>
<summary>Per-story detail</summary>

S01 moved cookie construction into one helper that every handler calls. S02 added a buffered audit writer with a 1,000-row bound.

</details>

<details>
<summary>Ship summary (tables for tooling)</summary>

## Ship summary

PRD: scripts/fixtures/renders/prd.md

| Story | Plan | Outcome | Requirements | Outcome proof |
|---|---|---|---|---|
| S01 | scripts/fixtures/renders/plan.json | [OC01] A page script cannot read the session cookie. | FR1 | python3 -m unittest tests.auth.test_session -> exit=0, Ran 2 tests, OK |
| S02 | scripts/fixtures/renders/plan.json | [OC01] Every sign-in attempt leaves one audit row. | FR2 | python3 -m unittest tests.audit.test_signin_log -> exit=0, Ran 3 tests, OK |
| S02 | scripts/fixtures/renders/plan.json | [OC02] A degraded audit store never fails a sign-in. | FR2 | python3 -m unittest tests.audit.test_signin_log -> exit=0, Ran 3 tests, OK |

| Lens | Verdict | Reviewed commit | Remediated |
|---|---|---|---|
| code | FAIL | 9c4e2a7 | yes |
| gap | PASS | 9c4e2a7 | yes |
| security | not reviewed | - | - |
| outcome | not reviewed | - | - |

| Read closely | Files | Note |
|---|---|---|
| most-harm | `src/auth/session/cookie.ts` | Sets the flags for every session. |
| no-check | `src/audit/log/write.ts` | Dropping the oldest row when the queue is full trades audit completeness for sign-in latency. |
| unchecked | - | No security or outcome review ran. |
| unchecked | `src/auth/session/refresh.ts` | The code review marked it not reviewed. |
| unchecked | - | `npm run test:e2e` was skipped. |
| after-review | `src/audit/log/write.ts` | The queue bound landed after the review at `9c4e2a7`. |

Undo: reverting the merge restores the old cookie code, but sessions issued meanwhile keep their flags until they expire, and the audit rows written stay.

</details>
