---
description: Analyze an existing codebase to produce structured documentation and discover implicit requirements. Trigger on 'map codebase', 'map this repo', 'analyze the project', 'understand this codebase', 'what does this repo do'.
argument-hint: "[output directory (defaults to docs/)]"
---

# Map Codebase


## VARIABLES

_Output directory (defaults to `docs/`, or as configured in **Project Document Index**):_
OUTPUT_DIR: $ARGUMENTS or `docs/`


## INSTRUCTIONS

- Read project rules and guidelines (`CLAUDE.md` / `AGENTS.md` and referenced files) before starting.
- **Read project learnings** – If the `Learnings` document (see **Project Document Index**) exists, read it before starting
- **Read-only source analysis** – no source-code changes or commits; documentation outputs and agent-instruction Conventions updates are the only expected writes
- **Structured output** – All documents follow templates from `${CLAUDE_PLUGIN_ROOT}/references/project-state-templates.md`
- **Discovery, not invention** – Document what exists, don't prescribe what should exist


## GOTCHAS
- Producing a surface-level summary instead of deep structural analysis
- Missing implicit conventions that aren't documented but are visible in code patterns


## WORKFLOW

### 1. Codebase Survey

1. Survey project shape: directory tree, file inventory, existing docs (README, CLAUDE.md, AGENTS.md, docs/), primary language(s)/frameworks from config files, and recent git history.
2. **Detect monorepo/workspace structure** – look for `pnpm-workspace.yaml`, `lerna.json`, `nx.json`, `turbo.json`, `"workspaces"` in root `package.json`, `[workspace]` in root `Cargo.toml`, `go.work`, or multiple sub-dirs with their own package config. If detected: list workspace tool and sub-projects. Set `IS_MONOREPO = true` and pass the sub-project list to all analysis sub-agents.

**Gate**: Project shape understood, technologies identified, monorepo status determined


### 2. Parallel Analysis

Spawn parallel sub-agents, routing each per the **Sub-Agent Model Policy** (default: inherit): *scanning* (retrieval) at **low** effort, *synthesis* (routine) at **medium**.

**Monorepo note** (apply to all sub-agents when `IS_MONOREPO = true`): organize findings with clear sub-project boundaries. Document shared aspects once; only call out per-sub-project specifics where they differ.

#### 2a. Stack Analysis (sub-agent)
Analyze and document languages/versions, frameworks and libraries (with versions from lock files), infrastructure, external services, build tools and CI/CD.
Output: the `Stack` document (see **Project Document Index**; default: `OUTPUT_DIR/STACK.md`)

#### 2b. Architecture Analysis (sub-agent)
Analyze and document system design and component boundaries, key modules and responsibilities, data flow, entry points (routes, CLI, event handlers), and integration points with external systems. If monorepo: document sub-project boundaries and inter-project relationships.
Output: the `Architecture` document (see **Project Document Index**; default: `OUTPUT_DIR/ARCHITECTURE.md`)

#### 2c. Conventions Analysis (sub-agent)
Analyze and document naming conventions, file organization patterns, error handling, logging, testing patterns, and code style (formatting, imports, exports).
Output: a `## Conventions` section for the project's root agent instruction file (`CLAUDE.md` and/or `AGENTS.md`). Append it to whichever root instruction file exists; if both exist, keep the section aligned in both; if neither exists, include the section in the completion output so the `andthen:init` skill can insert it when creating the file(s).

#### 2d. Testing Overview (sub-agent)
Analyze test framework(s), test directory structure, coverage patterns, test helpers/fixtures, and integration/E2E setup.
Output: included in the `Architecture` document (see **Project Document Index**) under a "Testing" section

#### 2e. Key Development Commands Discovery (sub-agent)
Discover commands by scanning `package.json` scripts, `Makefile`, `Taskfile.yml`, `justfile`, `deno.json`, `Cargo.toml` aliases, CI/CD configs, and README files. If monorepo: organize commands per sub-project and identify root-level orchestration commands.
Output: the `Key Dev Commands` document (see **Project Document Index**; default: `docs/KEY_DEVELOPMENT_COMMANDS.md`)

**Gate**: All analysis sub-agents complete


### 3. Requirements & Decisions Discovery

Spawn a sub-agent (capable coding model) to reverse-engineer a discovered requirements document by analyzing:

- **What the System Does**: user-facing features/workflows (routes, UI, API), admin/operator features, background processes
- **Implicit Requirements**: validation rules, business logic, access control, data integrity rules
- **External Dependencies**: third-party API contracts, infrastructure requirements, environment requirements
- **Non-Functional Characteristics**: caching, rate limiting, error handling, logging, performance optimizations

Extend the same sub-agent's brief to also identify **load-bearing implicit decisions** visible in the codebase – framework choice, persistence shape, boundary lines between modules, build/test tooling, deployment topology – and any in-tree ADRs already present under the `ADRs` location. These are decisions worth surfacing because they constrain future work, even when no ADR was ever written.

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

Also emit `OUTPUT_DIR/decisions-discovered.md` using the `DECISIONS.md` template shape from `${CLAUDE_PLUGIN_ROOT}/references/project-state-templates.md`, with the header `> Status: Discovered – requires validation by team` (same convention as `requirements-discovered.md`). Place existing in-tree ADRs in **Current ADRs**; place implicit load-bearing decisions in **Still Current** with brief evidence (file path or pattern). Leave **Superseded** and **Pending** empty unless evidence supports an entry.

**Gate**: Requirements and decisions discovery complete


### 4. Output Summary

1. Write all documents to `OUTPUT_DIR/`
2. Print summary listing all generated files with brief descriptions
3. If `IS_MONOREPO = true`: generate lightweight sub-project agent instruction file(s) that match the root file choice (`CLAUDE.md`, `AGENTS.md`, or both) for each sub-project that doesn't already have them (under ~40 lines: name/description, key development commands inline table, sub-project-specific notes)
4. Suggest next steps: review discovered requirements and decisions with team (validate `decisions-discovered.md` and promote to `DECISIONS.md` when confirmed), invoke the `andthen:plan` skill: `/andthen:plan docs/requirements-discovered.md`


## OUTPUT

Print each output file's **relative path from the project root**.
