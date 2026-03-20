---
description: Create a Feature Implementation Specification from requirements or a plan story. Trigger on 'write spec', 'create FIS', 'specify this feature'.
argument-hint: <description> | --issue <number> [--to-issue]
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
```


## INSTRUCTIONS

- **Make sure `ARGUMENTS` is provided** — otherwise **STOP** immediately and ask the user to provide the feature requirements.
- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails**
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Spec generation only** - No code changes, commits, or modifications during execution of this command
- **Remember**: Agents executing the FIS only get the context you provide. Include all necessary documentation, examples, and references.
- **Read project learnings** — If `LEARNINGS.md` exists (check Project Document Index for location), read it before starting to avoid known traps and error patterns


## GOTCHAS
- Generating a FIS without reading the codebase first — architecture analysis must precede specification
- Over-specifying implementation details that constrain the implementer unnecessarily
- Acceptance criteria that can't be verified programmatically — every criterion needs a verify command


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

#### Additional Research - If Needed
- Only perform research if the feature request lacks sufficient detail or context
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
- Ubiquitous Language glossary (`UBIQUITOUS_LANGUAGE.md`) — use canonical terms in the FIS; flag any terms that contradict the glossary

#### Generate from Template
**USE THE TEMPLATE**: Generate the FIS using the template in the **Appendix** below as your structure.

#### Key Generation Guidelines
1. Each task: atomic, self-contained, with file:line references
2. Mark parallelizable tasks with [P]
3. Reference patterns, don't reproduce them
4. Each task must include a **`Verify:`** line — concrete, observable proof that the task was completed correctly (e.g. command output, file existence, test result, UI state). This enables meaningful gap analysis during execution.
5. Stay within 300-500 line target
6. Replace `<path-to-this-file>` in the self-executing callout with the actual FIS output path


### 4. Self-Check

Quick sanity check before saving:
- [ ] FIS follows template structure
- [ ] All tasks are atomic and have file:line references where relevant
- [ ] ADR clearly states the decision
- [ ] No over-specification — if a section feels padded, trim it

#### Confidence Check
Rate your FIS 1-10 for single-pass implementation success:
- **9-10**: All context present, clear decisions, validation automated
- **7-8**: Good detail, minor clarifications might be needed
- **<7**: Missing context, unclear architecture, needs revision

**If score <7**: Revise or ask for user clarification.

> **Optional**: Run the `andthen:review-doc` skill for thorough validation (recommended for large/complex features). Skip for small/clear features — issues surface during execution anyway.


## OUTPUT
Save FIS as: _`<project_root>/docs/specs/{feature-name}.md`_ _(or as configured in **Project Document Index**)_
- If from GitHub issue: include issue reference in filename, e.g. `issue-123-feature-name.md`

**Update source plan** — if this spec was created for a story from a `plan.md`:
- Set the story's **FIS** field to the generated FIS file path
- Set the story's **Status** field to `In Progress`

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
