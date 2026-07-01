---
description: "The default review skill - start here for code, docs, gap, security, mixed, PR, adversarial, critic, skeptic, red-team, and multi-reviewer reviews. Runs one or more lenses, proves coverage before verdict, routes findings into Fix/Note, and can remediate or visualize the report."
user-invocable: true
argument-hint: "[--mode <mode>[,<mode>...]] [--council] [--team] [--fix] [--inline-findings] [--output-dir <path>] [--from-pr <number>] [--to-pr <number>] [--worktree] [--fanout|--no-fanout] [--visual] [--auto] [target/files/PR/spec path]"
---

# Review

## VARIABLES
ARGUMENTS: $ARGUMENTS (strip flag tokens before interpreting the remainder as target/path/PR/focus)

Flags:
- `--mode <mode>[,<mode>...]`: `code`, `doc`, `gap`, `security`, or `mixed`; chains share one target map. `mixed` is a resolver and cannot be combined with explicit lenses.
- `--council`: opt-in multi-perspective review; load `references/council-mode.md`. Reject single-lens `doc` or `gap`.
- `--team`: force Agent Teams for council; error if unavailable.
- `--from-pr <number>` / `--worktree` / `--to-pr <number>`: PR input, optional full-fidelity checkout, optional PR comment. Load `references/from-pr-mode.md` when `--from-pr` is set; `--worktree` requires it.
- `--fanout` / `--no-fanout`: force partition fan-out on/off for `code` and `gap`; otherwise use `references/large-diff-fanout.md` triggers.
- `--output-dir <path>`: writable report directory override.
- `--inline-findings`: return the report inline; incompatible with `--fix`, `--visual`, or `--output-dir`.
- `--fix`: after writing the report, invoke the `andthen:remediate-findings` skill on Fix-routed findings only.
- `--visual`: after report publication/remediation, invoke the `andthen:visualize` skill.
- `--auto`: no prompts; propagate to nested `andthen:*` skills except the deterministic `andthen:ops` skill.


## NON-NEGOTIABLES

- Read project rules (`CLAUDE.md` / `AGENTS.md`) and collect **Project Rules Context** + **Intent Context** per `${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md` before reviewing.
- Review is read-only unless `--fix` runs. Only the `andthen:remediate-findings` skill edits review findings; only the `andthen:ops` skill may update ledgers/learnings.
- Load `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` before judging severity. Every selected lens also runs the Critic posture from `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md` with `${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md`.
- **Coverage before verdict**: prove what was reviewed before saying Ready/PASS. A clean report without concrete coverage proof is a failed review, not a clean review.
- Findings favor recall first. Filtering and routing happen after discovery; do not talk yourself out of recording a falsifiable issue during the find pass.
- Reject up-front (emit the `BLOCKED:` reason in `AUTO_MODE`): `--fix`/`--visual`/`--output-dir` with `--inline-findings`; any chain containing `mixed`; single-lens `--council --mode doc` or `--council --mode gap` (`BLOCKED: --council requires code/security in scope or a chain of 2+ lenses`); `--worktree` without `--from-pr`; `--from-pr` with a local target.


## WORKFLOW

### 1. Resolve Scope

Build one target map:
- Review target, implementation scope, requirements baseline, user intent
- Resolved lens set and why
- Intent Context source or `none discoverable`
- Reconciliation ledger path/status when a governing FIS exists

Lens resolution:
- Explicit `--mode code|doc|gap|security`: run that lens.
- Explicit chain: run declared lenses in declared order for reporting, but dispatch find-passes as one flat batch.
- Explicit `--mode mixed`: include every applicable lens from `{doc, code, security, gap}`; `mixed` is a resolver, so it still applies the security trigger internally.
- No `--mode`: choose the first matching lens set:

| Signal | Lens set |
|---|---|
| requirements-vs-implementation fit | `mixed` |
| broad docs+code audit | `mixed` |
| explicit security intent, no baseline | `security` |
| PR/code/implementation audit, no baseline | `code` |
| only implementation changed | `code` |
| only docs changed, or target is a spec/FIS/PRD/plan | `doc` |

- Neighboring requirements docs are context, not a baseline; rule 1 fires only when the question is requirements-vs-implementation fit.
- Add `security` only when no explicit mode/chain was supplied and a `references/lens-security.md` escalation trigger fires. Explicit `--mode code` is honored as-is; the code lens flags missed security coverage as a HIGH finding.

When the requirements baseline is itself in the changed-docs set, the gap lens reviews its post-change version while the doc lens covers doc-side defects – do not double-count.

Report `BLOCKED:` only when no declared lens can resolve a required target/baseline (`BLOCKED: mixed has no scope` when `--mode mixed` resolves to no applicable lens), an unsafe external action is required, or publication cannot proceed.

**Gate**: target map, lens set, rules/intent context, and ledger state are explicit.


### 2. Plan Coverage

Before finding issues, create the review coverage plan. This is the recall engine.

For every active lens, list the surfaces that must be attacked:
- FIS/PRD/issue claims, Acceptance Scenarios, Structural Criteria, Work Areas, Expected Outcomes, Non-Goals, and explicit deferrals
- Changed implementation/config/test/doc artifacts and their obvious callers/consumers
- New or changed tests, parsers, validators, release registers, sign-off artifacts, generated artifacts, user-facing copy, locale pairs, fixture data, migrations, workflows, and public APIs
- Trust boundaries and security-trigger surfaces

For each surface, capture:
- `surface`
- `evidence read`
- `positive proof`
- `falsifier attempted` – the negative/edge/path/state that would prove the artifact does not actually satisfy the claim
- `result` – `covered`, `finding`, or `not reviewed`

`not reviewed` on an in-scope primary surface becomes a finding unless a cited Intent/Non-Goal/deferral removes it from scope.

**Test-contract falsification.** When tests or sign-off artifacts changed, ask for each important assertion: “What bad state would still pass?” Missing malformed-input, extra-item, duplicate, stale-copy, locale-pair, timezone, fallback, row-closure, or boundary probes are findings when they threaten the story intent.

Use fan-out when the surface is semantically wide, not just when the diff is large: FIS with multiple Work Areas, story risk high/medium with several proof surfaces, sign-off/test-contract changes, or the existing size/package thresholds. `--no-fanout` still forces inline review and must be reported.

**Gate**: coverage plan exists and high-risk surfaces have falsifiers assigned.


### 3. Run Find-Passes

Load only the references required by the resolved lenses:

| Lens | Reference |
|---|---|
| code | `references/lens-code.md` |
| doc | `references/lens-doc.md` |
| gap | `references/lens-gap.md` |
| security | `references/lens-security.md` |

Run:
- Guardrails pass once against diff-verifiable Project Rules Context; each violation cites source file/section and contributes to `Guardrails Coverage: N checked, M findings`.
- Each selected lens against the coverage plan.
- Critic pass for every selected lens; under `--council`, use `references/council-mode.md`.
- Refactor-invariants pass when deletion/rename/relocation/cache/codegen/schema/parameter-threading triggers fire.
- Fan-out partition reviews and one boundary pass when triggered.

For chains, dispatch leaf find-passes as siblings from the orchestrator. Do not wrap lenses in per-lens orchestrators and do not run lens-by-lens sequentially unless sub-agents are unavailable.

**Gate**: all declared lens, guardrail, critic, fan-out/boundary, and council passes completed or are explicitly marked unavailable with impact.


### 4. Filter, Classify, Route

Apply `${CLAUDE_PLUGIN_ROOT}/references/findings-filter-templates.md` only after collection. Full filter runs when any Critical finding exists or total findings >5; otherwise perform the same falsifier-based inline check.

Every accepted finding must carry:
- `Reviewer`, `Severity`, `Confidence`, `Location`, `Scope relation`
- `Finding`, `Threatened assumption or invariant`, `Evidence`, `Impact`, `Suggested fix`, `Verification needed`
- `Class: code-defect | spec-stale | design-changed | ambiguous-intent`
- `Routing: Fix | Note` with one-line rationale

Class rules:
- `code-defect`: artifact is wrong relative to Intent/requirements and the correction is clear.
- `spec-stale`: requirements trail the implementation/decision now in force.
- `design-changed`: coherent design pivot that needs explicit reconciliation.
- `ambiguous-intent`: missing decision prevents knowing whether code or spec is wrong.

Route to `Fix` only when confidence ≥75, scope relation is `primary`, class is `code-defect`, the fix is mechanical/bounded/uniquely determined, and it does not expand past Intent. Everything else routes `Note`. Severity affects verdict, not auto-apply eligibility. Security fixes must be mechanically secure, not merely plausible.

Intent anchor routing:

| Anchor | Decision |
|---|---|
| Non-Goal or deferral | Dismiss or demote to `Note`; cite the anchor. |
| Stated Expected Outcome | `Fix`-eligible regardless of severity heuristics when other Fix criteria hold. |
| No Intent Context | Route on severity/confidence/scope; ties default to `Note`. |

When a reconciliation ledger is loaded, match findings by `${CLAUDE_PLUGIN_ROOT}/references/reconciliation-ledger.md`; tracked reconciliation-class findings route Note, closed/withdrawn entries stay suppressed unless refuted, and recurring unreconciled drift escalates per the ledger contract.

Emit:
- `CONVERGED` when no new `code-defect` at severity ≥ MEDIUM appeared.
- `Auto-Remediation: PENDING|STALLED|CLEAR` exactly once beside the verdict block, per `references/review-verdict.md`.

**Gate**: every accepted finding is structured, classed, routed, and scored.


### 5. Write One Report

Use `${CLAUDE_PLUGIN_ROOT}/references/review-report-location.md` for path resolution and this suffix/mode table:

| Resolved lens set | Report suffix | Mode token |
|---|---|---|
| `code` | `code-review` | `code` |
| `doc` | `doc-review` | `doc` |
| `gap` | `gap-review` | `gap` |
| `security` | `security-review` | `security` |
| any chain | `mixed-review` | `mixed` |
| single `code`/`security` + `--council` | `council-review` | `council` |

Report content:
- Scope, `Review mode used:`, `Resolved chain:` when mixed, Intent Context, Reconciliation Ledger
- `Coverage Matrix` with the surface/evidence/proof/falsifier/result rows, compact but specific
- Guardrails Coverage and findings
- Cross-Lens Synthesis when chain + `--council`
- Per-lens findings by severity with Class/Routing
- Verdict/readiness from `references/review-verdict.md`; gap reports preserve the canonical `## Verdict` table exactly
- CONVERGED, Auto-Remediation, ledger annotations, verification evidence, readiness/counts

For `--inline-findings`, return the same structured content inline. For `--to-pr`, post the written report via `gh pr comment <number> --body-file <report-path>`.

**Gate**: one consolidated parseable result delivered.


### 6. Optional Follow-Through

`--fix`: invoke the `andthen:remediate-findings` skill with `<report-path>` and `--auto` when set. Skip only for a clean report, single-lens gap PASS with no findings, or all findings routed Note; state the reason.

`--visual`: invoke the `andthen:visualize` skill with `<report-path>` after report write and any publication/remediation.

After the report (any lens), if findings expose a recurring trap – a defect class repeated across findings, or a repeat of an existing `Learnings` entry – append it via the `andthen:ops` skill (`update-learnings add`).

On completion, print the report path relative to the project root. When `AUTO_MODE=true`, skip all follow-up offers and print only the verdict/readiness, the **absolute** report path, and the remediation result when `--fix` ran. Otherwise offer remediation for actionable findings, a narrower rerun when coverage gaps remain, or visualization when the report is large.
