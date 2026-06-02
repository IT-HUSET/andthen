# Architecture Anti-Patterns Catalog

Common structural anti-patterns to check for during architecture review.

---

## Entity Trap

CRUD-centric decomposition by data entity instead of business capability.

**Symptoms**:
- Services named after entities: UserService, OrderService, ProductService
- Most user operations require 3-5 inter-service calls
- Business logic accumulates in API gateways or orchestrator layers
- High fan-in to entity services (load hotspots)
- Services expose their data model directly as API

**Root cause**: Confusing data relationships for capability boundaries. "Order" in fulfillment context has different properties and lifecycle than "Order" in billing context – treating them as the same entity forces contexts to share a data model.

**Fix**: Decompose by business capability using DDD bounded contexts. Ask "what does this module DO for the business?" not "what data does it own?"

**Review question**: Are modules named after nouns (entities) or verbs (capabilities)?

---

## Distributed Monolith

Split topology but coupled behavior – the worst of both worlds.

**Symptoms**:
- Services require coordinated deployment (can't deploy independently)
- Shared database schema across multiple services
- Chatty inter-service calls for every user operation
- Integration test failures when any single service changes
- Service A must understand Service B's internals to function

**Root cause**: Split without identifying and severing the architectural quantum. The quantum boundary was drawn at the wrong place.

**Fix**: Identify true quanta boundaries. Either merge back to monolith and re-split correctly, or invest in decoupling (async events, separate data stores, API contracts).

**Review question**: Can each service be deployed, tested, and released independently?

---

## God Module

A module that does too much – high LOC, high coupling, high complexity.

**Detection thresholds** (all three must be present to reduce false positives):
- LOC > 1000 (relative to sibling packages)
- Ce > 10 (depends on too many other modules)
- Mean cyclomatic complexity > 10

**Symptoms**:
- Difficult to understand without reading the entire module
- Changes frequently for many different reasons (CCP violation)
- Hard to test in isolation – requires extensive setup

**Fix**: Extract cohesive submodules. Apply CCP – group by change driver, not by technical role.

**Review question**: Can you state in one sentence what this module does, without the word "and"?

---

## Zone of Pain

Concrete, stable packages (I ≈ 0, A ≈ 0). Heavily depended upon with no abstractions.

**Characteristics**:
- High change cost – every modification cascades to many dependents
- Low extensibility – no interfaces to extend, only concrete classes to modify
- Cascading breakage on any change

**When acceptable**: Infrastructure genuinely stable by nature (database drivers, language runtime bindings). NOT acceptable for business logic or domain rules.

**Fix**: Extract interfaces from the stable package. Move concrete implementations behind abstractions. Consumers depend on the interface; implementations become swappable.

**Metrics**: I < 0.2, A < 0.1, Ca > 5. D > 0.7.

---

## Zone of Uselessness

Abstract, unstable packages (I ≈ 1, A ≈ 1). Nobody depends on them.

**Characteristics**:
- Interfaces with no implementations
- Abstract base classes with no subclasses
- Speculative abstractions created for hypothetical future use

**When acceptable**: Temporarily during active design/prototyping phase. Not acceptable when persisting to production.

**Fix**: Either find consumers and wire them up (the abstraction is useful but undiscovered), or delete the dead abstraction.

**Metrics**: I > 0.8, A > 0.8, Ca = 0 or very low. D > 0.7.

---

## Microservices Premium

Paying distribution costs without distribution benefits.

**Check these conditions** – if most are true, the premium is not justified:
- Team smaller than ~8 engineers
- Domain is unclear or greenfield (boundaries not yet understood)
- No subsystem needs independent scaling
- No regulatory reason for process isolation
- DevOps maturity is low (no automated deployment, no distributed tracing)

**Fix**: Use a modular monolith with enforced boundaries (Shopify/Packwerk approach). Get the benefits of decomposition (clear boundaries, independent testing) without the distributed systems tax.

**Reference**: Fowler's "MonolithFirst" – start with a well-structured monolith, decompose when you have proven reasons.

---

## Circular Dependencies

Packages that form a dependency cycle – cannot be independently compiled, tested, or deployed.

**Always a finding. Always fix.** There is no acceptable production use of circular package dependencies.

**Breaking strategies**:
1. **DIP**: Extract an interface into a third package that both depend on
2. **Merge**: If the cycle reflects genuine cohesion, the packages should be one package
3. **Event/callback**: Invert the dependency via an event bus or callback parameter

**Severity**: Scales with cycle size. 2-node cycle = HIGH. 3+ nodes = CRITICAL.

---

## Leaky Abstraction

Callers depend on implementation details rather than the declared interface, **or** the same internal design decision is reflected in more than one interface (Ousterhout's _information leakage_, APoSD Ch. 5).

**Symptoms**:
- Callers import internal/`src/` types from another package
- Callers cast to implementation classes
- Callers depend on behavior that's an implementation artifact (result ordering, side effects)
- Callers access fields or methods not part of the declared API
- A single design decision (file format, protocol detail, data layout, algorithm choice) shows up in the shape of multiple module interfaces – so changing it forces coordinated API changes

**Fix**: Narrow the public API surface. Move implementation types to `src/`-only access. Add missing methods to the interface so callers don't need to bypass it. For shape-level leakage, relocate the decision so exactly one module's interface reflects it.

**Review question**: If the implementation (or the leaked decision) changed, how many interfaces would have to change with it? More than one ⇒ leakage.

---

## Premature Decomposition

Splitting before the domain is understood.

**Symptoms**:
- Boundaries drawn based on initial guesses, not proven usage patterns
- Frequent boundary refactoring as understanding grows
- Abstractions created for zero consumers
- "We might need this separation later"

**Fix**: Fowler's "monolith first" – build a well-structured monolith, learn the domain, then decompose when boundaries are clear and the benefit is measurable.

**Review question**: How many times have these boundaries been redrawn? If more than twice, the domain isn't understood well enough to split.

---

## Speculative Generality

Abstractions, configuration options, or extension points created for hypothetical future requirements.

**Symptoms**:
- Generic type parameters with only one concrete type
- Strategy patterns with only one strategy
- Configuration options nobody has ever changed
- "Just in case" interfaces

**Fix**: Delete the abstraction and use the concrete type directly. Reintroduce when there's a second consumer (the Rule of Three).

**Review question**: How many concrete implementations/consumers exist? If one, the abstraction may be speculative.

---

## Convenience Coupling

Dependencies added because a class is available, not because the dependency is architecturally justified.

**Symptoms**:
- A high-level module importing a low-level utility for one small function
- A package depending on another for a single type that could be duplicated or extracted
- Dependencies that "seemed easier than writing it ourselves" but create architectural coupling

**Fix**: Evaluate whether the convenience dependency creates an SDP violation. If so, extract the shared type into a leaf package or duplicate the small utility.

**Review question**: Does this dependency make sense architecturally, or was it added for convenience?

---

## Shallow Module

A module whose interface is about as complex as its implementation – it adds a boundary to cross without abstracting meaningfully (Ousterhout, APoSD Ch. 4).

**Symptoms**:
- Interface parameters mirror implementation details (one parameter per internal step, field, or branch)
- Callers must read the implementation to use the module safely
- Decomposing an existing module produced N helpers whose signatures together carry as much information as the original body
- "Classitis" – many small classes/methods each doing a single trivial operation with non-trivial plumbing

**Fix**: Collapse shallow modules into a deeper one that hides more; or widen the implementation behind the existing interface until the abstraction earns its depth. Prefer fewer, deeper modules over many small ones when cohesion allows.

**Review question**: Could a caller use this correctly without reading its implementation? If no, the module is shallow (or the interface is underspecified).

**Cross-check**: Do not collapse if it would violate CCP/SRP or re-create a god module. Depth is bounded above by cohesion.

---

## Pass-Through Method / Layer

A method, class, or layer that forwards to another with the same (or near-identical) parameters, adding no abstraction or meaningful work (Ousterhout, APoSD Ch. 7 – _different layer, different abstraction_).

**Symptoms**:
- Wrapper methods that just call a delegate with the same arguments
- Facade classes whose methods match the underlying service 1:1
- Layer whose every public call is a thin forward to the layer below, with identical types crossing the boundary

**Fix**: Remove the layer, or give it a distinct abstraction (aggregation, translation, policy, caching, authorization – something the caller would actually ask for). If nothing qualifies, the layer is not earning its existence.

**Review question**: What abstraction does this layer introduce that the layer below does not already provide? If the answer is "none," delete it.

---

## Temporal Decomposition

Modules split by the **order operations occur at runtime** rather than by the knowledge they encapsulate (Ousterhout, APoSD Ch. 5).

**Symptoms**:
- Modules named for pipeline stages: `Reader`, `Parser`, `Validator`, `Processor`, `Writer`
- Multiple modules each hold partial knowledge of the same format, protocol, or data shape
- Changes to that shared concept require coordinated edits across the sequence

**Fix**: Re-decompose by knowledge ownership. Group code that shares knowledge of the same external contract (format, protocol, schema) into one module, even if that module spans multiple execution stages internally.

**Review question**: If the file format (or protocol, or schema) changed, how many of these modules would need edits? More than one ⇒ temporal decomposition masking shared knowledge.

**When acceptable**: True pipeline / stream architectures (compilers, ETL, stream processors) where each stage owns a **distinct abstraction** and communicates through a typed intermediate form. The signal is that each stage's knowledge is disjoint, not shared – a parser that emits AST nodes the next stage consumes is legitimate; a parser that the next stage re-parses or re-interprets is not.
