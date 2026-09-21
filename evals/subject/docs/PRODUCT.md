# Product

## Vision

Finance analysts keep their monthly ledgers as plain delimited files and need a report the rest of the company can open. Reporter turns one of those files into a CSV report from the command line, with no install step, no account, and no service to keep running.

## Target Users

- **Ledger owner**: closes a month and wants the numbers out as a file they can attach or drop in a shared folder.
- **Analyst on a locked-down laptop**: can run Python but cannot install packages or reach an internal service.

## Value Propositions

- A report in one command, from a tree that is copied rather than installed.
- The same output on macOS, Linux, and Windows, because nothing below the standard library differs.

## Non-Goals

- **No network access.** The tool reads and writes local files only; it never fetches, posts, or uploads. Rejected 2026-04-02, requested as "mail the report from the tool".
- **No plugin or extension mechanism.** Output formats ship in the package and are read from the code, not discovered at run time. Rejected 2026-05-18.
- **No configuration file.** Every option is a command-line argument, so a run is reproducible from its own command.
- **No stored history.** The tool keeps no database and no run log beyond the files it writes into the output directory.

## Proportionality

- **Stage**: internal
- **Scale**: about 30 analysts · ledgers under 50,000 rows · run on a laptop, nothing deployed · 2 maintainers
- **Standing technical non-goals**: no new services, no plugin system, no configuration surface

## Success Metrics

- A month closes without anyone opening a spreadsheet to reshape the export by hand.
- A new analyst produces their first report from `docs/KEY_DEVELOPMENT_COMMANDS.md` alone.
