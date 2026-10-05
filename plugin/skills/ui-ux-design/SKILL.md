---
description: UI/UX design – research, design systems, wireframes, singly or chained; validating a built UI is the andthen:visual-validation skill. Trigger on 'design this', 'create a design system', 'wireframe this feature'.
argument-hint: "[--auto] [inputs/path]"
---

# UI/UX Design

Design tokens, wireframes, and style decisions are the canonical reference for every target platform (web, mobile, desktop); platform-specific implementation happens downstream.

## Input

`ARGUMENTS` is `$ARGUMENTS` minus flags – the inputs or path.

- `--auto` makes the run unattended: read [`unattended-runs.md`](../../references/unattended-runs.md) and follow it.

`Design System` and `Wireframes` are Project Document Index entries.

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

Validating a built UI is not a mode here: route "UX review", "validate this UI", or "design compliance check" to the `andthen:visual-validation` skill.

When exactly one mode's triggers match `ARGUMENTS`, proceed in that mode and say in one line which mode and why, so the user can redirect: mode selection is cheap and reversible, so a named, correctable choice beats a blocking menu.

Ask only when no mode matches, when two or more match with no dominant intent, or when the detected mode's required input is missing. Present the table's rows one line each, and ask what the user wants to accomplish and what inputs they have. A missing input scopes the ask to that input, not the full menu.

**Multi-mode**: a request naming several modes in order ("research, then a design system, then wireframes") runs them in that order, sharing context. Research insights feed design-system decisions, and the design-system mode's `OUTPUT_DIR` binds the wireframes mode's `DESIGN_DIR`, so the wireframes use the tokens just written.

**Gate**: the mode or modes and their inputs are settled.

### 2. Run the mode

Read the mode's reference and follow it; each declares its own phases and outputs:

- design-system: [`mode-design-system.md`](references/mode-design-system.md).
- wireframes: [`mode-wireframes.md`](references/mode-wireframes.md).
- research: below.

**Research** understands users, flows, pain points, and constraints, and defines the information architecture. It reads feature requirements, PRDs, or a problem statement (required); existing product, competitors, or domain benchmarks (optional); and user-facing constraints (accessibility, localization, device targets). It outputs:

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
- **A design system, with no wireframes yet, drawn from a PRD whose `Decisions Log` puts design before planning** – this skill in wireframes mode on that PRD.
- **A design system or wireframes drawn from a PRD or other requirements document** – the `andthen:plan` skill on it.
- **Otherwise** – no line: a next mode runs here, since research findings live in this conversation.
