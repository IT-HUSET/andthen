# Status-write derivation and deferred-write replay

Mechanics for exec-spec's Step 5b status writes: the Plan-level status derivation ladder (used by 5b.3 success and 4d failure) and the deferred-shared-writes replay (orchestrator vs standalone). SKILL.md holds the invocation pointers and the `## Deferred Shared Writes` audit-block template; this ref holds the algorithm and the replay explanation.

## Plan-level status derivation rule

Shared by 5b.3 success and 4d failure; the failure path appends its blocker before applying, the success path removes its prior blocker first. Output is the State-document plan-health value, one of `On Track`, `At Risk`, `Blocked` (distinct from per-story plan.json `status`) – quote at invocation:

1. Re-read `{PLAN_FILE_PATH}` and the State document.
2. `schedulable` = stories where `status` ∈ {`pending`, `spec-ready`} AND every `dependsOn` ID resolves to `status` ∈ {`done`, `skipped`}.
3. Derive (first match wins):
   - any plan.json story `status === "blocked"` → `Blocked`
   - else `schedulable == 0` AND (any plan.json story is not in {`done`, `skipped`} OR any State blocker exists) → `Blocked`
   - else (any State blocker exists OR any plan.json story `status === "skipped"`) → `At Risk`
   - else → `On Track`

## Deferred-write replay mechanics

The orchestrator constructs the actual `andthen:ops update-*` invocations from the audit-block values plus its single-repo vs multi-repo knowledge: in worktree mode applied post-merge (see `andthen:exec-plan` Step 3T Merge Wave); in `--from-issue` mode against `.agent_temp/from-issue-<N>/plan.json` after exec-spec + quick-review clear. Do not emit a list of `andthen:ops` lines – the orchestrator does not parse that.

**Standalone use** (no orchestrator): when `Plan` is a local path, the user applies the deferred writes (the same `update-plan` / `update-state` calls listed in 5b.2 / 5b.3) after committing FIS changes. When `Plan` is `github://issue/<N>`, do not run local `ops update-plan` unless the caller supplies the materialized plan.json path; post or close the issue record instead. Standalone `--defer-shared-writes` is for users who explicitly want this deferral – do not set it without one.
