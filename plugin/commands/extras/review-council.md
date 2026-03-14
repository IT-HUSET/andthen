---
description: Multi-perspective code review using Agent Teams with adversarial debate to validate findings
argument-hint: [Optional - specific files, PR number, or focus area]
---

# Review Council

Multi-perspective code review where specialized reviewers challenge each other's findings through debate, producing validated, high-confidence issues.

**Uses Agent Teams** - Falls back to the `andthen-review-code` skill if Teams unavailable.


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
- **Requires Agent Teams** - Falls back to the `andthen-review-code` skill if unavailable
- **Multi-perspective validation** - Findings must survive two-phase challenge (Devil's Advocate → Synthesis Challenger)
- **Read-only analysis** - No code changes, commits, or modifications during review


## Workflow

### 1. Check Agent Teams Availability

Verify Agent Teams are available by checking that the `TeamCreate` tool exists in your available tools.

If the `TeamCreate` tool is NOT available (experimental feature not enabled):
- Inform user that review-council requires Agent Teams (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`)
- Automatically fall back to the `andthen-review-code` skill with the same arguments
- Exit

### 2. Analyze Review Scope

Determine what's being reviewed to select appropriate council members:

**Gather context:**
- If PR number: `gh pr diff <number>` + `gh pr view <number>`
- Otherwise: `git diff --stat` + `git diff --name-only`
- Check file types, directories, patterns
- Look for requirements docs, specs, or ADRs in recent changes

**Categorize the review:**
- **Product feature** - New functionality, user-facing changes, requirement docs
- **Backend changes** - API endpoints, business logic, data processing
- **Frontend changes** - UI components, state management, styling
- **Database changes** - Migrations, schema, queries
- **Infrastructure** - Config, deployment, build scripts
- **Refactoring** - Code restructuring, pattern changes
- **Bug fix** - Targeted fixes, edge cases

### 3. Select Council Members

Choose 5-7 reviewers from this roster based on scope analysis:

**Available Reviewers:**

**Product & Requirements:**
- **Product Manager** - Feature alignment, user value, requirements match, scope creep, business logic correctness
- **Requirements Analyst** - Acceptance criteria verification, edge case coverage, spec compliance, completeness

**Technical Specialists:**
- **Security Sentinel** - Auth, XSS, CSRF, injection, secrets, input validation, OWASP Top 10, trust boundaries
- **Performance Oracle** - Query optimization, N+1, algorithmic complexity, caching, bundle size, rendering
- **Architecture Strategist** - SOLID principles, coupling/cohesion, patterns, abstractions, maintainability
- **Database Specialist** - Schema design, migrations, indexes, constraints, data integrity, query performance
- **API Designer** - API contracts, versioning, backwards compatibility, REST/GraphQL best practices
- **Frontend Specialist** - Component design, state management, hooks, rendering, bundle optimization
- **Backend Specialist** - Business logic, error handling, data flow, service integration

**Quality & Experience:**
- **UX/Accessibility Advocate** - Usability, error states, WCAG compliance, keyboard nav, responsive design
- **Test Strategist** - Test coverage, test quality, missing cases, test maintainability, integration tests
- **Code Maintainer** - Long-term maintainability, documentation, tech debt, onboarding, code clarity
- **Content Designer** - Prompt quality (clarity, structure, tokens), user-facing text (error messages, docs, UI copy), technical writing, tone consistency

**Always Include:**
- **Devil's Advocate** - Challenges ALL findings during initial review, filters false positives, forces validation through debate
- **Synthesis Challenger** - Reviews AFTER all debates, challenges final conclusions, ensures consistency, validates severity ratings, acts as quality gate

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

### 4. Create Review Council

**IMPORTANT — Use Agent Team tools, NOT regular sub-agents.**
You MUST use the `TeamCreate` tool to create an actual Agent Team. Do NOT use the `Task` tool alone (without `team_name`) — that spawns isolated sub-agents that cannot communicate with each other, which defeats the purpose of the council's adversarial debate workflow.

**Required tool sequence:**
1. `TeamCreate` — Create the team (e.g., `team_name: "review-council"`)
2. `TaskCreate` — Create tasks for each review phase (specialist reviews, debate, synthesis)
3. `Task` with `team_name` param — Spawn each reviewer INTO the team (e.g., `Task(team_name: "review-council", name: "security-sentinel", ...)`)
4. `TaskUpdate` — Track task assignments and completion
5. `SendMessage` — Coordinate inter-agent debate and findings exchange
6. `SendMessage(type: "shutdown_request")` — Gracefully shut down each reviewer when done
7. `TeamDelete` — Clean up team resources

**Reviewer spawn template** (use as prompt when calling `Task` for each reviewer):
```
Review Council for: {SCOPE}
Team: review-council (use TaskList, TaskUpdate, SendMessage to coordinate)

Your role: {reviewer name and focus areas from roster}

Review process (two-phase validation):

PHASE 1 - Initial Review & Debate:
Each specialist reviewer should:
- Analyze the code through their specialized lens
- Report findings with severity (CRITICAL/HIGH/MEDIUM/LOW)
- Provide specific file:line references
- Use the `andthen-review-code` skill for the review

Devil's Advocate should:
- Challenge ALL findings from specialist reviewers
- Ask "why is this actually a problem?"
- Question assumptions and severity ratings
- Force validation through debate
- Help filter false positives
- Engage in back-and-forth (max 2-3 rounds per finding)
- If no consensus after 3 rounds, mark finding as "disputed"

PHASE 2 - Synthesis Review:
After all Phase 1 debates complete, Synthesis Challenger should:
- Review ALL validated findings holistically
- Challenge the final conclusions and synthesis
- Question: "Are severity ratings consistent across findings?"
- Question: "Are multiple related findings actually one larger issue?"
- Question: "Did we miss patterns or systemic issues?"
- Question: "Are any validated findings actually false positives in context?"
- Question: "Is the overall assessment accurate?"
- Act as quality gate - only findings that survive both phases get reported

Final output: Unified report showing findings validated through BOTH phases.
```

### 5. Coordinate Review & Debate

Monitor the two-phase validation process:

**Phase 1 - Initial Review & Debate:**
- Wait for all specialist reviewers to complete initial analysis
- Ensure Devil's Advocate challenges each finding (max 2-3 debate rounds per finding)
- Track findings as: validated, withdrawn, or disputed (if no consensus after 3 rounds)
- **Gate:** All Phase 1 debates resolved

**Phase 2 - Synthesis Review:**
- After all Phase 1 debates complete, Synthesis Challenger reviews holistically
- Challenges final conclusions, severity ratings, and synthesis
- May reclassify, merge, or split findings based on overall context
- **Gate:** Synthesis Challenger completes final validation

### 6. Synthesize Report

Compile findings from all reviewers into unified report:

**Report structure:**
```markdown
# Review Council Report: {Scope}
Date: {YYYY-MM-DD}

## Executive Summary
{Brief overview of what was reviewed, total issues found, validated count}

## CRITICAL Severity (Validated through debate)
{Blocking issues: security vulnerabilities, data loss, core functionality broken}

## HIGH Severity (Validated through debate)
{Issues that survived Devil's Advocate challenge}

## MEDIUM Severity (Validated through debate)
{Issues confirmed after discussion}

## LOW Severity
{Minor issues and suggestions}

## Disputed/Withdrawn
{Findings challenged and withdrawn after debate}

## Key Debates
{Interesting discussions that clarified understanding}

## Recommendations
{Prioritized action items based on validated findings}
```

Store in: `.agent_temp/reviews/{scope}-council-review-{YYYY-MM-DD}.md`

Where `{scope}` is kebab-case identifier: file name (e.g., `auth-module`), PR number (e.g., `pr-123`), or feature name from arguments.

### 7. Clean Up

1. Use `SendMessage(type: "shutdown_request")` for each council reviewer
2. Wait for shutdown confirmations
3. Use `TeamDelete` to remove team and task files

## Report Location

Inform user of final report location when complete.
