# Project Learnings

## Platform Traps

- **A report file open in a spreadsheet blocks the rewrite**: on Windows the write fails with `PermissionError` while the previous report is open, which is why `export.write_report` is called through `retry` – the failure is transient, not a bad path.
- **`amount` arrives with padding**: ledgers exported from the finance system pad every cell, so a row is stripped cell by cell before `int()` sees it.

## Process & Tooling

- **Tiers run from the repository root only**: `src.reporter` resolves through the working directory, so a tier started from `tests/` fails on import rather than on a test.
- **A helper added to `text_tools` stays pure**: the module touches no files and imports nothing from the package, so a new helper is proved by calling it rather than by running the command line.
