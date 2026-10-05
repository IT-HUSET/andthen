# Mode: codebase

Map an existing codebase into structured documentation and discovered implicit requirements; with `MODEL`, emit the typed Architecture Model.

## Rules

`Learnings`, `Architecture`, `Key Dev Commands`, `Context Map`, `ADRs`, and `Models` are Project Document Index entries. Read `Learnings`, when it exists, before starting.

- **Discovery, not invention.**
- **Merge, never overwrite.** `Architecture` and `Key Dev Commands` are derived documents: an existing one is merged per the **Regeneration contract** in `project-document-templates.md`. Name any `<NAME>.discovered.md` pair it produces in the completion summary.

## Workflow

`MODEL_ONLY` runs Step 1 and Step 2a's model emission only, skipping every documentation output and Steps 3 and 4. Existing `Architecture` and `Context Map` documents inform clustering.

### 1. Survey

Detect a monorepo or workspace. When one is found, list the workspace tool and sub-projects, set `IS_MONOREPO`, and pass the sub-project list to every analysis subagent.

**Gate**: `IS_MONOREPO` is decided, with the sub-project list when set.

### 2. Parallel analysis

Spawn parallel subagents, each prompt carrying its task and a scope that is read-only on source: a subagent writes only the output files its brief names, such as its document or `architecture-model.json`.

- **Small retrieval** – the command inventory (2c), when tightly scoped: a `worker`.
- **High judgment** – everything else: architecture with its testing overview, boundary analysis, conventions synthesis, and requirements and decision discovery. Always a generic inherited subagent, since judgment keeps the session's model; never downshift these as scanning.

A subagent briefed to write a derived document carries the Regeneration contract in its brief: an analyst who never sees it overwrites the file it was meant to merge into.

Under `IS_MONOREPO`, every subagent organizes findings by sub-project boundary, documents shared aspects once, and calls out per-sub-project specifics only where they differ.

#### 2a. Architecture

Document what the system is built on (language, runtime, main framework – versions stay in the manifest), system design and component boundaries, key modules and their responsibilities, data flow, entry points (routes, CLI, event handlers), and integration points with external systems and infrastructure. In a monorepo, add sub-project boundaries and inter-project relationships.

Add a "Testing" section covering test frameworks, test directory structure, coverage patterns, test helpers and fixtures, and integration or E2E setup. One subagent writes the whole document, because two writers to one file overwrite each other.

Output: the `Architecture` document (default `OUTPUT_DIR/ARCHITECTURE.md`).

Under `MODEL` or `MODEL_ONLY`, the same subagent emits the **Architecture Model** – the typed JSON `architecture-model.md` defines – as `architecture-model.json` under `Models` (default `docs/models/`).

**Deterministic first.** Nodes and edges come from ecosystem dependency tooling or import scans plus git change-coupling (evidence `imports` / `git-coupling`). Where the ecosystem has no import graph, they come from structured declarations in project docs and manifests (evidence `declared`). Agent judgment is confined to clustering nodes into contexts, naming, summaries, and optional tours (evidence `inferred`).

#### 2b. Conventions

Document naming conventions, file organization patterns, error handling, logging, testing patterns, and code style (formatting, imports, exports).

Output: a `## Conventions` section for the project's root agent instruction file. Append it to whichever of `CLAUDE.md` and `AGENTS.md` exists, keeping the section aligned in both when both exist. With neither, include the section in the completion output, so the `andthen:init` skill can insert it when it creates the file.

#### 2c. Key development commands

Discover commands from the sources the KEY_DEVELOPMENT_COMMANDS.md template names, and fill its Testing tiers and run-one-test row: a document that declares no tiers leaves every reader inferring what is heavy. In a monorepo, organize commands per sub-project and identify the root-level orchestration commands.

Output: the `Key Dev Commands` document (default `docs/KEY_DEVELOPMENT_COMMANDS.md`).

**Gate**: every analysis subagent has returned, and each output file exists with one writer.

### 3. Requirements and decisions discovery

Spawn a high-judgment subagent, per Step 2, to reverse-engineer a discovered requirements document from:

- **What the system does** – user-facing features and workflows (routes, UI, API), admin and operator features, background processes.
- **Implicit requirements** – validation rules, business logic, access control, data integrity rules.
- **External dependencies** – third-party API contracts, infrastructure and environment requirements.
- **Non-functional characteristics** – caching, rate limiting, error handling, logging, performance optimizations.

The same subagent identifies the **load-bearing implicit decisions** visible in the code – framework choice, persistence shape, boundary lines between modules, build and test tooling, deployment topology – and any ADRs already under `ADRs`. They constrain future work even when no ADR was ever written.

Output `OUTPUT_DIR/requirements-discovered.md`, compatible with the `andthen:plan` skill's input, with these sections and entry shapes:

```markdown
# Discovered Requirements: [Project Name]
> Status: Discovered – requires validation by team

## System Overview
## Discovered Features
### [Feature Area]
- **REQ-D01**: [description] – Evidence: [file paths] – Confidence: High/Medium/Low
## Implicit Business Rules
- **RULE-D01**: [rule] – Evidence: [where enforced]
## External Integration Contracts
- **INT-D01**: [system] – Contract: [what the code expects]
## Non-Functional Characteristics
## Gaps & Uncertainties
```

Output `OUTPUT_DIR/decisions-discovered.md` in the `DECISIONS.md` template shape from `project-document-templates.md`, headed `> Status: Discovered – requires validation by team`. Existing in-tree ADRs go in **Current ADRs**; implicit load-bearing decisions go in **Still Current** with brief evidence (a file path or pattern). **Superseded** and **Pending** stay empty unless evidence supports an entry.

**Gate**: both discovered documents are written in their shapes.

### 4. Sub-project instruction files

In a monorepo, write a lightweight agent instruction file, matching the root choice (`CLAUDE.md`, `AGENTS.md`, or both), for each sub-project that lacks one: name and description, an inline table of key development commands, and sub-project-specific notes.

**Gate**: every sub-project has an instruction file.

## Output

Print each output file's path relative to the project root, the Architecture Model JSON included when emitted; under `MODEL_ONLY`, print only the model's path.

The discovered requirements and decisions are for team review, and `decisions-discovered.md` is promoted into `DECISIONS.md` once confirmed.

## Follow-up

Suggest the `andthen:plan` skill on `OUTPUT_DIR/requirements-discovered.md`.
