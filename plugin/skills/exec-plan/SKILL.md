---
description: Use when the user wants to execute a fully-specced implementation plan bundle. Runs a fixed pipeline per story (exec-spec + quick-review) and a final gap review on the whole plan. Requires a plan bundle where every story already has a FIS. Supports Agent Teams (--team) and sub-agents (portable fallback). Trigger on 'execute this plan', 'implement this plan', 'run the plan', 'execute with agents', 'run as team'.
argument-hint: "[--team] [--worktree] [--from-issue <number>] [--to-pr <number>] [--auto] <path-to-plan-directory> [path-to-code-repo]"
---

# Execute Plan

## VARIABLES

PLAN_DIR: $ARGUMENTS first positional argument (strip any flag tokens like `--team`, `--worktree`, `--from-issue`, `--to-pr`, `--auto`, or `--headless` before interpreting the remainder as positional args). When `--from-issue <N>` is set, `PLAN_DIR` is empty and the plan source is the GitHub issue body.
CODE_DIR: second positional argument _(optional – for multi-repo setups where plan and code live in different repos)_
PLAN_PATH: resolved in Step 1, used unchanged in Steps 3, 4, 5. Local-directory mode: `PLAN_DIR/plan.json` (absolute). `--from-issue` mode: `.agent_temp/from-issue-<N>/plan.json` (absolute) – the materialized local ledger. Do not re-derive `PLAN_DIR/plan.json` in `--from-issue` mode (`PLAN_DIR` is empty there).

### Optional Flags
- `--team` → USE_TEAM: force Agent Teams mode; error if unavailable
- `--worktree` → USE_WORKTREE: enable isolated git worktrees for parallel execution (team mode only; default: `false`)
- `--from-issue <number>` → ISSUE_INPUT: use a GitHub plan issue as input (`gh issue view <N>`). Auto-detects single-issue vs granular shape per [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md), extracts `## Shared Decisions`, `## Binding Constraints`, and the PRD source for per-story FIS context, generates each story's FIS just-in-time via `andthen:spec` with a temp story-source file, then runs the per-story exec-spec + quick-review pipeline with shared local writes deferred. Posts shape-appropriate closure comments after Step 5. **Mutually exclusive with `--team`** (parallel JIT FIS generation not supported) – reject with `BLOCKED: --from-issue is mutually exclusive with --team` in `AUTO_MODE`; warn and stop otherwise.
- `--to-pr <number>` → PUBLISH_PR: after Step 5 Final Verification, post the rolled-up completion summary + final gap verdict as a PR comment via `gh pr comment <number> --body-file <summary-path>`. Composes with `--from-issue`. See Step 5b.
- `--auto` → AUTO_MODE: automation-safe execution with no conversational prompts

## INSTRUCTIONS

Require `PLAN_DIR` unless `--from-issue <N>` is set. **You are the orchestrator** – delegate story code to a sub-agent running `exec-spec` (or a teammate under `--team`); take over in-orchestrator only as a bounded recovery path when a story returns partial/non-green. In `AUTO_MODE`, persistent failures are recorded and reported at the end.

### Rules
- Read project rules and guidelines (`CLAUDE.md` / `AGENTS.md` and referenced files) before starting.
- **Plan is source of truth** – `plan.json` per [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md). Follow phase ordering, `dependsOn`, `parallel` exactly. In local-directory mode, every schedulable story (`status` ∈ {`pending`, `spec-ready`, `in-progress`}) must carry an existing `fis`; abort otherwise – no auto-recovery. `done`/`skipped` are terminal; `blocked` is a manual escape hatch. `--from-issue` relaxes the FIS requirement (JIT generation).
- **Execution discipline** – Stop-the-Line on red gates per [`execution-discipline.md`](${CLAUDE_PLUGIN_ROOT}/references/execution-discipline.md). See **Status-Write Contract** below.
- **Automation rules** – see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md) (referenced below as *The Automation-Mode Rules*). `BLOCKED:` triggers: invalid inputs, unrepairable red gates, missing execution tools, unsafe external actions.
- **Status updates are gates** – `plan.json` is mutated only via `andthen:ops update-plan` / `update-plan-fis` (no-double-write contract; see **Status-Write Contract**).
- **Story failure containment** – see **Status-Write Contract** below (failed stories keep pre-run status; dependents recorded as `skipped`).
- **State document updates are gated** – update on phase transitions and blocker discovery (see **Project Document Index**).


### Status-Write Contract (Multi-Story Orchestration)

Orchestrator-side rules extending the universal Stop-the-Line gate.

- **Story-scoped containment** – a failed story is not `Done`, not merged as complete, and does not unblock dependents. `done` means fully green; a failed story keeps its pre-run `plan.json` status unless an explicit `andthen:ops update-plan` changes it. Dependents not attempted because an upstream dependency failed are recorded as `skipped`; never invent a status outside the enum. `AUTO_MODE`: record the failure, preserve partial work, skip dependents, continue independent stories, finish with aggregate report. In shared checkouts, continue only after preserving partial work off the active checkout and proving the checkout clean.

- **Authoritative writes (no double-write)** – `exec-spec` Step 5b writes per-story status (FIS checkboxes, `plan.json` `status`, State active-story) via `andthen:ops`. Sub-agents/teammates **do not** call `andthen:ops update-*` on top of exec-spec. The orchestrator writes cross-story state (phase transitions, overall status, session notes) plus *repair writes* when a Step 3c Writes-Landed Checklist item is missing.

- **Worktree deferral** – under `--worktree`, `exec-spec` runs with `--defer-shared-writes`: writes only the FIS (story-local) and emits a `## Deferred Shared Writes` audit block. The orchestrator constructs the `andthen:ops update-*` calls from its own `STORY_ID` / `FIS_FILE_PATH` / `PLAN_FILE_PATH` plus the audit's `Completion summary` and applies them as the **primary** write path immediately after merging that worktree.
  - Repo placement: single-repo writes land on `{BASE_BRANCH}`; multi-repo writes land in `PLAN_DIR` (committed there if it's a git repo) and leave `CODE_DIR` untouched.
  - Missing audit block → fall back to a generated `Completion summary`; log the miss, not Stop-the-Line.
  - The Writes-Landed Checklist runs *after* deferred writes; any miss → one-shot repair.


## WORKFLOW

### Step 1: Parse Plan

> **When `--from-issue <N>` is set**: load `references/from-issue-mode.md`. That reference covers the flag-combination guard, the plan-issue body fetch, shape detection, materialization of a local `plan.json` ledger at `.agent_temp/from-issue-<N>/plan.json`, and reconciliation on rerun. After materialization, this Step 1 falls through to validation against the local ledger (items 4–6 below) using the materialized path as `{PLAN_PATH}`. The FIS-existence check (item 5) is relaxed for `--from-issue` because FIS files are generated just-in-time in Step 3.

1. **Resolve CODE_DIR** _(skip if `--team` not set and no second positional arg)_:
   - Provided → verify git repo, resolve absolute path.
   - Not provided → auto-detect from PLAN_DIR's git root (when set) vs CWD's git root. Same repo → use that root. Different → CWD's git root.
   - Resolve `BASE_BRANCH = git -C {CODE_DIR} rev-parse --abbrev-ref HEAD`.
   - **Log + non-default warning** _(only when CODE_DIR was resolved)_: print `BASE_BRANCH={value}`. Resolve `DEFAULT_BRANCH` from `git symbolic-ref refs/remotes/origin/HEAD --short` (strip `origin/`), else local `main`, else local `master`. None resolve → skip the warning (no nag in repos without a clear default). When `BASE_BRANCH ≠ DEFAULT_BRANCH`: confirm in default mode; `AUTO_MODE` proceeds with `WARNING: BASE_BRANCH={value} is not the repo's default branch ({DEFAULT_BRANCH}) – all stories will land here.` Catches the silent "wrong branch" case.

2. **Load session state** – read `State` document (default: `docs/STATE.md`) if present. Extract continuity notes, active stories, blockers, current phase.

3. Read `PLAN_DIR/plan.json` _(local-directory mode)_. If only `plan.md` is present, stop with: `BLOCKED: plan.md is no longer consumed by exec-plan. Run /andthen:plan {PLAN_DIR} to migrate to plan.json (existing FIS files are preserved).` If `plan.json` is missing entirely, stop – a valid plan artifact is required upstream (the `andthen:plan` skill). Set `PLAN_PATH` to the absolute path; `--from-issue` mode materializes it via `references/from-issue-mode.md`.
4. **Validate against schema** – `schemaVersion === "1"` (else `BLOCKED: unsupported plan.json schemaVersion – re-run /andthen:plan to regenerate`). Parse error → `BLOCKED: malformed plan.json – re-run /andthen:plan`. Validate `dependsOn` closure: every element matches an `id` in `stories[]`. Unknown IDs → `BLOCKED: invalid dependency in {story_id}: "{value}" – story not in catalog`. Status must be in the closed enum.
5. **Verify FIS files exist** _(local-directory mode only; relaxed under `--from-issue`)_: every story with `status` ∈ {`pending`, `spec-ready`, `in-progress`} must carry an existing `fis`. Matches the schedulable set in item 6 (interrupted bundles abort here, not mid-pipeline). `blocked` stories are not gated (manual escape hatch). Failure: `Plan bundle has stories with missing FIS – run /andthen:plan {PLAN_DIR} to fill them (plan is resumable).` No auto-recovery in `--auto`. JIT exception → Step 3b.
6. Build the execution plan from JSON: phase ordering (`overview.phases[]`), dependency chains (`dependsOn`), wave grouping (`stories[].wave`), parallel markers. Schedulable: `stories.filter(s => s.status !== 'done' && s.status !== 'skipped' && s.status !== 'blocked' && depsSatisfied(s))`. For each `blocked` story, log `WARNING: story {id} is blocked – skipping` and record it in the ledger's `skipped` list with reason `manually blocked`.

**Gate**: Plan parsed (from local `plan.json` or materialized ledger); schema valid; in local mode FIS files exist on disk; phases identified


### Step 2: Determine Execution Mode

**Pre-validate**: `--worktree` requires `--team` (worktree isolation is team-only). `USE_WORKTREE=true` + `USE_TEAM=false`: default mode asks whether to add `--team` or drop `--worktree`; `AUTO_MODE` emits `BLOCKED: --worktree requires --team`.

Check Agent Teams availability by verifying team creation tools (e.g. `TeamCreate`).

- **`--team` + available** → Team mode (Step 3T).
- **`--team` + unavailable** → stop. Default mode informs that `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is required. `AUTO_MODE`: `BLOCKED: Agent Teams unavailable (requires CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1)`.
- **No `--team`** → Sub-agent mode (Step 3). Mention `--team` is available unless `AUTO_MODE=true`.

**Gate**: execution mode determined

Before story execution, initialize a run ledger: `completed`, `failed`, `skipped`, `blocked_by`. `plan.json` records successful `done` transitions; the ledger feeds the aggregate report.


### Step 3: Phase Loop

For each phase in the plan:

#### 3a. Phase Transition

**Update project state** (if `State` exists): `andthen:ops update-state phase "{Phase N}: {phase_name}"` and `update-state status "On Track"`.

Re-read `plan.json` (local-directory mode) or the materialized ledger (`--from-issue`).

**Gate**: phase context loaded, `plan.json` current

#### 3b. Execute Story Pipelines

> **JIT FIS layer** _(only when `--from-issue` is set)_: load `references/from-issue-mode.md` for per-story FIS materialization (story-body extraction, temp-file invocation, `andthen:spec` failure policy). The orchestrator injects `**Plan**: github://issue/<plan-N>` and `**Story-ID**: <S0N>` provenance fields into each materialized FIS – `andthen:spec`'s file-reference branch does not auto-emit them. After provenance + ledger update, fall through to the per-story pipeline below using the captured FIS path.

**Per-story pipeline** (one FIS per story): `exec-spec` implements, then `quick-review` gates the changes. Accepted review findings are a story gate – remediate once, re-run, do not enter the Writes-Landed Checklist until clear. Persistent findings → contained story failure in `AUTO_MODE`. Under `--from-issue`, the orchestrator updates the local ledger post-merge and Step 5c handles issue-side closure (no local `State` target in `--from-issue` mode).

**Spawn one sub-agent per story in the current wave, in parallel.** The orchestrator does not run `exec-spec` itself – delegate, then wait for the whole wave before scheduling the next. In-orchestrator execution is a recovery path only (delegated story returns partial/non-green and the repair is bounded), never the default.

Before scheduling, check dependencies against the run ledger. Any dependency failed/skipped → skip the story, record `blocked_by`, do not invoke `exec-spec`. `AUTO_MODE`: continue with independent stories; default mode: include skips in the next summary.

Per sub-agent, substitute `{FIS_PATH}` (absolute) into the **Worker Prompt** below. Append ` --auto` to both invocations when `AUTO_MODE=true` (per *The Automation-Mode Rules*); append ` --defer-shared-writes` to `exec-spec` when `--from-issue`.

**Worker Prompt** _(canonical; `team-mode-orchestration.md`'s Implementer and Reviewer prompts reference the **Worker Contract** below – team mode splits the line 1 invocation across `impl-*` and `review-*` tasks, but the Worker Contract applies in both modes)_:

```
Run /andthen:exec-spec {FIS_PATH} then /andthen:quick-review on the changes.

Worker Contract:
- exec-spec Step 5b handles the plan/FIS/State writes – do not call andthen:ops update-* yourself.
- Stop and report back if either returns BLOCKED: or a Failed Story Report.
```

**Sub-agent model**: inherit the session model; **medium** effort (depth comes from effort, not a different model).

#### 3c. Verify Green, Confirm Writes Landed (**Gate**)

Run immediately after each story – not as a batch. Worker self-reports do not count. Enter only after exec-spec succeeded and per-story quick-review has no accepted findings.

**Green gate**: build clean, targeted tests pass, lint/types clean, no broken intermediate state. Fail → Stop-the-Line; repair locally, re-delegate, or invoke `andthen:triage`; iterate until green.

`AUTO_MODE`: a story non-green after bounded repair, returning `BLOCKED:`, or failing its scenarios/criteria becomes a contained story failure:
- Record story id, FIS path, failure summary, verification evidence, changed files/worktree path, and any `## Failed Story Report`.
- Do not invoke `quick-review`, mark `Done`, or rerun in a dirty worktree.
- Shared-checkout: preserve partial work off the active checkout, prove clean, skip dependents, continue independent stories. If isolation cannot be proven, emit `BLOCKED:` instead of continuing.

Pass → run the **Writes-Landed Checklist** below. Outside this repair path and Post-Completion bookkeeping, the orchestrator does not write story-level status.

**Writes-Landed Checklist** (per story):

- [ ] **FIS** – every task / Acceptance Scenario / Structural Criteria checkbox `[x]`; Final Validation Checklist `[x]` when present.
- [ ] **`plan.json` story status** – the story object with `id === {story_id}` shows `status: "done"` and `fis` points at `{fis_path}`.
- [ ] **State document** _(local-directory mode only, when it exists)_ – `{story_id}` no longer in Active Stories.

`--from-issue` mode: skip the State item; the `plan.json` check applies to the materialized ledger. The FIS carries `**Plan**: github://issue/<plan-N>` for traceability; Step 5c posts the issue-side completion record.

Missing item → call the matching `andthen:ops update-*` once, then re-read that item only. Persistent miss is Stop-the-Line – do not advance on unverified status.

Pass → append story id, FIS path, verification summary to the ledger's `completed` list.

**Re-delegation** (remediation in a fresh sub-agent): spawn a new sub-agent with the same prompt as Step 3b above, prepended with a `Failure list:` section enumerating the specific failures and a `Prior review findings:` line pointing at the prior review findings file path.

**Gate**: every schedulable story in the phase is verified green or recorded failed/skipped; successful stories have FIS writes confirmed and (local-directory mode) `plan.json` / State writes confirmed or repaired.

**Gate**: all phases complete, or remaining work is blocked only by recorded failed/skipped stories.


### Step 3T: Phase Loop (Team Mode)

> **Replaces Step 3 when `--team` is active.** Steps 4–6 are shared.

Load `references/team-mode-orchestration.md` for full orchestration (team setup, implementer/reviewer prompts, task management, merge wave, status updates gate, monitoring, Final Worktree Teardown).

Per phase: update project state (Step 3a), then create and manage the Agent Team pipeline per `team-mode-orchestration.md`. The bundle is already specced – no per-phase spec generation.

**Pre-create-and-verify isolation** _(when `USE_WORKTREE=true`)_: worktree lifecycle runs through bash scripts and the `andthen:merge-resolve` skill, never `EnterWorktree` / `ExitWorktree` / `Agent({isolation:"worktree"})` – harness isolation is unreliable under `team_name`. The script-by-script flow (`create-worktree.sh` → `verify-in-worktree.sh` HARD GATE → `/andthen:merge-resolve` with guards G1/G2/G3 → `teardown-worktrees.sh`) is owned by the reference loaded above.

**Gate**: all phases complete, or remaining work is blocked only by recorded failed/skipped stories.


### Step 4: Final Review

If the ledger has failed/skipped stories, skip the final gap review – a verdict on an incomplete plan is noise; Step 6 emits the aggregate failure report instead.

**Spawn a fresh-context sub-agent** for the final gap review (orchestrator is biased by construction context). **Sub-agent model**: inherit the session model; **high** effort – gap review is cross-cutting.

Substitute `{PLAN_PATH}` (session-level `PLAN_PATH` from Step 1 – do not re-derive from `PLAN_DIR`, empty in `--from-issue`). Append ` --auto` when `AUTO_MODE=true`.

```
Run /andthen:review --mode gap {PLAN_PATH}. Do NOT pass --inline-findings – the final gap gate must write a report file so remediate-findings can consume it.
Report back the verdict (PASS/FAIL) and the absolute path to the written report file.
```

Verify the sub-agent returned a verdict and a readable report path. Missing → `BLOCKED: final gap review returned malformed output` in `AUTO_MODE`; stop in default mode.

FAIL verdict → invoke `/andthen:remediate-findings {absolute_report_path}` in the orchestrator (not a sub-agent). Scope to gap findings. Escalate after one remediation pass.

**Gate**: final gap review complete

### Step 5: Final Verification

If the ledger has failed/skipped stories, skip final verification as a success gate and proceed to Step 6. The aggregate report still includes any per-story verification that ran.

Run build, tests, linting/types, and cross-story integration. Include: **Build** (exit code/status), **Tests** (pass/fail counts), **Linting/types** (error/warning counts).

**Gate**: build, tests, linting/types, and integration pass

#### 5b. Publish to PR _(only when `--to-pr <number>`)_

After Final Verification passes, post the rolled-up summary (per-story completion + Step 4 gap verdict) per **Pattern B** in [`github-publish.md`](${CLAUDE_PLUGIN_ROOT}/references/github-publish.md). Summary temp file: `.agent_temp/exec-plan-completion-{plan-slug}.md`. In `--from-issue` mode, `{plan-slug}` = `issue-<N>`.

**Pattern B failure-handling override (only when `--from-issue` is also set)**: on `gh` failure, record verbatim and **continue to Step 5c** so issue-side closure still runs – skipping would leave granular story issues unclosed. Surface as `BLOCKED: gh pr comment failed for #<number>` in the final report (non-fatal here).

Without `--from-issue`, Pattern B's default applies: surface the error and stop. No Step 5c to protect.

**Gate**: PR comment posted (default `--to-pr` only); or posted / deferred-failure with Step 5c continuing (when `--from-issue` is also set)

#### 5c. Issue Closure Comments _(only when `--from-issue <N>` was set)_

Load `references/from-issue-mode.md` for the shape-appropriate closure protocol (single-issue: N+1 comments on the plan issue; granular: comment-then-close 2-call pattern per story plus a rolled-up summary). Use existing per-story summaries (from `andthen:exec-spec` Step 5c) and the rolled-up plan summary (Step 5).

**Gate**: closure comments posted per shape (or skipped when `--from-issue` is absent)

### Step 6: Aggregate Completion Report

Always write a deterministic summary. On success: completed stories, total phases, execution mode, review/verification results, path to `PLAN_PATH`.

If any story failed/skipped:
- `AUTO_MODE` emits `BLOCKED: exec-plan completed with failed stories`; default mode prints the same aggregate summary without asking for a mid-run decision.
- Include `Completed`, `Failed`, `Skipped`, `Blocked by` sections: story ids, FIS paths, failure evidence, preserved worktree/branch paths, report/artifact paths.
- Update `State` when present: `"At Risk"` when independent work completed but failures remain, or `"Blocked"` when no schedulable story can proceed; add blockers with one-line evidence.
- No success-only PR publishing. For issue-backed runs, comment on failures without closing unfinished story records.

**Gate**: aggregate report exists; unresolved failures visible to the next orchestrator run.

## FAILURE HANDLING

Containment, Stop-the-Line, dependent-skipping, final-review remediation, and aggregate reporting are specified inline at the **Status-Write Contract** and Steps 3c / 4 / 6. Two cross-cutting invariants not stated at a gate:

- **Always run Final Worktree Teardown before exiting** (see `references/team-mode-orchestration.md`), including failure exits – unmerged worktrees are preserved and listed in the failure summary.
- `State` on failure: `update-state status "At Risk"` or `"Blocked"` (per Step 6).

## COMPLETION

Print the Step 6 summary.

## Post-Completion

Update the `State` document (see **Project Document Index**): on success, set phase/status, mark completed stories `Done`, and add a session continuity note. If the run has failed or skipped stories, preserve Step 6's `"At Risk"` / `"Blocked"` status and blockers; only add the continuity note. Capture cross-story insights, traps, and error patterns via the `andthen:ops` skill (`update-learnings add` form, brief, by topic).
