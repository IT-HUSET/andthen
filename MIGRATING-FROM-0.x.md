# Migrating from AndThen 0.x to 1.0

1.0 removes retired 0.x skills and flags outright – there are no compatibility aliases. 1.0 does not run a 0.x Feature Implementation Specification (FIS, the per-story spec an agent executes); unfinished work is re-planned from its requirements.

This guide has four upgrade steps, an optional prompt that has your agent carry them out, and tables mapping every retired name to its 1.0 replacement. Once you are on 1.0 you will not need it again.


## What changes for you

- **The `andthen:clarify` skill writes the PRD.** The `prd` skill is gone. `clarify --brief` stops at an `intent.md` you can edit and share first.
- **Every FIS belongs to a plan.** A plan bundle is a feature directory holding a schema v2 `plan.json` and one FIS per story. The `andthen:spec` skill writes a one-story plan beside a standalone FIS, so there is one state format and no sidecar.
- **State lives in `plan.json`.** The `State` and `State (local)` documents are retired; the `andthen:handoff` skill carries continuity between sessions.
- **The `ops` skill is gone.** No script writes `plan.json`. The session running a plan or spec edits it directly and is its only writer.
- **Review runs twice.** The `andthen:exec-spec` skill reviews each story with one fresh reviewer subagent per run. The plan-level `review --mode code,gap,security,outcome` is a separate step in a fresh session, which the `andthen:exec-plan` skill hands over on its `Next:` line.
- **The plan bundle lives only on its branch.** Before the merge, move each FIS's `## Implementation Observations` into Learnings and Decisions, then delete `plan.json` and the FIS files. `prd.md` stays.
- **Many flags became plain requests.** The `architecture`, `ui-ux-design`, `testing`, and `review` skills infer the mode or lens from what you ask. The tables below map every retired flag.


## Upgrade in four steps

Do it one of two ways: follow the steps below by hand, or paste [the migration prompt](#the-migration-prompt) into an agent session. The prompt carries out the same steps and adds nothing to them. It reports what it would change and applies only what you approve. Either way, make a clean commit, or another copy you can restore, before changing anything.

Each step says when it applies; skip the ones that don't.

**1. Update your installation.** Always.

- **Plugin (Claude Code or Codex):** run the README's [develop-branch install commands](README.md#10-release-candidate-from-the-develop-branch). They remove the old `andthen` marketplace – on Claude Code that also uninstalls the 0.x plugin – and add `IT-HUSET/andthen@develop` on both hosts. The host's plugin cache (`~/.claude/plugins/cache`, `~/.codex/plugins/cache`) refreshes itself; leave it alone. <!-- pre-release: point this at the released install once 1.0 ships on main -->
- **Loose `install-skills.sh` install:** the current installer updates the skills it still ships but does not remove retired ones. Note the prefix and the skill and agent directories your 0.x install used, remove the retired files listed under [Installation cleanup](#installation-cleanup-loose-installs-only) once you confirm each is AndThen's, then run the current installer.
- **Moving from loose skills to the plugin:** remove the loose ones the same way, or both naming schemes stay visible as duplicate commands.

Done when `/andthen:clarify` is available and no retired skill such as `prd` is still offered.

**2. Retire the State documents.** When your Project Document Index (the document list in your root `CLAUDE.md` or `AGENTS.md`) has `State` or `State (local)` entries. Before removing anything, move what is still current:

- blockers to the governing FIS or a handoff, setting the story's status to `blocked` where it applies;
- durable decisions to Decisions or ADRs;
- durable traps to Learnings;
- current focus and continuity to a handoff.

Then remove the two Index entries and only the AndThen files they point at. A same-named state file elsewhere is unrelated; leave it. From now on `plan.json` answers what is active: the `andthen:spec` skill writes a one-story plan for a small feature, and the `andthen:plan` skill writes one from a PRD.

**3. Refresh the project setup.** Always. Re-run `/andthen:init`: it adds missing Core documents and offers missing Index entries and the optional role agents. It leaves an existing Index header and a populated Product document alone, so two edits are yours:

- **Add a `## Proportionality` section** to the Product document your Index names (`docs/PRODUCT.md` by default): the project's stage, scale, and standing technical non-goals. Every skill that proposes work sizes it against these facts, and without them that sizing degrades silently.
- **Repoint retired names** in your own `CLAUDE.md` / `AGENTS.md`, docs, scripts, aliases, and CI config, using the tables below. This search finds the retired skills in both naming schemes; retired flags are in the tables:

  ```
  rg -n 'andthen[:-](prd|quick-implement|quick-review|remediate-findings|preflight|refactor|map-codebase|ubiquitous-language|issue-triage|e2e-test|visualize|explain-changes|excalidraw-diagram|merge-resolve|ops)\b'
  ```

**4. Regenerate unexecuted plans and specs.** When a plan or FIS is not fully executed yet. 1.0 runs neither a 0.x plan nor a 0.x FIS – the `andthen:exec-spec` skill stops before its first edit when the story is not in a schema v2 `plan.json` – and nothing converts them in place, so you regenerate them in 1.0 form. Finished plans and FIS files need nothing – keep them as history or delete them.

- **A 0.x plan** (schema v1 `plan.json` or markdown `plan.md`, with its FIS files): `/andthen:plan` refuses to regenerate over a v1 `plan.json`, and the old FIS files sit at the paths the new ones take. So first `git mv` the old plan and its FIS files into a `0.x/` folder beside the PRD. If some stories are already implemented, mark them out of scope in the PRD. Then run `/andthen:plan <feature-dir>`. It works from the PRD alone, so a decision an old FIS settled comes back as a question; answer it from `0.x/`. Delete `0.x/` once the new bundle is in place.
- **A standalone 0.x FIS** (no `**Plan**:` line under its title): run `/andthen:spec <old-fis>`. 1.0 reads it as a requirements note, so what it settled carries over, and writes the new FIS and a one-story plan beside it. Delete the old file afterwards.
- **An unfinished schema v2 `plan.json`** from a 1.0 release candidate: re-running `/andthen:plan` keeps each story whose content did not drift and lists the story IDs it kept and reset; check both lists.


## The migration prompt

Optional – the four steps above are the whole migration. Copy this whole file (GitHub's **Copy raw file** button) into an agent session **in your own project**, not the AndThen repo, with AndThen 1.0 installed. The plugin does not ship this file, and the prompt works from the steps above it and the inventory below it. Pass 1 only reads and reports; make a clean commit or another recoverable copy before you approve any change in pass 2.

````text
You are migrating this project from AndThen 0.x to 1.0. The rest of this file is the
contract: "Upgrade in four steps" says what changes, and the sections after this
prompt map every retired 0.x name, which has no alias, to its 1.0 disposition.

Work in two passes. Instruction files, State documents, and plans hold content that
exists nowhere else, and a deletion cannot be undone, so nothing changes until the user
has seen the whole inventory and approved each action.

PASS 1 - INSPECT ONLY

Do not edit, delete, install, or publish anything. Return one numbered report of what
each of the four steps would change in this project: the evidence, the exact proposed
action, and any information it could lose. Report what you cannot see, such as a
user-level directory or the old install prefix, as unknown rather than guessing.
Beyond the steps:

- Installation: name every channel in use (Claude plugin, Codex plugin, loose
  install-skills.sh bundles) and report loose AndThen bundles beside a plugin as
  duplicates. For a loose channel, resolve the actual prior prefix and directories,
  and list the files from "Installation cleanup" that exist, by exact path. Plugin
  caches (~/.claude/plugins/cache, ~/.codex/plugins/cache) belong to the host, which
  refreshes them on reinstall; never propose deleting from them. Report a
  user-level instruction file (~/.claude/CLAUDE.md, ~/.codex/AGENTS.md) whose
  Critical Rules copy has the stale shape in "Retired files and fields".
- State: resolve paths only from the State and State (local) Index rows, confirm the
  AndThen shape (shared State begins "# Project State", local State begins
  "# Local State (not committed)"), and summarize still-current content with its
  step 2 destination, so nothing unique is discarded.
- Proportionality: if the section is missing, list the three questions pass 2 will
  ask – stage; scale facts (users, data, topology, maintainers); standing technical
  non-goals – without asking them.
- Retired names: search root instruction files, docs, scripts, aliases, CI config,
  and automation prompts for every 0.x token in the tables, and report each hit with
  its disposition.
- Unexecuted work: list each plan with a story neither done nor skipped (naming the
  stories already done) and each standalone FIS not yet executed, with the step 4
  actions it needs. Do not audit the contents of old FIS files; finished work needs
  nothing.

Then STOP. Do not ask migration questions yet.

PASS 2 - ONLY AFTER EXPLICIT APPROVAL

Confirm that a clean commit or another recoverable copy exists. Ask only the open
questions the approved items need, and apply only those items, at exact validated
paths. Never delete by basename, wildcard, unresolved prefix, or broad directory.
Write "unknown" for a Proportionality fact the user cannot answer, never a TODO.
Finish by re-scanning for retired tokens and reporting the diff and every skipped or
reset item.
````


## Retired skills

| 0.x skill | In 1.0 |
|---|---|
| `prd`, in every form | Retired. `/andthen:clarify <same source>` writes the PRD. It has no non-interactive form: an unattended pipeline starts at `/andthen:plan` from the requirements file or issue. |
| `remediate-findings` | `/andthen:implement-fix <report>` – same six phases, Fix bar, and `## Remediation Status` annotation ([ADR-016](docs/adrs/ADR-016-one-no-spec-change-skill.md)). |
| `quick-implement`, its `--tdd` flag, and its commit/PR creation | `/andthen:implement-fix "<request>"`, which treats your sentence as its whole Fix set. For strict TDD, use `/andthen:testing --mode tdd`. The verified change is left in the working tree; commit and open the PR yourself. |
| `quick-review` | `/andthen:review --quick`; `--quick --fix` applies Fix-routed findings inline, as `quick-review --fix` did. The `commit <sha>` shorthand has no replacement: pin the commit with your Git tooling, then give the review its diff and changed files as explicit scope. The per-story review runs inside `exec-spec`, sized to the change. |
| `preflight`, Persisted Decision Blocks, `Preflight:` | Now the Preflight step that closes `/andthen:plan` and `/andthen:spec`, ending on the next command. There is no verdict line and no held story: under `--auto`, or when a question goes unanswered, the recommendation becomes an `ASSUMPTION:` in the FIS. |
| `refactor` | `/andthen:simplify-code` |
| `map-codebase` | `/andthen:describe --mode codebase` |
| `ubiquitous-language` | `/andthen:describe --mode domain` |
| `issue-triage` | `/andthen:backlog-triage` |
| `review --council` | Retired. The Findings Filter built into `review` carries the Devil's Advocate and Synthesis Challenger seats. |
| Deep security orchestration in `review` | `/andthen:review --mode security`, with exposure calibration. The OWASP checklists and threat-modelling orchestration are retired. |
| `architecture` modes `review`, `decompose`, `fitness`, `strategic-design`, `event-storming`, and deep-mode chains | Unchanged: `/andthen:architecture` with the matching `--mode`, chains included. |
| `e2e-test` | Retired. Drive the browser directly; the `visual-validation` skill captures and judges screens. |
| `spike`, `simplify-code` | Unchanged: `/andthen:spike`, `/andthen:simplify-code`. |
| `visualize`, `explain-changes` | Removed with no replacement; AndThen owns the artifact contracts, not rendered views. |
| `excalidraw-diagram` | Removed with no replacement; diagramming is outside AndThen's scope. |
| Internal `merge-resolve` | Removed with team/worktree orchestration. Resolve branch conflicts through your normal workflow. |


## Retired flags, forms, and `ops` commands

The `ops` skill and its script are gone. The session running a plan edits `plan.json` itself, per `plan.schema.json`; markdown documents were always agent-edited.

| 0.x form | In 1.0 |
|---|---|
| `quick-implement --issue <number>` | Fetch and review the issue through your tracker, then pass the approved small-fix requirements inline to `/andthen:implement-fix`; commit and push the change yourself. For larger work, pass the issue URL to `/andthen:spec` or `/andthen:plan`. |
| `--issue <number>` | Pass the full issue URL positionally to `/andthen:clarify`, `/andthen:spec`, `/andthen:plan`, or `/andthen:triage`. |
| `--from-issue` | No reverse-sync mode. Pass the issue URL to `/andthen:plan`, then run `/andthen:exec-plan`. |
| `--create-story-issues`, or publishing a local plan as tracker work | `/andthen:tracker publish <plan.json>` creates the parent and child issues and updates them on a re-run. |
| `--to-issue` | No general publisher. For a plan bundle, use tracker `publish`. Publish a PRD, report, or triage artifact yourself through your tracker or host CLI after reviewing it. |
| `--to-pr` | No report or comment publisher. A PR is a review target – `/andthen:review "PR <number>"`; post output through the host yourself if wanted. |
| `review --from-pr <number>`, `review --worktree` | `/andthen:review "PR <number>"` reviews the PR in a scratch worktree, so neither flag is needed. |
| `--team`, `--max-parallel` | Removed with Agent Teams orchestration and `merge-resolve`. `exec-plan --worktree` remains: one worktree per story of a ready batch (about five), merged back with `git merge --no-ff` rather than squashed. |
| Installer `--codex-agents-dir`, `--no-codex-agents`, `--claude-agents-dir` | Removed: the 1.0 loose installer installs no agents. `/andthen:init` offers the four optional role agents (`oracle`, `implementer`, `reviewer`, `worker`) instead. |
| `scripts/generate-codex-agents.sh` | Removed; role agents come from `/andthen:init` templates. |
| `review --inline-findings` | Ask `/andthen:review` to return the structured findings in the conversation. |
| `review --fanout`, `review --no-fanout` | Fan-out follows the scope's shape. Ask to partition, or ask to keep the review in one pass. |
| `review --mode mixed` | Omit the mode, or name a comma-separated chain such as `--mode code,gap`. |
| `review --mode doc` | Retired. `/andthen:clarify`, `/andthen:spec`, and `/andthen:plan` each self-review what they write in a fresh context; `--mode gap` or `--mode outcome` reviews a requirements document again as the baseline; documentation shipped as a deliverable falls under `--mode code`. |
| `architecture --count <N>` | Say how many alternatives you want in the trade-off request. |
| `architecture --mode advise` | Omit the mode and ask the question; advice is inferred. |
| `ui-ux-design --mode research`, `design-system`, or `wireframes`, including chains | Say what you want and in which order; the mode is inferred. |
| `ui-ux-design --mode review` | `/andthen:visual-validation` |
| `testing --mode write` | `/andthen:testing <target>`; writing tests is the default. |
| `testing --mode strategy` | Same flag, new job: it writes the `Testing Strategy` document (`docs/TESTING-STRATEGY.md`). For 0.x's read-only coverage and risk assessment, ask `/andthen:testing` for it on a scope; no mode does it. |
| `clarify --mode product`, `clarify --mode feature` | Say whether the request is about the whole product or one feature. |
| `quick-implement --pr`, `quick-implement --no-pr` | Gone. `/andthen:implement-fix` never commits or pushes; commit and open the PR yourself. |
| `now-what --no-handoff` | Ask `/andthen:now-what` for a recommendation only, without running the next skill. |
| `handoff --no-mutate` | Ask `/andthen:handoff` for the document only. Its durable writes are idempotent, so there is nothing to opt out of. |
| `issue-triage --limit <N>` | `/andthen:backlog-triage`, with the item cap stated in the request. |
| `map-codebase --model-only` | `/andthen:describe --mode codebase --model-only` |
| `triage --investigate` | `/andthen:triage --plan-only` |
| `triage --headless` | `/andthen:triage --auto` |
| `ubiquitous-language --update` | `/andthen:describe --mode domain`; it merges into the existing glossary by default. |
| `simplify-code --path <path>` | Pass the path as positional scope to `/andthen:simplify-code`. |
| `--visual` | Removed. Skills print the artifact path, and you read the markdown. |
| `--skip-review` | Remove it. 1.0's authoring and execution review gates have no bypass. |
| `--defer-shared-writes` | Remove it; an internal team/worktree contract with no replacement. |
| `GOVERNING PLAN PATH:` caller line | Remove it. A plan-backed FIS names its plan in its `**Plan**:` header, which every consumer reads. |
| `Story-Gate: PASS \| FAIL` lines and `.agent_temp/story-gate-*.md` reports | Removed with the story gate. The per-story review reports on the completion report's `Reviewed:` line; open findings go to `/andthen:review`, then `/andthen:implement-fix`. Nothing reads the old report files. |
| Legacy plan `--skip-specs`, `--stories`, `--phase` | Remove them. A 1.0 plan is a complete `plan.json` + FIS bundle, executed as a whole; narrow the PRD or generate a smaller plan instead. |
| `ops complete-task`, `ops complete-story`, `ops update-plan*`, `ops validate-plan`, `ops progress`, `ops merge-story`, `ops commit` | The session running `/andthen:exec-plan` or `/andthen:exec-spec` is `plan.json`'s only writer. It edits the story's row per `plan.schema.json` (`done` only together with the `verified` line quoting executed proof output), commits with `git add -- <paths>` then `git commit`, and merges a story branch with `git merge --no-ff`. |
| `ops update-state`, `ops read-state` | Read `plan.json`; `/andthen:handoff` carries session continuity. Retire the old State documents as in step 2. |
| `ops update-ledger` and the reconciliation ledger | Append the drift note to the FIS's `## Implementation Observations` yourself; there is no separate ledger. |
| `ops update-fis ...` in every form, `ops update-decisions` | Append to the FIS's `## Implementation Observations` or `## Discovered Requirements` yourself. Preflight settles FIS-local questions. For a durable project choice, use `/andthen:architecture --mode trade-off` for an ADR or edit the Decisions document. |
| `ops update-tech-debt append <body>`, `ops update-learnings add\|remove\|error ...` | Edit the document yourself: a Tech Debt entry under its severity heading, or one Learnings bullet under the fitting topic. First check that the entry is unknown to a frontier model, absent from code and history, and durable beyond this initiative. |
| `ops changelog` | Edit the project changelog under its own rules. |
| `ops stale`, `ops branch` | Removed. Name a branch `{type}/{story-id}-{slug}` by hand. |


## Retired files and fields

| 0.x file or field | In 1.0 |
|---|---|
| `requirements-clarification.md` | `intent.md`, in the same feature directory, with the H1 `# Intent: <name>`. Rename existing files with `git mv` so `/andthen:clarify` finds them as baselines to fold into the PRD, and repoint any script or alias naming the old path. |
| Indexed `STATE.md`, `STATE.local.md` | Retire them as in step 2. |
| Markdown `plan.md` | `plan.json`; see step 4. |
| Schema v1 `plan.json`, legacy metadata, and removed scheduling fields | Re-run `/andthen:plan` from the PRD (step 4); v1 state never migrates. Inspect the diff rather than editing schema fields by hand. |
| Reconciliation ledger | FIS Drift Notes under `## Implementation Observations`. |
| 0.x FIS shape (free-prose `Proof` / `Verify`, unbound scenarios or Structural Criteria) | Never converted in place. An unexecuted one is regenerated (step 4); a finished one needs nothing. |
| Source Trust enum/header and `UNTRUSTED REQUIREMENTS DATA:` artifact line | Artifacts keep a durable `> **Source**: <path-or-url>` pointer; fetched content is still treated as evidence, not instructions, when read. |
| User-level `# Critical Rules and Guardrails` copy carrying a `## Working Style` section | A pre-0.40 copy. Its conversation rules now ship as the `concise-critical` output style, so with the style enabled they load twice. Replace the block, from that heading to the next top-level heading, with the current guideline body, or remove it once the project adopts the rules through `/andthen:init`. |
| `learnings/` topic shards | Keep them. A shard is a topic file the Learnings index points at in one line, with no ceiling, graduation, or prune verb: shard when appending would make the index long, and what to drop is your call. |
| `scripts/validate-plan-json.sh` | No script. The skill that writes a plan checks it against `plan.schema.json`. |
| `docs/OUT-OF-SCOPE.md` (Out of Scope Registry) and its Index row | Retired. Move each `## <Concept>` section by hand into the Product document's Non-Goals as one dated bullet (decision, date, prior requests on one line), then drop the Index row. Left in place, it is inert. |
| `[TI<NN>]` scenario tags | Retired; `SATISFIES` alone links a task to what it proves. A spec still carrying the tag parses unchanged (it reads as title text), so the tag alone forces no re-spec. |
| The Project Document Index as a three-column table | Still works; nothing parses it. A 1.0 entry is two lines: name and location, then the read/update trigger that tells a skill when to open the document. `/andthen:init` does not rewrite an existing Index; copy the entry shape from its template to get the triggers. |
| Index rows `Product Backlog` and `Changelog` | Dropped from the `init` template; existing rows are inert. No skill reads a backlog: a deferral stays in its PRD's Out of Scope, a put-off fix goes to Tech Debt, and a completed story adds the changelog entry when the project keeps one. |
| Root instruction file `### Visual Validation Workflow` section | Move its content to the `Visual Validation` Index document (`docs/VISUAL-VALIDATION.md`) and delete the section, which no skill reads: an instruction file loads on every turn, and only a validator needs the capture procedure. `/andthen:visual-validation --mode setup` serves the app, proves the procedure, and writes the document. |
| Index row `Stack` and `docs/STACK.md` | Retired; nothing reads the file. Its content belongs in the `Architecture` document (System Overview, Integration Points), `Decisions`, and the manifest and lockfile. |
| Index row `Diagram Style Guide` | Drop the row; it retired with `excalidraw-diagram`. |
| Index rows `Architecture Model` and `Domain Model` (`.agent_temp/models/*.json`) | Replace both with one `Models` entry, default `docs/models/`, where `/andthen:describe --model` writes committed projections. `validate-model` is retired; the model reference is the contract. The old transient files are stale and unread. |


## Installation cleanup (loose installs only)

Skip this with a plugin install. A 0.x loose install could use custom destinations and a custom `--prefix`; resolve both before touching anything. With the default prefix, the eleven retired skill directories are:

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

The 12 retired generated agents were installed as `<prefix><basename>.toml` in the old Codex agents directory and `<prefix><basename>.md` in the old Claude agents directory:

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

List the exact matches and confirm each is an AndThen file before removing it.


Everything else that changed is in [CHANGELOG.md](CHANGELOG.md).
