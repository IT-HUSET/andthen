# Model & Effort Selection Guide

How AndThen steers reasoning depth across Claude Code and Codex CLI. Principles only – no model version numbers, prices, or benchmark tables (those rot; consult the harness/provider docs for current specifics).

---

## Default policy: session · top · cheap

AndThen ships a named, overridable **Sub-Agent Model Policy** (defined in `CRITICAL-RULES-AND-GUARDRAILS.md`). Three tiers: **session** (the root conversation model, and the ceiling – nothing routes above it), **top** (a strong coding model, never above session), **cheap** (a small fast model). Routing is by task, classified on **specification × judgment**: high judgment (orchestration, planning, architecture, design, reviews, security, creative or ambiguous work) → session at `xhigh`; implementation and other medium/larger subtasks → top at `medium`; small, well-specified, verifiable work → cheap at `medium` when simple, otherwise `xhigh`.

Top/cheap examples are used only when exposed by the host and within the session ceiling; otherwise inherit. Concrete examples live in generated guardrails, not executable config.

Downshifting requires an exact scope, output contract, and done-criterion; the generated guardrails own that rule.

Review and research plugin agents inherit the model with fixed effort; documentation lookup retains the cheap-tier alias exception. The policy governs ad-hoc delegated work.

### Overriding the default

Projects or users that want different routing replace the Sub-Agent Model Policy section in their guardrails copy, or define one in project/user instructions – the nearest definition wins. Generic skill callers provide only the **task shape** (retrieval / implementation / cross-cutting judgment); the policy selects model and effort. The never-version-pin invariant governs AndThen's shipped content; a project's own copy is the project's to maintain.

---

## Effort levels

Effort is a **behavioral signal, not a hard token cap** – even at `low`, the model still thinks on genuinely hard problems, just less.

| Level | Behavior | Use for |
|-------|----------|---------|
| **low** | Minimal thinking, max speed. | Retrieval, doc-lookup, scanning, formatting, trivial edits, high-volume parallel leaves |
| **medium** | Balanced – thinks when useful. The default. | Routine coding, tests, docs, execution sub-agents, routine reviews |
| **high** | Almost always thinks deeply. | Subtle debugging, gap review, specs; the shipped review personas |
| **xhigh / max** | No constraints on depth. (`max` is Anthropic-only; Codex tops out at `xhigh`.) | Judgment work: planning, architecture, design, trade-offs/ADRs, security and standalone review, creative or ambiguous work; the hardest one-off decisions |

---

## How to set it

### Claude Code

Plugin agents declare inherited model plus effort in frontmatter:

```yaml
---
name: review-security
model: inherit   # run on the session model; no version string to rot
effort: high     # low | medium | high | xhigh | max – overrides session effort for this unit
---
```

AndThen agent frontmatter (`plugin/agents/*.md`) supports `model:` and `effort:`. Skill frontmatter (`plugin/skills/*/SKILL.md`) does not carry model or effort overrides in the current AndThen contract; orchestrating skills steer ad-hoc sub-agents in prose instead. The session model itself is the user's choice (`/model`, `claude --model`, the alias system including 1M variants) – AndThen does not override it. Session-level effort fallback: `/effort`, `claude --effort`, `CLAUDE_CODE_EFFORT_LEVEL`, `effortLevel` in settings.json, per-turn `ultrathink`. Precedence for agents: `CLAUDE_CODE_EFFORT_LEVEL` env > agent frontmatter `effort` > session level.

### Codex CLI

Agent TOMLs **omit `model` entirely** to inherit the session/profile model – there is no `inherit` sentinel in Codex, so leaving the key out *is* the inherit signal. Per-agent `model_reasoning_effort` sets depth. The session/profile (`codex --profile X`, `-m`) is the user's model choice. AndThen's `scripts/generate-codex-agents.sh` reflects this: it emits no `model` line and passes each agent's `effort:` through to `model_reasoning_effort` (clamping `max` → `xhigh`).

### AndThen agents

The review-council and `research` agents (`plugin/agents/*.md`) carry `model: inherit` plus an explicit `effort:` (reasoning-heavy personas like security/correctness/critic at `high`; specialists, filters, and `research` at `medium`). `documentation-lookup` is the shipped cheap-tier leaf – `model: haiku`, `effort: low` – because pure retrieval is tier-flat and high-volume (see the alias-pin principle below). These dedicated configs are the exception; ad-hoc callers provide task shape and defer both model and effort to the policy.

---

## Durable principles

- **Alias-pin the cheap tier for small, well-specified work; never version-pin executable config.** Naming a *version ID* (`claude-opus-4-8`, `gpt-5.4`) rots and is forbidden in executable config. Naming a *tier alias* (`haiku`) floats to the current model in that tier, so it does not rot. Where this earns its keep is tier-flat, high-volume leaves – `documentation-lookup` pins `model: haiku` on Claude; Codex omits the model line and inherits, since it has no rot-free small-tier alias to pin. The guardrails template's concrete names are non-executable, availability-checked examples in a document the project maintains; unavailable examples inherit rather than being guessed.
- **The session model is the single deliberate knob.** Choose it consciously: it is the ceiling, and every delegated task routes at or below it. If the session runs a 1M-context variant, fan-out leaves inherit that too – so pick the session variant with fan-out cost in mind, not just the orchestrator's needs.
- **Adaptive thinking > static budgets.** On current models, interleaved thinking between tool calls matters more for agentic work than a high effort floor everywhere. Prefer letting the model think adaptively over forcing high effort on routine work.
- **Diminishing returns on pure thinking.** For tool-heavy agentic tasks, the number and quality of tool calls matters as much as thinking depth. Raising effort is not a substitute for a well-scoped brief.
- **Fan-out cost compounds with parallelism.** A council or batch can spawn many agents at once. Default leaves to `low`/`medium` and escalate per-turn (`ultrathink`) or per-agent rather than raising the session floor globally.
- **Escalate narrowly, not globally.** Bump the specific hard turn or agent, not the whole session.
