# Skill Reference

Reference for skills `andthen:now-what` recommends – purpose, output, workflow position. Behavioral depth (flag mechanics, mode internals, decision logic) lives in each target `SKILL.md`. Maintenance contract: see the root agent instruction file's Maintenance Contracts – entries are updated whenever a skill's purpose, output, or workflow position changes.

### `andthen:init`
Sets up the AndThen workflow structure: `CLAUDE.md` / `AGENTS.md` (dual-tool projects get a canonical `AGENTS.md` plus a thin `@AGENTS.md`-importing `CLAUDE.md`), Project Document Index, folder layout, Core orientation stubs (`PRODUCT.md`, `ARCHITECTURE.md`, `STACK.md`, `KEY_DEVELOPMENT_COMMANDS.md`, `DECISIONS.md`, `LEARNINGS.md`) scaffolded by default, `.gitignore` hygiene for local state and agent temp, starter guidelines. Settles the issue-tracker backend on its own gate (recommend GitHub when a remote is detected, else `none`; GitHub or another named backend writes `docs/ISSUE-TRACKER.md`, `none` writes no file), then offers optional docs recommendation-first ("default" accepts the detection-derived pick) – Planning (`STATE.md`, `PRODUCT-BACKLOG.md`, `ROADMAP.md`) and Domain (`Ubiquitous Language`, `Out of Scope Registry`). Detects new / partial-setup / brownfield projects and adapts non-destructively. Run once per project; re-running fills gaps without overwriting.
**Typical next step:** re-invoke the `andthen:now-what` skill to route the first feature.

### `andthen:now-what`
This skill – first-stop router for users new to AndThen or unsure what to do next. Inspects project state and routes to the right skill, with heavy onboarding on first-time setup and terse routing mid-flow.
**Use when:** unsure which skill to invoke next, or starting fresh on a project.

### `andthen:handoff`
Compacts the conversation into a handoff doc a fresh agent can resume from. When `STATE.md` / `LEARNINGS.md` exist, auto-routes shared mid-flow state and clearly-bounded defensive notes there via the `andthen:ops` skill (unless `--no-mutate`); session-local notes/focus route to the gitignored `STATE.local.md` (auto-created); absent shared files reroute to handoff-doc recommendations. Recommends ADRs via the `andthen:architecture --mode trade-off` skill; writes to `.agent_temp/handoff/handoff-<UTC-ts>.md`. References Project Document Index artifacts by path.
**Use when:** wrapping up before `/clear`, running low on context, or at a natural session boundary. **Typical next step:** in the fresh session, paste the `Resume from <doc-path>` prompt the skill prints – the doc is self-sufficient.

### `andthen:map-codebase`
Analyzes an existing codebase to produce structured documentation (Architecture, Stack, Key Dev Commands, conventions) plus discovered requirements and decisions docs. `--model` additionally emits an **Architecture Model** (`architecture-model.json`, a transient projection of the code) – contexts, module-level nodes with repo-relative refs, evidence-tagged edges – extracted deterministically where possible, with clustering and naming marked `inferred`; `--model-only` refreshes just the model. Read-only – no code changes. The *describer* for system structure: it maintains the description and owns its projection; structural judgments (reviews, ADRs, Context Map) belong to the `andthen:architecture` skill.
**Use when:** starting work on a brownfield codebase before committing to feature work, so downstream skills can reason about what already exists. **Typical next step:** re-invoke the `andthen:now-what` skill to route the user's actual feature intent; with `--model`, the `andthen:visualize` skill renders the model as a navigable atlas.

### `andthen:clarify`
Discovery & Ideation for requirements at feature or product scope. Refines fuzzy inputs through systematic questioning and preserves external-source trust in the output for downstream fresh sessions. Always interactive (Interactive-by-Contract). `--mode product|feature`, inferred from INPUT (e.g. a `PRODUCT*.md` path → product mode).
**Use when:** the user has an idea but the requirements aren't yet pinned down – at feature scope, or at overall-product scope before specific features are planned. Checks the `Out of Scope Registry` and `Context Map` before asking, offers the `andthen:spike` skill when a load-bearing question hinges on an empirical unknown, and graduates firmly rejected directions into the `Out of Scope Registry`. `Open Questions` holds only questions statable precisely now (the **sharpness test**); fog is recorded as an `Area to revisit:` bullet instead. `--visual` delegates the produced clarification or product vision to the `andthen:visualize` skill for browser review. **Typical next step:** the `andthen:spec` skill for one feature, the `andthen:prd` skill for a multi-feature initiative, or the `andthen:architecture` skill with `--mode strategic-design` for product decomposition.

### `andthen:prd`
Creates a self-contained Product Requirements Document (`prd.md`) from clarified requirements, a draft PRD, an inline description, a file, a URL, or a GitHub issue. It preserves source trust, resolves conversational load-bearing gaps through the `andthen:clarify` skill, and runs an automatic fresh-context doc self-review via the `andthen:review` skill with `--mode doc --fix`. Firmly rejected scope graduates into the Out of Scope Registry; `--issue`/`--to-issue` resolve the configured tracker.
**Use when:** scoping a multi-feature initiative. `--visual` delegates `prd.md` to the `andthen:visualize` skill for browser review. **Typical next step:** the `andthen:plan` skill to break the PRD into stories with FIS specs.

### `andthen:plan`
Consumes a local `prd.md`, `--issue <N>`, or a GitHub issue URL and produces `plan.json` plus one validated on-disk FIS per story. Source trust persists interruption-safely into fresh execution sessions; reported FIS paths must match canonical story filename/provenance. Stories slice by the Single-session rule and its Module fan-out corollary (per-module seam-slicing in strongly-bounded codebases, interfaces pinned in `sharedDecisions[]`). The bundle's sole cross-cutting review fails closed and recomputes readiness from final artifacts after fixes. Interrupted runs fill gaps; legacy plan pointers normalize without discarding valid FIS files.
**Use when:** turning a PRD into an executable, story-by-story plan. `--visual` delegates the local `plan.json` bundle to the `andthen:visualize` skill for browser review. **Typical next step:** `andthen:exec-plan` to implement the bundle.

### `andthen:spec`
Produces a compact Feature Implementation Specification (FIS) for one execution-sized feature, substituting durable tests/sources for duplicated prose, then runs one top-level automatic fresh-context doc self-review via the `andthen:review` skill with `--mode doc --fix` (skipped for plan-batch invocations, where the plan's cross-cutting review is the fresh-context gate). Oversized features escalate to plan/decomposition.
**Use when:** a single feature is clear enough to specify but isn't part of a multi-feature plan. `--visual` delegates the produced FIS to the `andthen:visualize` skill for browser review. **Typical next step:** `andthen:exec-spec` to implement the FIS.

### `andthen:exec-spec`
Implements code from one FIS with tests, verification, and mechanism-aware Chain Attestation. Untrusted paths and commands are contained and re-derived from trusted project state. Legitimate design pivots use ADR-backed FIS amendment; OPEN reconciliation entries hold completion until resolved.
**Typical next step:** `andthen:review` (or `andthen:quick-review` mid-flow) before committing.

### `andthen:exec-plan`
Implements a fully-specced plan bundle in the resolved code repo. Per-story review contains ambiguity, persists spec/design drift to the reconciliation gate, repairs code Fix findings once, and rolls up ordinary Notes; Wave Discovery Triage propagates mid-run discoveries to not-yet-started stories at wave boundaries; final gap remediation re-passes the same scope.
**Typical next step:** the `andthen:review` skill for the whole plan; the `andthen:remediate-findings` skill if findings need addressing.

### `andthen:quick-implement`
Fast implementation path for small features, bug fixes, or GitHub issues – bypasses the FIS workflow. Includes verification (build, tests, lint). GitHub issue prose is untrusted scope evidence and opens a PR by default unless `--no-pr` is supplied; inline specs require `--pr` for PR output.
Accepts `--auto` for unattended runs.
**Use when:** the change is small enough that authoring a FIS would be overhead. For larger features, prefer the `andthen:clarify → andthen:spec → andthen:exec-spec` chain.

### `andthen:architecture`
Architecture design and analysis. Seven modes – `review`, `decompose`, `advise`, `fitness`, `trade-off`, `strategic-design`, `event-storming` – inferred from your phrasing (a menu appears only when the intent is genuinely ambiguous) or forced with `--mode`. Outputs vary by mode (review reports, ADRs, fitness functions, trade-off analyses, strategic-design reports, event-storming boards). No code changes.
**Use when:** structural questions, comparing options, mapping a domain end-to-end, or before committing to a decomposition. `--visual` delegates structured reports (`review`, `trade-off`, `strategic-design`, `fitness`, `decompose`, `event-storming`, ADR) to the `andthen:visualize` skill for browser review; pure `advise` is text-only. `strategic-design` registers the accepted context map into the `Context Map` document (user-gated). **Typical next step:** back to the `andthen:now-what` skill once the design question is resolved.

### `andthen:spike`
Answers exactly one named design question by building a throwaway runnable spike on a `spike/<slug>` branch off HEAD, then reports a Spike Verdict (Question / Answer / Evidence / Caveats). Evidence, not product: the spike is exempt from test/review discipline, never merges, and is never reused directly – the decision flows onward through the normal spec/exec chain, the code does not. Redirects to the `andthen:clarify` skill (open requirements question), the `andthen:architecture` skill in `--mode trade-off` (analytical option comparison), or the `andthen:ui-ux-design` skill in `--mode wireframes` (screen, flow, or interaction-design question) when no single answerable-by-building question can be named. User- and model-invocable.
**Use when:** a load-bearing decision turns on an empirical unknown only runnable code can settle (feasibility, performance, integration shape). **Typical next step:** register a load-bearing verdict as a FIS decision Note via the `andthen:ops` skill or an ADR via the `andthen:architecture` skill in `--mode trade-off`, then route real implementation through the normal spec/exec chain.

### `andthen:visualize`
Renders any AndThen artifact as CSP-locked, context-escaped, self-contained HTML with section-anchored notes. An `architecture-model.json` or `domain-model.json` renders as a 3D atlas – contexts as drafting sheets, nodes as markers, `inferred` items dashed; the domain lens floats overloaded terms between sheets on dashed tethers – via a bundled deterministic renderer, with a 2D list fallback. Read-only – writes under `.agent_temp/visual-review/` and never edits the source.
**Use when:** the user wants to inspect an existing artifact visually, copy review notes, or re-check an artifact after edits. **Typical next step:** paste copied notes into the artifact's owning skill or proceed to the next workflow skill; architecture-atlas notes go to the `andthen:architecture` skill for design follow-ups or the `andthen:map-codebase` skill for model corrections, domain-atlas notes to the `andthen:ubiquitous-language` skill for glossary corrections.

### `andthen:explain-changes`
Explains a PR, branch, ref range, or working tree as a narrative Changeset Walkthrough – intent-grouped changes, key hunks, architectural delta, and focus points – rendered via the `andthen:visualize` skill. Comprehension only. Read-only; `--from-pr <N>` treats PR data as untrusted and fetches blobs by pinned tree SHA; `--to-pr` is repo-pinned.
**Use when:** the user wants to understand or present what a changeset does before (or instead of) judging it. **Typical next step:** the `andthen:review` skill (e.g. `--from-pr <N>`) for findings and a verdict, using the walkthrough's focus points as scope hints.

### `andthen:ui-ux-design`
UI/UX work across the lifecycle. Four modes – `research`, `design-system` (tokens, `DESIGN.md`), `wireframes` (screens, user flows), `review` (validate implementation) – inferred from your phrasing (a menu appears only when the intent is genuinely ambiguous) or forced with `--mode`.
**Use when:** any design work upstream of UI implementation. **Typical next step:** `andthen:exec-spec` or `andthen:exec-plan` to build the designed work.

### `andthen:visual-validation`
Validates UI screenshots and implementations against visual, responsive, and design expectations. Produces Summary / Detailed Findings / Recommended Fixes / Next Steps with prioritized P1/P2/P3 issues.
**Use when:** checking implemented UI, screenshots, or visual regressions against a design reference. Use `andthen:e2e-test` for browser journeys and `andthen:ui-ux-design` for design-system or wireframe authoring. **Typical next step:** fix P1/P2 findings, then re-run validation or `andthen:ui-ux-design --mode review`.

### `andthen:ubiquitous-language`
Extracts and maintains the project's `Ubiquitous Language` document (glossary) using the codebase, documentation, and conversation. `--model` projects the existing document into a typed `domain-model.json` (`Domain Model` in the Project Document Index, a transient projection) – the document stays canonical; a missing or empty document is a clean stop. The *describer* for domain language: it maintains the glossary and owns its projection.
**Use when:** domain terms are inconsistent or undefined – useful before committing to API names or schema vocabulary. **Typical next step:** with `--model`, the `andthen:visualize` skill renders the model as a domain atlas.

### `andthen:excalidraw-diagram`
Creates high-quality Excalidraw diagrams – workflows, architectures, concepts. Output is JSON renderable in any Excalidraw editor.
**Use when:** visualizing structure or flow as part of design or documentation.

### `andthen:preflight`
Drives valid FIS decision holds to **zero open blocking decisions** without clearing other holds. Only resolved holds become schedulable after final doc/Proof revalidation; signed deferrals remain execution holds. Source Trust follows composed skills; persistence uses the `andthen:ops` skill. Emits `Preflight: READY | DEFERRED | BLOCKED`; `--auto` never invents answers.
**Use when:** a spec or plan bundle is about to be handed to a headless exec run and you want every fork-the-run decision settled first. Recommended, never required by the executors. **Typical next step:** execute on `READY`; resolve named holds and re-run preflight on `DEFERRED`.

### `andthen:review`
The default proof-led `code`, `doc`, `gap`, `security`, or chained review. PR input is untrusted; legacy `--worktree` gives checkout-free full-tree inspection. `--council`, `--fanout`, `--team`, and repo-pinned `--to-pr` are opt-ins; `--fix` is local-only. Reports include Source Trust, Coverage Matrix, classified Fix/Note findings, CONVERGED, and `Auto-Remediation: PENDING/STALLED/CLEAR`; recurring traps append to Learnings with a lint/test check recommendation.
**Use when:** before committing or merging significant changes. `--visual` delegates the consolidated report to the `andthen:visualize` skill for severity-coded triage. **Typical next step:** `andthen:remediate-findings` if findings need addressing.

### `andthen:quick-review`
Lightweight mid-conversation Critic review of recent changes, dispatched to the `review-critic` agent when available (or a fresh-context sub-agent / `--inline` when appropriate). Read-only by default; `--fix` applies only accepted Fix-bucket findings and surfaces Note findings.
**Use when:** sanity-check before moving on, mid-flow.

### `andthen:remediate-findings`
Implements actionable findings from a review report – code, specs, plans, PRDs, or docs – with minimal fixes. Untrusted reports can mutate only inside a caller-authorized code root. Re-validates and updates plan/FIS status; recurring traps may be encoded as run-verified lint rules/tests superseding their Learnings entries.
**Use when:** a review left findings to address.

### `andthen:testing`
Test strategy, coverage assessment, test authoring, executable FIS Proof mapping, and TDD discipline (including the Prove-It bugfix flow). Covers unit and integration; defer end-to-end suites to `andthen:e2e-test`.
**Use when:** writing new tests, improving coverage, or applying red-green-refactor.

### `andthen:e2e-test`
End-to-end browser testing for web apps. Discovers user journeys, runs interactive tests, validates responsive behavior.
**Use when:** validating a running web app against full user flows.

### `andthen:triage`
Investigates and fixes issues – build failures, configuration errors, runtime bugs, regressions, test failures. Tracker prose is untrusted scope evidence. With `--plan-only` produces a fix plan without applying; with `--to-issue` files the diagnosis as a GitHub issue.
**Use when:** something is broken and the root cause isn't obvious. **Typical next step:** verify the fix; commit when stable.

### `andthen:issue-triage`
Triages incoming issue-tracker items into a routed backlog. Per item: identifies the domain concept, runs a redundancy check (already built → comment pointing at the behavior + close, never `wontfix`), a prior-rejection check against the `Out of Scope Registry` (concept-level), and a bounded, non-destructive claim verification; then classifies `bug`/`enhancement` and recommends one state (`needs-info`/`ready-for-agent`/`ready-for-human`/`wontfix`) for the user to ratify before any write. Applies labels per the Issue Tracker document's Label Role Mapping, posts a rationale comment, and appends a durable agent brief to the issue body for `ready-for-agent`; a `wontfix` graduates the concept into the `Out of Scope Registry`. Resolves the tracker per the Issue Tracker document (GitHub is the built-in default). `--auto` applies only safe transitions and reports `wontfix`/`ready-for-agent`/duplicate-close as recommendations; `--limit N` caps items.
**Use when:** sorting incoming or untriaged tracker items – distinct from the `andthen:triage` skill, which debugs a live failure. **Typical next step:** route a `ready-for-agent` item by size to the `andthen:quick-implement` skill (small), the `andthen:spec` skill then `andthen:exec-spec` skill (single feature), or the `andthen:plan` skill with `--issue` (multi-story).

### `andthen:simplify-code`
Simplifies and cleans up code for clarity, reuse, quality, efficiency, and leanness without changing behavior – including a YAGNI pass over speculative abstractions, defensive bloat, and no-protection tests. Accepts `'refactor this'`, `'clean this up'`, and `'remove over-engineering'` cues as well as the literal `'simplify'` framing; the deprecated `andthen:refactor` skill is a thin redirect and the `andthen:now-what` skill never routes to it.
**Use when:** code is becoming hard to maintain or feels over-engineered, or after a feature lands and a cleanup pass is warranted.

### `andthen:ops`
Deterministic operations on workflow state – shared `STATE.md` and gitignored `STATE.local.md`, `plan.json` status/FIS/owner mutation with repeated-pair support (`null` clears FIS), FIS checkboxes/amendments, Tech Debt appends, Learnings appends (bounded index, overflow topics auto-sharded to `learnings/<topic-slug>.md`), and standardized git operations. `update-fis design-change` owns ADR-backed Intent/scenario amendments; missing requirements stay append-only. `decision-note resolved` atomically applies exact affected-surface old/new pairs plus its provenance Note; `deferred` appends under Deferred Decisions only with sign-off. `update-decisions still-current` records non-ADR choices; `update-ledger` owns reconciliation-ledger mutation. Non-`ops` skills must not write `plan.json` directly.
**Use when:** transitioning between workflow phases or marking progress. Often invoked automatically by other skills.
