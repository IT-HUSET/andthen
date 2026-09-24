# Testing Strategy

The project's testing contract: which levels it uses, how its tests are built, and what must be proven before merge.

## Where it comes from

The `Testing Strategy` document (**Project Document Index**; default `docs/TESTING-STRATEGY.md`) is the one source. **Read it before authoring or planning tests.** The read is unconditional, and a convention it already states is never re-derived from general testing theory. It names levels, fixtures, the before-merge bar, and this project's gotchas – never commands; those stay in the `Key Dev Commands` document per `verification-evidence.md`.

## When the document does not answer

A missing document, or one that is silent on the level or convention in question, is named the same way `verification-evidence.md` names a missing command: apply the distilled defaults below, and wherever the test work is reported say what was missing and that distilled defaults stood in for it.

Generic defaults applied silently read to the next agent as decisions this project made, which is how a codebase acquires two test styles nobody chose.

## Distilled defaults

Level follows trust boundaries, not file count. A **trust boundary** is a line you do not own the other side of at runtime – filesystem, DB engine, third-party API, browser event loop, OS. Crossing none is a unit test, one at a time is integration, many (usually with a browser or the full stack) is E2E. The default is the sociable test – real collaborators, doubles only at trust boundaries – with behavior that lives at a boundary (a query, a file format) proved against the real dependency and an HTTP API through a contract test, since a fake of it proves the fake. E2E is reserved for journeys the business cannot ship without, because they cost minutes and rot fastest.

A test whose label and whose boundaries disagree is slow, fragile, or proves nothing:

- **"Integration" that is E2E** – Crosses services, a browser, or a queue. Split: contract tests at each boundary plus per-service integration.
- **"E2E" that is unit** – Asserts a value that never leaves the backend. Demote.

Rank what to cover by blast radius of a silent failure and by change frequency – a global coverage percentage as a target is a vanity metric, while uncovered changed lines are a real signal. Refuse coverage theatre: did-not-throw tests, line coverage with no assertion on output semantics, and mock-heavy tests that stay green when their collaborators break.
