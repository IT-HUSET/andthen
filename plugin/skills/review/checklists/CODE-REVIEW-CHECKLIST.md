# Code Review Checklist

Concise, actionable checklist for thorough code reviews.

---

## Pre-Review
- [ ] Understand code's purpose and context
- [ ] Review changed files (`git diff` or equivalent)
- [ ] Check project guidelines (`CLAUDE.md` / `AGENTS.md`, coding standards)

---

## Code Quality

### Correctness & Logic
- [ ] No bugs or logical errors
- [ ] Edge cases handled (null/undefined, empty arrays, boundary conditions)
- [ ] Error handling comprehensive (try/catch, error propagation, user-friendly messages)
- [ ] Async operations handled correctly (promises, race conditions, error handling)
- [ ] Business logic correct and complete

### Readability & Clarity
- [ ] Code is simple, clear, self-documenting
- [ ] Naming is descriptive, consistent, follows conventions
- [ ] Functions/methods focused, reasonably sized
- [ ] Complex logic explained with comments where needed
- [ ] Magic numbers/strings replaced with named constants

### Baseline Smell Scan

Use this fixed Fowler-inspired baseline even when the repo has no local standards. A documented project standard overrides the baseline, and every smell is a judgement call: report as "possible <smell>" with concrete diff evidence and a bounded remedy, never as a hard violation. Skip anything static tooling already enforces.

- [ ] **Mysterious Name** – a function, variable, type, file, or test name hides what it does or represents; rename, or simplify until an honest name fits
- [ ] **Duplicated Code** – the same logic shape appears in multiple hunks/files; extract the shared shape or justify the duplication
- [ ] **Feature Envy** – behavior reaches into another object/module's data more than its own; move the behavior toward the data or expose an intention-revealing API
- [ ] **Data Clumps** – the same fields/params travel together repeatedly; introduce a value object, parameter object, or domain type
- [ ] **Primitive Obsession** – strings/numbers/booleans stand in for domain concepts with rules; model the concept explicitly where it protects invariants
- [ ] **Repeated Switches** – the same switch/if-cascade on the same type recurs; centralize the decision, use a map/strategy, or let polymorphism carry it
- [ ] **Shotgun Surgery** – one logical change forces scattered edits across many files; gather the reason-to-change behind one boundary
- [ ] **Divergent Change** – one file/module is edited for unrelated reasons; split responsibilities so each module has a coherent reason to change
- [ ] **Speculative Generality** – abstractions, hooks, params, or extension points serve no current requirement; inline/delete until a real need appears
- [ ] **Message Chains** – callers navigate long internal object/module paths; hide the traversal behind one intention-revealing method/API
- [ ] **Middle Man** – a wrapper mostly delegates without policy, translation, or boundary value; remove it or give it real responsibility
- [ ] **Refused Bequest** – a subclass/implementer ignores or overrides most inherited behavior; replace inheritance with composition or split the contract

### Best Practices
- [ ] Language/framework idioms followed
- [ ] DRY principle applied pragmatically
- [ ] SOLID/CUPID principles respected
- [ ] No code duplication without justification
- [ ] Appropriate design patterns used
- [ ] No anti-patterns (god objects, circular dependencies, tight coupling)

### Performance
- [ ] No obvious performance issues (N+1 queries, inefficient algorithms)
- [ ] Appropriate data structures used
- [ ] Resource usage reasonable (memory, CPU, network)
- [ ] Caching applied where beneficial
- [ ] Database queries optimized (indexes, pagination)

## Maintainability

### Code Organization
- [ ] Separation of concerns clear
- [ ] Responsibilities well-distributed
- [ ] Layer boundaries respected (no improper dependencies)
- [ ] Module/package structure logical
- [ ] Files/classes reasonably sized

### Testability
- [ ] Code testable (dependency injection, pure functions where possible)
- [ ] Test coverage adequate (critical paths, edge cases)
- [ ] Tests pass and are meaningful
- [ ] Tests are maintainable and readable
- [ ] Mocks/stubs confined to system edges (filesystem, network, clock, randomness); domain objects and the unit under test are not mocked
- [ ] Each test would fail if the asserted production behavior were removed; fixtures capture real outputs rather than substitute for the production computation

### Documentation
- [ ] Public APIs documented
- [ ] Complex algorithms explained
- [ ] Assumptions and constraints documented
- [ ] Breaking changes noted
- [ ] No obsolete comments or TODOs without context

### Configuration & Dependencies
- [ ] No hardcoded values (use config/env vars/constants)
- [ ] Dependencies version-pinned or ranged appropriately

### Technical Debt
- [ ] No new technical debt without explicit acknowledgment
- [ ] Workarounds documented with reason and follow-up plan
- [ ] Deprecated code usage avoided
- [ ] Code complexity reasonable (cyclomatic complexity, nesting depth)

## Additional Checks

### Regression Prevention
- [ ] Existing functionality still works
- [ ] Tests updated/added for changes
- [ ] Integration points validated
- [ ] Backward compatibility maintained or migration path clear

### Operational Concerns
- [ ] Logging appropriate (level, content, no sensitive data)
- [ ] Monitoring/observability supported (metrics, traces)
- [ ] Error messages actionable and user-friendly
- [ ] Graceful degradation for failures
- [ ] Resource cleanup (connections, files, memory)

### Deployment & Rollback
- [ ] Database migrations safe and reversible
- [ ] Feature flags for risky changes
- [ ] No breaking API changes without versioning
- [ ] Deployment risks identified

Severity: see [`review-calibration.md`](${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md) and the relevant `<lens>-review-calibration.md`
