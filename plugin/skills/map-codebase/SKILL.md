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
- **Read project learnings** – If `LEARNINGS.md` exists (check Project Document Index for location), read it before starting
- **Read-only analysis** – No code changes, commits, or modifications
- **Delegate heavily** – Spawn parallel sub-agents for codebase analysis
- **Structured output** – All documents follow templates from `${CLAUDE_PLUGIN_ROOT}/../templates/project-state-templates.md`
- **Discovery, not invention** – Document what exists, don't prescribe what should exist


## GOTCHAS
- Producing a surface-level summary instead of deep structural analysis
- Missing implicit conventions that aren't documented but are visible in code patterns


## WORKFLOW

### 1. Codebase Survey

1. Run `tree -d -L 3` for directory structure
2. Run `git ls-files | head -500` for file inventory
3. Check existing documentation: README, CLAUDE.md, docs/, etc.
4. Identify primary language(s) and frameworks from config files
5. Check git history: `git log --oneline -20`
6. **Detect monorepo/workspace structure** – look for `pnpm-workspace.yaml`, `lerna.json`, `nx.json`, `turbo.json`, `"workspaces"` in root `package.json`, `[workspace]` in root `Cargo.toml`, `go.work`, or multiple sub-dirs with their own package config. If detected: list workspace tool and sub-projects. Set `IS_MONOREPO = true` and pass the sub-project list to all analysis sub-agents.

**Gate**: Project shape understood, technologies identified, monorepo status determined


### 2. Parallel Analysis

Spawn parallel sub-agents _(if supported by your coding agent)_. Use a fast/lightweight model (`model: "haiku"`, `gpt-5.4-mini`, or similar) for scanning agents and a capable coding model (`model: "sonnet"`, `gpt-5.3-codex`, or similar) for synthesis.

**Monorepo note** (apply to all sub-agents when `IS_MONOREPO = true`): organize findings with clear sub-project boundaries. Document shared aspects once; only call out per-sub-project specifics where they differ.

#### 2a. Stack Analysis (sub-agent)
Analyze and document languages/versions, frameworks and libraries (with versions from lock files), infrastructure, external services, build tools and CI/CD.
Output: `OUTPUT_DIR/STACK.md`

#### 2b. Architecture Analysis (sub-agent)
Analyze and document system design and component boundaries, key modules and responsibilities, data flow, entry points (routes, CLI, event handlers), and integration points with external systems. If monorepo: document sub-project boundaries and inter-project relationships.
Output: `OUTPUT_DIR/ARCHITECTURE.md`

#### 2c. Conventions Analysis (sub-agent)
Analyze and document naming conventions, file organization patterns, error handling, logging, testing patterns, and code style (formatting, imports, exports).
Output: a `## Conventions` section to be appended to the project's `CLAUDE.md`

#### 2d. Testing Overview (sub-agent)
Analyze test framework(s), test directory structure, coverage patterns, test helpers/fixtures, and integration/E2E setup.
Output: included in ARCHITECTURE.md under a "Testing" section

#### 2e. Key Development Commands Discovery (sub-agent)
Discover commands by scanning `package.json` scripts, `Makefile`, `Taskfile.yml`, `justfile`, `deno.json`, `Cargo.toml` aliases, CI/CD configs, and README files. If monorepo: organize commands per sub-project and identify root-level orchestration commands.
Output: `docs/KEY_DEVELOPMENT_COMMANDS.md` (or location from Project Document Index), using the template from `${CLAUDE_PLUGIN_ROOT}/../templates/project-state-templates.md`

**Gate**: All analysis sub-agents complete


### 3. Requirements Discovery

Spawn a sub-agent (capable coding model) to reverse-engineer a discovered requirements document by analyzing:

- **What the System Does**: user-facing features/workflows (routes, UI, API), admin/operator features, background processes
- **Implicit Requirements**: validation rules, business logic, access control, data integrity rules
- **External Dependencies**: third-party API contracts, infrastructure requirements, environment requirements
- **Non-Functional Characteristics**: caching, rate limiting, error handling, logging, performance optimizations

Output: `OUTPUT_DIR/requirements-discovered.md` in a format compatible with `andthen:plan` input:

```markdown
# Discovered Requirements: [Project Name]

> **Generated by**: `andthen:map-codebase` on [date]
> **Source**: Reverse-engineered from codebase analysis
> **Status**: Discovered – requires validation by team

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

**Gate**: Requirements discovery complete


### 4. Output Summary

1. Write all documents to `OUTPUT_DIR/`
2. Print summary listing all generated files with brief descriptions
3. If `IS_MONOREPO = true`: generate a lightweight `CLAUDE.md` for each sub-project that doesn't already have one (under ~40 lines: name/description, key development commands inline table, sub-project-specific notes)
4. Suggest next steps: review discovered requirements with team, run `andthen:plan docs/requirements-discovered.md`


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
