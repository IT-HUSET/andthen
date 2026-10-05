# Project Document Templates

Canonical starter templates for the supplementary project documents in the **Project Document Index**. Read the section you need (see Contents), not the whole file.

A template's `>` note sits above its fenced block, states who owns that document, and does not ship. Everything inside a fenced block is emitted verbatim into the created file, HTML comments included, because they guide whoever maintains the document later.

## Contents
- Regeneration contract – merge rules shared by the derived documents (ARCHITECTURE, KEY_DEVELOPMENT_COMMANDS)
- ROADMAP.md – phases, success criteria, milestones
- TECH-DEBT-BACKLOG.md – tech debt by severity
- PRODUCT.md – product vision and high-level requirements
- DECISIONS.md – ADR index plus non-ADR choices
- ARCHITECTURE.md – component boundaries and data flow
- LEARNINGS.md – defensive knowledge and error patterns
- KEY_DEVELOPMENT_COMMANDS.md – dev/test/build/deploy commands
- TESTING-STRATEGY.md – levels, conventions, and the before-merge bar
- UBIQUITOUS_LANGUAGE.md – domain glossary
- ISSUE-TRACKER.md – agent issue-tracker backend + label role mapping
- CONTEXT-MAP.md – bounded contexts and integration patterns

---

## Regeneration contract

> Binds every writer of a _derived_ document – ARCHITECTURE.md, KEY_DEVELOPMENT_COMMANDS.md – whose content a fresh analysis of the codebase re-derives.
>
> - **An existing document at the target path** is **merged, never overwritten**. Regenerate the sections its template note marks _derived_ from the current analysis. Preserve the sections marked _judgment_, because rationale is the one thing code cannot re-derive, and append genuinely new items marked `(new)`.
> - **A row whose subject can no longer be located** is flagged in place, never deleted: it may have moved rather than gone.
> - **Template headings not locatable at all** mean the document was hand-written to a different structure, so no merge is attempted. Leave the file untouched, write the analysis beside it as `<NAME>.discovered.md` under a `> Status: Discovered – requires validation by team` header, and name the pair for reconciliation.
> - **An absent target** is written fresh from the template.

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

> Known technical debt grouped by severity, append-only. An agent deferring a fix reads the document and appends one entry under the matching severity heading, which *is* the entry's severity. A section's first write replaces its placeholder line.

```markdown
# Technical Debt Backlog

<!-- One bullet per deferral: `- **{title}** – {symptom} at {location}. Deferred because {named
     blocker}. Source: {report, story, or run}.` Blocker and back-link keep it auditable here alone. -->

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

> Product vision and high-level requirements – the "what and why" agents read before product-shaping work. Richer detail belongs in a PRD (produced by the `andthen:clarify` skill); this document is the durable orientation layer above any single PRD.

```markdown
# Product

## Vision
<!-- One paragraph: what this product is, who it's for, why it exists. -->

## Target Users
<!-- User segments and what each is trying to accomplish. -->

- **[Segment]**: [Job-to-be-done / core need]

## Value Propositions
<!-- Concrete value per segment. -->

- ...

## Non-Goals
<!-- What this product is deliberately NOT, firmly rejected concepts included: one bullet each – the concept,
     why, the date, where it was requested – matched on the concept, not the wording. Built is not rejected:
     a request closed as already-implemented gets no bullet. -->

- ...

## Proportionality
<!-- The facts proposals are sized against, not values. `unknown` is a valid answer; an empty line is not. -->

- **Stage**: prototype | internal | production
- **Scale**: [users] · [data volume] · [deploy topology] · [maintainers]
- **Standing technical non-goals**: [what this project will not grow – e.g. no new services, no plugin system, no config surface]

## Success Metrics
<!-- How we'll know the product is working; qualitative is fine. -->

- ...
```

---

## DECISIONS.md

> Decisions registry – index of ADRs plus load-bearing non-ADR choices. Individual ADRs live in `docs/adrs/` (or as configured in the **Project Document Index**).

```markdown
# Decisions

<!-- Maintenance:
     - The `andthen:decide` skill auto-registers
       ADRs (appends to Current ADRs; moves prior rows to Superseded on
       supersession). Idempotent on ADR ID.
     - "Still Current" captures load-bearing choices that don't warrant a full
       ADR. Promote via the `andthen:decide` skill if the choice becomes contested.
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
     the `andthen:decide` skill when a
     recommendation hasn't yet been accepted as an ADR. -->

- ...
```

---

## ARCHITECTURE.md

> System architecture overview – enough for an agent to understand component boundaries and data flow.
>
> **Regeneration contract** applies. _Derived_: `Key Components`, `Integration Points`. _Judgment_: `System Overview`, `Data Flow`, `Key Constraints`.

```markdown
# Architecture

## System Overview
<!-- One paragraph: what the system is and what it is built on – language, runtime, main framework.
     Versions stay in the manifest and lockfile. -->

## Key Components
<!-- List major components/modules and their responsibilities. With more than one process,
     deployable units first, then the modules inside each. -->

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

> Defensive knowledge for future contributors – traps, domain insights, procedural knowledge, and error patterns, organised by topic, not chronologically. Skills read it whole at task start, so its size is paid on nearly every run.
>
> **Boundary**: LEARNINGS = _"watch out for X"_. `DECISIONS.md` = _"we chose X over Y because…"_. Route overlapping entries to their owner.
>
> **Graduation ladder** – record each insight at the strongest tier it supports: encode it as a lint rule/test/hook (prose is advisory; a red check is enforced) > DECISIONS/ADR > an entry here > a harness-memory note (personal context only – project-durable knowledge belongs in committed docs, visible to every agent and developer).

```markdown
# Project Learnings

<!-- Traps only, one bullet each: `- **{title}** – …` trap + pointer; postmortem depth lives in
     the story commit or an ADR. An entry is admitted only if a frontier model does not already
     know it, the code and git history do not already carry it, and it outlives the current
     initiative – anything else belongs in that initiative's PRD, plan, or FIS. Read the document
     before appending, so a reworded duplicate of an entry it already carries never lands; keep
     the document short and trim stale entries as you go. Delete entries once encoded as checks
     or stale. A topic that outgrows this index moves to `learnings/<topic-slug>.md` and leaves
     one pointer line here; open a shard only when the task names its topic. -->

## [Topic Area 1]
<!-- e.g. "Language Traps", "Framework Patterns", "API Quirks", "Deployment", etc. -->

- **[Trap/insight]**: [Description] _(context/version)_

## Error Patterns
<!-- Log recurring errors. Deterministic errors (bad schema, wrong type) → conclude immediately.
     Infrastructure errors (timeout, rate limit) → log, no conclusion until pattern emerges.
     Conclusions are promoted into the relevant topic section. -->

| Error | Type | Conclusion |
|-------|------|------------|
| ...   | Deterministic / Infrastructure | ... |

## Process & Tooling
<!-- Non-code knowledge: deploy steps, test prerequisites, CI quirks, agent workflow patterns. -->

- ...
```

---

## KEY_DEVELOPMENT_COMMANDS.md

> The project's checks contract – skills read it instead of guessing, and execute its rows verbatim. Fill every row from what the project already declares: package manifest scripts, `Makefile` / `justfile` targets, `pyproject.toml` / `Cargo.toml` aliases, the CI workflow, README.
>
> **Regeneration contract** applies. _Derived_: every command table. Hand-added commands with no discoverable source (undocumented scripts, team habits) are judgment – flag them, never drop them.

```markdown
# Key Development Commands

<!-- Keep commands up to date as the project evolves.
     For monorepos: add a section per sub-project with its own commands.

     Two ways a command silently lies about a green check, both worth care
     because these rows run unattended inside a story's execution:
     - Config discovery is relative to the working directory. A row that only
       works from one directory says so; otherwise write it to run from the
       repo root.
     - These rows execute in the host's shell, including PowerShell and CMD on
       Windows. Keep POSIX-only idioms (`$(...)`, backticks, `2>/dev/null`,
       shell globs) out of them, or the row fails for reasons unrelated to the
       code. -->

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
<!-- Two tiers, because a per-story run and an end-of-run gate are not the same
     run. Both rows are required: a reader that finds no tiers has to guess what
     is heavy, which is what the tiering exists to stop.
     Keep `{file}` and `{test}` literal in the run-one-test row – the executor
     substitutes them to execute a single proof target; the separator between
     them is whatever this project's runner takes. -->
| Tier | Command | Description |
|------|---------|-------------|
| fast | `TODO`  | Once per story – unit tests and the checks that finish in seconds |
| full | `TODO`  | End of run – integration, E2E, and performance suites |
| run one test | `TODO {file}::{test}` | One test, by file and name |

## Build & Deployment
<!-- Commands for building and deploying the application. -->
| Command | Description |
|---------|-------------|
| `TODO`  | Production build |
| `TODO`  | Deploy |

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

## TESTING-STRATEGY.md

> How this project tests. Authored and maintained by the `andthen:testing` skill in `--mode strategy`, read by every skill that writes a test. Fill it from what the test tree already does, not from general testing theory.

```markdown
# Testing Strategy

<!-- What is true of THIS project's tests, short enough to read on every
     test-writing run. Commands live in the Key Dev Commands document – link
     them, never copy them: two copies drift, and the stale one is the one
     someone runs. -->

Commands: see `docs/KEY_DEVELOPMENT_COMMANDS.md` § Testing (`fast`, `full`, run one test).

## Levels In Use
<!-- Place a behavior by the trust boundary it crosses, not by file count. Say
     whether each boundary runs real (a container, a temp dir) or a fake. Drop
     a row this project does not run rather than leaving it TODO. -->
| Level | Applies to | Lives in |
|-------------|------------|----------|
| Unit        | `TODO`     | `TODO`   |
| Integration | `TODO`     | `TODO`   |
| E2E         | `TODO`     | `TODO`   |

## Framework and Fixture Conventions
<!-- Runner, assertion style, fixture/factory pattern, naming, where helpers
     live, what a new test file is expected to look like. -->
- `TODO`

## What Must Have a Test Before Merge
<!-- The bar, stated so an agent applies it without asking: the named high-risk
     areas and E2E journeys, whether test-first is required, the changed-lines
     coverage gate (or none), and who may quarantine a flaky test, for how long. -->
- `TODO`

## Known Gotchas
<!-- Flaky areas, ordering dependencies, passes-locally-fails-in-CI traps,
     fixtures that lie. One line each. -->
- `TODO`
```

---

## UBIQUITOUS_LANGUAGE.md

> Domain glossary – scaffolded by the `andthen:init` skill on confirm; extracted and maintained by the `andthen:describe` skill in `--mode domain`, clustering terms by the Context Map's bounded contexts when one exists.

```markdown
# Ubiquitous Language

> Domain glossary for [Project Name]. Use these exact terms in code, documentation, and discussion; avoid the listed synonyms.
>
> **Glossary and nothing else.** A term earns a row when getting its name wrong causes a defect – ambiguity, schema drift, misrouting. A row is one sentence under 200 characters: what the term is and where it lives. Mechanism, rationale, status, and open questions stay in the document that owns them – point, don't restate. A row that needs more is a spec in a cell.

## [Domain Cluster Name]

| Term | Definition | Avoid (synonyms) | Bounded Context |
|------|-----------|-------------------|-----------------|
| | | | |

## Overloaded Terms

| Term | Context A | Meaning A | Context B | Meaning B |
|------|-----------|-----------|-----------|-----------|
| | | | | |

```

---

## ISSUE-TRACKER.md

> Maps the issue-tracker backend agent workflows read from and publish to. Resolved before any issue operation via **Tracker resolution**. Any backend other than GitHub fills the Operation Table so skills substitute each transport call. Body shapes, label names, and footer tokens stay identical: the document maps transport, not contract. The `andthen:init` skill registers its Index entry, and the first skill that needs it offers to create it from here.

```markdown
# Issue Tracker

Backend: GitHub
<!-- One of: GitHub | none | <named backend, e.g. Jira, Linear>. GitHub (or no file) uses the built-in gh
     default; none declares no tracker. Either way, omit the Operation Table below. -->

## Operation Table
<!-- Non-GitHub backends only. Map every abstract operation to the backend's concrete command/API call.
     A required operation left unmapped stops triage/publish before the first external call.
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

> Bounded contexts and the patterns that integrate them. Registered and refreshed by the `andthen:architecture` skill in `--mode strategic-design`: the accepted Target map, or the confirmed Current map when auditing, graduates here. Brownfield re-runs read it first and report drift against it. Idempotent per context and per ordered pair plus channel.

```markdown
# Context Map

## Bounded Contexts

| Context | Purpose | Code location |
|---------|---------|---------------|
| ...     | ...     | ...           |

## Integration Patterns
<!-- One row per ordered context pair that exchanges data. Pattern names come from the 9-pattern catalog
     (Partnership, Shared Kernel, Customer/Supplier, Conformist, Anticorruption Layer, Open Host Service,
     Published Language, Separate Ways, Big Ball of Mud). Split a multi-channel pair into one row per channel;
     Channel stays empty for a single-channel pair. -->

| Upstream | Downstream | Channel | Pattern | Notes |
|----------|------------|---------|---------|-------|
| ...      | ...        | ...     | ...     | ...   |

```
