---
description: Work the issue tracker – `publish` projects a plan bundle into a parent issue and one child issue per story, `triage` labels and routes incoming items toward implementation or a human decision, and `setup` writes the Issue Tracker document. Trigger on 'publish this plan to the tracker', 'triage the backlog', 'set up the issue tracker'.
argument-hint: "[--auto] (publish <plan.json> [--dry-run] | triage [issue number(s) or tracker query] | setup)"
---

# Tracker

Work the project's issue tracker through its `Issue Tracker` document, one verb per run.

## Input

`$ARGUMENTS` opens with the verb, and `ARGUMENTS` is the rest minus flags. With no verb there, take the one the request's words name.

| Verb | `ARGUMENTS` | Read |
|---|---|---|
| **publish** | the path to a `plan.json` | § 2a below |
| **triage** | issue number(s) or a tracker query; empty triages the untriaged backlog | [`triage.md`](references/triage.md), [`agent-brief.md`](references/agent-brief.md) |
| **setup** | none | § 2c below |

`--auto` makes the run unattended: read [`unattended-runs.md`](../../references/unattended-runs.md) and follow it.

## Rules

- Print each recommended skill invocation as a complete, paste-ready line in the host's syntax, including its target path or request and required arguments.

- **Executable config.** The `Issue Tracker` document is security-critical, because its table values run as commands. Each value is a single direct command invocation (an executable, fixed arguments, `<placeholders>`) with no pipes, shell operators, command substitution, or piping to an interpreter. Review changes to it as code.
- **Complete mapping first.** Before a verb's first tracker call, reads included, stop on any operation it needs that the Operation Table leaves unmapped, so a multi-issue write never strands partial state.
- **Argv-safe.** Every payload field is data: pass `title`, `body_file`, and issue number as distinct argv elements (or structured MCP fields), never as interpolated shell source. On GitHub, `create issue` maps them to `gh issue create --title` and `--body-file`, and `edit body` maps the issue number and `body_file` to `gh issue edit`. An operation-table backend keeps the same argument boundary, and a mapping that only offers a shell template is unresolved executable config: stop before the first external call.

## Workflow

### 1. Tracker resolution

Before `publish` or `triage` runs any tracker operation, resolve the `Issue Tracker` document (**Project Document Index**; default `docs/ISSUE-TRACKER.md`) by its `Backend:` line:

- `GitHub` takes the built-in `gh` flows.
- `none` declares no tracker: end on one line saying so, naming the `Backend:` line.
- Another backend substitutes every operation from its **Operation Table**. A value naming an MCP tool is invoked the same way.
- An unparseable `Backend:` line takes `setup`.
- For `publish`, an absent document takes `setup`, since creating it is part of the first publish.
- For `triage`, an absent document takes the `gh` default where the repository has a GitHub remote, and `setup` where it has none, since there is nothing to read.

Taking `setup` means offering it, and an unattended run stops as step 2c says. On acceptance, run it, then resolve against the document it wrote.

**Gate**: the backend is known and every operation the verb needs is mapped.

### 2a. Publish

`plan.json` is agent truth, and the tracker is its human projection. `publish` writes that projection and never writes `plan.json`.

**One-way sync.** A PM reprioritizing in the tracker is a re-plan.

**Idempotent publish**, keyed on the script's marker line.

**Operations used**: `list issues`, `create issue`, `edit body`. GitHub is the worked path: do not hand-roll another backend's CLI here.

#### Assemble the payloads

**`--dry-run`** is the safety boundary: one script call with `--dry-run` and no `--existing`, print the payloads, and stop. It makes no tracker call and writes no file, and every `action` reads `unknown` – only the lookup below decides create-versus-update.

**Live**, assemble once without `--existing` to derive the canonical plan identity and every exact `search` marker. For each marker, call `list issues` with that whole marker as the body-search phrase and a limit of 2. Combine the returned `number,body` rows in `.agent_temp/tracker-existing.json` and assemble against it:

```sh
python3 <skill-dir>/scripts/tracker.py publish <plan.json> --sha <commit-sha>
gh issue list --search '"<exact emitted search marker>" in:body' --state all --json number,body --limit 2
python3 <skill-dir>/scripts/tracker.py publish <plan.json> --sha <commit-sha> --existing .agent_temp/tracker-existing.json
```

`--sha` pins each child's FIS link to a commit, and defaults to `HEAD`.

The lookup is per marker because a globally capped query can omit an older issue and turn a re-run into a duplicate.

**Gate**: the payloads are assembled against `--existing`, every row `create` or `update`; under `--dry-run`, the payloads are printed.

#### Send it

Assemble again with `--body-dir .agent_temp/tracker-bodies`. The script writes deterministic UTF-8 files and adds an absolute `body_file` to each payload.

Send the parent first (its checklist follows plan story order), then each child. Then rewrite the parent's checklist and each child's `Blocked by:` lines with the created issue numbers, and send each rewritten body through `edit body`.

**Gate**: every payload is sent or reported as skipped with a reason, and every cross-reference body is re-sent through `edit body`.

### 2b. Triage

Follow `triage.md`.

### 2c. Setup

Ask which backend the tracker uses, and for any backend but GitHub, the command each operation maps to. An unattended run writes nothing and stops on `BLOCKED:` naming `setup` and the `Backend:` line to set.

- **An existing document** is edited in place, with no template loaded: set its `Backend:` line and the operations the answer maps.
- **A new document** is seeded by a subagent – the installed `worker` role agent when available, else a generic inherited one – that invokes the `andthen:init` skill with `seed Issue Tracker` and the chosen backend, which keeps the templates out of this run's context. Add its Index entry when the instruction file lacks one.

**Gate**: the document carries a parseable `Backend:` line and every operation the chosen backend needs.

## Output

`publish` reports the counts of created and updated issues, and any payload skipped with its reason.
