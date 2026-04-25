---
description: "The default review skill – start here for all reviews. Runs code, doc, gap, or mixed review, plus multi-perspective council mode via `--council`. Trigger on 'review this', 'review this PR/spec/PRD', 'audit this', 'does this match the spec', 'council review', 'adversarial review', 'multi-reviewer'."
user-invocable: true
argument-hint: "[target/files/PR/spec path] [--mode code|doc|gap|mixed] [--council] [--team] [--inline-findings] [--to-pr <number>] [--fix] [--auto|--headless]"
---

# Review

Unified review skill. Determine what is actually being reviewed, run the right lens inline, and produce one consolidated result.

Code, document, gap, and mixed reviews all run inside this skill using lens-specific references. Multi-perspective **council mode** (5-7 specialized reviewers with adversarial debate) runs as an augmented code review when `--council` is passed or when scope/complexity warrants it.


## VARIABLES
ARGUMENTS: $ARGUMENTS (strip any `--auto` / `--headless` tokens before interpreting the remainder as target/path/PR/focus)

### Optional Mode Flags
- `--mode code|doc|gap|mixed` → force the review lens. Absent → auto-detect per the routing heuristics in Step 2
- `--council` → run multi-perspective adversarial review (5–7 specialists with two-phase challenge). Implies `--mode code` unless another mode is explicitly combined. Detailed orchestration lives in `references/council-mode.md` — load it only when this flag is set (or when auto-escalation triggers). Auto-escalate when the scope spans multiple concerns (security, performance, architecture, UX), the surface is high-risk (auth, payments, data integrity), or the user asks for "multi-perspective" / "adversarial" / "thorough" review.
- `--team` → force Agent Teams execution for council (error if unavailable). See `references/council-mode.md` for fallback behavior.
- `--inline-findings` → return findings inline and skip report-file output. **Do not pass** when the caller depends on a report file (e.g. the `andthen:exec-plan` skill's final gap gate, which feeds the `andthen:remediate-findings` skill).
- `--to-pr <number>` → post the consolidated report as a PR comment
- `--fix` → after the report is written, hand it to the `andthen:remediate-findings` skill to address actionable findings. **Incompatible with `--inline-findings`** — reject up-front, before running any review work. When combined with `--to-pr <number>`, post the PR comment first (so the comment reflects the original findings), then run remediation.
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Read the Workflow Rules, Guardrails, and relevant project guidelines before starting.
- The review itself is read-only. Do not modify the reviewed artifacts. Remediation only runs in Step 5 when `--fix` is set, and delegates editing to the `andthen:remediate-findings` skill.
- Reject `--fix` combined with `--inline-findings` before doing any review work — remediation requires the report file.
- Default to the minimum correct lens for the target.
- One lens per call (except **Mixed**, which intentionally runs both doc and code lenses).
- Load the lens-specific reference before running the lens — it carries the rubric, calibration pointers, and report format.
- Use the unified severity scale and per-mode verdict definitions from `references/review-verdict.md`.
- **Calibration-first**: Always load `references/review-calibration.md` (universal) plus the lens-specific calibration (cited by each lens reference) before categorising findings.
- **FIS Required / Deeper Context handling** (when a FIS is in scope — gap, doc, or mixed modes): treat `Required Context` blocks as the authoritative upstream intent at review time — do not re-read their source documents just to reconfirm inlined content. For `Deeper Context` anchors that are load-bearing for a finding, verify the anchor resolves in the source and warn (do not stop) on broken anchors. If a reviewer notices that a `Required Context` block's content appears to no longer match the current source, that is a legitimate doc-review finding (MEDIUM by default — spec should be re-run against the updated source), not an execution blocker. **Legacy FIS fallback**: a FIS authored before these sections existed will have neither. Fall back to whatever upstream-reference structures the legacy FIS uses: the old `## References & Constraints` heading and its `### Documentation & References` table (rows typed `file|doc|url|wire`), or prose mentions. Don't flag the absence of Required/Deeper Context as a defect on legacy FIS files.
- **Default output is a report file.** `--inline-findings` is the explicit opt-out; without it, always write the consolidated report to disk.
- **Automation mode** (`--auto` / `--headless`) — never ask the user what to do next. Auto-detect the minimum correct lens when possible, write the normal report artifact, propagate `--auto` to nested `andthen:*` skill invocations that accept it (including the `andthen:remediate-findings` skill when `--fix` is set; the `andthen:ops` skill is exempt — it is deterministic), and return deterministic verdict/report-path output. Stop with `BLOCKED:` (listing the minimum missing input) only when the requested mode cannot resolve a required target/baseline, an external action is unsafe, or report publication fails.


## GOTCHAS
- Treating all review requests as code review
- Running `--mode gap` without a real requirements baseline
- Running `--mode mixed` when the real question is requirements fit — use `--mode gap` instead
- Skipping the report file when `--inline-findings` was not passed — the default path always writes a file
- Passing `--inline-findings` when the caller will consume a report file (breaks the `andthen:remediate-findings` skill)
- Forgetting that the `andthen:remediate-findings` skill reads the canonical PASS/FAIL verdict block from gap reports — don't re-label, re-phrase, or re-order its columns
- Loading council-mode content when `--council` was not passed — council orchestration is gated behind `references/council-mode.md` for a reason


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

**Council mode** (`--council`): load `references/council-mode.md` and run the orchestration described there instead of standard code-mode orchestration. That reference owns reviewer selection, Agent Teams vs sub-agent execution paths, the two-phase adversarial debate, and the council-specific report structure.

**Gate**: Primary lens complete


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

For **Council** reviews, use the report structure defined in `references/council-mode.md` (§4 Report Structure) — only findings that survived both debate phases appear in the severity sections.

**Gate**: One consolidated result delivered


### 5. Remediate _(only when `--fix`)_

Invoke the `andthen:remediate-findings` skill with the report path as its argument (append `--auto` when `AUTO_MODE=true`). Skip only when there is nothing actionable to remediate — a `gap` PASS verdict, or a clean report with no findings. In every other case (code / doc / mixed / council), hand the report over and let the remediation skill scope the fixes.

Do not re-interpret findings or pre-filter by severity here. The `andthen:remediate-findings` skill owns the fix scoping — this step is pure delegation.

**Gate**: Remediation invoked or explicitly skipped with reason


## FOLLOW-UP ACTIONS

Skip this section when `AUTO_MODE=true`; print only the verdict/readiness, the absolute report path, and the remediation result when `--fix` ran. The verdict + report path is the orchestrator's machine-readable signal — it owns the decision to invoke the `andthen:remediate-findings` skill on FAIL / `Needs Significant Rework` / `Not Ready` / CRITICAL outcomes when `--fix` was not passed.

After the report, ask whether the user wants to:
1. Update the reviewed artifact based on findings
2. Focus on a narrower area
3. Proceed to implementation
4. Escalate to stakeholders for offline resolution (decisions that need human owners outside this conversation)
5. For **doc** mode (or the doc sub-pass of **mixed** mode) with a requirement-gap cluster on a PRD or draft spec/FIS (per `references/lens-doc.md` → Downstream Routing) — offer to run the `andthen:clarify` skill against the listed gaps. Fires even when `--fix` already ran in Step 5, since the `andthen:remediate-findings` skill cannot answer questions whose answers don't exist yet. Skip only when the dominant pattern is a defect cluster (route to the `andthen:remediate-findings` skill instead).
6. For FAIL / `Needs Significant Rework` / `Not Ready` / CRITICAL outcomes — run the `andthen:remediate-findings` skill with the report path or URL. Skip this prompt when `--fix` already ran remediation in Step 5.
