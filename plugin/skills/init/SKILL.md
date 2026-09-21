---
description: Set up the AndThen workflow structure – new projects, partial setups, brownfield codebases. Trigger on 'set up AndThen', 'initialize the workflow'.
argument-hint: "[project name]"
---

# Initialize Project


`PROJECT_NAME` is `$ARGUMENTS` – optional; absent, infer it from the directory name or package config.


## INSTRUCTIONS

- **Non-destructive** – Preserve existing content; replace only what the user explicitly selects.
- **Defaults, then options** – Core orientation stubs, gitignore hygiene, and missing Index entries land without prompting; everything else is offered.


## WORKFLOW

### 1. Detect Current State

Scan the project to determine the setup path:

1. **Check the existing setup** – root agent instruction files (`CLAUDE.md`, `AGENTS.md`), `docs/` and its documents, guidelines in docs/guidelines/, and package config (package.json, Cargo.toml, go.mod, pyproject.toml, deno.json, etc.) for project name and tech stack
2. **Check the Python 3 runtime** – run `python3 --version` (on Windows, `python --version` when only the launcher is on PATH). Python 3 is AndThen's one runtime requirement: the `andthen:tracker` skill's projection is a stdlib script. Absent, carry `python3 not found → tracker projection unavailable` into the Step 4 summary and continue – nothing in setup depends on it.
3. **Detect monorepo/workspace structure** – look for `pnpm-workspace.yaml`, `lerna.json`, `nx.json`, `turbo.json`, `"workspaces"` in root `package.json`, `[workspace]` in root `Cargo.toml`, `go.work`, or multiple sub-dirs with their own package config. If detected, note the workspace tool, list sub-projects, and set `IS_MONOREPO = true`.
4. **Detect a test suite and a served UI** – a test directory or a manifest test script; a UI framework dependency, HTML templates, or a dev/serve script. Carry each result into the Step 4 offers.

Classify into one of three paths:

| State | Indicators | Path |
|-------|-----------|------|
| **New project** | No CLAUDE.md or AGENTS.md, minimal or no docs/ | → Step 2a |
| **Partial setup** | CLAUDE.md and/or AGENTS.md exists but missing sections or document types | → Step 2b |
| **Brownfield** | Substantial codebase but no agent instruction file or workflow structure | → Step 2c |

**Gate**: Project state classified


### 2a. New Project Setup

Ask for the context Step 1 could not infer – description, tech stack, and the project name when `PROJECT_NAME` is absent and inference failed.

Generate the root agent instruction file(s) using `templates/CLAUDE.template.md` as the base, by the host(s) in play:

- **Claude Code alone** – one full `CLAUDE.md`.
- **Codex or a generic agent alone** – one full `AGENTS.md`.
- **Both, or the target unclear** – `AGENTS.md` carries the full template content and `CLAUDE.md` is a thin import: `@AGENTS.md` as the first line, Claude-specific additions (if any) below it under a `## Claude Code` heading.

Claude Code expands the import at session start; Codex never reads `CLAUDE.md`, so the `@` sigil is safe there, and shared content has exactly one authored home.

Fill in the Project Overview section; keep the Project Document Index and Project-Specific Guidelines and Rules sections intact; leave no `TODO` placeholder behind – resolve each from the project context or delete its section, since an instruction file is read on every turn of every session.

Create the base directories `docs/specs/` and `docs/guidelines/`.

Gitignore hygiene: append an entry for the agent workspace (`.agent_temp/`) to `.gitignore` idempotently (only if absent); create `.gitignore` if missing.

Offer to ignore or commit review reports, recommending **ignore**: a report is a working file of one review run, read by whoever ran it and the fix that follows, while a committed one puts what was reviewed and at which revision in the team's history. On **ignore**, append `*-andthen-*-review-*.md` the same idempotent way; on commit, write nothing.

Offer the **role agents** – ask, never assume. The subagent definitions `oracle`, `implementer`, `reviewer`, and `worker` in `templates/agents/` (Claude Code `.md`, Codex `.toml`) make the Subagent Model Policy's tiers enforceable: a definition pins model and effort for every spawn of that role, instead of relying on each spawn call to set them.

Compare what is installed against the shipped templates at both levels for the host(s) in play – a copy from an older release differs. Anything differing → name those files and ask before replacing; never overwrite one unasked. Nothing installed → ask the level:

- **User** – a personal default across projects: `agents/` under `$CLAUDE_CONFIG_DIR` / `$CODEX_HOME`, defaulting to `~/.claude` / `~/.codex`.
- **Project** – `.claude/agents/`, `.codex/agents/`, sharing the pins with the team.

Create nothing under a host whose home directory is absent. Definitions load at session start, so the roles take effect next session.

Scaffold the **Core orientation stubs by default** – the documents every project benefits from agents being able to find: `Product` (docs/PRODUCT.md), `Architecture` (docs/ARCHITECTURE.md), `Key Dev Commands` (docs/KEY_DEVELOPMENT_COMMANDS.md), `Testing Strategy` (docs/TESTING-STRATEGY.md), `Decisions` (docs/DECISIONS.md), `Learnings` (docs/LEARNINGS.md). Create these from the templates in `../../references/project-document-templates.md` without prompting; pre-fill what's auto-detectable (e.g., the `Key Dev Commands` document from manifest scripts).

The `andthen:architecture` skill in `--mode trade-off` auto-registers accepted ADRs into the `Decisions` stub.

**Ask for the `Product` document's Proportionality facts and write the answers in** – three questions alongside the Step 2a context questions: _"Stage – prototype, internal, or production?"_, _"Scale – how many users, how much data, what deploy topology, how many maintainers?"_, and _"Standing technical non-goals – what should this project not grow (new services, a plugin system, a config surface)?"_. Ask an unanswered one once more, then write `unknown`; never leave a TODO stub or an empty section.

Then present the **optional documents**, recommendation-first. Wait for the user's selection before creating any of these:

- **Planning** (optional): `Roadmap` (docs/ROADMAP.md).
- **Domain** (optional): `Ubiquitous Language` document (the `andthen:clarify` skill seeds it as terms settle; the `andthen:describe` skill in `--mode domain` extracts it in full).
- **Monorepo** (if `IS_MONOREPO = true`): offer per-sub-project agent instruction files matching the root file choice

Lead with a recommendation drawn from what Step 2a detected, and let the user reply **"default"** to accept it: add `Roadmap` when the intent spans multiple features or phases; add `Ubiquitous Language` for domain-heavy work. State the recommendation, then ask: _"Which optional documents would you like to create alongside the Core stubs? Reply 'default' to accept the recommendation, name specific documents (e.g. 'Roadmap, Ubiquitous Language'), or 'none for now'."_

For each confirmed document type, generate the file from templates in `../../references/project-document-templates.md`, using the location from the **Project Document Index** or the default path above.

For each confirmed sub-project agent instruction file, generate a lightweight file (under ~40 lines) containing: sub-project name and description, key development commands (inline table), and any conventions that differ from root. Mirror the root file choice (`CLAUDE.md`, `AGENTS.md`, or both – both uses the same thin-import pattern; `@` paths resolve relative to the importing file, so the sub-project `CLAUDE.md` imports its sibling `AGENTS.md`). Also update the root `Key Dev Commands` document (see **Project Document Index**) if created to include per-sub-project sections.

**Gate**: Agent instruction file(s) and selected documents generated; the `Product` document's Proportionality section answered, `unknown` included, never a stub – then Step 3.


### 2b. Partial Setup (CLAUDE.md and/or AGENTS.md exists)

Read [`partial-setup.md`](references/partial-setup.md) now and work it: what to check in the existing files, the host-layout repair, which gaps are applied by default, and the confirmed-action list.

**Gate**: All selected gaps filled – then Step 3.


### 2c. Brownfield Setup (existing codebase, no workflow structure)

Inform the user:
```
Existing codebase detected without AndThen workflow structure.

Recommended approach:
1. Invoke the `andthen:describe` skill in `--mode codebase` to auto-generate the `Architecture` document (see **Project Document Index**) plus conventions for the root agent instruction file(s)
2. Then set up the agent instruction file(s) and remaining structure

Invoke the `andthen:describe` skill first? (recommended for codebases with 20+ files)
```

Wait for response. If yes: invoke the `andthen:describe` skill in `--mode codebase`, then proceed with Step 2a using generated documents as foundation (skip the `Architecture` document from templates). If no: proceed directly to Step 2a.

**Gate**: Brownfield analysis complete or declined


### 3. Adopt Project Rules

Policy in the project instruction file travels with the checkout, into CI and containers, which a user-level append never reaches – that is why project tier is the default. The shipped `templates/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md` is a starter, not a runtime dependency or a policy to synchronize on upgrades: required skill behavior stays in the owning skill, so a team may customize or decline it and nothing breaks.

Read the root instructions and any existing critical-rules reference before offering adoption. An existing policy – custom, referenced, or a copy of the template – is valid setup: preserve it, and offer replacement only when the user asks for an update, showing the diff first. When neither a policy nor an opt-out is present, recommend adopting the rules in the root instruction file and offer **skip**. Wait for the choice unless already authorized:
- **Adopt**: place the guideline body in the root instruction file under its own `# Critical Rules and Guardrails` heading, rewriting only from that heading to the next top-level heading so surrounding content and customizations survive. A symlinked instruction file is never written through – report it and stop, since the target lives outside the project. Both hosts share `AGENTS.md` through the Step 2a import layout; reconcile an unconverted pair only with agreement (Step 2b) and otherwise apply per host what was confirmed for that host. Never create a second copy of the guideline: an existing project that moves its rules inline updates their references in the same pass. Name any user-level copy you find and let the user decide whether to keep it – never remove or replace it automatically.
- **Skip**: add the standalone marker `<!-- AndThen critical rules: skipped -->` to each owning instruction file where adoption was declined (`AGENTS.md` alone in the shared layout). It records the choice across init runs; remove it only when the user later asks to adopt. Active rules take precedence over the marker; it does not disable existing project or global policy.

**Personal configuration (only when requested).** User-level rules take the same bounded block in the same host home as the role agents (Step 2a); skip an absent one. Conversation style is independent of rules adoption: read `templates/output-styles/concise-critical.md` and configure only the requested hosts:
- **Claude Code**: the installed plugin registers `<plugin-name>:concise-critical`; otherwise copy the style to the host's `output-styles/` and use `concise-critical`. Merge `outputStyle` into user `settings.json`, preserving other keys; report a project setting that shadows it.
- **Codex**: put the style body below its frontmatter into top-level `developer_instructions` in user `config.toml`, above the first table header. Preserve existing instructions and other settings.

Never replace an existing style choice or rewrite an unparseable configuration. If the user wants the style in an instruction file instead, append its body there. Tell the user configuration changes take effect next session.

**Gate**: Project policy adopted, preserved, or explicitly declined; only requested personal configuration changed.

### 4. Final Summary

List **only what this run created or changed**, plus the Step 1 runtime line when Python 3 was absent: one line per file with its purpose, grouped as project setup, selected optional documents, and requested personal configuration, with project paths relative to the project root and host paths written with `~`. State the critical-rules outcome; omit unchanged groups.

**Offer the documents this skill cannot author** – a stub is a location, its content comes from the project itself. Offer to invoke the `andthen:testing` skill in `--mode strategy` when Step 1 found a test suite, and the `andthen:visual-validation` skill in `--mode setup` when it found a served UI – that one serves the app and proves the capture procedure before writing it down. One line each, and invoke what the user accepts; a project with neither is offered neither.

Close with next steps: customize the root instruction file's Project Overview, then the `andthen:now-what` skill to route from an idea, or a named skill (the `andthen:clarify`, `andthen:plan`, or `andthen:architecture` skill) when the user already knows what they want.
