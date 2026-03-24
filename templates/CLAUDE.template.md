# [Project Name]

> AI coding agent instructions. This file tells agents where things are and how to work in this project.


---


## Project Overview

<!-- TODO: Describe your project – what it does, who it's for, key architectural patterns.
     This section is your "steering context" – agents read it before every task. -->

_**TODO**: Add Project Overview, Architecture, Tech Stack, Structure etc. here._


---


## Project Document Index

<!-- These paths tell AndThen (https://github.com/IT-HUSET/andthen) workflow commands (clarify, spec, plan, trade-off, etc.)
     where your project keeps its documents. Adjust to match your project structure.
     Remove rows you don't use. Paths are relative to repository root. -->

| Document Type        | Location                            | Notes                                   |
|----------------------|-------------------------------------|-----------------------------------------|
| Product              | `docs/PRODUCT.md`                   | Product vision and high-level roadmap, requirements backlog etc   |
| Product Backlog      | `docs/PRODUCT-BACKLOG.md`           | Product backlog for future work (REQ-IDs) |
| Roadmap              | `docs/ROADMAP.md`                   | Phase structure with success criteria   |
| Specs & Plans        | `docs/specs/<version-or-feature>/`  | PRDs, implementation plans, FIS, story breakdowns &dagger; |
| ADRs                 | `docs/adrs/`                        | Architecture Decision Records           |
| Research             | `docs/research/`                    | Trade-off analysis output               |
| Architecture         | `docs/ARCHITECTURE.md`              | System architecture overview            |
| Stack                | `docs/STACK.md`                     | Technology stack documentation          |
| Ubiquitous Language  | `docs/UBIQUITOUS_LANGUAGE.md`       | Domain glossary – canonical terms, definitions, synonyms to avoid |
| Guidelines           | `docs/guidelines/`                  | Development guidelines                  |
| Wireframes           | `docs/wireframes/`                  | UI wireframes (HTML or images)          |
| Design System        | `docs/design-system/`               | Tokens, components, style guide         |
| Diagram Style Guide  | `docs/design/diagram-style-guide.md` | Excalidraw diagram visual style (colors, fills, typography) |
| State                | `docs/STATE.md`                     | Cross-session state tracking (current phase, progress, blockers) |
| Learnings            | `docs/LEARNINGS.md`                 | Accumulated project knowledge and error patterns |
| Tech Debt            | `docs/TECH-DEBT-BACKLOG.md`         | Known technical debt                    |
| Changelog            | `CHANGELOG.md`                      | Release history                         |
| Agent Temp           | `.agent_temp/`                      | Temporary agent workspace (reviews, research, QA) |

&dagger; Organized by version or feature name: `docs/specs/{version-or-feature}/prd.md`, `plan.md`, `fis/`. Standalone specs go directly in `docs/specs/`.

<!-- Workflow commands read this table to determine where to write output.
     If a location isn't specified, commands use the defaults shown above.
     The State–Stack rows are optional. Starter templates for these documents
     are in the AndThen repo at templates/project-state-templates.md.
     You can also generate Architecture, Conventions, and Stack docs
     automatically using /andthen:map-codebase. -->


---


## Workflow Rules, Guardrails and Guidelines

### Foundational Rules and Guardrails
_Always fully read and understand this file before doing any work:_ @docs/rules/CRITICAL-RULES-AND-GUARDRAILS.md

> **Alternative (stronger adherence):** Instead of the `@` reference above, you can inject the rules
> directly into the system prompt via a shell alias. This keeps the rules in a privileged position
> that survives long sessions without drift.


### Foundational Development Guidelines and Standards
**Always read** relevant guidelines below as _needed_, based on the type of work being done. Review what guidelines are relevant to the task at hand before starting any work that involves coding, code exploration, architecture and solution design, UX/UI, code review, etc.

- _`<repository_root>/docs/guidelines/DEVELOPMENT-ARCHITECTURE-GUIDELINES.md`_ when doing development work (coding, architecture, etc.)
- _`<repository_root>/docs/guidelines/UX-UI-GUIDELINES.md`_ when doing UX/UI related work
- _`<repository_root>/docs/guidelines/WEB-DEV-GUIDELINES.md`_ when doing web development work


---


## Project-Specific Guidelines
<!-- Add references to project-specific guidelines here (don't @ them, just list the paths) -->


## Visual Validation Workflow
<!-- Describe any project-specific visual validation workflow here, or reference documentation files -->


---


## Vital Documentation Resources
<!-- Add references to other important documentation files here (don't @ them, just list the paths) -->

**IMPORTANT**: When lookup of documentation (such as API documentation, user guides, language references, etc.) is needed, or when user asks to lookup documentation directly, _always_ execute the documentation lookup in a separate background sub task (use the _`andthen:documentation-lookup`_ agent). This is **CRITICAL** to reduce the load on the main context window and ensure that the main agent can continue working without interruptions.


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

### Code Analysis and Style (Analysis, Linting and Formatting)

**Automatically use the IDE's built-in diagnostics tool to check for analysis, linting and type errors:**
- Run `mcp__ide_getDiagnostics` to check all files for diagnostics
- Fix any linting or type errors before considering the task complete
- Do this for any file you create or modify

### Tools and MCP Servers for visual validation and UI testing/exploration

#### Agent Browser (`https://github.com/vercel-labs/agent-browser`)

Use `agent-browser` for web automation and quick and efficient visual validation.

Run `agent-browser --help` for all commands.
Core workflow:
1. `agent-browser open <url>` - Navigate to page
2. `agent-browser snapshot -i` - Get interactive elements with refs (@e1, @e2)
3. `agent-browser click @e1` / `fill @e2 "text"` - Interact using refs
4. Re-snapshot after page changes

See also this skill: `agent-browser`

#### Chrome DevTools MCP (`https://github.com/ChromeDevTools/chrome-devtools-mcp`)
Use the `chrome-devtools` for deeper visual validation and UI testing/exploration, as well as debugging, analysis/execution of JavaScript etc.

See also this skill: `chrome-devtools`


---


## Key Development Commands

See `<repository_root>/docs/rules/KEY_DEVELOPMENT_COMMANDS.md` for key commands related to development, running, deployment, testing, formatting, linting, and UI testing.


---


## External Agent Application Delegation Protocol _[TODO: OPTIONAL]_

When requested, delegate specific tasks to multiple AI coding agents (external applications), running each review in **parallel background** `Bash` tool processes to speed up the process while keeping the main agent free to continue working.

### codex CLI
Execute the `codex` command via the `Bash` tool.

```bash
# Example:
codex exec --full-auto --config hide_agent_reasoning="true" "<PROMPT_TEXT>"
```
