# AndThen Plugin Architecture

How the AndThen plugin is structured: the skill loading model, how shared content is propagated at install time, and the patterns skills follow internally. Read this when working on changes that touch skill structure, shared references, the install pipeline, or how skills consume project context.

For everyday rules and routing, see `CLAUDE.md` instead.


---


## Project Context Discovery

Skills read the **user's project** `CLAUDE.md` (not this repo's) for two key integration points:

- **Project Document Index** – a table mapping document types to file paths (specs, plans, ADRs, etc.). Skills use this to determine where to read/write output. See `plugin/skills/init/templates/CLAUDE.template.md` for the table format.
- **Project-Specific Guidelines and Rules** – project-specific guidelines and workflow notes that skills load before starting work (e.g. project conventions, prohibitions, visual-validation workflow). The universal `Foundational Rules, Guardrails and Principles` are wired in separately at the top of the file.


---


## Skill Anatomy

Each skill lives in `plugin/skills/<name>/` and contains:

- `SKILL.md` – the skill prompt (with frontmatter: `description`, `argument-hint`, and optional `user-invocable`, `context`, `agent`). The `description` is also a routing surface: front-load the primary use case, prefer a `Use when...` framing, include 2-4 natural trigger phrases and AndThen-native terms users actually say (`spec`, `FIS`, `PRD`, `plan`, `gap analysis`, etc.), and keep it concise enough that key terms survive truncation.
- `agents/openai.yaml` – OpenAI/Codex agent metadata for cross-agent portability.
- Optional subdirectories for templates, checklists, or references.


---


## Plugin Agents

Agents live in `plugin/agents/*.md`. These markdown files are the source of truth for both Claude Code plugin-tier agents and generated Codex agents.

Current agent families:

- `documentation-lookup` – documentation retrieval specialist.
- `review-*` – review council persona agents. They are deliberately review-scoped, not a broad agent zoo: Critic, Devil's Advocate, Synthesis Challenger, and a small set of specialist reviewers.

Install targets:

| Target | Agent behavior |
|---|---|
| Claude Code plugin tier | Reads `plugin/agents/*.md` directly as plugin-provided agents. |
| `--claude-user` | Copies `plugin/agents/*.md` to `~/.claude/agents`, prefixing frontmatter `name:` to match the installed filename. |
| Default / Codex | Runs `scripts/generate-codex-agents.sh`, converting each markdown agent into a TOML file with `developer_instructions`. |

Claude markdown remains canonical because it maps directly to custom sub-agent prompts; Codex TOMLs are generated artifacts and should not be edited by hand.


---


## Self-Contained Skills

Skills are fully self-contained: each skill owns its `references/`, `templates/`, and `scripts/` locally. Skill files never reach into sibling skills (no `../<other-skill>/...` paths).

Content shared by ≥2 skills lives at `plugin/references/` and is consumed via `${CLAUDE_PLUGIN_ROOT}/references/<asset>.md` – see **Shared Plugin Assets** below. `install-skills.sh` inlines each canonical into every consuming skill at install time, so installed bundles stay self-contained.

**Forking shared content** – when a consumer genuinely needs a divergent version, fork explicitly: copy the canonical into the skill's local `references/` under a distinct name (e.g. `triage-trust-boundaries.md` as a triage-only fork of `trust-boundaries.md`) and point that skill's references at the local copy. Don't preemptively duplicate – fork on demand, not by default.


---


## Shared Plugin Assets

The 20 shared assets live at `plugin/references/` – a single canonical location consumed by multiple skills.

| Asset | Consumed by |
|---|---|
| `adversarial-challenge.md` | review, architecture |
| `automation-mode.md` | prd, plan, spec, exec-spec, exec-plan, simplify-code, refactor, remediate-findings |
| `critic-calibration.md` | review, quick-review |
| `data-contract.md` | ops, plan, spec, exec-spec, exec-plan, review |
| `design-tree.md` | clarify, architecture |
| `execution-discipline.md` | exec-spec, exec-plan |
| `execution-named-blocks.md` | spec, exec-spec, quick-implement, triage |
| `farley-framework.md` | architecture, testing |
| `fis-authoring-guidelines.md` | spec, plan, review |
| `fis-template.md` | spec |
| `github-publish.md` | clarify, prd, triage, exec-spec, exec-plan, plan |
| `intent-and-rules-context.md` | review, quick-review, remediate-findings, simplify-code |
| `lens-adversarial.md` | review, quick-review |
| `plan-issue-shape.md` | plan, exec-plan |
| `plan-schema.md` | plan, exec-plan, ops, review |
| `prd-template.md` | prd |
| `project-state-templates.md` | init, map-codebase |
| `review-calibration.md` | review, quick-review, architecture |
| `review-report-location.md` | review, architecture |
| `trust-boundaries.md` | review, e2e-test, triage |


---


## Reference Syntax in Skill Prompts

Two patterns, distinct purposes:

- `${CLAUDE_PLUGIN_ROOT}/references/<asset>.md` – for the **shared canonicals** at `plugin/references/`. The asset lives at plugin root, not inside a specific skill. `install-skills.sh` inlines the canonical into each consuming skill's local `references/` and rewrites the path to skill-root-relative form (Codex / `--claude-user`); Plugin tier resolves `${CLAUDE_PLUGIN_ROOT}` at runtime. In markdown links, put the bare filename in the link text and the full token in the URL – `` [`<asset>.md`](${CLAUDE_PLUGIN_ROOT}/references/<asset>.md) `` – so the rendered link text stays stable across install tiers; the URL is what `install-skills.sh` rewrites.
- `${CLAUDE_SKILL_DIR}/<rest>` – **required for bash invocations of skill-bundled scripts**, where the agent's cwd is not guaranteed. Use for any bash invocation of a bundled script (e.g. `bash ${CLAUDE_SKILL_DIR}/scripts/teardown-worktrees.sh`); avoid `../scripts/foo.sh`. **Markdown links and prose references** to bundled files (`templates/`, `scripts/`, non-canonical `references/`) may use bare-relative paths – they're read as documentation, not executed. Bash invocations are the only context where `${CLAUDE_SKILL_DIR}` is mandatory.

Both forms require the strict braces in their contexts (canonicals always; `${CLAUDE_SKILL_DIR}` in bash invocations); bare `$CLAUDE_PLUGIN_ROOT` and `$CLAUDE_SKILL_DIR` are rejected by `install-skills.sh`.


---


## Install-Time Propagation

`scripts/install-skills.sh` per-target behavior:

| Target | `${CLAUDE_PLUGIN_ROOT}/references/<asset>` | `${CLAUDE_SKILL_DIR}/<rest>` |
|---|---|---|
| Plugin install (Claude Code plugin tier) | No rewrite – resolves at runtime | No rewrite – resolves at runtime |
| `--claude-user` (Claude Code user tier) | Inline canonical into skill's `references/`; rewrite path to local-relative form | No rewrite – Claude Code substitutes natively |
| Default / Codex (`~/.agents/skills/`) | Inline canonical into skill's `references/`; rewrite path to local-relative form | Replace with absolute install path of the skill |

The installer also propagates `plugin/agents/*.md`: Claude user-tier installs get prefixed markdown agents, and Codex installs get generated TOMLs via `scripts/generate-codex-agents.sh`. `--no-codex-agents` skips Codex agent generation; `--claude-agents-dir` overrides the Claude agent destination alongside `--claude-skills-dir`.

Agent propagation is overwrite-only. Removing or renaming a source agent does not delete stale generated `<prefix>*.toml` or copied `<prefix>*.md` files from prior installs; users must remove obsolete generated agents when they need the visible set to exactly match `plugin/agents/`.
