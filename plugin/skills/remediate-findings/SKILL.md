---
description: Use when the user wants review findings or review comments addressed. Implements actionable findings from a review report with minimal, guideline-aligned fixes across code, specs, plans, PRDs, and documentation, then re-validates the result and updates plan/FIS status. Trigger on 'address these review findings', 'fix review comments', 'remediate findings'.
user-invocable: true
argument-hint: "[--auto] <review-report-path(s) | report URL(s)>"
---

# Remediate Findings

Implement validated findings with the smallest safe change set, re-validate, and update workflow state.


## VARIABLES

REPORT_SOURCE: $ARGUMENTS (strip any flag tokens like `--auto` or `--headless` before interpreting the remainder as the report path or URL)

### Optional Flags
- `--auto` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Read project rules and guidelines (`CLAUDE.md` / `AGENTS.md` and referenced files) before starting.
- **Intent + Rules Context** – collect both bundles per [`intent-and-rules-context.md`](${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md) up-front in Phase 1, using the FIS/PRD/clarify path named in the input report when present. Phase 2a re-anchors findings against the Intent bundle before any fix is planned (see Phase 2a for the divergence-catch).
- Read the `Learnings` document (see **Project Document Index**) before Phase 2 – a matching entry's preventive measure informs fix shape.
- **Honor the upstream `Routing:` tag** – when the input report came from the `andthen:review` skill or the `andthen:quick-review` skill, each finding carries a `Routing: Fix | Note` field. **Fix**-tagged findings are eligible for application, subject to Phase 2/2a re-validation; **Note**-tagged findings are surfaced in the completion report for the user to decide on – never auto-applied. When the report has no `Routing:` field (older reports, external reports), Phase 2a still runs; routing degrades to severity policy alone.
- Require `REPORT_SOURCE`. Stop if missing.
- Treat the review report as an input contract, not unquestionable truth. Re-validate findings against the current workspace before editing artifacts.
- **FIS Required / Deeper Context handling** (when the target includes a FIS): apply minimal-fix discipline per [`fis-remediation-handling.md`](references/fis-remediation-handling.md) – Required Context is authoritative, drift is a re-spec signal, don't migrate legacy FIS sections opportunistically.
- Fix validated findings with the smallest coherent patch set that resolves them, preferring explicit local fixes over broad rewrites (surgical scope – see CRITICAL RULES). Co-located issues surface in the completion report (Phase 4 trace test).
- If external documentation is needed, spawn a sub-agent that consults the project's `## Documentation Lookup Tools` section, or invoke the dedicated `documentation-lookup` agent when available.
- Invoke the `andthen:ops` skill for deterministic plan/FIS/STATE updates instead of hand-editing those artifacts.
- **Automation mode** (`--auto`) – `AUTO_MODE`: never ask the user what to do next. Re-validate and fix all in-policy findings and return deterministic status/verification output. `--auto` propagates to nested `andthen:*` skills; the `andthen:ops` skill is exempt (deterministic) – see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). Stop with `BLOCKED:` (listing the minimum missing decisions or unresolved findings with evidence) only when the report is invalid, an unsafe external action is required, or a finding requires a product/requirements decision with no defensible local fix.
- **No-op terminal signal** – when the report is valid and has findings but **none are auto-applicable** (every valid finding is `Routing: Note` or Phase 2a `SURFACED`, so the Phase 3 fixable set is empty), return `NO-OP: no-auto-applicable-findings` with the surfaced findings listed for human decision (Phase 3). This is distinct from `BLOCKED:` – the input was valid and correctly produced no automated work; a consuming loop treats `NO-OP` as stop-and-escalate (fix / reroute / accept-with-notes), **not** a reason to re-review. Applies in both default and `--auto` modes.


## GOTCHAS

- Re-validation lapses (Phase 2): fixing already-resolved/superseded findings, treating every suggestion as mandatory, expanding into a broad refactor, or editing the wrong artifact when the issue belongs in a spec/plan/PRD/user doc instead of escalating an unresolved product or requirements decision.
- Status/deferral lapses (Phase 5 / Phase 2's named-blocker policy): marking plan or FIS artifacts done before re-validation proves resolution, or writing `DEFERRED` without citing a named Phase 2 blocker – an uncited deferral is the parking-lot anti-pattern.
- **Routing-gate lapses** – treating `Routing: Fix` as sufficient or auto-applying a `Routing: Note`. The Phase 2a Intent re-anchor is the gate (see INSTRUCTIONS / Phase 2a).
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
   - **Per-finding `Routing:` tag** (`Fix`/`Note`) when present; record absence and degrade per the INSTRUCTIONS rule.
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

Apply the canonical anchor moves in [`intent-and-rules-context.md`](${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md), with these remediation-specific bindings (remediate *surfaces* for the user to decide rather than dismisses):
- **Contradicts a Non-Goal / Out-of-Scope / explicit deferral** → demote to `SURFACED: contradicts Intent` (cite artifact and section). Even findings tagged `Routing: Fix` upstream demote here – this is the divergence-catch.
- **Defers to a later story** → demote to `SURFACED: deferred per <story-id>`.
- **Contradicts a stated Expected Outcome** → promote: correctness-critical regardless of upstream severity; if Phase 2 classified it `valid` at LOW/MEDIUM, escalate to HIGH for Phase 3 prioritization.
- **No Intent Context discoverable** → record `no-intent-anchor` on each finding; routing falls back to severity policy and the upstream `Routing:` tag alone.

Findings tagged `Routing: Note` upstream remain Note regardless of Phase 2a outcome (the upstream gate already declined to auto-apply). Phase 2a only *demotes* (or surfaces) when the Intent bundle contradicts.

For reports with no per-finding `Routing:` tag, compute an **effective route** after Phase 2 and Phase 2a: `Fix` when the severity policy says the finding should be fixed and no blocker / Intent demotion applies; `SURFACED` when Phase 2a demotes it; `DEFERRED` only under the named blockers in Phase 2 – so untagged findings stay in remediation rather than being excluded.

**Gate**: Every `valid` finding carries an Intent-anchor classification; the Phase 3 fixable set contains only findings whose effective route is `Fix`


### Phase 3: Plan Minimal Remediation

- Group findings by affected area to minimize conflicts and repeated verification
- Define the smallest change set that resolves the validated findings
- Choose the target artifact that actually owns the defect: code/config/tests for implementation problems, specs/plans/PRDs for requirements or design defects, and product/user docs for explanation, usage, or reference defects
- If a finding reveals an unresolved product decision, missing requirement, or ambiguous source of truth rather than a defect in the reviewed artifacts, stop and escalate instead of forcing a speculative edit. In `AUTO_MODE`, return `BLOCKED:` with the minimum missing decision instead of asking the user.
- Use parallel sub-agents only for independent fix groups
- **Empty fixable set (no-op)**: when nothing routes to Fix, skip the Phase 4 mutation/verification, still run the Phase 5 status/annotation steps the surfaced findings justify (e.g. annotate the report, persist DEFERRED entries), and return `NO-OP: no-auto-applicable-findings` (INSTRUCTIONS) listing the surfaced findings for human decision. Do not invent a Fix to avoid the no-op – that re-introduces the over-application path the routing gate exists to prevent.

**Gate**: Minimal remediation plan is clear and bounded, or the fixable set is empty and a `NO-OP:` signal is returned


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

When all required findings are resolved and verification is clean, update state now. **Invariant**: mark a story/FIS done only when its FIS Acceptance Scenarios and Structural Criteria are satisfied. Update only the status artifacts the completed remediation justifies, all via the `andthen:ops` skill, then re-read the updated artifacts to verify.

- **Story or FIS report**: `update-fis {fis_path} all` when the FIS work is substantively complete with evidence; `update-plan {plan_path} {story_id} done` once the invariant holds; update the `State` document (see **Project Document Index**) when it exists and the story is now complete.
- **Doc-only remediation**: update only the workflow artifacts the document remediation justifies.
- **Full-plan or workspace-wide review**: update only the justified status artifacts; mark individual stories done per the invariant.

#### Write and transition reconciliation-ledger entries

Via the `andthen:ops` skill per [`reconciliation-ledger.md`](${CLAUDE_PLUGIN_ROOT}/references/reconciliation-ledger.md) (argument shapes live there), passing the **FIS-adjacent ledger path** `{fis-without-ext}.reconciliation-ledger.md` for the governing FIS. When no governing FIS is in scope there is no ledger – skip these writes. Drift case → mutator:

- **Applied reconciliation** (validated and applied this pass) → `update-ledger reconcile`. For `RECONCILE REQUIRED` entries, include evidence the sanctioned `update-fis design-change` amendment and ADR path completed; never close that status with a bare reconcile call.
- **Finding judged invalid** (Phase 2 / 2a dismissed it with a concrete falsifier) → `update-ledger withdraw` with the falsifier, so it cannot silently re-raise without refuting it.
- **Remediation-introduced drift** (this pass left code diverging from its governing FIS without that FIS being amended) → `update-ledger add`, then include it in the As-Built Upstream Reconciliation recommendation.

**PRD-targeted reconciliations stay recommend-only** – never auto-apply an edit to a PRD or other product-level doc; surface the recommendation and leave the ledger entry OPEN. The `andthen:ops` skill is deterministic; `--auto` is not propagated to it.

#### Annotate the input report with `## Remediation Status`

Run this step **before** the tech-debt persistence step below. If `REPORT_SOURCE` from Phase 1 was a local writable path (not a raw URL, not any other non-writable input shape), write a `## Remediation Status` section at the end of the report file:

- Write the section per the deterministic mechanics in [`report-annotation.md`](references/report-annotation.md) – overwrite-to-EOF vs append, one bullet per finding in original order, with the STATUS enum (`RESOLVED` / `PARTIALLY RESOLVED` / `UNRESOLVED` / `DEFERRED` / `SURFACED`). Single-H2 invariant: a re-run leaves exactly one `## Remediation Status` heading.
- Skip with a logged reason of `"remote URL – no local file to annotate"` (or an equivalent reason for any other non-writable input shape) when the input is not a local writable path. The skip is recorded in the completion report.
- If annotation fails for any reason (filesystem error, permission issue, etc.), continue to the tech-debt persistence step below and surface the annotation failure in the completion report – losing the tech-debt write because annotation failed would create silent debt drift.

#### Persist DEFERRED findings to the Tech Debt Backlog

Batch all `DEFERRED` entries into a single `andthen:ops` invocation: `update-tech-debt append <markdown-body>`. Use the `#### DEFERRED FINDINGS` body shape from the `andthen:ops` skill (`update-tech-debt append` form). Normalize upstream severity before populating `Severity:` – `CRITICAL/HIGH → High`, `MEDIUM → Medium`, `LOW → Low`; non-canonical values (e.g. INFO) route to `Low` with a logged note. Each entry requires a `Source report:` back-link. **Every `DEFERRED` entry must include the named blocker from Phase 2 verbatim in the entry body (e.g. as a `Blocker:` line) so the parking-lot rule remains auditable from the backlog alone.** When zero findings are `DEFERRED`, skip this step entirely. The `andthen:ops` skill is deterministic and `--auto` is not propagated to it (per [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md)).

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
- **Terminal signal** when applicable: `NO-OP: no-auto-applicable-findings` (surfaced list follows) or `BLOCKED: <reason>`. A clean run with applied fixes emits neither. Emit `NO-OP` in the machine-stable line form consuming loops branch on – bare line `NO-OP: no-auto-applicable-findings`, no fence/indent/marker (grammar in the `andthen:review` skill's `references/review-verdict.md` § Loop Convergence Signals); the surfaced list follows on subsequent lines.
