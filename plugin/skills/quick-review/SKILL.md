---
description: Quick in-conversation review of recent changes using a fresh-context sub-agent for adversarial critique. Use mid-conversation to sanity-check work before moving on. Trigger on 'quick review this', 'sanity-check this', 'give this a quick pass'.
user-invocable: true
argument-hint: "[optional focus or scope]"
---

# Quick Review

Lightweight, ad-hoc review of recent work in the current conversation. Spawns a fresh-context sub-agent to critique what was just done — catching errors, inconsistencies, and missed edge cases that in-context work tends to overlook.

**For thorough reviews, start with:** `andthen:review`. Use `andthen:review-council` when you explicitly want multi-perspective adversarial review.


## VARIABLES

FOCUS: $ARGUMENTS


## INSTRUCTIONS

- This is a **mid-conversation checkpoint**, not a formal review. Keep it fast and focused.
- **Read-only analysis.** Do not modify any files.
- The sub-agent must review in a **fresh context** to avoid confirmation bias from the work just done.
- Apply the anti-leniency principle: if the sub-agent identifies a problem, it IS a problem. Do not rationalize issues away.
- Output findings inline in the conversation — no separate report file.


## GOTCHAS
- Sending the sub-agent too little context (it needs to understand what was done and why)
- Sending the sub-agent too much context (entire files when only a section changed)
- Rationalizing away findings because "I just wrote that and it seemed fine"
- Using this as a substitute for a proper review on significant changes


## WORKFLOW

### 1. Determine Scope

Identify what to review, in priority order:

1. **Explicit focus**: If `FOCUS` is provided, use it to narrow scope
2. **Pending changes**: Run `git diff --stat` and `git diff` for uncommitted changes
3. **Recent conversation work**: If no pending changes, identify artifacts created or modified in this conversation (specs, configs, docs, etc.)

Collect the **change set** — the specific content to review. Keep it focused: only include what actually changed, with enough surrounding context for comprehension.

**Gate**: Change set is identified and bounded

### 2. Classify and Frame

Determine what type of work was done to frame the review appropriately:

| Change type | Review lens |
|---|---|
| Code (new or modified) | Correctness, edge cases, consistency with existing patterns, error handling |
| Specification / plan | Completeness, clarity, implementability, contradictions |
| Configuration | Safety, correctness, environment consistency |
| Documentation | Accuracy, clarity, completeness |
| Prompt / skill | Clarity of intent, edge case handling, instruction consistency |
| Mixed | Apply relevant lenses per artifact |

### 3. Sub-Agent Review

Spawn a **single sub-agent** with the following prompt structure:

```
You are a critical reviewer performing an adversarial review of recent changes.

Your job is to find real problems — errors, inconsistencies, missed edge cases,
contradictions with existing patterns, and gaps. You are not here to validate
or praise the work.

## Anti-Leniency Rules
- If you identify a problem, it IS a problem. Do not talk yourself out of it.
- "Works on the happy path" is not a pass — check edge cases and error paths.
- Do not hedge with "could be an issue" or "might cause problems" — be definitive.
- Substance over surface: check that things are actually complete, not just present.

## Context
{what was done and why — brief description of the task/goal}

## Review Lens
{applicable lens from classification step}

## Changes to Review
{the change set — diffs, file contents, or artifact content}

## Review Instructions
1. Review the changes through the specified lens
2. Check for internal consistency within the changes
3. Check for consistency with the surrounding codebase/project context
4. Identify concrete issues only — no speculative or hypothetical problems
5. For each finding, state: what's wrong, where, and why it matters
6. If no significant issues found, say so plainly — do not invent findings

Report findings as a concise list. No preamble, no summary section, no severity table.
Format: one finding per item, each with location and a clear statement of the problem.
```

Use the `general-purpose` agent type. Provide sufficient context in the prompt for the sub-agent to do its job without needing to explore the codebase extensively — include relevant diffs, file excerpts, and project context inline.

**Gate**: Sub-agent review complete

### 4. Evaluate and Report

Review the sub-agent's findings. For each:
- **Accept**: the finding is valid and actionable
- **Dismiss**: the finding is based on a misunderstanding of the context (explain briefly why)

Present accepted findings to the user as a concise inline list. If there are actionable issues, offer to fix them. If no significant issues were found, state that clearly and move on.

Do not produce a report file. Do not add a summary preamble. Keep it tight.
