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

- **Route by durability; auto-mutate bounded stores, recommend authorial ones.** Per-bin destinations and mechanics live in the Step 1 triage table; the one non-obvious case: uncertain `LEARNINGS.md` wording or topic placement → leave as recommendation, don't auto-write.
- **Respect `ops` contracts.** `update-learnings add` rejects bullets that don't start with `- **{title}**` or exceed 200 chars – normalize first. `update-state` forms route by field: shared `active-story <id> "<name>" "In Progress"` (or `Done` to remove), `blocker "<text>"` (or `blocker remove "<text>"`), `decision "<text>"` → shared STATE.md; local `note "<text>"`, `focus "<text>"` → the gitignored STATE.local.md. Plan-governed story status/claims use `update-plan <plan> <id> <status>` (lowercase enum, e.g. `in-progress`/`done`) / `update-plan-owner <plan> <id> <owner>`; resolve `<plan>` from the Project Document Index `Specs & Plans` row, the State's FIS paths, or session context. `ops` timestamps decision/note automatically.
- **Reference, don't duplicate.** Point to artifacts named in the **Project Document Index** (PRD, `plan.json`, FIS, review reports, ADRs, `Ubiquitous Language`) by path – the next session reads them directly.
- **Redact secrets; omit when unsure.** Tokens, keys, credentials, PII, and shell output that may carry them → `[REDACTED:<kind>]` or drop the entry. The doc lands under `.agent_temp/` and may be picked up by IDE indexers, screen-share, or backups – assume non-private.
- **Pragmatic by default.** No per-mutation confirmation; show applied diffs inline at the end. `--no-mutate` is the escape hatch.


## GOTCHAS

- Re-running `/andthen:handoff` in quick succession duplicates `decision` / `note` entries (`update-learnings add` is idempotent at `ops`; decision/note are not). Re-run only after substantive new conversation.
- Treating the handoff as a transcript dump – compress to what changes the next session's decisions, not what happened.


## WORKFLOW

### 1. Triage by durability

Bin each substantive fragment; skip empty bins.

| Bin | Examples | Where it goes |
|---|---|---|
| **Shared mid-flow state** | New active story, story status change, blockers raised/lifted, decisions | The `andthen:ops` skill: story status/claims → `update-plan` / `update-plan-owner` when a `plan.json` governs, else `update-state active-story`; `blocker` / `decision` → shared STATE.md (auto unless `--no-mutate`; skip+recommend if STATE.md absent) |
| **Session-local state** | Your session continuity notes, current focus for next session | The `andthen:ops` skill: `update-state note` / `focus` → gitignored STATE.local.md (auto unless `--no-mutate`) |
| **Defensive knowledge** | "Watch out for X", error → root cause patterns, tooling gotchas with clear scope | The `andthen:ops` skill: `update-learnings add <topic> <entry>` (auto for clearly-bounded entries; uncertain ones stay as recommendations) |
| **Structural decision needing rationale** | "We chose X over Y because…" with real trade-offs and consequences | Recommend the `andthen:architecture --mode trade-off` skill – do not auto-create the ADR |
| **Transient context** | Open questions, hypotheses, things tried, failed approaches, next-session priming | The handoff doc itself |

### 2. Apply durable mutations

Skip if `--no-mutate`. Otherwise, per entry in the first two bins:

- Resolve shared `STATE.md`, local `STATE.local.md`, and `LEARNINGS.md` paths from the **Project Document Index** (`State`, `State (local)`, `Learnings` rows).
- For shared `STATE.md` / `LEARNINGS.md`: if the file (or its Index row) is absent, **skip** and reroute to `Pending durable writes` naming the missing file. Do not create – the `andthen:init` skill owns creation.
- For local `note` / `focus`: the `andthen:ops` skill auto-creates the gitignored `STATE.local.md`, so these always apply (no skip).
- Otherwise invoke the `andthen:ops` skill with the appropriate sub-operation (arg shapes per INSTRUCTIONS). One invocation per logical entry.
- Capture each applied mutation for the step 4 summary.

### 3. Write the handoff doc

Resolve project root via `git rev-parse --show-toplevel` (fallback: CWD). Save to `.agent_temp/handoff/handoff-<UTC-ts>.md` where `<UTC-ts>` = `date -u +%Y%m%d-%H%M%S` (UTC → lexicographic = chronological across timezones, matching the `andthen:ops` convention). The doc is the resume contract – a fresh agent reads it cold, so ALWAYS use this exact template:

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
<workflow skill to run after resuming context; usually `/andthen:now-what`, or a specific skill when one obvious next step exists>

## Index
- PRD: <path or omit>
- plan.json: <path or omit>
- FIS: <paths or omit>
- Review reports: <paths or omit>
- ADRs: <paths or omit>
- Ubiquitous Language: <path or omit>
````

### 4. Print summary

- One line per applied mutation (e.g. `STATE: added active-story s03 "validator hardening" (In Progress)`).
- The resume prompt, as a fenced block the user pastes into a fresh session:

  ````text
  Resume from .agent_temp/handoff/handoff-<UTC-ts>.md
  ````


## OUTPUT

- `.agent_temp/handoff/handoff-<UTC-ts>.md` – always.
- Durable mutations to shared `STATE.md` / `LEARNINGS.md` (when those files exist) and to the gitignored `STATE.local.md` via the `andthen:ops` skill, when `--no-mutate` is unset.

The doc is self-sufficient; no skill invocation needed to resume.
