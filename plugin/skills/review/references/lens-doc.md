# Lens: Document Review

Rubric for reviewing requirement and design documents (spec, FIS, PRD, plan, ADR). Load this reference when running `andthen:review --mode doc` or when the Mixed mode's doc sub-pass runs.

## Contents
- Scope · Review Dimensions · Critic Sub-Lens · Calibration
- FIS Upstream-Context Handling · Findings Filter · Findings Output
- Downstream Routing · Report Sections · Report Output Conventions


## Scope

Specs, FIS, PRDs, plans, ADRs, design docs, prompts, or other written artifacts. Locate the document(s) or focus area from arguments or context. Build context: project type, stage, goals, constraints, existing patterns, and any related docs. Read extra docs only when they materially affect correctness.

Favor **proportional review** – judge a prototype/library/MVP by its scale, not an enterprise platform's. Flag over-engineering; recommend the smallest solution meeting the real need.


## Review Dimensions

Review the document through these lenses and record only issues relevant to the project's scale:

- **Completeness**: functional requirements, important non-functional requirements, integrations, edge cases, testing, and operations where applicable
- **Clarity**: vague language, contradictions, missing details, inconsistent naming, unclear acceptance criteria, or unclear implementation handoff
- **Technical accuracy**: outdated APIs, deprecated approaches, infeasible designs, missing standards alignment. When the document names concrete frameworks, APIs, libraries, or version-bound patterns, verify claims against authoritative documentation by consulting the project's `## Documentation Lookup Tools` section or the dedicated `documentation-lookup` agent when available.
- **Scope and architecture**: explicit in/out-of-scope boundaries, phase boundaries, architecture soundness, evidence for structural choices, and signs of disproportionate complexity
- **Stakeholder fit**: user needs, success criteria, UX/error-state coverage
- **FIS / spec quality** _(the primary job when a FIS or spec is reviewed before implementation)_: the FIS is the shared implementer/reviewer contract, so apply [`fis-authoring-guidelines.md`](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md) as acceptance gates, not a structure checklist. Attack scenario falsifiability – every Expected Outcome traces to ≥1 scenario and back, each Then is observable rather than an implementation detail, edge/failure paths are scenarios not prose. Decisive test: when a requirement *is* a mechanism (an LLM/agent turn, specific algorithm, external call), at least one scenario's Then must assert a mechanism-distinguishing observable a stub, hardcoded value, or verbatim copy would fail – a scenario a trivial substitute could pass does not specify the feature and is a finding.
- **FIS architecture claims**: challenge unsupported structural prescriptions, missing trade-off evidence where alternatives matter, over-specific implementation direction, and standalone-FIS assumptions presented as facts. If no Architecture/ADR/Decisions baseline exists, architectural prescriptions need code-pattern evidence or must be framed as assumptions / execution-time discovery, not settled design.
- **Fidelity** _(post-implementation – code already landed)_: does the artifact still describe what was built, including the Intent, Expected Outcomes, mechanism assumptions, and ADR-backed decisions? If not, the finding is spec-side – classify it `spec-stale`, `design-changed`, or `ambiguous-intent` so reconciliation is explicit (a wrong implementation is `code-defect`, handled by the gap lens, not here).

**Doc-fix routing**: a deterministic, mechanical doc-quality defect classes as `code-defect` (despite the name), so `--fix` can safely remediate it; reserve `ambiguous-intent` for when the document lacks the decision needed to choose the correct requirement or design.


## Critic Sub-Lens (Always On)

Run `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md` against the document as an always-on sub-lens. Attack ambiguous requirements, missing unhappy paths, hidden implementation guesses, contradiction-prone terminology, and places where an implementer would have to infer behavior not stated in the artifact.

Dispatch per `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md` § Sub-agent dispatch (prefer the `review-critic` agent with a read-first task prompt for the three calibration files; else a generic fresh-context sub-agent; inline fallback requires a `Critic Coverage` note).

Merge Critic findings into the normal document review findings before calibration and filtering. Do not treat the Critic as a separate mode or an optional escalation.


## Calibration

Calibrate severity with `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` (universal) and `doc-review-calibration.md` (doc-specific). Load `${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md` while running the always-on Critic sub-lens; use the document-specific calibration to assign final severity after findings are collected. Use the unified severity scale defined in `review-verdict.md`: CRITICAL / HIGH / MEDIUM / LOW.


## FIS Upstream-Context Handling

When a FIS is in scope, apply [`fis-context-handling.md`](fis-context-handling.md) (Required/Deeper Context rules, legacy-FIS fallback).


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

**Severity scale**: per `review-verdict.md` (see Calibration).

**Readiness label**: four-value scale per `review-verdict.md` (doc-mode readiness scale preserved); rendered in the Readiness Assessment report section.


## Downstream Routing

After producing findings, classify the dominant pattern and name the right downstream skill in the report's **Recommended Next Action** section.

**Document maturity signal** – distinguishes "draft" from "mature" via concrete markers, in priority order:
1. PRD – always draft for routing purposes (its job is to be clarified into a plan/spec)
2. Plan or FIS with a `Status:` field whose value is pre-execution (e.g. `draft`, `ready-for-review`, `ready-for-execution`) – draft until the value indicates execution has started or completed
3. Plan with no story checkboxes ticked, or FIS with no implementation work landed in the codebase – draft
4. Otherwise – mature

**Pattern precedence** – a single document can match more than one pattern; apply the first that fires:
1. **Architecture-decision gap** – a FIS/spec makes or requires a structural choice that cannot be mechanically corrected because the Architecture/ADR/Decisions/code-pattern evidence is absent or contested. Route → the `andthen:architecture` skill with `--mode trade-off`. Do not auto-design inside doc review; name the missing decision and the FIS section it blocks.
2. **Requirement-gap cluster** – any "unanswered question / undefined behavior" finding (regardless of severity), OR ≥2 Completeness / Stakeholder Fit findings at MEDIUM or higher. Fires only on draft documents (per maturity signal). Route → the `andthen:clarify` skill. The answers don't exist yet; mechanical edits would paper over the gap. Phrase the recommendation concretely, naming both the gap areas and the doc path, e.g. *"Significant requirement gaps in <areas> in `<doc-path>` – run `andthen:clarify` against `<doc-path>` to resolve them before re-running spec/exec."*
3. **Defect cluster** – clarity, technical accuracy, structural/anchor defects. Route → the `andthen:remediate-findings` skill (or let `--fix` invoke it). Fixes are mechanical edits to the doc.
4. **Mature spec/FIS with requirement-fit concerns** – same triggers as the requirement-gap cluster but on a mature document. Route → the `andthen:remediate-findings` skill. Re-running the `andthen:clarify` skill on a near-final FIS produces churn; encode the concerns as targeted edits instead.

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
