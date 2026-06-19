---
description: "The default review skill - start here for all reviews. Runs code, doc, gap, security, or mixed review - single lens or `--mode a,b` chains - plus multi-perspective council mode via `--council`. Trigger on 'review this', 'review this PR/spec/PRD', 'audit this', 'security review', 'OWASP review', 'does this match the spec', 'council review', 'adversarial review', 'critic review', 'red-team review', 'skeptic review', 'multi-reviewer'."
user-invocable: true
argument-hint: "[--mode <mode>[,<mode>...]] [--council] [--team] [--fix] [--inline-findings] [--output-dir <path>] [--from-pr <number>] [--to-pr <number>] [--worktree] [--fanout|--no-fanout] [--visual] [--auto] [target/files/PR/spec path]"
---

# Review

## VARIABLES
ARGUMENTS: $ARGUMENTS (strip any flag tokens like `--mode`, `--council`, `--team`, `--fix`, `--inline-findings`, `--output-dir`, `--from-pr`, `--to-pr`, `--worktree`, `--fanout`, `--no-fanout`, `--visual`, `--auto`, or `--headless` before interpreting the remainder as target/path/PR/focus)

### Optional Mode Flags
- `--mode <mode>[,<mode>...]` → comma-separated list. Values: `code`, `doc`, `gap`, `security`, `mixed`. Single value runs that lens. Multiple values chain with a shared target map, producing one combined report; declared order governs report/synthesis order, not execution (find-passes dispatch as one parallel batch – see Step 4 *Chain*). `mixed` auto-resolves (Step 2) and cannot be combined with explicit lenses. Absent → auto-detect per Step 2 routing.
- `--council` → multi-perspective review with debate; scales with chain shape (see `references/council-mode.md`). Single `doc`/`gap` is rejected up-front (see the INSTRUCTIONS reject list for the verbatim `BLOCKED:` string). Detailed orchestration in `references/council-mode.md` – load only when this flag is set. Council is opt-in via `--council` only; the "adversarial/critic/skeptic" trigger vocabulary activates this skill, not council.
- `--team` → force Agent Teams execution for council (error if unavailable). See `references/council-mode.md` for fallback behavior.
- `--inline-findings` → return findings inline and skip report-file output. **Do not pass** when the caller depends on a report file (e.g. the `andthen:exec-plan` skill's final gap gate, which feeds the `andthen:remediate-findings` skill).
- `--output-dir <path>` → explicit output directory override; bypasses the directory-priority resolution and source-code subdirectory guard in `${CLAUDE_PLUGIN_ROOT}/references/review-report-location.md`. Path must exist and be writable – `BLOCKED: --output-dir <path> not writable` in `AUTO_MODE`, warning + fallthrough in default mode. When combined with `--to-pr`, file writes to `--output-dir` then posts as the PR comment.
- `--from-pr <number>` → use the named PR as implementation scope (lightweight fetch, local tree untouched; mechanics in `references/from-pr-mode.md`). Mutually exclusive with a local target – reject up-front (`BLOCKED: --from-pr is mutually exclusive with a local target` in `AUTO_MODE`). Composes with `--to-pr` to form `--from-pr 42 --to-pr 42`.
- `--worktree` → opt-in full-fidelity local review of `--from-pr` when a lens needs project analyzers/build state at PR HEAD; mechanics in `references/from-pr-mode.md`.
- `--to-pr <number>` → post the consolidated report as a PR comment
- `--fanout` / `--no-fanout` → force-on or force-off partition-based sub-agent fan-out for the active lens. Auto-triggers by diff size: ≥20 files, ≥1000 LOC (excluding generated/vendored/lockfile noise), or 3+ top-level packages. Applies to `code` and `gap` lenses only. Partition strategy and boundary pass in [`references/large-diff-fanout.md`](references/large-diff-fanout.md) (and the no-horizontal-partitioning GOTCHA).
- `--fix` → after the report is written, hand it to the `andthen:remediate-findings` skill to address actionable findings. When combined with `--to-pr <number>`, post the PR comment first (so the comment reflects the original findings), then run remediation.
- `--visual` → VISUAL_MODE: after the consolidated report file is written (and any `--to-pr` / `--fix` actions land), invoke the `andthen:visualize` skill on the produced report. Convenience handoff – the visualizer owns HTML rendering and note export.
- `--auto` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Read project rules and guidelines (`CLAUDE.md` / `AGENTS.md` and referenced files) before starting.
- **Intent + Rules Context** – collect both bundles per [`intent-and-rules-context.md`](${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md) in Step 1; they feed Step 3 Guardrails and Step 5 routing.
- **Guardrails pass** – lens-independent, run once (Step 3); per-finding rule citation required (`Guardrails Coverage` is the trace).
- **Routing gate** – classify every accepted finding (`Class:` + `Routing: Fix|Note`) before the report; `--fix` auto-applies Fix only. Routing keys on **fix character, not severity**. Mechanism, class enum, and recall rationale in Step 5a.
- Review is read-only; editing only runs in Step 6 (`--fix`) via the `andthen:remediate-findings` skill. **Exceptions**: Step 5a may call the `andthen:ops` skill for deterministic reconciliation-ledger transitions (`update-ledger bump-recurrence` and terminal re-open with refuting evidence), and if any lens surfaces a recurring trap (defect class across findings, or a repeat of an existing `Learnings` entry), after the report is written append via the `andthen:ops` skill (`update-learnings add` form). Applies to every lens, not just `gap`.
- Reject up-front: `--fix` + `--inline-findings` (remediation needs a file); `--output-dir` + `--inline-findings` (no file to apply to); `--visual` + `--inline-findings` (no file to visualize); any chain containing `mixed` (e.g. `--mode mixed,gap`) – `mixed` is a resolver, print correction and stop; `--council` with a single-lens `--mode doc` or `--mode gap` (`BLOCKED: --council requires code/security in scope or a chain of 2+ lenses` in `AUTO_MODE`; no silent broadening – rerun without `--council`, or add another lens). `--worktree` without `--from-pr` is also rejected up-front (`BLOCKED: --worktree requires --from-pr` in `AUTO_MODE`).
- Default to the minimum correct lens; load lens references before running; chains share one target map (never re-classify or re-scan).
- **Calibration-first / anti-leniency**: load `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` (universal, § Anti-Leniency Protocol) plus each lens's calibration before categorising findings; record at find time. The Critic sub-lens also loads `${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md`; the Findings Filter uses `${CLAUDE_PLUGIN_ROOT}/references/findings-filter-templates.md` after findings are collected.
- **Structured findings**: Code, doc, gap, security, and council findings use the field contract from `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md` / `references/council-mode.md`; lens reports may render it as markdown, but the fields must be present.
- **Critic enforcement**: Every selected lens runs the Critic posture as an actual finding pass (mechanism in Step 4). Prefer the installed `review-critic` agent, then a generic fresh-context sub-agent, then inline fallback with a required `Critic Coverage` note.
- **FIS Required / Deeper Context handling** (when a FIS is in scope): see `references/lens-doc.md` and `references/lens-gap.md` for the authoritative handling rules (treat Required Context as upstream intent; warn on broken Deeper Context anchors; legacy FIS fallback).
- **Automation mode** (`--auto`) – never ask the user what to do next; auto-detect the minimum correct lens; write the normal report artifact; propagate `--auto` to nested `andthen:*` skill invocations (the `andthen:ops` skill is exempt – it is deterministic). Stop with `BLOCKED:` only when the requested mode cannot resolve a required target/baseline, an external action is unsafe, or report publication fails.


## GOTCHAS
- Treating the Critic as a top-level mode or optional flag: it is an always-on sub-lens inside code, doc, security, and gap
- Silently broadening `--from-pr` into a `--worktree` checkout when the lightweight path is insufficient for a lens – instead, emit a HIGH finding via the lens calibration ("deep code lens needs project analyzers – re-run with `--worktree`") and let the user re-invoke with the flag. Auto-promotion would mutate the working tree without consent.
- **Routing every accepted finding into Fix** – find-passes favor recall, so collapsing the buckets is how `--fix` turns into chain-drift; see Step 5a Fix-bucket criteria.
- **Routing a mechanically-fixable defect to Note because it is MEDIUM/LOW** – the inverse failure: a bounded, decision-free `code-defect` is Fix-eligible at any severity, and over-routing to Note strands a convergence loop; see Step 5a Fix-bucket criteria.
- Load `references/refactor-invariants.md` on deletion/rename/relocation/cache/codegen/schema/parameter-threading diffs; not on additive-only work.
- **Horizontal partitioning under `--fanout`** – never partition by architectural layer (hides cross-layer invariants); see [`references/large-diff-fanout.md`](references/large-diff-fanout.md) § Partition Strategy.
- **Wrapping a chain lens in a per-lens orchestrator sub-agent** – dispatch is flat by design, not by host limitation: do not wrap a chain lens in a per-lens orchestrator. Expand each lens into its leaf sub-agent tasks (Step 4 *Chain*) and fire them all as siblings from the orchestrator.


## WORKFLOW

### 1. Resolve Target and Context

Determine what is being reviewed from: explicit path/PR/issue/URL in `ARGUMENTS`, explicit `--mode`, current pending changes (`git diff --stat`, `git diff --name-only`), or neighboring artifacts (plan/FIS/PRD/spec, changed files, related PR context).

Apply `--mode` value(s) during discovery. Per-lens discovery: `doc` → changed doc artifacts; `code`/`security` → changed implementation/config/IaC/CI/CD/lockfile files; `gap` → requirements baseline + implementation target (stop if either absent); `mixed` → all three (stop with `BLOCKED: mixed has no scope` when none exist). Stop with a missing-scope error only if no declared lens can resolve a target.

Build a concise target map: Review target · Relevant artifacts · Implementation scope · Requirements baseline · User intent. Use neighboring requirements docs to clarify context, not to override explicit review intent.

**Intent + Rules Context collection.** Alongside the target map, collect both bundles (**Project Rules Context**, **Intent Context**) per [`intent-and-rules-context.md`](${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md); they feed Step 3's Guardrails pass and Step 5's routing gate. When no governing artifact is discoverable, omit the Intent Context bundle and record `Intent Context: none discoverable` in the target map – do not synthesize intent from the code itself.

**When `--from-pr <N>` is set**: load `references/from-pr-mode.md` for the PR-as-input fetch mechanics, `--worktree` opt-in handling, and the lens-side trigger conditions for emitting the HIGH "needs `--worktree`" finding. The implementation scope is the named PR, not local pending changes – reject up-front when a local target/path was also supplied.

**Reconciliation-ledger load.** When the review covers code against a governing FIS (code/gap lenses), read that FIS's adjacent ledger (`{fis-without-ext}.reconciliation-ledger.md`). A doc-lens-only review, or any review with no governing FIS, loads no ledger → record `Reconciliation Ledger: none` and skip the Step 5a match step (schema, adjacency, match/recurrence rules in [`reconciliation-ledger.md`](${CLAUDE_PLUGIN_ROOT}/references/reconciliation-ledger.md)).

**Gate**: Review target, lens-set context, the Intent + Rules Context bundles, and the reconciliation-ledger state are explicit (or absent with the reason recorded)


### 2. Classify the Review Surface

Resolve the lens set for this run. Atomic lenses: **code** (implementation/config/tests – quality, architecture, domain language, UI/UX, thin security awareness); **doc** (spec/FIS/PRD/plan/ADR/design/prompt); **security** (implementation/IaC/CI/CD at OWASP depth – checklists, trust-boundary analysis, tooling); **gap** (baseline + implementation – "does this satisfy the requirements?").

Resolution rules:
- **Explicit single `--mode`** (`code` / `doc` / `security` / `gap`): use that lens.
- **Explicit chain** (`--mode a,b[,c,d]`): use the declared lenses in declared order.
- **Explicit `--mode mixed`**: auto-resolve to the subset of {doc, code, security, gap} that applies (see resolver below). May yield a single lens or a chain.
- **Absent `--mode`**: apply heuristics – first-match wins: (1) implementation-vs-baseline comparison → **mixed**; (2) broad audit with both docs and code → **mixed** (or suggest interactively); (3) explicit security intent, no baseline → **security**; (4) PR/code/implementation audit, no baseline → **code**; (5) only implementation changed → **code**; (6) only docs changed or target is a spec/FIS/PRD/plan → **doc**. The mere presence of neighboring requirements docs provides context, not a baseline – rule 1 fires only when the user's question is requirements-vs-implementation fit.

**Security escalation** (applies only when `--mode` is absent and the heuristic above selects `code` or `mixed`): scan the target map for security-critical surface. If any trigger fires (the trigger list lives in `references/lens-security.md` § Escalation Triggers), add `security` to the resolved lens set – turning `code` into `code,security` (which becomes `mixed`), or adding `security` to an already-`mixed` chain.

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

**Critic pass execution**: Run a separate Critic pass per lens before filtering – prefer the installed `review-critic` agent, else a generic fresh-context sub-agent, else inline with a required `Critic Coverage` note (per `references/lens-adversarial.md` § Sub-agent dispatch).

**Single lens**: load its reference and run the lens.

**Chain (multi-lens)**: load the deduplicated union of references upfront, then dispatch every lens's find-pass as **one flat parallel batch of sub-agents from the orchestrator** – not lens-by-lens in sequence. The find-passes share only the Step 1 target map and Intent + Rules Context and have no data dependency, so sequential stepping only adds wall-time and lets one lens prime the next. Never re-classify or re-scan.

Expand each lens into its leaf find-passes per its reference and fire them all as siblings of the orchestrator (flat by design – see the *per-lens orchestrator sub-agent* GOTCHA): `lens-doc.md` and `lens-gap.md` (rubric/mechanical pass + Critic each), `lens-code.md` (N applicable specialists + generalist Critic), `lens-security.md` (per-checklist + Critic). `--fanout` partitions (code/gap) join the same batch as further siblings.

After the batch returns, synthesize in the orchestrator: per lens, merge its specialist/Critic findings, apply that lens's calibration and Findings Filter, and assign the per-lens verdict. Keep per-lens findings in distinct subsections. Overall readiness = worst across lenses. When sub-agents are unavailable, fall back to running the lenses inline in declared order.

Only **find-passes** join the flat batch. Under `--council`, the code/security leaves above are that lens's council specialist find-passes; the within-lens filter (Devil's Advocate → Synthesis Challenger) and the cross-lens pass keep their sequential data dependency and run during/after synthesis, per `references/council-mode.md` (§3b and § Cross-Lens Chain Mode). Under `--team`, leaf tasks become team tasks per `references/council-mode.md` §3a.

**Gate**: All declared lenses complete


### 5. Route, then Synthesize One Final Result

#### 5a. Apply the Routing Gate

Before writing the report, classify and route each accepted finding (from the Guardrails pass and every lens). The class lands as a `Class:` field and the routing decision lands as a `Routing:` field on each finding in the report; `--fix` (Step 6) auto-applies only **Fix**-bucket findings.

**Finding class** (required, parseable, one per finding):
- `code-defect` – the reviewed artifact is wrong relative to the governing Intent / Expected Outcomes / requirements and the correction is clear. Covers code/config/tests in implementation reviews; in doc-only reviews, mechanical document defects (broken anchors, missing required proof coverage, inconsistent prescribed details, rule violations) where the reviewed artifact and project rules determine the correct text.
- `spec-stale` – the requirements artifact no longer describes the implementation or decision now in force.
- `design-changed` – the implementation reflects a coherent design pivot from the FIS / spec, requiring explicit reconciliation.
- `ambiguous-intent` – the artifact does not define enough intent to decide whether the code or spec is wrong.

`spec-stale` and `design-changed` are not code-remediation findings: route them to spec-amendment + ADR reconciliation and never auto-apply code edits for them. If `design-changed` fires and no ADR records the decision, include a companion finding routed to the `andthen:architecture` skill in `--mode trade-off` to create the ADR before spec amendment. `ambiguous-intent` is not auto-applied because the required decision is missing. Do not label a deterministic document defect `ambiguous-intent` merely because it appears in a spec; reserve that class for missing or undecidable intent.

**Reconciliation-ledger match** (when a ledger was loaded in Step 1). Compute each finding's stable ID and route by matched entry status per [`reconciliation-ledger.md`](${CLAUDE_PLUGIN_ROOT}/references/reconciliation-ledger.md) (§ Stable finding ID, § Match-and-route rules, § Recurrence and escalation). Tokens that section governs and this gate emits: `RECONCILE REQUIRED` matches route `Routing: Note`; re-open a suppressed entry with refuting evidence via the `andthen:ops` skill `update-ledger add`; on an unreconciled OPEN `spec-stale` / `design-changed` re-surfacing call `update-ledger bump-recurrence`; a `RECONCILE REQUIRED` escalation clears only via `update-fis design-change` + ADR.

**Class-scored verdict.** The gap-verdict's three dimensions are fed only by `code-defect` findings; reconciliation-class findings route Note and never lower them (`references/review-verdict.md`, `reconciliation-ledger.md` § Verdict scoping). The byte-level `## Verdict` block format is unchanged.

**CONVERGED stopping criterion.** Emit a `CONVERGED` signal when this pass produced **no new `code-defect` at severity ≥ MEDIUM** – where OPEN-ledger-matched findings are *not* "new". It is an **additive line** alongside the unchanged byte-level `## Verdict` block – never inside it; the Verdict block is a parser contract and CONVERGED plus any ledger annotations are parsed separately.

**Auto-Remediation signal (loop control).** Emit one additive line carrying the single resolved token (e.g. `Auto-Remediation: STALLED`, not the `PENDING | STALLED | CLEAR` menu) beside (never inside) the `## Verdict` block, in the machine-stable line form consumers branch on – bare line, no fence/indent/marker, once (grammar and `PENDING` / `STALLED` / `CLEAR` definitions in `references/review-verdict.md` § Loop Convergence Signals). Under `--council`, compute it from the final post-synthesis routed findings only, so advisory perspectives that do not survive synthesis never inflate it.

**Fix-bucket criteria** (all must hold). Find-passes favor recall (per `critic-calibration.md`), so reviews accept more than warrant auto-application; this gate keeps recall-biased findings out of `--fix`. It routes by **fix character, not defect severity** – severity measures impact-if-unfixed (feeds the verdict, sets escalation priority); auto-apply safety depends on whether the *correction* is unambiguous, so a bounded, decision-free fix is equally safe at MEDIUM or CRITICAL:
- Confidence ≥ 75
- Scope relation `primary` (traces to a line, section, or stated outcome the change set itself adds, modifies, or claims to deliver)
- Does not introduce scope past the change set's stated Intent / Expected Outcomes (when Intent Context was loaded)
- Class is `code-defect`
- The correction is **mechanical and bounded**. **Falsifiable test**: the correct replacement is *uniquely determined* by the reviewed artifact, project rules, requirements, or a cited source – if choosing it means picking between plausible alternatives, depends on intent the artifact does not pin down, or needs a product / design / architecture / requirements decision, it is **not** mechanical → Note (even at high severity). Missing-feature and completeness gaps whose fix needs a design decision stay Note even when they gate the verdict – those are precisely the findings a human must resolve.
- **Security caveat**: a wrong security fix can pass verification yet stay exploitable, so route a security finding to Fix only when the secure correction is mechanical and unambiguous (parameterize a query, verify the signature on the raw body); anything needing a security-design judgment stays Note.

All other accepted findings → **Note** bucket: real, surfaced inline in the report, but never auto-applied. Note findings travel with the report so the user (or the `andthen:remediate-findings` skill operating in surfaced-only mode) can decide on them.

**Intent anchor.** When Intent Context was loaded in Step 1, apply the canonical anchor moves from [`intent-and-rules-context.md`](${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md) (Non-Goal → Dismiss or demote to Note; deferred → Note; contradicts Expected Outcome → Fix-eligible regardless of severity heuristics). When no Intent Context was loaded, the routing gate operates on severity, confidence, and scope alone – do not invent intent to justify routing. **On tie, default to Note**: without the Intent anchor the scope-expansion guard is silently weaker, so the gate leans conservative.

**Verdict still wins for code-defects.** The routing gate decides what `--fix` auto-applies; it does *not* hide real `code-defect` severity. In gap mode, the class-scored verdict rule above is authoritative: only `code-defect` findings feed Functionality / Completeness / Wiring. Reconciliation-class findings (`spec-stale`, `design-changed`, `ambiguous-intent`) remain surfaced as Notes and annotations; they do not lower the canonical PASS/FAIL verdict, even when severe.

**Gate**: Every accepted finding carries a `Class:` value and a `Routing:` decision with a one-line rationale (severity / confidence / scope / class, plus the Intent anchor citation when one applied)

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

Report/inline content: **Scope** · **Review mode used** (canonical token – exactly one, parseable line) · **Resolved chain** (when `mixed`) · **Intent Context** (one line: source path of the governing FIS/PRD/clarify artifact, or `none discoverable`) · **Guardrails** (`Guardrails Coverage: N checked, M findings` line + any guardrail-violation findings with rule cited by source) · **Cross-Lens Synthesis** (chain + `--council` only – `## Cross-Lens Synthesis` H2 placed above the per-lens sections, leads with `Coverage attacked:` proof-of-work line and lists Cross-Lens Critic findings by severity) · **Per-lens findings** by severity, with each finding carrying exactly one class value as `Class: <code-defect | spec-stale | design-changed | ambiguous-intent>` (for example, `Class: spec-stale`; never emit the enum string as the value) plus a `Routing: Fix | Note` field and one-line rationale (the `Routing:` field is what the `andthen:remediate-findings` skill parses) · **Overall readiness/verdict** per `references/review-verdict.md` · **CONVERGED** signal as an additive line beside (never inside) the byte-level `## Verdict` block when the pass produced no new `code-defect` at severity ≥ MEDIUM (OPEN-ledger-matched findings are not new) · **Auto-Remediation** signal (`PENDING` / `STALLED` / `CLEAR`) as an additive line beside the Verdict block · **Reconciliation annotations** (when a ledger was loaded): ledger-matched findings noted with their entry stable ID and status (OPEN / RECONCILE REQUIRED → Note / tracked, CLOSED-WITHDRAWN → suppressed), and any `bump-recurrence` / `RECONCILE REQUIRED` transition this run made.

`--inline-findings`: skip the file; return the same structured content inline.

For `--to-pr <number>`: post via `gh pr comment <number> --body-file <report-path>`; mode token and resolved chain must be visible in the body.

For **chains**: one combined result with per-lens sections; merge overlapping findings (strongest framing wins); canonical PASS/FAIL block appears verbatim in the gap section. When `--council` is set on a chain, the cross-lens Critic + Devil's Advocate + Synthesis Challenger trio (per `references/council-mode.md` *Cross-Lens Chain Mode*) replaces this lightweight merge: per-lens findings are tagged by source lens and fed through the trio, surviving findings render in the new `## Cross-Lens Synthesis` section above the per-lens sections, and per-lens sections remain intact. For **single-lens council**: use `references/council-mode.md` §4 Report Structure.

**Gate**: One consolidated result delivered


### 6. Remediate _(only when `--fix`)_

Invoke the `andthen:remediate-findings` skill with the report path (append `--auto` when `AUTO_MODE=true`). The `andthen:remediate-findings` skill reads the `Routing:` field on each finding and auto-applies the **Fix** bucket only; **Note** findings are surfaced in the remediation completion report for the user to decide on. Skip only when nothing is actionable – a single-lens `gap` PASS, a clean report with no findings, or a report where every finding routed to Note (state the reason explicitly).

**Gate**: Remediation invoked or explicitly skipped with reason


### 7. Visual Review _(only when `--visual`)_

After the consolidated report is written and any `--to-pr` / `--fix` actions land, invoke the `andthen:visualize` skill on the report path. Print both the report path and the visualizer's output path.

**Gate**: Visualization invoked or explicitly skipped with reason


## FOLLOW-UP ACTIONS

Skip this section when `AUTO_MODE=true`; print only the verdict/readiness, the absolute report path, and the remediation result when `--fix` ran.

After the report, ask whether the user wants to:
1. Update the reviewed artifact based on findings
2. Focus on a narrower area
3. When the lens set includes **doc** and the doc lens produced a requirement-gap cluster – offer to run the `andthen:clarify` skill against the listed gaps (skip when `--fix` already ran)
4. For FAIL / `Needs Significant Rework` / `Not Ready` / CRITICAL outcomes – run the `andthen:remediate-findings` skill with the report path (skip when `--fix` already ran)
5. **Review visually** – run `andthen:visualize <report-path>` to triage findings by severity, navigate via the risk-map chips, and copy section-anchored notes (skip when `--visual` already ran)
