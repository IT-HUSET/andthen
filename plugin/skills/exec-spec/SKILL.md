---
description: Use when the user wants to execute or implement an existing spec or FIS. Implements code from a Feature Implementation Specification. Trigger on 'execute this spec', 'execute this FIS', 'implement this spec', 'implement this FIS', 'build from spec'.
argument-hint: "[--auto|--headless] [--tdd] [--defer-shared-writes] [--to-pr <number>] <path-to-fis>"
---

# Execute Feature Implementation Specification

Execute a fully-defined FIS document as the **executor**. Implement the FIS directly, use sub-agents only for narrow advisory/review work, and complete all validation and status gates before finishing.

## VARIABLES
FIS_FILE_PATH: $ARGUMENTS (strip any flag tokens like `--auto`, `--headless`, `--tdd`, `--defer-shared-writes`, or `--to-pr` before interpreting the remainder as the FIS path)

### Optional Flags
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts
- `--tdd` → TDD_MODE: strict TDD execution mode. Scaffold exactly one scenario test, observe it fail, drive red→green→refactor, then advance to the next scenario. The TDD canon — Anti-Cheat Invariant, Living Test List, Horizontal Slicing as Anti-Pattern, red→green→refactor discipline — is owned by the `andthen:testing` skill; load it via `/andthen:testing --mode tdd` (or the Skill tool) for canon depth, but the executor remains the test author — this is canon consultation, not delegation of test writing. `AUTO_MODE` honors `--tdd` without confirmation gates. Default off; opt in for logic-heavy or bug-mode FISes.
- `--defer-shared-writes` → DEFER_SHARED_WRITES: skip direct `plan.md` and `State` document writes (FIS writes still run); emit a `## Deferred Shared Writes (worktree mode)` audit block in the completion report instead. Set automatically by `andthen:exec-plan --team --worktree` to prevent concurrent worktree merges from colliding on shared files. Intended for orchestrated use — see Step 5b.5 for emission format and standalone-use details.
- `--to-pr <number>` → PUBLISH_PR: after Step 5b status writes succeed, post the existing completion summary (the report produced by Step 5c) as a PR comment via `gh pr comment <number> --body-file <summary-path>`. No new content generation — the comment body is the local summary verbatim. Explicit number only; no auto-detect from the current branch. See Step 5d for emission details.


## INSTRUCTIONS

### Core Rules
- Require `FIS_FILE_PATH`. Stop if missing.
- **Complete implementation** — reporting incomplete work with a caveat is **not** completion.
- **FIS is source of truth** — follow it exactly.
- **Execution discipline** — Stop-the-Line on red gates (build, tests, lint, stub, wiring, task `Verify`); iterate until green; escalate only on real external blockers. See `${CLAUDE_PLUGIN_ROOT}/references/execution-discipline.md`.
- **Automation rules** (headless-first, `--auto` / `--headless` strict mode, `--auto` propagation): see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). Exec-spec-specific `BLOCKED:` triggers: missing/unreadable FIS, FIS contradiction with no defensible implementation, unsafe external action.
- **Direct execution** — implement the code yourself. Sub-agents are for advisory work, review, and validation only.
- **Surgical scope; surface — don't fix** — every changed line should trace to a FIS task. Clean only orphans your own changes caused (an import you made unused, a helper your refactor stranded). Pre-existing issues outside that orphan radius — including lint/analyzer warnings, dead code, typos, and small co-located bugs *inside files you touch* — go into a `NOTICED BUT NOT TOUCHING` block in working notes during the run, are persisted to the FIS's `## Implementation Observations` section at completion (Step 5b), and are surfaced as a brief pointer (not a full duplicate) from the completion report; do not fix inline. Boy Scout cleanup is reserved for review/refactor skills (the `andthen:review`, `andthen:quick-review`, `andthen:refactor`, and `andthen:architecture` skills), not exec-spec. See **Workflow Rules, Guardrails and Guidelines** in the project `CLAUDE.md`.
- **Anti-rationalization** — reject rationalizations for skipping test scaffolding, deferring verification, batching status updates, or pushing past a red gate (e.g. *"I'll verify after the next group"*, *"this failing check is unrelated"*, *"I'll batch status updates at the end"*, *"completing with a caveat is fine"*). Broken is not Done; Stop-the-Line applies.

### Proactive Sub-Agents
Spawn narrow sub-agents when they materially improve a coding decision. Their output is advisory; the FIS remains the contract.

**Documentation lookup and research**:

- For unfamiliar APIs, library/framework behavior, migration details, or version-specific questions, spawn a sub-agent that consults the project's `## Documentation Lookup Tools` section in `CLAUDE.md` / `AGENTS.md`. Claude Code plugin users may invoke the `andthen:documentation-lookup` agent directly for the same behavior.
- For external best-practice research or context not available in the codebase, do research in a sub-agent. Prefer official sources and separate evidence from inference.

**Skills** (invoke as `/andthen:<name>`; when you want fresh-context isolation, spawn a sub-agent whose prompt runs the skill):

- the `andthen:testing` skill – test strategy, coverage assessment, test-first / red-green-refactor discipline, Prove-It bugfix flow, or unfamiliar test-harness patterns
- the `andthen:architecture` skill (`--mode advise` or `--mode trade-off`) – unresolved architectural trade-offs or integration-pattern ambiguity not settled by the FIS
- the `andthen:ui-ux-design` skill – UI layout, interaction, accessibility, or responsive-pattern advice when the FIS needs a design contract
- the `andthen:visual-validation` skill – visual/design compliance against wireframes, screenshots, or baselines
- the `andthen:triage` skill – non-trivial build failures, dependency conflicts, or cascading test failures

For advisory analysis, use a capable reasoning model (`model: "sonnet"` or stronger, `gpt-5.4`, or similar); for retrieval and routine lookups, haiku-class is sufficient.

Usage rules:
- Prefer multiple narrow questions over one broad prompt
- Spawn early when the need appears; do not wait until you are fully blocked
- If sub-agent guidance conflicts with the FIS, follow the FIS
- Do not spawn a sub-agent for coding work you should do directly


## GOTCHAS
- **Treating spec size or difficulty as permission to narrow scope** – exec-spec executes the FIS it was given; if the spec should have been split, that is an upstream spec-quality problem, not a license to land a subset and stop


## WORKFLOW

### Step 1: Resolve FIS and Story Context
1. Require a local `FIS_FILE_PATH`. Stop if the argument is missing or does not resolve to a readable file.
2. Read the FIS header (lines between the H1 and the first `## ` heading) and extract `STORY_ID` from `**Story-ID**:` and `PLAN_FILE_PATH` from `**Plan**:`. These provenance fields are the authoritative source.
   - If either field is absent (older FIS without provenance fields): fall back to filename-prefix extraction (e.g. `s01-feature-name.md` → `S01`) and sibling-`plan.md` lookup. Emit to stdout: `WARN: FIS missing **Plan**:/**Story-ID**: provenance fields; using filename/sibling fallback (re-spec to upgrade)`. For single-feature specs not derived from a plan, leave `STORY_ID` empty.
3. Record `PLAN_FILE_PATH` for Step 5b updates when the FIS is plan-backed.

**Gate**: `FIS_FILE_PATH` exists; `STORY_ID` and `PLAN_FILE_PATH` captured when the FIS is plan-backed

### Step 2: Read and Prepare

1. Read the full FIS at `FIS_FILE_PATH`.

2. **Structural integrity guard** — verify the FIS is well-formed before any destructive work. Apply the three conditions from [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md) (FIS Structural Integrity Contract section):
   - `## Success Criteria` heading exists and its span contains at least one `- [ ] ` line.
   - `## Implementation Plan` heading exists and its span contains at least one task with a Verify line.
   - `## Final Validation Checklist` heading exists.

   On any failure: emit `BLOCKED: <FIS_FILE_PATH> missing: <comma-separated list of failed sections>` and stop. Do not read upstream documents, do not enter Step 3.

3. Understand the sections that define execution: Success Criteria, Scenarios, Scope & Boundaries, Architecture Decision, Technical Overview, Implementation Plan, Testing Strategy, Validation, and Final Validation Checklist.

4. **Process Required / Deeper Context** — the FIS's `Required Context` blocks are inlined verbatim from upstream documents at spec time and are authoritative for execution; do not re-read source documents just to reconfirm inlined content. `Deeper Context` pointers (`path#anchor`) are optional — read on demand only if the inlined Required Context leaves a gap. When following a Deeper Context anchor, verify it resolves in the source and warn (do not stop) on broken anchors.

5. **Read Technical Research** — if the FIS references a `.technical-research.md`, read it before making code changes. Treat findings as leads to verify, not facts to trust.

6. Read the `Learnings` document (see **Project Document Index**) if it exists and is relevant.

7. Read the `Ubiquitous Language` document (see **Project Document Index**) if it exists and is relevant. Use canonical terms in code and avoid listed synonyms.

8. Read the `Key Dev Commands` document (see **Project Document Index**; default: `docs/KEY_DEVELOPMENT_COMMANDS.md`) if it exists. It is the canonical source for build, format, lint/type-check, test, and run commands. Use these whenever a FIS task `Verify` line does not already specify the command. If the document is missing, fall back to discovery and language / tech stack conventions.

9. Build a quick codebase overview once (`tree -d`, `git ls-files | head -250`), then stop broad discovery and focus on the files the FIS actually touches.

10. **Scaffold scenario tests** — if the FIS has **Scenarios** and/or **Testing Strategy**, scaffold the minimum high-signal scenario-test skeletons inline using nearby test patterns. When `TDD_MODE=true`, scaffold exactly one scenario test, observe it fail for the right reason, then proceed to Step 3 for that scenario only. When practical, confirm tests fail before implementation. If the test harness is unclear after one bounded pass, note the skip and continue.

11. **UI design contract** — if the FIS has UI work and no adequate design contract is already referenced, create a short `.agent_temp/ui-spec-{feature-name}.md` covering spacing, typography, color, component patterns, and responsive breakpoints. Source from FIS → project design system → UX guidelines → reasonable defaults.

12. **Update project state** (if the `State` document exists per **Project Document Index** and the FIS originated from a plan): restore story context from `STORY_ID` and mark it as the active story.

13. Initialize working notes you will maintain during the run:
    - Per-task status
    - `changed-files`
    - Any `CONFUSION`, `NOTICED BUT NOT TOUCHING`, `MISSING REQUIREMENT`, `DISCOVERED REQUIREMENT`, or AUTO_MODE `ASSUMPTION` items

### Step 3: Implement
Implement the FIS yourself, task by task, in the order listed.

When `TDD_MODE=true`, run every scenario-bearing task as a strict red→green→refactor loop; load `/andthen:testing --mode tdd` (or `--mode prove-it` for bug-fix tasks) for canon depth — the `--tdd` flag definition above carries the full description.

For each task:
1. Implement the outcome described
2. Run the task's **Verify** line before proceeding to the next task
3. **If Verify fails**: remediate the current task before advancing. Do not mark the task complete or advance while Verify is red. Raise `CONFUSION` / `MISSING REQUIREMENT` if the FIS itself is the problem.
4. For tasks with paired scenario tests, drive them red → green when practical
5. Honor prescriptive details exactly: column names, format strings, error messages, file paths, UI control names, and similar contract-level details
6. Update `changed-files`
7. Mark the task checkbox complete immediately in the FIS — do not batch checkbox updates
8. Record the task result in your working notes

#### Traceability Gate: Requirement-Anchored Implementation

Every test and motivated source-code change must trace to a requirement already present in the FIS or appended through the sanctioned Discovered Requirements path. Apply these friction tiers:

- **Tier A — free pass**: Tidy First refactors, helper extractions transitively traced through a parent test, renames, formatting, and type-narrowing need no extra note when behavior is unchanged.
- **Tier B — inline trace**: each new test names the scenario or success-criterion ID it satisfies via test name, comment, or task report line; each new code path is motivated by a currently-failing test.
- **Tier C — stop-and-amend**: discovered edge cases, failure modes, or scenario ambiguities must be appended through the `andthen:ops` skill's `update-fis <path> discovered-requirements <body>` form before writing the test or code that addresses them. Mark the entry persisted in working notes only after `update-fis` returns success — Step 5b's catch-up pass relies on the unpersisted-list being truthful. For regression-style discoveries (a defect surfaced mid-run, not a missing edge case), follow the Prove-It path: the first dependent test pins the defect and stays as a regression guard.

On `BLOCKED: invalid discovered-requirements body` from this op, reformat per the ops skill's body constraints and retry once. Persistent failure: do not write the dependent test or code (Tier C's "append before dependent change" temporal invariant). Surface as `CONFUSION` (interactive) or `BLOCKED:` in the completion report (`AUTO_MODE`).

For Tier C in `AUTO_MODE`, pick the conservative interpretation, append the discovered requirement with rationale, write the test traced to that appended requirement, implement, and surface the full Discovered Requirements block in the completion report.

Implementation rules:
- When stuck, emit named output blocks per [`execution-named-blocks.md`](${CLAUDE_PLUGIN_ROOT}/references/execution-named-blocks.md): `CONFUSION:` → `-> Which approach?`, `NOTICED BUT NOT TOUCHING:` → `-> Want me to create tasks?`, `MISSING REQUIREMENT:` → `-> Which behavior?`. Under `AUTO_MODE`, see the reference's AUTO_MODE Override section.
- Spawn proactive sub-agents when the need arises, but keep ownership of the code changes locally
- If `changed-files` becomes incomplete or ambiguous, derive it from the current worktree diff before Step 4

### Step 4: Validate
Step 3 verifies task-level outcomes. Step 4 catches cross-cutting issues — integration, security, architectural coherence, and spec drift — that can still survive per-task Verify lines.

#### 4a. Direct Checks
Use the canonical commands from the `Key Dev Commands` document (read in Step 2.8) for build/format/lint/type-check/test invocations below; if the document was not present, the discovery fallback from Step 2.8 stands. The per-task `Verify` lines (Step 3.2) drive Step 3's inner-loop checks; 4a runs the cross-cutting project-wide pass *in addition* (per the Step 4 framing above), not instead.

1. **Build**: run the project's applicable build/package checks; every available build step relevant to the feature must succeed
2. **Tests**: run the applicable test suites; all relevant tests must pass (or pre-existing failures documented)
3. **Lint/types**: run the applicable static analysis checks; no new violations introduced by your changes. Pre-existing violations inside `changed-files` are surfaced under `NOTICED BUT NOT TOUCHING`, not fixed inline (surgical scope — Core Rules).
4. **Format**: prefer a formatter *check* mode (e.g. `prettier --check`, `ruff format --check`, `gofmt -l`) over a write mode so pre-existing formatting drift in `changed-files` does not get bundled into the diff. Treat any *new* formatting violations introduced by your edits as remediation inputs; surface pre-existing drift on touched files under `NOTICED BUT NOT TOUCHING` (surgical scope — Core Rules), not as inline fixes. Never run a project-wide format pass. When formatter and linter overlap (e.g. `ruff format` + `ruff check`), running both is fine.
5. **Stub detection**: grep `changed-files` for incomplete-implementation markers (`TODO`, `FIXME`, `XXX`, `NotImplementedError`, language-appropriate `pass`/empty-body/`throw.*not implemented` patterns). Triage each hit — intentional (e.g. a `pass` in an abstract stub) vs. forgotten — and remediate the forgotten ones.
6. **Wiring check**: for each new file in `changed-files`, confirm at least one other file imports or references it (language-appropriate import/require/include grep on the basename or module path). Isolated new files are a Stop-the-Line signal unless the FIS explicitly justifies them.
7. **Spec compliance spot-check**: extract prescriptive details from the FIS (output format strings, column name lists, file paths for new artifacts, exact error messages, UI elements like buttons/controls) and grep/verify each against the implementation — any mismatch is a remediation input
8. **Tautology check**: for each test added or modified in `changed-files`, inspect the test source — the unit under test must be imported and called without being replaced by a mock/stub; assertions must reference its return value or an observable effect, not mock call arguments; fixtures must not substitute for the production computation (captured golden outputs are fine). A test that would still pass if the asserted behavior were removed is tautological and is a remediation input.

#### 4b. Code Review (mandatory fresh-context review)
Run the `andthen:review` **skill** with `--mode code` for independent fresh-context review covering: static analysis, linting, formatting, type checking, code quality, architecture, security, domain language, stub detection, wiring verification, and simplification opportunities (unnecessary complexity, duplication, over-abstraction introduced during implementation). Prefer to invoke it in a fresh-context sub-agent: spawn a sub-agent whose prompt runs `/andthen:review --mode code`. Do not pass `andthen:review` as `subagent_type` — it is a skill, not an agent type.

#### 4c. Visual Validation (if UI)
Invoke the `andthen:visual-validation` **skill** in a sub-agent per any Visual Validation Workflow defined in CLAUDE.md.

Steps 4b and 4c can run in parallel.

#### 4d. Remediation

Apply the Gate Classes policy from `${CLAUDE_PLUGIN_ROOT}/references/execution-discipline.md`.

1. **Collect** — combine required failures from 4a with findings from 4b/4c. A failed build/test/lint/format/stub/wiring check is a remediation input even if the code review does not flag it separately.
2. **Triage** — severity scale: CRITICAL/HIGH must fix, MEDIUM should fix, LOW optional.
3. **Objective red gates (4a)** — iterate until green, invoking the `andthen:triage` skill when iteration stalls.
4. **Subjective findings (4b/4c)** — one pass on CRITICAL/HIGH, re-run the affected lens (`/andthen:review --mode code` or visual validation) on the touched scope; escalate if they persist.

### Step 5: Complete
All substeps below are gates — complete them before finishing.

#### 5b. Update FIS, Source Plan, and Project State

Status writes are gates, not bookkeeping. Run each substep in order, then verify before reporting completion. Do not collapse this into a single hand-wave invocation — the failure mode for this step is _silent partial execution at end of context_.

1. **FIS** (always) — invoke the `andthen:ops` skill:
   - `update-fis {FIS_FILE_PATH} all` — Marks task checkboxes, success criteria, and Final Validation Checklist items in one pass.
   - **Persist observations** (if any): if working notes contain `NOTICED BUT NOT TOUCHING` items or AUTO_MODE `ASSUMPTION` records, format them as a markdown body with `#### NOTICED BUT NOT TOUCHING` and/or `#### ASSUMPTIONS (AUTO_MODE)` subsections (each item one line, file:line if applicable), then invoke `update-fis {FIS_FILE_PATH} observations '{body}'`. Skip when both lists are empty. The ops skill appends a timestamped `### Run:` block to the FIS's `## Implementation Observations` section (creating the section if absent).
   - **Persist Discovered Requirements** (if any remain unpersisted): Tier C normally appends before dependent tests/code in Step 3. If working notes still contain unpersisted Discovered Requirements entries, format them as a markdown body with a `#### DISCOVERED REQUIREMENTS` subsection using the FIS template entry shape, then invoke `update-fis {FIS_FILE_PATH} discovered-requirements '{body}'`. Skip when the unpersisted list is empty.

2. **Source plan** (plan-backed FIS only; **skip if `DEFER_SHARED_WRITES=true`** — defer to orchestrator):
   - `andthen:ops update-plan {PLAN_FILE_PATH} {STORY_ID} Done` — sets the story's Status field, Story Catalog row, and acceptance-criteria checkboxes.
   - If the plan story row's FIS field is *unset* (empty / `–` / placeholder) or *stale* (path differs from `{FIS_FILE_PATH}` after path normalization): `andthen:ops update-plan {PLAN_FILE_PATH} {STORY_ID} fis "{FIS_FILE_PATH}"`.

3. **State document** (if it exists per **Project Document Index**; **skip if `DEFER_SHARED_WRITES=true`** — defer to orchestrator):
   - `andthen:ops update-state active-story {STORY_ID} Done` — removes the story from Active Stories.
   - `andthen:ops update-state note "{one-line completion summary}"`.

4. **Verify** — re-read each updated file:
   - **FIS**: every task checkbox `[x]`; Final Validation Checklist `[x]`; success criteria `[x]`. If observations or Discovered Requirements were persisted, the `## Implementation Observations` section contains a new `### Run:` block dated to this run.
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

   **Standalone use** (no orchestrator above): the audit block tells the user what to apply — after committing FIS changes, run the same `andthen:ops update-plan` and `update-state` calls listed in 5b.2 and 5b.3. Standalone `--defer-shared-writes` is intended only for users who explicitly want this deferral; do not set it without one.


#### 5c. Completion Report
**Gate** (uses Step 4a results, does not re-run checks): verify all success criteria met, all task checkboxes marked, and Final Validation Checklist items satisfied.

Report: per-task status, files created/modified, verification evidence — **Build** (exit code/status), **Tests** (pass/fail counts), **Linting/types** (error/warning counts), **Format** (clean/violations); add **Visual validation** and **Runtime** for UI/runtime stories — and a brief summary of any persisted observations or Discovered Requirements. Full `NOTICED BUT NOT TOUCHING`, `ASSUMPTIONS`, and Discovered Requirements details live in the FIS's `## Implementation Observations` section (written in Step 5b.1) — reference the section, duplicating only the full Discovered Requirements block when `AUTO_MODE` Tier C required it.

#### 5d. Publish to PR _(only when `--to-pr <number>`)_

After Step 5b status writes have verified, post the Step 5c completion summary per **Pattern B** in [`github-publish.md`](${CLAUDE_PLUGIN_ROOT}/references/github-publish.md). Summary temp file: `.agent_temp/exec-spec-completion-{STORY_ID-or-feature-slug}.md`. Pattern B's default failure handling applies (surface and stop).

**Gate**: PR comment posted (or skipped when `--to-pr` is absent)

## Post-Completion
If the `Learnings` document (see **Project Document Index**) exists, capture story-level traps, domain knowledge, procedural knowledge, and error patterns. Organize by topic, not chronology. Keep entries brief (1-2 sentences). Do not create a new `Learnings` document unless one already exists.
