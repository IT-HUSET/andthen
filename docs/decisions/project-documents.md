# Decisions: Project documents

Rationale, evidence, history, and reopen conditions for the **Project documents** bullets in [DECISIONS.md](../DECISIONS.md) § Still Current. Each decision is stated there; a section here holds only what would not fit its one line.

## Durable documents carry no size ceilings

A size count's blindness is why the ceilings, their `hard` form, `prune`, and the admission regexes all retired. A part read never applies to a document a task is checked against, because there it misses silently; it suits history or user-facing reference that pruning would damage. Sharding is by hand, one pointer line per shard, with no verb or size check, and a shard is opened when the task names its topic.

The numbers that are load-bearing live where they are used: the FIS oversize threshold in `plan` and the authoring guidelines, the 200-character glossary row rule in the Ubiquitous Language header.

Reopens on a document-growth failure the read-whole convention did not prevent, or a part read that missed what the task needed.

## The Index entry catalog carries no Product Backlog or Changelog entry

No skill reads a backlog: a deferral stays in its PRD's `Scope > Out of Scope`, a put-off fix in Tech Debt. A changelog would need a completion clause in `exec-plan` and `implement-fix`, not an Index entry.

## No `Stack` document

Adopting projects showed versions drifting from the lockfile within weeks. Where its content goes instead: a library choice with a reason is a Decisions row, a rejected one a Product non-goal.

Reopens if a polyglot repository with no single manifest needs an inventory the Architecture document cannot carry.

## Tracker setup is first-use, not an `init` gate

The skills that need the backend first: a reader handed a non-GitHub URL, and `tracker triage` or `tracker publish` with no GitHub remote. Under `Backend: none`, `tracker publish` and `tracker triage` name the line to change and run no `gh` flow.

Reopens if a project needs the backend declared before any skill sees a URL.

## `init` wires the rules and role agents in prose; unattended setup places them by script

`wire.py` re-derived what the agent already has in context. Its reopen condition, an unattended `init` needing a machine-checkable wiring result, was met on 2026-11-10 for unattended environments: ADR-030 gives the setup script user-level placement, limited to what needs no merge, with the install's exit code as the result. Attended setup keeps the prose.

Reopens if unattended placement needs a merge the setup script refuses (ADR-030 § Reopens).

## The architecture-model schema is for code-structure graphs only

A JSON model carries its own schema. ADR-029 holds the one-record rule and its rationale.
