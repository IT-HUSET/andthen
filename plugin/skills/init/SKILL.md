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

Generate `CLAUDE.md` using `${CLAUDE_PLUGIN_ROOT}/../templates/CLAUDE.template.md` as the base. Fill in the Project Overview section; keep the Project Document Index and Workflow Rules sections intact; remove TODO comments from filled sections.

Create base directory structure:
```
docs/
├── specs/
└── guidelines/
```

Present optional documents and ask which to create:

```
Optional core project document types from the **Project Document Index**:

Core (recommended):
  [ ] `Learnings` document                     – see **Project Document Index**; default: docs/LEARNINGS.md – Accumulated project knowledge and error patterns
  [ ] `Stack` document                         – see **Project Document Index**; default: docs/STACK.md – Technology stack documentation
  [ ] `Key Dev Commands` document              – see **Project Document Index**; default: docs/KEY_DEVELOPMENT_COMMANDS.md – Dev, test, build, deploy commands

Planning (when ready):
  [ ] `State` document                         – see **Project Document Index**; default: docs/STATE.md – Cross-session state tracking
  [ ] `Product Backlog` document               – see **Project Document Index**; default: docs/PRODUCT-BACKLOG.md – Product backlog with REQ-IDs
  [ ] `Roadmap` document                       – see **Project Document Index**; default: docs/ROADMAP.md – Phase structure with success criteria

Architecture (or generate later via the `andthen:map-codebase` skill):
  [ ] `Architecture` document                  – see **Project Document Index**; default: docs/ARCHITECTURE.md – System architecture overview

Domain (or generate later via the `andthen:ubiquitous-language` skill):
  [ ] `Ubiquitous Language` document           – see **Project Document Index**; default: docs/UBIQUITOUS_LANGUAGE.md – Domain glossary

Which would you like to create? (e.g. "Learnings, Stack" or "all core" or "none for now")
```

If `docs/guidelines/` is empty, also offer:
```
AndThen includes starter guidelines. Copy any that are useful:
  [ ] DEVELOPMENT-ARCHITECTURE-GUIDELINES.md
  [ ] UX-UI-GUIDELINES.md
  [ ] WEB-DEV-GUIDELINES.md
  [ ] CRITICAL-RULES-AND-GUARDRAILS.md
```

If `IS_MONOREPO = true`, also offer per-sub-project CLAUDE.md files:
```
Monorepo detected ([workspace tool]: [list of sub-projects]).
Claude Code loads per-directory CLAUDE.md files automatically – each sub-project can have
its own context agents pick up when working in that directory.

Create per-sub-project CLAUDE.md files? (recommended)
  [list of discovered sub-projects]
```

> **CRITICAL**: Present all the above options together and **STOP and WAIT** for user response before creating any files.

For each confirmed document type, generate the file from templates in `${CLAUDE_PLUGIN_ROOT}/../templates/project-state-templates.md`, using the location from the **Project Document Index** or the default path above. Pre-fill what's auto-detectable (e.g., the `Stack` document from package config).

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
  2. Start a feature: /andthen:spec "your feature description"  (or $andthen:spec ...)
  3. Or plan an MVP:  /andthen:plan "your requirements"  (or $andthen:plan ...)
```


## OUTPUT

All files are written to the project root. Print relative paths only.
