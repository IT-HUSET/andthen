# AndThen Plugin Architecture

How the AndThen plugin is structured: the skill loading model, how shared content is propagated at install time, which documents the skills own, and where the pipeline crosses a conversation boundary. Read this when working on changes that touch skill structure, shared references, the install pipeline, or how skills consume project context.

For everyday rules and routing, see `CLAUDE.md` instead.


---


## One Plugin, One Marketplace

**`andthen`** (`plugin/`, 21 skills) is the pipeline end to end – `init`, `now-what`, `clarify`, `plan`, `spec`, `exec-spec`, `exec-plan`, `implement-fix`, `review`, `triage`, `testing`, `handoff`, `architecture`, `describe`, `ui-ux-design`, `visual-validation` – plus `tracker` for the issue-tracker projection and the solo tools `spike`, `simplify-code`, `skill-review`, `backlog-triage`. Both marketplace files carry the one entry.

**Document ownership.** The plugin owns all three domain documents – scaffold, write, and read.

| Document | Scaffold | Write | Read |
|---|---|---|---|
| Ubiquitous Language | `init` (optional Domain doc) | `describe --mode domain`; `clarify` seeds it inline as terms settle | `spec`, `plan`, `exec-spec`, `review` lenses, `handoff`, `describe` |
| Context Map | `init` – Index entry only, when confirmed | `architecture --mode strategic-design` | `clarify`, `spec`, `describe`, `architecture --mode advise` |
| Models (committed, `docs/models/`) | `init` – Index entry, always present | `describe --mode domain --model` (domain model), `describe --mode codebase --model` (architecture model), `architecture --mode event-storming` / `--mode strategic-design` (boards) | `plan`, `architecture` |

Names stay `Ubiquitous Language` / `Context Map`: the Document Index entry, not the path, is the contract, and "context" is the most overloaded word in the agent world.

**Working artifacts are branch-scoped; the requirements source – `prd.md`, or the tracker item a plan with `prd: null` came from – is the surviving product record.** `plan.json` and FIS files stay on the branch and are deleted before the merge. Reading each FIS's Implementation Observations for what belongs in Learnings or Decisions, and writing it, comes before the deletion, because the bodies go with the bundle. The FIS head (`Story-ID`, Intent, Expected Outcomes) travels in the squash-merge message so `git log --grep <story-id>` keeps the why, and the per-story commit `exec-plan` and `exec-spec` make, staged by path, carries the same `Story-ID:`/`Plan:` trailers, so the key exists before merge. Stated once here; the skills cite it.


---


## Project Context Discovery

Skills read the **user's project** `CLAUDE.md` (not this repo's) for two key integration points:

- **Project Document Index** – a list mapping document types to file paths (specs, plans, ADRs, etc.). Skills use this to determine where to read/write output. See `plugin/skills/init/templates/CLAUDE.template.md` for the entry shape: name and location on one line, the read/update trigger on the next.
- **Project-Specific Guidelines and Rules** – project conventions and workflow notes. The `andthen:init` skill offers critical rules directly in the root instruction file; dual-host projects share `AGENTS.md` through a thin `CLAUDE.md` import. The shipped guideline is a starter, not a runtime dependency: the project owns its adopted policy, customizations and opt-out survive reruns, and existing referenced policies remain valid. `init` edits the rule section between its own heading and the next top-level heading, at project scope by default; personal rules and the separate `concise-critical` conversation style are configured only on request.

**Runtime state lives in one place.** Schema v2 `plan.json` is the machine truth for every story, standalone features included – the `andthen:spec` skill writes a one-story plan beside a standalone FIS, so there is one state shape, one reader, and no second schema. **One writer**: the session running `andthen:exec-plan` or `andthen:exec-spec` edits the rows with its file tools, and a story subagent reports its state instead of writing it – concurrent writers, not a race in one file, was what dropped a status write. Continuity across sessions remains the `andthen:handoff` skill's on-demand document. [ADR-003](adrs/ADR-003-runtime-state.md) records the rationale.

**External artifact compatibility is fixture-bound.** `scripts/fixtures/renders/` publishes one minimal, real-shaped artifact per type, and a downstream consumer pins that directory by AndThen tag. That consumer owns its real adapter and compatibility run; a breaking candidate waits for that repository to pass the pinned corpus. AndThen carries neither adapter copies nor cross-repository CI.


---


## Skill Anatomy

Skills live in `plugin/skills/<name>/`, the plugin dir under its Claude Code and Codex manifests. Each skill contains:

- `SKILL.md` – the skill prompt (with frontmatter: `description`, `argument-hint`, and optional `user-invocable`, `context`, `agent`). The `description` is also a routing surface: front-load the primary use case, prefer a `Use when...` framing, include 2-4 natural trigger phrases and AndThen-native terms users actually say (`spec`, `FIS`, `PRD`, `plan`, `gap analysis`, etc.), and keep it concise enough that key terms survive truncation.
- `agents/openai.yaml` – OpenAI/Codex agent metadata for cross-agent portability.
- Optional subdirectories for templates, checklists, or references.


---


## Self-Contained Skills

Skills are fully self-contained: each skill owns its `references/`, `templates/`, and `scripts/` locally, and no skill file reaches into another skill's directory – `../<other-skill>/...` fails validation like every `..` path but the canonical one. A skill that needs another skill's rubric spawns a subagent that invokes that skill, so the skill body loaded there is the one copy and no install tier has a cross-skill path to resolve.

**References are one level deep**: no file in a skill but `SKILL.md` links or paths to another file – the skill body naming a load site names its whole read-set, since a chained reference is invisible to a reader who previews the intermediate file – and `install-skills.sh --validate-only` fails on any such link or path, naming file and line (a bare filename in prose stays a legal mention). The load and mention rule itself is in `docs/SKILL-AUTHORING-GUIDELINES.md` § Scripts and references.

Reusable canonical content lives at `plugin/references/` and is consumed via `../../references/<asset>` – see **Shared Plugin Assets** below. Canonicals are shared by multiple skills; a single-consumer template lives in its owning skill's own `references/` instead (`fis-template.md` under `spec`, `prd-template.md` under `clarify`), so a dedup pass has nothing to promote back. `install-skills.sh` inlines each canonical into every consuming skill at install time, so installed bundles stay self-contained.

**Forking shared content** – when a consumer genuinely needs a divergent version, fork explicitly: copy the canonical into the skill's local `references/` under a distinct name (e.g. `triage-plan-schema.md` as a triage-only fork of `plan-schema.md`) and point that skill's references at the local copy. Don't preemptively duplicate – fork on demand, not by default.


---


## Shared Plugin Assets

The canonical assets live at `plugin/references/` – a single canonical location for install-inlined reference content. **Consumed by** lists the skills each asset installs into: the direct references `install-skills.sh` finds in that skill's own files. A canonical naming another canonical by bare filename is prose, not a load – references are one level deep (see above), so that mention never pulls the named asset into a consumer that doesn't reference it itself.

**One canonical.** `../../references/` climbs from a skill root into `plugin/references/`, which stays the one place an asset is edited. No build step, no symlinks (Windows checkout), no copies to keep in sync. A skill-local reference is not covered by any of this – nothing syncs two skills' own copies – so a second consumer is a reason to promote the file to a canonical, not to fork it.

| Asset | Consumed by |
|---|---|
| `architecture-model.md` | describe |
| `architecture-model.schema.json` | describe |
| `automation-mode.md` | plan, spec, exec-spec, exec-plan, implement-fix, triage, ui-ux-design, simplify-code, backlog-triage, tracker |
| `board-models.md` | architecture |
| `closure.md` | spec, plan |
| `context-map.schema.json` | architecture |
| `design-tree.md` | architecture, clarify |
| `event-storm.schema.json` | architecture |
| `execution-discipline.md` | exec-spec, exec-plan |
| `fis-authoring-guidelines.md` | plan, spec |
| `fis-contract.md` | plan, spec, exec-spec, review |
| `fis-mutability.md` | exec-spec, review, implement-fix |
| `intent-and-rules-context.md` | review, implement-fix, simplify-code, skill-review |
| `lens-adversarial.md` | review, skill-review |
| `plan-schema.md` | plan, spec, exec-spec, exec-plan, review |
| `plan.schema.json` | plan, spec |
| `project-document-templates.md` | architecture, describe, init, tracker |
| `review-calibration.md` | review, architecture, implement-fix, skill-review |
| `self-review.md` | clarify, spec, plan |
| `testing-strategy.md` | testing |
| `verification-evidence.md` | exec-spec, exec-plan, implement-fix, review, testing, triage, simplify-code |


---


## Reference Syntax in Skill Prompts

Every path in shipped skill content resolves from the skill's own directory, which both hosts announce to the model – Claude Code as *Base directory for this skill: `<path>`*, Codex as the `SKILL.md` path it loaded. Neither substitutes a variable in skill text – Claude Code's two path variables are retired and Codex never had them, so a token left in place cost the model a plugin-cache search before every read – and `install-skills.sh --validate-only` rejects both names anywhere under a plugin dir, naming the shape to use instead.

Three forms, and nothing else leaves the skill root:

- `references/<name>.md` – the skill's own reference.
- `../../references/<asset>.md` – a **shared canonical**. It climbs from the skill root to `plugin/references/`. In a markdown link the bare filename is the link text and the path the URL – `` [`<asset>.md`](../../references/<asset>.md) `` – so the rendered text stays stable across install tiers; the URL is what `install-skills.sh` rewrites. Any other `..` path in a `SKILL.md` fails validation, named with its file and line; no file but `SKILL.md` paths to anything, code fences included (see **Self-Contained Skills**).
- `<skill-dir>/scripts/<name>` – **required for bash invocations of bundled scripts**, where the shell's cwd is the project, not the skill. `<skill-dir>` is a literal placeholder the model fills with the announced directory. Markdown links and prose references to bundled files may stay bare-relative – they are read, not executed.

A path is a load, a bare backticked filename a mention; the authoring guidelines state the rule, the installer enforces it – a skill's canonical closure is exactly the `../../references/` paths in its own files, and a bare canonical name in a `SKILL.md` that never loads that canonical fails validation.


---


## Typed Artifacts

The atlas has a typed data contract with two kinds sharing one invariant core (schema canonical: `plugin/references/architecture-model.md`): `architecture-model.json`, produced by the `andthen:describe` skill in `--mode codebase --model` – deterministic extraction (dependency tooling, import scans, doc/manifest declarations, git change-coupling) owns nodes and edges, agent judgment is confined to clustering, naming, summaries, and tours, and every claim carries an `evidence` tag – and `domain-model.json`, produced by the same skill in `--mode domain --model` as a 1:1 projection of the Ubiquitous Language document (contexts from its clusters, doc-anchored `ref`s, overloaded terms carrying per-context `meanings`). Each model's schema ships beside its reference in `plugin/references/` as the shape contract; no shipped verb validates a model, so a producer checks its own candidate before writing. Both models are **committed projections** under the `Models` Index location (default `docs/models/`), carrying the source revision in `meta.revision` – the code and the Ubiquitous Language document are the sources of truth, and a `Context Map`, when present, owns bounded-context identity across both kinds. The two board models the `andthen:architecture` skill emits – `event-storm` and `context-map`, schema canonical `plugin/references/board-models.md` – follow the same pattern.


---


## Conversation Boundaries

Every hand-off in the pipeline is either the same conversation or fresh context, and each fresh boundary exists for one of two reasons: **context rot** (a long-running context degrades, so heavy or independent work gets a clean one) or **reviewer independence** (an agent cannot review what it just wrote). The mechanism is always the same – a generic subagent whose prompt invokes the skill, or the user pasting one line into a new session; no skill declares `context: fork`. Derived from the skills themselves; each reason is the one the skill states.

Per transition – the boundary it crosses, then its reason:

- **`now-what` → the routed skill** – same conversation; hands off in place, deliberately without `context: fork`. No reason needed: routing.
- **`clarify` → `plan`, `plan` → `exec-plan`, `spec` → `exec-spec`** – fresh session; the authoring skill prints one paste-ready line and offers nothing in-session. Context rot: planning and execution each perform best in a clean session, and the artifact is the whole hand-off.
- **`clarify` / `spec` → self-review** – fresh-context subagent loading the `self-review.md` rubric (§ PRD or § FIS, the latter beside `fis-authoring-guidelines.md` and `fis-contract.md`) by absolute path; the author-loaded guidelines carry no reviewer text, so the author never reads the rubric it is judged by. Reviewer independence: the author does not review its own document.
- **`plan` → per-story FIS authoring (`spec --auto story <id>`)** – one subagent per story; the orchestrator never authors FIS content. Context rot: protects the orchestrator's context window.
- **`plan` → cross-cutting review** – fresh-context subagent on the same rubric (§ FIS and § Bundle), reading the PRD fresh and returning a per-FIS roster. Reviewer independence: the bundle's single fresh-context gate.
- **`exec-plan` → one story** – one fresh subagent per ready story invoking the `andthen:exec-spec` skill with `--auto --no-full-tier`; it owns that story whole, down to the code commit; under `--worktree` a ready batch runs at once, one worktree each, merged back by the run session with `git merge --no-ff` – a conflict stops the line rather than being resolved blind. Context rot: the Single-session rule sizes a story to one fresh-context run, and each story's implementation, proof, and review output stays in its own ([ADR-014](adrs/ADR-014-story-runs-where-invoked.md)).
- **`exec-spec` → the story's code and proofs** – same conversation: it implements the FIS and runs its tier and every `Proof` and `Verify` where it was invoked. No boundary needed: a direct run is already a fresh session, and under `exec-plan` the story's subagent is that context.
- **`exec-spec` → documentation lookup, codebase reconnaissance** – read-only subagents returning distilled briefs. Context rot.
- **`exec-spec` → the per-story review** – one fresh reviewer subagent invoking the `andthen:review` skill with `--quick` and `--intent`, on every run. Reviewer independence: `exec-spec` wrote the code, so the independent pass is not its own; one quick pass is the depth a story earns, and the rest stays at the plan-level review ([ADR-014](adrs/ADR-014-story-runs-where-invoked.md)).
- **`exec-spec` → `visual-validation`** – subagent. Reviewer independence.
- **`exec-plan` → plan-level review (`review --mode code,gap,security,outcome`)** – fresh session; the run ends on a `Next:` line carrying that one invocation with `--fix`, which runs `implement-fix` on the report. Context rot: after N stories the run session is the most loaded context in the workflow; `implement-fix` applies the fixes as one round, and is where a per-story review's open findings are enforced.
- **`exec-plan` → final repair after a red full tier** – one fresh subagent invoking the `andthen:triage` skill with `--auto` on the failing checks and the affected FIS paths; the run session re-runs what the repair invalidated. Context rot: the repair reads the failing checks, not the run's history.
- **`review` → a chain's lens pass, fan-out partitions and boundary pass** – fresh reviewer subagents, partitions dispatched as one flat batch. Context rot: a chain's rubrics, or a large diff's partitions, against a session that still owes filtering, verdict, and report. A single lens below the fan-out trigger runs in the invoking session, which the caller already made the independent reader; the Critic is a posture every lens applies, never its own pass.
- **any session → `handoff` → the next session** – the document is written for a fresh session. Context rot: the session is ending or low on context.


---


## Install-Time Propagation

`scripts/install-skills.py` per-target behavior:

Before loose-skill copies begin, the installer derives each skill's direct canonical references – the `../../references/` paths in its own files, no transitive following. That required set must exactly match the skill's `_skill_assets_*` declaration. After rewriting a staged bundle, each required canonical asset and canonical markdown link is checked inside that bundle before it replaces the destination, so both declaration drift and copy/rewrite omissions fail before success is reported.

| Target | `../../references/<asset>` | `<skill-dir>/<rest>` |
|---|---|---|
| Plugin install (either host) | No rewrite – the canonical travels with the plugin | No rewrite – the model fills the placeholder |
| `--claude-user` and default / Codex (`~/.agents/skills/`) | Inline canonical into skill's `references/`; rewrite path to local-relative form | Replace with absolute install path of the skill |

Skills are the only propagated unit, exported as `<prefix><name>`: the installer rewrites `andthen:` to that prefix in markdown and `agents/openai.yaml`, and in the `SKILL_NS = ` assignment line a bundled script defines, so runtime diagnostics name skills that exist in the installed namespace while identifiers matched on read (the tracker's issue marker, schema `$id`s) stay literal. No plugin agent auto-loads; `init` carries opt-in role templates separately. A loose reinstall stages and replaces each owned surviving skill directory, removing stale files inside it. Removing or renaming a whole skill still does not delete its previously installed `<prefix>*` directory.


---


## Distribution Channels

One source directory, three channels – `plugin/` is neither duplicated nor pre-built into the repo:

- **Claude Code plugin (primary)** – `.claude-plugin/marketplace.json` lists it (`andthen` → `./plugin`), shipped verbatim – no inlining, no path rewrites. The `concise-critical` output style lives under `plugin/skills/init/templates/output-styles/` (so it travels with the `init` skill on every channel) and is registered through the manifest's `outputStyles` field – opt-in via `outputStyle`, never `force-for-plugin` (that would silently override the user's own style). Codex ignores the field; on user-tier/loose installs `init` copies the file to `~/.claude/output-styles/` when wiring.
- **Codex plugin (primary)** – the same directory, described by its `.codex-plugin/plugin.json` and served by the repo-level `.agents/plugins/marketplace.json` (`codex plugin marketplace add IT-HUSET/andthen`). Codex copies a plugin directory whole into its versioned cache, so `plugin/references/` travels with the skills – no inlining, no build step, no rewrites. Skills register as `andthen:<name>`, byte-identical to Claude Code, which is why shipped prose uses that form. Codex plugins cannot carry subagents, which costs nothing here: no agents auto-load from the plugin – the optional role-agent templates travel inside the init skill bundle and are installed opt-in – and delegation is always a generic subagent whose prompt invokes a skill or loads a reference.
- **Loose skills (secondary)** – `scripts/install-skills.sh` for the `~/.agents/skills` readers (Gemini CLI, Cursor, opencode, Amp, Copilot, plugin-less Codex), the Claude user tier, and white-label installs. It exports `plugin/skills` as one skill set, inlining canonicals from `plugin/references/`. This is the only channel where bundles leave the plugin structure, so it performs the inlining and rewrites described above.

**Version contract**: four locations carry the same version – `CHANGELOG.md`, the `andthen` entry in `.claude-plugin/marketplace.json`, `plugin/.claude-plugin/plugin.json`, `plugin/.codex-plugin/plugin.json` – enforced by CI (`validate-plugin.yml`), because four hand-edited copies skew.
