# ADR-014: Fixed session cookie flags

**Status:** accepted
**Date:** 2026-08-28
**Deciders:** platform, security
**Related:** ADR-009

## Context

Two call sites issued session cookies and disagreed on `SameSite`, because the flag set was a caller-supplied argument. Prior art: ADR-009 fixed the cookie name for the same reason.

## Decision

Session cookies are rendered by one helper with a fixed flag set. Callers pass the session id and nothing else.

## Alternatives Considered

### Per-environment override map

Keeps a local escape hatch for staging, and reintroduces exactly the argument that let the two call sites drift.

### Lint rule over the existing call sites

Detects drift after it is written rather than making it unwritable, and does not survive a new call site added in a file the rule does not cover.

## Consequences

### Positive
- The policy is stated once and cannot be varied per call site.

### Negative
- A genuine environment difference now requires an ADR amendment, not a config edit.

### Neutral
- The helper is one more module on the sign-in path.
