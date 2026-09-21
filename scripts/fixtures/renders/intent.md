# Intent: Session Hardening

## Scope

### In Scope
- Cookie flag policy.

### Out of Scope
- Session revocation UI.

### Deferred
- Device fingerprinting.

### Not Doing
- Third-party identity federation.

## Design Decisions

### Design Space Decomposition

```
Session hardening
├── Cookie policy
│   ├── Fixed flags (chosen)
│   └── Per-environment overrides
└── Audit trail
    ├── Synchronous write (chosen)
    └── Fire-and-forget
```

### Cross-Consistency Notes

- Per-environment overrides are incompatible with a single stated policy.
- Fire-and-forget audit conflicts with the reviewer's reconstruct-an-incident need.

### Resolved Decisions

| Dimension | Choice | Rationale |
|---|---|---|
| Cookie flags | Fixed set, no overrides | The two call sites drifted precisely because the flags were caller-supplied; a fixed helper removes the seam rather than documenting it. |
| Audit write | Awaited before the response | A reviewer reconstructing an incident needs the row to exist whenever the response says the sign-in succeeded. |

## Edge Cases

| Scenario | Expected Behavior |
|---|---|
| Audit store unavailable | Buffered write, sign-in still succeeds |

## Success Criteria

- [x] Every issued session cookie carries the full flag set
- [ ] Every sign-in attempt has an audit row

## Decisions Log

| Decision | Rationale | Date |
|---|---|---|
| Fixed cookie flags | Removes the drift seam | 2026-08-28 |

## Open Questions

- Does the refresh path need its own event kind?
