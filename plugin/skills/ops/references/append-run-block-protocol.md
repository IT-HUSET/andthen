# Append-Run Block Protocol

Applies to the `observations`, `discovered-requirements`, `design-change`, and `update-tech-debt append` forms. `<markdown-body>` is freeform multi-line markdown passed verbatim – quote characters in the invocation (`'...'` / `"..."`) are illustrative framing, not delimiters; do not strip or shell-escape. Each form names its own tag suffix, target section, and body-constraint variant – the following protocol is common to all four:

- **Empty/whitespace-only body**: no-op; do not append a run block and do not create the target file (for `update-tech-debt append`).
- **Body constraints**: `<markdown-body>` MUST use `####`-or-deeper headings only. The body MUST NOT contain `## ` headings or another `### Run:` line – these would visually close the section and break the append protocol.
- **Placeholder removal**: if the placeholder line `_No observations recorded yet._` or `_No tech debt recorded yet._` is present in the target section, remove it (exact-string match only; no-op otherwise).
- **Timestamp resolution**: resolve a timestamp via `date -u +"%Y-%m-%d %H:%M UTC"` so all run blocks share a single timezone and ordering is unambiguous.
- **Whitespace normalization**: ensure exactly one blank line precedes the new run block and the previous block ends with a trailing newline.
- **Run-block frame**: append the run block tagged with the form's own suffix:
  ```
  ### Run: {YYYY-MM-DD HH:MM UTC} – {tag}

  {markdown-body}
  ```
- **Append-only**: never rewrite or remove prior `### Run:` blocks.
- **Idempotent retry** (2-minute window): if the most recent existing `### Run: ... – {tag}` block (matched by tag suffix) has identical body content (whitespace-normalized; for `update-tech-debt append` compare the per-severity filtered body against the matching severity block, not the full body) AND its timestamp is within 2 minutes of the resolved timestamp, no-op for that block. Compare only against same-tag blocks – an intervening block with a different tag suffix does not affect the decision.
