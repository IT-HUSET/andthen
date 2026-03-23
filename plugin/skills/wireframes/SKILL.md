---
description: Create simple HTML wireframes for all pages/screens from feature requirements
argument-hint: "[Feature requirements - inline, file path, or PRD reference] [Optional - design system or concept design directory]"
---

# Create Wireframes


Transform feature requirements into simple HTML wireframes that capture key layout and interaction patterns for all pages/screens.

**Platform-Agnostic**: HTML/CSS is used as the universal design language for ALL projects (web, mobile, desktop). Wireframes serve as the canonical design reference that will be adapted to platform-specific implementations later.


## VARIABLES

REQUIREMENTS: $1 (feature requirements - inline description, file path, or PRD reference)
DESIGN_DIR: $2 (optional - design system directory or concept design inputs)
OUTPUT_DIR: ${3:-docs/wireframes} _(or as configured in **Project Document Index**)_


## INSTRUCTIONS

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails**
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Wireframes only** - No design system creation (use the `andthen:design-system` skill for that)
- **Simple, grayscale layouts** - Focus on structure, not visual polish
- **100% page coverage** - Every page/screen in requirements MUST have a wireframe
- **Delegate to sub-agents** _(if supported by your coding agent; otherwise execute sequentially)_ for parallel wireframe creation
- **Browser automation required** - Use Playwright MCP or Chrome DevTools MCP for visual validation (falls back to manual if unavailable)


## GOTCHAS
- Missing pages from the requirements — 100% page coverage is critical
- Creating pixel-perfect designs instead of low-fidelity wireframes — grayscale, layout-only
- Not testing across viewport sizes — check all 4 viewports


## WORKFLOW

### Phase 1: Requirements Analysis

#### 1.1 Validate Inputs
- Verify _`REQUIREMENTS`_ is provided - if not, **STOP** and ask user
- If _`DESIGN_DIR`_ provided, verify it exists and note available design assets

#### 1.2 Create Page Inventory
**CRITICAL**: Extract comprehensive list of ALL pages/screens from _`REQUIREMENTS`_:
- Main pages (home, dashboard, settings, etc.)
- Sub-pages and detail views
- Modal/overlay states (if complex enough to warrant separate wireframe)
- Error/empty/loading states (if distinct layouts needed)

Document in _`OUTPUT_DIR/page-inventory.md`_:
```markdown
# Page Inventory

## Pages to Wireframe
1. [page-name] - [brief description]
2. [page-name] - [brief description]
...

## Total: [N] wireframes required
```

#### 1.3 Identify Key Patterns
From requirements, note:
- **Navigation structure** (header, sidebar, tabs, etc.)
- **Key content blocks** and their hierarchy
- **Primary user actions** and CTA placement
- **Responsive requirements** (mobile/tablet/desktop)

**Gate**: Complete page inventory created, patterns identified


### Phase 2: Wireframe Creation

#### 2.1 Wireframe Approach
Create basic, grayscale HTML layouts showing:
- **Major sections** and their placement
- **Key containers** (panels, cards, etc.)
- **Content blocks** with realistic proportions
- **Primary navigation** structure
- **Important CTAs** and hierarchy
- **Basic responsive behavior**

**Keep it simple**:
- Use boxes and placeholders
- Grayscale only - no colors
- Focus on layout, not details
- Show information hierarchy

#### 2.2 Base Template
Use this template for all wireframes:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Page Name] - Wireframe</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: system-ui, sans-serif;
            line-height: 1.5;
            color: #333;
            background: #f5f5f5;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .box {
            background: white;
            border: 2px solid #ddd;
            padding: 20px;
            margin-bottom: 20px;
        }
        .placeholder {
            background: #e0e0e0;
            border: 2px dashed #999;
            padding: 40px;
            text-align: center;
            color: #666;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: #666;
            color: white;
            text-decoration: none;
        }
        .btn-outline {
            background: white;
            color: #666;
            border: 2px solid #666;
        }
        .grid {
            display: grid;
            gap: 20px;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        }
        .flex { display: flex; gap: 20px; align-items: center; }
        @media (max-width: 768px) {
            .flex { flex-direction: column; }
        }
    </style>
</head>
<body>
    <!-- Page content here -->
</body>
</html>
```

#### 2.3 Common Patterns

**Navigation:**
```html
<nav class="box">
    <div class="flex" style="justify-content: space-between;">
        <div class="placeholder" style="width: 120px; height: 40px;">LOGO</div>
        <div class="flex">
            <a href="#" class="btn btn-outline">Menu 1</a>
            <a href="#" class="btn btn-outline">Menu 2</a>
            <a href="#" class="btn">Sign Up</a>
        </div>
    </div>
</nav>
```

**Hero Section:**
```html
<section class="box">
    <div class="grid" style="grid-template-columns: 1fr 1fr;">
        <div>
            <h1 style="font-size: 2.5rem; margin-bottom: 1rem;">Headline</h1>
            <p style="margin-bottom: 2rem; color: #666;">Description text</p>
            <a href="#" class="btn">Get Started</a>
        </div>
        <div class="placeholder" style="height: 300px;">IMAGE</div>
    </div>
</section>
```

**Content Grid:**
```html
<div class="grid">
    <div class="box">
        <div class="placeholder" style="height: 150px; margin-bottom: 10px;">IMG</div>
        <h3>Item Title</h3>
        <p>Brief description</p>
    </div>
    <!-- Repeat -->
</div>
```

#### 2.4 Parallel Wireframe Creation
**CRITICAL**: Create wireframes in parallel for efficiency.

For each page in the inventory, launch `andthen:ui-ux-designer` _(if supported by your coding agent)_ with:
- Page name and purpose
- Key content/sections to include
- Navigation context
- Responsive requirements
- Reference to base template

**Execute multiple agents simultaneously** _(if supported by your coding agent; otherwise execute sequentially)_ - each handles a single page.

**Naming convention**: `[page-name].html` (e.g., `home.html`, `dashboard.html`, `user-profile.html`)

#### 2.5 Completeness Verification
After all wireframes created:
- Cross-check against Phase 1 inventory
- Verify EVERY page has corresponding wireframe
- No page skipped because "similar" to another

**Gate**: All pages from inventory have wireframes


### Phase 3: Validation

#### 3.1 Browser-Based Visual Validation
**CRITICAL**: Use browser automation (Playwright MCP or Chrome DevTools MCP) to capture and validate wireframes across viewports.

##### 3.1.1 MCP Server Detection
Check available browser automation tools in order of preference:
1. **Playwright MCP** (`mcp__playwright__*` tools) - preferred
2. **Chrome DevTools MCP** (`mcp__chrome-devtools__*` tools) - fallback
3. **Manual validation** - if no MCP available, use `andthen:visual-validation-specialist` with manually opened browser

##### 3.1.2 Viewport Matrix
Test each wireframe at these viewports:
| Device | Width | Height |
|--------|-------|--------|
| Mobile | 375px | 667px |
| Tablet | 768px | 1024px |
| Desktop | 1280px | 800px |
| Wide | 1920px | 1080px |

##### 3.1.3 Automated Screenshot Capture
For **each wireframe** in `OUTPUT_DIR`:

**Using Playwright MCP:**
```
1. Navigate to file:///path/to/OUTPUT_DIR/[page].html
2. For each viewport in matrix:
   - Set viewport size
   - Wait for layout to stabilize
   - Capture full-page screenshot
   - Save to OUTPUT_DIR/screenshots/[page]-[viewport].png
```

**Using Chrome DevTools MCP:**
```
1. Open file:///path/to/OUTPUT_DIR/[page].html
2. For each viewport:
   - Emulate device/viewport
   - Capture screenshot
   - Save to OUTPUT_DIR/screenshots/[page]-[viewport].png
```

##### 3.1.4 Automated Validation Checks
Run these checks programmatically via browser automation:

**Layout Integrity:**
- No horizontal overflow (scroll width ≤ viewport width)
- Content doesn't overflow containers
- All boxes render with expected dimensions
- No negative margins pushing content off-screen

**Overlapping Elements:**
- Check element bounding boxes for unexpected overlaps
- Verify z-index stacking is intentional (nav over content is OK, content over content is not)
- Detect elements with same position coordinates that shouldn't overlap
- Check for text overlapping other text or UI elements

**Broken Layouts:**
- Elements with zero width/height that should have content
- Flex/grid children overflowing their parents
- Absolute/fixed positioned elements outside viewport
- Elements with `display: none` that should be visible
- Collapsed containers (height: 0) with visible children

**Missing Assets:**
- Placeholder images not rendering (broken `<img>` tags)
- Missing background images (check `background-image` loads)
- Icons not displaying (font icons, SVG, or image icons)
- Check network tab for 404 errors on any assets

**Responsive Behavior:**
- Navigation collapses/adapts at mobile breakpoints
- Grid layouts reflow correctly (no single-column becoming zero-width)
- Flexible elements resize proportionally
- Touch targets remain ≥44px on mobile
- Text remains readable (no tiny fonts at small viewports)

**Element Visibility:**
- All placeholder boxes visible and non-zero size
- Text content readable (not truncated unexpectedly)
- CTAs accessible and clickable
- No content hidden behind other elements unintentionally

**Console Errors:**
- Check for JavaScript errors
- Check for resource loading failures (404s, CORS issues)
- Check for CSS parsing errors

##### 3.1.5 Issue Detection & Fix Protocol
When issues are detected, follow this protocol:

**For Overlapping Elements:**
```css
/* Fix: Add explicit positioning or adjust flex/grid */
.overlapping-element {
  position: relative; /* or adjust z-index */
  margin-top: 20px;   /* or add spacing */
}
/* Or fix grid/flex gap */
.parent { gap: 20px; }
```

**For Broken Layouts:**
```css
/* Fix: Ensure minimum dimensions */
.box { min-height: 50px; min-width: 100px; }
/* Fix: Prevent overflow */
.container { overflow: hidden; } /* or overflow: auto; */
/* Fix: Constrain absolute elements */
.absolute-child { max-width: 100%; }
```

**For Missing Icons/Images:**
```html
<!-- Fix: Add fallback text for placeholders -->
<div class="placeholder">
  <span class="fallback-text">IMAGE</span>
</div>
<!-- Fix: Use CSS background with fallback color -->
<style>
.icon { background: #ccc url('icon.svg') center/contain no-repeat; }
</style>
```

**For Responsive Issues:**
```css
/* Fix: Add missing breakpoint rules */
@media (max-width: 768px) {
  .grid { grid-template-columns: 1fr; }
  .flex { flex-direction: column; }
  .btn { min-height: 44px; min-width: 44px; }
}
```

**Severity Classification:**
| Issue | Severity | Action |
|-------|----------|--------|
| Content completely hidden/invisible | 🔴 Critical | Fix immediately |
| Overlapping text/buttons | 🔴 Critical | Fix immediately |
| Missing navigation elements | 🔴 Critical | Fix immediately |
| Horizontal scroll on mobile | 🟠 High | Fix before review |
| Minor overlap (decorative only) | 🟡 Medium | Fix if time permits |
| Suboptimal spacing | 🟢 Low | Note for refinement |

#### 3.2 Visual Comparison
Launch `andthen:visual-validation-specialist` _(if supported by your coding agent)_ with:
- **Screenshots captured** from Phase 3.1
- **Comparison criteria**:
  - Layout consistency across viewports
  - Proportional scaling of elements
  - Readable content hierarchy
  - Proper spacing and alignment

**Specific issues to detect visually:**
- **Overlapping elements**: Text on text, buttons on content, nav items colliding
- **Broken layouts**: Gaps where content should be, asymmetric grids, misaligned elements
- **Missing visuals**: Empty placeholder boxes, broken image indicators, missing icons
- **Truncated content**: Text cut off mid-word, ellipsis where full text expected
- **Inconsistent spacing**: Uneven margins/padding between similar elements
- **Z-index issues**: Content hidden behind other elements, dropdowns under content

Agent should produce `OUTPUT_DIR/validation-report.md` documenting:
```markdown
# Wireframe Validation Report

## Summary
- Pages validated: [N]
- Viewports tested: [mobile, tablet, desktop, wide]
- Issues found: [N] (🔴 Critical: X, 🟠 High: Y, 🟡 Medium: Z)

## Per-Page Results

### [page-name].html
| Viewport | Status | Issues |
|----------|--------|--------|
| Mobile | ✅/❌ | [issue summary] |
| Tablet | ✅/❌ | [issue summary] |
| Desktop | ✅/❌ | [issue summary] |
| Wide | ✅/❌ | [issue summary] |

**Issues Found:**
1. 🔴 [Critical issue description]
   - Screenshot: screenshots/[page]-[viewport].png
   - Location: [element/section]
   - Fix: [specific CSS/HTML fix]

2. 🟠 [High priority issue]
   ...

## Recommended Fixes
[Consolidated list of fixes with code snippets]
```

#### 3.3 Design Review
Launch `andthen:ui-ux-designer` _(if supported by your coding agent)_ to:
- Evaluate information hierarchy
- Check content organization
- Verify user flow representation
- Identify missing UI states

#### 3.4 Refinement
Based on review feedback:
- Fix layout issues
- Improve unclear sections
- Add missing elements
- Ensure consistency across pages

**Gate**: All automated checks pass, reviews complete


### Phase 4: Documentation

#### 4.1 Update Page Inventory
Mark all wireframes as complete in _`OUTPUT_DIR/page-inventory.md`_.

#### 4.2 Create Index Page
Create _`OUTPUT_DIR/index.html`_ as navigation hub:
- Grid/list of all wireframes with thumbnails
- Brief description of each page
- Links to individual wireframe files

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wireframe Index</title>
    <style>
        body { font-family: system-ui; padding: 40px; background: #f5f5f5; }
        .grid { display: grid; gap: 20px; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
        .card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }
        .card iframe { width: 100%; height: 200px; border: none; pointer-events: none; }
        .card-body { padding: 16px; }
        .card h3 { margin: 0 0 8px; }
        .card p { color: #666; margin: 0 0 12px; }
        .card a { color: #333; }
    </style>
</head>
<body>
    <h1>Wireframes</h1>
    <p style="color: #666; margin-bottom: 24px;">Total: [N] pages</p>
    <div class="grid">
        <!-- Card per wireframe -->
        <div class="card">
            <iframe src="[page].html"></iframe>
            <div class="card-body">
                <h3>[Page Name]</h3>
                <p>[Brief description]</p>
                <a href="[page].html">View wireframe &rarr;</a>
            </div>
        </div>
    </div>
</body>
</html>
```

**Gate**: Documentation complete


## OUTPUT

```
OUTPUT_DIR/
├── index.html              # Navigation hub for all wireframes
├── page-inventory.md       # Checklist of all pages
├── home.html               # Individual wireframes...
├── dashboard.html
├── [page-name].html
├── screenshots/            # Visual validation captures
│   ├── home-mobile.png
│   ├── home-tablet.png
│   ├── home-desktop.png
│   ├── home-wide.png
│   ├── dashboard-mobile.png
│   └── ...
├── validation-report.md    # Automated validation results
└── ...
```


## QUALITY CHECKLIST

### Coverage
- [ ] **100% coverage**: Every page from requirements has a wireframe
- [ ] **No missing pages**: Cross-checked against inventory
- [ ] Page inventory matches actual files
- [ ] Index page links to all wireframes

### Design Quality
- [ ] Layout hierarchy is clear
- [ ] Navigation is consistent across pages
- [ ] All wireframes use grayscale (no colors)

### Visual Validation (Browser Automation)
- [ ] **Screenshots captured**: All viewports (mobile/tablet/desktop/wide) for each page
- [ ] **No horizontal overflow**: Content fits viewport at all sizes
- [ ] **No overlapping elements**: Text/buttons don't collide unexpectedly
- [ ] **No broken layouts**: All containers render with content, no collapsed sections
- [ ] **No missing visuals**: Placeholders, icons, and images all render
- [ ] **Responsive behavior**: Layouts adapt correctly at breakpoints
- [ ] **Touch targets**: Buttons ≥44px on mobile viewports
- [ ] **No console errors**: Clean browser console (no 404s, no JS errors)
- [ ] **All critical issues fixed**: No 🔴 items remaining in validation report
- [ ] **Validation report**: Generated with pass/fail per page/viewport


**Remember**: Wireframes focus on structure, not polish. Keep them simple, grayscale, and focused on layout patterns. Every page in the requirements must have a corresponding wireframe.
