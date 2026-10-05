# Skill-Authoring Guidelines

How to write a prompt-like file – a skill bundle, a reference, an agent definition, an instruction file, an output style – for the current frontier models (Claude Fable 5.1, Fable 5, Opus 5, Sonnet 5; GPT-6 Astra, GPT-5.6) at the smallest context cost. Model and effort choice is `docs/MODEL-EFFORT-SELECTION-GUIDE.md`'s.

## The one test

Before you write a line, and again when you review one, ask: **would the reading agent do the right thing without it?** Right means an outcome that serves the file's purpose, not the steps you would take. If it would, the line is not written, and an existing one is cut. When unsure, assume it would, unless the failure would be destructive or silent.

The agent cannot get right what only the author knows, so keep it: the product and audience, environment facts, the quality bar, contracts and their mechanics, the hard judgment calls, and the reason behind a rule that runs against the model's default. That is context, and context is never cruft. Cut restated defaults, behaviour the model shows unprompted (planning, thoroughness, tool use, testing, reading docs, where to look in a repository, telling a pre-existing failure from a regression), and workarounds for failures current models no longer have. Justify a cut by the pattern it removes, never by its length.

Length buys no compliance, and restating the repository's own docs lowers task success. Conflicting instructions collapse compliance, make Astra pause, and make Claude spend effort reconciling them. Past roughly 150–200 live instructions on the loaded path, adherence drops and earlier instructions win.

### What no longer belongs

Each was written for models that needed it, and is neutral at best on current ones.

- **Pressure language** – MUST, NEVER, CRITICAL over-apply and set an anxious register. A hedge ("try to", "if possible") on a real requirement reads as permission to skip it. Emphasis is a tested fix for one underweighted instruction, never a register.
- **Thinking scaffolds** – "think step by step", "plan first", "be thorough" cause over-planning; depth is an effort setting. Never ask a model to show its reasoning, which Fable 5.1 can refuse.
- **Step choreography for judgment work** – micro-steps where the model's own plan does better. Spell out a sequence only for a narrow bridge where one alone is safe: destructive commands, migrations, auth.
- **Prohibitions without provenance** – a "never" against a failure the model would not make anchors it toward that failure. Keep one that encodes a real constraint or a reproduced failure, with its reason, and rewrite the rest as the wanted behaviour plus a check.
- **Anchoring examples** – the model copies an example's length, tone, and structure. Use examples only to pin a format-sensitive output shape: several, varied, labelled illustrative.
- **Numeric output shaping** – word caps, "at most five bullets", "be concise". State the audience and the outcome.
- **Fossils** – retired-model workarounds, rules nothing enforces, reminders on a cadence.
- **Update suppressors** – "hold findings for the end", "don't narrate", "never use bullets". Current models under-narrate with them present.
- **Ask-first reflexes** – "confirm before", "ask if unsure", "stop for review" make Claude, and Astra most, pause on safe actions and stop early. Define done, and reserve confirmation for destructive, irreversible, external, or scope-expanding acts.
- **Verification nagging** – "run the tests", "double-check", "read the docs first". Verification the model cannot give itself stays, as a dispatch: a fresh-context reviewer beats self-critique, on a cadence in long builds.
- **Rules the host states** – the Claude Code and Codex system prompts carry autonomy, scope, progress, and formatting rules. A repeat wastes tokens, and a contradiction fights the harness.
- **Grader vocabulary and strategy coaching** – "you will be graded on", "it's usually best to".

## Writing

- **Altitude** – state the outcome, the constraints, and how success is verified.
- **A reason in one clause**, only where the rule runs against the model's default, because there a bare rule is followed rigidly or rationalised away.
- **Scope stated** – current models apply a rule exactly as scoped. "Report only high-severity findings" loses recall, so ask for every finding with a severity and filter downstream.
- **Leading words** – name a load-bearing rule with a term that already carries pretraining weight (*Chesterton's Fence*, *Stop-the-Line*, *Boy Scout rule*), in place of its explanation, and reuse it verbatim everywhere. Keep only what the project adds to its common meaning, settled by asking the cheapest model cold. Coin a term only where plain words fail, and keep one term per concept.
- **Gates over steps** – a phase ends on an observable that shows it done ("every modified model accounted for"), and a gate restating its step is cut. Visible later phases pull toward premature completion. Sharpen the current gate first, and hide later phases behind a fresh subagent only when runs show rushing.
- **Dispatch sites** – a delegating step names the skill the subagent invokes, fresh or in-session context, the values it cannot derive as that skill's arguments, and the return shape the caller parses. It names the target in words and passes only switches such as `--fix`, `--quick`, and `--auto` as flags, never a mode or lens the invoked skill resolves from its target. The loaded skill is the **Single Authority**, and a hand-rolled prompt is a second copy that drifts. GPT models delegate in parallel only when told to.
- **Prose for behaviour, lists for data** – a rule is one sentence with its reason. Data is what the model looks up – a token mapped to an action, a route by flag or host, a return shape – and takes a list, one key per item. A table cell is a phrase; `tests/test_table_legibility.py` fails one over 200 chars.
- **Plain sentences** – one condition and one action per sentence, in common words, imperative for instructions and descriptive for definitions. The actor is you unless the sentence names another. Split a sentence holding two or more of `:`, `;` and ` – `, unless it is a data line. Cut filler and mannered turns: an aphorism, a clause restating the one before, a contrast written for rhythm. Shorten by selecting, never by packing clauses.
- **Contrast only a named failure** – write "X, not Y" only where Y is behaviour a recorded run produced.
- **One concern per paragraph**, so an "otherwise" never reaches back past its condition. Layout adds markup, never instructions, so it does not count against concision.
- **Bind shared names once**, in a line such as "`Learnings` and `Tech Debt` are Project Document Index entries", then use the bare names.
- **Tested vendor wording** (the Astra guide's autonomy, approve-last, and anti-slop snippets) is reused verbatim, in an instruction file or output style and never in a skill.
- **A mitigation names the model it patches**, so the next release can remove it. Re-audit prompt-like files at each model release.

## Skills

A skill is a folder – `SKILL.md` plus optional references and scripts – that an agent discovers by its description and loads on demand.

| Item | Loads | Limit |
|---|---|---|
| `name`, `description` | Every turn, every installed skill | Name 1–64 chars, lowercase, hyphens, matching the directory; description 1,024 chars |
| All descriptions | Every turn | Codex: 2% of the window, or 8,000 chars when unknown |
| Body | On trigger, then stays | Under 500 lines, under 5k tokens |
| References, scripts | On explicit read or run | One level deep; a table of contents past 100 lines |
| Instruction files | Every turn | Codex `AGENTS.md` chain 32 KiB; `CLAUDE.md` under 200 lines |

The body loads once and is never re-read, so a rule for the whole run is a standing instruction. Compaction keeps each re-attached skill's first 5,000 tokens, 25,000 across all, so what must survive a long run goes early. A step that must happen is a hook's job, because a skill is probabilistic.

### Frontmatter

- Codex reads `agents/openai.yaml` beside the skill, and the `/command` name comes from the directory.
- `model`, `effort`, `disable-model-invocation`, and `user-invocable` stay out of shipped skills: roles and the session steer models, and every skill serves users and subagents alike (`docs/DECISIONS.md`).
- `context: fork` runs the body as a fresh subagent without the conversation, only for an actionable task, paired with `agent`.
- `allowed-tools` pre-approves and does not sandbox.

### Description – the trigger surface

The only text seen before the skill fires, loaded every turn. Codex trims descriptions from the end, then drops skills, once the shared budget overflows, and `tests/test_surface_budget.py` caps each shipped one at 400 chars.

- What it does, then when, in the users' words, the load-bearing trigger first.
- No first or second person ("I can help…", "You can use this…"), because the description joins the system prompt and a shifting point of view hurts discovery.
- One boundary clause where a neighbour is easily confused.
- Calibrated urgency belongs here and nowhere else, because skills under-trigger. No procedure or option menu.
- Name a category of intent; a phrase per missed trigger generalises worse.
- Brevity cuts steering and examples, never contract: what it does, when, and its inputs. Under-description is the common failure, here and in agent and tool descriptions.
- The body explains each term the description uses. `argument-hint` names every input the body accepts and nothing else, and the Codex default prompt agrees with both.

### The body

**The prompt handles the edge case.** A skill covers the path most runs take. An edge case the user can steer with a line of input gets no text: revising the skill's own output, a narrower scope, another destination, a non-default choice. Every branch is read on every run and invites the model to take it where it does not apply, and the Cookbook carries the user's recipe instead. A destructive or silent failure is the exception, and gets a one-sentence guard.

**Text allowance by aspect.** Every line serves one aspect, and text past its aspect's allowance is cut, however true. A line the one test removes is unprompted behaviour, even where it reads as a guard or a rubric item. It goes whole, because a one-line version still gives the instruction.

| Aspect | Allowance |
|---|---|
| Purpose | 1–3 sentences opening the body |
| Input | One sentence placing `$ARGUMENTS`; a line per flag, and per input shape only where it loads a different file |
| Main flow | One short step per phase: what it achieves, and the gate that shows it done |
| Common variation | One sentence, at the step it changes |
| Guard against a destructive or silent failure | One sentence, at the step it guards |
| Edge case the user can prompt: rare input, re-entry, recovery, legacy state | None |
| Parsed contract | Exact and once, in a template or data list |
| Project fact the model cannot know | One line |
| Reason for a rule | One clause, only where the rule runs against the model's default |
| What the model does unprompted | None |
| Another skill's or file's behaviour | A mention, never a restatement |
| One host's quirk | None; a Learning, unless a one-line fix is proven on that host |

- **Common** means most runs, or an input users type often. A case whose only evidence is one eval cell is rare.
- **Parsed contract** means a token, shape, path, or line another skill, script, hook, or test reads, and a skill's description. In an instruction file it includes every rule other skills, hooks, or the user's own instructions rely on, and each index entry resolved by name. In an agent definition it includes the frontmatter and the tier contract the role carries.
- **Destructive** means lost or reverted work someone else made, or an irreversible action. **Silent** means no gate, test, or reviewer downstream would catch it.
- Input gets one sentence because nothing parses it: `$ARGUMENTS` is raw substitution, and `argument-hint` validates nothing.

**Skeleton.** Every body uses these sections in run order, leaving out any it does not need, and a reference uses the same headings for the part it continues.

| Section | Holds |
|---|---|
| Opening lines | Purpose |
| `## Input` | `$ARGUMENTS` and the flags |
| `## Rules` | Standing rules for the whole run, a few lines |
| `## Workflow` | Numbered steps in run order, each ending on its gate; a branch loads its reference at the step |
| `## Output` | What is written where, and the shapes other files parse |
| `## Follow-up` | The one next command |

**Flow.**

- One condition per branch point, read off the input or an artifact. Nested branches are two flows, and the second is a reference or another skill.
- One case, one rule: where two rules can apply to one case with different outcomes, rewrite until one does.
- One home per fact, and every other mention points at it.
- Only `--auto` stops a skill asking what its text says to ask (`docs/DECISIONS.md`), and only then does it read `plugin/references/unattended-runs.md`. A skill whose interview is the deliverable takes no `--auto`.

### Scripts and references

Script source never enters context, only its output. Deterministic work goes to a script, and the body says whether to run or read it. Name MCP tools `Server:tool`.

**The file rule.** Text every run needs goes in the body. Text only some runs need moves to a reference once it passes a few paragraphs, loaded behind a condition decided without judgment: a flag, a mode, a host. A reference holds such a branch or a rubric (lens, calibration, schema, contract), never a procedure handed to a subagent. A dispatched run is its own run, so `exec-plan` routes a FIS to `references/story.md` rather than its orchestrating body. A shared canonical stays in `plugin/references/` wherever it loads. Once the file rule holds, a large per-path load is no reason to split further.

**Loading a reference.** A reference loads where its path appears in `SKILL.md`, relative to the skill root. The skill's own file is `references/<name>.md`, and a canonical is `../../references/<name>.md`. The link form is the one `docs/ARCHITECTURE.md` § Reference Syntax in Skill Prompts fixes.

- Link each file once, where the run loads it, in a list with one line per condition. A mode table's cells and a flag's argument line serve as that list. A link threaded through a sentence hides the load.
- A reference continues the body's step numbering, or cites no step outside itself.
- A later mention is the bare backticked filename or a declared alias, and loads nothing. Mention only a file the same body loads, or another skill's file as a fact. A model opens any name it can resolve, so `install-skills.sh --validate-only` fails on a bare name of an unloaded file under `references/`.
- Only `SKILL.md` links or paths to another file, and every other file only mentions, code fences included. Chained loads get partial reads.

## Changing a skill

Most changes are a few lines in an existing file, and most bloat arrives that way.

- **Rework, don't accrete.** Rewrite the sentence or step the change touches, so the file reads as if the behaviour was always there and holds or shrinks its size. An appended clause or a sentence bolted on beside the old one leaves a seam.
- **An added sentence names its cause**: the run that went wrong without it, or the contract it carries (the **Product** document's Decision Rule). A review finding about a rare path names neither, so a fix pass adds text for it only as a one-sentence guard against a destructive or silent failure.
- **A rule several skills need** is one sentence built on its leading word, identical in each, plus only that skill's own exception. Search the shipped surface for the concept before writing it, because a paraphrase drifts from its siblings on the first edit.
- **Preserve behaviour the request does not change**, and keep cleanup inside the files the change touches.
- **The shipped surface has one word budget** (`tests/surface-budget.json`, ADR-018): a round ceiling a few percent above the count, so an ordinary fix fits under it. Growth past it cuts elsewhere or raises it in the same commit to a new round number with that headroom, as one reviewed line.

## Pruning and review

The allowance is the test, for old text as for new.

### Conflict audit

Read the target with everything that loads beside it – its references, the project instruction file, the host prompt – and resolve every pair pulling different ways first. No cut repairs a conflict.

### Failure modes

Measure against what one load pays for, since a link pulls its whole target into every consumer.

- **Duplication** – one meaning stated twice. On one loaded path it costs every load, and across skills a paraphrase drifts from its siblings.
- **Sediment** – seams of add-only edits: bolted-on sentences, doubled altitude, contradictions, history phrasing ("now", "no longer", "instead of", a diff against text the model never saw).
- **Sprawl** – text in the wrong file by the file rule.
- **No-op** – what the model does unprompted or the host already says, the catalogue above, filler, usage blocks, description restatement. Settle a dispute by running the skill, because No-op status is model-relative.

### Branch ledger

List every branch and aspect in scope with the verdict its allowance sets: keep, one line, move, or cut. Then count the live instructions left on the loaded path against the 150–200 threshold.

- An edge case the user can prompt is cut, however well tested. A test or rubric grading a sentence is no reason to keep it, and the eval of a cut branch changes or retires in the same commit.
- Doubt about a rare case cuts it. A failure on a common path brings it back as one sentence.
- A cut names its keeper: where the behaviour still comes from on the loaded path, such as a kept row, a loaded reference, the host prompt, or the model's own default. A keeper is text the running agent will have loaded, so a dispatched skill's body, an unshipped note, a project document, or a README is none. A cut without a keeper is a decision, named in the commit message.
- A move goes to the file that already owns the fact, loaded before the first step that needs it on every invocation that reached it. A gate moves only with its whole step, and a fail-fast check stays in the body, because position is part of their contract.
- Packing is not a cut: a list collapsed into a paragraph keeps every instruction, harder to find. A reshape that pulls data out of prose or splits a packed sentence is a fix, and its markup does not count against the size.

### Proof

Author evaluation-driven: baseline the most capable model the file meets, write the minimum text that fixes the observed failures, keep the cases, then test the other tiers. Agents report adherence they did not perform, so gates and verifiable artifacts carry what matters, and proof is a test or a case under `evals/cases/`.

Rewrite from intent, never compress: write the purpose and main flow on a blank page, then add back what the ledger keeps, because compressing keeps the branches. A rewrite proves no regression three ways:

- Before the first edit, the eval cases run several times in parallel on Claude, and the smoke tier on Codex, as the baseline. One run proves nothing, because evals are intermittent.
- Parsed contracts stay byte-exact, checked by a command diff of code spans, because reading misses omissions.
- A fresh-context reviewer finds each kept ledger row in the rewrite, and the re-run evals match or beat the baseline, or the change reverts.

The `skill-review` skill's `--fix` runs this.

## Repository constraints

A reference in `plugin/references/` needs two consuming skills, and with one it moves into that skill.

## References

- Skills: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices, https://agentskills.io/specification, https://code.claude.com/docs/en/skills, https://developers.openai.com/codex/skills, https://developers.openai.com/codex/guides/agents-md
- Prompting: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices, the migration and prompt-audit guides bundled with the Claude Code `claude-api` skill, and https://developers.openai.com/api/docs/guides/latest-model (Astra, with the tested snippets)
- Evidence: IFScale, arXiv:2507.11538; Instruction Stacking Collapse, arXiv:2608.02639; Instruction Adherence in Coding Agent Configuration Files, arXiv:2605.10039; ETH SRI, Evaluating AGENTS.md (2026); The Few-shot Dilemma, arXiv:2509.13196
