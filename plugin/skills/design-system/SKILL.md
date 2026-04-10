---
description: Create a pragmatic design system/style guide from feature requirements and optional concept design inputs
argument-hint: "[Feature requirements - inline, file path, or PRD reference] [Optional - concept design directory]"
---

# Create Design System / Style Guide


Transform feature requirements into a focused design system with essential visual language, design tokens, component styles, and documentation.

**Platform-Agnostic**: Design tokens and styles serve as the canonical reference for ALL platforms (web, mobile, desktop). They will be adapted to platform-specific implementations later.


## VARIABLES

REQUIREMENTS: $1 (feature requirements - inline description, file path, or PRD reference)
CONCEPT_DIR: $2 (optional - directory with concept design, mockups, or existing design system)
OUTPUT_DIR: ${3:-docs/design-system} _(or as configured in **Project Document Index**)_


## INSTRUCTIONS

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work
- **Favor simplicity** - recommend simplest solution (KISS, YAGNI, DRY)
- **Design system only** - No wireframes or page layouts (use `andthen:wireframes` skill for that)
- **Delegate to sub-agents** _(if supported by your coding agent)_ for research and review tasks


## GOTCHAS
- Creating too many tokens/components – start minimal, essential only
- Not using CSS custom properties – everything should be themeable


## WORKFLOW

### Phase 1: Input Analysis

**1.1 Validate Inputs**
- Verify _`REQUIREMENTS`_ is provided - if not, **STOP** and ask user
- If _`CONCEPT_DIR`_ provided, verify it exists and catalog contents (mockups, brand guidelines, existing design system)

**1.2 Extract Requirements**
From _`REQUIREMENTS`_, identify: all UI components needed, key user actions and visual hierarchy, content types, brand/mood requirements, platform targets, and accessibility requirements.

**Gate**: Requirements understood, design inputs cataloged


### Phase 2: Design Research (Conditional)

**Skip this phase** if _`CONCEPT_DIR`_ contains sufficient design direction.

Using parallel sub-agents _(if supported; otherwise sequential)_: research appropriate design patterns and UI conventions, accessibility-first patterns, similar products for inspiration (3-5), suitable foundation design systems or component libraries, and domain-specific best practices.

Save research to _`<project_root>/.agent_temp/research/design/`_ only if substantial.

**Gate**: Design direction established


### Phase 3: Design Token Creation

Create essential design tokens using CSS custom properties – start minimal, avoid premature complexity.

**Naming conventions:**
- Colors: `--color-{role}[-{variant}]` (e.g. `--color-primary`, `--color-primary-dark`, `--color-gray-50` through `--color-gray-900`, `--color-success`, `--color-error`)
- Typography: `--font-{property}` and `--text-{size}` (e.g. `--font-sans`, `--font-normal: 400`, `--text-xs` through `--text-3xl`)
- Spacing: `--space-{n}` on an 8px base grid (e.g. `--space-1` through `--space-8`)
- Layout: `--container`, `--mobile: 640px`, `--tablet: 768px`, `--desktop: 1024px`
- Effects: `--shadow-{level}` (3 levels), `--radius[-{variant}]`, `--transition`

**Principles:**
- Use system fonts unless brand requires otherwise
- Define semantic colors (success, error, warning) only if needed
- 3 shadow levels and 3 border radius variants are sufficient for most projects

**Gate**: Core tokens defined


### Phase 4: Component Styles

From Phase 1 requirements, list only the components actually needed. Typical set: buttons (primary, secondary, states), form elements (input, select, textarea, checkbox, radio), cards/containers, navigation patterns, typography classes.

For each component: base styles using design tokens, variant styles, state styles (hover, focus, active, disabled), and responsive adjustments. Components should be minimal and composable.

**Gate**: Essential components styled


### Phase 5: Documentation & Showcase

**5.1 Style Guide** – Create _`OUTPUT_DIR/style-guide.md`_ documenting colors, typography, spacing, components (with usage notes), and breakpoints.

**5.2 Interactive Showcase** – Create _`OUTPUT_DIR/showcase.html`_ demonstrating all color swatches with hex values, typography scale, spacing visualization, every component variant with live examples, interactive states, light/dark theme toggle (if applicable), and code snippets.

**Gate**: Documentation complete


### Phase 6: Validation

Review for: design consistency across tokens and components, accessibility compliance (contrast ratios, focus states), CSS quality, redundancy or over-engineering, and token usage consistency (no hardcoded values). Fix any issues found.

**Gate**: Validation complete


## OUTPUT

```
OUTPUT_DIR/
├── tokens.css          # Design tokens (CSS custom properties)
├── components.css      # Component styles
├── style-guide.md      # Documentation
└── showcase.html       # Interactive component library
```


## QUALITY CHECKLIST

- [ ] Tokens are consistent and minimal
- [ ] Components use tokens (no hardcoded values)
- [ ] All required components from requirements are covered
- [ ] No unnecessary components or over-engineering
- [ ] Showcase demonstrates all variants and states
- [ ] Documentation is complete but concise
- [ ] Accessibility considerations addressed


**Remember**: Goal is a pragmatic, implementable design system - not perfection. Focus on what developers need to build the product.
