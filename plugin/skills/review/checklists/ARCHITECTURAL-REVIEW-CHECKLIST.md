# Architectural Review Checklist

Concise, actionable checklist for architectural reviews and validation.

---

## Pre-Review
- [ ] Understand architectural scope and intent
- [ ] Review project architectural guidelines (CLAUDE.md, ADRs)
- [ ] Identify changed components and their relationships
- [ ] Determine review mode (design, implementation, advisory)

---

## CUPID Principles Assessment

Rate each 1-5, provide specific observations:

### C - Composable (Dependencies, coupling, reusability)
- [ ] Components work together seamlessly with minimal dependencies
- [ ] Clear, well-defined interfaces between components
- [ ] Minimal coupling, easy to swap/extend components
- [ ] Plugin architectures and extensibility patterns where appropriate
- [ ] Framework-agnostic design where possible
- **Score**: _/5

### U - Unix Philosophy (Single responsibility, scope)
- [ ] Each component/service does one thing well
- [ ] Appropriate granularity (not too fine, not too coarse)
- [ ] Clear separation of concerns
- [ ] Focused APIs without feature creep
- [ ] Well-defined boundaries
- **Score**: _/5

### P - Predictable (Clarity, consistency, robustness)
- [ ] System behavior consistent and unsurprising
- [ ] Consistent error handling patterns across components
- [ ] Predictable performance characteristics
- [ ] Well-defined failure modes and recovery patterns
- [ ] Clear data flow and state management
- [ ] Observable and debuggable behavior
- **Score**: _/5

### I - Idiomatic (Convention adherence, cognitive load)
- [ ] Industry-standard patterns followed
- [ ] Consistent technology choices across system
- [ ] Familiar deployment and operational patterns
- [ ] Team-appropriate technology selections
- [ ] Convention-over-configuration where beneficial
- **Score**: _/5

### D - Domain-Aligned (Business alignment, domain expression)
- [ ] System structure reflects business domains
- [ ] Service boundaries match business capabilities
- [ ] DDD principles applied appropriately
- [ ] Business-meaningful names and interfaces
- [ ] Technical and organizational boundaries aligned
- [ ] Business workflows clearly expressed
- **Score**: _/5

## Domain-Driven Design (DDD) Assessment

### Strategic Level
- [ ] Bounded contexts clearly defined and appropriately sized
- [ ] Context mapping accurately reflects business relationships
- [ ] Appropriate attention to core vs supporting vs generic subdomains
- [ ] Team boundaries aligned with context boundaries
- [ ] Anti-corruption layers used for external integrations
- [ ] Ubiquitous language established and used consistently

### Tactical Level
- [ ] Domain concepts clearly expressed in model
- [ ] Entities properly identified (unique identity, mutable state)
- [ ] Value objects used appropriately (immutable, compared by value)
- [ ] Aggregates enforce business invariants correctly
- [ ] Aggregate roots properly defined (single entry point)
- [ ] Domain services for operations not fitting entities/value objects
- [ ] Domain events capture important business occurrences
- [ ] Repositories provide clean abstraction for aggregates

### DDD Anti-Patterns (Check for violations)
- [ ] No anemic domain model (behavior in domain objects, not just data)
- [ ] No leaky abstractions (domain pure, no tech concerns)
- [ ] No context explosion (contexts appropriately sized)
- [ ] No over-engineered generic subdomains
- [ ] No big ball of mud (clear boundaries)

## Pattern Adherence & Architecture Compliance

### Clean Architecture / Layering
- [ ] Dependency rule respected (dependencies point inward)
- [ ] Domain layer pure (no framework/infrastructure dependencies)
- [ ] Application layer orchestrates domain operations
- [ ] Infrastructure layer implements technical concerns
- [ ] Layer boundaries not crossed inappropriately
- [ ] Proper abstractions at layer boundaries (interfaces, DTOs)

### Service Architecture
- [ ] Service boundaries clear and well-justified
- [ ] Appropriate service granularity for context
- [ ] High cohesion within services
- [ ] Low coupling between services
- [ ] Service communication patterns appropriate (sync/async)
- [ ] Shared database anti-pattern avoided
- [ ] No distributed monolith (excessive sync dependencies)

### API Design
- [ ] Clear API contracts and documentation (OpenAPI, GraphQL schema, etc.)
- [ ] RESTful principles followed (or GraphQL/gRPC as appropriate)
- [ ] Proper HTTP status codes
- [ ] Request/response validation
- [ ] Versioning strategy for breaking changes
- [ ] Rate limiting implemented for public APIs
- [ ] CORS configured correctly
- [ ] API design supports usability and discoverability

### Data Architecture
- [ ] Database choice appropriate (SQL vs NoSQL)
- [ ] Schema design reflects domain model
- [ ] Proper indexing strategy for queries
- [ ] Data access patterns well-defined (repository, DAO, etc.)
- [ ] Transaction boundaries appropriate
- [ ] Data consistency and integrity constraints enforced
- [ ] Caching strategy appropriate (application, distributed, CDN)
- [ ] CQRS applied where beneficial (read/write separation)

## Anti-Pattern Detection

Check for these violations:
- [ ] No god objects (single classes with too many responsibilities)
- [ ] No circular dependencies
- [ ] No tight coupling (components changeable independently)
- [ ] No framework coupling (business logic framework-agnostic)
- [ ] No inappropriate intimacy (modules knowing too much about internals)
- [ ] No feature envy (methods using more of another class)
- [ ] No chatty interfaces (excessive back-and-forth)
- [ ] No shotgun surgery (changes requiring many file edits)
- [ ] No primitive obsession (using primitives instead of value objects)

## Performance & Scalability

### Scalability
- [ ] Horizontal/vertical scaling strategy clear
- [ ] Stateless design where appropriate
- [ ] Load balancing strategy defined
- [ ] Database scaling approach (read replicas, sharding, etc.)
- [ ] Caching strategy multi-layered and appropriate
- [ ] Resource contention identified and addressed

### Performance
- [ ] No obvious performance bottlenecks
- [ ] Database queries optimized (N+1 prevention, indexes)
- [ ] Appropriate data structures and algorithms
- [ ] Lazy loading used where beneficial
- [ ] Pagination implemented for large datasets
- [ ] Background processing for long-running tasks

## Resilience & Reliability

### Error Handling & Recovery
- [ ] Circuit breaker pattern for external dependencies
- [ ] Retry logic with exponential backoff
- [ ] Timeout handling appropriate
- [ ] Graceful degradation for failures
- [ ] Bulkhead pattern for resource isolation where needed
- [ ] Dead letter queues for failed messages

### Observability
- [ ] Logging strategy comprehensive (structured logging)
- [ ] Monitoring metrics defined (business and technical)
- [ ] Distributed tracing implemented for microservices
- [ ] Health check endpoints available
- [ ] Alerting strategy defined
- [ ] No sensitive data in logs

## Security Architecture

### Security Patterns
- [ ] Authentication strategy sound (OAuth, JWT, session-based)
- [ ] Authorization model appropriate (RBAC, ABAC, etc.)
- [ ] Security headers configured (CSP, HSTS, X-Frame-Options)
- [ ] HTTPS enforced throughout
- [ ] Secrets management strategy (no hardcoded secrets)
- [ ] Encryption at rest and in transit where required
- [ ] CSRF protection for state-changing operations
- [ ] Rate limiting and throttling implemented

### Security Best Practices
- [ ] Input validation at all boundaries
- [ ] Output encoding to prevent XSS
- [ ] Prepared statements to prevent SQL injection
- [ ] Least privilege principle applied
- [ ] Attack surface minimized
- [ ] Security by design, not afterthought

## Integration & Communication

### Integration Patterns
- [ ] Appropriate communication patterns (REST, GraphQL, gRPC, events)
- [ ] Synchronous vs asynchronous communication justified
- [ ] Message broker selection appropriate (Kafka, RabbitMQ, etc.)
- [ ] Event-driven architecture applied where beneficial
- [ ] Saga pattern for distributed transactions where needed
- [ ] API gateway pattern for cross-cutting concerns

### Event-Driven Architecture (if applicable)
- [ ] Domain events clearly defined
- [ ] Event schema versioning strategy
- [ ] Event sourcing applied appropriately
- [ ] Eventual consistency handled correctly
- [ ] Event replay capability where needed

## Deployment & Operations

### Deployment Architecture
- [ ] Deployment strategy clear (blue-green, canary, rolling)
- [ ] Environment parity maintained (dev/staging/prod)
- [ ] Configuration management externalized
- [ ] Feature flags for risky changes
- [ ] Database migration strategy safe (reversible, tested)
- [ ] Rollback procedure defined

### Infrastructure
- [ ] Infrastructure as code used
- [ ] Containerization strategy appropriate
- [ ] Orchestration platform justified (Kubernetes, etc.)
- [ ] Resource limits and quotas defined
- [ ] Auto-scaling configured appropriately

## Technical Debt & Maintainability

### Code Quality Architecture
- [ ] Code complexity manageable (cyclomatic complexity, nesting)
- [ ] Test architecture supports easy testing
- [ ] Test coverage adequate for critical paths
- [ ] Documentation architecture (API docs, ADRs, diagrams)
- [ ] Dependency management strategy (versions, updates, security)

### Technical Debt Assessment
- [ ] New technical debt identified and justified
- [ ] Technical debt prioritized and tracked
- [ ] Refactoring opportunities documented
- [ ] Migration paths for deprecated components
- [ ] Long-term sustainability considered

---

## Issue Classification

### 🚨 Critical Issues (Must Address)
- Architectural violations causing serious issues
- Security vulnerabilities at architectural level
- Data loss/corruption risks
- Performance/scalability blockers
- Breaking existing guarantees

### ⚠️ High Priority (Should Address)
- Anti-patterns requiring refactoring
- Maintainability concerns
- Coupling issues
- Missing abstractions
- Technical debt accumulation

### 💡 Suggestions (Consider)
- Refactoring opportunities
- Pattern improvements
- Performance optimizations
- Documentation enhancements
