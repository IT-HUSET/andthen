---
description: "Deterministic operations: update STATE.md, plan status, FIS checkboxes, standardized commits. Trigger on 'update state', 'mark story done', 'update FIS checkboxes', 'progress summary'."
context: fork
agent: general-purpose
user-invocable: true
argument-hint: "<operation> [args...] (operations: read-state, update-state, update-plan, update-plan-fis, update-fis, update-fis observations, update-fis discovered-requirements, update-fis design-change, update-ledger (add|reconcile|withdraw|bump-recurrence|override-close), update-tech-debt append, update-learnings add, update-learnings error, commit, branch, changelog, progress, stale)"
---

# Deterministic Operations Skill


Template-driven operations following strict patterns to avoid LLM interpretation drift.


## INSTRUCTIONS

- Follow the operation grammars exactly; improvisation defeats determinism. Validate inputs before mutating, and report changes in a structured format.


## GOTCHAS
- Forgetting to update all three version locations on version bumps: CHANGELOG.md, .claude-plugin/marketplace.json, and plugin/.claude-plugin/plugin.json
- Creating the `State` document when it doesn't exist – initialization is the andthen:init skill's job; ops only reads/writes an existing `State` document as defined in the **Project Document Index**
- Letting Active Stories or Session Notes grow unbounded – apply maintenance rules on every write
- **File-creation exceptions** – two forms may create their target file: `update-tech-debt append` (Tech Debt Backlog only; mechanics in *Update Tech Debt*) and `update-ledger add` (Reconciliation Ledger only; mechanics in *Update Reconciliation Ledger*). No other form may – do not extend to State, Plan, FIS, or any future target. Ledger *transition* forms (`reconcile`, `withdraw`, `bump-recurrence`, `override-close`) never create the file; they require an existing matching entry.


## OPERATIONS

### Append-Run Block Protocol

Applies to the `observations`, `discovered-requirements`, `design-change`, and `update-tech-debt append` forms. `<markdown-body>` is freeform multi-line markdown passed verbatim – quote characters in the invocation (`'...'` / `"..."`) are illustrative framing, not delimiters; do not strip or shell-escape. Each form names its own tag suffix, target section, and body-constraint variant – the following protocol is common to all four:

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
Mutate a FIS document – mark checkboxes, append implementation observations, append discovered requirements, or apply a design-change amendment.

**Usage**:
- Mark checkboxes: `update-fis <fis_path> <task_id|all>`
- Append observations: `update-fis <fis_path> observations <markdown-body>`
- Append discovered requirements: `update-fis <fis_path> discovered-requirements <markdown-body>`
- Apply design-change amendment: `update-fis <fis_path> design-change <markdown-body>`

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

Actions for `design-change` form:
- Body constraint variant: MUST contain `#### DESIGN CHANGE`, `#### ADR`, and one or more exact amendment pairs with `Old:` and `New:` fenced blocks. Body headings must be `####`-or-deeper and MUST NOT contain `## ` headings or another `### Run:` line. Reject (no-op + `BLOCKED: invalid design-change body`) if the ADR entry is missing, if an old/new pair is missing, or if the heading constraints are violated.
- Idempotent retry and all-or-nothing: before rejecting missing `Old:` spans, check the most recent same-tag run block within the 2-minute retry window. If its body is identical and every missing `Old:` span's paired `New:` span is already present in the allowed Intent/scenario region, no-op instead of blocking. If the paired `New:` spans are present but the audit block is missing, append the audit block and report that the retry repaired the audit trail. Otherwise validate every pair before applying any replacement; reject (no-op + `BLOCKED: invalid design-change body`) if any `Old:` span does not exactly match the current FIS text, and apply none if one pair fails. Treat replacements plus audit append as one logical mutation: if the audit append cannot be written, do not apply replacements.
- Apply each exact old/new replacement to the FIS Intent and/or Acceptance Scenario text only. Do not edit task checkboxes, Structural Criteria, plan provenance, or Implementation Observations through this form.
- Append the same body to `## Implementation Observations` using tag suffix `– design-change` via the Append-Run Block Protocol, so the mutable spec edit is auditable and retry-safe. This form is distinct from `discovered-requirements`; do not use it for missing requirements or edge cases that should stay append-only.

#### Update Reconciliation Ledger
Deterministic mutator for the Reconciliation Ledger – the durable, greppable record of deliberate spec-vs-code drift. Schema, stable-ID derivation, status lifecycle, and match/recurrence/escalation rules are owned by [`reconciliation-ledger.md`](${CLAUDE_PLUGIN_ROOT}/references/reconciliation-ledger.md); this form is the only sanctioned write path. Modeled on the `update-fis` write discipline: atomic, transition-audited, AUTO_MODE-safe, rejecting malformed transitions. **Single-document** – it mutates only the ledger; the completion-presentation gate that *reads* the ledger lives in the orchestrating skills (`exec-spec` / `exec-plan`), not here.

The caller passes the **FIS-adjacent ledger path** (`{fis-without-ext}.reconciliation-ledger.md`, resolved per [`reconciliation-ledger.md`](${CLAUDE_PLUGIN_ROOT}/references/reconciliation-ledger.md)) as the first argument; `ops` mutates exactly that file and does not discover a path. There is no project-global ledger.

**Usage**:
- Add an OPEN entry: `update-ledger add <ledger-path> <stable-id> <class> <stale-targets> <source-run> [notes]`
- Close on applied reconciliation: `update-ledger reconcile <ledger-path> <stable-id> [design-change+ADR-evidence]`
- Withdraw with falsifier: `update-ledger withdraw <ledger-path> <stable-id> <falsifier>`
- Bump recurrence (may escalate): `update-ledger bump-recurrence <ledger-path> <stable-id>`
- Record close-gate override: `update-ledger override-close <ledger-path> <stable-id> <reason>`

Common rules:
- Reuse the existing class vocabulary only (`code-defect | spec-stale | design-changed | ambiguous-intent`); reject any other class. Status values are `OPEN | RECONCILE REQUIRED | CLOSED | WITHDRAWN`.
- `<stable-id>` is the `{relative-path}:{class}:{normalized-title-slug}` value. Match entries primarily on `{relative-path}:{class}` when that key is unique; when multiple entries share it, use the full stable ID to select the intended entry. All entries live under `## Entries` in the schema shape from the reference; field edits are surgical single-line replacements so the file diffs cleanly.
- Resolve dates via `date -u +"%Y-%m-%d"`; set `Updated:` on every mutation.
- **Atomicity**: validate the requested transition fully before writing; apply nothing on a rejected transition. Treat an entry's field edits as one logical mutation.
- **AUTO_MODE-safe**: never prompt; reject malformed input with a `BLOCKED:` line and no-op.

Actions for `add` form:
- **File-creation exception** (one of the two documented deviations from "ops never creates target files" – see GOTCHAS): if the passed ledger file does not exist, scaffold it from the canonical ledger template in `reconciliation-ledger.md` (H1 `# Reconciliation Ledger` + lead paragraph + `## Entries` carrying placeholder `_No reconciliation entries recorded yet._`) before appending.
- Remove the `_No reconciliation entries recorded yet._` placeholder (exact-string match only) when appending the first entry.
- Append a new entry with `Status: OPEN`, the given `Class:`, `Stale targets:`, `Source run:`, `Recurrence: 1`, `Falsifier: –`, `Override reason: –`, and `Created:`/`Updated:` set to today.
- **Idempotent**: no-op only if a non-terminal (OPEN / RECONCILE REQUIRED) entry already matches the full stable ID. If another non-terminal entry shares `{relative-path}:{class}` but has a different slug, append the new entry.
- **Terminal-match re-open**: if the stable ID matches a terminal entry (`CLOSED`/`WITHDRAWN`) by the common matching rule above – unique `{relative-path}:{class}` first, full stable ID only when that key is ambiguous – do **not** append a second entry. Instead re-open that entry **in place** – transition it to `OPEN`, append the refuting evidence to `Notes:` while preserving the prior `Falsifier:` as history, and set `Updated:`. This requires refuting evidence in the call (pass it as the `[notes]` argument); reject (no-op + `BLOCKED: re-open requires refuting evidence`) when none is supplied, so a suppressed entry never silently re-creates. On a terminal re-open only the refuting evidence is consumed; `<class>`/`<stale-targets>`/`<source-run>` must restate the existing entry's values and are not overwritten.
- Reject (no-op + `BLOCKED: invalid ledger class "<value>"`) on an out-of-vocabulary class.

Actions for `reconcile` form:
- Require an existing matching entry in `OPEN` or `RECONCILE REQUIRED`. For `RECONCILE REQUIRED`, require non-empty evidence that the sanctioned `update-fis design-change` amendment and ADR path completed; reject a bare `update-ledger reconcile <ledger-path> <stable-id>` with `BLOCKED: reconcile requires design-change + ADR evidence for RECONCILE REQUIRED`. Transition valid entries to `CLOSED`; set `Updated:`.
- Reject (no-op + `BLOCKED: no matching ledger entry for <stable-id>`) when no entry matches; reject when the entry is already terminal (`CLOSED`/`WITHDRAWN`).

Actions for `withdraw` form:
- Require an existing matching non-terminal entry and a non-empty `<falsifier>`. Transition to `WITHDRAWN`; record `Falsifier:`; set `Updated:`.
- Reject (no-op + `BLOCKED: withdraw requires a falsifier`) when the falsifier is empty; reject when no entry matches.

Actions for `bump-recurrence` form:
- Require an existing matching `OPEN` entry. For `spec-stale`/`design-changed`: increment `Recurrence:`; when it reaches `2`, transition the entry to `RECONCILE REQUIRED`. Further bumps neither duplicate nor re-nag. Set `Updated:`.
- **No-op** for `code-defect`/`ambiguous-intent` entries (these classes do not escalate) – report the no-op, do not error.
- Reject (no-op + `BLOCKED: no matching ledger entry for <stable-id>`) when no entry matches.

Actions for `override-close` form:
- Require an existing matching `OPEN`/`RECONCILE REQUIRED` entry and a non-empty `<reason>`. Record the `Override reason:` against that entry; set `Updated:`. The entry keeps its status (the override unblocks the completion-presentation gate; it does not close the entry).
- Reject (no-op + `BLOCKED: override-close requires a reason`) when the reason is empty; reject when no entry matches. A blanket bypass with no recorded reason is forbidden.

#### Update Tech Debt
Append tech-debt entries (typically deferred review findings) to the project's Tech Debt Backlog.

**Usage**: `update-tech-debt append <markdown-body>`

Resolve the target file path from the **Project Document Index** `Tech Debt` row (default `docs/TECH-DEBT-BACKLOG.md`).

Actions for `append` form:
- Body constraint variant: MUST use `####`-or-deeper headings (typically `#### DEFERRED FINDINGS`). Reject (no-op + `BLOCKED: invalid tech-debt body`) if violated.
- **File creation exception** (the *one* documented deviation from "ops never creates target files" – see GOTCHAS): if the resolved target file does not exist, scaffold it from the `# Technical Debt Backlog` template defined in `project-state-templates.md` (H1 `# Technical Debt Backlog` + H2 `## High` / `## Medium` / `## Low` in fixed order, each carrying placeholder line `_No tech debt recorded yet._`) before appending.
- **Severity routing**: each entry is a top-level `- **{title}** ...` bullet with its `Severity:` line nested as a sub-bullet. Parse the `Severity:` value and route the entry to the matching H2 section (`High` / `Medium` / `Low`). Default to `Medium` when the severity is missing or unrecognized. When a single body batches mixed severities, split into per-severity run blocks sharing one timestamp – one new run block under each affected severity H2.
- Tag suffix: `– tech-debt`. Idempotency lane scoped per severity H2.
- Apply the Append-Run Block Protocol above (once per affected severity section).

#### Update Learnings
Append defensive-knowledge entries to the project's Learnings file. **Not a run-block append** – LEARNINGS is a topic-organized knowledge base, not a chronological log (template: `project-state-templates.md` `## LEARNINGS.md`).

**Usage**:
- Topic entry: `update-learnings add <topic> <entry-markdown>`
- Error-pattern row: `update-learnings error <error> <type> [conclusion]`

Resolve the target file path from the **Project Document Index** `Learnings` row (default `docs/LEARNINGS.md`). If the file does not exist, refuse with `BLOCKED: Learnings document not found at <path> – run the andthen:init skill to scaffold it`; do not create it (the andthen:init skill owns creation).

Actions for `add` form:
- `<entry-markdown>`: a single bullet. MUST start with `- **{title}**` and be under 200 characters. Reject with `BLOCKED: invalid learnings entry – must start with "- **{title}**" and stay under 200 chars` if violated.
- Locate `## {topic}` case-insensitively. If absent, create as a new H2 above `## Error Patterns` (or at EOF if Error Patterns is also absent). Append the bullet under the topic.
- **Idempotency**: no-op if a bullet matching the `- **{title}**` prefix already exists in the topic.

Actions for `error` form:
- `<type>`: `Deterministic` / `Infrastructure`. Default `Deterministic`.
- `[conclusion]`: optional; omit or pass `-` for empty.
- Locate the `## Error Patterns` table. Append `| {error} | {type} | {conclusion} |`. If the section or table is missing, recreate as `## Error Patterns` H2 + header `| Error | Type | Conclusion |` + separator before appending.
- **Idempotency**: if a row with identical `{error}` exists, update its other columns; do not duplicate.
- Graduation (row → topic section) is judgment-driven; rows stay until a human promotes them.

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
