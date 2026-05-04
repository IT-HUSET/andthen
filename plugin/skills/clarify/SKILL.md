---
description: Clarify requirements through systematic discovery of gaps, edge cases, and scope boundaries. Trigger on 'clarify this', 'clarify requirements', 'what are the requirements', 'discover requirements'.
argument-hint: "[requirements source: description or file path | --issue <number>] [--to-issue]"
---

# Clarify Requirements


Transform incomplete requirements into complete, actionable specifications through systematic discovery of gaps, edge cases, and scope boundaries.


## VARIABLES

_Requirements to clarify (**required**):_
INPUT: $ARGUMENTS (strip any flag tokens like `--issue` or `--to-issue` before interpreting the remainder as the requirements source — description or file path)

### Optional Flags
- `--issue <number>` → Fetch and use a GitHub issue as requirements input
- `--to-issue` → After Step 4 Validation, save the clarification doc locally (as today), then create a NEW GitHub issue with the doc body via `gh issue create --title "Requirements Clarification: <name>" --body-file <path>`. When an input issue was supplied (via `--issue <N>` or a GitHub issue URL), append `Refs #<N>` as the last line of the issue body. The flag never comments on or edits the input issue. Print the new issue URL.

_Output directory for clarified requirements:_
OUTPUT_DIR: `<project_root>/docs/specs/` _(or as configured in **Project Document Index**)_


## INSTRUCTIONS

- Require `INPUT`. Stop if missing.
- **Interactive process** — ask questions iteratively and wait for user input before proceeding. Recommending an answer is allowed (see Step 2); treating it as confirmed without user input is not.
- **Check before asking** — if the answer lives in the codebase, existing docs, or the **Project Document Index**, look it up. State derivable facts directly; surface ambiguous findings or codebase-vs-INPUT conflicts as recommendations to confirm. *Exception:* a prior clarification doc is a baseline to amend (see Step 1 *Amendment check*), not a lookup that closes discovery.
- Challenge assumptions, find edge cases, identify ambiguities.
- Clarify requirements, do not design solutions.

### Requirements vs. Implementation Boundary
Clarify operates at the **requirements level** — decisions that users, stakeholders, or product owners care about. The test is **load-bearing-ness**, not topic: *would the answer change user-visible behavior, scope, or acceptance criteria?*

- **In scope — load-bearing technical questions**: offline support; sync semantics; user-visible auth model (IdP, SSO, MFA); data residency; user-facing limits (file size, rate, retention); choice of externally-visible third-party providers; platform or device targets.
- **Out of scope — implementation-only choices**: library or framework selection; caching strategy; internal API shape; token format; code organization; DB engine. These belong downstream in the `andthen:spec` skill or the `andthen:architecture` skill (`--mode trade-off`).

Litmus when the load-bearing test is unclear: *would a non-developer stakeholder care about the answer itself — not a downstream consequence of it?*


## GOTCHAS
- Agent answers its own questions instead of waiting for user input
- Treating a recommended answer as confirmed when the user hasn't addressed it
- Asking the user things that are already answerable from the codebase or existing docs (except a prior clarification doc in amendment mode — that is a baseline to extend)
- Scope creep: expanding beyond the original request
- Jumping to solution design instead of requirement discovery


## WORKFLOW

### 1. Parse and Assess Input

1. **Parse INPUT** - Determine type: inline description, file path, `--issue`, or URL
   - If `--issue <number>` flag present (or INPUT is a GitHub issue URL): fetch the body with `gh issue view <number>` and use its content as raw requirements input. Store the issue number for reference in the output header. On re-invocation against an existing `issue-{n}-*/` directory, the issue body becomes the delta and *Amendment check* below applies.
   - If file path: Read and extract requirements
   - If URL: Fetch and extract requirements
   - If description: Use directly
   - **Amendment check** — derive a feature slug from INPUT, then check if `OUTPUT_DIR/<slug>/` (or a path in INPUT) contains a prior clarification doc — recognised by an `# Requirements Clarification:` H1 or a `Decisions Log` table, any filename, never a `prd.md` or FIS file. If yes, switch to **amendment mode**: existing doc = baseline, INPUT = delta. Re-run Step 2 *Discovery Interview* only for new or still-open gaps; Step 3 updates the baseline in place at its existing path. Multiple matches: prefer most-recently-modified. A prior doc is a baseline to extend, not an authority that closes discovery.

2. **Initial assessment** - Document what's explicitly stated, what's assumed, what's missing (amendment mode: only what the delta adds, changes, or contradicts)

3. **Gap identification** - List gaps in: functional requirements, user flows, edge cases, success criteria, scope boundaries

4. **Design space decomposition** — when the feature has **user-visible or product-level** decisions with multiple viable approaches, decompose load-bearing dimensions only (see `${CLAUDE_PLUGIN_ROOT}/references/design-tree.md` for the Dimension Independence + cross-consistency rubric). Implementation-only dimensions are downstream concerns for the `andthen:spec` skill or the `andthen:architecture` skill (`--mode trade-off`). Include the decomposition in the requirements output. _Skip for simple features with no meaningful design alternatives._

**Gate**: Assessment complete with documented gap list and design space decomposition (if applicable)


### 2. Discovery Interview

Ask targeted questions based on identified gaps and unresolved design dimensions. Ask 3-5 questions at a time, then stop and wait for the user's response before continuing. Iterate until no major gaps remain. **Amendment mode**: scope questions and the gate to delta-introduced gaps only — do not re-ask resolved baseline questions.

**Recommend, don't decide.** Offer a best-guess answer with a one-line rationale for each question so the user can ratify or redirect. If you have no defensible basis, ask open-ended instead of fabricating one. Wait for input either way — unaddressed recommendations are unanswered, not confirmed.

**Probe before accepting load-bearing answers.** A confident-sounding answer can still be wrong. Apply the matching technique from `references/discovery-interview-techniques.md`: Five Whys (stated solution, not problem), Scenario Testing (abstract requirement), Extremes and Boundaries (fuzzy scope), Trade-off Forcing ("everything is important"), Laddering (too specific or too vague), Perspective Shift (happy-path fixation).

> After presenting questions, stop your response and wait for user input. Use the `AskUserQuestion` tool if available. Do not proceed to Step 3 until the user has answered and no major gaps remain.

Cover these areas when relevant: scope & boundaries (in/out of scope, MVP, deferrals); users & flows (roles, happy path, alternate paths, UI involvement); edge cases & errors (invalid input, failures, boundary conditions); success criteria (acceptance criteria, metrics, test/validation approach); dependencies & constraints (external systems, technical constraints, timeline).

**Gate**: All critical questions answered, no blocking ambiguities, unaddressed recommendations re-surfaced or moved to Open Questions


### 3. Consolidate Requirements

Structure all findings into the requirements document using the template in **REPORT** below (amendment mode: preserve unchanged sections verbatim, add missing template sections only when the delta requires them).

**Gate**: Requirements document complete and structured


### 4. Validation

Review consolidated requirements: all user flows have clear steps; design space decomposition constructed with decisions resolved or flagged; wireframes included if applicable; edge cases identified; scope boundaries explicit; **Not Doing** items specific and justified; success criteria specific and testable; no contradictions; dependencies documented; no vague undefined terms. In amendment mode, validate the *merged* document, not just the delta — contradictions between delta and untouched baseline must be caught here.

Fix any issues found before finalizing.

**Gate**: All validation checks pass


### 4b. Publish to GitHub _(only when `--to-issue`)_

After the local clarification doc is written and validated, publish per **Pattern A** in [`github-publish.md`](${CLAUDE_PLUGIN_ROOT}/references/github-publish.md). Title: `Requirements Clarification: <feature-name>`. Body temp file: `.agent_temp/clarify/<feature-slug>-issue-body.md` when `Refs #<N>` is appended; otherwise pass the local doc path directly to `--body-file`.

The flag is additive — the local doc is the source of truth; the issue is a durable transport record for downstream skills (`andthen:prd --issue <N>`).

**Gate**: Issue created (or skipped when `--to-issue` is absent)


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

Skip this section when `AUTO_MODE=true` — print only the output path and completion summary.

After completion, ask user if they'd like to:
1. **Review visually** – invoke the `andthen:visualize` skill on `requirements-clarification.md` to spot scope and edge-case issues a markdown view obscures.
2. **Create feature spec** – invoke the `andthen:spec` skill on the output directory to generate a FIS from the clarified requirements.
3. **Create a PRD** – invoke the `andthen:prd` skill on the output directory before planning a multi-feature effort.
4. **Proceed to planning** – invoke the `andthen:prd` skill, then the `andthen:plan` skill on the output directory for multi-feature / MVP scope.
5. Review specific areas in more depth.
6. Share with stakeholders for validation.

> **Session tip**: `spec`, `prd`, and `plan` can run in this session. But the heavier skills that follow them — `exec-spec`, `exec-plan` — are context-intensive and perform best in a **clean session**. `plan` also benefits from a clean session when generating the full FIS bundle.
