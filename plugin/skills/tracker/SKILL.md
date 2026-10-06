---
description: Work the issue tracker – `publish` projects a PRD and its plan into a parent issue and one child issue per story, `triage` labels and routes incoming items toward implementation or a human decision, and `setup` writes the Issue Tracker document. Trigger on 'publish this plan to the tracker', 'triage the backlog', 'set up the issue tracker'.
argument-hint: "[--auto] (publish <plan.json | prd.md> [--dry-run] | triage [issue number(s) or tracker query] | setup)"
---

# Tracker

Work the project's issue tracker through its `Issue Tracker` document, one verb per run.

## Input

`$ARGUMENTS` opens with the verb, and `ARGUMENTS` is the rest minus flags. With no verb there, take the one the request's words name.

| Verb | `ARGUMENTS` | Read |
|---|---|---|
| **publish** | a `plan.json`, or a `prd.md` alone | § 2a below |
| **triage** | issue number(s) or a tracker query; empty triages the untriaged backlog | [`triage.md`](references/triage.md), [`agent-brief.md`](references/agent-brief.md) |
| **setup** | none | § 2c below |

- `--auto` makes the run unattended: read [`unattended-runs.md`](../../references/unattended-runs.md) and follow it.

## Rules

- Print each recommended skill invocation as a complete, paste-ready line in the host's syntax, including its target path or request and required arguments.

- **Executable config.** The `Issue Tracker` document is security-critical, because its table values run as commands. Each value is a single direct command invocation (an executable, fixed arguments, `<placeholders>`) with no pipes, shell operators, command substitution, or piping to an interpreter. Review changes to it as code.
- **Complete mapping first.** Before a verb's first tracker call, reads included, stop on any operation it needs that the Operation Table leaves unmapped, so a multi-issue write never strands partial state.
- **Durability rule.** What you write into a tracker body or comment outlives the branch that prompted it. Name interfaces (types, signatures, commands) and behavior, never file paths, line numbers, commits, or code snippets. A snippet that itself encodes a settled decision (schema, state machine, type) may be inlined, trimmed to the decision-carrying part.
- **Argv-safe.** Every title, body, and issue number is data: pass the title, the body file, and the issue number as distinct argv elements (or structured MCP fields), never as interpolated shell source. On GitHub, `create issue` maps them to `gh issue create --title` and `--body-file`, and `edit body` maps the issue number and the body file to `gh issue edit --body-file`. An operation-table backend keeps the same argument boundary, and a mapping that only offers a shell template is unresolved executable config: stop before the first external call.

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

The bundle is agent truth, and the tracker is its human projection. `publish` never writes `plan.json`, and sync is one way: a PM reprioritizing in the tracker is a re-plan.

**Operations used**: `fetch issue`, `list issues`, `create issue`, `edit body`. GitHub is the worked path: do not hand-roll another backend's CLI here.

#### The issues

Each body you write is projected from one hidden line down. On the parent the line is `<!-- andthen-projection <source> -->`, where `<source>` is the repo path of the PRD, else of the `plan.json`, kept as identity only. On a child it is `<!-- andthen-projection <id> <source> -->`, led by its story's id so the parent's line never matches it. Keep the text above the line, such as a source issue's original request, and put the line below the text of an issue that has none.

- **The parent** is titled by the PRD's heading, else `Plan: <plan directory name>`, and a found parent keeps its title. Below the line goes the PRD, then a `## Stories` checklist with one `- [ ] <id> #<number> – <name>` per story, checked once the story is `done` or `skipped`. A plan without a PRD writes only the checklist. A `prd.md` alone writes only the PRD and keeps the checklist already there.
- **A child** per story is titled `<id> - <name>`. Below the line go the story's scope, then its FIS's Intent, Expected Outcomes, and Acceptance Scenarios without their Proof lines, then `Blocked by:` its dependencies' issues, and once the story is done `Verified:` with its `verified.summary`.
- **A closed issue is the shipped record**, so never edit one.

#### Find them

The parent is the first open issue among the issue the PRD's header names, a tracker item the plan's `sourceRefs` cite, and the issue `list issues` finds with the line as the body-search phrase. With none open, create the parent, and when a candidate was closed, link it in the text above the line. A child is the issue the parent's checklist links for its story, else the open issue `list issues` finds with its line, because a run that stopped before the checklist write left it unlinked. Two open candidates at one step, for the parent or a child, stop the run, naming both.

#### Preview and send

Compare each composed body with the issue's text below its line. Show each issue to create and what each update changes, and ask once before the first write, because an update replaces an edit made in the tracker since the last publish. An edit worth keeping goes into its source first: `prd.md` through the `andthen:clarify` skill, or the story's FIS. When the skill that invoked this run already showed this preview and got a yes, as the `andthen:ship` skill does, that answer is the ask.

`--dry-run` prints the preview and stops before any write. An unattended run skips the ask and reports what each update replaced.

Write each body as a UTF-8 file under `.agent_temp/tracker-bodies/` and send it as the body file. Create the missing issues, parent first and stories in plan order, and add each child to the parent's checklist as soon as it exists. Then edit each body still missing an issue number it names, and send the other updates.

**Gate**: every issue created, updated, or found unchanged, or the user's no; under `--dry-run`, the preview printed.

### 2b. Triage

Follow `triage.md`.

### 2c. Setup

Ask which backend the tracker uses, for any backend but GitHub the command each operation maps to, and whether a feature's requirements record lives in the repo or the tracker. An unattended run writes nothing and stops on `BLOCKED:` naming `setup` and the `Backend:` line to set.

- **An existing document** is edited in place, with no template loaded: set its `Backend:` and `Record:` lines and the operations the answer maps.
- **A new document** is seeded by a subagent – the installed `worker` role agent when available, else a generic inherited one – that invokes the `andthen:init` skill with `seed Issue Tracker`, the chosen backend, and the record's home, which keeps the templates out of this run's context. Add its Index entry when the instruction file lacks one.

**Gate**: the document carries a parseable `Backend:` line and every operation the chosen backend needs.

## Output

`publish` reports each issue it created, updated, or found unchanged, by number, and in an unattended run what each update replaced.
