# UI/UX – Mockups Mode

Turn feature requirements into clickable, hi-fi HTML Mockups of every page and flow, built on the project's design system, so the builder and customers judge the design before anything is built.

Bound from `ARGUMENTS`:

- `REQUIREMENTS` – required: an inline description, a file path, or a PRD reference.
- `DESIGN_DIR` – required: the `Design System` location holding `DESIGN.md`, or the design-system mode's `OUTPUT_DIR` earlier in this run.
- `WIREFRAMES` – the feature's folder under the `Wireframes` location, when it exists.
- `OUTPUT_DIR` – `<Mockups location>/<feature>/` (default location `docs/mockups`), the feature named as `REQUIREMENTS` names it.

A Mockup folder is frozen and standalone: it links nothing outside itself, so it opens anywhere and stays what was approved after the design system changes.

## Workflow

### Phase 1: Inventory

Record in `OUTPUT_DIR/inventory.md` every page and distinct state the feature needs, and every flow as the ordered pages and interactions a user walks through it.
Read `WIREFRAMES` as input when present; the Mockups may change its layout without listing the changes, and its folder stays untouched.

**Gate**: every page, state, and flow the requirements imply is in the inventory.

### Phase 2: Mockup creation

#### 2.1 Mockup principles

- Copy `tokens.css`, `components.css`, and the assets the pages use from `DESIGN_DIR` into `OUTPUT_DIR`, and style every page from them, so it renders from disk with no server.
- Write realistic text drawn from `REQUIREMENTS`, and a labelled placeholder for each image.
- Link the pages so every inventory flow can be walked, and make the interactions it needs work in-page: dialogs, tabs, error and empty states, a form advancing a step. Store no data and run no data logic.
- Build what the design system lacks from its tokens, and report it.

#### 2.2 Parallel creation

The pages are independent, so fan out one implementer subagent per inventory page, concurrently.
Each gets its page only and never re-enters this mode, because a child re-entering it would rebuild the inventory and re-run validation once per page.
Give each one 2.1 verbatim, the copied stylesheet paths, its `OUTPUT_DIR/[page-name].html` target, the page's purpose and content, and its links and interactions from the inventory's flows.
It writes that page and returns the path and what it built beyond the design system, which you list in `OUTPUT_DIR/design-system-gaps.md`.

**Gate**: every page in the inventory has a Mockup.

### Phase 3: Validation

Validation needs browser automation.
When the subagent below reports that nothing available can set viewports and capture screenshots, report validation as not run, and why: a manually opened browser does not satisfy it.

Spawn a fresh reviewer subagent that invokes the `andthen:visual-validation` skill over every Mockup page at Mobile 375×667, Tablet 768×1024, Desktop 1280×800, and Wide 1920×1080.
It judges against `DESIGN_DIR` and `REQUIREMENTS`, never `WIREFRAMES`.
Ask it also to report:

- text and UI component contrast below WCAG 2.x AA;
- colour and size values outside the design system's tokens;
- a click-through of every inventory flow, naming each link or interaction that leads nowhere;
- any network request a page makes when opened over `file://`.

Screenshots land at `OUTPUT_DIR/screenshots/[page]-[viewport].png`, overriding its default capture directory, and the report at `OUTPUT_DIR/validation-report.md`.
Fix each P1 and P2 finding and re-validate what the fix touched.

**Gate**: the report holds no open P1 or P2 finding and no `not judged` region, or validation is reported as not run.

### Phase 4: Hub

Create `OUTPUT_DIR/index.html` linking every page with its title and purpose, stamped with the design system the Mockups were built against: its `DESIGN.md` path and that file's last-change date.

**Gate**: `index.html` links every inventory page and carries the stamp.

## Output

```
OUTPUT_DIR/
├── index.html               # Hub linking every page, with the design-system stamp
├── inventory.md             # Pages, states, and flows
├── design-system-gaps.md    # What the design system lacked, built from its tokens
├── tokens.css               # Copied from the design system, with components.css and assets
├── [page-name].html         # Mockups...
├── screenshots/             # Visual validation captures
└── validation-report.md     # Validation results
```
