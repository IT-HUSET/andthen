# Mode: codebase

Map an existing codebase into structured documentation and discovered implicit requirements; with `--model`, emit the typed Architecture Model.


## INSTRUCTIONS

- **Read project learnings** – If the `Learnings` document (see **Project Document Index**) exists, read it before starting
- **Regeneration contract** – The `Architecture` and `Key Dev Commands` documents are derived documents: an existing one is merged, never overwritten, per the **Regeneration contract** in `project-document-templates.md`. Name any `<NAME>.discovered.md` pair it produces in the completion summary
- **Discovery, not invention** – Document what exists, don't prescribe what should exist
- **Model-only fast path** (`MODEL_ONLY`) – run only the codebase survey (step 1) and the Architecture Model emission from step 2a; skip every documentation output and the discovery steps. Existing `Architecture` and `Context Map` documents inform clustering. This is the normal way to refresh the committed projection.


## WORKFLOW

### 1. Codebase Survey

1. Survey project shape: existing docs (README, CLAUDE.md, AGENTS.md, docs/), primary language(s)/frameworks from config files, and recent git history.
2. **Detect monorepo/workspace structure** – look for `pnpm-workspace.yaml`, `lerna.json`, `nx.json`, `turbo.json`, `"workspaces"` in root `package.json`, `[workspace]` in root `Cargo.toml`, `go.work`, or multiple sub-dirs with their own package config. If detected: list workspace tool and sub-projects. Set `IS_MONOREPO = true` and pass the sub-project list to all analysis subagents.

**Gate**: Project shape understood, technologies identified, monorepo status determined


### 2. Parallel Analysis

Spawn parallel generic subagents whose prompts carry the task and a read-only scope – the installed role agent for the tier when available, else inherit, never a model or effort pinned in the prompt. Route each task to its tier:

- **Small retrieval** – command inventory, when tightly scoped.
- **High judgment** – architecture, boundary analysis, conventions synthesis, and implicit-requirements/decision discovery. Never downshift these as scanning.

A subagent briefed to write a derived document carries the **Regeneration contract** in its brief – an analyst who never sees it overwrites the file it was meant to merge into.

**Monorepo note** (apply to all subagents when `IS_MONOREPO = true`): organize findings with clear sub-project boundaries. Document shared aspects once; only call out per-sub-project specifics where they differ.

#### 2a. Architecture Analysis (subagent)
Analyze and document what the system is built on (language, runtime, main framework – versions stay in the manifest), system design and component boundaries, key modules and responsibilities, data flow, entry points (routes, CLI, event handlers), and integration points with external systems and infrastructure. If monorepo: document sub-project boundaries and inter-project relationships.
Output: the `Architecture` document (see **Project Document Index**; default: `OUTPUT_DIR/ARCHITECTURE.md`)

When `MODEL`, the same subagent also emits an **Architecture Model** – the typed JSON defined in `architecture-model.md` – as `architecture-model.json` under the `Models` location (see **Project Document Index**; default: `docs/models/`), a committed projection per the schema's Persistence and precedence: `meta.revision` is the code revision it describes, and the code stays the record. Method contract:
- **Deterministic first** – nodes and edges come from ecosystem dependency tooling or import scans plus git change-coupling (evidence `imports` / `git-coupling`) – or, where the ecosystem has no import graph, from structured declarations in project docs and manifests (evidence `declared`); agent judgment is confined to clustering nodes into contexts, naming, summaries, and optional tours (evidence `inferred`).
- Every node carries a real repo-relative `ref` – a node whose location can't be named is invention, not discovery.
- When a `Context Map` document exists (see **Project Document Index**), bounded-context ids/names come from it – never a second name for a mapped context.
- Check the candidate against `architecture-model.schema.json` and `architecture-model.md` before writing.

#### 2b. Conventions Analysis (subagent)
Analyze and document naming conventions, file organization patterns, error handling, logging, testing patterns, and code style (formatting, imports, exports).
Output: a `## Conventions` section for the project's root agent instruction file (`CLAUDE.md` and/or `AGENTS.md`). Append it to whichever root instruction file exists; if both exist, keep the section aligned in both; if neither exists, include the section in the completion output so the `andthen:init` skill can insert it when creating the file(s).

#### 2c. Testing Overview (subagent)
Analyze test framework(s), test directory structure, coverage patterns, test helpers/fixtures, and integration/E2E setup.
Output: included in the `Architecture` document (see **Project Document Index**) under a "Testing" section

#### 2d. Key Development Commands Discovery (subagent)
Discover commands from the sources the KEY_DEVELOPMENT_COMMANDS.md template names, and fill its Testing tiers and run-one-test row – a document that declares no tiers leaves every reader inferring what is heavy. If monorepo: organize commands per sub-project and identify root-level orchestration commands.
Output: the `Key Dev Commands` document (see **Project Document Index**; default: `docs/KEY_DEVELOPMENT_COMMANDS.md`)

**Gate**: All analysis subagents complete


### 3. Requirements & Decisions Discovery

Spawn a subagent (task shape: high judgment) to reverse-engineer a discovered requirements document by analyzing:

- **What the System Does**: user-facing features/workflows (routes, UI, API), admin/operator features, background processes
- **Implicit Requirements**: validation rules, business logic, access control, data integrity rules
- **External Dependencies**: third-party API contracts, infrastructure requirements, environment requirements
- **Non-Functional Characteristics**: caching, rate limiting, error handling, logging, performance optimizations

Extend the same subagent's brief to also identify **load-bearing implicit decisions** visible in the codebase – framework choice, persistence shape, boundary lines between modules, build/test tooling, deployment topology – and any in-tree ADRs already present under the `ADRs` location. These are decisions worth surfacing because they constrain future work, even when no ADR was ever written.

Output: `OUTPUT_DIR/requirements-discovered.md` in a format compatible with the `andthen:plan` skill input. Required sections and entry shapes:

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

Also emit `OUTPUT_DIR/decisions-discovered.md` using the `DECISIONS.md` template shape from `project-document-templates.md`, with the header `> Status: Discovered – requires validation by team` (same convention as `requirements-discovered.md`). Place existing in-tree ADRs in **Current ADRs**; place implicit load-bearing decisions in **Still Current** with brief evidence (file path or pattern). Leave **Superseded** and **Pending** empty unless evidence supports an entry.

**Gate**: Requirements and decisions discovery complete


### 4. Output Summary

1. If `IS_MONOREPO = true`: generate lightweight sub-project agent instruction file(s) that match the root file choice (`CLAUDE.md`, `AGENTS.md`, or both) for each sub-project that doesn't already have them (under ~40 lines: name/description, key development commands inline table, sub-project-specific notes)
2. Suggest next steps: review discovered requirements and decisions with team (validate `decisions-discovered.md` and promote to `DECISIONS.md` when confirmed), invoke the `andthen:plan` skill on `OUTPUT_DIR/requirements-discovered.md`


## OUTPUT

Print each output file's **relative path from the project root**, including the Architecture Model JSON when emitted. With `MODEL_ONLY`, print only the model's path.
