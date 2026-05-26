---
description: Use when the user wants review findings or review comments addressed. Implements actionable findings from a review report with minimal, guideline-aligned fixes across code, specs, plans, PRDs, and documentation, then re-validates the result and updates plan/FIS status. Trigger on 'address these review findings', 'fix review comments', 'remediate findings'.
user-invocable: true
argument-hint: "[--auto|--headless] <review-report-path(s) | report URL(s)>"
---

# Remediate Findings

Implement validated findings from a review report. The goal is to clear real issues with the smallest safe change set across implementation and document artifacts, avoid over-engineering, re-run the right verification, and update workflow state when the reviewed work is now complete.


## VARIABLES

REPORT_SOURCE: $ARGUMENTS (strip any flag tokens like `--auto` or `--headless` before interpreting the remainder as the report path or URL)

### Optional Flags
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- **Fully read and understand all project rules, guardrails, principles and guidelines (as defined in `CLAUDE.md` / `AGENTS.md` and other referenced files) before starting work.**
- **Intent + Rules Context** – collect both bundles per [`intent-and-rules-context.md`](${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md) up-front in Phase 1, using the FIS/PRD/clarify path named in the input report when present. Phase 2a re-anchors findings against the Intent bundle before any fix is planned. A finding flagged for application by the upstream review can still be blocked here if it contradicts a Non-Goal the upstream review missed – this skill is the last gate before mutation.
- Read the `Learnings` document (see **Project Document Index**) before Phase 2 – a matching entry's preventive measure informs fix shape.
- **Honor the upstream `Routing:` tag** – when the input report came from the `andthen:review` skill or the `andthen:quick-review` skill, each finding carries a `Routing: Fix | Note` field. **Fix**-tagged findings are eligible for application (subject to Phase 2 re-validation and Phase 2a Intent re-anchor); **Note**-tagged findings are surfaced in the completion report for the user to decide on – never auto-applied. When the report has no `Routing:` field (older reports, external reports), Phase 2a still runs; routing degrades to severity policy alone.
- Require `REPORT_SOURCE`. Stop if missing.
- Treat the review report as an input contract, not unquestionable truth. Re-validate findings against the current workspace before editing artifacts.
- **FIS Required / Deeper Context handling** (when the remediation target includes a FIS): `Required Context` blocks are inlined verbatim at spec time and are authoritative – do not "fix" by re-fetching against the current source (that silently changes the executor's contract). Drift is a re-spec signal; escalate to the `andthen:spec` skill if fresh content is required. For broken `Deeper Context` anchors: repair the anchor, don't delete silently. **Legacy FIS fallback**: apply the same minimal-fix discipline to whatever upstream-reference structure the legacy FIS uses (old `## References & Constraints` heading, `### Documentation & References` table, or prose mentions). Don't migrate a legacy FIS to the new sections opportunistically – that's a re-spec, not a remediation.
- Fix validated findings with the smallest coherent patch set that resolves them.
- Avoid scope creep across files. Apply changes only to issues listed in the findings report; co-located issues you spot while remediating are surfaced in the completion report rather than fixed inline (surgical scope – see CRITICAL RULES). Do not expand into untouched files or rewrite nearby docs unless required to resolve a finding or prevent a regression.
- Prefer explicit, local fixes over broad rewrites, reorganizations, helpers, or framework layers.
- If external documentation is needed, spawn a sub-agent that consults the project's `## Documentation Lookup Tools` section; Claude Code plugin users may invoke the `andthen:documentation-lookup` agent directly.
- Invoke the `andthen:ops` skill for deterministic plan/FIS/STATE updates instead of hand-editing those artifacts.
- **Automation mode** (`--auto` / `--headless`) – never ask the user what to do next. Re-validate and fix all in-policy findings, propagate `--auto` to nested `andthen:*` skill invocations that accept it (the `andthen:ops` skill is exempt – it is deterministic), and return deterministic status/verification output. Stop with `BLOCKED:` (listing the minimum missing decisions or unresolved findings with evidence) only when the report is invalid, an unsafe external action is required, or a finding requires a product/requirements decision with no defensible local fix.


## GOTCHAS

- Fixing stale findings that were already resolved
- Treating every suggestion as mandatory when it does not affect correctness, maintainability, or PASS/FAIL
- Expanding a narrow remediation into a broad refactor
- Marking plan or FIS artifacts done before re-validation proves the findings are actually addressed
- Editing the wrong artifact when the real issue belongs in a spec, plan, PRD, or user-facing document
- Forcing a speculative doc rewrite when the real issue is an unresolved product or requirements decision that needs escalation
- Writing `DEFERRED` without citing one of the named blockers from Phase 2's severity policy – that means you are using the Tech Debt Backlog as a parking lot, not as a deferred-work queue
- **Applying a `Routing: Note` finding** – upstream review (or quick-review) routed it out of the auto-apply path on purpose; remediating it anyway re-introduces the drift the routing gate exists to prevent. Notes are surfaced for the user, not silently fixed.
- **Skipping Phase 2a Intent re-anchor** – an upstream `Routing: Fix` tag is necessary, not sufficient. If the originating FIS lists the finding's subject as a Non-Goal or deferral, applying it here drifts the feature even though the upstream review approved it. Phase 2a is the last gate.
- **Adding abstractions the finding didn't name** – named over-engineering shapes that creep in during remediation: a helper used once, a new config knob, a new wrapper or interface layer, a new error type, defensive validation at the wrong layer. None resolve the finding – they expand the change set under "while I'm here". If the finding doesn't name the abstraction, don't add it.


## WORKFLOW

### Phase 1: Resolve Report and Targets

1. Resolve `REPORT_SOURCE` to readable report content:
   - Local report path or direct raw report URL: read it directly
   - Any other input shape (issue page, PR shell URL, generic link): stop with an invalid-input error stating that the actual report content is required
2. Extract from the report body:
   - Review mode (`gap`, `code`, `doc`, `security`, `mixed`, `architecture`, `council`) – read from the report's mode line or the report filename suffix (e.g. `-gap-review.md` → `gap`, `-security-review.md` → `security`)
   - Report verdict (PASS/FAIL) when present
   - Findings, severity, remediation recommendations, and reviewed scope
   - **Per-finding `Routing:` tag** when present (`Fix` or `Note`). Reports from the current `andthen:review` skill and the `andthen:quick-review` skill always carry it; older reports and external reports may not – record absence and degrade per the INSTRUCTIONS rule.
   - **`Intent Context:` line** when present (path to the governing FIS/PRD/clarify artifact, or `none discoverable`). Used to seed Phase 2a.
   - Referenced implementation targets, requirements baseline, FIS path, `plan.json`, and story IDs when the report names them
3. Collect the **Intent + Rules Context** bundles per [`intent-and-rules-context.md`](${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md) – seed with the `Intent Context:` line from step 2 when present; otherwise discover from the report's referenced targets and the **Project Document Index**. When no governing artifact is discoverable, record so explicitly – Phase 2a still runs and falls back to severity policy alone.
4. If the report has no actionable findings, stop and return that there are no actionable findings.

**Gate**: Actionable findings, the remediation target, per-finding `Routing:` tags (when present), and the Intent + Rules Context bundles are explicit


### Phase 2: Re-Validate Findings

For each finding:
- Check whether it is still true in the current workspace
- Classify it as `valid`, `already fixed`, `superseded`, or `unclear`
- Classify the remediation surface as `implementation`, `document`, `workflow-artifact`, or `mixed`
- Keep only currently valid findings in scope

Severity policy:
- **Default**: fix every reviewer-flagged finding (all severities, including INFO findings with a remediation suggestion). Severity sets escalation priority, not the defer/fix default.
- **Defer** only when a named blocker applies, cited explicitly with the deferral:
  - `out-of-scope file` – the file is NOT named in the input review report's findings. The review report is the input contract; a file the reviewer cited is in-scope here, regardless of upstream IO carve-outs from prior implementation passes.
  - `decision needed` – the fix encodes an unresolved product, design, or requirements decision.
  - `new test harness required` – needs a new test file, fixture, or framework setup. Adding a case to an existing test file is not a blocker.
  - `risk: <concrete>` – a named caller, test, input shape, or invariant the fix could break. Generic "regression risk" is not concrete.
  - `caller API change required` – the fix would require breaking changes to public APIs or callers outside the change set's stated scope.
  - `data migration required` – the fix requires a data or schema migration the change set is not scoped to deliver.
- **Observational findings** (the reviewer confirmed something passes, no gap flagged – e.g. "TI Verify lines pass when re-executed") are acknowledged in the completion report; not deferred.

Critical/High findings with a valid blocker escalate; lower-severity findings with a valid blocker route to the Tech Debt Backlog. Triviality and locality bias toward fixing.

If all findings are already fixed or superseded, skip to Phase 5 and only update status artifacts when that is now justified.

**Gate**: Remediation scope is bounded to currently valid findings


### Phase 2a: Intent Re-Anchor

For every finding that survived Phase 2 as `valid`, classify it against the **Intent Context** bundle collected in Phase 1 (per [`intent-and-rules-context.md`](${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md)). This is the last gate before mutation – an upstream `Routing: Fix` tag is necessary, not sufficient.

Apply the canonical anchor moves:
- **Contradicts a Non-Goal / Out-of-Scope statement / explicit deferral** → demote to `SURFACED: contradicts Intent` (not auto-applied; appears in the completion report for the user to decide). Cite the artifact and section. Even findings tagged `Routing: Fix` upstream demote here – this is the divergence-catch.
- **Defers to a later story** → demote to `SURFACED: deferred per <story-id>`. Same treatment as the contradiction case.
- **Contradicts a stated Expected Outcome** → promote: the finding is correctness-critical regardless of upstream severity. If Phase 2 classified it `valid` but at LOW/MEDIUM severity, escalate to HIGH for Phase 3 prioritization.
- **No Intent Context discoverable** → record `no-intent-anchor` on each finding; routing falls back to severity policy and the upstream `Routing:` tag alone.

Findings tagged `Routing: Note` upstream remain Note regardless of Phase 2a outcome (the upstream gate already declined to auto-apply). Phase 2a never *promotes* a Note into a Fix – that direction would re-introduce the over-application path the routing gate exists to prevent. Phase 2a only *demotes* (or surfaces) when the Intent bundle contradicts.

For reports with no per-finding `Routing:` tag, compute an **effective route** after Phase 2 and Phase 2a: `Fix` when the severity policy says the finding should be fixed and no blocker / Intent demotion applies; `SURFACED` when Phase 2a demotes it; `DEFERRED` only under the named blockers in Phase 2. This preserves older and external report behavior instead of excluding untagged findings from remediation.

**Gate**: Every `valid` finding carries an Intent-anchor classification; the Phase 3 fixable set is bounded to findings whose effective route is `Fix`: upstream `Routing: Fix`, or no upstream routing tag and the severity policy says fix, excluding findings demoted or deferred here


### Phase 3: Plan Minimal Remediation

- Group findings by affected area to minimize conflicts and repeated verification
- Define the smallest change set that resolves the validated findings
- Favor boring, readable fixes over clever or reusable abstractions
- Choose the target artifact that actually owns the defect: code/config/tests for implementation problems, specs/plans/PRDs for requirements or design defects, and product/user docs for explanation, usage, or reference defects
- If a finding reveals an unresolved product decision, missing requirement, or ambiguous source of truth rather than a defect in the reviewed artifacts, stop and escalate instead of forcing a speculative edit. In `AUTO_MODE`, return `BLOCKED:` with the minimum missing decision instead of asking the user.
- Use parallel sub-agents only for independent fix groups

**Gate**: Minimal remediation plan is clear and bounded


### Phase 4: Implement and Re-Validate

1. Implement fixes by logical area and artifact type. **Trace test**: every changed hunk traces to a Fix-bucket finding's location; hunks without a finding are scope creep – surface them in the completion report instead of bundling them.
2. Add or update tests when an implementation finding requires proof-of-work.
3. Run targeted verification after each fix group:
   - Implementation fixes: tests, linting, type checks, builds – use the commands from the `Key Dev Commands` document (see **Project Document Index**; default: `docs/KEY_DEVELOPMENT_COMMANDS.md`); fall back to discovery (package.json scripts, Makefile targets, language conventions) only when the document is missing
   - Document fixes: verify terminology, cross-references, linked paths, commands/examples, consistency with source of truth
   - Workflow artifact fixes: verify templates, status semantics, cross-document consistency
4. Invoke the `andthen:quick-review` skill on the touched scope (via `/andthen:quick-review` or the Skill tool – not as `subagent_type`; append `--auto` when `AUTO_MODE=true`).
5. **Findings re-check**: Walk through every finding from the original report and verify resolution against the current workspace. For each finding, state: `RESOLVED` (with evidence), `PARTIALLY RESOLVED` (what remains), `UNRESOLVED` (why), `DEFERRED` (per severity policy, with justification), or `SURFACED` (Phase 2a demoted, or upstream `Routing: Note` – not auto-applied, listed for user decision with the Intent-anchor citation when one applied). Every `DEFERRED` entry must cite one of the named blockers from Phase 2's severity policy – entries without a cited blocker are not valid deferrals and the finding must be fixed instead. `SURFACED` entries cite the upstream tag and/or the Phase 2a Intent-anchor reason, not a Phase 2 blocker. This is the primary close-the-loop validation.
6. If both implementation and document artifacts changed, verify consistency across them.
7. If Critical/High findings remain after one remediation pass, escalate rather than looping. In `AUTO_MODE`, return `BLOCKED:` with unresolved findings and verification evidence.

**Gate**: Every Critical/High finding is RESOLVED with evidence, Medium/Low findings are RESOLVED / DEFERRED / SURFACED with justification, quick-review on touched scope is clean, no new regressions


### Phase 5: Update Workflow State

When all required findings are resolved and verification is clean, update state now.

If the report is tied to a story or FIS and remediation passed validation:
- Use the `andthen:ops` skill: `update-fis {fis_path} all` when the FIS work is substantively complete and evidence exists
- Use the `andthen:ops` skill: `update-plan {plan_path} {story_id} Done` only after confirming the FIS Acceptance Scenarios and Structural Criteria satisfy the plan story scope
- Update the `State` document (see **Project Document Index**) through the `andthen:ops` skill when it exists and the story is now complete
- Re-read the updated artifacts to verify the status changes applied

If the remediation only fixes document artifacts:
- Update only the workflow artifacts justified by the document remediation
- Do not mark implementation complete unless the FIS Acceptance Scenarios and Structural Criteria are also satisfied

If the report is a full-plan or workspace-wide review:
- Update only the status artifacts that can be justified from the completed remediation
- Do not mark individual stories done unless their FIS Acceptance Scenarios and Structural Criteria are clearly satisfied

#### Annotate the input report with `## Remediation Status`

Run this step **before** the tech-debt persistence step below. If `REPORT_SOURCE` from Phase 1 was a local writable path (not a raw URL, not any other non-writable input shape), write a `## Remediation Status` section at the end of the report file:

- Whole-section replace if the heading already exists: locate the LAST line that starts at column 0 with `## Remediation Status` and is not inside a fenced code block; overwrite from that line to EOF (so re-running on the same report leaves exactly one `## Remediation Status` H2). Append-with-leading-blank-line otherwise.
- One bullet per finding, in the original report's finding order: `- **{finding title or short quote}** – {STATUS} – {one-line evidence or justification}` where `{STATUS}` is one of `RESOLVED` / `PARTIALLY RESOLVED` / `UNRESOLVED` / `DEFERRED` / `SURFACED` from the Phase 4 findings re-check. `SURFACED` entries include the upstream `Routing:` tag and/or the Phase 2a Intent-anchor citation in the justification.
- Skip with a logged reason of `"remote URL – no local file to annotate"` (or an equivalent reason for any other non-writable input shape) when the input is not a local writable path. The skip is recorded in the completion report.
- If annotation fails for any reason (filesystem error, permission issue, etc.), continue to the tech-debt persistence step below and surface the annotation failure in the completion report – losing the tech-debt write because annotation failed would create silent debt drift.

#### Persist DEFERRED findings to the Tech Debt Backlog

Batch all `DEFERRED` entries into a single `andthen:ops` invocation: `update-tech-debt append <markdown-body>`. Use the `#### DEFERRED FINDINGS` body shape from the `andthen:ops` skill (`update-tech-debt append` form). Normalize upstream severity before populating `Severity:` – `CRITICAL/HIGH → High`, `MEDIUM → Medium`, `LOW → Low`; non-canonical values (e.g. INFO) route to `Low` with a logged note. Each entry requires a `Source report:` back-link. **Every `DEFERRED` entry must include the named blocker from Phase 2 verbatim in the entry body (e.g. as a `Blocker:` line) so the parking-lot rule remains auditable from the backlog alone – an entry with no blocker citation is the anti-pattern itself.** When zero findings are `DEFERRED`, skip this step entirely. The `andthen:ops` skill is deterministic and `--auto` is not propagated to it (per [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md)).

**Gate**: Status artifacts reflect the validated post-remediation state; the input report is annotated when writable; deferred findings are persisted to the Tech Debt Backlog when present


### Phase 6: Capture Cross-Finding Patterns _(optional)_

If a recurring trap emerged (same defect class across findings, or a repeat of an existing `Learnings` entry), append via the `andthen:ops` skill (`update-learnings add` form). Bar: "Would a competent developer with code and git access still get bitten?" One-offs do not qualify.

**Gate**: Recurring patterns captured, or skipped


## COMPLETION

Report:
- Findings re-check table (each finding → RESOLVED / PARTIALLY RESOLVED / UNRESOLVED / DEFERRED / SURFACED with evidence or justification)
- Findings intentionally left open and why (including `SURFACED` findings the user needs to decide on, with the upstream `Routing:` tag and/or Phase 2a Intent-anchor citation that surfaced them)
- Verification results (tests, lints, builds, quick-review)
- Which workflow artifacts were updated
- **Tech-debt entries written**: count of new entries appended, target file path, and per-severity breakdown (e.g. `2 new entries → docs/TECH-DEBT-BACKLOG.md (High: 1, Medium: 1, Low: 0)`); state `0 entries` when no findings were `DEFERRED`
- **Report annotation status**: `written` (new `## Remediation Status` section), `replaced` (existing section replaced in place), or `skipped: <reason>` (e.g. `skipped: remote URL – no local file to annotate`); state the report path when written or replaced
