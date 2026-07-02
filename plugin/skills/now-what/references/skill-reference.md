# Skill Reference

Reference for skills `andthen:now-what` recommends – purpose, output, workflow position. Behavioral depth (flag mechanics, mode internals, decision logic) lives in each target `SKILL.md`. Maintenance contract: see the root agent instruction file's Maintenance Contracts – entries are updated whenever a skill's purpose, output, or workflow position changes.

### `andthen:init`
Sets up the AndThen workflow structure: `CLAUDE.md` / `AGENTS.md`, Project Document Index, folder layout, Core orientation stubs (`PRODUCT.md`, `ARCHITECTURE.md`, `STACK.md`, `KEY_DEVELOPMENT_COMMANDS.md`, `DECISIONS.md`, `LEARNINGS.md`) scaffolded by default, optional Planning docs (`STATE.md`, `PRODUCT-BACKLOG.md`, `ROADMAP.md`) on user opt-in, `.gitignore` hygiene for local state and agent temp, starter guidelines. Detects new / partial-setup / brownfield projects and adapts non-destructively. Run once per project; re-running fills gaps without overwriting.
**Typical next step:** re-invoke `andthen:now-what` to route the first feature.

### `andthen:now-what`
This skill – first-stop router for users new to AndThen or unsure what to do next. Inspects project state and routes to the right skill, with heavy onboarding on first-time setup and terse routing mid-flow.
**Use when:** unsure which skill to invoke next, or starting fresh on a project.

### `andthen:handoff`
Compacts the conversation into a handoff doc a fresh agent can resume from. When `STATE.md` / `LEARNINGS.md` exist, auto-routes shared mid-flow state and clearly-bounded defensive notes there via the `andthen:ops` skill (unless `--no-mutate`); session-local notes/focus route to the gitignored `STATE.local.md` (auto-created); absent shared files reroute to handoff-doc recommendations. Recommends ADRs via the `andthen:architecture --mode trade-off` skill; writes to `.agent_temp/handoff/handoff-<UTC-ts>.md`. References Project Document Index artifacts by path.
**Use when:** wrapping up before `/clear`, running low on context, or at a natural session boundary. **Typical next step:** in the fresh session, paste the `Resume from <doc-path>` prompt the skill prints – the doc is self-sufficient.

### `andthen:map-codebase`
Analyzes an existing codebase to produce structured documentation (Architecture, Stack, Key Dev Commands, conventions) plus discovered requirements and decisions docs. Read-only – no code changes.
**Use when:** starting work on a brownfield codebase before committing to feature work, so downstream skills can reason about what already exists. **Typical next step:** re-invoke `andthen:now-what` to route the user's actual feature intent.

### `andthen:clarify`
Discovery & Ideation for requirements at feature or product scope. Refines fuzzy inputs into clarified requirements through systematic questioning – gaps, edge cases, scope boundaries, alternatives the user hadn't considered. Always interactive (Interactive-by-Contract). `--mode product|feature`, inferred from INPUT (e.g. a `PRODUCT*.md` path → product mode).
**Use when:** the user has an idea but the requirements aren't yet pinned down – at feature scope, or at overall-product scope before specific features are planned. `--visual` delegates the produced clarification or product vision to the `andthen:visualize` skill for browser review. **Typical next step:** `andthen:spec` for one feature, `andthen:prd` for a multi-feature initiative, or (product mode) `andthen:architecture --mode strategic-design` for bounded-context decomposition.

### `andthen:prd`
Creates a self-contained Product Requirements Document (`prd.md`) from clarified requirements, a draft PRD, an inline description, a file, a URL, or a GitHub issue. Conversationally, it resolves load-bearing gaps by invoking the `andthen:clarify` skill inline rather than assuming them, and runs an automatic fresh-context doc self-review via the `andthen:review` skill with `--mode doc --fix` before finishing.
**Use when:** scoping a multi-feature initiative. `--visual` delegates `prd.md` to the `andthen:visualize` skill for browser review. **Typical next step:** `andthen:plan` to break the PRD into stories with FIS specs.

### `andthen:plan`
Consumes an existing local `prd.md`, `--issue <N>`, or a GitHub issue URL and produces the full plan bundle: `plan.json` (typed story manifest, canonical) plus one on-disk FIS file per story. Re-running on an interrupted bundle fills missing FIS files; re-running on a legacy `plan.md`-only bundle migrates to `plan.json` and preserves existing FIS files.
**Use when:** turning a PRD into an executable, story-by-story plan. `--visual` delegates the local `plan.json` bundle to the `andthen:visualize` skill for browser review. **Typical next step:** `andthen:exec-plan` to implement the bundle.

### `andthen:spec`
Produces a single Feature Implementation Specification (FIS) for one execution-sized feature, then runs automatic fresh-context doc self-review via the `andthen:review` skill with `--mode doc --fix`. If the feature exceeds size thresholds, escalates – standalone inputs route to the `andthen:prd → andthen:plan → andthen:exec-plan` chain; plan-story inputs go upstream for plan decomposition.
**Use when:** a single feature is clear enough to specify but isn't part of a multi-feature plan. `--visual` delegates the produced FIS to the `andthen:visualize` skill for browser review. **Typical next step:** `andthen:exec-spec` to implement the FIS.

### `andthen:exec-spec`
Implements code from a single FIS – code, tests, and verification. Honors the FIS contract (Required Context, Acceptance Scenarios, Structural Criteria), runs intent/gap review alongside code review, and uses mechanism-aware Chain Attestation before completion. Legitimate design pivots route to ADR-backed FIS amendment rather than silent divergence; when an amendment leaves an upstream doc stale, opens a reconciliation-ledger entry and emits a recommend-only As-Built Upstream Reconciliation.
**Typical next step:** `andthen:review` (or `andthen:quick-review` mid-flow) before committing.

### `andthen:exec-plan`
Implements a fully-specced plan bundle story-by-story. Runs a fixed pipeline per story (`exec-spec` + `quick-review`) plus a final gap review (scoped to completed stories on partial runs, with a warning naming unreviewed ones) and a consolidated As-Built Upstream Reconciliation rollup at completion.
**Typical next step:** `andthen:review` for the whole plan; `andthen:remediate-findings` if findings need addressing.

### `andthen:quick-implement`
Fast implementation path for small features, bug fixes, or GitHub issues – bypasses the FIS workflow. Includes verification (build, tests, lint). GitHub issue input opens a PR by default unless `--no-pr` is supplied; inline specs require `--pr` for PR output.
Accepts `--auto` for unattended runs.
**Use when:** the change is small enough that authoring a FIS would be overhead. For larger features, prefer the `andthen:clarify → andthen:spec → andthen:exec-spec` chain.

### `andthen:architecture`
Architecture design and analysis. Seven modes – `review`, `decompose`, `advise`, `fitness`, `trade-off`, `strategic-design`, `event-storming` – inferred from your phrasing (a menu appears only when the intent is genuinely ambiguous) or forced with `--mode`. Outputs vary by mode (review reports, ADRs, fitness functions, trade-off analyses, strategic-design reports, event-storming boards). No code changes.
**Use when:** structural questions, comparing options, mapping a domain end-to-end, or before committing to a decomposition. `--visual` delegates structured reports (`review`, `trade-off`, `strategic-design`, `fitness`, `decompose`, `event-storming`, ADR) to the `andthen:visualize` skill for browser review; pure `advise` is text-only. **Typical next step:** back to `andthen:now-what` once the design question is resolved.

### `andthen:visualize`
Renders any AndThen artifact – PRD, `plan.json`, FIS, requirements-clarification, product vision, review report (any lens), changeset walkthrough, architecture review / trade-off / strategic-design / fitness / decompose / event-storming report, or ADR – as a self-contained HTML review surface with section-anchored notes. Read-only – writes HTML under `.agent_temp/visual-review/` and never edits the source artifact.
**Use when:** the user wants to inspect an existing artifact visually, copy review notes, or re-check an artifact after edits. **Typical next step:** paste copied notes into the owning skill (`andthen:prd`, `andthen:plan`, `andthen:spec`, `andthen:clarify`, `andthen:review`, `andthen:explain-changes`, or `andthen:architecture`) or proceed to the next workflow skill.

### `andthen:explain-changes`
Explains a PR, branch, ref range, or working tree as a narrative Changeset Walkthrough – changes grouped by intent, ordered by conceptual importance, with key diff hunks, per-file risk tags, an architectural-delta module map, and reviewer focus points – rendered as an interactive HTML tour via the `andthen:visualize` skill. Comprehension only: no findings, no verdict. Read-only; `--from-pr <N>` reads via `gh`, `--to-pr` posts the walkthrough as a PR comment.
**Use when:** the user wants to understand or present what a changeset does before (or instead of) judging it. **Typical next step:** `andthen:review` (e.g. `--from-pr <N>`) for findings and a verdict, using the walkthrough's focus points as scope hints.

### `andthen:ui-ux-design`
UI/UX work across the lifecycle. Four modes – `research`, `design-system` (tokens, `DESIGN.md`), `wireframes` (screens, user flows), `review` (validate implementation) – inferred from your phrasing (a menu appears only when the intent is genuinely ambiguous) or forced with `--mode`.
**Use when:** any design work upstream of UI implementation. **Typical next step:** `andthen:exec-spec` or `andthen:exec-plan` to build the designed work.

### `andthen:visual-validation`
Validates UI screenshots and implementations against visual, responsive, and design expectations. Produces Summary / Detailed Findings / Recommended Fixes / Next Steps with prioritized P1/P2/P3 issues.
**Use when:** checking implemented UI, screenshots, or visual regressions against a design reference. Use `andthen:e2e-test` for browser journeys and `andthen:ui-ux-design` for design-system or wireframe authoring. **Typical next step:** fix P1/P2 findings, then re-run validation or `andthen:ui-ux-design --mode review`.

### `andthen:ubiquitous-language`
Extracts and maintains the project's `Ubiquitous Language` document (glossary) using the codebase, documentation, and conversation.
**Use when:** domain terms are inconsistent or undefined – useful before committing to API names or schema vocabulary.

### `andthen:excalidraw-diagram`
Creates high-quality Excalidraw diagrams – workflows, architectures, concepts. Output is JSON renderable in any Excalidraw editor.
**Use when:** visualizing structure or flow as part of design or documentation.

### `andthen:preflight`
Drives a single FIS or a plan bundle to **zero open blocking decisions** before an unattended `exec-spec`/`exec-plan` run. Auto-detects the target (FIS file vs. directory with `plan.json`; ambiguous/missing → ask, or `BLOCKED:` under `--auto`). Interactive-by-Contract: detects decisions via the `andthen:review` skill (`--mode doc --inline-findings`), settles open ADRs inline via the `andthen:architecture` skill (`--mode trade-off`), routes requirements-altitude gaps to the `andthen:clarify` skill, runs its own interview on implementation-blocking decisions, and persists each resolution by altitude via the `andthen:ops` skill (FIS decision-Note / `DECISIONS.md` Still Current note / ADR); converged bundle stories flip to `spec-ready`. Emits a machine-stable `Preflight: READY | DEFERRED | BLOCKED` verdict; under `--auto` never interviews or fabricates – enumerates the unresolved blocking set as a signal.
**Use when:** a spec or plan bundle is about to be handed to a headless exec run and you want every fork-the-run decision settled first. Recommended, never required by the executors. **Typical next step:** `andthen:exec-spec` / `andthen:exec-plan` on `READY`/`DEFERRED`.

### `andthen:review`
The default proof-led review skill. Lenses: `code` (correctness, patterns, named smell baseline), `doc`, `gap`, `security`, `mixed` (chain) – chosen from the concerns you name ("check correctness and security"), or from the target when you don't, or forced with `--mode`; a bare "PR 42" reads that PR (read-only). `--council`, `--fanout`, `--team`, `--fix`, and `--to-pr` are explicit opt-ins, never inferred from phrasing. Each report includes a Coverage Matrix proving primary surfaces with evidence, positive proof, attempted falsifier, and result; changed tests/sign-off artifacts get explicit test-contract falsification. Critic posture is always on; findings are classified before Fix/Note routing, so mechanically-correctable defects can be fixed under `--fix` while spec/design drift routes to reconciliation. Emits CONVERGED and `Auto-Remediation: PENDING/STALLED/CLEAR` so loops branch on the auto-applicable set.
**Use when:** before committing or merging significant changes. `--visual` delegates the consolidated report to the `andthen:visualize` skill for severity-coded triage. **Typical next step:** `andthen:remediate-findings` if findings need addressing.

### `andthen:quick-review`
Lightweight mid-conversation Critic review of recent changes, dispatched to the `review-critic` agent when available (or a fresh-context sub-agent / `--inline` when appropriate). Read-only by default; `--fix` applies only accepted Fix-bucket findings and surfaces Note findings.
**Use when:** sanity-check before moving on, mid-flow.

### `andthen:remediate-findings`
Implements actionable findings from a review report – code, specs, plans, PRDs, or docs – with minimal, guideline-aligned fixes. Re-validates the result and updates plan / FIS status.
**Use when:** a review left findings to address.

### `andthen:testing`
Test strategy, coverage assessment, test authoring, and TDD discipline (Prove-It bugfix flow, FIS scenario → test mapping). Covers unit and integration; defer end-to-end suites to `andthen:e2e-test`.
**Use when:** writing new tests, improving coverage, or applying red-green-refactor.

### `andthen:e2e-test`
End-to-end browser testing for web apps. Discovers user journeys, runs interactive tests, validates responsive behavior.
**Use when:** validating a running web app against full user flows.

### `andthen:triage`
Investigates and fixes issues – build failures, configuration errors, runtime bugs, regressions, test failures. With `--plan-only` produces a fix plan without applying; with `--to-issue` files the diagnosis as a GitHub issue.
**Use when:** something is broken and the root cause isn't obvious. **Typical next step:** verify the fix; commit when stable.

### `andthen:simplify-code`
Simplifies and cleans up code for clarity, reuse, quality, and efficiency without changing behavior. Accepts `'refactor this'` and `'clean this up'` cues as well as the literal `'simplify'` framing; the deprecated `andthen:refactor` skill is a thin redirect to this one and is never routed to from `andthen:now-what`.
**Use when:** code is becoming hard to maintain, or after a feature lands and a cleanup pass is warranted.

### `andthen:ops`
Deterministic operations on workflow state – shared `STATE.md` and gitignored `STATE.local.md` (`note`/`focus` route local; other fields shared), `plan.json` (canonical mutator of `stories[].status`/`fis`/`owner`; `read-state` derives Active Stories from it when one exists), FIS checkboxes, audited FIS amendments, decision notes, Tech Debt and `LEARNINGS.md` appends, standardized commits. `update-fis design-change` amends FIS Intent/scenario text only when backed by an ADR or ADR-creation action; missing requirements stay on the append-only `discovered-requirements` path. `update-fis decision-note <key> <resolved|deferred>` records a preflight decision (resolved → `## Implementation Observations`; deferred → `## Deferred Decisions`, requiring `Signed-off-by:`); `update-decisions still-current <topic>` appends a load-bearing non-ADR choice to the `DECISIONS.md` `## Still Current` registry. `update-ledger` (`add`/`reconcile`/`withdraw`/`bump-recurrence`/`override-close`) is the deterministic single-document mutator for the reconciliation ledger. Non-`ops` skills must not write `plan.json` directly.
**Use when:** transitioning between workflow phases or marking progress. Often invoked automatically by other skills.
