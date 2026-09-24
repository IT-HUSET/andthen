# Architecture – Strategic-Design Mode

Discover or audit the strategic shape of a domain. Outputs a textual report and the typed map(s) it describes (`board-models.md`, kind `context-map`).

## Bounded Context Canvas

For any single context that needs deeper scrutiny, fill the Bounded Context Canvas (DDD Crew, Tune): name and purpose, strategic classification, domain roles, inbound and outbound messages, upstream and downstream dependencies with their integration patterns, and a ubiquitous-language excerpt. Use as a per-context appendix when the report's main Bounded Contexts table cannot carry enough detail.

## Steps

### Step 1 – Scope and Inputs
Confirm the scope (whole project, one product line, or a named slice) and the input source. Two paths:

- **Greenfield** – drive from a PRD, a hand-written `intent.md`, or the user's narrative description. Treat the user as the domain expert; ask focused questions when subdomain boundaries or vocabulary are ambiguous.
- **Brownfield** – drive from observed structure: the `andthen:describe` skill's `--mode codebase` output (the `Architecture` document) when present, existing module boundaries, persisted entities, and cross-module API calls, plus the registered `Context Map` document when one exists (see **Project Document Index**) – read it first; Step 6 reports drift against it.

Default the path from artifact presence; surface the choice in the Executive Summary.

### Step 2 – Subdomain Classification
For each capability the scope covers, name the subdomain, classify it as exactly one of core (maximal investment, full tactical DDD) / supporting (fit-for-purpose) / generic (off-the-shelf behind an anticorruption layer), and attach a one-line rationale referencing business differentiation and model complexity. When the call is genuinely contested (a capability core today but generic in 18 months), plot it on the Core Domain Chart (DDD Crew, Tune) and record both sides as a hotspot in the Recommendations section rather than forcing a verdict.

### Step 3 – Bounded Context Discovery and Sizing
Propose bounded contexts. For each context: name, purpose (one sentence), the subdomains it owns, the owning team (or "to be determined"), and the sizing rationale. Apply the calibration's bounded-context and sizing heuristics; when sizing is contested, its cognitive-load ceiling settles it. A team boundary cutting across a context boundary is a finding (calibration: distributed monolith).

For brownfield: name observed contexts (modules, services, packages) and note the gap to the target context list – what is currently merged but should split, what is currently scattered but should consolidate.

### Step 4 – Context Map
Build the context map as a table: every ordered pair of contexts that exchange data, the named pattern from the calibration's nine, and a one-line rationale ("upstream is external SaaS; we cannot negotiate the model" → Conformist; "upstream model is hostile + legacy" → ACL). When the same pair has multiple integration channels with different patterns, list them as separate rows.

For brownfield, produce two maps: **Current** (what exists in code today) and **Target** (what it should look like). The delta drives the Drift Findings section.

Emit each map as a `context-map` model from `board-models.md` into the report's own output directory – `context-map-current.json` and `context-map-target.json` on brownfield, `context-map-target.json` on greenfield – with `meta.status` set accordingly; only the map Step 8 registers is written under the `Models` location. Every context carries its `subdomainType` from Step 2 and every table row is a relationship with its pattern, direction, and rationale. Check each candidate against `context-map.schema.json` and `board-models.md` and write only what holds; a failing map is not written – print the violations and fix the map.

### Step 5 – Ubiquitous-Language Touchpoints
For each context, name the 3–8 vocabulary items whose meaning is contested or load-bearing – terms that mean different things across contexts, terms that have drifted between business and engineering use, and terms with no agreed-on definition yet. The list is a hand-off note for Step 7, not a glossary.

### Step 6 – Drift Findings _(brownfield only)_
For each delta across three inputs – the code-observed Current map, the registered `Context Map` document (when one exists), and the proposed Target map – name the gap, the likely root cause (vocabulary collision, Conway's-Law mismatch, premature decomposition, accidental coupling, or drift from the registered map), and the smallest move that would close it.

### Step 7 – Recommendations
Synthesize: which subdomains warrant immediate investment (core), which integration patterns need to change (and toward what), which contexts are sized wrong, and which UL touchpoints are blocking communication. Each recommendation names a framework or principle (Evans, Khononov, Tune, the 9-pattern catalog) and a concrete next step – typically a hand-off to another mode or skill. Hand-off catalog:

- Bounded-context boundary contested → re-invoke this skill in `--mode decompose`.
- Strategic decisions need fitness-function enforcement → re-invoke this skill in `--mode fitness`.
- Per-context UL extraction → invoke the `andthen:describe` skill in `--mode domain` against this mode's context list, with Step 5's touchpoint names as its seed list.
- Accepted context map → register it into the `Context Map` document (Step 8).
- Big-picture event-storming as upstream input when the domain is unfamiliar – run `--mode event-storming` first, then chain back into `--mode strategic-design`.

### Step 8 – Register the Context Map _(gated on user acceptance)_

Distil the accepted map into the `Context Map` document – the durable record later runs and other skills read first. Registration graduates the **accepted Target** map (or **Current**, when a brownfield audit confirms it is the intended shape) into the document; the report's Current/Target tables stay as authored. Gate on explicit user acceptance – the map has organizational implications the user owns. `--auto` skips this step rather than inferring the acceptance: nothing is registered, and the completion summary carries `context map not registered – needs acceptance`.

- Resolve the `Context Map` location from the **Project Document Index** (default: `docs/CONTEXT-MAP.md`).
- If the file does not exist, have it seeded from the `CONTEXT-MAP.md` template by the document-creation subagent (SKILL **Post-Completion**).
- Write the **Bounded Contexts** rows and the **Integration Patterns** rows from the accepted map.
- **Idempotent per context and per ordered pair**: when a row for the same context or the same pair already exists, update its fields in place rather than appending a duplicate. Never delete – the record is cumulative and its lineage is load-bearing.
- Write the accepted map as `context-map.json` with `meta.status` `registered` under the `Models` location (see **Project Document Index**; default `docs/models/`), beside the Markdown document and under Step 4's validation gate.

## Report Contents

Strategic-design-mode report must include:

1. **Executive Summary** – scope, path (greenfield / brownfield), one-paragraph synthesis of the strategic shape and the one or two findings that change the conversation
2. **How to Read This Report** – legend for subdomain types (core / supporting / generic), 9-pattern catalog short-names, and any "current/target" notation used in brownfield runs
3. The Step 2–7 artifacts in order – Drift Findings brownfield only – and **Context Map Registration**, where the map was registered (`Context Map` document path and the `context-map.json` path), omitted when the user declines.

The emitted map files' paths are printed with the report's.
