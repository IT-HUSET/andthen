---
description: Project a plan bundle into the issue tracker – `publish` creates the parent issue and one child issue per story, updated on a re-run. Trigger on 'publish this plan to the tracker', 'create issues for these stories'.
argument-hint: "publish <plan.json> [--dry-run] [--auto]"
---

# Tracker: Project the Plan Into the Issue Tracker

`plan.json` is agent truth; the tracker is the human projection of it. This skill writes that projection and nothing else – it never ships the plan file, never invents work the plan does not carry, and never writes `plan.json`.

**One way, by design.** The projection flows repo → tracker. There is no reverse sync: a PM reprioritizing in the tracker is a re-plan, not a status write, and reading it back would make two writers of one field.

**No state of its own.** The join key is one exact HTML-comment marker line carrying the repository-relative plan path and, for a child, its story ID. That canonical identity makes relative and absolute invocations converge on the same issue without adding a `plan.json` field.

`$ARGUMENTS` is the verb (`publish`) then the path to a `plan.json`.

`--auto` is `AUTO_MODE`: no conversational prompts, per [`automation-mode.md`](../../references/automation-mode.md).

`--dry-run` prints the assembled payloads and stops – the safety boundary: no tracker call and no file, so it works offline and unauthenticated.

## INSTRUCTIONS

- **Tracker resolution** – resolve the `Issue Tracker` document (see **Project Document Index**; default `docs/ISSUE-TRACKER.md`) before any tracker operation; absent → offer to scaffold it, because this skill owns that document and creating it is part of the first publish, not a prerequisite the user has to discover. A present document routes on its `Backend:` line:
  - `GitHub` or `none` → the built-in `gh` flows below.
  - Any other named backend → substitute every operation from the document's **Operation Table**; a table value may name an MCP tool instead of a CLI, and is invoked the same way.
  - Missing or unparseable → `BLOCKED: issue-tracker backend unspecified – set the Backend: line in <tracker-doc path>`.
- **Scaffolding it** – an accepted offer is seeded by a subagent, so the template set stays out of this run's context: spawn a generic inherited subagent, the installed `worker` role agent when available, whose prompt names the ISSUE-TRACKER.md template section in [`project-document-templates.md`](../../references/project-document-templates.md), the target path resolved from the **Project Document Index**, and the backend the user chose. Its Index entry is added with it, and resolution then proceeds against the seeded document. A present document is used as it stands, with no template loaded at all.
- **Operations used**: `list issues`, `create issue`, `edit body`. A backend that cannot express an assignee carries `Owner:` in the body instead. An unmapped operation this run needs → `BLOCKED: issue-tracker operation <op> unmapped` **before** the first external call, so a multi-issue publish never strands half a plan in the tracker.
- **The document is executable config** – its table values are run as commands. Each is a single direct invocation with no pipes, shell operators, or command substitution; review changes to it as code.
- **GitHub is the worked path.** Do not hand-roll another backend's CLI here.

## WORKFLOW

### 1. Assemble the payloads

**`--dry-run`**: one script call, `--dry-run` and no `--existing`, then print the payloads and stop. It makes no tracker lookup, so every `action` reads `unknown` – the lookup below is what decides create-versus-update.

Live: assemble once without `--existing` to derive the canonical plan identity and every
exact `search` marker. For each emitted marker, call `list issues` with that whole
marker as the body-search phrase and a limit of 2, then combine the returned
`number,body` rows in `.agent_temp/tracker-existing.json` and assemble against it:

```sh
python3 <skill-dir>/scripts/tracker.py publish <plan.json> --sha <commit-sha>
gh issue list --search '"<exact emitted search marker>" in:body' --state all --json number,body --limit 2
python3 <skill-dir>/scripts/tracker.py publish <plan.json> --sha <commit-sha> --existing .agent_temp/tracker-existing.json
```

`--sha` pins each child's FIS link to a commit; it defaults to `HEAD`.

Pass the search phrase as one argv value, never interpolated shell source.

The exact per-marker lookup is intentionally narrow: a globally capped query can
omit an older issue and turn a re-run into a duplicate. Zero matches creates, one
updates, and multiple matches stop with `BLOCKED:` before any write call. The
script prints JSON – the parent payload and one child per story, each carrying
`action: create|update` and, on update, the issue number.

### 2. Send it

Assemble again with `--body-dir .agent_temp/tracker-bodies`. The script writes deterministic UTF-8 files and adds an absolute `body_file` to each payload. These are temporary transport, not tracker state. Send the parent first (its checklist follows plan story order), then each child. Then rewrite the parent's checklist and each child's `Blocked by:` lines with the created issue numbers, and send each rewritten body through `edit body`.

**Safe transport contract.** Treat every payload field as data: pass `title`, `body_file`, assignee, and issue number as distinct argv elements (or structured MCP fields), never as interpolated shell source. GitHub `create issue` maps those fields to `gh issue create --title`, `--body-file`, and `--assignee`; `edit body` maps the issue number and `body_file` to `gh issue edit`. The operation-table backend must preserve that same argument boundary. A backend mapping that only offers a shell template is unresolved executable config, so emit `BLOCKED:` before the first external call.

**Gate**: every payload either sent or reported as skipped with a reason, every cross-reference body re-sent through `edit body`; the counts of created / updated stated. Under `--auto`, no prompts – emit `BLOCKED:` for an unresolvable tracker and stop.
