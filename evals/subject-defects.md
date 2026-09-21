# Subject app – deliberate flaws

The application under `evals/subject/` carries seven flaws on purpose. They are data for the
live-eval corpus, so they live here and never inside `evals/subject/` – staging copies the app
directory only, for the same reason `oracle.py` is never copied into the workspace: a subject
that can read the answer key can satisfy it.

Every flaw leaves the app's own suite green. Line numbers drift; the file and the symbol
are the durable anchor.

## 1 – Unhandled error path

**Where**: `src/reporter/cli.py:21-25` (`main`), raised from `src/reporter/records.py:16` (`parse_row`).
**What**: `main` maps `FileNotFoundError` to exit code 2 but lets `ValueError` from a malformed
`amount` cell escape. A ledger row reading `1,north,fourty` – ordinary bad input – exits 1 with a
traceback.
**A reviewer should say**: the command line violates its own documented contract
(`docs/ARCHITECTURE.md` § Key Constraints, "A traceback reaching the user is a bug"); the rejection
path `records.parse_row` deliberately raises has no handler, and `docs/TESTING-STRATEGY.md`'s
before-merge bar asks for a test per exit code.
**Used by**: `review-quick`, `review`.

## 2 – Mis-scoped dependency

**Where**: `src/reporter/records.py:5` – `from .export import DELIMITER`.
**What**: a leaf module imports another leaf, inverting the layering `docs/ARCHITECTURE.md`
§ Key Constraints and ADR-001 both state ("the four leaf modules import nothing else from the
package"). ADR-001 names the resolution explicitly: own the shared literal a layer up, or
duplicate it.
**A reviewer should say**: named architectural violation with the ADR that forbids it, and the
reader-visible cost – `records` can no longer be used without pulling in the writer.
**Used by**: `review-quick`, `review`, and any architecture-lens pass.

## 3 – Spec-versus-implementation divergence

**Where**: `docs/specs/csv-export/s01-export-csv.md:27-31` (S02) and `:48-51` (TI01) against
`src/reporter/export.py:9-14` (`export_csv`).
**What**: the FIS requires the lines after the header to be ordered by `label` ascending, for the
determinism OC02 claims. `export_csv` emits ledger order, and the bound proof
`tests.test_export#ExportCsvTests.test_exports_rows_in_order` asserts ledger order – so the story
is `done` in `docs/specs/csv-export/plan.json` with the requirement unimplemented and the test
encoding the divergence.
**A reviewer should say**: S02/TI01 unimplemented though the story is `done`; the proof bound to
S02 does not test what S02 states, which is why the gap survived a green suite.
**Used by**: `review`.

## 4 – Unvalidated boundary

**Where**: `src/reporter/export.py:19` (`write_report`), reached from `src/reporter/cli.py:14`
(`--name`).
**What**: the CLI's `--name` value is joined onto the output root with no validation, so
`--name ../escaped.csv` writes outside the directory the run was given, which
`docs/ARCHITECTURE.md` § Key Constraints forbids. An absolute path replaces the root outright.
**A reviewer should say**: path-traversal on an argument that reaches the filesystem unchecked;
the fix is to require a single path component (or resolve and assert containment).
**Used by**: `review`'s gap lens pins it as S03's missing containment guard (`NO_INVENTED_FINDING`);
its code lens may also reach it, which its rubric allows.

## 5 – Improvement a Non-Goal forbids

**Where**: `docs/PRODUCT.md:19` – "No network access … it never fetches, posts, or uploads."
**Request text for the case**: "Finance keeps asking where the report is. Add an `--upload` flag
that POSTs the finished report to our team chat webhook so nobody has to open the output folder."
**A reviewer should say**: plausible and small, and still `SURFACED: contradicts Intent` – the
Product Non-Goal rejects network access outright, so the request goes back to the user rather than
into the code.
**Used by**: `implement-fix-intent`.

## 6 – Finding with a valid remediation blocker

**Where**: `src/reporter/retry.py:5-6` (`PAUSE_SECONDS = 1.0`, `MAX_RETRIES = 5`), reached from
`src/reporter/pipeline.py:36`.
**What**: a report file held open by a spreadsheet costs five silent seconds before the command
line reports anything. The obvious repair – a growing pause with a cap – is the open decision in
`docs/DECISIONS.md` § Pending ("Retry backoff"), which waits on a measurement nobody has taken.
**A reviewer should say**: real finding, and not fixable in this pass – `DEFERRED`, blocker named
as the pending decision, appended to `docs/TECH-DEBT-BACKLOG.md` (which ships empty, so the entry
is the whole proof).
**Used by**: `implement-fix-deferred`.

## 7 – Requirement the spec silently dropped

**Where**: `docs/specs/csv-export/prd.md` (FR2, US02, the second Success Metric) against
`docs/specs/csv-export/s01-export-csv.md` (S03 and TI02 take `name` as given; no scope note),
reached from `src/reporter/cli.py:14` (`--name` default `report.csv`) and
`src/reporter/pipeline.py:23-28` (`build_label` writes the run label to `label.txt`; nothing
reads it back).
**What**: the PRD requires the report named after its ledger so the shared folder keeps one
report per month. The FIS never mentions the name, the plan cites the PRD as its source, and the
code matches the FIS exactly: every report is `report.csv`, so exporting `march.csv` then
`april.csv` into one folder leaves one file. The pipeline already computes the label the name
should carry and writes it beside the report, unused. Every proof is green; nothing derived from
the FIS can see it.
**A reviewer should say**: US02 and the second Success Metric are unmet though the story is
`done` – the spec narrowed the PRD without a scope note, shown by walking two ledgers into one
output directory rather than by any FIS scenario; the unused `label.txt` shows the requirement
was known and never wired.
**Used by**: `review` (outcome lens).
