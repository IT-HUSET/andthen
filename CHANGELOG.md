# Changelog

All notable changes to **AndThen** are documented here, in a brief and concise format.
Follows [Semantic Versioning](https://semver.org/) and [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.


---

## [1.0.1]

---

## [1.0.0] – 2026-11-05

Changes since 0.40.4; each `v1.0.0-rc.N` tag's CHANGELOG.md keeps that candidate's notes.

### Added
- **Four skills, 21 in all.** `decide` interviews you over a solution's technical choices and writes ADRs, each labelled a one-way or two-way door ([ADR-025](docs/adrs/ADR-025-decide-skill.md)). `ship` closes out a branch and opens its pull request ([ADR-026](docs/adrs/ADR-026-ship-skill.md)). `domain` models subdomains, bounded contexts, the glossary, and event storms into the `Domain Map` and `Ubiquitous Language` documents ([ADR-029](docs/adrs/ADR-029-domain-skill-and-domain-map.md)). `tracker` runs `publish`, `triage`, and `setup` against the issue tracker ([ADR-028](docs/adrs/ADR-028-tracker-record.md)).
- **GitHub Copilot CLI is a supported host** beside Claude Code and Codex CLI. `init` offers Copilot role agents and writes the conversation style into `~/.copilot/copilot-instructions.md`, and `scripts/andthen-plugins.py` switches release lines (`rc`, `stable`, `--path`, `--copilot-only`). CI checks that every skill loads; the evals do not cover Copilot.
- **A story reaches `done` only on executed proof.** A FIS names each proof as `<file>#<test>`, `cmd: <command>`, or `inspect: path:LINE`; `exec-plan` runs them and writes one output line into the story's `verified` in `plan.json` (schema v2).
- **`review` has four lenses and two forms beyond a report.** `code`, `gap` (implementation against its FIS), `security`, and `outcome` (the finished feature against its PRD, walked as its Target Users); `--quick` returns one pass's findings inline, and `PR 42` reviews a pull request in a scratch worktree.
- **`ui-ux-design` writes clickable mockups** into `docs/mockups/<feature>/`, built from your design system with working in-page interactions and checked for contrast, off-token values, and dead links. Wireframes go to `docs/wireframes/<feature>/`.
- **More documents skills read and write.** `Testing Strategy` (`testing --mode strategy`), `Key Dev Commands` (the `fast` and `full` tiers and a run-one-test row), `Visual Validation` (`visual-validation --mode setup`), `Domain Map`, `Issue Tracker`, and an optional `Review Policy`. The `Product` document gains Proportionality facts, which `clarify`, `decide`, `plan`, `architecture`, `domain`, and `review` size proposals against, and Product Principles for design tiebreakers.
- **Optional role agents.** `init` offers `oracle`, `implementer`, `reviewer`, and `worker` for Claude Code, Codex, and Copilot, each pinning a model and effort per task tier.
- **Example permission and sandbox settings** for Claude Code and Codex in [`permissions/`](permissions/README.md): sandbox on with no network, credentials and `.env` files hidden from commands, `git push` asking first, and `block-dangerous-commands.py` as a pre-tool hook.
- **`COOKBOOK.md`.** Task-oriented recipes (the prompt, what comes back, where to go next), how the workflow fits together, working in a team, and one worked example.

### Changed
- **Breaking: 0.x skills, flags, and files are retired with no aliases.** [`MIGRATING-FROM-0.x.md`](MIGRATING-FROM-0.x.md) has a copy-paste migration prompt and a table mapping every retired name to its 1.0 replacement.
- **The workflow is `clarify` → `plan` → `exec-plan` → `review --fix` → `ship`.** Each step ends on one paste-ready `Next (fresh session):` command, `--auto` is the only way to run unattended, and a question waits for your answer, with a recommendation, unless a line states it. `now-what` routes by inspecting project state; work on the remote's default branch starts on a feature branch.
- **`clarify` writes the PRD.** It interviews in rounds, plays the settled picture back before writing, and writes acceptance criteria as EARS rules. `--brief` stops at `intent.md`; amending a PRD whose plan has started says where the change goes. `clarify` and `decide` can list every question at once for someone else to answer.
- **`plan` writes `plan.json` plus a FIS per story, a single story included.** It sizes a written source itself, flags a story past about 12 tasks, links each story's `sourceRefs` to the PRD's `#### FRn:` sections, and writes acceptance scenarios in the domain's terms with concrete values. On a tracker item it reuses the `issue-{n}-*` directory `clarify` wrote, and a re-plan numbers new stories after the highest old ID, which published issues keep. A several-story plan closes on `exec-plan` for the first story, so each story runs in its own session.
- **`exec-plan` runs a FIS or a plan directory.** A plan run gives each ready story to a fresh subagent (`--worktree` runs independent ones in parallel), commits each story with `Story-ID:` and `Plan:` trailers, runs `simplify-code` on it, and appends what it learned to the stories still to run. A test a FIS proof already ran keeps its assertions unless they contradict the scenario. Test-first is a project convention you set in your `Testing Strategy` document or request.
- **`ship` closes out the branch.** It lands each FIS's Implementation Observations as `Learnings` bullets, asks whether to delete the plan bundle and the feature's design folders, and after one confirmation pushes and opens the PR. The body states intent, outcomes, proof, where to read closely, the change's door and blast radius, and ends on a fixed `## Ship summary`.
- **`ship` links the issues it finishes.** In both record modes it adds a closing link for the parent once the plan is ready and for each `done` or `skipped` story's child issue; under `Record: repo` it reads the children from the parent's `## Stories` checklist. A link closes only from a PR into the default branch, so for another base, such as a milestone branch, `ship` names the issues left open for you to close after the merge.
- **The issue tracker can hold a feature's record.** With `Record: tracker` in the `Issue Tracker` document, `clarify` saves the PRD to its issue, `plan` takes it back, and `ship` publishes the final issues and deletes `prd.md` with the bundle. `tracker publish` gives each story issue its intent, outcomes, and acceptance scenarios with no file or commit link, and shows what each write changes before asking once. It never unchecks a finished story or drops a checklist entry (a story removed from the plan keeps its entry, and publish names its open child for you to close) and keeps a found issue's title.
- **`tracker triage` and the Operation Table.** `tracker triage` labels and routes incoming issues, skips those carrying an `andthen-projection` line, puts its Agent Brief above that line, and sends a bug with an unknown cause to `triage`. The GitHub mapping for `list issues` is an exact-phrase body search across all states, and the Operation Table's placeholders are `<N>` (id or key), `<title>`, `<body-file>`, `<query>`, `<label>`; on a keyed tracker the parent's checklist names each child by its key (`ENG-123`), not `#<number>`.
- **`implement-fix` is the one no-spec change skill.** It takes a request, a review report, or a tracker item URL (working from its `## Agent Brief`, else its body), runs one round of re-validate, fix, verify, and re-check, and leaves the change in your working tree. A large Fix set goes to fresh `implementer` subagents, and an attended run ends on one question over each open Note, decision, and deferred finding.
- **`review` reports have one format, and a finding names every place its defect occurs.** A follow-up after fixes covers only what changed, earlier reports are input and never scope, and a report states the revision it reviewed. The code lens checks consumers a symbol search misses, production scale against an anchored cardinality, and resilience against the `Product` document's Proportionality facts.
- **`triage` questions its premise** after two failed fixes, looks for a root cause's other instances, and hands over to `oracle` once, when installed, before it stops. Traps go to `Learnings` and deferred fixes to the `Tech Debt` backlog.
- **`architecture` keeps `advise`, `review`, `decompose`, and `fitness`**, grading against Ousterhout's deep modules and weighing Locality of Behaviour. Modeling the domain is `domain`; `describe` maps the codebase, and `--model` adds the typed `architecture-model.json` under the `Models` location.
- **`visual-validation` returns a blocking verdict it has to earn.** It lists per region what differs from the reference before deciding, judges a screen against its own feature's mockup first, else its wireframe, and recaptures after a fix.
- **`testing` names tests that cannot fail** or are coupled to structure, and its Anti-Cheat Invariant binds every mode. Sociable tests are the default.
- **The Project Document Index lists only documents that exist.** `init` asks only what it cannot infer, and the first skill that writes any other document creates it and adds its entry from a template.
- **The critical-rules starter `init` offers** asks agents to think long-term, prefer deep modules, say how they know, make Boy Scout tidies, commit only their own changes by path, wait without outliving the prompt cache, and check that a reported problem still exists before fixing it. Ask `init` to update installed rules.
- **Optional hooks in `hooks/` are current.** Re-copy them: `block-dangerous-commands.py` refuses force pushes and the Windows forms of its list, and `context-hint.py` shows the session's size without spending a turn.
- **No Python needed.** `tracker publish` is skill text, and no script reads or writes `plan.json`. Tests live in a root `tests/`, so an installed plugin carries runtime files only, and CI runs the suites on ubuntu, macos, and windows.

### Removed
- **Skills**: `prd`, `spec`, `exec-spec`, `preflight`, `quick-implement`, `quick-review`, `remediate-findings`, `refactor`, `map-codebase`, `ubiquitous-language`, `issue-triage`, `explain-changes`, `excalidraw-diagram`, `e2e-test`, `merge-resolve`, and `ops`.
- **Flags and modes**: `exec-plan --tdd`, `testing --mode tdd`, `review --council` and `--mode doc`, team mode (`--team`, `--max-parallel`), the tracker transport flags (`--issue`, `--from-issue`, `--to-issue`, `--to-pr`, `--create-story-issues`), `--visual`, `--skip-review`, and `--defer-shared-writes`.
- **Files and scripts**: the 12 plugin agents and `generate-codex-agents.sh`, the `State` documents and `STATE.md`, legacy FIS execution and `plan.md`, the glossary's typed model, and `scripts/validate-plan-json.sh`.

---

## [0.40.4] – 2026-08-27

### Changed
- **`concise-critical`: substance floor, narration ban, answer-first** – concision never cuts requested detail, error output, or destructive-action confirmations; step narration ("Let me look at…") banned; conclusion-last becomes answer first / ask last; short answers stay plain prose. Codex: re-paste `developer_instructions`.

---

## [0.40.3] – 2026-08-21

### Changed
- **`concise-critical`: reference codes must be introduced** – a lead-in ties each letter to its bolded kind word before first use. Codex: re-paste `developer_instructions`.

---

## [0.40.2] – 2026-08-20

### Changed
- **"Always-on" rules/tiers renamed "always-loaded"** across docs, templates, and the `init` skill – the rules are loaded into every prompt, not running; "always-on" stays only for the review Critic sub-lens, which does run in every review.
- **CRITICAL-RULES preamble trimmed to the precedence sentence** – agent-read files don't describe themselves.

### Fixed
- **Sub-agent names stay readable.** The concision rules were leaking into identifiers ("S38r", "TDguards"): the `concise-critical` style now scopes compression to prose (names you assign stay descriptive words), and the CRITICAL-RULES delegate rule requires plain task words plus the model name in every sub-agent name. Codex: re-paste `developer_instructions`.

---

## [0.40.1] – 2026-08-19

### Changed
- **`concise-critical` output style names the AI tells it forbids** – opening/closing filler, unnamed authority, filler vocabulary, trailing "-ing" justifications, forced triads, stacked hedges – and asks for the mechanism or number instead of the adjective; a sentence that would hold for any project is cut. Reference codes now carry their kind word where used (heading or "**R1 (risk)**"), never a bare letter, and only the six standard kinds get letters – other lists number under their heading. Same rules reach Codex through `developer_instructions` – re-paste the body.
- **CRITICAL-RULES-AND-GUARDRAILS.md assumes a shared worktree** – stage by path, never whole-tree `reset`/`restore`/`stash`/`clean` or `.git/*.lock` deletion without sanction; another agent may be mid-edit.
- **CRITICAL-RULES-AND-GUARDRAILS.md tightens deliverable prose** – specs/PRDs/docs state mechanisms and numbers, not qualities (a sentence that would hold in any project is cut); dashes used sparingly (en dashes still, but prefer a period or comma).

---

## [0.40.0] – 2026-08-18

### Added
- **`concise-critical` output style – conversation-style rules at the system-prompt tier.** The plugin registers `skills/init/templates/output-styles/concise-critical.md` (critical stance, extreme concision, state-each-fact-once, plain language, conclusion last, reference codes for 3+ items) as an output style; opt in with `"outputStyle": "andthen:concise-critical"` – never forced. Codex users paste the body into `developer_instructions`.
- **`init` wires the always-on tiers at user level.** New final step, once per machine: appends CRITICAL-RULES to `~/.claude/CLAUDE.md` / `~/.codex/AGENTS.md` and sets the conversation style (`outputStyle` / Codex `developer_instructions`) on confirm – or, with **rules-only**, folds the conversation rules into the instruction files instead. Detects what is already wired, never overwrites; re-run `init` on any project to wire later. The plugin README carries a paste-prompt for wiring without init.

### Changed
- **CRITICAL-RULES-AND-GUARDRAILS.md drops the conversation-style rules** (critical stance, concision) now carried by the output style, so no rule lives in two tiers; everything sub-agents must also see – commit, attribution, date, and artifact rules – stays. The template's setup comment documents both tiers. Shell-alias system-prompt injection dropped from the wiring options.

---

## [0.39.2] – 2026-08-17

### Fixed
- **`map-codebase` merges into existing docs instead of overwriting them.** Re-runs against an existing `Stack`, `Architecture`, or `Key Dev Commands` document regenerate the derived tables (key components, integration points, stack inventories, commands) and preserve the judgment sections (system overview, data flow, key constraints), appending new items marked `(new)`; rows whose component is no longer found are flagged, not dropped. A document written to a different structure is left untouched, with the analysis written beside it as `<NAME>.discovered.md`.

---

## [0.39.1] – 2026-08-15

### Fixed
- **Review find-passes must return their findings – and stay read-only.** Find-passes now spawn as plain result-returning sub-agents: host teammate/naming options route a pass's output off the channel the orchestrator collects, so completed reports vanish silently (observed in the field); council's Agent Teams path is the sole exception and must collect each member's findings from team state. Every finding-producing child prompt also carries the skill's read-only rule, so improvised destructive verification (e.g. mutating code to test test-suite strength) runs only against an isolated copy.

---

## [0.39.0] – 2026-08-14

### Added
- **Architecture Model – a typed model of the codebase as it stands.** `architecture-model.json` (canonical schema in `references/architecture-model.md`) captures contexts, module-level nodes each anchored to a repo-relative `ref`, and evidence-tagged edges, so every drawn dependency is refutable against the code. Producers validate the invariants before writing and the atlas renderer re-checks them and refuses an invalid model; `scripts/validate-architecture-model.sh` is the AndThen-repo dev check for the same set, not a shipped gate (exit `0` valid / `1` violations / `2` bad usage).
- **`map-codebase --model` emits the model.** Nodes and edges come from dependency tooling, import scans, and change coupling; agent judgment is confined to clustering, naming, summaries, and tours, and marked `inferred`. Target altitude is 10–60 module-level nodes – file-level granularity re-clusters instead of shipping.
- **`visualize` renders it as an atlas.** A new `architecture-model` artifact type renders through a bundled deterministic Node renderer into a self-contained 3D view – contexts as drafting sheets, nodes as markers, `inferred` items dashed – with a 2D list fallback, the standard notes loop (anchored to nodes and contexts), and the same CSP-locked no-network output as every other render. Notes route back to the `andthen:architecture` skill for design follow-ups or the `andthen:map-codebase` skill for corrections.
- **Atlas navigation.** Zoom anchors on the pointer, shift/middle/two-finger drag pans (bounds-clamped), double-click on empty space recenters.
- **Domain Model – the glossary as a typed atlas artifact.** `ubiquitous-language --model` projects the canonical Ubiquitous Language document into `domain-model.json` (`Domain Model` in the Project Document Index) – a sibling kind sharing the architecture-model invariant core, checked identically by producer and renderer.
- **Typed models are transient projections.** Markdown documents and the code are the persistent sources of truth; both atlas models default to `.agent_temp/models/` and regenerate on demand – a projection disagreeing with its source is stale, never authoritative. A `Context Map`, when present, owns bounded-context identity across both kinds. Point a model's Project Document Index row at a committed path only to pin reviewed snapshots.
- **`map-codebase --model-only` refreshes the projection cheaply.** Runs only the codebase survey and model emission – no documentation outputs – so regenerating an atlas on demand stays lightweight.
- **Domain lens in the atlas.** `visualize` renders `domain-model.json` with overloaded terms floating between their contexts' sheets on dashed tethers (verbatim doc labels, italic), strikethrough avoid-term chips, and DDD-category lens chips; notes route to the `andthen:ubiquitous-language` skill. Architecture-atlas rendering is unchanged.

### Changed
- **Module-aware story slicing.** The `plan` skill gains the **Module fan-out rule** (Single-session corollary): where module/package/service boundaries are strong, stories confine to one module; genuinely cross-module features seam-split into per-module stories, interfaces in `sharedDecisions[]`. Boundary discovery consumes the Architecture Model when present.
- **Wave Discovery Triage in `exec-plan`.** Mid-run discoveries propagate at wave boundaries instead of only the end-of-run rollup: constraints append to not-yet-started stories' FIS via `ops`; contract-invalidating discoveries surface for decision (`--auto` blocks the story).
- **Dual-tool projects get one canonical instruction file.** `init` now generates `AGENTS.md` as the full root instruction file and `CLAUDE.md` as a thin `@AGENTS.md` import (Claude-specific additions below the import) instead of two byte-equivalent copies – Claude Code's official interop pattern. Partial setup offers conversion of existing duplicated pairs and counterpart creation follows the same shape.
- **Foundational Rules wiring is opt-in.** The shipped CLAUDE/AGENTS template's Foundational Rules section now carries commented setup options only – no active reference line. User-level copy into `~/.claude/CLAUDE.md` / `~/.codex/AGENTS.md` remains the recommended wiring; `init` still installs `docs/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md`.

### Fixed
- **`exec-plan --worktree` no longer requires `--team`.** Per-story worktree isolation (create → verify → squash-merge → teardown) now runs in the default sub-agent mode too; the lifecycle moved to the mode-agnostic `worktree-mode.md` reference, with `team-mode-orchestration.md` keeping only the team-side wiring.

---

## [0.38.1] – 2026-08-12

### Changed
- **Plan fix rounds are severity-gated and policy-routed.** Step 6 dispatches rework only for readiness-affecting findings (CRITICAL/HIGH, cross-story contract breaks, coverage/chain gaps, mechanical-validity defects); lesser findings fold into an occurring dispatch or land as **Documented residuals** in the completion summary – never a dedicated round. Fix dispatches route per the Sub-Agent Model Policy by heaviest finding (all-mechanical rounds downshift), and reviewer/validator reports are findings-only, citing anchors. Targets the measured dominant cost of bundle generation: remediation dispatch overhead.
- **Ops hot path slimmed.** `update-learnings` shard mechanics and `update-ledger` per-form actions moved to the skill-local references `learnings-shards.md` and `ledger-forms.md` (read on use), plus a dedup/tighten pass across the skill and its references – ~5.5k chars off every ops invocation; contracts unchanged.

### Fixed
- **Spec drift fix.** Removed stale pre-batching OPS-34 and realigned OPS-59 to the per-pair `REJECTED:` grammar (spec-only; skill behavior unchanged).
- **Learnings shard contract polish.** Shard-wins merges keep non-bullet content on every path (not only ceiling graduation), repeat-checking a trap counts as touching its topic's shard, and the Decisions `BLOCKED:` string is aligned between skill and spec.

---

## [0.38.0] – 2026-08-07

### Removed
- **Generic starter guidelines dropped.** `DEVELOPMENT-ARCHITECTURE-`, `UX-UI-`, and `WEB-DEV-GUIDELINES.md` no longer ship – frontier models follow these practices unprompted, and generic guides dilute the rules that matter. `CRITICAL-RULES-AND-GUARDRAILS.md` is now the sole starter guideline (absorbing the few unique rules); the template's guidelines section becomes a placeholder for project-authored guidelines.

### Changed
- **Learnings become a bounded index with topic shards.** `LEARNINGS.md` is capped at 150 lines: `ops update-learnings` routes entries to sharded topics, graduates overflow topics to `learnings/<topic-slug>.md`, and gains a `remove` form for check-superseded or stale entries; skills read the index whole and open only task-relevant shards. Entries stay under 200 chars (trap + pointer, postmortems linked not inlined), and recurring traps prefer encoding as a lint rule/test over prose. CRITICAL-RULES adds the matching boundary: harness auto-memory holds personal/machine-local context only – project-durable knowledge belongs in committed docs.
- **Executors investigate before blocking.** A five-rung Resolution Ladder governs ambiguity; `exec-spec --auto` may amend scenario articulation only with fixed tags/Proof, while Intent/outcome changes still stop. Review ambiguity is re-tested only with new evidence.
- **Reconciliation gates are durable.** Same-run entries stay visible, AUTO_MODE cannot self-clear them, and completion is not presented as shipped before human reconciliation. `exec-plan` persists drift/ambiguity before Done, repairs worker input blockers once, and serializes multi-repo FIS writes.
- **Discovery records sharp questions, not fog.** `clarify` emits imprecise areas as `Area to revisit:`, `now-what` excludes those from open-question counts, and signed Preflight deferrals remain execution holds.
- **Sub-agent routing runs on three tiers.** The **Sub-Agent Model Policy** owns model and effort: judgment routes to session/xhigh, implementation to top/medium, and small well-specified work to cheap/medium-or-xhigh. Availability/ceiling-checked examples otherwise inherit; dedicated agent configs are the explicit exception.
- **Browser and simplification work are capability-led.** E2E selects any qualifying browser provider; simplify-code adds a Necessity/YAGNI lens that removes only proven-inert complexity and defers observable removals without approval.
- **Generated guidance and FIS files are leaner.** Init drops generic tool tutorials; skills avoid redundant rule reloads; optional FIS sections are omitted; bound scenarios may use precise title + executable Proof without duplicated GWT. Verify describes outcomes, and OVERSIZE measures words as well as lines.
- **Review gates are consolidated.** Plan batches use one cross-cutting fresh-context review with external-claim falsification; standalone PRD/spec use one full review plus bounded verification. Plan writes batch verified or cleared FIS pointers per sub-wave, and final gap remediation must re-pass.
- **External inputs remain inert end to end.** Trust survives agent boundaries; operations and paths are re-derived/contained; PR reads and publication are SHA/repo-bound; visual HTML is escaped and CSP-locked.
- **Issue triage follows the no-attribution rule.** Tracker comments and Agent Briefs no longer add an AI-attribution marker.
- **Document/visual gates focus on substance.** Doc lint collapses into one aggregate LOW finding; visual completion uses the same canonical scenario/task sets as its KPIs.

---

## [0.37.0] – 2026-07-25

### Added
- **New `andthen:issue-triage` skill.** Triages incoming issue-tracker items into a routed backlog – one category and one recommended state per item, ratified before any write, then labels, an AI-attributed comment, and (for `ready-for-agent`) a durable agent brief; `--auto` applies only safe transitions. Distinct from the `andthen:triage` skill, which debugs a live failure.
- **New `andthen:spike` skill.** Answers exactly one named design question by building a throwaway runnable spike on a `spike/<slug>` branch, then reports a Spike Verdict; the spike is evidence, not product – it never merges and is never reused directly, only the decision flows on. Model- and user-invocable; upstream skills route empirical-unknown questions to it; screen/flow/mockup questions redirect to the `andthen:ui-ux-design` skill.
- **Three new document types.** `Issue Tracker` (`docs/ISSUE-TRACKER.md` – backend, label role mapping, and an operation table for non-GitHub trackers), `Context Map` (`docs/CONTEXT-MAP.md` – bounded contexts + integration patterns), and `Out of Scope Registry` (`docs/OUT-OF-SCOPE.md` – cross-feature rejected concepts), with ready-made templates.

### Changed
- **Issue operations resolve through a tracker backend (GitHub default).** Issue-facing skills resolve the optional `Issue Tracker` document before any issue op; absent or `Backend: GitHub` keeps the exact `gh` behavior, another named backend substitutes per its operation table with every body shape, label, and footer unchanged. PR flows stay GitHub-native.
- **`andthen:init` gains a tracker gate and recommendation-first optional docs.** A dedicated gate settles where agent workflows read and publish issues (recommend GitHub when a remote is detected, else local artifacts); optional docs now lead with a detection-derived recommendation ("default" accepts it) and add the Out of Scope Registry to the Domain group.
- **`andthen:architecture --mode strategic-design` registers a Context Map.** The accepted map graduates into the `Context Map` document (user-gated, idempotent per context/pair); the `andthen:spec`, `andthen:clarify`, and `andthen:ubiquitous-language` skills read it, and glossary clusters group by its bounded contexts.
- **`andthen:plan` names two story-sizing rules.** The **Single-session rule** – a story plus its FIS must fit one fresh-context exec run, so an `OVERSIZE:` signal (shared with the `andthen:spec` skill) means split rather than push on – and the **Wide-refactor exception** – large mechanical changes sequenced expand → migrate → contract, one build-green story per batch.
- **Firmly rejected directions graduate to the Out of Scope Registry.** The `andthen:clarify` and `andthen:prd` skills record rejected concepts (not deferrals) into the registry, and the `andthen:clarify` and `andthen:issue-triage` skills check it before acting so an already-rejected concept isn't silently re-litigated; already-implemented closures never enter it.
- **Published descriptive bodies follow a Durability rule.** PRD issues, plan-issue summaries, triage agent briefs, and comments name interfaces and behavior, not file paths, line numbers, or code snippets, so they outlive the code snapshot.

---

## [0.36.0] – 2026-07-16

### Added
- **Codex plugin channel.** The same `plugin/` directory now installs as a Codex plugin – `plugin/.codex-plugin/plugin.json` plus a repo-level Codex marketplace (`codex plugin marketplace add IT-HUSET/andthen`, then `codex plugin add andthen@andthen`). Codex caches the plugin whole, so shared references travel with it (no build step) and skills register under the same `andthen:<name>` ids as Claude Code; CI now enforces version consistency across CHANGELOG and all three plugin manifests, and Codex review agents (TOML) remain on the installer path.

### Changed
- **Sigil-free skill cross-references in shipped content.** Skill/reference/agent prose now references skills as "the `andthen:<name>` skill" – never host invocation sigils (`/andthen:<name>`, `$andthen-<name>`), which render as the wrong syntax on other hosts. The installer's slash-form rewrites are removed and a pre-copy validator rejects sigil forms – runnable standalone via `--validate-only` and CI-gated on plugin changes; `SYS-15` codifies the contract.
- **Skill descriptions trimmed to a lean trigger surface.** 27 of 29 frontmatter descriptions reworked (two already lean) to front-load the primary use case, keep 2–4 distinct trigger phrases, and drop body restatement – the always-loaded description footprint shrinks ~36% (≈1,540 → ≈980 words) with cross-skill disambiguation constraints preserved. `SYS-21` updated to codify the tightened contract.
- **Tighten pass over the five largest skill bodies.** `exec-spec`, `exec-plan`, `visualize`, `ops`, and `plan` pruned of duplication, sediment, and no-op prose (16 surgical edits, every removed fact still living at a reachable canonical); a stale `## Binding Constraints` pointer in `plan` now names the `bindingConstraints[]` array it feeds. Verified by a fresh-context contract-preservation review.
- **Skill-authoring rubric extended with skill-craft concepts.** Leading words, a four-way pruning taxonomy (Duplication/Sediment/Sprawl/No-op), gate clarity × demand, the premature-completion failure mode, and negation→positive-target steering – landed in the authoring/prompt guidelines and the project-local tighten skill.
- **`andthen:preflight` interview questions now carry decision context.** Each question leads with where the decision surfaced, what it affects, and why an unattended run would fork on it; each option states its observable consequence – enough to decide informed without re-opening the FIS, kept deliberately brief.

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
- **Cost/outward flags stay explicit by contract.** `--council`, `--team`, `--worktree`, `--fix`, `--to-pr`, and `--to-issue` are never inferred from phrasing – they spend tokens, write code, or post externally, so they require the explicit flag. Partition fan-out is the one deliberate exception – keyed on surface shape (a semantically wide or proof-bearing diff, e.g. a standard FIS or changed tests/migrations/APIs), it makes proof-led reviews parallelize by default, with `--no-fanout` to opt out; READMEs now lead with natural-language examples and show the flag form as the equivalent.
- **`andthen:review` permits required sub-agents explicitly.** Review now treats skill invocation as permission for required review sub-agents and checks lazy-loaded delegation tooling before running inline.
- **Plugin-wide skill tightening (behavior-preserving).** Applied the same lean, proof-led pass to the rest of the skills: removed restated contracts, wrong-altitude prose, and accreted seams across 49 skill files (~-22k chars). Every deduplicated contract keeps a single reachable home; parser tokens, deterministic grammars, cross-skill contracts, and calibration catalogs are unchanged. Also fixed three drift/correctness issues found in passing – the `andthen:map-codebase` skill's read-only wording now matches its documented outputs, the `andthen:visualize` skill's static affordances list `Copy section`, and a dangling "Output Path Semantics" pointer in the `andthen:prd` skill now targets the Step 1 dispatch.

---

## [0.33.0] – 2026-06-30

### Added
- **New `andthen:preflight` skill** – an interactive convergence gate that drives a single FIS or a whole plan bundle to zero open blocking decisions before an unattended `exec-spec`/`exec-plan` run. It detects decisions via `review --mode doc`, settles open ADRs inline via `architecture --mode trade-off`, routes requirements-altitude gaps to `clarify`, interviews the user on each implementation-blocking decision, and persists every resolution by altitude; it emits a machine-stable `Preflight: READY | DEFERRED | BLOCKED` verdict, and under `--auto` it never interviews but enumerates the unresolved blocking decisions as a signal. A recommended gate – the executors honor it but never require it.

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

Releases 0.1.0 – 0.29.0 (2026-03-13 – 2026-06-12) are culled from this file; read them in git history (`git log -p -- CHANGELOG.md`).
