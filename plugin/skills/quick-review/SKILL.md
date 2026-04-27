---
description: Quick in-conversation skill for red-team review of recent changes in fresh context. Use mid-conversation to sanity-check work before moving on. Trigger on 'quick review this', 'sanity-check this', 'give this a quick pass', 'red-team this'.
user-invocable: true
argument-hint: "[--fix] [--auto|--headless] [focus or scope | commit <sha>]"
---

# Quick Review

Lightweight, ad-hoc review of recent work in the current conversation. Internally delegates the critique to a fresh-context sub-agent to catch errors, inconsistencies, and missed edge cases that in-context work tends to overlook.

`andthen:quick-review` is a **skill**, not an agent type. Invoke it via `/andthen:quick-review` or the Skill tool — do not pass it as `subagent_type`.


## VARIABLES

FOCUS: $ARGUMENTS (strip any flag tokens like `--fix`, `--auto`, or `--headless` before interpreting the remainder as focus)


### Optional Flags
- `--fix` → after evaluating findings, apply the **accepted** ones directly. Dismissed findings stay dismissed — the Accept/Dismiss step in Phase 4 remains the guardrail. If zero findings are accepted, report that plainly and stop — nothing to fix. Without this flag, the skill is strictly read-only — see Phase 4.
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- This is a **lightweight mid-conversation review** – a fast, focused checkpoint scoped to recent changes rather than a full formal pass.
- **Default mode is read-only.** Without `--fix`, this skill must not modify any files — it reviews and reports, nothing else. Both the review sub-agent and the outer skill are read-only unless `--fix` is set. The outer skill may edit files only in Phase 4, and only when `--fix` is set on the **current** invocation. If the user wants fixes applied after seeing the report, they must re-invoke with `--fix` — an in-conversation reply alone never unlocks editing.
- The sub-agent reviews in a **fresh context** to avoid confirmation bias.
- Anti-leniency: if the sub-agent identifies a problem, it is a problem. Do not rationalize issues away.
- Output findings inline — no separate report file.
- **Automation mode** (`--auto` / `--headless`) — never ask the user what to do next. If `--fix` is present, apply accepted findings directly; otherwise remain read-only and return accepted findings for the orchestrator to decide on. Stop with `BLOCKED:` (listing what could not be resolved, e.g. no change set, unreadable target) only when the review scope cannot be resolved.


## GOTCHAS
- Sending the sub-agent too little context (it needs to understand what was done and why)
- Sending the sub-agent too much context (entire files when only a section changed)
- Rationalizing away findings because "I just wrote that and it seemed fine"
- Using this as a substitute for a proper review on significant changes
- **Editing files when `--fix` was not passed** — default mode is report-only. Named failure modes this guardrail blocks: treating a vague in-conversation reply ("looks good", "ok", "sure") as confirmation; "starting with the easy ones" inline; pre-emptively patching because the fixes seem trivial or "obviously what the user wants". None of these unlock editing — only `--fix` on the current invocation does.


## WORKFLOW

### 1. Determine Scope

Identify what to review, in priority order:

1. **Commit SHA in FOCUS** (highest priority): if `FOCUS` matches the form `[story <id> ]commit <sha>` — i.e. contains the literal token `commit` followed by a 7+ character hex string — set the change set to the output of `git show <sha>` and skip steps 2–3. Verify the SHA resolves first (`git cat-file -e <sha>`); if it doesn't, stop with `BLOCKED: commit <sha> not found in current repo`. This form is used by orchestrated callers (e.g. the `andthen:exec-plan` skill's team-mode reviewer) where the change is already committed and `git diff` would be empty.
2. **Explicit focus** (FOCUS without a SHA): if `FOCUS` is provided as free-text scope hint, use it to narrow scope from the priorities below
3. **Pending changes**: Run `git diff --stat` and `git diff` for uncommitted changes
4. **Recent conversation work**: If no pending changes, identify artifacts created or modified in this conversation (specs, configs, docs, etc.)

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

Spawn a **single `general-purpose` sub-agent** to apply the canonical Red-Team rubric. Construct its prompt by:

1. Reading `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md` and `${CLAUDE_PLUGIN_ROOT}/references/red-team-calibration.md` and pasting their contents verbatim as the lead of the sub-agent prompt.
2. Appending the call-specific sections below, filled in from the scope and classification steps above:

```
## Context
{what was done and why — brief description of the task/goal}

## Review Lens
{applicable lens from classification step}

## Changes to Review
{the change set — diffs, file contents, or artifact content}

## Output

Report findings as a concise list using the **Finding Shape** from the rubric above. No preamble, no summary section, no severity table. If no weakness survives the attack, say so explicitly using the wording in the rubric's Review Instructions.
```

Provide enough inline context (diffs, file excerpts, project framing) that the sub-agent does not need to explore the codebase extensively.

**Gate**: Sub-agent review complete

### 4. Evaluate and Report

Review the sub-agent's findings. For each:
- **Accept**: the finding is valid and actionable
- **Dismiss**: the finding is based on a misunderstanding of the context (explain briefly why)

Present accepted findings to the user as a concise inline list.

- **Without `--fix` (default, read-only)**: report the accepted findings and **STOP**. Do not edit any files. If actionable issues exist, end with a single short line such as *"Re-run with `--fix` to apply these fixes."* Then wait — fixes only run on a re-invocation that includes `--fix`, never on the strength of a follow-up reply alone. In `AUTO_MODE`, remain read-only and return the accepted findings for the orchestrator to decide whether to invoke a fixing step. If no significant issues were found, state that clearly and move on.
- **With `--fix`**: if zero findings were accepted, report that plainly and stop — nothing to fix. Otherwise, apply the accepted findings directly with minimal, surgical edits — one coherent patch set, no scope creep, no "nearby cleanup". Then re-run the minimum verification that proves the fixes hold (type-check, relevant tests, or targeted re-read). Report what changed in one tight line per fix.

Do not produce a report file. Do not add a summary preamble. Keep it tight.
