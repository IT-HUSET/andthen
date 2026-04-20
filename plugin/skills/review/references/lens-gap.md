# Lens: Gap Analysis

Rubric for comparing a current implementation against its requirements baseline (spec, PRD, plan, issue, FIS, or other source of truth) and producing remediation-focused output with a PASS/FAIL verdict. Load this reference when running `andthen:review --mode gap`.

The target is always the implementation, not the requirements document itself.


## Scope

Two inputs must be explicit before the lens can run:
1. **Requirements baseline** — docs, issues, comments, or source-of-truth files that define expected behavior
2. **Implementation target** — repo(s), package(s), directories, or changed files that contain the implementation

Default to **workspace-wide resolution** when requirements and implementation may live in different repos.


## 0. Resolve Review Target

### Requirements Discovery

When the caller provides a directory path or a plan file, discover the full requirements baseline rather than treating the single input as the only source.

**Directory path** — search the directory (and its parent, for cases where a subdirectory like `fis/` is given) for:
- `plan.md` — the implementation plan with story breakdown
- `prd.md` — the product requirements document
- FIS/spec files (`s01-*.md`, `s02-*.md`, etc.) co-located with the plan
- Also check the Project Document Index in the project `CLAUDE.md` for additional pointers

**Plan file** — read the plan and extract related requirements:
- Look for a sibling `prd.md` in the same directory
- Extract FIS file paths from the **Story Catalog** table (`FIS` column) and from `**FIS**:` fields in Phase Breakdown sections — these are typically relative paths in the same directory or under a `fis/` subdirectory
- Read all referenced FIS files that exist on disk (skip entries marked `–` or not yet created)

**Any other input** (specific file, issue, URL) — use as-is without further discovery.

### State

- **Requirements baselines**: all discovered files, issues, PRDs, plans, or URLs that define expected behavior
- **Implementation target**: repo(s), package(s), directories, or changed files that contain the implementation
- **Mapping rationale**: why those paths are the right implementation target

If no implementation target exists yet, stop and report that gap analysis cannot run.

**Gate**: Requirements sources and implementation target are explicit


## 1. Compile Requirements

Gather the requirements baseline from docs, issues, comments, and caller context. Build a concise view of expected behavior, success criteria, constraints, and non-functional requirements. Verify external technical claims against authoritative docs when needed.


## 2. Inspect Current Implementation

Map the current implementation state:
- Identify relevant changed files and implementation inventory
- Understand codebase structure, affected components, and existing patterns
- Stop if there is still nothing implemented to compare


## 3. Quality Review

Run project checks and gather evidence directly — do not delegate to the code lens. When an upstream step has already run code review (e.g. a `plan` pipeline's per-story `quick-review`), reuse that evidence; otherwise gather it here:
- Run applicable build/package checks
- Run applicable test suites
- Run static analysis, linting, type checks
- **Stub scan**: grep changed files for incomplete-implementation markers (`TODO`, `FIXME`, `XXX`, `NotImplementedError`, language-appropriate `pass`/empty-body/`throw.*not implemented` patterns). Triage intentional vs. forgotten.
- **Wiring check**: for each new file, confirm at least one other file imports or references it (language-appropriate import/require/include grep on basename or module path).
- Check substance and wiring using `verification-patterns.md`
- Run available security tooling (e.g. `../scripts/run-security-scan.sh <path>`) when applicable

Focus on requirements-vs-implementation alignment — the unique value of this lens.


## 4. Gap Analysis

Record gaps in these categories:
- **Functionality**
- **Integration**
- **Requirement mismatches**
- **Consistency**
- **Domain language** when the `Ubiquitous Language` document (see **Project Document Index**) exists
- **Holistic sanity check**
- **Verification depth**: substance, wiring, and failing verification signals


## 5. Optional Retrospective

If it adds value, reflect on architectural trade-offs, simpler alternatives, process failures, and recurring knowledge gaps.


## 6. Adversarial Challenge

Run the full adversarial challenge only when any finding is Critical OR total findings > 5. Otherwise apply an inline self-check: re-read each finding against calibration examples, adjust severity, and withdraw findings that don't hold up. Add one line: "Applied inline severity calibration (adversarial challenge skipped: no Critical findings and ≤5 total)."

**Full challenge** (when triggered): Use `adversarial-challenge.md` (`Generic Findings-Challenger Template`) with:
- **Role**: `Adversarial Challenger reviewing gap analysis findings`
- **Shared calibration**: `review-calibration.md`
- **Skill calibration**: `code-review-calibration.md`
- **Context block**: `Review target context: {implementation target paths from Step 0}`
- **Questions**: Is this a real gap? Is severity justified? Could there be an existing mitigation? Would a senior engineer flag this?
- **Verdicts**: `VALIDATED`, `DOWNGRADED`, `WITHDRAWN`
- **Findings payload**: `{all findings from quality review, gap analysis, and optional retrospective}`

Apply verdicts before scoring.


## Calibration

Calibrate severity with `review-calibration.md` (universal) and `code-review-calibration.md` (code-specific). Use the unified severity scale defined in `review-verdict.md`: CRITICAL / HIGH / MEDIUM / LOW.


## 7. Dimensional Scoring & Verdict

| Dimension | Question | Threshold | Scoring Guide |
|-----------|----------|-----------|---------------|
| **Functionality** | Does it work correctly for specified requirements? | >= 7 | 10: all requirements met, edge cases handled. 7: core happy path works, minor gaps. 4: major functionality broken. 1: does not function. |
| **Completeness** | Are there stubs, TODOs, placeholders, or missing features? | >= 9 | 10: no stubs/TODOs, all features present. 9: trivial TODOs only. 7: non-critical features stubbed. 4: significant features missing. 1: mostly stubs. |
| **Wiring** | Is everything connected end-to-end? | >= 8 | 10: all components wired, verified via build/tests. 8: all critical paths wired, minor integration gaps. 5: some components exist but are not connected. 2: significant unwired code. |

**Verdict rules**
- If any dimension is below threshold: **FAIL**
- If all dimensions meet threshold: **PASS**
- No conditional verdicts

Include this exact summary in the Executive Summary:

```markdown
## Verdict

| Dimension     | Score | Threshold | Status |
|---------------|-------|-----------|--------|
| Functionality | X/10  | >= 7      | PASS/FAIL |
| Completeness  | X/10  | >= 9      | PASS/FAIL |
| Wiring        | X/10  | >= 8      | PASS/FAIL |

**Overall: PASS / FAIL**
```

> **Contract invariance**: The PASS/FAIL verdict table above is a byte-level compatibility contract. Downstream skills (`andthen:exec-plan`, `andthen:remediate-findings`) parse this table directly. Do not re-label, re-phrase, or re-order the columns.


## Report Sections

```markdown
## Executive Summary
overview, verdict table, high-level findings, challenge stats

## Requirements Analysis

## Implementation Overview

## Quality Review Findings

## Over-Engineering Analysis

## Gap Analysis Results

## Retrospective & Reflection
(when used)

## Remediation Plan
Critical / High / Medium / Low, dependencies, sequencing, acceptance criteria

## Appendix
(when needed)
```

If notable recurring traps emerge, append them to an existing learnings file.


## Report Output Conventions

When writing a report file (not `--inline-findings`):
- **Filename**: `<feature-name>-gap-review-<agent>-<YYYY-MM-DD>.md` — on collision append `-2`, `-3`. `<agent>` is your agent short name (`claude`, `codex`, etc.; fall back to `agent`).
- **Directory priority**:
  1. **Spec directory** — when the requirements baseline is a spec/FIS/plan in a spec directory, or the reviewed feature has an associated spec directory from the Project Document Index
  2. **Target directory** — next to the primary implementation target (the localized implementation directory)
  3. **Fallback** — `{AGENT_TEMP}/reviews/` (default `.agent_temp/reviews/`)
- On completion, print the report's relative path from the project root.
