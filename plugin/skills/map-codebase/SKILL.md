---
description: Analyze an existing codebase to produce structured documentation and discover implicit requirements. Trigger on 'map codebase', 'analyze the project', 'what does this repo do'.
argument-hint: "[output directory (defaults to docs/)]"
---

# Map Codebase


Brownfield codebase analysis that produces structured understanding of an existing codebase plus a discovered requirements document. Use this when onboarding to an existing project or when project documentation is missing/outdated.

**Output**: Structured documentation files + discovered requirements document that feeds directly into `andthen:plan`.


## VARIABLES

_Output directory (defaults to `docs/`, or as configured in **Project Document Index**):_
OUTPUT_DIR: $ARGUMENTS or `docs/`


## INSTRUCTIONS

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work
- **Read project learnings** – If `LEARNINGS.md` exists (check Project Document Index for location), read it before starting to contextualize findings with existing project knowledge
- **Read-only analysis** – No code changes, commits, or modifications
- **Delegate heavily** – Spawn parallel sub-agents for codebase analysis
- **Structured output** – All documents follow templates from `${CLAUDE_PLUGIN_ROOT}/../templates/project-state-templates.md`
- **Discovery, not invention** – Document what exists, don't prescribe what should exist


## GOTCHAS
- Producing a surface-level summary instead of deep structural analysis
- Missing implicit conventions that aren't documented but are visible in code patterns


## WORKFLOW

### 1. Codebase Survey

Quick orientation to understand the project shape:

1. Run `tree -d -L 3` for directory structure
2. Run `git ls-files | head -500` for file inventory
3. Check for existing documentation: README, CLAUDE.md, docs/, etc.
4. Identify primary language(s) and framework(s) from config files (package.json, Cargo.toml, go.mod, pyproject.toml, deno.json, etc.)
5. Check git history: `git log --oneline -20` for recent activity patterns
6. **Detect monorepo/workspace structure** – look for:
   - `pnpm-workspace.yaml`, `lerna.json`, `nx.json`, `turbo.json`
   - `"workspaces"` field in root `package.json` (npm/yarn workspaces)
   - `[workspace]` in root `Cargo.toml` (Rust workspaces)
   - `go.work` (Go workspaces)
   - Multiple sub-directories each containing their own package config

   If detected: list the workspace tool and all discovered sub-projects. Set `IS_MONOREPO = true` and pass the sub-project list to all analysis sub-agents.

**Gate**: Project shape understood, primary technologies identified, monorepo status determined


### 2. Parallel Analysis

Spawn parallel sub-agents _(if supported by your coding agent)_ to produce structured documents. Use `model: "haiku"` for scanning agents (cost-efficient) and `model: "sonnet"` for synthesis.

**Monorepo note**: If `IS_MONOREPO = true`, pass the sub-project list to each sub-agent. Each sub-agent should organize its findings with clear sub-project boundaries where differences exist. Don't duplicate shared/common information per sub-project — document shared aspects once and only call out per-sub-project specifics.

#### 2a. Stack Analysis (sub-agent)
Analyze and document:
- Languages and versions
- Frameworks and libraries (with versions from lock files)
- Infrastructure (databases, queues, caches)
- External services and APIs
- Build tools and CI/CD
- _Monorepo_: note which dependencies/tools are shared vs. sub-project-specific
- Output: `OUTPUT_DIR/STACK.md`

#### 2b. Architecture Analysis (sub-agent)
Analyze and document:
- System design and component boundaries
- Key modules and their responsibilities
- Data flow between components
- Entry points (routes, CLI commands, event handlers)
- Integration points with external systems
- _Monorepo_: document sub-project boundaries, how sub-projects relate to each other (shared libraries, API contracts, data flow between sub-projects)
- Output: `OUTPUT_DIR/ARCHITECTURE.md`

#### 2c. Conventions Analysis (sub-agent)
Analyze and document:
- Naming conventions (files, functions, variables, types)
- File organization patterns
- Error handling patterns
- Logging patterns
- Testing patterns and conventions
- Code style (formatting, imports, exports)
- _Monorepo_: note conventions that differ between sub-projects (e.g. different linters, naming styles, test frameworks)
- Output: a `## Conventions` section to be appended to the project's `CLAUDE.md`

#### 2d. Testing Overview (sub-agent)
Analyze and document:
- Test framework(s) in use
- Test directory structure
- Test coverage patterns (what's tested, what's not)
- Test helpers, fixtures, and utilities
- Integration/E2E test setup
- Output: included in ARCHITECTURE.md under a "Testing" section

#### 2e. Key Development Commands Discovery (sub-agent)
Discover commands by scanning:
- `package.json` `"scripts"` fields (all levels)
- `Makefile`, `Taskfile.yml`, `justfile`
- `deno.json` tasks, `Cargo.toml` aliases
- CI/CD configs for build/test/deploy commands
- README files for documented commands
- _Monorepo_: organize commands per sub-project; identify root-level orchestration commands (e.g. `pnpm -r test`, `nx run-many`) vs. sub-project-specific commands

Output: `docs/KEY_DEVELOPMENT_COMMANDS.md` (or location from Project Document Index), using the template from `${CLAUDE_PLUGIN_ROOT}/../templates/project-state-templates.md`. Pre-fill discovered commands — replace TODO placeholders with actual values.

**Gate**: All analysis sub-agents complete


### 3. Requirements Discovery

Analyze the codebase to reverse-engineer a discovered requirements document. This is a **synthesis** task – use `model: "sonnet"`.

Spawn a sub-agent to analyze:

#### What the System Does
- User-facing features and workflows (from routes, UI components, API endpoints)
- Admin/operator features (from admin routes, CLI commands, dashboards)
- Background processes (cron jobs, workers, event handlers)
- _Monorepo_: attribute features to the sub-project they belong to

#### Implicit Requirements
- Validation rules (from form validators, API input checks, DB constraints)
- Business logic (from service layers, domain models, state machines)
- Access control (from auth middleware, permission checks, role gates)
- Data integrity rules (from DB constraints, unique indexes, foreign keys)

#### External Dependencies
- Third-party API contracts (from API clients, webhook handlers)
- Infrastructure requirements (from Docker configs, deploy scripts)
- Environment requirements (from .env files, config loaders)

#### Non-Functional Characteristics
- Caching patterns (from cache setup, TTL configs)
- Rate limiting (from middleware, API configs)
- Error handling and recovery patterns
- Logging and observability setup
- Performance optimizations present

Output: `OUTPUT_DIR/requirements-discovered.md` in a format compatible with `andthen:plan` input:

```markdown
# Discovered Requirements: [Project Name]

> **Generated by**: `andthen:map-codebase` on [date]
> **Source**: Reverse-engineered from codebase analysis
> **Status**: Discovered – requires validation by team

## System Overview
[What the system does, who uses it, key workflows]

## Discovered Features
### [Feature Area 1]
- **REQ-D01**: [Discovered requirement description]
  - Evidence: [file paths / code patterns that indicate this]
  - Confidence: High/Medium/Low

### [Feature Area 2]
...

## Implicit Business Rules
- **RULE-D01**: [Business rule discovered in code]
  - Evidence: [where this is enforced]

## External Integration Contracts
- **INT-D01**: [External system/API]
  - Contract: [what the code expects from this integration]

## Non-Functional Characteristics
- [Performance, caching, security patterns observed]

## Gaps & Uncertainties
- [Areas where intent is unclear from code alone]
- [Potential missing requirements]
- [Inconsistencies between different parts of the system]
```

**Gate**: Requirements discovery complete


### 4. Output Summary

1. Write all documents to `OUTPUT_DIR/`
2. Print summary listing all generated files with brief descriptions
3. **Monorepo: Generate per-sub-project CLAUDE.md files**
   If `IS_MONOREPO = true`, generate a lightweight `CLAUDE.md` for each discovered sub-project (if one doesn't already exist). Each should contain:
   - Sub-project name and brief description (inferred from package config, README, or code)
   - Key development commands for that sub-project (inline table format)
   - Sub-project-specific conventions or notes that differ from the root

   Keep these files short (under ~40 lines). They supplement the root CLAUDE.md.
4. Suggest next steps:
   - Review discovered requirements with the team
   - Run the `andthen:plan` skill: `/andthen:plan docs/requirements-discovered.md` (or `$andthen:plan ...`)
   - Fill in gaps identified in the discovery document


## OUTPUT

```
OUTPUT_DIR/
├── STACK.md                              # Technology stack
├── ARCHITECTURE.md                       # System architecture + testing overview
├── KEY_DEVELOPMENT_COMMANDS.md            # Discovered dev commands
└── requirements-discovered.md            # Reverse-engineered requirements

Additionally:
- A `## Conventions` section is appended to the project's `CLAUDE.md`
- (Monorepo) Per-sub-project `CLAUDE.md` files are generated in each sub-project directory
```

When complete, print each output file's **relative path from the project root**.
