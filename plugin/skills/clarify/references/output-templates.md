# Clarify Output Templates

Output-contract templates for the `andthen:clarify` skill. Every section heading is part of the document contract – preserve them as-is.

## Feature mode template

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
- [Explicit non-goal or deferred item] – [why it is out of scope now]

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

## Product mode template

```markdown
# Product Vision: [Product Name]

## Vision
[One paragraph: what this product is, why it exists, the change it makes for users]

## Problem Statement
[The user/market problem being solved; current pain; alternatives users use today]

## Target Users & Personas
- **[Persona]** – [role, context, jobs-to-be-done]

## Value Propositions
- [Promised user/business outcome – specific, testable]

## Product Principles
- [Design-decision tiebreakers – e.g. "favor depth over breadth"]

## Anti-Goals
- [Explicit non-goals – what this product is NOT, and why]

## Success Metrics
### North Star
- [Single metric tied to value delivered]
### Leading Indicators
- [Earlier signals that predict the north star]

## Strategic Constraints
- **Business**: [budget, timeline, partnerships]
- **Regulatory**: [compliance, data residency]
- **Technical**: [non-negotiable platform / integration constraints]

## Roadmap Themes
<!-- Themes, not features. Features are decided downstream in andthen:prd. -->
- **[Theme]** – [what this theme unlocks, when it matters]

## Open Questions
- [Strategic ambiguities deferred to future product clarification rounds]

## Decisions Log
| Decision | Rationale | Date |
```
