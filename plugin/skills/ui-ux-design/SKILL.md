---
description: UI/UX design – research, design systems, wireframes, singly or chained; validating a built UI is the andthen:visual-validation skill. Trigger on 'design this', 'create a design system', 'wireframe this feature', 'UX research'.
argument-hint: "[--auto] [inputs/path]"
---

# UI/UX Design

`ARGUMENTS` is `$ARGUMENTS` minus flags – the inputs or path; `--auto` is `AUTO_MODE`, automation-safe execution with no conversational prompts.

## Mode (auto-detected from arguments)

| Mode | Triggers | Required input | Mode reference |
|------|----------|----------------|----------------|
| **research** | "user research", "journey map", "information architecture", "competitive analysis", "flows" | feature requirements, a PRD, or a problem statement | `references/mode-research.md` |
| **design-system** | "design system", "style guide", "design tokens", "component styles" | `REQUIREMENTS` | `references/mode-design-system.md` |
| **wireframes** | "wireframes", "sketch the screens", "page layouts", "low-fi" | `REQUIREMENTS` | `references/mode-wireframes.md` |

Validating a built UI is not a mode here: route "UX review", "validate this UI", or "design compliance check" to the `andthen:visual-validation` skill.

**Multi-mode**: a request naming several of them in order ("research, then a design system, then wireframes") runs them in that order, sharing context – research insights feed design-system decisions, and the design-system mode's `OUTPUT_DIR` binds the wireframes mode's `DESIGN_DIR` so the tokens just written are the ones the wireframes use.

## INSTRUCTIONS

- Resolve the mode from `ARGUMENTS` via the auto-detect table. When exactly one mode's triggers match, proceed in that mode and state which mode and why in one line so the user can redirect – mode selection is cheap and reversible, so a named, correctable choice beats a blocking menu. Enter guided setup (Phase 0) only when the intent is genuinely ambiguous (no mode matches, or 2+ match with no dominant intent) or the detected mode's required input is missing, and a missing input scopes Phase 0 to eliciting just that input, not the full menu. Do not pick a mode from an empty invocation.
- **Automation mode** (`--auto`) – load [`automation-mode.md`](../../references/automation-mode.md) and run under its Strict Mode, inferring mode and inputs from the arguments via the auto-detect table; the `BLOCKED:` trigger here is arguments supporting no defensible inference. Without `--auto` this skill is interactive by contract – Phase 0 elicits, FOLLOW-UP ACTIONS offer – so that reference's headless-first default is not in play.
- **Intentional visual direction** – avoid generic AI aesthetics and default stacks. Choose typography with character. Use color intentionally with a dominant direction and clear accents.
- **Platform-agnostic canonical reference** – design tokens, wireframes, and style decisions serve as the canonical reference for all target platforms (web, mobile, desktop). Platform-specific implementation happens downstream.

## WORKFLOW

### Phase 0: Guided Setup _(only when mode is genuinely ambiguous or a required input is missing)_

Never runs in `AUTO_MODE`. Present the Mode table's rows one line each, and ask what they want to accomplish and what inputs they have (feature requirements, existing design system, concept directory, implementation URL, screenshots, etc.).

**Gate**: Mode(s) and inputs confirmed

### Phase 1: Execute Mode

Follow the selected mode's reference (see Mode table above). Each reference declares its own phases and outputs.

**Gate**: Mode work complete

### Phase 2: Report

For multi-mode chains, combine into a single session summary that points at each mode's artifacts.

## FOLLOW-UP ACTIONS

Skip this section when `AUTO_MODE=true` – print only the mode summary and artifact paths.

Offer, one line each: continue with the next mode (research → design-system → wireframes; the `andthen:visual-validation` skill validates the built UI against them), refine a named artifact, hand a component library to implementation, or end.
