# GPT-Specific Prompt Engineering Guidelines

What changes when the reader is a current OpenAI model – GPT-6 Astra (the default) or GPT-5.6 (Sol, Terra, Luna) – and the host is Codex CLI. Read `PROMPT-ENGINEERING-GUIDELINES.md` first; this file adds only what is specific to these models. Model choice and reasoning effort belong to the harness and the role definitions, never to prose: see `docs/MODEL-EFFORT-SELECTION-GUIDE.md`.

## Behaviour that changes what you write

- **Under-persistence.** Astra can stop at a first implementation and hand back for review while work remains, and any "stop for review", "confirm before", or "ask if unsure" line pulls that stopping point earlier. Define what done means before the work starts, and treat "can you…" and "I want to…" as instructions to do the work.
- **Restraint and verification text bites hardest here.** Astra takes "ask first" and hard "never" lines literally and pauses on safe, expected actions, and it tests and reads on its own, so "run the tests" and "read the docs first" produce redundant work. The GPT-5.6 guide's autonomy policy is the shape: state each real constraint once, name the safe local actions, and reserve confirmation for external writes, destructive or irreversible acts, purchases, and scope expansion.
- **Formatting and slop drift.** Astra tends toward long, formatted answers with recurring phrases; the anti-slop snippet below is the fix. "Be concise" over-shortens GPT-5.6; ask for the shape the reader needs instead.
- **Under-delegation.** Parallel subagent work happens only when the prompt asks for it.
- **Mixed-model repositories.** Guidance tuned for Sol or Luna over-constrains Astra. Write for the most capable model that will read the file and drop constraints only an older model needed.

## What still earns its place

- **A contradiction audit across skills, AGENTS.md, and references.** OpenAI strongly recommends it: conflicting guidance makes the model pause and block work early. It outranks trimming.
- **Instruction precedence.** The user's instructions take precedence over a skill's; say so once.
- **Scope discipline.** Approval to complete a task does not expand it.

## Snippets

Tested text from the Astra guide, verbatim. Reuse it as written; paraphrase loses what was tested. These belong in the harness prompt or `AGENTS.md`; a skill states only its own contract.

Autonomy, when more autonomous work is wanted:

> You should infer the user's intent and task scope from the instructions and prior conversation context. Your job is to bias towards action and carry the user's intended task to completion.
>
> When the user expresses intent to perform new work or fix an existing issue, persist until the user's intended goal is complete. Progress autonomously towards the user's goal (e.g. creating isolated worktrees / checkouts if needed, resolving merge conflicts, read-only actions, creating draft PRs etc.) unless they are clearly destructive or irreversible.

Follow-through, when the model asks for clarification the request already implied:

> When the user's prompt indicates a request for action, such as "can you...", "I want to...", "help me..." and similar expressions, treat these as instructions to do the work and take action. Do not stop at acknowledging capability (e.g. "Yes…"), proposing a plan, or offering to continue. Do not settle for a partial or "helpful enough" solution that does not fully satisfy the user's task to save time, effort or tokens. If a task requires sustained work, complete all the necessary work until the intended outcome is fulfilled.

Approve last:

> Before asking the user clarifying questions, you should complete the work that is already authorized from context and necessary to make the proposed action concrete and reviewable. The user should be approving a concrete, reviewable result. For example, before deploying a change, writing to an external application, merging a PR or publishing a site, do all the required work first so that user approval is the final step. You don't need user permission for reversible tasks, read-only actions, reviews or fixes, or anything for which authorization is provided earlier in the session or strongly implied from the task instruction.
>
> Do not introduce unsolicited warnings, disclaimers, approval flows, or safety/compliance checklists due to hypothetical risk.

Instruction precedence:

> The user's instructions take precedence over guidelines provided in a skill. If explicit user instructions conflict with a skill's instructions, prioritize the user's instructions.

Conflict diagnostics, to find silent or conflicting guidance when many skills and instruction files load:

> If a skill causes you to ask for permission or confirmation, pause, leave requested work unfinished, or diverge from the user's intent, name and link to the exact SKILL.md file you read, quote the relevant instruction, and briefly explain how it applies. Distinguish explicit skill requirements from your interpretation of guidelines.

Anti-slop:

> Avoid using slop words or phrases like "Bottom Line:" in conclusions, "delve," "foster," "leverage," "it's worth noting," "importantly," "Question? Answer." or "This isn't about X. It's about Y.", "genuinely" or hyphenated compound descriptions and adjectives. Do not use concluding summary statements such as "In short:..", "The simplest mental model is:...".
>
> State the intended action directly. Avoid adding what you won't do, what will remain unchanged, or how you'll separate or categorize results. Do not use contrastive framing such as "X, not Y" or "X—not Y" that introduces an unprompted alternative that the user didn't ask about. Avoid invented compound labels like "exact-head checks" and "editorial-row layouts", vague qualifiers, and canned transitions; use plain verbs and prepositions to state the actual relationship directly.

## Codex packaging limits

- The skills list (every installed skill's name and description) is capped at 2% of the context window, or 8,000 characters when the window is unknown; Codex shortens descriptions first, then drops skills with a warning. AndThen's 26 shipped descriptions total about 8,350 characters, so description length is a budget shared by every skill, not a style choice.
- The AGENTS.md chain is capped at 32 KiB (`project_doc_max_bytes`); files beyond it are dropped. "Keep it small" is the only stated size rule.
- Skill names stay under 64 characters, and the entry file is "as short as the task permits – a large upper bound is not a target".
- Long descriptions and over-broad triggers contradict each other and load skills that do not help the task.

## Parameters

Astra rejects `reasoning.effort: none`, `temperature`, and `top_p`; GPT-5.6 defaults to medium effort. Prose cannot set any of these.

## References

- Using GPT-6 Astra (behaviour and the snippets above) – https://developers.openai.com/api/docs/guides/latest-model
- GPT-5.6 guide ("Favor leaner prompts", autonomy and approval boundaries) – https://developers.openai.com/api/docs/guides/latest-model/gpt-5.6
- Rethinking skills and prompts for GPT-6 Astra – https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra
- Reasoning guide and prompt engineering guide – https://developers.openai.com/api/docs/guides/reasoning and https://developers.openai.com/api/docs/guides/prompt-engineering
- Codex skills, AGENTS.md, and customization – https://developers.openai.com/codex/skills, https://developers.openai.com/codex/guides/agents-md, https://developers.openai.com/codex/concepts/customization
