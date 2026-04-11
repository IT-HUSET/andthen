---
description: Clarify requirements through systematic discovery of gaps, edge cases, and scope boundaries. Trigger on 'clarify', 'what are the requirements', 'discover requirements'.
argument-hint: "[Requirements source - description, file path, or --issue <number>]"
---

# Clarify Requirements


Transform incomplete requirements into complete, actionable specifications through systematic discovery of gaps, edge cases, and scope boundaries.


## VARIABLES

_Requirements to clarify (**required**):_
INPUT: $ARGUMENTS

### Optional Flags
- `--issue <number>` → Fetch and use a GitHub issue as requirements input

_Output directory for clarified requirements:_
OUTPUT_DIR: `<project_root>/docs/specs/` _(or as configured in **Project Document Index**)_


## USAGE

```
/clarify "Users need to export data in multiple formats"  # From inline description
/clarify @docs/feature-request.md                         # From requirements file
/clarify --issue 42                                       # From GitHub issue
```


## INSTRUCTIONS

- **Make sure `INPUT` is provided** - otherwise **STOP** immediately and ask user for input
- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work
- **Interactive process** - Ask questions iteratively; don't assume answers. After asking questions, **STOP and WAIT** for user responses before proceeding
- **Be thorough** - Challenge assumptions, find edge cases, identify ambiguities
- **Stay focused** - Clarify requirements, don't design solutions

### Requirements vs. Implementation Boundary
Clarify operates at the **requirements level** — decisions that users, stakeholders, or product owners care about. Technical choices that only developers evaluate (architecture patterns, library choices, data storage strategies, internal API design, code organization) belong downstream in `andthen:spec` or `andthen:trade-off`. Explore only user-facing behavior, product scope, workflow, content architecture, and access control models.


## GOTCHAS
- Agent answers its own questions instead of waiting for user input – STOP and WAIT is critical
- Scope creep: expanding beyond the original request
- Jumping to solution design instead of requirement discovery
- Drifting into implementation-level decisions during design space decomposition (see boundary above)


## WORKFLOW

### 1. Parse and Assess Input

1. **Parse INPUT** - Determine type: inline description, file path, `--issue`, or URL
   - If `--issue` flag present (or INPUT refers to a GitHub issue): use `gh issue view <number>` to fetch issue details (title, body, labels, comments). Use issue content as requirements input. Store issue number for reference in output.
   - If file path: Read and extract requirements
   - If URL: Fetch and extract requirements
   - If description: Use directly

2. **Initial assessment** - Document what's explicitly stated, what's assumed, what's missing

3. **Gap identification** - List gaps in: functional requirements, user flows, edge cases, success criteria, scope boundaries

4. **Design space decomposition** _(see `plugin/references/design-tree.md`)_

   When the feature involves **user-visible or product-level** design decisions with multiple viable approaches, decompose the solution space into independent dimensions:
   - Identify independent dimensions of choice at the requirements level (navigation model, data display, auth method, interaction pattern) – these are peers, not a hierarchy
   - List viable options per dimension (2–5 each)
   - Assess cross-consistency: evaluate pairwise compatibility between options, marking incompatible or conditional pairings with rationale
   - Use the decomposition to generate targeted questions — each unresolved dimension is a question to ask

   > **Scope guard**: Only decompose dimensions where the *user or stakeholder* would recognize the options as meaningfully different. If a dimension is purely technical (caching strategy, API protocol, DB engine), flag it as a downstream concern for `andthen:spec` or `andthen:trade-off` — do not decompose it here.

   Include the decomposition in the requirements output so downstream skills can reference resolved decisions.
   _Skip this step for simple features with no meaningful design alternatives._

**Gate**: Assessment complete with documented gap list and design space decomposition (if applicable)


### 2. Discovery Interview

Ask targeted questions based on identified gaps and unresolved design dimensions. Ask 3-5 questions at a time, then **STOP and WAIT for the user's response** before continuing. Do NOT assume or infer answers — you MUST receive actual answers from the user. Iterate until no major gaps remain.

> **CRITICAL**: After presenting questions, stop your response and wait for user input. Use the `AskUserQuestion` tool if available in your environment. Do not proceed to Step 3 until the user has answered and you've confirmed no major gaps remain.

Cover these areas when relevant: scope & boundaries (in/out of scope, MVP, deferrals); users & flows (roles, happy path, alternate paths, UI involvement); edge cases & errors (invalid input, failures, boundary conditions); success criteria (acceptance criteria, metrics, test/validation approach); dependencies & constraints (external systems, technical constraints, timeline).

When answers are surface-level, vague, or contradictory, use probing techniques from `plugin/references/discovery-interview-techniques.md`.

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

Review consolidated requirements: all user flows have clear steps; design space decomposition constructed with decisions resolved or flagged; wireframes included if applicable; edge cases identified; scope boundaries explicit; success criteria specific and testable; no contradictions; dependencies documented; no vague undefined terms.

Fix any issues found before finalizing.

**Gate**: All validation checks pass


### 5. Domain Language Extraction _(if domain complexity warrants)_

If the project involves significant domain complexity (business rules, multiple bounded contexts, domain-specific terminology):
1. Extract candidate terms from requirements: entities, actions, states, rules, relationships
2. Identify synonym clusters and ambiguous terms
3. Create or update `UBIQUITOUS_LANGUAGE.md` with initial glossary grouped by domain cluster

> **Skip** for simple projects (CRUD apps, utilities, scripts) or when domain language is obvious.

**Gate**: Domain glossary created or skipped with rationale


## REPORT

Generate markdown document:

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

## Design Decisions
<!-- Include only if design space decomposition was constructed -->
### Design Space Decomposition
[Feature] ├── [Dimension 1]: [Option A] ← chosen · [Option B] · [Option C] ✗ (pruned)

### Cross-Consistency Notes
- [Option] + [Option] – incompatible/conditional: [reason]

### Resolved Decisions
| Dimension | Choice | Rationale |

### Open Design Questions
- [Dimensions needing further analysis via `andthen:trade-off`]

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

Store report in: `OUTPUT_DIR/<feature-name>/requirements-clarification.md`
- If from GitHub issue: use `issue-{number}-{feature-name}/` as the output subdirectory name (e.g. `docs/specs/issue-42-data-export/requirements-clarification.md`). Include issue reference in the document header.

If domain language extraction was performed, also store: `docs/UBIQUITOUS_LANGUAGE.md` _(or as configured in **Project Document Index**)_

When complete, print the report's **relative path from the project root**.


## FOLLOW-UP ACTIONS

After completion, ask user if they'd like to:
1. **Create feature spec** – for single features: `/andthen:spec <output-directory>` (or `$andthen:spec` for Codex CLI). The spec skill will pick up `requirements-clarification.md` from the output directory and use the clarified requirements as input.
2. **Proceed to planning** – for multi-feature / MVP scope: `/andthen:plan <output-directory>` (or `$andthen:plan`). The plan skill will pick up `requirements-clarification.md` and use it as the basis for PRD creation.
3. Review specific areas in more depth
4. Share with stakeholders for validation

> **Session tip**: `spec` and `plan` can run in this session. But the heavier skills that follow them — `exec-spec`, `spec-plan`, `exec-plan` — are context-intensive and perform best in a **clean session**.
