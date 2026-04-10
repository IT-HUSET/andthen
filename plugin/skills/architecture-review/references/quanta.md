# Architectural Quanta & Evolutionary Architecture

Concepts from Ford/Richards ("Software Architecture: The Hard Parts") and Ford/Parsons/Kua ("Building Evolutionary Architectures").

## Architectural Quantum

### Definition
The smallest independently deployable artifact with three simultaneous characteristics:
1. **High functional cohesion** — unified in purpose (aligned with a DDD bounded context)
2. **High static coupling** — tightly bound structurally (shared contracts, shared deps resolved at build time)
3. **Synchronous dynamic coupling** — communicates with internal parts synchronously; async communication across boundaries signals separate quanta

### Counting Quanta
The quantum count is a diagnostic of true independence:
- Monolith = 1 quantum
- Well-decomposed microservices = N quanta
- Poorly decomposed distributed system with coordinated deployments = still effectively 1 quantum

### Identification Questions
- Can this artifact be deployed without deploying anything else?
- Does it own its own data persistence? (Shared databases collapse quanta)
- Can it function when its synchronous dependencies are unavailable?
- Do any synchronous call chains require other artifacts to be available?

### Anti-Patterns
- **Distributed monolith**: Many deployed services that cannot actually deploy independently — shared schemas, shared libraries with breaking APIs, synchronous chains
- **Nano-services**: Quanta so small that operational overhead (infra, observability, latency) exceeds modularity benefit

### Trade-offs
Fewer, larger quanta → lower operational complexity, easier transactions, but less deployment independence and scaling granularity.
More, smaller quanta → higher evolvability and independent scaling, but distributed systems problems (consistency, observability, saga coordination).

---

## Evolutionary Architecture

### The Formula
```
Evolutionary Architecture = Incremental Change + Fitness Functions + Appropriate Coupling
```

Architecture rarely decays because teams stop caring. It decays because change accumulates faster than the system can absorb it. The job is to keep absorption rate ahead of change rate.

### Last Responsible Moment
Delay architectural decisions until the cost of NOT deciding exceeds the cost of deciding. Fitness functions support this by making the cost of deciding later visible — when coupling calcifies without guardrails, the delayed cost becomes apparent.

### Sacrificial Architecture
Deliberately build a system expecting to discard it, because early uncertainty makes premature optimization wasteful.
- Maintain modularity and test coverage even in sacrificial systems (these enable graceful replacement)
- Focus fitness functions on handoff qualities (modularity, tests, documented interfaces) rather than long-term operations (extreme performance)

### Architectural Runway
Just enough infrastructure and structural investment to support near-term features without blocking:
- **Too little runway**: Teams constantly pay architecture tax
- **Too much runway**: Speculative engineering that may never be needed
- **Sweet spot**: 2-4 sprints of prepared capacity
- Fitness functions that enforce seams (clean interfaces, isolated modules) are runway investments

### Conway's Law Alignment
Organizational structure constrains architecture. Services split across team boundaries create coordination overhead that negates autonomy benefits.

**Reverse Conway Maneuver**: Design the org to match the desired architecture. The architecture follows the team topology, not vice versa. Amazon's service-oriented architecture emerged from the two-pizza team mandate, not the other way around.

---

## Saga Patterns

Ford/Richards classify distributed workflows across three axes, producing 8 patterns:

| Axis | Options |
|------|---------|
| Communication | Synchronous / Asynchronous |
| Consistency | Atomic (all-or-nothing) / Eventual |
| Coordination | Orchestrated (central controller) / Choreographed (event-driven) |

### The 8 Patterns

| Pattern | Sync | Consistency | Coordination | Coupling | Complexity |
|---------|------|-------------|--------------|----------|------------|
| **Epic** | Sync | Atomic | Orchestrated | Very high | Low |
| **Phone Tag** | Sync | Atomic | Choreographed | High | High |
| **Fairy Tale** | Sync | Eventual | Orchestrated | High | Very low |
| **Time Travel** | Sync | Eventual | Choreographed | Medium | Low |
| **Fantasy Fiction** | Async | Atomic | Orchestrated | High | High |
| **Horror Story** | Async | Atomic | Choreographed | Medium | Very high |
| **Parallel** | Async | Eventual | Orchestrated | Low | Low |
| **Anthology** | Async | Eventual | Choreographed | Very low | High |

### Selection Guidance
- **Async + Eventual + Choreographed** (Anthology): Lowest coupling, highest complexity. Best for event-driven systems with mature ops.
- **Sync + Atomic + Orchestrated** (Epic): Lowest complexity, highest coupling. Best for simple workflows within a single quantum.
- Most production systems mix patterns per workflow: Epic for payments, Anthology for notifications.
- **Rule of thumb**: "As workflow complexity goes up, the need for an orchestrator rises."

### Orchestration vs Choreography

**Orchestration**:
- Explicit workflow state in one component
- Easier to reason about, debug, monitor
- Natural audit trail
- Risk: orchestrator becomes bottleneck/single point of failure

**Choreography**:
- Maximum decoupling — services evolve independently
- Scales horizontally without coordination
- Risk: implicit workflow — distributed across event handlers, harder to trace

### Connascence Lens on Sagas
- **RPC-style** services have CoE (execution order) + CoTm (timing) — strong dynamic connascence across boundaries
- **Event-driven** services have only CoN + CoT (event name and schema) — weak static connascence
- Event-driven architectures are architecturally superior from a connascence standpoint: they convert CoE and CoTm into CoN and CoT. The cost is eventual consistency and operational complexity.
