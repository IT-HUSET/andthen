---
name: andthen.trade-off
description: Systematic trade-off analysis and technical research for architectural decisions
argument-hint: [Topic/decision to research - inline or file path] [Number of alternatives (default is 5)] [Output path (default is docs/research/)]
---

# Technical Trade-off Research & Analysis

Conduct parallel research on technical options, perform systematic trade-off analysis, and deliver evidence-based recommendations for informed decision-making.


## Variables

_Topic/decision to research - inline or file path_:
TOPIC=$1 (required)

_Number of alternatives to evaluate_:
COUNT=$2 (defaults to 5 if not provided)

_Output directory_:
OUTPUT_DIR=$3 (defaults to `<project_root>/docs/research/` if not provided) _(or as configured in **Project Document Index**)_

### Variables Validation
Before running:
    - If TOPIC empty, **STOP** - prompt user for decision/topic to research
    - Create OUTPUT_DIR if missing


## Instructions

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails**
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Execute systematic research**, deliver actionable insights.
- **Favor simplicity** - Actively identify over-engineering; recommend simplest solution (KISS, YAGNI, DRY)
- **Conciseness and Brevity** - Ensure created documents are as brief and concise as possible without losing meaning. Unnecessary prose should be avoided, and code listings should be minimized (prefer using pseudo code when possible)

### Anti-Patterns

**NEVER:**
- Research options user didn't ask for
- Skip weighted criteria (biased results)
- Recommend based on "popularity" alone
- Ignore cost/complexity implications
- Deviate from COUNT without user approval


## Workflow

### Phase 0: Discovery and Context

1. **Understand topic/decision to research**
   - Fully understand the topic or decision to research (i.e. _`TOPIC`_), including any provided documents or areas of focus   

2. **Build context**
   - Understand existing patterns, conventions, tech stack
   - Identify problem being solved, success criteria, scope boundaries
   - Note dependencies, constraints, and assumptions
   - **Read additional guidelines and documentation** - Read additional relevant guidelines and documentation (API, guides, reference, etc.) as needed

**Gate**: All relevant specs identified and context understood


### Phase 1: Scope Definition

**1.1 Clarify Decision Context**

Ask user to define:
- **Core question**: What needs deciding?
- **Constraints**: Budget, timeline, team skills, existing tech
- **Success criteria**: Performance, scalability, maintainability requirements
- **Dealbreakers**: Absolute requirements or blockers

**1.2 Design Space Decomposition** _(see `plugin/references/design-tree.md`)_

Instead of listing options directly, decompose the decision into its independent dimensions:

1. **Identify dimensions** — What are the orthogonal axes of choice? (These may be architectural, UI/UX, interaction patterns, or any mix.) Dimensions are independent peers — listing order carries no meaning.
2. **List options per dimension** — Enumerate viable approaches for each axis (2–5 per dimension)
3. **Cross-consistency assessment** — Evaluate pairwise compatibility between options across dimensions. Mark incompatible or conditional pairings with rationale. This typically eliminates the majority of theoretical combinations.
4. **Derive candidate solutions** — The remaining consistent combinations are viable options to evaluate. Select up to _`COUNT`_ of the most promising.

Present the decomposition to the user for validation. If a dimension has an obvious winner, resolve it immediately and focus research on contested dimensions.

If the decision is single-dimensional (e.g., "which database?"), skip decomposition and list options directly.

**1.3 Define Evaluation Criteria**

Present relevant criteria from list below, ask user to prioritize (1-10 scale):

**Technical Criteria:**
- Developer experience (learning curve, tooling, debugging)
- Maintainability (code clarity, refactoring ease, dependency burden)
- Performance (runtime speed, resource efficiency, scalability)
- Security (built-in features, vulnerability record, supply chain risk)
- Flexibility (extensibility, migration paths, vendor lock-in)
- Community & ecosystem (docs, libraries, hiring pool)

**Operational Criteria:**
- Deployment complexity (hosting options, CI/CD, rollback)
- Monitoring & observability (logging, metrics, debugging)
- Cost (infrastructure, services, licenses, scaling economics)
- Reliability (uptime, data durability, fault tolerance)

**Strategic Criteria:**
- Long-term viability (backing, roadmap, industry trends)
- Team alignment (existing skills, learning appetite)
- Time-to-market (implementation speed, productivity)
- Standards compliance (web standards, accessibility, frameworks)

**Gate**: User confirms options list + weighted criteria


### Phase 1.5: Generative Design Exploration _(optional)_

> **"Design It Twice"** — Instead of evaluating pre-defined options, first generate radically different designs by giving parallel agents contrasting constraints. The value is in contrast, not consensus.

**When to use**: Multi-dimensional decisions with contested design choices. **Skip** for single-option evaluations, well-understood technology choices, or when the design space has already been explored (e.g., via `andthen.trade-off` or `andthen.clarify`).

**1.5.1 Define Constraint Lenses**

Select 3+ contrasting architectural constraints from the decision context. Examples:
- "Minimize API surface area — fewest possible public methods/endpoints"
- "Maximize extensibility — plugin/adapter architecture for future needs"
- "Optimize for the common case — simplest possible happy path"
- "Ports-and-adapters — strict separation of domain from infrastructure"
- "Convention over configuration — zero-config defaults"

Each lens should produce a meaningfully different design — avoid lenses that would converge.

**1.5.2 Parallel Design Generation**

Spawn 3+ parallel sub-agents _(if supported by your coding agent; otherwise execute sequentially)_ using `andthen:solution-architect`, each with a different constraint:

```markdown
## Design Exploration: [TOPIC]

**Your constraint**: [Constraint lens — e.g., "Minimize API surface area"]

Design a solution for [TOPIC] that fully commits to this constraint.

Return:
1. **Interface sketch**: Key types, methods, endpoints, or components
2. **What it hides**: Complexity absorbed by the design
3. **What it exposes**: Decisions pushed to the consumer
4. **Trade-offs**: What you gain and what you sacrifice
5. **Best suited for**: Scenarios where this design excels
6. **Breaks down when**: Scenarios where this design fails
```

**1.5.3 Comparative Synthesis**

After all sub-agents return, synthesize findings **in prose, not tables**:
- Compare designs by discussing trade-offs between pairs
- Identify surprising convergences (where different constraints led to the same choice)
- Identify genuine tensions (where constraints force incompatible designs)
- Note which design dimensions are most sensitive to constraint choice

Present synthesis to user. The strongest candidates feed into Phase 2 as the options to evaluate systematically.

**Gate**: Design alternatives generated and synthesized → proceed to Phase 2 with refined options


### Phase 2: Parallel Deep Research (Use Sub-Agents)

For each option, launch a sub-agent _(if supported by your coding agent)_ with `andthen:solution-architect` to investigate, using this template:

**Research Template:**
```markdown
Research: [Option Name] for [TOPIC]

Evaluate against criteria:
- [List weighted criteria from Phase 1]

Required findings:
1. Core capabilities & limitations
2. Performance characteristics (benchmarks if available)
3. Integration requirements & dependencies
4. Total cost of ownership (infrastructure + operational)
5. Real-world examples (case studies, production usage)
6. Known issues, gotchas, edge cases
7. Migration complexity (from/to alternatives)
8. Community health (activity, support, roadmap)

Return:
- Score per criterion (1-10 + justification)
- Concrete evidence (links, benchmarks, examples)
- Critical warnings/limitations
```

Launch all research sub-agents _(if supported by your coding agent)_ using **parallel execution**.

**Gate**: All research completed


### Phase 3: Trade-off Analysis

**3.1 Create Comparison Matrix**

Build structured comparison across all options:

```markdown
## Trade-off Comparison: [TOPIC]

### Options Summary

**Option A: [Name]**
- Strengths: [Top 3 advantages]
- Weaknesses: [Top 3 limitations]
- Best for: [Ideal scenarios]
- Weighted score: [X.X]/10

**Option B: [Name]**
- [Same structure]

### Detailed Matrix

| Criterion (Weight) | Option A | Option B | Option C | Winner |
|-------------------|----------|----------|----------|---------|
| Performance (9) | 8/10 | 7/10 | 9/10 | C |
| DX (7) | 9/10 | 6/10 | 8/10 | A |
| Cost (8) | 6/10 | 9/10 | 7/10 | B |
| **Weighted Total** | **7.8** | **7.2** | **8.1** | **C** |

### Risk Analysis

**Option A Risks:**
- [Risk]: [Mitigation strategy]

**Option B Risks:**
- [Risk]: [Mitigation strategy]
```

**3.2 Identify Decision Factors**

Highlight:
- Clear winner (if exists) vs close competition
- Deal-breaking limitations for any option
- Context-dependent trade-offs
- Hybrid approaches (if applicable)


### Phase 4: Recommendation

**4.1 Evidence-Based Conclusion**

```markdown
## Recommendation: [TOPIC]

### Choice: [Option X]

**Rationale:**
- [Primary reason based on highest-weight criteria]
- [Supporting evidence from research]
- [Alignment with user constraints/goals]

**Implementation Path:**
1. [First step]
2. [Integration requirements]
3. [Validation approach]

**Risks & Mitigations:**
- [Risk 1]: [How to address]
- [Risk 2]: [How to address]

**Decision Confidence:** High | Medium | Low
- Why: [Explain confidence level]

**Alternatives Worth Considering:**
- [Option Y]: If [specific condition changes]
- [Option Z]: For [particular use case]
```

**4.2 User Review**

Present recommendation, ask:
- Does this align with your expectations?
- Any concerns about the choice?
- Need deeper analysis on any aspect?

**Gate**: User accepts recommendation or requests refinement


### Phase 5: Documentation

Store artifacts in OUTPUT_DIR/[topic-slug]/:

1. **design-tree.md**: Decision decomposition with dimensions, options, and pruning rationale (if multi-dimensional)
2. **research.md**: Consolidated findings from all options
3. **tradeoff-matrix.md**: Comparison matrix + risk analysis
4. **recommendation.md**: Final recommendation + implementation guidance

**Optional**: If decision is critical/complex, ask user if they want formal ADR created.


## Report

### Quality Checklist

Before completion:

**Completeness:**
- [ ] All options researched with evidence
- [ ] Criteria applied consistently
- [ ] Trade-offs clearly documented
- [ ] Risks identified with mitigations

**Quality:**
- [ ] Recommendations evidence-based, not opinion
- [ ] Real-world examples included
- [ ] No over-engineering or gold-plating
- [ ] Cost implications transparent

**Alignment:**
- [ ] Addresses user's core question
- [ ] Respects stated constraints
- [ ] Matches success criteria
- [ ] Team capabilities considered

### Output Structure

```bash
OUTPUT_DIR/
├── [topic-slug]/
│   ├── design-tree.md        # Decision decomposition (if multi-dimensional)
│   ├── research.md           # Consolidated research findings
│   ├── tradeoff-matrix.md    # Systematic comparison
│   └── recommendation.md     # Evidence-based conclusion
```


## Follow-Up Actions

After generating the reports/recommendations, offer:

**"Would you like me to create an ADR to formally document this decision? If you'd like any adjustments to the recommendation, let me know."**

**Handling User Response:**

1. **User accepts as-is** → Generate ADR using recommendation from Phase 4

2. **User requests adjustments** → Before generating ADR:
   - Acknowledge the requested changes
   - If user chooses different option: Update rationale to reflect their reasoning
   - If user modifies constraints/criteria: Adjust consequences section accordingly
   - If user wants hybrid approach: Document the combination and trade-offs
   - Incorporate user's additional context or business reasons into the ADR

3. **User declines** → Skip ADR creation, research artifacts remain available for future reference

### ADR Creation Template

Generate ADR using this template (incorporating any user adjustments):

```markdown
# ADR-[Number]: [Decision Title]

## Status
[Proposed | Accepted | Superseded]

## Context
[Background and requirements driving this decision - draw from TOPIC and Phase 1 scope]

## Decision
**We will use [recommended option] for [specific purpose].**

[Practical explanation of what this means]

## Consequences

### Positive
- [Key benefits from research findings]

### Negative
- [Trade-offs/limitations identified]

### Neutral
- [Implications neither good nor bad]

## Alternatives Considered

### [Alternative 1]
- **Pros**: [From trade-off matrix]
- **Cons**: [From trade-off matrix]
- **Rejected because**: [Specific reason from analysis]

[Repeat for each evaluated option]

## Implementation Notes
- [From recommendation.md implementation path]
- [Configuration requirements]
- [Integration considerations]

## References
- [Links to sources used in research]
- [Documentation, benchmarks, case studies cited]
```

**ADR Storage:**
- If project has existing ADRs: Place in same directory, follow existing numbering
- If no existing ADRs: Create `docs/adrs/` (or as configured in **Project Document Index**) and start with `ADR-001`
- Also keep copy in `OUTPUT_DIR/[topic-slug]/adr.md` for reference

**ADR Validation Checklist:**
- [ ] Actionable - provides clear implementation direction
- [ ] Justified - rationale is evidence-based (from research)
- [ ] Complete - all evaluated alternatives documented
- [ ] Traceable - links back to research artifacts
