---
description: Set up the AndThen workflow structure – new projects, partial setups, and brownfield codebases. Trigger on 'set up AndThen', 'initialize the workflow', 'bootstrap AndThen'.
argument-hint: "[project name or path]"
---

# Initialize Project


## VARIABLES

PROJECT_NAME: $ARGUMENTS _(optional – inferred from directory name or package config if not provided)_


## INSTRUCTIONS

- **Non-destructive** – Never overwrite existing files. Only add missing pieces.
- **Interactive** – Ask before creating optional documents. Don't assume what the user wants.
- **Minimal by default** – Create only what's needed. Suggest optional additions.
- **Detect, don't guess** – classify state from existing files (Step 1) before proposing changes.


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

Generate the root agent instruction file(s) using `templates/CLAUDE.template.md` as the base. A single-tool target gets one full file: `CLAUDE.md` for Claude Code, `AGENTS.md` for Codex/generic agents. When both tools are in play or the target is unclear, `AGENTS.md` carries the full template content and `CLAUDE.md` is a thin import – `@AGENTS.md` as the first line, Claude-specific additions (if any) below it under a `## Claude Code` heading. Claude Code expands the import at session start; Codex never reads `CLAUDE.md`, so the `@` sigil is safe there, and shared content has exactly one authored home. Fill in the Project Overview section; keep the Project Document Index and Project-Specific Guidelines and Rules sections intact; remove TODO comments from filled sections.

Create base directory structure:
```
docs/
├── specs/
└── guidelines/
```

Gitignore hygiene: append entries for the `State (local)` path (default `docs/STATE.local.md`) and the agent workspace (`.agent_temp/`) to `.gitignore` idempotently (only if absent); create `.gitignore` if missing.

Copy `CRITICAL-RULES-AND-GUARDRAILS.md` from `templates/guidelines/` to `docs/guidelines/` if missing as part of baseline setup – the template's Foundational Rules section documents wiring options (commented) that point at it; the user-level wiring itself is offered in Step 3. Never overwrite existing guideline files; preserve project-specific files.

Scaffold the **Core orientation stubs by default** – the documents every project benefits from agents being able to find: `Product` (docs/PRODUCT.md), `Architecture` (docs/ARCHITECTURE.md), `Stack` (docs/STACK.md), `Key Dev Commands` (docs/KEY_DEVELOPMENT_COMMANDS.md), `Decisions` (docs/DECISIONS.md), `Learnings` (docs/LEARNINGS.md). Create these from the templates in `${CLAUDE_PLUGIN_ROOT}/references/project-state-templates.md` without prompting; pre-fill what's auto-detectable (e.g., the `Stack` document from package config). The `andthen:architecture` skill in `--mode trade-off` auto-registers accepted ADRs into the `Decisions` stub. The user can fill these in later, or generate richer content via skills like `andthen:map-codebase` (Architecture/Stack) or `andthen:prd` (Product).

Then settle the **issue-tracker backend** – where agent workflows (triage, PRD/plan issue publishing) read and publish issues. **STOP and WAIT** for the answer:

Ask: _"Where should agent workflows read and publish issues?"_ Recommend **GitHub** when a GitHub remote is detected, otherwise **none (local plan artifacts)**; offer a third option: any other backend, named, with a free-form description of how its operations map.
- **GitHub** or **another named backend** → create `docs/ISSUE-TRACKER.md` from the `ISSUE-TRACKER.md` template (set `Backend:`; for a non-GitHub backend complete the Operation Table from the user's description).
- **none** → create no file; the `Issue Tracker` Index row stays as a dormant location declaration – it names where a tracker config would live if one is ever added, and Tracker resolution treats the absent file as today's on-demand GitHub default (same as the always-present State/Stack rows shipping before their files exist).

**Gate**: Tracker backend chosen (file created only for GitHub/other; Index row always present)

Then present the **optional documents**, recommendation-first. **STOP and WAIT** for the user's selection before creating any of these:

- **Planning** (optional): `State` (docs/STATE.md), `Product Backlog` (docs/PRODUCT-BACKLOG.md), `Roadmap` (docs/ROADMAP.md). When `State` is created, also add the `State (local)` row (`docs/STATE.local.md`) to the Project Document Index – the gitignored, per-developer companion the `andthen:ops` skill auto-creates for session-local notes. Do not create the local file itself (ops owns that); just register the row (its gitignore entry already landed with the base structure).
- **Domain** (optional): `Ubiquitous Language` document (or generate later via the `andthen:ubiquitous-language` skill) and `Out of Scope Registry` (docs/OUT-OF-SCOPE.md) – the cross-feature registry of rejected concepts.
- **Monorepo** (if `IS_MONOREPO = true`): offer per-sub-project agent instruction files matching the root file choice

Lead with a recommendation drawn from what Step 2a detected, and let the user reply **"default"** to accept it: `State` earns its place on nearly every project; add `Roadmap` when the intent spans multiple features or phases; add `Ubiquitous Language` and the `Out of Scope Registry` for domain-heavy work. State the recommendation, then ask: _"Which optional documents would you like to create alongside the Core stubs? Reply 'default' to accept the recommendation, name specific documents (e.g. 'State, Roadmap'), 'all planning', or 'none for now'."_

For each confirmed document type, generate the file from templates in `${CLAUDE_PLUGIN_ROOT}/references/project-state-templates.md`, using the location from the **Project Document Index** or the default path above.

For each confirmed sub-project agent instruction file, generate a lightweight file (under ~40 lines) containing: sub-project name and description, key development commands (inline table), and any conventions that differ from root. Mirror the root file choice (`CLAUDE.md`, `AGENTS.md`, or both – both uses the same thin-import pattern; `@` paths resolve relative to the importing file, so the sub-project `CLAUDE.md` imports its sibling `AGENTS.md`). Also update the root `Key Dev Commands` document (see **Project Document Index**) if created to include per-sub-project sections.

**Gate**: Agent instruction file(s), required starter guidelines, and selected documents generated – then Step 3.


### 2b. Partial Setup (CLAUDE.md and/or AGENTS.md exists)

Read the existing root agent instruction file(s) and check for: Project Document Index (table present? which rows exist?), Project-Specific Guidelines and Rules section, Project Overview filled in, the Core orientation stubs (`PRODUCT.md`, `ARCHITECTURE.md`, `STACK.md`, `KEY_DEVELOPMENT_COMMANDS.md`, `DECISIONS.md`, `LEARNINGS.md` – same set Step 2a scaffolds by default), and referenced documents that actually exist. If both `CLAUDE.md` and `AGENTS.md` exist with duplicated content, offer conversion to the thin-import layout (Step 2a): merge any CLAUDE.md-only content into `AGENTS.md`, then rewrite `CLAUDE.md` to `@AGENTS.md` plus a `## Claude Code` section for genuinely Claude-specific instructions – on confirm only; if declined, apply repairs to both keeping shared sections aligned. If only one exists, repair that file and offer the missing counterpart for cross-agent portability: existing `AGENTS.md` → a thin `CLAUDE.md` import; existing `CLAUDE.md` only → promote it (`git mv CLAUDE.md AGENTS.md`, preserving blame) and create the thin `CLAUDE.md` import.

Present findings and offer fixes. **Missing Core orientation stubs and gitignore hygiene are applied by default** (consistent with Step 2a) – not listed as optional. Planning / Domain / Monorepo docs, the issue-tracker backend, and the optional Index rows (`Context Map`, `Out of Scope Registry`) are offered interactively – never added by default.

```
Current setup analysis:

✓ CLAUDE.md / AGENTS.md exists
✓ Project Document Index present
  - 9/13 document types configured
  - Missing: State, Requirements, Roadmap, Conventions
✓ Project-Specific Guidelines and Rules section configured
✗ CRITICAL-RULES-AND-GUARDRAILS.md is missing from docs/guidelines/
✗ Core orientation stubs missing: PRODUCT.md, ARCHITECTURE.md, DECISIONS.md, LEARNINGS.md
✗ User-level always-loaded rules not wired for ~/.claude (see Step 3)

Would you also like to:
1. Add missing Document Index rows
2. Create missing referenced documents (optional ones)
3. All of the above
```

If the `Architecture` document, the `Stack` document, or a Conventions section in the root agent instruction file(s) are missing and the codebase has 20+ files, also suggest:
```
Missing architecture/stack/conventions documentation detected.
Run the `andthen:map-codebase` skill to auto-generate from codebase analysis? (recommended)
```

Wait for user response, then execute confirmed actions:
- **Missing Core orientation stubs** (default): scaffold per Step 2a.
- **Gitignore hygiene** (default): apply per Step 2a.
- **Issue-tracker backend**: ask the same tracker question as Step 2a; on GitHub/other create the `Issue Tracker` document (path per its Index row, default `docs/ISSUE-TRACKER.md`) from template only when it does not already exist – leave an existing valid file untouched (Non-destructive rule), though a malformed one (a missing or unparseable `Backend:` line – the `BLOCKED: issue-tracker backend unspecified` state) may be repaired interactively here on confirmation. The `Issue Tracker` row is always present (add it if an older file lacks it); a declined tracker leaves the row as a dormant location declaration, so don't re-litigate the absent tracker file as a missing referenced document to create.
- **New optional Index rows** (`Context Map`, `Out of Scope Registry`): append the row only when confirmed. Create the `Out of Scope Registry` file from template with its row; the Context Map file is written later by the `andthen:architecture` skill in `--mode strategic-design`, so add its row without a file.
- **Missing Index rows**: Append to existing table (don't rewrite the whole table). The `Architecture Model` and `Domain Model` rows are always present (add them if an older file lacks them); their JSON is written later by the `andthen:map-codebase` skill with `--model` and the `andthen:ubiquitous-language` skill with `--model` respectively, so the rows are location declarations, not missing referenced documents to create.
- **Missing documents**: Generate from templates, pre-fill where possible
- **Missing guidelines**: Copy `CRITICAL-RULES-AND-GUARDRAILS.md` from `templates/guidelines/` if missing; never overwrite existing files
- **Missing sections**: Add to the root agent instruction file(s) at the appropriate location (in the thin-import layout, sections belong in `AGENTS.md`, never the thin `CLAUDE.md`). If this adds the template's Foundational Rules section, also copy `CRITICAL-RULES-AND-GUARDRAILS.md` if missing so the section's setup options resolve.
- **map-codebase**: Invoke the `andthen:map-codebase` skill; skip creating the `Architecture` and `Stack` documents from templates since map-codebase produces them from actual analysis
- **User-level wiring**: Step 3 – this is how an already-initialized project picks up the always-loaded tiers later.

**Gate**: All selected gaps filled – then Step 3.


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


### 3. Wire the Always-Loaded Tiers (user level, once per machine)

Project files cannot make the foundational rules load in every session – that takes user-level wiring, done once per machine, not per project. Detect first; never re-ask what is already wired.

Hosts: Claude Code at `$CLAUDE_CONFIG_DIR` (default `~/.claude/`) and Codex at `~/.codex/`; consider only directories that exist. Per host, the user-level instruction file is `CLAUDE.md` / `AGENTS.md` in that directory:
- **Rules tier** is wired when that file contains the `# Critical Rules and Guardrails` heading and no `## Working Style` section – that section marks a pre-split copy still carrying the conversation rules, which counts as *stale*, not wired.
- **Conversation tier** is wired when that file contains the `# Response Style` heading (an earlier **rules-only** wiring), or `settings.json` sets `outputStyle` to this plugin's style, or `config.toml` sets `developer_instructions`. An `outputStyle` naming another style is the user's choice – never change it; report it and offer only **rules-only** for the conversation rules.

Everything wired, or no host directory → skip silently. Otherwise name only the missing pieces – for a stale copy: "replace the pre-split Critical Rules section (its heading through the next top-level heading or end of file) with the current guideline" – and **STOP and WAIT**:

_"Wire AndThen's always-loaded rules at user level (once per machine)? **both** (recommended) – engineering and artifact rules into the user-level `CLAUDE.md` / `AGENTS.md`, conversation style into the system prompt (Claude Code output style / Codex `developer_instructions`); **rules-only** – everything, conversation rules included, into the instruction files, no output style; **skip**."_

Execute on confirmation only, per host:
- **Rules tier**: append `templates/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md` verbatim to the instruction file (create it if missing); a stale copy is replaced within the boundary named above. For **rules-only**, also append the body of `templates/output-styles/concise-critical.md` (below its frontmatter) – the full rule set then lives in one tier and nothing is lost.
- **Conversation tier**, Claude Code: the style name follows the install. With the AndThen Claude Code plugin installed (listed in `<config dir>/plugins/installed_plugins.json`, or its cache directory under `<config dir>/plugins/cache/`) the plugin registers it as `<plugin-name>:concise-critical` – `andthen` followed by `:concise-critical` for the stock plugin; otherwise copy the style file to `<config dir>/output-styles/` and use `concise-critical`. Merge `"outputStyle": "<name>"` into `<config dir>/settings.json` (create if missing; preserve every other key). A project-level `outputStyle` (`.claude/settings*.json` in the project) shadows the user-level one – say so when present. Codex: add `developer_instructions = """<style body>"""` to the *top-level* section of `config.toml` (create if missing) – above the first `[table]` header, since keys after one belong to that table; mention `model_verbosity = "low"` as an optional length knob rather than setting it.
- A settings or config file that does not parse is never rewritten – stop and report it. Wiring takes effect in the next session; say so.

**Gate**: User-level wiring applied, declined, or already in place.


### 4. Final Summary

Print a summary listing **only what this run actually created**. Group by Core orientation stubs (always scaffolded by default in 2a/2b), starter guidelines, any optional documents the user confirmed, and user-level wiring. Omit groups that were already in place. Example:

```
Project initialized:

Created:
  CLAUDE.md / AGENTS.md                       – Project configuration
  docs/PRODUCT.md                             – Product vision (stub)
  docs/ARCHITECTURE.md                        – System architecture (stub)
  docs/STACK.md                               – Technology stack (pre-filled from package config)
  docs/KEY_DEVELOPMENT_COMMANDS.md            – Dev / test / build commands (stub)
  docs/DECISIONS.md                           – Decisions registry (stub)
  docs/LEARNINGS.md                           – Defensive knowledge / traps (empty template)
  docs/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md
  [+ any optional documents the user selected, e.g. docs/STATE.md, docs/ROADMAP.md, …]

User-level (once per machine, active from the next session):
  ~/.claude/CLAUDE.md                         – Critical Rules appended
  ~/.claude/settings.json                     – outputStyle set to the plugin's concise-critical style

Next steps:
  1. Review and customize CLAUDE.md / AGENTS.md (especially Project Overview)
  2. Not sure where to start? Use the andthen:now-what skill
     – it inspects state and routes to the right skill (clarify, spec, plan,
     architecture, ui-ux-design, etc.). Pass your idea inline if you have one.
  3. Already know what you need? Jump straight to the andthen:spec, andthen:plan,
     andthen:quick-implement, andthen:architecture, etc. skills.
```


## OUTPUT

Project files are written to the project root and printed as relative paths; user-level wiring (Step 3) is printed with `~`.
