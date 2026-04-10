# Connascence Taxonomy

Connascence (Page-Jones, 1992; refined by Weirich) is a coupling quality metric. Two components are connascent if a change to one could require a change to the other to preserve correctness.

## Three Evaluation Dimensions

Every connascence instance has three orthogonal properties:

- **Strength** — How hard to detect and refactor. Static (compile-time) < Dynamic (runtime-only). Determines priority.
- **Degree** — How many entities are involved. More = worse. Scales the impact.
- **Locality** — How close the coupled elements are. Same class < same package < cross-package. Modulates severity.

### Severity Formula

```
Severity = (Strength × Degree) / Locality
```

- **Strength**: ordinal position in taxonomy (CoN=1, CoT=2, CoM=3, CoP=4, CoA=5, CoE=6, CoTm=7, CoV=8, CoI=9)
- **Degree**: count of files, classes, or call sites affected
- **Locality**: 3 = within-class, 2 = cross-class within package, 1 = cross-package

Example: CoM (strength=3) across 3 packages (degree=3, locality=1) → severity = (3 × 3) / 1 = **9.0**
Example: CoN (strength=1) within a class (degree=2, locality=3) → severity = (1 × 2) / 3 = **0.67**

---

## Strength Ordering (weakest → strongest)

```
CoN → CoT → CoM → CoP → CoA → CoE → CoTm → CoV → CoI
 ←——————— Static ————————→  ←————————— Dynamic ——————————→
```

**Critical axiom**: Any dynamic connascence is categorically worse than any static connascence, regardless of specific types. Dynamic forms require runtime reasoning to detect — invisible to static analysis, harder to test, harder to review.

---

## Static Connascence

### CoN — Connascence of Name (Strength: 1, Weakest)

Multiple components must agree on the name of an entity.

```dart
// Every caller of startSession() has CoN with this declaration
session.startSession();
```

- **Why problematic across boundaries**: Renames propagate to all callers across packages. Public API renames require coordinated consumer updates.
- **Detection**: Unavoidable — all code has it. Flag only when names are ambiguous or inconsistent across packages (package A says `startSession`, B says `beginSession` for the same concept).
- **Refactoring target**: This IS the target. All other reductions should aim to reach CoN.

### CoT — Connascence of Type (Strength: 2)

Multiple components must agree on the type of an entity.

```dart
// Provider and consumer must agree userId is String, not int
void processUser(String userId) { ... }
```

- **Why problematic across boundaries**: Type changes in shared models require recompilation of all consumers. In dynamic languages, invisible until runtime.
- **Detection**: Flag runtime type checks (`is`, `as`), wide use of `dynamic` or `Object` — these indicate CoT the type system isn't enforcing.
- **Refactoring**: Consolidate shared types into a dedicated models package. Use sealed interfaces for enumerated types. Replace `dynamic` with proper types.

### CoM — Connascence of Meaning (Strength: 3)

Multiple components must agree on the meaning of specific values. Also called Connascence of Convention.

```dart
// Magic number — "1" means admin, "0" means user (implicit)
if (user.role == 1) grantAdminAccess();

// Boolean positional parameter — what does `true` mean?
PStore.new("demo.store", true);

// Sentinel value — "-1" means "not found"
if (userId == -1) insertUser(user);
```

- **Why problematic across boundaries**: Meaning lives in developers' heads, not the type system. When convention changes, both sides silently break.
- **Detection**: Flag magic numbers, boolean positional params, sentinel return values, undocumented string constants used as identifiers.
- **Refactoring**: Extract to enums, named constants, keyword arguments, or typed result types.

### CoP — Connascence of Position (Strength: 4)

Multiple components must agree on the order of values.

```dart
// Caller must know: first=firstName, second=lastName, third=age
void createUser(String firstName, String lastName, int age) { ... }
createUser("Löfstrand", "Tobias", 40); // SILENT BUG — compiles, wrong semantics
```

- **Why problematic across boundaries**: Same-type positional parameters are invisible errors. Reordering compiles but corrupts data.
- **Detection**: Flag methods with 3+ positional parameters. Flag 2+ positional parameters of the same type in public APIs.
- **Refactoring**: Use named/keyword parameters, data classes, or builder pattern.

### CoA — Connascence of Algorithm (Strength: 5, Strongest Static)

Multiple components must independently implement the same algorithm.

```dart
// Encrypter in service layer
String encrypt(String value) => sha256.convert(utf8.encode(value)).toString();

// Validator in another package — must use IDENTICAL algorithm
bool validate(String raw, String hash) =>
  sha256.convert(utf8.encode(raw)).toString() == hash;
```

- **Why problematic across boundaries**: No type system enforces algorithmic identity. If one side changes (SHA-256 → SHA-512), the other silently breaks.
- **Detection**: Look for duplicated transformation logic across packages. Check for hash, encoding, serialization routines appearing more than once.
- **Refactoring**: Extract to single authoritative location. Use Strategy pattern to inject the algorithm.

---

## Dynamic Connascence

### CoE — Connascence of Execution (Strength: 6)

The order of execution must be correct for the system to behave correctly.

```dart
article.publish();   // BUG: must call generate() first
article.generate();
```

- **Why problematic across boundaries**: Callers must know the internal operation order of the callee — an implementation detail leaked into orchestration.
- **Detection**: Look for `init()` methods, ordered multi-step setup without builder/factory, ordering documented only in comments.
- **Refactoring**: Template Method pattern, factory methods, state machines that make valid transitions explicit.

### CoTm — Connascence of Timing (Strength: 7)

Timing of execution (not just order) affects correctness — race conditions, timeouts, cache TTLs.

```dart
cache.write(key, data);
await Future.delayed(Duration(seconds: 61));
cache.read(key); // null — TTL expired
```

- **Why problematic across boundaries**: Timing assumptions are invisible in code. A cache consumer in one package assumes a TTL set in another.
- **Detection**: Flag hardcoded `sleep`/`delay` for coordination. Flag retry logic with magic delay constants. Flag cache interactions with assumed-but-unhandled TTL.
- **Refactoring**: Use `async/await` to declare temporal dependencies. Add explicit timeout handling. Use circuit breakers for cross-service timing.

### CoV — Connascence of Values (Strength: 8)

Multiple values across components are related by a constraint and must change together.

```dart
// Two packages independently define the same constraint
// Package A:
const defaultPageSize = 100;
// Package B:
const maxResultsPerPage = 100; // Same constraint, different name — will drift
```

- **Why problematic across boundaries**: Partial updates create inconsistent state. Root cause of distributed transaction complexity.
- **Detection**: Flag duplicate constant definitions across packages. Flag multi-step operations that must succeed atomically but have no rollback.
- **Refactoring**: Centralize related constants in a shared package. Use Saga pattern for distributed value constraints. Use event sourcing.

### CoI — Connascence of Identity (Strength: 9, Strongest)

Multiple components must reference the exact same object instance.

```dart
// Both publisher and subscriber must share the SAME queue instance
final publisher = Publisher(); // Creates internal queue
final subscriber = Subscriber();
subscriber.consume(publisher); // Works only if same queue
```

- **Why problematic across boundaries**: Changes to the shared entity affect all holders. Makes testing impossible without providing shared instances. Creates race conditions in concurrent code.
- **Detection**: Look for shared mutable singletons, static mutable state, objects passed by reference where mutations are expected to be observed by multiple holders.
- **Refactoring**: Dependency injection (DI container owns shared instances). Value semantics with immutable objects. Copy-on-write patterns.

---

## Guiding Principles

### Page-Jones's Three Guidelines
1. **Minimize overall connascence** — encapsulate to reduce total coupling surface
2. **Minimize connascence crossing encapsulation boundaries** — cross-package coupling should be CoN or CoT only
3. **Maximize connascence within encapsulation boundaries** — high internal connascence IS cohesion

### Weirich's Two Rules
1. **Rule of Degree**: Convert strong forms into weaker forms (CoP → CoN via named params)
2. **Rule of Locality**: As distance increases, use weaker forms. Tolerate CoA within a class; across a package boundary, reduce to CoN/CoT

### Decision Framework for Package Boundaries
- If all cross-boundary coupling is CoN/CoT: boundary is healthy. Keep it.
- If cross-boundary coupling includes CoM/CoP/CoA: medium severity — refactoring targets before boundary can be considered stable.
- If ANY cross-boundary coupling is dynamic (CoE/CoTm/CoV/CoI): strong merge signal or must-fix refactoring target.

---

## Detection Automation

| Type | Difficulty | Approach |
|------|-----------|----------|
| CoM | Easy, high value | Lint for magic numbers, boolean positional params, string sentinels |
| CoP | Easy, high value | Flag 3+ positional params of same type; 4+ total positional in public API |
| CoA | Medium | Code duplication detection across package boundaries |
| CoE | Medium | Pattern-match `init()` anti-patterns, ordered setup without builder |
| CoI | Medium-hard | Flag shared mutable singletons, static mutable state |
| CoTm | Hard | Flag `sleep`/`delay` coordination as heuristic proxy |
