# Architecture

## System Overview

One Python package, `src/reporter/`, run as `python3 -m src.reporter`. There is no server, no packaging step, and no state outside the output directory a run is given. The command line is a thin shell over the pipeline, so the same export runs from another Python program by calling `pipeline.run`.

## Key Components

| Component | Responsibility | Key Files/Dirs |
|---|---|---|
| Command line | Parse arguments, map failures to an exit code | `src/reporter/cli.py`, `src/reporter/__main__.py` |
| Pipeline | Stage a run: seed, label, then the report | `src/reporter/pipeline.py` |
| Records | Read a delimited ledger into records | `src/reporter/records.py` |
| Export | Render records as CSV lines and write the file | `src/reporter/export.py` |
| Retry | Re-attempt a write that failed transiently | `src/reporter/retry.py` |
| Text tools | Label normalization | `src/reporter/text_tools.py` |

## Data Flow

1. `cli.main` parses the ledger path, the output directory, and the report name.
2. `pipeline.run` writes `seed.txt`, derives `label.txt` from it, then loads the ledger.
3. `export.export_csv` renders the records; `export.write_report` writes the file through `retry`.
4. The written path goes to stdout; a failure the user can act on leaves as a message on stderr and an exit code.

## Integration Points

None. The tool reads and writes local files only – there is no service, endpoint, or credential anywhere in the tree.

## Key Constraints

- **Layering is strictly downward**: `cli` → `pipeline` → {`records`, `export`, `retry`, `text_tools`}. The four leaf modules import nothing else from the package, which is what keeps the exporter usable without the command line (ADR-001).
- A report is written only inside the directory the run was given; a run never writes outside it.
- A bad ledger is reported as a message on stderr with exit code 2. A traceback reaching the user is a bug.
- Standard library only, Python 3.9+, identical behavior on macOS, Linux, and Windows.
