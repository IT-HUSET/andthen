# Prompt Engineering Guidelines for Autonomous AI Agents

What belongs in a prompt-like file – a skill, a reference, an agent prompt, `AGENTS.md` or `CLAUDE.md` – written for the current frontier generation (Claude Fable 5.1, Fable 5, Opus 5, Sonnet 5; GPT-6 Astra, GPT-5.6), and what no longer does. Vendor specifics: [Claude](PROMPT-ENGINEERING-GUIDELINES-CLAUDE.md) | [GPT](PROMPT-ENGINEERING-GUIDELINES-GPT.md). Skill packaging: `docs/SKILL-AUTHORING-GUIDELINES.md`. Model, effort, and API parameters are the harness's: `docs/MODEL-EFFORT-SELECTION-GUIDE.md` and the provider docs.

## The one test

For every line: **could the model already know this?** Keep what only the author knows – the audience and product, environment facts, the quality bar, contracts and their mechanics, the genuinely hard judgment calls, and the reasons behind constraints. That is context, and context is never cruft; too little of it produces generic output, and minimal does not mean short. Cut restatements of trained defaults, behaviour the model does unprompted (thoroughness, planning, tool use, testing), and workarounds for failures the current models no longer have. Justify every cut by the pattern it removes, never by character count.

What leanness buys is not compliance: instruction files of 25 to 500 lines showed no adherence difference across 1,650 coding-agent sessions. It buys tokens, steps, cost, and fewer distractors – human-written non-obvious facts raised task success, restating the repository's own docs lowered it and cost 14–22% more reasoning tokens, and OpenAI's leaner system prompts scored 10–15% higher at 41–66% fewer tokens. Conflict is the other cost: conflicting instructions drove a 96%-to-20% collapse in a 2026 stacking study, make GPT-6 Astra pause and block work, and make Claude spend effort reconciling wordings. Count itself starts to hurt around 150–200 live instructions on the loaded path, and earlier instructions win.

## What no longer belongs

Each of these was written for models that needed it. On current models it is neutral at best and harmful often.

- **Pressure language.** Capitalised MUST, NEVER, CRITICAL over-apply: rigid behaviour, over-triggering, and an anxious register that becomes the output's register. Hedges ("try to", "if possible") on real requirements read as permission to under-deliver. Say exactly what you mean at normal volume; emphasis is a tested fix for one underweighted instruction, never a first-draft register.
- **Thinking and planning scaffolds.** "Think step by step", scratchpad tags, "plan before acting", "be thorough, don't stop early": the models reason and plan internally and these cause over-planning. Depth is an effort setting, not prose.
- **Step choreography for judgment work.** Numbered steps for tasks the model's own plan handles better; prompts written for prior models are often too prescriptive for current ones and reduce output quality. Keep numbered steps only where one sequence is safe.
- **Prohibition lists without provenance.** A prohibition against a failure the model was not going to make anchors it toward that failure, and negated framing destabilises. Keep prohibitions that encode a real constraint or a failure that reproduces on the target model, with the reason; rewrite the rest as the behaviour wanted plus a check.
- **Example over-indexing.** The model copies an example's length, tone, and structure, examples written for an older model freeze that model's behaviour into the new one, and more examples anchor harder. Zero-shot first; where an output shape is format-sensitive, several varied examples labelled illustrative, never one gold output.
- **Numeric output shaping.** Word caps, "summarise every N tool calls", "at most five bullets": remove them together and re-baseline. State the audience and outcome instead ("scan-able, answers only what was asked").
- **Fossils.** Retired-model workarounds; "now", "no longer", "instead of" phrasing – a diff against a prompt the model never saw; patch accretion of narrow conditionals; rules nothing enforces and nobody misses; reminders repeated on a cadence, when a once-stated instruction persists. Write as if the current rules are the only rules that ever existed.
- **Update suppressors and anti-formatting rules.** "Hold all findings for the end", "don't narrate", "never use bullets" were tuned against chatty, over-formatted models; the current generation under-narrates and under-formats with them present. Remove first; if more is wanted, say when user-facing text and formatting are appropriate.
- **Ask-first and stop-for-review reflexes.** "Confirm before…", "ask if unsure", "stop for review after the first implementation" now produce approval pauses on safe actions and earlier stopping points. Define completion, name the safe local actions, and reserve confirmation for destructive, irreversible, external, or scope-expanding acts.
- **Verification and testing nagging.** Current models test, verify, and gather context on their own; "run the tests", "double-check your answer", "read the docs first" produce redundant testing and burnt context. Say when not to. Verification the model cannot do for itself – a fresh-context reviewer, a gate – is stated as a dispatch, not a reminder.
- **Rules the host already states.** The host's system prompt carries generation-specific behaviour rules – autonomy, scope, progress reporting, formatting. Before a skill states one, read the host's prompt: a repeat costs tokens, a contradiction fights the harness.
- **Grader vocabulary and strategy coaching.** "You will be graded on…" pushes effort toward being watched; "it's usually best to…" is the author's heuristic where the model's plan is usually better. State every requirement, delete the rest.

## What still earns its place

- Context and reasons, as above. A one-line role statement is fine; a role statement standing in for context is the defect.
- Exact scripts for fragile operations – destructive commands, auth flows, compliance steps – where only one sequence is safe.
- Contract precision in tool and skill descriptions: what it does, when and when not, each parameter, what it does not return. Under-description is the common failure; the cut is steering and examples, never contract.
- Calibrated urgency in trigger text, because skills under-trigger – never in bodies.
- One end-of-prompt recap of the few key constraints. Working redundancy – the same contract stated in two files that still agree – is a refactoring preference, not cruft; dedupe when the copies disagree or one is loaded where it is inert.
- Instruction precedence – the user's instructions over a skill's – stated once in the project instruction file.
- Re-baselining text for a new generation's failure modes; the vendor files carry the tested snippets. A mitigation names the model it patches so the next release can remove it.

## How to write it

- **Altitude.** Outcome, constraints, and how success is verified; heuristics for open fields, exact commands for narrow bridges.
- **Why beside the rule**, once. The reason is what the model generalises from.
- **Scope stated, not implied.** Current models apply a rule exactly as scoped and do not silently generalize it.
- **Positive behaviour plus a check** where a "never" would go; a gate, a script, or a test enforces what prose only asks.
- **Prose for behaviour, structure for data.** A rule stays one sentence with its reason: bullets flatten priority and sever the two, and prompt format bleeds into output format. Data is what the model looks up rather than weighs: a token or condition mapped to an action, a choice between routes, a return shape. It takes a list, one item per key with its reason inline, even inside a behaviour section. In running prose the model has to rebuild the mapping, and a special case hides mid-sentence. Markdown headings or XML tags for unambiguous sectioning; format sensitivity shrinks on stronger models.
- **Laid out for the maintainer too.** The model executes the file; a person reviews and edits it, and a seam or a contradiction hides in a wall of text. One concern per paragraph, so an "otherwise" never reaches back past its condition; a blank line between paragraphs; a list for parallel items, numbered only where order matters. Layout adds markup, never instructions, so it does not count against concision. Readability never justifies keeping text the one test cuts.
- **Plain sentences.** One instruction per sentence, the actor and the action named, in common words. A sentence that carries no instruction, fact, or reason is filler: cut it, along with mannered turns – an aphorism, a clause restating the one before, a contrast written for rhythm. Shorten by selecting what to say, never by packing clauses: a paragraph that chains its sentences with dashes keeps every instruction and buries them.
- **Long inputs first, the question last.** Anthropic's best-practices page puts the gain at up to 30% on multi-document inputs.
- **Each instruction once per loaded path**, then a conflict audit across everything that loads together.
- **Leading words.** Name a load-bearing rule with a term that already carries weight, in place of its explanation, and reuse it verbatim.
- **Gates over steps**: what must be true to advance, not what to do.
- **Dispatch, never the subagent's procedure**: name the skill and its arguments, say "subagent", and have it return a distilled summary, not a transcript.
- **Give the reason with the request** in long-running work: "I'm working on [the larger task] for [who it's for]. They need [what the output enables]. With that in mind: [request]."

## Prove it

Start on the most capable model the file will meet, baseline it unaided, write the minimum text that fixes the observed failures, and keep the cases. Removal is a hypothesis: cut a block and re-run. A pass over an existing file lists its contracts before the first edit and accounts for each one after – kept, moved, or cut with the behaviour's new source named – and doubt reverts the edit, because a lost contract costs more than the text saved. Then test on every other tier the file will meet. Assertion is not compliance – agents report adherence they did not perform – so gates and verifiable artifacts carry what matters. Re-audit every prompt-like file at each model release; a date stamp is not a trigger.

## References

- Anthropic, prompt audit guide and model migration guide – bundled with the Claude Code `claude-api` skill (`shared/prompt-audit.md`, `shared/model-migration.md`)
- Anthropic, Claude prompting best practices – https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Anthropic, Effective context engineering for AI agents – https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- OpenAI, Using GPT-6 Astra and the GPT-5.6 guide – https://developers.openai.com/api/docs/guides/latest-model
- Evidence: IFScale, arXiv:2507.11538; Instruction Stacking Collapse, arXiv:2608.02639; Instruction Adherence in Coding Agent Configuration Files, arXiv:2605.10039; ETH SRI, Evaluating AGENTS.md (2026); Revisiting Chain-of-Thought Prompting, arXiv:2506.14641; The Few-shot Dilemma, arXiv:2509.13196; Prompting Science Report 3, arXiv:2508.00614
