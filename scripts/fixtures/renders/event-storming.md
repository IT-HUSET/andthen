# Event Storming: Sign-in and Audit (Big Picture)

## Executive Summary

One pivotal event – `SessionIssued` – separates credential handling from everything downstream. The audit trail hangs off it, and so does the open question about refresh.

## Event Timeline

- `CredentialsSubmitted`
- `CredentialsValidated`
- `SessionIssued` (pivotal)
- `SignInRecorded`

## Commands and Actors

| Command | Actor |
|---|---|
| Submit credentials | Visitor |
| Issue session | Sign-in handler |
| Record sign-in | Audit writer |

## Policies and Read Models

- **Policy**: whenever `SessionIssued`, record the attempt.
- **Read model**: recent sign-ins per user, built from `SignInRecorded`.

## Hotspots

- Refresh issues a session without emitting `SessionIssued`, so the audit trail has a hole nobody has named.

## Subdomain Candidates

- **Session issuance** – clusters on `SessionIssued`.
- **Authentication audit** – clusters on `SignInRecorded`.

## Recommended Next Steps

- `andthen:architecture --mode strategic-design` – the two candidates are ready to be drawn as contexts.
