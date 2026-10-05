---
description: Review a skill bundle, a prompt-like file (`AGENTS.md`, a guideline, an agent definition), or a change to them for conflicts, text past its allowance, and dropped parsed contracts, returning findings, a branch ledger, and a ship-ready verdict; `--fix` rewrites from the ledger. Trigger on 'review this skill change', 'is this AGENTS.md lean', 'tighten this prompt'.
argument-hint: "[--fix] [--output-dir <path>] <skill directory, prompt-like file, or a change to them>"
---

# Skill Review

Reviews what a prompt's text makes the model do and what it costs. Frontmatter validity is the host validator's job.

## Input

`$ARGUMENTS` minus flags, and the request around it, name the scope: a skill bundle, one or more prompt-like files (an instruction file, a guideline, an agent definition, an output style, a task-start document), or a change to them, such as a diff, a commit range, or the working tree's edits. Read the working tree as it stands, because that is what the next commit ships.

- `--fix` rewrites the scope from the branch ledger, and a direct imperative in the request ("tighten", "rewrite") counts as `--fix`. Only it edits. After the review, read [`fix.md`](references/fix.md) and follow it.
- `--output-dir <path>` writes the report there as `skill-review-<stem>.md`, or `skill-review-<stem>-fix.md` under `--fix`. Without it the report prints inline.

## Rules

- Read [`SKILL-AUTHORING-GUIDELINES.md`](../../../docs/SKILL-AUTHORING-GUIDELINES.md) (the guideline) whole before the review. It is the rubric, and every finding cites its rule.
- The loaded path is the files one load pays for: a bundle's `SKILL.md`, every reference it names, and `agents/openai.yaml`, or a file plus what it pulls in on the same turn.
- Findings and the ledger cover the scope, judged in its loaded path. For a change, the scope is the changed text.
- `../../../plugin/references/review-calibration.md` owns the Anti-Leniency Protocol, Scope Discipline, the Structured Finding Contract, and the Findings Filter, so a remediation reader parses this report like any other. The Critic posture in `../../../plugin/references/lens-adversarial.md` is the finding pass.
- Collect the Project Rules Context per `../../../plugin/references/intent-and-rules-context.md`, including the surfaces a parsed contract's reader lives in: README sections, tests, eval cases, Key Dev Commands.
- The size ledger is `wc -c` per loaded file, their sum, and how often that text loads: a skill when it fires, an instruction file or guideline every turn, an agent definition every spawn, a task-start document nearly every run. It is the only size claim, so "too long" without its numbers is no finding.
- A task-start document (`LEARNINGS.md`, `DECISIONS.md`) is data. Review it for Duplication, Sediment, and each entry's truth against the code and the current skills.

## Review

1. **Conflict audit** across the loaded path, the project instruction file, and the host prompt.
2. **Critic pass.** Attack the scope against the guideline. Search the shipped surface and the project's docs for each rule the scope states, because a paraphrase of a rule stated elsewhere is Duplication however well each copy reads. Each finding names the span (file and line), the guideline rule it fails, and what the model does differently because of it.
3. **Branch ledger.** One row per branch and aspect in scope: the span, its aspect, its skeleton section on a bundle, and the verdict its allowance sets. A cut row carries the characters it frees and its keeper, or `decision`. The ledger is the rewrite's plan, and a row becomes a finding only where a change adds text past its allowance. A ledger without a cut on a body written before the current model generation is the reviewer under-firing, so re-walk it before reporting `Ready`.
4. **Leading-word probe.** Probe every cut to a leading word in one spawn: a subagent with no tools and none of the target's text (the installed `worker` role agent when available, else a generic inherited subagent) returns per term `recognised: yes | partly | no` and the behaviour the term implies. A recognised term replaces the span, keeping what the project adds beyond the probe's answer; otherwise the span stays. A term the installed skills' descriptions name is in every subagent's context, so it cannot be probed cold and keeps its definition.
5. **Filter.** Run the Findings Filter as Devil's Advocate over the scope: does the span fail the rule, does the model do worse because of it, and is the severity the one below? Report the `Filter summary` line and each withdrawal's falsifier.

Severity:

- CRITICAL – an instruction conflict, or a parsed contract dropped, broken, or contradicted: a dispatch naming a skill or argument that does not exist, a parsed token misspelt.
- HIGH – text a change adds past its allowance, a trigger-surface defect, a phase without a gate, a procedure at a dispatch site.
- MEDIUM – a rule paraphrased across files, a rule against the model's default without its reason, an anchoring example, data in running prose, a task-start document entry no longer true.
- LOW – a paragraph carrying several concerns, a packed sentence, a leading word not reused, a missing table of contents, an unqualified tool name.

The readiness line is `Blocked` on any CRITICAL, else `Needs Fixes` on any HIGH or three or more MEDIUM, else `Ready`. It names the host validator the target still has to pass (`claude plugin validate` inside a Claude Code plugin, the loose-skill installer when the project ships one) or says none applies.

**Gate**: every loaded file is in the size ledger, the conflict audit has a result, every branch and aspect in scope has its row, every leading-word cut carries its probe result, and every surviving finding carries `Class:` and `Routing:`. A change to a parsed contract, or a move that changes a registration, routes `Note` with its fix written as `SURFACED: <what> – <what would resolve it>`.

## Output

Verdict first, per the calibration: the readiness line, the size ledger with the characters the cuts free, the conflict audit, the findings in the contract's shape, the branch ledger, the `Filter summary`, and `Critic Coverage`. Under `--fix`, add every item of the gate in `fix.md`.
