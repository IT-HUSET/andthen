# UI/UX — Design System Mode

Transform feature requirements into a focused design system with essential visual language, design tokens, component styles, and documentation.

**Platform-agnostic**: Design tokens and styles serve as the canonical reference for ALL platforms (web, mobile, desktop). They will be adapted to platform-specific implementations later.

## Variables

- **REQUIREMENTS**: feature requirements — inline description, file path, or PRD reference (required)
- **CONCEPT_DIR**: optional — directory with concept design, mockups, or existing design system
- **OUTPUT_DIR**: defaults to `docs/design-system` or as configured in the **Project Document Index**

## Principles

- **Design system only** — no wireframes or page layouts (use the `wireframes` mode for that)
- **Start minimal** — essential tokens/components only; avoid premature complexity
- **Use CSS custom properties** — everything should be themeable; no hardcoded values in component styles

## Phase 1: Input Analysis

1. **Validate inputs**: verify `REQUIREMENTS` is provided — stop with a missing-input error if not. If `CONCEPT_DIR` is provided, verify it exists and catalog its contents (mockups, brand guidelines, existing design system).
2. **Extract requirements**: identify all UI components needed, key user actions and visual hierarchy, content types, brand/mood requirements, platform targets, and accessibility requirements.

**Gate**: Requirements understood, design inputs cataloged

## Phase 2: Design Research (Conditional)

Skip if `CONCEPT_DIR` contains sufficient design direction.

Using parallel sub-agents: research appropriate design patterns and UI conventions, accessibility-first patterns, similar products for inspiration (3-5), suitable foundation design systems or component libraries, and domain-specific best practices.

Save research to `<project_root>/.agent_temp/research/design/` only if substantial.

**Gate**: Design direction established

## Phase 3: Design Token Creation

Create essential design tokens using CSS custom properties — start minimal, avoid premature complexity.

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
- Choose typography with character when the brief warrants it — don't default to safe/generic

**Gate**: Core tokens defined

## Phase 4: Component Styles

From Phase 1 requirements, list only the components actually needed. Typical set: buttons (primary, secondary, states), form elements (input, select, textarea, checkbox, radio), cards/containers, navigation patterns, typography classes.

For each component: base styles using design tokens, variant styles, state styles (hover, focus, active, disabled), and responsive adjustments. Components should be minimal and composable.

**Gate**: Essential components styled

## Phase 5: Documentation & Showcase

**5.1 Style Guide** — Create `OUTPUT_DIR/style-guide.md` documenting colors, typography, spacing, components (with usage notes), and breakpoints.

**5.2 Interactive Showcase** — Create `OUTPUT_DIR/showcase.html` demonstrating all color swatches with hex values, typography scale, spacing visualization, every component variant with live examples, interactive states, light/dark theme toggle (if applicable), and code snippets.

**Gate**: Documentation complete

## Phase 6: Validation

Review for: design consistency across tokens and components, accessibility compliance (contrast ratios, focus states), CSS quality, redundancy or over-engineering, and token usage consistency (no hardcoded values). Fix any issues found.

**Gate**: Validation complete

## Output Layout

```
OUTPUT_DIR/
├── tokens.css          # Design tokens (CSS custom properties)
├── components.css      # Component styles
├── style-guide.md      # Documentation
└── showcase.html       # Interactive component library
```

## Quality Checklist

- [ ] Tokens are consistent and minimal
- [ ] Components use tokens (no hardcoded values)
- [ ] All required components from requirements are covered
- [ ] No unnecessary components or over-engineering
- [ ] Showcase demonstrates all variants and states
- [ ] Documentation is complete but concise
- [ ] Accessibility considerations addressed

Goal is a pragmatic, implementable design system — not perfection. Focus on what developers need to build the product.
