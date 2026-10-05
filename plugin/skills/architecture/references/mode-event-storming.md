# Architecture – Event Storming Mode

Run a Brandolini event-storming session as a discovery technique. The mode produces a textual report and the typed board it describes (`board-models.md`, kind `event-storm`).

## Rules

Event storming treats the user as the domain expert. Step 1 (scope + level) and Step 2 (event harvest) are the gates. Ask focused questions when vocabulary or causality is unclear. An unattended run bypasses the gates and records each assumption as a hotspot whose label is its `ASSUMPTION:` line.

Brandolini's color palette – keep colors stable across the report so readers can visually parse the board.

| Color | Element |
|---|---|
| **orange** | Domain event (past tense) |
| **blue** | Command |
| **yellow** | Actor |
| **lilac** | Policy |
| **green** | Read model |
| **pale yellow** | Aggregate _(Design Level)_ |
| **pink** | External system |
| **purple** | Hotspot |

External systems earn a sticky when the integration is itself a step on the timeline (Brandolini's Big Picture convention). At Process Modeling and Design Level an actor or policy usually carries the integration, so a pink sticky there is rare, never wrong.

## Workflow

### Step 1 – Scope and Level
Confirm the topic and Brandolini's level – Big Picture, Process Modeling, or Design Level. Two paths:

- **Greenfield** – drive the session from a PRD, a hand-written `intent.md`, or the user's narrative description of the workflow. Keep the timeline shallow and surface hotspots aggressively, because the goal is to find the questions.
- **Brownfield** – drive the session from observed behaviour: existing endpoints, message contracts, persisted entities, and the `andthen:describe` skill's `--mode codebase` outputs when available. Pivotal events often surface as cross-context API calls or transactional boundaries that look arbitrary in code but are load-bearing in the domain.

A board already under `Models` for the scope holds the user's earlier answers, so the session resumes it and changes it rather than replacing it.

### Step 2 – Harvest Events
Walk the domain chronologically, listing orange events in past tense, one per line. An unexplained gap in the timeline is a question to the user. An unanswered one is a purple hotspot, never a guess.

### Step 3 – Reverse the Narrative _(Process Modeling and Design Level only)_
For each event, name the command that caused it (blue) and the actor that issued the command (yellow). When a command has no clear actor, that is a hotspot – flag it.

### Step 4 – Policies and Read Models _(Process Modeling and Design Level only)_
For each pivotal event, name the policy that reacts to it (lilac) and the read model the deciding actor consults (green).

### Step 5 – Hotspots and Pivotal Events
Promote contested transitions, vocabulary conflicts ("two actors mean different things by `Order`"), and unanswered causality questions to purple hotspots. Identify pivotal events – the events that mark a change in pace, ownership, or invariants, such as `OrderShipped` or `LoanApproved`. They are the candidate boundaries between subdomains and aggregates.

### Step 6 – Candidates
Produce the level-appropriate output:
- **Big Picture** → subdomain candidates anchored on pivotal-event clusters, each with a one-line rationale.
- **Process Modeling** → workflow boundaries with the commands/events/policies they own.
- **Design Level** → aggregate candidates with the invariants that would force their state into one transaction.

### Step 7 – Emit the Board
Project the session into the `event-storm` model from `board-models.md`, with `meta.level`, `scope`, and `source` matching the report:

- every sticky with its `kind`, verbatim `label`, and timeline `order`;
- lanes where the timeline splits by process or actor;
- flows for the command → aggregate → event → policy chains at Process Modeling and Design Level;
- the Step 6 candidates with their `members`, aggregates carrying their invariants;
- unanswered questions as hotspots `attachedTo` the sticky they question.

Check the candidate against `event-storm.schema.json` and `board-models.md`, and write it only when it holds, to the resumed board's file, else `event-storms/<slug>.json` under the `Models` location (see **Project Document Index**; default `docs/models/`), `<slug>` the kebab of the report's scope. A failing board is not written: print the violations and fix the board, never the level.

Rewriting the file after each round lets a watching viewer show the board live.

## Output

Event-storming-mode report must include:

1. **Executive Summary** – level run, scope, and the one or two findings that change the conversation
2. **How to Read This Report** – sticky-note color legend, level explanation, pivotal-event marker convention
3. **Event Timeline** – chronological, pivotal events marked; at Big Picture, each event with the actors involved
4. **Commands and Actors** _(Process Modeling and Design Level only)_ – unattributed commands flagged
5. **Policies and Read Models** _(Process Modeling and Design Level only)_
6. **Hotspots** – unresolved questions, conflicts, and risks
7. **Subdomain Candidates** _(Big Picture)_, **Workflow Boundaries** _(Process Modeling)_, **or** **Aggregate Candidates** _(Design Level)_ – one section per output, anchored on pivotal events with rationale and invariants
8. **Recommended Next Steps** – a one-line trigger condition each: Big Picture subdomain candidates → this skill in `--mode strategic-design`; Design-Level aggregate candidates → `--mode decompose`; vocabulary conflicts surfaced as hotspots → the `andthen:describe` skill in `--mode domain`

The board file's path is printed with the report's.
