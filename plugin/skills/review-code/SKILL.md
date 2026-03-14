---
name: andthen-review-code
description: Performs thorough code reviews covering code quality, security, architecture, and UI/UX. Use when reviewing code changes, PRs, implementations, or when asked to review, audit, or assess code quality. Generates detailed reports with prioritized findings.
context: fork
agent: general-purpose
user-invocable: true
---

# Code Review Skill

Comprehensive code review covering quality, security, architecture, and UI/UX aspects.


## Instructions

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md (and/or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails**
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Non-modifying** - Analysis only, no code changes
- Follow project guidelines from CLAUDE.md
- Use checklists in `checklists/` subdirectory for systematic assessment


## Workflow

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
**Checklist**: [SECURITY-REVIEW-CHECKLIST.md](checklists/SECURITY-REVIEW-CHECKLIST.md)

Assess:
- Input validation & sanitization
- Injection prevention (SQL, command, XSS, path traversal)
- Authentication & authorization
- Cryptography (encryption, hashing, key management)
- Data protection (secrets, logging exposure)
- API security, headers, CORS, CSRF
- OWASP Top 10 coverage

#### Architecture Review
**Checklist**: [ARCHITECTURAL-REVIEW-CHECKLIST.md](checklists/ARCHITECTURAL-REVIEW-CHECKLIST.md)

Assess:
- CUPID principles (Composable, Unix philosophy, Predictable, Idiomatic, Domain-aligned)
- DDD patterns (bounded contexts, aggregates, domain events)
- Pattern adherence (clean architecture, service boundaries, API design)
- Anti-patterns, performance, scalability, resilience

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


## Report Format

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

Store report at: `<project_root>/.agent_temp/reviews/<feature-name>-code-review-<YYYY-MM-DD>.md`

Return report location to user.
