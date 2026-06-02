# Lens: Gap Analysis

Rubric for comparing a current implementation against its requirements baseline (spec, PRD, plan, issue, FIS, or other source of truth) and producing remediation-focused output with a PASS/FAIL verdict. Load this reference when running `andthen:review --mode gap`.

Default target is the implementation, not the requirements doc – but not absolutely. When coherent, tested code contradicts the FIS Intent, Expected Outcomes, or an ADR-backed decision, do not assume which party is wrong: classify the finding (`code-defect | design-changed | spec-stale | ambiguous-intent`, defined in §4 Spec/design drift) rather than reflexively routing to code remediation.

## Contents
- Scope · §0 Resolve Review Target · §1 Compile Requirements · §2 Inspect Implementation
- §3 Quality Review · §4 Gap Analysis · §5 Critic Sub-Lens (behavioral dry-run)
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


## 3. Quality Review

Run project checks and gather evidence directly – do not delegate to the code lens. When an upstream step has already run code review (e.g. a `plan` pipeline's per-story `quick-review`), reuse that evidence; otherwise gather it here:
- Run applicable build/package checks
- Run applicable test suites
- Run static analysis, linting, type checks
- **Stub scan**: grep changed files for incomplete-implementation markers (`TODO`, `FIXME`, `XXX`, `NotImplementedError`, language-appropriate `pass`/empty-body/`throw.*not implemented` patterns). Triage intentional vs. forgotten.
- **Wiring check**: for each new file, confirm at least one other file imports or references it (language-appropriate import/require/include grep on basename or module path). When the diff matches a [`refactor-invariants.md`](refactor-invariants.md) trigger (deletion, rename, lifecycle relocation, cache introduction, codegen, schema migration, parameter threading), expand this check into the full invariant pass – the existing wiring check is the deletion-completeness primitive that the refactor-invariants rubric generalizes.
- Check substance and wiring using `verification-patterns.md`
- Run available security tooling (e.g. `${CLAUDE_SKILL_DIR}/scripts/run-security-scan.sh <path>`) when applicable

Focus on requirements-vs-implementation alignment – the unique value of this lens.


## 4. Gap Analysis

Compare requirements to implementation; record gaps per the categories below – each targets a distinct failure mode, so skipping one silently narrows the review. Note affected file(s) and the violated requirement per finding.

- **Functionality gaps** – missing or incomplete features, unfulfilled acceptance criteria, absent error handling, unhandled edge cases, weak input validation, missing user-facing feedback for failure paths.

- **Forward-coverage gaps** _(FIS baselines)_ – Work Areas declared in the FIS that lack any corresponding task, scenario proof, or implementation evidence in the changed files. Distinct from missing-test or missing-feature gaps: a Work Area declares a surface that must be exercised; if nothing proves it was touched, the scope was claimed but not delivered.

- **Integration gaps** – missing or broken integration points (API endpoints, database migrations, configuration, feature flags, jobs, workers, CLI entry points). Incomplete data flows between modules, broken or stale dependencies, contract mismatches at module boundaries, missing wiring for new components into the system.

- **Requirement mismatches** – behavior or logic that does not match what the requirements specify. Incorrect defaults, inverted conditions, misinterpreted acceptance criteria. Unmet non-functional requirements: performance, security, accessibility, internationalization, observability, compatibility.

- **Spec/design drift** – implementation is coherent and tested but contradicts the FIS Intent sentence, tagged Expected Outcomes, or recorded design decision. Classify `design-changed` (deliberate pivot), `spec-stale` (requirements simply trail the code), or `ambiguous-intent` (artifact cannot say which party is wrong). These require a human reconcile decision, not blind code remediation.

- **Consistency gaps** – deviations from existing codebase patterns, conventions, and architecture. Documentation gaps (README, inline docs, user-facing copy). Test coverage gaps at the levels the project expects (unit, integration, end-to-end).

- **Domain language gaps** – terminology drift between requirements and implementation: the same concept named differently, terms leaking across bounded contexts, or new domain concepts introduced without glossary entries. _Skip when no `Ubiquitous Language` document exists (see **Project Document Index**)._

- **Holistic sanity check** – zoom out and ask whether the implementation makes sense end-to-end. Does it actually achieve the user-facing outcome, not just the technical checklist? Any hidden assumptions, tech debt, or architectural drift introduced? Would a reasonable user or operator be surprised by how it behaves?

- **Verification depth** – fold the §3 stub-scan / wiring-check / passing-command evidence into the relevant category above: a stub or unwired component that violates a requirement is a Functionality or Integration gap, not just a quality note.


## 5. Critic Sub-Lens (Always On): Behavioral Dry-Run Walkthrough

Use `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md`, `${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md`, and `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` for the posture of this walkthrough. The rubric below is the canonical gap-review Critic work.

Dispatch per `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md` § Sub-agent dispatch (prefer the `review-critic` agent with a read-first task prompt for the three calibration files; else a generic fresh-context sub-agent; inline fallback requires a `Critic Coverage` note).

Methodically simulate how the implementation actually runs against each requirement, one path at a time. This surfaces issues that mechanical file-vs-spec comparison misses: latent state bugs, incorrect logic, fragile assumptions, missing defensive behavior, and requirements filled in by guessing.

For each significant requirement, feature flow, or user-visible behavior the implementation claims to satisfy, perform the following passes. (Add an explicit **Behavioral** subcategory to Step 4 if needed; routing is in *Record and route* below.)

### Trace execution

- Identify the entry point that satisfies the requirement: handler, command, route, event, scheduled job, CLI, migration, UI action.
- Walk the control flow step by step. Mentally execute each branch – do not jump to the happy path.
- Track the shape, source, and trust level of data at each step (user input, external service response, database row, derived state).

### Check conditions and invariants

- **Preconditions** – guaranteed by the caller, enforced on entry, or silently assumed?
- **Postconditions** – delivered on every path, including early returns and exceptions?
- **Invariants** (transactional consistency, ordering, uniqueness, referential integrity, UI state) – any path that could violate them?
- **Idempotency and re-entry** – safe to retry, replay, or run concurrently if the requirement implies that?

### Stress the unhappy paths

- What does each external call do when it fails, times out, returns an error, returns partial or malformed data, or returns stale data?
- Which errors are caught, which are propagated, which are swallowed? Are failures observable (logs, metrics, traces, user-facing feedback)?
- What happens under concurrent access, retries, partial writes, network partitions, duplicate events, out-of-order delivery?
- What about empty, null, zero, negative, oversized, Unicode, mixed-case, or otherwise-boundary inputs?
- What is the rollback / cleanup story when an operation fails halfway?

### Test the assumptions

- Which behaviors depend on an assumption about upstream, downstream, or environment state that the requirements did not pin down? List the assumption explicitly.
- Where did the implementer fill a requirements gap with a guess? Is the guess defensible? Is it documented (comment, ADR, commit message) or invisible?
- Is there logic that only works because of an unrelated implementation detail elsewhere (implicit coupling, load-bearing side effects)?
- Are there places where the requirements themselves are ambiguous or contradictory – and the implementation picked one reading without flagging it?

### Sanity-check the design

- For each `[x]` FIS Acceptance Scenario, does the implementation satisfy the tagged `[OC<NN>]` outcome and the Intent sentence, not merely the literal **Then** clause? A scenario satisfiable by an implementation that defeats the Intent is a finding regardless of checkbox state.
- Are there operations that look correct locally but compose incorrectly (e.g. correct individual queries that together violate an invariant)?
- Are failure modes survivable – does a single external dependency outage degrade gracefully or cascade?
- Could the same requirement be met with meaningfully less code, fewer abstractions, or fewer failure surfaces? If so, the complexity itself is a finding.

### Record and route

Every concern from the walkthrough is a finding. Each finding must carry: location, class (`code-defect | spec-stale | design-changed | ambiguous-intent`), the requirement or invariant it threatens, the path or input that triggers it, and the observable impact. Merge into the Step 4 categories so they are scored and filtered alongside the mechanical gap findings. When a `design-changed` finding fires and no ADR records the decision, emit a companion finding routing to the `andthen:architecture` skill in `--mode trade-off` to create the missing ADR before spec amendment.


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

Reproduce the canonical `## Verdict` summary block from [`review-verdict.md`](review-verdict.md) (§ Gap mode) verbatim in the Executive Summary. It is a byte-level compatibility contract parsed by `andthen:exec-plan` / `andthen:remediate-findings` – do not re-label, re-phrase, or re-order its columns.


## Report Sections

```markdown
## Executive Summary
overview, verdict table, high-level findings, Findings Filter stats

## Requirements Analysis

## Implementation Overview

## Quality Review Findings

## Over-Engineering Analysis

## Gap Analysis Results

## Behavioral Dry-Run Findings
(issues surfaced by the Step 5 walkthrough that are not already covered above – logic flaws, unstated assumptions, unhappy-path and edge-case gaps, fragile composition)

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
