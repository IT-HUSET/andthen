# Post-Completion Guide

Use this reference for STATE.md and learnings-file updates after successful execution.

## Shared Rules
- Update `STATE.md` only if it already exists.
- Update `LEARNINGS.md` or `implementation-notes.md` only if the file exists, unless the calling skill explicitly says otherwise.
- Organize learnings by topic, not chronology.
- Keep entries brief (1-2 sentences each). Record traps, domain knowledge, procedural knowledge, and error patterns that would still surprise a competent developer with repo access.
- **Error pattern classification**: Note whether an error is deterministic (bad schema, wrong type → conclude immediately) or infrastructure (timeout, rate limit → log, conclude only when pattern emerges).
- Do not record: implementation inventory (that's in git history), how parts integrate (that's in the code), routine decisions (that's in the FIS/spec), or language basics/framework docs.
- **Self-maintenance**: When touching a learnings file, also review nearby entries — merge overlapping items, remove knowledge that's no longer accurate, split sections that grow too long.

## Plan Runs
Applies to `exec-plan` and `exec-plan-team`.

### STATE.md
- Set phase to the completed or current phase.
- Set status to `On Track` when all required checks passed, otherwise `At Risk`.
- Clear completed stories from Active Stories by marking them `Done`.
- Add a session continuity note summarizing what completed, what remains, and what the next session needs.

### Learnings
- Capture cross-story insights in addition to the shared learnings categories.
- Do not create a new learnings file if none exists.

## Story Runs
Applies to `exec-spec`.

### STATE.md
- For plan-originated stories, mark the active story `Done`.
- Add a short completion note for the story.

### Learnings
- Capture story-level traps, domain knowledge, procedural knowledge, and error patterns.
- Do not create a new learnings file if none exists.

## Quick Implement
Applies to `quick-implement`.

### STATE.md
- Add only a lightweight session note when `STATE.md` exists.

### Learnings
- If a learnings file exists, append brief traps/gotchas there.
- If no learnings file exists and there are noteworthy traps, add a `Learnings` section at the end of the original spec document.
