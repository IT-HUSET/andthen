---
description: Implement actionable findings from a review report with minimal, guideline-aligned fixes, re-validation, and plan/FIS status updates. Use after review-gap, review-code, or similar review reports.
user-invocable: true
argument-hint: <review-report-path | report URL>
---

# Remediate Findings

Implement validated findings from a review report. The goal is to clear real issues with the smallest safe change set, avoid over-engineering, re-run the right verification, and update workflow state when the reviewed work is now complete.


## VARIABLES

REPORT_SOURCE: $ARGUMENTS


## USAGE

```bash
/remediate-findings docs/specs/feature/feature-gap-review-codex-2026-04-10.md
/remediate-findings https://example.com/reviews/feature-gap-review.md
/remediate-findings https://github.com/org/repo/wiki/feature-gap-review
```


## INSTRUCTIONS

- Read the Workflow Rules, Guardrails, and relevant project guidelines before starting.
- Make sure `REPORT_SOURCE` is provided; otherwise stop and ask for it.
- Treat the review report as an input contract, not unquestionable truth. Re-validate findings against the current workspace before editing code.
- Fix validated findings with the smallest coherent patch set that resolves them.
- Avoid scope creep. Do not "clean up nearby code" unless it is required to resolve a finding or prevent a regression.
- Prefer explicit, local fixes over new abstractions, helpers, or framework layers.
- If external documentation is needed, use the `andthen:documentation-lookup` agent.
- Invoke the `andthen:ops` skill for deterministic plan/FIS/STATE updates instead of hand-editing those artifacts.


## GOTCHAS

- Fixing stale findings that were already resolved
- Treating every suggestion as mandatory when it does not affect correctness, maintainability, or PASS/FAIL
- Expanding a narrow remediation into a broad refactor
- Marking plan or FIS artifacts done before re-validation proves the findings are actually addressed
- Patching implementation when the real issue is a spec or requirements mismatch that needs escalation


## WORKFLOW

### Phase 1: Resolve Report and Targets

1. Read the review report from the provided path or direct report URL.
2. Extract:
   - Review type (`review-gap`, `review-code`, or other)
   - Report verdict (PASS/FAIL) when present
   - Findings, severity, remediation recommendations, and reviewed scope
   - Referenced implementation targets, requirements baseline, FIS path, `plan.md`, and story IDs when available
3. If the input URL does not contain the actual review report content, stop and ask for the report itself instead of guessing from an issue or PR shell page.
4. If the report has no actionable findings, stop and say so.

**Gate**: Actionable findings and the remediation target are explicit


### Phase 2: Re-Validate Findings

For each finding:
- Check whether it is still true in the current workspace
- Classify it as `valid`, `already fixed`, `superseded`, or `unclear`
- Keep only currently valid findings in scope

Severity policy:
- **Critical / High**: must fix
- **Medium**: fix when it affects requirements, correctness, maintainability, or report PASS/FAIL
- **Low**: fix only when it is cheap, low-risk, or explicitly requested

If all findings are already fixed or superseded, skip to Phase 5 and only update status artifacts when that is now justified.

**Gate**: Remediation scope is bounded to currently valid findings


### Phase 3: Plan Minimal Remediation

- Group findings by affected area to minimize conflicts and repeated verification
- Define the smallest change set that resolves the validated findings
- Favor boring, readable fixes over clever or reusable abstractions
- If a finding points to a requirements or spec defect rather than an implementation defect, stop and escalate instead of forcing a code-only fix
- Use parallel sub-agents only for independent fix groups

**Gate**: Minimal remediation plan is clear and bounded


### Phase 4: Implement and Re-Validate

1. Implement fixes by logical area.
2. Add or update tests when a finding requires proof-of-work.
3. Run targeted verification after each fix group.
4. Run final validation in parallel when supported:
   - Tests
   - Linting and type checks
   - Visual validation when UI changed
5. **Findings re-check**: Walk through every finding from the original report and verify resolution against the current workspace. For each finding, state one of: `RESOLVED` (with evidence), `PARTIALLY RESOLVED` (what remains), `UNRESOLVED` (why), or `DEFERRED` (intentionally left open per severity policy, with justification). This is the primary close-the-loop validation — it proves each finding was addressed without the cost of a full re-review.
6. Invoke the `andthen:review-code` skill on the touched scope to catch regressions introduced by the fixes.
7. Repeat the remediation loop until all required findings are resolved or explicitly deferred, or escalate after 2 cycles.

**Gate**: Every Critical/High finding is RESOLVED with evidence, Medium/Low findings are RESOLVED or DEFERRED with justification, review-code on touched scope is clean, and no new regressions are introduced


### Phase 5: Update Workflow State

The findings re-check and review-code results from Phase 4 are the evidence needed to update state. When all required findings are resolved and verification is clean, update state now — do not defer to "a future run" merely because the originating review was not re-run.

If the report is tied to a story or FIS and remediation passed validation:
- Use `andthen:ops update-fis {fis_path} all` when the FIS work is substantively complete and evidence exists
- Use `andthen:ops update-plan {plan_path} {story_id} Done` only after confirming plan acceptance criteria are satisfied
- Update `STATE.md` through the `andthen:ops` skill when it exists and the story is now complete
- Re-read the updated artifacts to verify the status changes applied

If the report is a full-plan or workspace-wide review:
- Update only the status artifacts that can be justified from the completed remediation
- Do not mark individual stories done unless their acceptance criteria are clearly satisfied

**Gate**: Status artifacts reflect the validated post-remediation state


## COMPLETION

Report:
- Findings re-check table (each finding → RESOLVED / PARTIALLY RESOLVED / UNRESOLVED with evidence)
- Findings intentionally left open and why
- Verification results (tests, lints, review-code)
- Which workflow artifacts were updated
