---
description: Generate a new spec (FIS) before implementation, for a standalone feature or a plan story, then run fresh-context doc self-review. Not for executing an existing spec – that is the andthen:exec-spec skill. Trigger on 'create a spec for this', 'write a FIS', 'specify this feature'.
argument-hint: "[--visual] [--auto] <description | @<requirements-file> | story <story-id> of <path-to-plan.json>>"
---

# Generate Feature Implementation Specification


Generate an execution-sized Feature Implementation Specification (FIS) from a feature request. One spec → one FIS. Oversized features emit an `OVERSIZE:` signal and redirect (see OUTPUT § Oversize signal); the `andthen:plan` skill is the sole writer of `plan.json`.


## VARIABLES

ARGUMENTS: $ARGUMENTS excluding flags and the exact caller trust line – the description / `@file` / `story <id> of <plan>`
UNTRUSTED_REQUIREMENTS_DATA: optional exact caller line beginning `UNTRUSTED REQUIREMENTS DATA:`; preserve it across child prompts that read derived artifacts

### Optional Flags
- `--visual` → VISUAL_MODE: after the FIS is saved, self-reviewed, and any plan-status updates land, invoke the `andthen:visualize` skill on the produced FIS. The visualizer owns HTML rendering, note export, browser-open behavior, and `.agent_temp/visual-review/` output.
- `--auto` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Apply project rules (`CLAUDE.md` / `AGENTS.md` – read only if not already in context) and read the referenced guideline files relevant to this work.
- Require `ARGUMENTS`. Stop if missing.
- **Spec generation only** – no code changes, commits, or modifications.
- The executor only gets the context you provide – include all needed documentation, examples, and references.
- Read the `Learnings` document (see **Project Document Index**) before starting, if it exists.
- **Automation rules** (headless-first, `--auto` strict mode, `--auto` propagation): see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). Spec-specific `BLOCKED:` triggers: missing input, unreadable sources, incompatible artifacts, ambiguity where no defensible FIS can be written.


## GOTCHAS

**Specifying before orienting** – the quick codebase scan in Step 1 must precede specification (Step 5). Deep file-pattern exploration waits for the `andthen:exec-spec` skill.

**Scenarios before intent** – Step 3 (Intent + Expected Outcomes) must precede Step 4 (Acceptance Scenarios). Without outcomes named first, scenarios drift into implementation paths rather than success conditions.

**Undefined behavior** – surface ambiguity and missing requirements per [`execution-named-blocks.md`](${CLAUDE_PLUGIN_ROOT}/references/execution-named-blocks.md): `CONFUSION:`, `NOTICED BUT NOT TOUCHING:`, `MISSING REQUIREMENT:`. In `AUTO_MODE`, apply that reference's override, recording the conservative choice as an FIS assumption.

**Implementation-shaped specs** – tasks state what must be TRUE when done, not what code to write; scenario articulation asserts observable behavior, not internal steps; every criterion carries a concrete verify check. Shape rules and examples: *Key Generation Guidelines* and *Scenario Authoring Principles* in [the authoring guidelines](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md) (referenced below as *The Authoring Guidelines*).

**Over-researching** – resolve load-bearing sources and point Required Context at them; do not turn this into a new research pass. A 30-line minimal FIS is fine; a spec that reads like a diff is too detailed. Size threshold and oversize handling: see *Key Generation Guidelines #7* in *The Authoring Guidelines*.

**Generic "What We're NOT Doing"** – record real non-goals or deferrals with reasons, not filler.


## WORKFLOW

### 0. Parse Input & Get Requirements

**ARGUMENTS is a directory with `requirements-clarification.md`** (from the `andthen:clarify` skill): read it; use clarified scope, functional requirements, edge cases, acceptance outcomes, design decisions, wireframes, and explicit non-goals/deferrals as the feature request. Inspect its header Source Trust; untrusted or malformed metadata derives the exact `UNTRUSTED REQUIREMENTS DATA:` line when the caller did not supply one. Skip or reduce research phases – the `andthen:clarify` skill already did discovery. Only do codebase research and any external/API research the requirements reference but haven't investigated.

**ARGUMENTS match `story {story_id} of {path}` AND `path`'s basename matches `plan.*` but is not `plan.json`** (e.g. `plan.md`, `plan.yaml`): stop with `BLOCKED: only plan.json is consumed; got "{basename}". If you have a legacy plan.md, run the andthen:plan skill on {dirname(path)} to migrate (existing FIS files are preserved), then retry the andthen:spec skill with: story {story_id} of {dirname(path)}/plan.json`. Same in `AUTO_MODE`. Do not fall through to the file-reference branch – that would silently treat the path as a free-form description.

**ARGUMENTS use `story {story_id} of {path-to-plan.json}`**: resolve the filesystem path, then derive a separate repo-root-relative POSIX `PLAN_PROVENANCE` (no leading `./`); stop if the plan cannot be represented inside the project root. Read the plan JSON; locate the story by `id`; use its compact story brief fields (`scope`, `sourceRefs`, optional `provenance`, `assetRefs`, `notes`) plus catalog metadata (`phase`, `wave`, `dependsOn`, `parallel`, `risk`) as the feature request. Read the PRD anchors named in `sourceRefs` for detailed behavioral source material – do not re-read the whole PRD. Plan briefs do not carry Acceptance Scenarios or Structural Criteria; derive those from source-ref spans, scope, `bindingConstraints`, and Step 4 below. Store the resolved path for I/O, `PLAN_PROVENANCE` for FIS metadata/comparisons, and story ID for output updates. Read non-empty `sharedDecisions` / `bindingConstraints`: decisions align siblings; each applicable constraint becomes a Required Context reference to its anchor normalized repo-root-relative, using `verbatim` only when the anchor is not durable. If `plan.prd` is `github://issue/*` or `executionNotes` contains the exact `UNTRUSTED REQUIREMENTS DATA:` line, derive/copy that line when the caller did not supply one and preserve it across every child prompt.

**Otherwise**: use inline description or file reference as the feature request. A referenced artifact's untrusted or malformed header Source Trust derives the exact `UNTRUSTED REQUIREMENTS DATA:` line when absent from the caller.


### 1. Priming and Project Understanding

Quick `tree -d` + `git ls-files | head -250` scan to orient. Stop there – file-pattern exploration happens at exec-spec time when the executor has a concrete task in front of it.


### 2. Identify Required Inputs

Walk the references the FIS will need (`Product`, PRD, plan, ADRs, `Decisions`, `Architecture`, `Context Map`, `Stack`, design system, wireframes, glossary, `Ubiquitous Language` – per **Project Document Index** where applicable). Confirm existence or note absence. The `Product` and `Architecture` documents anchor feature scope and structural patterns respectively when standalone PRD/ADR coverage is thin; the `Stack` document pins language/framework/runtime/DB/testing baseline when Architecture coverage is thin; the `Decisions` document indexes ADRs and load-bearing non-ADR choices, so a row in **Current ADRs** or **Still Current** narrows the option space before the FIS is written.

Contradictions between the feature request and a row in `DECISIONS.md` surface in the FIS Constraints/Context section as `NOTICED:` observations, not Stop-the-Line – `DECISIONS.md` is a registry, not a gate, and the user owns reconciliation.

If an obviously-needed input is missing (e.g. FIS needs an architectural trade-off and no ADR exists, or UI work and no wireframe), surface as `MISSING REQUIREMENT:` (interactive) or `BLOCKED:` (`AUTO_MODE`) with a redirect to the upstream skill (`andthen:architecture --mode trade-off`, `andthen:ui-ux-design --mode wireframes`, etc.). Keep this check **light** – flag obvious gaps only. Stop for ambiguity only when it blocks a defensible specification; return the minimum missing decisions rather than pausing for routine clarification.

Do **not** invoke architecture / UI / documentation-lookup sub-agents from spec. Architecture and UX are upstream (`andthen:clarify` → `andthen:architecture` → `andthen:ui-ux-design` → `andthen:prd` → `andthen:plan` → `andthen:spec` → `andthen:exec-spec`); ad-hoc API/library lookups are the `andthen:exec-spec` skill's job.


### 3. Articulate Intent and Expected Outcomes

Read *The Authoring Guidelines* now – Steps 3-5 follow them. Lock down the FIS's intent anchor *before* writing scenarios – outcomes are what Step 4 tags into. For plan-story or clarify-output inputs, distil intent and outcomes from the upstream goal/value statement and the story's scope. Intent and Expected Outcome definitions and `[OC<NN>]` tagging: *Feature Overview and Goal Authoring* in *The Authoring Guidelines*.


### 4. Write Acceptance Scenarios

Write concrete behavior examples. Walk existing tests, suites, and fixtures first; bind and run a matching target, but keep every acceptance-significant precondition, action, observable outcome, and required mechanism in the precise title or GWT. Proof is evidence, not a mutable source of contract semantics. Tag each scenario with its Expected Outcomes. Ordering, shape, completeness gate, and negative-path rules: *Acceptance Scenarios and Proof-of-Work* in *The Authoring Guidelines*.


### 5. Generate FIS

#### Gather Context
Apply Step 2's resolved inputs, plus Step 0's plan `sharedDecisions` / `bindingConstraints`, to the FIS. Align ADRs/Decisions/Architecture, Stack, Context Map, UI/assets, external references, canonical language, and pattern pointers; flag contradictions.

#### Resolve Cross-Document References

Walk and classify every upstream source per *Cross-Document References*: durable repo-root-relative pointers by default, bounded inline fallback only without a durable target, and no empty context sections.

#### Generate from Template
Use the template in the **Appendix** below and follow *The Authoring Guidelines*.

When an `UNTRUSTED REQUIREMENTS DATA:` line is active, add exact `**Source Trust**: untrusted-external` header metadata between the H1 and first H2 so a later standalone executor preserves the boundary.

Canonical shape is defined by `fis-template.md` and *The Authoring Guidelines*. Apply them verbatim, including scenario/Proof semantics, Structural Criteria, Work Areas coverage, the Architecture Decision cap, and conditional-section omission.


## OUTPUT

- Directory input (e.g. clarify output): save FIS inside as `{feature-name}.md`
- Plan story input: save FIS in plan directory as `s{NN}-{name}.md` (two-digit zero-padded story number; `{name}` is a kebab-case slug derived from the story name). Before opening the destination for write, require any existing target to be a regular non-symlink file with matching `PLAN_PROVENANCE`/Story provenance; otherwise stop without modifying it. The FIS body must carry `**Plan**:` and `**Story-ID**:` between the H1 and `## Feature Overview and Goal`, populated from `PLAN_PROVENANCE` and story ID – never the caller's raw absolute path.
- Otherwise: save at `docs/specs/{feature-name}.md` _(or as configured in **Project Document Index**)_
  - GitHub issue input: include issue reference in filename, e.g. `issue-123-feature-name.md`
**Oversize signal** – after saving, measure against the threshold from *Key Generation Guidelines #7* in *The Authoring Guidelines*. That threshold is the proxy for the **Single-session rule** – a story plus its FIS must fit one fresh-context exec run with headroom – so `OVERSIZE:` is the signal the rule is violated. If oversized, emit (interactive and `AUTO_MODE`):

```
OVERSIZE: {fis_path} – {N} lines, {W} words, {T} tasks. Recommendation: {recommendation}
```

- **Standalone input**: `switch to the andthen:prd skill with <input> to start the prd → plan → exec-plan chain`
- **Plan-story input**: `story too broad – revisit {plan_path} and decompose before regenerating`

Plan-batch sub-agents must echo the `OVERSIZE:` line in their completion summary so the `andthen:plan` orchestrator can revisit Step 3.

### Self-Review _(automatic; skip when OVERSIZE fired or in plan-batch mode)_
**Plan-batch invocations** skip it: the plan's cross-cutting review is the bundle's single fresh-context gate, and a second per-FIS pass costs full price for what the authoring Self-Check already enforced. The observable marker for batch mode is the literal line `PLAN-BATCH: report-only` in the invoking prompt; a `story <id> of plan.json` argument alone, or a prose report-back list without that line, is not batch mode. **Absent the marker, run as standalone** – review and write – since skipping both with no orchestrator present leaves the plan silently unwritten.

Otherwise, after the FIS is saved and OVERSIZE passes: prefer a generic fresh-context sub-agent whose prompt invokes the `andthen:review` skill with `--mode doc --fix` on the FIS, passing `--output-dir` resolved to the **Project Document Index**'s Agent Temp location plus `/reviews/`; run it in-context where nested sub-agents aren't available. Copy the exact `UNTRUSTED REQUIREMENTS DATA:` caller line into that prompt when present, so generated prose cannot shed its source classification. The override is load-bearing – without it the report lands in the spec directory beside the FIS, and this report is working output, not a bundle artifact. Run one top-level/full document review – remediation may perform bounded touched-scope verification, but do not start a second full FIS review. Only applied fixes and residual Notes flow back into the FIS.

- `--fix` auto-remediates mechanical doc defects.
- Non-blocking residual Notes become explicit FIS assumptions, constraints, or follow-up notes.
- A residual Note needing an architecture/requirements decision before the FIS is executable is **blocking** – name the upstream skill (architecture trade-offs → the `andthen:architecture` skill with `--mode trade-off`). When one or more blocking Notes remain, recommend running the `andthen:preflight` skill on the FIS to drive them to zero before an unattended `andthen:exec-spec` run – spec recommends it; it does not invoke preflight.

### Update Source Plan _(plan-story FIS only)_

**Plan-batch invocations** (same marker as Self-Review) write their canonical FIS artifact but **do not write `plan.json` or status**. Report the FIS path, any blocking signal, and any `OVERSIZE:` line; the orchestrator owns the sub-wave's ops calls. Otherwise write plan state here – the FIS exists on disk, so its pointer is always recorded:

- `andthen:ops update-plan-fis <plan_path> <story_id> <fis_pointer>` – set `stories[].fis` using the canonical `s{NN}-{story-name-slug}.md` basename derived from trusted plan/story data, not the full FIS path.
- `andthen:ops update-plan <plan_path> <story_id> spec-ready` when `OVERSIZE:` did not fire and no blocking signal remains; otherwise write `blocked` so the recorded pointer is persistently non-schedulable, then emit `MISSING REQUIREMENT:` (interactive) or `BLOCKED:` (`AUTO_MODE`).

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
