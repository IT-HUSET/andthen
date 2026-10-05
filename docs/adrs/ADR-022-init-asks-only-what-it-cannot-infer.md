# ADR-022: `init` asks only what it cannot infer

## Status
Accepted. Recorded 2026-09-25.

Amended 2026-09-25: the Proportionality ask fires only when a fact is absent. A recorded `unknown` is an answer and is never asked again; the proposal sizes it as "anchor unavailable". This narrows the Decision's "absent or `unknown`".

## Context

`init` is a new user's first contact with AndThen. Before any value, it asks about seven questions:

- project context;
- three Proportionality facts;
- the level for the role agents;
- whether review reports are ignored or committed;
- the optional documents;
- adopting the critical rules;
- the brownfield `describe` offer.

It also scaffolds six Core documents, two base directories and `.gitignore` entries. Its path loads 8,547 words, plus 1,640 when optional content applies. Among comparable skill sets, Pocock's setup asks three questions and Superpowers asks none.

What depends on the scaffolding:

- **Already handle a missing document:**
  - `Product`: its four consumers "say the anchor was unavailable and let the user set it";
  - `Decisions`: seeded from its template "when missing" (`mode-trade-off.md:76`);
  - `Testing Strategy`: an unanswered item is recorded as an assumption.
- **Say nothing about absence:** the readers of `Architecture`, `Key Dev Commands` and `Learnings`. `Key Dev Commands` matters most, because it is "the one source for every skill that runs a check" (`verification-evidence.md:7`).
- **Evals:** the `now-what-uninitialized` case covers routing only, not `init`'s behaviour.

The precedent is Still Current "Tracker setup is first-use, not an `init` gate".

**Weighted criteria:**

| Criterion | Weight |
|---|---|
| First-contact weight | 30 |
| Robust when a document is missing | 25 |
| Proportionality anchor kept | 20 |
| Migration cost | 15 |
| Words loaded on the `init` path | 10 |

## Decision

**`init` asks only what it cannot infer.** In an existing repository that means no questions. In an empty one it means one: what the project is.

**`init` writes:**

- the root instruction file or files, with the full Project Document Index, so every later first write knows its location;
- `Key Dev Commands`, pre-filled from the manifest scripts, when the project has a manifest;
- the `.agent_temp/` and review-report `.gitignore` entries. Review reports are ignored by default, and the closing summary says how to commit them instead.

**First write creates the other Core documents** (`Product`, `Architecture`, `Testing Strategy`, `Decisions`, `Learnings`). One shared rule covers this: a document the Index names but that does not exist yet reads as empty, and the first skill that writes to it creates it from its template at the Index location.

*Amended 2026-09-28: "from its template" binds every first writer except `Learnings`, which opens with its one-line header comment instead, as the Index preamble now says; S03 had shipped "at the path" to keep `project-document-templates.md` out of the loose-skill bundles. A skill that does not carry that file has a subagent invoke the `andthen:init` skill with `seed <entry>`, so no bundle gains it.*

**The first proposal skill asks for the Proportionality facts.** When the `Product` facts are absent or `unknown`, the first skill that proposes a design asks for all three as one question and writes the answers to `PRODUCT.md`. Those skills are `clarify`, `plan` and `architecture`. An unattended run keeps today's behaviour: it says the anchor was unavailable and sizes nothing against assumed scale.

**Offered in the closing summary, never gated:** the role agents, the critical rules, `describe --mode codebase` for an existing codebase, per-sub-project instruction files in a monorepo, and the optional documents (Roadmap, Ubiquitous Language). The Issue Tracker document stays first-use.

## Consequences

**Easier**

- On an existing codebase, `init` finishes with no questions.
- The Proportionality questions come when a proposal needs them, from a skill that is already talking with the user.
- The `init` path loads fewer words.
- A project carries no empty Core documents it has not used yet.

**Harder**

- Three reader sites gain a first-write clause through the shared rule: `verification-evidence.md` for `Key Dev Commands`, the Learnings appenders, and `describe` for `Architecture`.
- The proposal skills gain a small write path to `PRODUCT.md`.
- A project whose every proposal runs unattended may never set its Proportionality facts. Today the same project records `unknown`.
- Role agents and critical rules move from default-offered to summary-offered, so fewer projects may adopt them.

**Unchanged**

- The Project Document Index and its default locations.
- Tracker setup at first use.
- Rules adoption through `init`, when asked.

## Alternatives Considered

1. **A – one combined question that includes the Proportionality facts, with the Index and `Key Dev Commands` scaffolded and the rest on first write.** Rejected by a small margin (385 against 395). It asks in every repository, including existing ones where nothing else needs asking.
2. **C – one question, but all six Core stubs still scaffolded.** Rejected (385). It keeps empty documents, the reading of six templates, and most of the first-contact weight.
3. **Floor option: keep `init` as it is and only reword its questions.** Rejected (350). It is the most robust and keeps the anchor. It also keeps the roughly seven-question, six-document first contact that decides whether AndThen feels lightweight.

## Project Compliance

- **Product.** "Lightweight: make individual skills useful without adopting the whole pipeline." "Flexible: respect existing project locations." The Decision Rule favours the smallest setup that meets the verification bar. `Key Dev Commands`, the one document verification depends on, is still created up front.
- **Settled decisions.** It extends "Tracker setup is first-use" to the other Core documents, and keeps "`init` wires the rules and role agents in prose, not a script".

## References

- Research, 2026-09-25: copying templates by file operation instead of reading them saves 1,100–3,700 words on the `init` path, and splitting `project-document-templates.md` per document saves about 2,700 under this Decision, at the cost of about 11 new shared references. An Index-and-`Key Dev Commands` scaffold needs one template of about 180 words.
- Dependency check, 2026-09-25: the six readers of `docs/specs/` resolve it through the Index's `Specs & Plans` entry, and none states behaviour when it is missing; nothing depends on `docs/guidelines/`. Hence no base directories.
- Related: Still Current "Tracker setup is first-use, not an `init` gate".
