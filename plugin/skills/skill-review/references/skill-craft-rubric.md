# Skill Craft Rubric

What a skill bundle or a single prompt-like file is reviewed and compressed against, over the loaded path. The multiplier prices what the text costs, because the same cut is worth very different amounts:

- a skill – when it fires;
- an instruction file or guideline – every turn of every session;
- an agent definition – every spawn of that role;
- a document skills read at task start – nearly every run.

The ledger therefore names what loads the text and how often. Written for the current frontier generation: prompts written for prior models are too prescriptive for it and lower output quality, and length buys no compliance.

## Contract – what a span may not lose

A contract is any behaviour an agent or a parser depends on: exact tokens and grammars (`ASSUMPTION:`, a verdict block, a field set), cross-skill routes and the arguments a dispatch passes, the paths a body loads by name, named failure modes, the flags, modes, and edge cases the project's documentation states, a bundle's trigger surface, and what the project's tests or eval cases assert about the text. On a file target it is what the file's readers build on: for an instruction file or guideline, the rules other skills, hooks, and the user's own instructions rely on, plus the Project Document Index entries skills resolve by name; for an agent or role definition, its frontmatter – model, effort, tools – and the tier contract the role carries. A document skills read whole at task start (`LEARNINGS.md`, `DECISIONS.md`) is data rather than instruction: the No-op catalogue mostly does not apply, and the review is Duplication, Sediment, and whether each entry is still true against the code and the current skills. Markers that protect a span: an imperative lead verb, enumerated inputs, outputs, or modes, a counter-prior phrase ("preserving exact behaviour"), a verification commitment, a fail-fast gate at the top of the body – position is part of that contract. Changing what a documented behaviour means is a contract change, never a tighten.

## Conflict audit – first

Read the loaded path together with the project instruction file and the host's own prompt, which already states autonomy, scope, progress, and formatting rules. Every pair pulling in different directions is a finding, and no cut repairs one: conflicting instructions collapse compliance and make the model spend its effort reconciling wordings. A rule the host already states is a No-op below; a rule that contradicts it fights the harness – a conflict.

## The one test – every span, burden on the span

For every span: **could the model already know this?** Only these earn text – context only the author has (the audience and product, environment facts, the quality bar, contracts and their mechanics, the genuinely hard judgment calls, the reason behind a constraint), exact scripts for fragile operations where one sequence is safe, contract precision in a description (what it does, when and when not, each parameter), calibrated urgency in trigger text, one end-of-prompt recap of the few key constraints, and instruction precedence stated once in the project's instruction file. A span with none of these and no contract marker is cut; unsure means cut, because a wrong keep costs every invocation – but only with its keeper named. Context is never cruft – minimal does not mean short; the cut is restatement, not information.

What no longer belongs, each written for models that needed it and neutral at best on current ones:

- Pressure language – capitalised MUST, NEVER, CRITICAL over-apply and set an anxious register; hedges ("try to", "if possible") on real requirements read as permission to under-deliver. Say it once at normal volume.
- Thinking and planning scaffolds – "think step by step", "plan before acting", "be thorough": the model plans internally; these cause over-planning. Depth is an effort setting.
- Step choreography for judgment work – numbered steps where the model's own plan does better; keep them only where one sequence is safe.
- Prohibitions without provenance – a "never" against a failure the model would not make anchors it toward that failure. Keep the ones encoding a real constraint or a failure that reproduces on the target model, with the reason; rewrite the rest as the behaviour wanted plus a check.
- Example over-indexing – the model copies an example's length, tone, and structure. Zero-shot first; examples only where an output shape is format-sensitive, several and varied, labelled illustrative, never one gold output.
- Numeric output shaping – word caps, "at most five bullets", "summarise every N calls". State the audience and outcome instead.
- Fossils – retired-model workarounds, "now" / "no longer" / "instead of" phrasing (a diff against a prompt the model never saw), patch accretion of narrow conditionals, rules nothing enforces, a mitigation that does not name the model it patches, reminders on a cadence when a once-stated instruction persists.
- Update suppressors and anti-formatting rules – "hold findings for the end", "don't narrate", "never use bullets": the current generation under-narrates with them present.
- Ask-first and stop-for-review reflexes – "confirm before", "ask if unsure", "stop after the first implementation" produce approval pauses on safe actions. Define completion, name the safe local actions, reserve confirmation for destructive, irreversible, external, or scope-expanding acts.
- Verification and testing nagging – "run the tests", "double-check", "read the docs first": the model does these unprompted. Say when not to; verification it cannot do for itself (a fresh-context reviewer, a gate) is a dispatch, not a reminder.
- Rules the host already states, and restatements of the project's own documents – a repeat costs tokens, a contradiction fights the harness.
- Grader vocabulary and strategy coaching – "you will be graded on", "it's usually best to": the author's heuristic where the model's plan is better.

## How the kept text is shaped

- Altitude: outcome, constraints, and how success is verified; heuristics for open fields, exact commands for narrow bridges (migrations in sequence, destructive commands, auth flows).
- Why beside the rule, once – the reason is what the model generalises from; a bare rule is followed rigidly or rationalised past.
- Scope stated, not implied: the model applies a rule exactly as scoped.
- Positive behaviour plus a check where a "never" would go; a gate, script, or test enforces what prose only asks.
- Prose for behaviour, structure for data. A rule stays one sentence with its reason: bullets flatten priority and sever the two, and prompt format bleeds into output format. Data is what the model looks up rather than weighs: a token or condition mapped to an action, a choice between routes, a return shape. It takes a list, one item per key with its reason inline, even inside a behaviour section. In running prose the model has to rebuild the mapping, and a special case hides mid-sentence. A table cell is a phrase.
- Laid out for the maintainer too – the model executes the text, a person reviews and edits it, and a seam or a contradiction hides in a wall. One concern per paragraph, so an "otherwise" never reaches back past its condition; a blank line between paragraphs; a list for parallel items, numbered only where order matters. Layout adds markup, never instructions, and never justifies keeping a span the one test cuts.
- Plain sentences – one instruction per sentence, the actor and the action named, in common words. A sentence that carries no instruction, fact, or reason is filler and goes on the cut list, along with mannered turns: an aphorism, a clause restating the one before, a contrast written for rhythm.
- Long inputs first, the question last; each instruction once per loaded path; compliance degrades from roughly 150–200 live instructions across system prompt, instruction files, skill, and references, and earlier instructions win.
- Gates over steps – a phase ends on a falsifiable condition, not an action; visible later phases pull toward premature completion, so the current gate is sharpened first.
- Dispatch, never the subagent's procedure – name the skill and its arguments, say "subagent", have it return a distilled summary; the skill body loaded there is the Single Authority and a hand-rolled prompt is a second copy that drifts.
- Leading words – a load-bearing rule named with a term that already carries weight (Chesterton's Fence, Stop-the-Line), reused verbatim across description, body, and references; one term per concept. The term stands in for its explanation: a span paraphrasing a concept the model knows by name shrinks to the name plus what the project adds to it.
- Headless by default for execution skills – completion on recorded assumptions, a stop only on an unusable call; discovery and design skills are interactive by contract and say so.

A bundle's trigger surface, and only a bundle's: third person, what then when in the words users say, the load-bearing trigger first – Codex trims descriptions from the end and drops skills when the shared budget overflows – one boundary clause where a neighbour is easily confused, no option menu. Vague never fires; broad fires on unrelated work; one phrase per missed trigger generalises worse than a named intent. `argument-hint` names every input the body accepts and nothing it does not, and the body opens with one sentence placing `$ARGUMENTS` and stating only what the hint cannot; the Codex metadata's default prompt agrees with both. A term the description uses, the body explains.

References are rubrics – a lens, a calibration, a schema, a contract – never a procedure handed to a subagent, one level deep, loaded where a path to the file stands in `SKILL.md` with the moment stated – a bare filename is a mention, legal only for a file that body already loads – one file per domain so a task loads only its own, a table of contents above 100 lines; deterministic work goes to a script with run-or-read stated, its source never entering context; MCP tools qualified `Server:tool`. Proof exists: a test or eval case the target's claims can fail.

## The four prose failure modes

Measure against what one load pays for, never one file alone: a pointer pulls its whole target into every consumer, so a short rule copied into five skills can cost less than five links to one long reference.

- **Duplication** – one meaning stated twice on one loaded path, usually already drifting in wording. One statement per path; across skills, a fix must land in every copy. Working redundancy that still agrees is a refactoring preference; dedupe when the copies disagree or one is loaded where it is inert.
- **Sediment** – seams left by add-only edits: bolted-on sentences, doubled altitude, contradictions, history phrasing. Rework the section whole, describing only the current shape, as if the current rules were the only rules that ever existed.
- **Sprawl** – material only some invocations need, inline in a file every invocation loads. The cure is a split by consumer. A split into a bundle's own `references/` is a `Fix` when the load condition needs no judgment (a flag, a mode, a host), because nothing registers such a file. A split that changes a registration is surfaced.
- **No-op** – what the model does unprompted or the host already says, and filler: the catalogue above. Delete, or replace with the behaviour wanted plus a check. No-op status is model-relative: when contested, run the skill and observe, never debate.

## Cuts and functional preservation

A cut is `old → new` (or DELETE) with its delta and its **keeper**: where the behaviour still comes from after the cut – a contract marker elsewhere on the path, a reference already loaded, the host prompt, or the model's own default, named as which. A keeper on the path is text the agent running the target will have loaded – the target, the references it loads, the shared files it names by path; a dispatched skill's body, a note that does not ship, a project document, and a README are not keepers, because the agent reaches the cut span without them.

- A cut with no keeper is not a cut.
- A cut to a leading word (`span → term`) names the model's knowledge of the term as its keeper, and the reviewer's recall does not show it: the reviewer knows more than the cheapest model that runs the target. A cold probe does – what a model given the term and none of the target's text says an agent told "the term applies" will do, answering "no" rather than guessing. Recognised, the span minus the probe's answer is what the project adds, and stays. Partly or not, the whole span stays. A term the installed skills' descriptions name reaches every subagent's context, so it cannot be probed and keeps its definition.
- Packing is not a cut – a list collapsed into a paragraph, sentences chained with dashes: the delta is markup, and every instruction stays, harder to find.
- A reshape is a finding's fix – data moved out of running prose, a paragraph split by concern, a packed sentence made plain. The markup it adds is justified on the ledger, not counted against the cuts. A new list directly above another at the same indent merges with it when rendered, so every reshape is read rendered, not as source.
- A cut whose keeper is a documented behaviour changing meaning is a contract change: `SURFACED:`, never applied.

The preservation pass puts the burden on the edit, because no ledger gain pays for a lost contract: an edit stands only when every contract it touched is shown to survive, and doubt reverts it.

Survival is shown against a **contract inventory** taken from the pre-edit text: every item of the Contract section found on the loaded path, by file and line, plus every dispatch and what it carries, each calibration (a threshold, a default, a judgment call the text settles), and each rule with its reason. After the edit each item resolves one of three ways, and an item that resolves none of them is lost:

- **Kept** – on the post-edit path with the same meaning, by file and line.
- **Moved** – in a reference whose load site comes before the first step that needs the item, under a condition covering every path that needed it. Name every pre-edit invocation that reached the item and show the condition true on each; one uncovered invocation makes the item lost. A gate or fail-fast check stays in the body: position is part of its contract.
- **Cut** – on the cut list with its keeper.

Two checks resolve the inventory, because the editor re-reading its own edit misses what it omitted: a mechanical set diff of the pre-edit against the post-edit text, taken as sets of code spans, flags, paths, numbers, and named output strings, and a reviewer in fresh context building its own inventory from the pre-edit text and opening the cut list only to judge each absent item's keeper. An item only the reviewer lists is resolved like any other: the two inventories clear as their union.

Removal stays a hypothesis after both, until the target's own proof re-runs, where one exists. The size of lean text is whatever survives this; a remainder still too large for one trigger means moving content out of per-run context – a split by consumer, a deeper tier – not trimming harder.

## Severity and readiness

- CRITICAL – an instruction conflict, or a contract the text drops, breaks, or contradicts: a dispatch naming a skill or argument that does not exist, a parsed token misspelt.
- HIGH – a trigger-surface defect on a bundle, a phase without a gate, a procedure at a dispatch site.
- MEDIUM – a rule without its reason; an example that anchors; data in running prose (a mapping, a route choice, or a return shape the model has to rebuild); an entry of a data target no longer true against the code, because a stale trap misleads every run that reads it; a span the one test fails that the cut list cannot take because its keeper is unclear.
- LOW – a paragraph carrying several concerns, a sentence packing several instructions, a leading word not reused, a missing table of contents, an unqualified tool name.

The cut list is not a finding: it is the compression itself, reported with its total delta.

Readiness is one line: `Ready` with no CRITICAL or HIGH; `Needs Fixes` on any HIGH or three or more MEDIUM; `Blocked` on any CRITICAL. The line names the host validator the target still has to pass – `claude plugin validate` inside a Claude Code plugin, the project's loose-skill installer when it ships one – or says none is named.
