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

## Setup

Skills reference your project's root agent instruction file (`CLAUDE.md` for Claude Code, `AGENTS.md` for Codex/generic agents) for two things:

- **Project Document Index** – tells skills where to write output (specs, plans, etc.)
- **Project-Specific Guidelines and Rules** – project-specific guidelines and workflow notes (the universal `Foundational Rules, Guardrails and Principles` are wired in separately, above)

See [`plugin/skills/init/templates/CLAUDE.template.md`](skills/init/templates/CLAUDE.template.md) for a starter template.

**Foundational Rules and Guardrails** – [`skills/init/templates/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md`](skills/init/templates/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md) is the source file; `andthen:init` installs it to `docs/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md` in your project and the template wires it in by reference. For stronger adherence, prefer copying its contents into your user-level `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md` once – this works for both Claude Code and Codex with no per-project setup. Alternatives: `@`-import via `@docs/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md` (Claude Code only – Codex treats `@` as literal text); shell-alias injection into the system prompt (terminal workflows only).

### Agent Teams (Optional, Claude Code only)

`exec-plan --team` and `review --council --team` use [Agent Teams](https://code.claude.com/docs/en/agent-teams) for enhanced parallel multi-agent coordination with real-time inter-agent communication. Without `--team`, both use sub-agents with sequential fallback and work across all agents. To enable Agent Teams:

```json
// ~/.claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

## Workflows

Every skill works standalone – no pipeline required. Use them individually for everyday tasks, or compose them into structured workflows for larger efforts. See the [full documentation](../README.md#key-concepts) for detailed workflow diagrams and artifact flow.

**Session management**: The context-intensive skills – `exec-spec`, `plan` (full FIS generation), `exec-plan`, `review --council` – perform best when started in a **clean session**. Pipeline predecessor skills (`clarify`, `prd`, `spec`) will suggest when to start fresh. Standalone skills like `triage`, `quick-review`, and `simplify-code` are lightweight and run well mid-conversation.

**Headless orchestration**: The core pipeline skills (`prd`, `plan`, `spec`, `exec-spec`, `exec-plan`, `review`, `quick-review`, `remediate-findings`) and the supporting skills they call (`architecture`, `ui-ux-design`, `triage`) accept `--auto` / `--headless`. In automation mode they do not ask follow-up questions or emit arrow-prompts, make conservative assumptions, record assumptions/deferred decisions in artifacts or summaries, propagate `--auto` to nested `andthen:*` skill calls that accept it (`ops` is exempt – it is deterministic), and stop with `BLOCKED:` on contract failures or unsafe actions. Multi-story `exec-plan --auto` contains failed stories to their dependency chains: partial work is preserved, dependents are skipped, independent stories continue, and the run exits with an aggregate failure report.

## Skills

Invoke with `/andthen:<skill>` (e.g. `/andthen:triage`, `/andthen:spec`).

> **Not sure where to start?** Run `/andthen:now-what` – it inspects your project state and routes you to the right skill.

### Standalone Skills

Use these individually for everyday development – no setup, no pipeline, no prior artifacts needed.

| Skill | Purpose |
|-------|---------|
| `now-what` | First-stop router – inspects project state and routes to the right skill (use when starting fresh or unsure what to do next) |
| `handoff` | Compact the conversation into a handoff doc a fresh agent can resume from. Triages by durability via the `andthen:ops` skill: mid-flow state (active stories, blockers, decisions, notes) → `STATE.md`; clearly-bounded defensive notes → `LEARNINGS.md` (uncertain entries stay as recommendations); structural decisions → ADR via the `andthen:architecture --mode trade-off` skill. Absent durable files / Index rows reroute to handoff-doc recommendations. Doc lives at `.agent_temp/handoff/handoff-<UTC-ts>.md` and is self-sufficient – resume by pasting `Resume from <doc-path>` into a fresh session. `--no-mutate` opts out of durable writes |
| `triage` | Investigate, diagnose, and fix issues (`--plan-only` for investigation only) |
| `quick-implement` | Fast path for small features/fixes (supports `--issue` for GitHub → auto-PR) |
| `quick-review` | Quick in-conversation sanity-check via fresh-context Critic sub-agent; loads Intent Context (FIS/PRD/clarify) when present so Non-Goals act as falsifiers; routes accepted findings into **Fix** (HIGH/CRITICAL, confidence ≥ 75, primary scope) and **Note** buckets so `--fix` only auto-applies the former; reports Guardrails Coverage for diff-verifiable project rules |
| `review` | Smart review entrypoint: routes to code, doc, gap, security, mixed, or structured multi-perspective council review (`--council` – within-lens specialist debate on `code` / `security`, plus a cross-lens Critic + Devil's Advocate + Synthesis Challenger pass on any chain of 2+ lenses that surfaces lens-boundary contradictions and silence-licenses-risk in a `## Cross-Lens Synthesis` section); loads Intent Context (FIS/PRD/clarify) when present so Non-Goals act as falsifiers; routes accepted findings into **Fix** (HIGH/CRITICAL, confidence ≥ 75, primary scope, no scope expansion past Intent) and **Note** buckets so `--fix` only auto-applies the former; emits Guardrails Coverage with per-finding rule citations; on refactor-shaped diffs (deletion, rename, lifecycle move, cache, codegen, schema migration, parameter threading) the `code`/`gap` lenses run a cross-file refactor-invariants pass; `--fanout` / `--no-fanout` force partition-based sub-agent fan-out for `code`/`gap` (auto on ≥20 files, ≥1000 LOC, or 3+ packages – partitions into vertical slices + a cross-partition boundary pass); `--visual` delegates the consolidated report to the `andthen:visualize` skill for severity-coded triage |
| `simplify-code` | Behavior-preserving code simplification and cleanup; loads Intent Context when present and drops cleanups that contradict Non-Goals, implement deferred outcomes, or restructure code the FIS explicitly chose a shape for (Boy Scout cleanup is intent-bounded, not just behavior-preserving) |
| `refactor` | Deprecated – redirects to `simplify-code` (kept for legacy invocations only) |
| `architecture` | Architecture design, review, decomposition, trade-off analysis, ADRs, fitness functions, strategic design, and event storming (modes: `review`, `decompose`, `advise`, `fitness`, `trade-off`, `strategic-design`, `event-storming`; `trade-off` updates the project's `DECISIONS.md` registry when ADR creation is accepted; `--visual` delegates every mode's primary report – `review`, `trade-off`, `strategic-design`, `fitness`, `decompose`, `event-storming`, and ADR – to `andthen:visualize`) |
| `ui-ux-design` | UI/UX work – research, design systems, wireframes, and design review (modes: `research`, `design-system`, `wireframes`, `review`) |
| `map-codebase` | Codebase analysis – auto-generates architecture, stack, conventions docs (called by `init` or standalone) |
| `testing` | Test strategy, coverage, authoring, and test-first / red-green-refactor discipline (Prove-It for bugfixes) |
| `ubiquitous-language` | Extract and maintain domain glossary from codebase and docs |
| `excalidraw-diagram` | Generate Excalidraw diagram JSON files that make visual arguments |
| `visual-validation` | Validate UI screenshots and implementations against visual, responsive, and design expectations (`andthen:visual-validation` skill) |
| `visualize` | Render any AndThen artifact – PRD, `plan.json`, FIS, requirements-clarification, product vision, review report (any lens), architecture trade-off / strategic-design / fitness / decompose / event-storming report, or ADR – as a self-contained HTML view (inline CSS+JS+SVG, warm-light theme, no external deps); section-anchored notes export via clipboard as a markdown payload identifying the artifact owner (`andthen:prd`, `andthen:plan`, `andthen:spec`, `andthen:clarify`, `andthen:review`, or `andthen:architecture`). Open-loop and read-only. Output: `.agent_temp/visual-review/<slug>-<ts>.html` |
| `e2e-test` | End-to-end browser testing for web applications |

### Pipeline Skills

These compose into structured workflows – from requirements through implementation to review.

| Skill | Purpose |
|-------|---------|
| `init` | Set up AndThen workflow structure (new projects, partial setups, brownfield) |
| `clarify` | Discovery & Ideation – clarify requirements at feature or product scope (`--mode product\|feature`, inferred from INPUT). Always interactive (Interactive-by-Contract; no headless mode). Supports `--issue` for GitHub input, `--to-issue` for publishing, and `--visual` as a convenience handoff to `andthen:visualize` |
| `prd` | Create a Product Requirements Document from requirements (supports `--issue` for GitHub input, `--to-issue` for publishing, and `--visual` as a convenience handoff to `andthen:visualize`) |
| `spec` | Generate Feature Implementation Specification from requirements (supports `--visual` as a convenience handoff to `andthen:visualize` for the produced FIS) |
| `exec-spec` | Execute a FIS – direct implementation with validation |
| `plan` | Full plan bundle: typed `plan.json` (story manifest per `plan-schema.md`) + FIS for every story + cross-cutting review. Requires `prd.md` input. Re-running on a legacy `plan.md`-only bundle migrates to `plan.json` and preserves existing FIS files. Supports `--visual` as a convenience handoff to `andthen:visualize` for the local plan bundle |
| `exec-plan` | Execute a fully-specced plan bundle – reads `plan.json`, runs exec-spec + quick-review per story, final gap review. `--from-issue` materializes a local `plan.json` ledger from a GitHub plan issue. Use `--team` for Agent Teams |
| `remediate-findings` | Implement validated review findings with re-validation and status updates; honors the upstream `Routing: Fix\|Note` tag on each finding and runs a Phase 2a Intent re-anchor against the originating FIS (Non-Goals / deferrals / Expected Outcomes) before any fix is planned – findings that contradict the Intent are surfaced for user decision rather than auto-applied |
| `ops` | Deterministic state management, plan/FIS mutations, Tech Debt and Learnings appends, git conventions, and progress tracking |

> Both `exec-plan` and `review --council` auto-detect Agent Teams and use them when available. Use `--team` to force Agent Teams mode.

## Agents

AndThen ships a small agent set:

- The `andthen:documentation-lookup` agent handles documentation retrieval.
- Review persona agents support `review --council` and Critic review: `review-critic`, `review-devils-advocate`, `review-synthesis-challenger`, `review-correctness`, `review-security`, `review-architecture`, `review-testing`, `review-project-standards`, `review-product-requirements`, and `review-agent-workflow`.

Agent names are tier-specific: Claude Code plugin sources use unprefixed `review-*` names inside `plugin/agents/`; Codex and Claude user-tier installs generate/copy prefixed names such as `andthen-review-critic` or `<custom-prefix>review-critic`. Reinstalls overwrite matching generated files but do not delete stale prefixed agent files.

Architecture, UI/UX design, build/test diagnosis, visual validation, and visual artifact review are **skills** – use `/andthen:architecture`, `/andthen:ui-ux-design`, `/andthen:triage`, `/andthen:visual-validation`, and `/andthen:visualize` where relevant. Research outside documentation lookup remains inline sub-agent guidance embedded in the skill prompts that need it.

Visual review has one renderer owner: `andthen:visualize <artifact-path>`. Producer `--visual` flags remain convenience handoffs: after `clarify`, `prd`, `spec`, `plan`, `review`, or supported `architecture` outputs pass their normal gates, they invoke the visualizer on the produced artifact.

## Usage Examples

### Standalone

```bash
# Debug and fix a broken build
/andthen:triage

# Quick feature or bug fix from a GitHub issue
/andthen:quick-implement --issue 123

# Sanity-check what you just built (mid-conversation)
/andthen:quick-review

# Review current changes, a PR, or a spec/plan
/andthen:review
/andthen:review --pr 42
/andthen:review --mode doc docs/specs/my-feature/plan.json

# Simplify messy code
/andthen:simplify-code src/utils/

# Trade-off analysis – evaluate architectural options, compare alternatives, write an ADR
/andthen:architecture --mode trade-off "caching strategy for API responses"

# Architecture health check
/andthen:architecture src/

# Multi-perspective review with adversarial debate
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
/andthen:visualize docs/research/event-source-vs-snapshot/recommendation.md   # trade-off
/andthen:visualize docs/research/order-domain/strategic-design.md             # strategic-design
/andthen:visualize docs/research/governance/fitness-functions.md              # fitness
/andthen:visualize docs/research/order-service-split/decompose.md             # decompose
/andthen:visualize docs/research/fulfillment-domain/event-storming.md         # event-storming
/andthen:visualize docs/adrs/007-event-sourcing.md                            # ADR
```

#### Architecture Modes

```bash
# Interactive – presents modes and asks what you want to do
/andthen:architecture

# Full architecture health assessment
/andthen:architecture --mode review src/

# Evaluate a split/merge decision
/andthen:architecture --mode decompose src/core

# Propose fitness functions for architectural governance
/andthen:architecture --mode fitness

# Design/advisory guidance grounded in CUPID, DDD, and architectural frameworks
/andthen:architecture --mode advise "should I use event sourcing for the order domain"

# Trade-off analysis – compare options with weighted criteria, produce an evidence-based recommendation and ADR (default; opt out with "No ADR" at Step 5)
/andthen:architecture --mode trade-off "SQL vs document DB for the events store"

# Strategic design – subdomain classification, bounded contexts, context map, UL touchpoints (greenfield + brownfield)
/andthen:architecture --mode strategic-design "order fulfillment domain"

# Event storming – Brandolini-style discovery of pivotal events, hotspots, and subdomain candidates
/andthen:architecture --mode event-storming "loan origination workflow"

# Pin the report destination (any mode) – tier-1 override of the report-location resolver
/andthen:architecture --mode review src/ --output-dir docs/reviews/

# Supports multi-step sessions – after any run, continue with another mode
# (e.g. advise → trade-off → formal ADR, review → decompose → fitness, or
# event-storming → strategic-design → decompose for end-to-end discovery into decomposition)
```

#### Multi-Perspective Review

```bash
# Adaptive review - analyzes scope and selects 5-7 relevant reviewers
/andthen:review --council

# Review specific PR with council
/andthen:review --council --to-pr 123

# Deep security review with multi-perspective council
/andthen:review --mode security --council

# Force partition-based fan-out on a large diff (auto-triggers at ≥20 files /
# ≥1000 LOC / 3+ packages); --no-fanout forces inline when latency matters
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

# 2. Optional: create design assets
/andthen:ui-ux-design --mode wireframes
/andthen:ui-ux-design --mode design-system

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

**GitHub integration surface** (narrow on purpose): `clarify --issue` and `prd --issue` read an issue body as requirements input; `prd --to-issue` and `triage --to-issue` publish markdown reports for stakeholder visibility; `quick-implement --issue` reads an issue body and opens a PR with `Closes #N`; `review --to-pr` and `architecture --to-pr` post reports as PR comments. Everything else is local – use a branch + PR as the transport.

## Migration Notes

See [CHANGELOG.md](../CHANGELOG.md) for full release notes. Entries below cover migration steps for recent releases – both breaking changes and non-breaking shape additions that affect the FIS or plan surfaces consumers parse.

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

Downstream consumers (`exec-plan`, `review --mode gap`, `ops`, `now-what`) read `plan.json` directly. GitHub plan issues continue to use the markdown shape from [`plan-issue-shape.md`](references/plan-issue-shape.md) – `exec-plan --from-issue` materializes a local ledger at `.agent_temp/from-issue-<N>/plan.json` and drives execution from there.

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
