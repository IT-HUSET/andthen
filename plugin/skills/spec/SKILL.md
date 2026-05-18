---
description: Use when the user wants to generate a new spec or FIS before implementation for a feature or plan story. Do not use when the user wants to execute or implement an existing spec or FIS. Produces an execution-sized FIS; if the draft exceeds size thresholds, saves it anyway and warns – recommending the `andthen:prd → andthen:plan → andthen:exec-plan` chain for standalone inputs, or upstream plan decomposition for plan-story inputs. Trigger on 'create a spec for this', 'create a FIS for this', 'write a spec', 'write a FIS', 'specify this feature'.
argument-hint: "[--visual] [--auto|--headless] <description | @<requirements-file> | story <story-id> of <path-to-plan.json>>"
---

# Generate Feature Implementation Specification


Given a feature request, generate an execution-sized Feature Implementation Specification (FIS). One spec → one FIS. When a feature is too large for a single FIS, the skill emits an `OVERSIZE:` signal and redirects: standalone inputs switch to the `andthen:prd → andthen:plan → andthen:exec-plan` chain (the `andthen:plan` skill is the sole writer of `plan.json` per the schema's write-authority model); plan-story inputs need upstream plan decomposition before regenerating.


## VARIABLES

ARGUMENTS: $ARGUMENTS (strip any flag tokens like `--visual`, `--auto`, or `--headless` before interpreting the remainder as the description / `@file` / `story <id> of <plan>`)

### Optional Flags
- `--visual` → VISUAL_MODE: after the FIS is saved (and any plan-status updates land), invoke the `andthen:visualize` skill on the produced FIS. Convenience handoff – the visualizer owns HTML rendering, note export, browser-open behavior, and `.agent_temp/visual-review/` output.
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- **Fully read and understand all project rules, guardrails, principles and guidelines (as defined in `CLAUDE.md` / `AGENTS.md` and other referenced files) before starting work.**
- Require `ARGUMENTS`. Stop if missing.
- **Spec generation only** – no code changes, commits, or modifications.
- Agents executing the FIS only get the context you provide. Include all necessary documentation, examples, and references.
- Read the `Learnings` document (see **Project Document Index**) before starting, if it exists.
- **Automation rules** (headless-first, `--auto` / `--headless` strict mode, `--auto` propagation): see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). Spec-specific `BLOCKED:` triggers: missing input, unreadable sources, incompatible artifacts, ambiguity where no defensible FIS can be written.
- **Visual review is a post-save handoff.** In `AUTO_MODE`, run it only when `--visual` is present. When present, complete the normal FIS save (and any `andthen:ops` plan updates for plan-story inputs) first, then invoke the `andthen:visualize` skill on the produced FIS; the visualizer owns HTML rendering, note export, browser-open behavior, and `.agent_temp/visual-review/` output.


## GOTCHAS

**Generating a FIS without orienting in the codebase first** – the quick codebase scan in Step 1 must precede specification (Step 5), but deep file-pattern exploration waits until `exec-spec`.

**Writing scenarios before intent is locked down** – Step 3 (Articulate Intent and Expected Outcomes) must precede Step 4 (Write Acceptance Scenarios). Scenarios are concrete BDD examples of how Expected Outcomes are met; without outcomes named first, scenarios drift into describing implementation paths rather than success conditions.

**Undefined behavior** – surface ambiguity and missing requirements rather than silently inventing answers. Emit named output blocks:
- `CONFUSION:` – ambiguity + labeled options + `-> Which approach?`
- `NOTICED BUT NOT TOUCHING:` – out-of-scope observations + `-> Want me to create tasks?`
- `MISSING REQUIREMENT:` – undefined behavior + labeled options + `-> Which behavior?`

In `AUTO_MODE`, do not use arrow prompts. Choose the most conservative defensible option and record it as an assumption in the FIS; if no defensible option exists, stop with `BLOCKED:` and list the minimum missing decisions.

**Describing code changes instead of outcomes** – tasks should state what must be TRUE when done, not what code to write. Bad: "Create lib/auth.ts with login() and logout()". Good: "Auth module with login/logout; follow pattern at lib/users.ts#getUser".

**Acceptance criteria that can't be verified programmatically** – every criterion needs a concrete verify command or observable check. If you can't write the scenario's **Then** clause, you don't understand the requirement yet.

**Acceptance Scenarios that describe implementation, not behavior** – scenarios should use Given/When/Then to describe observable outcomes from the user's or system's perspective, not internal code steps. Bad: "Given a new AuthService class, When login() is called...". Good: "Given valid credentials, When the user submits login, Then a session token is returned."

**Over-researching** – do not research what `clarify`, `prd`, `architecture`, or `ui-ux-design` already produced upstream. The spec skill identifies which upstream inputs are needed and inlines the load-bearing spans into Required Context – it is not a new research pass. External API/library lookups are deferred to `exec-spec`'s proactive documentation-lookup sub-agent. A spec that reads like a diff is too detailed. A 30-line minimal FIS is fine; zero FIS is not. Size threshold and oversize handling: see *Key Generation Guidelines #7* in [the authoring guidelines](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md) (referenced below as *The Authoring Guidelines*).

**Generic "What We're NOT Doing" section** – use it to record real non-goals or deferrals with reasons, not filler bullets.


## WORKFLOW

### 0. Parse Input & Get Requirements

**If ARGUMENTS is a directory with `requirements-clarification.md`** (from the `andthen:clarify` skill): read it; use clarified scope, functional requirements, edge cases, acceptance outcomes, design decisions, wireframes, and any explicit non-goals / deferred items as the feature request. Skip or reduce research phases (clarify already did discovery). Only do codebase research and any external/API research the requirements reference but haven't investigated.

**If ARGUMENTS match `story {story_id} of {path}` AND `path`'s basename matches `plan.*` but is not `plan.json`** (e.g. `plan.md`, `plan.jsom`, `plan.yaml`): stop with `BLOCKED: only plan.json is consumed; got "{basename}". If you have a legacy plan.md, run /andthen:plan {dirname(path)} to migrate (existing FIS files are preserved), then retry: /andthen:spec story {story_id} of {dirname(path)}/plan.json`. Same in `AUTO_MODE`. Do not fall through to the file-reference branch – that would silently treat the path as a free-form feature description.

**If ARGUMENTS use `story {story_id} of {path-to-plan.json}`**: read the plan JSON; locate the story by `id`; use its compact story brief fields (`scope`, `sourceRefs`, plus optional `provenance`, `assetRefs`, `notes`) together with its catalog metadata (`phase`, `wave`, `dependsOn`, `parallel`, `risk`) as the feature request. Read the PRD anchors named in `sourceRefs` and use those spans as detailed behavioral source material; do not re-read the whole PRD. Plan story briefs intentionally do not carry full Acceptance Scenarios or Structural Criteria; derive those in the FIS from the source-ref spans, scope, `bindingConstraints`, and scenario-writing workflow below. Store plan path and story ID for output updates. If `plan.json` carries non-empty `sharedDecisions` and/or `bindingConstraints` arrays, read them – `sharedDecisions` inform architectural alignment with sibling stories; `bindingConstraints` flow unchanged into FIS Required Context blocks (each entry's `verbatim` becomes a Required Context block with the entry's `anchor` as the source pin).

**Otherwise**: use inline description or file reference as the feature request.


### 1. Priming and Project Understanding

Quick `tree -d` + `git ls-files | head -250` scan to orient. Stop there – file-pattern exploration happens at exec-spec time when the executor has a concrete task in front of it.


### 2. Identify Required Inputs

Walk the references the FIS will need (the `Product` document, PRD, plan, ADRs, the `Architecture` document, design system, wireframes, glossary, `Ubiquitous Language` – all per **Project Document Index** where applicable). For each, confirm the input exists or note its absence. The `Product` document and `Architecture` document anchor feature scope and structural patterns respectively when standalone PRD/ADR coverage is thin.

If an obviously-needed input is missing – e.g., the FIS would require an architectural trade-off and no ADR exists, or UI work and no wireframe – surface as `MISSING REQUIREMENT:` (interactive) or `BLOCKED:` (`AUTO_MODE`) with a redirect to the upstream skill (`andthen:architecture --mode trade-off`, `andthen:ui-ux-design --mode wireframes`, etc.). Keep this check **light** – flag obvious gaps, not every conceivable input.

Do **not** invoke architecture / UI / documentation-lookup sub-agents from spec. Architecture and UX are upstream skills (`andthen:clarify` → `andthen:architecture` → `andthen:ui-ux-design` → `andthen:prd` → `andthen:plan` → `andthen:spec` → `andthen:exec-spec`); ad-hoc API/library lookups are exec-spec's responsibility via its proactive documentation-lookup sub-agent.

Only stop for ambiguity when it blocks a defensible specification. In that case, return the minimum missing decisions required rather than pausing for routine clarification.


### 3. Articulate Intent and Expected Outcomes

Lock down the FIS's intent anchor *before* writing scenarios; the outcomes are what Step 4's scenarios will tag into. For plan-story or clarify-output inputs, distil intent and outcomes from the upstream goal/value statement and the story's scope rather than authoring from scratch. See *Feature Overview and Goal Authoring* in *The Authoring Guidelines* for the full rule set.

- **Intent** – one sentence: why this feature exists, the problem it solves or the user/business value it unlocks.
- **Expected Outcomes** – 2-4 user- or business-observable success conditions, each `[OC<NN>]`-tagged.


### 4. Write Acceptance Scenarios

Write the **Acceptance Scenarios** section next. Scenarios are concrete examples of expected behavior (BDD-style Given/When/Then) that serve triple duty: requirement, test specification, and proof-of-work contract. Each scenario tags the Expected Outcome(s) from Step 3 it exemplifies via `[OC<NN>]` – this closes the chain Intent → Outcomes → Scenarios. Start with the happy path, then edge cases, then error cases. 3-7 scenarios is the sweet spot. After drafting, apply the **negative-path checklist** from *The Authoring Guidelines* – verify coverage for omitted optional inputs, no-match selectors/filters, and rejection paths. See *Scenario Authoring Principles* and *Feature Overview and Goal Authoring* (Outcome ↔ Scenario coverage rule) for detailed guidance.

**Emit the canonical scenario shape** per *Acceptance Scenarios and Proof-of-Work* in *The Authoring Guidelines* – top-level checkbox with a bold scenario-ID label carrying outcome-tag set then task-tag set, followed by nested Given/When/Then; the template carries the worked examples.

**Lock down proof-of-work**: every Acceptance Scenario's nested Given/When/Then IS the proof contract; Structural Criteria use task Verify lines.


### 5. Generate FIS

#### Gather Context
- ADRs and the `Architecture` document (see **Project Document Index**); `file#symbol` references for patterns to follow (see *Cross-Document References* rule #1 for the symbol-anchor ladder)
- UI wireframes/mockups; design system references; external documentation URLs
- `Ubiquitous Language` document (see **Project Document Index**) – use canonical terms; flag any contradictions
- For plan-story inputs: `sharedDecisions` and `bindingConstraints` arrays from `plan.json` (when non-empty) – `bindingConstraints[].verbatim` PRD spans become Required Context blocks with the entry's `anchor` as the source pin

#### Resolve Cross-Document References

Walk every upstream document the spec depends on (PRD, plan, ADRs, project guidelines like `Ubiquitous Language` / coding standards / security rules, glossary) and resolve each reference into one of two tiers per *Cross-Document References* in *The Authoring Guidelines*:

- **Required Context** – load-bearing spans inlined verbatim, source-pinned with `<!-- source: -->` and `<!-- extracted: -->` comments. Inline budget and pin format live in the same *Cross-Document References* section.
- **Deeper Context** – supplementary anchored pointers. Validate each anchor resolves before finalizing.

The walk is mandatory; the sections themselves are optional based on what's found. Omit Required Context entirely when no load-bearing upstream spans surface; omit Deeper Context when no supplementary pointers are worth surfacing. A truly standalone feature request with no PRD/plan/ADR/guideline upstream legitimately produces neither section – but only after the walk confirms there's nothing to inline or anchor.

A bare "see the plan" without an anchor or inlined content is not acceptable. The author saw the source; the author names what matters. Code-pattern `file#symbol` pointers stay inside task descriptions or the `Code Patterns & External References` section – they're not Required/Deeper Context material.

#### Generate from Template
Use the template in the **Appendix** below. Then read and follow *The Authoring Guidelines*.

The emitted FIS uses the canonical shape:

- `## Acceptance Scenarios` – behavioral requirements, each in the canonical checkbox shape from Step 4 (no `### S<NN>` headers).
- `## Structural Criteria` – non-behavioral proof requirements (regression guards, invariants); each checkbox is proved by a task Verify line.
- `### Work Areas` under the `## Scope & Boundaries` parent – 3-7 bullets inventorying components, files, or surfaces being changed. Each Work Area maps to at least one task or scenario.
- `## Architecture Decision` capped at 3-4 lines max (one `**Approach**:` line, optional `**Why this over alternatives**:` line). Longer trade-off analysis routes upstream to the `andthen:architecture` skill in `--mode trade-off`.
- Every always-present template section ships in the emitted FIS. Sections with a "**Leave empty** when…" blockquote prompt (`## Technical Overview`, `### Testing Strategy`, `### Validation`, `### Execution Contract`, `## Final Validation Checklist`) stay empty in the typical case – fill only when the named condition in the prompt actually applies. Resist auto-filling; empty is the default. `## Required Context` and `## Deeper Context` are content-conditional omits – drop the heading entirely when there are no upstream sources to inline (or no supplementary pointers worth surfacing), per the template's "**Omit this entire section**" prompts.

> **Optional**: Invoke the `andthen:review --mode doc` skill for thorough validation (recommended for large/complex features). This keeps pre-implementation FIS review on the document-review path.


## OUTPUT

- Directory input (e.g. clarify output): save FIS inside as `{feature-name}.md`
- Plan story input: save FIS in plan directory as `s{NN}-{name}.md` (two-digit zero-padded story number; `{name}` is a kebab-case slug derived from the story name). The FIS body must carry `**Plan**:` and `**Story-ID**:` between the H1 and `## Feature Overview and Goal`, populated from the source plan path and story ID.
- Otherwise: save at `docs/specs/{feature-name}.md` _(or as configured in **Project Document Index**)_
  - GitHub issue input: include issue reference in filename, e.g. `issue-123-feature-name.md`
- **Update source plan** – if this spec was created for a plan story:
  - Invoke `andthen:ops update-plan-fis <plan_path> <story_id> <fis_path>` to set `stories[].fis`
  - Invoke `andthen:ops update-plan <plan_path> <story_id> spec-ready` to advance status

**Oversize signal** – after saving, measure the FIS against the threshold from *Key Generation Guidelines #7* in *The Authoring Guidelines* (>700 lines or >18 tasks). If oversized, emit a structured line as part of the artifact output (printed in both interactive and `AUTO_MODE`):

```
OVERSIZE: {fis_path} – {N} lines, {T} tasks. Recommendation: {recommendation}
```

- **Standalone input** recommendation: `switch to /andthen:prd <input> to start the prd → plan → exec-plan chain`
- **Plan-story input** recommendation: `story too broad – revisit {plan_path} and decompose before regenerating`

Plan-batch sub-agents must echo the `OVERSIZE:` line back in their completion summary so the `andthen:plan` orchestrator can revisit Step 3 for the over-broad story.

### Visual Review _(if --visual)_
After the FIS is saved, any plan-status updates land, and the OVERSIZE check has fired, invoke the `andthen:visualize` skill on the produced FIS path. Print both the FIS path and the visualizer's output path. **Skip when `OVERSIZE:` fired** – the FIS is about to be discarded (standalone → switch chain) or regenerated upstream (plan-story → decompose); print `--visual skipped: OVERSIZE` instead so the user knows the flag was honored but suppressed.

---


## FOLLOW-UP ACTIONS

Skip this section when `AUTO_MODE=true`; print only the generated artifact paths, the `OVERSIZE:` line if applicable, and downstream command shape.

After the FIS is saved, suggest:

1. **Implement the FIS**: Invoke the `andthen:exec-spec` skill.
2. **Review first**: Invoke the `andthen:review` skill with `--mode doc` on the FIS before implementation.
3. **Review visually**: Run `andthen:visualize <fis-path>` to spot scenario/task coverage and verify-line issues a markdown view obscures.

> **Session tip**: The `andthen:exec-spec` skill is context-intensive (it runs the full implementation + verification loop). Start a **clean session** for best results.

If the `OVERSIZE:` signal fired, expand the recommendation conversationally: standalone inputs should switch to the `andthen:prd → andthen:plan → andthen:exec-plan` chain; plan-story inputs need upstream plan decomposition before regenerating.


---


## Appendix: FIS Template

**USE THE TEMPLATE**: Read and use the template at [`fis-template.md`](${CLAUDE_PLUGIN_ROOT}/references/fis-template.md) to generate the Feature Implementation Specification.
