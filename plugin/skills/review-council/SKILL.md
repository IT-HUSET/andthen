---
name: andthen.review-council
description: Multi-perspective code review with adversarial debate to validate findings
argument-hint: [Optional - specific files, PR number, or focus area]
---

# Review Council

Multi-perspective code review where specialized reviewers challenge each other's findings through adversarial debate, producing validated, high-confidence issues.

Uses **parallel sub-agents** _(if supported by your coding agent)_ for concurrent reviews, otherwise executes sequentially.


## Variables

ARGUMENTS: $ARGUMENTS


## Usage

```
/review-council                          # Review recent changes
/review-council --pr 123                 # Review specific PR
/review-council src/auth/                # Review specific path
/review-council "security"               # Focus on security aspect
```


## Instructions

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work
- **Multi-perspective validation** — Findings must survive two-phase challenge (Devil's Advocate → Synthesis Challenger)
- **Read-only analysis** — No code changes, commits, or modifications during review


## Workflow

### 1. Analyze Review Scope

Determine what's being reviewed to select appropriate council members:

**Gather context:**
- If PR number: `gh pr diff <number>` + `gh pr view <number>`
- Otherwise: `git diff --stat` + `git diff --name-only`
- Check file types, directories, patterns
- Look for requirements docs, specs, or ADRs in recent changes

**Categorize the review:**
- **Product feature** — New functionality, user-facing changes, requirement docs
- **Backend changes** — API endpoints, business logic, data processing
- **Frontend changes** — UI components, state management, styling
- **Database changes** — Migrations, schema, queries
- **Infrastructure** — Config, deployment, build scripts
- **Refactoring** — Code restructuring, pattern changes
- **Bug fix** — Targeted fixes, edge cases

### 2. Select Council Members

Choose 5-7 reviewers from this roster based on scope analysis:

**Available Reviewers:**

**Product & Requirements:**
- **Product Manager** — Feature alignment, user value, requirements match, scope creep, business logic correctness
- **Requirements Analyst** — Acceptance criteria verification, edge case coverage, spec compliance, completeness

**Technical Specialists:**
- **Security Sentinel** — Auth, XSS, CSRF, injection, secrets, input validation, OWASP Top 10, trust boundaries
- **Performance Oracle** — Query optimization, N+1, algorithmic complexity, caching, bundle size, rendering
- **Architecture Strategist** — SOLID principles, coupling/cohesion, patterns, abstractions, maintainability
- **Database Specialist** — Schema design, migrations, indexes, constraints, data integrity, query performance
- **API Designer** — API contracts, versioning, backwards compatibility, REST/GraphQL best practices
- **Frontend Specialist** — Component design, state management, hooks, rendering, bundle optimization
- **Backend Specialist** — Business logic, error handling, data flow, service integration

**Quality & Experience:**
- **UX/Accessibility Advocate** — Usability, error states, WCAG compliance, keyboard nav, responsive design
- **Test Strategist** — Test coverage, test quality, missing cases, test maintainability, integration tests
- **Code Maintainer** — Long-term maintainability, documentation, tech debt, onboarding, code clarity
- **Content Designer** — Prompt quality (clarity, structure, tokens), user-facing text (error messages, docs, UI copy), technical writing, tone consistency

**Always Include:**
- **Devil's Advocate** — Challenges ALL findings during initial review, filters false positives, forces validation through debate
- **Synthesis Challenger** — Reviews AFTER all debates, challenges final conclusions, ensures consistency, validates severity ratings, acts as quality gate

**Selection examples:**

*Product feature (new user export):*
→ Product Manager, Requirements Analyst, Security Sentinel, Content Designer (prompts/messages), Devil's Advocate, Synthesis Challenger (6)

*Backend API changes:*
→ Security Sentinel, Performance Oracle, API Designer, Backend Specialist, Devil's Advocate, Synthesis Challenger (6)

*Frontend UI update:*
→ UX/Accessibility, Performance Oracle, Frontend Specialist, Architecture Strategist, Devil's Advocate, Synthesis Challenger (6)

*Database migration:*
→ Security Sentinel, Performance Oracle, Database Specialist, Backend Specialist, Devil's Advocate, Synthesis Challenger (6)

*Bug fix (small):*
→ Requirements Analyst, Architecture Strategist, Test Strategist, Devil's Advocate, Synthesis Challenger (5)

*Infrastructure/config:*
→ Security Sentinel, Architecture Strategist, Code Maintainer, Devil's Advocate, Synthesis Challenger (5)

**Gate:** 5-7 reviewers selected (always include Devil's Advocate + Synthesis Challenger)

### 3. Phase 1 — Specialist Reviews

Run specialist reviews using **parallel sub-agents** _(if supported by your coding agent; otherwise execute sequentially)_.

Spawn one sub-agent per specialist reviewer (excluding Devil's Advocate and Synthesis Challenger — those run in later phases). Each sub-agent receives this prompt:

```
You are the {reviewer name} on a Review Council for: {SCOPE}

Your focus areas: {focus areas from roster}

Review process:
1. Analyze the code through your specialized lens
2. Use the `andthen.review-code` skill for the review
3. Report findings with severity (CRITICAL/HIGH/MEDIUM/LOW)
4. Provide specific file:line references
5. For each finding, explain WHY it's a problem and suggest a fix

Note: The `andthen.review-code` skill may not be available in all environments. If unavailable, perform the review directly using your own analysis capabilities.

Output format per finding:
- **Severity**: CRITICAL/HIGH/MEDIUM/LOW
- **Location**: file:line
- **Finding**: What's wrong
- **Why it matters**: Impact if not addressed
- **Suggested fix**: How to resolve
```

Collect all findings from specialist sub-agents.

**Gate:** All specialist reviews complete, findings collected

### 4. Phase 2 — Devil's Advocate Challenge

Spawn a **sub-agent** _(if supported by your coding agent; otherwise execute directly)_ as the Devil's Advocate. Provide ALL collected findings as input:

```
You are the Devil's Advocate on a Review Council for: {SCOPE}

You have received {N} findings from specialist reviewers. Your job is to challenge every single finding:

For each finding, ask:
- "Is this actually a problem, or is it acceptable in this context?"
- "Is the severity rating justified?"
- "Could this be a false positive?"
- "Is there a simpler explanation or existing mitigation?"

For each finding, output one of:
- **VALIDATED** — Finding holds up under scrutiny. Explain why.
- **DOWNGRADED** — Finding is real but severity is too high. Suggest new severity and explain.
- **WITHDRAWN** — Finding is a false positive or not applicable. Explain why.
- **DISPUTED** — Reasonable arguments both ways. Note the tension.

Findings to challenge:
{all collected findings}
```

Apply the Devil's Advocate's verdicts to the findings list.

**Gate:** All findings challenged, verdicts applied

### 5. Phase 3 — Synthesis Review

Spawn a **sub-agent** _(if supported by your coding agent; otherwise execute directly)_ as the Synthesis Challenger. Provide the validated/downgraded findings:

```
You are the Synthesis Challenger on a Review Council for: {SCOPE}

You are the final quality gate. Review ALL findings that survived the Devil's Advocate phase holistically:

Questions to answer:
- "Are severity ratings consistent across findings?"
- "Are multiple related findings actually one larger issue?"
- "Did we miss patterns or systemic issues?"
- "Are any validated findings actually false positives in context?"
- "Is the overall assessment accurate?"

For each finding, confirm or reclassify. You may also:
- Merge related findings into a single higher-severity issue
- Split a finding that covers multiple distinct problems
- Add a new finding if you spot a systemic pattern the specialists missed

Output: Final validated findings with confirmed severity ratings.

Findings to review:
{validated and downgraded findings from Phase 2}
```

**Gate:** Synthesis Challenger completes final validation

### 6. Synthesize Report

Compile findings from all phases into unified report:

**Report structure:**
```markdown
# Review Council Report: {Scope}
Date: {YYYY-MM-DD}

## Executive Summary
{Brief overview of what was reviewed, total issues found, validated count}

## Council Members
{List of reviewers selected and their focus areas}

## CRITICAL Severity (Validated)
{Blocking issues: security vulnerabilities, data loss, core functionality broken}

## HIGH Severity (Validated)
{Issues that survived Devil's Advocate challenge}

## MEDIUM Severity (Validated)
{Issues confirmed after challenge}

## LOW Severity
{Minor issues and suggestions}

## Withdrawn/Downgraded
{Findings challenged and withdrawn or downgraded, with reasoning}

## Disputed
{Findings where reasonable arguments exist both ways}

## Recommendations
{Prioritized action items based on validated findings}
```

**Report file naming:**
- **Agent identifier**: Determine your agent short name (e.g., `claude`, `codex`, `cursor`, `aider`). If uncertain, use `agent`.
- **File collision avoidance**: Before writing, check if the target filename already exists. If it does, append an incrementing suffix: `-2`, `-3`, etc. **Never overwrite existing reports!**

Store in: `<project_root>/.agent_temp/reviews/<scope>-council-review-<agent>-<YYYY-MM-DD>.md`

Where `<scope>` is kebab-case identifier: file name (e.g., `auth-module`), PR number (e.g., `pr-123`), or feature name from arguments.

## Report Location

When complete, print the report's **relative path from the project root** (e.g., `.agent_temp/reviews/auth-module-council-review-claude-2026-03-15.md`). Do not use absolute paths.
