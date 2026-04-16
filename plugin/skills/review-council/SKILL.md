---
description: Multi-perspective code review with adversarial debate to validate findings. Supports Agent Teams (real-time debate) and sub-agents (sequential fallback). Trigger on 'council review', 'adversarial review', 'multi-reviewer', 'multiple reviewers', 'team review'.
argument-hint: "[Optional - specific files, PR number, or focus area] [--team]"
---

# Review Council


Multi-perspective code review where specialized reviewers challenge each other's findings through adversarial debate, producing validated, high-confidence issues.

Supports two execution modes:
- **Agent Teams** – real-time inter-agent debate when Agent Teams are available (or forced with `--team`)
- **Sub-agents** – parallel sub-agents with sequential debate phases (portable fallback)


## VARIABLES

ARGUMENTS: $ARGUMENTS

### Optional Flags
- `--team` → force Agent Teams execution mode; error if unavailable


## INSTRUCTIONS

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work
- **Multi-perspective validation** – Findings must survive two-phase challenge (Devil's Advocate → Synthesis Challenger)
- **Read-only analysis** – No code changes, commits, or modifications during review


## GOTCHAS
- Selecting too many reviewers (>7) dilutes debate quality – 5 is the sweet spot for most reviews
- Devil's Advocate challenge phase gets skipped under context pressure – it's the most valuable phase
- Reviewers agreeing too easily – if no findings survive challenge, the review was too shallow
- Falling back gracefully when Agent Teams is unavailable and `--team` was not explicitly requested


## WORKFLOW

### 1. Determine Execution Mode

Check whether Agent Teams are available by verifying that team creation tools exist (e.g. `TeamCreate`).

- **Agent Teams available** (or `--team` flag) → use Agent Teams mode (Step 4a)
- **Agent Teams unavailable, no `--team` flag** → use sub-agent mode (Step 4b)
- **Agent Teams unavailable, `--team` flag present** → inform user it requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and exit

### 2. Analyze Review Scope

Gather context:
- If PR number: `gh pr diff <number>` + `gh pr view <number>`
- Otherwise: `git diff --stat` + `git diff --name-only`
- Check file types, directories, patterns; look for specs or ADRs in recent changes

Categorize: product feature, backend, frontend, database, infrastructure, refactoring, or bug fix.

### 3. Select Council Members

Choose 5-7 reviewers from `${CLAUDE_PLUGIN_ROOT}/references/reviewer-roster.md` based on scope analysis.
Start from the closest selection example in that reference, then adapt to the actual review surface.
Always include **Devil's Advocate** and **Synthesis Challenger**.

**Gate:** 5-7 reviewers selected (always include Devil's Advocate + Synthesis Challenger)

### 4a. Execute Reviews – Agent Teams Mode

**Use this path when Agent Teams are available (Step 1).**

**IMPORTANT – Use Agent Teams, NOT regular sub-agents.**
Reviewers must be spawned into the team (with `team_name` and `name`) so they share a task list and can debate in real time. Regular sub-agents are isolated and cannot communicate.

**Workflow:**
1. Create the team (e.g., name: `"review-council"`)
2. Create tasks for each review phase (specialist reviews, debate, synthesis)
3. Spawn each reviewer into the team (`team_name: "review-council"`, `name: "<reviewer>"`)
4. Track task assignments and completion
5. Use inter-agent messaging to coordinate debate and findings exchange
6. Send shutdown requests when done
7. Delete the team to clean up resources

**Reviewer spawn template:**
```
Review Council for: {SCOPE}
Team: review-council (use the shared task list and inter-agent messaging to coordinate)

Your role: {reviewer name and focus areas from `${CLAUDE_PLUGIN_ROOT}/references/reviewer-roster.md`}

Review process (two-phase validation):

PHASE 1 - Initial Review & Debate:
Each specialist reviewer should:
- Analyze the code through their specialized lens
- Report findings with severity (CRITICAL/HIGH/MEDIUM/LOW)
- Provide specific file:line references
- Use the `andthen:review-code` skill for the review (if unavailable, perform the review directly)

Devil's Advocate should:
- Challenge ALL findings from specialist reviewers
- Question assumptions and severity ratings; force validation through debate
- Engage in back-and-forth (max 2-3 rounds per finding)
- If no consensus after 3 rounds, mark finding as "disputed"

PHASE 2 - Synthesis Review:
After all Phase 1 debates complete, Synthesis Challenger should:
- Review ALL validated findings holistically
- Question severity consistency, merged issues, missed patterns, false positives
- Act as quality gate — only findings surviving both phases get reported

Final output: Unified report showing findings validated through BOTH phases.
```

**Phase 1 – Initial Review & Debate:**
- Wait for all specialist reviewers to complete initial analysis
- Ensure Devil's Advocate challenges each finding (max 2-3 debate rounds)
- Track findings as: validated, withdrawn, or disputed

**Gate:** All Phase 1 debates resolved

**Phase 2 – Synthesis Review:**
- Synthesis Challenger reviews holistically after all Phase 1 debates complete
- May reclassify, merge, or split findings based on overall context

**Gate:** Synthesis Challenger completes final validation

**Clean up:**
1. Send shutdown requests to each council reviewer
2. Wait for shutdown confirmations
3. Delete the team to remove team and task files

Then proceed to **Step 5. Synthesize Report**.

### 4b. Execute Reviews – Sub-Agent Mode

**Use this path when Agent Teams are unavailable (Step 1).**

Run specialist reviews using **parallel sub-agents** _(if supported; otherwise execute sequentially)_.

**Phase 1 – Specialist Reviews:**

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

**Phase 2 – Devil's Advocate Challenge:**

Spawn a **sub-agent** as the Devil's Advocate.
Use `${CLAUDE_PLUGIN_ROOT}/references/adversarial-challenge.md` (`Devil's Advocate`) with:
- **Role**: `Devil's Advocate on a Review Council for: {SCOPE}`
- **Context block**: `You have received {N} findings from specialist reviewers.`
- **Questions**: Is this actually a problem? Is severity justified? Could this be a false positive? Is there an existing mitigation?
- **Verdicts**: `VALIDATED`, `DOWNGRADED`, `WITHDRAWN`, `DISPUTED`
- **Findings payload**: `{all collected findings}`

Apply the Devil's Advocate's verdicts to the findings list.

**Gate:** All findings challenged, verdicts applied

**Phase 3 – Synthesis Review:**

Spawn a **sub-agent** as the Synthesis Challenger.
Use `${CLAUDE_PLUGIN_ROOT}/references/adversarial-challenge.md` (`Synthesis Challenger`) with:
- **Role**: `Synthesis Challenger on a Review Council for: {SCOPE}`
- **Context block**: `You are the final quality gate. Review all findings that survived the Devil's Advocate phase holistically.`
- **Questions**: Are severity ratings consistent? Are related findings actually one larger issue? Did we miss systemic patterns? Are any validated findings false positives in context?
- **Optional extra rules**: `You may merge related findings, split a finding covering multiple distinct problems, or add a new finding only if you spot a systemic pattern the specialists missed.`
- **Findings payload**: `{validated and downgraded findings from Phase 2}`

**Gate:** Synthesis Challenger completes final validation

### 5. Synthesize Report

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
