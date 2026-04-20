# Lens: Document Review

Rubric for reviewing specifications, implementation plans, PRDs, technical designs, or other requirement documents. Load this reference when running `andthen:review --mode doc` or when the Mixed mode's doc sub-pass runs.


## Scope

Specs, FIS, PRDs, plans, ADRs, design docs, prompts, or other written artifacts. Locate the document(s) or focus area from arguments or context. Build context: project type, stage, goals, constraints, existing patterns, and any related docs. Read extra docs only when they materially affect correctness.

Favor **proportional review** — a prototype, library, or MVP should not be judged like an enterprise platform. Favor simplicity — flag over-engineering and recommend the smallest solution that meets the real need.


## Review Dimensions

Review the document through these lenses and record only issues relevant to the project's scale:

- **Completeness**: functional requirements, important non-functional requirements, integrations, edge cases, testing, and operations where applicable
- **Clarity**: vague language, contradictions, missing details, inconsistent naming, unclear acceptance criteria, or unclear implementation handoff
- **Technical accuracy**: outdated APIs, deprecated approaches, infeasible designs, missing standards alignment. When the document names concrete frameworks, APIs, libraries, or version-bound patterns, verify claims against authoritative documentation (use the `andthen:documentation-lookup` agent if available)
- **Scope and architecture**: explicit in/out-of-scope boundaries, phase boundaries, architecture soundness, and signs of disproportionate complexity
- **Stakeholder fit**: user needs, success criteria, UX/error-state coverage

If the document is a FIS, verify it still follows the structure and intent-first authoring rules from `fis-authoring-guidelines.md`.


## Calibration

Calibrate severity with `review-calibration.md` (universal) and `doc-review-calibration.md` (doc-specific). Use the unified severity scale defined in `review-verdict.md`: CRITICAL / HIGH / MEDIUM / LOW.


## Adversarial Challenge

Run the full adversarial challenge only when any finding is Critical OR total findings > 5. Otherwise apply an inline self-check: re-read each finding against calibration examples, adjust severity, and withdraw findings that don't hold up. Add one line: "Applied inline severity calibration (adversarial challenge skipped: no Critical findings and ≤5 total)."

**Full challenge** (when triggered): Use `adversarial-challenge.md` (`Generic Findings-Challenger Template`) with:
- **Role**: `Adversarial Challenger reviewing document review findings`
- **Shared calibration**: `review-calibration.md`
- **Skill calibration**: `doc-review-calibration.md`
- **Context block**: `Document type, path, project scale/stage context from discovery.`
- **Questions**: Is this a real gap given project scale? Is severity proportional? Is it addressed elsewhere? Would it mislead or block implementation?
- **Verdicts**: `VALIDATED`, `DOWNGRADED`, `WITHDRAWN`
- **Findings payload**: `{all findings}`

Apply verdicts before writing the final report.


## Findings Output

Use the unified severity scale from `review-verdict.md`: CRITICAL / HIGH / MEDIUM / LOW.

**Readiness label**: `Ready` / `Needs Minor Updates` / `Needs Significant Rework` / `Not Ready` — per the verdict reference (doc-mode readiness scale preserved).


## Report Sections

```markdown
## Executive Summary
Overall assessment, high-level findings, challenge stats, key recommendations

## Scope and Context

## Completeness Analysis

## Clarity Issues

## Technical Accuracy

## Edge Cases and Risks

## Architecture Assessment

## Over-Engineering Analysis

## Stakeholder Alignment

## Prioritized Recommendations
Critical / High / Medium / Low

## Readiness Assessment
Ready / Needs Minor Updates / Needs Significant Rework / Not Ready
```


## Report Output Conventions

When writing a report file (not `--inline-findings`):
- **Filename**: `<spec-name>-doc-review-<agent>-<YYYY-MM-DD>.md` — on collision append `-2`, `-3`. `<agent>` is your agent short name (`claude`, `codex`, etc.; fall back to `agent`).
- **Directory priority**:
  1. **Spec directory** — when the document being reviewed lives in a spec/FIS directory or has an associated spec directory from the Project Document Index
  2. **Target directory** — otherwise, same directory as the document being reviewed
  3. **Fallback** — `{AGENT_TEMP}/reviews/` (default `.agent_temp/reviews/`)
- On completion, print the report's relative path from the project root.
