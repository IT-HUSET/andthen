---
description: UI/UX design – research, design systems, wireframes, clickable mockups, singly or chained; validating a built UI is the andthen:visual-validation skill. Trigger on 'design this', 'create a design system', 'wireframe this feature', 'mock up these screens'.
argument-hint: "[--auto] [inputs/path]"
---

# UI/UX Design

Design tokens, wireframes, Mockups, and style decisions are the canonical reference for every target platform (web, mobile, desktop); platform-specific implementation happens downstream.

## Input

`ARGUMENTS` is `$ARGUMENTS` minus flags – the inputs or path.

- `--auto` makes the run unattended: read [`unattended-runs.md`](../../references/unattended-runs.md) and follow it.

`Design System`, `Wireframes`, and `Mockups` are Project Document Index entries.

## Rules

- Print each recommended skill invocation as a complete, paste-ready line in the host's syntax, including its target path or request and required arguments.

Every dispatch is a fresh subagent: the installed role agent it names (`implementer`, `reviewer`) when available, else a generic inherited subagent. Never pin model or effort in a prompt.

## Workflow

### 1. Resolve the mode

| Mode | Triggers | Required input |
|------|----------|----------------|
| **research** | "user research", "journey map", "information architecture", "competitive analysis", "flows" | feature requirements, a PRD, or a problem statement |
| **design-system** | "design system", "style guide", "design tokens", "component styles" | `REQUIREMENTS` |
| **wireframes** | "wireframes", "sketch the screens", "page layouts", "low-fi" | `REQUIREMENTS` |
| **mockups** | "mockups", "hi-fi", "clickable", a prototype of screens or flows | `REQUIREMENTS` |

Validating a built UI is not a mode here: route "UX review", "validate this UI", or "design compliance check" to the `andthen:visual-validation` skill.

When exactly one mode's triggers match `ARGUMENTS`, in any language, proceed in that mode.

**Level**: a design system is present when `DESIGN.md` sits at the `Design System` location or an earlier mode of this run writes it.

- A request to design screens that names no level runs mockups while a design system is present, else wireframes.
- Mockups asked for with no design system run wireframes, and the mode line says mockups need the design-system mode first.
- A "prototype" that may mean technical feasibility is asked about, because that prototype is the `andthen:spike` skill's.

Say in one line which mode or modes run and why, so the user can redirect.

Ask only when no mode matches, when two or more match with no dominant intent, or when the detected mode's required input is missing. A missing input scopes the ask to that input, not the full menu.

**Multi-mode**: a request naming several modes in order ("research, then a design system, then wireframes") runs them in that order, sharing context. Research insights feed design-system decisions, and the design-system mode's `OUTPUT_DIR` binds the mockups mode's `DESIGN_DIR`, so the Mockups use the tokens just written.
Wireframes stay grayscale.

**Gate**: the mode or modes and their inputs are settled.

### 2. Run the mode

Read the mode's reference and follow it; each declares its own phases and outputs:

- design-system: [`mode-design-system.md`](references/mode-design-system.md).
- wireframes: [`mode-wireframes.md`](references/mode-wireframes.md).
- mockups: [`mode-mockups.md`](references/mode-mockups.md).
- research: below.

**Research** understands users, flows, pain points, and constraints, and defines the information architecture. It outputs:

- **Job-to-be-done** – one sentence: what the interface must make easy.
- **Primary journeys** – the 2–5 flows carrying most of the value, each an ordered list of user intents and system responses.
- **IA sketch** – the hierarchy and navigation model; prefer shallow, legible hierarchies.
- **Constraints** – accessibility (tap targets, contrast, focus, safe areas), platform, performance, localization length.
- **Open questions** – the few decisions design cannot proceed without, or `none`.

**Gate**: all five outputs are written, Open questions possibly `none`.

## Output

Name each mode's artifacts by path; a multi-mode chain does so in one session summary.

## Follow-up

Close on one `Next (fresh session):` line for the first case that applies, never a menu:

- **The run ended on research with open questions** – the `andthen:clarify` skill on the requirements source, or the problem statement, with: `<the questions>`.
- **A design system, with no screens designed yet, drawn from a PRD whose `Decisions Log` puts design before planning** – this skill on that PRD.
- **A design system, wireframes, or Mockups drawn from a PRD or other requirements document** – the `andthen:plan` skill on it.
- **Otherwise** – no line: a next mode runs here, since research findings live in this conversation.
