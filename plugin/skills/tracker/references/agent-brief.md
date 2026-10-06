# Agent Brief

The handoff payload triage appends to the issue body when an item reaches `ready-for-agent`. A fresh executor (the `andthen:implement-fix`, `andthen:plan`, or `andthen:clarify` skill) reads the brief alone – it must carry enough for that executor to start without re-reading the whole thread.

## Rules

Author it per the skill's **Durability rule**.

## Output

The section `edit body` appends:

```markdown
## Agent Brief

**Current behavior** – what the system does today in the relevant area, stated observably.

**Desired behavior** – what must be true when this is done; the observable change.

**Key interfaces** – the types, signatures, commands, or endpoints the change turns on, named (not located).

**Acceptance criteria** – checkable conditions that prove the desired behavior, one per line.

**Out of scope** – adjacent work this item deliberately does not cover, so the executor does not widen the change.
```
