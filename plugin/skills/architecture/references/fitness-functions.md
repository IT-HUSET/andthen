# Architectural Fitness Functions

"Any mechanism that provides an objective integrity assessment of some architectural characteristic(s)." — Ford, Parsons, Kua

Fitness functions are to architectural properties what unit tests are to domain behavior.

## Table of Contents
- [Taxonomy](#taxonomy)
- [The Governance Stack](#the-governance-stack)
- [Concrete Examples](#concrete-examples-by-dimension)
- [ADR-to-Fitness-Function Pipeline](#adr-to-fitness-function-pipeline)
- [Frozen Rules Pattern](#frozen-rules-pattern)
- [Tooling by Language](#tooling-by-language)

---

## Taxonomy

Every fitness function is classified across these dimensions:

| Dimension | Options | Description |
|-----------|---------|-------------|
| Scope | Atomic / Holistic | Single property vs. multiple interacting properties |
| Invocation | Triggered / Continual | On event vs. always running |
| Result | Static / Dynamic | Fixed threshold vs. context-adjusted |
| Execution | Automated / Manual | CI vs. human review |
| Applicability | Domain-specific / Cross-cutting | One context vs. everywhere |
| Origin | Intentional / Emergent | Deliberate decision vs. discovered through monitoring |

---

## The Governance Stack

Organize fitness functions into four levels by execution frequency and cost:

### Level 1 — Fast Deterministic (every commit, < 30s)
- Dependency direction rules (no upward imports)
- Cycle detection (zero tolerance)
- Naming conventions
- Import restriction (no internal package access from outside)
- Dependency age / CVE scan

### Level 2 — Structural (every PR, 1-5 min)
- Layer violation tests
- Module boundary assertions
- Coupling metric thresholds (Ca, Ce, I, D)
- Interface/implementation isolation checks
- Test ratio regression check

### Level 3 — Integrative (nightly/weekly)
- Contract tests and schema compatibility
- DORA metric trends (change failure rate, lead time)
- Build time budget
- Full dependency graph analysis with NCCD
- Consumer waste analysis

### Level 4 — Continual (always running in production)
- Latency budgets (p99)
- Error rate thresholds
- SLO compliance
- Resource consumption bounds
- Security event monitoring

**Recommended starting point**: 3 fitness functions. Mature codebases: 5-6 actively governed dimensions.

---

## Concrete Examples by Dimension

### Modularity

**Dependency direction (layer enforcement)**
Define allowed dependency directions. Assert no violations.
```
# ArchUnit (Java)
layeredArchitecture()
  .layer("Controller").definedBy("..controller..")
  .layer("Service").definedBy("..service..")
  .whereLayer("Service").mayOnlyBeAccessedByLayers("Controller")
```

**Cycle detection**
Always zero tolerance. Any cycle is a violation.
```
# Dart (lakos)
lakos --no-cycles-allowed packages/dartclaw_core/lib/
# Exit code 5 = cycles found → fail CI
```

**API/implementation isolation**
Public interfaces must not depend on private implementations.

### Coupling

**Instability direction check (SDP)**
For each dependency edge A → B: assert I(A) ≥ I(B).

**Efferent coupling threshold**
Flag modules where Ce > threshold (default: 10) for review.

**Afferent coupling with low abstractness**
Flag modules where Ca > 10 AND A < 0.1 — concrete hotspot in Zone of Pain.

### Cohesion

**LCOM (Lack of Cohesion in Methods)**
Flag classes with LCOM* > 0.8 AND > 200 LOC.

**God module detection**
Composite: LOC > 1000 + Ce > 10 + mean cyclomatic complexity > 10 → all three = God Module.

**Feature scatter**
Count packages importing a cross-cutting concern directly (not through a facade). If > N, flag.

### Testability

**Test ratio**
Test files / production files per module. Threshold: < 0.5 = warning, < 0.2 = fail for new modules.

**Mock depth**
Average constructor-injected mocks per test class. Alert when > 4-5.

**Cyclomatic complexity per function**
< 10 = healthy, 10-15 = warning, > 15 = fail.

### Deployability

**Build time budget**
Baseline + alert on regression. If full build exceeds N minutes, flag.

**Independent deployability check**
No service's test suite imports classes from another service's source.

### Security

**Dependency age**
Any direct dependency with CVE ≥ CVSS 7.0 = fail. Any dependency > 18 months behind latest = warning.

**Attack surface boundary**
Only designated entry-point layers may expose public endpoints. Inner layers with HTTP annotations = violation.

**Sensitive path patterns**
No source file may contain `.ssh/`, `.aws/credentials`, `BEGIN RSA PRIVATE KEY`, etc.

### Performance

**Latency budget (continual)**
P99 response time under threshold.

**Query count per request**
No endpoint causes more than M database queries (guards against N+1).

---

## ADR-to-Fitness-Function Pipeline

An ADR records the decision; a fitness function enforces it. They are complementary:
- ADR without fitness function = documentation that may be ignored
- Fitness function without ADR = rule whose reasoning is opaque

### Pipeline
1. **ADR authored** with concrete prohibitions ("We will use X. We will not use Y.")
2. **Fitness function written** in the same PR as the ADR
3. **CI enforces** on every PR — violations block merge or require sign-off
4. **Bidirectional linking** — test references ADR number; ADR references test location

### Governance Gap Check
For each active ADR, verify at least one corresponding automated check exists. An ADR without a fitness function is a finding.

---

## Frozen Rules Pattern

For existing codebases with many violations, the "frozen rules" pattern enables progressive improvement:

1. Snapshot current violation count as baseline
2. Set the fitness function to fail only on NEW violations (count > baseline)
3. Optionally set a ratchet: as violations are fixed, lower the baseline
4. Eventually reach zero and switch to zero-tolerance mode

This prevents the "too many violations to fix, so we won't start" paralysis.

---

## Tooling by Language

### Java
- **ArchUnit** — architecture tests as JUnit tests. Layer enforcement, cycle detection, coding rules, PlantUML compliance.

### .NET
- **NetArchTest** — fluent API for namespace-based rules, naming conventions, dependency restrictions.

### JavaScript / TypeScript
- **dependency-cruiser** — rule engine with JSON config. Forbidden/allowed/required dependency patterns. `--output-type metrics` for numeric data.
- **ts-arch / ArchUnitTS** — ArchUnit-style declarative rules for TS.

### Python
- **Pyarchtest** — ArchUnit-style rules.
- **Deptry** — unused, missing, or transitive dependency detection.
- **import-linter** — contract-based import rules.

### Dart
No dedicated ArchUnit equivalent exists. Compose from:
- **`lakos`** — CCD, ACD, NCCD, instability per node, cycle detection, Graphviz DOT output
- **`dart pub deps --json`** — machine-readable package dependency graph
- **`dart analyze`** — static analysis with configurable severity
- **`custom_lint`** — write custom lint rules checking import patterns and structure
- **Custom `tool/arch_check.dart`** — use the `analyzer` package to walk AST, extract imports, assert layer rules

### Rust
- **`cargo tree`** — dependency tree
- **`cargo udeps`** — unused dependency detection
- **`cargo deny`** — license and advisory checks

### Go
- **`go mod graph`** — dependency graph
- **`depguard`** — import allowlist/denylist linter
