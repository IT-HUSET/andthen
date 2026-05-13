---
description: Use when the user wants to execute a fully-specced implementation plan bundle. Runs a fixed pipeline per story (exec-spec + quick-review) and a final gap review on the whole plan. Requires a plan bundle where every story already has a FIS. Supports Agent Teams (--team) and sub-agents (portable fallback). Trigger on 'execute this plan', 'implement this plan', 'run the plan', 'execute with agents', 'run as team'.
argument-hint: "[--team] [--worktree] [--from-issue <number>] [--to-pr <number>] [--auto|--headless] <path-to-plan-directory> [path-to-code-repo]"
---

# Execute Plan

## VARIABLES

PLAN_DIR: $ARGUMENTS first positional argument (strip any flag tokens like `--team`, `--worktree`, `--from-issue`, `--to-pr`, `--auto`, or `--headless` before interpreting the remainder as positional args). When `--from-issue <N>` is set, `PLAN_DIR` is empty and the plan source is the GitHub issue body.
CODE_DIR: second positional argument _(optional – for multi-repo setups where plan and code live in different repos)_
PLAN_PATH: resolved in Step 1, used unchanged in Steps 3, 4, 5. Local-directory mode: `PLAN_DIR/plan.json` (absolute). `--from-issue` mode: `.agent_temp/from-issue-<N>/plan.json` (absolute) – the materialized local ledger. Do not re-derive `PLAN_DIR/plan.json` in `--from-issue` mode (`PLAN_DIR` is empty there).

### Optional Flags
- `--team` → USE_TEAM: force Agent Teams mode; error if unavailable
- `--worktree` → USE_WORKTREE: enable isolated git worktrees for parallel execution (team mode only; default: `false`)
- `--from-issue <number>` → ISSUE_INPUT: Use a GitHub plan issue as input (`gh issue view <N>`). Auto-detects single-issue vs granular shape per [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md), extracts `## Shared Decisions`, `## Binding Constraints`, and the PRD source for inlining into per-story FIS context, generates each story's FIS just-in-time by invoking the `andthen:spec` skill with a temp story-source file (single-issue: extracted from the story section in the parent body; granular: fetched via `gh issue view <story-N> --json body` from the linked story issue), then runs the existing per-story exec-spec + quick-review pipeline against the materialized FIS with shared local writes deferred. Posts shape-appropriate closure comments after Step 5. **Mutually exclusive with `--team`** (parallel JIT FIS generation is not supported under this flag) – reject with `BLOCKED: --from-issue is mutually exclusive with --team` in `AUTO_MODE`; warn and stop in default mode.
- `--to-pr <number>` → PUBLISH_PR: after Step 5 Final Verification, post the existing rolled-up completion summary plus final gap verdict as a PR comment via `gh pr comment <number> --body-file <summary-path>`. No new content generation. Composes with `--from-issue <N>` (the same flag works whether the plan came from a local directory or a GitHub issue). See Step 5 Publish to PR sub-step.
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts

## INSTRUCTIONS

Require `PLAN_DIR` unless `--from-issue <N>` is set. Stop if the required plan source is missing. **You are the orchestrator.** Parse the plan, run the per-story pipeline (`exec-spec` → `quick-review` per story, then one final `review --mode gap`), verify writes landed, handle phase transitions, manage failures, run final verification. Delegate story code to `exec-spec` (sub-agent, teammate, or sequential fallback); take over locally when a story returns partial or non-green and the repair is clearly bounded. In `AUTO_MODE`, persistent story failures are recorded and reported at the end.

### Rules
- **Plan is source of truth** – `plan.json` per [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md). Follow phase ordering, `dependsOn`, and `parallel` exactly. In local-directory mode, every schedulable story (`status` ∈ {`pending`, `spec-ready`, `in-progress`}) must carry an existing `fis` path; abort if missing – no auto-recovery. `done` and `skipped` are terminal; `blocked` is a manual escape hatch – consumers skip with a warning per `plan-schema.md`. The `--from-issue` mode relaxes the FIS requirement because FIS files are generated just-in-time.
- **Execution discipline** – Stop-the-Line on red gates per [`execution-discipline.md`](${CLAUDE_PLUGIN_ROOT}/references/execution-discipline.md). See the **Status-Write Contract** below for orchestrator-side specifics (story-scoped containment, no-double-write, worktree deferral).
- **Automation rules** – see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). `BLOCKED:` triggers: invalid inputs, unrepairable red gates, missing execution tools, unsafe external actions.
- **Status updates are gates** – plan and FIS checkpoint updates block the next phase; do not defer. `plan.json` is mutated only via `andthen:ops update-plan` / `update-plan-fis` (writability rules in `plan-schema.md`).
- **Story failure containment** – `done` still means fully green. Failed stories transition to `skipped` (dependency-chain containment) or remain `in-progress` until repaired; never skip the enum.
- **State document updates are gated** – update on phase transitions and blocker discovery (see **Project Document Index**).


### Status-Write Contract (Multi-Story Orchestration)

Orchestrator-side rules that extend the universal Stop-the-Line gate (see [`execution-discipline.md`](${CLAUDE_PLUGIN_ROOT}/references/execution-discipline.md)).

- **Story-scoped containment** – A failed story is not `Done`, not merged as complete, and does not unblock dependents. In `AUTO_MODE`, record the failure, preserve partial work, skip dependents, continue independent stories, and finish with an aggregate failed-run report. When stories share a checkout, continue only after preserving the failed story's partial work off the active checkout and proving the active checkout is clean.

- **Authoritative writes (no double-write)** – `exec-spec` Step 5b writes the per-story status (FIS checkboxes, `plan.json` story `status`, State active-story) via `andthen:ops`. Sub-agents and teammates **do not** additionally call `andthen:ops update-*` on top of the executing skill – that duplicates writes. The orchestrator writes cross-story state only (phase transitions, overall status, session notes) plus *repair writes* when a Step 3c Writes-Landed Checklist item is missing (one `andthen:ops update-*` per missing item).

- **Worktree deferral** – Under `--worktree`, `exec-spec` runs with `--defer-shared-writes`: it writes only the FIS (story-local, merges cleanly) and emits a `## Deferred Shared Writes` audit block (`Story`, `Plan`, `FIS`, `Completion summary`). The orchestrator constructs the `andthen:ops update-*` calls from its own `STORY_ID` / `FIS_FILE_PATH` / `PLAN_FILE_PATH` plus the audit's `Completion summary` and applies them as the **primary** write path immediately after merging that worktree, before the next merge or Wave N+1 creation.
  - Repo placement: single-repo writes land on `{BASE_BRANCH}`; multi-repo writes land in `PLAN_DIR` (committed there if it's a git repo) and leave `CODE_DIR` untouched.
  - Missing audit block → fall back to a generated `Completion summary` and proceed; log the miss but don't Stop-the-Line.
  - The Writes-Landed Checklist runs *after* deferred writes are applied; any miss there is a real loss → one-shot repair.


## WORKFLOW

### Step 1: Parse Plan

> **When `--from-issue <N>` is set**: load `references/from-issue-mode.md`. That reference covers the flag-combination guard, the plan-issue body fetch, shape detection, materialization of a local `plan.json` ledger at `.agent_temp/from-issue-<N>/plan.json`, and reconciliation on rerun. After materialization, this Step 1 falls through to validation against the local ledger (items 4–6 below) using the materialized path as `{PLAN_PATH}`. The FIS-existence check (item 5) is relaxed for `--from-issue` because FIS files are generated just-in-time in Step 3.

1. **Resolve CODE_DIR** _(skip if `--team` not set and no second positional arg)_:
   - If provided: verify git repository, resolve to absolute path
   - If not provided: auto-detect from PLAN_DIR's git root (when set) vs CWD's git root. Same repo → use that root. Different repos → use CWD's git root.
   - Resolve `BASE_BRANCH`: `git -C {CODE_DIR} rev-parse --abbrev-ref HEAD`.
   - **Log + non-default warning** _(only when CODE_DIR was resolved above; default no-team runs do not branch off `BASE_BRANCH` and skip this step)_: print `BASE_BRANCH={value}` explicitly. Resolve `DEFAULT_BRANCH` from the most authoritative source available – `git symbolic-ref refs/remotes/origin/HEAD --short` (strip `origin/` prefix), else a local `main`, else a local `master`. If none resolve, skip the warning (no nag in repos without a clear default). When `BASE_BRANCH ≠ DEFAULT_BRANCH`: confirm in default mode; in `AUTO_MODE`, proceed but log `WARNING: BASE_BRANCH={value} is not the repo's default branch ({DEFAULT_BRANCH}) – all stories will land here.`. Catches the "I thought I was on a different branch" silent-corruption case.

2. **Load session state** – Read the `State` document (see **Project Document Index**; default: `docs/STATE.md`) if it exists. Extract session continuity notes, active stories, blockers, and current phase.

3. Read `PLAN_DIR/plan.json` _(local-directory mode)_. If only `plan.md` is present and `plan.json` is not, stop with: `BLOCKED: plan.md is no longer consumed by exec-plan. Run /andthen:plan {PLAN_DIR} to migrate to plan.json (existing FIS files are preserved).` If `plan.json` is missing entirely, stop – a valid plan artifact is required upstream (the `andthen:plan` skill). On success, set `PLAN_PATH` to the absolute path of the resolved file (in `--from-issue` mode, `references/from-issue-mode.md` materialization sets `PLAN_PATH` to `.agent_temp/from-issue-<N>/plan.json`).
4. **Validate against schema** – confirm `schemaVersion === "1"`; if not, `BLOCKED: unsupported plan.json schemaVersion – re-run /andthen:plan to regenerate`. On parse error, `BLOCKED: malformed plan.json – re-run /andthen:plan`. Validate `dependsOn` closure: every element in every story's `dependsOn` array must match an `id` in `stories[]`. On unknown IDs, stop with `BLOCKED: invalid dependency in {story_id}: "{value}" – story not in catalog`. Validate the status enum: each story's `status` must be one of `pending`, `spec-ready`, `in-progress`, `done`, `skipped`, `blocked`.
5. **Verify FIS files exist** _(local-directory mode only; relaxed under `--from-issue`)_: every story whose `status` is `pending`, `spec-ready`, or `in-progress` must carry a `fis` path that points at an existing file. This matches the schedulable set in item 6, so an interrupted local bundle with `pending` / `fis: null` stories aborts cleanly here instead of failing mid-pipeline. `blocked` stories are skipped at scheduling time and are not gated here (manual escape hatch – `consumers skip and warn` per `plan-schema.md`). If any story fails this check, abort with: `Plan bundle has stories with missing FIS – run /andthen:plan {PLAN_DIR} to fill them (plan is resumable).` Do not proceed (same in `--auto` mode – no auto-recovery). The `--from-issue` JIT exception lives in Step 3b.
6. Build the execution plan declaratively from the JSON: respect phase ordering (`overview.phases[]`), dependency chains (`dependsOn`), wave grouping (`stories[].wave`), and parallel markers (`stories[].parallel`). Schedulable: `stories.filter(s => s.status !== 'done' && s.status !== 'skipped' && s.status !== 'blocked' && depsSatisfied(s))`. For each story dropped because `status === 'blocked'`, log `WARNING: story {id} is blocked – skipping` and record it in the run ledger's `skipped` list with reason `manually blocked`.

**Gate**: Plan parsed (from local `plan.json` or materialized ledger); schema valid; in local mode FIS files exist on disk; phases identified


### Step 2: Determine Execution Mode

**Pre-validate flag combinations**: `--worktree` requires `--team` (worktree isolation is a team-mode feature; sub-agent mode runs sequentially in the orchestrator's CWD and has no worktrees to merge). If `USE_WORKTREE=true` and `USE_TEAM=false`, stop. In default mode, inform the user that `--worktree` is only meaningful with `--team` and ask whether to proceed with `--team` added or drop `--worktree`. In `AUTO_MODE`, emit `BLOCKED: --worktree requires --team` and exit.

Check whether Agent Teams are available by verifying that team creation tools exist (e.g. `TeamCreate`).

- **`--team` AND available** → Team mode (Step 3T)
- **`--team` AND unavailable** → stop. In default mode, inform the user it requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`; in `AUTO_MODE`, emit `BLOCKED: Agent Teams unavailable (requires CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1)` and exit.
- **No `--team`** → Sub-agent mode (Step 3). Mention `--team` is available if the user wants team execution, unless `AUTO_MODE=true`.

**Gate**: Execution mode determined

Before story execution (Step 3 or Step 3T), initialize a run ledger: `completed`, `failed`, `skipped`, and `blocked_by`. `plan.json` records successful `done` transitions; the ledger feeds the aggregate report.


### Step 3: Phase Loop

For each phase in the plan:

#### 3a. Phase Transition

**Update project state** (if the `State` document exists; see **Project Document Index**): invoke the `andthen:ops` skill with `update-state phase "{Phase N}: {phase_name}"` and `update-state status "On Track"`.

In local-directory mode, FIS files were verified to exist in Step 1, item 5; re-read `plan.json` if any status updates from a prior phase may have landed during execution. In `--from-issue` mode, the materialized local ledger (`.agent_temp/from-issue-<N>/plan.json`) is reread the same way – `--from-issue` and local-directory mode share a single execution path after Step 1.

**Gate**: Phase context loaded, `plan.json` current

#### 3b. Execute Story Pipelines

> **JIT FIS layer** _(only when `--from-issue` is set)_: load `references/from-issue-mode.md` for the per-story FIS materialization recipe (story-body extraction, temp-file invocation form, and the `andthen:spec` failure policy). The orchestrator (this skill) is the actor that injects `**Plan**: github://issue/<plan-N>` and `**Story-ID**: <S0N>` provenance fields into each materialized FIS – `andthen:spec`'s file-reference branch does not auto-emit them. After provenance injection and ledger update, fall through to the standard per-story pipeline below using the captured FIS path as `{fis_path}`.

**Per-story pipeline** (one FIS per story, so each story gets its own exec-spec + quick-review run):
1. **Implement**: `/andthen:exec-spec {fis_path}{AUTO_SUFFIX}{SHARED_WRITE_SUFFIX}`. When `--from-issue` is set, `{SHARED_WRITE_SUFFIX}` is ` --defer-shared-writes`; the local `plan.json` ledger update is handled by the orchestrator after the worktree merges, and issue-side closure is handled in Step 5c. There is no local `State` status target in `--from-issue` mode.
2. **Review**: only after exec-spec succeeds, run `/andthen:quick-review{AUTO_SUFFIX}` on the story's changes. Accepted findings are a story gate: remediate once, re-run quick-review, and do not enter the Writes-Landed Checklist until findings are cleared. Persistent findings become a contained story failure in `AUTO_MODE`.

**Wave-based execution**: W1 in parallel (via sub-agents), then W2, etc. Fall back to sequential in-orchestrator execution if sub-agents are unavailable or delegated execution stalls / returns partial / non-green.

Before scheduling a story, check its dependencies against the run ledger. If any dependency is failed or skipped, skip this story, record `blocked_by`, and do not invoke `exec-spec`. In `AUTO_MODE`, continue with other stories whose dependencies are satisfied; in default mode, include the skip in the next progress/failure summary.

Compose the per-story sub-agent prompt by substituting the canonical **Per-Story Worker Prompt** block (see bottom of this file) with `{MODE}=default` and overrides:
- `{STORY_ID}` = the story's plan identifier (e.g. `S03`)
- `{FIS_PATH}` = absolute path to the story's FIS
- `{PLAN_PATH}` = absolute path to `PLAN_DIR/plan.json` (local-directory mode) or to the materialized ledger `.agent_temp/from-issue-<N>/plan.json` (`--from-issue`)
- `{BASE_BRANCH}` = resolved at run start
- `{AUTO_SUFFIX}` = `" --auto"` when `AUTO_MODE=true`, else `""`
- `{SHARED_WRITE_SUFFIX}` = `" --defer-shared-writes"` when `--from-issue` is set, else `""`
- Apply `--auto` propagation per `${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md` when `AUTO_MODE=true`

**Model assignment**: Use a capable coding model (`model: "sonnet"`, `gpt-5.3-codex`, or similar).

#### 3c. Verify Green, Confirm Writes Landed (**Gate**)

Run immediately after each story – not as a batch. Worker self-reports do not count. Enter this gate only after exec-spec succeeded and per-story quick-review has no accepted findings.

**Green gate**: build clean, targeted tests pass, lint/types clean, no broken intermediate state. Fail → Stop-the-Line per `${CLAUDE_PLUGIN_ROOT}/references/execution-discipline.md`; repair locally, re-delegate, or invoke the `andthen:triage` skill; iterate until green.

In `AUTO_MODE`, a story that remains non-green after bounded repair, returns `BLOCKED:`, or fails its Success Criteria becomes a contained story failure:
- Record story id, FIS path, failure summary, verification evidence, changed files/worktree path, and any `exec-spec` `## Failed Story Report`.
- Do not invoke `quick-review`, mark `Done`, or blindly rerun in the same dirty worktree.
- In shared-checkout mode, preserve partial work off the active checkout, prove the checkout clean, then skip dependents and continue independent stories. If isolation cannot be proven, emit `BLOCKED:` instead of continuing.

Pass → run the **Writes-Landed Checklist** below. This is a structured re-read, not a glance. Outside this repair path and Post-Completion bookkeeping, the orchestrator does not write story-level status.

**Writes-Landed Checklist** (per story just completed):

- [ ] **FIS** – open the FIS at `{fis_path}`. Every task checkbox is `[x]`. Final Validation Checklist items are `[x]`. Success criteria are `[x]`.
- [ ] **`plan.json` story status** – open `{PLAN_PATH}`. The story object with `id === {story_id}` shows `status: "done"` and its `fis` field points at `{fis_path}`.
- [ ] **State document** _(local-directory mode only, if it exists per **Project Document Index**)_ – `{story_id}` is no longer in the Active Stories table.

In `--from-issue` mode, the State checklist item is skipped (no local State target); the `plan.json` story-status check applies to the materialized ledger (`.agent_temp/from-issue-<N>/plan.json`). The generated FIS carries `**Plan**: github://issue/<plan-N>` for traceability – Step 5c posts the issue-side completion record.

Missing item → call the matching `andthen:ops update-*` once to repair, then re-read that item only. Persistent miss after one repair pass is Stop-the-Line – do not advance the wave on unverified status.

Checklist pass → append story id, FIS path, and verification summary to the run ledger's `completed` list.

**Re-delegation** (remediation via sub-agent): compose the per-story sub-agent prompt by substituting the canonical **Per-Story Worker Prompt** block with `{MODE}=re-delegation` and overrides:
- `{STORY_ID}`, `{FIS_PATH}`, `{PLAN_PATH}`, `{BASE_BRANCH}` as above
- `{AUTO_SUFFIX}` = `" --auto"` when `AUTO_MODE=true`, else `""`
- `{SHARED_WRITE_SUFFIX}` as above
- `{REVIEW_FINDINGS_PATH}` = path to prior review findings
- Add a `Failure list:` section with the specific failures before the main prompt block

**Gate**: All schedulable stories in the current phase are either verified green or recorded failed/skipped in the run ledger; successful stories have FIS writes confirmed and, in local-directory mode, `plan.json` / State writes confirmed or repaired.

**Gate**: All phases complete, or remaining work is blocked only by recorded failed/skipped stories.


### Step 3T: Phase Loop (Team Mode)

> **This step replaces Step 3 when `--team` is active.** Steps 4–6 are shared.

Load `references/team-mode-orchestration.md` for the full orchestration content (team setup, implementer/reviewer prompts, task management, merge wave, status updates gate, monitoring, and Final Worktree Teardown).

For each phase: update project state (same as Step 3a), then create and manage the Agent Team pipeline per `team-mode-orchestration.md`. The bundle is already fully specced – no per-phase spec generation step.

**Pre-create-and-verify isolation** _(when `USE_WORKTREE=true`)_: worktree lifecycle runs through bash scripts, never through `EnterWorktree` / `ExitWorktree` / `Agent({isolation:"worktree"})` – harness isolation is unreliable under `team_name`. Flow: `create-worktree.sh` (orchestrator, pre-spawn per `impl-*`) → `verify-in-worktree.sh` (implementer HARD GATE, first action every turn) → `merge-worktree.sh` with guards G1/G2/G3 (orchestrator, Merge Wave) → `teardown-worktrees.sh` (Final Worktree Teardown). See `references/team-mode-orchestration.md`.

**Gate**: All phases complete, or remaining work is blocked only by recorded failed/skipped stories.


### Step 4: Final Review

If the run ledger contains failed or skipped stories, skip the final gap review. A whole-plan gap verdict on an incomplete plan is noise; Step 6 will emit the aggregate failure report instead.

Spawn a sub-agent with fresh context (the orchestrator is biased by construction context). **Model**: use a strong reasoning model (`model: "opus"`, `gpt-5.4`, or similar) – gap review is cross-cutting, not routine pattern-matching.

Resolve `CODE_DIR` to an absolute path before composing the prompt. Compose by substituting the canonical **Per-Story Worker Prompt** block (bottom of this file) with `{MODE}=final-review` and overrides:
- `{PLAN_PATH}` = the session-level `PLAN_PATH` resolved in Step 1 (local-directory: `PLAN_DIR_ABS/plan.json`; `--from-issue`: `.agent_temp/from-issue-<N>/plan.json` – the materialized ledger). Do not re-derive from `PLAN_DIR` here; in `--from-issue` mode `PLAN_DIR` is empty.
- `{CODE_DIR_ABS}` = resolved absolute code directory
- `{STORY_ID}` and `{FIS_PATH}` empty/omitted; apply `--auto` propagation when `AUTO_MODE=true`

Verify the sub-agent returned both a verdict and a readable report path. If either is missing: `BLOCKED: final gap review returned malformed output` in `AUTO_MODE`; stop in default mode.

If the verdict is FAIL: invoke `/andthen:remediate-findings {absolute_report_path}` in the orchestrator (not a sub-agent). Scope narrowly to gap report findings. Escalate if issues persist after one remediation pass.

**Gate**: Final gap review complete

### Step 5: Final Verification

If the run ledger contains failed or skipped stories, skip final verification as a success gate and proceed to Step 6. The aggregate report must still include any per-story verification that did run.

Run build, run tests, review cross-story integration. Include verification evidence: **Build** (exit code/status), **Tests** (pass/fail counts), **Linting/types** (error/warning counts).

**Gate**: Build, tests, integration pass

#### 5b. Publish to PR _(only when `--to-pr <number>`)_

After Final Verification has passed, post the rolled-up summary (per-story completion + final gap verdict from Step 4) per **Pattern B** in [`github-publish.md`](${CLAUDE_PLUGIN_ROOT}/references/github-publish.md). Summary temp file: `.agent_temp/exec-plan-completion-{plan-slug}.md` – in `--from-issue` mode where `PLAN_DIR` is empty, `{plan-slug}` resolves to `issue-<N>` (full path: `.agent_temp/exec-plan-completion-issue-<N>.md`).

**Failure-handling override of Pattern B (only when `--from-issue` is also set)**: on `gh` failure here, record the error verbatim and **continue to Step 5c** so issue-side closure still runs – skipping it on a PR-side failure would leave granular story issues unclosed. Surface in the final completion report as `BLOCKED: gh pr comment failed for #<number>` (recorded but non-fatal at this step).

When `--from-issue` is NOT set, Pattern B's default applies: surface the `gh` error verbatim and stop. There is no Step 5c to protect, so the override would silently mask a transport failure as success – fall through to the default stop.

**Gate**: PR comment posted (default `--to-pr` only); or PR comment posted / surfaced as deferred failure with Step 5c continuing (when `--from-issue` is also set)

#### 5c. Issue Closure Comments _(only when `--from-issue <N>` was set)_

Load `references/from-issue-mode.md` for the shape-appropriate closure protocol – single-issue posts N+1 comments on the plan issue; granular uses the deliberate comment-then-close 2-call pattern per story plus a rolled-up summary on the plan issue. Use the existing per-story completion summaries (already produced by `andthen:exec-spec` Step 5c) and the rolled-up plan summary (Step 5).

**Gate**: Closure comments posted per shape (or skipped when `--from-issue` is absent)

### Step 6: Aggregate Completion Report

Always write a deterministic summary. On success, include completed stories, total phases, execution mode, review/verification results, and path to `PLAN_DIR/plan.json`.

If any story failed or was skipped:
- Emit `BLOCKED: exec-plan completed with failed stories` in `AUTO_MODE`; in default mode, print the same aggregate summary without asking for a mid-run decision.
- Include `Completed`, `Failed`, `Skipped`, and `Blocked by` sections with story ids, FIS paths, failure evidence, preserved worktree/branch paths, and report/artifact paths.
- Update the `State` document when present: status `"At Risk"` when independent work completed but failures remain, or `"Blocked"` when no remaining schedulable story can proceed; add blockers for failed stories with one-line evidence.
- Do not run success-only PR publishing. For issue-backed runs, comment on failures without closing unfinished story records.

**Gate**: Aggregate report exists and unresolved failures are visible to the next orchestrator run.

## FAILURE HANDLING

- **Story pipeline fails / non-green** → Stop-the-Line per `${CLAUDE_PLUGIN_ROOT}/references/execution-discipline.md` within that story. In `AUTO_MODE`, persistent failure is recorded, dependent stories are skipped, independent stories continue, and Step 6 reports the aggregate failure.
- **Final review fails** → one remediation pass (subjective-finding policy); escalate if issues persist
- **Dependent stories blocked** when predecessor fails; **>50% of a phase fails** → record skips/failures and return them in the aggregate report. Do not pause in `AUTO_MODE`.
- **Update the `State` document on failure** (see **Project Document Index**): `update-state status "At Risk"` or `"Blocked"`
- **Always run Final Worktree Teardown before exiting** (see `references/team-mode-orchestration.md`), including failure exits – unmerged worktrees are preserved and listed in the failure summary.

## Per-Story Worker Prompt

Single canonical prompt template for all per-story sub-agent invocation sites. Placeholders:
- `{STORY_ID}`, `{FIS_PATH}`, `{PLAN_PATH}`, `{BASE_BRANCH}` – plan/story identity (FIS, plan, branch as absolute path/value).
- `{MODE}` – `default` / `team` / `re-delegation` / `final-review`.
- `{WORKTREE_PATH_ABS}` – absolute worktree path captured from `create-worktree.sh` (team + worktree only; empty otherwise).
- `{WORKTREE_PRELUDE}` – orchestrator-composed block injected ahead of the per-story body. When `{WORKTREE_PATH_ABS}` is non-empty: the substituted value is a leading blank line + `cd {WORKTREE_PATH_ABS}` + `bash ${CLAUDE_SKILL_DIR}/scripts/verify-in-worktree.sh {STORY_ID} {WORKTREE_PATH_ABS}` + STOP-on-anything-other-than-`VERIFY_OK` + absolute-paths-only mandate + trailing blank line. Empty for non-worktree runs (template collapses flush – see the template below). **Kept in sync** with the Implementer system-prompt step 1 in `references/team-mode-orchestration.md` (`## Implementer Prompt` → `Per task, worktree mode` → step 1): the prelude is the per-task injection, the system-prompt step is the durable rule; both encode the same verify-first-or-STOP contract. Edit both together.
- `{AUTO_SUFFIX}` – `" --auto"` when `AUTO_MODE=true`, else `""`.
- `{WORKTREE_SUFFIX}` / `{SHARED_WRITE_SUFFIX}` – `" --defer-shared-writes"` when defer applies (worktree mode or `--from-issue`), else `""`.
- `{REVIEW_FINDINGS_PATH}` – prior review findings (re-delegation only).
- `{CODE_DIR_ABS}` – absolute code repo path (final-review mode).

For the no-double-write contract, see **Status-Write Contract** above.

**Modes `default` / `team` / `re-delegation`** (per-story execution):
```
Story {STORY_ID} | Mode: {MODE}
Plan: {PLAN_PATH} | FIS: {FIS_PATH}
{WORKTREE_PRELUDE}
1. /andthen:exec-spec {FIS_PATH}{AUTO_SUFFIX}{SHARED_WRITE_SUFFIX}
2. If exec-spec succeeded, run `/andthen:quick-review{AUTO_SUFFIX} on the changes`. If it returned `BLOCKED:` or a Failed Story Report, stop this story and report it to the orchestrator.

Run `/andthen:exec-spec` – its Step 5b writes this story's status unless `{SHARED_WRITE_SUFFIX}` defers shared local writes back to the orchestrator / issue workflow.
Do not call `andthen:ops update-*` yourself – `exec-spec` Step 5b handles those calls.

Report:
- Step results (success/failure), files changed
- exec-spec Step 4a numbers (build, tests, lint/type-check, format)
- Any issues, incomplete work, non-green state, or `BLOCKED:` / Failed Story Report – be explicit
```

**Mode `final-review`** (whole-plan gap review; `{STORY_ID}` and `{FIS_PATH}` are empty/omitted):
```
Mode: final-review
Plan: {PLAN_PATH} | Implementation: {CODE_DIR_ABS}

Run /andthen:review --mode gap {PLAN_PATH}

Do NOT pass --inline-findings – the final gap gate must write a report file
so remediate-findings can consume it.

Report back:
1. The verdict (PASS/FAIL) from the canonical gap verdict table
2. The absolute path to the written report file
```



## COMPLETION

Print the Step 6 summary.

## Post-Completion

Update the `State` document (see **Project Document Index**): on success, set phase/status, mark completed stories `Done`, and add a session continuity note. If the run has failed or skipped stories, preserve Step 6's `"At Risk"` / `"Blocked"` status and blockers; only add the continuity note. If the `Learnings` document exists, capture cross-story insights, traps, and error patterns (brief, by topic; do not create if none exists).
