---
description: Use when the user wants to execute or implement an existing spec or FIS. Implements code from a Feature Implementation Specification. Trigger on 'execute this spec', 'execute this FIS', 'implement this spec', 'implement this FIS', 'build from spec'.
argument-hint: <path-to-fis | --issue <number> | issue URL>
---

# Execute Feature Implementation Specification

Execute a fully-defined FIS document as the **executor**. Implement the FIS directly, use sub-agents only for narrow advisory/review work, and complete all validation and status gates before finishing.

## VARIABLES
FIS_SOURCE: $ARGUMENTS


## INSTRUCTIONS

### Core Rules
- Require `FIS_SOURCE`. Stop if missing.
- **Complete implementation** — 100% completion required; partial completion is not acceptable.
- **FIS is source of truth** — follow it exactly.
- Persist until the full FIS is complete or a real external blocker makes completion impossible.
- **Direct execution** — implement the code yourself. Sub-agents are for advisory work, review, and validation only.
- If you catch yourself rationalizing away test scaffolding, verification gates, or status updates, load `${CLAUDE_PLUGIN_ROOT}/references/anti-rationalization.md`.

### Executor Role
**You are the executor.** Your job:
- Load and understand the FIS
- Read technical research, project learnings, and ubiquitous-language guidance needed to implement accurately
- Build a quick codebase overview once at the start, then focus on the files the FIS actually touches
- Handle bounded prep inline when it improves execution quality (for example scenario-test scaffolding and optional UI contract generation)
- Implement tasks directly, in order, running each task's **Verify** line before moving on
- Mark task checkboxes immediately after each task completes
- Proactively spawn narrow advisory sub-agents when you hit genuine uncertainty
- Run validation, triage findings, and fix must-fix issues directly in one remediation pass
- Ensure all status updates and gates complete before finishing

Do not: delegate coding to advisory agents, batch status updates until the end, silently narrow scope, or skip final gates.

### Helper Scripts
Available in `${CLAUDE_PLUGIN_ROOT}/scripts/`:
- `check-stubs.sh <path>` – scan for incomplete implementation indicators
- `check-wiring.sh <path>` – verify new/changed files are imported/referenced
- `verify-implementation.sh <file1> [file2...]` – combined existence + substance + wiring check

### Proactive Sub-Agents
Spawn narrow background sub-agents when they materially improve a coding decision and you can keep implementing while they run. Their output is advisory; the FIS remains the contract.

- `andthen:documentation-lookup` – use for unfamiliar APIs, library/framework behavior, migration details, or version-specific questions. This is the required path for documentation lookup; run it as a separate background sub-task.
- `andthen:solution-architect` – use for unresolved architectural trade-offs or integration-pattern ambiguity not settled by the FIS
- `andthen:ui-ux-designer` – use for UI layout, interaction, accessibility, or responsive-pattern advice when the FIS needs a design contract
- `andthen:build-troubleshooter` – use for non-trivial build failures, dependency conflicts, or cascading test failures
- `andthen:research-specialist` – use for external best-practice research or context not available in the codebase
- `andthen:qa-test-engineer` – use for complex test strategy or unfamiliar test-harness patterns

Usage rules:
- Prefer multiple narrow questions over one broad prompt
- Spawn early when the need appears; do not wait until you are fully blocked
- Continue local implementation when the sub-agent is background-able
- If sub-agent guidance conflicts with the FIS, follow the FIS
- Do not spawn a sub-agent for coding work you should do directly


## GOTCHAS
- **Delegating implementation to advisory sub-agents** – recreates the context-loss and serial overhead the skill is designed to avoid
- **Status updates dropped when context exhausted** – update FIS task checkboxes immediately; plan and FIS updates in Step 5 are gates
- **FIS references get stale if spec was updated** – always re-read the FIS
- **Not signaling active-story status to the `State` document when called in a plan context** – read the location from the **Project Document Index** and set "In Progress" at start
- **Treating spec size or difficulty as permission to narrow scope** – exec-spec executes the FIS it was given; if the spec should have been split, that is an upstream spec-quality problem, not a license to land a subset and stop


## WORKFLOW

### Step 1: Resolve FIS Source
1. Resolve `FIS_SOURCE` to a local `FIS_FILE_PATH`:
   - Local file path: use it directly
   - `--issue <number>` or GitHub issue URL: follow `${CLAUDE_PLUGIN_ROOT}/references/resolve-github-input.md`.
     Compatible types: `fis-bundle` — extract and set `FIS_FILE_PATH` from `canonical_local_primary`. Redirects: `plan-bundle` → `andthen:exec-plan` / `andthen:spec-plan`; `triage-plan` / `triage-completion` / any `*-review` → stop with matching downstream skill. Untyped: stop — `exec-spec` requires a local FIS path or a typed GitHub FIS artifact.
   - If `canonical_local_primary` is missing, ambiguous, or does not match an extracted file, stop.
   - Recover metadata from the envelope:
     - `FIS_CANONICAL_PATH` = `fis_path` when present, otherwise `canonical_local_primary`
     - `PLAN_FILE_PATH` = `plan_path` when present; if it refers to an embedded companion file, use the extracted copy
     - `STORY_IDS` = `story_ids`
   - If the envelope says the FIS originated from a plan (`plan_path` present) but omits `story_ids`, stop — plan-backed FIS execution needs that context for plan/state updates.
   - If `plan_path` is present but no embedded or local `PLAN_FILE_PATH` can actually be resolved, stop — plan-backed FIS execution cannot update source plan state without the plan file.
   - Otherwise set `FIS_SOURCE_MODE = github-artifact`
2. Recover enough source metadata to finish the run cleanly: `FIS_SOURCE_MODE`, `FIS_CANONICAL_PATH`, optional `PLAN_FILE_PATH`, and optional `STORY_IDS`

**Gate**: canonical FIS path resolved and any plan/artifact metadata captured

### Step 2: Read and Prepare
1. Read the full FIS at _`FIS_FILE_PATH`_
2. Understand the sections that define execution: Success Criteria, Scenarios, Scope & Boundaries, Architecture Decision, Technical Overview, Implementation Plan, Testing Strategy, Validation, and Final Validation Checklist
3. **Read Technical Research** – if the FIS references a `.technical-research.md`, read it before making code changes. Treat findings as leads to verify, not facts to trust.
4. Read the `Learnings` document (see **Project Document Index**) if it exists and is relevant
5. Read the `Ubiquitous Language` document (see **Project Document Index**) if it exists and is relevant. Use canonical terms in code and avoid listed synonyms.
6. Build a quick codebase overview once at the start (`tree -d`, `git ls-files | head -250`), then stop broad discovery and focus on the files/tasks the FIS actually touches
7. If the FIS has **Scenarios** and/or **Testing Strategy**, scaffold the minimum high-signal scenario-test skeletons inline using nearby test patterns. When practical, confirm they fail before implementation. If the test harness is still unclear after one bounded pass, note the skip and continue.
8. If the FIS has UI work and no adequate design contract is already referenced, create a short `.agent_temp/ui-spec-{feature-name}.md` covering spacing, typography, color, component patterns, and responsive breakpoints. Source from FIS → project design system → UX guidelines → reasonable defaults.
9. **Update project state** (if the `State` document exists in the location defined by the **Project Document Index** and the FIS originated from a plan): restore story context from `STORY_IDS`. For a single-story FIS, use that story directly. For a composite/shared FIS, mark the active work as the composite/story set rather than inventing a single story ID.
10. Initialize working notes you will maintain during the run:
   - Per-task status
   - `changed-files`
   - Any `CONFUSION`, `NOTICED BUT NOT TOUCHING`, or `MISSING REQUIREMENT` items

### Step 3: Implement
Implement the FIS yourself, task by task, in the order listed.

For each task:
1. Implement the outcome described
2. Run the task's **Verify** line before proceeding to the next task
3. For tasks with paired scenario tests, drive them red → green when practical
4. Honor prescriptive details exactly: column names, format strings, error messages, file paths, UI control names, and similar contract-level details
5. Update `changed-files`
6. Mark the task checkbox complete immediately in the FIS — do not batch checkbox updates
7. Record the task result in your working notes

Implementation rules:
- Use the structured output protocols from `${CLAUDE_PLUGIN_ROOT}/references/structured-output-protocols.md` when needed:
  - **CONFUSION**: the FIS is ambiguous and you cannot safely proceed
  - **NOTICED BUT NOT TOUCHING**: you found something relevant but out of scope
  - **MISSING REQUIREMENT**: a task assumes something absent from the codebase
- Spawn proactive sub-agents when the need arises, but keep ownership of the code changes locally
- If `changed-files` becomes incomplete or ambiguous, derive it from the current worktree diff before Step 4

### Step 4: Validate
Step 3 verifies task-level outcomes. Step 4 catches cross-cutting issues — integration, security, architectural coherence, and spec drift — that can still survive per-task Verify lines.

#### 4a. Direct Checks
1. **Build**: run the project's applicable build/package checks; every available build step relevant to the feature must succeed
2. **Tests**: run the applicable test suites; all relevant tests must pass (or pre-existing failures documented)
3. **Lint/types**: run the applicable static analysis checks; no new violations
4. **Stub detection**: `check-stubs.sh <changed-files>` — must be clean
5. **Wiring check**: `check-wiring.sh <changed-files>` — each new file referenced by at least one other
6. **Spec compliance spot-check**: extract prescriptive details from the FIS (output format strings, column name lists, file paths for new artifacts, exact error messages, UI elements like buttons/controls) and grep/verify each against the implementation — any mismatch is a remediation input

#### 4b. Code Review (mandatory sub-agent)
Spawn `andthen:review-code` sub-agent for independent fresh-context review covering: static analysis, linting, formatting, type checking, code quality, architecture, security, domain language, stub detection, wiring verification, and simplification opportunities (unnecessary complexity, duplication, over-abstraction introduced during implementation).

#### 4c. Visual Validation (if UI)
Spawn `andthen:visual-validation-specialist` sub-agent _(if supported)_ per any Visual Validation Workflow defined in CLAUDE.md.

Steps 4b and 4c can run in parallel _(if supported)_.

#### 4d. Remediation (1 pass max)
1. **Collect failures and findings** — combine required failures from 4a with findings from 4b/4c. A failed build/test/lint/stub/wiring check is a remediation input even if review-code does not flag it separately.
2. **Triage** — direct-check failures and CRITICAL/HIGH findings must fix; MEDIUM should fix; LOW optional (review-code mapping: CRITICAL→CRITICAL, HIGH→HIGH, SUGGESTIONS→MEDIUM)
3. **Fix + re-check once** — fix all must-fix items directly, then re-run the failed or affected validation checks once. If remediation touched any `review-code` finding, re-run `andthen:review-code` on the touched scope before proceeding. If remediation touched any visual-validation finding, re-run the applicable visual validation on the touched scope before proceeding.
4. **No second loop** — if required failures or CRITICAL/HIGH findings remain after one remediation pass, escalate to the user with a summary of unresolved issues and stop the run

### Step 5: Complete
All substeps below are gates — complete them before finishing.

#### 5a. Verify Completion
Lightweight gate – uses Step 4a results, does not re-run checks:
1. Verify all success criteria met
2. Verify all task checkboxes marked (catch any missed from Step 3)
3. Verify Final Validation Checklist items satisfied
4. Collect verification evidence from Step 4a: **Build** (exit code/status), **Tests** (pass/fail counts), **Linting/types** (error/warning counts); add **Visual validation** and **Runtime** for UI/runtime stories

#### 5b. Update FIS, Source Plan, and Project State
Update FIS status, source plan (if applicable), and project state via `andthen:ops`. For plan-backed FIS: set each covered story Status to `Done`, set FIS field path, check off acceptance criteria, and mark the story `Done` in the `State` document (see **Project Document Index**) with a short completion note. For composite/shared FIS, update all constituent stories in `STORY_IDS`. Re-read to verify updates applied.

If `FIS_SOURCE_MODE = github-artifact`, apply the continuation sync from `${CLAUDE_PLUGIN_ROOT}/references/github-artifact-roundtrip.md` before finishing.

#### 5c. Completion Report
Report: per-task status, files created/modified, verification evidence, any unresolved low-priority issues or `NOTICED BUT NOT TOUCHING` items.

## Post-Completion
If the `Learnings` document (see **Project Document Index**) exists, capture story-level traps, domain knowledge, procedural knowledge, and error patterns. Organize by topic, not chronology. Keep entries brief (1-2 sentences). Do not create a new `Learnings` document unless one already exists.

> FIS checkbox/status updates and plan updates are handled in Step 5 — they are gates, not post-completion tasks.
