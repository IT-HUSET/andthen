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
| shipped-surface words | `find plugin -name '*.md' ! -name README.md ! -path '*/templates/agents/copilot/*' -print0 \| xargs -0 cat \| wc -w` | The count `tests/surface-budget.json` caps, equal to the test's `surface_words()`. Use it instead of an inline script, which the repo hook blocks |
| plan check | `python3 evals/validate_plan.py docs/temp/specs/<feature>/plan.json` | Stdlib schema check of one `plan.json`: `OK:` or one `ERROR:` line per violation; `jsonschema` is not installed |

- Run `bash scripts/install-skills.sh` only with a flag here, because bare it conflicts with the local Codex plugin. `--validate-only` and `--claude-user --dry-run` install nothing; run the latter on its own when you touch user-tier packaging.
- To refresh your own installs from this checkout, run `python3 scripts/andthen-plugins.py --path .` (`--claude-only`, `--codex-only`, `--dry-run` narrow it), never a copy under another plugin name, because the name is the `andthen:` namespace and a renamed copy's skills call the installed release's. It uninstalls and reinstalls on both hosts and diffs the cache against `plugin/`, because both hosts cache by version and an in-place update keeps the stale copy. It skips plugins the manifest no longer lists and what `init` copied into your home folder (output style, role agents, critical rules).
- Read `evals/README.md` before running an eval or authoring a case, and `AGENTS.md` § General Principles for the Codex gate and the no-edit rule while a tier runs.

## Release

Run with the user present: step 4 is a `git push`, an `ask` rule on purpose, and an unattended one has waited hours for approval.

1. Bump the version in the four places `AGENTS.md` § Plugin manifests names, unless the branch's first commit already did, and set `## [<version>]` in `CHANGELOG.md` to `## [<version>] – <date>`, with the date from `date +%Y-%m-%d` at tag time (rename `## [Unreleased]` if that is still the heading). Run the `full` tier, then commit titled `<version>`.
2. Update your installs on both hosts with the refresh command above and restart sessions: both cache by version, so a session otherwise loads the previous release's skills.
3. Squash the branch onto `develop`: `git fetch origin`, then `git commit-tree 'HEAD^{tree}' -p origin/develop -m <version>` prints `<sha>`, and `git tag -a v<version> -m <version> <sha>`.
4. Last, `git push origin <sha>:refs/heads/develop v<version>`. A release (no `-rc.N`) adds `<sha>:refs/heads/main` to that push: `main` only ever moves to a commit on `develop`, so it fast-forwards with no force, and a rejected `main` means something landed on `main` alone.
