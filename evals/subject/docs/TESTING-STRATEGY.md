# Testing Strategy

Commands: see `docs/KEY_DEVELOPMENT_COMMANDS.md` § Testing (`fast`, `full`, run one test).

## Levels In Use

| Level | Applies to | Lives in |
|---|---|---|
| Unit | One module's public functions, called directly | `tests/test_*.py` |
| Journey | The command line end to end, over a ledger on disk | `tests/journeys/journey_*.py` |

## Framework and Test-Data Conventions

- `unittest` from the standard library; one test module per source module, named after it.
- A journey module is named `journey_*.py` so the `fast` tier's default discovery pattern leaves it out; the `full` tier names the pattern explicitly.
- Sample input is written into a `tempfile.TemporaryDirectory` inside the test, never committed and never shared between tests.
- A test asserts the observable result – the returned value or the written file's text – not the calls that produced it.

## What Must Have a Test Before Merge

- Every behavior a caller can reach: each public function, and each exit code the command line returns.
- Every rejection path that is part of the contract – a malformed row, a missing ledger.
- A bug fix starts from a test that fails for that bug.

## Known Gotchas

- The suite must run from the repository root; `src.reporter` resolves through the working directory.
- A temporary directory on Windows can still hold an open handle when the test ends, so a test never asserts that a directory was removed.
