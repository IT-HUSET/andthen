# Eval Harness

Live evals of AndThen skills on Claude Code and Codex. Commands: `AGENTS.md` § Key Development Commands → Testing (`eval smoke`, `eval full`).

## A cell

A cell is one case on one provider, run as one `dartclaw-workflow run` over its own workspace. `workflows/tail.yaml` appends two steps to the case's subject workflow: `checks` (`step.py` over `checks.evaluate`) and `judge`. A cell passes only when both do. Its `result.json` carries DartClaw's token accounting for subject and judge.

- **Claude** cells dispatch in the operator's own environment, so they measure the installed plugin, not the working tree.
- **Codex** cells register a staged snapshot under the `CODEX_HOME` DartClaw pins.

## Tiers

Two named sets in `cases.py`, run `--jobs N` cells at a time:

- `smoke` – eight cells, each under `SMOKE_SECONDS`; the report names any that runs over.
- `full` – every case, Claude only beyond smoke.

Size a case to what `stage.py` enforces: `TURN_TIMEOUT` gives one step an hour and `TIMEOUT` bounds the cell. The longest cells have run close to an hour, and a suite that takes hours does not get run.

## Workspaces

`subject/` is the vendored subject application every cell starts from: one project's documents and one real suite, so a review has real code and the Intent, Learnings, and tech-debt anchors a skill reads are present. A case either starts from it unchanged, stages its `overlay/` over it, or replaces it with a whole `fixture/` workspace when the prompt needs a different project; validation refuses a case carrying both directories.

`subject-defects.md` records the deliberate flaws a case pins its expectation to. It sits beside the app, never inside it, because a subject that can read the answer key can satisfy it.
