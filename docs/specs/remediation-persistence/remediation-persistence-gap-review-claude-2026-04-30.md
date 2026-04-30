# Gap Review: Remediation Persistence

- **Review target**: `docs/specs/remediation-persistence/remediation-persistence.md`
- **Review mode used**: gap
- **Reviewer**: claude — 2026-04-30

## Executive Summary

The FIS specifies one new ops form (`update-tech-debt append`) and two Phase 5 steps in `andthen:remediate-findings` (annotation + tech-debt persistence). All five Implementation Tasks (TI01–TI05) are checked, every Verify-line `rg` check passes, and `scripts/install-skills.sh` runs cleanly. The cross-skill body-shape contract, ordering rule (annotation before tech-debt), and idempotency clauses are present verbatim where the spec required them.

One real wiring defect surfaced via behavioral dry-run: the producer/consumer **severity vocabulary mismatch** silently demotes a `CRITICAL` deferred finding to `Medium` tech debt. Two MEDIUM-severity prose-precision gaps and two LOW-severity polish items round out the findings. None block the FIS, but the HIGH finding should be addressed before the contract is considered canonical.

### Verdict

| Dimension     | Score | Threshold | Status |
|---------------|-------|-----------|--------|
| Functionality | 8/10  | >= 7      | PASS |
| Completeness  | 9/10  | >= 9      | PASS |
| Wiring        | 8/10  | >= 8      | PASS |

**Overall: PASS**

Findings Filter stats: full filter applied (6 findings > 5 threshold). 1 VALIDATED at HIGH, 1 VALIDATED at MEDIUM, 1 DOWNGRADED HIGH→LOW (count semantics), 1 VALIDATED at LOW (bare prose mention), 2 WITHDRAWN (parent-dir creation, data-lineage implicitness).

## Requirements Analysis

Baseline: 9 Success Criteria + 4 Health Metrics + 7 Scenarios + 5 Implementation Tasks (TI01–TI05). The contract surface spans three files:

1. `plugin/references/project-state-templates.md` — new `# Technical Debt Backlog` template (TI01)
2. `plugin/skills/ops/SKILL.md` — new `update-tech-debt append` form, frontmatter `argument-hint`, GOTCHAS exception clause (TI02)
3. `plugin/skills/remediate-findings/SKILL.md` — Phase 5 annotation step (TI04, runs first), Phase 5 tech-debt persistence step (TI03), COMPLETION enumeration (TI05)

Critical ordering rule: annotation before tech-debt; annotation failure must not block tech-debt write. Body-shape contract: producer populates a fixed-format markdown body, consumer parses `Severity:` to route per H2.

## Implementation Overview

| File | TI | Status | Evidence |
|------|----|--------|----------|
| `plugin/references/project-state-templates.md:112-133` | TI01 | Present | H1 + 3× H2 in fixed order + 3× placeholder line |
| `plugin/skills/ops/SKILL.md:6` | TI02 | Present | `argument-hint` lists `update-tech-debt append` |
| `plugin/skills/ops/SKILL.md:29` | TI02 | Present | GOTCHAS exception clause names the *one* deviation |
| `plugin/skills/ops/SKILL.md:175-198` | TI02 | Present | Form documented; tagged Run header, 2-minute idempotent retry per severity, body constraints, scaffolding from template, severity routing |
| `plugin/skills/remediate-findings/SKILL.md:124-131` | TI04 | Present | Annotation step before tech-debt step; whole-section replace; URL-skip with logged reason; failure-doesn't-block-tech-debt |
| `plugin/skills/remediate-findings/SKILL.md:133-146` | TI03 | Present | DEFERRED batching; no-op-when-zero; back-link required; ops `--auto` exemption noted |
| `plugin/skills/remediate-findings/SKILL.md:158-159` | TI05 | Present | COMPLETION enumerates `Tech-debt entries written` + `Report annotation status` |

## Quality Review Findings

- `scripts/install-skills.sh` ran cleanly: 21 skills, 3 Codex agents installed.
- Stub scan over the three changed files: clean for FIS scope. The `TODO` matches in `project-state-templates.md` are pre-existing in the unrelated `KEY_DEVELOPMENT_COMMANDS.md` template.
- Strict-braces token check (`$CLAUDE_PLUGIN_ROOT` outside `${...}`): zero violations across the three files.
- Wiring check (installed bundle): `~/.agents/skills/andthen-ops/SKILL.md` carries the new form and exception clause; `~/.agents/skills/andthen-remediate-findings/SKILL.md` carries TI03/TI04 with link tokens correctly rewritten to `references/automation-mode.md`.
- Project Document Index: `Tech Debt` row at `plugin/skills/init/templates/CLAUDE.template.md:49` confirms the default `docs/TECH-DEBT-BACKLOG.md`. The project's own `CLAUDE.md` has no Project Document Index — ops will use the default path.

## Over-Engineering Analysis

The FIS deliberately rejected three alternatives (separate `andthen:tech-debt` skill, inline finding-level annotation, `update-review-report` ops form). The chosen design reuses the proven `update-fis observations` append protocol verbatim, which is the right call — minimum new contract surface, naturally idempotent. No over-engineering observed.

## Gap Analysis Results

### Functionality gaps

None blocking. All 9 Success Criteria have corresponding implementation prose with passing Verify lines.

### Integration gaps

**HIGH-1 — Silent severity demotion at the producer/consumer boundary**

- **Location**: `plugin/skills/remediate-findings/SKILL.md:141` (producer body shape) ↔ `plugin/skills/ops/SKILL.md:186` (consumer severity routing)
- **Requirement violated**: implicit data-fidelity expectation behind Scenario *Deferred finding lands in Tech Debt Backlog*; severity-bucket placement under the correct H2.
- **Path that triggers it**: a `--mode code` or `--mode gap` review produces a finding at `CRITICAL` severity (per `review-verdict.md` line 11). Phase 4 classifies it `DEFERRED` with strong justification (which is rare but allowed — `remediate-findings/SKILL.md:70` says "Critical / High: must fix" but does not strictly forbid deferral). Phase 5 populates the body as `Severity: CRITICAL`. Ops parses `Severity:` at SKILL.md:186, sees an unrecognized value, defaults to `Medium` per the same line ("Default to `Medium` when the severity is missing or unrecognized"), and routes the entry under `## Medium`.
- **Observable impact**: a Critical concern is silently filed under `## Medium` tech debt, where it will be triaged as "schedule deliberately" rather than "address with priority". No log line surfaces the demotion. Operators reading the backlog have no signal that the entry was originally Critical.
- **Why the spec/SKILL.md doesn't catch it**: the body-shape illustration `Severity: {High|Medium|Low}` (FIS line 126; SKILL.md line 141) suggests the producer should map upstream severities into that bucket set, but no producer-side mapping rule is written. The consumer's "default unrecognized → Medium" silently absorbs the mismatch instead of stopping or routing to High.
- **Fix options** (not chosen here — that's `andthen:remediate-findings` skill's job): producer maps `CRITICAL → High` before populating; or consumer rejects unrecognized severity instead of defaulting; or the body shape is amended to use the upstream `CRITICAL|HIGH|MEDIUM|LOW` vocabulary and ops gains a `CRITICAL → High` route rule explicitly.

### Requirement mismatches

None. The four-state status vocabulary (`RESOLVED`/`PARTIALLY RESOLVED`/`UNRESOLVED`/`DEFERRED`) is consistent across spec, ops, and remediate-findings. The Critical-ordering rule from FIS line 163 is implemented.

### Consistency gaps

**LOW-1 — Bare prose mentions of an unbundled shared asset**

- **Location**: `plugin/skills/ops/SKILL.md:29` and `plugin/skills/ops/SKILL.md:185`
- Both lines name `project-state-templates.md` as bare prose (no markdown link, no `${CLAUDE_PLUGIN_ROOT}` token). The spec's Validation block (line 208) explicitly states "consumer list is unchanged, so this is a sanity check rather than a contract change", so the omission is intentional. But the installed user-tier bundle (`~/.agents/skills/andthen-ops/references/`) doesn't ship `project-state-templates.md`, so an agent following the prose pointer would not find the file in that tier.
- Mitigated by line 185 inlining the template structure verbatim (H1 + 3× H2 + placeholder line), so file lookup isn't actually needed.
- Severity LOW: documentation/consistency wrinkle, no functional impact.

### Domain language gaps

Skipped — no `Ubiquitous Language` document registered in this project per the **Project Document Index**.

### Holistic sanity check

- End-to-end flow makes sense: review → findings → remediate → re-check → DEFERRED batch → ops appends to backlog → annotation written.
- New Phase 5 sub-sections are orthogonal to the existing FIS/plan/state update prose; ordering between them is not pinned but doesn't need to be.
- The producer-side data lineage (where the `location`, `Severity:`, and `title` come from) is implicit — the body shape communicates the requirement, but Phase 4/5 prose doesn't explicitly thread it. WITHDRAWN as a finding (the body shape itself is sufficient signal for an attentive agent).

### Verification depth — substance and wiring

- Substance: every Verify line in the FIS resolves to a real, on-target match in the implementation. No stubs.
- Wiring: argument-hint frontmatter updated; Skill-tool / slash-form invocation documented; install-time propagation works (Codex install renamed `andthen:ops` → `andthen-ops` correctly, and rewrote the `automation-mode.md` link token).
- One bundle-level concern (LOW-1 above): bare mention of `project-state-templates.md` in installed ops bundle.

## Behavioral Dry-Run Findings

**MEDIUM-1 — `## Remediation Status` heading-search ambiguity on whole-section replace**

- **Location**: `plugin/skills/remediate-findings/SKILL.md:128`
- **Walkthrough**: a review report quotes `## Remediation Status` inside a fenced code block earlier in the body (e.g., the report itself documents the contract or shows an example). On re-run, Phase 5 annotation searches "for `## Remediation Status`" with no anchoring rule (no "first H2 at start-of-line, not inside a fence", no "last occurrence"). A naive search hits the first match, overwriting from inside the fenced example to EOF, corrupting the report.
- **Impact**: rare in normal operation but possible — the H2 token is generic enough that meta-discussion in review reports could trigger it. The contract is silent on disambiguation.
- **Suggested wording**: "locate the LAST line that starts at column 0 with `## Remediation Status` and is not inside a fenced code block; overwrite from that line to EOF". The whole-section-replace logic on re-run requires a deterministic anchor.

## Remediation Plan

### High

- **HIGH-1 — Silent severity demotion** — *Acceptance*: producer-side normalization step (e.g., "before populating `Severity:`, map `CRITICAL → High`, `HIGH → High`, `MEDIUM → Medium`, `LOW → Low`; preserve unmapped severities verbatim and let ops default to Medium") added to `remediate-findings/SKILL.md` Phase 5; OR consumer-side: ops accepts the upstream vocabulary and routes `CRITICAL → High` explicitly. Update body-shape illustration in both files. Whichever path is chosen, the silent-default-to-Medium behavior is gone.

### Medium

- **MEDIUM-1 — Heading-search ambiguity** — *Acceptance*: `remediate-findings/SKILL.md:128` names the search anchor explicitly (last column-0 occurrence, not inside fenced code). One-sentence prose change.

### Low

- **LOW-1 — Bare prose mentions of unbundled `project-state-templates.md`** — *Acceptance*: either register `ops` as a consumer of `project-state-templates.md` in `CLAUDE.md` Shared Plugin Assets table (and rely on `install-skills.sh` to bundle it), or convert the two bare mentions on lines 29 and 185 to `(template structure inlined below)` framing so future readers don't expect to find the file in the bundle. The spec's Validation block (line 208) was explicit that the consumer list is unchanged, so the doc-pointer change is the lighter-touch fix.

### Dependencies and sequencing

- HIGH-1 should land before this FIS is considered canonical. It's a single-edit fix in either file.
- MEDIUM-1 can land in the same patch as HIGH-1.
- LOW-1 is truly opportunistic.

## Appendix

### Findings Filter trace

Total: 6 raw findings. Threshold (`> 5`) triggered the full Findings Filter per `lens-gap.md:149`.

| # | Finding | Initial | Verdict | Final |
|---|---------|---------|---------|-------|
| 1 | Silent severity demotion CRITICAL→Medium | HIGH | VALIDATED | HIGH |
| 2 | `## Remediation Status` heading-search ambiguity | MEDIUM | VALIDATED | MEDIUM |
| 3 | Tech-debt entry-count semantics in COMPLETION | MEDIUM | DOWNGRADED | LOW (then merged with WITHDRAWN — example carries the per-severity breakdown which is unambiguous) |
| 4 | Bare prose mentions of unbundled `project-state-templates.md` | LOW | VALIDATED | LOW |
| 5 | Missing parent-directory creation when `docs/` absent | LOW | WITHDRAWN | — (init bootstraps `docs/`; edge case is too rare) |
| 6 | Producer-side data-lineage implicitness | LOW | WITHDRAWN | — (body shape itself is sufficient signal) |

Final: 1 HIGH, 1 MEDIUM, 1 LOW.
