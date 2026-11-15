# Model & Effort Selection Guide

How AndThen steers model and reasoning depth across Claude Code, Codex CLI, and Copilot CLI, and how each role's pin is chosen. Principles and the selection rule only: no model version numbers, prices, or benchmark tables, because those rot. The last recalibration's scored shortlist is `docs/ROLE-PINS.md`, and the project-level `recalibrate-roles` skill (`.claude/skills/recalibrate-roles/`) runs the procedure.

---

## The model: four optional roles, one generic fallback

A subagent's model and effort are set per spawn call (the model where the host's spawn tool offers one, the effort on Codex) or pinned once by an agent definition loaded at session start. AndThen therefore ships its delegation policy in two parts:

- **The Subagent Model Policy** (in the CRITICAL-RULES guideline `init` places in project or user rules) routes by task, on two questions: how pinned is the scope, and how much judgment does it take. Judgment work (orchestration, planning, spec authoring, architecture, design, ambiguous or creative work) stays in the **session**, whose model the user chose for exactly that; only the two `oracle` gates below route above it.
- **Four opt-in role agents**, installed by `andthen:init` at user or project level in each host's format (`.md` for Claude Code, `.toml` for Codex, `.agent.md` for Copilot). Each role is a tier: a task shape with its own selection rule (below), pinned per host to the model and effort that rule picks. Two roles can share a model and differ by effort.

- **`oracle`**: judgment work the user assigns it, and hard problems an agent hands over because they exceed its tier. The hand-over states what was tried, what every attempt assumed, and what stays unexplained. Never self-selected for routine judgment, never an agent's consult: a second opinion on a decision is the user's to ask for. Two skills name it at a gate, each once per run (ADR-031): `decide` takes its second opinion on the one-way doors before they are confirmed, and `plan`, when it breaks the work into several stories, takes one on the reviewed bundle and its open items before Preflight.
- **`implementer`**: one fully specified unit, such as executing a story or spec, authoring a plan story's FIS, or research that weighs or synthesises.
- **`reviewer`**: every review pass (code, doc, gap, per-story review, Critic). Its effort stays at `medium` unless reviews are observed missing defects, because higher review effort bred analysis-paralysis and scope creep, not findings.
- **`worker`**: small, well-specified, verifiable subtasks (retrieval, scans, mechanical edits, fact lookups) with exact scope, output contract, and done-criterion in the prompt.

Nothing auto-loads: without the roles, delegation still works through the generic fallback, a plain subagent on the session's model and effort whose prompt invokes the skill or loads the reference. Only a role can run on a model other than the session's, and only because its definition says so.

### Overriding the default

A project's own agent definitions win over the installed roles; a project or user that wants different routing edits the Subagent Model Policy in its own rules copy, and the nearest definition wins. Skill prompts name the role for each dispatch's **task shape** (`worker`, `implementer`, `reviewer`, `oracle` at its gates and `triage`'s hand-over, or a generic inherited subagent for judgment), never a model or effort; the roles select those. The never-version-pin invariant governs AndThen's shipped content; a project's own copies are the project's to maintain.

---

## Choosing a role's pin

A pin is chosen in two stages. Stage 1 is judgment about what the benchmarks do not measure, written down with its reasons. Stage 2 is arithmetic on benchmark scores and measured cost, so anyone can rerun it from the published numbers.

### Sources

Three fixed sources are re-tested on every run, each in its own role:

- **Artificial Analysis** is the scorer: the coding and general scores and the run cost of every (model, effort) pair.
- **SWE-rebench** (tasks mined monthly from active repositories) and **DeepSWE** (tasks written from scratch) are checks: independent coding scores with published intervals.

Each run also searches for newer contamination-resistant coding benchmarks and admits any that pass as checks for that run only.
A fixed source that fails a run is recorded in `docs/ROLE-PINS.md` and skipped, not dropped.
Replacing one is the user's call, proposed when a fixed source failed both this run and the one before, per that record, and a found source passed this run.

The scorer must pass all six items below; a check must pass items 1–3 and have scored both pairs it compares (the **coverage clause**):

1. It names its operator, method, and task source.
2. Its tasks resist contamination: private, held out, or written after the scored models' training, not drawn from public repositories or exercises models can have trained on.
3. Its runner is independent of the model vendors, and vendor-reported scores are excluded or marked.
4. It scores each effort level separately.
5. It reports cost per task, or token counts and prices from the same run, with cache pricing applied.
6. It has scored the current lineup of every host being calibrated.

A composite passes item 2 when the components that pass it carry most of its weight.
Among admitted sources, private or held-out tasks outrank fresh public ones, and a benchmark an independent audit rates flawed counts only as a minority weight inside a composite.
An aggregator that merges vendor-reported numbers under undisclosed weights fails item 1.
Use the scorer's run for both score and cost, so the two describe the same work.

Where a check ranks the rule's pick below another eligible pair by more than the check's own margin, the pin stays as it is and the conflict goes to the user, because two sound benchmarks that disagree mean neither settles the pick.

Two scores feed the rule: a **coding score** (the scorer's own coding composite where it defines one) and a **general score** (its broad index).
Cost is the measured cost of the run, never list price per token, because step count and verbosity differ more between pairs than prices do.
The **margin** is the score's 95% interval; where the source publishes none, estimate it from task and trial counts and record the estimate in `docs/ROLE-PINS.md`.

### Stage 1: eligible models

- **`oracle`**: any model the host offers.
- **`implementer` and `reviewer`**: the provider's mid flagship, the model it positions for complex technical work below its top model. The top model is reserved for `oracle`: its cost and turn length are paid on every story, and practitioner reports find it needs more supervision on routine work. Small models are out, because practitioner and provider guidance confines them to read-only, checkable work, and every admitted coding score so far ranks them well below the mid flagship on multi-step edits.
- **`worker`**: models below the mid flagship.
- **No pin uses the top effort level** (`max`): providers reserve it for measuring a model's ceiling, and effort sweeps on private tasks show no reliable gain over the level below.

Change this stage only on new evidence (a provider repositions a model, practitioner reports shift, a new rung appears) and say which in `docs/ROLE-PINS.md`.

### Stage 2: the rule

Candidates are the eligible (model, effort) pairs.

- **`oracle`**: the cheapest pair whose general score is within the margin of the host's best pair.
- **`implementer`**: the lowest effort of the eligible model whose coding score is within the margin of that model's best effort.
- **`reviewer`**: the implementer's model at `medium`.
- **`worker`**: the cheapest pair whose coding score is at least half the implementer pin's.
- **Change a pin only when the rule's pick scores outside the margin of the current pin, or costs at least a third less within it.** Without this, pins flip on noise.

Copilot templates list one Anthropic and one OpenAI model per role, each the rule's pick for its provider, and set the effort the first model's pick uses, since one file carries one effort. List only model IDs GitHub publishes for Copilot CLI.

### Planning sessions

Planning (`clarify`, `plan`, `decide`, `architecture`) is judgment, so it stays in the session but for the two `oracle` gates, and the session model is the user's to pick. The recommendation for it is the `oracle` template's model and effort for the host, because both are chosen for the hardest judgment: `plugin/README.md` says so, and a recalibration that changes the `oracle` pin changes the recommendation with it. Skill frontmatter carries no model or effort override (see How to set it).

---

## Effort levels

Effort is a **behavioral signal, not a hard token cap**: even at `low`, the model still thinks on genuinely hard problems, just less.

| Level | Behavior | Use for |
|-------|----------|---------|
| **low** | Minimal thinking, max speed. | Retrieval, doc-lookup, scanning, formatting, trivial edits, high-volume parallel leaves |
| **medium** | Balanced, thinks when useful. | Routine coding, tests, docs, reviews |
| **high** | Almost always thinks deeply. | Story and spec execution, subtle debugging |
| **xhigh** | Deeper still. (Which levels above `high` a model accepts varies by provider and model, so check before pinning one.) | The session's own judgment work: planning, architecture, design, trade-offs/ADRs, the hardest one-off decisions |
| **max** | No constraints on depth. | Measuring a model's ceiling; no pin uses it |

---

## How to set it

Skill frontmatter (`plugin/skills/*/SKILL.md`) carries no model or effort override; the roles and the host's own knobs are the whole surface.

### Claude Code

The session model is the user's choice (`/model`, `claude --model`, the alias system including 1M variants); AndThen does not override it. Session-level effort: `/effort`, `claude --effort`, `CLAUDE_CODE_EFFORT_LEVEL`, `effortLevel` in settings.json, per-turn `ultrathink`. Role definitions live in `~/.claude/agents/` or `.claude/agents/` with `model:` and `effort:` frontmatter; precedence is `CLAUDE_CODE_EFFORT_LEVEL` env > agent frontmatter `effort` > session level. `init` reports whether the installed roles match the shipped templates.

### Codex CLI

The session/profile (`codex --profile X`, `-m`) is the user's model choice; `model_reasoning_effort` sets depth. Role definitions are `.toml` files under the Codex agents directory; Codex has no `inherit` sentinel, so omitting `model` *is* the inherit signal, the shape the generic fallback relies on.

### Copilot CLI

The session model is the user's choice (`/model`, `copilot --model`, `--reasoning-effort`). Role definitions are `.agent.md` files with `model:` and `reasoning-effort:` frontmatter (kebab-case; `reasoningEffort` is silently ignored). A `model:` list loads as the first model plus fallbacks. An effort the model does not support draws a warning and keeps the session's effort rather than failing.

---

## Durable principles

- **The shipped pins are recommendations, as of each template's last change.** A template's model and effort were the rule's pick at the last recalibration, recorded with its numbers in `docs/ROLE-PINS.md`. Both providers change their lineups between AndThen releases, so recalibrate when either ships or reprices a model, and before a release. On Claude the templates name family aliases, which float within a family; which family serves which role is part of the recommendation. Codex has no aliases, so its templates name the current model per role and are executable config. Copilot's templates name a priority list, because which models a Copilot user may select depends on their plan and organization policy, and a single pin the user cannot select is unusable. Dated *version IDs* stay out of everything else.
- **Calibrate effort per host; write it only in the templates.** Providers' models differ in capability, and effort labels are not comparable across providers, so each host's template pins its own model and effort for the role. A role description, the Subagent Model Policy, or a doc that repeats a pinned level goes stale at the next recalibration.
- **The session model is the single deliberate knob.** Choose it consciously: it runs every generic delegation, and judgment work never leaves it. If the session runs a 1M-context variant, fan-out leaves inherit that too, so pick the session variant with fan-out cost in mind, not just the orchestrator's needs.
- **Adaptive thinking > static budgets.** On current models, interleaved thinking between tool calls matters more for agentic work than a high effort floor everywhere. The roles set a floor per task shape; they do not force high effort on routine work.
- **Diminishing returns on pure thinking.** For tool-heavy agentic tasks, the number and quality of tool calls matters as much as thinking depth. Raising effort is not a substitute for a well-scoped brief, which is why `worker` prompts carry exact scope and done-criterion.
- **Fan-out cost compounds with parallelism.** A fan-out or batch spawns many agents at once; leaves run at their role's pin, or the session's model for a judgment fan-out, and escalation is per hard turn (`ultrathink`) or per agent, never the session floor.
- **Escalate narrowly, not globally.** On a quality miss, move one step up (`worker` to `implementer`, `implementer` to the session) rather than retrying unchanged or raising the whole session.
