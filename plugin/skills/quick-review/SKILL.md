---
description: Quick in-conversation skill for critic review of recent changes in fresh context. Use mid-conversation to sanity-check work before moving on. Trigger on 'quick review this', 'sanity-check this', 'give this a quick pass', 'critic this', 'red-team this'.
user-invocable: true
argument-hint: "[--inline] [--fix] [--auto|--headless] [focus or scope | commit <sha>]"
---

# Quick Review

Lightweight, ad-hoc review of recent work in the current conversation. By default, delegates the critique to a fresh-context sub-agent so confirmation bias from the calling conversation can't soften findings; with `--inline`, applies the rubric directly when the calling conversation is itself fresh w.r.t. the change set. Either path catches errors, inconsistencies, and missed edge cases that in-context work tends to overlook.

`andthen:quick-review` is a **skill**, not an agent type. Invoke it via `/andthen:quick-review` or the Skill tool — do not pass it as `subagent_type`.


## VARIABLES

FOCUS: $ARGUMENTS (strip any flag tokens like `--inline`, `--fix`, `--auto`, or `--headless` before interpreting the remainder as focus)


### Optional Flags
- `--inline` → apply the Critic rubric directly in the current conversation instead of dispatching a fresh-context sub-agent. Use when the calling conversation has **not** produced or substantively reasoned about the change set under review (e.g. the skill is invoked as the first action in a new session, or against a `commit <sha>` from work the conversation never touched). The sub-agent's bias-reduction property is already satisfied by the caller's freshness w.r.t. the change set, so the dispatch is redundant scaffolding. Do not use when the calling conversation produced, edited, or actively reasoned about the change set — the `--inline` branch in Phase 3 will reject the flag and fall back to default dispatch.
- `--fix` → after evaluating findings, apply the **accepted** ones directly. Dismissed findings stay dismissed — the Accept/Dismiss step in Phase 4 remains the guardrail. If zero findings are accepted, report that plainly and stop — nothing to fix. Without this flag, the skill is strictly read-only — see Phase 4.
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- This is a **lightweight mid-conversation review** – a fast, focused checkpoint scoped to recent changes rather than a full formal pass.
- **Default mode is read-only.** Without `--fix`, this skill must not modify any files — it reviews and reports, nothing else. The reviewer (sub-agent under default dispatch, the outer skill under `--inline`) and any wrapping logic are read-only unless `--fix` is set. The outer skill may edit files only in Phase 4, and only when `--fix` is set on the **current** invocation. If the user wants fixes applied after seeing the report, they must re-invoke with `--fix` — an in-conversation reply alone never unlocks editing.
- Bias reduction comes from **fresh context** — provided by the sub-agent under default dispatch, by the calling conversation under `--inline`. If the calling conversation is not in fact fresh w.r.t. the change set, the `--inline` branch in Phase 3 falls back to default dispatch.
- Anti-leniency: if a finding is identified, it is a problem. Do not rationalize issues away.
- Output findings inline — no separate report file.
- **Automation mode** (`--auto` / `--headless`) — never ask the user what to do next. If `--fix` is present, apply accepted findings directly; otherwise remain read-only and return accepted findings for the orchestrator to decide on. Stop with `BLOCKED:` (listing what could not be resolved, e.g. no change set, unreadable target) only when the review scope cannot be resolved.


## GOTCHAS
- Sending the sub-agent too little context (it needs to understand what was done and why)
- Sending the sub-agent too much context (entire files when only a section changed)
- Rationalizing away findings because "I just wrote that and it seemed fine"
- Using this as a substitute for a proper review on significant changes
- **Using `--inline` in a non-fresh conversation** — the flag's whole premise is that the calling conversation has no in-context bias to escape. If the work being reviewed was produced by this same conversation's earlier turns, drop the flag and use the default sub-agent dispatch.
- **Editing files when `--fix` was not passed** — default mode is report-only. Named failure modes this guardrail blocks: treating a vague in-conversation reply ("looks good", "ok", "sure") as confirmation; "starting with the easy ones" inline; pre-emptively patching because the fixes seem trivial or "obviously what the user wants". None of these unlock editing — only `--fix` on the current invocation does.
- **Discarding uncommitted work as a "fix"** — `git restore`, `git checkout --`, file deletions, or any other discard of working-tree changes are NEVER an applicable fix, even with `--fix` set. Files modified outside the review focus may be parallel work, exploratory edits, staged-for-later commits, or another task in progress — they are not yours to revert. Scope-creep findings ("this file shouldn't have been changed at all") are **flag-only**: surface them and stop, the user decides what to do.


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

### 3. Critic Review

Apply the canonical Critic rubric to the change set. Default execution dispatches to a fresh-context sub-agent so confirmation bias from the calling conversation can't soften findings; `--inline` applies the rubric directly when the calling conversation is already fresh.

**Default — sub-agent dispatch.** The outer skill loads the same three references itself before dispatch so it can apply the same calibration in Phase 4. Spawn a **single sub-agent** with a prompt of this shape, filled in from the scope and classification steps above:

```
Read all three references before applying the rubric:
- ${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md — Critic posture, what to attack, Finding Shape
- ${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md — find-pass calibration and contrastive examples
- ${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md — Anti-Leniency Protocol

Apply the Critic posture to the change set below.

## Context
{what was done and why — brief description of the task/goal}

## Review Lens
{applicable lens from classification step}

## Changes to Review
{the change set — diffs, file contents, or artifact content}

## Output

Report findings as a concise list using the **Finding Shape** from `lens-adversarial.md`. No preamble, no summary section, no severity table. If no weakness survives the attack, say so explicitly using the wording in that file's Review Instructions.
```

Provide enough inline context (diffs, file excerpts, project framing) that the sub-agent does not need to explore the codebase extensively.

**`--inline` — in-context application.** Read the same three reference files directly, adopt the Critic posture, and apply it to the change set in the current conversation. Use the same Finding Shape and anti-leniency rules.

Before applying the rubric, verify the calling conversation has not produced or substantively reasoned about the change set. If it has, emit `FALLBACK: --inline rejected, dispatching sub-agent (calling conversation not fresh w.r.t. change set)` and continue with default dispatch — surface the fallback in the final report so the caller knows the flag was overridden. In `AUTO_MODE`, the fallback is reported the same way; never silently swap mechanisms.

**Gate**: Critic review complete

### 4. Evaluate and Report

Review the findings produced in Phase 3 (sub-agent or `--inline`). For each:
- **Accept**: the finding is valid and actionable
- **Dismiss**: only on a concrete falsifier — observed mitigation in the artifact, explicit upstream citation, or calibration match. Never dismiss on recall ("I already considered that") or recency ("I just wrote that and it seemed fine").

**Under `--inline`** (and especially `--inline --fix`): the same agent generated and is now evaluating the findings — the structural separation default dispatch provides is collapsed. The falsifier rule above applies with extra force.

Present accepted findings to the user as a concise inline list.

- **Without `--fix` (default, read-only)**: report the accepted findings and **STOP**. Do not edit any files. If actionable issues exist, end with a single short line such as *"Re-run with `--fix` to apply these fixes."* Then wait — fixes only run on a re-invocation that includes `--fix`, never on the strength of a follow-up reply alone. In `AUTO_MODE`, remain read-only and return the accepted findings for the orchestrator to decide whether to invoke a fixing step. If no significant issues were found, state that clearly and move on.
- **With `--fix`**: if zero findings were accepted, report that plainly and stop — nothing to fix. Otherwise, apply the accepted findings directly with minimal, surgical edits — one coherent patch set, no scope creep, no "nearby cleanup". Edits are **additive/corrective only**: never `git restore`, `git checkout --`, delete files, or otherwise discard uncommitted working-tree changes — those changes may be unrelated work in progress and destroying them is unrecoverable. A finding of the shape "this file shouldn't have been changed at all" is **flag-only** under `--fix` — surface it and stop, do not auto-revert. Then re-run the minimum verification that proves the fixes hold (type-check, relevant tests, or targeted re-read). Report what changed in one tight line per fix.

Do not produce a report file. Do not add a summary preamble. Keep it tight.
