# AndThen – Structured Workflows for Agentic Development

This file provides guidance to AI coding agents when working with code in this project.


---


## Project Overview

AndThen is an opinionated workflow system for AI coding agents. It provides structured skills that guide development through disciplined pipelines – from requirements discovery through implementation to review. See `plugin/README.md` for the full workflow overview and skill reference.

Core artifacts are the **Feature Implementation Specification (FIS)** for single features and the **PRD + Implementation Plan** (story breakdown) for multi-feature work. Detailed FIS specs are created just-in-time per story during plan execution.

**Structure:**
- `plugin/` – Claude Code plugin (skills, agents, references)
- `hooks/` – Claude Code hooks (blocked commands, notification scripts)
- `scripts/` – Installation and setup scripts
- `docs/` – Guidelines and reference documentation used by workflow skills
- `docs/temp/research/` – Research outputs (worktree strategies, skill analysis, etc.)
- `templates/` – Starter templates for user projects
- `skills` → symlink to `plugin/skills/` (for Codex/agent discovery)


---


## Skill Invocation

Skills are invoked as `/andthen:<skill>` (e.g. `/andthen:spec`, `/andthen:plan`). Agents use the same `andthen:<name>` namespace. When skills are exported for other agents via `scripts/install-skills.sh`, references are rewritten to the portable `andthen-` prefix (hyphen, not dot – required for Codex CLI `$` sigil parser compatibility).


---


## How Skills Work

### Project Context Discovery
Skills read the **user's project** `CLAUDE.md` (not this repo's) for two key integration points:
- **Project Document Index** – a table mapping document types to file paths (specs, plans, ADRs, etc.). Skills use this to determine where to read/write output. See `templates/CLAUDE.template.md` for the table format
- **Workflow Rules, Guardrails and Guidelines** – behavioral rules and development standards that skills load before starting work (e.g. rules files, development/architecture/UI guidelines)

### Skill Anatomy
Each skill lives in `plugin/skills/<name>/` and contains:
- `SKILL.md` – the skill prompt (with frontmatter: `description`, `argument-hint`, and optional `user-invocable`, `context`, `agent`)
- `agents/openai.yaml` – OpenAI/Codex agent metadata for cross-agent portability
- Optional subdirectories for templates, checklists, or references

### Shared References
`plugin/references/` contains reusable reference documents loaded by multiple skills (e.g. `design-tree.md` used by `clarify`, `plan`, and `trade-off`). When skills are exported via `scripts/install-skills.sh`, reference paths are rewritten to resolve correctly outside this repo.

### External Plugin Dependencies (Optional)
Some skills delegate to other Claude Code plugins when available:
- `code-simplifier:code-simplifier` – used by `refactor`, `exec-spec`, `quick-implement` for code cleanup
- `frontend-design` – used by `wireframes` (via `ui-ux-designer` agent) for design implementation

Skills work without these plugins but skip the corresponding steps.


---


## Workflow Rules, Guardrails and Guidelines

### Foundational Rules and Guardrails
_Always fully understand and adhere to the "CRITICAL RULES and GUARDRAILS in this environment" (part of system prompt) before doing any work_.


### Foundational Development Guidelines and Standards
Always fully read relevant guidelines below as needed, based on the type of work being done:
- _`docs/guidelines/DEVELOPMENT-ARCHITECTURE-GUIDELINES.md`_ when doing development work (coding, architecture, etc.)
- _`docs/guidelines/UX-UI-GUIDELINES.md`_ when doing UX/UI related work
- _`docs/guidelines/WEB-DEV-GUIDELINES.md`_ when doing web development work


---


## Vital Documentation Resources

**IMPORTANT**: When lookup of documentation (such as API documentation, user guides, language references, etc.) is needed, or when user asks to lookup documentation directly, _always_ execute the documentation lookup in a separate background sub task (use the _`andthen:documentation-lookup`_ agent). This is **CRITICAL** to reduce the load on the main context window and ensure that the main agent can continue working without interruptions.


---


## Version Bumps

When bumping the version, **always** update both:
- `CHANGELOG.md` – add new version entry
- `.claude-plugin/marketplace.json` – update the `"version"` field


---


## Useful Tools and MCP Servers

### Command line file search and code exploration tools
- **ripgrep (rg)**: Fast recursive search. Example: `rg "createServerSupabaseClient"`. _Use instead of grep_ for better search performance.
- **ast-grep**: Search by AST node types. Example: `ast-grep 'import { $X } from "supabase"' routes/`
- **tree**: Directory structure visualization. Example: `tree -L 2 routes/`

### Context7 MCP - Library and Framework Documentation Lookup (https://github.com/upstash/context7)
Context7 MCP pulls up-to-date, version-specific documentation and code examples straight from the source.
**Only** use Context7 MCP via the _`andthen:documentation-lookup`_ sub-agent for documentation retrieval tasks.

### Fetch (https://github.com/modelcontextprotocol/servers/tree/main/src/fetch)
Retrieves and processes content from web pages, converting HTML to markdown for easier consumption.
**Only** use Fetch MCP via the _`andthen:documentation-lookup`_ sub-agent for documentation retrieval tasks.
