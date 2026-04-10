---
description: Multi-perspective code review with adversarial debate to validate findings. Trigger on 'council review', 'adversarial review', 'multi-reviewer'.
argument-hint: "[Optional - specific files, PR number, or focus area]"
---

# Review Council


Multi-perspective code review where specialized reviewers challenge each other's findings through adversarial debate, producing validated, high-confidence issues.

Uses **parallel sub-agents** _(if supported by your coding agent)_ for concurrent reviews, otherwise executes sequentially.


## VARIABLES

ARGUMENTS: $ARGUMENTS


## INSTRUCTIONS

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work
- **Multi-perspective validation** – Findings must survive two-phase challenge (Devil's Advocate → Synthesis Challenger)
- **Read-only analysis** – No code changes, commits, or modifications during review


## GOTCHAS
- Selecting too many reviewers (>7) dilutes debate quality – 5 is the sweet spot for most reviews
- Devil's Advocate challenge phase gets skipped under context pressure – it's the most valuable phase
- Reviewers agreeing too easily – if no findings survive challenge, the review was too shallow


## WORKFLOW

### 1. Analyze Review Scope

Gather context:
- If PR number: `gh pr diff <number>` + `gh pr view <number>`
- Otherwise: `git diff --stat` + `git diff --name-only`
- Check file types, directories, patterns; look for specs or ADRs in recent changes

Categorize: product feature, backend, frontend, database, infrastructure, refactoring, or bug fix.

### 2. Select Council Members

Choose 5-7 reviewers from `${CLAUDE_PLUGIN_ROOT}/references/reviewer-roster.md` based on scope analysis.
Start from the closest selection example in that reference, then adapt to the actual review surface.
Always include **Devil's Advocate** and **Synthesis Challenger**.

**Gate:** 5-7 reviewers selected (always include Devil's Advocate + Synthesis Challenger)

### 3. Phase 1 – Specialist Reviews

Run specialist reviews using **parallel sub-agents** _(if supported; otherwise execute sequentially)_.

Spawn one sub-agent per specialist reviewer (excluding Devil's Advocate and Synthesis Challenger). Each sub-agent receives:

```
You are the {reviewer name} on a Review Council for: {SCOPE}

Your focus areas: {focus areas from roster}

Review process:
1. Analyze the code through your specialized lens
2. Use the `andthen:review-code` skill for the review
3. Report findings with severity (CRITICAL/HIGH/MEDIUM/LOW)
4. Provide specific file:line references
5. For each finding, explain WHY it's a problem and suggest a fix

Note: The `andthen:review-code` skill may not be available in all environments. If unavailable, perform the review directly using your own analysis capabilities.

Output format per finding:
- **Severity**: CRITICAL/HIGH/MEDIUM/LOW
- **Location**: file:line
- **Finding**: What's wrong
- **Why it matters**: Impact if not addressed
- **Suggested fix**: How to resolve
```

**Gate:** All specialist reviews complete, findings collected

### 4. Phase 2 – Devil's Advocate Challenge

Spawn a **sub-agent** as the Devil's Advocate.
Use `${CLAUDE_PLUGIN_ROOT}/references/adversarial-challenge.md` (`Devil's Advocate`) with:
- **Role**: `Devil's Advocate on a Review Council for: {SCOPE}`
- **Context block**: `You have received {N} findings from specialist reviewers.`
- **Questions**: Is this actually a problem? Is severity justified? Could this be a false positive? Is there an existing mitigation?
- **Verdicts**: `VALIDATED`, `DOWNGRADED`, `WITHDRAWN`, `DISPUTED`
- **Findings payload**: `{all collected findings}`

Apply the Devil's Advocate's verdicts to the findings list.

**Gate:** All findings challenged, verdicts applied

### 5. Phase 3 – Synthesis Review

Spawn a **sub-agent** as the Synthesis Challenger.
Use `${CLAUDE_PLUGIN_ROOT}/references/adversarial-challenge.md` (`Synthesis Challenger`) with:
- **Role**: `Synthesis Challenger on a Review Council for: {SCOPE}`
- **Context block**: `You are the final quality gate. Review all findings that survived the Devil's Advocate phase holistically.`
- **Questions**: Are severity ratings consistent? Are related findings actually one larger issue? Did we miss systemic patterns? Are any validated findings false positives in context?
- **Optional extra rules**: `You may merge related findings, split a finding covering multiple distinct problems, or add a new finding only if you spot a systemic pattern the specialists missed.`
- **Findings payload**: `{validated and downgraded findings from Phase 2}`

**Gate:** Synthesis Challenger completes final validation

### 6. Synthesize Report

Compile findings into unified report:

```markdown
# Review Council Report: {Scope}
Date: {YYYY-MM-DD}

## Executive Summary
{Brief overview: what was reviewed, total issues, validated count}

## Council Members
{Reviewers and focus areas}

## CRITICAL Severity (Validated)
## HIGH Severity (Validated)
## MEDIUM Severity (Validated)
## LOW Severity

## Withdrawn/Downgraded
{Findings challenged and withdrawn or downgraded, with reasoning}

## Disputed
{Findings where reasonable arguments exist both ways}

## Recommendations
{Prioritized action items}
```

**Report output conventions**: Follow `${CLAUDE_PLUGIN_ROOT}/references/report-output-conventions.md` with:
- **Report suffix**: `council-review`
- **Scope placeholder**: `scope`
- **Spec-directory rule**: the review relates to a spec/FIS directory or feature with an associated spec directory from the Project Document Index
- **Target-directory rule**: the review target is a specific file or localized directory, so the report belongs next to the primary review target
