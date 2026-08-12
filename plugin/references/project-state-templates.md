# Project State Document Templates

Canonical starter templates for the supplementary project documents referenced in the **Project Document Index** of the root agent instruction file (`CLAUDE.md` / `AGENTS.md`), consumed at scaffold- and write-time by the skills that create or maintain these documents – where a specific skill owns a document, its template's `>` note says so. Read the section you need (see Contents), not the whole file. Fill in what applies, remove what doesn't.

The `>` notes address the consuming skill and do not ship. Everything inside a fenced block is emitted verbatim into the created file – **including the HTML comments**, which are deliberate embedded guidance for whoever later maintains that document in the target repo, with or without AndThen installed. The comments are contract, not noise: do not strip them when scaffolding, and do not prune them from this reference.

## Contents
- STATE.md – shared, committed cross-session state snapshot
- STATE.local.md – per-developer, **gitignored** session-local state (never committed)
- PRODUCT-BACKLOG.md – requirements registry with REQ-IDs
- ROADMAP.md – phases, success criteria, milestones
- TECH-DEBT-BACKLOG.md – tech debt by severity
- PRODUCT.md – product vision and high-level requirements
- DECISIONS.md – ADR index plus non-ADR choices
- ARCHITECTURE.md – component boundaries and data flow
- LEARNINGS.md – defensive knowledge and error patterns
- STACK.md – technology stack with versions
- KEY_DEVELOPMENT_COMMANDS.md – dev/test/build/deploy commands
- UBIQUITOUS_LANGUAGE.md – domain glossary
- ISSUE-TRACKER.md – agent issue-tracker backend + label role mapping
- CONTEXT-MAP.md – bounded contexts and integration patterns
- OUT-OF-SCOPE.md – cross-feature registry of rejected concepts

---

## STATE.md

> **Shared, committed** cross-session state – a snapshot of _current_ team-wide state, not a history log. Keep under ~60 lines so agents can consume it quickly. Created by the `andthen:init` skill; field updates go through the `andthen:ops` skill (`update-state` form).
>
> **Team note**: STATE.md holds only shared, low-churn team state; high-churn per-developer context lives in the **gitignored** `STATE.local.md` so teammates never collide.

```markdown
# Project State

Last Updated: YYYY-MM-DD HH:MM

## Current Phase
<!-- Active phase/milestone name and one-line status -->

Phase: ...
Status: On Track | At Risk | Blocked

## Active Stories
<!-- When a plan.json governs (has undone stories), Active Stories derive from it on read – store rows only for ad-hoc work in no governing plan.
     Otherwise one row per in-progress story (Owner = who is executing it); move completed stories to Recently Completed. -->

| Story | Owner | Status | FIS | Notes |
|-------|-------|--------|-----|-------|
| ...   | ...   | ...    | ... | ...   |

## Recently Completed
<!-- Last 2 milestones only, one line each. Older milestones belong in CHANGELOG.md.
     If more exist, add a trailing line: "Previous: 0.3, 0.2, 0.1" -->

- **{version}** ({date}): {one-line summary}

## Blockers
<!-- Anything preventing progress. Remove resolved blockers and those older than ~14 days with no activity. -->

- ...

## Recent Decisions
<!-- Key decisions made in the last 1-2 sessions. Keep max ~10. Move older items to ADRs. -->

- ...
```

---

## STATE.local.md

> **Per-developer, gitignored** session-local state – never committed (the `andthen:init` skill adds it to `.gitignore`). Holds high-churn, personal context so teammates sharing the repo don't collide on `STATE.md`; each checkout has its own. Keep it short – a scratch snapshot for _your next session_, not a shared record.

```markdown
# Local State (not committed)

Last Updated: YYYY-MM-DD HH:MM

## My Current Focus
<!-- What you are actively working on this session – story id / FIS / one-line intent. -->

- ...

## Session Continuity Notes
<!-- Context YOUR next session needs to pick up where you left off. Keep max ~5.
     Remove notes already captured in shared STATE.md, CHANGELOG, or a handoff doc. -->

- ...
```

---

## PRODUCT-BACKLOG.md

> Product backlog with unique IDs for traceability.

```markdown
# Product Backlog

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
<!-- Explicitly excluded requirements – useful to prevent scope creep. -->

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

## TECH-DEBT-BACKLOG.md

> Known technical debt grouped by severity. Append-only run blocks (`### Run: {timestamp} – tech-debt`) are written under the matching severity heading by the `andthen:ops` skill (`update-tech-debt append` form). The placeholder line is removed on the first write per section.

```markdown
# Technical Debt Backlog

## High
<!-- Severity: blocks correctness, security, or critical workflow. Address with priority. -->

_No tech debt recorded yet._

## Medium
<!-- Severity: maintainability, clarity, or non-critical correctness. Schedule deliberately. -->

_No tech debt recorded yet._

## Low
<!-- Severity: cosmetic, minor consistency, or opportunistic cleanup. Address when convenient. -->

_No tech debt recorded yet._
```

---

## PRODUCT.md

> Product vision and high-level requirements – the "what and why" agents read before product-shaping work. Richer detail belongs in a PRD (produced by the `andthen:prd` skill); this document is the durable orientation layer above any single PRD.

```markdown
# Product

## Vision
<!-- One paragraph: what this product is, who it's for, and why it exists. -->

## Target Users
<!-- Primary user segments / personas and what they're trying to accomplish. -->

- **[Segment]**: [Job-to-be-done / core need]

## Value Propositions
<!-- The specific value delivered to each user segment. Keep concrete. -->

- ...

## Key Capabilities
<!-- High-level capability list – not features, capabilities. Link to PRDs for detail. -->

| Capability | Description | Status |
|------------|-------------|--------|
| ...        | ...         | Planned / In Progress / Shipped |

## Non-Goals
<!-- Explicit scope boundaries – what this product is deliberately NOT. Prevents drift. -->

- ...

## Success Metrics
<!-- How we'll know the product is working. Qualitative is fine if quantitative isn't available yet. -->

- ...
```

---

## DECISIONS.md

> Decisions registry – index of ADRs plus load-bearing non-ADR choices. Individual ADRs live in `docs/adrs/` (or as configured in the **Project Document Index**).

```markdown
# Decisions

<!-- Maintenance:
     - The `andthen:architecture` skill in `--mode trade-off` auto-registers
       ADRs (appends to Current ADRs; moves prior rows to Superseded on
       supersession). Idempotent on ADR ID.
     - "Still Current" captures load-bearing choices that don't warrant a full
       ADR. Promote via `--mode trade-off` if the choice becomes contested.
     - Status enum (Current ADRs): Proposed | Accepted | Deprecated.
       Superseded decisions move to the dedicated table; Rejected decisions
       stay only in the ADR file itself (not indexed). -->

## Current ADRs

| ID | Title | Status | Scope |
|----|-------|--------|-------|
| ... | ... | ... | ... |

## Superseded

<!-- Move prior rows here when a new ADR supersedes them. Never delete –
     the lineage is load-bearing context for agents reading the codebase. -->

| Prior Decision | Superseded By | Notes |
|----------------|---------------|-------|
| ... | ... | ... |

## Still Current

<!-- Load-bearing decisions that don't warrant a full ADR. One bullet each.
     Format: **<Topic>**: <decision + brief rationale>. -->

- ...

## Pending

<!-- Decisions under discussion, awaiting acceptance. Typically populated by
     the `andthen:architecture` skill in `--mode trade-off` when a
     recommendation hasn't yet been accepted as an ADR. -->

- ...
```

---

## ARCHITECTURE.md

> System architecture overview – enough for an agent to understand component boundaries and data flow.

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

> Defensive knowledge for future contributors – traps, domain insights, procedural knowledge, and error patterns. Organized by topic, not chronologically. The file is a bounded **index**: skills read it whole at task start, so its size is paid on nearly every run.
>
> **Boundary**: LEARNINGS = _"watch out for X"_. `DECISIONS.md` = _"we chose X over Y because…"_. `STATE.md` = _"we're currently doing X"_ (transient). Route overlapping entries to their owner.
>
> **Graduation ladder** – record each insight at the strongest tier it supports: encode it as a lint rule/test/hook (prose is advisory; a red check is enforced) > DECISIONS/ADR > an entry here > a harness-memory note (personal context only – project-durable knowledge belongs in committed docs, visible to every agent and teammate). Delete entries once encoded or stale.

```markdown
# Project Learnings

<!-- Traps only, one bullet each: `- **{title}** – …` under 200 chars, trap + pointer; postmortem
     depth lives in the spec archive or an ADR. Bar: "Would a competent developer with code and
     git access still get bitten?" Skills read this index whole – keep it lean; shards load per
     touched topic, and a repeat-check touches its topic. Maintain via the
     `andthen:ops` skill (`update-learnings` forms), which owns the 150-line ceiling and
     `learnings/` shard graduation. Delete entries once encoded as checks or stale. -->

## [Topic Area 1]
<!-- e.g. "Language Traps", "Framework Patterns", "API Quirks", "Deployment", etc. -->

- **[Trap/insight]**: [Description] _(context/version)_

## Error Patterns
<!-- Log recurring errors. Deterministic errors (bad schema, wrong type) → conclude immediately.
     Infrastructure errors (timeout, rate limit) → log, no conclusion until pattern emerges.
     Conclusions are promoted into the relevant topic section (or its shard). -->

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

## KEY_DEVELOPMENT_COMMANDS.md

> Key commands for development, running, testing, deployment, and code quality. For monorepos, organize commands per sub-project.

```markdown
# Key Development Commands

<!-- Keep commands up to date as the project evolves.
     For monorepos: add a section per sub-project with its own commands. -->

## Running the Application
<!-- List commands to start the application in development mode. -->
| Command | Description |
|---------|-------------|
| `TODO`  | Start development server |

Application URL: `TODO` <!-- e.g. http://localhost:3000 -->

## Code Quality (Formatting, Linting, Type Checking)
<!-- Commands to run after each task to ensure code quality. -->
| Command | Description |
|---------|-------------|
| `TODO`  | Format code |
| `TODO`  | Lint and type-check |

## Testing
<!-- Commands to run tests – unit, integration, E2E. -->
| Command | Description |
|---------|-------------|
| `TODO`  | Run all tests |
| `TODO`  | Run a specific test file |

## Build & Deployment
<!-- Commands for building and deploying the application. -->
| Command | Description |
|---------|-------------|
| `TODO`  | Production build |
| `TODO`  | Deploy |

## Visual Validation
<!-- Remove this section if not applicable. -->
| Command / Tool | Description |
|----------------|-------------|
| `TODO`         | Launch app for manual testing |
| `TODO`         | Capture screenshot |

<!-- For monorepos, add per-sub-project sections below:

## [sub-project-name] (e.g. apps/frontend)
| Command | Description |
|---------|-------------|
| `TODO`  | Start dev server |
| `TODO`  | Run tests |
| `TODO`  | Lint |
-->
```

---

## UBIQUITOUS_LANGUAGE.md

> Domain glossary – scaffolded by the `andthen:init` skill on confirm; extracted and maintained by the `andthen:ubiquitous-language` skill, clustering terms by the Context Map's bounded contexts when one exists.

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

---

## ISSUE-TRACKER.md

> Maps the issue-tracker backend agent workflows read from and publish to. Resolved before any issue operation via **Tracker resolution**. `Backend: GitHub`, or an absent document, uses the built-in `gh` flows – leave the Operation Table out. Any other backend fills the Operation Table so skills substitute each transport call; body shapes, label names, and footer tokens stay identical (the document maps transport, not contract). The `andthen:init` skill registers it.

```markdown
# Issue Tracker

Backend: GitHub
<!-- One of: GitHub | <named backend, e.g. Jira, Linear>. GitHub (or no file) uses the built-in gh default –
     omit the Operation Table below. -->

## Operation Table
<!-- Non-GitHub backends only. Map every abstract operation to the backend's concrete command/API call.
     A required operation left unmapped blocks triage/publish (BLOCKED: issue-tracker operation <op> unmapped).
     Each value is a single direct command invocation (executable + fixed args + <placeholders>) – no pipes,
     shell operators, command substitution, or piping to an interpreter.
     This file is security-critical executable config: review changes as code.
     The backend must expose numeric issue ids; <N> is the issue number. -->

| Operation      | Backend call |
|----------------|--------------|
| fetch issue    | ...          |
| list issues    | ...          |
| create issue   | ...          |
| comment        | ...          |
| edit body      | ...          |
| add label      | ...          |
| remove label   | ...          |
| close issue    | ...          |

## Label Role Mapping
<!-- Canonical role → the label this repo actually uses. Defaults equal the canonical names;
     change the right column only when your tracker uses different label text. -->

| Canonical role  | Repo label      |
|-----------------|-----------------|
| needs-triage    | needs-triage    |
| needs-info      | needs-info      |
| ready-for-agent | ready-for-agent |
| ready-for-human | ready-for-human |
| wontfix         | wontfix         |
| bug             | bug             |
| enhancement     | enhancement     |

## Notes
<!-- Backend-specific quirks: auth, project/board scoping, required fields, rate limits. -->

- ...
```

---

## CONTEXT-MAP.md

> Bounded contexts and the patterns that integrate them. Registered and refreshed by the `andthen:architecture` skill in `--mode strategic-design` – the accepted Target map (or the confirmed Current map when auditing) graduates here; brownfield re-runs read it first and report drift against it. Idempotent per context and per context pair.

```markdown
# Context Map

## Bounded Contexts

| Context | Purpose | Code location |
|---------|---------|---------------|
| ...     | ...     | ...           |

## Integration Patterns
<!-- One row per ordered context pair that exchanges data. Pattern names come from the 9-pattern catalog
     (Partnership, Shared Kernel, Customer/Supplier, Conformist, Anticorruption Layer, Open Host Service,
     Published Language, Separate Ways, Big Ball of Mud). Split a multi-channel pair into separate rows. -->

| Upstream | Downstream | Pattern | Notes |
|----------|------------|---------|-------|
| ...      | ...        | ...     | ...   |

## Ubiquitous Language
<!-- Per-context pointer into the matching cluster(s) of the Ubiquitous Language document – a pointer, not a copy. -->

| Context | Language clusters |
|---------|-------------------|
| ...     | ...               |

## Changelog
- [date]: Initial registration
```

---

## OUT-OF-SCOPE.md

> Cross-feature registry of deliberately rejected *concepts* – institutional memory plus a concept-level dedup surface so the same idea is not re-litigated under a new name ("night theme" matches a dark-mode entry). Distinct from a document's own `Out of Scope` section (per-feature non-goals): only firmly rejected directions graduate here; deferred follow-ups stay in the backlog. The `andthen:clarify`, `andthen:prd`, and `andthen:issue-triage` skills write it; the `andthen:init` skill scaffolds it.
>
> **Graduation contract** (all writers): resolve the registry location from the **Project Document Index** (default `docs/OUT-OF-SCOPE.md`); create the file from this template and add its index row when missing (the `DECISIONS.md` create-if-missing pattern); append or update the concept's `## <Concept>` section with the **Decision** (why rejected, dated) and its **Prior requests** source. Never record a request closed as already-implemented – it was built, not rejected.

```markdown
# Out of Scope Registry

<!-- One `## <Concept>` section per rejected concept – match on the concept, not the wording.
     Poisoning rule: never record a request closed as already-implemented. That closure points at the
     implementation; it is not a rejection, and recording it here would falsely block the real feature. -->

## [Concept]

**Decision**: [why it was rejected] _(YYYY-MM-DD)_

**Prior requests**:
- [source / where it came up]
```
