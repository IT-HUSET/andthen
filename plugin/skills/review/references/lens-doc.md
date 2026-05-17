# Lens: Document Review

Rubric for reviewing specifications, implementation plans, PRDs, technical designs, or other requirement documents. Load this reference when running `andthen:review --mode doc` or when the Mixed mode's doc sub-pass runs.


## Scope

Specs, FIS, PRDs, plans, ADRs, design docs, prompts, or other written artifacts. Locate the document(s) or focus area from arguments or context. Build context: project type, stage, goals, constraints, existing patterns, and any related docs. Read extra docs only when they materially affect correctness.

Favor **proportional review** – a prototype, library, or MVP should not be judged like an enterprise platform. Favor simplicity – flag over-engineering and recommend the smallest solution that meets the real need.


## Review Dimensions

Review the document through these lenses and record only issues relevant to the project's scale:

- **Completeness**: functional requirements, important non-functional requirements, integrations, edge cases, testing, and operations where applicable
- **Clarity**: vague language, contradictions, missing details, inconsistent naming, unclear acceptance criteria, or unclear implementation handoff
- **Technical accuracy**: outdated APIs, deprecated approaches, infeasible designs, missing standards alignment. When the document names concrete frameworks, APIs, libraries, or version-bound patterns, verify claims against authoritative documentation by consulting the project's `## Documentation Lookup Tools` section; Claude Code plugin users may invoke the `andthen:documentation-lookup` agent directly.
- **Scope and architecture**: explicit in/out-of-scope boundaries, phase boundaries, architecture soundness, and signs of disproportionate complexity
- **Stakeholder fit**: user needs, success criteria, UX/error-state coverage

If the document is a FIS, verify it still follows the structure and intent-first authoring rules from [`fis-authoring-guidelines.md`](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md).


## Critic Sub-Lens (Always On)

Run `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md` against the document as an always-on sub-lens. Attack ambiguous requirements, missing unhappy paths, hidden implementation guesses, contradiction-prone terminology, and places where an implementer would have to infer behavior not stated in the artifact.

When available, use the installed `review-critic` custom agent for the Critic pass, but still supply a read-first task prompt for `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md`, `${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md`, and `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md`. If unavailable, use a generic fresh-context sub-agent with the same read-first instruction. Inline fallback must include `Critic Coverage` in the report.

Merge Critic findings into the normal document review findings before calibration and filtering. Do not treat the Critic as a separate mode or an optional escalation.


## Calibration

Calibrate severity with `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` (universal) and `doc-review-calibration.md` (doc-specific). Load `${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md` while running the always-on Critic sub-lens; use the document-specific calibration to assign final severity after findings are collected. Use the unified severity scale defined in `review-verdict.md`: CRITICAL / HIGH / MEDIUM / LOW.


## FIS Upstream-Context Handling

When a FIS is in scope: treat `Required Context` blocks as the authoritative upstream intent – do not re-read source documents just to reconfirm inlined content. For `Deeper Context` anchors that are load-bearing for a finding, verify the anchor resolves in the source and warn (do not stop) on broken anchors. If a `Required Context` block appears to no longer match the current source, that is a doc-review finding (MEDIUM by default – spec should be re-run against the updated source), not an execution blocker.

**Legacy FIS fallback**: a FIS without `Required Context` / `Deeper Context` sections predates them. Fall back to whatever upstream-reference structures it uses: the old `## References & Constraints` heading and its `### Documentation & References` table (rows typed `file|doc|url|wire`), or prose mentions. Do not flag the absence of these sections as a defect on legacy FIS files.


## Findings Filter

> **Findings Filter**: see [`lens-findings-filter.md`](lens-findings-filter.md).

Lens-specific placeholder values:
- **Role**: `Findings Filter reviewing document review findings`
- **Skill calibration**: `doc-review-calibration.md`
- **Context block**: `Document type, path, project scale/stage context from discovery.`
- **Questions**: Is this a real gap given project scale? Is severity proportional? Is it addressed elsewhere? Would it mislead or block implementation?
- **Findings payload**: `{all findings}`

Apply verdicts before writing the final report.


## Findings Output

Use the unified severity scale from `review-verdict.md`: CRITICAL / HIGH / MEDIUM / LOW.

**Readiness label**: `Ready` / `Needs Minor Updates` / `Needs Significant Rework` / `Not Ready` – per the verdict reference (doc-mode readiness scale preserved).


## Downstream Routing

After producing findings, classify the dominant pattern and name the right downstream skill in the report's **Recommended Next Action** section.

**Document maturity signal** – distinguishes "draft" from "mature" via concrete markers, in priority order:
1. PRD – always draft for routing purposes (its job is to be clarified into a plan/spec)
2. Plan or FIS with a `Status:` field whose value is pre-execution (e.g. `draft`, `ready-for-review`, `ready-for-execution`) – draft until the value indicates execution has started or completed
3. Plan with no story checkboxes ticked, or FIS with no implementation work landed in the codebase – draft
4. Otherwise – mature

**Pattern precedence** – a single document can match more than one pattern; apply the first that fires:
1. **Requirement-gap cluster** – any "unanswered question / undefined behavior" finding (regardless of severity), OR ≥2 Completeness / Stakeholder Fit findings at MEDIUM or higher. Fires only on draft documents (per maturity signal). Route → the `andthen:clarify` skill. The answers don't exist yet; mechanical edits would paper over the gap. Phrase the recommendation concretely, naming both the gap areas and the doc path, e.g. *"Significant requirement gaps in <areas> in `<doc-path>` – run `andthen:clarify` against `<doc-path>` to resolve them before re-running spec/exec."*
2. **Defect cluster** – clarity, technical accuracy, structural/anchor defects. Route → the `andthen:remediate-findings` skill (or let `--fix` invoke it). Fixes are mechanical edits to the doc.
3. **Mature spec/FIS with requirement-fit concerns** – same triggers as the requirement-gap cluster but on a mature document. Route → the `andthen:remediate-findings` skill. Re-running the `andthen:clarify` skill on a near-final FIS produces churn; encode the concerns as targeted edits instead.

**Interactivity contract** – this reference states which branch is interactive; the `SKILL.md` `FOLLOW-UP ACTIONS` step owns the gate. The clarify branch is interactive by nature (the `andthen:clarify` skill cannot run headless), so:
- Under `AUTO_MODE=off`, the SKILL.md `FOLLOW-UP ACTIONS` step prompts the user to run the `andthen:clarify` skill inline against the listed gaps.
- Under `AUTO_MODE=on`, the recommendation appears only in the report's **Recommended Next Action** – never prompt and never invoke the `andthen:clarify` skill automatically. The orchestrator decides.


## Report Sections

```markdown
## Executive Summary
Overall assessment, high-level findings, Findings Filter stats, key recommendations

## Scope and Context

## Completeness Analysis

## Clarity Issues

## Technical Accuracy

## Edge Cases and Risks

## Architecture Assessment

## Over-Engineering Analysis

## Stakeholder Alignment

## Critic Coverage
[Ambiguities, unhappy paths, hidden implementation guesses, and contradiction-prone terms attacked. Required when Critic ran inline.]

## Prioritized Recommendations
Critical / High / Medium / Low

## Readiness Assessment
Ready / Needs Minor Updates / Needs Significant Rework / Not Ready

## Recommended Next Action
One line. Name the specific skill (`andthen:clarify`, `andthen:remediate-findings`, or none), the doc path, and the trigger pattern. Do **not** duplicate the Prioritized Recommendations list – this section records the routing decision, not the findings. Per **Downstream Routing** above.
```


## Report Output Conventions

Filename and directory resolve per [`review-report-location.md`](${CLAUDE_PLUGIN_ROOT}/references/review-report-location.md). This lens contributes:
- **`<feature-name>` token**: the spec/FIS/PRD/plan name (e.g. `payments-prd`, `s03-checkout-fis`)
- **Report suffix**: `doc-review` (canonical source: the `andthen:review` skill's mode table)
- **Target nature**: doc artifact. Tier-2 "next to target" remains enabled – when no spec directory resolves, doc reviews co-locate with the document under review.
