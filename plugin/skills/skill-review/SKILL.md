---
description: Review one skill bundle or prompt-like file (`AGENTS.md`, a guideline, an agent definition) against skill craft – instruction conflicts, dropped contracts, spans the model already knows – returning findings, a cut list, and a ship-ready verdict; `--fix` compresses it in place with zero contract loss. Trigger on 'review this skill', 'is this AGENTS.md lean', 'tighten this prompt'.
argument-hint: "[--fix] [--output-dir <path>] <skill directory, paths inside one, or one prompt-like file>"
---

# Skill Review

Reviews what a prompt's text makes the model do and what it costs, against `references/skill-craft-rubric.md`. Frontmatter validity and layout are the host validator's job, usage statistics nobody's here; the audience is any prompt author on Claude Code or Codex.

`$ARGUMENTS` minus flags is one target: a skill bundle – a directory holding `SKILL.md`, or paths inside it – or one prompt-like file, meaning a project instruction file (`AGENTS.md`, `CLAUDE.md`), a guideline, an agent or role definition, an output style, or a document skills read whole at task start (`LEARNINGS.md`, `DECISIONS.md`). It is read from the working tree as it stands, uncommitted edits included, because that is the text the next commit ships; several targets are several runs, because the findings and the size ledger are per target. `--fix` applies the Fix-routed findings and the cut list, and a direct imperative in the request ("tighten", "compress") is `--fix`. `--output-dir` writes the report as a file there; without it the findings and verdict print inline. Only `--fix` edits the target.

## Rules

- The loaded path is the unit under review – the files one load pays for: a bundle's `SKILL.md`, every reference it names, and `agents/openai.yaml`; a file target plus whatever it pulls in on the same turn, an `@import` or a Project Document Index entry read at task start. Sprawl and Duplication measure against that real cost.
- `../../references/review-calibration.md` owns the Anti-Leniency Protocol, Scope Discipline, the Structured Finding Contract, and the Findings Filter; the Critic posture in `../../references/lens-adversarial.md` is the finding pass. The `Fix` bar is the contract's – nothing here redefines a field or a severity, so a remediation reader parses this report like any other.
- Collect the Project Rules Context per `../../references/intent-and-rules-context.md`: the project instructions, its guideline files, and the documented surfaces the target's contracts live in – its README section, its tests, its eval cases, Key Dev Commands. That bundle is where a span's contract is looked up; Intent Context is the target's own documented purpose when the project states one.
- The size ledger is `wc -c` per loaded file and their sum, carried with the rubric's multiplier – what loads this text, and how often. The cut list's total delta counts against that sum, and the ledger is the only size claim: "too long" without the numbers is not a finding.

## Review

Two passes over the loaded path, after the ledger, the context, and the rubric's conflict audit. A reviewer running only the Critic pass reports a 20k-char body as clean.

The Critic pass attacks the text for defects – conflicts, dropped contracts, a bundle's trigger surface, gates, dispatch sites, and on a data target each entry's truth against the code and the current skills, the loaded path widening to those subjects – and every finding names the span (file and line), the rubric item it fails, and what the model does differently because of it.

The compression pass walks every span with the rubric's one test, burden on the span, and produces the cut list: each cut `old → new` (or DELETE), its delta, and its keeper – where the behaviour still comes from. Cuts to a leading word are probed before they are listed, every term in one spawn: a subagent with no tools and none of the target's text – the installed `worker` role agent when available, else a generic inherited subagent, which shows only that the term is known unprimed – returns per term `recognised: yes | partly | no` and the behaviour the term implies, and the rubric's Cuts section reads the result.

Before routing, run the Findings Filter over the findings as Devil's Advocate, the loaded path its scope and the rubric's severities its calibration. Its questions per finding:

- Does the span really fail the item?
- Does the model do something different, and worse, because of it?
- Is the severity the rubric's?

Report the `Filter summary` line and each withdrawal's falsifier; the per-finding records stay in your notes.

**Gate**: every loaded file is in the ledger, the conflict audit has a result (findings or none), every span of the loaded path was either kept with its reason class or is on the cut list, every leading-word cut carries its probe result, every surviving finding carries `Class:` and `Routing:`, and the readiness line names the validators the target still has to pass – named, not run, on a review. A contract change routes `Note`, and so does a split that changes a registration; never `Fix`. Their suggested fix is written as `SURFACED: <what> – <what would resolve it>`, so a reader can pick them out.

An empty cut list on a body written before the current model generation is the reviewer under-firing, not the target being lean; re-walk it with the rubric's catalogue span by span before reporting `Ready`.

## Fix

With `--fix`, before the first edit copy the target into the project's agent temp directory, or the session's when the project names none – never inside the target. The copy and the edits cover the target alone: a shared file it loads by path stays in the ledger, read-only, unless it is itself the target passed. Uncommitted text no commit can restore is why the copy exists.

Then take the rubric's contract inventory from the copy – every contract in the text, not a sample, because a sampled inventory clears spans it never read.

Apply every `Fix`-routed finding and the whole cut list as one pass, smallest coherent change per span, from the one agent holding the whole picture – parallel writers re-expand each other's cuts. A split changes a registration when it adds, removes, or renames a file the project's packaging, manifests, or instruction files enumerate for the skill – an asset list, a manifest entry, a Project Document Index entry, an `@import`, a frontmatter `name` – and is applied only when the request approves it. Net non-increase on the ledger's sum, with three exceptions, each justified on the ledger: a flagged correctness fix (a now-misleading instruction clarified), a split's heading and load sentence, and a reshape's markup – no sentence a reshape adds carries an instruction. A split is ledgered per consuming path.

Then clear the edit against the rubric's Cuts section, in this order:

1. Run the rubric's mechanical set diff of the copy against the edited target, by command. An absence that no cut-list entry or named reshape answers is a lost item.
2. You cannot clear your own cuts, so the inventory is resolved in fresh context. Spawn a fresh reviewer subagent – the installed `reviewer` role agent when available, else a generic inherited subagent; never pin model or effort in a prompt – and hand it the rubric's Cuts section (`references/skill-craft-rubric.md`), the copy, the edited target, and the cut list: not this skill, which would put it on a second review, and not your inventory, which would anchor it to yours. It builds its own inventory from the copy and returns one resolution per item – kept, moved, absent with its keeper, lost, or doubtful. Where no subagent can be spawned, resolve your own inventory against the diff and say the assurance is weaker.
3. A lost or doubtful item reverts the narrowest edit that touched it, byte-exact from the copy, and no narrower re-cut replaces it in the same run.
4. Run the validators the readiness line named, the project's fast tier when Key Dev Commands names one, and the target's own proof – its test or eval case – when one exists, asking first when it is a live eval run.

**Gate**: the copy's path, and your inventory taken from it before the first edit; the mechanical check's command and its result – absences or none, each answered or reverted; every item on either inventory – yours and the reviewer's – kept, moved, or cut, and none lost; ledger before and after; the validators, the fast tier, and the target's proof green or absent by name. One pass, no loop.

## Output

Verdict first, as the calibration orders it: the readiness line, then the ledger with the cut list's total delta, the conflict audit, the findings in the contract's shape (`SURFACED:` inside the Note-routed ones), the cut list, the `Filter summary`, and `Critic Coverage`. Under `--fix`, also every item of the Fix gate. Under `--output-dir`, the same content as `skill-review-<target's directory or file stem>.md` in that directory – `skill-review-<stem>-fix.md` under `--fix`, so a tighten never overwrites the review-only report beside it.
