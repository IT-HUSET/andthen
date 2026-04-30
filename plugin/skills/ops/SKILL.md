---
description: "Deterministic operations: update STATE.md, plan status, FIS checkboxes, standardized commits. Trigger on 'update state', 'mark story done', 'update FIS checkboxes', 'progress summary'."
context: fork
agent: general-purpose
user-invocable: true
argument-hint: "<operation> [args...] (operations: read-state, update-state, update-plan, update-fis, update-fis observations, update-fis discovered-requirements, update-tech-debt append, commit, branch, changelog, progress, stale)"
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
- **Exception – `update-tech-debt append` IS allowed to create its target file**: this is the *one* documented deviation from the "ops never creates target files" rule. When the Tech Debt Backlog file (resolved from the **Project Document Index** `Tech Debt` row, default `docs/TECH-DEBT-BACKLOG.md`) does not exist, this form scaffolds it from the `# Technical Debt Backlog` template (canonical in `project-state-templates.md`; structure inlined in the `Update Tech Debt` form below) before appending. No other ops form may follow this pattern – do not extend the exception to State, Plan, FIS, or any future target.


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
- Set story **Status** field per the Status State Machine in [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md). Forward transitions are skill-implicit; backward transitions (`Done → In Progress`, `In Progress → Spec Ready`) are valid only via explicit `update-plan` calls.
- Update Story Catalog table status column
- When setting to `Done`: check off all acceptance criteria checkboxes

Actions for `fis` form:
- Set the `**FIS**` field on the story's section header to `<fis_path>`
- Update the Story Catalog table FIS column to `<fis_path>`
- No-op if the field already equals `<fis_path>` (path-normalized)

#### Update FIS
Mutate a FIS document — mark checkboxes, append implementation observations, or append discovered requirements.

**Usage**:
- Mark checkboxes: `update-fis <fis_path> <task_id|all>`
- Append observations: `update-fis <fis_path> observations <markdown-body>`
- Append discovered requirements: `update-fis <fis_path> discovered-requirements <markdown-body>`

Actions for `<task_id|all>` form:
- When `task_id` is a specific ID: Mark that task's checkbox: `- [ ] **{task_id}**` → `- [x] **{task_id}**`
- When `task_id` is `all`: Mark ALL unchecked task checkboxes (`- [ ]` → `- [x]`), all success criteria checkboxes, and all Final Validation Checklist items in one pass
- Before marking done, verify that evidence of completion exists — the calling skill should have already performed verification. Do not re-run full verification; check that it was performed, not that it passes again.
- When all tasks are done (or using `all`): also mark success criteria and Final Validation Checklist items

Actions for `observations` form:
- `<markdown-body>` is freeform multi-line markdown passed verbatim — quote characters in the invocation (`'...'` / `"..."`) are illustrative framing, not delimiters; do not strip or shell-escape.
- Body constraints: the caller MUST format `<markdown-body>` using `####`-or-deeper headings only (typically `#### NOTICED BUT NOT TOUCHING` and/or `#### ASSUMPTIONS (AUTO_MODE)`). The body MUST NOT contain `## ` headings or another `### Run:` line — these would visually close the section and break the append protocol. The body MUST NOT contain `#### DISCOVERED REQUIREMENTS` — that subsection belongs in the dedicated `discovered-requirements` op so the tagged-lane separation holds. Reject (no-op + `BLOCKED: invalid observations body`) if the body violates these constraints.
- Locate the `## Implementation Observations` section. If absent, append it to the end of the FIS using the standard lead paragraph from the FIS template.
- If the placeholder line `_No observations recorded yet._` is present, remove it (exact-string match only; no-op otherwise).
- Resolve a timestamp: prefer `date -u +"%Y-%m-%d %H:%M UTC"` so all run blocks share a single timezone and ordering is unambiguous.
- Normalize whitespace: ensure exactly one blank line precedes the new run block and the previous block ends with a trailing newline.
- Append the new run block to the section, tagging the header with the op name so concurrent op types do not share an idempotency lane:
  ```
  ### Run: {YYYY-MM-DD HH:MM UTC} — observations

  {markdown-body}
  ```
- No-op if `<markdown-body>` is empty or whitespace-only.
- **Idempotent retry**: if the most recent existing `### Run: ... — observations` block (matched by tag suffix) has identical `<markdown-body>` (whitespace-normalized) AND its timestamp is within 2 minutes of the resolved timestamp, no-op — the call is a retry of an already-applied write. Compare only against same-tag blocks; an intervening `— discovered-requirements` block does not affect the decision. This makes the operation safe under exec-spec's Step 5b.4 retry-once protocol when both ops write to `## Implementation Observations` in the same run.
- Append-only otherwise: never rewrite or remove prior `### Run:` blocks.

Actions for `discovered-requirements` form:
- `<markdown-body>` is freeform multi-line markdown passed verbatim — quote characters in the invocation (`'...'` / `"..."`) are illustrative framing, not delimiters; do not strip or shell-escape.
- Body constraints: the caller MUST format `<markdown-body>` using `####`-or-deeper headings only, specifically `#### DISCOVERED REQUIREMENTS` for the requirement block. The body MUST NOT contain `## ` headings or another `### Run:` line. Reject (no-op + `BLOCKED: invalid discovered-requirements body`) if the body violates these constraints or lacks `#### DISCOVERED REQUIREMENTS`.
- Locate the `## Implementation Observations` section. If absent, append it to the end of the FIS using the standard lead paragraph from the FIS template.
- If the placeholder line `_No observations recorded yet._` is present, remove it (exact-string match only; no-op otherwise).
- Resolve a timestamp: prefer `date -u +"%Y-%m-%d %H:%M UTC"` so all run blocks share a single timezone and ordering is unambiguous.
- Normalize whitespace: ensure exactly one blank line precedes the new run block and the previous block ends with a trailing newline.
- Append the new run block to the section, tagging the header with the op name so concurrent op types do not share an idempotency lane:
  ```
  ### Run: {YYYY-MM-DD HH:MM UTC} — discovered-requirements

  {markdown-body}
  ```
- No-op if `<markdown-body>` is empty or whitespace-only.
- **Idempotent retry**: if the most recent existing `### Run: ... — discovered-requirements` block (matched by tag suffix) has identical `<markdown-body>` (whitespace-normalized) AND its timestamp is within 2 minutes of the resolved timestamp, no-op. Compare only against same-tag blocks; an intervening `— observations` block does not affect the decision.
- Append-only otherwise: never rewrite or remove prior `### Run:` blocks.

#### Update Tech Debt
Append tech-debt entries (typically deferred review findings) to the project's Tech Debt Backlog.

**Usage**: `update-tech-debt append <markdown-body>`

Resolve the target file path from the **Project Document Index** `Tech Debt` row (default `docs/TECH-DEBT-BACKLOG.md`).

Actions for `append` form:
- `<markdown-body>` is freeform multi-line markdown passed verbatim — quote characters in the invocation (`'...'` / `"..."`) are illustrative framing, not delimiters; do not strip or shell-escape.
- Body constraints: the caller MUST format `<markdown-body>` using `####`-or-deeper headings only (typically `#### DEFERRED FINDINGS`). The body MUST NOT contain `## ` headings or another `### Run:` line — these would visually close the section and break the append protocol. Reject (no-op + `BLOCKED: invalid tech-debt body`) if the body violates these constraints.
- **File creation exception** (the *one* documented deviation from "ops never creates target files" — see GOTCHAS): if the resolved target file does not exist, scaffold it from the `# Technical Debt Backlog` template defined in `project-state-templates.md` (H1 `# Technical Debt Backlog` + H2 `## High` / `## Medium` / `## Low` in fixed order, each carrying placeholder line `_No tech debt recorded yet._`) before appending. Do not extend this exception to any other ops form.
- **Severity routing**: each entry is a top-level `- **{title}** ...` bullet with its `Severity:` line nested as a sub-bullet. Parse the `Severity:` value and route the entry to the matching H2 section (`High` / `Medium` / `Low`). Default to `Medium` when the severity is missing or unrecognized. When a single body batches mixed severities, split into per-severity run blocks sharing one timestamp — one new run block under each affected severity H2.
- For each affected severity section: if the placeholder line `_No tech debt recorded yet._` is present, remove it (exact-string match only; no-op otherwise).
- Resolve a timestamp: prefer `date -u +"%Y-%m-%d %H:%M UTC"` so all run blocks share a single timezone and ordering is unambiguous.
- Normalize whitespace: ensure exactly one blank line precedes each new run block and the previous block ends with a trailing newline.
- Append the new run block(s) under the matching severity H2, tagging the header with the op name so concurrent op types do not share an idempotency lane:
  ```
  ### Run: {YYYY-MM-DD HH:MM UTC} — tech-debt

  {filtered-body for this severity}
  ```
- No-op if `<markdown-body>` is empty or whitespace-only — and do not create the target file in that case.
- **Idempotent retry**: if the most recent existing `### Run: ... — tech-debt` block under the affected severity H2 (matched by tag suffix) has identical filtered body (whitespace-normalized) AND its timestamp is within 2 minutes of the resolved timestamp, no-op for that severity. Compare only against same-tag blocks. This makes the operation safe under exec-spec's Step 5b.4 retry-once protocol and parallels `update-fis observations` idempotency, scoped per severity H2.
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
