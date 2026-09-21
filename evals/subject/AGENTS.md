# AI Coding Agent Instructions for working with Reporter

## Project Overview

Reporter is a command-line tool that turns a delimited ledger file into a CSV report a spreadsheet opens directly. Python 3.9+ and the standard library, one package under `src/reporter/`, no packaging step. Read `docs/PRODUCT.md` and `docs/ARCHITECTURE.md` for the depth.

## Project Document Index

Each document here is read whole whenever its trigger matches, so keep them short and trim stale entries when you append. Entry names are how skills refer to these documents; keep them stable.

- **Product** – `docs/PRODUCT.md`
  Vision, non-goals, and the proportionality facts. Read before clarifying or specifying a feature – a feature anchors to it, never contradicts it.
- **Specs & Plans** – `docs/specs/<feature>/`
  A PRD, `plan.json`, and one FIS per story, co-located per feature. Read the governing FIS before implementing; it is the artifact execution updates.
- **Architecture** – `docs/ARCHITECTURE.md`
  Module boundaries, the layering rule, and data flow. Read for architecture-touching changes.
- **Decisions** – `docs/DECISIONS.md`
  Decision index and Still Current notes; points into `docs/adrs/`. Read before proposing or changing a design choice; a settled one is not reopened without new evidence.
- **ADRs** – `docs/adrs/`
  Architecture Decision Records. Read the record a decision cites before revisiting it; add one when a new decision is made.
- **Key Dev Commands** – `docs/KEY_DEVELOPMENT_COMMANDS.md`
  Run and test commands, `fast` and `full` tiers. Read before running verification; update when a command changes.
- **Testing Strategy** – `docs/TESTING-STRATEGY.md`
  Levels in use, conventions, the before-merge bar, known gotchas. Read before authoring a test; update when a convention changes.
- **Learnings** – `docs/LEARNINGS.md`
  Known traps, one bullet each. Read at task start; add a bullet when bitten by a non-obvious failure.
- **Tech Debt** – `docs/TECH-DEBT-BACKLOG.md`
  Known technical debt by severity. Read when working in an area that has a listed item; add an entry when deferring a fix.
- **Agent Temp** – `.agent_temp/`
  Temporary agent workspace. Write scratch artifacts here; never ship from it.

## Project-Specific Guidelines and Rules

### Project Guidelines and Standards

- Standard library only – no third-party runtime or test dependency, so the tool installs by copying the tree.
- Every command in the Key Dev Commands document runs from the repository root.

### Do Not / Never

- Never import upward or sideways across the layers in `docs/ARCHITECTURE.md` – the layering is what keeps the exporter usable without the command line.
- Never reach into another module's private names; extend its public surface instead.
- Never let a bad ledger reach the user as a traceback – the command line reports input errors and exits 2.

## Key Development Commands

Tests run in two tiers (`fast`, `full`) plus a run-one-test row, declared in `docs/KEY_DEVELOPMENT_COMMANDS.md`.
