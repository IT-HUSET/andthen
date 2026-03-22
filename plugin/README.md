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

- **Project Document Index** — tells skills where to write output (specs, plans, etc.)
- **Workflow Rules, Guardrails and Guidelines** — behavioral rules and development standards

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
│  clarify ──────────────→   spec   ────→ review-doc          │
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
│       clarify ──────→  plan  ──────→  review-doc            │
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
- **Quick path** (`quick-implement`): Bug fix, small feature, GitHub issue — you know what to do and it's under ~3 files
- **Feature workflow** (`clarify` → `spec` → `exec-spec` → `review-gap`): Single feature with real complexity — multiple files, non-obvious requirements, needs a blueprint
- **Plan workflow** (`clarify` → `plan` → `exec-plan` → `review-gap`): Multiple features, MVP, or a new project — needs story breakdown and phased execution

Not sure? Start with `quick-implement`. If it feels too complex, switch to the feature workflow. See the [full documentation](../README.md#getting-started) for a complete walkthrough.

**Pre-activities** (feed into spec or plan):
- `clarify` — When requirements are vague (can't list 3 acceptance criteria? run `clarify`)
- `wireframes` / `design-system` — When UI design is needed
- `trade-off` — When architectural decisions are needed

## Skills

Invoke with `/andthen:<skill>` (e.g. `/andthen:spec`, `/andthen:plan`).

### Core Skills

| Skill | Purpose |
|-------|---------|
| `init` | Set up AndThen workflow structure (new projects, partial setups, brownfield) |
| `clarify` | Requirements discovery — from vague idea to structured requirements |
| `spec` | Generate Feature Implementation Specification from requirements |
| `exec-spec` | Execute a FIS — orchestrated implementation with validation |
| `review-gap` | Gap analysis + code review against requirements |
| `plan` | Requirements discovery + PRD creation (if needed) + story breakdown |
| `trade-off` | Architecture decision research with evidence-based recommendations |
| `review-code` | Code review with checklists (quality, security, architecture, UI/UX) |
| `review-doc` | Document review for completeness, clarity, and technical accuracy |

### Extras

| Skill | Purpose |
|-------|---------|
| `exec-plan` | Execute plan — sub-agent pipeline (spec → exec-spec → review-gap per story) |
| `quick-implement` | Fast path for small features/fixes (supports `--issue` for GitHub) |
| `e2e-test` | End-to-end browser testing for web applications |
| `ops` | Deterministic state management, git conventions, and progress tracking |
| `design-system` | Create design tokens and component styles |
| `wireframes` | Generate HTML wireframes for UI planning |
| `refactor` | Code improvement and simplification |
| `review-council` | Multi-perspective review (5-7 reviewers + adversarial debate) |
| `triage` | Investigate, diagnose, and fix issues (`--plan-only` for investigation only) |
| `ubiquitous-language` | Extract and maintain domain glossary from codebase and docs |
| `map-codebase` | Brownfield codebase analysis + reverse requirements discovery |
| `excalidraw-diagram` | Generate Excalidraw diagram JSON files that make visual arguments |

### Agent Teams Variants (Claude Code only)

| Skill | Purpose |
|-------|---------|
| `exec-plan-team` | Execute plan via Agent Team pipeline with inter-agent coordination |
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

- **Gap Analysis** (`review-gap`): Does implementation match requirements? Includes code review + remediation plan
- **Code Review** (`review-code`): Reusable code review with checklists — used by `review-gap` and other skills
- **Doc Review** (`review-doc`): Review specs, PRDs, and documentation for completeness and clarity

## External Dependencies (Optional)

| Plugin | Used by | Purpose |
|--------|---------|---------|
| `code-simplifier` | `refactor`, `exec-spec`, `quick-implement` | Code cleanup and simplification |
| `frontend-design` | `wireframes` (via `ui-ux-designer` agent) | Design implementation |

Skills work without these plugins but skip the corresponding steps.

## License

MIT
