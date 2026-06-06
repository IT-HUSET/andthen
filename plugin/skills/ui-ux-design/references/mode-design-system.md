# UI/UX – Design System Mode

Transform feature requirements into a focused design system with essential visual language, design tokens, component styles, and documentation.

**Platform-agnostic**: Design tokens and styles are the canonical reference for ALL platforms (web, mobile, desktop), adapted to each later.

**Inputs/destinations**: `REQUIREMENTS`, `CONCEPT_DIR`, `OUTPUT_DIR` are declared in SKILL.md `## VARIABLES > ### Mode Inputs` (each marked required, optional, or a default destination).

## Principles

- **Design system only** – no wireframes or page layouts (use the `wireframes` mode for that)
- **Start minimal** – essential tokens/components only; avoid premature complexity
- **Use CSS custom properties** – everything should be themeable; no hardcoded values in component styles

## Phase 1: Input Analysis

1. **Validate inputs**: verify `REQUIREMENTS` is provided – stop with a missing-input error if not. If `CONCEPT_DIR` is provided, verify it exists and catalog its contents (mockups, brand guidelines, existing design system).
2. **Extract requirements**: identify all UI components needed, key user actions and visual hierarchy, content types, brand/mood requirements, platform targets, and accessibility requirements.

**Gate**: Requirements understood, design inputs cataloged

## Phase 2: Design Research (Conditional)

Skip if `CONCEPT_DIR` contains sufficient design direction.

Using parallel sub-agents: research appropriate design patterns and UI conventions, accessibility-first patterns, similar products for inspiration (3-5), suitable foundation design systems or component libraries, and domain-specific best practices.

Save research to `<project_root>/.agent_temp/research/design/` only if substantial.

**Gate**: Design direction established

## Phase 3: Design Token Creation

Create essential design tokens. Tokens have two homes that must stay in sync: the **canonical** machine-readable source is the `DESIGN.md` front matter (Phase 5.1, agent- and tooling-consumable); `tokens.css` is the CSS-custom-property export for direct web consumption. The naming conventions below govern the CSS export.

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
- Choose typography with character when the brief warrants it – don't default to safe/generic

**Gate**: Core tokens defined

## Phase 4: Component Styles

From Phase 1 requirements, list only the components actually needed. Typical set: buttons (primary, secondary, states), form elements (input, select, textarea, checkbox, radio), cards/containers, navigation patterns, typography classes.

For each component: base styles using design tokens, variant styles, state styles (hover, focus, active, disabled), and responsive adjustments. Components should be minimal and composable.

**Gate**: Essential components styled

## Phase 5: Documentation & Showcase

**5.1 DESIGN.md** – Create `OUTPUT_DIR/DESIGN.md` in the DESIGN.md format: machine-readable YAML front matter followed by a human-readable markdown body. This is the canonical design-system artifact; `tokens.css` is its CSS export.

Front matter (delimited by `---` fences) – the canonical token source, keyed by category:
- `colors:` – role → CSS color value (hex/rgb/oklch)
- `typography:` – named text style → `family`, `size`, `weight`, `lineHeight`, `letterSpacing`
- `rounded:` – border-radius scale
- `spacing:` – spacing scale (8px base grid)
- `components:` – named UI element → token-referencing properties (`backgroundColor`, `textColor`, `padding`, `rounded`, …)

Markdown body – the canonical sections, in this order, including only those that apply: **Overview, Colors, Typography, Layout, Elevation & Depth, Shapes, Components, Do's and Don'ts**. Document rationale and application guidance (the *why* and *when*), not just values.

**5.2 Interactive Showcase** – Create `OUTPUT_DIR/showcase.html` demonstrating all color swatches with hex values, typography scale, spacing visualization, every component variant with live examples, interactive states, light/dark theme toggle (if applicable), and code snippets.

**Gate**: Documentation complete

## Phase 6: Validation

Verify against the Quality Checklist below; fix any failures.

**Gate**: Validation complete

## Output Layout

```
OUTPUT_DIR/
├── DESIGN.md           # Canonical design system: token front matter + rationale (DESIGN.md format)
├── tokens.css          # CSS custom properties – export of DESIGN.md tokens for direct web use
├── components.css      # Component styles
└── showcase.html       # Interactive component library
```

## Quality Checklist

- [ ] Tokens are consistent and minimal
- [ ] `DESIGN.md` front matter is valid (parseable YAML) and its tokens match `tokens.css`
- [ ] `DESIGN.md` body covers the applicable canonical sections with rationale, not just values
- [ ] Components use tokens (no hardcoded values)
- [ ] All required components from requirements are covered
- [ ] No unnecessary components or over-engineering
- [ ] Showcase demonstrates all variants and states
- [ ] Documentation is complete but concise
- [ ] Accessibility considerations addressed

Goal is a pragmatic, implementable design system – not perfection. Focus on what developers need to build the product.
