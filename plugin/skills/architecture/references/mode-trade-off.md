# Architecture – Trade-off Mode

**Trade-off analysis** – research technical options, compare them systematically against weighted criteria, and deliver an evidence-based recommendation the user can act on. Optionally formalize the decision as an ADR. Use this mode to make architectural decisions defensible rather than opinion-based.

**Shared reference**: `${CLAUDE_PLUGIN_ROOT}/references/design-tree.md` for multi-dimensional decomposition.

**Inputs**: `TOPIC`, `COUNT`, `OUTPUT_DIR` are declared in SKILL.md `## VARIABLES` (Optional Output Flags + Mode-Specific Flags subsections).

## Contents

Interactive-by-Contract · Principles · Step 1 Define the Decision Space · Step 2 Design It Twice · Step 3 Parallel Deep Research · Step 4 Analysis · Step 5 Recommendation · Step 6 Documentation · Report Contents · Verification Before Finishing

## Interactive-by-Contract

Trade-off analysis is a *decision* skill, not an execution skill. **Three hard gates** require user input before the skill can continue:

1. **Step 1a** – decision context (core question, constraints, success criteria, dealbreakers).
2. **Step 1c** – candidate options + weighted criteria. The most load-bearing gate: wrong criteria/weights → wrong recommendation, and Step 3 deep research is wasted.
3. **Step 5** – recommendation acceptance + ADR / refinement / deeper-analysis decision.

At each gate, the same mechanical pattern applies: **present a structured proposal back to the user** (recommendation first, one-line rationale, real alternatives, room for free-form input), **ask** using an interactive user input tool when available (e.g. `AskUserQuestion` in Claude Code, 3–5 numbered markdown questions otherwise), **wait for the response**, then continue. Recommending an answer is allowed and encouraged; treating it as confirmed without user input is not.

### Named failure mode: implicit confirmation from detailed input

**Detailed `INPUT` is never implicit gate confirmation** – it's the *context* the answers derive from, not the answers. The contract is presenting a proposal back and getting explicit confirm-or-adjust. Rationalizing past it ("prompt was detailed enough, so I recorded assumptions instead of asking") is this skill's top-reported failure across Claude Code and Codex.

### `--auto` is the only bypass

When set, infer all gate answers from `INPUT` conservatively, record the assumptions in the report under labeled sections (*Decision Context*, *Criteria + Weights*, *ADR decision*), and document open questions. Without the flag, the gates apply regardless of how detailed `INPUT` is.

## Principles

- Do not research extra options, skip weighting, or recommend based on popularity alone.
- Don't let a long criteria catalog replace actual judgment – name only the criteria that move the recommendation, and identify which are decisive vs. tie-breakers.

## Step 1 – Define the Decision Space

### 1a. Clarify Decision Context _(hard gate – ask, do not infer)_

Even when `INPUT` addresses these explicitly, present them back as a structured proposal and ask the user to confirm or adjust:
- Core question
- Constraints
- Success criteria
- Dealbreakers

Wait for the response before continuing.

### 1b. Design Space Decomposition

For multi-dimensional decisions, decompose the space instead of listing flat options. See `${CLAUDE_PLUGIN_ROOT}/references/design-tree.md`.

1. Identify the independent dimensions.
2. List viable options per dimension.
3. Mark incompatible or conditional pairings.
4. Derive up to `COUNT` candidate solutions from the surviving combinations.

If the decision is single-dimensional, skip decomposition and list direct options.

### 1c. Define Weighted Criteria _(hard gate – ask, do not infer)_

Choose only the criteria that matter for this decision. Typical examples:
- Developer experience and maintainability
- Performance and scalability
- Security and reliability
- Deployment/operations complexity
- Cost and time-to-market
- Team fit and long-term viability

**Present a proposed weighting table** (criterion + suggested weight + one-line rationale) **and the candidate-options list** back to the user, and **ask them to confirm or adjust** before Step 3 deep research begins. Wait for the response. Wrong criteria/weights → wrong recommendation.

## Step 2 – Design It Twice _(optional)_

Use this only when the design space is still fuzzy or heavily contested.

1. Pick 3+ contrasting constraint lenses.
2. Spawn parallel sub-agents, each instructed to run the `andthen:architecture` skill in `advise` mode under one lens.
3. Have each agent fully commit to its lens and return an interface sketch, what the design hides/exposes, trade-offs, and where it breaks down.
4. Synthesize the results in prose: convergences, tensions, and which design dimensions are most sensitive to constraints.

Skip this phase for simple technology choices or well-understood options.

## Step 3 – Parallel Deep Research

Focus on contested dimensions and risky conditions, not the whole design space – dimensions where every surviving option meets the criteria need no deep research.

For each option, launch a parallel sub-agent (the `research` agent when available) to investigate:
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

## Step 4 – Analysis

Produce a compact comparison that includes:
- Option strengths, weaknesses, and best-fit scenarios
- Weighted scores
- Major risks and mitigations
- Clear dealbreakers or context-dependent trade-offs
- Any hybrid approach worth considering

Focus on the decision factors that actually move the recommendation.

## Step 5 – Recommendation _(hard gate – ADR decision; ask, do not infer)_

Write the recommendation with:
- Chosen option
- Evidence-based rationale
- Implementation path
- Risks and mitigations
- Confidence level
- Alternatives worth reconsidering if conditions change

Present it to the user. **Formalizing as an ADR is the default next step** – that is the primary purpose of running trade-off analysis. Ask whether to:
- **Proceed with ADR creation** _(default; Step 6 produces it)_
- **Refine first** (adjust criteria, weights, or options and re-run before the ADR)
- **Deeper analysis** of a specific option before deciding
- **No ADR** (trade-off report only; recommendation stands as advisory)

Wait for the response. Do not assume – the ADR has organizational implications the user owns.

## Step 6 – Documentation

Store artifacts in `OUTPUT_DIR/[topic-slug]/`:
- `design-tree.md` for multi-dimensional decisions
- `research.md` for consolidated option findings
- `tradeoff-matrix.md` for the comparison
- `recommendation.md` for the final recommendation

**If the user chose "Proceed with ADR creation" in Step 5, produce the ADR** ("Refine first" and "Deeper analysis" loop back to earlier steps before Step 6; "No ADR" skips this block):
- Use the `ADRs` location from the **Project Document Index** if the project has one; otherwise create the default ADR directory at `docs/adrs/`
- Follow the existing numbering scheme, or start with `ADR-001`
- Also keep a copy at `OUTPUT_DIR/[topic-slug]/adr.md`
- **Populate from trade-off artifacts**:
  - *Status*: `Proposed` (until the user accepts it)
  - *Context*: decision context + weighted criteria from Step 1
  - *Decision*: the chosen option from Step 5 plus its headline rationale
  - *Consequences*: positive/negative implications drawn from the trade-off matrix for the chosen option
  - *Alternatives Considered*: the scored non-chosen options with a one-line rejection rationale each
  - *Implementation Notes*: Step 5's implementation path, risks, and mitigations
  - *Project Compliance*: alignment with project-specific architectural guidelines (see `mode-advise.md`); `N/A` if the project has none
  - *References*: link to the trade-off report files (`research.md`, `tradeoff-matrix.md`, `recommendation.md`)

**Register in `DECISIONS.md`** (same gate – only when the user chose "Proceed with ADR creation"):

- Resolve the `Decisions` location from the **Project Document Index** (default: `docs/DECISIONS.md`).
- If the file does not exist, create it from the `DECISIONS.md` template in `${CLAUDE_PLUGIN_ROOT}/references/project-state-templates.md`.
- Append a row to **Current ADRs** with `ID` (e.g. `ADR-001`), `Title`, `Status: Proposed`, and `Scope` (one-phrase summary of where the decision applies). Link the ID cell to the ADR file.
- If the new ADR supersedes a prior decision, **move** the prior row from **Current ADRs** to **Superseded**: leave the new row in Current, add a row to Superseded with `Prior Decision` (linked) / `Superseded By` (linked to the new ADR) / `Notes` (one-line reason). Never delete – the lineage is load-bearing.
- **Idempotent on ADR ID**: if a row with the same ID already exists in Current, update its fields in place rather than appending a duplicate.

See `adr-template.md` for the canonical ADR template.

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
