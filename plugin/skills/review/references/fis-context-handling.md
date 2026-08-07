# FIS Upstream-Context Handling

Shared handling rules for the `doc` and `gap` lenses when a FIS is in scope.

When a FIS is in scope:

- Resolve anchored `Required Context` by probing repo root and FIS directory; one match wins, zero/two distinct matches are broken/ambiguous. Conflict with FIS Intent/Outcomes is spec-stale.
- Treat source-pinned inline fallbacks/legacy blocks as authoritative snapshots; source drift is a re-spec finding, not an invitation to rewrite.
- Read `Deeper Context` only when load-bearing for a finding; warn on a broken followed anchor.

Absence is valid when no upstream source is load-bearing. For older FIS files, fall back to `## References & Constraints`, its `### Documentation & References` table, or prose mentions; do not require migration.
