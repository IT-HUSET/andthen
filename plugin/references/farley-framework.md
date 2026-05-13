# Farley's Complexity Management Framework

From Dave Farley's "Modern Software Engineering." Frames all of software engineering as solving two fundamental problems.

## Two Core Problems

### 1. Optimize for Learning
Software is design, not manufacturing – stay empirical, iterative, and feedback-driven.

### 2. Optimize for Managing Complexity
Systems that grow beyond single-team comprehension degrade toward "big ball of mud" absent deliberate discipline.

---

## Five Tools for Managing Complexity

### 1. Modularity
Decompose into independently changeable units. **Heuristic**: flat cost-of-change curve over time – "If I increment a counter here, what else do I need to know about the system to be confident the change is correct?"

### 2. Cohesion
"The bits that are closely related should be close together in the software." **Heuristic**: state the module's responsibility in one sentence; "and also..." signals low cohesion.

### 3. Separation of Concerns
Isolate the concern most likely to change (business rules, UI) from less-likely-to-change concerns (infrastructure). **Anti-pattern**: business logic coupled to its persistence or transport layer.

### 4. Information Hiding and Abstraction
Expose only what callers need. **Test**: if you change HOW this module implements its behavior, what breaks outside? If "nothing" – information hiding works.

### 5. Managing Coupling
Prefer interaction through stable abstractions. **Heuristic**: "Does this dependency reflect a genuine relationship, or just convenience?" Convenience coupling is accidental complexity.

---

## Testability as Architecture Proxy

Farley's most actionable insight:

> **Testability is a proxy metric for modularity.**

TDD "prefers software that's modular, cohesive, with separation of concerns, abstract, and loosely coupled – it's much easier to write tests for software with these properties."

**Review heuristic**: "How hard is it to write a unit test for this component?" is a reliable stand-in for "how modular and loosely coupled is this component?"

- Hard-to-test code = structurally coupled code
- If a test requires extensive mocking, large object graphs, or infrastructure – those are coupling signals, not test design problems
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

The ultimate diagnostic. Plot effort-per-feature over time:
- **Well-modularized** – flat curve. Adding feature N costs roughly the same as adding feature 3.
- **Poorly modularized** – exponential curve. Each feature is harder than the last because coupling forces understanding of more of the system.

If cost-of-change is accelerating, the architecture is failing – regardless of what other metrics say.
