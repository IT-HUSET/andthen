# Key Development Commands

AndThen has no build step – it is a skill bundle.

## Testing

Run from the repo root. `{file}` is a dotted module path (not a slash path); `{test}` is `Class.method`.

| Tier | Command | Description |
|------|---------|-------------|
| fast | `python3 -m unittest discover -s tests && python3 evals/test_checks.py && python3 scripts/validate-plugin.py` | Per-change gate – every `tests/` suite including the shipped-surface word budget, the evals checks, and the plugin content check |
| full | `python3 -m unittest discover -s tests && python3 evals/test_checks.py && python3 scripts/validate-plugin.py && python3 scripts/audit-cookbook.py && python3 scripts/andthen.py install --loose --dry-run --skills-dir .agent_temp/loose-preview` | Before a release or merge – the fast tier plus the CI release checks (cookbook/README invocations) and the loose-skill packaging preview |
| run one test | `python3 -m unittest {file}.{test}` | One test, e.g. `python3 -m unittest tests.test_audit_cookbook.FiringTest.test_missing_skill_fires` |
| eval smoke | `python3 -m evals.run smoke --provider both --jobs 5` | Live run, a few minutes: seven cells under the 300 s smoke bar on both hosts. Ask first; needs `dartclaw-workflow` (DartClaw 0.26.1 or later), `claude`, `codex` on PATH, subscription credentials |
| eval full | `python3 -m evals.run full --provider both --jobs 5` | Live run before a release: every case on Claude plus smoke on Codex. Case names in place of a tier run just those |
| shipped-surface words | `find plugin -name '*.md' ! -name README.md ! -path '*/templates/agents/copilot/*' -print0 \| xargs -0 cat \| wc -w` | The count `tests/surface-budget.json` caps, equal to the test's `surface_words()`. Use it instead of an inline script, which the repo hook blocks |
| plan check | `python3 evals/validate_plan.py docs/temp/specs/<feature>/plan.json` | Stdlib schema check of one `plan.json`: `OK:` or one `ERROR:` line per violation; `jsonschema` is not installed |

- Run `python3 scripts/andthen.py install --loose` only with `--skills-dir` or `--dry-run` here: bare, it refuses while the local Codex plugin is installed, and it would otherwise write into `~/.agents/skills`. `validate-plugin.py` and the `--dry-run` preview write nothing; run the preview on its own when you touch loose-skill packaging.
- To refresh your own installs from this checkout, run `python3 scripts/andthen.py install` (`--claude-only`, `--codex-only`, `--copilot-only` narrow it, `--dry-run` previews it), never a copy under another plugin name, because the name is the `andthen:` namespace and a renamed copy's skills call the installed release's. It uninstalls and reinstalls on every host it finds and diffs the cache against `plugin/`, because Claude Code and Codex cache by version and an in-place update keeps the stale copy. It places nothing in your home folder beyond the plugin unless you pass `--roles`, `--rules`, or `--trust` (role agents, critical rules, Codex trust in `config.toml`); the output style stays `init`'s.
- Read `evals/README.md` before running an eval or authoring a case, and `AGENTS.md` § General Principles for the Codex gate and the no-edit rule while a tier runs.

## Release

Publish with the user's authorization; a push without it has waited hours for approval in an unattended run.

1. Bump the version per § Version bump below, unless the branch's first commit already did, and set `## [<version>]` in `CHANGELOG.md` to `## [<version>] – <date>`, with the date from `date +%Y-%m-%d` at tag time (rename `## [Unreleased]` if that is still the heading). Run the `full` tier, then commit titled `<version>`.
2. Update your installs on every host with the refresh command above and restart sessions: Claude Code and Codex cache by version, so a session otherwise loads the previous release's skills.
3. Open the feature branch's pull request into `develop`, wait for its checks, and squash-merge with title `<version>` and a message pointing to its CHANGELOG section.
4. Run `git fetch origin`, then tag the merged commit with `git tag -a v<version> -m <version> <sha>`, where `<sha>` is the squash merge's commit, and publish it with `git push origin v<version>`.
   Leave `main` in place while real users test the tagged version on `develop`.

After the maintainer accepts that testing, fetch origin and verify the tagged commit contains `origin/main` and belongs to `origin/develop` with `git merge-base --is-ancestor origin/main 'v<version>^{commit}'` and `git merge-base --is-ancestor 'v<version>^{commit}' origin/develop`.
Promote that exact commit with `git push origin 'v<version>^{commit}:refs/heads/main'`.
A rejected fast-forward means `main` holds work the tested commit lacks; integrate it and test a new version rather than moving the tag or forcing the push.

A patch whose pull request targets `main` (`AGENTS.md` § Git Remotes) replaces steps 3–4.
Its version bump and dated `CHANGELOG.md` heading go in the pull request, dated the day you merge and tag, because nothing is committed to `main` outside one.
Once it merges, `git fetch origin`, then `git tag -a v<version> -m <version> origin/main`, then `git push origin v<version>`.
Last, carry `develop` onto that commit: `git push origin origin/main:refs/heads/develop` where the two refs were level, else `git merge origin/main` on `develop` and push the result, because a `develop` holding its own pre-release work cannot be fast-forwarded.

### Version bump

A version bump is one commit titled with the version.
It sets the version in `CHANGELOG.md`, the `andthen` entry of `.claude-plugin/marketplace.json`, and both `plugin.json` files (`plugin/.claude-plugin/plugin.json`, `plugin/.codex-plugin/plugin.json`); `.agents/plugins/marketplace.json` carries none.
It opens `## [<version>]` in `CHANGELOG.md`, renaming `## [Unreleased]` when present.
CI fails on skew and reads only the first bracketed semver in `CHANGELOG.md`, so the heading's date can wait for the tag.
A pre-release bump renames its release's one cumulative section to `## [<version>-rc.N]` instead of opening another, and the release renames it `## [<version>] – <date>`.
