---
description: "The default review skill - start here for all reviews. Runs code, doc, gap, or mixed review - single lens or `--mode a,b` chains - plus multi-perspective council mode via `--council`. Trigger on 'review this', 'review this PR/spec/PRD', 'audit this', 'does this match the spec', 'council review', 'adversarial review', 'red-team review', 'skeptic review', 'multi-reviewer'."
user-invocable: true
argument-hint: "[--mode <mode>[,<mode>...]] [--council] [--team] [--fix] [--inline-findings] [--to-pr <number>] [--auto|--headless] [target/files/PR/spec path]"
---

# Review

Unified review skill. Determine what is actually being reviewed, run the right lens inline, and produce one consolidated result.

Code, document, gap, and mixed reviews all run inside this skill using lens-specific references. Single lens by default; `--mode` accepts a comma-separated list (e.g. `--mode doc,code,gap`) to chain lenses in declared order with shared context and one combined report. `mixed` auto-resolves to the subset of {code, doc, gap} the inputs warrant. Each primary lens includes the always-on Red-Team sub-lens; multi-perspective **council mode** (5-7 specialized reviewers with Red-Team plus findings-filter debate) augments the code lens when `--council` is passed or scope/complexity warrants it.


## VARIABLES
ARGUMENTS: $ARGUMENTS (strip any flag tokens like `--mode`, `--council`, `--team`, `--fix`, `--inline-findings`, `--to-pr`, `--auto`, or `--headless` before interpreting the remainder as target/path/PR/focus)

### Optional Mode Flags
- `--mode <mode>[,<mode>...]` → comma-separated list. Values: `code`, `doc`, `gap`, `mixed`. Single value runs that lens. Multiple values chain in declared order with shared context, producing one combined report. `mixed` auto-resolves (Step 2) and cannot be combined with explicit lenses. Absent → auto-detect per Step 2 routing.
- `--council` -> multi-perspective red-team review (5-7 specialists, Findings Filter, synthesis). Augments the **code** lens only; in a chain, append `code` at the end if absent (deliberate exception to declared order). Detailed orchestration in `references/council-mode.md` - load only when this flag is set or auto-escalation triggers (multi-concern scope, high-risk surface like auth/payments/data, or explicit "multi-perspective" / "adversarial" / "red-team" / "skeptic" / "thorough" request).
- `--team` → force Agent Teams execution for council (error if unavailable). See `references/council-mode.md` for fallback behavior.
- `--inline-findings` → return findings inline and skip report-file output. **Do not pass** when the caller depends on a report file (e.g. the `andthen:exec-plan` skill's final gap gate, which feeds the `andthen:remediate-findings` skill).
- `--to-pr <number>` → post the consolidated report as a PR comment
- `--fix` → after the report is written, hand it to the `andthen:remediate-findings` skill to address actionable findings. **Incompatible with `--inline-findings`** — reject up-front, before running any review work. When combined with `--to-pr <number>`, post the PR comment first (so the comment reflects the original findings), then run remediation.
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Read the Workflow Rules, Guardrails, and relevant project guidelines before starting.
- The review itself is read-only. Do not modify the reviewed artifacts. Remediation only runs in Step 5 when `--fix` is set, and delegates editing to the `andthen:remediate-findings` skill.
- Reject `--fix` + `--inline-findings` up-front — remediation requires the report file.
- Reject any chain containing `mixed` (e.g. `--mode mixed,gap`) up-front — `mixed` is a resolver, not a lens. Print the correction and stop.
- Default to the minimum correct lens. Chain only when `--mode a,b` is explicit or `mixed` resolves to ≥2 lenses.
- Load the lens reference(s) before running — each carries the rubric, calibration pointers, and report format. Chains load the deduplicated union.
- Chains run in declared order with shared target map and findings — never re-classify or re-scan.
- Use the unified severity scale and per-mode verdict definitions from `references/review-verdict.md`.
- **Calibration-first**: Always load `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` (universal) plus the lens-specific calibration (cited by each lens reference) before categorising findings. The Red-Team sub-lens also loads `${CLAUDE_PLUGIN_ROOT}/references/red-team-calibration.md`; the Findings Filter uses `${CLAUDE_PLUGIN_ROOT}/references/adversarial-challenge.md` after findings are collected.
- **FIS Required / Deeper Context handling** (when a FIS is in scope — any lens set that includes `doc` or `gap`): treat `Required Context` blocks as the authoritative upstream intent at review time — do not re-read their source documents just to reconfirm inlined content. For `Deeper Context` anchors that are load-bearing for a finding, verify the anchor resolves in the source and warn (do not stop) on broken anchors. If a reviewer notices that a `Required Context` block's content appears to no longer match the current source, that is a legitimate doc-review finding (MEDIUM by default — spec should be re-run against the updated source), not an execution blocker. **Legacy FIS fallback**: a FIS authored before these sections existed will have neither. Fall back to whatever upstream-reference structures the legacy FIS uses: the old `## References & Constraints` heading and its `### Documentation & References` table (rows typed `file|doc|url|wire`), or prose mentions. Don't flag the absence of Required/Deeper Context as a defect on legacy FIS files.
- **Default output is a report file.** `--inline-findings` is the explicit opt-out; without it, always write the consolidated report to disk.
- **Automation mode** (`--auto` / `--headless`) — never ask the user what to do next. Auto-detect the minimum correct lens when possible, write the normal report artifact, propagate `--auto` to nested `andthen:*` skill invocations that accept it (including the `andthen:remediate-findings` skill when `--fix` is set; the `andthen:ops` skill is exempt — it is deterministic), and return deterministic verdict/report-path output. Stop with `BLOCKED:` (listing the minimum missing input) only when the requested mode cannot resolve a required target/baseline, an external action is unsafe, or report publication fails.


## GOTCHAS
- Treating all review requests as code review
- Running `--mode gap` without a real requirements baseline
- Combining `mixed` with explicit lenses — rejected up-front; `mixed` is a resolver
- Emitting a comma-separated mode token in the report — chains write `mixed` on the parseable line and the resolved chain on a separate `Resolved chain:` line
- Re-classifying or re-scanning per lens in a chain — chains carry forward
- Skipping the report file when `--inline-findings` was not passed — the default path always writes a file
- Passing `--inline-findings` when the caller will consume a report file (breaks the `andthen:remediate-findings` skill)
- Forgetting that the `andthen:remediate-findings` skill reads the canonical PASS/FAIL verdict block from gap reports — don't re-label, re-phrase, or re-order its columns
- Loading council-mode content when `--council` was not passed — council orchestration is gated behind `references/council-mode.md` for a reason
- Treating Red-Team as a top-level mode or optional flag: it is an always-on sub-lens inside code, doc, and gap


## WORKFLOW

### 1. Resolve Target and Context

Determine what the user wants reviewed, in priority order:
1. Explicit path, PR, issue, URL, or focus from `ARGUMENTS`
2. Explicit `--mode` flag
3. Current pending changes (`git diff --stat`, `git diff --name-only`) when no target is provided
4. Neighboring artifacts that clarify intent: plan/FIS/PRD/spec docs, changed implementation files, related issue/PR context

Apply explicit `--mode` value(s) during discovery, not only during later classification. For a comma-separated list, apply the union of the per-lens discovery rules below — discovery stops with the missing-side error only if **none** of the declared lenses can resolve a target.
- `doc`: when no explicit target is provided, include changed document artifacts (spec/FIS/PRD/plan/ADR/design/prompt/docs) in the target map; if no document targets are found and `doc` is the only declared lens, stop and report that doc mode has no matching scope
- `code`: when no explicit target is provided, include changed implementation/config/test files in the target map; if no implementation targets are found and `code` is the only declared lens, stop and report that code mode has no matching scope
- `gap`: when no explicit target is provided, resolve both a requirements baseline and an implementation target from the current changes plus neighboring artifacts; if either side cannot be resolved and `gap` is the only declared lens, stop and report that the missing side is required for gap review
- `mixed`: discover changed docs, changed implementation, and candidate baselines; classify any explicit target path (doc vs. implementation) and merge with worktree discovery. Lens set resolves in Step 2. Stop with `BLOCKED: mixed has no scope` when no explicit target is given and the worktree has none of the three.

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

Resolve the lens set for this run. The atomic lenses are:
- **code**: implementation, config, tests, or current code changes
- **doc**: spec, FIS, PRD, plan, ADR, design doc, prompt, or other written artifact
- **gap**: requirements baseline plus implementation target, where the real question is "does this implementation satisfy the requirements?"

Resolution rules:
- **Explicit single `--mode`** (`code` / `doc` / `gap`): use that lens.
- **Explicit chain** (`--mode a,b[,c]`): use the declared lenses in declared order.
- **Explicit `--mode mixed`**: auto-resolve to the subset of {doc, code, gap} that applies (see rules below). May yield a single lens or a chain.
- **Absent `--mode`**: route via the heuristics below.

Routing heuristics when `--mode` is absent. Apply in order; first match wins:
1. **Compares implementation against a requirements baseline** (spec, PRD, plan, FIS, issue) — phrasings like "review implementation of X", "does X match Y?", "is this consistent with the spec?", "audit Y against its requirements" → **mixed**. The resolver below picks the lens set. For a strict gap-only check, the user must pass `--mode gap` explicitly.
2. **Broad audit intent** ("review everything", "audit"), with both docs and code changed → suggest `--mode mixed` (interactive) or use **mixed** in `AUTO_MODE`.
3. **PR / code / change review or implementation audit**, no baseline in scope → **code**.
4. **Only implementation changed**, no baseline in scope → **code**.
5. **Only docs changed**, or the target is a spec/FIS/PRD/plan path with no implementation in scope → **doc**.

The mere presence of neighboring PRD/FIS/plan/spec artifacts is not enough to trigger rule 1. Nearby requirements docs provide context; they become a baseline only when the user's question is actually requirements-vs-implementation fit.

`mixed` resolution rules (applied after Step 1 discovery). Include each lens when its condition holds; run the resulting set in the order `doc, code, gap`:
- **doc** — when the target map has any doc artifact (explicit target or changed in worktree).
- **code** — when there is implementation to review (explicit target or changed in worktree).
- **gap** — when both a usable baseline and an implementation target exist. The explicit doc target may itself be the baseline.

A "usable baseline" is a spec/FIS/PRD/plan that genuinely scopes the implementation under review — not just any nearby document. If only one lens applies, run as a single-lens call. When the baseline is in the changed-docs set, the gap lens uses the **post-change** version; the doc lens already covers doc-side defects, so don't double-count.

**Gate**: Lens set is resolved (single lens or ordered chain) and justified


### 3. Run the Selected Lens(es)

Load the lens reference(s) for the resolved lens set and run each lens inline. References carry the rubric, dimensions, calibration pointers, and report format:

| Lens | Reference |
|------|-----------|
| code | `references/lens-code.md` |
| doc | `references/lens-doc.md` |
| gap | `references/lens-gap.md` |

Unified severity and verdict: `references/review-verdict.md` — CRITICAL / HIGH / MEDIUM / LOW; per-mode readiness/verdict rules defined there.

Each lens reference includes the always-on Red-Team sub-lens (`${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md`) and its calibration (`${CLAUDE_PLUGIN_ROOT}/references/red-team-calibration.md`). This is not a separate mode token.

**Single lens**: load its reference and run the lens.

**Chain (multi-lens)**: load the deduplicated union of references upfront, then run each lens in declared order. Each lens reads the shared target map and the findings produced by earlier lenses; never re-classify artifacts or re-scan baselines a previous lens already processed. Keep per-lens findings in distinct subsections in the final report. Overall readiness = worst across all lenses run (per `references/review-verdict.md`).

**Code lens** orchestration: when two or more lenses from `lens-code.md` apply (code quality, security, architecture, domain language, UI/UX) and sub-agents are supported, delegate one parallel reviewer per applicable lens. Otherwise run the lenses sequentially inline.

**Council mode** (`--council`): load `references/council-mode.md` and run its orchestration in place of standard code-lens orchestration. In a chain, council scopes to the code lens only (append `code` at end if absent — see `--council` flag); other lenses run normally. Council owns reviewer selection, Agent Teams vs sub-agent paths, the two-phase debate, and its report structure.

**Gate**: All declared lenses complete


### 4. Synthesize One Final Result

**Default path — write a consolidated markdown report file.** Use this deterministic suffix mapping (downstream skills parse the filename — do not vary):

| Resolved lens set | Report suffix | Mode token (in body) |
|---|---|---|
| `code` only | `code-review` | `code` |
| `doc` only | `doc-review` | `doc` |
| `gap` only | `gap-review` | `gap` |
| Any chain (2+ lenses) | `mixed-review` | `mixed` |
| `code` (single) + `--council` | `council-review` | `council` |
| Chain + `--council` | `mixed-review` | `mixed` (council fills the code-lens section) |

The mode token (third column) is the canonical, parseable string downstream consumers read (e.g. `andthen:remediate-findings`). Chains keep `mixed` on that line and put the resolved chain (e.g. `doc,code,gap`) on a separate `Resolved chain:` line for humans.

- **Filename**: `<review-target>-<suffix>-<agent>-<YYYY-MM-DD>.md` — on collision append `-2`, `-3`. `<agent>` is your agent short name (`claude`, `codex`, etc.; fall back to `agent`).
- **Directory priority**:
  1. **Spec directory** — when the review centers on a spec/FIS/plan, use its feature/spec directory
  2. **Target directory** — next to the primary review target
  3. **Fallback** — `{AGENT_TEMP}/reviews/` (default `.agent_temp/reviews/`)
- On completion, print the report's relative path from the project root.

Only when `--inline-findings` is present: skip the file and return the same structured content inline — same shape, no file.

Report/inline content must include:
- **Scope**
- **Review mode used**: the canonical token (`code`, `doc`, `gap`, `mixed`, or `council`) — exactly one, no comma list, no arrow. Parseable line.
- **Resolved chain** (when token = `mixed`): ordered lens list, e.g. `doc,code,gap`. For `--mode mixed`, prefix with the resolution: `mixed → doc,code,gap`. Human-readable, not parsed.
- **Findings by severity** using the unified scale (CRITICAL / HIGH / MEDIUM / LOW)
- **Readiness / verdict** per `references/review-verdict.md`:
  - `code`: severity counts + readiness label (`Ready` / `Needs Fixes` / `Blocked`)
  - `doc`: readiness label (`Ready` / `Needs Minor Updates` / `Needs Significant Rework` / `Not Ready`)
  - `gap`: PASS/FAIL verdict table (byte-level compatible — reproduce the canonical block verbatim)
  - `mixed` (chain): per-lens verdicts in declared order + overall readiness = worst across lenses
- **Recommended next action**

For `--to-pr <number>`: post the report's contents as a PR comment via `gh pr comment <number> --body-file <report-path>`. Print the direct comment URL (resolve via follow-up lookup if the command does not print one). The mode token, resolved chain (when applicable), and any referenced `plan_path` / `fis_path` must be visible in the body so downstream readers (including `andthen:remediate-findings`) can interpret the findings.

For **chains** (file or inline): one combined result — single header (Scope, mode token `mixed`, resolved chain, overall readiness), then per-lens sections in declared order. Merge overlapping findings (strongest framing wins) and tag each with its source lens. When the chain includes `gap`, the canonical PASS/FAIL block appears verbatim inside the gap section.

For **Council**: use the report structure in `references/council-mode.md` (§4 Report Structure) — only findings that survived both debate phases appear in severity sections. In a chain, that structure fills the code-lens section.

**Gate**: One consolidated result delivered


### 5. Remediate _(only when `--fix`)_

Invoke the `andthen:remediate-findings` skill with the report path (append `--auto` when `AUTO_MODE=true`). Skip only when nothing is actionable — a single-lens `gap` PASS, or a clean report with no findings across any lens. Otherwise hand over the report; the remediation skill scopes the fixes.

Do not re-interpret findings or pre-filter by severity here. The `andthen:remediate-findings` skill owns the fix scoping — this step is pure delegation.

**Gate**: Remediation invoked or explicitly skipped with reason


## FOLLOW-UP ACTIONS

Skip this section when `AUTO_MODE=true`; print only the verdict/readiness, the absolute report path, and the remediation result when `--fix` ran. The verdict + report path is the orchestrator's machine-readable signal — it owns the decision to invoke the `andthen:remediate-findings` skill on FAIL / `Needs Significant Rework` / `Not Ready` / CRITICAL outcomes when `--fix` was not passed.

After the report, ask whether the user wants to:
1. Update the reviewed artifact based on findings
2. Focus on a narrower area
3. Proceed to implementation
4. Escalate to stakeholders for offline resolution (decisions that need human owners outside this conversation)
5. When the lens set includes **doc** and the doc lens produced a requirement-gap cluster on a PRD or draft spec/FIS (per `references/lens-doc.md` → Downstream Routing) — offer to run the `andthen:clarify` skill against the listed gaps. Fires even when `--fix` already ran in Step 5, since the `andthen:remediate-findings` skill cannot answer questions whose answers don't exist yet. Skip only when the dominant pattern is a defect cluster (route to the `andthen:remediate-findings` skill instead).
6. For FAIL / `Needs Significant Rework` / `Not Ready` / CRITICAL outcomes — run the `andthen:remediate-findings` skill with the report path or URL. Skip this prompt when `--fix` already ran remediation in Step 5.
