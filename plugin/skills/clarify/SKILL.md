---
description: Clarify requirements through systematic discovery of gaps, edge cases, and scope boundaries. Trigger on 'clarify this', 'clarify requirements', 'what are the requirements', 'discover requirements'.
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


## INSTRUCTIONS

- Require `INPUT`. Stop if missing.
- **Interactive process** — ask questions iteratively and wait for user input before proceeding. Recommending an answer is allowed (see Step 2); treating it as confirmed without user input is not.
- **Check before asking** — if the answer lives in the codebase, existing docs, or the **Project Document Index**, look it up. State derivable facts directly; surface ambiguous findings or codebase-vs-INPUT conflicts as recommendations to confirm.
- Challenge assumptions, find edge cases, identify ambiguities.
- Clarify requirements, do not design solutions.

### Requirements vs. Implementation Boundary
Clarify operates at the **requirements level** — decisions that users, stakeholders, or product owners care about. The test is **load-bearing-ness**, not topic: *would the answer change user-visible behavior, scope, or acceptance criteria?*

- **In scope — load-bearing technical questions**: offline support; sync semantics (real-time vs eventual consistency); user-visible auth model (which IdP, SSO yes/no, MFA requirement); data residency or sovereignty; user-facing limits (file size, rate, retention); choice of externally-visible third-party providers (payment, identity, geolocation); platform or device targets that change what is possible.
- **Out of scope — implementation-only choices**: library or framework selection; caching strategy; internal API shape and protocol; token format and session storage; code organization; DB engine; schema layout; deployment topology. These belong downstream in the `andthen:spec` skill or the `andthen:architecture` skill (`--mode trade-off`).

Litmus when the load-bearing test is unclear: *would a non-developer stakeholder care about the answer itself — not a downstream consequence of it?* Stakeholders care that pages feel fast, but that does not pull caching strategy into scope; the caring is about the consequence, not the choice.


## GOTCHAS
- Agent answers its own questions instead of waiting for user input
- Treating a recommended answer as confirmed when the user hasn't addressed it
- Asking the user things that are already answerable from the codebase or existing docs
- Scope creep: expanding beyond the original request
- Jumping to solution design instead of requirement discovery
- Decomposing implementation-only dimensions during design space decomposition (see boundary above) — note that load-bearing technical questions that shape user-visible behavior, scope, or acceptance criteria *are* fair game


## WORKFLOW

### 1. Parse and Assess Input

1. **Parse INPUT** - Determine type: inline description, file path, `--issue`, or URL
   - If `--issue <number>` flag present (or INPUT is a GitHub issue URL): fetch the body with `gh issue view <number>` and use its content as raw requirements input. Store the issue number for reference in the output header.
   - If file path: Read and extract requirements
   - If URL: Fetch and extract requirements
   - If description: Use directly

2. **Initial assessment** - Document what's explicitly stated, what's assumed, what's missing

3. **Gap identification** - List gaps in: functional requirements, user flows, edge cases, success criteria, scope boundaries

4. **Design space decomposition** _(see `references/design-tree.md`)_

   When the feature involves **user-visible or product-level** design decisions with multiple viable approaches, decompose the solution space into independent dimensions:
   - Identify independent dimensions of choice at the requirements level (navigation model, data display, auth method, interaction pattern) – these are peers, not a hierarchy
   - List viable options per dimension (2–5 each)
   - Assess cross-consistency: evaluate pairwise compatibility between options, marking incompatible or conditional pairings with rationale
   - Use the decomposition to generate targeted questions — each unresolved dimension is a question to ask

   > **Scope guard**: Decompose a dimension only if it passes the load-bearing test in *Requirements vs. Implementation Boundary* above. Implementation-only dimensions are flagged as downstream concerns for the `andthen:spec` skill or the `andthen:architecture` skill (`--mode trade-off`) — do not decompose them here.

   Include the decomposition in the requirements output so downstream skills can reference resolved decisions.
   _Skip this step for simple features with no meaningful design alternatives._

**Gate**: Assessment complete with documented gap list and design space decomposition (if applicable)


### 2. Discovery Interview

Ask targeted questions based on identified gaps and unresolved design dimensions. Ask 3-5 questions at a time, then stop and wait for the user's response before continuing. Iterate until no major gaps remain.

**Recommend, don't decide.** Offer a best-guess answer with a one-line rationale for each question so the user can ratify or redirect. If you have no defensible basis, ask open-ended instead of fabricating one. Wait for input either way — unaddressed recommendations are unanswered, not confirmed.

**Probe before accepting load-bearing answers.** A confident-sounding answer can still be wrong. Apply the matching technique from `references/discovery-interview-techniques.md`: Five Whys (stated solution, not problem), Scenario Testing (abstract requirement), Extremes and Boundaries (fuzzy scope), Trade-off Forcing ("everything is important"), Laddering (too specific or too vague), Perspective Shift (happy-path fixation).

> After presenting questions, stop your response and wait for user input. Use the `AskUserQuestion` tool if available. Do not proceed to Step 3 until the user has answered and no major gaps remain.

Cover these areas when relevant: scope & boundaries (in/out of scope, MVP, deferrals); users & flows (roles, happy path, alternate paths, UI involvement); edge cases & errors (invalid input, failures, boundary conditions); success criteria (acceptance criteria, metrics, test/validation approach); dependencies & constraints (external systems, technical constraints, timeline).

**Gate**: All critical questions answered, no blocking ambiguities, unaddressed recommendations re-surfaced or moved to Open Questions


### 3. Consolidate Requirements

Structure all findings into comprehensive requirements document:
1. **Summary** - 2-3 sentences: what, who, core value
2. **Scope definition** - In scope, out of scope, MVP boundary
3. **Not Doing (for now)** - Explicit non-goals or deferred items with brief reasons
4. **Functional requirements** - Core flows, alternate paths, user stories
5. **UI wireframes** _(if applicable)_ - Simple ASCII wireframes for core screens
6. **Edge cases** - Scenarios with expected behavior
7. **Error handling** - Error types, messages, recovery actions
8. **Non-functional requirements** - Performance, security, accessibility
9. **Success criteria** - Testable acceptance criteria
10. **Dependencies** - External systems, integrations
11. **Open questions** - Any remaining items for later phases

**Gate**: Requirements document complete and structured


### 4. Validation

Review consolidated requirements: all user flows have clear steps; design space decomposition constructed with decisions resolved or flagged; wireframes included if applicable; edge cases identified; scope boundaries explicit; **Not Doing** items specific and justified; success criteria specific and testable; no contradictions; dependencies documented; no vague undefined terms.

Fix any issues found before finalizing.

**Gate**: All validation checks pass


### 5. Domain Language Extraction _(if domain complexity warrants)_

If the project involves significant domain complexity (business rules, multiple bounded contexts, domain-specific terminology):
1. Extract candidate terms from requirements: entities, actions, states, rules, relationships
2. Identify synonym clusters and ambiguous terms
3. Create or update the `Ubiquitous Language` document (see **Project Document Index**) with an initial glossary grouped by domain cluster

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

### Not Doing (for now)
- [Explicit non-goal or deferred item] — [why it is out of scope now]

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

Store report in: `OUTPUT_DIR/<feature-name>/requirements-clarification.md`
- If from GitHub issue: use `issue-{number}-{feature-name}/` as the output subdirectory name (e.g. `docs/specs/issue-42-data-export/requirements-clarification.md`). Include issue reference in the document header.

If domain language extraction was performed, also store it in the `Ubiquitous Language` document location from the **Project Document Index** (default: `docs/UBIQUITOUS_LANGUAGE.md`)

When complete, print the report's **relative path from the project root**.


## FOLLOW-UP ACTIONS

After completion, ask user if they'd like to:
1. **Create feature spec** – invoke the `andthen:spec` skill on the output directory to generate a FIS from the clarified requirements.
2. **Create a PRD** – invoke the `andthen:prd` skill on the output directory before planning a multi-feature effort.
3. **Proceed to planning** – invoke the `andthen:prd` skill, then the `andthen:plan` skill on the output directory for multi-feature / MVP scope.
4. Review specific areas in more depth.
5. Share with stakeholders for validation.

> **Session tip**: `spec`, `prd`, and `plan` can run in this session. But the heavier skills that follow them — `exec-spec`, `exec-plan` — are context-intensive and perform best in a **clean session**. `plan` also benefits from a clean session when generating the full FIS bundle.
