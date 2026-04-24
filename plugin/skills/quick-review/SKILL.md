---
description: Quick in-conversation skill for adversarial review of recent changes in fresh context. Use mid-conversation to sanity-check work before moving on. Trigger on 'quick review this', 'sanity-check this', 'give this a quick pass'.
user-invocable: true
argument-hint: "[optional focus or scope] [--fix] [--auto|--headless]"
---

# Quick Review

Lightweight, ad-hoc review of recent work in the current conversation. Internally delegates the critique to a fresh-context sub-agent to catch errors, inconsistencies, and missed edge cases that in-context work tends to overlook.

`andthen:quick-review` is a **skill**, not an agent type. Invoke it via `/andthen:quick-review` or the Skill tool — do not pass it as `subagent_type`.

**For thorough reviews, start with** the `andthen:review` **skill**. Pass `--council` when you explicitly want multi-perspective adversarial review.


## VARIABLES

FOCUS: $ARGUMENTS (strip any leading flag tokens like `--fix`, `--auto`, or `--headless` before interpreting as focus)


### Optional Flags
- `--fix` → after evaluating findings, apply the **accepted** ones directly (skip the "offer to fix" prompt). Dismissed findings stay dismissed — the Accept/Dismiss step in Phase 4 remains the guardrail. If zero findings are accepted, report that plainly and stop — nothing to fix.
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- This is a **lightweight mid-conversation review** – a fast, focused checkpoint scoped to recent changes rather than a full formal pass.
- The **review** sub-agent is read-only. Only the outer skill may edit files, and only in Phase 4 when `--fix` is set.
- The sub-agent reviews in a **fresh context** to avoid confirmation bias.
- Anti-leniency: if the sub-agent identifies a problem, it is a problem. Do not rationalize issues away.
- Output findings inline — no separate report file.
- **Automation mode** (`--auto` / `--headless`) — never ask the user what to do next. If `--fix` is present, apply accepted findings directly; otherwise remain read-only and return accepted findings for the orchestrator to decide on. Stop with `BLOCKED:` (listing what could not be resolved, e.g. no change set, unreadable target) only when the review scope cannot be resolved.


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

Present accepted findings to the user as a concise inline list.

- **Without `--fix`**: if there are actionable issues, offer to fix them unless `AUTO_MODE=true`. In `AUTO_MODE`, report the accepted findings and stop read-only so the orchestrator can decide whether to invoke a fixing step. If no significant issues were found, state that clearly and move on.
- **With `--fix`**: apply the accepted findings directly with minimal, surgical edits — one coherent patch set, no scope creep, no "nearby cleanup". Then re-run the minimum verification that proves the fixes hold (type-check, relevant tests, or targeted re-read). Report what changed in one tight line per fix.

Do not produce a report file. Do not add a summary preamble. Keep it tight.
