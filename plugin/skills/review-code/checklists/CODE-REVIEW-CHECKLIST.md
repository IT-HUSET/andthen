# Code Review Checklist

Concise, actionable checklist for thorough code reviews.

---

## Pre-Review
- [ ] Understand code's purpose and context
- [ ] Review changed files (`git diff` or equivalent)
- [ ] Check project guidelines (CLAUDE.md, coding standards)

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

### Best Practices
- [ ] Language/framework idioms followed
- [ ] DRY principle applied pragmatically
- [ ] SOLID/CUPID principles respected (see guidelines)
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
- [ ] Responsibilities well-distributed (no god objects)
- [ ] Layer boundaries respected (no improper dependencies)
- [ ] Module/package structure logical
- [ ] Files/classes reasonably sized

### Testability
- [ ] Code testable (dependency injection, pure functions where possible)
- [ ] Test coverage adequate (critical paths, edge cases)
- [ ] Tests pass and are meaningful
- [ ] Tests are maintainable and readable
- [ ] Mock/stub usage appropriate

### Documentation
- [ ] Public APIs documented
- [ ] Complex algorithms explained
- [ ] Assumptions and constraints documented
- [ ] Breaking changes noted
- [ ] No obsolete comments or TODOs without context

### Configuration & Dependencies
- [ ] No hardcoded values (use config/env vars/constants)
- [ ] Dependencies version-pinned or ranged appropriately
- [ ] Feature flags used for risky changes
- [ ] Database migrations reversible

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

---

## Issue Classification

### 🚨 CRITICAL (Must Fix)
- Data loss/corruption risks
- Breaking changes/regressions
- Critical bugs

### ⚠️ HIGH (Should Fix)
- Performance issues
- Maintainability concerns
- Incorrect error handling
- Significant technical debt

### 💡 SUGGESTIONS (Consider)
- Code style improvements
- Refactoring opportunities
- Documentation enhancements
- Test coverage gaps
- Performance optimizations
