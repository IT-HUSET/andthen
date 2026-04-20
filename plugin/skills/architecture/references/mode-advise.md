# Architecture — Advise Mode

Design or refactor guidance for architectural questions, greenfield systems, service boundaries, bounded contexts, and pattern selection. Covers both **Design** (creating new architectures, making significant decisions) and **Advisory** (answering questions, mentoring refactors).

Optimize for sound decisions, clear boundaries, and guidance a team can implement and operate.

**Supporting references** (load on demand based on the question): `anti-patterns.md`, `package-principles.md`, `connascence.md`, `fitness-functions.md`, `decomposition.md`, `farley-framework.md`.

## Decision-Making Process

1. **Project context**: read `CLAUDE.md`, project docs, and existing ADRs for constraints, standards, and established patterns.
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

## Core Competencies

### Architectural Analysis & Design

- run structured trade-off analysis using cost, risk, and technical-debt lenses
- apply layered, Clean, hexagonal, event-driven, CQRS, event sourcing, and reactive patterns in context
- define clear domain boundaries, bounded contexts, and aggregate responsibilities
- use C4, UML, or other architecture descriptions when they clarify the decision

### System Design

- evaluate monolith vs modular monolith vs microservices based on team, complexity, and organizational factors
- design synchronous and asynchronous integration patterns, including event-driven flows and API gateways where justified
- reason about concurrency, consistency, availability, and partition-tolerance trade-offs
- choose caching, storage, and communication patterns appropriate to the workload, including application, distributed, and CDN caching

### API Design

- define explicit API contracts and documentation
- choose REST, GraphQL, gRPC, or event-driven interfaces based on use case and team fit
- optimize for usability, discoverability, and change management, using OpenAPI or similar specifications when useful
- handle versioning, status codes, validation, rate limiting, and CORS deliberately

### Database & Data Access

- choose SQL or NoSQL based on data shape, access patterns, and consistency needs
- design schemas around the domain model rather than incidental implementation details
- use repositories or similar patterns when they improve boundary clarity
- plan constraints, validation, indexing, transactions, and rollback behavior up front
- use CQRS when read and write concerns materially diverge
- consider event sourcing when change history is central to the domain
- consider brokers such as Kafka or RabbitMQ when asynchronous integration is operationally justified
- plan schema and data versioning so change is manageable over time

### Service Granularity & Modularity

- define service boundaries around business capabilities, not just technical layers
- apply single-responsibility thinking at service and module boundaries
- evaluate the organizational and operational forces behind service splits
- optimize for high cohesion, low coupling, and independent change
- use service discovery, gateways, or meshes only when their operational cost is justified

### Quality, Performance, and Operations

- use SOLID and/or CUPID as design lenses
- choose the simplest effective scaling strategy: horizontal, vertical, load balancing, and targeted optimization
- account for security, observability, operability, and resilience in major decisions
- treat performance characteristics and failure modes as first-class design concerns

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

- Composable: _/5 — dependencies, coupling, reusability
- Unix Philosophy: _/5 — single responsibility, scope, granularity
- Predictable: _/5 — consistency, failure modes, operational clarity
- Idiomatic: _/5 — convention adherence, team fit, cognitive load
- Domain-based: _/5 — business alignment, domain expression, ubiquitous language

Use CUPID to compare options, identify weak properties, give the team shared vocabulary, and target refactoring.

## Domain-Driven Design

Use DDD to reduce accidental complexity, sharpen boundaries, and create a shared language between business and technical teams.

### Strategic Patterns

**Bounded Contexts**
- each context should have a clear business purpose
- terms should be consistent within the context
- boundaries often align with team structure and ownership
- each context should own its model and schema when possible
- context size should remain manageable by one team

**Context Mapping** — design context relationships explicitly:
- Shared Kernel: shared code or model, used sparingly
- Customer/Supplier: downstream depends on upstream
- Conformist: downstream adopts upstream's model
- Anti-Corruption Layer: translate between incompatible models
- Open Host Service: stable API for multiple consumers
- Published Language: shared integration language or format

**Core vs Supporting vs Generic**
- invest most in the core domain
- keep supporting subdomains fit for purpose
- avoid over-engineering generic subdomains; prefer off-the-shelf where sensible

### Tactical Building Blocks

| Block | Identity | Mutability | Purpose |
|-------|----------|------------|---------|
| **Entity** | Unique ID | Mutable | Object whose identity persists over time |
| **Value Object** | By value | Immutable | Object defined by attributes, not identity |
| **Aggregate** | Root ID | Via root only | Consistency boundary and transaction unit |
| **Domain Service** | - | Stateless | Business operation that does not naturally belong to one entity |
| **Domain Event** | - | Immutable | Fact that something important happened |
| **Repository** | - | - | Collection-like interface for aggregate access |

### DDD Integration with Modern Architecture

**Microservices + DDD**: align service boundaries with bounded contexts; let each service own its model and data; use domain events for inter-service communication when decoupling matters; use anti-corruption layers at external or legacy boundaries.

**Event-Driven + DDD**: let domain events drive behavior where the domain supports it; use event sourcing only when the audit trail and temporal model justify the cost; use CQRS when read and write models differ materially; use sagas or process managers for long-running coordination.

**Clean Architecture + DDD**: keep DDD building blocks in the domain layer; let the application layer orchestrate domain operations; keep infrastructure concerns at the edge; preserve the dependency rule so the domain stays clean.

### DDD Anti-Patterns

- **Anemic Domain Model**: domain objects contain only data; move business logic into entities or value objects
- **Leaky Abstraction**: technical concerns pollute domain concepts; restore clean boundaries and dependency inversion
- **Context Explosion**: too many tiny contexts; start broader and split only when real forces justify it
- **Generic Subdomains as Core**: over-investment in undifferentiating areas; prefer simpler or off-the-shelf solutions
- **Big Ball of Mud**: no clear domain boundaries; define explicit contexts and dependency rules

### DDD Assessment Questions

Strategic: are bounded contexts clearly defined and appropriately sized? Does the context map reflect actual business relationships? Is investment proportionate across core, supporting, and generic subdomains? Do team boundaries reinforce the context boundaries?

Tactical: are domain concepts clearly expressed in the model? Do aggregates enforce business invariants correctly? Is the ubiquitous language used consistently? Are domain events capturing meaningful business occurrences? Is business logic kept in domain objects rather than drifting into application services?

## Modern Architecture Patterns

### Cloud-Native & Distributed Systems

- evaluate microservices vs modular monolith based on team size, complexity, and organizational readiness
- use event-driven architecture for asynchronous or resilience-sensitive workflows when the domain supports it
- consider serverless for suitable event processing, API, and batch workloads
- use API gateways only when the centralization benefit justifies the added layer

### Performance & Scalability

- choose horizontal vs vertical scaling based on actual workload characteristics
- use multi-layer caching only when it improves performance without corrupting correctness
- consider CQRS, event sourcing, polyglot persistence, and read replicas only when justified
- make load balancing and failover part of the design, not an afterthought

### Resilience & Observability

- use circuit breakers, retries, timeouts, and backoff deliberately to prevent cascading failure
- define metrics, logging, tracing, and alerting around critical paths
- include observability in architecture decisions, not only implementation details

## Common Anti-Patterns to Detect

- **God Objects**: responsibilities concentrated in one class or module; split by responsibility and boundary
- **Circular Dependencies**: direct or indirect mutual dependency; introduce a stable abstraction or boundary
- **Tight Coupling**: components cannot change independently; reduce knowledge and invert dependencies
- **Framework Coupling**: business logic tied to framework constructs; restore architectural boundaries
- **Anemic Domain Model**: domain objects have no behavior; move business logic into the domain
- **Inappropriate Intimacy**: modules know too much about each other's internals; enforce encapsulation
- **Feature Envy**: logic belongs closer to the data or behavior it depends on; move it to the proper owner
- **Distributed Monolith**: services are split physically but not operationally; reduce synchronous coupling or consolidate
- **Chatty Interfaces**: excessive cross-boundary back-and-forth; coarsen APIs or restructure ownership
- **Shared Database**: multiple services write the same store directly; separate ownership or add integration boundaries
- **Big Ball of Mud**: boundaries are absent or unenforced; re-establish explicit domains and dependency rules

## Codebase Analysis Approach

When analyzing a codebase as part of advisory work:

- use `tree -d` and `git ls-files | head -250` for a fast structural overview
- identify likely bounded contexts by business capability, not only folder names
- check dependency direction for clean-architecture or layering violations
- inspect layer leaks such as business logic in controllers or infrastructure concerns in the domain
- map integration points: what talks to what, over which protocols, and with what coupling
- spot anti-patterns and name them explicitly

## ADR Template

```markdown
# ADR-{N}: {Short Title}

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
What is the issue motivating this decision?

## Decision
What are we doing?

## Consequences
What becomes easier or harder?

## Alternatives Considered
1. **{Alt}** — rejected: {reason}

## Project Compliance
How does this align with project-specific architectural guidelines?
```

## Report Contents

### Design sub-mode output

1. **Project Context Assessment**: relevant project rules, domain constraints, team factors, and current system landscape.
2. **Problem Analysis**: the architectural challenge plus key functional and non-functional requirements.
3. **Solution Options**: 2-3 viable approaches assessed with relevant lenses such as CUPID, DDD, cost, and operational complexity.
4. **Trade-off Analysis**: risks, complexity, maintainability, performance, technical debt, and mitigation.
5. **Recommendation & Implementation**: recommendation, implementation roadmap, success criteria, monitoring approach, and ADR when appropriate.

### Advisory sub-mode output

Structured answer with framework attribution, trade-offs, and counter-arguments. Expand acronyms and briefly explain named frameworks if they are not standard for the expected audience. Use direct next steps, concrete examples, and ASCII diagrams when helpful.
