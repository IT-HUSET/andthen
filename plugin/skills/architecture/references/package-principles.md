# Package Principles & Metrics

Robert C. Martin's six package principles and the quantitative metrics that operationalize them.

## Table of Contents
- [Cohesion Principles](#cohesion-principles)
- [Coupling Principles](#coupling-principles)
- [Metrics](#metrics)
- [The Main Sequence](#the-main-sequence)
- [Problem Zones](#problem-zones)
- [SOLID at Package Level](#solid-at-package-level)
- [Lakos Metrics](#lakos-metrics)
- [Thresholds](#thresholds)

---

## Cohesion Principles

What belongs in the same package?

### REP — Reuse-Release Equivalence Principle
> The granule of reuse is the granule of release.

Everything in a package is released and versioned together. If a consumer reuses one class, they accept all classes and all breaking changes.

- **Review question**: If a consumer needs one class, are they forced to take unnecessary classes?
- **Anti-pattern**: Utility grab-bags of unrelated small classes
- **Implication**: Groups with different stability and release cycles should not share a package

### CCP — Common Closure Principle
> Classes that change for the same reasons, at the same times, belong in the same package.

SRP applied at the package level. Group by change driver so a single business requirement change touches exactly one package.

- **Review question**: Does a single business change require modifying multiple packages?
- **Anti-pattern**: A feature spread across 5 packages (entity, repository, service, controller, dto) — adding a field touches all 5
- **Dominates when**: Early in development — reducing change blast radius is priority

### CRP — Common Reuse Principle
> Classes that are reused together belong together. Don't force consumers to depend on classes they don't use.

ISP applied at the package level. A package is a dependency unit — every class creates transitive dependency burden.

- **Review question**: Does importing this package force consumers to take on dependencies they don't use?
- **Anti-pattern**: A "common" package with 40 loosely related utilities
- **Dominates when**: Consumer diversity grows — minimizing unnecessary coupling becomes priority

### The Tension Triangle

REP, CCP, and CRP pull in different directions:
- **CCP** groups by change-reason (maximizes closure)
- **CRP** groups by reuse-pattern (minimizes unnecessary coupling)
- **REP** groups by release-unit (aligns reuse with versioning)

A package cannot maximize all three simultaneously. Early in development, prioritize CCP. As consumer diversity grows, shift toward CRP.

---

## Coupling Principles

How should packages relate?

### ADP — Acyclic Dependencies Principle
> No cycles in the package dependency graph.

Cycles make packages impossible to independently compile, test, and deploy. All packages in a cycle are effectively one unit.

- **Measurement**: Run cycle detection (Tarjan's SCC). Any SCC with >1 node = violation.
- **Breaking cycles**: (1) DIP — extract an interface both sides depend on, (2) Merge the cyclic packages, (3) Create a new abstraction package
- **Severity**: Always a finding. Always fix.

### SDP — Stable Dependencies Principle
> Depend in the direction of stability.

Volatile packages must not be depended upon by stable packages. A stable package depending on a volatile one inherits that volatility.

- **Measurement**: For each edge A → B, check I(A) ≥ I(B). If A is stable (I=0.1) and depends on B which is volatile (I=0.9), that's a violation.
- **Review question**: Does this dependency arrow point from lower-I toward higher-I?
- **Fix**: Introduce an abstraction (interface) that inverts the dependency direction

### SAP — Stable Abstractions Principle
> A package should be as abstract as it is stable.

Stability should be achieved through abstraction, not by freezing concrete implementations. Heavily-depended-upon packages should contain primarily interfaces.

- **Measurement**: For packages with I < 0.3, check A > 0.3. Stable-but-concrete = SAP violation.
- **Review question**: For heavily depended-upon packages — are they abstract enough to extend without modification?
- **Connection**: SAP + SDP together enforce DIP at the package level

---

## Metrics

### Coupling Metrics

| Metric | Formula | Range | Meaning |
|--------|---------|-------|---------|
| Ca (Afferent) | Count of packages depending on this one | 0..N | "Responsibility" — high = heavily depended upon |
| Ce (Efferent) | Count of packages this one depends on | 0..N | "Dependence" — high = reaches into many modules |

### Instability

```
I = Ce / (Ca + Ce)     range: [0, 1]
```

- **I = 0**: Maximally stable — many dependents, no dependencies. Difficult to change. Should be abstract.
- **I = 1**: Maximally unstable — no dependents, many dependencies. Easy to change. Should be concrete.

### Abstractness

```
A = abstract_types / total_types     range: [0, 1]
```

- **A = 0**: Entirely concrete. Fine if volatile (I=1). Problem if also stable (I=0).
- **A = 1**: Entirely abstract. Fine if stable (I=0). Problem if also volatile (I=1).

Count abstract classes, interfaces, and mixins as abstract types.

### Distance from Main Sequence

```
D = |A + I - 1|     range: [0, 1]
```

D = 0 means the package sits on the ideal main sequence. D > 0 means it's drifting toward a problem zone.

---

## The Main Sequence

The ideal: **A + I ≈ 1**

Packages should be either:
- **Stable and abstract** (I ≈ 0, A ≈ 1): core interfaces, domain models — heavily depended upon, extended without modification
- **Volatile and concrete** (I ≈ 1, A ≈ 0): implementations, adapters, plugins — free to change because nothing depends on them

---

## Problem Zones

### Zone of Pain (I ≈ 0, A ≈ 0)
Concrete and stable. Heavily depended upon but cannot be abstracted or extended.

- **Characteristics**: High change cost, low extensibility, cascading breakage
- **Classic examples**: Database schemas, utility libraries without abstractions, monolithic config classes
- **When acceptable**: Infrastructure genuinely stable by nature (database drivers, language runtime). NOT acceptable for business logic.
- **Fix**: Extract interfaces. Move concrete implementations behind abstractions.

### Zone of Uselessness (I ≈ 1, A ≈ 1)
Abstract and volatile. Nobody depends on it — the abstraction serves no consumer.

- **Characteristics**: Orphaned interfaces, unused abstract base classes, speculative generalization
- **When acceptable**: During active design/prototyping (temporary). Not acceptable in production.
- **Fix**: Find consumers and wire them up, or delete the dead abstraction.

---

## SOLID at Package Level

| Class-Level | Package-Level | Mapping |
|-------------|---------------|---------|
| SRP | CCP | One reason to change per package |
| OCP | SAP | Stable packages open for extension via abstraction |
| LSP | Substitutability | Implementing packages must be substitutable for their abstract package |
| ISP | CRP | Don't force consumers to depend on types they don't use |
| DIP | SDP + SAP | Depend on abstractions; dependencies point toward stability |

---

## Lakos Metrics

From John Lakos's "Large-Scale C++ Software Design." Computable from any dependency graph.

| Metric | Definition | Interpretation |
|--------|-----------|----------------|
| CD (Component Dependency) | Nodes reachable from X (including itself) | Blast radius of changes to X |
| CCD (Cumulative Component Dependency) | Sum of CD across all nodes | Total coupling in the graph |
| ACD (Average Component Dependency) | CCD / N | Average reachability; perfect = 1, tangled = O(N²) |
| NCCD (Normalized CCD) | CCD / CCD_of_balanced_binary_tree(N) | < 1.0 = better than baseline; > 1.0 = worse |

**For Dart**: `lakos` computes all of these. Run `lakos --metrics --node-metrics <package_dir>`.

---

## Thresholds

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| D (distance) | < 0.3 | 0.3 – 0.5 | > 0.5 |
| NCCD | < 1.0 | 1.0 – 2.0 | > 2.0 |
| Ce (efferent) | < 8 | 8 – 12 | > 12 (God Module) |
| Ca with A < 0.1 | < 5 | 5 – 10 | > 10 (concrete hotspot) |
| Cycles | 0 | Any 2-node | > 3-node cycle |
| Package LOC | < 3000 | 3000 – 10000 | > 10000 |
| Consumer waste | < 30% | 30 – 50% | > 50% (split signal) |

These thresholds are guidelines, not laws. Context matters — a core utility package will naturally have high Ca. The question is whether high Ca is justified by the package's role and whether it's abstract enough (SAP).
