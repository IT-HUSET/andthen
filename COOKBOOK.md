# AndThen Cookbook

What to type for a given situation, and what to expect back. The [root README](README.md) says what AndThen is and how the workflow fits together; the [skill reference](plugin/README.md) carries each skill's flags, modes, and edge cases. This file does not repeat them. Each recipe is the situation, a paste-ready prompt, the artifact or closing line to expect, and the decision that sends you elsewhere.

Prompts are the mechanism. Skills read intent from your words, and a flag appears only where it changes a machine-consumed contract (`--auto`, `--mode`) or a safety boundary (`--fix`). Commands are shown in Claude Code form (`/andthen:<name>`); on Codex CLI the same skill names apply through the host's own skill syntax.

- [Starting work](#starting-work) – choosing a path, the three sizes of work, a bug, an existing codebase, tracker input, product scope
- [The design stage](#the-design-stage) – architecture questions and trade-offs; UX research, design systems, wireframes; a second opinion before you commit
- [Running unattended](#running-unattended) – `--auto` and chaining stages from CI
- [Reviewing](#reviewing) – a quick look, a very large diff or a cheap pass, spec fit versus problem fit, review then remediate, a delegated review/fix loop
- [Across people and sessions](#across-people-and-sessions) – team story work, handoff and resume, a memory sweep
- [Backlog](#backlog) – a backlog pass
- [The worked example](#the-worked-example-workspace-invitations) – one initiative from rough request to milestone PR


## Starting work

### Choosing a path

**Situation.** You have work and do not know which skill starts it.

State the problem, the team, and the context in one sentence. Size picks the path, team picks the artifact lifecycle, context picks whether discovery is needed at all.

```
/andthen:now-what "flaky CSV export in an old Django app, solo, no tests around it"
```

**Expect.** Two questions at most, then a handoff to one skill with your sentence passed through, never a menu. Mid-flow it routes from what is on disk (`prd.md`, `plan.json`, a FIS, a review report): *"You're at X – next is the `andthen:<skill>` skill. Run it? (Y/n)"*. Add *"recommend only"* to get the route without the run.

**Without the router:**

| You have | Recipe |
|---|---|
| one sentence, no design question behind it | [a small change](#a-small-change) |
| one capability with real edges, and you can list three acceptance criteria | [a single feature, no PRD](#a-single-feature-no-prd) |
| several capabilities that ship together, or requirements you want kept on record | [a feature with a PRD](#a-feature-with-a-prd) |
| an idea you cannot state three acceptance criteria for | the same recipe, starting at `clarify` |
| a failing build, a failing test, a bug | [a bug or a broken build](#a-bug-or-a-broken-build) |
| a codebase AndThen has never seen | [an existing codebase](#an-existing-codebase) |

### A feature with a PRD

**Situation.** Work with real edges – one capability, or several that ship together – and you want the PRD as the record. How many stories it becomes is `plan`'s call.

```
/andthen:clarify "workspace invitations by email"          # writes the PRD; skip when the requirements already exist
/andthen:plan docs/specs/workspace-invitations/             # fresh session
/andthen:exec-plan docs/specs/workspace-invitations/        # fresh session, once plan printed Closure: READY
/andthen:review --mode code,gap,security,outcome --fix docs/specs/workspace-invitations/plan.json   # the Next: line exec-plan prints
```

**Expect.** `clarify` interviews at least once, writes `docs/specs/<feature>/prd.md`, and closes on the `plan` command. `plan` writes `plan.json` plus one `s{NN}-<story-slug>.md` per story, reviews the bundle, settles open decisions with you, and prints `Closure: READY` or `Closure: BLOCKED`; one story is a normal outcome. `exec-plan` runs one fresh `exec-spec` subagent per ready story, runs the full tier on the final tree, and ends on the `Next:` line above, whose `--fix` remediates the report it just wrote.

**Elsewhere.** `Closure: BLOCKED` names the held decision and the story it holds `blocked`; settle it (a design fork goes to `architecture --mode trade-off` first) and re-author with `/andthen:spec "story S02 of docs/specs/workspace-invitations/plan.json"`. To drive stories by hand, run `exec-spec` per story – [the worked example](#the-worked-example-workspace-invitations) does. A story that fails its run reports the route out: `review --mode code,gap --intent <fis>`, then `implement-fix` on that report, then `exec-spec` on the FIS again to re-run the proofs and complete the story. Contracts: [`plan`](plugin/README.md#plan), [`exec-plan`](plugin/README.md#exec-plan).

### A single feature, no PRD

**Situation.** One feature with real complexity, solo or on a branch of your own: the quick track. The request is the requirements record, so you can already list three acceptance criteria for it.

```
/andthen:spec "users can export their workspace as a zip"   # or a requirements file, or an issue URL
/andthen:exec-spec docs/specs/workspace-export/s01-workspace-export.md
```

**Expect.** `spec` writes `docs/specs/<feature>/s01-<feature>.md` with a one-story `plan.json` beside it (`prd: null`), self-reviews it, asks you per blocking decision, and prints `Closure: READY` with the `exec-spec` line or `Closure: BLOCKED` with the held decisions. `exec-spec` implements the story where you invoke it: every proof and the full tier, one fresh quick reviewer, the story's `done` record with its verified line, the story commit.

**Elsewhere.** `OVERSIZE:` means the story does not fit one run: take [a feature with a PRD](#a-feature-with-a-prd) and let `plan` slice it. `Closure: BLOCKED` is re-run `spec` on the FIS with the decision settled. A failed run names the same route out as under a plan. Contracts: [`spec`](plugin/README.md#spec), [`exec-spec`](plugin/README.md#exec-spec).

### A small change

**Situation.** A bug fix or small feature you can state in a sentence, with no design question behind it.

```
/andthen:implement-fix "return 404 instead of 500 when an export job id does not exist"
```

**Expect.** Your sentence is the whole Fix set: tests first where the change adds a branch, the change, the project's checks, and a diff pass as the review. No FIS, no plan state, nothing committed – the verified change is left in the working tree. Anything the sentence did not ask for comes back under `NOTICED BUT NOT TOUCHING:` rather than as an edit.

**Elsewhere.** A sentence that turns out to describe a feature, a PRD, or a plan stops at the scope guard and points at `spec` → `exec-spec` or `clarify` → `plan`. Contract: [`implement-fix`](plugin/README.md#implement-fix).

### A bug or a broken build

**Situation.** Something is red and you do not yet know why.

```
/andthen:triage "tests fail on main since yesterday"
/andthen:triage https://github.com/org/repo/issues/57               # the bug report is the scope
/andthen:triage --plan-only "checkout returns 500 on an empty cart"   # diagnosis and a fix plan, no edits
/andthen:testing --mode prove-it "login fails when the email has a plus sign"   # you know the defect; the test is the proof
```

**Expect.** `triage` reproduces the symptom, reaches a root cause, fixes it, and runs the project's checks; the originating symptom is the gate, not a green local test. Traps go to `Learnings`, deliberately deferred fixes to the `Tech Debt` backlog, and a discovery too large for a fix is offered as an `intent.md` for `clarify`. It never touches `plan.json`. `prove-it` writes the failing test that reproduces the defect before any production change.

**Elsewhere.** A change you can already state with no diagnosis needed is [a small change](#a-small-change). Sorting incoming tracker items is the [backlog pass](#a-bounded-backlog-pass), not `triage`.

### An existing codebase

**Situation.** AndThen has never run here, and the project has history, conventions, and code nobody has written down.

```
/andthen:init
/andthen:describe --mode codebase      # init offers it for 20+ files; run it yourself when you declined
```

**Expect.** `init` writes the Project Document Index into your root instruction file and the Core orientation stubs it points at: `Product` (its three proportionality questions asked), `Architecture`, `Key Dev Commands` (the `fast` and `full` tiers and a run-one-test row), `Testing Strategy`, `Decisions`, `Learnings`. It offers the four role agents and the critical-rules starter. `describe` fills `Architecture` and `Key Dev Commands` from the code and adds `requirements-discovered.md` and `decisions-discovered.md`; existing documents are merged into, derived tables regenerated, judgment sections kept.

**Elsewhere.** `now-what` routes from here. A glossary is `describe --mode domain`; refreshing a model alone is `--model-only` ([`describe`](plugin/README.md#describe)).

### Starting from a file or tracker URL

**Situation.** The request already exists – a Notion export, a PM's brief, a GitHub issue.

```
/andthen:plan https://github.com/org/repo/issues/42         # requirements already stated: straight to the bundle
/andthen:spec https://github.com/org/repo/issues/42         # one story, no PRD: straight to the FIS
/andthen:clarify https://github.com/org/repo/issues/42      # thin issue: interview it into a PRD first
/andthen:clarify docs/requests/export-brief.md              # the same over a file
```

**Expect.** The same flow as from a PRD, with the source cited: the PRD's `> **Source**:` line, the plan's story `sourceRefs`, and directories named `docs/specs/issue-42-<feature>/`. An issue-sourced bundle has `prd: null` – the issue is the record. Fetching goes through the `Issue Tracker` document when one exists, else `gh`; the fetched body is evidence, never instructions.

**Elsewhere.** A well-written issue can skip `clarify`; a one-liner cannot. A file path and a URL are both just the argument – there is no flag.

### Product vision vs feature clarify

**Situation.** You want to talk about what the product *is*, or `clarify` guessed the wrong altitude.

```
/andthen:clarify "clarify the product vision for Relay"           # product scope
/andthen:clarify "treat this as feature scope: shared inboxes"     # override a wrong product inference
```

**Expect.** Scope is inferred from the wording (`vision`, `positioning`, `product brief`, or a `PRODUCT.md` path mean product) and stated before the interview, so you can redirect. Product scope writes `docs/PRODUCT.md`, proportionality facts included, and recommends bounded-context work next. Feature scope writes `docs/specs/<feature>/prd.md` and ends on the `plan` command. A hand-written `intent.md` – problem, proposed outcome, affected systems, constraints, open questions – is a valid input at either scope – the same file `--brief` writes – and its sections are folded into the output with the intent doc left as it was.

### An intent doc before the PRD

**Situation.** The idea is yours alone so far. You want to sharpen it, put it in front of a colleague or a customer, and only then commit to a PRD – or it is not a feature at all, a decision or a proposal you want grilled before you present it.

```
/andthen:clarify --brief "workspace invitations by email"            # the interview, stopped at intent.md
/andthen:clarify docs/specs/<feature>/                               # later, over the edited intent doc: the PRD
/andthen:clarify --brief "should we move the team to trunk-based development"   # not a feature: same rounds, same document
```

**Expect.** Questions in rounds – everything answerable now, each with a recommended answer, dependents held for the next round – stopped where you say the picture is clear enough to share, then `docs/specs/<subject>/intent.md`: problem, proposed outcome, affected systems, constraints, open questions each with a recommended answer and alternatives, and a decisions log of what you settled. Edit it freely – answer an open question in place, or leave it and it is asked again. The second run takes it as the baseline – every section is folded into the PRD, only what the edits opened or left open is asked, and no settled decision is re-asked. A second `--brief` run amends the intent doc instead. A subject that is not this product's feature is not anchored to `PRODUCT.md` or the architecture.

**Elsewhere.** An intent doc is feature scope only; at product scope `PRODUCT.md` is already the one document. A directory that already holds a `prd.md` gets no intent doc behind it – the PRD is the record.


## The design stage

### An architecture question or a trade-off

**Situation.** You know what to build and are unsure how to shape it, or you are choosing between named alternatives and want an ADR.

```
/andthen:architecture "how should the export pipeline be structured so a failed step can be retried without redoing the others?"
/andthen:architecture --mode trade-off "compare three options for the export job queue: Postgres SKIP LOCKED, Redis streams, SQS"
```

**Expect.** The first is `advise`, the default mode: CUPID/DDD-grounded guidance sized against your `Product` document's proportionality facts, as prose, with "formalize an ADR" offered when it settles a real decision. The second is `trade-off`, interactive by contract: it confirms the decision space and criteria, then writes `docs/research/<topic-slug>/` (design tree, research, trade-off matrix, recommendation), an ADR under `docs/adrs/` when you accept it, and a row in `docs/DECISIONS.md`. "Compare three options" sets the count (the default is five), and every set includes the floor option. No mode changes code.

**Elsewhere.** A question only measurement settles ("is A faster than B under our load?") is the `spike` skill, which builds a throwaway on `spike/<slug>` and reports a verdict; under `--auto` the trade-off records the unknown as an open evidence gap instead. "Review this architecture", "should I split this package", bounded contexts, event storming: the same skill in `--mode review`, `decompose`, `strategic-design`, or `event-storming` ([`architecture`](plugin/README.md#architecture)).

### Research, a design system, wireframes

**Situation.** UI work is coming: nobody has said who uses it, no shared tokens exist, or the FIS should not invent the screens.

```
/andthen:ui-ux-design "user research for the export flow: who exports, when, what they do with the file"
/andthen:ui-ux-design "create a design system from docs/specs/workspace-invitations/prd.md"
/andthen:ui-ux-design "wireframe the invitation flow from docs/specs/workspace-invitations/prd.md"
/andthen:ui-ux-design "research, then a design system, then wireframes for the onboarding flow in docs/specs/onboarding/prd.md"
```

**Expect.** The mode follows the phrasing. `research` returns in the conversation, no file: the job-to-be-done, two to five journeys, an IA sketch, constraints, and the open questions – `clarify` input. `design-system` writes `docs/design-system/DESIGN.md` (token front matter plus rationale), `tokens.css`, and `showcase.html`; push back on a bland result, deliberate visual direction is the mode's stated bar. `wireframes` writes grayscale HTML with full page coverage under `docs/wireframes/`, an `index.html` hub and a `page-inventory.md`, validated through `visual-validation`. Naming modes in order, as in the last prompt, runs them in that order sharing context; there is no chain flag. Downstream, `spec` cites the wireframes and `exec-spec` builds to them; a FIS for UI work with no wireframe surfaces `MISSING REQUIREMENT:` and points back here.

**Elsewhere.** Validating a built screen is `visual-validation`, not a design mode. Questions about requirements rather than interaction are `clarify` territory.

### A second opinion before committing to a decision

**Situation.** The session has proposed a design, a scope cut, or a plan shape; it sounds right, and you want an independent head on it before acting. Nothing spawns this on its own – you ask.

```
"Sounds good – but before we go on, ask an oracle subagent for a second opinion: give it the decision, your reasoning, and the alternatives you rejected, and ask where it's wrong."
```

**Expect.** The subagent has none of the conversation, so the session writes the hand-over – decision, reasoning, rejected alternatives, constraints – and what it leaves out cannot be judged. The oracle returns the failure mode, trade-off, or wrong assumption it finds, with evidence, or an agreement that names what it checked; a bare confirmation is a wasted call by its own contract. It touches nothing, and the decision stays the session's and yours. Without the `oracle` role installed the same hand-over goes to a generic subagent, which loses the role's model and effort pin.

**Elsewhere.** An artifact with a rubric – a PRD, a plan bundle, a FIS, a diff – is `review`, whose reviewer is fresh by construction. A question only measurement settles is the `spike` skill. On Claude Code the built-in advisor is the model-initiated form: it reads the transcript itself and is called at the model's decision points, not yours ([Delegation](plugin/README.md#delegation)).


## Running unattended

### Unattended execution

**Situation.** CI or an agent runner drives the pipeline; nobody will answer a question.

```
/andthen:plan --auto docs/requests/workspace-invitations.md                # from the requirements file; an unsettled decision → Closure: BLOCKED, story blocked
/andthen:exec-plan --auto docs/specs/workspace-invitations/                # runs every spec-ready story, skips blocked ones
/andthen:review --auto --fix --mode code,gap,security,outcome docs/specs/workspace-invitations/plan.json   # the Next: line exec-plan printed
```

**Expect.** `--auto` is the one flag every pipeline skill after requirements shares: no prompts, conservative assumptions written into the artifact, and a hard stop on a bare `BLOCKED: <minimum missing input or decision>` line an orchestrator can parse. The interview is what it cannot buy: `clarify` has no `--auto`, so the pipeline starts at `plan` from a requirements file or tracker item, and `plan --auto` neither interviews nor invents, so an unsettled decision leaves its story `blocked`. `exec-plan --auto` keeps a failed story at its prior status, skips its dependents, finishes the rest, and ends with the aggregate report or `BLOCKED: exec-plan completed with failed stories`. It never reviews the plan itself: the `Next:` line is the review, and something has to launch it.

**Chaining the stages.** An authoring skill ends by printing one next-step line and stopping, because the next stage wants a clean context. Put the chain where the trigger and the authorization already live – a CI job keyed to the merge:

```bash
# on a merge that touched prd.md – plan the bundle in a fresh headless session
claude -p "/andthen:plan --auto docs/specs/workspace-invitations/"

# only if that run printed `Closure: READY`, execute it – again fresh
claude -p "/andthen:exec-plan --auto docs/specs/workspace-invitations/"
```

Each `-p` call is its own session, so the fresh-context property holds by construction. `Closure: READY` is the only verdict that authorizes execution. Codex CLI is the same shape through `codex exec`.

**Elsewhere.** `Closure: BLOCKED` from `plan --auto` is the signal to run `plan` interactively once. A `BLOCKED:` from `exec-plan` names the story; the plan's own rows show where the bundle stands. Contract: [Headless orchestration](plugin/README.md#workflows).


## Reviewing

### A quick look review with no report file

**Situation.** A sanity check before moving on – findings in the conversation, nothing written.

```
/andthen:review "quick look at src/export/ – return the findings here, no report file"
```

**Expect.** The lens set resolves from your words (`code` here; "does this match the spec" is `gap`; security words are `security`), and the same structured findings with `Class:` and `Routing:` come back inline instead of as a report file. Phrasing selects lenses and inline return only; `--fix` writes code and always needs the flag or a direct imperative.

**Elsewhere.** A report is what `implement-fix` consumes, so ask for the file when you intend to remediate.

### Reviewing a very large diff, or keeping a review cheap

**Situation.** A diff too wide for one pass, or the opposite: a review you want in one pass regardless.

```
/andthen:review "review PR 418"                                            # fan-out triggers on diff size, not phrasing
/andthen:review "review src/billing/ in one pass – don't split this into partitions"
```

**Expect.** Fan-out into partition reviews plus a boundary pass is decided by surface size; a large PR gets it without asking. *"Don't split this into partitions"* forces a single pass and the report says so – you trade coverage for cost knowingly. "Review PR 418" fetches the PR into a scratch worktree and reviews it as a local tree; the project's checks run on it when the branch lives in the repository, a fork PR gets a static pass unless you say "run the checks".

**Elsewhere.** Under `--mode security`, scanner output is compacted by `review`'s bundled script; checklists are the project's own. Contract: [`review`](plugin/README.md#review).

### Does it match the spec, or does it solve the problem

**Situation.** A story or the whole plan is built, and the question is either "is this what the FIS said" or "does what we built do the job the PRD stated" – different evidence, different lens.

```
/andthen:review "does this match the spec?" docs/specs/workspace-invitations/s02-accept-an-invitation.md
/andthen:review --mode gap docs/specs/workspace-invitations/plan.json                      # the whole plan, every story
/andthen:review --mode outcome docs/specs/workspace-invitations/plan.json                  # the built feature against prd.md
```

**Expect.** `gap` is conformance: every Acceptance Scenario, Structural Criterion, and stated deferral against the implementation, a falsifier attempted per row, a `PASS`/`FAIL` verdict over a scored dimension table. `outcome` never reads the FIS proofs: it walks the product as the PRD's Target Users along its flows – a browser journey by hand or through `visual-validation` when the surface is a UI, the CLI or API by hand otherwise – with each user's unhappy path as the falsifier. It needs a PRD (`BLOCKED: outcome has no PRD baseline` without one). An implementation short of the PRD is a `code-defect`; a PRD the build has overtaken routes to `clarify`, never to code. Reports land in the spec directory of the plan or FIS the run resolved, named `<feature>-andthen-gap-review-<agent>-<date>.md` or `…-andthen-outcome-review-…`, and open with a header naming the lens, the typed target, and the revision reviewed.

**Elsewhere.** Both lenses run in the plan-level chain `exec-plan` hands over, so after a full plan run this is its `Next:` line, not a separate call. A PR target works too – it is reviewed as a local tree. Contract: [`review`](plugin/README.md#review).

### Review, then remediate

**Situation.** You want the findings applied, not only written – or you have a report from an earlier pass and want it worked off.

```
/andthen:review --fix src/export/                                   # report, then the Fix set applied
/andthen:review "review src/export/ and fix what you find"          # the imperative is the flag
/andthen:implement-fix docs/specs/workspace-invitations/workspace-invitations-andthen-mixed-review-claude-2026-09-15.md
```

**Expect.** `--fix` hands the report to `implement-fix` once it is written: one round – re-validate, apply the `Routing: Fix` findings, verify once, re-check every finding. `Note` findings are never edited, whatever their severity; they come back to you, with the `## Remediation Status` the pass writes into the report, and a Fix whose repair would settle a decision the project leaves open is `DEFERRED` to the Tech Debt Backlog against that blocker. A report with nothing Fix-routed returns `NO-OP: no-auto-applicable-findings`. The change stays in the working tree; nothing is committed.

**Elsewhere.** "This should be cleaned up" is not authorization: the review stays read-only and names `--fix`. `--fix` on a PR target is rejected – the scratch tree is discarded, so there is nothing to remediate. More than one round is [the loop below](#review-and-fix-until-clean-from-a-coordinating-session). Contract: [`implement-fix`](plugin/README.md#implement-fix).

### Review and fix until clean, from a coordinating session

**Situation.** A plan is built and you want review and remediation repeated until the review comes back clean, without the reports and diffs filling the session you steer from.

```
Run a review/fix loop on the implementation of docs/specs/<feature>/plan.json.
Delegate every review and every fix round to its own fresh subagent; this conversation
only coordinates and reports.

Each review subagent invokes the andthen:review skill on that plan with
"--auto --mode code,gap,security,outcome"; from the second review on, it also asks for
a follow-up on the previous report, by its path. Each fix subagent invokes the
andthen:implement-fix skill with "--auto" on the report that review wrote.

Stop when a review's overall readiness is Ready/PASS or nothing is Fix-routed. Also
stop, and report, when a finding survives a fix round unchanged or a fix needs a
decision. Finish with the final verdict, the report paths, and the remaining Note and
DEFERRED findings.
```

**Expect.** One full review, then follow-up reviews over the previous report's findings, what their fixes touched, and regressions from them – each a full `review` run on the same lenses with its own report and verdict, its `Follows` header naming the report before it. The narrowing is yours: it happens because the prompt asks for a follow-up, and a review that is not asked stays full, reading earlier reports only to say which of their findings are resolved, still open, or regressed. The loop ends on the verdict, never on a severity count – a `Note` finding is never edited and a `DEFERRED` one waits in the Tech Debt Backlog, so "until no MEDIUM remains" cannot terminate while either is MEDIUM. Both come back to you with the last report; a blocked CRITICAL or HIGH fix escalates instead, which is the "needs a decision" stop.

**Elsewhere.** One round is `review --fix` above. A full sweep after the loop is the same `review` command with no follow-up asked. Contract: [`review`](plugin/README.md#review).


## Across people and sessions

### Team story work

**Situation.** Several people take stories from one plan; the tracker is where the rest of the team looks.

```
/andthen:tracker publish docs/specs/workspace-invitations/plan.json --dry-run   # see the payloads first
/andthen:tracker publish docs/specs/workspace-invitations/plan.json
"claim S02 for alex"                                                            # sets the story's owner in plan.json
git switch -c feat/S02-accept-an-invitation                                     # {type}/{story-id}-{slug}
/andthen:exec-spec docs/specs/workspace-invitations/s02-accept-an-invitation.md
/andthen:tracker publish docs/specs/workspace-invitations/plan.json             # re-publish to refresh
```

**Expect.** `publish` creates one parent issue and one child per story, titled `S02 - Accept an invitation`, each carrying a plan/story marker so a re-run updates instead of duplicating; the child projects `dependsOn`, completed task IDs, and owner from the plan. The claim is asked for in words – the session edits the row. `plan.json` is agent truth while the plan governs; the tracker is the human projection, one way, repo → tracker – reprioritising in the tracker is a re-plan.

**Elsewhere.** The five steps, the local-files-versus-tracker table, and the merge record are in the [root README](README.md#working-in-a-team); GitLab and Linear are rows you fill in the `Issue Tracker` document's operation table.

### Resuming interrupted work

**Situation.** Context is running out, the session is ending mid-story, or you are picking up someone else's branch.

```
/andthen:handoff "finish S02 – accept path is green, revoke check still red"   # before you stop
```

then, in the fresh session, paste the line the handoff printed:

```
Resume from .agent_temp/handoff/handoff-20260831-142210.md
```

**Expect.** `handoff` routes the durable fragments home – story status and claims into `plan.json`, bounded traps into `Learnings` – and writes the rest (open questions, what was tried, the recommended next skill) to `.agent_temp/handoff/handoff-<UTC-ts>.md`. The next session reads it cold; no skill is needed to resume.

**Without a handoff.** Asking what is active reads `docs/specs/workspace-invitations/plan.json` – status and completed task IDs are the answer – and `/andthen:now-what` routes from the artifacts on disk. Mid-story, `exec-spec` resumes from the recorded task IDs and attributes the dirty tree: earlier story work stays in scope, foreign paths are never staged or reverted.

### Moving project knowledge out of auto-memory

**Situation.** Claude Code's auto-memory has accumulated project facts – traps, decisions, conventions – that only you, on this machine, can see; teammates and Codex read the committed documents. Any other per-user store the host keeps takes the same sweep.

```
"Sweep your auto-memory for this project: anything project-durable moves to its committed home – traps to Learnings, decisions to Decisions, conventions to the guidelines – verified against the repo first. What the repo already records is deleted; personal preferences and machine facts stay. List every move."
```

**Expect.** `handoff`'s durability rule, applied to the store instead of the conversation: a trap becomes one bullet under the fitting topic of `Learnings` or its shard, admitted against the header note; a decision is recommended as a `Decisions` entry, not written, since that document is authorial; a convention goes to the guidelines. Each fact is checked against the current code before it moves – a memory records what was true when it was written – and one the code or git history already carries is deleted, not moved. The memory file and its index line both go, and the run ends with the moves, the deletions, and what it left as recommendations.

**Elsewhere.** `handoff` routes the same fragments home from a conversation at a session boundary; this is for the store that outlives sessions. A trap the sweep keeps meeting belongs in a lint or test check, after which its `Learnings` bullet is deleted – the document's header says so.


## Backlog

### A bounded backlog pass

**Situation.** Untriaged tracker items are piling up.

```
/andthen:backlog-triage "triage the ten oldest"
/andthen:backlog-triage 212 215                          # specific items
```

**Expect.** Per item: a category (`bug` / `enhancement`), one recommended state (`needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`, or close as already implemented), and a one-line rationale – ratified by you before any label or comment is written, because a wrong `wontfix` is visible to the whole team. "The ten oldest" is the cap; the default is no cap. `ready-for-agent` items get an `## Agent Brief` appended, and the hand-off is by size: a small fix to `implement-fix`, real edges to `plan` with the issue URL, a thin item to `clarify` first.

**Elsewhere.** A live failure to debug is [a bug or a broken build](#a-bug-or-a-broken-build), not this.


## The worked example: workspace invitations

One initiative end to end. The project is *Relay*, a Python web app with `pytest`, `Key Dev Commands` filled in (`fast` = `pytest -q tests/unit`, `full` = `pytest -q`, run one test = `pytest -q {file}::{test}`), and `init` already run. Three stories; a milestone branch `1.2` off `main`; story branches off `1.2`. Each turn shows the prompt, what came back, and where the next conversation starts.

### Turn 1 – rough request → PRD *(session A)*

```
/andthen:clarify "we need a way to invite people to a workspace by email"
```

The skill infers feature scope and says so, checks the codebase for what already exists (a `Mailer`, a `Member` model, no invitation concept), then interviews – two rounds, recommendation first:

> Who may invite – any member or owners only? *Recommended: owners only for now; opening it up is a one-line change later.*
> What happens to an invitation nobody accepts? *Recommended: it expires; the window is a product call.*
> Can an owner take an invitation back? *Recommended: yes, revoke; a revoked token must fail on accept.*
> Existing account vs new sign-up on accept? …

Terms settle as they go: `Invitation`, `Member`, `Owner` land in `docs/UBIQUITOUS_LANGUAGE.md`. The answers structure into the PRD: problem, three functional requirements (`FR-1 Send an invitation`, `FR-2 Accept an invitation`, `FR-3 Revoke and list pending invitations`) with acceptance criteria, non-functional thresholds (email dispatch never blocks the request), scope in and out. The one open question – *expiry window, 7 days or 30?* – lands in `Constraints & Assumptions` as unresolved. A fresh-context self-review applies two mechanical fixes, and the run ends:

```
docs/specs/workspace-invitations/prd.md            > **Source**: inline description
Run the andthen:plan skill on docs/specs/workspace-invitations/.
```

**Checkpoint.** The PRD is the initiative's surviving record and the last cheap place to change scope. On a team, this is the PR to `1.2` carrying `prd.md`.

**Conversation boundary.** Fresh session. `plan` reads the PRD once and spawns one spec subagent per story; two interview rounds and a review transcript are the wrong context for it.

### Turn 2 – plan bundle *(session B)*

```
/andthen:plan docs/specs/workspace-invitations/
```

Story breakdown, `plan.json`, three FIS files authored in parallel by `spec --auto --batch story S0N of …plan.json` subagents, one cross-cutting review across all three, then preflight.

```json
{
  "schemaVersion": "2",
  "prd": "prd.md",
  "overview": {
    "summary": "Owners invite teammates by email; invitees accept a single-use token; owners can see and revoke what is pending."
  },
  "sharedDecisions": [
    {
      "title": "Invitation token lifetime",
      "description": "Tokens expire 7 days after creation; S01 stamps expires_at, S02 refuses an expired token with 410.",
      "stories": ["S01", "S02"]
    }
  ],
  "bindingConstraints": [{ "featureId": "FR-1", "anchor": "prd.md#non-functional-requirements" }],
  "stories": [
    { "id": "S01", "name": "Send an invitation", "dependsOn": [],
      "status": "spec-ready", "fis": "s01-send-an-invitation.md", "completedTaskIds": [], "owner": null,
      "scope": "An owner creates a pending Invitation for an email address and the invitee receives one email carrying a single-use link.",
      "sourceRefs": ["prd.md#fr-1-send-an-invitation"], "provenance": null, "assetRefs": [], "sequencing": null },
    { "id": "S02", "name": "Accept an invitation", "dependsOn": ["S01"],
      "status": "spec-ready", "fis": "s02-accept-an-invitation.md", "completedTaskIds": [], "owner": null,
      "scope": "A valid token turns its invitee into a Member and is consumed; expired or unknown tokens are refused.",
      "sourceRefs": ["prd.md#fr-2-accept-an-invitation"], "provenance": null, "assetRefs": [], "sequencing": null },
    { "id": "S03", "name": "Revoke pending invitations", "dependsOn": ["S02"],
      "status": "spec-ready", "fis": "s03-revoke-pending-invitations.md", "completedTaskIds": [], "owner": null,
      "scope": "An owner lists pending invitations and revokes one; a revoked token fails on accept.",
      "sourceRefs": ["prd.md#fr-3-revoke-and-list-pending-invitations"], "provenance": null, "assetRefs": [],
      "sequencing": "Revocation is only observable once accept exists to refuse it." }
  ]
}
```

The `sharedDecisions` entry is the expiry question: preflight asked it once, you answered *7 days*, and the answer landed at the altitude that owns it – cross-story, so the plan. Each FIS carries its own runnable proof surface, for example `s01-send-an-invitation.md`:

```markdown
# FIS: Send an invitation

**Plan**: docs/specs/workspace-invitations/plan.json
**Story-ID**: S01

## Feature Overview and Goal

**Intent**: an owner must be able to bring a teammate in without an admin, so an invitation carries a single-use token to the invitee's email.

**Expected Outcomes**:
- `[OC01]` An owner's invite request produces one pending Invitation and one email.
- `[OC02]` A non-owner's invite request is refused.

## Acceptance Scenarios

- **S01 [OC01] An owner's invite creates one pending invitation and sends one email**
  - **Given** an owner of workspace W and no invitation for a@example.com
  - **When** POST /workspaces/W/invitations with that address returns 201
  - **Then** one Invitation exists with expires_at 7 days out and the mailer sent exactly one message
  - **Proof**: `tests/invitations/test_send.py#test_owner_invite_creates_one_invitation` – red at spec time
- **S02 [OC02] A member who is not an owner is refused**
  - **Proof**: `tests/invitations/test_send.py#test_non_owner_is_forbidden` – red at spec time

## Structural Criteria

- **SC01** The email is dispatched off the request path

## Implementation Plan

### Implementation Tasks

- **TI01** POST /workspaces/{id}/invitations creates the Invitation and enqueues the email
  - **Verify**: `tests/invitations/test_send.py#test_owner_invite_creates_one_invitation`
  - **SATISFIES**: S01
- **TI02** Non-owners receive 403
  - **Verify**: `tests/invitations/test_send.py#test_non_owner_is_forbidden`
  - **SATISFIES**: S02
- **TI03** Dispatch goes through the existing background queue
  - **Verify**: `cmd: pytest -q tests/invitations/test_send.py::test_send_is_enqueued_not_awaited`
  - **SATISFIES**: SC01
```

Preflight ran its tail on every story – settle, re-canonicalize, size gate, proof-design audit – and printed:

```
Closure: READY
Run the andthen:exec-plan skill on docs/specs/workspace-invitations/.
```

**Checkpoint.** Every story is `spec-ready`. Read the three FIS files once – scope, non-goals, proof targets – cheaper now than mid-execution. On a team: PR `plan.json` and the FIS files to `1.2` beside the PRD, and review the slicing there. Solo, commit the bundle:

```
"commit the prd and plan bundle"   # git add -- docs/specs/workspace-invitations/ ; git commit
```

**Conversation boundary.** The printed line runs every story for you; this example drives the inner loop by hand to show what one story looks like. Either way, execution starts in a fresh session: an executor needs its context for the codebase, not for how the plan was argued.

### Turn 3 – story S01 through the inner loop *(session C)*

`spec` is already done for this story – the plan bundle authored it. Three steps remain: branch, execute, ship.

```
git switch -c feat/S01-send-an-invitation 1.2            # {type}/{story-id}-{slug}
/andthen:exec-spec docs/specs/workspace-invitations/s01-send-an-invitation.md
```

The run resolved the plan from the FIS header, wrote the three tests and confirmed each red for the scenario's reason, implemented `TI01`–`TI03` in `src/invitations/` recording each in the story's `completedTaskIds` as its `Verify` passed, then ran the full tier and every proof itself. Its completion report:

```
TI01 done · TI02 done · TI03 done
Changed: src/invitations/models.py, src/invitations/routes.py, src/invitations/jobs.py, tests/invitations/test_send.py

full tier   – pytest -q – exit 0
S01 Proof   – pytest -q tests/invitations/test_send.py::test_owner_invite_creates_one_invitation – exit 0
S02 Proof   – pytest -q tests/invitations/test_send.py::test_non_owner_is_forbidden – exit 0
TI01 Verify – pytest -q tests/invitations/test_send.py::test_owner_invite_creates_one_invitation – exit 0
TI02 Verify – pytest -q tests/invitations/test_send.py::test_non_owner_is_forbidden – exit 0
TI03 Verify – pytest -q tests/invitations/test_send.py::test_send_is_enqueued_not_awaited – exit 0

Reviewed: fresh reviewer subagent, review --quick --fix --intent s01-send-an-invitation.md.
  Fixed (1): F1 HIGH token compared with == in routes.py:41, timing-observable → hmac.compare_digest; focused test re-run, exit 0.
  Open (1): F2 MEDIUM Mailer.send swallows SMTP errors – pre-existing, outside this FIS (Routing: Note).

Chain Attestation: OC01 holds – S01 passed, satisfied by TI01 and TI03. OC02 holds – S02 passed, satisfied by TI02.
Observations: docs/specs/workspace-invitations/s01-send-an-invitation.md#implementation-observations
NOTICED BUT NOT TOUCHING: Mailer.send swallows SMTP errors

S01 record: fis s01-send-an-invitation.md · completedTaskIds TI01, TI02, TI03
            verified 2026-08-31T14:22Z "full tier – pytest -q – exit 0" · status done
Commit: 4f2c9a1 feat(S01): send an invitation
```

Three things the report does not spell out. The reviewer was a fresh subagent, so the independent pass was not the implementer's to give; F1 was Fix-routed and applied as the story's one repair round, F2 stays open and reported, never gated. `status done` went into the row beside that `verified` line – the quoted line is the durable trace once the bundle is deleted, and `done` is never written without it. The commit staged the changed files, the plan, and the FIS by path, so the `Story-ID:` and `Plan:` trailers ride it.

**Checkpoint.** The one thing to read by hand is the open Note – whether `Mailer.send` becomes a Tech Debt entry is a human call.

### Turn 4 – ship S01 *(session C continues)*

Open the PR to `1.2`. Its squash-merge message carries the FIS head – the subject, `Intent:`, up to five `Expected Outcomes:`, and the two trailers – so the *why* survives the bundle's deletion and `git log --grep S01` finds it afterwards:

```
feat(invitations): send an invitation [S01]

Intent: an owner must be able to bring a teammate in without an admin, so an invitation carries a single-use token to the invitee's email.

Expected Outcomes:
- [OC01] An owner's invite request produces one pending Invitation and one email.
- [OC02] A non-owner's invite request is refused.

Story-ID: S01
Plan: docs/specs/workspace-invitations/plan.json
```

On a team it also says `Closes #<the S01 child issue>`.

**Conversation boundary.** Merge, then a fresh session per story. Nothing from session C is needed: the FIS is the story's whole context and `plan.json` is the state.

### Turns 5–6 – S02 and S03 by reference

Same three steps each, from an up-to-date `1.2`:

```
git switch -c feat/S02-accept-an-invitation 1.2
/andthen:exec-spec docs/specs/workspace-invitations/s02-accept-an-invitation.md
```

S02 recorded one Drift Note: the PRD's accept flow said `GET`, the implementation is `POST` because a `GET` would leak the token into access logs. It sits under `#### DRIFT` in the FIS's Implementation Observations as `- spec-stale: accept is POST, not GET as prd.md#fr-2 says | Stale targets: prd.md#fr-2-accept-an-invitation | –`. The story's quick review read it before flagging, so it routed as a Note instead of a fresh blocker; the PRD edit is recommended, never applied – reconciliation above the FIS stays yours.

S03 `dependsOn` S02, so it starts only after S02 merged. Before it ran, S02's report surfaced one constraint for it – the revoke endpoint must invalidate the queued email too – which landed under `## Discovered Requirements` in `s03-revoke-pending-invitations.md` before any code depending on it.

Between stories, state is one ask away:

```
"progress on the invitations plan?"   # reads docs/specs/workspace-invitations/plan.json
```

```
## Progress Summary
- **Total Stories**: 3
- **Done**: 2 (67%)
- **In Progress**: 0
- **Spec Ready**: 1
- **Pending**: 0
- **Skipped**: 0
- **Blocked**: 0
- **Dependency Ready**: S03
```

### Turn 7 – plan-level review and merge *(on `1.2`, after S03 merged)*

Each story was reviewed against its own change set; the plan as a whole has not been, and `now-what` says so – every story `done`, no `*-mixed-review-*.md` beside `plan.json`. One deep pass, remediating whatever it routes `Fix`:

```
/andthen:review --mode code,gap,security,outcome --fix docs/specs/workspace-invitations/plan.json
```

Then retire the bundle before the milestone PR: read each FIS's `## Implementation Observations` first and land what belongs in `Learnings` or `Decisions`, because the bodies – Drift Notes, cited ADRs – go with the files. `prd.md` stays. Open the milestone PR `1.2` → `main`.

**What survives.** `prd.md`, the merge commits carrying `Story-ID:` and `Plan:` trailers, the tests, and on a team the issues and PRs.
