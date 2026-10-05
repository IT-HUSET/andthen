# UI/UX – Wireframes Mode

Turn feature requirements into simple HTML wireframes that capture the key layout and interaction patterns of every page and screen.

Bound from `ARGUMENTS`:

- `REQUIREMENTS` – required: an inline description, a file path, or a PRD reference.
- `DESIGN_DIR` – optional: a design system directory or concept inputs, noted when it exists.
- `OUTPUT_DIR` – the `Wireframes` document location (default `docs/wireframes`).

**100% page coverage**: an un-wireframed page becomes an un-designed surface downstream, so every distinct page and state in the inventory gets its own wireframe.

## Workflow

### Phase 1: Requirements analysis

#### 1.1 Page inventory

Extract every page and screen from `REQUIREMENTS`, including modal and overlay states complex enough to warrant their own wireframe and error, empty, and loading states that need distinct layouts. Record them in `OUTPUT_DIR/page-inventory.md`:

```markdown
# Page Inventory
## Pages to Wireframe
1. [page-name] - [brief description]
## Total: [N] wireframes required
```

#### 1.2 Key patterns

Note the navigation structure, key content blocks and their hierarchy, primary user actions and CTA placement, and responsive requirements (mobile, tablet, desktop).

**Gate**: `page-inventory.md` lists every page and distinct state.

### Phase 2: Wireframe creation

#### 2.1 Wireframe principles

Basic grayscale HTML layouts: major sections and their placement, key containers (panels, cards), content blocks in realistic proportions, primary navigation, important CTAs. Boxes and placeholders only; layout and hierarchy over polish.

**HTML structure**: Use `system-ui` font, `#f5f5f5` background, white `.box` containers with `2px solid #ddd`, `.placeholder` divs with `#e0e0e0` background and `2px dashed #999`, `.btn` in `#666`, CSS grid/flex for layout, and a `@media (max-width: 768px)` breakpoint. Include `<!DOCTYPE html>`, a `viewport` meta tag, and the CSS inline in `<style>`.

#### 2.2 Parallel creation

The pages are independent, so fan out one implementer subagent per inventory page, concurrently. Each gets its page only and never re-enters this mode: a child re-entering the mode would rebuild the inventory and re-run validation once per page. Give each one 2.1's HTML structure verbatim, its `OUTPUT_DIR/[page-name].html` target, the page's name and purpose, its key content and sections, its navigation context, and its responsive requirements. It writes that page's HTML and returns the path.

**Gate**: every page in the inventory has a wireframe, none skipped for seeming "similar" to another.

### Phase 3: Validation

#### 3.1 Visual validation

Validation needs browser automation. When the subagent below reports that nothing available can set viewports and capture screenshots, report validation as not run, and why: a manually opened browser does not satisfy it.

Spawn a fresh reviewer subagent that invokes the `andthen:visual-validation` skill over every wireframe page at four viewports:

- Mobile 375×667
- Tablet 768×1024
- Desktop 1280×800
- Wide 1920×1080

Ask it also to judge missing UI states.

Screenshots land at `OUTPUT_DIR/screenshots/[page]-[viewport].png`, overriding its default capture directory, and the report at `OUTPUT_DIR/validation-report.md`, per page and viewport.

#### 3.2 Refinement

Fix hidden or overlapping content, missing navigation, and horizontal scroll on mobile first, by adjusting CSS (gap, overflow, min-height, breakpoint rules). Note spacing and decorative overlap and continue. Then improve unclear sections, add missing elements, and make the pages consistent.

**Gate**: the report holds no P1 or P2 finding and no `not judged` region for any page and viewport, or validation is reported as not run.

### Phase 4: Documentation

Mark every wireframe complete in `OUTPUT_DIR/page-inventory.md`. Create `OUTPUT_DIR/index.html` as a navigation hub: a grid of all wireframes, each with an iframe preview, its title, a brief description, and a link to its file.

**Gate**: `index.html` links every wireframe in the inventory.

## Output

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
