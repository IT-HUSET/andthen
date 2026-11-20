# Architecture – Fitness Mode

Propose fitness functions for governance and ADR enforcement.

## Workflow

### Step 1 – Analyze Current Architecture

Identify which architectural properties are currently protected (existing tests, CI checks, lint rules) and which are unprotected.

### Step 2 – Map ADRs

Check which ADRs have corresponding automated enforcement. An active ADR with no automated check is a **governance gap** and a finding.

New fitness functions are written in the same PR as the ADR and link both ways – the test names the ADR number, the ADR names the test location.

### Step 3 – Propose Functions

Organize proposals by the 4-level governance stack:

- **Level 1 – fast deterministic** (every commit, < 30s): dependency-direction rules, cycle detection at zero tolerance, naming conventions, import restrictions, CVE scan.
- **Level 2 – structural** (every PR, 1-5 min): layer-violation tests, module-boundary assertions, coupling thresholds, interface/implementation isolation, test-ratio regression.
- **Level 3 – integrative** (nightly/weekly): contract tests and schema compatibility, DORA trends, build-time budget, full graph analysis, consumer-waste analysis.
- **Level 4 – continual** (production): latency budgets, error-rate thresholds, SLO compliance, resource bounds, security event monitoring.

Default thresholds to propose unless the project's own evidence says otherwise:

- **Modularity** – declared layer directions asserted by an architecture test; any dependency cycle fails CI; public interfaces must not depend on private implementations.
- **Coupling** – SDP asserted per edge; Ce and concrete-hotspot Ca at the calibration's critical thresholds.
- **Cohesion** – LCOM* > 0.8 **and** > 200 LOC; the God Module composite from the calibration's traps; feature scatter – packages importing a cross-cutting concern directly instead of through a facade.
- **Testability** – test files / production files per module: < 0.5 warning, < 0.2 fail for new modules; constructor-injected mocks per test class above 4–5; cyclomatic complexity per function < 10 healthy, 10–15 warning, > 15 fail.
- **Deployability** – build-time baseline plus regression alert; no service's test suite imports another service's source.
- **Security** – a direct dependency with CVE ≥ CVSS 7.0 fails, > 18 months behind latest warns; only designated entry-point layers expose public endpoints (HTTP annotations on inner layers are violations); no source file contains `.ssh/`, `.aws/credentials`, `BEGIN RSA PRIVATE KEY`.
- **Performance** – p99 latency budget; query count per request capped per endpoint (N+1 guard).

Each proposal gives:

- name;
- what it checks;
- threshold;
- implementation approach, in the stack's tooling (`review-output.md` § Language Tooling); where the stack has no architecture-test library, compose the check from its dependency-graph tool, its analyzer, and a script walking the import graph;
- which ADR it enforces;
- severity if violated;
- the failure message, which says what to do instead.

### Step 4 – Prioritize

Rank by: (1) blast radius if violated, (2) likelihood of accidental violation, (3) implementation effort.

Start with 3 fitness functions and grow; 5–6 actively governed dimensions is a mature codebase, not a starting bar. Fitness functions that enforce seams are runway investment – roughly 2–4 sprints of prepared capacity is the calibration, below which teams pay architecture tax continuously and above which it is speculative.

## Output

Fitness-mode report opens with Step 1's governance coverage assessment and How to Read This Report (compact legend for ADR, governance levels, and any architecture shorthand used), then carries the Step 2–4 artifacts in order.
