# Model & Effort Selection Guide

How AndThen steers reasoning depth across Claude Code and Codex CLI. Principles only – no model version numbers, prices, or benchmark tables (those rot; consult the harness/provider docs for current specifics).

---

## Default policy: inherit the model, vary the effort

AndThen ships a named, overridable **Sub-Agent Model Policy** (defined in `CRITICAL-RULES-AND-GUARDRAILS.md`). The default: every agent – orchestrator and sub-agents alike – runs on **whatever model the session is using** (`inherit`), and the only thing that varies per task is **reasoning effort**.

Under the default there is **one model knob**: the session model the user launches with. AndThen names no *version-pinned* model anywhere, so nothing goes stale, and the user's choice (including a 1M-context variant) flows through to every sub-agent automatically. Reasoning depth – the thing that actually differs between scanning a file and auditing security – is set directly via effort, not by swapping to a bigger or smaller model.

**The one exception is `documentation-lookup`**, which pins `model: haiku` (see the alias-pin principle below). Pure retrieval is quality-flat across model tiers and is the highest-volume leaf, so the cheap tier is strictly better there. This is a *tier alias*, not a version pin, so it does not rot; on Codex the generator omits the line and the agent inherits.

### Overriding the default

Projects or users that want task-tiered routing (e.g. judgment→top tier, implementation→mid, mechanical→cheap) replace the Sub-Agent Model Policy section in their guardrails copy, or define one in project/user instructions – the nearest definition wins. Skills defer to the policy by *name* and describe each sub-agent's **task shape** (retrieval / routine / cross-cutting judgment) plus effort, so an override re-routes them without skill edits. The never-version-pin invariant (see the durable principles below) binds every strategy.

---

## Effort levels

Effort is a **behavioral signal, not a hard token cap** – even at `low`, the model still thinks on genuinely hard problems, just less.

| Level | Behavior | Use for |
|-------|----------|---------|
| **low** | Minimal thinking, max speed. | Retrieval, doc-lookup, scanning, formatting, trivial edits, high-volume parallel leaves |
| **medium** | Balanced – thinks when useful. The default. | Routine coding, tests, docs, execution sub-agents, routine reviews |
| **high** | Almost always thinks deeply. | Architecture, trade-offs/ADRs, security audits, subtle debugging, cross-cutting gap review, specs |
| **xhigh / max** | No constraints on depth. (`max` is Anthropic-only; Codex tops out at `xhigh`.) | Critical one-off decisions, the hardest problems |

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

The review-council and `research` agents (`plugin/agents/*.md`) carry `model: inherit` plus an explicit `effort:` (reasoning-heavy personas like security/correctness/critic at `high`; specialists, filters, and `research` at `medium`). `documentation-lookup` is the sole model-pinned exception – `model: haiku`, `effort: low` – because pure retrieval is tier-flat and high-volume (see the alias-pin principle below). Orchestrating skills that spawn ad-hoc sub-agents defer to the Sub-Agent Model Policy by name and set effort by task.

---

## Durable principles

- **Alias-pin only for tier-flat, high-volume retrieval; never version-pin.** Naming a *version ID* (`claude-opus-4-8`, `gpt-5.4`) rots and is forbidden. Naming a *tier alias* (`haiku`) floats to the current model in that tier, so it does not rot. The one place this earns its keep is `documentation-lookup`: pure retrieval is quality-flat across tiers and is the highest-volume leaf, so it pins `model: haiku` on Claude. Codex omits the model line and inherits, since it has no rot-free small-tier alias to pin. Everything else inherits under the default policy; a tiered override may route by task, but the never-version-pin invariant binds it just the same.
- **The session model is the single deliberate knob.** Choose it consciously: under the default policy every sub-agent inherits it. If the session runs a 1M-context variant, fan-out leaves inherit that too – so pick the session variant with fan-out cost in mind, not just the orchestrator's needs.
- **Adaptive thinking > static budgets.** On current models, interleaved thinking between tool calls matters more for agentic work than a high effort floor everywhere. Prefer letting the model think adaptively over forcing high effort on routine work.
- **Diminishing returns on pure thinking.** For tool-heavy agentic tasks, the number and quality of tool calls matters as much as thinking depth. Raising effort is not a substitute for a well-scoped brief.
- **Fan-out cost compounds with parallelism.** A council or batch can spawn many agents at once. Default leaves to `low`/`medium` and escalate per-turn (`ultrathink`) or per-agent rather than raising the session floor globally.
- **Escalate narrowly, not globally.** Bump the specific hard turn or agent, not the whole session.
