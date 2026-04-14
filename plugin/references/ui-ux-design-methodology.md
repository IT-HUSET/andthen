# UI/UX Design Methodology

Core approach for UI/UX design, visual direction, and implementation validation. Aim for deliberate, coherent design rather than safe generic output.

## Operating Modes

**Research Mode**: understand users, flows, pain points, and business constraints.

**Strategy Mode**: define information architecture, primary journeys, and what the interface must make easy.

**Visual Design Mode**: commit to a clear aesthetic direction and execute it consistently.

- avoid generic AI aesthetics and default stacks
- choose typography with character
- use color intentionally, with a dominant direction and clear accents
- build atmosphere with depth, layering, gradients, texture, or pattern when appropriate
- use motion sparingly but purposefully
- match implementation complexity to the chosen visual ambition

**Validation & Review Mode**: capture states, assess quality, and report issues with evidence.

## Issue Classification

- **Immediate**: blocks task completion, breaks layout, or creates critical accessibility failures
- **High Priority**: harms hierarchy, task flow, responsiveness, or feedback
- **Enhancement**: polish, refinement, or optional depth

## Quality Checklist

### Visual & Layout
- hierarchy is obvious
- spacing and alignment are consistent
- text is readable and not truncated
- contrast is sufficient
- layout survives target breakpoints and safe areas

### Usability
- primary actions are obvious quickly
- key flows are short and low-friction
- touch targets and focus states are usable
- error prevention and recovery are present
- the interface responds clearly to user actions

## Design Reference Sources

Use project guidance first. External references are optional and should support a concrete direction, not replace judgment.

Good sources are:
- high-quality pattern libraries
- product references close to the target domain
- established UX principles and accessibility guidance

## Design Tokens Pattern

When creating a design system or implementation-ready handoff, define the small token set that drives consistency:

```css
--primary: #[hex];
--secondary: #[hex];
--spacing-unit: 8px;
--border-radius: 12px;
```

## Output Formats

### Creating Designs
1. Design brief
2. Research insights
3. Design solution: IA, flows, visual direction, states, accessibility
4. Implementation package: tokens, measurements, interactions, key states

### Reviewing/Validating Implementations
- validation scope
- overall quality assessment
- prioritized issues with evidence
- recommended fixes and next steps
