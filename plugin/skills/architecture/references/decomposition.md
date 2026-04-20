# Decomposition Trade-Off Framework

Frameworks for evaluating split/merge decisions. Sources: Ford & Richards ("Software Architecture: The Hard Parts"), Sam Newman ("Building Microservices"), Martin Fowler, Michael Nygard.

## Table of Contents
- [Disintegration Drivers](#disintegration-drivers)
- [Integration Drivers](#integration-drivers)
- [Decomposition Patterns](#decomposition-patterns)
- [Anti-Patterns](#anti-patterns)
- [Consumer Profile Analysis](#consumer-profile-analysis)
- [4-Criteria Evaluation Matrix](#4-criteria-evaluation-matrix)
- [Sizing Heuristics](#sizing-heuristics)
- [Split and Merge Signals](#split-and-merge-signals)
- [DDD Bounded Contexts](#ddd-bounded-contexts)
- [Newman's Decision Tree](#newmans-decision-tree)
- [Incremental Decomposition Patterns](#incremental-decomposition-patterns)
- [Decomposition Triggers](#decomposition-triggers)

---

## Disintegration Drivers

Six drivers that justify breaking a component apart (Ford/Richards). Score each as **Strong / Moderate / Weak / N/A** with evidence.

### 1. Service Scope and Function
The component handles unrelated responsibilities.
- **Review question**: Does this module violate SRP? Would a change in domain A force redeployment for domain B?
- **Never sufficient alone** — needs at least one other driver

### 2. Code Volatility
Parts change at different rates.
- **Review question**: Are high-change parts forcing redeployment of stable parts?
- **Input**: Commit history, change frequency per subdirectory

### 3. Scalability and Throughput
Parts have different performance profiles.
- **Review question**: Does one subsystem need 10x the resources of others?
- **Limitation**: Premature optimization risk — measure actual load first

### 4. Fault Tolerance
Parts have different availability requirements.
- **Review question**: Does a failure in one domain take down unrelated functionality?
- **Note**: Container-level isolation may address this without a logical split

### 5. Security
Parts have different trust/access profiles.
- **Review question**: Are sensitive operations bundled with public ones, widening the attack surface?

### 6. Extensibility
One part is a planned extension point.
- **Review question**: Would isolating this enable independent evolution?
- **YAGNI risk**: Only split for extensibility when there are actual (not hypothetical) extension consumers

---

## Integration Drivers

Four drivers that argue for keeping things together. Score each with evidence.

### 1. Database Transactions
ACID requirements span the proposed boundary.
- **Review question**: Would splitting require a saga? Is that complexity justified?

### 2. Workflow and Choreography
Tight sequential workflow dependencies.
- **Review question**: Would splitting create chatty inter-service calls? Does a use case require 3+ synchronous calls across the boundary?

### 3. Shared Code
Significant non-trivial shared logic.
- **Review question**: Is the shared code a sign of a missing service, or genuinely reusable infrastructure?

### 4. Data Relationships
Foreign keys, referential integrity, views.
- **Review question**: Can data consistency be maintained across the boundary? Does the data share a lifecycle?

### Decision Heuristic
When disintegrators and integrators are in tension, weigh coupling cost (instability, blast radius) against coordination cost (distributed transactions, eventual consistency). There is no correct granularity — the goal is "the least worst combination of trade-offs."

---

## Decomposition Patterns

### Component-Based Decomposition
For codebases with existing modular structure.
1. Identify and size components — target 1-2 std devs from mean
2. Gather common domain components — consolidate shared logic
3. Flatten component domains — group into domain groupings
4. Extract domain services — promote to separately deployable units
5. Verify quantum independence before finalizing
6. Check dependency direction (SDP) in the new graph

### Tactical Forking
For "big ball of mud" codebases with no discernible structure.
1. Duplicate the entire codebase into N parallel versions
2. Each team deletes code they don't own
3. Route traffic via proxy between old and new
4. Incrementally harden what remains
- **Advantage**: Deletion is simpler than surgical extraction
- **Disadvantage**: Residual dead code, requires cleanup phase

---

## Anti-Patterns

### The Entity Trap
Decomposing by data entity (UserService, OrderService, ProductService) instead of business capability.
- **Symptoms**: Most requests touch 3-5 services; business logic in API gateways; high fan-in to entity services
- **Fix**: Decompose by capability and workflow using DDD bounded contexts

### Distributed Monolith
Split but still coupled.
- **Symptoms**: Coordinated deployments, shared database, chatty inter-service calls, can't deploy independently
- **Root cause**: Split without severing the architectural quantum

### Microservices Premium
The fixed cost of running any distributed architecture — tracing, latency, service discovery, serialization, operational complexity.
- **Only justified when**: independent scaling, deployment, or team autonomy is actually needed and measurable
- **Not justified when**: team < 8 engineers, domain unclear/greenfield, no independent scaling needed

---

## Consumer Profile Analysis

A concrete, metrics-based approach to evaluating decomposition (from DartClaw SDK research).

### Process
1. Define 5-7 concrete consumer profiles (actual use cases with code examples)
2. For each profile, trace the dependency tree to identify forced subsystems
3. Calculate "forced LOC waste" — LOC imported but not used
4. Compute the "true shared kernel" across all profiles

### Waste Thresholds
- **< 30%**: Acceptable. Package granularity is fine.
- **30-50%**: Watch zone. Monitor as new consumers appear.
- **> 50%**: Split signal. The median consumer is carrying more dead weight than useful code.

### Example Format

| Profile | Use Case | LOC needed | LOC forced | Waste % |
|---------|----------|-----------|------------|---------|
| P1: Minimal | Single-turn agent | ~1,500 | ~11,000 | 88% |
| P2: Custom server | Custom server + harness | ~6,400 | ~6,200 | 49% |
| P5: Guard plugin | Compliance guard only | ~2,600 | ~10,000 | 79% |

P5 at 79% waste is a clear decomposition signal for extracting the guard subsystem.

---

## 4-Criteria Evaluation Matrix

For each split candidate, check all four:

| Criterion | Description | Test |
|-----------|-------------|------|
| **(a)** Zero external deps | Can the package avoid third-party deps? | Pure language? |
| **(b)** Independent consumer use | Would an external dev import this alone? | Concrete example exists? |
| **(c)** Acyclic dependency graph | Clean DAG post-split? | No circular deps? |
| **(d)** Low breaking-change cost | Mechanical migration for existing consumers? | < 5 files affected? |

**Threshold**: Execute if **(a) + (b) + (c)** all pass. Evaluate (d) for net benefit.

---

## Sizing Heuristics

| Method | Source | Rule |
|--------|--------|------|
| Component size | Ford/Richards | Target 1-2 std devs from mean component size |
| Team cognitive load | Team Topologies | A team can manage 2-3 low-complexity domains |
| Two-pizza rule | Amazon | If the owning team can't be fed by 2 pizzas (~5-7 people), the service may be too large |
| Change containment | General | A business requirement change should touch exactly one package |
| Barrel symbol count | Practical | If exported symbols > 50, reassess scope |

---

## Split and Merge Signals

### Signals to Split
- Module description requires "and" — it does X **and** Y
- Different subsets have different change frequencies
- Different consumers use disjoint subsets (CRP violation)
- Consumer waste > 50%
- Barrel exports > 50 symbols
- I metric suggests stability but contains volatile code

### Signals to Merge
- Two packages always change together (coordinated releases)
- Packages form a cycle in the dependency graph
- One package is only accessed transitively through another
- Package has very high Ca but is tiny — may be over-extracted

---

## DDD Bounded Contexts

A bounded context is a linguistic boundary — within it, all terms have a single unambiguous meaning. Each bounded context maps to at most one architectural quantum.

### Context Mapping Patterns

| Pattern | Coupling | When to Use |
|---------|----------|-------------|
| **Shared Kernel** | Tightest | Closely related contexts, good team communication, stable shared model |
| **Anti-Corruption Layer** | Medium | Integrating with legacy or third-party systems |
| **Conformist** | Medium | Upstream is authoritative (external standard) |
| **Customer/Supplier** | Negotiated | Teams can negotiate requirements |
| **Open Host Service** | Loosest | Platform teams publishing stable APIs |
| **Separate Ways** | None | Integration cost exceeds value — accept duplication |

---

## Newman's Decision Tree

1. **Do you have a compelling reason?** No → stay modular monolith
2. **Is the domain clear?** No → monolith first; boundaries emerge from experience
3. **Is the team large enough?** < 8 engineers → microservices premium not justified
4. **Do you need independent deployability?** No → modular monolith (Shopify approach)
5. **Do you need independent scaling?** → Extract only those subsystems
6. **Do you need team autonomy?** → Align service boundaries with team boundaries (Conway)

---

## Incremental Decomposition Patterns

### Strangler Fig
1. Identify the slice to extract
2. Implement new service alongside old code
3. Reroute with proxy or feature toggle
4. Remove old code once new path is proven

### Branch by Abstraction
1. Introduce abstraction layer over functionality to replace
2. Move all callers to use the abstraction
3. Build new implementation behind the abstraction
4. Flip to new implementation
5. Delete old code

---

## Decomposition Triggers

Rather than "split when convenient" or "never split," define concrete triggers:

| Trigger | Action |
|---------|--------|
| Third consumer with different needs | Consider per-consumer packages |
| External contributor maintains a subsystem | Extract that subsystem |
| Barrel exceeds ~60 exported symbols | Reassess package scope |
| Subsystem reused outside original project | Extract as independent package |
| Pre-1.0 review | Revisit deferred decomposition decisions |
| Consumer waste > 50% for a profile | Strong split signal |

Triggers prevent both premature decomposition AND indefinite paralysis.
