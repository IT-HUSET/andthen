# Architecture Review Calibration

Domain-specific calibration for reviewing package/module architecture. Load `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` first for universal calibration principles (anti-leniency protocol, finding quality, over-leniency patterns), then apply the domain-specific calibration below.


## Severity Calibration — Contrastive Examples

Each pair shows what IS and is NOT that severity level. Use these to calibrate your severity assignments.

### Critical

**IS Critical:**
> Dynamic connascence of Identity (CoI) crossing a service boundary: `OrderService` and `PaymentService` both hold a reference to the same mutable `TransactionContext` singleton. A race condition causes payment status to leak between unrelated orders. — Severity formula: strength=9, degree=4, locality=1 -> score 36.0

Why: Dynamic connascence across a package boundary is categorically dangerous. CoI means both sides must reference the exact same instance — any change to that instance affects all holders. This is invisible to static analysis and creates race conditions.

**IS Critical:**
> 5-node dependency cycle: `config` -> `channel` -> `task` -> `events` -> `logging` -> `config`. All 5 packages are effectively one deployment unit — changing any one requires recompiling and retesting all 5. SCC analysis confirms no subset can be independently deployed.

Why: Cycles with >3 nodes are architectural emergencies. They destroy independent deployability and make the dependency graph unmaintainable.

**is NOT Critical (common over-escalation):**
> Package `utils` has D=0.85 (Zone of Pain). It contains 12 concrete utility classes with Ca=8.

Why: High D-score alone is not Critical. Utility packages naturally sit in the Zone of Pain when they contain stable, rarely-changing concrete code. If the utilities genuinely don't change, the cost of abstraction exceeds the benefit. This is Medium — worth monitoring, not an emergency. Check change frequency before escalating.

**is NOT Critical:**
> Two-node dependency cycle between `models` and `serialization` — `models` imports serialization annotations, `serialization` imports model types.

Why: Two-node cycles are HIGH, not CRITICAL. They are typically solvable with a single interface extraction. Reserve CRITICAL for larger cycles (3+ nodes) or cycles involving core business packages.


### High

**IS High:**
> SDP violation: `core` package (I=0.08, stable) depends on `plugins` package (I=0.92, volatile). Any change to the plugin interface forces a change to the stable core. 14 downstream packages transitively inherit this volatility. — Per SDP (Martin): stable packages must not depend on volatile packages.

Why: A measurable principle violation with quantified blast radius. The dependency arrow points from stability toward instability, making the "stable" package fragile.

**IS High:**
> Package `domain` has I=0.05, A=0.03, D=0.92 — deep in the Zone of Pain. Contains 8 concrete domain model classes with no interfaces. 11 packages depend on it. Any field addition to a domain entity cascades to all 11 dependents. — Per SAP (Martin): stable packages should be abstract.

Why: Concrete + stable + heavily depended upon = every change is expensive. The package needs interfaces so dependents can be shielded from implementation changes.

**is NOT High (common over-escalation):**
> Package `database_driver` has I=0.02, A=0.0, D=0.98 — extreme Zone of Pain. Contains only concrete connection pool and query builder classes.

Why: Database driver packages are infrastructure genuinely stable by nature. They rarely change and represent external dependencies, not business logic. This is INFO — note the metrics but don't flag as a problem unless the package contains business logic or changes frequently.

**is NOT High:**
> Ce=9 for the `api_gateway` package. Approaches the Ce>10 "God Module" threshold.

Why: Approaching a threshold is not the same as exceeding it. An API gateway naturally has high efferent coupling — it's the entry point that routes to many services. Report as INFO with context, not as a finding.


### Medium vs Low vs Info

**IS Medium:**
> Package `auth` has D=0.45 (Zone of Pain, warning range). Contains 3 concrete implementations with Ca=6 but no interfaces. Change frequency: 2-3 commits/month.

Why: Moderate drift from the main sequence in a package that changes regularly. Not urgent, but worth extracting interfaces before more dependents accumulate.

**IS Low:**
> Inconsistent package naming: `user_management` uses snake_case while `OrderProcessing` uses PascalCase. No impact on dependency structure.

Why: Convention violation with no structural consequence. Worth noting for consistency but doesn't affect coupling or deployability.

**IS Info:**
> Package `helpers` has D=0.32 — just above the 0.3 warning threshold. Ce=5, Ca=3. Relatively balanced.

Why: Marginally outside the healthy range. Log for awareness but don't flag as a finding that requires action.


## False Positive Traps

Patterns that look like architecture problems but aren't. Check before recording a finding:

1. **Infrastructure in the Zone of Pain.** Database drivers, logging frameworks, serialization libraries, and language runtime bindings naturally sit at I~0, A~0. These are stable by nature, not by accident. Only flag if the package contains business logic or changes frequently.

2. **Leaf packages with high Ce.** Application-layer packages (CLI entry points, web controllers, test harnesses) naturally depend on many modules. High Ce at I~1 is expected — these are the "wiring" packages. Check that they are actually leaves (Ca~0) before flagging.

3. **Small packages with high Ca.** A tiny shared types package depended on by everything is not a God Module — it's a correctly extracted shared kernel. Check LOC and complexity alongside Ce before applying the God Module label.

4. **Cross-module CoN as a finding.** Connascence of Name is the weakest form and unavoidable across public APIs. Only flag CoN when names are ambiguous or inconsistent — not for the mere existence of cross-package name references.

5. **Theoretical decomposition benefits.** "This package could be split" is not a finding. Apply the 4-criteria check and score actual drivers. If no consumer would import the sub-package independently, the split adds complexity without benefit. Per Newman: "Do you have a compelling reason?"

6. **Monorepo structure confused with coupling.** Packages in a monorepo sharing a build system is not architectural coupling. Coupling is measured by import edges and runtime dependencies, not repository topology.
