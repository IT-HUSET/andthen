---
description: Use when the user wants to execute or implement an existing spec or FIS. Implements code from a Feature Implementation Specification. Trigger on 'execute this spec', 'execute this FIS', 'implement this spec', 'implement this FIS', 'build from spec'.
argument-hint: "[--auto|--headless] [--defer-shared-writes] <path-to-fis>"
---

# Execute Feature Implementation Specification

Execute a fully-defined FIS document as the **executor**. Implement the FIS directly, use sub-agents only for narrow advisory/review work, and complete all validation and status gates before finishing.

## VARIABLES
FIS_FILE_PATH: $ARGUMENTS (strip any flag tokens like `--auto`, `--headless`, or `--defer-shared-writes` before interpreting the remainder as the FIS path)

### Optional Flags
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts
- `--defer-shared-writes` → DEFER_SHARED_WRITES: skip direct `plan.md` and `State` document writes (FIS writes still run); emit a `## Deferred Shared Writes (worktree mode)` audit block in the completion report instead. Set automatically by `andthen:exec-plan --team --worktree` to prevent concurrent worktree merges from colliding on shared files. Intended for orchestrated use — see Step 5b.5 for emission format and standalone-use details.


## INSTRUCTIONS

### Core Rules
- Require `FIS_FILE_PATH`. Stop if missing.
- **Complete implementation** — 100% required. Reporting incomplete work with a caveat is **not** completion.
- **FIS is source of truth** — follow it exactly.
- **Execution discipline** — Stop-the-Line on red gates (build, tests, lint, stub, wiring, task `Verify`); iterate until green; escalate only on real external blockers. See `${CLAUDE_PLUGIN_ROOT}/references/execution-discipline.md`.
- **Automation rules** (headless-first, `--auto` / `--headless` strict mode, `--auto` propagation): see [`${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). Exec-spec-specific `BLOCKED:` triggers: missing/unreadable FIS, FIS contradiction with no defensible implementation, unsafe external action.
- **Direct execution** — implement the code yourself. Sub-agents are for advisory work, review, and validation only.
- **Surgical scope; surface — don't fix** — every changed line should trace to a FIS task. Clean only orphans your own changes caused (an import you made unused, a helper your refactor stranded). Pre-existing issues outside that orphan radius — including lint/analyzer warnings, dead code, typos, and small co-located bugs *inside files you touch* — go into a `NOTICED BUT NOT TOUCHING` block in the completion report; do not fix inline. Boy Scout cleanup is reserved for review/refactor skills (the `andthen:review`, `andthen:quick-review`, `andthen:refactor`, and `andthen:architecture` skills), not exec-spec. See **Workflow Rules, Guardrails and Guidelines** in the project `CLAUDE.md`.
- **Anti-rationalization** — if you catch yourself skipping test scaffolding, deferring verification, batching status updates, or pushing past a red gate, reject these common rationalizations:
  - "I'll verify after the next group" — defects compound; verify before more work builds on a bad assumption.
  - "This failing check is probably unrelated" — Stop-the-Line applies.
  - "I'll update status at the end" — deferred bookkeeping drifts from reality.
  - "I'll report this complete with a caveat" — broken is not Done. Finish it or surface a real external blocker.

### Executor Role
**You are the executor.** Your job:
- Load and understand the FIS
- Read technical research, project learnings, and ubiquitous-language guidance needed to implement accurately
- Build a quick codebase overview once at the start, then focus on the files the FIS actually touches
- Handle bounded prep inline when it improves execution quality (for example scenario-test scaffolding and optional UI contract generation)
- Implement tasks directly, in order, running each task's **Verify** line before moving on
- Mark task checkboxes immediately after each task completes
- Proactively spawn narrow advisory sub-agents when you hit genuine uncertainty
- Run validation, triage findings, and fix must-fix issues directly until all gates are green
- Ensure all status updates and gates complete before finishing

Do not: delegate coding to advisory agents, batch status updates until the end, silently narrow scope, or skip final gates.

### Proactive Sub-Agents
Spawn narrow sub-agents when they materially improve a coding decision. Their output is advisory; the FIS remains the contract.

**Agents** (pass as `subagent_type` to the Task tool):

- the `andthen:documentation-lookup` agent – unfamiliar APIs, library/framework behavior, migration details, or version-specific questions. Required path for documentation lookup. Use a fast/lightweight model (`model: "haiku"`, `gpt-5.4-mini`, or similar).
- the `andthen:research-specialist` agent – external best-practice research or context not available in the codebase
- the `andthen:visual-validation-specialist` agent – visual/design compliance against wireframes or baselines

**Skills** (invoke as `/andthen:<name>`; when you want fresh-context isolation, spawn a `general-purpose` sub-agent whose prompt runs the skill):

- the `andthen:testing` skill – test strategy, coverage assessment, test-first / red-green-refactor discipline, Prove-It bugfix flow, or unfamiliar test-harness patterns
- the `andthen:architecture` skill (`--mode advise` or `--mode trade-off`) – unresolved architectural trade-offs or integration-pattern ambiguity not settled by the FIS
- the `andthen:ui-ux-design` skill – UI layout, interaction, accessibility, or responsive-pattern advice when the FIS needs a design contract
- the `andthen:triage` skill – non-trivial build failures, dependency conflicts, or cascading test failures

For advisory analysis, use a capable reasoning model (`model: "sonnet"` or stronger, `gpt-5.4`, or similar); for retrieval and routine lookups, haiku-class is sufficient.

Usage rules:
- Prefer multiple narrow questions over one broad prompt
- Spawn early when the need appears; do not wait until you are fully blocked
- If sub-agent guidance conflicts with the FIS, follow the FIS
- Do not spawn a sub-agent for coding work you should do directly


## GOTCHAS
- **Delegating implementation to advisory sub-agents** – recreates the context-loss and serial overhead the skill is designed to avoid
- **Status updates dropped when context exhausted** – update FIS task checkboxes immediately; plan and FIS updates in Step 5 are gates
- **FIS references get stale if spec was updated** – always re-read the FIS
- **Not signaling active-story status to the `State` document when called in a plan context** – read the location from the **Project Document Index** and set "In Progress" at start
- **Treating spec size or difficulty as permission to narrow scope** – exec-spec executes the FIS it was given; if the spec should have been split, that is an upstream spec-quality problem, not a license to land a subset and stop


## WORKFLOW

### Step 1: Resolve FIS and Story Context
1. Require a local `FIS_FILE_PATH`. Stop if the argument is missing or does not resolve to a readable file.
2. Read the FIS header (lines between the H1 and the first `## ` heading) and extract `STORY_ID` from `**Story-ID**:` and `PLAN_FILE_PATH` from `**Plan**:`. These provenance fields are the authoritative source.
   - If either field is absent (0.14.x FIS without provenance): fall back to filename-prefix extraction (e.g. `s01-feature-name.md` → `S01`) and sibling-`plan.md` lookup. Emit to stdout: `WARN: FIS missing **Plan**:/**Story-ID**: provenance fields; using filename/sibling fallback (re-spec to upgrade)`. For single-feature specs not derived from a plan, leave `STORY_ID` empty.
3. Record `PLAN_FILE_PATH` for Step 5b updates when the FIS is plan-backed.

**Gate**: `FIS_FILE_PATH` exists; `STORY_ID` and `PLAN_FILE_PATH` captured when the FIS is plan-backed

### Step 2: Read and Prepare

1. Read the full FIS at _`FIS_FILE_PATH`_

**Structural integrity guard** — after reading the full FIS, verify it is well-formed before any destructive work. Apply the three conditions from [`${CLAUDE_PLUGIN_ROOT}/references/data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md) (FIS Structural Integrity Contract section):
1. `## Success Criteria` heading exists and its span contains at least one `- [ ] ` line.
2. `## Implementation Plan` heading exists and its span contains at least one task with a Verify line.
3. `## Final Validation Checklist` heading exists.

On any failure: emit `BLOCKED: <FIS_FILE_PATH> missing: <comma-separated list of failed sections>` and stop. Do not read upstream documents, do not enter Step 3.
2. Understand the sections that define execution: Success Criteria, Scenarios, Scope & Boundaries, Architecture Decision, Technical Overview, Implementation Plan, Testing Strategy, Validation, and Final Validation Checklist
3. **Process Required / Deeper Context** – the FIS's `Required Context` blocks are inlined verbatim from upstream documents at spec time and are authoritative for execution. Do not re-read their source documents just to reconfirm inlined content. `Deeper Context` pointers (`path#anchor`) are optional — read on demand only if the inlined Required Context leaves a gap. When following a Deeper Context anchor, verify it resolves in the source (any reasonable check that confirms the slug or `<a id="...">` exists) and warn (do not stop) on broken anchors.
4. **Read Technical Research** – if the FIS references a `.technical-research.md`, read it before making code changes. Treat findings as leads to verify, not facts to trust.
5. Read the `Learnings` document (see **Project Document Index**) if it exists and is relevant
6. Read the `Ubiquitous Language` document (see **Project Document Index**) if it exists and is relevant. Use canonical terms in code and avoid listed synonyms.
7. Build a quick codebase overview once at the start (`tree -d`, `git ls-files | head -250`), then stop broad discovery and focus on the files/tasks the FIS actually touches
8. If the FIS has **Scenarios** and/or **Testing Strategy**, scaffold the minimum high-signal scenario-test skeletons inline using nearby test patterns. When practical, confirm they fail before implementation. If the test harness is still unclear after one bounded pass, note the skip and continue.
9. If the FIS has UI work and no adequate design contract is already referenced, create a short `.agent_temp/ui-spec-{feature-name}.md` covering spacing, typography, color, component patterns, and responsive breakpoints. Source from FIS → project design system → UX guidelines → reasonable defaults.
10. **Update project state** (if the `State` document exists in the location defined by the **Project Document Index** and the FIS originated from a plan): restore story context from `STORY_ID` and mark it as the active story.
11. Initialize working notes you will maintain during the run:
   - Per-task status
   - `changed-files`
   - Any `CONFUSION`, `NOTICED BUT NOT TOUCHING`, or `MISSING REQUIREMENT` items

### Step 3: Implement
Implement the FIS yourself, task by task, in the order listed.

For each task:
1. Implement the outcome described
2. Run the task's **Verify** line before proceeding to the next task
3. **If Verify fails**: remediate the current task before advancing. Do not mark the task complete or advance while Verify is red. Raise `CONFUSION` / `MISSING REQUIREMENT` if the FIS itself is the problem.
4. For tasks with paired scenario tests, drive them red → green when practical
5. Honor prescriptive details exactly: column names, format strings, error messages, file paths, UI control names, and similar contract-level details
6. Update `changed-files`
7. Mark the task checkbox complete immediately in the FIS — do not batch checkbox updates
8. Record the task result in your working notes

Implementation rules:
- When stuck, emit named output blocks instead of guessing:
  - `CONFUSION:` — the FIS is ambiguous and you cannot safely proceed. State the ambiguity, list labeled options, ask `-> Which approach?`
  - `NOTICED BUT NOT TOUCHING:` — out-of-scope observations. List issues, ask `-> Want me to create tasks?`
  - `MISSING REQUIREMENT:` — a task assumes something absent. State what is undefined, list labeled options, ask `-> Which behavior?`
  Each is a labeled block with concrete choices and an arrow-prompt for the user.
- In `AUTO_MODE`, do not use arrow prompts. Choose the safest FIS-preserving option and record it as an `ASSUMPTION`; if no safe option exists, stop with `BLOCKED:` and list the minimum missing decisions.
- Spawn proactive sub-agents when the need arises, but keep ownership of the code changes locally
- If `changed-files` becomes incomplete or ambiguous, derive it from the current worktree diff before Step 4

### Step 4: Validate
Step 3 verifies task-level outcomes. Step 4 catches cross-cutting issues — integration, security, architectural coherence, and spec drift — that can still survive per-task Verify lines.

#### 4a. Direct Checks
1. **Build**: run the project's applicable build/package checks; every available build step relevant to the feature must succeed
2. **Tests**: run the applicable test suites; all relevant tests must pass (or pre-existing failures documented)
3. **Lint/types**: run the applicable static analysis checks; no new violations introduced by your changes. Pre-existing violations inside `changed-files` are surfaced under `NOTICED BUT NOT TOUCHING`, not fixed inline (surgical scope — Core Rules).
4. **Stub detection**: grep `changed-files` for incomplete-implementation markers (`TODO`, `FIXME`, `XXX`, `NotImplementedError`, language-appropriate `pass`/empty-body/`throw.*not implemented` patterns). Triage each hit — intentional (e.g. a `pass` in an abstract stub) vs. forgotten — and remediate the forgotten ones.
5. **Wiring check**: for each new file in `changed-files`, confirm at least one other file imports or references it (language-appropriate import/require/include grep on the basename or module path). Isolated new files are a Stop-the-Line signal unless the FIS explicitly justifies them.
6. **Spec compliance spot-check**: extract prescriptive details from the FIS (output format strings, column name lists, file paths for new artifacts, exact error messages, UI elements like buttons/controls) and grep/verify each against the implementation — any mismatch is a remediation input
7. **Tautology check**: for each test added or modified in `changed-files`, inspect the test source — the unit under test must be imported and called without being replaced by a mock/stub; assertions must reference its return value or an observable effect, not mock call arguments; fixtures must not substitute for the production computation (captured golden outputs are fine). A test that would still pass if the asserted behavior were removed is tautological and is a remediation input.

#### 4b. Code Review (mandatory fresh-context review)
Run the `andthen:review` **skill** with `--mode code` for independent fresh-context review covering: static analysis, linting, formatting, type checking, code quality, architecture, security, domain language, stub detection, wiring verification, and simplification opportunities (unnecessary complexity, duplication, over-abstraction introduced during implementation). Prefer to invoke it in a fresh-context sub-agent: spawn a `general-purpose` sub-agent whose prompt runs `/andthen:review --mode code`. Do not pass `andthen:review` as `subagent_type` — it is a skill, not an agent type.

#### 4c. Visual Validation (if UI)
Spawn the `andthen:visual-validation-specialist` **agent** per any Visual Validation Workflow defined in CLAUDE.md.

Steps 4b and 4c can run in parallel.

#### 4d. Remediation

Apply the Gate Classes policy from `${CLAUDE_PLUGIN_ROOT}/references/execution-discipline.md`.

1. **Collect** — combine required failures from 4a with findings from 4b/4c. A failed build/test/lint/stub/wiring check is a remediation input even if the code review does not flag it separately.
2. **Triage** — severity scale: CRITICAL/HIGH must fix, MEDIUM should fix, LOW optional.
3. **Objective red gates (4a)** — iterate until green, invoking the `andthen:triage` skill when iteration stalls.
4. **Subjective findings (4b/4c)** — one pass on CRITICAL/HIGH, re-run the affected lens (`/andthen:review --mode code` or visual validation) on the touched scope; escalate if they persist.

### Step 5: Complete
All substeps below are gates — complete them before finishing.

#### 5a. Verify Completion
Lightweight gate – uses Step 4a results, does not re-run checks:
1. Verify all success criteria met
2. Verify all task checkboxes marked (catch any missed from Step 3)
3. Verify Final Validation Checklist items satisfied
4. Collect verification evidence from Step 4a: **Build** (exit code/status), **Tests** (pass/fail counts), **Linting/types** (error/warning counts); add **Visual validation** and **Runtime** for UI/runtime stories

#### 5b. Update FIS, Source Plan, and Project State

Status writes are gates, not bookkeeping. Run each substep in order, then verify before reporting completion. Do not collapse this into a single hand-wave invocation — the failure mode for this step is _silent partial execution at end of context_.

1. **FIS** (always) — invoke the `andthen:ops` skill: `update-fis {FIS_FILE_PATH} all`. Marks task checkboxes, success criteria, and Final Validation Checklist items in one pass.

2. **Source plan** (plan-backed FIS only; **skip if `DEFER_SHARED_WRITES=true`** — defer to orchestrator):
   - `andthen:ops update-plan {PLAN_FILE_PATH} {STORY_ID} Done` — sets the story's Status field, Story Catalog row, and acceptance-criteria checkboxes.
   - If the plan story row's FIS field is *unset* (empty / `–` / placeholder) or *stale* (path differs from `{FIS_FILE_PATH}` after path normalization): `andthen:ops update-plan {PLAN_FILE_PATH} {STORY_ID} fis "{FIS_FILE_PATH}"`.

3. **State document** (if it exists per **Project Document Index**; **skip if `DEFER_SHARED_WRITES=true`** — defer to orchestrator):
   - `andthen:ops update-state active-story {STORY_ID} Done` — removes the story from Active Stories.
   - `andthen:ops update-state note "{one-line completion summary}"`.

4. **Verify** — re-read each updated file:
   - **FIS**: every task checkbox `[x]`; Final Validation Checklist `[x]`; success criteria `[x]`.
   - **Plan** (if 5b.2 ran): story row `Done`; acceptance criteria `[x]`; FIS field set.
   - **State** (if 5b.3 ran): story absent from Active Stories.
   - Any miss → retry the matching `update-*` once. Persistent failure is Stop-the-Line — do not report completion on missing writes.

5. **Deferred shared writes** — when `DEFER_SHARED_WRITES=true` (typically under `/andthen:exec-plan --team --worktree`), substeps 2 and 3 are deferred so concurrent stories in a wave do not conflict on `plan.md` / `State` document during merge. Skip those invocations and emit this **audit block** in the completion report:

   ```
   ## Deferred Shared Writes (worktree mode)
   Story: {STORY_ID}
   Plan: {PLAN_FILE_PATH}
   FIS: {FIS_FILE_PATH}
   Completion summary: {one-line completion summary}
   ```

   Substitute literal values before emitting. The block is an **audit record and summary source** — the orchestrator constructs the actual `andthen:ops update-*` invocations from these values plus its own knowledge of single-repo vs multi-repo layout, and applies them post-merge (see `andthen:exec-plan` Step 3T Merge Wave). Do not emit a list of `andthen:ops` lines as the consumption format; the orchestrator does not parse it that way.

   Substeps 1 and 4's FIS verification still run in-worktree (FIS is story-local and merges cleanly).

   **Standalone use** (no orchestrator above): the audit block tells the user what to apply. After committing FIS changes, the user runs the same writes the orchestrator would: `andthen:ops update-plan {PLAN_FILE_PATH} {STORY_ID} Done`; if the plan story row's FIS field is unset or stale, `andthen:ops update-plan {PLAN_FILE_PATH} {STORY_ID} fis "{FIS_FILE_PATH}"`; `andthen:ops update-state active-story {STORY_ID} Done`; and `andthen:ops update-state note "{one-line completion summary}"`. Standalone `--defer-shared-writes` is intended only for users who explicitly want this deferral; do not set it without one.


#### 5c. Completion Report
Report: per-task status, files created/modified, verification evidence, any unresolved low-priority issues or `NOTICED BUT NOT TOUCHING` items.

## Post-Completion
If the `Learnings` document (see **Project Document Index**) exists, capture story-level traps, domain knowledge, procedural knowledge, and error patterns. Organize by topic, not chronology. Keep entries brief (1-2 sentences). Do not create a new `Learnings` document unless one already exists.

> FIS checkbox/status updates and plan updates are handled in Step 5 — they are gates, not post-completion tasks.
