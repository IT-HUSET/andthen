# Legacy `plan.md` Migration (Step 1.3)

Local-output-mode migration for the `andthen:plan` skill. Fires when `OUTPUT_DIR/plan.json` is absent and `OUTPUT_DIR/plan.md` is present – including the `--issue` rerun case, when `OUTPUT_DIR` already carries a legacy `plan.md` from a prior run.

Parse the legacy Story Catalog (markdown contract per [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md)), build the in-memory plan per *The Plan Schema*, and hold it for Step 4:

- Map legacy statuses per the **Migration from legacy `plan.md`** section of *The Plan Schema*. Unrecognized values (e.g. `Retired`) → `"skipped"` with a durable `executionNotes` annotation: `Migrated from legacy plan.md: status "<old>" mapped to "skipped" for stories <id-list>.`
- Preserve `fis` paths and statuses for rows whose `FIS` cell points at an existing file. FIS-unset rows get `fis: null`, `status: "pending"`.
- After Step 4's `plan.json` write, emit: `Migrated plan.md → plan.json. plan.md is no longer consumed; delete when ready.` Do not auto-delete `plan.md`.
