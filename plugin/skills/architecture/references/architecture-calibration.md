# Architecture Calibration

Thresholds, selection criteria, and misfire traps for the architecture modes, applied on top of `review-calibration.md` where the mode loads it. The frameworks are assumed known – Martin's package principles, Page-Jones/Weirich connascence, Evans/Vernon/Khononov DDD, Ford & Richards decomposition drivers, Ousterhout's module design, Newman on extraction. What follows is only what a model does not get from knowing them.

## Metrics and Thresholds

**Ca** afferent, **Ce** efferent, **I** = `Ce / (Ca + Ce)`, **A** = abstract types / total types (abstract classes, interfaces, and mixins count as abstract), **D** = `|A + I - 1|`. Graph-level, computable from any dependency graph (Dart: `lakos --metrics --node-metrics <dir>`): CD = nodes reachable from a node including itself (blast radius), CCD = sum of CD, ACD = CCD / N, NCCD = CCD relative to a balanced binary tree of N – below 1.0 beats that baseline.

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| D (distance) | < 0.3 | 0.3 – 0.5 | > 0.5 |
| NCCD | < 1.0 | 1.0 – 2.0 | > 2.0 |
| Ce (efferent) | < 8 | 8 – 10 | > 10 (God Module) |
| Ca with A < 0.1 | < 5 | 5 – 10 | > 10 (concrete hotspot) |
| Cycles | 0 | any 2-node | > 3-node cycle |
| Package LOC | < 3000 | 3000 – 10000 | > 10000 |
| Consumer waste | < 30% | 30 – 50% | > 50% (split signal) |

**Principle assertions.** ADP: Tarjan's SCC, any SCC with more than one node is a violation – always a finding, always fixed. SDP: for every edge A → B assert `I(A) ≥ I(B)`. SAP: for packages with I < 0.3 assert A > 0.3 – stable-but-concrete is the violation, since stability should come from abstraction, not from freezing implementations. The cohesion principles pull against each other and no package maximizes all three: prioritize CCP early, when blast radius dominates, and shift toward CRP as consumer diversity grows.

**Zones.** Zone of Pain: I < 0.2, A < 0.1, Ca > 5, D > 0.7 – concrete and stable, so every change cascades. Zone of Uselessness: I > 0.8, A > 0.8, Ca ≈ 0, D > 0.7 – abstract with nothing depending on it; acceptable only during active design.

## Connascence Scoring

`Severity = (Strength × Degree) / Locality`

- **Strength** – static: CoN 1, CoT 2, CoM 3, CoP 4, CoA 5. Dynamic: CoE 6, CoTm 7, CoV 8, CoI 9.
- **Degree** – affected files, classes, or call sites. **Locality** – 3 within a class, 2 cross-class within a package, 1 cross-package.

Axiom: any dynamic form is categorically worse than any static form – detecting it needs runtime reasoning, so static analysis cannot see it and review usually misses it. Every reduction aims at CoN, and the weaker form is required as distance grows (Weirich's Rule of Locality); high connascence *inside* a boundary is cohesion, not a finding.

Boundary reading: cross-boundary coupling that is all CoN/CoT means a healthy boundary; any CoM/CoP/CoA crossing is MEDIUM and names refactoring targets before the boundary counts as stable; any dynamic form crossing is HIGH or CRITICAL and a strong merge signal.

## Severity Calibration

Contrastive pairs. The over-escalations are the ones this skill actually makes.

**CRITICAL is** dynamic connascence across a service boundary – `OrderService` and `PaymentService` both holding the same mutable `TransactionContext` singleton, payment status leaking between unrelated orders (9 × 4 / 1 = 36).

**CRITICAL is not** `utils` at D=0.85 with 12 concrete classes and Ca=8: a high D alone is MEDIUM, and stable concrete utilities cost more to abstract than to leave – check change frequency before escalating. Nor a 2-node cycle (`models` ↔ `serialization`): that is HIGH, one interface extraction away. Reserve CRITICAL for 3+ node cycles or cycles through core business packages.

**HIGH is** a measured principle violation with quantified blast radius – `core` (I=0.08) depending on `plugins` (I=0.92) with 14 packages transitively inheriting the volatility (SDP).

**HIGH is not** `database_driver` at D=0.98: infrastructure stable by nature, not by accident – INFO unless it holds business logic or changes often. Nor Ce=9 against the God Module threshold: approaching a threshold is INFO with context.

**MEDIUM** is drift in a package that keeps changing – `auth` at D=0.45, Ca=6, no interfaces, 2–3 commits a month. **LOW** is a convention violation with no structural consequence. **INFO** is a metric marginally outside the healthy range (D=0.32, Ce=5, Ca=3).

**Ousterhout's module-design lens** (APoSD) applies to in-process module, class, and public-API design only – never service boundaries; a full-project, container, or decomposition scope skips it. The eight tests: depth, information leakage, pass-through, obviousness, temporal decomposition, error existence, one-sentence description, designed-twice; findings tag C4 **Component** or **Code**. No special thresholds: an isolated single-module finding defaults to INFO, and HIGH needs measurable impact across several consumers.

## Boundary and Domain Calibration

**Bounded contexts** are a linguistic boundary, not a deployment one – a context map applies inside a modular monolith too. One team owns one or more whole contexts, never a fraction of one, with a cognitive-load ceiling of 2–3 low-complexity domains per team. One term meaning two things is two contexts, or a failure to tell them apart; a God-object aggregate at the centre says the context is too broad. Every pair in a context map names its integration pattern from the nine – Evans' eight plus Big Ball of Mud as a quarantine wrapper – and moves up that list (Partnership, Shared Kernel) when teams are aligned and models stable, down it (Conformist, Anticorruption Layer, Separate Ways) when teams are distant, models incompatible, or the upstream cannot be negotiated with. Team boundaries cutting across context boundaries predict a distributed monolith.

**Aggregates.** An invariant is a rule enforced *at commit*; a rule that only has to hold eventually never justifies widening an aggregate. To test a cluster, list the aggregates one use case modifies and name the invariant forcing them into a single transaction – no invariant, break the cluster. The rules describe a steady state, so a migration step may violate them transiently.

**CQRS** only when read and write shapes genuinely diverge, query load is a real constraint, or different teams own the two paths – never for CRUD. **Event sourcing** only when audit or temporal queries are first-class, or state is fully derivable from history; schema versioning becomes permanent operational work. CQRS does not require event sourcing; event sourcing nearly always requires CQRS.

**Ubiquitous language.** Domain class names are the terms an expert uses unprompted; weasel suffixes are the smell (`UserInfo`, `OrderData`, `PaymentManager`, `CustomerEntity`), with infrastructure classes the exception. Constant translation between code names and business terms means the language is not operational. Per-context glossary curation is the `andthen:describe` skill in `--mode domain`.

**Sizing.** Component size within 1–2 standard deviations of the mean (Ford/Richards); 2–3 low-complexity domains per team (Team Topologies); an owning team past ~5–7 people means the service may be too large; one business requirement change should touch exactly one package; a barrel exporting more than ~50 symbols means reassess scope.

**Extraction gate** (Newman). No compelling reason, an unclear domain, fewer than ~8 engineers, or no need for independent deployability → stay a modular monolith. Extract only the subsystems that need independent scaling, or the boundaries that need team autonomy (Conway).

## Traps

Check each before recording a finding – these are the shapes that look like architecture problems and are not.

1. **Infrastructure in the Zone of Pain** – drivers, logging, serialization, and runtime bindings sit at I≈0, A≈0 by nature. Flag only when the package holds business logic or changes frequently.
2. **Leaf package with high Ce** – CLI entry points, controllers, and test harnesses are the wiring. Check that Ca≈0 before flagging.
3. **Small package with high Ca** – a shared-types package is a shared kernel, not a God Module. That label needs all three: LOC > 1000 relative to siblings, Ce > 10, mean cyclomatic complexity > 10.
4. **Cross-module CoN** – unavoidable across public APIs; a finding only when names are ambiguous or inconsistent for one concept.
5. **Theoretical decomposition** – "this could be split" is not a finding without scored drivers and the evaluation matrix. If no consumer would import the sub-package alone, the split adds complexity and removes none.
6. **Monorepo structure read as coupling** – coupling is import edges and runtime dependencies, not repository topology.
7. **Service count read as quanta** – independence is the unit: coordinated deployment, a shared database, or breaking shared libraries collapse many services into one quantum, which is the distributed monolith. The opposite extreme, nano-services, pays operational overhead exceeding the modularity gained. Merging back and re-splitting is a legitimate fix.
8. **Shallow module collapsed too far** – depth is bounded above by cohesion: collapsing is wrong when it re-creates a God Module or violates CCP/SRP, and decomposing one shallow module into five helpers replaces one shallow thing with five. Count total interface information, not module count.
9. **Temporal decomposition in a real pipeline** – compilers, ETL, and stream processors legitimately split by stage when each stage owns a *distinct* abstraction and hands on a typed intermediate form. A parser emitting AST nodes is legitimate; a parser whose output the next stage re-interprets is the anti-pattern.
10. **Leakage read too narrowly** – a design decision (file format, protocol detail, data layout, algorithm) leaks by *shape*, not only through imported internal types. The question is how many interfaces change when it changes; more than one is leakage.
11. **Pass-through layer** – a layer earns its place only by introducing an abstraction the caller would ask for: aggregation, translation, policy, caching, authorization. "None" means delete it.
12. **Convenience coupling** – a dependency taken because the class happened to be there is a finding only when it creates an SDP violation.
13. **Speculative generality** – one implementation of an abstraction is a candidate, not a verdict; reintroduce at the second consumer (Rule of Three).
14. **Premature decomposition** – boundaries redrawn more than twice mean the domain is not understood well enough to split.
15. **Microservices premium** – distribution costs (tracing, latency, discovery, serialization, ops) without distribution benefits. No regulatory reason for process isolation and low DevOps maturity each argue against paying it.
16. **False-invariant aggregate** – grouped by navigational convenience; the symptom is that most use cases touch only a subset.
17. **Leaky integration event** – internal aggregate structure published as a public contract, so consumers break on internal refactors. Domain events stay inside their context; integration events are purpose-built, versioned additively, published after persistence via an outbox, and consumed idempotently.
