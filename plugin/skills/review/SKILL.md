---
description: "The default review skill – start here for all reviews. Runs code, doc, gap, or mixed review, plus multi-perspective council mode via `--council`. Trigger on 'review this', 'review this PR/spec/PRD', 'audit this', 'does this match the spec', 'council review', 'adversarial review', 'multi-reviewer'."
user-invocable: true
argument-hint: "[target/files/PR/spec path] [--mode code|doc|gap|mixed] [--council] [--team] [--inline-findings] [--to-pr <number>] [--fix]"
---

# Review

Unified review skill. Determine what is actually being reviewed, run the right lens inline, and produce one consolidated result.

Code, document, gap, and mixed reviews all run inside this skill using lens-specific references. Multi-perspective **council mode** (5-7 specialized reviewers with adversarial debate) runs as an augmented code review when `--council` is passed or when scope/complexity warrants it.


## VARIABLES
ARGUMENTS: $ARGUMENTS

### Optional Mode Flags
- `--mode code|doc|gap|mixed` → force the review lens. Absent → auto-detect per the routing heuristics in Step 2
- `--council` → run multi-perspective adversarial review (5-7 specialized reviewers with two-phase challenge). Implies `--mode code` unless another mode is explicitly combined. Auto-escalate to council mode when the scope spans multiple concerns (security, performance, architecture, UX), the surface is high-risk (auth, payments, data integrity), or the user asks for "multi-perspective" / "adversarial" / "thorough" review.
- `--team` → force Agent Teams execution mode for council (error if unavailable). Without `--team`, council auto-detects Agent Teams and falls back to parallel sub-agents with sequential debate.
- `--inline-findings` → return findings inline and skip report-file output. **Do not pass** when the caller depends on a report file (e.g. the `andthen:exec-plan` skill's final gap gate, which feeds the `andthen:remediate-findings` skill).
- `--to-pr <number>` → post the consolidated report as a PR comment
- `--fix` → after the report is written, hand it to the `andthen:remediate-findings` skill to address actionable findings. **Incompatible with `--inline-findings`** — reject up-front, before running any review work. When combined with `--to-pr <number>`, post the PR comment first (so the comment reflects the original findings), then run remediation.


## INSTRUCTIONS

- Read the Workflow Rules, Guardrails, and relevant project guidelines before starting.
- The review itself is read-only. Do not modify the reviewed artifacts. Remediation only runs in Step 5 when `--fix` is set, and delegates editing to the `andthen:remediate-findings` skill.
- Reject `--fix` combined with `--inline-findings` before doing any review work — remediation requires the report file.
- Default to the minimum correct lens for the target.
- One lens per call (except **Mixed**, which intentionally runs both doc and code lenses).
- Load the lens-specific reference before running the lens — it carries the rubric, calibration pointers, and report format.
- Use the unified severity scale and per-mode verdict definitions from `references/review-verdict.md`.
- **Calibration-first**: Always load `references/review-calibration.md` (universal) plus the lens-specific calibration (cited by each lens reference) before categorising findings.
- **Default output is a report file.** `--inline-findings` is the explicit opt-out; without it, always write the consolidated report to disk.


## GOTCHAS
- Treating all review requests as code review
- Running `--mode gap` without a real requirements baseline
- Running `--mode mixed` when the real question is requirements fit — use `--mode gap` instead
- Skipping the report file when `--inline-findings` was not passed — the default path always writes a file
- Passing `--inline-findings` when the caller will consume a report file (breaks the `andthen:remediate-findings` skill)
- Forgetting that the `andthen:remediate-findings` skill reads the canonical PASS/FAIL verdict block from gap reports — don't re-label, re-phrase, or re-order its columns
- **Council:** selecting too many reviewers (>7) dilutes debate quality — 5 is the sweet spot
- **Council:** skipping Devil's Advocate under context pressure — it's the most valuable phase
- **Council:** reviewers agreeing too easily — if no findings survive challenge, the review was too shallow
- **Council:** forcing `--team` when Agent Teams are unavailable — fall back to sub-agents unless `--team` was explicit


## WORKFLOW

### 1. Resolve Target and Context

Determine what the user wants reviewed, in priority order:
1. Explicit path, PR, issue, URL, or focus from `ARGUMENTS`
2. Explicit `--mode` flag
3. Current pending changes (`git diff --stat`, `git diff --name-only`) when no target is provided
4. Neighboring artifacts that clarify intent: plan/FIS/PRD/spec docs, changed implementation files, related issue/PR context

Apply an explicit `--mode` flag during discovery, not only during later classification:
- `--mode doc`: when no explicit target is provided, restrict discovery to changed document artifacts (spec/FIS/PRD/plan/ADR/design/prompt/docs) and ignore changed implementation files as primary review targets; if no document targets are found, stop and report that doc mode has no matching scope
- `--mode code`: when no explicit target is provided, restrict discovery to changed implementation/config/test files and ignore changed docs as primary review targets; if no implementation targets are found, stop and report that code mode has no matching scope
- `--mode gap`: when no explicit target is provided, resolve both a requirements baseline and an implementation target from the current changes plus neighboring artifacts; if either side cannot be resolved, stop and report that the missing side is required for gap review
- `--mode mixed`: resolve both a document target (for the doc sub-pass) and an implementation target (for the code sub-pass); if either side cannot be resolved, stop and report the missing side

When no explicit target is provided and no mode flag narrows the scope, build the target map from the dirty worktree by separating:
- changed document artifacts
- changed implementation artifacts
- nearby requirements artifacts that may serve as baselines

Use nearby requirements artifacts to clarify context, not to override explicit review intent.

Build a concise target map:
- **Review target**
- **Relevant artifacts**
- **Implementation scope** if any
- **Requirements baseline** if any
- **User intent**: code quality, doc readiness, requirements fit, or broad audit

**Gate**: Review target and available context are explicit


### 2. Classify the Review Surface

Choose one mode:
- **code**: implementation, config, tests, or current code changes
- **doc**: spec, FIS, PRD, plan, ADR, design doc, prompt, or other written artifact
- **gap**: requirements baseline plus implementation target, where the real question is "does this implementation satisfy the requirements?"
- **mixed**: both document artifacts and implementation artifacts are independently in scope and each needs its own review lens; this dispatches to **doc + code**, not to **gap**

Routing heuristics when `--mode` is absent:
- If the user explicitly asks whether implementation matches a spec, plan, PRD, issue, or requirements baseline, use **gap**
- If the user says "review implementation of [doc]" or similar phrasing where a requirements document is the object of "implementation of", treat [doc] as the requirements baseline and route to **gap** — the intent is requirements-fit validation, not a document review
- If the user explicitly asks for PR review, code review, change review, or an implementation audit, prefer **code** unless they also clearly ask for requirements-fit validation
- If only docs changed, default to **doc**
- If the target is a spec/FIS/PRD/plan path and no implementation target is explicit, default to **doc**
- If only implementation changed, default to **code**
- If there is a clear requirements baseline plus implementation scope and the user's core question is requirements fit, default to **gap**
- If both docs and code changed:
  - Use **gap** when the docs are acting as the requirements baseline for the implementation and the core question is whether the implementation matches them
  - Use **mixed** when the docs themselves need readiness review and the implementation also needs independent code review
- The mere presence of neighboring PRD/FIS/plan/spec artifacts is not enough to force **gap**. Nearby requirements docs provide context; they become the primary lens only when the user's question is actually requirements-vs-implementation fit

**Gate**: Review mode is selected and justified


### 3. Run the Selected Lens

Load the lens reference for the selected mode and run the lens inline. The reference carries the rubric, dimensions, calibration pointers, and report format:

| Mode | Lens reference |
|------|----------------|
| code | `references/lens-code.md` |
| doc | `references/lens-doc.md` |
| gap | `references/lens-gap.md` |
| mixed | **doc sub-pass**: `lens-doc.md`; **code sub-pass**: `lens-code.md` (run both; see below) |

Unified severity and verdict: `references/review-verdict.md` — CRITICAL / HIGH / MEDIUM / LOW; per-mode readiness/verdict rules defined there.

**Mixed mode**: run the doc sub-pass first, then the code sub-pass. Keep findings in distinct subsections in the final report. Overall readiness = worst of the two sub-modes (per `review-verdict.md`).

**Code mode** orchestration: when two or more lenses from `lens-code.md` apply (code quality, security, architecture, domain language, UI/UX) and sub-agents are supported, delegate one parallel reviewer per applicable lens. Otherwise run the lenses sequentially inline.

**Council mode** (`--council`): run the Council Mode workflow in Step 3c instead of standard code-mode orchestration.

**Gate**: Primary lens complete


### 3c. Council Mode Execution _(only when `--council`)_

Multi-perspective code review where specialized reviewers challenge each other's findings through adversarial debate, producing validated, high-confidence issues. Council mode augments **code mode** (or the code sub-pass of mixed mode) — it does not apply to `doc` or `gap` alone.

#### Determine Execution Mode

Check whether Agent Teams are available by verifying that team creation tools exist (e.g. `TeamCreate`):
- **Agent Teams available** (or `--team` flag) → Agent Teams path
- **Agent Teams unavailable, no `--team`** → sub-agent path
- **Agent Teams unavailable, `--team` present** → inform the user that it requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and exit

#### Select Council Members

Choose 5-7 reviewers from `references/reviewer-roster.md` based on the review scope (see the Selection Examples in that reference). Always include **Devil's Advocate** and **Synthesis Challenger**.

**Gate:** 5-7 reviewers selected (always include Devil's Advocate + Synthesis Challenger)

#### Agent Teams Path

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

Your role: {reviewer name and focus areas from `references/reviewer-roster.md`}

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

**Phase 1 – Initial Review & Debate:** wait for specialist completion; ensure Devil's Advocate challenges each finding (max 2-3 rounds); track findings as validated, withdrawn, or disputed. **Gate:** Phase 1 debates resolved.

**Phase 2 – Synthesis Review:** Synthesis Challenger reviews holistically after Phase 1; may reclassify, merge, or split findings. **Gate:** Synthesis complete.

**Clean up:** send shutdown requests, await confirmations, delete the team.

#### Sub-Agent Path

Run specialist reviews using **parallel sub-agents** _(if supported; otherwise sequentially)_.

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

**Phase 2 – Devil's Advocate Challenge:** spawn a sub-agent as the Devil's Advocate. Use `references/adversarial-challenge.md` (`Devil's Advocate`) with:
- **Role**: `Devil's Advocate on a Review Council for: {SCOPE}`
- **Context block**: `You have received {N} findings from specialist reviewers.`
- **Questions**: Is this actually a problem? Is severity justified? Could this be a false positive? Is there an existing mitigation?
- **Verdicts**: `VALIDATED`, `DOWNGRADED`, `WITHDRAWN`, `DISPUTED`
- **Findings payload**: `{all collected findings}`

Apply the verdicts to the findings list. **Gate:** findings challenged, verdicts applied.

**Phase 3 – Synthesis Review:** spawn a sub-agent as the Synthesis Challenger. Use `references/adversarial-challenge.md` (`Synthesis Challenger`) with:
- **Role**: `Synthesis Challenger on a Review Council for: {SCOPE}`
- **Context block**: `You are the final quality gate. Review all findings that survived the Devil's Advocate phase holistically.`
- **Questions**: Are severity ratings consistent? Are related findings actually one larger issue? Did we miss systemic patterns? Are any validated findings false positives in context?
- **Optional extra rules**: `You may merge related findings, split a finding covering multiple distinct problems, or add a new finding only if you spot a systemic pattern the specialists missed.`
- **Findings payload**: `{validated and downgraded findings from Phase 2}`

**Gate:** Synthesis complete.


### 4. Synthesize One Final Result

**Default path — write a consolidated markdown report file.** Use this deterministic suffix mapping (downstream skills parse the filename — do not vary):

| Mode | Report suffix |
|------|---------------|
| code | `code-review` |
| doc | `doc-review` |
| gap | `gap-review` |
| mixed | `review` |
| code + `--council` | `council-review` |

- **Filename**: `<review-target>-<suffix>-<agent>-<YYYY-MM-DD>.md` — on collision append `-2`, `-3`. `<agent>` is your agent short name (`claude`, `codex`, etc.; fall back to `agent`).
- **Directory priority**:
  1. **Spec directory** — when the review centers on a spec/FIS/plan, use its feature/spec directory
  2. **Target directory** — next to the primary review target
  3. **Fallback** — `{AGENT_TEMP}/reviews/` (default `.agent_temp/reviews/`)
- On completion, print the report's relative path from the project root.

Only when `--inline-findings` is present: skip the file and return the same content inline, stating the mode(s) run.

Report/inline content must include:
- **Scope**
- **Review mode used**: code / doc / gap / mixed
- **Findings by severity** using the unified scale (CRITICAL / HIGH / MEDIUM / LOW)
- **Readiness / verdict** per `references/review-verdict.md`:
  - `code`: severity counts + readiness label (`Ready` / `Needs Fixes` / `Blocked`)
  - `doc`: readiness label (`Ready` / `Needs Minor Updates` / `Needs Significant Rework` / `Not Ready`)
  - `gap`: PASS/FAIL verdict table (byte-level compatible — reproduce the canonical block verbatim)
  - `mixed`: per-sub-mode verdicts + overall readiness = worst of the two
- **Recommended next action**

For `--to-pr <number>`: post the report file's contents as a plain PR comment via `gh pr comment <number> --body-file <report-path>`. Print the direct comment URL returned (resolve via follow-up lookup if the command does not print one). The mode and any referenced `plan_path` / `fis_path` must be visible in the report body itself so downstream readers (including `andthen:remediate-findings` run against the local report path) can interpret the findings.

For **Mixed** reviews, keep findings from the doc and code sub-passes in distinct subsections. Merge overlapping findings and use the strongest framing as canonical.

For **Council** reviews, use this report structure — only findings that survived both debate phases appear in the severity sections:

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

**Gate**: One consolidated result delivered


### 5. Remediate _(only when `--fix`)_

Invoke the `andthen:remediate-findings` skill with the report path as its argument. Skip only when there is nothing actionable to remediate — a `gap` PASS verdict, or a clean report with no findings. In every other case (code / doc / mixed / council), hand the report over and let the remediation skill scope the fixes.

Do not re-interpret findings or pre-filter by severity here. The `andthen:remediate-findings` skill owns the fix scoping — this step is pure delegation.

**Gate**: Remediation invoked or explicitly skipped with reason


## FOLLOW-UP ACTIONS

After the report, ask whether the user wants to:
1. Update the reviewed artifact based on findings
2. Focus on a narrower area
3. Proceed to implementation
4. Escalate critical issues for clarification
5. For FAIL / `Needs Significant Rework` / `Not Ready` / CRITICAL outcomes — run the `andthen:remediate-findings` skill with the report path or URL. Skip this prompt when `--fix` already ran remediation in Step 5.
