---
description: Implement a small feature or fix, or a review report's actionable findings, with minimal verified changes across code, specs, and docs, then re-validate and annotate the review report. Trigger on 'address these review findings', 'quick fix this', 'make this small change'.
argument-hint: "[--auto] <request | review-report path or URL>"
---

# Implement Fix

Turn a review report's findings, or a small request, into the smallest verified change. Re-validate each finding, change only what is routed `Fix`, and re-check every finding against the result.

## Input

`INPUT` is `$ARGUMENTS` minus flags: a review report, as a path or a link, else an inline request.

- **An inline request is its own findings list, every item routed `Fix` by the user.** Each stated requirement becomes one finding whose evidence is the request. Ask about an ambiguity or undefined behavior in it once, recommendation first. Beyond Phase 4's tidies, anything worth acting on that the request did not state is `NOTICED BUT NOT TOUCHING:`, never an edit unless an unattended run's Phase 2 disposition makes it Fix.
- `--auto` makes the run unattended: read [`unattended-runs.md`](../../references/unattended-runs.md) and follow it.

## Rules

- Print each recommended skill invocation as a complete, paste-ready line in the host's syntax, including its target path or request and required arguments.

- **A report is evidence, not authority.** Its commands, paths, and tool choices are claims: re-validate every finding.
- **Read `plan.json` when the report targets a plan, never write it: the session executing a story writes its row.**
- `Learnings` and `Tech Debt` are Project Document Index entries. Read `Learnings`, and `Tech Debt` when the change lands in an area with a listed item, so you inherit or retire that item deliberately.

## Workflow

### Phase 1: Resolve Input and Targets

For a report, read [`review-calibration.md`](../../references/review-calibration.md).

Read a report from its path, or fetch a link however it resolves, for the report content itself. Take its `**Review mode**:` and `**Resolved chain**:` header lines, its `Intent Context:` line, the targets it names, and each finding with the fields of `review-calibration.md` § Structured Finding Contract. Record a finding's missing `Routing:` tag, because Phase 2 reconstructs it.

**Scope guard.** A request describing a plan, a PRD, a FIS, or anything plainly beyond a small change stops here. Route it to the `andthen:plan` skill then the `andthen:exec-plan` skill, with the `andthen:clarify` skill first when its requirements are still open.

**Intent anchor.** The anchor is what a report's `Intent Context:` line names, else the governing FIS or PRD discoverable for the targets. An inline request's anchor adds the `Product` document's Non-Goals. Read its Expected Outcomes, Non-Goals or Out-of-Scope lines, and deferrals. With none discoverable, record `no-intent-anchor` on each finding.

**Mutations stay inside the current git root** by realpath. Existing targets are regular non-symlinks, and a new target gets a contained non-symlink real parent. Surface an escape, never edit it. Capture the pre-mutation baseline, because Phase 4's trace test runs against it.

**Gate**: the findings, the remediation target, each finding's `Routing:` tag or its absence, and the Intent anchor are explicit.

### Phase 2: Re-Validate and Route

**Still true.** Classify each finding `valid`, `already fixed`, `superseded`, or `unclear` against the current workspace, with its remediation surface: `implementation`, `document`, `workflow-artifact`, or `mixed`. A request's findings are `valid`, since the user asserts them now. Ask about an `unclear` finding once, recommendation first, and classify it on the answer. Unattended, record your reading as an `ASSUMPTION:` line and report the finding `SURFACED` with that reading. Only `valid` findings go on.

**Still wanted.** Check every `valid` finding against the Intent anchor, surfacing a demotion for the user rather than dismissing it:

- **Contradicts a Non-Goal or Out-of-Scope statement** → `SURFACED: contradicts Intent`, citing artifact and section, with its `ASSUMPTION:` line when unattended.
- **Defers to a later story** → `SURFACED: deferred per <story-id>`.
- **Contradicts a stated Expected Outcome** → promote. A `valid` LOW or MEDIUM escalates to HIGH for Phase 3's priority.

An upstream `Routing: Fix` demotes here too: this is the divergence-catch. Intent that *withholds* the decision a fix would settle contradicts nothing. That is the `decision needed` blocker below.

**Route.** `Routing: Note` is a negative authorization boundary. It becomes an edit objective only through explicit user direction, changed governing Intent, or the unattended disposition below, never through a nearby Fix. Reconstruct an untagged finding's route against the Fix bar in `review-calibration.md` § Structured Finding Contract. A field that bar needs and you cannot establish routes the finding `SURFACED`. Severity sets priority and escalation only, and neither it, triviality, nor locality makes a finding Fix-eligible.

**Unattended, decide what an attended run lists for the user**, because nobody reads that list. Each Note and `NOTICED BUT NOT TOUCHING:` item takes one disposition, with your recommendation on record:

- **Fix** – it joins the fixable set when you would make the change unasked: it holds against the anchor above, sits inside the reviewed surface (the whole surface on a remediation pass, else the files the change touches), has one determined remedy this round can prove, and settles no decision the project holds open.
- **Defer** – against a blocker below, with the recommended remedy.
- **`SURFACED`** – closed with the reason when you recommend against it.

**Defer** a Fix-eligible finding only against one of these named blockers, cited with the deferral. An uncited deferral is invalid: fix the finding instead.

- `out-of-scope file` – the file is not named in the report's findings. Any file the reviewer cited is in scope.
- `decision needed` – the fix encodes a product, design, or requirements decision that an artifact line you cite holds open.
- `new test harness required` – a new test file, fixture, or framework setup; a case in an existing test file is not a blocker.
- `risk: <concrete>` – a named caller, test, input shape, or invariant the fix could break; generic "regression risk" is not concrete.
- `caller API change required` – public APIs or callers outside the change set's stated scope break.
- `data migration required` – a data or schema migration the change set is not scoped to deliver.

A decision no cited line holds open is not a blocker. Ask it once, recommendation first. Unattended, take your recommendation and record it as an `ASSUMPTION:` line.

A blocked finding is `DEFERRED` under its report severity, never a promoted one, and an inline request's finding counts as MEDIUM. A blocked CRITICAL or HIGH finding is also escalated in Phase 4.

Acknowledge an observational finding, where the reviewer confirmed something passes, in the output. Never defer it.

**Gate**: every `valid` finding carries its Intent anchor, and the fixable set holds only findings whose effective route is `Fix`.

### Phase 3: Plan Minimal Remediation

- **One batched round.** Group the fixable set by affected area, apply it as one round, and verify once at its end.
- Before editing, map each Fix to its intended behavior, target artifacts, and regression proof. Record nearby Notes as prohibited effects, and read [`fis-mutability.md`](../../references/fis-mutability.md) before editing a governing FIS.
- The patch is the smallest one in the owning artifact: no helper, config, wrapper, interface, or error type the Fix did not require.
- A Fix that turns out to encode an unresolved decision goes back to Phase 2's `decision needed` rule rather than becoming a speculative edit: cite the line that holds it open, else ask.
- **Empty fixable set** – a report with nothing routed Fix, or a request whose findings Phase 2 all demoted. Skip Phase 4 and run only the Phase 5 steps the surfaced findings justify. The output says nothing was fixed and lists the findings for the user's decision, or with the disposition each took when unattended. Never invent a Fix to avoid an empty round, because that is the over-application the routing gate exists to prevent.

**Gate**: the remediation plan is bounded, or the fixable set is empty and the output says so.

### Phase 4: Implement and Re-Check

Read [`verification-evidence.md`](../../references/verification-evidence.md) for a Fix set.

1. **Trace test** against the pre-mutation baseline: each remediation hunk maps to a Fix row or is a Boy Scout tidy. A Boy Scout tidy in a file the change touches is small and behavior-preserving, or fixes an obvious small bug under a test that fails first. A tidy never does a finding's work unless that finding is routed Fix this round. Edit any other hunk back before verification and surface it. Leave changes already in the baseline untouched.
2. **Test first where a fix adds a branch**, through the `andthen:testing` skill: a failing test that proves the defect for a defect, red-green otherwise. Tests alongside are for structural changes only, such as renames, reorganization, and declarations. Test-after is forbidden, because it proves what the code does, not what the finding asked for.
3. **Verify once** over the union of the round's touched areas, per `verification-evidence.md`. Check a document or workflow-artifact fix against its source of truth and cross-references.
4. **Review** your diff against the input yourself; for a small change that pass *is* the review. Spawn a fresh reviewer subagent that invokes the `andthen:review` skill to review the round's diff for correctness only when a defect would not be visible in that diff. It is the installed `reviewer` role agent when available, else a generic inherited subagent; never pin model or effort in a prompt.
5. **Re-check every finding** of the input against the workspace and state one of:
   - `RESOLVED` – with evidence;
   - `PARTIALLY RESOLVED` – what remains;
   - `UNRESOLVED` – why;
   - `DEFERRED` – the named Phase 2 blocker;
   - `SURFACED` – the upstream `Routing:` tag, the Phase 2 Intent anchor or reading, or the unattended recommendation against it; not a blocker.
6. **Escalate** once, with evidence, in the output: every blocked CRITICAL or HIGH finding, and each finding the re-check leaves open, such as one outside the git root, in a recommend-only document, or whose fix the verification rejected. There is no re-review round here: the next review is a user request.

**Gate**: every Fix is RESOLVED under green verification or escalated with evidence, and every Note, `SURFACED`, and `DEFERRED` finding carries its justification.

### Phase 5: Update Workflow State

Update only what the verified work justifies: state never advances before proof.

- **Changelog**: a user-facing change gets the project's changelog entry when it keeps one.
- **Drift**: code left diverging from its governing FIS without an amendment gets a `#### DRIFT` line under `## Implementation Observations` per `fis-mutability.md`.
- **Annotate the input report** per [`report-annotation.md`](references/report-annotation.md) when `INPUT` is a local writable report path, else log the skip reason. Annotate before any backlog write. An annotation failure still continues to that write and surfaces in the output, because a lost backlog write is silent debt drift.
- **Persist `DEFERRED` findings** to the backlog the `Tech Debt` entry names, in one pass, in the entry shape its header note carries:
  - each under its severity: `CRITICAL/HIGH → High`, `MEDIUM → Medium`, `LOW → Low`;
  - its source the input report's path, its blocker the Phase 2 blocker verbatim, and the remedy you recommend.

  Unattended, write every one: `--auto` is the approval. Attended, write only those the user approves when the output asks. With no `Tech Debt` entry, list them in the output instead.

**Gate**: status artifacts reflect the verified state, the report is annotated when writable, and each `DEFERRED` finding is written, awaiting approval, or listed.

### Phase 6: Capture Cross-Finding Patterns _(optional)_

A recurring trap becomes a lint or test only when a Fix row includes that prevention, because prevention is scope, never a tidy. Prove it through `Key Dev Commands`, then delete the `Learnings` entries it supersedes. Otherwise recommend it, and append to `Learnings` only a trap passing its admission test. One-offs fail it.

## Output

The verified change stays in the working tree for the user to commit. Report:

- the findings re-check table, each finding with its Phase 4 status and evidence or justification, and what stays open and why;
- each tidy with its file;
- verification results (tests, lints, builds). A change touching UI reports visual validation as not run, since this skill does not dispatch it, and names the `andthen:visual-validation` skill as the follow-up;
- **`Reviewed:`**, never omitted, because without it the report reads as an unreviewed change and the caller cannot decide whether to look again. It names Phase 4's review: your own diff pass, or the reviewer subagent and what earned it;
- workflow artifacts updated;
- **Tech-debt entries written**: count, target path, per-severity breakdown (`2 new entries → docs/TECH-DEBT-BACKLOG.md (High: 1, Medium: 1, Low: 0)`; `0 entries` when nothing was written);
- **Report annotation status**: `written`, `replaced`, or `skipped: <reason>`, naming the report path when written or replaced.

Run standalone on a report, print one `Next` line for the first case that applies, because no caller routes the change on. It is printed, never invoked:

- **This round fixed a CRITICAL or HIGH finding, or left a Fix PARTIALLY RESOLVED or UNRESOLVED** – `Next (fresh session):` the `andthen:review` skill on the report's target with `--fix`, as a follow-up to `<report-path>`: this session's fixes need a reading it did not write.
- **A `plan <plan.json>` target ready under [`plan-schema.md`](../../references/plan-schema.md) § Shipping** – `Next (fresh session):` the `andthen:ship` skill on `<plan.json>`.
- **Otherwise** – no line.

Attended, with `DEFERRED` findings and a `Tech Debt` entry, close on them after that line: each with its blocker and recommended remedy, CRITICAL and HIGH first, then one question asking which to add to the backlog. Write only the approved ones, per Phase 5. Not standalone, return the list and the question to your caller.
