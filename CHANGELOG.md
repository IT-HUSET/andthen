# Changelog

All notable changes to **AndThen** are documented here.
Follows [Semantic Versioning](https://semver.org/) and [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.


---

## [0.8.7] – 2026-04-06

### Added
- **Discovery interview techniques reference** – new `plugin/references/discovery-interview-techniques.md` with probing techniques (Five Whys, Scenario Testing, Extremes, Trade-off Forcing, Laddering), creative exploration methods (What If, Reversal, HMW, Assumption Reversal, SCAMPER, Role Perspective Shift), and strategies for managing difficult interview moments. Referenced from `clarify` Phase 2
- **`review-doc` adversarial challenge phase** – new Phase 8 spawns a sub-agent to challenge review findings with document-specific questions, filtering false positives and correcting disproportionate severity before report generation
- **Document review calibration** – new `plugin/skills/review-doc/references/doc-review-calibration.md` with document-specific severity calibration, contrastive examples, proportionality guidance, and false positive traps for spec/plan/PRD reviews
- **Code review calibration** – new `plugin/skills/review-code/references/code-review-calibration.md` with code-specific severity examples, completeness/wiring calibration, and code false positive traps

### Changed
- **Review calibration restructured** – `review-calibration.md` trimmed to universal core (anti-leniency protocol, finding quality, over-leniency patterns) with generalized rules. Domain-specific calibration moved to skill-local `references/` directories. `review-gap` now references `review-code`'s calibration since both operate in the code/implementation domain
- **Common Rationalizations tables** – `exec-spec`, `spec`, and `quick-implement` now include tables of self-deception patterns agents generate to skip steps, with reality checks for each
- **`exec-plan-team` `--no-worktree` flag** – disables git worktree isolation for sequential execution on main. Simpler for plans with few parallel stories or when merge complexity is undesirable
- **`ops` STATE.md Recently Completed section** – tracks last 2 milestones with one-line summaries for cross-session continuity
- **Guidelines condensed** – `DEVELOPMENT-ARCHITECTURE-GUIDELINES.md`, `UX-UI-GUIDELINES.md`, and `WEB-DEV-GUIDELINES.md` significantly trimmed to remove content that restates standard engineering principles. Focus shifted to project-specific standards and judgment calls
- **`ops` STATE.md maintenance rules tightened** – ~60 line target (down from ~100), Session Continuity Notes capped at 5 (down from 10), completed stories actively pruned, resolved blockers auto-removed
- **`project-state-templates.md` updated** – STATE.md template aligned with new maintenance rules: Recently Completed section, tighter size guidance, inline documentation for each section's pruning policy
- **`notify-elevenlabs.sh` async and audio improvements** – TTS/playback detached to background process to avoid hook timeout kills, switched from MP3 to PCM 44100 WAV to eliminate afplay frame-padding clipping

---

## [0.8.4] – 2026-03-31

### Added
- **`plan` GitHub issue input** – `plan` now accepts `--issue <number>` to fetch a GitHub issue via `gh issue view` and use it as requirements input for PRD and plan creation. Issue-sourced plans use `issue-{number}-{feature-name}/` output directory naming. Added USAGE section with examples
- **`clarify` GitHub issue input** – `clarify` now accepts `--issue <number>` to fetch a GitHub issue and use it as the starting point for requirements discovery. Previously mentioned "GitHub issue URL" in argument-hint but had no workflow implementation. Added USAGE section with examples

---

## [0.8.6] – 2026-04-01

### Added
- **Monorepo support for `init` and `map-codebase`** – both skills now detect workspace structures (pnpm, yarn, npm, Cargo, Go, nx, turbo, lerna) and adapt accordingly. `init` offers to generate per-sub-project `CLAUDE.md` files with sub-project-specific commands and conventions. `map-codebase` passes sub-project lists to all analysis sub-agents for workspace-aware output
- **`KEY_DEVELOPMENT_COMMANDS.md` template** – new template in `project-state-templates.md` for documenting dev, test, build, and deploy commands. Includes monorepo-aware per-sub-project command sections
- **`map-codebase` command discovery** – new sub-agent (2e) auto-discovers development commands from package.json scripts, Makefiles, Taskfiles, CI configs, and README files. Pre-fills the KEY_DEVELOPMENT_COMMANDS template with actual values
- **`init` offers KEY_DEVELOPMENT_COMMANDS.md** – added to "Core (recommended)" optional documents

### Fixed
- **`CLAUDE.template.md` dangling reference** – the "Key Development Commands" section referenced `docs/rules/KEY_DEVELOPMENT_COMMANDS.md` but the file had no template and wasn't in the Project Document Index. Now properly referenced at `docs/KEY_DEVELOPMENT_COMMANDS.md` with a Document Index row
- **`code-simplifier` agent name disambiguation** – `exec-spec`, `quick-implement`, and `refactor` skills now explicitly note to use the full agent name `code-simplifier:code-simplifier` to prevent shortening

---

## [0.8.5] – 2026-03-31

### Fixed
- **`init` missing `map-codebase` suggestion in partial setup path** – when CLAUDE.md already existed (partial setup), `init` never offered to run `map-codebase` for auto-generating architecture, stack, and conventions docs. The suggestion only existed in the brownfield path (no CLAUDE.md). Now both partial setup and brownfield paths offer `map-codebase` when relevant docs are missing

### Changed
- **READMEs clarify `init` / `map-codebase` relationship** – `init` is the single entry point for all project types; `map-codebase` is delegated to by `init` or run standalone. Updated skill table descriptions and Setup section

---

## [0.8.3] – 2026-03-31

### Added
- **Review evaluator calibration** – new `plugin/references/review-calibration.md` shared reference with anti-leniency protocol, contrastive severity examples (IS/is NOT Critical/High), over-lenient review scenario, finding quality calibration, and false positive traps. Loaded by both `review-gap` and `review-code`
- **Adversarial Challenger for `review-gap`** – new Step 6 spawns a sub-agent with fresh context to challenge all findings (VALIDATED/DOWNGRADED/WITHDRAWN verdicts). Counters self-evaluation bias where evaluators identify issues then rationalize approval. Includes severity mapping from `review-code`'s 3-tier to `review-gap`'s 4-tier system
- **Dimensional scoring with hard thresholds for `review-gap`** – new Step 7 scores Functionality (>=7), Completeness (>=9), and Wiring (>=8) on validated findings only. Any dimension below threshold = FAIL, no negotiation. Produces structured verdict table in Executive Summary for `exec-plan` to parse

### Fixed
- **Stub detection regex** – replaced wildcard `not.implemented` pattern with precise `not[_ -]implemented|notImplemented` in `verification-patterns.md` and `review-gap`

---

## [0.8.2] – 2026-03-29

### Changed
- **`clarify` requirements vs. implementation boundary** – added explicit guardrails preventing clarify from drifting into implementation-level decisions (architecture patterns, library choices, data storage strategies). New "Requirements vs. Implementation Boundary" section in GOTCHAS with concrete DO/DO NOT lists, scoped design space decomposition to user-visible/product-level dimensions only, and added inline scope guard at the step where drift occurs
- **`spec` outcome-focused tasks** – tasks now describe what must be TRUE when done, not what code to write. New gotcha against describing detailed code changes. Reduced spec size target from 300–500 to 200–400 lines. Added over-researching gotcha to keep research phases minimal. Authoring instructions (Grouping Constraints, Implementation Notes, Verification Criteria guidance) moved from FIS template into spec skill – template now only contains sections that appear in generated output
- **FIS template revision** – "Intent over Implementation" added as core principle #1. Example tasks rewritten as outcome-focused. New "Health Metrics" section for anti-regression baselines. New "Agent Decision Authority" section for scope boundary clarity. Verification criteria simplified from 4-dimension checklist to functional checks. Removed authoring meta-instructions that don't belong in generated output
- **Prompt engineering guidelines** – added `docs/prompt-guidelines/` with guidelines for prompt engineering work, including Claude-specific and GPT-specific supplements. Referenced from CLAUDE.md
- **Guardrails** – added en dash (–) preference over em dash (—) rule

---

## [0.8.1] – 2026-03-24

### Changed
- **`exec-plan` / `exec-plan-team` configurable review modes** – both plan execution skills now accept `--review-mode per-story|none|full-plan`. Default behavior remains per-story `review-gap`; `none` skips automated review for manual user follow-up; `full-plan` skips per-story review and runs a single final `review-gap` against `plan.md` with remediation

---

## [0.8.0] – 2026-03-24

### Added
- **`spec-plan` skill** – new skill that batch-creates FIS specs for all stories in a plan using parallel sub-agents (opus model) with wave-ordered execution and configurable concurrency (default 5, max 10). Includes a **cross-cutting review** step that detects inter-story issues: overlapping scope, inconsistent ADRs, missing integration seams, dependency gaps, naming inconsistencies, and duplicate work. Can be used standalone (enables human review gate before execution) or delegated by `exec-plan` / `exec-plan-team`
- **STATE.md lifecycle integration** – `exec-plan`, `exec-plan-team`, `exec-spec`, `plan`, `triage`, and `quick-implement` now read and/or write STATE.md via `andthen:ops`. Previously, `ops` had Read State and Update State operations but no skill triggered them — STATE.md was effectively orphaned
- **`exec-plan` / `exec-plan-team` full state tracking** – read STATE.md at start for session continuity context; update phase/status at each phase transition; update active stories after each story completes; write blockers on failure; write session continuity note at completion or interruption
- **`exec-spec` active-story signaling** – sets active story to "In Progress" at implementation start (Step 1) and marks it Done at completion (new Step 5d), enabling faster session recovery if interrupted
- **`plan` state context and initialization** – reads STATE.md during requirements analysis for current phase/blockers/decisions context; initializes STATE.md with Phase 1 after plan creation; suggests STATE.md in follow-up actions
- **`triage` bidirectional blocker management** – reads STATE.md for investigation context (Step 1.3); adds discovered Critical/High issues as blockers (Step 3.4); removes resolved blockers and restores "On Track" status after fixes (Step 5.4)
- **`quick-implement` session note** – adds lightweight completion note to STATE.md
- **`ops` new fields** – `status` (On Track / At Risk / Blocked), `decision` (timestamped entry), `active-story` expanded to support table rows with status/FIS columns, `blocker remove` for clearing resolved blockers
- **`ops` maintenance rules** – automatic trimming on every write: remove Done rows from Active Stories, keep last 10 Session Continuity Notes and Recent Decisions

### Changed
- **`exec-plan` delegates spec creation to `spec-plan`** – per-story pipeline simplified from 3 stages (spec → exec-spec → review-gap) to 2 stages (exec-spec → review-gap). All specs for each phase are pre-generated via `andthen:spec-plan --phase {N}` before implementation begins, replacing inline JIT spec creation. Sub-agents now use `model: "sonnet"` only (spec quality handled by spec-plan's opus sub-agents)
- **`exec-plan-team` delegates spec creation to `spec-plan`** – Step 3 (Generate Specs) replaced from inline parallel sub-agent spawning to a single `andthen:spec-plan --phase {N}` delegation. Eliminates duplicated spec-generation logic between exec-plan and exec-plan-team
- **`ops` STATE.md format reconciled** with `templates/project-state-templates.md` – replaced divergent `## Current State` bullet format with canonical `## Current Phase` / `## Active Stories` table structure matching what `init` creates
- **STATE.md template** – added `Last Updated` timestamp field

### Fixed
- **`spec` artifact chaining from `clarify`** – `spec` Step 0 now explicitly detects `requirements-clarification.md` in a directory argument (output from `andthen:clarify`), consuming clarified requirements, design decisions, edge cases, and wireframes as the feature request. Skips redundant discovery phases. Previously, the `clarify → spec` handoff in the single-feature workflow had no explicit contract – `plan` had artifact chaining but `spec` did not
- **`spec` FIS output co-location** – FIS files are now co-located with their input artifacts: directory input → FIS inside directory (e.g. `docs/specs/data-export/data-export.md`), plan story → FIS in plan directory. Previously, FIS was always written to the specs root regardless of input source, breaking the feature-directory convention used by `clarify` and `plan`
- **`exec-plan-team` race condition prevention** – added explicit gotcha that only the orchestrator writes STATE.md; parallel implementers and reviewers must not touch it



---

## [0.7.3] – 2026-03-22

### Changed
- **Cross-skill references standardized** – all 12 skill files with cross-references now use consistent, explicit patterns:
  - Bare skill names (`plan`, `spec`, `design-system`) replaced with fully qualified `andthen:` prefix
  - Ambiguous references now include explicit "skill" or "agent" noun (e.g., "run the `andthen:spec` skill", "delegate to the `andthen:build-troubleshooter` agent")
  - User-facing follow-up sections now include `/` and `$` invocation examples (e.g., `/andthen:spec story S01 of path/to/plan.md`)
  - Sub-agent prompt templates standardized to "Run the `andthen:xxx` skill" pattern
  - `review-doc` "command" → "skill" terminology fix

---

## [0.7.2] – 2026-03-22

### Added
- **Execution groups in spec and exec-spec** – FIS template and spec skill now organize tasks into execution groups (clusters of related tasks executed by a single sub-agent). exec-spec refactored from per-task to per-group delegation with Group Input/Result Templates and inter-group context relay
- **UI design contract gate** (`exec-spec` Step 1.7) – auto-generates a UI-SPEC.md design contract when FIS contains frontend work, sourced from FIS, project design system, and UX guidelines
- **Post-Completion learnings** in `exec-plan` and `exec-plan-team` – both plan execution skills now update LEARNINGS.md after all phases complete, capturing cross-story insights
- **Helper scripts** in `exec-plan-team` – added `check-stubs.sh`, `check-wiring.sh`, `verify-implementation.sh` references (consistent with other execution skills)

### Changed
- **Status updates are now REQUIRED GATES** – `exec-spec` (5b, 5c), `exec-plan` (2c), `exec-plan-team` (6f) all enforce plan/FIS status updates as gate conditions, not optional post-completion cleanup. Addresses observed failure mode where agents skip end-of-document instructions under context exhaustion
- **ops fork context documented for callers** – all three execution skills now include re-read verification after `andthen:ops` invocation (ops runs in fork context; file modifications may not be visible in caller's state)
- **ops uses Project Document Index** for STATE.md path resolution instead of hardcoded `docs/STATE.md`
- **ops checkbox verification clarified** – now checks evidence of completion rather than re-running full 4-dimension verification (avoids redundant work when called by exec-spec)
- **Severity tier mapping** in `exec-spec` TV04 – explicit mapping from review-code tiers (CRITICAL/HIGH/SUGGESTIONS) to remediation tiers (CRITICAL/HIGH/MEDIUM)
- **map-codebase reads project learnings** – added LEARNINGS.md reading instruction for contextualizing codebase analysis

### Fixed
- **exec-plan missing `check-wiring.sh`** in helper scripts section (consistency with exec-spec)
- **Gotcha added** to all three execution skills warning about status updates being dropped under context exhaustion

---

## [0.7.1] – 2026-03-21

### Changed
- **Review reports co-locate with targets** – all 5 review skills (`review-code`, `review-gap`, `review-doc`, `review-council`, `review-council-team`) now place reports alongside the review target instead of always under `.agent_temp/reviews/`. Resolution priority: spec/FIS directory (if related) → target directory → Agent Temp fallback
- **Configurable Agent Temp directory** – added `Agent Temp` row to the Project Document Index template, allowing projects to override the default `.agent_temp/` path for temporary agent output (reviews, research, QA)

### Fixed
- **BREAKING: Export prefix reverted from `andthen.` to `andthen-`** – The dot in `andthen.` was incompatible with Codex CLI's `$` sigil parser regex (`[a-zA-Z0-9_\-:]`), which does not include `.`. This caused explicit `<skill>` injection to silently fail for all 22 exported skills, forcing the model to read SKILL.md files from disk via tool calls (weakest invocation path). Empirically verified: zero `<skill>` injections occurred across 784 Codex sessions with dot-prefixed names. Reverting to hyphen (`andthen-`) restores Codex's explicit skill injection. Users must re-run `./scripts/install-skills.sh` after upgrading.
- **Research report added** – `docs/research/codex-skill-instruction-following.md` documents the full root cause analysis comparing Codex CLI and Claude Code skill injection architectures

---

## [0.7.0] – 2026-03-20

### Added
- **Gotchas sections** in all 22 SKILL.md files – fixed operational knowledge surfaced near the top of each skill (2-5 entries per skill covering known failure modes)
- **LEARNINGS.md integration** – 5 skills now read project learnings at start (`exec-spec`, `triage`, `spec`, `review-gap`, `review-code`); 3 skills append significant findings after execution (`triage`, `review-gap`, `exec-spec`)
- **Orchestrator pattern** for context-heavy skills – `review-code`, `triage`, and `spec` now delegate heavy work to sub-agents to preserve workflow context; `review-gap` orchestrator enhanced with stub/wiring delegation
- **Portable shared scripts** in `plugin/scripts/` – `check-stubs.sh`, `check-wiring.sh`, `run-security-scan.sh`, `verify-implementation.sh` for automated verification (used by review-gap, exec-spec, exec-plan, review-code)

### Changed
- **Unified `andthen:` namespace** – removed `name:` frontmatter override from all 22 SKILL.md files. Skills now use the natural plugin namespace (`andthen:<skill>`), consistent with agents (`andthen:<agent>`). The portable `andthen.` prefix is now only used when exporting for non-Claude Code agents via `install-skills.sh`
- **`install-skills.sh` rewrites skill references** – exported skills have `andthen:` cross-references rewritten to the portable `andthen.` prefix, alongside the existing reference path rewriting
- **CLAUDE.md updated** – added "How Skills Work" section (Project Document Index discovery, skill anatomy, shared references, external plugin dependencies), expanded project structure, updated skill invocation docs
- **Descriptions as triggers** – 10 skills rewritten with natural-language trigger phrases for better model matching (`exec-spec`, `review-gap`, `review-council`, `clarify`, `spec`, `trade-off`, `triage`, `map-codebase`, `e2e-test`, `ops`)
- **Reduced railroading** – `plan` requirements discovery condensed from 20+ individual questions to intent + constraints format; `triage` 5 Whys analysis condensed to single directive

### Fixed
- **Removed `context: fork` from orchestrator skills** – `review-code` and `e2e-test` no longer use `context: fork` because forked sub-agents cannot spawn nested sub-agents, which breaks the orchestrator pattern. `ops` and `review-doc` retain `context: fork` (no sub-agent needs)
- **Helper scripts made concurrency-safe** – all scripts now use `mktemp` with cleanup traps instead of fixed `/tmp` paths; eliminates race conditions under parallel sub-agent execution
- **`check-wiring.sh` inspects dirty worktrees** – now checks staged, unstaged, and untracked files (not just committed diffs); supports both file and directory path inputs
- **`verify-implementation.sh` strict exit codes** – stub and wiring findings now cause non-zero exit (previously treated as warnings); delegates to `check-stubs.sh` when available; removed unused `--base-branch` option
- **`check-stubs.sh` excludes docs by default** – markdown, templates, and documentation directories excluded to reduce false positives; `--include-docs` flag for full scan
- **Installer exports shared scripts** – `install-skills.sh` now copies `plugin/scripts/` alongside `plugin/references/` and rewrites `${CLAUDE_PLUGIN_ROOT}/scripts/` and `${CLAUDE_PLUGIN_ROOT}/references/` paths in all exported `.md` files (including nested subdirectories)
- **Installer filters `.DS_Store`** – macOS metadata files no longer included in exported bundles
- **CLAUDE.md skill anatomy corrected** – removed stale `name` reference from frontmatter documentation

---

## [0.6.4] – 2026-03-20

### Changed
- **`review-gap` clarified as implementation review** – description, input interpretation, and workflow now explicitly frame the skill as comparing current code/worktree against requirements baselines. New Step 0 ("Resolve Review Target") locates the implementation target before analysis begins. Added concrete examples showing correct usage vs. `review-doc`. Multi-repo workspace resolution with sensible fallback when no workspace metadata exists.

---

## [0.6.3] – 2026-03-19

### Changed
- **Plan skill: PRD responsibility explicit** – description, title, and OpenAI agent display name now clearly state PRD creation as a primary responsibility (not just an implicit prerequisite)
- **"AndThen -" prefix on all OpenAI display names** – consistent `"AndThen - <Skill>"` branding across all `openai.yaml` agent configs
- **`review-gap` input interpretation guardrails** – new "Input Interpretation" section clarifies that documents passed as arguments are comparison baselines (requirements sources), not the review target. Stops early if no implementation exists to compare against
- **Workflow diagrams corrected** – `review-gap --doc` → `review-doc` in README and plugin README pipeline diagrams
- **Model effort selection guide** – updated `review-gap` description to reflect its focused scope (gap analysis against requirements, no longer doc/PR review modes)
- **Triage OpenAI agent metadata** – display name and description updated to match the skill's current name and scope (`"Triage & Fix Issues"`)
- **CLAUDE.template.md** – expanded guideline trigger wording to include "code exploration, architecture and solution design"

### Fixed
- **`allow_implicit_invocation: true` policy** added to OpenAI agent skill configs – this is a workaround for an apparent bug in Codex.
- **Argument-hint quoting** – all `argument-hint` values in SKILL.md frontmatter now properly quoted
- **`install-skills.sh` reference path rewriting** – installed skills now rewrite `plugin/references/` paths to sibling `<prefix>references/` paths so references resolve correctly outside the repo

---

## [0.6.2] – 2026-03-17

### Added
- **Semgrep integration in security reviews**: `review-code` Security Review phase now includes automated Semgrep scanning via Claude Code plugin (`semgrep/mcp-marketplace`), CLI, or MCP tools – running in parallel with `/security-review`. All tools optional; graceful fallback to manual checklist review
- **Automated Scanning section in Security Review Checklist**: New checklist section with Semgrep triage steps, config recommendations by focus area (`p/security-audit`, `p/owasp-top-ten`, `p/secrets`), and other tool references
- **Security Sentinel uses Semgrep**: `review-council` and `review-council-team` Security Sentinel role now runs Semgrep scans on changed files when available

---

## [0.6.1] – 2026-03-17

### Changed
- **`init` offers UBIQUITOUS_LANGUAGE.md**: Added domain glossary to the optional document checklist under a new "Domain" category, with a hint to use `andthen.ubiquitous-language` for richer generation

---

## [0.6.0] – 2026-03-17

### Added
- **Ubiquitous Language skill** (`ubiquitous-language`): Extract and maintain a domain glossary (`UBIQUITOUS_LANGUAGE.md`) from codebase and documentation. Supports `--update` mode for incremental glossary maintenance. Integrates with DDD principles throughout the pipeline
- **UL pipeline integration**: Domain language awareness woven into `clarify` (term extraction), `spec` (canonical terms in FIS), `plan` (canonical terms in stories), `exec-spec` (sub-agents receive UL context, TV01 checks terminology), `review-code` (domain language checklist), and `review-gap` (terminology drift detection)
- **Domain Language Review Checklist** (`review-code`): New `DOMAIN-LANGUAGE-REVIEW-CHECKLIST.md` covering terminology consistency, domain model alignment, and new term detection
- **"Design It Twice" in trade-off** (`trade-off`): New optional Phase 1.5 spawns 3+ parallel sub-agents with contrasting architectural constraints to generate radically different designs before evaluation. Synthesizes findings in prose, not tables
- **Triage investigation mode** (`triage`): `--plan-only` flag stops after root cause analysis and outputs a structured fix plan instead of implementing fixes. `--to-issue` publishes the plan as a GitHub issue
- **TDD Lite** (`spec`, `exec-spec`): FIS template gains "Test-Implementation Pairing" section mapping tests to implementation tasks. `exec-spec` Step 2 directs sub-agents to write paired tests before implementing (red-green rhythm by structure)
- **Vertical slicing** (`plan`, `spec`): "Vertical" added as first story principle – stories cut through all layers end-to-end. Phase template restructured around tracer-bullet first phase. FIS template adds vertical-slice task ordering guidance
- **GitHub issue output** (`spec`, `plan`, `review-gap`, `review-code`): `--to-issue` flag publishes skill output as a GitHub issue. `review-gap` and `review-code` also support `--to-pr <number>` for PR comments
- **`UBIQUITOUS_LANGUAGE.md` template**: Added to project Document Index and `project-state-templates.md` as a standard project file
- **DDD guidelines expanded**: "Ubiquitous Language in Practice" subsection added to `DEVELOPMENT-ARCHITECTURE-GUIDELINES.md` with actionable guidance on domain naming, glossary maintenance, and ambiguity resolution

### Changed
- **Extras prefix removed**: All `extras-` prefixed skills renamed – `extras-quick-implement` → `quick-implement`, `extras-design-system` → `design-system`, `extras-wireframes` → `wireframes`, `extras-refactor` → `refactor`, `extras-review-council` → `review-council`, `extras-review-council-team` → `review-council-team`, `extras-map-codebase` → `map-codebase`
- **`extras-troubleshoot` → `triage`**: Renamed with both prefix removal and base name change to better reflect systematic investigation capability
- **Triage skill description**: Updated to mention investigation, diagnosis, and fix modes
- **Portable `andthen.` skill prefix**: All skills now use `name: andthen.<skill>` in SKILL.md frontmatter (e.g., `andthen.spec`, `andthen.review-code`). Leverages Claude Code bug [#22063](https://github.com/anthropics/claude-code/issues/22063) – the `name:` field bypasses the plugin namespace, registering skills as `/andthen.spec` (portable dot notation) instead of `/andthen:andthen.spec`. Cross-references within skills use `andthen.<skill>` for skills and `andthen:<agent>` for agents (Claude Code-specific)
- **`install-codex.sh` → `install-skills.sh`**: Renamed for clarity. Default prefix changed from `andthen-` to `andthen.` to match the new naming convention
- **Invocation docs updated**: Skills invoked as `/andthen.<skill>` in Claude Code, `$andthen.<skill>` or `/andthen.<skill>` in Codex and other agents

---

## [0.5.0] – 2026-03-17

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

## [0.4.0] – 2026-03-16

### Added
- **Goal-backward planning** (`plan`): New "Goal-Backward Analysis" step works backward from desired outcomes before defining stories – produces Must-be-TRUE statements that become primary acceptance criteria
- **Wave-based parallelization** (`plan`, `exec-plan`, `exec-plan-team`): Stories are pre-assigned to execution waves (W1, W2, W3...) during planning; execution commands consume wave assignments for cleaner parallel orchestration without runtime dependency analysis
- **Deep verification – Nyquist Rule** (`spec`, `exec-spec`, `review-gap`): Verification now checks 4 dimensions (Exists, Substantive, Wired, Functional) instead of just existence; stub detection and wiring checks catch TODOs, placeholders, and unconnected components
- **Verification patterns reference** (`plugin/references/verification-patterns.md`): Comprehensive reference with stub detection patterns, wiring check commands, and the Nyquist verification principle
- **`init` command**: Interactive project setup – detects current state (new project, partial setup, brownfield) and fills gaps non-destructively. Generates CLAUDE.md from template, creates selected document types, copies guidelines, and integrates with `map-codebase` for existing codebases
- **`map-codebase`** (extras): Brownfield codebase analysis command – spawns parallel sub-agents to produce STACK.md, ARCHITECTURE.md, CONVENTIONS.md, and a discovered requirements document that feeds directly into `/andthen:plan`
- **`andthen-ops` skill**: Deterministic operations for state management (STATE.md, plan.md status, FIS checkboxes), git conventions (commit messages, branch naming, changelog entries), and progress tracking (summary, stale detection)
- **UI Design Contract gate** (`exec-spec`): New Step 1.7 auto-generates a UI-SPEC.md design contract (spacing, typography, colors, components, breakpoints) when frontend work is detected, ensuring visual consistency across sub-agents
- **Project state templates** (`templates/project-state-templates.md`): Starter templates for STATE.md, PRODUCT-BACKLOG.md, ROADMAP.md, ARCHITECTURE.md, CONVENTIONS.md, LEARNINGS.md, and STACK.md
- **Project Document Index** (`templates/CLAUDE.template.md`): Seven new optional document rows – State, Product Backlog, Roadmap, Architecture, Conventions, Learnings, Stack

### Changed
- **`implementation-notes.md` → `LEARNINGS.md`**: Renamed and broadened scope – now captures domain knowledge, procedural knowledge, and error patterns (with deterministic vs infrastructure distinction) alongside implementation traps. Includes self-maintenance guidance (review, merge, prune). Topic-based organization instead of chronological
- **Story Catalog format** (`plan`): Table now includes a Wave column for pre-computed execution wave assignments
- **Codex installer**: Now also copies `plugin/references/` alongside prompts so non-Claude-Code agents can access verification patterns

---

## [0.3.1] – 2026-03-16

### Improved
- **`plan` – artifact chaining from `clarify`**: Plan command now detects `requirements-clarification.md` (from `/andthen:clarify`) and draft PRDs (`prd-draft.md`) in the input directory, using them as the basis for PRD creation instead of re-running full discovery
- **`plan` – new Step 1c** (PRD Creation from Existing Artifacts): Assesses coverage from prior artifacts, conducts only targeted gap-filling for genuinely missing information, and preserves existing decisions/rationale when structuring the PRD
- **`clarify` – improved handoff guidance**: Follow-up actions now explicitly guide users toward `/andthen:plan <output-directory>` for seamless artifact handoff
- **Interview guardrails** (`clarify`, `plan`): Strengthened STOP-and-WAIT instructions in discovery interviews to prevent agents from assuming answers or proceeding without user input

---

## [0.3.0] – 2026-03-15

### Added
- **Portable `exec-plan`**: New version that works across all coding agents (Claude Code, Codex CLI, Aider, Cursor, etc.) using sub-agents with sequential fallback – no longer requires Agent Teams
- **Portable `review-council`**: New version using a three-phase sub-agent pipeline (specialist reviews → Devil's Advocate challenge → Synthesis review) instead of requiring real-time Agent Teams debate
- **Agent Teams variants**: Previous Agent Teams implementations preserved as `exec-plan-team` and `review-council-team` for users who want enhanced parallelism with inter-agent coordination
- **Testing Strategy in FIS template** (`spec`): New section in the FIS template for defining test scope, key test scenarios, edge cases, and test pattern references – gives the testing agent concrete direction during `exec-spec` instead of inventing test cases from scratch
- **Test scaffolding step** (`exec-spec`): New optional Step 1.5 writes failing test skeletons from the FIS Testing Strategy before implementation begins, enabling a TDD-style workflow where tests become acceptance gates for implementation tasks
- **Structured remediation loop** (`exec-spec`): TV04 rewritten as a triage → fix → re-validate cycle that only re-runs affected validation levels, with a 3-cycle hard cap before escalating to the user
- **Review council callout** (`exec-spec`): Tip in TV04 suggesting `review-council` for high-stakes features (auth, payments, data integrity)

### Changed
- **`exec-plan` is now portable**: The default `exec-plan` command uses sub-agents (if available) with sequential fallback – works on any agent. The former Agent Teams version is now `exec-plan-team`
- **`review-council` is now portable**: The default `review-council` command uses parallel sub-agents for reviews and sequential adversarial debate phases. The former Agent Teams version is now `review-council-team`
- **Migration note**: Users of the previous `exec-plan` (which required Agent Teams) should use `exec-plan-team` for equivalent behavior. The new `exec-plan` works across all agents but uses sub-agents instead of Agent Teams coordination
- **Codex installer**: `install-skills.sh` now skips Agent Teams commands (`exec-plan-team`, `review-council-team`) since they require Claude Code. The portable `exec-plan` and `review-council` continue to be exported
- **Reduced tool-name coupling**: Agent Teams commands (`exec-plan-team`, `review-council-team`) now use intent-based language instead of hardcoded tool names, improving resilience to future API changes
- **Model selection for `exec-plan-team`**: Spec Creators use `opus` for deep reasoning; Implementers, Reviewers, and Troubleshooters use `sonnet` for fast execution

---

## [0.2.0] – 2026-03-15

### Added
- **Codex CLI installer** (`scripts/install-skills.sh`): Exports commands and skills with `andthen-`-prefixed names for Codex CLI and other agents that don't support `:` in prompt names
- **`exec-plan` – FIS existence check**: Pipeline now checks for existing FIS before creating spec tasks, skipping spec creation when one already exists – makes the pipeline resumable after partial runs
- **ElevenLabs hook enhancements**: Dynamic message generation via Claude Haiku (falls back to static messages), comma-separated voice ID support (random selection per notification), configurable model ID via `ELEVENLABS_MODEL_ID`

### Changed
- **`review` → `review-gap`**: Command renamed back to `review-gap` – the name `review` caused conflicts in some environments; all references updated across commands and documentation
- **Skills renamed** to dash-based names for cross-agent compatibility: `andthen:review-code` → `andthen-review-code`, `andthen:review-doc` → `andthen-review-doc`, `e2e-test` → `andthen-e2e-test`
- **Implementation notes** (`exec-spec`, `quick-implement`): Narrowed scope to traps, gotchas, and non-obvious patterns only – excludes information derivable from code, git history, or specs
- **ElevenLabs TTS model**: Default changed from `eleven_monolingual_v1` to `eleven_flash_v2_5`
- **Hooks docs**: Clarified settings file levels (user-level vs project-level vs local), expanded ElevenLabs setup with Claude Code `env` settings approach, free tier voice limitation note
- **README**: Updated installation section for non-Claude-Code agents to use the installer script

---

## [0.1.1] – 2026-03-13

### Added
- **Hooks**: `block-dangerous-commands.py` (blocks destructive shell commands), `notify.sh` (desktop notifications), `notify-elevenlabs.sh` (voice notifications via ElevenLabs TTS), `reinject-context.sh` (re-injects CLAUDE.md after context compaction)
- **Hooks documentation**: `hooks/README.md` with installation, configuration, and full settings example

### Fixed
- **`exec-plan`**, **`plan`**: Fixed stale `review-gap` references → `review` (command was renamed but internal references were not updated)

---

## [0.1.0] – 2026-03-13

Initial release of **AndThen** – structured workflows for agentic development.

Evolved from [cc-workflows](https://github.com/tolo/claude_code_common) (v0.12.0) with a new identity, streamlined structure, and consistent naming.

### Added

**Core Commands:**
- `clarify` – Requirements discovery – from vague idea to structured requirements
- `spec` – Feature Implementation Specification generation
- `exec-spec` – FIS execution with validation loops
- `review` – Gap analysis, code review (`--doc` for document review, `--pr` for PR review)
- `plan` – PRD creation (if needed) + story breakdown (absorbs former `prd` command)
- `exec-plan` – Agent Team pipeline execution (spec → exec-spec → review per story)
- `trade-off` – Architecture decision research with evidence-based recommendations

**Extras:**
- `quick-implement` – Fast path for small features/fixes (supports `--issue` for GitHub)
- `design-system` – Design tokens and component styles
- `wireframes` – HTML wireframes for UI planning
- `refactor` – Code improvement and simplification
- `review-council` – Multi-perspective Agent Teams review (5-7 reviewers + debate)
- `troubleshoot` – Systematic issue diagnosis and fixing

**Skills:**
- `review-code` – Code review with checklists (quality, security, architecture, UI/UX)
- `review-doc` – Document review for completeness, clarity, and technical accuracy
- `e2e-test` – End-to-end browser testing for web applications

**Agents:**
- `research-specialist` – Web research and synthesis
- `solution-architect` – Architecture design and technical decisions
- `qa-test-engineer` – Test coverage and validation
- `documentation-lookup` – External documentation retrieval
- `build-troubleshooter` – Build/test failure diagnosis
- `ui-ux-designer` – UI/UX design and prototyping
- `visual-validation-specialist` – Visual validation workflow

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
- `exec-plan-codex` – Codex CLI delegation (may return as separate integration)
- `ui-concept` – Exploratory UI design command
- `whimsy-injector` agent
- Prompt engineering guidelines (internal/meta – not part of the workflow system)
- Hooks (standalone safety scripts – separate concern, may return later)
