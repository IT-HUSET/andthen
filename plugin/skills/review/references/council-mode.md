# Council Mode

Multi-perspective code review: 5–7 specialized reviewers challenge each other's findings through adversarial debate, producing validated, high-confidence issues. Load this reference when running `andthen:review --council`, or when code mode auto-escalates to council because the scope spans multiple concerns (security, performance, architecture, UX), the surface is high-risk (auth, payments, data integrity), or the user asked for "multi-perspective" / "adversarial" / "thorough" review.

Council mode augments **code mode** (or the code sub-pass of mixed mode) — it does not apply to `doc` or `gap` alone.

Companion references:
- `reviewer-roster.md` — reviewer catalog and selection examples
- `lens-code.md` — the code-review rubric each specialist applies
- `adversarial-challenge.md` — prompt templates for Devil's Advocate and Synthesis Challenger


## Gotchas

- Selecting too many reviewers (>7) dilutes debate quality — 5 is the sweet spot
- Skipping Devil's Advocate under context pressure — it's the most valuable phase
- Reviewers agreeing too easily — if no findings survive challenge, the review was too shallow
- Forcing `--team` when Agent Teams are unavailable — fall back to sub-agents unless `--team` was explicit


## 1. Determine Execution Mode

Check whether Agent Teams are available by verifying that team creation tools exist (e.g. `TeamCreate`):
- **Agent Teams available** (or `--team` flag) → Agent Teams Path (§3a)
- **Agent Teams unavailable, no `--team`** → Sub-Agent Path (§3b)
- **Agent Teams unavailable, `--team` present** → inform the user that it requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and exit


## 2. Select Council Members

Choose 5–7 reviewers from `reviewer-roster.md` based on the review scope (see the Selection Examples in that reference). Always include **Devil's Advocate** and **Synthesis Challenger**.

**Gate:** 5–7 reviewers selected (always include Devil's Advocate + Synthesis Challenger)


## 3a. Agent Teams Path

Use Agent Teams (not regular sub-agents) so reviewers share a task list and can debate in real time. Regular sub-agents are isolated and cannot communicate.

1. Create the team (e.g., `name: "review-council"`)
2. Create tasks for each phase (specialist reviews, debate, synthesis)
3. Spawn each reviewer into the team (`team_name: "review-council"`, `name: "<reviewer>"`)
4. Track assignments and completion
5. Use inter-agent messaging to coordinate debate
6. Send shutdown requests when done; delete the team to clean up

**Reviewer spawn template:**
```
Review Council for: {SCOPE}
Team: review-council (use the shared task list and inter-agent messaging to coordinate)

Your role: {reviewer name and focus areas from `reviewer-roster.md`}

Review process (two-phase validation):

PHASE 1 - Initial Review & Debate:
Each specialist reviewer should:
- Analyze the code through their specialized lens
- Report findings with severity (CRITICAL/HIGH/MEDIUM/LOW)
- Provide specific file:line references
- Use `lens-code.md` rubric inline (if unavailable, perform the review directly)

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

Final output: Unified findings validated through BOTH phases.
```

**Phase 1 – Initial Review & Debate:** wait for specialist completion; ensure Devil's Advocate challenges each finding (max 2–3 rounds); track findings as validated, withdrawn, or disputed. **Gate:** Phase 1 debates resolved.

**Phase 2 – Synthesis Review:** Synthesis Challenger reviews holistically after Phase 1; may reclassify, merge, or split findings. **Gate:** Synthesis complete.

**Clean up:** send shutdown requests, await confirmations, delete the team.


## 3b. Sub-Agent Path

Run specialist reviews using **parallel sub-agents**.

**Phase 1 – Specialist Reviews:** spawn one sub-agent per specialist (excluding Devil's Advocate and Synthesis Challenger):

```
You are the {reviewer name} on a Review Council for: {SCOPE}

Your focus areas: {focus areas from roster}

Review process:
1. Analyze the code through your specialized lens using the `lens-code.md` rubric
2. Report findings with severity (CRITICAL/HIGH/MEDIUM/LOW)
3. Provide specific file:line references
4. For each finding, explain WHY it's a problem and suggest a fix

Output format per finding:
- **Severity**: CRITICAL/HIGH/MEDIUM/LOW
- **Location**: file:line
- **Finding**: What's wrong
- **Why it matters**: Impact if not addressed
- **Suggested fix**: How to resolve
```

**Gate:** Specialist reviews complete; findings collected.

**Phase 2 – Devil's Advocate Challenge:** spawn a sub-agent as the Devil's Advocate. Use `adversarial-challenge.md` (`Devil's Advocate`) with:
- **Role**: `Devil's Advocate on a Review Council for: {SCOPE}`
- **Context block**: `You have received {N} findings from specialist reviewers.`
- **Questions**: Is this actually a problem? Is severity justified? Could this be a false positive? Is there an existing mitigation?
- **Verdicts**: `VALIDATED`, `DOWNGRADED`, `WITHDRAWN`, `DISPUTED`
- **Findings payload**: `{all collected findings}`

Apply the verdicts to the findings list. **Gate:** findings challenged, verdicts applied.

**Phase 3 – Synthesis Review:** spawn a sub-agent as the Synthesis Challenger. Use `adversarial-challenge.md` (`Synthesis Challenger`) with:
- **Role**: `Synthesis Challenger on a Review Council for: {SCOPE}`
- **Context block**: `You are the final quality gate. Review all findings that survived the Devil's Advocate phase holistically.`
- **Questions**: Are severity ratings consistent? Are related findings actually one larger issue? Did we miss systemic patterns? Are any validated findings false positives in context?
- **Optional extra rules**: `You may merge related findings, split a finding covering multiple distinct problems, or add a new finding only if you spot a systemic pattern the specialists missed.`
- **Findings payload**: `{validated and downgraded findings from Phase 2}`

**Gate:** Synthesis complete.


## 4. Report Structure

When the caller writes a consolidated report, use this structure — only findings that survived both debate phases appear in the severity sections:

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
