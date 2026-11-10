# Verification Evidence

The project's checks contract: where a skill's check commands come from, how the results are reported, and how green work is committed.

## Where the commands come from

The `Key Dev Commands` document (**Project Document Index**; default `docs/KEY_DEVELOPMENT_COMMANDS.md`) is the one source for every skill that runs a check. Read it before running any check. Run a command its row states as written, never re-derived.

Its Testing section declares two tiers plus one single-test row, so no skill has to infer what is heavy:

- **fast** – once per story: unit tests and the checks that finish in seconds.
- **full** – end of a run: integration, E2E, and performance suites.
- **run one test** – a template with literal `{file}` and `{test}` placeholders, substituted to execute a single proof target.

## When the document does not answer

A missing document, or a Testing section without both tiers, is a **named outcome, never a silent fallback**. Derive the commands from the project's own configuration. Wherever the results are reported, say what was missing and what the commands were derived from. A guessed command that exits 0 looks exactly like a check that ran, so an unlabelled fallback makes "tests pass" uncheckable.

A run that writes to the project also creates the missing `Key Dev Commands` document from its template, per the Index preamble, holding the commands it derived. A read-only run writes nothing.

## Substance and wiring scans

A green suite proves the checks ran, not that the code behind them is real.

**Substance**: TODOs and placeholders, empty bodies and trivial returns, canned success responses, skipped or empty tests, config at placeholder defaults.

**Wiring**: every new route, component, endpoint, model, env var, or export has a consumer. Grep the new symbol repo-wide; a definition with no other hit is the finding.

## What the report names

Completion reports name each check and its numbers:

- **Build** – exit code or status.
- **Tests** – pass and fail counts.
- **Linting/types** – error and warning counts.
- **Visual validation** – when UI changed.
- **Runtime** – when the app was started or a flow exercised.

Name the tier that ran, and any applicable check skipped and why. Skills may add fields, never drop an applicable one.

## The commit rule

A skill that commits its work does so unasked, because the branch history keeps it and a revert undoes it.
A push or a pull request leaves the machine, so it waits for the user's yes.

- Before the first edit of a run that will commit, outside `--auto`, when the current branch is the remote's default branch, ask once whether to start a feature branch, because commits land on the current branch and the pull request opens from it. Recommend starting it the way the project's written convention for starting work says, else as `<type>/<slug>`.
- Commit only green work: a change whose checks fail stays in the tree.
- Stage by path, never `-A` or `-u`, and commit by path (`git commit -- <paths>`), because a plain commit takes whatever another session has staged.
- A file that also holds a change you did not make stays uncommitted and goes in the report.
- A run another skill invoked leaves its change for that skill to commit, except a story run of the `andthen:exec-plan` skill, which commits its own.
- Report the commit's short SHA and paths, or why nothing was committed.
