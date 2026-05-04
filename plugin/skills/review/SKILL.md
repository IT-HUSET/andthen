---
description: "The default review skill - start here for all reviews. Runs code, doc, gap, security, or mixed review - single lens or `--mode a,b` chains - plus multi-perspective council mode via `--council`. Trigger on 'review this', 'review this PR/spec/PRD', 'audit this', 'security review', 'OWASP review', 'does this match the spec', 'council review', 'adversarial review', 'critic review', 'red-team review', 'skeptic review', 'multi-reviewer'."
user-invocable: true
argument-hint: "[--mode <mode>[,<mode>...]] [--council] [--team] [--fix] [--inline-findings] [--output-dir <path>] [--from-pr <number>] [--to-pr <number>] [--worktree] [--auto|--headless] [target/files/PR/spec path]"
---

# Review

Unified review skill. Determine what is actually being reviewed, run the right lens inline, and produce one consolidated result.

## VARIABLES
ARGUMENTS: $ARGUMENTS (strip any flag tokens like `--mode`, `--council`, `--team`, `--fix`, `--inline-findings`, `--output-dir`, `--from-pr`, `--to-pr`, `--worktree`, `--auto`, or `--headless` before interpreting the remainder as target/path/PR/focus)

### Optional Mode Flags
- `--mode <mode>[,<mode>...]` → comma-separated list. Values: `code`, `doc`, `gap`, `security`, `mixed`. Single value runs that lens. Multiple values chain in declared order with shared context, producing one combined report. `mixed` auto-resolves (Step 2) and cannot be combined with explicit lenses. Absent → auto-detect per Step 2 routing.
- `--council` → multi-perspective review with debate (5-7 specialists, Findings Filter, synthesis). Augments the **code** and **security** lenses only; behavior depends on which applicable lenses are in scope:

  | Chain shape | Council behavior |
  |---|---|
  | Single lens, or chain containing exactly one of `code` / `security` | Scopes council to that lens. |
  | Chain contains both `code` and `security` | Runs once per lens; one council section per lens. |
  | Chain contains neither | Appends one lens at end (deliberate ordering exception): `security` when the target map fires any Step 2 security-escalation trigger, otherwise `code`. |

  **Security-trigger surface, `security` not in scope** — when the explicit lens set omits `security` and the target map fires a Step 2 security-escalation trigger, the chain is honored and council runs on `code` only — no silent broadening. See the Step 2 mixed-resolver carve-out for the explicit-`--mode code` rule and HIGH finding contract.

  Detailed orchestration in `references/council-mode.md` — load only when this flag is set or auto-escalation triggers (multi-concern scope, high-risk surface like auth/payments/data, or explicit "multi-perspective" / "adversarial" / "critic" / "skeptic" / "thorough" request).
- `--team` → force Agent Teams execution for council (error if unavailable). See `references/council-mode.md` for fallback behavior.
- `--inline-findings` → return findings inline and skip report-file output. **Do not pass** when the caller depends on a report file (e.g. the `andthen:exec-plan` skill's final gap gate, which feeds the `andthen:remediate-findings` skill).
- `--output-dir <path>` → explicit output directory override; bypasses the directory-priority resolution and source-code subdirectory guard in `${CLAUDE_PLUGIN_ROOT}/references/review-report-location.md`. Path must exist and be writable — `BLOCKED: --output-dir <path> not writable` in `AUTO_MODE`, warning + fallthrough in default mode. Incompatible with `--inline-findings` (reject up-front). When combined with `--to-pr`, file writes to `--output-dir` then posts as the PR comment.
- `--from-pr <number>` → use the named PR as the implementation scope. **Lightweight default**: fetch metadata via `gh pr view <N> --json number,title,baseRefName,headRefName,headRefOid,files,body`, change scope via `gh pr diff <N>`, and on-demand file blobs via `gh api repos/:owner/:repo/contents/<path>?ref=<headRefOid>` (base64-decoded). No `git checkout`, no worktree creation — the local working tree stays untouched. Mutually exclusive with explicit local target/path arguments — when both are supplied, reject up-front (`BLOCKED: --from-pr is mutually exclusive with a local target` in `AUTO_MODE`). Composes with `--to-pr <N>` to form the canonical "review this PR" call (`--from-pr 42 --to-pr 42`).
- `--worktree` → opt-in for full-fidelity local review of `--from-pr`: `gh pr checkout <N>` into a temp worktree (reuse the pattern from `plugin/skills/exec-plan/references/team-mode-orchestration.md`) and review from there. Use only when a lens genuinely needs project analyzers/build state at the PR HEAD.
- `--to-pr <number>` → post the consolidated report as a PR comment
- `--fix` → after the report is written, hand it to the `andthen:remediate-findings` skill to address actionable findings. **Incompatible with `--inline-findings`** — reject up-front, before running any review work. When combined with `--to-pr <number>`, post the PR comment first (so the comment reflects the original findings), then run remediation.
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Read the Workflow Rules, Guardrails, and relevant project guidelines before starting.
- Review is read-only; editing only runs in Step 5 (`--fix`) via the `andthen:remediate-findings` skill.
- Reject up-front: `--fix` + `--inline-findings` (remediation needs a file); `--output-dir` + `--inline-findings` (no file to apply to); any chain containing `mixed` (e.g. `--mode mixed,gap`) — `mixed` is a resolver, print correction and stop. `--worktree` without `--from-pr` is also rejected up-front (`BLOCKED: --worktree requires --from-pr` in `AUTO_MODE`); the flag has no other meaning in this skill (do not confuse with the `andthen:exec-plan` skill's `--worktree` semantics).
- **Explicit `--mode code` rule**: Explicit lens sets are honored — no silent broadening. See the Step 2 mixed-resolver carve-out for the canonical statement and HIGH finding contract.
- Default to the minimum correct lens; load lens references before running; chains run in declared order with shared target map — never re-classify or re-scan.
- **Anti-leniency**: `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` § Anti-Leniency Protocol — record findings at find time; severity and dismissal belong to calibration and the Findings Filter, not to ad-hoc rationalization.
- **Calibration-first**: Always load `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` (universal) plus the lens-specific calibration (cited by each lens reference) before categorising findings. The Critic sub-lens also loads `${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md`; the Findings Filter uses `${CLAUDE_PLUGIN_ROOT}/references/adversarial-challenge.md` after findings are collected.
- **FIS Required / Deeper Context handling** (when a FIS is in scope): see `references/lens-doc.md` and `references/lens-gap.md` for the authoritative handling rules (treat Required Context as upstream intent; warn on broken Deeper Context anchors; legacy FIS fallback).
- **Default output is a report file.** `--inline-findings` is the explicit opt-out; without it, always write the consolidated report to disk.
- **Automation mode** (`--auto` / `--headless`) — never ask the user what to do next; auto-detect the minimum correct lens; write the normal report artifact; propagate `--auto` to nested `andthen:*` skill invocations (the `andthen:ops` skill is exempt — it is deterministic). Stop with `BLOCKED:` only when the requested mode cannot resolve a required target/baseline, an external action is unsafe, or report publication fails.


## GOTCHAS
- Loading council-mode content when `--council` was not passed — council orchestration is gated behind `references/council-mode.md` for a reason
- Loading the OWASP checklists from inside the code lens — depth-of-OWASP belongs in `references/lens-security.md`. The code lens runs only the thin awareness pass.
- Treating the Critic as a top-level mode or optional flag: it is an always-on sub-lens inside code, doc, security, and gap
- Auto-adding `security` to an explicit `--mode code` run — see the Step 2 mixed-resolver carve-out for the explicit-`--mode code` rule and the `--mode mixed` exception
- Forgetting that the `andthen:remediate-findings` skill reads the canonical PASS/FAIL verdict block from gap reports — don't re-label, re-phrase, or re-order its columns
- Silently broadening `--from-pr` into a `--worktree` checkout when the lightweight path is insufficient for a lens — instead, emit a HIGH finding via the lens calibration ("deep code lens needs project analyzers — re-run with `--worktree`") and let the user re-invoke with the flag. Auto-promotion would mutate the working tree without consent.


## WORKFLOW

### 1. Resolve Target and Context

Determine what is being reviewed from: explicit path/PR/issue/URL in `ARGUMENTS`, explicit `--mode`, current pending changes (`git diff --stat`, `git diff --name-only`), or neighboring artifacts (plan/FIS/PRD/spec, changed files, related PR context).

Apply `--mode` value(s) during discovery. Per-lens discovery: `doc` → changed doc artifacts; `code`/`security` → changed implementation/config/IaC/CI/CD/lockfile files; `gap` → requirements baseline + implementation target (stop if either absent); `mixed` → all three (stop with `BLOCKED: mixed has no scope` when none exist). Stop with a missing-scope error only if no declared lens can resolve a target.

Build a concise target map: Review target · Relevant artifacts · Implementation scope · Requirements baseline · User intent. Use neighboring requirements docs to clarify context, not to override explicit review intent.

**When `--from-pr <N>` is set**: load `references/from-pr-mode.md` for the PR-as-input fetch mechanics, `--worktree` opt-in handling, and the lens-side trigger conditions for emitting the HIGH "needs `--worktree`" finding. The implementation scope is the named PR, not local pending changes — reject up-front when a local target/path was also supplied.

**Gate**: Review target and available context are explicit


### 2. Classify the Review Surface

Resolve the lens set for this run. Atomic lenses: **code** (implementation/config/tests — quality, architecture, domain language, UI/UX, thin security awareness); **doc** (spec/FIS/PRD/plan/ADR/design/prompt); **security** (implementation/IaC/CI/CD at OWASP depth — checklists, trust-boundary analysis, tooling); **gap** (baseline + implementation — "does this satisfy the requirements?").

Resolution rules:
- **Explicit single `--mode`** (`code` / `doc` / `security` / `gap`): use that lens.
- **Explicit chain** (`--mode a,b[,c,d]`): use the declared lenses in declared order.
- **Explicit `--mode mixed`**: auto-resolve to the subset of {doc, code, security, gap} that applies (see resolver below). May yield a single lens or a chain.
- **Absent `--mode`**: apply heuristics — first-match wins: (1) implementation-vs-baseline comparison → **mixed**; (2) broad audit with both docs and code → **mixed** (or suggest interactively); (3) explicit security intent, no baseline → **security**; (4) PR/code/implementation audit, no baseline → **code**; (5) only implementation changed → **code**; (6) only docs changed or target is a spec/FIS/PRD/plan → **doc**. The mere presence of neighboring requirements docs provides context, not a baseline — rule 1 fires only when the user's question is requirements-vs-implementation fit.

**Security escalation** (applies only when `--mode` is absent and the heuristic above selects `code` or `mixed`): scan the target map for security-critical surface. If any trigger below fires, add `security` to the resolved lens set — turning `code` into `code,security` (which becomes `mixed`), or adding `security` to an already-`mixed` chain.

Triggers (any one):
- Authentication, session, or authorization code paths (login, JWT, OAuth, RBAC, password handling)
- Payment, financial, or money-handling code
- Network-exposed handlers (HTTP/GraphQL/gRPC routes, webhooks, message consumers)
- User input parsing or file upload handling
- Secret, credential, or key handling; crypto operations
- LLM, agent, RAG, or tool-call flows
- IaC, CI/CD workflow, deployment script, lockfile, or supply-chain changes
- Native or cross-platform mobile surface (iOS/Android/React Native/Flutter/Expo) — keychain/keystore, deep-link handlers, certificate pinning, biometric flows, in-app purchase flows

Do not auto-add `security` when the user passed an explicit single-lens or explicit-chain `--mode`. Explicit `--mode code` (or any chain that explicitly omits `security`) is honored as-is — the code lens flags missed coverage as a HIGH finding (per the INSTRUCTIONS rule above) instead of broadening scope. Explicit `--mode mixed` is the one exception: `mixed` is a *resolver*, not a narrow lens, so its semantics are "include every applicable lens for this surface" — applying the security trigger inside the resolver is consistent with that intent and not a coercive override of a narrow user choice.

`mixed` resolution rules (applied after Step 1 discovery). Include each lens when its condition holds; run the resulting set in the order `doc, code, security, gap`:
- **doc** — when the target map has any doc artifact (explicit target or changed in worktree).
- **code** — when there is implementation to review (explicit target or changed in worktree).
- **security** — when implementation is in scope **and** any security-escalation trigger above fires. For explicit `--mode mixed`, the trigger check still applies; security only joins the chain when the surface warrants it.
- **gap** — when both a usable baseline and an implementation target exist. The explicit doc target may itself be the baseline.

A "usable baseline" is a spec/FIS/PRD/plan that genuinely scopes the implementation under review — not just any nearby document. If only one lens applies, run as a single-lens call. When the baseline is in the changed-docs set, the gap lens uses the post-change version (doc lens covers doc-side defects; don't double-count).

**Gate**: Lens set is resolved (single lens or ordered chain) and justified


### 3. Run the Selected Lens(es)

Load the lens reference(s) for the resolved lens set and run each lens inline. References carry the rubric, dimensions, calibration pointers, and report format:

| Lens | Reference |
|------|-----------|
| code | `references/lens-code.md` |
| doc | `references/lens-doc.md` |
| security | `references/lens-security.md` |
| gap | `references/lens-gap.md` |

Unified severity and verdict: `references/review-verdict.md` — CRITICAL / HIGH / MEDIUM / LOW; per-mode readiness/verdict rules defined there.

Each lens reference includes the always-on Critic sub-lens (`${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md`) and its calibration (`${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md`). This is not a separate mode token.

**Single lens**: load its reference and run the lens.

**Chain (multi-lens)**: load the deduplicated union of references upfront, then run each lens in declared order with shared target map — never re-classify or re-scan. Keep per-lens findings in distinct subsections. Overall readiness = worst across lenses.

**Code lens**: delegate one parallel reviewer per applicable sub-lens when sub-agents are supported; otherwise inline. Security awareness runs inline; deep security runs in the security lens.

**Security lens**: run the applicability gate (OWASP checklists for the surface), then checklists, trust-boundary analysis, scanners, and the always-on Critic sub-lens. Parallel per checklist when sub-agents are available.

**Council mode** (`--council`): load `references/council-mode.md`; council scopes to `code` and `security` and owns reviewer selection, debate, and report structure.

**Gate**: All declared lenses complete


### 4. Synthesize One Final Result

**Default path — write a consolidated markdown report file.** Use this deterministic suffix mapping (downstream skills parse the filename — do not vary):

| Resolved lens set | Report suffix | Mode token (in body) |
|---|---|---|
| `code` only | `code-review` | `code` |
| `doc` only | `doc-review` | `doc` |
| `gap` only | `gap-review` | `gap` |
| `security` only | `security-review` | `security` |
| Any chain (2+ lenses) | `mixed-review` | `mixed` |
| `code` (single) + `--council` | `council-review` | `council` |
| `security` (single) + `--council` | `council-review` | `council` |
| Chain + `--council` | `mixed-review` | `mixed` (council fills code and/or security sections) |

The mode token (third column) is the canonical, parseable string downstream consumers read (e.g. `andthen:remediate-findings`). Chains keep `mixed` on that line and put the resolved chain (e.g. `doc,code,gap`) on a separate `Resolved chain:` line for humans.

**Filename and directory** — resolve per [`review-report-location.md`](${CLAUDE_PLUGIN_ROOT}/references/review-report-location.md); pass the suffix from the table above and `--output-dir` when set.

Report/inline content: **Scope** · **Review mode used** (canonical token — exactly one, parseable line) · **Resolved chain** (when `mixed`) · **Per-lens findings** by severity · **Overall readiness/verdict** per `references/review-verdict.md`.

`--inline-findings`: skip the file; return the same structured content inline.

For `--to-pr <number>`: post via `gh pr comment <number> --body-file <report-path>`; mode token and resolved chain must be visible in the body.

For **chains**: one combined result with per-lens sections; merge overlapping findings (strongest framing wins); canonical PASS/FAIL block appears verbatim in the gap section. For **council**: use `references/council-mode.md` §4 Report Structure.

**Gate**: One consolidated result delivered


### 5. Remediate _(only when `--fix`)_

Invoke the `andthen:remediate-findings` skill with the report path (append `--auto` when `AUTO_MODE=true`). Skip only when nothing is actionable — a single-lens `gap` PASS, or a clean report with no findings across any lens.

**Gate**: Remediation invoked or explicitly skipped with reason


## FOLLOW-UP ACTIONS

Skip this section when `AUTO_MODE=true`; print only the verdict/readiness, the absolute report path, and the remediation result when `--fix` ran.

After the report, ask whether the user wants to:
1. Update the reviewed artifact based on findings
2. Focus on a narrower area
3. When the lens set includes **doc** and the doc lens produced a requirement-gap cluster — offer to run the `andthen:clarify` skill against the listed gaps (skip when `--fix` already ran)
4. For FAIL / `Needs Significant Rework` / `Not Ready` / CRITICAL outcomes — run the `andthen:remediate-findings` skill with the report path (skip when `--fix` already ran)
