# Visual Review Handling (`--visual` / `VISUAL_MODE`)

Visual review is a **post-filter handoff**: complete the report/filter gate (Phase 3) first, then hand the produced report to the `andthen:visualize` skill, which owns rendering, note export, browser-open, and `.agent_temp/visual-review/`. In `AUTO_MODE`, run this only when `--visual` is set.

- **Mode support**: supported for every mode except pure `advise` – `advise` has no structured report template, so it is a no-op with a one-line note, not a generic renderer.
- **Multi-mode chains**: the visualizer dispatches first-match-wins on one artifact type per file. Print a one-line warning naming the active mode's renderer; other sections fall to Generic Prose. Re-run per-mode with `--output-dir` for fidelity.
