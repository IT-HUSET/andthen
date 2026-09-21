# Architecture – Advise Mode

Guidance for architectural questions, greenfield systems, service boundaries, bounded contexts, and pattern selection. Two sub-modes: **Design** (new architectures, significant decisions – options with their trade-offs, an ADR when the decision is significant, implementation milestones and validation) and **Advisory** (questions, refactors, mentoring – concrete examples grounded in the codebase and its constraints, implications and not only conclusions). A question that needs weighted comparison, a full context map, or a discovery session moves into the mode that owns it (`trade-off`, `strategic-design`, `event-storming`) rather than answering shallower; glossary operationalization is the `andthen:describe` skill in `--mode domain`.

## Every Recommendation

Names the framework or principle driving it ("Per SDP (Martin) …", "Ford/Richards' disintegration driver #3 …"), the trade-off (what is gained, what is lost), and the counter-argument or the condition under which the principle bends. Farley's complexity tools – modularity, cohesion, separation of concerns, information hiding, coupling – are the vocabulary for naming what a design costs.

## Lenses

- **CUPID** (Dan North) is an assessment lens, not a pass/fail checklist: rate each property 1–5 with concrete observations, then use the scores to compare options, find weak properties, give the team shared vocabulary, and target refactoring.
- **DDD** sharpens boundaries and the shared language – strategic (contexts clearly defined, sized, and owned by at most one team; a context map that reflects real relationships; investment proportionate across core / supporting / generic) and tactical (aggregates enforcing true invariants rather than navigational convenience, domain events distinct from integration events, business logic in the domain rather than application services, the ubiquitous language visible in code). The sizing, the nine context-mapping patterns, the CQRS and event-sourcing criteria, and the DDD traps behind these are in `architecture-calibration.md`.
- **Ousterhout's module-design lens** applies to in-process module, class, and public-API questions as the calibration scopes it – complementary to CUPID and DDD, never a replacement. Two of its principles inform recommendations rather than test them: pull complexity downward (simpler *for us* is no win if it multiplies cognitive load across N callers) and general-purpose interfaces (somewhat more general than one caller, never all conceivable callers).

## Report Contents

**Design sub-mode**: the architectural challenge in its project context, 2-3 viable approaches assessed with the lenses, their trade-off analysis, then the recommendation with an implementation roadmap and an ADR when appropriate.

**Advisory sub-mode**: structured answer with framework attribution, trade-offs, counter-arguments, and direct next steps.
