# Skill-Authoring Guidelines

How to write a `SKILL.md` bundle that a current frontier model runs well at the smallest context cost. Anthropic's Agent Skills best-practices page and the Agent Skills specification own the general doctrine; this document carries the numbers, what the current model generation changes, and this repository's own craft and constraints. Read `docs/prompt-guidelines/PROMPT-ENGINEERING-GUIDELINES.md` first – it says what belongs in any prompt and what no longer does.

**Audience**: anyone, human or agent, authoring or reviewing a skill bundle.

## What a skill is

A folder – `SKILL.md` plus optional references and scripts – that an agent discovers by name and description and loads on demand. It is an onboarding guide for a capable new hire, not a manual: it carries what the model cannot know (this project's contracts, the counter-intuitive rules, the named failure modes) and nothing the model already does unprompted.

It loads in three levels – progressive disclosure – and each level is paid differently:

| Level | Loads | Cost |
|---|---|---|
| Metadata (`name`, `description`) | Every turn, every installed skill | ~100 tokens per skill, always |
| Body | On trigger, then stays in context | Under 500 lines / 5k tokens |
| References and scripts | On explicit read or run | Zero until used |

The limits, from the specification and the hosts:

| Item | Limit | Source |
|---|---|---|
| `name` | 1–64 chars, lowercase, hyphens, matches the directory | Agent Skills spec |
| `description` | 1–1,024 chars; Claude Code allows 1,536 with `when_to_use` | spec; Claude Code |
| All descriptions together | 2% of the context window, or 8,000 chars when unknown | Codex |
| `SKILL.md` body | Under 500 lines, under 5k tokens | spec |
| References | One level deep from `SKILL.md` | spec; the installer enforces it |
| Reference table of contents | Files over 100 lines | Anthropic |
| Instruction files | `AGENTS.md` chain 32 KiB on Codex; `CLAUDE.md` under 200 lines | Codex; Claude Code |

Codex shortens descriptions and then drops skills when the shared budget overflows; this repository's 27 shipped descriptions total about 7,300 chars, under the 8,000 fallback only while every one stays lean. Description length is a packaging budget every skill shares.

## Frontmatter

Claude Code reads `name`, `description`, `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `background`, `hooks`, `paths`, `shell`, `metadata`, `license`, `compatibility`. Only `name`, `description`, `license`, `metadata`, `compatibility`, and `allowed-tools` are in the specification; the rest are host extensions, and Codex reads its own `agents/openai.yaml` beside the skill.

- The `/command` name comes from the directory, not `name`.
- `model` and `effort` stay out of shipped AndThen skills: the role definitions and the session are the only steering surface (`docs/MODEL-EFFORT-SELECTION-GUIDE.md`).
- `context: fork` runs the body as a fresh subagent's prompt with no access to the conversation; use it only for a skill that is an actionable task, and pair it with `agent` to pick the subagent type.
- `disable-model-invocation` and `user-invocable` stay out of shipped AndThen skills: every capability is a skill both a user and a subagent can invoke (`docs/DECISIONS.md`, "No model-only or user-only skills").
- `allowed-tools` pre-approves; it does not sandbox. List what the skill needs so review is legible.

## Description engineering: the trigger surface

It is the only text the model sees before the skill fires, it loads every turn, and Codex trims it first. Write it as one discriminating sentence pair:

- Third person, present tense: what the skill does, then when to use it, in the words users actually say.
- The load-bearing trigger first: earlier text wins under primacy bias and survives budget trimming.
- One boundary clause when an adjacent skill is easily confused ("not for executing an existing spec – that is `exec-spec`").
- No manual, no option menu, no procedure.
- Calibrated urgency is allowed here, because skills under-trigger, and nowhere else in the bundle.

Failure modes: too vague (never selected); too broad (fires on unrelated work – tighten the boundary or set `disable-model-invocation`); a term the description uses and the body never explains; a description that grows one phrase per missed trigger – enumerated queries generalize worse than a named category of intent.

## The body

Written for the model that executes it, read once when the skill fires, and laid out for the person who maintains it. Prompts and skills written for prior models are too prescriptive for the current generation and reduce output quality (Anthropic's migration guide; OpenAI's Astra guidance): state the goal, the constraints, the verification, and the named failure modes, and let the model plan.

- **Intent over procedure.** Match specificity to fragility. An open field takes a direction and heuristics; a narrow bridge with cliffs – migrations in sequence, destructive commands, auth flows – takes the exact command. Numbered steps only where one sequence is safe.
- **Why beside the rule.** A rule with its reason generalizes to cases the author never listed; a bare rule is followed rigidly or rationalized past. The reason is what earns the tokens.
- **Leading words** (a project convention, unmeasured)**.** Name a load-bearing rule with a term that carries pretraining weight (*Chesterton's Fence*, *Stop-the-Line*, *tracer bullet*) and reuse the term verbatim in description, body, and references. The term replaces its explanation: keep only what the project adds to the common meaning, and settle what that meaning is by asking the cheapest model cold, never from your own recall. A coined term recruits no priors and costs its definition every time.
- **Gates over steps.** A phase ends on a falsifiable condition ("every modified model accounted for"), not an action ("produce a change list"). A gate has two dials: clarity, so done is distinguishable from not-done, and demand, so satisfying it forces the invisible work. Visible later phases pull the model toward being done – *premature completion*; sharpen the current gate first, and hide later phases behind a fresh subagent only when rushing is observed in runs.
- **Dispatch sites.** A delegating step writes the dispatch, never the work: which skill the subagent invokes, fresh context or in-session and why, the values it cannot derive, the return shape the caller parses. Values pass as that skill's arguments. The skill body loaded there is the **Single Authority**; a hand-rolled prompt is a second copy that drifts.
- **The host already speaks.** Before a skill states an autonomy, scope, progress, or formatting rule, read the host's system prompt – the general guidelines say why – and keep instruction precedence (the user's instructions over a skill's) in `AGENTS.md` once, never per skill.
- **Headless by default.** Execution skills run to completion on recorded assumptions; a decision never stops a run, only an unusable call does. Discovery and design skills are interactive by contract – the interview is the deliverable – and say so; suggested or preselected answers are never confirmation.
- **The argument line.** The body opens with one sentence placing the single `$ARGUMENTS` substitution point and stating only what `argument-hint` cannot – a default, a validity rule, a resolution order. No usage block and no variables block re-deriving the hint.
- **Data in lists**, on the general guidelines' terms. In a skill the data is a verb's output tokens and what each one triggers, a route chosen by flag or host, a dispatch's return shape.
- **Tables hold short cells.** A cell is a phrase; a sentence or an instruction becomes a list (`tests/test_table_legibility.py` fails any cell over 200 chars).

## Pruning

Length itself buys no compliance; what it costs, and what conflict costs, is in the general guidelines. Prune in this order:

1. **Conflict audit.** Read the body, its references, `AGENTS.md`, and the host prompt together and resolve every pair that pulls in different directions. This comes first because no cut repairs a conflict.
2. **The distillation test, per consuming path.** Delete the block: does a competent frontier model now do something different, and worse, on this path? Only three answers keep text: a counter-pretraining calibration (the untutored default is wrong), a named agent failure mode (a behaviour models actually exhibit), or a contract another skill or a parser reads. A block that is contract on one path and inert on another fails the test on the second path; the cure is a split by consumer, not a rewrite.
3. **The four failure modes**, by name. *Duplication* – one meaning stated twice, already drifting; one canonical statement. *Sediment* – layers left by add-only edits; rework the section whole. *Sprawl* – material only some paths need, inline; move it to a reference loaded behind a condition the model decides without judgment (a flag, a mode, a host). *No-op* – what the model does unprompted ("be thorough") and filler; delete, and settle disputes by running the skill.
4. **Count live instructions on the loaded path.** Compliance degrades from roughly 150–200 simultaneous instructions across system prompt, instruction files, skill, and references, and earlier instructions win.
5. **Prove nothing was lost.** Before the first edit, list the contracts on the loaded path: tokens, flags, arguments, dispatches, gates, named failure modes, literal commands, paths, numbers, and each rule with its reason. After the last, each one is kept, moved, or cut with its keeper named.
   - A moved item sits in a reference whose load site comes before the first step that needs it, under a condition shown true on every invocation that reached it. A gate or fail-fast check stays in the body, because position is part of its contract.
   - Diff the code spans of the before and after text with a command; reading misses omissions.
   - A fresh-context reviewer builds its own list from the before text and resolves it against the after text.
   - Re-run the skill's test or eval case.
   - Doubt reverts the edit: a regression costs more than the characters saved.

Contract markers that protect a span: an imperative lead verb, enumerated inputs, outputs, or modes, a counter-prior phrase ("preserving exact behaviour"), a verification commitment, a fail-fast gate at the top of the body – position is part of that contract. Always-safe cuts – the general guidelines' anti-patterns – usage blocks restating slash syntax (`argument-hint` owns it), description restatement, generic virtues, migration phrasing ("now", "no longer"), retired-model workarounds, examples of judgment the model owns. Examples survive only where they pin an output shape, on the general guidelines' terms.

When unsure whether the model already knows a span, propose the cut, unless a contract marker is present: redundant context cost 14–22% more reasoning tokens and lowered task success in the measured cases, and step 5 catches a wrong cut on a contract. Off that list nothing does, so name where the behaviour still comes from. A cut removes meaning the model does not need, never markup: collapsing a list into a paragraph or chaining sentences with dashes lowers the character count and keeps every instruction, harder to find. The size of a lean skill is whatever survives this pass; a remainder still too large for one trigger means moving content out of per-run context – a deeper tier, a split by consumer – not trimming harder. The shipped surface as a whole carries one aggregate word budget (ADR-018): a budget on an authored artifact, like the description budget above, not the output shaping the prompt guidelines reject. A change that grows past it cuts elsewhere or raises the number in the same commit, where the raise is one reviewed line.

## Scripts and references

Script source never enters context; only its output does. Deterministic work goes to a script, with explicit error handling and specific messages, and the body says whether to run it or read it. References are rubrics – a lens, a calibration, a schema, a contract – never a procedure handed to a subagent as "read this and perform it"; one file per domain so a task loads only its own; a table of contents above 100 lines; MCP tools named `Server:tool`.

**Loading a reference.** A reference loads where its path appears in `SKILL.md` – `references/<name>.md` for the skill's own file, `../../references/<name>.md` for a canonical, both relative to the skill root the host announces – as a link URL or a code span; the sentence around the path says what the file carries and when to read it, an unconditioned path meaning read it on reaching the line. A mode table's cells carry the paths. A bare `<name>.md` or a declared alias (*The Authoring Guidelines*) is a mention and loads nothing, so it may name only a file the same body already loads by path, or another skill's file as a fact – a model opens what a step needs and it can resolve, so a bare name of an unloaded file that exists under `references/` is a load waiting to happen, and `install-skills.sh --validate-only` fails on it. Every file but `SKILL.md` mentions and never links or paths, code fences included: chained loads get partial reads (`head`), which is why references stay one level deep.

## Prove it

- **Evaluation-driven authoring**, on the general guidelines' terms: baseline the model unaided, write the minimum text that fixes the observed failures, keep the cases, re-run after every cut, and test each tier the skill will meet.
- **This repository's gates**: the fast tier in `AGENTS.md` § Testing, the install validate-only check, the eval cases under `evals/cases/`.

## Repository constraints

`AGENTS.md` states them once – § Skill And Agent Model (no invocation sigils, `andthen:<name>` with the type noun adjacent, the wording audit) and § Maintenance Contracts (the README and CHANGELOG obligations, no tests under `plugin/`). A skill change that touches a shared canonical also updates the installer's asset arrays and the Architecture table.

## Checklist

1. Description: third person, what + when in the user's words, trigger first, boundary named, within the shared budget.
2. `argument-hint` matches every input the body accepts.
3. Body under 500 lines; references one level deep, rubric-shaped, table of contents above 100 lines.
4. No instruction conflicts across body, references, `AGENTS.md`, and the host prompt.
5. Every rule carries its reason; no pressure language, no hedges on real requirements.
6. No thinking, planning, or "be thorough" scaffolds; no numeric output caps or update cadences.
7. Steps only where one sequence is safe; every phase ends on a gate.
8. Dispatch sites name the skill and its arguments and say "subagent".
9. Examples only pin an output shape, labelled illustrative.
10. No retired-model workarounds, migration phrasing, history narrative, or dated guidance.
11. One term per concept; leading words reused verbatim, never re-explained.
12. Plain sentences, one concern per paragraph, data in lists, no filler.
13. Deterministic work in scripts, run-or-read stated, MCP names qualified.
14. Proof exists: an eval case or test, and a removal re-run for each cut.
15. After a pruning pass, every contract of the old text is kept, moved, or cut with its keeper.

## Layering

| Topic | Where it lives |
|---|---|
| What belongs in any prompt, what no longer does | `docs/prompt-guidelines/PROMPT-ENGINEERING-GUIDELINES.md` |
| Current Claude generation | `docs/prompt-guidelines/PROMPT-ENGINEERING-GUIDELINES-CLAUDE.md` |
| Current GPT generation and Codex limits | `docs/prompt-guidelines/PROMPT-ENGINEERING-GUIDELINES-GPT.md` |
| Skill packaging, discovery, pruning, this repo's craft | this document |
| Non-negotiable engineering rules | `docs/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md` |

Skill craft wins over general prompt craft for skill files.

## References

- Agent Skills best practices – https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Agent Skills specification – https://agentskills.io/specification
- Claude Code skills – https://code.claude.com/docs/en/skills
- Codex skills and AGENTS.md – https://developers.openai.com/codex/skills, https://developers.openai.com/codex/guides/agents-md
- Instruction count: IFScale, arXiv:2507.11538 (2025); conflict: Instruction Stacking Collapse, arXiv:2608.02639 (2026); file size and position: Instruction Adherence in Coding Agent Configuration Files, arXiv:2605.10039 (2026); context-file content: ETH SRI, Evaluating AGENTS.md (2026)
- Examples: Revisiting Chain-of-Thought Prompting, arXiv:2506.14641; The Few-shot Dilemma, arXiv:2509.13196
