# Design Space Decomposition

Use this when a decision has multiple meaningful dimensions and a flat list of "options" would hide the real trade-offs.

## When to Use

- **the `andthen:clarify` skill**: surface hidden decisions and turn them into explicit questions
- **the `andthen:architecture` skill (`--mode trade-off`)**: generate viable solution combinations before comparing them
- **the `andthen:plan` skill**: reuses this decomposition concept inline; this canonical file is not install-inlined into `plan`

Skip this for simple, single-axis choices. If the real question is just "which database?" or "which library?", compare the options directly.

## Key Principle: Dimension Independence

Default to **independent peer dimensions**, not hierarchy.

- **Independent dimensions**: any option from A could in principle combine with any option from B
- **Dependent dimensions**: a parent choice changes what options exist for the child

Handle incompatibilities in cross-consistency notes, not by inventing a tree too early. Only nest when one choice truly determines the available choices below it.

## Cross-Consistency Rubric

Mark important pairs as:
- **Compatible**
- **Incompatible**
- **Conditional**: works only if some condition is true

This is the pruning step. The goal is not to rank options yet; it is to rule out combinations that do not make sense.

## Output Shapes

Three named shapes; pick the one whose information density matches the decision.

### Compact List
Default for inline use in specs and clarification docs:

```text
[Decision]
- [Dimension A]: [Option 1] | [Option 2] | [Option 3]
- [Dimension B]: [Option X] | [Option Y]
- [Dimension C]: [Option P] | [Option Q]
```

### Morphological Matrix
Use when you need to reason systematically about combinations across many dimensions:

```text
| Dimension | Option 1 | Option 2 | Option 3 |
|-----------|----------|----------|----------|
| A         | ...      | ...      | ...      |
| B         | ...      | ...      |          |
| C         | ...      | ...      | ...      |
```

### Hierarchical Nesting
Use only for genuine dependency where a parent choice changes what options exist for the child:

```text
API Design
- Protocol: REST | GraphQL | gRPC
  - If GraphQL: Error handling uses GraphQL errors
  - If gRPC: Versioning and status codes follow gRPC conventions
- Authentication: JWT | Sessions | API keys
```

## Example

Caching Strategy dimensions:
- Storage: `In-process` | `Redis/Valkey` | `CDN edge`
- Consistency: `Strong` | `Eventual` | `Read-your-writes`
- Scope: `Per-user` | `Shared` | `Per-tenant`
- Invalidation: `TTL` | `Event-driven` | `Request`

Cross-consistency notes:
- `CDN edge` + `Strong` -> incompatible
- `In-process` + `Shared` -> incompatible in multi-instance deployments
- `Request` + `Event-driven` -> usually unnecessary
