# Lens: Gap Analysis

Rubric for comparing a current implementation against its requirements baseline (spec, PRD, plan, issue, FIS, or other source of truth) and producing remediation-focused output with a PASS/FAIL verdict. Load this reference when running the `andthen:review` skill with `--mode gap`.

Default target is the implementation, not the requirements doc – but not absolutely. When coherent, tested code contradicts the FIS Intent, Expected Outcomes, or an ADR-backed decision, do not assume which party is wrong: classify the finding (`code-defect | design-changed | spec-stale | ambiguous-intent`, defined in §4 Spec/design drift) rather than reflexively routing to code remediation.

## Contents
- Scope · §0 Resolve Review Target · §1 Compile Requirements · §2 Inspect Implementation
- §3 Coverage Matrix · §4 Gap Finding Pass · §5 Critic Sub-Lens
- FIS Upstream-Context Handling · §6 Findings Filter · Calibration · Large-Diff Fan-Out
- §7 Dimensional Scoring & Verdict · Report Sections · Report Output Conventions


## Scope

Two inputs must be explicit before the lens can run:
1. **Requirements baseline** – docs, issues, comments, or source-of-truth files that define expected behavior
2. **Implementation target** – repo(s), package(s), directories, or changed files that contain the implementation

Default to **workspace-wide resolution** when requirements and implementation may live in different repos.


## 0. Resolve Review Target

### Requirements Discovery

When the caller provides a directory path or a plan file, discover the full requirements baseline rather than treating the single input as the only source.

**Directory path** – search the directory (and its parent, for cases where a subdirectory like `fis/` is given) for:
- `plan.json` – the typed implementation plan (canonical; see [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md))
- `prd.md` – the product requirements document
- FIS/spec files (`s01-*.md`, `s02-*.md`, etc.) co-located with the plan
- Also check the Project Document Index in the project's root agent instruction file (`CLAUDE.md` / `AGENTS.md`) for additional pointers

**Plan file** – read the plan and extract related requirements:
- Look for a sibling `prd.md` in the same directory
- Read `stories[]` from `plan.json`; collect each story's `fis` value (skip entries where `fis` is `null`)
- Read all referenced FIS files that exist on disk

**Any other input** (specific file, issue, URL) – use as-is without further discovery.

### State

- **Requirements baselines**: all discovered files, issues, PRDs, plans, or URLs that define expected behavior
- **Implementation target**: repo(s), package(s), directories, or changed files that contain the implementation
- **Mapping rationale**: why those paths are the right implementation target

If no implementation target exists yet, stop and report that gap analysis cannot run.

**Gate**: Requirements sources and implementation target are explicit


## 1. Compile Requirements

Gather the requirements baseline from docs, issues, comments, and caller context. Build a concise view of expected behavior, acceptance criteria, constraints, and non-functional requirements. Verify external technical claims against authoritative docs when needed.

### FIS baseline (when a FIS is in scope)

When the requirements baseline includes a FIS, compile the three proof surfaces by their distinct roles:

- **Acceptance Scenarios** as behavioral requirements – each canonical `- [ ] **S<NN> [OC<NN>(,OC<NN>)*] [TI<NN>(,TI<NN>)*] <description>**` checkbox is one behavioral requirement; the nested Given/When/Then is the contract. Canonical shape: see [`fis-authoring-guidelines.md`](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md#acceptance-scenarios-and-proof-of-work). A concrete instance reads like `- [ ] **S01 [OC01] [TI01,TI03] Happy path – user can export filtered results**`.
- **Structural Criteria** as non-behavioral proof requirements – each checkbox names a verifiable structural property that must hold (e.g. "existing tests pass", "API contract unchanged"). These are proved by task Verify lines, not scenarios.
- **Work Areas** as forward-coverage anchors – each bullet names a component, file, or surface that must be covered by at least one task or scenario. A Work Area with no implementing task, scenario, or implementation evidence is a gap (see Forward-coverage gaps in Step 4).

Where the lens elsewhere refers to "acceptance criteria" generically, those are the Acceptance Scenarios above when the baseline is a FIS. Generic language continues to apply for non-FIS baselines (PRDs, issues, ad-hoc requirements).


## 2. Inspect Current Implementation

Map the current implementation state:
- Identify relevant changed files and implementation inventory
- Understand codebase structure, affected components, and existing patterns
- Stop if there is still nothing implemented to compare


## 3. Coverage Matrix

The gap lens succeeds by proving coverage, not by summarizing requirements. Build a compact matrix before judging readiness:

| surface | evidence read | positive proof | falsifier attempted | result |
|---|---|---|---|---|

Rows must cover every primary Acceptance Scenario, Structural Criterion, Work Area, Expected Outcome, changed proof artifact, and changed user-facing/data surface. `not reviewed` on a primary row is a finding unless Intent Context explicitly makes it a Non-Goal or defers it.

Use the matrix to force negative review. For each row, ask what bad state could still pass: malformed input, omitted locale sibling, extra/duplicate item, stale copy, wrong timezone, wrong fallback root, missing row-closure path, unreferenced component, failing dependency, or edge case the requirement implies. A claimed test or register proof that lacks the relevant falsifier is itself a gap.

Run or reuse verification evidence that strengthens the matrix: build/package checks, tests, lint/types, stub scan, wiring check, `verification-patterns.md`, refactor-invariants when triggered, and security tooling when applicable. Fold failed or skipped load-bearing checks into findings.


## 4. Gap Finding Pass

Compare the matrix to the implementation and record gaps by failure mode:

- **Functionality** – required behavior missing, incomplete, or wrong; edge/failure path not handled.
- **Forward coverage** – a FIS Work Area has no task, scenario proof, implementation evidence, or matrix row.
- **Integration/wiring** – component exists but is not connected end-to-end, or data contracts disagree.
- **Requirement mismatch** – implementation/test/docs prove a different behavior than Intent, Expected Outcomes, or acceptance text.
- **Spec/design drift** – coherent implementation contradicts FIS/ADR intent; classify `design-changed`, `spec-stale`, or `ambiguous-intent` rather than forcing code remediation.
- **Consistency/domain language** – changed artifacts drift from project patterns, architecture, terminology, locale pairs, or user-facing copy requirements.
- **Verification depth** – tests/checks pass but do not fail for the bad state the requirement exists to prevent.


## 5. Critic Sub-Lens (Always On)

Use `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md`, `${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md`, and `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` for the posture of this walkthrough. The rubric below is the canonical gap-review Critic work.

Dispatch per `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md` § Sub-agent dispatch (prefer the `review-critic` agent with a read-first task prompt for the three calibration files; else a generic fresh-context sub-agent; inline fallback requires a `Critic Coverage` note).

Use the Critic to attack the matrix, not to add a second checklist. Walk concrete requirement paths end-to-end, including branches, pre/postconditions, invariants, idempotency, retries, malformed/empty/boundary data, partial failures, hidden coupling, and guessed behavior. Every surviving concern becomes a normal gap finding with the threatened requirement/invariant, trigger path, evidence, impact, class, and routing. When a `design-changed` finding fires and no ADR records it, add the companion reconciliation finding for the `andthen:architecture` skill in `--mode trade-off`.


## FIS Upstream-Context Handling

When a FIS is in scope, apply [`fis-context-handling.md`](fis-context-handling.md) (Required/Deeper Context rules, legacy-FIS fallback).


## 6. Findings Filter

> **Findings Filter**: see [`lens-findings-filter.md`](lens-findings-filter.md).

Lens-specific placeholder values:
- **Role**: `Findings Filter reviewing gap analysis findings`
- **Skill calibration**: `code-review-calibration.md`
- **Context block**: `Review target context: {implementation target paths from Step 0}`
- **Questions**: Is this a real gap? Is severity justified? Could there be an existing mitigation? Would a senior engineer flag this?
- **Findings payload**: `{all findings from quality review, gap analysis, and behavioral dry-run walkthrough}`

Apply verdicts before scoring.


## Calibration

Calibrate severity with `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` (universal) and `code-review-calibration.md` (code-specific). Load `${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md` while running the always-on Critic sub-lens; use the code-specific calibration to assign final severity after findings are collected. Use the unified severity scale defined in `review-verdict.md`: CRITICAL / HIGH / MEDIUM / LOW.


## Large-Diff Fan-Out

When the diff exceeds the threshold in [`large-diff-fanout.md`](large-diff-fanout.md) (≥20 files, ≥1000 LOC, 3+ top-level packages, or explicit `--fanout`), partition the diff into 2–5 vertical (feature/concern) slices – never horizontal layers – dispatch one lens sub-agent per partition, then run a boundary pass attacking cross-partition surface. For FIS-driven implementations the FIS Implementation Task IDs (`TI<NN>`) are the canonical slice signal; for plan rollouts use Story IDs. Composes with `--council` and chain dispatch – see [`large-diff-fanout.md`](large-diff-fanout.md) for the partition strategy (and why horizontal slicing hides cross-layer invariants), partition × specialist accounting, and the concurrency model.


## 7. Dimensional Scoring & Verdict

| Dimension | Question | Threshold | Scoring Guide |
|-----------|----------|-----------|---------------|
| **Functionality** | Does it work correctly for specified requirements? | >= 7 | 10: all requirements met, edge cases handled. 7: core happy path works, minor gaps. 4: major functionality broken. 1: does not function. |
| **Completeness** | Are there stubs, TODOs, placeholders, or missing features? | >= 9 | 10: no stubs/TODOs, all features present. 9: trivial TODOs only. 7: non-critical features stubbed. 4: significant features missing. 1: mostly stubs. |
| **Wiring** | Is everything connected end-to-end? | >= 8 | 10: all components wired, verified via build/tests. 8: all critical paths wired, minor integration gaps. 5: some components exist but are not connected. 2: significant unwired code. |

**Verdict rules**
- If any dimension is below threshold: **FAIL**
- If all dimensions meet threshold: **PASS**
- No conditional verdicts

Reproduce the canonical `## Verdict` summary block from [`review-verdict.md`](review-verdict.md) (§ Gap mode) verbatim in the Executive Summary. It is a byte-level compatibility contract parsed by the `andthen:exec-plan` skill / `andthen:remediate-findings` skill – do not re-label, re-phrase, or re-order its columns.


## Report Sections

```markdown
## Executive Summary
overview, verdict table, high-level findings, Findings Filter stats

## Coverage Matrix
surface/evidence/proof/falsifier/result rows

## Gap Analysis Results

## Critic Coverage
(assumptions, requirements paths, unhappy paths, hidden coupling, and incomplete wiring attacked. Required when Critic ran inline.)

## Remediation Plan
Critical / High / Medium / Low, dependencies, sequencing, acceptance criteria

## Appendix
(when needed)
```

If notable recurring traps emerge, append via the `andthen:ops` skill (`update-learnings add` form).


## Report Output Conventions

Filename and directory resolve per [`review-report-location.md`](${CLAUDE_PLUGIN_ROOT}/references/review-report-location.md). This lens contributes:
- **`<feature-name>` token**: the feature/baseline name (e.g. `payments`, derived from the spec/FIS/plan path under review)
- **Report suffix**: `gap-review` (canonical source: the `andthen:review` skill's mode table)
- **Target nature**: source-code. The implementation under review is the primary target; the requirements baseline anchors tier 2 (spec directory). Tier-2 "next to target" is disabled for the implementation side – without a resolvable spec directory, current feature directory, or `--output-dir`, the report lands in `<agent-temp>/reviews/`.
