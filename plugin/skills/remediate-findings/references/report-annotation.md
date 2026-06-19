# Report Annotation Mechanics

Deterministic byte-level mechanics for writing the `## Remediation Status` section into the input report (Phase 5). The single-H2 invariant is counter-intuitive on re-run – overwrite-vs-append must be exact so re-running on the same report never accumulates duplicate sections.

- **Whole-section replace if the heading already exists**: locate the LAST line that starts at column 0 with `## Remediation Status` and is not inside a fenced code block; overwrite from that line to EOF. This leaves exactly one `## Remediation Status` H2 after a re-run (single-H2 idempotency).
- **Append otherwise**: when no such heading exists, append the section with a leading blank line.
- **One bullet per finding, in the original report's finding order**: `- **{finding title or short quote}** – {STATUS} – {one-line evidence or justification}` where `{STATUS}` is one of `RESOLVED` / `PARTIALLY RESOLVED` / `UNRESOLVED` / `DEFERRED` / `SURFACED` from the Phase 4 findings re-check. `SURFACED` entries include the upstream `Routing:` tag and/or the Phase 2a Intent-anchor citation in the justification.
