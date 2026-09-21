# Verification Evidence

The project's checks contract: where a skill's build, format, lint/type, test, and run commands come from, and how the results are reported.

## Where the commands come from

The `Key Dev Commands` document (**Project Document Index**; default `docs/KEY_DEVELOPMENT_COMMANDS.md`) is the one source for every skill that runs a check. Read it before running any check; a command a row states is never re-derived.

Its Testing section declares two tiers plus one single-test row, so no skill has to infer what is heavy:

- **fast** – once per story: unit tests and the checks that finish in seconds.
- **full** – end of a run: integration, E2E, and performance suites.
- **run one test** – a template with literal `{file}` and `{test}` placeholders, substituted to execute a single proof target.

## When the document does not answer

A missing document, or a Testing section that does not declare both tiers, is a **named outcome, never a silent fallback**. Derive the commands from the project's own configuration, and wherever the check results are reported say what was missing and what the commands were derived from.

A guessed command that exits 0 is indistinguishable from a check that ran, so an unlabelled fallback turns "tests pass" into a claim no reader can check.

## Substance and wiring scans

A green suite proves the checks ran, not that the code behind them is real. Two shapes hide there – present-but-hollow and complete-but-unconnected. Adapt the patterns to the project's language.

**Substance**: TODOs and placeholders, empty bodies and trivial returns, canned success responses, skipped or empty tests, config at placeholder defaults.

```bash
rg "TODO|FIXME|placeholder|not[_ -]implemented|lorem ipsum" <path>
rg "=>\\s*\\{\\s*\\}|test\\.skip|it\\.todo|xdescribe|xit" <changed-files>
```

**Wiring**: is the new route registered, the component rendered, the endpoint called, the model queried, the env var read, the export consumed? Grep the new symbol outside the file that defines it; a single hit is the finding.


## What the report names

Completion reports name each check and its numbers – **Build** (exit code/status), **Tests** (pass/fail counts), **Linting/types** (error/warning counts), plus **Visual validation** when UI changed and **Runtime** when the app was started or a flow exercised. Name the tier that ran, and any applicable check skipped and why. Skills add their own fields; none drops one that applies.
