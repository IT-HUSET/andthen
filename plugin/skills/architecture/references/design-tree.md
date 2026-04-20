# Design Space Decomposition

Use this when a decision has multiple meaningful dimensions and a flat list of "options" would hide the real trade-offs.

## When to Use

- **`clarify`**: surface hidden decisions and turn them into explicit questions
- **`trade-off`**: generate viable solution combinations before comparing them
- **`plan`**: separate independent dimensions into parallel stories and keep coupled decisions together

Skip this for simple, single-axis choices. If the real question is just "which database?" or "which library?", compare the options directly.

## Key Principle: Dimension Independence

Default to **independent peer dimensions**, not hierarchy.

- **Independent dimensions**: any option from A could in principle combine with any option from B
- **Dependent dimensions**: a parent choice changes what options exist for the child

Handle incompatibilities in cross-consistency notes, not by inventing a tree too early. Only nest when one choice truly determines the available choices below it.

## How to Construct

### 1. Name the Decision
State the feature, capability, or design question being explored.

### 2. Decompose into Dimensions
List 3-7 independent axes of choice.

Ask:
- What separate decisions are bundled together here?
- Which choices can change without automatically changing the others?
- Which distinctions matter to users, operators, or implementers?

### 3. List Options per Dimension
List 2-5 viable options per dimension.

Rules:
- Keep only realistic options
- Use codebase and domain language, not abstract placeholders
- Avoid "nice to have someday" brainstorming

### 4. Run Cross-Consistency Assessment
Mark important pairs as:
- **Compatible**
- **Incompatible**
- **Conditional**: works only if some condition is true

This is the pruning step. The goal is not to rank options yet; it is to rule out combinations that do not make sense.

### 5. Derive Viable Combinations
Pick the 2-4 combinations worth deeper evaluation or specification.

Each candidate should be one option per dimension plus any important conditions.

## Output Shapes

### Compact List
Use for most documentation:

```text
[Decision]
- [Dimension A]: [Option 1] | [Option 2] | [Option 3]
- [Dimension B]: [Option X] | [Option Y]
- [Dimension C]: [Option P] | [Option Q]
```

### Morphological Matrix
Use when you need to reason systematically about combinations:

```text
| Dimension | Option 1 | Option 2 | Option 3 |
|-----------|----------|----------|----------|
| A         | ...      | ...      | ...      |
| B         | ...      | ...      |          |
| C         | ...      | ...      | ...      |
```

### Hierarchical Nesting
Use only for genuine dependency:

```text
API Design
- Protocol: REST | GraphQL | gRPC
  - If GraphQL: Error handling uses GraphQL errors
  - If gRPC: Versioning and status codes follow gRPC conventions
- Authentication: JWT | Sessions | API keys
```

## Example

```text
Caching Strategy
- Invalidation: TTL | Event-driven | Hybrid
- Storage: In-process | Redis/Valkey | CDN edge
- Scope: Request | User/session | Shared
- Consistency: Strong | Eventual | Read-your-writes
```

Cross-consistency notes:
- `CDN edge` + `Strong` -> incompatible
- `In-process` + `Shared` -> incompatible in multi-instance deployments
- `Request` + `Event-driven` -> usually unnecessary

## Using the Output

### In `clarify`
- Turn unresolved dimensions into discovery questions
- Capture resolved dimensions as explicit decisions
- Keep open dimensions visible instead of quietly choosing defaults

### In `trade-off`
- Compare viable combinations, not imaginary "complete solutions"
- Research only the contested dimensions and risky conditions

### In `plan`
- Independent dimensions often become separate stories
- Coupled dimensions belong in the same story
- High-uncertainty dimensions may need a spike first
