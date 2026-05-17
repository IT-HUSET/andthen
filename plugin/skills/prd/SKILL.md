---
description: Use when the user wants a PRD. Creates a Product Requirements Document from clarified requirements, a draft PRD, an inline description, a file, a URL, or a GitHub issue. Trigger on 'create a PRD', 'write a PRD', 'draft a PRD', 'PRD from clarify output'.
argument-hint: "[--to-issue] [--visual] [--auto|--headless] [specs directory or requirements source | --issue <number>]"
---

# Create Product Requirements Document


Produce a `prd.md` from whatever requirements material is available: a clarified requirements doc, a draft PRD, an inline description, a requirements file, a URL, or a GitHub issue. If a `prd.md` already exists in the target directory, pass through and exit – do not regenerate.

Upstream of the `andthen:plan` skill. The PRD created here is the required input for `andthen:plan`.

**Philosophy**: PRDs focus on *what* must be true for users and the business – not *how* to build it. Story breakdown belongs in the `andthen:plan` skill; architecture/UX trade-offs belong in upstream specialist artifacts, and ad-hoc API/library lookup happens during execution.


## VARIABLES

_Requirements source (**required**):_
INPUT: $ARGUMENTS (strip any flag tokens like `--issue`, `--to-issue`, `--visual`, `--auto`, or `--headless` before interpreting the remainder as the requirements source)

_Output directory (derived from INPUT type – see Step 1 dispatch table):_
OUTPUT_DIR: _(resolved per Step 1)_

### Optional Flags
- `--issue <number>` → Fetch and use a GitHub issue as requirements input
- `--to-issue` → PUBLISH_ISSUE: Publish PRD as a GitHub issue after saving locally
- `--visual` → VISUAL_MODE: after `prd.md` is saved and validated, invoke the `andthen:visualize` skill on the produced `prd.md`.
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- **Fully read and understand all project rules, guardrails, principles and guidelines (as defined in `CLAUDE.md` / `AGENTS.md` and other referenced files) before starting work.**
- Require `INPUT`. Stop if missing.
- Delegate research and exploration to sub-agents to protect the main context window.
- **Automation rules** (headless-first, `--auto` / `--headless` strict mode, `--auto` propagation): see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). PRD-specific `BLOCKED:` triggers: missing input; ambiguity so severe two or more incompatible PRDs are equally plausible; unsafe external actions on `--to-issue`.
- **Visual review is a post-validation handoff.** In `AUTO_MODE`, run it only when `--visual` is present. When present, complete the normal PRD gate first, then invoke the `andthen:visualize` skill on the produced `prd.md`; the visualizer owns HTML rendering, note export, browser-open behavior, and `.agent_temp/visual-review/` output.
- Focus on "what" not "how". Replace vague terms with measurable criteria. Record rationale and trade-offs.
- Keep implementation-level details out (architecture patterns, library choices, API specifics, code organization). Capture significant technical constraints in `Constraints & Assumptions`; defer unresolved architecture/UX decisions upstream and API/library lookup to execution.


## GOTCHAS
- **Vague-Input Bailout** – skipping synthesis when only a vague one-liner exists. Instead: infer the smallest coherent MVP, document assumptions in `Constraints & Assumptions` and the `Decisions Log`, and continue. Only stop when multiple incompatible PRDs are equally plausible and none can be justified.
- Re-asking questions already answered in `requirements-clarification.md` or `prd-draft.md`
- Letting implementation details leak into the PRD – if it's about *how*, push it to the **Decisions Log** or defer to the `andthen:plan` skill
- Writing `prd.md` into the wrong directory – follow **Output Path Semantics** exactly so the `prd → plan` chain stays stable
- Overwriting an existing `prd.md` – always pass through when one exists


_Output path resolution – see the dispatch table in Step 1._


## WORKFLOW

### 1. Input Validation & Dispatch

1. **Parse INPUT** – route by type:

   | Input type | Action |
   |------------|--------|
   | Directory with `prd.md` | Pass-through: print the existing path and exit. |
   | Directory with prior artifacts (`requirements-clarification.md` and/or `prd-draft.md`, no finalized `prd.md`) | Proceed to Step 3 (PRD from Existing Artifacts). |
   | File path that is a prior artifact (`prd-draft.md` or `requirements-clarification.md`) | Proceed to Step 3. |
   | Other file path, URL, or inline description | Proceed to Step 2 (Synthesis). |
   | `--issue <N>` or GitHub issue URL | Fetch the body with `gh issue view <N>` and use its content as raw requirements input. Store the issue number for reference in the PRD header. Proceed to Step 2 (Synthesis). |

2. **Document optional assets** if present in the resolved directory (Architecture/ADRs, Design system, Wireframes). If the `Product` document exists at the project level (see **Project Document Index**), read it for vision, personas, anti-goals, and success metrics – the PRD is a feature/release-scope derivative within that product framing, not a re-derivation. Keep pointers to in-directory assets; don't inline contents.

**Gate**: Input validated, dispatch path chosen


### 2. Requirements Synthesis _(skip if a prior artifact is the basis; go to Step 3)_

Cover the same areas as the `andthen:clarify` skill Phase 2, but default to synthesis rather than interview: users & personas, core workflows, data model, integrations, constraints, NFRs, and success metrics. Fill ordinary gaps using explicit assumptions grounded in the source material, codebase patterns, adjacent artifacts, and standard product conventions.

When a gap materially affects scope or prioritization and the evidence is weak, choose the most conservative MVP assumption that still allows a coherent PRD. Record it under `Constraints & Assumptions` and in the `Decisions Log` with alternatives considered. Do not pause the run for routine clarification.

Stop and defer to the `andthen:clarify` skill only when the input is so ambiguous that two or more incompatible PRDs are equally plausible and no conservative MVP assumption would make one of them defensible. Below that bar, continue headlessly with documented assumptions.

Initial gap analysis – document what's explicitly stated, what's assumed/implied, and what's missing/unclear (functional requirements, user flows, edge cases, success criteria, business context, MVP scope).

**Gate**: PRD is specific enough for planning; major assumptions and unresolved questions are documented explicitly → continue to Step 4


### 3. PRD from Existing Artifacts _(skip if running synthesis in Step 2)_

Use existing artifacts (`requirements-clarification.md` from the `andthen:clarify` skill and/or `prd-draft.md`) as the primary basis for the PRD. This path avoids duplicating discovery work already completed.

- Map existing content against the PRD template (see [`prd-template.md`](${CLAUDE_PLUGIN_ROOT}/references/prd-template.md)); fill only the missing sections using bounded assumptions derived from the existing artifacts, codebase context, and adjacent documents.
- Do not re-ask questions already answered in the existing artifacts; do not pause for routine clarification.
- If the artifacts are too ambiguous to support any defensible PRD shape, stop and report the minimum missing decisions required. Mention the `andthen:clarify` skill as the interactive fallback.
- **Extract technical details**: if the draft contains implementation-level content (architecture patterns, technology choices, API details, framework constraints, integration specifics), keep them out of the PRD. Note significant technical constraints in `Constraints & Assumptions`; route unresolved architecture/UX decisions to their upstream skills and leave unfamiliar API/library lookup to execution (see Philosophy above).
- Preserve decisions, rationale, and specific details from existing artifacts – do not paraphrase or generalize away specifics.

**Gate**: Source artifacts mapped, gaps filled with bounded assumptions → continue to Step 4


### 4. Generate PRD Document

Structure the PRD from the synthesized or mapped requirements using the template at [`prd-template.md`](${CLAUDE_PLUGIN_ROOT}/references/prd-template.md). Keep the required sections, adapt optional subsections to the project, and preserve concrete decisions from discovery rather than generalizing them away. Apply MoSCoW prioritization (Must / Should / Could / Won't) and P0/P1/P2 levels to features.

The `Executive Summary` is the **human review entry point** – a reviewer should be able to read it alone and understand what is being built, for whom, why, and what is explicitly not in scope. Fill its `Capabilities at a Glance` (one line per FR in `Functional Requirements > Feature Specifications`, with ID and name matching the canonical `#### FRn:` heading exactly), `Scope Highlights` (drawn from `## Scope`), and `Key Constraints, Assumptions & Dependencies` (drawn from `## Constraints & Assumptions`). Do not introduce requirements that live only in the summary; if a fact appears nowhere below, move it into the matching detail section. The inline priority tag in `Capabilities at a Glance` must match the canonical FR's `**Priority**:` line – if they conflict, the canonical line wins and the summary is the bug.

When running headlessly, do not leave important ambiguity implicit. Capture it as an explicit assumption, dependency, or deferred decision in the PRD so downstream skills inherit a usable contract.

Save the PRD to the path resolved under **Output Path Semantics**.

**Gate**: PRD saved


### 5. PRD Validation

Self-check:
- [ ] Problem statement with measurable impact
- [ ] All user stories have testable acceptance criteria
- [ ] Success metrics are specific and measurable
- [ ] Scope explicitly defined (in/out)
- [ ] Every feature has defined error handling
- [ ] Non-functional requirements have clear thresholds
- [ ] No ambiguous terms without definitions
- [ ] All assumptions documented
- [ ] No conflicting requirements
- [ ] **Problem-solution fit (bidirectional)**: every pain or desired outcome named on the **problem side** – in `Problem Definition` and in the "so that..." clauses of `Functional Requirements > User Stories` – has at least one feature, acceptance criterion, or metric on the **solution side** (a row in `Functional Requirements > Feature Specifications`, an item in `Executive Summary > Success Metrics`, a `Non-Functional Requirements` threshold, or a `Scope > In Scope` capability) that signals it's resolved; and every solution-side item traces back to such a pain or outcome. Fix: unaddressed problem → add a feature/metric or drop the problem element; orphan solution → drop it or amend `Problem Definition` / user-story rationale to justify (solutionism smell).
- [ ] **Executive Summary is a summary, not a source**: walk each summary subsection bullet-by-bullet and confirm a matching canonical row exists below.
  - Each `Capabilities at a Glance` bullet → a `#### FRn: [Feature Name]` block in `Functional Requirements > Feature Specifications` with the exact same `FRn:` ID, the same feature name, and a `**Priority**:` line that agrees with the inline tag.
  - Each `Scope Highlights` bullet → an item in `## Scope > In Scope` / `Out of Scope` / `MVP Boundary`.
  - Each `Key Constraints, Assumptions & Dependencies` bullet → an item in `## Constraints & Assumptions > Constraints` / `Assumptions` / `Dependencies`.
  - Fix: if a summary bullet has no canonical row, either move it down into the matching detail section or delete it. If they conflict, canonical wins and the summary is the bug.
  - The summary stays under ~1 page rendered.

Optional: Invoke the `andthen:review --mode doc` skill to validate the PRD before finalizing.

**Gate**: Validation complete


## OUTPUT

```
OUTPUT_DIR/
└── prd.md                 # Product Requirements Document
```

- If from GitHub issue: use `issue-{number}-{feature-name}/` as the output subdirectory name (e.g. `docs/specs/issue-42-user-dashboard/prd.md`). Include issue reference in the PRD header.

When complete, print the output's **relative path from the project root**. Do not use absolute paths.

### Publish to GitHub _(if --to-issue)_
If `PUBLISH_ISSUE` is `true`, publish `prd.md` per **Pattern A** in [`github-publish.md`](${CLAUDE_PLUGIN_ROOT}/references/github-publish.md). Title: `[PRD] {project-name}: Product Requirements Document`. Labels: `prd`, `andthen-artifact`. Body temp file: `.agent_temp/prd/<feature-slug>-issue-body.md` when `Refs #<N>` is appended (input issue supplied via `--issue <N>` or a GitHub issue URL); otherwise pass `prd.md` directly to `--body-file`. Print the local path (`prd.md`) alongside the issue URL.

### Visual Review _(if --visual)_
After `prd.md` is saved and Step 5 Validation passes, invoke the `andthen:visualize` skill on the produced `prd.md`. Print both the PRD path and the visualizer's output path.


## FOLLOW-UP ACTIONS

Skip this section when `AUTO_MODE=true`; print only the output path and completion summary.

After completion, suggest the following next steps. **Recommend a clean session** for the context-intensive downstream skills.

1. **Review visually** – run `andthen:visualize <prd.md>` to spot scope and edge-case issues a markdown view obscures.
2. **Create implementation plan** _(clean session recommended)_: Invoke the `andthen:plan` skill on the PRD directory – it produces the full plan bundle (`plan.json` + all FIS).
3. **Review the PRD**: Invoke the `andthen:review --mode doc` skill on `prd.md`.
4. **Initialize project state** (if not already tracking): Create the `State` document via the `andthen:init` skill.


---


## Appendix: Template

**USE THE TEMPLATE**: [`prd-template.md`](${CLAUDE_PLUGIN_ROOT}/references/prd-template.md)
