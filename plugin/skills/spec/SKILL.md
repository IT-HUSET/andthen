---
description: Use when the user wants to generate a new spec or FIS before implementation for a feature or plan story. Do not use when the user wants to execute or implement an existing spec or FIS. Creates an execution-sized FIS by default, or pivots to a small plan bundle with multiple FIS files when one spec would be too large. Trigger on 'create a spec for this', 'create a FIS for this', 'write a spec', 'write a FIS', 'specify this feature'.
argument-hint: <description> | @<requirements-file> | story <story-id> of <path-to-plan.md> | --issue <number> [--to-issue]
---

# Generate Feature Implementation Specification


Given a feature request, generate an execution-sized specification artifact: a single Feature Implementation Specification (FIS) by default, or a small `plan.md` plus multiple child FIS files when one spec would clearly be too large.


## VARIABLES

ARGUMENTS: $ARGUMENTS

### Optional Output Flags
- `--to-issue` → PUBLISH_ISSUE: Publish the generated spec artifact (single FIS or plan bundle) as a GitHub issue after saving locally


## USAGE

```
/spec <feature description>        # Create FIS from inline description
/spec --issue 123                  # Create FIS from GitHub issue
/spec @docs/requirements.md        # Create FIS from requirements file
/spec docs/specs/my-feature/       # Create FIS from clarify output directory
/spec story S03 of docs/specs/dashboard/plan.md  # Create FIS for a plan story
```


## INSTRUCTIONS

- **Make sure `ARGUMENTS` is provided** – otherwise **STOP** immediately with a missing-input error that states the feature requirements or source artifact are required.
- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work
- **Spec generation only** - No code changes, commits, or modifications during execution of this command
- **Remember**: Agents executing the FIS only get the context you provide. Include all necessary documentation, examples, and references.
- **Read project learnings** – If the `Learnings` document (see **Project Document Index**) exists, read it before starting to avoid known traps and error patterns


## GOTCHAS

**Generating a FIS without reading the codebase first** – architecture analysis (Step 1) must precede specification (Step 4).

**Undefined behavior** – use structured output protocols (`${CLAUDE_PLUGIN_ROOT}/references/structured-output-protocols.md`) to surface ambiguity and missing requirements rather than silently inventing answers.

**Describing code changes instead of outcomes** – tasks should state what must be TRUE when done, not what code to write. Bad: "Create lib/auth.ts with login() and logout()". Good: "Auth module with login/logout; follow pattern at lib/users.ts:10-30".

**Acceptance criteria that can't be verified programmatically** – every criterion needs a concrete verify command or observable check. If you can't write the scenario's **Then** clause, you don't understand the requirement yet.

**Scenarios that describe implementation, not behavior** – scenarios should use Given/When/Then to describe observable outcomes from the user's or system's perspective, not internal code steps. Bad: "Given a new AuthService class, When login() is called...". Good: "Given valid credentials, When the user submits login, Then a session token is returned."

**Over-researching** – gather just enough context for a clear spec. Default to skipping research phases unless clearly needed (gap in requirements, unfamiliar APIs, novel features). A spec that reads like a diff is too detailed. A 30-line minimal FIS is fine; zero FIS is not. Most strong FIS files land in the 100-300 line range. If the first-pass draft is pushing past roughly ~400 lines or >12 tasks, pivot at spec time into a small plan bundle with multiple child FIS files instead of leaving the problem for `exec-spec`.

**Generic "What We're NOT Doing" section** – use it to record real non-goals or deferrals with reasons, not filler bullets.


## ORCHESTRATOR ROLE _(if supported by your coding agent)_

You are the orchestrator: parse input, delegate codebase analysis and research to sub-agents, then author the FIS from their findings. Delegate codebase analysis to the `andthen:solution-architect` agent; research to the `andthen:documentation-lookup` or `andthen:research-specialist` agent. Write the FIS yourself to keep it coherent.


## WORKFLOW

### 0. Parse Input & Get Requirements

**If `--issue` flag present**: use `gh issue view <number>` to fetch issue details, then inspect the body for a typed envelope per `${CLAUDE_PLUGIN_ROOT}/references/github-artifact-roundtrip.md`.
- If `artifact_type: fis-bundle`, **STOP** — the spec already exists. Exit with the correct downstream path: `andthen:exec-spec`, `andthen:review`, or the local FIS path. Do not regenerate it.
- If `artifact_type: plan-bundle`, **STOP** — the issue contains a plan, not a single-feature request. Exit with the correct downstream path: `story {story_id} of <path-to-plan.md>`, `andthen:spec-plan`, or `andthen:exec-plan`.
- If the issue contains another typed workflow artifact (`triage-plan`, `triage-completion`, or any `*-review` report), **STOP** and exit with the matching downstream skill.
- Otherwise use the issue as the feature request and store the issue number for FIS reference.

**If ARGUMENTS is a directory with `requirements-clarification.md`** (from `andthen:clarify`): read it; use clarified scope, functional requirements, edge cases, success criteria, design decisions, wireframes, and any explicit non-goals / deferred items as the feature request. Skip or reduce research phases (clarify already did discovery). Only do codebase research and any external/API research the requirements reference but haven't investigated.

**If ARGUMENTS use `story {story_id} of {path-to-plan.md}`**: read the plan; locate the story by ID; use its scope, acceptance criteria, dependencies, and phase context as feature request. If the story has **Key Scenarios**, use them as seeds for the Scenarios section (Step 3) — elaborate each seed into full Given/When/Then format. Store plan path and story ID for output updates.

**Otherwise**: use inline description or file reference as the feature request.


### 1. Priming and Project Understanding

Analyse the codebase to understand project structure, relevant files and similar patterns. Use `tree -d` and `git ls-files | head -250` for overview. Use the `Explore` agent _(if supported)_ for deeper context.


### 2. Feature Research and Design

Fully understand the feature request. Identify any ambiguities. Research only what's needed:

- **Codebase research**: similar features/patterns, files to reference with line numbers, existing conventions and test patterns. Delegate to the `andthen:solution-architect` agent _(if supported)_.
- **External research** _(if references to APIs/libraries without prior research)_: current documentation, known gotchas. Delegate to the `andthen:research-specialist` or `andthen:documentation-lookup` agent _(if supported)_.
- **Architecture trade-offs** _(if no ADR in ARGUMENTS)_: analyze 1-3 approaches, document risks. Delegate to the `andthen:solution-architect` agent _(if supported)_.
- **UI research** _(if applicable, and no prior wireframes)_: existing patterns, create wireframes. Delegate to the `andthen:ui-ux-designer` agent _(if supported)_.

**Save research findings** (if substantial) to `.technical-research.md` in the FIS output directory — a hidden companion document that keeps the FIS lean and reviewable. The FIS references this document; the executing agent reads it alongside the FIS for implementation context. See the [Technical Research Separation](../../references/fis-authoring-guidelines.md#technical-research-separation) guidelines for what belongs in the research doc vs the FIS. Skip this if findings are minimal — not every spec needs a technical research document.

If an existing `.technical-research.md` already exists (e.g. from `andthen:spec-plan` or `andthen:plan`), append story-specific findings under a `## {Story Name}` heading rather than overwriting.

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
**IMPORTANT**: Use the `Plan` agent _(if supported by your coding agent)_ to generate the FIS — it provides structured authoring support.

Use the template in the **Appendix** below. Then read and follow the FIS authoring guidelines at
[`${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md`](../../references/fis-authoring-guidelines.md).

> **Optional**: Invoke the `andthen:review --doc-only` skill for thorough validation (recommended for large/complex features). This keeps pre-implementation FIS review on the document-review path.

### 4.5 Oversize Pivot

After drafting the first-pass FIS, assess whether it is still execution-sized.

- Oversize signals: the draft is pushing past roughly ~400 lines, exceeds ~12 implementation tasks, spans multiple major execution phases that would likely be executed independently, or feels like a small plan disguised as one spec.
- If the draft is still execution-sized, save the single FIS normally.
- If the draft is oversized **and the input is a standalone feature request / issue / clarification directory**:
  1. Do **not** save the giant single FIS as the primary artifact.
  2. Create a small `plan.md` in the output directory with 2-5 focused stories in execution order.
  3. Generate that `plan.md` using the `andthen:plan` template at `${CLAUDE_PLUGIN_ROOT}/skills/plan/templates/plan-template.md`. Treat the template as an operational contract, not loose guidance.
  4. Preserve the plan template invariants because downstream skills parse them directly:
     - keep the heading names and overall document shape stable
     - keep the Story Catalog columns exactly `ID | Name | Phase | Wave | Dependencies | Parallel | Risk | Status | FIS`
     - include the document references header blockquote at the top with actual relative links for `PRD`, `ADRs`, `Design System`, `Wireframes`, and `Technical Research` when those documents exist
     - for each story, include `**Status**`, `**FIS**`, `**Phase**`, `**Wave**`, `**Dependencies**`, `**Parallel**`, `**Risk**`, `**Scope**`, `**Acceptance Criteria**`, and `**Asset refs**`
     - keep `**Key Scenarios**` optional, but include them when behavioral seeds are useful for downstream FIS generation
     - include `**Provenance**` when a story has no direct PRD feature coverage
  5. Use the oversize pivot as a **simple one-story-per-FIS breakdown**. Do **not** run THIN/COMPOSITE/shared-FIS classification here and do **not** emit `thin-specs.md`.
  6. Generate exactly one child FIS per story in the same directory, reusing the shared `.technical-research.md` when present.
  7. For each child FIS:
     - use the standard FIS template in the Appendix below and the FIS authoring guidelines
     - derive the content from that story's `Scope`, `Acceptance Criteria`, and `Key Scenarios` in the generated `plan.md`
     - reference the shared `.technical-research.md` from the FIS instead of copying codebase analysis or API research into each spec
     - save with a stable story-scoped filename such as `s01-{story-name}.md`
     - keep the spec execution-sized; if a child FIS would still be oversized, split the story further in `plan.md` before saving specs
  8. Update the generated `plan.md` immediately after each child FIS is written so that every story points at its child FIS path and has `Status: Spec Ready`.
  9. Treat the result as a **plan bundle** whose downstream path is `andthen:exec-plan`, not `andthen:exec-spec`.
- If the draft is oversized **and the input is `story {story_id} of {path-to-plan.md}`**:
  - Do **not** silently fan one plan story out into multiple FIS files.
  - **STOP** and report that the story itself needs upstream plan decomposition before spec generation can complete cleanly. Exit without generating a partial or oversized FIS.
  - Do not save an oversized single FIS just to satisfy the command.


## OUTPUT

### Single-FIS Mode
- Directory input (e.g. clarify output): save FIS inside as `{feature-name}.md`
- Plan story input: save FIS in plan directory as `{story-name}.md`
- Otherwise: save at `docs/specs/{feature-name}.md` _(or as configured in **Project Document Index**)_
  - GitHub issue input: include issue reference in filename, e.g. `issue-123-feature-name.md`
- **Technical research**: save as `.technical-research.md` in the same directory as the FIS. If the FIS is for a plan story and a plan-level `.technical-research.md` already exists, append story-specific findings under a `## {Story Name}` heading rather than creating a separate file.
- **Update source plan** – if this spec was created for a plan story:
  - Set the story's **FIS** field to the generated FIS file path
  - Set the story's **Status** field to `Spec Ready`

### Oversize Pivot Mode
- Save `plan.md` in the output directory as the primary artifact
- Generate `plan.md` from `${CLAUDE_PLUGIN_ROOT}/skills/plan/templates/plan-template.md` and preserve its required headings, Story Catalog columns, and story metadata labels
- Save exactly one child FIS per story in the same directory (prefer stable names like `s01-{story-name}.md`)
- Do **not** use THIN/COMPOSITE/shared-FIS grouping in oversize pivot mode; this mode is a straightforward one-story-per-FIS decomposition
- Save or reuse `.technical-research.md` beside the plan bundle
- Update `plan.md` so each generated story references its child FIS path and has `Status` = `Spec Ready`
- The downstream execution path is `andthen:exec-plan`
- Do **not** use oversize pivot mode for `story {story_id} of {path-to-plan.md}` input; that case must escalate for upstream plan decomposition instead

### Publish to GitHub _(if --to-issue)_
Follow `${CLAUDE_PLUGIN_ROOT}/references/github-artifact-roundtrip.md`:
- **Single-FIS mode**:
  - `artifact_type`: `fis-bundle`
  - Title: `[FIS] {feature-name}`
  - Primary file: generated FIS (`fis_path`)
  - Companion files: include `.technical-research.md` when it exists; if this spec came from a plan story, also include the current `plan.md`
  - Metadata: always set `fis_path`; if this spec came from a plan story, also set `plan_path` and `story_ids` (all constituent story IDs for composite/shared FIS)
  - Labels: `spec`, `fis`, `andthen-artifact`
- **Oversize pivot mode**:
  - `artifact_type`: `plan-bundle`
  - Title: `[PLAN] {feature-name}`
  - Primary file: generated `plan.md` (`plan_path`)
  - Companion files: include sibling `prd.md` when present, `.technical-research.md` when present, and every child FIS referenced by the plan
  - Metadata: set `plan_path`; leave `story_ids` empty at the bundle level unless a downstream consumer requires them
  - Labels: `plan`, `spec`, `andthen-artifact`

Print the issue URL and the local primary path (the generated FIS or `plan.md`, depending on mode).


---


## FOLLOW-UP ACTIONS

After completion, suggest:

1. **Single-FIS mode**: Run `andthen:exec-spec` to implement the FIS
   Example: `/andthen:exec-spec <path-to-fis>` (or `$andthen:exec-spec ...`)
2. **Oversize pivot mode**: Run `andthen:exec-plan` to execute the generated plan bundle
   Example: `/andthen:exec-plan <path-to-plan-directory>` (or `$andthen:exec-plan ...`)
3. **Review first**: Run `andthen:review --doc-only` on the primary artifact before implementation
   Example: `/andthen:review --doc-only <path-to-fis-or-plan>` (or `$andthen:review --doc-only ...`)

> **Session tip**: `exec-spec` is context-intensive (it runs the full implementation + verification loop). Start a **clean session** for best results.


---


## Appendix: FIS Template

**USE THE TEMPLATE**: Read and use the template at [`templates/fis-template.md`](templates/fis-template.md) to generate the Feature Implementation Specification.
