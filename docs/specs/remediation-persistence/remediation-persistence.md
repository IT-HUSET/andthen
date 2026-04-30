# Remediation Persistence

## Feature Overview and Goal

Persist remediation outcomes from `andthen:remediate-findings` so deferred findings flow into the project Tech Debt Backlog and the input review report carries a Remediation Status section reflecting per-finding outcomes (`RESOLVED` / `PARTIALLY RESOLVED` / `UNRESOLVED` / `DEFERRED`). Closes two persistence gaps where Phase 4's findings re-check classification only reaches the conversational completion report.


## Success Criteria (Must Be TRUE)

> Each criterion must have a defined proof path — at least one Scenario (for behavioral criteria) or a task Verify line (for structural criteria).

- [x] Running `andthen:ops update-tech-debt append <markdown-body>` appends a tagged `### Run: {YYYY-MM-DD HH:MM UTC} — tech-debt` block under the appropriate severity heading in the project's Tech Debt Backlog (resolved from the **Project Document Index** `Tech Debt` row, default `docs/TECH-DEBT-BACKLOG.md`)
- [x] When the Tech Debt Backlog file does not exist, the new ops form creates it from the template defined in `plugin/references/project-state-templates.md`. This is the **one** ops form that creates a missing target file, and the exception is explicit in `ops/SKILL.md`
- [x] Within a 2-minute retry window, identical `update-tech-debt append` invocations are no-ops (mirror `update-fis observations` idempotency)
- [x] After `andthen:remediate-findings` Phase 4 classifies findings, any `DEFERRED` entries are batched into a single `update-tech-debt append` invocation carrying severity, finding title/location, deferral justification, and a back-link to the source review report path
- [x] When `REPORT_SOURCE` is a local writable file, `andthen:remediate-findings` Phase 5 writes (or replaces) a `## Remediation Status` section at the end of the report listing each original finding with one of `RESOLVED` / `PARTIALLY RESOLVED` / `UNRESOLVED` / `DEFERRED` plus one-line evidence/justification
- [x] When `REPORT_SOURCE` is a raw URL or any non-writable input, the report annotation step is skipped and the skip is logged in the completion report
- [x] Re-running `andthen:remediate-findings` on the same report does not duplicate the `## Remediation Status` section — the existing section is replaced in place
- [x] A run where every finding is `RESOLVED` produces no `update-tech-debt append` write (no-op on empty body)
- [x] All new behaviors propagate `--auto` correctly and never wait on user input in `AUTO_MODE`

### Health Metrics (Must NOT Regress)

- [x] Existing `update-fis observations` and `update-fis discovered-requirements` behavior unchanged
- [x] Phase 4 findings re-check vocabulary (`RESOLVED` / `PARTIALLY RESOLVED` / `UNRESOLVED` / `DEFERRED`) unchanged
- [x] `scripts/install-skills.sh` still inlines references correctly across all install tiers
- [x] No new `${CLAUDE_PLUGIN_ROOT}` token usage outside the strict braces form


## Scenarios

### Deferred finding lands in Tech Debt Backlog

- **Given** a review report with one Medium finding the operator accepts as `DEFERRED` with justification "needs separate refactor pass"
- **When** `andthen:remediate-findings` completes Phase 4 with that finding classified `DEFERRED`
- **Then** `docs/TECH-DEBT-BACKLOG.md` (resolved from the **Project Document Index**) gains a new `### Run: {timestamp} — tech-debt` block under `## Medium` containing the finding title, location, justification, and a back-link to the source report path

### Tech Debt Backlog file created when missing

- **Given** the project has no `docs/TECH-DEBT-BACKLOG.md` yet
- **When** the new `update-tech-debt append` form is invoked with a non-empty body
- **Then** the file is created from the template in `project-state-templates.md` with H1 `# Technical Debt Backlog`, H2 sections `## High` / `## Medium` / `## Low` each carrying the placeholder line, and the new run block is appended in the correct severity section

### Idempotent retry on tech-debt append

- **Given** a tech-debt run block was just appended at timestamp T with body B
- **When** `update-tech-debt append B` is invoked again within 2 minutes (e.g. an `andthen:exec-spec` Step 5b.4 retry-once protocol)
- **Then** the form no-ops, no duplicate run block is written, and the existing block remains the most recent

### All-RESOLVED run skips tech debt write

- **Given** a review report whose findings are all classified `RESOLVED` in Phase 4
- **When** `andthen:remediate-findings` reaches Phase 5
- **Then** no `update-tech-debt append` invocation is made (empty-body no-op) and the completion report names zero deferred items

### Local report gains Remediation Status section

- **Given** `REPORT_SOURCE` is `docs/specs/foo/foo-code-review-claude-2026-04-30.md` (local, writable) with three findings classified `RESOLVED`, `RESOLVED`, `DEFERRED`
- **When** Phase 5 annotates the report
- **Then** the file gains a `## Remediation Status` section at the end listing each finding with status and one-line evidence/justification, in the same order as the original findings

### Re-run replaces (not duplicates) Remediation Status

- **Given** a review report already carrying a `## Remediation Status` section from a prior remediation run
- **When** `andthen:remediate-findings` runs again on the same report (e.g. after additional fixes resolve a previously `UNRESOLVED` item)
- **Then** the existing section is replaced in place; the file contains exactly one `## Remediation Status` H2

### Remote URL report skips annotation cleanly

- **Given** `REPORT_SOURCE` is a raw URL (`https://...`) and the body was fetched into memory
- **When** Phase 5 reaches the annotation step
- **Then** annotation is skipped, the completion report logs the skip with reason "remote URL — no local file to annotate", and the tech-debt persistence step still runs as normal


## Scope & Boundaries

### In Scope

- New `andthen:ops` form: `update-tech-debt append <markdown-body>` — append-only, tagged `### Run: ... — tech-debt`, idempotent within 2 minutes, target-file creation from template when missing
- Two new Phase 5 steps in `andthen:remediate-findings`: tech-debt persistence (DEFERRED batching) and report annotation (Remediation Status section)
- Template definition for `TECH-DEBT-BACKLOG.md` in `plugin/references/project-state-templates.md`
- Update to the `## COMPLETION` contract in `remediate-findings/SKILL.md` so the conversational summary names the new persistence outcomes

### What We're NOT Doing

- **Retroactive backfill of historical deferred findings** — only new runs write to the backlog; older deferred items are left to the operator
- **Inline annotation of individual findings within the report body** — too fragile against the unstructured shapes of `## CRITICAL ISSUES` / `## HIGH PRIORITY` / `## Gap Analysis Results` etc.; a single replace-in-place `## Remediation Status` section is the contract instead
- **A separate `update-review-report` ops form** — annotation logic is a single-purpose whole-section replace, simpler to keep inside `remediate-findings` than to bounce through ops
- **Changes to the Phase 4 findings re-check vocabulary or classification logic** — `DEFERRED` already exists; this FIS only consumes the existing classification
- **Auto-creation of TECH-DEBT-BACKLOG.md outside the new ops form** — no other skill (including `init`) is changed to scaffold the file; creation is on-demand via the first `update-tech-debt append`

### Agent Decision Authority

- **Autonomous**: severity-bucket routing inside the tech-debt body (parse the body's per-entry `Severity:` line; default `Medium` when ambiguous), one-line phrasing of evidence/justification in the Remediation Status section, ordering of the new Phase 5 steps relative to existing FIS/plan/state updates
- **Escalate**: any change to the existing `update-fis observations` / `update-fis discovered-requirements` contracts (those are stable; do not modify), and any introduction of a second ops form for the report annotation


## Architecture Decision

**We will**: extend `andthen:ops` with one new append form (`update-tech-debt`) that mirrors the proven `update-fis observations` protocol verbatim, and add two persistence steps to `andthen:remediate-findings` Phase 5 — over alternatives (a separate `andthen:tech-debt` skill, inline finding-level annotation tags, a bidirectional `update-review-report` ops form) — because reusing the proven append protocol minimises new contract surface and a structural single-section replace is naturally idempotent without per-finding identity tracking.


## Technical Overview

### Integration Points

- `andthen:ops update-tech-debt append` resolves the target file path from the **Project Document Index** `Tech Debt` row (default `docs/TECH-DEBT-BACKLOG.md`) — same resolution pattern used by State / FIS / Plan ops.
- `andthen:remediate-findings` Phase 5 invokes the new ops form via the Skill tool (or `/andthen:ops` slash form) — never hand-edits the tech debt backlog. Ops itself is deterministic and exempt from `--auto` propagation per `automation-mode.md`.
- The `## Remediation Status` section is written inline to the report file via Edit/Write — no ops form needed because the operation is simpler than an append (whole-section replace, single-skill scope).

### Data Models

**Tech Debt Backlog template** (added to `project-state-templates.md`):

- H1 `# Technical Debt Backlog`
- H2 sections per severity in fixed order: `## High`, `## Medium`, `## Low`
- Each section has placeholder line `_No tech debt recorded yet._` until first write (mirrors FIS Implementation Observations placeholder pattern at `plugin/references/fis-template.md:212`)
- New entries appended as `### Run: {YYYY-MM-DD HH:MM UTC} — tech-debt` blocks under the matching severity H2

**Tech-debt run-block body shape** (set by `remediate-findings`, consumed verbatim by ops):

```
#### DEFERRED FINDINGS

- **{Finding title}** (`{location}`)
  - Severity: {High|Medium|Low}
  - Justification: {one-line reason for deferral}
  - Source report: `{relative path to original report}`
```

The ops form parses each entry's `Severity:` line to route the entry to the matching H2 section. When a single body batches mixed severities, ops splits and writes one run block per severity bucket, all sharing the same timestamp. Producers (e.g. `andthen:remediate-findings` Phase 5) MUST normalize upstream review severities into the `{High|Medium|Low}` bucket set before populating `Severity:` — map `CRITICAL → High`, `HIGH → High`, `MEDIUM → Medium`, `LOW → Low` (case-insensitive) — so the ops `default-to-Medium` fallback for unrecognized values is a defensive backstop, not the primary path. For findings with a missing severity field or a non-canonical value (`P0`, `Blocker`, etc.), the producer surfaces the raw input in the completion report and routes to `Medium` — keeping the demotion logged rather than silent.

**`## Remediation Status` section in the review report**:

- Always last section in the file (after any existing trailing sections)
- Entries listed in the original report's finding order, one bullet per finding:
  - `- **{finding title or short quote}** — {STATUS} — {one-line evidence or justification}`
- On re-run: locate the LAST line that starts at column 0 with `## Remediation Status` and is not inside a fenced code block; replace from that line to EOF with the regenerated section


## Code Patterns & External References

```
# type | path/url | why needed
file   | plugin/skills/ops/SKILL.md:140-155              | Append protocol to mirror — `update-fis observations` form: tagged `### Run:` headers, body constraints, 2-minute idempotent retry, append-only
file   | plugin/skills/ops/SKILL.md:157-172              | Sibling `update-fis discovered-requirements` form — second example of the same pattern with a different tag
file   | plugin/skills/ops/SKILL.md:24-29                | GOTCHAS list — site for the explicit "ops never creates" exception note for the new form
file   | plugin/skills/remediate-findings/SKILL.md:99    | Phase 4 step 5 findings re-check vocabulary — classification source for the new persistence steps
file   | plugin/skills/remediate-findings/SKILL.md:106-124 | Phase 5 (Update Workflow State) — insertion point for the two new steps
file   | plugin/skills/remediate-findings/SKILL.md:127-134 | COMPLETION section — must enumerate the new persistence outcomes
file   | plugin/skills/init/templates/CLAUDE.template.md:49 | Project Document Index `Tech Debt` row registration — default path source
file   | plugin/references/project-state-templates.md:55-79 | Existing template patterns (Product Backlog, Roadmap) — match heading style for new TECH-DEBT-BACKLOG template
file   | plugin/references/fis-template.md:199-212       | Implementation Observations placeholder pattern — reuse `_No ... recorded yet._` convention for parity
```


## Constraints & Gotchas

- **Constraint**: ops resolves **Project Document Index** entries; never hard-code `docs/TECH-DEBT-BACKLOG.md` in `remediate-findings`. Workaround: pass through whatever path ops resolved.
- **Avoid**: introducing a separate idempotency mechanism. **Instead**: reuse the exact 2-minute window + body-whitespace-normalized comparison from `update-fis observations` (lines 140-155 of `ops/SKILL.md`).
- **Avoid**: inline-tagging individual findings inside the report body. **Instead**: a single `## Remediation Status` section that fully replaces on re-run.
- **Critical**: ops normally never creates target files (it must report "no state file" rather than create State — see `ops/SKILL.md:27`). The tech-debt form is the *one* documented exception. The exception MUST be explicit in `ops/SKILL.md` and called out as a deviation, not silently introduced.
- **Critical**: when both new Phase 5 steps run in the same `remediate-findings` invocation, run report annotation (TI04) BEFORE tech-debt persistence (TI03 wiring). If annotation fails, still write tech debt and surface the annotation failure in the completion report — losing the tech-debt write because annotation failed would create silent debt drift.


## Implementation Plan

### Implementation Tasks

- [x] **TI01** Tech Debt Backlog template defined in `project-state-templates.md`
  - Add a new template section after the existing `# Roadmap` template at `plugin/references/project-state-templates.md:55-108`. H1 `# Technical Debt Backlog`, H2 in fixed order `## High` → `## Medium` → `## Low`, each section carrying placeholder line `_No tech debt recorded yet._`. Match the heading style used by Product Backlog and Roadmap templates.
  - **Verify**: `rg "^# Technical Debt Backlog" plugin/references/project-state-templates.md` returns one match AND the template section contains all three severity H2s in order AND `rg "_No tech debt recorded yet\._" plugin/references/project-state-templates.md` returns three matches

- [x] **TI02** `andthen:ops update-tech-debt append` form documented in `ops/SKILL.md`
  - Add a new `#### Update Tech Debt` subsection under `### 1. State File Operations`, after the existing `#### Update FIS` block (around `plugin/skills/ops/SKILL.md:126`). Mirror the structure of `update-fis observations` (lines 140-155) verbatim with adapted wording: body constraints (`####`-or-deeper headings only; no `## ` headings; no other `### Run:` lines), tagged `### Run: {YYYY-MM-DD HH:MM UTC} — tech-debt` block, 2-minute idempotent retry against tag-matched blocks only, append-only. Severity routing: parse each `- **{title}** ...` entry's `Severity: ` line and write to the matching H2; when one body contains mixed severities, split into per-severity run blocks sharing one timestamp. Add an explicit exception clause to the GOTCHAS list (`ops/SKILL.md:27`) calling out that `update-tech-debt append` IS allowed to create the target file from the `project-state-templates.md` template when missing — and only that file. Update the `argument-hint` in frontmatter to add `update-tech-debt append`.
  - **Verify**: `rg "update-tech-debt append" plugin/skills/ops/SKILL.md` returns matches (including the frontmatter hint) AND the new subsection names `### Run: {YYYY-MM-DD HH:MM UTC} — tech-debt` verbatim, the 2-minute idempotent-retry clause, the body-constraint clause matching `####`-or-deeper headings, AND the gotcha-exception note about file creation

- [x] **TI03** `andthen:remediate-findings` Phase 5 persists DEFERRED findings via the new ops form
  - In `plugin/skills/remediate-findings/SKILL.md` Phase 5 (around lines 106-124), add a step after the existing FIS/plan/state updates that batches all `DEFERRED` entries from the Phase 4 re-check into a single `update-tech-debt append` invocation. Body MUST follow the format documented in this FIS (Technical Overview › Data Models › *Tech-debt run-block body shape*). Skip the step entirely when there are zero `DEFERRED` entries (no-op proven by Scenario *All-RESOLVED run skips tech debt write*). Document the back-link from each entry to the source report path. Note explicitly that ops is deterministic and `--auto` is not propagated to it (per `automation-mode.md`).
  - **Verify**: `rg "update-tech-debt append" plugin/skills/remediate-findings/SKILL.md` returns at least one match in Phase 5; the prompt names "DEFERRED" and a no-op-when-zero clause; the back-link-to-source-report requirement is named verbatim

- [x] **TI04** `andthen:remediate-findings` Phase 5 writes/updates `## Remediation Status` in the input report
  - Add a Phase 5 step (run BEFORE the TI03 tech-debt step per the Constraints & Gotchas ordering rule) that, when `REPORT_SOURCE` from Phase 1 was a local writable path (not a raw URL, not any other shape), writes a `## Remediation Status` section at the end of the report. Whole-section replace if the heading already exists (locate the LAST line that starts at column 0 with `## Remediation Status` and is not inside a fenced code block; overwrite from that line to EOF); append-with-leading-blank-line otherwise. Each entry: `- **{finding title or short quote}** — {STATUS} — {one-line evidence or justification}`, in original report finding order. Skip with logged reason `"remote URL — no local file to annotate"` (or equivalent for non-writable inputs) when the input is not a local writable path. If annotation fails for any reason, continue to TI03 and surface the annotation failure in the completion report.
  - **Verify**: `rg "## Remediation Status" plugin/skills/remediate-findings/SKILL.md` returns matches in Phase 5; the prompt names whole-section replace, the URL-skip condition with the specific logged reason, the ordering "before tech-debt", and the failure-doesn't-block-tech-debt rule

- [x] **TI05** COMPLETION contract enumerates the new persistence outcomes
  - Update the `## COMPLETION` section in `remediate-findings/SKILL.md` (lines 127-134). Add bullets so the conversational completion report explicitly enumerates: tech-debt entries written (count + path + per-severity breakdown), report annotation status (`written` / `replaced` / `skipped: <reason>`). Keeps the completion report informative for `AUTO_MODE` consumers parsing the output.
  - **Verify**: `rg "tech-debt entries|Remediation Status" plugin/skills/remediate-findings/SKILL.md` returns matches inside the COMPLETION section AND the section names both new outcomes

### Testing Strategy

This FIS modifies skill prompts (markdown), not executable code. Verification proceeds in two passes:

**1. Structural proof** (the Verify lines above) — `rg`-based checks that each prompt change names its required clauses verbatim. Quick to run; catches structural drift.

**2. Behavioral proof** (manual end-to-end after structural pass) — drive `andthen:remediate-findings` against test review-report fixtures exercising at least these scenarios:

- [TI02,TI03] Scenario *Deferred finding lands in Tech Debt Backlog* → assert `docs/TECH-DEBT-BACKLOG.md` gains a `### Run: ... — tech-debt` block under `## Medium` with the deferred finding's title, location, justification, and back-link
- [TI02] Scenario *Tech Debt Backlog file created when missing* → start with the file absent; assert post-run the file exists with full template structure
- [TI02] Scenario *Idempotent retry on tech-debt append* → invoke `update-tech-debt append` twice within 2 minutes with identical body; assert exactly one new run block
- [TI03] Scenario *All-RESOLVED run skips tech debt write* → fixture with all `RESOLVED`; assert no new tech-debt block written
- [TI04] Scenario *Local report gains Remediation Status section* → assert section exists at file end with one entry per finding in original order
- [TI04] Scenario *Re-run replaces (not duplicates) Remediation Status* → assert exactly one `## Remediation Status` H2 in the file after second run
- [TI04] Scenario *Remote URL report skips annotation cleanly* → fixture with raw-URL input; assert annotation skipped + logged reason in completion report

### Validation

- Run `scripts/install-skills.sh` after edits to confirm references inline cleanly across all install tiers (`project-state-templates.md` consumer list is unchanged, so this is a sanity check rather than a contract change).

### Execution Contract

- Implement tasks in listed order. Each **Verify** line must pass before proceeding to the next task.
- Prescriptive details (`### Run: {YYYY-MM-DD HH:MM UTC} — tech-debt` tag, `_No tech debt recorded yet._` placeholder, 2-minute retry window, four-state status vocabulary `RESOLVED`/`PARTIALLY RESOLVED`/`UNRESOLVED`/`DEFERRED`, severity headings `## High`/`## Medium`/`## Low`) are exact — implement verbatim.
- Proactively use sub-agents for non-coding needs: documentation lookup, architectural advice — spawn in background when possible.
- After all tasks: run `scripts/install-skills.sh`; `rg "TODO|FIXME|placeholder|not.implemented" plugin/skills/ops/SKILL.md plugin/skills/remediate-findings/SKILL.md plugin/references/project-state-templates.md` should be clean of new TODOs.
- Mark task checkboxes immediately upon completion — do not batch.


## Final Validation Checklist

- [x] **All success criteria** met
- [x] **All tasks** fully completed, verified, and checkboxes checked
- [x] **No regressions** in `update-fis observations` / `update-fis discovered-requirements`
- [x] `scripts/install-skills.sh` runs cleanly post-edit


## Implementation Observations

> _Managed by exec-spec post-implementation — append-only. Each `update-fis observations` or `update-fis discovered-requirements` invocation appends a dated `### Run: {timestamp} — {op-tag}` block (multiple writes per run are normal). Recognized inner subsections: `#### NOTICED BUT NOT TOUCHING` / `#### ASSUMPTIONS (AUTO_MODE)` under the `observations` tag, `#### DISCOVERED REQUIREMENTS` under the `discovered-requirements` tag. Untagged blocks from older FISes remain valid for reading; idempotency-dedup matches by tag and never dedupes against them. Available as a backlog for follow-up review/refactor work. Spec authors: leave this section empty._

Discovered Requirements entries use this shape:

- **Title**: short imperative phrase
- **Description**: 1-2 sentences on the discovered requirement
- **Rationale**: why it was missed in original spec
- **Interpretation** (AUTO_MODE only): the conservative interpretation chosen and why
- **Traced from**: task ID where the discovery occurred
- **Date**: YYYY-MM-DD

### Run: 2026-04-30 07:18 UTC — discovered-requirements

#### DISCOVERED REQUIREMENTS

- **Title**: Normalize upstream review severity into the {High|Medium|Low} bucket set before sending to ops
- **Description**: `remediate-findings` Phase 5 must map review-tier severities (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) to the tech-debt-tier severity bucket set (`High`, `Medium`, `Low`) before populating the `Severity:` line in the body passed to `update-tech-debt append`. Non-canonical or missing severity values are logged in the completion report and routed to `Medium` so the demotion is visible rather than silent.
- **Rationale**: Without this normalization, the consumer's `default-to-Medium` fallback for unrecognized severities would silently demote a `CRITICAL` deferred finding to `Medium` tech debt. The FIS prescribed the `{High|Medium|Low}` bucket set as the contract surface but did not specify the upstream→bucket map; the executor recognized this as a missing requirement during TI03 and chose the conservative explicit-mapping interpretation. With the map in place, the `default-to-Medium` ops fallback becomes a defensive backstop rather than the primary path for upper-case `CRITICAL` / `HIGH` values.
- **Interpretation** (AUTO_MODE only): Mapping is `CRITICAL → High`, `HIGH → High`, `MEDIUM → Medium`, `LOW → Low` (case-insensitive). Unrecognized or missing values default to `Medium` and are surfaced verbatim in the completion report.
- **Traced from**: TI03
- **Date**: 2026-04-30

