# Architecture — Trade-off Mode

**Trade-off analysis** — research technical options, compare them systematically against weighted criteria, and deliver an evidence-based recommendation the user can act on. Optionally formalize the decision as an ADR. Use this mode to make architectural decisions defensible rather than opinion-based.

**Shared reference**: `${CLAUDE_PLUGIN_ROOT}/references/design-tree.md` for multi-dimensional decomposition.

**Inputs**: `TOPIC`, `COUNT`, `OUTPUT_DIR` are declared in SKILL.md `## VARIABLES` (Optional Output Flags + Mode-Specific Flags subsections).

## Principles

- Be concise, evidence-based, and proportional to the decision's actual scale.
- Favor the simplest option that satisfies the decision constraints.
- Do not research extra options, skip weighting, or recommend based on popularity alone.

## Step 1 — Define the Decision Space

### 1a. Clarify Decision Context

Get or confirm:
- Core question
- Constraints
- Success criteria
- Dealbreakers

### 1b. Design Space Decomposition

For multi-dimensional decisions, decompose the space instead of listing flat options. See `${CLAUDE_PLUGIN_ROOT}/references/design-tree.md`.

1. Identify the independent dimensions.
2. List viable options per dimension.
3. Mark incompatible or conditional pairings.
4. Derive up to `COUNT` candidate solutions from the surviving combinations.

If the decision is single-dimensional, skip decomposition and list direct options.

### 1c. Define Weighted Criteria

Choose only the criteria that matter for this decision. Typical examples:
- Developer experience and maintainability
- Performance and scalability
- Security and reliability
- Deployment/operations complexity
- Cost and time-to-market
- Team fit and long-term viability

Ask the user to confirm the options and the weighted criteria before deep research.

## Step 2 — Design It Twice _(optional)_

Use this only when the design space is still fuzzy or heavily contested.

1. Pick 3+ contrasting constraint lenses.
2. Spawn parallel sub-agents, each instructed to run the `andthen:architecture` skill in `advise` mode under one lens.
3. Have each agent fully commit to its lens and return an interface sketch, what the design hides/exposes, trade-offs, and where it breaks down.
4. Synthesize the results in prose: convergences, tensions, and which design dimensions are most sensitive to constraints.

Skip this phase for simple technology choices or well-understood options.

## Step 3 — Parallel Deep Research

Focus on contested dimensions and risky conditions, not the whole design space — dimensions where every surviving option meets the criteria need no deep research.

For each option, launch a parallel sub-agent to investigate:
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

## Step 4 — Analysis

Produce a compact comparison that includes:
- Option strengths, weaknesses, and best-fit scenarios
- Weighted scores
- Major risks and mitigations
- Clear dealbreakers or context-dependent trade-offs
- Any hybrid approach worth considering

Focus on the decision factors that actually move the recommendation.

## Step 5 — Recommendation

Write the recommendation with:
- Chosen option
- Evidence-based rationale
- Implementation path
- Risks and mitigations
- Confidence level
- Alternatives worth reconsidering if conditions change

Present it to the user and confirm whether they want refinement, deeper analysis, or a formal ADR.

## Step 6 — Documentation

Store artifacts in `OUTPUT_DIR/[topic-slug]/`:
- `design-tree.md` for multi-dimensional decisions
- `research.md` for consolidated option findings
- `tradeoff-matrix.md` for the comparison
- `recommendation.md` for the final recommendation

If the user wants an ADR:
- Use the `ADRs` location from the **Project Document Index** if the project has one; otherwise create the default ADR directory at `docs/adrs/`
- Follow the existing numbering scheme, or start with `ADR-001`
- Also keep a copy at `OUTPUT_DIR/[topic-slug]/adr.md`

See `mode-advise.md` for the ADR template.

## Report Contents

Trade-off mode report must include:
1. Executive Summary (the recommendation in one paragraph)
2. How to Read This Report (legend for any weighting/criteria notation used)
3. Decision context, constraints, success criteria, dealbreakers
4. Candidate options (with brief descriptions)
5. Weighted criteria and scores (comparison matrix)
6. Risks and mitigations per option
7. Recommendation with evidence-based rationale, implementation path, and confidence level
8. Alternatives worth reconsidering if conditions change

## Verification Before Finishing

- All options were researched with evidence
- Criteria were applied consistently
- Risks and costs are explicit
- The recommendation answers the user's actual decision
