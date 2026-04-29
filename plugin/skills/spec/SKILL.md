---
description: Use when the user wants to generate a new spec or FIS before implementation for a feature or plan story. Do not use when the user wants to execute or implement an existing spec or FIS. Produces an execution-sized FIS; if the draft exceeds size thresholds, saves it anyway and warns — recommending the `andthen:prd → andthen:plan → andthen:exec-plan` chain for standalone inputs, or upstream plan decomposition for plan-story inputs. Trigger on 'create a spec for this', 'create a FIS for this', 'write a spec', 'write a FIS', 'specify this feature'.
argument-hint: "[--auto|--headless] <description | @<requirements-file> | story <story-id> of <path-to-plan.md>>"
---

# Generate Feature Implementation Specification


Given a feature request, generate an execution-sized specification artifact: a single Feature Implementation Specification (FIS) by default, or a small `plan.md` plus multiple child FIS files when one spec would clearly be too large.


## VARIABLES

ARGUMENTS: $ARGUMENTS (strip any flag tokens like `--auto` or `--headless` before interpreting the remainder as the description / `@file` / `story <id> of <plan>`)

### Optional Flags
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Require `ARGUMENTS`. Stop if missing.
- **Spec generation only** — no code changes, commits, or modifications.
- Agents executing the FIS only get the context you provide. Include all necessary documentation, examples, and references.
- Read the `Learnings` document (see **Project Document Index**) before starting, if it exists.
- **Automation rules** (headless-first, `--auto` / `--headless` strict mode, `--auto` propagation): see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). Spec-specific `BLOCKED:` triggers: missing input, unreadable sources, incompatible artifacts, ambiguity where no defensible FIS can be written.


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

**Over-researching** – gather just enough context for a clear spec. Default to skipping research phases unless clearly needed (gap in requirements, unfamiliar APIs, novel features). A spec that reads like a diff is too detailed. A 30-line minimal FIS is fine; zero FIS is not. Size threshold and oversize handling: see [`fis-authoring-guidelines.md`](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md) Key Generation Guidelines #6.

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

- **Solution architecture** _(skip if technical research already frames the solution for this story)_: frame how the feature fits the existing architecture — module boundaries, integration points, component responsibilities, data flow, test seams. Worth doing for most code changes, not just novel ones. Invoke the `andthen:architecture` skill (`--mode advise`) in a spawned `general-purpose` sub-agent.

- **External research** _(if references to APIs/libraries without prior research)_: current documentation, known gotchas. Delegate to the `andthen:documentation-lookup` agent or the `andthen:research-specialist` agent.

- **Architecture trade-offs** _(often unnecessary — skip unless the story has 1-3 genuinely competing approaches with non-trivial risk or cost differences; also skip if technical research covers shared decisions or an ADR is in ARGUMENTS)_: analyse the candidate approaches, document risks, pick one with rationale. Invoke the `andthen:architecture` skill (`--mode trade-off`) in a spawned `general-purpose` sub-agent.

- **UI research** _(if applicable, and no prior wireframes)_: existing patterns, create wireframes. Invoke the `andthen:ui-ux-design` skill (`--mode research` or `--mode wireframes`) in a spawned `general-purpose` sub-agent.

**Save research findings** (if substantial) to `.technical-research.md` in the FIS output directory — a hidden companion document that keeps the FIS lean and reviewable. The FIS references this document; the executing agent reads it alongside the FIS for implementation context. See the [Technical Research Separation](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md#technical-research-separation) guidelines for what belongs in the research doc vs the FIS. Skip this if findings are minimal — not every spec needs a technical research document.

If an existing `.technical-research.md` already exists, append story-specific findings under a `## {Story Name}` heading rather than overwriting.

Only stop for ambiguity when it blocks a defensible specification. In that case, return the minimum missing decisions required rather than pausing for routine clarification.


### 3. Write Scenarios

Before generating the full FIS, write the **Scenarios** section first. Scenarios are concrete examples of expected behavior (BDD-style Given/When/Then) that serve triple duty: requirement, test specification, and proof-of-work contract. Start with the happy path, then edge cases, then error cases. 3-7 scenarios is the sweet spot. After drafting, apply the **negative-path checklist** from the FIS authoring guidelines — verify coverage for omitted optional inputs, no-match selectors/filters, and rejection paths. See the [scenario authoring principles](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md#scenario-authoring-principles) in the FIS authoring guidelines for detailed guidance.

**Lock down proof-of-work**: every Success Criterion must have a proof path — at least one scenario (for behavioral criteria) or a task Verify line (for structural criteria). If a criterion has no proof path after writing scenarios, either add a scenario or flag it for a Verify line during FIS generation.


### 4. Generate FIS

#### Gather Context
- Technical research from Step 2 (reference `.technical-research.md` — don't inline findings into the FIS)
- ADRs and the `Architecture` document (see **Project Document Index**); file paths with line numbers for patterns to follow
- UI wireframes/mockups; design system references; external documentation URLs
- `Ubiquitous Language` document (see **Project Document Index**) – use canonical terms; flag any contradictions

#### Resolve Cross-Document References

Walk every upstream document the spec depends on (PRD, plan, ADRs, project guidelines like `Ubiquitous Language` / coding standards / security rules, glossary) and resolve each reference into one of two tiers per the [Cross-Document References](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md#cross-document-references) guideline (which carries the full rules, the inline budget, and the `.technical-research.md` exclusion):

- **Required Context** — load-bearing spans inlined verbatim, source-pinned with `<!-- source: -->` and `<!-- extracted: -->` comments. See the [Cross-Document References](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md#cross-document-references) guideline for the inline budget, pin format, and `.technical-research.md` exclusion.
- **Deeper Context** — supplementary anchored pointers. Validate each anchor resolves before finalizing.

The walk is mandatory; the sections themselves are optional based on what's found. Omit Required Context entirely when no load-bearing upstream spans surface; omit Deeper Context when no supplementary pointers are worth surfacing. A truly standalone feature request with no PRD/plan/ADR/guideline upstream legitimately produces neither section — but only after the walk confirms there's nothing to inline or anchor.

A bare "see plan.md" without an anchor or inlined content is not acceptable. The author saw the source; the author names what matters. Code-pattern `file:line` pointers stay inside task descriptions or the `Code Patterns & External References` section — they're not Required/Deeper Context material.

#### Generate from Template
Use the template in the **Appendix** below. Then read and follow the FIS authoring guidelines at
[`fis-authoring-guidelines.md`](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md).

> **Optional**: Invoke the `andthen:review --mode doc` skill for thorough validation (recommended for large/complex features). This keeps pre-implementation FIS review on the document-review path.


## OUTPUT

- Directory input (e.g. clarify output): save FIS inside as `{feature-name}.md`
- Plan story input: save FIS in plan directory as `s{NN}-{name}.md` (two-digit zero-padded story number; `{name}` is a kebab-case slug derived from the story name). The FIS body must carry `**Plan**:` and `**Story-ID**:` between the H1 and `## Feature Overview and Goal`, populated from the source plan path and story ID.
- Otherwise: save at `docs/specs/{feature-name}.md` _(or as configured in **Project Document Index**)_
  - GitHub issue input: include issue reference in filename, e.g. `issue-123-feature-name.md`
- **Technical research**: save as `.technical-research.md` in the same directory as the FIS. If the FIS is for a plan story and `.technical-research.md` already exists (from the `andthen:plan` skill), append story-specific findings under a `## {Story Name}` heading rather than creating a separate file.
- **Update source plan** – if this spec was created for a plan story:
  - Set the story's **FIS** field to the generated FIS file path
  - Set the story's **Status** field to `Spec Ready`

**Oversize signal** — after saving, measure the FIS against the threshold from [`fis-authoring-guidelines.md`](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md) Key Generation Guidelines #6 (>700 lines or >18 tasks). If oversized, emit a structured line as part of the artifact output (printed in both interactive and `AUTO_MODE`):

```
OVERSIZE: {fis_path} — {N} lines, {T} tasks. Recommendation: {recommendation}
```

- **Standalone input** recommendation: `switch to /andthen:prd <input> to start the prd → plan → exec-plan chain`
- **Plan-story input** recommendation: `story too broad — revisit {plan_path} and decompose before regenerating`

Plan-batch sub-agents must echo the `OVERSIZE:` line back in their completion summary so the `andthen:plan` orchestrator can revisit Step 3 for the over-broad story.

---


## FOLLOW-UP ACTIONS

Skip this section when `AUTO_MODE=true`; print only the generated artifact paths, the `OVERSIZE:` line if applicable, and downstream command shape.

After the FIS is saved, suggest:

1. **Implement the FIS**: Invoke the `andthen:exec-spec` skill.
2. **Review first**: Invoke the `andthen:review` skill with `--mode doc` on the FIS before implementation.

> **Session tip**: The `andthen:exec-spec` skill is context-intensive (it runs the full implementation + verification loop). Start a **clean session** for best results.

If the `OVERSIZE:` signal fired, expand the recommendation conversationally: standalone inputs should switch to the `andthen:prd → andthen:plan → andthen:exec-plan` chain; plan-story inputs need upstream plan decomposition before regenerating.


---


## Appendix: FIS Template

**USE THE TEMPLATE**: Read and use the template at [`fis-template.md`](${CLAUDE_PLUGIN_ROOT}/references/fis-template.md) to generate the Feature Implementation Specification.
