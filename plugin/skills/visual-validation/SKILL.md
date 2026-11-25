---
description: Inspect a built UI and screenshots for layout defects, design mismatches, and visual regressions, or set up the project's capture strategy. Trigger on 'visual validation', 'check UI against design', 'set up visual validation'. Design authoring is the andthen:ui-ux-design skill.
argument-hint: "[--mode setup] [<screens-or-states-to-validate>] [design-reference/baseline]"
---

# Visual Validation

Judge the requested UI from rendered evidence, accounting for every required view before reporting a pass.

## Input

`$ARGUMENTS` minus flags names the screens, states, URLs, screenshots, Mockups, wireframes, baselines, or design requirements to validate.

- `--mode setup` writes the project's capture strategy without judging the UI, following [`setup.md`](references/setup.md).

## Rules

- `Visual Validation`, `Mockups`, `Wireframes`, `Design System`, and `Key Dev Commands` are Project Document Index entries.

## Workflow

### 1. Scope and references

Read the project's `Visual Validation` document (default `docs/VISUAL-VALIDATION.md`) for capture procedures, viewports, and reference locations.
Honor explicit limits on screens, states, and viewports.
For a journey or change, cover affected states within those limits, including failures and layout-changing content the `Visual Validation` document omits.
Without a narrower scope, cover the journeys users depend on.

- Cover the requested viewports, defaulting to the project's.
  Within a responsive review's scope, fill coverage gaps at layout transitions and tight supported widths.
- Judge each requested comparison against its named reference, retaining the comparison as a gap if that reference is unavailable.
- For built UI layout without a named comparator, use the feature's own Mockup at the `Mockups` location, else its wireframe at the `Wireframes` location, then design requirements or a baseline.
  Judge a design artifact against the caller's requirements.

**Gate**: each required screen, state, and viewport has an expected visible result and its source, or an explicit reference-free defect check.

### 2. Capture

Use the project's capture tooling, else the host's available browser, automation MCP, or CLI.
If none can capture the view, use temporary tooling or record the gap.
Save distinct captures under the requested path, else where the `Visual Validation` document puts them, else `.agent_temp/validation/`.

- On a live UI, perform the scoped interactions and capture the response before changing scroll or focus.
  Scroll the page and its scrolling containers to expose content and fixed overlays in context.
- Record an interaction, transition, or flow when the request or the `Visual Validation` document asks for one, in addition to the stills each required view needs.
  A recording is evidence only through frames you open, because you cannot watch video:
  - use the frames in the recording tool's contact sheet (agent-browser: `record start <file>.mp4 --cursor --contact-sheet` also writes `<file>.contact-sheet.png`);
  - extract a frame with ffmpeg for any moment the sheet skips, such as a small inline change;
  - judge a defect on a full-size frame or still, because a contact sheet is a downsampled composite.
- Open the images and verify the intended state and viewport.
  Recapture a wrong state, an unreadable shot, or a recording that misses the flow's result when the UI is available.
- Inspect the whole composition, then each region.
  Keep reference and subject as separate images, because a side-by-side composite is downsampled as one image.

**Gate**: each required view, comparison, or interaction has opened evidence covering it, or a `not judged` entry with the reason.
Judge the remaining views even when one lacks evidence.

### 3. Judge

**Differences before verdict.** Compare the arrangement of landmarks, their relative sizes, reading order, spacing, and primary action with the expectation for that viewport.
Where a Mockup's colours, type, or sizes differ from the current `Design System`, the design system governs those values.
Use pixel comparison on trustworthy baselines and judge the differences against user intent.

Inspect every region even where the reference matches or none exists:

- Look inside containers and at their edges for missing, clipped, overlapping, truncated, or unintentionally wrapped content.
- Check readability, contrast, target size, focus and state treatment, and whether the primary action and its response are visible in the relevant state.
- Report every visible defect and every mismatch with an expectation for this state and viewport.
- Carry an expectation from another viewport only when its source applies to both.
- Give the location, expected and observed appearance, and severity supported by the visible or exercised impact, or the named decision allowing the deviation.

Severities:

- **P1 Critical** – breaks intent, blocks use, hides content, or creates a critical accessibility failure.
- **P2 Major** – missing behavior, missing elements, visibly wrong implementation, or broken responsive behavior.
- **P3 Minor** – polish, small alignment or spacing issues, or low-risk refinement.

**Gate**: reconcile the findings with Step 1's required views.
A passing region identifies a landmark in its expected position and a visible detail at its boundary, quoting edge text where present.

## Output

Fail on any open P1 Critical or P2 Major finding.
Otherwise report incomplete if any required item is `not judged`, and pass when all are judged.
Report coverage gaps and P3 findings with any verdict.
After a fix, recapture the affected views and retain both verdicts and their evidence.

- **Summary** – verdict, coverage gaps, and whether the project document or the host's tooling supplied the procedure.
- **Detailed Findings** – by screen, state, viewport, and region, give each finding or pass with its capture path, or `not judged` with the reason.
- **Recommended Fixes** – specific changes in priority order, each tied to evidence from the capture, the design reference, or the accessibility guideline it fails.
- **Next Steps** – remaining gaps or retest needs.
