# AndThen Plugin

Lightweight agentic software engineering for AI coding agents, spec-driven when the work needs a spec. This is the reference for the 21 skills: what to type, what comes back, and what might surprise you. For recipes, see [`COOKBOOK.md`](../COOKBOOK.md). For the workflow overview, see the [main README](../README.md).

## Installation

Install steps for Claude Code, Codex CLI, GitHub Copilot CLI, and other agents live in the [main README](../README.md#installation). With the repo cloned, `python3 scripts/andthen.py install` from its root installs it on every host whose CLI is on `PATH`.

## Setup

Skills read your project's root agent instruction file (`CLAUDE.md` for Claude Code, `AGENTS.md` for Codex, Copilot, and generic agents) for two things:

- **Project Document Index**: a list that maps each document the project has (specs, plans, decisions, testing strategy) to its location and says when to read it, so skills know where to read and write. Documents are read whole, so keep them short; an entry's trigger may name the part to read only for history or reference that no task is checked against, such as a changelog.
- **Project-Specific Guidelines and Rules**: your own conventions and workflow notes.

Skills name documents and folders by their Index entry (Specs & Plans, Agent Temp, Research, Models, Tech Debt, Learnings). The Index lists only documents that exist: the skill that first writes one creates it at its default path and adds its entry. The `fast` and `full` check tiers are rows of the `Key Dev Commands` document.

When you use both tools, `AGENTS.md` holds the content and `CLAUDE.md` is a thin `@AGENTS.md` import. The `init` skill writes both from the [starter template](skills/init/templates/CLAUDE.template.md).

### How AndThen describes a project

Markdown documents are the sources of truth. Typed models (JSON) are committed projections of them, regenerated at deliberate points. A projection that disagrees with its source is stale.

| Aspect | Source of truth | Committed projection |
|---|---|---|
| Product intent | `PRODUCT.md`, including its Proportionality facts | none |
| Domain structure | `DOMAIN-MAP.md`: subdomains, bounded contexts, integration patterns, no terms | none |
| Domain language | `UBIQUITOUS_LANGUAGE.md` (glossary only) | none |
| System structure | the code (`ARCHITECTURE.md` is prose orientation) | `architecture-model.json` via `describe --model` |

Projections live under the `Models` Index location (default `docs/models/`) and record the commit they describe in `meta.revision`, suffixed `-dirty` when the working tree differs.

### Foundational Rules and Conversation Style

**Project rules.** At the end of a run, `init` offers the [critical-rules starter](skills/init/templates/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md) for your root instruction file. The rules then travel with the checkout into CI and containers. Your team owns them: init preserves your customizations and never overwrites them.

- Declining writes `<!-- AndThen critical rules: skipped -->` to the instruction file, and later runs respect it. Ignoring the offer writes nothing, so the next run offers again.
- To adopt later, ask init to remove the marker and add the rules. Without init, ask your agent to adopt the starter in your root instruction file, preserving existing policy.

**Conversation style.** [`concise-critical.md`](skills/init/templates/output-styles/concise-critical.md) asks for brief, plain answers, a critical stance, and the answer first with any ask last. It belongs in the system prompt, where it survives compaction, so init configures it only when you ask. To set it yourself:

- Claude Code: set `"outputStyle": "andthen:concise-critical"` in `~/.claude/settings.json` and start a new session. If your version does not list that name, copy the file to `~/.claude/output-styles/` and use `"outputStyle": "concise-critical"`. A project-level `outputStyle` overrides the user-level one.
- Codex: put the style body (everything below the frontmatter) in `~/.codex/config.toml`:
  ```toml
  model_verbosity = "low"        # optional; use "medium" if deliverables lose needed detail
  personality = "pragmatic"      # optional tone preset
  developer_instructions = """
  <body of skills/init/templates/output-styles/concise-critical.md>
  """
  ```
  Do not use `model_instructions_file` for this: it replaces Codex's base instructions.
- Copilot CLI has no style setting. The closest place is `~/.copilot/copilot-instructions.md`, which every session loads: put the style body there between `<!-- andthen-style -->` and `<!-- /andthen-style -->`, the block init writes and replaces.

## Workflows

Every skill works standalone. The cookbook covers [how the workflow fits together](../COOKBOOK.md#how-the-workflow-fits-together) and runnable sequences such as [one story or several](../COOKBOOK.md#one-story-or-several), [a small change](../COOKBOOK.md#a-small-change), and [unattended execution](../COOKBOOK.md#unattended-execution).

**Questions.** `clarify`, `decide`, `plan`, `exec-plan`, `architecture`, `domain`, `tracker triage`, and `ship` stop and wait for your answer, each question with a recommended answer. They never replace a question with a silent assumption unless you pass `--auto`. Ask `clarify` or `decide` for the complete set of questions to pass on, to a colleague or as a reply on an issue, and you get them in one list, each follow-up naming the earlier answer it assumes. Paste the answers back, or point the run at the issue, to continue ([recipe](../COOKBOOK.md#questions-for-someone-else-to-answer)).

**Unattended runs (`--auto`).** The flag makes a run ask nothing. It records each open decision as `ASSUMPTION: <what> – <what would change it>`, skips any action that needs your consent, and stops with `BLOCKED: <what is needed>` when the call is unusable. Only the flag does this, never how the run was launched, and the run passes it on to every skill it invokes. `clarify` has no unattended form, because the interview is the skill.

**Fresh sessions.** `plan` on several stories and `exec-plan` work best in a clean session. Each step of the pipeline – `clarify`, `decide`, `ui-ux-design`, `plan`, `exec-plan`, `review` – ends on one `Next (fresh session):` command, never a menu, and skips a step with nothing to do. Every skill recommendation includes the full invocation in your host's syntax, with its target or request and required arguments, ready to paste. `handoff` compacts a session that has to end mid-work.

**Proportionality.** `clarify`, `decide`, `plan`, `architecture`, and `domain` size proposals against the stage, scale, and technical non-goals in your `PRODUCT.md`. If they are missing, the first of these skills you run asks once and records the answers (`unknown` for anything left open). Every set of alternatives includes a do-nothing or extend-what-exists option.

**Tracker input.** `clarify` and `plan` accept an issue URL as a requirements source, `triage` as scope, and `review` a PR. Only `tracker` writes to the tracker. Fetching uses the optional `Issue Tracker` document (`docs/ISSUE-TRACKER.md`), or `gh` for GitHub URLs. A URL on another host offers `tracker setup` first.

## Skills

Invoke a skill with `/andthen:<skill>`, for example `/andthen:plan`. Not sure where to start? Run `/andthen:now-what`: it inspects your project and routes you to the right skill.

You rarely need flags. Describe what you want and the skill picks its mode or lens, asking only when intent is ambiguous. Each section below opens with the skill's exact `argument-hint`; `--auto` is listed under a skill only where it does more than [run unattended](#workflows).

### Inventory

| Skill | Purpose |
|---|---|
| [`init`](#init) | Set up the Project Document Index |
| [`now-what`](#now-what) | Route to the right skill |
| [`clarify`](#clarify) | Interview you, write the PRD |
| [`decide`](#decide) | Make technical decisions, write ADRs |
| [`plan`](#plan) | Write the FIS for one story or several |
| [`exec-plan`](#exec-plan) | Implement a FIS or run a plan |
| [`review`](#review) | Review code, spec conformance, security, outcome, PRs |
| [`implement-fix`](#implement-fix) | Small change or review fixes, no FIS |
| [`ship`](#ship) | Close out the branch and open the PR |
| [`triage`](#triage) | Diagnose and fix failures |
| [`testing`](#testing) | Test strategy, authoring, prove-it |
| [`handoff`](#handoff) | Write a resume document for a fresh session |
| [`architecture`](#architecture) | Design advice and structural analysis |
| [`domain`](#domain) | Domain Map, glossary, event storming |
| [`describe`](#describe) | Map an existing codebase |
| [`ui-ux-design`](#ui-ux-design) | UX research, design systems, wireframes, clickable mockups |
| [`visual-validation`](#visual-validation) | Check built UI against designs |
| [`visualize`](#visualize) | Draw an artifact as a checked HTML page |
| [`tracker`](#tracker) | Publish plans, triage incoming issues |
| [`spike`](#spike) | Answer one design question with throwaway code |
| [`simplify-code`](#simplify-code) | Behavior-preserving cleanup |

## Skill Reference

### `init`

`[project name | seed <Index entry>]`

Sets up the workflow structure for new projects, partial setups, and existing codebases. It asks nothing in an existing repository. In an empty one it asks a single question: what the project is.

- **You get**: the root instruction file(s) with the Project Document Index, listing the documents the project already has, `Key Dev Commands` when the project has a manifest (the `fast` and `full` check tiers plus a run-one-test row), and `.gitignore` entries for `.agent_temp/` and review reports. A partial setup gets only what is missing.
- **Options**: `seed <Index entry>` creates one missing document from its template and adds its Index entry. Skills use it internally.
- **Good to know**: every other document (`Product`, `Architecture`, `Testing Strategy`, `Decisions`, `Learnings`) is created, and its entry added, later by the first skill that writes to it. The closing summary offers the rest, one line each: role agents, critical rules, documents to create now (`Product`, `Decisions`, `Learnings`, `Tech Debt`, `Roadmap`, `Ubiquitous Language`), `describe` for existing code without a filled-in `Architecture` document, `testing --mode strategy`, and `visual-validation --mode setup`. An offer you ignore writes nothing. Reports are gitignored by default; delete that `.gitignore` line to commit them.

```bash
/andthen:init
/andthen:init "payments-service"
```

### `now-what`

`[brief description of what you want to do]`

Inspects project state and hands off to the skill that fits. Settled requirements go to `plan`, whatever their size. Open requirements go to `clarify`. A finished plan without a plan-level review goes to `review`; a failing load-bearing check goes to `triage`. Shipping readiness follows the canonical plan contract. Finished work counts as a record, not work in progress: a plan bundle whose `plan.json` carries `shipped`, or whose `prd.md` carries the `Shipped` line `ship` adds when it deletes the plan, and a review report whose `plan.json` is gone. Wireframes, mockups, and a design system count as work in progress only until they are implemented and visually validated, or merged into the default branch.

- **Good to know**: it invokes the skill it recommends. Ask for a recommendation only, or decline, and it prints the route and stops. It has no unattended form. New work on the remote's default branch starts on a feature branch, set up the way your instruction file, guidelines, or contributing doc say, else named `<type>/<slug>`.

```bash
/andthen:now-what
/andthen:now-what "I have an export feature in mind"
```

### `clarify`

`[--brief] <description | file path | tracker item URL | other URL | specs directory>`

The requirements skill. It interviews you in rounds about gaps, edge cases, scope, and alternatives you had not considered, then writes the document. Scope is inferred and stated first: **feature scope** writes `prd.md` under the Specs & Plans location, **product scope** writes `PRODUCT.md`.

- **You get**: a self-contained PRD with a problem definition and success metrics. Settled domain terms go to the `Ubiquitous Language` document when one exists, and concepts you explicitly reject to the `Product` document's Non-Goals, where a Non-Goal this PRD overturns is narrowed or removed.
- **Options**: `--brief` stops at `intent.md` (problem, outcome, affected systems, constraints, open questions, plus a decisions log). Edit or share it, then run `clarify` on its directory: only what is still open is asked. Product scope ignores the flag.
- **Tracker record**: with `Record: tracker` in the `Issue Tracker` document, it asks once and then saves the PRD to its issue, creating one when the input was not an issue. `plan` on that issue takes the PRD back, so the local `prd.md` is optional to keep. `clarify` on the issue amends it.
- **Good to know**: every run asks at least one round and waits for real answers, even when your input looks complete. You confirm the settled picture before anything is written; when the scope adds screens no wireframes or mockups cover, that question also asks whether design comes first. It closes on one next step: `decide` if a design fork binds beyond the work, then `ui-ux-design` if you chose design first, otherwise `plan`. An amendment to a plan already under way closes on a `plan` revision of the first pending story it changes, and is appended to each other changed pending FIS as a discovered requirement. When it changes done work or adds or drops a story, it moves the old `plan.json` and FIS files into `superseded/` beside the PRD and closes on `plan` for the whole PRD, with new stories numbered after the highest old ID; `ship` later lands that folder's Observations and deletes it.

```bash
/andthen:clarify "users should be able to export their data"
/andthen:clarify https://github.com/org/repo/issues/42
/andthen:clarify --brief "users should be able to export their data"   # stop at intent.md; later: /andthen:clarify docs/specs/<feature>/
```

### `decide`

`[--output-dir <path>] [--auto] <decision | technical area | PRD, plan, or report path>`

Makes the technical decisions a solution needs and records them. It sits between `clarify` (what to build) and `plan` (one story's how). It lists the decision points and sorts each: a choice that binds beyond one story or is costly to reverse is decided here, a story-local one is left to `plan`, a user-visible requirement goes back to the PRD via `clarify`, and anything the code or an earlier decision settles is cited, not asked.

- **You get**: one ADR per decision with real alternatives, registered in `DECISIONS.md` (superseded rows move, never disappear), or a one-line Still Current entry for a load-bearing choice with no alternative. You pick `Accepted` or `Proposed` when you confirm the closing summary. Parked decisions go under Pending. Run on a PRD, each Open Question or Decisions Log row it settled names the decision that closes it.
- **Options**: `--output-dir <path>` sets where trade-off research lands (default: the Research location, else `docs/research/`). `--auto` settles the named decisions on its own recommendations and writes `Proposed` ADRs, which a later run asks you again.
- **Good to know**: each decision is labelled a one-way or two-way door (costly or cheap to reverse), and its ADR says what reversing takes. When no option stands out, or you ask for a comparison, it runs a weighted trade-off analysis with five options unless you name a count ("compare three options"). Close options on a two-way door skip it, because either pick is cheap to undo. A question only running code can answer goes to `spike`. No code changes. Run on a PRD, it closes on `plan` (or `ui-ux-design` when the PRD puts design first); run from `plan`'s Preflight, it records the answer you already gave and closes on `exec-plan`.

```bash
/andthen:decide docs/specs/export/                                         # the PRD's open technical forks
/andthen:decide "how should the export job queue work?"
/andthen:decide "compare three options for the job queue: Postgres SKIP LOCKED, Redis streams, SQS"   # weighted trade-off
/andthen:decide --auto "SQL vs document DB" --output-dir docs/research/
```

### `plan`

`[--auto] <description | @<requirements-file> | tracker-item URL | a prd.md or intent.md path, or its directory | story <id> of <plan.json>>`

Writes the Feature Implementation Specification (FIS): the blueprint a fresh session implements without asking questions. `plan` decides whether the work is one story or several. Inline text and `story <id> of <plan.json>` are one story each. A written source (a PRD, intent doc, requirements file, or tracker item) is sized: one vertical slice that fits a fresh-context run is one story, anything larger is several, unless you ask for one story ("as one story").

- **You get**: for one story, a FIS plus a one-story `plan.json` beside it. For several, `plan.json` plus one FIS per story and a cross-story review. Output lands beside a PRD, intent doc, or plan story, else under `docs/specs/<feature>/`; for a tracker item, in the `issue-<number>-*` directory `clarify` wrote when one exists, so its `prd.md` is reused. No code changes. Each story's `sourceRefs` link the PRD's `#### FRn:` sections it covers, so the PR `ship` opens can name each outcome's FR IDs.
- **Options**: `--auto` writes each open question as an `ASSUMPTION:` instead of asking.
- **Good to know**: `plan` asks about missing requirements first, then runs a self-review, then a final round of open questions, each with a recommendation, and closes by listing every open item with what settled it. A FIS too big for one run is flagged `OVERSIZE:` and you choose to split it or keep it as one. Acceptance scenarios use your domain's terms and name an API, CLI flag, file format, or UI control only where something outside the change depends on it, so a better implementation does not break them. `plan` always authors from the source: it has no revise mode, so to revise a spec or re-plan after the source changed, see [the cookbook recipe](../COOKBOOK.md#revising-a-spec-or-re-planning). It closes on the `exec-plan` command for the first story's FIS in a fresh session, or stops early on `clarify` for a source too thin to spec, or on `ui-ux-design` when you choose to design new screens first.

```bash
/andthen:plan "users can export their data"
/andthen:plan docs/specs/data-export/
/andthen:plan https://github.com/org/repo/issues/42
/andthen:plan "story S03 of docs/specs/dashboard/plan.json"
```

### `exec-plan`

`[--auto] [--worktree] [--no-full-tier] <path-to-fis | plan directory>`

Implements one FIS in the current session, or runs a plan directory, giving each ready story to a fresh subagent. Either way it runs the project's checks and every proof the FIS names, has a fresh reviewer check the change, and completes a story only on executed proof.

Run a plan one story per fresh session: `plan` prints the first story's command and each story's report prints the next, so you read every result and can adjust the next story's FIS before it runs. Run on the plan directory, it runs every story without stopping, for unattended or parallel runs, with the full check tier once at the end instead of per story.

- **You get**: committed code per story, its commit message a brief subject with `Story-ID:` and `Plan:` trailers, and the story's `plan.json` row set to `done` and a `verified` summary quoting the proof it ran. The report ends with a `Reviewed:` line (what reviewed the change, what stays open) and a `Next (fresh session):` line. Each story then gets one `simplify-code` pass over its code, as its own `refactor` commit, before the next story runs (under `--worktree`, one per batch). Open findings are recorded in the FIS under `## Implementation Observations`.
- **Options**: `--worktree` runs a plan's independent stories in parallel, each on its own branch in its own git worktree, merged back after each batch. `--no-full-tier` runs the fast check tier where the full one would run, for a caller that runs the full tier itself.
- **Good to know**:
  - On the remote's default branch it first asks whether to start a feature branch, because every story commits to the current branch. An unattended run stays where it is.
  - A direct story run asks before building on dependency stories that are not `done`. An unattended run stops.
  - A discovery that affects a story still to run is appended to that story's FIS under `## Discovered Requirements` and committed before the next story starts. The later story proves it, and it outranks any FIS text it contradicts. A contradiction, or a scope change (never written into a FIS), is asked about first: on yes, the `Next (fresh session):` line names the `plan` revision of that FIS or the `clarify` PRD amendment, and an attended plan run stops there. `--auto` decides and records its reading in the appended requirement, and so does your answer to continue without a revision. The report names each FIS it changed.
  - A gap in a FIS (a broken anchor, an unbound proof) never stops the run: it takes the best reading and records it.
  - Plan run: stories run one at a time in the shared tree. Each story runs the fast tier, then the plan run runs the full tier once on the final tree and repairs failures. A failed story's dependents are reported skipped. Other stories continue only when the failure's changes are provably isolated, which is always true under `--worktree`; otherwise the run stops.
  - `--worktree` needs a clean tracked tree and a committed bundle (a gitignored specs directory fails this). A failed story keeps its branch and worktree, and a rerun resumes there. A merge conflict fails the story, except lines both sides appended to the changelog or `Learnings`.
  - Another session's uncommitted changes are never staged, stashed, or reverted.
  - A red gate is work to finish until a `triage` repair turns nothing green. A failed story ends with a route out: `review --fix` over the story's changed paths, for correctness and against its FIS, then `exec-plan` again on the same input.
  - The plan-level review (`review --fix <plan.json>`) is printed, never run for you.
  - `plan.json` and the FIS files stay in the tree. After a clean plan-level review, a `Next (fresh session):` line for `ship` lands their observations and asks whether to delete them. `prd.md` stays under `Record: repo`; under `Record: tracker`, its issue carries the record.

```bash
/andthen:exec-plan docs/specs/data-export/s01-data-export.md
/andthen:exec-plan docs/specs/dashboard/
/andthen:exec-plan --worktree docs/specs/dashboard/   # independent stories in parallel, one worktree each
```

### `review`

`[--mode code|gap|security|outcome[,...]] [--quick] [--fix] [--output-dir <path>] [--auto] [target: paths, a PRD/plan/FIS, or a PR]`

Reviews an implementation through one or more lenses: `code` (quality and correctness), `gap` (does it match its FIS or plan), `security`, and `outcome` (does the finished feature solve its PRD's problem for its users; needs a PRD). Lenses are inferred from your wording and can be chained into one report.

- **You get**: a report with an executive summary, coverage matrix, findings, verdict, and next steps. It lands beside the reviewed spec, else under `reviews/` in the Agent Temp location, named `<feature>-andthen-<suffix>-<agent>-<YYYY-MM-DD>.md`. Each finding is routed `Fix` (mechanical, safe to auto-apply) or `Note` (surfaced for you).
- **Options**:
  - `--fix` applies Fix-routed findings through `implement-fix` after the report, one round, with no re-review, and commits the verified change (under `--quick` too, unless `exec-plan` runs it, which commits the fixes with its story). On the remote's default branch it first asks whether to start a feature branch. When that round fixed a CRITICAL or HIGH finding or left a Fix finding partly fixed, it ends on a `Next (fresh session):` line for a follow-up review. A direct request such as "review this and fix what you find" counts as the flag. Vaguer wording such as "this should be cleaned up" stays read-only.
  - `--quick` returns one pass's findings inline: no report file, coverage matrix, or verdict. `exec-plan` uses it for the per-story review.
  - `--output-dir <path>` overrides the report directory.
- **Good to know**:
  - The review pass runs in a fresh reviewer subagent unless this session neither wrote nor reasoned about the target. A chained review always uses one.
  - Very large diffs (20+ files, 1000+ changed lines, or 3+ top-level modules) are split across several passes.
  - The latest earlier report on the same target is read, and each finding it left open is marked resolved or still open. A MEDIUM or LOW one the fix round surfaced to you or deferred stays in that list rather than coming back as a finding. When that report carries `**Remediated**:`, the follow-up covers only the work since its Revision, new files included, the callers of that code, and its open findings. It reviews the whole target instead when it adds a lens that report did not run, or when the Revision is no longer in the history.
  - A full review closes on one next step: the follow-up review `--fix` owes, else `clarify` for a PRD-side gap, `decide` for an unrecorded design change, or `implement-fix` for Fix-routed findings. A clean review of a plan whose stories are all `done` or `skipped` (cut from scope), nothing CRITICAL or HIGH left open (a deferred one counts), ends on a `Next (fresh session):` line for `ship`. A plan held by a deferred CRITICAL or HIGH finding ends on `Next: blocked –` with each finding and its blocker instead.
  - The `security` lens sets severity by exposure and records unavailable scanners rather than reading them as clean.
  - A PR (`PR 42` or its URL; a bare `#42` is ambiguous) is checked out in a scratch worktree and reviewed with every lens. Checks run only when the head branch is in the repository itself. Fork PRs get a static pass unless you say "run the checks". `--fix` is rejected for PRs.
  - An optional `Review Policy` document (path exclusions, extra passes, stricter verdict thresholds) is read when the Index names it. Nothing creates it: write it from the starter below, and `/andthen:init seed Review Policy` adds its Index entry.

```bash
/andthen:review                                       # current changes, lens auto-detected
/andthen:review "does this match the spec?" <path>    # gap lens
/andthen:review "review PR 42"                        # PR in a scratch worktree, every lens
/andthen:review --mode outcome docs/specs/my-feature/plan.json   # does the built feature solve the PRD's problem?
/andthen:review --mode gap,code,security              # chain lenses into one consolidated report
```

**Review Policy starter** (write it by hand; an empty section means the defaults apply):

```markdown
# Review Policy

## Excluded Paths
<!-- Globs for generated, vendored, or migration paths. An exclusion that would empty the coverage
     set for the change under review is surfaced, not honored. -->
- [glob] – [why this project does not review it]

## Extra Passes
- [pass or checklist this project wants run beyond the standard lenses] – [when it applies]

## Verdict Thresholds
<!-- Stricter than the defaults only; gap mode's dimension table is never calibrated. -->
- [dimension] – [threshold] (default [N])
```

### `implement-fix`

`[--auto] <request | review-report path or URL | tracker item URL>`

Implements a small change, or a review report's Fix-routed findings, with the smallest safe edit and re-validation. No FIS needed. A tracker item URL works from the item's `## Agent Brief`, else its body. A request describing a plan, PRD, or FIS stops and points you to `plan`, then `exec-plan`.

- **You get**: a verified change committed by path (on the remote's default branch it first asks whether to start a feature branch), a file that also holds another session's edit left uncommitted and named, a table with each finding resolved, deferred, or surfaced, and the `Reviewed:` line. A writable report gets a `## Remediation Status` section written back.
- **Good to know**:
  - A request is its own finding list. Beyond it, only Boy Scout tidies are edited, each named in the report: behavior-preserving fixes in the functions or doc sections the change edits and minor ones elsewhere. A larger issue you did not ask for is reported as `NOTICED BUT NOT TOUCHING:`. An ambiguity is asked once.
  - From a report, an attended run edits only `Routing: Fix` findings, plus Boy Scout tidies. `Note` findings stay untouched unless you direct otherwise; under `--auto`, eligible Notes can be promoted to Fix by the disposition below.
  - It is one round: re-validate, fix, verify once, re-check each finding. What stays open is escalated with evidence.
  - Run on a report, it closes like `review --fix`: a `Next (fresh session):` follow-up review when it fixed a CRITICAL or HIGH finding or left a Fix partly fixed, else a `Next (fresh session):` line for `ship` for a plan whose stories are all `done` or `skipped` with nothing CRITICAL or HIGH left open, a deferred one included.
  - A Fix finding blocked by a named reason (an open decision, a file outside scope, a new test harness, a migration, a caller API change, a concrete risk) is deferred to the `Tech Debt` backlog. Attended, you answer once for all of them, together with each open Note and decision, and "go" takes every recommendation. Unattended, all are written.
  - Unattended, it dispositions each `Note` item itself (apply, defer, or surface with a reason).
  - It never edits `plan.json`.

```bash
/andthen:implement-fix "add a --json flag to the export command"
/andthen:implement-fix docs/specs/csv-export/csv-export-andthen-code-review-claude-2026-09-07.md
```

### `ship`

`[--auto] [plan.json path] [notes for the pull request]`

Closes out the current branch and opens its pull request (a merge request on GitLab). On a branch with a plan bundle it first lands what the FIS files learned, `superseded/` ones included, then deletes the bundle if you agree, because a plan's specs govern one branch and go stale once it merges. On any other branch it commits and opens the request.

- **You get**: the traps from each FIS's `Implementation Observations` written as `Learnings` bullets, recommendations for the rest, the branch's fixes committed with the bundle's deletion (or, if you keep it, its `shipped` marker), and a pull request that states the change's intent, outcomes, and proof: the PRD's why, each story's Intent and Expected Outcomes, its `verified.summary`, and the review's verdict.
- **In the PR body**: where a reviewer should read closely, which is the files where an error does the most harm, choices no check can judge (such as a pattern others will copy), and what the proof left unchecked (skipped checks, surfaces no review read, work committed or fixed after the review). It also says whether the change is a one-way or two-way door, what breaks if it is wrong, and how to undo it where reverting the merge would not. It ends on a fixed `## Ship summary` section, collapsed where the host renders `<details>`, that repeats those facts in tables a viewer can parse: each outcome with its story, plan, PRD `FRn` IDs, and proof, each review lens's verdict and reviewed commit, and each read-closely item with its reason.
- **Good to know**:
  - It asks before the push, showing the base branch, the commits leaving, and the PR title and body. On the remote's default branch it first asks whether to start a feature branch, unless the run is unattended. Commits run unasked, because the branch history keeps them.
  - Your PR template or documented PR process sets the body's layout. The key points come first and per-story detail collapses below them. A flow or structure change gets a Mermaid or SVG diagram where a picture reads faster. For a UI change it captures screenshots or a recording when you ask, and otherwise offers them in that one question. An image the host's CLI cannot upload is listed for you to attach. The PR carries a closing link for each issue the merge finishes, in both record modes: the parent once the plan is ready (the tracker item the plan cites, or the one `tracker publish` reports), and the child of each story `done` or `skipped`; without a plan, the tracker item the request cites. Without a publish, the children come from the parent's `## Stories` checklist, read only. A link closes only from a PR into the default branch, so for another base, such as a milestone branch, `ship` names the issues left open for you to close after the merge.
  - `--auto` stops before anything leaves the machine and prints the push and PR commands with the title and body. It takes the recommendation on the bundle (delete, for a ready plan) and on the design folders, and records an `ASSUMPTION:` line in its report.
  - It writes only `Learnings` bullets and recommends the rest: a `Decisions` line or a `decide` run for a design change no record holds, and any upstream document edit.
  - For a ready plan, the one question before the push also asks whether to delete the bundle, recommending deletion; with no remote, it asks only about that. The same question names the feature folders under the wireframes and mockups locations that the branch added or the plan cites, recommending deletion unless the plan is unfinished or the branch holds only design and specs. Kept folders are listed in the report.
  - A delete removes `plan.json`, the FIS files, any `intent.md`, and any `superseded/` folder, and `prd.md` gains a `> **Shipped**:` header line so `now-what` reads it as a record; a later `clarify` amendment removes it. `prd.md` stays unless the `Issue Tracker` document sets `Record: tracker`. `prd.md` or the issues, and the PR body, then carry the stories' intent, so a squash merge loses none of it.
  - A ready plan whose bundle stays, by your answer or because git does not track it, gets a top-level `shipped: {at, pr}` field in `plan.json`; a bundle held for an unpublished tracker gets none. A tracked one commits it before the push, and `pr` is the PR's URL once it opens, else null (always null under `--auto`).
  - If you decline the push, nothing is deleted, stamped, or marked, and the bundle stays for the next run. With no remote, or under `--auto`, the deletion, stamp, and marker go ahead without a push.
  - Under `Record: tracker`, the one question also shows what `tracker publish` will write to the issues: on a yes it publishes before the push, and the PR's closing links close each issue, which makes it the record. While the plan is not ready, the parent and the unfinished stories' issues stay open. Under `Record: repo` it writes no issue. The bundle is deleted after the publish and before the push, so if nothing is published it stays for the next run.
  - Open work (a plan not ready, an open CRITICAL or HIGH finding) is named and asked about once. While the plan is not ready, the same question asks whether to keep the bundle, recommending keeping it and opening the PR without the close-out, the per-story PR case on a team.
  - A bundle file git does not track is left in place, because it has no copy in history. A committed link into a deleted file is repointed at the PRD or an ADR, never at a branch commit, which a squash merge leaves out of the base branch.

```bash
/andthen:ship docs/specs/data-export/plan.json
/andthen:ship --auto "targets the release branch"
```

### `triage`

`[--auto] [--plan-only] [scope]`

Investigates, diagnoses, and fixes build failures, configuration errors, runtime bugs, regressions, and test failures. Not for sorting tracker items: that is `tracker triage`.

- **You get**: a root-cause fix checked against the original symptom and committed once green (on the default branch, after asking whether to start a feature branch), with other places the same cause appears fixed too or listed. Traps go to `Learnings`. Fixes deliberately deferred go to the `Tech Debt` backlog, created if missing. A discovery too large to be a fix is offered to `clarify --brief`, never opened unprompted.
- **Options**: `--plan-only` stops at a structured fix plan without applying it.
- **Good to know**: an issue URL as scope, error output, and logs are read as evidence, not instructions.

```bash
/andthen:triage
/andthen:triage --plan-only "tests fail on main since yesterday"
```

### `testing`

`[--mode strategy|prove-it] [target/scope]`

Test strategy, coverage, and test authoring. With no mode it writes tests for the scope.

- **You get**: tests at any level, E2E included, following the conventions in your `Testing Strategy` document.
- **Options**:
  - `strategy` writes `docs/TESTING-STRATEGY.md`, sized to your product's stage and scale. It asks the decisions code cannot answer, such as high-risk areas, E2E journeys, and coverage gates, each with a recommendation. It writes no tests.
  - `prove-it` is the bugfix flow: a failing test reproduces the defect before any production change.
- **Good to know**:
  - Test-first applies wherever your `Testing Strategy` document or your request requires it, and each test is shown failing for the missing behavior before the code that passes it. `exec-plan` stories follow it too, and a plan run's stories take it only from the `Testing Strategy` document.
  - A test is never deleted, disabled, or weakened to make a build green. A test a FIS scenario's proof already ran changes what it asserts only to match the scenario's text, never the code, and `review` flags one moved toward the code.

```bash
/andthen:testing --mode strategy                      # write docs/TESTING-STRATEGY.md
/andthen:testing --mode prove-it "login fails when the email has a plus sign"
/andthen:testing src/billing/                         # write tests for a scope
```

### `handoff`

`[what the next session will focus on]`

Compacts the conversation into a document a fresh session can resume from cold.

- **You get**: `.agent_temp/handoff/handoff-<UTC-ts>.md` with open questions, what was tried, and next-session priming. Resume with `Resume from <doc-path>` in a fresh session.
- **Good to know**: clearly bounded gotchas are appended to `Learnings`. Structural decisions are recommended to `decide`, never written as ADRs. Secrets are redacted, but the file sits under `.agent_temp/`, so treat it as not private.

```bash
/andthen:handoff "next: finish S03's migration"
```

### `architecture`

`[--mode <mode>[,<mode>...]: advise|review|decompose|fitness] [--output-dir <path>] [--auto] [scope/path]`

Design guidance and structural analysis. It never changes code. The mode is inferred from your request or named with `--mode`.

- **You get**: `advise` returns text only. The three analysis modes write one report to `reviews/` under the Agent Temp location (or `--output-dir`). A chain such as `--mode review,fitness` produces one combined report.
- **Options**:
  - `advise`: design guidance, grounded in CUPID, DDD, deep modules, and Locality of Behaviour.
  - `review`: dependency metrics, connascence, anti-patterns, fitness proposals.
  - `decompose`: one split-or-merge decision with scored drivers.
  - `fitness`: governance and ADR enforcement.
- **Good to know**: modeling the domain (subdomains, bounded contexts, event storming) is [`domain`](#domain). A decision to settle and record goes to `decide`.

```bash
/andthen:architecture "should I use event sourcing for the order domain?"   # advise, text only
/andthen:architecture --mode review,fitness src/                            # one combined report
```

### `domain`

`[--mode <mode>[,<mode>...]: subdomains|contexts|glossary|event-storming] [--output-dir <path>] [--auto] [scope/path]`

Models the domain with you as the domain expert. It never changes code. The mode is inferred from your request or named with `--mode`, and a comma-separated chain runs in order.

- **You get**: each mode writes one record. `subdomains` and `contexts` write the `Domain Map` (default `docs/DOMAIN-MAP.md`), `glossary` the `Ubiquitous Language`, and `event-storming` a board under `docs/models/event-storms/`. A `contexts` or `event-storming` run also writes a report to `reviews/` under the Agent Temp location (or `--output-dir`).
- **Options**:
  - `subdomains`: classifies the business's parts as core, supporting, or generic, with a rationale each. The Domain Map's Subdomains, Relationships, Worked Example, and Open Questions hold it, and you confirm the classification before it is written.
  - `contexts`: bounded contexts, the subdomains each owns, the owning team, and the integration patterns between them, current and target for existing code. You confirm the contexts, then the Bounded Contexts and Integration Patterns sections are registered. With no classified subdomains it runs `subdomains` first.
  - `glossary`: extracts the `Ubiquitous Language`, merging into curated terms and clustering them by the Domain Map's bounded contexts when it has them.
  - `event-storming`: a discovery session at Big Picture (the default), Process Modeling, or Design Level for aggregates. A later run on the same scope continues the board. Subdomain candidates go on to `subdomains`, and Design-Level aggregate candidates, with their invariants, root, entities, and value objects, to `plan`.
- **Good to know**: the Domain Map is recommended first for a domain-heavy project and never required; a library or CRUD tool skips it. The map lists no terms, because the glossary holds each term once. Under `--auto`, `subdomains` writes nothing and prints its proposal, and `contexts` skips registration.

```bash
/andthen:domain --mode subdomains "order fulfilment"       # classify, write the Domain Map
/andthen:domain --mode contexts                            # bounded contexts and integrations
/andthen:domain --mode glossary                            # build or refresh the glossary
/andthen:domain --mode event-storming "checkout to delivery"
```

### `describe`

`[--model] [--model-only] [output directory]`

Documents what a project already is, without modifying code. A glossary request is [`domain`](#domain).

- **You get**: the repository mapped into the `Architecture` and `Key Dev Commands` documents, `requirements-discovered.md` and `decisions-discovered.md` for team review, and a `## Conventions` section in `CLAUDE.md` / `AGENTS.md`. A monorepo also gets a short instruction file per sub-project. Existing documents are merged into, never overwritten.
- **Options**:
  - `--model` also writes the typed model, `architecture-model.json`, under the `Models` location. A bounded context takes its `id` and `name` from the Domain Map's Bounded Contexts section when it has one.
  - `--model-only` writes just the model, no documentation. It is the refresh path.
- **Good to know**: `plan`, `architecture`, and `domain --mode contexts` read the architecture model.

```bash
/andthen:describe                                        # map the codebase
/andthen:describe --model-only                           # refresh the Architecture Model alone
```

### `ui-ux-design`

`[--auto] [inputs/path]`

UX research, design systems, wireframes, and clickable mockups, singly or chained. The mode is inferred from your phrasing.

- **You get**: `research` (journey maps, information architecture, competitive analysis, flows), `design-system` (tokens, component styles, style guide) in `docs/design-system`, `wireframes` (grayscale screen layouts) in `docs/wireframes/<feature>/`, or `mockups` (clickable pages styled from the design system, validated for contrast, off-token values, and dead links) in `docs/mockups/<feature>/`. The Index can name other locations.
- **Good to know**: design-system, wireframes, and mockups need requirements as text, a file, or a PRD, and ask for them when missing. Asking for screens, or giving a requirements source alone, without naming a level gets mockups when the project has a design system, else wireframes; mockups asked for without one get wireframes and a note to create the design system first. Mockups read the feature's wireframes when they exist, and open from disk with their styles copied in, so you can send the folder to a customer. Name several modes in order and they run in that order, with each mode's output feeding the next (mockups use the design system just written). It closes on one next step: `clarify` for questions research left open, else `plan` on the requirements the design was drawn from. Checking a built UI is `visual-validation`, not this skill.

```bash
/andthen:ui-ux-design "wireframe the dashboard screens"
/andthen:ui-ux-design "mockups of the dashboard" docs/specs/dashboard/prd.md
/andthen:ui-ux-design "create a design system" docs/specs/dashboard/prd.md
```

### `visual-validation`

`[--mode setup] [<screens-or-states-to-validate>] [design-reference/baseline]`

Checks built UI screenshots against mockups, wireframes, design specs, or baselines, and runs visual regression checks. A screen is judged against its own feature's mockup, layout included, else its own feature's wireframe, never another feature's; colours, type, and sizes follow the current design system. For each screen, state, and viewport it lists the differences from the reference before deciding pass or fail.

- **You get**: one finding line per region judged. A P1 Critical or P2 Major finding blocks: a caller such as `exec-plan` gates completion on it, and after the fix the affected screens are recaptured and the second verdict recorded beside the first. P3 is reported, not gated. An unreadable image is `not judged`, never passed.
- **Options**: `--mode setup` runs once per project. It serves the app, proves the capture procedure with a trial capture, and writes the `Visual Validation` document (`docs/VISUAL-VALIDATION.md`) with serve command, capture tooling, routes, states, breakpoints, and reference locations. Only what ran successfully is written down.
- **Good to know**: without the document, each run works out capture itself and says so.

```bash
/andthen:visual-validation --mode setup                  # write docs/VISUAL-VALIDATION.md
/andthen:visual-validation "checkout screen, mobile and desktop" docs/mockups/checkout/
```

### `visualize`

`<artifact path or name> [what the page should bring out]`

Draws one AndThen artifact as a self-contained HTML page with inline SVG figures. It is the public way to see what `architecture-model.json`, `event-storms/<slug>.json`, and `plan.json` hold: evidence levels, runtime shape, tours, story dependencies and status. Any other artifact works too, such as the Domain Map, the glossary, a FIS, a PRD, a review report, or an ADR.

- **You get**: the page at `.agent_temp/visualize/<artifact>.html`. It is a derived copy, so it is not committed by default and goes stale when its source changes.
- **Good to know**: before handing the page over it renders it in a browser, a headless one where available, and fixes overlaps, clipped labels, unreadable arrows, dead controls, and console errors. With no browser reachable it says the page is unchecked. The check is the model judging its own render. Checking your project's own UI is `visual-validation`.

```bash
/andthen:visualize docs/models/architecture-model.json "walk the tours"
/andthen:visualize docs/specs/export/plan.json
```

### `tracker`

`[--auto] (publish <plan.json | prd.md> [--dry-run] | triage [issue number(s) or tracker query] | setup)`

One skill for the issue tracker, with three verbs. `publish` and `triage` first read the `Issue Tracker` document; an absent document takes the built-in `gh` default where the repository has a GitHub remote, and offers `setup` where it has none. `Backend: none` means no tracker, and `publish` and `triage` end on one line saying so. GitHub via `gh` is the supported path, and other backends fill in the document's operation table, whose placeholders are `<N>` (the issue's id or key), `<title>`, `<body-file>`, `<query>`, and `<label>`. The document's `Record:` line says where a feature's requirements record lives after the merge: `repo` (the default) keeps `prd.md`, and `tracker` keeps the PRD and story issues instead.

- **`publish`** writes the PRD and a story checklist into the parent issue, which is the PRD's own issue when there is one, keeping its original text above the projected part. Each story gets a child issue (title `<plan directory name> S03 - <name>`, since story ids restart in every plan) with its scope, intent, expected outcomes, and acceptance scenarios, its dependencies, and once done its verification summary. No issue names a file or a commit, because both are gone after the merge. A `prd.md` alone publishes into its issue only. Re-running updates the same issues, found through the parent's checklist, or for a story the checklist does not link yet, by an exact-phrase body search across all states for its hidden line. A found issue keeps its title. A re-run never unchecks a finished story, edits its child from a copy of `plan.json` that has not finished it, or drops a checklist entry, because team branches carry diverging copies: a story removed from the plan keeps its entry, and publish names its open child for you to close. Before writing, it shows what each issue gains or loses and asks once, so an edit made in the tracker is seen before it is replaced; unattended, it writes and reports what it replaced. A closed issue is a shipped record and is never edited, so a later plan gets a new parent issue. Flow is one way, plan to tracker, with no reverse sync. `--dry-run` shows the preview and writes nothing. Issues published by an earlier release candidate are not found again.
- **`triage`** labels untriaged issues (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`; `bug`, `enhancement`), routes them toward implementation or a human decision, and appends an Agent Brief a fresh executor can act on to `ready-for-agent` items, above the item's `andthen-projection` line when it has one. It skips issues carrying that line, because they belong to a published plan. A ratified `wontfix` is also recorded in the `Product` document's Non-Goals. Interactively, you ratify every write per item. Unattended, it applies only safe transitions and leaves `wontfix`, `ready-for-agent`, and duplicate closes for a human.
- **`setup`** writes the `Issue Tracker` document. It asks which backend you use, for anything but GitHub the command for each operation, and whether requirements live in the repo or the tracker. Other skills offer it when they meet an unconfigured tracker URL, and an unattended run stops on `BLOCKED:` instead.

```bash
/andthen:tracker publish docs/specs/dashboard/plan.json --dry-run
/andthen:tracker publish docs/specs/dashboard/plan.json
/andthen:tracker triage                     # untriaged items
/andthen:tracker triage 118 121 "label:bug is:open"
/andthen:tracker setup
```

### `spike`

`[the one design question | approach A vs approach B]`

Answers one named design question by building a throwaway runnable spike, then reports a **Spike Verdict**: the answer, the evidence, and what the spike did not cover.

- **You get**: a verdict in chat and the code on a `spike/<slug>` branch. The spike runs in its own worktree under `.agent_temp/spike/`, so your checkout is never touched. The worktree is removed afterwards and the branch kept as evidence.
- **Good to know**: invoked directly, it confirms the question with you before building. Spike code is never merged or reused. The verdict feeds `clarify`, `decide`, and `plan`. A question building cannot answer is redirected: open requirements to `clarify`, a choice between options to `decide`, screen design to `ui-ux-design`. Shippable code is `implement-fix` or the plan path.

```bash
/andthen:spike "does the streaming parser hold under 10k events/s?"
```

### `simplify-code`

`[--auto] [scope: paths and/or description]`

Behavior-preserving simplification: clarity, reuse, and less over-engineering, within the scope you give.

- **You get**: edits that keep behavior, checked against the baseline it records first and committed once green (on the default branch, after asking whether to start a feature branch). Cleanups that contradict the governing FIS's `What We're NOT Doing` or `Architecture Decision` are dropped and reported. Run standalone, a substantial change ends on a `Next (fresh session):` line for a `review` of the changed paths.
- **Good to know**: without a scope it falls back to the current branch diff, and an unattended run stops if that is not a cohesive set. Removing anything observable or exported needs your approval; unattended, it is deferred. `exec-plan` runs it once per `done` story, as its own `refactor` commit before the next story runs (under `--worktree`, one pass per merged batch).

```bash
/andthen:simplify-code src/billing/invoice.ts
```

## Delegation

AndThen skills hand work to subagents. Nothing is installed by default. The `init` skill can install four optional role agents (for Claude Code as `.md`, for Codex as `.toml`, for Copilot CLI as `.agent.md`) that pin a model and effort level per task type. They take effect from the next session. Re-check the installed pins when a provider's model lineup changes.

- **`oracle`**: judgment work you assign it (a design, an architecture call, a second opinion on a decision), and hard problems an agent hands over because they exceed its tier. It returns a diagnosis or recommendation. `triage` hands over once, when `oracle` is installed, before it stops after three failed fixes. A second opinion is never requested unasked. The model-initiated form is Claude Code's built-in advisor (`/advisor`): experimental, Anthropic API only, with no Codex equivalent.
- **`implementer`**: one medium or large unit of pinned work, such as executing a story or authoring a plan story's FIS.
- **`reviewer`**: any review.
- **`worker`**: small, well-specified subtasks such as lookups and scans.

Without the roles installed, every skill falls back to the same portable shape: a generic subagent on your session's model, whose prompt invokes the relevant skill or reference. Judgment work stays in your session. Execution nests: a plan run starts one subagent per story, and each of those starts its own reviewer.

## Working in a Team

See [Working in a team](../COOKBOOK.md#working-in-a-team) in the cookbook.

## Release Notes

See CHANGELOG.md at the repository root.

## License

MIT
