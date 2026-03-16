# AndThen Plugin

Structured workflows for agentic development — from requirements to shipped code.

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

Commands reference your project's `CLAUDE.md` for two things:

- **Project Document Index** — tells commands where to write output (specs, plans, etc.)
- **Workflow Rules, Guardrails and Guidelines** — behavioral rules and development standards

See [`templates/CLAUDE.template.md`](../templates/CLAUDE.template.md) for a starter template.

### Agent Teams (Optional, Claude Code only)

The `-team` command variants (`exec-plan-team`, `review-council-team`) use [Agent Teams](https://code.claude.com/docs/en/agent-teams) for enhanced parallel multi-agent coordination with real-time inter-agent communication. The portable versions (`exec-plan`, `review-council`) work across all agents using sub-agents with sequential fallback. To enable Agent Teams:

```json
// ~/.claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────┐
│  FEATURE WORKFLOW (single feature)                          │
│                                                             │
│  ┌─────────────────────── OPTIONAL: ─────────────────────┐  │
│  │ wireframes, design-system, trade-off                  │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │                              │
│  (optional)                  ▼          (optional)          │
│  clarify ──────────────→   spec   ────→ review-gap --doc    │
│                              │                              │
│                              ▼                              │
│                          exec-spec                          │
│                              │                              │
│                              ▼                              │
│                        review-gap                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  PLAN WORKFLOW (MVP / multi-feature)                        │
│                                                             │
│  ┌──────────────── OPTIONAL PRE-WORK: ─────────────────┐    │
│  │ wireframes, design-system, trade-off                │    │
│  └───────────────────────┬─────────────────────────────┘    │
│                          │                                  │
│      (optional)          ▼            (optional)            │
│       clarify ──────→  plan  ──────→  review-gap --doc      │
│             (PRD + story breakdown)                         │
│                          │                                  │
│              ┌───────────┴───────────┐                      │
│              ▼                       ▼                      │
│         exec-plan              Per story:                   │
│       (sub-agent              spec → exec-spec → review-gap │
│        pipeline)              (repeat for each story)       │
│              └───────────┬───────────┘                      │
│                          ▼                                  │
│                      review-gap                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  QUICK PATH (small features/fixes)                          │
│                                                             │
│  quick-implement ──→ review-gap (optional) ──→ done (or PR) │
└─────────────────────────────────────────────────────────────┘
```

**When to use which:**
- **Feature workflow**: Single feature, complex changes, multi-file modifications
- **Plan workflow**: MVP, new project, multi-feature work
- **Quick path**: Bug fixes, small features, GitHub issues

**Pre-activities** (feed into spec or plan):
- `clarify` — When requirements are vague
- `wireframes` / `design-system` (extras) — When UI design is needed
- `trade-off` — When architectural decisions are needed

## Commands

Invoke with `/andthen:<command>` or just `/<command>` if unambiguous.

### Core

| Command | Purpose |
|---------|---------|
| `init` | Set up AndThen workflow structure (new projects, partial setups, brownfield) |
| `clarify` | Requirements discovery — from vague idea to structured requirements |
| `spec` | Generate Feature Implementation Specification from requirements |
| `exec-spec` | Execute a FIS — orchestrated implementation with validation |
| `review-gap` | Gap analysis + code review (default), doc review (`--doc`), PR review (`--pr`) |
| `plan` | Requirements discovery + PRD creation (if needed) + story breakdown |
| `exec-plan` | Execute plan — sub-agent pipeline (spec → exec-spec → review-gap per story) |
| `trade-off` | Architecture decision research with evidence-based recommendations |

### Extras (`commands/extras/`)

| Command | Purpose |
|---------|---------|
| `quick-implement` | Fast path for small features/fixes (supports `--issue` for GitHub) |
| `design-system` | Create design tokens and component styles |
| `wireframes` | Generate HTML wireframes for UI planning |
| `refactor` | Code improvement and simplification |
| `review-council` | Multi-perspective review (5-7 reviewers + adversarial debate) |
| `troubleshoot` | Diagnose and fix implementation issues systematically |
| `map-codebase` | Brownfield codebase analysis + reverse requirements discovery |

### Agent Teams Variants (Claude Code only)

| Command | Purpose |
|---------|---------|
| `exec-plan-team` | Execute plan via Agent Team pipeline with inter-agent coordination |
| `review-council-team` | Multi-perspective review with real-time Agent Teams debate |

### Skills (`skills/`)

| Skill | Purpose |
|-------|---------|
| `andthen-review-code` | Code review with checklists (quality, security, architecture, UI/UX) |
| `andthen-review-doc` | Document review for completeness, clarity, and technical accuracy |
| `andthen-e2e-test` | End-to-end browser testing for web applications |
| `andthen-ops` | Deterministic state management, git conventions, and progress tracking |

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

### Feature Workflow (single feature)

```bash
# 1. Clarify vague requirements
/andthen:clarify "users should be able to export their data"

# 2. Generate implementation spec (includes research)
/andthen:spec <requirements from step 1>

# 3. Execute the spec
/andthen:exec-spec

# 4. Final review (against requirements)
/andthen:review-gap
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

# 4a. Execute all stories via pipeline (recommended)
/andthen:exec-plan docs/specs/dashboard/

# 4b. OR use Agent Teams variant for enhanced parallelism (Claude Code only)
/andthen:exec-plan-team docs/specs/dashboard/

# 4c. OR manually per story: create spec JIT, then execute
/andthen:spec "S01: Project Setup" # from plan
/andthen:exec-spec
/andthen:review-gap
# ... repeat for each story

# 5. Final review (against PRD requirements)
/andthen:review-gap
```

### Quick Fix from GitHub Issue

```bash
# Fetches issue, implements, creates PR
/andthen:quick-implement --issue 123
```

### Technical Decision Making

```bash
# When facing architectural choices
/andthen:trade-off "caching strategy for API responses"
```

### Plan Execution

```bash
# Execute entire plan through pipeline (uses sub-agents if available)
/andthen:exec-plan docs/specs/dashboard/

# OR use Agent Teams variant for enhanced parallelism (Claude Code only)
/andthen:exec-plan-team docs/specs/dashboard/
```

### Multi-Perspective Review

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

## Key Concepts

### Feature Implementation Specification (FIS)

A structured document generated by `spec` containing everything needed for autonomous implementation:
- Requirements and acceptance criteria
- Technical approach and architecture
- File changes and dependencies
- Validation checklist

### Implementation Plan

A lightweight planning document generated by `plan` that breaks down PRD into stories:
- Story scope and acceptance criteria (high-level)
- Dependencies and execution sequence
- Phase organization (Foundation → Features → Integration → Polish)

Detailed FIS specs are created just-in-time via `spec` when each story is ready for implementation.

### Implementation Loop

Both `exec-spec` and `quick-implement` use an iterative cycle:
```
Implement → Verify → Evaluate → (repeat if needed)
```

Verification includes code review, testing, and visual validation (when applicable).

### Review Types

- **Gap Analysis** (`review-gap`): Does implementation match requirements? Includes code review + remediation plan (after execution)
- **Document Review** (`review-gap --doc`): Is the spec/PRD complete and clear? (before execution)
- **PR Review** (`review-gap --pr`): Scoped review of a pull request
- **Code Review** (`andthen-review-code` skill): Reusable code review with checklists — used by `review-gap` and other commands
- **Doc Review** (`andthen-review-doc` skill): Reusable document review — used by `review-gap --doc` and other commands

## External Dependencies (Optional)

| Plugin | Used by | Purpose |
|--------|---------|---------|
| `code-simplifier` | `refactor`, `exec-spec`, `quick-implement` | Code cleanup and simplification |
| `frontend-design` | `wireframes` (via `ui-ux-designer` agent) | Design implementation |

Commands work without these plugins but skip the corresponding steps.

## License

MIT
