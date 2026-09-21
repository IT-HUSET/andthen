# Claude-Specific Prompt Engineering Guidelines

What changes when the reader is a current Claude model – Claude Fable 5.1, Fable 5, Opus 5, Sonnet 5 – and the host is Claude Code. Read `PROMPT-ENGINEERING-GUIDELINES.md` first; this file adds only what is specific to these models. Thinking, effort, and model choice belong to the harness and the role definitions: `docs/MODEL-EFFORT-SELECTION-GUIDE.md`. API mechanics are Anthropic's migration guide's.

## The host already states the generation's rules

Claude Code's system prompt, as observed in version 2.1.272, carries the migration guide's own snippets: the autonomous-operation block and its end-of-turn check, the scope-holding block, the progress-claim audit, the progress-update line, the conditional-formatting rule, the tool-call batching nudge, the "only you see that command's output" note. Nothing documents this, so check the host prompt in the version you run before a skill restates any of them.

## Behaviour that changes what you write

- **No silent generalization** (Opus 4.7, Sonnet 5, Opus 5). A rule is applied exactly as scoped: "apply this formatting to every section, not just the first one". A review prompt that says "report only high-severity findings" is followed literally and depresses measured recall; ask for everything with a confidence and a severity, and filter downstream.
- **Over-planning on ambiguous tasks** at higher effort. The tested line: "When you have enough information to act, act. Do not re-derive facts already established in the conversation, re-litigate a decision the user has already made, or narrate options you will not pursue in user-facing messages. If you are weighing a choice, give a recommendation, not an exhaustive survey. This does not apply to thinking blocks." The other lever is effort, never more procedure.
- **Under-narration and under-formatting** (Fable 5.1). Fewer user-facing updates during long tool chains, less bold, fewer headers and lists. Text written against chatty, bullet-heavy models now strips output the reader wanted; remove it before adding anything.
- **Elaboration when unsteered.** Structured summaries, sections on alternatives not chosen, comments narrating the next line. One communication-style paragraph beats enumerating the behaviours: "Lead with the outcome… The way to keep output short is to be selective about what you include, not to compress the writing into fragments, abbreviations, arrow chains, or jargon." On Opus 5, length is prompt-tuned, not effort-tuned: "Keep responses focused, brief, and concise" cut it by about a fifth.
- **Adjacent actions and extras.** Unrequested-but-adjacent actions, fixes to nearby code, scratch checks committed as permanent tests. State boundaries: what not to touch, where scratch scripts live, when tests are wanted. The migration guide's scope-and-test-coverage block is the tested wording; its short form is "keep verification scripts outside the repository and delete any you did add".
- **Whole-file rewrites** (Fable 5.1) where a targeted edit would do. One sentence restores surgical edits: "when it will not affect the end result, try to surgically edit a file rather than rewrite the entire thing."
- **Dense prose late in long sessions** – arrow chains, invented labels, working shorthand. The readability addendum (outcome first, complete sentences, no shorthand, each identifier explained in its own clause) fixes the final summary; "Please remove all mannered prose." fixes the register.
- **Answers from memory at low effort** (Fable 5.1) for names it recognises. Tell it that recognising a name is not knowing its current state, and to search the name as the user wrote it.
- **Context anxiety** when a remaining-token count is visible. Never surface budget countdowns.
- **Reasoning reproduction can trigger a refusal** (Fable 5.1). Never ask it to show its thinking.

## Guidance that flips between models

A mitigation written for one model is often wrong for the next; name the model it patches and re-audit at each release.

- **Verification.** On Opus 5, "double-check your answer", "include a final verification step for virtually any non-trivial task", "use a subagent to verify" is a delete, not a rewrite – removal reduced over-verification with no capability regression. On Fable 5.1 an existing test-before-reporting instruction is kept; the guide marks this tentative.
- **Delegation.** Opus 4.6 over-spawned, 4.8 under-reached, Opus 5 over-delegates and takes a cap, Fable 5.1 delegates reliably and asynchronously and finishes sooner when the lead is not forced to wait.
- **Narration.** The 4.6 family skipped the summary after tool use and took "provide a brief summary of what you did"; 4.8 and Opus 5 over-narrate; Fable 5.1 under-narrates.

## What a Claude skill still states

For long builds, a fresh-context verifier subagent on a cadence – it outperforms self-critique – and a place with a format to write lessons; Fable 5.1 does notably better with one. Everything else a skill states is in the general guidelines.

## References

- Anthropic, model migration guide – "Migrating to Claude Opus 5", "Migrating to Claude Fable 5.1" and "…from Claude Fable 5": the behavioural shifts and long-running agent recommendations; bundled with the Claude Code `claude-api` skill as `shared/model-migration.md`
- Anthropic, prompt audit guide – the dated-pattern groups and the keep list; bundled as `shared/prompt-audit.md`
- Anthropic, Claude prompting best practices – https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
