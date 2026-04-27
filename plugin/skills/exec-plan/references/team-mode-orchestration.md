# Team-Mode Orchestration

Loaded when `--team` is active (Step 3T). Covers team setup, per-story implementer and reviewer prompts, task management, merge wave, status updates gate, monitoring, and Final Worktree Teardown.

This reference is the single source of truth for all team-mode behavior. Default-mode invocation (no `--team`) does not load this reference.


## Team Setup

Create team `"plan-pipeline"` with pre-assigned tasks. Size: 1 implementer (≤4 stories), 2 (5–10), 3 (11+). Add 1–2 reviewers for `quick-review` tasks. Use a capable coding model for all teammates.

Define `AUTO_SUFFIX = " --auto"` when `AUTO_MODE=true`, else `AUTO_SUFFIX = ""`. Define `WORKTREE_SUFFIX = " --defer-shared-writes"` when `USE_WORKTREE=true`, else `WORKTREE_SUFFIX = ""` (this is the propagated form of exec-plan's `--worktree` — exec-spec's flag describes its own behavior: defer shared-file writes).

**Substitution scope** — at team creation, replace each of the following placeholders in every teammate system prompt with its literal resolved value: `{AUTO_SUFFIX}`, `{WORKTREE_SUFFIX}`, `{CODE_DIR_ABS}` (absolute path to code repo), `{BASE_BRANCH}` (resolved at run start per Step 1). Per-task placeholders — `{task_id}`, `{fis_path}` for the implementer; the reviewer derives `STORY_ID` from its task name at runtime — are filled by the team runtime per assignment and need no orchestrator substitution. Teammates have no access to `AUTO_MODE` / `USE_WORKTREE` / orchestrator-side variables, so anything not in either list must be derived by the teammate at runtime.


## Implementer Prompt

Compose the per-story sub-agent prompt by substituting the canonical Per-Story Worker Prompt block (see `exec-plan/SKILL.md` bottom section) with `{MODE}=team` and these overrides:
- `{WORKTREE_PATH}`: the worktree path for the assigned story (`story-{task_id}`)
- `{AUTO_SUFFIX}` and `{WORKTREE_SUFFIX}`: pre-substituted per Team Setup above

Include in each implementer's system prompt:
- Only work on assigned `impl-*` tasks
- Per task: `cd {CODE_DIR_ABS}` → (worktree: `EnterWorktree "story-{task_id}"`) → `/andthen:exec-spec {fis_path}{AUTO_SUFFIX}{WORKTREE_SUFFIX}` → commit → (worktree: `ExitWorktree(keep)`) → mark done; report `exec-spec` Step 4a numbers (build, tests, lint/type-check)
- **Worktree mode (`{WORKTREE_SUFFIX}` non-empty)**: `exec-spec` skips `plan.md` and `State` document writes and emits a `## Deferred Shared Writes (worktree mode)` audit block (Story / Plan / FIS / Completion summary). Pass that block through to your report so the orchestrator can read the `Completion summary` line and audit what was deferred — the orchestrator already knows Story / Plan / FIS from its own plan parse and constructs / applies the writes post-merge itself. Constraints: (1) do not apply those writes yourself, (2) do not stage or commit `plan.md` or the `State` document inside the worktree branch — only code (and FIS) edits belong there. Shadow plan/state commits inside the worktree defeat the deferral and resurrect the merge-conflict failure mode this flag exists to prevent.
- Absolute FIS paths; escalate unresolvable issues
- For no-double-write contract, see `${CLAUDE_PLUGIN_ROOT}/references/execution-discipline.md`


## Reviewer Prompt

Compose the per-story sub-agent prompt by substituting the canonical Per-Story Worker Prompt block (see `exec-plan/SKILL.md` bottom section) with `{MODE}=team` and reviewer-specific overrides.

Include in each reviewer's system prompt:
- Role constraint: only work on assigned `review-*` tasks. `{CODE_DIR_ABS}`, `{BASE_BRANCH}`, and `{AUTO_SUFFIX}` are pre-substituted in this prompt by the orchestrator (per the substitution-scope rule above). Derive your story id at runtime by stripping the `review-` prefix from your task name (`review-S03` → `S03`); call this `<story-id>`.
- **Per-task workflow**:
  1. `cd {CODE_DIR_ABS}`.
  2. **Resolve the commit SHA to review** — the change set is committed in both modes, so `git diff` is empty either way; `quick-review`'s `commit <sha>` FOCUS form is what gives it the change set:
     - **Worktree mode (`USE_WORKTREE=true`)**: `git log {BASE_BRANCH} --grep="^Squashed-story: <story-id>$" --pretty=format:%H | head -1` (substitute the literal `<story-id>` into the grep). Empty result → escalate (the squash merge for this story has not landed). Under squash-merge the implementer's intermediate commits are not preserved on `{BASE_BRANCH}`; the squash commit IS the story's changes. If a Stop-the-Line retry produced multiple commits with the trailer, `head -1` returns the most recent — that is the right one to review.
     - **No worktree mode (`USE_WORKTREE=false`)**: `git rev-parse HEAD`. Task-dependency ordering (`impl-<story-id>` completes before `review-<story-id>` starts, no tasks intervene) guarantees the implementer's just-completed commit is at HEAD.
  3. **Substitute both `<story-id>` and `<hex-sha>` as literal values** (slash-command lines are not bash; `$VAR` and `<placeholder>` reach `quick-review` unexpanded). Invoke: `/andthen:quick-review story <story-id> commit <hex-sha>{AUTO_SUFFIX}`. The `commit <sha>` form is recognized by `quick-review`'s Determine Scope step (priority 1) — it sets the change set to `git show <sha>` and skips the empty-`git diff` fallback path.
  4. Mark task done.
- Escalate unresolvable issues to orchestrator.


## Task Management

**Task naming**: `impl-{story_id}` / `review-{story_id}` (one impl task per story, one review task per story — each story has its own FIS). Round-robin assign; do not self-assign impl and review of the same story to the same agent.

**Dependencies** (sequential, `USE_WORKTREE=false`): each `impl-*` blocked by previous `review-*`. Parallel markers ignored.

**Dependencies** (worktree, `USE_WORKTREE=true`): current-wave `impl-*` unblocked; `review-*` blocked until wave merge; W2+ `impl-*` blocked by prior-wave merge completion.


## Merge Wave _(worktree mode only)_

After all `impl-*` in the current wave complete, for each worktree branch in sequence:

1. **Squash-merge** the worktree branch into `{BASE_BRANCH}` and create the code-side commit. **Precondition (checked once, at step 1 entry)**: `git status --porcelain` in the orchestrator's CWD must be empty — `git merge --squash` refuses with staged/unstaged changes, and a leftover stage from the previous wave's step 4 would point at a missed commit boundary. If non-empty, Stop-the-Line; investigate before proceeding. Mid-step the index is intentionally dirty in two windows: between the `git merge --squash` and `git commit -F -` substeps below (the squash stages the combined diff, the commit clears it), and between top-level Step 3's plan/state writes and Step 4's commit. Neither violates the precondition.
   - **Extract `SUMMARY` first** — pull `Completion summary` from the implementer's audit block now using the regex / fallback defined in step 3 (`^Completion summary:\s*(.+)$`, trimmed; fall back to `"{STORY_ID}: completed (worktree merge)"` if the block is missing or the field is empty). The same value is reused in step 3 for `update-state note`; extract once to avoid divergence.
   - `git merge --squash story-{task_id}` stages the combined diff in the index; it does **not** advance HEAD or create a merge commit, and never auto-commits even on a clean merge. Conflict handling: imports → take both; lock files → `--theirs` + reinstall; logic conflicts → spawn troubleshooter or escalate. Resolve and `git add` before committing.
   - Apply the commit message via stdin, **not** `git commit -m "..."` — `SUMMARY` is implementer-authored prose and may contain backticks, `$(…)`, or quotes that would re-interpret under a `-m` argument:
     ```
     printf 'story-%s: %s\n\nSquashed-story: %s\n' "$STORY_ID" "$SUMMARY" "$STORY_ID" | git commit -F -
     ```
     `printf %s` does no metacharacter expansion on its substituted value, and `git commit -F -` reads the message as a byte stream — `SUMMARY` never reaches the shell argument vector. The `Squashed-story: {STORY_ID}` trailer is **load-bearing**: Final Worktree Teardown uses it to classify cross-run leftover worktrees as merged. `STORY_ID` is the bare plan id (e.g. `S03`), not the task name (`impl-S03`).
   - Consequences worth knowing: (a) **implementer authorship is collapsed** into the orchestrator's commit — `git blame` on `{BASE_BRANCH}` surfaces the orchestrator, not the implementer; the FIS, squash commit message, and deferred-writes completion summary are the forensic record. (b) **Single-repo only** (`PLAN_DIR == CODE_DIR`) — step 4's plan/state writes land as a *second* commit on `{BASE_BRANCH}`, so `git revert <squash-sha>` reverts code only; full story revert in single-repo also requires reverting the plan/state commit. The "one squash commit per story" framing applies to code-side history; plan/state side adds one more in single-repo.
2. **Verify build** on `{BASE_BRANCH}` post-commit.
3. **Apply deferred shared writes for this story.** The implementer's report contains a `## Deferred Shared Writes (worktree mode)` audit block with `Story`, `Plan`, `FIS`, and `Completion summary` fields. **Do not parse it as a script** — use it as audit / summary source.

   **Value sources** — the orchestrator already holds the structural values from Step 1's plan parse, not from the audit block or the task name:
   - `STORY_ID` is the plan story identifier (e.g. `S03`), extracted from `plan.md` at parse time. The team task names (`impl-{STORY_ID}` / `review-{STORY_ID}`) embed the same value but are *not* the source of truth.
   - `FIS_FILE_PATH` and `PLAN_FILE_PATH` are likewise from Step 1.
   - `Completion summary` is the only field actually pulled from the audit block — extract by matching the line `^Completion summary:\s*(.+)$` and trimming the captured value.

   Construct and run the writes:
   - `andthen:ops update-plan {PLAN_FILE_PATH} {STORY_ID} Done` — sets Status, Story Catalog row, acceptance-criteria checkboxes.
   - `andthen:ops update-plan {PLAN_FILE_PATH} {STORY_ID} fis "{FIS_FILE_PATH}"` — only if the plan story row's FIS field is *unset* (empty / `–` / placeholder) or *stale* (path differs from `{FIS_FILE_PATH}` after path normalization).
   - `andthen:ops update-state active-story {STORY_ID} Done` — only if the `State` document exists.
   - `andthen:ops update-state note "{Completion summary}"` — use the summary line from the audit block; if the audit block is missing or its summary is empty, fall back to `"{STORY_ID}: completed (worktree merge)"` (the substituted `STORY_ID` is the bare plan ID like `S03`, not the team task name `impl-S03`). A missing audit block is **not** a Stop-the-Line — all required values are already in the orchestrator's hand; the writes still proceed. Log the missing block as a worker self-report drift signal for follow-up.

   This is the **primary** write path for `plan.md` and `State` document in worktree mode (not a repair).

4. **Commit the resulting writes in the repo where the files live**:
   - **Single-repo** (`PLAN_DIR == CODE_DIR`) — commit on `CODE_DIR`'s `{BASE_BRANCH}`. See Worktree Merge Ordering below — subsequent merges in this wave and Wave N+1 worktrees must include these commits.
   - **Multi-repo** (`PLAN_DIR ≠ CODE_DIR`) — `plan.md` and the `State` document are **not** in `CODE_DIR`'s history. If `PLAN_DIR` is itself a git repo, commit there; otherwise the file edits stand on their own. `CODE_DIR`'s `{BASE_BRANCH}` is unaffected, so the Wave N+1 stale-base concern does not apply to plan/state files in multi-repo. (Code-side commits from the merge in step 1 still land on `CODE_DIR`'s `{BASE_BRANCH}` as usual.)

5. **Clean up worktree and branch** in `CODE_DIR` (orchestrator's CWD). The implementer exited with `ExitWorktree(keep)`, so the directory and branch are still on disk; `ExitWorktree(remove)` cannot be used cross-session, so drop to git. Substitute the actual story id for the `{task_id}` placeholder in every command below (story ids are alphanumeric/hyphen, no further shell escaping needed). **Precondition**: `pwd` must be `CODE_DIR` (the main checkout), not inside a `story-*` worktree — `git worktree remove` refuses to remove the worktree you are currently in.
   - Resolve the worktree path: `WORKTREE_PATH=$(git worktree list --porcelain | awk -v b="refs/heads/story-{task_id}" '/^worktree /{p=$2} $1=="branch" && $2==b {print p}')`.
   - **Empty resolution** — if `WORKTREE_PATH` is empty (the implementer crashed before `EnterWorktree` succeeded, or the directory was manually deleted): skip `git worktree remove`, run `git worktree prune` to clear any stale admin record, then `git branch -D story-{task_id} 2>/dev/null || true` (the branch may or may not exist). Continue to the next merge — this is recoverable, not Stop-the-Line.
   - **Dirty-tree check** — `git -C "$WORKTREE_PATH" status --porcelain` must be empty (the implementer committed inside `exec-spec`). If not, **Stop-the-Line** per FAILURE HANDLING: log path + branch in the failure summary, leave the worktree intact, and abort the wave — uncommitted work is not safe to discard.
   - `git worktree remove "$WORKTREE_PATH"` then `git branch -D story-{task_id}`. `-D` (not `-d`) is **required** under squash-merge: a squash commit has different SHA + tree-parents than the side branch's tip, so the side branch is *never* an ancestor of `{BASE_BRANCH}` after squash — `-d`'s "fully-merged" check always refuses. The squash commit on `{BASE_BRANCH}` already carries all the work, so the branch ref is safe to discard.
   - Verify `git worktree list` no longer contains `story-{task_id}`. If it does, Stop-the-Line — a leftover will collide with `EnterWorktree` if the same story id reappears.

   Then **unblock** the matching review task.

Run all five steps for one worktree before starting the next — sequential ordering keeps each merge based on a tip that already includes the prior story's deferred writes (single-repo) or sees the latest plan/state file content (multi-repo).


### Worktree Merge Ordering

Ordering violations cause stale-base overwrites — a Wave N+1 worktree branched off an outdated base will stomp deferred writes when it merges back. All rules below follow from this one constraint.

**Wave N+1 worktrees must be created AFTER Wave N merges.** Specifically:
- Wave N+1 worktrees must branch off `{BASE_BRANCH}` only after all Wave N squash-merges have committed **and** any orchestrator-applied writes that land in `CODE_DIR` (deferred shared writes in single-repo, repair writes, phase transition writes) are committed to `CODE_DIR`'s `{BASE_BRANCH}`.
- A worktree branched off a stale base will stomp those writes when it merges back.
- Multi-repo plan/state writes land in `PLAN_DIR`, not `CODE_DIR`'s `{BASE_BRANCH}`, so they are not at risk from this; only `CODE_DIR`-bound writes apply to this gate.

**Deferred shared writes must commit before next-wave worktree creation.** In single-repo setups, the plan/state write commit from Merge Wave step 4 must land on `{BASE_BRANCH}` before any Wave N+1 worktree is created. Do not parallelize worktree creation and deferred-writes commits.

**Do not use `isolation: "worktree"` with `team_name`** — Claude Code bug ([#33045](https://github.com/anthropics/claude-code/issues/33045)); instruct implementers to call `EnterWorktree` themselves.


## Status Updates Gate

Same green-gate discipline as Step 3c, then run the **Writes-Landed Checklist** (defined in Step 3c of `exec-plan/SKILL.md`) per story.

Source of truth for the checklist depends on mode:
- **Worktree** — primary writes come from the Merge Wave step's "apply deferred shared writes" substep, not from inside the worktree branch. Run the checklist after the deferred writes are applied and committed (single-repo: read from `{BASE_BRANCH}`; multi-repo: read directly from `PLAN_DIR`). Any miss after that is a real loss → repair via the matching `andthen:ops update-*` once.
- **No worktree** — `exec-spec` Step 5b writes status in-place. Run the checklist as in Step 3c; one-shot repair on miss.

Additionally verify the **Plan Acceptance Gate** before accepting `Done`: each acceptance criterion demonstrably satisfied, scope notes present when the FIS narrowed scope.

Move to the next phase only after the current phase fully passes the checklist for every story.

**Green-gate timing**:
- **Worktree** — per-worktree build/tests pre-merge; orchestrator gate on `{BASE_BRANCH}` post-merge. Stop-the-Line on `{BASE_BRANCH}`, not inside a worktree.
- **No worktree** — gate after each `impl-*`, before the matching `review-*` unblocks.

**Take-over topology** (orchestrator repair):
- **Worktree, pre-merge** — re-enter the live worktree using `EnterWorktree`'s **path form** (`EnterWorktree path: <resolved-worktree-path>`), not the name form: the orchestrator did not create the worktree itself, and the name form only resolves session-created worktrees. Per `EnterWorktree`'s contract, path-entered worktrees cannot be removed via `ExitWorktree(remove)` — fix → re-verify → commit → exit with `ExitWorktree(keep)` → merge in step 1; cleanup still runs through bash `git worktree remove` in Merge Wave step 5, never `ExitWorktree(remove)`.
- **Worktree post-merge** or **no worktree** — repair on `{BASE_BRANCH}` in orchestrator's CWD.


## Multi-Repo Rules _(when CODE_DIR ≠ PLAN_DIR's git root)_
- All git operations target `CODE_DIR` – never the plan repo
- `EnterWorktree` must be called from `CODE_DIR` context
- FIS paths passed to agents must be **absolute**
- The plan repo is **read-only for git operations** – only the orchestrator updates `plan.md`


## Monitoring

Print progress updates — the user cannot see agent activity. Report task creation/assignment, agent starts/completions, wave completions, merge results, phase summaries, and failures.


## Final Worktree Teardown

Run after all phases complete and before shutting down the team. Also runs on failure exits (Stop-the-Line escalation, `>50%` phase failure, final review unresolvable) — skipping teardown on failure is the main source of accumulated leftovers across runs. See FAILURE HANDLING in `exec-plan/SKILL.md` for the cross-link.

**Precondition**: `pwd` must be `CODE_DIR` (the main checkout), not inside a `story-*` worktree.

Invoke:
```
bash ${CLAUDE_PLUGIN_ROOT}/skills/exec-plan/scripts/teardown-worktrees.sh {BASE_BRANCH}
```

`git worktree prune` alone does **not** clean anything — it only purges admin records for worktrees whose directories are already gone. Live `story-*` worktrees from failed waves, abandoned stories, or earlier runs persist until removed explicitly.

**Stdout consumption** (parse one line at a time):
- `MERGED:<branch>` — informational; worktree and branch were removed by the script.
- `MERGED_DIRTY:<branch>` — worktree is squash-merged but has uncommitted edits or post-squash commits; preserved so the user can commit, rebase, or discard before re-running. Log branch in the failure summary; do not treat as Stop-the-Line.
- `UNMERGED:<branch>` — worktree is preserved; log branch in the failure summary so the user can decide whether to resume or discard.
- `DETACHED:<path>` — worktree is preserved; log path in the failure summary.

**Non-zero exit** → Stop-the-Line per `${CLAUDE_PLUGIN_ROOT}/references/execution-discipline.md`. Do not silently ignore a non-zero exit or unparseable output.

**Empty stdout** (no leftovers) → exit 0, no action needed.

**Post-teardown verify**: `git worktree list` should show only the main checkout, pre-existing non-`story-*` user worktrees, and any `story-*` worktrees explicitly preserved as unmerged or detached. Anything else is Stop-the-Line.

After teardown: shutdown teammates, delete team.
