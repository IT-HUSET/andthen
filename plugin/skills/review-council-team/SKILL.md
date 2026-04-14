---
description: Multi-perspective code review using Agent Teams with real-time adversarial debate (requires Agent Teams). Trigger on 'council review with agents', 'team review', 'multi-reviewer team review'.
argument-hint: "[Optional - specific files, PR number, or focus area]"
---

# Review Council (Agent Teams)


Multi-perspective code review where specialized reviewers challenge each other's findings through real-time debate, producing validated, high-confidence issues.

**Requires Agent Teams** – Falls back to the `andthen:review-council` skill if Teams unavailable.


## VARIABLES

ARGUMENTS: $ARGUMENTS


## INSTRUCTIONS

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work
- **Requires Agent Teams** – Falls back to the `andthen:review-council` skill if unavailable
- **Multi-perspective validation** – Findings must survive two-phase challenge (Devil's Advocate → Synthesis Challenger)
- **Read-only analysis** – No code changes, commits, or modifications during review


## GOTCHAS
- Selecting too many reviewers (>7) dilutes debate quality – 5 is the sweet spot for most reviews
- Devil's Advocate challenge phase gets skipped under context pressure – it's the most valuable phase
- Reviewers agreeing too easily — if no findings survive challenge, the review was too shallow; flag this to the user
- Falling back gracefully when Agent Teams is unavailable


## WORKFLOW

### 1. Check Agent Teams Availability

Verify Agent Teams are available by checking that team creation tools exist (e.g. `TeamCreate`).

If NOT available:
- Suggest the `andthen:review-council` skill instead (portable, no Agent Teams required)
- If user specifically wants Agent Teams, inform them it requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Exit

### 2. Analyze Scope & Select Council

Follow the same scope analysis and reviewer selection as `andthen:review-council`:
- Gather context: `gh pr diff/view` for PRs, otherwise `git diff --stat/--name-only`
- Choose 5-7 reviewers from `${CLAUDE_PLUGIN_ROOT}/references/reviewer-roster.md`
- Always include **Devil's Advocate** and **Synthesis Challenger**

**Gate:** 5-7 reviewers selected

### 3. Create Review Council (Agent Teams)

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
- Use the `andthen:review-code` skill for the review

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

### 4. Coordinate Review & Debate

**Phase 1 - Initial Review & Debate:**
- Wait for all specialist reviewers to complete initial analysis
- Ensure Devil's Advocate challenges each finding (max 2-3 debate rounds)
- Track findings as: validated, withdrawn, or disputed

**Gate:** All Phase 1 debates resolved

**Phase 2 - Synthesis Review:**
- Synthesis Challenger reviews holistically after all Phase 1 debates complete
- May reclassify, merge, or split findings based on overall context

**Gate:** Synthesis Challenger completes final validation

### 5. Synthesize Report & Clean Up

Compile findings into a unified report matching the structure in `andthen:review-council`.

**Report output conventions**: Follow `${CLAUDE_PLUGIN_ROOT}/references/report-output-conventions.md` with:
- **Report suffix**: `council-review`
- **Scope placeholder**: `scope`
- **Spec-directory rule**: the review relates to a spec/FIS directory or feature with an associated spec directory from the Project Document Index
- **Target-directory rule**: the review target is a specific file or localized directory, so the report belongs next to the primary review target

**Clean up:**
1. Send shutdown requests to each council reviewer
2. Wait for shutdown confirmations
3. Delete the team to remove team and task files

When complete, print the report's **relative path from the project root**.
