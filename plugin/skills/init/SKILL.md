---
description: Set up AndThen workflow structure for a project – handles new projects, partial setups, and brownfield codebases. Trigger on 'set up AndThen', 'initialize the workflow', 'bootstrap this project for AndThen'.
argument-hint: "[project name or path]"
---

# Initialize Project


Set up the AndThen workflow structure for a project. Detects current state and fills gaps non-destructively – never overwrites existing files.


## VARIABLES

PROJECT_NAME: $ARGUMENTS _(optional – inferred from directory name or package config if not provided)_


## INSTRUCTIONS

- **Non-destructive** – Never overwrite existing files. Only add missing pieces.
- **Interactive** – Ask before creating optional documents. Don't assume what the user wants.
- **Minimal by default** – Create only what's needed. Suggest optional additions.
- **Detect, don't guess** – Read existing files to understand what's already in place before proposing changes.


## GOTCHAS
- Overwriting existing project files without checking – non-destructive by design
- Creating files for workflows the user doesn't need


## WORKFLOW

### 1. Detect Current State

Scan the project to determine the setup path:

1. **Check for CLAUDE.md** (or AGENTS.md) at project root
2. **Check for docs/ directory** and existing documents
3. **Check for package config** (package.json, Cargo.toml, go.mod, pyproject.toml, deno.json, etc.) to infer project name and tech stack
4. **Check for existing guidelines** in docs/guidelines/ or similar
5. **Detect monorepo/workspace structure** – look for `pnpm-workspace.yaml`, `lerna.json`, `nx.json`, `turbo.json`, `"workspaces"` in root `package.json`, `[workspace]` in root `Cargo.toml`, `go.work`, or multiple sub-dirs with their own package config. If detected, note the workspace tool, list sub-projects, and set `IS_MONOREPO = true`.

Classify into one of three paths:

| State | Indicators | Path |
|-------|-----------|------|
| **New project** | No CLAUDE.md, minimal or no docs/ | → Step 2a |
| **Partial setup** | CLAUDE.md exists but missing sections or document types | → Step 2b |
| **Brownfield** | Substantial codebase but no CLAUDE.md or workflow structure | → Step 2c |

**Gate**: Project state classified


### 2a. New Project Setup

Ask the user for basic project context (or accept from `PROJECT_NAME`): project name, brief description, primary tech stack (if not auto-detected).

Generate `CLAUDE.md` using `templates/CLAUDE.template.md` as the base. Fill in the Project Overview section; keep the Project Document Index and Workflow Rules sections intact; remove TODO comments from filled sections.

Create base directory structure:
```
docs/
├── specs/
└── guidelines/
```

Present the following options together. **STOP and WAIT** for the user's selection before creating any files:

- **Core** (recommended): `Learnings` (docs/LEARNINGS.md), `Stack` (docs/STACK.md), `Key Dev Commands` (docs/KEY_DEVELOPMENT_COMMANDS.md)
- **Planning**: `State` (docs/STATE.md), `Product Backlog` (docs/PRODUCT-BACKLOG.md), `Roadmap` (docs/ROADMAP.md)
- **Architecture**: `Architecture` document (or generate later via the `andthen:map-codebase` skill)
- **Domain**: `Ubiquitous Language` document (or generate later via the `andthen:ubiquitous-language` skill)
- **Guidelines** (if `docs/guidelines/` is empty): offer the starter guidelines (`DEVELOPMENT-ARCHITECTURE-GUIDELINES.md`, `UX-UI-GUIDELINES.md`, `WEB-DEV-GUIDELINES.md`, `CRITICAL-RULES-AND-GUARDRAILS.md`)
- **Monorepo** (if `IS_MONOREPO = true`): offer per-sub-project `CLAUDE.md` files

Ask: _"Which would you like to create? (e.g. 'Learnings, Stack' or 'all core' or 'none for now')"_

For each confirmed document type, generate the file from templates in `${CLAUDE_PLUGIN_ROOT}/references/project-state-templates.md`, using the location from the **Project Document Index** or the default path above. Pre-fill what's auto-detectable (e.g., the `Stack` document from package config).

For each confirmed sub-project CLAUDE.md, generate a lightweight file (under ~40 lines) containing: sub-project name and description, key development commands (inline table), and any conventions that differ from root. Also update the root `Key Dev Commands` document (see **Project Document Index**) if created to include per-sub-project sections.

**Gate**: CLAUDE.md created, selected documents generated


### 2b. Partial Setup (CLAUDE.md exists)

Read CLAUDE.md and check for: Project Document Index (table present? which rows exist?), Workflow Rules section, Project Overview filled in, and referenced documents that actually exist.

Present findings and offer fixes:
```
Current setup analysis:

✓ CLAUDE.md exists
✓ Project Document Index present
  - 8/13 document types configured
  - Missing: State, Requirements, Roadmap, Learnings, Conventions
✓ Workflow Rules section configured
✗ docs/guidelines/ is empty (referenced but no files)
✗ `Learnings` document is listed in the **Project Document Index** but the file doesn't exist

Would you like to:
1. Add missing Document Index rows
2. Create missing referenced documents
3. Copy starter guidelines
4. All of the above
```

If the `Architecture` document, the `Stack` document, or a Conventions section in CLAUDE.md are missing and the codebase has 20+ files, also suggest:
```
Missing architecture/stack/conventions documentation detected.
Run the `andthen:map-codebase` skill to auto-generate from codebase analysis? (recommended)
```

Wait for user response, then execute confirmed actions:
- **Missing Index rows**: Append to existing table (don't rewrite the whole table)
- **Missing documents**: Generate from templates, pre-fill where possible
- **Missing guidelines**: Copy from plugin
- **Missing sections**: Add to CLAUDE.md at the appropriate location
- **map-codebase**: Invoke the `andthen:map-codebase` skill; skip creating the `Architecture` and `Stack` documents from templates since map-codebase produces them from actual analysis

**Gate**: All selected gaps filled


### 2c. Brownfield Setup (existing codebase, no workflow structure)

Inform the user:
```
Existing codebase detected without AndThen workflow structure.

Recommended approach:
1. Invoke the `andthen:map-codebase` skill to auto-generate the `Architecture` document and the `Stack` document (see **Project Document Index**) plus conventions for CLAUDE.md
2. Then set up CLAUDE.md and remaining structure

Invoke the `andthen:map-codebase` skill first? (recommended for codebases with 20+ files)
```

Wait for response. If yes: invoke the `andthen:map-codebase` skill, then proceed with Step 2a using generated documents as foundation (skip the `Architecture` and `Stack` documents from templates). If no: proceed directly to Step 2a.

**Gate**: Brownfield analysis complete (or skipped), proceed to project setup


### 3. Final Summary

Print a summary of everything created:

```
Project initialized:

Created:
  CLAUDE.md                              – Project configuration
  [Learnings document path]             – Project knowledge (empty)
  [Stack document path]                 – Technology stack (pre-filled)
  docs/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md

Next steps:
  1. Review and customize CLAUDE.md (especially Project Overview)
  2. Not sure where to start? Run /andthen:now-what (or $andthen:now-what)
     — it inspects state and routes to the right skill (clarify, spec, plan,
     architecture, ui-ux-design, etc.). Pass your idea inline if you have one.
  3. Already know what you need? Jump straight to /andthen:spec, /andthen:plan,
     /andthen:quick-implement, /andthen:architecture, etc.
```


## OUTPUT

All files are written to the project root. Print relative paths only.
