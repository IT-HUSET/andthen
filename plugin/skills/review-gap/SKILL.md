---
description: "Use when you explicitly want requirements-vs-implementation review rather than the general `review` router: compare the current implementation against a spec, PRD, or plan and produce remediation guidance. Trigger on 'gap analysis', 'review against the spec', 'compare implementation to the plan', 'compare implementation to the PRD'."
argument-hint: "[Requirements baseline: plan/spec/PRD/issue/directory/URL] [--inline-findings] [--to-issue] [--to-pr <number>]"
---

# Gap Analysis

Compare the current implementation in the workspace against requirements, then produce a remediation-focused report. The target is always the implementation, not the requirements document itself.

Most users should start with `andthen:review`. Use this skill directly when the question is explicitly whether an implementation matches its requirements baseline.

## VARIABLES
ADDITIONAL_CONTEXT: $ARGUMENTS

### Optional Output Flags
- `--inline-findings` → return findings and PASS/FAIL verdict inline and skip report-file output (for delegated use by `andthen:review`)
- `--to-issue` → PUBLISH_ISSUE
- `--to-pr <number>` → PUBLISH_PR

## INSTRUCTIONS
- Read the Workflow Rules, Guardrails, and relevant project guidelines before starting.
- Read-only analysis. The only file you write is the report.
- If `--inline-findings` is present, do not write a report file. Return findings plus verdict inline to the parent skill instead.
- Calibrate severity with `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` and `${CLAUDE_PLUGIN_ROOT}/skills/review-code/references/code-review-calibration.md`.
- Default to workspace-wide resolution when requirements and implementation may live in different repos.
- Delegate implementation code review to a sub-agent using `andthen:review-code` when available. Instruct the sub-agent to return findings inline — do **not** let it write a separate report file. This skill produces the single consolidated report.

## GOTCHAS
- Reviewing the wrong implementation target
- Treating the requirements document as the review target
- Losing the PASS/FAIL contract by writing a hand-wavy conclusion
- Using only the provided input as requirements when sibling PRD/plan/FIS files exist — always run discovery

### Helper Scripts
- `${CLAUDE_PLUGIN_ROOT}/scripts/check-stubs.sh <path>`
- `${CLAUDE_PLUGIN_ROOT}/scripts/check-wiring.sh <path>`
- `${CLAUDE_PLUGIN_ROOT}/scripts/run-security-scan.sh <path>`

## WORKFLOW

### 0. Resolve Review Target

#### Requirements Discovery
When `ADDITIONAL_CONTEXT` is a directory path or a plan file, discover the full requirements baseline rather than treating the single input as the only source.

**GitHub issue or URL** — fetch the body and inspect the typed envelope per `${CLAUDE_PLUGIN_ROOT}/references/github-artifact-roundtrip.md` before treating it as prose:
- `artifact_type: plan-bundle` — extract embedded files to `.agent_temp/github-artifacts/{github-id}-plan-bundle/` and continue as a directory / plan input so sibling PRD and FIS discovery still works
- `artifact_type: fis-bundle` — extract embedded files to `.agent_temp/github-artifacts/{github-id}-fis-bundle/` and continue as a specific FIS input
- Any `*-review` artifact — **STOP** and exit with the correct downstream path: `andthen:remediate-findings`
- Any other typed artifact — **STOP** and exit with the matching workflow skill. Do not infer compatibility from prose content
- Untyped issue or URL — use as-is without further discovery

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

#### State
- **Requirements baselines**: all discovered files, issues, PRDs, plans, or URLs that define expected behavior
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
- Delegate comprehensive code review to `andthen:review-code` sub-agent — instruct it to skip report file output and return findings inline
- Check substance and wiring using `${CLAUDE_PLUGIN_ROOT}/references/verification-patterns.md`

**Gate**: Quality review complete

### 4. Gap Analysis
Record gaps in these categories:
- **Functionality**
- **Integration**
- **Requirement mismatches**
- **Consistency**
- **Domain language** when the `Ubiquitous Language` document (see **Project Document Index**) exists
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
Write a markdown report with the following sections unless `--inline-findings` is present. When `--inline-findings` is present, return the same content inline in concise structured form, including the PASS/FAIL verdict and prioritized remediation guidance.

Standard report sections:
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
1. Follow the optional GitHub publishing flow in `${CLAUDE_PLUGIN_ROOT}/references/report-output-conventions.md`
   Publish target: typed PR comment. If the posting command does not return a direct comment URL, resolve it via follow-up GitHub lookup before completing
2. Print the direct comment URL
