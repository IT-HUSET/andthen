# FIS Remediation Handling

Minimal-fix discipline for remediation targets that include a Feature Implementation Specification (FIS).

- **`Required Context`** blocks are inlined verbatim at spec time and are authoritative – do not "fix" by re-fetching against the current source (that silently changes the executor's contract). Drift is a re-spec signal; escalate to the `andthen:spec` skill if fresh content is required.
- **`Deeper Context` anchors**: for a broken anchor, repair the anchor – don't delete silently.
- **Legacy FIS fallback**: apply the same minimal-fix discipline to whatever upstream-reference structure the legacy FIS uses (old `## References & Constraints` heading, `### Documentation & References` table, or prose mentions). Don't migrate a legacy FIS to the new sections opportunistically – that's a re-spec, not a remediation.
