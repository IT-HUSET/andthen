<p align="center">
  <img src="assets/logo.png" alt="AndThen" width="500">
</p>

<p align="center">
  Structured workflows for agentic development — from requirements to shipped code.
</p>

> "I have a feature idea" → *and then?* → clarify → *and then?* → spec → *and then?* → plan → *and then?* → execute → *and then?* → review → **ship it.**

AndThen is an opinionated workflow system for AI coding agents. It provides structured commands that guide development through a disciplined pipeline, producing a **Feature Implementation Specification (FIS)** as the core artifact — a comprehensive blueprint that enables reliable, autonomous implementation.

Works as a **Claude Code plugin** with full sub-agent orchestration, and commands are designed to be **agent-agnostic** — falling back to direct execution when sub-agents aren't available.


## Installation

### Claude Code Plugin (recommended)

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

**Local install** (if you have the repo cloned):
```bash
claude plugin install ./plugin
```

### Other AI Coding Agents (Codex CLI, Aider, Cursor, etc.)

Commands use capability detection and work without the plugin infrastructure. Copy or reference command files directly:

```bash
# Codex CLI — copy as prompts
cp plugin/commands/*.md ~/.codex/prompts/

# Or reference individual commands in any agent
```


## Setup

Commands reference your project's `CLAUDE.md` for context. Add these sections:

**1. Project Document Index** — tells commands where to write output (specs, plans, etc.)
**2. Workflow Rules, Guardrails and Guidelines** — behavioral rules and development standards

See [`templates/CLAUDE.template.md`](templates/CLAUDE.template.md) for a starter template.

### Agent Teams (Optional)

Commands like `review-council` and `exec-plan` use [Agent Teams](https://code.claude.com/docs/en/agent-teams) for parallel multi-agent coordination. To enable:

```json
// ~/.claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Commands automatically fall back to single-agent mode when Agent Teams are unavailable.


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
│  clarify ──────────────→   spec   ────→ review --doc        │
│                              │                              │
│                              ▼                              │
│                          exec-spec                          │
│                              │                              │
│                              ▼                              │
│                           review                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  PLAN WORKFLOW (MVP / multi-feature)                        │
│                                                             │
│  ┌──────────────── OPTIONAL PRE-WORK: ─────────────────┐   │
│  │ wireframes, design-system, trade-off                 │   │
│  └───────────────────────┬─────────────────────────────┘   │
│                          │                                  │
│  (optional)              ▼            (optional)            │
│  clarify ──────→  plan  ──────→  review --doc               │
│             (PRD + story breakdown)                         │
│                          │                                  │
│              ┌───────────┴───────────┐                      │
│              ▼                       ▼                      │
│         exec-plan              Per story:                   │
│       (Agent Team              spec → exec-spec → review    │
│        pipeline)               (repeat for each story)      │
│              └───────────┬───────────┘                      │
│                          ▼                                  │
│                       review                                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  QUICK PATH (small features/fixes)                          │
│                                                             │
│  quick-implement ──→ review (optional) ──→ done (or PR)     │
└─────────────────────────────────────────────────────────────┘
```

**When to use which:**
- **Feature workflow**: Single feature, complex changes, multi-file modifications
- **Plan workflow**: MVP, new project, multi-feature work
- **Quick path**: Bug fixes, small features, GitHub issues


## Commands

Invoke with `/andthen:<command>` or just `/<command>` if unambiguous.

### Core Commands

| Command | Purpose |
|---------|---------|
| `clarify` | Requirements discovery — from vague idea to structured requirements |
| `spec` | Generate Feature Implementation Specification from requirements |
| `exec-spec` | Execute a FIS — orchestrated implementation with validation |
| `review` | Gap analysis + code review (default), doc review (`--doc`), PR review (`--pr`) |
| `plan` | Requirements discovery + PRD creation (if needed) + story breakdown |
| `exec-plan` | Execute plan via Agent Team pipeline (spec → exec-spec → review per story) |
| `trade-off` | Architecture decision research with evidence-based recommendations |

### Extras

| Command | Purpose |
|---------|---------|
| `quick-implement` | Fast path for small features/fixes (supports `--issue` for GitHub) |
| `design-system` | Create design tokens and component styles |
| `wireframes` | Generate HTML wireframes for UI planning |
| `refactor` | Code improvement and simplification |
| `review-council` | Multi-perspective review with Agent Teams (5-7 reviewers + debate) |
| `troubleshoot` | Diagnose and fix implementation issues systematically |

### Skills

| Skill | Purpose |
|-------|---------|
| `review-code` | Reusable code review with checklists (quality, security, architecture, UI/UX) |
| `review-doc` | Reusable document review for completeness, clarity, and technical accuracy |
| `e2e-test` | End-to-end browser testing for web applications |


## Key Concepts

### Feature Implementation Specification (FIS)

The core artifact. A structured document generated by `spec` containing everything needed for autonomous implementation:
- Requirements and acceptance criteria
- Technical approach and architecture
- File changes and dependencies
- Validation checklist

### The AndThen Pipeline

The philosophy: every step naturally leads to the next. *"And then?"* forces structured progression rather than ad-hoc development.

```
clarify → spec → plan → execute → review
   ↑                                  │
   └──────── feedback loop ───────────┘
```

### Implementation Loop

Both `exec-spec` and `quick-implement` use an iterative cycle:
```
Implement → Verify → Evaluate → (repeat if needed)
```

Verification includes code review, testing, and visual validation (when applicable).


## Agents

Specialized sub-agents used internally by commands:

| Agent | Purpose |
|-------|---------|
| `research-specialist` | Web research and synthesis |
| `solution-architect` | Architecture design and technical decisions |
| `qa-test-engineer` | Test coverage and validation |
| `documentation-lookup` | External documentation retrieval |
| `build-troubleshooter` | Build/test failure diagnosis |
| `ui-ux-designer` | UI/UX design and prototyping |
| `visual-validation-specialist` | Visual validation workflow |


## Docs

### Guidelines (`docs/guidelines/`)

Simplified starting points — copy into your project and adapt to your needs. Workflow commands reference these via your project's `CLAUDE.md`, so you can replace them entirely with your own.

| Guide | Purpose |
|-------|---------|
| `DEVELOPMENT-ARCHITECTURE-GUIDELINES.md` | Development standards and architecture patterns |
| `UX-UI-GUIDELINES.md` | UX/UI design guidelines |
| `WEB-DEV-GUIDELINES.md` | Web development best practices |
| `CRITICAL-RULES-AND-GUARDRAILS.md` | Safety rules and behavioral guardrails for AI agents |

### Reference (`docs/`)

| Document | Purpose |
|----------|---------|
| `MODEL-EFFORT-SELECTION-GUIDE.md` | Model and thinking effort selection guide |


## External Dependencies (Optional)

Some commands optionally use skills from other plugins when available:

| Plugin | Used by | Purpose |
|--------|---------|---------|
| `code-simplifier` | `refactor`, `exec-spec`, `quick-implement` | Code cleanup and simplification |
| `frontend-design` | `wireframes` (via `ui-ux-designer` agent) | Design implementation |

Commands work without these plugins but skip the corresponding steps.


## Evolved From

AndThen evolved from [cc-workflows](https://github.com/tolo/claude_code_common) — a general-purpose AI coding agent toolkit.


## License

MIT
