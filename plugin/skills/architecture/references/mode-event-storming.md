# Architecture — Event Storming Mode

Run a Brandolini-style event-storming session as a discovery technique — surface domain events end-to-end, expose hotspots and pivotal events, and harvest candidates downstream modes can formalize. The mode produces a textual board (with optional diagram hand-off), not a synchronous workshop; treat the user (or a clarification artifact) as the domain expert and ask focused questions when vocabulary or causality is unclear.

**Supporting references**: `ddd.md` (section 4.1 — sticky-note vocabulary cross-reference; section 4.3 — context-map artifact when a Big Picture session ends with subdomain candidates).

## Sticky-Note Vocabulary

Brandolini's color palette — keep colors stable across the report so readers can visually parse the board.

| Color | Element | Form |
|---|---|---|
| **orange** | Domain event | Past-tense fact (`OrderPlaced`, `PaymentDeclined`) |
| **blue** | Command | Imperative intent triggering an event (`PlaceOrder`) |
| **yellow** | Actor | Person or system issuing a command (`Customer`, `Fulfillment Service`) |
| **lilac** | Policy | Reactive rule — "whenever X, do Y" |
| **green** | Read model | Information an actor reads to decide a command |
| **purple** | Hotspot | Unresolved question, conflict, or risk |

Pink/red is canonical for external systems on Big Picture boards (Brandolini); use when external integrations are load-bearing for the timeline. Skip on Process Modeling and Design Level — those levels surface external systems via actors and policies instead.

## Brandolini's Three Levels

Pick the level that matches the user's framing — do not force all three. Big Picture is the default when no scope is given.

### Big Picture
Map the domain end-to-end. Surface orange events in chronological order; cluster around pivotal events (events that change the conversation — `OrderShipped`, `LoanApproved`); flag language conflicts and unresolved causality as purple hotspots. Output: an event timeline plus subdomain candidates derived from pivotal-event clusters.

### Process Modeling
Zoom into one workflow. Reconstruct command → aggregate → event → policy chains; attach yellow actors to commands and green read models to decisions. Output: per-process command/actor/event/policy maps with purple hotspots flagged on contested transitions.

### Design Level
Detail aggregates and transactional boundaries inside a single process. Output: aggregate candidates with their invariants and per-aggregate command/event lists — feeds directly into the `andthen:architecture` skill in `--mode decompose`.

## Steps

### Step 1 — Scope and Level
Confirm the topic (e.g. "order fulfillment", "loan origination") and the level — Big Picture, Process Modeling, or Design Level. If the user supplied no level, default to Big Picture and surface the choice in the Executive Summary.

### Step 2 — Harvest Events
Walk the domain chronologically. List orange events in past tense, one per line. Ask the user for missing events when the timeline has unexplained gaps; record unanswered questions as purple hotspots rather than guessing.

### Step 3 — Reverse the Narrative
For each event, name the command that caused it (blue) and the actor that issued the command (yellow). When a command has no clear actor, that is a hotspot — flag it.

### Step 4 — Policies and Read Models _(Process Modeling and Design Level only)_
For each pivotal event, name the policy that reacts to it (lilac) and the read model the deciding actor consults (green). Skip when the level is Big Picture.

### Step 5 — Hotspots and Pivotal Events
Promote contested transitions, vocabulary conflicts ("two actors mean different things by `Order`"), and unanswered causality questions to purple hotspots. Identify pivotal events — the events that mark a change in pace, ownership, or invariants — they are the candidate boundaries between subdomains and aggregates.

### Step 6 — Candidates
Produce the level-appropriate output:
- **Big Picture** → subdomain candidates anchored on pivotal-event clusters, each with a one-line rationale.
- **Process Modeling** → workflow boundaries with the commands/events/policies they own.
- **Design Level** → aggregate candidates with the invariants that would force their state into one transaction.

### Step 7 — Hand-off
Recommend the next mode explicitly:
- Big Picture subdomain candidates → invoke the `andthen:architecture` skill in `--mode strategic-design` to formalize subdomain classification, bounded-context sizing, and a context map.
- Design-Level aggregate candidates → invoke the `andthen:architecture` skill in `--mode decompose` to score the boundary with Ford/Richards drivers.
- Vocabulary conflicts surfaced as hotspots → invoke the `andthen:ubiquitous-language` skill to lift terms into a per-context glossary.
- Visual board (timeline, command/actor map) → invoke the `andthen:excalidraw-diagram` skill; the textual board is the source of truth, the diagram is for human review.

## Greenfield vs. Brownfield

Brownfield event-storming converges on the same outputs as greenfield (event timeline, hotspots, level-appropriate candidates) — the codebase serves as a memory aid for surfacing real events, not as a separate path with its own report shape. The two bullets below differ only in input source.

- **Greenfield** — drive the session from a clarification artifact (`requirements-clarification.md`) or the user's narrative description of the workflow. Keep the timeline shallow and surface hotspots aggressively; the goal is to find the questions, not to ship an exhaustive board.
- **Brownfield** — drive the session from observed behaviour: existing endpoints, message contracts, persisted entities, and the `andthen:map-codebase` skill's outputs when available. Pivotal events often surface as cross-context API calls or transactional boundaries that look arbitrary in code but are load-bearing in the domain.

## Recommended Chain

`event-storming → strategic-design → decompose` is the canonical discovery-to-decomposition sequence: discover pivotal events, formalize the subdomain map, then evaluate any contested boundary with driver scoring. Run it as a single multi-mode invocation when the user wants the full sweep; run modes individually when only one level of formalization is needed.

## Report Contents

Event-storming-mode report must include:

1. **Executive Summary** — level run (Big Picture / Process Modeling / Design Level), scope, and the one or two findings that change the conversation
2. **How to Read This Report** — sticky-note color legend (orange / blue / yellow / lilac / green / purple), level explanation, pivotal-event marker convention
3. **Event Timeline** — orange events in chronological order; pivotal events marked
4. **Commands and Actors** — blue commands paired with yellow actors; unattributed commands flagged
5. **Policies and Read Models** — lilac policies and green read models (Process Modeling and Design Level only; omit for Big Picture)
6. **Hotspots** — purple unresolved questions, conflicts, and risks
7. **Subdomain Candidates** _(Big Picture)_, **Workflow Boundaries** _(Process Modeling)_, **or** **Aggregate Candidates** _(Design Level)_ — one section per output, anchored on pivotal events with rationale and invariants
8. **Recommended Next Steps** — explicit hand-off with a one-line trigger condition for each: architecture modes (`strategic-design`, `decompose`) and delegation skills (the `andthen:ubiquitous-language` skill for vocabulary conflicts, the `andthen:excalidraw-diagram` skill for board diagrams)
