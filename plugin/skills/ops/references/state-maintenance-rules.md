# State Maintenance Rules

Apply automatically on every write to the relevant State document.

- **Active Stories table** (shared): remove rows with status `Done` (they belong in `plan.json`, not state). Tracks only _currently in-progress_ work – never accumulate completed milestone summaries here. Stored rows whose story id resolves in a governing `plan.json` are legacy – prune them on write (the view derives from `plan.json` on read); ad-hoc rows persist.
- **Recently Completed** (shared): keep only the **last 2 milestones/releases**. Older milestones should already be captured in CHANGELOG.md. Use a one-line summary per milestone (not full release notes). If there are older milestones beyond the kept 2, condense into a single trailing line: `Previous: 0.14, 0.13, 0.12, ...`
- **Blockers** (shared): remove entries that are no longer relevant (e.g. the blocking condition has been resolved, the related story is `Done`, or the blocker is older than 14 days with no recent activity)
- **Recent Decisions** (shared): keep only the **last 10** entries; graduate older items to ADRs if warranted
- **Session Continuity Notes** (local): keep only the **last 5** entries; older entries are trimmed. Notes already captured elsewhere (CHANGELOG, Recently Completed, a handoff doc) should be removed.
- **Overall size**: each document stays small (shared `State` under ~60 lines). If it exceeds this after other maintenance rules, trim the oldest/longest entries first. These are snapshots of _current_ state, not history logs.
