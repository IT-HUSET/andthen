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

See [`templates/CLAUDE.template.md`](../templates/CLAUDE.template.md) for a starter template.

### Agent Teams (Optional, Claude Code only)

The `-team` skill variants (`exec-plan-team`, `review-council-team`) use [Agent Teams](https://code.claude.com/docs/en/agent-teams) for enhanced parallel multi-agent coordination with real-time inter-agent communication. The portable versions (`exec-plan`, `review-council`) work across all agents using sub-agents with sequential fallback. To enable Agent Teams:

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

**Session management**: The context-intensive skills — `exec-spec`, `spec-plan`, `exec-plan`/`exec-plan-team`, `review-council`/`review-council-team` — perform best when started in a **clean session**. Pipeline predecessor skills (`clarify`, `plan`, `spec`) will suggest when to start fresh. Standalone skills like `triage`, `quick-review`, and `refactor` are lightweight and run well mid-conversation.

## Skills

Invoke with `/andthen:<skill>` (e.g. `/andthen:triage`, `/andthen:spec`).

### Standalone Skills

Use these individually for everyday development — no setup, no pipeline, no prior artifacts needed.

| Skill | Purpose |
|-------|---------|
| `triage` | Investigate, diagnose, and fix issues (`--plan-only` for investigation only) |
| `quick-implement` | Fast path for small features/fixes (supports `--issue` for GitHub) |
| `quick-review` | Quick in-conversation sanity-check via fresh-context sub-agent |
| `refactor` | Code improvement and simplification |
| `review-code` | Code review with checklists (quality, security, architecture, UI/UX) |
| `review-doc` | Document review for completeness, clarity, and technical accuracy |
| `trade-off` | Architecture decision research with evidence-based recommendations |
| `architecture-review` | Deep quantitative architecture review – metrics, connascence, decomposition, fitness functions |
| `review-council` | Multi-perspective review (5-7 reviewers + adversarial debate) |
| `map-codebase` | Codebase analysis – auto-generates architecture, stack, conventions docs (called by `init` or standalone) |
| `ubiquitous-language` | Extract and maintain domain glossary from codebase and docs |
| `excalidraw-diagram` | Generate Excalidraw diagram JSON files that make visual arguments |
| `e2e-test` | End-to-end browser testing for web applications |

### Pipeline Skills

These compose into structured workflows — from requirements through implementation to review.

| Skill | Purpose |
|-------|---------|
| `init` | Set up AndThen workflow structure (new projects, partial setups, brownfield) |
| `clarify` | Requirements discovery – from vague idea to structured requirements (supports `--issue`) |
| `spec` | Generate Feature Implementation Specification from requirements (supports `--issue`) |
| `exec-spec` | Execute a FIS – orchestrated implementation with validation |
| `plan` | Requirements discovery + PRD creation (if needed) + story breakdown (supports `--issue`) |
| `spec-plan` | Batch-create all FIS specs for a plan (parallel + cross-cutting review) |
| `exec-plan` | Execute plan – spec-plan per phase, then sub-agent pipeline with `--review-mode per-story|none|full-plan` |
| `review-gap` | Gap analysis + code review against requirements |
| `remediate-findings` | Implement validated review findings with re-validation and status updates |
| `ops` | Deterministic state management, git conventions, and progress tracking |
| `wireframes` | Generate HTML wireframes for UI planning |
| `design-system` | Create design tokens and component styles |

### Agent Teams Variants (Claude Code only)

| Skill | Purpose |
|-------|---------|
| `exec-plan-team` | Execute plan via Agent Team pipeline with inter-agent coordination and configurable review mode |
| `review-council-team` | Multi-perspective review with real-time Agent Teams debate |

## Agents

| Agent | Purpose |
|-------|---------|
| `research-specialist` | Web research and synthesis |
| `solution-architect` | Architecture design and technical decisions |
| `qa-test-engineer` | Test coverage and validation |
| `documentation-lookup` | External documentation retrieval |
| `build-troubleshooter` | Build/test failure diagnosis |
| `ui-ux-designer` | UI/UX design and prototyping |
| `visual-validation-specialist` | Visual validation workflow |

## Usage Examples

### Standalone

```bash
# Debug and fix a broken build
/andthen:triage

# Quick feature or bug fix from a GitHub issue
/andthen:quick-implement --issue 123

# Sanity-check what you just built (mid-conversation)
/andthen:quick-review

# Review code changes or a PR
/andthen:review-code
/andthen:review-code --pr 42

# Refactor messy code
/andthen:refactor src/utils/

# Evaluate architectural options
/andthen:trade-off "caching strategy for API responses"

# Architecture health check
/andthen:architecture-review src/

# Multi-perspective review with adversarial debate
/andthen:review-council

# Understand a new codebase
/andthen:map-codebase

# Build a domain glossary
/andthen:ubiquitous-language

# Visualize an architecture or workflow
/andthen:excalidraw-diagram "data pipeline architecture"
```

#### Architecture Review Modes

```bash
# Interactive — presents modes and asks what you want to analyze
/andthen:architecture-review

# Full architecture health assessment
/andthen:architecture-review src/

# Evaluate a split/merge decision
/andthen:architecture-review src/core --mode decompose

# Propose fitness functions for architectural governance
/andthen:architecture-review --mode fitness

# Get framework-grounded guidance on an architecture question
/andthen:architecture-review "should I use event sourcing for the order domain" --mode advise

# Supports multi-step sessions — after any analysis, continue with
# another mode (e.g. review → decompose a finding → propose fitness functions)
```

#### Multi-Perspective Review

```bash
# Adaptive review - analyzes scope and selects 5-7 relevant reviewers
/andthen:review-council

# Review specific PR with council
/andthen:review-council --pr 123

# Focus on specific aspect
/andthen:review-council "security"

# Reviewers auto-selected based on changes:
# - Product features → Product Manager, Requirements Analyst, etc.
# - Backend APIs → Security, Performance, API Designer, etc.
# - Frontend UI → UX/Accessibility, Frontend Specialist, etc.
# - Always includes Devil's Advocate + Synthesis Challenger

# OR use Agent Teams variant for real-time debate (Claude Code only)
/andthen:review-council-team
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
/andthen:review-gap <path-to-fis>

# 5. If the review reports actionable findings:
/andthen:remediate-findings <path-to-gap-review-report>
```

### Plan Workflow (MVP / multi-feature)

```bash
# 1. Clarify requirements (optional)
/andthen:clarify "dashboard for analytics"

# 2. Optional: create design assets
/andthen:wireframes
/andthen:design-system

# 3. Generate plan (includes PRD creation if needed + story breakdown)
/andthen:plan docs/specs/dashboard/
/andthen:plan --issue 42   # or directly from a GitHub issue

# 4a. Execute all stories via pipeline (default per-story review)
/andthen:exec-plan docs/specs/dashboard/

# 4a-alt. Single full-plan review after all stories
/andthen:exec-plan docs/specs/dashboard/ --review-mode full-plan

# 4a-alt. Skip automated review; review manually after execution
/andthen:exec-plan docs/specs/dashboard/ --review-mode none

# 4b. OR use Agent Teams variant for enhanced parallelism (Claude Code only)
/andthen:exec-plan-team docs/specs/dashboard/
# Same review modes also work here:
# /andthen:exec-plan-team docs/specs/dashboard/ --review-mode full-plan
# /andthen:exec-plan-team docs/specs/dashboard/ --review-mode none

# 4c. OR manually: batch-create all specs, then execute per story
/andthen:spec-plan docs/specs/dashboard/
/andthen:exec-spec docs/specs/dashboard/s01-project-setup.md
/andthen:review-gap docs/specs/dashboard/s01-project-setup.md
/andthen:remediate-findings <path-to-gap-review-report>   # when review-gap fails
# ... repeat exec-spec + review-gap (+ remediation when needed) for each story in per-story mode

# 5. Final review (single-feature workflow, or manual review after `--review-mode none`)
/andthen:review-gap
```

## License

MIT
