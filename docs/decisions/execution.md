# Decisions: Execution

Rationale, evidence, history, and reopen conditions for the **Execution** bullets in [DECISIONS.md](../DECISIONS.md) § Still Current. Each decision is stated there; a section here holds only what would not fit its one line.

## `--auto` is the only unattended trigger

A host with approvals off does not count, because a host that cannot prompt still leaves the caller free to read the reply. A project-rules "never ask" line is no substitute either: attended sessions read the same file.

A 2026-09-25 change removed the flag and named the caller sentence `This run is unattended: no one can answer until it ends.` instead; its own acceptance gate reverted it two days later, when the `plan` and `architecture` eval cases failed with the sentence in place of the flag. It cost more surface than the flag it replaced (a definition, two disambiguating sentences, a load line in ten skills, and a test pinning them) while hosts still inferred the mode from context, and the load line made attended `implement-fix` read the unattended rules and stop on a trivial question.

Reopens if a caller needs the mode without control of the argument line.

## No skill settles questions its own text asks

`unattended-runs.md` carried a § Headless-First naming four skills (`spec`, `exec-spec`, `triage`, `simplify-code`) that answered routine questions themselves even in an attended run. That set was the set which had linked the retired `automation-mode.md`: a packaging fact about where the `--auto` rules lived, read as a statement about who should ask. It contradicted `spec`'s two ask points and `triage`'s "asked once, recommendation first", and the other two carry no ask contract for it to override. On the `plan` eval it cost the ask it was meant to preserve: attended, no flag, Codex settled the PRD's self-contradiction itself in 3 of 3 runs, Claude in 2 of 3.

Reopens if an executor is measured stopping on a question its own text does not ask.

## A question goes where the run stops for it

Codex's `plan` run asked all four contested items through `request_user_input_async`, a channel that does not end the turn, slept 50s, got `{"accepted":true}` with no answers, and finished on a report. The reply a caller read showed a settled plan, and the four unanswered items shipped as specified behaviour.

The old test was suitability ("where it fits", "suited to the question"), which a multi-choice tool with a preselected recommendation passes perfectly; turn-holding is the property that matters, and it is host-agnostic. Turn-holding is not sufficient, because it is a property of the host's tool and the model judges it wrong (Codex reached for the non-blocking channel in 15 of 15 cells), so the duty is stated about the run's own output and binds whichever channel carried the ask. That is a clarity edit, not a fix: measured 0 of 6 on Codex, where `<collaboration_mode>` licenses continuing whatever our text says. It is a host limitation, not a wording defect, which is why a Codex `plan-asks` failure is recorded as such and there is no third wording attempt.

The five ask sites disagreed before this: `tracker` and `architecture` required an answer before proceeding, `clarify`, `preflight.md` and `plugin/README.md` did not. `tests/test_unattended_runs_load.py` now pins every site that routes an ask to a structured tool (five at 2026-09-28).

"Only where" restricted the tool without preferring it: on 2026-10-04 a Claude Code `plan` Preflight bound to "one sitting" put twelve items in the reply, past `AskUserQuestion`'s four per call, so every site now prefers the tool and every batching site splits a round over consecutive calls.

Separately and not fixable here: DartClaw's Codex adapter accepts that call and neither delivers an answer nor surfaces the request, so on that host the channel is a dead end.

Reopens if a host offers a non-blocking channel that does reliably deliver.

## An assumption is reachable only from a question

The old wording keyed an assumption on a question "nobody answered", which the run certifies about itself: Codex closed the `plan` case with "Unanswered choices … are recorded as assumptions in the specs", having asked nothing. Asked-then-unanswered is a fact about the transcript, so it can be checked, but only if "asked" means the run stopped for the answer: a question sent down a channel the run continued past satisfied the weaker reading, which is how six Codex cells wrote their own choice into the specs.

The canonical rule in `unattended-runs.md` already said "one it continued past was not asked, however the question was sent", but that file loads only under `--auto`, so attended runs read `preflight.md`'s weaker restatement; the two are now one clause pinned in both files. `preflight.md` gates its fallback the same way and has the asking reply answer nothing (no default listed, no assumption written), since a question behind its own recorded answer reads as settled.

## A decision never stops a run

`BLOCKED:` is defined once in `unattended-runs.md`. A run reads an older plan's `blocked` row as `pending`. The dropped markers and per-skill trigger lists had no reader: nothing parsed them, and DartClaw reads its own step-outcome envelope.

Reopens if an orchestrator needs a stop reason beyond `BLOCKED:` versus failure.

## `exec-plan` never stops on FIS detail

The FIS is the executable brief, and authoring polices its detail. The orchestration stops that remain are unresolvable provenance, unfinished dependencies, and an unsafe action. For a foreign change overlapping the story's hunks, only the commit has to stay separate, never the work.

## No edge-case knobs, no strictness blocks, one verification run

Reopens on a case a frontier model running in the repo cannot handle without it.

## A plan run hands off the plan-level review

The hand-off works because `implement-fix` already owns review → fix → closure, including findings the per-story review left open.

Reopens on evidence that a fresh-session review misses cross-story defects the run session caught.

## A plan runs story by story by default

Adopted 2026-10-17. A story run carries each discovery that affects an unstarted story into that FIS before its commit, as a plan run does between stories, and commits it, because the next run treats an uncommitted edit to its own FIS as foreign. Story by story pays one full tier per story where a plan run pays one on the final tree. `plan --auto` prints the first story too, since `--auto` makes the authoring run unattended, not the execution, and a runner that chains `Next` lines still finishes the plan.

The pause is where a person adjusts the spec ahead (2026-10-19): a yes to a contradicting or scope-changing discovery makes the `Next` line that revision, `plan` with the discovery in its request (since `plan` has no re-entry handling), or `clarify`'s amendment. The next story attests each inherited Discovered Requirement over its proof, so its reviewer checks it.

Reopens on evidence that the pause between stories catches nothing a plan run's discovery triage would not.

## Each story is simplified before the next builds on it

Adopted 2026-10-18, replacing the once-per-plan pass in place since rc.4. A story run simplifies after its commit, a plan run after each story. An agent adds code but never volunteers repair. The premise changed, not the evidence: the once-per-plan pass assumed no reader between stories, which the story-by-story default ended. Its cost argument stands, one pass per story. Its duplication argument holds only for parallel siblings, which the batch pass sees merged, because a sequential pass sees every earlier story in the tree. `implement-fix` skips it because its trace test edits back any hunk no finding maps.

Reopens on shipped duplication where an earlier story's code repeats a helper a later story added: that story's pass may not edit the earlier code, so only the reader and the plan-level review catch it.

## The `Product` document is read where scope is chosen or the result validated, never where code is transformed

`plan` already distilled what binds, and a behavior-preserving or finding-bounded change cannot choose scope; the review after a transforming step catches an accidental breach. An inline request adds the Non-Goals because no spec distilled them.

Reopens on a run where a transforming step shipped a change the `Product` document forbids.

## A fresh-session hand-off says so in the line it prints

The line takes the first case of the skill's Follow-up that applies. The Architecture document's Conversation Boundaries map is for maintainers; the user sees only the printed line. 0.x carried clean-session tips, 1.0 trims dropped them, and a 2026-09-24 manual `plan` run closed on a bare `exec-plan` command. One shape, because a 2026-10-02 audit found two: `clarify` and `plan` printed prose that does not paste. It also found menus in `ui-ux-design` and `review`, and `decide` and design reachable only by an aside.

Reopens if a host starts skill hand-offs in a fresh context on its own.

## Per-story parallelism is plain git in the run session, not AndThen scripts

A worktree comes from `git worktree add`, one per story of a batch of the wave, merged per return. Each story carries its code, FIS appends, and its own `plan.json` row, edited in place so sibling rows merge cleanly and nothing is reconciled. A failed story reports the conflicting paths. The flags and the `merge-resolve` squash protocol were dropped because Agent Teams is host-experimental, and squash was what made rollback, the `Squashed-story:` trailer, and `branch -D` necessary.

## The `ops` skill and its script are retired

No script and no reconciliation code close the 0.14.4 concurrent-writer collision (`e5202ed`): no copy of the file has two writers at once. A story run of `exec-plan` (direct on a FIS, or a plan run's story subagent) loads neither `plan-schema.md` nor `plan.schema.json` and writes its row from `story.md` alone: `status: in-progress` before its first edit, then at Step 4 `fis`, `completedTaskIds`, `verified: {at, summary}`, and `status: done`. Under `--worktree` the row is edited in place (2026-09-29): a review found no silent rule whose absence yields a row that fails validation or is misread (serialisation layout is valid either way, only two hand-started direct runs in one tree could race), and each story run loads about 620 fewer words. Reopens if a story-written row fails validation or is misread on a recorded run.

No script parses an agent-read document (FIS, Index, Key Dev Commands, Learnings) for meaning: each parser pinned its document's shape (the Index could not stop being a table, a FIS bullet could not gain a word before its id), and that cost was paid on every edit of the document. No validator for plans or models: none caught anything on a recorded run, a dangling FIS pointer surfaces when the FIS is opened, and producers check their candidate against the schema shipped beside its reference. Reopens on a run where a hand-written row breaks execution or a consumer refuses a model.

## `exec-plan` carries minimal resume text

The lines that stay: a re-run's own edits are not foreign; a failed worktree story keeps its branch and worktree, and a rerun resumes on them; a resumed `story/{id}` may be a descendant of the base; under `--worktree` the review and fix run in the preserved worktree (2026-09-29).

Reopens on a recorded re-run that loses or duplicates work.

## Unattended remediation dispositions Notes on its own recommendation; attended remediation asks before any Tech Debt write

A deferred Note carries the recommended remedy. The reviewer's `Fix` bar is unchanged, but an unattended run has nobody to answer the list an interactive `implement-fix` returns, and 1.0 runs left `Note` and `NOTICED BUT NOT TOUCHING` items piling up unread. `--auto` is the approval for the unattended backlog writes. An attended run lists every `DEFERRED` finding with its blocker and remedy, because the backlog should not grow without a human choosing it (2026-09-29). `review` reads a story's recorded open items as it reads earlier reports.

Reopens if an eval shows it applying marginal observations.

## A change tidies what it finds

A tidy is a behavior-preserving fix in a function or doc section the change edits, or a minor mechanical or check-covered one elsewhere, or an obvious small bug in an edited function fixed under a test. An item goes to `NOTICED BUT NOT TOUCHING` only when someone should act on it. The 0.15.1 default of surface-don't-fix sent a smell the implementer could fix in one edit through three passes: recorded in the FIS, read back by the review as a finding (a "did not touch" note inside the change is a MEDIUM finding by `review-calibration.md` rule 7), then applied by the fix round. Rule 7's radius matches the tidy's. The never-a-tidy list dates from 2026-10-03.

Widened from the files the change touches (2026-10-15), because reports still filled with minor issues a behavior-preserving edit could clear. A parallel story's own-files limit exists because a tidy elsewhere can conflict with a sibling at merge.

Reopens if a review or eval shows a tidy hiding a regression.

## Test-first is a project convention, not a flag; Prove-It is mandatory

`testing --mode tdd`, `tdd-discipline.md` and `exec-plan --tdd` retired 2026-10-20: Böckeler, "TDD inside the agent loop – theater or actual value?" (martinfowler.com, 10 Aug 2026) measured 3–8.5× tokens and no measured gain, and the procedure restated canon the model knows. Prove-It rests on its own rationale, proof the bug existed and the retained regression guard, which those studies do not measure. `implement-fix` keeps test-first because, with no FIS, writing order is its only independence check.

Reopens on a measured gain from a TDD prompt that carries a test list.
