# Report Annotation Mechanics

Exact mechanics for the two marks Phase 5 writes into the input report: the `## Remediation Status` section and the `**Remediated**:` header line. Overwrite-vs-append and write-once must be exact, so re-running on the same report never accumulates duplicates.

- **Whole-section replace if the heading already exists**: locate the LAST line that starts at column 0 with `## Remediation Status` and is not inside a fenced code block; overwrite from that line to EOF. This leaves exactly one `## Remediation Status` H2 after a re-run (single-H2 idempotency).
- **Append otherwise**: when no such heading exists, append the section with a leading blank line.
- **One bullet per finding, in the original report's finding order**: `- **{finding title or short quote}** – {STATUS} – {one-line evidence or justification}` where `{STATUS}` is one of `RESOLVED` / `PARTIALLY RESOLVED` / `UNRESOLVED` / `DEFERRED` / `SURFACED` from the Phase 4 findings re-check. `SURFACED` entries include the upstream `Routing:` tag and/or the Phase 2 Intent-anchor citation in the justification.
- **Header marker, written once**: a reader meets the report's bold-label header under the H1 before the verdict these fixes have overtaken. Append this line to that header, verbatim, unless it already carries a `**Remediated**:` line; a report with no such header gets no marker.

  ```markdown
  **Remediated**: fixes applied after this verdict – see `## Remediation Status`
  ```

  It carries no counts and no verdict: a count goes stale on the next pass, and only a review issues a verdict.
