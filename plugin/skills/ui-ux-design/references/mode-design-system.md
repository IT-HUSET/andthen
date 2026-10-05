# UI/UX – Design System Mode

Turn feature requirements into a focused design system: essential visual language, design tokens, component styles, and documentation. Start minimal – essential tokens and components only, never premature complexity.

Bound from `ARGUMENTS`:

- `REQUIREMENTS` – required: an inline description, a file path, or a PRD reference.
- `CONCEPT_DIR` – optional: a concept design, mockups, or an existing design system.
- `OUTPUT_DIR` – the `Design System` document location (default `docs/design-system`).

## Workflow

### Phase 1: Input analysis

When `CONCEPT_DIR` is given, verify it exists and catalog its contents (mockups, brand guidelines, an existing design system).

Extract from `REQUIREMENTS` the components needed, the visual hierarchy, and the brand, platform, and accessibility requirements.

### Phase 2: Design research

Skip it when `CONCEPT_DIR` holds sufficient design direction. Otherwise research with parallel implementer subagents, each returning a findings summary per topic. Save the research to `<project_root>/.agent_temp/research/design/` only when it is substantial.

### Phase 3: Design tokens

Tokens have two homes that stay in sync. The **canonical**, machine-readable source is the `DESIGN.md` front matter (Phase 5), which agents and tooling consume; `tokens.css` is the CSS-custom-property export for direct web use. These naming conventions govern the CSS export:

- Colors: `--color-{role}[-{variant}]` (`--color-primary`, `--color-primary-dark`, `--color-gray-50` through `--color-gray-900`, `--color-success`, `--color-error`)
- Typography: `--font-{property}` and `--text-{size}` (`--font-sans`, `--font-normal: 400`, `--text-xs` through `--text-3xl`)
- Spacing: `--space-{n}` on an 8px base grid (`--space-1` through `--space-8`)
- Layout: `--container`, `--mobile: 640px`, `--tablet: 768px`, `--desktop: 1024px`
- Effects: `--shadow-{level}` (3 levels), `--radius[-{variant}]`, `--transition`

Give the system an intentional visual direction – typography with character, color with a dominant direction and clear accents – never generic AI aesthetics or default stacks. Semantic colors (success, error, warning) only when needed. Three shadow levels and three border-radius variants suffice for most projects.

### Phase 4: Component styles

From Phase 1's requirements, list only the components actually needed. Each component's base and variant styles reference design tokens, never hardcoded values; components stay minimal and composable.

**Gate**: no hardcoded value remains in `components.css`.

### Phase 5: Documentation and showcase

**`OUTPUT_DIR/DESIGN.md`**, in the DESIGN.md format: machine-readable YAML front matter, then a human-readable markdown body.

The front matter, delimited by `---` fences, is the canonical token source, keyed by category:

- `colors:` – role → CSS color value (hex, rgb, oklch)
- `typography:` – named text style → `family`, `size`, `weight`, `lineHeight`, `letterSpacing`
- `rounded:` – border-radius scale
- `spacing:` – spacing scale (8px base grid)
- `components:` – named UI element → token-referencing properties (`backgroundColor`, `textColor`, `padding`, `rounded`, …)

The markdown body holds the canonical sections that apply, in this order: **Overview, Colors, Typography, Layout, Elevation & Depth, Shapes, Components, Do's and Don'ts**. Document rationale and application guidance – the *why* and *when* – not just values.

**`OUTPUT_DIR/showcase.html`**, an interactive showcase: every color swatch with its hex value, the typography scale, a spacing visualization, every component variant with live examples, interactive states, a light/dark theme toggle where applicable, and code snippets.

**Gate**: every `tokens.css` property has its `DESIGN.md` front-matter value.

## Output

```
OUTPUT_DIR/
├── DESIGN.md           # Canonical design system: token front matter + rationale (DESIGN.md format)
├── tokens.css          # CSS custom properties – export of DESIGN.md tokens for direct web use
├── components.css      # Component styles
└── showcase.html       # Interactive component library
```
