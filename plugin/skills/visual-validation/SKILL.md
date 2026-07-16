---
description: Validate UI screenshots and run visual regression checks against wireframes/design specs. Full browser journeys belong to the andthen:e2e-test skill; design-system/wireframe authoring to the andthen:ui-ux-design skill. Trigger on 'visual validation', 'check UI against design', 'visual regression'.
argument-hint: "[<screens-or-states-to-validate>] [design-reference/baseline]"
user-invocable: true
---

# Visual Validation

## VARIABLES

SCOPE: $ARGUMENTS (screens, states, URLs, screenshots, wireframes, baselines, or design requirements to validate)


## INSTRUCTIONS

- Read project rules and guidelines (`CLAUDE.md` / `AGENTS.md` and referenced files) before starting – including any UI guidelines.
- Check for a `Visual Validation Workflow` section in `CLAUDE.md` / `AGENTS.md` first (at any heading level). If one exists, follow it as the primary workflow.
- Use the fallback workflow below only when no project-specific workflow is defined.
- Choose tools already available in the project environment before introducing new ones.
- Validate the states users depend on, not only the default state.


## Fallback Workflow

### Phase 1: Setup & Inventory

1. Define the screens, states, breakpoints, and platforms that matter.
2. Identify baselines, wireframes, design references, or acceptance criteria – consult the `Wireframes` and `Design System` documents (see **Project Document Index**) when the project specifies non-default locations.
3. Choose available capture and comparison tools.
4. Build a short validation checklist before collecting evidence.

### Phase 2: Capture Screenshots

- Use consistent names such as `{screen}-{state}.png`.
- Store captures in `.agent_temp/validation/`.
- Capture meaningful states: default, loading, empty, error, hover/focus/active, modal/overlay, and target breakpoints where relevant.

### Phase 3: Comparison

Primary review is semantic: layout, hierarchy, typography/readability, spacing, color/contrast, component presence and state treatment, responsive behavior, touch-target size, overlays/modals/focus states, and accessibility-relevant affordances.

Use pixel comparison when trustworthy baselines exist. Treat pixel diffs as evidence, not judgment; validate whether the diff matters to user intent.

### Phase 4: Issue Documentation

Classify findings:

- **P1 Critical**: breaks intent, blocks use, hides content, or creates a critical accessibility failure
- **P2 Major**: missing behavior, missing elements, visibly wrong implementation, or broken responsive behavior
- **P3 Minor**: polish, small alignment/spacing issues, or low-risk refinement

### Phase 5: Fix Recommendations

Recommend specific changes: exact components, styles, spacing, typography, states, or layout behavior. Tie each recommendation to evidence from the capture or design reference.


## GOTCHAS

1. Comparing against the wrong reference.
2. Reporting vague findings without a concrete, evidenced fix.


## Output Format

Return:

- **Summary**: overall status, screens/states covered, workflow used
- **Detailed Findings**: per screen/state with evidence and severity
- **Recommended Fixes**: specific changes in priority order
- **Next Steps**: remaining gaps or retest needs
