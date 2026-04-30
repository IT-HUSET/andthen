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

Exceptions: bare `/andthen:<name>` in code blocks or inline code spans (data, not prose), schema/frontmatter data values, and compact routing maps where a leading parenthetical qualifier covers all entries.

Audit: `rg 'andthen:[a-z-]+' CLAUDE.md plugin/ docs/`

### Citation Convention

Cite the canonical author + work title that originated a principle, not a popularizer's restatement. Don't inline external URLs in shipped skill content — they invite unnecessary agent fetches and rot. Personal skill-collection repositories (`*/skills/*`) are not authoritative sources. When a popularizer's turn-of-phrase is load-bearing, rephrase in our own words. Provenance URLs belong in research artifacts (`.agent_temp/research/*.md`) and FIS Required Context comments only.

Audit: `rg 'github\.com/[^/]+/skills' plugin/`


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

### Self-Contained Skills

Skills are fully self-contained: each skill owns its `references/`, `templates/`, and `scripts/` locally. Skill files never reach into sibling skills (no `../<other-skill>/...` paths).

Content shared by ≥2 skills lives at `plugin/references/` and is consumed via `${CLAUDE_PLUGIN_ROOT}/references/<asset>.md` — see [Shared Plugin Assets](#shared-plugin-assets) below. `install-skills.sh` inlines each canonical into every consuming skill at install time, so installed bundles stay self-contained.

**Forking shared content** — when a consumer genuinely needs a divergent version, fork explicitly: copy the canonical into the skill's local `references/` under a distinct name (e.g. `triage-trust-boundaries.md` as a triage-only fork of `trust-boundaries.md`) and point that skill's references at the local copy. Don't preemptively duplicate. The earlier two-tier model (canonical + skill-level duplicates with `source:` frontmatter pointers) was retired after the duplicates failed to actually diverge — divergence is now an explicit-fork-on-demand pattern, not a default.

**Skill-level scripts**

| File | Owner | Also in |
|---|---|---|
| run-security-scan.sh | review | — |


### Shared Plugin Assets

The 15 shared assets live at `plugin/references/` — a single canonical location consumed by multiple skills.

| Asset | Consumed by |
|---|---|
| `adversarial-challenge.md` | review, architecture |
| `automation-mode.md` | prd, plan, spec, exec-spec, exec-plan, refactor, remediate-findings |
| `data-contract.md` | ops, exec-spec, exec-plan |
| `design-tree.md` | clarify, architecture |
| `execution-discipline.md` | exec-spec, exec-plan |
| `farley-framework.md` | architecture, testing |
| `fis-authoring-guidelines.md` | spec, plan, review |
| `fis-template.md` | spec, plan |
| `lens-adversarial.md` | review, quick-review |
| `prd-template.md` | prd, plan |
| `project-state-templates.md` | init, map-codebase |
| `red-team-calibration.md` | review, quick-review |
| `review-calibration.md` | review, architecture |
| `review-report-location.md` | review, architecture |
| `trust-boundaries.md` | review, e2e-test, triage |

**Reference syntax** in skill prompts: `${CLAUDE_PLUGIN_ROOT}/references/<asset>.md` (strict braces form only; bare `$CLAUDE_PLUGIN_ROOT` is rejected by `install-skills.sh`). In markdown links, put the bare filename in the link text and the full token in the URL — `` [`<asset>.md`](${CLAUDE_PLUGIN_ROOT}/references/<asset>.md) `` — so the rendered link text stays stable across install tiers; the URL is what `install-skills.sh` rewrites.

**Install-time propagation** (`scripts/install-skills.sh` per-target behavior):

| Target | Behavior |
|---|---|
| Plugin install (Claude Code plugin tier) | No rewrite — `${CLAUDE_PLUGIN_ROOT}` resolves at runtime |
| `--claude-user` (Claude Code user tier) | Inline canonical content into each skill's `references/`; rewrite path to local-relative form |
| Default / Codex (`~/.agents/skills/`) | Inline canonical content into each skill's `references/`; rewrite path to local-relative form |


---


## Workflow Rules, Guardrails and Guidelines

### Foundational Rules and Guardrails
_Always fully understand and adhere to the "CRITICAL RULES and GUARDRAILS in this environment" (part of system prompt) before doing any work_.

### Skill and Prompt Authoring Guidelines

_**Always apply the following rules whenever modifying or creating skills, skill reference files or prompts in general.**_

Modern frontier models understand *why* things matter. Skills should express **intent** — goals, outcomes, and verification criteria — not micro-managed procedures, if-then chains, or exhaustive enumerations.

**Core principles:**
- **Why over what**: Explain the reasoning behind non-obvious rules so the model can generalize to novel situations. A rule without a "why" is followed rigidly; a rule with a "why" is followed intelligently. (Aligned with Anthropic's own principle: *"AI models need to understand why we want them to behave in certain ways, rather than merely specifying what we want them to do."*)
- **Right altitude**: Use heuristics and principles, not step-by-step prescriptions. If a frontier model would naturally do something, don't instruct it. Be specific about counter-intuitive behaviors, cross-skill integration contracts, and named failure modes. Be general about standard engineering practices.
- **Named principles over unnamed rules**: A named principle (Chesterton's Fence, Prove-It Pattern, Proof-of-Work, Stop-the-Line) gives the model a conceptual anchor for *when* and *why* the principle applies. An unnamed rule is just a constraint to follow or ignore.
- **Intent reasoning is not waste**: Token efficiency is a *consequence* of intent-driven authoring, not the goal. Explaining why a verification gate exists or why test scaffolding precedes implementation is worth the tokens — it prevents the model from rationalizing its way past the step.
- **Headless by default**: Skills should run to completion without waiting for another user turn unless they are explicitly interactive by nature (for example `clarify` or `init`) or blocked by a real contract failure. Prefer explicit assumptions, conservative defaults, and documented open questions over `STOP and WAIT` patterns in execution-oriented skills.
- **Brevity and clear language**: Always keep skills pragmatic, concise and actionable. Avoid jargon, verbosity, prose, and complex sentence structures. Use simple, direct language to convey instructions and principles.

**Fitness check.** Skills are working when implementation diffs trace cleanly to specs/FIS, headless runs reach completion without "stop and wait" pauses, and review findings are downstream of clarification gaps — not implementation drift or mid-implementation Boy Scout creep.

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
