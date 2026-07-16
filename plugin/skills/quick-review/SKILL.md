---
description: Quick critic review of recent changes in fresh context – a mid-conversation sanity check before moving on. Trigger on 'quick review this', 'sanity-check this', 'critic this'.
user-invocable: true
argument-hint: "[--inline] [--fix] [--auto] [focus or scope | commit <sha>]"
---

# Quick Review

Lightweight, ad-hoc review of recent work in the current conversation. By default, delegates the critique to a fresh-context sub-agent so confirmation bias from the calling conversation can't soften findings; `--inline` applies the rubric directly when the caller is already fresh (see Optional Flags).

`andthen:quick-review` is a **skill**, not an agent type. Invoke it as a skill – do not pass it as `subagent_type`.


## VARIABLES

FOCUS: $ARGUMENTS (strip any flag tokens like `--inline`, `--fix`, `--auto`, or `--headless` before interpreting the remainder as focus)


### Optional Flags
- `--inline` → apply the Critic rubric directly in the current conversation instead of dispatching a fresh-context sub-agent. Use only when the calling conversation has **not** produced or reasoned about the change set, so the caller's own freshness satisfies the bias-reduction property. Misuse is governed by the Phase 3 non-fresh-conversation reject + fallback.
- `--fix` → after evaluating findings, apply accepted **Fix**-bucket findings only; **Note** findings are never auto-applied. Read-only is the default. Phase 4 owns the routing and zero-Fix-findings rules.
- `--auto` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Read project rules and guidelines (`CLAUDE.md` / `AGENTS.md` and referenced files) before starting.
- Default read-only; only `--fix` on the current invocation unlocks edits (Phase 4).
- Guardrails pass runs once per review in Phase 3.
- Output findings inline – no separate report file.
- **Automation mode** (`--auto` / `AUTO_MODE`): never ask the user what to do next; with `--fix` apply Fix findings only, else remain read-only and return both groups. Stop with `BLOCKED:` only when the review scope cannot be resolved (e.g. no change set, unreadable target).


## GOTCHAS
- Skipping the fresh-context sub-agent because the spawn tool is missing from the visible tool list – that is not unavailability; where the host supports deferred tool loading, run its tool discovery before treating dispatch as unavailable.
- Sending the sub-agent too little context (it needs to understand what was done and why)
- Sending the sub-agent too much context (entire files when only a section changed)
- Rationalizing away findings because "I just wrote that and it seemed fine"
- Using this as a substitute for a proper review on significant changes
- **Discarding uncommitted work as a fix** → never; may be unrelated WIP (Phase 4).
- **Routing every accepted finding to Fix** → Phase 4 Routing gate.
- **Reviewing without Intent Context** → strips Phase 4 of its falsifier source (Phase 3 collection).


## WORKFLOW

### 1. Determine Scope

Identify what to review, in priority order:

1. **Commit SHA in FOCUS** (highest priority): if `FOCUS` matches the form `[story <id> ]commit <sha>` – i.e. contains the literal token `commit` followed by a 7+ character hex string – set the change set to the output of `git show <sha>` and skip steps 2–3. Verify the SHA resolves first (`git cat-file -e <sha>`); if it doesn't, stop with `BLOCKED: commit <sha> not found in current repo`. This form is used by orchestrated callers (e.g. the `andthen:exec-plan` skill's team-mode reviewer) where the change is already committed and `git diff` would be empty.
2. **Explicit focus** (FOCUS without a SHA): if `FOCUS` is provided as free-text scope hint, use it to narrow scope from the priorities below
3. **Pending changes**: Run `git diff --stat` and `git diff` for uncommitted changes
4. **Recent conversation work**: If no pending changes, identify artifacts created or modified in this conversation (specs, configs, docs, etc.)

Collect the **change set** – only what actually changed, with enough surrounding context to comprehend it.

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

Apply the canonical Critic rubric to the change set. Default dispatches a single Critic pass to a fresh-context sub-agent (prefer the installed `review-critic` agent, else a generic fresh sub-agent – the installed-agent path still gets the read-first prompt), using the prompt in [`dispatch-prompt.md`](references/dispatch-prompt.md) – fill its Context / Review Lens / Project Rules Context / Intent Context / Changes-to-Review sections and provide enough inline context that the sub-agent need not explore the codebase. The outer skill loads the same three references and collects the **Project Rules Context** and **Intent Context** bundles per [`intent-and-rules-context.md`](${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md) so Phase 4 can apply the same calibration. **`--inline`** applies the same rubric, Guardrails pass, Finding Shape, and context collection inline, per the same dispatch-prompt contract.

Before applying the rubric, verify the calling conversation has not produced or substantively reasoned about the change set. If it has, emit `FALLBACK: --inline rejected, dispatching sub-agent (calling conversation not fresh w.r.t. change set)` and continue with default dispatch – surface the fallback in the final report so the caller knows the flag was overridden. In `AUTO_MODE`, the fallback is reported the same way; never silently swap mechanisms.

**Gate**: Critic review complete

### 4. Evaluate and Report

Each finding passes through two gates: a **Validity gate** (Accept / Dismiss) and a **Routing gate** that splits accepted findings into **Fix** and **Note** buckets. The split exists because the Critic find-pass intentionally favors recall (per `critic-calibration.md`); without a routing step every accepted finding flows into `--fix`, turning marginal observations into edits and drifting the change set away from its stated intent.

**Validity gate.** Decide Accept or Dismiss for each finding.
- **Accept**: the named defect, gap, or contradiction is real.
- **Dismiss**: only on a concrete falsifier – observed mitigation in the artifact, explicit upstream citation (e.g. the Intent Context names the gap as a Non-Goal or defers it to a later story), or calibration match. Never dismiss on recall or recency.

**Routing gate (accepted findings only).** Decide Fix or Note. Routing keys on **fix character, not defect severity** – severity feeds escalation priority, not auto-apply eligibility, because a bounded, decision-free fix is equally safe to apply at any severity.
- **Fix**: confidence ≥ 75, scope relation is `primary` (the finding traces to a line, section, or stated outcome the change set itself adds, modifies, or claims to deliver), the fix does not introduce new scope beyond the change set's stated Intent / Expected Outcomes, AND the correction is **mechanical and bounded** – the correct replacement is *uniquely determined* by the artifact, rules, requirements, or a cited source, needing no product / design / architecture / requirements decision; if it means choosing between plausible fixes or depends on behavior the artifact does not pin down, it is not mechanical → Note (so a gap needing a design decision stays Note whatever its severity). Security fixes are Fix-eligible only when the secure correction is mechanical and unambiguous. Eligible for auto-apply under `--fix`.
- **Note**: everything else – lower confidence, scope relation `secondary` / `pre_existing`, "consider adding X" / "could be cleaner" shapes, fixes needing a product / design / requirements decision, or any fix that would expand scope past the stated Intent. Surfaced inline but **never auto-applied**, even under `--fix`. This matches the **Surgical scope; surface – don't fix** rule in `CRITICAL-RULES-AND-GUARDRAILS.md` and the `NOTICED BUT NOT TOUCHING` channel.

**Class axis (orthogonal to routing).** This skill already runs an intent-aware Critic pass; the delta is emitting a finding **`Class:`** so per-story drift is writable to the reconciliation ledger by the orchestrating skill (`andthen:exec-plan`). On each accepted finding, set `Class:` to exactly one of `code-defect | spec-stale | design-changed | ambiguous-intent` per [`reconciliation-ledger.md`](${CLAUDE_PLUGIN_ROOT}/references/reconciliation-ledger.md): `code-defect` (the change is wrong relative to Intent/Expected Outcomes and the fix is clear), `spec-stale` (the spec no longer describes what was built), `design-changed` (a coherent pivot from the spec needing reconciliation), `ambiguous-intent` (not enough intent to decide). The class is orthogonal to Fix/Note routing – a `spec-stale` finding is still `spec-stale` whether routed Fix or Note. Keep this lightweight – emit the axis, don't re-derive the intent-awareness.

**Intent anchor.** When Intent Context was collected in Phase 3, apply the canonical anchor moves from [`intent-and-rules-context.md`](${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md), mapped to this skill's vocabulary: Non-Goal → Dismiss; deferred → Note; contradicts Expected Outcome → Fix-eligible regardless of severity heuristics. When no Intent Context was collected, the Routing gate operates on severity, confidence, and scope relation alone – do not invent intent to justify routing. **On tie, default to Note**.

**Under `--inline`** (and especially `--inline --fix`): the same agent generated and is now evaluating the findings – the structural separation default dispatch provides is collapsed. Both gates apply with extra force (same tie defaults).

Start the inline result with `Intent Context: <source path | none discoverable>`. Then present accepted findings inline, grouped by routing (**Fix** first, then **Note**). For each accepted finding, include exactly one class value as `Class: <code-defect | spec-stale | design-changed | ambiguous-intent>` (e.g. `Class: spec-stale`; never emit the enum string as the value) and a literal `Routing: Fix` or `Routing: Note` field plus the routing rationale in one short clause (severity / confidence / scope relation, plus the Intent-anchor citation when one applied). The output remains inline but must stay parseable as a full review report.

- **Without `--fix` (default, read-only)**: report both groups and **STOP**. If any **Fix** findings exist, end with one hint line to re-run with `--fix`; if only **Note** findings exist, say so. Fixes run only on a re-invocation with `--fix`, never on a follow-up reply.
- **With `--fix`**: if zero **Fix** findings exist, report that plainly and stop. Otherwise apply only the **Fix** findings as one surgical patch set – no scope creep, no nearby cleanup, and **never** touch Note findings. Edits are **additive/corrective only**: never `git restore`, `git checkout --`, or delete to discard uncommitted working-tree changes – it may be unrelated WIP and is unrecoverable. A "this file shouldn't have been changed" finding is **flag-only / no auto-revert**. Then re-run the minimum verification that proves the fixes hold and report each in one tight line. **One pass only**: surface new issues, do not loop.

No summary preamble; keep it tight.
