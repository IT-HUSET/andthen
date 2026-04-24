---
description: Use when the user wants to generate a new spec or FIS before implementation for a feature or plan story. Do not use when the user wants to execute or implement an existing spec or FIS. Creates an execution-sized FIS by default, or pivots to a small plan bundle with multiple FIS files when one spec would be too large. Trigger on 'create a spec for this', 'create a FIS for this', 'write a spec', 'write a FIS', 'specify this feature'.
argument-hint: "<description> | @<requirements-file> | story <story-id> of <path-to-plan.md> [--auto|--headless]"
---

# Generate Feature Implementation Specification


Given a feature request, generate an execution-sized specification artifact: a single Feature Implementation Specification (FIS) by default, or a small `plan.md` plus multiple child FIS files when one spec would clearly be too large.


## VARIABLES

ARGUMENTS: $ARGUMENTS (strip any `--auto` / `--headless` tokens before interpreting the remainder as the description / `@file` / `story <id> of <plan>`)

### Optional Flags
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Require `ARGUMENTS`. Stop if missing.
- **Spec generation only** — no code changes, commits, or modifications.
- Agents executing the FIS only get the context you provide. Include all necessary documentation, examples, and references.
- Read the `Learnings` document (see **Project Document Index**) before starting, if it exists.
- **Automation mode** (`--auto` / `--headless`) — never ask the user what to do next. Make the best conservative requirement/spec assumption that yields an execution-sized FIS, document it in the FIS under assumptions, propagate `--auto` to nested `andthen:*` skill invocations that accept it (the `andthen:ops` skill is exempt — it is deterministic), and return deterministic artifact paths for the orchestrator. Stop with `BLOCKED:` (listing the minimum missing decisions) only for missing input, unreadable sources, incompatible artifacts, unsafe external actions, or ambiguity where no defensible FIS can be written.


## GOTCHAS

**Generating a FIS without reading the codebase first** – architecture analysis (Step 1) must precede specification (Step 4).

**Undefined behavior** – surface ambiguity and missing requirements rather than silently inventing answers. Emit named output blocks:
- `CONFUSION:` — ambiguity + labeled options + `-> Which approach?`
- `NOTICED BUT NOT TOUCHING:` — out-of-scope observations + `-> Want me to create tasks?`
- `MISSING REQUIREMENT:` — undefined behavior + labeled options + `-> Which behavior?`

In `AUTO_MODE`, do not use arrow prompts. Choose the most conservative defensible option and record it as an assumption in the FIS; if no defensible option exists, stop with `BLOCKED:` and list the minimum missing decisions.

**Describing code changes instead of outcomes** – tasks should state what must be TRUE when done, not what code to write. Bad: "Create lib/auth.ts with login() and logout()". Good: "Auth module with login/logout; follow pattern at lib/users.ts:10-30".

**Acceptance criteria that can't be verified programmatically** – every criterion needs a concrete verify command or observable check. If you can't write the scenario's **Then** clause, you don't understand the requirement yet.

**Scenarios that describe implementation, not behavior** – scenarios should use Given/When/Then to describe observable outcomes from the user's or system's perspective, not internal code steps. Bad: "Given a new AuthService class, When login() is called...". Good: "Given valid credentials, When the user submits login, Then a session token is returned."

**Over-researching** – gather just enough context for a clear spec. Default to skipping research phases unless clearly needed (gap in requirements, unfamiliar APIs, novel features). A spec that reads like a diff is too detailed. A 30-line minimal FIS is fine; zero FIS is not. Most strong FIS files land in the 150-450 line range. If the first-pass draft is pushing past roughly ~600 lines or >18 tasks, pivot at spec time into a small plan bundle with multiple child FIS files instead of leaving the problem for `exec-spec`.

**Generic "What We're NOT Doing" section** – use it to record real non-goals or deferrals with reasons, not filler bullets.


## ORCHESTRATOR ROLE

You are the orchestrator: parse input, gather codebase analysis and research, then author the FIS from the findings. 
To protect the main context window, prefer running research tasks inside a spawned sub-agent (named or `general-purpose`). 
Always write the FIS yourself to keep it coherent.


## WORKFLOW

### 0. Parse Input & Get Requirements

**If ARGUMENTS is a directory with `requirements-clarification.md`** (from the `andthen:clarify` skill): read it; use clarified scope, functional requirements, edge cases, success criteria, design decisions, wireframes, and any explicit non-goals / deferred items as the feature request. Skip or reduce research phases (clarify already did discovery). Only do codebase research and any external/API research the requirements reference but haven't investigated.

**If ARGUMENTS use `story {story_id} of {path-to-plan.md}`**: read the plan; locate the story by ID; use its scope, acceptance criteria, dependencies, and phase context as feature request. If the story has **Key Scenarios**, use them as seeds for the Scenarios section (Step 3) — elaborate each seed into full Given/When/Then format. Store plan path and story ID for output updates. If a plan-scoped `.technical-research.md` exists in the plan directory (from the `andthen:plan` skill — check for the `## Story-Scoped File Map` section as a fingerprint), read it and reduce Steps 1 and 2 research accordingly.

**Otherwise**: use inline description or file reference as the feature request.


### 1. Priming and Project Understanding

If a **plan-scoped** `.technical-research.md` exists (created by the `andthen:plan` skill — check for the `## Story-Scoped File Map` section as a fingerprint), read it and reduce this step to a quick verification that the project structure matches the research. Otherwise, analyse the codebase to understand project structure, relevant files and similar patterns. Use `tree -d` and `git ls-files | head -250` for overview. Spawn a `general-purpose` sub-agent for deeper context when the scan is broad.


### 2. Feature Research and Design

If a plan-scoped `.technical-research.md` exists with relevant coverage, skip research categories it already addresses. Only research what's genuinely missing:

- **Codebase research** _(skip if technical research covers file maps and patterns for this story)_: locate similar features/patterns, files to reference with line numbers, existing conventions and test patterns. Use `rg`/`tree`/file reads directly.

- **Solution architecture** _(skip if technical research already frames the solution for this story)_: frame how the feature fits the existing architecture — module boundaries, integration points, component responsibilities, data flow, test seams. Worth doing for most code changes, not just novel ones. Invoke the `andthen:architecture` skill (`--mode advise`; append `--auto` when `AUTO_MODE=true`) in a spawned `general-purpose` sub-agent.

- **External research** _(if references to APIs/libraries without prior research)_: current documentation, known gotchas. Delegate to the `andthen:documentation-lookup` agent or the `andthen:research-specialist` agent.

- **Architecture trade-offs** _(often unnecessary — skip unless the story has 1-3 genuinely competing approaches with non-trivial risk or cost differences; also skip if technical research covers shared decisions or an ADR is in ARGUMENTS)_: analyse the candidate approaches, document risks, pick one with rationale. Invoke the `andthen:architecture` skill (`--mode trade-off`; append `--auto` when `AUTO_MODE=true`) in a spawned `general-purpose` sub-agent.

- **UI research** _(if applicable, and no prior wireframes)_: existing patterns, create wireframes. Invoke the `andthen:ui-ux-design` skill (`--mode research` or `--mode wireframes`; append `--auto` when `AUTO_MODE=true`) in a spawned `general-purpose` sub-agent.

**Save research findings** (if substantial) to `.technical-research.md` in the FIS output directory — a hidden companion document that keeps the FIS lean and reviewable. The FIS references this document; the executing agent reads it alongside the FIS for implementation context. See the [Technical Research Separation](references/fis-authoring-guidelines.md#technical-research-separation) guidelines for what belongs in the research doc vs the FIS. Skip this if findings are minimal — not every spec needs a technical research document.

If an existing `.technical-research.md` already exists, append story-specific findings under a `## {Story Name}` heading rather than overwriting.

Only stop for ambiguity when it blocks a defensible specification. In that case, return the minimum missing decisions required rather than pausing for routine clarification.


### 3. Write Scenarios

Before generating the full FIS, write the **Scenarios** section first. Scenarios are concrete examples of expected behavior (BDD-style Given/When/Then) that serve triple duty: requirement, test specification, and proof-of-work contract. Start with the happy path, then edge cases, then error cases. 3-7 scenarios is the sweet spot. After drafting, apply the **negative-path checklist** from the FIS authoring guidelines — verify coverage for omitted optional inputs, no-match selectors/filters, and rejection paths. See the FIS authoring guidelines for detailed guidance.

**Lock down proof-of-work**: every Success Criterion must have a proof path — at least one scenario (for behavioral criteria) or a task Verify line (for structural criteria). If a criterion has no proof path after writing scenarios, either add a scenario or flag it for a Verify line during FIS generation.


### 4. Generate FIS

#### Gather Context (as references, not inline content)
- Technical research from Step 2 (reference `.technical-research.md` — don't inline findings into the FIS)
- ADRs and the `Architecture` document (see **Project Document Index**); file paths with line numbers for patterns to follow
- UI wireframes/mockups; design system references; external documentation URLs
- `Ubiquitous Language` document (see **Project Document Index**) – use canonical terms; flag any contradictions

#### Generate from Template
Use the template in the **Appendix** below. Then read and follow the FIS authoring guidelines at
[`references/fis-authoring-guidelines.md`](references/fis-authoring-guidelines.md).

> **Optional**: Invoke the `andthen:review --mode doc` skill for thorough validation (recommended for large/complex features; append `--auto` when `AUTO_MODE=true`). This keeps pre-implementation FIS review on the document-review path.

### 4.5 Oversize Pivot

After drafting the first-pass FIS, assess whether it is still execution-sized.

- Oversize signals: the draft is pushing past roughly ~600 lines, exceeds ~18 implementation tasks, spans multiple major execution phases that would likely be executed independently, or feels like a small plan disguised as one spec.
- If the draft is still execution-sized, save the single FIS normally.
- If the draft is oversized **and the input is a standalone feature request / issue / clarification directory**:
  1. Do **not** save the giant single FIS as the primary artifact.
  2. Create a small `plan.md` in the output directory with 2-5 focused stories in execution order.
  3. Generate that `plan.md` using the `andthen:plan` skill's template at `templates/plan-template.md`. Treat the template as an operational contract, not loose guidance.
  4. Preserve the plan template invariants because downstream skills parse them directly:
     - keep the heading names and overall document shape stable
     - keep the Story Catalog columns exactly `ID | Name | Phase | Wave | Dependencies | Parallel | Risk | Status | FIS`
     - include the document references header blockquote at the top with actual relative links for `PRD`, `ADRs`, `Design System`, `Wireframes`, and `Technical Research` when those documents exist
     - for each story, include `**Status**`, `**FIS**`, `**Phase**`, `**Wave**`, `**Dependencies**`, `**Parallel**`, `**Risk**`, `**Scope**`, `**Acceptance Criteria**`, and `**Asset refs**`
     - keep `**Key Scenarios**` optional, but include them when behavioral seeds are useful for downstream FIS generation
     - include `**Provenance**` when a story has no direct PRD feature coverage
  5. Use the oversize pivot as a **simple one-story-per-FIS breakdown**.
  6. Generate exactly one child FIS per story in the same directory, reusing the shared `.technical-research.md` when present.
  7. For each child FIS:
     - use the standard FIS template in the Appendix below and the FIS authoring guidelines
     - derive the content from that story's `Scope`, `Acceptance Criteria`, and `Key Scenarios` in the generated `plan.md`
     - reference the shared `.technical-research.md` from the FIS instead of copying codebase analysis or API research into each spec
     - save with a stable story-scoped filename such as `s01-{story-name}.md`
     - keep the spec execution-sized; if a child FIS would still be oversized, split the story further in `plan.md` before saving specs
  8. Update the generated `plan.md` immediately after each child FIS is written so that every story points at its child FIS path and has `Status: Spec Ready`.
  9. Treat the result as a **fully-specced plan bundle** whose downstream path is the `andthen:exec-plan` skill, not the `andthen:exec-spec` skill. Specs for every story are already included, so `exec-plan` can consume the bundle directly without an upstream `andthen:plan` pass.
- If the draft is oversized **and the input is `story {story_id} of {path-to-plan.md}`**:
  - Do **not** silently fan one plan story out into multiple FIS files.
  - Stop and report that the story needs upstream plan decomposition before spec generation can complete. Do not save an oversized single FIS.


## OUTPUT

### Single-FIS Mode
- Directory input (e.g. clarify output): save FIS inside as `{feature-name}.md`
- Plan story input: save FIS in plan directory as `{story-name}.md`
- Otherwise: save at `docs/specs/{feature-name}.md` _(or as configured in **Project Document Index**)_
  - GitHub issue input: include issue reference in filename, e.g. `issue-123-feature-name.md`
- **Technical research**: save as `.technical-research.md` in the same directory as the FIS. If the FIS is for a plan story and `.technical-research.md` already exists (from the `andthen:plan` skill), append story-specific findings under a `## {Story Name}` heading rather than creating a separate file.
- **Update source plan** – if this spec was created for a plan story:
  - Set the story's **FIS** field to the generated FIS file path
  - Set the story's **Status** field to `Spec Ready`

### Oversize Pivot Mode
- Save `plan.md` in the output directory as the primary artifact
- Generate `plan.md` from `templates/plan-template.md` and preserve its required headings, Story Catalog columns, and story metadata labels
- Save exactly one child FIS per story in the same directory (prefer stable names like `s01-{story-name}.md`)
- Save or reuse `.technical-research.md` beside the plan bundle
- Update `plan.md` so each generated story references its child FIS path and has `Status` = `Spec Ready`
- The downstream execution path is the `andthen:exec-plan` skill
- Do **not** use oversize pivot mode for `story {story_id} of {path-to-plan.md}` input; that case must escalate for upstream plan decomposition instead

---


## FOLLOW-UP ACTIONS

Skip this section when `AUTO_MODE=true`; print only the generated artifact paths and downstream command shape.

After completion, suggest:

1. **Single-FIS mode**: Invoke the `andthen:exec-spec` skill to implement the FIS.
2. **Oversize pivot mode**: Invoke the `andthen:exec-plan` skill to execute the generated plan bundle.
3. **Review first**: Invoke the `andthen:review` skill with `--mode doc` on the primary artifact before implementation.

> **Session tip**: The `andthen:exec-spec` skill is context-intensive (it runs the full implementation + verification loop). Start a **clean session** for best results.


---


## Appendix: FIS Template

**USE THE TEMPLATE**: Read and use the template at [`templates/fis-template.md`](templates/fis-template.md) to generate the Feature Implementation Specification.
