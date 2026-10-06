---
description: Set up the AndThen workflow structure – new projects, partial setups, brownfield codebases. Trigger on 'set up AndThen', 'initialize the workflow'.
argument-hint: "[project name | seed <Index entry>]"
---

# Initialize Project

Write the root agent instruction file(s) and the defaults the AndThen skills rely on, then offer the optional rest.

## Input

`$ARGUMENTS` is the project name, optional: absent, infer it from the directory name or the package config.

- `seed <Index entry>` is a first write, run by a subagent. Create only that document at its Index location, from its section in [`project-document-templates.md`](../../references/project-document-templates.md), with any content the prompt carries, and return its path. Nothing below runs.

## Rules

- Print each recommended skill invocation as a complete, paste-ready line in the host's syntax, including its target path or request and required arguments.

- **Non-destructive** – preserve existing content; replace only what the user explicitly selects.

## Workflow

### 1. Detect

Scan the project for:

- **The existing setup** – root agent instruction files (`CLAUDE.md`, `AGENTS.md`), `docs/` and its documents, guidelines in `docs/guidelines/`, and the package manifest for the project name and tech stack.
- **A monorepo or workspace** – note the workspace tool and list the sub-projects.
- **A test suite and a served UI** – a test directory or a manifest test script; a UI framework dependency, HTML templates, or a dev or serve script.

**Gate**: One path taken – no `CLAUDE.md` or `AGENTS.md` → Step 2a; one exists → Step 2b.

### 2a. No instruction file

Ask a question only in an empty repository, where Step 1 found no manifest, README or source file. There, before you write anything, ask in one question what the project is; the answer fills the Project Overview. Everywhere else, take the Project Overview from the README, the manifest and the code, and ask nothing.

Generate the root agent instruction file(s) from [`CLAUDE.template.md`](templates/CLAUDE.template.md), by the host(s) in play:

- **Claude Code alone** – one full `CLAUDE.md`.
- **Codex or a generic agent alone** – one full `AGENTS.md`.
- **Both, or the target unclear** – `AGENTS.md` carries the full template content and `CLAUDE.md` is a thin import: `@AGENTS.md` as the first line, Claude-specific additions (if any) below it under a `## Claude Code` heading. Codex never reads `CLAUDE.md`, so the `@` sigil is safe there.

Keep the Project Document Index and the Project-Specific Guidelines and Rules sections intact, with every Index entry, including those whose document does not exist yet: the preamble's first-write sentences say how the first skill that writes one creates it.

Leave no `TODO` placeholder behind: resolve each from the project context or delete its section, since an instruction file is read on every turn of every session.

Append `.agent_temp/` and `*-andthen-*-review-*.md` to `.gitignore` when absent, creating the file if missing.

When Step 1 found a manifest, derive the `fast`, `full` and run-one-test commands from it and the task runner beside it (`Makefile`, `justfile`, the CI workflow). Seed the `Key Dev Commands` document with them through a subagent – the installed `worker` role agent when available, else a generic inherited one – that invokes this skill with `seed Key Dev Commands` and those commands, so the template set stays out of this run's context.

**Gate**: The instruction file(s) carry every Index entry and the preamble's first-write sentences, and no `TODO`; `.gitignore` carries both entries; `Key Dev Commands` exists when a manifest does; nothing else was created – then Step 3.

### 2b. An instruction file exists

Follow [`partial-setup.md`](references/partial-setup.md), with `CLAUDE.template.md` as the shape the existing file(s) are checked against.

### 3. Offer the rest

Offer each item that applies, one line each:

- the role agents `oracle`, `implementer`, `reviewer` and `worker`, which pin model and effort for each subagent tier;
- the critical rules in the root instruction file, unless a policy – inline, referenced or custom – or the skip marker is already there;
- the `andthen:describe` skill in `--mode codebase`, for an existing codebase with no filled-in `Architecture` document;
- per-sub-project instruction files, when Step 1 found a monorepo or workspace;
- the `Roadmap` and `Ubiquitous Language` documents;
- the `andthen:testing` skill in `--mode strategy`, when Step 1 found a test suite;
- the `andthen:visual-validation` skill in `--mode setup`, when Step 1 found a served UI;
- the offers Step 2b passed on.

For a role-agent, rules, document or sub-project offer taken up, the critical-rules offer declined, or a request for personal rules or a conversation style, read [`offers.md`](references/offers.md) and follow its section for it, with:

- the role agents: the [role templates](templates/agents/);
- the critical rules or personal rules: [`CRITICAL-RULES-AND-GUARDRAILS.md`](templates/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md);
- a conversation style: [`concise-critical.md`](templates/output-styles/concise-critical.md);
- the `Roadmap` or `Ubiquitous Language` document: `project-document-templates.md`.

**Gate**: Each offer taken up is done, a declined critical-rules offer is marked, and nothing was written for an offer ignored.

## Output

The closing summary lists only what this run created or changed, one line per file with its purpose, then the offers. Write project paths relative to the project root and host paths with `~`.

Say how to commit review reports instead: delete the `*-andthen-*-review-*.md` line from `.gitignore`.

## Follow-up

Recommend the `andthen:clarify` skill as the first step.
