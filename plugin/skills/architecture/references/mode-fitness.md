# Architecture – Fitness Mode

Propose fitness functions for governance and ADR enforcement.

## Step 1 – Analyze Current Architecture

Identify which architectural properties are currently protected (existing tests, CI checks, lint rules) and which are unprotected.

## Step 2 – Map ADRs

Check which ADRs have corresponding automated enforcement. An active ADR with no automated check is a **governance gap** and a finding: an ADR without a fitness function is documentation that may be ignored, a fitness function without an ADR is a rule with opaque reasoning. New ones are written in the same PR as the ADR and link both ways – the test names the ADR number, the ADR names the test location.

## Step 3 – Propose Functions

Organize proposals by the 4-level governance stack:

- **Level 1 – fast deterministic** (every commit, < 30s): dependency-direction rules, cycle detection at zero tolerance, naming conventions, import restrictions, CVE scan.
- **Level 2 – structural** (every PR, 1-5 min): layer-violation tests, module-boundary assertions, coupling thresholds, interface/implementation isolation, test-ratio regression.
- **Level 3 – integrative** (nightly/weekly): contract tests and schema compatibility, DORA trends, build-time budget, full graph analysis, consumer-waste analysis.
- **Level 4 – continual** (production): latency budgets, error-rate thresholds, SLO compliance, resource bounds, security event monitoring.

Default thresholds to propose unless the project's own evidence says otherwise:

- **Modularity** – declared layer directions asserted (ArchUnit `layeredArchitecture()`); cycles zero tolerance (`lakos --no-cycles-allowed <dir>`, exit 5 = cycles → fail CI); public interfaces must not depend on private implementations.
- **Coupling** – SDP asserted per edge; Ce and concrete-hotspot Ca at the calibration's critical thresholds.
- **Cohesion** – LCOM* > 0.8 **and** > 200 LOC; the God Module composite from the calibration's traps; feature scatter – packages importing a cross-cutting concern directly instead of through a facade.
- **Testability** – test files / production files per module: < 0.5 warning, < 0.2 fail for new modules; constructor-injected mocks per test class above 4–5; cyclomatic complexity per function < 10 healthy, 10–15 warning, > 15 fail.
- **Deployability** – build-time baseline plus regression alert; no service's test suite imports another service's source.
- **Security** – a direct dependency with CVE ≥ CVSS 7.0 fails, > 18 months behind latest warns; only designated entry-point layers expose public endpoints (HTTP annotations on inner layers are violations); no source file contains `.ssh/`, `.aws/credentials`, `BEGIN RSA PRIVATE KEY`.
- **Performance** – p99 latency budget; query count per request capped per endpoint (N+1 guard).

For each proposal give: name, what it checks, threshold, implementation approach (language-specific tooling), which ADR it enforces, and severity if violated. **Dart has no ArchUnit equivalent** – compose from `lakos` (CCD/ACD/NCCD, instability, cycles, DOT output), `dart pub deps --json`, `dart analyze`, `custom_lint`, and a `tool/arch_check.dart` walking the AST with the `analyzer` package.

## Step 4 – Prioritize

Rank by: (1) blast radius if violated, (2) likelihood of accidental violation, (3) implementation effort. Start with 3 fitness functions and grow; 5–6 actively governed dimensions is a mature codebase, not a starting bar. Fitness functions that enforce seams are runway investment – roughly 2–4 sprints of prepared capacity is the calibration, below which teams pay architecture tax continuously and above which it is speculative. A deliberately sacrificial architecture still gets fitness functions, pointed at handoff qualities – modularity, tests, documented interfaces – not long-term operational ones.

## Report Contents

Fitness-mode report opens with Step 1's governance coverage assessment and How to Read This Report (compact legend for ADR, governance levels, and any architecture shorthand used), then carries the Step 2–4 artifacts in order.
