---
description: Quick in-conversation skill for critic review of recent changes in fresh context. Use mid-conversation to sanity-check work before moving on. Trigger on 'quick review this', 'sanity-check this', 'give this a quick pass', 'critic this', 'red-team this'.
user-invocable: true
argument-hint: "[--inline] [--fix] [--auto] [focus or scope | commit <sha>]"
---

# Quick Review

Lightweight, ad-hoc review of recent work in the current conversation. By default, delegates the critique to a fresh-context sub-agent so confirmation bias from the calling conversation can't soften findings; `--inline` applies the rubric directly when the caller is already fresh (see Optional Flags). Either path catches errors, inconsistencies, and missed edge cases that in-context work tends to overlook.

`andthen:quick-review` is a **skill**, not an agent type. Invoke it via `/andthen:quick-review` or the Skill tool – do not pass it as `subagent_type`.


## VARIABLES

FOCUS: $ARGUMENTS (strip any flag tokens like `--inline`, `--fix`, `--auto`, or `--headless` before interpreting the remainder as focus)


### Optional Flags
- `--inline` → apply the Critic rubric directly in the current conversation instead of dispatching a fresh-context sub-agent. Use when the calling conversation has **not** produced or substantively reasoned about the change set under review (e.g. the skill is invoked as the first action in a new session, or against a `commit <sha>` from work the conversation never touched) – the caller's own freshness already satisfies the sub-agent's bias-reduction property. The **non-fresh-conversation** trap (Phase 3 reject + fallback) governs misuse.
- `--fix` → after evaluating findings, apply accepted **Fix**-bucket findings directly. Accepted **Note** findings are surfaced but never auto-applied; dismissed findings stay dismissed. If zero Fix findings exist, report that plainly and stop – nothing to auto-apply. Read-only is the default (Phase 4 owns the rule).
- `--auto` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Read project rules and guidelines (`CLAUDE.md` / `AGENTS.md` and referenced files) before starting.
- This is a **lightweight mid-conversation review** – a fast, focused checkpoint scoped to recent changes rather than a full formal pass.
- **Default mode is read-only** – only `--fix` on the **current** invocation unlocks edits (Phase 4 owns the rule).
- **Guardrails pass** runs once per review alongside the Critic rubric, emitting a `Guardrails Coverage: N checked, M findings` line; procedure lives in Phase 3.
- Anti-leniency: if a finding is identified, it is a problem. Do not rationalize issues away.
- Output findings inline – no separate report file.
- **Automation mode** (`--auto`) – never ask the user what to do next. If `--fix` is present, apply **Fix**-bucket findings only (per Phase 4's Routing gate); otherwise remain read-only and return both Fix and Note groups for the orchestrator to decide on. Stop with `BLOCKED:` (listing what could not be resolved, e.g. no change set, unreadable target) only when the review scope cannot be resolved.


## GOTCHAS
- Sending the sub-agent too little context (it needs to understand what was done and why)
- Sending the sub-agent too much context (entire files when only a section changed)
- Rationalizing away findings because "I just wrote that and it seemed fine"
- Using this as a substitute for a proper review on significant changes
- **Non-fresh-conversation `--inline`** → see Phase 3 (`--inline` branch rejects and falls back to default dispatch).
- **Editing files when `--fix` was not passed** – default mode is read-only. Named failure modes this guardrail blocks: treating a vague in-conversation reply ("looks good", "ok", "sure") as confirmation; "starting with the easy ones" inline; pre-emptively patching because the fixes seem trivial or "obviously what the user wants". None of these unlock editing – only `--fix` on the current invocation does.
- **Discarding uncommitted work as a "fix"** → never; see Phase 4 (working-tree changes may be unrelated WIP).
- **Routing every accepted finding to Fix** → see Phase 4 Routing gate (collapsing Fix/Note turns this into over-engineering).
- **Reviewing without Intent Context** – when a FIS, PRD, `clarify` output, or active plan story governs the change set, skipping the Intent Context collection in Phase 3 strips the Phase 4 gates of their primary falsifier source. A "you didn't handle X" finding may already be a documented Non-Goal; without the artifact loaded, the Critic has no way to know and the gate has no way to dismiss.


## WORKFLOW

### 1. Determine Scope

Identify what to review, in priority order:

1. **Commit SHA in FOCUS** (highest priority): if `FOCUS` matches the form `[story <id> ]commit <sha>` – i.e. contains the literal token `commit` followed by a 7+ character hex string – set the change set to the output of `git show <sha>` and skip steps 2–3. Verify the SHA resolves first (`git cat-file -e <sha>`); if it doesn't, stop with `BLOCKED: commit <sha> not found in current repo`. This form is used by orchestrated callers (e.g. the `andthen:exec-plan` skill's team-mode reviewer) where the change is already committed and `git diff` would be empty.
2. **Explicit focus** (FOCUS without a SHA): if `FOCUS` is provided as free-text scope hint, use it to narrow scope from the priorities below
3. **Pending changes**: Run `git diff --stat` and `git diff` for uncommitted changes
4. **Recent conversation work**: If no pending changes, identify artifacts created or modified in this conversation (specs, configs, docs, etc.)

Collect the **change set** – the specific content to review. Keep it focused: only include what actually changed, with enough surrounding context for comprehension.

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

Apply the canonical Critic rubric to the change set. Default dispatches to a fresh-context sub-agent; `--inline` applies the rubric directly when the caller is already fresh.

**Default – sub-agent dispatch.** The outer skill loads the same three references itself before dispatch so it can apply the same calibration in Phase 4. It also collects the **Project Rules Context** and **Intent Context** bundles per [`intent-and-rules-context.md`](${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md) (loader contract, discovery rules, falsifier principle, degradation when no governing artifact exists).

Dispatch a **single Critic pass** with the prompt shape below; prefer the installed `review-critic` custom agent when the host can select it, otherwise use a generic fresh-context sub-agent. The installed-agent path still receives the same read-first prompt – custom agent instructions are not a substitute for calibration.

```
Read all three references before applying the rubric:
- ${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md – Critic posture, what to attack, Finding Shape
- ${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md – find-pass calibration and contrastive examples
- ${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md – Anti-Leniency Protocol

Also read the Project Rules Context and Intent Context (if present) below before running the rubric and the Guardrails pass; treat them as the evidence sets for project rules and for feature/product intent respectively.

Apply the Critic posture to the change set below.

Also run a **Guardrails pass**: enumerate project rules, guardrails, principles and guidelines from your context (as defined in `CLAUDE.md` / `AGENTS.md` and other referenced files); filter to those a diff can verify (skip process-only rules); for each applicable rule, check the change set and report violations as findings with the rule cited by source (file and section). Report `Guardrails Coverage: N checked, M findings` alongside the Critic findings.

Use the Intent Context to sharpen, not soften, the find pass: gaps between Expected Outcomes and the change set are Critic findings; behavior outside the stated Intent or contradicting a Non-Goal is a Critic finding even when the code "works". Do not pre-filter findings against the Intent here – the Phase 4 routing gate handles dismissal and Fix/Note routing.

## Context
{what was done and why – brief description of the task/goal}

## Review Lens
{applicable lens from classification step}

## Project Rules Context
{source-path-labeled rule / guardrail / guideline excerpts collected by the outer skill}

## Intent Context
{source-path-labeled Intent / Expected Outcomes / Non-Goals excerpts; omit the section entirely if no governing artifact was found}

## Changes to Review
{the change set – diffs, file contents, or artifact content}

## Output

Report findings as a concise list using the **Finding Shape** from `lens-adversarial.md` (reviewer, severity, confidence, location, scope relation, finding, threatened assumption or invariant, evidence, impact, suggested fix, verification needed). No preamble, no summary section, no severity table. If no weakness survives the attack, say so explicitly using the wording in that file's Review Instructions. Include the `Guardrails Coverage` line and any guardrail-violation findings (cited by rule source) inline with the rest.
```

Provide enough inline context (diffs, file excerpts, project framing) that the sub-agent does not need to explore the codebase extensively.

**`--inline` – in-context application.** Read the same three reference files directly, adopt the Critic posture, and apply it to the change set in the current conversation. Collect the same Project Rules Context and Intent Context bundles per [`intent-and-rules-context.md`](${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md) so Phase 4 has the evidence it needs. Run the same Guardrails pass alongside (per INSTRUCTIONS). Use the same Finding Shape and anti-leniency rules; report `Guardrails Coverage: N checked, M findings` alongside the Critic findings.

Before applying the rubric, verify the calling conversation has not produced or substantively reasoned about the change set. If it has, emit `FALLBACK: --inline rejected, dispatching sub-agent (calling conversation not fresh w.r.t. change set)` and continue with default dispatch – surface the fallback in the final report so the caller knows the flag was overridden. In `AUTO_MODE`, the fallback is reported the same way; never silently swap mechanisms.

**Gate**: Critic review complete

### 4. Evaluate and Report

Each finding passes through two gates: a **Validity gate** (Accept / Dismiss) and a **Routing gate** that splits accepted findings into **Fix** and **Note** buckets. The split exists because the Critic find-pass intentionally favors recall (per `critic-calibration.md`); without a routing step every accepted finding flows into `--fix`, turning marginal observations into edits and drifting the change set away from its stated intent.

**Validity gate.** Decide Accept or Dismiss for each finding.
- **Accept**: the named defect, gap, or contradiction is real.
- **Dismiss**: only on a concrete falsifier – observed mitigation in the artifact, explicit upstream citation (e.g. the Intent Context names the gap as a Non-Goal or defers it to a later story), or calibration match. Never dismiss on recall ("I already considered that") or recency ("I just wrote that and it seemed fine").

**Routing gate (accepted findings only).** Decide Fix or Note.
- **Fix**: severity HIGH or CRITICAL, confidence ≥ 75, scope relation is `primary` (the finding traces to a line, section, or stated outcome the change set itself adds, modifies, or claims to deliver), AND the fix does not introduce new scope beyond the change set's stated Intent / Expected Outcomes. Eligible for auto-apply under `--fix`.
- **Note**: everything else – LOW/MEDIUM severity, lower confidence, scope relation `secondary` / `pre_existing`, "consider adding X" / "could be cleaner" shapes, or any fix that would expand scope past the stated Intent. Surfaced inline but **never auto-applied**, even under `--fix`. This matches the **Surgical scope; surface – don't fix** rule in `CRITICAL-RULES-AND-GUARDRAILS.md` and the `NOTICED BUT NOT TOUCHING` channel.

**Intent anchor.** When Intent Context was collected in Phase 3, apply the canonical anchor moves from [`intent-and-rules-context.md`](${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md) (Non-Goal → Dismiss; deferred → Note; contradicts Expected Outcome → Fix-eligible regardless of severity heuristics). When no Intent Context was collected, the Routing gate operates on severity, confidence, and scope relation alone – do not invent intent to justify routing. **On tie, default to Note**: without the Intent anchor the scope-expansion guard is silently weaker, so the gate leans conservative.

**Under `--inline`** (and especially `--inline --fix`): the same agent generated and is now evaluating the findings – the structural separation default dispatch provides is collapsed. Both gates apply with extra force; on tie, route toward **Note** rather than **Fix**, and toward **Accept** rather than **Dismiss**.

Start the inline result with `Intent Context: <source path | none discoverable>`. Then present accepted findings inline, grouped by routing (**Fix** first, then **Note**). For each accepted finding, include a literal `Routing: Fix` or `Routing: Note` field plus the routing rationale in one short clause (severity / confidence / scope relation, plus the Intent-anchor citation when one applied). The output remains inline, but downstream capture must be able to parse the same fields as a full review report.

- **Without `--fix` (default, read-only)**: report both groups and **STOP**. Do not edit any files. If any **Fix**-bucket findings exist, end with a single short line such as *"Re-run with `--fix` to apply the Fix findings; Note findings are surfaced for you to decide on."* If only **Note**-bucket findings exist, say so explicitly so the user knows there is nothing for `--fix` to act on. Fixes only run on a re-invocation that includes `--fix`, never on the strength of a follow-up reply alone. In `AUTO_MODE`, remain read-only and return both groups for the orchestrator to decide whether to invoke a fixing step.
- **With `--fix`**: if zero **Fix**-bucket findings exist, report that plainly (Note findings still surfaced) and stop – nothing to auto-apply. Otherwise, apply only the **Fix** findings with minimal, surgical edits – one coherent patch set, no scope creep, no "nearby cleanup", and **never** touch Note findings even when adjacent. Edits are **additive/corrective only**: never `git restore`, `git checkout --`, delete files, or otherwise discard uncommitted working-tree changes – those changes may be unrelated work in progress and destroying them is unrecoverable. A finding of the shape "this file shouldn't have been changed at all" is **flag-only** under `--fix` regardless of routing – surface it and stop, do not auto-revert. Then re-run the minimum verification that proves the fixes hold (type-check, relevant tests, or targeted re-read). Report what changed in one tight line per fix. **One pass only**: if verification surfaces new issues, surface them and stop – do not loop. Re-invocation is the user's call.

Do not produce a report file. Do not add a summary preamble. Keep it tight.
