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
- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails**
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Spec generation only** - No code changes, commits, or modifications during execution of this command
- **Remember**: Agents executing the FIS only get the context you provide. Include all necessary documentation, examples, and references.
- **Read project learnings** – If `LEARNINGS.md` exists (check Project Document Index for location), read it before starting to avoid known traps and error patterns


## GOTCHAS
- Generating a FIS without reading the codebase first – architecture analysis must precede specification
- **Describing detailed code changes instead of outcomes** – tasks should state what must be TRUE when done, not _exactly_ what code to write. The implementing agent decides *how*. Bad: "Create lib/auth.ts with login() and logout() functions". Good: "Auth module with login/logout capability; follow pattern at lib/users.ts:10-30"
- Over-specifying implementation details that constrain the implementer unnecessarily – a spec that reads like a diff is too detailed
- Acceptance criteria that can't be verified programmatically – every criterion needs a verify command
- **Over-researching** – the goal is enough context to write a clear spec, not exhaustive exploration. Default to skipping research phases unless clearly needed (e.g. gap in requirements, unfamiliar APIs/libraries, or novel features etc).

### Common Rationalizations

These are the excuses you will generate to skip steps. Recognize them.

| Rationalization | Reality |
|---|---|
| "I know this codebase well enough to skip analysis" | You know what you remember, not what's there now. A 5-minute codebase scan catches the refactor that landed last week. |
| "I'll add implementation details to help the implementer" | A spec that reads like a diff constrains the implementer to your assumptions. Specify *what must be true*, not *what code to write*. The implementer sees the codebase – you don't need to describe it. |
| "This feature is simple, it barely needs a spec" | Simple features don't need long specs, but they still need acceptance criteria, a verify line, and scope boundaries. A 30-line minimal FIS is fine. Zero FIS is not. |
| "I'll skip research – I know this API/library" | Your knowledge has a training cutoff. The API may have changed, been deprecated, or gained a better pattern. A 2-minute doc lookup beats a 20-minute debugging session. |
| "More detail is better — I want to be thorough" | Spec bloat is worse than spec gaps. A 400-line FIS signals unclear thinking, not thoroughness. Target 100-250 lines. If it's longer, you haven't made enough decisions — or you're writing code instead of specifying outcomes. |
| "I'll put all the tasks in one group since they're closely related" | Groups over 4 implementation tasks exhaust sub-agent context. The tasks feel related to *you* because you hold the full picture. The sub-agent doesn't. Split at natural boundaries. |


## ORCHESTRATOR ROLE _(if supported by your coding agent)_

You are the orchestrator. Your job is to:
- Parse input requirements and determine scope
- Delegate codebase analysis and research to sub-agents
- Author the FIS using the template, informed by sub-agent findings
- Ensure the FIS is complete and all sections populated

### Phase Delegation

1. **Codebase Analysis**: Delegate to a sub-agent (andthen:solution-architect).
   Provide: feature scope, key directories, what to look for.
   Receive: architecture summary, relevant patterns, existing code to build on,
   integration points, potential conflicts.

2. **Research** (if needed): Delegate to andthen:documentation-lookup
   or andthen:research-specialist for API docs, library usage, etc.

3. **FIS Authoring**: Write the FIS yourself using the template and
   sub-agent findings. This keeps the spec coherent and consistent.


## WORKFLOW

### 0. Parse Input & Get Requirements

**If `--issue` flag present (or if ARGUMENTS contain description that refers to GitHub issue(s)):**
1. Extract issue number(s) from ARGUMENTS
2. Use `gh issue view <number>` to fetch issue details (title, body, labels, comments)
3. Use issue content as the feature request
4. Store issue number for reference in generated FIS

**If ARGUMENTS is a directory containing `requirements-clarification.md`** (output from `andthen:clarify`):
1. Read `requirements-clarification.md` from the directory
2. Use the clarified requirements as the feature request – scope, functional requirements, edge cases, success criteria, design decisions, and any wireframes are all pre-resolved
3. Also read any other artifacts in the directory (design space decomposition, research files, ubiquitous language glossary)
4. Store the directory path for FIS output co-location
5. **Skip or reduce** the research phases in Step 2 – clarify has already done requirements discovery, gap analysis, and design space exploration. Only perform additional *codebase* research (Step 2, section 1) and *external/API* research if the clarified requirements reference libraries or services not yet investigated.

**If ARGUMENTS use the plan-story form `story {story_id} of {path-to-plan.md}`:**
1. Read the referenced `plan.md`
2. Locate the matching story by ID
3. Use that story's scope, acceptance criteria, dependencies, and surrounding phase context as the feature request
4. Store the source plan path and story ID for output updates

**Otherwise:**
- Use inline description or file reference from ARGUMENTS as the feature request


### 1. Priming and Project Understanding

- Analyse the codebase to properly understand the project structure, relevant files and similar patterns
   - Use commands like `tree -d` and `git ls-files | head -250` to get overview of codebase structure
   - For complex codebase exploration, consider using the Explore agent _(if supported by your coding agent)_
- Use the `Explore` agent _(if supported by your coding agent)_ to gather additional context about the project, architecture, patterns etc.


### 2. Feature Research and Design

#### Analyze Requirements
- Fully understand the feature request and requirements
- If from GitHub issue: include issue number reference, labels, and any relevant discussion from comments
- Note any provided documentation, examples, or constraints
- **Read additional guidelines and documentation** - Read additional relevant guidelines and documentation (API, guides, reference, etc.) as needed
- Determine _completeness of requirements_ - Identify any ambiguities or missing details that need clarification
  - **Identify** if additional research is needed

#### Additional Research - Only If Needed
- **Keep research minimal** — gather just enough context to write a clear spec, not to exhaustively explore. Default to skipping research sub-phases unless clearly needed.
- Use **parallel sub-agents** _(if supported by your coding agent)_ for research tasks - multiple Task calls in one message.
- Save findings to _`<project_root>/.agent_temp/research/{feature-name}/`_ **only** if substantial, and add links to generated FIS. Note: If only a file/URL is needed, do not create a research file, just add the reference.

##### 1. Codebase Research:
- Search codebase for relevant files and similar patterns
   - Use command like `tree -d` and `git ls-files | head -250` to get an overview of the codebase structure
- Similar features/patterns in the codebase
- Files to reference with exact line numbers
- Existing conventions and test patterns
- Existing patterns and architecture
- Recommended agents _(if supported by your coding agent)_: `andthen:research-specialist`, `andthen:solution-architect`

##### 2. External Research:
If _`ARGUMENTS`_ includes references to research already conducted, then use those as your primary research sources.

_Otherwise - if no such references are present_ - perform external research:
    - Search for similar features/patterns online
    - Library/framework documentation (include specific URLs)
    - Implementation examples (GitHub/StackOverflow/blogs)
    - UI inspiration
    - Best practices and common pitfalls
    - General explorative and deep web research
    - Recommended agents _(if supported by your coding agent)_: `andthen:research-specialist`, `andthen:solution-architect`, `andthen:ui-ux-designer`

##### 3. Research Multiple Architectural Approaches and Trade-offs
If _`ARGUMENTS`_ includes a reference to an ADR or other architecture decision document, then simply use that as the architecture.

_Otherwise - if no such reference is present_ - perform architecture research:
    - Analyze 1-3 different approaches with trade-offs
    - Consider the trade-offs of different approaches 
    - Evaluate implementation complexity, performance implications etc
    - Document potential risks and mitigation strategies
    - Create architecture diagrams (when needed)
    - Recommended agents _(if supported by your coding agent)_: `andthen:solution-architect`

##### 4. UI Designs Research (when applicable)
If _`ARGUMENTS`_ includes references to UI research already conducted, then use those as your primary research sources.

_Otherwise - if no such references are present_ - perform UI research:
    - Explore existing UI patterns and components
    - Download appropriate design inspiration assets
    - Gather inspiration from design systems and libraries
    - Create UI wireframes, mockups and sketches
    - Create and describe UI flows
    - Recommended agents _(if supported by your coding agent)_: `andthen:ui-ux-designer`

#### User Clarification
Ask ONLY if implementation is blocked by ambiguity.


### 3. Generate FIS
**IMPORTANT**: Use the `Plan` agent _(if supported by your coding agent)_ to create the FIS.

#### Gather Context (as references, not inline content)
- Research docs from previous phase (link to files in `.agent_temp/research/`)
- ADRs and architecture docs
- File paths with line numbers for patterns to follow
- UI wireframes/mockups (required for UI tasks)
- Design system references (required for UI tasks)
- External documentation URLs with specific sections
- Ubiquitous Language glossary (`UBIQUITOUS_LANGUAGE.md`) – use canonical terms in the FIS; flag any terms that contradict the glossary

#### Generate from Template
**USE THE TEMPLATE**: Generate the FIS using the template in the **Appendix** below as your structure.

#### FIS Authoring Guidelines

Read and follow the FIS authoring guidelines at
[`${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md`](../../references/fis-authoring-guidelines.md)
— this covers: authoring principles, generation guidelines, task grouping
heuristics, plan-spec alignment check, and self-check.

> **Optional**: Run the `andthen:review-doc` skill for thorough validation (recommended for large/complex features). Skip for small/clear features – issues surface during execution anyway.


## OUTPUT

**Co-locate with input artifacts when a feature directory exists:**
- If input was a **directory** (e.g. clarify output dir): save FIS inside that directory as `{feature-name}.md`
  - Example: input `docs/specs/data-export/` → FIS at `docs/specs/data-export/data-export.md`
- If input was a **plan story**: save FIS in the plan directory as `{story-name}.md`
  - Example: plan at `docs/specs/dashboard/plan.md` → FIS at `docs/specs/dashboard/s01-auth-middleware.md`
- **Otherwise** (inline description, file reference, issue): save FIS at _`<project_root>/docs/specs/{feature-name}.md`_ _(or as configured in **Project Document Index**)_
  - If from GitHub issue: include issue reference in filename, e.g. `issue-123-feature-name.md`

**Update source plan** – if this spec was created for a story from a `plan.md`:
- Set the story's **FIS** field to the generated FIS file path
- Set the story's **Status** field to `Spec Ready`

`andthen:exec-spec` is responsible for moving `Spec Ready` → `In Progress` when implementation actually starts.

**Remember**: The FIS should be executable with minimal orchestration. All complexity and detail belongs in the FIS itself, not the execution command.

### Publish to GitHub _(if --to-issue)_
If PUBLISH_ISSUE is `true`:
1. Create a GitHub issue using `gh issue create`:
   - Title: `[FIS] {feature-name}`
   - Body: Contents of the generated FIS
   - Labels: `spec`, `fis` (create if they don't exist)
2. Print the issue URL


---


## Appendix: FIS Template

**USE THE TEMPLATE**: Read and use the template at [`templates/fis-template.md`](templates/fis-template.md) to generate the Feature Implementation Specification.
