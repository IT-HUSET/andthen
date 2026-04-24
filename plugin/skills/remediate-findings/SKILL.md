---
description: Use when the user wants review findings or review comments addressed. Implements actionable findings from a review report with minimal, guideline-aligned fixes across code, specs, plans, PRDs, and documentation, then re-validates the result and updates plan/FIS status. Trigger on 'address these review findings', 'fix review comments', 'remediate findings'.
user-invocable: true
argument-hint: "<review-report-path | report URL> [--auto|--headless]"
---

# Remediate Findings

Implement validated findings from a review report. The goal is to clear real issues with the smallest safe change set across implementation and document artifacts, avoid over-engineering, re-run the right verification, and update workflow state when the reviewed work is now complete.


## VARIABLES

REPORT_SOURCE: $ARGUMENTS (strip any `--auto` / `--headless` tokens before interpreting the remainder as the report path or URL)

### Optional Flags
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Require `REPORT_SOURCE`. Stop if missing.
- Treat the review report as an input contract, not unquestionable truth. Re-validate findings against the current workspace before editing artifacts.
- Fix validated findings with the smallest coherent patch set that resolves them.
- Avoid scope creep. Do not "clean up nearby code" or rewrite nearby docs unless it is required to resolve a finding or prevent a regression.
- Prefer explicit, local fixes over broad rewrites, reorganizations, helpers, or framework layers.
- If external documentation is needed, use the `andthen:documentation-lookup` agent.
- Invoke the `andthen:ops` skill for deterministic plan/FIS/STATE updates instead of hand-editing those artifacts.
- **Automation mode** (`--auto` / `--headless`) — never ask the user what to do next. Re-validate and fix all in-policy findings, propagate `--auto` to nested `andthen:*` skill invocations that accept it (the `andthen:ops` skill is exempt — it is deterministic), and return deterministic status/verification output. Stop with `BLOCKED:` (listing the minimum missing decisions or unresolved findings with evidence) only when the report is invalid, an unsafe external action is required, or a finding requires a product/requirements decision with no defensible local fix.


## GOTCHAS

- Fixing stale findings that were already resolved
- Treating every suggestion as mandatory when it does not affect correctness, maintainability, or PASS/FAIL
- Expanding a narrow remediation into a broad refactor
- Marking plan or FIS artifacts done before re-validation proves the findings are actually addressed
- Editing the wrong artifact when the real issue belongs in a spec, plan, PRD, or user-facing document
- Forcing a speculative doc rewrite when the real issue is an unresolved product or requirements decision that needs escalation


## WORKFLOW

### Phase 1: Resolve Report and Targets

1. Resolve `REPORT_SOURCE` to readable report content:
   - Local report path or direct raw report URL: read it directly
   - Any other input shape (issue page, PR shell URL, generic link): stop with an invalid-input error stating that the actual report content is required
2. Extract from the report body:
   - Review mode (`gap`, `code`, `doc`, `mixed`, `architecture`, `council`) — read from the report's mode line or the report filename suffix (e.g. `-gap-review.md` → `gap`)
   - Report verdict (PASS/FAIL) when present
   - Findings, severity, remediation recommendations, and reviewed scope
   - Referenced implementation targets, requirements baseline, FIS path, `plan.md`, and story IDs when the report names them
3. If the report has no actionable findings, stop and return that there are no actionable findings.

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
- If a finding reveals an unresolved product decision, missing requirement, or ambiguous source of truth rather than a defect in the reviewed artifacts, stop and escalate instead of forcing a speculative edit. In `AUTO_MODE`, return `BLOCKED:` with the minimum missing decision instead of asking the user.
- Use parallel sub-agents only for independent fix groups

**Gate**: Minimal remediation plan is clear and bounded


### Phase 4: Implement and Re-Validate

1. Implement fixes by logical area and artifact type.
2. Add or update tests when an implementation finding requires proof-of-work.
3. Run targeted verification after each fix group:
   - Implementation fixes: tests, linting, type checks, builds
   - Document fixes: verify terminology, cross-references, linked paths, commands/examples, consistency with source of truth
   - Workflow artifact fixes: verify templates, status semantics, cross-document consistency
4. Invoke the `andthen:quick-review` skill on the touched scope (via `/andthen:quick-review` or the Skill tool — not as `subagent_type`; append `--auto` when `AUTO_MODE=true`).
5. **Findings re-check**: Walk through every finding from the original report and verify resolution against the current workspace. For each finding, state: `RESOLVED` (with evidence), `PARTIALLY RESOLVED` (what remains), `UNRESOLVED` (why), or `DEFERRED` (per severity policy, with justification). This is the primary close-the-loop validation.
6. If both implementation and document artifacts changed, verify consistency across them.
7. If Critical/High findings remain after one remediation pass, escalate rather than looping. In `AUTO_MODE`, return `BLOCKED:` with unresolved findings and verification evidence.

**Gate**: Every Critical/High finding is RESOLVED with evidence, Medium/Low findings are RESOLVED or DEFERRED with justification, quick-review on touched scope is clean, no new regressions


### Phase 5: Update Workflow State

The findings re-check and quick-review results from Phase 4 are the evidence needed to update state. When all required findings are resolved and verification is clean, update state now.

If the report is tied to a story or FIS and remediation passed validation:
- Use the `andthen:ops` skill: `update-fis {fis_path} all` when the FIS work is substantively complete and evidence exists
- Use the `andthen:ops` skill: `update-plan {plan_path} {story_id} Done` only after confirming plan acceptance criteria are satisfied
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
