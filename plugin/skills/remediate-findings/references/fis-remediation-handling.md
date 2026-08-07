# FIS Remediation Handling

Minimal-fix discipline for remediation targets that include a Feature Implementation Specification (FIS).

- **Anchored `Required Context`**: broken targets and substantive source/FIS conflicts route to a re-spec Note; remediation does not mutate FIS spec content.
- **Source-pinned inline fallbacks/legacy blocks** remain authoritative – do not refresh or migrate them opportunistically.
- **`Deeper Context` anchors**: route broken targets to a re-spec Note; don't delete silently.
- **Legacy FIS fallback**: apply the same minimal-fix discipline to old reference tables or prose mentions; don't migrate them opportunistically.
