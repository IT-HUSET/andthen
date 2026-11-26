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

## The critical-rules starter's comment rule is one test, and `simplify-code` enforces it

Sources, cited from memory and not re-checked against the books.
The test is Ousterhout's (*A Philosophy of Software Design*, "Comments should describe things that aren't obvious from the code"): a comment someone could write from the code beside it adds nothing.
Deleting such a comment is Beck's Delete Redundant Comments tidying (*Tidy First?*), Martin's redundant and noise comments (*Clean Code*, ch. 4), and DRY applied to comments (Hunt and Thomas, *The Pragmatic Programmer*).
Martin and Ousterhout part on interface comments: Martin would extract a function to avoid a comment, Ousterhout holds that an interface comment is part of a deep module.
The starter already prefers deep modules, so the rule keeps a contract the signature leaves open and carries no "say it in code first" sentence.

Evidence, 2026-11-20, from AndThen Studio (Dart): 6,012 of 45,054 non-test lines were comments, about 170 of them `/// Creates a …` constructor docs.
Studio had carried a far longer comment rule set since its second commit, and its over-commenting followed that rule set's own "DO document public members" and one-sentence-summary tier, so the cause there was a conflict inside a long rule, not a missing one.
An `oracle` sample put the comments the test removes at roughly a tenth of the total; the multi-line blocks carry contracts and reasons and stay.

Probe: `simplify-code --auto` over three Studio files holding 538 comment lines and 24 restating constructor docs, on scratch clones, the project's 1,700-test fast tier green in every run.
With the text before the lens, one run deleted none and ended at 563 lines, having extended a doc-comment table that duplicates an enum.
With the lens as shipped, two runs ended at 513 and 495 lines; every removed line restated its declaration, and one run kept 17 constructor docs in an exported file because Studio's guideline requires full docs there.
A run of an earlier wording kept restating docs for being "the codebase's dominant pattern", which is why the lens says that is no reason.

The starter is worded for the writer and the lens for the cleaner ("Delete a comment…"), because a deletion imperative in the starter plus the Boy Scout tidy rule would have every run delete comments in files it only reads.
A three-sentence starter rule was cut to one on the maintainer's word that the file was already too long.
Its examples of a contract, the doc-comment qualifier, and the reason clause stay in the lens, and the writer-side ban on plan and report IDs went, since Studio held about 10 such lines.
No run has measured the starter's rule against the one line it replaced ("Comments explain *why*, not *what*").

Reopens on a run where the lens deletes a comment that carried a reason, or on a rule-ablation run showing the starter's rule changes nothing a model writes.

## `init` wires the rules and role agents in prose; unattended setup places them by script

`wire.py` re-derived what the agent already has in context. Its reopen condition, an unattended `init` needing a machine-checkable wiring result, was met on 2026-11-10 for unattended environments: ADR-030 gives the setup script user-level placement, limited to what needs no merge, with the install's exit code as the result. Attended setup keeps the prose.

Reopens if unattended placement needs a merge the setup script refuses (ADR-030 § Reopens).

## The architecture-model schema is for code-structure graphs only

A JSON model carries its own schema. ADR-029 holds the one-record rule and its rationale.
