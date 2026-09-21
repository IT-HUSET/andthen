# Product Mode Output Template

The `andthen:clarify` skill's product-scope **output** contract. Every section heading is contract – preserve verbatim.

```markdown
# Product Vision: [Product Name]

> **Source**: [stable source identity: resolved path, full URL, or inline digest]

## Vision
[One paragraph: what it is, why it exists, the change it makes for users]

## Problem Statement
[The user/market problem; current pain; today's alternatives]

## Target Users & Personas
- **[Persona]** – [role, context, jobs-to-be-done]

## Value Propositions
- [Promised user/business outcome – specific, testable]

## Product Principles
- [Design-decision tiebreaker – e.g. "favor depth over breadth"]

## Non-Goals
- [What this product is NOT, and why]

## Proportionality
<!-- Facts, not philosophy – preserve any answers init already wrote; `unknown` beats an empty line. -->
- **Stage**: prototype | internal | production
- **Scale**: [users] · [data volume] · [deploy topology] · [maintainers]
- **Standing technical non-goals**: [what this project will not grow]

## Success Metrics
### North Star
- [Single metric tied to value delivered]
### Leading Indicators
- [Earlier signals predicting the north star]

## Strategic Constraints
- **Business**: [budget, timeline, partnerships]
- **Regulatory**: [compliance, data residency]
- **Technical**: [non-negotiable platform / integration limits]

## Roadmap Themes
<!-- Themes, not features; features are decided downstream in a feature-scope PRD. -->
- **[Theme]** – [what it unlocks, when it matters]

## Open Questions
- [Strategic question precise enough to be closed as written]
- Area to revisit: [area not yet stateable as a question] – [what would sharpen it]

## Decisions Log
| Decision | Rationale | Date |
```
