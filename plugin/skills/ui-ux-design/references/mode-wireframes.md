# UI/UX – Wireframes Mode

Transform feature requirements into simple HTML wireframes that capture key layout and interaction patterns for all pages/screens.

**Platform-agnostic**: HTML/CSS is used as the universal design language for ALL projects (web, mobile, desktop). Wireframes serve as the canonical design reference that will be adapted to platform-specific implementations later.

**Inputs/destinations**: `REQUIREMENTS`, `DESIGN_DIR`, `OUTPUT_DIR` are declared in SKILL.md `## VARIABLES > ### Mode Inputs` (with per-token binding type – required input, optional contextual input, or default destination).

## Principles

- **Wireframes only** – no design system creation (use the `design-system` mode for that)
- **Simple, grayscale layouts** – focus on structure, not visual polish
- **100% page coverage** – every page/screen in requirements MUST have a wireframe
- **Delegate to sub-agents** for parallel wireframe creation
- **Browser automation required** for visual validation (Playwright MCP or Chrome DevTools MCP; falls back to manual if unavailable)

## Phase 1: Requirements Analysis

### 1.1 Validate Inputs
- Verify `REQUIREMENTS` is provided – stop with a missing-input error if not
- If `DESIGN_DIR` provided, verify it exists and note available design assets

### 1.2 Create Page Inventory

**CRITICAL**: Extract comprehensive list of ALL pages/screens from `REQUIREMENTS`:
- Main pages (home, dashboard, settings, etc.)
- Sub-pages and detail views
- Modal/overlay states (if complex enough to warrant separate wireframe)
- Error/empty/loading states (if distinct layouts needed)

Document in `OUTPUT_DIR/page-inventory.md`:
```markdown
# Page Inventory
## Pages to Wireframe
1. [page-name] - [brief description]
## Total: [N] wireframes required
```

### 1.3 Identify Key Patterns

From requirements, note: navigation structure, key content blocks and hierarchy, primary user actions and CTA placement, responsive requirements (mobile/tablet/desktop).

**Gate**: Complete page inventory created, patterns identified

## Phase 2: Wireframe Creation

### 2.1 Wireframe Principles

Create basic, grayscale HTML layouts showing major sections and placement, key containers (panels, cards), content blocks with realistic proportions, primary navigation, and important CTAs. Use boxes and placeholders, grayscale only, focus on layout and information hierarchy.

**HTML structure**: Use `system-ui` font, `#f5f5f5` background, white `.box` containers with `2px solid #ddd`, `.placeholder` divs with `#e0e0e0` background and `2px dashed #999`, `.btn` in `#666`, CSS grid/flex for layout, and a `@media (max-width: 768px)` breakpoint. Include `<!DOCTYPE html>`, a `viewport` meta tag, and the CSS inline in `<style>`.

### 2.2 Common Patterns

- **Nav**: flex row with logo placeholder + nav items justified space-between
- **Hero**: two-column grid with headline/CTA text and image placeholder
- **Content grid**: `auto-fit, minmax(250px, 1fr)` grid of cards with image + text

### 2.3 Parallel Wireframe Creation

**CRITICAL**: Create wireframes in parallel for efficiency.

For each page in the inventory, spawn a sub-agent and have it run this skill with `--mode wireframes` scoped to a single page, given:
- Reference to base HTML template (the structure from 2.1), page name and purpose, key content/sections, navigation context, responsive requirements

**Execute multiple agents simultaneously** – each handles a single page.

**Naming convention**: `[page-name].html` (e.g., `home.html`, `dashboard.html`, `user-profile.html`)

### 2.4 Completeness Verification

Cross-check against Phase 1 inventory. Verify EVERY page has a corresponding wireframe. No page skipped because it seems "similar" to another – every distinct page/state in the inventory must have its own file.

**Gate**: All pages from inventory have wireframes

## Phase 3: Validation

### 3.1 Browser-Based Visual Validation

**CRITICAL**: Use browser automation (Playwright MCP or Chrome DevTools MCP) to capture and validate wireframes across viewports.

**MCP Server Detection** (in order of preference):
1. **Playwright MCP** (`mcp__playwright__*` tools) – preferred
2. **Chrome DevTools MCP** (`mcp__chrome-devtools__*` tools) – fallback
3. **Manual validation** – if no MCP available, invoke the `andthen:visual-validation` skill in a sub-agent with a manually opened browser

**Viewport Matrix:**
| Device | Width | Height |
|--------|-------|--------|
| Mobile | 375px | 667px |
| Tablet | 768px | 1024px |
| Desktop | 1280px | 800px |
| Wide | 1920px | 1080px |

For each wireframe: navigate to it, set each viewport, capture full-page screenshot to `OUTPUT_DIR/screenshots/[page]-[viewport].png`.

**Checks to run:**
- No horizontal overflow (scroll width ≤ viewport width)
- No overlapping elements (check bounding boxes)
- No collapsed/zero-height containers that should have content
- Responsive reflow at breakpoints (grids, flex, touch targets ≥44px on mobile)
- No console errors or 404s

**Issue severity**: Critical (hidden/invisible content, overlapping text/buttons, missing navigation) – fix before proceeding. High (horizontal scroll on mobile) – fix before review. Medium/Low (spacing, decorative overlap) – note and continue.

Fix issues by adjusting CSS (gap, overflow, min-height, breakpoint rules) before proceeding.

### 3.2 Visual Comparison

Invoke the `andthen:visual-validation` skill in a sub-agent with the screenshots. The validation report at `OUTPUT_DIR/validation-report.md` documents pass/fail per page/viewport and issues found.

### 3.3 Design Review

Run this skill's `review` mode against the wireframes to evaluate information hierarchy, content organization, user flow representation, and missing UI states.

### 3.4 Refinement

Fix layout issues, improve unclear sections, add missing elements, ensure consistency.

**Gate**: All automated checks pass, reviews complete

## Phase 4: Documentation

### 4.1 Update Page Inventory
Mark all wireframes as complete in `OUTPUT_DIR/page-inventory.md`.

### 4.2 Create Index Page

Create `OUTPUT_DIR/index.html` as a navigation hub: a grid of all wireframes with iframes previewing each page, title, brief description, and a link to the wireframe file.

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

## Quality Checklist

- [ ] **100% coverage**: Every page from requirements has a wireframe, cross-checked against inventory
- [ ] **Grayscale only**: No colors, focus on layout and hierarchy
- [ ] **Screenshots captured**: All 4 viewports for each page; no horizontal overflow, no overlapping elements, no broken layouts
- [ ] **Validation report**: Generated with pass/fail per page/viewport; all critical issues fixed
- [ ] **Index page**: Links to all wireframes

Wireframes focus on structure, not polish. Keep them simple, grayscale, and focused on layout patterns. Every page in the requirements must have a corresponding wireframe.
