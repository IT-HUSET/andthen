---
description: Generate a new spec (FIS) before implementation, for a standalone feature or a plan story, then run fresh-context doc self-review. Not for executing an existing spec – that is the andthen:exec-spec skill. Trigger on 'create a spec for this', 'write a FIS', 'specify this feature'.
argument-hint: "[--visual] [--auto] <description | @<requirements-file> | story <story-id> of <path-to-plan.json>>"
---

# Generate Feature Implementation Specification


Generate an execution-sized Feature Implementation Specification (FIS) from a feature request. One spec → one FIS. Oversized features emit an `OVERSIZE:` signal and redirect (see OUTPUT § Oversize signal); the `andthen:plan` skill is the sole writer of `plan.json`.


## VARIABLES

ARGUMENTS: $ARGUMENTS (strip any flag tokens like `--visual`, `--auto`, or `--headless` before interpreting the remainder as the description / `@file` / `story <id> of <plan>`)

### Optional Flags
- `--visual` → VISUAL_MODE: after the FIS is saved, self-reviewed, and any plan-status updates land, invoke the `andthen:visualize` skill on the produced FIS. The visualizer owns HTML rendering, note export, browser-open behavior, and `.agent_temp/visual-review/` output.
- `--auto` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Read project rules and guidelines (`CLAUDE.md` / `AGENTS.md` and referenced files) before starting.
- Require `ARGUMENTS`. Stop if missing.
- **Spec generation only** – no code changes, commits, or modifications.
- The executor only gets the context you provide – include all needed documentation, examples, and references.
- Read the `Learnings` document (see **Project Document Index**) before starting, if it exists.
- **Automation rules** (headless-first, `--auto` strict mode, `--auto` propagation): see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). Spec-specific `BLOCKED:` triggers: missing input, unreadable sources, incompatible artifacts, ambiguity where no defensible FIS can be written.


## GOTCHAS

**Specifying before orienting** – the quick codebase scan in Step 1 must precede specification (Step 5). Deep file-pattern exploration waits for the `andthen:exec-spec` skill.

**Scenarios before intent** – Step 3 (Intent + Expected Outcomes) must precede Step 4 (Acceptance Scenarios). Without outcomes named first, scenarios drift into implementation paths rather than success conditions.

**Undefined behavior** – surface ambiguity and missing requirements per [`execution-named-blocks.md`](${CLAUDE_PLUGIN_ROOT}/references/execution-named-blocks.md): `CONFUSION:`, `NOTICED BUT NOT TOUCHING:`, `MISSING REQUIREMENT:`. In `AUTO_MODE`, apply that reference's override, recording the conservative choice as an FIS assumption.

**Implementation-shaped specs** – tasks state what must be TRUE when done, not what code to write; Given/When/Then asserts observable behavior, not internal code steps; every criterion carries a concrete verify check (if you can't write the **Then**, you don't understand the requirement yet). Shape rules and worked bad/good examples: *Key Generation Guidelines* and *Scenario Authoring Principles* in [the authoring guidelines](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md) (referenced below as *The Authoring Guidelines*).

**Over-researching** – this skill inlines load-bearing upstream spans into Required Context; it is not a new research pass. A 30-line minimal FIS is fine; a spec that reads like a diff is too detailed. Size threshold and oversize handling: see *Key Generation Guidelines #7* in *The Authoring Guidelines*.

**Generic "What We're NOT Doing"** – record real non-goals or deferrals with reasons, not filler.


## WORKFLOW

### 0. Parse Input & Get Requirements

**ARGUMENTS is a directory with `requirements-clarification.md`** (from the `andthen:clarify` skill): read it; use clarified scope, functional requirements, edge cases, acceptance outcomes, design decisions, wireframes, and explicit non-goals/deferrals as the feature request. Skip or reduce research phases – the `andthen:clarify` skill already did discovery. Only do codebase research and any external/API research the requirements reference but haven't investigated.

**ARGUMENTS match `story {story_id} of {path}` AND `path`'s basename matches `plan.*` but is not `plan.json`** (e.g. `plan.md`, `plan.yaml`): stop with `BLOCKED: only plan.json is consumed; got "{basename}". If you have a legacy plan.md, run the andthen:plan skill on {dirname(path)} to migrate (existing FIS files are preserved), then retry the andthen:spec skill with: story {story_id} of {dirname(path)}/plan.json`. Same in `AUTO_MODE`. Do not fall through to the file-reference branch – that would silently treat the path as a free-form description.

**ARGUMENTS use `story {story_id} of {path-to-plan.json}`**: read the plan JSON; locate the story by `id`; use its compact story brief fields (`scope`, `sourceRefs`, optional `provenance`, `assetRefs`, `notes`) plus catalog metadata (`phase`, `wave`, `dependsOn`, `parallel`, `risk`) as the feature request. Read the PRD anchors named in `sourceRefs` for detailed behavioral source material – do not re-read the whole PRD. Plan briefs do not carry Acceptance Scenarios or Structural Criteria; derive those from source-ref spans, scope, `bindingConstraints`, and Step 4 below. Store plan path and story ID for output updates. When `plan.json` carries non-empty `sharedDecisions` and/or `bindingConstraints` arrays, read them: `sharedDecisions` inform architectural alignment with siblings; each `bindingConstraints[]` entry's `verbatim` becomes a Required Context block with the entry's `anchor` as the source pin.

**Otherwise**: use inline description or file reference as the feature request.


### 1. Priming and Project Understanding

Quick `tree -d` + `git ls-files | head -250` scan to orient. Stop there – file-pattern exploration happens at exec-spec time when the executor has a concrete task in front of it.


### 2. Identify Required Inputs

Walk the references the FIS will need (`Product`, PRD, plan, ADRs, `Decisions`, `Architecture`, `Stack`, design system, wireframes, glossary, `Ubiquitous Language` – per **Project Document Index** where applicable). Confirm existence or note absence. The `Product` and `Architecture` documents anchor feature scope and structural patterns respectively when standalone PRD/ADR coverage is thin; the `Stack` document pins language/framework/runtime/DB/testing baseline when Architecture coverage is thin; the `Decisions` document indexes ADRs and load-bearing non-ADR choices, so a row in **Current ADRs** or **Still Current** narrows the option space before the FIS is written.

Contradictions between the feature request and a row in `DECISIONS.md` surface in the FIS Constraints/Context section as `NOTICED:` observations, not Stop-the-Line – `DECISIONS.md` is a registry, not a gate, and the user owns reconciliation.

If an obviously-needed input is missing (e.g. FIS needs an architectural trade-off and no ADR exists, or UI work and no wireframe), surface as `MISSING REQUIREMENT:` (interactive) or `BLOCKED:` (`AUTO_MODE`) with a redirect to the upstream skill (`andthen:architecture --mode trade-off`, `andthen:ui-ux-design --mode wireframes`, etc.). Keep this check **light** – flag obvious gaps only. Stop for ambiguity only when it blocks a defensible specification; return the minimum missing decisions rather than pausing for routine clarification.

Do **not** invoke architecture / UI / documentation-lookup sub-agents from spec. Architecture and UX are upstream (`andthen:clarify` → `andthen:architecture` → `andthen:ui-ux-design` → `andthen:prd` → `andthen:plan` → `andthen:spec` → `andthen:exec-spec`); ad-hoc API/library lookups are the `andthen:exec-spec` skill's job.


### 3. Articulate Intent and Expected Outcomes

Read *The Authoring Guidelines* now – Steps 3-5 follow them. Lock down the FIS's intent anchor *before* writing scenarios – outcomes are what Step 4 tags into. For plan-story or clarify-output inputs, distil intent and outcomes from the upstream goal/value statement and the story's scope. Intent and Expected Outcome definitions and `[OC<NN>]` tagging: *Feature Overview and Goal Authoring* in *The Authoring Guidelines*.


### 4. Write Acceptance Scenarios

Concrete BDD examples (Given/When/Then) serving triple duty: requirement, test specification, proof-of-work contract. Each tags the Expected Outcome(s) it exemplifies via `[OC<NN>]`, closing the Intent → Outcomes → Scenarios chain. After drafting, apply the **negative-path checklist** from *The Authoring Guidelines*. Ordering, count, canonical checkbox shape, and proof-of-work semantics: *Acceptance Scenarios and Proof-of-Work* and *Scenario Authoring Principles* there, plus the Outcome ↔ Scenario coverage rule in *Feature Overview and Goal Authoring*; the template carries the worked examples.


### 5. Generate FIS

#### Gather Context
- ADRs, the `Decisions` registry, and the `Architecture` document (see **Project Document Index**); `file#symbol` references for patterns to follow (see *Cross-Document References* rule #1 for the symbol-anchor ladder)
- `Stack` document (see **Project Document Index**) when present – language, framework, runtime, DB, and testing-library baseline; FIS Approach, Code Patterns, and Testing Strategy must align with it
- UI wireframes/mockups; design system references; external documentation URLs
- `Ubiquitous Language` document (see **Project Document Index**) – use canonical terms; flag any contradictions
- For plan-story inputs: `sharedDecisions` and `bindingConstraints` handling per Step 0

#### Resolve Cross-Document References

Walk every upstream document the spec depends on, sorting each reference into **Required Context** (load-bearing spans inlined verbatim) or **Deeper Context** (anchored pointers) per *Cross-Document References* in *The Authoring Guidelines*. The walk is mandatory; both sections are conditional – omit either when the walk surfaces nothing for it.

#### Generate from Template
Use the template in the **Appendix** below and follow *The Authoring Guidelines*.

Canonical shape:

- `## Acceptance Scenarios` – canonical checkbox shape per *The Authoring Guidelines* (no `### S<NN>` headers).
- `## Structural Criteria` – non-behavioral proof requirements (regression guards, invariants); each proved by a task Verify line.
- `### Work Areas` under `## Scope & Boundaries` – 3-7 bullets inventorying components, files, or surfaces changed. Each Work Area maps to ≥1 task or scenario.
- `## Architecture Decision` – 3-4 lines max (`**Approach**:`, optional `**Why this over alternatives**:`). Longer analysis routes to `andthen:architecture --mode trade-off`.
- Always-present sections with a "**Leave empty** when…" prompt (`## Technical Overview`, `### Testing Strategy`, `### Validation`, `### Execution Contract`, `## Final Validation Checklist`) stay empty in the typical case – fill only when the prompt's named condition applies. Resist auto-filling; empty is the default.
- `## Required Context` and `## Deeper Context` are content-conditional omits per the template's "**Omit this entire section**" prompts.


## OUTPUT

- Directory input (e.g. clarify output): save FIS inside as `{feature-name}.md`
- Plan story input: save FIS in plan directory as `s{NN}-{name}.md` (two-digit zero-padded story number; `{name}` is a kebab-case slug derived from the story name). The FIS body must carry `**Plan**:` and `**Story-ID**:` between the H1 and `## Feature Overview and Goal`, populated from the source plan path and story ID.
- Otherwise: save at `docs/specs/{feature-name}.md` _(or as configured in **Project Document Index**)_
  - GitHub issue input: include issue reference in filename, e.g. `issue-123-feature-name.md`
**Oversize signal** – after saving, measure against the threshold from *Key Generation Guidelines #7* in *The Authoring Guidelines*. If oversized, emit (interactive and `AUTO_MODE`):

```
OVERSIZE: {fis_path} – {N} lines, {T} tasks. Recommendation: {recommendation}
```

- **Standalone input**: `switch to the andthen:prd skill with <input> to start the prd → plan → exec-plan chain`
- **Plan-story input**: `story too broad – revisit {plan_path} and decompose before regenerating`

Plan-batch sub-agents must echo the `OVERSIZE:` line in their completion summary so the `andthen:plan` orchestrator can revisit Step 3.

### Self-Review _(automatic, skip when OVERSIZE fired)_
After the FIS is saved and OVERSIZE passes, run a doc self-review: prefer a generic fresh-context sub-agent whose prompt invokes the `andthen:review` skill with `--mode doc --fix <fis_path>`; run it in-context where nested sub-agents aren't available. The pass owns review/remediation – spec consumes its result.

- `--fix` auto-remediates mechanical doc defects.
- Non-blocking residual Notes become explicit FIS assumptions, constraints, or follow-up notes.
- A residual Note needing an architecture/requirements decision before the FIS is executable is **blocking** – name the upstream skill (architecture trade-offs → the `andthen:architecture` skill with `--mode trade-off`). When one or more blocking Notes remain, recommend running the `andthen:preflight` skill on the FIS to drive them to zero before an unattended `andthen:exec-spec` run – spec recommends it; it does not invoke preflight.

**Update source plan** – for a plan-story FIS when `OVERSIZE:` did not fire (the FIS exists on disk, so its pointer is always recorded):
  - `andthen:ops update-plan-fis <plan_path> <story_id> <fis_path>` – set `stories[].fis`.
  - `andthen:ops update-plan <plan_path> <story_id> spec-ready` – **only** when self-review left no blocking Note. On a blocking Note, leave the status unchanged and emit `MISSING REQUIREMENT:` (interactive) or `BLOCKED:` (`AUTO_MODE`).

### Visual Review _(if --visual)_
After save, self-review, plan-status updates, and OVERSIZE check – identically in `AUTO_MODE` – invoke the `andthen:visualize` skill on the produced FIS path. Print both the FIS path and the visualizer's output path. **Skip when `OVERSIZE:` fired** – the FIS is about to be discarded or regenerated; print `--visual skipped: OVERSIZE` instead.

---


## FOLLOW-UP ACTIONS

Skip this section when `AUTO_MODE=true`; print only the generated artifact paths, the `OVERSIZE:` line if applicable, and downstream command shape.

After the FIS is saved, suggest:

1. **Implement the FIS**: Invoke the `andthen:exec-spec` skill.
2. **Review visually**: Run `andthen:visualize <fis-path>` to spot scenario/task coverage and verify-line issues a markdown view obscures (skip when `--visual` already ran).

> **Session tip**: The `andthen:exec-spec` skill is context-intensive (it runs the full implementation + verification loop). Start a **clean session** for best results.

If the `OVERSIZE:` signal fired, expand the OUTPUT recommendation conversationally.


---


## Appendix: FIS Template

**USE THE TEMPLATE**: Read and use the template at [`fis-template.md`](${CLAUDE_PLUGIN_ROOT}/references/fis-template.md) to generate the Feature Implementation Specification.
