# Migrating from AndThen 0.x to 1.0

1.0 removes the retired 0.x command surface rather than carrying aliases. Re-spec legacy FIS files through the `andthen:spec` skill before execution. This file is the whole migration: what changed in the model, the four steps to take, a safe copy-paste prompt that inventories your project first, and the dispositions for retired skills, agents, flags, operations, and artifacts.

Delete this file's usefulness by using it – once you are on 1.0 there is nothing here to come back to.


## What changed

The command surface moved because the model under it did:

- **`clarify` writes the PRD.** The `prd` skill is gone; `clarify` absorbed its input resolution, template, validation, and self-review, and `--brief` stops at an `intent.md` you can edit and share first.
- **Every FIS is a plan story.** Schema v2 `plan.json` is the one state shape – `spec` writes a one-story plan beside a standalone FIS, so there is no second schema and no sidecar.
- **State is derived, not stored.** The `State` and `State (local)` documents are retired: `plan.json` carries runtime state, and the `handoff` skill carries session continuity.
- **The `ops` skill is gone.** No script reads or writes `plan.json` any more – the session running a plan or spec edits the rows itself, and it is the only writer.
- **Review happens twice, in two places.** The story's own review runs inside `exec-spec` – one fresh reviewer subagent per run – and the plan-level `review --mode code,gap,security,outcome` is a separate fresh-session step that `exec-plan` hands over on its `Next:` line.
- **The plan bundle is branch-scoped.** `plan.json` and the FIS files are deleted before the merge, after each FIS's `## Implementation Observations` has been graduated into Learnings and Decisions; `prd.md` stays.
- **Situational flags became phrasing.** `architecture`, `ui-ux-design`, `testing`, and `review` infer the mode or lens from what you ask; the retired flag values are in the tables below.


## The migration in four steps

Before changing migration-sensitive files, make a clean commit or another recoverable copy.

**1. Refresh the installation you actually use.** For a Claude Code or Codex plugin install, [switch release lines](README.md#switching-release-lines-10-rc--0x) with `scripts/andthen-plugins.py`, which removes the 0.x plugin, installs the 1.0 plugin on both hosts, and verifies the version that landed. <!-- pre-release: name the released channel here --> During the preview, `rc` is the `develop` branch. For a loose `install-skills.sh` install, first record the old prefix and destination directories: the installer replaces each surviving owned skill bundle, so stale files inside it are removed, but it cannot remove the eleven retired skill directories or the 12 generated agent files. Review those exact targets, remove only confirmed 0.x AndThen files, then run the current installer. [Installation cleanup](#installation-cleanup) has the inventory, and covers switching from loose skills to a plugin without leaving duplicate commands.

**2. Retire the indexed State documents, not every same-named file.** Resolve the old `State` and `State (local)` entries from the Project Document Index. Preserve still-current content before removal: blocker detail in the governing FIS or a handoff, with story status set to `blocked` when applicable; durable decisions in Decisions/ADRs; durable traps in Learnings; focus and continuity in a handoff. Then remove the two Index entries and only the confirmed AndThen files they reference. An unrelated state file elsewhere is out of scope. Runtime state now lives in the schema v2 `plan.json` that governs the story – a one-story feature gets a one-story plan of its own, written by `spec` on the quick track or by `plan` from a PRD source. Reading it answers what is active, and the `handoff` skill carries session continuity.

**3. Re-run `/andthen:init`.** It scaffolds missing Core documents and offers missing Index entries and the optional role agents. It does not rewrite an existing Index header or a populated Product document, so two edits stay yours:
- **Add a `## Proportionality` section** to the Product document resolved from the Project Document Index (`docs/PRODUCT.md` is only the default) – stage, scale, standing technical non-goals. Every proposal skill sizes what it proposes against those facts, and an empty anchor degrades silently.
- **Repoint retired skill names** in your own `CLAUDE.md` / `AGENTS.md`, and in any scripts or aliases – the tables below map every one.

**4. Upgrade plans and unfinished work from a recoverable tree.** Re-run `/andthen:plan` from the original PRD for every schema v1 plan. V1 labels incompatible 0.x and early 1.0 shapes and is evidence only; 1.0 emits schema v2. On a v2 rerun, a story keeps its `status`, `owner`, FIS pointer, and completed task IDs only when its content did not drift and its FIS file is still beside the plan; the run reports which story IDs it preserved and which it reset, so inspect both lists and the diff. For an unfinished FIS with no plan beside it, run `/andthen:spec` from its original requirements source; if unavailable, use the legacy FIS as evidence only after making the recoverable copy.

The acceptance check is wider than runnable syntax: every present `Proof` and required `Verify` value must be enclosed in literal backticks and contain `path#test`, `cmd: <command>`, or `inspect: path:LINE`; every task must carry a valid `SATISFIES`; and every Acceptance Scenario and numbered Structural Criterion must be named by at least one task. A markdown `plan.md` is no longer read at all.

Prefer to have an agent do it? The prompt below inventories first, waits for your approval, and then applies only the actions you select.


## The migration prompt

Copy this whole file (GitHub's **Copy raw file** button) into an agent session **in your own project** (not in the AndThen repo), with AndThen 1.0 available – a plugin install does not ship it. The prompt is the block below; the tables after it are the retired-surface inventory it consumes. The first pass is read-only. Make a clean commit or another recoverable copy before approving any mutation in the second pass.

````text
You are migrating this project from AndThen 0.x to 1.0. Retired 0.x commands have
no compatibility aliases. Re-spec a legacy FIS through the andthen:spec skill before execution; use its
original requirements source, or the old FIS as evidence when that source is absent.

Use the retired-surface inventory in the sections after this prompt.
Work in two passes.

PASS 1 - INSPECT ONLY

Do not edit, delete, install, or publish anything. Return one numbered report, then
stop for approval.

1. Installation channel and residue
   - Determine whether this machine uses the Claude plugin, Codex plugin, loose
     install-skills.sh bundles, or more than one channel. If user-level locations or
     the old prefix are not visible, report them as unknown instead of guessing.
   - For a plugin channel, propose refreshing the andthen plugin. Report any
     simultaneously visible loose AndThen bundles as duplicates.
   - For a loose channel, resolve the actual prior prefix and skill/agent destination
     directories. Inventory the eleven retired skill directories and 12 generated agent
     files from the tables. Report exact existing paths only. Do not propose a wildcard
     or recursive deletion over an unresolved directory.
   - Report a user-level instruction file (~/.claude/CLAUDE.md, ~/.codex/AGENTS.md)
     whose Critical Rules copy matches the stale shape in the artifacts table.

2. Retired State documents and the Project Document Index
   - Find the Project Document Index in the root CLAUDE.md / AGENTS.md. Resolve the
     exact paths from rows named State and State (local). A same-named file elsewhere
     is unrelated unless there is separate evidence it is an AndThen artifact.
   - For each resolved file, verify the old AndThen shape: shared State begins
     "# Project State"; local State begins "# Local State (not committed)". Summarize
     any still-current blockers, decisions, focus, or continuity notes. Route blocker
     detail to the governing FIS or a handoff and set story status to blocked when
     applicable; durable decisions to Decisions/ADRs; durable traps to Learnings; focus
     and continuity to a handoff. Do not discard unique content.
   - Propose removal of the two retired Index rows and only the confirmed files after
     their useful content is preserved.

3. Product proportionality and init
   - Report whether the Product document resolved from the Index has a
     "## Proportionality" section. If missing, list the three questions pass 2 must ask:
     stage; scale facts (users, data, topology, maintainers); and standing technical
     non-goals. Do not ask them or write the section in pass 1.
   - Report the missing Core documents and Index rows that rerunning andthen:init can
     scaffold or offer. State separately that init does not retrofit the existing Index
     header or populated Product content and only offers role-agent installation.

4. Retired names and forms
   - Search root instruction files, docs, scripts, aliases, CI config, and automation
     prompts for every 0.x token in the pasted tables. Report each hit and its exact
     disposition. Do not treat tracker as a generic replacement for issue input,
     single-artifact issue publication, or PR comments.

5. Plans and unfinished work
   - Inspect schemaVersion before story shape. Every v1 plan must be regenerated from
     its original source: v1 labels incompatible 0.x and early 1.0 shapes and is
     evidence only. 1.0 emits schema v2; any other version is unsupported.
   - For every v2 plan with a story whose status is neither done nor skipped, report
     that rerunning andthen:plan is a full regeneration: a story keeps its status,
     owner, completed task IDs, and FIS pointer only when its content did not drift
     and its FIS file is still beside the plan. The run reports which story IDs it preserved and which it
     reset; both lists and the diff are what to inspect.
   - Classify legacy FIS files as plan-backed or standalone. For every FIS that may still
     be executed, report all completion blockers: each present Proof and required Verify must be
     enclosed in literal backticks and contain one of `path#test`, `cmd: <command>`,
     or `inspect: path:LINE`; every task must name real S<NN>/SC<NN> targets in
     SATISFIES; every Acceptance Scenario and numbered Structural Criterion must be
     named by at least one task.
   - Propose andthen:plan regeneration for an unfinished bundle. For a standalone FIS,
     propose andthen:spec from the original requirements source, or use the legacy FIS
     only as evidence when the source is unavailable. Both are mutation-phase actions.

6. Legacy plan files
   - Report any markdown plan.md. AndThen 1.0 does not read it. Do not delete it until
     any still-needed content is represented in plan.json, a PRD, or another owner.

For each finding, give the evidence, exact proposed action, possible information loss,
and verification after the action. Then STOP. Do not ask migration questions yet.

PASS 2 - ONLY AFTER EXPLICIT APPROVAL

Confirm that a clean commit or another recoverable copy exists. Ask only the unresolved
questions needed for approved items. Apply only those items, using exact validated paths.
Never delete by basename, wildcard, unresolved prefix, or broad directory. Write
"unknown" for an approved Proportionality fact the user cannot answer, never a TODO.
Afterward, condition each check on the approved action: refresh the selected plugin or
rerun the installer only when installation cleanup was approved; rerun andthen:init only
when selected; check a regenerated v2 plan against plan.schema.json. Always
re-scan retired tokens and report the resulting diff and every skipped or reset item.
````


## Installation cleanup

For a plugin install, refresh the `andthen` plugin through that host's plugin manager. If switching from a loose install to a plugin, clean up the confirmed loose targets below so both naming schemes do not remain visible.

The 0.x loose installer could use custom destinations and a custom `--prefix`; resolve both before touching anything. With the default prefix, the eleven retired skill directories are:

```
andthen-excalidraw-diagram/
andthen-issue-triage/
andthen-map-codebase/
andthen-merge-resolve/
andthen-prd/
andthen-preflight/
andthen-quick-implement/
andthen-quick-review/
andthen-refactor/
andthen-remediate-findings/
andthen-ubiquitous-language/
```

The 12 retired generated-agent basenames are:

```
documentation-lookup
research
review-agent-workflow
review-architecture
review-correctness
review-critic
review-devils-advocate
review-product-requirements
review-project-standards
review-security
review-synthesis-challenger
review-testing
```

The installed files used `<prefix><basename>.toml` in the old Codex agents directory and `<prefix><basename>.md` in the old Claude agents directory. List exact matches and confirm ownership before removal. Reinstalling 1.0 replaces each surviving owned skill directory, removing stale files inside it, but does not remove these retired directories or agents.


## Where the 0.x skills went

| 0.x surface | 1.0 disposition |
|---|---|
| `prd` in every form | Retired with no alias. `/andthen:clarify <same source>` writes the PRD now – it absorbed the input resolution, the template, the validation and the self-review; there is no non-interactive form – an unattended pipeline starts at `/andthen:plan` from the requirements file or issue. |
| `remediate-findings` | Renamed with no alias: `/andthen:implement-fix <report>`. Same six phases, same Fix bar, same `## Remediation Status` annotation ([ADR-016](docs/adrs/ADR-016-one-no-spec-change-skill.md)). |
| `quick-implement`, its `--tdd` flag, and its commit/PR creation | Retired into the same skill: `/andthen:implement-fix "<request>"` reads your sentence as its whole Fix set. Use `/andthen:testing --mode tdd` for strict TDD, and commit and open the PR by hand – the verified change is left in the working tree. |
| `quick-review` | Use `/andthen:review --quick` for the same ad hoc sanity-review intent. `--quick --fix` applies Fix-routed findings inline, as `quick-review --fix` did. The old `commit <sha>` shorthand has no exact replacement: first pin that commit with project Git tooling, then give the ordinary review its diff and changed-file set as explicit scope. The per-story review is executor-owned: `exec-spec` performs it, sized to the change. |
| `preflight`, Persisted Decision Blocks, `Preflight:` | The skill retires; its interview is the Preflight step that closes `/andthen:plan` and `/andthen:spec`, ending in `Closure: READY` or `Closure: BLOCKED`. |
| `refactor` | `/andthen:simplify-code` |
| `map-codebase` | `/andthen:describe --mode codebase` |
| `ubiquitous-language` | `/andthen:describe --mode domain` |
| `issue-triage` | `/andthen:backlog-triage` |
| `review --council` | Retired – `review`'s inline Findings Filter carries Devil's Advocate and Synthesis Challenger; the seats had no trigger that was not inference from phrasing. |
| Deep security orchestration in `review` | `/andthen:review --mode security` carries exposure calibration; the OWASP checklists and threat-modelling orchestration are retired. |
| `architecture` modes `review`, `decompose`, `fitness`, `strategic-design`, `event-storming`, and deep-mode chains | `/andthen:architecture` with the matching `--mode`, chains included. Unchanged from 0.x. |
| `e2e-test` | Retired – drive the browser directly; `visual-validation` captures and judges screens. |
| `spike`, `simplify-code` | Same skill names under `andthen:` – `/andthen:spike`, `/andthen:simplify-code`. |
| `visualize`, `explain-changes` | Removed – AndThen owns the artifact contracts, not the rendered views; no replacement. |
| `excalidraw-diagram` | Removed – a diagramming tool is outside AndThen's scope; no replacement. |
| Internal `merge-resolve` | Removed with team/worktree orchestration; no standalone replacement. Resolve host-managed branch conflicts through the normal project workflow. |


## Retired flags and forms

The `ops` skill and its script are gone in 1.0. Every `plan.json` write is the run session's own edit, per `plan.schema.json`; every markdown document was always agent-edited.

| 0.x form | 1.0 disposition |
|---|---|
| `quick-implement --issue <number>` | The shorthand is removed. Fetch and review the issue through the configured tracker and pass the approved small-fix requirements inline to `/andthen:implement-fix`, which leaves the verified change in the working tree for you to commit and push. Route larger work through the same issue URL passed to `/andthen:spec` or `/andthen:plan` instead. |
| `--issue <number>` | Pass the full issue URL positionally to `/andthen:clarify`, `/andthen:spec`, `/andthen:plan`, or `/andthen:triage` where that issue supplies input. |
| `--from-issue` | No materialized reverse-sync mode. Pass the issue URL to `/andthen:plan`, then `/andthen:exec-plan`. |
| `--create-story-issues`, or publishing a local plan as tracker work | `/andthen:tracker publish <plan.json>` creates the parent and child issues and refreshes them on a re-run. |
| `--to-issue` | No generic single-artifact publisher. For a plan bundle only, use tracker `publish`; for a PRD/report/triage artifact, publish explicitly with the configured tracker or host CLI after reviewing the payload. |
| `--to-pr` | No generic report/comment publisher. PR input is the target – `/andthen:review "PR <number>"`; post output explicitly through the host when wanted. |
| `review --from-pr <number>`, `review --worktree` | The PR is the positional target: `/andthen:review "PR <number>"` reviews it in a scratch worktree, so neither flag is needed. |
| `--team`, `--max-parallel` | Removed with Agent Teams orchestration and the `merge-resolve` skill. `exec-plan --worktree` stays: one worktree per story of a ready batch (about five), merged back with `git merge --no-ff` – plain merge instead of squash, no bash scripts. |
| Installer `--codex-agents-dir`, `--no-codex-agents`, `--claude-agents-dir` | Removed because 1.0's loose installer installs no agents. `/andthen:init` offers the four optional role-agent templates (`oracle`, `implementer`, `reviewer`, `worker`) instead. |
| `scripts/generate-codex-agents.sh` | Removed with generated agents; role agents now come from `/andthen:init` templates. |
| `review --inline-findings` | Ask `/andthen:review` to return the structured findings in the conversation. |
| `review --fanout`, `review --no-fanout` | Fan-out is selected from scope shape; ask to partition explicitly, or ask to keep the review in one pass. |
| `review --mode mixed` | Omit the mode and let the lens set resolve, or give an explicit comma-separated chain such as `--mode code,gap`. |
| `review --mode doc` | Retired. Document review is an authoring gate: `/andthen:clarify`, `/andthen:spec`, and `/andthen:plan` each close on a fresh-context self-review of what they wrote, and a requirements document is reviewed again as a baseline under `--mode gap` or `--mode outcome`. Documentation as a deliverable is a `--mode code` surface. |
| `architecture --count <N>` | State the requested number of alternatives in the trade-off request. |
| `architecture --mode advise` | Omit the mode and ask the architecture question; advice is inferred. |
| `ui-ux-design --mode research`, `design-system`, or `wireframes`, including chains | State the intent and order in words; mode selection is inferred. |
| `ui-ux-design --mode review` | `/andthen:visual-validation` |
| `testing --mode write` | `/andthen:testing <target>`; test authoring is the no-flag default. |
| `testing --mode strategy` | Same token, different job: it authors the `Testing Strategy` document (`docs/TESTING-STRATEGY.md`) instead of assessing coverage and ranking risk. For 0.x's read-only assessment, ask `/andthen:testing` for it on a scope – no mode performs it. |
| `clarify --mode product`, `clarify --mode feature` | State whether the request concerns the whole product or one feature. |
| `quick-implement --pr`, `quick-implement --no-pr` | Both are gone. `/andthen:implement-fix` never commits or pushes; commit and open the PR yourself. |
| `now-what --no-handoff` | Ask `/andthen:now-what` for a recommendation only, without invoking the next skill. |
| `handoff --no-mutate` | Ask `/andthen:handoff` for the doc only; every durable write it makes is idempotent, so the opt-out guarded nothing. |
| `issue-triage --limit <N>` | Use `/andthen:backlog-triage` and state the item cap in the request. |
| `map-codebase --model-only` | `/andthen:describe --mode codebase --model-only`. |
| `triage --investigate` | `/andthen:triage --plan-only` |
| `triage --headless` | `/andthen:triage --auto` |
| `ubiquitous-language --update` | `/andthen:describe --mode domain`; merging into the existing glossary is the default. |
| `simplify-code --path <path>` | Pass the path as positional scope to `/andthen:simplify-code`. |
| `--visual` | Removed in 1.0; no visual step. Skills print the artifact path and you read the markdown. |
| `--skip-review` | Remove it. 1.0 authoring/execution review gates have no bypass. |
| `--defer-shared-writes` | Remove it. It was an internal team/worktree caller contract and has no standalone replacement. |
| `GOVERNING PLAN PATH:` caller line | Remove it. A plan-backed FIS names its own plan in its `**Plan**:` header, which is what every consumer resolves. |
| `Story-Gate: PASS \| FAIL` verdict lines and `.agent_temp/story-gate-*.md` reports | Removed with the story gate. The per-story review reports what it reviewed on the completion report's `Reviewed:` line, and open findings go to `/andthen:review` then `/andthen:implement-fix`. Existing report files are historical; nothing reads them. |
| Legacy plan `--skip-specs`, `--stories`, `--phase` | Remove them. A 1.0 plan is a complete `plan.json` + FIS bundle and execution consumes that bundle; narrow the PRD or regenerate a smaller plan instead. |
| `ops complete-task`, `ops complete-story`, `ops update-plan*`, `ops validate-plan`, `ops progress`, `ops merge-story`, `ops commit` | The verb surface is gone with the skill. The session running `/andthen:exec-plan` or `/andthen:exec-spec` is `plan.json`'s only writer: it edits the story's row per `plan.schema.json` – `done` only together with the `verified` line quoting executed proof output – commits with `git add -- <paths>` then `git commit`, and merges a story branch with `git merge --no-ff`. |
| `ops update-state`, `ops read-state` | State is derived: read `plan.json`. `/andthen:handoff` carries session continuity; migrate durable content before deleting the old State documents. |
| `ops update-ledger` and the reconciliation ledger | Append the drift note to the FIS's `## Implementation Observations` with your editor; there is no separate ledger. |
| `ops update-fis ...` in every form, `ops update-decisions` | The FIS is agent-read: append to `## Implementation Observations` or `## Discovered Requirements` yourself. Preflight owns FIS-local resolution; use `/andthen:architecture --mode trade-off` for an ADR or maintain the Decisions document for durable project choices. |
| `ops update-tech-debt append <body>` | Append the entry to the Tech Debt backlog yourself, under the severity heading it belongs to; first judge whether it is unknown to a frontier model, absent from code/history, and durable beyond this initiative. |
| `ops update-learnings add\|remove\|error ...` | Read the Learnings document and append one bullet under the fitting topic with your editor. Before appending, judge whether the entry is unknown to a frontier model, absent from code/history, and durable beyond this initiative. |
| `ops changelog` | Edit the project changelog under its own project rules. |
| `ops stale`, `ops branch` | Removed. `stale` had no caller; a branch is `{type}/{story-id}-{slug}`, named by hand. |


## Retired artifacts and fields

| 0.x artifact | 1.0 disposition |
|---|---|
| `requirements-clarification.md` | `intent.md`, in the same feature directory. Rename existing files (`git mv`) so `/andthen:clarify` finds them as baselines to fold into the PRD, and repoint any script or alias naming the old path. The document's H1 becomes `# Intent: <name>`. |
| Indexed `STATE.md`, `STATE.local.md` | Derived state from `plan.json`; session continuity through `/andthen:handoff`. Preserve useful content, then remove the Index rows and confirmed files. |
| Markdown `plan.md` | `plan.json`; preserve unique requirements in the PRD or regenerated plan before retiring the markdown file. |
| Schema v1 `plan.json`, legacy metadata, and removed scheduling fields | Re-run `/andthen:plan` from the PRD to emit schema v2; v1 state is evidence only and never migrates. Inspect the diff rather than editing schema fields by hand. |
| Reconciliation ledger | FIS Drift Notes under `## Implementation Observations`. |
| Free-prose `Proof` / `Verify`, unbound scenarios or Structural Criteria | Re-spec to the three runnable proof forms and complete task `SATISFIES` coverage: `/andthen:exec-spec` stops on a violation before the first edit, and it is what runs those targets. |
| Source Trust enum/header and `UNTRUSTED REQUIREMENTS DATA:` artifact line | Artifacts retain a durable `> **Source**: <path-or-url>` pointer; fetched content is still treated as evidence rather than instructions at read time. |
| User-level `# Critical Rules and Guardrails` copy carrying a `## Working Style` section | A pre-0.40 copy: its conversation rules now ship as the `concise-critical` output style, so with the style enabled they load twice. Replace the block, from that heading to the next top-level heading, with the current guideline body, or remove it once the project adopts the rules through `/andthen:init`. |
| `learnings/` topic shards | Keep them. A shard is a convention now – a topic file the Learnings index points at with one line – with no ceiling, graduation, or prune verb: shard when appending would make the index long, and what to drop is yours. |
| `scripts/validate-plan-json.sh` | No script. The skill that writes a plan checks its candidate against `plan.schema.json`. |
| `docs/OUT-OF-SCOPE.md` (Out of Scope Registry) and its Index row | Retired. A firmly rejected concept is one dated bullet in the Product document's Non-Goals; move each `## <Concept>` section there by hand (decision, date, prior requests on one line) and drop the Index row – left in place it is inert, not an error. |
| `[TI<NN>]` scenario tags | Retired from the FIS grammar; `SATISFIES` is the one trace between a task and what it proves. A spec still carrying the tag parses unchanged – it reads as title text – so the tag alone forces no re-spec. |
| The Project Document Index as a three-column table | Keeps working – nothing parses it – but 1.0 entries are two lines: name and location, then the read/update trigger that tells a skill when to open the document. `/andthen:init` does not rewrite an existing Index; copy the entry shape from its template when you want the triggers. |
| Index rows `Product Backlog` and `Changelog` | Gone from the `init` template. No skill reads a backlog, a deferral stays in its PRD's Out of Scope and a put-off fix goes to the Tech Debt row, and a completed story adds the project's changelog entry when the project keeps one. Existing rows are inert, not an error. |
| Root instruction file `### Visual Validation Workflow` section | The `Visual Validation` Index document (`docs/VISUAL-VALIDATION.md`). Move the section's content there and delete the section – only a validator needs a capture procedure, and an instruction file is read on every turn of every session. `/andthen:visual-validation --mode setup` serves the app, proves the procedure, and writes the document; the skill reads no section. |
| Index row `Stack` and `docs/STACK.md` | Retired; nothing reads the file. What it carried lives in the `Architecture` document (System Overview, Integration Points), `Decisions`, and the manifest and lockfile. |
| Index row `Diagram Style Guide` | Retired with `excalidraw-diagram`; drop the row. |
| Index rows `Architecture Model` and `Domain Model` (`.agent_temp/models/*.json`) | Replaced by one `Models` entry, default `docs/models/`: `/andthen:describe --model` writes committed projections there. No verb gates them – `validate-model` is retired and the model reference is the contract. Replace the two rows with it; the old transient files are stale and nothing reads them. |

Everything else that changed is in [CHANGELOG.md](CHANGELOG.md).
