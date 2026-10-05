# Migrating from AndThen 0.x to 1.0

1.0 removes retired 0.x skills and flags outright – there are no compatibility aliases. Re-plan unfinished 0.x work from its requirements into a current Feature Implementation Specification (FIS, the per-story spec an agent executes).

This guide has four upgrade steps, an optional prompt that has your agent carry them out, and tables mapping every retired name to its 1.0 replacement. Once you are on 1.0 you will not need it again.


## What changes for you

- **The `andthen:clarify` skill writes the PRD.** The `prd` skill is gone. `clarify --brief` stops at an `intent.md` you can edit and share first.
- **Every FIS belongs to a plan.** A plan bundle is a feature directory holding a schema v2 `plan.json` and one FIS per story. The `andthen:plan` skill writes a one-story plan beside a standalone FIS, so there is one state format and no sidecar.
- **State lives in `plan.json`.** The `State` and `State (local)` documents are retired; the `andthen:handoff` skill carries continuity between sessions.
- **The `ops` skill is gone.** No script writes `plan.json`. The session executing a story edits that story's row directly and commits it with its work; a `plan` breakdown's session alone writes the plan it authors.
- **Review runs twice.** The `andthen:exec-plan` skill reviews each story with one fresh reviewer subagent per run. The plan-level `review --fix <plan.json>` is a separate step in a fresh session, which the `andthen:exec-plan` skill hands over on its `Next (fresh session):` line.
- **The plan bundle lives only on its branch.** The `andthen:ship` skill closes it out before the merge: it lands each FIS's `## Implementation Observations` worth keeping as Learnings bullets, recommends Decisions and upstream edits, deletes tracked `plan.json` and FIS files, commits, and after one confirmation pushes and opens the PR. Untracked bundle files stay in place; `prd.md` stays.
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

- blockers to the governing FIS or a handoff;
- durable decisions to Decisions or ADRs;
- durable traps to Learnings;
- current focus and continuity to a handoff.

Then remove the two Index entries and only the AndThen files they point at. A same-named state file elsewhere is unrelated; leave it. From now on `plan.json` answers what is active: the `andthen:plan` skill writes it – a one-story plan for a small feature, a plan of several stories from a PRD.

**3. Refresh the project setup.** Always. Re-run `/andthen:init`: it adds missing Index entries and `Key Dev Commands` without asking, and offers the rest, the optional role agents included, in its closing summary. It leaves an existing Index header alone apart from appending the first-write sentences an older preamble lacks, and leaves a populated Product document alone. A Product document without a `## Proportionality` section gets one from the first `clarify`, `decide`, `plan`, or `architecture` run with someone to answer: it asks the project's stage, scale, and standing technical non-goals in one question. One edit is yours:

- **Repoint retired names** in your own `CLAUDE.md` / `AGENTS.md`, docs, scripts, aliases, and CI config, using the tables below. This search finds the retired skills in both naming schemes; retired flags are in the tables:

  ```
  rg -n 'andthen[:-](prd|quick-implement|quick-review|remediate-findings|preflight|refactor|map-codebase|ubiquitous-language|issue-triage|e2e-test|explain-changes|excalidraw-diagram|merge-resolve|ops|spec|exec-spec|backlog-triage|skill-review)\b'
  ```

**4. Re-spec unexecuted plans and specs.** When a plan or FIS is not fully executed yet. The `andthen:exec-plan` skill admits a story by resolving its FIS `Plan` and `Story-ID`, then checking that the plan holds that story and its `fis` points back to the file; it does not reject a plan solely for an older `schemaVersion`. A standalone 0.x FIS without that provenance cannot pass admission. Nothing converts old bundles in place, so move the old bundle out of the way and write a new one from its source. `plan` never reads an old plan or FIS as state. Finished plans and FIS files need nothing – keep them as history or delete them.

- **A 0.x plan** (schema v1 `plan.json` or markdown `plan.md`, with its FIS files): `git mv` the old plan and its FIS files into a `0.x/` folder beside the PRD, since the new files take their paths. If some stories are already implemented, mark them out of scope in the PRD. Then run `/andthen:plan <feature-dir>`. It works from the PRD alone, so a decision an old FIS settled comes back as a question; answer it from `0.x/`. Delete `0.x/` once the new bundle is in place.
- **A standalone 0.x FIS** (no `**Plan**:` line under its title): move it into a `0.x/` folder, then run `/andthen:plan` on its requirements source – or, with the source gone, on the moved FIS as a requirements file, so what it settled carries over. Delete the old file once the new FIS and its one-story plan are in place.
- **An unfinished `plan.json` from a 1.0 release candidate** needs no re-spec: run `/andthen:exec-plan` on its directory as it stands, since an older status such as `spec-ready` reads as `pending`.


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
| `remediate-findings` | `/andthen:implement-fix <report>` – same six phases, Fix bar, and `## Remediation Status` annotation. |
| `quick-implement`, its `--tdd` flag, and its commit/PR creation | `/andthen:implement-fix "<request>"`, which treats your sentence as its whole Fix set. For strict TDD, use `/andthen:testing --mode tdd`. The verified change is left in the working tree; `/andthen:ship` commits it and opens the PR, with one confirmation before the push. |
| `quick-review` | `/andthen:review`. A story's own review runs the quick pass inside `/andthen:exec-plan`, applying Fix-routed findings inline as `quick-review --fix` did. The `commit <sha>` shorthand has no replacement: pin the commit with your Git tooling, then give the review its diff and changed files as explicit scope. |
| `preflight`, Persisted Decision Blocks, `Preflight:` | Now the Preflight step that closes `/andthen:plan`, ending on the next command. There is no verdict line and no held story: in an unattended run, or when a question goes unanswered, the recommendation becomes an `ASSUMPTION:` in the FIS. |
| `refactor` | `/andthen:simplify-code` |
| `map-codebase` | `/andthen:describe --mode codebase` |
| `ubiquitous-language` | `/andthen:describe --mode domain` |
| `issue-triage` | `/andthen:tracker triage` |
| `backlog-triage` (a 1.0 release-candidate name) | `/andthen:tracker triage` |
| `skill-review` (a 1.0 release-candidate name) | Left the plugin; it is a project-level skill for contributors to the AndThen repository. |
| `spec`, `plan <source>` | `/andthen:plan <source>`. It decides the story count itself and writes `plan.json` plus one FIS per story when the work needs several ([ADR-020](docs/adrs/ADR-020-one-authoring-and-one-execution-skill.md)). |
| `exec-spec`, `exec-plan [--worktree] <dir>` | `/andthen:exec-plan [--worktree] <dir>`. A plan directory runs every ready story, one fresh subagent each; a FIS path runs one story. |
| `review --council` | Retired. The Findings Filter built into `review` pressure-tests every collected finding in its place. |
| Deep security orchestration in `review` | `/andthen:review --mode security`, with exposure calibration. The OWASP checklists and threat-modelling orchestration are retired. |
| `architecture` modes `advise`, `review`, `decompose`, `fitness`, `strategic-design`, `event-storming`, and deep-mode chains | Unchanged: `/andthen:architecture` with the matching `--mode`, chains included. Without `--mode`, it infers the mode from your request and asks when the request names none. |
| `architecture --mode trade-off` | `/andthen:decide <decision>`. It interviews you over the decisions a solution needs, deepens a contested one into the weighted trade-off analysis, and writes the ADRs or Decisions lines. `--auto` stays. |
| `e2e-test` | Retired. Drive the browser directly; the `visual-validation` skill captures and judges screens. |
| `spike`, `simplify-code` | Unchanged: `/andthen:spike`, `/andthen:simplify-code`. |
| `visualize` | `/andthen:visualize <artifact>`, rebuilt small: it writes one self-contained HTML page with inline SVG figures and checks it by rendering it. The modes, templates, and notes loop are gone ([ADR-027](docs/adrs/ADR-027-visualize-skill.md)). |
| `explain-changes` | Removed with no replacement; AndThen owns the artifact contracts, not rendered views. |
| `excalidraw-diagram` | Removed with no replacement; diagramming is outside AndThen's scope. |
| Internal `merge-resolve` | Removed with team/worktree orchestration. Resolve branch conflicts through your normal workflow. |


## Retired flags, forms, and `ops` commands

The `ops` skill and its script are gone. The session running a plan edits `plan.json` itself, per `plan.schema.json`; markdown documents were always agent-edited.

| 0.x form | In 1.0 |
|---|---|
| `quick-implement --issue <number>` | Fetch and review the issue through your tracker, then pass the approved small-fix requirements inline to `/andthen:implement-fix`; `/andthen:ship` commits and pushes it, with one confirmation before the push. For larger work, pass the issue URL to `/andthen:plan`. |
| `--issue <number>` | Pass the full issue URL positionally to `/andthen:clarify`, `/andthen:plan`, or `/andthen:triage`. |
| `--from-issue` | No reverse-sync mode. Pass the issue URL to `/andthen:plan`, then run `/andthen:exec-plan` on the plan directory. |
| `--create-story-issues`, or publishing a local plan as tracker work | `/andthen:tracker publish <plan.json>` creates the parent and child issues and updates them on a re-run. |
| `--to-issue` | No general publisher. For a plan bundle, use tracker `publish`. Publish a PRD, report, or triage artifact yourself through your tracker or host CLI after reviewing it. |
| `--to-pr` | No report or comment publisher. A PR is a review target – `/andthen:review "PR <number>"`; post output through the host yourself if wanted. |
| `review --from-pr <number>`, `review --worktree` | `/andthen:review "PR <number>"` reviews the PR in a scratch worktree, so neither flag is needed. |
| `--team`, `--max-parallel` | Removed with Agent Teams orchestration and `merge-resolve`. `exec-plan --worktree` on a plan directory remains: one worktree per story of a batch of the wave (about five), merged back with `git merge --no-ff` rather than squashed. |
| Installer `--codex-agents-dir`, `--no-codex-agents`, `--claude-agents-dir` | Removed: the 1.0 loose installer installs no agents. `/andthen:init` offers the four optional role agents (`oracle`, `implementer`, `reviewer`, `worker`) instead. |
| `scripts/generate-codex-agents.sh` | Removed; role agents come from `/andthen:init` templates. |
| `review --inline-findings` | `/andthen:review --quick <target>` returns structured findings in the conversation. |
| `review --fanout`, `review --no-fanout` | Fan-out follows the scope's shape. Ask to partition, or ask to keep the review in one pass. |
| `review --intent <FIS>` (a 1.0 release-candidate flag) | Name the FIS in the request; a FIS the request names governs the review. |
| `review --mode mixed` | Omit the mode, or name a comma-separated chain such as `--mode code,gap`. |
| `review --mode doc` | Retired. `/andthen:clarify` and `/andthen:plan` each self-review what they write in a fresh context; `--mode gap` or `--mode outcome` reviews a requirements document again as the baseline; documentation shipped as a deliverable falls under `--mode code`. |
| `architecture --count <N>` | Say how many alternatives you want in the `/andthen:decide` request. |
| `ui-ux-design --mode research`, `design-system`, or `wireframes`, including chains | Say what you want and in which order; the mode is inferred. |
| `ui-ux-design --mode review` | `/andthen:visual-validation` |
| `testing --mode write` | `/andthen:testing <target>`; writing tests is the default. |
| `testing --mode strategy` | Same flag, new job: it writes the `Testing Strategy` document (`docs/TESTING-STRATEGY.md`). For 0.x's read-only coverage and risk assessment, ask `/andthen:testing` for it on a scope; no mode does it. |
| `clarify --mode product`, `clarify --mode feature` | Say whether the request is about the whole product or one feature. |
| `quick-implement --pr`, `quick-implement --no-pr` | Gone. `/andthen:implement-fix` never commits or pushes; `/andthen:ship` does it, with one confirmation before the push. |
| `now-what --no-handoff` | Ask `/andthen:now-what` for a recommendation only, without running the next skill. |
| `handoff --no-mutate` | Ask `/andthen:handoff` for the document only. Its durable writes are idempotent, so there is nothing to opt out of. |
| `issue-triage --limit <N>` | `/andthen:tracker triage`, with the item cap stated in the request. |
| `map-codebase --model-only` | `/andthen:describe --mode codebase --model-only` |
| `triage --investigate` | `/andthen:triage --plan-only` |
| `triage --headless` | `/andthen:triage --auto`. `--auto` is unchanged on every skill that had it: the run asks nothing, records each open decision as an `ASSUMPTION:`, and stops only on an unusable call. |
| `ubiquitous-language --update` | `/andthen:describe --mode domain`; it merges into the existing glossary by default. |
| `ubiquitous-language --model` | `/andthen:describe --mode domain --model-only`; `--model` now extracts the glossary first. |
| `simplify-code --path <path>` | Pass the path as positional scope to `/andthen:simplify-code`. |
| `--visual` | Removed. Skills print the artifact path, and you read the markdown. |
| `--skip-review` | Remove it. 1.0's authoring and execution review gates have no bypass. |
| `--defer-shared-writes` | Remove it; an internal team/worktree contract with no replacement. |
| `GOVERNING PLAN PATH:` caller line | Remove it. A plan-backed FIS names its plan in its `**Plan**:` header, which every consumer reads. |
| `Story-Gate: PASS \| FAIL` lines and `.agent_temp/story-gate-*.md` reports | Removed with the story gate. The per-story review reports on the completion report's `Reviewed:` line; open findings go to `/andthen:review`, then `/andthen:implement-fix`. Nothing reads the old report files. |
| Legacy plan `--skip-specs`, `--stories`, `--phase` | Remove them. A 1.0 plan is a complete `plan.json` + FIS bundle, executed as a whole; narrow the PRD or generate a smaller plan instead. |
| `ops complete-task`, `ops complete-story`, `ops update-plan*`, `ops validate-plan`, `ops progress`, `ops merge-story`, `ops commit` | The session executing a story with `/andthen:exec-plan` edits its row per `plan.schema.json` (`done` only together with the `verified` line quoting executed proof output) and commits with `git add -- <paths>` then `git commit -- <paths>`; a plan run under `--worktree` merges each story branch with `git merge --no-ff`. |
| `ops update-state`, `ops read-state` | Read `plan.json`; `/andthen:handoff` carries session continuity. Retire the old State documents as in step 2. |
| `ops update-ledger` and the reconciliation ledger | Append the drift note to the FIS's `## Implementation Observations` yourself; there is no separate ledger. |
| `ops update-fis ...` in every form, `ops update-decisions` | Append to the FIS's `## Implementation Observations` or `## Discovered Requirements` yourself. Preflight settles FIS-local questions. For a durable project choice, use `/andthen:decide` for an ADR or edit the Decisions document. |
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
| 0.x FIS shape (free-prose `Proof` / `Verify`, unbound scenarios or Structural Criteria) | Never converted in place. An unexecuted one is re-specced from its source (step 4); a finished one needs nothing. |
| Source Trust enum/header and `UNTRUSTED REQUIREMENTS DATA:` artifact line | Artifacts keep a durable `> **Source**: <path-or-url>` pointer; fetched content is still treated as evidence, not instructions, when read. |
| User-level `# Critical Rules and Guardrails` copy carrying a `## Working Style` section | A pre-0.40 copy. Its conversation rules now ship as the `concise-critical` output style, so with the style enabled they load twice. Replace the block, from that heading to the next top-level heading, with the current guideline body, or remove it once the project adopts the rules through `/andthen:init`. |
| `learnings/` topic shards | Keep them. A shard is a topic file the Learnings index points at in one line, with no ceiling, graduation, or prune verb: shard when appending would make the index long, and what to drop is your call. |
| `hooks/scripts/reinject-context.sh` | Removed. Delete its `SessionStart` (`compact`) entry from your settings: Claude Code re-reads the project-root `CLAUDE.md` after compaction on its own. |
| `scripts/validate-plan-json.sh` | No script. The skill that writes a plan checks it against `plan.schema.json`. |
| `docs/OUT-OF-SCOPE.md` (Out of Scope Registry) and its Index row | Retired. Move each `## <Concept>` section by hand into the Product document's Non-Goals as one dated bullet (decision, date, prior requests on one line), then drop the Index row. Left in place, it is inert. |
| `[TI<NN>]` scenario tags | Retired; `SATISFIES` alone links a task to what it proves. A spec still carrying the tag parses unchanged (it reads as title text), so the tag alone forces no re-spec. |
| The Project Document Index as a three-column table | Still works; nothing parses it. A 1.0 entry is a `###` heading with name and location, over `Description`, `Read`, and `Write` bullets, the triggers that tell a skill when to open or write the document; the older two-line shape keeps working too. `/andthen:init` does not rewrite an existing Index; copy the entry shape from its template to get the triggers. |
| Index rows `Product Backlog` and `Changelog` | Dropped from the `init` template; existing rows are inert. No skill reads a backlog: a deferral stays in its PRD's Out of Scope, a put-off fix goes to Tech Debt, and a completed story adds the changelog entry when the project keeps one. |
| Root instruction file `### Visual Validation Workflow` section | Move its content to the `Visual Validation` Index document (`docs/VISUAL-VALIDATION.md`) and delete the section, which no skill reads: an instruction file loads on every turn, and only a validator needs the capture procedure. `/andthen:visual-validation --mode setup` serves the app, proves the procedure, and writes the document. |
| Index row `Stack` and `docs/STACK.md` | Retired; nothing reads the file. Its content belongs in the `Architecture` document (System Overview, Integration Points), `Decisions`, and the manifest and lockfile. |
| Index row `Diagram Style Guide` | Drop the row; it retired with `excalidraw-diagram`. |
| Index rows `Architecture Model` and `Domain Model` (`.agent_temp/models/*.json`) | Replace both with one `Models` entry, default `docs/models/`, where `/andthen:describe --model` writes committed projections. `validate-model` is retired; the model reference is the contract. The old transient files are stale and unread. |


## Installation cleanup (loose installs only)

Skip this with a plugin install. A 0.x loose install could use custom destinations and a custom `--prefix`; resolve both before touching anything. With the default prefix, the sixteen retired skill directories are:

```
andthen-e2e-test/
andthen-excalidraw-diagram/
andthen-exec-spec/
andthen-explain-changes/
andthen-issue-triage/
andthen-map-codebase/
andthen-merge-resolve/
andthen-ops/
andthen-prd/
andthen-preflight/
andthen-quick-implement/
andthen-quick-review/
andthen-refactor/
andthen-remediate-findings/
andthen-spec/
andthen-ubiquitous-language/
```

A loose install of rc.2 or rc.3 also left `andthen-backlog-triage/` and `andthen-skill-review/`.

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
