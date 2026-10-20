# Key Development Commands

AndThen has no build step – it is a skill bundle.

## Testing

Run from the repo root. `{file}` is a dotted module path (not a slash path); `{test}` is `Class.method`.

| Tier | Command | Description |
|------|---------|-------------|
| fast | `python3 -m unittest discover -s tests && python3 evals/test_checks.py && bash scripts/install-skills.sh --validate-only` | Per-change gate – every `tests/` suite including the shipped-surface word budget, the evals checks, and the install-clean check |
| full | `python3 -m unittest discover -s tests && python3 evals/test_checks.py && bash scripts/install-skills.sh --validate-only && python3 scripts/audit-cookbook.py && bash scripts/install-skills.sh --claude-user --dry-run` | Before a release or merge – the fast tier plus the CI release checks (cookbook/README invocations) and the user-tier packaging preview |
| run one test | `python3 -m unittest {file}.{test}` | One test, e.g. `python3 -m unittest tests.test_audit_cookbook.FiringTest.test_missing_skill_fires` |
| eval smoke | `python3 -m evals.run smoke --provider both --jobs 5` | Live run, a few minutes: seven cells under the 300 s smoke bar on both hosts. Ask first; needs `dartclaw-workflow` (DartClaw 0.26.1 or later), `claude`, `codex` on PATH, subscription credentials |
| eval full | `python3 -m evals.run full --provider both --jobs 5` | Live run before a release: every case on Claude plus smoke on Codex. Case names in place of a tier run just those |

- Run `bash scripts/install-skills.sh` only with a flag here, because bare it conflicts with the local Codex plugin. `--validate-only` and `--claude-user --dry-run` install nothing; run the latter on its own when you touch user-tier packaging.
- To refresh your own installs from this checkout, run `python3 scripts/andthen-plugins.py --path .` (`--claude-only`, `--codex-only`, `--dry-run` narrow it). It uninstalls and reinstalls on both hosts and diffs the cache against `plugin/`, because both hosts cache by version and an in-place update keeps the stale copy. It skips plugins the manifest no longer lists and what `init` copied into your home folder (output style, role agents, critical rules).
- Read `evals/README.md` before running an eval or authoring a case, and `AGENTS.md` § General Principles for the Codex gate and the no-edit rule while a tier runs.
