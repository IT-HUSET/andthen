# Architecture – Advise Mode

Two sub-modes: **Design** for new architectures and significant decisions, **Advisory** for questions, refactors, and mentoring. A question that needs weighted comparison, a full context map, or a discovery session moves into the mode that owns it (`trade-off`, `strategic-design`, `event-storming`) rather than answering shallower; glossary operationalization is the `andthen:describe` skill in `--mode domain`.

## Every Recommendation

Names the framework or principle driving it ("Per SDP (Martin) …", "Per Ford/Richards' scalability driver …"), the trade-off (what is gained, what is lost), and the counter-argument or the condition under which the principle bends. Farley's complexity tools – modularity, cohesion, separation of concerns, information hiding, coupling – are the vocabulary for naming what a design costs. Two Farley probes supply the evidence: what must be built or mocked to test the component (test friction is coupling, though a deep module is still tested through its interface – the calibration's testability trap), and which dependency lengthens the path from a change to confident production (deployable is not releasable: a business release gate is not coupling).

## Lenses

- **CUPID** (Dan North) is an assessment lens, not a pass/fail checklist: rate each property 1–5 with concrete observations.
- **DDD**, strategic and tactical, on the calibration's Boundary and Domain terms and its traps.
- **Deep modules** (Ousterhout) for in-process module, class, and public-API questions, on the calibration's Deep Modules terms.

## Report Contents

**Design sub-mode**: the architectural challenge in its project context, 2-3 viable approaches assessed with the lenses, their trade-off analysis, then the recommendation with an implementation roadmap, how to validate it, and an ADR when the decision is significant.

**Advisory sub-mode**: the answer with concrete examples from this codebase and its constraints, its implications, and direct next steps.
