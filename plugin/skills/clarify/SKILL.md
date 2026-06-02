---
description: Discovery & Ideation for requirements at feature or product scope – clarify requirements, product vision, and overall product requirements through systematic discovery of gaps, edge cases, scope boundaries, and alternatives the user hadn't considered. Trigger on 'clarify this', 'clarify requirements', 'what are the requirements', 'discover requirements', 'product vision', 'clarify the product', 'product-level requirements'.
argument-hint: "[requirements source: description or file path | --issue <number>] [--mode product|feature] [--to-issue] [--visual]"
---

# Clarify Requirements


Refine fuzzy inputs into clarified requirements through **Discovery** (probing latent requirements) and **Ideation** (alternatives the user hadn't considered). Two scopes: **feature** (default) and **product** (vision, target users, value props, anti-goals – when INPUT carries product-level intent or `--mode product` is set).


## OPERATING PRINCIPLE

**Interactive-by-Contract.** This skill's deliverable IS the back-and-forth Discovery & Ideation – user input is the work, not an obstacle to it. Producing a clarification doc without at least one round of user-answered questions is a contract violation, not a shortcut. The "input looks complete" intuition is the agent rationalizing past the contract; run the interview anyway.


## VARIABLES

_Requirements to clarify (**required**):_
INPUT: $ARGUMENTS (strip any flag tokens like `--issue`, `--mode`, `--to-issue`, or `--visual` before interpreting the remainder as the requirements source – description or file path)

_Scope mode:_
MODE: `feature | product` – resolved in Step 1 substep 0. Default `feature`. Explicit `--mode` flag wins over inference.

### Optional Flags
- `--issue <number>` → Fetch and use a GitHub issue as requirements input
- `--mode product|feature` → MODE override; explicit value wins over inference. `product` runs the skill at overall-product scope (vision, personas, value props, anti-goals, metrics) and writes to the Project Document Index `Product` location.
- `--to-issue` → After Step 4 Validation, save the clarification doc locally (as today), then create a NEW GitHub issue with the doc body via `gh issue create --title "Requirements Clarification: <name>" --body-file <path>`. When an input issue was supplied (via `--issue <N>` or a GitHub issue URL), append `Refs #<N>` as the last line of the issue body. The flag never comments on or edits the input issue. Print the new issue URL.
- `--visual` → After the clarification or product vision document is written and validated, invoke the `andthen:visualize` skill on the produced artifact.

_Output directory for clarified requirements (branched by MODE):_
- **Feature mode** – OUTPUT_DIR: `<project_root>/docs/specs/` _(or as configured in **Project Document Index**)_. Output path: `OUTPUT_DIR/<feature-name>/requirements-clarification.md`.
- **Product mode** – resolved from the **Project Document Index** `Product` row (default `<project_root>/docs/PRODUCT.md`). Single file, no `<feature-name>/` wrapper.


## INSTRUCTIONS

- Read project rules and guidelines (`CLAUDE.md` / `AGENTS.md` and referenced files) before starting.
- Require `INPUT`. Stop if missing.
- **Interactive-by-Contract** (see **OPERATING PRINCIPLE**) – ask iteratively, wait for input. Recommending ≠ confirmed (Step 2).
- **Ideation alongside Discovery** – propose alternative MVPs, surface anti-goals, suggest pruning candidates, and offer adjacent capability spaces in or out of scope. Discovery probes what the user stated; Ideation surfaces what they didn't.
- **Visual review is a post-validation handoff.** When `--visual` is present, complete the normal clarification/product-vision gate first, then invoke the `andthen:visualize` skill on the produced artifact; the visualizer owns HTML rendering, note export, browser-open behavior, and `.agent_temp/visual-review/` output.
- **Check before asking** – if the answer lives in the codebase, existing docs, or the **Project Document Index**, look it up. In **feature mode**, the `Product` document (see **Project Document Index**) is the upstream framing – vision, personas, anti-goals; feature requirements should anchor to it, not contradict it. Also read the `Learnings` document (see **Project Document Index**) – prior traps inform Discovery probes. State derivable facts directly; surface ambiguous findings or codebase-vs-INPUT conflicts as recommendations to confirm. *Exception:* a prior clarification doc is a baseline to amend (see Step 1 *Amendment check*), not a lookup that closes discovery.
- Challenge assumptions, find edge cases, identify ambiguities.
- Clarify requirements, do not design solutions.

### Requirements vs. Implementation Boundary
Clarify operates at the **requirements level** – decisions that users, stakeholders, or product owners care about. The test is **load-bearing-ness**, not topic: *would the answer change user-visible behavior, scope, or acceptance criteria?*

- **In scope – load-bearing technical questions**: offline support; sync semantics; user-visible auth model (IdP, SSO, MFA); data residency; user-facing limits (file size, rate, retention); choice of externally-visible third-party providers; platform or device targets.
- **Out of scope – implementation-only choices**: library or framework selection; caching strategy; internal API shape; token format; code organization; DB engine. These belong downstream in the `andthen:spec` skill or the `andthen:architecture` skill (`--mode trade-off`).

Litmus when the load-bearing test is unclear: *would a non-developer stakeholder care about the answer itself – not a downstream consequence of it?*

### Product vs. Feature Scope

- **Feature scope (default)** – a single capability, user story cluster, or epic with bounded user-visible behavior. Output: feature-level `requirements-clarification.md`.
- **Product scope** – the overall product or product-line: vision, target users, problem space, value props, anti-goals, success metrics, strategic constraints. Sits **above PRDs** (a product spawns multiple PRDs over time). Output: the Project Document Index `Product` document (default `docs/PRODUCT.md`).
- Litmus: *"Is the user asking 'what should this product be?' or 'what should this feature do?'"* – the former is product; the latter is feature.


## GOTCHAS
- Agent answers its own questions instead of waiting for user input
- Treating a recommended answer as confirmed when the user hasn't addressed it
- **Skipping Discovery & Ideation because the input "looks complete"** – see Step 2 HARD GATE.
- **Inferring feature mode when product-level intent is present** – see Step 1 mode resolution; surface the inference in the first response so the user can redirect.
- **Interactive user input tool (e.g. `AskUserQuestion`) misuse.** Falling back to markdown when the tool is available (forces typing instead of chip-tap), or encoding alternatives in prose ("Option A / Option B") inside a markdown question (defeats the chip UI). One option per candidate; `Other` carries user-originated alternatives.


## WORKFLOW

### 1. Parse and Assess Input

0. **Mode resolution** –
   - If `--mode product` or `--mode feature` is passed explicitly → use that.
   - Else infer: INPUT path matches `PRODUCT*.md` (case-insensitive, basename) OR resolves to the Project Document Index `Product` row OR INPUT prose contains product-strategy markers (`vision`, `positioning`, `product strategy`, `overall product`, `product brief`, `product-level`) → `MODE=product`.
   - Else → `MODE=feature` (default).
   - **Surface the inferred mode in the response** before proceeding to Step 2, so the user can redirect ("Treating as product-level – say so if you want feature scope instead").

1. **Parse INPUT** - Determine type: inline description, file path, `--issue`, or URL
   - If `--issue <number>` flag present (or INPUT is a GitHub issue URL): fetch the body with `gh issue view <number>` and use its content as raw requirements input. Store the issue number for reference in the output header. On re-invocation against an existing `issue-{n}-*/` directory, the issue body becomes the delta and *Amendment check* below applies.
   - If file path: Read and extract requirements
   - If URL: Fetch and extract requirements
   - If description: Use directly
   - **Amendment check (mode-aware)**:
     - **Feature mode**: derive a feature slug from INPUT, then check if `OUTPUT_DIR/<slug>/` (or a path in INPUT) contains a prior clarification doc – recognised by an `# Requirements Clarification:` H1 or a `Decisions Log` table, any filename, never a `prd.md` or FIS file. If yes, switch to **amendment mode**: existing doc = baseline, INPUT = delta. Multiple matches: prefer most-recently-modified.
     - **Product mode**: check the resolved Product path (default `docs/PRODUCT.md`). If the file is the init-scaffolded **stub** (≤ 10 lines AND contains a `TODO` or `[fill me in]` marker), treat as **fill mode** (write fresh content). Otherwise treat as **amendment mode**: existing doc = baseline, INPUT = delta.
     - In amendment mode: re-run Step 2 *Discovery & Ideation Interview* only for new or still-open gaps; Step 3 updates the baseline in place at its existing path. A prior doc is a baseline to extend, not an authority that closes discovery.

2. **Initial assessment** - Document what's explicitly stated, what's assumed, what's missing (amendment mode: only what the delta adds, changes, or contradicts)

3. **Gap identification** - List gaps in: functional requirements, user flows, edge cases, success criteria, scope boundaries

4. **Design space decomposition** – when the feature has **user-visible or product-level** decisions with multiple viable approaches, decompose load-bearing dimensions only (see `${CLAUDE_PLUGIN_ROOT}/references/design-tree.md` for the Dimension Independence + cross-consistency rubric). Implementation-only dimensions are downstream concerns for the `andthen:spec` skill or the `andthen:architecture` skill (`--mode trade-off`). Include the decomposition in the requirements output. _Skip for simple features with no meaningful design alternatives._

**Gate**: Assessment complete with documented gap list and design space decomposition (if applicable)


### 2. Discovery & Ideation Interview

> **HARD GATE (Interactive-by-Contract, see OPERATING PRINCIPLE).** Step 3 may not begin with zero user-answered questions on record – regardless of input completeness.

Ask targeted questions based on identified gaps, unresolved design dimensions, and Ideation prompts (alternatives the user hasn't considered). Iterate until no major gaps remain. **Amendment mode**: scope questions and the gate to delta-introduced or still-open gaps only – do not re-ask resolved baseline questions.

**Recommend, don't decide.** Offer a best-guess answer with a one-line rationale for each question so the user can ratify or redirect. If you have no defensible basis, ask open-ended instead of fabricating one. Wait for input either way – unaddressed recommendations are unanswered, not confirmed.

**Discovery techniques** – probe before accepting load-bearing answers. A confident-sounding answer can still be wrong. Apply the matching technique from `references/discovery-interview-techniques.md`: Five Whys (stated solution, not problem), Scenario Testing (abstract requirement), Extremes and Boundaries (fuzzy scope), Trade-off Forcing ("everything is important"), Laddering (too specific or too vague), Perspective Shift (happy-path fixation).

**Ideation moves** – additive to Discovery, not replacement. Propose alternative MVPs (smaller, faster, different shape); surface anti-goals ("things this is explicitly NOT"); suggest pruning candidates (stated requirements that may be deferrable); offer adjacent capability spaces in/out of scope so the user can confirm boundaries explicitly.

**Question delivery.** One question per gap; first option = recommendation with rationale; remaining options = real alternatives (not throwaways); leave room for free-form input. Use an interactive user input tool when available (e.g. `AskUserQuestion` in Claude Code, cap 4 questions per call – iterate if more gaps remain); fall back to 3–5 numbered markdown questions otherwise.

**Question scope branches by MODE:**
- **Feature mode** – scope & boundaries (in/out of scope, MVP, deferrals); users & flows (roles, happy path, alternate paths, UI involvement); edge cases & errors (invalid input, failures, boundary conditions); success criteria (acceptance criteria, metrics, test/validation approach); dependencies & constraints (external systems, technical constraints, timeline).
- **Product mode** – vision & problem statement (what the product is, why it exists, the user/market problem); target users & personas (roles, contexts, jobs-to-be-done); value propositions (specific, testable outcomes); anti-goals (explicit non-goals and why); success metrics (north star + leading indicators); strategic constraints (business, regulatory, technical); roadmap themes (themes, not features).

**Gate**: At least one round of user-answered questions on record; all critical questions answered; no blocking ambiguities; unaddressed recommendations re-surfaced or moved to Open Questions.


### 3. Consolidate Requirements

Structure all findings into the requirements document using the template in **REPORT** below (amendment mode: preserve unchanged sections verbatim, add missing template sections only when the delta requires them).

**Gate**: Requirements document complete and structured


### 4. Validation

Review consolidated requirements: all user flows have clear steps; design space decomposition constructed with decisions resolved or flagged; wireframes included if applicable; edge cases identified; scope boundaries explicit; **Not Doing** items specific and justified; success criteria specific and testable; no contradictions; dependencies documented; no vague undefined terms. In amendment mode, validate the *merged* document, not just the delta – contradictions between delta and untouched baseline must be caught here.

Fix any issues found before finalizing.

**Gate**: All validation checks pass


### 4b. Publish to GitHub _(only when `--to-issue`)_

After the local clarification doc is written and validated, publish per **Pattern A** in [`github-publish.md`](${CLAUDE_PLUGIN_ROOT}/references/github-publish.md). Title: `Requirements Clarification: <feature-name>`. Body temp file: `.agent_temp/clarify/<feature-slug>-issue-body.md` when `Refs #<N>` is appended; otherwise pass the local doc path directly to `--body-file`.

The flag is additive – the local doc is the source of truth; the issue is a durable transport record for downstream skills (`andthen:prd --issue <N>`).

**Gate**: Issue created (or skipped when `--to-issue` is absent)


### 4c. Visual Review _(only when `--visual`)_

After the local document is written and Step 4 Validation passes, invoke the `andthen:visualize` skill on the produced artifact. Feature mode passes `requirements-clarification.md`; product mode passes the resolved Product document. Print both the artifact path and the visualizer's output path.

**Gate**: HTML rendered and browser-open attempted, or fallback path printed


### 5. Domain Language Extraction _(if domain complexity warrants)_

If the project involves significant domain complexity (business rules, multiple bounded contexts, domain-specific terminology):
1. Extract candidate terms from requirements: entities, actions, states, rules, relationships
2. Identify synonym clusters and ambiguous terms
3. Create or update the `Ubiquitous Language` document (see **Project Document Index**) with an initial glossary grouped by domain cluster

> **Skip** for simple projects (CRUD apps, utilities, scripts) or when domain language is obvious.

**Gate**: Domain glossary created or skipped with rationale


## REPORT

Generate a markdown document using the template that matches `MODE`.

### Feature mode template

```markdown
# Requirements Clarification: [Name]

## Summary
[2-3 sentences: what this is, who it's for, core value]

## Scope

### In Scope
- [Explicit inclusions]

### Out of Scope
- [Explicit exclusions]

### MVP Boundary
- [Minimum viable version definition]

### Not Doing (for now)
- [Explicit non-goal or deferred item] – [why it is out of scope now]

## Functional Requirements

### User Stories
- As a [user], I want [goal], so that [benefit]

### Core Flows
1. [Primary flow with steps]

### Alternate Flows
- [Alternate paths and variations]

### UI Wireframes
<!-- Include only if requirements involve UI work -->

## Design Decisions
<!-- Include only if design space decomposition was constructed -->
### Design Space Decomposition
[Feature] ├── [Dimension 1]: [Option A] ← chosen · [Option B] · [Option C] ✗ (pruned)

### Cross-Consistency Notes
- [Option] + [Option] – incompatible/conditional: [reason]

### Resolved Decisions
| Dimension | Choice | Rationale |

### Open Design Questions
- [Dimensions needing further analysis via the `andthen:architecture` skill (`--mode trade-off`)]

## Edge Cases
| Scenario | Expected Behavior |

## Error Handling
| Error | User Message | Recovery |

## Non-Functional Requirements
- **Performance**: [Expectations]
- **Security**: [Requirements]
- **Accessibility**: [Standards]

## Success Criteria
- [ ] [Testable criterion]

## Dependencies
| Dependency | Purpose | Risk |

## Open Questions
- [Remaining ambiguities for later phases]

## Decisions Log
| Decision | Rationale | Date |
```

### Product mode template

```markdown
# Product Vision: [Product Name]

## Vision
[One paragraph: what this product is, why it exists, the change it makes for users]

## Problem Statement
[The user/market problem being solved; current pain; alternatives users use today]

## Target Users & Personas
- **[Persona]** – [role, context, jobs-to-be-done]

## Value Propositions
- [Promised user/business outcome – specific, testable]

## Product Principles
- [Design-decision tiebreakers – e.g. "favor depth over breadth"]

## Anti-Goals
- [Explicit non-goals – what this product is NOT, and why]

## Success Metrics
### North Star
- [Single metric tied to value delivered]
### Leading Indicators
- [Earlier signals that predict the north star]

## Strategic Constraints
- **Business**: [budget, timeline, partnerships]
- **Regulatory**: [compliance, data residency]
- **Technical**: [non-negotiable platform / integration constraints]

## Roadmap Themes
<!-- Themes, not features. Features are decided downstream in andthen:prd. -->
- **[Theme]** – [what this theme unlocks, when it matters]

## Open Questions
- [Strategic ambiguities deferred to future product clarification rounds]

## Decisions Log
| Decision | Rationale | Date |
```

### Storage path (branched by MODE)

- **Feature mode**: `OUTPUT_DIR/<feature-name>/requirements-clarification.md`. If from GitHub issue: use `issue-{number}-{feature-name}/` as the output subdirectory name (e.g. `docs/specs/issue-42-data-export/requirements-clarification.md`). Include issue reference in the document header.
- **Product mode**: the resolved Product path (default `<project_root>/docs/PRODUCT.md`) – single file, no subdirectory wrapper. Amendment mode preserves untouched sections verbatim per the existing baseline rule.

If domain language extraction was performed, also store it in the `Ubiquitous Language` document location from the **Project Document Index** (default: `docs/UBIQUITOUS_LANGUAGE.md`).

When complete, print the report's **relative path from the project root**.


## FOLLOW-UP ACTIONS

After completion, ask user if they'd like to:

### Feature mode follow-ups
1. **Review visually** – run `andthen:visualize <requirements-clarification.md>` when a browser review would help spot scope and edge-case issues a markdown view obscures (skip when `--visual` already ran).
2. **Create feature spec** – invoke the `andthen:spec` skill on the output directory to generate a FIS from the clarified requirements.
3. **Create a PRD** – invoke the `andthen:prd` skill on the output directory before planning a multi-feature effort.
4. **Proceed to planning** – invoke the `andthen:prd` skill, then the `andthen:plan` skill on the output directory for multi-feature / MVP scope.
5. Review specific areas in more depth.
6. Share with stakeholders for validation.

### Product mode follow-ups
1. **Review visually** – run `andthen:visualize <PRODUCT.md>` when a browser review would help spot vision and anti-goal issues a markdown view obscures (skip when `--visual` already ran).
2. **Strategic decomposition** – invoke the `andthen:architecture` skill in `--mode strategic-design` to derive bounded contexts and subdomains from the product vision.
3. **First PRD** – invoke the `andthen:prd` skill on a specific epic/feature carved from a Roadmap Theme.
4. **Domain language** – invoke the `andthen:ubiquitous-language` skill to extract a product-wide glossary.
5. Iterate: re-invoke `andthen:clarify` in product mode later to amend as the product evolves.

> **Session tip**: `spec`, `prd`, and `plan` can run in this session. But the heavier skills that follow them – `exec-spec`, `exec-plan` – are context-intensive and perform best in a **clean session**. `plan` also benefits from a clean session when generating the full FIS bundle.
