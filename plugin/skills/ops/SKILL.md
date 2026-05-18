---
description: "Deterministic operations: update STATE.md, plan status, FIS checkboxes, standardized commits. Trigger on 'update state', 'mark story done', 'update FIS checkboxes', 'progress summary'."
context: fork
agent: general-purpose
user-invocable: true
argument-hint: "<operation> [args...] (operations: read-state, update-state, update-plan, update-plan-fis, update-fis, update-fis observations, update-fis discovered-requirements, update-tech-debt append, commit, branch, changelog, progress, stale)"
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

### Append-Run Block Protocol

Applies to the `observations`, `discovered-requirements`, and `update-tech-debt append` forms. `<markdown-body>` is freeform multi-line markdown passed verbatim – quote characters in the invocation (`'...'` / `"..."`) are illustrative framing, not delimiters; do not strip or shell-escape. Each form names its own tag suffix, target section, and body-constraint variant – the following protocol is common to all three:

- **Empty/whitespace-only body**: no-op; do not append a run block and do not create the target file (for `update-tech-debt append`).
- **Body constraints**: `<markdown-body>` MUST use `####`-or-deeper headings only. The body MUST NOT contain `## ` headings or another `### Run:` line – these would visually close the section and break the append protocol.
- **Placeholder removal**: if the placeholder line `_No observations recorded yet._` or `_No tech debt recorded yet._` is present in the target section, remove it (exact-string match only; no-op otherwise).
- **Timestamp resolution**: resolve a timestamp via `date -u +"%Y-%m-%d %H:%M UTC"` so all run blocks share a single timezone and ordering is unambiguous.
- **Whitespace normalization**: ensure exactly one blank line precedes the new run block and the previous block ends with a trailing newline.
- **Run-block frame**: append the run block tagged with the form's own suffix:
  ```
  ### Run: {YYYY-MM-DD HH:MM UTC} – {tag}

  {markdown-body}
  ```
- **Append-only**: never rewrite or remove prior `### Run:` blocks.
- **Idempotent retry** (2-minute window): if the most recent existing `### Run: ... – {tag}` block (matched by tag suffix) has identical body content (whitespace-normalized; for `update-tech-debt append` compare the per-severity filtered body against the matching severity block, not the full body) AND its timestamp is within 2 minutes of the resolved timestamp, no-op for that block. Compare only against same-tag blocks – an intervening block with a different tag suffix does not affect the decision.

### 1. State File Operations

#### Read State

**Usage**: `read-state`

Parse the `State` document (path from **Project Document Index**, default: `docs/STATE.md`) and return: current phase/status, active stories table, blockers, recent decisions, session continuity notes, last updated timestamp. If absent, report "no state file" – do not create it.

#### Update State
Update specific fields in the `State` document (path from **Project Document Index**, default: `docs/STATE.md`):

**Usage**: `update-state <field> <value>`

If the `State` document does not exist in the location defined by the **Project Document Index**, report "no state file" – do not create it.

Supported fields:
- `phase`: Current phase name/number (e.g. `"Phase 2: Core Features"`)
- `status`: Overall project status – one of `On Track`, `At Risk`, `Blocked`
- `active-story`: Add or update an active story entry
  - Set status: `update-state active-story {story_id} "{story_name}" "In Progress"`
  - Mark done: `update-state active-story {story_id} Done` → removes the row from Active Stories. Token is literal `Done` (capital D), distinct from the lowercase `plan.json` `done` enum used by `update-plan`.
  - Set FIS: `update-state active-story {story_id} fis "{fis_path}"` → updates the FIS column
- `blocker`: Add or remove a blocker
  - Add: `update-state blocker "{description}"`
  - Remove: `update-state blocker remove "{description}"` → removes the matching entry
- `decision`: Add a recent decision entry with timestamp
- `note`: Add a session continuity note with timestamp

After any update, set `Last Updated` to current timestamp.

**Maintenance rules** (apply automatically on every write):
- **Active Stories table**: remove rows with status `Done` (they belong in `plan.json`, not state). This section tracks only _currently in-progress_ work – never accumulate completed milestone summaries here.
- **Recently Completed**: keep only the **last 2 milestones/releases**. Older milestones should already be captured in CHANGELOG.md. Use a one-line summary per milestone (not full release notes). If there are older milestones beyond the kept 2, condense into a single trailing line: `Previous: 0.14, 0.13, 0.12, ...`
- **Blockers**: remove entries that are no longer relevant (e.g. the blocking condition has been resolved, the related story is `Done`, or the blocker is older than 14 days with no recent activity)
- **Recent Decisions**: keep only the **last 10** entries; graduate older items to ADRs if warranted
- **Session Continuity Notes**: keep only the **last 5** entries; older entries are trimmed. Notes from completed milestones that have been captured elsewhere (CHANGELOG, Recently Completed) should be removed.
- **Overall size**: the `State` document should stay under ~60 lines. If it exceeds this after other maintenance rules, trim the oldest/longest entries first. This file is a snapshot of _current_ state, not a history log.

State document format: see [`project-state-templates.md`](${CLAUDE_PLUGIN_ROOT}/references/project-state-templates.md).

#### Update Plan Status
Mutate `stories[].status` in `plan.json` per [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md).

**Usage**: `update-plan <plan_path> <story_id> <status>`

Actions:
- Read `plan.json`, locate the entry in `stories[]` whose `id === <story_id>`, validate `<status>` against the closed enum (`pending` / `spec-ready` / `in-progress` / `done` / `skipped` / `blocked`), set the field, write back with deterministic formatting (2-space indent, schema key order, trailing newline).
- Forward transitions are skill-implicit per the schema's Write Authority; backward transitions (e.g. `done → spec-ready`) are valid only via explicit `update-plan` calls.
- Reject unknown status values with `BLOCKED: invalid status "<value>" – must be one of pending, spec-ready, in-progress, done, skipped, blocked`.
- No-op when `status` already equals the target value.

#### Update Plan FIS
Mutate `stories[].fis` in `plan.json`.

**Usage**: `update-plan-fis <plan_path> <story_id> <fis_path>`

Actions:
- Read `plan.json`, locate the entry in `stories[]` whose `id === <story_id>`, set `fis` to `<fis_path>` (relative POSIX), write back.
- Reject duplicates: if any other story already has `fis === <fis_path>`, refuse with `BLOCKED: fis path "<fis_path>" already used by story <other-id> – the 1:1 story↔FIS invariant must hold`.
- No-op when `fis` already equals `<fis_path>` (path-normalized).

#### Update FIS
Mutate a FIS document – mark checkboxes, append implementation observations, or append discovered requirements.

**Usage**:
- Mark checkboxes: `update-fis <fis_path> <task_id|all>`
- Append observations: `update-fis <fis_path> observations <markdown-body>`
- Append discovered requirements: `update-fis <fis_path> discovered-requirements <markdown-body>`

Actions for `<task_id|all>` form:
- When `task_id` is a specific ID: Mark that task's checkbox: `- [ ] **{task_id}**` → `- [x] **{task_id}**`
- When `task_id` is `all`: Mark ALL unchecked task checkboxes (`- [ ]` → `- [x]`) plus every proof-surface checkbox set in one pass:
  - **`## Acceptance Scenarios`** – each scenario is one canonical-shape checkbox; the canonical scenario shape is defined in [`fis-authoring-guidelines.md`](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md) under *Acceptance Scenarios and Proof-of-Work*. Flip each scenario's `- [ ]` to `- [x]` while preserving the bold-label content. Example: `- [ ] **S01 [OC01] [TI01,TI03] Happy path**` → `- [x] **S01 [OC01] [TI01,TI03] Happy path**`.
  - **`## Structural Criteria`** – each checkbox flips `- [ ]` to `- [x]`.
  - **`## Final Validation Checklist`** – only when the section exists (it is optional content). When present, each checkbox flips `- [ ]` to `- [x]`.
- Before marking done, verify that evidence of completion exists – the calling skill should have already performed verification; do not re-run it. When all tasks are done (or using `all`): also mark Acceptance Scenarios, Structural Criteria, and Final Validation Checklist items (when present).

Actions for `observations` form:
- Body constraint variant: MUST use `####`-or-deeper headings (typically `#### NOTICED BUT NOT TOUCHING` and/or `#### ASSUMPTIONS (AUTO_MODE)`). MUST NOT contain `#### DISCOVERED REQUIREMENTS` – that subsection belongs in the `discovered-requirements` form so tagged-lane separation holds. Reject (no-op + `BLOCKED: invalid observations body`) if violated.
- Tag suffix: `– observations`. Target section: `## Implementation Observations`. If absent, append it to the end of the FIS using the standard lead paragraph from the FIS template.
- Apply the Append-Run Block Protocol above.

Actions for `discovered-requirements` form:
- Body constraint variant: MUST contain `#### DISCOVERED REQUIREMENTS`. Reject (no-op + `BLOCKED: invalid discovered-requirements body`) if the body lacks `#### DISCOVERED REQUIREMENTS`.
- Tag suffix: `– discovered-requirements`. Target section: `## Implementation Observations`. If absent, append it to the end of the FIS using the standard lead paragraph from the FIS template.
- Apply the Append-Run Block Protocol above.

#### Update Tech Debt
Append tech-debt entries (typically deferred review findings) to the project's Tech Debt Backlog.

**Usage**: `update-tech-debt append <markdown-body>`

Resolve the target file path from the **Project Document Index** `Tech Debt` row (default `docs/TECH-DEBT-BACKLOG.md`).

Actions for `append` form:
- Body constraint variant: MUST use `####`-or-deeper headings (typically `#### DEFERRED FINDINGS`). Reject (no-op + `BLOCKED: invalid tech-debt body`) if violated.
- **File creation exception** (the *one* documented deviation from "ops never creates target files" – see GOTCHAS): if the resolved target file does not exist, scaffold it from the `# Technical Debt Backlog` template defined in `project-state-templates.md` (H1 `# Technical Debt Backlog` + H2 `## High` / `## Medium` / `## Low` in fixed order, each carrying placeholder line `_No tech debt recorded yet._`) before appending. Do not extend this exception to any other ops form.
- **Severity routing**: each entry is a top-level `- **{title}** ...` bullet with its `Severity:` line nested as a sub-bullet. Parse the `Severity:` value and route the entry to the matching H2 section (`High` / `Medium` / `Low`). Default to `Medium` when the severity is missing or unrecognized. When a single body batches mixed severities, split into per-severity run blocks sharing one timestamp – one new run block under each affected severity H2.
- Tag suffix: `– tech-debt`. Idempotency lane scoped per severity H2.
- Apply the Append-Run Block Protocol above (once per affected severity section).


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
- Story ID from `plan.json` if available

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
Generate a progress summary from `plan.json`:

**Usage**: `progress <plan_path>`

Output:
```
## Progress Summary
- **Total Stories**: {N}
- **Done**: {done} ({percentage}%)
- **In Progress**: {in_progress}
- **Spec Ready**: {spec_ready}
- **Pending**: {pending}
- **Skipped**: {skipped}
- **Blocked**: {blocked}

### By Phase
| Phase | Total | Done | In Progress | Spec Ready | Pending | Skipped/Blocked |
|-------|-------|------|-------------|------------|---------|-----------------|
| {phase} | {n} | {n} | {n} | {n} | {n} | {n} |

### Current Wave
- Wave {N}: {status} ({done}/{total} stories complete)
```

#### Stale Detection
Detect stories that may be stale:

**Usage**: `stale <plan_path>`

A story is potentially stale if:
- `fis` exists but no task checkboxes are checked
- All entries in `dependsOn` have `status: "done"` but the story is still `pending` or `spec-ready`

Output: List of potentially stale stories with reasons.
