# Decisions

## Current ADRs

| ID | Title | Status | Scope |
|---|---|---|---|
| ADR-001 | Strictly downward module layering | Accepted | `src/reporter/` |

## Superseded

Nothing superseded yet.

## Still Current

- **Standard library only**: the tool must run on a laptop where nothing can be installed, so a dependency would cost more than any library saves.
- **CSV is the only output format**: every consumer opens a spreadsheet, and a second format would need a format-selection surface nobody has asked for.
- **Amounts are whole units**: the ledgers carry no fractional amounts, so records parse `amount` as an integer and a fractional value is a rejected row.

## Pending

- **Retry backoff**: a fixed 1 s pause and a five-retry maximum ship today. Whether that becomes a growing pause with a cap stays open until we have measured how long a spreadsheet actually holds a report file open on the shared drive.
- **CSV rendering cost**: `export_csv` joins each row by hand. Whether the standard library's `csv` writer is faster over a full-size ledger is unmeasured, so the hand-rolled join stays until someone measures it.
