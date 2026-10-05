# Model & Effort Selection Guide

How AndThen steers model and reasoning depth across Claude Code and Codex CLI. Principles only – no model version numbers, prices, or benchmark tables (those rot; consult the harness/provider docs for current specifics).

---

## The model: four optional roles, one generic fallback

A subagent's model and effort are set per spawn call – the model where the host's spawn tool offers one, the effort on Codex – or pinned once by an agent definition loaded at session start. AndThen therefore ships its delegation policy in two parts:

- **The Subagent Model Policy** (in the CRITICAL-RULES guideline `init` places in project or user rules) routes by task, on two questions: how pinned is the scope, and how much judgment does it take. Judgment work – orchestration, planning, spec authoring, architecture, design, ambiguous or creative work – stays in the **session**, whose model the user chose for exactly that; nothing routes above it.
- **Four opt-in role agents**, installed by `andthen:init` at user or project level in both host formats (`.md` for Claude Code, `.toml` for Codex). Each definition pins the model and effort currently recommended for the tier the policy routes to it. A tier is a capability class, not a fixed model, so two roles can share one:

- **`oracle`** – S-tier model. Judgment work the user assigns it, and hard problems an agent hands over because they exceed its tier – the hand-over states what was tried and what stays unexplained. Never self-selected for routine judgment, never an agent's consult – a second opinion on a decision is the user's to ask for.
- **`implementer`** – A-tier model. One fully specified unit: executing a story or spec, authoring a plan story's FIS, research that weighs or synthesises.
- **`reviewer`** – A-tier model. Every review pass – code, doc, gap, per-story review, Critic. Its effort sits below `implementer`'s deliberately: higher review effort bred analysis-paralysis and scope creep, not findings.
- **`worker`** – B-tier model. Small, well-specified, verifiable subtasks – retrieval, scans, mechanical edits, fact lookups – with exact scope, output contract, and done-criterion in the prompt.

Nothing auto-loads: without the roles, delegation still works through the generic fallback – a plain inherited subagent whose prompt invokes the skill or loads the reference. Effort then inherits from the session, and the model is chosen only where the spawn tool offers one, never above the session's. The role is the only thing that can exceed the session's tier, and only because its definition says so.

### Overriding the default

A project's own agent definitions win over the installed roles; a project or user that wants different routing edits the Subagent Model Policy in its own rules copy – the nearest definition wins. Skill prompts name the role for each dispatch's **task shape** – `worker`, `implementer`, `reviewer`, or a generic inherited subagent for judgment – never a model or effort; the roles select those. The never-version-pin invariant governs AndThen's shipped content; a project's own copies are the project's to maintain.

---

## Effort levels

Effort is a **behavioral signal, not a hard token cap** – even at `low`, the model still thinks on genuinely hard problems, just less.

| Level | Behavior | Use for |
|-------|----------|---------|
| **low** | Minimal thinking, max speed. | Retrieval, doc-lookup, scanning, formatting, trivial edits, high-volume parallel leaves |
| **medium** | Balanced – thinks when useful. The default. | Routine coding, tests, docs, reviews |
| **high** | Almost always thinks deeply. | Story and spec execution, subtle debugging |
| **xhigh / max** | No constraints on depth. (`max` is Anthropic-only; Codex tops out at `xhigh`.) | The session's own judgment work: planning, architecture, design, trade-offs/ADRs, the hardest one-off decisions |

---

## How to set it

Skill frontmatter (`plugin/skills/*/SKILL.md`) carries no model or effort override; the roles and the host's own knobs are the whole surface.

### Claude Code

The session model is the user's choice (`/model`, `claude --model`, the alias system including 1M variants) – AndThen does not override it. Session-level effort: `/effort`, `claude --effort`, `CLAUDE_CODE_EFFORT_LEVEL`, `effortLevel` in settings.json, per-turn `ultrathink`. Role definitions live in `~/.claude/agents/` or `.claude/agents/` with `model:` and `effort:` frontmatter; precedence is `CLAUDE_CODE_EFFORT_LEVEL` env > agent frontmatter `effort` > session level. `init` reports whether the installed roles match the shipped templates.

### Codex CLI

The session/profile (`codex --profile X`, `-m`) is the user's model choice; `model_reasoning_effort` sets depth. Role definitions are `.toml` files under the Codex agents directory; Codex has no `inherit` sentinel, so omitting `model` *is* the inherit signal – the shape the generic fallback relies on.

---

## Durable principles

- **The shipped pins are recommendations, as of each template's last change.** A template's model and effort were the best fit for its tier when the file last changed (`git log` on `plugin/skills/init/templates/agents/`), and both providers change their lineups between AndThen releases, so re-check every pin when either ships or reprices a model, and before a release. On Claude the templates name family aliases, which float within a family; which family serves which tier is part of the recommendation. Codex has no aliases, so its templates name the current model per tier and are the one place a model name is executable config. Dated *version IDs* stay out of everything else.
- **Calibrate effort per host; write it only in the templates.** Providers' models differ in capability, so one effort level lands a tier at different strengths: Sonnet at `low` roughly matched GPT-6-Luna at `high` (2026-09-29), so `worker` pins each. A role description, the Subagent Model Policy, or a doc that repeats a level goes stale at the next recalibration.
- **The session model is the single deliberate knob.** Choose it consciously: it is the ceiling for every generic delegation, and judgment work never leaves it. If the session runs a 1M-context variant, fan-out leaves inherit that too – so pick the session variant with fan-out cost in mind, not just the orchestrator's needs.
- **Adaptive thinking > static budgets.** On current models, interleaved thinking between tool calls matters more for agentic work than a high effort floor everywhere. The roles set a floor per task shape; they do not force high effort on routine work.
- **Diminishing returns on pure thinking.** For tool-heavy agentic tasks, the number and quality of tool calls matters as much as thinking depth. Raising effort is not a substitute for a well-scoped brief – which is why `worker` prompts carry exact scope and done-criterion.
- **Fan-out cost compounds with parallelism.** A fan-out or batch spawns many agents at once; leaves run at their role's pin, or the session's model for a judgment fan-out, and escalation is per hard turn (`ultrathink`) or per agent, never the session floor.
- **Escalate narrowly, not globally.** On a quality miss, move one tier up – `worker` to `implementer`, `implementer` to the session – rather than retrying unchanged or raising the whole session.
