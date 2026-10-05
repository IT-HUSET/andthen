# ADR-003: Separate runtime state from specification prose

**Status:** Accepted

**Recorded:** 2026-09-07 (retrospective); rewritten 2026-09-28 to the decision as it now holds – the standalone sidecar state file, the `ops` mutation verbs, and write locking it once named are retired.

## Context

Execution must resume from durable progress without rewriting the specification. On 0.x, FIS task checkboxes were the execution state, so progress lived in prose, and any second record of it competes with the first. Two writers of one state file also lose updates: the 0.14.4 concurrent-writer collision (`e5202ed`) dropped a status write.

## Decision

- **`plan.json` owns runtime state.** Schema v2 carries bundle intent, dependencies, and per story its status, FIS pointer, completed task ids, and `verified` record. Scheduling batches are derived from `dependsOn`, never persisted. Schema versions count breaking changes against a release, not unreleased intermediate designs.
- **One shape.** Every FIS is a plan story: a standalone feature gets a one-story `plan.json` beside its FIS, so there is no second schema and every reader has one branch.
- **FIS prose never carries progress.** Progress touches only `plan.json`; once execution begins, the FIS changes only as `fis-mutability.md` allows.
- **One writer per copy at a time.** The session executing a story – a direct `exec-plan`, or the story subagent a plan run dispatched – writes that story's row with its file tools per `plan.schema.json` and commits it with its work; a plan run writes none, except, under `--worktree`, the batch's `in-progress` rows before the batch branches. Under `--worktree` the row is edited in place in the story's worktree copy and the `--no-ff` merge brings it over. Authoring keeps one writer: the `plan` breakdown session writes the plan, and its story subagents never open it. One writer per copy replaces locking: the failure locking existed for was two writers on one file.

*Amended 2026-09-29: the executing story writes its own row, where the run session wrote every row, and `owner` leaves the schema, so a plan carrying it fails validation; `implement-fix` no longer writes a row, because the executing story writes `completedTaskIds` itself (`exec-spec/references/story.md` Step 4). Evidence: a merge test that day merged two stories' in-place row edits cleanly in every array and object layout once `owner` was gone; with `owner: null` in both rows, one layout conflicted.*

*Amended 2026-10-02 by [ADR-024](ADR-024-plan-names-and-story-status-writers.md). The executing story writes `in-progress` when it starts. Under `--worktree` the plan run also commits the dispatched batch's `in-progress` rows on `BASE_BRANCH` before the batch branches, so the main checkout shows execution. No story copy exists yet, so each copy still has one writer at a time. `handoff` no longer writes a row: the story's own `in-progress` write made it redundant, and run from a plan run's session it was a second writer.*

## Rationale

Keeping progress beside its owning artifact avoids a central state document and leaves the specification stable for review. Rejected: state in the FIS (it puts an author's checkbox or a script's markdown edit back in the loop); a per-FIS sidecar schema (every reader needed two branches); a mutation script with locking (it guarded only writers that used it, and a direct edit bypassed it).

## Consequences

Reading a FIS alone does not reveal progress; `plan.json` does. A malformed hand-written row can be written – accepted in Still Current "The `ops` skill and its script are retired". Reopens if two sessions must write one copy of a plan concurrently.

## Evidence

- History: `9d9a2ac` introduces external FIS state; `ae14dd2` settles release schema v2; `e5202ed` fixes the 0.14.4 dropped status writes.
- Current contracts: [plan schema](../../plugin/references/plan-schema.md), [the machine schema](../../plugin/references/plan.schema.json), and [FIS mutability](../../plugin/references/fis-mutability.md).
