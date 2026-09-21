---
description: Compact the conversation into a handoff document a fresh session resumes from – before `/clear`, when low on context, at a session boundary. Trigger on 'handoff', 'wrap up for resume', 'fresh start'.
argument-hint: "[what the next session will focus on]"
---

# Hand Off Conversation to a Fresh Session

`FOCUS` is `$ARGUMENTS` – optional free-form focus for the next session.


## INSTRUCTIONS

- **Story status and claims are `plan.json`'s alone** – write `status` and `owner` in the story's row; `done` is the run session's write against executed proof, never this skill's.
- **Reference, don't duplicate.** Point to artifacts named in the **Project Document Index** (PRD, `plan.json`, FIS, review reports, ADRs, `Ubiquitous Language`) by path – the next session reads them directly.
- **Redact secrets; omit when unsure.** Tokens, keys, credentials, PII, and shell output that may carry them → `[REDACTED:<kind>]` or drop the entry. The doc lands under `.agent_temp/` and may be picked up by IDE indexers, screen-share, or backups – assume non-private.
- **Pragmatic by default.** No per-mutation confirmation. Keep every write idempotent – status and owner are set, and a `Learnings` bullet whose bold label is already there is not added again.
- **Not a transcript dump** – compress to what changes the next session's decisions, not what happened.


## WORKFLOW

### 1. Triage by durability

Bin each substantive fragment; skip empty bins.

| Bin | Examples | Where it goes |
|---|---|---|
| **Story status and claims** | Story started, finished, blocked, or claimed | `status` / `owner` in the governing `plan.json` – a single-story feature has a one-story plan like any other |
| **Defensive knowledge** | "Watch out for X", error → root cause patterns, tooling gotchas with clear scope | One bullet under the fitting topic of the `Learnings` document, admitted against its header note; uncertain entries stay as recommendations |
| **Settled load-bearing choice** | A decision taken and not contested – no trade-off left to weigh, no ADR warranted | Recommend one bullet under the `Decisions` document's **Still Current** – do not auto-write |
| **Structural decision needing rationale** | "We chose X over Y because…" with real trade-offs and consequences | Recommend the `andthen:architecture --mode trade-off` skill – do not auto-create the ADR |
| **Transient context** | Open questions, hypotheses, things tried, failed approaches, next-session priming | The handoff doc itself |

### 2. Apply durable mutations

Per entry in the first two bins:

- Resolve the governing `plan.json` (`Specs & Plans` row) and the `Learnings` path from the **Project Document Index**, or from session context.
- If the target (or its Index entry) is absent, **skip** and reroute to `Pending durable writes` naming what is missing. Do not create – the `andthen:init` skill owns creation.
- Otherwise write it with your editor – a plan field, a `Learnings` bullet. One write per logical entry.
- Capture each applied mutation for the step 4 summary.

### 3. Write the handoff doc

Resolve project root via `git rev-parse --show-toplevel` (fallback: CWD). Save to `.agent_temp/handoff/handoff-<UTC-ts>.md` where `<UTC-ts>` = `date -u +%Y%m%d-%H%M%S`. The doc is the resume contract – a fresh agent reads it cold, so use this exact template:

````markdown
> Handoff context for a fresh session. May contain conversation excerpts – review before sharing or restoring.

# Handoff – <UTC-ts>

## Next session focus
<FOCUS, or "Resume current mid-flow work" if empty>

## Where we are
<1–3 lines naming active feature/artifact/phase; reference the in-flight FIS / plan.json / PRD by path – do not restate>

## Open questions
- <each tied to a concrete next action where possible>

## Hypotheses & things tried
- <only what changes the next session's decisions>

## Pending durable writes
<omit when empty; otherwise: ADRs to consider via `andthen:architecture --mode trade-off`; `Decisions` **Still Current** bullets and `Learnings` candidates left as recommendations; missing durable files named (e.g. "no governing plan.json – story status has no durable home this session")>

## Recommended next skill
<workflow skill to run after resuming context; usually the `andthen:now-what` skill, or a specific skill when one obvious next step exists>

## Index
- PRD: <path or omit>
- plan.json: <path or omit>
- FIS: <paths or omit>
- Review reports: <paths or omit>
- ADRs: <paths or omit>
- Ubiquitous Language: <path or omit>
````

### 4. Print summary

- One line per applied mutation (e.g. `plan.json: s03 → in-progress`).
- The resume prompt, as a fenced block the user pastes into a fresh session:

  ````text
  Resume from .agent_temp/handoff/handoff-<UTC-ts>.md
  ````


## OUTPUT

- `.agent_temp/handoff/handoff-<UTC-ts>.md` – always.
- Durable mutations to the governing `plan.json` and the `Learnings` document, when those exist.
