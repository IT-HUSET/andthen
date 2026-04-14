# Post-Completion Guide

Use this reference for updates to the `State` document and the project's `Learnings` document as defined in the **Project Document Index**.

## Shared Rules
- Update the `State` document (see **Project Document Index**) only if it already exists.
- Update the `Learnings` document (see **Project Document Index**) or `implementation-notes.md` only if the file exists, unless the calling skill explicitly says otherwise.
- Organize learnings by topic, not chronology.
- Keep entries brief (1-2 sentences each). Record traps, domain knowledge, procedural knowledge, and error patterns that would still surprise a competent developer with repo access.
- **Error pattern classification**: Note whether an error is deterministic (bad schema, wrong type → conclude immediately) or infrastructure (timeout, rate limit → log, conclude only when pattern emerges).
- Do not record: implementation inventory (that's in git history), how parts integrate (that's in the code), routine decisions (that's in the FIS/spec), or language basics/framework docs.
- **Self-maintenance**: When touching a learnings file, also review nearby entries — merge overlapping items, remove knowledge that's no longer accurate, split sections that grow too long.

## Plan Runs
Applies to `exec-plan` and `exec-plan-team`.

### `State` Document (see **Project Document Index**)
- Set phase to the completed or current phase.
- Set status to `On Track` when all required checks passed, otherwise `At Risk`.
- Clear completed stories from Active Stories by marking them `Done`.
- Add a session continuity note summarizing what completed, what remains, and what the next session needs.

### `Learnings` (see **Project Document Index**)
- Capture cross-story insights in addition to the shared learnings categories.
- Do not create a new `Learnings` document if none exists in the location defined by the **Project Document Index**.

## Story Runs
Applies to `exec-spec`.

### `State` Document (see **Project Document Index**)
- For plan-originated stories, mark the active story `Done`.
- Add a short completion note for the story.

### `Learnings` (see **Project Document Index**)
- Capture story-level traps, domain knowledge, procedural knowledge, and error patterns.
- Do not create a new `Learnings` document if none exists in the location defined by the **Project Document Index**.

## Quick Implement
Applies to `quick-implement`.

### `State` Document (see **Project Document Index**)
- Add only a lightweight session note when the `State` document (see **Project Document Index**) exists.

### `Learnings` (see **Project Document Index**)
- If the `Learnings` document (see **Project Document Index**) exists, append brief traps/gotchas there.
- If no `Learnings` document exists in the location defined by the **Project Document Index** and there are noteworthy traps, add a `Learnings` section at the end of the original spec document.
