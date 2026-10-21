# Eval Harness

Live evals of AndThen skills on Claude Code and Codex. Commands: `docs/KEY_DEVELOPMENT_COMMANDS.md` § Testing (`eval smoke`, `eval full`).

## A cell

A cell is one case on one provider, run as one `dartclaw-workflow run` over its own workspace. `workflows/tail.yaml` appends two steps to the case's subject workflow: `checks` (`step.py` over `checks.evaluate`) and `judge`. A cell passes only when both do. Its `result.json` carries DartClaw's token accounting for subject and judge, and under `dartclaw` the `path` and `--version` of the `dartclaw-workflow` the tier resolved once, with `version` null and `error` set when it could not be read.

The subject reads its prompt from the case's `subject-workflow.yaml` `prompt:`, and `prompt.md` feeds only the judge (`step.py`), so a prompt fix edits both. No judge-only entry point exists, so a rubric change needs a full re-run of the cell.

Every cell runs a snapshot of the working tree's `plugin/`, copied into the run's `candidate/` – uncommitted edits included, never the installed plugin. Cells run on a dirty tree all report the same `candidate:` SHA, so group them by grepping each cell's `candidate/plugin/` for the clause in question. A run stages under `$TMPDIR/andthen-evals/` and moves to `.agent_temp/evals/<case>/<provider>/<stamp>/` when it ends, because Claude loads every `CLAUDE.md` above its working directory and this repo's would reach the subject.

- **Claude** cells keep the operator's environment for the login only: `inherit_user_settings: false` spawns the CLI with project-only setting sources, so `~/.claude/CLAUDE.md`, memory, the output style, and user MCP servers stay out. The cell's `claude` wrapper loads the candidate with `--plugin-dir`, and the role agents `init` bundles are committed into the workspace as project agents.
- **Codex** cells register the candidate under the `CODEX_HOME` DartClaw pins.

A case keeps its directory name through a skill rename, because retained runs are filed under it ([ADR-020](../docs/adrs/ADR-020-one-authoring-and-one-execution-skill.md)): `spec` and `spec-two-stories` run the `plan` skill.

## Tiers

Two named sets in `cases.py`, run `--jobs N` cells at a time:

- `smoke` – seven cells, each under `SMOKE_SECONDS`; the report names any that runs over.
- `full` – every case, Claude only beyond smoke.

Size a case to what `stage.py` enforces: `TURN_TIMEOUT` gives one step an hour and `TIMEOUT` bounds the cell. The longest cells have run close to an hour, and a suite that takes hours does not get run.

## Workspaces

`subject/` is the vendored subject application every cell starts from: one project's documents and one real suite, so a review has real code and the Intent, Learnings, and tech-debt anchors a skill reads are present. A case either starts from it unchanged, stages its `overlay/` over it, or replaces it with a whole `fixture/` workspace when the prompt needs a different project; validation refuses a case carrying both directories.

A cell runs with `SHELL=/bin/bash`, so the operator's login shell does not change a result. The `init` cases also get a scratch `HOME` holding only Claude's login, because the skill inspects `~/.claude/agents` and `~/.codex` and the operator's machine would pick its branch.

`subject-defects.md` records the deliberate flaws a case pins its expectation to. It sits beside the app, never inside it, because a subject that can read the answer key can satisfy it.

## Running and reading

- **Run cells in parallel, never in rounds.** The harness runs a case once per invocation, so repeat a case with concurrent invocations; each sequential round waits on its slowest cell, and five rounds of the four `spec` cases took 40 minutes (2026-09-29).
- **Act on each cell's `result.json` as it lands** and re-run a failure while the other cells still run, instead of polling until the whole invocation ends (40 minutes lost on 2026-10-21).
- A tier start keeps the newest three runs per case and provider under `.agent_temp/evals/` and deletes the rest, so rename a cell's directory to keep it. The tree still holds cells of retired cases and older eras, so an aggregate filters to cases under `evals/cases/` and reads the newest cell per provider with its date.
- **Attribute cells by the report's `run` column, never a directory diff**, because concurrent launchers share the tree.
- **A slow cell is fan-out before it is wording.** Count its spawned subagents against a retained run of the same case from before the slowdown, then trim prose.
- `Permission mode forced to default – CLAUDE_CODE_SUBPROCESS_ENV_SCRUB is set` in `stderr.log` is benign; read the workflow's `errorMessage` in `stdout.jsonl` for the real cause.
- **`Turn boundary held` followed by `stalled for 300s` in a cell's `stderr.log` is the host hang, not the skill.** A story subagent's background reviewer reports back to that subagent, but DartClaw still counts it as outstanding at the top level and holds the finished turn until `TURN_TIMEOUT`, so the checks never run. The signature shows about five minutes in: kill that cell and re-run it now, because the work itself finished in minutes and the hour mark only turns it into an ERROR (2026-10-02, 2026-10-03, 2026-10-21).
- **An ERROR saying the subject "wrote no output and said nothing" is a run that ended without its answer**, not a skill FAIL. Re-run it.
- **A Codex ERROR in seconds with `not enabled` in the rollout's `task_complete` error is the API rejecting the model**, before any turn ran. Re-run it (2026-10-03).
- **A criterion about what a run dispatched needs a schema'd output carrying it.** The judge sees declared outputs and the retained workspace, never the subject's tool calls.
- **A criterion that turns on host behaviour says so in its rubric.** `plan-asks` depends on Codex's `request_user_input_async` returning without blocking and on that host's `<collaboration_mode>` text – both upstream, so the case can flip with no edit on our side.
- **Count a subject's tool calls from parsed rollout records, never by substring.** Filter the subject rollout's `type == "function_call"` and `type == "custom_tool_call"` entries (Codex 0.155.1 records every call as the latter). A name grep over a cell's evidence also matches the tool schema, the host's developer message, and the judge's own files, and the judge grades the reply, so its rationale is silent on whether a call happened. A plausible wrong count cost an hour and a wrong recommendation (2026-09-28).
