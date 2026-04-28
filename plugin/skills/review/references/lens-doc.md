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

If the document is a FIS, verify it still follows the structure and intent-first authoring rules from [`fis-authoring-guidelines.md`](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md).


## Red-Team Sub-Lens (Always On)

Run `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md` against the document as an always-on sub-lens. Attack ambiguous requirements, missing unhappy paths, hidden implementation guesses, contradiction-prone terminology, and places where an implementer would have to infer behavior not stated in the artifact.

Merge red-team findings into the normal document review findings before calibration and filtering. Do not treat Red-Team as a separate mode or an optional escalation.


## Calibration

Calibrate severity with `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` (universal) and `doc-review-calibration.md` (doc-specific). Load `${CLAUDE_PLUGIN_ROOT}/references/red-team-calibration.md` while running the always-on Red-Team sub-lens; use the document-specific calibration to assign final severity after findings are collected. Use the unified severity scale defined in `review-verdict.md`: CRITICAL / HIGH / MEDIUM / LOW.


## Findings Filter

This pass cannot find new issues; that is the Red-Team Lens's job (`${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md`).

Run the full Findings Filter only when any finding is Critical OR total findings > 5. Otherwise apply an inline self-check: re-read each finding against calibration examples, adjust severity, and withdraw findings that don't hold up. Add one line: "Applied inline severity calibration (Findings Filter skipped: no Critical findings and <=5 total)."

**Full filter** (when triggered): Use `${CLAUDE_PLUGIN_ROOT}/references/adversarial-challenge.md` (`Generic Findings-Filter Template`) with:
- **Role**: `Findings Filter reviewing document review findings`
- **Shared calibration**: `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md`
- **Skill calibration**: `doc-review-calibration.md`
- **Context block**: `Document type, path, project scale/stage context from discovery.`
- **Questions**: Is this a real gap given project scale? Is severity proportional? Is it addressed elsewhere? Would it mislead or block implementation?
- **Verdicts**: `VALIDATED`, `DOWNGRADED`, `WITHDRAWN`
- **Findings payload**: `{all findings}`

Apply verdicts before writing the final report.


## Findings Output

Use the unified severity scale from `review-verdict.md`: CRITICAL / HIGH / MEDIUM / LOW.

**Readiness label**: `Ready` / `Needs Minor Updates` / `Needs Significant Rework` / `Not Ready` — per the verdict reference (doc-mode readiness scale preserved).


## Downstream Routing

After producing findings, classify the dominant pattern and name the right downstream skill in the report's **Recommended Next Action** section.

**Document maturity signal** — distinguishes "draft" from "mature" via concrete markers, in priority order:
1. PRD — always draft for routing purposes (its job is to be clarified into a plan/spec)
2. Plan or FIS with a `Status:` field whose value is pre-execution (e.g. `draft`, `ready-for-review`, `ready-for-execution`) — draft until the value indicates execution has started or completed
3. Plan with no story checkboxes ticked, or FIS with no implementation work landed in the codebase — draft
4. Otherwise — mature

**Pattern precedence** — a single document can match more than one pattern; apply the first that fires:
1. **Requirement-gap cluster** — any "unanswered question / undefined behavior" finding (regardless of severity), OR ≥2 Completeness / Stakeholder Fit findings at MEDIUM or higher. Fires only on draft documents (per maturity signal). Route → the `andthen:clarify` skill. The answers don't exist yet; mechanical edits would paper over the gap. Phrase the recommendation concretely, naming both the gap areas and the doc path, e.g. *"Significant requirement gaps in <areas> in `<doc-path>` — run `andthen:clarify` against `<doc-path>` to resolve them before re-running spec/exec."*
2. **Defect cluster** — clarity, technical accuracy, structural/anchor defects. Route → the `andthen:remediate-findings` skill (or let `--fix` invoke it). Fixes are mechanical edits to the doc.
3. **Mature spec/FIS with requirement-fit concerns** — same triggers as the requirement-gap cluster but on a mature document. Route → the `andthen:remediate-findings` skill. Re-running the `andthen:clarify` skill on a near-final FIS produces churn; encode the concerns as targeted edits instead.

**Interactivity contract** — this reference states which branch is interactive; the `SKILL.md` `FOLLOW-UP ACTIONS` step owns the gate. The clarify branch is interactive by nature (the `andthen:clarify` skill cannot run headless), so:
- Under `AUTO_MODE=off`, the SKILL.md `FOLLOW-UP ACTIONS` step prompts the user to run the `andthen:clarify` skill inline against the listed gaps.
- Under `AUTO_MODE=on`, the recommendation appears only in the report's **Recommended Next Action** — never prompt and never invoke the `andthen:clarify` skill automatically. The orchestrator decides.


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

## Prioritized Recommendations
Critical / High / Medium / Low

## Readiness Assessment
Ready / Needs Minor Updates / Needs Significant Rework / Not Ready

## Recommended Next Action
One line. Name the specific skill (`andthen:clarify`, `andthen:remediate-findings`, or none), the doc path, and the trigger pattern. Do **not** duplicate the Prioritized Recommendations list — this section records the routing decision, not the findings. Per **Downstream Routing** above.
```


## Report Output Conventions

When writing a report file (not `--inline-findings`):
- **Filename**: `<spec-name>-doc-review-<agent>-<YYYY-MM-DD>.md` — on collision append `-2`, `-3`. `<agent>` is your agent short name (`claude`, `codex`, etc.; fall back to `agent`).
- **Directory priority**:
  1. **Spec directory** — when the document being reviewed lives in a spec/FIS directory or has an associated spec directory from the Project Document Index
  2. **Target directory** — otherwise, same directory as the document being reviewed
  3. **Fallback** — `{AGENT_TEMP}/reviews/` (default `.agent_temp/reviews/`)
- On completion, print the report's relative path from the project root.
