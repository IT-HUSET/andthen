# Report Annotation Mechanics

The two marks Phase 5 writes into the input report: the `## Remediation Status` section and the `**Remediated**:` header line. Both are exact, so a re-run on the same report never duplicates them.

- **Replace the section when it exists**: find the LAST line that starts at column 0 with `## Remediation Status` and is not inside a fenced code block, and overwrite from that line to EOF.
- **Append it otherwise**, with a leading blank line.
- **One bullet per finding, in the report's finding order**: `- **Finding {N} - {title}** - {STATUS} - {one-line evidence or justification}`.
  - `{N}` is the report's finding number, so a reader joins each bullet to its finding. A report that numbers no findings gets `**{finding title or short quote}**` instead.
  - `{STATUS}` is the Phase 4 re-check status: `RESOLVED`, `PARTIALLY RESOLVED`, `UNRESOLVED`, `DEFERRED`, or `SURFACED`.
  - A `SURFACED` justification names the upstream route as `routed Note`, never as a `Routing:` tag, which a parser would read as the finding's own. Otherwise it names the Phase 2 Intent anchor or reading, or the unattended recommendation against the finding.
- **Header marker, written once**: a reader meets the report's bold-label header under the H1 before the verdict these fixes have overtaken. Append this line to that header, verbatim, unless it already carries a `**Remediated**:` line. A report with no such header gets no marker.

  ```markdown
  **Remediated**: fixes applied after this verdict – see `## Remediation Status`
  ```

  It carries no counts and no verdict: a count goes stale on the next pass, and only a review issues a verdict.
