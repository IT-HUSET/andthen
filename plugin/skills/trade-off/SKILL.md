---
description: Systematic trade-off analysis and technical research for architectural decisions. Trigger on 'compare options', 'trade-off', 'write an ADR', 'which approach'.
argument-hint: "[Topic/decision to research - inline or file path] [Number of alternatives (default is 5)] [Output path (default is docs/research/)]"
---

# Technical Trade-off Research & Analysis

Research technical options, compare them systematically, and deliver an evidence-based recommendation the user can act on.

## VARIABLES

TOPIC: `$1` (required)
COUNT: `$2` (defaults to `5`)
OUTPUT_DIR: `$3` (defaults to `<project_root>/docs/research/` or the Project Document Index location)

## INSTRUCTIONS

- Read the project rules and relevant guidelines before starting.
- Be concise, evidence-based, and proportional to the decision's actual scale.
- Favor the simplest option that satisfies the decision constraints.
- Do not research extra options, skip weighting, or recommend based on popularity alone.

## GOTCHAS

- Recommending a winner without exploring real alternatives
- Missing cost, maintenance, or migration implications
- Letting a huge criteria catalog replace actual judgment

## WORKFLOW

### Phase 0: Validate Input and Context

1. Stop if `TOPIC` is missing.
2. Create `OUTPUT_DIR` if needed.
3. Understand the decision, existing constraints, project context, and success criteria.
4. Read extra docs/guidance only when they materially affect the decision.

**Gate**: Topic, context, and output location are clear

### Phase 1: Define the Decision Space

#### 1.1 Clarify Decision Context

Get or confirm:
- Core question
- Constraints
- Success criteria
- Dealbreakers

#### 1.2 Design Space Decomposition

For multi-dimensional decisions, decompose the space instead of listing flat options. See `plugin/references/design-tree.md`.

1. Identify the independent dimensions.
2. List viable options per dimension.
3. Mark incompatible or conditional pairings.
4. Derive up to `COUNT` candidate solutions from the surviving combinations.

If the decision is single-dimensional, skip decomposition and list direct options.

#### 1.3 Define Weighted Criteria

Choose only the criteria that matter for this decision. Typical examples:
- Developer experience and maintainability
- Performance and scalability
- Security and reliability
- Deployment/operations complexity
- Cost and time-to-market
- Team fit and long-term viability

Ask the user to confirm the options and the weighted criteria before deep research.

**Gate**: Options and criteria are agreed

### Phase 1.5: Design It Twice _(optional)_

Use this only when the design space is still fuzzy or heavily contested.

1. Pick 3+ contrasting constraint lenses.
2. Spawn parallel instances of the `andthen:solution-architect` agent, one per lens.
3. Have each agent fully commit to its lens and return an interface sketch, what the design hides/exposes, trade-offs, and where it breaks down.
4. Synthesize the results in prose: convergences, tensions, and which design dimensions are most sensitive to constraints.

Skip this phase for simple technology choices or well-understood options.

**Gate**: Candidate designs are concrete enough to evaluate

### Phase 2: Parallel Deep Research

For each option, launch a parallel sub-agent _(if supported)_ to investigate:
- Core capabilities and hard limitations
- Performance characteristics
- Integration requirements and dependencies
- Total cost of ownership
- Real-world examples or production use
- Known gotchas, edge cases, and migration costs
- Ecosystem and maintenance signals

Each option should return:
- A score per weighted criterion with justification
- Concrete evidence
- Critical warnings

**Gate**: Every option has evidence, scores, and risks

### Phase 3: Analysis

Produce a compact comparison that includes:
- Option strengths, weaknesses, and best-fit scenarios
- Weighted scores
- Major risks and mitigations
- Clear dealbreakers or context-dependent trade-offs
- Any hybrid approach worth considering

Focus on the decision factors that actually move the recommendation.

**Gate**: Trade-offs are explicit and defensible

### Phase 4: Recommendation

Write the recommendation with:
- Chosen option
- Evidence-based rationale
- Implementation path
- Risks and mitigations
- Confidence level
- Alternatives worth reconsidering if conditions change

Present it to the user and confirm whether they want:
- Refinement
- Deeper analysis
- Formal ADR creation

**Gate**: Recommendation is accepted or refined

### Phase 5: Documentation

Store artifacts in `OUTPUT_DIR/[topic-slug]/`:
- `design-tree.md` for multi-dimensional decisions
- `research.md` for consolidated option findings
- `tradeoff-matrix.md` for the comparison
- `recommendation.md` for the final recommendation

If the user wants an ADR:
- Use the `ADRs` location from the **Project Document Index** if the project has one; otherwise create the default ADR directory at `docs/adrs/`
- Follow the existing numbering scheme, or start with `ADR-001`
- Also keep a copy at `OUTPUT_DIR/[topic-slug]/adr.md`

An ADR should cover:
- Status
- Context
- Decision
- Consequences
- Alternatives considered
- Implementation notes
- References

## REPORT

Before finishing, verify:
- All options were researched with evidence
- Criteria were applied consistently
- Risks and costs are explicit
- The recommendation answers the user's actual decision

## FOLLOW-UP ACTIONS

Offer:
- ADR creation
- Recommendation adjustments
- Deeper research on a specific option or trade-off
