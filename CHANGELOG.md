# Changelog

All notable changes to **AndThen** are documented here, in a brief and concise format.
Follows [Semantic Versioning](https://semver.org/) and [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.


---

## [0.35.0] – 2026-07-05

### Changed
- **`andthen:preflight` now reconciles resolutions into the FIS body.** Ratified decisions are reworked into the sections they affect (the DECISION NOTE stays as provenance) and the resolved set is checked for contradictions before the verdict – `READY` means a coherent artifact, not just an empty ledger.
- **Review-family `--output-dir` now creates missing directories.** The directory is created (`mkdir -p`) and verified writable using the argument exactly as the caller wrote it (env-var form like `--output-dir "$VAR"` accepted) – no more re-typed existence pre-check; `BLOCKED` (auto) / warn-and-fallthrough (default) fires only on genuine create-or-write failure.
- **Sub-agent model routing is now an overridable policy.** Inherit-the-session-model + vary-effort ships as the labeled **Sub-Agent Model Policy** default in the guardrails; orchestrating skills defer to it by name, so projects/users can swap in tiered or custom strategies as first-class overrides – never version-pinned, tier aliases only.

---

## [0.34.0] – 2026-07-02

### Changed
- **`andthen:review` is leaner and proof-led** – the skill now centers reviews on a Coverage Matrix: each primary surface records evidence, positive proof, and the falsifier attempted before verdict. Test/sign-off artifacts get explicit test-contract falsification so weak assertions surface on the first pass instead of through repeated review loops.
- **`andthen:review` code lens adds a named smell baseline** – code review now checks a curated Fowler-inspired smell set as heuristic findings: project standards override it, baseline smells are never hard violations, and tooling-owned issues stay with tooling.
- **Skills infer intent from plain language – fewer flags needed.** `andthen:architecture` and `andthen:ui-ux-design` now proceed directly when your phrasing names a single mode (naming the mode so you can redirect), showing the guided menu only when the intent is genuinely ambiguous or a required input is missing. `andthen:review` picks its lens(es) from the concerns you name ("check correctness and security") above the target-signal fallback, and reads a bare "PR 42" as read-only scope.
- **Cost/outward flags stay explicit by contract.** `--council`, `--team`, `--worktree`, `--fix`, `--to-pr`, and `--to-issue` are never inferred from phrasing – they spend tokens, write code, or post externally, so they require the explicit flag. Partition fan-out is the one deliberate exception – keyed on surface shape (a semantically wide or proof-bearing diff, e.g. a standard FIS or changed tests/migrations/APIs), it makes proof-led reviews parallelize by default; `--no-fanout` opts out. READMEs now lead with natural-language examples and show the flag form as the equivalent.
- **`andthen:review` permits required sub-agents explicitly.** Review now treats skill invocation as permission for required review sub-agents and checks lazy-loaded delegation tooling before running inline.
- **Plugin-wide skill tightening (behavior-preserving).** Applied the same lean, proof-led pass to the rest of the skills: removed restated contracts, wrong-altitude prose, and accreted seams across 49 skill files (~-22k chars). Every deduplicated contract keeps a single reachable home; parser tokens, deterministic grammars, cross-skill contracts, and calibration catalogs are unchanged. Also fixed three drift/correctness issues found in passing – the `andthen:map-codebase` skill's read-only wording now matches its documented outputs, the `andthen:visualize` skill's static affordances list `Copy section`, and a dangling "Output Path Semantics" pointer in the `andthen:prd` skill now targets the Step 1 dispatch.

---

## [0.33.0] – 2026-06-30

### Added
- **New `andthen:preflight` skill** – an interactive convergence gate that drives a single FIS or a whole plan bundle to zero open blocking decisions before an unattended `exec-spec`/`exec-plan` run. It detects decisions via `review --mode doc`, settles open ADRs inline via `architecture --mode trade-off`, routes requirements-altitude gaps to `clarify`, interviews the user on each implementation-blocking decision, and persists every resolution by altitude. Emits a machine-stable `Preflight: READY | DEFERRED | BLOCKED` verdict; under `--auto` it never interviews and instead enumerates the unresolved blocking decisions as a signal. A recommended gate – the executors honor it but never require it.

### Changed
- **`andthen:ops` records decisions** – two new write forms: `update-fis decision-note <key> <resolved|deferred>` persists a preflight decision to the FIS (resolved → `## Implementation Observations`; deferred → a signed-off `## Deferred Decisions` block), and `update-decisions still-current <topic>` appends a load-bearing non-ADR choice to the `DECISIONS.md` registry. The `Preflight:` token is registered alongside `Auto-Remediation` in the loop-convergence signal grammar; `spec`/`prd` now recommend a preflight pass on residual blocking decision Notes.

---

## [0.32.0] – 2026-06-26

### Changed
- **PRD/FIS doc self-review runs in fresh context** – the `andthen:prd` and `andthen:spec` skills run post-save doc review in fresh context; FIS review blocks `spec-ready` on unresolved architecture/requirements decision Notes, and FIS-generating callers (`andthen:plan`, `andthen:exec-plan --from-issue`) preserve that block instead of force-advancing the story.

---

## [0.31.0] – 2026-06-14

### Changed
- **Skill hot-path trimming, second wave** – slimmed the always-on `SKILL.md` prompts for the remaining 16 skills, took deeper passes on `review`/`exec-spec`/`exec-plan`/`remediate-findings`, and trimmed 9 shared references in place. Reference-only content moved to skill-local refs (progressive disclosure); restatement cut; over-specified procedure compressed. Behavior-preserving – parser tokens, cross-skill contracts, and calibration examples are unchanged.
- **Machine-stable loop-convergence signals** – the `Auto-Remediation: PENDING/STALLED/CLEAR` (`andthen:review`) and `NO-OP: no-auto-applicable-findings` (`andthen:remediate-findings`) signals now carry a documented bare-line grammar (line-anchored, no fence/indent/marker, emitted once) so a consuming workflow engine can branch deterministically without scraping markdown. The contract names `Auto-Remediation` the canonical loop input and steers consumers away from a severity-based gating count, which can disagree with fix-character routing and deadlock the loop. Emission behavior unchanged.

---

## [0.30.0] – 2026-06-14

### Changed
- **Review routing keys on fix character, not severity** – `andthen:review` and `andthen:quick-review` route a finding to the auto-apply **Fix** bucket when its correction is mechanical and bounded, not by defect severity, so bounded MEDIUM/LOW fixes are no longer stranded in **Note**. Design-judgment gaps and decision/reconciliation findings still stay Note; severity still drives the verdict.
- **Hot-path skill trimming (context efficiency)** – the 12 largest always-on `SKILL.md` bundles are ~17% leaner (−7.5k words) by relocating step-specific detail into skill-local references and cutting restatement; behavior, parser tokens, and cross-skill contracts unchanged. Lowers the context cost paid on every invocation.

### Added
- **Review→remediate loop convergence signals** – `andthen:review` emits an `Auto-Remediation: PENDING | STALLED | CLEAR` loop signal beside the `## Verdict` block, and `andthen:remediate-findings` returns a `NO-OP: no-auto-applicable-findings` terminal signal, so a converging loop escalates a no-auto-fix stall to a human once instead of churning. Loop control stays with the consumer.
- **exec-plan per-story gate honors Fix/Note routing** – a story's quick-review gate now blocks only on **Fix-routed** findings; accepted **Note-routed** findings no longer fail the story (nothing is auto-applicable) but are recorded as surfaced notes and rolled up at completion for human review.

---

## [0.29.0] – 2026-06-12

### Added
- **New `andthen:explain-changes` skill – visual changeset walkthroughs** – explains a PR, branch, ref range, or working tree as a narrative Changeset Walkthrough: changes untangled into intent clusters and ordered by conceptual importance, with key diff hunks, per-file risk tags, an architectural-delta module map, and reviewer focus points. Comprehension only (findings and verdicts stay with `andthen:review`); `--to-pr` posts the walkthrough as a PR comment.
- **`andthen:visualize` renders changeset walkthroughs as an interactive app** – new `changeset-walkthrough` artifact type rendered by a bundled deterministic renderer (Node ≥18, zero dependencies) so output quality is identical on every agent: tabbed perspectives (Overview change-mosaic + cluster cards · guided cluster Tour with docked module map and review ledger · Files table with facet filters, delta bars, and a directory sunburst · Architecture module map with collision-free layout, zoom/pan, blast-radius hover, and flow playback), command palette, keyboard navigation, and notes in a slide-over drawer.

---

## [0.28.1] – 2026-06-11

### Changed
- **README intro polish** – landing intro restructured into scannable bullets with a copy-paste quick-start; tightened skill blurbs, no content dropped.
- **Review flat-dispatch rationale corrected** – the `andthen:review` chain dispatch no longer claims hosts cannot nest sub-agents (they now can); the flat sibling-batch is retained by design (single synthesizer, no lossy mid-tier). Dispatch behavior unchanged.


---


## [0.28.0] – 2026-06-09

### Added
- **Team collaboration: shared vs. session-local state split** – session-continuity notes and current focus now live in a per-developer, **gitignored** `STATE.local.md` (`andthen:ops update-state note`/`focus` route there and auto-create it), so teammates stop fighting over the shared `STATE.md`. Shared `STATE.md` keeps only team-wide, low-churn state (phase, blockers, decisions, owner-annotated active stories).
- **Story ownership** – optional `owner` field on `plan.json` stories, set via `andthen:ops update-plan-owner`, with an `Owner` column in the GitHub plan-issue Story Catalog so claiming a story is visible to the whole team and two people don't grab the same one. Survives plan regeneration and `--to-issue` republish; in `--from-issue` mode claims live on the issue and refresh into local plans on rerun; `null`/absent for solo plans.

### Changed
- **Large-codebase context scoping** – FIS tasks may now pin a read-set (critical callers/callees of changed surfaces), and the `andthen:exec-spec` skill may spawn codebase-reconnaissance sub-agents that return distilled briefs, keeping implementer context for coding. The `andthen:plan` skill gains a named enabler exception: foundational layer-shaped stories verified by tests/fitness criteria instead of demos.
- **Active Stories derived from `plan.json`** – `andthen:ops read-state` derives the shared Active Stories view from `plan.json` (stories in progress or claimed) when a plan governs current work, so nothing is stored to conflict on; the stored `STATE.md` table remains the fallback for planless and ad-hoc work.
- **`andthen:init` gitignore hygiene** – adds `docs/STATE.local.md` and `.agent_temp/` to `.gitignore` and registers a `State (local)` row in the Project Document Index; `andthen:ops` also appends the ignore entry if it scaffolds the local file first.
- **Team guidance** – `plugin/README.md` documents the recommended multi-human workflow (branch-per-story, claim via `owner`, GitHub issues as the durable source of truth).
- **Migration note** – existing repos: see `plugin/README.md` § Migration Notes (move session notes to the gitignored `STATE.local.md`).


---

## [0.27.0] – 2026-06-06

### Changed
- **`andthen:prd` resolves load-bearing gaps instead of assuming them** – conversationally, a gap that would change user-visible behavior, scope, or acceptance criteria now triggers an inline `andthen:clarify` pass rather than a documented guess; routine gaps are still assumed, and `--auto` keeps the conservative-assumption fallback (`andthen:clarify` has no automation mode).
- **`andthen:prd` runs an automatic doc self-review** – after validation it invokes `andthen:review --mode doc --fix` (both modes), auto-applying mechanical fixes and surfacing substantive gaps as Notes; conversationally it reflects on them and recommends a focused clarify pass or planning, under `--auto` it folds them into the PRD.
- **Feature-level PRDs are self-contained** – the produced `prd.md` inlines discovery substance and no longer links transient artifacts (`requirements-clarification.md`, `prd-draft.md`); durable references (issue, roadmap, ADRs) still allowed.


---

## [0.26.0] – 2026-06-06

### Added
- **Cross-skill reconciliation ledger** – adds a durable, per-FIS ledger (adjacent to each FIS) recording deliberate code-vs-FIS drift (not FIS-vs-PRD) from implementation and remediation, with recommend-only upstream reconciliation notes and gated shipped summaries while reconciliation is pending.

### Changed
- **The `andthen:exec-plan` skill's drift backstop survives partial runs** – the final gap review now runs scoped to completed stories (with a loud warning naming unreviewed skipped/failed stories) instead of being skipped wholesale, and the per-story gate emits the finding `Class:` axis so per-story drift is ledger-writable.
- **`andthen:ui-ux-design --mode design-system` emits a canonical `DESIGN.md`** – replaces `style-guide.md` with a DESIGN.md-format file (machine-readable token front matter + rationale sections); `tokens.css` becomes its CSS export. No external tooling required.
- **"Ledger" now means only the reconciliation ledger** – the `--from-issue` runtime `plan.json` is no longer called a "ledger" (now "materialized plan" / "local plan.json"), removing the collision with the new reconciliation ledger. Includes a wording change to one `andthen:exec-spec` `BLOCKED:` message ("materialized plan.json path").


---

## [0.25.2] – 2026-06-04

### Fixed
- **Planner completion contract** – `andthen:plan` now treats missing per-story FIS files as incomplete output instead of reporting successful paths that do not exist on disk.


---

## [0.25.1] – 2026-06-03

### Changed
- **Reworked the critical-rules guardrails template** – `andthen:init`'s `CRITICAL-RULES-AND-GUARDRAILS.md` is ~50% smaller, with merged overlapping rules, less emphatic framing, and clearer scope-discipline rules that fix behavior-preserving issues within a change's scope and surface anything out-of-scope.


---

## [0.25.0] – 2026-05-30

### Added
- **Intent-fidelity guardrails** – FIS authoring, exec-spec validation, review routing, and ops now distinguish right-outcome / wrong-mechanism implementations from legitimate spec/design pivots.
- **Restored the `research` agent** – Multi-source web/project research and synthesis for trade-off option investigation, competitive/landscape scans, and fact-checking. `architecture --mode trade-off` and `prd` delegate to it; ships to both Claude (plugin/user) and Codex tiers.

### Changed
- **Sub-agent model strategy: inherit the session model, vary only effort** – Review-council, `research`, and orchestrating skills inherit the session model and steer sub-agents by effort. The sole exception is `documentation-lookup`, which pins the cheap `haiku` tier alias (rot-free, quality-flat retrieval; Codex inherits). The model-effort guide and agent metadata reflect this inherit-plus-effort contract without version-pinned model names.
- **The `andthen:review` skill's finding classes** – Findings now carry `code-defect`, `spec-stale`, `design-changed`, or `ambiguous-intent` before Fix/Note routing. Spec/design drift routes to spec amendment + ADR reconciliation instead of code remediation.
- **The `andthen:exec-spec` skill's intent checks** – Mandatory fresh-context review now includes a gap pass against FIS Intent / Expected Outcomes, and Chain Attestation refuses outcomes delivered through a different mechanism than the Intent names.
- **The `andthen:ui-ux-design` skill's wireframes browser tooling** – Visual validation now defers to the project's documented browser tooling (`CLAUDE.md` / `AGENTS.md`) instead of hardcoding a Playwright → Chrome DevTools MCP order; still falls back to `andthen:visual-validation` with a manual browser when no automation is available.

### Fixed
- **Requirements spec alignment** – Reconciled reverse-spec contracts for automation scope, plan and exec status semantics, GitHub issue workflows, review routing, E2E ownership, visual fallback artifacts, installer behavior, and ID-ledger handling.
- **Quick implement automation flags** – `andthen:quick-implement` now documents and parses `--auto`, matching the shared automation surface.
- **Installed-bundle reference wiring** – Skills now copy transitive shared references and rewrite nested/local reference links correctly, keeping Codex and Claude user-tier bundles self-contained.
- **Remediation status update token** – `andthen:remediate-findings` now calls `andthen:ops update-plan` with lowercase `done`, matching the plan schema enum.
- **The `andthen:review --mode doc --fix` routing gate** – Safe mechanical document/workflow-artifact findings can now route to Fix, while unresolved intent, design, and reconciliation decisions remain Note-only.
- **The `andthen:ops` skill's `update-fis design-change` retry safety** – The design-change amendment form now no-ops on identical recent retries after the `New:` spans already landed, and validates all pairs before applying any replacement.
- **Workflow validation and routing fixes** – Restored canonical `plan.json` formatting and nested-object validation, documentation-lookup naming, granular plan-issue bullet detection, final exec-plan lint/type gates, worktree teardown semantics, and architecture-review visualizer routing.
- **Excalidraw style defaults** – `element-format.md` no longer contradicts the authoritative `style-guide.md` on default `roughness` (1, the signature hand-drawn look) or `fillStyle` (`solid`); the reference now defers instead of declaring conflicting defaults.

### Internal
- **Skill and reference prompt cleanup** – Collapsed multi-altitude restatement across every skill body and skill-local reference (one canonical statement per rule, with named pointers from GOTCHAS/recap sections), de-duplicated prose, normalized en-dashes and the `GOTCHAS` heading, disambiguated skill-noun wording, and kept tables of contents on long references. Renamed shared canonical `adversarial-challenge.md` → `findings-filter-templates.md`.
- **The `andthen:visualize` skill's progressive disclosure** – Extracted the shared render chrome (theme, layout, section-block contract, component CSS, JS layer) into `templates/render-shell.md`, cutting `SKILL.md` from ~860 to ~280 lines; added tables of contents to the visualize templates.

### Documentation
- **README overhaul** – Rewrote the root `README.md` as a shorter first-time-user overview (clearer workflow paths, explicit `architecture --mode trade-off` pre-work, corrected `clarify` → `prd` pipeline framing); moved installer/bundling detail into `plugin/README.md` and tightened both skill tables to match actual skill modes and flags.


---

## [0.24.0] – 2026-05-30

### Added
- **`andthen:review` refactor-invariants pass** – New `refactor-invariants.md`, loaded by the `code`/`gap` lenses on refactor-shaped diffs (deletion, rename, lifecycle relocation, cache, codegen, schema migration, parameter threading). Runs six cross-file invariant checks – the class of issue hunk-by-hunk review misses – with findings merged into the primary lens.
- **`andthen:review --fanout` large-diff fan-out** – New `--fanout` / `--no-fanout` flags (auto on ≥20 files, ≥1000 LOC, or 3+ packages). Partitions the diff into 2–5 vertical slices, reviews each in a sub-agent, then runs a cross-partition boundary pass. Applies to `code`/`gap`; composes with `--council`.

### Changed
- **`andthen:review` chains run as one parallel sub-agent batch** – A chain (2+ lenses, incl. resolved `mixed`) now dispatches every lens's find-pass concurrently from the orchestrator instead of sequentially, cutting wall-time and cross-lens anchoring. `--fanout`, `--council`, and chain leaves fire as siblings with no artificial concurrency cap; the host schedules the batch. Falls back to inline when sub-agents are unavailable.
- **`andthen:review` council is opt-in only** – `--council` is the sole trigger; the "multi-perspective / adversarial / critic / skeptic / thorough" vocabulary activates the review skill itself, not council. Removes the prior auto-escalation wording that contradicted the council load-gate.
- **`andthen:handoff` resume contract is the doc, not `andthen:now-what`** – The skill prints a copy-pasteable `Resume from <doc-path>` prompt; the self-sufficient doc is the contract. Removed `andthen:now-what`'s Phase 1 handoff-priming auto-detection as redundant.

### Internal
- **`andthen:review` reference cleanup** – Single-sourced the Critic-dispatch, severity-scale, FIS-context, and PASS/FAIL verdict contracts to one canonical home each (new shared `fis-context-handling.md`); added tables of contents to the long lens/calibration references; trimmed duplicated SKILL.md flag-rejection and verification-pattern wording. No behavior change.


---

## [0.23.0] – 2026-05-25

### Added
- **`LEARNINGS.md` promoted to Core orientation stub** – `andthen:init` scaffolds it by default; template clarifies the LEARNINGS-vs-DECISIONS boundary (defensive notes vs. choices with rationale).
- **`andthen:ops update-learnings` form** – `add <topic> <entry>` (bold-label-deduped, topic-routed) and `error <error> <type> [conclusion]` (Error Patterns table). 300-line size-guard warning. No file-creation exception.
- **New `andthen:handoff` skill** – Compacts the conversation into `.agent_temp/handoff/handoff-<UTC-ts>.md`; when `STATE.md` / `LEARNINGS.md` exist, auto-routes mid-flow state and clearly-bounded defensive notes there via the `andthen:ops` skill (ADRs recommend-only; missing files reroute to handoff-doc recommendations). The `andthen:now-what` skill surfaces the doc on resume; `--no-mutate` opts out.

### Changed
- **Primary `Learnings` writes route through `andthen:ops update-learnings`** – `andthen:exec-spec`, `andthen:exec-plan`, `andthen:triage`, `andthen:quick-implement` migrated from direct writes (`quick-implement` retains a spec-document fallback for projects without `Learnings`); `andthen:architecture` (trade-off / strategic-design / decompose / event-storming), `andthen:review` (any lens, generalizing the prior `gap`-only precedent), and `andthen:remediate-findings` (new Phase 6) gain the write hook.
- **Wider `Learnings` read coverage** – `andthen:prd`, `andthen:clarify`, `andthen:remediate-findings` now read it alongside existing readers in `spec`, `plan`, `exec-spec`, `triage`, `map-codebase`, `architecture`.
- **`andthen:architecture` `Learnings` phrasing aligned to the canonical Index-driven lookup form.**


---

## [0.22.1] – 2026-05-20

### Added
- **`DECISIONS.md` registry wired through the workflow** – `andthen:init` and `andthen:map-codebase` scaffold `docs/DECISIONS.md` by default (template in `plugin/references/project-state-templates.md`); `andthen:architecture` `--mode trade-off` Step 6 auto-registers accepted ADRs into **Current ADRs**, moving prior rows to **Superseded** on supersession (idempotent on ADR ID). `andthen:prd` and `andthen:spec` read it as context; spec contradictions surface as `NOTICED:` observations, not Stop-the-Line. `andthen:map-codebase` also emits `decisions-discovered.md` for brownfield validation.

### Fixed
- **`--mode advise` routing audit** – `andthen:now-what` Step 4 drops `"should I split"` from the advise row (belongs to `--mode decompose`); `andthen:exec-spec`'s upstream skill list splits `--mode trade-off` (concrete competing options) from `--mode advise` (open pattern ambiguity).


---

## [0.22.0] – 2026-05-18

### Added
- **Internal `andthen:merge-resolve` skill** – `exec-plan --team --worktree` now delegates each story merge to a private helper with a structured outcome contract.

### Changed
- **Interactive-by-Contract gates in `andthen:architecture` trade-off and event-storming modes** – discovery/design modes now stop for clarification before producing reports, and the shared headless-mode rule is execution-scoped so it no longer silently bypasses them. Fixes "trade-off ran to completion without asking" reproduced across projects. **Trade-off Step 6 now produces an ADR by default** (Step 5's hard gate offers *Proceed* / *Refine first* / *Deeper analysis* / *No ADR*; only the explicit *No ADR* opt-out skips the ADR write, with explicit population guidance per ADR section). The ADR template is extracted to a per-skill canonical (`plugin/skills/architecture/references/adr-template.md`) shared by `trade-off` and `advise` modes.
- **Intent + Rules Context threads through review → remediate → simplify** – a new shared reference is consumed by `andthen:review`, `andthen:quick-review`, `andthen:remediate-findings`, and `andthen:simplify-code` so Non-Goals / deferrals / Expected Outcomes act as falsifiers at every mutation step. Review findings now carry `Routing: Fix | Note` (only `Fix` auto-applies under `--fix`); remediate re-anchors against Intent and demotes drift to `SURFACED`; simplify drops Boy Scout cleanups that contradict Intent.
- **Surgical-scope teeth on `--fix`** – `andthen:remediate-findings` adds a per-hunk trace test, names the over-engineering shapes that creep in during remediation, and adds `caller API change required` / `data migration required` as defer-blockers. `andthen:quick-review --fix` is one-pass-only – verification surfacing new issues stops the run instead of looping.
- **FIS Structural Integrity gate dropped** – `andthen:exec-spec` no longer parser-checks heading shape; substantive FIS in either canonical or legacy shape execute without ceremony, stopping only on wrong-artifact-type.
- **`andthen:exec-plan` team-mode worktree handling simplified** – merge-time guards own leak detection; team prompts share the Worker Contract with sub-agent mode and only state team-specific overrides; tasks are orchestrator-pre-assigned with same-story self-review blocked at assignment time.
- **Wider Project Document Index lookups** – `andthen:prd` reads Architecture and Roadmap; `andthen:plan` adds Stack and Product; `andthen:spec` adds Stack; `andthen:visual-validation`, `andthen:e2e-test`, and `andthen:testing` route Wireframes / Design System / Key Dev Commands through the index. All reuse the existing parenthetical pattern – no new shared references.
- **`andthen:review --council` scales with chain shape** – on any chain of 2+ lenses a cross-lens Critic + Devil's Advocate + Synthesis Challenger pass attacks lens-boundary surface (contradictions, silence-licenses-risk, verdict-vs-finding mismatch) over the merged per-lens findings and surfaces survivors in a new `## Cross-Lens Synthesis` H2 above the per-lens sections of the `mixed-review` report. Within-lens specialist councils for `code` / `security` unchanged. `--mode doc --council` and `--mode gap --council` now reject up-front (previously silently broadened to a code or security council via the dropped "Chain contains neither" auto-append).

### Fixed
- **`andthen:exec-plan` fans out to sub-agents again** – per-story and final-review prompts now carry explicit "spawn a sub-agent" imperatives; in-orchestrator execution is recovery-only. Fixes silent fall-through to single-context execution under Codex CLI.


---

## [0.21.3] – 2026-05-18

### Changed
- **`--visual`-supporting skills gate the visualize follow-up** – the `andthen:prd`, `andthen:plan`, `andthen:spec`, `andthen:clarify`, and `andthen:architecture` skills now mark the "Review visually" follow-up as `(skip when --visual already ran)`, matching the existing precedent in `andthen:review`. Prevents the redundant "now run `andthen:visualize`" suggestion after a `--visual` run that already invoked the visualizer.


---

## [0.21.2] – 2026-05-18

### Changed
- **Shared-reference prose trim** – `plan-schema.md`, `plan-issue-shape.md`, `data-contract.md`, `github-publish.md`, and `exec-plan/references/worktree-merge-resolve.md` compressed for token efficiency (-7% to -11% per file; `worktree-merge-resolve.md` held at -2% to keep its bash steps, output-contract values, and Absolute prohibitions intact). Parser-facing headings, contract tokens, JSON examples, tables, regexes, schema fields, status enum values, and parser anchor names preserved verbatim.
- **Core FIS/plan skill prose trim** – the `andthen:spec`, `andthen:exec-spec`, `andthen:plan`, `andthen:exec-plan` skill bundles plus `fis-authoring-guidelines.md` and the skill-scoped references (`from-issue-mode.md`, `team-mode-orchestration.md`, `to-issue-mode.md`) compressed ~17%–31% per file (~21% aggregate, 26,599 → 21,172 words). Structure held: parser-facing headings and contract anchors, contract tokens (`BLOCKED:`, `OVERSIZE:`, `andthen-finalizing`, `DEFER_SHARED_WRITES`, `update-plan-fis`, etc.), exact failure strings, audit-block field shapes, status-derivation rules, and JSON field names preserved verbatim.


---

## [0.21.1] – 2026-05-18

### Changed
- **FIS Intent → Outcomes → Scenarios → Tasks anchoring made explicit** – `## Feature Overview and Goal` now carries two load-bearing sub-blocks (`**Intent**:` + `**Expected Outcomes**:`); the canonical scenario shape gains an outcome-tag set so each scenario tags the outcome(s) it exemplifies (`- [ ] **S<NN> [OC<NN>(,OC<NN>)*] [TI<NN>(,TI<NN>)*] <description>**`). Closes the chain from why-the-feature-exists through to which-task-proves-it.
- **The `andthen:spec` skill reorders to outcome-first** – new Step 3 *Articulate Intent and Expected Outcomes* precedes Step 4 *Write Acceptance Scenarios*, so outcomes anchor scenarios rather than being back-described to fit them. For plan-story / clarify-output inputs, intent and outcomes are distilled from upstream rather than authored blank-slate.
- **The `andthen:exec-spec` skill adopts Expected Outcomes as in-FIS tie-breaker** – when a scenario or task is ambiguous, the Expected Outcome(s) it tags resolve the ambiguity before raising `CONFUSION:`. Feature Overview and Goal is now first in the Step 2.4 section-reading list. Legacy FIS without an `**Expected Outcomes**:` sub-block emit a `WARN: FIS predates Expected Outcomes` line and the tie-breaker is a no-op.
- **The `andthen:exec-spec` skill gains a Chain Attestation gate at Step 5a** – before any status writes, the executor walks Intent → Outcomes → Scenarios → Tasks backwards and articulates each link with evidence; any link that cannot be evidenced is Stop-the-Line. Structural/setup tasks attest via the Structural Criterion branch; legacy FIS without `[OC<NN>]` tags degrade to Task → Scenario only; persistent `AUTO_MODE` failure emits a Failed Story Report including the partial chain articulation.
- **FIS authoring gates** – Self-Check gains *Intent vs. scope*, *Outcome ↔ Scenario coverage*, and *Task ↔ Scenario coverage* (every behavioral task referenced by ≥1 scenario or named in ≥1 Structural Criterion Verify line). Enforcement is authoring/review-time only; the FIS Structural Integrity Contract is unchanged so legacy FIS files keep executing under the `andthen:exec-spec` skill.
- **Consuming-skill alignment** – the `andthen:spec`, `andthen:exec-spec`, `andthen:plan`, `andthen:ops`, `andthen:review --mode gap`, and `andthen:visualize` skills all ship aligned with the new scenario shape and Feature Overview and Goal sub-blocks. The `andthen:visualize` skill's FIS template renders outcome chips on scenario cards (anchor-only, distinct styling from task chips) and emits `id="feature-overview-and-goal-oc<nn>"` on Expected Outcome bullets so scenario-card outcome chips backlink correctly.
- **`plugin/README.md ## Breaking Changes` renamed to `## Migration Notes`** – the section already covered non-breaking-but-parser-relevant shape additions; the new name matches its actual purpose. README WARNING anchor updated to `#migration-notes`.

**To migrate**: existing FIS files still execute; the `andthen:review --mode doc` skill will flag them on the new Self-Check gates. Re-spec via `/andthen:spec` (or `/andthen:plan` for a multi-story bundle), or hand-edit `## Feature Overview and Goal` and add `[OC<NN>]` tags to scenarios.

---

## [0.21.0] – 2026-05-14

### Added
- **`andthen:simplify-code` skill** – canonical behavior-preserving cleanup skill for clarity, reuse, quality, and efficiency. The `andthen:refactor` skill is now a deprecated redirect to it; legacy `/andthen:refactor` invocations keep working but new work should target `andthen:simplify-code` directly.
- **Review persona agents restored** – `plugin/agents/` now includes focused review agents for Critic, council filtering/synthesis, correctness, security, architecture, testing, project standards, product requirements, and agent workflow review. Claude markdown is the source of truth; Codex TOMLs are generated at install time.
- **Skill-authoring guidelines doc** – new `docs/guidelines/SKILL-AUTHORING-GUIDELINES.md` consolidates generic skill-authoring craft (frontmatter, progressive disclosure, description engineering, workflows and feedback loops, output patterns, scripts, anti-patterns, evaluation-driven authoring) with a publish checklist. Wired into `CLAUDE.md`'s foundational guidelines list so it loads when editing a skill.

### Changed
- **Simplification workflow sharpened** – no-argument scope now defaults to current branch changes, analysis is organized around reuse / quality / efficiency lenses, verification favors full lint/typecheck plus risk-scaled tests, and the `andthen:now-what` skill plus model/effort guide route cleanup/refactor cues to the new skill.
- **Review council now uses structured persona findings** – council mode prefers installed review agents, keeps Critic / Devil's Advocate / Synthesis Challenger as the fixed spine, and requires proof of attacked coverage when no findings survive filtering. Non-council reviews also prefer the `review-critic` agent for the always-on Critic pass.
- **Installer propagates agents again** – `scripts/install-skills.sh` restores `--codex-agents-dir`, `--no-codex-agents`, and `--claude-agents-dir`; `scripts/generate-codex-agents.sh` maps Claude agent markdown to Codex TOMLs.
- **Installer validation tightened** – missing option values and invalid custom prefixes now fail with explicit errors before copy or generation starts.
- **Standalone visualizer restored as visual review owner** – `andthen:visualize` is again the canonical read-only renderer; producer `--visual` flags remain convenience handoffs that delegate to it.
- **`andthen:visualize` supports every AndThen artifact type** – new first-class renderers for FIS, review reports (any lens), and architecture fitness / decompose / event-storming reports. Adds to existing support for PRD, `plan.json`, clarification, product vision, trade-off, strategic-design, and ADR.
- **Producer `--visual` flags extended to match** – `andthen:spec --visual` (FIS) and `andthen:review --visual` (consolidated report) are new; `andthen:architecture --visual` now covers every mode's primary report (was: trade-off / strategic-design / ADR only).
- **FIS format v2 (breaking)** – the structural-integrity contract now gates on `## Acceptance Scenarios` + `## Implementation Plan`; the v1 `## Success Criteria` heading no longer satisfies the gate, and `## Final Validation Checklist` is dropped from required sections to optional content. Older v1 FIS files fail intentionally – re-spec them.
- **Canonical scenario shape** – every Acceptance Scenario is a top-level checkbox `- [ ] **S<NN> [TI<NN>(,TI<NN>)*] <description>**` with nested Given/When/Then, so `ops update-fis all`, the spec/plan generation prompts, and review-tier verification can mark and audit scenarios per-line. The template, authoring guidelines, data contract, and consuming skills (`exec-spec`, `ops`, `spec`, `plan`, `review`, `now-what`, `exec-plan`) all ship aligned in this release.
- **FIS template tightened** – `### In Scope` becomes `### Work Areas` (forward-coverage inventory). Architecture Decision capped at 3-4 lines with optional `**Why this over alternatives**:`; longer trade-off analysis routes upstream to `andthen:architecture --mode trade-off`. Template-explainer blockquote callouts and HTML-commented stubs are gone.
- **Section-pattern model codified** – three patterns: *always-present* (heading + body always emitted), *visible-empty with prompt* (heading always emitted, body carries a "**Leave empty** when…" blockquote – Technical Overview, Testing Strategy, Validation, Execution Contract, Final Validation Checklist), and *content-conditional omit* (Required Context, Deeper Context – heading dropped entirely when there is nothing to inline). See plugin/README §0.21.0 for the full surface.
- **Authoring discipline named** – the FIS authoring guidelines now name the `unavailability test`, outcome-shape audit, Verify prescribed-detail audit, and forward-coverage check. Self-Check gains anchor + Verify dry-run audit, cross-consumer surface inventory, prose-vs-Verify scope alignment, and empty-section discipline.
- **Authoring guidelines trimmed** – symbol-anchor ladder collapsed into a heuristic, canonical scenario shape deduplicated to a single home, Self-Check compressed into named principles.
- **No format versions in skills or references** – stripped `v1`/`v2` qualifiers from skill prompts and shared references (template, authoring guidelines, data contract, ops/spec/visualize/review skills). Version history lives in README and CHANGELOG only. The visualizer drops legacy `## Success Criteria` / `## Scenarios` rendering paths; the structural-integrity gate already rejects those FIS files at execution time.
- **`remediate-findings` severity policy tightened** – fix is the default for every reviewer-flagged finding (all severities, including INFO with a remediation suggestion); defer only with a named blocker. The `out-of-scope file` blocker now explicitly excludes upstream IO carve-outs – a file the reviewer cited is in-scope here, regardless of prior-pass scope decisions.
- **CRITICAL-RULES de-named** – surgical-scope and Boy Scout rules no longer enumerate specific skills; mode is determined by the active skill's *job* (review-, cleanup-, or remediation-driven vs implementation-driven). Adding or renaming skills no longer requires CRITICAL-RULES edits.
- **Guardrails pass in the `andthen:review` skill and the `andthen:quick-review` skill** – before the lens / Critic rubric, both skills enumerate the project's rules / guardrails / principles / guidelines from context, filter to diff-verifiable rules, and emit findings citing each violated rule by source, plus a `Guardrails Coverage: N checked, M findings` line in the consolidated report. Converts long-conversation rule decay from an invisible failure mode into a named, verifiable axis.
- **Project-rule preamble broadened across 18 skills** – implementation, authoring, and review skills now explicitly read project rules, guardrails, principles, and guidelines from `CLAUDE.md` / `AGENTS.md` and referenced files before starting. Drops the assumption of a single `## Project-Specific Guidelines and Rules` section name; covers all four rule classes generically.

### Fixed
- **Visualizer module-map detail bodies are inert text** – strategic-design node detail content now renders as escaped text with preserved line breaks instead of flowing artifact-derived content into raw `innerHTML`.

---

## [0.20.0] – 2026-05-12

### Added
- **`andthen:visualize` supports `plan.json`** – local plan bundles now render as first-class visual artifacts with virtual sections for overview, story catalog, dependency lanes, shared decisions, binding constraints, risks, and execution notes. Plan review notes can feed `andthen:plan`, `andthen:exec-plan`, or `andthen:review --mode gap`.

### Changed
- **`CRITICAL-RULES-AND-GUARDRAILS.md` gains four core behavioral rules** – `Read before write`, `Fail loud, not silent`, `Tests verify intent, not just behavior`, `Surface conflicts, don't average them`. Ships to every project that runs `andthen:init`.
- **`CLAUDE.template.md` restructured into two distinct rule-sections** – `## Foundational Rules, Guardrails and Principles` (universal critical-rules pointer, top of file) and `## Project-Specific Guidelines and Rules` (project conventions, prohibitions, Visual Validation Workflow). New `## Do Not / Never` stub section.
- **Foundational rules install guidance** – setup-instructions HTML block describes three install options for `CRITICAL-RULES-AND-GUARDRAILS.md`; user-level install (copy contents into `~/.claude/CLAUDE.md` + `~/.codex/AGENTS.md`) is recommended as the cross-tool primary (`@`-import demoted to Claude-only since Codex treats `@` as literal text). READMEs aligned with the same guidance.
- **`docs/ARCHITECTURE.md` introduced as a core orientation doc** – the template's `## Project Overview` now points to it for deep architectural detail, keeping `CLAUDE.md` lean. AndThen's own repo follows the pattern.
- **`andthen:init` scaffolds Core orientation stubs by default** – `PRODUCT.md`, `ARCHITECTURE.md`, `STACK.md`, `KEY_DEVELOPMENT_COMMANDS.md` now created automatically on new-project setup and on partial-setup repair; only Planning / Domain / Monorepo docs remain interactive.
- **Section rename: `## Workflow Rules, Guardrails and Guidelines` → `## Project-Specific Guidelines and Rules`** – disambiguates from the new sibling `## Foundational Rules, Guardrails and Principles`. All skills look for the new name; existing projects can re-run `andthen:init` to repair (or rename the section manually). `andthen:visual-validation`'s `## Visual Validation Workflow` check relaxed to any heading level (template now nests it as H3 under the new section).
- **`andthen:clarify` hardened as Interactive-by-Contract + dual-scope (feature/product)** – names the **Interactive-by-Contract** principle to neutralize *Headless by default* drift; Step 2 is now a hard gate (zero answered questions → cannot proceed) and reframed as **Discovery & Ideation** (probing latent requirements + proposing alternatives). New `--mode product|feature` (inferred from INPUT) – product mode writes the Project Document Index `Product` location (default `docs/PRODUCT.md`) from a vision/personas/value-props/anti-goals/metrics template and routes follow-ups to `andthen:architecture --mode strategic-design`, `andthen:prd` per epic, and `andthen:ubiquitous-language`. `AskUserQuestion` promoted to the primary Claude Code mechanism (markdown 3–5-question fallback elsewhere); `andthen:now-what` Step 2 gains a product-vision routing row.
- **`andthen:visualize` adds ADR and first-class Strategic-Design support** – ADR files (`# ADR-NNN: …`) and architecture strategic-design reports are now first-class visualized types (previously: detection error / generic-prose fallback). Strategic-design renders an interactive **module map** from a `mapviz` block in the source: a click-to-explore SVG with a paired detail panel that updates as the reviewer clicks each component. ADRs show a status pill (Proposed / Accepted / Superseded / Deprecated), option cards for alternatives, an accent-boxed Decision, and a Positive / Negative / Neutral three-bucket Consequences layout.
- **`andthen:visualize` opens every render with richer document context** – new eyebrow line (artifact type), H1, and a wrapping status pill row carrying status, section count, open-question count, last-updated, and short SHA. A four-cell KPI summary band sits below (per-artifact cells: e.g. PRD shows Capabilities · Stories · Open Questions · Risks; ADR shows Status · Alternatives · Consequences · Related), and an optional Where-to-Focus list ranks the 2–5 most important things to review first — turning a 12-section document into a 3-priority walk. The focus list omits itself when fewer than 2 items would render.
- **`andthen:visualize` new interactive affordances and renderers** – numbered section badges (`01 02 03 …`) for orientation; risk-map chips above summary sections (clicking a chip jumps to its section and briefly highlights it); collapsible supporting-detail blocks under trade-off Options and PRD Risks; a per-section **Copy section** button alongside `+ Note` and `View source`; indented sub-entries in the sidebar TOC for in-section subheadings; light TL;DR callouts at the top of heavy sections; smooth in-page scrolling. Numbered **step walkthroughs** replace flowcharts in PRD User Flows, trade-off Options, and clarification Resolved Decisions when substeps carry substantial prose, each with a collapsible source listing.
- **`andthen:visualize` switches to a warm-light Anthropic-style theme** – ivory background, warm-dark slate text, clay coral (active / interactive) and deep olive (resolved / done) accents, with rust for failure and amber for caution. Headlines use a serif family (Tiempos / Charter fallback chain); body stays sans, code and metadata stay monospace. Color is load-bearing: the reviewer's eye learns the four-color signal within seconds and navigates by it. Status pills, risk chips, recommendation boxes, scoring-matrix highlights, capability cards, and risk levels all inherit the new tokens. Replaces the previous dark theme entirely.

### Removed
- **`plan.json` digest enforcement (`metadata.immutableDigest`) dropped** – the canonical-form sha256 baseline shipped in 0.19.0 was over-engineered ceremony that BLOCKED benign hand edits. The writability rule (only `andthen:ops` mutates `status`/`fis`) remains as skill-level guidance; legacy `metadata` blocks are silently discarded on the next `andthen:plan` regeneration.

### Fixed
- **`andthen:init` Core stub scaffolding completed** – `PRODUCT.md` template added to `project-state-templates.md` (the other three Core stubs already had templates); SKILL.md Steps 2a/2b reworded from "minimal stubs (heading + brief TODO line)" to "scaffold from the templates in `project-state-templates.md`" so the instruction matches the now-richer template assets.
- **`andthen:init` Final Summary made truthful** – Step 3 summary now lists the four Core stubs explicitly and instructs printing only what the current run actually created, replacing a static example that read as a checklist and could claim creation of files that already existed.
- **Skills now consume `PRODUCT.md` / `ARCHITECTURE.md` per Project Document Index** – `andthen:clarify` (feature mode), `andthen:prd`, `andthen:plan`, `andthen:spec`, `andthen:exec-spec`, `andthen:quick-implement`, `andthen:refactor`, `andthen:review --mode code`, `andthen:triage`, `andthen:architecture`, and `andthen:ubiquitous-language` now reference the Core orientation docs at their natural context-reading points using the established `` `<DocName>` document (see **Project Document Index**) `` pattern. Skills consume them when present; absent docs remain non-blocking.

---

## [0.19.2] – 2026-05-11

### Changed
- **`andthen:architecture --output-dir` promoted from trade-off-only to general Output Flag** – applies to all modes as a tier-1 override of the report-location resolver (`review-report-location.md`). Trade-off mode retains the dual use of the path as the research-artifacts subtree root at `OUTPUT_DIR/[topic-slug]/`, with the report file alongside the subtree at `OUTPUT_DIR/`; trade-off's default OUTPUT_DIR (Project Document Index Research location, or `<project_root>/docs/research/`) preserved in the SKILL.md flag doc. Composes with `--to-pr` (writes to `--output-dir`, then posts as PR comment).
- **`## Variables` sections removed from mode references; UI/UX inputs hoisted to SKILL.md** – eliminates the silent-override risk where mode-ref `## Variables` blocks competed with the SKILL.md contract surface. `architecture/mode-trade-off.md`, `ui-ux-design/mode-design-system.md`, and `ui-ux-design/mode-wireframes.md` now carry a one-line `**Inputs**` breadcrumb anchored at the specific SKILL.md subsection. `ui-ux-design/SKILL.md` gains a `### Mode Inputs` subsection declaring per-mode named tokens with binding-type discrimination (required input / optional contextual input / default destination).

---

## [0.19.1] – 2026-05-11

### Changed
- **`exec-plan --team --worktree` worktree lifecycle is bash-driven** – harness isolation (`EnterWorktree`, `Agent({isolation:"worktree"})`) is unreliable under `team_name`, so it's replaced by **pre-create-and-verify isolation**: `create-worktree.sh` pre-creates the worktree, the implementer runs `verify-in-worktree.sh` as its first action every turn, and absolute paths are mandatory (relative paths silently leak to the main checkout).
- **Merge Wave squash hardened with three guards + output-encoded status** – `merge-worktree.sh` runs PRECONDITION (CWD repo + branch + clean), G1 (branch has commits beyond merge-base), G2 (no diffs against `--guard-path` files), G3 (worktree clean), then squash and commit with a load-bearing `Squashed-story:` trailer. Guard failures preserve the worktree and drop a `.andthen-fail-reason` marker that `teardown-worktrees.sh` surfaces as `UNMERGED:<branch>:<reason>`.
- **Squash conflicts route to a `worktree-merge-resolve.md` sub-agent** – semantic resolution (imports → union, lock files → worktree side, logic → reasoned tie-break or `outcome: failed`), runs `Key Dev Commands` verification, commits all-or-nothing. Absolute prohibition on `git reset` / `git clean` / `git checkout .` / `git branch -D` on any failure path.
- **Skill prose trim across `exec-plan`** – external URLs and historical bug references removed, restated procedures cut, **pre-create-and-verify isolation** named; counter-intuitive notes (slash-command `$VAR` non-expansion, `git branch -D` under squash-merge) preserved.
- **Teammate contract hardenings** – Step 1 logs `BASE_BRANCH` and warns on non-default; implementer prompt gains **Post-impl HARD GATE** and **Inbox-STOP first**; Implementer/Reviewer carry **Self-review prevention** (no `review-Sxx` after `impl-Sxx`); new `## Known Limitations` section documents mid-turn-interrupt absence and self-claim race semantics.

---

## [0.19.0] – 2026-05-08

### Changed
- **Plan output flips to `plan.json` (canonical, machine-parseable)** – `andthen:plan` now emits a typed JSON manifest per the new shared `plan-schema.md` (consumed by `plan`, `exec-plan`, `ops`, `review`); `andthen:ops update-plan` / `update-plan-fis` are the only mutators, gated by a `metadata.immutableDigest` baseline that refuses writes touching any non-mutable field. Re-running `andthen:plan` on a legacy `plan.md`-only directory migrates to `plan.json` and preserves existing FIS files; `andthen:exec-plan --from-issue` parses the plan-issue body once into a local `.agent_temp/from-issue-<N>/plan.json` ledger and drives execution from there.
- **`andthen:remediate-findings` Low-severity policy inverted to fix-by-default** – Phase 2 flips the Low rule from "fix only when cheap" to fix-by-default, with `DEFERRED Low` requiring one of four named blockers (`out-of-scope file`, `decision needed`, `new test harness required`, `risk: <concrete>`); Phase 4 findings re-check and Phase 5 tech-debt persistence both propagate the blocker so the rule cannot rot at later phase boundaries. New GOTCHA names writing `DEFERRED Low` without a blocker as the parking-lot anti-pattern itself.

---

## [0.18.1] – 2026-05-06

### Fixed
- **`exec-plan --auto` story failure containment** – failed stories now stay scoped to their dependency chain: partial work is preserved, dependents are skipped, independent stories continue, and the run ends with an aggregate failure report. `exec-spec --auto` now classifies dirty retry worktrees before editing and returns a structured failed-story report instead of asking for approval.

---

## [0.18.0] – 2026-05-05

### Added

### Changed
- **Plan story sections are now compact story briefs** – `Status`, `FIS`, phase/wave, dependencies, parallelism, and risk live only in the Story Catalog. Phase Breakdown stories carry `Scope`, PRD-backed `Source refs`, plus optional provenance, asset refs, and notes; FIS files own detailed success criteria and scenarios.
- **Plan dependency cells are explicitly machine-readable** – `Dependencies` now accepts only `-` or comma-separated Story IDs from the same Story Catalog. Broad sequencing prose belongs in `## Dependency Graph`, phase notes, or execution guidance; `exec-plan` now blocks with a targeted invalid-dependency message before scheduler handoff.

### Removed
- **`andthen:plan --skip-specs`** – plan-only output is no longer a public mode. Local `andthen:plan` always aims to produce an executable bundle (`plan.md` + one FIS per story), while interrupted or legacy partial bundles are resumed by re-running `andthen:plan`. GitHub `--to-issue` remains the intentional no-local-FIS publication path, with `exec-plan --from-issue` materializing FIS just-in-time. Legacy invocations now fail with a targeted removal message instead of being parsed as input.
- **`andthen:plan --stories` and `--phase`** – targeted plan-side FIS generation filters are no longer public modes. Re-running `andthen:plan <dir>` fills every missing FIS; use `andthen:spec story <id> of <plan.md>` for one-off story spec generation.

### Fixed
- **Compact GitHub plan stories keep resolvable PRD source** – local `andthen:plan --issue` now materializes the fetched PRD issue as `OUTPUT_DIR/prd.md`; plan issues carry a `> **PRD**:` source header; and `exec-plan --from-issue` resolves that source into JIT FIS temp files so `Source refs` do not collapse into symbolic-only hints.
- **`exec-plan --from-issue` no longer treats `github://issue/<N>` as a local plan path** – JIT FIS provenance stays traceable, while `exec-spec` runs with deferred shared writes and issue-side completion is represented by closure comments instead of `andthen:ops update-plan` against a synthetic URI.
- **Installed `spec` and `review` bundles now carry `data-contract.md`** – their copied `fis-authoring-guidelines.md` / `fis-template.md` links resolve under Codex and Claude user-tier installs.
- **`andthen:init` guideline setup** – starter guidelines now ship inside the init skill bundle (`templates/guidelines/`) so Plugin, Claude user-tier, and Codex installs can actually copy them; repo-level `docs/guidelines/` is a symlink to that bundled template directory to avoid duplicate files. The generated agent instruction template now references `docs/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md` instead of the stale `docs/rules/` path and treats `CLAUDE.md` / `AGENTS.md` as first-class setup targets. `andthen:map-codebase` now emits conventions for whichever root agent instruction file exists instead of hard-coding `CLAUDE.md`.

---

## [0.17.0] – 2026-05-05

### Added
- **Selective skill installs** – `scripts/install-skills.sh` now accepts `--skills <comma-separated-list>` to export only named source skills, with upfront validation, duplicate handling, support for prefixed names, and the same self-contained copy/rewrite pipeline used by full installs.

### Changed
- **Claude installer flag simplified** – `--claude` is now the documented Claude Code user-tier install flag. `--claude-user` remains accepted as a backward-compatible hidden alias.
- **`.technical-research.md` artifact eliminated** across `andthen:plan` and `andthen:spec` (batch and standalone). Plan's old Step 5 (3-sub-agent technical research fan-out) is gone, FIS template loses its `> **Technical Research**:` reference line, and `plugin/skills/plan/templates/technical-research-template.md` is removed.
- **`andthen:plan` reads the PRD once.** Step 2 reads `prd.md` directly (no sub-agent); the cross-cutting review sub-agent in Step 6 is the only other PRD read (fresh context for validation). Previously the PRD was loaded 3+ times across orchestrator and sub-agents.
- **Two new optional plan sections absorb the load-bearing extraction**: `## Shared Decisions` (inter-story interface contracts) and `## Binding Constraints` (verbatim PRD spans + heading anchors that flow unchanged into FIS Required Context). Inline-extracted by the orchestrator in Step 4, no sub-agent fan-out.
- **Plan-template reference header is now extensible.** Fixed-slot blockquote (PRD/ADRs/Design System/Wireframes/Technical Research) becomes a generic `**References**` bullet list with PRD as the only named slot – accommodates ad-hoc upstream artifacts without privileging any single category.
- **`andthen:spec` Step 2 reframed to "Identify Required Inputs"** – lightweight check that confirms upstream artifacts exist and surfaces obvious gaps via `MISSING REQUIREMENT:` / `BLOCKED:`. Spec no longer invokes `andthen:architecture --mode advise/trade-off` or `andthen:ui-ux-design` from inside Step 2; those are upstream prerequisites in the canonical chain.
- **External API/library research deferred to `andthen:exec-spec`.** Exec-spec's documentation-lookup sub-agent contract tightened ("do not pause and ask") so executors reliably reach for it on unfamiliar API surface. Exec-spec Step 2 drops the "Read Technical Research" substep and renumbers.
- **FIS template trims**: Architecture Decision demoted to a one-line default (full Alternatives form is opt-in only when an inline trade-off actually happened – otherwise reference the ADR); Technical Overview reframed as the home for spec-time elaborations only (load-bearing material belongs in Required Context).
- **`fis-authoring-guidelines.md` simplifications**: `## Technical Research Separation` section deleted; Cross-Document References rule #4 simplified; Reverse Coverage Check updated to read `## Binding Constraints` from `plan.md`.
- **GitHub-issue plan shape** (`plan-issue-shape.md`, `to-issue-mode.md`, `exec-plan --from-issue`, `from-issue-mode.md`) deprecates `## Technical Research` as a producer-emitted section (parser tolerance retained for legacy issues). New parser anchors `## Shared Decisions` and `## Binding Constraints` round-trip the load-bearing pieces; `exec-plan --from-issue` no longer materializes `## Technical Research` to a temp file.
- **`andthen:visualize` durability contracts** – `SKILL.md` adds *Layout Skeleton*, *Section Block*, *Sidebar Behavior*, *Renderer Discipline*, and *JavaScript Authoring Discipline* sections preventing four named regressions: empty Non-Functional Requirements section (a renderer dispatched against a schema it didn't fit), every button on the page going inert (literal newlines inside regex / quoted-string literals threw a `SyntaxError` disabling the entire `<script>`), invisible TOC on common laptop widths, and missing `+ Note` / `View source` affordances (JS-injected buttons vanished if JS failed). Section Block requires both `id` and `data-anchor` per H2 with static-HTML affordances; Renderer Discipline carries a per-section schema-contract table, an inline canonical Non-Functional Requirements renderer, and a section-deduplication mechanism.

---

## [0.16.0] – 2026-05-04

### Changed
- **Agent-to-skill consolidation** – added the `andthen:visual-validation` skill, removed the `research-specialist` and `visual-validation-specialist` agents, and slimmed `documentation-lookup` to a Claude Code plugin-tier-only agent that reads the project's `## Documentation Lookup Tools` contract first. Deleted `scripts/generate-codex-agents.sh`, removed all agent-install logic from `scripts/install-skills.sh`, and added the documentation lookup tool-priority section to the init template. Manual cleanup for stale user-tier agent files from older installs: `rm ~/.codex/agents/andthen-{documentation-lookup,research-specialist,visual-validation-specialist}.toml ~/.claude/agents/andthen-{documentation-lookup,research-specialist,visual-validation-specialist}.md`
- **Skill bloat trim across the corpus** – ~750 lines net removed against the *Skill and Prompt Authoring Guidelines*: ceremonial preambles, restated rules, stale `## Issue Classification` tables, and tutorial-shaped reference content cut from skill prompts and shared references. Mode flags, integration contracts, named principles, and parseable anchors preserved.
- **`andthen:e2e-test` AUTO_MODE bypass** – `FOLLOW-UP ACTIONS` section skips when `AUTO_MODE=true`, matching `andthen:architecture`, `andthen:triage`, and `andthen:ui-ux-design`.
- **`review-calibration.md` Anti-Leniency Protocol** gains rules 7 (no hedging language) and 8 (disclaimer-as-finding inside changed files). Re-threads two adversarial-lens rules so every review lens (doc/code/gap/security) carries them.
- **`Pre-0.14.x` version qualifier** removed from `data-contract.md` per the "no version history in skill prompts" rule; structural-failure-on-old-FIS content preserved.
- **`Key Dev Commands` anchored across execution skills** – `andthen:exec-spec`, `andthen:exec-plan`, `andthen:quick-implement`, `andthen:refactor`, `andthen:remediate-findings`, `andthen:triage`, and `andthen:review`'s `lens-code.md` now point build/format/lint/type-check/test invocations at the canonical `Key Dev Commands` document with discovery as fallback. New `Format` peer check added to `andthen:exec-spec` (Build/Tests/Lint/Format), defaulting to `--check` so pre-existing drift routes to `NOTICED BUT NOT TOUCHING` instead of the diff.

### Fixed
- **`andthen:quick-review` install propagation** – `review-calibration.md` now propagates alongside `lens-adversarial.md` and `critic-calibration.md` in `_skill_assets_quick_review` and the sub-agent dispatch contract. Closes the gap where installed bundles silently dropped the canonical Anti-Leniency rules.
- **`scripts/install-skills.sh` exit status** – successful installs now exit `0` even when an optional counter is zero. The trailing `[ "$count" -gt 0 ] && printf …` chain was short-circuiting the script's exit status to `1`; replaced with `if` blocks plus an explicit `exit 0`.
- **Skill-bundled script paths under non-Plugin install tiers** – adopt the Anthropic-documented `${CLAUDE_SKILL_DIR}` substitution for skill-bundled scripts (team-mode teardown, security-scan invocations). Plugin and `--claude-user` tiers resolve natively; `install-skills.sh` rewrites to the absolute install path for the Codex tier and rejects bare `$CLAUDE_SKILL_DIR` via the same strict-braces rule already used for `$CLAUDE_PLUGIN_ROOT`.
- **`install-skills.sh` strict-braces validator EOL gap** – bare `$CLAUDE_PLUGIN_ROOT` / `$CLAUDE_SKILL_DIR` at end-of-line silently passed validation because `[^}]` required a following character. Tightened both validators to `([^{]|$)` so any non-braces form is rejected regardless of position.
- **`install-skills.sh` `_canonicalize_dir` silent fallback** – relative `--skills-dir` / `--claude-skills-dir` arguments could fall through to the original (relative) path on `mkdir`/`cd` failure, producing broken absolute-path rewrites in installed `.md` files. Now fails loud (`error: cannot canonicalize directory <path>`) and aborts the install.
- **`install-skills.sh` `_canonicalize_dir` empty-arg leak** – an empty `--skills-dir ""` / `--claude-skills-dir ""` argument silently resolved to the script's cwd via `cd ""` (a bash no-op), causing the install to write 24 `andthen-*/` bundles into the script's working directory (typically the repo root). Added an empty-input guard at the top of `_canonicalize_dir` so the failure is loud (`error: cannot canonicalize empty path …`) before any copy runs. Triggered in practice when calling code's `$(mktemp -d)` failed silently (e.g., sandboxed `$TMPDIR`) and produced an empty value.
- **`install-skills.sh` non-deterministic `find` ordering** – `rewrite_plugin_root_dir` / `rewrite_skill_dir_dir` / `rewrite_namespace_dir` iterations now `LC_ALL=C sort` the file list so reinstalls are byte-stable across machines.
- **`install-skills.sh` silent pipeline failures** – switched shebang to `#!/usr/bin/env bash` with `set -o pipefail` so early-pipeline errors abort instead of silently producing empty lists; validator pipelines moved to `grep -m1` to avoid SIGPIPE-tripping pipefail. **Note**: bash is now required (some minimal Alpine images will need it installed first).
- **`andthen:plan` consumer claim for `fis-template.md` / `prd-template.md`** – both rows in the CLAUDE.md "Shared Plugin Assets" table and the `_skill_assets_plan` map listed `plan` as a consumer, but after the trim the `andthen:plan` skill delegates FIS authoring to the `andthen:spec` sub-agent and PRD synthesis to the `andthen:prd` skill – no direct reference remains. Both rows now correctly reflect single-skill consumption (`spec` / `prd` only).
- **`andthen:now-what` Phase 1 detection coverage** – extended the in-flow signal row to also check `requirements-clarification.md`, the most recent architecture-report, the most recent triage-report, and ui-ux-design outputs. Phase 4 previously routed on these without Phase 1 looking for them, mis-classifying mid-flow users as "no work in progress."
- **`andthen:now-what` Phase 4 routing coverage** – added rows for triage / architecture / strategic-design / trade-off / ui-ux-design mid-flow states so users with any of those reports get routed instead of silently treated as fresh starts.
- **`andthen:now-what` `--auto` contract** – explicit instruction added: skip interactive prompts, emit `BLOCKED: now-what cannot route headlessly without an idea or unambiguous mid-flow state` when the route is ambiguous and the user has not provided one.
- **`andthen:visualize` anchor scheme** – documented the `data-anchor-parent` attribute used by the trade-off template's per-option H3 cards (purely a CSS/DOM hook; only H2 sections carry `data-anchor` and a Note affordance).
- **`andthen:visualize` `notesDirty` on restore** – accepting a "Restore previous notes?" prompt now sets `notesDirty = true`, so closing the tab without a fresh clipboard copy re-arms the `beforeunload` warning. Restored notes were never copied to clipboard *in this tab*; treating them as already-saved was a data-loss footgun.
- **`andthen:visualize` output path resolution** – `.agent_temp/visualize/<slug>-<ts>.html` now resolves against `git rev-parse --show-toplevel` when inside a git working tree (falling back to CWD outside one), matching the convention other AndThen skills use for `.agent_temp/`. Previously CWD-relative, which surprised users invoking from subdirectories.
- **`andthen:init` `STOP and WAIT` parseable anchor** – restored as bolded inline emphasis (was softened to "wait for the user's selection" in the trim). Behaviour unchanged; the parseable signal is back.
- **`andthen:exec-spec` Anti-rationalization examples** – restored four named-rationalization quotes ("I'll verify after the next group", "this failing check is unrelated", etc.) as a one-line dense list inline under the principle. The named principle survived the trim; the comparison set didn't.
- **`mode-event-storming.md` pink/red sticky-note rationale** – was vague ("sometimes used for external systems… keep it optional"); now anchored to Brandolini's canonical use (Big Picture only, when external integrations are load-bearing).
- **`mode-event-storming.md` brownfield asymmetry** – added a one-line rationale clarifying that brownfield event-storming converges on the same outputs as greenfield with the codebase as memory aid, not a separate path.
- **`install-skills.sh` `claude_skills_dir` canonicalization** – gated on `install_claude_user=1` so plugin-only / Codex-only runs no longer pre-create `~/.claude/skills` via the `mkdir -p` inside `_canonicalize_dir`.
- **CLAUDE.md `${CLAUDE_SKILL_DIR}` reference-syntax scope** – clarified to match the Anthropic doc quote: required for *bash invocations* of bundled scripts; markdown links and prose references to bundled `templates/` / `scripts/` / non-canonical `references/` may use bare-relative paths. Resolves the corpus-vs-guidance inconsistency the trim review flagged as Low tech debt.

### Added
- **`andthen:architecture --mode strategic-design`** – discovery-oriented strategic-DDD mode: subdomain classification (core/supporting/generic), bounded-context discovery and sizing, context map across the 9-pattern catalog (8 Evans + Big Ball of Mud), UL touchpoints. Supports both greenfield (clarification artifact / PRD) and brownfield (current vs target context map with drift findings) paths; delegates UL extraction to the `andthen:ubiquitous-language` skill, board diagrams to the `andthen:excalidraw-diagram` skill, and visual report review to the `andthen:visualize` skill.
- **`andthen:architecture --mode event-storming`** – Brandolini three-level event-storming session (Big Picture / Process Modeling / Design Level): orange events, blue commands, yellow actors, lilac policies, purple hotspots, green read models. Produces event timelines, command/actor maps, hotspots, and subdomain or aggregate candidates; canonical chain `event-storming → strategic-design → decompose` covers end-to-end discovery into decomposition.
- **`andthen:visualize` recognises strategic-design reports** – Artifact Type Detection adds a `strategic-design` row (H1 contains "strategic design" OR H2 set contains "subdomains" + "context map"), ordered before `tradeoff` so the more-specific marker pair wins. Renders through the generic-prose passthrough – no specialized template; specialized renderers (context-map visual, subdomain-tree card grid) deferred.
- **`andthen:visualize` skill** – renders a PRD, `requirements-clarification.md`, or architecture trade-off report as a self-contained HTML view with section-anchored notes the user pastes into downstream skills (`prd`, `clarify`, `architecture`). Auto-detects artifact type; outputs to ephemeral `.agent_temp/visualize/<slug>-<ts>.html`. End-of-run hints wired into the upstream skills and `andthen:now-what` Phase 4 routing.
- **`andthen:now-what` skill** – first-stop router for users new to AndThen or unsure what to do next; inspects project state (init'd? greenfield? brownfield? mid-flow?) and routes to the right skill (`init`, `map-codebase`, `clarify`, `prd`, `architecture`, `ui-ux-design`, `triage`, etc.) with heavy onboarding for first-time setup and terse routing mid-flow. Includes a `Skill Reference` section (one entry per AndThen skill – purpose, output, workflow position) governed by a new `CLAUDE.md` "Skill Reference maintenance" guideline; `andthen:init` closing message updated to surface `/andthen:now-what` as the recommended entry point.
- **`plugin/references/execution-named-blocks.md`** – new shared asset consolidating the `CONFUSION:` / `NOTICED BUT NOT TOUCHING:` / `MISSING REQUIREMENT:` block protocol used by `andthen:exec-spec`, `andthen:quick-implement`, and `andthen:triage`. Per-consumer arrow-prompt phrasing and `AUTO_MODE` override semantics preserved.
- **`plugin/skills/review/references/lens-findings-filter.md`** – shared snippet replacing the near-byte-identical Findings Filter sections in `lens-doc.md` / `lens-gap.md` / `lens-security.md`. Lens-specific severity-checking and verdict timing preserved.
- **`plugin/references/github-publish.md`** – new shared asset extracting `gh issue create` / `gh pr comment` / `gh issue comment` recipes into Patterns A (create new issue with `Refs #<input-N>` provenance), B (post existing summary as PR comment), and C (comment-then-close for granular issue closure – sidesteps `gh issue close --comment`'s shell-escape and 65,536-char limits). No behavior change.
- **GitHub integration expansion** – new `plugin/references/plan-issue-shape.md` defines single-issue and granular plan-issue body contracts. New `--from-pr` / `--from-issue` / `--to-pr` / `--to-issue` / `--create-story-issues` flags wired across `review`, `plan`, `exec-plan`, `exec-spec`, `clarify`, `prd`, and `triage`; full flag matrix and mutual-exclusion rules in `plugin/README.md`.

---

## [0.15.9] – 2026-05-01

### Added
- **`andthen:quick-review --inline`** – apply the Critic rubric directly in the current conversation instead of dispatching a fresh-context sub-agent; use when the calling conversation has not produced or substantively reasoned about the change set under review, otherwise the `--inline` branch verifies caller freshness up-front and emits `FALLBACK: --inline rejected, dispatching sub-agent (calling conversation not fresh w.r.t. change set)` then continues with default dispatch – fallback is surfaced in the final report, never silent, `AUTO_MODE` included. Phase 4 carries an `--inline`-specific anti-leniency reminder since generator and evaluator collapse into one context under the flag (and applicator too under `--inline --fix`) – dismissals require a concrete falsifier (observed mitigation in the artifact, explicit upstream citation, calibration match), never recall ("I already considered that") or recency ("I just wrote that and it seemed fine"); `--inline` reads `lens-adversarial.md` + `critic-calibration.md` directly rather than pasting them into a sub-agent prompt. Default dispatch behavior is unchanged; new GOTCHA names the non-fresh misuse case.

### Changed
- **Red-Team → Critic vocabulary rename** – the always-on adversarial finding pass is now the **Critic** Lens / Sub-Lens / Reviewer, aligning with the ASDLC Critic Agent pattern that the rubric content was originally descended from and with the Citation Convention added in 0.15.6 (which the prior "Red-Team" labeling predated); also defuses the security-priming the broader-than-security lens carried under the old name. `'red-team review'` and `'red-team this'` retained as additive trigger phrases for routing parity; `lens-security.md`'s OWASP attacker posture is unchanged (it lives in natural-language attacker vocabulary, independent of the role-noun).

---

## [0.15.8] – 2026-04-30

### Added
- **`andthen:review --mode security`** – security promoted from a sub-lens of `code` to a peer lens. New `plugin/skills/review/references/lens-security.md` owns the OWASP applicability gate (Web/API/LLM/Mobile/CI-CD checklists, loaded only when the surface matches), deep `trust-boundaries.md` data-flow analysis (one finding per source/sink pair where validation is missing or weak), Semgrep + dependency/secret/IaC scanner integration, and the always-on Red-Team sub-lens with attacker posture. New `security-review-calibration.md` pins severity to **exposure tier** (public / authenticated low-priv / admin / internal-VPN / build-CI-supply-chain) so the same code defect lands at different severity levels by where it sits – modifiers explicit in the calibration. Suffix `security-review`; mode token `security` recognized by the `andthen:remediate-findings` skill.
- **Mixed mode resolver gains `security`** – `mixed` now resolves to a subset of `{doc, code, security, gap}` and runs in that order. Security joins the chain when implementation is in scope **and** any auto-escalation trigger fires (auth, payments, network-exposed handlers, user input, secrets/crypto, LLM/agent flows, IaC/CI-CD/lockfile changes). For explicit `--mode mixed`, the trigger check still applies – security only joins when the surface warrants it, not "for completeness."
- **Security auto-escalation** in routing – when `--mode` is absent and the heuristic selects `code` or `mixed`, any auto-escalation trigger (auth, payments, network handlers, user input, secrets/crypto, LLM/agent flows, IaC/CI-CD/lockfile, native/cross-platform mobile surfaces – keychain/keystore, deep-link handlers, certificate pinning, biometric, in-app purchases) adds `security` to the resolved chain. Explicit `--mode code` (or any chain that explicitly omits `security`) is honored as-is; the code lens flags the missed coverage as a HIGH finding ("surface warrants security lens – consider `--mode code,security`") rather than silently broadening scope. `--mode mixed` is the one exception that opts back into trigger-based addition – mixed is a resolver, not a narrow lens, so applying the trigger inside the resolver matches its broad-audit semantics.
- **Council augments security** – `--council` now scopes to `code` and/or `security` (whichever applicable lens is in the run). In a chain with both, council runs once per lens with distinct reviewer rosters (security-mode councils always include Security Sentinel plus 1-3 surface specialists; reviewer-roster examples added for Web / API / LLM / supply-chain surfaces). Council append-fallback (when the chain includes neither code nor security) prefers `security` when the surface fires an auto-escalation trigger, otherwise `code`. A chain that explicitly includes `code` but not `security` on a security-trigger surface is honored – council runs on `code` only and the code lens emits the standard HIGH "surface warrants security lens" finding.

### Changed
- **`plugin/skills/review/references/lens-code.md` slimmed** – the 5-row OWASP routing table and Semgrep tooling hook moved out to `lens-security.md`; the code lens now runs a thin "Security awareness" pass that flags obvious smells (hardcoded secrets, raw SQL/shell concatenation, missing authn on new endpoints) without loading OWASP content. The `trust-boundaries.md` cross-reference stays in code mode (it covers logs, scraped content, agent I/O – broader than just security). Compliance-section line renamed from "Security best practices" to "Security awareness – defer to security lens for depth when applicable" so reports stop reading as security-flavored when the security lens did not run.
- **Mixed-mode verdict ladder unified** in `review-verdict.md` – three readiness vocabularies (doc 4-level, code/security 3-level, gap PASS/FAIL) merged into one precedence order with `Blocked` / `FAIL` / `Not Ready` at the top of the ladder and `Ready` / `PASS` at the bottom. Security findings that overlap with code findings (SQLi is both a correctness bug and an injection vuln) keep the security framing as canonical with a back-reference from the code section.

### Fixed
- **`hooks/configs/blocked-commands.json` shell-interpreter-escape regex tightened** – `\b(bash|sh|zsh|dash|ksh)\s+-c\s+["']` → `\b(bash|sh|zsh|dash|ksh)\s+-c\b`, dropping the trailing-quote requirement that let unquoted forms (`bash -c rm\ -rf\ /`) bypass the block. Word boundary preserved so `bash --check` and other non-`-c` flags still don't match.

---

## [0.15.7] – 2026-04-30

### Added
- **`andthen:review --output-dir <path>` flag** – explicit output directory override for the consolidated report file. Bypasses heuristic resolution; validated up-front (must exist and be writable, otherwise `BLOCKED:` in `AUTO_MODE`). Ignored when `--inline-findings` is set.
- **`andthen:ops update-tech-debt append` form** – appends deferred review findings to the project's Tech Debt Backlog (resolved from the **Project Document Index** `Tech Debt` row, default `docs/TECH-DEBT-BACKLOG.md`). Tagged `### Run: ... – tech-debt` blocks under `## High` / `## Medium` / `## Low` mirror `update-fis observations` semantics – 2-minute idempotent retry per severity, append-only, body-constraint check (`####`-or-deeper headings only). Severity routing parses each entry's `Severity:` line; mixed-severity bodies split into per-severity run blocks sharing one timestamp. The form is the *one* documented exception to the "ops never creates target files" rule – when the target file is missing, it is scaffolded from the new `# Technical Debt Backlog` template; the exception is called out explicitly in `ops/SKILL.md` GOTCHAS to keep the pattern from spreading to State, Plan, FIS, or any future target.
- **`andthen:remediate-findings` Phase 5 persistence** – two new steps. *Annotation* writes (or replaces in place) a `## Remediation Status` section at the end of the input review report listing each original finding with `RESOLVED` / `PARTIALLY RESOLVED` / `UNRESOLVED` / `DEFERRED` plus one-line evidence; whole-section replace anchors on the LAST column-0 `## Remediation Status` line not inside a fenced code block, so a code-fenced quote of the heading earlier in the report cannot be overwritten. *Tech-debt persistence* batches all `DEFERRED` entries into a single `update-tech-debt append` invocation; producer-side severity normalization maps upstream `CRITICAL → High`, `HIGH → High`, `MEDIUM → Medium`, `LOW → Low` (case-insensitive) before populating `Severity:` so deferred Critical findings don't silently demote to Medium via the consumer's default-Medium fallback, and missing or non-canonical severities (`P0`, `Blocker`) route to Medium with the raw input surfaced in the completion report. Annotation runs before tech-debt persistence; if annotation fails, tech-debt still writes and the failure surfaces in the completion report. Annotation skips cleanly when `REPORT_SOURCE` is a remote URL or non-writable input. The COMPLETION contract enumerates `Tech-debt entries written` (count + path + per-severity breakdown) and `Report annotation status` (`written` / `replaced` / `skipped: <reason>`) so `AUTO_MODE` consumers parsing the output can see both outcomes.
- **Tech Debt Backlog template** in `project-state-templates.md` – `# Technical Debt Backlog` + `## High` / `## Medium` / `## Low` in fixed order, each carrying `_No tech debt recorded yet._` placeholder. Reuses the FIS Implementation Observations placeholder pattern; placeholder is removed from a severity section on its first write.

### Changed
- **Unified review report location rules into a shared reference** – new canonical `plugin/references/review-report-location.md` is the single source of truth for review report filename and directory priority, consumed by both the `andthen:review` and `andthen:architecture` skills. Replaces five near-identical "Report Output Conventions" blocks previously duplicated across `andthen:review/SKILL.md` Step 4, `lens-code.md`, `lens-doc.md`, `lens-gap.md`, and `andthen:architecture/SKILL.md` Phase 4. Each lens contributes only its `<feature-name>` token and target nature (doc vs source-code); the canonical mode-suffix table stays in the review SKILL.md.
- **Source-code subdirectory guard** – review reports no longer fall back to "next to target" when the target is a source-code artifact, preventing reports from littering `src/`/`lib/`/`app/` etc. Doc/spec targets retain co-location. New tier inferring the **current feature directory** from `STATE.md` Active Stories sits between the spec-directory match and the `<agent-temp>/reviews/` fallback. With a single in-progress row the destination is `dirname(FIS)`; with multiple in-progress rows the tier fires only when exactly one row's `dirname(FIS)` is a directory ancestor of the review target (no name-overlap or fuzzy matching). The user-explicit `--output-dir` flag bypasses the guard for callers that genuinely want a source-code path.
- **Generalized spec-directory tier** – the location reference now recognizes any of: target lives inside a spec dir, target has an associated spec dir from the Project Document Index, or the requirements baseline path itself is a spec dir. Lifts the most-permissive variant (previously gap-only) into the shared rule so code reviews land in the same predictable place.
- **`--output-dir` rejection rules** – incompatible with `--inline-findings` (no file to apply the override to); validates path up-front (`BLOCKED:` in `AUTO_MODE`; in default mode the skill warns and falls through to the heuristic tiers, staying headless); applies to the single consolidated report in chains (most-restrictive target nature wins, so source-code wins whenever a chain includes `code` or `gap`); coexists with `--to-pr` (file writes to override path, then is posted as the PR comment).
- **Tier-2 substitution hook** – the asset documents that consuming skills MAY substitute tier 2's destination when "next to target" is wrong by construction (e.g. architecture's `advise` / `trade-off` modes write to the project's research/ADR location). Tier 1 still wins; tiers 3/4 still apply on miss.

---

## [0.15.6] – 2026-04-29

### Added
- **TDD/BDD canon tightened with named principles** – `tdd-discipline.md` adds Anti-Cheat Invariant, Horizontal Slicing as Anti-Pattern, and Living Test List (Beck); FIS scenario guidance names North/Keogh's Concrete over Abstract, Observable Boundary, and Declarative over Imperative.
- **Opt-in `--tdd` strict mode** on the `andthen:exec-spec` and `andthen:quick-implement` skills, with Requirement-Anchored traceability tiers (A/B/C).
- **Discovered Requirements append-only path** – new `update-fis <path> discovered-requirements <body>` form on the `andthen:ops` skill; FIS template documents the entry shape; data contract codifies FIS Mutability and Tier C as the sanctioned amendment channel during execution. New `### Run:` headers carry an `– observations` / `– discovered-requirements` tag so the two ops have separate idempotency lanes (untagged pre-existing blocks remain valid as content).
- **Citation Convention** codified in `CLAUDE.md` – cite the canonical author + work title, no inline URLs in shipped skill content, personal skill-collection repositories are not authoritative. Testing-skill attributions reattributed accordingly.

---

## [0.15.5] – 2026-04-28

### Changed
- **`andthen:prd` Executive Summary expanded into a human-review entry point** – the section in `prd-template.md` now layers three new subsections on top of the existing Problem/Vision/Users/Metrics bullets: `Capabilities at a Glance` (one line per FR with `FRn:` ID and name matching the canonical `#### FRn:` heading exactly, plus an inline priority tag that must agree with the canonical `**Priority**:` line – canonical wins on conflict), `Scope Highlights` (mirror canonical `## Scope` when ≤4 items per bucket; cherry-pick the most likely misread items when more), and `Key Constraints, Assumptions & Dependencies` (top 2–4 drawn from any of the three canonical buckets). Solves long-PRD scannability without a separate sidecar file – the summary lives in the same file as the canonical detail, so drift is structurally bounded.
- **`andthen:prd` skill wires the new contract** – Step 4 names the `Executive Summary` as the human-review entry point and points each new subsection at its canonical source. Step 5 self-check gains a concrete bullet-by-bullet trace ("each `Capabilities at a Glance` row → a `#### FRn:` block; each `Scope Highlights` row → an item in `## Scope`; each constraint/assumption/dependency row → its canonical bucket; missing canonical row = move down or delete"), replacing the earlier paper-rule shape with a procedure that matches the substance bar set by the bidirectional problem-solution-fit check above it.
- **`andthen:exec-spec` skill prompt cleanup** – Step 2 *Read and Prepare* rebuilt so the structural-integrity guard is its own substep with bullets for the three required conditions (replacing a nested numbered list that broke the outer ordering and silently implied an order between parallel checks). Executor Role compressed from a 9-bullet workflow recap into one role-framing paragraph plus the existing Do-not anti-pattern line; Step 5b.5 *Standalone use* points at the `andthen:ops` commands in substeps 5b.2/5b.3 instead of duplicating them. Trimmed leftover version-history (`0.14.x FIS without provenance`, "now live in"), the awkward "100% required" phrase, and the inconsistent `_`FIS_FILE_PATH`_` styling; fixed Step 2 item 12 sub-bullet indent (3→4 spaces) for CommonMark correctness under the two-digit marker.

---

## [0.15.4] – 2026-04-28

### Added
- **`--display-brand BRAND` flag on `scripts/install-skills.sh`** – white-label installs can now substitute the brand-cased token `AndThen` in installed `agents/openai.yaml` files (`display_name`, `short_description`, `default_prompt`). Default `AndThen` is a no-op so the default-install bundle stays byte-identical. Pairs with `--prefix` for full white-labeling (e.g. `--prefix dartclaw- --display-brand DartClaw`); the two flags are independent. Replacement is sed-escaped (`\`, `|`, `&`) so brand strings containing metacharacters render verbatim, and empty brands are rejected at arg-parse. Scope is narrowed to `agents/openai.yaml` to avoid silently rewriting incidental `AndThen` substrings in unrelated yaml.

---

## [0.15.3] – 2026-04-28

### Added
- **`--auto` flag on `andthen:refactor`** – the skill opts into the shared automation-mode contract so headless callers can drive it without conversational prompts. Phase 2's confirmation pause becomes a conservative auto-subset (deferred items recorded), Phase 1's no-arguments and red-baseline branches gain `AUTO_MODE` `BLOCKED:` behavior, and Phase 4 emits a deterministic `STATUS` / `FILES_CHANGED` / `VERIFY` / `DEFERRED` completion block.

### Changed
- **`andthen:spec` oversize handling softened from hard block to structured signal** – the Step 4.5 *Oversize Escalation* gate (which stopped, refused to save the FIS, and emitted `BLOCKED:` in `AUTO_MODE` when the draft exceeded size thresholds) is replaced by an always-on `OVERSIZE: {fis_path} – {N} lines, {T} tasks. Recommendation: …` line emitted as part of the artifact output in both interactive and `AUTO_MODE` (so headless callers do not lose the signal that the prior `BLOCKED:` carried). The drafted FIS always saves; recommendation routes by input shape – `/andthen:prd → /andthen:plan → /andthen:exec-plan` for standalone, upstream plan decomposition for plan-story. `andthen:plan` batch sub-agents echo the `OVERSIZE:` line back so the plan orchestrator's Step 3 size signal stays wired (the regeneration pass discards the oversized FIS). Canonical rule in `fis-authoring-guidelines.md` #6, plus its Self-Check size-check item and Confidence Check `<7 AND oversized` branch, all reworded to match the new save-and-signal contract.
- **Historical release notes removed from `plugin/README.md`** – the 0.13.0 / 0.14.0 *Breaking Changes* sections drift from CHANGELOG over time; the README now points at CHANGELOG as the single source of release history.

---

## [0.15.2] – 2026-04-27

### Added
- **`## Implementation Observations` section in FIS** – `andthen:exec-spec` now persists `NOTICED BUT NOT TOUCHING` items and AUTO_MODE `ASSUMPTION` records to a new bottom section in the FIS at completion (Step 5b.1) instead of losing them with the conversational completion report. Append-only with a UTC-stamped `### Run:` block per execution; `andthen:ops` gains an `update-fis <fis_path> observations <body>` form with body-content guardrails (`####`-or-deeper headings only; no nested `##` or `### Run:`) and idempotent retry under exec-spec's retry-once protocol. FIS template grows the new section with a placeholder; Step 2.11 working-notes bucket extended to track `ASSUMPTION` items so AUTO_MODE persistence is wired end-to-end; Core Rules and Step 5c surface the section as a brief pointer rather than duplicating the list.

### Fixed
- **`andthen:clarify` re-invocation amends prior clarification docs instead of refusing them** – previously a second invocation hit the agent's "already answerable from existing docs" guard and stopped, citing the prior clarification as authoritative. Step 1 now detects a prior doc under the derived feature slug (positive markers: `# Requirements Clarification:` H1 or `Decisions Log` table; negative guard: never `prd.md` or FIS, any filename) and switches to **amendment mode** – existing doc = baseline, INPUT = delta – with no new flag. Steps 2/3/4 each gain an in-line amendment-mode branch (delta-scoped questions, in-place section preservation, merged-doc validation); INSTRUCTIONS *Check before asking* and the matching GOTCHA name the amendment exception so the regression cannot re-route through them. `--issue` re-invocations against an existing `issue-{n}-*/` directory compose with amendment.

---

## [0.15.1] – 2026-04-27

### Added
- **`--claude-skills-dir` / `--claude-agents-dir` install flags** – override the previously-hardcoded `~/.claude/skills` and `~/.claude/agents` destinations independently. Either flag implies a Claude Code install (no separate `--claude-user` needed); pass both for a clean project-local install (the unset half otherwise lands at the user-level default – the installer warns about asymmetric paths but does not block). Unblocks downstream toolkits (e.g. DartClaw) bundling AndThen with their own `--prefix`. README gains a "Bundling AndThen into a downstream toolkit" snippet covering both user-tier and project-local patterns; Codex-side targets (`--skills-dir`, `--codex-agents-dir`) remain independent and still default to user-tier.
- **Goal-transformation prompts in `andthen:quick-implement`** – Phase 1.2 gains three task→verifiable-goal rewrites ("Fix the bug → write a failing test that reproduces it", etc.) so non-FIS quick fixes inherit the success-criteria discipline FIS scenarios provide. CLAUDE.md Skill Authoring Philosophy also gains a closing **Fitness check** working-signal line. Both inspired by a Karpathy-style coding-agent guidelines compilation (`forrestchang/andrej-karpathy-skills`).

### Changed
- **Boy Scout cleanup re-scoped to review/refactor modes** – CRITICAL RULES splits the prior combined rule into two named modes: **Surgical scope; surface – don't fix** (default for implementation skills, with explicit "every changed line traces to the spec/FIS or the issue under investigation" trace test) and **Boy Scout cleanup** (own role for `andthen:review`, `andthen:quick-review`, `andthen:refactor`, and `andthen:architecture`, *within the user's requested scope*). Implementation skills route spotted pre-existing issues through the existing Osmani-derived `NOTICED BUT NOT TOUCHING` channel for downstream review/refactor consumption rather than fixing inline; `exec-spec`, `remediate-findings`, the testing skill's `prove-it-pattern` and `tdd-discipline` references, and the `andthen:refactor` skill's anti-rationalization realigned. Central rule also adds a triage carveout for investigation-driven work, a gate-blocker exception for analyzer noise / blocking pre-existing issues, and a nested-call mode-precedence rule (called skill's mode wins for its run). Policy-split inspired by a Karpathy-style coding-agent guidelines compilation (`forrestchang/andrej-karpathy-skills`).
- **Coexistence warning narrowed to actual collisions** – the `--claude-user` plugin-coexistence warning now fires only when prefix is the default `andthen-` AND both the skills and agents paths target the user-tier defaults. Downstream toolkits using a distinct `--prefix`, or redirecting the Claude-side paths via `--claude-skills-dir` / `--claude-agents-dir`, no longer see a false-positive warning. Note: skill/slash-command scope is per-install-location, but `subagent_type` agent-name resolution is global within a Claude Code session, so a distinct `--prefix` is still the way to coexist on the agent side.
- **Skill-level duplicates promoted to `plugin/references/`** – the 6 files that lived as skill-level duplicates with `source:` frontmatter pointers (`adversarial-challenge`, `design-tree`, `farley-framework`, `review-calibration`, `trust-boundaries`, `project-state-templates`) are now canonical shared references, growing the inlined-canonical list from 8 to 14. The two-tier asset model collapses into one tier with explicit forks as the divergence escape hatch; `review-calibration.md` was slimmed to drop review-specific orchestration already restated in `review/SKILL.md` and the lens references. CLAUDE.md asset-ownership section rewritten; `install-skills.sh` extended with the 6 new canonicals and 6 new consuming skills.

### Fixed
- **Dead `lens-adversarial.md` dependency removed from `architecture` skill install payload** – `_skill_assets_architecture` registered `lens-adversarial.md` since 0.15.0, but no architecture-skill prompt ever loaded it; the file was inlined into every architecture install as dead bytes. Removed from `install-skills.sh` and the corresponding row in CLAUDE.md's Shared Plugin Assets table.

---

## [0.15.0] – 2026-04-27

### Added
- **Red-Team Lens as an always-on sub-lens of `andthen:review`** – every code, doc, and gap review now runs a primary adversarial finding pass (`plugin/references/lens-adversarial.md` + `plugin/references/red-team-calibration.md`) that attacks assumptions, unhappy paths, hidden coupling, guessed behavior, and incomplete wiring before severity is assigned and any filter pass runs. Closes the leniency drift the source Anthropic harness research flagged: peer-reviewer calibration without an adversarial primary stance lets evaluators rationalize approvals. The gap lens's existing Behavioral Dry-Run is folded under the same sub-lens so the pattern is uniform across all three lenses. `andthen:quick-review` and the `andthen:architecture` review pipeline source the same canonical rubric instead of inlining a duplicate.
- **Red-Team Reviewer council role** – `andthen:review --council` always includes a Red-Team Reviewer specialist alongside Devil's Advocate and Synthesis Challenger. The find/filter/synthesize spine sits at the top of `reviewer-roster.md` as Always Include; selection examples now span the documented 5–7 range (Infrastructure/config dropped to 5 to demonstrate the smaller end). Council Gotchas reflect the new floor: 3 fixed roles + 2–4 scope-relevant specialists.
- **`--mode` chains in `andthen:review`** – `--mode` accepts a comma-separated list (e.g. `--mode doc,code,gap`) that runs lenses in declared order with shared target map and findings, producing one combined report. `mixed` is no longer a fixed doc+code chain; it auto-resolves to whichever subset of {code, doc, gap} the inputs warrant. The chain rules apply identically to file and inline output; the canonical mode token (`mixed`) stays parseable while a separate `Resolved chain:` line shows the actual lenses that ran.

### Changed
- **Shared `automation-mode.md` reference** – the headless-first / `--auto` strict-mode / propagation paragraph that was restated in five SKILL.md files (`prd`, `plan`, `spec`, `exec-spec`, `exec-plan`) now lives in a single canonical reference (`exec-plan/references/automation-mode.md`) duplicated to the other four per the self-contained-skills policy. Each SKILL.md keeps only its skill-specific `BLOCKED:` triggers inline. The 14 per-call-site `(append --auto when AUTO_MODE=true)` reminders are removed – propagation is now one universal rule readers apply themselves. CLAUDE.md asset-ownership table updated.
- **`andthen:plan` PRD-proxy mechanics trimmed** – the technical-research extraction still produces a "Binding PRD Constraints" list (verbatim text + heading anchor for each entry), and that list is still the authoritative binding-constraint set for batch sub-agents. Removed: the anchor-fallback-policy paragraph (coarsen-to-enclosing-heading rules) and the "do not read prd.md directly" prohibition. Sub-agents may consult `prd.md` for context; the binding constraint set remains fixed by the extraction. Reverse-coverage batch-mode resolution still works against the same extraction.
- **`andthen:plan` template Execution Guide rewritten** – previously instructed readers to invoke `/andthen:spec` per story, but `andthen:plan` already batch-generates all FIS upstream (1:1 story↔FIS invariant). Now points at `/andthen:exec-plan` (whole bundle) or `/andthen:exec-spec` (per story) as the actual execution paths.
- **FIS size threshold consolidated** – the 200-500 sweet spot / >700 lines / >18 tasks rule had four restatements across `fis-authoring-guidelines.md` (#6 + Self-Check), `spec/SKILL.md` gotcha, and `fis-template.md`. #6 is now the canonical statement; the three echoes defer to it.
- **`andthen:review` routing heuristics consolidated** – the 9-bullet absent-`--mode` block had three overlapping rules ("does X match Y?", "implementation of [doc]", "clear baseline + impl + fit question") routing similar phrasings to two different lenses. Now five mutually exclusive, first-match-wins rules; any "compare implementation against a requirements baseline" intent (including "review implementation of [doc]") routes to **mixed** instead of `gap` alone, so the default delivers gap + code (plus doc when the baseline is itself in flight). Strict gap-only is still reachable via explicit `--mode gap`.
- **"Adversarial Challenge" renamed to "Findings Filter"** across `andthen:review` (lens-doc, lens-gap, council-mode, `adversarial-challenge.md`), `andthen:quick-review`, and the `andthen:architecture` review pipeline – the old name suggested adversarial primary stance but the prompt forbade new findings (`Do NOT add new findings – your job is to filter, not expand`), making it a filter-only role. The new name matches actual behavior. Two new plugin-level shared assets (`lens-adversarial.md`, `red-team-calibration.md`) bring the canonical-asset list from 6 to 8; `review`, `quick-review`, and `architecture` are registered consumers in `install-skills.sh` so the rubric is inlined into each at install time.
- **`argument-hint` frontmatter standardized across all 18 user-invocable skills** – `argument-hint` now leads with control flags and ends with positional input (and adjacent input-alternative flags like `--issue`, `--path`). Every VARIABLES block gains a uniform strip-tokens parenthetical naming each skill's actual flags so leading and trailing flags are handled the same way. `e2e-test` and `ops` gained hints they were missing.
- **`andthen:quick-review` read-only contract tightened** – without `--fix` on the current invocation, the skill is now strictly read-only. An in-conversation reply ("looks good", "ok", "sure") never unlocks editing – only a re-invocation with `--fix` does. Named failure modes ("starting with the easy ones" inline, pre-emptive patching of "obvious" fixes) are explicit Gotchas.

### Removed
- **`andthen:spec` Oversize Pivot mode** – the Step 4.5 mechanism that turned the spec skill into a mini-plan generator (creating `plan.md` + child FIS files when a draft exceeded size thresholds) was inconsistent with the rest of the system: it produced fully-specced plan bundles **without** a PRD, while `andthen:plan` itself fails fast without one. Replaced with a redirect to the `/andthen:prd → /andthen:plan → /andthen:exec-plan` chain so all plan bundles come from a PRD. The plan-story-input branch (escalate to upstream plan decomposition) is unchanged. The unused `plugin/skills/spec/templates/plan-template.md` duplicate is deleted.

### Fixed
- **`scripts/install-skills.sh` path rewriter is now location-aware** – previously rewrote `${CLAUDE_PLUGIN_ROOT}/references/<asset>` uniformly to `references/<asset>`, which was ambiguous from inside `<skill>/references/<file>.md` (file-relative semantics would resolve to `references/references/<asset>`). Now branches on the consumer file's dirname: skill-root files keep `references/<asset>` (skill-root-relative); files inside `*/references/` get bare filename (sibling-relative). `teardown-worktrees.sh` also gains three safety guards before destructive ops.

---

## [0.14.4] – 2026-04-26

### Fixed
- **Status writes no longer dropped under `andthen:exec-plan --team --worktree`** – previously each implementer wrote `plan.md` / `State` document status from inside its own worktree, which collided on every concurrent wave merge (table-row conflicts the merge-conflict taxonomy could not resolve). The `andthen:exec-spec` skill gains a `--defer-shared-writes` flag – set automatically by `andthen:exec-plan --team --worktree` – that skips direct `plan.md` and `State` document writes and emits a `## Deferred Shared Writes (worktree mode)` audit block in the completion report instead (Story / Plan / FIS / Completion summary fields). The orchestrator constructs the actual `andthen:ops update-*` invocations from values it already knows (`STORY_ID`, `FIS_FILE_PATH`, `PLAN_FILE_PATH`) plus the completion summary, and applies them post-merge – on `BASE_BRANCH` in single-repo, in `PLAN_DIR` in multi-repo (`PLAN_DIR ≠ CODE_DIR`). The audit block is summary source, not a parsed script; a missing block is recoverable, not Stop-the-Line. FIS writes still happen in-worktree (story-local, merges cleanly). Implementers are explicitly forbidden from staging or committing `plan.md` / `State` document inside the worktree branch (shadow commits would defeat the deferral). `andthen:exec-plan` Step 2 now fails fast when `--worktree` is set without `--team` (worktree isolation is a team-mode feature). `andthen:exec-spec --defer-shared-writes` standalone is documented as user-applies-manually.
- **`andthen:exec-spec` Step 5b made prescriptive** – the dense single-paragraph status-write instruction is now five numbered substeps (FIS / Plan / State / Verify / Deferred shared writes) listing exact `andthen:ops update-*` invocations, so end-of-context "summarize and exit" no longer skips any of the four required writes.
- **`andthen:exec-plan` worktree cleanup made concrete** – the per-merge `Clean up worktree and branch` step (Step 3T Merge Wave step 5) and the post-phases sentence previously hand-waved cleanup with a `git worktree prune` reference that only purges admin records. Per-merge cleanup now spells out `git worktree remove` + `git branch -D story-{task_id}` with porcelain-driven path resolution and a clean-status sanity check, since the implementer's session-scoped `ExitWorktree(keep)` cannot be reversed cross-session by the orchestrator. Post-phases adds a five-step **Final Worktree Teardown** (inventory `story-*`, classify merged vs unmerged via `merge-base --is-ancestor`, remove only merged ones – preserving unmerged work as the only artifact, then prune + verify); FAILURE HANDLING now mandates the same teardown on failure exits, ending the cross-run leftover accumulation.

### Changed
- **`andthen:exec-plan` Writes-Landed Checklist** – Step 3c's one-line "re-read plan.md and FIS to confirm" is replaced with a structured per-story checklist (FIS task/Final Validation/success criteria, plan story row, plan story section, `State` Active Stories) the orchestrator must tick before advancing; Step 3T references the same checklist with mode-conditional source-of-truth notes. Wave N+1 worktree creation is also gated on orchestrator-applied writes (deferred shared writes, repair writes, phase transitions) being committed to `BASE_BRANCH`, not just on Wave N merges completing.
- **`andthen:exec-plan` Merge Wave switched from `--no-ff` to `--squash`** – each story now lands on `BASE_BRANCH` as a single commit with a load-bearing `Squashed-story: {STORY_ID}` trailer, giving one-commit-per-story history, trivial story-level revert, and a `git log --grep` index. Final Worktree Teardown's classifier becomes layered: trailer-match (primary, squash-aware) with `merge-base --is-ancestor` retained as a fallback for legacy `--no-ff` leftovers. Trade-off: implementer's intermediate commits are not preserved on `BASE_BRANCH`; the FIS, squash commit message, and deferred-writes completion summary are the forensic record.
- **`andthen:quick-review` gains `commit <sha>` FOCUS form** – when `FOCUS` matches `[story <id> ]commit <sha>` (literal `commit` token followed by a 7+ char hex SHA), the Determine Scope step (priority 1) sets the change set to `git show <sha>` and skips the empty-`git diff` fallback path. This is the load-bearing primitive that lets `andthen:exec-plan`'s team-mode reviewer (under squash-merge) actually review the squash commit; without it, the reviewer would fall through to an empty `git diff` and silently return green. The orchestrator's reviewer prompt resolves the SHA via the trailer-grep (worktree mode) or `git rev-parse HEAD` (no-worktree mode) and passes both `<story-id>` and `<hex-sha>` as literal substitutions in the slash-command line.


---

## [0.14.3] – 2026-04-24

### Added
- **`--claude-user` in `scripts/install-skills.sh`** – opt-in alternative install path that writes skills to `~/.claude/skills/andthen-*/` and agents to `~/.claude/agents/andthen-*.md` with `/andthen-<name>` slash-command invocation, giving naming parity with Codex for users who want one convention across both runtimes instead of the Claude Code plugin's `andthen:<name>` form. Warns when the `andthen` plugin is already installed, prefixes agent frontmatter `name:` so Task-tool resolution works, and fails loudly on malformed agent sources rather than silently installing a broken file.

### Changed
- **FIS cross-document reference precision** – Template gains `Required Context` (load-bearing spans inlined verbatim, source-pinned with `<!-- source: path#anchor -->` and `<!-- extracted: ... -->`) and `Deeper Context` (anchored pointers), replacing the old undifferentiated `Documentation & References` table for doc-type refs and forcing authoring-time resolution instead of vague "see plan.md" punts. Plan-batch per-story sub-agents inherit pre-validated PRD anchors via a curated "PRD proxy" in technical research; FIS size envelope raised to 200–500 lines (oversize >700) to accommodate inlining.
- **Doc-review routes to `andthen:clarify` vs `andthen:remediate-findings`** – The `andthen:review` skill in `--mode doc` (and the doc sub-pass of `--mode mixed`) now classifies findings into a requirement-gap cluster (→ the `andthen:clarify` skill) or a defect cluster (→ the `andthen:remediate-findings` skill) via an explicit document-maturity signal and first-fires-wins pattern precedence, recording the routing decision in a new `Recommended Next Action` report section. Under `AUTO_MODE=off` the skill offers to invoke the `andthen:clarify` skill inline against the listed gaps; under `AUTO_MODE=on` the recommendation is report-only – the `andthen:clarify` skill is interactive by nature and never runs headless.
- **`andthen:clarify` requirement-vs-implementation boundary made effect-based** – the boundary now passes the **load-bearing test** (does the answer change user-visible behavior, scope, or acceptance criteria?) instead of a categorical "technical = downstream" rule, letting questions like offline support, sync semantics, user-visible auth model, data residency, and externally-visible provider choice into scope while still deferring library/caching/internal-API/DB/deployment choices to the `andthen:spec` skill and the `andthen:architecture` skill (`--mode trade-off`). Scope guard and the `design-tree.md` "In `clarify`" bullet now defer to one canonical example list to prevent drift, and the non-developer-stakeholder litmus is repositioned as a tiebreaker qualified to "the answer itself, not a downstream consequence".
- **Boy Scout in touch radius enforced across exec/review/remediate** – the `andthen:exec-spec` skill gains a Core Rule and a 4a lint/types gate requiring pre-existing violations inside `changed-files` to be fixed or deferred with a one-line reason, ending the bare "did not touch pre-existing errors" disclaimer. The `andthen:review` (`lens-code`) and `andthen:quick-review` skills now treat that disclaimer as a finding when the issue sits *inside the changed files* (default MEDIUM, HIGH for correctness/security); issues in unchanged files remain out of scope. The `andthen:remediate-findings` scope-creep rule is clarified to permit Boy Scout cleanup within files already being edited while still forbidding expansion into untouched files.

### Fixed
- **`excalidraw-diagram` portable export and text clipping** – saved `.excalidraw` files previously kept the `label:` shorthand and undersized standalone text widths, producing empty shapes and clipped titles when opened in `app.excalidraw.com`. Phase 3.6 promoted to mandatory Phase 5 step; render template now measures standalone text via Canvas `measureText` with the actual Excalidraw font and patches width/height during `getConvertedJSON`. Author no longer needs to hand-size text elements.


---


## [0.14.2] – 2026-04-24

### Added
- **`--auto` for core pipeline and supporting skills** – `prd`, `plan`, `spec`, `exec-spec`, `exec-plan`, `review`, `quick-review`, `remediate-findings`, `architecture`, `ui-ux-design`, and `triage` now expose an automation-safe mode for external orchestrators. In this mode skills avoid conversational prompts and arrow-prompts, make conservative assumptions, record deferred decisions in artifacts or summaries, propagate `--auto` to nested `andthen:*` skill calls that accept it (`ops` is exempt – deterministic), and stop with `BLOCKED:` only on contract failures or unsafe actions.


---


## [0.14.1] – 2026-04-24

### Added
- **DDD reference in `andthen:architecture`** – new `references/ddd.md` covering strategic (subdomains, bounded contexts, 9-pattern context map, team topology) and tactical DDD (aggregate rules, entities/VOs, domain vs integration events, application vs domain service, factories, repositories), plus Hexagonal/CQRS/Event Sourcing, Event Storming, Bounded Context Canvas, Functional DDD, and three new anti-patterns (False Invariant Aggregates, Leaky Integration Events, Model-Code Gap). Lazy-loaded from `advise` and `decompose` modes.
- **Ousterhout module-design lens in `andthen:architecture`** – new `references/ousterhout-modules.md` covering deep vs shallow modules, information leakage, pass-through methods, pull-complexity-downward, define-errors-out-of-existence, temporal decomposition, and an 8-test review checklist. Opt-in Step 6 in `mode-review.md` at Component/Code scope only.
- **Three Ousterhout-derived anti-patterns** in `architecture/references/anti-patterns.md` – **Shallow Module**, **Pass-Through Method / Layer**, and **Temporal Decomposition**, each with symptoms, fix, review question, and false-positive boundary. Existing **Leaky Abstraction** extended to cover shape-level information leakage.
- **Composition Playbook for `andthen:excalidraw-diagram`** – new `references/composition-playbook.md` with five archetype recipes (Pipeline, Architecture, Taxonomy, Lifecycle, Comparison) keyed to concrete XY positions, zone plans, size cascades, and anti-checks.
- **`window.lintLayout()` in the Excalidraw render template** – automated layout linter returning CRITICAL/MAJOR/MINOR findings (overlaps, text-over-shape, uniform grids, font < 14, tight spacing, missing hero, off-grid coords, missing primary-flow arrow). Integrated into the render loop and re-checked after each fix.
- **AndThen skills overview diagram** – `docs/diagrams/andthen-skills-overview.excalidraw` plus rendered PNG.

### Changed
- **`architecture` advise-mode DDD section trimmed** – `mode-advise.md` DDD block replaced by a building-blocks quick-reference table + assessment questions with a pointer to `ddd.md`. Added **Application Service** row and fixed prior conflation of domain events with integration events.
- **`architecture` decompose-mode context-map catalog expanded** – `decomposition.md` context-mapping table: 6 → 9 patterns (**Partnership**, **Separate Ways**, **Big Ball of Mud**), added **Team relationship** column and selection-trigger guidance. Pattern/coupling/team-relationship columns kept byte-synced with `ddd.md`.
- **`andthen:review` council mode extracted** – the ~140 lines of council orchestration moved from `SKILL.md` into a new `references/council-mode.md` (lazy-loaded on `--council`). `SKILL.md` 325 → 185 lines; non-council reviews no longer load council content. Auto-escalation triggers kept in `SKILL.md` so the load decision doesn't require reading the reference first.
- **`andthen:review` gap-lens Step 5 behavioral dry-run walkthrough** – replaces the one-line "Optional Retrospective" stub. Five mandatory passes per requirement: trace execution, check pre/post/invariants, stress unhappy paths, test assumptions, sanity-check the design. Findings merge into Step 4 categories – Step 6 adversarial challenge and scoring unchanged.
- **`andthen:review` gap-lens Step 4 Gap Analysis restored** – reverses the v0.10.0 compression that reduced each of the seven gap categories to a single word. Each category now carries one concrete sentence with examples. PASS/FAIL verdict table untouched (downstream contract preserved).
- **Mandatory Layout Contract in `andthen:excalidraw-diagram` Phase 1.5** – 10-line pre-JSON commitment covering narrative, archetype, axis, hero, size cascade, shape vocabulary, zone plan, canvas size, evidence artifacts, and rhythm breakers. Named as the primary fix for uniform-grid AI-generic output.
- **Excalidraw render loop hardened** – dropped the `esm.sh?bundle` query (silent font-ID bug), switched to a 60s bash polling loop on `window.__moduleReady` (`wait --fn` timeout is not honoured empirically), and replaced manual viewport sizing with `AGENT_BROWSER_FULL=true` full-page screenshots.
- **`style-guide.md` gains Size Cascade, Anti-Uniformity, Signal Badges, and Density Gradient sections** – authoritative `hero : primary : secondary ≈ 3 : 1.8 : 1` numbers, ban on 6+ shapes sharing `(type, width, height, color)`, pill-badge spec, and three-band density layout for XL/XXL canvases.
- **`element-format.md` gains Label Auto-Sizing math and Text Metrics table** – per-shape minimum-width formulas (ellipse ≈ 1.4× rectangle, diamond ≈ 2×), `BOUND_TEXT_PADDING = 8px`, per-font character-width estimates at fontSize 16/18/24, and 20px grid-snap rule.
- **`andthen:clarify` recommend-don't-decide loop** – Step 2 requires a best-guess answer with rationale per question, probing on load-bearing answers, and treats unaddressed recommendations as unanswered. New gotchas for "treating recommendation as confirmed" and "asking things already answerable from the codebase".
- **`andthen:spec` research steps tightened** – Codebase research uses direct `rg`/`tree`/file reads; new **Solution architecture** step invokes `andthen:architecture --mode advise` in a sub-agent and is recommended for most code changes; architecture trade-offs reframed as optional unless 1–3 genuinely competing approaches exist.
- **Breaking-changes docs consolidated in `plugin/README.md`** – root `README.md` now carries a one-line pointer; the detailed 0.13.0 migration tables moved to a new **Breaking Changes** section in `plugin/README.md`, extended with a 0.14.0 entry for the 1:1 story↔FIS invariant.

### Removed
- **Sub-agent capability hedges across 12 skills** – stripped `_(if supported)_` / `_(if supported by your coding agent)_` qualifiers from `exec-plan`, `exec-spec`, `map-codebase`, `plan`, `prd`, `quick-implement`, `refactor`, `spec`, `triage`, `ubiquitous-language`, `ui-ux-design` (+ `mode-design-system`, `mode-wireframes`), and `architecture/mode-trade-off`. Sub-agents are now assumed available; `general-purpose` is the portable fallback.


---

## [0.14.0] – 2026-04-21

### Changed
- **1:1 story↔FIS invariant in `andthen:plan`** – removed THIN and COMPOSITE classification tiers; every story now maps to exactly one FIS file and no two stories share a FIS path. Step 3 Story Breakdown gained a **Consolidation Pass** that merges stories at breakdown time when they share an implementation surface, form a tight dependency chain (where the downstream story has no independent demo value), or would both produce trivially small FIS with a shared primary concern. Rationale: the plan↔FIS join is a single-column contract; keeping it unique-key eliminates a recurring class of consistency bugs ("stories not corresponding to FIS files") and lets downstream skills drop their shared-spec branching logic. Files updated: `plan/SKILL.md` (Step 6 collapsed from three sub-sections to one, composite/thin paths removed from Orchestrator Role, GOTCHAS, OUTPUT tree, Spec Flow Example, and COMPLETION summary), `plan/templates/plan-template.md` (composite-sharing example replaced; new 1:1 invariant callout).
- **`andthen:exec-plan` simplified** – deleted the Shared-FIS Dedup mechanism in both solo mode (Step 3b) and team mode (Task Management). `impl-*` / `review-*` task naming dropped the composite form; each story now gets its own exec-spec + quick-review run. Removed the "re-executing a composite FIS already implemented" gotcha.
- **`andthen:exec-spec` simplified** – `STORY_IDS` (list) collapsed to `STORY_ID` (single) for plan-backed specs. Dropped the composite-vs-single branches in Step 2 project-state setup and Step 5b completion updates.
- **`andthen:spec` oversize-pivot disclaimers removed** – the "do not run THIN/COMPOSITE/shared-FIS classification" caveats are no longer needed since that classification no longer exists. Oversize pivot mode remains unchanged (straightforward one-story-per-FIS decomposition).
- **FIS size thresholds raised** – sweet spot `100-300` → `150-450` lines; oversize pivot trigger `>400 lines or >12 tasks` → `>600 lines or >18 tasks`. Rationale: consolidated stories (from the plan's Consolidation Pass) legitimately land where the old thresholds triggered pivots. Updated in `spec/SKILL.md:40,109`, all three copies of `fis-authoring-guidelines.md` (canonical in `spec`, dupes in `plan` and `review`), and both copies of `fis-template.md` (canonical in `spec`, dupe in `plan`).
- **`init/templates/CLAUDE.template.md` Project Document Index** – removed `composite s0N-s0M-*.md` and `thin-specs.md` from the spec directory description; the pattern is now just `s01-*.md`, `s02-*.md`, …


---

## [0.13.2] – 2026-04-20

### Fixed
- **Deprecated Excalidraw font IDs in `andthen:excalidraw-diagram`** – `style-guide.md` and `element-format.md` instructed the agent to emit `fontFamily: 1` (Virgil), `2` (Helvetica), and `3` (Cascadia) on text and labeled-shape elements. All three are flagged `deprecated: true` in Excalidraw's `packages/common/src/font-metadata.ts` and persist a deprecated-font marker into generated scenes. Updated both references to the current non-deprecated IDs: `5` (Excalifont – hand-drawn default), `6` (Nunito – clean sans-serif), `8` (Comic Shanns – the only non-deprecated ID that `getGenericFontFamilyFallback` routes to the monospace CSS fallback). Added a new Font Family IDs table to `element-format.md` and an explicit "do not use 1/2/3" callout to `style-guide.md`. Updated all prose mentions of "Virgil/Helvetica/Cascadia" and the three aesthetic preset tables (Hand-drawn Blueprint, Warm Industrial, Clean Technical) accordingly.
- **Phantom preset name in the Complete Example caption** (`element-format.md:194`) – the caption called the bronze-hachure + warm-parchment example "the default 'Schematic Warmth' style", but `style-guide.md` defines only three presets (Hand-drawn Blueprint, Warm Industrial, Clean Technical) and the actual default is Hand-drawn Blueprint (pastel palette, white canvas). Rewrote the caption to correctly identify the example as a **Warm Industrial** illustration and point readers to `style-guide.md` for the default palette. JSON unchanged – it's a valid bronze-zone + green-accent example on the warm-parchment preset.


---

## [0.13.1] – 2026-04-20

### Fixed
- **Agent/skill confusion around `andthen:quick-review`** – the skill's own description led with "fresh-context sub-agent" and the `andthen:remediate-findings` call site sat next to "heavyweight re-review sub-agents", which primed callers (especially when `remediate-findings` itself ran inside a sub-agent) to pass `andthen:quick-review` as `subagent_type` to the Task tool and fail with "Agent type not found". Reframed the skill description and opening, added an explicit "this is a skill, not an agent type – do not pass as `subagent_type`" guardrail, and rewrote the `remediate-findings` step-4 invocation to mirror the defensive pattern already used in `exec-spec/SKILL.md:135,138`.

### Changed
- **Testing discipline tightened in verification gates** – `andthen:exec-spec` Step 4a gains a new "Tautology check" (the unit under test must be imported and called without being replaced by a mock; assertions must reference its return value or an observable effect, not mock call arguments; fixtures must not substitute for the production computation). The code-review checklist replaces the generic "Mock/stub usage appropriate" item with two sharper checks: mocks/stubs confined to system edges, and each test would fail if the asserted production behavior were removed.
- **Removed changelog framing from prompt artifacts** – per the "no historical-change notes in skill prompts, references, or templates" principle, dropped the `Replaces/evolves the narrower "implementation-notes.md" concept.` tail from the LEARNINGS.md blockquote in both `init/templates/project-state-templates.md` and `map-codebase/templates/project-state-templates.md`, and removed the "replaces the heavyweight re-review sub-agents" comparative from `remediate-findings/SKILL.md:93`.


---

## [0.13.0] – 2026-04-20

### Added
- **`andthen:architecture` skill** (`plugin/skills/architecture/`) – renamed from `architecture-review` and expanded into a five-mode skill: `review`, `decompose`, `advise` (absorbs the former `solution-architect` agent's CUPID/DDD/ADR methodology), `fitness`, and `trade-off` (absorbs the former `andthen:trade-off` skill). Each mode's body lives in `plugin/skills/architecture/references/mode-<mode>.md`; `SKILL.md` is a thin router.
- **`andthen:ui-ux-design` skill** (`plugin/skills/ui-ux-design/`) – new skill that merges the former `design-system` skill, `wireframes` skill, and `ui-ux-designer` agent into one four-mode skill: `research`, `design-system`, `wireframes`, `review`. Per-mode bodies in `plugin/skills/ui-ux-design/references/mode-<mode>.md`. Named `ui-ux-design` (activity) rather than `ui-ux-designer` (persona) to reinforce the skill-is-activity / agent-is-persona convention.
- **`andthen:testing` skill** (`plugin/skills/testing/`) – new skill that replaces the former `qa-test-engineer` agent and adds test-first discipline as first-class craft. Modes: `strategy`, `write` (default), `tdd`, `prove-it`. `SKILL.md` is a thin router; authoritative material lives in four references drawing on Kent Beck, Dave Farley, Addy Osmani, Michael Feathers, Kent C. Dodds, and Matt Pocock:
  - `references/tdd-discipline.md` – Red/Green/Refactor, triangulation, anti-rationalization table, when NOT to TDD.
  - `references/prove-it-pattern.md` – failing-test-first for bugfixes, characterization tests for legacy code, Beyonce Rule.
  - `references/test-design.md` – behavior-over-implementation, diagnosability, mock minimization, property-based and contract testing.
  - `references/levels-and-strategy.md` – unit/integration/E2E trust-boundary criteria, Testing Trophy, coverage prioritization matrix.
  - `references/farley-framework.md` – duplicate of the `architecture` skill's Farley framework (activity-local anchor for testability-as-modularity).
  Callers (`exec-spec`, `triage`, `e2e-test`) invoke it directly as `/andthen:testing`; runs in the caller's context by default (useful for `tdd`/`prove-it` continuity), with optional `general-purpose` sub-agent wrapping for fresh-context isolation.
- **Codex agent generator** (`scripts/generate-codex-agents.sh`) – generates `andthen-*.toml` files from `plugin/agents/*.md` into the user's Codex agents directory (`~/.codex/agents` by default) at install time, so Claude Code agent files are the single source of truth. Invoked automatically by `scripts/install-skills.sh` (use `--no-codex-agents` to skip).
- **`andthen:prd` skill** (`plugin/skills/prd/`) – extracts PRD creation from `plan`. Produces `prd.md` from clarified requirements, draft PRDs, raw description, a file, a URL, or a GitHub issue. Pass-through when a `prd.md` already exists in the target directory. Output-path semantics match the `andthen:plan` input contract so the `prd → plan` chain is stable.
- **Unified verdict reference** (`plugin/skills/review/references/review-verdict.md`) – normalised severity scale (`CRITICAL` / `HIGH` / `MEDIUM` / `LOW`) and per-mode readiness/verdict definitions for the `andthen:review` modes (including `--council`). Gap-mode PASS/FAIL contract preserved byte-for-byte.
- **Lens references for `andthen:review`** (`plugin/skills/review/references/lens-code.md`, `lens-doc.md`, `lens-gap.md`) – self-contained rubrics loaded per mode; `andthen:review` now runs each lens inline instead of delegating.
- **`--fix` flag on `andthen:review` and `andthen:quick-review`** – optional auto-remediation after the review runs. `review --fix` delegates to the `andthen:remediate-findings` skill with the consolidated report path (incompatible with `--inline-findings`; with `--to-pr`, the PR comment is posted first so the comment reflects the original findings). `quick-review --fix` applies the accepted findings inline after the Accept/Dismiss step – dismissed findings stay dismissed. Single flag, no severity levels: `remediate-findings` owns fix scoping.

### Changed (breaking)
- **`andthen:plan` requires `prd.md` input and produces the full plan bundle in one run** (`plugin/skills/plan/`) – `plan` now expects a directory containing `prd.md` and produces `plan.md` + batch-generated FIS for every story + shared `.technical-research.md` + cross-cutting review. Absorbs the work the removed `spec-plan` skill used to do. Adds `--skip-specs` for a cheap planning pass. Resume contract preserved: re-running on a partially-specced directory only fills missing FIS.
- **`andthen:exec-plan` no longer generates specs** (`plugin/skills/exec-plan/`) – requires a fully-specced plan bundle. Fails fast and redirects to `andthen:plan` if any story's `**FIS**` field is `–` or points at a non-existent file. Removed the per-phase `spec-plan` step.
- **`andthen:review` absorbs `review-code`, `review-doc`, `review-gap`, and `review-council` as internal modes** (`plugin/skills/review/`) – one user-facing review skill. Code, doc, and gap lenses run inline using `plugin/skills/review/references/lens-*.md`. Multi-perspective adversarial review (5-7 reviewers + two-phase challenge) runs via `--council`, auto-escalating for high-risk scope or when the user asks for multi-perspective/adversarial review. `--team` still forces Agent Teams mode. Reviewer roster moved to `plugin/skills/review/references/reviewer-roster.md`.
- **`andthen:review` flag renames**: `--code-only` / `--doc-only` / `--gap-only` → `--mode code|doc|gap|mixed`. Council mode invoked via `--council` (replaces the former peer `andthen:review-council` skill). Auto-detection behavior unchanged when `--mode` is absent.
- **Unified severity scale across review modes** – `SUGGESTIONS` bucket normalised to `LOW`; `MEDIUM` added to the code lens. Old reports remain readable via the mapping in `plugin/skills/review/references/review-verdict.md`.
- **Skills are fully self-contained** – `plugin/references/`, `plugin/scripts/`, and the repo-root `templates/` directory retired. Each skill owns its `references/`, `templates/`, and `scripts/` locally; skill files never cross skill boundaries (no `../<other-skill>/...` paths, no `${CLAUDE_PLUGIN_ROOT}` references). Short refs inlined into consumer SKILL.md; larger refs, templates, and scripts duplicated into each consuming skill. Markdown duplicates carry a YAML `source:` frontmatter pointer to the canonical owner; script duplicates track ownership via the table in CLAUDE.md. The former repo-root starter templates (`CLAUDE.template.md`, `project-state-templates.md`) now live canonically under `plugin/skills/init/templates/`, with `map-codebase` carrying a duplicate of `project-state-templates.md`. Skills are now droppable into any Claude Code tier (plugin/user/project) or Codex export without path rewriting.
- **`install-skills.sh` simplified** – removed all path rewriting (~100 lines). Only namespace transforms remain (`andthen:` → `andthen-` and `/andthen:` → `$andthen-`). No top-level `andthen-scripts` or `andthen-templates` sibling dirs are installed.
- **`fis-authoring-guidelines.md` trimmed** – removed exec-time guidance that belongs in `andthen:exec-spec`, compressed the Execution Contract section and the Self-Check bullets, and kept one weak/strong `Verify:` pair instead of several. Canonical lives in `plugin/skills/spec/references/`; duplicated into `plan/` and `review/` with `source:` frontmatter.
- **Checklists and calibration files moved** (`plugin/skills/review/checklists/`, `plugin/skills/review/references/`) – merged the assets from the deleted `review-code`, `review-doc`, and `review-council` skills into the unified `review` skill; all path references updated across consuming skills.
- **PRD framing removed from `andthen:plan`** – the `plan` description, workflow, and OpenAI agent prompt no longer claim to create PRDs. That work lives in the new `andthen:prd` skill.

### Removed (breaking)
- **`andthen:qa-test-engineer` agent** – replaced by the new `andthen:testing` skill. The skill surface lets test-first/TDD discipline live alongside coverage and strategy in one place. Callers (`exec-spec`, `triage`, `e2e-test`) now invoke `/andthen:testing` instead of spawning the agent. The `scripts/install-skills.sh` stale-agent list removes the old Codex `andthen-qa-test-engineer.toml` on upgrade.
- **`andthen:solution-architect` agent, `andthen:ui-ux-designer` agent, `andthen:build-troubleshooter` agent** – these three agents didn't need fresh context, they needed methodology applied to current work. Converted into skills or merged into existing skills:
  - `solution-architect` → merged into `andthen:architecture --mode advise` (CUPID/DDD/ADR methodology now lives in `plugin/skills/architecture/references/mode-advise.md`)
  - `ui-ux-designer` (agent) → new `andthen:ui-ux-design` skill (merges the former `design-system` and `wireframes` skills as modes alongside `research` and `review`)
  - `build-troubleshooter` → merged into `andthen:triage` (diagnostic methodology now lives in `plugin/skills/triage/references/diagnostic.md`)
  - The remaining lookup, research, and visual-capture agents stayed as agents at that point because they benefited from fresh context.
- **`andthen:trade-off` skill** – absorbed into `andthen:architecture --mode trade-off`. Trade-off analysis stays the same (weighted criteria, option research, recommendation, optional ADR); it now chains naturally with `advise` (design options) and `fitness` (governance for the chosen path).
- **`andthen:design-system` skill** – absorbed into `andthen:ui-ux-design --mode design-system`.
- **`andthen:wireframes` skill** – absorbed into `andthen:ui-ux-design --mode wireframes`.
- **`andthen:architecture-review` skill folder** – renamed to `andthen:architecture` via `git mv` (blame history preserved). Callers using `/andthen:architecture-review` must migrate to `/andthen:architecture`. Modes unchanged; `trade-off` added as a 5th mode.
- **Agent-scoped methodology references** – the 6 `*-methodology.md` files and `documentation-retrieval-guide.md` under `plugin/references/` are gone. Methodology now lives inline in each agent `.md` file or as a skill-local reference, removing the brittle two-file-with-path-substitution pattern.
- **Committed `codex/agents/*.toml`** – replaced by install-time generation (see Added). The `codex/` directory is no longer committed.
- **`andthen:spec-plan` skill** – absorbed into `andthen:plan`. Re-running `andthen:plan` on a directory with existing FIS is the new "fill missing specs" path. `--skip-specs` preserves the old two-step flow on demand.
- **`andthen:review-code`, `andthen:review-doc`, `andthen:review-gap`, `andthen:review-council` skills** – absorbed into `andthen:review` as internal modes. External callers of `/andthen:review-code` etc must migrate to `/andthen:review --mode code|doc|gap`; `/andthen:review-council` callers migrate to `/andthen:review --council`.
- **`andthen:review` `--deep` flag** – removed. Multi-perspective adversarial review is now the dedicated `--council` flag; plain `--mode code` runs a single-reviewer pass.
- **Typed GitHub artifact envelope contract removed** – `plugin/references/github-artifact-roundtrip.md` and `plugin/references/resolve-github-input.md` deleted. The `<!-- ANDTHEN_ARTIFACT:BEGIN -->` envelope, `schema: andthen/github-artifact-v1`, `artifact_type`, `canonical_local_primary`, embedded `### File:` blocks, and all round-trip metadata fields are gone. Rationale: the envelope was designed for cross-machine resumption of multi-file artifacts, a scenario already solved by `git push` + branch checkout. Paying envelope cost on every producer/consumer was over-engineering.
- **GitHub I/O narrowed to six prose-only integration points**:
  - `clarify --issue <n>` / `prd --issue <n>` – fetch issue body as prose requirements
  - `prd --to-issue` – publish PRD as a plain GitHub issue
  - `triage --to-issue` – publish triage plan / completion summary as a plain issue
  - `quick-implement --issue <n>` – read issue body as prose, implement, open a PR with `Closes #N`
  - `review --to-pr <number>` / `architecture --to-pr <number>` – post the report as a plain PR comment
- **`--issue` and `--to-issue` removed** from `andthen:plan`, `andthen:spec`, `andthen:exec-plan`, and `andthen:exec-spec` – these skills are local-only. Use a feature branch + PR for cross-machine handoff.
- **`andthen:review --to-issue` removed** – use `--to-pr <number>` for PR-scoped publication; otherwise the report file lives on disk. `andthen:architecture --to-issue` removed for the same reason.
- **`andthen:remediate-findings` GitHub URL input removed** – accepts only local report paths and direct raw report URLs. Issue/PR-shell URLs stop with an invalid-input error.
- **`exec-plan` variable rename**: `PLAN_SOURCE` → `PLAN_DIR`.
- **`exec-spec` variable rename**: `FIS_SOURCE` → `FIS_FILE_PATH`. `STORY_IDS` and `PLAN_FILE_PATH` are now extracted from the FIS itself (header field or filename prefix).
- **`check-stubs.sh`, `check-wiring.sh`, `verify-implementation.sh` scripts removed** – grep-based heuristics now inlined as short prose instructions in `andthen:exec-spec` Step 4a and `andthen:review` gap lens. Frontier models run the underlying greps directly; wrapping them in shell scripts violated the "if a frontier model would naturally do something, don't instruct it" principle and carried a drift vector across duplicated copies. `plugin/skills/exec-spec/scripts/` directory removed; `plugin/skills/review/scripts/` now only holds `run-security-scan.sh` (real tool wrapper). `scripts/test-scripts.sh` removed (tested a path – `plugin/scripts/` – that no longer exists).


---

## [0.12.1] – 2026-04-17

### Fixed
- **Skills-as-agents regression eliminated** (CLAUDE.md, and 19 skill prompts including `review`, `exec-spec`, `plan`, `spec`, and `spec-plan`) – skill names were being passed as `subagent_type` to the Task tool, triggering "Agent type not found" errors. Reworded every `andthen:<name>` reference across skill prompts, references, and templates so the type noun ("skill" or "agent") sits adjacent to the name; purged the "Spawn `andthen:<skill>` sub-agent" antipattern
- **Install-script slash-command translation** (`scripts/install-skills.sh`) – added anchored rewrite rule so `/andthen:<name>` invocations correctly become `$andthen-<name>` for Codex/portable agents while preserving path separators, markdown links, and URLs containing `/andthen:` substrings

### Added
- **Skills vs Agents invariant** (CLAUDE.md) – new guardrail section names the authoritative agent/skill lists, the "Spawn `andthen:<skill>` sub-agent" antipattern, the mandatory wording convention (type noun adjacent to each `andthen:<name>` reference), and an audit command for future refactorings
- **`architecture-review` multi-mode chains** (`architecture-review`) – `--mode` now accepts a comma-separated list (e.g. `--mode review,fitness` or `--mode review,decompose,fitness`); chained modes execute in declared order, share computed metrics, dependency graph, connascence, and findings without recomputation, and produce a single combined report with merged Executive Summary and legend. Skill description updated to surface the four modes and chaining capability

### Changed
- **`quick-review` instruction reworded** (`quick-review`) – clarified positioning as a "lightweight mid-conversation review" scoped to recent changes, rather than framing it primarily as "not a formal review"


---

## [0.12.0] – 2026-04-16

### Changed
- **Redundant review layers eliminated across core flows** (`review-gap`, `remediate-findings`) – `review-gap` no longer delegates to `review-code` (exec-spec already runs it), and `remediate-findings` uses `quick-review` instead of spawning up to 3 heavyweight review sub-agents
- **`exec-plan` simplified to fixed pipeline** (`exec-plan`) – removed `--review-mode` parameter and conditional branching; each story now runs `exec-spec` → `quick-review`, with a single `review-gap` on the whole plan at the end
- **GitHub artifact routing factored into shared reference** (`resolve-github-input.md`, `clarify`, `spec`, `exec-spec`, `review-gap`, `remediate-findings`, `plan`, `spec-plan`, `exec-plan`) – extracted GitHub input resolution logic from 8 skills into a single shared reference, reducing per-skill prompt weight and ensuring consistent routing
- **Adversarial challenge made conditional** (`review-gap`, `review-doc`) – full adversarial challenge now triggers only when any finding is Critical or total findings exceed 5; otherwise applies inline severity calibration
- **`exec-spec` completion steps consolidated** (`exec-spec`) – merged Steps 5b (Update FIS/Plan), 5c (Update State), and 5d (Continuation Sync) into a single combined gate step, reducing 5 substeps to 3
- **Small references inlined and deleted** (`exec-spec`, `exec-plan`, `quick-implement`) – `verification-evidence.md` and `post-completion-guide.md` inlined into consuming skills and removed
- **`spec-plan` classification simplified** (`spec-plan`) – THIN/COMPOSITE classification reduced from 9+ conditions to 2 criteria each
- **`plan` skill trimmed** (`plan`) – reduced from 356 to 298 lines by condensing goal-backward analysis, story metadata, design space analysis, and wave assignment sections
- **Language trimming applied across workflow skills** (`clarify`, `spec`, `exec-spec`, `exec-plan`, `plan`, `spec-plan`, `review-gap`, `remediate-findings`, `review`, `review-code`, `review-doc`, `quick-review`, `quick-implement`) – replaced emphatic MUST/NEVER/CRITICAL patterns with balanced direct language, removed filler prose, and consolidated redundant mixed-mode guidance in `review`
- **"Read Workflow Rules" instruction normalized** (`quick-implement`) – replaced verbose form with the shortened cross-agent-safe form used by other review/secondary skills
- **`fis-authoring-guidelines.md` trimmed** (`fis-authoring-guidelines.md`) – principles block condensed, self-check reduced, philosophical framing removed
- **`github-artifact-roundtrip.md` consumption logic factored out** (`github-artifact-roundtrip.md`) – routing/extraction rules moved to `resolve-github-input.md`; roundtrip doc now focuses on publishing and continuation sync
- **Research responsibility clarified across plan → spec-plan → spec** (`plan`, `spec-plan`, `spec`) – `plan` no longer creates `.technical-research.md` (lightweight scan for story boundaries only); `spec-plan` reduced from 4 to 3 upfront research sub-agents (external API research deferred to individual spec sub-agents that need it); `spec` now structurally skips research steps when plan-scoped `.technical-research.md` exists upstream
- **`exec-plan` and `exec-plan-team` merged into single `exec-plan` skill** (`exec-plan`) – Agent Teams mode available via `--team` flag with auto-detection; `--worktree` for parallel execution in team mode; team section written at higher altitude instead of verbatim prompt templates; shared final review/verification steps
- **`review-council` and `review-council-team` merged into single `review-council` skill** (`review-council`) – Agent Teams mode available via `--team` flag with auto-detection; shared preamble and forked execution paths
- **Review skills consolidated to fewer user-facing entry points** (`review`, `review-code`, `review-doc`, `review-gap`) – `review-code`, `review-doc`, and `review-gap` demoted to internal delegates (`user-invocable: false`); `review` router description updated to emphasize it as the single entry point for all review types; added "review implementation of [doc]" routing heuristic to correctly route to gap review

### Removed
- **`plugin/references/verification-evidence.md`** – content inlined into consuming skills
- **`plugin/references/post-completion-guide.md`** – content inlined into consuming skills
- **`plugin/skills/exec-plan-team/`** – merged into `exec-plan` with `--team` flag
- **`plugin/skills/review-council-team/`** – merged into `review-council` with `--team` flag

## [0.11.2] – 2026-04-15

### Changed
- **`plan` now defaults to headless requirements synthesis** (`plan`) – replaced the interactive discovery interview path with headless-first PRD/plan synthesis that proceeds with explicit assumptions and only stops on true contract failures or irreducible ambiguity
- **Non-interactive workflow stop gates now use fail-fast contract wording** (`spec`, `spec-plan`, `exec-spec`, `exec-plan`, `exec-plan-team`, `triage`, `review-gap`, `remediate-findings`, `design-system`, `wireframes`, `excalidraw-diagram`) – normalized prompt language away from conversational “ask/recommend/direct user” phrasing toward explicit missing-input, invalid-input, and downstream-routing exits suitable for headless execution
- **Technical research companion files are hidden again** (`plan`, `spec`, `spec-plan`, `exec-spec`, templates, artifact round-trip docs, FIS authoring guidelines`) – renamed the documented companion artifact from `technical-research.md` to `.technical-research.md` to make it easier to ignore by default while still keeping it available for execution context when needed
- **`architecture-review` reports now explain their shorthand inline** (`architecture-review`) – added a required `How to Read This Report` legend for review, decompose, and fitness outputs so package and graph metrics, package-principle acronyms, C4 labels, zone labels, and connascence abbreviations are explained in the report instead of assuming prior architecture-review knowledge

## [0.11.1] – 2026-04-14

### Fixed
- **Project Document Index wording drift in workflow skills** (`spec-plan`, `exec-spec`, `ops`, `init`) – removed stale hardcoded document-name references (`LEARNINGS.md`, `STATE.md`, `ARCHITECTURE.md`, `STACK.md`) where those prompts should refer to the `Learnings`, `State`, `Architecture`, and `Stack` documents via the **Project Document Index**
- **`spec-plan` project-context discovery drift** (`spec-plan`) – Step 1.5 now reads the `Learnings` document using the same Project Document Index contract as the rest of the workflow, avoiding a stale direct filename reference during batch spec generation
- **`review` routing ambiguity** (`review`) – explicit mode flags now constrain target discovery, explicit code-review intent no longer gets silently upgraded to gap review just because nearby spec artifacts exist, and `Mixed` is now a stable `Doc + Code` dispatch mode instead of a fuzzy fallback

## [0.11.0] – 2026-04-14

### Added
- **Direct `exec-spec` execution model** (`exec-spec`) – `exec-spec` now implements FIS documents directly, keeping deep implementation context in one agent while reserving sub-agents for advisory work, fresh-context review, and visual validation
- **Shared methodology references for thin agents** (`plugin/references/*-methodology.md`, `plugin/agents/*`, `codex/agents/*`) – extracted reusable diagnostic, documentation lookup, QA, research, solution architecture, UI/UX, and visual validation guidance into shared reference files consumed by thin Claude and Codex agent wrappers
- **Codex custom agent distribution** (`codex/agents`, `install-skills`) – expanded portable Codex agent distribution for the advisory/review agent layer and wired the installer to export those agents alongside skills

### Changed
- **FIS execution contract simplified** (`exec-spec`, `spec`, `spec-plan`, `fis-template`, `fis-authoring-guidelines`) – the workflow now centers direct execution, task-level scenario proof mapping, explicit execution contracts, and tighter size/traceability checks for specs
- **Downstream plan execution alignment** (`exec-plan`, `exec-plan-team`, `MODEL-EFFORT-SELECTION-GUIDE`, `README`) – downstream orchestration and model-selection docs now reflect the direct-execution `exec-spec` contract instead of an implementor sub-agent architecture
- **Portable install path expanded** (`install-skills`, `README`) – the installer now exports skills, shared references, shared templates, helper scripts, and Codex agents as a single portable setup flow instead of leaving Codex agent installation as a manual step
- **`exec-spec` execution flow clarified** (`exec-spec`) – scenario-test scaffolding, technical-research/learnings/ubiquitous-language lookup, proactive advisory sub-agent usage, direct remediation, and completion reporting now live in one executor workflow instead of being split across orchestrator and implementor prompts

### Fixed
- **Bounded remediation path in `exec-spec`** – preserved a single recovery path for required validation failures while keeping the no-second-loop rule after one remediation pass
- **Portable path and namespace rewriting coverage** (`install-skills`, `templates/CLAUDE.template.md`) – exported bundles now rewrite `${CLAUDE_PLUGIN_ROOT}/skills/...` references, markdown link targets, and embedded `andthen:` skill/agent references in shared templates, preventing broken links and plugin-only command names in installed non-plugin bundles
- **Direct-execution validation continuity** (`exec-spec`) – `exec-spec` now maintains `changed-files` within the main run before scoped stub/wiring/substance checks instead of depending on a separate implementor handoff
- **Authoring and diagnostic source-of-truth drift** (`fis-authoring-guidelines`, `triage`) – aligned the FIS guide with task-ID proof mapping and direct-execution context, and pointed `triage` at the shared diagnostic methodology
- **Stale architecture docs after the direct-execution rewrite** (`README`, `plugin/README`, `CHANGELOG`) – updated live docs to stop describing `exec-spec` as an orchestrator/implementor flow after the implementor agents were removed
- **Trigger-eval harness robustness** (`scripts/eval-skill-triggers.sh`, `evals/skill-trigger-queries.json`) – removed a duplicate positive routing case from the eval corpus, stopped `--skill` from being interpolated into jq source, and made eval runs fail explicitly on `claude`/`jq` runtime errors instead of misreporting them as routing misses

## [0.10.8] – 2026-04-13

### Added
- **PRD and plan artifact templates** (`plan`) – added dedicated `prd-template.md` and `plan-template.md` files so long-lived planning artifacts now have explicit reusable baseline formats, similar to the existing FIS template pattern
- **Shared anti-rationalization reference** (`anti-rationalization`) – new `plugin/references/anti-rationalization.md` keeps the old excuse→reality pattern available as an on-demand reference instead of re-inlining rationalization tables into multiple skill bodies. Wired from `exec-spec`, `quick-implement`, `triage`, and `refactor`
- **Shared trust-boundaries reference** (`trust-boundaries`) – new `plugin/references/trust-boundaries.md` defines a compact 3-tier trust model (`Trusted` / `Verify Before Acting` / `Untrusted`) for browser state, logs, error output, scraped content, external docs, and tool/model output crossing boundaries

### Changed
- **Template-backed planning flow** (`plan`) – PRD creation and `plan.md` generation now reference dedicated template files instead of carrying the full document shapes inline in the skill prompt
- **Plan contract guidance** (`plan`) – the plan skill now explicitly preserves the Story Catalog columns and standard story metadata labels that downstream execution and review skills depend on
- **Lightweight anti-rationalization hooks** (`exec-spec`, `quick-implement`, `triage`, `refactor`) – skip-prone implementation/refactor skills now point to the shared `anti-rationalization` reference at the moment discipline is most likely to erode, preserving the pattern without re-bloating the main workflows
- **Trust-boundary wiring centralized** (`e2e-test`, `triage`, `review-code`) – inline trust warnings now route through the shared `trust-boundaries` reference so browser/runtime/tool-output handling can evolve in one place instead of diverging across skills
- **Scope-boundary artifacts strengthened** (`clarify`, `spec`, `fis-template`, `fis-authoring-guidelines`) – `clarify` now emits a `Not Doing (for now)` section for explicit non-goals and deferrals, `spec` carries those non-goals forward from `requirements-clarification.md`, and FIS authoring now requires non-goal items to be specific and justified rather than filler
- **FIS non-goals content upgraded without changing the contract** (`spec`, `spec-plan`, `fis-template`, `fis-authoring-guidelines`) – the canonical section remains `What We're NOT Doing`, but the template and guidance now require `3-5` intentional exclusions/deferrals with reasons so scope cuts survive session handoffs cleanly

### Fixed
- **Plan template story metadata contract** (`plan`) – restored `Phase`, `Wave`, `Dependencies`, `Parallel`, `Risk`, and `Asset refs` in the per-story template so generated plans match the story definition contract
- **Plan template example consistency** (`plan`) – aligned the Story Catalog example with the Phase Breakdown example to avoid teaching an internally inconsistent `plan.md` structure
- **Review-code trust-boundary trigger scope** (`review-code`) – broadened the trigger text to include logs, stack traces, error output, scraped content, and tool results so it matches the actual scope of the shared `trust-boundaries` reference
- **Non-goals section naming drift** (`fis-template`, `fis-authoring-guidelines`, `spec-plan`) – kept `What We're NOT Doing` as the canonical heading after strengthening the template, avoiding downstream checks and review logic keying off inconsistent section names

## [0.10.7] – 2026-04-13

### Added
- **Typed GitHub artifact envelope** (`github-artifact-roundtrip`, `plan`, `spec`, `review-gap`, `review-code`, `architecture-review`, `triage`) – GitHub issues and PR comments now have a machine-consumable AndThen envelope with artifact metadata plus embedded file blocks for round-trip workflows

### Changed
- **GitHub-first execution paths** (`exec-spec`, `spec-plan`, `exec-plan`, `review-gap`, `remediate-findings`) – downstream skills now accept typed GitHub issues / PR comment URLs and extract embedded artifacts into `.agent_temp/github-artifacts/...` before continuing
- **GitHub publish contract** (`report-output-conventions`, `quick-implement`) – PR-published review artifacts now require direct comment URLs, and `quick-implement` prints the created PR URL / number for follow-on PR workflows
- **Plan-backed FIS round-trip metadata** (`spec`, `exec-spec`) – `fis-bundle` now preserves `plan_path` / `story_ids`, requires deterministic primary-file resolution via `canonical_local_primary`, and restores plan context before plan/STATE updates
- **Canonical continuation sync** (`github-artifact-roundtrip`, `spec-plan`, `exec-plan`, `exec-plan-team`, `exec-spec`) – GitHub-extracted bundles are now explicitly treated as working mirrors that must sync back to local canonical files or refreshed GitHub artifacts before completion

## [0.10.6] – 2026-04-12

### Added
- **Negative-path scenario checklist** (`fis-authoring-guidelines`, `fis-template`) – systematic coverage check for omitted optional inputs, no-match selectors/filters, and rejection paths for external integrations. Applies to both `spec` and `spec-plan` via shared references
- **Scope-consistency and output format self-checks** (`fis-authoring-guidelines`, `fis-template`) – every In Scope item must be covered by a scenario or task; structured output criteria must specify shape, not just "returns JSON"
- **Prescriptive detail verification for Verify lines** (`fis-authoring-guidelines`) – when a FIS prescribes specific formats, columns, paths, or strings, the Verify line must check them verbatim. Weak/strong examples included
- **PRD-FIS semantic traceability** (`spec-plan`) – cross-cutting review check #10 verifies PRD feature requirements flow into FIS scenarios, catching requirements lost during plan decomposition. Binding PRD constraints extracted by technical research sub-agent and consumed by spec sub-agents
- **Spec compliance spot-check** (`exec-spec`) – Step 4a.7 extracts prescriptive details from the FIS and greps the implementation before marking complete. Prescriptive Detail Injection guidance ensures sub-agent prompts include format strings, column names, and file paths verbatim
- **Review mode guidance** (`exec-plan`) – recommends `per-story` (default) for most plans; documents when `none` and `full-plan` are appropriate
- **Plan provenance field** (`plan`) – `Provenance` story field for carried-forward stories with no PRD coverage, wired into Story Definition, output example, and validation self-check

### Changed
- **Plan Acceptance Gate expanded** (`exec-plan`) – now verifies exec-spec's spec compliance check completed (FIS checkboxes marked, verification evidence exists) before marking Done
- **`spec` Step 3 references negative-path checklist** – scenarios are now drafted with explicit negative-path guidance at the point where they're written, not just in the template
- **Composite FIS naming convention** (`plan`) – naming rule moved from advisory GOTCHAS into normative Composite FIS section

### Context
Based on post-mortem analysis of a real 11-story plan execution (plan → spec-plan → exec-plan → 2x review-gap) that failed gap review with 8 findings across 3 systemic patterns: missing negative-path scenarios, PRD-to-FIS requirements drift, and implementation ignoring explicit spec details.

---

## [0.10.5] – 2026-04-12

### Added
- **Technical Research Separation** – new `technical-research.md` companion document pattern keeps FIS and PRD/Plan focused on intent (reviewable for correctness) while preserving codebase analysis, API research, and architecture trade-offs for the executing agent. Updated FIS authoring guidelines with "what goes where" guidance and verification-during-execution contract. Touches `spec`, `plan`, `spec-plan`, `exec-spec`, FIS template, and authoring guidelines
- **Rollback-Friendly Groups** (`fis-authoring-guidelines`) – cross-cutting constraint on all slicing strategies: prefer additive changes within a group, separate "add new" from "remove old" so each group is independently revertable. A group that deletes and replaces in one pass leaves the system broken on revert
- **Prove-It Pattern for verification gates** (`exec-spec`) – behavioral failures between execution groups now require a failing test before the fix, proving the bug existed and preventing reintroduction in later groups
- **Non-reproducible bug classification** (`triage`) – when 5 Whys stalls on non-reproducible issues, classify by failure pattern (timing-dependent, environment-dependent, state-dependent, truly intermittent) with concrete investigation actions for each

### Changed
- **`spec-plan` renamed `.research-brief.md` to `technical-research.md`** – no dot prefix, includes "technical" for clarity. All prose references updated from "research brief" to "technical research" for consistency
- **`exec-spec` Step 1.5 skip conditions refined** – scaffold tests when a test runner exists and tasks have branching logic; skip only for config-only tasks with no scenarios. Beyonce Rule: when in doubt, scaffold
- **Development guidelines testing principle** – added Beyonce Rule: non-trivial branching logic gets a test even when no scenario covers it
- **FIS template scenario skip aligned with exec-spec** – replaced broad "purely structural work (scaffolding, config, migrations)" with narrow "configuration-only work with no branching logic" to match exec-spec's test-scaffold gate

### Fixed
- **Stale "Research brief" in `spec-plan`** – one COMPOSITE classification criterion still referenced "Research brief" after the rename to "technical research"
- **`spec` unconditional research file creation** – Step 2 mandated `technical-research.md` creation without qualifier; added "if substantial" guard matching `plan` skill's pattern
- **FIS template broken relative link** – `../../references/fis-authoring-guidelines.md` resolves inside the plugin tree but breaks in every generated FIS; removed the link, kept the description
- **`exec-spec` skip condition AND/OR ambiguity** – natural-language precedence was unclear; restructured as bulleted list with unambiguous nesting

---

## [0.10.4] – 2026-04-11

### Added
- **Plugin manifest** (`plugin/.claude-plugin/plugin.json`) – new per-plugin manifest file aligned with the official Claude Code plugin specification. Version bump instructions updated in `CLAUDE.md` and `ops` skill to cover all three version locations
- **Session management guidance** – predecessor skills (`clarify`, `plan`, `spec`, `spec-plan`) now recommend starting a clean session before context-intensive skills (`exec-spec`, `spec-plan`, `exec-plan`/`exec-plan-team`, `review-council`/`review-council-team`). README documents the principle in the Workflows section
- **Follow-up actions for `spec` and `spec-plan`** – both skills now have FOLLOW-UP ACTIONS sections suggesting next steps (previously missing)

### Changed
- **Marketplace.json aligned with official schema** – added `$schema`, moved `description` to top level, added `category` and `homepage`, removed redundant `metadata.pluginRoot` and `strict` fields
- **Skills reorganized as Standalone / Pipeline** – README skill tables restructured from Core/Extras to Standalone (13 everyday skills) and Pipeline (12 workflow skills), with usage examples reordered to lead with standalone one-liners. Both `plugin/README.md` and root `README.md` aligned
- **`plan` follow-up actions reordered** – lightweight options (spec S01, wireframes, review) listed first, context-intensive options (spec-plan, exec-plan) grouped after with clean-session tags

---

## [0.10.3] – 2026-04-11

### Fixed
- **Skill/agent invocation disambiguation** – fixed ~44 ambiguous `andthen:` references across 20 SKILL.md files where invocation instructions did not clearly distinguish between skills and sub-agents. Skills now consistently use "invoke the `andthen:X` skill" pattern; agents use "delegate to the `andthen:X` agent" pattern. Cross-references (non-invocation mentions) are left bare. Regression from v0.10.0 where the standardization was incomplete
- **`review-gap` requirements discovery** – gap analysis now discovers the full requirements baseline when given a directory or plan file, instead of treating the single input as the only requirements source. Searches for sibling PRD, plan, and FIS files; extracts FIS paths from Story Catalog tables and Phase Breakdown sections. Prevents shallow reviews that miss requirements context
- **`review-gap` code review report consolidation** – review-code sub-agent now returns findings inline instead of writing a separate report file, keeping the gap analysis as the single consolidated report

---

## [0.10.2] – 2026-04-10

### Fixed
- **`remediate-findings` re-validation loop** – replaced impractical "re-run originating review" step (which the model always skipped, cascading into skipped state updates) with a concrete findings re-check pattern: walk each finding, classify as RESOLVED/PARTIALLY RESOLVED/UNRESOLVED/DEFERRED with evidence, then run `review-code` on touched scope for regression detection. Scoped the "do not defer state updates" directive to prevent both the original caution deadlock and premature state updates on partial resolutions. Removed duplicate `review-code` invocation and aligned the Phase 4 gate with the severity policy

---

## [0.10.1] – 2026-04-10

### Added
- **`remediate-findings` skill** – new remediation workflow for implementing actionable findings from review reports such as `review-gap` and `review-code`. Re-validates findings against the current workspace, applies the smallest safe fix set, re-runs the relevant verification, and updates `plan.md`, FIS checkboxes, and `STATE.md` through `ops` when the reviewed work is now complete

### Changed
- **Review remediation path made explicit** – `exec-plan` and `exec-plan-team` now route review failures through `remediate-findings` instead of vague inline “fix issues” instructions, with consistent two-round review/remediation limits
- **Workflow and model docs updated** – README, plugin README, and the model-effort guide now document `remediate-findings` as the follow-up path after actionable review findings

---

## [0.10.0] – 2026-04-10

### Added
- **`architecture-review` skill** – deep quantitative architecture review with four modes: **review** (dependency metrics, package principles, connascence analysis, anti-pattern scan), **decompose** (split/merge evaluation using Ford/Richards drivers), **advise** (framework-grounded architectural guidance), and **fitness** (fitness function proposals with 4-level governance stack). Includes 9 reference files synthesizing Ford & Richards, Farley, Martin's Package Principles, Page-Jones/Weirich connascence taxonomy, and Building Evolutionary Architectures. Features adversarial challenge pass, language-aware tooling suggestions, and shared calibration integration
- **`quick-review` skill** – lightweight in-conversation review that spawns a fresh-context sub-agent for adversarial critique of recent changes. Auto-scopes from pending git changes or conversation context, classifies change type (code, spec, config, docs, prompt) to select the appropriate review lens, and applies anti-leniency principles inline. Designed for mid-conversation sanity checks without the overhead of formal review skills
- **Skill Authoring Philosophy** in CLAUDE.md – codifies intent-driven authoring principles: why over what, right altitude, named principles over unnamed rules, and intent reasoning as non-waste. Establishes the reference point for skill authors to prevent over/under-correction in future edits
- **Structured Output Protocols reference** – new `plugin/references/structured-output-protocols.md` with three named agent-user communication formats (CONFUSION, NOTICED BUT NOT TOUCHING, MISSING REQUIREMENT) for surfacing ambiguity and scope boundaries. Referenced from `exec-spec`, `quick-implement`, `triage`, and `spec`
- **Slicing vocabulary** in FIS authoring guidelines – three named strategies (Vertical, Risk-First, Contract-First) for execution group ordering decisions
- **Named principles** across skills – Chesterton's Fence (`refactor`), Prove-It Pattern (`triage`), Proof-of-Work (`spec`, `exec-spec`), Stop-the-Line (`exec-spec` verification gates), Trust Tiers for external content (`e2e-test`, `triage`)
- **Scenarios and Proof-of-Work** – BDD-inspired Given/When/Then scenarios serve triple duty: requirement, test specification, and proof-of-work contract. Traceable chain across the workflow: `plan` stories seed Key Scenarios (one-line behavioral seeds) → `spec` elaborates them into full Given/When/Then → `exec-spec` scaffolds them as failing tests (Step 1.5) and proves them green during implementation. Concept grounded in Tegmark & Omohundro's verification asymmetry (arXiv:2309.01933)
- **Documentation Source Authority** hierarchy in development guidelines – 4-tier source ranking with explicit exclusion of unreliable sources (Stack Overflow, blog tutorials, AI-generated summaries, training data recall)
- **Restored intent reasoning** in `exec-spec` – three pieces of load-bearing "why" reasoning from the v0.8.7 rationalizations tables that were over-aggressively removed during condensation: why test scaffolding precedes implementation (verifies intent, not incidental behavior), why verification gates exist (prevent cascading failures across groups), and why Step 3 validation differs from Step 2 gates (cross-cutting vs task-level issues)

### Removed
- **Minimal FIS template removed** – `plugin/skills/spec/templates/fis-template-minimal.md` deleted. THIN stories now use the standard FIS template, collected into a single `thin-specs.md` per phase
- **All external plugin dependencies removed** – `code-simplifier` and `frontend-design` plugins are no longer referenced by any skill or agent. AndThen is now fully standalone
  - **`refactor` skill made standalone** – removed all `code-simplifier:code-simplifier` delegation. Refactoring philosophy (preserve behavior, favor readability over cleverness, balance simplification) integrated directly into the skill
  - **`exec-spec` and `quick-implement` code-simplifier references inlined** – replaced external agent delegation with inline intent ("review implemented code for simplification opportunities")
  - **`frontend-design` philosophy integrated into `ui-ux-designer` agent** – bold aesthetic direction, anti-AI-slop stance, typography/color/atmosphere/motion principles added to Visual Design Mode
  - External Dependencies sections removed from CLAUDE.md, README.md, and plugin/README.md

### Changed
- **`spec-plan` THIN stories collected into single file** – THIN specs are no longer written as individual files using the minimal FIS template. All THIN stories are collected into one `{PLAN_DIR}/thin-specs.md` following standard FIS structure, with execution groups organized by story. Leverages existing shared-FIS dedup in `exec-plan`/`exec-plan-team` – exec-spec runs once, remaining stories skip to acceptance gate
- **`spec-plan` COMPOSITE criteria broadened** – added two new grouping signals: same module/directory (stories primarily affecting the same directory per research brief), phase cohesion (all stories in a phase of ≤4 stories sharing an architectural layer). Max composite group size raised from 3 to 5. Shared files threshold relaxed from 50% to any shared files. Guidance added to prefer COMPOSITE over STANDARD when grouping signals exist
- **Shared-FIS Dedup terminology unified** – `exec-plan` and `exec-plan-team` dedup sections now reference both composite and collected thin-specs FIS paths
- **`exec-spec` validation restructured** – quality review (functionality gaps, simplification opportunities) moved from standalone Step 4 into Step 3 as TV04, feeding into the remediation loop (now TV05). Previously, issues found in Step 4 had no fix path. Step numbering updated throughout (old Steps 5/6 → Steps 4/5)
- **Intent engineering overhaul** – all 24 skill prompts condensed to eliminate cross-skill duplication, template over-specification, validation bloat, and emphatic overtriggering. Total prompt volume reduced from ~7,500 to ~4,500 lines (~40% reduction). Post-condensation review restored 30 behavioral details initially over-trimmed (tool references, scope guards, gate instructions, classification rules across 11 skills and references)
- **Shared references extracted** – `report-output-conventions.md`, `adversarial-challenge.md`, `reviewer-roster.md`, `post-completion-guide.md`, `verification-evidence.md` created in `plugin/references/`. Review and execution skills reference these instead of inlining duplicate content
- **`exec-plan-team` worktree default flipped** – sequential execution on the current branch is now the default. Use `--worktree` to opt in to isolated git worktrees (previously the default, with `--no-worktree` as opt-out)
- **`exec-plan-team` branch name generalized** – hardcoded `main` branch references replaced with a `BASE_BRANCH` variable resolved at startup via `git rev-parse --abbrev-ref HEAD`, supporting feature branches and non-main base branches
- **`exec-plan-team` wave overlap** – W2 implementation can now overlap with W1 reviews (worktrees are isolated), but W2 *merge* waits for W1 review completion (`per-story` mode) since reviews may fix code on the base branch. Updated timing diagrams and dependency rules
- **`exec-plan-team` progress reporting** – orchestrator must print status updates (task creation, agent start/complete, wave/merge/review/phase milestones) to the user throughout execution – the user cannot see agent activity directly
- **Spawn templates consolidated** – `exec-plan-team` reduced from 4 spawn templates (implementer/reviewer × worktree/no-worktree) to 2 with inline worktree conditionals
- **PRD template deduplicated** – `plan` skill collapsed from structure enumeration + duplicate markdown template into a single condensed template
- **Quality checklists trimmed** – all skill validation checklists reduced from 12-30 items to 3-5 non-obvious items per skill
- **Rationalizations tables removed** – `exec-spec`, `spec`, and `quick-implement` no longer include "Common Rationalizations" tables (introduced in 0.8.7). The table format micro-managed reasoning; load-bearing intent reasoning from the tables was restored separately as inline explanations (see Added)
- **GOTCHAS sections pruned** – all skills trimmed to genuinely non-obvious hazards only (items the model would not infer from the workflow itself)
- **Emphatic markers reduced** – `MUST`/`NEVER`/`CRITICAL` reserved for genuinely counter-intuitive constraints across all skills
- **review-council-team refocused** – eliminated ~70 lines duplicated from `review-council`, now focuses exclusively on Agent Teams-specific mechanics
- **excalidraw-diagram phases merged** – near-duplicate Phase 4 (Design Refinement) and Phase 5 (Visual Validation) merged into one review-and-refine phase; render code block stated once and referenced
- **wireframes templates replaced** – inline HTML/CSS code blocks replaced with design principles
- **exec-plan review modes** – defined once in a "Review Mode Contract" section instead of restated 3 times
- **Model references made platform-agnostic** – all hardcoded `model: "opus"` / `"sonnet"` / `"haiku"` references now include cross-platform equivalents (`gpt-5.4`, `gpt-5.3-codex`, `gpt-5.4-mini`) and "or similar" to support Codex CLI and other agents
- **Report output resolution order** – `report-output-conventions.md` now explicitly states the `spec directory → target directory → fallback` priority, previously implicit in bullet ordering
- **`review-council-team` fallback corrected** – instructions now consistently point to `andthen:review-council` (was incorrectly `review-code` in one location)

---

## [0.9.0] – 2026-04-09

### Added
- **`spec-plan` research brief** – new Step 1.5 performs all discovery work once via parallel sub-agents (project context, story-scoped file map, shared architectural decisions, external research) before spawning any spec sub-agents. Eliminates redundant per-story codebase scanning, guideline reading, and architecture analysis. Output saved to `{PLAN_DIR}/.research-brief.md`
- **`spec-plan` story classification** – new Step 1.6 automatically classifies stories into three tiers: THIN (orchestrator writes minimal FIS directly), COMPOSITE (one sub-agent covers tightly coupled story groups), and STANDARD (one sub-agent per story). Classification uses research brief data (file maps, shared decisions), not subjective judgment
- **Minimal FIS template** – new `plugin/skills/spec/templates/fis-template-minimal.md` for THIN stories (30-60 line target)
- **FIS authoring guidelines reference** – new `plugin/references/fis-authoring-guidelines.md` extracts shared authoring knowledge (principles, generation guidelines, task grouping heuristics, plan-spec alignment check, self-check) from `spec` into a reusable reference
- **Plan-Spec Alignment Check** – new step in `spec` (and shared guidelines) cross-checks each plan acceptance criterion against FIS Success Criteria before finalizing. Prevents specs from silently narrowing plan requirements
- **Plan Acceptance Gate** – `exec-plan` and `exec-plan-team` now verify each plan acceptance criterion is demonstrably satisfied before marking a story `Done`. Catches scope narrowing that slipped through spec generation
- **Composite FIS support in `plan`** – plan template and Story Catalog now show composite FIS examples where multiple tightly coupled stories share one spec file
- **Composite FIS dedup in `exec-plan` and `exec-plan-team`** – when multiple stories share a composite FIS path, `exec-spec` runs once; constituent stories skip re-execution and go straight to the Plan Acceptance Gate

### Changed
- **`spec-plan` sub-agents no longer invoke `andthen:spec`** – sub-agents now reference the FIS template and authoring guidelines directly, eliminating the indirection of loading spec's full workflow and skipping steps via fast-path guards. Reduces per-sub-agent context by ~200 lines
- **`spec-plan` relaxed wave ordering** – the research brief pre-resolves most inter-story architectural decisions, so stories can be specced in parallel regardless of wave assignment. Falls back to strict wave ordering only when the brief is incomplete
- **FIS template streamlined** – removed inline authoring principles/DON'Ts (moved to shared guidelines reference), removed section descriptions and emoji markers, simplified Architecture Decision to compact/full formats, removed pseudocode blocks and "Outline of New/Changed Files" section
- **`spec` authoring guidelines externalized** – inline FIS Authoring Principles, Key Generation Guidelines, Task Grouping Heuristics, and Self-Check sections replaced with reference to shared `fis-authoring-guidelines.md`
- **`spec` fast-path guards removed** – the `> Fast-path: If a research brief was provided...` blockquotes in Steps 1 and 2 are no longer needed since `spec-plan` no longer invokes `spec`
- **`spec` stricter verification** – Verify lines must now assert described behavior, not just build success. Weak/strong examples added. FIS line target tightened from 200-400 to 100-250
- **`spec` Cross-Group Contracts** – new Task Grouping guidance requiring explicit cross-group interface declarations (sub-agents work in separate contexts with no shared memory)
- **`exec-plan-team` composite task handling** – task naming, worktree management, dependency chains, and merge steps generalized from `{story_id}` to `{task_id}` convention supporting both standard and composite tasks

---

## [0.8.7] – 2026-04-06

### Added
- **Discovery interview techniques reference** – new `plugin/references/discovery-interview-techniques.md` with probing techniques (Five Whys, Scenario Testing, Extremes, Trade-off Forcing, Laddering), creative exploration methods (What If, Reversal, HMW, Assumption Reversal, SCAMPER, Role Perspective Shift), and strategies for managing difficult interview moments. Referenced from `clarify` Phase 2
- **`review-doc` adversarial challenge phase** – new Phase 8 spawns a sub-agent to challenge review findings with document-specific questions, filtering false positives and correcting disproportionate severity before report generation
- **Document review calibration** – new `plugin/skills/review-doc/references/doc-review-calibration.md` with document-specific severity calibration, contrastive examples, proportionality guidance, and false positive traps for spec/plan/PRD reviews
- **Code review calibration** – new `plugin/skills/review-code/references/code-review-calibration.md` with code-specific severity examples, completeness/wiring calibration, and code false positive traps

### Changed
- **Review calibration restructured** – `review-calibration.md` trimmed to universal core (anti-leniency protocol, finding quality, over-leniency patterns) with generalized rules. Domain-specific calibration moved to skill-local `references/` directories. `review-gap` now references `review-code`'s calibration since both operate in the code/implementation domain
- **Common Rationalizations tables** – `exec-spec`, `spec`, and `quick-implement` now include tables of self-deception patterns agents generate to skip steps, with reality checks for each
- **`exec-plan-team` `--no-worktree` flag** – disables git worktree isolation for sequential execution on main. Simpler for plans with few parallel stories or when merge complexity is undesirable
- **`ops` STATE.md Recently Completed section** – tracks last 2 milestones with one-line summaries for cross-session continuity
- **Guidelines condensed** – `DEVELOPMENT-ARCHITECTURE-GUIDELINES.md`, `UX-UI-GUIDELINES.md`, and `WEB-DEV-GUIDELINES.md` significantly trimmed to remove content that restates standard engineering principles. Focus shifted to project-specific standards and judgment calls
- **`ops` STATE.md maintenance rules tightened** – ~60 line target (down from ~100), Session Continuity Notes capped at 5 (down from 10), completed stories actively pruned, resolved blockers auto-removed
- **`project-state-templates.md` updated** – STATE.md template aligned with new maintenance rules: Recently Completed section, tighter size guidance, inline documentation for each section's pruning policy
- **`notify-elevenlabs.sh` async and audio improvements** – TTS/playback detached to background process to avoid hook timeout kills, switched from MP3 to PCM 44100 WAV to eliminate afplay frame-padding clipping

---

## [0.8.4] – 2026-03-31

### Added
- **`plan` GitHub issue input** – `plan` now accepts `--issue <number>` to fetch a GitHub issue via `gh issue view` and use it as requirements input for PRD and plan creation. Issue-sourced plans use `issue-{number}-{feature-name}/` output directory naming. Added USAGE section with examples
- **`clarify` GitHub issue input** – `clarify` now accepts `--issue <number>` to fetch a GitHub issue and use it as the starting point for requirements discovery. Previously mentioned "GitHub issue URL" in argument-hint but had no workflow implementation. Added USAGE section with examples

---

## [0.8.6] – 2026-04-01

### Added
- **Monorepo support for `init` and `map-codebase`** – both skills now detect workspace structures (pnpm, yarn, npm, Cargo, Go, nx, turbo, lerna) and adapt accordingly. `init` offers to generate per-sub-project `CLAUDE.md` files with sub-project-specific commands and conventions. `map-codebase` passes sub-project lists to all analysis sub-agents for workspace-aware output
- **`KEY_DEVELOPMENT_COMMANDS.md` template** – new template in `project-state-templates.md` for documenting dev, test, build, and deploy commands. Includes monorepo-aware per-sub-project command sections
- **`map-codebase` command discovery** – new sub-agent (2e) auto-discovers development commands from package.json scripts, Makefiles, Taskfiles, CI configs, and README files. Pre-fills the KEY_DEVELOPMENT_COMMANDS template with actual values
- **`init` offers KEY_DEVELOPMENT_COMMANDS.md** – added to "Core (recommended)" optional documents

### Fixed
- **`CLAUDE.template.md` dangling reference** – the "Key Development Commands" section referenced `docs/rules/KEY_DEVELOPMENT_COMMANDS.md` but the file had no template and wasn't in the Project Document Index. Now properly referenced at `docs/KEY_DEVELOPMENT_COMMANDS.md` with a Document Index row
- **`code-simplifier` agent name disambiguation** – `exec-spec`, `quick-implement`, and `refactor` skills now explicitly note to use the full agent name `code-simplifier:code-simplifier` to prevent shortening

---

## [0.8.5] – 2026-03-31

### Fixed
- **`init` missing `map-codebase` suggestion in partial setup path** – when CLAUDE.md already existed (partial setup), `init` never offered to run `map-codebase` for auto-generating architecture, stack, and conventions docs. The suggestion only existed in the brownfield path (no CLAUDE.md). Now both partial setup and brownfield paths offer `map-codebase` when relevant docs are missing

### Changed
- **READMEs clarify `init` / `map-codebase` relationship** – `init` is the single entry point for all project types; `map-codebase` is delegated to by `init` or run standalone. Updated skill table descriptions and Setup section

---

## [0.8.3] – 2026-03-31

### Added
- **Review evaluator calibration** – new `plugin/references/review-calibration.md` shared reference with anti-leniency protocol, contrastive severity examples (IS/is NOT Critical/High), over-lenient review scenario, finding quality calibration, and false positive traps. Loaded by both `review-gap` and `review-code`
- **Adversarial Challenger for `review-gap`** – new Step 6 spawns a sub-agent with fresh context to challenge all findings (VALIDATED/DOWNGRADED/WITHDRAWN verdicts). Counters self-evaluation bias where evaluators identify issues then rationalize approval. Includes severity mapping from `review-code`'s 3-tier to `review-gap`'s 4-tier system
- **Dimensional scoring with hard thresholds for `review-gap`** – new Step 7 scores Functionality (>=7), Completeness (>=9), and Wiring (>=8) on validated findings only. Any dimension below threshold = FAIL, no negotiation. Produces structured verdict table in Executive Summary for `exec-plan` to parse

### Fixed
- **Stub detection regex** – replaced wildcard `not.implemented` pattern with precise `not[_ -]implemented|notImplemented` in `verification-patterns.md` and `review-gap`

---

## [0.8.2] – 2026-03-29

### Changed
- **`clarify` requirements vs. implementation boundary** – added explicit guardrails preventing clarify from drifting into implementation-level decisions (architecture patterns, library choices, data storage strategies). New "Requirements vs. Implementation Boundary" section in GOTCHAS with concrete DO/DO NOT lists, scoped design space decomposition to user-visible/product-level dimensions only, and added inline scope guard at the step where drift occurs
- **`spec` outcome-focused tasks** – tasks now describe what must be TRUE when done, not what code to write. New gotcha against describing detailed code changes. Reduced spec size target from 300–500 to 200–400 lines. Added over-researching gotcha to keep research phases minimal. Authoring instructions (Grouping Constraints, Implementation Notes, Verification Criteria guidance) moved from FIS template into spec skill – template now only contains sections that appear in generated output
- **FIS template revision** – "Intent over Implementation" added as core principle #1. Example tasks rewritten as outcome-focused. New "Health Metrics" section for anti-regression baselines. New "Agent Decision Authority" section for scope boundary clarity. Verification criteria simplified from 4-dimension checklist to functional checks. Removed authoring meta-instructions that don't belong in generated output
- **Prompt engineering guidelines** – added `docs/prompt-guidelines/` with guidelines for prompt engineering work, including Claude-specific and GPT-specific supplements. Referenced from CLAUDE.md
- **Guardrails** – added en dash (–) preference over em dash (–) rule

---

## [0.8.1] – 2026-03-24

### Changed
- **`exec-plan` / `exec-plan-team` configurable review modes** – both plan execution skills now accept `--review-mode per-story|none|full-plan`. Default behavior remains per-story `review-gap`; `none` skips automated review for manual user follow-up; `full-plan` skips per-story review and runs a single final `review-gap` against `plan.md` with remediation

---

## [0.8.0] – 2026-03-24

### Added
- **`spec-plan` skill** – new skill that batch-creates FIS specs for all stories in a plan using parallel sub-agents (opus model) with wave-ordered execution and configurable concurrency (default 5, max 10). Includes a **cross-cutting review** step that detects inter-story issues: overlapping scope, inconsistent ADRs, missing integration seams, dependency gaps, naming inconsistencies, and duplicate work. Can be used standalone (enables human review gate before execution) or delegated by `exec-plan` / `exec-plan-team`
- **STATE.md lifecycle integration** – `exec-plan`, `exec-plan-team`, `exec-spec`, `plan`, `triage`, and `quick-implement` now read and/or write STATE.md via `andthen:ops`. Previously, `ops` had Read State and Update State operations but no skill triggered them – STATE.md was effectively orphaned
- **`exec-plan` / `exec-plan-team` full state tracking** – read STATE.md at start for session continuity context; update phase/status at each phase transition; update active stories after each story completes; write blockers on failure; write session continuity note at completion or interruption
- **`exec-spec` active-story signaling** – sets active story to "In Progress" at implementation start (Step 1) and marks it Done at completion (new Step 5d), enabling faster session recovery if interrupted
- **`plan` state context and initialization** – reads STATE.md during requirements analysis for current phase/blockers/decisions context; initializes STATE.md with Phase 1 after plan creation; suggests STATE.md in follow-up actions
- **`triage` bidirectional blocker management** – reads STATE.md for investigation context (Step 1.3); adds discovered Critical/High issues as blockers (Step 3.4); removes resolved blockers and restores "On Track" status after fixes (Step 5.4)
- **`quick-implement` session note** – adds lightweight completion note to STATE.md
- **`ops` new fields** – `status` (On Track / At Risk / Blocked), `decision` (timestamped entry), `active-story` expanded to support table rows with status/FIS columns, `blocker remove` for clearing resolved blockers
- **`ops` maintenance rules** – automatic trimming on every write: remove Done rows from Active Stories, keep last 10 Session Continuity Notes and Recent Decisions

### Changed
- **`exec-plan` delegates spec creation to `spec-plan`** – per-story pipeline simplified from 3 stages (spec → exec-spec → review-gap) to 2 stages (exec-spec → review-gap). All specs for each phase are pre-generated via `andthen:spec-plan --phase {N}` before implementation begins, replacing inline JIT spec creation. Sub-agents now use `model: "sonnet"` only (spec quality handled by spec-plan's opus sub-agents)
- **`exec-plan-team` delegates spec creation to `spec-plan`** – Step 3 (Generate Specs) replaced from inline parallel sub-agent spawning to a single `andthen:spec-plan --phase {N}` delegation. Eliminates duplicated spec-generation logic between exec-plan and exec-plan-team
- **`ops` STATE.md format reconciled** with `templates/project-state-templates.md` – replaced divergent `## Current State` bullet format with canonical `## Current Phase` / `## Active Stories` table structure matching what `init` creates
- **STATE.md template** – added `Last Updated` timestamp field

### Fixed
- **`spec` artifact chaining from `clarify`** – `spec` Step 0 now explicitly detects `requirements-clarification.md` in a directory argument (output from `andthen:clarify`), consuming clarified requirements, design decisions, edge cases, and wireframes as the feature request. Skips redundant discovery phases. Previously, the `clarify → spec` handoff in the single-feature workflow had no explicit contract – `plan` had artifact chaining but `spec` did not
- **`spec` FIS output co-location** – FIS files are now co-located with their input artifacts: directory input → FIS inside directory (e.g. `docs/specs/data-export/data-export.md`), plan story → FIS in plan directory. Previously, FIS was always written to the specs root regardless of input source, breaking the feature-directory convention used by `clarify` and `plan`
- **`exec-plan-team` race condition prevention** – added explicit gotcha that only the orchestrator writes STATE.md; parallel implementers and reviewers must not touch it



---

## [0.7.3] – 2026-03-22

### Changed
- **Cross-skill references standardized** – all 12 skill files with cross-references now use consistent, explicit patterns:
  - Bare skill names (`plan`, `spec`, `design-system`) replaced with fully qualified `andthen:` prefix
  - Ambiguous references now include explicit "skill" or "agent" noun (e.g., "run the `andthen:spec` skill", "delegate to the `andthen:build-troubleshooter` agent")
  - User-facing follow-up sections now include `/` and `$` invocation examples (e.g., `/andthen:spec story S01 of path/to/plan.md`)
  - Sub-agent prompt templates standardized to "Run the `andthen:xxx` skill" pattern
  - `review-doc` "command" → "skill" terminology fix

---

## [0.7.2] – 2026-03-22

### Added
- **Execution groups in spec and exec-spec** – FIS template and spec skill now organize tasks into execution groups (clusters of related tasks executed by a single sub-agent). exec-spec refactored from per-task to per-group delegation with Group Input/Result Templates and inter-group context relay
- **UI design contract gate** (`exec-spec` Step 1.7) – auto-generates a UI-SPEC.md design contract when FIS contains frontend work, sourced from FIS, project design system, and UX guidelines
- **Post-Completion learnings** in `exec-plan` and `exec-plan-team` – both plan execution skills now update LEARNINGS.md after all phases complete, capturing cross-story insights
- **Helper scripts** in `exec-plan-team` – added `check-stubs.sh`, `check-wiring.sh`, `verify-implementation.sh` references (consistent with other execution skills)

### Changed
- **Status updates are now REQUIRED GATES** – `exec-spec` (5b, 5c), `exec-plan` (2c), `exec-plan-team` (6f) all enforce plan/FIS status updates as gate conditions, not optional post-completion cleanup. Addresses observed failure mode where agents skip end-of-document instructions under context exhaustion
- **ops fork context documented for callers** – all three execution skills now include re-read verification after `andthen:ops` invocation (ops runs in fork context; file modifications may not be visible in caller's state)
- **ops uses Project Document Index** for STATE.md path resolution instead of hardcoded `docs/STATE.md`
- **ops checkbox verification clarified** – now checks evidence of completion rather than re-running full 4-dimension verification (avoids redundant work when called by exec-spec)
- **Severity tier mapping** in `exec-spec` TV04 – explicit mapping from review-code tiers (CRITICAL/HIGH/SUGGESTIONS) to remediation tiers (CRITICAL/HIGH/MEDIUM)
- **map-codebase reads project learnings** – added LEARNINGS.md reading instruction for contextualizing codebase analysis

### Fixed
- **exec-plan missing `check-wiring.sh`** in helper scripts section (consistency with exec-spec)
- **Gotcha added** to all three execution skills warning about status updates being dropped under context exhaustion

---

## [0.7.1] – 2026-03-21

### Changed
- **Review reports co-locate with targets** – all 5 review skills (`review-code`, `review-gap`, `review-doc`, `review-council`, `review-council-team`) now place reports alongside the review target instead of always under `.agent_temp/reviews/`. Resolution priority: spec/FIS directory (if related) → target directory → Agent Temp fallback
- **Configurable Agent Temp directory** – added `Agent Temp` row to the Project Document Index template, allowing projects to override the default `.agent_temp/` path for temporary agent output (reviews, research, QA)

### Fixed
- **BREAKING: Export prefix reverted from `andthen.` to `andthen-`** – The dot in `andthen.` was incompatible with Codex CLI's `$` sigil parser regex (`[a-zA-Z0-9_\-:]`), which does not include `.`. This caused explicit `<skill>` injection to silently fail for all 22 exported skills, forcing the model to read SKILL.md files from disk via tool calls (weakest invocation path). Empirically verified: zero `<skill>` injections occurred across 784 Codex sessions with dot-prefixed names. Reverting to hyphen (`andthen-`) restores Codex's explicit skill injection. Users must re-run `./scripts/install-skills.sh` after upgrading.
- **Research report added** – `docs/research/codex-skill-instruction-following.md` documents the full root cause analysis comparing Codex CLI and Claude Code skill injection architectures

---

## [0.7.0] – 2026-03-20

### Added
- **Gotchas sections** in all 22 SKILL.md files – fixed operational knowledge surfaced near the top of each skill (2-5 entries per skill covering known failure modes)
- **LEARNINGS.md integration** – 5 skills now read project learnings at start (`exec-spec`, `triage`, `spec`, `review-gap`, `review-code`); 3 skills append significant findings after execution (`triage`, `review-gap`, `exec-spec`)
- **Orchestrator pattern** for context-heavy skills – `review-code`, `triage`, and `spec` now delegate heavy work to sub-agents to preserve workflow context; `review-gap` orchestrator enhanced with stub/wiring delegation
- **Portable shared scripts** in `plugin/scripts/` – `check-stubs.sh`, `check-wiring.sh`, `run-security-scan.sh`, `verify-implementation.sh` for automated verification (used by review-gap, exec-spec, exec-plan, review-code)

### Changed
- **Unified `andthen:` namespace** – removed `name:` frontmatter override from all 22 SKILL.md files. Skills now use the natural plugin namespace (`andthen:<skill>`), consistent with agents (`andthen:<agent>`). The portable `andthen.` prefix is now only used when exporting for non-Claude Code agents via `install-skills.sh`
- **`install-skills.sh` rewrites skill references** – exported skills have `andthen:` cross-references rewritten to the portable `andthen.` prefix, alongside the existing reference path rewriting
- **CLAUDE.md updated** – added "How Skills Work" section (Project Document Index discovery, skill anatomy, shared references, external plugin dependencies), expanded project structure, updated skill invocation docs
- **Descriptions as triggers** – 10 skills rewritten with natural-language trigger phrases for better model matching (`exec-spec`, `review-gap`, `review-council`, `clarify`, `spec`, `trade-off`, `triage`, `map-codebase`, `e2e-test`, `ops`)
- **Reduced railroading** – `plan` requirements discovery condensed from 20+ individual questions to intent + constraints format; `triage` 5 Whys analysis condensed to single directive

### Fixed
- **Removed `context: fork` from orchestrator skills** – `review-code` and `e2e-test` no longer use `context: fork` because forked sub-agents cannot spawn nested sub-agents, which breaks the orchestrator pattern. `ops` and `review-doc` retain `context: fork` (no sub-agent needs)
- **Helper scripts made concurrency-safe** – all scripts now use `mktemp` with cleanup traps instead of fixed `/tmp` paths; eliminates race conditions under parallel sub-agent execution
- **`check-wiring.sh` inspects dirty worktrees** – now checks staged, unstaged, and untracked files (not just committed diffs); supports both file and directory path inputs
- **`verify-implementation.sh` strict exit codes** – stub and wiring findings now cause non-zero exit (previously treated as warnings); delegates to `check-stubs.sh` when available; removed unused `--base-branch` option
- **`check-stubs.sh` excludes docs by default** – markdown, templates, and documentation directories excluded to reduce false positives; `--include-docs` flag for full scan
- **Installer exports shared scripts** – `install-skills.sh` now copies `plugin/scripts/` alongside `plugin/references/` and rewrites `${CLAUDE_PLUGIN_ROOT}/scripts/` and `${CLAUDE_PLUGIN_ROOT}/references/` paths in all exported `.md` files (including nested subdirectories)
- **Installer filters `.DS_Store`** – macOS metadata files no longer included in exported bundles
- **CLAUDE.md skill anatomy corrected** – removed stale `name` reference from frontmatter documentation

---

## [0.6.4] – 2026-03-20

### Changed
- **`review-gap` clarified as implementation review** – description, input interpretation, and workflow now explicitly frame the skill as comparing current code/worktree against requirements baselines. New Step 0 ("Resolve Review Target") locates the implementation target before analysis begins. Added concrete examples showing correct usage vs. `review-doc`. Multi-repo workspace resolution with sensible fallback when no workspace metadata exists.

---

## [0.6.3] – 2026-03-19

### Changed
- **Plan skill: PRD responsibility explicit** – description, title, and OpenAI agent display name now clearly state PRD creation as a primary responsibility (not just an implicit prerequisite)
- **"AndThen -" prefix on all OpenAI display names** – consistent `"AndThen - <Skill>"` branding across all `openai.yaml` agent configs
- **`review-gap` input interpretation guardrails** – new "Input Interpretation" section clarifies that documents passed as arguments are comparison baselines (requirements sources), not the review target. Stops early if no implementation exists to compare against
- **Workflow diagrams corrected** – `review-gap --doc` → `review-doc` in README and plugin README pipeline diagrams
- **Model effort selection guide** – updated `review-gap` description to reflect its focused scope (gap analysis against requirements, no longer doc/PR review modes)
- **Triage OpenAI agent metadata** – display name and description updated to match the skill's current name and scope (`"Triage & Fix Issues"`)
- **CLAUDE.template.md** – expanded guideline trigger wording to include "code exploration, architecture and solution design"

### Fixed
- **`allow_implicit_invocation: true` policy** added to OpenAI agent skill configs – this is a workaround for an apparent bug in Codex.
- **Argument-hint quoting** – all `argument-hint` values in SKILL.md frontmatter now properly quoted
- **`install-skills.sh` reference path rewriting** – installed skills now rewrite `plugin/references/` paths to sibling `<prefix>references/` paths so references resolve correctly outside the repo

---

## [0.6.2] – 2026-03-17

### Added
- **Semgrep integration in security reviews**: `review-code` Security Review phase now includes automated Semgrep scanning via Claude Code plugin (`semgrep/mcp-marketplace`), CLI, or MCP tools – running in parallel with `/security-review`. All tools optional; graceful fallback to manual checklist review
- **Automated Scanning section in Security Review Checklist**: New checklist section with Semgrep triage steps, config recommendations by focus area (`p/security-audit`, `p/owasp-top-ten`, `p/secrets`), and other tool references
- **Security Sentinel uses Semgrep**: `review-council` and `review-council-team` Security Sentinel role now runs Semgrep scans on changed files when available

---

## [0.6.1] – 2026-03-17

### Changed
- **`init` offers UBIQUITOUS_LANGUAGE.md**: Added domain glossary to the optional document checklist under a new "Domain" category, with a hint to use `andthen.ubiquitous-language` for richer generation

---

## [0.6.0] – 2026-03-17

### Added
- **Ubiquitous Language skill** (`ubiquitous-language`): Extract and maintain a domain glossary (`UBIQUITOUS_LANGUAGE.md`) from codebase and documentation. Supports `--update` mode for incremental glossary maintenance. Integrates with DDD principles throughout the pipeline
- **UL pipeline integration**: Domain language awareness woven into `clarify` (term extraction), `spec` (canonical terms in FIS), `plan` (canonical terms in stories), `exec-spec` (sub-agents receive UL context, TV01 checks terminology), `review-code` (domain language checklist), and `review-gap` (terminology drift detection)
- **Domain Language Review Checklist** (`review-code`): New `DOMAIN-LANGUAGE-REVIEW-CHECKLIST.md` covering terminology consistency, domain model alignment, and new term detection
- **"Design It Twice" in trade-off** (`trade-off`): New optional Phase 1.5 spawns 3+ parallel sub-agents with contrasting architectural constraints to generate radically different designs before evaluation. Synthesizes findings in prose, not tables
- **Triage investigation mode** (`triage`): `--plan-only` flag stops after root cause analysis and outputs a structured fix plan instead of implementing fixes. `--to-issue` publishes the plan as a GitHub issue
- **TDD Lite** (`spec`, `exec-spec`): FIS template gains "Test-Implementation Pairing" section mapping tests to implementation tasks. `exec-spec` Step 2 directs sub-agents to write paired tests before implementing (red-green rhythm by structure)
- **Vertical slicing** (`plan`, `spec`): "Vertical" added as first story principle – stories cut through all layers end-to-end. Phase template restructured around tracer-bullet first phase. FIS template adds vertical-slice task ordering guidance
- **GitHub issue output** (`spec`, `plan`, `review-gap`, `review-code`): `--to-issue` flag publishes skill output as a GitHub issue. `review-gap` and `review-code` also support `--to-pr <number>` for PR comments
- **`UBIQUITOUS_LANGUAGE.md` template**: Added to project Document Index and `project-state-templates.md` as a standard project file
- **DDD guidelines expanded**: "Ubiquitous Language in Practice" subsection added to `DEVELOPMENT-ARCHITECTURE-GUIDELINES.md` with actionable guidance on domain naming, glossary maintenance, and ambiguity resolution

### Changed
- **Extras prefix removed**: All `extras-` prefixed skills renamed – `extras-quick-implement` → `quick-implement`, `extras-design-system` → `design-system`, `extras-wireframes` → `wireframes`, `extras-refactor` → `refactor`, `extras-review-council` → `review-council`, `extras-review-council-team` → `review-council-team`, `extras-map-codebase` → `map-codebase`
- **`extras-troubleshoot` → `triage`**: Renamed with both prefix removal and base name change to better reflect systematic investigation capability
- **Triage skill description**: Updated to mention investigation, diagnosis, and fix modes
- **Portable `andthen.` skill prefix**: All skills now use `name: andthen.<skill>` in SKILL.md frontmatter (e.g., `andthen.spec`, `andthen.review-code`). Leverages Claude Code bug [#22063](https://github.com/anthropics/claude-code/issues/22063) – the `name:` field bypasses the plugin namespace, registering skills as `/andthen.spec` (portable dot notation) instead of `/andthen:andthen.spec`. Cross-references within skills use `andthen.<skill>` for skills and `andthen:<agent>` for agents (Claude Code-specific)
- **`install-codex.sh` → `install-skills.sh`**: Renamed for clarity. Default prefix changed from `andthen-` to `andthen.` to match the new naming convention
- **Invocation docs updated**: Skills invoked as `/andthen.<skill>` in Claude Code, `$andthen.<skill>` or `/andthen.<skill>` in Codex and other agents

---

## [0.5.0] – 2026-03-17

### Changed
- **Commands → Skills migration**: All 17 commands (9 core + 8 extras) converted to the skills format (`SKILL.md` in dedicated directories). Commands and skills are now unified under `plugin/skills/`. The `plugin/commands/` directory has been removed
- **Extras prefix**: Extras skills now use an `extras-` prefix in directory and skill name (e.g., `extras-quick-implement`, `extras-wireframes`, `extras-review-council`). In Claude Code: `/andthen:extras-quick-implement`
- **Skill names simplified**: Removed `andthen-` prefix from `name` field in existing skills (`andthen-review-code` → `review-code`, `andthen-review-doc` → `review-doc`, `andthen-e2e-test` → `e2e-test`, `andthen-ops` → `ops`). Claude Code plugin namespacing (`/andthen:<skill>`) provides the vendor scope
- **FIS template extracted** (`spec`): The inline FIS template (~225 lines) moved to `templates/fis-template.md` within the skill directory, leveraging the skills directory structure for supporting files
- **Codex install script**: Rewritten for skills-only workflow. Default destination changed from `~/.codex/prompts` + `~/.codex/skills` to `~/.agents/skills/` (the emerging cross-agent standard). The `--prompts-dir` option has been removed

### Added
- **OpenAI Codex metadata** (`agents/openai.yaml`): Every skill now includes an `agents/openai.yaml` with `display_name`, `short_description`, and `allow_implicit_invocation` policy for Codex compatibility
- **Cross-agent portability**: Skills follow the open agent skills standard (`SKILL.md` + optional `agents/`, `templates/`, `scripts/`, `references/`), compatible with Claude Code, Codex CLI, and other agents that scan `~/.agents/skills/`

---

## [0.4.0] – 2026-03-16

### Added
- **Goal-backward planning** (`plan`): New "Goal-Backward Analysis" step works backward from desired outcomes before defining stories – produces Must-be-TRUE statements that become primary acceptance criteria
- **Wave-based parallelization** (`plan`, `exec-plan`, `exec-plan-team`): Stories are pre-assigned to execution waves (W1, W2, W3...) during planning; execution commands consume wave assignments for cleaner parallel orchestration without runtime dependency analysis
- **Deep verification – Nyquist Rule** (`spec`, `exec-spec`, `review-gap`): Verification now checks 4 dimensions (Exists, Substantive, Wired, Functional) instead of just existence; stub detection and wiring checks catch TODOs, placeholders, and unconnected components
- **Verification patterns reference** (`plugin/references/verification-patterns.md`): Comprehensive reference with stub detection patterns, wiring check commands, and the Nyquist verification principle
- **`init` command**: Interactive project setup – detects current state (new project, partial setup, brownfield) and fills gaps non-destructively. Generates CLAUDE.md from template, creates selected document types, copies guidelines, and integrates with `map-codebase` for existing codebases
- **`map-codebase`** (extras): Brownfield codebase analysis command – spawns parallel sub-agents to produce STACK.md, ARCHITECTURE.md, CONVENTIONS.md, and a discovered requirements document that feeds directly into `/andthen:plan`
- **`andthen-ops` skill**: Deterministic operations for state management (STATE.md, plan.md status, FIS checkboxes), git conventions (commit messages, branch naming, changelog entries), and progress tracking (summary, stale detection)
- **UI Design Contract gate** (`exec-spec`): New Step 1.7 auto-generates a UI-SPEC.md design contract (spacing, typography, colors, components, breakpoints) when frontend work is detected, ensuring visual consistency across sub-agents
- **Project state templates** (`templates/project-state-templates.md`): Starter templates for STATE.md, PRODUCT-BACKLOG.md, ROADMAP.md, ARCHITECTURE.md, CONVENTIONS.md, LEARNINGS.md, and STACK.md
- **Project Document Index** (`templates/CLAUDE.template.md`): Seven new optional document rows – State, Product Backlog, Roadmap, Architecture, Conventions, Learnings, Stack

### Changed
- **`implementation-notes.md` → `LEARNINGS.md`**: Renamed and broadened scope – now captures domain knowledge, procedural knowledge, and error patterns (with deterministic vs infrastructure distinction) alongside implementation traps. Includes self-maintenance guidance (review, merge, prune). Topic-based organization instead of chronological
- **Story Catalog format** (`plan`): Table now includes a Wave column for pre-computed execution wave assignments
- **Codex installer**: Now also copies `plugin/references/` alongside prompts so non-Claude-Code agents can access verification patterns

---

## [0.3.1] – 2026-03-16

### Improved
- **`plan` – artifact chaining from `clarify`**: Plan command now detects `requirements-clarification.md` (from `/andthen:clarify`) and draft PRDs (`prd-draft.md`) in the input directory, using them as the basis for PRD creation instead of re-running full discovery
- **`plan` – new Step 1c** (PRD Creation from Existing Artifacts): Assesses coverage from prior artifacts, conducts only targeted gap-filling for genuinely missing information, and preserves existing decisions/rationale when structuring the PRD
- **`clarify` – improved handoff guidance**: Follow-up actions now explicitly guide users toward `/andthen:plan <output-directory>` for seamless artifact handoff
- **Interview guardrails** (`clarify`, `plan`): Strengthened STOP-and-WAIT instructions in discovery interviews to prevent agents from assuming answers or proceeding without user input

---

## [0.3.0] – 2026-03-15

### Added
- **Portable `exec-plan`**: New version that works across all coding agents (Claude Code, Codex CLI, Aider, Cursor, etc.) using sub-agents with sequential fallback – no longer requires Agent Teams
- **Portable `review-council`**: New version using a three-phase sub-agent pipeline (specialist reviews → Devil's Advocate challenge → Synthesis review) instead of requiring real-time Agent Teams debate
- **Agent Teams variants**: Previous Agent Teams implementations preserved as `exec-plan-team` and `review-council-team` for users who want enhanced parallelism with inter-agent coordination
- **Testing Strategy in FIS template** (`spec`): New section in the FIS template for defining test scope, key test scenarios, edge cases, and test pattern references – gives the testing agent concrete direction during `exec-spec` instead of inventing test cases from scratch
- **Test scaffolding step** (`exec-spec`): New optional Step 1.5 writes failing test skeletons from the FIS Testing Strategy before implementation begins, enabling a TDD-style workflow where tests become acceptance gates for implementation tasks
- **Structured remediation loop** (`exec-spec`): TV04 rewritten as a triage → fix → re-validate cycle that only re-runs affected validation levels, with a 3-cycle hard cap before escalating to the user
- **Review council callout** (`exec-spec`): Tip in TV04 suggesting `review-council` for high-stakes features (auth, payments, data integrity)

### Changed
- **`exec-plan` is now portable**: The default `exec-plan` command uses sub-agents (if available) with sequential fallback – works on any agent. The former Agent Teams version is now `exec-plan-team`
- **`review-council` is now portable**: The default `review-council` command uses parallel sub-agents for reviews and sequential adversarial debate phases. The former Agent Teams version is now `review-council-team`
- **Migration note**: Users of the previous `exec-plan` (which required Agent Teams) should use `exec-plan-team` for equivalent behavior. The new `exec-plan` works across all agents but uses sub-agents instead of Agent Teams coordination
- **Codex installer**: `install-skills.sh` now skips Agent Teams commands (`exec-plan-team`, `review-council-team`) since they require Claude Code. The portable `exec-plan` and `review-council` continue to be exported
- **Reduced tool-name coupling**: Agent Teams commands (`exec-plan-team`, `review-council-team`) now use intent-based language instead of hardcoded tool names, improving resilience to future API changes
- **Model selection for `exec-plan-team`**: Spec Creators use `opus` for deep reasoning; Implementers, Reviewers, and Troubleshooters use `sonnet` for fast execution

---

## [0.2.0] – 2026-03-15

### Added
- **Codex CLI installer** (`scripts/install-skills.sh`): Exports commands and skills with `andthen-`-prefixed names for Codex CLI and other agents that don't support `:` in prompt names
- **`exec-plan` – FIS existence check**: Pipeline now checks for existing FIS before creating spec tasks, skipping spec creation when one already exists – makes the pipeline resumable after partial runs
- **ElevenLabs hook enhancements**: Dynamic message generation via Claude Haiku (falls back to static messages), comma-separated voice ID support (random selection per notification), configurable model ID via `ELEVENLABS_MODEL_ID`

### Changed
- **`review` → `review-gap`**: Command renamed back to `review-gap` – the name `review` caused conflicts in some environments; all references updated across commands and documentation
- **Skills renamed** to dash-based names for cross-agent compatibility: `andthen:review-code` → `andthen-review-code`, `andthen:review-doc` → `andthen-review-doc`, `e2e-test` → `andthen-e2e-test`
- **Implementation notes** (`exec-spec`, `quick-implement`): Narrowed scope to traps, gotchas, and non-obvious patterns only – excludes information derivable from code, git history, or specs
- **ElevenLabs TTS model**: Default changed from `eleven_monolingual_v1` to `eleven_flash_v2_5`
- **Hooks docs**: Clarified settings file levels (user-level vs project-level vs local), expanded ElevenLabs setup with Claude Code `env` settings approach, free tier voice limitation note
- **README**: Updated installation section for non-Claude-Code agents to use the installer script

---

## [0.1.1] – 2026-03-13

### Added
- **Hooks**: `block-dangerous-commands.py` (blocks destructive shell commands), `notify.sh` (desktop notifications), `notify-elevenlabs.sh` (voice notifications via ElevenLabs TTS), `reinject-context.sh` (re-injects CLAUDE.md after context compaction)
- **Hooks documentation**: `hooks/README.md` with installation, configuration, and full settings example

### Fixed
- **`exec-plan`**, **`plan`**: Fixed stale `review-gap` references → `review` (command was renamed but internal references were not updated)

---

## [0.1.0] – 2026-03-13

Initial release of **AndThen** – structured workflows for agentic development.

Evolved from [cc-workflows](https://github.com/tolo/claude_code_common) (v0.12.0) with a new identity, streamlined structure, and consistent naming.

### Added

**Core Commands:**
- `clarify` – Requirements discovery – from vague idea to structured requirements
- `spec` – Feature Implementation Specification generation
- `exec-spec` – FIS execution with validation loops
- `review` – Gap analysis, code review (`--doc` for document review, `--pr` for PR review)
- `plan` – PRD creation (if needed) + story breakdown (absorbs former `prd` command)
- `exec-plan` – Agent Team pipeline execution (spec → exec-spec → review per story)
- `trade-off` – Architecture decision research with evidence-based recommendations

**Extras:**
- `quick-implement` – Fast path for small features/fixes (supports `--issue` for GitHub)
- `design-system` – Design tokens and component styles
- `wireframes` – HTML wireframes for UI planning
- `refactor` – Code improvement and simplification
- `review-council` – Multi-perspective Agent Teams review (5-7 reviewers + debate)
- `troubleshoot` – Systematic issue diagnosis and fixing

**Skills:**
- `review-code` – Code review with checklists (quality, security, architecture, UI/UX)
- `review-doc` – Document review for completeness, clarity, and technical accuracy
- `e2e-test` – End-to-end browser testing for web applications

**Agents:**
- Initial specialized agents for web research, architecture decisions, QA, documentation lookup, build troubleshooting, UI/UX design, and visual validation.

**Docs:**
- Development architecture guidelines
- UX/UI guidelines
- Web development guidelines
- Critical rules and guardrails
- Model and effort selection guide

### Changed (from cc-workflows)
- **Project rename**: `cc-workflows` → `andthen`
- **Repository structure**: Flat plugin layout (`plugin/` at root) replacing nested `plugins/cc-workflows/`
- **Command renames**: `review-gap` → `review`, `trade-off-analysis` → `trade-off`
- **Command consolidation**: `prd` merged into `plan`
- **Guidelines**: Moved to `docs/guidelines/` with uppercase naming convention

### Removed (from cc-workflows)
- `exec-plan-codex` – Codex CLI delegation (may return as separate integration)
- `ui-concept` – Exploratory UI design command
- `whimsy-injector` agent
- Prompt engineering guidelines (internal/meta – not part of the workflow system)
- Hooks (standalone safety scripts – separate concern, may return later)
