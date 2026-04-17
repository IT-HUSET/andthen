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

Skills are invoked as `/andthen:<skill>` (e.g. `/andthen:spec`, `/andthen:plan`). Agents share the `andthen:` *string prefix* but are **not** `/andthen:` invokable — they are spawned via the Task tool with `subagent_type: "andthen:<name>"`. When skills are exported for other agents via `scripts/install-skills.sh`, references are rewritten to the portable `andthen-` prefix (hyphen, not dot – required for Codex CLI `$` sigil parser compatibility). Specifically: `/andthen:<name>` rewrites to `$andthen-<name>` (sigil + separator swap) and bare `andthen:<name>` rewrites to `andthen-<name>`.

### Skills vs Agents — Invariant

**This is a load-bearing distinction. Violating it causes the Task tool to fail with "Agent type not found".**

Skills and agents share the `andthen:` namespace but have different invocation mechanisms and are not interchangeable:

- **Agents** (`plugin/agents/*.md`, 7 total: `build-troubleshooter`, `documentation-lookup`, `qa-test-engineer`, `research-specialist`, `solution-architect`, `ui-ux-designer`, `visual-validation-specialist`) — valid `subagent_type` values for the Task tool. Spawned as real sub-agents.
- **Skills** (`plugin/skills/*/`) — invoked via `/andthen:<name>` slash command or the Skill tool. **Not valid `subagent_type` values.**

When a skill needs a fresh context (e.g. independent review), the pattern is: spawn a `general-purpose` sub-agent whose prompt runs the `/andthen:<name>` slash command. Never pass a skill name as `subagent_type`.

### Wording Convention (mandatory when authoring or refactoring skill prompts)

Every `andthen:<name>` reference in a skill prompt, reference doc, or CLAUDE.md must have the type noun **adjacent** to the name:
- "the `andthen:<name>` **skill**" / "invoke the `andthen:<name>` skill" / "run the `andthen:<name>` skill"
- "the `andthen:<name>` **agent**" / "delegate to the `andthen:<name>` agent" / "spawn the `andthen:<name>` agent"

Named antipattern: **"Spawn `andthen:<skill-name>` sub-agent"**. This phrasing primes agents to pass skill names as `subagent_type`, which fails. It caused a real regression (see commit history around 0.12.x). Prefer "invoke the `andthen:<name>` skill" for in-context work, or "spawn a `general-purpose` sub-agent and have it run `/andthen:<name>`" when fresh context is genuinely needed.

Exceptions (convention does not apply):
- Bare `/andthen:<name>` invocation lines in code blocks and user-facing examples — the `/` sigil carries the meaning
- YAML/JSON schema values and metadata fields (e.g. `source_skill: andthen:plan`) — data tokens, not prose references
- Frontmatter fields like `agent: general-purpose` — runtime contract, not a reference
- Compact arrow-notation routing/redirect maps where a single parenthetical type qualifier covers all entries (e.g. `Redirects (all **skills**): fis-bundle → andthen:exec-spec / andthen:spec; ...`) — individual per-name tags would make the map unreadable; the leading qualifier suffices

When refactoring AndThen itself, any change that touches `andthen:*` references must preserve this convention. Audit command (covers every directory where the convention applies):

```sh
rg 'andthen:[a-z-]+' CLAUDE.md plugin/skills/ plugin/references/ plugin/agents/ templates/ docs/
```

For every hit, confirm it is either (a) a bare invocation in a code block/example, (b) a schema value / frontmatter field, or (c) has the type noun ("skill" / "agent") adjacent.


---


## How Skills Work

### Project Context Discovery
Skills read the **user's project** `CLAUDE.md` (not this repo's) for two key integration points:
- **Project Document Index** – a table mapping document types to file paths (specs, plans, ADRs, etc.). Skills use this to determine where to read/write output. See `templates/CLAUDE.template.md` for the table format
- **Workflow Rules, Guardrails and Guidelines** – behavioral rules and development standards that skills load before starting work (e.g. rules files, development/architecture/UI guidelines)

### Skill Anatomy
Each skill lives in `plugin/skills/<name>/` and contains:
- `SKILL.md` – the skill prompt (with frontmatter: `description`, `argument-hint`, and optional `user-invocable`, `context`, `agent`). The `description` is also a routing surface: front-load the primary use case, prefer a `Use when...` framing, include 2-4 natural trigger phrases and AndThen-native terms users actually say (`spec`, `FIS`, `PRD`, `plan`, `gap analysis`, etc.), and keep it concise enough that key terms survive truncation.
- `agents/openai.yaml` – OpenAI/Codex agent metadata for cross-agent portability
- Optional subdirectories for templates, checklists, or references

### Shared References
`plugin/references/` contains reusable reference documents loaded by multiple skills (e.g. `design-tree.md` used by `clarify`, `plan`, and `trade-off`). When skills are exported via `scripts/install-skills.sh`, reference paths are rewritten to resolve correctly outside this repo.


---


## Skill Authoring Philosophy

Modern frontier models understand *why* things matter. Skills should express **intent** — goals, outcomes, and verification criteria — not micro-managed procedures, if-then chains, or exhaustive enumerations.

**Core principles:**
- **Why over what**: Explain the reasoning behind non-obvious rules so the model can generalize to novel situations. A rule without a "why" is followed rigidly; a rule with a "why" is followed intelligently. (Aligned with Anthropic's own principle: *"AI models need to understand why we want them to behave in certain ways, rather than merely specifying what we want them to do."*)
- **Right altitude**: Use heuristics and principles, not step-by-step prescriptions. If a frontier model would naturally do something, don't instruct it. Be specific about counter-intuitive behaviors, cross-skill integration contracts, and named failure modes. Be general about standard engineering practices.
- **Named principles over unnamed rules**: A named principle (Chesterton's Fence, Prove-It Pattern, Proof-of-Work, Stop-the-Line) gives the model a conceptual anchor for *when* and *why* the principle applies. An unnamed rule is just a constraint to follow or ignore.
- **Intent reasoning is not waste**: Token efficiency is a *consequence* of intent-driven authoring, not the goal. Explaining why a verification gate exists or why test scaffolding precedes implementation is worth the tokens — it prevents the model from rationalizing its way past the step.
- **Headless by default**: Skills should run to completion without waiting for another user turn unless they are explicitly interactive by nature (for example `clarify` or `init`) or blocked by a real contract failure. Prefer explicit assumptions, conservative defaults, and documented open questions over `STOP and WAIT` patterns in execution-oriented skills.


---


## Workflow Rules, Guardrails and Guidelines

### Foundational Rules and Guardrails
_Always fully understand and adhere to the "CRITICAL RULES and GUARDRAILS in this environment" (part of system prompt) before doing any work_.


### Foundational Development Guidelines and Standards
Always fully read relevant guidelines below as needed, based on the type of work being done:
- _`docs/guidelines/DEVELOPMENT-ARCHITECTURE-GUIDELINES.md`_ when doing development work (coding, architecture, etc.)
- _`docs/guidelines/UX-UI-GUIDELINES.md`_ when doing UX/UI related work
- _`docs/guidelines/WEB-DEV-GUIDELINES.md`_ when doing web development work

- _`docs/prompt-guidelines/PROMPT-ENGINEERING-GUIDELINES.md`_ when doing prompt engineering work, i.e. writing skill prompts, agent system prompts, etc.
   - For Anthropic/Claude models, see also _`docs/prompt-guidelines/PROMPT-ENGINEERING-GUIDELINES-CLAUDE.md`_
   - For OpenAI GPT models, see also _`docs/prompt-guidelines/PROMPT-ENGINEERING-GUIDELINES-GPT.md`_


---


## Vital Documentation Resources

**IMPORTANT**: When lookup of documentation (such as API documentation, user guides, language references, etc.) is needed, or when user asks to lookup documentation directly, _always_ execute the documentation lookup in a separate background sub task (use the _`andthen:documentation-lookup`_ agent). This is **CRITICAL** to reduce the load on the main context window and ensure that the main agent can continue working without interruptions.


---


## Version Bumps

When bumping the version, **always** update all three:
- `CHANGELOG.md` – add new version entry
- `.claude-plugin/marketplace.json` – update the `"version"` field in the plugin entry
- `plugin/.claude-plugin/plugin.json` – update the `"version"` field


---


## Useful Tools and MCP Servers

### Command line file search and code exploration tools
- **ripgrep (rg)**: Fast recursive search. Example: `rg "createServerSupabaseClient"`. _Use instead of grep_ for better search performance.
- **ast-grep**: Search by AST node types. Example: `ast-grep 'import { $X } from "supabase"' routes/`
- **tree**: Directory structure visualization. Example: `tree -L 2 routes/`

### Context7 MCP - Library and Framework Documentation Lookup (https://github.com/upstash/context7)
Context7 MCP pulls up-to-date, version-specific documentation and code examples straight from the source.
**Only** use Context7 MCP via the _`andthen:documentation-lookup`_ agent for documentation retrieval tasks.

### Fetch (https://github.com/modelcontextprotocol/servers/tree/main/src/fetch)
Retrieves and processes content from web pages, converting HTML to markdown for easier consumption.
**Only** use Fetch MCP via the _`andthen:documentation-lookup`_ agent for documentation retrieval tasks.
