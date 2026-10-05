# Architecture – Advise Mode

Guidance for architectural questions, greenfield design, refactors, and mentoring, as text. A question that needs a full context map or a discovery session moves into the mode that owns it (`strategic-design`, `event-storming`) rather than answering shallower. Glossary operationalization is the `andthen:describe` skill in `--mode domain`.

## Rules

Every recommendation names the framework or principle driving it ("Per SDP (Martin) …", "Per Ford/Richards' scalability driver …"), the trade-off (what is gained, what is lost), and the counter-argument or the condition under which the principle bends.

Farley's complexity tools are the vocabulary for naming what a design costs: modularity, cohesion, separation of concerns, information hiding, and coupling. Two Farley probes supply the evidence:

- What must be built or mocked to test the component. Test friction is coupling, though a deep module is still tested through its interface (the calibration's testability trap).
- Which dependency lengthens the path from a change to confident production. Deployable is not releasable, because a business release gate is not coupling.

Lenses:

- **CUPID** (Dan North) is an assessment lens: rate each property 1–5 with concrete observations.
- **DDD**, strategic and tactical, on the calibration's Boundary and Domain terms and its traps.
- **Deep modules** (Ousterhout) for in-process module, class, and public-API questions, on the calibration's Deep Modules terms.
- **Locality of Behaviour** (Carson Gross) weighs against separation of concerns at the same scope, on the calibration's hidden-behaviour trap.

## Output

The answer in its project context, with concrete examples from this codebase and its constraints. For a design question, the viable approaches assessed with the lenses, the recommendation, and how to validate it. Then its implications and direct next steps, with the `andthen:decide` skill offered when the answer settles a choice that binds beyond the work or is costly to reverse.
