---
description: "The default review command – start here for all reviews. Inspects target and routes to code review, document review, gap analysis, or council escalation as needed. Trigger on 'review this', 'review these changes', 'review this PR', 'review this spec', 'review this PRD', 'audit this', 'does this match the spec'."
user-invocable: true
argument-hint: "[target/files/PR/spec path] [--deep] [--council] [--code-only] [--doc-only] [--gap-only] [--to-issue] [--to-pr <number>]"
---

# Review

Unified review entrypoint. Determine what is actually being reviewed, run the minimum correct review stack, and produce one consolidated result.

Use this as the default review skill. It delegates internally to `andthen:review-code`, `andthen:review-doc`, or `andthen:review-gap` based on the review surface.

## VARIABLES
ARGUMENTS: $ARGUMENTS

### Optional Mode Flags
- `--deep` → prefer more thorough review and escalate when risk justifies it on implementation-facing reviews
- `--council` → force `andthen:review-council` in addition to the primary stack for implementation-facing reviews
- `--code-only` → force implementation/code review
- `--doc-only` → force document review
- `--gap-only` → force requirements-vs-implementation review
- `--to-issue` → publish the final report to GitHub issue when a single delegated review owns publishing, or publish the consolidated report if this skill writes it
- `--to-pr <number>` → publish the final report to a PR comment when a single delegated review owns publishing, or publish the consolidated report if this skill writes it

## INSTRUCTIONS
- Read the Workflow Rules, Guardrails, and relevant project guidelines before starting.
- Read-only analysis. Do not modify the reviewed artifacts.
- Default to the minimum sufficient review stack.
- Own the final synthesis — gather delegated results into one clear conclusion.
- Boundaries: `review-code` for implementation, `review-doc` for requirements/design artifacts, `review-gap` for implementation-vs-requirements comparison, `review-council` for high-assurance adversarial validation.

## GOTCHAS
- Treating all review requests as code review
- Running `review-gap` without a real requirements baseline
- Running both `review-doc` and `review-gap` when `review-gap` already covers the real question
- Escalating to `review-council` by default instead of when risk, ambiguity, or user intent warrants it
- Letting delegated skills each write their own report file when this skill should own the combined output

## WORKFLOW

### 1. Resolve Target and Context

Determine what the user wants reviewed, in priority order:
1. Explicit path, PR, issue, URL, or focus from `ARGUMENTS`
2. Explicit mode flags (`--code-only`, `--doc-only`, `--gap-only`)
3. Current pending changes (`git diff --stat`, `git diff --name-only`) when no target is provided
4. Neighboring artifacts that clarify intent: plan/FIS/PRD/spec docs, changed implementation files, related issue/PR context

Apply explicit mode flags during discovery, not only during later classification:
- `--doc-only`: when no explicit target is provided, restrict discovery to changed document artifacts (spec/FIS/PRD/plan/ADR/design/prompt/docs) and ignore changed implementation files as primary review targets; if no document targets are found, stop and report that doc-only review has no matching scope
- `--code-only`: when no explicit target is provided, restrict discovery to changed implementation/config/test files and ignore changed docs as primary review targets; if no implementation targets are found, stop and report that code-only review has no matching scope
- `--gap-only`: when no explicit target is provided, resolve both a requirements baseline and an implementation target from the current changes plus neighboring artifacts; if either side cannot be resolved, stop and report that the missing side is required for gap review

When no explicit target is provided and no mode flag narrows the scope, build the target map from the dirty worktree by separating:
- changed document artifacts
- changed implementation artifacts
- nearby requirements artifacts that may serve as baselines

Use nearby requirements artifacts to clarify context, not to override explicit review intent.

Build a concise target map:
- **Review target**
- **Relevant artifacts**
- **Implementation scope** if any
- **Requirements baseline** if any
- **User intent**: code quality, doc readiness, requirements fit, broad audit, or deep/high-confidence review

**Gate**: Review target and available context are explicit

### 2. Classify the Review Surface

Choose one of these modes:
- **Code**: implementation, config, tests, or current code changes
- **Doc**: spec, FIS, PRD, plan, ADR, design doc, prompt, or other written artifact
- **Gap**: requirements baseline plus implementation target, where the real question is “does this implementation satisfy the requirements?”
- **Mixed**: both document artifacts and implementation artifacts are independently in scope and each needs its own review lens; this mode dispatches to `Doc + Code`, not to `Gap`

Routing heuristics:
- Explicit mode flags override inference
- If the user explicitly asks whether implementation matches a spec, plan, PRD, issue, or requirements baseline, use **Gap**
- If the user says "review implementation of [doc]" or similar phrasing where a requirements document is the object of "implementation of", treat [doc] as the requirements baseline and route to **Gap** – the intent is requirements-fit validation, not a document review
- If the user explicitly asks for PR review, code review, change review, or an implementation audit, prefer **Code** unless they also clearly ask for requirements-fit validation
- If only docs changed, default to **Doc**
- If the target is a spec/FIS/PRD/plan path and no implementation target is explicit, default to **Doc**
- If only implementation changed, default to **Code**
- If there is a clear requirements baseline plus implementation scope and the user's core question is requirements fit, default to **Gap**
- If both docs and code changed:
  - Use **Gap** when the docs are acting as the requirements baseline for the implementation and the core question is whether the implementation matches them
  - Use **Mixed** when the docs themselves need readiness review and the implementation also needs independent code review
- The mere presence of neighboring PRD/FIS/plan/spec artifacts is not enough to force **Gap**. Nearby requirements docs provide context; they become the primary lens only when the user's question is actually requirements-vs-implementation fit

**Gate**: Review mode is selected and justified

### 3. Select the Review Stack

Run the minimum correct stack:
- **Code** → `andthen:review-code`
- **Doc** → `andthen:review-doc`
- **Gap** → `andthen:review-gap`
- **Mixed** → `andthen:review-doc` + `andthen:review-code`

Use **Mixed** only when there are two independent review surfaces (document readiness + implementation quality), not as uncertainty between `Doc` and `Gap`. Once selected, keep it through execution and reporting.

Escalate with `andthen:review-council` when:
- the selected review surface is **Code**, **Gap**, or **Mixed** with implementation changes
- `--council` is present
- `--deep` is present and the change is broad, risky, or cross-cutting
- the primary review finds severe or ambiguous issues that would benefit from adversarial challenge
- the user explicitly wants a high-confidence or multi-perspective review

`review-council` is implementation-focused — skip it for doc-only reviews even if `--council` is present.

When delegating:
- Instruct `review-code` and `review-doc` to return findings inline and skip separate report-file output
- Instruct `review-gap` to return inline findings plus PASS/FAIL verdict when used as a delegated sub-review
- Keep file-writing and GitHub publishing on this skill. Delegated specialists return findings inline; this skill owns the final report or final inline output.

**Gate**: Review stack is proportional to the review surface

### 4. Execute Delegated Reviews

Run the selected specialist reviews, using sub-agents when supported.

Delegation guidance:
- `review-code`: implementation-focused findings only
- `review-doc`: document readiness findings only
- `review-gap`: requirements-vs-implementation findings, verdict, and remediation priorities
- `review-council`: challenge and validate implementation-facing findings; do not use it as a generic router

If a delegated review cannot run, fall back to direct analysis using the same lens and note the fallback.

**Gate**: All selected review passes complete

### 5. Synthesize One Final Result

Produce one final review output. Include:
- **Scope**
- **Review mode used**: Code / Doc / Gap / Mixed
- **Review stack run**
- **Findings by severity**
- **Gap verdict** when `review-gap` ran
- **Escalation result** when `review-council` ran
- **Recommended next action**

Output conventions:
- If no file output is needed, present one consolidated inline result and clearly state which sub-review(s) ran
- If a report file or GitHub publishing is needed, write one consolidated markdown report and use `${CLAUDE_PLUGIN_ROOT}/references/report-output-conventions.md`
  - **Report suffix**: `review`
  - **Scope placeholder**: `review-target`
  - **Spec-directory rule**: use the feature/spec directory when the review centers on a spec/FIS/plan
  - **Target-directory rule**: otherwise store next to the primary review target

For GitHub publishing:
- Publish the consolidated report as `artifact_type: review`
- Populate metadata with `report_path`, `plan_path`, `fis_path`, `requirements_baseline`, and `implementation_targets` when known
- If the final review mode is clearly doc-only, code-only, or gap-only, mention that mode prominently in the report summary so downstream remediation can interpret the findings correctly

For **Mixed** reviews, keep `review-doc` and `review-code` findings in distinct subsections. Merge overlapping findings and use the strongest framing as canonical.
