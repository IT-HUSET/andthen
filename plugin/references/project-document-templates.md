# Project Document Templates

Canonical **Project Document Index** entries and starter templates for the project documents. Read the section you need (see Contents), not the whole file.

A template's `>` note sits above its fenced block, states who owns that document, and does not ship. Everything inside a fenced block is emitted verbatim into the created file, HTML comments included, because they guide whoever maintains the document later.

## Contents
- Index entries – one line per document, with its default location
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
- DOMAIN-MAP.md – subdomains, bounded contexts, and integration patterns

---

## Index entries

> The skill that creates a document appends that document's line below to the Index, changing the path only where the project keeps the document elsewhere, so each path below is the default location. `Key Dev Commands` points at the instruction file's § Key Development Commands instead when the project keeps its commands inline. `Agent Temp` ships in the `init` template. An Index that already has a `Context Map` entry keeps it, read as the `Domain Map`, so the skill seeding the `Domain Map` adds no second line.

```markdown
- **Product** – `docs/PRODUCT.md`: vision, personas, non-goals (firmly rejected concepts included), Proportionality facts. Read before proposing a feature, a design, or new machinery, or triaging a request: features anchor to it, and its stage and scale size what gets built.
- **Roadmap** – `docs/ROADMAP.md`: phases with success criteria. Read when sequencing work across phases; update when a phase's scope or criteria change.
- **Specs & Plans** – `docs/specs/<version-or-feature>/`: per version or feature, its `prd.md`, `plan.json`, and one FIS per story (`s01-*.md`, …), written by the `clarify` and `plan` skills. Read the governing FIS before implementing; update the FIS and its story's `plan.json` row as execution proceeds. `plan.json` has one writer per copy at a time, so a `plan` breakdown's story subagents never write it. An oversized FIS is a story too big: decompose it (`OVERSIZE:`), never trim it.
- **Issue Tracker** – `docs/ISSUE-TRACKER.md` (optional): tracker backend, its commands, label role mapping, where the requirements record lives. Read before any issue fetch, triage, or label write.
- **Decisions** – `docs/DECISIONS.md`: ADR index and Still Current notes. Read before proposing or changing a design or architecture choice; settled decisions are not relitigated without new evidence.
- **ADRs** – `docs/adrs/`. Read the ADR a decision cites before revisiting it; add one per new decision.
- **Research** – `docs/research/`: trade-off analyses. Read when re-opening a settled trade-off; add one per new analysis.
- **Architecture** – `docs/ARCHITECTURE.md`: components, data flow, integrations, key constraints. Read before changing a component, a boundary, or data flow.
- **Models** – `docs/models/`: committed typed projections (`architecture-model.json`, `event-storms/<slug>.json`). Read when a task needs component boundaries or a storming session's findings. Regenerate at deliberate points; never hand-edit, since the sources stay the records.
- **Domain Map** – `docs/DOMAIN-MAP.md`: the parts of the business, how much each matters, and the bounded contexts that own them, with their integration patterns. Read before placing a feature, boundary, or integration; update when a subdomain, context, or relationship changes.
- **Ubiquitous Language** – `docs/UBIQUITOUS_LANGUAGE.md`: canonical terms and the synonyms to avoid. Read before naming, renaming, or describing domain concepts; add a row when a term settles.
- **Guidelines** – `docs/guidelines/`. Read a guideline when its condition under Project Guidelines and Standards matches the task.
- **Review Policy** – `docs/REVIEW-POLICY.md` (optional): paths excluded from review, extra passes, verdict thresholds. Read before a review.
- **Wireframes** – `docs/wireframes/` (HTML or images). Read before building or validating a screen; update when a flow changes.
- **Design System** – `docs/design-system/`: `DESIGN.md` is canonical (tokens and rationale), `showcase.html` renders it. Read before writing UI markup or styles; update when a token or component is added.
- **Visual Validation** – `docs/VISUAL-VALIDATION.md`: how the UI is served and captured (serve command, capture tooling, routes and states, breakpoints, reference locations). Read before capturing a screen.
- **Learnings** – `docs/LEARNINGS.md`. Read at task start; add a bullet when bitten by a non-obvious failure.
- **Tech Debt** – `docs/TECH-DEBT-BACKLOG.md`. Read when working in an area that has a listed item; add an entry when deferring a fix.
- **Key Dev Commands** – `docs/KEY_DEVELOPMENT_COMMANDS.md`: dev, test, build, deploy commands. Read before running verification; update when a command changes.
- **Testing Strategy** – `docs/TESTING-STRATEGY.md`: levels in use, framework and fixture conventions, the before-merge bar, known gotchas. Read before authoring tests; update when a convention changes.
- **Agent Temp** – `.agent_temp/`: scratch workspace for reviews, research, and QA; never ship from it.
```

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
     an ADR. An entry is admitted only if a frontier model does not already
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

> Domain glossary – scaffolded by the `andthen:init` skill on confirm; extracted and maintained by the `andthen:domain` skill in `--mode glossary`, clustering terms by the Domain Map's bounded contexts when it has them, else by its subdomains, else by domain theme.

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

> Maps the issue-tracker backend agent workflows read from and publish to. Resolved before any issue operation via **Tracker resolution**. Any backend other than GitHub fills the Operation Table so skills substitute each transport call. Body shapes, label names, and footer tokens stay identical: the document maps transport, not contract. The first skill that needs it offers to create it from here.

```markdown
# Issue Tracker

Backend: GitHub
<!-- One of: GitHub | none | <named backend, e.g. Jira, Linear>. GitHub (or no file) uses the built-in gh
     default; none declares no tracker. Either way, omit the Operation Table below. -->

Record: repo
<!-- Where a feature's requirements record lives after the merge: repo (prd.md stays; the default when
     this line is absent) or tracker (the PRD lives in its issue, child issues keep each story's record,
     and ship deletes prd.md with the plan). -->

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

## DOMAIN-MAP.md

> The parts of the business, how much each matters, and which software boundary owns each. Written by the `andthen:domain` skill: `--mode subdomains` owns Subdomains, Relationships, Worked Example, and Open Questions, and `--mode contexts` owns Bounded Contexts and Integration Patterns. Neither mode rewrites the other's sections, except that `--mode contexts` records a reclassification, an accepted one into Subdomains and a declined one under Open Questions, and rows are idempotent and never deleted. It lists no terms: the glossary holds each once.

```markdown
# Domain Map

## Subdomains
<!-- One entry per subdomain: core, supporting, or generic, why, and what it owns. -->

| Subdomain | Type | Rationale | Owns |
|-----------|------|-----------|------|
| ...       | ...  | ...       | ...  |

## Relationships
<!-- Optional. How subdomains relate, in domain language ("a visit happens at a facility"). -->

- ...

## Worked Example
<!-- Optional. Named instances, a scenario across subdomains, and the rules it shows. -->

- ...

## Open Questions
<!-- A contested classification, both sides recorded, never forced into a verdict. -->

- ...

## Bounded Contexts

| Context | Purpose | Subdomains owned | Team | Code location |
|---------|---------|------------------|------|---------------|
| ...     | ...     | ...              | ...  | ...           |

## Integration Patterns
<!-- One row per ordered context pair that exchanges data. Pattern names come from the 9-pattern catalog
     (Partnership, Shared Kernel, Customer/Supplier, Conformist, Anticorruption Layer, Open Host Service,
     Published Language, Separate Ways, Big Ball of Mud). Split a multi-channel pair into one row per channel;
     Channel stays empty for a single-channel pair. A symmetric pattern (Partnership, Shared Kernel,
     Separate Ways) names its peers in the two context columns, not an upstream and a downstream. -->

| Upstream / peer | Downstream / peer | Channel | Pattern | Notes |
|----------|------------|---------|---------|-------|
| ...      | ...        | ...     | ...     | ...   |

```
