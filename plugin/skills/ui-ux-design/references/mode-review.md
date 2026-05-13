# UI/UX – Review Mode

Validate an existing UI implementation – capture states, assess quality against intended design and UX principles, and report issues with evidence and fix recommendations.

## Inputs

- implementation URL, running app, or screenshots
- intended design reference (wireframes, design system, mockups) – optional but strengthens the review
- scope (which screens, which states, which breakpoints)

## Process

### 1. Scope & Setup

Define the screens, states, breakpoints, and platforms that matter. Identify design references. Choose the available capture and comparison tools.

### 2. Capture

Capture the states users actually depend on, not just the default view:
- default / loaded / empty / loading / error
- hover / focus / active where relevant
- each target breakpoint

For visual capture and pixel-level regression checks, invoke the `andthen:visual-validation` skill in a sub-agent. Use the semantic review process below as the primary assessment.

### 3. Semantic Review

Assess each captured state against:

**Visual & Layout**
- hierarchy is obvious
- spacing and alignment are consistent
- text is readable and not truncated
- contrast is sufficient
- layout survives target breakpoints and safe areas

**Usability**
- primary actions are obvious quickly
- key flows are short and low-friction
- touch targets and focus states are usable
- error prevention and recovery are present
- the interface responds clearly to user actions

### 4. Issue Classification

- **Immediate (P1)**: blocks task completion, breaks layout, or creates critical accessibility failures
- **High Priority (P2)**: harms hierarchy, task flow, responsiveness, or feedback
- **Enhancement (P3)**: polish, refinement, or optional depth

### 5. Fix Recommendations

Recommend specific changes: exact components, styles, spacing, typography, states, or layout behavior. Tie each recommendation to a principle or a reference (design system token, wireframe layout, accessibility guideline).

## Output

Return:
- **Validation scope** – screens/states/breakpoints reviewed
- **Overall quality assessment** – one paragraph
- **Prioritized issues** – P1/P2/P3, each with evidence (screenshot or description) and a recommended fix
- **Next steps** – remaining gaps or retest needs
