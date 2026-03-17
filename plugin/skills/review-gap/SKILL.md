---
name: review-gap
description: "Gap analysis: review implementation against requirements with code review and actionable remediation plan."
argument-hint: [Additional Context]
---

# Gap Analysis
Comprehensive post-execution review that validates implementation against requirements, performs code review, and identifies gaps. Generates actionable report with findings and remediation plan.


## Variables

ADDITIONAL_CONTEXT: $ARGUMENTS
*(Optional: Additional requirements or context beyond what's in the codebase)*


## Instructions

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails**
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Read-only analysis** - No code changes, commits, or modifications during analysis
- **Be thorough** - Don't skip steps or rush analysis; completeness is critical
- **Delegate code review to a sub-agent** _(if supported by your coding agent)_ that uses the `review-code` skill (do NOT invoke the skill directly)
- **Document everything** - All findings and recommendations must be captured in final report


## Workflow

### 1. Compile and Analyze Requirements

Gather and understand all requirements from multiple sources:

- **Code Context** - Review recent commits, branches, and work-in-progress to understand what's being implemented
- **Documentation** - Check specs, ADRs, design docs, PRDs, or feature documentation in the codebase
- **Issue/Ticket References** - Look for referenced issues, tickets, or PRs that define requirements
- **Code Comments** - Review TODO comments, function documentation, or inline requirement notes
- **ADDITIONAL_CONTEXT** - If specified via arguments, these requirements take precedence and should be the primary focus
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


### 3. Review Solution Quality

Review general quality, soundness and adherence to guidelines, standards and best practices of current implementation.

#### Code Analysis
- Run static analysis, linting, type checking as per project guidelines
- Use IDE diagnostics (`mcp__ide_getDiagnostics`) if available
- Scan for incomplete implementations: `rg "TODO|FIXME|placeholder|not.implemented" <changed-files>` — flag any found as potential gaps

#### Comprehensive Code Review
Spawn a **sub-agent** _(if supported by your coding agent)_ (via Task tool, `subagent_type: "general-purpose"`) to perform the code review.
The sub-agent should **use the `review-code` skill** for thorough review covering:
- Code quality (correctness, readability, best practices, performance)
- Architecture (CUPID principles, DDD patterns, anti-patterns)
- Security (OWASP Top 10, injection prevention, auth, data protection)
- UI/UX (if applicable)

**Do NOT invoke the skill directly** — delegate to a sub-agent to preserve context for remaining workflow steps.
Incorporate the sub-agent's findings into the gap analysis.

**Gate**: Quality reviews complete, over-engineering identified, all issues documented


### 4. Gap Analysis

Systematically identify all gaps between requirements and implementation:

- **Functionality Gaps** - Missing/incomplete features, unfulfilled acceptance criteria, missing error handling/edge cases/validation

- **Integration Gaps** - Missing integration points, incomplete data flows, missing API endpoints/migrations/config, broken dependencies between modules

- **Requirement Mismatches** - Features that don't match requirements, incorrect behavior/logic, unmet non-functional requirements (performance, security, accessibility, i18n)

- **Consistency Gaps** - Deviations from codebase patterns/conventions, documentation gaps, test coverage gaps (unit/integration/e2e)

- **Holistic Sanity Check** - Zoom out: Does the implementation make sense end-to-end? Would it actually work for users? Any hidden assumptions or tech debt introduced?

- **Verification Depth (Substance & Wiring)** — Beyond existence, check:
  - Are implementations substantive? (No stubs, TODOs, placeholders, empty handlers)
  - Are components wired into the system? (Imported, routed, called, rendered)
  - Do verification commands pass? (Build, tests, type-check)
  - Reference: `${CLAUDE_PLUGIN_ROOT}/references/verification-patterns.md`

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


### 6. Remediation Plan

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


## Report

Your job is *ONLY* to analyze and generate report. Do *NOT* make any code changes or commits.

Generate markdown report with:
- **Executive Summary** - What was analyzed, overall assessment, high-level findings
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

Store report in: `<project_root>/.agent_temp/reviews/<feature-name>-gap-review-<agent>-<YYYY-MM-DD>.md`

When complete, print the report's **relative path from the project root** (e.g., `.agent_temp/reviews/auth-gap-review-claude-2026-03-15.md`). Do not use absolute paths.
