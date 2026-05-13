# Architecture – Strategic-Design Mode

Discover or audit the strategic shape of a domain – classify subdomains by investment posture, propose bounded contexts and their sizing, draw the integration relationships between contexts, and surface the ubiquitous-language touchpoints. Outputs a textual report; UL extraction, board diagrams, and visual review are delegated to dedicated skills.

**Supporting references**: `ddd.md` (sections 1.1–1.4 – subdomain types, bounded contexts, the 9-pattern context-mapping catalog, team-topology alignment; section 4.2 – Bounded Context Canvas; section 5 – UL operationalization), `decomposition.md` (load when bounded-context sizing is contested – applies the cognitive-load heuristic, "team owns at most 2–3 low-complexity contexts").

## Subdomains – Quick Reference

Mirror Evans / Khononov ch. 1; full depth lives in `ddd.md` §1.1. Classify each subdomain into exactly one type, with a one-line rationale tying it to business differentiation and model complexity.

| Type | Investment | Pattern hint |
|---|---|---|
| **core** | Maximal – best engineers, full tactical DDD, richest model | Rich aggregates + domain events |
| **supporting** | Fit-for-purpose – pragmatic patterns, simpler model | Active Record, transaction script, thin domain model |
| **generic** | Minimal – prefer off-the-shelf; integrate, don't build | Don't model; wrap with ACL if the vendor model is hostile |

When the differentiation/complexity call is contested, plot subdomains on the Core Domain Chart (DDD Crew, Tune) and note the trade-off rather than forcing a verdict.

## Context-Mapping Pattern Catalog

Nine patterns – eight Evans canonical plus Big Ball of Mud (DDD Crew, as a quarantine strategy). Full table with coupling level, team relationship, and "choose when" guidance lives in `ddd.md` §1.3. Every pair of contexts in the report's Context Map names the pattern explicitly.

- **Partnership** – high coupling, shared fate; teams release together.
- **Shared Kernel** – small co-owned model subset; close communication.
- **Customer/Supplier** – upstream/downstream with the downstream having leverage on the upstream's roadmap.
- **Conformist** – downstream accepts the upstream model as authoritative.
- **Anticorruption Layer** – downstream wraps a hostile or legacy upstream to protect its model.
- **Open Host Service** – upstream publishes a stable API for many consumers.
- **Published Language** – shared exchange format (schemas, event envelopes); often pairs with OHS.
- **Separate Ways** – explicit non-integration; duplication is cheaper.
- **Big Ball of Mud** – quarantine strategy for legacy or entangled systems; never let the model contaminate neighbors (wrap with ACL).

Move toward the top of the catalog when teams are aligned and models are stable; toward the bottom when teams are distant, models are incompatible, or the upstream cannot be negotiated with.

## Bounded Context Canvas

For any single context that needs deeper scrutiny, fill the Bounded Context Canvas (DDD Crew, Tune): name and purpose, strategic classification (core/supporting/generic), domain roles, inbound/outbound messages, dependencies (upstream/downstream + integration patterns), ubiquitous-language excerpt. Full depth in `ddd.md` §4.2. Use as a per-context appendix when the report's main Bounded Contexts table cannot carry enough detail; skip when the high-level table suffices.

## Team-Topology Alignment

Context-mapping patterns map onto Team Topologies interaction modes – Partnership ↔ closely-collaborating stream-aligned teams, Conformist ↔ X-as-a-Service without negotiation, ACL ↔ platform team owns translation, OHS+Published Language ↔ platform team's stable API, Separate Ways ↔ fully independent stream-aligned teams. Full table in `ddd.md` §1.4. When team boundaries cut across context boundaries (Conway's Law violated), the distributed monolith is the predictable result – surface as a finding.

## Steps

### Step 1 – Scope and Inputs
Confirm the scope (whole project, one product line, or a named slice) and the input source. Two paths:

- **Greenfield** – drive from `requirements-clarification.md`, a PRD, or the user's narrative description. Treat the user as the domain expert; ask focused questions when subdomain boundaries or vocabulary are ambiguous.
- **Brownfield** – drive from observed structure: the `andthen:map-codebase` skill's outputs (Architecture, Stack), existing module boundaries, persisted entities, and cross-module API calls. Surface drift between the apparent map and the proposed target map.

Default the path from artifact presence; surface the choice in the Executive Summary.

### Step 2 – Subdomain Classification
For each capability the scope covers, name the subdomain, classify it (core / supporting / generic), and attach a one-line rationale referencing business differentiation and model complexity. When the call is genuinely contested (e.g. a capability that is core today but generic in 18 months), record both sides as a hotspot in the Recommendations section rather than forcing a single verdict.

### Step 3 – Bounded Context Discovery and Sizing
Propose bounded contexts. For each context: name, purpose (one sentence), the subdomains it owns, the owning team (or "to be determined"), and the sizing rationale. Apply the heuristics from `ddd.md` §1.2:

- One team owns one or more contexts; never split a context across teams.
- Same term used two ways → two contexts (or a failure to distinguish them).
- A single aggregate becoming the "God object" of a context → context is probably too broad.
- Cognitive-load upper bound: 2–3 low-complexity domains per team (load `decomposition.md` Sizing Heuristics when sizing is contested).

For brownfield: name observed contexts (modules, services, packages) and note the gap to the target context list – what is currently merged but should split, what is currently scattered but should consolidate.

### Step 4 – Context Map
Build the context map as a table: every ordered pair of contexts that exchange data, the named pattern from the 9-pattern catalog, and a one-line rationale ("upstream is external SaaS; we cannot negotiate the model" → Conformist; "upstream model is hostile + legacy" → ACL). When the same pair has multiple integration channels with different patterns, list them as separate rows.

For brownfield, produce two maps: **Current** (what exists in code today) and **Target** (what it should look like). The delta drives the Drift Findings section.

### Step 5 – Ubiquitous-Language Touchpoints
For each context, name the 3–8 vocabulary items whose meaning is contested or load-bearing – terms that mean different things across contexts, terms that have drifted between business and engineering use, and terms with no agreed-on definition yet. The list is a hand-off note, not a glossary; the actual extraction and curation is delegated. Recommend invoking the `andthen:ubiquitous-language` skill against the context list this mode produced, and pass the touchpoint names through as the seed list.

### Step 6 – Drift Findings _(brownfield only)_
For each delta between the Current and Target context maps: name the gap, the likely root cause (vocabulary collision, Conway's-Law mismatch, premature decomposition, accidental coupling), and the smallest move that would close it. Skip the section entirely on greenfield runs.

### Step 7 – Recommendations
Synthesize: which subdomains warrant immediate investment (core), which integration patterns need to change (and toward what), which contexts are sized wrong, and which UL touchpoints are blocking communication. Each recommendation names a framework or principle (Evans, Khononov, Tune, the 9-pattern catalog) and a concrete next step – typically a hand-off to another mode or skill. Hand-off catalog:

- Bounded-context boundary contested → invoke the `andthen:architecture` skill in `--mode decompose`.
- Strategic decisions need fitness-function enforcement → invoke the `andthen:architecture` skill in `--mode fitness`.
- Per-context UL extraction → invoke the `andthen:ubiquitous-language` skill.
- Subdomain-tree, context-map, or team-topology diagram → invoke the `andthen:excalidraw-diagram` skill (the textual report is the source of truth; the diagram is for human review).
- Visual review of the textual report itself – section-anchored notes that round-trip via clipboard back into a follow-up architecture run – invoke the `andthen:visualize` skill.
- Big-picture event-storming as upstream input when the domain is unfamiliar – invoke the `andthen:architecture` skill in `--mode event-storming` first, then chain back into `--mode strategic-design`.

## Greenfield vs. Brownfield Cheat Sheet

| Aspect | Greenfield | Brownfield |
|---|---|---|
| Input source | clarification artifact / PRD / user narrative | the `andthen:map-codebase` skill's outputs + code |
| Subdomain table | Forward-only | Today + target |
| Context map | Target only | Current + Target + drift list |
| UL touchpoints | Candidate terms to confirm | Observed conflicts in code/docs |
| Hotspots | Open requirements-side questions | Conway's-Law mismatches, vocabulary collisions |
| Hand-off emphasis | UL extraction, fitness functions | UL extraction, decomposition, refactor |

## Recommended Chains

- `event-storming → strategic-design → decompose` – discovery-to-decomposition: surface pivotal events, formalize the subdomain map, then score any contested boundary.
- `strategic-design → fitness` – formalize the strategic decisions as architectural fitness functions so drift is visible in CI.
- `strategic-design,trade-off` – when an integration-pattern choice between two contexts is genuinely contested (e.g. ACL vs. Conformist for a hostile upstream), chain into `--mode trade-off` for weighted-criteria comparison.

## Report Contents

Strategic-design-mode report must include:

1. **Executive Summary** – scope, path (greenfield / brownfield), one-paragraph synthesis of the strategic shape and the one or two findings that change the conversation
2. **How to Read This Report** – legend for subdomain types (core / supporting / generic), 9-pattern catalog short-names, and any "current/target" notation used in brownfield runs
3. **Subdomains** – table of subdomain name, type, rationale, and key invariants
4. **Bounded Contexts** – per-context entry: purpose, subdomains owned, sizing rationale, owning team
5. **Context Map** – table of context pairs with the named integration pattern and rationale; brownfield runs include both Current and Target tables
6. **Ubiquitous Language Touchpoints** – per-context list of contested or load-bearing terms; closes with the hand-off pointer to the `andthen:ubiquitous-language` skill
7. **Drift Findings** – brownfield only; gaps between Current and Target with root cause and smallest closing move
8. **Recommendations** – synthesized next steps with framework attribution and explicit hand-offs to other modes / skills
