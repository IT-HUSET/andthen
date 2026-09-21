# Testing Strategy

<!-- What is true of THIS project's tests. Commands live in AGENTS.md
     § Key Development Commands – link them, never copy them. -->

Commands: see `AGENTS.md` § Key Development Commands → Testing (`fast`, `full`, run one test).

AndThen ships prompts, not an application, so most of what is testable is a *contract stated in shipped text* plus the Python 3 stdlib scripts that enforce it. There is no application to start, no browser, and no service to stand up.

## Levels In Use

| Level | Applies to | Lives in |
|-------------|------------|----------|
| Unit | `tracker.py` payload assembly, the budget measurement rules, the cookbook/README invocation extraction | `tests/test_*.py` |
| Integration | A script driven end to end over a real temp-dir repo – `subprocess` against it, real files, real exit codes | the same `test_*.py` files, in temp-dir cases |
| E2E | Not run. The install channels are the closest thing: `install-skills.sh --validate-only` and `--claude-user --dry-run` | `scripts/install-skills.py` |

Placement follows the trust boundary crossed. A pure projection over parsed JSON is a unit test; code that writes a file or shells out is exercised through the process boundary with a real temp tree, because mocking the filesystem here proves the mock.

## Framework and Fixture Conventions

- Python 3 stdlib `unittest` only – no pytest, no third-party runner. The scripts ship inside the plugin and must run on `ubuntu` / `macos` / `windows-latest` with nothing installed.
- Test files live in `tests/`, one per script they prove (`tests/test_tracker.py` for `tracker.py`), never inside `plugin/`: both hosts install the plugin directory wholesale with no exclude list, so a test beside a shipped script ships with it. Each file puts its script's directory on `sys.path`; a script whose filename has hyphens (`audit-cookbook.py`) is loaded by `importlib.util`. `evals/test_checks.py` stays with the POSIX-only harness it proves, which CI skips on Windows.
- Committed input fixtures live in `scripts/fixtures/renders/`, one real-shaped artifact per type, shared by the fixtures, tracker, and cookbook-audit suites. Synthetic one-off input is written into a `tempfile.mkdtemp()` tree inside the test, never into the repo.
- **Release checks are tested like any other assertion.** `scripts/audit-cookbook.py` proves every `/andthen:<skill>` invocation printed in `COOKBOOK.md`, the two READMEs, and `MIGRATING-FROM-0.x.md` still resolves to a shipped skill, flag, and `--mode` value; `tests/test_audit_cookbook.py` fires each failure mode on synthetic prose and asserts the live docs pass.
- **Eval harness tests drive the runner, never a re-implementation.** `evals/test_checks.py` scripts the one dispatch through `run.py`'s own seams and asserts every acceptance boundary in both directions: a case shape that must refuse before dispatch and the valid example of the same key, a judge PASS that must quote retained material and the absence-based FAIL that stays expressible, a reused session that is an ERROR and a missing id that is not, a failing check that still reaches the judge and a cell that passes only when checks and criteria both do. A cell is one `dartclaw-workflow run`: `evals/workflows/tail.yaml` appends the `checks` step (`evals/step.py` over `checks.evaluate`) and the `judge` step to the case's own subject workflow, so the checks run for real inside the dispatch double rather than beside it. Six eval cases' `oracle.py` are proved the same way on staged workspaces (the one-story `exec-plan` and `plan` are not driven). The live eval suite is two named tiers in `evals/cases.py` (`smoke`, eight cells each under the `SMOKE_SECONDS` bar, and the report names one that runs over it; `full`, every case, Claude only beyond smoke) run `--jobs N` cells at a time, each its own DartClaw run over its own workspace whose `result.json` carries DartClaw's token accounting for subject and judge; a Claude cell dispatches in the operator's own environment and so measures the plugin he has installed, a Codex cell registers a staged snapshot under the `CODEX_HOME` DartClaw pins; a case is sized against what the harness enforces, `stage.TURN_TIMEOUT` giving one step an hour and `stage.TIMEOUT` bounding the cell at 6300 s (the `exec-plan` case is one story, and the longest cells have run close to an hour), because a suite that takes hours does not get run. `evals/subject/` is the vendored subject application every cell starts from – one project's documents and one real suite, so a code or gap review has real code to look at and the Intent, Learnings and tech-debt anchors a skill reads are present everywhere; a case stages its `overlay/` over it, or starts from it unchanged when it carries neither directory, or replaces it with a `fixture/` whole workspace where the prompt needs a project the app is not, and validation refuses only a case carrying both. `evals/subject-defects.md` records the deliberate flaws a case pins its expectation to, and `SubjectAppTest` proves the app's suite stays green and the tree stays silent about the harness – as `cases.OVERLAY_WORDS` does for every overlay.
- **Prompt-contract tests** are the local idiom for a gate over shipped text: a fixture holding the prose, the gate's own regex imported by name (never a copy), and a docstring stating what the pair proves. Both directions are asserted – the pattern fires on the prose it replaced and does *not* fire on the replacement, because a gate that flags its own fix gets switched off.

## What Must Have a Test Before Merge

- Every release-check assertion is proved against synthetic input, not only against the live tree. An assertion that cannot be shown to fire is a non-catch with more ceremony.
- Every shipped script's refusal path has a test asserting the exit code, the message, and that nothing was written.

## Known Gotchas

- A script that greps the tree for the patterns it polices matches its own source, so it skips its own file.
- `bash scripts/install-skills.sh` without a flag conflicts with the locally installed Codex plugin; only `--validate-only` and `--claude-user --dry-run` are safe here.
- The shipped-surface budget (`tests/surface-budget.json`) counts words, so a rewrite at equal length passes – it catches accretion, not a bad instruction.
