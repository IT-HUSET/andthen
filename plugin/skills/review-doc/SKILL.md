---
description: Review specifications, plans, PRDs, requirement documents, or other documentation for completeness, clarity, edge cases, and technical accuracy. Generate detailed report with prioritized findings and readiness assessment.
context: fork
agent: general-purpose
user-invocable: true
---

# Review Spec, Plan, Requirements, or Other Documents

Thoroughly review specifications, implementation plans, PRDs, technical designs, or other requirement documents to determine whether they are complete, clear, proportionate, and ready for implementation.

## VARIABLES
SPEC_PATH_OR_FOCUS: $ARGUMENTS

## INSTRUCTIONS
- Make sure `SPEC_PATH_OR_FOCUS` is provided; otherwise stop and ask for it.
- Read the Workflow Rules, Guardrails, and relevant project guidelines before starting.
- Read-only review. Do not modify the reviewed document.
- Calibrate severity with `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` and `${CLAUDE_PLUGIN_ROOT}/skills/review-doc/references/doc-review-calibration.md`.
- Favor proportional review. A prototype, library, or MVP should not be judged like an enterprise platform.
- Favor simplicity. Flag over-engineering and recommend the smallest solution that meets the real need.

## GOTCHAS
- Reviewing at the wrong depth for the document's maturity
- Confusing `review-doc` with `review-gap`

## WORKFLOW

### 1. Discovery and Context
1. Locate the document(s) or focus area from `SPEC_PATH_OR_FOCUS`.
2. Build context: project type, stage, goals, constraints, existing patterns, and any related docs.
3. Read extra docs only when they materially affect correctness.

**Gate**: Scope, context, and project scale are clear

### 2. Review Pass
Review the document through these lenses and record only issues relevant to the project's scale:
- **Completeness**: functional requirements, important non-functional requirements, integrations, edge cases, testing, and operations where applicable
- **Clarity**: vague language, contradictions, missing details, inconsistent naming, unclear acceptance criteria, or unclear implementation handoff
- **Technical accuracy**: outdated APIs, deprecated approaches, infeasible designs, missing standards alignment. When the document names concrete frameworks, APIs, libraries, or version-bound patterns, verify claims against authoritative documentation (use the `andthen:documentation-lookup` agent if available)
- **Scope and architecture**: explicit in/out-of-scope boundaries, phase boundaries, architecture soundness, and signs of disproportionate complexity
- **Stakeholder fit**: user needs, success criteria, UX/error-state coverage

If the document is a FIS, verify it still follows the `andthen:spec` structure.

**Gate**: Findings identified across all relevant dimensions

### 3. Adversarial Challenge
Use `${CLAUDE_PLUGIN_ROOT}/references/adversarial-challenge.md` (`Generic Findings-Challenger Template`) with:
- **Role**: `Adversarial Challenger reviewing document review findings`
- **Shared calibration**: `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md`
- **Skill calibration**: `${CLAUDE_PLUGIN_ROOT}/skills/review-doc/references/doc-review-calibration.md`
- **Context block**: `The document being reviewed is a {document type} for a {project description and scale}. Document under review: {path to document}. Project scale/stage context: {from discovery}.`
- **Questions**:
  1. `Is this a real gap, or irrelevant given the project's scale, stage, and goals?`
  2. `Is the severity proportional to the document's purpose and audience?`
  3. `Is this addressed elsewhere in the document or project context?`
  4. `Would this actually mislead or block implementation?`
- **Verdicts**: `VALIDATED`, `DOWNGRADED`, `WITHDRAWN`
- **Findings payload**: `{all findings}`

Apply verdicts before writing the final report.

**Gate**: Findings challenged and filtered

### 4. Report
Generate a markdown report using only surviving findings:
- **Executive Summary**: overall assessment, high-level findings, challenge stats, key recommendations
- **Scope and Context**
- **Completeness Analysis**
- **Clarity Issues**
- **Technical Accuracy**
- **Edge Cases and Risks**
- **Architecture Assessment**
- **Over-Engineering Analysis**
- **Stakeholder Alignment**
- **Prioritized Recommendations**: Critical/High/Medium/Low
- **Readiness Assessment**: Ready / Needs Minor Updates / Needs Significant Rework / Not Ready

**Report output conventions**: Follow `${CLAUDE_PLUGIN_ROOT}/references/report-output-conventions.md` with:
- **Report suffix**: `doc-review`
- **Scope placeholder**: `spec-name`
- **Spec-directory rule**: the document being reviewed lives in a spec/FIS directory or has an associated spec directory from the Project Document Index
- **Target-directory rule**: otherwise, store the report in the same directory as the document being reviewed

## FOLLOW-UP ACTIONS
After the report, ask whether the user wants to:
1. Update the document based on findings
2. Focus on a narrower area
3. Proceed to implementation
4. Escalate critical issues for clarification
