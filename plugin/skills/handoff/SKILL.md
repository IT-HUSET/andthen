---
description: Use when the user wants to compact the current conversation into a handoff document a fresh agent can resume from – before `/clear`, before running out of context, or at a natural session boundary. Trigger on 'hand off', 'handoff', 'compact this', 'wrap up for resume', 'before I /clear', 'fresh start', "I'm running out of context".
argument-hint: "[what the next session will focus on] [--no-mutate]"
---

# Hand Off Conversation to a Fresh Session

Compact the conversation; route durable fragments to canonical homes via the `andthen:ops` skill; write the transient remainder to `.agent_temp/handoff/`.


## VARIABLES

ARGUMENTS: $ARGUMENTS _(optional – free-form focus for the next session)_

### Optional Flags
- `--no-mutate` → Skip durable-store auto-updates; produce the handoff doc only.


## INSTRUCTIONS

- **Route by durability.** Mid-flow state and defensive notes → `STATE.md` / `LEARNINGS.md`; structural decisions → ADR via the `andthen:architecture --mode trade-off` skill; everything else → the handoff doc.
- **Auto-mutate bounded stores; recommend authorial ones.** `STATE.md` updates are schema-shaped and reversible – auto-run via the `andthen:ops` skill when the file exists. `LEARNINGS.md` appends auto-run for clearly-bounded entries when the file exists; uncertain wording or topic placement → leave as recommendation. ADRs need real trade-off authoring – recommend only, never auto-create.
- **Respect `ops` contracts.** `update-learnings add` rejects bullets that don't start with `- **{title}**` or exceed 200 chars – normalize first. `update-state` forms: `active-story <id> "<name>" "In Progress"` (or `Done` to remove), `blocker "<text>"` (or `blocker remove "<text>"`), `decision "<text>"`, `note "<text>"`. `ops` timestamps decision/note automatically.
- **Reference, don't duplicate.** Point to artifacts named in the **Project Document Index** (PRD, `plan.json`, FIS, review reports, ADRs, `Ubiquitous Language`) by path – the next session reads them directly.
- **Redact secrets; omit when unsure.** Tokens, keys, credentials, PII, and shell output that may carry them → `[REDACTED:<kind>]` or drop the entry. The doc lands under `.agent_temp/` and may be picked up by IDE indexers, screen-share, or backups – assume non-private.
- **Detect-and-skip on missing files or Index rows.** The `andthen:ops` mutators refuse when `STATE.md` / `LEARNINGS.md` is absent; `STATE.md` is *optional* (init Planning, not Core), so many projects lack it. Reroute those entries to handoff-doc recommendations naming the missing file – the user runs the `andthen:init` skill to enable durable routing.
- **Pragmatic by default.** No per-mutation confirmation; show applied diffs inline at the end. `--no-mutate` is the escape hatch.


## GOTCHAS

- Writing the handoff anywhere other than `.agent_temp/handoff/` – the `andthen:now-what` skill won't find it.
- Re-running `/andthen:handoff` in quick succession duplicates `STATE.md` `decision` / `note` entries (`update-learnings add` is idempotent at `ops`; decision/note are not). Re-run only after substantive new conversation.
- Treating the handoff as a transcript dump – compress to what changes the next session's decisions, not what happened.


## WORKFLOW

### 1. Triage by durability

Bin each substantive fragment; skip empty bins.

| Bin | Examples | Where it goes |
|---|---|---|
| **Mid-flow workflow state** | New active story, story status change, blockers raised/lifted, decisions, session notes | The `andthen:ops` skill: `update-state active-story` / `blocker` / `decision` / `note` (auto unless `--no-mutate`) |
| **Defensive knowledge** | "Watch out for X", error → root cause patterns, tooling gotchas with clear scope | The `andthen:ops` skill: `update-learnings add <topic> <entry>` (auto for clearly-bounded entries; uncertain ones stay as recommendations) |
| **Structural decision needing rationale** | "We chose X over Y because…" with real trade-offs and consequences | Recommend the `andthen:architecture --mode trade-off` skill – do not auto-create the ADR |
| **Transient context** | Open questions, hypotheses, things tried, failed approaches, next-session priming | The handoff doc itself |

### 2. Apply durable mutations

Skip if `--no-mutate`. Otherwise, per entry in the first two bins:

- Resolve `STATE.md` / `LEARNINGS.md` paths from the **Project Document Index**.
- If the file (or its Index row) is absent, **skip** and reroute to `Pending durable writes` naming the missing file. Do not create – the `andthen:init` skill owns creation.
- Otherwise invoke the `andthen:ops` skill with the appropriate sub-operation (arg shapes per INSTRUCTIONS). One invocation per logical entry.
- Capture each applied mutation for the step 4 summary.

### 3. Write the handoff doc

Resolve project root via `git rev-parse --show-toplevel` (fallback: CWD). Save to `.agent_temp/handoff/handoff-<UTC-ts>.md` where `<UTC-ts>` = `date -u +%Y%m%d-%H%M%S` (UTC → lexicographic = chronological across timezones, matching the `andthen:ops` convention). ALWAYS use this exact template – the `andthen:now-what` skill parses these headings:

````markdown
> Handoff context for a fresh session. May contain conversation excerpts – review before sharing or restoring.

# Handoff – <UTC-ts>

## Next session focus
<$ARGUMENTS, or "Resume current mid-flow work" if empty>

## Where we are
<1–3 lines naming active feature/artifact/phase; reference STATE.md / in-flight FIS / plan.json / PRD by path – do not restate>

## Open questions
- <each tied to a concrete next action where possible>

## Hypotheses & things tried
- <only what changes the next session's decisions>

## Pending durable writes
<omit when empty; otherwise: ADRs to consider via `andthen:architecture --mode trade-off`; LEARNINGS candidates left as recommendations; missing durable files named (e.g. "STATE.md absent – run /andthen:init to enable durable routing")>

## Recommended next skill
<usually `/andthen:now-what`; name a specific skill only when one obvious next step exists>

## Index
- PRD: <path or omit>
- plan.json: <path or omit>
- FIS: <paths or omit>
- Review reports: <paths or omit>
- ADRs: <paths or omit>
- Ubiquitous Language: <path or omit>
````

### 4. Print summary

- The handoff doc path.
- One line per applied mutation (e.g. `STATE: added active-story s03 "validator hardening" (In Progress)`).
- The recommended resume command (default: `/andthen:now-what`).


## OUTPUT

- `.agent_temp/handoff/handoff-<UTC-ts>.md` – always.
- Durable mutations to `STATE.md` / `LEARNINGS.md` via the `andthen:ops` skill, when those files exist and `--no-mutate` is unset.

Resume with `/andthen:now-what` – it scans `.agent_temp/handoff/` and surfaces the most recent doc as priming context.
