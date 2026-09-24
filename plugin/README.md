# AndThen Plugin

Lightweight spec-driven development for AI coding agents. This is the reference for the 21 skills – flags, modes, edge-case behavior. The task-oriented companion is [`COOKBOOK.md`](../COOKBOOK.md).

See the [full documentation](../README.md) for the workflow overview and setup.

## Installation

<!-- pre-release: delete this warning when 1.0 is public -->
> [!WARNING]
> 1.0 is not on the public marketplace yet – the `IT-HUSET/andthen` commands below install 0.40.x. Use the [1.0 preview install](../README.md#10-release-candidate-from-the-develop-branch).

```bash
/plugin marketplace add IT-HUSET/andthen
/plugin install andthen
```

**Scope options:**
```bash
/plugin install andthen --scope project   # current project only (default: user scope)
```

**Enable auto-update**: run `/plugin`, go to the **Marketplaces** tab, select the `andthen` marketplace, and choose **Enable auto-update**.

**Local install** (repo cloned):
```bash
claude plugin install ./plugin
```

**Codex CLI plugin**:
```bash
codex plugin marketplace add IT-HUSET/andthen
codex plugin add andthen@andthen
```

For loose-skill installs on other agents, see [Other agents](../README.md#other-agents-aider-cursor-gemini-cli-opencode) in the full documentation. Python 3 is the one runtime requirement (the `tracker` script).

## Setup

Skills reference your project's root agent instruction file (`CLAUDE.md` for Claude Code, `AGENTS.md` for Codex/generic agents; when both tools are used, `AGENTS.md` is the canonical file and `CLAUDE.md` is a thin `@AGENTS.md` import with any Claude-specific additions below it) for two things:

- **Project Document Index** – tells skills where to read and write (specs, plans, project docs). Each entry names a document and its location on one line and its read/update trigger on the next. Documents are read whole, so they stay short and stale entries are trimmed on append.
- **Project-Specific Guidelines and Rules** – project-specific guidelines and workflow notes (critical rules are adopted through init as described below).

See [`skills/init/templates/CLAUDE.template.md`](skills/init/templates/CLAUDE.template.md) for the starter template.

### How AndThen describes a project

Markdown documents are the **sources of truth**; typed models are **committed projections** of them, written against the schema shipped beside each model's reference:

| Aspect | Source of truth | Committed projection |
|---|---|---|
| Product intent | `PRODUCT.md` (including its Proportionality facts) | – |
| Domain language | `UBIQUITOUS_LANGUAGE.md` (glossary and nothing else); `CONTEXT-MAP.md` owns bounded-context identity when present | `domain-model.json` via `describe --mode domain --model` |
| System structure | the code itself (`ARCHITECTURE.md` is prose orientation) | `architecture-model.json` via `describe --mode codebase --model` |

Projections live under the `Models` Index location (default `docs/models/`), carry the source revision they describe in `meta.revision` – its last commit, suffixed `-dirty` when the working tree differs – and are regenerated at deliberate points – a projection that disagrees with its source is stale, never authoritative. The plugin owns all of these: `describe` writes the glossary and both models, `architecture --mode strategic-design` writes the Context Map, and `clarify` adds settled terms to the glossary when the Project Document Index configures one.

### Foundational Rules and Conversation Style

**Project rules are the recommended scope.** The `andthen:init` skill offers the [critical-rules starter](skills/init/templates/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md) directly in the root instruction file: `AGENTS.md` for Codex/generic agents, `CLAUDE.md` for Claude Code alone, or shared `AGENTS.md` with a thin `CLAUDE.md` import for both. The adopted rules travel with the checkout into CI and containers; no home-directory copy, runtime plugin path, or hook is needed.

Teams own their adopted policy. Init preserves customizations and existing referenced rules; upgrades do not synchronize them back to the starter. **Skip** records `<!-- AndThen critical rules: skipped -->` in the owning instruction file, so later init runs respect the choice. An active rules block takes precedence over the marker, which declines adoption rather than disabling existing project or global policy. To adopt later, ask init to remove the marker and add the rules. Existing separate or global copies are reconciled only with the user's agreement.

Init rewrites only the block between the `# Critical Rules and Guardrails` heading and the next top-level heading, so surrounding content and customizations survive; it never creates a second copy of the guideline. Personal installation remains available on request at user level, with the same comparison against the shipped starter and the same replacement protection. Neither rule adoption nor skipping configures conversation style.

Without init, ask your agent:

> Adopt AndThen's critical-rules starter in this project's root instruction file. Use AGENTS.md with CLAUDE.md importing it when both hosts are used. Preserve existing policy and customizations, reconcile any duplicate copies with me, and leave personal configuration alone.

**Conversation style** – [`skills/init/templates/output-styles/concise-critical.md`](skills/init/templates/output-styles/concise-critical.md) (brief plain-language answers a cold reader can act on, critical stance, state-each-fact-once, reference codes, conclusion last). Only the top-level agent talks to you, and the harness's own system prompt sets competing tone and verbosity defaults there – so these rules go in the system prompt, where they survive compaction and Claude Code re-emphasizes them. Keeping a rule in both tiers dilutes it, so the guideline above deliberately omits them.
- Claude Code: the plugin registers the style (`outputStyles` in the plugin manifest); opt in with `"outputStyle": "andthen:concise-critical"` in `~/.claude/settings.json`, then start a new session (confirm the plugin-namespaced name is listed by your Claude Code version; if not, use the copy below). `keep-coding-instructions: true` keeps Claude Code's built-in engineering instructions alongside. User-tier and loose installs: copy the file to `~/.claude/output-styles/` and use `"outputStyle": "concise-critical"`. A project-level `outputStyle` (`.claude/settings*.json`) shadows the user-level one.
- Codex: the style body (everything below the frontmatter) goes into `~/.codex/config.toml`, top-level section:
  ```toml
  model_verbosity = "low"        # optional response-length knob; back off to "medium" if deliverables lose needed detail
  personality = "pragmatic"      # optional tone preset
  developer_instructions = """
  <body of skills/init/templates/output-styles/concise-critical.md>
  """
  ```
  Do not use `model_instructions_file` for this – it replaces Codex's base instructions wholesale.
- Don't want an output style / `developer_instructions`? Append the style body to your user-level `CLAUDE.md`/`AGENTS.md` instead on explicit request.

## Workflows

**User input**: `clarify`'s interview rounds, the Preflight questions `plan` and `spec` close on, `architecture`'s trade-off gates, and `backlog-triage`'s per-item ratification use the host's structured question tool when available, permitted, and suited to the question, respecting its mode restrictions, schema, and limits; otherwise they ask in chat. Asynchronous questions still require your response before dependent decisions; preselected answers are not confirmation.

Every skill works standalone – no pipeline required. See the [full documentation](../README.md#the-workflow) for the workflow, the design stage, and the two loops, and the cookbook for the runnable sequences: [one story](../COOKBOOK.md#one-story), [several stories](../COOKBOOK.md#several-stories), [a small change](../COOKBOOK.md#a-small-change), [team story work](../COOKBOOK.md#team-story-work), [unattended execution](../COOKBOOK.md#unattended-execution), [resuming interrupted work](../COOKBOOK.md#resuming-interrupted-work).

**Session management**: the context-intensive skills – `exec-spec`, `plan`, `exec-plan` – perform best in a **clean session**. The authoring skills (`clarify`, `plan`, `spec`) close on one paste-ready next command that says to run it in a fresh session, `exec-spec` and `exec-plan` on a `Next (fresh session):` line, and `handoff` compacts a session that has to end mid-work. The conversation-boundary map in [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md#conversation-boundaries) lists every hand-off and whether it stays in the conversation.

**Headless orchestration**: `plan`, `spec`, `exec-spec`, `exec-plan`, `review`, `implement-fix`, `triage`, `architecture`, and `ui-ux-design` accept `--auto`. In automation mode they do not ask follow-up questions, record each open decision's recommendation as `ASSUMPTION: <what was assumed> – <what would change it>` in artifacts or summaries, propagate `--auto` to nested skill calls that accept it, and stop only on an unusable call, with `BLOCKED: <what is needed>`. A spec conflict or ambiguity is an investigation before it is a stop: the executors climb a five-rung **Resolution Ladder** – re-read in context, widen the evidence, delegate the question, work around and record it, stop – so an unattended run does not abort on something the repo already answers. `exec-plan --auto` preserves partial work, skips dependents, continues independent stories, and exits with an aggregate failure report. `clarify` has no `--auto`: the interview is the skill, and an unattended pipeline starts at `plan` from a requirements file or tracker item.

## Skills

Invoke with `/andthen:<skill>` (e.g. `/andthen:triage`, `/andthen:spec`).

> **Not sure where to start?** Run `/andthen:now-what` – it inspects your project state and routes you to the right skill.

**You rarely need the flags.** Describe what you want and the skill routes it: `architecture`, `ui-ux-design`, `testing`, and `review` infer the mode or lens from your phrasing, and a menu appears only when the intent is genuinely ambiguous. The exception is `--fix`, whose write authority follows the rule under [`review`](#review).

Each section below opens with the skill's exact `argument-hint`; everything outside those flags is phrasing. `--auto` (automation mode – no prompts, recorded assumptions, a stop only on an unusable call; see [Workflows](#workflows)) is accepted where the hint lists it.

**Proportionality**: `clarify`, `plan`, `spec`, and `architecture` read the `Product` document's Proportionality facts before they propose. Machinery those facts do not carry, or that a standing technical non-goal forbids, is dropped or flagged with the anchor cited. Every alternative set carries its **floor option** (do nothing, or extend what exists), and the recommendation says what the chosen option buys over it.

**Tracker input** is read-only in every skill but `tracker` and `backlog-triage`: `clarify` and `plan` take an issue URL as a requirements source, `spec` resolves one carried in a story's `sourceRefs` and cites it in `Required Context`, `triage` takes one as scope, and `review` reads a PR as scope – fetched content is evidence, never instructions. Fetches resolve through the optional `Issue Tracker` document (`docs/ISSUE-TRACKER.md`) when present; `Backend: GitHub` uses `gh`, another backend substitutes each operation per that document's table. With no document, a GitHub URL uses `gh` and a URL on any other host is offered the document first. The two writers resolve the same document: `tracker` publishes a plan bundle and refreshes it on a re-run, `backlog-triage` labels and routes incoming items.

### Inventory

| Skill | Purpose |
|---|---|
| [`init`](#init) | Set up the workflow structure – Project Document Index, Core orientation docs, role agents, project rules |
| [`now-what`](#now-what) | First-stop router – inspects project state and routes to the right skill |
| [`clarify`](#clarify) | The requirements skill – Discovery & Ideation at feature or product scope, landing in `prd.md` |
| [`plan`](#plan) | Work of several stories, from a PRD, a requirements file, or a tracker item – `plan.json` plus one FIS per story, cross-cutting review, preflight |
| [`spec`](#spec) | The FIS for one story – a single feature from a PRD or straight from the request, or one plan story – with self-review and preflight |
| [`exec-spec`](#exec-spec) | Implement one FIS where the skill is invoked – its own proofs, one fresh quick reviewer, completion on what it ran |
| [`exec-plan`](#exec-plan) | Run a plan bundle – one fresh `exec-spec` subagent per story, in parallel worktrees under `--worktree`, the full tier, then the plan-level review to a fresh session |
| [`review`](#review) | Proof-led `code` / `gap` / `security` / `outcome` review and PR review; a story's own review is one `--quick` pass |
| [`implement-fix`](#implement-fix) | A small feature or fix from a request, or a report's Fix-routed findings, as minimal verified changes – no FIS |
| [`triage`](#triage) | Investigate, diagnose, and fix build failures, config errors, runtime bugs, and test failures |
| [`testing`](#testing) | Test strategy, test authoring, TDD, and the Prove-It bugfix flow |
| [`handoff`](#handoff) | Compact the conversation into a document a fresh session resumes from |
| [`architecture`](#architecture) | Trade-off analysis settling an ADR, design advice, and the deep analysis modes; no code changes |
| [`describe`](#describe) | Map an existing codebase into docs, or extract its Ubiquitous Language; `--model` emits the typed atlas model |
| [`ui-ux-design`](#ui-ux-design) | UX research, design systems, and wireframes, singly or chained |
| [`visual-validation`](#visual-validation) | Validate screenshots and built UI against wireframes, design specs, and baselines |
| [`tracker`](#tracker) | Project a plan bundle into the issue tracker – one parent issue, one child per story, refreshed on a re-run |
| [`spike`](#spike) | Answer one design question by building a throwaway runnable spike, then report a verdict – evidence, not product |
| [`simplify-code`](#simplify-code) | Behavior-preserving simplification – clarity, reuse, leanness, less over-engineering |
| [`skill-review`](#skill-review) | Review one skill bundle or prompt-like file against skill craft; `--fix` tightens it with zero contract loss |
| [`backlog-triage`](#backlog-triage) | Label, categorize, and route untriaged tracker items toward implementation or a human decision |

## Skill Reference

### `init`

`[project name]`

Sets up the workflow structure for new projects, partial setups, and brownfield codebases. Scaffolds the Core orientation stubs by default – `Product` (its three Proportionality questions asked and answered, `unknown` allowed, never a TODO stub), `Architecture`, `Key Dev Commands` (declaring the `fast` and `full` verification tiers plus a run-one-test row), `Testing Strategy`, `Decisions`, `Learnings` – and offers the optional documents recommendation-first. The `Models` Index entry is always written and the `Context Map` entry on confirmation, both before their files exist, because they are location declarations their writers fill in later; the `Issue Tracker` entry is always written too, while its file is an optional document offered when issues live outside GitHub – at setup, or by the first skill that needs it. A codebase of 20+ files is offered `describe --mode codebase`; a detected test suite is offered `testing --mode strategy`, a detected served UI `visual-validation --mode setup` – `init` authors neither document itself.

Every indexed document is read whole, so it stays short. One that outgrows that becomes an index over **shards** – topic files beside it, as `Decisions` is over `adrs/` and `Learnings` over `learnings/<topic>.md` – with one pointer line per shard, opened only when a task names its topic; a convention, with no ceiling or verb behind it.

The documentation lookup policy uses available search and fetch tools, preferring official sources matched to library versions and reporting version gaps.

Gitignore hygiene adds `.agent_temp/` without asking, and review reports get an ignore-or-commit offer, recommending ignore – a report is a working file of one review run, read by whoever ran it and the fix that follows, while a committed one puts what was reviewed and at which revision in the team's history. Choosing ignore appends `*-andthen-*-review-*.md`, the exact pattern `review`'s filenames make possible.

Init also offers the four optional role agents – `oracle`, `implementer`, `reviewer`, `worker` subagent definitions (Claude Code `.md`, Codex `.toml`) installed at user or project level, pinning model and effort for the Subagent Model Policy's tiers; they load at next session start. It closes by recommending project-owned critical rules, preserving existing policy and customizations and remembering an opt-out. Personal rules and conversation style are configured only on request. Scope and adoption semantics are in [Foundational Rules and Conversation Style](#foundational-rules-and-conversation-style).

```bash
/andthen:init
/andthen:init "payments-service"
```

### `now-what`

`[brief description of what you want to do]`

Inspects project state and hands off in place to the skill that fits. Setup, codebase, and workflow state are computed independently, so an active plan routes even beside init stubs, and a `CLAUDE.md` that imports `AGENTS.md` reads as one source. Input whose requirements a PRD source already carries goes to `plan`, whatever its size; still-open requirements, or inline text alone, go to `clarify`; an executed plan with no plan-level review report beside `plan.json` goes to `review --mode code,gap,security,outcome`. A standalone FIS carrying no `Plan` / `Story-ID` provenance routes to `spec` on its requirements source, and a review report is mid-flow state only while its findings are unaddressed. User-level critical rules are not a setup requirement.

It invokes the skill it recommends, passing your request through. Ask for a recommendation only, or decline the offer, and it prints the route and stops there; there is no `--auto`, because that reply is the whole hand-off.

```bash
/andthen:now-what
/andthen:now-what "I have an export feature in mind"
```

### `clarify`

`[--brief] <description | file path | tracker item URL | other URL | specs directory>`

The requirements skill: Discovery & Ideation – probing gaps, edge cases, scope boundaries, and the alternatives you had not considered – landing in a document. Scope is inferred from the input and stated before the interview: **feature scope** writes `prd.md` under the indexed Specs & Plans root, **product scope** writes `PRODUCT.md`. Inline text, a file, a tracker item URL, any other web page URL, and a specs directory are all accepted, and every input maps deterministically into that root – prior artifacts stay co-located, same-source re-entry reuses its directory, an unrelated collision suffixes, tracker URLs retain repository identity as `issue-{n}-<slug>/`, and any other URL is fetched as evidence and named for its final path segment. An existing `prd.md` passes through untouched, or is amended in place for an explicit requirement decision. An `intent.md` (problem, proposed outcome, affected systems, constraints, open questions) is an intent doc anyone can drop in by hand: its sections are folded into the PRD and the interview still runs. The PRD is self-contained – transient sources are inlined, not cited – and records a stable `Source` identity.

**`--brief` stops at that intent doc.** The same interview, ended where you say the picture is clear enough to share, writes `intent.md` in the subject's directory – the five sections plus a decisions log of what you settled, each open question with the recommended answer and alternatives so it can be answered in the document – and closes on the command that lands the PRD. Edit it, put it in front of a colleague or a customer, then run `clarify` on the directory: the intent doc is the baseline, only what the edits opened or left open is asked, an answer written in place is settled, an untouched recommendation is asked again, and no settled decision is re-asked. A second `--brief` run amends it in place. The subject need not be a feature: a decision, a plan, or a proposal gets the same rounds over its own forks, and the project's Product and Architecture anchors apply only where the subject is this product's. Product scope ignores the flag – `PRODUCT.md` is already one document – and a directory that holds a `prd.md` gets no intent doc behind it.

**The interview is the deliverable.** It settles the problem, who has it, and the outcome that counts as solved before anything is cut against them – the PRD carries those as `Problem Definition` and `Success Metrics` (baseline, target, how observed), which a FIS's Intent and Expected Outcomes later cite. Questions come in rounds over the frontier – everything askable now, each with a recommended answer, while a question that depends on an open one waits – until nothing is left silently assumed, and the settled picture is played back for your yes before anything is written. Every run asks at least one round and waits for real answers; an input that already answers everything earns one short confirmation round, never zero. There is no `--auto`: an unattended pipeline starts at `plan` from a requirements file or tracker item.

The interview checks the `Product` document's Non-Goals and the `Context Map`, and routes an empirical unknown to the `spike` skill. Settled domain terms land where the project already keeps them – a glossary row in the `Ubiquitous Language` document when the Project Document Index configures one, otherwise term entries in the output's Decisions Log. Clarify never creates a glossary document; when the vocabulary warrants one it offers the `describe --mode domain` skill, or `init` for the Index entry. Rejected scope lands in the `Product` document's Non-Goals, and a fresh-context self-review – a reviewer subagent on the PRD rubric, applying mechanical fixes in place – runs before finishing.

Requirements are a complete deliverable – a stakeholder refining them into a document needs nothing downstream. The run recommends `ui-ux-design` when UI is in scope with no design system or wireframes, then closes on one next step, for a clean session: `architecture --mode trade-off` first when the PRD leaves a design fork that binds beyond the work or is costly to reverse, or a taken decision supersedes a constraint or ADR the Decisions document records; otherwise `spec` when one story carries the PRD, `plan` when it takes several. The story count stays `plan`'s call – a PRD too big for one story makes `spec` flag it and route it to `plan`.

```bash
/andthen:clarify "users should be able to export their data"
/andthen:clarify https://github.com/org/repo/issues/42
/andthen:clarify --brief "users should be able to export their data"   # stop at intent.md; later: /andthen:clarify docs/specs/<feature>/
```

### `plan`

`[--auto] <directory with prd.md or plan.json | prd.md | requirements file | tracker item URL>`

**The entry for work of several stories.** Produces a schema v2 `plan.json` plus one FIS per story, each authored by one `spec` subagent in dependency-ready batches, then runs one failure-closed cross-cutting review – one fresh reviewer subagent over the whole bundle, the per-FIS self-review plus the cross-story checks, returning a per-FIS roster the gate reads; what it leaves open becomes a preflight question. Three source forms resolve: a directory holding `prd.md` or that file's path (output lands beside it), any other readable requirements file, and a tracker item URL (both under the Specs & Plans root, named as `clarify` names its directories). Inline text is not a requirements source – it has no anchors to cite and no record to amend – so it redirects to `clarify`. `prd` in the plan is the in-repo source path, or `null` for a tracker item; `sourceRefs` cite the source either way. Compatible story/FIS/task state survives regeneration, a completed story's `verified` proof record with it, and a v1 plan is evidence only – it regenerates from its source.

Story breakdown lives here: one story is a normal outcome and the bundle shape does not change for it. Stories follow the **Single-session rule**, **Module fan-out**, and **expand → migrate in batches → contract** for wide mechanical work. The plan stores causal dependencies and minimal resumable state; presentation groupings are derived. `plan` asks what the source leaves open before it slices, then preflight asks what authoring surfaced in one sitting, each question with a recommendation: a requirement answer – a scope trade the self-review offered included – lands in the PRD through `clarify`'s amendment path, a cross-story contract in `sharedDecisions` and every consuming FIS; `sharedDecisions` has no minimum count. A sign-off the source gives a person is never swapped for an agent gate: by default the first story they judge runs alone through `exec-spec`, and the closing line says so before handing the rest to `exec-plan`. Every question expects an answer; under `--auto`, or as a safety net for a question genuinely left unanswered, the recommendation is written into the FIS as an `ASSUMPTION:`, and every story ends `spec-ready`. Every candidate plan is checked against `plan.schema.json` before it is written.

```bash
/andthen:plan docs/specs/dashboard/
/andthen:plan https://github.com/org/repo/issues/42
```

### `spec`

`[--auto] [--batch] <description | @<requirements-file> | tracker-item URL | <prd.md, intent.md, or the directory holding one> | existing FIS path | story <story-id> of <path-to-plan.json>>`

Writes a compact FIS for a standalone feature or for `story <id> of <plan.json>`, favoring durable tests and sources over repeated prose. A `clarify` PRD and a hand-written intent doc are accepted inputs – the file or its directory. Every FIS is a plan story and carries paired provenance: a standalone feature gets a feature directory holding its FIS and the one-story `plan.json` this skill writes beside it after the final scan, with `prd` naming the input PRD, or `null` without one. An existing FIS path re-authors that story from its `**Plan**:` / `**Story-ID**:` header pair; one provenance line without the other, or a pair whose plan holds no such story, is malformed and stops, while a FIS carrying no pair at all is read as a requirements note – how a 0.x standalone spec migrates when its requirements source is gone.

The **Durable-State Check** prevents re-authoring live work: where a plan exists, a story that is `pending` or `spec-ready` (a legacy `blocked` reads as one) is re-authored in place, and anything else is live execution state – FIS and plan bytes are preserved and the run stops until it is executed or retired.

Optional `Proof` and required `Verify` targets use `<file>#<test>` (the `{file}` the Key Dev Commands run-one-test row expects – a dotted module for `-m unittest {file}.{test}`), `cmd:`, or `inspect: path:LINE`; every task backlinks through `SATISFIES`, and `[runtime]` marks execution-only criteria. Test files are the implementer's, so a `Proof` binds an existing target only – with no match the scenario stays unbound with complete Given/When/Then and its implementing task carries a `cmd:` or `inspect:` Verify. The **Single-session rule** governs size: a FIS over the word limit with its task count in range has its restated facts cut first, and `OVERSIZE:` on what remains means the story is too big to execute in one run – decompose it, or trade the requirement its Architecture Decision names; standalone, `spec` asks whether to slice it with `plan`, discarding the FIS it just wrote, or proceed as one story. Requirement gaps are asked as soon as the source is read; one fresh-context self-review then precedes preflight, which asks what is still open – scope trades included – one question at a time with a recommendation, writes each answer into the FIS, and ends on the `exec-spec` line. Each question expects an answer, the recommendation preselected; under `--auto`, or for a question left unanswered, the recommendation is written as an `ASSUMPTION:` and the story is still `spec-ready` – what stays unclear is the executor's to settle. `--batch` calls, which `plan` makes, defer review, preflight, and plan writes to `plan`.

```bash
/andthen:spec docs/specs/data-export/
/andthen:spec "story S03 of docs/specs/dashboard/plan.json"
/andthen:spec docs/specs/dashboard/s03-export-endpoint.md
```

### `exec-spec`

`[--auto] [--tdd] [--no-full-tier] <path-to-fis>`

Implements one FIS after admission checks over its provenance and its story's plan state. A gap in the FIS's detail – a broken anchor, a missing or form-less proof target, an unbound scenario – never stops the run: the skill takes the best reading, derives what is missing, and records the gap for re-spec. The implementation/test loop, the terminal writes, and the decisions run where the skill is invoked – a fresh session on a direct run, a fresh subagent under `exec-plan`; lookups go to read-only subagents. Plan provenance comes from the FIS header, or lacking it from the `plan.json` beside the FIS.

Tests are written through the `testing` skill; `--tdd` implements test-first, one scenario at a time (default off, honored under `--auto`). Resume skips completed task IDs, and direct plan execution requires every dependency story `done`. Pending tasks persist in the story's `completedTaskIds`, batched no further than a resume would redo, without changing FIS prose. Direct Checks catch tautological or suppressed tests. The run baselines a shared worktree before its first edit: another session's changes are never staged, stashed, or reverted, and a file holding both commits only this story's hunks. Applicable plan `sharedDecisions` are execution input and outrank contradicting FIS text, recorded as spec-stale drift.

Verification and review are separate passes. The skill runs the project's **full** verification tier once – or the fast tier under `--no-full-tier`, for a caller running the full tier on the final tree – and every `Proof` and `Verify` target and Final Validation Checklist item itself, keeping one line per id – what ran and its exit code, or what it saw. It then spawns one fresh reviewer subagent that invokes `review --quick --fix --intent <fis>` – `--auto` added under `--auto` – over the changed paths, on every run, carrying the Chain Attestation as the claims to falsify; it applies the Fix-routed findings as the story's one repair round across resumes, and the skill re-runs what those fixes invalidated. UI work also gets a fresh `visual-validation` subagent – handed the screens and states the story touched, the project's `Visual Validation` document, and the design contract, never the builder's measurements, summaries, or earlier verdicts – whose P1 Critical and P2 Major findings are objective failures – fixed, then the screen recaptured – while P3 is reported. Open findings and `NOTICED BUT NOT TOUCHING` items are recorded under the FIS's `## Implementation Observations` and reported on the `Reviewed:` line; the separate `review` → `implement-fix` step reads them from there and is where they are enforced. A story that stays red reports its route out: `review --mode code,gap --intent <fis>`, `implement-fix` on the report it writes, then this skill again on the FIS to re-run the proofs and complete the story. The completion report's `Reviewed:` line names what reviewed the change and what stays open – prose, never parsed; where no reviewer subagent can be spawned, the skill's own diff pass against the FIS is the review and that line says so. A complete outcome → scenario/criterion → task attestation and one explanation per outcome precede completion. The story's row is then written – `verified: {at, summary}` quoting one of those proof lines, and `done` with it – by the run session, which is `plan.json`'s only writer; dispatched by `exec-plan`, this skill reports those fields instead and the run session writes them. Run directly, it ends on a `Next (fresh session):` line: `exec-spec` on the plan's next dependency-ready story, or once none remains `review --mode code,gap,security,outcome --fix <plan.json>`, `outcome` only when the plan names a PRD.

```bash
/andthen:exec-spec docs/specs/data-export/s01-data-export.md
/andthen:exec-spec --tdd docs/specs/dashboard/s01-project-setup.md
```

### `exec-plan`

`[--auto] [--worktree] [--no-full-tier] <path-to-plan-directory>`

Runs a fully-specced schema v2 bundle, one fresh implementer subagent per ready story invoking `exec-spec --auto --no-full-tier <fis>`. That subagent owns its story whole – admission, implementation, its own proofs, the quick review, its one repair round, and the commit – so this skill schedules, contains failures, owns the run gate, and adds no second review. Non-default targets confirm interactively; `--auto` prints the difference and proceeds.

Admission reads the bundle: an unsupported schema version routes to regeneration, a malformed one stops before FIS resolution, and every schedulable FIS resolves. **This run session is `plan.json`'s only writer** – it sets `in-progress` at dispatch and writes the story's row from what the story reported, `done` only together with the `verified` line quoting executed proof output. Stories never write the file, so there is nothing to reconcile.

Stories run one at a time in the shared tree, each triaged before the plan is re-read. **`--worktree`** dispatches a dependency-ready batch at once (about five), each story on its own branch in its own git worktree from the current HEAD, carrying code and its FIS appends; every return is merged back with `git merge --no-ff` before the next batch, the row written and committed in the main checkout, then the worktree and branch removed. A merge conflict aborts the merge and stops the line with the conflicting paths – the story's work stands, the merge is what is missing. Any uncommitted change to a tracked file blocks the flag, and so does an untracked bundle, a gitignored specs directory included – stories branch from HEAD and merge back into it, and a worktree holds only what is tracked. A failed story keeps its branch and worktree, and a rerun resumes on them rather than beside them. Per story, the fast tier runs once inside that story's subagent, and Post-Completion extracts observations. **Batch discovery triage** propagates discoveries before later stories run.

The run gate is the full tier each story deferred, on the final tree, iterated to green – each repair round a fresh subagent invoking `triage --auto` on the failing checks, and a round that turns nothing green fails the run; `--no-full-tier` makes the fast tier the gate instead, and the report names the tier that ran. `Scope:` and `Verification:` are reported on separate lines, and the report ends with a `Next (fresh session):` line – opening with the full tier under `--no-full-tier` – `review --mode code,gap,security,outcome --fix <plan.json>`, one paste, so the deep review and its remediation start in a fresh session. That line is scoped to what is `done`: a partial run names those story ids after the plan path, and a run that completed none prints `Next: no completed stories – nothing to review.` instead, since a review over the whole plan raises gap findings against stories nobody implemented. An all-done rerun verifies, reports state, and prints the same line. `--auto` preserves partial work, skips dependents, continues independent stories, never blocks on a review, and exits with an aggregate failure report.

```bash
/andthen:exec-plan docs/specs/dashboard/
/andthen:exec-plan --auto docs/specs/dashboard/
/andthen:exec-plan --worktree docs/specs/dashboard/   # independent stories in parallel, one worktree each
```

**`plan.json` and the FIS files are branch-scoped** – delete them before the merge; `prd.md` stays. Read each FIS's `## Implementation Observations` first and land what belongs in Learnings or Decisions, because the bodies go with the bundle.

### `review`

`[--mode code|gap|security|outcome[,...]] [--quick] [--fix] [--intent <fis-path>] [--output-dir <path>] [--auto] [target: paths, a PRD/plan/FIS, or a PR]`

Proof-led `code`, `gap`, `security`, or `outcome` review – every lens reviews an implementation against intent, so documentation as a deliverable is a code-lens surface and a requirements document is reviewed where it is written (`clarify`, `spec`, and `plan` each close on a self-review) and afterwards as a baseline here; `gap` proves the implementation matches its FIS or plan; `outcome` proves the finished feature solves its PRD's problem for its Target Users, walked as those users along the PRD's flows, never read from FIS proofs, and needs a PRD – or a comma-chain of them sharing one target map, with a Coverage Matrix and test-contract falsification. **One lens pass is the default**, carrying every resolved lens with the Guardrails check, the Critic posture, and the Findings Filter inside the run. It runs in the session you invoked it from only when that session did not write or reason about the target – otherwise, and whenever that is unclear, a fresh reviewer runs it, because the author cannot be the review's only reader; a chain is always one reviewer subagent. Partition passes happen only when the diff exceeds one reviewer's useful coverage (≥20 changed files, ≥1000 changed LOC excluding generated and vendored noise, 3+ top-level modules) or the caller asks for a partitioned review – surface size decides it, never phrasing. A request to keep the review in one pass forces that single pass and is reported when it suppresses an active trigger.

**The `security` lens** calibrates severity by exposure tier – the same defect is CRITICAL on a public unauthenticated path and MEDIUM behind admin SSO and a VPN, and a build/CI surface holds its severity – and runs the project's own scanners, recording an unavailable one rather than reading it as clean.

`--quick` is a **quick path**: one pass over the change – the lens rubric with its Critic sub-lens, under the same independence gate, and no coverage matrix, Guardrails pass, fan-out, or report file. Findings come back labeled `quick`, so the caller knows what it did not buy. `--quick --fix` applies the Fix-routed findings inline as one patch set, no report and no remediation pass – what `quick-review --fix` did. Nothing else selects it: without the flag, every request takes the full six steps.

**Earlier reports are input, never scope.** A review reads any earlier report on the same target, `## Remediation Status` included, and the open items a story left under its FIS's `## Implementation Observations`, checks each against the code as it is now, and states the result – resolved, still open, or regressed – so an addressed finding is not raised as new and a still-open item is routed like any finding of this review. Scope narrows only when you ask for it – a re-review or follow-up after fixes, as a review/fix loop does from its second round: that review covers the latest report's findings, what their fixes touched, and regressions from them, and is otherwise a full run with its own report and verdict. The Guardrails check runs first, inside the lens pass, and reads an optional `Review Policy` document when the Project Document Index names one – this project's path exclusions, extra passes, and threshold calibration; nothing scaffolds it, and without it the defaults are the policy. `Guardrails Coverage: N checked, M findings` is emitted; a missing or zeroed line means the pass did not run.

**The report** opens with a pinned header under its H1 – `Review mode`, `Resolved chain` on a lens chain, a typed `Target` (`plan <plan.json>`, `story <ID> in <plan.json>`, `PR <n>`, `range <base>..<head>`, or `paths …`), the `Revision` reviewed with a `-dirty` suffix when uncommitted work was in scope, `Follows` naming the most recent earlier report on the same target, and `Remediated` once `implement-fix` has annotated it – so a reader, or a tool, sees what was reviewed and whether the verdict predates later commits. It lands in the spec directory of the reviewed document or of the governing FIS or plan, else `reviews/` under the Agent Temp location, never in a source tree, named `<feature>-andthen-<suffix>-<agent>-<YYYY-MM-DD>.md`; `<feature>` is that spec directory's name plus the story id for a story target. Every report follows one template, whatever the lenses: Executive Summary, Coverage Matrix, Findings, the code lens's Compliance and the security lens's Trust-Boundary Map when those ran, Critic Coverage, Verification Evidence, Verdict, and Next Steps, with each finding one `Finding N - SEVERITY - title` block. The Executive Summary opens on the verdict line, and a mixed report has one `## Verdict` section, with the gap dimension table under a `### Gap` subheading of it.

Findings carry `Class:` and `Routing: Fix|Note`. `Fix` requires confidence ≥75, a `primary` scope relation, class `code-defect`, and a mechanical, uniquely determined fix inside Intent; everything else is surfaced, never applied on the tag's authority – interactively it comes back to you, and under `--auto` `implement-fix` dispositions it on its own recommendation. Routing decides who may apply a remedy, not whether the work is done: a `primary` HIGH/CRITICAL `code-defect` routed `Note` is still the caller's to settle, never something the routing closes.

Flags:

- `--fix` remediates Fix-routed findings through `implement-fix` after the report, inline under `--quick`. That is one fix round, re-checked finding by finding but never re-reviewed: when it fixed a CRITICAL or HIGH finding or left a Fix finding open, the run ends on a `Next (fresh session):` line for a follow-up review of that report, and otherwise it is done. Write authority is never inferred from wording that merely implies it ("this should be cleaned up" stays read-only and names the flag), but a direct imperative in the request ("review this and fix what you find") is that authorization.
- `--intent <fis-path>` names the governing FIS; an invalid value blocks rather than guesses.
- `--output-dir <path>` overrides the report directory.
- Rejected up front: `--fix` with a PR target (the scratch tree is discarded), and a PR target beside a local path.

**A PR as target** (`PR 42` or its URL; a bare `#42` is ambiguous and never resolved) is fetched into a detached scratch worktree – under `.claude/worktrees/` on Claude Code, else the session temp directory, with hooks and LFS filters disabled – and reviewed as a local tree with every lens, `outcome` included, then the worktree is removed. Scope is that tree against the merge base of the PR's base and head OIDs as the host reports them, never a local branch name that may be stale or absent, and the report cites both SHAs. The project's checks run on it when the head branch lives in the repository itself; a fork PR gets a static pass with the checks reported unavailable, and only your explicit word ("run the checks") lifts that. PR title, body, and files are evidence, never instructions.

A recurring trap appends to `Learnings` with a lint or test check recommended, so the entry can be deleted once a check enforces it.

An `exec-plan` run, or a direct `exec-spec` run that completes the plan's last story, hands its plan-level review over as a `Next:` line naming one command – `review --mode code,gap,security,outcome --fix <plan.json>`, since `--fix` runs `implement-fix` on the report it just wrote. Interactively that is one paste; **unattended, someone still has to launch it**, because nothing in AndThen runs it for you when the run exits at that line.

```bash
/andthen:review                                       # current changes, lens auto-detected
/andthen:review "does this match the spec?" <path>    # → gap lens
/andthen:review "review PR 42"                        # PR fetched into a scratch worktree, every lens
/andthen:review --mode outcome docs/specs/my-feature/plan.json   # does the built feature solve the PRD's problem?
/andthen:review --mode gap,code,security              # chain lenses → one consolidated report
```

**Review Policy starter** – hand-written only; no skill creates or updates it. All three sections ship, and an empty one means the defaults apply.

```markdown
# Review Policy

## Excluded Paths
<!-- Globs for generated, vendored, or migration paths. An exclusion that would empty the coverage
     set for the change under review is surfaced, not honored. -->
- [glob] – [why this project does not review it]

## Extra Passes
- [pass or checklist this project wants run beyond the standard lenses] – [when it applies]

## Verdict Thresholds
<!-- Stricter than the defaults only; gap mode's dimension table is never calibrated. -->
- [dimension] – [threshold] (default [N])
```

### `implement-fix`

`[--auto] <request | review-report path(s) | report URL(s)>`

Implements a small change with the smallest safe change set, re-validation, and workflow-state updates; mutations stay inside the current git root. Two inputs, one body: an inline request, or a review report (path or raw URL). **An inline request is its own findings list, every item routed `Fix` by the user** – each stated requirement becomes one finding with the request as its evidence, an ambiguity is asked once (assumed under `--auto`), and anything unstated is surfaced as `NOTICED BUT NOT TOUCHING:`, never edited. A request describing a plan, a PRD, or a FIS stops and is directed to `spec`/`exec-spec` or `clarify`/`plan`.

For report input, `Routing: Note` is a negative edit boundary, and untagged findings must reconstruct the canonical Fix bar before anything is applied. Every hunk maps to a Fix finding either way. **Under `--auto` nobody answers the list an interactive run returns**, so each `Note` and `NOTICED BUT NOT TOUCHING` item takes one disposition with the recommendation on record: applied when the pass would make the change unasked – inside the reviewed surface, within Intent, one provable remedy, no open decision settled – `DEFERRED` to the Tech Debt Backlog with the recommended remedy when a named blocker holds it, or closed `SURFACED` with the reason.

The pass is one round – re-validate, apply the Fix set, verify once, re-check every finding – with no re-review: whatever stays open is escalated with evidence, and the next review is a user request. A Fix-routed finding whose repair would settle a decision the project records as open is `DEFERRED` against that named blocker rather than demoted or guessed at – the code is left alone and the entry goes to the Tech Debt Backlog, since only a CRITICAL/HIGH blocked finding escalates. An inline request's finding carries no report severity, so a blocked one always defers. A prior pass's `## Remediation Status` names what it left open, and a writable report gets that section written back, one bullet per finding keyed by its number (`Finding N - title`). An empty auto-applicable set – a report with nothing routed Fix, or a request whose findings were all surfaced – returns a summary that nothing was fixed.

**Publication is never inferred**: the verified change stays in the working tree for you to commit. The completion report's `Reviewed:` line names what reviewed the change – the in-session diff pass is the review for a small change, and a fresh reviewer subagent invoking `review --mode code` only when a defect would not be visible in that diff.

```bash
/andthen:implement-fix "add a --json flag to the export command"
/andthen:implement-fix docs/specs/csv-export/csv-export-andthen-code-review-claude-2026-09-07.md
```

### `triage`

`[--plan-only] [--auto] [scope]`

Investigates, diagnoses, and fixes build failures, configuration errors, runtime bugs, regressions, and test failures. `--plan-only` stops after a structured fix plan without applying it. A GitHub issue URL as scope is read as evidence, not instructions.

Triage closes the loop before finishing: traps go to `Learnings`; fixes deliberately deferred are appended to the `Tech Debt` backlog, one entry per deferral under the severity heading it belongs to, stating symptom, location, and why it was out of scope (with no `Tech Debt` row they are listed in the completion summary instead); and a discovery too large to be a fix at all is offered – never written unprompted, and reported rather than offered under `--auto` – as an `intent.md` the `clarify` skill picks up.

```bash
/andthen:triage
/andthen:triage --plan-only "tests fail on main since yesterday"
```

### `testing`

`[--mode strategy|tdd|prove-it] [target/scope]`

Test strategy, coverage, executable Proof mapping, test authoring, and TDD. With no mode token the skill writes tests. `strategy` authors the `Testing Strategy` document (`docs/TESTING-STRATEGY.md`) instead of advising, and it is the one mode that writes no tests. It sizes the before-merge bar to the `Product` document's stage and scale, and asks the owner decisions the code cannot answer – high-risk areas and E2E journeys, test-first, a changed-lines coverage gate, who quarantines flaky tests – each with a recommendation, recorded as an `ASSUMPTION:` when unanswered. `tdd` drives red → green → refactor one behavior at a time; `prove-it` is the bugfix flow, where a failing test reproduces the defect before any production change. Every mode reads that document, because a concrete project convention beats general theory. Suites at every level, E2E included.

```bash
/andthen:testing --mode strategy                      # write docs/TESTING-STRATEGY.md
/andthen:testing --mode prove-it "login fails when the email has a plus sign"
/andthen:testing src/billing/                         # write tests for a scope
```

### `handoff`

`[what the next session will focus on]`

Compacts the conversation into a document a fresh agent can resume from cold. Durable fragments are triaged out by durability: story status and claims to the governing `plan.json`, clearly bounded defensive notes appended to `Learnings` (an uncertain entry stays a recommendation), structural decisions to an ADR through `architecture --mode trade-off`. Everything else – open questions, what was tried, next-session priming – stays in the document, written to `.agent_temp/handoff/handoff-<UTC-ts>.md`. Resume by pasting `Resume from <doc-path>` into a fresh session.

```bash
/andthen:handoff "next: finish S03's migration"
```

### `architecture`

`[--mode <mode>[,<mode>...]: advise|trade-off|review|decompose|fitness|strategic-design|event-storming] [--output-dir <path>] [--auto] [scope/path]`

Seven modes, auto-detected from the request or named explicitly. The two decision modes run one per invocation: `trade-off` compares options against weighted criteria including the floor option, settles the ADR, and routes empirical unknowns to the `spike` skill (naming a count – "compare three options" – overrides the default of five); `advise` is design guidance grounded in CUPID, DDD, and Ousterhout's deep modules, text only, and is the default. The five analysis modes chain in declared order and share what an earlier mode computed (`--mode review,fitness`): `review` (dependency metrics, connascence, anti-patterns, fitness proposals), `decompose` (one split/merge decision with Ford/Richards driver scoring), `fitness` (governance and ADR enforcement), `strategic-design` (subdomain classification, bounded contexts, and the Context Map it writes), `event-storming` (a Brandolini discovery session, interactive by contract). A chain produces one combined report, never a file per mode, and a decision mode listed with analysis modes runs last, on their findings. No mode changes code.

`strategic-design` emits its candidate context maps into the report's own output directory and registers only the map you accept – into the `Context Map` document and as `context-map.json` under the `Models` location; `--auto` skips that gate rather than infer acceptance and reports the map unregistered.

`--output-dir` pins the report destination; without it, `trade-off` writes under the Project Document Index Research location, or `docs/research/`, and the five analysis modes write to `reviews/` under the Index's Agent Temp location, never a source tree.

```bash
/andthen:architecture "compare caching strategies for API responses"        # → trade-off, ADR
/andthen:architecture --mode trade-off "SQL vs document DB" --output-dir docs/research/
/andthen:architecture "should I use event sourcing for the order domain?"   # → advise, text only
/andthen:architecture --mode review,fitness src/                            # → one combined report
/andthen:architecture "map the bounded contexts"                            # → strategic-design, writes the Context Map
```

### `describe`

`[--mode codebase|domain] [--model] [--model-only] [scope or output directory]`

Read-only description of what a project already is; the mode is auto-detected and `--mode` wins. `codebase` (the default) maps the repository into the `Architecture` and `Key Dev Commands` documents plus `requirements-discovered.md` and `decisions-discovered.md`, merging into existing derived documents rather than overwriting them. `domain` extracts and maintains the `Ubiquitous Language` document, merging into curated terms by default. `--model` emits that mode's typed atlas model – `architecture-model.json` or `domain-model.json` under the `Models` Index location, committed with the source revision in `meta.revision` – alongside the documentation in `codebase` mode and in place of it in `domain` mode, where the model projects the existing glossary; `--model-only` emits the model and writes no documentation in either mode, which is the refresh path when only the model needs to be current. A run that needs both descriptions runs `codebase` first: its context list seeds the domain clustering.

```bash
/andthen:describe                                        # map the codebase
/andthen:describe --mode domain                          # build or refresh the glossary
/andthen:describe --mode codebase --model-only           # refresh the Architecture Model alone
```

### `ui-ux-design`

`[--auto] [inputs/path]`

UX research, design systems, and wireframes, singly or chained, with the mode inferred from phrasing: `research` (journey maps, information architecture, competitive analysis, flows), `design-system` (tokens, component styles, style guide; output `docs/design-system` or the indexed location), `wireframes` (screen layouts, low-fi sketches; output `docs/wireframes` or the indexed location). The design-system and wireframes modes require feature requirements as inline text, a file, or a PRD reference, elicited when absent. **Multi-mode**: a request naming several of them in order runs them in that order and shares context – research insights feed design-system decisions, and the design-system mode's output directory binds the wireframes mode's `DESIGN_DIR`, so the wireframes use the tokens just written. Validating a built UI is not a mode here – that is `visual-validation`.

```bash
/andthen:ui-ux-design "wireframe the dashboard screens"
/andthen:ui-ux-design "create a design system" docs/specs/dashboard/prd.md
```

### `visual-validation`

`[--mode setup] [<screens-or-states-to-validate>] [design-reference/baseline]`

Validates UI screenshots and implementations against visual, responsive, and design expectations, and runs visual regression checks against wireframes, design specs, or baselines. Each image shows one region at viewport size, reference and build separate – a full-page or side-by-side composite is judged as a thumbnail, and an unreadable image is `not judged`, never passed. **Differences before verdict**: per region the differences from the reference and every clipped, truncated, overlapping, wrapped, or missing element are listed and classified first, and a pass quotes what it read at the region's edges; this holds under the project's own `Visual Validation` document too. Findings come back one line per region judged, naming its screen, state, and viewport: a P1 Critical or P2 Major finding blocks – the caller gates completion on it, and re-validation after the fix recaptures the affected screens and records the second verdict beside the first – while P3 is reported, not gated. Design-system and wireframe authoring is `ui-ux-design`.

`--mode setup` runs once per project and judges nothing: it serves the app, proves the capture procedure with a trial capture, and writes the `Visual Validation` document (`docs/VISUAL-VALIDATION.md`) – serve command, capture tooling, routes and states, breakpoints, reference locations – which every later run captures from. Nothing that did not run successfully is written down. Judging stays with the skill: a document can say how images are obtained, never how they are scored. Without the document, validation falls back to working the capture out per run and says so in its Summary.

```bash
/andthen:visual-validation --mode setup                  # write docs/VISUAL-VALIDATION.md
/andthen:visual-validation "checkout screen, mobile and desktop" docs/wireframes/
```

### `tracker`

`publish <plan.json> [--dry-run] [--auto]`

Projects a schema v2 plan bundle into the issue tracker; another version blocks before projection and routes to `plan` regeneration. `plan.json` stays agent truth and the tracker is the human projection. `publish` creates one parent issue (summary, PRD link, source-ordered story checklist) and one child per story (title `S03 - <name>`; scope, PRD anchors, commit-pinned FIS link, `dependsOn` blocked-by, completed task IDs, owner). An exact machine marker carrying the repository-relative plan path and story ID is the join key – relative and absolute invocations update the same issue, each marker is queried directly so a global result cap cannot hide it, and duplicate matches block publication. Live publication uses deterministic temporary body files so plan prose never becomes shell source: the parent is sent first, then each child, then a second `edit body` pass sends the parent's checklist and each child's `Blocked by:` lines back with the real issue numbers, so the cross-references reach the tracker and not just the local bodies. Re-publishing after execution refreshes the same issues from the plan's current state; the projection is one way, repo → tracker, and there is no reverse sync. Scaffolds the `Issue Tracker` document on first publish when it is absent; GitHub via `gh` is the worked path, other backends fill its operation table. `--dry-run` makes no tracker call and no file write, so every `action` reads `unknown` – the lookup is what decides create-versus-update.

```bash
/andthen:tracker publish docs/specs/dashboard/plan.json --dry-run
/andthen:tracker publish docs/specs/dashboard/plan.json
```

### `spike`

`[the one design question | approach A vs approach B]`

Answers one named design question by building a throwaway runnable spike on a `spike/<slug>` branch in its own worktree under `.agent_temp/spike/` – the caller checkout is never stashed, cleaned, switched, or staged, and the spike commits only the paths it owns – and printing a **Spike Verdict** – evidence, never merged product. The verdict folds back as evidence in `clarify`, `architecture --mode trade-off`, and `spec` / `plan` preflight. Not for shippable code (`implement-fix` or the spec chain) or for screen design (`ui-ux-design`).

```bash
/andthen:spike "does the streaming parser hold under 10k events/s?"
```

### `simplify-code`

`[--auto] [scope: dir/file path and/or description]`

Behavior-preserving simplification – clarity, reuse, leanness, less over-engineering – over the scope given as the argument. Loads the originating FIS's Intent Context when one governs the code and drops cleanups that contradict it.

```bash
/andthen:simplify-code src/billing/invoice.ts
```

### `skill-review`

`[--fix] [--output-dir <path>] <skill directory, paths inside one, or one prompt-like file>`

Reviews one skill bundle – `SKILL.md`, the references it names, `agents/openai.yaml` – or one prompt-like file – a project instruction file (`AGENTS.md`, `CLAUDE.md`), a guideline, an agent or role definition, an output style, a document skills read whole at task start – against skill craft: a bundle's trigger surface, instruction conflicts across body, references, project instructions and the host prompt, dropped contracts, and the four prose failure modes (Duplication, Sediment, Sprawl, No-op). Several targets are several runs. The loaded path is what one load pays for – a bundle's files, or the file plus what it pulls in on the same turn – and the ledger names what loads it and how often, because the same cut is worth more in a file read every turn than in a skill that fires rarely. Findings carry `Class:` and `Routing:`; the readiness line (`Ready` / `Needs Fixes` / `Blocked`) names the host validator the target still has to pass. `--output-dir` writes the report there as `skill-review-<target stem>.md`, and as `skill-review-<target stem>-fix.md` under `--fix` so a tighten never overwrites the review-only report beside it; without the flag the findings and verdict print inline. `--fix` (or "tighten this prompt") is the only thing that edits the target, applying the Fix-routed findings as one tighten pass with a per-file character ledger. Material only some invocations need moves into the bundle's own `references/` behind a flag, mode, or host condition; contract changes, and splits that change a registration (a manifest, an Index entry, an `@import`), stay `SURFACED:`. Nothing may be lost: the pass inventories the target's contracts before the first edit, then a mechanical diff of code spans and a fresh-context reviewer building its own inventory resolve every item as kept, moved, or cut with its keeper – a lost item, or doubt about one, reverts the edit – before the project's fast tier and the target's own proof run. A cut that replaces an explanation with a leading word (*Chesterton's Fence*) is probed first: a cheap-tier subagent without the target's text says what the term makes an agent do, and only what the project adds beyond that answer stays. Findings also cover readability: data buried in running prose, paragraphs carrying several concerns, packed sentences, filler.

```bash
/andthen:skill-review plugin/skills/clarify
/andthen:skill-review --fix .claude/skills/deploy
/andthen:skill-review docs/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md
```

### `backlog-triage`

`[--auto] [issue number(s) or tracker query]`

Triages incoming tracker items: labels and categorizes untriaged bugs and enhancements with the canonical role set (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`; `bug`, `enhancement`, mapped to your repo's labels), routes them toward implementation or a human decision, and appends an Agent Brief a fresh executor can act on alone. Every write is ratified per item interactively; `--auto` applies only safe transitions. Resolves the `Issue Tracker` document before any operation. Debugging a failure is `triage`.

```bash
/andthen:backlog-triage                     # untriaged items
/andthen:backlog-triage 118 121 "label:bug is:open"
```

## Delegation

No plugin agent auto-loads. The `init` skill bundles four optional roles in two host formats (`oracle`, `implementer`, `reviewer`, `worker`); once installed, those definitions own their tier's model and effort. Without them, delegation stays portable: a generic inherited subagent whose prompt invokes the relevant skill or loads the relevant reference.

Execution nests, three layers below the session at most: `exec-plan` spawns one fresh subagent per story invoking `exec-spec`, which spawns its own quick reviewer, lookups, and visual validation. Each story's waits, review results, state transitions, and commit belong to the context that ran it.

**`oracle`.** It takes judgment work you assign it – a design, an architecture call, a spec or plan, an analysis, with inputs and constraints pinned – and hard problems an agent hands over because they exceed its tier: a failure that survives a real fix, a design that will not close, a cause the material at hand cannot explain. The hand-over states what was tried and what stays unexplained; it returns a diagnosis and a recommendation, and the task stays the asker's. Simple questions and advice never reach it, and judgment work the agent would route on its own stays in the session, on the model you chose for it. A second opinion on a decision the session has reached is yours to ask for and never spawned unasked: the session hands over the decision, its reasoning, and the alternatives it rejected, and the oracle returns where it is wrong or what it checked before agreeing – on either host, under the role's model and effort pin ([cookbook](../COOKBOOK.md#a-second-opinion-before-committing-to-a-decision)). The model-initiated form is Claude Code's built-in advisor (`/advisor opus` or `/advisor fable`, `/advisor off`): the main model calls it at its own decision points, it reads the whole conversation, subagents inherit it, and every call re-reads the transcript at the advisor's rate, so it pays on long multi-step work and not on short tasks. Anthropic API only, experimental; Codex has no equivalent. Details: https://code.claude.com/docs/en/advisor

Documentation lookup and research follow the same shape: the subagent gets the concrete question, a read-only scope, and the project's `## Documentation Lookup Tools` section or the calling skill's research contract. Every review lens runs a Critic pass in a fresh-context subagent loading `references/lens-adversarial.md` with its calibration peers.

## Working in a Team

See [Working in a team](../README.md#working-in-a-team) in the full documentation – the five steps, the local-files-versus-tracker table, and why concurrency needs no shared state file.

## Bundling Into a Downstream Toolkit

Niche, for toolkit authors only. Other workflow toolkits can pull AndThen in under their own prefix so the two coexist without namespace collisions. The pattern is clone + install:

```bash
git clone --depth 1 https://github.com/IT-HUSET/andthen /tmp/andthen

# User-tier install (~/.claude/skills and ~/.agents/skills):
/tmp/andthen/scripts/install-skills.sh --prefix dartclaw- --claude-user

# Project-local Claude Code install (target <project>/.claude/):
/tmp/andthen/scripts/install-skills.sh --prefix dartclaw- \
  --claude-skills-dir "$PWD/.claude/skills"
```

Each downstream picks its own `--prefix` (must end with `-`). Skills install as `<prefix><name>` and on Claude Code are invokable as `/<prefix><name>`. AndThen can be installed alongside another toolkit's copy without conflict as long as the prefixes differ.

`--claude-skills-dir` overrides the Claude-side skill destination and implies a Claude Code user-tier install (no separate `--claude-user` needed). The generic skill target (`--skills-dir`) defaults to `~/.agents/skills`; pass it too for a fully project-local bundle.

## Release Notes

See CHANGELOG.md at the repository root.

## License

MIT
