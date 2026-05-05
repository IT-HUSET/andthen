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

1. **Check for agent instruction files** (`CLAUDE.md` and/or `AGENTS.md`) at project root
2. **Check for docs/ directory** and existing documents
3. **Check for package config** (package.json, Cargo.toml, go.mod, pyproject.toml, deno.json, etc.) to infer project name and tech stack
4. **Check for existing guidelines** in docs/guidelines/ or similar
5. **Detect monorepo/workspace structure** – look for `pnpm-workspace.yaml`, `lerna.json`, `nx.json`, `turbo.json`, `"workspaces"` in root `package.json`, `[workspace]` in root `Cargo.toml`, `go.work`, or multiple sub-dirs with their own package config. If detected, note the workspace tool, list sub-projects, and set `IS_MONOREPO = true`.

Classify into one of three paths:

| State | Indicators | Path |
|-------|-----------|------|
| **New project** | No CLAUDE.md or AGENTS.md, minimal or no docs/ | → Step 2a |
| **Partial setup** | CLAUDE.md and/or AGENTS.md exists but missing sections or document types | → Step 2b |
| **Brownfield** | Substantial codebase but no agent instruction file or workflow structure | → Step 2c |

**Gate**: Project state classified


### 2a. New Project Setup

Ask the user for basic project context (or accept from `PROJECT_NAME`): project name, brief description, primary tech stack (if not auto-detected).

Generate the root agent instruction file(s) using `templates/CLAUDE.template.md` as the base. Create `CLAUDE.md` for Claude Code, `AGENTS.md` for Codex/generic agents, and both when the target agent is unclear. Fill in the Project Overview section; keep the Project Document Index and Workflow Rules sections intact; remove TODO comments from filled sections. When creating both files, keep the shared workflow sections byte-equivalent so agents read the same document contract.

Create base directory structure:
```
docs/
├── specs/
└── guidelines/
```

Because the generated root agent instruction template references the starter guideline filenames directly, copy any missing files from `templates/guidelines/` into `docs/guidelines/` as part of baseline setup. Never overwrite existing guideline files; preserve project-specific files.

Present the following options together. **STOP and WAIT** for the user's selection before creating any optional files:

- **Core** (recommended): `Learnings` (docs/LEARNINGS.md), `Stack` (docs/STACK.md), `Key Dev Commands` (docs/KEY_DEVELOPMENT_COMMANDS.md)
- **Planning**: `State` (docs/STATE.md), `Product Backlog` (docs/PRODUCT-BACKLOG.md), `Roadmap` (docs/ROADMAP.md)
- **Architecture**: `Architecture` document (or generate later via the `andthen:map-codebase` skill)
- **Domain**: `Ubiquitous Language` document (or generate later via the `andthen:ubiquitous-language` skill)
- **Monorepo** (if `IS_MONOREPO = true`): offer per-sub-project agent instruction files matching the root file choice

Ask: _"Which would you like to create? (e.g. 'Learnings, Stack' or 'all core' or 'none for now')"_

For each confirmed document type, generate the file from templates in `${CLAUDE_PLUGIN_ROOT}/references/project-state-templates.md`, using the location from the **Project Document Index** or the default path above. Pre-fill what's auto-detectable (e.g., the `Stack` document from package config).

For each confirmed sub-project agent instruction file, generate a lightweight file (under ~40 lines) containing: sub-project name and description, key development commands (inline table), and any conventions that differ from root. Mirror the root file choice (`CLAUDE.md`, `AGENTS.md`, or both). Also update the root `Key Dev Commands` document (see **Project Document Index**) if created to include per-sub-project sections.

**Gate**: Agent instruction file(s), required starter guidelines, and selected documents generated


### 2b. Partial Setup (CLAUDE.md and/or AGENTS.md exists)

Read the existing root agent instruction file(s) and check for: Project Document Index (table present? which rows exist?), Workflow Rules section, Project Overview filled in, and referenced documents that actually exist. If both `CLAUDE.md` and `AGENTS.md` exist, check both and keep shared workflow sections aligned. If only one exists, repair that file and offer to create the missing counterpart for cross-agent portability.

Present findings and offer fixes:
```
Current setup analysis:

✓ CLAUDE.md / AGENTS.md exists
✓ Project Document Index present
  - 8/13 document types configured
  - Missing: State, Requirements, Roadmap, Learnings, Conventions
✓ Workflow Rules section configured
✗ Required starter guideline files are missing from docs/guidelines/
✗ `Learnings` document is listed in the **Project Document Index** but the file doesn't exist

Would you like to:
1. Add missing Document Index rows
2. Create missing referenced documents
3. Copy missing starter guidelines
4. All of the above
```

If the `Architecture` document, the `Stack` document, or a Conventions section in the root agent instruction file(s) are missing and the codebase has 20+ files, also suggest:
```
Missing architecture/stack/conventions documentation detected.
Run the `andthen:map-codebase` skill to auto-generate from codebase analysis? (recommended)
```

Wait for user response, then execute confirmed actions:
- **Missing Index rows**: Append to existing table (don't rewrite the whole table)
- **Missing documents**: Generate from templates, pre-fill where possible
- **Missing guidelines**: Copy any missing starter guideline files referenced by the generated template from `templates/guidelines/`; never overwrite existing files
- **Missing sections**: Add to the root agent instruction file(s) at the appropriate location. If this adds the template's Workflow Rules section or creates a missing counterpart file from the template, also copy any missing starter guideline files so the new references resolve.
- **map-codebase**: Invoke the `andthen:map-codebase` skill; skip creating the `Architecture` and `Stack` documents from templates since map-codebase produces them from actual analysis

**Gate**: All selected gaps filled


### 2c. Brownfield Setup (existing codebase, no workflow structure)

Inform the user:
```
Existing codebase detected without AndThen workflow structure.

Recommended approach:
1. Invoke the `andthen:map-codebase` skill to auto-generate the `Architecture` document and the `Stack` document (see **Project Document Index**) plus conventions for the root agent instruction file(s)
2. Then set up the agent instruction file(s) and remaining structure

Invoke the `andthen:map-codebase` skill first? (recommended for codebases with 20+ files)
```

Wait for response. If yes: invoke the `andthen:map-codebase` skill, then proceed with Step 2a using generated documents as foundation (skip the `Architecture` and `Stack` documents from templates). If no: proceed directly to Step 2a.

**Gate**: Brownfield analysis complete (or skipped), proceed to project setup


### 3. Final Summary

Print a summary of everything created:

```
Project initialized:

Created:
  CLAUDE.md / AGENTS.md                  – Project configuration
  [Learnings document path]             – Project knowledge (empty)
  [Stack document path]                 – Technology stack (pre-filled)
  docs/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md

Next steps:
  1. Review and customize CLAUDE.md / AGENTS.md (especially Project Overview)
  2. Not sure where to start? Run /andthen:now-what (or $andthen:now-what)
     — it inspects state and routes to the right skill (clarify, spec, plan,
     architecture, ui-ux-design, etc.). Pass your idea inline if you have one.
  3. Already know what you need? Jump straight to /andthen:spec, /andthen:plan,
     /andthen:quick-implement, /andthen:architecture, etc.
```


## OUTPUT

All files are written to the project root. Print relative paths only.
