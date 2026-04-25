# Changelog

All notable changes to **AndThen** are documented here, in a brief and concise format.
Follows [Semantic Versioning](https://semver.org/) and [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.


---

## [0.14.3] – 2026-04-24

### Added
- **`--claude-user` in `scripts/install-skills.sh`** – opt-in alternative install path that writes skills to `~/.claude/skills/andthen-*/` and agents to `~/.claude/agents/andthen-*.md` with `/andthen-<name>` slash-command invocation, giving naming parity with Codex for users who want one convention across both runtimes instead of the Claude Code plugin's `andthen:<name>` form. Warns when the `andthen` plugin is already installed, prefixes agent frontmatter `name:` so Task-tool resolution works, and fails loudly on malformed agent sources rather than silently installing a broken file.

### Changed
- **FIS cross-document reference precision** – Template gains `Required Context` (load-bearing spans inlined verbatim, source-pinned with `<!-- source: path#anchor -->` and `<!-- extracted: ... -->`) and `Deeper Context` (anchored pointers), replacing the old undifferentiated `Documentation & References` table for doc-type refs and forcing authoring-time resolution instead of vague "see plan.md" punts. Plan-batch per-story sub-agents inherit pre-validated PRD anchors via a curated "PRD proxy" in technical research; FIS size envelope raised to 200–500 lines (oversize >700) to accommodate inlining.
- **Doc-review routes to `andthen:clarify` vs `andthen:remediate-findings`** – The `andthen:review` skill in `--mode doc` (and the doc sub-pass of `--mode mixed`) now classifies findings into a requirement-gap cluster (→ the `andthen:clarify` skill) or a defect cluster (→ the `andthen:remediate-findings` skill) via an explicit document-maturity signal and first-fires-wins pattern precedence, recording the routing decision in a new `Recommended Next Action` report section. Under `AUTO_MODE=off` the skill offers to invoke the `andthen:clarify` skill inline against the listed gaps; under `AUTO_MODE=on` the recommendation is report-only — the `andthen:clarify` skill is interactive by nature and never runs headless.
- **`andthen:clarify` requirement-vs-implementation boundary made effect-based** – the boundary now passes the **load-bearing test** (does the answer change user-visible behavior, scope, or acceptance criteria?) instead of a categorical "technical = downstream" rule, letting questions like offline support, sync semantics, user-visible auth model, data residency, and externally-visible provider choice into scope while still deferring library/caching/internal-API/DB/deployment choices to the `andthen:spec` skill and the `andthen:architecture` skill (`--mode trade-off`). Scope guard and the `design-tree.md` "In `clarify`" bullet now defer to one canonical example list to prevent drift, and the non-developer-stakeholder litmus is repositioned as a tiebreaker qualified to "the answer itself, not a downstream consequence".
- **Boy Scout in touch radius enforced across exec/review/remediate** – the `andthen:exec-spec` skill gains a Core Rule and a 4a lint/types gate requiring pre-existing violations inside `changed-files` to be fixed or deferred with a one-line reason, ending the bare "did not touch pre-existing errors" disclaimer. The `andthen:review` (`lens-code`) and `andthen:quick-review` skills now treat that disclaimer as a finding when the issue sits *inside the changed files* (default MEDIUM, HIGH for correctness/security); issues in unchanged files remain out of scope. The `andthen:remediate-findings` scope-creep rule is clarified to permit Boy Scout cleanup within files already being edited while still forbidding expansion into untouched files.

### Fixed
- **`excalidraw-diagram` portable export and text clipping** – saved `.excalidraw` files previously kept the `label:` shorthand and undersized standalone text widths, producing empty shapes and clipped titles when opened in `app.excalidraw.com`. Phase 3.6 promoted to mandatory Phase 5 step; render template now measures standalone text via Canvas `measureText` with the actual Excalidraw font and patches width/height during `getConvertedJSON`. Author no longer needs to hand-size text elements.


---


## [0.14.2] – 2026-04-24

### Added
- **`--auto` / `--headless` for core pipeline and supporting skills** – `prd`, `plan`, `spec`, `exec-spec`, `exec-plan`, `review`, `quick-review`, `remediate-findings`, `architecture`, `ui-ux-design`, and `triage` now expose an automation-safe mode for external orchestrators. In this mode skills avoid conversational prompts and arrow-prompts, make conservative assumptions, record deferred decisions in artifacts or summaries, propagate `--auto` to nested `andthen:*` skill calls that accept it (`ops` is exempt — deterministic), and stop with `BLOCKED:` only on contract failures or unsafe actions.


---


## [0.14.1] – 2026-04-24

### Added
- **DDD reference in `andthen:architecture`** – new `references/ddd.md` covering strategic (subdomains, bounded contexts, 9-pattern context map, team topology) and tactical DDD (aggregate rules, entities/VOs, domain vs integration events, application vs domain service, factories, repositories), plus Hexagonal/CQRS/Event Sourcing, Event Storming, Bounded Context Canvas, Functional DDD, and three new anti-patterns (False Invariant Aggregates, Leaky Integration Events, Model-Code Gap). Lazy-loaded from `advise` and `decompose` modes.
- **Ousterhout module-design lens in `andthen:architecture`** – new `references/ousterhout-modules.md` covering deep vs shallow modules, information leakage, pass-through methods, pull-complexity-downward, define-errors-out-of-existence, temporal decomposition, and an 8-test review checklist. Opt-in Step 6 in `mode-review.md` at Component/Code scope only.
- **Three Ousterhout-derived anti-patterns** in `architecture/references/anti-patterns.md` – **Shallow Module**, **Pass-Through Method / Layer**, and **Temporal Decomposition**, each with symptoms, fix, review question, and false-positive boundary. Existing **Leaky Abstraction** extended to cover shape-level information leakage.
- **Composition Playbook for `andthen:excalidraw-diagram`** – new `references/composition-playbook.md` with five archetype recipes (Pipeline, Architecture, Taxonomy, Lifecycle, Comparison) keyed to concrete XY positions, zone plans, size cascades, and anti-checks.
- **`window.lintLayout()` in the Excalidraw render template** – automated layout linter returning CRITICAL/MAJOR/MINOR findings (overlaps, text-over-shape, uniform grids, font < 14, tight spacing, missing hero, off-grid coords, missing primary-flow arrow). Integrated into the render loop and re-checked after each fix.
- **AndThen skills overview diagram** – `docs/diagrams/andthen-skills-overview.excalidraw` plus rendered PNG.

### Changed
- **`architecture` advise-mode DDD section trimmed** – `mode-advise.md` DDD block replaced by a building-blocks quick-reference table + assessment questions with a pointer to `ddd.md`. Added **Application Service** row and fixed prior conflation of domain events with integration events.
- **`architecture` decompose-mode context-map catalog expanded** – `decomposition.md` context-mapping table: 6 → 9 patterns (**Partnership**, **Separate Ways**, **Big Ball of Mud**), added **Team relationship** column and selection-trigger guidance. Pattern/coupling/team-relationship columns kept byte-synced with `ddd.md`.
- **`andthen:review` council mode extracted** – the ~140 lines of council orchestration moved from `SKILL.md` into a new `references/council-mode.md` (lazy-loaded on `--council`). `SKILL.md` 325 → 185 lines; non-council reviews no longer load council content. Auto-escalation triggers kept in `SKILL.md` so the load decision doesn't require reading the reference first.
- **`andthen:review` gap-lens Step 5 behavioral dry-run walkthrough** – replaces the one-line "Optional Retrospective" stub. Five mandatory passes per requirement: trace execution, check pre/post/invariants, stress unhappy paths, test assumptions, sanity-check the design. Findings merge into Step 4 categories — Step 6 adversarial challenge and scoring unchanged.
- **`andthen:review` gap-lens Step 4 Gap Analysis restored** – reverses the v0.10.0 compression that reduced each of the seven gap categories to a single word. Each category now carries one concrete sentence with examples. PASS/FAIL verdict table untouched (downstream contract preserved).
- **Mandatory Layout Contract in `andthen:excalidraw-diagram` Phase 1.5** – 10-line pre-JSON commitment covering narrative, archetype, axis, hero, size cascade, shape vocabulary, zone plan, canvas size, evidence artifacts, and rhythm breakers. Named as the primary fix for uniform-grid AI-generic output.
- **Excalidraw render loop hardened** – dropped the `esm.sh?bundle` query (silent font-ID bug), switched to a 60s bash polling loop on `window.__moduleReady` (`wait --fn` timeout is not honoured empirically), and replaced manual viewport sizing with `AGENT_BROWSER_FULL=true` full-page screenshots.
- **`style-guide.md` gains Size Cascade, Anti-Uniformity, Signal Badges, and Density Gradient sections** – authoritative `hero : primary : secondary ≈ 3 : 1.8 : 1` numbers, ban on 6+ shapes sharing `(type, width, height, color)`, pill-badge spec, and three-band density layout for XL/XXL canvases.
- **`element-format.md` gains Label Auto-Sizing math and Text Metrics table** – per-shape minimum-width formulas (ellipse ≈ 1.4× rectangle, diamond ≈ 2×), `BOUND_TEXT_PADDING = 8px`, per-font character-width estimates at fontSize 16/18/24, and 20px grid-snap rule.
- **`andthen:clarify` recommend-don't-decide loop** – Step 2 requires a best-guess answer with rationale per question, probing on load-bearing answers, and treats unaddressed recommendations as unanswered. New gotchas for "treating recommendation as confirmed" and "asking things already answerable from the codebase".
- **`andthen:spec` research steps tightened** – Codebase research uses direct `rg`/`tree`/file reads; new **Solution architecture** step invokes `andthen:architecture --mode advise` in a sub-agent and is recommended for most code changes; architecture trade-offs reframed as optional unless 1–3 genuinely competing approaches exist.
- **Breaking-changes docs consolidated in `plugin/README.md`** – root `README.md` now carries a one-line pointer; the detailed 0.13.0 migration tables moved to a new **Breaking Changes** section in `plugin/README.md`, extended with a 0.14.0 entry for the 1:1 story↔FIS invariant.

### Removed
- **Sub-agent capability hedges across 12 skills** – stripped `_(if supported)_` / `_(if supported by your coding agent)_` qualifiers from `exec-plan`, `exec-spec`, `map-codebase`, `plan`, `prd`, `quick-implement`, `refactor`, `spec`, `triage`, `ubiquitous-language`, `ui-ux-design` (+ `mode-design-system`, `mode-wireframes`), and `architecture/mode-trade-off`. Sub-agents are now assumed available; `general-purpose` is the portable fallback.


---

## [0.14.0] – 2026-04-21

### Changed
- **1:1 story↔FIS invariant in `andthen:plan`** – removed THIN and COMPOSITE classification tiers; every story now maps to exactly one FIS file and no two stories share a FIS path. Step 3 Story Breakdown gained a **Consolidation Pass** that merges stories at breakdown time when they share an implementation surface, form a tight dependency chain (where the downstream story has no independent demo value), or would both produce trivially small FIS with a shared primary concern. Rationale: the plan↔FIS join is a single-column contract; keeping it unique-key eliminates a recurring class of consistency bugs ("stories not corresponding to FIS files") and lets downstream skills drop their shared-spec branching logic. Files updated: `plan/SKILL.md` (Step 6 collapsed from three sub-sections to one, composite/thin paths removed from Orchestrator Role, GOTCHAS, OUTPUT tree, Spec Flow Example, and COMPLETION summary), `plan/templates/plan-template.md` (composite-sharing example replaced; new 1:1 invariant callout).
- **`andthen:exec-plan` simplified** – deleted the Shared-FIS Dedup mechanism in both solo mode (Step 3b) and team mode (Task Management). `impl-*` / `review-*` task naming dropped the composite form; each story now gets its own exec-spec + quick-review run. Removed the "re-executing a composite FIS already implemented" gotcha.
- **`andthen:exec-spec` simplified** – `STORY_IDS` (list) collapsed to `STORY_ID` (single) for plan-backed specs. Dropped the composite-vs-single branches in Step 2 project-state setup and Step 5b completion updates.
- **`andthen:spec` oversize-pivot disclaimers removed** – the "do not run THIN/COMPOSITE/shared-FIS classification" caveats are no longer needed since that classification no longer exists. Oversize pivot mode remains unchanged (straightforward one-story-per-FIS decomposition).
- **FIS size thresholds raised** – sweet spot `100-300` → `150-450` lines; oversize pivot trigger `>400 lines or >12 tasks` → `>600 lines or >18 tasks`. Rationale: consolidated stories (from the plan's Consolidation Pass) legitimately land where the old thresholds triggered pivots. Updated in `spec/SKILL.md:40,109`, all three copies of `fis-authoring-guidelines.md` (canonical in `spec`, dupes in `plan` and `review`), and both copies of `fis-template.md` (canonical in `spec`, dupe in `plan`).
- **`init/templates/CLAUDE.template.md` Project Document Index** – removed `composite s0N-s0M-*.md` and `thin-specs.md` from the spec directory description; the pattern is now just `s01-*.md`, `s02-*.md`, …


---

## [0.13.2] – 2026-04-20

### Fixed
- **Deprecated Excalidraw font IDs in `andthen:excalidraw-diagram`** – `style-guide.md` and `element-format.md` instructed the agent to emit `fontFamily: 1` (Virgil), `2` (Helvetica), and `3` (Cascadia) on text and labeled-shape elements. All three are flagged `deprecated: true` in Excalidraw's `packages/common/src/font-metadata.ts` and persist a deprecated-font marker into generated scenes. Updated both references to the current non-deprecated IDs: `5` (Excalifont – hand-drawn default), `6` (Nunito – clean sans-serif), `8` (Comic Shanns – the only non-deprecated ID that `getGenericFontFamilyFallback` routes to the monospace CSS fallback). Added a new Font Family IDs table to `element-format.md` and an explicit "do not use 1/2/3" callout to `style-guide.md`. Updated all prose mentions of "Virgil/Helvetica/Cascadia" and the three aesthetic preset tables (Hand-drawn Blueprint, Warm Industrial, Clean Technical) accordingly.
- **Phantom preset name in the Complete Example caption** (`element-format.md:194`) – the caption called the bronze-hachure + warm-parchment example "the default 'Schematic Warmth' style", but `style-guide.md` defines only three presets (Hand-drawn Blueprint, Warm Industrial, Clean Technical) and the actual default is Hand-drawn Blueprint (pastel palette, white canvas). Rewrote the caption to correctly identify the example as a **Warm Industrial** illustration and point readers to `style-guide.md` for the default palette. JSON unchanged – it's a valid bronze-zone + green-accent example on the warm-parchment preset.


---

## [0.13.1] – 2026-04-20

### Fixed
- **Agent/skill confusion around `andthen:quick-review`** – the skill's own description led with "fresh-context sub-agent" and the `andthen:remediate-findings` call site sat next to "heavyweight re-review sub-agents", which primed callers (especially when `remediate-findings` itself ran inside a sub-agent) to pass `andthen:quick-review` as `subagent_type` to the Task tool and fail with "Agent type not found". Reframed the skill description and opening, added an explicit "this is a skill, not an agent type — do not pass as `subagent_type`" guardrail, and rewrote the `remediate-findings` step-4 invocation to mirror the defensive pattern already used in `exec-spec/SKILL.md:135,138`.

### Changed
- **Testing discipline tightened in verification gates** – `andthen:exec-spec` Step 4a gains a new "Tautology check" (the unit under test must be imported and called without being replaced by a mock; assertions must reference its return value or an observable effect, not mock call arguments; fixtures must not substitute for the production computation). The code-review checklist replaces the generic "Mock/stub usage appropriate" item with two sharper checks: mocks/stubs confined to system edges, and each test would fail if the asserted production behavior were removed.
- **Removed changelog framing from prompt artifacts** – per the "no historical-change notes in skill prompts, references, or templates" principle, dropped the `Replaces/evolves the narrower "implementation-notes.md" concept.` tail from the LEARNINGS.md blockquote in both `init/templates/project-state-templates.md` and `map-codebase/templates/project-state-templates.md`, and removed the "replaces the heavyweight re-review sub-agents" comparative from `remediate-findings/SKILL.md:93`.


---

## [0.13.0] – 2026-04-20

### Added
- **`andthen:architecture` skill** (`plugin/skills/architecture/`) – renamed from `architecture-review` and expanded into a five-mode skill: `review`, `decompose`, `advise` (absorbs the former `solution-architect` agent's CUPID/DDD/ADR methodology), `fitness`, and `trade-off` (absorbs the former `andthen:trade-off` skill). Each mode's body lives in `plugin/skills/architecture/references/mode-<mode>.md`; `SKILL.md` is a thin router.
- **`andthen:ui-ux-design` skill** (`plugin/skills/ui-ux-design/`) – new skill that merges the former `design-system` skill, `wireframes` skill, and `ui-ux-designer` agent into one four-mode skill: `research`, `design-system`, `wireframes`, `review`. Per-mode bodies in `plugin/skills/ui-ux-design/references/mode-<mode>.md`. Named `ui-ux-design` (activity) rather than `ui-ux-designer` (persona) to reinforce the skill-is-activity / agent-is-persona convention.
- **`andthen:testing` skill** (`plugin/skills/testing/`) – new skill that replaces the former `qa-test-engineer` agent and adds test-first discipline as first-class craft. Modes: `strategy`, `write` (default), `tdd`, `prove-it`. `SKILL.md` is a thin router; authoritative material lives in four references drawing on Kent Beck, Dave Farley, Addy Osmani, Michael Feathers, Kent C. Dodds, and Matt Pocock:
  - `references/tdd-discipline.md` — Red/Green/Refactor, triangulation, anti-rationalization table, when NOT to TDD.
  - `references/prove-it-pattern.md` — failing-test-first for bugfixes, characterization tests for legacy code, Beyonce Rule.
  - `references/test-design.md` — behavior-over-implementation, diagnosability, mock minimization, property-based and contract testing.
  - `references/levels-and-strategy.md` — unit/integration/E2E trust-boundary criteria, Testing Trophy, coverage prioritization matrix.
  - `references/farley-framework.md` — duplicate of the `architecture` skill's Farley framework (activity-local anchor for testability-as-modularity).
  Callers (`exec-spec`, `triage`, `e2e-test`) invoke it directly as `/andthen:testing`; runs in the caller's context by default (useful for `tdd`/`prove-it` continuity), with optional `general-purpose` sub-agent wrapping for fresh-context isolation.
- **Codex agent generator** (`scripts/generate-codex-agents.sh`) – generates `andthen-*.toml` files from `plugin/agents/*.md` into the user's Codex agents directory (`~/.codex/agents` by default) at install time, so Claude Code agent files are the single source of truth. Invoked automatically by `scripts/install-skills.sh` (use `--no-codex-agents` to skip).
- **`andthen:prd` skill** (`plugin/skills/prd/`) – extracts PRD creation from `plan`. Produces `prd.md` from clarified requirements, draft PRDs, raw description, a file, a URL, or a GitHub issue. Pass-through when a `prd.md` already exists in the target directory. Output-path semantics match the `andthen:plan` input contract so the `prd → plan` chain is stable.
- **Unified verdict reference** (`plugin/skills/review/references/review-verdict.md`) – normalised severity scale (`CRITICAL` / `HIGH` / `MEDIUM` / `LOW`) and per-mode readiness/verdict definitions for the `andthen:review` modes (including `--council`). Gap-mode PASS/FAIL contract preserved byte-for-byte.
- **Lens references for `andthen:review`** (`plugin/skills/review/references/lens-code.md`, `lens-doc.md`, `lens-gap.md`) – self-contained rubrics loaded per mode; `andthen:review` now runs each lens inline instead of delegating.
- **`--fix` flag on `andthen:review` and `andthen:quick-review`** – optional auto-remediation after the review runs. `review --fix` delegates to the `andthen:remediate-findings` skill with the consolidated report path (incompatible with `--inline-findings`; with `--to-pr`, the PR comment is posted first so the comment reflects the original findings). `quick-review --fix` applies the accepted findings inline after the Accept/Dismiss step — dismissed findings stay dismissed. Single flag, no severity levels: `remediate-findings` owns fix scoping.

### Changed (breaking)
- **`andthen:plan` requires `prd.md` input and produces the full plan bundle in one run** (`plugin/skills/plan/`) – `plan` now expects a directory containing `prd.md` and produces `plan.md` + batch-generated FIS for every story + shared `.technical-research.md` + cross-cutting review. Absorbs the work the removed `spec-plan` skill used to do. Adds `--skip-specs` for a cheap planning pass. Resume contract preserved: re-running on a partially-specced directory only fills missing FIS.
- **`andthen:exec-plan` no longer generates specs** (`plugin/skills/exec-plan/`) – requires a fully-specced plan bundle. Fails fast and redirects to `andthen:plan` if any story's `**FIS**` field is `–` or points at a non-existent file. Removed the per-phase `spec-plan` step.
- **`andthen:review` absorbs `review-code`, `review-doc`, `review-gap`, and `review-council` as internal modes** (`plugin/skills/review/`) – one user-facing review skill. Code, doc, and gap lenses run inline using `plugin/skills/review/references/lens-*.md`. Multi-perspective adversarial review (5-7 reviewers + two-phase challenge) runs via `--council`, auto-escalating for high-risk scope or when the user asks for multi-perspective/adversarial review. `--team` still forces Agent Teams mode. Reviewer roster moved to `plugin/skills/review/references/reviewer-roster.md`.
- **`andthen:review` flag renames**: `--code-only` / `--doc-only` / `--gap-only` → `--mode code|doc|gap|mixed`. Council mode invoked via `--council` (replaces the former peer `andthen:review-council` skill). Auto-detection behavior unchanged when `--mode` is absent.
- **Unified severity scale across review modes** – `SUGGESTIONS` bucket normalised to `LOW`; `MEDIUM` added to the code lens. Old reports remain readable via the mapping in `plugin/skills/review/references/review-verdict.md`.
- **Skills are fully self-contained** – `plugin/references/`, `plugin/scripts/`, and the repo-root `templates/` directory retired. Each skill owns its `references/`, `templates/`, and `scripts/` locally; skill files never cross skill boundaries (no `../<other-skill>/...` paths, no `${CLAUDE_PLUGIN_ROOT}` references). Short refs inlined into consumer SKILL.md; larger refs, templates, and scripts duplicated into each consuming skill. Markdown duplicates carry a YAML `source:` frontmatter pointer to the canonical owner; script duplicates track ownership via the table in CLAUDE.md. The former repo-root starter templates (`CLAUDE.template.md`, `project-state-templates.md`) now live canonically under `plugin/skills/init/templates/`, with `map-codebase` carrying a duplicate of `project-state-templates.md`. Skills are now droppable into any Claude Code tier (plugin/user/project) or Codex export without path rewriting.
- **`install-skills.sh` simplified** – removed all path rewriting (~100 lines). Only namespace transforms remain (`andthen:` → `andthen-` and `/andthen:` → `$andthen-`). No top-level `andthen-scripts` or `andthen-templates` sibling dirs are installed.
- **`fis-authoring-guidelines.md` trimmed** – removed exec-time guidance that belongs in `andthen:exec-spec`, compressed the Execution Contract section and the Self-Check bullets, and kept one weak/strong `Verify:` pair instead of several. Canonical lives in `plugin/skills/spec/references/`; duplicated into `plan/` and `review/` with `source:` frontmatter.
- **Checklists and calibration files moved** (`plugin/skills/review/checklists/`, `plugin/skills/review/references/`) – merged the assets from the deleted `review-code`, `review-doc`, and `review-council` skills into the unified `review` skill; all path references updated across consuming skills.
- **PRD framing removed from `andthen:plan`** – the `plan` description, workflow, and OpenAI agent prompt no longer claim to create PRDs. That work lives in the new `andthen:prd` skill.

### Removed (breaking)
- **`andthen:qa-test-engineer` agent** – replaced by the new `andthen:testing` skill. The skill surface lets test-first/TDD discipline live alongside coverage and strategy in one place. Callers (`exec-spec`, `triage`, `e2e-test`) now invoke `/andthen:testing` instead of spawning the agent. The `scripts/install-skills.sh` stale-agent list removes the old Codex `andthen-qa-test-engineer.toml` on upgrade.
- **`andthen:solution-architect` agent, `andthen:ui-ux-designer` agent, `andthen:build-troubleshooter` agent** – these three agents didn't need fresh context, they needed methodology applied to current work. Converted into skills or merged into existing skills:
  - `solution-architect` → merged into `andthen:architecture --mode advise` (CUPID/DDD/ADR methodology now lives in `plugin/skills/architecture/references/mode-advise.md`)
  - `ui-ux-designer` (agent) → new `andthen:ui-ux-design` skill (merges the former `design-system` and `wireframes` skills as modes alongside `research` and `review`)
  - `build-troubleshooter` → merged into `andthen:triage` (diagnostic methodology now lives in `plugin/skills/triage/references/diagnostic.md`)
  - Remaining 3 agents kept — `documentation-lookup`, `research-specialist`, `visual-validation-specialist` — they genuinely benefit from fresh context (background lookups, long research, visual capture/compare).
- **`andthen:trade-off` skill** – absorbed into `andthen:architecture --mode trade-off`. Trade-off analysis stays the same (weighted criteria, option research, recommendation, optional ADR); it now chains naturally with `advise` (design options) and `fitness` (governance for the chosen path).
- **`andthen:design-system` skill** – absorbed into `andthen:ui-ux-design --mode design-system`.
- **`andthen:wireframes` skill** – absorbed into `andthen:ui-ux-design --mode wireframes`.
- **`andthen:architecture-review` skill folder** – renamed to `andthen:architecture` via `git mv` (blame history preserved). Callers using `/andthen:architecture-review` must migrate to `/andthen:architecture`. Modes unchanged; `trade-off` added as a 5th mode.
- **Agent-scoped methodology references** – the 6 `*-methodology.md` files and `documentation-retrieval-guide.md` under `plugin/references/` are gone. Methodology now lives inline in each agent `.md` file or as a skill-local reference, removing the brittle two-file-with-path-substitution pattern.
- **Committed `codex/agents/*.toml`** – replaced by install-time generation (see Added). The `codex/` directory is no longer committed.
- **`andthen:spec-plan` skill** – absorbed into `andthen:plan`. Re-running `andthen:plan` on a directory with existing FIS is the new "fill missing specs" path. `--skip-specs` preserves the old two-step flow on demand.
- **`andthen:review-code`, `andthen:review-doc`, `andthen:review-gap`, `andthen:review-council` skills** – absorbed into `andthen:review` as internal modes. External callers of `/andthen:review-code` etc must migrate to `/andthen:review --mode code|doc|gap`; `/andthen:review-council` callers migrate to `/andthen:review --council`.
- **`andthen:review` `--deep` flag** – removed. Multi-perspective adversarial review is now the dedicated `--council` flag; plain `--mode code` runs a single-reviewer pass.
- **Typed GitHub artifact envelope contract removed** — `plugin/references/github-artifact-roundtrip.md` and `plugin/references/resolve-github-input.md` deleted. The `<!-- ANDTHEN_ARTIFACT:BEGIN -->` envelope, `schema: andthen/github-artifact-v1`, `artifact_type`, `canonical_local_primary`, embedded `### File:` blocks, and all round-trip metadata fields are gone. Rationale: the envelope was designed for cross-machine resumption of multi-file artifacts, a scenario already solved by `git push` + branch checkout. Paying envelope cost on every producer/consumer was over-engineering.
- **GitHub I/O narrowed to six prose-only integration points**:
  - `clarify --issue <n>` / `prd --issue <n>` — fetch issue body as prose requirements
  - `prd --to-issue` — publish PRD as a plain GitHub issue
  - `triage --to-issue` — publish triage plan / completion summary as a plain issue
  - `quick-implement --issue <n>` — read issue body as prose, implement, open a PR with `Closes #N`
  - `review --to-pr <number>` / `architecture --to-pr <number>` — post the report as a plain PR comment
- **`--issue` and `--to-issue` removed** from `andthen:plan`, `andthen:spec`, `andthen:exec-plan`, and `andthen:exec-spec` — these skills are local-only. Use a feature branch + PR for cross-machine handoff.
- **`andthen:review --to-issue` removed** — use `--to-pr <number>` for PR-scoped publication; otherwise the report file lives on disk. `andthen:architecture --to-issue` removed for the same reason.
- **`andthen:remediate-findings` GitHub URL input removed** — accepts only local report paths and direct raw report URLs. Issue/PR-shell URLs stop with an invalid-input error.
- **`exec-plan` variable rename**: `PLAN_SOURCE` → `PLAN_DIR`.
- **`exec-spec` variable rename**: `FIS_SOURCE` → `FIS_FILE_PATH`. `STORY_IDS` and `PLAN_FILE_PATH` are now extracted from the FIS itself (header field or filename prefix).
- **`check-stubs.sh`, `check-wiring.sh`, `verify-implementation.sh` scripts removed** – grep-based heuristics now inlined as short prose instructions in `andthen:exec-spec` Step 4a and `andthen:review` gap lens. Frontier models run the underlying greps directly; wrapping them in shell scripts violated the "if a frontier model would naturally do something, don't instruct it" principle and carried a drift vector across duplicated copies. `plugin/skills/exec-spec/scripts/` directory removed; `plugin/skills/review/scripts/` now only holds `run-security-scan.sh` (real tool wrapper). `scripts/test-scripts.sh` removed (tested a path — `plugin/scripts/` — that no longer exists).


---

## [0.12.1] – 2026-04-17

### Fixed
- **Skills-as-agents regression eliminated** (CLAUDE.md, and 19 skill prompts including `review`, `exec-spec`, `plan`, `spec`, and `spec-plan`) – skill names were being passed as `subagent_type` to the Task tool, triggering "Agent type not found" errors. Reworded every `andthen:<name>` reference across skill prompts, references, and templates so the type noun ("skill" or "agent") sits adjacent to the name; purged the "Spawn `andthen:<skill>` sub-agent" antipattern
- **Install-script slash-command translation** (`scripts/install-skills.sh`) – added anchored rewrite rule so `/andthen:<name>` invocations correctly become `$andthen-<name>` for Codex/portable agents while preserving path separators, markdown links, and URLs containing `/andthen:` substrings

### Added
- **Skills vs Agents invariant** (CLAUDE.md) – new guardrail section names the authoritative agent/skill lists, the "Spawn `andthen:<skill>` sub-agent" antipattern, the mandatory wording convention (type noun adjacent to each `andthen:<name>` reference), and an audit command for future refactorings
- **`architecture-review` multi-mode chains** (`architecture-review`) – `--mode` now accepts a comma-separated list (e.g. `--mode review,fitness` or `--mode review,decompose,fitness`); chained modes execute in declared order, share computed metrics, dependency graph, connascence, and findings without recomputation, and produce a single combined report with merged Executive Summary and legend. Skill description updated to surface the four modes and chaining capability

### Changed
- **`quick-review` instruction reworded** (`quick-review`) – clarified positioning as a "lightweight mid-conversation review" scoped to recent changes, rather than framing it primarily as "not a formal review"


---

## [0.12.0] – 2026-04-16

### Changed
- **Redundant review layers eliminated across core flows** (`review-gap`, `remediate-findings`) – `review-gap` no longer delegates to `review-code` (exec-spec already runs it), and `remediate-findings` uses `quick-review` instead of spawning up to 3 heavyweight review sub-agents
- **`exec-plan` simplified to fixed pipeline** (`exec-plan`) – removed `--review-mode` parameter and conditional branching; each story now runs `exec-spec` → `quick-review`, with a single `review-gap` on the whole plan at the end
- **GitHub artifact routing factored into shared reference** (`resolve-github-input.md`, `clarify`, `spec`, `exec-spec`, `review-gap`, `remediate-findings`, `plan`, `spec-plan`, `exec-plan`) – extracted GitHub input resolution logic from 8 skills into a single shared reference, reducing per-skill prompt weight and ensuring consistent routing
- **Adversarial challenge made conditional** (`review-gap`, `review-doc`) – full adversarial challenge now triggers only when any finding is Critical or total findings exceed 5; otherwise applies inline severity calibration
- **`exec-spec` completion steps consolidated** (`exec-spec`) – merged Steps 5b (Update FIS/Plan), 5c (Update State), and 5d (Continuation Sync) into a single combined gate step, reducing 5 substeps to 3
- **Small references inlined and deleted** (`exec-spec`, `exec-plan`, `quick-implement`) – `verification-evidence.md` and `post-completion-guide.md` inlined into consuming skills and removed
- **`spec-plan` classification simplified** (`spec-plan`) – THIN/COMPOSITE classification reduced from 9+ conditions to 2 criteria each
- **`plan` skill trimmed** (`plan`) – reduced from 356 to 298 lines by condensing goal-backward analysis, story metadata, design space analysis, and wave assignment sections
- **Language trimming applied across workflow skills** (`clarify`, `spec`, `exec-spec`, `exec-plan`, `plan`, `spec-plan`, `review-gap`, `remediate-findings`, `review`, `review-code`, `review-doc`, `quick-review`, `quick-implement`) – replaced emphatic MUST/NEVER/CRITICAL patterns with balanced direct language, removed filler prose, and consolidated redundant mixed-mode guidance in `review`
- **"Read Workflow Rules" instruction normalized** (`quick-implement`) – replaced verbose form with the shortened cross-agent-safe form used by other review/secondary skills
- **`fis-authoring-guidelines.md` trimmed** (`fis-authoring-guidelines.md`) – principles block condensed, self-check reduced, philosophical framing removed
- **`github-artifact-roundtrip.md` consumption logic factored out** (`github-artifact-roundtrip.md`) – routing/extraction rules moved to `resolve-github-input.md`; roundtrip doc now focuses on publishing and continuation sync
- **Research responsibility clarified across plan → spec-plan → spec** (`plan`, `spec-plan`, `spec`) – `plan` no longer creates `.technical-research.md` (lightweight scan for story boundaries only); `spec-plan` reduced from 4 to 3 upfront research sub-agents (external API research deferred to individual spec sub-agents that need it); `spec` now structurally skips research steps when plan-scoped `.technical-research.md` exists upstream
- **`exec-plan` and `exec-plan-team` merged into single `exec-plan` skill** (`exec-plan`) – Agent Teams mode available via `--team` flag with auto-detection; `--worktree` for parallel execution in team mode; team section written at higher altitude instead of verbatim prompt templates; shared final review/verification steps
- **`review-council` and `review-council-team` merged into single `review-council` skill** (`review-council`) – Agent Teams mode available via `--team` flag with auto-detection; shared preamble and forked execution paths
- **Review skills consolidated to fewer user-facing entry points** (`review`, `review-code`, `review-doc`, `review-gap`) – `review-code`, `review-doc`, and `review-gap` demoted to internal delegates (`user-invocable: false`); `review` router description updated to emphasize it as the single entry point for all review types; added "review implementation of [doc]" routing heuristic to correctly route to gap review

### Removed
- **`plugin/references/verification-evidence.md`** – content inlined into consuming skills
- **`plugin/references/post-completion-guide.md`** – content inlined into consuming skills
- **`plugin/skills/exec-plan-team/`** – merged into `exec-plan` with `--team` flag
- **`plugin/skills/review-council-team/`** – merged into `review-council` with `--team` flag

## [0.11.2] – 2026-04-15

### Changed
- **`plan` now defaults to headless requirements synthesis** (`plan`) – replaced the interactive discovery interview path with headless-first PRD/plan synthesis that proceeds with explicit assumptions and only stops on true contract failures or irreducible ambiguity
- **Non-interactive workflow stop gates now use fail-fast contract wording** (`spec`, `spec-plan`, `exec-spec`, `exec-plan`, `exec-plan-team`, `triage`, `review-gap`, `remediate-findings`, `design-system`, `wireframes`, `excalidraw-diagram`) – normalized prompt language away from conversational “ask/recommend/direct user” phrasing toward explicit missing-input, invalid-input, and downstream-routing exits suitable for headless execution
- **Technical research companion files are hidden again** (`plan`, `spec`, `spec-plan`, `exec-spec`, templates, artifact round-trip docs, FIS authoring guidelines`) – renamed the documented companion artifact from `technical-research.md` to `.technical-research.md` to make it easier to ignore by default while still keeping it available for execution context when needed
- **`architecture-review` reports now explain their shorthand inline** (`architecture-review`) – added a required `How to Read This Report` legend for review, decompose, and fitness outputs so package and graph metrics, package-principle acronyms, C4 labels, zone labels, and connascence abbreviations are explained in the report instead of assuming prior architecture-review knowledge

## [0.11.1] – 2026-04-14

### Fixed
- **Project Document Index wording drift in workflow skills** (`spec-plan`, `exec-spec`, `ops`, `init`) – removed stale hardcoded document-name references (`LEARNINGS.md`, `STATE.md`, `ARCHITECTURE.md`, `STACK.md`) where those prompts should refer to the `Learnings`, `State`, `Architecture`, and `Stack` documents via the **Project Document Index**
- **`spec-plan` project-context discovery drift** (`spec-plan`) – Step 1.5 now reads the `Learnings` document using the same Project Document Index contract as the rest of the workflow, avoiding a stale direct filename reference during batch spec generation
- **`review` routing ambiguity** (`review`) – explicit mode flags now constrain target discovery, explicit code-review intent no longer gets silently upgraded to gap review just because nearby spec artifacts exist, and `Mixed` is now a stable `Doc + Code` dispatch mode instead of a fuzzy fallback

## [0.11.0] – 2026-04-14

### Added
- **Direct `exec-spec` execution model** (`exec-spec`) – `exec-spec` now implements FIS documents directly, keeping deep implementation context in one agent while reserving sub-agents for advisory work, fresh-context review, and visual validation
- **Shared methodology references for thin agents** (`plugin/references/*-methodology.md`, `plugin/agents/*`, `codex/agents/*`) – extracted reusable diagnostic, documentation lookup, QA, research, solution architecture, UI/UX, and visual validation guidance into shared reference files consumed by thin Claude and Codex agent wrappers
- **Codex custom agent distribution** (`codex/agents`, `install-skills`) – expanded portable Codex agent distribution for the advisory/review agent layer and wired the installer to export those agents alongside skills

### Changed
- **FIS execution contract simplified** (`exec-spec`, `spec`, `spec-plan`, `fis-template`, `fis-authoring-guidelines`) – the workflow now centers direct execution, task-level scenario proof mapping, explicit execution contracts, and tighter size/traceability checks for specs
- **Downstream plan execution alignment** (`exec-plan`, `exec-plan-team`, `MODEL-EFFORT-SELECTION-GUIDE`, `README`) – downstream orchestration and model-selection docs now reflect the direct-execution `exec-spec` contract instead of an implementor sub-agent architecture
- **Portable install path expanded** (`install-skills`, `README`) – the installer now exports skills, shared references, shared templates, helper scripts, and Codex agents as a single portable setup flow instead of leaving Codex agent installation as a manual step
- **`exec-spec` execution flow clarified** (`exec-spec`) – scenario-test scaffolding, technical-research/learnings/ubiquitous-language lookup, proactive advisory sub-agent usage, direct remediation, and completion reporting now live in one executor workflow instead of being split across orchestrator and implementor prompts

### Fixed
- **Bounded remediation path in `exec-spec`** – preserved a single recovery path for required validation failures while keeping the no-second-loop rule after one remediation pass
- **Portable path and namespace rewriting coverage** (`install-skills`, `templates/CLAUDE.template.md`) – exported bundles now rewrite `${CLAUDE_PLUGIN_ROOT}/skills/...` references, markdown link targets, and embedded `andthen:` skill/agent references in shared templates, preventing broken links and plugin-only command names in installed non-plugin bundles
- **Direct-execution validation continuity** (`exec-spec`) – `exec-spec` now maintains `changed-files` within the main run before scoped stub/wiring/substance checks instead of depending on a separate implementor handoff
- **Authoring and diagnostic source-of-truth drift** (`fis-authoring-guidelines`, `triage`) – aligned the FIS guide with task-ID proof mapping and direct-execution context, and pointed `triage` at the shared diagnostic methodology
- **Stale architecture docs after the direct-execution rewrite** (`README`, `plugin/README`, `CHANGELOG`) – updated live docs to stop describing `exec-spec` as an orchestrator/implementor flow after the implementor agents were removed
- **Trigger-eval harness robustness** (`scripts/eval-skill-triggers.sh`, `evals/skill-trigger-queries.json`) – removed a duplicate positive routing case from the eval corpus, stopped `--skill` from being interpolated into jq source, and made eval runs fail explicitly on `claude`/`jq` runtime errors instead of misreporting them as routing misses

## [0.10.8] – 2026-04-13

### Added
- **PRD and plan artifact templates** (`plan`) – added dedicated `prd-template.md` and `plan-template.md` files so long-lived planning artifacts now have explicit reusable baseline formats, similar to the existing FIS template pattern
- **Shared anti-rationalization reference** (`anti-rationalization`) – new `plugin/references/anti-rationalization.md` keeps the old excuse→reality pattern available as an on-demand reference instead of re-inlining rationalization tables into multiple skill bodies. Wired from `exec-spec`, `quick-implement`, `triage`, and `refactor`
- **Shared trust-boundaries reference** (`trust-boundaries`) – new `plugin/references/trust-boundaries.md` defines a compact 3-tier trust model (`Trusted` / `Verify Before Acting` / `Untrusted`) for browser state, logs, error output, scraped content, external docs, and tool/model output crossing boundaries

### Changed
- **Template-backed planning flow** (`plan`) – PRD creation and `plan.md` generation now reference dedicated template files instead of carrying the full document shapes inline in the skill prompt
- **Plan contract guidance** (`plan`) – the plan skill now explicitly preserves the Story Catalog columns and standard story metadata labels that downstream execution and review skills depend on
- **Lightweight anti-rationalization hooks** (`exec-spec`, `quick-implement`, `triage`, `refactor`) – skip-prone implementation/refactor skills now point to the shared `anti-rationalization` reference at the moment discipline is most likely to erode, preserving the pattern without re-bloating the main workflows
- **Trust-boundary wiring centralized** (`e2e-test`, `triage`, `review-code`) – inline trust warnings now route through the shared `trust-boundaries` reference so browser/runtime/tool-output handling can evolve in one place instead of diverging across skills
- **Scope-boundary artifacts strengthened** (`clarify`, `spec`, `fis-template`, `fis-authoring-guidelines`) – `clarify` now emits a `Not Doing (for now)` section for explicit non-goals and deferrals, `spec` carries those non-goals forward from `requirements-clarification.md`, and FIS authoring now requires non-goal items to be specific and justified rather than filler
- **FIS non-goals content upgraded without changing the contract** (`spec`, `spec-plan`, `fis-template`, `fis-authoring-guidelines`) – the canonical section remains `What We're NOT Doing`, but the template and guidance now require `3-5` intentional exclusions/deferrals with reasons so scope cuts survive session handoffs cleanly

### Fixed
- **Plan template story metadata contract** (`plan`) – restored `Phase`, `Wave`, `Dependencies`, `Parallel`, `Risk`, and `Asset refs` in the per-story template so generated plans match the story definition contract
- **Plan template example consistency** (`plan`) – aligned the Story Catalog example with the Phase Breakdown example to avoid teaching an internally inconsistent `plan.md` structure
- **Review-code trust-boundary trigger scope** (`review-code`) – broadened the trigger text to include logs, stack traces, error output, scraped content, and tool results so it matches the actual scope of the shared `trust-boundaries` reference
- **Non-goals section naming drift** (`fis-template`, `fis-authoring-guidelines`, `spec-plan`) – kept `What We're NOT Doing` as the canonical heading after strengthening the template, avoiding downstream checks and review logic keying off inconsistent section names

## [0.10.7] – 2026-04-13

### Added
- **Typed GitHub artifact envelope** (`github-artifact-roundtrip`, `plan`, `spec`, `review-gap`, `review-code`, `architecture-review`, `triage`) – GitHub issues and PR comments now have a machine-consumable AndThen envelope with artifact metadata plus embedded file blocks for round-trip workflows

### Changed
- **GitHub-first execution paths** (`exec-spec`, `spec-plan`, `exec-plan`, `review-gap`, `remediate-findings`) – downstream skills now accept typed GitHub issues / PR comment URLs and extract embedded artifacts into `.agent_temp/github-artifacts/...` before continuing
- **GitHub publish contract** (`report-output-conventions`, `quick-implement`) – PR-published review artifacts now require direct comment URLs, and `quick-implement` prints the created PR URL / number for follow-on PR workflows
- **Plan-backed FIS round-trip metadata** (`spec`, `exec-spec`) – `fis-bundle` now preserves `plan_path` / `story_ids`, requires deterministic primary-file resolution via `canonical_local_primary`, and restores plan context before plan/STATE updates
- **Canonical continuation sync** (`github-artifact-roundtrip`, `spec-plan`, `exec-plan`, `exec-plan-team`, `exec-spec`) – GitHub-extracted bundles are now explicitly treated as working mirrors that must sync back to local canonical files or refreshed GitHub artifacts before completion

## [0.10.6] – 2026-04-12

### Added
- **Negative-path scenario checklist** (`fis-authoring-guidelines`, `fis-template`) – systematic coverage check for omitted optional inputs, no-match selectors/filters, and rejection paths for external integrations. Applies to both `spec` and `spec-plan` via shared references
- **Scope-consistency and output format self-checks** (`fis-authoring-guidelines`, `fis-template`) – every In Scope item must be covered by a scenario or task; structured output criteria must specify shape, not just "returns JSON"
- **Prescriptive detail verification for Verify lines** (`fis-authoring-guidelines`) – when a FIS prescribes specific formats, columns, paths, or strings, the Verify line must check them verbatim. Weak/strong examples included
- **PRD-FIS semantic traceability** (`spec-plan`) – cross-cutting review check #10 verifies PRD feature requirements flow into FIS scenarios, catching requirements lost during plan decomposition. Binding PRD constraints extracted by technical research sub-agent and consumed by spec sub-agents
- **Spec compliance spot-check** (`exec-spec`) – Step 4a.7 extracts prescriptive details from the FIS and greps the implementation before marking complete. Prescriptive Detail Injection guidance ensures sub-agent prompts include format strings, column names, and file paths verbatim
- **Review mode guidance** (`exec-plan`) – recommends `per-story` (default) for most plans; documents when `none` and `full-plan` are appropriate
- **Plan provenance field** (`plan`) – `Provenance` story field for carried-forward stories with no PRD coverage, wired into Story Definition, output example, and validation self-check

### Changed
- **Plan Acceptance Gate expanded** (`exec-plan`) – now verifies exec-spec's spec compliance check completed (FIS checkboxes marked, verification evidence exists) before marking Done
- **`spec` Step 3 references negative-path checklist** – scenarios are now drafted with explicit negative-path guidance at the point where they're written, not just in the template
- **Composite FIS naming convention** (`plan`) – naming rule moved from advisory GOTCHAS into normative Composite FIS section

### Context
Based on post-mortem analysis of a real 11-story plan execution (plan → spec-plan → exec-plan → 2x review-gap) that failed gap review with 8 findings across 3 systemic patterns: missing negative-path scenarios, PRD-to-FIS requirements drift, and implementation ignoring explicit spec details.

---

## [0.10.5] – 2026-04-12

### Added
- **Technical Research Separation** – new `technical-research.md` companion document pattern keeps FIS and PRD/Plan focused on intent (reviewable for correctness) while preserving codebase analysis, API research, and architecture trade-offs for the executing agent. Updated FIS authoring guidelines with "what goes where" guidance and verification-during-execution contract. Touches `spec`, `plan`, `spec-plan`, `exec-spec`, FIS template, and authoring guidelines
- **Rollback-Friendly Groups** (`fis-authoring-guidelines`) – cross-cutting constraint on all slicing strategies: prefer additive changes within a group, separate "add new" from "remove old" so each group is independently revertable. A group that deletes and replaces in one pass leaves the system broken on revert
- **Prove-It Pattern for verification gates** (`exec-spec`) – behavioral failures between execution groups now require a failing test before the fix, proving the bug existed and preventing reintroduction in later groups
- **Non-reproducible bug classification** (`triage`) – when 5 Whys stalls on non-reproducible issues, classify by failure pattern (timing-dependent, environment-dependent, state-dependent, truly intermittent) with concrete investigation actions for each

### Changed
- **`spec-plan` renamed `.research-brief.md` to `technical-research.md`** – no dot prefix, includes "technical" for clarity. All prose references updated from "research brief" to "technical research" for consistency
- **`exec-spec` Step 1.5 skip conditions refined** – scaffold tests when a test runner exists and tasks have branching logic; skip only for config-only tasks with no scenarios. Beyonce Rule: when in doubt, scaffold
- **Development guidelines testing principle** – added Beyonce Rule: non-trivial branching logic gets a test even when no scenario covers it
- **FIS template scenario skip aligned with exec-spec** – replaced broad "purely structural work (scaffolding, config, migrations)" with narrow "configuration-only work with no branching logic" to match exec-spec's test-scaffold gate

### Fixed
- **Stale "Research brief" in `spec-plan`** – one COMPOSITE classification criterion still referenced "Research brief" after the rename to "technical research"
- **`spec` unconditional research file creation** – Step 2 mandated `technical-research.md` creation without qualifier; added "if substantial" guard matching `plan` skill's pattern
- **FIS template broken relative link** – `../../references/fis-authoring-guidelines.md` resolves inside the plugin tree but breaks in every generated FIS; removed the link, kept the description
- **`exec-spec` skip condition AND/OR ambiguity** – natural-language precedence was unclear; restructured as bulleted list with unambiguous nesting

---

## [0.10.4] – 2026-04-11

### Added
- **Plugin manifest** (`plugin/.claude-plugin/plugin.json`) – new per-plugin manifest file aligned with the official Claude Code plugin specification. Version bump instructions updated in `CLAUDE.md` and `ops` skill to cover all three version locations
- **Session management guidance** – predecessor skills (`clarify`, `plan`, `spec`, `spec-plan`) now recommend starting a clean session before context-intensive skills (`exec-spec`, `spec-plan`, `exec-plan`/`exec-plan-team`, `review-council`/`review-council-team`). README documents the principle in the Workflows section
- **Follow-up actions for `spec` and `spec-plan`** – both skills now have FOLLOW-UP ACTIONS sections suggesting next steps (previously missing)

### Changed
- **Marketplace.json aligned with official schema** – added `$schema`, moved `description` to top level, added `category` and `homepage`, removed redundant `metadata.pluginRoot` and `strict` fields
- **Skills reorganized as Standalone / Pipeline** – README skill tables restructured from Core/Extras to Standalone (13 everyday skills) and Pipeline (12 workflow skills), with usage examples reordered to lead with standalone one-liners. Both `plugin/README.md` and root `README.md` aligned
- **`plan` follow-up actions reordered** – lightweight options (spec S01, wireframes, review) listed first, context-intensive options (spec-plan, exec-plan) grouped after with clean-session tags

---

## [0.10.3] – 2026-04-11

### Fixed
- **Skill/agent invocation disambiguation** – fixed ~44 ambiguous `andthen:` references across 20 SKILL.md files where invocation instructions did not clearly distinguish between skills and sub-agents. Skills now consistently use "invoke the `andthen:X` skill" pattern; agents use "delegate to the `andthen:X` agent" pattern. Cross-references (non-invocation mentions) are left bare. Regression from v0.10.0 where the standardization was incomplete
- **`review-gap` requirements discovery** – gap analysis now discovers the full requirements baseline when given a directory or plan file, instead of treating the single input as the only requirements source. Searches for sibling PRD, plan, and FIS files; extracts FIS paths from Story Catalog tables and Phase Breakdown sections. Prevents shallow reviews that miss requirements context
- **`review-gap` code review report consolidation** – review-code sub-agent now returns findings inline instead of writing a separate report file, keeping the gap analysis as the single consolidated report

---

## [0.10.2] – 2026-04-10

### Fixed
- **`remediate-findings` re-validation loop** – replaced impractical "re-run originating review" step (which the model always skipped, cascading into skipped state updates) with a concrete findings re-check pattern: walk each finding, classify as RESOLVED/PARTIALLY RESOLVED/UNRESOLVED/DEFERRED with evidence, then run `review-code` on touched scope for regression detection. Scoped the "do not defer state updates" directive to prevent both the original caution deadlock and premature state updates on partial resolutions. Removed duplicate `review-code` invocation and aligned the Phase 4 gate with the severity policy

---

## [0.10.1] – 2026-04-10

### Added
- **`remediate-findings` skill** – new remediation workflow for implementing actionable findings from review reports such as `review-gap` and `review-code`. Re-validates findings against the current workspace, applies the smallest safe fix set, re-runs the relevant verification, and updates `plan.md`, FIS checkboxes, and `STATE.md` through `ops` when the reviewed work is now complete

### Changed
- **Review remediation path made explicit** – `exec-plan` and `exec-plan-team` now route review failures through `remediate-findings` instead of vague inline “fix issues” instructions, with consistent two-round review/remediation limits
- **Workflow and model docs updated** – README, plugin README, and the model-effort guide now document `remediate-findings` as the follow-up path after actionable review findings

---

## [0.10.0] – 2026-04-10

### Added
- **`architecture-review` skill** – deep quantitative architecture review with four modes: **review** (dependency metrics, package principles, connascence analysis, anti-pattern scan), **decompose** (split/merge evaluation using Ford/Richards drivers), **advise** (framework-grounded architectural guidance), and **fitness** (fitness function proposals with 4-level governance stack). Includes 9 reference files synthesizing Ford & Richards, Farley, Martin's Package Principles, Page-Jones/Weirich connascence taxonomy, and Building Evolutionary Architectures. Features adversarial challenge pass, language-aware tooling suggestions, and shared calibration integration
- **`quick-review` skill** – lightweight in-conversation review that spawns a fresh-context sub-agent for adversarial critique of recent changes. Auto-scopes from pending git changes or conversation context, classifies change type (code, spec, config, docs, prompt) to select the appropriate review lens, and applies anti-leniency principles inline. Designed for mid-conversation sanity checks without the overhead of formal review skills
- **Skill Authoring Philosophy** in CLAUDE.md – codifies intent-driven authoring principles: why over what, right altitude, named principles over unnamed rules, and intent reasoning as non-waste. Establishes the reference point for skill authors to prevent over/under-correction in future edits
- **Structured Output Protocols reference** – new `plugin/references/structured-output-protocols.md` with three named agent-user communication formats (CONFUSION, NOTICED BUT NOT TOUCHING, MISSING REQUIREMENT) for surfacing ambiguity and scope boundaries. Referenced from `exec-spec`, `quick-implement`, `triage`, and `spec`
- **Slicing vocabulary** in FIS authoring guidelines – three named strategies (Vertical, Risk-First, Contract-First) for execution group ordering decisions
- **Named principles** across skills – Chesterton's Fence (`refactor`), Prove-It Pattern (`triage`), Proof-of-Work (`spec`, `exec-spec`), Stop-the-Line (`exec-spec` verification gates), Trust Tiers for external content (`e2e-test`, `triage`)
- **Scenarios and Proof-of-Work** – BDD-inspired Given/When/Then scenarios serve triple duty: requirement, test specification, and proof-of-work contract. Traceable chain across the workflow: `plan` stories seed Key Scenarios (one-line behavioral seeds) → `spec` elaborates them into full Given/When/Then → `exec-spec` scaffolds them as failing tests (Step 1.5) and proves them green during implementation. Concept grounded in Tegmark & Omohundro's verification asymmetry (arXiv:2309.01933)
- **Documentation Source Authority** hierarchy in development guidelines – 4-tier source ranking with explicit exclusion of unreliable sources (Stack Overflow, blog tutorials, AI-generated summaries, training data recall)
- **Restored intent reasoning** in `exec-spec` – three pieces of load-bearing "why" reasoning from the v0.8.7 rationalizations tables that were over-aggressively removed during condensation: why test scaffolding precedes implementation (verifies intent, not incidental behavior), why verification gates exist (prevent cascading failures across groups), and why Step 3 validation differs from Step 2 gates (cross-cutting vs task-level issues)

### Removed
- **Minimal FIS template removed** – `plugin/skills/spec/templates/fis-template-minimal.md` deleted. THIN stories now use the standard FIS template, collected into a single `thin-specs.md` per phase
- **All external plugin dependencies removed** – `code-simplifier` and `frontend-design` plugins are no longer referenced by any skill or agent. AndThen is now fully standalone
  - **`refactor` skill made standalone** – removed all `code-simplifier:code-simplifier` delegation. Refactoring philosophy (preserve behavior, favor readability over cleverness, balance simplification) integrated directly into the skill
  - **`exec-spec` and `quick-implement` code-simplifier references inlined** – replaced external agent delegation with inline intent ("review implemented code for simplification opportunities")
  - **`frontend-design` philosophy integrated into `ui-ux-designer` agent** – bold aesthetic direction, anti-AI-slop stance, typography/color/atmosphere/motion principles added to Visual Design Mode
  - External Dependencies sections removed from CLAUDE.md, README.md, and plugin/README.md

### Changed
- **`spec-plan` THIN stories collected into single file** – THIN specs are no longer written as individual files using the minimal FIS template. All THIN stories are collected into one `{PLAN_DIR}/thin-specs.md` following standard FIS structure, with execution groups organized by story. Leverages existing shared-FIS dedup in `exec-plan`/`exec-plan-team` — exec-spec runs once, remaining stories skip to acceptance gate
- **`spec-plan` COMPOSITE criteria broadened** – added two new grouping signals: same module/directory (stories primarily affecting the same directory per research brief), phase cohesion (all stories in a phase of ≤4 stories sharing an architectural layer). Max composite group size raised from 3 to 5. Shared files threshold relaxed from 50% to any shared files. Guidance added to prefer COMPOSITE over STANDARD when grouping signals exist
- **Shared-FIS Dedup terminology unified** – `exec-plan` and `exec-plan-team` dedup sections now reference both composite and collected thin-specs FIS paths
- **`exec-spec` validation restructured** – quality review (functionality gaps, simplification opportunities) moved from standalone Step 4 into Step 3 as TV04, feeding into the remediation loop (now TV05). Previously, issues found in Step 4 had no fix path. Step numbering updated throughout (old Steps 5/6 → Steps 4/5)
- **Intent engineering overhaul** – all 24 skill prompts condensed to eliminate cross-skill duplication, template over-specification, validation bloat, and emphatic overtriggering. Total prompt volume reduced from ~7,500 to ~4,500 lines (~40% reduction). Post-condensation review restored 30 behavioral details initially over-trimmed (tool references, scope guards, gate instructions, classification rules across 11 skills and references)
- **Shared references extracted** – `report-output-conventions.md`, `adversarial-challenge.md`, `reviewer-roster.md`, `post-completion-guide.md`, `verification-evidence.md` created in `plugin/references/`. Review and execution skills reference these instead of inlining duplicate content
- **`exec-plan-team` worktree default flipped** – sequential execution on the current branch is now the default. Use `--worktree` to opt in to isolated git worktrees (previously the default, with `--no-worktree` as opt-out)
- **`exec-plan-team` branch name generalized** – hardcoded `main` branch references replaced with a `BASE_BRANCH` variable resolved at startup via `git rev-parse --abbrev-ref HEAD`, supporting feature branches and non-main base branches
- **`exec-plan-team` wave overlap** – W2 implementation can now overlap with W1 reviews (worktrees are isolated), but W2 *merge* waits for W1 review completion (`per-story` mode) since reviews may fix code on the base branch. Updated timing diagrams and dependency rules
- **`exec-plan-team` progress reporting** – orchestrator must print status updates (task creation, agent start/complete, wave/merge/review/phase milestones) to the user throughout execution — the user cannot see agent activity directly
- **Spawn templates consolidated** – `exec-plan-team` reduced from 4 spawn templates (implementer/reviewer × worktree/no-worktree) to 2 with inline worktree conditionals
- **PRD template deduplicated** – `plan` skill collapsed from structure enumeration + duplicate markdown template into a single condensed template
- **Quality checklists trimmed** – all skill validation checklists reduced from 12-30 items to 3-5 non-obvious items per skill
- **Rationalizations tables removed** – `exec-spec`, `spec`, and `quick-implement` no longer include "Common Rationalizations" tables (introduced in 0.8.7). The table format micro-managed reasoning; load-bearing intent reasoning from the tables was restored separately as inline explanations (see Added)
- **GOTCHAS sections pruned** – all skills trimmed to genuinely non-obvious hazards only (items the model would not infer from the workflow itself)
- **Emphatic markers reduced** – `MUST`/`NEVER`/`CRITICAL` reserved for genuinely counter-intuitive constraints across all skills
- **review-council-team refocused** – eliminated ~70 lines duplicated from `review-council`, now focuses exclusively on Agent Teams-specific mechanics
- **excalidraw-diagram phases merged** – near-duplicate Phase 4 (Design Refinement) and Phase 5 (Visual Validation) merged into one review-and-refine phase; render code block stated once and referenced
- **wireframes templates replaced** – inline HTML/CSS code blocks replaced with design principles
- **exec-plan review modes** – defined once in a "Review Mode Contract" section instead of restated 3 times
- **Model references made platform-agnostic** – all hardcoded `model: "opus"` / `"sonnet"` / `"haiku"` references now include cross-platform equivalents (`gpt-5.4`, `gpt-5.3-codex`, `gpt-5.4-mini`) and "or similar" to support Codex CLI and other agents
- **Report output resolution order** – `report-output-conventions.md` now explicitly states the `spec directory → target directory → fallback` priority, previously implicit in bullet ordering
- **`review-council-team` fallback corrected** – instructions now consistently point to `andthen:review-council` (was incorrectly `review-code` in one location)

---

## [0.9.0] – 2026-04-09

### Added
- **`spec-plan` research brief** – new Step 1.5 performs all discovery work once via parallel sub-agents (project context, story-scoped file map, shared architectural decisions, external research) before spawning any spec sub-agents. Eliminates redundant per-story codebase scanning, guideline reading, and architecture analysis. Output saved to `{PLAN_DIR}/.research-brief.md`
- **`spec-plan` story classification** – new Step 1.6 automatically classifies stories into three tiers: THIN (orchestrator writes minimal FIS directly), COMPOSITE (one sub-agent covers tightly coupled story groups), and STANDARD (one sub-agent per story). Classification uses research brief data (file maps, shared decisions), not subjective judgment
- **Minimal FIS template** – new `plugin/skills/spec/templates/fis-template-minimal.md` for THIN stories (30-60 line target)
- **FIS authoring guidelines reference** – new `plugin/references/fis-authoring-guidelines.md` extracts shared authoring knowledge (principles, generation guidelines, task grouping heuristics, plan-spec alignment check, self-check) from `spec` into a reusable reference
- **Plan-Spec Alignment Check** – new step in `spec` (and shared guidelines) cross-checks each plan acceptance criterion against FIS Success Criteria before finalizing. Prevents specs from silently narrowing plan requirements
- **Plan Acceptance Gate** – `exec-plan` and `exec-plan-team` now verify each plan acceptance criterion is demonstrably satisfied before marking a story `Done`. Catches scope narrowing that slipped through spec generation
- **Composite FIS support in `plan`** – plan template and Story Catalog now show composite FIS examples where multiple tightly coupled stories share one spec file
- **Composite FIS dedup in `exec-plan` and `exec-plan-team`** – when multiple stories share a composite FIS path, `exec-spec` runs once; constituent stories skip re-execution and go straight to the Plan Acceptance Gate

### Changed
- **`spec-plan` sub-agents no longer invoke `andthen:spec`** – sub-agents now reference the FIS template and authoring guidelines directly, eliminating the indirection of loading spec's full workflow and skipping steps via fast-path guards. Reduces per-sub-agent context by ~200 lines
- **`spec-plan` relaxed wave ordering** – the research brief pre-resolves most inter-story architectural decisions, so stories can be specced in parallel regardless of wave assignment. Falls back to strict wave ordering only when the brief is incomplete
- **FIS template streamlined** – removed inline authoring principles/DON'Ts (moved to shared guidelines reference), removed section descriptions and emoji markers, simplified Architecture Decision to compact/full formats, removed pseudocode blocks and "Outline of New/Changed Files" section
- **`spec` authoring guidelines externalized** – inline FIS Authoring Principles, Key Generation Guidelines, Task Grouping Heuristics, and Self-Check sections replaced with reference to shared `fis-authoring-guidelines.md`
- **`spec` fast-path guards removed** – the `> Fast-path: If a research brief was provided...` blockquotes in Steps 1 and 2 are no longer needed since `spec-plan` no longer invokes `spec`
- **`spec` stricter verification** – Verify lines must now assert described behavior, not just build success. Weak/strong examples added. FIS line target tightened from 200-400 to 100-250
- **`spec` Cross-Group Contracts** – new Task Grouping guidance requiring explicit cross-group interface declarations (sub-agents work in separate contexts with no shared memory)
- **`exec-plan-team` composite task handling** – task naming, worktree management, dependency chains, and merge steps generalized from `{story_id}` to `{task_id}` convention supporting both standard and composite tasks

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
