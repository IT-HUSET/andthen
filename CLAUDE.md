# AndThen – Structured Workflows for Agentic Development

This file provides guidance to AI coding agents when working with code in this project.


---


## Project Overview

AndThen is an opinionated workflow system for AI coding agents. It provides structured skills that guide development through disciplined pipelines – from requirements discovery through implementation to review. See `plugin/README.md` for the full workflow overview and skill reference.

Core artifacts are the **Feature Implementation Specification (FIS)** for single features and the **PRD + Plan Bundle** (story breakdown + FIS for every story + shared technical research) for multi-feature work. The `andthen:prd` skill produces the PRD; the `andthen:plan` skill consumes that PRD and produces the plan bundle in one pass; the `andthen:exec-plan` skill consumes the bundle as-is.

**Structure:**
- `plugin/` – Claude Code plugin (skills and agents). Each skill is fully self-contained with its own `references/`, `templates/`, and `scripts/` where needed — no cross-skill or plugin-root paths are used inside skill files.
- `hooks/` – Claude Code hooks (blocked commands, notification scripts)
- `scripts/` – Installation and setup scripts
- `docs/` – Guidelines and reference documentation used by workflow skills
- `docs/temp/research/` – Research outputs (worktree strategies, skill analysis, etc.)
- `skills` → symlink to `plugin/skills/` (for Codex/agent discovery)


---


## Skill Invocation

Skills invoke as `/andthen:<name>` or via the Skill tool. Agents invoke via the Task tool with `subagent_type: "andthen:<name>"`. Both share the `andthen:` prefix but are **not** interchangeable — passing a skill name as `subagent_type` fails with "Agent type not found". The 3 valid agents live in `plugin/agents/`: `documentation-lookup`, `research-specialist`, `visual-validation-specialist`. All other AndThen capabilities (architecture, UI/UX, testing, triage, etc.) are **skills** — invoke via `/andthen:<name>` or via the Skill tool. Skills marked `context: fork` in their frontmatter (e.g. `ops`) auto-isolate in a sub-context when invoked; other skills that need fresh context are run by spawning a `general-purpose` sub-agent whose prompt runs `/andthen:<name>`.

**Naming convention**: skills are named for the *activity* (`architecture`, `ui-ux-design`, `testing`, `triage`); agents are named for the *persona* (`research-specialist`, `documentation-lookup`, `visual-validation-specialist`). Activity-nouns belong in `plugin/skills/`, persona-nouns in `plugin/agents/`.

**Codex agents are generated at install time** from `plugin/agents/*.md` by `scripts/generate-codex-agents.sh`, invoked by `scripts/install-skills.sh`. Claude Code agent files are the source of truth; Codex TOMLs are not committed.

`scripts/install-skills.sh` rewrites references for portability: `/andthen:<name>` → `$andthen-<name>` and bare `andthen:<name>` → `andthen-<name>` (hyphen required for Codex CLI `$` sigil parser).

### Wording Convention

Every `andthen:<name>` reference in prose (skill prompts, references, this file) must have the type noun **adjacent**: "the `andthen:<name>` **skill**" or "the `andthen:<name>` **agent**". The named antipattern **"Spawn `andthen:<skill-name>` sub-agent"** primes agents to pass skill names as `subagent_type` and caused a real regression (0.12.x) — prefer "invoke the `andthen:<name>` skill" or "spawn a `general-purpose` sub-agent and have it run `/andthen:<name>`".

Exceptions: bare `/andthen:<name>` in code blocks, schema/frontmatter data values, and compact routing maps where a leading parenthetical qualifier covers all entries.

Audit: `rg 'andthen:[a-z-]+' CLAUDE.md plugin/ docs/`


---


## How Skills Work

### Project Context Discovery
Skills read the **user's project** `CLAUDE.md` (not this repo's) for two key integration points:
- **Project Document Index** – a table mapping document types to file paths (specs, plans, ADRs, etc.). Skills use this to determine where to read/write output. See `plugin/skills/init/templates/CLAUDE.template.md` for the table format
- **Workflow Rules, Guardrails and Guidelines** – behavioral rules and development standards that skills load before starting work (e.g. rules files, development/architecture/UI guidelines)

### Skill Anatomy
Each skill lives in `plugin/skills/<name>/` and contains:
- `SKILL.md` – the skill prompt (with frontmatter: `description`, `argument-hint`, and optional `user-invocable`, `context`, `agent`). The `description` is also a routing surface: front-load the primary use case, prefer a `Use when...` framing, include 2-4 natural trigger phrases and AndThen-native terms users actually say (`spec`, `FIS`, `PRD`, `plan`, `gap analysis`, etc.), and keep it concise enough that key terms survive truncation.
- `agents/openai.yaml` – OpenAI/Codex agent metadata for cross-agent portability
- Optional subdirectories for templates, checklists, or references

### Self-Contained Skills — Asset Ownership

Skills are fully self-contained: each skill owns its `references/`, `templates/`, and `scripts/` locally. Skill files never reach into sibling skills (no `../<other-skill>/...` paths).

**Two categories of shared assets:**

1. **Plugin-level shared assets** (`plugin/references/`) — 8 contract-load-bearing files consumed by multiple skills via `${CLAUDE_PLUGIN_ROOT}/references/<asset>.md`. See `## Shared Plugin Assets` below.
2. **Skill-level duplicates** — remaining shared assets duplicated into each consuming skill's `references/` or `templates/`. Markdown duplicates carry a YAML frontmatter `source:` pointer naming the canonical owner:

```yaml
---
source: plugin/skills/<owner-skill>/<subdir>/<file>.md
---
```

Script duplicates (`.sh`) do not support frontmatter; their ownership is tracked only in the table below.

Edits land in the canonical source first; consumers pull in or diverge as their needs evolve. No sync script, no CI check — accept drift and reconcile ad hoc.

**Promotion criterion** — a file belongs in tier (1) only when wording drift between copies would break a cross-skill contract (status strings, severity scales, FIS structural rules, automation `BLOCKED:` triggers — anything one skill produces and another consumes against). Craft guidance (calibration heuristics, taxonomies, framework prose) stays in tier (2) so each consumer can specialize. The plugin-shared tier costs install-time path rewriting and inlined-canonical propagation per target; pay it only where the contract demands it. Historical pendulum: a single shared `plugin/references/` was tried and retired in favor of pure self-containment, then partially reinstated for the contract-load-bearing subset — promote conservatively.

**References (`references/`)** — skill-level duplicates only; canonical plugin-level shared references live at `plugin/references/` (see [Shared Plugin Assets](#shared-plugin-assets) below).

| File | Owner | Also in |
|---|---|---|
| adversarial-challenge.md | review | architecture |
| design-tree.md | architecture | clarify |
| farley-framework.md | architecture | testing |
| review-calibration.md | review | architecture |
| trust-boundaries.md | review | e2e-test, triage |

**Templates (`templates/`)** — skill-level duplicates only

| File | Owner | Also in |
|---|---|---|
| plan-template.md | plan | — |
| CLAUDE.template.md | init | — |
| project-state-templates.md | init | map-codebase |

**Scripts (`scripts/`)**

| File | Canonical source | Also in |
|---|---|---|
| run-security-scan.sh | review | — |

**Contract-critical fields** (severity labels, verdict strings, report section names, script CLI contracts) must stay aligned across copies. Guidance content is allowed to diverge.


### Shared Plugin Assets

The 8 contract-load-bearing assets live at `plugin/references/` — a single canonical location shared across all consuming skills. These files carry **no** `source:` frontmatter; absence of `source:` is the unambiguous signal that a file is the canonical source.

| Asset | Consumed by |
|---|---|
| `automation-mode.md` | prd, plan, spec, exec-spec, exec-plan |
| `data-contract.md` | ops, exec-spec, exec-plan |
| `execution-discipline.md` | exec-spec, exec-plan |
| `fis-authoring-guidelines.md` | spec, plan, review |
| `fis-template.md` | spec, plan |
| `lens-adversarial.md` | review, quick-review, architecture |
| `prd-template.md` | prd, plan |
| `red-team-calibration.md` | review, quick-review |

**Reference syntax** in skill prompts: `${CLAUDE_PLUGIN_ROOT}/references/<asset>.md` (strict braces form only; bare `$CLAUDE_PLUGIN_ROOT` is rejected by `install-skills.sh`).

**Install-time propagation** (`scripts/install-skills.sh` per-target behavior):

| Target | Behavior |
|---|---|
| Plugin install (Claude Code plugin tier) | No rewrite — `${CLAUDE_PLUGIN_ROOT}` resolves at runtime |
| `--claude-user` (Claude Code user tier) | Inline canonical content into each skill's `references/`; rewrite path to local-relative form |
| Default / Codex (`~/.agents/skills/`) | Inline canonical content into each skill's `references/`; rewrite path to local-relative form |


---


## Skill Authoring Philosophy

Modern frontier models understand *why* things matter. Skills should express **intent** — goals, outcomes, and verification criteria — not micro-managed procedures, if-then chains, or exhaustive enumerations.

**Core principles:**
- **Why over what**: Explain the reasoning behind non-obvious rules so the model can generalize to novel situations. A rule without a "why" is followed rigidly; a rule with a "why" is followed intelligently. (Aligned with Anthropic's own principle: *"AI models need to understand why we want them to behave in certain ways, rather than merely specifying what we want them to do."*)
- **Right altitude**: Use heuristics and principles, not step-by-step prescriptions. If a frontier model would naturally do something, don't instruct it. Be specific about counter-intuitive behaviors, cross-skill integration contracts, and named failure modes. Be general about standard engineering practices.
- **Named principles over unnamed rules**: A named principle (Chesterton's Fence, Prove-It Pattern, Proof-of-Work, Stop-the-Line) gives the model a conceptual anchor for *when* and *why* the principle applies. An unnamed rule is just a constraint to follow or ignore.
- **Intent reasoning is not waste**: Token efficiency is a *consequence* of intent-driven authoring, not the goal. Explaining why a verification gate exists or why test scaffolding precedes implementation is worth the tokens — it prevents the model from rationalizing its way past the step.
- **Headless by default**: Skills should run to completion without waiting for another user turn unless they are explicitly interactive by nature (for example `clarify` or `init`) or blocked by a real contract failure. Prefer explicit assumptions, conservative defaults, and documented open questions over `STOP and WAIT` patterns in execution-oriented skills.
- **Brevity and clear language**: Always keep skills pragmatic, concise and actionable. Avoid jargon, verbosity, and complex sentence structures. Use simple, direct language to convey instructions and principles. 


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
