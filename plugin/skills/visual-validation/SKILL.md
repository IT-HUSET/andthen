---
description: Validate UI screenshots and run visual regression checks against wireframes or design specs, or set up the project's capture procedure; wireframe authoring is the andthen:ui-ux-design skill. Trigger on 'visual validation', 'check UI against design', 'set up visual validation'.
argument-hint: "[--mode setup] [<screens-or-states-to-validate>] [design-reference/baseline]"
---

# Visual Validation

Validate built UI against its design references, listing the differences before any verdict.

## Input

`$ARGUMENTS` minus flags names the screens, states, URLs, screenshots, wireframes, baselines, or design requirements to validate.

- `--mode setup` authors the project's `Visual Validation` document, once per project, and judges nothing: read [`setup.md`](references/setup.md) and follow it.

## Rules

- Inspect and capture within the current git root.
- `Visual Validation`, `Wireframes`, `Design System`, and `Key Dev Commands` are Project Document Index entries.

## Workflow

### 1. Scope and references

Read the `Visual Validation` document (default `docs/VISUAL-VALIDATION.md`) first. Its procedure replaces the fallback in Steps 1 and 2, gates included; the Evidence rule, Step 3 with its gate, and the Output hold either way. A missing document is not an error: the fallback stands in.

Scope is the states the work under validation touched, non-default states included, at the breakpoints the project names. With no change named, it is the states users depend on.

Fallback: identify the baselines, wireframes, design references, or acceptance criteria for every state in scope, consulting the `Wireframes` and `Design System` documents.

**Gate**: every state in scope is paired with the reference it will be judged against, or with a note that it has none.

### 2. Capture

Select capture and comparison tooling from what the environment already provides: project-documented browser or visual tooling first, then the host's built-in browser tooling or any available browser-automation MCP or CLI. Introduce a new tool only when nothing available can capture the states in scope, because an install is a dependency change the user did not ask for. Fallback captures go in `.agent_temp/validation/`.

**Evidence.** A vision model downsamples what it is given, so a full-page or side-by-side composite is judged as a thumbnail and its clipped edges read as fine. Each image, captured here or handed in, shows one region at viewport size, with reference and build as separate images of the same region. Scale a high-density capture down to 1×, then crop anything still over about 1600px on its long side. An image that cannot be read at that size is recorded `not judged`, never passed.

**Gate**: every state in scope has a capture, or a recorded reason it could not be captured.

### 3. Judge

**Differences before verdict**, per region:

1. List every visible difference from the reference, and every element that is clipped, truncated, overlapping, unintentionally wrapped, or missing. Region edges and container boundaries are where these sit.
2. Classify each one P1, P2, P3, or as a deviation a named decision allows.

With no reference, the defect sweep runs alone, against the design contract. Either way, judge what no reference shows: hierarchy and spacing, readability and contrast, touch-target size, state and focus treatment, responsive behavior, and whether the primary action is obvious and input gets a visible response.

Use pixel comparison when trustworthy baselines exist, and decide whether the diff matters to user intent.

Severities:

- **P1 Critical** – breaks intent, blocks use, hides content, or creates a critical accessibility failure.
- **P2 Major** – missing behavior, missing elements, visibly wrong implementation, or broken responsive behavior.
- **P3 Minor** – polish, small alignment or spacing issues, or low-risk refinement.

**Gate**: every image in scope has its classified list before its verdict. An empty list quotes what was read at the region's edges.

## Output

A P1 Critical or P2 Major finding blocks: a caller gates completion on it, and re-validation after the fix recaptures the affected screens and states, the caller recording the second verdict beside the first. P3 is reported, not gated.

- **Summary** – overall status, the screens and states covered, and the workflow used: the document or the fallback.
- **Detailed Findings** – one line per region judged, naming its screen, state, and viewport: a pass with the edge content it read, the finding with its severity and capture path, or `not judged`.
- **Recommended Fixes** – specific changes in priority order, each tied to evidence from the capture, the design reference, or the accessibility guideline it fails.
- **Next Steps** – remaining gaps or retest needs.
