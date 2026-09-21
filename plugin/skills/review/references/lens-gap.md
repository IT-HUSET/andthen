# Lens: Gap Analysis

Rubric for comparing an implementation against its requirements baseline (FIS, PRD, plan, issue, or other source of truth) and producing remediation-focused output with a PASS/FAIL verdict.

The implementation is the default target, not absolutely: when coherent, tested code contradicts the FIS Intent, Expected Outcomes, or an ADR-backed decision, which party is wrong is the finding's question – classify it (`code-defect | design-changed | spec-stale | ambiguous-intent`, per Spec/design drift below) rather than reflexively routing it to code remediation.


## Baseline Inputs

Two inputs are explicit before the lens runs: the **requirements baseline** and the **implementation target**; a baseline with nothing implemented against it routes as Step 1 says. When the caller gives a directory or a plan file, discover the full baseline rather than treating the one input as the only source:

- **Directory path** – search it and its parent for `plan.json` (canonical; `plan-schema.md`), `prd.md`, and co-located FIS files (`s01-*.md`, …); the Project Document Index may point further.
- **Plan file** – `schemaVersion` `"2"` before shape, else `BLOCKED: unsupported plan.json schemaVersion` and regeneration through the `andthen:plan` skill. The baseline is what the plan's `prd` names (a repo path, not necessarily a sibling) or, with `prd` null, the sources its `stories[].sourceRefs` cite – repo paths, or a tracker item URL resolved through the `Issue Tracker` document (**Project Document Index**); when neither yields a readable source, `BLOCKED: plan names no readable requirements baseline` rather than reviewing the FIS files against themselves. Then each non-null `stories[].fis` and the FIS files present on disk.
- **Any other input** (file, issue, URL) – as-is.

**FIS baseline** – its three proof surfaces in the distinct roles `fis-contract.md` defines: Acceptance Scenarios as behavioral requirements, Structural Criteria as non-behavioral properties proved by task Verify lines, Work Areas as forward-coverage anchors. "Acceptance criteria" here means the Acceptance Scenarios when the baseline is a FIS; the generic reading holds for PRDs, issues, and ad-hoc requirements. Upstream context for a FIS resolves per `fis-contract.md` § Consuming Upstream Context.


## Coverage Matrix

The lens succeeds by proving coverage, not by summarizing requirements: in the spine's matrix, one row per primary Acceptance Scenario, Structural Criterion, Work Area, and Expected Outcome beside the changed proof and user-facing/data surfaces. Re-attack Acceptance Scenarios against their `[OC<NN>]` outcomes and Intent; a claimed test or register proof that lacks the relevant falsifier is itself a gap, and external task progress proves effort, not conformance.

Verification evidence strengthens the matrix – build/package checks, tests, lint/types, the substance and wiring scans in `verification-evidence.md`, refactor-invariants when triggered, security tooling when applicable – run or reused; a failed or skipped load-bearing check is a finding.


## Gap Failure Modes

Record gaps by failure mode:

- **Functionality** – required behavior missing, incomplete, or wrong; edge/failure path not handled.
- **Forward coverage** – a FIS Work Area has no task, scenario proof, implementation evidence, or matrix row.
- **Integration/wiring** – component exists but is not connected end-to-end, or data contracts disagree.
- **Requirement mismatch** – implementation, test, or docs prove a different behavior than Intent, Expected Outcomes, or acceptance text.
- **Spec/design drift** – coherent implementation contradicts FIS/ADR intent; classify `design-changed`, `spec-stale`, or `ambiguous-intent` rather than forcing code remediation. A `design-changed` finding with no ADR recording it gets a companion reconciliation finding for the `andthen:architecture` skill in `--mode trade-off`.
- **Consistency/domain language** – changed artifacts drift from project patterns, architecture, terminology, locale pairs, or user-facing copy requirements.
- **Verification depth** – tests/checks pass but do not fail for the bad state the requirement exists to prevent.

**Critic angles for this lens** – attack the matrix rows as concrete requirement paths walked end-to-end, not a second checklist.


## Findings Filter Values

Role `Findings Filter reviewing gap analysis findings`; questions: is this a real gap, is the severity justified, could an existing mitigation cover it, would a senior engineer flag it?


## Dimensional Scoring

Thresholds and the canonical `## Verdict` block are `review-verdict.md` § Gap mode. Score each dimension:

| Dimension | Scoring Guide |
|-----------|---------------|
| **Functionality** | 10: all requirements met, edge cases handled. 7: core happy path works, minor gaps. 1: does not function. |
| **Completeness** | 10: no stubs/TODOs, all features present. 9: trivial TODOs only. 1: mostly stubs. |
| **Wiring** | 10: all components wired, verified via build/tests. 8: all critical paths wired, minor integration gaps. 2: significant unwired code. |


## Report Sections

```markdown
## Executive Summary
verdict block, overview, high-level findings, Findings Filter stats

## Coverage Matrix

## Gap Analysis Results
findings per the Structured Finding Contract, grouped by failure mode

## Critic Coverage

## Remediation Plan
by severity, with dependencies, sequencing, acceptance criteria
```

The report's `<feature>` token is the baseline's feature name (from the spec, FIS, or plan path); the baseline supplies the spec directory the report may sit in, never beside the implementation.
