# Testing Strategy

<!-- What is true of THIS project's tests. Commands live in AGENTS.md
     § Key Development Commands – link them, never copy them. -->

Commands: see `AGENTS.md` § Key Development Commands → Testing (`fast`, `full`, run one test).

AndThen ships prompts, not an application. What is testable is a contract stated in shipped text and the Python 3 stdlib scripts that enforce it – no app to start, no browser, no service.

## Levels In Use

| Level | Applies to | Lives in |
|-------------|------------|----------|
| Unit | Pure logic: `tracker.py` payload assembly, the word-budget rules, cookbook/README invocation extraction | `tests/test_*.py` |
| Integration | A script driven through `subprocess` over a real temp-dir repo – real files, real exit codes; the eval harness through `run.py`'s own seams | `tests/test_*.py`, `evals/test_checks.py` |
| E2E | Not run as tests. Closest: the install checks (`install-skills.sh --validate-only`, `--claude-user --dry-run`) and the live evals (`evals/README.md`) | – |

Code that writes files or shells out is tested through the process boundary with a real temp tree, because a mocked filesystem proves the mock.

## Framework and Fixture Conventions

- **Stdlib `unittest` only**, no pytest: the scripts ship in the plugin and must run on ubuntu, macOS, and Windows with nothing installed.
- **One test file per script, in `tests/`**, never in `plugin/` – both hosts install `plugin/` wholesale, so a test there ships. A file puts its script's directory on `sys.path`; a hyphenated script name (`audit-cookbook.py`) loads via `importlib.util`. `evals/test_checks.py` stays beside the POSIX-only harness it proves; CI skips it on Windows.
- **Fixtures**: committed inputs in `scripts/fixtures/renders/`, one real-shaped artifact per type. One-off input goes in a `tempfile.mkdtemp()` tree, never the repo.
- **Prompt-contract tests** gate shipped text: a fixture holding the prose, the gate's own regex imported by name (never copied), and a docstring stating what the pair proves. Assert both directions – the pattern fires on the prose it replaced and not on the replacement – because a gate that flags its own fix gets switched off.
- **Eval harness tests drive the runner, never a re-implementation.** Each acceptance boundary is asserted in both directions: a case shape refused before dispatch and its valid counterpart; a judge PASS that must quote retained material and the absence-based FAIL; a failing check that still reaches the judge. Case `oracle.py` files are proved on staged workspaces (all but `exec-plan`). `SubjectAppTest` keeps the subject app's suite green and its tree silent about the harness.

## What Must Have a Test Before Merge

Sized to an experimental release candidate with one maintainer: the `fast` tier green on every change, the `full` tier before a merge to `develop`, and the live `eval full` before a release.

- **Highest risk, always tested:** the shipped `tracker.py` (it writes to a user's issue tracker) and `scripts/install-skills.py` (its rewrites reach every loose-skill install). A behavior change in either comes with a test of that behavior.
- Every release-check assertion (e.g. `scripts/audit-cookbook.py`), proved to fire on synthetic input, not only to pass on the live tree – an assertion never shown to fire is a non-catch.
- Every shipped script's refusal path: exit code, message, and that nothing was written.
- **Test-first for script defects:** a bug in any script gets a failing test before the fix (Prove-It). Prompt text has no executable behavior; its gate is a prompt-contract test where one exists, otherwise the evals.
- **No coverage gate** – stdlib only, no coverage tool, and the suites are small enough to review whole.
- **No quarantine.** A flaky test in `tests/` or `evals/test_checks.py` is made deterministic before merge; the suites run offline, so flakiness is a bug in the test. Live eval cells vary by design – compare runs, never read one cell as a verdict on a rule change.

## Known Gotchas

- A script that greps the tree for patterns it polices matches its own source, so it skips its own file.
- `bash scripts/install-skills.sh` without a flag conflicts with the local Codex plugin; only `--validate-only` and `--claude-user --dry-run` are safe.
- The shipped-surface budget (`tests/surface-budget.json`) counts words, so an equal-length rewrite passes – it catches accretion, not a bad instruction.
