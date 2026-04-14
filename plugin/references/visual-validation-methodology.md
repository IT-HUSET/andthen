# Visual Validation Methodology

Fallback workflow for visual validation when the project does not define its own. Use it to capture the right states, compare them against the intended design, and report issues precisely.

## Workflow Selection

Check CLAUDE.md first for a project-specific visual validation workflow. If one exists, follow it. Use this file only as the fallback.

## Fallback Workflow

### Phase 1: Setup & Inventory
1. Define the screens, states, breakpoints, and platforms that matter.
2. Identify baselines or design references.
3. Choose the available capture and comparison tools.
4. Build a short validation checklist before collecting evidence.

### Phase 2: Capture Screenshots
- use consistent names such as `{screen}-{state}.png`
- store captures in `.agent_temp/validation/`
- capture the states users actually depend on, not just the default view

### Phase 3: Comparison
**Primary**: semantic review against the intended layout, hierarchy, typography, spacing, color, and states.

**Secondary**: pixel comparison when trustworthy baselines exist.

### Phase 4: Issue Documentation
Classify findings:
- **P1 Critical**: breaks intent or blocks use
- **P2 Major**: missing behavior, missing elements, or visibly wrong implementation
- **P3 Minor**: polish or small alignment/spacing issues

### Phase 5: Fix Recommendations
Recommend specific changes: exact components, styles, spacing, typography, states, or layout behavior.

## Core Validation Checks

For each screen, check:
- layout and hierarchy
- typography and readability
- color and contrast
- component presence and state treatment
- responsiveness across target sizes
- touch target size where relevant

## Tool Awareness

Use the tools already available in the project environment. Common categories:
- browser automation/screenshot tools
- native simulator screenshot tools
- image diff tools
- browser/device inspection tools

Check CLAUDE.md for project-preferred tooling before choosing your own.

## Common Pitfalls

1. validating only the default state
2. comparing against the wrong reference
3. missing overlays, modals, or transient UI
4. reporting vague issues without concrete fixes
5. ignoring the project-specific workflow when one exists

## Output Format

Return:
- **Summary**: overall status, screens/states covered, workflow used
- **Detailed Findings**: per screen/state with evidence and severity
- **Recommended Fixes**: specific changes in priority order
- **Next Steps**: remaining gaps or retest needs
