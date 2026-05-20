# Architecture – Advise Mode

Design or refactor guidance for architectural questions, greenfield systems, service boundaries, bounded contexts, and pattern selection. Covers both **Design** (creating new architectures, making significant decisions) and **Advisory** (answering questions, mentoring refactors).

Optimize for sound decisions, clear boundaries, and guidance a team can implement and operate.

**Supporting references** (load on demand based on the question): `anti-patterns.md`, `package-principles.md`, `connascence.md`, `fitness-functions.md`, `decomposition.md`, `${CLAUDE_PLUGIN_ROOT}/references/farley-framework.md`, `ousterhout-modules.md` (for in-process module, class, and API design questions), `ddd.md` (for bounded contexts, aggregates, domain events, Event Storming, and Hexagonal/CQRS/Event Sourcing in a DDD setting).

## Decision-Making Process

1. **Project context**: read `CLAUDE.md` / `AGENTS.md`, project docs, and existing ADRs for constraints, standards, and established patterns.
2. **Business context**: understand functional and non-functional requirements, team capability, organizational constraints, and the current system landscape.
3. **Options**: present 2-3 viable approaches for this project.
4. **Trade-offs**: compare complexity, maintainability, performance, cost, technical debt, and team fit.
5. **Recommendation**: give a clear decision, rationale, implementation guidance, and risk mitigation.
6. **Compliance**: ensure the recommendation aligns with project-specific architectural rules.
7. **Validation**: define measurable success criteria, operational signals, and monitoring expectations.

## Operating Sub-Modes

### Design (greenfield or significant decisions)

- run explicit trade-off analysis
- generate multiple viable options
- create an ADR for significant decisions
- design with DDD and appropriate modern architecture patterns
- outline implementation milestones and validation

For structured option comparison with weighted criteria, chain into the `trade-off` mode (`--mode advise,trade-off`).

### Advisory (questions, refactors, mentoring)

- answer with concrete examples grounded in the codebase and constraints
- explain implications, not just conclusions
- guide refactoring and decomposition
- keep guidance pragmatic and project-aware

## Every Recommendation Must

1. Name the framework or principle driving it (e.g. "Per SDP (Martin)..." or "Ford/Richards' disintegration driver #3...")
2. Explain the trade-off (what you gain, what you lose)
3. Cite counter-arguments or when the principle should bend

## CUPID Assessment Lens

Use CUPID (https://cupid.dev/) as an assessment lens, not a pass/fail checklist.

| Property | Question | Focus |
|----------|----------|-------|
| **C**omposable | Can parts be combined cleanly? | Coupling, contracts, extensibility |
| **U**nix Philosophy | Does each component do one thing well? | Scope, focused services, granularity |
| **P**redictable | Is behavior consistent and unsurprising? | Failure modes, consistency, data flow |
| **I**diomatic | Does it follow established patterns? | Convention, team fit, cognitive load |
| **D**omain-based | Does structure reflect business domains? | Boundaries, language, business alignment |

Rate each property 1-5 with concrete observations when doing a CUPID assessment:

- Composable: _/5 – dependencies, coupling, reusability
- Unix Philosophy: _/5 – single responsibility, scope, granularity
- Predictable: _/5 – consistency, failure modes, operational clarity
- Idiomatic: _/5 – convention adherence, team fit, cognitive load
- Domain-based: _/5 – business alignment, domain expression, ubiquitous language

Use CUPID to compare options, identify weak properties, give the team shared vocabulary, and target refactoring.

## Domain-Driven Design

Use DDD to sharpen boundaries and create shared language between business and engineering. **Strategic** design picks bounded contexts and their relationships; **tactical** design shapes the model inside one.

**Quick reference:**

| Building block | Purpose |
|---|---|
| **Entity** | Identity persists over time; mutable |
| **Value Object** | Defined by attributes; immutable; prefer when lifecycle doesn't matter |
| **Aggregate** | Consistency boundary; one transaction = one aggregate |
| **Domain Event** | Past-tense fact published inside the bounded context |
| **Domain Service** | Stateless business logic with no natural entity home; contains branching business rules |
| **Application Service** | Orchestrates a use case (load aggregate → invoke domain op → persist); no branching business rules |
| **Repository** | Collection-like interface over aggregate roots only |

**Assessment questions** – Strategic: are bounded contexts clearly defined, appropriately sized, and owned by at most one team? Does the context map reflect real relationships? Is investment proportionate across core / supporting / generic? Tactical: do aggregates enforce true invariants (not navigational convenience)? Are domain events distinguished from integration events? Is business logic kept in domain objects rather than drifting into application services? Is the ubiquitous language visible in code?

**For full depth – four aggregate design rules, domain vs. integration events, the 9-pattern context-mapping catalog with selection guidance, Event Storming, Bounded Context Canvas, Hexagonal as the bounded-context skeleton, CQRS/Event Sourcing decision criteria, domain vs. application service distinction, module layout, and DDD anti-patterns – load `ddd.md`.** Cross-link to the `andthen:ubiquitous-language` skill for glossary operationalization and `andthen:clarify` for Event Storming.

## Ousterhout Module-Design Lens

For questions about **in-process** module, class, or public-API design (not service boundaries), load `ousterhout-modules.md` and apply its heuristics alongside CUPID and DDD:

- **Deep vs. shallow modules** – prefer a small interface over a powerful implementation; beware "classitis" (many trivial modules each with near-equivalent interface and implementation complexity).
- **Information leakage** – each non-trivial design decision (format, protocol, data layout, algorithm) should be reflected in exactly one interface.
- **Different layer, different abstraction** – a layer that only forwards calls with the same parameters is not earning its existence.
- **Pull complexity downward** – when complexity must live somewhere, keep it in the implementation; a simpler interface is worth a more complex implementation.
- **Define errors out of existence** – prefer abstractions that make error cases disappear over abstractions that require handling them, when the "no-op" case is legitimate state (not a masked fault).
- **Design it twice** – for any non-trivial new API, require a genuinely different alternative considered and rejected with reason.

**Reconciling with CUPID Unix Philosophy**: "prefer fewer, deeper modules" does not contradict "do one thing well." Unix Philosophy is about focused *scope*, not small *size* – `grep` does one thing and is a deep module. Use CUPID to check whether the module has a single coherent purpose; use Ousterhout to check whether its interface is simpler than its implementation. Both must hold.

**Boundary with Speculative Generality**: Ousterhout's "general-purpose interfaces" means *slightly* more general than one caller, not speculative. When only one consumer exists and no second is visible, the Speculative Generality anti-pattern (`anti-patterns.md`) wins.

This lens is **complementary** to CUPID and DDD, not a replacement: apply it to within-service design, not to service decomposition. For altitude and limits, see `ousterhout-modules.md`.

Common anti-patterns: see [`anti-patterns.md`](anti-patterns.md) for the full catalog of anti-patterns to detect during advisory work.

## Codebase Analysis Approach

When analyzing a codebase as part of advisory work:

- use `tree -d` and `git ls-files | head -250` for a fast structural overview
- identify likely bounded contexts by business capability, not only folder names
- check dependency direction for clean-architecture or layering violations
- inspect layer leaks such as business logic in controllers or infrastructure concerns in the domain
- map integration points: what talks to what, over which protocols, and with what coupling
- spot anti-patterns and name them explicitly

## ADR Template

See `adr-template.md` for the canonical ADR template.

## Report Contents

### Design sub-mode output

1. **Project Context Assessment**: relevant project rules, domain constraints, team factors, and current system landscape.
2. **Problem Analysis**: the architectural challenge plus key functional and non-functional requirements.
3. **Solution Options**: 2-3 viable approaches assessed with relevant lenses such as CUPID, DDD, cost, and operational complexity.
4. **Trade-off Analysis**: risks, complexity, maintainability, performance, technical debt, and mitigation.
5. **Recommendation & Implementation**: recommendation, implementation roadmap, success criteria, monitoring approach, and ADR when appropriate.

### Advisory sub-mode output

Structured answer with framework attribution, trade-offs, and counter-arguments. Expand acronyms and briefly explain named frameworks if they are not standard for the expected audience. Use direct next steps, concrete examples, and ASCII diagrams when helpful.
