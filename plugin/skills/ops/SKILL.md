---
description: "Deterministic operations: update STATE.md, plan status, FIS checkboxes, standardized commits. Trigger on 'update state', 'mark story done', 'update FIS checkboxes', 'progress summary'."
context: fork
agent: general-purpose
user-invocable: true
argument-hint: "<operation> [args...] (operations: read-state, update-state, update-plan, update-fis, commit, branch, changelog, progress, stale)"
---

# Deterministic Operations Skill


Reliable, template-driven operations for state management, git conventions, and progress tracking. These operations follow strict patterns to avoid LLM interpretation drift.

> **Philosophy**: This skill provides structured templates and validation – it doesn't bypass the agent but gives it reliable patterns to follow. Think of it as "guardrails for deterministic work."


## INSTRUCTIONS

- Follow patterns exactly – do not improvise or add creative interpretation
- Validate inputs before making changes
- Report what was changed in a structured format


## GOTCHAS
- Improvising instead of following patterns exactly – this skill exists to prevent LLM interpretation drift
- Forgetting to update all three version locations on version bumps: CHANGELOG.md, .claude-plugin/marketplace.json, and plugin/.claude-plugin/plugin.json
- Creating the `State` document when it doesn't exist – initialization is the `init` skill's job; ops only reads/writes an existing `State` document as defined in the **Project Document Index**
- Letting Active Stories or Session Notes grow unbounded – apply maintenance rules on every write


## OPERATIONS

### 1. State File Operations

#### Read State

**Usage**: `read-state`

Parse the `State` document (path from **Project Document Index**, default: `docs/STATE.md`) and return a structured summary:
- Current phase and status (On Track / At Risk / Blocked)
- Active stories table (story, status, FIS, notes)
- Blockers (list)
- Recent decisions (list with dates)
- Session continuity notes (list with dates)
- Last updated timestamp

If the `State` document does not exist in the location defined by the **Project Document Index**, report "no state file" – do not create it or prompt the user.

#### Update State
Update specific fields in the `State` document (path from **Project Document Index**, default: `docs/STATE.md`):

**Usage**: `update-state <field> <value>`

If the `State` document does not exist in the location defined by the **Project Document Index**, report "no state file" – do not create it.

Supported fields:
- `phase`: Current phase name/number (e.g. `"Phase 2: Core Features"`)
- `status`: Overall project status – one of `On Track`, `At Risk`, `Blocked`
- `active-story`: Add or update an active story entry
  - Set status: `update-state active-story {story_id} "{story_name}" "In Progress"`
  - Mark done: `update-state active-story {story_id} Done` → removes the row from Active Stories
  - Set FIS: `update-state active-story {story_id} fis "{fis_path}"` → updates the FIS column
- `blocker`: Add or remove a blocker
  - Add: `update-state blocker "{description}"`
  - Remove: `update-state blocker remove "{description}"` → removes the matching entry
- `decision`: Add a recent decision entry with timestamp
- `note`: Add a session continuity note with timestamp

After any update, set `Last Updated` to current timestamp.

**Maintenance rules** (apply automatically on every write):
- **Active Stories table**: remove rows with status `Done` (they belong in plan.md, not state). This section tracks only _currently in-progress_ work — never accumulate completed milestone summaries here.
- **Recently Completed**: keep only the **last 2 milestones/releases**. Older milestones should already be captured in CHANGELOG.md. Use a one-line summary per milestone (not full release notes). If there are older milestones beyond the kept 2, condense into a single trailing line: `Previous: 0.14, 0.13, 0.12, ...`
- **Blockers**: remove entries that are no longer relevant (e.g. the blocking condition has been resolved, the related story is `Done`, or the blocker is older than 14 days with no recent activity)
- **Recent Decisions**: keep only the **last 10** entries; graduate older items to ADRs if warranted
- **Session Continuity Notes**: keep only the **last 5** entries; older entries are trimmed. Notes from completed milestones that have been captured elsewhere (CHANGELOG, Recently Completed) should be removed.
- **Overall size**: the `State` document should stay under ~60 lines. If it exceeds this after other maintenance rules, trim the oldest/longest entries first. This file is a snapshot of _current_ state, not a history log.

Format for the `State` document (see **Project Document Index**):
```markdown
# Project State

Last Updated: {YYYY-MM-DD HH:MM}

## Current Phase
Phase: {phase}
Status: {On Track | At Risk | Blocked}

## Active Stories
| Story | Status | FIS | Notes |
|-------|--------|-----|-------|
| {story_id}: {story_name} | {In Progress | Blocked} | {fis_path or –} | {brief note} |

## Recently Completed
- **{version/milestone}** ({date}): {one-line summary}
- **{version/milestone}** ({date}): {one-line summary}
Previous: {older milestone list, if any}

## Blockers
- {blocker description} _(added {date})_

## Recent Decisions
- [{date}] {decision}

## Session Continuity Notes
- [{date}] {note}
```

#### Update Plan Status
Update story status or FIS-field on a plan story row:

**Usage**:
- Set status: `update-plan <plan_path> <story_id> <status>`
- Set FIS field: `update-plan <plan_path> <story_id> fis "<fis_path>"`

Actions for status form:
- Set story **Status** field per the Status State Machine in [`${CLAUDE_PLUGIN_ROOT}/references/data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md). Forward transitions are skill-implicit; backward transitions (`Done → In Progress`, `In Progress → Spec Ready`) are valid only via explicit `update-plan` calls.
- Update Story Catalog table status column
- When setting to `Done`: check off all acceptance criteria checkboxes

Actions for `fis` form:
- Set the `**FIS**` field on the story's section header to `<fis_path>`
- Update the Story Catalog table FIS column to `<fis_path>`
- No-op if the field already equals `<fis_path>` (path-normalized)

#### Update FIS
Mutate a FIS document — mark checkboxes or append implementation observations.

**Usage**:
- Mark checkboxes: `update-fis <fis_path> <task_id|all>`
- Append observations: `update-fis <fis_path> observations <markdown-body>`

Actions for `<task_id|all>` form:
- When `task_id` is a specific ID: Mark that task's checkbox: `- [ ] **{task_id}**` → `- [x] **{task_id}**`
- When `task_id` is `all`: Mark ALL unchecked task checkboxes (`- [ ]` → `- [x]`), all success criteria checkboxes, and all Final Validation Checklist items in one pass
- Before marking done, verify that evidence of completion exists — the calling skill should have already performed verification. Do not re-run full verification; check that it was performed, not that it passes again.
- When all tasks are done (or using `all`): also mark success criteria and Final Validation Checklist items

Actions for `observations` form:
- `<markdown-body>` is freeform multi-line markdown passed verbatim — quote characters in the invocation (`'...'` / `"..."`) are illustrative framing, not delimiters; do not strip or shell-escape.
- Body constraints: the caller MUST format `<markdown-body>` using `####`-or-deeper headings only (typically `#### NOTICED BUT NOT TOUCHING` and/or `#### ASSUMPTIONS (AUTO_MODE)`). The body MUST NOT contain `## ` headings or another `### Run:` line — these would visually close the section and break the append protocol. Reject (no-op + `BLOCKED: invalid observations body`) if the body violates these constraints.
- Locate the `## Implementation Observations` section. If absent, append it to the end of the FIS using the standard lead paragraph from the FIS template.
- If the placeholder line `_No observations recorded yet._` is present, remove it (exact-string match only; no-op otherwise).
- Resolve a timestamp: prefer `date -u +"%Y-%m-%d %H:%M UTC"` so all run blocks share a single timezone and ordering is unambiguous.
- Normalize whitespace: ensure exactly one blank line precedes the new run block and the previous block ends with a trailing newline.
- Append the new run block to the section:
  ```
  ### Run: {YYYY-MM-DD HH:MM UTC}

  {markdown-body}
  ```
- No-op if `<markdown-body>` is empty or whitespace-only.
- **Idempotent retry**: if the most recent existing `### Run:` block has identical `<markdown-body>` (whitespace-normalized) AND its timestamp is within 2 minutes of the resolved timestamp, no-op — the call is a retry of an already-applied write. This makes the operation safe under exec-spec's Step 5b.4 retry-once protocol.
- Append-only otherwise: never rewrite or remove prior `### Run:` blocks.


### 2. Git Operations

#### Commit
Standardized commit message formatting:

**Format**: `{type}({scope}): {description}`

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `style`, `perf`, `ci`

**Usage**: `commit <type> <scope> <description>`

Rules:
- Scope is optional but recommended
- Description: imperative mood, lowercase, no period, max 72 chars
- If story context exists, append story ID: `feat(auth): add login form [S03]`

#### Branch
Standardized branch naming:

**Format**: `{type}/{story-id}-{slug}`

Types: `feat`, `fix`, `refactor`, `chore`, `docs`

**Usage**: `branch <type> <story-id> <slug>`

Example: `feat/S03-user-authentication`

Rules:
- Slug: lowercase, hyphen-separated, max 5 words
- Story ID from plan.md if available

#### Changelog Entry
Format a changelog entry:

**Usage**: `changelog <version> <entries...>`

Format:
```markdown
## [{version}] – {YYYY-MM-DD}

### Added
- {description} ([S{id}])

### Changed
- {description}

### Fixed
- {description}
```


### 3. Progress Tracking

#### Progress Summary
Generate progress summary from plan.md:

**Usage**: `progress <plan_path>`

Output:
```
## Progress Summary
- **Total Stories**: {N}
- **Completed**: {done} ({percentage}%)
- **Spec Ready**: {spec_ready}
- **In Progress**: {in_progress}
- **Pending**: {pending}
- **Blocked**: {blocked}

### By Phase
| Phase | Total | Done | Spec Ready | In Progress | Pending |
|-------|-------|------|------------|-------------|---------|
| {phase} | {n} | {n} | {n} | {n} | {n} |

### Current Wave
- Wave {N}: {status} ({done}/{total} stories complete)
```

#### Stale Detection
Detect stories that may be stale:

**Usage**: `stale <plan_path>`

A story is potentially stale if:
- Status is `In Progress` but no commits touch related files in 2+ days
- FIS exists but no task checkboxes are checked
- Dependencies are all `Done` but story hasn't started

Output: List of potentially stale stories with reasons.
