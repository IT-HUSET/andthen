# Decomposition Analysis: Extract the audit client

## Boundary Map

```mapviz
[SignIn] "src/auth/routes"
[AuditClient] "src/audit/client"
[AuditStore] "external"
SignIn -> AuditClient : "write"
AuditClient -> AuditStore : "http"
```

Coupling points: the event union is shared by value between the handler and the client.

## Driver Scores

| Driver | Score |
|---|---|
| Change velocity divergence | 2 |
| Fault isolation | 5 |
| Scaling divergence | 1 |
| Data independence | 4 |
| Team ownership | 2 |
| Compliance isolation | 3 |
| Shared data | 4 |
| Latency sensitivity | 5 |
| Transaction span | 2 |
| Operational cost | 3 |

## Connascence Analysis

- **Connascence of type** across the boundary: the event union is compiled into both sides.
- **Connascence of timing**: the handler awaits the client, so the client's latency is the handler's.

## Evaluation Matrix

| Criterion | Result |
|---|---|
| a. Zero external dependencies | FAIL |
| b. Independent consumer use case | PASS |
| c. Acyclic DAG post-split | PASS |
| d. Low breaking-change cost | PASS |

## Recommendation

**Defer.** Criterion (a) fails: the client still owns the store's HTTP contract, so a split moves the dependency rather than removing it. Revisit when a second consumer of the audit client exists, or when fault isolation forces the buffer out of process.
