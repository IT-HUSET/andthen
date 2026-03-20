---
description: Creates a pragmatic design system/style guide from feature requirements and optional concept design inputs
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

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails**
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Favor simplicity** - recommend simplest solution (KISS, YAGNI, DRY)
- **Design system only** - No wireframes or page layouts (use `andthen:wireframes` skill for that)
- **Delegate to sub-agents** _(if supported by your coding agent)_ for research and review tasks


## GOTCHAS
- Creating too many tokens/components — start minimal, essential only
- Not using CSS custom properties — everything should be themeable


## WORKFLOW

### Phase 1: Input Analysis

#### 1.1 Validate Inputs
- Verify _`REQUIREMENTS`_ is provided - if not, **STOP** and ask user
- If _`CONCEPT_DIR`_ provided, verify it exists and catalog contents:
  - Concept designs / mockups / inspiration images
  - Existing design system files or references
  - Brand guidelines or constraints

#### 1.2 Extract Requirements
From _`REQUIREMENTS`_, identify:
- **All UI components** needed (buttons, forms, cards, navigation, etc.)
- **Key user actions** and their visual hierarchy
- **Content types** to display
- **Brand/mood requirements** (professional, playful, minimal, etc.)
- **Platform targets** (web, mobile, desktop)
- **Accessibility requirements**

- **Read additional guidelines and documentation** - Read additional relevant guidelines and documentation (API, guides, reference, etc.) as needed

**Gate**: Requirements understood, design inputs cataloged


### Phase 2: Design Research (Conditional)

**Skip this phase** if _`CONCEPT_DIR`_ contains sufficient design direction.


#### 2.1 Research Execution (Parallel Agents)
- Analyze requirements for design implications
- Identify appropriate design patterns and UI conventions
- Research accessibility-first design patterns
- Search for 3-5 similar products for inspiration
- Identify suitable foundation design systems and/or component libraries
- Research best practices for the specific domain

_If available, delegate using **parallel sub-agents** _(if supported by your coding agent; otherwise execute sequentially)_ - multiple Task calls in one message._

#### 2.2 Document Findings
Save research to _`<project_root>/.agent_temp/research/design/`_ only if substantial.


**Gate**: Design direction established


### Phase 3: Design Token Creation

Create essential design tokens only - avoid premature complexity.

#### 3.1 Color System
Define only what's needed:
```css
/* Primary - Main brand color with variants */
--color-primary: #...;
--color-primary-dark: #...;
--color-primary-light: #...;

/* Neutrals - Grayscale for text and borders */
--color-white: #...;
--color-gray-50 through --color-gray-900: #...;
--color-black: #...;

/* Semantic - Only if needed */
--color-success: #...;
--color-error: #...;
--color-warning: #...;
```

#### 3.2 Typography
Use system fonts unless brand requires otherwise:
```css
/* Font Stack */
--font-sans: system-ui, -apple-system, sans-serif;

/* Sizes - Only what you need */
--text-xs through --text-3xl: ...;

/* Weights */
--font-normal: 400;
--font-medium: 500;
--font-bold: 700;
```

#### 3.3 Spacing & Layout
Simple base grid:
```css
/* Spacing - 8px base */
--space-1 through --space-8: ...;

/* Container & Breakpoints */
--container: 1200px;
--mobile: 640px;
--tablet: 768px;
--desktop: 1024px;
```

#### 3.4 Effects
Minimal set:
```css
/* Shadows - Just 3 levels */
--shadow-sm, --shadow-md, --shadow-lg: ...;

/* Border Radius */
--radius, --radius-lg, --radius-full: ...;

/* Transition */
--transition: all 150ms ease;
```

**Gate**: Core tokens defined


### Phase 4: Component Styles

#### 4.1 Identify Essential Components
From Phase 1 requirements, list components actually needed. Typical set:
- Buttons (primary, secondary, states)
- Form elements (input, select, textarea, checkbox, radio)
- Cards/containers
- Navigation patterns
- Typography classes

#### 4.2 Create Component CSS
For each component:
- Base styles using design tokens
- Variant styles (primary, secondary, etc.)
- State styles (hover, focus, active, disabled)
- Responsive adjustments

**Principle**: Components should be minimal and composable.

**Gate**: Essential components styled


### Phase 5: Documentation & Showcase

#### 5.1 Style Guide Document
Create _`OUTPUT_DIR/style-guide.md`_:
```markdown
# [Project] Design System

## Colors
- Primary: [hex]
- Grays: [range]
- Semantic: [if used]

## Typography
- Font: [stack]
- Sizes: [scale]
- Weights: [values]

## Spacing
- Base unit: 8px
- Scale: [values]

## Components
- [List with usage notes]

## Breakpoints
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px
```

#### 5.2 Interactive Showcase
Create _`OUTPUT_DIR/showcase.html`_ demonstrating:
- All color swatches with hex values
- Typography scale with specifications
- Spacing system visualization
- Every component variant with live examples
- Interactive states (buttons, forms)
- Light/dark theme toggle (if applicable)
- Code snippets for implementation

**Gate**: Documentation complete


### Phase 6: Validation

#### 6.1 Self-Review
Review your work for:
- Design consistency across tokens and components
- Accessibility compliance (contrast ratios, focus states)
- CSS quality and organization
- Redundancy or over-engineering
- Token usage consistency (no hardcoded values)

_If available, delegate using **parallel sub-agents** _(if supported by your coding agent; otherwise execute sequentially)_ - multiple Task calls in one message._

#### 6.2 Refinement
Address any issues found:
- Remove unnecessary complexity
- Fix inconsistencies
- Ensure all tokens are actually used

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
