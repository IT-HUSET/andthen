# Changelog

All notable changes to **AndThen** are documented here.
Follows [Semantic Versioning](https://semver.org/) and [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.

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
