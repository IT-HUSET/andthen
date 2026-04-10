# Farley's Complexity Management Framework

From Dave Farley's "Modern Software Engineering." Frames all of software engineering as solving two fundamental problems.

## Two Core Problems

### 1. Optimize for Learning
Software is design, not manufacturing. Two-thirds of ideas from top software companies fail to produce expected value. The discipline must be empirical, iterative, and feedback-driven.

### 2. Optimize for Managing Complexity
Systems that grow beyond single-team comprehension degrade toward "big ball of mud" absent deliberate discipline.

---

## Five Tools for Managing Complexity

### 1. Modularity
Decompose systems into independently understandable, independently changeable units.

- **Test**: Can you change this module without understanding the whole system? Can you test it in isolation?
- **Effect**: Well-modularized systems maintain flat cost-of-change curves. Poorly modularized = exponential cost growth.
- **Review question**: "If I increment a counter here, what else do I need to know about the system to be confident the change is correct?"

### 2. Cohesion
The degree to which things inside a module actually belong together.

- **Heuristic**: "The bits that are closely related should be close together in the software."
- **Test**: Can you state in ONE sentence what this module is responsible for? If it requires "and also...", cohesion is low.
- **Anti-pattern**: Modules organized by technical role (all controllers together) rather than by domain — feature changes touch multiple layers.

### 3. Separation of Concerns
Distinct concerns (business logic, persistence, presentation, concurrency, security) should be structurally isolated.

- **Architectural application**: At LMAX, Farley's team isolated concurrency — business logic ran single-threaded, concurrency confined to I/O infrastructure. Both parts became simpler and more correct.
- **Review question**: Is the concern most likely to change (business rules, UI) isolated from less-likely-to-change concerns (infrastructure)?
- **Anti-pattern**: Business logic aware of its persistence mechanism; domain logic coupled to HTTP models.

### 4. Information Hiding and Abstraction
Expose only what callers need. Changes inside a module must not require changes in callers.

- **Test**: If you change HOW this module implements its behavior, what breaks outside? If "nothing" — information hiding works.
- **Leaky abstraction red flags**: Callers importing internal types, casting to implementation classes, depending on ordering that's an implementation artifact.

### 5. Managing Coupling
Minimize dependencies between modules. Prefer interaction through stable abstractions.

- **Coupling compounds**: Farley cites 300x performance penalty from poorly managed concurrency coupling.
- **Review question**: Does adding this dependency make sense because the things are genuinely related, or because the class is conveniently available? Convenience coupling is accidental complexity.
- **Anti-pattern**: "God classes" or service locators everything depends on; importing a package for one utility and getting 40 transitive deps.

---

## Testability as Architecture Proxy

Farley's most actionable insight:

> **Testability is a proxy metric for modularity.**

TDD "prefers software that's modular, cohesive, with separation of concerns, abstract, and loosely coupled — it's much easier to write tests for software with these properties."

**Review heuristic**: "How hard is it to write a unit test for this component?" is a reliable stand-in for "how modular and loosely coupled is this component?"

- Hard-to-test code = structurally coupled code
- If a test requires extensive mocking, large object graphs, or infrastructure — those are coupling signals, not test design problems
- Test friction is architectural feedback

---

## Deployability as First-Class Property

> "What is the unit of deployment? What thing can I evaluate until happy for production without further work?"

If the answer is "the entire system" → modularity is insufficient.
If the answer is an individual component → the architecture enables feedback.

**Key distinction**: Deployable ≠ Releasable. A component can be deployable (technically launchable in isolation) without being releasable (safe for user traffic). Deployment independence is the architectural property; release strategy is business policy.

---

## Feedback Loops

Architecture quality is readable from feedback loop speed.

> "Use the speed of feedback releasability to drive down and remove work and complexity until you can release every day."

- Minutes from change to confident deployment → architecture supports learning
- Days/weeks → architecture has coupling problems
- Each lengthening factor is a coupling problem to address

**Review question**: How long does it take from a code change to confident production deployment? What architectural factors lengthen that cycle?

---

## Cost-of-Change Curve

The ultimate diagnostic:
- **Well-modularized**: Flat cost-of-change curve over time. Adding feature N is roughly as expensive as adding feature 3.
- **Poorly modularized**: Exponential curve. Each feature is harder than the last because coupling means understanding more of the system.

If cost-of-change is accelerating, the architecture is failing — regardless of what the metrics say.
