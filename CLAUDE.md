# AndThen — Structured Workflows for Agentic Development

This file provides guidance to AI coding agents when working with code in this project.


---


## Project Overview

AndThen is an opinionated workflow system for AI coding agents. It provides structured commands that guide development through a disciplined pipeline: clarify → spec → plan → execute → review.

The core artifact is the **Feature Implementation Specification (FIS)** — a comprehensive blueprint that enables reliable, autonomous implementation.

**Structure:**
- `plugin/` — Claude Code plugin (commands, agents, skills)
- `docs/` — Guidelines and reference documentation used by workflow commands
- `templates/` — Starter templates for user projects


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


## Commands & Skills

All workflow commands are **unified** — a single set of files works across Claude Code, Codex CLI, Aider, Cursor, and other agents. Commands use capability detection to delegate to sub-agents when available and fall back to direct execution when not.

### Available Commands

| Command | Purpose |
|---------|---------|
| `clarify` | Requirements discovery — from vague idea to structured requirements |
| `spec` | Clarify requirements and generate Feature Implementation Specification |
| `exec-spec` | Execute a FIS — orchestrated implementation with validation |
| `review` | Gap analysis, code review, or document review |
| `plan` | Requirements discovery + PRD creation (if needed) + story breakdown |
| `exec-plan` | Execute plan via Agent Team pipeline |
| `trade-off` | Architecture decision research |

Specialized commands in `extras/`: `quick-implement`, `design-system`, `wireframes`, `refactor`, `review-council`, `troubleshoot`


---


## Vital Documentation Resources

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

---
