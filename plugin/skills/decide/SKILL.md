---
description: Technical decisions, made and recorded – interviews the user over the choices a technical solution needs, recommends each, deepens a contested one into a weighted trade-off, writes ADRs. Trigger on 'decide', 'write an ADR', 'trade-off', 'compare options', 'which approach'. Design advice and analysis of existing structure are the andthen:architecture skill.
argument-hint: "[--output-dir <path>] [--auto] <decision | technical area | PRD, plan, or report path>"
---

# Decide

Interview the user over the technical decisions a solution needs until each is made, then record it: an ADR, or a Still Current line in the `Decisions` document. A contested decision gets a weighted trade-off analysis before it is made.

## Input

`$ARGUMENTS` minus flags is `INPUT`, required: one decision, a technical area to settle, or a PRD, plan, or architecture report whose open forks need deciding.

- `--output-dir` sets `OUTPUT_DIR` for trade-off artifacts, which must be writable. Absent, it is the **Project Document Index** `Research` location, else `docs/research/`.
- `--auto` makes the run unattended: read [`unattended-runs.md`](../../references/unattended-runs.md) and follow it.

`Decisions`, `ADRs`, `Product`, `Learnings`, `Architecture`, and `Context Map` are Project Document Index entries.

## Rules

- Print each recommended skill invocation as a complete, paste-ready line in the host's syntax, including its target path or request and required arguments.

- **Cite, then ask.** A decision the code, an `Accepted` ADR, a Still Current line, or a Preflight answer of the `andthen:plan` skill that the FIS states and `INPUT` quotes to record already settles is cited, never asked. A recommendation that reopens one names it and the new evidence. A `Proposed` ADR or a **Pending** entry is a recommendation, never a settled source: ask it.
- **Recommend, don't decide.** One decision per question: the recommendation first with a one-line rationale, the real alternatives with their observable consequence, and room for free-form input. The asking turn ends on the question, never on a report of what was produced. Use the host's structured question tool wherever it holds the turn for the answer, otherwise the reply. Questions past the tool's per-call limit go in consecutive calls, with nothing done between them.
- A suggested or preselected answer is not confirmation, and neither is detailed `INPUT`. *Implicit confirmation from detailed input* is the failure mode: recording assumptions because the prompt seemed complete.
- **Fit over fashion.** Recommend from fit for this project, never popularity or novelty. Every alternative set includes the floor option per [`design-tree.md`](../../references/design-tree.md), and a recommendation above the floor states what it buys.
- **Anchor on the `Product` document's Proportionality facts.** Drop or flag an option they do not carry or a standing technical non-goal forbids, citing the anchor (`flagged: exceeds stage prototype in docs/PRODUCT.md`). When the facts are absent, ask for all three in one question before you recommend, and write the answers into its Proportionality section, `unknown` for one left unanswered. An unattended run skips the question, writes nothing to `Product`, and says the anchor was unavailable.
- A project document the run creates – `Decisions` on the first registration, `Product` on the first Proportionality answer – is seeded through a `worker` subagent that invokes the `andthen:init` skill with `seed <Index entry>` and the content to seed.
- Every dispatch is a fresh subagent: the installed role agent it names (`implementer`, `reviewer`, `worker`) when available, else a generic inherited subagent. Never pin model or effort in a prompt.
- No code changes.

## Workflow

### 1. Frame the decisions

Read `Decisions`, `Learnings`, `Architecture` and `Context Map` where present, and the code `INPUT` touches. List the decision points, decomposed per `design-tree.md` where a flat list would hide the real trade-offs, and sort each:

- **settled** by a source you can cite – cite it;
- **a requirement** – user-visible behaviour, scope, or a threshold users would notice – goes to the PRD through the `andthen:clarify` skill;
- **binds beyond one story or is costly to reverse** – decided in this run, labelled a one-way or two-way door;
- **local to one story** – left to the `andthen:plan` skill's Preflight.

The first round of questions opens with the list and its sorting, so the user can add, drop, or move a point.

**Gate**: every decision point sorted, settled ones cited.

### 2. Interview

Ask in rounds over the frontier. Every decision whose prerequisites are settled goes in this round, and one that depends on an open answer waits for the next, so no answer is guessed before it is heard. Probe a load-bearing answer before accepting it: what it costs, what breaks at 10x, what reversing it later takes.

A decision is **contested** when no option stands out: the options sit close on the criteria that matter, the evidence is missing, or the user asks for the comparison. Close options on a two-way door are not contested, because either pick is cheap to reverse. A contested decision runs through [`trade-off.md`](references/trade-off.md) before you recommend, with its gates asked in the round where the decision sits. Its Findings Filter reviewer reads [`review-calibration.md`](../../references/review-calibration.md), whose path you pass. A question only running code settles goes to the `andthen:spike` skill, whose Spike Verdict folds back in as evidence.

Shared understanding is confirmed, not inferred. Play the settled set back in a few lines – each decision with its rationale and cost, and what stays open – and ask whether that is it. In the same question, ask whether its ADRs go in `Accepted` or `Proposed` for others to sign off, with `Accepted` recommended since the user just settled them. A correction reopens the frontier.

**Gate**: every decision answered by the user or parked as open, the settled set confirmed, and the ADR status chosen.

### 3. Record

Record each decision at its weight:

- **An ADR** for a decision with real alternatives and consequences, from [`adr-template.md`](references/adr-template.md), in the `ADRs` location, else `docs/adrs/`, numbered after the existing ADRs or from `ADR-001`. Status is the one chosen at the playback, `Proposed` in an unattended run. A `Proposed` ADR the user accepts here becomes `Accepted`, in its file and its row.
- **A Still Current line** for a load-bearing choice with no real alternative: `**<Topic>**: <decision + brief rationale>` under the `Decisions` document's **Still Current**.
- **A Pending bullet** for a decision parked as open, and in an unattended run for a choice with no real alternative, since nobody settled it.

Register each ADR in `Decisions` with a **Current ADRs** row – `ID` linked to the file, `Title`, `Status`, `Scope` (one phrase) – idempotent on ID, updating an existing row in place. When it supersedes a prior decision, move the prior row to **Superseded** with `Prior Decision` (linked), `Superseded By` (linked to the new ADR), and `Notes` (one-line reason), never deleting it, because the lineage is load-bearing.

**Gate**: every decision written and registered, each path printed relative to the project root.

## Follow-up

Close on one `Next (fresh session):` line for the first case that applies, never a menu. A run another skill invoked prints none, because its caller owns the next step.

- **A requirement went to the PRD** – the `andthen:clarify` skill on `<prd-dir>` with: `<the requirements>`.
- **Every decision recorded is one the FIS already states** – the `andthen:exec-plan` skill on that FIS.
- **The run served a plan or FIS** – the `andthen:plan` skill on the FIS, or on `story <id> of <plan.json>` for a story the decisions change (never the plan directory, which re-plans whole), with the recorded decisions as what changed.
- **The run served a PRD whose `Decisions Log` puts design before planning, and no wireframes cover it yet** – the `andthen:ui-ux-design` skill on `<prd-dir>`, naming the modes it lacks, design-system before wireframes.
- **The run served a PRD** – the `andthen:plan` skill on `<prd-dir>`.
- **Otherwise** – the recorded paths, and no line.
