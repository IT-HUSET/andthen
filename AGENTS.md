# AI Coding Agent Instructions for working with AndThen

## Project Overview

AndThen is a lightweight agentic software engineering framework of skills, adoptable piece by piece, with no forced workflow or directory layout.
Its main workflow is spec-driven: a **Feature Implementation Specification (FIS)** for one story, or a plan with one FIS per story, written before the code (often from a PRD) and executed autonomously.
Skills find every document through the **Project Document Index** below, which keeps locations configurable.

One `plugin/` directory ships to Claude Code, ChatGPT/Codex, and GitHub Copilot under dual manifests, with no build step, and to other agents as loose skills via `scripts/andthen.py install --loose`.
Skills are invoked as `andthen:<name>` on every plugin host.
Shared content in `plugin/references/` travels whole with the plugin, and a loose install inlines it per skill.

### Repo Map

- `plugin/skills/<name>/SKILL.md` – a skill; `agents/openai.yaml` beside it is its Codex metadata.
- `plugin/references/` – shared reference files consumed by several skills.
- `plugin/skills/init/templates/output-styles/concise-critical.md` – the conversation-style rules, wired by `init` as a Claude Code output style (`outputStyles` in `plugin/.claude-plugin/plugin.json`) and as Codex `developer_instructions`.
  A rule subagents must also see (engineering, git and commit, artifact conventions) belongs in the CRITICAL-RULES guideline instead, because subagents do not reliably get the output style.
- `scripts/andthen.py` – the setup script: `install` sets up the plugin on each host and, on request, user-level role agents, rules, and Codex trust; `--loose` hands off to `scripts/andthen_loose.py` (portability rewrites, shared-reference inlining, the canonical-asset tables).
- `scripts/validate-plugin.py` – the content check CI and the fast tier run.
- `scripts/fixtures/renders/` – one minimal, real-shaped artifact per type its `README.md` names, read by the `tests/` suites.
- `evals/` – the live eval harness (`README.md`) and `subject/`, the app every case starts from, carrying seven deliberate flaws.
  Their answer key, `subject-defects.md`, sits beside the app and never inside it, because a subject that can read the answer key can satisfy it.

---

## Project Document Index

Read a document whole when its trigger matches, because a search finds only what you already suspect and misses the trap or settled decision you didn't.
A trigger may instead name the part to read, but only for history or reference that no task is checked against.
When you append, prune stale entries, and split one still too long into topic files beside it (**shards**), leaving a pointer line per shard in the original; open a shard only when the task names its topic.
Skills cite entries by name, so keep names stable.

Create a missing document and its entry here from `project-document-templates.md` when that file is loaded, else through a subagent that invokes the `andthen:init` skill with `seed <name>`.

- **Product** – `docs/PRODUCT.md`: vision, users, principles, non-goals, and Proportionality facts; the principles and facts assess added machinery. Read before proposing or changing product scope, skills, workflows, or architecture, or triaging an issue or feature request; update when goals, non-goals, or scale facts change.
- **Architecture** – `docs/ARCHITECTURE.md`. Read for changes to skill structure, shared references, or install-time propagation.
- **Specs & Plans** – `docs/temp/specs/<feature>/`: gitignored working specs per feature (a PRD, `plan.json`, one FIS per story), written by the `clarify` and `plan` skills. Read the governing FIS before implementing a story. Update the plan and FIS as execution proceeds, never the PRD. `plan.json` has one writer per copy at a time – the session executing a story writes its row, and a `plan` breakdown's story subagents never write it. An oversized FIS is a story too big: decompose it (`OVERSIZE:`), never trim it.
- **Key Dev Commands** – `docs/KEY_DEVELOPMENT_COMMANDS.md`: test tiers, live evals, the shipped-surface word count, release steps, install-script cautions. Read before running any check; its rows are executed verbatim. Update when a command changes.
- **Testing Strategy** – `docs/TESTING-STRATEGY.md`. Read before authoring a test; update when a convention changes.
- **Changelog** – `CHANGELOG.md`. Read the section you write under before writing an entry.
  Write one only when a release changes what a user runs, gets, or must do (a skill, flag, artifact, or install step added, removed, or behaving differently), because every extra bullet buries the ones an upgrading user needs.
  Skip doc wording, figures, layout, and internal refactors, and rework the bullet when the release already lists the thing changed.
  Bullets are a bold lead plus one or two sentences.
  On a `feat/<version>` branch, write under `## [<version>]`, never `[Unreleased]`.
- **Plugin reference** – `plugin/README.md`: the canonical user-facing reference for every shipped skill. Read the skill's section and every line naming it before changing or describing its behavior; update when a flag, mode, or edge case changes.
- **Public intro** – `README.md`: the front door (about 3k words), covering install, setup, the first feature, and the nine core skills. Update when a user-invocable skill is added, renamed, or removed – the shipped skill count, and a row when it is one of the nine – and regenerate its figures with `python3 scripts/skills-overview.py`.
- **Cookbook** – `COOKBOOK.md`: task recipes, how the workflow fits together, team work, and the worked example. Read the recipes for a workflow before describing it to users; update when a skill, option, or artifact a recipe names changes – `scripts/audit-cookbook.py` fails CI on a stale reference.
- **Migration guide** – `MIGRATING-FROM-0.x.md`: 0.x → 1.0 migration prompt and retired-name mapping; delete it once 0.x is out of circulation. Read and update when a 1.0 skill named in its table is renamed or moved – `scripts/audit-cookbook.py` covers it too.
- **Ubiquitous Language** – `docs/UBIQUITOUS_LANGUAGE.md`: canonical terms and the synonyms to avoid. Read before naming, renaming, or describing framework concepts; add a row when a term settles, on the shape its header states.
- **Models** – `docs/models/`: committed typed projections (`architecture-model.json`, `event-storms/<slug>.json`). Regenerate at deliberate points, never per commit, and never hand-edit – the code and the session are the records. Nothing validates a model, so the producer checks it against the schema and reference in `plugin/skills/describe/references/` or `plugin/skills/domain/references/`.
- **Role Pin Record** – `docs/ROLE-PINS.md`: the last recalibration's sources, margins, and shortlist behind the role templates. The `recalibrate-roles` skill reads it first and overwrites it.
- **Skill-authoring guidelines** – `docs/SKILL-AUTHORING-GUIDELINES.md`: the one source for prompt and skill craft, and the `skill-review` skill's rubric. Read before authoring, editing, or reviewing prompt-like content (skills, references, agent definitions, instruction files), or a doc line that tells the reader to invoke a skill; its § Repository constraints holds this repo's skill and agent rules.
- **Dev guidelines** – `docs/guidelines/`: foundational rules (CRITICAL-RULES) plus project-authored guidelines. Read at task start for any code or script change, or before triaging an issue or feature request.
- **Research** – `docs/temp/research/`: transient research artifacts, not shipped. Read when re-opening that investigation; write when a task produces durable research.
- **Learnings** – `docs/LEARNINGS.md`. Read at task start for skill, packaging, or agent-workflow changes; add a bullet when bitten by a non-obvious failure.
- **Decisions** – `docs/DECISIONS.md`: ADR index and Still Current notes. Read before proposing or changing a design or architecture choice; settled decisions are not relitigated without new evidence.
- **Plugin manifests** – `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `plugin/.claude-plugin/plugin.json`, `plugin/.codex-plugin/plugin.json` (Copilot reads the Claude Code pair). Write all four together on an install-metadata change.
  A version bump is the first commit of a `feat/<version>` branch, else it happens at release, and follows `docs/KEY_DEVELOPMENT_COMMANDS.md` § Version bump.
- **Agent Temp** – `.agent_temp/`: scratch workspace for reviews, research, and QA; never ship from it.

---

## Project-Specific Guidelines and Rules

### General Principles

- Before a refactor beyond a Boy Scout tidy, a design change to a skill or the architecture, or a change in `plugin/references/`, get a second opinion from an `oracle` subagent (the decision, its reasoning, the rejected alternatives); afterwards, review the change in a subagent as the next section routes it. This standing rule is the user's ask.
- On Codex only the smoke set is a gate. Any other Codex failure, `plan-asks` included, is a host-behaviour report until reproduced, never a reason to reword a skill, because two sessions once lost hours rewording against an upstream cause. Read `evals/README.md` before acting on an eval result.
- While an eval tier runs, edit nothing in `evals/`, because running cells read its cases, subject, and harness from this tree. `plugin/` is editable once the run prints `candidate staged:`.
- The repo's Bash hook blocks inline interpreters (`python3 -c`, `sh -c`, `eval`) and `rm -rf`.
  Write a script under `.agent_temp/` and run it by path, and delete with `rm -r`.
- Before editing `plugin/` while another session's uncommitted changes sit there, or before launching a side session on it, write which files each session owns in `.agent_temp/session-ownership.md`, because five sessions on `plugin/` once ended in a 21-file consolidation.
  Every session in this tree reads that gitignored file, and a side session in its own worktree gets its owned files in its launch prompt.

### Skill, Prompt and Intent Engineering Rules

- Shipped skills and references cite nothing outside `plugin/`, such as this repo's `docs/`, ADRs, or `AGENTS.md`, because only `plugin/` ships: state what a skill needs in the skill or a shared reference. A file in the user's project, such as a default `docs/PRODUCT.md`, is not such a citation. No external URLs unless explicitly asked.
- Review a changed skill, reference, or other prompt-like file with the project-level `skill-review` skill (`.claude/skills/skill-review/`, symlinked at `.agents/skills/` for Codex; ADR-021). It outranks the `andthen:review` skill for those files, so a mixed change runs `skill-review` over its prompt-like files and leaves only scripts and tests to `andthen:review`.
  After a `--fix`, rerun `skill-review` only when it resolved a CRITICAL or HIGH finding, and only over the fix diff.

### Git Remotes

One remote: `origin` is the public repo (`IT-HUSET/andthen`).
Changes land through a pull request from their `feat/<version>` branch, because CI runs on pull requests only.
Releases target `develop`; a patch may target `main`.
`main` carries versions real users tested on `develop`: tag `v<version>` on `develop` before that test period (`v0.40.4` is the last 0.x), then promote the tagged commit to `main` by fast-forward, leaving later `develop` work out.
`develop` always contains `main`, so a patch that lands on `main` is carried into `develop` in the same sitting.
Both paths' commands are in `docs/KEY_DEVELOPMENT_COMMANDS.md` § Release.

### Maintenance Contracts

- Every shipped skill is user-invocable, so a skill change updates `README.md`, `plugin/README.md`, and `CHANGELOG.md` on their index entries' terms.
- Tests live in `tests/`, one file per script they prove, never under `plugin/`, because every host installs the plugin directory wholesale.
- Adding, renaming, or removing a shared canonical in `plugin/references/` updates `docs/ARCHITECTURE.md`'s **Shared Plugin Assets** table and, in `scripts/andthen_loose.py`, `_canonical_assets` and the `_skill_assets_*` array of every consuming skill.
- Renaming or reshaping a parsed contract (a report template, finding IDs, a heading another file cites by name) updates its readers in the same change, found by `rg` for the old token across `plugin/` and `evals/cases/`, because nothing on the cited side marks a citation and an eval case keyed on the old shape fails on both hosts.
- A change to a `gh` command the `tracker` skill spells gets the live GitHub check (`docs/TESTING-STRATEGY.md` § Live GitHub Check) before merge.
- Release-time flips carry a `pre-release` comment (found by `rg 'pre-release[:]'`) at their site, each stating its own flip.
- Before a release, and when a provider ships or reprices a model, run the project-level `recalibrate-roles` skill (`.claude/skills/recalibrate-roles/`) over the role templates (`plugin/skills/init/templates/agents/`).

---

## Documentation Lookup Tools

Send library, framework, or API documentation lookups to a `worker` subagent whose prompt names the question and the library versions.
It prefers official documentation for those versions, then the most authoritative source, and returns conclusions with source citations, and reports a missing source or version gap in place of answering from memory.
