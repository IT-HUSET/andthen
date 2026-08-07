---
description: Deterministic operations – update shared/local state, plan status, story ownership, FIS checkboxes, standardized commits. Trigger on 'mark story done', 'claim story', 'update FIS checkboxes', 'progress summary'.
context: fork
agent: general-purpose
user-invocable: true
argument-hint: "<operation> [args...] (operations: read-state, update-state, update-plan, update-plan-fis, update-plan-owner, update-fis, update-fis observations, update-fis discovered-requirements, update-fis design-change, update-fis decision-note, update-decisions still-current, update-ledger (add|reconcile|withdraw|bump-recurrence|override-close), update-tech-debt append, update-learnings add, update-learnings remove, update-learnings error, commit, branch, changelog, progress, stale)"
---

# Deterministic Operations Skill

Template-driven operations to avoid LLM interpretation drift: follow the operation grammars exactly and validate inputs before mutating, then report changes in a structured format.


## GOTCHAS
- Creating the shared `State` document when it doesn't exist – initialization is the andthen:init skill's job; ops only reads/writes an existing shared `State` document as defined in the **Project Document Index**.
- Letting Active Stories (shared) or Session Continuity Notes (local) grow unbounded – apply the maintenance rules under *Update State* on every write.
- **File-creation exceptions** – four operations may create their target file: `update-tech-debt append` (Tech Debt Backlog only; mechanics in *Update Tech Debt*), `update-ledger add` (Reconciliation Ledger only; mechanics in *Update Reconciliation Ledger*), `update-state note`/`update-state focus` (the **gitignored** `State (local)` document, plus its `.gitignore` entry – the one sanctioned side-write; mechanics in *Update State*), and `update-learnings` (topic **shard** files under `learnings/` only – never the Learnings index itself; mechanics in *Update Learnings*). No other form may – do not extend to the shared State, Plan, FIS, or any future target. Ledger *transition* forms (`reconcile`, `withdraw`, `bump-recurrence`, `override-close`) never create the file; they require an existing matching entry.


## OPERATIONS

### Append-Run Block Protocol

See [append-run-block-protocol.md](references/append-run-block-protocol.md).

### 1. State File Operations

State is split so teammates don't collide on one shared file: the **shared `State`** (Project Document Index `State` row, default `docs/STATE.md`) is committed and team-wide; the **local `State (local)`** (Project Document Index `State (local)` row, default `docs/STATE.local.md`) is **gitignored** and per-developer.

#### Read State

**Usage**: `read-state`

Parse the shared `State` document and, when present, the local `State (local)` document, and return a merged view: current phase/status, active stories, blockers, recent decisions, plus the local My Current Focus and session continuity notes, and each file's last-updated timestamp. The local file is optional – when absent, omit its sections (do not create it on read). If the shared `State` document is absent, report "no shared state file" – do not create it – but still return the local sections and the plan-derived Active Stories when resolvable.

**Active Stories sourcing**: when one or more `plan.json` files govern current work (discoverable via the Project Document Index `Specs & Plans` location or the FIS paths the State references), derive the Active Stories view as the union across them of stories that are `in-progress` **or claimed** (`owner` set, `status` not `done`/`skipped`) – claims stay visible before a story starts. A plan governs only while it has undone stories (the **Governing plan** predicate in `plan-schema.md`); story ids are per-plan, so resolve them per governing plan and annotate each derived row with its plan when several contribute. The stored `## Active Stories` table is the fallback for projects without a governing `plan.json`; stored rows whose story id is in no governing plan (ad-hoc work) always render.

#### Update State
Update specific fields, routed to the shared or local State document by field.

**Usage**: `update-state <field> <value>`

**Shared fields** → shared `State` document. If it does not exist, report "no shared state file" – do not create it (the andthen:init skill owns creation).
- `phase`: Current phase name/number (e.g. `"Phase 2: Core Features"`)
- `status`: Overall project status – one of `On Track`, `At Risk`, `Blocked`
- `active-story`: Add or update an active story entry. **Planless fallback only** – when the story id resolves in a governing `plan.json`, add/update forms no-op, reporting `NO-OP: story "<story_id>" is plan-governed – use update-plan / update-plan-owner` so the redirect is never silent; ad-hoc ids (in no governing plan) still write stored rows. `Done` removal still prunes stored rows.
  - Set status: `update-state active-story {story_id} "{story_name}" "In Progress"`
  - Set owner: `update-state active-story {story_id} owner "{owner}"` → updates the Owner column (pass `-` to clear); keeps the table partitioned by person so teammates edit different rows.
  - Mark done: `update-state active-story {story_id} Done` → removes the row from Active Stories. Token is literal `Done` (capital D), distinct from the lowercase `plan.json` `done` enum used by `update-plan`.
  - Set FIS: `update-state active-story {story_id} fis "{fis_path}"` → updates the FIS column
- `blocker`: Add or remove a blocker
  - Add: `update-state blocker "{description}"`
  - Remove: `update-state blocker remove "{description}"` → removes the matching entry
- `decision`: Add a recent decision entry with timestamp

**Local fields** → local `State (local)` document. **File-creation exception**: if the local file does not exist, scaffold it from the `## STATE.local.md` template in `project-state-templates.md` before writing (gitignored, so this does not violate the shared-State "init owns creation" rule). On every local-field write, also ensure `.gitignore` covers it – append the entry idempotently (create `.gitignore` if missing); a tracked local file reintroduces the collision surface.
- `note`: Add a session continuity note with timestamp (to `## Session Continuity Notes`)
- `focus`: Set/replace My Current Focus (to `## My Current Focus`) – your private working scratch; the shared claim is `plan.json` `owner` + `in-progress`

After any update, set the touched document's `Last Updated` to the current timestamp.

**Maintenance rules** (apply on every write): see [state-maintenance-rules.md](references/state-maintenance-rules.md).

State document format (both files): see [`project-state-templates.md`](${CLAUDE_PLUGIN_ROOT}/references/project-state-templates.md).

#### Update Plan Status
Mutate `stories[].status` in `plan.json` per [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md).

**Usage**: `update-plan <plan_path> <story_id> <status> [<story_id> <status> ...]`

Actions:
- Read `plan.json` once; for each `<story_id> <status>` pair locate the entry in `stories[]` whose `id === <story_id>`, validate `<status>` against the closed enum (`pending` / `spec-ready` / `in-progress` / `done` / `skipped` / `blocked`), set the field; write back once per `plan-schema.md` Formatting conventions.
- **Batched pair form** (`update-plan`, `update-plan-fis`): before any write, emit `BLOCKED: expected <story_id> <value> pairs` if post-path arity is odd, an ID position is not `S` + exactly two digits, or a value position matches that ID pattern. Otherwise process pairs independently: invalid, absent, or repeated IDs/values and pointer/path/provenance failures emit story-named `REJECTED:` lines; rejected/no-op pairs do not block siblings. Reserve `BLOCKED:` for unreadable plans, mis-paired arguments, or write failure. A caller may batch a wave.
- Transition authority: see `plan-schema.md` Writability rules.
- Reject an unknown status pair with `REJECTED: story "<story_id>" – invalid status "<value>" – must be one of pending, spec-ready, in-progress, done, skipped, blocked`.
- Reject an unknown `<story_id>` pair with `REJECTED: story "<story_id>" – not found in <plan_path>` for every `update-plan*` operation. Never append a new story object (the andthen:plan skill owns story creation).
- No-op when `status` already equals the target value.

#### Update Plan FIS
Mutate `stories[].fis` in `plan.json`.

**Usage**: `update-plan-fis <plan_path> <story_id> <fis_pointer|null> [<story_id> <fis_pointer|null> ...]`

Actions:
- Read `plan.json` once. Literal `null` clears `fis`; otherwise derive the story's canonical basename per `data-contract.md`, accept only that no-directory value, and require its sibling target to be a regular non-symlink with matching `**Story-ID**:` / `**Plan**:` provenance before setting it. Write once.
- **Batched pair form**: arity guard, per-pair semantics, and reporting are identical to *Update Plan Status* – the arity guard matters most here, since an omitted pointer could otherwise put a story id in the value position. The duplicate check spans the invocation as well as stories on disk – two pairs claiming one pointer reject the second.
- For non-null pointers, if another story already claims it, emit `REJECTED: story "<story_id>" – fis pointer "<fis_pointer>" already used by story <other-id>; the 1:1 story↔FIS invariant must hold`.
- No-op when `fis` already equals `<fis_pointer>`.

#### Update Plan Owner
Mutate `stories[].owner` in `plan.json` – the optional coordination field recording who is executing a story (per [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md)).

**Usage**: `update-plan-owner <plan_path> <story_id> <owner>`

Actions:
- Read `plan.json`, locate the entry in `stories[]` whose `id === <story_id>`, set `owner` to `<owner>` (a name or forge handle), write back per `plan-schema.md` Formatting conventions.
- Clear a claim: pass `-` (or empty) as `<owner>` → set `owner` to `null`.
- Reject (`BLOCKED: invalid owner value`) values containing `|` or newlines, or equal to a FIS-Unset Sentinel form other than `-`/empty (per `data-contract.md`; `-`/empty mean "clear" per the bullet above).
- Displacing a claim: when `owner` is already a *different* non-null value, still set it (advisory, not a lock – see `plan-schema.md`) but emit `WARNING: displaced previous owner "<old>" on <story_id>` so the takeover is visible.
- No-op when `owner` already equals the target value (path/owner-normalized; treat `-`/empty/absent as `null`).
- If the story object lacks an `owner` key (legacy plan), insert it in schema order (after `fis`).

#### Update FIS
Mutate a FIS document – mark checkboxes, append implementation observations, append discovered requirements, or apply a design-change amendment.

**Usage**:
- Mark checkboxes: `update-fis <fis_path> <task_id|all>`
- Append observations: `update-fis <fis_path> observations <markdown-body>`
- Append discovered requirements: `update-fis <fis_path> discovered-requirements <markdown-body>`
- Apply design-change amendment: `update-fis <fis_path> design-change <markdown-body>`
- Record a resolved or deferred decision: `update-fis <fis_path> decision-note <decision_key> <resolved|deferred> <markdown-body>`

Actions for `<task_id|all>` form:
- When `task_id` is a specific ID: Mark that task's checkbox: `- [ ] **{task_id}**` → `- [x] **{task_id}**`
- When `task_id` is `all`: Mark ALL unchecked task checkboxes (`- [ ]` → `- [x]`) plus every proof-surface checkbox set in one pass:
  - **`## Acceptance Scenarios`** – each scenario is one canonical-shape checkbox (shape per [`fis-authoring-guidelines.md`](${CLAUDE_PLUGIN_ROOT}/references/fis-authoring-guidelines.md) *Acceptance Scenarios and Proof-of-Work*). Flip each `- [ ]` to `- [x]`. Example: `- [ ] **S01 [OC01] [TI01,TI03] Happy path**` → `- [x] ...`.
  - **`## Structural Criteria`** – each checkbox flips `- [ ]` to `- [x]`.
  - **`## Final Validation Checklist`** – only when the section exists (it is optional content). When present, each checkbox flips `- [ ]` to `- [x]`.
- Before marking done, verify that evidence of completion exists – the calling skill should have already performed verification; do not re-run it. When all tasks are done (or using `all`), also flip the proof-surface checkbox sets above.

Both `observations` and `discovered-requirements` target `## Implementation Observations`; if that section is absent, append it to the end of the FIS using the standard lead paragraph from the FIS template, then apply the [Append-Run Block Protocol](references/append-run-block-protocol.md).

Actions for `observations` form:
- Body constraint variant: MUST use `####`-or-deeper headings (typically `#### NOTICED BUT NOT TOUCHING` and/or `#### ASSUMPTIONS (AUTO_MODE)`). MUST NOT contain `#### DISCOVERED REQUIREMENTS` – that subsection belongs in the `discovered-requirements` form so tagged-lane separation holds. Reject (no-op + `BLOCKED: invalid observations body`) if violated.
- Tag suffix: `– observations`.

Actions for `discovered-requirements` form:
- Body constraint variant: MUST contain `#### DISCOVERED REQUIREMENTS`. Reject (no-op + `BLOCKED: invalid discovered-requirements body`) if the body lacks `#### DISCOVERED REQUIREMENTS`.
- Tag suffix: `– discovered-requirements`.

Actions for `design-change` form:
- Body constraint variant: MUST contain `#### DESIGN CHANGE`, `#### ADR`, and one or more exact amendment pairs with `Old:` and `New:` fenced blocks. Body headings must be `####`-or-deeper and MUST NOT contain `## ` headings or another `### Run:` line. Reject (no-op + `BLOCKED: invalid design-change body`) if the ADR entry is missing, if an old/new pair is missing, or if the heading constraints are violated.
- Idempotent retry and all-or-nothing: on a retry within the 2-minute window (per the [Append-Run Block Protocol](references/append-run-block-protocol.md)), if the body is identical and every missing `Old:` span's paired `New:` span is already present in the allowed Intent/scenario region, no-op instead of blocking; if the paired `New:` spans are present but the audit block is missing, append the audit block and report the retry repaired the audit trail. Otherwise validate every pair before applying any replacement; reject (no-op + `BLOCKED: invalid design-change body`) if any `Old:` span does not exactly match the current FIS text, and apply none if one pair fails. Treat replacements plus audit append as one logical mutation: if the audit append cannot be written, do not apply replacements.
- Apply each exact old/new replacement to the FIS Intent and/or Acceptance Scenario text only. A scenario-only amendment may change title/Given/When/Then articulation but must leave tags and Proof path/selector/state byte-identical. Do not edit task checkboxes, Structural Criteria, plan provenance, or Implementation Observations through this form.
- Append the same body to `## Implementation Observations` using tag suffix `– design-change` via the [Append-Run Block Protocol](references/append-run-block-protocol.md), so the mutable spec edit is auditable and retry-safe. This form is distinct from `discovered-requirements`; do not use it for missing requirements or edge cases that should stay append-only.

Actions for `decision-note` form (the `andthen:preflight` skill's resolved/deferred-decision write path; atomic, AUTO_MODE-safe, reject-malformed):
- `<resolved|deferred>` is the decision class.
- Validate the canonical body and persisted-block grammar in [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md); reject malformed input with `BLOCKED: invalid decision-note body`.
- **Target by class**:
  - `resolved` → validate every exact pair before changing anything. Each `Old:` span must occur exactly once in the named `Affected surface` above the mutable-section boundary; reject pairs touching the H1 provenance block, completion checkbox state, task/scenario IDs and tags, or Proof identity. Once implementation has begun, pairs touching Acceptance Scenario or Structural Criteria prose belong to the ADR-audited `design-change` form – reject them here. Apply all replacements and append the `#### DECISION NOTE: <decision_key>` block under `## Implementation Observations` as one logical mutation; if either half cannot write, apply neither. A retry with replacements already present repairs only a missing audit block; otherwise a missing `Old:` span rejects the whole call.
  - `deferred` → append a `#### DEFERRED DECISION: <decision_key>` block under a `## Deferred Decisions` section (create the section at the end of the FIS if absent – it and `## Implementation Observations` must stay below all spec content, since the FIS read-only boundary is positional; it collects signed-off punts so a reader finds them in one place).
- Apply the shared same-key/class replacement rule; byte-identical retries are no-ops.
- Do not touch completion state, plan provenance, or design-change audit blocks through this form.

#### Update Decisions
Append a load-bearing non-ADR choice to the project Decisions registry's `## Still Current` section. The `andthen:preflight` skill's project-decision-altitude write path; ADR indexing stays owned by the `andthen:architecture` skill (`--mode trade-off`).

**Usage**: `update-decisions still-current <topic> <decision-and-rationale>`

Resolve the target file path from the **Project Document Index** `Decisions` row (default `docs/DECISIONS.md`). If the file does not exist, refuse with `BLOCKED: Decisions document not found at <path> – run the andthen:init skill to scaffold it`; do not create it.

Actions for `still-current` form:
- Locate `## Still Current` case-insensitively; if absent, create it as a new H2. Remove the `- ...` placeholder bullet if present (exact-string match only).
- Append one bullet in the registry's existing format: `- **<Topic>**: <decision + brief rationale>.` (single bullet; substitute `<Topic>` and the decision/rationale).
- **Idempotency**: `<topic>` is the key – no-op if a bullet with the same `- **<Topic>**:` prefix already exists; update its text in place when the rationale changed.

#### Update Reconciliation Ledger
Deterministic mutator for the Reconciliation Ledger and its only sanctioned write path: atomic, transition-audited, AUTO_MODE-safe, reject-malformed. **Single-document** – it mutates only the ledger; the completion-presentation gate that *reads* the ledger lives in the orchestrating skills (`exec-spec` / `exec-plan`), not here.

The caller passes the **FIS-adjacent ledger path** (`{fis-without-ext}.reconciliation-ledger.md`, resolved per [`reconciliation-ledger.md`](${CLAUDE_PLUGIN_ROOT}/references/reconciliation-ledger.md)) as the first argument; `ops` mutates exactly that file and does not discover a path. There is no project-global ledger.

**Usage**:
- Add an OPEN entry: `update-ledger add <ledger-path> <stable-id> <class> <stale-targets> <source-run> [notes]`
- Close on applied reconciliation: `update-ledger reconcile <ledger-path> <stable-id> [design-change+ADR-evidence]`
- Withdraw with falsifier: `update-ledger withdraw <ledger-path> <stable-id> <falsifier>`
- Bump recurrence (may escalate): `update-ledger bump-recurrence <ledger-path> <stable-id>`
- Record close-gate override: `update-ledger override-close <ledger-path> <stable-id> <reason>`

Common rules:
- Reuse the existing class vocabulary only (`code-defect | spec-stale | design-changed | ambiguous-intent`); reject any other class. Status values are `OPEN | RECONCILE REQUIRED | CLOSED | WITHDRAWN`.
- Stable-ID format/derivation/matching, entry schema (surgical single-line edits), status lifecycle, recurrence/escalation, atomicity, and AUTO_MODE-safe reject-malformed behavior are owned by `reconciliation-ledger.md`.
- Resolve dates via `date -u +"%Y-%m-%d"`; set `Updated:` on every mutation.

Actions for `add` form:
- **File-creation exception** (see GOTCHAS): if the passed ledger file does not exist, scaffold it from the canonical ledger template in `reconciliation-ledger.md` before appending.
- Append a new entry with `Status: OPEN`, the given `Class:`, `Stale targets:`, `Source run:`, `Recurrence: 1`, `Falsifier: –`, `Override reason: –`, and `Created:`/`Updated:` set to today.
- **Idempotent**: no-op only if a non-terminal (OPEN / RECONCILE REQUIRED) entry already matches the full stable ID. If another non-terminal entry shares `{relative-path}:{class}` but has a different slug, append the new entry.
- **Terminal-match re-open**: when the stable ID matches a terminal (`CLOSED`/`WITHDRAWN`) entry, re-open it in place rather than appending – mechanics owned by `reconciliation-ledger.md` *Status lifecycle and transitions / add*. Requires refuting evidence in the call (the `[notes]` argument); reject (no-op + `BLOCKED: re-open requires refuting evidence`) when none is supplied.
- Reject (no-op + `BLOCKED: invalid ledger class "<value>"`) on an out-of-vocabulary class.

Actions for `reconcile` form:
- Require an existing matching entry in `OPEN` or `RECONCILE REQUIRED`. For `RECONCILE REQUIRED`, require non-empty evidence that the sanctioned `update-fis design-change` amendment and ADR path completed; reject a bare `update-ledger reconcile <ledger-path> <stable-id>` with `BLOCKED: reconcile requires design-change + ADR evidence for RECONCILE REQUIRED`. Transition valid entries to `CLOSED`; set `Updated:`.
- Reject (no-op + `BLOCKED: no matching ledger entry for <stable-id>`) when no entry matches; reject when the entry is already terminal (`CLOSED`/`WITHDRAWN`).

Actions for `withdraw` form:
- Require an existing matching non-terminal entry and a non-empty `<falsifier>`. Transition to `WITHDRAWN`; record `Falsifier:`; set `Updated:`.
- Reject (no-op + `BLOCKED: withdraw requires a falsifier`) when the falsifier is empty; reject when no entry matches.

Actions for `bump-recurrence` form (escalation rules owned by `reconciliation-ledger.md` *Recurrence and escalation rules*):
- Require an existing matching `OPEN` entry. For `spec-stale`/`design-changed`: increment `Recurrence:`; at `2`, transition to `RECONCILE REQUIRED`. Set `Updated:`.
- **No-op** for `code-defect`/`ambiguous-intent` entries (these classes do not escalate) – report the no-op, do not error.
- Reject (no-op + `BLOCKED: no matching ledger entry for <stable-id>`) when no entry matches.

Actions for `override-close` form:
- Require an existing matching `OPEN`/`RECONCILE REQUIRED` entry and a non-empty `<reason>`. Record the `Override reason:` against that entry; set `Updated:`. The entry keeps its status (the override unblocks the completion-presentation gate; it does not close the entry).
- Reject (no-op + `BLOCKED: override-close requires a reason`) when the reason is empty; reject when no entry matches.

#### Update Tech Debt
Append tech-debt entries (typically deferred review findings) to the project's Tech Debt Backlog.

**Usage**: `update-tech-debt append <markdown-body>`

Resolve the target file path from the **Project Document Index** `Tech Debt` row (default `docs/TECH-DEBT-BACKLOG.md`).

Actions for `append` form:
- Body constraint variant: MUST use `####`-or-deeper headings (typically `#### DEFERRED FINDINGS`). Reject (no-op + `BLOCKED: invalid tech-debt body`) if violated.
- **File-creation exception** (see GOTCHAS): if the resolved target file does not exist, scaffold it from the `# Technical Debt Backlog` template in `project-state-templates.md` before appending.
- **Severity routing**: each entry is a top-level `- **{title}** ...` bullet with its `Severity:` line nested as a sub-bullet. Parse the `Severity:` value and route the entry to the matching H2 section (`High` / `Medium` / `Low`). Default to `Medium` when missing or unrecognized. When a single body batches mixed severities, split into per-severity run blocks sharing one timestamp – one new run block under each affected severity H2.
- Tag suffix: `– tech-debt`. Idempotency lane scoped per severity H2.
- Apply the [Append-Run Block Protocol](references/append-run-block-protocol.md) (once per affected severity section).

#### Update Learnings
Maintain defensive-knowledge entries in the project's Learnings index. **Not a run-block append** – LEARNINGS is a topic-organized knowledge base, not a chronological log (template: `project-state-templates.md` `## LEARNINGS.md`).

**Usage**:
- Topic entry: `update-learnings add <topic> <entry-markdown>`
- Entry removal: `update-learnings remove <topic> <title>`
- Error-pattern row: `update-learnings error <error> <type> [conclusion]`

Resolve the index file path from the **Project Document Index** `Learnings` row (default `docs/LEARNINGS.md`); topic shards live in a `learnings/` directory beside it. If the index does not exist, refuse with `BLOCKED: Learnings document not found at <path> – run the andthen:init skill to scaffold it`; do not create it – shard files are the sanctioned creation exception (see GOTCHAS).

**Pointer grammar and shard identity** – a shard's first line is `# {Topic}`, and that H1, never the filename, is shard↔topic identity; the slug only names the file (topic lowercased, non-alphanumeric runs → `-`, edge hyphens trimmed, plus a `-2`/`-3` suffix when the slug's existing shard names a different topic). The canonical pointer is `→ learnings/<topic-slug>.md – {hook}`, written exactly as the template shows; on any pointer write the hook defaults to the topic's first bullet's `{title}` (from the shard when sharded), else the topic name. A topic is **sharded** when a `→` pointer whose path ends in `learnings/<slug>.md` appears anywhere under its H2 and the pointed file's H1 matches the topic (case-insensitive); a pointer to a missing file still counts (the next mutating write creates it), while a pointer whose H1 names a different topic is inert – treat the topic as inline, surface the mismatch, never merge. Tolerate backticks or extra formatting around the path when detecting; normalization rewrites formatting only – the path is preserved verbatim (a suffixed shard keeps its suffixed path). **Shard-wins invariant**: any *mutating* write touching a topic first merges leftover inline content – or an unpointed shard whose H1 matches – into the shard, idempotent on the `- **{title}**` prefix, leaving only the pointer; a call resolving to `NO-OP`/`BLOCKED` mutates nothing, normalization included.

Actions for `add` form:
- `<entry-markdown>`: a single bullet. MUST start with `- **{title}**` and be under 200 characters. Reject with `BLOCKED: invalid learnings entry – must start with "- **{title}**" and stay under 200 chars` if violated.
- Locate `## {topic}` case-insensitively in the index. Sharded topic: append the bullet to the shard, creating it if missing. Inline topic: append under the H2. Absent: create as a new H2 above `## Error Patterns` (or at EOF).
- **Idempotency**: no-op if a bullet matching the `- **{title}**` prefix already exists in the topic (index or shard).

Actions for `remove` form (graduation-ladder delete step: entries superseded by an enforced check, or stale):
- Delete the bullet matching the `- **{title}**` prefix from the topic (index or shard); `NO-OP: entry not found` when absent – a NO-OP mutates nothing else.
- After a successful deletion, if nothing remains beyond the H2 (and pointer) in the index and, when sharded, beyond the shard's H1, remove the H2 (never `## Error Patterns`) and delete the emptied shard together with its pointer. Remaining non-bullet content keeps section and shard in place; when a surviving shard's pointer hook matches the deleted title, refresh the hook (per the grammar default).

Actions for `error` form:
- `<type>`: `Deterministic` / `Infrastructure`. Default `Deterministic`.
- `[conclusion]`: optional; omit or pass `-` for empty.
- Append `| {error} | {type} | {conclusion} |` to the `## Error Patterns` table; if the section or table is missing, recreate it (`## Error Patterns` + header `| Error | Type | Conclusion |` + separator) first.
- **Idempotency**: if a row with identical `{error}` exists, update its other columns; do not duplicate.
- Row promotion (row → topic section) is judgment-driven; rows stay until a human promotes them.

**Ceiling** (checked after every `update-learnings` write, any form): while the index exceeds 150 lines and inline topics remain, graduate the largest inline topic – most lines under its H2, tie → first in file, never `## Error Patterns` – by moving its entire section body verbatim into its shard, created if missing, else merged idempotently on the `- **{title}**` prefix keeping non-bullet content, leaving under the H2 only the canonical pointer. Graduation is atomic: if either the shard write or the index rewrite cannot apply, apply neither. A graduation performed when no sharded topic pre-exists in the index also replaces a header comment differing from the current template's – inserting it when absent – so legacy files gain the read contract their shards now depend on; later graduations leave the header alone. When the index still exceeds 150 lines with no inline topic left, report `NOTICE: Learnings index over ceiling – promote Error Patterns rows or remove stale entries`.

### 2. Git Operations

**Usage**:
- `commit <type> <scope> <description>` – format: see [git-and-progress-formats.md](references/git-and-progress-formats.md).
- `branch <type> <story-id> <slug>` – format: see [git-and-progress-formats.md](references/git-and-progress-formats.md).
- `changelog <version> <entries...>` – format: see [git-and-progress-formats.md](references/git-and-progress-formats.md).


### 3. Progress Tracking

**Usage**:
- `progress <plan_path>` – format/logic: see [git-and-progress-formats.md](references/git-and-progress-formats.md).
- `stale <plan_path>` – format/logic: see [git-and-progress-formats.md](references/git-and-progress-formats.md).
