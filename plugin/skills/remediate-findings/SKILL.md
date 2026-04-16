---
description: Use when the user wants review findings or review comments addressed. Implements actionable findings from a review report with minimal, guideline-aligned fixes across code, specs, plans, PRDs, and documentation, then re-validates the result and updates plan/FIS status. Trigger on 'address these review findings', 'fix review comments', 'remediate findings'.
user-invocable: true
argument-hint: <review-report-path | report URL | GitHub issue/comment URL>
---

# Remediate Findings

Implement validated findings from a review report. The goal is to clear real issues with the smallest safe change set across implementation and document artifacts, avoid over-engineering, re-run the right verification, and update workflow state when the reviewed work is now complete.


## VARIABLES

REPORT_SOURCE: $ARGUMENTS


## USAGE

```bash
/remediate-findings docs/specs/feature/feature-gap-review-codex-2026-04-10.md
/remediate-findings https://example.com/reviews/feature-gap-review.md
/remediate-findings https://github.com/org/repo/wiki/feature-gap-review
/remediate-findings https://github.com/org/repo/issues/123
/remediate-findings https://github.com/org/repo/pull/456#issuecomment-789
```


## INSTRUCTIONS

- Require `REPORT_SOURCE`. Stop if missing.
- Treat the review report as an input contract, not unquestionable truth. Re-validate findings against the current workspace before editing artifacts.
- Fix validated findings with the smallest coherent patch set that resolves them.
- Avoid scope creep. Do not "clean up nearby code" or rewrite nearby docs unless it is required to resolve a finding or prevent a regression.
- Prefer explicit, local fixes over broad rewrites, reorganizations, helpers, or framework layers.
- If external documentation is needed, use the `andthen:documentation-lookup` agent.
- Invoke the `andthen:ops` skill for deterministic plan/FIS/STATE updates instead of hand-editing those artifacts.


## GOTCHAS

- Fixing stale findings that were already resolved
- Treating every suggestion as mandatory when it does not affect correctness, maintainability, or PASS/FAIL
- Expanding a narrow remediation into a broad refactor
- Marking plan or FIS artifacts done before re-validation proves the findings are actually addressed
- Editing the wrong artifact when the real issue belongs in a spec, plan, PRD, or user-facing document
- Forcing a speculative doc rewrite when the real issue is an unresolved product or requirements decision that needs escalation


## WORKFLOW

### Phase 1: Resolve Report and Targets

1. Resolve `REPORT_SOURCE`:
   - Local report path or direct raw report URL: read the report content directly
   - GitHub issue URL or PR comment URL: follow `${CLAUDE_PLUGIN_ROOT}/references/resolve-github-input.md`.
     Compatible types: `review`, `gap-review`, `code-review`, `architecture-review`, `doc-review`, `council-review` — extract the embedded primary report and any companion files; use the typed metadata to recover `report_path`, `plan_path`, `fis_path`, `story_ids`, `requirements_baseline`, and `implementation_targets`. Redirects: any non-review typed artifact → stop with invalid-input error. Untyped: fall through to step 3 validation below.
2. Extract:
   - Review type (`review-gap`, `review-code`, `review-doc`, or other)
   - Report verdict (PASS/FAIL) when present
   - Findings, severity, remediation recommendations, and reviewed scope
   - Referenced implementation targets, requirements baseline, FIS path, `plan.md`, and story IDs when available
3. If the input URL does not contain the actual review report content or a valid typed GitHub review artifact, stop with an invalid-input error that states the report itself is required. Do not guess from an issue or PR shell page.
4. If the report has no actionable findings, stop and return that there are no actionable findings.

**Gate**: Actionable findings and the remediation target are explicit


### Phase 2: Re-Validate Findings

For each finding:
- Check whether it is still true in the current workspace
- Classify it as `valid`, `already fixed`, `superseded`, or `unclear`
- Classify the remediation surface as `implementation`, `document`, `workflow-artifact`, or `mixed`
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
- Choose the target artifact that actually owns the defect: code/config/tests for implementation problems, specs/plans/PRDs for requirements or design defects, and product/user docs for explanation, usage, or reference defects
- If a finding reveals an unresolved product decision, missing requirement, or ambiguous source of truth rather than a defect in the reviewed artifacts, stop and escalate instead of forcing a speculative edit
- Use parallel sub-agents only for independent fix groups

**Gate**: Minimal remediation plan is clear and bounded


### Phase 4: Implement and Re-Validate

1. Implement fixes by logical area and artifact type.
2. Add or update tests when an implementation finding requires proof-of-work.
3. Run targeted verification after each fix group:
   - Implementation fixes: tests, linting, type checks, builds
   - Document fixes: verify terminology, cross-references, linked paths, commands/examples, consistency with source of truth
   - Workflow artifact fixes: verify templates, status semantics, cross-document consistency
4. Run `andthen:quick-review` on the touched scope. This replaces the heavyweight re-review sub-agents – one lightweight pass is sufficient for targeted fixes.
5. **Findings re-check**: Walk through every finding from the original report and verify resolution against the current workspace. For each finding, state: `RESOLVED` (with evidence), `PARTIALLY RESOLVED` (what remains), `UNRESOLVED` (why), or `DEFERRED` (per severity policy, with justification). This is the primary close-the-loop validation.
6. If both implementation and document artifacts changed, verify consistency across them.
7. If Critical/High findings remain after one remediation pass, escalate to the user rather than looping.

**Gate**: Every Critical/High finding is RESOLVED with evidence, Medium/Low findings are RESOLVED or DEFERRED with justification, quick-review on touched scope is clean, no new regressions


### Phase 5: Update Workflow State

The findings re-check and quick-review results from Phase 4 are the evidence needed to update state. When all required findings are resolved and verification is clean, update state now.

If the report is tied to a story or FIS and remediation passed validation:
- Use `andthen:ops update-fis {fis_path} all` when the FIS work is substantively complete and evidence exists
- Use `andthen:ops update-plan {plan_path} {story_id} Done` only after confirming plan acceptance criteria are satisfied
- Update the `State` document (see **Project Document Index**) through the `andthen:ops` skill when it exists and the story is now complete
- Re-read the updated artifacts to verify the status changes applied

If the remediation only fixes document artifacts:
- Update only the workflow artifacts justified by the document remediation
- Do not mark implementation complete unless the implementation acceptance criteria are also satisfied

If the report is a full-plan or workspace-wide review:
- Update only the status artifacts that can be justified from the completed remediation
- Do not mark individual stories done unless their acceptance criteria are clearly satisfied

**Gate**: Status artifacts reflect the validated post-remediation state


## COMPLETION

Report:
- Findings re-check table (each finding → RESOLVED / PARTIALLY RESOLVED / UNRESOLVED with evidence)
- Findings intentionally left open and why
- Verification results (tests, lints, builds, quick-review)
- Which workflow artifacts were updated
