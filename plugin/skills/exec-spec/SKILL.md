---
description: Use when the user wants to execute or implement an existing spec or FIS. Implements code from a Feature Implementation Specification. Trigger on 'execute this spec', 'execute this FIS', 'implement this spec', 'implement this FIS', 'build from spec'.
argument-hint: "[--auto] [--tdd] [--defer-shared-writes] [--to-pr <number>] <path-to-fis>"
---

# Execute Feature Implementation Specification

## VARIABLES
FIS_FILE_PATH: $ARGUMENTS (strip any flag tokens like `--auto`, `--headless`, `--tdd`, `--defer-shared-writes`, or `--to-pr` before interpreting the remainder as the FIS path)

### Optional Flags
- `--auto` → AUTO_MODE: automation-safe execution with no conversational prompts
- `--tdd` → TDD_MODE: strict TDD execution mode. Scaffold exactly one scenario test, observe it fail, drive red→green→refactor, then advance to the next scenario. The executor remains the test author. TDD canon is owned by the `andthen:testing` skill – load `/andthen:testing --mode tdd` for depth. `AUTO_MODE` honors `--tdd` without confirmation gates. Default off; opt in for logic-heavy or bug-mode FISes.
- `--defer-shared-writes` → DEFER_SHARED_WRITES (boolean; default `false`; immutable for the run):
  - **`true`**: skip all shared-status writes (`plan.json` + `State`); see each Step 5b/4d substep for which writes it gates. FIS writes (5b.1) still run; emit the `## Deferred Shared Writes` audit block (5b.5) for the caller to apply.
  - **`false`** (standalone default): run the shared writes (5b = success, 4d = failure blocker). Mirrors `andthen:exec-plan`'s per-story/phase-boundary writes so standalone use keeps plan/State consistent. No audit block.
  - Auto-propagated to `true` by `andthen:exec-plan --team --worktree` (avoids concurrent worktree-merge collisions) and `--from-issue` (orchestrator owns the local `plan.json`). Standalone: set only when you deliberately want deferral (see Step 5b.5 standalone-use note).
- `--to-pr <number>` → PUBLISH_PR: after the Step 5c completion-presentation gate passes, post the Step 5c summary verbatim as a PR comment via `gh pr comment <number> --body-file <summary-path>`. Explicit number only; no auto-detect. See Step 5d.


## INSTRUCTIONS

### Core Rules
- Read project rules and guidelines (`CLAUDE.md` / `AGENTS.md` and referenced files) before starting.
- Require `FIS_FILE_PATH`. Stop if missing.
- **Complete implementation** – finish the work.
- **FIS is source of truth** – follow it exactly.
- **Preflight is recommended, not required** – a prior `andthen:preflight` pass (which drives blocking decisions to zero and honors `spec-ready`) reduces mid-run forks, but exec-spec never hard-depends on it: an interactive gate cannot be a precondition of a headless run without risking deadlock. Execute the FIS as given whether or not preflight ran.
- **Execution discipline** – Stop-the-Line on red gates (build, tests, lint, stub, wiring, task `Verify`); iterate until green; escalate only on real external blockers. See [`execution-discipline.md`](${CLAUDE_PLUGIN_ROOT}/references/execution-discipline.md) (referenced below as *The Execution-Discipline Rules*).
- **Automation rules** (headless-first, `--auto` strict mode, `--auto` propagation): see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). Exec-spec-specific `BLOCKED:` triggers: missing/unreadable FIS, FIS contradiction with no defensible implementation, unsafe external action.
- **Retry-safe dirty worktrees** – classify pre-existing dirty paths before editing; never discard unrelated edits. See Step 2.3 for the operational taxonomy.
- **Direct execution** – implement code yourself. Sub-agents are advisory/review only.
- **Surgical scope; surface – don't fix** – every changed line traces to a FIS task. Clean only orphans your own changes caused. Pre-existing issues go into `NOTICED BUT NOT TOUCHING` during the run, persist to `## Implementation Observations` in Step 5b, and pointer from the completion report. Boy Scout cleanup is reserved for review/cleanup/remediation skills, not exec-spec.
- **Anti-rationalization** – reject rationalizations for skipping test scaffolding, deferring verification, batching status updates, or pushing past a red gate (*"I'll verify after the next group"*, *"this failing check is unrelated"*, *"completing with a caveat is fine"*). Broken is not Done.

### Proactive Sub-Agents
Spawn narrow sub-agents when they materially improve a coding decision. Output is advisory; the FIS remains the contract.

**Documentation lookup, research, and reconnaissance**:

- External API/library docs are **not** pre-resolved at spec time. Spawn a documentation-lookup sub-agent for unfamiliar API surface, library/framework behavior, migration details, or version-specific questions – do not pause and ask. The sub-agent consults `## Documentation Lookup Tools` in `CLAUDE.md` / `AGENTS.md`, or invoke the dedicated `documentation-lookup` agent when available.
- For external best-practice research, use a sub-agent. Prefer official sources; separate evidence from inference.
- **Codebase reconnaissance**: when the FIS leaves the read-set unpinned in a large or unfamiliar neighborhood, spawn an Explore (or general-purpose) sub-agent per work area to map callers, callees, conventions, and invariants – returning a distilled brief (signatures, traps, idioms), not file dumps.

**Skills** (invoke as `/andthen:<name>`; for fresh-context isolation, spawn a sub-agent whose prompt runs the skill):

- the `andthen:testing` skill – test strategy, coverage, TDD / red-green-refactor, Prove-It bugfix flow, unfamiliar test-harness patterns
- the `andthen:architecture` skill in `--mode trade-off` for unresolved trade-offs with concrete competing options; `--mode advise` for open design/integration-pattern ambiguity without crystallized options
- the `andthen:ui-ux-design` skill – UI layout, interaction, accessibility, responsive patterns
- the `andthen:visual-validation` skill – visual/design compliance against wireframes, screenshots, baselines
- the `andthen:triage` skill – non-trivial build failures, dependency conflicts, cascading test failures

Sub-agents inherit the session model; use **medium** effort for advisory analysis, **low** for retrieval.

Rules:
- Prefer multiple narrow questions over one broad prompt, spawned early – do not wait until fully blocked
- If sub-agent guidance conflicts with the FIS, follow the FIS
- Do not spawn a sub-agent for coding work you should do directly


## GOTCHAS
- **Treating spec size or difficulty as permission to narrow scope** – exec-spec executes the FIS it was given; if the spec should have been split, that is an upstream spec-quality problem, not a license to land a subset and stop


## WORKFLOW

### Step 1: Resolve FIS and Story Context
1. Require a local `FIS_FILE_PATH`. Stop if missing or unreadable.
2. Read the FIS header (lines between the H1 and the first `## ` heading) and extract `STORY_ID` from `**Story-ID**:` and `PLAN_FILE_PATH` from `**Plan**:`. These provenance fields are authoritative.
   - **Legacy / missing provenance fields**: when `**Plan**:` points at legacy plan.md or `**Story-ID**:`/`**Plan**:` are absent, follow the recovery branch in [`exec-spec-legacy-fis.md`](references/exec-spec-legacy-fis.md) (sibling-json preference, filename fallback, `WARN:`/`BLOCKED:` emissions).
3. Record `PLAN_FILE_PATH` for Step 5b updates when plan-backed.
   - **`github://issue/<N>` provenance**: no on-disk `plan.json`. With `DEFER_SHARED_WRITES=true`, proceed (Step 5b.2 skips). With `DEFER_SHARED_WRITES=false`, stop with `BLOCKED: FIS provenance points at github://issue/<N>; no local plan.json to update. Re-invoke with --defer-shared-writes, or supply a materialized plan.json path explicitly.`

**Gate**: `FIS_FILE_PATH` exists; `STORY_ID` and `PLAN_FILE_PATH` captured when plan-backed

### Step 2: Read and Prepare

1. Read the full FIS at `FIS_FILE_PATH`.

2. **Sanity check** – if the file at `FIS_FILE_PATH` isn't an executable FIS (wrong artifact type, no actionable content), stop: surface `CONFUSION: <FIS_FILE_PATH> not an executable FIS – <one-line reason>` interactively, emit `BLOCKED:` with the same content in `AUTO_MODE`. Do not enter Step 3.

3. **Classify pre-existing dirty paths** (`git status --porcelain`) before scaffolding, state writes, or code edits:
   - Clean: record `BASELINE_DIRTY=none`.
   - Clearly FIS-owned: treat as retry context; in `AUTO_MODE`, record `ASSUMPTION: resuming existing edits for {STORY_ID}`.
   - Unrelated: record `BASELINE_DIRTY=<paths>`; preserve and exclude from `changed-files`.
   - Ambiguous overlap: stop before editing. In `AUTO_MODE`, emit `BLOCKED: dirty worktree overlaps {STORY_ID}: <paths>`; otherwise surface `CONFUSION:`.

4. Read the FIS's execution-defining sections; the **Feature Overview and Goal** (Intent + Expected Outcomes) is the in-FIS intent anchor. Template-empty sections mean standard handling applies.

   **Intent as in-FIS tie-breaker** – when a scenario or task is ambiguous, its tagged Expected Outcome(s) resolve ambiguity in favor of the named success condition before raising `CONFUSION:`. For *behavioral* tasks, walk the indirection: scenarios whose `[TI<NN>]` includes the task → those scenarios' `[OC<NN>]` tags → matching Expected Outcomes. For *structural* tasks (no scenario tags it; its Verify line proves a Structural Criterion), the resolving anchor is the matched Structural Criterion's text. If the resolving outcome/criterion is itself ambiguous, raise `CONFUSION:` – do not guess. The tie-breaker resolves *referent* ambiguity, not *text* ambiguity.

   **Legacy-FIS notice**: when no `**Expected Outcomes**:` sub-block exists under `## Feature Overview and Goal`, emit `WARN: FIS predates Expected Outcomes; in-FIS tie-breaker inactive (re-spec to upgrade).` Execution proceeds; the in-FIS tie-breaker and Step 5a upper-chain attestation are silent no-ops.

5. **Process Required / Deeper Context** – `Required Context` blocks are authoritative; do not re-read source documents to reconfirm. `Deeper Context` pointers (`path#anchor`) are optional, on-demand reads when Required Context has gaps. Verify each followed anchor resolves; warn (do not stop) on broken anchors.

6. Read these when present/relevant (see **Project Document Index**): `Learnings`; `Ubiquitous Language` – use canonical terms, avoid listed synonyms; `Architecture` – when the FIS touches structural or cross-component code (Required Context stays authoritative for execution; Architecture is the system-shape baseline). Build a quick codebase overview once (`tree -d`, `git ls-files | head -250`), then focus on the files the FIS touches.

7. Read the `Key Dev Commands` document (default: `docs/KEY_DEVELOPMENT_COMMANDS.md`) – canonical source for build, format, lint/type-check, test, run commands. Use these whenever a Verify line does not specify its own. If missing, fall back to discovery and language conventions.

8. **Scaffold scenario tests** – if the FIS has Acceptance Scenarios, scaffold minimum high-signal scenario-test skeletons using nearby test patterns. When `TDD_MODE=true`, scaffold exactly one scenario test, observe it fail for the right reason, then proceed to Step 3 for that scenario only. When practical, confirm tests fail before implementation. If the test harness is unclear after one bounded pass, note the skip and continue.

9. **UI design contract** – if the FIS has UI work and no adequate design contract is referenced, create a short `.agent_temp/ui-spec-{feature-name}.md` covering spacing, typography, color, component patterns, responsive breakpoints. Source: FIS → design system → UX guidelines → defaults.

10. **Update project state** (if `State` exists, FIS is plan-backed, and `DEFER_SHARED_WRITES=false`): restore story context from `STORY_ID` and mark active. When deferred, the orchestrator owns shared status surfaces.

11. Initialize working notes:
    - Per-task status
    - `changed-files`
    - Pre-existing dirty baseline classification, if any
    - Any `CONFUSION`, `NOTICED BUT NOT TOUCHING`, `MISSING REQUIREMENT`, `DISCOVERED REQUIREMENT`, or AUTO_MODE `ASSUMPTION` items

### Step 3: Implement
Implement the FIS yourself, task by task, in the order listed.

When `TDD_MODE=true`, run every scenario-bearing task as a strict red→green→refactor loop; load `/andthen:testing --mode tdd` (or `--mode prove-it` for bug-fix tasks) for canon depth – the `--tdd` flag definition above carries the full description.

For each task:
1. Implement the outcome described; update `changed-files` and record the result in working notes.
2. Run the task's **Verify** line before advancing.
3. **If Verify fails**: remediate the current task before advancing. Do not mark complete or advance while Verify is red. Raise `CONFUSION` / `MISSING REQUIREMENT` if the FIS itself is the problem.
4. For tasks with paired scenario tests, drive them red → green when practical
5. Honor prescriptive details exactly: column names, format strings, error messages, file paths, UI control names, and similar contract-level details
6. Mark the task checkbox complete immediately in the FIS – do not batch checkbox updates

#### Traceability Gate: Requirement-Anchored Implementation

Every test and motivated source-code change must trace to an existing FIS requirement or one appended through Discovered Requirements. Friction tiers:

- **Tier A – free pass**: behavior-unchanged changes traced through a parent test (Tidy First refactors, renames, formatting, type-narrowing) need no extra note.
- **Tier B – inline trace**: each new test names the Acceptance Scenario ID or Structural Criterion it satisfies via test name, comment, or task report line; each new code path is motivated by a currently-failing test.
- **Tier C – stop-and-amend**: discovered edge cases, failure modes, or scenario ambiguities are appended via `andthen:ops update-fis <path> discovered-requirements <body>` *before* the dependent test or code lands. Mark the entry persisted in working notes only after `update-fis` returns success – Step 5b's catch-up pass relies on the unpersisted-list being truthful. For regression-style discoveries (defect surfaced mid-run), follow Prove-It: the first dependent test pins the defect and stays as a regression guard.

On `BLOCKED: invalid discovered-requirements body`, reformat per ops body constraints and retry once. Persistent failure: do not write the dependent test or code (Tier C's "append before dependent change" temporal invariant). Surface as `CONFUSION` (interactive) or `BLOCKED:` in the completion report (`AUTO_MODE`).

In `AUTO_MODE` Tier C: pick the conservative interpretation, append with rationale, write the test traced to the appended requirement, implement, surface the full Discovered Requirements block in the completion report.

**Design-change amendment path** – when execution reveals the correct approach legitimately changes the FIS Intent or scenario mechanism, do not hide the pivot in Discovered Requirements or ship divergent code. Stop, record an ADR via the `andthen:architecture` skill in `--mode trade-off`, amend the affected Intent/scenario through the `andthen:ops` skill's `update-fis <path> design-change <body>` form, then re-run the relevant Verify line(s) and Chain Attestation. Design pivots only; missing requirements still use Tier-C Discovered Requirements before dependent tests or code. In `AUTO_MODE`, do not auto-rewrite the Intent – that re-creates the silent drift this path exists to prevent; emit `BLOCKED:` with the proposed pivot and the required ADR in the completion report for human reconcile (never an interactive wait).

**Reconciliation-ledger write** – when a `design-change` (or a Tier-C `discovered-requirements`) amendment leaves a *named upstream document* stale – a PRD section, sibling FIS, public doc, or a missing ADR – call the `andthen:ops` skill `update-ledger add <ledger-path> <stable-id> <class> <stale-targets> <source-run>` – where `<ledger-path>` is the ledger adjacent to this FIS (`{fis-without-ext}.reconciliation-ledger.md`) – to record an OPEN entry naming the stale target(s), per [`reconciliation-ledger.md`](${CLAUDE_PLUGIN_ROOT}/references/reconciliation-ledger.md) (`design-changed` for a pivot, `spec-stale` for a discovered requirement that contradicts upstream). The entry is what makes the pivot durable so review stops re-discovering it. **AUTO_MODE ordering is load-bearing**: when the pivot itself emits `BLOCKED:`, write the OPEN ledger entry *first* (the entry-write precedes the `BLOCKED:` emit) so a deferred pivot is recorded rather than lost. The common-case flow (no drift, no amendment) writes no ledger entry and gains no new gates.

Implementation rules:
- When stuck, emit named output blocks per [`execution-named-blocks.md`](${CLAUDE_PLUGIN_ROOT}/references/execution-named-blocks.md): `CONFUSION:` → `-> Which approach?`, `NOTICED BUT NOT TOUCHING:` → `-> Want me to create tasks?`, `MISSING REQUIREMENT:` → `-> Which behavior?`. `AUTO_MODE`: see reference's AUTO_MODE Override.
- Spawn proactive sub-agents for advisory work; retain code ownership.
- If `changed-files` is incomplete/ambiguous, derive from the worktree diff before Step 4, subtracting `BASELINE_DIRTY`.

### Step 4: Validate
Step 3 verifies task-level outcomes. Step 4 catches cross-cutting issues – integration, security, architectural coherence, spec drift – that survive per-task Verify lines.

#### 4a. Direct Checks
Use canonical commands from `Key Dev Commands` (Step 2.7); if absent, the discovery fallback from Step 2.7 stands. Per-task `Verify` lines drive Step 3's inner loop; 4a is the *additional* cross-cutting project-wide pass.

1. **Build**: every applicable build/package step succeeds.
2. **Tests**: all relevant tests pass (or pre-existing failures documented).
3. **Lint/types**: no new violations from your changes. Pre-existing violations inside `changed-files` surface under `NOTICED BUT NOT TOUCHING`.
4. **Format**: prefer formatter *check* mode (`prettier --check`, `ruff format --check`, `gofmt -l`) so pre-existing drift in `changed-files` is not bundled. New violations are remediation inputs; pre-existing drift on touched files surfaces under `NOTICED BUT NOT TOUCHING`. Never run a project-wide format pass. Formatter + linter overlap (e.g. `ruff format` + `ruff check`) is fine.
5. **Stub detection**: grep `changed-files` for incomplete-implementation markers (`TODO`, `FIXME`, `XXX`, `NotImplementedError`, language-appropriate `pass`/empty-body/`throw.*not implemented`). Triage intentional vs. forgotten; remediate forgotten.
6. **Wiring check**: for each new file in `changed-files`, confirm ≥1 other file imports/references it. Isolated new files are Stop-the-Line unless the FIS justifies them.
7. **Spec compliance spot-check**: grep each prescribed detail from the FIS (format strings, column lists, file paths for new artifacts, exact error messages, UI elements) against the implementation – any mismatch is a remediation input.
8. **Tautology check**: for each test added/modified, the unit under test must be imported and called (not replaced by a mock); assertions must reference its return value or observable effect, not mock call arguments; fixtures must not substitute for the production computation (golden outputs are fine). Tests that pass with the asserted behavior removed are tautological – remediation input.

#### 4b. Code Review (mandatory fresh-context review)
Invoke the `andthen:review` **skill** with `--mode code,gap` for independent review: `code` runs the static-analysis/quality/security/wiring/simplification lens; `gap` is the independent falsifier for the self-attested Step 5a gate, comparing the implementation against the FIS Intent + Expected Outcomes. Prefer a fresh-context sub-agent whose prompt runs `/andthen:review --mode code,gap {FIS_FILE_PATH} {changed-files}`.

#### 4c. Visual Validation (if UI)
Invoke the `andthen:visual-validation` **skill** in a sub-agent per any Visual Validation Workflow in `CLAUDE.md` / `AGENTS.md`.

4b and 4c can run in parallel.

#### 4d. Remediation

Apply Gate Classes from *The Execution-Discipline Rules*.

1. **Collect** – combine 4a required failures with 4b/4c findings. A failed build/test/lint/format/stub/wiring check is a remediation input even if not separately flagged in review.
2. **Review class/routing gate** – apply `Class:` and `Routing:` to 4b/4c findings before severity remediation. `code-defect` follows normal remediation below. `spec-stale` / `design-changed` do not enter code remediation; Stop-the-Line into the design-change amendment path above. `ambiguous-intent` blocks for human reconcile – `CONFUSION` interactive, or `BLOCKED:` in the completion report under `AUTO_MODE` (never a silent wait). `Routing: Note` findings are surfaced but never auto-remediated by exec-spec.
3. **Triage code-remediation findings** – apply the Gate Classes from *The Execution-Discipline Rules* to `code-defect` severity.
4. **Objective red gates (4a)** – iterate until green; invoke `andthen:triage` when iteration stalls.
5. **Subjective code-defect findings (4b/4c)** – one pass on CRITICAL/HIGH, re-run the affected lens on touched scope; escalate if they persist.

If any gate, Acceptance Scenario, or Structural Criterion stays red after repair, do not mark completion.

**Persistent-failure State writes** (plan-backed FIS; State exists; **skip if `DEFER_SHARED_WRITES=true`**):
1. `andthen:ops update-state blocker "{STORY_ID}: exec-spec persistent-failure"` – stable description so Step 5b.3's "Clear prior blocker" can match on a later successful re-run. Failure detail lives in the Failed Story Report, not the blocker text.
2. Apply the **Plan-level status derivation rule** (see [`exec-spec-status-writes.md`](references/exec-spec-status-writes.md)) and write via `andthen:ops update-state status "{derived}"`.

The story's `plan.json` status is unchanged – the bundled flow goes `spec-ready → done` directly, so failed stories stay at their pre-run status. The blocker entry carries the failure signal.

In `AUTO_MODE`, emit `BLOCKED: exec-spec failed {STORY_ID-or-FIS_FILE_PATH}` plus `## Failed Story Report` with Story/FIS, failing gates, verification evidence, changed files, preserved partial-work location.

### Step 5: Complete
All substeps are gates. Chain Attestation (5a) is a proof gate and runs **before** any status writes – `andthen:ops update-fis` and the plan/state writes in 5b are append-only, so a failed attestation after writes leaves the FIS/plan/State green-on-paper, problem-in-prose.

#### 5a. Chain Attestation gate

Walk Intent → Outcomes → Scenarios → Tasks backwards and articulate each link with evidence. The named principle is **Chain Attestation**: a frontier model that has to put words to each link cannot easily fake it. Articulation IS the gate.

One line of evidence-anchored prose per link – not a checkbox flip:
- **Task → Scenario** (behavioral tasks): for each behavioral `TI<NN>` (referenced by ≥1 scenario `[TI<NN>]` tag), name the scenario(s) it evidences and confirm those scenario tests are green (file:test-name or behavioral assertion). Task Verify passing is necessary but not sufficient – the tagged scenario must also exercise the outcome. **Structural/setup tasks** (no scenario tag; task's Verify proves a Structural Criterion) attest differently: name the Structural Criterion this task proves (matched by Verify-line text against criterion text; no syntactic suffix required) and confirm the Verify command passes. Do not force-fit a structural task into a fake scenario. Any task fitting neither category is an orphan and Stop-the-Line. Any Structural Criterion with no proving task is also Stop-the-Line.
- **Scenario → Outcome**: for each scenario, name how its Given/When/Then exercises the `[OC<NN>]` tag(s) – the *user-observable* success condition, not an internal proxy. If the Intent names a mechanism (LLM/agent turn, specific algorithm, external call, or equivalent), confirm that the implementation actually exercises that Intent-named mechanism; an outcome satisfied through a different mechanism does **not** attest and is Stop-the-Line until reconciled by fixing the code or using the design-change amendment path. Mock/tautology-driven scenario passes cannot attest outcomes (overlaps Step 4a #8 Tautology check; named here at the chain level).
- **Outcome → Intent**: for each Expected Outcome, name the passing scenarios that collectively prove it and confirm it serves the Intent in `## Feature Overview and Goal`.

Legacy FIS without `[OC<NN>]` tags degrade gracefully: attest Task → Scenario only (plus structural-task branch), and note "FIS lacks outcome anchors – upper-chain attestation skipped". Narrower coverage, not failure.

Orphan tasks – behavioral `TI<NN>` referenced by no scenario tag and no Structural Criterion Verify line – are **Stop-the-Line**. Any other un-evidenced link is also Stop-the-Line – return to Step 4d; articulate or fix.

In `AUTO_MODE`, persistent attestation failure follows the Failed Story Report path: emit `BLOCKED: exec-spec attestation failed {STORY_ID-or-FIS_FILE_PATH}` plus `## Failed Story Report` including the **partial chain articulation** (links evidenced before Stop-the-Line, and which link failed) so a downstream remediator can resume. Do not degrade to a single `Chain Attestation: FAILED` line.

Hold per-link articulation lines for the 5c report (or Failed Story Report on failure).

**Gate**: every link evidenced (or legacy-graceful note recorded); structural-task branch applied; no Stop-the-Line outstanding.

#### 5b. Update FIS, Source Plan, and Project State

Status writes are gates, not bookkeeping. Run each substep in order then verify. Do not collapse – the failure mode is _silent partial execution at end of context_.

1. **FIS** (always) – invoke the `andthen:ops` skill:
   - `update-fis {FIS_FILE_PATH} all` – marks task checkboxes, every Acceptance Scenario checkbox (canonical shape per fis-authoring-guidelines.md), every Structural Criteria checkbox, and Final Validation Checklist items (when present) in one pass.
   - **Persist observations**: when working notes hold `NOTICED BUT NOT TOUCHING` items or AUTO_MODE `ASSUMPTION` records, format as a markdown body with `#### NOTICED BUT NOT TOUCHING` and/or `#### ASSUMPTIONS (AUTO_MODE)` subsections (each item one line, file:line if applicable), then invoke `update-fis {FIS_FILE_PATH} observations '{body}'`. Skip when both lists are empty. Ops appends a timestamped `### Run:` block to `## Implementation Observations` (creating the section if absent).
   - **Persist Discovered Requirements**: Tier C normally appends before dependent tests/code in Step 3. If unpersisted entries remain, format as `#### DISCOVERED REQUIREMENTS` using the FIS template shape, then `update-fis {FIS_FILE_PATH} discovered-requirements '{body}'`. Skip when empty.
   - **Reconciliation-ledger catch-up**: if a Step 3 amendment staled a named upstream doc but its OPEN ledger entry was not yet written (per the Step 3 *Reconciliation-ledger write*), write it now via `andthen:ops update-ledger add`. Skip otherwise.

2. **Source plan** (plan-backed FIS only; **skip if `DEFER_SHARED_WRITES=true`**):
   - `andthen:ops update-plan {PLAN_FILE_PATH} {STORY_ID} done` – sets `stories[].status` to `done`.
   - If the story's `fis` is `null` or differs from `{FIS_FILE_PATH}` after normalization: `andthen:ops update-plan-fis {PLAN_FILE_PATH} {STORY_ID} {FIS_FILE_PATH}`.

3. **State documents** (shared writes skipped if `DEFER_SHARED_WRITES=true`):
   - Shared `State` (only if it exists): `andthen:ops update-state active-story {STORY_ID} Done` – prunes any legacy Active-Stories row (no-op for plan-governed stories, whose view derives from `plan.json`).
   - `andthen:ops update-state note "{one-line completion summary}"` – routes to the gitignored `State (local)` document (ops auto-creates it). Per-developer, no collision risk, so it runs even under `DEFER_SHARED_WRITES=true`; the executor owns this note – the orchestrator's deferred-write replay covers shared surfaces only and never re-applies it, and in a temp worktree the file is discarded with the worktree.
   - **Clear prior blocker** (shared `State`, plan-backed, only if it exists): `andthen:ops update-state blocker remove "{STORY_ID}: exec-spec persistent-failure"`. Best-effort – ignore "not found" returns; this clears any blocker a prior failed run wrote in Step 4d so the derivation below can downgrade `"At Risk"`.
   - **Plan health** (shared `State`, plan-backed, only if it exists): apply the **Plan-level status derivation rule** (see [`exec-spec-status-writes.md`](references/exec-spec-status-writes.md)) and write via `andthen:ops update-state status "{derived}"`. Mirrors exec-plan's phase-boundary write so standalone runs keep plan-level health current.

4. **Verify** – re-read each updated file:
   - **FIS**: every task / Acceptance Scenario / Structural Criteria checkbox `[x]`; Final Validation Checklist `[x]` when present. If observations or Discovered Requirements were persisted, `## Implementation Observations` has a new `### Run:` block dated to this run.
   - **Plan** (if 5b.2 ran): the story's `status` is `"done"`; `fis` points at `{FIS_FILE_PATH}`.
   - **State** (if 5b.3 ran): story absent from Active Stories.
   - Any miss → retry the matching `update-*` once. Persistent failure is Stop-the-Line.

5. **Deferred shared writes** – when `DEFER_SHARED_WRITES=true` (typically under `/andthen:exec-plan --team --worktree` or `--from-issue`), substeps 2 and 3 are deferred so the executor does not mutate shared local status. Skip those invocations and emit this **audit block** in the completion report:

   ```
   ## Deferred Shared Writes
   Story: {STORY_ID}
   Plan: {PLAN_FILE_PATH}
   FIS: {FIS_FILE_PATH}
   Completion summary: {one-line completion summary}
   ```

   Substitute literal values. Deferred-write replay mechanics (orchestrator vs standalone, worktree post-merge vs `--from-issue`, `github://issue/<N>` handling) are in [`exec-spec-status-writes.md`](references/exec-spec-status-writes.md).

   Substeps 1 and 4's FIS verification still run in-worktree (FIS is story-local).


#### 5c. Completion Report

**Checkbox gate** (uses Step 4a results, no re-run): verify all Acceptance Scenarios, Structural Criteria, task checkboxes, and Final Validation Checklist items (when present) are `[x]`. Any miss returns to Step 4d; persistent miss in `AUTO_MODE` uses the Failed Story Report shape. Chain Attestation already passed in 5a.

**As-Built Upstream Reconciliation recommendation** _(only when this run wrote OPEN ledger entries)_: emit a recommendation block listing every OPEN ledger entry written this run and the upstream targets needing update; recommend-only, see [`reconciliation-ledger.md`](${CLAUDE_PLUGIN_ROOT}/references/reconciliation-ledger.md). Present interactively and as text in `AUTO_MODE` (never an interactive wait).

**Completion-presentation gate** (standalone use): before presenting this run as **complete/shipped**, read this FIS's adjacent ledger and refuse to present a shipped summary while any `OPEN` or `RECONCILE REQUIRED` entry exists – name the blocking entries instead. The only bypass is an explicit override reason recorded against those entries via the `andthen:ops` skill `update-ledger override-close <ledger-path> <stable-id> <reason>`. This gate is a *presentation* refusal, not a per-story status block: the Step 5b writes (FIS / plan / State – the story records its own completion) already ran and are **not** gated, since upstream reconciliation is human-owned and recommend-only. In `AUTO_MODE`, surface the refusal as `BLOCKED:` text naming the blockers (never an interactive wait); the per-story writes still stand. Under `DEFER_SHARED_WRITES=true` (orchestrated by `andthen:exec-plan`), the orchestrator owns the consolidated gate at its completion summary – skip the standalone refusal here; the orchestrator reads each story's FIS-adjacent ledger (story-local, merged with the story branch) at its own completion gate.

Report: per-task status, files created/modified, verification evidence – **Build** (exit code/status), **Tests** (pass/fail counts), **Linting/types** (error/warning counts), **Format** (clean/violations); add **Visual validation** and **Runtime** for UI/runtime stories – the **Chain Attestation** per-link articulation lines from 5a, and a brief summary of any persisted observations or Discovered Requirements. Reference `## Implementation Observations` for full `NOTICED BUT NOT TOUCHING`, `ASSUMPTIONS`, and Discovered Requirements detail – duplicating the full Discovered Requirements block only when `AUTO_MODE` Tier C required it.

#### 5d. Publish to PR _(only when `--to-pr <number>`)_

After the Step 5c completion-presentation gate passes, post the 5c summary per **Pattern B** in [`github-publish.md`](${CLAUDE_PLUGIN_ROOT}/references/github-publish.md). If the gate refuses because reconciliation is pending, do not post. Summary temp file: `.agent_temp/exec-spec-completion-{STORY_ID-or-feature-slug}.md`. Pattern B's default failure handling applies.

**Gate**: PR comment posted (or skipped when `--to-pr` absent)

## Post-Completion
Capture story-level traps, domain or procedural knowledge, and error patterns via the `andthen:ops` skill (`update-learnings add` form, brief, by topic).
