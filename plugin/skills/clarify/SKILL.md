---
description: Clarify requirements through systematic discovery of gaps, edge cases, and scope boundaries. Trigger on 'clarify', 'what are the requirements', 'discover requirements'.
argument-hint: "[Requirements source - description, file path, or GitHub issue URL]"
---

# Clarify Requirements
Transform incomplete requirements into complete, actionable specifications through systematic discovery of gaps, edge cases, and scope boundaries.


## VARIABLES

_Requirements to clarify (**required**):_
INPUT: $ARGUMENTS

_Output directory for clarified requirements:_
OUTPUT_DIR: `<project_root>/docs/specs/` _(or as configured in **Project Document Index**)_


## INSTRUCTIONS

- **Make sure `INPUT` is provided** - otherwise **STOP** immediately and ask user for input
- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails**
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Interactive process** - Ask questions iteratively; don't assume answers. After asking questions, **STOP and WAIT** for user responses before proceeding
- **Be thorough** - Challenge assumptions, find edge cases, identify ambiguities
- **Stay focused** - Clarify requirements, don't design solutions
- **Document decisions** - Record rationale for scope choices and trade-offs


## GOTCHAS
- Agent answers its own questions instead of waiting for user input — STOP and WAIT is critical
- Scope creep: expanding beyond the original request — stay focused on what was asked
- Jumping to solution design instead of requirement discovery


## WORKFLOW

### 1. Parse and Assess Input

1. **Parse INPUT** - Determine type: inline description, file path, or URL
   - If file path: Read and extract requirements
   - If URL: Fetch and extract requirements
   - If description: Use directly

2. **Identify requirement type**
   - **New application/MVP**: Full product scope needed
   - **Feature addition**: Bounded scope within existing system

3. **Initial assessment** - Document:
   - What's explicitly stated
   - What's assumed or implied
   - What's missing or unclear

4. **Gap identification** - List gaps in:
   - Functional requirements
   - User flows and interactions
   - Edge cases and error handling
   - Success criteria
   - Scope boundaries

5. **Design space decomposition** _(see `plugin/references/design-tree.md`)_

   When the feature involves design decisions with multiple viable approaches — whether architectural, UI/UX, or user-facing functionality — decompose the solution space into independent dimensions:

   - Identify **independent dimensions of choice** (e.g., navigation model, data display, authentication method, interaction pattern) — these are peers, not a hierarchy
   - List viable options per dimension (2–5 each)
   - Perform **cross-consistency assessment**: evaluate pairwise compatibility between options across dimensions, marking incompatible or conditional pairings with rationale
   - Use the decomposition to generate targeted questions for the discovery interview — each unresolved dimension is a question to ask

   Include the decomposition in the requirements output so downstream skills (`plan`, `spec`) can reference the resolved decisions.

   _Skip this step for simple features with no meaningful design alternatives._

**Gate**: Assessment complete with documented gap list and design space decomposition (if applicable)


### 2. Discovery Interview

Ask targeted questions based on identified gaps and unresolved design dimensions. Ask 3-5 questions at a time, then **STOP and WAIT for the user's response** before continuing. Do NOT assume or infer answers — you MUST receive actual answers from the user. Iterate until no major gaps remain.

> **CRITICAL**: After presenting questions, you must stop your response and wait for user input. Do not proceed to Step 3 until the user has answered your questions and you've confirmed no major gaps remain. Use the `AskUserQuestion` tool if available in your environment.

**Scope & Boundaries**
- What's explicitly IN scope?
- What's explicitly OUT of scope?
- What's the minimum viable version?
- What can be deferred to future iterations?

**Users & Flows**
- Who are the users? What roles/permissions?
- What's the primary user flow (happy path)?
- What alternate paths exist?
- What's the expected user journey?
- Does this involve UI/frontend work? (determines if wireframes needed)

**Edge Cases & Errors**
- What happens with invalid input?
- How to handle network/service failures?
- What are the boundary conditions (max/min values)?
- How should errors be communicated to users?
- What about concurrent access scenarios?

**Success Criteria**
- How do we know this is done?
- What are the acceptance criteria?
- What metrics define success?
- How will this be tested/validated?

**Dependencies & Constraints**
- What external systems/APIs are involved?
- What technical constraints exist?
- What data/integrations are required?
- Are there timeline or resource constraints?

**Gate**: All critical questions answered, no blocking ambiguities


### 3. Consolidate Requirements

Structure all findings into comprehensive requirements document:

1. **Summary** - 2-3 sentences: what, who, core value
2. **Scope definition** - In scope, out of scope, MVP boundary
3. **Functional requirements** - Core flows, alternate paths, user stories
4. **UI wireframes** _(if applicable)_ - Simple ASCII wireframes for core screens
5. **Edge cases** - Scenarios with expected behavior
6. **Error handling** - Error types, messages, recovery actions
7. **Non-functional requirements** - Performance, security, accessibility
8. **Success criteria** - Testable acceptance criteria
9. **Dependencies** - External systems, integrations
10. **Open questions** - Any remaining items for later phases

**Gate**: Requirements document complete and structured


### 4. Validation

Review consolidated requirements for quality:

- [ ] All user flows have clear steps
- [ ] Design space decomposition constructed with decisions resolved or flagged (if applicable)
- [ ] UI wireframes included (if applicable)
- [ ] Edge cases identified with expected behavior
- [ ] Scope boundaries explicit (in/out)
- [ ] Success criteria specific and testable
- [ ] No contradictions between requirements
- [ ] Dependencies documented
- [ ] No vague terms without definitions

Fix any issues found before finalizing.

**Gate**: All validation checks pass


### 5. Domain Language Extraction _(if domain complexity warrants)_

If the project involves significant domain complexity (business rules, multiple bounded contexts, domain-specific terminology):

1. Review the consolidated requirements for domain-relevant terms
2. Extract candidate terms: entities, actions, states, rules, relationships
3. Identify synonym clusters and ambiguous terms
4. Create or update `UBIQUITOUS_LANGUAGE.md` with initial glossary:
   - Group terms by domain cluster
   - Pick canonical names, list synonyms to avoid
   - Note bounded contexts where applicable

> **Skip** for simple projects (CRUD apps, utilities, scripts) or when domain language is obvious and unambiguous.

**Gate**: Domain glossary created or skipped with rationale


## REPORT

Generate markdown document with:

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

## Functional Requirements

### User Stories
- As a [user], I want [goal], so that [benefit]

### Core Flows
1. [Primary flow with steps]

### Alternate Flows
- [Alternate paths and variations]

### UI Wireframes
<!-- Include only if requirements involve UI work -->
```
+----------------------------------+
|  [Screen Name]                   |
+----------------------------------+
|  [Header/Nav]                    |
+----------------------------------+
|                                  |
|  [Main Content Area]             |
|  - Key element 1                 |
|  - Key element 2                 |
|                                  |
+----------------------------------+
|  [Actions/Footer]                |
+----------------------------------+
```

## Design Decisions
<!-- Include only if design space decomposition was constructed -->
### Design Space Decomposition
```
[Feature Name]
├── [Dimension 1]: [Option A] ← chosen · [Option B] · [Option C] ✗ (pruned)
├── [Dimension 2]: [Option X] ← chosen · [Option Y]
└── [Dimension 3]: [Open — deferred to spec/trade-off]
```

### Cross-Consistency Notes
- [Option] + [Option] — incompatible: [reason]
- [Option] + [Option] — conditional: [condition]

### Resolved Decisions
| Dimension | Choice | Rationale |
|-----------|--------|-----------|
| [Dimension] | [Chosen option] | [Why] |

### Open Design Questions
- [Dimensions needing further analysis via `andthen:trade-off`]

## Edge Cases
| Scenario | Expected Behavior |
|----------|------------------|
| [Edge case] | [Handling] |

## Error Handling
| Error | User Message | Recovery |
|-------|--------------|----------|
| [Error type] | [Message] | [Action] |

## Non-Functional Requirements
- **Performance**: [Expectations]
- **Security**: [Requirements]
- **Accessibility**: [Standards]

## Success Criteria
- [ ] [Testable criterion 1]
- [ ] [Testable criterion 2]

## Dependencies
| Dependency | Purpose | Risk |
|------------|---------|------|
| [System/API] | [Why needed] | [Risk level] |

## Open Questions
- [Any remaining ambiguities for later phases]

## Decisions Log
| Decision | Rationale | Date |
|----------|-----------|------|
| [Choice made] | [Why] | [When] |
```

Store report in: `OUTPUT_DIR/<feature-name>/requirements-clarification.md`

If domain language extraction was performed, also store: `docs/UBIQUITOUS_LANGUAGE.md` _(or as configured in **Project Document Index**)_

When complete, print the report's **relative path from the project root**. Do not use absolute paths.


## FOLLOW-UP ACTIONS

After completion, ask user if they'd like to:
1. Create feature spec (`andthen:spec`) — for single features
2. Proceed to planning (`andthen:plan <output-directory>`) — for multi-feature / MVP scope. The plan command will automatically pick up the `requirements-clarification.md` from the output directory and use it as the basis for PRD creation, avoiding duplicate discovery
3. Review specific areas in more depth
4. Share with stakeholders for validation
