# Changelog

All notable changes to **AndThen** are documented here.
Follows [Semantic Versioning](https://semver.org/) and [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.

---

## [1.2.1] — 2026-03-16

### Improved
- **`plan` — artifact chaining from `clarify`**: Plan command now detects `requirements-clarification.md` (from `/andthen:clarify`) and draft PRDs (`prd-draft.md`) in the input directory, using them as the basis for PRD creation instead of re-running full discovery
- **`plan` — new Step 1c** (PRD Creation from Existing Artifacts): Assesses coverage from prior artifacts, conducts only targeted gap-filling for genuinely missing information, and preserves existing decisions/rationale when structuring the PRD
- **`clarify` — improved handoff guidance**: Follow-up actions now explicitly guide users toward `/andthen:plan <output-directory>` for seamless artifact handoff
- **Interview guardrails** (`clarify`, `plan`): Strengthened STOP-and-WAIT instructions in discovery interviews to prevent agents from assuming answers or proceeding without user input

---

## [1.2.0] — 2026-03-15

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
- **Codex installer**: `install-codex.sh` now skips Agent Teams commands (`exec-plan-team`, `review-council-team`) since they require Claude Code. The portable `exec-plan` and `review-council` continue to be exported
- **Reduced tool-name coupling**: Agent Teams commands (`exec-plan-team`, `review-council-team`) now use intent-based language instead of hardcoded tool names, improving resilience to future API changes
- **Model selection for `exec-plan-team`**: Spec Creators use `opus` for deep reasoning; Implementers, Reviewers, and Troubleshooters use `sonnet` for fast execution

---

## [1.1.0] — 2026-03-15

### Added
- **Codex CLI installer** (`scripts/install-codex.sh`): Exports commands and skills with `andthen-`-prefixed names for Codex CLI and other agents that don't support `:` in prompt names
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

## [1.0.1] — 2026-03-13

### Added
- **Hooks**: `block-dangerous-commands.py` (blocks destructive shell commands), `notify.sh` (desktop notifications), `notify-elevenlabs.sh` (voice notifications via ElevenLabs TTS), `reinject-context.sh` (re-injects CLAUDE.md after context compaction)
- **Hooks documentation**: `hooks/README.md` with installation, configuration, and full settings example

### Fixed
- **`exec-plan`**, **`plan`**: Fixed stale `review-gap` references → `review` (command was renamed but internal references were not updated)

---

## [1.0.0] — 2026-03-13

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
