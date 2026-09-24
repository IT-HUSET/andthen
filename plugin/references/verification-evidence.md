# Verification Evidence

The project's checks contract: where a skill's check commands come from, and how the results are reported.

## Where the commands come from

The `Key Dev Commands` document (**Project Document Index**; default `docs/KEY_DEVELOPMENT_COMMANDS.md`) is the one source for every skill that runs a check. Read it before running any check; a command a row states is never re-derived.

Its Testing section declares two tiers plus one single-test row, so no skill has to infer what is heavy:

- **fast** – once per story: unit tests and the checks that finish in seconds.
- **full** – end of a run: integration, E2E, and performance suites.
- **run one test** – a template with literal `{file}` and `{test}` placeholders, substituted to execute a single proof target.

## When the document does not answer

A missing document, or a Testing section without both tiers, is a **named outcome, never a silent fallback**: derive the commands from the project's own configuration, and wherever the results are reported say what was missing and what the commands were derived from. A guessed command that exits 0 looks exactly like a check that ran, so an unlabelled fallback makes "tests pass" uncheckable.

## Substance and wiring scans

A green suite proves the checks ran, not that the code behind them is real.

**Substance**: TODOs and placeholders, empty bodies and trivial returns, canned success responses, skipped or empty tests, config at placeholder defaults.

**Wiring**: every new route, component, endpoint, model, env var, or export has a consumer. Grep the new symbol repo-wide; a definition with no other hit is the finding.


## What the report names

Completion reports name each check and its numbers – **Build** (exit code/status), **Tests** (pass/fail counts), **Linting/types** (error/warning counts), plus **Visual validation** when UI changed and **Runtime** when the app was started or a flow exercised. Name the tier that ran, and any applicable check skipped and why. Skills may add fields, never drop an applicable one.
