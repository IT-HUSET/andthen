# Project State Document Templates

Lightweight starter templates for the supplementary project documents referenced in the **Project Document Index** of `CLAUDE.md`. Each template provides structure and brief guidance — fill in what applies, remove what doesn't.

---

## STATE.md

> Cross-session state tracking. Keep this under ~100 lines so agents can consume it quickly.

```markdown
# Project State

## Current Phase
<!-- Active phase/milestone name and one-line status -->

Phase: ...
Status: On Track | At Risk | Blocked

## Active Stories
<!-- Stories currently in progress — link to FIS/plan if available -->

| Story | Status | FIS | Notes |
|-------|--------|-----|-------|
| ...   | ...    | ... | ...   |

## Blockers
<!-- Anything preventing progress. Remove section if none. -->

- ...

## Recent Decisions
<!-- Key decisions made in the last 1-2 sessions. Move older items to ADRs. -->

- ...

## Session Continuity Notes
<!-- Context the next session needs to pick up where this one left off. -->

- ...
```

---

## REQUIREMENTS.md

> Validated project requirements with unique IDs for traceability.

```markdown
# Requirements

## Validated
<!-- Requirements confirmed and accepted for implementation. -->

| REQ-ID  | Description | Priority | Stories | Status    |
|---------|-------------|----------|---------|-----------|
| REQ-001 | ...         | Must     | ...     | Planned   |

## Active (Under Discussion)
<!-- Requirements being refined or awaiting validation. -->

| REQ-ID  | Description | Priority | Open Questions |
|---------|-------------|----------|----------------|
| REQ-0XX | ...         | ...      | ...            |

## Out of Scope
<!-- Explicitly excluded requirements — useful to prevent scope creep. -->

- ...
```

---

## ROADMAP.md

> Phase structure with success criteria and milestone grouping.

```markdown
# Roadmap

## Phase 1: [Name]
<!-- Goal: one-sentence purpose of this phase -->

**Success Criteria:**
- [ ] ...

**Milestones:**
| Milestone | Target | Status |
|-----------|--------|--------|
| ...       | ...    | ...    |

## Phase 2: [Name]
<!-- Repeat structure as needed -->

## Future / Backlog
<!-- Items acknowledged but not yet scheduled -->

- ...
```

---

## ARCHITECTURE.md

> System architecture overview — enough for an agent to understand component boundaries and data flow.

```markdown
# Architecture

## System Overview
<!-- One paragraph describing the system at a high level. -->

## Key Components
<!-- List major components/modules and their responsibilities. -->

| Component | Responsibility | Key Files/Dirs |
|-----------|---------------|----------------|
| ...       | ...           | ...            |

## Data Flow
<!-- Describe how data moves through the system. A simple numbered list or diagram reference. -->

1. ...

## Integration Points
<!-- External services, APIs, databases the system depends on. -->

| Service | Purpose | Config Location |
|---------|---------|-----------------|
| ...     | ...     | ...             |

## Key Constraints
<!-- Architectural decisions or constraints that shape the system. Reference ADRs if available. -->

- ...
```

---

## LEARNINGS.md

> Accumulated project knowledge — traps, domain insights, procedural knowledge, and error patterns. Organized by topic, not chronologically. Replaces/evolves the narrower "implementation-notes.md" concept.

```markdown
# Project Learnings

<!-- Organize by topic. Entries should be brief (1-2 sentences).
     The bar: "Would a competent developer with code and git access still get bitten?"
     Actively maintain: merge overlapping entries, remove stale knowledge, split large sections. -->

## [Topic Area 1]
<!-- e.g. "Language Traps", "Framework Patterns", "API Quirks", "Deployment", etc. -->

- **[Trap/insight]**: [Description] _(context/version)_

## [Topic Area 2]

- ...

## Error Patterns
<!-- Log recurring errors. Deterministic errors (bad schema, wrong type) → conclude immediately.
     Infrastructure errors (timeout, rate limit) → log, no conclusion until pattern emerges.
     Conclusions graduate into the relevant topic section above. -->

| Error | Type | Conclusion |
|-------|------|------------|
| ...   | Deterministic / Infrastructure | ... |

## Process & Tooling
<!-- Non-code knowledge: deploy steps, test prerequisites, CI quirks, agent workflow patterns. -->

- ...
```

---

## STACK.md

> Technology stack documentation with versions.

```markdown
# Technology Stack

## Languages
| Language | Version | Notes |
|----------|---------|-------|
| ...      | ...     | ...   |

## Frameworks & Libraries
| Name | Version | Purpose |
|------|---------|---------|
| ...  | ...     | ...     |

## Infrastructure
| Service  | Purpose | Notes |
|----------|---------|-------|
| ...      | ...     | ...   |

## External Services
| Service | Purpose | Docs |
|---------|---------|------|
| ...     | ...     | ...  |

## Dev Tools
| Tool | Purpose | Config |
|------|---------|--------|
| ...  | ...     | ...    |
```

---

## UBIQUITOUS_LANGUAGE.md

```markdown
# Ubiquitous Language

> Domain glossary for [Project Name]. Canonical terms for use in code, documentation, and team communication.
>
> **Usage**: Use these exact terms in code (class names, variables, functions), documentation, and discussion. Avoid synonyms listed in the "Avoid" column.

## [Domain Cluster Name]

| Term | Definition | Avoid (synonyms) | Bounded Context |
|------|-----------|-------------------|-----------------|
| | | | |

## Overloaded Terms

| Term | Context A | Meaning A | Context B | Meaning B |
|------|-----------|-----------|-----------|-----------|
| | | | | |

## Changelog
- [date]: Initial extraction
```
