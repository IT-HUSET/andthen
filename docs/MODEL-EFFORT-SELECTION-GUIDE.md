# Model & Effort Selection Guide for AI Coding Agents

Practical guidance for selecting models and thinking/effort levels across Claude Code and Codex CLI, mapped to specific tasks and workflow commands.

**Last Updated**: 2026-03-17

---

## Quick Reference

### Claude Code

```bash
# Set model via CLI flag, effort via env var (no --effort flag exists)
CLAUDE_CODE_EFFORT_LEVEL=high claude --model opus

# Or set effort persistently in settings JSON: "effortLevel": "medium"
# Or change mid-session via /model slider (left/right arrow keys)
```

| Alias | Resolves To | Notes |
|-------|-------------|-------|
| `opus` | Opus 4.6 | Strongest reasoning |
| `sonnet` | Sonnet 4.6 | Best cost/quality ratio |
| `haiku` | Haiku 4.5 | Fastest, cheapest (no effort param support) |
| `opusplan` | Opus 4.6 (plan) → Sonnet 4.6 (execute) | Automatic hybrid switching |

### Codex CLI

```bash
# Set model via --model, effort via -c override (no --reasoning-effort flag exists)
codex -m gpt-5.4 -c model_reasoning_effort='"high"' "prompt"

# Or use named profiles in ~/.codex/config.toml:
# [profiles.deep-review]
# model = "gpt-5.3-codex"
# model_reasoning_effort = "high"
#
# codex --profile deep-review "prompt"
```

---

## Model Overview

### Anthropic (Claude Code)

| Model | SWE-bench Verified | Pricing (in/out MTok) | Effort Levels | Context | Max Output |
|-------|-------------------|----------------------|---------------|---------|------------|
| Opus 4.6 | 80.8% | $5 / $25 | low, medium, high, **max** | 200K (1M beta) | 128K |
| Sonnet 4.6 | 79.6% | $3 / $15 | low, medium, high | 200K (1M beta) | 64K |
| Haiku 4.5 | 73.3% | $1 / $5 | _(not supported)_ | 200K | 64K |

- **Adaptive thinking** (GA on 4.6 models): Claude dynamically decides how much to think per turn. Enables interleaved thinking between tool calls - critical for agentic workflows.
- **`max` effort is Opus 4.6 exclusive** - returns error on other models.
- **`budget_tokens` is deprecated** on 4.6 models; use effort parameter instead.
- Per-turn escalation: type "ultrathink" (or "think harder", "megathink") to bump a single turn to high effort.

### OpenAI (Codex CLI)

| Model | SWE-Bench Pro | Pricing (in/out MTok) | Effort Levels | Context | Max Output |
|-------|--------------|----------------------|---------------|---------|------------|
| GPT-5.4 | 57.7% | $2.50 / $15 | low–xhigh | 1M* | 128K |
| GPT-5.3-Codex | 56.8% | $3 / $12 | low–xhigh | 1M* | 128K |
| GPT-5.2-Codex | 56.4% | TBD | low–xhigh | 400K | 128K |

\* Extended context (>272K input tokens) requires the experimental `model_context_window` parameter and is billed at **2x input / 1.5x output** for the full session.

- **GPT-5.4 is the recommended default** — unified frontier model that absorbed GPT-5.3-Codex coding capabilities. Marginally better on SWE-Bench Pro, same context window, cheaper.
- **GPT-5.3-Codex** retains a small edge on Terminal-Bench 2.0 (77.3% vs 75.1%) — relevant for terminal-heavy/CLI-scripting workflows. For most tasks, GPT-5.4 is preferred.
- **Retired models** (Feb 2026): o4-mini, GPT-4o, GPT-4.1, GPT-4.1 mini. Do not use for new development.
- `plan_mode_reasoning_effort` is a separate config key (defaults to `medium`).

> **Note**: SWE-Bench Verified and SWE-Bench Pro are different benchmarks with different scales. Scores across them are not comparable.

---

## Effort Levels Explained

Effort is a **behavioral signal, not a hard token cap**. Even at `low`, the model will still think on genuinely hard problems — just less.

| Level | Behavior | When to Use |
|-------|----------|------------|
| **low** | Minimal thinking, max speed. May skip thinking on simple problems. | Subagents, simple edits, high-volume parallel tasks |
| **medium** | Balanced. Thinks when useful, skips when not. | Most daily coding work — the recommended default |
| **high** | Almost always thinks deeply. | Complex reasoning, architecture, debugging subtle bugs |
| **max** / **xhigh** | No constraints on thinking. Maximum depth. | Critical one-off decisions, security audits, hardest problems |

---

## Task-to-Configuration Matrix

### General Tasks

| Task | Claude Code | Codex CLI |
|------|-------------|-----------|
| Simple edits, typos, formatting | `haiku` or `sonnet` @ `low` | `gpt-5.4` @ `low` |
| Boilerplate, CRUD, scaffolding | `sonnet` @ `low`–`medium` | `gpt-5.4` @ `medium` |
| Unit/integration test generation | `sonnet` @ `medium` | `gpt-5.4` @ `medium` |
| Frontend components (React/Vue/CSS) | `sonnet` @ `medium` | `gpt-5.4` @ `medium` |
| Debugging (clear errors, stack traces) | `sonnet` @ `medium` | `gpt-5.4` @ `medium` |
| Debugging (subtle, race conditions) | `opus` @ `high` (or `sonnet` + "ultrathink") | `gpt-5.4` @ `high` |
| Single-file refactoring | `sonnet` @ `medium` | `gpt-5.4` @ `medium` |
| Cross-file / large-scale refactoring | `opus` @ `high` | `gpt-5.4` @ `high` |
| Architecture / system design | `opus` @ `high`–`max` | `gpt-5.4` @ `high`–`xhigh` |
| Security review / vulnerability audit | `opus` @ `high`–`max` | `gpt-5.4` @ `high`–`xhigh` |
| ADR / trade-off analysis | `opus` @ `high`–`max` | `gpt-5.4` @ `high`–`xhigh` |
| Documentation writing | `sonnet` @ `low`–`medium` | `gpt-5.4` @ `low`–`medium` |
| Subagents / parallel delegated work | `haiku` or `sonnet` @ `low` | `gpt-5.4` @ `low` |

---

## Workflow Command Recommendations

### AndThen Plugin (Claude Code)

Commands are grouped by workflow phase. Recommendations assume Claude Code with adaptive thinking enabled (default on 4.6 models).

#### Requirements & Planning Phase

| Command | Description | Model | Effort | Rationale |
|---------|-------------|-------|--------|-----------|
| `/clarify` | Requirements discovery — structured requirements from vague idea | `sonnet` | `medium` | Analytical but not deeply reasoning-heavy |
| `/plan` | Full-journey planning: requirements discovery through story breakdown | `opus` or `opusplan` | `high` | Architectural thinking, phasing decisions, cross-cutting reasoning |

#### Design & Architecture Phase

| Command | Description | Model | Effort | Rationale |
|---------|-------------|-------|--------|-----------|
| `/design-system` | Design system tokens + style guide | `sonnet` | `medium` | Pattern-following with design knowledge |
| `/wireframes` | HTML wireframes for screens | `sonnet` | `medium` | Visual/structural, not deep reasoning |
| `/trade-off` | Systematic trade-off analysis | `opus` | `high`–`max` | Core reasoning task, decision quality critical |

#### Implementation & Execution Phase

| Command | Description | Model | Effort | Rationale |
|---------|-------------|-------|--------|-----------|
| `/spec` | Clarify requirements + create Feature Implementation Spec (FIS) | `opus` | `high` | Reasoning-heavy: edge cases, constraints, cross-cutting concerns |
| `/exec-spec` | Execute a FIS — orchestrated implementation with validation | `opusplan` | `medium`–`high` | Opus plans subtasks, Sonnet executes code. Medium for straightforward specs, high for complex ones |
| `/exec-plan` | Execute full plan via Agent Teams | `opusplan` | `medium` | Orchestrator delegates to subagents; medium keeps costs reasonable at scale |
| `/quick-implement` | Quick path for small features/fixes | `sonnet` | `medium` | Small scope, speed matters |
| `/refactor` | Code improvement and simplification | `sonnet` | `medium`–`high` | Medium for localized, high for cross-file |
| `/triage` | Investigate, diagnose, and fix issues | `sonnet` | `medium`–`high` | Medium for clear issues, high for subtle root cause analysis |

#### Review & Validation Phase

| Command | Description | Model | Effort | Rationale |
|---------|-------------|-------|--------|-----------|
| `/review-gap` | Gap analysis + code review (default), doc review (`--doc`), PR review (`--pr`) | `sonnet` | `medium`–`high` | Medium for routine, high for security-critical or complex gap analysis |
| `review-code` (skill) | Thorough code review (quality, security, architecture) | `sonnet` | `medium`–`high` | Medium for routine review, high for security-critical |
| `review-doc` (skill) | Review specs/PRDs/documentation | `sonnet` | `medium` | Comprehension and completeness checking |
| `/review-council` | Multi-perspective adversarial review | `sonnet` | `high` | Multiple subagent perspectives need depth to be meaningful |
| `/ubiquitous-language` | Extract and maintain domain glossary | `sonnet` | `medium` | Analytical extraction and resolution, not deep reasoning |

#### Other Agents (invoked by commands or directly)

| Agent | Description | Model | Effort | Rationale |
|-------|-------------|-------|--------|-----------|
| `visual-validation-specialist` | Screenshot capture, comparison, design compliance | `sonnet` | `medium` | Primarily perceptual (multimodal), not reasoning-heavy |
| `solution-architect` | Architecture design, ADR creation | `opus` | `high` | Core reasoning task |
| `build-troubleshooter` | Systematic debugging, root cause analysis | `sonnet` | `medium`–`high` | Medium for clear errors, high for subtle issues |
| `qa-test-engineer` | Test strategy, coverage, implementation | `sonnet` | `medium` | Formulaic with domain knowledge |
| `documentation-lookup` | Fetch up-to-date library/API docs | `haiku` | `low` | Retrieval task, no reasoning needed |
| `research-specialist` | Deep web research, multi-source synthesis | `sonnet` | `medium` | Broad search + synthesis, not deep per-query reasoning |
| `ui-ux-designer` | UI/UX design and quality validation | `sonnet` | `medium` | Design knowledge + perception |
| Subagents (general parallel work) | Delegated subtasks | `haiku` or `sonnet` | `low` | Cost multiplies with parallelism |

### Commands via Other Agents (Codex CLI, etc.)

Skills are agent-agnostic — the same files work across all agents. Recommendations for Codex CLI assume you ran `./scripts/install-skills.sh`, which exports skills as `andthen.*/`:

| Skill | Description | Model | Effort | Rationale |
|-------|-------------|-------|--------|-----------|
| `andthen.clarify` | Requirements discovery from vague ideas | `gpt-5.4` | `medium` | Analytical, not deeply complex |
| `andthen.spec` | Clarify requirements + create FIS | `gpt-5.4` | `high` | Reasoning-heavy, completeness critical |
| `andthen.exec-spec` | Execute a FIS | `gpt-5.4` | `medium`–`high` | Medium for straightforward, high for complex specs |
| `andthen.review-gap` | Gap analysis + code review | `gpt-5.4` | `medium`–`high` | Medium routine, high for security-critical |
| `andthen.design-system` | Design system tokens + style guide | `gpt-5.4` | `medium` | Pattern-following |
| `andthen.wireframes` | HTML wireframes for screens | `gpt-5.4` | `medium` | Structural generation |
| `andthen.trade-off` | Trade-off analysis | `gpt-5.4` | `high` | Decision quality matters |
| `andthen.refactor` | Code simplification and cleanup | `gpt-5.4` | `medium`–`high` | Medium for localized, high for cross-file |
| `andthen.quick-implement` | Fast path for small features/fixes | `gpt-5.4` | `medium` | Bounded scope, standard implementation |
| `andthen.e2e-test` | End-to-end browser testing | `gpt-5.4` | `medium` | Sequential test execution |
| `andthen.triage` | Systematic debugging | `gpt-5.4` | `medium`–`high` | Medium for clear issues, high for complex |

---

## Cost Optimization Strategies

1. **Default to medium effort** — captures ~95% of high-effort quality at significantly lower cost and latency. Both Anthropic and OpenAI recommend this as the daily driver.

2. **Use `opusplan` for plan-then-execute workflows** — gets Opus-quality planning with Sonnet-cost execution automatically. Ideal for `/exec-spec` and `/exec-plan`.

3. **Use `haiku` or `low` effort for subagents** — when an orchestrator spawns parallel subagents, cost compounds. Haiku at $1/$5 MTok delivers ~73% SWE-bench at 1/5th the cost of Opus.

4. **Escalate per-turn, not globally** — use "ultrathink" (Claude Code) or profile switching (Codex CLI) for specific hard turns rather than raising session-level defaults.

5. **Use Codex CLI profiles for task presets** — define `[profiles.security-review]` with `model_reasoning_effort = "high"` to switch cleanly without remembering flags.

6. **Set `max_tokens` >= 32K for agentic sessions** — thinking and response text share the output budget. At high/max effort, the model can exhaust the budget mid-response.

---

## Key Behavioral Notes

- **Effort is behavioral, not a hard cap**: even at `low`, models will still think on genuinely hard problems. `low` is safe for subagents — they won't produce garbage on unexpectedly complex subtasks.
- **Adaptive thinking > static budgets**: for agentic coding, interleaved thinking (between tool calls) matters more than a large upfront thinking budget. This is why adaptive mode on 4.6 models outperforms manual extended thinking.
- **Diminishing returns on pure thinking**: research shows that for tool-heavy agentic tasks, raw thinking token increases have diminishing returns. The number of tool calls and their quality matters as much as thinking depth.
- **Sonnet 4.6 is surprisingly close to Opus 4.6 on coding**: 79.6% vs 80.8% SWE-bench at 60% of the price. Reserve Opus for reasoning-heavy tasks (planning, specs, ADRs, trade-off analysis), not routine coding.
