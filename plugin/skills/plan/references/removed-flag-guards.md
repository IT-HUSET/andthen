# Removed-Flag Guards (Step 1.0)

Flag-combination guard for the `andthen:plan` skill. Enforced up-front in Step 1.0, before any I/O. Each reject block prints the verbatim `Error:` (interactive) or emits the verbatim `BLOCKED:` line and exits (`AUTO_MODE`).

- `--skip-specs`: reject. Print `Error: --skip-specs was removed. Run andthen:plan on the directory to create or resume the full local bundle, or use --to-issue for GitHub issue output without local FIS files.` and stop. `AUTO_MODE`: emit `BLOCKED: --skip-specs was removed; rerun andthen:plan to create/resume the full bundle or use --to-issue` and exit.
- `--stories` or `--phase`: reject. Print `Error: --stories and --phase were removed. Run andthen:plan on the directory to fill all missing FIS files, or use andthen:spec story <id> of <plan.json> for a one-off story spec.` and stop. `AUTO_MODE`: emit `BLOCKED: --stories/--phase were removed; rerun andthen:plan to fill all missing FIS files` and exit.
- `--create-story-issues` without `--to-issue`: reject. Print `Error: --create-story-issues requires --to-issue (granular GitHub mode is meaningless without GitHub output).` and stop. `AUTO_MODE`: emit `BLOCKED: --create-story-issues requires --to-issue` and exit.
