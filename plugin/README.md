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

Skills reference your project's `CLAUDE.md` for two things:

- **Project Document Index** – tells skills where to write output (specs, plans, etc.)
- **Workflow Rules, Guardrails and Guidelines** – behavioral rules and development standards

See [`plugin/skills/init/templates/CLAUDE.template.md`](skills/init/templates/CLAUDE.template.md) for a starter template.

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

Every skill works standalone — no pipeline required. Use them individually for everyday tasks, or compose them into structured workflows for larger efforts. See the [full documentation](../README.md#key-concepts) for detailed workflow diagrams and artifact flow.

**Session management**: The context-intensive skills — `exec-spec`, `plan` (full FIS generation), `exec-plan`, `review --council` — perform best when started in a **clean session**. Pipeline predecessor skills (`clarify`, `prd`, `spec`) will suggest when to start fresh. Standalone skills like `triage`, `quick-review`, and `refactor` are lightweight and run well mid-conversation.

**Headless orchestration**: The core pipeline skills (`prd`, `plan`, `spec`, `exec-spec`, `exec-plan`, `review`, `quick-review`, `remediate-findings`) and the supporting skills they call (`architecture`, `ui-ux-design`, `triage`) accept `--auto` / `--headless`. In automation mode they do not ask follow-up questions or emit arrow-prompts, make conservative assumptions, record assumptions/deferred decisions in artifacts or summaries, propagate `--auto` to nested `andthen:*` skill calls that accept it (`ops` is exempt — it is deterministic), and stop with `BLOCKED:` on contract failures or unsafe actions.

## Skills

Invoke with `/andthen:<skill>` (e.g. `/andthen:triage`, `/andthen:spec`).

> **Not sure where to start?** Run `/andthen:now-what` — it inspects your project state and routes you to the right skill.

### Standalone Skills

Use these individually for everyday development — no setup, no pipeline, no prior artifacts needed.

| Skill | Purpose |
|-------|---------|
| `now-what` | First-stop router — inspects project state and routes to the right skill (use when starting fresh or unsure what to do next) |
| `triage` | Investigate, diagnose, and fix issues (`--plan-only` for investigation only) |
| `quick-implement` | Fast path for small features/fixes (supports `--issue` for GitHub → auto-PR) |
| `quick-review` | Quick in-conversation sanity-check via fresh-context sub-agent |
| `review` | Smart review entrypoint: routes to code, doc, gap, security, mixed, or multi-perspective council review (`--council`) |
| `refactor` | Code improvement and simplification |
| `architecture` | Architecture design, review, decomposition, trade-off analysis, ADRs, fitness functions, strategic design, and event storming (modes: `review`, `decompose`, `advise`, `fitness`, `trade-off`, `strategic-design`, `event-storming`) |
| `ui-ux-design` | UI/UX work — research, design systems, wireframes, and design review (modes: `research`, `design-system`, `wireframes`, `review`) |
| `map-codebase` | Codebase analysis – auto-generates architecture, stack, conventions docs (called by `init` or standalone) |
| `testing` | Test strategy, coverage, authoring, and test-first / red-green-refactor discipline (Prove-It for bugfixes) |
| `ubiquitous-language` | Extract and maintain domain glossary from codebase and docs |
| `excalidraw-diagram` | Generate Excalidraw diagram JSON files that make visual arguments |
| `visual-validation` | Validate UI screenshots and implementations against visual, responsive, and design expectations (`andthen:visual-validation` skill) |
| `visualize` | Render PRD / requirements-clarification / trade-off report as a self-contained HTML view (inline CSS+JS+SVG, dark theme, no external deps); section-anchored notes export via clipboard as a markdown payload that downstream skills (`prd`, `clarify`, `architecture`) consume as conversational input. Open-loop (emits HTML, opens browser, exits). Output: `.agent_temp/visualize/<slug>-<ts>.html`. Diagrams: design-tree (clarification), per-option radar (trade-off), User Flows flowchart + Decisions Log timeline + Dependencies list-graph (PRD). Notes survive refresh via per-tab LocalStorage with restore prompt; `beforeunload` warning on unsaved notes; clipboard-API fallback to selectable textarea |
| `e2e-test` | End-to-end browser testing for web applications |

### Pipeline Skills

These compose into structured workflows — from requirements through implementation to review.

| Skill | Purpose |
|-------|---------|
| `init` | Set up AndThen workflow structure (new projects, partial setups, brownfield) |
| `clarify` | Requirements discovery – from vague idea to structured requirements (supports `--issue` for GitHub input) |
| `prd` | Create a Product Requirements Document from requirements (supports `--issue` for GitHub input, `--to-issue` for publishing) |
| `spec` | Generate Feature Implementation Specification from requirements |
| `exec-spec` | Execute a FIS – direct implementation with validation |
| `plan` | Full plan bundle: story breakdown + FIS for every story + cross-cutting review. Requires `prd.md` input (`--skip-specs` for cheap planning pass) |
| `exec-plan` | Execute a fully-specced plan bundle – exec-spec + quick-review per story, final gap review. Use `--team` for Agent Teams |
| `remediate-findings` | Implement validated review findings with re-validation and status updates |
| `ops` | Deterministic state management, git conventions, and progress tracking |

> Both `exec-plan` and `review --council` auto-detect Agent Teams and use them when available. Use `--team` to force Agent Teams mode.

## Agents

AndThen ships one agent: the `andthen:documentation-lookup` agent for Claude Code plugin-tier installs only. Other install paths use equivalent skill-prompt routing through the project's `## Documentation Lookup Tools` section.

Architecture, UI/UX design, build/test diagnosis, and visual validation are **skills** — use `/andthen:architecture`, `/andthen:ui-ux-design`, `/andthen:triage`, and `/andthen:visual-validation` where relevant. Research is inline sub-agent guidance embedded in the skill prompts that need it (no standalone skill or agent).

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
/andthen:review --mode doc docs/specs/my-feature/plan.md

# Refactor messy code
/andthen:refactor src/utils/

# Trade-off analysis — evaluate architectural options, compare alternatives, write an ADR
/andthen:architecture --mode trade-off "caching strategy for API responses"

# Architecture health check
/andthen:architecture src/

# Multi-perspective review with adversarial debate
/andthen:review --council

# Understand a new codebase
/andthen:map-codebase

# Build a domain glossary
/andthen:ubiquitous-language

# Visualize an architecture or workflow
/andthen:excalidraw-diagram "data pipeline architecture"

# Render a PRD / requirements-clarification / trade-off report as a self-contained HTML view
# with section-anchored notes (notes round-trip to downstream skills via clipboard)
/andthen:visualize docs/specs/auth-feature/prd.md
/andthen:visualize docs/specs/auth-feature/requirements-clarification.md
```

#### Architecture Modes

```bash
# Interactive — presents modes and asks what you want to do
/andthen:architecture

# Full architecture health assessment
/andthen:architecture --mode review src/

# Evaluate a split/merge decision
/andthen:architecture --mode decompose src/core

# Propose fitness functions for architectural governance
/andthen:architecture --mode fitness

# Design/advisory guidance grounded in CUPID, DDD, and architectural frameworks
/andthen:architecture --mode advise "should I use event sourcing for the order domain"

# Trade-off analysis — compare options with weighted criteria, produce an evidence-based recommendation or ADR
/andthen:architecture --mode trade-off "SQL vs document DB for the events store"

# Strategic design — subdomain classification, bounded contexts, context map, UL touchpoints (greenfield + brownfield)
/andthen:architecture --mode strategic-design "order fulfillment domain"

# Event storming — Brandolini-style discovery of pivotal events, hotspots, and subdomain candidates
/andthen:architecture --mode event-storming "loan origination workflow"

# Supports multi-step sessions — after any run, continue with another mode
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

# Reviewers auto-selected based on changes:
# - Product features → Product Manager, Requirements Analyst, etc.
# - Backend APIs → Performance Oracle, API Designer, Backend Specialist, etc.
# - Frontend UI → UX/Accessibility, Frontend Specialist, etc.
# - Security-mode councils → Security Sentinel + 1-3 surface specialists
# - Always includes Devil's Advocate + Synthesis Challenger

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
# Cheap planning pass (plan.md only, skip FIS generation):
/andthen:plan --skip-specs docs/specs/dashboard/

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

**GitHub integration surface** (narrow on purpose): `clarify --issue` and `prd --issue` read an issue body as requirements input; `prd --to-issue` and `triage --to-issue` publish markdown reports for stakeholder visibility; `quick-implement --issue` reads an issue body and opens a PR with `Closes #N`; `review --to-pr` and `architecture --to-pr` post reports as PR comments. Everything else is local — use a branch + PR as the transport.

## Release Notes

See [CHANGELOG.md](../CHANGELOG.md) for release notes.

## License

MIT
