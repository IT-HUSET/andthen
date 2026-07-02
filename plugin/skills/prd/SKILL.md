---
description: Use when the user wants a PRD. Creates a Product Requirements Document from clarified requirements, a draft PRD, an inline description, a file, a URL, or a GitHub issue, then runs fresh-context doc self-review. Trigger on 'create a PRD', 'write a PRD', 'draft a PRD', 'PRD from clarify output'.
argument-hint: "[--to-issue] [--visual] [--auto] [specs directory or requirements source | --issue <number>]"
---

# Create Product Requirements Document


Produce a `prd.md` from whatever requirements material is available: a clarified requirements doc, a draft PRD, an inline description, a requirements file, a URL, or a GitHub issue. If a `prd.md` already exists in the target directory, pass through and exit – do not regenerate.

The PRD created here is the canonical local input for the `andthen:plan` skill, which can also fetch a GitHub PRD issue directly.

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
- `--auto` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Read project rules and guidelines (`CLAUDE.md` / `AGENTS.md` and referenced files) before starting.
- Require `INPUT`. Stop if missing.
- Delegate research and exploration to sub-agents (the `research` agent when available) to protect the main context window.
- **Resolve load-bearing gaps, don't assume them.** A gap is load-bearing when its answer would change user-visible behavior, scope, or acceptance criteria (the `andthen:clarify` skill's litmus). Conversationally, escalate each load-bearing gap by invoking the `andthen:clarify` skill inline on the same requirements source / feature directory, then continue from its `requirements-clarification.md`. Fill only routine gaps (convention, codebase patterns, adjacent docs) with documented assumptions. Under `--auto` the `andthen:clarify` skill is unavailable, so fall back to the most conservative MVP assumption and record it (see Automation rules and GOTCHAS).
- **Automation rules** (headless-first, `--auto` strict mode, `--auto` propagation): see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). PRD-specific `BLOCKED:` trigger: ambiguity past the Vague-Input Bailout bar (see GOTCHAS).
- **Visual review is a post-validation handoff.** In `AUTO_MODE`, the `--visual` handoff runs only when the flag is present (see OUTPUT > Visual Review).
- Focus on *what* not *how* (see Philosophy). Replace vague terms with measurable criteria; record rationale and trade-offs. Significant technical constraints → `Constraints & Assumptions`.
- **Feature-level PRDs are self-contained.** Inline the substance of transient discovery artifacts (`requirements-clarification.md`, `prd-draft.md`); never link or cite them by path. Durable references (GitHub issue, roadmap, ADRs) may be cited.


## GOTCHAS
- **Vague-Input Bailout** (`--auto` / routine gaps) – never skip synthesis when only a vague one-liner exists: infer the smallest coherent MVP, document assumptions in `Constraints & Assumptions` and the `Decisions Log`, and continue. Conversationally, load-bearing gaps escalate per INSTRUCTIONS; under `--auto`, assume conservatively and only `BLOCKED:` when multiple incompatible PRDs are equally plausible and none can be justified.
- **Implementation leak** – route *how* to the **Decisions Log** or the `andthen:plan` skill (Philosophy; Step 3 owns extraction)
- Writing `prd.md` into the wrong directory – resolve `OUTPUT_DIR` from the Step 1 dispatch exactly so the `prd → plan` chain stays stable


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

2. **Document optional assets** if present in the resolved directory (Architecture/ADRs, Design system, Wireframes). At the project level (see **Project Document Index**), read the `Product` document for vision/personas/anti-goals/success metrics, the `Architecture` document for structural constraints the PRD must not contradict, the `Decisions` document for recorded architectural constraints the PRD inherits, the `Roadmap` document for release phasing the PRD sits within, and the `Learnings` document for prior traps – when each exists. The PRD is a feature/release-scope derivative within these framings, not a re-derivation. Keep pointers to in-directory assets; don't inline contents.

**Gate**: Input validated, dispatch path chosen


### 2. Requirements Synthesis _(skip if a prior artifact is the basis; go to Step 3)_

Default to synthesis rather than interview – cover users & personas, core workflows, data model, integrations, constraints, NFRs, and success metrics. Fill routine gaps with explicit assumptions grounded in the source material, codebase patterns, adjacent artifacts, and standard product conventions – do not pause for them. Resolve load-bearing gaps per INSTRUCTIONS – conversationally this routes the clarification output back through the Step 3 path.

Initial gap analysis – document what's explicitly stated, what's assumed/implied, and what's missing/unclear (functional requirements, user flows, edge cases, success criteria, business context, MVP scope).

**Gate**: PRD is specific enough for planning; major assumptions and unresolved questions are documented explicitly → continue to Step 4


### 3. PRD from Existing Artifacts _(skip if running synthesis in Step 2)_

Use existing artifacts (`requirements-clarification.md` from the `andthen:clarify` skill and/or `prd-draft.md`) as the primary basis for the PRD.

- Map existing content against the PRD template (see [`prd-template.md`](${CLAUDE_PLUGIN_ROOT}/references/prd-template.md)); fill only the missing sections using bounded assumptions derived from the existing artifacts, codebase context, and adjacent documents.
- Do not re-ask questions already answered in the existing artifacts; do not pause for routine clarification.
- Resolve residual load-bearing gaps per INSTRUCTIONS; under `--auto`, `BLOCKED:` only when no defensible PRD shape exists.
- **Extract technical details**: if the draft contains implementation-level content (architecture patterns, technology choices, API details, framework constraints, integration specifics), keep them out of the PRD. Note significant technical constraints in `Constraints & Assumptions`; route unresolved architecture/UX decisions to their upstream skills and leave unfamiliar API/library lookup to execution (see Philosophy above).
- Preserve decisions, rationale, and specific details from existing artifacts – do not paraphrase or generalize away specifics; inline their substance.

**Gate**: Source artifacts mapped, gaps filled with bounded assumptions → continue to Step 4


### 4. Generate PRD Document

Structure the PRD from the synthesized or mapped requirements using the template at [`prd-template.md`](${CLAUDE_PLUGIN_ROOT}/references/prd-template.md). Keep the required sections, adapt optional subsections to the project, and preserve concrete decisions from discovery rather than generalizing them away. Apply MoSCoW prioritization (Must / Should / Could / Won't) and P0/P1/P2 levels to features.

The `Executive Summary` follows the template's summary-not-source contract: every summary bullet derives from a canonical row below (a fact that appears nowhere below moves into the matching detail section), and a conflicting `Capabilities at a Glance` priority tag resolves to the canonical FR's `**Priority**:` line – the summary is the bug.

Save the PRD to the `OUTPUT_DIR` resolved in Step 1.

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
- [ ] **Executive Summary derives, not declares**: every summary bullet maps to a canonical row below; no fact lives only in the summary; conflicts resolve to the canonical row (Step 4); summary stays under ~1 page rendered.

**Gate**: Validation complete


### 6. Self-Review _(automatic)_

Spawn a generic fresh-context sub-agent whose prompt invokes the `andthen:review` skill with `--mode doc --fix <prd.md>` (append `--auto` when `AUTO_MODE=true`). `--fix` auto-applies mechanical document defects; substantive gaps surface as `Note` findings. Run this before any `--to-issue` / `--visual` post-step so those act on the fixed PRD.

- **Conversational**: reflect on the residual `Note` findings. Route `ambiguous-intent` / requirement-gap Notes to a focused `andthen:clarify` pass (recommend it); otherwise recommend proceeding to the `andthen:plan` skill. When residual Notes carry blocking decisions that would fork downstream execution, note that the `andthen:preflight` skill drives them to zero on the resulting plan bundle (after `andthen:plan`); preflight targets a FIS or plan bundle, not the PRD, and prd does not invoke it.
- **`AUTO_MODE`**: fold residual `Note` findings into `Constraints & Assumptions` / `Decisions Log` so downstream skills inherit them; no conversational reflection.

**Gate**: Self-review complete; PRD reflects auto-applied fixes; residual Notes surfaced (recommended conversationally, recorded under `--auto`)


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
After Step 6 Self-Review completes, invoke the `andthen:visualize` skill on the produced `prd.md`. Print both the PRD path and the visualizer's output path.


## FOLLOW-UP ACTIONS

Skip this section when `AUTO_MODE=true`; print only the output path and completion summary.

After completion, suggest the following next steps. **Recommend a clean session** for the context-intensive downstream skills.

1. **Review visually** – run `andthen:visualize <prd.md>` to spot scope and edge-case issues a markdown view obscures (skip when `--visual` already ran).
2. **Create implementation plan** _(clean session recommended)_: Invoke the `andthen:plan` skill on the PRD directory – it produces the full plan bundle (`plan.json` + all FIS).
3. **Initialize project state** (if not already tracking): Create the `State` document via the `andthen:init` skill.

> Step 6 Self-Review already ran the `andthen:review` skill with `--mode doc --fix`; don't re-suggest a doc review here.


---


## Appendix: Template

**USE THE TEMPLATE**: [`prd-template.md`](${CLAUDE_PLUGIN_ROOT}/references/prd-template.md)
