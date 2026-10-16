# ADR-029: Model the domain in a `domain` skill, recorded in one Domain Map

## Status
Accepted. Recorded 2026-10-16.

Makes ADR-025's "`architecture` becomes read-only advice and analysis" true: the two modes that wrote design records leave it. Amends ADR-027: `context-map.json` retires, reversing its Alternative 4 for that type, so three JSON types remain (`architecture-model`, `event-storm`, `plan`). Rewrites the Still Current note on the architecture-model schema, whose "typed JSON" clause for non-code graphs the rule below replaces, and the rationale in `docs/ARCHITECTURE.md` for keeping the `Context Map` name.

## Context

**Modelling a domain has three routes in two skills.** `describe --mode domain` writes the glossary, and `architecture` runs `strategic-design` and `event-storming`, so `now-what` routes "model the domain" three ways (`now-what/SKILL.md:63`). `architecture` also holds two kinds of mode: four write an analysis report to `Agent Temp`, and those two run a workshop with the user as domain expert and write committed records.

**The business side of the domain has no durable record.** Strategic design classifies subdomains as core, supporting, or generic, but the classification survives only in a transient report and as one `subdomainType` per bounded context in `context-map.json`. One value cannot record a context that owns two subdomains, though Step 3 asks for "the subdomains it owns". The `CONTEXT-MAP.md` template has no classification at all. DartClaw's hand-maintained map added a Subdomains section and a "Subdomains owned" column for exactly this.

**A business-facing domain map shows what is missing.** A colleague's page for another project, made 2026-10-16, shows each subdomain as a card: its type, what it owns, its key terms, relationships to the others in domain language ("a visit happens at a facility"), and a worked example with named instances, a scenario across subdomains, and the rules the scenario shows. A domain expert confirms or corrects a model faster from that than from a table of integration patterns.

**`context-map.json` mirrors a document.** No skill reads it. `visualize` and a downstream viewer do, and every skill reads the `Context Map` document. ADR-027's amendment retired `glossary-model.json` on the same ground this morning. The JSON does hold four fields the document lacks: `subdomainType`, `team`, a symmetric `direction`, and `rationale`.

The user's goal, with 1.0 unreleased and breaking changes acceptable: every architecture and DDD skill, mode, document, and model fits one picture a user can read at a glance, with few documents and one purpose each, and one rule for Markdown versus JSON.

## Decision

### 1. A `domain` skill models the domain and owns its records

It is the 21st skill. Each mode writes one record:

| Mode | Writes | From |
|---|---|---|
| `subdomains` | The Domain Map's business half: each subdomain classified core, supporting, or generic with its rationale, and what it owns. Optional Relationships and Worked Example sections, and Open Questions for a contested classification. The user confirms the classification at a gate, because whether a capability sets the business apart is the user's knowledge. | `strategic-design` Step 2 |
| `contexts` | The Domain Map's software half: bounded contexts with the subdomains each owns, integration patterns, brownfield drift, distillation. It reads the classified subdomains, and runs `subdomains` first when there are none, needing only the classification. A reclassification it finds is proposed at its gate and written once accepted, else recorded under Open Questions. | the rest of `strategic-design` |
| `glossary` | The Ubiquitous Language. Terms group by bounded context once the Domain Map has contexts, and by subdomain before that, because a language holds within the context where its model holds. | `describe --mode domain` |
| `event-storming` | The boards, at three levels, unchanged. A Big Picture session's subdomain candidates seed `subdomains`. | `architecture` |

- `--mode` takes a chain, as `architecture`'s does. The "context map" trigger routes to `contexts`.
- Under `--auto`, `subdomains` writes nothing and prints its proposal, and `contexts` skips registration as today.
- The findings filter runs over findings and recommendations, never over what the user confirmed at a gate.
- `describe` keeps codebase mapping only, and its `--mode` flag goes. A caller that passes `--mode codebase` gets its best reading.
- `architecture` keeps `advise`, `review`, `decompose`, and `fitness`, and writes no design record. A choice to settle goes to `decide`, unchanged from ADR-025. `advise` drops its "which pattern" trigger, which `now-what` already routes to `decide`.

### 2. One Domain Map document replaces the Context Map

`docs/DOMAIN-MAP.md`, Index entry `Domain Map`, answers one question: what are the parts of the business, how much does each matter, and which software boundary owns each?

- **Sections and writers.** `subdomains` owns Subdomains, Relationships, Worked Example, and Open Questions. `contexts` owns Bounded Contexts, with Subdomains owned and Team columns, and Integration Patterns, where a symmetric pattern (Partnership, Shared Kernel, Separate Ways) is written as symmetric rather than as upstream and downstream. Neither mode rewrites the other's sections. Context and pattern rows stay idempotent and are never deleted.
- **No terms.** The glossary holds every term once. A viewer shows a subdomain's terms from its glossary cluster or from the cluster of the context that owns it, so a rename touches one file.
- **Written to a template, read leniently.** People curate the map by hand, and DartClaw's carries sections no template has. Skills write to the template; skills, `visualize`, and downstream viewers read whatever sections are present. A `domain-map.md` fixture joins the corpus.
- **Recommended first, never required.** When the domain is not described elsewhere, `now-what` routes to it, `contexts` and `event-storming` read it, and a Cookbook recipe puts it first. A library or a CRUD tool skips it, as the Product document's Proportionality facts would say.
- An existing `Context Map` Index entry is read as the Domain Map until the project migrates.

### 3. One rule for Markdown and JSON

**Each fact has one record. A record people curate is Markdown. A JSON model exists only for facts a skill generates and nobody hand-edits, which no document holds: measured code structure, an event-storming session's board, or a plan's runtime state. JSON never mirrors a document.**

- `context-map.json` and the report-side `context-map-current.json` and `context-map-target.json` retire, with `context-map.schema.json`. The report's tables are the run's record, and `visualize` draws a report like any artifact.
- `board-models.md` covers the event storm only, and calls the committed board the session's record and the report its write-up.

### 4. The document set, one question each

| Record | Question | Written by |
|---|---|---|
| Product | Why build this, and for whom? | `clarify`, `init` |
| Domain Map | What are the parts of the business, how much does each matter, and which software boundary owns each? | `domain` `subdomains`, `contexts` |
| Ubiquitous Language | What do we call things? | `domain` `glossary` |
| Architecture | What is built? | `describe` |
| Models | What does the code measurably look like, and what did a storming session find? | `describe --model`, `domain` `event-storming` |
| Decisions and ADRs | Why is it this way? | `decide` |

## Consequences

**Easier**
- One skill answers "model the domain", and each of its modes writes one record.
- The subdomain classification survives the run, and a context that owns two subdomains is recorded as such.
- A business reader gets the domain's parts, their weight, and a worked example in one document, and a viewer draws it from one file.
- Every JSON file passes one stated rule.

**Harder**
- One more always-loaded description: descriptions total 5,505 characters (measured 2026-10-16), and `domain` adds about 350, under Codex's shared 8,000-character fallback.
- The prompt surface grows. `domain` copies the Boundary and Domain Calibration section and traps 17, 19, and 20 of `architecture-calibration.md` (about 500 words), because `advise` and `decompose` still need them and dedup never creates a reference file (Still Current), plus the gate, dispatch, seeding, and Proportionality rules. The surface measured 68,566 of 70,000 words on 2026-10-16; the estimated growth is 1,200–1,800 words (inferred). The implementing change raises `tests/surface-budget.json` to its measured need (ADR-018).
- Breaking for release-candidate users:
  - `architecture --mode strategic-design` becomes `domain --mode contexts`, `architecture --mode event-storming` becomes `domain --mode event-storming`, and `describe --mode domain` becomes `domain --mode glossary`.
  - `CONTEXT-MAP.md` becomes `DOMAIN-MAP.md`.
  - `context-map.json` retires. Run `domain --mode contexts` while the old file exists, so its subdomain types, teams, and rationales reach the Domain Map, then delete it.
  - A downstream viewer re-pins: it reads the Domain Map Markdown, and event-storm `meta.generatedBy` becomes `andthen:domain`, a free string in the schema.
- No eval case covers the moved modes, so verification rests on `skill-review` and the unit tests.

**Reversal**: two-way door until 1.0 ships – a revert of the implementing change. After that the skill and mode names are public, and moving them needs a migration.

## Alternatives Considered
1. **Floor option – extend what exists.** `strategic-design` writes the classified subdomains into the `Context Map` document, `context-map.json` retires, and nothing moves (DartClaw's practice). Rejected: it gives the durable record at a fraction of the cost, but it keeps three routes for "model the domain" and keeps reports and design records in one skill, which is the problem the user set out to remove.
2. **Keep the DDD modes in `architecture` and move the glossary there.** No new skill. Rejected: eight modes doing two jobs, analysis reports and committed records.
3. **A domain-map stage inside `strategic-design`.** Rejected: one mode writing two records, with a stop-halfway knob.
4. **Keep `CONTEXT-MAP.md` beside a new domain map.** Separates the business and engineering readers. Rejected: one more document, and DartClaw's map shows subdomains, contexts with the subdomains they own, and integration patterns living in one file.
5. **A `domain-map.json`, alone or beside the document.** Rejected: the map is curated by hand, AndThen models are never hand-edited, and a document-plus-JSON pair is what `glossary-model.json` retired for.
6. **Bounded contexts as a section of the Architecture document.** Rejected: that document is the as-built system, regenerated from code; the accepted map is design intent.
7. **Mode names `map` or `domains`, and `bounded-contexts`.** Rejected: `map` collides with "context map" and with `describe`'s "map this codebase"; `domains` adds a second word for subdomain; `bounded-contexts` is precise but slow to type, and after `domain` the word `contexts` has one meaning.
8. **The glossary always grouped by subdomain.** Rejected: it files a term under a business area instead of the context where its meaning holds.
9. **The Domain Map lists each subdomain's key terms.** Readable in the raw file. Rejected: every glossary rename must also edit the map, and a missed edit breaks the join silently.
10. **A strict template a viewer parses deterministically.** Rejected: it contradicts the Robust principle and a hand-curated record, and a pinned shape costs every edit, as the retired parsers did.

## Implementation Notes

One plan, in this order, swept with `rg -i` on the bare names, not only on sigils (LEARNINGS):

1. **The record.** The Domain Map template and Index entry in `project-document-templates.md`, replacing the Context Map's, with the clause reading an old `Context Map` entry as the Domain Map. A `domain-map.md` fixture in `scripts/fixtures/renders/`; the `context-map` row and fixture go, and the `strategic-design` and `event-storming` rows take owner `andthen:domain`.
2. **The skill.** `plugin/skills/domain/`: `SKILL.md`, the four mode references, the copied calibration, `agents/openai.yaml`, and `_skill_assets_domain` in `scripts/install-skills.py`.
3. **The sources.** `architecture` loses `strategic-design`, `event-storming`, their board loads, and the "which pattern" trigger. `describe` loses domain mode and its `--mode` flag. `board-models.md` shrinks to the event storm, and `context-map.schema.json` goes.
4. **Readers and routers.** `now-what`; `clarify` (`SKILL.md`, `references/product-mode.md`); `decide`; `plan/references/breakdown.md`; `describe/references/mode-codebase.md` and `architecture-model.md` (context identity); `mode-advise.md`'s hand-off; `visualize` (`SKILL.md`, `json-artifacts.md`); both `openai.yaml` default prompts; `evals/cases/init/rubric.json`.
5. **Docs.** `README.md` (count and the "other twelve" line), `plugin/README.md`, `COOKBOOK.md` (glossary pointer, event storming recipe, a domain-map-first recipe), `MIGRATING-FROM-0.x.md`, `CHANGELOG.md` Unreleased with the migration step above, `docs/UBIQUITOUS_LANGUAGE.md` (Domain Map and subdomain rows), `docs/ARCHITECTURE.md` (its model and naming lines), `AGENTS.md`, `scripts/skills-overview.py` and the regenerated figure.
6. **Budget.** Raise `tests/surface-budget.json` to the measured need.
7. **Review.** `skill-review` over the prompt-like files, `andthen:review` over scripts and tests.

## Project Compliance
- **Decision Rule** (`docs/PRODUCT.md`): the new skill names its outcome, one route and one record per question, and the floor option is weighed above.
- **Robust**: readers take the Domain Map leniently, and an old `Context Map` entry keeps working.
- **Flexible**: the Domain Map is recommended, never required, and every mode runs alone.
- **ADR-018**: the budget raise is stated here and made in the implementing change.
- **ADR-025**: `architecture` writes no design record, and `decide` still settles choices.

## References
- ADR-018 (one plugin, one surface budget), ADR-025 (`decide`; `architecture` as advice and analysis), ADR-027 and its 2026-10-16 amendment (glossary model retired).
- `docs/DECISIONS.md` Still Current: the architecture-model schema note, AndThen owning artifact contracts, dedup never creating a reference file.
- DartClaw `dev/architecture/context-map.md`: subdomains, contexts with the subdomains they own, and integration patterns in one hand-maintained file.
- Evans, *Domain-Driven Design* (2003): a ubiquitous language holds within its bounded context.
