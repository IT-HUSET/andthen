---
description: Compact the conversation into a handoff document a fresh session resumes from – before `/clear`, when low on context, at a session boundary. Trigger on 'handoff', 'wrap up for resume', 'fresh start'.
argument-hint: "[what the next session will focus on]"
---

# Hand Off Conversation to a Fresh Session

Route the session's durable fragments to their homes, then write the document a fresh agent resumes from cold.

## Input

`$ARGUMENTS` is the optional focus for the next session (`FOCUS`).

## Rules

- Print each recommended skill invocation as a complete, paste-ready line in the host's syntax, including its target path or request and required arguments.

- **Reference, don't duplicate.** Point to artifacts named in the **Project Document Index** by path; the next session reads them directly.
- **Redact secrets; omit when unsure.** Tokens, keys, credentials, PII, and shell output that may carry them become `[REDACTED:<kind>]`, or the entry is dropped, because `.agent_temp/` is not private.
- **No per-mutation confirmation.** Keep every write idempotent.
- **Compress to what changes the next session's decisions.**

## Workflow

**1. Triage by durability.** Bin each substantive fragment; skip empty bins. Ends with every fragment in a bin.

| Bin | Examples | Where it goes |
|---|---|---|
| **Defensive knowledge** | "Watch out for X", error → root cause patterns, tooling gotchas with clear scope | One bullet under the fitting topic of the `Learnings` document, admitted against its header note; uncertain entries stay as recommendations |
| **Settled load-bearing choice** | A decision taken with no real alternative – no trade-off left to weigh, no ADR warranted | Recommend one bullet under the `Decisions` document's **Still Current** – do not auto-write |
| **Structural decision needing rationale** | "We chose X over Y because…" with real trade-offs and consequences | Recommend the `andthen:decide` skill – do not auto-create the ADR |
| **Transient context** | Open questions, hypotheses, things tried, failed approaches, a story blocked or stopped mid-way, next-session priming | The handoff doc itself |

**2. Apply durable mutations.** For each defensive-knowledge entry, resolve the `Learnings` document from the **Project Document Index**. Ends with every such entry a written bullet or a `Pending durable writes` line.

- **Target present** – write one bullet per logical entry.
- **No `Learnings` Index entry** – skip the write and list it under `Pending durable writes`, naming what is missing.
- **`Learnings` indexed but the file missing** – create it at the path its entry names, opening with the header line the Index preamble quotes, then write the bullet.

**3. Write the handoff doc** to the Output path. Ends with the document at the stamped path holding every template heading.

## Output

Save to `.agent_temp/handoff/handoff-<UTC-ts>.md`, where `<UTC-ts>` is `date -u +%Y%m%d-%H%M%S`. Use this exact template:

````markdown
> Handoff context for a fresh session. May contain conversation excerpts – review before sharing or restoring.

# Handoff – <UTC-ts>

## Next session focus
<FOCUS, or "Resume current mid-flow work" if empty>

## Where we are
<active feature, artifact, and phase, by path>

## Open questions
- <each tied to a concrete next action where possible>

## Hypotheses & things tried
- <item>

## Pending durable writes
<omit when empty; Step 1's recommendations and Step 2's skipped writes>

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

Print one line per applied mutation (e.g. `Learnings: + **Fixture reset**`).

## Follow-up

Print the resume prompt as a fenced block the user pastes into a fresh session:

````text
Resume from .agent_temp/handoff/handoff-<UTC-ts>.md
````
