---
description: "Gap analysis: review implementation against requirements with code review and actionable remediation plan."
argument-hint: "[Requirements baseline: plan/spec/PRD/issue/path/URL] [--to-issue] [--to-pr <number>]"
---

# Gap Analysis


Comprehensive post-execution review that validates implementation against requirements, performs code review, and identifies gaps. Generates actionable report with findings and remediation plan.


## VARIABLES

ADDITIONAL_CONTEXT: $ARGUMENTS
*(Optional: Requirements baselines or additional context beyond what's in the codebase)*

### Input Interpretation
- Treat file paths, directories, URLs, issue links, PRDs, specs, plans, and other documents passed in `ADDITIONAL_CONTEXT` as **requirements sources / comparison baselines**, **not** as the artifact to review.
- The review target is always the **current implementation in the project workspace**. This may span multiple repos, packages, or directories.
- If a requirements document lives in a different repo than the implementation, use the document as the baseline and review the implementation repo/worktree it refers to.
- The primary task is always: **compare the current implementation in the workspace against the requirements** and identify gaps.
- If the user wants the document itself reviewed for clarity, completeness, or quality, that is **not** `andthen:review-gap`; use `andthen:review-doc`.
- If, after resolving the workspace structure, there is still no identifiable implementation to compare against, stop and report that a gap analysis cannot be performed yet because there is no implementation target.

### Examples
- `andthen:review-gap docs/specs/payments/plan.md`
  - Use `plan.md` as the requirements baseline, then inspect the current payments implementation in the workspace. Do **not** review the plan text itself.
- `andthen:review-gap ../private/docs/specs/sdk-phase4/plan.md`
  - Use the private-repo plan as the baseline, then inspect the implementation in the public/code repo if workspace docs indicate that is where the code lives.
- If the user wants feedback on the plan/spec document itself:
  - That is `andthen:review-doc`, not `andthen:review-gap`.

### Optional Output Flags
- `--to-issue` → PUBLISH_ISSUE: Publish review report as a GitHub issue
- `--to-pr <number>` → PUBLISH_PR: Post review report as a comment on the specified PR


## INSTRUCTIONS

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails**
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Read-only analysis** – no code changes or commits. The only file you write is the final report.
- **Be thorough** - Don't skip steps or rush analysis; completeness is critical
- **Calibrate severity rigorously** – Read `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` before assigning severity. If you identified a problem, it IS a problem — do not rationalize it away. "It probably works" is not a pass.
- **Default to workspace-wide resolution** - Do not assume the implementation is in the same repo as the requirements document. In multi-repo workspaces, explicitly locate the implementation target first.
- **Delegate code review to a sub-agent** _(if supported by your coding agent)_ that uses the `andthen:review-code` skill (do NOT invoke the skill directly)
- **Document everything** - All findings and recommendations must be captured in final report
- **Read project learnings** – If `LEARNINGS.md` exists (check Project Document Index for location), read it before starting to avoid known traps and error patterns


## GOTCHAS
- Most common failure: reviewing the wrong target – resolve implementation target FIRST, before any analysis
- Requirements documents in a different repo than the implementation cause confusion – establish the mapping explicitly
- Confusing review-gap with review-doc – gap reviews implementation against requirements, doc reviews the document itself

### Helper Scripts
Helper scripts are available in `${CLAUDE_PLUGIN_ROOT}/scripts/` – use when applicable:
- `check-stubs.sh <path>` – scan for incomplete implementation indicators (TODO/FIXME, empty functions, placeholders)
- `check-wiring.sh <path>` – verify new/changed files are imported/referenced
- `run-security-scan.sh <path>` – Semgrep with pattern-based fallback


## WORKFLOW

### 0. Resolve Review Target

Before any analysis, identify and state:

- **Requirements baselines** - Which files, issues, PRDs, specs, plans, or URLs define expected behavior
- **Implementation target** - Which repo(s), package(s), directories, or changed files contain the implementation to inspect
- **Mapping rationale** - Why those paths are the correct implementation target for these requirements

Use workspace metadata first:

- `AGENTS.md` / `CLAUDE.md`
- Repo maps and cross-references
- Monorepo/workspace manifests
- Changed files, package boundaries, and import relationships

If no workspace metadata exists, default to the current repo/worktree as the implementation target.

If this mapping is ambiguous, resolve it before proceeding. Do **not** substitute a document-quality review for implementation analysis.

### 1. Compile and Analyze Requirements

Gather and understand all requirements from multiple sources:

- **Code Context** - Review recent commits, branches, and work-in-progress to understand what's being implemented
- **Documentation** - Check specs, ADRs, design docs, PRDs, or feature documentation in the codebase
- **Issue/Ticket References** - Look for referenced issues, tickets, or PRs that define requirements
- **Code Comments** - Review TODO comments, function documentation, or inline requirement notes
- **ADDITIONAL_CONTEXT** - If specified via arguments, treat it as supplemental or authoritative requirements input. These requirements take precedence, but they remain the **comparison baseline**, not the review target.
- **Read additional guidelines and documentation** - Read additional relevant guidelines and documentation (API, guides, reference, etc.) as needed
- **Verify against authoritative sources** - When reviewing technical choices, API usage, security patterns, or framework conventions, look up official documentation to verify findings are based on current facts (not outdated assumptions). Use web searches and Context7 MCP as needed.

Create a clear, consolidated view of:
- What functionality should be implemented
- What success criteria must be met
- What constraints or non-functional requirements apply
- What the expected behavior and user experience should be

**Gate**: All requirements compiled, understood, and documented


### 2. Analyze Current Implementation

Map the current state of the implementation:

- **Implementation Status**
  - Use `git status --porcelain` to identify modified, added, and deleted files
  - Use `git diff` to see actual code changes
  - Use `git log` with options like `--since="1 week ago"` or `--author` to review recent commit history
  - Check for work-in-progress branches or uncommitted changes
  - If no relevant implementation can be found, stop and report that there is nothing to compare against the requirements yet

- **Codebase Understanding**
  - Use `tree -d -L 3` to understand directory structure
  - Use `git ls-files` to see all tracked files
  - Identify relevant files and components affected by the implementation
  - Look for existing patterns, conventions, and similar implementations to understand expected approach

- **Implementation Inventory**
  - List all components, modules, or features that have been added or modified
  - Identify what's completed vs. what appears incomplete
  - Map relationships and dependencies between modified components

**Gate**: Current implementation state fully mapped and documented

Only after both gates above pass should you continue. Do not substitute a document-quality review for implementation analysis.


### 3. Review Solution Quality

Review general quality, soundness and adherence to guidelines, standards and best practices of current implementation.

#### Code Analysis
- Run static analysis, linting, type checking as per project guidelines
- Use IDE diagnostics (`mcp__ide_getDiagnostics`) if available
- Scan for incomplete implementations: `rg "TODO|FIXME|placeholder|not[_ -]implemented|notImplemented" <changed-files>` – flag any found as potential gaps

#### Comprehensive Code Review
Spawn a **sub-agent** _(if supported by your coding agent)_ (via Task tool, `subagent_type: "general-purpose"`) to perform the code review.
The sub-agent should **use the `andthen:review-code` skill** for thorough review covering:
- Code quality (correctness, readability, best practices, performance)
- Architecture (CUPID principles, DDD patterns, anti-patterns)
- Security (OWASP Top 10, injection prevention, auth, data protection)
- UI/UX (if applicable)

**Do NOT invoke the skill directly** – delegate to a sub-agent to preserve context for remaining workflow steps.
Incorporate the sub-agent's findings into the gap analysis.

**Gate**: Quality reviews complete, over-engineering identified, all issues documented


### 4. Gap Analysis

Systematically identify all gaps between requirements and implementation:

- **Functionality Gaps** - Missing/incomplete features, unfulfilled acceptance criteria, missing error handling/edge cases/validation

- **Integration Gaps** - Missing integration points, incomplete data flows, missing API endpoints/migrations/config, broken dependencies between modules

- **Requirement Mismatches** - Features that don't match requirements, incorrect behavior/logic, unmet non-functional requirements (performance, security, accessibility, i18n)

- **Consistency Gaps** - Deviations from codebase patterns/conventions, documentation gaps, test coverage gaps (unit/integration/e2e)

- **Domain language gaps** - Terminology drift between requirements and implementation – same concept with different names, terms used outside their bounded context, or new domain concepts without glossary entries. _(Skip if no `UBIQUITOUS_LANGUAGE.md` exists)_

- **Holistic Sanity Check** - Zoom out: Does the implementation make sense end-to-end? Would it actually work for users? Any hidden assumptions or tech debt introduced?

- **Verification Depth (Substance & Wiring)** – Beyond existence, check:
  - Are implementations substantive? (No stubs, TODOs, placeholders, empty handlers)
  - Are components wired into the system? (Imported, routed, called, rendered)
  - Do verification commands pass? (Build, tests, type-check)
  - Reference: `${CLAUDE_PLUGIN_ROOT}/references/verification-patterns.md`
  - Calibration: `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` – use severity examples and anti-leniency protocol to benchmark findings before recording them
  - Delegate stub detection and wiring checks to a sub-agent _(if supported by your coding agent)_, or use helper scripts from `${CLAUDE_PLUGIN_ROOT}/scripts/` when available

**Gate**: All gaps comprehensively identified and documented


### 5. [Optional] Retrospective & Deep Reflection

#### Design & Architecture Reflection
Think deeply and critically about the implementation choices made:

- **Decision Analysis** - For each significant design/architecture choice: What alternatives existed? What trade-offs were made? With hindsight, was this the right call?
- **Alternative Approaches** - Identify 2-3 fundamentally different ways the implementation could have been structured. Evaluate pros/cons vs the chosen approach.
- **Hindsight Analysis** - If starting over with current knowledge, what would change? What assumptions proved wrong? What would a senior/staff engineer critique?
- **Effort Allocation** - Where was effort misallocated? What was over-engineered vs under-invested?
- **Simplicity Check** - Could the same outcome have been achieved with significantly less code, fewer abstractions, or simpler patterns?

#### Process Retrospective
- **What Went Well** - Patterns, decisions, or practices worth repeating
- **What Didn't Go Well** - Problems, inefficiencies, or missteps during implementation
- **Deviation Analysis** - Compare actual vs planned implementation. Were deviations justified?
- **Root Causes** - For significant issues, why did they occur? (unclear requirements, complexity, missing knowledge, etc.)
- **Process Improvements** - Specific changes to prevent similar issues in future
- **Knowledge Gaps** - Areas where lack of knowledge or documentation caused issues

**Gate**: Retrospective and deep reflection complete with actionable insights


### 6. Adversarial Challenge

Spawn a **sub-agent** _(if supported by your coding agent)_ to challenge the findings from Steps 3-5. The challenger operates in a fresh context — it sees findings and code, but not the reasoning that produced them. This counters self-evaluation bias (evaluators trend toward leniency without adversarial challenge).

**Sub-agent prompt:**

```
You are an Adversarial Challenger reviewing gap analysis findings.

Read the calibration reference: ${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md

For each finding, evaluate:
1. "Is this a real gap, or acceptable in context (trade-off, framework convention, intentional choice)?"
2. "Is the severity justified per the calibration examples?"
3. "Could there be an existing mitigation the reviewer missed?"
4. "Would a senior engineer on this codebase flag this in a PR review?"

For each finding, assign a verdict:
- **VALIDATED** — Finding holds up under scrutiny. State why in one sentence.
- **DOWNGRADED** — Real issue, but severity is too high. State new severity and why.
- **WITHDRAWN** — False positive or not applicable. State why.

Do NOT add new findings — your job is to filter, not expand.

Severity mapping: `review-code` emits CRITICAL/HIGH/SUGGESTIONS. Normalize before challenging:
CRITICAL → Critical, HIGH → High, SUGGESTIONS → Medium.

Review target context: {implementation target paths from Step 0}
Findings to challenge:
{all findings from Steps 3-5, including code review sub-agent output}
```

**Apply verdicts**: Remove WITHDRAWN findings from the working set. Update severity for DOWNGRADED findings. Carry VALIDATED and DOWNGRADED findings forward to subsequent steps.

**Record in report**: Challenge statistics (N validated, N downgraded, N withdrawn) and rationale for each DOWNGRADED and WITHDRAWN verdict.

> **Note**: If sub-agents are not available, execute the challenge inline — review your own findings using the four questions above and apply verdicts. The self-challenge is less effective than a fresh-context sub-agent but still catches obvious false positives.

**Gate**: All findings challenged, verdicts applied


### 7. Dimensional Scoring & Verdict

Score the implementation on three dimensions using ONLY the **validated/downgraded findings** that survived the Adversarial Challenge. Each dimension is scored 1-10.

| Dimension | Question | Threshold | Scoring Guide |
|-----------|----------|-----------|---------------|
| **Functionality** | Does it work correctly for specified requirements? | >= 7 | 10: all requirements met, edge cases handled. 7: core happy path works, minor gaps. 4: major functionality broken. 1: does not function. |
| **Completeness** | Are there stubs, TODOs, placeholders, or missing features? | >= 9 | 10: no stubs/TODOs, all features present. 9: trivial TODOs only (comments, minor polish). 7: non-critical features stubbed. 4: significant features missing. 1: mostly stubs. |
| **Wiring** | Is everything connected end-to-end? (imported, routed, called, rendered, migrated) | >= 8 | 10: all components wired, verified via build/tests. 8: all critical paths wired, minor integration gaps. 5: some components exist but aren't connected. 2: significant unwired code. |

**Verdict rules:**
- If ANY dimension scores below its threshold: **FAIL**
- If ALL dimensions meet or exceed thresholds: **PASS**
- No negotiation. No "conditional pass". No "pass with caveats".

**Output format** (include in report Executive Summary):

```
## Verdict

| Dimension     | Score | Threshold | Status |
|---------------|-------|-----------|--------|
| Functionality | X/10  | >= 7      | PASS/FAIL |
| Completeness  | X/10  | >= 9      | PASS/FAIL |
| Wiring        | X/10  | >= 8      | PASS/FAIL |

**Overall: PASS / FAIL**
```

**Gate**: Scores assigned, verdict determined


### 8. Remediation Plan

Prioritized plan for addressing all identified gaps and issues:

- **Issue Categorization** - Group by severity:
  - Critical: Blocks core functionality, security vulnerabilities, data loss risks
  - High: Significant functionality gaps, major quality/architectural problems
  - Medium: Minor functionality gaps, code quality, maintainability concerns
  - Low: Nice-to-have improvements, minor optimizations, cosmetic issues

- **Dependencies & Sequencing** - Map dependencies between fixes. Sequence: blockers first, related fixes grouped, quick wins, then risk-balanced remainder.

- **Risk Assessment** - Per item: complexity, blast radius, uncertainty, breaking change potential

- **Remediation Steps** - Per issue: problem description, proposed solution, affected files, dependencies, acceptance criteria

- **Rollout Considerations** - Incremental vs big-bang delivery, rollback strategies, required testing/validation

**Gate**: Actionable remediation plan created


### 9. Write Report

Your job is *ONLY* to analyze and generate report. Do *NOT* make any code changes or commits.

Generate markdown report with:
- **Executive Summary** - What was analyzed, overall assessment, dimensional verdict table (from Step 7), high-level findings, challenge statistics (N validated/downgraded/withdrawn)
- **Requirements Analysis** - Requirements identified, ambiguities or unclear items
- **Implementation Overview** - What was implemented, components/files modified, approach taken
- **Quality Review Findings** - Code quality, security, architecture, maintainability, UI/UX, performance issues
- **Over-Engineering Analysis** - Unnecessary complexity, premature optimizations, excessive layering, feature bloat, technology overkill, pattern misapplication (with simpler alternatives)
- **Gap Analysis Results** - Functionality gaps, integration gaps, requirement mismatches, consistency issues, missing tests/docs
- **Retrospective & Reflection** - Design decision analysis, alternative approaches considered, what went well/didn't, root causes, lessons learned
- **Remediation Plan** - Categorized/prioritized issues (Critical/High/Medium/Low), dependencies, sequencing, risk assessment, specific remediation steps, acceptance criteria
- **Appendix** (if needed) - Code snippets, technical details, reference materials

**Report file naming:**
- **Agent identifier**: Determine your agent short name (e.g., `claude`, `codex`, `cursor`, `aider`). If uncertain, use `agent`.
- **File collision avoidance**: Before writing, check if the target filename already exists. If it does, append an incrementing suffix: `-2`, `-3`, etc. **Never overwrite existing reports!**

**Report output directory** – resolve in priority order:
1. **Spec directory**: If the requirements baseline is a spec/FIS/plan in a spec directory, or the reviewed feature has an associated spec directory from the Project Document Index, store the report **in that spec directory**.
2. **Target directory**: If the implementation being reviewed is localized to a specific directory, store the report **in the same directory** as the primary implementation target.
3. **Fallback**: Store in `{AGENT_TEMP}/reviews/` where `{AGENT_TEMP}` is the **Agent Temp** path from the Project Document Index (default: `.agent_temp/`).

**Filename**: `<feature-name>-gap-review-<agent>-<YYYY-MM-DD>.md`

When complete, print the report's **relative path from the project root**. Do not use absolute paths.

- **Update project learnings** – If significant non-obvious traps or error patterns are discovered during execution (especially recurring patterns across reviews), append them to `LEARNINGS.md` (check Project Document Index for location). Bar: "Would a competent developer with code and git access still get bitten?"

#### Publish to GitHub _(if --to-issue or --to-pr)_
If PUBLISH_ISSUE is `true`:
1. Create a GitHub issue: title `[Review] {scope}: Gap Analysis Report`, body = report content
2. Print the issue URL

If PUBLISH_PR is set:
1. Post report as a PR comment using `gh pr comment <number> --body "..."`
2. Print confirmation
