# AndThen Plugin

Lightweight spec-driven development for AI coding agents.

See the [full documentation](../README.md) for workflow overview, usage examples, and setup.

## Installation

```bash
# Add marketplace
/plugin marketplace add IT-HUSET/andthen

# Install plugin
/plugin install andthen
```

**Scope options:**
```bash
/plugin install andthen --scope project   # current project only (default: user scope)
```

**Enable auto-update** (recommended): Run `/plugin`, go to the **Marketplaces** tab, select the `andthen` marketplace, and choose **Enable auto-update**.

**Local install** (repo cloned):
```bash
claude plugin install ./plugin
```

For installing on Codex CLI and other agents, see [Other agents](../README.md#other-agents-codex-cli-aider-cursor) in the full documentation.

## Setup

Skills reference your project's root agent instruction file (`CLAUDE.md` for Claude Code, `AGENTS.md` for Codex/generic agents) for two things:

- **Project Document Index** – tells skills where to write output (specs, plans, etc.)
- **Project-Specific Guidelines and Rules** – project-specific guidelines and workflow notes (the universal `Foundational Rules, Guardrails and Principles` are wired in separately, above)

See [`plugin/skills/init/templates/CLAUDE.template.md`](skills/init/templates/CLAUDE.template.md) for a starter template.

**Foundational Rules and Guardrails** – [`skills/init/templates/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md`](skills/init/templates/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md) is the source file; `andthen:init` installs it to `docs/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md` in your project and the template wires it in by reference. For stronger adherence, prefer copying its contents into your user-level `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md` once – this works for both Claude Code and Codex with no per-project setup. Alternatives: `@`-import via `@docs/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md` (Claude Code only – Codex treats `@` as literal text); shell-alias injection into the system prompt (terminal workflows only).

### Agent Teams (Optional, Claude Code only)

`exec-plan --team` and `review --council --team` use [Agent Teams](https://code.claude.com/docs/en/agent-teams) for enhanced parallel multi-agent coordination with real-time inter-agent communication. `review --council` auto-detects Agent Teams when available even without `--team`; `exec-plan` uses Agent Teams only when `--team` is set. Without Agent Teams, both use sub-agents with sequential fallback and work across all agents. To enable Agent Teams:

```json
// ~/.claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

## Workflows

Every skill works standalone – no pipeline required. Use them individually for everyday tasks, or compose them into structured workflows for larger efforts. See the [full documentation](../README.md#the-workflows) for detailed workflow diagrams and artifact flow.

**Session management**: The context-intensive skills – `exec-spec`, `plan` (full FIS generation), `exec-plan`, `review --council` – perform best when started in a **clean session**. Pipeline predecessor skills (`clarify`, `prd`, `spec`) will suggest when to start fresh. Standalone skills like `triage`, `quick-review`, and `simplify-code` are lightweight and run well mid-conversation.

**Headless orchestration**: The core pipeline skills (`prd`, `plan`, `spec`, `exec-spec`, `exec-plan`, `review`, `quick-review`, `remediate-findings`), standalone execution skills (`quick-implement`, `simplify-code`, `triage`), the deprecated `refactor` passthrough, the first-stop router (`now-what`), and design/review helpers (`architecture`, `ui-ux-design`) accept `--auto`. In automation mode they do not ask follow-up questions or emit arrow-prompts, make conservative assumptions, record assumptions/deferred decisions in artifacts or summaries, propagate `--auto` to nested `andthen:*` skill calls that accept it (`ops` is exempt – it is deterministic), and stop with `BLOCKED:` on contract failures or unsafe actions. Multi-story `exec-plan --auto` contains failed stories to their dependency chains: partial work is preserved, dependents are skipped, independent stories continue, and the run exits with an aggregate failure report.

## Skills

Invoke with `/andthen:<skill>` (e.g. `/andthen:triage`, `/andthen:spec`).

> **Not sure where to start?** Run `/andthen:now-what` – it inspects your project state and routes you to the right skill.

### Standalone Skills

Use these individually for everyday development – no setup, no pipeline, no prior artifacts needed.

| Skill | Purpose |
|-------|---------|
| `now-what` | First-stop router – inspects project state and routes to the right skill (use when starting fresh or unsure what to do next) |
| `handoff` | Compact the conversation into a handoff doc a fresh agent can resume from. Triages by durability via the `andthen:ops` skill: story status/claims → `plan.json` when one governs, else Active Stories rows; blockers/decisions → `STATE.md`; personal notes/focus → the gitignored `STATE.local.md` (auto-created by ops); clearly-bounded defensive notes → `LEARNINGS.md` (uncertain entries stay as recommendations); structural decisions → ADR via the `andthen:architecture --mode trade-off` skill. Absent durable files / Index rows reroute to handoff-doc recommendations. Doc lives at `.agent_temp/handoff/handoff-<UTC-ts>.md` and is self-sufficient – resume by pasting `Resume from <doc-path>` into a fresh session. `--no-mutate` opts out of durable writes |
| `triage` | Investigate, diagnose, and fix build failures, config errors, runtime bugs, regressions, and test failures (`--plan-only` for a fix plan without applying; `--issue` reads a GitHub issue as scope; `--to-issue` files the diagnosis) |
| `quick-implement` | Fast path for small features/fixes – implement + verify, bypassing the FIS workflow (`--tdd` strict red-green-refactor; `--issue` reads a GitHub issue → auto-PR; `--pr` / `--no-pr` control PR creation; `--auto` runs without prompts) |
| `quick-review` | Quick in-conversation sanity-check via fresh-context Critic sub-agent; loads Intent Context (FIS/PRD/clarify) when present so Non-Goals act as falsifiers; routes accepted findings into **Fix** (mechanical/bounded correction needing no design decision, confidence ≥ 75, primary scope – by fix character, not defect severity) and **Note** buckets so `--fix` only auto-applies the former; emits the finding `Class:` axis (`code-defect`/`spec-stale`/`design-changed`/`ambiguous-intent`) so per-story drift is reconciliation-ledger-writable; reports Guardrails Coverage for diff-verifiable project rules |
| `review` | Smart proof-led review entrypoint: runs one lens (`code`, `doc`, `gap`, `security`) or a chain that consolidates into one `mixed` report; every report includes a Coverage Matrix with evidence, positive proof, falsifier attempted, and result for primary surfaces. Test/sign-off artifacts get explicit test-contract falsification; code reviews include the named smell baseline. Optional `--council` adds multi-perspective review; `--fanout` / auto fan-out split semantically wide or large `code`/`gap` surfaces into vertical slices with a boundary pass. Findings keep structured fields plus `Class:` (`code-defect`/`spec-stale`/`design-changed`/`ambiguous-intent`) and `Routing: Fix|Note`; `--fix` sends only Fix-routed findings to the `andthen:remediate-findings` skill. Emits Guardrails Coverage, CONVERGED, and machine-stable `Auto-Remediation: PENDING/STALLED/CLEAR`; `--visual` delegates to the `andthen:visualize` skill |
| `explain-changes` | Explain a PR, branch, ref range, or working tree as a **Changeset Walkthrough** – changes untangled into intent clusters (behavior / refactor / config / tests / docs), ordered narratively, with key diff hunks, per-file risk tags (`attention`/`medium`/`safe`), an architectural-delta module map, reviewer focus points, scope boundary, and verification status – then rendered by the `andthen:visualize` skill as a tabbed interactive app via its bundled deterministic renderer, identical on every agent (Overview change-mosaic + cluster cards · guided cluster Tour with docked module map · Files table with filters and directory sunburst · zoomable Architecture module map; needs Node ≥18, plain-document fallback otherwise; default on, `--no-visual` skips). Comprehension only – no findings, no verdict (use `review` for judgment). Read-only: `--from-pr <N>` reads via `gh` without checkout; `--to-pr [<N>]` posts the walkthrough markdown as a PR comment (number from the flag, `--from-pr`, or the current branch's open PR; splits at the 65,536-char limit); `--auto` for unattended runs. Artifact: `.agent_temp/walkthrough/<slug>-walkthrough-<date>.md` |
| `simplify-code` | Behavior-preserving code simplification and cleanup; loads Intent Context when present and drops cleanups that contradict Non-Goals, implement deferred outcomes, or restructure code the FIS explicitly chose a shape for (Boy Scout cleanup is intent-bounded, not just behavior-preserving) |
| `refactor` | Deprecated – redirects to `simplify-code` with args forwarded verbatim; `--auto` suppresses only the deprecation notice |
| `architecture` | Architecture design, review, decomposition, trade-off analysis, ADRs, fitness functions, strategic design, and event storming (modes: `review`, `decompose`, `advise`, `fitness`, `trade-off`, `strategic-design`, `event-storming`; `trade-off` updates the project's `DECISIONS.md` registry when ADR creation is accepted; `--visual` delegates structured reports – `review`, `trade-off`, `strategic-design`, `fitness`, `decompose`, `event-storming`, and ADR – to the `andthen:visualize` skill; pure `advise` is text-only) |
| `ui-ux-design` | UI/UX work – research, design systems, wireframes, and design review (modes: `research`, `design-system`, `wireframes`, `review`) |
| `map-codebase` | Codebase analysis – auto-generates architecture, stack, Key Dev Commands docs, conventions, and discovered requirements/decisions (called by `init` or standalone) |
| `testing` | Test strategy, coverage assessment, authoring, and TDD / red-green-refactor discipline (modes: `strategy`, `write`, `tdd`, `prove-it`; Prove-It for bugfixes). Unit + integration; defers persistent E2E suites to `e2e-test` |
| `ubiquitous-language` | Extract and maintain the domain glossary from codebase and docs (`--update` merges new terms with the existing glossary) |
| `excalidraw-diagram` | Generate high-quality Excalidraw diagrams from a topic, file, URL, or concept reference – outputs portable `.excalidraw` JSON + a rendered PNG |
| `visual-validation` | Validate UI screenshots and implementations against visual, responsive, and design expectations; use `e2e-test` for browser journeys and `ui-ux-design` for design-system or wireframe authoring (`andthen:visual-validation` skill) |
| `visualize` | Render any AndThen artifact – PRD, `plan.json`, FIS, requirements-clarification, product vision, review report (any lens), changeset walkthrough, architecture review / trade-off / strategic-design / fitness / decompose / event-storming report, or ADR – as a self-contained HTML view (inline CSS+JS+SVG, warm-light theme, no external deps); section-anchored notes export via clipboard as a markdown payload identifying the artifact owner (`andthen:prd`, `andthen:plan`, `andthen:spec`, `andthen:clarify`, `andthen:review`, `andthen:explain-changes`, or `andthen:architecture`). Open-loop and read-only. Output: `.agent_temp/visual-review/<slug>-<ts>.html` |
| `e2e-test` | End-to-end browser testing for web apps – discovers user journeys, runs interactive tests, fixes bugs found, and validates responsive behavior across viewports (`--focus` to scope to specific routes/features) |

### Pipeline Skills

These compose into structured workflows – from requirements through implementation to review.

| Skill | Purpose |
|-------|---------|
| `init` | Set up AndThen workflow structure (new projects, partial setups, brownfield) |
| `clarify` | Discovery & Ideation – interactive requirements discovery at feature or product scope (`--mode product\|feature`, inferred from INPUT). Feature scope → `requirements-clarification.md`; product scope → `PRODUCT.md` (vision, personas, value props, anti-goals). Always interactive (Interactive-by-Contract; no headless mode). Supports `--issue` for GitHub input, `--to-issue` for publishing, and `--visual` as a convenience handoff to the `andthen:visualize` skill |
| `prd` | Create a Product Requirements Document from requirements. Conversationally, load-bearing gaps are resolved by invoking the `andthen:clarify` skill inline rather than assumed (under `--auto`, assumed conservatively); produces a self-contained `prd.md` (no links to transient discovery artifacts); runs an automatic fresh-context doc self-review via the `andthen:review` skill with `--mode doc --fix` before finishing. Supports `--issue` for GitHub input, `--to-issue` for publishing, and `--visual` as a convenience handoff to the `andthen:visualize` skill |
| `spec` | Generate Feature Implementation Specification from requirements; after save, runs an automatic fresh-context doc self-review via the `andthen:review` skill with `--mode doc --fix` and blocks `spec-ready` on unresolved architecture/requirements decision Notes. Supports `--visual` as a convenience handoff to the `andthen:visualize` skill for the produced FIS |
| `exec-spec` | Execute a FIS – direct implementation with validation, intent/gap review, mechanism-aware Chain Attestation, and a design-change reconciliation path when the implementation legitimately diverges from the FIS. When an amendment leaves an upstream doc (PRD section, sibling FIS, public doc, missing ADR) stale, opens a reconciliation-ledger entry (entry-write precedes any AUTO_MODE `BLOCKED:` so deferred pivots aren't lost) and emits a recommend-only As-Built Upstream Reconciliation recommendation; a completion-presentation gate refuses to present the standalone run as shipped while OPEN/`RECONCILE REQUIRED` entries exist (per-story status writes stay ungated). (`--tdd` strict red-green-refactor per scenario; `--to-pr` posts a completion summary) |
| `plan` | Full plan bundle: typed `plan.json` (story manifest per `plan-schema.md`) + an on-disk FIS for every story + cross-cutting review. Consumes a local `prd.md`, `--issue <N>`, or a GitHub issue URL. Re-running on a legacy `plan.md`-only bundle migrates to `plan.json` and preserves existing FIS files. Supports `--visual` as a convenience handoff to the `andthen:visualize` skill for the local plan bundle |
| `exec-plan` | Execute a fully-specced plan bundle – reads `plan.json`, runs exec-spec + quick-review per story, final gap review. The per-story gate is **Fix-routed** quick-review findings only; accepted **Note-routed** findings don't fail the story – they're recorded as surfaced notes and rolled up at completion for human review. On partial runs the final gap review now runs scoped to completed stories (with a loud warning naming unreviewed skipped/failed stories) instead of being skipped wholesale; at completion it emits one consolidated As-Built Upstream Reconciliation rollup across stories and applies the completion-presentation gate (ungated per-story writes). `--from-issue` materializes a local `plan.json` from a GitHub plan issue. Use `--team` for Agent Teams |
| `preflight` | Drive a single FIS or a plan bundle to **zero open blocking decisions** before an unattended `exec-spec`/`exec-plan` run. Auto-detects the target (FIS file vs. directory with `plan.json`; ambiguous/missing → ask, or `BLOCKED:` under `--auto`). Interactive-by-Contract: detects decisions via the `andthen:review` skill (`--mode doc --inline-findings`), settles open ADRs inline via the `andthen:architecture` skill (`--mode trade-off`), routes requirements-altitude gaps to the `andthen:clarify` skill, resolves implementation-blocking decisions with its own interview, and persists each resolution by altitude through the `andthen:ops` skill (FIS decision-Note / `DECISIONS.md` Still Current note / ADR); converged bundle stories flip to `spec-ready`. Emits a machine-stable `Preflight: READY \| DEFERRED \| BLOCKED` verdict (one resolved token, line-anchored). Under `--auto` it never interviews and never fabricates an answer – it enumerates the unresolved blocking decisions as a signal. Recommended gate, never required by the executors (interactive skill, headless-deadlock risk) |
| `remediate-findings` | Implement validated review findings with re-validation and status updates; honors the upstream `Routing: Fix\|Note` tag on each finding and runs a Phase 2a Intent re-anchor against the originating FIS (Non-Goals / deferrals / Expected Outcomes) before any fix is planned – findings that contradict the Intent are surfaced for user decision rather than auto-applied; when a valid report has findings but none are auto-applicable (all Note/SURFACED), returns a machine-stable `NO-OP: no-auto-applicable-findings` terminal signal (bare line-anchored grammar, distinct from `BLOCKED:`) so a consuming loop escalates once to a human instead of re-reviewing; Phase 5 transitions reconciliation-ledger entries (applied reconciliation → CLOSED; finding judged invalid → WITHDRAWN + falsifier) and opens a new entry when a fix or applied intent-misaligned finding leaves code diverging from its governing FIS (remediation-introduced drift), keeping PRD-targeted reconciliations recommend-only |
| `ops` | Deterministic state management, plan/FIS mutations, Tech Debt and Learnings appends, git conventions, and progress tracking. `update-state` routes by field: `note`/`focus` → the gitignored `STATE.local.md` (auto-created), everything else (`phase`/`status`/`active-story`/`blocker`/`decision`) → shared `STATE.md`. `update-plan-owner` sets the optional story `owner` (story claiming). `read-state` derives the Active Stories view from `plan.json` (in-progress or claimed stories) when a plan governs, else falls back to the stored `STATE.md` table. `update-fis design-change` is the audited mutation path for ADR-backed Intent/scenario amendments (missing requirements still use `discovered-requirements`); `update-fis decision-note <key> <resolved\|deferred>` records a preflight decision as a `#### DECISION NOTE` (under `## Implementation Observations`) or `#### DEFERRED DECISION` (under `## Deferred Decisions`, requiring `Signed-off-by:`); `update-decisions still-current <topic>` appends a load-bearing non-ADR choice to the `DECISIONS.md` `## Still Current` registry; `update-ledger` (`add`/`reconcile`/`withdraw`/`bump-recurrence`/`override-close`) is the deterministic single-document mutator for the reconciliation ledger |

> `review --council` auto-detects Agent Teams and uses them when available; `--team` forces the mode. `exec-plan` is `--team`-gated – it uses Agent Teams only when `--team` is passed, otherwise sub-agents.

## Agents

AndThen ships a small agent set:

- The plugin-tier `documentation-lookup` agent handles documentation retrieval.
- The plugin-tier `research` agent handles web and project research, multi-source verification, and trade-off option investigation (used by `architecture --mode trade-off` and `prd`).
- Review persona agents support `review --council` and Critic review: `review-critic`, `review-devils-advocate`, `review-synthesis-challenger`, `review-correctness`, `review-security`, `review-architecture`, `review-testing`, `review-project-standards`, `review-product-requirements`, and `review-agent-workflow`.

Agent names are tier-specific: Claude Code plugin sources use unprefixed `documentation-lookup` and `review-*` names inside `plugin/agents/`; Codex and Claude user-tier installs generate/copy prefixed names such as `andthen-documentation-lookup`, `andthen-review-critic`, or `<custom-prefix>review-critic`. Reinstalls overwrite matching generated files but do not delete stale prefixed agent files.

Architecture, UI/UX design, build/test diagnosis, visual validation, and visual artifact review are **skills** – use `/andthen:architecture`, `/andthen:ui-ux-design`, `/andthen:triage`, `/andthen:visual-validation`, and `/andthen:visualize` where relevant. Research outside documentation lookup remains inline sub-agent guidance embedded in the skill prompts that need it.

Visual review has one renderer owner: `andthen:visualize <artifact-path>`. Producer `--visual` flags remain convenience handoffs: after `clarify`, `prd`, `spec`, `plan`, `review`, or supported `architecture` outputs pass their normal gates, they invoke the visualizer on the produced artifact.

## Usage Examples

**You rarely need the flags.** Most examples below can be expressed in plain language – describe what you want and the skill routes it (mode-driven skills like `architecture`, `ui-ux-design`, and `review` infer the mode/lens from your phrasing; a menu appears only when the intent is genuinely ambiguous). The flag form is shown as the explicit equivalent. The exceptions are deliberate opt-ins that are **never** inferred from phrasing because they cost tokens, write, or post externally – `--council`, `--team`, `--worktree`, `--fix`, `--to-pr`, `--to-issue`. Reach for those explicitly.

### Standalone

```bash
# Debug and fix a broken build
/andthen:triage

# Quick feature or bug fix from a GitHub issue ("fix issue 123" → note: --issue auto-opens a PR)
/andthen:quick-implement --issue 123

# Sanity-check what you just built (mid-conversation)
/andthen:quick-review

# Review current changes, a PR, or a spec/plan – say what to review, or name the lens
/andthen:review                                       # current changes, lens auto-detected
/andthen:review "does this match the spec?" <path>    # → gap lens
/andthen:review "review PR 42"                        # → --from-pr 42 (read-only)
/andthen:review --mode doc docs/specs/my-feature/plan.json
/andthen:review --mode gap,code,security        # chain lenses → one consolidated report
/andthen:review --from-pr 42 --to-pr 42         # --to-pr posts on the PR (explicit opt-in)

# Understand a PR or branch before reviewing it – interactive HTML walkthrough
/andthen:explain-changes --from-pr 42
/andthen:explain-changes main                   # current branch vs main
/andthen:explain-changes --from-pr 42 --to-pr   # also post the walkthrough on the PR

# Simplify messy code
/andthen:simplify-code src/utils/

# Trade-off analysis – naming the intent routes the mode; no --mode needed
/andthen:architecture "compare caching strategies for API responses"   # → trade-off mode
/andthen:architecture --mode trade-off "caching strategy for API responses"   # explicit equivalent

# Architecture health check
/andthen:architecture src/                      # → review mode (default)

# Multi-perspective review with adversarial debate (explicit opt-in – spends tokens/agents)
/andthen:review --council

# Understand a new codebase
/andthen:map-codebase

# Build a domain glossary
/andthen:ubiquitous-language

# Draw an architecture or workflow
/andthen:excalidraw-diagram "data pipeline architecture"

# Render existing artifacts as self-contained HTML review surfaces
# with section-anchored notes (notes round-trip to downstream skills via clipboard)
/andthen:visualize docs/specs/auth-feature/prd.md
/andthen:visualize docs/specs/auth-feature/plan.json
/andthen:visualize docs/specs/auth-feature/requirements-clarification.md
/andthen:visualize docs/specs/auth-feature/s01-login.md                       # FIS
/andthen:visualize docs/specs/auth-feature/s01-login-doc-review-claude-*.md   # review report
/andthen:visualize .agent_temp/walkthrough/pr-42-walkthrough-2026-06-12.md    # changeset walkthrough
/andthen:visualize docs/research/event-source-vs-snapshot/recommendation.md   # trade-off
/andthen:visualize docs/research/order-domain/strategic-design.md             # strategic-design
/andthen:visualize docs/research/governance/fitness-functions.md              # fitness
/andthen:visualize docs/research/order-service-split/decompose.md             # decompose
/andthen:visualize docs/research/fulfillment-domain/event-storming.md         # event-storming
/andthen:visualize docs/adrs/007-event-sourcing.md                            # ADR
```

#### Architecture Modes

The mode is inferred from your phrasing – you only need `--mode` to force a mode or when the intent is genuinely ambiguous (then the skill presents the menu). Each line below shows the natural phrasing; the `→ mode` comment is what it resolves to.

```bash
# No mode, no scope → presents the mode menu (only when genuinely ambiguous)
/andthen:architecture

# Full architecture health assessment
/andthen:architecture "assess the health of" src/                         # → review
/andthen:architecture src/                                                # → review (default)

# Evaluate a split/merge decision
/andthen:architecture "should I split" src/core                           # → decompose

# Propose fitness functions for architectural governance
/andthen:architecture "propose fitness functions for governance"          # → fitness

# Design/advisory guidance grounded in CUPID, DDD, and architectural frameworks
/andthen:architecture "should I use event sourcing for the order domain?"  # → advise

# Trade-off analysis – compare options with weighted criteria, produce an evidence-based recommendation and ADR
/andthen:architecture "compare SQL vs document DB for the events store"   # → trade-off

# Strategic design – subdomain classification, bounded contexts, context map, UL touchpoints
/andthen:architecture "model the order fulfillment domain"                # → strategic-design

# Event storming – Brandolini-style discovery of pivotal events, hotspots, and subdomain candidates
/andthen:architecture "event storming for the loan origination workflow"  # → event-storming

# Force a specific mode explicitly (equivalent to the inferred forms above)
/andthen:architecture --mode decompose src/core

# Pin the report destination (any mode) – tier-1 override of the report-location resolver
/andthen:architecture --mode review src/ --output-dir docs/reviews/

# Supports multi-step sessions – after any run, continue with another mode
# (e.g. advise → trade-off → formal ADR, review → decompose → fitness, or
# event-storming → strategic-design → decompose for end-to-end discovery into decomposition)
```

#### Multi-Perspective Review

`--council`, `--fanout`, and `--team` are explicit opt-ins – phrasing never triggers them (they spend tokens/agents). Phrasing still picks the *lens* inside a council; the flag just opts into the council itself.

```bash
# Adaptive review - analyzes scope and selects 5-7 relevant reviewers
/andthen:review --council

# Review specific PR with council (PR read from NL; --to-pr posts back, explicit)
/andthen:review "review PR 123" --council
/andthen:review --from-pr 123 --to-pr 123 --council      # explicit + post findings on the PR

# Deep security review with multi-perspective council (NL picks the lens, flag opts into council)
/andthen:review "security review" --council
/andthen:review --mode security --council                # explicit equivalent

# Force partition-based fan-out (auto-triggers on a large or semantically wide
# surface – see the review skill's large-diff-fanout triggers); --no-fanout forces inline
/andthen:review --mode code --fanout

# Chain + council – per-lens reviews plus a cross-lens Critic pass over the
# merged findings; produces a `## Cross-Lens Synthesis` section above the
# per-lens sections that surfaces contradictions and silence-licenses-risk
# (e.g. a doc gap masking a correctness regression).
/andthen:review --mode doc,code,gap --council

# Reviewers auto-selected based on changes:
# - Product features → Product Requirements, Correctness, Architecture, Standards
# - Backend APIs → Correctness, Architecture, Testing, Standards
# - Prompt/skill changes → Agent Workflow, Standards, Testing
# - Security-mode councils → Security Sentinel + 1-3 surface specialists
# - Always includes Critic Reviewer + Devil's Advocate + Synthesis Challenger
# - Chain + council adds a fixed-spine cross-lens pass (Critic / DA / Synthesis Challenger)
#   over per-lens outputs; no extra specialists at the cross-lens scope

# OR force Agent Teams for real-time debate (Claude Code only)
/andthen:review --council --team
```

### Feature Workflow (single feature)

```bash
# 1. Clarify vague requirements (interactive)
/andthen:clarify "users should be able to export their data"
/andthen:clarify --issue 42   # or from a GitHub issue
# → docs/specs/data-export/requirements-clarification.md

# 2. Generate implementation spec (picks up clarified requirements automatically)
/andthen:spec docs/specs/data-export/

# 3. Execute the spec (path printed by spec)
/andthen:exec-spec <path-to-fis>

# 4. Final review (against requirements)
/andthen:review --mode gap <path-to-fis>

# 5. If the review reports actionable findings:
/andthen:remediate-findings <path-to-review-report>
```

### Plan Workflow (MVP / multi-feature)

```bash
# 1. Clarify requirements (optional)
/andthen:clarify "dashboard for analytics"

# 2. Optional: create design assets (mode inferred from phrasing, or forced with --mode)
/andthen:ui-ux-design "wireframe the dashboard screens"    # → wireframes
/andthen:ui-ux-design "create a design system" <reqs>      # → design-system
/andthen:ui-ux-design --mode wireframes                    # explicit equivalent

# 3a. Create the PRD
/andthen:prd docs/specs/dashboard/
/andthen:prd --issue 42            # read from a GitHub issue
/andthen:prd --to-issue docs/specs/dashboard/   # publish PRD to a GitHub issue for stakeholder review

# 3b. Create the full plan bundle (story breakdown + FIS for every story)
/andthen:plan docs/specs/dashboard/

# 4a. Execute all stories via pipeline (default per-story review)
/andthen:exec-plan docs/specs/dashboard/

# 4b. OR use Agent Teams for enhanced parallelism (Claude Code only)
/andthen:exec-plan --team docs/specs/dashboard/
# Or with worktree isolation for parallel execution:
/andthen:exec-plan --team --worktree docs/specs/dashboard/

# 4c. OR execute story by story manually (plan already produced FIS for every story):
/andthen:exec-spec docs/specs/dashboard/s01-project-setup.md
/andthen:review --mode gap docs/specs/dashboard/s01-project-setup.md
/andthen:remediate-findings <path-to-review-report>   # when review reports actionable gaps
# ... repeat exec-spec + review (+ remediation when needed) for each story in per-story mode

# 5. Final review (single-feature workflow, or manual review after exec-plan)
/andthen:review --mode gap
```

**GitHub integration surface** (narrow on purpose): `clarify --issue` and `prd --issue` read an issue body as requirements input; `prd --to-issue` and `triage --to-issue` publish markdown reports for stakeholder visibility; `quick-implement --issue` reads an issue body and opens a PR with `Closes #N`; `review --from-pr` and `explain-changes --from-pr` read a PR as scope (also inferable from NL – "review PR 42"); `review --to-pr`, `architecture --to-pr`, and `explain-changes --to-pr` post reports as PR comments. The read-only side (`clarify`/`prd`/`plan`/`triage --issue`, `review`/`explain-changes --from-pr`) is safe to infer from phrasing; anything that writes or publishes is always an explicit flag, never triggered by phrasing – this includes `--to-issue`, `--to-pr`, and `quick-implement --issue` (which opens a PR with `Closes #N`, so despite reading an issue it is not phrasing-inferable). Everything else is local – use a branch + PR as the transport.

## Working in a Team

AndThen supports multiple people working the same repo concurrently. The design principle is **shared contract + per-developer runtime**: artifacts split cleanly so teammates rarely touch the same bytes.

- **State is split.** Shared `STATE.md` (committed) holds team-wide, low-churn state – phase, blockers, decisions, recently-completed, and an owner-annotated Active Stories view. Your personal context – current focus, session continuity notes – lives in `STATE.local.md`, which `andthen:init` **gitignores**, so it never merge-conflicts.
- **`plan.json` is the source of truth for "who's doing what".** It already supports multiple `in-progress` stories at once. Claim a story by setting its `owner` (`andthen:ops update-plan-owner <plan> <id> <you>`) and opening its branch – `owner` is advisory coordination, not a lock, but it makes claims visible so two people don't grab the same story. Surgical per-row edits and fixed key order let concurrent status/owner updates 3-way merge cleanly across branches; in a single shared checkout they are last-writer-wins – prefer the `--from-issue` per-developer workflow there.
- **Branch per story.** Use the `feat/S03-...` convention (`andthen:ops branch`), land via PR, and let `dependsOn` order the work. Per-story FIS files and per-FIS reconciliation ledgers are naturally partitioned – different stories touch different files.
- **GitHub issues as the durable contract (recommended team mode).** `andthen:plan --to-issue` publishes the Story Catalog (with an optional `Owner` column) to an issue; each developer runs `andthen:exec-plan --from-issue <N>`, which materializes a *private* local `plan.json` under `.agent_temp/` and generates FIS just-in-time. The issue is the shared contract, runtime state is per-developer, so there is nothing shared to clobber. Claim a story by editing its `Owner` cell on the issue – reruns of `--from-issue` refresh `owner` from it, so claims and un-claims propagate to every teammate's local plan. (`--from-issue` is mutually exclusive with the intra-session `--team` mode – combining the flags is rejected.)
- **Append-logs are merge-friendly.** `LEARNINGS.md`, `TECH-DEBT-BACKLOG.md`, `DECISIONS.md`, and `CHANGELOG.md` use timestamped, idempotent append blocks via `andthen:ops`, so concurrent appends rarely conflict and resolve trivially when they do.

## Bundling Into a Downstream Toolkit

Niche, for toolkit authors only. Other workflow toolkits (e.g. DartClaw) can pull AndThen in under their own prefix so the two coexist without namespace collisions. The pattern is clone + install:

```bash
git clone --depth 1 https://github.com/IT-HUSET/andthen /tmp/andthen

# User-tier install (~/.claude/skills, ~/.claude/agents, ~/.agents/skills, ~/.codex/agents):
/tmp/andthen/scripts/install-skills.sh --prefix dartclaw- --claude-user

# Project-local Claude Code install (target <project>/.claude/):
/tmp/andthen/scripts/install-skills.sh --prefix dartclaw- \
  --claude-skills-dir "$PWD/.claude/skills" \
  --claude-agents-dir "$PWD/.claude/agents"
```

Each downstream picks its own `--prefix` (must end with `-`). Skills install as `<prefix><name>` and on Claude Code are invokable as `/<prefix><name>`. The AndThen Claude Code plugin can be installed alongside without conflict as long as the prefixes differ.

`--claude-skills-dir` overrides the Claude-side skill destination and implies a Claude Code user-tier install (no separate `--claude-user` needed). Pair it with `--claude-agents-dir` for fully project-local Claude agents. The generic skill target (`--skills-dir`) defaults to `~/.agents/skills`; pass it too for a fully project-local bundle.

## Migration Notes

See [CHANGELOG.md](../CHANGELOG.md) for full release notes. Entries below cover migration steps for recent releases – both breaking changes and non-breaking shape additions that affect the FIS or plan surfaces consumers parse.

### 0.29.0 – New `explain-changes` skill + changeset-walkthrough artifact type (non-breaking addition)

A new `andthen:explain-changes` skill produces a **Changeset Walkthrough** markdown artifact (`.agent_temp/walkthrough/<slug>-walkthrough-<date>.md`) and the `andthen:visualize` skill gains a matching `changeset-walkthrough` artifact type (detection: H1 starts with "Changeset Walkthrough", or H2 set contains both "Change Map" and "Change Narrative"; notes-payload owner: `andthen:explain-changes`). This type renders via a bundled deterministic Node script (`skills/visualize/scripts/render-changeset.mjs`, Node ≥18, no dependencies) rather than model-authored HTML; without Node it degrades to a plain document render. Existing artifact types, detection order outcomes, and the notes payload format are unchanged; the visualizer's exact no-match error message now also lists changeset walkthroughs. Parsers that enumerate supported types should add the new one.

**To migrate**: no action required; existing artifacts and downstream consumers are unaffected.

### 0.28.0 – Shared vs. session-local state split (non-breaking shape addition)

Session Continuity Notes and current focus now live in a per-developer, **gitignored** `STATE.local.md` instead of the shared `STATE.md`; the `andthen:ops` skill routes `note`/`focus` there and keeps everything else in the shared file. `STATE.md` also gains an `Owner` column on the Active Stories table (derived from `plan.json` when one exists), and the GitHub plan-issue Story Catalog gains an optional trailing `Owner` column. Solo workflows and existing single-file `STATE.md` files keep working – `read-state` merges both files and treats the local one as optional.

**To migrate** an existing repo: move any `## Session Continuity Notes` (and personal "current focus" lines) out of the committed `STATE.md` into a new `docs/STATE.local.md` and gitignore it (re-running the `andthen:init` skill does this idempotently). Left in place, those notes are orphaned – `ops` no longer maintains them and `read-state` surfaces them alongside the local copy.

### 0.22.0 – Review reports gain `Routing:` field + `Intent Context:` line (non-breaking shape addition)

The `andthen:review` skill and the `andthen:quick-review` skill now route each accepted finding into a **Fix** or **Note** bucket and emit a `Routing: Fix | Note` field per finding plus a one-line `Intent Context:` line in the report or inline-result header. The `andthen:remediate-findings` skill reads both: `Routing: Note` findings are surfaced (`SURFACED` in the findings re-check) rather than auto-applied, and a new Phase 2a Intent re-anchor demotes findings that contradict Non-Goals or deferrals from the originating FIS – even when upstream tagged them `Routing: Fix`. Reports without these fields (older `andthen:review` skill reports, external reports) execute under the prior behavior; routing degrades to the existing severity policy alone. The `andthen:simplify-code` skill also loads Intent Context and drops cleanups that contradict it (no report consumption, just self-anchoring).

**To migrate**, no action required for existing reports. New reports automatically carry the fields; remediation honors them on first re-run.

### 0.22.0 – `--council` scales with chain shape (behavior change + non-breaking shape addition)

`andthen:review --council` now scales with the chain shape. Single `code` / `security` still run within-lens specialist councils (unchanged). On any chain of 2+ lenses a new **cross-lens Critic + Devil's Advocate + Synthesis Challenger pass** runs after the per-lens reviews and surfaces lens-boundary issues (contradictions, silence-licenses-risk, verdict-vs-finding mismatch) in a new `## Cross-Lens Synthesis` H2 placed above the per-lens sections of the consolidated `mixed-review` report. The mode token stays `mixed` and per-lens sections are unchanged, so the `andthen:remediate-findings` skill and the `andthen:visualize` skill continue to parse and render correctly (the visualizer falls through to its generic-prose renderer for the new H2 until a first-class template lands).

**Behavior change most likely to surprise**: `--council` with a single-lens `--mode doc` or `--mode gap` now rejects up-front (`BLOCKED: --council requires code/security in scope or a chain of 2+ lenses`). Previously the resolver silently appended `code` or `security` so the council ran on an unrelated lens; that "Chain contains neither" auto-append has been dropped in favor of explicit rejection. To get a council over doc/gap-shaped surface, add another lens to the chain (e.g. `--mode doc,code` or `--mode doc,code,gap --council`).

**To migrate**: scripted `--mode doc --council` / `--mode gap --council` invocations need updating to either drop `--council` or add another lens. New chain + `--council` reports automatically carry the `## Cross-Lens Synthesis` section; downstream skills require no changes.

### 0.21.1 – FIS Intent + Expected Outcomes (non-breaking shape addition)

`## Feature Overview and Goal` now carries two load-bearing sub-blocks: `**Intent**:` (one sentence) and `**Expected Outcomes**:` (2-4 bullets, each `[OC<NN>]`-tagged). The canonical Acceptance Scenario shape gains an outcome-tag set: `- [ ] **S<NN> [OC<NN>(,OC<NN>)*] [TI<NN>(,TI<NN>)*] <description>**`. The FIS structural-integrity contract is unchanged so legacy 0.21.0 FIS files keep executing under the `andthen:exec-spec` skill; the `andthen:review --mode doc` skill flags them on the new Self-Check gates (`Intent vs. scope`, `Outcome ↔ Scenario coverage`, `Task ↔ Scenario coverage`).

**To migrate**, run `/andthen:spec` (or `/andthen:plan` for a multi-story bundle) to regenerate, or hand-edit `## Feature Overview and Goal` and add `[OC<NN>]` tags to scenarios.

### 0.21.0 – FIS format v2

The FIS structural-integrity contract now gates on `## Acceptance Scenarios` + `## Implementation Plan`; the v1 `## Success Criteria` heading no longer satisfies the gate, and `## Final Validation Checklist` is dropped from required sections to optional content. Older v1 FIS files fail the gate intentionally.

**Section-pattern surface**:
- *Always-present* (heading + body always emitted): Feature Overview and Goal, Acceptance Scenarios, Structural Criteria, Work Areas, What We're NOT Doing, Architecture Decision, Code Patterns, Constraints & Gotchas, Implementation Tasks, Implementation Observations.
- *Visible-empty with prompt* (heading always emitted, body carries a "**Leave empty** when…" blockquote): Technical Overview, Testing Strategy, Validation, Execution Contract, Final Validation Checklist.
- *Content-conditional omit* (heading dropped entirely when there is nothing to inline): Required Context, Deeper Context.
- *Off-template* (overlaps with exec-spec's named-blocks runtime escalation): `### Agent Decision Authority`.

Consuming-skill alignment: `exec-spec`, `ops`, `spec`, `plan`, `review`, `now-what`, `exec-plan`, `remediate-findings`, `visualize`.

**To migrate**, re-spec older FIS files – there is no automated migration tool. Run `/andthen:spec` (or `/andthen:plan` for a multi-story bundle) against the existing requirements baseline to regenerate FIS files in v2 shape.

### 0.19.0 – `plan.md` → `plan.json`

`andthen:plan` now emits a typed `plan.json` manifest ([schema](references/plan-schema.md)) instead of the prior `plan.md` markdown table. Mutability is contractually narrower: story `status` and `fis` are mutable only via `andthen:ops update-plan` / `update-plan-fis`; every other field is immutable between full plan regenerations, enforced by a `metadata.immutableDigest` baseline that refuses non-`ops` writes. Superseded in 0.20.0 – see the 0.20.0 `### Removed` entry in [CHANGELOG.md](../CHANGELOG.md).

**To migrate an existing bundle**, re-run `/andthen:plan <dir>`:
- The legacy `plan.md` Story Catalog is parsed once and `plan.json` is written next to it.
- For each migrated story whose `FIS` cell pointed at an existing file, the FIS path and migrated status are preserved – **FIS regeneration is skipped**.
- Stories with sentinel or missing FIS paths get `fis: null`, `status: "pending"`, and FIS generation runs as on a fresh plan.
- The legacy `plan.md` is left in place for you to delete; downstream skills ignore it.

Downstream consumers (`exec-plan`, `review --mode gap`, `ops`, `now-what`) read `plan.json` directly. GitHub plan issues continue to use the markdown shape from [`plan-issue-shape.md`](references/plan-issue-shape.md) – `exec-plan --from-issue` materializes a local `plan.json` at `.agent_temp/from-issue-<N>/plan.json` and drives execution from there.

### 0.18.0 – `andthen:plan` flags removed; story shape compacted

- `--skip-specs`, `--stories`, and `--phase` removed. Re-run `/andthen:plan <dir>` to fill every missing FIS; for a single story, use `/andthen:spec story <id> of <plan>`. Legacy invocations now fail with a targeted removal message.
- Plan story sections are now compact briefs – `Status`, `FIS`, phase/wave, dependencies, parallelism, and risk live only in the Story Catalog. Detailed Acceptance Scenarios and Structural Criteria live in the per-story FIS.
- Plan `Dependencies` cells accept only `-` or comma-separated Story IDs from the same Story Catalog. Broad sequencing prose belongs in `## Dependency Graph`, phase notes, or execution guidance.

### 0.14.0 – `plan` is 1:1 with FIS

- Removed THIN / COMPOSITE story tiers. Every story now maps to exactly one FIS file; no two stories share a FIS path.
- `exec-plan` and `exec-spec` dropped composite / shared-FIS handling. Re-run `/andthen:plan <dir>` on legacy bundles – the Consolidation Pass merges candidates at breakdown time.
- FIS size sweet spot raised to `150–450` lines; oversize-pivot trigger raised to `>600 lines or >18 tasks`.

### 0.13.0 – plan altitudes and unified review

**Plan side** – three altitudes: `prd` (product), `plan` (stories + FIS bundle), `exec-plan` (execution).

| Before | After |
|---|---|
| `/andthen:plan <requirements>` | `/andthen:prd <requirements>` → `/andthen:plan <dir-with-prd>` |
| `/andthen:spec-plan <plan-dir>` | `/andthen:plan <plan-dir>` (re-run fills missing FIS) |
| `/andthen:exec-plan <plan-dir>` (auto-spec per phase) | `/andthen:plan <plan-dir>` → `/andthen:exec-plan <plan-dir>` |

**Review side** – one user-facing skill with modes instead of separate delegates.

| Before | After |
|---|---|
| `/andthen:review-code`, `/andthen:review-doc`, `/andthen:review-gap` | `/andthen:review --mode code\|doc\|gap` |
| `/andthen:review --code-only` / `--doc-only` / `--gap-only` | `/andthen:review --mode code\|doc\|gap` |

Severity scale unified: `SUGGESTIONS` → `LOW`. Gap-mode PASS/FAIL verdict contract preserved.

## Release Notes

See [CHANGELOG.md](../CHANGELOG.md) for release notes.

## License

MIT
