# Story Run

- **The FIS is the source of truth – execute its intent.** Implement the whole of it. Where its detail falls short, take the best reading rather than stopping, and record the gap under `## Implementation Observations`.
- **Surgical scope.** Every changed line traces to a FIS task, an accepted finding, the story's simplification, or a Boy Scout tidy. A Boy Scout tidy is a behavior-preserving fix to a smell or problem in a function or doc section the change edits, or to a minor one elsewhere when the fix is mechanical, touches only comments or docs, or is covered by checks that would catch a mistake in it. In an edited function, an obvious small bug fixed under a test that fails first is a tidy too. Make every tidy you find. What no tidy can fix and someone should act on goes under `## Implementation Observations` as `NOTICED BUT NOT TOUCHING`.

`Learnings` and `Tech Debt` are Project Document Index entries.

## Step 1: Admission

1. **Provenance.** Resolve `PLAN_FILE_PATH` and `STORY_ID` from the FIS's `**Plan**:` / `**Story-ID**:` header – the path repo-root-relative, from the git root holding the FIS, never the working directory.
2. **Plan check.** Stop unless `PLAN_FILE_PATH` holds that story and its `fis` names this file.
3. **Dependencies.** A `dependsOn` story not yet `done` means this one would build on work that is not there: ask whether to run anyway, recommending no.
4. **Shared decisions and discoveries.** Applicable `sharedDecisions` and the FIS's Discovered Requirements (read through their Interpretation) are execution input and outrank FIS text contradicting them: record that text as a `spec-stale` `#### DRIFT` line, and the scenario's bound Proof follows the outranking reading.

## Step 2: Implement

Read `Learnings` and the `Tech Debt` item for the story's area.

**Baseline the tree before the first edit**, because the worktree may be shared. What `git status` shows then is foreign, except on a re-run of this story the changes implementing its FIS tasks. Never revert, stash, or stage a foreign change. Then set the row's `status` to `in-progress`, before the first task edit, so a reader of `plan.json` sees the story executing.

- **Tasks in FIS order, implemented yourself** (`plan` sizes a story to one run), each passing its `Verify` before the next.
- **Tests go through the `andthen:testing` skill** for every unbound scenario, each written before the code it proves wherever the `Testing Strategy` document or the request requires test-first. A task that fixes a defect, and any defect surfaced mid-run, takes a failing test that proves the defect: it precedes the fix and stays as the regression guard.
- **UI work with no design contract in the FIS** writes one to `.agent_temp/ui-spec-<feature>.md` before the first screen is built, sourced from the design system, then the UX guidelines, then defaults.
- **The FIS changes only as `fis-mutability.md` allows.** A pivot records its ADR with the `andthen:decide` skill before the amendment.
- **Direct Checks before Step 3**: the substance and wiring scans of `verification-evidence.md`, and test integrity. **Falsifiability** – removing the protected behavior makes its owning test fail. A suppression this diff adds needs a recorded reason. A deleted test whose behavior still ships is a red objective gate.

Close with the **Chain Attestation**: one sentence per Expected Outcome over its `[OC<NN>]`-tagged scenarios and the tasks whose `SATISFIES` name them, and one per Discovered Requirement it did not append itself, over its proof. A link missing from the change is unfinished work, not a caveat.

## Step 3: Verify and review

1. **Run the proofs yourself**: the full tier once, or the fast tier under `--no-full-tier`, then every `Proof` and `Verify` target per `fis-contract.md` § Runnable Proof Forms, and every Final Validation Checklist item the FIS carries. Keep one line per proof id and checklist item – what ran, its exit code, and the runner's own result line, or what it saw – plus the tier result. Those lines are the story's evidence; recalling what a task did is not.
2. **One fresh reviewer, always.** You wrote this code, so the independent pass is not yours to give. Spawn a fresh reviewer subagent that invokes the `andthen:review` skill with `--quick --fix`, plus `--auto` in an unattended run, over the story's changed paths against its FIS, `<absolute FIS_FILE_PATH>`, carrying the Chain Attestation as the claims to falsify, one line per tidy as intended scope, and that it leaves its fixes uncommitted for Step 4. It applies the Fix-routed findings and returns every finding. Where no subagent can be spawned, your own diff pass against the FIS is the review, you apply its fixes, and the `Reviewed:` line says so.
3. **UI work** spawns a fresh reviewer subagent that invokes the `andthen:visual-validation` skill with the screens and states this story touched, the project's `Visual Validation` document, and the design contract. It captures for itself and gets nothing else of yours: your measurements, summaries, and earlier verdicts frame it toward a pass. A re-validation carries only the finding it rechecks.
4. **Route what came back.** Objective failures converge and subjective findings thrash, so the two route differently:
   - An objective failure is Step 2 work until green. A P1 Critical or P2 Major visual finding is one, and its screen is recaptured after the fix.
   - The fixes the review applied are the story's one repair round: re-run what they invalidated. A further review is a separate request.
   - Record everything else under `## Implementation Observations`, its location and `Routing:` kept, and report it without gating on it.

## Step 4: Complete

1. **Triage**, in a direct story run, per `between-stories.md` § Discovery triage, before the row, so a question waiting on the person leaves no `done` row uncommitted.
2. **Write the story's row** in `PLAN_FILE_PATH`: `fis` this file's canonical basename, every verified task id in `completedTaskIds`, `verified: {at, summary}` after it, and only then `status: done`. `at` is a UTC ISO-8601 minute. `summary` is one line quoted from Step 3's output: the proof command, its exit status, and the runner's own result line (`{cmd} -> exit=0, Ran 4 tests, OK`).
3. **Write what the project keeps**: a changelog entry for a user-facing change where the project keeps a changelog, and each story-level trap as one `Learnings` bullet under its fitting topic, admitted against its header note.
4. **Commit** the change set, the review's applied fixes, the FIS, `plan.json`, and the writes of Steps 4.1 and 4.3, per the commit rule. The message is a subject and two trailers with no body, because a squash merge can list every commit's message:

   ```
   {type}({STORY_ID}): <the FIS title, lowercased>

   Story-ID: {STORY_ID}
   Plan: {PLAN_FILE_PATH}
   ```

5. **Simplify**, in a direct story run, per `between-stories.md` § Simplify.
6. **Report** per-task status, the changed files, each tidy with its file, and Step 3's proof lines with the tier result. A dispatched story run names each discovery that affects an unstarted story, and that story, for its plan run to triage.
   - Then the labeled line `Reviewed:`, never omitted: what reviewed the change and what it found, which findings the repair round fixed, and what stays open.
   - Add the Chain Attestation, the visual results where they apply, and a pointer to `## Implementation Observations`.
   - End on the `Next (fresh session):` line of Follow-up.

## Failure handling

Past admission, unfinished work ends only on a stop named in this skill or a reference it loads.
Return `## Failed Story Report` with the story and FIS, the stop and its evidence, the failing gates, the commands and results, the changed files, and every open finding, then Follow-up's route out.
