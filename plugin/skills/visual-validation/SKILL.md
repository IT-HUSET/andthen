---
description: Validate UI screenshots and run visual regression checks against wireframes or design specs, or set up the project's capture procedure; wireframe authoring is the andthen:ui-ux-design skill. Trigger on 'visual validation', 'check UI against design', 'visual regression', 'set up visual validation'.
argument-hint: "[--mode setup] [<screens-or-states-to-validate>] [design-reference/baseline]"
---

# Visual Validation

`$ARGUMENTS` minus flags names the screens, states, URLs, screenshots, wireframes, baselines, or design requirements to validate. Inspect and capture within the current git root.


## MODES

| Mode | Purpose | Loads |
|------|---------|-------|
| `validate` (default, no flag) | Judge captures against their references. | – |
| `setup` | Author the project's `Visual Validation` document, once per project. Nothing is judged. | `references/setup.md` |


## INSTRUCTIONS

- Validating, read the `Visual Validation` document (see **Project Document Index**; default `docs/VISUAL-VALIDATION.md`) first – it replaces the Fallback Workflow. A missing document is not an error: the Fallback Workflow stands in and the Summary says the document was absent. Validation never writes it; `setup` does.
- Evidence, Judging, and Output Format hold under either workflow.
- Select capture and comparison tooling from what the environment already provides – project-documented browser/visual tooling first, then the host's built-in browser tooling or any available browser-automation MCP or CLI. Introduce a new tool only when nothing available can capture the states in scope.
- Scope is the states the work under validation touched, non-default states included, at the breakpoints the project names; with no change named, the states users depend on.


## Evidence

A vision model downsamples what it is given, so a full-page or side-by-side composite is judged as a thumbnail and its clipped edges read as fine. Each image, captured here or handed in, shows one region at viewport size, with reference and build as separate images of the same region. Scale a high-density capture down to 1×, then crop anything still over about 1600px on its long side. An image that cannot be read at that size is recorded `not judged`, never passed.


## Fallback Workflow

### Phase 1: Setup & Inventory

Identify baselines, wireframes, design references, or acceptance criteria for every state in scope – consult the `Wireframes` and `Design System` documents (see **Project Document Index**) when the project specifies non-default locations.

**Gate**: every state in scope is paired with the reference it will be judged against, or with a note that it has none.

### Phase 2: Capture Screenshots

Store captures in `.agent_temp/validation/`.

**Gate**: every state in scope has a capture, or a recorded reason it could not be captured.


## Judging

**Differences before verdict**: a reviewer asked whether a screen passes describes what is there; one asked what differs finds what is wrong. Per region, before any verdict:

1. List every visible difference from the reference, and every element that is clipped, truncated, overlapping, unintentionally wrapped, or missing. Region edges and container boundaries are where these sit.
2. Classify each one P1, P2, P3, or as a deviation a named decision allows.

With no reference, the defect sweep runs alone, against the design contract. Either way, judge what no reference shows: hierarchy and spacing, readability and contrast, touch-target size, state and focus treatment, responsive behavior, and whether the primary action is obvious and input gets a visible response.

Use pixel comparison when trustworthy baselines exist. Treat pixel diffs as evidence, not judgment; validate whether the diff matters to user intent.

**Gate**: every image in scope has its classified list before its verdict. An empty list quotes what was read at the region's edges; a verdict without a list is not a verdict.


## Output Format

Classify every finding:

- **P1 Critical**: breaks intent, blocks use, hides content, or creates a critical accessibility failure
- **P2 Major**: missing behavior, missing elements, visibly wrong implementation, or broken responsive behavior
- **P3 Minor**: polish, small alignment/spacing issues, or low-risk refinement

A P1 Critical or P2 Major finding blocks: a caller gates completion on it rather than filing it as advice, and re-validation after the fix recaptures the affected screens and states, the caller recording the second verdict beside the first. P3 is reported, not gated.

Return:

- **Summary**: overall status, screens/states covered, workflow used
- **Detailed Findings**: one line per region judged, naming its screen, state, and viewport – pass with the edge content it read, the finding with its severity and capture path, or `not judged`
- **Recommended Fixes**: specific changes in priority order, each tied to evidence from the capture, the design reference, or the accessibility guideline it fails
- **Next Steps**: remaining gaps or retest needs
