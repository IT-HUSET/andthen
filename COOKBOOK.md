# AndThen Cookbook

What to type for a given situation, and what to expect back. The [root README](README.md) says what AndThen is; the [skill reference](plugin/README.md) carries each skill's flags, modes, and edge cases, which this file does not repeat.

Each recipe has a **Situation** (skim these to find yours), a paste-ready prompt, **Expect** (the artifact or closing line), and **Elsewhere** (where else to go). Prompts are the mechanism: skills read intent from your words, and a flag appears only where it changes a machine-consumed contract (`--mode`), a safety boundary (`--fix`), or the run mode (`--auto`, for an unattended run). Commands are shown in Claude Code form (`/andthen:<name>`); Codex CLI uses the same skill names through its own skill syntax. Skills recommend complete invocations in your host's syntax, including the target or request and required arguments, so you can paste the whole line.

**Contents**

- **[Starting work](#starting-work)**: [Choosing a path](#choosing-a-path) · [One story or several](#one-story-or-several) · [A small change](#a-small-change) · [A bug or a broken build](#a-bug-or-a-broken-build) · [An existing codebase](#an-existing-codebase) · [Product vision vs feature](#product-vision-vs-feature-clarify) · [An intent doc first](#an-intent-doc-before-the-prd) · [Revising a spec](#revising-a-spec-or-re-planning)
- **[The design stage](#the-design-stage)**: [Technical decisions or an architecture question](#technical-decisions-or-an-architecture-question) · [Event storming](#event-storming-a-new-domain-or-a-system-to-rewrite) · [Research, design system, wireframes](#research-a-design-system-wireframes) · [A second opinion](#a-second-opinion-before-committing-to-a-decision)
- **[Running unattended](#running-unattended)**: [Unattended execution and CI chaining](#unattended-execution)
- **[Reviewing](#reviewing)**: [Quick look, big PR, one pass](#review-phrasing-a-quick-look-a-big-pr-one-pass) · [Spec fit vs problem fit](#does-it-match-the-spec-or-does-it-solve-the-problem) · [Review, then remediate](#review-then-remediate) · [Review/fix loop](#review-and-fix-until-clean-from-a-coordinating-session)
- **[Across people and sessions](#across-people-and-sessions)**: [Working in a team](#working-in-a-team) · [Resuming interrupted work](#resuming-interrupted-work)
- **[Backlog](#backlog)**: [A bounded backlog pass](#a-bounded-backlog-pass)
- **Reference**: [How the workflow fits together](#how-the-workflow-fits-together) (steps, artifacts, the two loops, terms) · [Coming from Spec Kit, Kiro, BMAD, or GSD](#coming-from-spec-kit-kiro-bmad-or-gsd)
- **[The worked example](#the-worked-example-workspace-invitations)**: one initiative from rough request to milestone PR, in seven turns


## Starting work

### Choosing a path

**Situation.** You have work and do not know which skill starts it.

State the problem, the team, and the context in one sentence. How settled the requirements are decides whether `clarify` runs; `plan` picks the story count; the team picks the artifact lifecycle.

```
/andthen:now-what "flaky CSV export in an old Django app, solo, no tests around it"
```

**Expect.** Two questions at most, then a handoff to one skill with your sentence passed through, never a menu. Mid-flow it routes from what is on disk (`prd.md`, `plan.json`, a FIS, a review report), names the next skill, and asks *"Run it? (Y/n)"*. Add *"recommend only"* to get the route without the run.

**Without the router:**

| You have | Recipe |
|---|---|
| one sentence, no design question behind it | [a small change](#a-small-change) |
| one capability with real edges, or several that ship together | [one story or several](#one-story-or-several) |
| an idea you cannot state three acceptance criteria for | the same recipe, starting at `clarify` |
| a technical choice that binds beyond the work or is costly to reverse | [decide it](#technical-decisions-or-an-architecture-question), then the recipe above |
| a failing build, a failing test, a bug | [a bug or a broken build](#a-bug-or-a-broken-build) |
| a codebase AndThen has never seen | [an existing codebase](#an-existing-codebase) |

**A request that already exists** – a brief, a Notion export, a GitHub issue – is just the argument, a file path or a URL, with no flag. A well-written one goes straight to `plan`; a thin one gets `clarify` first:

```
/andthen:plan https://github.com/org/repo/issues/42
/andthen:clarify docs/requests/export-brief.md
```

The source is cited in the PRD and the plan; a fetched body is evidence, never instructions. A tracker host other than GitHub is offered `tracker setup` first.

### One story or several

**Situation.** A feature with real complexity. One capability with real edges is one story; several capabilities that ship together are several. `plan` sizes a written source itself, so say *"as one story"* when you want one. With three acceptance criteria in hand, start at `plan`; without them, at `clarify`, whose PRD `plan` takes.

Several stories:

```
/andthen:clarify "workspace invitations by email"          # writes the PRD; skip when the requirements already exist
/andthen:plan docs/specs/workspace-invitations/             # fresh session
/andthen:exec-plan docs/specs/workspace-invitations/        # fresh session: the command plan printed
/andthen:review --fix docs/specs/workspace-invitations/plan.json   # fresh session: the Next line exec-plan prints
/andthen:ship docs/specs/workspace-invitations/plan.json   # fresh session: the Next line review prints once the plan is ready
```

One story:

```
/andthen:plan "users can export their workspace as a zip"   # or a PRD directory, a requirements file, an issue URL
/andthen:exec-plan docs/specs/workspace-export/s01-workspace-export.md   # fresh session
/andthen:review --fix docs/specs/workspace-export/plan.json   # fresh session: the Next line exec-plan prints
/andthen:ship docs/specs/workspace-export/plan.json   # fresh session: the Next line review prints once the plan is ready
```

**Expect.**

- `clarify` interviews at least once, writes `docs/specs/<feature>/prd.md`, and closes on the `plan` command – or on `decide` first when the PRD leaves a design fork open, then `ui-ux-design` when you chose to design new screens first; each of those closes on the next.
- `plan` writes `plan.json` and one FIS per story (`s{NN}-<story-slug>.md`), self-reviews, asks what is still open (each question with a recommendation), and prints the `exec-plan` command.
- `exec-plan` on a plan directory runs one fresh subagent per ready story, the full tier on the final tree, and one `simplify-code` pass. It ends on the `Next (fresh session):` line above, whose `--fix` remediates the report it just wrote.
- `exec-plan` on one FIS implements the story where you invoke it: every proof, the full tier, one fresh quick reviewer, the story's `done` record, and the story commit, plus one `simplify-code` pass when it completes the plan. It prints the review line above.
- After the plan review, `now-what` routes a failing load-bearing check to `triage`; it recommends `ship` only when the plan meets the canonical Shipping condition.

**Elsewhere.**

- A question left unanswered becomes an `ASSUMPTION:` line in the FIS. To overturn one before execution, re-run `/andthen:plan "story S02 of docs/specs/workspace-invitations/plan.json"` with your answer.
- `OVERSIZE:` means a story does not fit one run: `plan` offers to slice it, in the same run for a written source and through `clarify` for a description, or to proceed as one.
- To drive stories by hand, run `exec-plan` per story – [the worked example](#the-worked-example-workspace-invitations) does.
- A failed story reports its route out: `review --fix` on the story's changed paths, for correctness and against its FIS (under `--worktree`, in the story's preserved worktree), then `exec-plan` again on the same input.

Contracts: [`plan`](plugin/README.md#plan), [`exec-plan`](plugin/README.md#exec-plan).

### A small change

**Situation.** A bug fix or small feature you can state in a sentence, with no design question behind it.

```
/andthen:implement-fix "return 404 instead of 500 when an export job id does not exist"
```

**Expect.** Your sentence is the whole Fix set: tests first where the change adds a branch, the change, the project's checks, and a diff pass as the review. No FIS, no plan state, nothing committed – the verified change stays in the working tree. Beyond it, only small tidies in the files the change touches are made, each named. A larger issue the sentence did not ask for comes back under `NOTICED BUT NOT TOUCHING:` rather than as an edit.

**Elsewhere.** A sentence that turns out to describe a feature, a PRD, or a plan stops at the scope guard and points at `plan` → `exec-plan`, with `clarify` first when requirements are still open. Contract: [`implement-fix`](plugin/README.md#implement-fix).

### A bug or a broken build

**Situation.** Something is red and you do not yet know why.

```
/andthen:triage "tests fail on main since yesterday"
/andthen:triage https://github.com/org/repo/issues/57               # the bug report is the scope
/andthen:triage --plan-only "checkout returns 500 on an empty cart"   # diagnosis and a fix plan, no edits
/andthen:testing --mode prove-it "login fails when the email has a plus sign"   # you know the defect; the test is the proof
```

**Expect.** `triage` reproduces the symptom, finds the root cause, fixes it, and runs the project's checks; the originating symptom is the gate, not a green local test. Traps go to `Learnings`, deferred fixes to the `Tech Debt` backlog, and a discovery too large for a fix is offered to `clarify --brief`. It never touches `plan.json`. `prove-it` writes the failing test that reproduces the defect before any production change.

**Elsewhere.** A change you can already state with no diagnosis is [a small change](#a-small-change). Sorting incoming tracker items is the [backlog pass](#a-bounded-backlog-pass).

### An existing codebase

**Situation.** AndThen has never run here, and the project has history, conventions, and code nobody has written down.

```
/andthen:init
/andthen:describe --mode codebase      # init's closing summary offers it; run it yourself when you declined
```

**Expect.** `init` asks nothing here. It writes the Project Document Index into your root instruction file, `Key Dev Commands` from your manifest (the `fast` and `full` tiers and a run-one-test row), and the `.gitignore` entries; the first skill that writes to any other indexed document creates it. The closing summary offers `describe --mode codebase`, the four role agents, and the critical-rules starter. `describe` fills `Architecture` and `Key Dev Commands` from the code and adds `requirements-discovered.md` and `decisions-discovered.md`; existing documents are merged into, judgment sections kept.

**Elsewhere.** `now-what` routes from here. A glossary is `describe --mode domain`; refreshing a model alone is `--model-only` ([`describe`](plugin/README.md#describe)).

### Product vision vs feature clarify

**Situation.** You want to talk about what the product *is*, or `clarify` guessed the wrong altitude.

```
/andthen:clarify "clarify the product vision for Relay"           # product scope
/andthen:clarify "treat this as feature scope: shared inboxes"     # override a wrong product inference
```

**Expect.** Scope is inferred from the wording (`vision`, `positioning`, `product brief`, or a `PRODUCT.md` path mean product) and stated before the interview, so you can redirect. Product scope writes `docs/PRODUCT.md`, Proportionality facts included, and recommends bounded-context work next. Feature scope writes `docs/specs/<feature>/prd.md` and ends on the `plan` command. A hand-written `intent.md` is valid input at either scope; it is folded into the output and left as it was.

### An intent doc before the PRD

**Situation.** The idea is yours alone so far. You want to sharpen it, put it in front of a colleague or a customer, and only then commit to a PRD – or it is a decision or a proposal you want grilled before you present it.

```
/andthen:clarify --brief "workspace invitations by email"            # the interview, stopped at intent.md
/andthen:clarify docs/specs/<feature>/                               # later, over the edited intent doc: the PRD
/andthen:clarify --brief "should we move the team to trunk-based development"   # not a feature: same rounds, same document
```

**Expect.** Questions in rounds (everything answerable now, each with a recommended answer), stopped where you say the picture is clear enough to share. Then `docs/specs/<subject>/intent.md`: problem, proposed outcome, affected systems, constraints, open questions (each with a recommended answer and alternatives), and a decisions log.

Edit it freely: answer an open question in place, or leave it and it is asked again. The second run takes the file as baseline, folds every section into the PRD, and asks only what the edits opened or left open. A second `--brief` run amends the intent doc instead. A subject that is not this product's feature is not anchored to `PRODUCT.md` or the architecture.

**Elsewhere.** Feature scope only; at product scope `PRODUCT.md` is already the one document. A directory that already holds a `prd.md` gets no intent doc. One story the intent doc already settles needs no PRD: `plan` takes the directory.

### Revising a spec or re-planning

**Situation.** A FIS needs a change before it runs – an answer that overturns an `ASSUMPTION:`, a scope correction – or the source changed and the plan no longer matches.

```
/andthen:plan "docs/specs/workspace-export/s01-workspace-export.md – exports are capped at 2 GB; revise this FIS"
/andthen:plan "story S02 of docs/specs/workspace-invitations/plan.json – invite links now expire after 72 hours; revise its FIS"
/andthen:plan "docs/specs/workspace-invitations/ – the PRD dropped bulk invites; re-plan from it, S01 is done and stays out of scope"
```

**Expect.** `plan` has no revision mode, so the prompt carries it: what you point at is the source, what you say changed is the correction, and the run writes the FIS (for a re-plan, the whole bundle) through the usual questions, self-review, and Preflight. A re-plan keeps nothing of the old `plan.json` and renumbers its stories from `S01`, so a new FIS can take a finished story's path. First `git mv` the old `plan.json` and FIS files into a `superseded/` folder beside the PRD, name the finished stories so they stay out, and delete the folder once the new bundle is in place.

**Elsewhere.** Finish a story that has started, or reset it in words first (*"reset S02 to pending, clearing its task IDs"*); otherwise its row names tasks the new FIS no longer has. Contract: [`plan`](plugin/README.md#plan).


## The design stage

### Technical decisions or an architecture question

**Situation.** You know what to build, and the how still has open choices – a queue, a storage shape, a boundary – that later stories will build on. Or you only want advice on how to shape something.

```
/andthen:decide docs/specs/workspace-export/
/andthen:decide "compare three options for the export job queue: Postgres SKIP LOCKED, Redis streams, SQS"
/andthen:architecture "how should the export pipeline be structured so a failed step can be retried without redoing the others?"
```

**Expect.** `decide` lists the decision points it finds and sorts them. It interviews you, in rounds with a recommendation each, on those that bind beyond one story or are costly to reverse. A story-local one goes to `plan`'s Preflight, a user-visible requirement back to `clarify`, and an already settled one is cited. Once you confirm the played-back set, it writes an ADR under `docs/adrs/` and a row in `docs/DECISIONS.md` per real decision, or one Still Current line for a choice with no real alternative.

The second prompt asks for a comparison, so that decision gets the weighted trade-off: criteria and weights for you to confirm, then `docs/research/<topic-slug>/` (design tree, research, trade-off matrix, recommendation). "Three options" sets the count (the default is five); every set includes the floor option (do nothing, or extend what exists). The third prompt is `architecture`'s `advise` mode: prose guidance sized against your `Product` document's Proportionality facts, with `decide` offered when it settles a choice worth recording. Neither changes code.

**Elsewhere.** A question only measurement settles ("is A faster than B under our load?") is the `spike` skill: a throwaway on `spike/<slug>` and a verdict. Architecture review, splitting a package, bounded contexts, event storming: `architecture` in its other modes ([`architecture`](plugin/README.md#architecture)).

### Event storming a new domain or a system to rewrite

**Situation.** The domain is new to you, or you are taking over a system that needs a rewrite, and you want its events, actors, and open questions on one board before writing requirements.

```
/andthen:architecture --mode event-storming "order fulfilment, checkout to delivery"
/andthen:architecture --mode event-storming "order fulfilment as built, from the code"    # before a rewrite
/andthen:clarify "order fulfilment v2, from the event storm .agent_temp/reviews/<report>.md"
/andthen:visualize docs/models/event-storms/<slug>.json
```

**Expect.** You are the domain expert: the run asks where the timeline has gaps or unclear causes, at Big Picture unless you name Process Modeling or Design Level. It writes a report under `.agent_temp/reviews/` and the board as `docs/models/event-storms/<slug>.json`, the slug taken from the scope, and a later run on the same scope continues that board. For a rewrite, storm the system as built, then the target under a second scope, and ask that run what is kept, renamed, and dropped. The report's hotspots are open questions, which makes it a good `clarify` source; `--mode event-storming,strategic-design` turns its subdomain candidates into bounded contexts in one run. `visualize` draws the board as a page.

### Research, a design system, wireframes

**Situation.** UI work is coming: nobody has said who uses it, no shared tokens exist, or the FIS should not invent the screens.

```
/andthen:ui-ux-design "user research for the export flow: who exports, when, what they do with the file"
/andthen:ui-ux-design "create a design system from docs/specs/workspace-invitations/prd.md"
/andthen:ui-ux-design "wireframe the invitation flow from docs/specs/workspace-invitations/prd.md"
/andthen:ui-ux-design "research, then a design system, then wireframes for the onboarding flow in docs/specs/onboarding/prd.md"
```

**Expect.** The mode follows the phrasing:

- `research` returns in the conversation, no file: the job-to-be-done, two to five journeys, an IA sketch, constraints, and open questions (`clarify` input).
- `design-system` writes `docs/design-system/DESIGN.md` (token front matter plus rationale), `tokens.css`, and `showcase.html`. Push back on a bland result: deliberate visual direction is the mode's bar.
- `wireframes` writes grayscale HTML with full page coverage under `docs/wireframes/`, an `index.html` hub and a `page-inventory.md`, validated through `visual-validation`.

Naming modes in order, as in the last prompt, runs them in that order sharing context; there is no chain flag. A run from a PRD closes on the `plan` command; `plan` cites the wireframes and `exec-plan` builds to them.

**Elsewhere.** Validating a built screen is `visual-validation`, not a design mode. Questions about requirements rather than interaction are `clarify` territory.

### A second opinion before committing to a decision

**Situation.** The session has proposed a design, a scope cut, or a plan shape, and you want an independent view before acting. Nothing spawns this on its own – you ask.

```
"Sounds good – but before we go on, ask an oracle subagent for a second opinion: give it the decision, your reasoning, and the alternatives you rejected, and ask where it's wrong."
```

**Expect.** The subagent sees none of the conversation, so the hand-over (decision, reasoning, rejected alternatives, constraints) is all it can judge. It returns the failure mode or wrong assumption it finds, with evidence, or an agreement that names what it checked. It touches nothing; the decision stays yours. Without the `oracle` role installed, a generic subagent takes the same hand-over.

**Elsewhere.** An artifact with a rubric (a PRD, a plan, a FIS, a diff) is `review`. A question only measurement settles is the `spike` skill. Claude Code's built-in advisor is the model-initiated form ([Delegation](plugin/README.md#delegation)).


## Running unattended

To run a skill from CI or an agent runner with no one to answer, pass `--auto` ([what the run does then](plugin/README.md#workflows)).

### Unattended execution

**Situation.** CI or an agent runner drives the pipeline; nobody will answer a question.

Every skill in the chain takes the same flag:

```
/andthen:plan --auto docs/requests/workspace-invitations.md    # open questions → ASSUMPTION: lines
/andthen:exec-plan --auto docs/specs/workspace-invitations/    # runs every ready story
/andthen:review --auto --fix docs/specs/workspace-invitations/plan.json   # the Next (fresh session): line exec-plan printed
```

**Expect.** Every pipeline skill after requirements reads `--auto` the same way: no prompts, and a stop only on an unusable call, ending on `BLOCKED: <what is needed>`.

- `clarify` has no unattended form (the interview is what `--auto` cannot buy), so the pipeline starts at `plan` from a requirements file or tracker item.
- `plan` records each open question's recommendation in the FIS as an `ASSUMPTION:`.
- `exec-plan` on a plan leaves a failed story `in-progress`, skips its dependents, finishes the rest, and ends with the aggregate report. It never reviews the plan itself: the `Next (fresh session):` line is the review, and something has to launch it.
- `review --fix` passes the flag on to `implement-fix`, which gives every `Note` and `NOTICED BUT NOT TOUCHING` item an interactive run would hand back one disposition: applied, deferred to the Tech Debt Backlog, or closed with a reason.

**Chaining the stages.** An authoring skill prints one next-step line and stops, because the next stage wants a clean context. Put the chain where the trigger and authorization already live, such as a CI job keyed to the merge:

```bash
# on a merge that touched prd.md – plan the bundle in a fresh unattended session
claude -p "/andthen:plan --auto docs/specs/workspace-invitations/"

# if that run succeeded, execute it – again fresh
claude -p "/andthen:exec-plan --auto docs/specs/workspace-invitations/"
```

Each `-p` call is its own session, so fresh context holds by construction. Codex CLI is the same shape through `codex exec`.

**Elsewhere.** Read the `ASSUMPTION:` lines the unattended `plan` wrote before trusting the bundle; overturn one with `plan` on that story's FIS and your answer. Contract: [Unattended runs](plugin/README.md#workflows).


## Reviewing

### Review phrasing: a quick look, a big PR, one pass

**Situation.** A sanity check with nothing written, a diff too wide for one pass, or the opposite: a review you want in one pass regardless.

```
/andthen:review --quick "quick look at src/export/ – return the findings here, no report file"
/andthen:review "review PR 418"                                            # fan-out triggers on diff size, not phrasing
/andthen:review "review src/billing/ in one pass – don't split this into partitions"
```

**Expect.**

- The lens set resolves from your words (`code` for a plain review; "does this match the spec" is `gap`; security words are `security`). `--quick` returns the same structured findings, with `Class:` and `Routing:`, inline instead of as a report file. Omit `--quick` when you intend to remediate from a report, since `implement-fix` consumes one.
- Fan-out into partition reviews plus a boundary pass follows surface size; a large PR gets it without asking. *"Don't split this into partitions"* forces a single pass, and the report says so.
- "Review PR 418" reviews the PR as a local tree in a scratch worktree; a fork PR gets a static pass unless you say "run the checks".
- Phrasing selects lenses and can suppress fan-out. Only `--quick` selects inline return. `--fix` writes code and always needs the flag or a direct imperative.

**Elsewhere.** `--mode security` calibrates severity by exposure tier and runs the project's own scanners. Contract: [`review`](plugin/README.md#review).

### Does it match the spec, or does it solve the problem

**Situation.** A story or the whole plan is built, and the question is either "is this what the FIS said" or "does what we built do the job the PRD stated" – different evidence, different lens.

```
/andthen:review "does this match the spec?" docs/specs/workspace-invitations/s02-accept-an-invitation.md
/andthen:review --mode gap docs/specs/workspace-invitations/plan.json                      # the whole plan, every story
/andthen:review --mode outcome docs/specs/workspace-invitations/plan.json                  # the built feature against prd.md
```

**Expect.**

- `gap` is conformance: every Acceptance Scenario, Structural Criterion, and stated deferral against the implementation, a falsifier attempted per row, a `PASS`/`FAIL` verdict over a scored dimension table.
- `outcome` never reads the FIS proofs. It needs a PRD and walks the product as the PRD's Target Users along their flows (a browser journey by hand or through `visual-validation` for a UI, the CLI or API by hand otherwise), with each user's unhappy path as the falsifier. An implementation short of the PRD is a `code-defect`; a PRD the build has overtaken routes to `clarify`, never to code.
- Reports land beside the plan or FIS the run resolved, named `<feature>-andthen-gap-review-<agent>-<date>.md` or `…-andthen-outcome-review-…`.

**Elsewhere.** Both lenses run in the plan-level chain `exec-plan` hands over, so after a full plan run this is its `Next (fresh session):` line, not a separate call. A PR target works too. Contract: [`review`](plugin/README.md#review).

### Review, then remediate

**Situation.** You want the findings applied, not only written – or you have a report from an earlier pass and want it worked off.

```
/andthen:review --fix src/export/                                   # report, then the Fix set applied
/andthen:review "review src/export/ and fix what you find"          # the imperative is the flag
/andthen:implement-fix docs/specs/workspace-invitations/workspace-invitations-andthen-mixed-review-claude-2026-09-15.md
```

**Expect.** `--fix` hands the written report to `implement-fix` for one round: re-validate, apply the `Routing: Fix` findings, verify once, re-check every finding.

- In an attended run, `Note` findings are not edited without your direction, whatever their severity. They come back to you in the `## Remediation Status` the pass writes into the report. Under `--auto`, eligible Notes can be promoted to Fix as [unattended execution](#unattended-execution) describes.
- A Fix whose repair would settle a decision the project leaves open is `DEFERRED`: offered to you, or written to the Tech Debt Backlog in an unattended run.
- When the round fixed a CRITICAL or HIGH finding or left a Fix finding open, the run ends on a `Next (fresh session):` line for a follow-up review; otherwise one round is the whole job.
- The change stays in the working tree; nothing is committed.

**Elsewhere.** "This should be cleaned up" is not authorization: the review stays read-only and names `--fix`. `--fix` on a PR target is rejected – the scratch tree is discarded, so there is nothing to remediate. More than one round is [the loop below](#review-and-fix-until-clean-from-a-coordinating-session). Contract: [`implement-fix`](plugin/README.md#implement-fix).

### Review and fix until clean, from a coordinating session

**Situation.** A plan is built and you want review and remediation repeated until the review comes back clean, without the reports and diffs filling the session you steer from.

```
Run a review/fix loop on the implementation of docs/specs/<feature>/plan.json.
Delegate every review and every fix round to its own fresh subagent; this conversation
only coordinates and reports.

Each review subagent invokes the andthen:review skill on that plan; from the
second review on, it also asks for a follow-up on the previous report, by its
path. Each fix subagent invokes the
andthen:implement-fix skill on the report that review wrote. Every subagent brief
passes --auto.

Stop when a review's overall readiness is Ready/PASS or a fix round fixes nothing. Also
stop, and report, when a finding survives a fix round unchanged or a fix needs a
decision. Finish with the final verdict, the report paths, and the remaining Note and
DEFERRED findings.
```

**Expect.** One full review, then follow-up reviews: each a full `review` run on the same lenses with its own report and verdict, a `Follows` header naming the report before it, and a summary of which of that report's open findings are now resolved or still open.

The loop ends on the verdict, never on a severity count: a `Note` the fix round closes with a reason or defers keeps its MEDIUM in the report, so "until no MEDIUM remains" cannot terminate. A blocked CRITICAL or HIGH fix is deferred and escalated, which is the "needs a decision" stop. Both come back to you with the last report.

**Elsewhere.** One round is `review --fix` above. Contract: [`review`](plugin/README.md#review).


## Across people and sessions

### Working in a team

The pipeline does not change per tracker; the tracker is a projection of the plan, never a second source of truth. Five steps:

1. **A request arrives** as a tracker item – one line or a long brief.
2. **Outer loop, once per epic** – `clarify <item-url>` → `prd.md` → `plan` → `plan.json` + a FIS per story → **PR to the milestone branch**, where the team reviews the PRD and the plan. An item that already states its requirements goes straight to `plan <item-url>`.
3. **Publish the breakdown** – `tracker publish plan.json` creates one parent issue and one child issue per story (scope, PRD anchors, a commit-pinned FIS link, blocked-by links, completed task IDs); a re-run updates them.
4. **Inner loop, once per story** – claim the story's issue by assigning it to yourself, branch (`{type}/{story-id}-{slug}`) → `exec-plan`, its quick review included → PR with `Closes #N`. Merge closes the issue natively.
5. **State** – `plan.json` is agent truth while the plan governs; the tracker is the human projection (re-run `tracker publish` to refresh it). `prd.md` outlives the bundle; the issues and PRs are the per-story record.

A single story is the same flow with a different argument:

| Step | Local files | Tracker |
|---|---|---|
| Request | any short source – inline, a file, an `intent.md`, or a `clarify` PRD | issue URL / key |
| Plan | `plan <source>` → the FIS plus its one-story plan on the feature branch | `plan <issue-url>` → same bundle; the plan records the URL as its source |
| Build + prove | `exec-plan` → `review --fix` → `ship` | same; PR body `Closes #42` |
| Status | branch + PR | native: branch name / PR link moves the issue, merge closes it |
| Record after merge | the PR and commits – each story commit carries the FIS head (intent and expected outcomes), kept through the merge | the issue and the PR |
| Close-out | `ship`, once the plan-level review's `Next (fresh session):` line names it: Observations land in `Learnings`, the rest is recommended, then `plan.json` and the FIS files are deleted before the plan's branch merges; `prd.md` stays | same |

A PRD leaves `prd.md` behind as the requirements record; any other source leaves only the request itself. Concurrent stories need no shared state file: `plan.json` is the one state owner, and per-story FIS prose is frozen.

**In commands**, with several people taking stories from one plan:

```
/andthen:tracker publish docs/specs/workspace-invitations/plan.json --dry-run   # see the payloads first
/andthen:tracker publish docs/specs/workspace-invitations/plan.json
git switch -c feat/S02-accept-an-invitation                                     # {type}/{story-id}-{slug}
/andthen:exec-plan docs/specs/workspace-invitations/s02-accept-an-invitation.md
/andthen:tracker publish docs/specs/workspace-invitations/plan.json             # re-publish to refresh
```

Each child issue is titled `S02 - Accept an invitation`. The projection is one way, repo → tracker, so reprioritising in the tracker is a re-plan. GitLab and Linear are rows you fill in the `Issue Tracker` document's operation table.

### Resuming interrupted work

**Situation.** Context is running out, the session is ending mid-story, or you are picking up someone else's branch.

```
/andthen:handoff "finish S02 – accept path is green, revoke check still red"   # before you stop
```

then, in the fresh session, paste the line the handoff printed:

```
Resume from .agent_temp/handoff/handoff-20260831-142210.md
```

**Expect.** `handoff` routes durable fragments home (bounded traps into `Learnings`) and writes the rest – open questions, what was tried, the recommended next skill – to `.agent_temp/handoff/handoff-<UTC-ts>.md`. The next session reads it cold; no skill is needed to resume.

**Without a handoff.** Asking what is active reads `docs/specs/workspace-invitations/plan.json` – status and completed task IDs are the answer – and `/andthen:now-what` routes from the artifacts on disk. Mid-story, `exec-plan` reruns the story using its existing work and plan state; earlier story edits stay in scope, and foreign paths are never staged or reverted.


## Backlog

### A bounded backlog pass

**Situation.** Untriaged tracker items are piling up.

```
/andthen:tracker triage "the ten oldest"
/andthen:tracker triage 212 215                          # specific items
```

**Expect.** Per item: a category (`bug` / `enhancement`), one recommended state (`needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`, or close as already implemented), and a one-line rationale – ratified by you before any label or comment is written, because a wrong `wontfix` is visible to the whole team. "The ten oldest" is the cap; the default is no cap. `ready-for-agent` items get an `## Agent Brief`, and the hand-off is by size: a small fix to `implement-fix`, real edges to `plan` with the issue URL, a thin item to `clarify`.

**Elsewhere.** A live failure to debug is [a bug or a broken build](#a-bug-or-a-broken-build), not this.


## How the workflow fits together

Reference for [the workflow](README.md#the-workflow): what each step reads and writes, where design decisions enter, how long each artifact lives, and the terms the skills use.

| Step | Skill | Reads | Writes |
|---|---|---|---|
| Setup, once per project | `init` | the repository | the Project Document Index in `CLAUDE.md` / `AGENTS.md`, `Key Dev Commands`, the `.gitignore` entries; every other document on its first write |
| Requirements, optional | `clarify` | your idea, or a source from anywhere – a pasted note, a tracker issue, an `intent.md` | `prd.md` – what to build and why |
| Design, optional | `decide`, `ui-ux-design` | the PRD or the request | ADRs and Decisions lines; a design system or wireframes |
| Plan | `plan` | a description, a `prd.md` (or its directory), a requirements file, a tracker issue | `plan.json` – the stories, their dependencies and status – plus one FIS per story |
| Build | `exec-plan`, on a FIS or the plan directory | `plan.json` and the FIS | the code, one commit per story carrying its FIS head, each story `done` in `plan.json` |
| Review and fix | `review --fix` | `plan.json` – its PRD and FIS files – and the code | a review report beside `plan.json`, and the fixes |
| Ship | `ship` | each FIS's `## Implementation Observations` and the branch's commits | `Learnings` bullets and printed recommendations; `plan.json` and the FIS files deleted, `prd.md` kept; the commits; the PR after one confirmation |

`plan` sizes the work before it writes a FIS. When a story still turns out too big for one run, it offers to split it – in the same run for a written source, through `clarify` for a description. `review --fix` is one review and one fix round; when it fixed a CRITICAL or HIGH finding or left a Fix finding open, it prints a follow-up review as its `Next (fresh session):` line. Once the plan's stories are all `done` or `skipped` (cut from scope) and nothing CRITICAL or HIGH is open, its `Next (fresh session):` line runs `ship` instead; `implement-fix` run on the report closes the same way.

### The design stage and ADRs

Two skills settle what the requirements left open, neither changing code: `decide` (a technical interview, a weighted trade-off where a choice is contested, ADRs) and `ui-ux-design` (research, design systems, wireframes). `architecture` advises, and its analysis modes can feed a decision first. An ADR comes in at three points, on one test – the choice binds beyond this work or is costly to reverse:

- **Before the spec** – `clarify` makes `decide` its closing command when the PRD leaves such a fork open.
- **While specifying** – a fork only the spec surfaces is a Preflight question; you answer it into the FIS, and the ADR is recommended as its record. That `decide` run records your answer without asking it again and closes on `exec-plan`.
- **While building** – a real pivot in `exec-plan` records one before the FIS changes.

Design comes in before the spec, on your answer: `clarify` asks at its playback whether new screens no wireframes cover are designed first, and `plan` asks the same when its source skipped `clarify`. Either way `ui-ux-design` closes on `plan`.

### The artifacts – where each comes from, who reads it, how long it lives

| Artifact | Written by | Read by | Lifecycle |
|---|---|---|---|
| any short source – `intent.md` is one shape | anyone, by hand; `clarify --brief` writes `intent.md` | `clarify`, `plan`, `now-what`, `architecture` | superseded – `clarify` folds it into `prd.md`, `plan` into the FIS |
| `PRODUCT.md` | the first of `clarify`, `decide`, `plan`, `architecture` to ask its Proportionality facts, or `clarify` at product scope | every proposal skill, as the proportionality anchor | durable |
| `prd.md` | `clarify` | `plan`, `review --mode gap,outcome` | survives the merge – the product record |
| `plan.json` | `plan`; runtime state by the session executing each story (under `--worktree`, by the plan run before each batch) | `exec-plan`, `review`, `now-what`, `tracker`, `ship` | branch-scoped – deleted by `ship` before the merge |
| FIS (one per story) | `plan`, one fresh subagent per story when there are several | `exec-plan`, `review`, `ship` | branch-scoped – deleted by `ship` before the merge |
| Review report | `review` | `implement-fix` | one run's working file – ignored by default, committed once the project drops its `.gitignore` line |
| `LEARNINGS.md`, `DECISIONS.md` | `decide` (ADR rows, Still Current lines), `ship` at close-out (it writes `Learnings` and recommends `Decisions`), and the agents that read them after triage | every skill at task start | durable |

### The two loops

- **Outer loop, once per initiative** – `clarify`, then `plan`: what and why, then a FIS per story.
- **Inner loop, once per story** – `exec-plan`: build one story and prove it, review included, then on a team its PR into the milestone branch. On the plan directory `exec-plan` runs this loop for you, one story at a time in the shared tree, or independent stories in parallel under `--worktree`, one worktree each.

**When the PR opens.** `ship` opens it, after one confirmation. The plan's branch ships once its plan-level review's `Next (fresh session):` line names `ship`: solo, that is the plan's one PR. On a team, `ship` on a story branch opens the story PR and keeps the bundle, because later stories still read it; the close-out runs on the milestone branch before the milestone PR, after the per-story PRs have merged into it.

This is a scope-and-cadence split, not the DevEx sense of inner loop (edit-build-test) versus outer loop (CI/CD). A third motion, the **knowledge cycle**, is not a loop: FIS `Implementation Observations` graduate into `LEARNINGS.md` at close-out through `ship`, which recommends the `DECISIONS.md` lines, recurring review traps become lint rules or tests, and settled trade-offs become ADRs.

### Terms

- **Story** – one bounded, verifiable unit of work that fits one fresh-context run, 1:1 with a FIS. `OVERSIZE:` means it does not fit: split it (recommended) or proceed knowingly.
- **Plan Bundle** – the feature directory holding `plan.json`, its FIS files, and `prd.md` when a PRD was the source.
- **FIS** – Feature Implementation Specification, one per story: intent, expected outcomes, acceptance scenarios with runnable `Proof` bindings, and tasks, each naming what it `SATISFIES` and how to `Verify` it.
- **Preflight** – the closing round of `plan`: every question the run could not answer itself, asked in one sitting with a recommendation preselected and answered into the FIS. Unanswered, the recommendation is recorded as an assumption.
- **Verification tier** – `fast` or `full`, declared in `Key Dev Commands`. `exec-plan` on one FIS runs `full`; on a plan directory each story gets `fast` and the final tree gets `full` once.


## Coming from Spec Kit, Kiro, BMAD, or GSD

**Where AndThen sits.** Spec Kit is a spec-driven toolkit: its core commands form one chain from `constitution` to `converge`; debugging comes from a bundled opt-in `bug` extension, code review and existing-codebase work from community extensions. In AndThen the spec-driven workflow is the main path, not the whole: `review`, `triage`, `testing`, `architecture`, `describe`, and the design skills work with or without a spec. The workflow is spec-first with programmatic enforcement: `sourceRefs` and `SATISFIES` backlinks trace requirements to stories and tasks while the plan governs, and a story reaches `done` only with the line naming what was run to prove it. The limit is deliberate: a team needing audit-grade, permanent spec traceability (a regulator, a requirement→test matrix that outlives the merge) needs a spec-anchored tool, since AndThen keeps governing artifacts branch-scoped.

**Reading across frameworks.** The frameworks differ first in scope. Within the spec-driven part they share the same layers under different names, and "spec" is the word they disagree on most:

| Layer | Anthropic AI-native SDLC playbook | Spec Kit | Kiro | BMAD | GSD (Get Shit Done) | AndThen |
|---|---|---|---|---|---|---|
| Scope – what it covers | a guide, not a tool: six stages, Plan to Maintain | spec-driven development; debugging and review are extensions | agentic IDE, CLI, web app: spec sessions, hooks, steering | agile delivery by agent roles, product to testing | phase loop: discuss, plan, execute, verify, ship; plus milestones, codebase mapping, debugging, quick mode | spec-driven workflow plus skills that run without a spec |
| Intake – the problem, before committing | `intent.md` | `intake.md` … `decision.md` (opt-in `assess` extension) | – | project brief | questioning in `new-project`; no document | any short source; `intent.md` is one shape |
| Requirements – what to build, what counts as done | `spec.md` | `spec.md`, replacing the PRD | `requirements.md` | `SPEC.md` from `bmad-spec`; PRD only when several must agree | `PROJECT.md` + `REQUIREMENTS.md`; every plan must cover the IDs | `prd.md`, written by `clarify` |
| Architecture – structure, trade-offs, decisions | inside `spec.md`; no separate decision record | `research.md`, `data-model.md`; ADRs are community extensions | `design.md` per spec; `structure.md` steering file | Architect agent's doc: real trade-offs only, IDs stories cite; readiness gate before stories | decisions in `CONTEXT.md`; `map-codebase` writes `ARCHITECTURE.md` | `decide` writes ADRs; `architecture` and `describe` analyse and map |
| UX/UI design – research, design system, screens | UX standards applied as skills while writing `spec.md` | none in core; Figma and wireframe community extensions | none built in; opt-in Figma power | UX Designer agent: `DESIGN.md`, `EXPERIENCE.md`, both optional | `ui-phase` writes `UI-SPEC.md`, `sketch` HTML mockups, `ui-review` a six-pillar audit | `ui-ux-design`; `visual-validation` checks the built UI |
| Plan and execution – split, order, run | `plan.md`, built in parallel worktree sessions | `plan.md` + `tasks.md`; `[P]` tasks run in parallel | `tasks.md`; one at a time or in dependency waves | `bmad-ticket` orders stories in `tickets.toml`; `bmad-build` plans each and hands it to a subagent | `ROADMAP.md` phases; `execute-phase` runs plans in parallel waves, each in a fresh agent | FIS per story + `plan.json`; `exec-plan`, fresh subagent per story, parallel under `--worktree` |
| Intent and proof – goal, outcomes, proof each is met | `intent.md` states the outcome; `plan.md` defines the proof | Given/When/Then, `FR-` and `SC-` IDs; test tasks only on request; `analyze` flags uncovered requirements | EARS criteria (WHEN … THE SYSTEM SHALL …); optional property-based tests | criteria from the epic's *Done when* and `Verify:`; runs the plan's Verification commands | `must_haves` and per-task `<verify>`; gate requires every REQ-ID | tagged outcomes, scenarios, some with a runnable `Proof`; `done` needs the line naming what ran |
| Review – does the build match the ask | self-verify, then PR review under `REVIEW.md` | `converge` checks code against spec, plan, tasks | none of its own; property tests and hooks | parallel reviewers on the diff; Test Architect `trace` gate | fresh verifier writes `VERIFICATION.md`; `verify-work` is human UAT; `code-review` as a separate agent | `review`: code, gap, security, outcome lenses; a fresh reviewer per story |

The row that trips people up is Requirements: AndThen's "spec" is the FIS, and it sits **downstream** of the PRD rather than replacing it. Arriving from Spec Kit or BMAD, you will map it one layer too high.

**What the critiques ask for.** The standing critique of spec-driven development is that a spec written up front assumes implementation teaches nothing, and that an agent verifying its own work will certify it. Beyond the four mechanisms at the top of the [root README](README.md):

- **Learning during implementation** – requirements found mid-execution are appended through the FIS's Discovered Requirements channel before the code that needs them, and deliberate divergence is a Drift Note, which `ship` reads at close-out with the rest of the Implementation Observations.
- **Agents reviewing their own work** – a fresh reviewer subagent takes the executor's attestation as the claims to falsify, so nothing completes on its author's own reading.
- **Repeat incidents** – a reproducible bug gets a failing test before the fix.


## The worked example: workspace invitations

One initiative end to end. The project is *Relay*, a Python web app with `pytest`, `init` already run, and `Key Dev Commands` filled in (`fast` = `pytest -q tests/unit`, `full` = `pytest -q`, run one test = `pytest -q {file}::{test}`). Three stories; a milestone branch `1.2` off `main`; story branches off `1.2`. Each turn shows the prompt, what came back, and where the next conversation starts.

### Turn 1 – rough request → PRD *(session A)*

```
/andthen:clarify "we need a way to invite people to a workspace by email"
```

The skill infers feature scope and says so, checks the codebase for what exists (a `Mailer`, a `Member` model, no invitation concept), then interviews in two rounds, recommendation first:

> Who may invite – any member or owners only? *Recommended: owners only for now; opening it up is a one-line change later.*
> What happens to an invitation nobody accepts? *Recommended: it expires; the window is a product call.*
> Can an owner take an invitation back? *Recommended: yes, revoke; a revoked token must fail on accept.*
> Existing account vs new sign-up on accept? …

Terms settle as they go: `Invitation`, `Member`, `Owner` land in the PRD's `Decisions Log`, since Relay keeps no glossary document. The answers become the PRD: problem, three functional requirements (`FR-1 Send an invitation`, `FR-2 Accept an invitation`, `FR-3 Revoke and list pending invitations`) with acceptance criteria, non-functional thresholds (email dispatch never blocks the request), and scope in and out. The one open question – *expiry window, 7 days or 30?* – lands in `Constraints & Assumptions` as unresolved. A fresh-context self-review applies two mechanical fixes, and the run ends:

```
docs/specs/workspace-invitations/prd.md            > **Source**: inline description
Next (fresh session): /andthen:plan docs/specs/workspace-invitations/
```

**Checkpoint.** The PRD is the initiative's surviving record and the last cheap place to change scope. On a team, this is the PR to `1.2` carrying `prd.md`.

**Conversation boundary.** Fresh session: `plan` reads the PRD once, and two interview rounds are the wrong context for it.

### Turn 2 – plan bundle *(session B)*

```
/andthen:plan docs/specs/workspace-invitations/
```

Three functional requirements in two modules size to several stories, so `plan` runs the breakdown: `plan.json`, three FIS files authored in parallel by unattended `plan` subagents (one per `story S0N of …plan.json`), one cross-cutting review, then Preflight.

```json
{
  "schemaVersion": "2",
  "prd": "docs/specs/workspace-invitations/prd.md",
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
  "bindingConstraints": [{ "featureId": "FR-1", "anchor": "docs/specs/workspace-invitations/prd.md#non-functional-requirements" }],
  "stories": [
    { "id": "S01", "name": "Send an invitation", "dependsOn": [],
      "status": "pending", "fis": "s01-send-an-invitation.md", "completedTaskIds": [],
      "scope": "An owner creates a pending Invitation for an email address and the invitee receives one email carrying a single-use link.",
      "sourceRefs": ["docs/specs/workspace-invitations/prd.md#fr-1-send-an-invitation"] },
    { "id": "S02", "name": "Accept an invitation", "dependsOn": ["S01"],
      "status": "pending", "fis": "s02-accept-an-invitation.md", "completedTaskIds": [],
      "scope": "A valid token turns its invitee into a Member and is consumed; expired or unknown tokens are refused.",
      "sourceRefs": ["docs/specs/workspace-invitations/prd.md#fr-2-accept-an-invitation"] },
    { "id": "S03", "name": "Revoke pending invitations", "dependsOn": ["S02"],
      "status": "pending", "fis": "s03-revoke-pending-invitations.md", "completedTaskIds": [],
      "scope": "An owner lists pending invitations and revokes one; a revoked token fails on accept.",
      "sourceRefs": ["docs/specs/workspace-invitations/prd.md#fr-3-revoke-and-list-pending-invitations"],
      "sequencing": "Revocation is only observable once accept exists to refuse it." }
  ]
}
```

The PRD's open expiry question was asked before slicing, since two stories build on it: you answered *7 days*, the answer went into the PRD's `Constraints & Assumptions` through `clarify`'s amendment, and the `sharedDecisions` entry pins the contract in the plan and each FIS. Each FIS carries its own runnable proof surface, for example `s01-send-an-invitation.md`:

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
- **S02 [OC02] A member who is not an owner is refused**
  - **Given** a member of workspace W who is not an owner
  - **When** they POST /workspaces/W/invitations with an email address
  - **Then** the request returns 403, with no Invitation created or email queued

## Structural Criteria

- **SC01** The email is dispatched off the request path

## Implementation Plan

### Implementation Tasks

- **TI01** POST /workspaces/{id}/invitations creates the Invitation and enqueues the email
  - **Verify**: `cmd: pytest -q tests/invitations/test_send.py::test_owner_invite_creates_one_invitation`
  - **SATISFIES**: S01
- **TI02** Non-owners receive 403
  - **Verify**: `cmd: pytest -q tests/invitations/test_send.py::test_non_owner_is_forbidden`
  - **SATISFIES**: S02
- **TI03** Dispatch goes through the existing background queue
  - **Verify**: `cmd: pytest -q tests/invitations/test_send.py::test_send_is_enqueued_not_awaited`
  - **SATISFIES**: SC01
```

Authoring left nothing open, so Preflight asked nothing, and `plan` printed:

```
Next (fresh session): /andthen:exec-plan docs/specs/workspace-invitations/
```

**Checkpoint.** Every story is `pending` with its FIS. Read the three FIS files once – scope, non-goals, proof targets – which is cheaper now than mid-execution. On a team, PR the bundle to `1.2` beside the PRD and review the slicing there. Solo, commit it:

```
"commit the prd and plan bundle"   # git add -- docs/specs/workspace-invitations/ ; git commit -- docs/specs/workspace-invitations/
```

**Conversation boundary.** The printed line runs every story for you; this example drives the inner loop by hand to show one story. Either way, execution starts in a fresh session.

### Turn 3 – story S01 through the inner loop *(session C)*

The plan bundle already authored this story's FIS. Three steps remain: branch, execute, ship.

```
git switch -c feat/S01-send-an-invitation 1.2            # {type}/{story-id}-{slug}
/andthen:exec-plan docs/specs/workspace-invitations/s01-send-an-invitation.md
```

The run resolved the plan from the FIS header, wrote the three tests and confirmed each red for its intended behavior, implemented `TI01`–`TI03` in `src/invitations/` (recording each in `completedTaskIds` as its `Verify` passed), then ran the full tier, the new scenario proofs, and every `Verify` itself. Its illustrative completion report shows the result each command returned:

```
TI01 done · TI02 done · TI03 done
Changed: src/invitations/models.py, src/invitations/routes.py, src/invitations/jobs.py, tests/invitations/test_send.py
Tidied: routes.py – dropped an unused import

full tier   – pytest -q -> exit=0, 3 passed in 0.12s
S01 Proof   – pytest -q tests/invitations/test_send.py::test_owner_invite_creates_one_invitation -> exit=0, 1 passed in 0.04s
S02 Proof   – pytest -q tests/invitations/test_send.py::test_non_owner_is_forbidden -> exit=0, 1 passed in 0.04s
TI01 Verify – pytest -q tests/invitations/test_send.py::test_owner_invite_creates_one_invitation -> exit=0, 1 passed in 0.04s
TI02 Verify – pytest -q tests/invitations/test_send.py::test_non_owner_is_forbidden -> exit=0, 1 passed in 0.04s
TI03 Verify – pytest -q tests/invitations/test_send.py::test_send_is_enqueued_not_awaited -> exit=0, 1 passed in 0.04s

Reviewed: fresh reviewer subagent, review quick pass with --fix against s01-send-an-invitation.md.
  Fixed (1): F1 HIGH token compared with == in routes.py:41, timing-observable → hmac.compare_digest; focused test re-run, exit 0, 1 passed.
  Open (1): F2 MEDIUM Mailer.send swallows SMTP errors – pre-existing, outside this FIS (Routing: Note).

Chain Attestation: OC01 holds – S01 passed, satisfied by TI01 and TI03. OC02 holds – S02 passed, satisfied by TI02.
Observations: docs/specs/workspace-invitations/s01-send-an-invitation.md#implementation-observations
NOTICED BUT NOT TOUCHING: Mailer.send swallows SMTP errors

S01 record: fis s01-send-an-invitation.md · completedTaskIds TI01, TI02, TI03
            verified 2026-08-31T14:22Z "pytest -q -> exit=0, 3 passed in 0.12s" · status done
Commit: 4f2c9a1 feat(S01): send an invitation

Next (fresh session): /andthen:exec-plan docs/specs/workspace-invitations/s02-accept-an-invitation.md
```

Three things the report does not spell out. The reviewer was a fresh subagent, so the pass was independent; F1 was Fix-routed and applied as the story's one repair round, and F2 stays open and reported, never gated. `status done` went into the row beside the `verified` line, the durable trace once the bundle is deleted; `done` is never written without it. The commit staged the changed files, the plan, and the FIS by path, so the `Story-ID:` and `Plan:` trailers ride it.

**Checkpoint.** The one thing to read by hand is the open Note – whether `Mailer.send` becomes a Tech Debt entry is a human call.

### Turn 4 – ship S01 *(session C continues)*

`ship` on the story branch opens the PR to `1.2` and, with stories still to run, keeps the bundle. The story commit already carries the FIS head – the subject, `Intent:`, `Expected Outcomes:`, and the two trailers – so keep it as the squash-merge message: the *why* survives the FIS's deletion and `git log --grep S01` finds it:

```
feat(S01): send an invitation

Intent: an owner must be able to bring a teammate in without an admin, so an invitation carries a single-use token to the invitee's email.

Expected Outcomes:
- [OC01] An owner's invite request produces one pending Invitation and one email.
- [OC02] A non-owner's invite request is refused.

Story-ID: S01
Plan: docs/specs/workspace-invitations/plan.json
```

On a team it also says `Closes #<the S01 child issue>`.

**Conversation boundary.** Merge, then a fresh session per story: the FIS is the story's whole context and `plan.json` is the state.

### Turns 5–6 – S02 and S03 by reference

Same three steps each, from an up-to-date `1.2`:

```
git switch -c feat/S02-accept-an-invitation 1.2
/andthen:exec-plan docs/specs/workspace-invitations/s02-accept-an-invitation.md
```

S02 recorded one Drift Note: the PRD's accept flow said `GET`, the implementation is `POST` because a `GET` would leak the token into access logs. It sits under `#### DRIFT` in the FIS's Implementation Observations as `- spec-stale: accept is POST, not GET as prd.md#fr-2 says | Stale targets: prd.md#fr-2-accept-an-invitation | –`. The story's quick review read it first, so the divergence routed as a Note, not a blocker; the PRD edit is recommended, never applied.

S03 `dependsOn` S02, so it starts only after S02 merged. S02's report surfaced one constraint for it – the revoke endpoint must invalidate the queued email too – which landed under `## Discovered Requirements` in `s03-revoke-pending-invitations.md` before any code depending on it.

Between stories, state is one ask away:

```
"progress on the invitations plan?"   # reads docs/specs/workspace-invitations/plan.json
```

```
## Progress Summary
- **Total Stories**: 3
- **Done**: 2 (67%)
- **In Progress**: 0
- **Pending**: 1
- **Skipped**: 0
- **Dependency Ready**: S03
```

### Turn 7 – plan-level review and merge *(on `1.2`, after S03 merged)*

Each story was reviewed against its own change set; the plan as a whole has not been, and `now-what` says so – every story `done`, and no review report beside `plan.json` targets the plan yet. One deep pass remediates whatever it routes `Fix`, and it reads S01's open Note on `Mailer.send` from the FIS observations, so that comes back routed instead of forgotten:

```
/andthen:review --fix docs/specs/workspace-invitations/plan.json
```

It ends on a `Next (fresh session):` line for `ship`, which runs on `1.2` as the close-out before the milestone PR:

```
/andthen:ship docs/specs/workspace-invitations/plan.json
```

It lands what belongs in `Learnings` from each FIS's `## Implementation Observations` and recommends the rest, including the PRD edit S02's Drift Note names, because the Drift Notes and cited ADRs go with the files. It then deletes `plan.json` and the FIS files (`prd.md` stays), commits, shows the `1.2` → `main` PR title and body, and asks once before it pushes.

**What survives.** `prd.md`, the story commits carrying each FIS head with its `Story-ID:` and `Plan:` trailers, the tests, and on a team the issues and PRs.
