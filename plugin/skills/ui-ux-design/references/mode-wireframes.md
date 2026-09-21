# UI/UX – Wireframes Mode

Transform feature requirements into simple HTML wireframes that capture key layout and interaction patterns for all pages/screens.

## Inputs

Bound from `ARGUMENTS`: `REQUIREMENTS` (required – inline description, file path, or PRD reference; absent, stop with a missing-input error), `DESIGN_DIR` (optional – design system directory or concept inputs, noted when it exists), `OUTPUT_DIR` (`docs/wireframes`, or the **Project Document Index** wireframes location).

## Principles

- **100% page coverage** – an un-wireframed page becomes an un-designed surface downstream, so every distinct page/state in the inventory gets its own wireframe

## Phase 1: Requirements Analysis

### 1.1 Create Page Inventory

Extract the comprehensive list of pages/screens from `REQUIREMENTS`, modal/overlay states (if complex enough to warrant separate wireframe) and error/empty/loading states (if distinct layouts needed) included.

Document in `OUTPUT_DIR/page-inventory.md`:
```markdown
# Page Inventory
## Pages to Wireframe
1. [page-name] - [brief description]
## Total: [N] wireframes required
```

### 1.2 Identify Key Patterns

From requirements, note: navigation structure, key content blocks and hierarchy, primary user actions and CTA placement, responsive requirements (mobile/tablet/desktop).

**Gate**: Complete page inventory created, patterns identified

## Phase 2: Wireframe Creation

### 2.1 Wireframe Principles

Create basic grayscale HTML layouts: major sections and placement, key containers (panels, cards), content blocks with realistic proportions, primary navigation, important CTAs. Boxes and placeholders only; layout and hierarchy over polish.

**HTML structure**: Use `system-ui` font, `#f5f5f5` background, white `.box` containers with `2px solid #ddd`, `.placeholder` divs with `#e0e0e0` background and `2px dashed #999`, `.btn` in `#666`, CSS grid/flex for layout, and a `@media (max-width: 768px)` breakpoint. Include `<!DOCTYPE html>`, a `viewport` meta tag, and the CSS inline in `<style>`.

### 2.2 Parallel Wireframe Creation

Fan out one subagent per inventory page, concurrently – the pages are independent. Each is a plain subagent, not a re-entry into this mode: given 2.1's HTML structure verbatim, its `OUTPUT_DIR/[page-name].html` target, the page name and purpose, key content/sections, navigation context, and responsive requirements, it writes that one page's HTML and returns the path. A child re-entering the mode would rebuild the inventory and re-run validation once per page.

**Naming convention**: `[page-name].html` (e.g., `home.html`, `dashboard.html`, `user-profile.html`)

### 2.3 Completeness Verification

Cross-check against Phase 1 inventory: every page has a corresponding wireframe, none skipped because it seems "similar" to another.

**Gate**: All pages from inventory have wireframes

## Phase 3: Validation

### 3.1 Visual Validation

Browser automation is the gate: when the subagent below reports that nothing available can set viewports, capture full-page screenshots, inspect DOM geometry, and read console and network failures, stop with `BLOCKED: wireframe validation requires browser automation` – a manually opened browser does not satisfy it.

Spawn a fresh subagent that invokes the `andthen:visual-validation` skill over every wireframe page at four viewports:

- Mobile 375×667
- Tablet 768×1024
- Desktop 1280×800
- Wide 1920×1080

Ask it to check horizontal overflow, overlapping elements, collapsed containers, responsive reflow (grids, flex, touch targets ≥44px on mobile), and console errors and 404s, and to judge information hierarchy, content organization, user-flow representation, and missing UI states.

Full-page screenshots land at `OUTPUT_DIR/screenshots/[page]-[viewport].png`, overriding its default capture directory, and the report at `OUTPUT_DIR/validation-report.md`, pass/fail per page and viewport.

### 3.2 Refinement

Fix hidden or overlapping content, missing navigation, and horizontal scroll on mobile before anything else, by adjusting CSS (gap, overflow, min-height, breakpoint rules); note spacing and decorative overlap and continue. Improve unclear sections, add missing elements, ensure consistency.

**Gate**: the validation report passes every page and viewport

## Phase 4: Documentation

Mark all wireframes as complete in `OUTPUT_DIR/page-inventory.md`, and create `OUTPUT_DIR/index.html` as a navigation hub: a grid of all wireframes with iframes previewing each page, title, brief description, and a link to the wireframe file.

**Gate**: Documentation complete

## Output Layout

```
OUTPUT_DIR/
├── index.html              # Navigation hub for all wireframes
├── page-inventory.md       # Checklist of all pages
├── home.html               # Individual wireframes...
├── dashboard.html
├── [page-name].html
├── screenshots/            # Visual validation captures
│   ├── home-mobile.png
│   ├── home-desktop.png
│   └── ...
└── validation-report.md    # Automated validation results
```
