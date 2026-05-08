# Lens: Gap Analysis

Rubric for comparing a current implementation against its requirements baseline (spec, PRD, plan, issue, FIS, or other source of truth) and producing remediation-focused output with a PASS/FAIL verdict. Load this reference when running `andthen:review --mode gap`.

The target is always the implementation, not the requirements document itself.


## Scope

Two inputs must be explicit before the lens can run:
1. **Requirements baseline** — docs, issues, comments, or source-of-truth files that define expected behavior
2. **Implementation target** — repo(s), package(s), directories, or changed files that contain the implementation

Default to **workspace-wide resolution** when requirements and implementation may live in different repos.


## 0. Resolve Review Target

### Requirements Discovery

When the caller provides a directory path or a plan file, discover the full requirements baseline rather than treating the single input as the only source.

**Directory path** — search the directory (and its parent, for cases where a subdirectory like `fis/` is given) for:
- `plan.json` — the typed implementation plan (canonical; see [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md))
- `prd.md` — the product requirements document
- FIS/spec files (`s01-*.md`, `s02-*.md`, etc.) co-located with the plan
- Also check the Project Document Index in the project's root agent instruction file (`CLAUDE.md` / `AGENTS.md`) for additional pointers

**Plan file** — read the plan and extract related requirements:
- Look for a sibling `prd.md` in the same directory
- Read `stories[]` from `plan.json`; collect each story's `fis` value (skip entries where `fis` is `null`)
- Read all referenced FIS files that exist on disk

**Any other input** (specific file, issue, URL) — use as-is without further discovery.

### State

- **Requirements baselines**: all discovered files, issues, PRDs, plans, or URLs that define expected behavior
- **Implementation target**: repo(s), package(s), directories, or changed files that contain the implementation
- **Mapping rationale**: why those paths are the right implementation target

If no implementation target exists yet, stop and report that gap analysis cannot run.

**Gate**: Requirements sources and implementation target are explicit


## 1. Compile Requirements

Gather the requirements baseline from docs, issues, comments, and caller context. Build a concise view of expected behavior, success criteria, constraints, and non-functional requirements. Verify external technical claims against authoritative docs when needed.


## 2. Inspect Current Implementation

Map the current implementation state:
- Identify relevant changed files and implementation inventory
- Understand codebase structure, affected components, and existing patterns
- Stop if there is still nothing implemented to compare


## 3. Quality Review

Run project checks and gather evidence directly — do not delegate to the code lens. When an upstream step has already run code review (e.g. a `plan` pipeline's per-story `quick-review`), reuse that evidence; otherwise gather it here:
- Run applicable build/package checks
- Run applicable test suites
- Run static analysis, linting, type checks
- **Stub scan**: grep changed files for incomplete-implementation markers (`TODO`, `FIXME`, `XXX`, `NotImplementedError`, language-appropriate `pass`/empty-body/`throw.*not implemented` patterns). Triage intentional vs. forgotten.
- **Wiring check**: for each new file, confirm at least one other file imports or references it (language-appropriate import/require/include grep on basename or module path).
- Check substance and wiring using `verification-patterns.md`
- Run available security tooling (e.g. `${CLAUDE_SKILL_DIR}/scripts/run-security-scan.sh <path>`) when applicable

Focus on requirements-vs-implementation alignment — the unique value of this lens.


## 4. Gap Analysis

Compare requirements to the implementation and record gaps in the categories below. Each category targets a distinct failure mode — skipping categories silently narrows the review. For every finding, note the affected file(s) and the specific requirement or expectation it violates.

- **Functionality gaps** — missing or incomplete features, unfulfilled acceptance criteria, absent error handling, unhandled edge cases, weak input validation, missing user-facing feedback for failure paths.

- **Integration gaps** — missing or broken integration points (API endpoints, database migrations, configuration, feature flags, jobs, workers, CLI entry points). Incomplete data flows between modules, broken or stale dependencies, contract mismatches at module boundaries, missing wiring for new components into the system.

- **Requirement mismatches** — behavior or logic that does not match what the requirements specify. Incorrect defaults, inverted conditions, misinterpreted acceptance criteria. Unmet non-functional requirements: performance, security, accessibility, internationalization, observability, compatibility.

- **Consistency gaps** — deviations from existing codebase patterns, conventions, and architecture. Documentation gaps (README, inline docs, user-facing copy). Test coverage gaps at the levels the project expects (unit, integration, end-to-end).

- **Domain language gaps** — terminology drift between requirements and implementation: the same concept named differently, terms leaking across bounded contexts, or new domain concepts introduced without glossary entries. _Skip when no `Ubiquitous Language` document exists (see **Project Document Index**)._

- **Holistic sanity check** — zoom out and ask whether the implementation makes sense end-to-end. Does it actually achieve the user-facing outcome, not just the technical checklist? Any hidden assumptions, tech debt, or architectural drift introduced? Would a reasonable user or operator be surprised by how it behaves?

- **Verification depth — substance and wiring** — beyond "does the file exist," check:
  - Are implementations substantive? (No stubs, placeholders, silently-empty handlers, `pass`, `TODO`, `NotImplementedError`.)
  - Are new components wired into the system? (Imported, routed, called, rendered, migrated, registered.)
  - Do verification commands actually pass? (Build, tests, type check, lint.)
  - Cross-reference `verification-patterns.md` for the substance/wiring rubric.


## 5. Critic Sub-Lens (Always On): Behavioral Dry-Run Walkthrough

Use `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md` and `${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md` for the posture of this walkthrough. The rubric below is the canonical gap-review Critic work.

Methodically simulate how the implementation actually runs against each requirement, one path at a time. This surfaces issues that mechanical file-vs-spec comparison misses: latent state bugs, incorrect logic, fragile assumptions, missing defensive behavior, and requirements filled in by guessing.

Walk through the work; do not skim it. For each significant requirement, feature flow, or user-visible behavior the implementation claims to satisfy, perform the following passes and record every concern as a finding. Feed those findings back into the Step 4 categories (or add an explicit **Behavioral** subcategory) before running the Findings Filter.

### Trace execution

- Identify the entry point that satisfies the requirement: handler, command, route, event, scheduled job, CLI, migration, UI action.
- Walk the control flow step by step. Mentally execute each branch — do not jump to the happy path.
- Track the shape, source, and trust level of data at each step (user input, external service response, database row, derived state).

### Check conditions and invariants

- **Preconditions** — what must be true before each function or block runs? Are those conditions guaranteed by the caller, enforced on entry, or silently assumed?
- **Postconditions** — what state or output does the code promise after it runs? Is that promise delivered on every path, including early returns and exceptions?
- **Invariants** — what must remain true throughout the operation (transactional consistency, ordering, uniqueness, referential integrity, UI state)? Any path that could violate them?
- **Idempotency and re-entry** — is it safe to retry, replay, or run concurrently if the requirement implies that?

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
- Are there places where the requirements themselves are ambiguous or contradictory — and the implementation picked one reading without flagging it?

### Sanity-check the design

- Does the end-to-end flow actually achieve the user-facing outcome, or only the technical acceptance checklist?
- Are there operations that look correct locally but compose incorrectly (e.g. correct individual queries that together violate an invariant)?
- Are failure modes survivable — does a single external dependency outage degrade gracefully or cascade?
- Could the same requirement be met with meaningfully less code, fewer abstractions, or fewer failure surfaces? If so, the complexity itself is a finding.

### Record and route

Every concern from the walkthrough is a finding. Each finding must carry: location, the requirement or invariant it threatens, the path or input that triggers it, and the observable impact. Merge into the Step 4 categories so they are scored and filtered alongside the mechanical gap findings.


## FIS Upstream-Context Handling

When a FIS is in scope: treat `Required Context` blocks as the authoritative upstream intent — do not re-read source documents just to reconfirm inlined content. For `Deeper Context` anchors that are load-bearing for a finding, verify the anchor resolves in the source and warn (do not stop) on broken anchors. If a `Required Context` block appears to no longer match the current source, that is a doc-review finding (MEDIUM by default — spec should be re-run against the updated source), not an execution blocker.

**Legacy FIS fallback**: a FIS without `Required Context` / `Deeper Context` sections predates them. Fall back to whatever upstream-reference structures it uses: the old `## References & Constraints` heading and its `### Documentation & References` table (rows typed `file|doc|url|wire`), or prose mentions. Do not flag the absence of these sections as a defect on legacy FIS files.


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

Include this exact summary in the Executive Summary:

```markdown
## Verdict

| Dimension     | Score | Threshold | Status |
|---------------|-------|-----------|--------|
| Functionality | X/10  | >= 7      | PASS/FAIL |
| Completeness  | X/10  | >= 9      | PASS/FAIL |
| Wiring        | X/10  | >= 8      | PASS/FAIL |

**Overall: PASS / FAIL**
```

> **Contract invariance**: The PASS/FAIL verdict table above is a byte-level compatibility contract. Downstream skills (`andthen:exec-plan`, `andthen:remediate-findings`) parse this table directly. Do not re-label, re-phrase, or re-order the columns.


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
(issues surfaced by the Step 5 walkthrough that are not already covered above — logic flaws, unstated assumptions, unhappy-path and edge-case gaps, fragile composition)

## Remediation Plan
Critical / High / Medium / Low, dependencies, sequencing, acceptance criteria

## Appendix
(when needed)
```

If notable recurring traps emerge, append them to an existing learnings file.


## Report Output Conventions

Filename and directory resolve per [`review-report-location.md`](${CLAUDE_PLUGIN_ROOT}/references/review-report-location.md). This lens contributes:
- **`<feature-name>` token**: the feature/baseline name (e.g. `payments`, derived from the spec/FIS/plan path under review)
- **Report suffix**: `gap-review` (canonical source: the `andthen:review` skill's mode table)
- **Target nature**: source-code. The implementation under review is the primary target; the requirements baseline anchors tier 2 (spec directory). Tier-2 "next to target" is disabled for the implementation side — without a resolvable spec directory, current feature directory, or `--output-dir`, the report lands in `<agent-temp>/reviews/`.
