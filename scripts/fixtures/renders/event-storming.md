# Event Storming: Sign-in and Audit (Big Picture)

## Executive Summary

One pivotal event – `SessionIssued` – separates credential handling from everything downstream. The audit trail hangs off it, and so does the open question about refresh.

## Event Timeline

- `CredentialsSubmitted` – Visitor
- `CredentialsValidated` – Sign-in handler
- `SessionIssued` (pivotal) – Sign-in handler
- `SignInRecorded` – Audit writer

## Hotspots

- Refresh issues a session without emitting `SessionIssued`, so the audit trail has a hole nobody has named.

## Subdomain Candidates

- **Session issuance** – clusters on `SessionIssued`.
- **Authentication audit** – clusters on `SignInRecorded`.

## Recommended Next Steps

- `andthen:architecture --mode strategic-design` – the two candidates are ready to be drawn as contexts.
