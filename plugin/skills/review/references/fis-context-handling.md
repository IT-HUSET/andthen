# FIS Upstream-Context Handling

Shared handling rules for the `doc` and `gap` lenses when a FIS is in scope.

When a FIS is in scope: treat `Required Context` blocks as the authoritative upstream intent – do not re-read source documents just to reconfirm inlined content. For `Deeper Context` anchors that are load-bearing for a finding, verify the anchor resolves in the source and warn (do not stop) on broken anchors. If a `Required Context` block appears to no longer match the current source, that is a doc-review finding (MEDIUM by default – spec should be re-run against the updated source), not an execution blocker.

**Legacy FIS fallback**: a FIS without `Required Context` / `Deeper Context` sections predates them. Fall back to whatever upstream-reference structures it uses: the old `## References & Constraints` heading and its `### Documentation & References` table (rows typed `file|doc|url|wire`), or prose mentions. Do not flag the absence of these sections as a defect on legacy FIS files.
