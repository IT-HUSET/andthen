---
description: Use for UI/UX design work across the full lifecycle – research, design system creation, wireframing, and validation/review of implementations. Operates in four modes – `research`, `design-system`, `wireframes`, `review` – runnable singly or as a chain (e.g. `--mode design-system,wireframes`). Trigger on 'design this', 'create a design system', 'make a style guide', 'define design tokens', 'create wireframes', 'wireframe this feature', 'sketch the screens', 'review this UI', 'validate this UI', 'UX review'.
user-invocable: true
argument-hint: "[--mode <mode>[,<mode>...]] [--auto] [inputs/path]"
---

# UI/UX Design

Aim for deliberate, coherent design over safe generic output.

## VARIABLES

ARGUMENTS: $ARGUMENTS (strip any flag tokens like `--mode`, `--auto`, or `--headless` before interpreting the remainder as inputs/path)

### Optional Flags
- `--auto` → AUTO_MODE: automation-safe execution with no conversational prompts

### Mode Inputs (per-mode named tokens, bound from ARGUMENTS or elicited in Phase 0)

For **design-system** mode:
- `REQUIREMENTS` – required; feature requirements as inline description, file path, or PRD reference.
- `CONCEPT_DIR` – optional; directory with concept design, mockups, or existing design system.
- `OUTPUT_DIR` – `docs/design-system` or the **Project Document Index** design-system location.

For **wireframes** mode:
- `REQUIREMENTS` – required; feature requirements as inline description, file path, or PRD reference.
- `DESIGN_DIR` – optional; design system directory or concept design inputs.
- `OUTPUT_DIR` – `docs/wireframes` or the **Project Document Index** wireframes location.

Modes `research` and `review` describe inputs in prose – see their mode references.

### Mode (auto-detected from arguments or explicit `--mode`)

| Mode | Triggers | Mode reference |
|------|----------|----------------|
| **research** | "user research", "journey map", "information architecture", "competitive analysis", "flows" | `references/mode-research.md` |
| **design-system** | "design system", "style guide", "design tokens", "component styles" | `references/mode-design-system.md` |
| **wireframes** | "wireframes", "sketch the screens", "page layouts", "low-fi" | `references/mode-wireframes.md` |
| **review** | "UX review", "visual review", "validate this UI", "design compliance check" | `references/mode-review.md` |

**Multi-mode**: `--mode` accepts a comma-separated list (e.g. `--mode research,design-system,wireframes`). Modes execute in declared order, sharing context – research insights feed design-system decisions; tokens feed wireframes; wireframes feed review.

## INSTRUCTIONS

- Resolve the mode from `ARGUMENTS` via the auto-detect table: when exactly one mode's triggers match, proceed in that mode and state which mode and why in one line so the user can redirect – mode selection is cheap and reversible, so a named, correctable choice beats a blocking menu. Enter guided setup (Phase 0) only when the intent is genuinely ambiguous (no mode matches, or 2+ match with no dominant intent) or the detected mode is missing its required input (per the Mode Inputs above – design-system / wireframes need `REQUIREMENTS`; research / review need the primary untagged input listed in their mode reference's `## Inputs` section) – a missing input scopes Phase 0 to eliciting just that input, not the full menu. Do not pick a mode from an empty invocation.
- **Automation mode** (`--auto`) – never ask the user what to do next. Infer mode and inputs from the arguments via the auto-detect table; if no defensible inference is possible, stop with `BLOCKED:` listing the minimum missing inputs. Propagate `--auto` to nested `andthen:*` skill invocations that accept it.
- Read project rules and guidelines (`CLAUDE.md` / `AGENTS.md` and referenced files) before starting – including relevant UX/UI and Web Dev guidelines.
- **Intentional visual direction** – avoid generic AI aesthetics and default stacks. Choose typography with character. Use color intentionally with a dominant direction and clear accents.
- **Platform-agnostic canonical reference** – design tokens, wireframes, and style decisions serve as the canonical reference for ALL target platforms (web, mobile, desktop). Platform-specific implementation happens downstream.
- **Delegate to sub-agents** for parallel research, wireframe creation, or visual validation.

## GOTCHAS

- Guessing a mode when the goal is genuinely ambiguous instead of running Phase 0 – but equally, presenting the Phase 0 menu when the phrasing already names exactly one mode (auto-detect and proceed instead)
- Over-engineering – too many tokens, too many components, pixel-perfect wireframes

## WORKFLOW

### Phase 0: Guided Setup _(only when mode is genuinely ambiguous or a required input is missing)_

Skip per the mode-resolution and Automation contracts in INSTRUCTIONS (never runs in AUTO_MODE); when only a required input is missing, elicit just that input.

1. Present the available modes with one-line descriptions:
   - **research** – Understand users, flows, pain points, and the interface's job. Produces IA, journeys, and constraints.
   - **design-system** – Pragmatic design tokens, component styles, and a canonical `DESIGN.md` (token front matter + rationale) from feature requirements.
   - **wireframes** – Low-fidelity grayscale HTML wireframes with 100% page coverage from feature requirements.
   - **review** – Validate an existing UI implementation semantically and/or visually; produce prioritized issues with fix recommendations.

2. Ask what they want to accomplish and what inputs they have (feature requirements, existing design system, concept directory, implementation URL, screenshots, etc.).

3. Confirm mode(s) and inputs before proceeding.

**Gate**: Mode(s) and inputs confirmed

### Phase 1: Execute Mode

Follow the selected mode's reference (see Mode table above). Each reference declares its own phases, outputs, and quality checklist.

**Gate**: Mode work complete

### Phase 2: Report

Each mode reference declares its own output layout. For multi-mode chains, combine into a single session summary that points at each mode's artifacts.

## FOLLOW-UP ACTIONS

Skip this section when `AUTO_MODE=true` – print only the mode summary and artifact paths.

Offer:
1. **Continue with another mode** – research → design-system → wireframes → review is the natural chain
2. **Refine a specific artifact** – tokens, a wireframe page, a component style, a review finding
3. **Formalize a component library** in the project's frontend framework (hand off to implementation)
4. **End session**
