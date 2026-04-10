---
description: Create a Feature Implementation Specification from requirements or a plan story. Trigger on 'write spec', 'create FIS', 'specify this feature'.
argument-hint: <description> | @<requirements-file> | story <story-id> of <path-to-plan.md> | --issue <number> [--to-issue]
---

# Generate Feature Implementation Specification


Given a feature request, generate a Feature Implementation Specification (FIS) using the template in the **Appendix** below.


## VARIABLES

ARGUMENTS: $ARGUMENTS

### Optional Output Flags
- `--to-issue` → PUBLISH_ISSUE: Publish FIS as a GitHub issue after saving locally


## USAGE

```
/spec <feature description>        # Create FIS from inline description
/spec --issue 123                  # Create FIS from GitHub issue
/spec @docs/requirements.md        # Create FIS from requirements file
/spec docs/specs/my-feature/       # Create FIS from clarify output directory
/spec story S03 of docs/specs/dashboard/plan.md  # Create FIS for a plan story
```


## INSTRUCTIONS

- **Make sure `ARGUMENTS` is provided** – otherwise **STOP** immediately and ask the user to provide the feature requirements.
- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work
- **Spec generation only** - No code changes, commits, or modifications during execution of this command
- **Remember**: Agents executing the FIS only get the context you provide. Include all necessary documentation, examples, and references.
- **Read project learnings** – If `LEARNINGS.md` exists (check Project Document Index for location), read it before starting to avoid known traps and error patterns


## GOTCHAS

**Generating a FIS without reading the codebase first** – architecture analysis (Step 1) must precede specification (Step 4).

**Undefined behavior** – use structured output protocols (`${CLAUDE_PLUGIN_ROOT}/references/structured-output-protocols.md`) to surface ambiguity and missing requirements rather than silently inventing answers.

**Describing code changes instead of outcomes** – tasks should state what must be TRUE when done, not what code to write. Bad: "Create lib/auth.ts with login() and logout()". Good: "Auth module with login/logout; follow pattern at lib/users.ts:10-30".

**Acceptance criteria that can't be verified programmatically** – every criterion needs a concrete verify command or observable check. If you can't write the scenario's **Then** clause, you don't understand the requirement yet.

**Scenarios that describe implementation, not behavior** – scenarios should use Given/When/Then to describe observable outcomes from the user's or system's perspective, not internal code steps. Bad: "Given a new AuthService class, When login() is called...". Good: "Given valid credentials, When the user submits login, Then a session token is returned."

**Over-researching** – gather just enough context for a clear spec. Default to skipping research phases unless clearly needed (gap in requirements, unfamiliar APIs, novel features). A spec that reads like a diff is too detailed. A 30-line minimal FIS is fine; zero FIS is not. Target 100-250 lines.


## ORCHESTRATOR ROLE _(if supported by your coding agent)_

You are the orchestrator: parse input, delegate codebase analysis and research to sub-agents, then author the FIS from their findings. Delegate codebase analysis to `andthen:solution-architect`; research to `andthen:documentation-lookup` or `andthen:research-specialist`. Write the FIS yourself to keep it coherent.


## WORKFLOW

### 0. Parse Input & Get Requirements

**If `--issue` flag present**: use `gh issue view <number>` to fetch issue details. Use as feature request. Store issue number for FIS reference.

**If ARGUMENTS is a directory with `requirements-clarification.md`** (from `andthen:clarify`): read it; use clarified scope, functional requirements, edge cases, success criteria, design decisions, wireframes as the feature request. Skip or reduce research phases (clarify already did discovery). Only do codebase research and any external/API research the requirements reference but haven't investigated.

**If ARGUMENTS use `story {story_id} of {path-to-plan.md}`**: read the plan; locate the story by ID; use its scope, acceptance criteria, dependencies, and phase context as feature request. If the story has **Key Scenarios**, use them as seeds for the Scenarios section (Step 3) — elaborate each seed into full Given/When/Then format. Store plan path and story ID for output updates.

**Otherwise**: use inline description or file reference as the feature request.


### 1. Priming and Project Understanding

Analyse the codebase to understand project structure, relevant files and similar patterns. Use `tree -d` and `git ls-files | head -250` for overview. Use the `Explore` agent _(if supported)_ for deeper context.


### 2. Feature Research and Design

Fully understand the feature request. Identify any ambiguities. Research only what's needed:

- **Codebase research**: similar features/patterns, files to reference with line numbers, existing conventions and test patterns. Delegate to `andthen:solution-architect` _(if supported)_.
- **External research** _(if references to APIs/libraries without prior research)_: current documentation, known gotchas. Delegate to `andthen:research-specialist` or `andthen:documentation-lookup` _(if supported)_.
- **Architecture trade-offs** _(if no ADR in ARGUMENTS)_: analyze 1-3 approaches, document risks. Delegate to `andthen:solution-architect` _(if supported)_.
- **UI research** _(if applicable, and no prior wireframes)_: existing patterns, create wireframes. Delegate to `andthen:ui-ux-designer` _(if supported)_.

Save substantial findings to `.agent_temp/research/{feature-name}/` and link from the FIS.

Ask user ONLY if implementation is blocked by ambiguity.


### 3. Write Scenarios

Before generating the full FIS, write the **Scenarios** section first. Scenarios are concrete examples of expected behavior (BDD-style Given/When/Then) that serve triple duty: requirement, test specification, and proof-of-work contract. Start with the happy path, then edge cases, then error cases. 3-7 scenarios is the sweet spot. See the FIS authoring guidelines for detailed guidance.

**Lock down proof-of-work**: every Success Criterion must have a proof path — at least one scenario (for behavioral criteria) or a task Verify line (for structural criteria). If a criterion has no proof path after writing scenarios, either add a scenario or flag it for a Verify line during FIS generation.


### 4. Generate FIS

#### Gather Context (as references, not inline content)
- Research docs from previous phase (link to files in `.agent_temp/research/`)
- ADRs and architecture docs; file paths with line numbers for patterns to follow
- UI wireframes/mockups; design system references; external documentation URLs
- Ubiquitous Language glossary (`UBIQUITOUS_LANGUAGE.md`) – use canonical terms; flag any contradictions

#### Generate from Template
**IMPORTANT**: Use the `Plan` agent _(if supported by your coding agent)_ to generate the FIS — it provides structured authoring support.

Use the template in the **Appendix** below. Then read and follow the FIS authoring guidelines at
[`${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md`](../../references/fis-authoring-guidelines.md).

> **Optional**: Run `andthen:review-doc` for thorough validation (recommended for large/complex features).


## OUTPUT

**Co-locate with input artifacts when a feature directory exists:**
- Directory input (e.g. clarify output): save FIS inside as `{feature-name}.md`
- Plan story input: save FIS in plan directory as `{story-name}.md`
- Otherwise: save at `docs/specs/{feature-name}.md` _(or as configured in Project Document Index)_
  - GitHub issue input: include issue reference in filename, e.g. `issue-123-feature-name.md`

**Update source plan** – if this spec was created for a plan story:
- Set the story's **FIS** field to the generated FIS file path
- Set the story's **Status** field to `Spec Ready`

### Publish to GitHub _(if --to-issue)_
Create a GitHub issue with `gh issue create`: title `[FIS] {feature-name}`, body = FIS contents, labels `spec`, `fis`. Print the issue URL.


---


## Appendix: FIS Template

**USE THE TEMPLATE**: Read and use the template at [`templates/fis-template.md`](templates/fis-template.md) to generate the Feature Implementation Specification.
