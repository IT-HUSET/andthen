# Changelog

All notable changes to **AndThen** are documented here, in a brief and concise format.
Follows [Semantic Versioning](https://semver.org/) and [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.


---

## [1.0.0-rc.4] – 2026-10-05

### Changed
- **`spec` and `plan` merge into `plan`, and `exec-spec` and `exec-plan` into `exec-plan`.** `plan` writes `plan.json` plus a FIS per story, a single story included, and sizes a written source itself unless you ask for one story; `exec-plan` runs either, and under `--worktree` first commits a missing `Key Dev Commands` document on your branch. `MIGRATING-FROM-0.x.md` maps the old commands.
- **`decide`, the 18th skill, makes and records technical decisions.** It interviews you over the choices a solution needs, recommends each, and writes an ADR, or a `Decisions` line where there is no real alternative. `architecture --mode trade-off` is gone and `advise` no longer writes ADRs ([ADR-025](docs/adrs/ADR-025-decide-skill.md)).
- **`ship`, the 19th skill, closes out a branch.** It lands each FIS's Implementation Observations worth keeping as `Learnings` bullets, recommends the `Decisions` and upstream edits, deletes `plan.json` and the FIS files, repoints links into them, commits, and after one confirmation pushes and opens the PR. The PR states the change's intent, outcomes, and proof (each story's `verified.summary` and the review verdict) in the project's PR template when there is one, with a diagram where a picture reads faster; the confirmation shows the base branch and marks commits the review never saw. `--auto` stops before the push. A plan-level `review`, `implement-fix` on its report, and `now-what` end a ready plan on `Next (fresh session):` for `ship`; a deferred CRITICAL or HIGH finding still ends `review` and `now-what` on `Next: blocked –` with its blocker ([ADR-026](docs/adrs/ADR-026-ship-skill.md)).
- **`visualize` returns as the 20th skill, rebuilt small.** It draws an AndThen artifact, such as the architecture or domain model, a context map, an event storm, or a plan, as one self-contained HTML page with inline SVG figures under `.agent_temp/visualize/`. It renders the page in a browser and fixes what it sees before handing it over, or says the page is unchecked when no browser is reachable. 0.x modes, templates, and the notes loop stay retired ([ADR-027](docs/adrs/ADR-027-visualize-skill.md)).
- **Skill recommendations print the full invocation**, in the host's syntax with the target or request and required arguments, ready to paste. `clarify`, `decide`, `architecture`, `ui-ux-design`, `plan`, `exec-plan`, and `review` end on one `Next (fresh session):` command rather than a menu. Design joins the path when you choose it, at `clarify`'s playback or in `plan`.
- **`exec-plan` runs `simplify-code` once a plan is built**, over the plan's code before the review, never per story.
- **`--auto` is the only way to run unattended.** Without it every skill asks what its text says to ask, however it was launched; with it, the flag passes to every nested skill, and a consent-needing action incidental to the call is skipped and named.
- **A question is asked where you can answer it.** A skill's asking turn ends on the question, so a run no longer proceeds past an unanswered choice. It uses the host's question tool wherever that tool waits for your reply, over several dialogs when one holds too few questions.
- **Skills settle a question only where a line states the answer.** `clarify` and `plan` otherwise ask, or offer their reading as a recommendation, and `plan` closes by listing every open item with what settled it. A cited decision never vouches for an untested claim about how code behaves: their self-review raises it as a question to test. `review` withdraws a finding or calls a spec stale only on a line it cites.
- **Outcome and end state are asked, not assumed.** `clarify` plays both back before writing; `plan` asks when its source leaves them open, puts its own draft to you when there is no PRD or intent doc, and routes a source too thin to draft them to `clarify`.
- **Changes tidy the files they touch.** `exec-plan` stories, `implement-fix`, `triage`, and `testing`'s refactor step make small Boy Scout tidies there, behavior kept or an obvious bug fixed under a test, and name them in the report. `NOTICED BUT NOT TOUCHING` is kept for what someone should act on. The critical-rules starter says the same: re-copy it where you installed an earlier one.
- **A requested change that contradicts a recorded Non-Goal is your decision.** An attended run asks; an unattended one leaves the change unmade and records an `ASSUMPTION:` line.
- **`backlog-triage` is now `tracker triage`.** `tracker` takes `publish`, `triage`, and `setup`; a non-GitHub issue URL without an `Issue Tracker` document gets an offer of `tracker setup`, and `tracker publish` no longer sets an assignee.
- **Plan stories are `pending`, `in-progress`, `done`, or `skipped`.** A `pending` story with its `fis` set is ready to run, and a story's `provenance` says why no source covers it, or is `null`. An older plan runs as it stands: `spec-ready` and `blocked` read as `pending`, `owner` is ignored, and a story with any other status stays unstarted and is named in the run report.
- **Each story writes and commits its own `plan.json` row**, a failed one staying `in-progress` and a `skipped` one still blocking its dependents; a re-run redoes its tasks. Under `--worktree` the plan run commits each batch's rows as `in-progress` before it branches, and a merge conflict made only of lines both sides appended to the changelog or `Learnings` keeps both sides.
- **`plan` no longer revises an existing FIS or `plan.json`.** Revising a spec or re-planning is a prompt; the Cookbook's [Revising a spec or re-planning](COOKBOOK.md#revising-a-spec-or-re-planning) recipe says what to write.
- **Skills hand off in words, not mode flags.** `exec-plan` prints a plain `review --fix <plan.json>`, and `review` picks the lenses the plan supports, `security` when its trigger fires; `testing` likewise picks its mode from the request when `--mode` is absent. `review --intent` is gone: a FIS the request names governs the review.
- **A follow-up `review` runs its normal scope** and says which earlier findings are resolved or still open. It no longer offers a narrower rerun.
- **`implement-fix` adds to the Tech Debt backlog only with your approval**, and `--auto` writes every deferral, a blocked CRITICAL or HIGH finding included. It no longer writes `plan.json`, routes to a re-spec, or runs fix groups in parallel.
- **`init` asks only what it cannot infer.** It writes the instruction file with the full document index, `Key Dev Commands` from your manifest, and `.gitignore` entries, review reports included; other documents are created by the first skill that writes to them, through `init seed <entry>` where that skill lacks the template. The first `clarify`, `decide`, `plan`, or `architecture` run asks the project's stage and scale, and role agents and critical rules are one-line offers.
- **The Project Document Index gives each document a `###` heading** over the `Description`, `Read`, and `Write` bullets that apply. The older bullet shape keeps working.
- **`describe` and `architecture` ask for the mode** when the request names none; `advise` is no longer `architecture`'s default. `--model` in domain mode extracts the glossary before projecting it, and `--model-only` extracts a missing one instead of stopping.
- **Model tiers are named S, A, and B.** Installed role definitions pin the current model and effort per tier and host. Without those roles, skill dispatch uses a generic subagent that inherits the session model.
- **Every subagent a skill spawns names its role**, and `triage` hands a problem to an installed `oracle` once before its three-failed-fixes stop.
- **`architecture` weighs Locality of Behaviour** against separation of concerns, and its review flags indirection only where it buys the caller nothing.
- **`testing` names tests that cannot fail or are coupled to structure**, its Anti-Cheat Invariant binds every mode, and `review`'s code lens checks the same as Falsifiability. Where the project runs a mutation tool, `testing` counts surviving mutants as missing assertions and `strategy` asks whether to gate on it.
- **Skills load less**, a story in a plan run about 2,400 fewer words.
- **Optional hooks brought up to date, plus a context-size hint.** `block-dangerous-commands.py` catches more `rm` and quoted-command forms, including executables after wrappers, and no longer lets `| cat` through; the notify hooks need a new `UserPromptSubmit` entry; `reinject-context.sh` is removed. The new `context-hint.py`, a `Stop` hook for Claude Code and Codex, tells the agent the session's size once it passes 200k tokens, so its closing line can suggest a fresh session.
- **Shorter, plainer docs.** The README leads with what AndThen is and a quick start, the skill reference is half as long, and the workflow reference, team work, and the framework comparison live in the Cookbook.
- **`skill-review` leaves the plugin.** It is a project-level skill for contributors to the AndThen repository.

### Fixed
- **A description always produces a FIS.** An inline description is one story, and one too big for a single run is caught by `OVERSIZE:` after its FIS is written.
- **A plan review leaves `skipped` stories out of its gap baseline**, and reads a requirement only they cite as `not reviewed`.
- **A failed story no longer strands its dependents**, which a later run still takes, and running a story before its dependencies are done asks you first.
- **`now-what` routes more cases right, and asks less.** A spec'd single story goes to `exec-plan` on its FIS, an architecture report to `decide`, and a terminal plan's failing load-bearing check to `triage`; shipping readiness follows the canonical plan contract. It no longer asks whether the project is new, ends on a menu, or passes your request to `init` as a project name.
- **Off-template input is worked with.** `plan` plans from a directory of requirements files, `tracker publish` and `review` read a plan of any `schemaVersion`, and `implement-fix` fetches a report from any link. `tracker publish` stops, naming the field, on a malformed `fis` or `sourceRefs` or a repeated story id.
- **`Backend: none` means the project has no tracker**, and `tracker` ends on one line saying so.
- **The `Context Map` keeps every channel of a context pair.** Its integration table gains a `Channel` column, so `architecture` no longer overwrites a pair's first channel with its second, and `describe --model` gives a mapped context the map's id.
- **An event-storming re-run continues its board** instead of replacing it, so the answers an earlier session settled survive, and a Big Picture report names each event's actors. A board's `order` is a column on one timeline all lanes share, so a pivotal event divides every lane; per-lane numbering made boards draw cuts the session never made.
- **`exec-plan --worktree` merges only a story's own work.** A misplaced story fails instead of reaching `done`, and a failed story resumes after its siblings merge.
- **`clarify --brief` asks before it writes**, and `clarify` leaves a non-requirements file at its target path alone.
- **Two skills stop contradicting themselves.** `ui-ux-design` validates wireframes per viewport, never as full-page screenshots, and its bold visual direction applies to design systems, not grayscale wireframes. `describe --mode codebase` writes the `Architecture` document from one subagent, so the testing overview no longer overwrites its body.
- **Smaller fixes.** An unattended `review` prints the absolute report path, an unattended `simplify-code` no longer stops on checks that were already failing, `triage` hands a discovery too big to fix to `clarify --brief` instead of writing its own `intent.md`, `clarify` no longer creates a glossary the project does not keep, `testing --mode strategy` says when no Proportionality facts sized its bar, `init` recognizes a custom critical-rules policy, no longer names a missing commands file, writes the skip marker when you decline the critical rules, and ends a rules update at the guideline's own last heading, the one-story plan records its source, and the critical-rules starter lets an agent resolve a merge conflict whose intent is clear, constrains shell commands only where a person approves them, leaves fresh sessions to each step's `Next (fresh session):` line, and, like `exec-plan` and `ship`, commits by path (`git commit -- <paths>`), so another session's staged change stays out of the commit.


## [1.0.0-rc.3] – 2026-09-24

### Changed
- **`architecture` grades against Ousterhout's deep modules by name.** The calibration uses the book's terms – shallow module, information leakage, temporal decomposition, pass-through method, define errors out of existence, design it twice – for any in-process interface, packages included, and never for service boundaries. Two misfire traps return: an error is defined out of existence only when the absent case is valid state, and testability never justifies splitting a deep module. A God Module needs all three of its thresholds – LOC, Ce, and mean cyclomatic complexity – and high Ce alone is only a signal. The mode references drop textbook framework content the model already knows and statements made twice.
- **Code review attacks production scale again.** The code lens gains a conditional Scale dimension – N+1 and missing pagination, unbounded result sets, algorithmic growth, long foreground work – that runs when a change touches a query, a collection walk, a request path, or a data-volume boundary. Severity needs an anchored cardinality – the Product document's Scale fact, a requirement, or a reachable exhaustion path – so speculative optimization stays out of reports.
- **Unattended runs disposition every surfaced item.** `implement-fix --auto` no longer lists Notes for a reader who is not there: each `Note` and `NOTICED BUT NOT TOUCHING` item is applied when the pass would make the change unasked and it settles no open decision, `DEFERRED` to the Tech Debt Backlog with the recommended remedy, or closed with the reason. `review` reads a story's open items from its FIS's `## Implementation Observations` as it reads earlier reports, `exec-spec` records its quick review's open findings there and passes `--auto` to that review, and `review --fix --auto` no longer skips remediation on an all-Note report.
- **`exec-spec` executes the FIS instead of auditing it.** A broken anchor, a missing or form-less proof target, an unbound scenario, or FIS text a shared decision contradicts no longer stops the run: it takes the best reading, derives what is missing, and records the gap for re-spec. It still stops when no defensible implementation exists.
- **Leaner FIS.** `spec` writes only what the executor would miss, nothing the project documents, the code, or a cited source already says. Fewer sections: retired ones fold into Architecture Decision (`Flow`), the tasks, Constraints & Gotchas and the Final Validation Checklist; an older FIS is read as-is.
- **Preflight asks, then hands off – no `Closure:` verdict.** `spec` and `plan` ask what the requirements leave open, each question once with the recommendation preselected and no defer option, then end on the one next command. Under `--auto`, or for a question left unanswered, the recommendation becomes `ASSUMPTION: <what was assumed> – <what would change it>` in the FIS; stories always end `spec-ready`, and `OVERSIZE:` is advice.
- **A decision never stops a run.** It is asked once with a recommendation, or taken as an `ASSUMPTION:` under `--auto`; only an unusable call – missing input, credentials, or consent – stops, as `BLOCKED: <what is needed>` under `--auto`. `CONFUSION:`, `MISSING REQUIREMENT:`, `NO-OP:`, and the `blocked` story status retire; an existing `blocked` row reads as `spec-ready`.
- **Where to start is two questions.** Unsure what to build → `clarify`; then one story → `spec`, several → `plan`. `spec` now takes a PRD and records it in its one-story plan, and `clarify` closes on `spec` or `plan` – or on `architecture --mode trade-off` first when the PRD leaves a fork that binds beyond the work or is costly to reverse.
- **`exec-spec` and `review --fix` print the next review.** A direct `exec-spec` prints a `Next:` line – the plan's next story, or the review once none remains – and `review --fix` prints a follow-up review when its one fix round fixed a Critical or High finding or left one open.
- **`architecture --mode advise` asks Farley's two probes.** What must be built or mocked to test a component, and which dependency lengthens the path from a change to confident production – with the caveats that a deep module is tested through its interface and a business release gate is not coupling.
- **Review reports have one format.** Every `review` report, single lens or chain, follows one template: fixed section order, one finding block shape with severity in its heading only, and one verdict line per mode that the Executive Summary opens on. The per-lens section lists retire; `Recommendations`, `Remediation Plan`, and `Recommended Next Action` become `## Next Steps`, and `Cleanup Required` items are findings. `implement-fix` keys each `## Remediation Status` bullet by finding number.
- **`testing --mode strategy` asks what the code cannot answer.** It sizes the before-merge bar to the `Product` document's stage and scale and asks, recommendation-first, for high-risk areas and E2E journeys, test-first, a changed-lines coverage gate, and flaky-test quarantine ownership; unanswered choices land as `ASSUMPTION:`. Sociable tests (real collaborators, doubles only at trust boundaries) are the default, and an agent never quarantines a flaky test. `exec-spec` and `implement-fix` now write every test through the `testing` skill, so its test-design rules apply outside TDD too.
- **`concise-critical` is shorter and less cryptic.** Concision is one short-by-default rule (one to three sentences for a simple question, only what the user must decide or act on, full substance kept), and the counter-rules that repaired over-compression are gone. Explanations keep the context the user never saw, define project terms, and keep their "because"; a question says what is being decided, why it matters, and what each answer leads to. Codex: re-paste `developer_instructions`.
- **The README and overview figure lead with the one-story path.** `spec` → `exec-spec` comes before `plan` → `exec-plan` in the figure and in *Your first feature*, which now also explains fresh sessions and which review runs where. The release-line switcher section is gone – the develop-branch install commands cover it – and `MIGRATING-FROM-0.x.md` is rewritten shorter, loose-install cleanup last.

### Fixed
- **`plan` asks what its story specs had to assume.** An `ASSUMPTION:` a story subagent wrote because it could not ask is now a Preflight question outside `--auto`, not a settled answer, and a recommendation no longer closes a question by itself – it is the preselected answer you confirm. The reply ends on the questions, and a recommendation you ratify is written into the spec as a decision, not left as an assumption.
- **Every hand-off says to start a fresh session.** `clarify`, `spec`, and `plan` close on `In a fresh session, run …`, and `exec-spec`, `exec-plan`, and `review --fix`'s follow-up review end on a `Next (fresh session):` line – the clean-session advice 0.x gave, lost in the 1.0 rewrite.
- **`exec-plan`'s final gate iterates to green.** A red build or test on the final tree gets repair rounds until green, not one attempt; a round that turns nothing green fails the run. The one-round cap stays with review findings.
- **Completed-story proof survives plan regeneration.** `plan` preserves a done story's `verified` record with the rest of its runtime state and drops it when the story resets; `plan.schema.json` now rejects a `done` story without a `verified` record or a FIS.
- **Non-GitHub trackers configure at first use.** `clarify`, `plan`, `spec`, `triage`, and `backlog-triage` no longer guess when the `Issue Tracker` document is absent or says `Backend: none` and the issue is not on GitHub, or its `Backend:` line is malformed – they offer to set it up and resolve against it, and under `--auto` they stop, naming the `Backend:` line to set. `init` lists the document among its optional documents.
- **`architecture` floor row and unattended close.** The ADR template's floor option reads `chosen` when it wins instead of always `rejected`, and `--auto` closes on a report path only for a mode that writes one.
- **C4 altitude reads consistently.** A finding's `location` names the element at any C4 level, so a service-boundary finding can tag Container; the `ARCHITECTURE.md` template lists deployable units before their modules when a system runs more than one process.
- **`cmd:` proofs run on any host.** A FIS `cmd:` uses only the project's toolchain and `git` (`git grep` to search), never a tool like `rg` or a POSIX idiom the executing host may lack.
- **Architecture model node kinds have meanings.** `service`, `entrypoint`, `store`, and `external` are defined, so `describe --model` no longer files a third-party library beside a runtime system; libraries are not nodes.
- **The `architecture-review` fixture follows the report contract.** Its finding carries the full field set with an allowed dimension, and its dashboard the contract's columns. The review tooling table is marked as examples and names `lizard` for complexity in every listed language but Dart.

## [1.0.0-rc.2] – 2026-09-09

The 1.0 release candidate, and a breaking one; everything here is relative to 0.40.4. AndThen ships as one
plugin – `andthen`, 21 skills: the whole workflow plus five standalone tools – and a story reaches `done` only on
executed proof. Options whose situation was prose rather than a machine contract are gone, replaced by saying
what you want in words. Retired command aliases and legacy
FIS execution are gone – a 0.x FIS is re-specced before it runs. `MIGRATING-FROM-0.x.md` has the migration: a
copy-paste prompt that inspects a project before changing anything, and every retired surface with its 1.0
disposition.

### Added
- **Five standalone tools beside the pipeline.** `spike`, `simplify-code` (was `refactor`), `backlog-triage` (was `issue-triage`), `tracker`, and `skill-review` install with `andthen`; `tracker` projects a plan bundle, the other four need no plan, spec, or setup to run ([ADR-018](docs/adrs/ADR-018-one-plugin.md)).
- **One writer for `plan.json`.** The session running `exec-plan` or `exec-spec` edits the story rows itself against `plan.schema.json`; a story subagent reports its state and never opens the file, so parallel stories cannot lose a row ([ADR-003](docs/adrs/ADR-003-runtime-state.md)).
- **Proof-bound completion.** `Proof`/`Verify` have three runnable forms – `<file>#<test>`, `cmd: <command>`, `inspect: path:LINE` – and every task backlinks its scenario or `SC<NN>` criterion with `SATISFIES`. `exec-spec` runs them with the project's test tier and writes one output line into the story's `verified`, without which `done` is never set; the plan keeps that trace after the bundle is deleted. A `[runtime]` tag, never the wording, marks what an `inspect:` proof cannot cover.
- **`review` gains an `outcome` lens.** Where `gap` proves the implementation matches its FIS, `outcome` validates the finished feature against its PRD, walked as its Target Users; PRD-side findings route to `clarify`. It needs a PRD and runs in the plan-level chain `exec-plan` hands over.
- **`review --quick`.** One pass over a diff – no coverage matrix, no fan-out, no report file, findings labeled `quick` – replacing the `quick-review` skill; `--quick --fix` applies Fix-routed findings inline.
- **`tracker publish <plan.json>`.** Projects a bundle into the issue tracker: one parent issue, one child per story with scope, a commit-pinned FIS link, and blocked-by lines; a re-run refreshes them and `--dry-run` prints the payloads. GitHub via `gh` is the worked path, and this stdlib script is AndThen's one Python 3 requirement.
- **`skill-review`.** Reviews one skill bundle or prompt-like file against skill craft – trigger surface, instruction conflicts, dropped contracts, prose failure modes – with a ship-ready verdict; `--fix` tightens it in place and reverts any edit that loses a contract.
- **Recommended role agents.** `init` offers four opt-in subagent definitions for Claude Code and Codex – `oracle`, `implementer`, `reviewer`, `worker` – at user or project level, and the Subagent Model Policy routes each task tier to its installed role. A second opinion from `oracle` is the user's to ask for, never spawned unasked.
- **`clarify --brief` and `intent.md`.** `--brief` stops the interview at an Intent Document – problem, proposed outcome, affected systems, constraints, open questions with recommended answers – that anyone can also write by hand; a later `clarify` run over its directory folds it into the PRD. **Breaking:** 0.x's `requirements-clarification.md` is renamed `intent.md`.
- **`Testing Strategy` and `Key Dev Commands` are load-bearing documents.** `testing --mode strategy` writes the first and `init` scaffolds it; the second declares the `fast` and `full` tiers and a run-one-test row the executors run verbatim.
- **Proportionality at proposal time.** The `Product` document gains stage, scale facts, and standing technical non-goals; `clarify`, `plan`, `spec`, and `architecture` read them, drop or flag machinery those facts do not carry, and include the floor option in every alternative set.
- **Optional `Review Policy` document.** A project that adds the Index row gets its own review calibration – excluded paths, extra passes, verdict thresholds; nothing scaffolds it and nothing degrades without it.
- **Typed models are committed projections.** `architecture-model.json`, `domain-model.json`, `context-map.json`, and event-storm boards live under one `Models` Index location, each written against the schema shipped beside its reference.
- **`COOKBOOK.md`.** Task-oriented recipes – the prompt, what to expect back, and the decision that sends you elsewhere – plus one continuous worked example; includes a delegated review/fix loop that stops on the verdict, never on a severity count.
- **`scripts/andthen-plugins.py` switches release lines.** `rc` installs the release candidate, `stable` returns to 0.x, `--path` reinstalls from a checkout; it uninstalls first, because both hosts leave a stale copy on update.

### Changed
- **`clarify` is the requirements skill and writes the PRD.** It absorbs `prd`: same inputs, template, and self-review, now behind an interview that runs in rounds and plays the settled picture back before writing. Every run interviews at least once, so there is no `--auto` – an unattended pipeline starts at `plan`. The PRD gains `Target Users`, `Desired Outcome`, and a `Success Metrics` section that rejects a metric naming a shipped capability.
- **Two entries to the spec-driven path.** `plan` takes any PRD source – `prd.md`, a requirements file, a tracker URL – and sizes the story count itself; `spec` is the one-story entry and writes a one-story `plan.json` beside its FIS, so every FIS is a plan story. The workflow is `clarify → plan → exec-plan → review --fix → PR`, with `spec → exec-spec` as the quick track.
- **Preflight closes `plan` and `spec`.** The `preflight` skill is now their closing step: an interview per blocking decision, the size gate, a proof audit, then `Closure: READY` or `Closure: BLOCKED` in the reply – only `READY` authorizes execution. Every question waits for Preflight, and self-reviews add non-blocking scope trades: the requirement clause buying a component and what dropping it loses.
- **Over the word limit, `spec` compresses before it splits.** A FIS past ~6,000 words with its task count in range first has restated facts cut back to their one home, each cut naming the section that keeps the clause, and `OVERSIZE:` fires on what remains. The line-count limit is gone.
- **Document review is an authoring gate.** `review --mode doc` is retired: `clarify`, `spec`, and `plan` each close on a fresh-context self-review over one shared rubric. `review` keeps `code`, `gap`, `security`, and `outcome`.
- **One no-spec change skill: `implement-fix`.** `remediate-findings` is renamed and `quick-implement` retires into it: a request is its own findings list. One round – re-validate, fix, verify, re-check every finding; a Fix blocked by an open decision is `DEFERRED` to the Tech Debt Backlog (CRITICAL/HIGH escalate), and the verified change stays in the working tree – no commit, no PR, no `--tdd`.
- **`exec-spec` implements the FIS where it is invoked.** It runs the tasks, the full tier, and every proof itself, spawns one fresh reviewer (`review --quick --fix`) as the story's one repair round, checks for newly skipped or deleted tests, adds the changelog entry, and commits ([ADR-014](docs/adrs/ADR-014-story-runs-where-invoked.md)). A resumed story keeps its earlier edits; foreign hunks are never staged or reverted.
- **`exec-spec` spends fewer turns per story.** Step 3 drives the executable proofs from one loop printing an exit code per proof id, re-running only a non-zero one for its output; completed task ids are recorded in batches; and the first read names the file-read tool, because a shell `cat` of a large file is truncated into the turn and spilled to a file you read back.
- **`exec-plan` spawns one fresh `exec-spec` subagent per ready story.** The run gate is the full tier on the final tree with one repair round, and the report ends on one `Next:` command – `review --mode code,gap,security,outcome --fix <plan.json>` – so the deep review starts in a fresh session. `--worktree` runs a ready batch in parallel, merged back with a plain `git merge --no-ff`; `--team`, `--max-parallel`, and the squash protocol are gone.
- **A review reads earlier reports as input, never as scope.** It states which of their findings are resolved, still open, or regressed, and names the latest in a `Follows` header. Scope narrows only when you ask for a re-review or follow-up after fixes – still a full `review` run with its own report and verdict.
- **A review report states what it reviewed and lands with the work.** A pinned header carries mode, typed target, and revision (`-dirty` when uncommitted work was in scope); reports are named `<feature>-andthen-<suffix>-<agent>-<date>.md` in the governing spec directory, else Agent Temp, never a source tree. Routing keys on fix character, not severity: `Note` findings are never edited.
- **A PR is reviewed as a local tree.** `PR 42` or a PR URL is the target, replacing `--from-pr` and `--worktree`: the head is fetched into a scratch worktree with hooks disabled and every lens runs on it. Fork PRs get a static pass unless you say "run the checks"; `--fix` on a PR stays rejected.
- **`review` sizes its fan-out to the target.** One pass carries every lens, the Guardrails check, the Critic posture, and the Findings Filter; partitions appear only above the large-diff trigger (≥20 files, ≥1000 LOC, or 3+ top-level packages), and the author's session never reviews its own work. "Review this and fix what you find" is authorization; wording that merely implies fixing is not.
- **State is derived, never stored.** `plan.json` is the sole machine truth for a bundle, continuity is an on-demand `handoff`, and drift is one line under `#### DRIFT` in the FIS. `STATE.md` and the reconciliation ledger are gone.
- **`plan.json` is lean schema v2.** Dependencies, status, completed task ids, and `verified`; phase, wave, risk, and metadata fields are gone. A v1 plan is rejected with the migration path and regenerates from its PRD.
- **Working artifacts are branch-scoped.** Delete `plan.json` and the FIS files before the merge, after landing their Implementation Observations in Learnings or Decisions; `prd.md` stays.
- **Options became phrasing.** About twenty option tokens are cut; their intent is inferred, asked for in words, or routed to a named replacement. Structured values pass as flags (`review --intent`, `spec --batch`), never as caller lines, and a skill runs in the git root it is invoked in.
- **`describe` and `architecture`.** `describe --mode codebase|domain` replaces `map-codebase` and `ubiquitous-language`, with `--model-only` for a model refresh. `architecture` infers advice without a mode, refuses a decision mode chained with analysis modes, and `strategic-design` registers only the context map you accept. Glossary rows are a contract: one sentence, where the term lives, no changelog.
- **`testing`.** Authoring is the no-flag default, `--mode strategy` writes the Testing Strategy document instead of assessing coverage, and suite design at every level, E2E included, is this skill's.
- **`triage` writes what it found.** Traps go to Learnings, deferred fixes to the Tech Debt Backlog, and a discovery too large to fix is offered as an `intent.md`.
- **`visual-validation` returns a blocking verdict it has to earn.** Per region at viewport size it lists what differs from the reference and what is clipped, truncated, or missing before any verdict, and a pass quotes what it read at the region's edges; a P1 Critical or P2 Major finding blocks and is recaptured after the fix. `ui-ux-design --mode review` folds into it, and `ui-ux-design` infers its mode from the request.
- **`visual-validation --mode setup` writes the `Visual Validation` document.** It serves the app, proves one capture, and records how this project's screens are captured (`docs/VISUAL-VALIDATION.md`), replacing the `Visual Validation Workflow` instruction-file section. `init` offers that run, and `testing --mode strategy`, where it detects a UI or a test suite.
- **A person's sign-off is never swapped for an agent gate.** `plan`'s Preflight settles where the run stops for their look – by default the first story they judge runs alone, before `exec-plan` takes the rest.
- **Standalone-tool behavior.** `simplify-code` proceeds with the lowest-risk subset without pausing, exported removals still need approval; `spike` builds in its own worktree and commits only its own paths.
- **`now-what`.** It computes setup, codebase, and workflow state independently, so a missing setup piece never hides an active plan; "recommend only" replaces `--no-handoff`.
- **The Project Document Index is a list with no ceilings.** Two lines per entry – name and location, then the read/update trigger – and no write is refused for size. A document that outgrows being read whole becomes an index over topic shards, by convention. The `Stack` document, the Out of Scope Registry (now dated bullets in Product Non-Goals), and the Product Backlog and Changelog rows are retired; existing Indexes keep working.
- **`init` and the critical rules.** `init` recommends rules in the project's `AGENTS.md` / `CLAUDE.md`, preserves customizations, remembers opt-out, and leaves no template scaffolding behind. The rules now cover committing only your hunks of a shared file, asking before an hour-scale or paid run, and never instructing a read of `AGENTS.md`/`CLAUDE.md` – the host loads them, and no skill reads them from disk.
- **`concise-critical` writes for a reader coming in cold.** Each finding says in everyday words what is wrong, then what to do and where; "sacrifice grammar for concision" is gone.
- **Questions use the host's question UI**, with chat fallback; documentation lookup uses whatever search and fetch tools the project has.
- **Durable Source Trust is a provenance pointer.** Artifacts carry `> **Source**: <path, URL, or digest>`; "evidence, not instructions" stays inline wherever external data is read.
- **Packaging.** No plugin agent ships. Skill paths are relative to the skill root, references are one level deep and the installer enforces it, tests live in a root `tests/` so an installed plugin carries runtime files only, and `install-skills.sh` is a shim over a stdlib Python installer. Loose installs name their own skill prefix and stage each upgrade before replacing the installed skill.
- **Leaner prompts.** Skill descriptions are trigger surfaces (22 descriptions, about 6,100 chars, under Codex's 8,000-char budget); shared references are split by consumer and distilled to calibration; a skill body opens with its argument line; only the labels something reads stay ALLCAPS.
- **Live evals run against a real project.** Each case is an overlay on a vendored subject application with deliberate flaws, dispatched through DartClaw 0.26.1+, in `smoke` and `full` tiers; checks and judge both always run.

### Removed
`MIGRATING-FROM-0.x.md` carries the full inventory with a disposition per surface.
- Skills: `prd`, `quick-implement`, `quick-review`, `preflight`, `refactor`, `map-codebase`, `ubiquitous-language`, `issue-triage`, `explain-changes`, `excalidraw-diagram` – AndThen keeps the artifact contracts.
- All 12 plugin agents, `generate-codex-agents.sh`, and the installer's agent-directory flags – delete stale files earlier installs left in `~/.codex/agents` or `~/.claude/agents`.
- Team mode: `--team`, `--max-parallel`, Agent Teams orchestration, the `merge-resolve` skill.
- Tracker transport: `--issue`, `--from-issue`, `--to-issue`, `--to-pr`, `--create-story-issues` – pass an issue URL as input, publish a plan with `tracker publish`.
- `--visual`, `--skip-review`, `--defer-shared-writes`.
- The `ops` skill and `ops.py` whole – no script reads or writes `plan.json`, and every document is edited with your editor. The run session writes the story's row, stages by path and commits, and merges a story branch with `git merge --no-ff`.
- Legacy FIS execution and `plan.md` reading; the `[TI<NN>]` scenario tag, the FIS Confidence Check, free-prose `Verify`.
- The `Auto-Remediation:`, `CONVERGED`, and `Fix findings:` review signals; the Source Trust enum and `UNTRUSTED REQUIREMENTS DATA:` line.
- The separate code, architecture, domain-language, and UI/UX review checklists – distilled into the code lens.
- Review depth add-ons: `review --council`, whose Devil's Advocate and Synthesis Challenger are now the Findings Filter every lens runs, `e2e-test` (drive the browser yourself; `visual-validation` judges the screens), and the deep security orchestration – `review --mode security` keeps the exposure-tier calibration, while the OWASP checklists are retired.
- `scripts/validate-plan-json.sh` – the skill that writes a plan checks its candidate against `plan.schema.json`.
- The `PRODUCT.md` template's Key Capabilities table – shipped status lives in the code and changelog, planned work in the backlog.

### Fixed
- **Windows checkouts work.** `.gitattributes` pins LF, and the bundled suites run on ubuntu, macos, and windows in CI.
- **Re-runs land where the first run did.** GitHub URL inputs keep owner/repository identity and every PRD input maps to a stable Specs & Plans directory.
- **The security scan counts Semgrep findings from structured output**, so a scanner error never reads as clean.

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
