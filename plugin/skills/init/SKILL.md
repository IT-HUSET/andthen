---
description: Set up AndThen workflow structure for a project — handles new projects, partial setups, and brownfield codebases
argument-hint: "[project name or path]"
---

# Initialize Project

Set up the AndThen workflow structure for a project. Detects current state and fills gaps non-destructively — never overwrites existing files.


## VARIABLES

PROJECT_NAME: $ARGUMENTS _(optional — inferred from directory name or package config if not provided)_


## INSTRUCTIONS

- **Non-destructive** — Never overwrite existing files. Only add missing pieces.
- **Interactive** — Ask before creating optional documents. Don't assume what the user wants.
- **Minimal by default** — Create only what's needed. Suggest optional additions.
- **Detect, don't guess** — Read existing files to understand what's already in place before proposing changes.


## GOTCHAS
- Overwriting existing project files without checking — non-destructive by design
- Creating files for workflows the user doesn't need


## WORKFLOW

### 1. Detect Current State

Scan the project to determine the setup path:

1. **Check for CLAUDE.md** (or AGENTS.md) at project root
2. **Check for docs/ directory** and existing documents
3. **Check for package config** (package.json, Cargo.toml, go.mod, pyproject.toml, deno.json, etc.) to infer project name and tech stack
4. **Check for existing guidelines** in docs/guidelines/ or similar

Classify into one of three paths:

| State | Indicators | Path |
|-------|-----------|------|
| **New project** | No CLAUDE.md, minimal or no docs/ | → Step 2a |
| **Partial setup** | CLAUDE.md exists but missing sections or document types | → Step 2b |
| **Brownfield** | Substantial codebase but no CLAUDE.md or workflow structure | → Step 2c |

**Gate**: Project state classified


### 2a. New Project Setup

#### Generate CLAUDE.md

Ask the user for basic project context (or accept what's provided in `PROJECT_NAME`):
- Project name
- Brief description (1-2 sentences)
- Primary tech stack (if not auto-detected from package config)

Generate `CLAUDE.md` using `${CLAUDE_PLUGIN_ROOT}/../templates/CLAUDE.template.md` as the base:
- Fill in the Project Overview section with provided context
- Keep the full Project Document Index (users can remove rows they don't need)
- Keep Workflow Rules, Guardrails and Guidelines references intact
- Remove TODO comments and placeholder text from filled sections

#### Create docs/ structure

Create the base directory:
```
docs/
├── specs/
└── guidelines/
```

#### Offer optional starter documents

Present the available document types and ask which to create:

```
Optional project documents (from Project Document Index):

Core (recommended):
  [ ] docs/LEARNINGS.md    — Accumulated project knowledge and error patterns
  [ ] docs/STACK.md        — Technology stack documentation

Planning (when ready):
  [ ] docs/STATE.md        — Cross-session state tracking
  [ ] docs/REQUIREMENTS.md — Requirements with REQ-IDs
  [ ] docs/ROADMAP.md      — Phase structure with success criteria

Architecture (create now or generate later via andthen:map-codebase):
  [ ] docs/ARCHITECTURE.md — System architecture overview

Domain (create starter now or generate later via andthen:ubiquitous-language):
  [ ] docs/UBIQUITOUS_LANGUAGE.md — Domain glossary with canonical terms

Which would you like to create? (e.g. "LEARNINGS, STACK" or "all core" or "none for now")
```

> **CRITICAL**: Present this list and **STOP and WAIT** for user response. Do not create documents without confirmation.

For each selected document, generate from templates in `${CLAUDE_PLUGIN_ROOT}/../templates/project-state-templates.md`. Pre-fill what's auto-detectable (e.g., STACK.md from package config).

#### Offer guidelines

If `docs/guidelines/` is empty:

```
AndThen includes starter guidelines. Copy any that are useful:
  [ ] DEVELOPMENT-ARCHITECTURE-GUIDELINES.md
  [ ] UX-UI-GUIDELINES.md
  [ ] WEB-DEV-GUIDELINES.md
  [ ] CRITICAL-RULES-AND-GUARDRAILS.md

These are starting points — adapt to your project's needs.
```

> **CRITICAL**: **STOP and WAIT** for user response before copying any guidelines.

Copy selected guidelines from the AndThen plugin's guidelines directory.

**Gate**: CLAUDE.md created, selected documents generated


### 2b. Partial Setup (CLAUDE.md exists)

#### Analyze existing setup

Read CLAUDE.md and check for:
- **Project Document Index** — Is the table present? Which rows exist?
- **Workflow Rules section** — Present and properly configured?
- **Project Overview** — Filled in or still placeholder?
- **Referenced documents** — Do the files pointed to by the Document Index actually exist?

#### Report and offer fixes

Present findings:

```
Current setup analysis:

✓ CLAUDE.md exists
✓ Project Document Index present
  - 8/13 document types configured
  - Missing: State, Requirements, Roadmap, Learnings, Conventions
✓ Workflow Rules section configured
✗ docs/guidelines/ is empty (referenced but no files)
✗ docs/LEARNINGS.md referenced but doesn't exist

Would you like to:
1. Add missing Document Index rows
2. Create missing referenced documents
3. Copy starter guidelines
4. All of the above
```

> **CRITICAL**: **STOP and WAIT** for user response. Do not modify CLAUDE.md or create files without confirmation.

For each confirmed action:
- **Missing Index rows**: Append to existing table (don't rewrite the whole table)
- **Missing documents**: Generate from templates, pre-fill where possible
- **Missing guidelines**: Copy from plugin
- **Missing sections**: Add to CLAUDE.md at the appropriate location

**Gate**: All selected gaps filled


### 2c. Brownfield Setup (existing codebase, no workflow structure)

#### Codebase analysis

Inform the user:
```
Existing codebase detected without AndThen workflow structure.

Recommended approach:
1. Run andthen:map-codebase to auto-generate ARCHITECTURE.md, STACK.md, and conventions for CLAUDE.md
2. Then set up CLAUDE.md and remaining structure

Run map-codebase first? (recommended for codebases with 20+ files)
```

> **CRITICAL**: **STOP and WAIT** for user response.

**If yes**: Run `andthen:map-codebase` (or instruct the user to run it), then proceed with Step 2a using the generated documents as a foundation. Skip creating ARCHITECTURE.md and STACK.md since map-codebase already produced them.

**If no**: Proceed directly to Step 2a (standard new project setup). The user can run map-codebase later.

**Gate**: Brownfield analysis complete (or skipped), proceed to project setup


### 3. Final Summary

Print a summary of everything created:

```
Project initialized:

Created:
  CLAUDE.md                              — Project configuration
  docs/LEARNINGS.md                      — Project knowledge (empty)
  docs/STACK.md                          — Technology stack (pre-filled)
  docs/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md

Next steps:
  1. Review and customize CLAUDE.md (especially Project Overview)
  2. Start a feature: andthen:spec "your feature description"
  3. Or plan an MVP:  andthen:plan "your requirements"
```


## OUTPUT

All files are written to the project root. Print relative paths only.
