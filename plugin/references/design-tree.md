# Design Space Decomposition

Systematically explore solution spaces by decomposing decisions into independent dimensions, then pruning incompatible combinations to derive viable candidate solutions.

> **Core idea**: Don't jump to comparing complete solutions. First identify the *dimensions* of the decision, then the *options per dimension*, then assess cross-consistency and prune, then derive viable combinations. This applies equally to architecture, UI/UX, and user-facing functionality.

> **Lineage**: This methodology draws on Fritz Zwicky's General Morphological Analysis (1940s), the QOC framework from HCI (MacLean et al. 1991), and design tree concepts from software architecture (Qian et al. 2009, Askren & Korkan 1971).


## When to Use

- **Requirements discovery** (`clarify`): Surface hidden decisions and ensure requirements capture choices for each dimension
- **Trade-off analysis** (`trade-off`): Systematic option discovery before evaluation – replaces ad-hoc "list N alternatives"
- **Story breakdown** (`plan`): Identify which dimensions are independent (separate/parallel stories) vs coupled (same story)

Skip for simple, single-dimensional decisions (e.g., "which database?" – just list the options directly).


## Key Principle: Dimension Independence

Dimensions are **independent peers**, not a hierarchy. The order in which they are listed carries no meaning – any option from dimension A can in principle be combined with any option from dimension B. Incompatibilities between specific options are handled through cross-consistency assessment (step 4), not through structural nesting.

This distinction matters:
- **Independent dimensions** → morphological matrix (flat, all dimensions are peers)
- **Dependent dimensions** → decision tree (hierarchical, parent constrains child)

Most design problems have primarily independent dimensions with some pairwise incompatibilities. Use the flat decomposition by default; only nest dimensions when one genuinely determines what options exist for another.


## How to Construct

### 1. Name the Decision
Identify the feature, capability, or decision being explored.

### 2. Decompose into Dimensions
List the **independent axes of choice** – aspects that can (in principle) be decided separately. Ask:
- What are the distinct design decisions embedded in this feature?
- Which choices are orthogonal (changing one doesn't force the others)?
- What would a user/stakeholder see as separate concerns?

Aim for 3–7 dimensions. Fewer than 3 usually means the decision is simple enough not to need this method. More than 7 becomes unwieldy without tooling.

### 3. List Options per Dimension
For each dimension, enumerate 2–5 viable approaches. Include only realistic options – this isn't brainstorming, it's structured exploration.

### 4. Cross-Consistency Assessment (CCA)
Evaluate **pairwise** compatibility between options across dimensions. For each pair of options from different dimensions, assess:

- **Compatible** – can coexist without issues
- **Incompatible** – logically contradictory, technically impossible, or practically unviable
- **Conditional** – works only under specific circumstances (note the condition)

This is the methodological core. The number of pairwise evaluations grows quadratically (not exponentially), making it tractable even for larger decompositions. CCA typically eliminates 70–95% of the theoretical combination space.

Document incompatibilities with rationale – they are auditable design decisions, not structural assumptions baked into the hierarchy.

### 5. Derive Viable Combinations
The remaining consistent combinations are your candidate solutions. Each is a tuple selecting one option per dimension. Select the most promising candidates for deeper evaluation or specification.


## Visualization

### Compact List (default for documentation)

Use for quick communication. Dimensions are peers – the list order is arbitrary:

```
[Feature Name]
├── [Dimension A]: [Option 1] · [Option 2] · [Option 3]
├── [Dimension B]: [Option X] · [Option Y]
├── [Dimension C]: [Option P] · [Option Q] · [Option R]
└── [Dimension D]: [Option M] · [Option N]
```

### Morphological Matrix (best for cross-consistency work)

Use when evaluating combinations systematically. Each row is a dimension, each cell an option. A candidate solution is one selection per row:

```
┌─────────────────┬──────────────┬──────────────┬──────────────┐
│ Dimension A     │ Option 1     │ Option 2     │ Option 3     │
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ Dimension B     │ Option X     │ Option Y     │              │
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ Dimension C     │ Option P     │ Option Q     │ Option R     │
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ Dimension D     │ Option M     │ Option N     │              │
└─────────────────┴──────────────┴──────────────┴──────────────┘

Candidate A: Option 1 + Option X + Option Q + Option M
Candidate B: Option 2 + Option Y + Option P + Option N
```

### When to Use Hierarchical Nesting

Only use tree nesting (parent → child) when a dimension is **genuinely dependent** – meaning the parent's choice determines what child options exist, not merely which are preferred:

```
API Design
├── Protocol: REST │ GraphQL │ gRPC
│   └── [if GraphQL] Error Handling: errors array (no other option)
│   └── [if gRPC] Versioning: package versioning (not URL-based)
├── Authentication: JWT │ Sessions │ API keys
└── Rate Limiting: token bucket │ sliding window │ fixed window
```

Here, error handling and versioning formats are structurally determined by protocol choice – genuine dependency, not just preference.


## Examples

### Architecture: Caching Strategy

```
Caching Strategy
├── Invalidation:  TTL-based · Event-driven (pub/sub) · Hybrid (TTL + event)
├── Storage:       In-process memory · Redis/Valkey · CDN edge · Multi-tier
├── Scope:         Per-request · Per-user/session · Global (shared)
└── Consistency:   Strong (invalidate-on-write) · Eventual (async) · Read-your-writes
```

**Cross-consistency issues:**
- "CDN edge" + "strong consistency" – incompatible (edge caches cannot guarantee strong consistency)
- "In-process memory" + "global scope" – incompatible in multi-instance deployments (no shared state)
- "Per-request scope" + "event-driven invalidation" – unnecessary complexity (request-scoped caches are inherently short-lived)


### UI/UX: User Onboarding

```
User Onboarding
├── Authentication:     Social login · Email+password · Magic link · SSO
├── Profile Completion: Required upfront (wizard) · Progressive · Optional (skip)
├── First-Run:          Guided tour · Contextual tooltips · Sample data · Self-discovery
└── Verification:       Email required · Phone (SMS) · None
```

**Cross-consistency issues:**
- "SSO" + "phone verification" – redundant (enterprise IdP handles identity trust)
- "Progressive profile" + "guided tour" – conditional (tour may need profile context to personalize; works if tour is generic)
- "Optional profile" + "required upfront wizard" – contradictory by definition
- "Self-discovery" + "magic link" – compatible but may compound unfamiliarity for new users


### UI/UX: Data Dashboard

```
Data Dashboard
├── Display Mode:   Table · Card grid · List view · Switchable (user toggles)
├── Filtering:      Sidebar (persistent) · Top bar dropdowns · Query builder · Faceted
├── Data Freshness: Real-time (WebSocket/SSE) · Polling · Manual refresh · Stale-while-revalidate
└── Bulk Actions:   Select + action bar · Row actions only · Context menu · Keyboard-driven
```

**Cross-consistency issues:**
- "Card grid" + "select + action bar" – awkward UX (cards lack the visual row structure that makes bulk selection intuitive)
- "Real-time" + "faceted navigation" – conditional (dynamic facet counts changing in real-time may cause layout thrashing; works with debouncing)
- "Query builder" + "card grid" – conditional (query builder implies power users who typically prefer table density)


### Architecture: API Design

```
API Design
├── Protocol:       REST · GraphQL · gRPC · tRPC
├── Authentication: JWT (stateless) · Session cookies · API keys · OAuth2 + refresh
├── Versioning:     URL path (/v1/) · Header-based · Query param · Additive only
└── Error Handling: HTTP status + RFC 9457 · Envelope (always 200) · GraphQL errors · gRPC codes
```

**Cross-consistency issues (with genuine dependencies):**
- "gRPC" forces "gRPC status codes" for error handling and its own versioning model – these are **dependent dimensions** under gRPC
- "GraphQL" forces "GraphQL errors array" – dependent
- "tRPC" + "URL versioning" – not applicable (tRPC uses TypeScript module structure)
- "API keys" + "session cookies" – conceptually different auth models; pick based on client type (machine vs. browser)

_Note: Protocol choice creates genuine dependencies for error handling and versioning. In a more rigorous decomposition, these dependent dimensions would nest under protocol rather than sit as peers._


## Using the Output

### In Requirements Discovery (`clarify`)
- Present the decomposition to surface decisions the user hasn't considered
- Each dimension becomes a question in the discovery interview
- Resolved dimensions become documented decisions; unresolved ones become open questions
- The decomposition and cross-consistency findings become part of the requirements output

### In Trade-off Analysis (`trade-off`)
- Use CCA to prune the combination space before investing in deep research
- Derive viable combinations as the options to evaluate in Phase 2
- Dimensions with obvious winners can be resolved immediately – focus research on contested dimensions
- The decomposition artifact accompanies the trade-off matrix

### In Story Breakdown (`plan`)
- **Independent dimensions** can map to separate, parallelizable stories
- **Coupled dimensions** (significant cross-consistency constraints) should be in the same story to avoid rework
- **Foundational dimensions** (ones others depend on) belong in earlier phases
- Dimensions with **high uncertainty** or contested options may warrant a spike/research story before implementation
- If a decomposition was produced upstream (by `clarify` or `trade-off`), reference and build on it


## Background

This methodology synthesizes several established approaches:

- **General Morphological Analysis** (Fritz Zwicky, 1940s) – the foundational method of decomposing problem spaces into independent parameters and systematically exploring combinations. The morphological matrix and cross-consistency assessment originate here.
- **QOC – Questions, Options, Criteria** (MacLean, Young, Bellotti, Moran, 1991) – the HCI/UX equivalent, where design questions decompose into options evaluated against criteria, with questions cascading hierarchically.
- **Design Option Decision Tree** (Askren & Korkan, 1971) – early systems engineering formalization showing design options at each decision point.
- **Feature Models** (Kang et al., FODA, 1990) – tree-structured variability representation in software product lines with mandatory/optional/XOR operators.
