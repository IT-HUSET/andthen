---
description: "The default review skill - start here for all reviews. Runs code, doc, gap, security, or mixed review - single lens or `--mode a,b` chains - plus multi-perspective council mode via `--council`. Trigger on 'review this', 'review this PR/spec/PRD', 'audit this', 'security review', 'OWASP review', 'does this match the spec', 'council review', 'adversarial review', 'critic review', 'red-team review', 'skeptic review', 'multi-reviewer'."
user-invocable: true
argument-hint: "[--mode <mode>[,<mode>...]] [--council] [--team] [--fix] [--inline-findings] [--output-dir <path>] [--from-pr <number>] [--to-pr <number>] [--worktree] [--fanout|--no-fanout] [--visual] [--auto|--headless] [target/files/PR/spec path]"
---

# Review

Unified review skill. Determine what is actually being reviewed, run the right lens inline, and produce one consolidated result.

## VARIABLES
ARGUMENTS: $ARGUMENTS (strip any flag tokens like `--mode`, `--council`, `--team`, `--fix`, `--inline-findings`, `--output-dir`, `--from-pr`, `--to-pr`, `--worktree`, `--fanout`, `--no-fanout`, `--visual`, `--auto`, or `--headless` before interpreting the remainder as target/path/PR/focus)

### Optional Mode Flags
- `--mode <mode>[,<mode>...]` → comma-separated list. Values: `code`, `doc`, `gap`, `security`, `mixed`. Single value runs that lens. Multiple values chain with a shared target map, producing one combined report; declared order governs report/synthesis order, not execution (find-passes dispatch as one parallel batch – see Step 4 *Chain*). `mixed` auto-resolves (Step 2) and cannot be combined with explicit lenses. Absent → auto-detect per Step 2 routing.
- `--council` → multi-perspective review with debate (structured findings, Findings Filter, synthesis). Scales with the chain shape – within-lens specialist councils (5-7 reviewers) augment `code` and `security`; chains add a cross-lens Critic + Devil's Advocate + Synthesis Challenger pass on top:

  | Chain shape | Council behavior |
  |---|---|
  | Single `code` or `security` | Within-lens specialist council (5-7 reviewers, scoped to that lens). |
  | Single `doc` or `gap` | **Reject up-front**: `BLOCKED: --council requires code/security in scope or a chain of 2+ lenses` (no silent broadening; rerun without `--council`, or add another lens to the chain). |
  | Any chain (2+ lenses) | Per-lens reviews run as today; within-lens councils run for `code` / `security` when in scope; **then** a cross-lens Critic + Devil's Advocate + Synthesis Challenger pass attacks lens-boundary surface (contradictions, silence-licenses-risk, verdict-vs-finding mismatch) over the merged finding set. |

  **Security-trigger surface, `security` not in scope** – when an explicit lens set omits `security` and the target map fires a Step 2 security-escalation trigger, the chain is honored with no silent broadening: code-inclusive chains run the `code` within-lens council plus the cross-lens pass; chains without `code` / `security` run the cross-lens pass only; single `code` runs the existing HIGH "surface warrants security lens" finding. See the Step 2 mixed-resolver carve-out for the explicit-`--mode code` rule and HIGH finding contract.

  Detailed orchestration in `references/council-mode.md` – load only when this flag is set. (The "adversarial" / "critic" / "skeptic" / "thorough" vocabulary activates the review skill itself, per the `description`; it does not silently upgrade a review to council. Council is opt-in via `--council`.)
- `--team` → force Agent Teams execution for council (error if unavailable). See `references/council-mode.md` for fallback behavior.
- `--inline-findings` → return findings inline and skip report-file output. **Do not pass** when the caller depends on a report file (e.g. the `andthen:exec-plan` skill's final gap gate, which feeds the `andthen:remediate-findings` skill).
- `--output-dir <path>` → explicit output directory override; bypasses the directory-priority resolution and source-code subdirectory guard in `${CLAUDE_PLUGIN_ROOT}/references/review-report-location.md`. Path must exist and be writable – `BLOCKED: --output-dir <path> not writable` in `AUTO_MODE`, warning + fallthrough in default mode. When combined with `--to-pr`, file writes to `--output-dir` then posts as the PR comment.
- `--from-pr <number>` → use the named PR as the implementation scope. **Lightweight default**: fetch metadata via `gh pr view <N> --json number,title,baseRefName,headRefName,headRefOid,files,body`, change scope via `gh pr diff <N>`, and on-demand file blobs via `gh api repos/:owner/:repo/contents/<path>?ref=<headRefOid>` (base64-decoded). No `git checkout`, no worktree creation – the local working tree stays untouched. Mutually exclusive with explicit local target/path arguments – when both are supplied, reject up-front (`BLOCKED: --from-pr is mutually exclusive with a local target` in `AUTO_MODE`). Composes with `--to-pr <N>` to form the canonical "review this PR" call (`--from-pr 42 --to-pr 42`).
- `--worktree` → opt-in for full-fidelity local review of `--from-pr`: `gh pr checkout <N>` into a temp worktree (reuse the pattern from `plugin/skills/exec-plan/references/team-mode-orchestration.md`) and review from there. Use only when a lens genuinely needs project analyzers/build state at the PR HEAD.
- `--to-pr <number>` → post the consolidated report as a PR comment
- `--fanout` / `--no-fanout` → force-on or force-off partition-based sub-agent fan-out for the active lens. Default is auto by diff size: ≥20 files, ≥1000 LOC (excluding generated/vendored/lockfile noise), or 3+ top-level packages. Partitions the diff into 2–5 vertical slices (feature/concern shape, **not** horizontal `api/` / `domain/` / `infra/` layers) and dispatches one sub-agent per partition, then runs a boundary pass attacking cross-partition surface. Composes with `--council` and chain dispatch – no artificial concurrency cap (every leaf fires as a sibling of the orchestrator); choose the fewest partitions that still give coverage. See [`references/large-diff-fanout.md`](references/large-diff-fanout.md). Applies to `code` and `gap` lenses; `doc` is small enough to run inline and `security` already parallelizes per checklist.
- `--fix` → after the report is written, hand it to the `andthen:remediate-findings` skill to address actionable findings. When combined with `--to-pr <number>`, post the PR comment first (so the comment reflects the original findings), then run remediation.
- `--visual` → VISUAL_MODE: after the consolidated report file is written (and any `--to-pr` / `--fix` actions land), invoke the `andthen:visualize` skill on the produced report. Convenience handoff – the visualizer owns HTML rendering, severity-coded risk-map chips, finding-card navigation, note export, and `.agent_temp/visual-review/` output.
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- **Fully read and understand all project rules, guardrails, principles and guidelines (as defined in `CLAUDE.md` / `AGENTS.md` and other referenced files) before starting work.**
- **Intent + Rules Context** – collect both bundles per [`intent-and-rules-context.md`](${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md) up-front in Step 1; the bundles supply the falsifier evidence the Guardrails pass (Step 3) and the routing gate (Step 5) depend on. When no governing artifact is discoverable, omit the Intent Context bundle and state so explicitly in the report so downstream consumers know routing operated without an Intent anchor.
- **Guardrails pass** – a lens-independent finding axis run once per review. Procedure lives in Step 3; findings and the coverage line land in the consolidated report's **Guardrails** section. Per-finding rule citation is required – `Guardrails Coverage` is the trace, not the assertion.
- **Routing gate** – every accepted finding is routed into **Fix** or **Note** before the report is written (Step 5 sub-step). `--fix` auto-applies the Fix bucket only; Note findings travel with the report for the user (or downstream skill) to decide on. This is what prevents recall-biased find-passes from flowing unfiltered into remediation.
- Review is read-only; editing only runs in Step 6 (`--fix`) via the `andthen:remediate-findings` skill. **Exception**: if any lens surfaces a recurring trap (defect class across findings, or a repeat of an existing `Learnings` entry), after the report is written append via the `andthen:ops` skill (`update-learnings add` form). Applies to every lens, not just `gap`.
- Reject up-front: `--fix` + `--inline-findings` (remediation needs a file); `--output-dir` + `--inline-findings` (no file to apply to); `--visual` + `--inline-findings` (no file to visualize); any chain containing `mixed` (e.g. `--mode mixed,gap`) – `mixed` is a resolver, print correction and stop; `--council` with a single-lens `--mode doc` or `--mode gap` (`BLOCKED: --council requires code/security in scope or a chain of 2+ lenses` in `AUTO_MODE`; no silent broadening – rerun without `--council`, or add another lens). `--worktree` without `--from-pr` is also rejected up-front (`BLOCKED: --worktree requires --from-pr` in `AUTO_MODE`); the flag has no other meaning in this skill (do not confuse with the `andthen:exec-plan` skill's `--worktree` semantics).
- Default to the minimum correct lens; load lens references before running; chains share one target map (never re-classify or re-scan) and dispatch all lens find-passes as one parallel sub-agent batch – see Step 4 *Chain* dispatch.
- **Anti-leniency**: `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` § Anti-Leniency Protocol – record findings at find time; severity and dismissal belong to calibration and the Findings Filter, not to ad-hoc rationalization.
- **Calibration-first**: Always load `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` (universal) plus the lens-specific calibration (cited by each lens reference) before categorising findings. The Critic sub-lens also loads `${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md`; the Findings Filter uses `${CLAUDE_PLUGIN_ROOT}/references/adversarial-challenge.md` after findings are collected.
- **Structured findings**: Code, doc, gap, security, and council findings use the contract from `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md` / `references/council-mode.md`: reviewer, severity, confidence, location, scope relation, finding, threatened assumption or invariant, evidence, impact, suggested fix, verification needed. Lens reports may render this as markdown, but the fields must be present.
- **Critic enforcement**: Every selected lens runs the Critic posture as an actual finding pass. When sub-agents are supported, dispatch a read-first Critic task that explicitly includes `lens-adversarial.md`, `critic-calibration.md`, and `review-calibration.md`; prefer the installed `review-critic` agent for that task when the host can select it, otherwise use a generic fresh-context sub-agent. Inline fallback is allowed only when sub-agents are unavailable, and the report must include a short `Critic Coverage` note naming what assumptions, unhappy paths, and hidden coupling were attacked.
- **FIS Required / Deeper Context handling** (when a FIS is in scope): see `references/lens-doc.md` and `references/lens-gap.md` for the authoritative handling rules (treat Required Context as upstream intent; warn on broken Deeper Context anchors; legacy FIS fallback).
- **Default output is a report file.** `--inline-findings` is the explicit opt-out; without it, always write the consolidated report to disk.
- **Automation mode** (`--auto` / `--headless`) – never ask the user what to do next; auto-detect the minimum correct lens; write the normal report artifact; propagate `--auto` to nested `andthen:*` skill invocations (the `andthen:ops` skill is exempt – it is deterministic). Stop with `BLOCKED:` only when the requested mode cannot resolve a required target/baseline, an external action is unsafe, or report publication fails.


## GOTCHAS
- Loading council-mode content when `--council` was not passed – council orchestration is gated behind `references/council-mode.md` for a reason
- Loading the OWASP checklists from inside the code lens – depth-of-OWASP belongs in `references/lens-security.md`. The code lens runs only the thin awareness pass.
- Treating the Critic as a top-level mode or optional flag: it is an always-on sub-lens inside code, doc, security, and gap
- Auto-adding `security` to an explicit `--mode code` run – see the Step 2 mixed-resolver carve-out for the explicit-`--mode code` rule and the `--mode mixed` exception
- Forgetting that the `andthen:remediate-findings` skill reads the canonical PASS/FAIL verdict block from gap reports – don't re-label, re-phrase, or re-order its columns
- Silently broadening `--from-pr` into a `--worktree` checkout when the lightweight path is insufficient for a lens – instead, emit a HIGH finding via the lens calibration ("deep code lens needs project analyzers – re-run with `--worktree`") and let the user re-invoke with the flag. Auto-promotion would mutate the working tree without consent.
- **Routing every accepted finding into Fix** – the lens find-passes are calibrated to favor recall (per `critic-calibration.md`), so most reviews accept more findings than warrant auto-application. Only **Fix**-bucket findings (HIGH/CRITICAL, confidence ≥ 75, primary scope, no scope expansion past Intent) feed `--fix`; everything else stays in the **Note** bucket. Collapsing the buckets is how the `andthen:review --fix` invocation turns into chain-drift through the `andthen:remediate-findings` skill.
- **Reviewing without Intent Context** – when a FIS, PRD, `clarify` output, or active plan story governs the change set, skipping the Intent Context collection in Step 1 strips Step 5's routing gate of its primary falsifier source. "You didn't handle X" may already be a documented Non-Goal; without the artifact loaded, neither the Critic nor the routing gate can tell.
- **Skipping `references/refactor-invariants.md` on a deletion/rename/relocation/cache/codegen/schema/parameter-threading diff** – the rubric exists precisely for the invariant class no individual hunk hosts. Trigger conditions are diff-shape only; apply when they fire even when each hunk reads correctly in isolation. Equally: do **not** load it on a non-refactor diff (additive feature work without any trigger) – it adds noise without coverage.
- **Horizontal partitioning under `--fanout`** – partitioning by architectural layer (`api/`, `domain/`, `infra/`, `tests/`) hides exactly the cross-layer invariants `--fanout` is meant to surface. Use vertical slices (feature/concern shape); fall back to package partitioning when no slice signal resolves; never partition by layer. See [`references/large-diff-fanout.md`](references/large-diff-fanout.md) § Partition Strategy.
- **Trying to run a chain lens as a single nested sub-agent** – the host cannot nest sub-agents, so a lens find-pass cannot be one orchestrator sub-agent that then spawns its own specialists / Critic / partitions. Expand each lens into its leaf sub-agent tasks (Step 4 *Chain*) and fire them all as siblings from the orchestrator; the orchestrator keeps the target map, Guardrails pass, per-lens synthesis, and routing.


## WORKFLOW

### 1. Resolve Target and Context

Determine what is being reviewed from: explicit path/PR/issue/URL in `ARGUMENTS`, explicit `--mode`, current pending changes (`git diff --stat`, `git diff --name-only`), or neighboring artifacts (plan/FIS/PRD/spec, changed files, related PR context).

Apply `--mode` value(s) during discovery. Per-lens discovery: `doc` → changed doc artifacts; `code`/`security` → changed implementation/config/IaC/CI/CD/lockfile files; `gap` → requirements baseline + implementation target (stop if either absent); `mixed` → all three (stop with `BLOCKED: mixed has no scope` when none exist). Stop with a missing-scope error only if no declared lens can resolve a target.

Build a concise target map: Review target · Relevant artifacts · Implementation scope · Requirements baseline · User intent. Use neighboring requirements docs to clarify context, not to override explicit review intent.

**Intent + Rules Context collection.** Alongside the target map, collect the two context bundles per [`intent-and-rules-context.md`](${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md): **Project Rules Context** (rules/guardrails/guidelines from `CLAUDE.md` / `AGENTS.md` and referenced files, with source paths) and **Intent Context** (Intent / Expected Outcomes / Non-Goals / deferrals from the governing FIS/PRD/clarify artifact, with source paths). The bundles feed Step 3's Guardrails pass and Step 5's routing gate. When no governing artifact is discoverable, omit the Intent Context bundle and record `Intent Context: none discoverable` in the target map – do not synthesize intent from the code itself.

**When `--from-pr <N>` is set**: load `references/from-pr-mode.md` for the PR-as-input fetch mechanics, `--worktree` opt-in handling, and the lens-side trigger conditions for emitting the HIGH "needs `--worktree`" finding. The implementation scope is the named PR, not local pending changes – reject up-front when a local target/path was also supplied.

**Gate**: Review target, lens-set context, and the Intent + Rules Context bundles are explicit (or absent with the reason recorded)


### 2. Classify the Review Surface

Resolve the lens set for this run. Atomic lenses: **code** (implementation/config/tests – quality, architecture, domain language, UI/UX, thin security awareness); **doc** (spec/FIS/PRD/plan/ADR/design/prompt); **security** (implementation/IaC/CI/CD at OWASP depth – checklists, trust-boundary analysis, tooling); **gap** (baseline + implementation – "does this satisfy the requirements?").

Resolution rules:
- **Explicit single `--mode`** (`code` / `doc` / `security` / `gap`): use that lens.
- **Explicit chain** (`--mode a,b[,c,d]`): use the declared lenses in declared order.
- **Explicit `--mode mixed`**: auto-resolve to the subset of {doc, code, security, gap} that applies (see resolver below). May yield a single lens or a chain.
- **Absent `--mode`**: apply heuristics – first-match wins: (1) implementation-vs-baseline comparison → **mixed**; (2) broad audit with both docs and code → **mixed** (or suggest interactively); (3) explicit security intent, no baseline → **security**; (4) PR/code/implementation audit, no baseline → **code**; (5) only implementation changed → **code**; (6) only docs changed or target is a spec/FIS/PRD/plan → **doc**. The mere presence of neighboring requirements docs provides context, not a baseline – rule 1 fires only when the user's question is requirements-vs-implementation fit.

**Security escalation** (applies only when `--mode` is absent and the heuristic above selects `code` or `mixed`): scan the target map for security-critical surface. If any trigger below fires, add `security` to the resolved lens set – turning `code` into `code,security` (which becomes `mixed`), or adding `security` to an already-`mixed` chain.

Triggers (any one):
- Authentication, session, or authorization code paths (login, JWT, OAuth, RBAC, password handling)
- Payment, financial, or money-handling code
- Network-exposed handlers (HTTP/GraphQL/gRPC routes, webhooks, message consumers)
- User input parsing or file upload handling
- Secret, credential, or key handling; crypto operations
- LLM, agent, RAG, or tool-call flows
- IaC, CI/CD workflow, deployment script, lockfile, or supply-chain changes
- Native or cross-platform mobile surface (iOS/Android/React Native/Flutter/Expo) – keychain/keystore, deep-link handlers, certificate pinning, biometric flows, in-app purchase flows

Do not auto-add `security` when the user passed an explicit single-lens or explicit-chain `--mode`. Explicit `--mode code` (or any chain that explicitly omits `security`) is honored as-is – the code lens flags missed coverage as a HIGH finding (per the INSTRUCTIONS rule above) instead of broadening scope. Explicit `--mode mixed` is the one exception: `mixed` is a *resolver*, not a narrow lens, so its semantics are "include every applicable lens for this surface" – applying the security trigger inside the resolver is consistent with that intent and not a coercive override of a narrow user choice.

`mixed` resolution rules (applied after Step 1 discovery). Include each lens when its condition holds; run the resulting set in the order `doc, code, security, gap`:
- **doc** – when the target map has any doc artifact (explicit target or changed in worktree).
- **code** – when there is implementation to review (explicit target or changed in worktree).
- **security** – when implementation is in scope **and** any security-escalation trigger above fires. For explicit `--mode mixed`, the trigger check still applies; security only joins the chain when the surface warrants it.
- **gap** – when both a usable baseline and an implementation target exist. The explicit doc target may itself be the baseline.

A "usable baseline" is a spec/FIS/PRD/plan that genuinely scopes the implementation under review – not just any nearby document. If only one lens applies, run as a single-lens call. When the baseline is in the changed-docs set, the gap lens uses the post-change version (doc lens covers doc-side defects; don't double-count).

**Gate**: Lens set is resolved (single lens or ordered chain) and justified


### 3. Guardrails Pass

Run once against the change set, before any lens executes. Produces lens-independent findings that land in the consolidated report's **Guardrails** section.

1. Use the **Project Rules Context** bundle collected in Step 1 (per [`intent-and-rules-context.md`](${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md)) – the rules, guardrails, principles, and guidelines are already enumerated with source paths, not pulled ambiently from context.
2. Filter to those a diff can verify (skip process-only rules like *"verify before claiming done"* that aren't observable in the artifact).
3. For each applicable rule, check the change set; record violations as findings with the rule cited by source (file and section). **Per-finding rule citation is required** – an uncited "guardrails violation" is the assertion-not-trace anti-pattern this pass exists to prevent.
4. Classify rule violations by concrete risk and the consuming verdict policy. This pass is trace-based enforcement: cite the violated rule by source and route it through the normal severity / verdict flow; do not infer an automatic hard-fail policy from the rule source tier alone.
5. Report `Guardrails Coverage: N checked, M findings`; carry the line and any findings into Step 5 for the consolidated report. The line is the audit trail – a missing or zeroed Coverage line means the pass did not run, not that nothing was checked.

**Gate**: Guardrails pass complete with per-finding rule citations; coverage line and any findings ready for the consolidated report


### 4. Run the Selected Lens(es)

Load the lens reference(s) for the resolved lens set and run each lens inline. References carry the rubric, dimensions, calibration pointers, and report format:

| Lens | Reference |
|------|-----------|
| code | `references/lens-code.md` |
| doc | `references/lens-doc.md` |
| security | `references/lens-security.md` |
| gap | `references/lens-gap.md` |

Unified severity and verdict: `references/review-verdict.md` – CRITICAL / HIGH / MEDIUM / LOW; per-mode readiness/verdict rules defined there.

Each lens reference includes the always-on Critic sub-lens (`${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md`) plus its finding calibration (`${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md`) and anti-leniency calibration (`${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md`). This is not a separate mode token.

**Critic pass execution**: For `code`, `doc`, `gap`, and `security`, run or simulate a separate Critic pass before filtering:
- Preferred: installed `review-critic` custom agent, selected as the executor for a read-first task prompt supplied with the target map, lens scope, relevant lens reference, `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md`, `${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md`, and `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md`.
- Fallback: generic fresh-context sub-agent with the same read-first instruction.
- Last resort: inline application of the Critic rubric with a required `Critic Coverage` note in the report.

**Single lens**: load its reference and run the lens.

**Chain (multi-lens)**: load the deduplicated union of references upfront, then dispatch every lens's find-pass as **one flat parallel batch of sub-agents from the orchestrator** – not lens-by-lens in sequence. The find-passes share only the Step 1 target map and Intent + Rules Context and have no data dependency, so sequential stepping only adds wall-time and lets one lens's findings prime the next (the cross-lens anchoring the always-on Critic exists to fight). Never re-classify or re-scan.

Expand each lens into its leaf sub-agent tasks and fire them all as siblings of the orchestrator (no nesting – see the *single nested sub-agent* GOTCHA):
- **doc** → one sub-agent for the rubric pass + one Critic sub-agent.
- **gap** → one sub-agent for the mechanical gap + quality-evidence pass + one Critic sub-agent (the behavioral dry-run).
- **code** → the N applicable specialists + one generalist Critic (per `references/lens-code.md`).
- **security** → one sub-agent per applicable OWASP checklist + one Critic (per `references/lens-security.md`).
- `--fanout` partitions (code/gap) join the same batch as further siblings.

After the batch returns, synthesize in the orchestrator: per lens, merge its specialist/Critic findings, apply that lens's calibration and Findings Filter, and assign the per-lens verdict. Keep per-lens findings in distinct subsections. Overall readiness = worst across lenses. When sub-agents are unavailable, fall back to running the lenses inline in declared order.

Only **find-passes** join the flat batch. Under `--council`, the code/security leaves above are that lens's council specialist find-passes; the within-lens filter (Devil's Advocate → Synthesis Challenger) and the cross-lens pass keep their sequential data dependency and run during/after synthesis, per `references/council-mode.md` (§3b and § Cross-Lens Chain Mode). Under `--team`, leaf tasks become team tasks per `references/council-mode.md` §3a.

**Code lens**: delegate one parallel reviewer per applicable sub-lens when sub-agents are supported; otherwise inline. Security awareness runs inline; deep security runs in the security lens.

**Security lens**: run the applicability gate (OWASP checklists for the surface), then checklists, trust-boundary analysis, scanners, and the always-on Critic sub-lens. Parallel per checklist when sub-agents are available.

**Council mode** (`--council`): load `references/council-mode.md`; within-lens specialist councils run for `code` and `security` when in scope (reviewer selection, custom-agent preference, debate, structured findings, report structure), and on any chain (2+ lenses) a cross-lens Critic + Devil's Advocate + Synthesis Challenger pass runs after per-lens reviews and feeds the consolidated report's `## Cross-Lens Synthesis` section.

**Gate**: All declared lenses complete


### 5. Route, then Synthesize One Final Result

#### 5a. Apply the Routing Gate

Before writing the report, route each accepted finding (from the Guardrails pass and every lens) into a **Fix** or **Note** bucket. The routing decision lands as a `Routing:` field on each finding in the report; `--fix` (Step 6) auto-applies only **Fix**-bucket findings.

**Fix-bucket criteria** (all must hold):
- Severity HIGH or CRITICAL
- Confidence ≥ 75
- Scope relation `primary` (traces to a line, section, or stated outcome the change set itself adds, modifies, or claims to deliver)
- Does not introduce scope past the change set's stated Intent / Expected Outcomes (when Intent Context was loaded)

All other accepted findings → **Note** bucket: real, surfaced inline in the report, but never auto-applied. Note findings travel with the report so the user (or the `andthen:remediate-findings` skill operating in surfaced-only mode) can decide on them.

**Intent anchor.** When Intent Context was loaded in Step 1, apply the canonical anchor moves from [`intent-and-rules-context.md`](${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md) (Non-Goal → Dismiss or demote to Note; deferred → Note; contradicts Expected Outcome → Fix-eligible regardless of severity heuristics). When no Intent Context was loaded, the routing gate operates on severity, confidence, and scope alone – do not invent intent to justify routing. **On tie, default to Note**: without the Intent anchor the scope-expansion guard is silently weaker, so the gate leans conservative.

**Verdict still wins for FAIL.** The routing gate decides what `--fix` auto-applies; it does *not* downgrade verdict severity. A CRITICAL Note-routed finding (e.g. one demoted because it contradicts a Non-Goal but is still a real correctness issue) still drives the overall readiness/verdict per `references/review-verdict.md`. Routing is about *auto-application*, not *severity*.

**Gate**: Every accepted finding carries a `Routing:` decision with a one-line rationale (severity / confidence / scope, plus the Intent anchor citation when one applied)

#### 5b. Write the consolidated report

**Default path – write a consolidated markdown report file.** Use this deterministic suffix mapping (downstream skills parse the filename – do not vary):

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

The mode token (third column) is the canonical, parseable string downstream consumers read (e.g. the `andthen:remediate-findings` skill). Chains keep `mixed` on that line and put the resolved chain (e.g. `doc,code,gap`) on a separate `Resolved chain:` line for humans.

**Filename and directory** – resolve per [`review-report-location.md`](${CLAUDE_PLUGIN_ROOT}/references/review-report-location.md); pass the suffix from the table above and `--output-dir` when set.

Report/inline content: **Scope** · **Review mode used** (canonical token – exactly one, parseable line) · **Resolved chain** (when `mixed`) · **Intent Context** (one line: source path of the governing FIS/PRD/clarify artifact, or `none discoverable`) · **Guardrails** (`Guardrails Coverage: N checked, M findings` line + any guardrail-violation findings with rule cited by source) · **Cross-Lens Synthesis** (chain + `--council` only – `## Cross-Lens Synthesis` H2 placed above the per-lens sections, leads with `Coverage attacked:` proof-of-work line and lists Cross-Lens Critic findings by severity) · **Per-lens findings** by severity, with each finding carrying a `Routing: Fix | Note` field and one-line rationale (parsed by the `andthen:remediate-findings` skill) · **Overall readiness/verdict** per `references/review-verdict.md`.

`--inline-findings`: skip the file; return the same structured content inline.

For `--to-pr <number>`: post via `gh pr comment <number> --body-file <report-path>`; mode token and resolved chain must be visible in the body.

For **chains**: one combined result with per-lens sections; merge overlapping findings (strongest framing wins); canonical PASS/FAIL block appears verbatim in the gap section. When `--council` is set on a chain, the cross-lens Critic + Devil's Advocate + Synthesis Challenger trio (per `references/council-mode.md` *Cross-Lens Chain Mode*) replaces this lightweight merge: per-lens findings are tagged by source lens and fed through the trio, surviving findings render in the new `## Cross-Lens Synthesis` section above the per-lens sections, and per-lens sections remain intact. For **single-lens council**: use `references/council-mode.md` §4 Report Structure.

**Gate**: One consolidated result delivered


### 6. Remediate _(only when `--fix`)_

Invoke the `andthen:remediate-findings` skill with the report path (append `--auto` when `AUTO_MODE=true`). The `andthen:remediate-findings` skill reads the `Routing:` field on each finding and auto-applies the **Fix** bucket only; **Note** findings are surfaced in the remediation completion report for the user to decide on. Skip only when nothing is actionable – a single-lens `gap` PASS, a clean report with no findings, or a report where every finding routed to Note (state the reason explicitly).

**Gate**: Remediation invoked or explicitly skipped with reason


### 7. Visual Review _(only when `--visual`)_

After the consolidated report is written and any `--to-pr` / `--fix` actions land, invoke the `andthen:visualize` skill on the report path. Print both the report path and the visualizer's output path. The visualizer renders findings as severity-coded cards with a risk-map chip row above the Findings section, surfaces the verdict/readiness as the status pill, and exposes the gap-mode PASS/FAIL block as the section TL;DR callout.

**Gate**: Visualization invoked or explicitly skipped with reason


## FOLLOW-UP ACTIONS

Skip this section when `AUTO_MODE=true`; print only the verdict/readiness, the absolute report path, and the remediation result when `--fix` ran.

After the report, ask whether the user wants to:
1. Update the reviewed artifact based on findings
2. Focus on a narrower area
3. When the lens set includes **doc** and the doc lens produced a requirement-gap cluster – offer to run the `andthen:clarify` skill against the listed gaps (skip when `--fix` already ran)
4. For FAIL / `Needs Significant Rework` / `Not Ready` / CRITICAL outcomes – run the `andthen:remediate-findings` skill with the report path (skip when `--fix` already ran)
5. **Review visually** – run `andthen:visualize <report-path>` to triage findings by severity, navigate via the risk-map chips, and copy section-anchored notes (skip when `--visual` already ran)
