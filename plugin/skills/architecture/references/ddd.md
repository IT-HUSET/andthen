# Domain-Driven Design – Architecture Reference

Design, evaluate, and evolve bounded contexts and the models inside them. Strategic + tactical DDD; sources at end.

Operates at C4 **Context / Container / Component** level – strategic design picks bounded contexts and their relationships; tactical design shapes the model inside one. Complements the Ford/Richards decomposition lens and the Ousterhout in-process lens – use all three where they fit.

Pure in-process class/module API design: `ousterhout-modules.md`. Low-level dependency analysis: `connascence.md` / `package-principles.md`.

## Table of Contents
- [1. Strategic Design](#1-strategic-design)
- [2. Tactical Design](#2-tactical-design)
- [3. Architecture Integration](#3-architecture-integration)
- [4. Discovery Techniques](#4-discovery-techniques)
- [5. Ubiquitous Language – Operationalizing](#5-ubiquitous-language--operationalizing)
- [6. Functional DDD (Alternative Lens)](#6-functional-ddd-alternative-lens)
- [7. DDD Anti-Patterns](#7-ddd-anti-patterns)
- [8. When to Bend the Rules](#8-when-to-bend-the-rules)
- [Sources](#sources)

---

## 1. Strategic Design

### 1.1 Subdomains and Investment

Three types (Evans; Khononov ch. 1):

- **Core** – the differentiated business capability; where competitive advantage lives. Invest maximally: full tactical DDD, best engineers, richest model.
- **Supporting** – necessary but undifferentiated. Keep fit for purpose with simpler patterns (Active Record, transaction script, thin domain model). Don't over-model.
- **Generic** – commodity (auth, billing, CMS). Prefer off-the-shelf; integrate, don't build.

**Core Domain Chart** (DDD Crew, Nick Tune): plot each subdomain on *Business Differentiation* × *Model Complexity*. High-differentiation + high-complexity = Core. Low-differentiation + low-complexity = Generic. The value is the cross-discipline conversation it triggers with product.

**Tactical pattern selection by subdomain** (Khononov ch. 10): Core → rich aggregates + domain events; Supporting → pragmatic patterns; Generic → don't model.

### 1.2 Bounded Contexts

A bounded context is a **linguistic boundary** within which each term has one unambiguous meaning. It is owned by at most one team, carries its own model and schema, and enforces its own ubiquitous language. Context maps are **logical** – they apply equally to microservices and to modules inside a modular monolith.

Sizing heuristics:
- One team → one or more contexts; never split a context across teams. Upper bound on contexts per team follows cognitive-load guidance (2–3 low-complexity domains per team – see `decomposition.md` Sizing Heuristics).
- If the same term is used two ways, you have two contexts (or a failure to distinguish them).
- If a single aggregate becomes the "God object" of the context, the context is probably too broad.

### 1.3 Context-Mapping Pattern Catalog

Eight canonical patterns from Evans, plus Big Ball of Mud as a quarantine strategy added by the DDD Crew community (`context-mapping`). Move toward the top of the table when teams are aligned and models are stable; toward the bottom when teams are distant, models are incompatible, or the upstream cannot be negotiated with. *Acronyms: ACL = Anticorruption Layer; OHS = Open Host Service.*

| Pattern | Coupling | Team relationship | Choose when |
|---|---|---|---|
| **Partnership** | High | Mutual, synchronized releases | Teams succeed or fail together; shared fate on a specific capability. *Tension: reduces deployment independence – use sparingly.* |
| **Shared Kernel** | High | Shared ownership of a model subset | Closely related contexts, stable shared model, strong communication; keep the kernel small. |
| **Customer/Supplier** | Negotiated | Upstream/downstream, downstream has leverage | Downstream needs factor into upstream planning. |
| **Conformist** | Medium | Upstream authoritative | Upstream is external or can't be influenced; simplicity wins over autonomy. |
| **Anticorruption Layer** | Medium | Downstream protects itself | Upstream model is hostile, legacy, or semantically incompatible. |
| **Open Host Service** | Low | Upstream serves many | Upstream publishes a stable API for multiple consumers; standardize once. |
| **Published Language** | Low | Shared exchange format | Common integration format (schemas, event envelopes); often pairs with OHS. |
| **Separate Ways** | None | Explicit non-integration | Integration cost exceeds value; duplication is cheaper and faster. |
| **Big Ball of Mud** _(quarantine, not Evans canon)_ | Variable | Quarantine | Legacy or entangled system; never let its model contaminate neighbors – wrap with an ACL. |

### 1.4 Team Topology Alignment

Context-mapping patterns correspond to Team Topologies interaction modes (Kaiser, *Architecture for Flow*; Tune):

| Context-map pattern | Team Topologies analogue |
|---|---|
| Partnership | Closely collaborating stream-aligned teams |
| Customer/Supplier | X-as-a-Service with negotiation |
| Conformist | X-as-a-Service, no negotiation |
| ACL | Platform team owns translation |
| OHS + Published Language | Platform team's stable API |
| Separate Ways | Fully independent stream-aligned teams |

When team boundaries cut across context boundaries (Conway's Law violated), the distributed monolith is the predictable result.

---

## 2. Tactical Design

### 2.1 The Four Aggregate Design Rules (Vernon)

From *Effective Aggregate Design* I–III (dddcommunity.org) and IDDD ch. 10.

**Rule 1 – Model true invariants in consistency boundaries.** An invariant is a business rule enforced *at commit*. If the rule only needs to hold eventually, it is not a reason to widen the aggregate.

**Rule 2 – Design small aggregates.** Observation: most aggregates are a single root with value-typed properties. Large clusters usually reflect false invariants or navigational convenience, not real consistency needs. If you cannot state the invariant that forces two objects into one transaction, they belong in separate aggregates.

**Rule 3 – Reference other aggregates by identity only.** Hold the other aggregate's ID (typically wrapped in a Value Object), not a direct object reference. Direct references allow unintended modifications and force co-loading.

**Rule 4 – Use eventual consistency outside the aggregate boundary.** When a business rule spans aggregates, publish a domain event and let a subscriber update the other aggregate in a separate transaction. Vernon's test: *"if another user or system could reasonably handle this update, eventual consistency is fine here."*

**Discovery heuristic** (community practice, extends Rule 2): list the aggregates modified in one use case; for each grouping, name the true invariant that requires them in one transaction. No invariant → break the cluster.

### 2.2 Entity vs. Value Object

Prefer Value Objects unless continuity demands otherwise.

- **Integer test**: replace the concept with an integer. If you care that "5" here is the *same* "5" there, it is an Entity. If two instances with identical attributes are interchangeable, it is a Value Object.
- **Immutability is necessary.** If a concept cannot be immutable, it is not a VO.
- **Lifecycle** – Entities have continuity across state changes; VOs are created-and-discarded.
- **Concentration of behavior.** VOs naturally gather business logic (`Money`, `DateRange`, `EmailAddress`). Don't scatter the logic across callers.

### 2.3 Domain Events

Immutable facts that something happened, named in past-tense ubiquitous language (`OrderPlaced`, `InventoryReserved`). Include: aggregate root ID, timestamp, event ID (UUID), relevant state at time of occurrence.

**Domain events ≠ integration events** – the most common event-driven + DDD mistake is treating them as one thing.

| | Domain event | Integration event |
|---|---|---|
| Scope | Within one bounded context | Between bounded contexts |
| Transport | In-process, typically synchronous | Async over a broker |
| Contract | Internal; can change freely | Public; versioned; additive evolution |
| Publish | At aggregate commit | After persistence, via **outbox** (avoids dual-write) |
| Metadata | Minimal | `eventId`, `causationId`, `correlationId` for tracing + idempotency |

Consumers of integration events must be idempotent (at-least-once delivery). Version with additive, optional fields; never mutate the meaning of a published field.

### 2.4 Domain Service vs. Application Service

| | Domain service | Application service |
|---|---|---|
| Contains branching business logic | Yes | No |
| I/O types | Domain objects | DTOs |
| Depends on infrastructure | No | Yes (repositories, brokers, APIs) |
| Purpose | Business operation with no natural entity home | Orchestrate a use case |

**Three-Phase Pattern** for application services: (1) load aggregate(s) from repositories; (2) invoke domain logic; (3) persist and publish. No `if`-branches expressing business rules in the application layer – those belong in the domain.

### 2.5 Factories and Repositories

- **Factory** – creates *new* aggregates. Use when creation requires business logic, structural variation, or cross-context translation; otherwise the root constructor suffices. Factories must leave the aggregate in an invariant-valid state.
- **Repository** – reconstitutes *existing* aggregates. One repository per aggregate root. Returns fully-hydrated, invariant-valid roots. **No** query methods returning non-root types (`FindOrderItemsByProductId` on `OrderRepository` is a bypass).
- Do not conflate the two. Evans is explicit: Factory = birth, Repository = persistence.
- **CQRS consequence** – query-side read models bypass repositories entirely. Repositories belong to the write side.

### 2.6 Module Layout Inside a Bounded Context

Vernon's canonical layout (IDDD_Samples on GitHub):

```
<context-name>/
  domain/
    model/          entities, value objects, aggregates
    service/        domain services
    event/          domain events
    repository/     repository interfaces (ports)
    factory/        factories (when needed)
  application/
    command/        command handlers / application services
    query/          query handlers (CQRS read side)
  infrastructure/
    persistence/    repository implementations, ORM mappers
    messaging/      event publishers, message adapters
    api/            controllers, serializers
```

Package names at the layer level (`domain`, `application`) are technical conventions; class names inside must be pure ubiquitous language (`Order`, not `OrderEntity`).

---

## 3. Architecture Integration

### 3.1 Hexagonal (Ports & Adapters) as the Bounded Context Skeleton

Vernon treats Hexagonal as the default shape for a bounded context (IDDD ch. 4). The domain model must be free of infrastructure dependencies so it can be tested and evolved independently.

- **Primary adapters** drive the application core (HTTP controllers, CLI, consumers).
- **Secondary adapters** are driven by the core through **port** interfaces defined in the application or domain layer (databases, brokers, external APIs).
- Combines naturally with Clean Architecture's dependency rule: dependencies point inward, toward the domain.

### 3.2 CQRS and DDD

CQRS (Command Query Responsibility Segregation; Young) separates the write model (rich, invariant-enforcing) from the read model (flat, query-optimized projections). Justified when read and write shapes genuinely diverge, query performance is a real constraint, or different teams own the two paths. Not justified for simple CRUD.

Granularity is a scale-tuning choice – apply per aggregate inside one service (a light-touch read projection) or across services (dedicated query side). CQRS does not require event sourcing; event sourcing nearly always requires CQRS.

### 3.3 Event Sourcing – Decision Criteria

**Use when** the audit trail or temporal queries (*what was the state at time T?*) are first-class domain requirements, or the aggregate's state is fully derivable from its event history.

**Do not use when** events are merely DB change logs, the team lacks experience, or simple CRUD covers the domain. Schema versioning becomes a permanent operational concern. Not a default – always a deliberate decision.

### 3.4 Sagas and Process Managers

Long-running workflows spanning aggregates or contexts. Two forms worth distinguishing in a DDD setting:

- **Saga** – no durable state; reacts to events and issues compensating actions. Simpler to reason about; limited memory.
- **Process Manager** – a durable state machine coordinating a workflow across multiple aggregates or contexts. More powerful; more to maintain.

**Orchestration vs. choreography** – orchestration (a process manager directing participants) is easier to trace but centralizes coupling; choreography (saga-style event chains) distributes coupling but is harder to observe. See `quanta.md` for Ford/Richards' 8-pattern saga classification and `${CLAUDE_PLUGIN_ROOT}/references/farley-framework.md` for reliability framing.

---

## 4. Discovery Techniques

### 4.1 Event Storming (Brandolini)

A collaborative workshop for exploring complex domains. Participants place sticky notes on a large surface: **orange** domain events (past tense), **blue** commands, **yellow** actors, **lilac** policies, **purple** hotspots, **green** read models.

Three levels:
1. **Big Picture** – map the domain end-to-end; discover bounded contexts from language conflicts and pivotal events.
2. **Process Modeling** – zoom into a workflow; identify command → aggregate → event → policy chains.
3. **Design Level** – detail aggregates and transactional boundaries.

Event Storming is primarily a **discovery** technique. Invoke the `andthen:clarify` skill for the Big Picture and Process levels; the Design level feeds directly into the `andthen:architecture` skill's `decompose` mode.

### 4.2 Bounded Context Canvas (DDD Crew, Tune)

One-page template for designing or auditing a single bounded context. Sections: name and purpose, strategic classification (core/supporting/generic), domain roles, inbound/outbound messages, dependencies (upstream/downstream + integration patterns), ubiquitous language excerpt. Forces explicit decisions about purpose and contracts before implementation.

### 4.3 Context Map as an Artifact

The context map is not just the pattern list – it is a maintained diagram of all bounded contexts and their labeled integration relationships. Keep it alongside the codebase (e.g., in the Project Document Index's architecture location) and update when team or integration relationships change. Render with the `andthen:excalidraw-diagram` skill.

---

## 5. Ubiquitous Language – Operationalizing

UL is a living artifact, not a glossary document (Vernon IDDD ch. 1–2).

- Domain class names must be terms a domain expert would use unprompted.
- **No weasel suffixes** in domain classes: avoid `UserInfo`, `OrderData`, `PaymentManager`, `CustomerEntity`. Infrastructure classes may keep technical suffixes; domain classes may not.
- **Model-code gap is a smell.** If translating between code names and business terms adds cognitive overhead in every conversation, the UL is not operational.
- Maintain a living glossary **per bounded context**, including candidate terms, rejected terms (and why), and terms that changed meaning.

The `andthen:ubiquitous-language` skill is the operational arm – invoke it to extract and maintain the glossary.

---

## 6. Functional DDD (Alternative Lens)

Scott Wlaschin's *Domain Modeling Made Functional* reframes tactical DDD with types: **make illegal states unrepresentable**. The type system carries invariants (`NonEmptyList`, `PositiveQuantity`, discriminated unions for state), commands are functions from current state to new state, and aggregates become pure transformations.

Complement, not replacement, for OO DDD. Useful when the target language is FP-first (F#, OCaml, Haskell, Rust/Scala in FP style) or when TypeScript/Kotlin code leans on sum types and exhaustive matching. Wlaschin builds on Evans' strategic design; the tactical patterns diverge from Vernon's OO-flavored treatment.

---

## 7. DDD Anti-Patterns

Classic DDD anti-patterns to check: **Anemic Domain Model**, **Leaky Abstraction**, **Context Explosion**, **Generic Subdomains as Core**, **Big Ball of Mud**. DDD-specific additions (not in the general `anti-patterns.md` catalog – consult this section under `review` or `decompose` mode when the target is aggregate- or event-heavy):

- **False Invariant Aggregates** – aggregate grouped by navigational convenience, not a true commit-time invariant. Symptom: multiple use cases only touch a subset. Fix: apply the Discovery heuristic (§2.1); split.
- **Leaky Integration Events** – internal aggregate structure exposed as a public event contract. Symptom: downstream consumers break when internal refactors ship. Fix: publish a purpose-built integration event via outbox; keep domain events internal.
- **Model-Code Gap** – domain experts and code disagree on names and boundaries. Symptom: constant translation overhead in design conversations. Fix: rename to UL; feed glossary discipline via the `andthen:ubiquitous-language` skill.

---

## 8. When to Bend the Rules

- Aggregate rules describe the *steady state*; legitimate migration steps may transiently violate them – converge back.

---

## Sources

- Evans, *Domain-Driven Design: Tackling Complexity in the Heart of Software* (2003).
- Vernon, *Implementing Domain-Driven Design* (2013); *Domain-Driven Design Distilled* (2016); *Effective Aggregate Design* I–III (2011, dddcommunity.org).
- Khononov, *Learning Domain-Driven Design* (2021).
- Wlaschin, *Domain Modeling Made Functional* (2018).
- Brandolini, *Introducing EventStorming* (Leanpub, ongoing).
- DDD Crew community – `github.com/ddd-crew/context-mapping`, `bounded-context-canvas`, `core-domain-charts`.
- Kaiser, *Architecture for Flow* (2021); Tune, bounded context canvas blog series.
- Khorikov, *enterprisecraftsmanship.com* – entity vs. VO, domain vs. application service, UL naming.
- de la Torre, Microsoft DevBlogs – domain events vs. integration events.
