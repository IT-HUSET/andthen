# Decisions

<!-- One Current ADRs row per ADR, keyed on its ID; the `andthen:decide` skill writes them.
     Status: Proposed | Accepted | Deprecated. A superseded row moves to Superseded; a rejected
     ADR leaves the index, and its file keeps the record. -->

## Current ADRs

ADR-003 was written retrospectively for 1.0; its commit references are the evidence. On 2026-09-28, before 1.0 shipped, the ADRs a later record superseded or already carried were deleted once rather than kept as lineage; what survived of them lives in the ADRs below and the Still Current notes, and git keeps the rest. Numbers are never reused: the next is ADR-031.

| ID | Title | Status | Scope |
|----|-------|--------|-------|
| [ADR-003](adrs/ADR-003-runtime-state.md) | Separate runtime state from specification prose | Accepted | `plan.json` owns runtime state; one shape; the executing story writes its row, one writer per copy |
| [ADR-014](adrs/ADR-014-story-runs-where-invoked.md) | Run the story where the skill is invoked | Accepted | Execution ownership, proof-bound completion, and per-story review |
| [ADR-018](adrs/ADR-018-one-plugin.md) | Ship AndThen as one plugin | Accepted | The satellite merges into core; `council` and `e2e-test` retire, `security-review` folds into the `security` lens; one aggregate prompt-surface budget |
| [ADR-020](adrs/ADR-020-one-authoring-and-one-execution-skill.md) | One authoring skill and one execution skill | Accepted | `plan` merges into `spec`, `exec-plan` into `exec-spec`, in a router layout; ADR-024 renames them `plan` and `exec-plan` |
| [ADR-021](adrs/ADR-021-fold-backlog-triage-and-move-skill-review-out.md) | Fold `backlog-triage` into `tracker`, and move `skill-review` to project level | Accepted | `tracker triage`; `skill-review` leaves the shipped plugin |
| [ADR-022](adrs/ADR-022-init-asks-only-what-it-cannot-infer.md) | `init` asks only what it cannot infer | Accepted | Core documents on first write; Proportionality asked at first use |
| [ADR-024](adrs/ADR-024-plan-names-and-story-status-writers.md) | Name the skills `plan` and `exec-plan`, and give every story status a writer | Accepted | `spec` → `plan`, `exec-spec` → `exec-plan`; statuses `pending`/`in-progress`/`done`/`skipped`; `skipped` blocks dependents |
| [ADR-025](adrs/ADR-025-decide-skill.md) | Make and record technical decisions in a `decide` skill | Accepted | `decide` interviews over technical decisions and writes ADRs; `architecture` loses `trade-off` and `advise`'s Design sub-mode |
| [ADR-026](adrs/ADR-026-ship-skill.md) | Ship the branch with a `ship` skill | Accepted | `ship` owns the close-out on any branch: lands FIS observations, deletes or keeps the bundle on one ask, commits, one ask before push and PR; the printers hand off to it |
| [ADR-027](adrs/ADR-027-visualize-skill.md) | Draw AndThen artifacts as checked pages with a small `visualize` skill | Accepted | Model-written self-contained HTML with inline SVG, gated by a render-and-look loop; any artifact; `now-what` drops its notes route |
| [ADR-028](adrs/ADR-028-tracker-record.md) | Keep a feature's record in the issue tracker, opt-in per project | Accepted | `Record: repo \| tracker`; the PRD lives in the source issue, story issues carry intent and acceptance, `ship` writes the final record and the merge closes it; prose, no script |
| [ADR-029](adrs/ADR-029-domain-skill-and-domain-map.md) | Model the domain in a `domain` skill, recorded in one Domain Map | Accepted | `domain` modes `subdomains`, `contexts`, `glossary`, `event-storming`; `DOMAIN-MAP.md` replaces `CONTEXT-MAP.md`; `context-map.json` retires; one Markdown-or-JSON rule |
| [ADR-030](adrs/ADR-030-one-setup-script.md) | One setup script installs AndThen and places its role agents and rules | Accepted | `scripts/andthen.py` replaces both install scripts; opt-in user-level roles and rules, written only where no merge is needed; `validate-plugin.py`; white-label and `--claude-user` go |

## Superseded

<!-- Never delete a superseded row: its lineage tells agents why the code is shaped as it is. -->

| Prior Decision | Superseded By | Notes |
|----------------|---------------|-------|

## Still Current

<!-- Load-bearing choices that don't warrant an ADR, one bullet each:
     `- **<Topic>**: <decision + brief rationale>`. State each as it holds now, rewriting or
     deleting it, and its shard section, when a later choice changes it; promote a contested
     one to an ADR. Longer rationale, evidence, dated amendments, and reopen conditions go in
     `decisions/<heading-slug>.md` under the bullet's topic, or stay in the ADR that carries them. -->

### Workflow and skills

Rationale and reopen conditions: [decisions/workflow-and-skills.md](decisions/workflow-and-skills.md).

- **Where work starts: two questions, and `plan` answers one**: the user answers "do I know what to build?", `plan` answers "one story or several?" (ADR-020). `clarify` writes the PRD at any size; the plan's `prd` stays a nullable path with no URL form, since a PRD is never mandatory. An open design choice that binds beyond the work or is costly to reverse goes to `decide` first (ADR-025).
- **`clarify` writes the brief too, and has no unattended form**: `--brief` stops at `intent.md`, the intake the next run folds into the PRD. No unattended form: the interview is the skill's value, and a pipeline with requirements starts at `plan`.
- **Specs are co-produced with the story breakdown**: `plan` cuts the stories and authors their FIS in one run, because specs decay when divorced from the story context that motivated them, and one cross-cutting review catches inter-story inconsistencies before execution.
- **One authoring subagent per story**: `plan` on several stories spawns one fresh authoring subagent per story, never one for several siblings, and a re-author stays scoped to its story, so an `OVERSIZE:` or `PHANTOM_SCOPE` finding stays attributable and each retry separate.
- **One no-spec change skill**: `implement-fix` takes a review report or a request, and a request is its own findings list routed `Fix` by the user, so the agent never invents scope; what it leaves unstated is reported, not edited, unless a Boy Scout tidy. Accepted: a one-line fix runs the full phases.
- **No model-only or user-only skills**: a capability is a skill a user invokes by name and a subagent invokes with arguments, never a `user-invocable: false` or `disable-model-invocation` skill or a "read X and perform it" reference. References are rubrics, few and one level deep, except a skill's own load-site branch (ADR-020).
- **Positioning terms**: AndThen is "lightweight agentic software engineering for AI coding agents": the whole engineering job, requirements to debugging, done through AI coding agents, with spec-driven development as its main workflow, never the whole product (`8a5dd64`). "AI coding agents" names the tools, never the product.

### Authoring

Rationale and reopen conditions: [decisions/authoring.md](decisions/authoring.md).

- **The PRD carries its outcomes as body sections**: `Problem Definition > Target Users`, `Desired Outcome`, and `## Success Metrics` (baseline, target, how observed). The Executive Summary derives from them, never the reverse; a FIS's Intent and Expected Outcomes cite them; validation rejects a metric naming a shipped capability.
- **PRD acceptance criteria are EARS rules, FIS scenarios their examples**: each FR states its criteria as `While <precondition>, when <trigger>, the <system name> shall <response>` and unwanted conditions as `If <condition>, then the <system name> shall <response>`, replacing the Validation and Error Handling lists so error cases reach a scenario. User-story criteria stay prose for the outcome lens.
- **Preflight closes, never holds**: `plan`'s closing step asks each open item once per bundle, recommendation first and preselected, no defer option; unattended, or stopped on and unanswered, the recommendation becomes an `ASSUMPTION:` where it bites. No status, hold, or `Closure:` verdict of its own.
- **The model judges which forks need the user**: skills say where asking happens and how a question is shaped, never which discretionary forks to ask, because per-case asking rules degraded the `plan` eval. Only a fork a skill's own contract owns is asked by rule. An eval that tests asking needs a fork with no defensible default, and its rubric requires that fork, never a question a capable model can default.
- **Scope trades are a self-review Note and a preflight question, not a skill**: the FIS self-review names each component the floor option would not carry, the requirement clause buying it, the narrower reading that drops it, and what the Target User loses. Preflight asks them once per bundle, never blocking; an accepted trade amends the PRD through `clarify`.
- **Document review is an authoring gate, not a `review` lens**: `clarify` and `plan` each run a fresh reviewer subagent on `self-review.md`, a rubric the author never loads. `review` has no `--mode doc` and keeps only lenses with an implementation target.
- **`plan` has no re-entry handling**: it authors from a source, never reading an existing FIS or `plan.json` as state. Revising or re-planning is a prompt the user writes, because edge-case handling a user can prompt around costs every run focus.
- **A FIS carries only what the executor would miss**: a fact restated from a cited source, a project document, or a scenario is a second copy that drifts. Past ~6,000 words with the task count in range, `plan` compresses under **Single source of truth** before `OVERSIZE:` fires; trimming is an authoring rule, not a reviewer cut duty. Technical Overview is the Architecture Decision's `Flow`, capped at ~10 lines.
- **Over-engineered work is discarded, and the PRD is cut first**: before executing a PRD or plan, weigh its FR count and acceptance volume against the problem, and redo bloat small rather than prune it. Prefer data-only extension points, one generic code path, and "running it is the test" over meta-tests.
- **Rejected concepts are Product non-goals, not a registry**: `clarify` and `tracker triage` append a firmly rejected concept to the `Product` document's Non-Goals as one dated bullet and check that section before re-proposing one. `clarify` curates in both directions, narrowing or removing a bullet its PRD overturns on the same user-traceable bar, because a standing bullet makes the `review` outcome lens grade the commissioned feature a HIGH no fix round can clear.

### Execution

Rationale and reopen conditions: [decisions/execution.md](decisions/execution.md).

- **`--auto` is the only unattended trigger**: the flag alone turns the mode on, never a task header, a workflow step, a host with approvals off, or a project rule. An unattended run passes `--auto` to every nested skill invocation that accepts it.
- **No skill settles questions its own text asks**: only `--auto` reduces a run's asks, never a skill's kind. `tests/test_unattended_runs_load.py` keeps out the retired "Headless-First" shape, a shared reference that reads on a skill's class instead of its arguments.
- **A question goes where the run stops for it**: a skill prefers the host's structured question tool wherever it holds the turn for the answer, splitting a round over consecutive calls, else asks in the reply; the asking turn ends on the question, never on a report. A Codex `plan-asks` failure is a host limitation, not a wording defect.
- **An assumption is reachable only from a question**: an `ASSUMPTION:` records a choice made because no answer was coming (an unattended run, no user, a question stopped on and unanswered, a reading the brief leaves open), never an answer to a question its text says to ask and the run did not stop on. A question the run continued past was not asked, and the asking reply lists no default and writes no assumption.
- **A decision never stops a run**: it is asked once, recommendation first, or under `--auto` taken as an `ASSUMPTION:`. Only an unusable call stops (input absent or invalid, missing credentials or tooling, a foreign dirty tree its skill has no rule for, an action without consent), unattended as `BLOCKED: <what is needed>`; a failed run ends on its failure evidence. No `CONFUSION:`, `MISSING REQUIREMENT:`, or `NO-OP:` markers or per-skill trigger lists, and no `blocked` story status; an older plan's `blocked` row reads as `pending`.
- **`exec-plan` never stops on FIS detail**: a broken anchor, a missing or form-less proof, an unbound scenario, or text a `sharedDecision` contradicts gets the best reading, recorded under Implementation Observations. Only a contradiction with no defensible implementation, or an orchestration stop, halts the run; a foreign change overlapping the story's hunks is left uncommitted and reported.
- **No edge-case knobs, no strictness blocks, one verification run**: the code root is the git root, a missing reviewer subagent falls back and says so in `Reviewed:`, and a story runs one tier, because each knob costs a flag, a validity rule, a trigger, docs, and tests.
- **A plan run hands off the plan-level review**: `exec-plan` on a plan directory gates on the full tier, iterated to green, then prints `Next (fresh session):` (`review --fix <plan.json>`) instead of reviewing in the run session, the workflow's most loaded context.
- **A plan runs story by story by default**: each `Next (fresh session):` line names the next dependency-ready story's FIS, so a person reads every result before the next runs. A story run commits discoveries into the unstarted FIS they affect, asking first when one contradicts it or changes scope. The next story attests each inherited Discovered Requirement over its proof, and `plan --auto` still prints the first story. The plan directory stays the unattended and parallel route.
- **Each story is simplified before the next builds on it**: `exec-plan` runs `simplify-code` over each `done` story as its own `refactor` commit (once per batch under `--worktree`), so later stories and the reader between them meet tidied code. Not in `implement-fix`, whose patch stays the smallest a finding needs.
- **The `Product` document is read where scope is chosen or the result validated, never where code is transformed**: `simplify-code` and `implement-fix` on a report anchor on the governing FIS or PRD, which already distilled what binds. `implement-fix` on an inline request adds the Non-Goals.
- **A fresh-session hand-off says so in the line it prints**: every pipeline skill closes on one `Next (fresh session): <command>` line in the host's invocation syntax, because the user sees only that line and a bare command reads as "continue here". The two words are the contract, not trimmable prose.
- **Per-story parallelism is plain git in the run session, not AndThen scripts**: `exec-plan --worktree` gives each story of a batch its own worktree and a `--no-ff` merge, as prose the run session executes. Lines both sides appended to the changelog or `Learnings` keep both; any other conflict fails that story, its worktree and branch kept. No `--team`, `--max-parallel`, or squash-merge protocol.
- **The `ops` skill and its script are retired**: each story run writes its own `plan.json` row with file tools from `story.md` alone, loading neither plan schema file, and `plan`'s story subagents never write it, so no copy has two writers (ADR-003). No script parses an agent-read document for meaning, and nothing validates plans or models. Accepted: a malformed plan or model can be written.
- **`exec-plan` carries minimal resume text**: a re-run relies on the plan fields and the standard workflow; only lines whose absence is destructive or silent stay.
- **Unattended remediation dispositions Notes on its own recommendation; attended remediation asks before any Tech Debt write**: unattended, `implement-fix` applies a Note it would change unasked (inside the reviewed surface, within Intent, one provable remedy, no open decision settled), defers the rest to the Tech Debt Backlog with its remedy, or closes it with a reason; `--auto` approves those backlog writes. Attended, it writes only the backlog entries the user approves. `review` reads a story's recorded open items as it reads earlier reports.
- **A change tidies what it finds**: a story, an `implement-fix` round, a triage fix, and a prove-it refactor step make and name every Boy Scout tidy they find, a parallel story only in its own files, so a one-edit smell takes one pass. `NOTICED BUT NOT TOUCHING` is for what no tidy can fix and someone should act on. A redesign, a public API change, or settling or reversing a recorded decision is never a tidy.
- **Test-first is a project convention, not a flag; Prove-It is mandatory**: the `Testing Strategy` document's test-first answer, or a request, turns it on, since a document survives a fresh story session and a flag does not; each red failure is quoted. No TDD mode or flag: measured cost, no measured gain. `implement-fix` keeps test-first as its only independence check.

### Review

Rationale and reopen conditions: [decisions/review.md](decisions/review.md).

- **Outcome validation is a `review` lens, not a skill**: `outcome` validates the finished feature against its PRD's Problem, Target Users, User Stories, and Success Metrics, walked as those users. A PRD-side finding counts toward readiness only at CRITICAL or HIGH, since a lesser one is a PRD decision no fix round makes.
- **A PR is reviewed as a local tree, not through the API**: `review` fetches `PR <n>` into a detached worktree with hooks and LFS smudge disabled, so every lens and tool reads a path and nothing executes. The project's checks run only for a head branch in the repository; a fork PR gets a static pass unless the user says otherwise.
- **A review reads earlier reports as input, and a remediated one narrows scope**: it marks each earlier finding resolved, still open, or regressed and names the latest in `**Follows**:`. After a `**Remediated**:` report it reviews the work since that report's Revision, the changed code's callers, and its open findings, and the fan-out and `security` triggers read that delta; no reviewer count decides when to widen, and only a lens the report did not run or a Revision outside HEAD's history returns it to the whole target. A `plan.json` remedy routes `Note`, a surfaced or deferred MEDIUM or LOW finding stays in the summary's list, and only fixes ask for another round.

### Project documents

Rationale and reopen conditions: [decisions/project-documents.md](decisions/project-documents.md).

- **Durable documents carry no size ceilings**: an Index entry holds name, location, and read/update trigger, no size number, since a count cannot tell needed explanation from dispensable text. Documents are read whole and stay short; a trigger names a part only for history or reference no task is checked against, and an outgrown document becomes an index over topic shards.
- **The Index entry catalog carries no Product Backlog or Changelog entry**: each entry is where its first writer creates the document (ADR-022), and no skill writes or reads a backlog or changelog. A project that keeps either adds its own entry.
- **No `Stack` document**: its template's rows projected the manifest, the lockfile, an ADR, or the Architecture document's Integration Points, and drifted. The baseline (language, runtime, main framework) is one sentence in the Architecture document's System Overview; versions stay in the manifest.
- **Tracker setup is first-use, not an `init` gate**: `init` writes neither the file nor its Index entry; the first skill that needs the backend offers `tracker setup`; `tracker publish` and `tracker triage` do so where the repository has no GitHub remote, since GitHub takes the built-in `gh` default, and an unattended run blocks naming the `Backend:` line. `Backend: none` declares no tracker, and `tracker publish` and `tracker triage` end on one line saying so. Accepted: a non-GitHub project's first unattended run blocks until the document exists.
- **The critical-rules starter's ownership lead is adapted, not quoted**: its codebase-care rule keeps the Fable 5.2 prompting guide's "This codebase is yours, and you keep building on it", because that framing, not an instruction to tidy, is what makes a model merge duplication rather than add another copy, and drops the guide's "what it's for and how it's built are your call", since `clarify` owns what the code is for and `decide` owns how it is built. Its bound sits in the same sentence ("and nothing beyond them"), because a scope rule elsewhere in the file does not cancel an ownership statement.
- **`init` wires the rules and role agents in prose; unattended setup places them by script**: attended, both are one-line offers in `init`'s closing summary (ADR-022), run as the prose in `init/references/offers.md`, which owns project-level placement and every merge into a file that differs. Unattended, `scripts/andthen.py` places user-level copies only where no merge is needed and refuses the rest, pointing at `init` (ADR-030).
- **The architecture-model schema is for code-structure graphs only**: `ref` anchors to repo-relative paths and `evidence` makes every edge refutable against code, so it never adds another `kind`. Any other JSON record follows ADR-029: generated facts nobody hand-edits and no document holds, never a mirror of a document.

### Packaging and measurement

Rationale and reopen conditions: [decisions/packaging-and-measurement.md](decisions/packaging-and-measurement.md).

- **AndThen owns the artifact contracts; downstream tooling owns its views**: the artifact schemas, the `scripts/fixtures/renders/` corpus, and the visual-review-notes payload are AndThen's; a downstream viewer owns its views and closes its notes loop by invoking the owning skill; no shipped skill reads the payload. AndThen's one view is `visualize` (ADR-027). Shipped skills never name a downstream app, since that prompt breaks for everyone without it.
- **No tests inside the plugin directory**: every suite lives in `tests/`, because both hosts install `plugin/` wholesale with no exclude list, so a test beside a shipped script ships to every user.
- **Codex does not substitute `${CLAUDE_PLUGIN_ROOT}` or `${CLAUDE_SKILL_DIR}` in skill text**: its shim is a hook environment variable only, so references are skill-root-relative (`../../references/<name>.md`, `<skill-dir>/scripts/<name>`), with no tokens anywhere (`scripts/validate-plugin.py` rejects them).
- **Leanness is measured per consuming path, and dedup never creates a reference file**: the number is the active lines a use case loads (body plus every reference it names), reported per path before and after, not SKILL.md size. A pointer pulls a whole file into every consuming bundle, so minor duplication in canonical wording is accepted.
- **No context-budget gate**: shipped-prompt size is bounded by `scripts/validate-plugin.py` and the shipped-surface word budget; the ratchet cost a fixtures directory, a ceilings file, and wording gotchas without producing a finding after its baseline.

### Evals

Rationale and reopen conditions: [decisions/evals.md](decisions/evals.md).

- **Eval cells run the plugin, not the operator**: a cell gets a snapshot of the working tree's `plugin/` plus the role agents `init` bundles, nothing else of `~/.claude`, so it measures the plugin, not the operator's rules. A case with a fuzzy criterion is fixed or cut, never kept.
- **`claude plugin eval` is not the eval harness**: it is Claude-only with no code graders, and a skill-trigger suite is rejected outright.

## Pending

<!-- Decisions under discussion, not yet accepted. -->
