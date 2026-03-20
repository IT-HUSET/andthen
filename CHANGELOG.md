# Changelog

All notable changes to **AndThen** are documented here.
Follows [Semantic Versioning](https://semver.org/) and [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.

---

## [0.6.4] — 2026-03-20

### Changed
- **`review-gap` clarified as implementation review** — description, input interpretation, and workflow now explicitly frame the skill as comparing current code/worktree against requirements baselines. New Step 0 ("Resolve Review Target") locates the implementation target before analysis begins. Added concrete examples showing correct usage vs. `review-doc`. Multi-repo workspace resolution with sensible fallback when no workspace metadata exists.

---

## [0.6.3] — 2026-03-19

### Changed
- **Plan skill: PRD responsibility explicit** — description, title, and OpenAI agent display name now clearly state PRD creation as a primary responsibility (not just an implicit prerequisite)
- **"AndThen -" prefix on all OpenAI display names** — consistent `"AndThen - <Skill>"` branding across all `openai.yaml` agent configs
- **`review-gap` input interpretation guardrails** — new "Input Interpretation" section clarifies that documents passed as arguments are comparison baselines (requirements sources), not the review target. Stops early if no implementation exists to compare against
- **Workflow diagrams corrected** — `review-gap --doc` → `review-doc` in README and plugin README pipeline diagrams
- **Model effort selection guide** — updated `review-gap` description to reflect its focused scope (gap analysis against requirements, no longer doc/PR review modes)
- **Triage OpenAI agent metadata** — display name and description updated to match the skill's current name and scope (`"Triage & Fix Issues"`)
- **CLAUDE.template.md** — expanded guideline trigger wording to include "code exploration, architecture and solution design"

### Fixed
- **`allow_implicit_invocation: true` policy** added to OpenAI agent skill configs – this is a workaround for an apparent bug in Codex.
- **Argument-hint quoting** — all `argument-hint` values in SKILL.md frontmatter now properly quoted
- **`install-skills.sh` reference path rewriting** — installed skills now rewrite `plugin/references/` paths to sibling `<prefix>references/` paths so references resolve correctly outside the repo

---

## [0.6.2] — 2026-03-17

### Added
- **Semgrep integration in security reviews**: `review-code` Security Review phase now includes automated Semgrep scanning via Claude Code plugin (`semgrep/mcp-marketplace`), CLI, or MCP tools — running in parallel with `/security-review`. All tools optional; graceful fallback to manual checklist review
- **Automated Scanning section in Security Review Checklist**: New checklist section with Semgrep triage steps, config recommendations by focus area (`p/security-audit`, `p/owasp-top-ten`, `p/secrets`), and other tool references
- **Security Sentinel uses Semgrep**: `review-council` and `review-council-team` Security Sentinel role now runs Semgrep scans on changed files when available

---

## [0.6.1] — 2026-03-17

### Changed
- **`init` offers UBIQUITOUS_LANGUAGE.md**: Added domain glossary to the optional document checklist under a new "Domain" category, with a hint to use `andthen.ubiquitous-language` for richer generation

---

## [0.6.0] — 2026-03-17

### Added
- **Ubiquitous Language skill** (`ubiquitous-language`): Extract and maintain a domain glossary (`UBIQUITOUS_LANGUAGE.md`) from codebase and documentation. Supports `--update` mode for incremental glossary maintenance. Integrates with DDD principles throughout the pipeline
- **UL pipeline integration**: Domain language awareness woven into `clarify` (term extraction), `spec` (canonical terms in FIS), `plan` (canonical terms in stories), `exec-spec` (sub-agents receive UL context, TV01 checks terminology), `review-code` (domain language checklist), and `review-gap` (terminology drift detection)
- **Domain Language Review Checklist** (`review-code`): New `DOMAIN-LANGUAGE-REVIEW-CHECKLIST.md` covering terminology consistency, domain model alignment, and new term detection
- **"Design It Twice" in trade-off** (`trade-off`): New optional Phase 1.5 spawns 3+ parallel sub-agents with contrasting architectural constraints to generate radically different designs before evaluation. Synthesizes findings in prose, not tables
- **Triage investigation mode** (`triage`): `--plan-only` flag stops after root cause analysis and outputs a structured fix plan instead of implementing fixes. `--to-issue` publishes the plan as a GitHub issue
- **TDD Lite** (`spec`, `exec-spec`): FIS template gains "Test-Implementation Pairing" section mapping tests to implementation tasks. `exec-spec` Step 2 directs sub-agents to write paired tests before implementing (red-green rhythm by structure)
- **Vertical slicing** (`plan`, `spec`): "Vertical" added as first story principle — stories cut through all layers end-to-end. Phase template restructured around tracer-bullet first phase. FIS template adds vertical-slice task ordering guidance
- **GitHub issue output** (`spec`, `plan`, `review-gap`, `review-code`): `--to-issue` flag publishes skill output as a GitHub issue. `review-gap` and `review-code` also support `--to-pr <number>` for PR comments
- **`UBIQUITOUS_LANGUAGE.md` template**: Added to project Document Index and `project-state-templates.md` as a standard project file
- **DDD guidelines expanded**: "Ubiquitous Language in Practice" subsection added to `DEVELOPMENT-ARCHITECTURE-GUIDELINES.md` with actionable guidance on domain naming, glossary maintenance, and ambiguity resolution

### Changed
- **Extras prefix removed**: All `extras-` prefixed skills renamed — `extras-quick-implement` → `quick-implement`, `extras-design-system` → `design-system`, `extras-wireframes` → `wireframes`, `extras-refactor` → `refactor`, `extras-review-council` → `review-council`, `extras-review-council-team` → `review-council-team`, `extras-map-codebase` → `map-codebase`
- **`extras-troubleshoot` → `triage`**: Renamed with both prefix removal and base name change to better reflect systematic investigation capability
- **Triage skill description**: Updated to mention investigation, diagnosis, and fix modes
- **Portable `andthen.` skill prefix**: All skills now use `name: andthen.<skill>` in SKILL.md frontmatter (e.g., `andthen.spec`, `andthen.review-code`). Leverages Claude Code bug [#22063](https://github.com/anthropics/claude-code/issues/22063) — the `name:` field bypasses the plugin namespace, registering skills as `/andthen.spec` (portable dot notation) instead of `/andthen:andthen.spec`. Cross-references within skills use `andthen.<skill>` for skills and `andthen:<agent>` for agents (Claude Code-specific)
- **`install-codex.sh` → `install-skills.sh`**: Renamed for clarity. Default prefix changed from `andthen-` to `andthen.` to match the new naming convention
- **Invocation docs updated**: Skills invoked as `/andthen.<skill>` in Claude Code, `$andthen.<skill>` or `/andthen.<skill>` in Codex and other agents

---

## [0.5.0] — 2026-03-17

### Changed
- **Commands → Skills migration**: All 17 commands (9 core + 8 extras) converted to the skills format (`SKILL.md` in dedicated directories). Commands and skills are now unified under `plugin/skills/`. The `plugin/commands/` directory has been removed
- **Extras prefix**: Extras skills now use an `extras-` prefix in directory and skill name (e.g., `extras-quick-implement`, `extras-wireframes`, `extras-review-council`). In Claude Code: `/andthen:extras-quick-implement`
- **Skill names simplified**: Removed `andthen-` prefix from `name` field in existing skills (`andthen-review-code` → `review-code`, `andthen-review-doc` → `review-doc`, `andthen-e2e-test` → `e2e-test`, `andthen-ops` → `ops`). Claude Code plugin namespacing (`/andthen:<skill>`) provides the vendor scope
- **FIS template extracted** (`spec`): The inline FIS template (~225 lines) moved to `templates/fis-template.md` within the skill directory, leveraging the skills directory structure for supporting files
- **Codex install script**: Rewritten for skills-only workflow. Default destination changed from `~/.codex/prompts` + `~/.codex/skills` to `~/.agents/skills/` (the emerging cross-agent standard). The `--prompts-dir` option has been removed

### Added
- **OpenAI Codex metadata** (`agents/openai.yaml`): Every skill now includes an `agents/openai.yaml` with `display_name`, `short_description`, and `allow_implicit_invocation` policy for Codex compatibility
- **Cross-agent portability**: Skills follow the open agent skills standard (`SKILL.md` + optional `agents/`, `templates/`, `scripts/`, `references/`), compatible with Claude Code, Codex CLI, and other agents that scan `~/.agents/skills/`

---

## [0.4.0] — 2026-03-16

### Added
- **Goal-backward planning** (`plan`): New "Goal-Backward Analysis" step works backward from desired outcomes before defining stories — produces Must-be-TRUE statements that become primary acceptance criteria
- **Wave-based parallelization** (`plan`, `exec-plan`, `exec-plan-team`): Stories are pre-assigned to execution waves (W1, W2, W3...) during planning; execution commands consume wave assignments for cleaner parallel orchestration without runtime dependency analysis
- **Deep verification — Nyquist Rule** (`spec`, `exec-spec`, `review-gap`): Verification now checks 4 dimensions (Exists, Substantive, Wired, Functional) instead of just existence; stub detection and wiring checks catch TODOs, placeholders, and unconnected components
- **Verification patterns reference** (`plugin/references/verification-patterns.md`): Comprehensive reference with stub detection patterns, wiring check commands, and the Nyquist verification principle
- **`init` command**: Interactive project setup — detects current state (new project, partial setup, brownfield) and fills gaps non-destructively. Generates CLAUDE.md from template, creates selected document types, copies guidelines, and integrates with `map-codebase` for existing codebases
- **`map-codebase`** (extras): Brownfield codebase analysis command — spawns parallel sub-agents to produce STACK.md, ARCHITECTURE.md, CONVENTIONS.md, and a discovered requirements document that feeds directly into `/andthen:plan`
- **`andthen-ops` skill**: Deterministic operations for state management (STATE.md, plan.md status, FIS checkboxes), git conventions (commit messages, branch naming, changelog entries), and progress tracking (summary, stale detection)
- **UI Design Contract gate** (`exec-spec`): New Step 1.7 auto-generates a UI-SPEC.md design contract (spacing, typography, colors, components, breakpoints) when frontend work is detected, ensuring visual consistency across sub-agents
- **Project state templates** (`templates/project-state-templates.md`): Starter templates for STATE.md, REQUIREMENTS.md, ROADMAP.md, ARCHITECTURE.md, CONVENTIONS.md, LEARNINGS.md, and STACK.md
- **Project Document Index** (`templates/CLAUDE.template.md`): Seven new optional document rows — State, Requirements, Roadmap, Architecture, Conventions, Learnings, Stack

### Changed
- **`implementation-notes.md` → `LEARNINGS.md`**: Renamed and broadened scope — now captures domain knowledge, procedural knowledge, and error patterns (with deterministic vs infrastructure distinction) alongside implementation traps. Includes self-maintenance guidance (review, merge, prune). Topic-based organization instead of chronological
- **Story Catalog format** (`plan`): Table now includes a Wave column for pre-computed execution wave assignments
- **Codex installer**: Now also copies `plugin/references/` alongside prompts so non-Claude-Code agents can access verification patterns

---

## [0.3.1] — 2026-03-16

### Improved
- **`plan` — artifact chaining from `clarify`**: Plan command now detects `requirements-clarification.md` (from `/andthen:clarify`) and draft PRDs (`prd-draft.md`) in the input directory, using them as the basis for PRD creation instead of re-running full discovery
- **`plan` — new Step 1c** (PRD Creation from Existing Artifacts): Assesses coverage from prior artifacts, conducts only targeted gap-filling for genuinely missing information, and preserves existing decisions/rationale when structuring the PRD
- **`clarify` — improved handoff guidance**: Follow-up actions now explicitly guide users toward `/andthen:plan <output-directory>` for seamless artifact handoff
- **Interview guardrails** (`clarify`, `plan`): Strengthened STOP-and-WAIT instructions in discovery interviews to prevent agents from assuming answers or proceeding without user input

---

## [0.3.0] — 2026-03-15

### Added
- **Portable `exec-plan`**: New version that works across all coding agents (Claude Code, Codex CLI, Aider, Cursor, etc.) using sub-agents with sequential fallback — no longer requires Agent Teams
- **Portable `review-council`**: New version using a three-phase sub-agent pipeline (specialist reviews → Devil's Advocate challenge → Synthesis review) instead of requiring real-time Agent Teams debate
- **Agent Teams variants**: Previous Agent Teams implementations preserved as `exec-plan-team` and `review-council-team` for users who want enhanced parallelism with inter-agent coordination
- **Testing Strategy in FIS template** (`spec`): New section in the FIS template for defining test scope, key test scenarios, edge cases, and test pattern references — gives the testing agent concrete direction during `exec-spec` instead of inventing test cases from scratch
- **Test scaffolding step** (`exec-spec`): New optional Step 1.5 writes failing test skeletons from the FIS Testing Strategy before implementation begins, enabling a TDD-style workflow where tests become acceptance gates for implementation tasks
- **Structured remediation loop** (`exec-spec`): TV04 rewritten as a triage → fix → re-validate cycle that only re-runs affected validation levels, with a 3-cycle hard cap before escalating to the user
- **Review council callout** (`exec-spec`): Tip in TV04 suggesting `review-council` for high-stakes features (auth, payments, data integrity)

### Changed
- **`exec-plan` is now portable**: The default `exec-plan` command uses sub-agents (if available) with sequential fallback — works on any agent. The former Agent Teams version is now `exec-plan-team`
- **`review-council` is now portable**: The default `review-council` command uses parallel sub-agents for reviews and sequential adversarial debate phases. The former Agent Teams version is now `review-council-team`
- **Migration note**: Users of the previous `exec-plan` (which required Agent Teams) should use `exec-plan-team` for equivalent behavior. The new `exec-plan` works across all agents but uses sub-agents instead of Agent Teams coordination
- **Codex installer**: `install-skills.sh` now skips Agent Teams commands (`exec-plan-team`, `review-council-team`) since they require Claude Code. The portable `exec-plan` and `review-council` continue to be exported
- **Reduced tool-name coupling**: Agent Teams commands (`exec-plan-team`, `review-council-team`) now use intent-based language instead of hardcoded tool names, improving resilience to future API changes
- **Model selection for `exec-plan-team`**: Spec Creators use `opus` for deep reasoning; Implementers, Reviewers, and Troubleshooters use `sonnet` for fast execution

---

## [0.2.0] — 2026-03-15

### Added
- **Codex CLI installer** (`scripts/install-skills.sh`): Exports commands and skills with `andthen-`-prefixed names for Codex CLI and other agents that don't support `:` in prompt names
- **`exec-plan` — FIS existence check**: Pipeline now checks for existing FIS before creating spec tasks, skipping spec creation when one already exists — makes the pipeline resumable after partial runs
- **ElevenLabs hook enhancements**: Dynamic message generation via Claude Haiku (falls back to static messages), comma-separated voice ID support (random selection per notification), configurable model ID via `ELEVENLABS_MODEL_ID`

### Changed
- **`review` → `review-gap`**: Command renamed back to `review-gap` — the name `review` caused conflicts in some environments; all references updated across commands and documentation
- **Skills renamed** to dash-based names for cross-agent compatibility: `andthen:review-code` → `andthen-review-code`, `andthen:review-doc` → `andthen-review-doc`, `e2e-test` → `andthen-e2e-test`
- **Implementation notes** (`exec-spec`, `quick-implement`): Narrowed scope to traps, gotchas, and non-obvious patterns only — excludes information derivable from code, git history, or specs
- **ElevenLabs TTS model**: Default changed from `eleven_monolingual_v1` to `eleven_flash_v2_5`
- **Hooks docs**: Clarified settings file levels (user-level vs project-level vs local), expanded ElevenLabs setup with Claude Code `env` settings approach, free tier voice limitation note
- **README**: Updated installation section for non-Claude-Code agents to use the installer script

---

## [0.1.1] — 2026-03-13

### Added
- **Hooks**: `block-dangerous-commands.py` (blocks destructive shell commands), `notify.sh` (desktop notifications), `notify-elevenlabs.sh` (voice notifications via ElevenLabs TTS), `reinject-context.sh` (re-injects CLAUDE.md after context compaction)
- **Hooks documentation**: `hooks/README.md` with installation, configuration, and full settings example

### Fixed
- **`exec-plan`**, **`plan`**: Fixed stale `review-gap` references → `review` (command was renamed but internal references were not updated)

---

## [0.1.0] — 2026-03-13

Initial release of **AndThen** — structured workflows for agentic development.

Evolved from [cc-workflows](https://github.com/tolo/claude_code_common) (v0.12.0) with a new identity, streamlined structure, and consistent naming.

### Added

**Core Commands:**
- `clarify` — Requirements discovery — from vague idea to structured requirements
- `spec` — Feature Implementation Specification generation
- `exec-spec` — FIS execution with validation loops
- `review` — Gap analysis, code review (`--doc` for document review, `--pr` for PR review)
- `plan` — PRD creation (if needed) + story breakdown (absorbs former `prd` command)
- `exec-plan` — Agent Team pipeline execution (spec → exec-spec → review per story)
- `trade-off` — Architecture decision research with evidence-based recommendations

**Extras:**
- `quick-implement` — Fast path for small features/fixes (supports `--issue` for GitHub)
- `design-system` — Design tokens and component styles
- `wireframes` — HTML wireframes for UI planning
- `refactor` — Code improvement and simplification
- `review-council` — Multi-perspective Agent Teams review (5-7 reviewers + debate)
- `troubleshoot` — Systematic issue diagnosis and fixing

**Skills:**
- `review-code` — Code review with checklists (quality, security, architecture, UI/UX)
- `review-doc` — Document review for completeness, clarity, and technical accuracy
- `e2e-test` — End-to-end browser testing for web applications

**Agents:**
- `research-specialist` — Web research and synthesis
- `solution-architect` — Architecture design and technical decisions
- `qa-test-engineer` — Test coverage and validation
- `documentation-lookup` — External documentation retrieval
- `build-troubleshooter` — Build/test failure diagnosis
- `ui-ux-designer` — UI/UX design and prototyping
- `visual-validation-specialist` — Visual validation workflow

**Docs:**
- Development architecture guidelines
- UX/UI guidelines
- Web development guidelines
- Critical rules and guardrails
- Model and effort selection guide

### Changed (from cc-workflows)
- **Project rename**: `cc-workflows` → `andthen`
- **Repository structure**: Flat plugin layout (`plugin/` at root) replacing nested `plugins/cc-workflows/`
- **Command renames**: `review-gap` → `review`, `trade-off-analysis` → `trade-off`
- **Command consolidation**: `prd` merged into `plan`
- **Guidelines**: Moved to `docs/guidelines/` with uppercase naming convention

### Removed (from cc-workflows)
- `exec-plan-codex` — Codex CLI delegation (may return as separate integration)
- `ui-concept` — Exploratory UI design command
- `whimsy-injector` agent
- Prompt engineering guidelines (internal/meta — not part of the workflow system)
- Hooks (standalone safety scripts — separate concern, may return later)
