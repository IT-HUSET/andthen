---
description: Use when the user wants to execute a fully-specced implementation plan bundle. Runs a fixed pipeline per story (exec-spec + quick-review) and a final gap review on the whole plan. Requires a plan bundle where every story already has a FIS. Supports Agent Teams (--team) and sub-agents (portable fallback). Trigger on 'execute this plan', 'implement this plan', 'run the plan', 'execute with agents', 'run as team'.
argument-hint: "[--team] [--worktree] [--from-issue <number>] [--to-pr <number>] [--auto|--headless] <path-to-plan-directory> [path-to-code-repo]"
---

# Execute Plan

## VARIABLES

PLAN_DIR: $ARGUMENTS first positional argument (strip any flag tokens like `--team`, `--worktree`, `--from-issue`, `--to-pr`, `--auto`, or `--headless` before interpreting the remainder as positional args). When `--from-issue <N>` is set, `PLAN_DIR` is empty and the plan source is the GitHub issue body.
CODE_DIR: second positional argument _(optional – for multi-repo setups where plan and code live in different repos)_

### Optional Flags
- `--team` → USE_TEAM: force Agent Teams mode; error if unavailable
- `--worktree` → USE_WORKTREE: enable isolated git worktrees for parallel execution (team mode only; default: `false`)
- `--from-issue <number>` → ISSUE_INPUT: Use a GitHub plan issue as input (`gh issue view <N>`). Auto-detects single-issue vs granular shape per [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md), materializes `## Technical Research` to `<run-tempdir>/.technical-research.md`, generates each story's FIS just-in-time by invoking the `andthen:spec` skill with inline-text input (single-issue: extracted from the story section in the parent body; granular: fetched via `gh issue view <story-N> --json body` from the linked story issue), then runs the existing per-story exec-spec + quick-review pipeline against the materialized FIS. Posts shape-appropriate closure comments after Step 5. **Mutually exclusive with `--team`** (parallel JIT FIS generation is not supported under this flag) — reject with `BLOCKED: --from-issue is mutually exclusive with --team` in `AUTO_MODE`; warn and stop in default mode.
- `--to-pr <number>` → PUBLISH_PR: after Step 5 Final Verification, post the existing rolled-up completion summary plus final gap verdict as a PR comment via `gh pr comment <number> --body-file <summary-path>`. No new content generation. Composes with `--from-issue <N>` (the same flag works whether the plan came from a local directory or a GitHub issue). See Step 5 Publish to PR sub-step.
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts

## INSTRUCTIONS

Require `PLAN_DIR`. Stop if missing. **You are the orchestrator.** Parse the plan, run the per-story pipeline (`exec-spec` → `quick-review` per story, then one final `review --mode gap`), verify writes landed, handle phase transitions, manage failures, run final verification. Delegate story code to `exec-spec` (sub-agent, teammate, or sequential fallback); take over locally if a story returns partial or non-green.

### Rules
- **Plan is source of truth** – follow phase ordering, dependencies, and parallel markers exactly. Every story's `**FIS**` field must point at an existing file (FIS-unset sentinel: [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md)); abort if missing — no auto-recovery.
- **Execution discipline and authoritative status writes** — see [`execution-discipline.md`](${CLAUDE_PLUGIN_ROOT}/references/execution-discipline.md). `exec-spec` Step 5b is the per-story status write; sub-agents and teammates do not additionally call `andthen:ops update-*`. The orchestrator writes cross-story state and repair writes only.
- **Automation rules** — see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). `BLOCKED:` triggers: invalid inputs, unrepairable red gates, missing execution tools, unsafe external actions.
- **Status updates are gates** – plan and FIS checkpoint updates block the next phase; do not defer.
- Not updating the `State` document (see **Project Document Index**) when phases transition or blockers are discovered is a common miss.


## WORKFLOW

### Step 1: Parse Plan

> **When `--from-issue <N>` is set**: load `references/from-issue-mode.md` for the flag-combination guard, plan-issue body fetch and shape detection, technical-research materialization, and execution-plan parsing. The local-directory flow below is skipped in favor of the issue-body parse; the FIS-existence check (item 5) is skipped because FIS files are generated just-in-time in Step 3.

1. **Resolve CODE_DIR** _(skip if `--team` not set and no second positional arg)_:
   - If provided: verify git repository, resolve to absolute path
   - If not provided: auto-detect from PLAN_DIR's git root (when set) vs CWD's git root. Same repo → use that root. Different repos → use CWD's git root.
   - Resolve `BASE_BRANCH`: `git -C {CODE_DIR} rev-parse --abbrev-ref HEAD`

2. **Load session state** – Read the `State` document (see **Project Document Index**; default: `docs/STATE.md`) if it exists. Extract session continuity notes, active stories, blockers, and current phase.

3. Read `PLAN_DIR/plan.md` _(local-directory mode)_. If missing, stop — a valid plan artifact is required upstream (typically from the `andthen:plan` skill).
4. Extract stories (ID, name, scope, acceptance criteria, dependencies), phases, parallel markers `[P]`, dependency graph, and wave assignments (W1, W2, W3...)
5. **Verify FIS files exist** _(local-directory mode only; skipped under `--from-issue` per `references/from-issue-mode.md`)_: every story's `**FIS**` field must (a) not match the FIS-unset sentinel per [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md) and (b) point at an existing file. If any story fails this check, abort with: `Plan bundle has stories with missing FIS — run /andthen:plan {PLAN_DIR} to fill them (plan is resumable).` Do not proceed (same in `--auto` mode — no auto-recovery). Status field values are not gated here; that is bookkeeping per the data contract, not a runtime precondition.
6. Build execution plan respecting phase ordering and dependency chains

**Gate**: Plan parsed (from local `plan.md` or fetched issue body); in local mode FIS files exist on disk; phases identified


### Step 2: Determine Execution Mode

**Pre-validate flag combinations**: `--worktree` requires `--team` (worktree isolation is a team-mode feature; sub-agent mode runs sequentially in the orchestrator's CWD and has no worktrees to merge). If `USE_WORKTREE=true` and `USE_TEAM=false`, stop. In default mode, inform the user that `--worktree` is only meaningful with `--team` and ask whether to proceed with `--team` added or drop `--worktree`. In `AUTO_MODE`, emit `BLOCKED: --worktree requires --team` and exit.

Check whether Agent Teams are available by verifying that team creation tools exist (e.g. `TeamCreate`).

- **`--team` AND available** → Team mode (Step 3T)
- **`--team` AND unavailable** → stop. In default mode, inform the user it requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`; in `AUTO_MODE`, emit `BLOCKED: Agent Teams unavailable (requires CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1)` and exit.
- **No `--team`** → Sub-agent mode (Step 3). Mention `--team` is available if the user wants team execution, unless `AUTO_MODE=true`.

**Gate**: Execution mode determined


### Step 3: Phase Loop

For each phase in the plan:

#### 3a. Phase Transition

**Update project state** (if the `State` document exists; see **Project Document Index**): invoke the `andthen:ops` skill with `update-state phase "{Phase N}: {phase_name}"` and `update-state status "On Track"`.

FIS files were verified to exist in Step 1, item 5. Re-read `plan.md` if any status updates from a prior phase may have landed during execution.

**Gate**: Phase context loaded, `plan.md` current

#### 3b. Execute Story Pipelines

> **JIT FIS layer** _(only when `--from-issue` is set)_: load `references/from-issue-mode.md` for the per-story FIS materialization recipe (story-body extraction, temp-file invocation form, and the `andthen:spec` failure policy). Once the FIS path is captured, fall through to the standard per-story pipeline below using that path as `{fis_path}`.

**Per-story pipeline** (one FIS per story, so each story gets its own exec-spec + quick-review run):
1. **Implement**: `/andthen:exec-spec {fis_path}`
2. **Review**: `/andthen:quick-review` on the story's changes

**Wave-based execution**: W1 in parallel (via sub-agents), then W2, etc. Fall back to sequential in-orchestrator execution if sub-agents are unavailable or delegated execution stalls / returns partial / non-green.

Compose the per-story sub-agent prompt by substituting the canonical **Per-Story Worker Prompt** block (see bottom of this file) with `{MODE}=default` and overrides:
- `{STORY_ID}` = the story's plan identifier (e.g. `S03`)
- `{FIS_PATH}` = absolute path to the story's FIS
- `{PLAN_PATH}` = absolute path to `PLAN_DIR/plan.md`
- `{BASE_BRANCH}` = resolved at run start
- Apply `--auto` propagation per `${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md` when `AUTO_MODE=true`

**Model assignment**: Use a capable coding model (`model: "sonnet"`, `gpt-5.3-codex`, or similar).

#### 3c. Verify Green, Confirm Writes Landed (**Gate**)

Run immediately after each story — not as a batch. Worker self-reports do not count.

**Green gate**: build clean, targeted tests pass, lint/types clean, no broken intermediate state. Fail → Stop-the-Line per `${CLAUDE_PLUGIN_ROOT}/references/execution-discipline.md`; repair locally, re-delegate, or invoke the `andthen:triage` skill; iterate until green.

Pass → run the **Writes-Landed Checklist** below. This is a structured re-read, not a glance. Outside this repair path and Post-Completion bookkeeping, the orchestrator does not write story-level status.

**Writes-Landed Checklist** (per story just completed):

- [ ] **FIS** — open the FIS at `{fis_path}`. Every task checkbox is `[x]`. Final Validation Checklist items are `[x]`. Success criteria are `[x]`.
- [ ] **Plan story row** — open `plan.md`. The Story Catalog row for `{story_id}` shows status `Done`.
- [ ] **Plan story section** — the story's section header field shows `**Status**: Done`. `**FIS**` field points at the correct path. Acceptance criteria checkboxes are all `[x]`.
- [ ] **State document** (if it exists per **Project Document Index**) — `{story_id}` is no longer in the Active Stories table.

Missing item → call the matching `andthen:ops update-*` once to repair, then re-read that item only. Persistent miss after one repair pass is Stop-the-Line — do not advance the wave on unverified status.

**Re-delegation** (remediation via sub-agent): compose the per-story sub-agent prompt by substituting the canonical **Per-Story Worker Prompt** block with `{MODE}=re-delegation` and overrides:
- `{STORY_ID}`, `{FIS_PATH}`, `{PLAN_PATH}`, `{BASE_BRANCH}` as above
- `{REVIEW_FINDINGS_PATH}` = path to prior review findings
- Add a `Failure list:` section with the specific failures before the main prompt block

**Gate**: All stories in current phase verified green and their plan.md + FIS writes confirmed (or repaired)

**Gate**: All phases complete.


### Step 3T: Phase Loop (Team Mode)

> **This step replaces Step 3 when `--team` is active.** Steps 4–6 are shared.

Load `references/team-mode-orchestration.md` for the full orchestration content (team setup, implementer/reviewer prompts, task management, merge wave, status updates gate, monitoring, and Final Worktree Teardown).

For each phase: update project state (same as Step 3a), then create and manage the Agent Team pipeline per `team-mode-orchestration.md`. The bundle is already fully specced — no per-phase spec generation step.

**Gate**: All phases complete.


### Step 4: Final Review

Spawn a sub-agent with fresh context (the orchestrator is biased by construction context). **Model**: use a strong reasoning model (`model: "opus"`, `gpt-5.4`, or similar) — gap review is cross-cutting, not routine pattern-matching.

Resolve `PLAN_DIR` and `CODE_DIR` to absolute paths before composing the prompt. Compose by substituting the canonical **Per-Story Worker Prompt** block (bottom of this file) with `{MODE}=final-review` and overrides:
- `{PLAN_PATH}` = `PLAN_DIR_ABS/plan.md`; `{CODE_DIR_ABS}` = resolved absolute code directory
- `{STORY_ID}` and `{FIS_PATH}` empty/omitted; apply `--auto` propagation when `AUTO_MODE=true`

Verify the sub-agent returned both a verdict and a readable report path. If either is missing: `BLOCKED: final gap review returned malformed output` in `AUTO_MODE`; stop in default mode.

If the verdict is FAIL: invoke `/andthen:remediate-findings {absolute_report_path}` in the orchestrator (not a sub-agent). Scope narrowly to gap report findings. Escalate if issues persist after one remediation pass.

**Gate**: Final gap review complete

### Step 5: Final Verification

Run build, run tests, review cross-story integration. Include verification evidence: **Build** (exit code/status), **Tests** (pass/fail counts), **Linting/types** (error/warning counts).

**Gate**: Build, tests, integration pass

#### 5b. Publish to PR _(only when `--to-pr <number>`)_

After Final Verification has passed, post the rolled-up summary (per-story completion + final gap verdict from Step 4) per **Pattern B** in [`github-publish.md`](${CLAUDE_PLUGIN_ROOT}/references/github-publish.md). Summary temp file: `.agent_temp/exec-plan-completion-{plan-slug}.md` — in `--from-issue` mode where `PLAN_DIR` is empty, `{plan-slug}` resolves to `issue-<N>` (full path: `.agent_temp/exec-plan-completion-issue-<N>.md`).

**Failure-handling override of Pattern B (only when `--from-issue` is also set)**: on `gh` failure here, record the error verbatim and **continue to Step 5c** so issue-side closure still runs — skipping it on a PR-side failure would leave granular story issues unclosed. Surface in the final completion report as `BLOCKED: gh pr comment failed for #<number>` (recorded but non-fatal at this step).

When `--from-issue` is NOT set, Pattern B's default applies: surface the `gh` error verbatim and stop. There is no Step 5c to protect, so the override would silently mask a transport failure as success — fall through to the default stop.

**Gate**: PR comment posted (default `--to-pr` only); or PR comment posted / surfaced as deferred failure with Step 5c continuing (when `--from-issue` is also set)

#### 5c. Issue Closure Comments _(only when `--from-issue <N>` was set)_

Load `references/from-issue-mode.md` for the shape-appropriate closure protocol — single-issue posts N+1 comments on the plan issue; granular uses the deliberate comment-then-close 2-call pattern per story plus a rolled-up summary on the plan issue. Use the existing per-story completion summaries (already produced by `andthen:exec-spec` Step 5c) and the rolled-up plan summary (Step 5).

**Gate**: Closure comments posted per shape (or skipped when `--from-issue` is absent)

## FAILURE HANDLING

- **Story pipeline fails / non-green** → Stop-the-Line per `${CLAUDE_PLUGIN_ROOT}/references/execution-discipline.md`; iterate until green; escalate only on real external blockers.
- **Final review fails** → one remediation pass (subjective-finding policy); escalate if issues persist
- **Dependent stories blocked** when predecessor fails; **>50% of a phase fails** → pause and return a failure summary
- **Update the `State` document on failure** (see **Project Document Index**): `update-state status "At Risk"` or `"Blocked"`
- **Always run Final Worktree Teardown before exiting** (see `references/team-mode-orchestration.md`), including failure exits — unmerged worktrees are preserved and listed in the failure summary.

## Per-Story Worker Prompt

Single canonical prompt template for all per-story sub-agent invocation sites. Placeholders:
- `{STORY_ID}` – story identifier from plan (e.g. `S03`)
- `{FIS_PATH}` – absolute path to the story's FIS file
- `{PLAN_PATH}` – absolute path to `plan.md`
- `{BASE_BRANCH}` – git branch resolved at run start
- `{MODE}` – one of `default` / `team` / `re-delegation` / `final-review`
- `{WORKTREE_PATH}` – resolved worktree path (team mode only)
- `{REVIEW_FINDINGS_PATH}` – path to prior review findings (re-delegation only)
- `{AUTO_SUFFIX}` – `" --auto"` when `AUTO_MODE=true`, else `""` (team mode; pre-substituted per Team Setup)
- `{WORKTREE_SUFFIX}` – `" --defer-shared-writes"` when `USE_WORKTREE=true`, else `""` (team mode; pre-substituted per Team Setup)
- `{CODE_DIR_ABS}` – resolved absolute path to the code repository (final-review mode)

For the no-double-write contract, see `${CLAUDE_PLUGIN_ROOT}/references/execution-discipline.md`.

**Modes `default` / `team` / `re-delegation`** (per-story execution):
```
Story {STORY_ID} | Mode: {MODE}
Plan: {PLAN_PATH} | FIS: {FIS_PATH}

1. /andthen:exec-spec {FIS_PATH}
2. /andthen:quick-review on the changes

Run `/andthen:exec-spec` — its Step 5b writes this story's status.
For the no-double-write contract, see execution-discipline.md.

Report:
- Step results (success/failure), files changed
- exec-spec Step 4a numbers (build, tests, lint/type-check, format)
- Any issues, incomplete work, or non-green state — be explicit
```

**Mode `final-review`** (whole-plan gap review; `{STORY_ID}` and `{FIS_PATH}` are empty/omitted):
```
Mode: final-review
Plan: {PLAN_PATH} | Implementation: {CODE_DIR_ABS}

Run /andthen:review --mode gap {PLAN_PATH}

Do NOT pass --inline-findings — the final gap gate must write a report file
so remediate-findings can consume it.

Report back:
1. The verdict (PASS/FAIL) from the canonical gap verdict table
2. The absolute path to the written report file
```



## COMPLETION

Print summary: stories completed, total phases, execution mode, review/verification results, path to `PLAN_DIR/plan.md`.

## Post-Completion

Update the `State` document (see **Project Document Index**): set phase/status; mark completed stories `Done`; add session continuity note. If the `Learnings` document exists, capture cross-story insights, traps, and error patterns (brief, by topic; do not create if none exists).
