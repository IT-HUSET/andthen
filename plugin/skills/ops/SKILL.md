---
description: Deterministic operations: update STATE.md, plan status, FIS checkboxes, standardized commits. Trigger on 'update state', 'mark done', 'progress summary'.
context: fork
agent: general-purpose
user-invocable: true
---

# Deterministic Operations Skill

Reliable, template-driven operations for state management, git conventions, and progress tracking. These operations follow strict patterns to avoid LLM interpretation drift.

> **Philosophy**: This skill provides structured templates and validation — it doesn't bypass the agent but gives it reliable patterns to follow. Think of it as "guardrails for deterministic work."


## INSTRUCTIONS

- Follow patterns exactly — do not improvise or add creative interpretation
- Validate inputs before making changes
- Report what was changed in a structured format


## GOTCHAS
- Improvising instead of following patterns exactly — this skill exists to prevent LLM interpretation drift
- Forgetting to update both CHANGELOG.md and marketplace.json on version bumps


## OPERATIONS

### 1. State File Operations

#### Read State
Parse `docs/STATE.md` and return structured summary:
- Current phase/milestone
- Active stories (in-progress)
- Blockers
- Last updated timestamp

#### Update State
Update specific fields in `docs/STATE.md`:

**Usage**: `update-state <field> <value>`

Supported fields:
- `phase`: Current phase name/number
- `active-story`: Story ID currently being worked on
- `blocker`: Add/remove a blocker entry
- `note`: Add a session continuity note with timestamp

Format for entries:
```markdown
## Current State
- **Phase**: {phase}
- **Active Story**: {story_id} — {story_name}
- **Last Updated**: {YYYY-MM-DD HH:MM}

## Blockers
- [ ] {blocker description} _(added {date})_

## Session Notes
- [{date}] {note}
```

#### Update Plan Status
Update story status fields in `plan.md`:

**Usage**: `update-plan <plan_path> <story_id> <status>`

Actions:
- Set story **Status** field: `Pending` → `In Progress` → `Done`
- Update Story Catalog table status column
- When setting to `Done`: check off all acceptance criteria checkboxes

#### Update FIS Checkboxes
Check off task/criteria checkboxes in a FIS document:

**Usage**: `update-fis <fis_path> <task_id> [done]`

Actions:
- Mark task checkbox: `- [ ] **{task_id}**` → `- [x] **{task_id}**`
- Before marking done, verify the task meets 4-dimension criteria per `${CLAUDE_PLUGIN_ROOT}/references/verification-patterns.md`
- When all tasks done: also mark success criteria and Final Validation Checklist items


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
## [{version}] — {YYYY-MM-DD}

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
- **In Progress**: {in_progress}
- **Pending**: {pending}
- **Blocked**: {blocked}

### By Phase
| Phase | Total | Done | In Progress | Pending |
|-------|-------|------|-------------|---------|
| {phase} | {n} | {n} | {n} | {n} |

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
