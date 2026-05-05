---
description: Use when the user wants review findings or review comments addressed. Implements actionable findings from a review report with minimal, guideline-aligned fixes across code, specs, plans, PRDs, and documentation, then re-validates the result and updates plan/FIS status. Trigger on 'address these review findings', 'fix review comments', 'remediate findings'.
user-invocable: true
argument-hint: "[--auto|--headless] <review-report-path | report URL>"
---

# Remediate Findings

Implement validated findings from a review report. The goal is to clear real issues with the smallest safe change set across implementation and document artifacts, avoid over-engineering, re-run the right verification, and update workflow state when the reviewed work is now complete.


## VARIABLES

REPORT_SOURCE: $ARGUMENTS (strip any flag tokens like `--auto` or `--headless` before interpreting the remainder as the report path or URL)

### Optional Flags
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Require `REPORT_SOURCE`. Stop if missing.
- Treat the review report as an input contract, not unquestionable truth. Re-validate findings against the current workspace before editing artifacts.
- **FIS Required / Deeper Context handling** (when the remediation target includes a FIS): `Required Context` blocks are inlined verbatim at spec time and are authoritative — do not "fix" by re-fetching against the current source (that silently changes the executor's contract). Drift is a re-spec signal; escalate to the `andthen:spec` skill if fresh content is required. For broken `Deeper Context` anchors: repair the anchor, don't delete silently. **Legacy FIS fallback**: apply the same minimal-fix discipline to whatever upstream-reference structure the legacy FIS uses (old `## References & Constraints` heading, `### Documentation & References` table, or prose mentions). Don't migrate a legacy FIS to the new sections opportunistically — that's a re-spec, not a remediation.
- Fix validated findings with the smallest coherent patch set that resolves them.
- Avoid scope creep across files. Apply changes only to issues listed in the findings report; co-located issues you spot while remediating are surfaced in the completion report rather than fixed inline (surgical scope — see CRITICAL RULES). Do not expand into untouched files or rewrite nearby docs unless required to resolve a finding or prevent a regression.
- Prefer explicit, local fixes over broad rewrites, reorganizations, helpers, or framework layers.
- If external documentation is needed, spawn a sub-agent that consults the project's `## Documentation Lookup Tools` section; Claude Code plugin users may invoke the `andthen:documentation-lookup` agent directly.
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
   - Review mode (`gap`, `code`, `doc`, `security`, `mixed`, `architecture`, `council`) — read from the report's mode line or the report filename suffix (e.g. `-gap-review.md` → `gap`, `-security-review.md` → `security`)
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
   - Implementation fixes: tests, linting, type checks, builds — use the commands from the `Key Dev Commands` document (see **Project Document Index**; default: `docs/KEY_DEVELOPMENT_COMMANDS.md`); fall back to discovery (package.json scripts, Makefile targets, language conventions) only when the document is missing
   - Document fixes: verify terminology, cross-references, linked paths, commands/examples, consistency with source of truth
   - Workflow artifact fixes: verify templates, status semantics, cross-document consistency
4. Invoke the `andthen:quick-review` skill on the touched scope (via `/andthen:quick-review` or the Skill tool — not as `subagent_type`; append `--auto` when `AUTO_MODE=true`).
5. **Findings re-check**: Walk through every finding from the original report and verify resolution against the current workspace. For each finding, state: `RESOLVED` (with evidence), `PARTIALLY RESOLVED` (what remains), `UNRESOLVED` (why), or `DEFERRED` (per severity policy, with justification). This is the primary close-the-loop validation.
6. If both implementation and document artifacts changed, verify consistency across them.
7. If Critical/High findings remain after one remediation pass, escalate rather than looping. In `AUTO_MODE`, return `BLOCKED:` with unresolved findings and verification evidence.

**Gate**: Every Critical/High finding is RESOLVED with evidence, Medium/Low findings are RESOLVED or DEFERRED with justification, quick-review on touched scope is clean, no new regressions


### Phase 5: Update Workflow State

When all required findings are resolved and verification is clean, update state now.

If the report is tied to a story or FIS and remediation passed validation:
- Use the `andthen:ops` skill: `update-fis {fis_path} all` when the FIS work is substantively complete and evidence exists
- Use the `andthen:ops` skill: `update-plan {plan_path} {story_id} Done` only after confirming the FIS success criteria satisfy the plan story scope
- Update the `State` document (see **Project Document Index**) through the `andthen:ops` skill when it exists and the story is now complete
- Re-read the updated artifacts to verify the status changes applied

If the remediation only fixes document artifacts:
- Update only the workflow artifacts justified by the document remediation
- Do not mark implementation complete unless the FIS success criteria are also satisfied

If the report is a full-plan or workspace-wide review:
- Update only the status artifacts that can be justified from the completed remediation
- Do not mark individual stories done unless their FIS success criteria are clearly satisfied

#### Annotate the input report with `## Remediation Status`

Run this step **before** the tech-debt persistence step below. If `REPORT_SOURCE` from Phase 1 was a local writable path (not a raw URL, not any other non-writable input shape), write a `## Remediation Status` section at the end of the report file:

- Whole-section replace if the heading already exists: locate the LAST line that starts at column 0 with `## Remediation Status` and is not inside a fenced code block; overwrite from that line to EOF (so re-running on the same report leaves exactly one `## Remediation Status` H2). Append-with-leading-blank-line otherwise.
- One bullet per finding, in the original report's finding order: `- **{finding title or short quote}** — {STATUS} — {one-line evidence or justification}` where `{STATUS}` is one of `RESOLVED` / `PARTIALLY RESOLVED` / `UNRESOLVED` / `DEFERRED` from the Phase 4 findings re-check.
- Skip with a logged reason of `"remote URL — no local file to annotate"` (or an equivalent reason for any other non-writable input shape) when the input is not a local writable path. The skip is recorded in the completion report.
- If annotation fails for any reason (filesystem error, permission issue, etc.), continue to the tech-debt persistence step below and surface the annotation failure in the completion report — losing the tech-debt write because annotation failed would create silent debt drift.

#### Persist DEFERRED findings to the Tech Debt Backlog

Batch all `DEFERRED` entries into a single `andthen:ops` invocation: `update-tech-debt append <markdown-body>`. Use the `#### DEFERRED FINDINGS` body shape from the `andthen:ops` skill (`update-tech-debt append` form). Normalize upstream severity before populating `Severity:` — `CRITICAL/HIGH → High`, `MEDIUM → Medium`, `LOW → Low`; non-canonical values route to `Medium` with a logged note. Each entry requires a `Source report:` back-link. When zero findings are `DEFERRED`, skip this step entirely. The `andthen:ops` skill is deterministic and `--auto` is not propagated to it (per [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md)).

**Gate**: Status artifacts reflect the validated post-remediation state; the input report is annotated when writable; deferred findings are persisted to the Tech Debt Backlog when present


## COMPLETION

Report:
- Findings re-check table (each finding → RESOLVED / PARTIALLY RESOLVED / UNRESOLVED / DEFERRED with evidence or justification)
- Findings intentionally left open and why
- Verification results (tests, lints, builds, quick-review)
- Which workflow artifacts were updated
- **Tech-debt entries written**: count of new entries appended, target file path, and per-severity breakdown (e.g. `2 new entries → docs/TECH-DEBT-BACKLOG.md (High: 1, Medium: 1, Low: 0)`); state `0 entries` when no findings were `DEFERRED`
- **Report annotation status**: `written` (new `## Remediation Status` section), `replaced` (existing section replaced in place), or `skipped: <reason>` (e.g. `skipped: remote URL — no local file to annotate`); state the report path when written or replaced
