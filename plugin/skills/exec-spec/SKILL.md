---
description: Execute an existing Feature Implementation Specification (FIS) – implement it, verify it against its own proofs, review the change, complete on executed proof. Trigger on 'execute this spec', 'implement this FIS'.
argument-hint: "[--auto] [--tdd] [--no-full-tier] <path-to-fis>"
---

# Execute Feature Implementation Specification

`FIS_FILE_PATH` is `$ARGUMENTS` minus flags. Proofs, edits, and git run from the current git root, while provenance resolves beside the FIS.

- `--auto` is `AUTO_MODE`: no conversational prompts.
- `--tdd` is `TDD_MODE`, honored under `--auto`.
- `--no-full-tier` runs the fast tier in Step 3 instead of the full one, for a caller that runs the full tier on the final tree.


## INSTRUCTIONS

### Core Rules

- **The FIS is the source of truth – execute its intent.** Implement the whole of it or none of it; where its detail falls short, the best reading beats stopping, and the gap is recorded under `## Implementation Observations` for re-spec. Size or difficulty is work to finish, not permission to land a subset; a spec that should have been split is an upstream problem.
- **Surgical scope** – every changed line traces to a FIS task or accepted finding. Pre-existing issues surface as `NOTICED BUT NOT TOUCHING` and reach the FIS observations, never a fix here.
- **`plan.json` has one writer, the run session.** Invoked directly you are it: claim `owner` at admission, write the row yourself, and release the claim with the terminal status, per [`plan-schema.md`](../../references/plan-schema.md). Dispatched by the `andthen:exec-plan` skill you are not: read the row at admission, never write it, and report every field below verbatim. The FIS is yours to edit either way, under Step 4's amendment rules.
- **Execution discipline** – Stop-the-Line on a red gate, climb the Resolution Ladder before stopping: [`execution-discipline.md`](../../references/execution-discipline.md).
- **Automation rules** – [`automation-mode.md`](../../references/automation-mode.md).
- **Every dispatch below is a fresh subagent**: the installed role agent (`reviewer`, `worker`) when available, else a generic inherited subagent; never pin model or effort in a prompt. Await each required result – a progress message is not completion, and keep failed or partial evidence.


## WORKFLOW

### Step 1: Admission

1. **Provenance.** Read the FIS at `FIS_FILE_PATH` with the file-read tool – here and for every file this run opens, since a truncated `cat` is paid for twice. Resolve `PLAN_FILE_PATH` and `STORY_ID` from its `**Plan**:` / `**Story-ID**:` header, never from the working directory; where the header is missing or partial, from the `plan.json` beside the FIS whose story's `fis` names this file – a header line that row contradicts stops the run.

2. **Plan check.** `PLAN_FILE_PATH` holds that story, its `fis` names this file, every `dependsOn` story is `done`, and nothing in it contradicts [`plan-schema.md`](../../references/plan-schema.md); otherwise stop, keeping the evidence. Applicable `sharedDecisions` are execution input and outrank FIS text contradicting them – record that text as a `spec-stale` `#### DRIFT` line.

3. **Runtime state** is that story's record: its `status` and `completedTaskIds` are the resume authority over memory.

4. **Commands.** Resolve `Key Dev Commands` per [`verification-evidence.md`](../../references/verification-evidence.md).

**Gate**: provenance, dependencies, and runtime state are valid before the first edit.


### Step 2: Implement

Read `Learnings` and the `Tech Debt` item for the story's area (**Project Document Index**).

**Baseline the tree before the first edit** – the worktree may be shared. What `git status` shows then is foreign, except on a resume the changes implementing the story's recorded tasks. A foreign change is never reverted, stashed, or staged; where one overlaps a hunk this story changes, build on top of it – Step 5 leaves that file uncommitted.

- **Pending tasks in FIS order**: each task's `Verify` before advancing, then record every id verified since the last one in `completedTaskIds`. Recorded ids attribute this story's edits on resume, so never leave more unrecorded than you would redo.
- **Tests are written through the `andthen:testing` skill**, which carries the test-design rules: under `TDD_MODE` its `--mode tdd`, one scenario at a time; otherwise its default mode, for every unbound scenario. A task that fixes a defect, and any defect surfaced mid-run, takes its `--mode prove-it`: the failing test precedes the fix and stays as the regression guard.
- **UI work with no design contract in the FIS** gets `.agent_temp/ui-spec-<feature>.md` before the first screen is built – spacing, typography, color, component patterns, breakpoints, sourced FIS → design system → UX guidelines → defaults; Step 3 hands its path on.
- **Only the FIS's two tail sections are writable**: a missing requirement is appended under `## Discovered Requirements` before the edit depending on it, discoveries and observations under `## Implementation Observations`, and a contradiction or pivot takes Step 4.
- **Direct Checks before Step 3**, your own gate and not the run's evidence: `verification-evidence.md` § Substance and wiring scans, plus test integrity – a test that passes with its behavior removed is tautological, a suppression this diff adds needs a recorded reason, and deleting a test whose behavior still ships is Stop-the-Line.

Close with the **Chain Attestation** – one sentence per Expected Outcome over its `[OC<NN>]`-tagged scenarios and the tasks whose `SATISFIES` name them. A link missing from the change is unfinished work, not a caveat; one missing from the FIS – a scenario no task names – is implemented and proved anyway.

**Gate**: a complete attributed change set, its per-task verification results, and the Chain Attestation over every binding are in hand.


### Step 3: Verify and review the change

1. **Run the proofs yourself.** The full tier, or the fast tier under `--no-full-tier`, once, then every `Proof` and `Verify` target per *Runnable Proof Forms* in [`fis-contract.md`](../../references/fis-contract.md), and every Final Validation Checklist item the FIS carries. Run the executable targets from one command printing `<exit code> <proof id>` per target, and re-run a non-zero line alone for its output. Keep one line per proof id and checklist item – what ran, its exit code, and the runner's own result line, or what it saw – plus the tier result. Those lines are the story's evidence; recalling what a task did is not.

2. **One fresh reviewer, always.** You wrote this code, so the independent pass is not yours to give: spawn a fresh reviewer subagent that invokes the `andthen:review` skill with `--quick --fix --intent <absolute FIS_FILE_PATH>`, plus `--auto` in `AUTO_MODE`, over the changed paths, carrying the Chain Attestation as the claims to falsify. It applies the Fix-routed findings and returns every finding.

   Where no reviewer subagent can be spawned, your own diff pass against the FIS is the review, you apply that round yourself, and Step 5's `Reviewed:` line says so.

3. **UI work** spawns a fresh subagent that invokes the `andthen:visual-validation` skill with the screens and states this story touched, the project's `Visual Validation` document, and the design contract from Step 2, collected before any fix. It captures for itself and gets nothing else of yours: your measurements, summaries, and earlier verdicts frame it toward a pass. A re-validation carries only the finding it rechecks.

4. **Route what came back.**
   - Objective failures are work to finish: back to Step 2 until green. A P1 Critical or P2 Major visual finding is one of them, and its screen is recaptured after the fix – otherwise a known layout or accessibility defect completes green.
   - The fixes the review applied are the story's **one repair round**: re-run what they invalidated.
   - Everything else is recorded under `## Implementation Observations`, location and `Routing:` kept, and reported, not gated: the separate `review` → `implement-fix` step reads open findings from there and enforces them.
   - A stale spec or design pivot takes Step 4.

**Gate**: the proof lines and the review findings are in hand, the repair round is spent or was not needed, and every open finding is recorded for the completion report.


### Step 4: Amendments

You edit the FIS yourself, only in the sections [`fis-mutability.md`](../../references/fis-mutability.md) opens for execution and under its rules.

- **Real pivot** – never smuggled through `## Discovered Requirements`. Record the ADR with the `andthen:architecture` skill `--mode trade-off`, amend the FIS prose it changes, then re-run the affected Verify lines and attestation.
- **Drift** – record each amendment and every upstream document it leaves stale as a `#### DRIFT` line under `## Implementation Observations`; reconciliation above the FIS stays a recommendation.

**Gate**: every amendment is in the FIS, and no dependent edit precedes its requirement.


### Step 5: Complete

1. **The story's record**: `fis` this file's canonical basename, every verified task id in `completedTaskIds`, `verified: {at, summary}` whose `summary` takes `plan-schema.md`'s shape, quoted from Step 3's output, and only then `status: done`. Invoked directly, write it into `PLAN_FILE_PATH` before the commit.

2. **Commit.** `git add -- {changed-files}`, never `-A`, then `git commit -- {changed-files}` – the index may hold another session's staged work, and a pathspec ignores it. A file that also holds a foreign change commits from a temporary index carrying only this story's hunks (`GIT_INDEX_FILE`, `git read-tree HEAD`, `git apply --cached`); one whose hunks overlap it stays uncommitted and goes in the report. The paths are the change set plus the review's applied fixes, the FIS, and `plan.json` where you wrote it:

   ```
   {type}({STORY_ID}): <the FIS title, lowercased>

   Intent: <the FIS's Intent line>

   Story-ID: {STORY_ID}
   Plan: {PLAN_FILE_PATH}
   ```

   The trailers are what survives the bundle's deletion or merge.

3. **Report.** The four record fields – `fis`, `completedTaskIds`, `verified`, `status` – then per-task status, the changed files – any left uncommitted named with the foreign change they overlap – and Step 3's per-proof lines with the tier result.
   - Then the labeled line `Reviewed:`, never omitted: what reviewed the change and what it found, which findings the repair round fixed, and what stays open.
   - Add the Chain Attestation, the visual results where they apply, and a pointer to `## Implementation Observations`.
   - When the project keeps a changelog, add its entry for a user-facing change.
   - Invoked directly, end on one `Next (fresh session):` line in the host's slash-command syntax, so it pastes as-is into a new conversation – this one holds the whole implementation, and the next step reads the files instead: the `andthen:exec-spec` skill on the plan's next dependency-ready FIS while one remains, else the `andthen:review` skill with `--mode code,gap,security,outcome --fix {PLAN_FILE_PATH}`, `outcome` dropped when the plan names no PRD. Dispatched by `exec-plan`, print none – the run prints its own.

**Gate**: state is `done`, the commit carries its trailers, and the report carries the proof lines and what the review found.


## FAILURE HANDLING

Any gate, scenario, or criterion still red means no completion: return `## Failed Story Report`:

- Step 5's four record fields – `fis`, `completedTaskIds`, `verified` absent or partial, `status` the prior one preserved – so the run session writes the row from them unchanged; then story and FIS, the failing gates, the commands and results, the changed files, every open finding;
- the route out, verbatim: `Run the andthen:review skill with --mode code,gap --intent <absolute FIS_FILE_PATH> <changed paths>; then the andthen:implement-fix skill on the report it writes; then re-run the andthen:exec-spec skill on the FIS to re-execute the proofs and complete the story` (implement-fix reads a report, never a FIS).


## Post-Completion

Capture story-level traps in the `Learnings` document (**Project Document Index**): apply the admission questions in its header note, then append one bullet under the fitting topic.
