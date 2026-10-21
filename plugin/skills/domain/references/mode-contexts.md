# Domain – Contexts Mode

Discover or audit the software half of the domain: bounded contexts, the subdomains each owns, and the integration patterns between them. Outputs a textual report with the current and target maps as tables, and registers the accepted map in the `Domain Map`. It writes no JSON.

## Workflow

### Step 1 – Baseline
Read the classification from the `Domain Map`'s Subdomains section. Under `--auto` the earlier `subdomains` proposal stands in for it, in the report only.

Report any divergence between the context ids and names in `architecture-model.json` under `Models` and the accepted map.

### Step 2 – Bounded Context Discovery and Sizing
Propose bounded contexts. For each context: name, purpose (one sentence), the subdomains it owns, the owning team (or "to be determined"), and the sizing rationale. Apply the calibration's bounded-context and sizing heuristics; when sizing is contested, its cognitive-load ceiling settles it.

Fill the Bounded Context Canvas (DDD Crew, Tune) as a per-context appendix for a context the report's Bounded Contexts table cannot carry.

For brownfield: name observed contexts (modules, services, packages) and note the gap to the target context list – what is currently merged but should split, what is currently scattered but should consolidate.

When the context analysis contradicts a classification, propose the reclassification alongside the context list. Step 7 writes it, and under `--auto` it stays in the report.

**Gate**: the context list and any proposed reclassification, confirmed or corrected by the user before Step 3 builds on them, because the classification and the boundaries are the user's knowledge, which the code does not carry.

### Step 3 – Integration Patterns
Build the map as a table: every ordered pair of contexts that exchange data, the named pattern from the calibration's nine, and a one-line rationale ("upstream is external SaaS; we cannot negotiate the model" → Conformist; "upstream model is hostile + legacy" → ACL). When the same pair has multiple integration channels with different patterns, list them as separate rows, each naming its channel. A symmetric pattern (Partnership, Shared Kernel, Separate Ways) is one row naming its peers.

For brownfield, produce two tables: **Current** (what exists in code today) and **Target** (what it should look like). The delta drives the Drift Findings section.

### Step 4 – Ubiquitous-Language Touchpoints
For each context, name the 3–8 vocabulary items whose meaning is contested or load-bearing – terms that mean different things across contexts, terms that have drifted between business and engineering use, and terms with no agreed-on definition yet. The list is a hand-off note for Step 6.

### Step 5 – Drift Findings _(brownfield only)_
For each delta across three inputs – the code-observed Current table, the registered `Domain Map` document (when one exists), and the proposed Target table – name the gap, the likely root cause (vocabulary collision, Conway's-Law mismatch, premature decomposition, accidental coupling, or drift from the registered map), and the smallest move that would close it.

### Step 6 – Recommendations
Synthesize: which subdomains warrant immediate investment (core), which generic mechanisms to extract from a core context (Evans' distillation), which integration patterns need to change (and toward what), which contexts are sized wrong, and which UL touchpoints are blocking communication. Each recommendation names a framework or principle (Evans, Khononov, Tune, the 9-pattern catalog) and a concrete next step – typically a hand-off to another mode or skill. Hand-off catalog:

- Bounded-context boundary contested, or a generic mechanism to extract from a core context → the `andthen:architecture` skill in `--mode decompose`.
- Strategic decisions need fitness-function enforcement → the `andthen:architecture` skill in `--mode fitness`.
- Per-context UL extraction → this skill in `--mode glossary`, with Step 4's touchpoint names as its seed list.
- The domain is unfamiliar → this skill in `--mode event-storming` first, then back into `--mode contexts`.

### Step 7 – Register in the Domain Map _(gated on user acceptance)_

Distil the accepted map into the `Domain Map` document – the durable record later runs and other skills read first. Registration graduates the **accepted Target** map (or **Current**, when a brownfield audit confirms it is the intended shape) into the document.

Gate on explicit user acceptance, because the map has organizational implications the user owns. An unattended run skips this step, and its completion summary carries `domain map not registered – needs acceptance`.

- Write the **Bounded Contexts** rows (each with its Subdomains owned and Team) and the **Integration Patterns** rows from the accepted map. A Bounded Contexts table without the Subdomains owned or Team column gains it.
- Edit no section `subdomains` owns, except to write an accepted reclassification into Subdomains and a declined one under Open Questions. Leave every other section of a hand-curated map byte-identical.
- **Idempotent per context and per pair plus channel.** When a row for the same context, or the same pair over the same channel, already exists, update its fields in place and add no duplicate. A pair's new channel is a new row, never an overwrite of the existing one. Name the existing row's channel at that point if it was blank. Never delete, because the record is cumulative and its lineage is load-bearing.

## Output

Contexts-mode report must include:

1. **Executive Summary** – scope, path (greenfield / brownfield), one-paragraph synthesis of the strategic shape and the one or two findings that change the conversation
2. **How to Read This Report** – legend for subdomain types (core / supporting / generic), 9-pattern catalog short-names, and any "current/target" notation used in brownfield runs
3. The Step 2–6 artifacts in order – Drift Findings brownfield only – and **Domain Map Registration**, where the map was registered (the `Domain Map` document path), omitted when the user declines.
