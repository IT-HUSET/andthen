# Testing Strategy

<!-- What is true of THIS project's tests. Commands live in
     docs/KEY_DEVELOPMENT_COMMANDS.md – link them, never copy them. -->

Commands: see `docs/KEY_DEVELOPMENT_COMMANDS.md` § Testing (`fast`, `full`, run one test).

AndThen ships prompts, not an application. What is testable is a contract stated in shipped text and the repo's Python 3 stdlib scripts that enforce it – no app to start, no browser, no service.

## Levels In Use

| Level | Applies to | Lives in |
|-------------|------------|----------|
| Unit | Pure logic: the word-budget rules, cookbook/README invocation extraction | `tests/test_*.py` |
| Integration | A script driven through `subprocess` over a real temp-dir repo – real files, real exit codes; the eval harness through `run.py`'s own seams | `tests/test_*.py`, `evals/test_checks.py` |
| E2E | Not run as tests. Closest: the install checks (`scripts/validate-plugin.py`, `andthen.py install --loose --dry-run`), the live evals (`evals/README.md`), and the live GitHub check below | – |

Code that writes files or shells out is tested through the process boundary with a real temp tree, because a mocked filesystem proves the mock.

## Framework and Fixture Conventions

- **Stdlib `unittest` only**, no pytest: the scripts must run on ubuntu, macOS, and Windows with nothing installed.
- **One test file per script, in `tests/`**, never in `plugin/` – every host installs `plugin/` wholesale, so a test there ships. A file puts its script's directory on `sys.path`; a hyphenated script name (`audit-cookbook.py`) loads via `importlib.util`. `evals/test_checks.py` stays beside the POSIX-only harness it proves; CI skips it on Windows.
- **Fixtures**: committed inputs in `scripts/fixtures/renders/`, one real-shaped artifact per type. One-off input goes in a `tempfile.mkdtemp()` tree, never the repo.
- **Prompt-contract tests** gate shipped text: a fixture holding the prose, the gate's own regex imported by name (never copied), and a docstring stating what the pair proves. Assert both directions – the pattern fires on the prose it replaced and not on the replacement – because a gate that flags its own fix gets switched off.
- **Eval harness tests drive the runner, never a re-implementation.** Each acceptance boundary is asserted in both directions: a case shape refused before dispatch and its valid counterpart; a judge PASS that must quote retained material and the absence-based FAIL; a failing check that still reaches the judge. Case `oracle.py` files are proved on staged workspaces (all but `exec-plan`). `SubjectAppTest` keeps the subject app's suite green and its tree silent about the harness.

## What Must Have a Test Before Merge

Sized to one maintainer: the `fast` tier green on every change, the `full` tier before a merge to `develop` or `main`, and the live `eval full` before a release.

- **Highest risk, always tested:** `scripts/andthen_loose.py`, because its rewrites reach every loose-skill install, and `scripts/andthen.py`, because it writes into the user's host homes. A behavior change in it comes with a test of that behavior.
- Every release-check assertion (e.g. `scripts/audit-cookbook.py`), proved to fire on synthetic input, not only to pass on the live tree – an assertion never shown to fire is a non-catch.
- Every script's refusal path: exit code, message, and that nothing was written.
- **Test-first for script defects:** a bug in any script gets a failing test before the fix (Prove-It). Prompt text has no executable behavior; its gate is a prompt-contract test where one exists, otherwise the evals.
- **No coverage gate** – stdlib only, no coverage tool, and the suites are small enough to review whole.
- **No quarantine.** A flaky test in `tests/` or `evals/test_checks.py` is made deterministic before merge; the suites run offline, so flakiness is a bug in the test. Live eval cells vary by design – compare runs, never read one cell as a verdict on a rule change.

## Live GitHub Check

The evals run the tracker through a Local backend's Operation Table (`tools/issues.py`), so no eval runs a `gh` command the `tracker` skill spells.
Those are the GitHub mapping under its Argv-safe rule, `list issues` in § Find them, and triage's `gh label create`.
Run this check before merging a change to one of them, and ask first, because it writes issues.

- **Target**: `IT-HUSET/andthen-sandbox`, private and disposable.
  Work from a scratch project under `.agent_temp/` whose only remote is the sandbox, and pass `--repo IT-HUSET/andthen-sandbox` on every hand-run `gh` call.
- **By hand**: each changed command, its failure exit included.
- **End to end**: copy `evals/cases/tracker-publish/overlay/docs/specs/ledger-hygiene/` into the scratch project, create an issue carrying the PRD's request, and set the PRD header's `#1` to its number, because the sandbox's #1 is closed.
  Then have a fresh subagent run `tracker publish <plan.json> --auto` twice, then `--only S01` with S01 set `done`.
  It passes when the first run takes the new issue as parent and creates the children with their sub-issue and blocked-by links, the second writes nothing, and `--only` changes only S01's checklist entry and child.
- **Compare snapshots of bodies, links, and timeline events**, never `updatedAt` alone, because a link write leaves `updatedAt` as it was.
- **Close every issue the check created; delete none.**

GitHub facts the skill relies on without saying them, from the 2026-11-23 run (gh 2.103.3):

- Re-adding an existing parent or blocked-by link exits 1, so the skill's read-before-add rule is what keeps a rerun from reporting false failures.
- GitHub links closed issues freely, so only the skill's own rule keeps a publish off them.
- Search lists a new issue about 4 s after its create.
- Create caps a body at 65,536 characters; edit accepts more.

`ship`'s `gh pr create` and `gh issue view` calls have not been run here.

## Known Gotchas

- A script that greps the tree for patterns it polices matches its own source, so it skips its own file.
- `python3 scripts/andthen.py install` without `--dry-run` reinstalls the plugin and `--loose` writes into `~/.agents/skills`, both on the real home. Tests pass a temp `HOME` or `--skills-dir`, and by hand only `scripts/validate-plugin.py` and `--dry-run` are safe.
- On Windows:
  - a bare `bash` in `subprocess.run` resolves to the System32 WSL stub, so resolve it with `shutil.which("bash")`;
  - the default read encoding is cp1252, so pass `encoding=` on every read;
  - user files arrive CRLF, so normalise `\r\n` before hashing bytes or `$`-anchoring.
- The shipped-surface budget (`tests/surface-budget.json`) counts words, so an equal-length rewrite passes – it catches accretion, not a bad instruction.
