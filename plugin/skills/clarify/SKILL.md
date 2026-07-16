---
description: Discovery & Ideation for requirements at feature or product scope – systematic discovery of gaps, edge cases, scope boundaries, and alternatives the user hadn't considered. Trigger on 'clarify requirements', 'what are the requirements', 'product vision'.
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
MODE: `feature | product` – resolved in Step 1 substep 0. Default `feature`.

### Optional Flags
- `--issue <number>` → Fetch and use a GitHub issue as requirements input
- `--mode product|feature` → MODE override (resolution: Step 1 substep 0; scope: **Product vs. Feature Scope**).
- `--to-issue` → publish the validated doc as a NEW GitHub issue (Step 4b).
- `--visual` → invoke the `andthen:visualize` skill on the produced artifact (Step 4c).

_Output directory for clarified requirements (branched by MODE):_
- **Feature mode** – OUTPUT_DIR: `<project_root>/docs/specs/` _(or as configured in **Project Document Index**)_.
- **Product mode** – resolved from the **Project Document Index** `Product` row (default `<project_root>/docs/PRODUCT.md`).

Full output paths: see **REPORT > Storage path**.


## INSTRUCTIONS

- Read project rules and guidelines (`CLAUDE.md` / `AGENTS.md` and referenced files) before starting.
- Require `INPUT`. Stop if missing.
- **Check before asking** – if the answer lives in the codebase, existing docs, or the **Project Document Index**, look it up. In **feature mode**, the `Product` document (see **Project Document Index**) is the upstream framing – vision, personas, anti-goals; feature requirements should anchor to it, not contradict it. Also read the `Learnings` document (see **Project Document Index**) – prior traps inform Discovery probes. State derivable facts directly; surface ambiguous findings or codebase-vs-INPUT conflicts as recommendations to confirm. *Exception:* a prior clarification doc is a baseline to amend (see Step 1 *Amendment check*), not a lookup that closes discovery.
- Clarify requirements, do not design solutions.
- **Invoked mid-PRD.** When another skill invokes this skill inline to resolve supplied load-bearing gaps, scope Discovery to those gaps (reuse amendment-mode scoping); don't re-litigate content settled by the calling artifact.

### Requirements vs. Implementation Boundary
Clarify operates at the **requirements level** – decisions that users, stakeholders, or product owners care about. The test is **load-bearing-ness**, not topic: *would the answer change user-visible behavior, scope, or acceptance criteria?*

- **In scope – load-bearing technical questions**: offline support; sync semantics; user-visible auth model (IdP, SSO, MFA); data residency; user-facing limits (file size, rate, retention); choice of externally-visible third-party providers; platform or device targets.
- **Out of scope – implementation-only choices**: library or framework selection; caching strategy; internal API shape; token format; code organization; DB engine. These belong downstream in the `andthen:spec` skill or the `andthen:architecture` skill (`--mode trade-off`).

Litmus when the load-bearing test is unclear: *would a non-developer stakeholder care about the answer itself – not a downstream consequence of it?*

### Product vs. Feature Scope

- **Feature scope (default)** – a single capability, user-story cluster, or epic.
- **Product scope** – the overall product/product-line, sitting **above PRDs** (one product spawns many PRDs over time).
- Litmus: *"Is the user asking 'what should this product be?' or 'what should this feature do?'"* – the former is product; the latter is feature.


## GOTCHAS
- Agent answers its own questions instead of waiting for user input
- Treating a recommended answer as confirmed when the user hasn't addressed it
- **Skipping Discovery & Ideation because input "looks complete"** – see Step 2 HARD GATE.
- **Inferring feature mode when product-level intent is present** – see Step 1 mode resolution.
- **Interactive user input tool (e.g. `AskUserQuestion`) misuse.** Falling back to markdown when the tool is available (forces typing instead of chip-tap), or encoding alternatives in prose ("Option A / Option B") inside a markdown question (defeats the chip UI). One option per candidate; `Other` carries user-originated alternatives.


## WORKFLOW

### 1. Parse and Assess Input

0. **Mode resolution** –
   - If `--mode product` or `--mode feature` is passed explicitly → use that.
   - Else infer: INPUT path matches `PRODUCT*.md` (case-insensitive, basename) OR resolves to the Project Document Index `Product` row OR INPUT prose contains product-strategy markers (`vision`, `positioning`, `product strategy`, `overall product`, `product brief`, `product-level`) → `MODE=product`.
   - Else → `MODE=feature` (default).
   - **Surface the inferred mode in the response** before proceeding to Step 2, so the user can redirect ("Treating as product-level – say so if you want feature scope instead").

1. **Parse INPUT** – Resolve INPUT by type (inline / file / URL / issue) and extract requirements.
   - If `--issue <number>` flag present (or INPUT is a GitHub issue URL): fetch the body with `gh issue view <number>` and use its content as raw requirements input. Store the issue number for reference in the output header. On re-invocation against an existing `issue-{n}-*/` directory, the issue body becomes the delta and *Amendment check* below applies.
   - **Amendment check (mode-aware)**:
     - **Feature mode**: derive a feature slug from INPUT, then check if `OUTPUT_DIR/<slug>/` (or a path in INPUT) contains a prior clarification doc – recognised by an `# Requirements Clarification:` H1 or a `Decisions Log` table, any filename, never a `prd.md` or FIS file. If yes, switch to **amendment mode**: existing doc = baseline, INPUT = delta. Multiple matches: prefer most-recently-modified.
     - **Product mode**: check the resolved Product path (default `docs/PRODUCT.md`). If the file is the init-scaffolded **stub** (≤ 10 lines AND contains a `TODO` or `[fill me in]` marker), treat as **fill mode** (write fresh content). Otherwise treat as **amendment mode**: existing doc = baseline, INPUT = delta.
     - In amendment mode: Step 2 scopes to new or still-open gaps (see Step 2); Step 3 updates the baseline in place at its existing path.

2. **Assess & identify gaps** – Document stated/assumed/missing and list gaps (functional, flows, edge cases, success criteria, scope boundaries). _(amendment mode: only what the delta adds, changes, or contradicts)_

3. **Design space decomposition** – when the feature has **user-visible or product-level** decisions with multiple viable approaches, decompose load-bearing dimensions only (see `${CLAUDE_PLUGIN_ROOT}/references/design-tree.md` for the Dimension Independence + cross-consistency rubric). Include the decomposition in the requirements output. _Skip for simple features with no meaningful design alternatives._

**Gate**: Assessment complete with documented gap list and design space decomposition (if applicable)


### 2. Discovery & Ideation Interview

> **HARD GATE** (see OPERATING PRINCIPLE). Step 3 may not begin with zero user-answered questions on record – regardless of input completeness.

Ask targeted questions based on identified gaps, unresolved design dimensions, and Ideation prompts (alternatives the user hasn't considered). Iterate until no major gaps remain. **Amendment mode**: scope questions and the gate to delta-introduced or still-open gaps only – do not re-ask resolved baseline questions.

**Recommend, don't decide.** Offer a best-guess answer with a one-line rationale for each question so the user can ratify or redirect. If you have no defensible basis, ask open-ended instead of fabricating one. Wait for input either way – unaddressed recommendations are unanswered, not confirmed.

**Discovery techniques** – probe before accepting load-bearing answers; a confident-sounding answer can still be wrong. Apply the matching technique from `references/discovery-interview-techniques.md`.

**Ideation moves** – additive to Discovery, not a replacement. Propose alternative MVPs (smaller/faster/different shape); surface anti-goals; suggest pruning candidates (deferrable stated requirements); offer adjacent capability spaces in/out of scope so the user confirms boundaries explicitly.

**Question delivery.** One question per gap; first option = recommendation with rationale; remaining options = real alternatives; leave room for free-form input. Use an interactive user input tool when available (e.g. `AskUserQuestion` in Claude Code, cap 4 questions per call – iterate if more gaps remain); fall back to 3–5 numbered markdown questions otherwise.

**Question scope branches by MODE:**
- **Feature mode** – scope & boundaries (in/out of scope, MVP, deferrals); users & flows (roles, happy path, alternate paths, UI involvement); edge cases & errors (invalid input, failures, boundary conditions); success criteria (acceptance criteria, metrics, test/validation approach); dependencies & constraints (external systems, technical constraints, timeline).
- **Product mode** – vision & problem statement (what the product is, why it exists, the user/market problem); target users & personas (roles, contexts, jobs-to-be-done); value propositions (specific, testable outcomes); anti-goals (explicit non-goals and why); success metrics (north star + leading indicators); strategic constraints (business, regulatory, technical); roadmap themes (themes, not features).

**Gate**: At least one round of user-answered questions on record; all critical questions answered; no blocking ambiguities; unaddressed recommendations re-surfaced or moved to Open Questions.


### 3. Consolidate Requirements

Structure all findings into the requirements document using the template in **REPORT** below (amendment mode: preserve unchanged sections verbatim, add missing template sections only when the delta requires them).

**Gate**: Requirements document complete and structured


### 4. Validation

Validate the consolidated document against the REPORT template – every applicable section present, complete, and self-consistent (no contradictions, no vague undefined terms, criteria testable). In amendment mode, validate the *merged* document, not just the delta – contradictions between delta and untouched baseline must be caught here.

Fix any issues found before finalizing.

**Gate**: All validation checks pass


### 4b. Publish to GitHub _(only when `--to-issue`)_

After the local clarification doc is written and validated, publish per **Pattern A** in [`github-publish.md`](${CLAUDE_PLUGIN_ROOT}/references/github-publish.md). Title: `Requirements Clarification: <feature-name>`. Body temp file: `.agent_temp/clarify/<feature-slug>-issue-body.md` when `Refs #<N>` is appended; otherwise pass the local doc path directly to `--body-file`. Print the new issue URL.

The flag is additive – the issue is a durable transport record for downstream skills (`andthen:prd --issue <N>`).

**Gate**: Issue created (or skipped when `--to-issue` is absent)


### 4c. Visual Review _(only when `--visual`)_

After the document is written and Step 4 Validation passes, invoke the `andthen:visualize` skill on the produced artifact – feature mode passes `requirements-clarification.md`, product mode passes the resolved Product document. Print both the artifact path and the visualizer's output path.

**Gate**: HTML rendered and browser-open attempted, or fallback path printed


### 5. Domain Language Extraction _(if domain complexity warrants)_

When domain complexity warrants (business rules, multiple bounded contexts, domain-specific terminology), create or update the `Ubiquitous Language` document (see **Project Document Index**; default `docs/UBIQUITOUS_LANGUAGE.md`) with an initial glossary grouped by domain cluster.

> **Skip** for simple projects (CRUD apps, utilities, scripts) or when domain language is obvious.

**Gate**: Domain glossary created or skipped with rationale


## REPORT

Generate a markdown document using the template that matches `MODE`:
- **Feature mode**: use the Feature template in `references/output-templates.md`.
- **Product mode**: use the Product template in `references/output-templates.md`.

### Storage path (branched by MODE)

- **Feature mode**: `OUTPUT_DIR/<feature-name>/requirements-clarification.md`. If from GitHub issue: use `issue-{number}-{feature-name}/` as the output subdirectory name (e.g. `docs/specs/issue-42-data-export/requirements-clarification.md`). Include issue reference in the document header.
- **Product mode**: the resolved Product path (default `<project_root>/docs/PRODUCT.md`) – single file, no subdirectory wrapper.

When complete, print the report's **relative path from the project root**.


## FOLLOW-UP ACTIONS

After completion, ask user if they'd like to:

### Feature mode follow-ups
1. **Review visually** – the `andthen:visualize` skill on the output (skip when `--visual` already ran).
2. **Create feature spec** – the `andthen:spec` skill on the output directory.
3. **Create a PRD** – the `andthen:prd` skill on the output directory.
4. **Proceed to planning** – the `andthen:prd` skill, then the `andthen:plan` skill (multi-feature / MVP scope).
5. Review specific areas in more depth, or share with stakeholders for validation.

### Product mode follow-ups
1. **Strategic decomposition** – the `andthen:architecture` skill in `--mode strategic-design` to derive bounded contexts/subdomains from the vision.
2. **First PRD** – the `andthen:prd` skill on an epic/feature carved from a Roadmap Theme.
3. **Domain language** – the `andthen:ubiquitous-language` skill for a product-wide glossary.
4. **Iterate** – re-invoke `andthen:clarify` in product mode later to amend as the product evolves.

> **Session tip**: `spec`, `prd`, and `plan` can run in this session. But the heavier skills that follow them – `exec-spec`, `exec-plan` – are context-intensive and perform best in a **clean session**. `plan` also benefits from a clean session when generating the full FIS bundle.
