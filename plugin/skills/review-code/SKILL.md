---
description: Perform thorough code reviews covering code quality, security, architecture, and UI/UX. Use when reviewing code changes, PRs, implementations, or when asked to review, audit, or assess code quality. Generate detailed reports with prioritized findings.
user-invocable: true
argument-hint: "[scope/files] [--to-issue] [--to-pr <number>]"
---

# Code Review Skill


Comprehensive code review covering quality, security, architecture, and UI/UX aspects.


## VARIABLES

ARGUMENTS: $ARGUMENTS

### Optional Output Flags
- `--to-issue` → PUBLISH_ISSUE: Publish review report as a GitHub issue
- `--to-pr <number>` → PUBLISH_PR: Post review report as a comment on the specified PR


## INSTRUCTIONS

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md (and/or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails**
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Non-modifying** - Analysis only, no code changes
- Follow project guidelines from CLAUDE.md
- Use checklists in `checklists/` subdirectory for systematic assessment
- **Severity calibration**: Reference `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` for severity benchmarking when assigning finding severity
- **Read project learnings** – If `LEARNINGS.md` exists (check Project Document Index for location), read it before starting to avoid known traps and error patterns


## GOTCHAS
- Over-reporting low-severity style nits drowns out critical findings – calibrate to project scale
- Forgetting to run Semgrep when available – check for it early and integrate findings
- Reviewing generated/vendored code wastes context – exclude lockfiles, build output, generated types

### Helper Scripts
Helper scripts are available in `${CLAUDE_PLUGIN_ROOT}/scripts/` – use when applicable:
- `run-security-scan.sh <path>` – Semgrep with pattern-based fallback for security scanning


## ORCHESTRATOR ROLE _(if supported by your coding agent)_

You are the orchestrator. Your job is to:
- Determine review scope and select applicable reviews
- Delegate review work to sub-agents (one per review dimension)
- Collect and deduplicate findings across reviewers
- Generate the final unified report

You do NOT:
- Read large amounts of implementation code directly (delegate to reviewers)
- Let your context get filled with code content

### Sub-Agent Delegation

Spawn parallel sub-agents _(if supported)_ for each applicable review type:

1. **Code Quality reviewer** – Apply CODE-REVIEW-CHECKLIST.md to changed files
2. **Security reviewer** – Apply SECURITY-REVIEW-CHECKLIST.md + run Semgrep/security scan
3. **Architecture reviewer** – Apply ARCHITECTURAL-REVIEW-CHECKLIST.md
4. **Domain Language reviewer** – Apply DOMAIN-LANGUAGE-REVIEW-CHECKLIST.md (if UL exists)
5. **UI/UX reviewer** – Apply UI-UX-REVIEW-CHECKLIST.md (if UI changes)

Each sub-agent receives: the checklist content, the list of changed files,
and project guidelines. They return: categorized findings (CRITICAL/HIGH/SUGGESTION).

If sub-agents are not supported, execute reviews sequentially but
be mindful of context – prioritize CRITICAL findings.


## WORKFLOW

### Phase 1: Context Analysis

1. **Determine review scope** from conversation context:
   - If specific files/dirs mentioned: Focus on those
   - If PR number mentioned: Run `gh pr diff <number>` to get changes
   - If focus area mentioned (security, architecture, ui): Emphasize in Phase 2
   - Otherwise: Use git status/diff for scope
2. Run `git status --porcelain` and `git diff` to identify changes
3. Run `git log -10 --oneline` to understand recent commits
4. Use `tree -d -L 3` and `git ls-files | head -250` for codebase overview
5. Identify applicable review types based on changed files (code, architecture, UI/UX)
6. Read additional relevant guidelines and documentation (API, guides, reference, etc.) as needed
7. **Verify against authoritative sources** - When reviewing technical choices, API usage, security patterns, or framework conventions, look up official documentation to verify findings are based on current facts (not outdated assumptions). Use web searches and Context7 MCP as needed.

**Gate**: Scope determined, relevant files identified


### Phase 2: Review Execution

Perform applicable reviews using the checklists. 

#### Code Analysis
- Run static analysis, linting, type checking per project guidelines
- Use IDE diagnostics if available
- **IMPORTANT**: Only format code that has been added or modified, **NEVER** format the entire codebase

#### Code Review
**Checklist**: [CODE-REVIEW-CHECKLIST.md](checklists/CODE-REVIEW-CHECKLIST.md)

Assess:
- Correctness, logic errors, edge cases, error handling
- Readability, naming, code organization
- Best practices, DRY, design patterns, anti-patterns
- Performance (N+1 queries, algorithms, caching)
- Maintainability, testability, documentation, tech debt

#### Security Review

Select the checklist(s) that match the code under review. Apply multiple when applicable (e.g. a web app with an API backend and a CI/CD pipeline warrants WEB + API + CICD).

| Checklist | Standard | Apply when... |
|-----------|----------|---------------|
| [SECURITY-CHECKLIST-WEB.md](checklists/SECURITY-CHECKLIST-WEB.md) | OWASP Top 10:2025 | Web applications, server-rendered pages, or any general-purpose backend – the baseline checklist for Web applications (Server-rendered), Web APIs or Browser Applications (SPA)|
| [SECURITY-CHECKLIST-API.md](checklists/SECURITY-CHECKLIST-API.md) | OWASP API Security Top 10:2023 | REST, GraphQL, or gRPC APIs; microservices; any code that exposes or consumes HTTP endpoints |
| [SECURITY-CHECKLIST-LLM.md](checklists/SECURITY-CHECKLIST-LLM.md) | OWASP LLM Top 10:2025 | Applications integrating LLMs or generative AI – prompt handling, RAG pipelines, agentic systems, AI-generated output |
| [SECURITY-CHECKLIST-MOBILE.md](checklists/SECURITY-CHECKLIST-MOBILE.md) | OWASP Mobile Top 10:2024 | Native iOS/Android apps and cross-platform mobile apps (React Native, Flutter, Expo) |
| [SECURITY-CHECKLIST-CICD.md](checklists/SECURITY-CHECKLIST-CICD.md) | OWASP Top 10 CI/CD Security Risks | Pipeline configuration files, deployment workflows, IaC, build scripts, and supply chain changes |

Assess (across applicable checklists):
- Input validation & sanitization
- Injection prevention (SQL, command, XSS, prompt, path traversal)
- Authentication & authorization
- Cryptography (encryption, hashing, key management)
- Data protection (secrets, logging exposure)
- API security, headers, CORS, CSRF
- Supply chain and pipeline integrity

**Automated security scanning** – Run available tools in parallel to complement manual checklist review. All tools are optional – proceed with manual review if none are available.

- **`/security-review`** – Run _(if available – Claude Code built-in)_ for a quick scan of pending changes against common vulnerability patterns.

- **Semgrep** – Run on changed files using one of these approaches (in order of preference):
  1. **Claude Code plugin** (`semgrep/mcp-marketplace`) – If installed, provides auto-scanning on Write/Edit via hooks and MCP tools for on-demand scanning.
  2. **CLI** – If `semgrep` is installed locally, run directly:
     ```bash
     semgrep scan --config auto --severity WARNING --severity ERROR --json <changed-files-or-dirs>
     ```
     Parse JSON output: `results[].extra.severity` (ERROR → CRITICAL, WARNING → HIGH), `results[].extra.metadata.cwe` for classification, `results[].extra.message` for descriptions.
  3. **MCP tools** – If the `semgrep` MCP server is available, call the `security_check` tool on changed files, or `semgrep_scan` with a specific config (e.g. `p/security-audit`, `p/owasp-top-ten`). Provides structured findings with severity, CWE references, and suggested fixes.

#### Architecture Review
**Checklist**: [ARCHITECTURAL-REVIEW-CHECKLIST.md](checklists/ARCHITECTURAL-REVIEW-CHECKLIST.md)

Assess:
- CUPID principles (Composable, Unix philosophy, Predictable, Idiomatic, Domain-aligned)
- DDD patterns (bounded contexts, aggregates, domain events)
- Pattern adherence (clean architecture, service boundaries, API design)
- Anti-patterns, performance, scalability, resilience

#### Domain Language Review
**Checklist**: [DOMAIN-LANGUAGE-REVIEW-CHECKLIST.md](checklists/DOMAIN-LANGUAGE-REVIEW-CHECKLIST.md) _(skip if no `UBIQUITOUS_LANGUAGE.md` exists)_

Assess:
- Terminology consistency, domain model alignment, new term detection

#### UI/UX Review (when applicable)
**Checklist**: [UI-UX-REVIEW-CHECKLIST.md](checklists/UI-UX-REVIEW-CHECKLIST.md)

Assess:
- Visual quality (layout, typography, color/contrast, responsive)
- Usability (5-second clarity, touch targets, cognitive load)
- Platform conventions (iOS HIG, Material Design, web standards)
- Accessibility (WCAG 2.2), performance, interaction patterns

**Gate**: All applicable reviews complete


### Phase 3: Analysis & Findings

1. Categorize findings by priority:
   - **CRITICAL**: Security vulnerabilities, data loss risks, broken functionality
   - **HIGH**: Performance issues, maintainability concerns, minor security issues
   - **SUGGESTIONS**: Improvements, optimizations, enhancements

2. Identify obsolete/temporary files and code requiring cleanup
3. Check for unmotivated complexity, over-engineering, or duplication
4. Verify adherence to project guidelines and patterns

**Gate**: Findings categorized and validated


## REPORT FORMAT

Generate markdown report with:

```markdown
# Review Report - [Date]

## Summary
[2-3 sentence overview of review scope and overall assessment]

## CRITICAL ISSUES
[Each issue: Title, Impact, Location, Fix Required]

## HIGH PRIORITY
[Each issue: Title, Impact, Location, Recommendation]

## SUGGESTIONS
[Brief list of improvements]

## Cleanup Required
- [Obsolete/temporary files to remove]
- [Dead code to remove]

## Compliance
- Guidelines adherence: [Assessment]
- Architecture patterns: [Assessment]
- Security best practices: [Assessment]
- [UI/UX if applicable]: [Assessment]

## Next Steps
1. [Prioritized action items]
```

**Report file naming:**
- **Agent identifier**: Determine your agent short name (e.g., `claude`, `codex`, `cursor`, `aider`). If uncertain, use `agent`.
- **File collision avoidance**: Before writing, check if the target filename already exists. If it does, append an incrementing suffix: `-2`, `-3`, etc. **Never overwrite existing reports!**

**Report output directory** – resolve in priority order:
1. **Spec directory**: If the review relates to a spec/FIS directory (e.g., the files being reviewed correspond to a feature that has an associated spec directory from the Project Document Index), store the report **in that spec directory**.
2. **Target directory**: If the review target is a specific file or localized directory, store the report **in the same directory** as the primary review target.
3. **Fallback**: Store in `{AGENT_TEMP}/reviews/` where `{AGENT_TEMP}` is the **Agent Temp** path from the Project Document Index (default: `.agent_temp/`).

**Filename**: `<feature-name>-code-review-<agent>-<YYYY-MM-DD>.md`

When complete, print the report's **relative path from the project root**. Do not use absolute paths.

### Publish to GitHub _(if --to-issue or --to-pr)_
If PUBLISH_ISSUE is `true`:
1. Create a GitHub issue: title `[Code Review] {scope}: Review Report`, body = report content
2. Print the issue URL

If PUBLISH_PR is set:
1. Post report as a PR comment using `gh pr comment <number> --body "..."`
2. Print confirmation
