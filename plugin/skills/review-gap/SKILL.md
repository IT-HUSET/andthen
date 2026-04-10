---
description: "Gap analysis: review implementation against requirements with code review and actionable remediation plan."
argument-hint: "[Requirements baseline: plan/spec/PRD/issue/path/URL] [--to-issue] [--to-pr <number>]"
---

# Gap Analysis

Compare the current implementation in the workspace against requirements, then produce a remediation-focused report. The target is always the implementation, not the requirements document itself.

## VARIABLES
ADDITIONAL_CONTEXT: $ARGUMENTS

### Optional Output Flags
- `--to-issue` → PUBLISH_ISSUE
- `--to-pr <number>` → PUBLISH_PR

## INSTRUCTIONS
- Read the Workflow Rules, Guardrails, and relevant project guidelines before starting.
- Read-only analysis. The only file you write is the report.
- Calibrate severity with `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` and `${CLAUDE_PLUGIN_ROOT}/skills/review-code/references/code-review-calibration.md`.
- Default to workspace-wide resolution when requirements and implementation may live in different repos.
- Delegate the implementation code review to a sub-agent using `andthen:review-code` when available.

## GOTCHAS
- Reviewing the wrong implementation target
- Treating the requirements document as the review target
- Losing the PASS/FAIL contract by writing a hand-wavy conclusion

### Helper Scripts
- `${CLAUDE_PLUGIN_ROOT}/scripts/check-stubs.sh <path>`
- `${CLAUDE_PLUGIN_ROOT}/scripts/check-wiring.sh <path>`
- `${CLAUDE_PLUGIN_ROOT}/scripts/run-security-scan.sh <path>`

## WORKFLOW

### 0. Resolve Review Target
State:
- **Requirements baselines**: files, issues, PRDs, plans, or URLs that define expected behavior
- **Implementation target**: repo(s), package(s), directories, or changed files that contain the implementation
- **Mapping rationale**: why those paths are the right implementation target

If no implementation target exists yet, stop and report that gap analysis cannot run.

**Gate**: Requirements sources and implementation target are explicit

### 1. Compile Requirements
Gather the requirements baseline from docs, issues, comments, and `ADDITIONAL_CONTEXT`. Build a concise view of expected behavior, success criteria, constraints, and non-functional requirements. Verify external technical claims against authoritative docs when needed.

**Gate**: Requirements are understood

### 2. Inspect Current Implementation
Map the current implementation state:
- Identify relevant changed files and implementation inventory
- Understand codebase structure, affected components, and existing patterns
- Stop if there is still nothing implemented to compare

**Gate**: Implementation state is understood

### 3. Quality Review
Review solution quality and gather evidence:
- Run project checks that matter here: static analysis, linting, type checks, tests when applicable
- Scan for stubs/placeholders
- Run or delegate comprehensive code review via `andthen:review-code`
- Check substance and wiring using `${CLAUDE_PLUGIN_ROOT}/references/verification-patterns.md`

**Gate**: Quality review complete

### 4. Gap Analysis
Record gaps in these categories:
- **Functionality**
- **Integration**
- **Requirement mismatches**
- **Consistency**
- **Domain language** when `UBIQUITOUS_LANGUAGE.md` exists
- **Holistic sanity check**
- **Verification depth**: substance, wiring, and failing verification signals

### 5. Optional Retrospective
If it adds value, reflect on architectural trade-offs, simpler alternatives, process failures, and recurring knowledge gaps.

### 6. Adversarial Challenge
Use `${CLAUDE_PLUGIN_ROOT}/references/adversarial-challenge.md` (`Generic Findings-Challenger Template`) with:
- **Role**: `Adversarial Challenger reviewing gap analysis findings`
- **Shared calibration**: `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md`
- **Skill calibration**: `${CLAUDE_PLUGIN_ROOT}/skills/review-code/references/code-review-calibration.md`
- **Context block**: `Review target context: {implementation target paths from Step 0}`
- **Questions**:
  1. `Is this a real gap, or acceptable in context?`
  2. `Is the severity justified per the calibration examples?`
  3. `Could there be an existing mitigation the reviewer missed?`
  4. `Would a senior engineer on this codebase flag this in review?`
- **Verdicts**: `VALIDATED`, `DOWNGRADED`, `WITHDRAWN`
- **Optional extra rules**: `Normalize review-code severities as CRITICAL -> Critical, HIGH -> High, SUGGESTIONS -> Medium.`
- **Findings payload**: `{all findings from quality review, gap analysis, and optional retrospective}`

Apply verdicts before scoring.

**Gate**: Findings challenged and filtered

### 7. Dimensional Scoring & Verdict

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

### 8. Report
Write a markdown report with:
- **Executive Summary**: overview, verdict table, high-level findings, challenge stats
- **Requirements Analysis**
- **Implementation Overview**
- **Quality Review Findings**
- **Over-Engineering Analysis**
- **Gap Analysis Results**
- **Retrospective & Reflection** when used
- **Remediation Plan**: Critical/High/Medium/Low, dependencies, sequencing, acceptance criteria
- **Appendix** when needed

**Report output conventions**: Follow `${CLAUDE_PLUGIN_ROOT}/references/report-output-conventions.md` with:
- **Report suffix**: `gap-review`
- **Scope placeholder**: `feature-name`
- **Spec-directory rule**: the requirements baseline is a spec/FIS/plan in a spec directory, or the reviewed feature has an associated spec directory from the Project Document Index
- **Target-directory rule**: the implementation being reviewed is localized to a specific directory, so the report belongs next to the primary implementation target

If notable recurring traps emerge, append them to an existing learnings file.

#### Publish to GitHub
If PUBLISH_ISSUE is `true`:
1. Follow the optional GitHub publishing flow in `${CLAUDE_PLUGIN_ROOT}/references/report-output-conventions.md`
   Title template: `[Review] {scope}: Gap Analysis Report`
2. Print the issue URL

If PUBLISH_PR is set:
1. Post the report as a PR comment using `gh pr comment <number> --body "..."`
2. Print confirmation
